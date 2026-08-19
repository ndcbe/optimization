"""The cusp where LICQ fails -- Biegler (4.44), Figure 4.8, book p. 77.

    figures/plots/licq-cusp.py  ->  media/figures/licq-cusp.{png,pdf}

`notebooks/7-dev/Constraint-Qualifications.ipynb` cell 12, redrawn. The
constraint set was re-derived from the lecture text, not copied:

    min  f(x) = x1                     grad f  = [1, 0]^T
    s.t. g1(x) = x2 - x1^3  <= 0       grad g1 = [-3 x1^2,  1]^T
         g2(x) = -x1^3 - x2 <= 0       grad g2 = [-3 x1^2, -1]^T

Together the two constraints give -x1^3 <= x2 <= x1^3, which is satisfiable
only when x1^3 >= -x1^3, i.e. x1 >= 0. The feasible set is therefore the
cusp-shaped sliver to the RIGHT of the origin, and x* = (0,0).

At x* both gradients collapse to [0, 1]^T and [0, -1]^T -- ANTIPARALLEL, so
the active Jacobian [[0,1],[0,-1]] has rank 1 and LICQ (Biegler Def. 4.12,
p. 77; Nocedal & Wright Def. 12.4, printed p. 320) fails. That single fact is
what this picture has to show, which is why the two arrows are drawn and named
rather than merely the region being shaded.

Deliberate departures from the notebook
---------------------------------------
1. GREYSCALE FIX, the case the figure inventory singled out. The notebook
   draws both half-regions in blue and red, both linestyle="-", both
   alpha=0.5; the overlap is purple, and all three tints collapse to the same
   grey on a mono laser printer -- so the notebook's own discussion question
   ("which region is feasible?") becomes unanswerable in print. Here each
   half-region carries a distinct HATCH from HATCH_CYCLE, so the feasible
   overlap is identified by crossed hatching, not by a third tint. The two
   boundary curves also carry distinct linestyles.
2. The gradients at the cusp are drawn AND labelled in place. An arrow gets no
   linestyle from the colour cycle, so colour is all it has -- see
   figures/README.md and plots/kkt-geometry.py.
3. Zoomed to |x1| <= 1.2. The notebook plots [-3, 3], where x1^3 = +-27 and the
   cusp -- the entire point of the example -- is a hairline at the origin.
"""

import numpy as np
import matplotlib.pyplot as plt

from _house import HATCH_CYCLE, SHADE_ALPHA

XLO, XHI = -1.2, 1.2
YLO, YHI = -1.35, 1.35

# One scale for both gradient arrows. They are unit vectors of equal length in
# opposite directions; drawing them at equal length is the whole point.
SCALE = 0.62


def _arrow(ax, base, vec, label, *, color, offset, ha="left", scale=SCALE):
    """One gradient, drawn AND named. The name is the greyscale-safe identity."""
    tip = np.asarray(base) + scale * np.asarray(vec)
    ax.arrow(
        base[0],
        base[1],
        scale * vec[0],
        scale * vec[1],
        width=0.022,
        length_includes_head=True,
        color=color,
        zorder=6,
    )
    ax.annotate(
        label,
        xy=(tip[0] + offset[0], tip[1] + offset[1]),
        fontsize=13,
        ha=ha,
        va="center",
        zorder=7,
        bbox=dict(facecolor="white", edgecolor="none", pad=1.0),
    )


def make_figure():
    x1 = np.linspace(XLO, XHI, 401)
    upper = x1**3          # x2 = x1^3,  boundary of g1 <= 0
    lower = -(x1**3)       # x2 = -x1^3, boundary of g2 <= 0

    fig, ax = plt.subplots(figsize=(5.2, 5.0))

    # g1 <= 0 is everything BELOW x2 = x1^3.
    ax.fill_between(
        x1,
        YLO,
        np.clip(upper, YLO, YHI),
        facecolor="0.55",
        alpha=SHADE_ALPHA,
        hatch=HATCH_CYCLE[0],
        edgecolor=plt.rcParams["hatch.color"],
        linewidth=0.0,
        zorder=0,
    )
    # g2 <= 0 is everything ABOVE x2 = -x1^3.
    ax.fill_between(
        x1,
        np.clip(lower, YLO, YHI),
        YHI,
        facecolor="0.55",
        alpha=SHADE_ALPHA,
        hatch=HATCH_CYCLE[1],
        edgecolor=plt.rcParams["hatch.color"],
        linewidth=0.0,
        zorder=0,
    )

    ax.plot(x1, upper, color="#0072B2", linestyle="-", linewidth=2.5, zorder=3)
    ax.plot(x1, lower, color="#E69F00", linestyle="--", linewidth=2.5, zorder=3)

    ax.annotate(
        "$g_1(x) = x_2 - x_1^3 \\leq 0$",
        xy=(-1.15, -1.22),
        fontsize=12,
        bbox=dict(facecolor="white", edgecolor="none", pad=1.0),
        zorder=4,
    )
    ax.annotate(
        "$g_2(x) = -x_1^3 - x_2 \\leq 0$",
        xy=(-1.15, 1.10),
        fontsize=12,
        bbox=dict(facecolor="white", edgecolor="none", pad=1.0),
        zorder=4,
    )

    # The feasible set: the doubly hatched sliver, x1 >= 0, between the curves.
    ax.annotate(
        "feasible set\n(both hatches)",
        xy=(0.55, 0.02),
        xytext=(0.86, -0.72),
        fontsize=12,
        ha="center",
        va="center",
        arrowprops=dict(arrowstyle="->", color="black", linewidth=1.2),
        bbox=dict(facecolor="white", edgecolor="none", pad=1.0),
        zorder=9,
    )

    # x* = (0,0): the cusp.
    ax.plot([0.0], [0.0], marker="*", markersize=18, color="black", linestyle="none", zorder=8)
    ax.annotate(
        "$x^*$",
        xy=(0.09, -0.17),
        fontsize=14,
        bbox=dict(facecolor="white", edgecolor="none", pad=1.0),
        zorder=8,
    )

    # The two active gradients at x*. grad g1 = [0,1]^T, grad g2 = [0,-1]^T:
    # antiparallel, so the active Jacobian has rank 1 and LICQ fails.
    _arrow(
        ax,
        (0.0, 0.0),
        (0.0, 1.0),
        "$\\nabla g_1(x^*)$\n$= (0,\\, 1)^{T}$",
        color="#0072B2",
        offset=(-0.10, -0.02),
        ha="right",
    )
    _arrow(
        ax,
        (0.0, 0.0),
        (0.0, -1.0),
        "$\\nabla g_2(x^*)$\n$= (0,\\, -1)^{T}$",
        color="#E69F00",
        offset=(-0.10, 0.02),
        ha="right",
    )

    ax.axhline(0.0, color="0.75", linewidth=0.8, zorder=1)
    ax.axvline(0.0, color="0.75", linewidth=0.8, zorder=1)
    ax.set_xlim(XLO, XHI)
    ax.set_ylim(YLO, YHI)
    ax.set_xlabel("$x_1$")
    ax.set_ylabel("$x_2$")
    ax.set_aspect("equal", adjustable="box")

    fig.tight_layout()
    return fig
