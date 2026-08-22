#!/usr/bin/env python3
"""Fail if solution content reached a PUBLISHED notebook.

WHY THIS EXISTS
---------------
On 2026-08-21 every graded discussion answer in
`notebooks/assignments/Algorithms6-MINLP.ipynb` was live on the site, printed in
full underneath a `# Add your solution here` cell, and
`notebooks/assignments/Algorithms1.ipynb` published the inverse, the solution
vector, the eigenvalues and the condition numbers the same way. 32 cells across
three notebooks.

`grep -r "BEGIN SOLUTION" notebooks/` was clean the entire time, because the leak
was in `cell.outputs` and the grep only sees `cell.source`. That is the whole
lesson: **the obvious check returns clean while the answers are on the page.**

`process_notebooks.py` now clears outputs when it strips a solution block, so
this is not a live leak. This script exists because that fix is one regression
away from being undone, and the regression is silent -- nothing errors, the build
succeeds, the site deploys, and the answers are simply there. A check that runs
on every build is the difference between "fixed" and "stays fixed".

WHAT IT CHECKS
--------------
1. No solution/hidden-test MARKER survives in a published notebook, in any cell
   type. (markdown is not stripped, so a marker there would publish verbatim.)
2. No published cell whose source was REWRITTEN by the pipeline -- i.e. carries
   the "Add your solution here" or "Removed autograder test" substitute -- still
   has stored `outputs`. This is the check that would have caught 2026-08-21.
3. No published cell tagged `drop-output` still has stored `outputs`. That tag
   marks a cell of provided code whose stored output is nonetheless an answer,
   because it calls something the student had to write (see the long comment in
   `process_notebooks.py`).
4. Every `### BEGIN ...` marker in the `-dev`/private SOURCES is matched by an
   `### END ...`. An unmatched pair means the regex silently strips nothing, and
   the whole solution publishes with no marker left behind to grep for.

USAGE
-----
    python3 scripts/check_solution_leaks.py             # check the public tree
    python3 scripts/check_solution_leaks.py --selftest   # prove it can FAIL

Exit status is 0 when clean and 1 on any finding, so it can gate a build.
A tool that says OK is not evidence until you have watched it say FAIL.
"""

import json
import re
import sys
import tempfile
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PRIVATE = ROOT.parent / "optimization-private"

# The substitutes process_notebooks.py leaves behind. A cell carrying one of
# these HAD a solution in it, so stored output on it is by definition an answer.
STRIPPED_MARKERS = (
    "# Add your solution here",
    "# Removed autograder test. You may delete this cell.",
)

# Markers that must never survive into a published notebook.
LIVE_MARKERS = (
    "### BEGIN SOLUTION",
    "### END SOLUTION",
    "### BEGIN HIDDEN TESTS",
    "### END HIDDEN TESTS",
)

DROP_OUTPUT_TAG = "drop-output"

BEGIN_END = re.compile(r"^\s*### (BEGIN|END) (SOLUTION|HIDDEN TESTS)\s*$", re.M)


def published_notebooks():
    """Every notebook that ships, i.e. everything under notebooks/ except -dev."""
    return sorted(
        p for p in ROOT.glob("notebooks/**/*.ipynb")
        if not any(part.endswith("-dev") for part in p.parts)
        and ".ipynb_checkpoints" not in p.parts
    )


def source_notebooks():
    """The authored corpus: notebooks/N-dev/ here, plus the private assignments."""
    out = [p for p in ROOT.glob("notebooks/*-dev/*.ipynb")
           if ".ipynb_checkpoints" not in p.parts]
    out += sorted(PRIVATE.glob("notebooks/assignments/*.ipynb"))
    return sorted(out)


def cells(path):
    with open(path, encoding="utf-8") as fp:
        nb = json.load(fp)
    return nb.get("cells", [])


def check_published(paths):
    findings = []
    for path in paths:
        rel = path.relative_to(ROOT) if ROOT in path.parents else path
        for i, cell in enumerate(cells(path)):
            src = "".join(cell.get("source", []))
            for marker in LIVE_MARKERS:
                if marker in src:
                    findings.append(
                        f"{rel}: cell {i} ({cell.get('cell_type')}) still contains "
                        f"{marker!r}")
            if cell.get("cell_type") != "code":
                continue
            outputs = cell.get("outputs") or []
            if not outputs:
                continue
            if any(m in src for m in STRIPPED_MARKERS):
                findings.append(
                    f"{rel}: cell {i} had its solution stripped but kept "
                    f"{len(outputs)} stored output(s) -- the answer is published "
                    f"as output")
            tags = (cell.get("metadata") or {}).get("tags") or []
            if DROP_OUTPUT_TAG in tags:
                findings.append(
                    f"{rel}: cell {i} is tagged {DROP_OUTPUT_TAG!r} but kept "
                    f"{len(outputs)} stored output(s)")
    return findings


def check_sources(paths):
    findings = []
    for path in paths:
        counts = {}
        for i, cell in enumerate(cells(path)):
            src = "".join(cell.get("source", []))
            for kind in ("SOLUTION", "HIDDEN TESTS"):
                b = len(re.findall(rf"^\s*### BEGIN {kind}\s*$", src, re.M))
                e = len(re.findall(rf"^\s*### END {kind}\s*$", src, re.M))
                if b != e:
                    findings.append(
                        f"{path}: cell {i} has {b} '### BEGIN {kind}' and {e} "
                        f"'### END {kind}' -- the strip regex needs both, in the "
                        f"same cell")
                counts[kind] = counts.get(kind, (0, 0))
                counts[kind] = (counts[kind][0] + b, counts[kind][1] + e)
            if cell.get("cell_type") == "markdown":
                for marker in LIVE_MARKERS:
                    if marker in src:
                        findings.append(
                            f"{path}: cell {i} is MARKDOWN and contains "
                            f"{marker!r}; markdown is not stripped, so this "
                            f"publishes verbatim")
    return findings


def main():
    pub = published_notebooks()
    src = source_notebooks()
    findings = check_published(pub) + check_sources(src)
    print(f"Checked {len(pub)} published notebook(s) and {len(src)} source(s).")
    if findings:
        print(f"\nFAIL: {len(findings)} finding(s).\n")
        for f in findings:
            print(f"  {f}")
        return 1
    print("clean: no solution source, no solution output, no unmatched markers.")
    return 0


# ---------------------------------------------------------------------------
# Self-test. Each rule gets a notebook that must FAIL it.

def _nb(cells_):
    return {"cells": cells_, "metadata": {}, "nbformat": 4, "nbformat_minor": 4}


def _code(source, outputs=None, tags=None):
    cell = {"cell_type": "code", "execution_count": 1, "metadata": {},
            "outputs": outputs or [], "source": source.splitlines(keepends=True)}
    if tags:
        cell["metadata"]["tags"] = tags
    return cell


def _out(text="42\n"):
    return {"output_type": "stream", "name": "stdout", "text": [text]}


def selftest():
    ok = True
    with tempfile.TemporaryDirectory() as d:
        d = Path(d)

        def write(name, nb):
            p = d / name
            p.write_text(json.dumps(nb), encoding="utf-8")
            return p

        cases = [
            ("marker survives in published source",
             check_published,
             write("a.ipynb", _nb([_code("### BEGIN SOLUTION\nx = 1\n"
                                         "### END SOLUTION\n")]))),
            ("marker survives in published MARKDOWN",
             check_published,
             write("b.ipynb", _nb([{"cell_type": "markdown", "metadata": {},
                                    "source": ["### BEGIN SOLUTION\n"]}]))),
            ("stripped cell kept its outputs (the 2026-08-21 leak)",
             check_published,
             write("c.ipynb", _nb([_code("# Add your solution here\n",
                                         outputs=[_out("the answer is 7\n")])]))),
            ("drop-output cell kept its outputs",
             check_published,
             write("d.ipynb", _nb([_code("f(x)\n", outputs=[_out()],
                                         tags=["drop-output"])]))),
            ("BEGIN without END in a source notebook",
             check_sources,
             write("e.ipynb", _nb([_code("### BEGIN SOLUTION\nx = 1\n")]))),
        ]
        for label, fn, path in cases:
            found = fn([path])
            status = "FAIL detected" if found else "MISSED"
            if not found:
                ok = False
            print(f"  [{status:13s}] {label}")
            for f in found:
                print(f"                  -> {f}")

        clean = write("ok.ipynb", _nb([
            _code("# Add your solution here\n"),
            _code("print(1)\n", outputs=[_out("1\n")]),
            _code("f(x)\n", tags=["drop-output"]),
        ]))
        found = check_published([clean]) + check_sources([clean])
        if found:
            ok = False
            print("  [FALSE POSITIVE] a clean notebook was flagged:")
            for f in found:
                print(f"                  -> {f}")
        else:
            print("  [clean passes  ] a correctly processed notebook is not flagged")

    print("\nself-test", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    sys.exit(main())
