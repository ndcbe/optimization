r"""Why the reactor NLP has two local solutions: a concave cost on a segment.

    figures/plots/reactor-concave-local-minima.py
        -> media/figures/reactor-concave-local-minima.{png,pdf}

This is Biegler, Grossmann & Westerberg, *Systematic Methods of Chemical
Process Design*, Prentice-Hall (1997), **Figure 15.12, p. 510** -- "Cost as a
function of x2 when cost Eqs. (15.5) and (15.6) are used" -- recomputed rather
than traced.

After eliminating z1, z2 and x0, BGW's problem (15.8), p. 511, is

    min  C = 5.5 x1^0.6 + 4.0 x2^0.6 + 5.0 x1 + 5.0 x2
    s.t. 0.8 x1 + 0.67 x2 = 10,   x1, x2 >= 0

One equality in two variables, so the feasible set is a SEGMENT and the whole
problem is a function of x2 alone on 0 <= x2 <= 10/0.67 = 14.925:

    x1(x2) = (10 - 0.67 x2) / 0.8

C is concave (each x^0.6 term has second derivative 0.6(-0.4)x^-1.4 < 0), so on
a segment its minima sit at the two ENDPOINTS and its maximum in the interior.
That is the whole content of the lecture's "Is the problem convex? No." answer,
and the reason a local NLP solver returns whichever endpoint it started near.

    x2 = 0        -> x1 = 12.5    C = $87.53/hr   global minimum, reactor I
    x2 = 14.925   -> x1 = 0       C = $94.88/hr   local  minimum, reactor II
    interior max                  C = $99.53/hr

NOTE, and it is why this figure is recomputed rather than traced: BGW annotate
their Figure 15.12 with a maximum at x2 = 11.4 and a right-hand endpoint of
95.3 at x2 = 15. Both are readings of the ROUNDED endpoint x2 = 15 rather than
the exact 14.925 the constraint gives. Solving dC/dx2 = 0 with the printed
data puts the maximum at x2 = 11.07, and C(14.925) = 94.88, not 95.3. The
labels here carry the recomputed values; the discrepancy is recorded in
optimization-private/lecture-notes/verification/integer-programming.md.

Greyscale: ONE curve, so colour carries nothing. Every feature -- the two
endpoint minima, the interior maximum, the two reactor regimes -- is identified
by a marker and a direct text label, and the infeasible region beyond the
endpoint is hatched rather than tinted.
"""

import numpy as np
import matplotlib.pyplot as plt

from _house import HATCH_CYCLE, SHADE_ALPHA

K1, K2 = 0.8, 0.67  # conversions, BGW (15.2)-(15.3), p. 510
TARGET = 10.0  # kmol/hr of B, BGW p. 509
C1, C2 = 5.5, 4.0  # vessel cost coefficients, (15.5)-(15.6), p. 510
FEED = 5.0  # $/kmol, p. 510

X2_MAX = TARGET / K2  # 14.9254


def cost(x2):
    """C along the mass balance, as a function of x2 alone. BGW (15.8), p. 511."""
    x1 = (TARGET - K2 * x2) / K1
    return C1 * x1**0.6 + C2 * x2**0.6 + FEED * (x1 + x2)


def make_figure():
    fig, ax = plt.subplots(figsize=(6.6, 4.4))

    x2 = np.linspace(0.0, X2_MAX, 601)
    C = cost(x2)

    ax.plot(x2, C, color="black", linestyle="-", zorder=3)

    # Interior maximum, located numerically on a fine grid then refined.
    fine = np.linspace(0.0, X2_MAX, 2_000_001)
    i = int(np.argmax(cost(fine)))
    x2_max, C_max = fine[i], cost(fine[i])

    C_left, C_right = cost(0.0), cost(X2_MAX)

    # Beyond x2 = 10/0.67 reactor I would need a negative feed: infeasible.
    ax.axvspan(
        X2_MAX,
        X2_MAX + 1.6,
        facecolor="0.55",
        alpha=SHADE_ALPHA,
        hatch=HATCH_CYCLE[0],
        edgecolor=plt.rcParams["hatch.color"],
        linewidth=0.0,
        zorder=0,
    )
    ax.annotate(
        "infeasible\n($x_1 < 0$)",
        xy=(X2_MAX + 0.8, 91.5),
        ha="center",
        va="center",
        fontsize=11,
        rotation=90,
    )

    # The three stationary points of interest.
    for xx, yy, mk in ((0.0, C_left, "o"), (X2_MAX, C_right, "o"), (x2_max, C_max, "^")):
        ax.plot([xx], [yy], marker=mk, markersize=9, color="black", zorder=5)

    ax.annotate(
        f"global min\n\\${C_left:.2f}/hr\nreactor I only\n($x_1 = 12.5$)",
        xy=(0.0, C_left),
        xytext=(1.2, 89.4),
        fontsize=12,
        arrowprops=dict(arrowstyle="->", lw=1.1, color="black"),
    )
    ax.annotate(
        f"local min\n\\${C_right:.2f}/hr\nreactor II only\n($x_2 = 14.93$)",
        xy=(X2_MAX, C_right),
        xytext=(8.6, 88.6),
        ha="right",
        fontsize=12,
        arrowprops=dict(arrowstyle="->", lw=1.1, color="black"),
    )
    ax.annotate(
        f"interior maximum, \\${C_max:.2f}/hr\nat $x_2 = {x2_max:.2f}$",
        xy=(x2_max, C_max),
        xytext=(2.4, 101.2),
        fontsize=12,
        arrowprops=dict(arrowstyle="->", lw=1.1, color="black"),
    )

    ax.set_xlabel("$x_2$, feed to reactor II (kmol/hr)")
    ax.set_ylabel("$C$ (\\$/hr)")
    ax.set_xlim(-0.6, X2_MAX + 1.6)
    ax.set_ylim(85.0, 104.0)

    fig.tight_layout()
    return fig
