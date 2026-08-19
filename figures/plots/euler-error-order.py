r"""Order of accuracy: global error vs step size for forward and backward Euler.

    figures/plots/euler-error-order.py  ->  media/figures/euler-error-order.{png,pdf}

`notebooks/3-dev/DAE_numeric_integration.ipynb` cell 16, which solves
z' = -z, z(0) = 1 to t = 2 with both Euler methods over six halvings of the
step and plots the error on log-log axes. That cell *prints* the two fitted
slopes underneath the plot; a printed handout has no "underneath", so the
slopes are annotated ON the axes here, which is the whole reason this figure
exists separately from the notebook's live cell.

WHY THIS FIGURE IS LOAD-BEARING. It is the empirical settlement of the
local-vs-global error question that section VI of the numeric-integration
handout spends a page on. Both methods are consistent of order 1, so the
GLOBAL error is O(h) and the measured slope is 1 -- not 2. A reader who has
mixed up the normalized local truncation error with the unnormalized per-step
error predicts slope 2 and is contradicted by this picture.

Error norm follows the notebook exactly, so the handout and the website report
the same number:

    Error = ||z_approx - z_exact||_2 / sqrt(N),  N = number of steps

which is a root-mean-square error over the mesh points. Any fixed norm gives
the same slope; this one is quoted because cell 17 of the notebook explains it.

Greyscale: two series, each carrying colour AND linestyle from the house cycle
AND a distinct marker (square = forward, circle = backward), plus a direct
label written onto each curve. The dotted reference triangle is neutral grey
and is not a series. No solver dependency -- pure numpy.
"""

import numpy as np
import matplotlib.pyplot as plt

from _house import label_curve

LAMBDA = 1.0
Z0 = 1.0
T_FINAL = 2.0

# Six halvings, exactly the notebook's list.
STEPS = np.array([1.0, 0.5, 0.25, 0.125, 0.0625, 0.03125])

exact = lambda t: Z0 * np.exp(-LAMBDA * t)


def _mesh(h):
    """Uniform mesh on [0, T_FINAL] with step h. T_FINAL/h is an integer here."""
    n = int(round(T_FINAL / h))
    return n, h * np.arange(n + 1)


def forward_euler(h):
    """z_{i+1} = z_i + h f(t_i, z_i);  f = -LAMBDA z  =>  z_{i+1} = (1 - h L) z_i."""
    n, t = _mesh(h)
    z = np.empty(n + 1)
    z[0] = Z0
    for i in range(1, n + 1):
        z[i] = z[i - 1] - h * LAMBDA * z[i - 1]
    return t, z


def backward_euler(h):
    """z_{i+1} = z_i + h f(t_{i+1}, z_{i+1})  =>  z_{i+1} = z_i / (1 + h L).

    The scalar linear test problem is solved in closed form rather than by a
    Newton iteration. That is not a shortcut that changes the answer: it IS the
    exact solution of the implicit step, so the measured slope is the method's
    and carries no solver tolerance in it.
    """
    n, t = _mesh(h)
    z = np.empty(n + 1)
    z[0] = Z0
    for i in range(1, n + 1):
        z[i] = z[i - 1] / (1.0 + h * LAMBDA)
    return t, z


def rms_error(t, z):
    """||z - z_exact||_2 / sqrt(N), N = number of steps. Notebook cell 17."""
    n = len(t) - 1
    return np.linalg.norm(z - exact(t)) / np.sqrt(n)


def _slope(h, err):
    """Observed order: the slope over the FINEST PAIR of steps.

    This is the notebook's ``calc_slope``, and it is deliberately not a
    least-squares fit over all six points. Order of accuracy is an asymptotic
    statement about h -> 0, and the coarse end of this sweep (h = 1 against a
    problem whose time constant is 1) is nowhere near asymptotic: a fit over
    all six gives 1.15 for forward Euler, which would have the handout print a
    number that is neither 1 nor anything else meaningful. The finest pair
    gives 1.02 and 0.99 -- the correct order 1, and the same numbers the
    website prints.
    """
    return (np.log(err[-1]) - np.log(err[-2])) / (np.log(h[-1]) - np.log(h[-2]))


def make_figure():
    err_f = np.array([rms_error(*forward_euler(h)) for h in STEPS])
    err_b = np.array([rms_error(*backward_euler(h)) for h in STEPS])

    fig, ax = plt.subplots(figsize=(5.4, 4.4))

    ax.loglog(STEPS, err_f, marker="s", label="forward Euler")
    ax.loglog(STEPS, err_b, marker="o", label="backward Euler")

    ax.set_xlim(0.022, 2.6)
    ax.set_ylim(3.0e-3, 1.4)

    # --- the reference triangle: a drawn slope of 1, so the eye can check the
    # measured numbers rather than take them on trust. Neutral grey and dotted,
    # because it is an annotation and not a third method.
    x0, x1 = 0.037, 0.085
    y0 = 0.0040
    y1 = y0 * (x1 / x0)
    ax.plot([x0, x1, x1, x0], [y0, y0, y1, y0],
            color="0.45", linestyle=":", linewidth=1.6, marker="", zorder=1)
    ax.annotate("slope 1", xy=(x1 * 1.12, np.sqrt(y0 * y1)),
                fontsize=12, color="0.35", ha="left", va="center")

    # --- direct labelling with the MEASURED order on the curve itself. This is
    # the information cell 16 prints to stdout and the handout otherwise loses.
    # Both labels sit above their curve in the upper-left half of the axes,
    # which is empty because the data run bottom-left to top-right.
    label_curve(ax, 0.030, 0.62,
                rf"forward Euler: slope $= {_slope(STEPS, err_f):.2f}$",
                ha="left", va="center", fontsize=12)
    label_curve(ax, 0.030, 0.30,
                rf"backward Euler: slope $= {_slope(STEPS, err_b):.2f}$",
                ha="left", va="center", fontsize=12)
    label_curve(ax, 0.030, 0.145,
                r"both are order 1: global error $O(h)$",
                ha="left", va="center", fontsize=12, color="0.35")

    ax.set_xlabel(r"step size $h$")
    ax.set_ylabel(r"global error $\|z_i - z(t_i)\|/\sqrt{N}$")
    ax.set_title(r"$\dot z = -z$, $z_0 = 1$, integrated to $t = 2$", fontsize=14)
    ax.grid(True, which="both", linestyle=":", linewidth=0.6, color="0.85")
    ax.set_axisbelow(True)

    fig.tight_layout()
    return fig
