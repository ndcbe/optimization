r"""The strip-packing optimum, drawn -- the picture the notebook never draws.

    figures/plots/strip-packing-solution.py
        -> media/figures/strip-packing-solution.{png,pdf}

`notebooks/2-dev/Modeling_Disjunctions_Strip_Packing.ipynb` states a problem
whose entire content is geometric -- pack eight rectangles into a strip of
fixed width, minimise the length -- solves it twice, and prints eight pairs of
numbers. It never draws the strip. This figure is that drawing.

Model (Vecchietti & Grossmann, MINLP library problem 121; the notebook's own
source). Rectangle i has x-extent L_i and y-extent W_i, placed at (x_i, y_i):

    min  lt   s.t.  lt >= x_i + L_i,   H_i <= y_i,  y_i <= W - W_i

with one four-term disjunction per pair (i, j), i < j, forbidding overlap:

    [ x_i + L_i <= x_j ] v [ x_j + L_j <= x_i ]
                         v [ y_i + W_i <= y_j ] v [ y_j + W_j <= y_i ]

NO SOLVER. The placement below is the optimum the notebook's committed CBC
output records for the `gdp.bigm` transformation, transcribed and then
re-verified here from first principles: `_check()` re-tests all 28 pairwise
disjunctions, both bounds, and the objective. It is hard-coded precisely so
`make` in this directory needs no MILP binary, per README.md.

Optimal strip length is 11. Total rectangle area is 109 and the strip encloses
11 x 10 = 110, so the packing wastes exactly ONE unit of area -- the single
white square at (3,2). That is worth pointing out in class: the bound
`lt >= area / W = 10.9` is nearly tight here, which is not typical.

The `gdp.hull` transformation in the same notebook reaches lt = 11 too, by a
DIFFERENT placement. Only one is drawn: the lesson is that big-M and the hull
give the same optimal value, not that they give the same optimal solution, and
two near-identical pictures would obscure rather than make that point.

Deliberate choices
------------------
1. Rectangles are hatched with a cycled texture and labelled with their index
   in the centre, so no rectangle is identified by colour alone. With eight
   items this is well past the four-series greyscale limit README.md sets for
   colour, so colour is not used to distinguish them at all.
2. The strip length lt = 11 is marked with a dimension line, since it is the
   objective and the whole reason the picture exists.
3. y is drawn upward and x rightward -- the notebook's docstring calls y a
   position "down the width", but nothing in the model orients it, and a
   conventional axis is easier to read against.
"""

import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

from _house import HATCH_CYCLE, SHADE_ALPHA

STRIP_WIDTH = 10  # W, the fixed width of the strip

# x-extent (the notebook's `rect_length`) and y-extent (`rect_width`).
LENGTH = {0: 4, 1: 3, 2: 2, 3: 2, 4: 3, 5: 3, 6: 4, 7: 4}
WIDTH = {0: 3, 1: 3, 2: 2, 3: 2, 4: 3, 5: 5, 6: 7, 7: 7}

# The CBC optimum recorded in the notebook's committed output, gdp.bigm.
PLACE = {
    0: (7.0, 7.0),
    1: (4.0, 0.0),
    2: (2.0, 0.0),
    3: (0.0, 0.0),
    4: (0.0, 2.0),
    5: (0.0, 5.0),
    6: (7.0, 0.0),
    7: (3.0, 3.0),
}
STRIP_LENGTH = 11.0

# Hatch index per rectangle, hand-assigned so that NO TWO TOUCHING rectangles
# share a texture. Six textures, eight rectangles, twelve adjacent pairs -- a
# plain `i % len(HATCH_CYCLE)` gives 0 and 6 the same hatch across a shared
# edge, and 1 and 7 likewise, which is exactly the seam the figure has to show.
# Verified by _check().
HATCH = {0: 0, 1: 2, 2: 4, 3: 5, 4: 0, 5: 3, 6: 3, 7: 1}


def _check():
    """Re-verify the hard-coded solution rather than trusting the transcription."""
    items = sorted(PLACE)
    for i in items:
        x, y = PLACE[i]
        assert x >= 0 and y >= 0, f"rectangle {i} outside the strip"
        assert y + WIDTH[i] <= STRIP_WIDTH, f"rectangle {i} overflows the width"
        assert x + LENGTH[i] <= STRIP_LENGTH, f"rectangle {i} overflows the length"
    for a, i in enumerate(items):
        for j in items[a + 1:]:
            xi, yi = PLACE[i]
            xj, yj = PLACE[j]
            # Exactly the four-term disjunction; at least one term must hold.
            assert (
                xi + LENGTH[i] <= xj
                or xj + LENGTH[j] <= xi
                or yi + WIDTH[i] <= yj
                or yj + WIDTH[j] <= yi
            ), f"rectangles {i} and {j} overlap"
    assert STRIP_LENGTH == max(PLACE[i][0] + LENGTH[i] for i in items), (
        "the strip is longer than it needs to be: lt is not tight")
    area = sum(LENGTH[i] * WIDTH[i] for i in items)
    assert area == 109 and STRIP_LENGTH * STRIP_WIDTH == 110, "area bookkeeping"
    # No two TOUCHING rectangles may carry the same hatch.
    for a, i in enumerate(items):
        for j in items[a + 1:]:
            xi, yi = PLACE[i]
            xj, yj = PLACE[j]
            touch = (
                (xi + LENGTH[i] == xj or xj + LENGTH[j] == xi)
                and yi < yj + WIDTH[j] and yj < yi + WIDTH[i]
            ) or (
                (yi + WIDTH[i] == yj or yj + WIDTH[j] == yi)
                and xi < xj + LENGTH[j] and xj < xi + LENGTH[i]
            )
            assert not (touch and HATCH[i] == HATCH[j]), (
                f"rectangles {i} and {j} touch and share a hatch")
    return area


def make_figure():
    area = _check()

    fig, ax = plt.subplots(figsize=(6.6, 4.6))

    # The strip itself: fixed width, and long enough to hold the packing.
    ax.add_patch(Rectangle((0, 0), STRIP_LENGTH, STRIP_WIDTH, fill=False,
                           edgecolor="black", linewidth=2.5, zorder=4))

    for i in sorted(PLACE):
        x, y = PLACE[i]
        ax.add_patch(Rectangle(
            (x, y), LENGTH[i], WIDTH[i],
            facecolor="0.55", alpha=SHADE_ALPHA,
            hatch=HATCH_CYCLE[HATCH[i]],
            edgecolor=plt.rcParams["hatch.color"], linewidth=0.0, zorder=2))
        ax.add_patch(Rectangle(
            (x, y), LENGTH[i], WIDTH[i],
            fill=False, edgecolor="black", linewidth=1.6, zorder=3))
        ax.annotate(f"{i}", xy=(x + LENGTH[i] / 2, y + WIDTH[i] / 2),
                    ha="center", va="center", fontsize=15, zorder=5,
                    bbox=dict(facecolor="white", edgecolor="none", pad=1.5))

    # The one wasted unit of area, named so nobody thinks it is a drawing slip.
    ax.annotate("1 unit wasted", xy=(3.5, 2.5), xytext=(-2.2, -1.6),
                ha="left", va="top", fontsize=11, zorder=6,
                arrowprops=dict(arrowstyle="->", linewidth=1.2, color="black"))

    # The objective, marked as a dimension.
    ax.annotate("", xy=(0, STRIP_WIDTH + 0.9), xytext=(STRIP_LENGTH, STRIP_WIDTH + 0.9),
                arrowprops=dict(arrowstyle="<->", linewidth=1.6, color="black"))
    ax.annotate("$lt = 11$  (minimised)", xy=(STRIP_LENGTH / 2, STRIP_WIDTH + 1.3),
                ha="center", va="bottom", fontsize=13,
                bbox=dict(facecolor="white", edgecolor="none", pad=1.0))
    ax.annotate("", xy=(-1.0, 0), xytext=(-1.0, STRIP_WIDTH),
                arrowprops=dict(arrowstyle="<->", linewidth=1.6, color="black"))
    ax.annotate("$W = 10$  (fixed)", xy=(-1.4, STRIP_WIDTH / 2), ha="center",
                va="center", rotation=90, fontsize=13)

    ax.annotate(f"rectangle area $= {area}$;  strip encloses $11 \\times 10 = 110$",
                xy=(STRIP_LENGTH, -2.9), ha="right", va="top", fontsize=11)

    ax.set_xlim(-2.4, 12.4)
    ax.set_ylim(-3.4, 13.4)
    ax.set_aspect("equal", adjustable="box")
    ax.axis("off")
    fig.tight_layout()
    return fig


if __name__ == "__main__":  # a check, not a rendering path
    print(f"strip-packing-solution: feasible and tight, area {_check()}")
