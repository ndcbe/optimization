"""Levenberg--Marquardt arc and Powell dogleg path inside a trust region.

    figures/plots/trust-region-steps.py  ->  media/figures/trust-region-steps.{png,pdf}

Biegler Figure 3.4 (p. 55) -- "Levenburg-Marquardt (dotted lines) and Powell
dogleg (dashed lines) steps for different trust regions" -- computed from an
explicit model problem rather than sketched.

WHY COMPUTED AND NOT DRAWN. The lecture handout `globalization.tex` previously
carried a hand-placed TikZ reconstruction of this figure, marked
`TODO: verify diagram`, whose coordinates were chosen by eye. The 2018 scan
(Lecture8_TrustRegion, p. 3) contains no drawing at all -- only the margin note
"Add Figure 3.4" above a blank half page. A sketch cannot be checked; this can.
Every point annotated below is computed from B and g by the book's own
formulas, and the assertions in make_figure() fail the render if the instance
ever stops illustrating the case it is supposed to illustrate.

THE INSTANCE.

    m(p) = g^T p + 1/2 p^T B p,      B = diag(1, 10),   g = (-2, -6)^T

chosen so that

  * B is positive definite, which is what the dogleg method requires (Biegler
    p. 55: "For the dogleg method, we assume that B^k is positive definite");
  * kappa(B) = 10, so the Newton step p^N = (2, 0.6) sits 22 degrees off the
    horizontal while the steepest descent direction -g = (2, 6) sits at 72
    degrees. The 50-degree gap is what gives the dogleg a visible bend; with a
    well-conditioned B the two legs are nearly collinear and the picture
    teaches nothing;
  * ||p^C|| = 0.695 < Delta = 1.5 < ||p^N|| = 2.088, i.e. the plotted radius
    falls in the THIRD of the three cases on Biegler p. 55 -- the only one in
    which the convex-combination weight (our \\cvxwt, his eta) is used at all.
    Here it comes out theta = 0.643 (dogleg_step returns 0.6434961).

WHAT THE PICTURE HAS TO SHOW, and does:

  * the L-M arc runs from p^N (delta = 0) back toward the origin along the
    steepest descent direction as delta grows -- Biegler's sentence "as Delta
    vanishes, p(lambda) points to the steepest descent direction", read as a
    curve;
  * the dogleg replaces that arc by two straight segments through p^C, and
    crosses the trust region boundary at a point NEAR BUT NOT ON the arc. That
    gap is the whole "exact solution vs approximate solution" row of the
    take-away table in the handout;
  * p^C, the minimizer of m along -g, lies strictly inside the circle, which is
    exactly why the third case fires rather than the second.

Greyscale: the arc and the dogleg differ by linestyle (dotted vs dashed) and
are directly labelled; the three named points differ by marker shape; the model
contours and the trust regions are drawn in plain greys. Nothing in the figure
is keyed by hue alone.
"""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

# --- the model problem ------------------------------------------------------
B = np.array([[1.0, 0.0], [0.0, 10.0]])
G = np.array([-2.0, -6.0])  # g = grad f(x^k)
DELTA = 1.5  # the plotted trust region radius
RINGS = (0.7, 1.5, 2.1)  # "for different trust regions"


def model(p1, p2):
    """m(p) = g^T p + 1/2 p^T B p, vectorised over a grid."""
    return (
        G[0] * p1
        + G[1] * p2
        + 0.5 * (B[0, 0] * p1**2 + 2 * B[0, 1] * p1 * p2 + B[1, 1] * p2**2)
    )


def lm_step(delta):
    """p(delta) = -(B + delta I)^{-1} g.  Biegler (3.50), p. 54."""
    return -np.linalg.solve(B + delta * np.eye(2), G)


def cauchy_step():
    """p^C, first branch of Biegler (3.52), p. 54.  B is PD here, so the
    denominator g^T B g is positive and the second branch never fires."""
    denom = G @ B @ G
    assert denom > 0, "second Cauchy branch would fire; B is meant to be PD"
    return -(G @ G) / denom * G


def dogleg_step(delta):
    """Biegler p. 55, all three cases, with the convex-combination weight."""
    pN = -np.linalg.solve(B, G)
    pC = cauchy_step()
    if delta >= np.linalg.norm(pN):
        return pN, None
    if delta <= np.linalg.norm(pC):
        return delta * pC / np.linalg.norm(pC), None
    d = pN - pC
    a = d @ d
    b = d @ pC
    c = np.linalg.norm(pC) ** 2 - delta**2
    theta = (-b + np.sqrt(b**2 - a * c)) / a
    return theta * pN + (1 - theta) * pC, theta


def make_figure():
    pN = -np.linalg.solve(B, G)
    pC = cauchy_step()
    pD, theta = dogleg_step(DELTA)

    # --- assertions: the instance must stay in the interesting case ---------
    assert np.linalg.norm(pC) < DELTA < np.linalg.norm(pN), "wrong dogleg case"
    assert theta is not None and 0 < theta < 1, "weight is not a convex weight"
    assert abs(np.linalg.norm(pD) - DELTA) < 1e-10, "dogleg step is off the boundary"

    # The L-M arc: delta = 0 is the Newton step, delta large is a vanishing
    # step along -g.  Log-spaced so the fast-moving end is resolved.
    deltas = np.concatenate([[0.0], np.logspace(-2, 2.6, 500)])
    arc = np.array([lm_step(d) for d in deltas])

    xlo, xhi, ylo, yhi = -0.35, 2.65, -0.30, 1.85
    fig, ax = plt.subplots(figsize=(6.4, 3.9))

    # Model contours: background only, one light grey, no colour key.
    gx, gy = np.meshgrid(np.linspace(xlo, xhi, 400), np.linspace(ylo, yhi, 400))
    ax.contour(gx, gy, model(gx, gy), levels=8, colors="0.86", linewidths=0.7, zorder=0)

    # Trust regions "for different trust regions"; the plotted Delta is solid.
    for r in RINGS:
        ax.add_patch(
            plt.Circle(
                (0, 0),
                r,
                fill=False,
                edgecolor="0.40" if r == DELTA else "0.72",
                linestyle="-" if r == DELTA else (0, (1, 3)),
                linewidth=1.4 if r == DELTA else 0.9,
                zorder=1,
            )
        )

    # The steepest descent ray, for orientation: p^C lies on it.
    ray = 1.95 * (-G) / np.linalg.norm(G)
    ax.plot([0, ray[0]], [0, ray[1]], color="0.55", lw=0.9, ls=(0, (5, 4)), zorder=1)

    # House cycle in order: black solid, blue dashed. Linestyles set explicitly
    # so the two paths differ in black and white as well as in colour.
    cyc = plt.rcParams["axes.prop_cycle"].by_key()["color"]
    ax.plot(arc[:, 0], arc[:, 1], color=cyc[0], ls=":", lw=2.4, zorder=3)
    ax.plot(
        [0, pC[0], pN[0]],
        [0, pC[1], pN[1]],
        color=cyc[1],
        ls="--",
        lw=2.0,
        zorder=3,
    )

    # The named points, distinguished by marker shape, not colour.
    ax.plot([pN[0]], [pN[1]], marker="o", ms=8, color="black", zorder=5)
    ax.plot([pC[0]], [pC[1]], marker="s", ms=7, color="black", zorder=5)
    ax.plot([pD[0]], [pD[1]], marker="D", ms=7, color="black", zorder=5)
    ax.plot([0], [0], marker="o", ms=4, color="black", zorder=5)

    box = dict(facecolor="white", edgecolor="none", pad=1.5)
    ax.annotate(r"$x^k$", xy=(-0.28, -0.13), fontsize=13, bbox=box, zorder=6)
    ax.annotate(
        r"$p^N$", xy=(pN[0] + 0.09, pN[1] - 0.04), fontsize=13, bbox=box, zorder=6
    )
    ax.annotate(
        r"$p^C$", xy=(pC[0] - 0.34, pC[1] - 0.05), fontsize=13, bbox=box, zorder=6
    )
    ax.annotate(
        r"$p^k$",
        xy=(pD[0] + 0.02, pD[1] - 0.36),
        ha="center",
        fontsize=13,
        bbox=box,
        zorder=6,
    )
    ax.annotate(
        r"$p(\delta)$ arc",
        xy=(0.667, 0.500),          # p(delta) at delta = 2, an exact arc point
        xytext=(0.30, 1.22),
        fontsize=12,
        color=cyc[0],
        bbox=box,
        zorder=6,
        arrowprops=dict(arrowstyle="-", lw=0.9, color=cyc[0]),
    )
    ax.annotate(
        "dogleg path",
        xy=(1.05, 0.653),
        xytext=(1.30, 1.22),
        fontsize=12,
        color=cyc[1],
        bbox=box,
        zorder=6,
        arrowprops=dict(arrowstyle="-", lw=0.9, color=cyc[1]),
    )
    ax.annotate(
        r"$-\nabla f(x^k)$",
        xy=(ray[0] + 0.07, ray[1] - 0.16),
        ha="left",
        va="top",
        fontsize=12,
        bbox=box,
        zorder=6,
    )
    ax.annotate(
        r"$\Delta$",
        xy=(DELTA * np.cos(-0.12) + 0.05, DELTA * np.sin(-0.12)),
        va="center",
        fontsize=13,
        bbox=box,
        zorder=6,
    )

    ax.set_xlabel(r"$p_1$")
    ax.set_ylabel(r"$p_2$")
    ax.set_xlim(xlo, xhi)
    ax.set_ylim(ylo, yhi)
    ax.set_aspect("equal")
    fig.tight_layout()
    return fig
