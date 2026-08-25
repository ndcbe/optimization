#!/usr/bin/env python3
r"""Assert that every committed figure archive still matches the notebook it came from.

WHY THIS EXISTS
---------------
``figures/results/<name>.json`` is a **generated artifact that is committed**:
solved numbers, extracted from Pyomo in a notebook, read back by
``figures/render_from_notebook.py`` so a style change can re-render ~27 figures
in seconds with no solver installed. That is the whole benefit -- and it is also
the whole hazard. A committed generated file that nothing polices goes stale
silently. Someone tightens a bound in the notebook next week, nobody re-runs it,
and the course pack quietly ships last term's answer while every build passes.

``lecture-notes/check_code_sync.py`` states the principle this is modelled on:

    "Generation alone guarantees nothing... Without a checker, 'single source of
     truth' is a claim; with one, it is an invariant."

Same idea, one stage further down the pipeline. ``check_code_sync.py`` pins the
typeset MODEL to the notebook cell that defines it; this pins the archived
RESULTS to that same cell. Between them, the model in the handout, the model in
the notebook, and the numbers in the figure are one thing.

HOW STALENESS IS DETECTED
-------------------------
Every archive records ``meta.source_tag`` -- the ``handout:<tag>`` on the cell
that defines the model -- and ``meta.source_digest``, the sha256 of that cell's
NORMALISED source at the moment the archive was written. The digest and the
normalisation both come from ``scripts/extract_pyomo_code.py``, imported rather
than reimplemented, because ``check_code_sync.py`` learned that a second
definition of "the same model" is a checker that agrees with nobody. Normalised
means comments and docstrings gone, so improving the commentary on the website
-- which should happen often -- does not make the archive stale. Changing a
bound, a set, a constraint or a name does.

🔴 WHAT THIS CANNOT SEE, AND WHY THAT IS ACCEPTED
--------------------------------------------------
The digest covers the MODEL cell, not the SOLVE. Edit the sweep range, the
solver options, or the input data file and the digest is unchanged while the
archived numbers are wrong. Two reasons not to widen it:

  * The model cell is the one thing that is already tagged, already
    single-sourced, and already stable enough to pin -- ``check_code_sync.py``'s
    own warning is that pinning anything unstable produces a checker that fails
    for reasons unrelated to the pack, and whoever silences it silences the real
    failures with it.
  * A change to the sweep or the data is a change someone is making ON PURPOSE
    to the figure, and they are looking at the figure while they do it. A change
    to the model is made for a different reason entirely -- fixing the handout
    listing, say -- with no thought of the figure at all. That is the case that
    needs a machine to notice.

So: this catches the silent class and says nothing about the loud one. Widening
it would mean digesting the whole notebook, which fails on every prose edit.

THE VERDICTS
------------
  OK           the archive matches the model cell it names.
  STALE        the model cell changed after the archive was written. Re-run the
               notebook and commit the new JSON and figures.
  UNVERIFIED   the archive names no ``source_tag``, or its digest is null (it
               was written on Colab, where the repo is not on disk). A WARNING,
               not a failure -- a data figure with no Pyomo model legitimately
               has no model cell to pin.
  ORPHAN       an archive whose ``source_tag`` exists in no notebook any more,
               or whose ``figure:`` cell has gone. Something still reads it.
  MISSING      a cell tagged ``figure:<name>`` with no ``results/<name>.json``.
               ``make`` cannot build that figure at all.
  MALFORMED    an archive missing a required ``meta`` key, or unparseable.

USAGE
-----
    python3 scripts/check_results_fresh.py
    python3 scripts/check_results_fresh.py --selftest   # prove it can FAIL

Exit status 0 when nothing fails, 1 on any failure, 2 when the repo layout is
wrong. Warnings do not fail unless ``--strict``. ``figures/Makefile``'s ``check``
target runs it.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
RESULTS_DIR = os.path.join(REPO, "figures", "results")
NB_GLOB = os.path.join(REPO, "notebooks", "*-dev", "*.ipynb")

sys.path.insert(0, os.path.join(REPO, "notebooks"))
sys.path.insert(0, os.path.join(REPO, "figures"))

FAIL_VERDICTS = {"STALE", "ORPHAN", "MISSING", "MALFORMED"}
WARN_VERDICTS = {"UNVERIFIED"}


def _load_deps():
    """Import the two modules that DEFINE the things being checked.

    ``pyomo_results.REQUIRED_META`` is the format; ``render_from_notebook``
    knows which cells are tagged and ``extract_pyomo_code`` defines the digest.
    All three are imported rather than restated, so this file cannot drift into
    checking a format nobody writes.
    """
    import pyomo_results
    import render_from_notebook

    return pyomo_results, render_from_notebook


# ---------------------------------------------------------------------------
# The core assertion, factored out so --selftest can drive it with fixtures.
# ---------------------------------------------------------------------------
def compare(archives, figure_cells, digests, required_meta):
    """Classify every figure. Returns (rows, problems).

    ``archives``      {name: parsed JSON payload, or None if unparseable}
    ``figure_cells``  {name: (notebook, cell index)} -- cells tagged figure:<name>
    ``digests``       {handout tag: current digest of that model cell}
    """
    rows = []
    for name in sorted(set(archives) | set(figure_cells)):
        payload = archives.get(name)
        cell = figure_cells.get(name)

        if payload is None and name in archives:
            rows.append((name, "MALFORMED", "the JSON does not parse"))
            continue
        if payload is None:
            rows.append((name, "MISSING", "a figure: cell with no archived results"))
            continue

        meta = payload.get("meta") or {}
        absent = [k for k in required_meta if k not in meta]
        if absent or "data" not in payload:
            rows.append(
                (name, "MALFORMED", f"meta is missing {', '.join(absent) or 'data'}")
            )
            continue

        if cell is None:
            rows.append(
                (name, "ORPHAN", "no notebook cell is tagged figure:" + name)
            )
            continue

        tag = meta.get("source_tag")
        stored = meta.get("source_digest")
        if not tag or not stored:
            rows.append(
                (name, "UNVERIFIED", "no source_tag/source_digest to compare against")
            )
            continue

        bare = tag.split(":", 1)[-1]
        if bare not in digests:
            rows.append(
                (name, "ORPHAN", f"no notebook cell carries the tag '{tag}' any more")
            )
            continue
        if digests[bare] != stored:
            rows.append(
                (
                    name,
                    "STALE",
                    f"the model cell '{tag}' now digests to {digests[bare]}, "
                    f"the archive recorded {stored}",
                )
            )
            continue
        rows.append((name, "OK", ""))

    return rows, [r for r in rows if r[1] in FAIL_VERDICTS or r[1] in WARN_VERDICTS]


# ---------------------------------------------------------------------------
def read_archives(results_dir=RESULTS_DIR):
    out = {}
    for p in sorted(glob.glob(os.path.join(results_dir, "*.json"))):
        name = os.path.basename(p)[:-5]
        try:
            out[name] = json.loads(open(p, encoding="utf-8").read())
        except (OSError, ValueError):
            out[name] = None
    return out


def current_digests(ex, nb_glob=NB_GLOB):
    snippets, _ = ex.find_snippets([nb_glob])
    return {s.tag: ex.digest(s.source) for s in snippets}


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Check archived figure results against their notebook cells.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("--strict", action="store_true", help="warnings fail too")
    ap.add_argument("--selftest", action="store_true", help="prove this can FAIL")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    try:
        pyr, rfn = _load_deps()
    except ImportError as exc:
        print(f"error: {exc}", file=sys.stderr)
        print(
            "Run this from inside the public repo; it imports notebooks/"
            "pyomo_results.py and figures/render_from_notebook.py.",
            file=sys.stderr,
        )
        return 2
    ex = pyr._extractor()
    if ex is None:
        print("error: cannot find scripts/extract_pyomo_code.py", file=sys.stderr)
        return 2

    archives = read_archives()
    cells = {n: (p, i) for n, (p, i, _) in rfn.find_figure_cells().items()}
    rows, _ = compare(archives, cells, current_digests(ex), pyr.REQUIRED_META)

    print("Figure results freshness  --  the notebook is the golden copy\n")
    if not rows:
        print("  Nothing archived and no cell tagged 'figure:<name>' yet.")
        print("  See figures/README.md, 'Solve -> extract -> plot'.")
        return 0

    print(f"  {'figure':<34}{'verdict':<13}source")
    print(f"  {'-' * 34}{'-' * 13}{'-' * 34}")
    for name, verdict, detail in rows:
        where = ""
        if name in cells:
            nb, idx = cells[name]
            where = f"{os.path.relpath(nb, REPO)} cell {idx}"
        print(f"  {name:<34}{verdict:<13}{where}")
        if detail:
            print(f"      {detail}")

    bad = [r for r in rows if r[1] in FAIL_VERDICTS]
    warn = [r for r in rows if r[1] in WARN_VERDICTS]
    if bad:
        print(f"\n{len(bad)} problem(s). Re-run the notebook that generates each,")
        print("then commit both figures/results/<name>.json and media/figures/<name>.*")
        return 1
    if warn:
        print(f"\n{len(warn)} unverified (no model cell to pin). Not a failure.")
        return 1 if args.strict else 0
    print(f"\nFRESH: {len(rows)} archive(s) match the model cells they name.")
    return 0


# ---------------------------------------------------------------------------
def selftest() -> int:
    """Drive `compare` with fixtures. A checker that cannot fail proves nothing."""
    print("Self-test: check_results_fresh.py -- must FAIL on a stale archive.\n")
    ok = True
    required = ("schema", "figure", "notebook", "generated")

    def expect(label, rows, name, verdict):
        nonlocal ok
        got = dict((n, v) for n, v, _ in rows).get(name)
        good = got == verdict
        ok &= good
        print(f"  {'OK  ' if good else 'FAIL'} {label}: -> {got} (expected {verdict})")

    def archive(digest="aaaa", tag="handout:m", **over):
        meta = {
            "schema": 1,
            "figure": "f",
            "notebook": "notebooks/1-dev/N.ipynb",
            "generated": "2026-08-24",
            "source_tag": tag,
            "source_digest": digest,
        }
        meta.update(over)
        return {"meta": meta, "data": {}}

    cells = {"f": ("notebooks/1-dev/N.ipynb", 7)}

    rows, _ = compare({"f": archive()}, cells, {"m": "aaaa"}, required)
    expect("archive matches the model cell", rows, "f", "OK")

    rows, _ = compare({"f": archive()}, cells, {"m": "bbbb"}, required)
    expect("model cell edited after archiving", rows, "f", "STALE")
    detail = [d for n, v, d in rows if n == "f"][0]
    good = "bbbb" in detail and "aaaa" in detail
    ok &= good
    print(f"  {'OK  ' if good else 'FAIL'} the stale report names both digests")

    rows, _ = compare({"f": archive()}, cells, {}, required)
    expect("the handout: tag has been removed", rows, "f", "ORPHAN")

    rows, _ = compare({"f": archive()}, {}, {"m": "aaaa"}, required)
    expect("the figure: cell has been removed", rows, "f", "ORPHAN")

    rows, _ = compare({}, cells, {"m": "aaaa"}, required)
    expect("a figure: cell with no archive", rows, "f", "MISSING")

    rows, _ = compare({"f": None}, cells, {}, required)
    expect("unparseable JSON", rows, "f", "MALFORMED")

    bad = archive()
    del bad["meta"]["generated"]
    rows, _ = compare({"f": bad}, cells, {"m": "aaaa"}, required)
    expect("meta missing a required key", rows, "f", "MALFORMED")

    rows, _ = compare(
        {"f": archive(digest=None, tag=None)}, cells, {"m": "aaaa"}, required
    )
    expect("archived on Colab, no digest", rows, "f", "UNVERIFIED")

    # A comment-only edit must NOT be stale. That is a property of the digest,
    # so it is tested against the real extractor rather than a fixture.
    try:
        import pyomo_results

        ex = pyomo_results._extractor()
        cell = "m = pyo.ConcreteModel()\n# a comment\nm.x = pyo.Var(bounds=(0, 1))\n"
        reworded = cell.replace("# a comment", "# a much better comment")
        same = ex.digest(cell) == ex.digest(reworded)
        changed = ex.digest(cell) != ex.digest(cell.replace("0, 1", "0, 4"))
        ok &= same and changed
        print(f"  {'OK  ' if same else 'FAIL'} rewording a comment does not change the digest")
        print(f"  {'OK  ' if changed else 'FAIL'} changing a bound does change the digest")
    except Exception as exc:  # noqa: BLE001
        ok = False
        print(f"  FAIL could not exercise the real digest: {exc}")

    print("\n" + ("self-test PASSED" if ok else "self-test FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
