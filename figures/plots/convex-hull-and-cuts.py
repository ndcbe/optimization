"""The convex hull of the integer points, and what a cutting plane is doing.

    figures/plots/convex-hull-and-cuts.py
        -> media/figures/convex-hull-and-cuts.{png,pdf}

WHY THIS FIGURE EXISTS. Prof. Dowling's own margin note on page 1 of the 2018
scan (`handwritten_notes/Lecture Notes Fall 2018/
Lecture25_IntegerProgrammingAlgorithms.pdf`, top-right of the first page) reads:

    "Next time: add convex hull picture"

Section 2 of the handout defines the convex hull in one line -- "the smallest
possible LP feasible region that contains ALL the integer solutions" -- and
then never draws it. This is that picture.

WHAT IT SHOWS. A two-variable integer program, small enough to enumerate:

    max  4 x1 - x2
    s.t. 7 x1 - 2 x2 <= 14
         2 x1 - 2 x2 <=  3
                 x2  <=  3
         x1, x2 >= 0 and integer

Panel 1, "the ideal we cannot have": the LP relaxation polytope P, every
integer point in it, and conv(S), the convex hull of those points. The LP
optimum over P is FRACTIONAL, at (20/7, 3) ~ (2.857, 3). Optimising the same
linear objective over conv(S) instead lands on (2, 1), an integer point -- and
that is the content of the handout's claim that if we had the hull we would be
done in one LP. Every vertex of conv(S) is an integer point, so an LP over it
cannot return anything else.

Panel 2, "what we do instead": the same polytope with two valid inequalities
added, x1 <= 2 and x1 - x2 <= 1. Each is a FACET of conv(S), so neither removes
a single integer point; together they cut the fractional vertex away and the LP
over the reduced region returns (2, 1) directly.

The pedagogy is the pair. Panel 1 says why the hull would solve the problem;
panel 2 says you get the same answer by adding inequalities on demand rather
than by constructing the hull up front -- which is the handout's three-strategy
list, drawn. Note that ONE cut is not enough: adding only x1 <= 2 moves the LP
optimum to (2, 0.5), still fractional. That is why the second cut is drawn, and
it is worth saying out loud, because a figure with a single cut quietly teaches
that one round always suffices.

AN HONESTY NOTE, and it belongs in the caption. On THIS instance the two cuts
do not merely approximate the hull near the optimum -- they reproduce it
exactly. P intersected with {x1 <= 2, x1 - x2 <= 1} has vertices (0,0), (1,0),
(2,1), (2,3), (0,3), which is precisely the vertex set of conv(S); the shaded
region in panel 2 IS the hatched region in panel 1. That is an artefact of an
instance small enough to draw: conv(S) here has only two facets that P does not
already have, so two cuts finish it. The general claim -- that cutting planes
buy a useful piece of the hull without ever writing down all of it -- is true
and is the reason the method exists, but this figure cannot be the evidence for
it, and the caption must not pretend otherwise. Checked in the self-check
below rather than asserted.

PROVENANCE. This is the standard textbook instance for the picture and is not
Prof. Dowling's; it is essentially Wolsey, *Integer Programming* (Wiley, 1998),
Chapter 1. It is used here rather than a BGW figure because Chapter 15 and
Appendix A of Biegler, Grossmann & Westerberg contain NO cutting planes, no
valid inequalities and no convex hull at all -- verified by reading both -- so
there is no figure in the course's own secondary text to redraw. Drawing our
own instance also avoids any reproduction question.

NO SOLVER BINARY. The integer points are enumerated over a bounded box; the
hull is `scipy.spatial.ConvexHull`; every LP is `scipy.optimize.linprog`
(HiGHS). Nothing here needs Pyomo or Ipopt.

GREYSCALE. Three regions and two cut lines is past what colour alone can carry,
so: P is an unfilled outline, conv(S) is hatched (see _house.py), the integer
points are black dots, the fractional LP optimum is an open star and the
integer optimum a filled star, and both cuts are labelled in place with their
own inequality rather than through a legend.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import linprog
from scipy.spatial import ConvexHull

from _house import HATCH_CYCLE, SHADE_ALPHA

# --- the instance -----------------------------------------------------------
# Rows of A x <= b for the LP relaxation P (plus x >= 0).
A_P = np.array([[7.0, -2.0], [2.0, -2.0], [0.0, 1.0]])
B_P = np.array([14.0, 3.0, 3.0])

# max 4 x1 - x2  ==  min -4 x1 + x2, which is what linprog wants.
C_MIN = np.array([-4.0, 1.0])

# The two valid inequalities added in panel 2. Both are facets of conv(S).
CUTS = [
    (np.array([1.0, 0.0]), 2.0, r"$x_1 \leq 2$"),
    (np.array([1.0, -1.0]), 1.0, r"$x_1 - x_2 \leq 1$"),
]

XLO, XHI = -0.35, 3.6
YLO, YHI = -0.45, 3.7


def solve_lp(A, b):
    """Maximise 4 x1 - x2 over {A x <= b, x >= 0}. Returns (x, objective)."""
    res = linprog(C_MIN, A_ub=A, b_ub=b, bounds=[(0, None), (0, None)],
                  method="highs")
    assert res.success, res.message
    return res.x, -res.fun


def integer_points():
    """Every integer point of P, by enumeration over a box that contains P."""
    pts = []
    for x1 in range(0, 6):
        for x2 in range(0, 6):
            v = np.array([float(x1), float(x2)])
            if np.all(A_P @ v <= B_P + 1e-9):
                pts.append(v)
    return np.array(pts)


def polygon(A, b, *, lo=-1.0, hi=8.0):
    """Vertices of {A x <= b, x >= 0}, in counter-clockwise order.

    Found by intersecting every pair of bounding lines and keeping the
    intersections that satisfy all the constraints -- adequate and exact for a
    polygon this small, and it avoids a dependency on a polytope library.
    """
    A_all = np.vstack([A, np.array([[-1.0, 0.0], [0.0, -1.0]])])
    b_all = np.concatenate([b, np.array([0.0, 0.0])])
    verts = []
    n = len(b_all)
    for i in range(n):
        for j in range(i + 1, n):
            M = np.array([A_all[i], A_all[j]])
            if abs(np.linalg.det(M)) < 1e-12:
                continue
            v = np.linalg.solve(M, np.array([b_all[i], b_all[j]]))
            if np.all(A_all @ v <= b_all + 1e-9) and np.all(v > lo) and np.all(v < hi):
                verts.append(v)
    verts = np.array(verts)
    # De-duplicate, then order by angle about the centroid.
    uniq = []
    for v in verts:
        if not any(np.allclose(v, u, atol=1e-7) for u in uniq):
            uniq.append(v)
    uniq = np.array(uniq)
    c = uniq.mean(axis=0)
    order = np.argsort(np.arctan2(uniq[:, 1] - c[1], uniq[:, 0] - c[0]))
    return uniq[order]


def _draw_line(ax, a, rhs, **kw):
    """Draw the line a . x = rhs across the current view."""
    xs = np.linspace(XLO, XHI, 2)
    if abs(a[1]) > 1e-12:
        ax.plot(xs, (rhs - a[0] * xs) / a[1], **kw)
    else:
        ax.axvline(rhs / a[0], **kw)


def _frame(ax):
    ax.set_xlim(XLO, XHI)
    ax.set_ylim(YLO, YHI)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("$x_1$")
    ax.set_xticks([0, 1, 2, 3])
    ax.set_yticks([0, 1, 2, 3])


def make_figure():
    S = integer_points()
    hull = ConvexHull(S)
    hull_v = S[hull.vertices]

    P = polygon(A_P, B_P)
    x_lp, z_lp = solve_lp(A_P, B_P)

    # Panel 2: P with both cuts appended.
    A_cut = np.vstack([A_P] + [c[0] for c in CUTS])
    b_cut = np.concatenate([B_P, np.array([c[1] for c in CUTS])])
    P_cut = polygon(A_cut, b_cut)
    x_cut, z_cut = solve_lp(A_cut, b_cut)

    fig, axes = plt.subplots(1, 2, figsize=(9.6, 4.6))

    for ax in axes:
        _frame(ax)
    axes[0].set_ylabel("$x_2$")

    # ---------------- Panel 1: the hull ---------------------------------
    ax = axes[0]
    ax.set_title("1. the hull we cannot afford", fontsize=14)
    ax.plot(np.append(P[:, 0], P[0, 0]), np.append(P[:, 1], P[0, 1]),
            color="black", linestyle="-", linewidth=2.2, zorder=3)
    ax.fill(hull_v[:, 0], hull_v[:, 1], facecolor="0.55", alpha=SHADE_ALPHA,
            hatch=HATCH_CYCLE[0], edgecolor=plt.rcParams["hatch.color"],
            linewidth=0.0, zorder=1)
    ax.plot(np.append(hull_v[:, 0], hull_v[0, 0]),
            np.append(hull_v[:, 1], hull_v[0, 1]),
            color="#0072B2", linestyle="--", linewidth=2.4, zorder=4)
    ax.plot(S[:, 0], S[:, 1], "o", color="black", markersize=7,
            linestyle="none", zorder=6)
    ax.plot(*x_lp, marker="*", markersize=20, markerfacecolor="white",
            markeredgecolor="black", markeredgewidth=1.6, linestyle="none",
            zorder=7)

    ax.annotate("LP relaxation $P$", xy=(3.02, 3.30), fontsize=12.5,
                ha="center", color="black")
    ax.annotate(r"$\bar{z}$ here: $x=(20/7,\,3)$",
                xy=(x_lp[0] - 0.14, x_lp[1] - 0.02), xytext=(1.32, 2.42),
                fontsize=12.5, ha="left", va="center",
                arrowprops=dict(arrowstyle="->", color="0.35", lw=1.3))
    ax.annotate(r"$\mathrm{conv}(S)$", xy=(0.22, 1.52), fontsize=13,
                color="#0072B2",
                bbox=dict(facecolor="white", edgecolor="none", pad=1.0))
    ax.annotate("every vertex\nis integral", xy=(2.0, 1.0),
                xytext=(2.28, 0.10), fontsize=12, ha="left", va="bottom",
                color="#0072B2",
                arrowprops=dict(arrowstyle="->", color="#0072B2", lw=1.3))

    # ---------------- Panel 2: two cuts ---------------------------------
    ax = axes[1]
    ax.set_title("2. two cuts, added on demand", fontsize=14)
    ax.plot(np.append(P[:, 0], P[0, 0]), np.append(P[:, 1], P[0, 1]),
            color="0.62", linestyle="-", linewidth=1.6, zorder=2)
    ax.fill(P_cut[:, 0], P_cut[:, 1], facecolor="0.55", alpha=SHADE_ALPHA,
            hatch=HATCH_CYCLE[0], edgecolor=plt.rcParams["hatch.color"],
            linewidth=0.0, zorder=1)
    ax.plot(np.append(P_cut[:, 0], P_cut[0, 0]),
            np.append(P_cut[:, 1], P_cut[0, 1]),
            color="black", linestyle="-", linewidth=2.2, zorder=3)

    for (a, rhs, lab), sty in zip(CUTS, ["--", "-."]):
        _draw_line(ax, a, rhs, color="#E69F00", linestyle=sty, linewidth=2.4,
                   zorder=4)

    ax.plot(S[:, 0], S[:, 1], "o", color="black", markersize=7,
            linestyle="none", zorder=6)
    ax.plot(*x_lp, marker="*", markersize=20, markerfacecolor="white",
            markeredgecolor="0.55", markeredgewidth=1.6, linestyle="none",
            zorder=5)
    ax.plot(*x_cut, marker="*", markersize=20, color="black",
            linestyle="none", zorder=7)

    ax.annotate(CUTS[0][2], xy=(2.06, 3.42), fontsize=12.5, color="#E69F00",
                ha="left", va="center")
    ax.annotate(CUTS[1][2], xy=(3.50, 1.12), fontsize=12.5, color="#E69F00",
                ha="right", va="center",
                bbox=dict(facecolor="white", edgecolor="none", pad=1.0))
    ax.annotate("cut off", xy=(x_lp[0], x_lp[1]), xytext=(2.32, 2.62),
                fontsize=12, ha="right", va="center", color="0.35",
                arrowprops=dict(arrowstyle="->", color="0.55", lw=1.2))
    ax.annotate(r"now integral: $x=(2,1)$", xy=(2.0, 1.0), xytext=(0.18, -0.28),
                fontsize=12.5, ha="left", va="center",
                arrowprops=dict(arrowstyle="->", color="0.35", lw=1.3),
                bbox=dict(facecolor="white", edgecolor="none", pad=1.0))

    fig.tight_layout()
    return fig


if __name__ == "__main__":
    S = integer_points()
    hull = ConvexHull(S)
    hull_v = S[hull.vertices]

    x_lp, z_lp = solve_lp(A_P, B_P)
    print(f"LP relaxation optimum  x = {x_lp}, z = {z_lp:.6f}")
    assert np.allclose(x_lp, [20 / 7, 3.0]), x_lp
    assert abs(z_lp - (4 * 20 / 7 - 3)) < 1e-9
    assert not np.allclose(x_lp, np.round(x_lp)), "LP optimum should be fractional"

    # Every hull vertex must be an integer point -- this is the panel-1 claim.
    for v in hull_v:
        assert np.allclose(v, np.round(v)), v
    print(f"conv(S) vertices (all integral): "
          f"{sorted(tuple(int(t) for t in v) for v in hull_v)}")

    # The integer optimum, by complete enumeration.
    z_int = max(4 * p[0] - p[1] for p in S)
    best = [tuple(int(t) for t in p) for p in S if 4 * p[0] - p[1] == z_int]
    print(f"integer optimum by enumeration: z* = {z_int:.0f} at {best}")
    assert z_int == 7.0 and best == [(2, 1)], (z_int, best)

    # Both cuts must be VALID: no integer point of P may violate either.
    for a, rhs, lab in CUTS:
        worst = max(a @ p for p in S)
        print(f"  valid inequality {lab:>22}: max over S = {worst:.0f} <= {rhs:.0f}")
        assert worst <= rhs + 1e-9

    # ... and together they must cut the fractional vertex away.
    A_cut = np.vstack([A_P] + [c[0] for c in CUTS])
    b_cut = np.concatenate([B_P, np.array([c[1] for c in CUTS])])
    x_cut, z_cut = solve_lp(A_cut, b_cut)
    print(f"LP after both cuts     x = {x_cut}, z = {z_cut:.6f}")
    assert np.allclose(x_cut, [2.0, 1.0]), x_cut
    assert abs(z_cut - z_int) < 1e-9, (z_cut, z_int)

    # One cut is NOT enough -- the docstring says so, so it is checked.
    A_one = np.vstack([A_P, CUTS[0][0]])
    b_one = np.concatenate([B_P, [CUTS[0][1]]])
    x_one, z_one = solve_lp(A_one, b_one)
    print(f"LP after the first cut only: x = {x_one}, z = {z_one:.6f}"
          f"  (still fractional)")
    assert np.allclose(x_one, [2.0, 0.5]), x_one
    # The honesty note in the docstring: on this instance the two cuts give
    # back the WHOLE hull, not a local piece of it. Checked, not assumed.
    P_cut = polygon(A_cut, b_cut)
    got = sorted(tuple(np.round(v, 9)) for v in P_cut)
    want = sorted(tuple(np.round(v, 9)) for v in hull_v)
    assert np.allclose(np.array(got), np.array(want)), (got, want)
    print("P + both cuts has exactly the vertices of conv(S): "
          f"{[tuple(int(round(t)) for t in v) for v in sorted(got)]}")
    print("  -> on THIS instance the cuts reproduce the hull exactly; the "
          "caption says so.")
    print("all self-checks passed")
