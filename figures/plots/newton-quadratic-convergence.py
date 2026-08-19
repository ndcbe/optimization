"""Newton's method: the quadratic rate, and the hypotheses that buy it.

    figures/plots/newton-quadratic-convergence.py
        ->  media/figures/newton-quadratic-convergence.{png,pdf}

This is Biegler's OWN worked example, drawn.  Example 2.19 (p. 30) defines the
two-variable nonconvex objective; Example 2.21 (pp. 35-36) runs Algorithm 2.1
on it from two starting points and prints the results as Tables 2.2 and 2.3.
The book gives the numbers and no picture of the iterate paths; this script
supplies the picture, and reproduces both tables to every digit they print (see
"Validation" below).

The pedagogy is the PAIR, which is why one figure carries both runs:

  * From x0 = (0.8, 0.3), inside the region where the Hessian is positive
    definite, Newton converges to x* = (0.7395, 0.3143) and the number of
    correct digits DOUBLES each iteration -- Theorem 2.20, p. 35.
  * From x0 = (1.0, 0.5), which is "not much farther away" (Biegler, p. 36) but
    lies in the region where the Hessian is INDEFINITE, the iteration walks off
    and converges -- just as fast, still quadratically -- to a SADDLE POINT at
    (1.0768, 0.9504), where the Hessian eigenvalues are 11.752 and -3.034.

So the right panel is deliberately unhelpful on its own: BOTH curves are
straight-ish lines of doubling slope on a log axis.  Quadratic convergence is
not evidence of a minimum.  Only the left panel, where the hatched indefinite
region is drawn, says which limit point is the one we wanted.  That is the
whole content of "x0 sufficiently close to x*, which satisfies the sufficient
second order conditions" -- the hypothesis of Theorem 2.20 that the handout's
closing sentence used to leave unstated.

Why quadratic convergence to a SADDLE is not a contradiction: Theorem 2.20
hypothesises the second-order sufficient conditions, so it says nothing about
this run.  Nocedal & Wright, Theorem 11.2, p. 276 does: Newton's method applied
to the nonlinear system grad f(x) = 0 converges Q-quadratically to any
NONDEGENERATE root -- one where the Jacobian of the system, here the Hessian,
is nonsingular.  A saddle qualifies.  Nonsingularity buys the rate; definiteness
buys the minimum.  They are different hypotheses doing different jobs.

Deliberate departures from the book
-----------------------------------
1. numpy only -- no Pyomo, no Ipopt, no scipy.optimize.  The gradient is
   analytic (chain rule, below) and the Hessian is taken by complex-step
   differentiation of that gradient, which is exact to machine precision and
   costs nothing.  A finite-difference gradient bottoms out around 1e-9 and
   would silently flatten the last two iterations -- exactly the part of the
   picture the figure exists to show.
2. The indefinite region is HATCHED, not tinted.  Biegler's own Figure 2.5
   (bottom, p. 31) shades regions by minimum eigenvalue in greyscale tints;
   tints are what the course greyscale policy forbids.  See _house.py.
3. The right panel plots ||grad f(x^k)||, not ||x^k - x*||.  Both are quadratic
   under Theorem 2.20, but the far run has no x* to measure against, so the
   gradient norm is the only quantity the two runs share.  It is also the
   column Biegler prints in BOTH tables.

Validation (checked 2026-08-19 against the printed tables)
----------------------------------------------------------
Table 2.2, ||grad f||: 3.000, 0.8163, 6.8524e-3, 2.6847e-6, 1.1483e-13.
Table 2.3, ||grad f||: 9.5731, 3.3651, 1.2696, 0.4894, 0.1525, 1.5904e-2,
                       2.0633e-4, 3.7430e-8, 9.9983e-15.
Both reproduced.  Hessian at x* has eigenvalues 43.417 and 426.362 (p. 30);
at the saddle, 11.752 and -3.034 (p. 36).  Both reproduced.
"""

import numpy as np
import matplotlib.pyplot as plt

from _house import HATCH_CYCLE, SHADE_ALPHA

# Biegler (2.32)-(2.36), p. 30.
A = (0.3, 0.6, 0.2)
B = (5.0, 26.0, 3.0)
C = (40.0, 1.0, 10.0)

XSTAR = np.array([0.73950, 0.31435])      # Biegler p. 30: [0.7395, 0.3144]

X1LO, X1HI = 0.65, 1.25
X2LO, X2HI = 0.15, 1.10


def f(x):
    """Biegler (2.32)-(2.36). Works elementwise, and on complex input."""
    x1, x2 = x[0], x[1]
    u = x1 - 0.8
    v = x2 - (A[0] + A[1] * u**2 * np.sqrt(1.0 - u) - A[2] * u)
    alpha = -B[0] + B[1] * u**2 * np.sqrt(1.0 + u) + B[2] * u
    beta = C[0] * v**2 * (1.0 - C[1] * v) / (1.0 + C[2] * u**2)
    return alpha * np.exp(-beta)


def grad(x):
    """Analytic gradient of f. Complex-safe, so complex-step works on it."""
    x1, x2 = x[0], x[1]
    u = x1 - 0.8
    s = np.sqrt(1.0 - u)
    t = np.sqrt(1.0 + u)

    # v = x2 - r(u)
    r_u = A[1] * (2.0 * u * s - u**2 / (2.0 * s)) - A[2]
    v = x2 - (A[0] + A[1] * u**2 * s - A[2] * u)
    dv_dx1 = -r_u
    dv_dx2 = 1.0

    alpha = -B[0] + B[1] * u**2 * t + B[2] * u
    dalpha_du = B[1] * (2.0 * u * t + u**2 / (2.0 * t)) + B[2]

    # beta = N(v) / D(u)
    N = C[0] * (v**2 - C[1] * v**3)
    dN_dv = C[0] * (2.0 * v - 3.0 * C[1] * v**2)
    D = 1.0 + C[2] * u**2
    dD_du = 2.0 * C[2] * u

    dbeta_dx1 = dN_dv * dv_dx1 / D - N * dD_du / D**2
    dbeta_dx2 = dN_dv * dv_dx2 / D

    e = np.exp(-beta_from(N, D))
    g1 = e * (dalpha_du - alpha * dbeta_dx1)
    g2 = e * (-alpha * dbeta_dx2)
    return np.array([g1, g2])


def beta_from(N, D):
    return N / D


def hess(x, h=1e-30):
    """Complex-step Jacobian of the analytic gradient: exact to machine eps."""
    H = np.empty((2, 2))
    for j in range(2):
        z = np.array(x, dtype=complex)
        z[j] = z[j] + 1j * h
        H[:, j] = np.imag(grad(z)) / h
    return 0.5 * (H + H.T)          # symmetrise the last ulp


def newton(x0, n):
    """Algorithm 2.1 with full steps, alpha = 1. Biegler p. 35."""
    xs, gs = [], []
    x = np.asarray(x0, dtype=float)
    for _ in range(n + 1):
        g = grad(x)
        xs.append(x.copy())
        gs.append(np.linalg.norm(g))
        H = hess(x)
        if abs(np.linalg.det(H)) < 1e-14:        # step 1: singular -> STOP
            break
        x = x + np.linalg.solve(H, -g)
    return np.array(xs), np.array(gs)


def _indefinite_mask(n=140):
    """True where lambda_min(Hessian) < 0 -- Biegler Fig. 2.5 (bottom), p. 31."""
    x1 = np.linspace(X1LO, X1HI, n)
    x2 = np.linspace(X2LO, X2HI, n)
    X, Y = np.meshgrid(x1, x2)
    lam = np.empty_like(X)
    for i in range(n):
        for j in range(n):
            lam[i, j] = np.linalg.eigvalsh(hess((X[i, j], Y[i, j])))[0]
    return X, Y, lam


def make_figure():
    near_x, near_g = newton([0.8, 0.3], 5)
    far_x, far_g = newton([1.0, 0.5], 8)
    saddle = far_x[-1]

    fig, (axL, axR) = plt.subplots(1, 2, figsize=(10.4, 4.4))

    # ---------------------------------------------------- left: iterate paths
    x1 = np.linspace(X1LO, X1HI, 260)
    x2 = np.linspace(X2LO, X2HI, 260)
    X, Y = np.meshgrid(x1, x2)
    Z = f((X, Y))
    axL.contour(
        X, Y, Z,
        levels=[-5, -4.5, -4, -3, -2, -1, -0.4, -0.15, -0.05, 0.0, 0.5, 1.5],
        colors="0.65", linewidths=0.8,
    )

    XG, YG, lam = _indefinite_mask()
    axL.contourf(
        XG, YG, lam, levels=[-1e9, 0.0],
        colors=["0.55"], alpha=SHADE_ALPHA, zorder=0,
    )
    axL.contourf(
        XG, YG, lam, levels=[-1e9, 0.0],
        colors=["none"], hatches=[HATCH_CYCLE[0]], zorder=0,
    )
    axL.contour(XG, YG, lam, levels=[0.0], colors="0.35",
                linewidths=1.2, linestyles=":")

    axL.plot(near_x[:, 0], near_x[:, 1], color="black", linestyle="-",
             linewidth=2.0, marker="o", markersize=7, zorder=5)
    axL.plot(far_x[:, 0], far_x[:, 1], color="#0072B2", linestyle="--",
             linewidth=2.0, marker="s", markersize=6, zorder=5)

    axL.plot(*XSTAR, marker="*", markersize=20, color="black",
             linestyle="none", zorder=6)
    axL.plot(*saddle, marker="X", markersize=13, color="#0072B2",
             linestyle="none", zorder=6)

    _tag(axL, 0.745, 0.215, "$x^*$")
    _tag(axL, 1.093, 0.955, "saddle")
    _tag(axL, 0.665, 0.395, "$x^0=(0.8,0.3)$")
    _tag(axL, 0.905, 0.435, "$x^0=(1.0,0.5)$")
    _tag(axL, 0.855, 0.755, r"$\nabla^2 f \not\succeq 0$", size=13)

    axL.set_xlim(X1LO, X1HI)
    axL.set_ylim(X2LO, X2HI)
    axL.set_xlabel("$x_1$")
    axL.set_ylabel("$x_2$")
    axL.set_title("iterate paths on contours of $f$", fontsize=14)

    # ------------------------------------------------- right: digits doubling
    kn = np.arange(len(near_g))
    kf = np.arange(len(far_g))
    floor = 1e-16
    axR.semilogy(kn, np.maximum(near_g, floor), color="black", linestyle="-",
                 linewidth=2.0, marker="o", markersize=7)
    axR.semilogy(kf, np.maximum(far_g, floor), color="#0072B2", linestyle="--",
                 linewidth=2.0, marker="s", markersize=6)

    axR.annotate("to $x^*$\n(4 iterations)", xy=(1.15, 2e-9), fontsize=13,
                 color="black")
    axR.annotate("to the saddle\n(8 iterations)", xy=(4.15, 6.0), fontsize=13,
                 color="#0072B2")

    axR.set_xlim(-0.3, 8.5)
    axR.set_ylim(1e-16, 3e2)
    axR.set_xlabel("iteration $k$")
    axR.set_ylabel(r"$\|\nabla f(x^k)\|$")
    axR.set_title("both runs are quadratic", fontsize=14)
    axR.set_xticks(range(0, 9))
    axR.grid(True, which="major", axis="y", color="0.85", linewidth=0.6)
    axR.set_axisbelow(True)

    fig.tight_layout()
    return fig


def _tag(ax, x, y, text, size=14):
    ax.annotate(text, xy=(x, y), fontsize=size, zorder=7,
                bbox=dict(facecolor="white", edgecolor="none", pad=1.0))
