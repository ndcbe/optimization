r"""Why the reactor NLP has two local solutions: a concave cost on a segment.

    figures/plots/reactor-concave-local-minima.py
        -> media/figures/reactor-concave-local-minima.{png,pdf}

This is Biegler, Grossmann & Westerberg, *Systematic Methods of Chemical
Process Design*, Prentice-Hall (1997), **Figure 15.12, p. 510** -- "Cost as a
function of x2 when cost Eqs. (15.5) and (15.6) are used" -- recomputed rather
than traced.

After eliminating z1, z2 and x0, BGW's problem (15.8), p. 511, is

    min  C = 5.5 x1^0.6 + 4.0 x2^0.6 + 5.0 x1 + 5.0 x2
    s.t. 0.8 x1 + (2/3) x2 = 10,   x1, x2 >= 0

One equality in two variables, so the feasible set is a SEGMENT and the whole
problem is a function of x2 alone on 0 <= x2 <= 10/(2/3) = 15:

    x1(x2) = (10 - (2/3) x2) / 0.8

C is concave (each x^0.6 term has second derivative 0.6(-0.4)x^-1.4 < 0), so on
a segment its minima sit at the two ENDPOINTS and its maximum in the interior.
That is the whole content of the lecture's "Is the problem convex? No." answer,
and the reason a local NLP solver returns whichever endpoint it started near.

    x2 = 0        -> x1 = 12.5    C = $87.53/hr   global minimum, reactor I
    x2 = 15       -> x1 = 0       C = $95.31/hr   local  minimum, reactor II
    interior max at x2 = 11.257   C = $99.86/hr

THETA_2 = 2/3, NOT 0.67 (changed 2026-08-21; see the note in
optimization-private/lecture-notes/verification/integer-programming.md).
BGW print the ROUNDED 0.67 in (15.2)-(15.3), p. 510, but their PROSE on p. 509
reads "reactor II has lower conversion (66.7%)" and every number they print
follows from the exact 2/3: the right-hand endpoint x2 = 15 on the axis of
Figure 15.12, the $95.3/hr they label it with, and the $95.5 in the MILP
enumeration on p. 512. At 0.67 the endpoint is 14.925 and C there is 94.88,
which is what this figure used to print WHILE THE LECTURE'S TABLE PRINTED 95.3
-- the figure and the table contradicted each other on the same page. They now
agree. This file, optimization-private/lecture-notes/lectures/
integer-programming.tex and notebooks/1-dev/IP.ipynb all use 2/3; do not change
one without the others.

The one residual gap to BGW is their interior maximum, annotated 11.4 against
the 11.257 that solving dC/dx2 = 0 gives. 2/3 moves us toward their number
(0.67 gave 11.07) and 11.4 is a reading off a hand-drawn axis.

Colour and greyscale (relaid out 2026-08-21). Prof. Dowling, on the previous
version: "text overlaps / move it" -- both endpoint labels sat on top of the
curve -- and "let's use some color". Both labels now sit in the empty band
BELOW the curve, and the three points of interest are colour-coded.

The colour is REDUNDANT, never load-bearing: each point carries a distinct
marker shape as well (filled circle = global min, open square = local min,
filled triangle = interior max), each label is placed next to the point it
names, and the label text repeats the classification in words. Only two
saturated hues appear -- see the palette note below -- and the infeasible region
is hatched rather than tinted.
"""

import numpy as np
import matplotlib.pyplot as plt

from _house import HATCH_CYCLE, SHADE_ALPHA

K1, K2 = 0.8, 2 / 3  # conversions, BGW (15.2)-(15.3), p. 510; see the
# docstring on why K2 is the exact 2/3 and not BGW's printed 0.67
TARGET = 10.0  # kmol/hr of B, BGW p. 509
C1, C2 = 5.5, 4.0  # vessel cost coefficients, (15.5)-(15.6), p. 510
FEED = 5.0  # $/kmol, p. 510

X2_MAX = TARGET / K2  # exactly 15.0

# Okabe-Ito, ordered for luminance spread. See the colour note in the docstring.
# Only TWO saturated hues, and they are the widest-separated pair Okabe-Ito
# offers: blue L* = 46 and orange L* = 70.6, dL* = 24.6. Adding vermillion for a
# third mark FAILED scripts/check_greyscale.py (blue vs vermillion, dL* = 8.2 --
# the same grey on a mono printer), so the two minima and the maximum are told
# apart by MARKER SHAPE, which is the channel that always survives.
CURVE = "#0072B2"   # blue,   L* = 46
GLOBAL = "#000000"  # black,  L* =  0
LOCAL = "#E69F00"   # orange, L* = 70.6
MAXPT = "#000000"   # black,  L* =  0


def cost(x2):
    """C along the mass balance, as a function of x2 alone. BGW (15.8), p. 511."""
    x1 = (TARGET - K2 * x2) / K1
    return C1 * x1**0.6 + C2 * x2**0.6 + FEED * (x1 + x2)


def make_figure():
    fig, ax = plt.subplots(figsize=(6.6, 4.4))

    x2 = np.linspace(0.0, X2_MAX, 601)
    C = cost(x2)

    ax.plot(x2, C, color=CURVE, linestyle="-", zorder=3)

    # Interior maximum, located numerically on a fine grid then refined.
    fine = np.linspace(0.0, X2_MAX, 2_000_001)
    i = int(np.argmax(cost(fine)))
    x2_max, C_max = fine[i], cost(fine[i])

    C_left, C_right = cost(0.0), cost(X2_MAX)

    # Beyond x2 = 10/(2/3) = 15 reactor I would need a negative feed: infeasible.
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

    # The three points of interest. Marker SHAPE is the greyscale-safe channel;
    # colour is redundant on top of it.
    ax.plot([0.0], [C_left], marker="o", markersize=10, color=GLOBAL,
            linestyle="none", zorder=5)
    ax.plot([X2_MAX], [C_right], marker="s", markersize=10, color=LOCAL,
            markerfacecolor="white", markeredgewidth=2.2, linestyle="none",
            zorder=5)
    ax.plot([x2_max], [C_max], marker="^", markersize=11, color=MAXPT,
            markeredgecolor="black", markeredgewidth=0.8, linestyle="none",
            zorder=5)

    # Labels moved OUT of the curve, into the empty band below it.
    ax.annotate(
        f"global min\n\\${C_left:.2f}/hr\nreactor I only\n($x_1 = 12.5$)",
        xy=(0.0, C_left),
        xytext=(1.7, 85.6),
        color=GLOBAL,
        fontsize=12,
        arrowprops=dict(arrowstyle="->", lw=1.2, color=GLOBAL),
    )
    ax.annotate(
        f"local min\n\\${C_right:.2f}/hr\nreactor II only\n($x_2 = {X2_MAX:.0f}$)",
        xy=(X2_MAX, C_right),
        xytext=(8.1, 85.6),
        color=LOCAL,
        fontsize=12,
        arrowprops=dict(arrowstyle="->", lw=1.2, color=LOCAL),
    )
    ax.annotate(
        f"interior maximum, \\${C_max:.2f}/hr\nat $x_2 = {x2_max:.2f}$",
        xy=(x2_max, C_max),
        xytext=(0.6, 101.6),
        color=MAXPT,
        fontsize=12,
        arrowprops=dict(arrowstyle="->", lw=1.2, color=MAXPT),
    )

    ax.set_xlabel("$x_2$, feed to reactor II (kmol/hr)")
    ax.set_ylabel("$C$ (\\$/hr)")
    ax.set_xlim(-0.6, X2_MAX + 1.6)
    ax.set_ylim(84.0, 105.0)

    fig.tight_layout()
    return fig
