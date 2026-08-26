#!/usr/bin/env python
###############################################################################
# The Institute for the Design of Advanced Energy Systems Integrated Platform
# Framework (IDAES IP) was produced under the DOE Institute for the
# Design of Advanced Energy Systems (IDAES).
#
# Copyright (c) 2018-2023 by the software owners: The Regents of the
# University of California, through Lawrence Berkeley National Laboratory,
# National Technology & Engineering Solutions of Sandia, LLC, Carnegie Mellon
# University, West Virginia University Research Corporation, et al.
# All rights reserved.  Please see the files COPYRIGHT.md and LICENSE.md
# for full copyright and license information.
###############################################################################
# This package was further modified by Alex Dowling for use in the course
# It is available under the IDAES license.

"""
The one course helper: Colab setup, solver install, house figure style, and the
solve -> extract -> plot plumbing the notebooks share with the lecture handouts.

Created by Alex Dowling (adowling@nd.edu) and Jeff Kantor at the University of Notre Dame
with input from John Siirola at Sandia National Laboratories.

To use this script, add the following to a code block in a Jupyter notebook:

```
import sys
if "google.colab" in sys.modules:
    !wget "https://raw.githubusercontent.com/ndcbe/optimization/main/notebooks/helper.py"
    import helper
    helper.easy_install()
else:
    sys.path.insert(0, '../')
    import helper
helper.set_plotting_style()
```

ONE FILE, ON PURPOSE
--------------------
Prof. Dowling, 2026-08-25: *"Let's have helper contain all of the useful
scripts/colab add-ons."*

The load-bearing reason is the cell above. It is the first thing a student runs
and the first thing that can fail, and **every module the course adds costs
another ``wget`` line that can 404**. Two files meant two chances to half-install
and a confusing traceback several cells later. One file is one failure mode.

``notebooks/pyomo_results.py`` used to hold the second half of this file. The
remaining callers migrated here on 2026-08-26, and that compatibility shim was
removed. Import this module directly.

WHAT IS IN HERE
---------------
    Part 1  on_colab / package_available / install_* / easy_install
            set_plotting_style                    -- the house figure style

    Part 2  extract / value_of / table / column / as_dataframe
                                                  -- solved model -> plain Python
            save_results / load_results           -- the committed JSON archive
            save_figure                           -- the committed handout PNG + PDF

🔴 THERE IS DELIBERATELY NO LIBRARY OF ``plot_*()`` FUNCTIONS HERE, and adding
one would be a regression -- see ``figures/README.md``. A notebook is a teaching
artifact: if the student sees only ``plot_frontier(m)`` imported from somewhere,
the plotting has been hidden from the person who is supposed to be learning it.
Merging the *plumbing* into this file does not make it a home for *plots*.
Everything here is the part that is the same for every figure and teaches
nothing.
"""

__version__ = "2026.08.25"

import datetime as _dt
import importlib.util as _ilu
import json
import re
import requests
import shutil
import subprocess
import sys
import os
import os.path
import urllib
import urllib.request
import warnings

# The house figure style. ONE source of style, shared with the LaTeX lecture
# handouts -- see figures/README.md. On Colab only the notebook is present (this
# file itself is fetched by raw URL), so the repo copy cannot be assumed on disk.
_STYLE_URL = (
    "https://raw.githubusercontent.com/ndcbe/optimization/main/figures/dowling.mplstyle"
)
_STYLE_LOCAL = "../../figures/dowling.mplstyle"

# figure.figsize is DELIBERATELY not taken from the style file. See the docstring
# of set_plotting_style below; 6.4 x 4.8 is matplotlib's own default, which is
# what every notebook in this repo has always rendered at.
NOTEBOOK_FIGSIZE = (6.4, 4.8)


def set_plotting_style(figsize=NOTEBOOK_FIGSIZE):
    """Apply the course house figure style to every subsequent matplotlib figure.

    Loads ``figures/dowling.mplstyle`` -- the single source of figure style,
    shared with the LaTeX lecture handouts -- so a notebook figure and a handout
    figure look like they came from the same course. That brings in the
    Okabe-Ito colour cycle paired element-wise with a linestyle cycle (so every
    series carries a redundant, colour-free identity and survives greyscale
    printing), viridis as the default colormap, inward ticks on all four sides,
    and the guide's font and line weights. Read the header of the style file for
    why each of those is the way it is.

    Arguments:
        figsize: default figure size in inches, or None to accept the style
            file's own ``figure.figsize``.

    Notes:
        **Why figsize is overridden.** The style file sets ``figure.figsize: 4, 4``,
        which is calibrated for a single-column figure in the printed handout.
        A notebook figure is rendered inline in a browser at its native size, and
        at 4 x 4 the style's own 16 pt bold axis labels and 15 pt tick labels no
        longer fit: x tick labels get dropped and legends collide with the data.
        Canvas size is layout, and layout is per-medium; everything that is
        figure *identity* -- colour, linestyle, colormap, fonts, ticks -- is
        taken from the style file unchanged. Individual figures should still set
        their own ``figsize`` when the aspect ratio matters, exactly as the
        scripts in ``figures/plots/`` do.

        **Grid.** The style sets ``axes.grid: False``. A notebook that calls
        ``plt.grid(True)`` still gets a grid; the house convention is to leave it
        off and use light ``axvline`` rules where a reading aid is needed.
    """
    # ⚠ Imported HERE, not at module scope. This file is now also imported by
    # scripts/check_results_fresh.py, which is a
    # checker that must run in CI with no display and no plotting stack in
    # play. set_plotting_style is the only function in this file that needs
    # pyplot, so it is the only place that pays for it.
    import matplotlib.pyplot as plt

    style = _STYLE_URL if on_colab() else _STYLE_LOCAL

    try:
        plt.style.use(style)
    except (OSError, ValueError) as e:
        # Never let a missing style file break a notebook: a wrong-looking plot
        # is recoverable, a stopped notebook in front of a class is not.
        print(f"WARNING: could not load the house style from {style} ({e}).")
        print("Falling back to matplotlib defaults with the course line width.")
        plt.rc("lines", linewidth=3)

    if figsize is not None:
        plt.rc("figure", figsize=figsize)


def _check_available(executable_name):
    """Utility to check in an executable is available"""
    return shutil.which(executable_name) or os.path.isfile(executable_name)


def package_available(package_name):
    """Utility to check if a package/executable is available

    This supports customization, e.g., glpk, for special package names
    """

    if package_name == "glpk":
        return _check_available("glpsol")
    else:
        return _check_available(package_name)


def on_colab():
    """Utility returns True if executed on Colab, False otherwise"""
    return "google.colab" in sys.modules

def install_idaes(verbose=False):
    """Installs latest version of IDAES-PSE via pip

    Argument:
        verbose: bool, if True, display console output from pip install

    """

    try:
        import idaes

        print("idaes was found! No need to install.")
    except ImportError:
        print("Installing idaes via pip...")
        v = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", "idaes_pse"],
            check=True,
            capture_output=True,
            text=True,
        )
        if verbose:
            print(v.stdout)
            print(v.stderr)
        print("idaes was successfully installed")
        v = subprocess.run(
            ["idaes", "--version"], check=True, capture_output=True, text=True
        )
        print(v.stdout)
        print(v.stderr)


def install_ipopt(verbose=False, try_conda_as_backup=False):
    """Install Ipopt and possibly other solvers.

    If running on Colab, this will install Ipopt, k_aug, and other COIN-OR
    solvers via idaes get-extensions.

    Arguments:
        verbose: bool, if True, display console output from idaes get-extensions and conda
        try_conda_as_backup: bool, if True, install ipopt via conda if idaes get-extensions fails
    """

    # Check if Ipopt (solver) is available. If not, install it.
    if not package_available("ipopt"):
        print("Running idaes get-extensions to install Ipopt, k_aug, and more...")
        v = subprocess.run(
            ["idaes", "get-extensions"], check=True, capture_output=True, text=True
        )
        if verbose:
            print(v.stdout)
            print(v.stderr)
        _update_path()
        print("Checking solver versions:")
        _print_solver_versions()

    # Check again if Ipopt is available. If not, try conda
    if try_conda_as_backup and not package_available("ipopt"):
        print("Installing Ipopt via conda...")
        v = subprocess.run(
            [sys.executable, "-m", "conda", "install", "-c", "conda-forge", "ipopt"],
            check=True,
            capture_output=True,
            text=True,
        )
        if verbose:
            print(v.stdout)
            print(v.stderr)
        print("Checking ipopt version:")
        _print_single_solver_version("ipopt")

def install_glpk():
    """Install GLPK via apt-get on Colab

    Deprecated: HiGHS (see install_highs) is the course default LP/MILP solver.
    This function is kept for the handful of older contributed notebooks that
    still call glpsol.
    """
    if not package_available("glpk") and on_colab():
        print("Installing glpk via apt-get...")
        os.system('apt-get install -y -qq glpk-utils')


def install_highs(verbose=False):
    """Installs HiGHS via pip

    HiGHS is the default LP/MILP solver for this course. It is distributed as
    the Python package `highspy` and is used from Pyomo via
    `pyo.SolverFactory('appsi_highs')`.

    Argument:
        verbose: bool, if True, display console output from pip install

    """

    try:
        import highspy

        print("highspy was found! No need to install.")
    except ImportError:
        print("Installing highspy via pip...")
        v = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", "highspy"],
            check=True,
            capture_output=True,
            text=True,
        )
        if verbose:
            print(v.stdout)
            print(v.stderr)
        print("highspy was successfully installed")


def easy_install(verbose=False):
    """Install IDAES and solvers in one step"""

    install_idaes(verbose=verbose)
    install_ipopt(verbose=verbose, try_conda_as_backup=True)
    install_highs(verbose=verbose)

def _update_path():
    """Add idaes executables to PATH"""
    if not re.search(re.escape("/root/.idaes/bin/"), os.environ["PATH"]):
        os.environ["PATH"] = "/root/.idaes/bin/:" + os.environ["PATH"]


def _print_single_solver_version(solvername):
    """Print the version for a single solver
    Arg:
        solvername: solver executable name (string)
    """
    v = subprocess.run([solvername, "-v"], check=True, capture_output=True, text=True)
    print(v.stdout)
    print(v.stderr)


def _print_solver_versions():
    """Print versions of solvers in idaes get-extensions

    This is the primary check that solvers installed correctly and are callable
    """

    # This does not work for cbc and clp; calling --version with these solvers,
    # enters their scripting language mode.
    for s in ["ipopt", "k_aug", "couenne", "bonmin", "ipopt_l1", "dot_sens"]:
        _print_single_solver_version(s)



# ===========================================================================
# PART 2 -- Solve -> extract -> plot: the notebook is the source of its figures
# ===========================================================================
r"""
    build + solve  -->  results = extract(...)  -->  def plot_x(results): ...
                              |                            |
                    figures/results/<name>.json      media/figures/<name>.{png,pdf}
                    (committed; lets a STYLE change      (committed; what the
                     re-render with no solver)            handout \includegraphics)

WHY THIS EXISTS
---------------
Prof. Dowling, 2026-08-24:

    "If it is for a Pyomo example, I want to plot the results from Pyomo. ...
    I do not want to recreate figures with scipy for the Pyomo sections."

    "What I do like is to separate the Pyomo solve from the analysis. For
    example, we could extract the results from Pyomo and then make functions
    that plot those results."

    "For research code, I encourage my students to pickle or otherwise extract
    and store the optimization results. That way, they can use archived results
    to adjust their plotting scripts. Thus, adjusting the plotting script does
    not require resolving the model."

    "But Python generated plots that visualize Pyomo related data -- those
    should live in the notebooks."

Before this, a handout figure re-derived the notebook's answer with
``scipy.optimize`` so ``make`` would need no solver. Two implementations of one
model is the drift ``figures/`` exists to prevent, and the handout showed a
number the notebook never computed.

THE FORMAT IS JSON, NOT PICKLE, AND THAT IS DELIBERATE
------------------------------------------------------
In research code you would reach for ``pickle``, and the notebooks say so. A
COMMITTED artifact is different: a pickle in git is an unreviewable binary blob
that breaks on a library version bump and whose diff nobody can read. Everything
written here is UTF-8 JSON -- human-readable, git-diffable, loadable by any
Python that can ``import json``. One file per figure::

    figures/results/<figure-name>.json
    {"meta": {provenance: notebook, tagged cell, solver, digest},
     "data": {whatever the plotting cell needs}}

``scripts/check_results_fresh.py`` polices ``meta``. A committed generated
artifact that nothing checks goes stale silently.

WHY THE ARCHIVE STILL EXISTS NOW THAT THE NOTEBOOK WRITES THE PDF
-----------------------------------------------------------------
Because the common regeneration is a STYLE change, not a model change. The
house style was reworked across every figure in the repo on 2026-08-24. Doing
that with notebook-only generation means running ~20 notebooks with Ipopt;
with the archive it is ``python3 figures/render_from_notebook.py --all``,
seconds, no solver binary, no Pyomo. That -- and only that -- is the archive's
job now.

COLAB
-----
On Colab only the notebook exists; the repo is not on disk. ``save_results``
and ``save_figure`` are **no-ops that print a note** when the repo is not on
disk, so a student running on Colab sees the figure inline and nothing raises.
Writing is a maintainer action: a Colab session has nowhere to commit to.
``load_results`` falls back to the raw URL and does work there.

⚠ The raw-URL fallback resolves against ``main``. Anything added to this file
on a branch is not reachable from Colab until it is pushed.

🔴 NEITHER WRITER RETURNS A VALUE, AND THAT IS THE FIX FOR A REAL BUG
----------------------------------------------------------------------
``save_results`` and ``save_figure`` used to return the path they wrote. The
cell contract says a plot cell *ends* with ``helper.save_figure(fig, "<name>")``,
so in a notebook that return became the cell's ``execute_result`` -- and the
published course website displayed an absolute path out of the maintainer's
home directory::

    '/Users/.../optimization/figures/results/portfolio-efficient-frontier.json'

13 cells across 5 notebooks. **The contract induced it**, so every future
conversion would have inherited it, and suppressing it call-site by call-site
is a rule somebody has to remember. Returning ``None`` makes the leak
structurally impossible instead. Nothing ever consumed the value -- verified
across the notebooks, ``figures/render_from_notebook.py`` and
``scripts/check_results_fresh.py`` -- so nothing had to change to accommodate
it. Both functions still PRINT what they wrote, which is the part a maintainer
actually reads.
"""

RAW_BASE = "https://raw.githubusercontent.com/ndcbe/optimization/main"

# This file lives in <repo>/notebooks/, so the repo root is one level up. On
# Colab it was downloaded into the working directory and _REPO is meaningless;
# every use is guarded by an existence check rather than by a Colab check,
# because "is the repo on disk" is the question that actually matters.
_HERE = os.path.dirname(os.path.abspath(__file__))
_REPO = os.path.dirname(_HERE)

RESULTS_SUBDIR = os.path.join("figures", "results")
FIGURES_SUBDIR = os.path.join("media", "figures")

# The dpi the Makefile uses for every other PNG in media/figures. Kept equal on
# purpose: a notebook-generated figure and a script-generated one must be
# indistinguishable in the built site.
PNG_DPI = 300

# meta keys every archived result must carry. check_results_fresh.py imports
# this rather than restating it, so the two halves cannot disagree.
REQUIRED_META = ("schema", "figure", "notebook", "generated")
SCHEMA = 1

# The tag that marks a notebook cell as the source of a handout figure. See
# figures/render_from_notebook.py for the cell contract.
FIGURE_TAG_PREFIX = "figure:"


def have_repo() -> bool:
    """Can helper writers update the public repo?

    False on Colab, on a bare notebook copy, and during the read-only notebook
    execution audit. The audit still reads local inputs; it simply must not
    rewrite committed result archives or rendered figures as a side effect.
    """
    return not os.environ.get("OPTIMIZATION_NOTEBOOK_READ_ONLY") and (
        os.path.isdir(os.path.join(_REPO, "figures"))
        and os.path.isdir(os.path.join(_REPO, "notebooks"))
    )


# ---------------------------------------------------------------------------
# Stage 1 -> 2: extract a solved Pyomo model into plain Python
# ---------------------------------------------------------------------------
def value_of(obj):
    """One Pyomo component -> a plain float, or a plain dict for an indexed one.

    Handles Var, Param, Objective, Expression and bare expressions. An indexed
    component becomes ``{index: float}``, with the index stringified when it is
    not already a JSON-safe scalar -- JSON object keys are strings, and a tuple
    index would otherwise round-trip into something unusable.

    A component with no value comes back as ``None`` rather than raising: the
    caller usually wants to see the hole, and ``json`` writes it as ``null``.
    """
    import pyomo.environ as pyo

    if hasattr(obj, "is_indexed") and obj.is_indexed():
        out = {}
        for idx in obj:
            key = idx if isinstance(idx, (str, int)) else str(idx)
            out[key] = _scalar(pyo.value(obj[idx], exception=False))
        return out
    return _scalar(pyo.value(obj, exception=False))


def _scalar(v):
    """float / int / None, never a numpy scalar -- json.dump cannot write those."""
    if v is None:
        return None
    if isinstance(v, bool):
        return bool(v)
    if isinstance(v, int):
        return int(v)
    try:
        return float(v)
    except (TypeError, ValueError):
        return str(v)


def extract(model=None, **components):
    """Solved model -> a plain dict, one entry per named component::

        results = helper.extract(m, x=m.x, variance=m.OBJ, rho=m.rho)
        # {'x': {'DJI': 0.31, ...}, 'variance': 1.83e-05, 'rho': 0.0008}

    ``model`` is accepted and ignored as the first positional argument so the
    call can read ``extract(m, ...)``; the components carry their own parent.

    Anything that is not a Pyomo component passes through ``_jsonable``, so
    numpy arrays, pandas objects, lists and scalars can be mixed in with no
    ceremony. This helper is small on purpose: if extracting a particular model
    needs more than this, **write that extraction in the notebook** rather than
    growing an abstraction here.
    """
    out = {}
    for name, comp in components.items():
        if hasattr(comp, "is_indexed") or hasattr(comp, "is_expression_type"):
            out[name] = value_of(comp)
        else:
            out[name] = _jsonable(comp)
    return out


def _jsonable(obj):
    """Recursively convert numpy / pandas / Pyomo objects to JSON-safe Python."""
    if obj is None or isinstance(obj, (bool, str, int, float)):
        return obj
    if isinstance(obj, dict):
        return {
            (k if isinstance(k, (str, int)) else str(k)): _jsonable(v)
            for k, v in obj.items()
        }
    if hasattr(obj, "columns") and hasattr(obj, "index"):
        return table(obj)  # pandas DataFrame
    if hasattr(obj, "to_dict") and hasattr(obj, "index"):
        return _jsonable(obj.to_dict())  # pandas Series
    if hasattr(obj, "tolist"):
        return obj.tolist()  # numpy array or numpy scalar
    if isinstance(obj, (list, tuple)):
        return [_jsonable(v) for v in obj]
    if hasattr(obj, "is_indexed"):
        return value_of(obj)
    return _scalar(obj)


# ---------------------------------------------------------------------------
# Tables
# ---------------------------------------------------------------------------
def table(df, columns=None):
    """DataFrame (or a list of rows) -> ``{"columns": [...], "rows": [[...]]}``.

    A parameter sweep is naturally a table, and this is the one encoding this
    project uses for one. Split form is chosen over a list of
    ``{column: value}`` records because records repeat every column name on
    every row: the portfolio sweep is 60 x 7, which is 420 repetitions of seven
    strings, and the git diff of a re-solve stops being readable. Split form
    keeps one row per line.
    """
    if hasattr(df, "columns"):
        return {
            "columns": [str(c) for c in df.columns],
            "rows": [[_scalar(v) for v in row] for row in df.to_numpy().tolist()],
        }
    rows = [list(r) for r in df]
    return {
        "columns": list(columns or range(len(rows[0]) if rows else 0)),
        "rows": [[_scalar(v) for v in r] for r in rows],
    }


def as_dataframe(tbl):
    """Inverse of :func:`table`. Needs pandas."""
    import pandas as pd

    return pd.DataFrame(tbl["rows"], columns=tbl["columns"])


def column(tbl, name):
    """One column of a :func:`table` as a plain list, without needing pandas."""
    j = tbl["columns"].index(name)
    return [row[j] for row in tbl["rows"]]


# ---------------------------------------------------------------------------
# Stage 2: the committed JSON archive
# ---------------------------------------------------------------------------
def results_dir():
    """Absolute path to ``figures/results/``, or None when the repo is off disk."""
    return os.path.join(_REPO, RESULTS_SUBDIR) if have_repo() else None


def save_results(
    name,
    data,
    *,
    notebook,
    source_tag=None,
    description="",
    solver=None,
    quiet=False,
):
    """Write ``figures/results/<name>.json``. Prints what it wrote; returns nothing.

    ⚠ Returns ``None`` on purpose -- see "NEITHER WRITER RETURNS A VALUE" in
    this section's header. It used to return the path, and because the cell
    contract puts this call last in a notebook cell, that path was published on
    the course website as the cell's output.

    Arguments:
        name: the FIGURE name -- the same ``<name>`` as
            ``media/figures/<name>.png``. One archive per figure keeps the
            correspondence greppable and lets the checker verify it.
        data: JSON-safe values, normally from :func:`extract` and :func:`table`.
        notebook: repo-relative path of the notebook that produced it, e.g.
            ``"notebooks/1-dev/Portfolio-Optimization.ipynb"``. ⚠ Always the
            ``-dev`` copy: ``notebooks/<n>/`` is generated output.
        source_tag: the ``handout:<tag>`` on the cell that defines the model,
            when there is one. Given that, and the notebook on disk, the model
            cell is digested and the digest stored -- which is what makes
            staleness detectable: change the model and the checker says so.
        solver: solver name and version. Recorded, never compared; solver
            versions move and that is not a defect.
    """
    d = results_dir()
    if d is None:
        if not quiet:
            print(
                f"[helper] not archiving '{name}': the repo is not on disk "
                "(Colab?).\n"
                "                The committed copy in figures/results/ is what the "
                "handout reads."
            )
        return None

    payload = {
        "meta": {
            "schema": SCHEMA,
            "figure": name,
            "notebook": notebook,
            "description": description,
            "generated": _dt.date.today().isoformat(),
            "generator": f"helper {__version__}",
            "source_tag": source_tag,
            "source_digest": digest_of_tag(source_tag) if source_tag else None,
            "solver": solver or "",
        },
        "data": _jsonable(data),
    }
    os.makedirs(d, exist_ok=True)
    path = os.path.join(d, name + ".json")
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, indent=1, sort_keys=False)
        fh.write("\n")
    if not quiet:
        print(f"[helper] wrote {os.path.relpath(path, _REPO)}")


def load_results(name):
    """Read ``figures/results/<name>.json``; falls back to the raw URL on Colab.

    Returns the whole payload, ``{"meta": ..., "data": ...}``.
    """
    local = os.path.join(_REPO, RESULTS_SUBDIR, name + ".json")
    if os.path.exists(local):
        return json.loads(open(local, encoding="utf-8").read())
    url = f"{RAW_BASE}/figures/results/{name}.json"
    with urllib.request.urlopen(url) as fh:  # noqa: S310
        return json.loads(fh.read().decode("utf-8"))


# ---------------------------------------------------------------------------
# Stage 3: the committed handout artifact
# ---------------------------------------------------------------------------
def save_figure(fig, name, *, dpi=PNG_DPI, quiet=False):
    """Write ``media/figures/<name>.png`` and ``.pdf``. No-op when off-repo.

    ⚠ Returns ``None`` on purpose -- see "NEITHER WRITER RETURNS A VALUE" in
    this section's header. This call is the LAST statement of every tagged
    figure cell, so anything it returned was published as that cell's output.


    PNG is what the website and the notebooks display (300 dpi, raster, works
    on Colab and GitHub); PDF is what the LaTeX handouts
    ``\\includegraphics`` (vector, sharp at any print size). Both come from one
    Figure object, so the site and the course pack cannot show different
    pictures.

    ⚠ The figure must set its own ``figsize``. ``helper.set_plotting_style()``
    overrides ``figure.figsize`` for on-screen readability while
    ``figures/render_from_notebook.py`` does not, so a figure that relies on the
    default renders at two different aspect ratios depending on who generated
    it. Every handout figure passes ``figsize=`` explicitly.
    """
    if not have_repo():
        if not quiet:
            print(
                f"[helper] not saving '{name}': the repo is not on disk "
                "(Colab?).\n"
                "                The figure is displayed above; the committed copy "
                "in media/figures/ is what the handout uses."
            )
        return
    out = os.path.join(_REPO, FIGURES_SUBDIR)
    os.makedirs(out, exist_ok=True)
    png = os.path.join(out, name + ".png")
    pdf = os.path.join(out, name + ".pdf")
    fig.savefig(png, dpi=dpi)
    fig.savefig(pdf)
    if not quiet:
        print(f"[helper] wrote {os.path.relpath(png, _REPO)} and .pdf")


# ---------------------------------------------------------------------------
# Freshness: digest the model cell the results came from
# ---------------------------------------------------------------------------
def _extractor():
    """Import ``scripts/extract_pyomo_code.py`` when the repo is on disk.

    Reused rather than reimplemented, on purpose. It already defines what "the
    same model" means -- docstrings dropped, comments stripped, blank lines
    removed -- and ``check_code_sync.py`` records the lesson that a second
    definition of normalisation is a checker that agrees with nobody.
    """
    p = os.path.join(_REPO, "scripts", "extract_pyomo_code.py")
    if not os.path.exists(p):
        return None
    spec = _ilu.spec_from_file_location("extract_pyomo_code", p)
    mod = _ilu.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def digest_of_tag(tag):
    """sha256[:16] of the normalised source of the ``handout:<tag>`` cell.

    ``None`` when the repo or the tag is unavailable -- on Colab, for instance.
    The checker reads a null digest as "unverifiable", a warning rather than a
    failure; every committed artifact is generated locally and carries one.

    ⚠ It digests the notebook FILE ON DISK, not the cell you are running. In a
    live session with unsaved edits those differ. Save the notebook before
    archiving, exactly as you would before running ``check_code_sync.py``.
    """
    ex = _extractor()
    if ex is None:
        return None
    bare = tag[len(ex.TAG_PREFIX):] if tag.startswith(ex.TAG_PREFIX) else tag
    # ⚠ Suppress nbformat's MissingIDFieldWarning while we read the notebooks
    # off disk. Added 2026-08-25 after the warning was BAKED INTO PUBLISHED
    # OUTPUT three separate times: nbformat writes it to stderr, the running
    # cell captures stderr as a stream output, and the warning text contains
    # the interpreter's absolute path -- so the course website ended up
    # displaying /Users/<name>/opt/anaconda3/envs/... Scrubbing the stored
    # output does not help, because the next re-execution puts it straight
    # back; this is the only place that can stop it.
    # It is a warning ABOUT NOTEBOOKS WE ONLY READ, never write, so ignoring
    # it here changes nothing except what students see.
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        snippets, _ = ex.find_snippets([ex.DEFAULT_NB_GLOB])
    for s in snippets:
        if s.tag == bare:
            return ex.digest(s.source)
    return None
