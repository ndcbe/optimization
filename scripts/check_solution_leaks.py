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
5. No solution/hidden-test marker appears in a published cell's stored OUTPUTS.
   Source-only checks are exactly what stayed clean through 2026-08-21.
6. PUBLISHED ANSWER blocks (below) are well formed everywhere they appear.

THE PUBLISHED-ANSWER EXCEPTION
------------------------------
Some homework is **completion-graded exam-calibration** material: the student is
meant to attempt it cold and then check their own work against a published
answer. Prof. Dowling, 2026-08-25, on the diet and portfolio problems: the
answers go on the public site "because the homework is completion-based."

That is a deliberate hole in the rule this script enforces, so it is made
MACHINE-READABLE rather than left to prose:

    code cell      ### BEGIN PUBLISHED ANSWER   ...   ### END PUBLISHED ANSWER
    markdown cell  <!-- BEGIN PUBLISHED ANSWER -->  ...  <!-- END PUBLISHED ANSWER -->

`process_notebooks.py` passes such a block through to the published notebook,
markers and stored outputs included, instead of stripping it.

WHY MACHINE-READABLE. Written as ordinary prose, a deliberate answer and a
genuine leak are indistinguishable -- to this script, and to the next person
reading the file. An exception the tooling understands is safe; an exception
that works by the tooling not noticing is not. So the markers SURVIVE into the
published notebook: the published artifact carries its own evidence that the
answer was intended.

WHY TWO SPELLINGS. `###` is a Python comment in a code cell but an H3 HEADING in
markdown, where it would pollute the page and the table of contents. Published
answers are mostly prose, so markdown needs a spelling that renders as nothing.
Each spelling is accepted only in the cell type it suits; the wrong one is a
FAILURE, never a silent pass.

WHAT IS STILL A FAILURE, and deliberately so:
  * `### BEGIN SOLUTION` anywhere in a published notebook. Unchanged. The
    published-answer marker does not whitelist it.
  * `### BEGIN SOLUTION` INSIDE a published-answer block. The two must never be
    confusable, and nesting them is how they would become so.
  * An unmatched, nested, or wrong-cell-type published-answer marker.
  * A cell that is both a published answer and tagged `drop-output`.

SCOPE LIMIT. This is for completion-graded, exam-calibration material only.
Anything graded on correctness keeps `### BEGIN SOLUTION`. This script cannot
enforce that -- it is an editorial rule -- so it is written down here, in
`org/pyomo-style-guide.md` section 11a, and in the private ASSIGNMENT_PLAN.

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

# ---------------------------------------------------------------------------
# The published-answer marker. See the module docstring for the reasoning.
#
# One regex, both spellings, so that nothing is "not recognised as a marker".
# A line that LOOKS like a marker is always parsed as one; whether it was the
# right spelling for the cell type is then reported, not ignored. Anything that
# is merely close (`## BEGIN PUBLISHED ANSWER`, a trailing word) fails to match
# and is caught by NEAR_MISS below, so a typo is loud rather than invisible.
PA_MARKER = re.compile(
    r"^[ \t]*(?:"
    r"###[ \t]*(?P<hash>BEGIN|END)[ \t]+PUBLISHED[ \t]+ANSWER"
    r"|<!--[ \t]*(?P<html>BEGIN|END)[ \t]+PUBLISHED[ \t]+ANSWER[ \t]*-->"
    r")[ \t]*$"
)

# A line mentioning PUBLISHED ANSWER that PA_MARKER did not accept. Almost
# always a malformed marker, and a malformed marker is how a block silently
# stops being a block.
NEAR_MISS = re.compile(r"\b(?:BEGIN|END)[ \t]+PUBLISHED[ \t]+ANSWER\b")

# Solution markers must never appear inside a published-answer block.
SOLUTION_MARKER_LINE = re.compile(
    r"^\s*### (?:BEGIN|END) (?:SOLUTION|HIDDEN TESTS)\s*$")


def published_answer_findings(cell_type, src, tags=(), where=""):
    """Validate every published-answer marker in one cell.

    Returns (findings, n_blocks). `n_blocks` counts well-formed blocks, so a
    caller can report how many answers it is deliberately publishing rather
    than discovering them by accident.
    """
    findings = []
    depth = 0
    blocks = 0
    open_line = None

    for lineno, line in enumerate(src.splitlines(), start=1):
        m = PA_MARKER.match(line)
        if m is None:
            stripped = line.lstrip()
            marker_shaped = stripped.startswith("#") or stripped.startswith("<!--")
            if marker_shaped and NEAR_MISS.search(line):
                findings.append(
                    f"{where}line {lineno}: {line.strip()!r} mentions a "
                    f"PUBLISHED ANSWER marker but is not one. The marker must be "
                    f"a bare line: '### BEGIN PUBLISHED ANSWER' in a code cell, "
                    f"'<!-- BEGIN PUBLISHED ANSWER -->' in markdown")
            if depth > 0 and SOLUTION_MARKER_LINE.match(line):
                findings.append(
                    f"{where}line {lineno}: {line.strip()!r} is INSIDE a "
                    f"PUBLISHED ANSWER block. A deliberate answer and a stripped "
                    f"solution must never be nested -- that is what makes them "
                    f"confusable")
            continue

        kind = m.group("hash") or m.group("html")
        form = "hash" if m.group("hash") else "html"

        if cell_type == "markdown" and form == "hash":
            findings.append(
                f"{where}line {lineno}: '### {kind} PUBLISHED ANSWER' in a "
                f"MARKDOWN cell renders as an H3 heading and lands in the table "
                f"of contents. Use '<!-- {kind} PUBLISHED ANSWER -->'")
        if cell_type != "markdown" and form == "html":
            findings.append(
                f"{where}line {lineno}: '<!-- {kind} PUBLISHED ANSWER -->' is not "
                f"a Python comment. In a code cell use "
                f"'### {kind} PUBLISHED ANSWER'")

        if kind == "BEGIN":
            if depth:
                findings.append(
                    f"{where}line {lineno}: nested 'BEGIN PUBLISHED ANSWER' "
                    f"(the block opened on line {open_line} is still open). "
                    f"Do not nest them")
            else:
                open_line = lineno
            depth += 1
        else:
            if depth == 0:
                findings.append(
                    f"{where}line {lineno}: 'END PUBLISHED ANSWER' with no "
                    f"matching BEGIN in this cell")
            else:
                depth -= 1
                if depth == 0:
                    blocks += 1

    if depth:
        findings.append(
            f"{where}'BEGIN PUBLISHED ANSWER' on line {open_line} is never "
            f"closed in this cell. Both markers must be in the SAME cell")

    if blocks or depth:
        if DROP_OUTPUT_TAG in (tags or []):
            findings.append(
                f"{where}cell is a PUBLISHED ANSWER but is also tagged "
                f"{DROP_OUTPUT_TAG!r}. Those are opposite instructions: publish "
                f"the answer, and drop the answer")

    return findings, blocks


def output_text(cell):
    """Every scrap of TEXT a cell's stored outputs would show a reader.

    Source-only checks are precisely what stayed clean through the 2026-08-21
    leak, so the marker scan has to see this too.
    """
    chunks = []
    for out in cell.get("outputs") or []:
        chunks.append("".join(out.get("text") or []))
        chunks.append(str(out.get("evalue") or ""))
        chunks.append("".join(out.get("traceback") or []))
        for key, val in (out.get("data") or {}).items():
            if key.startswith("text/") or key == "application/json":
                chunks.append("".join(val) if isinstance(val, list) else str(val))
    return "\n".join(chunks)


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
            tags = (cell.get("metadata") or {}).get("tags") or []
            for marker in LIVE_MARKERS:
                if marker in src:
                    findings.append(
                        f"{rel}: cell {i} ({cell.get('cell_type')}) still contains "
                        f"{marker!r}")

            # The published-answer marker is ALLOWED to survive here -- that is
            # the whole point of it -- but only well formed. A half-open block
            # on the public site is indistinguishable from a leak.
            pa, _ = published_answer_findings(
                cell.get("cell_type"), src, tags, where=f"{rel}: cell {i}: ")
            findings += pa

            if cell.get("cell_type") != "code":
                continue

            # Check 5: markers in stored OUTPUTS. A published answer may keep
            # its outputs; a SOLUTION marker printed by a cell may not. This is
            # the half a `grep BEGIN SOLUTION` over source never sees.
            otext = output_text(cell)
            for marker in LIVE_MARKERS:
                if marker in otext:
                    findings.append(
                        f"{rel}: cell {i} has {marker!r} in its stored OUTPUT -- "
                        f"the answer is published as output, and a source-only "
                        f"check reports clean")

            outputs = cell.get("outputs") or []
            if not outputs:
                continue
            if any(m in src for m in STRIPPED_MARKERS):
                findings.append(
                    f"{rel}: cell {i} had its solution stripped but kept "
                    f"{len(outputs)} stored output(s) -- the answer is published "
                    f"as output")
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

            # Published-answer blocks are validated in the SOURCE too, not only
            # after publishing. A malformed marker here is the typo that would
            # otherwise reach the site; catching it before the publish pass is
            # the whole point of checking sources at all.
            tags = (cell.get("metadata") or {}).get("tags") or []
            pa, _ = published_answer_findings(
                cell.get("cell_type"), src, tags, where=f"{path}: cell {i}: ")
            findings += pa

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


def _md(source):
    return {"cell_type": "markdown", "metadata": {},
            "source": source.splitlines(keepends=True)}


def _display(text):
    """A rich display output -- the shape a leak takes when it is not a print."""
    return {"output_type": "execute_result", "execution_count": 1,
            "metadata": {}, "data": {"text/plain": [text]}}


# The correctly marked forms, written out once so the self-test and the docs
# cannot drift apart.
PA_CODE_OK = ("### BEGIN PUBLISHED ANSWER\n"
              "# 4 foods, 3 nutrient constraints -> 1 degree of freedom\n"
              "print('cost = 2.28')\n"
              "### END PUBLISHED ANSWER\n")
PA_MD_OK = ("Check your work.\n"
            "\n"
            "<!-- BEGIN PUBLISHED ANSWER -->\n"
            "The model has 4 variables and 3 active constraints, so DOF = 1.\n"
            "<!-- END PUBLISHED ANSWER -->\n")


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

            # --- the published-answer marker -------------------------------
            ("solution marker leaked through stored OUTPUT, not source",
             check_published,
             write("f.ipynb", _nb([_code(
                 "print(open('key.py').read())\n",
                 outputs=[_out("### BEGIN SOLUTION\nx = 1\n"
                               "### END SOLUTION\n")])]))),
            ("solution marker leaked through a rich display output",
             check_published,
             write("g.ipynb", _nb([_code(
                 "key\n", outputs=[_display("### BEGIN SOLUTION")])]))),
            ("PUBLISHED ANSWER opened and never closed",
             check_published,
             write("h.ipynb", _nb([_code("### BEGIN PUBLISHED ANSWER\n"
                                         "x = 1\n")]))),
            ("stray END PUBLISHED ANSWER with no BEGIN",
             check_published,
             write("i.ipynb", _nb([_code("x = 1\n"
                                         "### END PUBLISHED ANSWER\n")]))),
            ("nested PUBLISHED ANSWER blocks",
             check_published,
             write("j.ipynb", _nb([_code("### BEGIN PUBLISHED ANSWER\n"
                                         "### BEGIN PUBLISHED ANSWER\n"
                                         "x = 1\n"
                                         "### END PUBLISHED ANSWER\n"
                                         "### END PUBLISHED ANSWER\n")]))),
            ("BEGIN SOLUTION inside a PUBLISHED ANSWER block",
             check_sources,
             write("k.ipynb", _nb([_code("### BEGIN PUBLISHED ANSWER\n"
                                         "### BEGIN SOLUTION\n"
                                         "x = 1\n"
                                         "### END SOLUTION\n"
                                         "### END PUBLISHED ANSWER\n")]))),
            ("misspelled marker ('## BEGIN', not '###')",
             check_sources,
             write("l.ipynb", _nb([_code("## BEGIN PUBLISHED ANSWER\n"
                                         "x = 1\n"
                                         "## END PUBLISHED ANSWER\n")]))),
            ("unterminated HTML-comment marker",
             check_sources,
             write("m.ipynb", _nb([_md("<!-- BEGIN PUBLISHED ANSWER\n"
                                       "the answer\n"
                                       "<!-- END PUBLISHED ANSWER -->\n")]))),
            ("'###' spelling in a MARKDOWN cell (renders as a heading)",
             check_sources,
             write("n.ipynb", _nb([_md("### BEGIN PUBLISHED ANSWER\n"
                                       "the answer\n"
                                       "### END PUBLISHED ANSWER\n")]))),
            ("HTML-comment spelling in a CODE cell (not Python)",
             check_sources,
             write("o.ipynb", _nb([_code("<!-- BEGIN PUBLISHED ANSWER -->\n"
                                         "x = 1\n"
                                         "<!-- END PUBLISHED ANSWER -->\n")]))),
            ("PUBLISHED ANSWER cell also tagged drop-output",
             check_sources,
             write("p.ipynb", _nb([_code(PA_CODE_OK, tags=["drop-output"])]))),
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

        # The exception itself must PASS -- in the source and, crucially, on the
        # published side, WITH its stored outputs intact. A published answer
        # whose printed number were stripped would not be an answer.
        answer = write("answer.ipynb", _nb([
            _md(PA_MD_OK),
            _code(PA_CODE_OK, outputs=[_out("cost = 2.28\n")]),
        ]))
        found = check_published([answer]) + check_sources([answer])
        if found:
            ok = False
            print("  [FALSE POSITIVE] a correct PUBLISHED ANSWER was flagged:")
            for f in found:
                print(f"                  -> {f}")
        else:
            print("  [answer passes ] a correctly marked published answer, with "
                  "outputs, is allowed")

    print("\nself-test", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    sys.exit(main())
