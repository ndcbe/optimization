"""Guess-and-check against the solver: objective vs. x3 for a 3-variable NLP.

    figures/plots/guess-and-check.py  ->  media/figures/guess-and-check.{png,pdf}

`notebooks/1-dev/Pyomo-Introduction.ipynb` cell 19. The model is

    min  x1^2 + 2 x2^2 - x3   s.t.  x1 + x2 = 1,  x1 + 2 x2 - x3 = 5,
                                    -10 <= x1, x2, x3 <= 10.

Three variables, two equalities, so exactly ONE degree of freedom. Guess x3,
solve the 2x2 linear system for (x1, x2), evaluate the objective, repeat: the
whole feasible set is a curve and you can draw it. The solver's answer has to
land at its minimum, and it does.

SOLVER-FREE, and exactly so rather than approximately. The notebook marks the
Pyomo/Ipopt solution; here it is re-derived in closed form. Eliminating the
constraints gives x1 = -3 - x3 and x2 = 4 + x3 (determinant 1), hence

    F(x3) = (x3 + 3)^2 + 2 (x3 + 4)^2 - x3 = 3 x3^2 + 21 x3 + 41,

so F'(x3) = 6 x3 + 21 = 0 at x3 = -7/2, with F = 17/4 and
(x1, x2) = (1/2, 1/2). All three lie strictly inside [-10, 10], so no bound is
active and this is the constrained minimum. The curve below is evaluated from
the linear solve, not from the closed form, so the two agree only if the
elimination is right.

Greyscale: two series, and they are already of different KINDS -- a solid line
and a single marker with no line. Nothing depends on colour.
"""

import numpy as np
import matplotlib.pyplot as plt

# Objective and the constraint solve, written the way the notebook writes them
# so the figure and the notebook can be read side by side.
A = np.array([[1.0, 1.0], [1.0, 2.0]])


def constraints(x3):
    """Solve [[1,1],[1,2]] [x1,x2]^T = [1, 5 + x3]^T."""
    return np.linalg.solve(A, np.array([1.0, 5.0 + x3]))


def objective(x1, x2, x3):
    return x1**2 + 2.0 * x2**2 - x3


# Closed-form optimum (see the docstring); asserted, not assumed.
X3_STAR = -3.5
OBJ_STAR = 4.25


def make_figure():
    x3_guesses = np.linspace(-10.0, 4.0, 29)
    obj = np.array([objective(*constraints(x3), x3) for x3 in x3_guesses])

    x1s, x2s = constraints(X3_STAR)
    assert np.allclose([x1s, x2s], [0.5, 0.5])
    assert np.isclose(objective(x1s, x2s, X3_STAR), OBJ_STAR)

    fig, ax = plt.subplots(figsize=(5.4, 3.9))

    ax.plot(x3_guesses, obj, label="guess and check")
    ax.plot(
        [X3_STAR],
        [OBJ_STAR],
        marker="o",
        markersize=11,
        linestyle="",
        markerfacecolor="none",
        markeredgewidth=2.5,
        label="solver",
    )

    # Direct labelling, per the house guide, rather than a legend: two items
    # only, and both sit in empty parts of the axes.
    ax.annotate("guess and check", xy=(-9.7, 150.0), fontsize=13)
    ax.annotate(
        "solver\n" + r"$x_3 = -3.5$, $f = 4.25$",
        xy=(X3_STAR, OBJ_STAR),
        xytext=(-2.8, 78.0),
        fontsize=13,
        va="center",
        arrowprops=dict(arrowstyle="->", lw=1.2, color="black"),
    )

    ax.set_xlabel("$x_3$")
    ax.set_ylabel("$f(x)$")
    ax.set_xlim(-10.0, 4.0)
    ax.set_ylim(bottom=0.0)

    fig.tight_layout()
    return fig
