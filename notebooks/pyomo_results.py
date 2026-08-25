r"""Solve -> extract -> plot: the notebook is the source of every figure it makes.

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

    "If the figure is generated in a notebook, such as showing algorithm
    results in Part II, we should use the version from the notebook in the
    lecture notes."

    "But Python generated plots that visualize Pyomo related data -- those
    should live in the notebooks."

Before this, a handout figure re-derived the notebook's answer with
``scipy.optimize`` so ``make`` would need no solver. Two implementations of one
model is the drift ``figures/`` exists to prevent, and the handout showed a
number the notebook never computed.

🔴 THE PLOTTING CODE LIVES IN THE NOTEBOOK CELL, NOT IN THIS MODULE
--------------------------------------------------------------------
There is deliberately no library of ``plot_*()`` functions here, and adding one
would be a regression. A notebook is a teaching artifact: if the student sees
only ``plot_frontier(m)`` imported from somewhere, the plotting has been hidden
from the person who is supposed to be learning it. Everything in this module is
plumbing -- extraction, archiving, saving at the right dpi to the right path --
i.e. the parts that are the same for every figure and teach nothing.

WHAT THIS MODULE IS FOR
-----------------------
    extract / table / column / as_dataframe   solved model -> plain Python
    save_results / load_results               the committed JSON archive
    save_figure                               the committed handout PNG + PDF

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
On Colab only the notebook exists; the repo is not on disk. Fetch this file the
way ``helper.py`` is fetched::

    import sys
    if "google.colab" in sys.modules:
        !wget -q "https://raw.githubusercontent.com/ndcbe/optimization/main/notebooks/helper.py"
        !wget -q "https://raw.githubusercontent.com/ndcbe/optimization/main/notebooks/pyomo_results.py"
        import helper
        helper.easy_install()
    else:
        sys.path.insert(0, "../")
        import helper
    helper.set_plotting_style()
    import pyomo_results as pyr

``save_results`` and ``save_figure`` are **no-ops that print a note** when the
repo is not on disk, so a student running on Colab sees the figure inline and
nothing raises. Writing is a maintainer action: a Colab session has nowhere to
commit to. ``load_results`` falls back to the raw URL and does work there.

⚠ The raw-URL fallback resolves against ``main``. A file added on a branch is
not reachable from Colab until it is pushed.
"""

from __future__ import annotations

import datetime as _dt
import importlib.util as _ilu
import json
import os
import sys
import urllib.request

__version__ = "2026.08.24"

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


def on_colab() -> bool:
    return "google.colab" in sys.modules


def have_repo() -> bool:
    """Is the public repo on disk? False on Colab, and on a bare notebook copy."""
    return os.path.isdir(os.path.join(_REPO, "figures")) and os.path.isdir(
        os.path.join(_REPO, "notebooks")
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

        results = pyr.extract(m, x=m.x, variance=m.OBJ, rho=m.rho)
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
    """Write ``figures/results/<name>.json``. Returns the path, or None on Colab.

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
                f"[pyomo_results] not archiving '{name}': the repo is not on disk "
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
            "generator": f"pyomo_results {__version__}",
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
        print(f"[pyomo_results] wrote {os.path.relpath(path, _REPO)}")
    return path


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

    Returns the PNG path, or None when the repo is not on disk.
    """
    if not have_repo():
        if not quiet:
            print(
                f"[pyomo_results] not saving '{name}': the repo is not on disk "
                "(Colab?).\n"
                "                The figure is displayed above; the committed copy "
                "in media/figures/ is what the handout uses."
            )
        return None
    out = os.path.join(_REPO, FIGURES_SUBDIR)
    os.makedirs(out, exist_ok=True)
    png = os.path.join(out, name + ".png")
    pdf = os.path.join(out, name + ".pdf")
    fig.savefig(png, dpi=dpi)
    fig.savefig(pdf)
    if not quiet:
        print(f"[pyomo_results] wrote {os.path.relpath(png, _REPO)} and .pdf")
    return png


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
    snippets, _ = ex.find_snippets([ex.DEFAULT_NB_GLOB])
    for s in snippets:
        if s.tag == bare:
            return ex.digest(s.source)
    return None
