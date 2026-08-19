"""The four cones of the second order conditions, drawn in two dimensions.

    figures/plots/cone-nesting-2d.py  ->  media/figures/cone-nesting-2d.{png,pdf}

Supports `lecture-notes/lectures/second-order-conditions.tex`, the nesting
display C_3 subset C_2 subset C_4. Biegler (2010) defines all four sets
symbolically -- C_1 and C_2 on printed p. 79, C_3 and C_4 on p. 82, the nesting
in the bullets on pp. 82-83 -- and never draws them. The nesting is the hardest
thing in that lecture to hold in the head from symbols alone, because the
inclusion runs the OPPOSITE way to the number of equations imposed.

There is no worked example behind this figure and it needs none: the sets are
defined by linear conditions on the direction d, so a well-chosen pair of
active constraint gradients renders the whole nesting exactly, with no
approximation and nothing solved.

The configuration
-----------------
n = 2, no equality constraints, two active inequality constraints at x*:

    grad g_1 = (1, 0),  u_1* > 0   -- STRONGLY active
    grad g_2 = (0, 1),  u_2* = 0   -- WEAKLY active

which is the smallest configuration in which all four sets are distinct. Under
the course's sign convention (g(x) <= 0, so feasible directions satisfy
grad g_i^T d <= 0) the definitions collapse to:

    C_1 = {d1 <= 0, d2 <= 0}   third quadrant       -- a WEDGE (a cone)
    C_2 = {d1 =  0, d2 <= 0}   downward half-axis   -- a RAY   (a cone)
    C_3 = {d1 =  0, d2 =  0}   the origin           -- {0}     (a subspace)
    C_4 = {d1 =  0}            the vertical axis    -- a LINE  (a subspace)

so C_3 subset C_2 subset C_4 is visible by inspection, as is the reason the
lecture needs two reduced Hessians rather than one: C_2 is a cone, and only
C_3 and C_4 are subspaces that a null space basis can span.

Why this configuration and not a worked example
-----------------------------------------------
A worked NLP would fix one of these sets to be trivial or would need n >= 3 to
keep all four distinct, and n = 3 cannot be drawn on a handout. Choosing the
gradients directly is the honest way to get the general picture: the figure is
about the DEFINITIONS, not about any particular problem.

Deliberate departures
---------------------
1. Axis-aligned gradients. Skewing them would be more "generic" but would buy
   nothing and would cost the reader the instant read of "d1 = 0".
2. The origin is drawn as an open marker in C_1, C_2 and C_4 and a filled one
   in C_3, because C_3 IS the origin there and is otherwise invisible.
3. The theorems quantify over NONZERO d, so d = 0 is excluded throughout; the
   panels draw the sets as defined and the caption carries the exclusion. Note
   the consequence, which the handout states: C_3 = {0} here means the weaker
   necessary condition is vacuous in this configuration.
"""

import numpy as np
import matplotlib.pyplot as plt

from _house import HATCH_CYCLE, SHADE_ALPHA

LIM = 1.35
ARROW_SCALE = 0.62

# The two active constraint gradients. Index 0 is strongly active.
GRAD_G1 = np.array([1.0, 0.0])
GRAD_G2 = np.array([0.0, 1.0])


def in_c1(d):
    """Linearized feasible directions: <= 0 on every active inequality."""
    return (GRAD_G1 @ d <= 1e-12) and (GRAD_G2 @ d <= 1e-12)


def in_c2(d):
    """Critical cone: = 0 on the strongly active, <= 0 on the weakly active."""
    return (abs(GRAD_G1 @ d) <= 1e-12) and (GRAD_G2 @ d <= 1e-12)


def in_c3(d):
    """= 0 on ALL active inequalities."""
    return (abs(GRAD_G1 @ d) <= 1e-12) and (abs(GRAD_G2 @ d) <= 1e-12)


def in_c4(d):
    """= 0 on the strongly active only."""
    return abs(GRAD_G1 @ d) <= 1e-12


def _frame(ax, title):
    ax.set_xlim(-LIM, LIM)
    ax.set_ylim(-LIM, LIM)
    ax.set_aspect("equal", adjustable="box")
    ax.set_title(title, fontsize=13.5)
    ax.axhline(0.0, color="0.75", linewidth=0.8, zorder=0)
    ax.axvline(0.0, color="0.75", linewidth=0.8, zorder=0)
    ax.set_xticks([])
    ax.set_yticks([])
    ax.set_xlabel("$d_1$", fontsize=13)


def _gradients(ax):
    """Both active gradients, drawn AND named -- an arrow has no linestyle."""
    for vec, name, off in (
        (GRAD_G1, r"$\nabla g_1$", (0.04, 0.10)),
        (GRAD_G2, r"$\nabla g_2$", (0.06, 0.02)),
    ):
        ax.arrow(
            0.0,
            0.0,
            ARROW_SCALE * vec[0],
            ARROW_SCALE * vec[1],
            width=0.022,
            length_includes_head=True,
            color="0.45",
            zorder=3,
        )
        tip = ARROW_SCALE * vec
        ax.annotate(
            name,
            xy=(tip[0] + off[0], tip[1] + off[1]),
            fontsize=11.5,
            color="0.35",
            zorder=6,
            bbox=dict(facecolor="white", edgecolor="none", pad=0.8),
        )


def make_figure():
    fig, axes = plt.subplots(1, 4, figsize=(11.6, 3.5))

    # --- C_1: the wedge ---------------------------------------------------
    ax = axes[0]
    _frame(ax, r"$\mathcal{C}_1(x^*)$")
    ax.fill(
        [-LIM, 0, 0, -LIM],
        [-LIM, -LIM, 0, 0],
        facecolor="0.55",
        alpha=SHADE_ALPHA,
        hatch=HATCH_CYCLE[0],
        edgecolor=plt.rcParams["hatch.color"],
        linewidth=0.0,
        zorder=1,
    )
    ax.plot([-LIM, 0], [0, 0], color="black", linewidth=3.0, zorder=4)
    ax.plot([0, 0], [-LIM, 0], color="black", linewidth=3.0, zorder=4)
    ax.plot(0, 0, marker="o", markersize=7, markerfacecolor="white",
            markeredgecolor="black", markeredgewidth=1.8, zorder=7, linestyle="none")
    ax.set_ylabel("$d_2$", fontsize=13)
    ax.annotate("wedge\n(a cone)", xy=(-1.22, -1.22), fontsize=11.5, ha="left",
                va="bottom", color="0.25")
    _gradients(ax)

    # --- C_2: the ray -----------------------------------------------------
    ax = axes[1]
    _frame(ax, r"$\mathcal{C}_2(x^*,u^*)$")
    ax.plot([0, 0], [-LIM, 0], color="black", linewidth=4.5, zorder=4)
    ax.plot(0, 0, marker="o", markersize=7, markerfacecolor="white",
            markeredgecolor="black", markeredgewidth=1.8, zorder=7, linestyle="none")
    ax.annotate("ray\n(a cone)", xy=(0.16, -1.22), fontsize=11.5, ha="left",
                va="bottom", color="0.25")
    _gradients(ax)

    # --- C_3: the origin --------------------------------------------------
    ax = axes[2]
    _frame(ax, r"$\mathcal{C}_3(x^*)$")
    ax.plot(0, 0, marker="o", markersize=11, color="black", zorder=7,
            linestyle="none")
    ax.annotate(r"$\{0\}$" + "\n(a subspace)", xy=(0.16, -1.22), fontsize=11.5,
                ha="left", va="bottom", color="0.25")
    _gradients(ax)

    # --- C_4: the line ----------------------------------------------------
    ax = axes[3]
    _frame(ax, r"$\mathcal{C}_4(x^*,u^*)$")
    ax.plot([0, 0], [-LIM, LIM], color="black", linewidth=4.5, zorder=4)
    ax.plot(0, 0, marker="o", markersize=7, markerfacecolor="white",
            markeredgecolor="black", markeredgewidth=1.8, zorder=7, linestyle="none")
    ax.annotate("line\n(a subspace)", xy=(0.16, -1.22), fontsize=11.5, ha="left",
                va="bottom", color="0.25")
    _gradients(ax)

    fig.tight_layout()
    return fig


if __name__ == "__main__":
    # Every claim the figure makes, checked numerically rather than asserted.
    rng = np.random.default_rng(0)

    # 1. Dense Monte Carlo over general directions for the two cone inclusions
    #    that are NOT exact-arithmetic degenerate.
    pts = rng.uniform(-2.0, 2.0, size=(200000, 2))
    # Snap d1 to exactly zero on half the sample so C_2/C_3/C_4 are populated.
    pts[::2, 0] = 0.0
    pts[::4, 1] = 0.0

    n2 = n3 = n4 = 0
    for d in pts:
        c1, c2, c3, c4 = in_c1(d), in_c2(d), in_c3(d), in_c4(d)
        if c3:
            assert c2, f"C_3 not subset C_2 at {d}"
            n3 += 1
        if c2:
            assert c4, f"C_2 not subset C_4 at {d}"
            assert c1, f"C_2 not subset C_1 at {d}"
            n2 += 1
        if c4:
            n4 += 1
    assert n2 > 0 and n3 > 0 and n4 > 0, "a set was never sampled"
    print(f"nesting verified on {len(pts)} directions: "
          f"|C_2 hits|={n2}, |C_3 hits|={n3}, |C_4 hits|={n4}")

    # 2. Dimensions, from the rank of the matrix of imposed equalities.
    #    A_3 imposes both gradients; A_4 imposes only the strongly active one.
    A3 = np.vstack([GRAD_G1, GRAD_G2])
    A4 = GRAD_G1.reshape(1, 2)
    dim3 = 2 - np.linalg.matrix_rank(A3)
    dim4 = 2 - np.linalg.matrix_rank(A4)
    assert dim3 == 0, dim3
    assert dim4 == 1, dim4
    print(f"dim C_3 = {dim3} (the origin), dim C_4 = {dim4} (a line)")

    # 3. The null space bases the lecture calls Z_3 and Z_4: Z_4 must have
    #    strictly MORE columns than Z_3, since A_4 has strictly fewer rows.
    z3_cols = dim3
    z4_cols = dim4
    assert z4_cols > z3_cols, "Z_4 must be wider than Z_3 when A_w is nonempty"
    print(f"Z_3 has {z3_cols} columns, Z_4 has {z4_cols} -- A_w nonempty, so strict")

    # 4. C_3 = {0} makes the WEAKER necessary condition vacuous here.
    print("C_3 = {0}: the necessary condition over C_3 is vacuous in this "
          "configuration, which is exactly why it is the weaker one")
