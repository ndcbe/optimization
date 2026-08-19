"""Why a nonlinear equality makes the feasible set nonconvex.

    figures/plots/nonconvex-equality-circle.py
        -> media/figures/nonconvex-equality-circle.{png,pdf}

Restores a picture the course LOST in typesetting. Prof. Dowling's Fall 2018
handwritten notes, Lecture 16 page 1, pose the activity

    "If h(x) is nonlinear, (5.1) is nonconvex. Why?  (circle example)"

and the parenthetical is a pointer to a drawing. The typeset lecture
(`lecture-notes/lectures/newton-equality-nlp.tex`) kept the question and the
verbal answer but dropped the picture. This is that picture.

Book source: Biegler (2010), *Nonlinear Programming*, p. 91, Section 5.1:

    "if the constraints h(x) = 0 are linear, then (5.1) is a convex problem if
     and only if f(x) is convex. On the other hand ... nonlinear equality
     constraints imply nonconvex problems even if f(x) is convex."

That sentence is a CONTRAST, so the figure is two panels. One panel showing
only the circle proves the feasible set is not convex but leaves the student
without the control case, and the control case is where the "if and only if"
lives.

    left   h(x) = x1^2 + x2^2 - 1 = 0     nonlinear -> a curve
    right  h(x) = x1 + x2 - 1     = 0     linear    -> a line

Both panels draw the SAME construction: two feasible points, the chord between
them, and the chord's midpoint. On the left the midpoint sits strictly inside
the circle and is infeasible; on the right it lies on the line and is feasible.
Convexity of a set is exactly the statement that this construction never
escapes, so one construction drawn twice is the whole proof.

Design notes
------------
1. The objective is deliberately absent. The claim under test is about the
   FEASIBLE SET only -- Biegler's sentence holds "even if f(x) is convex" --
   and drawing contours of some f would invite the reader to think the
   nonconvexity came from the objective. This is the one figure in the lecture
   where an empty background is the correct background.
2. The infeasible interior of the circle is NOT hatched. Hatching marks the
   infeasible side of an INEQUALITY (see kkt-geometry.py); here *everything*
   off the curve is infeasible, so shading a region would misrepresent an
   equality as an inequality. The feasible set is the curve, drawn heavy;
   that is the entire message.
3. Direct labels only, no legend. Four annotations per panel: the constraint,
   the two endpoints, and the midpoint verdict.
4. Greyscale: the two panels are distinguished by position and title, the
   chord by its dashed linestyle against the solid constraint, and every
   element carries a text label. Nothing is keyed by colour alone.

The endpoint angles are chosen (not fitted) so the chord is long enough for
the midpoint gap to be visible at handout size while both endpoints stay in
the upper half plane where the labels have room.
"""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt

# Endpoints on the unit circle, in radians. 150 deg and 30 deg: symmetric
# about the vertical axis, so the chord is horizontal and its midpoint falls
# on the axis of symmetry -- the gap to the curve is then unambiguous and
# reads as a vertical distance rather than an oblique one.
THETA_A = np.deg2rad(150.0)
THETA_B = np.deg2rad(30.0)

# Matching endpoints on the line x1 + x2 = 1. The chord is centred on the
# visible part of the line and given the SAME length as the circle's chord
# (2 cos 30 deg = sqrt(3)), so the two panels really are the same construction
# at the same scale.
#
# The earlier values (-0.85, 1.85) and (0.85, 0.15) were not: x2 = 1.85 is
# outside the axes, so the first endpoint, its label and half the chord were
# drawn off-screen and the panel showed a chord with one end.
_HALF = np.sqrt(3.0) / 2.0 / np.sqrt(2.0)      # half-length along (1,-1)/sqrt2
LINE_A = np.array([0.5 - _HALF, 0.5 + _HALF])
LINE_B = np.array([0.5 + _HALF, 0.5 - _HALF])

LIM = 1.55


def circle_points():
    """The two feasible points, their midpoint, and the midpoint's radius."""
    a = np.array([np.cos(THETA_A), np.sin(THETA_A)])
    b = np.array([np.cos(THETA_B), np.sin(THETA_B)])
    mid = 0.5 * (a + b)
    return a, b, mid, float(np.hypot(*mid))


def line_points():
    """Same construction on the linear constraint."""
    mid = 0.5 * (LINE_A + LINE_B)
    return LINE_A, LINE_B, mid, float(LINE_A[0] + LINE_A[1] - 1.0)


def _frame(ax, title):
    ax.set_xlim(-LIM, LIM)
    ax.set_ylim(-LIM, LIM)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("$x_1$")
    ax.set_title(title, fontsize=14)
    ax.axhline(0.0, color="0.85", linewidth=0.8, zorder=0)
    ax.axvline(0.0, color="0.85", linewidth=0.8, zorder=0)


def _name_constraint(ax, on_curve, text_at):
    """Label the feasible set, with a leader back to it.

    Both panels previously carried a bare "h(x) = 0" parked in a corner with
    nothing near it; on the right it sat a full unit away from the line. A
    label with no referent is worse than no label, so it now points.
    """
    ax.annotate(
        "$h(x) = 0$",
        xy=on_curve,
        xytext=text_at,
        fontsize=13,
        ha="left",
        va="center",
        zorder=6,
        arrowprops=dict(arrowstyle="->", color="0.35", lw=1.3,
                        shrinkA=2, shrinkB=5),
        bbox=dict(facecolor="white", edgecolor="none", pad=1.0),
    )


def _chord(ax, a, b, mid, *, feasible):
    """Draw the chord, its endpoints and its midpoint on one panel."""
    ax.plot(
        [a[0], b[0]],
        [a[1], b[1]],
        linestyle="--",
        linewidth=2.5,
        color="#E69F00",
        zorder=3,
    )
    for pt, name in ((a, "$x^{(1)}$"), (b, "$x^{(2)}$")):
        ax.plot(*pt, marker="o", markersize=9, color="black", linestyle="none", zorder=5)
        ax.annotate(
            name,
            xy=(pt[0], pt[1] + 0.13),
            fontsize=13,
            ha="center",
            zorder=6,
            bbox=dict(facecolor="white", edgecolor="none", pad=1.0),
        )

    ax.plot(
        *mid,
        marker="s" if not feasible else "D",
        markersize=11,
        color="black",
        markerfacecolor="white" if not feasible else "black",
        markeredgewidth=2.0,
        linestyle="none",
        zorder=6,
    )


def make_figure():
    a_c, b_c, mid_c, r_mid = circle_points()
    a_l, b_l, mid_l, _ = line_points()

    fig, axes = plt.subplots(1, 2, figsize=(9.0, 4.6))

    # ---------------- left: nonlinear equality, nonconvex -----------------
    ax = axes[0]
    _frame(ax, "nonlinear: $x_1^2 + x_2^2 = 1$")
    ax.set_ylabel("$x_2$")
    t = np.linspace(0.0, 2.0 * np.pi, 400)
    ax.plot(np.cos(t), np.sin(t), linestyle="-", linewidth=3.0, color="#0072B2", zorder=2)
    _chord(ax, a_c, b_c, mid_c, feasible=False)

    # Drop a marker line from the midpoint to the curve it fails to reach, so
    # the gap is measured rather than asserted.
    ax.plot(
        [mid_c[0], mid_c[0]],
        [mid_c[1], 1.0],
        linestyle=":",
        linewidth=2.0,
        color="0.35",
        zorder=4,
    )
    _name_constraint(ax, (-0.755, -0.656), (-1.45, -1.22))
    ax.annotate(
        "midpoint:\n$h = %.2f \\neq 0$" % (r_mid**2 - 1.0),
        xy=(mid_c[0], mid_c[1] - 0.30),
        fontsize=12.5,
        ha="center",
        va="top",
        zorder=6,
        bbox=dict(facecolor="white", edgecolor="0.6", pad=2.5),
    )

    # ---------------- right: linear equality, convex ----------------------
    ax = axes[1]
    _frame(ax, "linear: $x_1 + x_2 = 1$")
    xs = np.array([-LIM, LIM])
    ax.plot(xs, 1.0 - xs, linestyle="-", linewidth=3.0, color="#0072B2", zorder=2)
    _chord(ax, a_l, b_l, mid_l, feasible=True)
    _name_constraint(ax, (1.25, -0.25), (0.30, -1.22))
    ax.annotate(
        "midpoint:\n$h = 0$  ✓",
        xy=(mid_l[0] - 0.18, mid_l[1] - 0.30),
        fontsize=12.5,
        ha="right",
        va="top",
        zorder=6,
        bbox=dict(facecolor="white", edgecolor="0.6", pad=2.5),
    )

    fig.tight_layout()
    return fig


if __name__ == "__main__":
    a, b, mid, r = circle_points()
    # The two chosen points really are feasible for the circle.
    assert abs(np.hypot(*a) - 1.0) < 1e-12, a
    assert abs(np.hypot(*b) - 1.0) < 1e-12, b
    # ... and the midpoint really is not. cos(30 deg) = sqrt(3)/2, and by
    # symmetry the midpoint is (0, 1/2), so h = 1/4 - 1 = -3/4 exactly.
    assert np.allclose(mid, [0.0, 0.5], atol=1e-12), mid
    assert abs((r**2 - 1.0) - (-0.75)) < 1e-12, r
    print("circle:   x1 = %s" % np.round(a, 6))
    print("          x2 = %s" % np.round(b, 6))
    print("          midpoint = %s,  h(mid) = %+.4f  (infeasible)" % (np.round(mid, 6), r**2 - 1))

    al, bl, midl, resid = line_points()
    assert abs(al[0] + al[1] - 1.0) < 1e-12
    assert abs(bl[0] + bl[1] - 1.0) < 1e-12
    assert abs(midl[0] + midl[1] - 1.0) < 1e-12
    print("line:     midpoint = %s,  h(mid) = %+.4f  (feasible)"
          % (np.round(midl, 6), midl[0] + midl[1] - 1.0))

    # The convexity claim itself, checked by sampling rather than asserted:
    # for the LINE every convex combination is feasible; for the CIRCLE none
    # of the interior ones is.
    rng = np.random.default_rng(0)
    lam = rng.uniform(0.01, 0.99, size=2000)
    on_line = np.abs((1 - lam) * (al[0] + al[1] - 1) + lam * (bl[0] + bl[1] - 1))
    assert on_line.max() < 1e-12
    pts = (1 - lam)[:, None] * a + lam[:, None] * b
    off_circle = np.abs(np.hypot(pts[:, 0], pts[:, 1]) - 1.0)
    assert off_circle.min() > 1e-6, off_circle.min()
    print("sampled 2000 convex combinations: line max |h| = %.2e, "
          "circle min |h| = %.4f" % (on_line.max(), off_circle.min()))
