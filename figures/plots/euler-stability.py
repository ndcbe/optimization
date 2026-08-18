"""Forward vs backward Euler on z' = -z: the step-size stability contrast.

    figures/plots/euler-stability.py  ->  media/figures/euler-stability.{png,pdf}

`notebooks/3-dev/DAE_numeric_integration.ipynb` cells 10 and 12, carried as ONE
two-panel figure. The argument is the contrast between the panels -- same
problem, same two methods, only the step size changed -- so a handout that
printed either panel alone would lose it. h = 1.0 satisfies the explicit
stability bound h < 2/lambda = 2 and both methods track the exact solution;
h = 2.5 violates it and forward Euler oscillates away while backward Euler,
which is unconditionally stable for lambda > 0, does not.

Greyscale: three series, colour AND linestyle from the house cycle, plus a
distinct marker per method (square = forward, circle = backward) so the two
numerical solutions are told apart at a glance even in print. One legend serves
both panels.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy import optimize as opt

LAMBDA = 1.0
Z0 = 1.0

rhs = lambda t, z: -LAMBDA * z
exact = lambda t: np.exp(-LAMBDA * t)


def explicit_euler(h, t_end):
    """z_{i+1} = z_i + h f(t_i, z_i)."""
    n = int(np.ceil(t_end / h))
    t = h * np.arange(n + 1)
    z = np.zeros(n + 1)
    z[0] = Z0
    for i in range(1, n + 1):
        z[i] = z[i - 1] + h * rhs(t[i - 1], z[i - 1])
    return t, z


def implicit_euler(h, t_end):
    """z_{i+1} = z_i + h f(t_{i+1}, z_{i+1}), solved at each step.

    The notebook uses ``fsolve`` seeded with an explicit Euler step. Both parts
    of that are wrong for this script: the explicit seed overshoots badly at
    h = 2.5, and ``fsolve`` on a residual it solves exactly on the first
    iteration prints "not making good progress" on every step, which would put
    a wall of warnings in front of anyone running `make`. A scalar Newton
    solve -- which is what a real implicit integrator does -- converges cleanly
    and gives identical values.
    """
    n = int(np.ceil(t_end / h))
    t = h * np.arange(n + 1)
    z = np.zeros(n + 1)
    z[0] = Z0
    for i in range(1, n + 1):
        residual = lambda zz, zprev=z[i - 1], ti=t[i]: zprev + h * rhs(ti, zz) - zz
        z[i] = opt.newton(residual, z[i - 1], tol=1e-12)
    return t, z


def _panel(ax, h, t_end, ylim, label):
    te, ze = explicit_euler(h, t_end)
    ti, zi = implicit_euler(h, t_end)
    t_fine = np.linspace(0.0, t_end, 201)

    # House cycle in order: black solid (exact), blue dashed (forward),
    # orange dash-dot (backward). Markers added on top of the linestyle, so
    # each series carries THREE colour-free identities.
    ax.plot(t_fine, exact(t_fine), label="exact")
    ax.plot(te, ze, marker="s", label="forward Euler")
    ax.plot(ti, zi, marker="o", label="backward Euler")
    ax.axhline(0.0, color="0.7", linewidth=0.8, linestyle="-", zorder=0)

    ax.set_xlabel("$t$")
    ax.set_xlim(0, t_end)
    ax.set_ylim(*ylim)
    ax.set_title(label, fontsize=15)
    return te, ze, ti, zi


def make_figure():
    fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(9.0, 3.6))

    _panel(ax_l, 1.0, 5.0, (-0.15, 1.15), r"$h = 1.0 < 2/\lambda$: stable")
    _panel(ax_r, 2.5, 10.0, (-4.5, 6.5), r"$h = 2.5 > 2/\lambda$: unstable")

    ax_l.set_ylabel("$z(t)$")

    # One legend for both panels. Direct labelling was tried first and loses
    # here: in the left panel all three curves crowd into t < 2, and the right
    # panel would need the same three names again. The legend is keyed by
    # linestyle and marker as well as colour, so it survives greyscale.
    ax_l.legend(loc="upper right", fontsize=12)

    # The right panel gets the arithmetic instead of a second legend -- that is
    # the number the stability bound is about.
    box = dict(facecolor="white", edgecolor="none", pad=1.5)
    ax_r.annotate(
        r"$|1 - h\lambda| = 1.5 > 1$",
        xy=(9.4, 5.06),
        xytext=(1.3, 4.6),
        fontsize=13,
        bbox=box,
        arrowprops=dict(arrowstyle="->", lw=1.2, color="black"),
    )

    fig.tight_layout()
    return fig
