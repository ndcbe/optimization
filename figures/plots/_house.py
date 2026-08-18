"""Shared helpers for figures/plots/*.py.

Named with a leading underscore so the Makefile's wildcard skips it: this is
not a figure, it is the small amount of house convention that a style file
cannot express.

``dowling.mplstyle`` handles everything rcParams can reach -- colour cycle,
linestyle cycle, fonts, ticks, DPI. Two things it cannot reach live here.

1. HATCH_CYCLE. matplotlib has no ``hatch`` entry in ``axes.prop_cycle`` and no
   rcParam for a hatch sequence, so a shaded region distinguished only by
   ``alpha`` greys to mush on a mono laser printer -- the exact failure the
   course's greyscale policy exists to prevent. Pass ``hatch=HATCH_CYCLE[i]``
   to ``fill_between`` / ``axvspan`` / ``fill`` and the region keeps a
   colour-free identity. ``hatch.color`` and ``hatch.linewidth`` ARE rcParams
   and are set in dowling.mplstyle.

2. Direct labelling. README.md states the preference; ``label_curve`` makes it
   one call instead of five arguments to ``annotate`` at every call site.
"""

from __future__ import annotations

import matplotlib.pyplot as plt

# Ordered coarse-to-fine. Two adjacent entries must not read as the same
# texture at handout size (~3 in wide on the page), so this is not simply
# matplotlib's documented hatch list in its documented order.
HATCH_CYCLE = ("///", "\\\\\\", "...", "xxx", "|||", "---")

# A shaded region is background, not a series: keep the fill pale so the
# hatching, not the tint, is what identifies it.
SHADE_ALPHA = 0.18


def label_curve(ax, x, y, text, *, dx=0.0, dy=0.0, **kwargs):
    """Write ``text`` next to the point (x, y) on ``ax``.

    Direct labelling is preferred over a legend wherever it fits: a legend
    keyed only by colour is the single most common way a figure dies in black
    and white. Colour defaults to the axes' foreground so the label reads in
    greyscale even when the curve it names does not.
    """
    kwargs.setdefault("fontsize", 13)
    kwargs.setdefault("ha", "left")
    kwargs.setdefault("va", "bottom")
    return ax.annotate(text, xy=(x + dx, y + dy), **kwargs)


def shade(ax, x0, x1, *, hatch_index=0, color="0.5", label=None, **kwargs):
    """Shade the vertical band [x0, x1] with a hatch, not just a tint."""
    kwargs.setdefault("alpha", SHADE_ALPHA)
    kwargs.setdefault("edgecolor", plt.rcParams.get("hatch.color", "black"))
    kwargs.setdefault("linewidth", 0.0)
    return ax.axvspan(
        x0,
        x1,
        facecolor=color,
        hatch=HATCH_CYCLE[hatch_index % len(HATCH_CYCLE)],
        label=label,
        **kwargs,
    )
