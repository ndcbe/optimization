#!/usr/bin/env python3
"""Freeze the notebooks' PROSE and detect drift, so AI voice cannot displace human voice.

WHY THIS EXISTS
---------------
Prof. Dowling, 2026-08-21:

    "As the semester progresses, I plan on carefully checking over and refining
    the lecture notes. That will include refining text and manually checking AI
    generated text. I want to make sure that AI generated text in the current
    draft lecture notes does not spill over into the notebooks. The notebooks
    predate the widespread adoption of LLMs. They are written in mainly my
    voice, or voices of past students if they are contributed notebooks. I do
    not want to loose these voices in favor of an AI voice."

The notebooks are a pre-LLM corpus in HUMAN voices -- his, and past students' in
``notebooks/contrib/``. The LaTeX course pack in ``optimization-private/lecture-notes/``
is the opposite: a large amount of AI-drafted prose currently under revision.

There is real, deliberate traffic between the two. Pyomo models are single-sourced
from the notebooks into the handouts by ``extract_pyomo_code.py``. Every refinement
pass on a handout therefore puts an editor -- human or agent -- in both files on the
same afternoon, holding the handout's phrasing in mind while looking at the notebook.
Over months of such passes, handout prose migrating into notebook markdown is not a
far-fetched risk; it is the default outcome of ordinary carelessness.

"Don't let that happen" is a hope. This makes it a machine-checked invariant.

⚠ THE ANCHOR IS A COMMIT, NOT THE WORKING TREE
----------------------------------------------
    ANCHOR = feb00d2  "Redirect legacy JupyterBook 1 URLs to their MyST
                       equivalents", 2026-08-17

Every ``anchor`` hash in the baseline JSON is read with ``git show feb00d2:<path>``,
never from disk. Three reasons, and the first is the one that forced this design:

1. **A working-tree snapshot races the workers.** Agents were editing ``-dev``
   notebooks while this baseline was being captured. A disk snapshot would hash
   some notebooks before an edit and others after it, and NOTHING in the resulting
   file would say which. That is worse than no baseline, because it looks
   authoritative.
2. **A commit is exactly reproducible forever.** Anyone can re-derive the anchor
   hashes from git and get the same numbers, next week or next year.
3. **feb00d2 is a genuine pre-agent reference.** Agent editing of ``-dev``
   notebooks began 2026-08-18; feb00d2 is the last commit before it. A baseline
   taken from disk on 2026-08-21 would already be 47 commits late.

The anchor is IMMUTABLE. ``--update`` never touches it.

TWO LAYERS: `anchor` AND `current`
----------------------------------
``anchor``  -- from feb00d2. The pre-agent human corpus. Never updated.
``current`` -- from the working tree, timestamped, with a logged reason. This is
               what a plain run compares against, and it is expected to move as
               prose is legitimately refined.

Both are kept, clearly separated, because they answer different questions. The
anchor answers "is this still the prose the humans wrote?" -- and its diff against
``current``, stored as ``drift_from_anchor``, is the standing audit of what agent
work has already done to that prose. ``current`` answers "has anything changed
since the last time a person looked?", which is the question a pre-publish gate
needs, and the only one that can be asked without the alarm crying wolf about the
47 commits that are already in.

VOICES, PLURAL -- THE CHECK RUNS IN BOTH DIRECTIONS
---------------------------------------------------
The instruction is to preserve *the voices*, not to converge on one. A contributed
notebook rewritten into Prof. Dowling's voice is just as much a loss as one rewritten
into an AI's: the student's name is still on the page above prose they did not write.
So ``voice`` is recorded per notebook and a CHANGED cell in a ``contributed``
notebook is exactly as loud as one in a ``dowling`` notebook.

    dowling      -- Prof. Dowling's own prose.
    contributed  -- a past student's (or an outside collaborator's) prose.
    ai-drafted   -- the notebook was ABSENT or a bare STUB at the anchor and is
                    substantial now. No human voice was overwritten, but the prose
                    is agent-written and must never be mistaken for his. The
                    motivating case is commit fcfcd3e, "Chapter 8: populate the two
                    stub notebooks from their handouts": 8-dev/Global-Opt.ipynb went
                    from 1 markdown cell to 19 and 8-dev/MINLP-Algorithms.ipynb from
                    1 to 26, drafted FROM THE LATEX HANDOUTS -- the exact
                    notebook<->handout bleed this baseline exists to detect.
    unknown      -- the evidence does not settle it. Used honestly; a confident
                    wrong attribution is worse than an admitted gap, because it
                    invites someone to "restore" a voice that was never there.

⚠ NORMALISATION IS DELIBERATELY ALMOST NOTHING
----------------------------------------------
Before hashing, each cell has (1) trailing whitespace stripped from every line and
(2) trailing newlines removed. That is all.

It deliberately does NOT: collapse internal whitespace, normalise blank lines
inside the cell, lowercase, normalise Unicode, strip markdown syntax, unify dashes
or quotes, or touch LaTeX. Every one of those would hide a real prose edit -- and
hiding real prose edits is the only failure mode that matters here. The single
false-positive class worth suppressing is whitespace churn from editors and
formatters, which is what the two rules above cover.

The cost is accepted: a genuine typo fix reads as CHANGED. That is correct. A human
should see every prose change to this corpus and say "yes, I meant that."

⚠ ONE BLEED CHANNEL THIS TOOL CANNOT SEE
----------------------------------------
``optimization-private/lecture-notes/check_code_sync.py`` asserts that notebook CODE
cells still match the ``\pyomocode{}`` listings in the handouts. The intended
direction is notebook -> handout: the notebook is the golden copy.

An editor who changes a handout listing and then "fixes" the resulting sync failure
by editing the NOTEBOOK has reversed that arrow and pushed handout content backwards
into the pre-LLM corpus. **A code-sync failure is resolved by re-extracting from the
notebook, never by editing the notebook to match the handout.**

This checker covers MARKDOWN CELLS ONLY. It would not catch that, and claims no
coverage of it. Code cells are excluded on purpose -- code is expected to change,
and is being changed right now by the units work -- so a checker that flagged code
would be switched off within a day, and then nothing would be checked.

USAGE
-----
    python3 check_prose_baseline.py                    # vs `current`; exit 1 on drift
    python3 check_prose_baseline.py --audit            # vs `anchor`: the standing audit
    python3 check_prose_baseline.py --update --reason "..."   # move `current`, logged
    python3 check_prose_baseline.py --selftest         # prove it can FAIL

Exit status is 0 when clean and 1 on drift, so it can gate a publish. A tool that
says OK is not evidence until you have watched it say FAIL -- so ``--selftest``
exits 0 only after it has watched this checker exit non-zero on a dirty fixture.

``--update`` REQUIRES ``--reason``, and appends the reason and the date to
``current.history``. Re-baselining is legitimate -- prose is meant to be refined --
but it must leave a trail. A bypass that is frictionless and unlogged quietly
erases the very evidence the baseline exists to hold. It also cannot erase the
anchor, which is the point of keeping the anchor in git rather than on disk.
"""

import argparse
import contextlib
import datetime
import difflib
import hashlib
import io
import json
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
BASELINE = Path(__file__).resolve().parent / "prose_baseline.json"

SCHEMA = 2
EXCERPT_CHARS = 80

# The last commit before Fall 2026 prep began touching notebook content. Immutable.
ANCHOR = "feb00d2"
ANCHOR_DATE = "2026-08-17"
ANCHOR_SUBJECT = "Redirect legacy JupyterBook 1 URLs to their MyST equivalents"

# A notebook that had at most this many markdown cells at the anchor was a stub.
STUB_MAX_CELLS = 2
# ...and is called substantial now at this many. Between the two is "grew a bit",
# which is not evidence of anything.
SUBSTANTIAL_MIN_CELLS = 5

# ---------------------------------------------------------------------------
# Scope
#
# IN:  every ``*-dev/`` notebook (the authored sources) and every notebook in
#      ``notebooks/contrib/`` (the contributed corpus, whose voices are the ones
#      least able to defend themselves), plus any published notebook that has no
#      ``-dev`` source at all -- that is authored content with no source, and is
#      an audit finding in its own right.
#
# OUT: ``notebooks/<N>/`` published copies, because they are GENERATED OUTPUT.
#      ``process_notebooks.py`` reads ``notebooks/<N>-dev/`` and writes
#      ``notebooks/<N>/``, rewriting markdown as it goes (activity boxes become
#      MyST admonitions, relative media paths become raw.githubusercontent URLs).
#      They are derived, not authored: prose can only reach them THROUGH a
#      ``-dev`` source, which is baselined. Baselining both would double every
#      alarm and train the reader to skim.
#
#      ``notebooks/contrib/`` is the deliberate exception. It is generated the same
#      way, but is included anyway: it is where the student voices live, and it is
#      the one published directory holding a file with no ``-dev`` source.
#
# OUT: ``notebooks/assignments/``, also generated -- its sources live in
#      ``optimization-private/notebooks/assignments/`` and belong to a baseline
#      taken in that repo, not this one.
# ---------------------------------------------------------------------------
SCOPE_NOTES = {
    "included": [
        "notebooks/*-dev/**/*.ipynb -- the authored notebook sources",
        "notebooks/contrib/**/*.ipynb -- the contributed corpus as published",
        "any notebooks/<N>/**/*.ipynb with no corresponding -dev source",
    ],
    "excluded": {
        "notebooks/<N>/*.ipynb": (
            "Generated output. process_notebooks.py builds these from "
            "notebooks/<N>-dev/, rewriting markdown (activity boxes -> MyST "
            "admonitions, ../../media/ -> raw.githubusercontent URLs). Derived, "
            "not authored: prose can only reach them through a -dev source, which "
            "IS baselined. Exception -- any published notebook with no -dev source "
            "is included, because then it is authored content."
        ),
        "notebooks/assignments/*.ipynb": (
            "Generated output. Sources live in "
            "optimization-private/notebooks/assignments/ and belong to a baseline "
            "taken in the private repo."
        ),
        "code cells": (
            "Out of scope on purpose. Code is expected to change and is being "
            "changed now by the units work; flagging it would make this tool noise. "
            "See the checker docstring on the check_code_sync.py bleed channel that "
            "this exclusion therefore leaves uncovered."
        ),
    },
}

# An attribution line, e.g. "**Prepared by:** ..." or "This notebook was prepared
# by ...". Anchored at the start of the line (after markdown emphasis) on purpose.
# An unanchored search matches sentences that merely name a SOURCE -- 3-dev/
# PyomoDAE_TCLab.ipynb says its page was "developed by Prof. Jeff Kantor", which
# describes where the material came from, not who wrote this notebook.
ATTRIBUTION_RE = re.compile(
    r"^[\s*#>_]*(?:This\s+(?:notebook|page)\s+(?:was|is)\s+)?"
    r"(?:prepared|created|written|developed|authored)\s+by\b\s*:?\**\s*(.+)$",
    re.IGNORECASE,
)
# Any mention of Dowling, however he signs it that year: "Prof. Alexander Dowling",
# "Prof. Alex Dowling", "adowling@nd.edu", "github.com/adowling2".
DOWLING_RE = re.compile(r"dowling", re.IGNORECASE)

# Identity tokens inside an attribution line. Names alone are unreliable (an
# institution reads like a person); an email or a bare GitHub profile is not.
EMAIL_RE = re.compile(r"[\w.+-]+@[\w.-]+\.\w+")
GITHUB_USER_RE = re.compile(r"github\.com/([A-Za-z0-9-]+)/?(?=[)\s\]\"']|$)")
TITLED_NAME_RE = re.compile(r"\b(?:Prof\.?|Professor|Dr\.?)\s+"
                            r"([A-Z][A-Za-z.]*(?:\s+[A-Z][A-Za-z.'-]+){1,2})")
# "William Bartel (wbartel@nd.edu" -- a name introducing its own parenthetical.
NAME_BEFORE_PAREN_RE = re.compile(r"\b([A-Z][a-z]+(?:\s+[A-Z][a-z'’-]+)+)\s*\(")
LINK_TEXT_RE = re.compile(r"\[([^\]]{2,60})\]\(")

# Only the first few markdown cells are searched for attribution; it is always at
# the top, and scanning the whole notebook drags in body prose that happens to
# start with "Created by".
ATTRIBUTION_SEARCH_CELLS = 5


# ---------------------------------------------------------------------------
# Cells
# ---------------------------------------------------------------------------
def normalise(text: str) -> str:
    """Strip trailing whitespace per line; drop trailing newlines. Nothing else.

    See the module docstring for what this deliberately does NOT do, and why.
    """
    return "\n".join(line.rstrip() for line in text.splitlines()).rstrip("\n")


def sha(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def excerpt(text: str) -> str:
    """First ~80 characters, on one line, so a diff is legible without nbformat."""
    flat = " ".join(text.split())
    return flat[:EXCERPT_CHARS] + ("..." if len(flat) > EXCERPT_CHARS else "")


def cell_source(cell) -> str:
    src = cell.get("source", [])
    if isinstance(src, list):
        src = "".join(src)
    return src


def markdown_cells(nb_text: str):
    """[{i, id, sha256, excerpt}] for the markdown cells of a notebook, in order.

    ``i`` is the ordinal among markdown cells and ``id`` the nbformat 4.5 cell id
    when the notebook has one (many of these notebooks are 4.4 and have none).
    NEITHER is used to align the diff -- see ``compare`` -- because an inserted
    cell shifts every later ordinal and would cascade into dozens of false
    CHANGED reports. They are recorded so a human can find the cell.
    """
    nb = json.loads(nb_text)
    out = []
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "markdown":
            continue
        # Skip the generated AI-review banner. process_notebooks.py injects one
        # markdown cell at the top of a PUBLISHED notebook that still has
        # unreviewed agent prose (see build_ai_review_status.py). Published
        # contrib/ notebooks are IN SCOPE here, so without this skip every
        # banner would report as an ADDED cell and the audit would be measuring
        # its own plumbing. Matched on metadata, not on the text: the wording is
        # meant to be edited, and a text match would rot the moment it was.
        if cell.get("metadata", {}).get("ai_review_banner"):
            continue
        text = normalise(cell_source(cell))
        out.append({"i": len(out), "id": cell.get("id"),
                    "sha256": sha(text), "excerpt": excerpt(text)})
    return out


# ---------------------------------------------------------------------------
# Scope resolution -- one pure function, applied to a git tree and to disk alike
# ---------------------------------------------------------------------------
def select_scope(all_paths):
    """Filter a set of notebook paths down to the in-scope ones. See SCOPE_NOTES.

    Pure, so the SAME rule applies to the anchor's git tree and to the working
    tree. If the two used different rules the anchor-vs-current diff would be
    measuring the rule change, not the prose.
    """
    have = set(all_paths)
    out = set()
    for rel in have:
        parts = Path(rel).parts
        if len(parts) < 3 or parts[0] != "notebooks":
            continue
        top = parts[1]
        if top.endswith("-dev"):
            out.add(rel)
        elif top == "contrib":
            out.add(rel)
        elif top == "assignments":
            continue
        else:
            # A published chapter notebook. In scope only if nothing generated it.
            source = "/".join(("notebooks", f"{top}-dev", *parts[2:]))
            if source not in have:
                out.add(rel)
    return out


def git(root: Path, *args, check=False):
    """Run git, returning stdout or None. Git is optional; absence degrades to unknown."""
    try:
        r = subprocess.run(["git", "-C", str(root), *args],
                           capture_output=True, text=True, timeout=120)
    except (OSError, subprocess.SubprocessError):
        return None
    if r.returncode != 0:
        if check:
            raise RuntimeError(f"git {' '.join(args)} failed: {r.stderr.strip()}")
        return None
    return r.stdout


def anchor_notebooks(root: Path):
    """All ``.ipynb`` paths present in the anchor commit, or None if git is absent."""
    out = git(root, "ls-tree", "-r", "--name-only", ANCHOR, "--", "notebooks/")
    if out is None:
        return None
    return {p for p in out.splitlines()
            if p.endswith(".ipynb") and ".ipynb_checkpoints" not in p}


def working_notebooks(root: Path):
    return {p.relative_to(root).as_posix()
            for p in root.glob("notebooks/**/*.ipynb")
            if ".ipynb_checkpoints" not in p.parts}


def uncommitted_in_scope(root: Path):
    """In-scope notebooks that differ from HEAD right now: work in flight."""
    out = git(root, "status", "--porcelain", "--", "notebooks/")
    if out is None:
        return None
    paths = set()
    for line in out.splitlines():
        p = line[3:].strip().strip('"')
        if "->" in p:                       # a rename: take the destination
            p = p.split("->")[-1].strip()
        if p.endswith(".ipynb"):
            paths.add(p)
    return sorted(select_scope(paths | working_notebooks(root)) & paths)


def historical_paths(root: Path, rel: str):
    """Every path this notebook has ever had, newest first, following renames."""
    log = git(root, "log", "--follow", "--name-only", "--format=", "--", rel)
    if not log:
        return []
    seen = []
    for line in log.splitlines():
        line = line.strip()
        if line and line not in seen:
            seen.append(line)
    return seen


def resolve_at_anchor(root: Path, rel: str, anchor_paths):
    """The path this notebook had at the anchor, or None if it did not exist then.

    Rename resolution is load-bearing, not a nicety. Two notebooks were PROMOTED
    out of contrib after the anchor -- contrib-dev/Sudoku_Solver.ipynb became
    1-dev/Sudoku_Solver.ipynb and contrib-dev/Deterministic_Global_Optimization.ipynb
    became 8-dev/... . Without this they would read as "created after the anchor"
    and be labelled ``ai-drafted``, erasing four students' names from a corpus this
    tool exists to protect.
    """
    if rel in anchor_paths:
        return rel
    for cand in historical_paths(root, rel):
        if cand in anchor_paths:
            return cand
    return None


# ---------------------------------------------------------------------------
# Voice registry
# ---------------------------------------------------------------------------
def looks_like_person(text: str) -> bool:
    """True for "Hailey Lynch", false for "Institute for the Design of ...".

    Link text is a decent name source but a terrible one unfiltered: it is just as
    often an organisation. Requiring two to four words that all begin with a
    capital separates "Prof. Alex Dowling" from "adapted from our process control
    class" and from the IDAES institute's full name.
    """
    words = text.split()
    return 2 <= len(words) <= 4 and all(w[:1].isupper() for w in words)


def identity_tokens(line: str):
    """Identity evidence in an attribution line: emails, GitHub profiles, names.

    Bare GitHub *profiles* only -- ``github.com/hglynch`` is a person,
    ``github.com/IDAES/examples`` is an organisation's repository and names nobody.
    """
    toks = []
    toks += EMAIL_RE.findall(line)
    toks += ["github.com/" + u for u in GITHUB_USER_RE.findall(line)]
    toks += TITLED_NAME_RE.findall(line)
    toks += NAME_BEFORE_PAREN_RE.findall(line)
    toks += [t for t in LINK_TEXT_RE.findall(line) if looks_like_person(t)]
    out = []
    for t in toks:
        t = " ".join(t.split()).strip(" .,;:")
        if t and t not in out:
            out.append(t)
    return out


def find_attribution(nb_text: str):
    """The notebook's own "Prepared by: ..." line, if it has one.

    Strongest available evidence, and it takes precedence over the path: several
    notebooks were promoted OUT of contrib into a numbered chapter and kept the
    students' names -- notebooks/1-dev/Sudoku_Solver.ipynb is Bartel and Brooks
    even though it now sits in a chapter directory, and git records its creation
    there under Prof. Dowling, who only moved it.
    """
    try:
        nb = json.loads(nb_text)
    except Exception:
        return None
    seen = 0
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "markdown":
            continue
        seen += 1
        if seen > ATTRIBUTION_SEARCH_CELLS:
            break
        for line in cell_source(cell).splitlines():
            if len(line) > 600:
                continue
            if ATTRIBUTION_RE.match(line):
                return " ".join(line.split())
    return None


def derive_voice(root: Path, rel: str, nb_text: str, anchor_cells, current_cells,
                 origin: str):
    """(voice, evidence). Evidence is recorded so the call can be re-argued later."""
    # ai-drafted wins, and only in the narrow case it is actually evidence for:
    # a stub or an absent file at the anchor that is substantial now. No human
    # voice was displaced, so no attribution can be honoured -- there was nothing
    # to attribute.
    n_anchor = len(anchor_cells) if anchor_cells is not None else 0
    n_now = len(current_cells)
    # ⚠ "created-after-anchor" ONLY. An earlier version tested `origin != "at-anchor"`,
    # which swept in the two RENAMED notebooks -- Sudoku_Solver and
    # Deterministic_Global_Optimization, promoted out of contrib -- and labelled four
    # students' work ai-drafted. Exactly the erasure this tool exists to prevent, in
    # the tool itself.
    if origin == "created-after-anchor" and n_now >= SUBSTANTIAL_MIN_CELLS:
        return "ai-drafted", (
            f"absent at anchor {ANCHOR} ({ANCHOR_DATE}) and has {n_now} markdown "
            f"cells now: the prose was written after agent editing began")
    if anchor_cells is not None and n_anchor <= STUB_MAX_CELLS \
            and n_now >= SUBSTANTIAL_MIN_CELLS:
        return "ai-drafted", (
            f"a {n_anchor}-cell stub at anchor {ANCHOR} ({ANCHOR_DATE}), "
            f"{n_now} markdown cells now: prose written after agent editing began")

    attrib = find_attribution(nb_text)
    if attrib:
        toks = identity_tokens(attrib)
        others = [t for t in toks if not DOWLING_RE.search(t)]
        dowling = [t for t in toks if DOWLING_RE.search(t)]
        if others:
            return "contributed", (f"in-notebook attribution names {others}; "
                                   f"line: {attrib}")
        if dowling:
            return "dowling", (f"in-notebook attribution names only Dowling "
                               f"{dowling}; line: {attrib}")
        return "unknown", (f"attribution line found but no identifiable author "
                           f"parsed from it; line: {attrib}")

    if "contrib" in Path(rel).parts[1]:
        return "contributed", ("no in-notebook attribution; lives under "
                               "notebooks/contrib*, which is contributed by definition")

    first = git(root, "log", "--follow", "--diff-filter=A",
                "--format=%an|%ad", "--date=short", "--", rel)
    if first is None:
        return "unknown", "no in-notebook attribution and git was unavailable"
    lines = [l for l in first.strip().splitlines() if l]
    if not lines:
        return "unknown", "no in-notebook attribution and no git creation commit found"
    author, date = lines[-1].split("|", 1)
    kind = "dowling" if DOWLING_RE.search(author) else "contributed"
    return kind, (f"no in-notebook attribution; git --follow creation commit by "
                  f"{author} on {date}")


# ---------------------------------------------------------------------------
# Diffing
# ---------------------------------------------------------------------------
def compare(base_cells, now_cells):
    """Align two markdown-cell sequences by hash and classify the differences.

    Aligned with difflib on the HASH SEQUENCE, not by index. That is the whole
    point: inserting one cell at the top of a notebook must report one ADDED cell,
    not forty CHANGED ones. A checker whose output balloons on a legitimate
    insertion gets ignored, and then nothing is checked.

    ``replace`` runs are paired up positionally into CHANGED, which is the alarm:
    substitution -- the cell stays, the words become someone else's -- is how a
    voice is lost. Leftovers on either side fall through to ADDED / REMOVED.
    """
    a = [c["sha256"] for c in base_cells]
    b = [c["sha256"] for c in now_cells]
    changed, added, removed = [], [], []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(a=a, b=b,
                                                       autojunk=False).get_opcodes():
        if tag == "equal":
            continue
        if tag == "insert":
            added += now_cells[j1:j2]
        elif tag == "delete":
            removed += base_cells[i1:i2]
        else:
            n = min(i2 - i1, j2 - j1)
            changed += [(base_cells[i1 + k], now_cells[j1 + k]) for k in range(n)]
            removed += base_cells[i1 + n:i2]
            added += now_cells[j1 + n:j2]
    return changed, added, removed


# ---------------------------------------------------------------------------
# Capture
# ---------------------------------------------------------------------------
def read_anchor(root: Path):
    """{path_at_anchor: [cells]} for the in-scope notebooks of the anchor commit."""
    paths = anchor_notebooks(root)
    if paths is None:
        raise RuntimeError(
            f"Cannot read the anchor commit {ANCHOR}. The anchor is a git object, "
            "not a file on disk -- see the module docstring. Run this inside the "
            "public repo's git checkout.")
    out = {}
    for rel in sorted(select_scope(paths)):
        blob = git(root, "show", f"{ANCHOR}:{rel}", check=True)
        out[rel] = markdown_cells(blob)
    return out


def capture(root: Path, reason: str, previous=None):
    anchor = read_anchor(root)
    anchor_paths = anchor_notebooks(root) or set()

    current = {}
    registry = {}
    for rel in sorted(select_scope(working_notebooks(root))):
        nb_text = (root / rel).read_text(encoding="utf-8")
        cells = markdown_cells(nb_text)
        current[rel] = cells

        at = resolve_at_anchor(root, rel, anchor_paths)
        if at is None:
            origin, anchor_cells = "created-after-anchor", None
        elif at == rel:
            origin, anchor_cells = "at-anchor", anchor.get(rel)
        else:
            origin, anchor_cells = f"at-anchor-as:{at}", anchor.get(at)
            if anchor_cells is None:
                # Present at the anchor but out of scope there (e.g. it was a
                # published chapter copy). Read it directly so the drift is real.
                blob = git(root, "show", f"{ANCHOR}:{at}")
                anchor_cells = markdown_cells(blob) if blob else None

        voice, evidence = derive_voice(root, rel, nb_text, anchor_cells, cells, origin)
        entry = {"voice": voice, "voice_evidence": evidence, "origin": origin,
                 "n_markdown_cells": len(cells)}
        if anchor_cells is None:
            entry["drift_from_anchor"] = {
                "changed": 0, "added": len(cells), "removed": 0,
                "note": f"did not exist at {ANCHOR}; all prose is post-anchor"}
        else:
            ch, ad, rm = compare(anchor_cells, cells)
            entry["drift_from_anchor"] = {
                "changed": len(ch), "added": len(ad), "removed": len(rm),
                "changed_cells": [{"anchor_i": o["i"], "current_i": n["i"],
                                   "anchor_excerpt": o["excerpt"],
                                   "current_excerpt": n["excerpt"]}
                                  for o, n in ch],
                "note": (f"{len(anchor_cells)} markdown cells at {ANCHOR}, "
                         f"{len(cells)} now")}
        registry[rel] = entry

    # In-scope notebooks that existed at the anchor and are gone from the tree.
    for rel in sorted(set(anchor) - set(current)):
        if any(e["origin"] == f"at-anchor-as:{rel}" for e in registry.values()):
            continue           # renamed, already accounted for
        registry[rel] = {
            "voice": "unknown", "voice_evidence": "removed from the working tree",
            "origin": "at-anchor", "n_markdown_cells": 0,
            "drift_from_anchor": {"changed": 0, "added": 0,
                                  "removed": len(anchor[rel]),
                                  "note": f"present at {ANCHOR}, absent now"}}

    today = datetime.date.today().isoformat()
    history = (previous or {}).get("history", []) if previous else []
    return {
        "schema": SCHEMA,
        "generator": "scripts/check_prose_baseline.py",
        "why": (
            "The notebooks are a pre-LLM corpus in human voices -- Prof. Dowling's, "
            "and past students' in notebooks/contrib/. The LaTeX course pack is "
            "largely AI-drafted prose under revision, and code is single-sourced "
            "from notebooks into handouts, so an editor is regularly in both files "
            "at once. This baseline turns 'handout prose must not migrate into the "
            "notebooks' from a hope into a machine-checked invariant. It covers "
            "MARKDOWN CELLS ONLY; see the checker's docstring for the code-sync "
            "bleed channel it cannot see."
        ),
        "normalisation": (
            "Per cell: trailing whitespace stripped from each line, trailing "
            "newlines removed, then SHA-256 of the result. Deliberately does NOT "
            "collapse internal whitespace, normalise blank lines, lowercase, "
            "normalise Unicode, unify dashes or quotes, or strip markdown/LaTeX "
            "syntax -- each of those would hide a real prose edit, which is the "
            "only failure mode that matters here."
        ),
        "voice_registry_note": (
            "Per notebook: dowling / contributed / ai-drafted / unknown, with the "
            "evidence that settled it. The check runs in BOTH directions: a "
            "contributed notebook rewritten into Prof. Dowling's voice is as much a "
            "loss as one rewritten into an AI's, because the student's name is "
            "still on the page. The instruction is to preserve the voices, plural. "
            "'ai-drafted' marks a notebook that was absent or a bare stub at the "
            "anchor and is substantial now: no human voice was displaced, but the "
            "prose is agent-written and must not be mistaken for his."
        ),
        "scope": SCOPE_NOTES,
        "anchor": {
            "ref": ANCHOR,
            "date": ANCHOR_DATE,
            "subject": ANCHOR_SUBJECT,
            "immutable": True,
            "why": (
                "Read with `git show feb00d2:<path>`, never from disk. Agents were "
                "editing -dev notebooks while this baseline was captured, so a "
                "working-tree snapshot would have hashed some notebooks before an "
                "edit and others after it with nothing recording which -- worse "
                "than no baseline, because it would look authoritative. A commit is "
                "reproducible forever, immune to concurrent workers, and feb00d2 is "
                "the last commit before agent editing of -dev notebooks began on "
                "2026-08-18. --update never touches this section."
            ),
            "notebooks": {k: {"n_markdown_cells": len(v), "cells": v}
                          for k, v in anchor.items()},
        },
        "current": {
            "captured": today,
            "reason": reason,
            "history": history + [{"date": today, "reason": reason}],
            "note": ("A moving snapshot of the working tree, expected to change as "
                     "prose is legitimately refined. This is what a plain run "
                     "compares against."),
            "head": (git(root, "rev-parse", "--short", "HEAD") or "").strip() or None,
            "uncommitted_at_capture": uncommitted_in_scope(root),
            "uncommitted_note": (
                "In-scope notebooks that differed from HEAD when this snapshot was "
                "taken, i.e. work in flight. Recorded rather than smoothed over: "
                "several agents edit -dev notebooks concurrently, and a snapshot that "
                "silently mixes committed and half-finished states while looking "
                "authoritative is the failure this design exists to avoid. The "
                "`anchor` layer is a commit and is immune to this."
            ),
            "notebooks": {k: {"n_markdown_cells": len(v), "cells": v}
                          for k, v in current.items()},
        },
        "registry": registry,
    }


# ---------------------------------------------------------------------------
# Reporting
# ---------------------------------------------------------------------------
def _report(root: Path, reference, registry, label):
    """Compare the working tree against ``reference`` ({path: {cells}}). Returns rc."""
    current = select_scope(working_notebooks(root))
    known = set(reference)

    def voice(rel):
        return registry.get(rel, {}).get("voice", "unknown")

    changed_n = added_n = removed_n = 0
    rows = []
    for rel in sorted(known & current):
        try:
            now = markdown_cells((root / rel).read_text(encoding="utf-8"))
        except Exception as exc:
            rows.append((rel, voice(rel), str(exc), [], [], []))
            changed_n += 1
            continue
        ch, ad, rm = compare(reference[rel]["cells"], now)
        if ch or ad or rm:
            rows.append((rel, voice(rel), None, ch, ad, rm))
            changed_n += len(ch)
            added_n += len(ad)
            removed_n += len(rm)

    gone = sorted(known - current)
    fresh = sorted(current - known)

    total_cells = sum(v["n_markdown_cells"] for v in reference.values())
    print(f"Prose baseline check vs {label}  "
          f"({len(known)} notebooks, {total_cells} markdown cells)")

    if changed_n:
        print("\n" + "=" * 74)
        print("CHANGED PROSE -- an existing markdown cell was REPLACED.")
        print("This is the alarm. Substitution is how an AI voice displaces a human")
        print("one: the cell stays in place, the words are someone else's. Confirm")
        print("every one of these was a deliberate human edit.")
        print("=" * 74)
        for rel, v, err, ch, _, _ in rows:
            if err:
                print(f"\n  {rel}  [voice: {v}]\n      UNREADABLE: {err}")
            elif ch:
                print(f"\n  {rel}  [voice: {v}]")
                for old, new in ch:
                    print(f"      md[{old['i']}] CHANGED")
                    print(f"        was: {old['excerpt']}")
                    print(f"        now: {new['excerpt']}")

    if added_n or removed_n:
        print("\n" + "-" * 74)
        print("ADDED / REMOVED cells -- usually legitimate. New sections get written")
        print("and stale ones get deleted. Listed for the record, not as an alarm.")
        print("-" * 74)
        for rel, v, err, _, ad, rm in rows:
            if err or not (ad or rm):
                continue
            print(f"\n  {rel}  [voice: {v}]")
            for c in rm:
                print(f"      md[{c['i']}] REMOVED  {c['excerpt']}")
            for c in ad:
                print(f"      md[{c['i']}] ADDED    {c['excerpt']}")

    if gone or fresh:
        print("\n" + "-" * 74)
        print("NOTEBOOK INVENTORY CHANGED")
        print("-" * 74)
        for rel in gone:
            print(f"      GONE      {rel}  [voice: {voice(rel)}]")
        for rel in fresh:
            print(f"      NEW       {rel}  (not in this reference)")

    total = changed_n + added_n + removed_n + len(gone) + len(fresh)
    print(f"\n{changed_n} CHANGED, {added_n} added, {removed_n} removed, "
          f"{len(gone)} gone, {len(fresh)} new")
    return changed_n, added_n, removed_n, len(gone), len(fresh), total


def check(root: Path, baseline: dict) -> int:
    ref = baseline["current"]["notebooks"]
    reg = baseline["registry"]
    *_, total = _report(root, ref, reg,
                        f"`current` (captured {baseline['current']['captured']})")

    # The anchor drift is a standing fact, not this run's news. One line, always,
    # so nobody forgets the corpus is already 47 commits past its human state.
    drift = [(k, v["drift_from_anchor"]) for k, v in reg.items()]
    n_ch = sum(d["changed"] for _, d in drift)
    n_nb = sum(1 for _, d in drift if d["changed"])
    ai = sum(1 for v in reg.values() if v["voice"] == "ai-drafted")
    print(f"\nStanding audit vs anchor {ANCHOR} ({ANCHOR_DATE}): "
          f"{n_ch} substituted cells across {n_nb} notebooks; "
          f"{ai} notebooks are ai-drafted.  --audit for detail.")

    if total == 0:
        print("Prose baseline intact.")
        return 0
    print("\nIf every change above is a deliberate human edit, re-baseline with:")
    print('    python3 check_prose_baseline.py --update --reason "why"')
    print("If any CHANGED cell is not, revert it. Handout prose does not belong here.")
    return 1


def audit(root: Path, baseline: dict) -> int:
    """The standing audit: working tree vs the immutable anchor commit."""
    print(f"ANCHOR AUDIT -- working tree vs {ANCHOR} ({ANCHOR_DATE})")
    print(f'  "{ANCHOR_SUBJECT}"')
    print("The last commit before agent editing of -dev notebooks began (2026-08-18).")
    print("Drift here is EXPECTED and largely legitimate. It is printed so that what")
    print("agent work did to Prof. Dowling's prose stays visible and reviewable.\n")

    reg = baseline["registry"]
    anchor = baseline["anchor"]["notebooks"]
    # Reference the anchor under CURRENT paths, following the recorded renames.
    ref = {}
    for rel, entry in reg.items():
        origin = entry["origin"]
        if origin.startswith("at-anchor-as:"):
            src = origin.split(":", 1)[1]
        elif origin == "at-anchor":
            src = rel
        else:
            continue
        if src in anchor:
            ref[rel] = anchor[src]
    _report(root, ref, reg, f"anchor {ANCHOR}")

    ai = sorted(k for k, v in reg.items() if v["voice"] == "ai-drafted")
    if ai:
        print("\n" + "=" * 74)
        print("ai-drafted -- absent or a bare stub at the anchor, substantial now.")
        print("No human voice was displaced, but this prose is agent-written and")
        print("must never be presented as Prof. Dowling's or a student's.")
        print("=" * 74)
        for rel in ai:
            print(f"  {rel}\n      {reg[rel]['voice_evidence']}")

    print(f"\nVoices: {dict(Counter(v['voice'] for v in reg.values()))}")
    return 0


# ---------------------------------------------------------------------------
# Self-test
# ---------------------------------------------------------------------------
def selftest() -> int:
    """Exit 0 only after watching the checker exit non-zero on a dirty fixture."""
    import tempfile

    print("Self-test: the checker must FAIL on dirty fixtures, not merely pass on"
          " a clean one.\n")

    def nb(cells):
        return json.dumps({
            "cells": [{"cell_type": t, "source": s, "metadata": {}} for t, s in cells],
            "metadata": {}, "nbformat": 4, "nbformat_minor": 5})

    human = [
        ("markdown", "# Milk Pooling and Blending\n\nAdapted from Kantor.\n"),
        ("code", "m = pyo.ConcreteModel()\n"),
        ("markdown", "The pool cannot be richer than its richest input.\n"),
        ("markdown", "## Options 1 and 2 --- blending only\n"),
    ]
    stub = [("markdown", "# Deterministic Global Optimization\n")]
    populated = [("markdown", f"## Section {i}\nText drafted from the handout.\n")
                 for i in range(6)]

    cases = [
        ("unchanged corpus", human, (0, 0, 0), True),
        ("one-word prose edit",
         [human[0], human[1],
          ("markdown", "The pool cannot be richer than its finest input.\n"), human[3]],
         (1, 0, 0), False),
        ("whitespace-only change",
         [("markdown", "# Milk Pooling and Blending   \n\nAdapted from Kantor.\n\n\n"),
          human[1],
          ("markdown", "The pool cannot be richer than its richest input.\t\n"),
          human[3]],
         (0, 0, 0), True),
        ("code-cell change",
         [human[0],
          ("code", "m = pyo.ConcreteModel()\nm.x = pyo.Var(units=pyounits.kg)\n"),
          human[2], human[3]],
         (0, 0, 0), True),
        ("inserted cell -> ADDED, no cascade",
         [human[0], ("markdown", "A brand new section nobody had written yet.\n"),
          human[1], human[2], human[3]],
         (0, 1, 0), False),
        ("deleted cell -> REMOVED", [human[0], human[1], human[3]], (0, 0, 1), False),
    ]

    ok = True
    saw_failure = False
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "notebooks" / "1-dev").mkdir(parents=True)
        (root / "notebooks" / "8-dev").mkdir(parents=True)
        (root / "notebooks" / "contrib-dev").mkdir(parents=True)
        milk = root / "notebooks/1-dev/Milk-Pooling.ipynb"
        glob = root / "notebooks/8-dev/Global-Opt.ipynb"
        promoted_from = root / "notebooks/contrib-dev/Sudoku_Solver.ipynb"
        promoted_to = root / "notebooks/1-dev/Sudoku_Solver.ipynb"
        milk.write_text(nb(human))
        glob.write_text(nb(stub))
        promoted_from.write_text(nb(
            [("markdown", "# Sudoku\n\n**Prepared by:** William Bartel "
                          "(wbartel@nd.edu, 2024)\n")] + populated))

        # A real git history with a real anchor commit. The anchor is a git object,
        # so a fixture without one would exercise a different code path than
        # production -- which is how self-tests come to certify nothing.
        for args in (["init", "-q", "-b", "main"],
                     ["config", "user.email", "selftest@example.invalid"],
                     ["config", "user.name", "Self Test"],
                     ["add", "-A"],
                     ["commit", "-qm", "anchor"]):
            if git(root, *args) is None and args[0] not in ("config",):
                print(f"  SKIP: git unavailable ({args[0]}); cannot self-test the "
                      f"anchor path.")
                return 1
        real_anchor = git(root, "rev-parse", "HEAD").strip()[:7]

        global ANCHOR
        saved = ANCHOR
        try:
            ANCHOR = real_anchor
            # A stub at the anchor, substantial now -> ai-drafted. This is the
            # fcfcd3e shape: handout prose poured into an empty notebook.
            glob.write_text(nb(populated))
            # ...and a notebook PROMOTED out of contrib after the anchor. It is
            # absent at its current path but present at its old one, and must keep
            # its student's voice.
            git(root, "mv", "notebooks/contrib-dev/Sudoku_Solver.ipynb",
                "notebooks/1-dev/Sudoku_Solver.ipynb")
            git(root, "commit", "-qm", "promote out of contrib")
            base = capture(root, "self-test fixture")

            reg = base["registry"]
            entry = reg["notebooks/1-dev/Sudoku_Solver.ipynb"]
            good = (entry["voice"] == "contributed"
                    and entry["origin"].startswith("at-anchor-as:"))
            ok = ok and good
            print(f"  {'OK  ' if good else 'FAIL'} notebook promoted out of contrib "
                  f"after the anchor -> voice {entry['voice']!r}, origin "
                  f"{entry['origin']!r}; expected 'contributed' / 'at-anchor-as:...'")

            got = reg["notebooks/8-dev/Global-Opt.ipynb"]["voice"]
            good = got == "ai-drafted"
            ok = ok and good
            print(f"  {'OK  ' if good else 'FAIL'} stub-at-anchor, substantial now "
                  f"-> voice {got!r}, expected 'ai-drafted'")

            got = reg["notebooks/1-dev/Milk-Pooling.ipynb"]["voice"]
            good = got != "ai-drafted"
            ok = ok and good
            print(f"  {'OK  ' if good else 'FAIL'} unchanged human notebook "
                  f"-> voice {got!r}, must NOT be 'ai-drafted'")

            anchor_cells = base["anchor"]["notebooks"][
                "notebooks/8-dev/Global-Opt.ipynb"]["n_markdown_cells"]
            good = anchor_cells == 1
            ok = ok and good
            print(f"  {'OK  ' if good else 'FAIL'} anchor read from git, not disk: "
                  f"Global-Opt has {anchor_cells} anchor cell(s), expected 1 "
                  f"(disk has {len(populated)})")

            for name, cells, expect, should_pass in cases:
                milk.write_text(nb(cells))
                now = markdown_cells(milk.read_text())
                ch, ad, rm = compare(
                    base["current"]["notebooks"][
                        "notebooks/1-dev/Milk-Pooling.ipynb"]["cells"], now)
                got = (len(ch), len(ad), len(rm))
                # The one-word edit is printed in full: it is the report a human
                # will actually read when the alarm fires, so it should be seen
                # every time the self-test runs. The rest run silently.
                show = name.startswith("one-word")
                if show:
                    print("\n  --- full report for the case that matters "
                          "----------------------")
                    rc = check(root, base)
                    print("  ----------------------------------------"
                          "----------------------\n")
                else:
                    with contextlib.redirect_stdout(io.StringIO()):
                        rc = check(root, base)
                if rc != 0:
                    saw_failure = True
                good = got == expect and ((rc == 0) == should_pass)
                ok = ok and good
                print(f"  {'OK  ' if good else 'FAIL'} {name}: "
                      f"changed/added/removed = {got}, expected {expect}; "
                      f"exit {rc}, expected {0 if should_pass else 1}")
        finally:
            ANCHOR = saved

        # --update must refuse to run without a reason. A frictionless, unlogged
        # bypass would make the whole baseline decorative.
        with contextlib.redirect_stderr(io.StringIO()):
            rc = main(["--update"], root=root, baseline_path=root / "b.json")
        good = rc != 0
        ok = ok and good
        print(f"  {'OK  ' if good else 'FAIL'} --update without --reason is refused "
              f"(exit {rc})")

    print()
    if not saw_failure:
        print("Self-test FAILED: never observed a non-zero exit. A checker that has "
              "only been seen to pass is not evidence.")
        return 1
    if not ok:
        print("Self-test FAILED.")
        return 1
    print("Self-test PASSED: watched it FAIL on a prose edit, an insertion and a")
    print("deletion; ignore whitespace churn and a code-cell change; read the anchor")
    print("from git rather than disk; label a populated stub 'ai-drafted' without")
    print("mislabelling a human notebook; and refuse an unexplained --update.")
    return 0


# ---------------------------------------------------------------------------
def main(argv=None, root=ROOT, baseline_path=BASELINE) -> int:
    ap = argparse.ArgumentParser(
        description="Compare notebook markdown cells against the prose baseline.")
    ap.add_argument("--update", action="store_true",
                    help="re-capture `current`; REQUIRES --reason. Never touches the "
                         "immutable `anchor` section.")
    ap.add_argument("--reason", default=None,
                    help="why the baseline is being moved (recorded with the date)")
    ap.add_argument("--audit", action="store_true",
                    help=f"report the working tree against the anchor commit {ANCHOR}")
    ap.add_argument("--selftest", action="store_true",
                    help="prove the checker can fail")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    if args.update:
        if not args.reason or not args.reason.strip():
            print("--update requires --reason \"...\".\n\n"
                  "Re-baselining `current` is legitimate -- prose is meant to be\n"
                  "refined -- but it overwrites the record that a change happened. A\n"
                  "bypass that is frictionless and unlogged makes the baseline\n"
                  "decorative, so the reason and date are written into the JSON. Say\n"
                  "what you refined. (The `anchor` section cannot be moved at all.)",
                  file=sys.stderr)
            return 2
        previous = None
        if baseline_path.exists():
            try:
                previous = json.loads(baseline_path.read_text()).get("current")
            except Exception:
                previous = None
        data = capture(root, args.reason.strip(), previous)
        baseline_path.write_text(json.dumps(data, indent=1) + "\n")
        reg = data["registry"]
        print(f"Wrote {baseline_path}")
        print(f"  anchor  {ANCHOR} ({ANCHOR_DATE}): "
              f"{len(data['anchor']['notebooks'])} notebooks, "
              f"{sum(v['n_markdown_cells'] for v in data['anchor']['notebooks'].values())}"
              f" markdown cells")
        print(f"  current {data['current']['captured']}: "
              f"{len(data['current']['notebooks'])} notebooks, "
              f"{sum(v['n_markdown_cells'] for v in data['current']['notebooks'].values())}"
              f" markdown cells")
        print(f"  voices: {dict(Counter(v['voice'] for v in reg.values()))}")
        print(f"  origins: {dict(Counter(v['origin'].split(':')[0] for v in reg.values()))}")
        print(f"  drift from anchor: "
              f"{sum(v['drift_from_anchor']['changed'] for v in reg.values())} changed, "
              f"{sum(v['drift_from_anchor']['added'] for v in reg.values())} added, "
              f"{sum(v['drift_from_anchor']['removed'] for v in reg.values())} removed")
        print(f"  reason: {args.reason.strip()}")
        return 0

    if not baseline_path.exists():
        print(f"No baseline at {baseline_path}.\n"
              'Create one with: --update --reason "initial capture"', file=sys.stderr)
        return 2
    baseline = json.loads(baseline_path.read_text())
    if baseline.get("schema") != SCHEMA:
        print(f"Baseline schema {baseline.get('schema')} != {SCHEMA}; re-capture it.",
              file=sys.stderr)
        return 2
    if args.audit:
        return audit(root, baseline)
    return check(root, baseline)


if __name__ == "__main__":
    sys.exit(main())
