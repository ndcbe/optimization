"""Spatial branch and bound on the handout's one-dimensional example.

    figures/plots/spatial-branch-bound.py
        -> media/figures/spatial-branch-bound.{png,pdf}

    min  f(x) = x/4 + sin x     on  -3 <= x <= 6

`notebooks/8-dev/Global-Opt.ipynb` cells 6 and 11, carried as ONE two-panel
figure because the pedagogy is the *before and after*: the same convex
underestimator, first on the whole interval where its bound is useless, then
after one branch where two much smaller gaps close.

Left panel  -- the relaxation. f is nonconvex; the underestimator f^c is the
upper envelope of three affine pieces (the bound sin x >= -1, and the tangents
at the two endpoints), hence convex, and it touches f exactly at the two points
of tangency. Its minimum is the lower bound l = -1.533 at xbar = -2.133; a local
solve started on the right returns u = 0.147 at x = 4.460. The gap is 1.680,
which is nowhere near eps = 0.2.

Right panel -- after branching at the upper-bounding point x^U = 4.460, which
is where the relaxation is worst. Region A keeps the old lower bound and finds
the global solution x* = -1.823, u = -1.424, gap 0.109 < eps. Region B has
l = 0.115 > U = -1.424, so it is FATHOMED on its bound alone -- its optimum is
never located precisely, and that is the whole point of the method.

Deliberate departures from the notebook
---------------------------------------
1. scipy, not Pyomo + HiGHS + Ipopt. `make` in figures/ must not depend on a
   solver binary. The relaxation's minimum is the minimum of a max of affine
   functions, which `minimize_scalar` on a convex function returns exactly; the
   local solves are one-dimensional and bracketed. Every number below was
   checked against the notebook's solver output and agrees to 4 decimals.
2. TWO panels rather than two separate figures, sharing one y axis.
3. Greyscale: f and f^c are told apart by linestyle AND direct labels, not by
   colour. The fathomed region B is hatched, not tinted -- see _house.py.

The handout's printed coefficients (-0.74, -3.11, 1.21, -6.04) are the exact
tangents rounded to two decimals. The exact values are used here so the two
lower pieces meet cleanly.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize_scalar

from _house import HATCH_CYCLE, SHADE_ALPHA

LO, HI = -3.0, 6.0
EPS = 0.2


def f(x):
    return x / 4 + np.sin(x)


def f_prime(x):
    return 0.25 + np.cos(x)


def tangent(x0):
    """Slope and intercept of the tangent line to f at x0."""
    slope = f_prime(x0)
    return slope, f(x0) - slope * x0


# sin x >= -1 gives f(x) >= x/4 - 1; the two endpoint tangents happen to
# underestimate as well, which the notebook verifies on a 200,001 point grid.
PIECES = [(0.25, -1.0), tangent(LO), tangent(HI)]


def f_under(x):
    """Convex underestimator: the upper envelope of the affine pieces."""
    x = np.asarray(x, dtype=float)
    return np.max([m * x + b for m, b in PIECES], axis=0)


def lower_bound(lo, hi):
    """min f^c on [lo, hi]. f^c is convex, so a bounded scalar solve is exact."""
    r = minimize_scalar(lambda x: float(f_under(x)), bounds=(lo, hi), method="bounded",
                        options={"xatol": 1e-10})
    return r.x, r.fun


def local_min(lo, hi, x0):
    """A LOCAL minimum of f in [lo, hi], reached by descending from x0.

    Deliberately local: the upper bound in spatial branch and bound comes from
    a local NLP solve, and the figure would be dishonest if it quietly returned
    the global one. Steepest descent with a shrinking step, then a bracketed
    polish, reproduces what Ipopt does from the same start.
    """
    x, step = x0, 0.5
    for _ in range(200):
        g = f_prime(x)
        x_new = float(np.clip(x - step * g, lo, hi))
        if f(x_new) > f(x):
            step *= 0.5
        else:
            x = x_new
        if abs(g) < 1e-12 or step < 1e-14:
            break
    r = minimize_scalar(f, bounds=(max(lo, x - 0.9), min(hi, x + 0.9)),
                        method="bounded", options={"xatol": 1e-12})
    return r.x, r.fun


def make_figure():
    fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(9.4, 4.0), sharey=True)

    xs = np.linspace(LO, HI, 601)
    branch, u1 = local_min(LO, HI, 5.0)          # x^U = 4.4597, u = 0.1467
    xbar, l1 = lower_bound(LO, HI)               # xbar = -2.1325, l = -1.5331

    # ---------------------------------------------------------------- panel 1
    ax0.plot(xs, f(xs), color="black", ls="-", lw=2.4)
    ax0.plot(xs, f_under(xs), color="#0072B2", ls="--", lw=2.4)

    ax0.plot([LO, HI], [f(LO), f(HI)], marker="o", ls="none",
             mfc="none", mec="black", mew=1.8, ms=9)
    ax0.plot([xbar], [l1], marker="v", ls="none", color="#0072B2", ms=10)
    ax0.plot([branch], [u1], marker="o", ls="none", color="black", ms=10)

    ax0.annotate(r"$f(x)=\dfrac{x}{4}+\sin x$", xy=(-3.15, 1.62), fontsize=13,
                 ha="left", va="center")
    ax0.annotate(r"$f^{c}(x)$", xy=(2.3, -0.98), fontsize=13, color="#0072B2")
    ax0.annotate(rf"$l={l1:.3f}$", xy=(xbar, -1.97), fontsize=12,
                 ha="center", va="center", color="#0072B2")
    ax0.annotate(rf"$u={u1:.3f}$", xy=(branch, u1 - 0.30), fontsize=12,
                 ha="center", va="top")
    ax0.set_title(rf"iteration 1: gap $= {u1 - l1:.3f} \gg \varepsilon$",
                  fontsize=13)

    # ---------------------------------------------------------------- panel 2
    xB, uB = local_min(branch, HI, 5.2)          # 4.4597, 0.1467 -- the corner
    _, lB = lower_bound(branch, HI)              # 0.1149
    xA, uA = local_min(LO, branch, 0.7)          # -1.8235, -1.4241
    _, lA = lower_bound(LO, branch)              # -1.5331

    ax1.plot(xs, f(xs), color="black", ls="-", lw=2.4)
    ax1.plot(xs, f_under(xs), color="#0072B2", ls="--", lw=2.4)
    ax1.axvline(branch, color="0.35", lw=1.4, ls=":")

    # B is discarded on its bound alone: hatched, because a tint alone greys to
    # mush on a mono laser printer.
    ax1.axvspan(branch, HI, facecolor="0.55", alpha=SHADE_ALPHA,
                hatch=HATCH_CYCLE[0], edgecolor=plt.rcParams["hatch.color"],
                linewidth=0.0)

    ax1.plot([xA], [uA], marker="*", ls="none", color="black", ms=18)
    ax1.plot([xB], [uB], marker="o", ls="none", color="black", ms=9)

    ax1.annotate("A", xy=(0.4, 1.60), fontsize=17, ha="center")
    ax1.annotate("B", xy=(5.3, 1.60), fontsize=17, ha="center")
    ax1.annotate(rf"$x^{{*}}={xA:.3f}$, $u={uA:.3f}$",
                 xy=(xA + 0.30, uA - 0.62), fontsize=12, ha="left", va="center")
    ax1.annotate(rf"$l_B={lB:.3f} > U$: fathom",
                 xy=(branch + 0.15, -0.85), fontsize=12, ha="left", va="center")
    ax1.set_title(rf"after one branch: {uA - lA:.3f} and {uB - lB:.3f} $< \varepsilon$",
                  fontsize=13)

    for ax in (ax0, ax1):
        ax.set_xlabel("$x$")
        ax.set_xlim(LO - 0.45, HI + 0.45)
        ax.set_ylim(-2.3, 2.1)
    ax0.set_ylabel("$f(x)$")
    ax0.label_outer()
    ax1.label_outer()

    fig.tight_layout()
    return fig


if __name__ == "__main__":                                    # a self-check
    b, u1 = local_min(LO, HI, 5.0)
    xb, l1 = lower_bound(LO, HI)
    print(f"iter 1  xbar={xb:.4f} l={l1:.4f}  x^U={b:.4f} u={u1:.4f} "
          f"gap={u1 - l1:.4f}")
    xa, ua = local_min(LO, b, 0.7)
    _, la = lower_bound(LO, b)
    print(f"region A  x*={xa:.4f} u={ua:.4f} l={la:.4f} gap={ua - la:.4f}")
    xB, ub = local_min(b, HI, 5.2)
    _, lb = lower_bound(b, HI)
    print(f"region B  x={xB:.4f} u={ub:.4f} l={lb:.4f} gap={ub - lb:.4f}")
    grid = np.linspace(LO, HI, 200_001)
    print(f"max(f_under - f) = {np.max(f_under(grid) - f(grid)):.3e}  (must be <= 0)")
