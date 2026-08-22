#!/usr/bin/env python3
"""
build_ai_review_status.py -- maintain scripts/ai_review_status.tsv.

WHY THIS EXISTS
---------------
Prof. Dowling, 2026-08-22: "We need a way to track AI-drafted text on the
website. This way, I can see what is AI-draft when I review the corresponding
pages before each lecture. This also flags to students if content was
AI-drafted and I have not reviewed it yet."

So the marking has TWO audiences and therefore needs a REVIEW STATE, not just a
provenance flag:

  * him, deciding which pages need attention before a lecture, and
  * students, who should know when prose has not yet been through him.

The state lives in a hand-editable TSV, one row per notebook. He flips a row to
`reviewed` and the student-facing banner disappears on the next publish. The
format follows scripts/legacy_redirects.tsv -- an existing house convention that
diffs cleanly and needs no YAML parser.

WHAT COUNTS AS "AI-DRAFTED"
---------------------------
Not a guess. check_prose_baseline.py already answers this by diffing every
markdown cell against the IMMUTABLE anchor (commit feb00d2, 2026-08-17 -- the
last commit before agent editing of -dev notebooks began). This script reuses
that machinery rather than re-deriving it, so the two can never disagree.

  CHANGED  a cell that existed at the anchor and whose words are now different
           -- a human voice was displaced. The serious case.
  ADDED    a cell that did not exist at the anchor. New agent prose, but nothing
           was displaced.

Both count toward the banner. They are reported separately because they are not
equally serious.

*** THE LIMIT, AND IT MUST BE STATED WHEREVER THIS IS USED ***
This is blind to AI text OLDER than the anchor. A cell substituted before
2026-08-17 is invisible to the diff. The notebook-level `voice` label catches
the whole-notebook cases (`ai-drafted` = absent or a bare stub at the anchor),
but a pre-anchor cell-level substitution is not detected at all. So the honest
claim is "everything since agent editing began", NEVER "all AI-drafted text".
Do not let the banner or any report imply the stronger claim.

USAGE
-----
    python3 scripts/build_ai_review_status.py            # refresh the TSV
    python3 scripts/build_ai_review_status.py --check     # report, write nothing
    python3 scripts/build_ai_review_status.py --selftest

REFRESHING IS SAFE. Existing `reviewed` rows are PRESERVED -- a refresh never
silently un-reviews a page Prof. Dowling has already signed off. It only adds
new rows, updates counts, and retires rows whose notebook is gone. If a
reviewed notebook's prose changes AFTER review, the row is flagged
`reviewed-stale` rather than quietly reverted: that is a decision for him, and
downgrading it automatically would hide an agent edit made after his sign-off.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
TSV = HERE / "ai_review_status.tsv"

sys.path.insert(0, str(HERE))
import check_prose_baseline as cpb  # noqa: E402

HEADER = ["path", "status", "reviewed_date", "changed", "added", "voice", "note"]

STATUSES = {
    "unreviewed",     # banner shown
    "reviewed",       # banner suppressed
    "reviewed-stale", # was reviewed, prose changed since -- banner shown again
    "exempt",         # never banner (e.g. a page with no student-facing prose)
}


def read_tsv(path: Path) -> dict:
    if not path.exists():
        return {}
    rows = {}
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip() or line.startswith("#"):
            continue
        f = line.split("\t")
        if f[0] == "path":
            continue
        f += [""] * (len(HEADER) - len(f))
        rows[f[0]] = dict(zip(HEADER, f))
    return rows


def measure(root: Path):
    """{rel: {changed, added, voice, total}} for every in-scope notebook."""
    baseline = cpb.load(cpb.BASELINE) if hasattr(cpb, "load") else None
    import json
    if baseline is None:
        baseline = json.loads(cpb.BASELINE.read_text(encoding="utf-8"))
    anchor = baseline["anchor"]["notebooks"]
    registry = baseline.get("registry", {})

    current = cpb.select_scope(cpb.working_notebooks(root))
    out = {}
    for rel in sorted(current):
        try:
            now = cpb.markdown_cells((root / rel).read_text(encoding="utf-8"))
        except Exception:
            continue
        base = anchor.get(rel, {}).get("cells")
        if base is None:
            # Not present at the anchor at all: every cell is post-anchor prose.
            out[rel] = {"changed": 0, "added": len(now), "total": len(now),
                        "voice": registry.get(rel, {}).get("voice", "ai-drafted")}
            continue
        ch, ad, _rm = cpb.compare(base, now)
        out[rel] = {"changed": len(ch), "added": len(ad), "total": len(now),
                    "voice": registry.get(rel, {}).get("voice", "unknown")}
    return out


def merge(existing: dict, measured: dict):
    """Preserve human decisions; update counts. Returns (rows, notes)."""
    rows, retired, restaled, new = {}, [], [], []
    for rel, m in measured.items():
        touched = m["changed"] + m["added"]
        prev = existing.get(rel)
        if prev is None:
            status = "unreviewed" if touched else "exempt"
            rows[rel] = {"path": rel, "status": status, "reviewed_date": "",
                         "changed": str(m["changed"]), "added": str(m["added"]),
                         "voice": m["voice"], "note": ""}
            if touched:
                new.append(rel)
            continue
        status = prev["status"] if prev["status"] in STATUSES else "unreviewed"
        # A reviewed page whose counts have grown has been edited since sign-off.
        if status == "reviewed":
            was = int(prev["changed"] or 0) + int(prev["added"] or 0)
            if touched > was:
                status = "reviewed-stale"
                restaled.append(rel)
        if touched == 0 and status == "unreviewed":
            status = "exempt"
        rows[rel] = {"path": rel, "status": status,
                     "reviewed_date": prev["reviewed_date"],
                     "changed": str(m["changed"]), "added": str(m["added"]),
                     "voice": m["voice"], "note": prev["note"]}
    retired = [r for r in existing if r not in measured]
    return rows, {"retired": retired, "reviewed_stale": restaled, "new": new}


PREAMBLE = """\
# AI-review status, one row per notebook. Maintained by build_ai_review_status.py;
# EDIT THE status AND reviewed_date COLUMNS BY HAND -- that is the point of the file.
#
#   unreviewed      agent-touched prose, not yet reviewed -> student-facing banner
#   reviewed        signed off -> no banner. Set reviewed_date too (YYYY-MM-DD).
#   reviewed-stale  was reviewed, prose changed since -> banner returns. Re-read,
#                   then set back to `reviewed`. NEVER set automatically to
#                   `reviewed` -- that would hide an edit made after sign-off.
#   exempt          never banner (no agent-touched prose, or none student-facing).
#
# changed/added are COUNTS OF MARKDOWN CELLS vs the immutable anchor feb00d2
# (2026-08-17). `changed` displaced an existing human voice and is the serious
# column; `added` is new prose that displaced nothing.
#
# LIMIT: this is blind to AI text older than the anchor. Read it as "everything
# since agent editing began", never as "all AI-drafted text".
#
# Re-running the generator PRESERVES your `reviewed` rows. It is safe.
"""


def write(rows: dict, path: Path):
    lines = [PREAMBLE, "\t".join(HEADER)]
    for rel in sorted(rows):
        r = rows[rel]
        lines.append("\t".join(r[h] for h in HEADER))
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def selftest() -> int:
    """Watch the merge FAIL to lose a human decision, and FAIL to auto-approve."""
    ok = True

    def check(cond, msg):
        nonlocal ok
        print(("  ok   " if cond else "  FAIL ") + msg)
        ok = ok and cond

    print("build_ai_review_status --selftest")
    existing = {
        "notebooks/1-dev/A.ipynb": {"path": "notebooks/1-dev/A.ipynb",
            "status": "reviewed", "reviewed_date": "2026-08-20", "changed": "2",
            "added": "0", "voice": "dowling", "note": "checked"},
        "notebooks/1-dev/B.ipynb": {"path": "notebooks/1-dev/B.ipynb",
            "status": "reviewed", "reviewed_date": "2026-08-20", "changed": "1",
            "added": "0", "voice": "dowling", "note": ""},
        "notebooks/1-dev/GONE.ipynb": {"path": "notebooks/1-dev/GONE.ipynb",
            "status": "unreviewed", "reviewed_date": "", "changed": "3",
            "added": "0", "voice": "dowling", "note": ""},
    }
    measured = {
        # unchanged since review -> must STAY reviewed
        "notebooks/1-dev/A.ipynb": {"changed": 2, "added": 0, "total": 9, "voice": "dowling"},
        # edited since review -> must become reviewed-stale, NOT stay reviewed
        "notebooks/1-dev/B.ipynb": {"changed": 4, "added": 1, "total": 9, "voice": "dowling"},
        # brand new with agent prose -> unreviewed
        "notebooks/1-dev/C.ipynb": {"changed": 0, "added": 6, "total": 6, "voice": "ai-drafted"},
        # brand new, untouched -> exempt, no banner
        "notebooks/1-dev/D.ipynb": {"changed": 0, "added": 0, "total": 4, "voice": "dowling"},
    }
    rows, notes = merge(existing, measured)
    check(rows["notebooks/1-dev/A.ipynb"]["status"] == "reviewed",
          "a reviewed page with unchanged prose stays reviewed")
    check(rows["notebooks/1-dev/A.ipynb"]["reviewed_date"] == "2026-08-20",
          "the review date survives a refresh")
    check(rows["notebooks/1-dev/A.ipynb"]["note"] == "checked",
          "a hand-written note survives a refresh")
    check(rows["notebooks/1-dev/B.ipynb"]["status"] == "reviewed-stale",
          "prose edited after sign-off is flagged, not silently kept reviewed")
    check(rows["notebooks/1-dev/C.ipynb"]["status"] == "unreviewed",
          "new agent prose defaults to unreviewed (banner ON)")
    check(rows["notebooks/1-dev/D.ipynb"]["status"] == "exempt",
          "a notebook with no agent prose is exempt (no banner)")
    check("notebooks/1-dev/GONE.ipynb" in notes["retired"],
          "a vanished notebook is retired, not carried forever")
    check(all(r["status"] != "reviewed" for k, r in rows.items()
              if k == "notebooks/1-dev/C.ipynb"),
          "the generator never marks anything reviewed on its own")
    print("PASSED" if ok else "FAILED")
    return 0 if ok else 1


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--check", action="store_true", help="report only, write nothing")
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args(argv)
    if a.selftest:
        return selftest()

    measured = measure(ROOT)
    existing = read_tsv(TSV)
    rows, notes = merge(existing, measured)

    banner = [r for r in rows.values() if r["status"] in ("unreviewed", "reviewed-stale")]
    ch = sum(int(r["changed"] or 0) for r in banner)
    ad = sum(int(r["added"] or 0) for r in banner)
    print(f"{len(rows)} notebook(s) in scope")
    print(f"  banner ON : {len(banner)}  ({ch} changed + {ad} added markdown cells)")
    print(f"  reviewed  : {sum(1 for r in rows.values() if r['status']=='reviewed')}")
    print(f"  exempt    : {sum(1 for r in rows.values() if r['status']=='exempt')}")
    for k, v in notes.items():
        if v:
            print(f"  {k}: {len(v)}")
            for rel in v[:8]:
                print(f"      {rel}")
    if a.check:
        print("\n--check: nothing written")
        return 0
    write(rows, TSV)
    print(f"\nwrote {TSV.relative_to(ROOT)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
