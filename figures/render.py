#!/usr/bin/env python3
r"""Render one figures/plots/<name>.py to <out_dir>/<name>.{png,pdf}.

    python render.py plots/line-search-conditions.py ../media/figures

This is the matplotlib half of the "one source, two outputs" pipeline described
in README.md. It is the exact analogue of the ``pdflatex`` + ``pdftocairo``
rules the Makefile uses for ``tikz/*.tex``:

    tikz/<name>.tex   --Makefile-->  ../media/figures/<name>.{png,svg}
    plots/<name>.py   --render.py->  ../media/figures/<name>.{png,pdf}

Contract for a plot script
--------------------------
Each ``plots/<name>.py`` defines exactly one function::

    def make_figure():
        fig, ax = plt.subplots()
        ...
        return fig

It does NOT call ``plt.style.use`` and does NOT call ``savefig``. This driver
applies ``dowling.mplstyle`` and writes both outputs, so the DPI, the bounding
box and the PNG/PDF pairing are set in ONE place rather than in every script.
A script that saved its own output would be free to drift from the house style,
which is the whole failure mode this directory exists to prevent.

Files whose name starts with ``_`` are shared helpers, not figures; the
Makefile skips them and so should you.

PNG is what the notebooks display (300 dpi, raster, works on Colab and GitHub).
PDF is what the LaTeX handouts ``\includegraphics`` (vector, so it stays sharp
at any print size). Both come from the same call to ``make_figure()``, so the
website and the course pack cannot show different figures.
"""

from __future__ import annotations

import argparse
import importlib.util
import os
import sys

import matplotlib

matplotlib.use("Agg")  # no display; this runs from make and from CI
import matplotlib.pyplot as plt  # noqa: E402

HERE = os.path.dirname(os.path.abspath(__file__))
STYLE = os.path.join(HERE, "dowling.mplstyle")


def load_script(path: str):
    """Import plots/<name>.py by file path, without needing it on sys.path."""
    name = os.path.splitext(os.path.basename(path))[0]
    spec = importlib.util.spec_from_file_location(f"figplot_{name}", path)
    if spec is None or spec.loader is None:
        raise SystemExit(f"render.py: cannot import {path}")
    module = importlib.util.module_from_spec(spec)
    # Shared helpers live alongside as _*.py and are imported normally.
    sys.path.insert(0, os.path.dirname(os.path.abspath(path)))
    try:
        spec.loader.exec_module(module)
    finally:
        sys.path.pop(0)
    return name, module


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("script", help="path to figures/plots/<name>.py")
    ap.add_argument("out_dir", help="directory to write <name>.png and <name>.pdf")
    ap.add_argument(
        "--dpi", type=float, default=300, help="PNG resolution (default: 300)"
    )
    args = ap.parse_args(argv)

    name, module = load_script(args.script)
    if not hasattr(module, "make_figure"):
        raise SystemExit(
            f"render.py: {args.script} defines no make_figure(); see this file's docstring"
        )

    # The style is applied HERE, not in the script, so every figure in the
    # course is guaranteed to have had it applied.
    plt.style.use(STYLE)

    fig = module.make_figure()
    if fig is None:
        raise SystemExit(f"render.py: {args.script}: make_figure() returned None")

    os.makedirs(args.out_dir, exist_ok=True)
    png = os.path.join(args.out_dir, name + ".png")
    pdf = os.path.join(args.out_dir, name + ".pdf")
    fig.savefig(png, dpi=args.dpi)
    fig.savefig(pdf)
    plt.close(fig)
    print(f"  {png}\n  {pdf}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
