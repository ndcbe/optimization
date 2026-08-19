r"""The eigenvalue signature classifies the stationary point.

    figures/plots/quadratic-form-classification.py
        ->  media/figures/quadratic-form-classification.{png,pdf}

`notebooks/6-dev/Math-Primer-2.ipynb` cell 6 defines ``quad_analyze(c, a, B)``,
which builds B from prescribed eigenvalues, locates z*, and draws ONE surface.
Cells 8, 10 and 13 call it three separate times on three separate matrices, so
the notebook never puts the cases side by side -- and side by side is the whole
lesson. This figure is the assembly the notebook does not do: one panel per
eigenvalue signature, same eigenvectors throughout, only the eigenvalues change.

    top left      lambda = ( 3,  1)   positive definite       unique MINIMUM
    top right     lambda = (-3, -1)   negative definite       unique MAXIMUM
    bottom left   lambda = ( 3, -1)   indefinite              SADDLE point
    bottom right  lambda = ( 2,  0)   positive semidefinite   a LINE of minima

which are Biegler's four cases on p. 23 (his fifth, "singular with no
stationary point", is the same B as the bottom right with abar_j != 0, and is
unbounded below -- there is no picture of a minimum to draw, which is exactly
the point the handout's Warning makes in words).

    f(x) = c + a^T x + 1/2 x^T B x ,   B = V diag(lambda) V^T   (Biegler (2.8))

with a = 0 and c = 0 throughout, so x* = 0 in every panel and the four pictures
are directly comparable. V is a 30-degree rotation, deliberately NOT the
coordinate axes: the contour axes line up with the EIGENVECTORS, not with x1
and x2, and a panel drawn with V = I would hide that.

Not the same figure as `quadratic-form-level-sets.py`
-----------------------------------------------------
That one is for L11 (linear-algebra.tex) and varies the CONDITION NUMBER at
fixed sign -- both panels are positive definite and it is about the axis ratio
sqrt(kappa). This one holds the spread roughly fixed and varies the SIGNS. They
answer different questions and neither replaces the other.

Contours, not surfaces
----------------------
The notebook draws ``plot_surface``. A 3-D surface is the better object on
screen, where it can be rotated; in a 2x2 grid at handout width it is four
small ambiguous blobs, and a student cannot write on it. Contours also match
what the rest of this lecture and Biegler's own Figure 2.2 use, and they make
the degenerate case legible -- straight parallel bands -- where a surface makes
it look like a slightly tilted plane.

Greyscale
---------
The notebook uses ``cm.coolwarm``, which is diverging and NOT monotone in
luminance: its two ends are the same grey, so a printed panel cannot be read at
all. Replaced with viridis, truncated to its darker 82% so that white
annotation lines and white labels stay legible at every level (a monotone slice
of a monotone map is still monotone). Measured with scripts/check_greyscale.py's
own lstar(): full viridis runs L* 14.9 -> 90.9, non-decreasing throughout; the
truncation used here runs 14.9 -> 77.8, still non-decreasing; coolwarm BEGINS
AND ENDS AT L* = 37.7, i.e. the notebook's lowest and highest levels print as
exactly the same grey. No colour-coded series: every mark on these axes carries
a text label or a distinct linestyle.

`python3 scripts/check_greyscale.py media/figures/quadratic-form-classification.png`
REPORTS FAIL, and that is the documented over-report, not a defect: image mode
"will NOT know whether those two colours are two data series or one series and a
shaded band" (its own docstring), and every pair it flags here is a pair of
adjacent bands of ONE continuous colourmap. A sequential map whose adjacent
levels were 10 L* apart would not be a sequential map. The rule that actually
governs a colourmap -- monotone in luminance -- is measured above and holds.

numpy only, no solver.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from matplotlib.colors import ListedColormap

# One rotation for all four panels: the eigenvectors never move, only the
# eigenvalues change. 30 degrees so neither eigenvector lies on an axis.
THETA = np.deg2rad(30.0)
V = np.array([[np.cos(THETA), -np.sin(THETA)], [np.sin(THETA), np.cos(THETA)]])

LIM = 3.0                     # plot window, [-LIM, LIM] in both coordinates
NGRID = 300
NLEVELS = 12          # 12, not 18: fewer bands means a bigger luminance
                      # step between adjacent bands in print (dL* 5.4 vs 3.4)

# Truncated viridis: keep the dark 82%, so white lines and white text read at
# every level. Still monotone in luminance, which is the requirement.
_VIRIDIS = cm.get_cmap("viridis") if hasattr(cm, "get_cmap") else plt.get_cmap("viridis")
CMAP = ListedColormap(_VIRIDIS(np.linspace(0.0, 0.82, 256)))

PANELS = [
    ((3.0, 1.0), "positive definite", r"$x^*$ is the unique minimum"),
    ((-3.0, -1.0), "negative definite", r"$x^*$ is the unique maximum"),
    ((3.0, -1.0), "indefinite", r"$x^*$ is a saddle point"),
    ((2.0, 0.0), "positive semidefinite", r"$x^*$ is one of a line of minima"),
]


def quad(lam):
    """f(x) = 1/2 x^T B x with B = V diag(lam) V^T, on the plotting grid."""
    B = V @ np.diag(lam) @ V.T
    g = np.linspace(-LIM, LIM, NGRID)
    X1, X2 = np.meshgrid(g, g)
    F = 0.5 * (B[0, 0] * X1**2 + 2 * B[0, 1] * X1 * X2 + B[1, 1] * X2**2)
    return X1, X2, F


def _eigenvector_line(ax, column, label, style):
    """Draw the eigenvector direction v_j through the origin, and name it.

    White on the viridis fill, and named in place: an annotation line gets no
    identity from the colour cycle, so the text IS its identity in greyscale.
    """
    v = V[:, column]
    t = np.array([-LIM * 1.4, LIM * 1.4])
    ax.plot(t * v[0], t * v[1], color="white", linewidth=2.0, linestyle=style,
            zorder=4, solid_capstyle="butt")
    # Put the label just inside the frame, on the positive end of the direction,
    # pushed sideways off the line so the text does not sit on top of it.
    s = 0.66 * LIM / max(abs(v[0]), abs(v[1]))
    perp = np.array([-v[1], v[0]]) * 0.42
    ax.annotate(label, xy=(s * v[0] + perp[0], s * v[1] + perp[1]),
                color="white", fontsize=13, ha="center", va="center", zorder=6)


def make_figure():
    fig, axes = plt.subplots(2, 2, figsize=(8.4, 8.0))

    for ax, (lam, definiteness, verdict) in zip(axes.ravel(), PANELS):
        X1, X2, F = quad(np.array(lam))
        ax.contourf(X1, X2, F, levels=NLEVELS, cmap=CMAP)
        ax.contour(X1, X2, F, levels=NLEVELS, colors="white",
                   linewidths=0.5, alpha=0.55)

        degenerate = 0.0 in lam
        # v_1 carries lambda_1, v_2 carries lambda_2. In the degenerate panel
        # lambda_2 = 0, so the v_2 line IS the set of minimizers; it is drawn
        # solid and named as such rather than as a bare eigenvector.
        _eigenvector_line(ax, 0, r"$v_1$", (0, (6, 4)))
        if degenerate:
            _eigenvector_line(ax, 1, r"$v_2$: $f$ is flat", "-")
        else:
            _eigenvector_line(ax, 1, r"$v_2$", (0, (1.5, 2.5)))

        # The stationary point. White-edged so it reads against any level.
        ax.plot(0, 0, marker="*", markersize=20, color="white",
                markeredgecolor="black", markeredgewidth=1.0,
                linestyle="none", zorder=7)

        ax.set_xlim(-LIM, LIM)
        ax.set_ylim(-LIM, LIM)
        ax.set_aspect("equal", adjustable="box")
        ax.set_xticks([-2, 0, 2])
        ax.set_yticks([-2, 0, 2])
        ax.set_title(
            rf"$\lambda = ({lam[0]:.0f},\ {lam[1]:.0f})$ — {definiteness}"
            "\n" f"{verdict}",
            fontsize=12,
        )

    for ax in axes[1, :]:
        ax.set_xlabel("$x_1$")
    for ax in axes[:, 0]:
        ax.set_ylabel("$x_2$")

    fig.tight_layout()
    return fig
