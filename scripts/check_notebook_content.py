#!/usr/bin/env python3
"""Flag notebooks in `myst.yml` that are published but effectively empty.

WHY THIS EXISTS
---------------
`run_notebooks_from_myst.py` answers "does it run?". An empty notebook runs
perfectly, so it passes -- and a page consisting of one heading and one blank
code cell is published to the live site with a clean bill of health.

That is not hypothetical. On 2026-08-18 the W4 inventory found
`notebooks/8/MINLP-Algorithms.ipynb` and `notebooks/8/Global-Opt.ipynb` live in
`myst.yml`, each holding exactly a title and one empty cell, while the
corresponding handouts (`minlp-algorithms.tex`, 1804 lines, and
`global-optimization.tex`, 1244) are the two longest in the course pack. The
execution audit had reported the site healthy.

So this checks a different property: not "does it run" but "is there anything
there". The two questions need separate tools, because passing the first is
what disguises failing the second.

USAGE
-----
    python3 check_notebook_content.py            # check everything in myst.yml
    python3 check_notebook_content.py --selftest # prove it can FAIL

Exit status is 0 when clean and 1 when a published notebook is below threshold,
so it can gate a publish. A tool that says OK is not evidence until you have
watched it say FAIL.
"""

import json
import re
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
MYST = ROOT / "myst.yml"

# A notebook needs SOME substance. These are deliberately low bars -- the point
# is to catch stubs, not to police length.
MIN_NONEMPTY_CELLS = 3      # a title plus one cell is a stub
MIN_TOTAL_CHARS = 400       # prose or code -- a real page has SOMETHING in it

# NOT a rule: "must contain code". Several pages are legitimately prose --
# notebooks/1/Local-Install.ipynb and Optimization-Modeling.ipynb carry ~3,900
# characters of explanation and zero code, and are exactly what they should be.
# An earlier version of this check required code and flagged both, which would
# have trained the reader to ignore its output. The property that matters is
# whether there is CONTENT, not what kind.


def notebooks_in_myst(path: Path):
    """Active (non-commented) .ipynb entries listed in myst.yml."""
    out = []
    for line in path.read_text().splitlines():
        if line.lstrip().startswith("#"):
            continue
        m = re.search(r"file:\s*(\S+\.ipynb)", line)
        if m:
            out.append(m.group(1))
    return out


def assess(nb_path: Path):
    """Return (nonempty_cells, code_chars, markdown_chars) or None if unreadable."""
    try:
        nb = json.loads(nb_path.read_text())
    except Exception:
        return None
    nonempty = code = md = 0
    for c in nb.get("cells", []):
        src = "".join(c.get("source", [])).strip()
        if not src:
            continue
        nonempty += 1
        if c.get("cell_type") == "code":
            code += len(src)
        else:
            md += len(src)
    return nonempty, code, md


def main() -> int:
    if "--selftest" in sys.argv:
        return selftest()

    if not MYST.exists():
        print(f"myst.yml not found at {MYST}", file=sys.stderr)
        return 2

    entries = notebooks_in_myst(MYST)
    print(f"Notebook content check  ({len(entries)} published notebooks in myst.yml)")

    stubs, missing = [], []
    for rel in entries:
        p = ROOT / rel
        if not p.exists():
            missing.append(rel)
            continue
        res = assess(p)
        if res is None:
            missing.append(rel)
            continue
        nonempty, code, md = res
        if nonempty < MIN_NONEMPTY_CELLS or (code + md) < MIN_TOTAL_CHARS:
            stubs.append((rel, nonempty, code, md))

    if missing:
        print("\nUNREADABLE OR MISSING:")
        for rel in missing:
            print(f"  {rel}")

    if stubs:
        print("\nSTUBS -- published, but effectively empty. A reader gets a heading")
        print("and little else. These pass the execution audit precisely because")
        print("there is nothing in them to fail.\n")
        for rel, nonempty, code, md in stubs:
            print(f"  {rel}")
            print(f"      {nonempty} non-empty cell(s), {code} chars of code, {md} of prose")

    total_bad = len(stubs) + len(missing)
    print(f"\n{len(entries)} published notebooks: {total_bad} need attention")
    return 1 if total_bad else 0


def selftest() -> int:
    """Prove the checker fails on a stub and passes a real notebook."""
    import tempfile

    print("Self-test: must FAIL a stub and PASS a substantive notebook.\n")

    def make(cells):
        return {"cells": cells, "metadata": {}, "nbformat": 4, "nbformat_minor": 5}

    stub = make([
        {"cell_type": "markdown", "source": ["# Deterministic Global Optimization"]},
        {"cell_type": "code", "source": [""]},
    ])
    # Sized like an actual teaching page. The first version of this fixture was
    # ~150 characters and the self-test failed it -- correctly. The fixture was
    # unrealistic, not the threshold: no real notebook page is that short.
    real = make([
        {"cell_type": "markdown", "source": ["# A real page\n",
                                             "Explanation of the model. " * 12]},
        {"cell_type": "code", "source": ["import pyomo.environ as pyo\n",
                                         "m = pyo.ConcreteModel()\n",
                                         "m.x = pyo.Var(domain=pyo.NonNegativeReals)\n",
                                         "m.obj = pyo.Objective(expr=m.x)\n",
                                         "pyo.SolverFactory('glpk').solve(m)\n"]},
        {"cell_type": "markdown", "source": ["Discussion of the result. " * 12]},
    ])

    # A prose-only page is NOT a stub. Pinned because the first version of this
    # check got it wrong and flagged two legitimate installation/overview pages.
    prose = make([
        {"cell_type": "markdown", "source": ["# Installing the tools\n"]},
        {"cell_type": "markdown", "source": ["Long explanation. " * 40]},
        {"cell_type": "markdown", "source": ["More explanation. " * 40]},
    ])

    ok = True
    with tempfile.TemporaryDirectory() as tmp:
        for name, nb, should_flag in (("stub.ipynb", stub, True),
                                      ("real.ipynb", real, False),
                                      ("prose.ipynb", prose, False)):
            p = Path(tmp) / name
            p.write_text(json.dumps(nb))
            nonempty, code, md = assess(p)
            flagged = nonempty < MIN_NONEMPTY_CELLS or (code + md) < MIN_TOTAL_CHARS
            status = "OK  " if flagged == should_flag else "FAIL"
            if flagged != should_flag:
                ok = False
            verb = "flagged" if flagged else "passed"
            print(f"  {status} {name}: {verb}  "
                  f"({nonempty} cells, {code} code chars) -- expected "
                  f"{'flagged' if should_flag else 'passed'}")

    print()
    print("Self-test PASSED." if ok else "Self-test FAILED.")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
