"""Level sets of a quadratic form, and what conditioning does to them.

    figures/plots/quadratic-form-level-sets.py
        ->  media/figures/quadratic-form-level-sets.{png,pdf}

Authored for `lecture-notes/lectures/linear-algebra.tex` (Part II, L11). That
lecture defines eigenvalues, eigenvectors, positive definiteness and the
condition number and draws NONE of them; `notebooks/6-dev/Math-Primer` has no
executable plot to migrate, so this figure is new rather than a conversion.

Both panels plot the level sets of

    q(x) = 1/2 x^T A x ,   A = V diag(lambda_1, lambda_2) V^T ,   A symmetric PD

for the SAME eigenvectors (a 30-degree rotation) and the same reference level
c* = 2. Only the eigenvalues change. In the eigenvector coordinates z = V^T x
the level set 1/2 x^T A x = c* is

    lambda_1 z_1^2 + lambda_2 z_2^2 = 2 c* ,

an ellipse whose semi-axis along v_i has length sqrt(2 c* / lambda_i) -- that
is, PROPORTIONAL TO 1 / sqrt(lambda_i). So the arrows are not decoration: each
is drawn to exactly that length, and its tip lands on the heavy contour.

    left   lambda = (1, 4),     kappa = 4     axis ratio 2
    right  lambda = (0.25, 25), kappa = 100   axis ratio 10

kappa(A) = lambda_max / lambda_min for symmetric A (Biegler Def. 2.7, p. 22;
Nocedal & Wright p. 605), and the axis ratio is sqrt(kappa). That square root
is the point of the right-hand panel: kappa = 100 is already a visibly
degenerate valley, and the lecture's worked example reaches kappa = 4.5e14.

Greyscale
---------
Contours are grey, the reference level is a heavy black line, and each arrow
carries its symbol AND its eigenvalue as an in-place label, because an arrow
gets no linestyle from the colour cycle (figures/README.md, "Arrows are not
series"). No shaded regions, no colourmap, two series per axes.
"""

import numpy as np
import matplotlib.pyplot as plt

THETA = np.deg2rad(30.0)  # the eigenvectors, shared by both panels
CSTAR = 2.0  # the reference level set, drawn heavy
LIM = 4.6

# Grey companion levels. CSTAR is deliberately absent -- it is drawn separately.
LEVELS = [0.25, 0.75, 4.0, 6.5, 9.5]

PANELS = [
    ((1.0, 4.0), "well conditioned", [(0.45, -0.30), (-0.50, 0.30)]),
    ((0.25, 25.0), "ill conditioned", [(0.10, -0.62), (-0.62, 0.20)]),
]


def eigenbasis(theta):
    """V = [v1 | v2], orthogonal, columns are the principal axes."""
    c, s = np.cos(theta), np.sin(theta)
    return np.array([[c, -s], [s, c]])


def quad(X, Y, lam, V):
    """q(x) = 1/2 x^T A x with A = V diag(lam) V^T, evaluated on a grid."""
    # z = V^T x, so q = 1/2 (lam_1 z_1^2 + lam_2 z_2^2). Cheaper and exact.
    Z1 = V[0, 0] * X + V[1, 0] * Y
    Z2 = V[0, 1] * X + V[1, 1] * Y
    return 0.5 * (lam[0] * Z1**2 + lam[1] * Z2**2)


def _panel(ax, lam, label, offsets):
    V = eigenbasis(THETA)
    g = np.linspace(-LIM, LIM, 401)
    X, Y = np.meshgrid(g, g)
    Q = quad(X, Y, lam, V)

    ax.contour(X, Y, Q, levels=LEVELS, colors="0.62", linewidths=1.0)
    ax.contour(X, Y, Q, levels=[CSTAR], colors="black", linewidths=2.6)

    # Semi-axis along v_i has length sqrt(2 c* / lambda_i): the arrow tip sits
    # ON the heavy contour, which is the whole claim of the figure.
    # The eigenvalues live in the panel title, not on the arrow, so the two
    # in-place labels stay short enough not to collide at either aspect ratio.
    for i, offset in enumerate(offsets):
        v = V[:, i]
        r = np.sqrt(2.0 * CSTAR / lam[i])
        ax.annotate(
            "",
            xy=(r * v[0], r * v[1]),
            xytext=(0.0, 0.0),
            arrowprops=dict(arrowstyle="-|>", color="black", linewidth=1.8,
                            mutation_scale=16, shrinkA=0, shrinkB=0),
            zorder=6,
        )
        ax.annotate(
            r"$v_%d$" % (i + 1),
            xy=(r * v[0] + offset[0], r * v[1] + offset[1]),
            fontsize=14,
            ha="center",
            va="center",
            zorder=7,
            bbox=dict(facecolor="white", edgecolor="none", pad=1.0),
        )

    kappa = max(lam) / min(lam)
    ax.set_title(
        "%s\n" % label
        + r"$\lambda_1=%s,\ \lambda_2=%s,\ \kappa(A)=%g$"
        % (_fmt(lam[0]), _fmt(lam[1]), kappa),
        fontsize=12,
    )
    ax.set_xlim(-LIM, LIM)
    ax.set_ylim(-LIM, LIM)
    ax.set_xticks([-4, -2, 0, 2, 4])
    ax.set_yticks([-4, -2, 0, 2, 4])
    ax.set_xlabel("$x_1$")
    ax.set_aspect("equal", adjustable="box")


def _fmt(x):
    return ("%g" % x)


def make_figure():
    fig, axes = plt.subplots(1, 2, figsize=(9.0, 4.6))
    for ax, (lam, label, offsets) in zip(axes, PANELS):
        _panel(ax, lam, label, offsets)
    axes[0].set_ylabel("$x_2$")

    # One shared statement of what is being plotted, placed where it cannot
    # collide with either ellipse.
    axes[0].annotate(
        r"$q(x)=\frac{1}{2}x^{\mathsf{T}}Ax = 2$",
        xy=(-4.25, -4.25),
        fontsize=12,
        bbox=dict(facecolor="white", edgecolor="0.7", pad=2.5),
    )
    axes[1].annotate(
        r"semi-axis $\propto 1/\sqrt{\lambda_i}$",
        xy=(-4.25, -4.25),
        fontsize=12,
        bbox=dict(facecolor="white", edgecolor="0.7", pad=2.5),
    )

    fig.tight_layout()
    return fig
