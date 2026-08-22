import nbformat
from nbformat.v4.nbbase import new_code_cell, new_markdown_cell, new_notebook
import re
import os
import shutil

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

    ## Save new notebook
    output_notebook = os.path.join(folder_new, filename)
    
    with open(output_notebook, "w") as fp:
        if verbose >= 1:
            print("Saving ", output_notebook)
        nbformat.write(nb, fp)

# Testing
#process_notebook("./notebooks/01", "03-Flow-control.ipynb")

"""
IMPORTANT. We assume the source files are in XX-dev and the new files go into XX.
The list below is just values for XX.
"""
folders = ["1", "2", "3", "4", "5","6","7","8","contrib"]

for fld in folders:
    
    # Loop over filenames
    full_folder_name_original = "./notebooks/" + fld + "-dev"
    full_folder_name_new = "./notebooks/" + fld
    
    print("Processing files in ", full_folder_name_original)
    
    for file in sorted(os.listdir(full_folder_name_original)):
        
        # Check if file is a notebook using ending
        if re.match("(.*?)\.ipynb$", file):
            
            # process the notebook!
            process_notebook(full_folder_name_original, full_folder_name_new, file, verbose=1)

"""
Process assignments which are in a private repo
"""
# Loop over filenames
full_folder_name_original = "../optimization-private/notebooks/assignments/"
full_folder_name_new = "./notebooks/assignments/"

for file in sorted(os.listdir(full_folder_name_original)):
    
    # Check if file is a notebook using ending
    if re.match("(.*?)\.ipynb$", file):
        
        # process the notebook!
        process_notebook(full_folder_name_original, full_folder_name_new, file, verbose=1)