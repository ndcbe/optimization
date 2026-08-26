#!/usr/bin/env python3
r"""Re-render a notebook's handout figure from its ARCHIVED results. No solver.

    python3 render_from_notebook.py --list
    python3 render_from_notebook.py portfolio-efficient-frontier
    python3 render_from_notebook.py --all
    python3 render_from_notebook.py --selftest

WHAT THIS IS FOR, AND WHAT IT IS NOT FOR
----------------------------------------
Prof. Dowling, 2026-08-24:

    "If the figure is generated in a notebook, such as showing algorithm
     results in Part II, we should use the version from the notebook in the
     lecture notes."
    "Python generated plots that visualize Pyomo related data -- those should
     live in the notebooks."

So the notebook is the source. Running the notebook builds the model, solves
it, plots it, and writes ``media/figures/<name>.{png,pdf}`` plus the archive
``figures/results/<name>.json``. **That is the normal path, and this script is
not it.**

This script exists for one case: **a STYLE change**. The house style was
reworked across every figure in the repo on 2026-08-24. Re-rendering ~27
notebook-generated figures by running ~20 notebooks needs Pyomo, Ipopt, HiGHS
and several minutes; re-rendering them from the committed archives needs
matplotlib and a few seconds, and works in CI where no solver exists. It is
also what lets ``make`` still produce every figure on a machine with no solver
binary, exactly as ``figures/README.md`` has always promised.

🔴 IT RUNS THE NOTEBOOK'S OWN PLOTTING CELL. THERE IS NO SECOND COPY.
----------------------------------------------------------------------
The obvious way to get a solver-free re-render is a ``figures/plots/<name>.py``
that re-plots the archived data. That is a second implementation of the
plotting, it drifts from the notebook the first time someone edits one of them,
and drift between two copies of one figure is the entire failure mode
``figures/`` exists to prevent. So this driver does not reimplement anything:
it locates the notebook cell tagged ``figure:<name>``, binds ``results`` to the
archived data, and ``exec``s that cell's source. The notebook cell is the only
copy of the plotting code, on both paths.

THE CELL CONTRACT
-----------------
A cell that generates a handout figure carries the notebook tag
``figure:<name>``, where ``<name>`` is the figure's name --
``media/figures/<name>.png``, ``figures/results/<name>.json``, and what the
handout ``\includegraphics``.

  ON ENTRY the cell may assume these names are bound::

      results   the "data" block of figures/results/<name>.json
      np, pd, plt          numpy, pandas, matplotlib.pyplot
      helper               notebooks/helper.py

  ON EXIT the cell must leave::

      fig       the matplotlib Figure to write

  THE CELL MUST NOT: solve, import Pyomo, read a data file, use a random number
  without a fixed seed, or reference any name defined in an earlier cell other
  than the ones listed above. Everything the plot needs must be in ``results``.
  That restriction is what makes the cell runnable in both places; it is also
  the "separate the solve from the analysis" discipline, enforced rather than
  requested.

  ⚠ THE CELL MUST SET ITS OWN ``figsize``. ``helper.set_plotting_style()``
  overrides ``figure.figsize`` for on-screen readability and this driver does
  not, so a figure relying on the default renders at two different aspect
  ratios depending on who generated it.

  ⚠ THE CELL MUST NOT ``import _house``. ``figures/plots/_house.py`` is not on
  disk on Colab. A notebook figure needing a hatch sequence copies the literal
  with a comment pointing here.

  The cell SHOULD end with ``helper.save_figure(fig, "<name>")``. That call is a
  no-op off-repo, and this driver saves the figure itself, so it is harmless on
  both paths and it is what makes the notebook the generator. It returns
  ``None``, so ending the cell with it prints nothing -- which is the point:
  when it returned the path, that absolute path was published as the cell's
  output on the course website.

WHY ``exec`` AND NOT ``nbclient``
---------------------------------
Executing the whole notebook would need the solver -- the thing being avoided.
Executing one cell in a prepared namespace is the smallest thing that works,
and the cell contract above is exactly the interface that makes it safe. The
namespace is fresh per figure, so two figures cannot leak into each other.
"""

from __future__ import annotations

import argparse
import glob
import json
import os
import sys
import textwrap

import matplotlib

matplotlib.use("Agg")  # no display; this runs from make and from CI
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
STYLE = os.path.join(HERE, "dowling.mplstyle")
RESULTS_DIR = os.path.join(HERE, "results")
OUT_DIR = os.path.join(REPO, "media", "figures")

# ⚠ notebooks/<n>/ is GENERATED output that process_notebooks.py overwrites.
# The sources are notebooks/<n>-dev/, and only those are scanned.
NB_GLOB = os.path.join(REPO, "notebooks", "*-dev", "*.ipynb")

TAG_PREFIX = "figure:"

sys.path.insert(0, os.path.join(REPO, "notebooks"))
import helper  # noqa: E402


# ---------------------------------------------------------------------------
def find_figure_cells(nb_glob=NB_GLOB):
    """{figure name: (notebook path, cell index, cell source)} across all notebooks.

    A duplicate tag is fatal rather than last-one-wins: two cells claiming one
    figure means one of them is silently not the source, which is the class of
    bug this whole directory exists to make impossible.
    """
    found, dupes = {}, []
    for path in sorted(glob.glob(nb_glob)):
        try:
            nb = json.load(open(path, encoding="utf-8"))
        except (OSError, ValueError):
            continue
        for i, cell in enumerate(nb.get("cells", [])):
            if cell.get("cell_type") != "code":
                continue
            for tag in cell.get("metadata", {}).get("tags", []) or []:
                if not tag.startswith(TAG_PREFIX):
                    continue
                name = tag[len(TAG_PREFIX):]
                src = "".join(cell.get("source", []))
                if name in found:
                    dupes.append((name, found[name][0], path))
                found[name] = (path, i, src)
    if dupes:
        for name, a, b in dupes:
            print(
                f"ERROR: two cells are tagged '{TAG_PREFIX}{name}':\n"
                f"  {os.path.relpath(a, REPO)}\n  {os.path.relpath(b, REPO)}",
                file=sys.stderr,
            )
        raise SystemExit(2)
    return found


def render(name, cells=None, out_dir=OUT_DIR, results_dir=RESULTS_DIR, dpi=300):
    """Render one figure from its archived results. Returns the PNG path."""
    cells = find_figure_cells() if cells is None else cells
    if name not in cells:
        raise SystemExit(
            f"no notebook cell is tagged '{TAG_PREFIX}{name}'.\n"
            f"Tag the plotting cell in the notebook that generates this figure; "
            f"see this file's docstring for the cell contract."
        )
    nb_path, index, source = cells[name]

    archive = os.path.join(results_dir, name + ".json")
    if not os.path.exists(archive):
        raise SystemExit(
            f"figures/results/{name}.json is missing, so there is nothing to "
            f"re-render from.\nRun {os.path.relpath(nb_path, REPO)}; its solve cell "
            f"calls helper.save_results('{name}', ...). Commit the JSON."
        )
    payload = json.loads(open(archive, encoding="utf-8").read())

    ns = _namespace(payload["data"])
    plt.style.use(STYLE)
    try:
        exec(compile(source, f"{nb_path}[cell {index}]", "exec"), ns)  # noqa: S102
    except Exception as exc:  # noqa: BLE001
        raise SystemExit(
            f"{os.path.relpath(nb_path, REPO)} cell {index} "
            f"('{TAG_PREFIX}{name}') failed: {type(exc).__name__}: {exc}\n"
            f"The cell contract is in {os.path.basename(__file__)}'s docstring; "
            f"the usual cause is the cell using a name defined in an earlier cell."
        ) from exc

    fig = ns.get("fig")
    if fig is None or not hasattr(fig, "savefig"):
        raise SystemExit(
            f"{os.path.relpath(nb_path, REPO)} cell {index} "
            f"('{TAG_PREFIX}{name}') left no Figure bound to `fig`.\n"
            f"End the cell with e.g.  fig = plot_{name.replace('-', '_')}(results)"
        )

    os.makedirs(out_dir, exist_ok=True)
    png = os.path.join(out_dir, name + ".png")
    fig.savefig(png, dpi=dpi)
    fig.savefig(os.path.join(out_dir, name + ".pdf"))
    plt.close(fig)
    return png


class _ReadOnlyResults:
    """``helper`` with its two writers disabled.

    A ``figure:`` cell ends with ``save_figure(fig, name)``, which is right
    when the notebook runs it and wrong here: this driver owns where the output
    goes (``--out-dir`` exists so a check can render somewhere harmless), and a
    style re-render must never rewrite the archive it just read from. Everything
    else -- ``as_dataframe``, ``table``, ``column`` -- passes straight through.
    """

    def __getattr__(self, name):
        return getattr(helper, name)

    @staticmethod
    def save_figure(fig, name, **kw):
        return None

    @staticmethod
    def save_results(*a, **kw):
        return None


def _namespace(data):
    """The names a ``figure:`` cell may assume. Fresh per figure; see the contract."""
    import numpy as np
    import pandas as pd

    plumbing = _ReadOnlyResults()

    return {
        "__name__": "__figure_cell__",
        "results": data,
        "np": np,
        "pd": pd,
        "plt": plt,
        "helper": plumbing,
    }


# ---------------------------------------------------------------------------
def main(argv=None) -> int:
    ap = argparse.ArgumentParser(
        description=__doc__.splitlines()[0],
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("names", nargs="*", help="figure names to re-render")
    ap.add_argument("--all", action="store_true", help="re-render every tagged figure")
    ap.add_argument(
        "--list",
        action="store_true",
        help="print the figure names notebooks generate, one per line "
        "(this is what the Makefile consumes)",
    )
    ap.add_argument("--out-dir", default=OUT_DIR)
    ap.add_argument("--dpi", type=float, default=300)
    ap.add_argument("--selftest", action="store_true", help="prove this can FAIL")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    cells = find_figure_cells()

    if args.list:
        for n in sorted(cells):
            print(n)
        return 0

    names = sorted(cells) if args.all else args.names
    if not names:
        ap.error("give a figure name, or --all, or --list")

    for n in names:
        png = render(n, cells=cells, out_dir=args.out_dir, dpi=args.dpi)
        nb = os.path.relpath(cells[n][0], REPO)
        print(f"  {os.path.relpath(png, REPO)}  <- {nb} cell {cells[n][1]}")
    return 0


# ---------------------------------------------------------------------------
def selftest() -> int:
    """Drive `render` with fixtures. A driver that cannot fail proves nothing."""
    import tempfile

    print("Self-test: render_from_notebook.py -- must FAIL on a broken cell.\n")
    ok = True

    def note(good, label):
        nonlocal ok
        ok &= good
        print(f"  {'OK  ' if good else 'FAIL'} {label}")

    def fixture(tmp, source, data=None, name="fixture", tags=None):
        nbdir = os.path.join(tmp, "notebooks", "9-dev")
        os.makedirs(nbdir, exist_ok=True)
        nb = {
            "cells": [
                {
                    "cell_type": "code",
                    "metadata": {"tags": tags if tags is not None else [TAG_PREFIX + name]},
                    "source": source.splitlines(keepends=True),
                    "outputs": [],
                    "execution_count": None,
                }
            ],
            "metadata": {},
            "nbformat": 4,
            "nbformat_minor": 5,
        }
        json.dump(nb, open(os.path.join(nbdir, "F.ipynb"), "w"))
        rdir = os.path.join(tmp, "results")
        os.makedirs(rdir, exist_ok=True)
        if data is not None:
            json.dump(
                {"meta": {}, "data": data},
                open(os.path.join(rdir, name + ".json"), "w"),
            )
        return os.path.join(tmp, "notebooks", "*-dev", "*.ipynb"), rdir

    good = textwrap.dedent(
        """
        def plot_fixture(results):
            fig, ax = plt.subplots(figsize=(3, 2))
            ax.plot(results["x"], results["y"])
            return fig

        fig = plot_fixture(results)
        """
    )

    # 1. The happy path.
    with tempfile.TemporaryDirectory() as tmp:
        g, r = fixture(tmp, good, {"x": [0, 1], "y": [0, 1]})
        out = os.path.join(tmp, "out")
        png = render("fixture", cells=find_figure_cells(g), out_dir=out, results_dir=r)
        note(os.path.exists(png) and os.path.exists(png[:-4] + ".pdf"),
             "a well-formed cell renders a PNG and a PDF")

    # 2. Missing archive -> loud, not a blank figure.
    with tempfile.TemporaryDirectory() as tmp:
        g, r = fixture(tmp, good, None)
        try:
            render("fixture", cells=find_figure_cells(g), out_dir=tmp, results_dir=r)
            note(False, "a missing archive must abort")
        except SystemExit as e:
            note("missing" in str(e), "a missing archive aborts and says so")

    # 3. The cell leans on a name from an earlier cell -- the contract violation
    #    that would otherwise be found only when the style is next changed.
    with tempfile.TemporaryDirectory() as tmp:
        g, r = fixture(tmp, "fig = plot_it(solved_model)\n", {"x": [0]})
        try:
            render("fixture", cells=find_figure_cells(g), out_dir=tmp, results_dir=r)
            note(False, "a cell using an earlier cell's name must abort")
        except SystemExit as e:
            note("NameError" in str(e), "a cell using an undefined name aborts")

    # 4. The cell runs but binds no `fig`.
    with tempfile.TemporaryDirectory() as tmp:
        g, r = fixture(tmp, "x = results['x']\n", {"x": [0]})
        try:
            render("fixture", cells=find_figure_cells(g), out_dir=tmp, results_dir=r)
            note(False, "a cell leaving no `fig` must abort")
        except SystemExit as e:
            note("no Figure" in str(e), "a cell leaving no `fig` aborts")

    # 5. An untagged notebook contributes nothing.
    with tempfile.TemporaryDirectory() as tmp:
        g, _ = fixture(tmp, good, {"x": [0]}, tags=[])
        note(find_figure_cells(g) == {}, "an untagged cell is not picked up")

    print("\n" + ("self-test PASSED" if ok else "self-test FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    raise SystemExit(main())
