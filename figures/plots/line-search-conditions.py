"""Armijo and Goldstein conditions along a search direction.

    figures/plots/line-search-conditions.py  ->  media/figures/line-search-conditions.{png,pdf}

Biegler Figure 3.2 (p. 47), drawn from the course's own test function rather
than reproduced from the book. The lecture handout `globalization.tex` calls
Fig. 3.2 "the single most useful picture in the chapter" and then asks students
to sketch it; this is the figure they sketch onto.

The instance plotted is `notebooks/6-dev/Globalization.ipynb` cell 29 --
steepest descent from x^k = -3 with eta = 1/4 -- and NOT the notebook's first
call (Newton from x^k = -3, alpha_max = 1.5). That first call is the more
obvious choice and it is the wrong one: with a Newton step every alpha in
(0, 1.5] satisfies both conditions, so the picture shows no bracket at all.
The steepest-descent instance is the one that actually draws the interval
[alpha_g, alpha_a] that Fig. 3.2 is about, and it makes the second teaching
point for free -- the accepted interval is only [0.009, 0.036] and
backtracking lands at alpha^k = 0.0225, because an unscaled steepest descent
step (p^k = 51) is far too long.

Greyscale: the three series take colour AND linestyle from the house cycle,
and the accepted band is hatched rather than tinted (see _house.py) -- an
alpha fill alone would grey to mush next to the curve.
"""

import numpy as np
import matplotlib.pyplot as plt

from _house import HATCH_CYCLE, SHADE_ALPHA

# The course test function, verbatim from notebooks/6-dev/Globalization.ipynb
# cell 3. f(x) = 0.5 (x-1)^4 + (x+1)^3 - 10 x^2 + 5 x.
f = lambda x: 0.5 * (x - 1) ** 4 + (x + 1) ** 3 - 10 * x**2 + 5 * x
df = lambda x: 6 - 8 * x - 3 * x**2 + 2 * x**3

XK = -3.0  # iterate
ETA = 0.25  # eta in the Goldstein-Armijo conditions
ALPHA_MAX = 0.045  # backtracking starts here; also the plotted range


def make_figure():
    pk = -df(XK)  # steepest descent: p^k = -grad f(x^k) = 51
    fxk = f(XK)
    slope = df(XK) * pk  # grad f(x^k)^T p^k < 0

    alpha = np.linspace(0.0, ALPHA_MAX, 800)
    fval = f(XK + alpha * pk)
    armijo = fxk + ETA * alpha * slope  # (3.31): rules out steps that are too long
    goldstein = fxk + (1 - ETA) * alpha * slope  # (3.34): rules out steps too short

    # The accepted set is the interval [alpha_g, alpha_a] of Biegler p. 48.
    # alpha = 0 satisfies both conditions with equality and is not a step, so
    # it is excluded before taking the bracket.
    inner = alpha > 0
    accept = (fval <= armijo) & (fval >= goldstein) & inner
    a_lo, a_hi = alpha[accept].min(), alpha[accept].max()

    # Backtracking (Alg. 3.2): start at alpha_max, halve until Armijo holds.
    a_k = ALPHA_MAX
    while f(XK + a_k * pk) > fxk + ETA * a_k * slope:
        a_k *= 0.5

    ylo, yhi = -22.0, 17.0

    fig, ax = plt.subplots(figsize=(5.6, 4.2))

    ax.axvspan(
        a_lo,
        a_hi,
        facecolor="0.55",
        alpha=SHADE_ALPHA,
        hatch=HATCH_CYCLE[0],
        edgecolor=plt.rcParams["hatch.color"],
        linewidth=0.0,
        zorder=0,
    )

    # House cycle taken in order: black solid, blue dashed, orange dash-dot.
    ax.plot(alpha, fval, zorder=3)
    ax.plot(alpha, armijo, zorder=2)
    ax.plot(alpha, goldstein, zorder=2)
    ax.plot(
        [a_k],
        [f(XK + a_k * pk)],
        marker="o",
        markersize=11,
        color="black",
        zorder=4,
        clip_on=False,
    )

    # Direct labelling, not a legend: three lines and a band, all nameable in
    # place. A legend here would be keyed by colour and die in greyscale.
    # White bboxes so a label never has to compete with the hatching.
    box = dict(facecolor="white", edgecolor="none", pad=1.5)
    ax.annotate("Armijo", xy=(0.0130, 8.4), fontsize=13, bbox=box, zorder=5)
    ax.annotate("Goldstein", xy=(0.0022, -16.0), fontsize=13, bbox=box, zorder=5)
    # The curve is labelled on the right, where it is the only thing in that
    # part of the axes; a leader keeps the association unambiguous.
    ax.annotate(
        r"$f(x^k + \alpha^k p^k)$",
        xy=(0.0430, -4.9),
        xytext=(0.0445, 2.0),
        ha="right",
        va="bottom",
        fontsize=13,
        bbox=box,
        zorder=5,
        arrowprops=dict(arrowstyle="-", lw=1.0, color="black"),
    )
    ax.annotate(
        r"accepted $\alpha^k$",
        xy=(0.5 * (a_lo + a_hi), 13.4),
        ha="center",
        va="center",
        fontsize=13,
        bbox=box,
        zorder=5,
    )
    ax.annotate(
        r"$\alpha^k$",
        xy=(a_k + 0.0013, -13.8),
        va="top",
        fontsize=14,
        bbox=box,
        zorder=5,
    )

    # alpha_g and alpha_a name the two ends of the bracket. Kept INSIDE the
    # axes: below them they collide with the x-axis label.
    for xpos, name in ((a_lo, r"$\alpha_g$"), (a_hi, r"$\alpha_a$")):
        ax.annotate(
            name,
            xy=(xpos, -21.0),
            ha="center",
            va="bottom",
            fontsize=14,
            bbox=box,
            zorder=5,
        )

    ax.set_xlabel(r"$\alpha^k$")
    ax.set_ylabel(r"$f(x^k + \alpha^k p^k)$")
    ax.set_xlim(0, ALPHA_MAX)
    ax.set_ylim(ylo, yhi)
    fig.tight_layout()
    return fig
