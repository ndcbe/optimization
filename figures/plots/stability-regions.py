r"""Regions of absolute stability in the complex h*lambda-plane.

    figures/plots/stability-regions.py  ->  media/figures/stability-regions.{png,pdf}

Three panels, one per method, all on the same axes limits so the shapes are
comparable by eye:

    forward Euler    |1 + h*lambda| <= 1     the DISC of radius 1 centred at -1
    backward Euler   |1 - h*lambda| >= 1     everything OUTSIDE the unit disc at +1
    trapezoid / CN   |(2 + z)/(2 - z)| <= 1  exactly the closed left half-plane

The point of putting them side by side is the A-stability definition, Ascher &
Petzold printed p. 56: "A difference method is A-stable if its region of
absolute stability contains the entire left half-plane of z = h*lambda." Panel
1 plainly does not; panels 2 and 3 plainly do. Backward Euler covers strictly
MORE than the left half-plane -- it is stable on part of the right half-plane
too, where the true solution grows, which is a real (if rarely fatal) defect
and is visible here and nowhere else in the course pack.

NO CONTOURING, NO SAMPLING. Each region is drawn from its closed-form boundary,
so nothing here can be an artefact of a grid resolution. The amplification
factors are derived in section VIII of the numeric-integration handout:

    R_FE(z) = 1 + z          R_BE(z) = 1/(1 - z)      R_CN(z) = (2 + z)/(2 - z)

and |R_CN(z)| <= 1  <=>  |2 + z| <= |2 - z|  <=>  Re(z) <= 0, which is why the
third panel is a half-plane exactly and not approximately.

NOTATION. Everyone else calls the abscissa z. In this course z is the STATE, so
the handout writes the product h*lambda out and calls this "the complex
h lambda-plane" -- Ascher & Petzold's own phrase on printed p. 57.

Greyscale: the shaded regions carry HATCHING, not just a tint (README.md), so
they survive a mono laser printer; a distinct hatch per panel keeps them
distinguishable if the three are ever cropped apart. Boundaries are solid dark
lines. No colour is load-bearing.
"""

import numpy as np
import matplotlib.pyplot as plt

from _house import HATCH_CYCLE, SHADE_ALPHA

XLIM = (-3.4, 3.4)
YLIM = (-2.6, 2.6)

SHADE_FACE = "0.55"


def _hatch_kwargs(index):
    return dict(
        facecolor=SHADE_FACE,
        alpha=SHADE_ALPHA,
        hatch=HATCH_CYCLE[index % len(HATCH_CYCLE)],
        edgecolor=plt.rcParams.get("hatch.color", "black"),
        linewidth=0.0,
        zorder=1,
    )


def _axes_furniture(ax, title, verdict, condition):
    ax.axhline(0.0, color="0.35", linewidth=1.0, zorder=2)
    ax.axvline(0.0, color="0.35", linewidth=1.0, zorder=2)
    ax.set_xlim(*XLIM)
    ax.set_ylim(*YLIM)
    ax.set_aspect("equal")
    ax.set_xlabel(r"$\mathrm{Re}(h\lambda)$")
    # Verdict on the second title line rather than a separate annotation: an
    # annotation placed above the axes collides with the title at this figure
    # size, and the verdict IS what the panel is for.
    ax.set_title(f"{title}\n{verdict}", fontsize=14)
    ax.annotate(condition, xy=(0.5, -0.30), xycoords="axes fraction",
                ha="center", va="top", fontsize=13)


def _disc(centre, radius=1.0, n=400):
    theta = np.linspace(0.0, 2.0 * np.pi, n)
    return centre + radius * np.cos(theta), radius * np.sin(theta)


def make_figure():
    fig, (ax1, ax2, ax3) = plt.subplots(1, 3, figsize=(10.5, 4.0))

    # ---- forward Euler: |1 + h lambda| <= 1, the disc of radius 1 at -1.
    x, y = _disc(-1.0)
    ax1.fill(x, y, **_hatch_kwargs(0))
    ax1.plot(x, y, color="black", linewidth=2.0, marker="", zorder=3)
    _axes_furniture(ax1, "forward Euler", "not A-stable",
                    r"$|1 + h\lambda| \leq 1$")
    ax1.annotate("stable", xy=(-1.0, 0.0), ha="center", va="center",
                 fontsize=12, zorder=4)
    ax1.plot([-2.0], [0.0], marker="|", color="black", markersize=9, zorder=4)
    ax1.annotate(r"$-2$", xy=(-2.55, -0.95), ha="center", va="center",
                 fontsize=12, zorder=4)
    ax1.set_ylabel(r"$\mathrm{Im}(h\lambda)$")

    # ---- backward Euler: |1 - h lambda| >= 1, the COMPLEMENT of the unit disc
    # at +1. Drawn as the full rectangle hatched, then the disc punched out in
    # solid white -- the region is unbounded, so the rectangle IS the picture.
    ax2.add_patch(plt.Rectangle((XLIM[0], YLIM[0]),
                                XLIM[1] - XLIM[0], YLIM[1] - YLIM[0],
                                **_hatch_kwargs(1)))
    x, y = _disc(1.0)
    ax2.fill(x, y, facecolor="white", edgecolor="none", zorder=2.5)
    ax2.plot(x, y, color="black", linewidth=2.0, marker="", zorder=3)
    _axes_furniture(ax2, "backward Euler", "A-stable",
                    r"$|1 - h\lambda| \geq 1$")
    ax2.annotate("stable", xy=(-2.0, 1.6), ha="center", va="center",
                 fontsize=12, zorder=4)
    ax2.annotate("unstable", xy=(1.0, 0.0), ha="center", va="center",
                 fontsize=12, zorder=4)

    # ---- trapezoid / Crank-Nicolson: exactly Re(h lambda) <= 0.
    ax3.add_patch(plt.Rectangle((XLIM[0], YLIM[0]),
                                -XLIM[0], YLIM[1] - YLIM[0],
                                **_hatch_kwargs(2)))
    ax3.plot([0.0, 0.0], list(YLIM), color="black", linewidth=2.0,
             marker="", zorder=3)
    _axes_furniture(ax3, "trapezoid (Crank\u2013Nicolson)", "A-stable",
                    r"$\mathrm{Re}(h\lambda) \leq 0$")
    ax3.annotate("stable", xy=(-1.7, 1.6), ha="center", va="center",
                 fontsize=12, zorder=4)

    fig.tight_layout()
    return fig
