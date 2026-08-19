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
    ~ u^(2/3) ~ 1e-11. Three more correct digits, which is the trade the
    handout quotes.

Deliberate departures from the notebook
---------------------------------------
1. GREYSCALE. The notebook draws blue / red / green, all solid, no markers --
   the classic red-green collapse, and on a mono laser printer three identical
   grey curves. Here each series carries colour AND linestyle (from the house
   cycle) AND a distinct marker AND a direct label written onto the curve.
2. THE FITTED SLOPES ARE ON THE AXES. The notebook prints its findings in a
   markdown cell BELOW the plot (cells 27-28). A printed handout has no
   "below", so the slopes are fitted here and annotated in place -- the same
   discipline `euler-error-order.py` follows for the same reason.
3. The measured minima are annotated too, because the handout's answer quotes
   them as predictions and a prediction is worth more next to its measurement.

numpy only, no solver.
"""

import numpy as np
import matplotlib.pyplot as plt

from _house import label_curve

A = 1.0
EXACT = np.exp(A)

# Cell 19's sweep exactly: 10^(-16) to 10^0, four points per decade.
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

    # --- fitted slopes, annotated ON the axes, each beside its own branch ------
    # No legend. Forward and backward differ only in the sign of the step, so on
    # these axes they lie on top of each other: a legend that invited the reader
    # to tell them apart would be inviting a distinction the data does not make.
    # They are labelled jointly, with their markers named in the label itself,
    # which is the colour-free identity README.md requires.
    s_f = fitted_slope(fwd, FIT_TRUNC)
    s_b = fitted_slope(bwd, FIT_TRUNC)
    s_c = fitted_slope(ctr, FIT_TRUNC)
    s_r = fitted_slope(fwd, FIT_ROUND)

    ax.annotate(
        "forward (□) and backward (○) coincide\n"
        rf"slope $= {s_f:.2f}$ and ${s_b:.2f}$",
        xy=(1.5e1, 3e1), fontsize=12, ha="right", va="bottom", color="0.25",
    )
    ax.annotate(rf"central (△), slope $= {s_c:.2f}$",
                xy=(1.5e1, 1e-6), fontsize=12, ha="right", va="top", color="0.25")
    ax.annotate(rf"round-off, slope $= {s_r:.2f}$",
                xy=(1.5e-16, 1e2), fontsize=12, ha="left", va="bottom", color="0.25")

    # --- the two measured valley floors ---------------------------------------
    floors = (
        (fwd, "one-sided floor", (2.0e-15, 4e-10)),
        (ctr, "central floor", (2.0e-14, 1.5e-12)),
    )
    for err, name, xytext in floors:
        i = int(np.argmin(err))
        ax.annotate(
            rf"{name}: $\epsilon = 10^{{{np.log10(EPS[i]):.1f}}}$,"
            rf" error $= 10^{{{np.log10(err[i]):.1f}}}$",
            xy=(EPS[i], err[i]),
            xytext=xytext,
            fontsize=11, color="0.25", ha="left", va="center",
            # White bbox: these two labels sit in the busiest part of the axes
            # and would otherwise be crossed by the central curve.
            bbox=dict(facecolor="white", edgecolor="none", pad=1.5),
            arrowprops=dict(arrowstyle="->", color="0.45", linewidth=1.2,
                            shrinkA=6.0, shrinkB=4.0),
        )

    ax.set_xlabel(r"step size $\epsilon$")
    ax.set_ylabel(r"absolute error in $f'(1)$")
    ax.set_title(r"$f(x) = e^{x}$ at $a = 1$", fontsize=14)
    ax.grid(True, which="major", linestyle=":", linewidth=0.6, color="0.85")
    ax.set_axisbelow(True)

    fig.tight_layout()
    return fig
