"""Biegler Example 2.19 -- the candidate point, seen two ways.

    figures/plots/optimality-example-2-19.py
        ->  media/figures/optimality-example-2-19.{png,pdf}

`notebooks/6-dev/Optimality.ipynb` cell 8 (the 3-D surface) carried across for
the course pack, paired with a contour panel the notebook does not have.

    min f(x) = alpha exp(-beta)
        u     = x1 - 0.8
        v     = x2 - (a1 + a2 u^2 (1-u)^(1/2) - a3 u)
        alpha = -b1 + b2 u^2 (1+u)^(1/2) + b3 u
        beta  = c1 v^2 (1 - c2 v) / (1 + c3 u^2)
    a = [0.3, 0.6, 0.2], b = [5, 26, 3], c = [40, 1, 10].

Biegler (2010), Example 2.19 and (2.32)-(2.36), p. 30.  The book reports
x* = [0.7395, 0.3144], f(x*) = -5.0893, grad f(x*) = 0 and

    grad^2 f(x*) = [[77.012, 108.334], [108.334, 392.767]],
    eigenvalues 43.417 and 426.362.

All of that was RE-DERIVED here rather than copied: `_solve()` runs
Nelder-Mead from [0.7, 0.3] and `_hessian()` takes a central finite difference,
and the assertions at the bottom of `make_figure()` fail the render if the
book's numbers are not reproduced.  Re-derivation gives
x* = [0.73950546, 0.31436010], f = -5.089257, H = [[77.0121, 108.3341],
[108.3341, 392.7666]], eigenvalues 43.4174 and 426.3613 -- Biegler's numbers to
every digit he prints.

Deliberate departures from the notebook
---------------------------------------
1. `viridis`, not `cm.coolwarm`.  A diverging map is not monotone in luminance,
   so a coolwarm surface prints as two indistinguishable mid-greys with a light
   band through the middle.  The house rule is a luminance-monotone map.
2. The vertical drop-line at x* is KEPT.  It is a deliberate legibility aid --
   without it a reader cannot tell where on the (x1, x2) floor the marked point
   sits -- and it is the one piece of the notebook figure that most needs to
   survive into print.
3. A SECOND panel is added.  A lone 3-D surface is hard to annotate, and the
   demofigure exists to be written on.  The contour panel shows the same point
   with the curvature information the optimality test actually uses: the two
   eigenvectors of grad^2 f(x*), drawn to a common scale and labelled with
   their eigenvalues, so the class can see the 9.8:1 anisotropy that the
   condition number reports.
4. scipy/numpy only -- no solver, per figures/README.md.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize

A = np.array([0.3, 0.6, 0.2])
B = np.array([5.0, 26.0, 3.0])
C = np.array([40.0, 1.0, 10.0])

# Surface window: the notebook's, which shows the whole basin.
S1LO, S1HI = 0.0, 1.1
S2LO, S2HI = 0.0, 1.0

# Contour window: square, centred on x*, so the eigenvector geometry is honest.
HALF = 0.14


def f(x):
    """Biegler (2.32)-(2.36), p. 30. Vectorised over array arguments."""
    x1, x2 = x[0], x[1]
    u = x1 - 0.8
    v = x2 - (A[0] + A[1] * u**2 * np.sqrt(1.0 - u) - A[2] * u)
    alpha = -B[0] + B[1] * u**2 * np.sqrt(1.0 + u) + B[2] * u
    beta = C[0] * v**2 * (1.0 - C[1] * v) / (1.0 + C[2] * u**2)
    return alpha * np.exp(-beta)


def _solve():
    res = minimize(
        f,
        np.array([0.7, 0.3]),
        method="Nelder-Mead",
        options={"xatol": 1e-12, "fatol": 1e-14, "maxiter": 20000},
    )
    return res.x


def _hessian(x, h=1e-4):
    n = len(x)
    H = np.zeros((n, n))
    for i in range(n):
        for j in range(n):
            ei = np.eye(n)[i] * h
            ej = np.eye(n)[j] * h
            H[i, j] = (
                f(x + ei + ej) - f(x + ei - ej) - f(x - ei + ej) + f(x - ei - ej)
            ) / (4.0 * h * h)
    return 0.5 * (H + H.T)


def _surface_panel(ax, xstar, fstar):
    x1 = np.linspace(S1LO, S1HI, 90)
    x2 = np.linspace(S2LO, S2HI, 90)
    X1, X2 = np.meshgrid(x1, x2)
    F = f((X1, X2))

    ax.plot_surface(
        X1, X2, F, cmap="viridis", linewidth=0, antialiased=True, alpha=0.9
    )

    # The drop-line: without it the marked point floats free of the floor.
    ax.plot(
        [xstar[0], xstar[0]],
        [xstar[1], xstar[1]],
        [F.min(), F.max()],
        color="black",
        linestyle="-",
        linewidth=1.8,
        zorder=10,
    )
    ax.scatter(
        [xstar[0]], [xstar[1]], [fstar],
        s=70, color="black", marker="*", depthshade=False, zorder=11,
    )

    ax.set_xlabel("$x_1$", labelpad=-4)
    ax.set_ylabel("$x_2$", labelpad=-4)
    ax.set_zlabel("$f(x)$", labelpad=-6)
    ax.tick_params(labelsize=9, pad=-1)
    ax.set_title("the whole basin", fontsize=13)


def _contour_panel(ax, xstar, H, eigvals, eigvecs):
    g1 = np.linspace(xstar[0] - HALF, xstar[0] + HALF, 260)
    g2 = np.linspace(xstar[1] - HALF, xstar[1] + HALF, 260)
    X1, X2 = np.meshgrid(g1, g2)
    F = f((X1, X2))

    ax.contour(
        X1, X2, F,
        levels=np.linspace(F.min(), F.min() + 6.0, 13),
        colors="0.55",
        linestyles="solid",
        linewidths=0.8,
    )
    ax.plot(*xstar, marker="*", markersize=18, color="black", linestyle="none")

    # Eigenvectors of grad^2 f(x*), drawn to ONE scale. Each is labelled in
    # place: an arrow gets no linestyle from the cycle, so the label is its
    # only greyscale-safe identity.
    scale = 0.085
    # (linestyle, which end carries the label, label offset)
    decor = (("-", +1, (0.008, 0.008)), ("--", -1, (0.010, -0.020)))
    for k, (lam, (style, end, off)) in enumerate(zip(eigvals, decor)):
        d = eigvecs[:, k] * scale
        ax.plot(
            [xstar[0] - d[0], xstar[0] + d[0]],
            [xstar[1] - d[1], xstar[1] + d[1]],
            color="black",
            linestyle=style,
            linewidth=2.0,
        )
        ax.annotate(
            rf"$\lambda_{{{k + 1}}} = {lam:.1f}$",
            xy=(xstar[0] + end * d[0] + off[0], xstar[1] + end * d[1] + off[1]),
            fontsize=12,
            bbox=dict(facecolor="white", edgecolor="none", pad=1.0),
        )

    ax.annotate(
        r"$\nabla f(x^*) = 0$",
        xy=(xstar[0] - HALF + 0.012, xstar[1] + HALF - 0.028),
        fontsize=12,
        bbox=dict(facecolor="white", edgecolor="none", pad=1.0),
    )
    ax.set_xlim(xstar[0] - HALF, xstar[0] + HALF)
    ax.set_ylim(xstar[1] - HALF, xstar[1] + HALF)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("$x_1$")
    ax.set_ylabel("$x_2$")
    ax.set_title("zoomed on $x^*$", fontsize=13)


def make_figure():
    xstar = _solve()
    fstar = f(xstar)
    H = _hessian(xstar)
    eigvals, eigvecs = np.linalg.eigh(H)

    # Fail the render, not the lecture, if the book's numbers stop reproducing.
    assert np.allclose(xstar, [0.7395, 0.3144], atol=5e-5), xstar
    assert abs(fstar + 5.0893) < 5e-5, fstar
    assert np.allclose(
        H, [[77.012, 108.334], [108.334, 392.767]], atol=2e-3
    ), H
    assert np.allclose(eigvals, [43.417, 426.362], atol=2e-3), eigvals

    fig = plt.figure(figsize=(10.0, 4.3))
    ax3d = fig.add_subplot(1, 2, 1, projection="3d")
    ax2d = fig.add_subplot(1, 2, 2)

    _surface_panel(ax3d, xstar, fstar)
    _contour_panel(ax2d, xstar, H, eigvals, eigvecs)

    fig.tight_layout()
    return fig
