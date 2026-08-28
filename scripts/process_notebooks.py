import nbformat
from nbformat.v4.nbbase import new_code_cell, new_markdown_cell, new_notebook
import re
import os
import shutil
import sys

# The published-answer marker is DEFINED ONCE, in the checker, and imported
# here. Two copies of the grammar is how the stripper and the check that guards
# it drift apart, and the drift would be silent in exactly the direction that
# matters: the stripper stops recognising a block, the checker keeps saying the
# block is fine.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from check_solution_leaks import published_answer_findings  # noqa: E402

# ---------------------------------------------------------------------------
# AI-review banner
#
# Prof. Dowling, 2026-08-22: "We need a way to track AI-drafted text on the
# website. This way, I can see what is AI-draft when I review the corresponding
# pages before each lecture. This also flags to students if content was
# AI-drafted and I have not reviewed it yet."
#
# WHY THE BANNER IS INJECTED HERE, AND NOT WRITTEN INTO THE SOURCE.
# notebooks/<N>/ is GENERATED; notebooks/<N>-dev/ is the authored corpus, and
# that corpus is pre-LLM human prose the project is explicitly trying not to
# contaminate (see scripts/check_prose_baseline.py). Writing a visible marker
# into the -dev notebooks would mean an agent adding cells to the very corpus
# the baseline exists to protect -- the fix would commit the disease. Injecting
# at publish time keeps the source untouched, and the banner disappears on the
# next publish the moment a row is flipped to `reviewed`.
#
# The state lives in scripts/ai_review_status.tsv, one row per notebook, edited
# by hand. Regenerate counts with scripts/build_ai_review_status.py, which
# preserves rows already marked `reviewed`.
#
# The injected cell carries metadata `ai_review_banner: true` so that
# check_prose_baseline.py can skip it structurally -- published contrib/
# notebooks are in that checker's scope, and without the skip every banner
# would report as an ADDED cell and the audit would be measuring its own
# plumbing.
AI_STATUS_TSV = os.path.join(os.path.dirname(os.path.abspath(__file__)),
                             "ai_review_status.tsv")
AI_BANNER_STATUSES = ("unreviewed", "reviewed-stale")


def load_ai_status(path=AI_STATUS_TSV):
    """{notebook path: (status, changed, added)}. Missing file degrades to {}."""
    if not os.path.exists(path):
        print(f"  NOTE: {path} not found; AI-review banners disabled")
        return {}
    out = {}
    with open(path, encoding="utf-8") as fp:
        for line in fp:
            line = line.rstrip("\n")
            if not line.strip() or line.startswith("#"):
                continue
            f = line.split("\t")
            if f[0] == "path":
                continue
            f += [""] * (7 - len(f))
            out[f[0]] = (f[1], f[3], f[4])
    return out


AI_STATUS = load_ai_status()


def ai_banner_cell(changed, added):
    """The student- and instructor-facing notice. Wording is meant to be edited.

    Two constraints on the text. It must be honest about SCOPE: the measurement
    is against the anchor commit, so it covers everything since agent editing
    began and NOT all AI-drafted text ever -- prose changed before 2026-08-17 is
    invisible to it. And it must not imply anything about the code or results,
    which are verified by a separate process.
    """
    counts = []
    if int(changed or 0):
        counts.append(f"{changed} rewritten")
    if int(added or 0):
        counts.append(f"{added} added")
    detail = " and ".join(counts) if counts else "some"
    body = (
        "```{warning}\n"
        "**AI-drafted prose, not yet reviewed by Prof. Dowling.**\n"
        "\n"
        f"Some of the writing on this page was drafted or edited by an AI assistant and has "
        f"not yet been reviewed: {detail} markdown cells, measured against the last version "
        "of this notebook predating AI editing (2026-08-17).\n"
        "\n"
        "This notice is about the *prose only*. It says nothing either way about the code, "
        "the numbers or the figures, which are checked separately. It is removed once the "
        "page has been reviewed.\n"
        "```"
    )
    cell = new_markdown_cell(body)
    # This cell is generated afresh on every publish. nbformat otherwise gives
    # it a random ID, making an unchanged publish dirty dozens of notebooks.
    # Cell IDs need only be unique within a notebook, so a stable generated ID
    # is both valid and reproducible.
    cell["id"] = "ai-review-banner"
    cell.metadata["ai_review_banner"] = True
    return cell


def insert_ai_banner(nb, source_rel, published_rel, verbose=1):
    """Insert the banner if this notebook's row says it is unreviewed.

    Keyed on the -dev SOURCE path, because that is the authoring unit and the
    unit Prof. Dowling reviews. Falls back to the published path for the handful
    of notebooks that have no -dev source (some of contrib/).
    """
    row = AI_STATUS.get(source_rel) or AI_STATUS.get(published_rel)
    if not row:
        return False
    status, changed, added = row
    if status not in AI_BANNER_STATUSES:
        return False

    # After the title, not before it: MyST takes the page title from the first
    # H1, and shoving a warning above it buries the heading and risks the title
    # extraction. Title first, then the caveat about it.
    at = 0
    for i, cell in enumerate(nb.cells):
        if cell.cell_type == "markdown" and re.search(r"^#\s", cell.source, re.M):
            at = i + 1
            break
    nb.cells.insert(at, ai_banner_cell(changed, added))
    if verbose >= 1:
        print(f"  AI-review banner inserted at cell {at} ({status}: "
              f"{changed} changed, {added} added)")
    return True

# ---------------------------------------------------------------------------
# Deliberately published answers
#
# Prof. Dowling, 2026-08-25, on the diet and portfolio problems: the answers go
# on the public site "because the homework is completion-based." The student is
# meant to attempt the problem cold and then check their own work.
#
# That is an exception to the standing rule this pipeline enforces, so it is
# made explicit rather than left to prose. A block between
#
#     ### BEGIN PUBLISHED ANSWER   ...   ### END PUBLISHED ANSWER      (code)
#     <!-- BEGIN PUBLISHED ANSWER --> ... <!-- END PUBLISHED ANSWER --> (markdown)
#
# passes through UNCHANGED -- markers and stored outputs included. The markers
# survive so that the published notebook carries its own evidence the answer was
# intended; written as plain prose, a deliberate answer and a leak look the same
# to the checker and to the next reader.
#
# WHY THIS FUNCTION EXISTS, given that no strip pattern matches the marker and
# pass-through is therefore already the behaviour. Pass-through by ACCIDENT is
# one broadened regex away from becoming a strip, and the failure is silent:
# the answer quietly stops being published and nobody notices for a semester.
# So the count of well-formed blocks is measured before and after processing and
# must match. It also refuses to publish a MALFORMED marker at all -- an
# unmatched BEGIN is precisely the typo that would otherwise reach the site.
#
# SCOPE LIMIT: completion-graded, exam-calibration material only. Anything
# graded on correctness keeps ### BEGIN SOLUTION. Not machine-enforceable; see
# org/pyomo-style-guide.md section 11a.
def published_answer_audit(nb, label, verbose=1):
    """Per-cell count of well-formed published-answer blocks.

    Raises SystemExit if any marker is malformed, so a typo aborts the publish
    instead of quietly changing what gets published.
    """
    findings = []
    counts = []
    for i, cell in enumerate(nb.cells):
        tags = (cell.get("metadata") or {}).get("tags") or []
        f, n = published_answer_findings(
            cell.cell_type, cell.source, tags, where=f"{label}: cell {i}: ")
        findings += f
        counts.append(n)
    if findings:
        print(f"\nABORT: malformed PUBLISHED ANSWER marker in {label}:")
        for f in findings:
            print(f"  {f}")
        raise SystemExit(1)
    if verbose >= 1 and sum(counts):
        print(f"  Passing through {sum(counts)} PUBLISHED ANSWER block(s) "
              f"(deliberate; completion-graded material)")
    return counts


def process_notebook(folder_original, folder_new, filename, verbose=1):

    ''' Remove nbgrader content from notebooks and save updated version
    
    '''

    ## Setup

    # read notebook file
    # `filename`, not the module-level loop variable `file`. Identical for every
    # call the driver below makes (it passes filename=file), but this function
    # NameErrors if called from anywhere else.
    input_notebook = os.path.join(folder_original, filename)
    with open(input_notebook, "r") as fp:
        if verbose >= 1:
            print("\nOpening ",input_notebook)
        nb = nbformat.read(fp, as_version=4)

    # Validate published-answer markers BEFORE anything is rewritten, and record
    # how many blocks there are so the pass-through can be verified afterwards.
    pa_before = published_answer_audit(nb, input_notebook, verbose=verbose)

    # display file metadata
    if verbose >= 2:
        print(f"nbformat = {nb.nbformat}.{nb.nbformat_minor}")
        display(nb.metadata)
        
    ## Remove code elements with specific tag
    def replace_code(pattern, replacement, clear_outputs=False):
        ''' Replace content in code by applying regular expression

        clear_outputs: also discard the cell's stored outputs and execution
            count. Required whenever the removed content is a solution --
            see the comment above SOLUTION_CODE.
        '''

        if verbose >= 1:
            print("Removing following expression: ", pattern)

        count = 0

        regex = re.compile(pattern, re.DOTALL)
        for cell in nb.cells:
            if cell.cell_type == "code" and regex.findall(cell.source):
                cell.source = regex.sub(replacement, cell.source)
                if clear_outputs:
                    cell.outputs = []
                    cell.execution_count = None
                count += 1
                if verbose >= 2:
                    print(f" - {pattern} removed")

        if verbose >= 1:
            print("\t",count," cells processed")

    # IMPORTANT: stripping a solution from `cell.source` is NOT enough. A cell's
    # stored `outputs` are published verbatim, so an instructor notebook that was
    # executed before publishing hands the students the answer anyway -- as text,
    # as a printed number, or as a figure. This was live on the site on
    # 2026-08-21: every graded discussion answer in assignments/Algorithms6-MINLP
    # (answer_1a ... answer_5c) was printed in full under a
    # "# Add your solution here" cell, and assignments/Algorithms1 published the
    # inverse, the solution vector, the eigenvalues and the condition numbers the
    # same way. `grep -r "BEGIN SOLUTION" notebooks/` does not see any of it.
    # Hence clear_outputs=True on both solution patterns below.
    SOLUTION_CODE = "### BEGIN SOLUTION(.*?)### END SOLUTION"
    HIDDEN_TESTS = "### BEGIN HIDDEN TESTS(.*?)### END HIDDEN TESTS"
    replace_code(SOLUTION_CODE, "# Add your solution here", clear_outputs=True)
    replace_code(HIDDEN_TESTS, "# Removed autograder test. You may delete this cell.",
                 clear_outputs=True)

    # -----------------------------------------------------------------------
    # Cells whose OUTPUT is an answer even though their SOURCE is not.
    #
    # Prof. Dowling, 2026-08-22 (JUDGEMENT_CALLS G1c): "I want the instructor
    # copy to have the answers. I then want those answers, including Python
    # output, to get dropped from the published version."
    #
    # The two patterns above cover cells that CONTAIN a solution block. They
    # cannot cover the other case: a cell of fully provided code that CALLS a
    # function the student had to write, so its stored output is the student's
    # deliverable. `Algorithms4` cell 30 is the example -- three lines of given
    # setup, then `barrier_subproblem(...)`, whose implementation is a solution
    # block five cells earlier, and whose full iteration table is stored right
    # there. No regex over the source can tell that apart from
    # `Algorithms3` cell 17, whose stored table the assignment text explicitly
    # gives the student ("The (hopefully) correct results for the test cases are
    # available online in this notebook. Answer the questions using these
    # results.").
    #
    # So it is a per-cell editorial call, and it is recorded per cell, as a
    # standard nbformat cell TAG. Tags survive round-trips and are editable from
    # the Jupyter UI (View > Cell Toolbar > Tags), so marking or unmarking a cell
    # does not mean hand-editing JSON. The instructor source keeps its outputs
    # either way -- only the published copy loses them.
    DROP_OUTPUT_TAG = "drop-output"

    def drop_tagged_outputs():
        count = 0
        for cell in nb.cells:
            if cell.cell_type != "code":
                continue
            if DROP_OUTPUT_TAG not in (cell.get("metadata", {}).get("tags") or []):
                continue
            if cell.get("outputs") or cell.get("execution_count") is not None:
                count += 1
            cell.outputs = []
            cell.execution_count = None
        if verbose >= 1 and count:
            print(f"  Dropped stored output from {count} cell(s) "
                  f"tagged '{DROP_OUTPUT_TAG}'")

    drop_tagged_outputs()

    # Match "./data/" or "../data/" only -- NOT the character in front of them.
    #
    # This was ".\./data/", where the leading "." is a regex wildcard matching
    # ANY character. For "../data/" it happened to match the first dot and the
    # result was correct, which is why the bug survived. For "./data/" it
    # matched the OPENING QUOTE and consumed it, so
    #     data_dir = "./data/parmest_tutorial"
    # published as
    #     data_dir = https://.../parmest_tutorial"
    # -- an unterminated string, i.e. a syntax error on the live site. It is
    # currently live in notebooks/5/Parmest-generate-data.ipynb.
    OLD_DATA_PATH = r"\.\.?/data/"
    NEW_DATA_PATH = "https://raw.githubusercontent.com/ndcbe/optimization/main/notebooks/data/"    
    replace_code(OLD_DATA_PATH, NEW_DATA_PATH)
    
    ## Replace elements in markdown cells
    def replace_markdown(pattern, replacement):
        ''' Replace content in markdown by applying regular expression
    
        '''
    
        if verbose >= 1:
            print("Removing following expression: ", pattern)
    
        count = 0
    
        regex = re.compile(pattern, re.DOTALL)
        for cell in nb.cells:
            if cell.cell_type == "markdown" and regex.findall(cell.source):
                cell.source = regex.sub(replacement, cell.source)
                count += 1
                if verbose >= 2:
                    print(f" - {pattern} removed")
                
        if verbose >= 1:
            print("\t",count," cells processed")
    
    # Process Home Activity Boxes
    replace_markdown('style=\"background-color: rgba\(0,255,0,0.05\) ; padding: 10px; border: 1px solid darkgreen;\"',
                     'class=\"admonition seealso\"')
    replace_markdown('<b>Home Activity</b>:', '<p class=\"title\"><b>Home Activity</b></p>\n')
    replace_markdown('<b>Optional Home Activity</b>:', '<p class=\"title\"><b>Optional Home Activity</b></p>\n')
    
    # Process Tutorial Activity Boxes
    replace_markdown('style=\"background-color: rgba\(255,0,0,0.05\) ; padding: 10px; border: 1px solid darkred;\"',
                     'class=\"admonition danger\"')
    replace_markdown('<b>Tutorial Activity</b>:', '<p class=\"title\"><b>Tutorial Activity</b></p>\n')
    
    # Process Class Activity Boxes
    replace_markdown('style=\"background-color: rgba\(0,0,255,0.05\) ; padding: 10px; border: 1px solid darkblue;\"',
                     'class=\"admonition note\"')
    replace_markdown('<b>Class Activity</b>:', '<p class=\"title\"><b>Class Activity</b></p>\n')
    
    # Process Activities (for 60499)
    replace_markdown('<b>Activity</b>:', '<p class=\"title\"><b>Activity</b></p>\n')
    
    # Process Note Boxes
    replace_markdown('style=\"background-color: rgba\(255,255,0,0.05\) ; padding: 10px; border: 1px solid black;\"',
                     'class=\"admonition tip\"')
    replace_markdown('<b>Note</b>:', '<p class=\"title\"><b>Note</b></p>\n')
    
    # replace links to media with urls
    # 2022-09-21: removed "!" from the beginning both of these expressions to also work on handouts (pdf) in media folder
    # 2022-09-21: the use case is the error propagation handout
    '''
    MEDIA_LINK = '\[(.*)\]\(\.\./\.\./media/(.*\..*)\)'
    IMAGE_LINK = r'[\1](https://ndcbe.github.io/optimization/_images/\2)'
    
    for cell in nb.cells:
        if cell.cell_type == "markdown":
            media_links = re.findall(MEDIA_LINK, cell.source)
            # copy media files to _images
            for txt, media_file in media_links:
                path_to_media_file = f"./media/{media_file}"
                print(f"    found link to media file: ![{txt}](../../media/{media_file})")
                if not os.path.exists(path_to_media_file):
                    print(f"    WARNING: media file {path_to_media_file} not found.")
                else:
                    print(f"    copy media file {media_file} to _images")
                    shutil.copy2(path_to_media_file, "./_build/html/_images")
            # replace media files with urls to _images
            cell.source = re.sub(MEDIA_LINK, IMAGE_LINK, cell.source)

    '''

    replace_markdown('.\./.\./media/',
                     'https://raw.githubusercontent.com/ndcbe/optimization/main/media/')
    
    ## AI-review banner -- last, so it is not disturbed by the rewrites above
    # and so its own text is never subject to them.
    insert_ai_banner(nb,
                     source_rel="/".join(("notebooks",
                                          os.path.basename(folder_original.rstrip("/")),
                                          filename)),
                     published_rel="/".join(("notebooks",
                                             os.path.basename(folder_new.rstrip("/")),
                                             filename)),
                     verbose=verbose)

    ## Verify the published answers actually survived.
    #
    # Compare the multiset of NON-ZERO per-cell counts. Not position by
    # position, and not the raw lists: insert_ai_banner() adds a cell, so the
    # raw lists differ in length by one on every unreviewed notebook even when
    # nothing is wrong. (That is not hypothetical -- the first version of this
    # guard compared the raw lists and aborted the publish on notebooks/1-dev/
    # IP.ipynb, which contains no published answer at all.)
    #
    # Any block that vanished, or that lost a marker to one of the rewrites
    # above, shows up here as a mismatch and aborts the publish. A regression
    # that silently stops publishing an answer is worth failing loudly for;
    # nobody re-reads the generated notebook.
    pa_after = published_answer_audit(nb, f"{input_notebook} (after processing)",
                                      verbose=0)
    nonzero = lambda counts: sorted(c for c in counts if c)  # noqa: E731
    if nonzero(pa_before) != nonzero(pa_after):
        raise SystemExit(
            f"\nABORT: {input_notebook} had {sum(pa_before)} PUBLISHED ANSWER "
            f"block(s) before processing and {sum(pa_after)} after. The "
            f"pipeline is stripping or damaging a block it must pass through.")

    ## Save new notebook
    output_notebook = os.path.join(folder_new, filename)
    
    with open(output_notebook, "w") as fp:
        if verbose >= 1:
            print("Saving ", output_notebook)
        nbformat.write(nb, fp)

# Testing
#process_notebook("./notebooks/01", "03-Flow-control.ipynb")


def publish_all():
    """The publish pass. Paths are relative: run this from the repo ROOT."""
    # IMPORTANT. We assume the source files are in XX-dev and the new files go
    # into XX. The list below is just values for XX.
    folders = ["1", "2", "3", "4", "5", "6", "7", "8", "contrib"]

    for fld in folders:

        # Loop over filenames
        full_folder_name_original = "./notebooks/" + fld + "-dev"
        full_folder_name_new = "./notebooks/" + fld

        print("Processing files in ", full_folder_name_original)

        for file in sorted(os.listdir(full_folder_name_original)):

            # Check if file is a notebook using ending
            if re.match(r"(.*?)\.ipynb$", file):

                # process the notebook!
                process_notebook(full_folder_name_original,
                                 full_folder_name_new, file, verbose=1)

    # Assignments live in the private repo.
    full_folder_name_original = "../optimization-private/notebooks/assignments/"
    full_folder_name_new = "./notebooks/assignments/"

    for file in sorted(os.listdir(full_folder_name_original)):

        # Check if file is a notebook using ending
        if re.match(r"(.*?)\.ipynb$", file):

            # process the notebook!
            process_notebook(full_folder_name_original,
                             full_folder_name_new, file, verbose=1)


# ---------------------------------------------------------------------------
# Self-test.
#
# Runs the real process_notebook() over notebooks built in a temp directory and
# asserts on the FILE IT WROTE, not on an in-memory object. A tool that says OK
# is not evidence until you have watched it say FAIL, so the last two cases
# assert that a malformed marker and a damaged pipeline both abort.

def _selftest_nb(cells):
    return {"cells": cells, "metadata": {}, "nbformat": 4, "nbformat_minor": 4}


def _sc(source, outputs=None):
    return {"cell_type": "code", "execution_count": 1, "metadata": {},
            "outputs": outputs or [], "source": source}


def _sm(source):
    return {"cell_type": "markdown", "metadata": {}, "source": source}


def _so(text):
    return {"output_type": "stream", "name": "stdout", "text": [text]}


SELFTEST_SOLUTION = ("# Compute the optimal diet cost.\n"
                     "### BEGIN SOLUTION\n"
                     "cost = 2.28\n"
                     "### END SOLUTION\n")
SELFTEST_ANSWER_CODE = ("### BEGIN PUBLISHED ANSWER\n"
                        "# 4 foods, 3 nutrient constraints -> 1 degree of freedom\n"
                        "print('cost = 2.28')\n"
                        "### END PUBLISHED ANSWER\n")
SELFTEST_ANSWER_MD = ("Check your work against the answer below.\n"
                      "\n"
                      "<!-- BEGIN PUBLISHED ANSWER -->\n"
                      "DOF = 4 variables - 3 active constraints = 1.\n"
                      "<!-- END PUBLISHED ANSWER -->\n")


def selftest():
    import json
    import tempfile

    ok = True

    def check(label, condition, detail=""):
        nonlocal ok
        if not condition:
            ok = False
        print(f"  [{'PASS' if condition else 'FAIL':4s}] {label}")
        if detail and not condition:
            print(f"         {detail}")

    with tempfile.TemporaryDirectory() as d:
        src_dir = os.path.join(d, "src")
        out_dir = os.path.join(d, "out")
        os.makedirs(src_dir)
        os.makedirs(out_dir)

        def write(name, nb):
            with open(os.path.join(src_dir, name), "w") as fp:
                json.dump(nb, fp)

        write("t.ipynb", _selftest_nb([
            _sc(SELFTEST_SOLUTION, outputs=[_so("cost = 2.28\n")]),
            _sc(SELFTEST_ANSWER_CODE, outputs=[_so("cost = 2.28\n")]),
            _sm(SELFTEST_ANSWER_MD),
            _sc("### BEGIN HIDDEN TESTS\nassert cost == 2.28\n"
                "### END HIDDEN TESTS\n", outputs=[_so("ok\n")]),
        ]))
        process_notebook(src_dir, out_dir, "t.ipynb", verbose=0)
        with open(os.path.join(out_dir, "t.ipynb")) as fp:
            pub = json.load(fp)["cells"]

        s0 = "".join(pub[0]["source"])
        check("solution block stripped from source",
              "BEGIN SOLUTION" not in s0 and "cost = 2.28" not in s0, s0)
        check("stripped cell lost its stored outputs",
              not pub[0]["outputs"], str(pub[0]["outputs"]))

        s1 = "".join(pub[1]["source"])
        check("published answer passed through VERBATIM",
              s1 == SELFTEST_ANSWER_CODE, repr(s1))
        check("published answer KEPT its stored outputs",
              "".join(pub[1]["outputs"][0]["text"]) == "cost = 2.28\n",
              str(pub[1]["outputs"]))

        s2 = "".join(pub[2]["source"])
        check("markdown published answer passed through VERBATIM",
              s2 == SELFTEST_ANSWER_MD, repr(s2))

        s3 = "".join(pub[3]["source"])
        check("hidden tests stripped, outputs cleared",
              "HIDDEN TESTS" not in s3 and not pub[3]["outputs"], s3)

        # Must NOT abort: the AI-review banner INSERTS a cell, which lengthens
        # the per-cell count list. The first version of the pass-through guard
        # compared the raw lists and aborted the whole publish on the first
        # unreviewed notebook it met -- one with no published answer at all.
        write("banner.ipynb", _selftest_nb([
            _sm("# A title\n"),
            _sc(SELFTEST_ANSWER_CODE, outputs=[_so("cost = 2.28\n")]),
        ]))
        saved_status = dict(AI_STATUS)
        AI_STATUS[os.path.join(src_dir, "banner.ipynb")] = ("unreviewed", "1", "0")
        AI_STATUS["/".join(("notebooks", os.path.basename(src_dir),
                            "banner.ipynb"))] = ("unreviewed", "1", "0")
        try:
            process_notebook(src_dir, out_dir, "banner.ipynb", verbose=0)
        except SystemExit as exc:
            check("banner insertion does not trip the pass-through guard",
                  False, str(exc))
        else:
            with open(os.path.join(out_dir, "banner.ipynb")) as fp:
                bcells = json.load(fp)["cells"]
            banner = any(c["metadata"].get("ai_review_banner") for c in bcells)
            banner_ids = [c.get("id") for c in bcells
                          if c["metadata"].get("ai_review_banner")]
            answer = any("".join(c["source"]) == SELFTEST_ANSWER_CODE
                         for c in bcells)
            check("banner insertion does not trip the pass-through guard",
                  banner and answer,
                  f"banner={banner} answer_survived={answer}")
            check("generated banner has a deterministic cell ID",
                  banner_ids == ["ai-review-banner"],
                  repr(banner_ids))
        finally:
            AI_STATUS.clear()
            AI_STATUS.update(saved_status)

        # Must ABORT: an unmatched marker is the typo that would otherwise
        # publish the answer with nothing left to grep for.
        write("bad.ipynb", _selftest_nb([
            _sc("### BEGIN PUBLISHED ANSWER\ncost = 2.28\n")]))
        try:
            process_notebook(src_dir, out_dir, "bad.ipynb", verbose=0)
        except SystemExit:
            check("unmatched PUBLISHED ANSWER marker aborts the publish", True)
        else:
            check("unmatched PUBLISHED ANSWER marker aborts the publish", False,
                  "it published instead")
        check("the aborted notebook was NOT written",
              not os.path.exists(os.path.join(out_dir, "bad.ipynb")))

        # Must ABORT: simulate the regression this guard exists for -- a strip
        # pattern broadened until it eats a published-answer block.
        write("reg.ipynb", _selftest_nb([_sc(SELFTEST_ANSWER_CODE)]))
        # Patch the compiled-pattern path the pipeline actually uses. Verified
        # load-bearing: with the before/after count comparison removed, this
        # same patch publishes '# Add your solution here' and exits 0.
        real_compile = re.compile

        class _EatingPattern:
            def __init__(self, inner):
                self._inner = inner

            def findall(self, s):
                return ["x"] if "PUBLISHED ANSWER" in s else self._inner.findall(s)

            def sub(self, repl, s):
                if "PUBLISHED ANSWER" in s:
                    return "# Add your solution here"
                return self._inner.sub(repl, s)

        re.compile = lambda p, *a, **kw: _EatingPattern(real_compile(p, *a, **kw))
        try:
            process_notebook(src_dir, out_dir, "reg.ipynb", verbose=0)
        except SystemExit:
            check("a pipeline that EATS a published answer aborts", True)
        else:
            check("a pipeline that EATS a published answer aborts", False,
                  "the answer was silently dropped and the publish succeeded")
        finally:
            re.compile = real_compile

    print("\nself-test", "PASSED" if ok else "FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    if "--selftest" in sys.argv:
        sys.exit(selftest())
    publish_all()
