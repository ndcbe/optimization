"""Four convergence rates on one log axis: Newton, BFGS, SR1, steepest descent.

    figures/plots/quasi-newton-rates.py  ->  media/figures/quasi-newton-rates.{png,pdf}

`claude/figure_inventory.md` names "a BFGS-vs-Newton convergence-rate plot" as
the obvious missing figure for `notebooks/6-dev/Quasi-Newton-Methods`, which has
zero plotting cells. This is that figure, widened to all four methods the
lecture discusses, because the point is the *separation* of the rates:

    Newton            quadratic   -- digits double
    BFGS              superlinear -- steepens, but only near the end
    steepest descent  linear      -- a straight line on a log axis, and flat
    SR1 (line search) breaks down -- see below

Test problem: Rosenbrock, from x0 = (-1.2, 1). This is deliberately Nocedal &
Wright's OWN comparison problem -- their function (2.22), and the table on
printed p. 141 reports steepest descent / BFGS / Newton taking 5264 / 34 / 21
iterations to drive the gradient norm to 1e-5 from this exact starting point,
with Wolfe line searches. Measured at THAT criterion this script reproduces
21 (Newton) and 34 (BFGS) -- exactly the printed table, not merely close.
The counts to this script's own GTOL = 1e-11 are 22 and 37, and quoting those
against the book's 1e-5 figures compares two different stopping rules; an
earlier version of this docstring did, and called the exact reproduction
"agreement to within what the line-search details can move".

    f(x) = 100 (x2 - x1^2)^2 + (1 - x1)^2,   x* = (1, 1),  f(x*) = 0

THE SR1 CURVE STOPS, AND THAT IS THE RESULT
-------------------------------------------
SR1 is run here in the same line-search framework as the others, with NO
safeguard, and it terminates after three steps. Traced:

    k=2:  (y - B s)^T s = -0.070      <- denominator goes NEGATIVE
          the rank-one update therefore SUBTRACTS curvature, and
          eig(B) becomes (-642, +6)   <- B is now indefinite
    k=3:  grad f^T p = +0.26 > 0      <- the step is an ASCENT direction
          and a line search on an ascent direction has nothing to find.

That is exactly Nocedal & Wright's account, printed p. 144: SR1 "does not
guarantee that the updated matrix maintains positive definiteness," and printed
p. 145: the denominator "can vanish," which is why SR1 belongs in a trust region
rather than a line search. It is also, independently, why the course notebook's
SR1 cell fails. The curve is drawn to its last honest point and the failure is
annotated in place; it is NOT patched, and no safeguard is applied, because the
breakdown is the teaching content.

Newton's own guard is minimal and disclosed: where the exact Hessian is not
positive definite the code applies the lecture's own Levenberg-Marquardt shift
(Biegler (3.2)/p. 41-42 region), which is what Algorithm 3.1 assumes anyway.

No solver dependency: numpy only.
"""

import numpy as np
import matplotlib.pyplot as plt

from _house import label_curve

X0 = np.array([-1.2, 1.0])
NMAX = 60
GTOL = 1e-11


def f(x):
    return 100.0 * (x[1] - x[0] ** 2) ** 2 + (1.0 - x[0]) ** 2


def grad(x):
    return np.array(
        [-400.0 * x[0] * (x[1] - x[0] ** 2) - 2.0 * (1.0 - x[0]),
         200.0 * (x[1] - x[0] ** 2)]
    )


def hess(x):
    return np.array(
        [[-400.0 * (x[1] - 3.0 * x[0] ** 2) + 2.0, -400.0 * x[0]],
         [-400.0 * x[0], 200.0]]
    )


def wolfe_step(x, p, c1=1e-4, c2=0.9):
    """Backtrack from alpha = 1 until both Wolfe conditions hold.

    The Wolfe conditions are not decoration here: Nocedal & Wright, printed
    p. 138, (6.8), show they are what guarantees the BFGS curvature condition
    s^T y > 0, and therefore what keeps B^k positive definite.
    """
    a, f0, slope = 1.0, f(x), grad(x) @ p
    for _ in range(60):
        xn = x + a * p
        if f(xn) <= f0 + c1 * a * slope and grad(xn) @ p >= c2 * slope:
            return a
        a *= 0.5
    return a


def run(kind):
    """Return (gradient-norm history, note) for one method."""
    x, B, note = X0.astype(float).copy(), np.eye(2), None
    hist = [np.linalg.norm(grad(x))]

    for k in range(NMAX):
        g = grad(x)

        if kind == "newton":
            Bk = hess(x)
            lo = np.linalg.eigvalsh(Bk).min()
            if lo < 1e-8:                      # Levenberg-Marquardt shift
                Bk = Bk + (1e-8 - lo + 1e-3) * np.eye(2)
            p = np.linalg.solve(Bk, -g)
        elif kind == "steepest":
            p = -g
        else:
            p = np.linalg.solve(B, -g)
            if g @ p >= 0.0:                   # SR1 only, and only once
                note = f"ascent at k={k}"
                break

        s = wolfe_step(x, p) * p
        xn = x + s
        y = grad(xn) - g

        if kind == "bfgs":
            if s @ y > 1e-12:                  # skip test, Biegler (3.19)
                B = B + np.outer(y, y) / (s @ y) \
                      - np.outer(B @ s, s @ B) / (s @ B @ s)
        elif kind == "sr1":
            r = y - B @ s
            if abs(r @ s) < 1e-14:             # unsafeguarded: report, do not fix
                note = f"denominator ~ 0 at k={k}"
                break
            B = B + np.outer(r, r) / (r @ s)

        x = xn
        hist.append(max(np.linalg.norm(grad(x)), 1e-16))
        if hist[-1] < GTOL:
            break

    return np.array(hist), note


def make_figure():
    newton, _ = run("newton")
    bfgs, _ = run("bfgs")
    sr1, sr1_note = run("sr1")
    steepest, _ = run("steepest")

    fig, ax = plt.subplots(figsize=(7.0, 4.6))

    # Order matters: the prop_cycle pairs colour with linestyle, and the first
    # four entries are the greyscale-safe set. Every series is labelled in
    # place -- there is no legend, so colour is never load-bearing.
    for series in (newton, bfgs, steepest, sr1):
        ax.semilogy(np.arange(len(series)), series, linewidth=2.6)

    label_curve(ax, 15.5, 3e-6, "Newton\n(quadratic)", fontsize=13,
                ha="right", va="center")
    label_curve(ax, 37.0, 3e-6, "BFGS\n(superlinear)", fontsize=13,
                ha="left", va="center")
    label_curve(ax, 47.0, 1.2e1, "steepest descent (linear)", fontsize=13,
                ha="center", va="bottom")

    # SR1 stops. Mark the stop, name the mechanism, do not hide it.
    ax.plot(len(sr1) - 1, sr1[-1], marker="X", markersize=13,
            color=ax.lines[3].get_color(), linestyle="none", zorder=6)
    ax.annotate(
        "SR1 breaks down: $B^k$ indefinite,\nso $p^k$ is an ascent direction",
        xy=(len(sr1) - 1, sr1[-1] * 1.6),
        xytext=(6.5, 5.0e5),
        fontsize=12.5,
        ha="left",
        va="top",
        bbox=dict(facecolor="white", edgecolor="none", pad=1.5),
        arrowprops=dict(arrowstyle="->", linewidth=1.4, color="0.25"),
    )

    ax.set_xlabel("iteration $k$")
    ax.set_ylabel(r"$\|\nabla f(x^k)\|$")
    ax.set_xlim(0, NMAX)
    ax.set_ylim(1e-12, 1e6)
    ax.set_yticks([1e-12, 1e-9, 1e-6, 1e-3, 1e0, 1e3])

    fig.tight_layout()

    assert sr1_note is not None, "SR1 was expected to break down; it did not"
    return fig
