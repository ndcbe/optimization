#!/usr/bin/env python3
r"""Typeset the Pyomo model in a tagged notebook cell into the course pack.

THE GOLDEN COPY IS THE NOTEBOOK
-------------------------------
Prof. Dowling, 2026-08-19:

    "I want the 'golden' copy of the Pyomo models to live in the notebooks. I
    then want it carefully typeset in the notes... I like the 'correct forever'
    approach, provided we can do it in a robust and systematic way."

So there is exactly one place a Pyomo model is written -- a cell in
``notebooks/<n>-dev/<Notebook>.ipynb`` -- and the handout is *generated* from
it. Nobody retypes a model into LaTeX, so the notes cannot drift from the code
students actually run. ``check_code_sync.py`` in the private repo is the
enforcement half: it fails when a generated file is stale.

HOW A CELL IS MARKED
--------------------
Add an ``nbformat`` cell tag of the form ``handout:<tag>``::

    "metadata": {"tags": ["handout:battery-model"]}

In JupyterLab that is the Property Inspector's "Cell Tags" field; no notebook
extension and no magic comment. Tags were chosen over a marker comment for two
reasons: they survive ``black``/``nbformat`` normalisation untouched, and
``process_notebooks.py`` carries them through to the published notebook, so the
mark is visible from either copy.

The lecture then typesets it with the house macro, which needs no arguments
beyond the tag::

    \pyomocode{battery-model}                  % box titled "Pyomo"
    \pyomocode[Battery model in Pyomo]{battery-model}

TWO TRANSFORMATIONS, BOTH REQUESTED
-----------------------------------
1. **Comments are stripped -- except units.**

       "We might decide to strip out comments from the notebook cells into the
       lecture notes. This way, the website has more extensive comments, and
       the code in the course pack/lecture notes take up less space."
       ... "We should keep units."

   So the website keeps the teaching commentary and the handout keeps the
   dimensional information, which is the part a student cannot reconstruct by
   reading the code. ``# Charging rate [MW]`` survives; ``# define a function
   to build model`` does not. See ``is_unit_comment``.

   Docstrings go too, by default (``--keep-docstrings`` to keep them). A
   nine-line Args/Returns block is the most extensive comment in the cell and
   the clearest case of what he asked to move to the website. This is the one
   place the script goes beyond the literal instruction, so it is a flag.

2. **Model formulation only.**

       "Model formulation only -- no solve statement, no results extraction. I
       want to emphasize the modeling aspects and translation to Pyomo."

   A tagged cell that calls a solver or prints results is refused, with the
   offending lines named, rather than silently trimmed. Where the cell boundary
   should fall is a pedagogical decision belonging to the notebook, and a
   script that quietly deleted the second half of a cell would hide it. Use
   ``--allow-scope`` only to inspect what would come out.

USAGE
-----
    python3 scripts/extract_pyomo_code.py                # all tagged cells
    python3 scripts/extract_pyomo_code.py --list         # what is tagged, no writes
    python3 scripts/extract_pyomo_code.py --tag battery-model
    python3 scripts/extract_pyomo_code.py --check        # would anything change?
    python3 scripts/extract_pyomo_code.py --selftest     # prove it works, and fails

Exit status 0 on success, 1 on a scope violation / stale file under ``--check``
/ a failed self-test, 2 on a usage or IO error.
"""

from __future__ import annotations

import argparse
import ast
import glob
import hashlib
import io
import json
import os
import re
import sys
import tempfile

HERE = os.path.dirname(os.path.abspath(__file__))
PUBLIC = os.path.dirname(HERE)                                  # optimization/
PRIVATE = os.path.join(os.path.dirname(PUBLIC), "optimization-private")
DEFAULT_OUT = os.path.join(PRIVATE, "lecture-notes", "code")
DEFAULT_NB_GLOB = os.path.join(PUBLIC, "notebooks", "*-dev", "*.ipynb")

TAG_PREFIX = "handout:"
GENERATOR = "scripts/extract_pyomo_code.py"

# A tag becomes a filename and a LaTeX argument, so keep it boring.
TAG_RE = re.compile(r"^[a-z0-9][a-z0-9-]*$")


# ---------------------------------------------------------------------------
# Comment classification
# ---------------------------------------------------------------------------
# A unit annotation is a bracketed group of unit-ish characters that is NOT a
# Python subscript. `[MW]', `[MWh] = [MW]*[1 hr]', `[$/MWh]', `[kg/s]' are
# units; `m.HORIZON[t]' is not, and is excluded by requiring the `[' to have no
# identifier character immediately before it.
UNIT_BRACKET_RE = re.compile(r"(?<![A-Za-z0-9_\]\)])\[[^\[\]]{1,24}\]")
# Inside the brackets: letters, digits, and the operators units are written
# with. Requires at least one letter or `$' so `[0]' and `[1:3]' are not units.
UNIT_BODY_RE = re.compile(r"^[A-Za-z0-9$%°µΩ/*^.\-\s]+$")
UNIT_WORD_RE = re.compile(r"\b(pyo\.units|pyomo\.environ\.units|units\.)")


def is_unit_comment(text: str) -> bool:
    """True when this comment body carries dimensional information worth keeping.

    Deliberately generous: a false keep costs one line in the handout, a false
    strip loses the only statement of what a variable is measured in. The
    course pack is the document a student reads without the notebook beside it.
    """
    if UNIT_WORD_RE.search(text):
        return True
    for m in UNIT_BRACKET_RE.finditer(text):
        body = m.group(0)[1:-1].strip()
        if body and UNIT_BODY_RE.match(body) and re.search(r"[A-Za-z$]", body):
            return True
    return False


# ---------------------------------------------------------------------------
# Scope: model formulation only
# ---------------------------------------------------------------------------
# Each entry is (regex, what it is). Kept narrow on purpose -- `pyo.value(' is
# NOT here, because it legitimately appears inside a constraint rule, and a
# checker that cries wolf gets switched off.
SCOPE_VIOLATIONS = [
    (re.compile(r"\bSolverFactory\b"), "solver construction"),
    (re.compile(r"\.solve\s*\("), "solve call"),
    (re.compile(r"\bsolver\s*\.\s*solve\b"), "solve call"),
    (re.compile(r"\bresults\s*="), "results extraction"),
    (re.compile(r"\bassert_optimal_termination\b"), "solve status check"),
    (re.compile(r"^\s*print\s*\(", re.M), "printing results"),
    (re.compile(r"\bplt\s*\.\s*\w"), "plotting"),
    (re.compile(r"\.display\s*\(\s*\)"), "results display"),
    (re.compile(r"\bpprint\s*\("), "results display"),
]


def scope_violations(code: str) -> list[tuple[int, str, str]]:
    """(1-based line number, what it is, the line) for anything past formulation."""
    out = []
    for i, line in enumerate(code.splitlines(), 1):
        if line.lstrip().startswith("#"):
            continue                      # a comment about solving is fine
        for rx, what in SCOPE_VIOLATIONS:
            if rx.search(line):
                out.append((i, what, line.strip()))
                break
    return out


# ---------------------------------------------------------------------------
# Transformation
# ---------------------------------------------------------------------------
def strip_comments(code: str, keep_units: bool = True) -> str:
    """Remove ``#`` comments, optionally keeping the unit annotations.

    Tokenize rather than regex, so a ``#`` inside a string literal is left
    alone. ``"#0072B2"`` in a notebook cell is a colour, not a comment, and a
    regex would truncate the line.
    """
    import tokenize

    try:
        toks = list(tokenize.generate_tokens(io.StringIO(code).readline))
    except (tokenize.TokenError, IndentationError, SyntaxError):
        # Not parseable on its own (a cell that continues an earlier one).
        # Fall back to the line-wise form, which is right except inside a
        # multi-line string containing a `#'.
        return _strip_comments_linewise(code, keep_units)

    drop: dict[int, list[tuple[int, int]]] = {}
    for tok in toks:
        if tok.type != tokenize.COMMENT:
            continue
        body = tok.string.lstrip("#").strip()
        if keep_units and is_unit_comment(body):
            continue
        drop.setdefault(tok.start[0], []).append((tok.start[1], tok.end[1]))

    out = []
    for n, line in enumerate(code.splitlines(), 1):
        if n not in drop:
            out.append(line)
            continue
        start = min(s for s, _e in drop[n])
        head = line[:start].rstrip()
        if head:
            out.append(head)              # inline comment removed
        else:
            out.append(None)              # comment-only line: drop it entirely
    return "\n".join(l for l in out if l is not None)


def _strip_comments_linewise(code: str, keep_units: bool) -> str:
    out = []
    for line in code.splitlines():
        i, cut, quote = 0, None, None
        while i < len(line):
            ch = line[i]
            if quote:
                if ch == "\\":
                    i += 2
                    continue
                if ch == quote:
                    quote = None
            elif ch in "\"'":
                quote = ch
            elif ch == "#":
                cut = i
                break
            i += 1
        if cut is None:
            out.append(line)
            continue
        body = line[cut + 1:].strip()
        if keep_units and is_unit_comment(body):
            out.append(line)
            continue
        head = line[:cut].rstrip()
        if head:
            out.append(head)
    return "\n".join(out)


def strip_docstrings(code: str) -> str:
    """Drop module/function/class docstrings. Silently a no-op if unparseable."""
    try:
        tree = ast.parse(code)
    except SyntaxError:
        return code

    spans = []
    for node in ast.walk(tree):
        if not isinstance(node, (ast.Module, ast.FunctionDef,
                                ast.AsyncFunctionDef, ast.ClassDef)):
            continue
        body = getattr(node, "body", None)
        if not body:
            continue
        first = body[0]
        if (isinstance(first, ast.Expr)
                and isinstance(first.value, ast.Constant)
                and isinstance(first.value.value, str)):
            spans.append((first.lineno, first.end_lineno))

    if not spans:
        return code
    kill = set()
    for a, b in spans:
        kill.update(range(a, b + 1))
    return "\n".join(l for n, l in enumerate(code.splitlines(), 1)
                     if n not in kill)


def tidy(code: str) -> str:
    """Trailing whitespace out, runs of blank lines collapsed to one."""
    lines = [l.rstrip() for l in code.splitlines()]
    out: list[str] = []
    for line in lines:
        if not line and (not out or not out[-1]):
            continue
        out.append(line)
    while out and not out[-1]:
        out.pop()
    while out and not out[0]:
        out.pop(0)
    return "\n".join(out)


def transform(code: str, keep_docstrings: bool = False) -> str:
    """Notebook cell source -> the code that goes in the handout."""
    if not keep_docstrings:
        code = strip_docstrings(code)
    return tidy(strip_comments(code, keep_units=True))


def normalise(code: str) -> str:
    """The comparison form: no comments at all, no blank lines, no trailing space.

    ⚠ This is what makes ``check_code_sync.py`` usable. The generated file keeps
    unit comments and the notebook keeps every comment, so a byte comparison
    would report every single file as out of date, every time. Normalising both
    sides to comment-free code compares the thing that actually matters -- the
    model -- and stays quiet when someone improves the prose on the website.
    """
    code = strip_docstrings(code)
    code = strip_comments(code, keep_units=False)
    return "\n".join(l.rstrip() for l in code.splitlines() if l.strip())


def digest(code: str) -> str:
    return hashlib.sha256(normalise(code).encode("utf-8")).hexdigest()[:16]


# ---------------------------------------------------------------------------
# Notebook scanning
# ---------------------------------------------------------------------------
class Snippet:
    def __init__(self, tag, notebook, index, source):
        self.tag = tag
        self.notebook = notebook
        self.index = index
        self.source = source

    @property
    def rel(self):
        return _display(self.notebook)


def _display(path: str) -> str:
    """Path relative to the public repo, or absolute if it lives outside it.

    os.path.relpath alone produced ../../../../../var/folders/... for the
    self-test's temporary fixtures, which is noise in exactly the output a
    reader is trying to check.
    """
    ap = os.path.abspath(path)
    if ap.startswith(PUBLIC + os.sep):
        return os.path.relpath(ap, PUBLIC)
    return ap


def read_cells(path: str):
    """(index, cell_type, tags, source) for every cell.

    nbformat when available -- it validates and normalises -- and plain json
    otherwise, because reading a tag needs neither.
    """
    try:
        import nbformat

        nb = nbformat.read(path, as_version=4)
        cells = nb.cells
        get = lambda c: (c.get("cell_type"), c.get("metadata", {}) or {},
                         c.get("source", ""))
    except Exception:
        nb = json.load(open(path, encoding="utf-8"))
        cells = nb.get("cells", [])

        def get(c):
            src = c.get("source", "")
            return (c.get("cell_type"), c.get("metadata", {}) or {},
                    "".join(src) if isinstance(src, list) else src)

    for i, cell in enumerate(cells):
        ctype, meta, src = get(cell)
        tags = list(meta.get("tags", []) or [])
        yield i, ctype, tags, src


def find_snippets(patterns: list[str]) -> tuple[list[Snippet], list[str]]:
    """Every ``handout:<tag>`` code cell across the notebooks, plus complaints."""
    snippets, problems = [], []
    seen: dict[str, Snippet] = {}
    for pattern in patterns:
        for path in sorted(glob.glob(pattern)):
            if ".ipynb_checkpoints" in path:
                continue
            try:
                cells = list(read_cells(path))
            except Exception as exc:                        # noqa: BLE001
                problems.append(f"{path}: unreadable ({exc})")
                continue
            for i, ctype, tags, src in cells:
                for tag in tags:
                    if not tag.startswith(TAG_PREFIX):
                        continue
                    name = tag[len(TAG_PREFIX):]
                    rel = _display(path)
                    if ctype != "code":
                        problems.append(
                            f"{rel} cell {i}: tag {tag!r} is on a "
                            f"{ctype} cell; only code cells can be extracted")
                        continue
                    if not TAG_RE.match(name):
                        problems.append(
                            f"{rel} cell {i}: tag {name!r} must match "
                            f"{TAG_RE.pattern} -- it becomes a filename")
                        continue
                    if name in seen:
                        problems.append(
                            f"tag {name!r} claimed twice: "
                            f"{seen[name].rel} cell {seen[name].index} and "
                            f"{rel} cell {i}")
                        continue
                    s = Snippet(name, path, i, src)
                    seen[name] = s
                    snippets.append(s)
    snippets.sort(key=lambda s: s.tag)
    return snippets, problems


# ---------------------------------------------------------------------------
# Emission
# ---------------------------------------------------------------------------
BANNER = "% " + "-" * 74


def render(snip: Snippet, keep_docstrings: bool = False) -> str:
    """The full text of ``lecture-notes/code/<tag>.tex``."""
    code = transform(snip.source, keep_docstrings=keep_docstrings)
    lines = [
        BANNER,
        "% GENERATED FILE -- DO NOT EDIT.",
        "%",
        f"% tag       : {snip.tag}",
        f"% source    : optimization/{snip.rel}, cell {snip.index}",
        f"% generator : {GENERATOR}",
        f"% normhash  : {digest(snip.source)}",
        "%",
        "% The notebook cell above is the golden copy. Comments are stripped on",
        "% extraction except unit annotations; docstrings are dropped. Regenerate",
        f"% with:  python3 {GENERATOR} --tag {snip.tag}",
        "% Verify with: lecture-notes/check_code_sync.py",
        BANNER,
        r"\begin{lstlisting}[style=pyomohandout]",
        code,
        r"\end{lstlisting}",
        "",
    ]
    return "\n".join(lines)


LISTING_OPEN = re.compile(r"^\\begin\{lstlisting\}.*$", re.M)
LISTING_CLOSE = re.compile(r"^\\end\{lstlisting\}\s*$", re.M)
HASH_RE = re.compile(r"^%\s*normhash\s*:\s*(\w+)\s*$", re.M)
SOURCE_RE = re.compile(r"^%\s*source\s*:\s*(.+?), cell (\d+)\s*$", re.M)


def parse_generated(text: str) -> dict:
    """Pull the code body and the provenance header back out of a generated file.

    ``check_code_sync.py`` imports this, so the format is defined in exactly one
    place -- the writer and the reader cannot disagree about it.
    """
    o = LISTING_OPEN.search(text)
    c = LISTING_CLOSE.search(text)
    body = None
    if o and c and c.start() > o.end():
        body = text[o.end():c.start()].strip("\n")
    h = HASH_RE.search(text)
    s = SOURCE_RE.search(text)
    return {
        "body": body,
        "normhash": h.group(1) if h else None,
        "notebook": s.group(1) if s else None,
        "cell": int(s.group(2)) if s else None,
    }


# ---------------------------------------------------------------------------
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description="Typeset tagged Pyomo notebook cells into the course pack.",
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("--notebooks", nargs="*", default=[DEFAULT_NB_GLOB],
                    help="notebook glob(s) to scan (default: notebooks/*-dev/*.ipynb)")
    ap.add_argument("--out", default=DEFAULT_OUT,
                    help="output directory (default: the private repo's "
                         "lecture-notes/code/)")
    ap.add_argument("--tag", action="append", default=None,
                    help="extract only this tag; repeatable")
    ap.add_argument("--list", action="store_true",
                    help="report what is tagged and write nothing")
    ap.add_argument("--check", action="store_true",
                    help="write nothing; exit 1 if any output would change")
    ap.add_argument("--allow-scope", action="store_true",
                    help="downgrade solve/results scope violations to warnings")
    ap.add_argument("--keep-docstrings", action="store_true",
                    help="keep function docstrings (dropped by default)")
    ap.add_argument("--selftest", action="store_true",
                    help="prove the transformations, and prove they can fail")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    snippets, problems = find_snippets(args.notebooks)
    if args.tag:
        want = set(args.tag)
        missing = want - {s.tag for s in snippets}
        for m in sorted(missing):
            problems.append(f"tag {m!r} requested but not found in any notebook")
        snippets = [s for s in snippets if s.tag in want]

    for p in problems:
        print(f"  PROBLEM  {p}", file=sys.stderr)

    if not snippets:
        print(f"No cells tagged '{TAG_PREFIX}<tag>' in: "
              f"{', '.join(args.notebooks)}")
        print("Add a cell tag in JupyterLab's Property Inspector, e.g. "
              f"'{TAG_PREFIX}battery-model'.")
        return 1 if problems else 0

    if args.list:
        print(f"{len(snippets)} tagged cell(s):\n")
        for s in snippets:
            code = transform(s.source, keep_docstrings=args.keep_docstrings)
            v = scope_violations(s.source)
            print(f"  {s.tag:<28} {s.rel} cell {s.index}   "
                  f"{len(s.source.splitlines()):>3} -> "
                  f"{len(code.splitlines()):>3} lines"
                  f"{'   SCOPE: ' + str(len(v)) if v else ''}")
        return 1 if problems else 0

    os.makedirs(args.out, exist_ok=True)
    failed, changed, written = [], [], []
    for s in snippets:
        v = scope_violations(s.source)
        if v:
            label = "WARN " if args.allow_scope else "FAIL "
            print(f"  {label} {s.tag}: cell is not model formulation only "
                  f"({s.rel} cell {s.index})")
            for n, what, line in v:
                print(f"         line {n}: {what} -- {line[:70]}")
            if not args.allow_scope:
                failed.append(s.tag)
                continue

        text = render(s, keep_docstrings=args.keep_docstrings)
        path = os.path.join(args.out, f"{s.tag}.tex")
        old = open(path, encoding="utf-8").read() if os.path.exists(path) else None
        if old == text:
            print(f"  ok    {s.tag:<28} unchanged")
            continue
        changed.append(s.tag)
        if args.check:
            print(f"  STALE {s.tag:<28} {os.path.relpath(path)} "
                  f"{'differs' if old is not None else 'missing'}")
            continue
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        written.append(s.tag)
        print(f"  wrote {s.tag:<28} {os.path.relpath(path)}  "
              f"({len(transform(s.source, args.keep_docstrings).splitlines())} lines)")

    print()
    if failed:
        print(f"REFUSED {len(failed)}: {', '.join(failed)}")
        print("Split the notebook cell so the tagged one builds the model and "
              "nothing else, or pass --allow-scope to look at the output first.")
        return 1
    if args.check:
        if changed:
            print(f"STALE: {len(changed)} file(s) would change: "
                  f"{', '.join(changed)}")
            return 1
        print(f"UP TO DATE: {len(snippets)} snippet(s).")
        return 1 if problems else 0
    print(f"{len(written)} written, {len(snippets) - len(written)} unchanged.")
    return 1 if problems else 0


# ---------------------------------------------------------------------------
def selftest() -> int:
    """Exercise every transformation, in both directions.

    A tool that only demonstrates success proves nothing: three verification
    scripts in these repos shipped reporting OK while measuring nothing. Each
    case below states what must happen AND what must not.
    """
    print("Self-test: extract_pyomo_code.py\n")
    ok = True

    def check(label, got, want):
        nonlocal ok
        good = got == want
        ok &= good
        print(f"  {'OK  ' if good else 'FAIL'} {label}")
        if not good:
            print(f"         got  {got!r}")
            print(f"         want {want!r}")

    # --- unit comments are kept, prose comments are not --------------------
    for text, want in [
        ("Charging rate [MW]", True),
        ("[MWh] = [MW]*[1 hr]", True),
        ("price [$/MWh]", True),
        ("flow [kg/s]", True),
        ("uses pyo.units.kg", True),
        ("define a function to build model", False),
        ("First timestep", False),
        ("loop over m.HORIZON[t]", False),          # subscript, not a unit
        ("see equation [4]", False),                # digits only, not a unit
        ("", False),
    ]:
        check(f"is_unit_comment({text!r}) -> {want}", is_unit_comment(text), want)

    # --- the whole transformation on a realistic cell ----------------------
    cell = '\n'.join([
        "# define a function to build model",
        "def build_model(price, e0=0):",
        '    """Create optimization model.',
        "",
        "    Arguments:",
        "        price: NumPy array",
        '    """',
        "",
        "    m = pyo.ConcreteModel()",
        "",
        "    ## Define Sets",
        "    m.HORIZON = pyo.Set(initialize=range(len(price)))",
        "",
        "    # Charging rate [MW]",
        "    m.c = pyo.Var(m.HORIZON, bounds=(0, 1))",
        "",
        "    marker = \"#not-a-comment\"   # colour [MW]",
        "    return m",
    ])
    out = transform(cell)
    check("prose comment dropped", "define a function" in out, False)
    check("unit comment kept", "# Charging rate [MW]" in out, True)
    check("docstring dropped", "Arguments:" in out, False)
    check("hash-in-string survives", '"#not-a-comment"' in out, True)
    check("inline unit comment kept", out.count("[MW]") == 2, True)
    check("blank-line runs collapsed", "\n\n\n" in out, False)
    check("code intact", "m.c = pyo.Var(m.HORIZON, bounds=(0, 1))" in out, True)

    # --- normalisation is stable under a comment-only edit -----------------
    reworded = cell.replace("# define a function to build model",
                            "# Build the receding-horizon model. See eq. (2-4).")
    check("normalise() ignores a comment rewrite",
          normalise(cell) == normalise(reworded), True)
    check("normalise() drops even unit comments",
          "[MW]" in normalise(cell), False)
    moved = cell.replace("bounds=(0, 1)", "bounds=(0, 2)")
    check("normalise() NOTICES a model change",
          normalise(cell) == normalise(moved), False)
    check("digest() changes with the model", digest(cell) != digest(moved), True)
    check("digest() stable across a comment rewrite",
          digest(cell) == digest(reworded), True)

    # --- scope enforcement, both directions --------------------------------
    formulation = "m = pyo.ConcreteModel()\nm.x = pyo.Var()\n"
    check("clean formulation has no violations",
          scope_violations(formulation), [])
    for bad, why in [
        ("solver = pyo.SolverFactory('ipopt')", "SolverFactory"),
        ("results = solver.solve(m)", "solve"),
        ("print(pyo.value(m.x))", "print"),
        ("plt.plot(t, e)", "plot"),
        ("m.pprint()", "pprint"),
    ]:
        v = scope_violations(formulation + bad + "\n")
        good = len(v) == 1
        ok &= good
        print(f"  {'OK  ' if good else 'FAIL'} scope catches {why}: "
              f"{len(v)} violation(s), expected 1")
    # ...and does NOT fire on a value() inside a constraint rule.
    v = scope_violations("m.C = pyo.Constraint(expr=m.x <= pyo.value(m.p))\n")
    check("scope does not fire on pyo.value in a rule", v, [])

    # --- round trip through a real notebook file ---------------------------
    with tempfile.TemporaryDirectory() as tmp:
        nbdir = os.path.join(tmp, "notebooks", "9-dev")
        os.makedirs(nbdir)
        nbpath = os.path.join(nbdir, "Fixture.ipynb")
        nb = {
            "cells": [
                {"cell_type": "markdown", "metadata": {}, "source": ["# Title\n"]},
                {"cell_type": "code", "metadata": {"tags": ["handout:fixture"]},
                 "source": [cell], "outputs": [], "execution_count": None},
                {"cell_type": "code", "metadata": {"tags": ["handout:has-solve"]},
                 "source": ["m = pyo.ConcreteModel()\n",
                            "results = pyo.SolverFactory('ipopt').solve(m)\n"],
                 "outputs": [], "execution_count": None},
            ],
            "metadata": {}, "nbformat": 4, "nbformat_minor": 5,
        }
        json.dump(nb, open(nbpath, "w"))

        # The malformed tags live in a SEPARATE fixture, so the exit statuses
        # asserted below are not confounded by a standing PROBLEM report --
        # find_snippets deliberately makes any malformed tag anywhere a
        # nonzero exit, and that is checked on its own.
        badpath = os.path.join(nbdir, "Bad.ipynb")
        json.dump({"cells": [
            {"cell_type": "markdown",
             "metadata": {"tags": ["handout:on-prose"]}, "source": ["not code\n"]},
            {"cell_type": "code", "metadata": {"tags": ["handout:Bad_Tag"]},
             "source": ["m = 1\n"], "outputs": [], "execution_count": None},
        ], "metadata": {}, "nbformat": 4, "nbformat_minor": 5},
            open(badpath, "w"))

        snips, probs = find_snippets([nbpath])
        check("finds the tagged code cells", sorted(s.tag for s in snips),
              ["fixture", "has-solve"])
        _, probs = find_snippets([badpath])
        check("rejects a tag on a markdown cell",
              any("markdown" in p for p in probs), True)
        check("rejects a tag that is not filename-safe",
              any("Bad_Tag" in p for p in probs), True)
        rc = main(["--notebooks", badpath, "--out", os.path.join(tmp, "bad")])
        check("a malformed tag makes the run exit nonzero", rc, 1)

        outdir = os.path.join(tmp, "code")
        rc = main(["--notebooks", nbpath,
                   "--out", outdir, "--tag", "fixture"])
        check("writing one clean tag exits 0", rc, 0)
        gen = open(os.path.join(outdir, "fixture.tex"), encoding="utf-8").read()
        check("generated file names the house style",
              "style=pyomohandout" in gen, True)
        check("generated file records its source",
              "cell 1" in gen, True)
        parsed = parse_generated(gen)
        check("parse_generated round-trips the body",
              parsed["body"] == transform(cell), True)
        check("parse_generated round-trips the hash",
              parsed["normhash"] == digest(cell), True)

        rc = main(["--notebooks", nbpath,
                   "--out", outdir, "--tag", "fixture", "--check"])
        check("--check on a fresh file exits 0", rc, 0)

        with open(os.path.join(outdir, "fixture.tex"), "a") as fh:
            fh.write("% hand-edited\n")
        rc = main(["--notebooks", nbpath,
                   "--out", outdir, "--tag", "fixture", "--check"])
        check("--check FAILS on a hand-edited file", rc, 1)

        rc = main(["--notebooks", nbpath,
                   "--out", outdir, "--tag", "has-solve"])
        check("a cell containing a solve is REFUSED", rc, 1)
        check("...and no file is written",
              os.path.exists(os.path.join(outdir, "has-solve.tex")), False)
        rc = main(["--notebooks", nbpath,
                   "--out", outdir, "--tag", "has-solve", "--allow-scope"])
        check("--allow-scope writes it anyway", rc, 0)

    print()
    print("SELF-TEST PASSED" if ok else "SELF-TEST FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
