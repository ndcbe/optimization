r"""Finite-difference error: the truncation / round-off valley.

    figures/plots/finite-difference-error.py
        ->  media/figures/finite-difference-error.{png,pdf}

`notebooks/6-dev/Math-Primer-2.ipynb` cell 25, the last of three cells that
build the same picture up one curve at a time (cell 21 forward, cell 23 adds
backward, cell 25 adds central). Building up is a notebook virtue and a handout
redundancy, so only the finished picture is carried here.

    f(x) = exp(x),  f'(x) = exp(x),  evaluated at a = 1
    epsilon swept over 10^-16 ... 10^0, four points per decade  (cell 19)

Each curve is |approx - exp(1)|, so the plotted quantity is an ABSOLUTE error
and the reference value f'(1) = e is order 1 -- absolute and relative error
therefore agree to within a factor of 3 here, which is why the handout's
order-of-magnitude statements can be read straight off these axes.

What the picture has to show, because the handout's Part 6 asserts all of it:

  * right-hand branch, TRUNCATION dominant: slope +1 for the one-sided
    formulas, +2 for central.  (Biegler-free; Nocedal & Wright (8.4) p. 195 and
    p. 197 give exactly these two orders.)
  * left-hand branch, ROUND-OFF dominant: slope -1 for all three, because the
    cancellation error eps_mach/epsilon is divided by the same step regardless
    of the formula. Noisy, not smooth -- round-off is not a smooth function of
    the step, and the handout says so.
  * the valley: forward and backward bottom out near epsilon = sqrt(u) ~ 1e-8
    at an error ~ 1e-8; central bottoms out near u^(1/3) ~ 1e-5.3 at an error
    ~ u^(2/3) ~ 1e-10.7 predicted; measured on this grid, 1e-5.5 at 1e-10.5.
    Between two and three more correct digits, which is the trade the
    handout quotes.

Deliberate departures from the notebook
---------------------------------------
1. GREYSCALE. The notebook draws blue / red / green, all solid, no markers --
   the classic red-green collapse, and on a mono laser printer three identical
   grey curves. Here each series carries colour AND linestyle (from the house
   cycle) AND a distinct marker AND a direct label written onto the curve.
2. NO SLOPES OR MINIMA ON THE AXES (changed 2026-10-06). They used to be
   annotated in place; Lecture 13 now asks students to read them off the
   figure (Alex: "instead have an activity asking about this"), so printing
   them would give the activity away. fitted_slope() is kept so the answers
   can be re-checked: forward/backward +1.00, central +2.00, round-off -0.92;
   minima at epsilon = 10^-8.0 (one-sided) and 10^-5.5 (central).

numpy only, no solver.
"""

import numpy as np
import matplotlib.pyplot as plt

from _house import label_curve

A = 1.0
EXACT = np.exp(A)

# The notebook's sweep (6-dev cell 19, `np.arange(-16, 1, 0.25)`) cut off at
# 10^0: 10^(-16) to 10^0, four points per decade. The notebook runs on to
# 10^0.75; every minimum and fitted slope below lies inside this range.
EPS = np.power(10.0, np.arange(-16, 0.25, 0.25))

# Where each branch is fitted. The truncation branch has to stay well away from
# the valley floor (round-off already contributes at 1e-6 for the one-sided
# formulas) and away from epsilon ~ 1, where the higher Taylor terms the O()
# hides are no longer negligible.
FIT_TRUNC = (1e-4, 1e-1)
FIT_ROUND = (1e-16, 1e-11)


def errors():
    f = np.exp
    fa = f(A)
    fwd = np.abs((f(A + EPS) - fa) / EPS - EXACT)
    bwd = np.abs((fa - f(A - EPS)) / EPS - EXACT)
    ctr = np.abs((f(A + EPS) - f(A - EPS)) / (2 * EPS) - EXACT)
    return fwd, bwd, ctr


def fitted_slope(err, window):
    """Least-squares slope of log(err) against log(eps) over `window`."""
    lo, hi = window
    m = (EPS >= lo) & (EPS <= hi) & (err > 0)
    return np.polyfit(np.log10(EPS[m]), np.log10(err[m]), 1)[0]


def make_figure():
    fwd, bwd, ctr = errors()

    fig, ax = plt.subplots(figsize=(7.6, 5.4))

    series = [
        (fwd, "s", "forward"),
        (bwd, "o", "backward"),
        (ctr, "^", "central"),
    ]
    for err, marker, name in series:
        ax.loglog(EPS, err, marker=marker, markevery=3, markersize=6,
                  linewidth=2.0, label=name)

    ax.set_xlim(1e-17, 3e1)
    ax.set_ylim(1e-13, 1e4)

    # --- curve names only, ON the axes (2026-10-06) ----------------------------
    # The slopes and the measured valley floors are the ANSWERS to the handout's
    # observation activity (Lecture 13, "Read the figure"), so the figure no
    # longer prints them; fitted_slope() and the measured minima stay in this
    # file as the check on those answers (printed by `python3 -c` in the log).
    # No legend: forward and backward coincide on these axes, so they are
    # labelled jointly with their markers named in the label itself, which is
    # the colour-free identity README.md requires.
    ax.annotate("forward (□) and backward (○) coincide",
                xy=(1.5e1, 3e1), fontsize=12, ha="right", va="bottom", color="0.25")
    ax.annotate("central (△)",
                xy=(1.5e1, 1e-6), fontsize=12, ha="right", va="top", color="0.25")

    ax.set_xlabel(r"step size $\epsilon$")
    ax.set_ylabel(r"absolute error in $f'(1)$")
    ax.set_title(r"$f(x) = e^{x}$ at $a = 1$", fontsize=14)
    ax.grid(True, which="major", linestyle=":", linewidth=0.6, color="0.85")
    ax.set_axisbelow(True)

    fig.tight_layout()
    return fig
