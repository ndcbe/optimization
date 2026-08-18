"""KKT geometry, built up in three takes.

    figures/plots/kkt-geometry.py  ->  media/figures/kkt-geometry.{png,pdf}

`notebooks/7-dev/Local-Optimality.ipynb` cells 14, 16 and 18, carried as ONE
three-panel figure. The pedagogy is the accumulation -- unconstrained minimum,
then one inequality, then an equality as well -- so the panels only mean
something next to each other. Students should be labelling the multipliers on
the arrows during the demo, which is what the handout's annotation space is for.

    min  f(x) = x1^2 - 4 x1 + 1.5 x2^2 - 7 x2 + x1 x2 + 9 - ln x1 - ln x2
    s.t. g(x) = 4 - x1 x2 <= 0
         h(x) = 2 x1 - x2  = 0

Deliberate departures from the notebook
---------------------------------------
1. scipy, not Pyomo + Ipopt. The notebook is teaching Pyomo; this script is
   producing a picture, and making `make` in figures/ depend on a solver binary
   would be a bad trade. The three solutions agree to 6 figures.
2. The view is zoomed to [0.4, 4] x [0.4, 5]. The notebook plots [-1, 10],
   where all three solutions and every arrow crowd into one corner.
3. GREYSCALE FIX, the one the inventory called out. The notebook draws the
   three gradients as arrows distinguished by colour alone -- black, blue, red,
   identical width -- which is exactly the failure mode the course policy
   forbids. Here each arrow is also labelled in place with the symbol it
   carries, so the picture survives a mono laser printer.
4. The infeasible side of g is hatched, not tinted. See _house.py.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

from _house import HATCH_CYCLE, SHADE_ALPHA

X1LO, X1HI = 0.4, 4.0
X2LO, X2HI = 0.4, 5.0

# One scale for every gradient arrow. Uniform on purpose: the notebook's own
# discussion cell asks why the arrows are not the same length, and the answer
# (the multipliers, not the drawing) only works if the drawing is honest.
SCALE = 0.35


def f(x):
    return (
        x[0] ** 2
        - 4 * x[0]
        + 1.5 * x[1] ** 2
        - 7 * x[1]
        + x[0] * x[1]
        + 9
        - np.log(x[0])
        - np.log(x[1])
    )


def grad_f(x):
    return np.array(
        [2 * x[0] - 4 + x[1] - 1 / x[0], 3 * x[1] - 7 + x[0] - 1 / x[1]]
    )


# g(x) = 4 - x1 x2 <= 0
grad_g = lambda x: np.array([-x[1], -x[0]])
# h(x) = 2 x1 - x2 = 0
grad_h = lambda x: np.array([2.0, -1.0])


def solve(with_g, with_h):
    cons = []
    if with_g:
        cons.append({"type": "ineq", "fun": lambda x: x[0] * x[1] - 4})
    if with_h:
        cons.append({"type": "eq", "fun": lambda x: 2 * x[0] - x[1]})
    res = minimize(f, [10.0, 10.0], bounds=[(1e-3, 100)] * 2, constraints=cons)
    return res.x


def _contours(ax):
    x1 = np.linspace(X1LO, X1HI, 200)
    x2 = np.linspace(X2LO, X2HI, 200)
    X, Y = np.meshgrid(x1, x2)
    Z = f((X, Y))
    ax.contour(X, Y, Z, levels=np.arange(-1.0, 12.0, 1.0), colors="0.65", linewidths=0.8)
    ax.set_xlim(X1LO, X1HI)
    ax.set_ylim(X2LO, X2HI)
    ax.set_xlabel("$x_1$")
    ax.set_aspect("equal", adjustable="box")


def _arrow(ax, base, vec, label, scale=1.0, offset=(0.1, 0.1), **kwargs):
    """One gradient, drawn AND named. The name is the greyscale-safe identity."""
    kwargs.setdefault("width", 0.045)
    kwargs.setdefault("length_includes_head", True)
    tip = base + scale * vec
    ax.arrow(base[0], base[1], scale * vec[0], scale * vec[1], zorder=5, **kwargs)
    ax.annotate(
        label,
        xy=(tip[0] + offset[0], tip[1] + offset[1]),
        fontsize=14,
        zorder=6,
        bbox=dict(facecolor="white", edgecolor="none", pad=1.0),
    )


def make_figure():
    x_a = solve(False, False)
    x_b = solve(True, False)
    x_c = solve(True, True)

    fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.9))
    x1 = np.linspace(X1LO, X1HI, 200)

    for ax in axes:
        _contours(ax)
    axes[0].set_ylabel("$x_2$")

    # --- Take 1: unconstrained -------------------------------------------
    axes[0].plot(*x_a, marker="*", markersize=18, color="black", linestyle="none")
    axes[0].set_title("1. unconstrained", fontsize=14)

    # --- Takes 2 and 3 share the inequality -------------------------------
    for ax in axes[1:]:
        g_boundary = 4.0 / x1
        ax.plot(x1, g_boundary, color="#0072B2", linestyle="--", linewidth=2.5)
        # Infeasible side: x1 x2 < 4, i.e. below the hyperbola.
        ax.fill_between(
            x1,
            X2LO,
            np.minimum(g_boundary, X2HI),
            facecolor="0.55",
            alpha=SHADE_ALPHA,
            hatch=HATCH_CYCLE[0],
            edgecolor=plt.rcParams["hatch.color"],
            linewidth=0.0,
            zorder=0,
        )
        ax.annotate(
            "$g(x) \\leq 0$",
            xy=(2.55, 0.72),
            fontsize=13,
            bbox=dict(facecolor="white", edgecolor="none", pad=1.0),
        )

    axes[1].plot(*x_b, marker="*", markersize=18, color="black", linestyle="none")
    axes[1].set_title(r"2. add $g(x) \leq 0$", fontsize=14)
    _arrow(axes[1], x_b, grad_f(x_b), r"$\nabla f$", scale=SCALE, color="black")
    _arrow(
        axes[1],
        x_b,
        grad_g(x_b),
        r"$\nabla g$",
        scale=SCALE,
        color="#0072B2",
        offset=(-0.15, -0.42),
    )

    # --- Take 3: the full KKT picture -------------------------------------
    axes[2].plot(x1, 2 * x1, color="#E69F00", linestyle="-.", linewidth=2.5)
    axes[2].annotate(
        "$h(x) = 0$",
        xy=(2.52, 4.52),
        fontsize=13,
        bbox=dict(facecolor="white", edgecolor="none", pad=1.0),
    )
    axes[2].plot(*x_c, marker="*", markersize=18, color="black", linestyle="none")
    axes[2].set_title(r"3. add $h(x) = 0$", fontsize=14)
    _arrow(axes[2], x_c, grad_f(x_c), r"$\nabla f$", scale=SCALE, color="black")
    _arrow(
        axes[2],
        x_c,
        grad_g(x_c),
        r"$\nabla g$",
        scale=SCALE,
        color="#0072B2",
        offset=(0.16, -0.40),
    )
    _arrow(
        axes[2],
        x_c,
        grad_h(x_c),
        r"$\nabla h$",
        scale=SCALE,
        color="#E69F00",
        offset=(0.08, -0.32),
    )

    fig.tight_layout()
    return fig
