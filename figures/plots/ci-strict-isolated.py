"""Positive-side counterexample for the constrained minimizer definitions.

Reuse the canonical unconstrained figure's exact curve and bracketed minima;
show its fine zoom at a readable size in a compact handout panel.
"""
import importlib.util
from pathlib import Path


def make_figure():
    path = Path(__file__).with_name("uo-strict-isolated.py")
    spec = importlib.util.spec_from_file_location("strict_isolated_source", path)
    source = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(source)
    fig = source.make_figure()
    left, ax = fig.axes
    fig.set_layout_engine("none")
    fig.delaxes(left)
    fig.set_size_inches(5, 1.65)
    ax.set_position([.12, .28, .86, .61])
    ax.set_title("")
    ax.set_xlabel("$x$", fontsize=9)
    ax.set_ylabel("$f(x)$", fontsize=9)
    ax.tick_params(labelsize=8)
    ax.yaxis.get_offset_text().set_fontsize(8)
    for text in ax.texts:
        text.set_fontsize(9)
    return fig
