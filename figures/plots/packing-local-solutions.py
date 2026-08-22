"""Two local solutions of the circle-packing NLP, from two starting guesses.

    figures/plots/packing-local-solutions.py
        -> media/figures/packing-local-solutions.{png,pdf}

WHY THIS FIGURE EXISTS. `lecture-notes/lectures/constrained-intro.tex` builds
Biegler's Example 4.4 (p. 67) -- pack three circles in the smallest-perimeter
box -- then asks "Is this problem convex?" and answers, in the handout's own
words, that the No Overlap constraints are nonconvex, that
Theorem 4.2 therefore does not apply, and that

    "The optimum you find depends on where you start."

That last sentence was the only claim in the lecture with no evidence behind
it. This is the evidence. It is also Biegler's own second bullet on p. 68:

    "Change the initial arrangement of the circles and manually shrink the
     walls of the box. The optimal solution will depend on the initial
     positions of the circles."

THE MODEL is (4.7), pp. 67-68, exactly as the handout typesets it:

    min  2(A + B)
    s.t. A, B >= 0
         x_i >= R_i,  y_i >= R_i,  x_i <= B - R_i,  y_i <= A - R_i    In Box
         (x_i - x_j)^2 + (y_i - y_j)^2 >= (R_i + R_j)^2, i < j        No Overlap

Biegler prints no numerical radii -- Figure 4.4 is a sketch -- so the instance
is ours: R = (1.0, 0.7, 0.6), "three circles of different sizes" as the text
says, chosen by the search recorded below.

WHAT IT SHOWS. The same model, the same solver, the same tolerances, two
starting arrangements.

    left   start: the three circles strung along the diagonal
           -> box 2.596 x 3.148, perimeter 11.488
    right  start: one circle in each of three corners
           -> box 3.373 x 3.149, perimeter 13.045, which is 13.6% worse

Both are local solutions. Neither is refuted by anything local: a local solver
started at either one stays there. That is the entire content of "no guarantee
of a global solution".

⚠ THE CLAIM "LOCAL SOLUTION" IS CHECKED, NOT ASSERTED, AND THE OBVIOUS CHECK
IS WRONG. The tempting test -- perturb the answer, re-solve, see whether it
comes back -- measures the BASIN RADIUS, not local minimality: a genuine local
minimum is escaped by any perturbation larger than its basin. Run that test and
you conclude, falsely, that this problem has one local solution.

The test used instead is a trust-region certificate. For delta in
{0.05, 0.2, 0.5}, minimise the objective over the feasible set INTERSECTED with
the ball ||z - z*|| <= delta, from many starts inside that ball; z* is a local
minimum out to radius delta if nothing in the ball beats it. Both points below
survive delta = 0.5, which is large next to a box of side ~3.

This matters because SLSQP also stops at points that are NOT local minima --
on this instance at perimeters 11.833, 12.689, 12.738 and 13.139, every one of
which the certificate improves upon. Only 11.488 and 13.045 survive, and they
are the two drawn. A figure captioned "two local optima" that had picked
11.833 would have been a false claim that executed cleanly.

INSTANCE SELECTION. R = (1.0, 0.7, 0.6) was chosen by running the certificate
over candidate radii triples. Several give only ONE certified local minimum
(e.g. (1.0, 0.6, 0.4), where every other stationary point fails at delta =
0.05), which would make the picture impossible. This triple gives two, they are
13.6% apart -- far enough that the two boxes differ visibly on the page -- and
the radii are visibly unequal, as Biegler's "three circles of different sizes"
requires.

NO SOLVER BINARY. `scipy.optimize.minimize(method="SLSQP")`, which is a local
NLP solver in the same sense as IPOPT for this purpose. Nothing here needs
Pyomo, IPOPT or `idaes get-extensions`, so the figure rebuilds anywhere.

GREYSCALE. The three circles carry three genuinely different hatches (see the
warning above the HATCHES tuple) and their own labels, so they are told apart
without colour. The starting arrangement is
dotted and unfilled against the solid, filled solution -- a linestyle contrast,
not a colour one. The box is black in both panels.
"""

from __future__ import annotations

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle
from scipy.optimize import minimize

from _house import HATCH_CYCLE, SHADE_ALPHA

# ⚠ NOT HATCH_CYCLE[0], [1], [2] -- but NOT for the reason this comment used to
# give. The old reason was a matplotlib 3.5.1 rendering defect in which every
# backslash hatch came out at the forward-slash slope, making HATCH_CYCLE[1]
# ("\\\") pixel-for-pixel a coarser HATCH_CYCLE[0] ("///"). That defect does
# NOT reproduce under the matplotlib 3.11.1 in optimization_fall2026: [0] is
# +45 deg and [1] is -45 deg, which by the hatch spec is the most SEPARATED
# line pair in the cycle. Do not reintroduce the workaround; plots/licq-cusp.py
# pairs [0] with [1] on purpose.
#
# Index 1 is still skipped, for a reason of this figure's own, and it was
# checked by rendering the alternative and looking at it. Three circles need
# three textures, and the set below spends three different texture FAMILIES --
# lines, dots, crosses -- so every pair differs in kind. Restoring [1] gives
# "///", "\\\", "..." instead, which puts two of the three in the same family,
# separated only by the SIGN of the slope. That is the most fragile cue here:
# the hatch is drawn in pale grey at low alpha inside circles that touch, so at
# handout size R_1 and R_2 stop reading as two kinds of thing. The rendered
# comparison also loses the crossed "xxx" that currently makes R_3 distinctive.
HATCHES = (HATCH_CYCLE[0], HATCH_CYCLE[2], HATCH_CYCLE[3])   # /// ... xxx

# --- the instance -----------------------------------------------------------
RADII = np.array([1.0, 0.7, 0.6])
NCIRC = len(RADII)

# The box the search starts inside. Big enough that every starting arrangement
# below is feasible, so the solver never has to repair the guess first.
BOX0 = 4.6

# Two starting arrangements, both feasible, both describable in words. The
# decision vector is z = [A, B, x_1, y_1, x_2, y_2, x_3, y_3], matching the
# order the handout lists the variables in.
STARTS = {
    "strung along the diagonal": [BOX0, BOX0, 1.0, 1.0, 2.3, 2.3, 3.4, 3.4],
    "one circle per corner": [BOX0, BOX0, 1.2, 1.2, 3.9, 0.8, 0.7, 3.9],
}

LIM_LO, LIM_HI = -0.62, 5.00


def objective(z):
    """Perimeter 2(A + B). Biegler (4.7), p. 67."""
    return 2.0 * (z[0] + z[1])


def objective_grad(z):
    g = np.zeros_like(z)
    g[0] = 2.0
    g[1] = 2.0
    return g


def constraints(z):
    """All of (4.7) written as c(z) >= 0, In Box first then No Overlap."""
    A, B = z[0], z[1]
    x, y = z[2::2], z[3::2]
    c = []
    for i in range(NCIRC):
        c += [x[i] - RADII[i], y[i] - RADII[i],
              B - RADII[i] - x[i], A - RADII[i] - y[i]]
    for i in range(NCIRC):
        for j in range(i + 1, NCIRC):
            c.append((x[i] - x[j]) ** 2 + (y[i] - y[j]) ** 2
                     - (RADII[i] + RADII[j]) ** 2)
    return np.array(c)


def solve(z0, extra=()):
    """One local solve. SLSQP plays the part IPOPT plays in the notebook."""
    return minimize(
        objective, np.asarray(z0, dtype=float), jac=objective_grad,
        constraints=[{"type": "ineq", "fun": constraints}] + list(extra),
        method="SLSQP", options={"maxiter": 900, "ftol": 1e-13},
    )


def best_in_ball(z, delta, ntry=300, seed=1):
    """Smallest perimeter attainable inside ||w - z|| <= delta and feasible.

    The trust-region certificate described in the docstring. If this returns
    objective(z) then z is a local minimum out to radius delta; if it returns
    less, z is a point the solver stopped at and nothing more.
    """
    ball = {"type": "ineq", "fun": lambda w: delta ** 2 - np.sum((w - z) ** 2)}
    rng = np.random.default_rng(seed)
    best = objective(z)
    for _ in range(ntry):
        d = rng.normal(size=len(z))
        d *= (delta * rng.uniform(0.0, 1.0) ** (1.0 / len(z))) / np.linalg.norm(d)
        res = solve(z + d, extra=[ball])
        if (res.success and constraints(res.x).min() > -1e-7
                and np.linalg.norm(res.x - z) <= delta + 1e-6):
            best = min(best, objective(res.x))
    return best


def _draw_circles(ax, z, *, solution):
    """Draw one arrangement. `solution` toggles solved vs starting guess."""
    x, y = z[2::2], z[3::2]
    for i in range(NCIRC):
        if solution:
            ax.add_patch(Circle(
                (x[i], y[i]), RADII[i], facecolor="0.55", alpha=SHADE_ALPHA,
                hatch=HATCHES[i], edgecolor=plt.rcParams["hatch.color"],
                linewidth=0.0, zorder=2))
            ax.add_patch(Circle(
                (x[i], y[i]), RADII[i], facecolor="none", edgecolor="#0072B2",
                linewidth=2.4, zorder=3))
            ax.annotate("$R_%d$" % (i + 1), xy=(x[i], y[i]), fontsize=13,
                        ha="center", va="center", zorder=6)
        else:
            ax.add_patch(Circle(
                (x[i], y[i]), RADII[i], facecolor="none", edgecolor="0.72",
                linestyle=":", linewidth=1.5, zorder=1))


def _draw_box(ax, z):
    """The enclosing box, with its two dimensions written on it."""
    A, B = z[0], z[1]
    ax.add_patch(Rectangle((0.0, 0.0), B, A, facecolor="none", edgecolor="black",
                           linewidth=2.6, zorder=4))
    ax.annotate("", xy=(-0.30, 0.0), xytext=(-0.30, A),
                arrowprops=dict(arrowstyle="<->", color="black", lw=1.3))
    ax.annotate("$A = %.2f$" % A, xy=(-0.30, 0.5 * A), fontsize=12.5,
                ha="center", va="center", rotation=90,
                bbox=dict(facecolor="white", edgecolor="none", pad=1.0))
    ax.annotate("", xy=(0.0, -0.30), xytext=(B, -0.30),
                arrowprops=dict(arrowstyle="<->", color="black", lw=1.3))
    ax.annotate("$B = %.2f$" % B, xy=(0.5 * B, -0.30), fontsize=12.5,
                ha="center", va="center",
                bbox=dict(facecolor="white", edgecolor="none", pad=1.0))


def _draw_start_box(ax):
    """The loose box every run starts from. Biegler's p. 68 bullet is about
    shrinking these walls, so the walls have to be on the page."""
    ax.add_patch(Rectangle((0.0, 0.0), BOX0, BOX0, facecolor="none",
                           edgecolor="0.72", linestyle=":", linewidth=1.5,
                           zorder=1))


def _frame(ax, title):
    ax.set_xlim(LIM_LO, LIM_HI)
    ax.set_ylim(LIM_LO, LIM_HI)
    ax.set_aspect("equal", adjustable="box")
    ax.set_xlabel("$x$")
    ax.set_title(title, fontsize=13.5)
    ax.set_xticks([0, 1, 2, 3, 4])
    ax.set_yticks([0, 1, 2, 3, 4])


def make_figure():
    solved = {name: solve(z0).x for name, z0 in STARTS.items()}
    perims = {name: objective(z) for name, z in solved.items()}
    names = list(STARTS)
    penalty = 100.0 * (perims[names[1]] / perims[names[0]] - 1.0)

    fig, axes = plt.subplots(1, 2, figsize=(9.6, 5.0))
    axes[0].set_ylabel("$y$")

    captions = [
        "start: %s\n$2(A+B) = %.2f$" % (names[0], perims[names[0]]),
        "start: %s\n$2(A+B) = %.2f$   $(+%.1f\\%%)$"
        % (names[1], perims[names[1]], penalty),
    ]
    for ax, name, title in zip(axes, names, captions):
        _frame(ax, title)
        _draw_start_box(ax)
        _draw_circles(ax, STARTS[name], solution=False)
        _draw_circles(ax, solved[name], solution=True)
        _draw_box(ax, solved[name])

    axes[0].annotate("dotted: where the solver started",
                     xy=(0.10, 4.30), fontsize=11.5,
                     ha="left", va="top", color="0.40")

    fig.tight_layout()
    return fig


if __name__ == "__main__":
    print("radii R = %s" % RADII)
    solved = {}
    for name, z0 in STARTS.items():
        assert constraints(np.asarray(z0, float)).min() > -1e-9, \
            "starting arrangement %r is infeasible" % name
        res = solve(z0)
        assert res.success, (name, res.message)
        z = res.x
        assert constraints(z).min() > -1e-7, (name, constraints(z).min())
        solved[name] = z
        print("start %-28s -> A = %.4f, B = %.4f, perimeter = %.4f"
              % (name, z[0], z[1], objective(z)))
        print("      centres %s"
              % [(round(z[2 + 2 * i], 3), round(z[3 + 2 * i], 3))
                 for i in range(NCIRC)])

    names = list(STARTS)
    p0, p1 = (objective(solved[n]) for n in names)
    assert p1 > p0 + 1.0, (p0, p1)
    print("the two answers differ by %.1f%% of the better one"
          % (100.0 * (p1 / p0 - 1.0)))

    # THE CLAIM IN THE CAPTION: both really are local minima. Trust-region
    # certificate, not a perturb-and-resolve test -- see the docstring.
    for name in names:
        z = solved[name]
        for delta in (0.05, 0.2, 0.5):
            best = best_in_ball(z, delta, ntry=200, seed=17)
            print("  %-28s delta = %.2f: best feasible in ball = %.5f"
                  % (name, delta, best))
            assert best > objective(z) - 1e-3, (name, delta, best, objective(z))
    print("both points certified as local minima out to radius 0.5")

    # And the counterexample that makes the certificate worth running: SLSQP
    # also stops at points that are NOT local minima.
    rng = np.random.default_rng(0)
    stalls = {}
    for _ in range(300):
        z0 = np.concatenate([[BOX0, BOX0],
                             rng.uniform(0.6, BOX0 - 0.6, size=2 * NCIRC)])
        res = solve(z0)
        if res.success and constraints(res.x).min() > -1e-7:
            stalls.setdefault(round(objective(res.x), 3), res.x)
    bad = []
    for value in sorted(stalls):
        if any(abs(value - objective(solved[n])) < 1e-2 for n in names):
            continue
        if best_in_ball(stalls[value], 0.5, ntry=120, seed=5) < value - 1e-3:
            bad.append(value)
    print("SLSQP also stopped at %s, none of which survives the certificate"
          % bad)
    assert bad, "expected at least one non-minimal stopping point"
    print("all self-checks passed")
