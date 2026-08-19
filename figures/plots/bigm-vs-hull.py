r"""Big-M versus convex hull: the two relaxations of one two-term disjunction.

    figures/plots/bigm-vs-hull.py  ->  media/figures/bigm-vs-hull.{png,pdf}

The reactor-pressure disjunction of Biegler, Grossmann & Westerberg (1997),
Sec. 15.8, p. 519, drawn in the (y_1, P) plane -- the picture the lecture
argues for in words and never shows.

    [ Y_1 ;  P <= 10 ; -P <= -5  ]   v   [ Y_2 ;  P <= 30 ; -P <= -20 ]

Big-M, BGW (15.44), p. 520, with M_1 = M_2 = 20 (the smallest valid pair on
0 <= P <= 30, derived in the lecture):

    P <= 10 + 20(1 - y_1)      -P <= -5  + 20(1 - y_1)
    P <= 30 + 20(1 - y_2)      -P <= -20 + 20(1 - y_2)      y_1 + y_2 = 1

Convex hull, BGW (15.46), p. 521:

    P = P_1 + P_2   P_1 <= 10 y_1   P_2 <= 30 y_2
                   -P_1 <= -5 y_1  -P_2 <= -20 y_2         y_1 + y_2 = 1

Substituting y_2 = 1 - y_1 and writing t = y_1, both reduce to an interval of
P for each t in [0,1], so the whole comparison fits on one pair of axes:

    hull   20 - 15t <= P <= 30 - 20t                    (exact, a quadrilateral)
    big-M  max(20t - 15, 20 - 20t) <= P <= 30 - 20t     (a pentagon)

The upper boundaries COINCIDE; the entire difference is the lower boundary,
where big-M drops to a kink. Solving 20t - 15 = 20 - 20t gives t = 7/8 and
P = 5/2 -- the witness the lecture quotes. So the big-M relaxation projects
onto 2.5 <= P <= 30, strictly larger than the hull's 5 <= P <= 30, and the
hull's projection is exactly conv([5,10] u [20,30]) as the construction
promises.

At the integer points t = 0 and t = 1 the two agree exactly, [20,30] and
[5,10]: both relaxations are correct, and tightness is only ever a statement
about the fractional interior. That is the point of the figure.

No solver. Every boundary above is a line the docstring derives by hand, and
the two vertices are checked against exact fractions in the test at the bottom.

Deliberate choices
------------------
1. Two panels, not one overlay. The big-M region CONTAINS the hull region, so
   an overlay hides the smaller one; side by side, with the hull outline
   repeated as a dashed line on the big-M panel, shows the containment without
   either region being buried.
2. HATCHING, not alpha. Two tinted regions on one axes produce a third tint
   where they overlap, which means nothing in black and white. See _house.py.
3. The gap region -- in big-M but not in the hull -- is hatched a THIRD way and
   labelled in place, because it is the actual subject of the figure.
"""

import numpy as np
import matplotlib.pyplot as plt

from _house import HATCH_CYCLE, SHADE_ALPHA

# Disjunct data, BGW (15.42): [5,10] for reactor 1, [20,30] for reactor 2.
PL1, PU1 = 5.0, 10.0
PL2, PU2 = 20.0, 30.0

# Smallest valid big-M on 0 <= P <= 30, one M per term (lecture derivation):
#   M_1 >= max(max(P-10), max(-P+5))  = max(20, 5)  = 20
#   M_2 >= max(max(P-30), max(-P+20)) = max( 0, 20) = 20
M1 = M2 = 20.0

T = np.linspace(0.0, 1.0, 601)


def hull_bounds(t):
    """P = P_1 + P_2 with P_1 in [5t, 10t] and P_2 in [20(1-t), 30(1-t)]."""
    lo = PL1 * t + PL2 * (1.0 - t)  # 20 - 15t
    hi = PU1 * t + PU2 * (1.0 - t)  # 30 - 20t
    return lo, hi


def bigm_bounds(t):
    """The four big-M rows with y_1 = t, y_2 = 1 - t."""
    lo = np.maximum(PL1 - M1 * (1.0 - t), PL2 - M2 * t)  # max(20t-15, 20-20t)
    hi = np.minimum(PU1 + M1 * (1.0 - t), PU2 + M2 * t)  # min(30-20t, 30+20t)
    return lo, hi


# The big-M kink: 20t - 15 = 20 - 20t.
T_KINK = 7.0 / 8.0
P_KINK = PL1 - M1 * (1.0 - T_KINK)  # = 2.5


def _disjuncts(ax, label=True):
    """The two disjuncts themselves: the only points the MODEL ever allows.

    Drawn as thick solid bars at y_1 = 1 and y_1 = 0. Every linestyle here is
    stated explicitly: dowling.mplstyle cycles linestyle in lockstep with
    colour, so an unstated linestyle silently becomes dashed.
    """
    for t, lo, hi in ((1.0, PL1, PU1), (0.0, PL2, PU2)):
        ax.plot([t, t], [lo, hi], color="black", linestyle="-", linewidth=6.0,
                solid_capstyle="butt", zorder=6)
    if not label:  # named once, on the left panel; the bars are identical
        return
    ax.annotate("$y_1 = 0$:\nreactor 2", xy=(0.07, 25.0), ha="left", va="center",
                fontsize=12, zorder=8,
                bbox=dict(facecolor="white", edgecolor="none", pad=1.0))
    ax.annotate("$y_1 = 1$:\nreactor 1", xy=(0.93, 15.0), ha="right", va="bottom",
                fontsize=12, zorder=8,
                bbox=dict(facecolor="white", edgecolor="none", pad=1.0))


def _frame(ax, title):
    ax.set_xlim(-0.06, 1.06)
    ax.set_ylim(-1.0, 34.0)
    ax.set_xlabel("$y_1$  (relaxed to $[0,1]$)")
    ax.set_title(title, fontsize=15)
    ax.set_xticks([0.0, 0.25, 0.5, 0.75, 1.0])
    ax.set_yticks([0, 5, 10, 20, 30])


def make_figure():
    hlo, hhi = hull_bounds(T)
    blo, bhi = bigm_bounds(T)

    fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.4), sharey=True)

    # ---- Left: big-M -------------------------------------------------------
    ax = axes[0]
    ax.fill_between(T, blo, bhi, facecolor="0.55", alpha=SHADE_ALPHA,
                    hatch=HATCH_CYCLE[0],
                    edgecolor=plt.rcParams["hatch.color"], linewidth=0.0)
    ax.plot(T, blo, color="black", linestyle="-", linewidth=2.2)
    ax.plot(T, bhi, color="black", linestyle="-", linewidth=2.2)
    # The hull outline, repeated so the containment is visible on this panel.
    ax.plot(T, hlo, color="#0072B2", linestyle="--", linewidth=2.4, zorder=5)
    ax.plot(T_KINK, P_KINK, marker="o", markersize=10, color="black",
            linestyle="none", zorder=8)
    ax.annotate("$y_1 = \\frac{7}{8}$,  $P = 2.5$", xy=(T_KINK, P_KINK),
                xytext=(0.50, 0.4), ha="center", va="bottom", fontsize=12, zorder=8,
                arrowprops=dict(arrowstyle="->", linewidth=1.2, color="black"))
    ax.annotate("hull\nboundary", xy=(0.55, 11.75), xytext=(0.30, 4.0),
                ha="center", va="bottom", fontsize=12, color="#0072B2", zorder=8,
                arrowprops=dict(arrowstyle="->", linewidth=1.2, color="#0072B2"))
    _disjuncts(ax)
    _frame(ax, "big-$M$   ($M_1 = M_2 = 20$)")
    ax.set_ylabel("pressure $P$  [atm]")

    # ---- Right: convex hull ------------------------------------------------
    ax = axes[1]
    # The part big-M keeps and the hull cuts away, hatched separately.
    ax.fill_between(T, blo, hlo, where=(hlo > blo), facecolor="0.55",
                    alpha=SHADE_ALPHA, hatch=HATCH_CYCLE[3],
                    edgecolor=plt.rcParams["hatch.color"], linewidth=0.0)
    ax.fill_between(T, hlo, hhi, facecolor="0.55", alpha=SHADE_ALPHA,
                    hatch=HATCH_CYCLE[1],
                    edgecolor=plt.rcParams["hatch.color"], linewidth=0.0)
    ax.plot(T, hlo, color="black", linestyle="-", linewidth=2.2)
    ax.plot(T, hhi, color="black", linestyle="-", linewidth=2.2)
    ax.plot(T, blo, color="#0072B2", linestyle="--", linewidth=2.4, zorder=5)
    ax.annotate("cut away\nby the hull", xy=(0.72, 7.2), xytext=(0.34, 1.0),
                ha="center", va="bottom", fontsize=12, zorder=8,
                arrowprops=dict(arrowstyle="->", linewidth=1.2, color="black"))
    ax.annotate("big-$M$\nboundary", xy=(0.92, 2.4), xytext=(0.84, 14.0),
                ha="center", va="bottom", fontsize=12, color="#0072B2", zorder=8,
                arrowprops=dict(arrowstyle="->", linewidth=1.2, color="#0072B2"))
    _disjuncts(ax, label=False)
    _frame(ax, "convex hull (disaggregated)")

    fig.tight_layout()
    return fig


if __name__ == "__main__":  # a check, not a rendering path
    from fractions import Fraction as F

    t = F(7, 8)
    assert max(20 * t - 15, 20 - 20 * t) == F(5, 2), "big-M kink is not P = 5/2"
    assert 20 - 15 * t == F(55, 8), "hull lower boundary wrong at t = 7/8"
    for t in (F(0), F(1)):  # the relaxations must AGREE at the integer points
        assert (max(20 * t - 15, 20 - 20 * t), min(30 - 20 * t, 30 + 20 * t)) == (
            20 - 15 * t, 30 - 20 * t)
    print("bigm-vs-hull: geometry checks pass")
