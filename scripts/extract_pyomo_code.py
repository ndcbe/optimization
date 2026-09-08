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

THE OUTPUT HALF
---------------
Prof. Dowling, 2026-09-08, on the Lecture 7 race-car section:

    "Instead, let's show the Pyomo code and the numerical results."
    "You may need to extend our infrastructure to also import output from a
     website notebook. This is a good investment of time."

A cell tagged ``handout-output:<tag>`` has its stored OUTPUT extracted into
``lecture-notes/code/output/<tag>.tex``, typeset by ``\pyomooutput{<tag>}``. The
tag prefix, the directory and the macro are all distinct from the model half,
because the two are not the same kind of thing:

  * A ``handout:`` listing is a MODEL. It is deterministic text, it is pinned to
    its cell, and ``check_code_sync.py`` fails when it drifts.
  * A ``handout-output:`` listing is a SOLVER LOG. It is a trace of one run on
    one machine with one solver build.

🔴 WHY OUTPUTS ARE NOT PINNED
-----------------------------
``check_code_sync.py`` opens with a rule that must not be quietly repealed here:

    "Do not extend this to a solver trace, an iteration table, or any printed
     number that is not reproducible. 'Correct forever' only means anything if
     the thing pinned is stable; pin an unstable trace and the checker starts
     failing for reasons that have nothing to do with the pack, and whoever
     silences it will silence the real failures with it."

That rule is about *pinning*, not about *printing*, and this half does not pin
anything. The output is copied out of the notebook the notebook's author
executed, with provenance recorded in the file header, and nothing asserts that
re-running produces it again. Two consequences worth stating out loud:

  * ``code/output/`` is OUTSIDE the directory ``check_code_sync.py`` scans, so a
    log can never make ``verify_all.sh`` red.
  * That also means nothing warns you when the notebook is re-executed and the
    handout keeps last month's log. ``--check`` is the tool for that, and it is
    the author's job to run it after re-executing a notebook. This is a
    deliberate trade: an advisory staleness check you can run, rather than a
    mandatory one that would eventually be switched off.

ELISION
-------
    "include the first 10 iterations and the last 10 iterations. I want you to
     also show the Ipopt problem size statements."

An Ipopt log of an 80-iteration solve does not belong in a handout whole. The
first ``head`` and last ``tail`` lines are kept with a marker naming how many
lines were dropped, so the reader can see that the log was cut and by how much.
Both are configurable per cell, in the cell's own metadata::

    "metadata": {"tags": ["handout-output:race-car-coarse"],
                 "handout_output": {"head": 45, "tail": 30}}

Defaults are in ``OUTPUT_DEFAULTS``. The head default is measured against a real
Ipopt 3.13.2 log rather than chosen: the banner and the problem-size block run
to roughly line 30, so the default head reaches into the iteration table with
the statistics intact.

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

# --- the OUTPUT half (added 2026-09-08) ------------------------------------
# Prof. Dowling, on Lecture 7: "Instead, let's show the Pyomo code and the
# numerical results." ... "You may need to extend our infrastructure to also
# import output from a website notebook. This is a good investment of time."
#
# So a second tag prefix, deliberately NOT a variant of the first: a cell tagged
# ``handout-output:<tag>`` has its stored OUTPUT (not its source) typeset into
# ``lecture-notes/code/output/<tag>.tex``.
OUTPUT_TAG_PREFIX = "handout-output:"
# ...and a SUBDIRECTORY, which is load-bearing rather than tidiness.
# ``check_code_sync.py`` globs ``code/*.tex`` (non-recursive) and calls any file
# there with no matching ``handout:`` cell an ORPHAN. Writing outputs beside the
# models as ``code/<tag>-output.tex`` would make every one of them a standing
# ORPHAN failure in verify_all.sh. The subdirectory keeps the two populations
# apart, and it says the true thing about them: a model listing is PINNED to its
# cell and a solver log is not (see WHY OUTPUTS ARE NOT PINNED, below).
OUTPUT_SUBDIR = "output"
# Per-cell configuration lives in the cell's own metadata, e.g.
#     "metadata": {"tags": ["handout-output:race-car-coarse"],
#                  "handout_output": {"head": 40, "tail": 15}}
OUTPUT_META_KEY = "handout_output"
OUTPUT_DEFAULTS = {
    # Lines to DROP from the front before head/tail are applied. Added
    # 2026-09-08: a second solve of the same model repeats Ipopt's ~30-line
    # licence banner verbatim, which is pure noise the second time, but `head`
    # alone cannot skip it -- head counts from line 1, so trimming the banner
    # also trims the problem-size block that Prof. Dowling explicitly asked to
    # keep ("I want you to also show the Ipopt problem size statements").
    # `skip` removes the banner and LEAVES the statistics.
    "skip": 0,
    # Enough head to clear the Ipopt banner AND the problem-size block --
    # "I want you to also show the Ipopt problem size statements" -- and still
    # reach the first iterations. Measured on a real Ipopt 3.13.2 log: banner
    # and statistics run to line ~30, so 45 lines lands ~10 iterations in.
    "head": 45,
    # "include the first 10 iterations and the last 10 iterations": the last
    # iterations plus the EXIT line and the timing summary.
    "tail": 30,
    # Which stored outputs to take. "stdout" is the solver log under tee=True;
    # "all" adds stderr, execute_result and display_data text/plain.
    "streams": "stdout",
    # Hard wrap guard. The pyomooutput listing style fits ~106 characters; an
    # Ipopt iteration line is ~95. A line longer than this is truncated with a
    # visible marker rather than silently wrapped or silently cut.
    "width": 106,
}


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
# OUTPUT EXTRACTION
# ---------------------------------------------------------------------------
# Everything below is the second half described in THE OUTPUT HALF above. It
# shares the scanning, the banner and the file-writing discipline with the model
# half, and shares nothing with the *pinning* half on purpose.

# ANSI colour/cursor sequences. Solvers do not emit these, but tqdm, rich and a
# stray `print("\033[1m...")` do, and a raw escape byte in a .tex file is a
# LaTeX error whose message points nowhere near the notebook.
ANSI_RE = re.compile(r"\x1b\[[0-9;?]*[A-Za-z]")

# Characters a listing environment handles fine as bytes but that would arrive
# as mojibake or a missing glyph in a pdflatex T1 font. Mapped rather than
# dropped where there is an obvious ASCII spelling; see sanitize_output.
UNICODE_FALLBACKS = {
    "‘": "'", "’": "'", "“": '"', "”": '"',
    "–": "-", "—": "--", "…": "...", " ": " ",
    "−": "-", "µ": "u", "≤": "<=", "≥": ">=",
    "×": "x", "→": "->", "∞": "inf", "°": "deg",
    "✓": "[ok]", "✗": "[x]", "⚠": "[!]",
}

ELISION = "...  [ {n} lines omitted ]  ..."
TRUNCATED = " [...]"


def output_config(meta: dict) -> dict:
    """Merge a cell's ``handout_output`` metadata over the defaults.

    Unknown keys are an error rather than a silent no-op: a typo'd ``"heads"``
    that quietly kept the default is the sort of thing nobody notices until the
    handout is printed with the wrong 45 lines.
    """
    cfg = dict(OUTPUT_DEFAULTS)
    raw = (meta or {}).get(OUTPUT_META_KEY) or {}
    if not isinstance(raw, dict):
        raise ValueError(f"{OUTPUT_META_KEY!r} metadata must be a mapping, "
                         f"got {type(raw).__name__}")
    unknown = set(raw) - set(OUTPUT_DEFAULTS)
    if unknown:
        raise ValueError(f"unknown {OUTPUT_META_KEY} key(s): "
                         f"{', '.join(sorted(unknown))}; known keys are "
                         f"{', '.join(sorted(OUTPUT_DEFAULTS))}")
    cfg.update(raw)
    for k in ("skip", "head", "tail", "width"):
        if not isinstance(cfg[k], int) or cfg[k] < 0:
            raise ValueError(f"{OUTPUT_META_KEY}.{k} must be a non-negative "
                             f"integer, got {cfg[k]!r}")
    if cfg["streams"] not in ("stdout", "all"):
        raise ValueError(f"{OUTPUT_META_KEY}.streams must be 'stdout' or "
                         f"'all', got {cfg['streams']!r}")
    return cfg


def _text_of(payload) -> str:
    """nbformat stores text as either a string or a list of lines. Accept both."""
    if isinstance(payload, list):
        return "".join(payload)
    return payload or ""


def cell_output_text(outputs, streams: str = "stdout") -> str:
    """The stored output of one cell, flattened to plain text.

    ``tee=True`` puts the whole solver log on stdout, so ``streams='stdout'`` is
    the log and nothing else -- no ``execute_result`` repr of the results object
    trailing after it. ``streams='all'`` additionally takes stderr and the
    ``text/plain`` rendering of results and displays.

    An image output has no text form and is skipped rather than described; a
    figure belongs in the ``figure:<name>`` pipeline, not here.
    """
    chunks = []
    for out in outputs or []:
        kind = out.get("output_type")
        if kind == "stream":
            name = out.get("name", "stdout")
            if streams == "stdout" and name != "stdout":
                continue
            chunks.append(_text_of(out.get("text")))
        elif kind == "error":
            # Always kept, in both modes. A traceback in a cell whose output is
            # being typeset is not something to filter out by default.
            chunks.append("\n".join(_text_of(t) for t in
                                    (out.get("traceback") or [])))
        elif kind in ("execute_result", "display_data"):
            if streams != "all":
                continue
            data = out.get("data") or {}
            if "text/plain" in data:
                chunks.append(_text_of(data["text/plain"]))
    return "".join(chunks)


def sanitize_output(text: str, width: int = 0) -> tuple[str, list[str]]:
    """Make arbitrary captured stdout safe to ``\\input`` inside a listing.

    Returns ``(clean text, notes)``; the notes are written into the generated
    file's header so a reader of the PDF's source can see what was changed.

    A listing environment is verbatim -- backslashes and braces in the log are
    NOT a problem and are deliberately left alone -- so this handles only the
    four things that genuinely break or degrade:

      1. ANSI escapes and other control bytes, which are LaTeX errors.
      2. ``\\end{lstlisting}`` appearing in the data, which would close the
         environment early. Impossible from a solver, trivial from a cell that
         prints LaTeX, and catastrophic if it ever happened -- the build breaks
         hundreds of lines later with no clue where.
      3. Non-ASCII, which pdflatex renders as mojibake or drops.
      4. Tabs, which listings expands against a tabsize the log did not assume.
    """
    notes: list[str] = []

    n_ansi = len(ANSI_RE.findall(text))
    if n_ansi:
        text = ANSI_RE.sub("", text)
        notes.append(f"{n_ansi} ANSI escape sequence(s) removed")

    if r"\end{lstlisting}" in text:
        text = text.replace(r"\end{lstlisting}", r"\end {lstlisting}")
        notes.append(r"'\end{lstlisting}' in the output was broken with a "
                     "space so it cannot close the listing")

    for bad, good in UNICODE_FALLBACKS.items():
        if bad in text:
            text = text.replace(bad, good)
    stray = sorted({c for c in text if ord(c) > 126})
    if stray:
        for c in stray:
            text = text.replace(c, "?")
        notes.append(f"{len(stray)} non-ASCII character(s) replaced with '?': "
                     + " ".join(f"U+{ord(c):04X}" for c in stray))

    text = text.replace("\r\n", "\n").replace("\r", "\n")

    # BACKSPACES ARE APPLIED, not replaced. Ipopt's ASL driver ends its run by
    # backspacing over the "Ipopt 3.13.2: " it printed before the log, so the
    # captured stdout of a tee=True solve really does contain a run of \x08.
    # Replacing them with spaces (which the control sweep below would do) puts
    # fourteen leading blanks in front of the last line of every solver log;
    # applying them is both correct and what the reader saw on screen.
    if "\x08" in text:
        out = []
        for line in text.split("\n"):
            if "\x08" not in line:
                out.append(line)
                continue
            buf: list[str] = []
            for ch in line:
                if ch == "\x08":
                    if buf:
                        buf.pop()
                else:
                    buf.append(ch)
            out.append("".join(buf))
        text = "\n".join(out)
        notes.append("backspace characters applied (the ASL driver backspaces "
                     "over its own banner at the end of a solve)")

    text = text.expandtabs(8)
    # Remaining control characters (form feed, bell, NUL) have no verbatim
    # meaning and at least one of them is fatal.
    ctrl = sorted({c for c in text if ord(c) < 32 and c != "\n"})
    if ctrl:
        for c in ctrl:
            text = text.replace(c, " ")
        notes.append(f"{len(ctrl)} control character(s) replaced with a space")

    lines = [l.rstrip() for l in text.split("\n")]
    if width:
        cut = 0
        for i, l in enumerate(lines):
            if len(l) > width:
                lines[i] = l[:width - len(TRUNCATED)] + TRUNCATED
                cut += 1
        if cut:
            notes.append(f"{cut} line(s) longer than {width} characters "
                         f"truncated with '{TRUNCATED.strip()}'")

    while lines and not lines[-1]:
        lines.pop()
    while lines and not lines[0]:
        lines.pop(0)
    return "\n".join(lines), notes


def elide(text: str, head: int, tail: int, skip: int = 0) -> tuple[str, int]:
    """Drop ``skip`` leading lines, then keep the first ``head`` and last ``tail``.

    Returns (text, dropped), where ``dropped`` counts the skipped lines too --
    the marker must account for every line the reader is not being shown, or it
    understates the cut.

    The marker names the number of dropped lines rather than saying "...", so a
    reader can tell a 6-line cut from a 600-line one, and so nobody mistakes the
    printed log for the whole log.

    ``head + tail >= len(lines)`` returns the text untouched: eliding two lines
    to save one is worse than not eliding, and a marker claiming an elision that
    barely happened is misleading.
    """
    lines = text.split("\n")
    if skip:
        skipped, lines = lines[:skip], lines[skip:]
    else:
        skipped = []
    if head + tail >= len(lines):
        if not skipped:
            return text, 0
        # Nothing to elide in the middle, but the skipped head still has to be
        # declared -- silently dropping it would misreport the log.
        return "\n".join([ELISION.format(n=len(skipped))] + lines), len(skipped)
    dropped = len(lines) - head - tail + len(skipped)
    kept = ([ELISION.format(n=len(skipped))] if skipped else []) \
        + lines[:head] + [ELISION.format(n=len(lines) - head - tail)]
    if tail:
        kept += lines[-tail:]
    return "\n".join(kept), dropped


class OutputSnippet:
    """A cell whose OUTPUT is being extracted. Deliberately parallel to Snippet."""

    def __init__(self, tag, notebook, index, text, config):
        self.tag = tag
        self.notebook = notebook
        self.index = index
        self.text = text
        self.config = config

    @property
    def rel(self):
        return _display(self.notebook)


def read_cells_full(path: str):
    """(index, cell_type, tags, source, metadata, outputs) for every cell.

    A separate reader rather than a wider return from ``read_cells``: that
    function's four-tuple is used by ``find_snippets`` and imported by
    ``check_code_sync.py``, and widening a shared tuple to serve a new caller is
    how the other caller breaks silently.
    """
    try:
        import nbformat

        nb = nbformat.read(path, as_version=4)
        cells = nb.cells
    except Exception:
        nb = json.load(open(path, encoding="utf-8"))
        cells = nb.get("cells", [])

    for i, cell in enumerate(cells):
        src = cell.get("source", "")
        meta = cell.get("metadata", {}) or {}
        yield (i, cell.get("cell_type"),
               list(meta.get("tags", []) or []),
               "".join(src) if isinstance(src, list) else src,
               dict(meta),
               list(cell.get("outputs", []) or []))


def find_output_snippets(patterns: list[str]) -> tuple[list, list[str]]:
    """Every ``handout-output:<tag>`` code cell, plus complaints.

    An UNEXECUTED tagged cell is a problem, not an empty file. A cell with no
    stored output is what you get from a notebook that was cleared or never run,
    and writing an empty listing would put a blank box in the handout that looks
    like a typesetting bug rather than a missing solve.
    """
    snippets, problems = [], []
    seen: dict[str, OutputSnippet] = {}
    for pattern in patterns:
        for path in sorted(glob.glob(pattern)):
            if ".ipynb_checkpoints" in path:
                continue
            try:
                cells = list(read_cells_full(path))
            except Exception as exc:                        # noqa: BLE001
                problems.append(f"{path}: unreadable ({exc})")
                continue
            for i, ctype, tags, _src, meta, outputs in cells:
                for tag in tags:
                    if not tag.startswith(OUTPUT_TAG_PREFIX):
                        continue
                    name = tag[len(OUTPUT_TAG_PREFIX):]
                    rel = _display(path)
                    if ctype != "code":
                        problems.append(
                            f"{rel} cell {i}: tag {tag!r} is on a {ctype} "
                            "cell; only code cells have output")
                        continue
                    if not TAG_RE.match(name):
                        problems.append(
                            f"{rel} cell {i}: tag {name!r} must match "
                            f"{TAG_RE.pattern} -- it becomes a filename")
                        continue
                    if name in seen:
                        problems.append(
                            f"output tag {name!r} claimed twice: "
                            f"{seen[name].rel} cell {seen[name].index} and "
                            f"{rel} cell {i}")
                        continue
                    try:
                        cfg = output_config(meta)
                    except ValueError as exc:
                        problems.append(f"{rel} cell {i}: {exc}")
                        continue
                    text = cell_output_text(outputs, cfg["streams"])
                    if not text.strip():
                        problems.append(
                            f"{rel} cell {i}: tag {tag!r} has no stored "
                            f"{cfg['streams']} output -- execute the notebook "
                            "and save it before extracting")
                        continue
                    s = OutputSnippet(name, path, i, text, cfg)
                    seen[name] = s
                    snippets.append(s)
    snippets.sort(key=lambda s: s.tag)
    return snippets, problems


def render_output(snip: OutputSnippet) -> str:
    """The full text of ``lecture-notes/code/output/<tag>.tex``."""
    cfg = snip.config
    clean, notes = sanitize_output(snip.text, cfg["width"])
    total = len(clean.split("\n"))
    body, dropped = elide(clean, cfg["head"], cfg["tail"], cfg["skip"])

    lines = [
        BANNER,
        "% GENERATED FILE -- DO NOT EDIT.",
        "%",
        f"% tag       : {snip.tag}",
        f"% source    : optimization/{snip.rel}, cell {snip.index} OUTPUT",
        f"% generator : {GENERATOR}",
        f"% lines     : {total} captured, "
        + (f"{dropped} elided ({cfg['head']} head + {cfg['tail']} tail kept)"
           if dropped else "none elided"),
        "%",
    ]
    for n in notes:
        lines.append(f"% sanitised : {n}")
    lines += [
        "% This is a SOLVER LOG, not a model. It is a record of one run and is",
        "% NOT pinned by check_code_sync.py -- see 'WHY OUTPUTS ARE NOT PINNED'",
        f"% in {GENERATOR}. Re-executing the notebook changes it; regenerate",
        f"% with:  python3 {GENERATOR} --tag {snip.tag}",
        BANNER,
        r"\begin{lstlisting}[style=pyomooutput]",
        body,
        r"\end{lstlisting}",
        "",
    ]
    return "\n".join(lines)


def parse_generated_output(text: str) -> dict:
    """Pull the log body and provenance back out of a generated output file."""
    o = LISTING_OPEN.search(text)
    c = LISTING_CLOSE.search(text)
    body = None
    if o and c and c.start() > o.end():
        body = text[o.end():c.start()].strip("\n")
    s = OUTPUT_SOURCE_RE.search(text)
    return {
        "body": body,
        "notebook": s.group(1) if s else None,
        "cell": int(s.group(2)) if s else None,
    }


OUTPUT_SOURCE_RE = re.compile(r"^%\s*source\s*:\s*(.+?), cell (\d+) OUTPUT\s*$",
                              re.M)


def output_dir_of(out_root: str) -> str:
    return os.path.join(out_root, OUTPUT_SUBDIR)


def process_outputs(snippets, out_root: str, check: bool) -> tuple[list, list]:
    """Write (or --check) every output file. Returns (written, changed)."""
    outdir = output_dir_of(out_root)
    if not check:
        os.makedirs(outdir, exist_ok=True)
    written, changed = [], []
    for s in snippets:
        text = render_output(s)
        path = os.path.join(outdir, f"{s.tag}.tex")
        old = open(path, encoding="utf-8").read() if os.path.exists(path) else None
        if old == text:
            print(f"  ok    {s.tag:<28} unchanged (output)")
            continue
        changed.append(s.tag)
        if check:
            print(f"  STALE {s.tag:<28} {os.path.relpath(path)} "
                  f"{'differs' if old is not None else 'missing'} (output)")
            continue
        with open(path, "w", encoding="utf-8") as fh:
            fh.write(text)
        written.append(s.tag)
        print(f"  wrote {s.tag:<28} {os.path.relpath(path)}  (output)")
    return written, changed


def output_orphans(snippets, out_root: str) -> list[str]:
    """Generated output files whose tag no longer exists in any notebook.

    ``check_code_sync.py`` cannot see this directory (that is the whole point of
    the subdirectory), so the orphan check for outputs lives here instead.
    """
    outdir = output_dir_of(out_root)
    if not os.path.isdir(outdir):
        return []
    have = {s.tag for s in snippets}
    return [os.path.basename(p)[:-4]
            for p in sorted(glob.glob(os.path.join(outdir, "*.tex")))
            if os.path.basename(p)[:-4] not in have]


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
    ap.add_argument("--no-outputs", action="store_true",
                    help=f"skip '{OUTPUT_TAG_PREFIX}<tag>' cells; extract only "
                         "the model listings")
    ap.add_argument("--keep-docstrings", action="store_true",
                    help="keep function docstrings (dropped by default)")
    ap.add_argument("--selftest", action="store_true",
                    help="prove the transformations, and prove they can fail")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    snippets, problems = find_snippets(args.notebooks)
    outsnips, outproblems = ([], []) if args.no_outputs else \
        find_output_snippets(args.notebooks)
    problems += outproblems
    if args.tag:
        want = set(args.tag)
        missing = want - {s.tag for s in snippets} - {s.tag for s in outsnips}
        for m in sorted(missing):
            problems.append(f"tag {m!r} requested but not found in any notebook")
        snippets = [s for s in snippets if s.tag in want]
        outsnips = [s for s in outsnips if s.tag in want]

    # ORPHANS. check_code_sync.py does this for the model half; it cannot see
    # code/output/, so the output half reports its own. Advisory (a PROBLEM,
    # which is a nonzero exit here) rather than a deletion: removing a file the
    # pack still \pyomooutput's would break the build silently.
    if not args.no_outputs and not args.tag:
        for orphan in output_orphans(outsnips, args.out):
            problems.append(
                f"code/{OUTPUT_SUBDIR}/{orphan}.tex is an ORPHAN: no cell "
                f"carries '{OUTPUT_TAG_PREFIX}{orphan}' any more")

    for p in problems:
        print(f"  PROBLEM  {p}", file=sys.stderr)

    if not snippets and not outsnips:
        print(f"No cells tagged '{TAG_PREFIX}<tag>' or "
              f"'{OUTPUT_TAG_PREFIX}<tag>' in: {', '.join(args.notebooks)}")
        print("Add a cell tag in JupyterLab's Property Inspector, e.g. "
              f"'{TAG_PREFIX}battery-model'.")
        return 1 if problems else 0

    if args.list:
        print(f"{len(snippets)} tagged code cell(s):\n")
        for s in snippets:
            code = transform(s.source, keep_docstrings=args.keep_docstrings)
            v = scope_violations(s.source)
            print(f"  {s.tag:<28} {s.rel} cell {s.index}   "
                  f"{len(s.source.splitlines()):>3} -> "
                  f"{len(code.splitlines()):>3} lines"
                  f"{'   SCOPE: ' + str(len(v)) if v else ''}")
        if outsnips:
            print(f"\n{len(outsnips)} tagged output cell(s):\n")
            for s in outsnips:
                clean, _ = sanitize_output(s.text, s.config["width"])
                total = len(clean.split("\n"))
                _, dropped = elide(clean, s.config["head"], s.config["tail"],
                                   s.config["skip"])
                print(f"  {s.tag:<28} {s.rel} cell {s.index}   "
                      f"{total:>4} -> {total - dropped:>4} lines"
                      f"{f'   (elided {dropped})' if dropped else ''}")
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

    outwritten, outchanged = process_outputs(outsnips, args.out, args.check)
    written += outwritten
    changed += outchanged
    n_total = len(snippets) + len(outsnips)

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
        print(f"UP TO DATE: {n_total} snippet(s).")
        return 1 if problems else 0
    print(f"{len(written)} written, {n_total - len(written)} unchanged.")
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

    # --- THE OUTPUT HALF ---------------------------------------------------
    # Same discipline as above: every case says what must happen AND what must
    # not. The failure this section is really guarding against is a log that
    # typesets fine on the day and breaks the pack six months later because
    # somebody's cell printed a character pdflatex cannot set.

    # sanitize_output: the four things that break a listing
    clean, notes = sanitize_output("plain ipopt line\n")
    check("clean text is left alone", clean, "plain ipopt line")
    check("...and reports no changes", notes, [])

    clean, notes = sanitize_output("a \x1b[31mred\x1b[0m b\n")
    check("ANSI escapes removed", clean, "a red b")
    check("...and reported", any("ANSI" in n for n in notes), True)

    clean, notes = sanitize_output("before\n\\end{lstlisting}\nafter\n")
    check("a stray \\end{lstlisting} cannot close the listing",
          "\\end{lstlisting}" in clean, False)
    check("...and the line survives in readable form",
          "\\end {lstlisting}" in clean, True)

    clean, notes = sanitize_output("mu = 1e-8 \u00b5s and \u2264 tol\n")
    check("known Unicode is mapped, not dropped", "us and <= tol" in clean, True)
    clean, notes = sanitize_output("solver \u2603 says hi\n")
    check("unknown non-ASCII becomes '?'", "?" in clean, True)
    check("...and names the codepoint",
          any("U+2603" in n for n in notes), True)
    check("no non-ASCII survives sanitisation",
          all(ord(c) < 127 for c in clean), True)

    clean, _ = sanitize_output("a\tb\n")
    check("tabs are expanded", "\t" in clean, False)
    clean, notes = sanitize_output("a\x0cb\n")
    check("control characters removed", "\x0c" in clean, False)
    clean, notes = sanitize_output("Ipopt 3.13.2: \x08\x08final\n")
    check("backspaces are APPLIED, not blanked", clean, "Ipopt 3.13.2final")
    check("...and reported", any("backspace" in n for n in notes), True)
    check("a leading backspace run just disappears",
          sanitize_output("x\n\x08\x08final time = 1\n")[0],
          "x\nfinal time = 1")

    clean, notes = sanitize_output("x" * 200 + "\n", width=50)
    check("an over-wide line is truncated", len(clean), 50)
    check("...visibly", clean.endswith(TRUNCATED), True)
    check("...and reported", any("truncated" in n for n in notes), True)
    check("a line at the limit is NOT truncated",
          sanitize_output("y" * 50 + "\n", width=50)[0], "y" * 50)

    # backslashes and braces are DATA in a verbatim listing and must survive
    clean, _ = sanitize_output("norm ||d|| {a} \\frac 50% $x\n")
    check("verbatim-safe characters are untouched",
          clean, "norm ||d|| {a} \\frac 50% $x")

    # elide: head/tail and the marker
    body = "\n".join(f"L{i}" for i in range(100))
    got, dropped = elide(body, 10, 5)
    check("elision drops the middle", dropped, 85)
    lines = got.split("\n")
    check("...keeping the head", lines[:2], ["L0", "L1"])
    check("...keeping the tail", lines[-1], "L99")
    check("...with a marker naming the count",
          ELISION.format(n=85) in got, True)
    check("elided length = head + tail + marker", len(lines), 16)
    got, dropped = elide("a\nb\nc", 10, 10)
    check("a short log is NOT elided", (got, dropped), ("a\nb\nc", 0))
    got, dropped = elide(body, 100, 0)
    check("head covering everything is not elided", dropped, 0)

    # elide: the skip option (added 2026-09-08)
    got, dropped = elide(body, 10, 5, skip=20)
    lines = got.split("\n")
    check("skip drops the leading lines", lines[1], "L20")
    check("...declares them in a marker", lines[0], ELISION.format(n=20))
    check("...and counts them in dropped", dropped, 85)
    check("...still keeps the tail", lines[-1], "L99")
    got, dropped = elide(body, 100, 0, skip=20)
    check("skip is declared even when nothing else is elided",
          got.split("\n")[0], ELISION.format(n=20))
    check("...and reports exactly the skipped count", dropped, 20)
    check("skip=0 is identical to no skip",
          elide(body, 10, 5, skip=0), elide(body, 10, 5))

    # output_config: defaults, overrides, and typos
    check("defaults apply", output_config({})["head"], OUTPUT_DEFAULTS["head"])
    check("metadata overrides",
          output_config({OUTPUT_META_KEY: {"head": 3}})["head"], 3)
    for bad, why in [
        ({"heads": 3}, "a typo'd key"),
        ({"head": -1}, "a negative head"),
        ({"head": "5"}, "a string head"),
        ({"streams": "stdin"}, "an unknown stream"),
    ]:
        raised = False
        try:
            output_config({OUTPUT_META_KEY: bad})
        except ValueError:
            raised = True
        check(f"output_config REJECTS {why}", raised, True)

    # cell_output_text: which streams
    outs = [
        {"output_type": "stream", "name": "stdout", "text": ["log line\n"]},
        {"output_type": "stream", "name": "stderr", "text": ["a warning\n"]},
        {"output_type": "execute_result",
         "data": {"text/plain": "<results object>"}},
        {"output_type": "display_data", "data": {"image/png": "AAAA"}},
    ]
    check("stdout mode takes only the log",
          cell_output_text(outs, "stdout"), "log line\n")
    got = cell_output_text(outs, "all")
    check("all mode adds stderr and the repr",
          ("a warning" in got and "<results object>" in got), True)
    check("an image output is never text", "AAAA" in got, False)
    check("a traceback is kept in stdout mode",
          "ZeroDivision" in cell_output_text(
              [{"output_type": "error", "ename": "ZeroDivisionError",
                "traceback": ["ZeroDivisionError: division by zero"]}]),
          True)

    # --- round trip through a real notebook, output half -------------------
    with tempfile.TemporaryDirectory() as tmp:
        nbdir = os.path.join(tmp, "notebooks", "3-dev")
        os.makedirs(nbdir)
        nbpath = os.path.join(nbdir, "Out.ipynb")
        log = "".join(f"iter {i}\n" for i in range(60))
        json.dump({"cells": [
            {"cell_type": "code",
             "metadata": {"tags": ["handout-output:solve-log"],
                          OUTPUT_META_KEY: {"head": 4, "tail": 2}},
             "source": ["solver.solve(m, tee=True)\n"],
             "outputs": [{"output_type": "stream", "name": "stdout",
                          "text": [log]}],
             "execution_count": 1},
        ], "metadata": {}, "nbformat": 4, "nbformat_minor": 5},
            open(nbpath, "w"))

        # As in the model half above, the BAD fixture is a separate file so the
        # exit statuses asserted below are not confounded by a standing PROBLEM.
        badpath = os.path.join(nbdir, "NeverRun.ipynb")
        json.dump({"cells": [
            {"cell_type": "code",
             "metadata": {"tags": ["handout-output:never-run"]},
             "source": ["print(1)\n"], "outputs": [], "execution_count": None},
        ], "metadata": {}, "nbformat": 4, "nbformat_minor": 5},
            open(badpath, "w"))

        snips, probs = find_output_snippets([nbpath])
        check("finds the executed output cell",
              [s.tag for s in snips], ["solve-log"])
        _, probs = find_output_snippets([badpath])
        check("an UNEXECUTED tagged cell is a PROBLEM, not an empty file",
              any("never-run" in p and "no stored" in p for p in probs), True)
        check("...and nonzero exit follows",
              main(["--notebooks", badpath,
                    "--out", os.path.join(tmp, "bad")]), 1)

        outdir = os.path.join(tmp, "code")
        rc = main(["--notebooks", nbpath, "--out", outdir, "--tag", "solve-log"])
        check("writing one output tag exits 0", rc, 0)
        gen_path = os.path.join(outdir, OUTPUT_SUBDIR, "solve-log.tex")
        check("output lands in code/output/, NOT beside the models",
              os.path.exists(gen_path), True)
        check("...and nothing was written where check_code_sync.py looks",
              os.path.exists(os.path.join(outdir, "solve-log.tex")), False)
        gen = open(gen_path, encoding="utf-8").read()
        check("generated output names its own listing style",
              "style=pyomooutput" in gen, True)
        check("generated output records its source cell",
              "cell 0 OUTPUT" in gen, True)
        check("generated output says it is not pinned",
              "NOT pinned" in gen, True)
        parsed = parse_generated_output(gen)
        check("parse_generated_output round-trips the cell index",
              parsed["cell"], 0)
        check("the body is elided as configured",
              parsed["body"].split("\n"), ["iter 0", "iter 1", "iter 2",
                                           "iter 3", ELISION.format(n=54),
                                           "iter 58", "iter 59"])

        rc = main(["--notebooks", nbpath, "--out", outdir,
                   "--tag", "solve-log", "--check"])
        check("--check on a fresh output file exits 0", rc, 0)
        check("re-running is idempotent",
              open(gen_path, encoding="utf-8").read(), gen)

        with open(gen_path, "a") as fh:
            fh.write("% hand-edited\n")
        rc = main(["--notebooks", nbpath, "--out", outdir,
                   "--tag", "solve-log", "--check"])
        check("--check FAILS on a hand-edited output file", rc, 1)
        main(["--notebooks", nbpath, "--out", outdir, "--tag", "solve-log"])

        # ORPHAN: a generated log whose tag is gone from the notebook
        with open(os.path.join(outdir, OUTPUT_SUBDIR, "gone.tex"), "w") as fh:
            fh.write("% stale\n")
        rc = main(["--notebooks", nbpath, "--out", outdir])
        check("an orphaned output file makes the run exit nonzero", rc, 1)
        check("...and the file is NOT deleted",
              os.path.exists(os.path.join(outdir, OUTPUT_SUBDIR, "gone.tex")),
              True)
        os.remove(os.path.join(outdir, OUTPUT_SUBDIR, "gone.tex"))

        os.remove(gen_path)
        rc = main(["--notebooks", nbpath, "--out", outdir, "--no-outputs"])
        check("--no-outputs ignores the output cells entirely", rc, 0)
        check("...and writes nothing", os.path.exists(gen_path), False)

    print()
    print("SELF-TEST PASSED" if ok else "SELF-TEST FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
