"""Concave power-law reactor cost vs the fixed-charge linearization.

    figures/plots/reactor-cost-linearization.py
        -> media/figures/reactor-cost-linearization.{png,pdf}

`notebooks/1-dev/IP.ipynb` cell 35, migrated. That cell is pure numpy with
hard-coded constants -- no Pyomo, no solver -- but it sits DOWNSTREAM of a
deliberate failure at cell 22 ($0^{0.6}$ is undefined), so on a clean run of
the notebook it never executes and the plot is never seen. Rendering it here
fixes that without touching the pedagogical failure.

Source of the numbers: Biegler, Grossmann & Westerberg, *Systematic Methods of
Chemical Process Design*, Prentice-Hall (1997), Example 15.3 "Selection of
Reactors", pp. 509-512 -- eqns (15.5)-(15.6) for the power laws, (15.9) for the
fixed charges, and the $5/kmol feed price on p. 510. The LEFT panel is the
quantitative version of their Figure 15.13, "Fixed charge cost model" (p. 511).

    vessel cost      reactor I    5.5 x^0.6      vs   7.5 + 1.4 x
                     reactor II   4.0 x^0.6      vs   5.5 + 1.0 x
    plus $5/kmol feed             + 5.0 x             + 5.0 x
    ------------------------------------------------------------------
    total            reactor I    5.5 x^0.6+5x   vs   7.5 + 6.4 x
                     reactor II   4.0 x^0.6+5x   vs   5.5 + 6.0 x

The 6.4 and 6.0 on the right are exactly the coefficients BGW's MILP (15.12)
carries, which is why the right panel is the one drawn in the same units as the
objective the lecture writes down. The notebook plots only the right panel; the
left is added because the feed term is linear in both models, so including it
buries the very difference the figure exists to show.

The point the notebook's version does not make: the linearized model is
DISCONTINUOUS at x = 0. The fixed charge is paid only if the unit exists, so
the cost drops to zero there rather than to 7.5 or 5.5. That discontinuity is
the whole reason a binary variable appears. It is drawn with an open circle at
the jump and a filled dot on the axis.

Greyscale: two reactors x two cost models = four curves per panel, keyed by TWO
independent non-colour channels rather than one. Colour separates the reactors
(black L* = 0 vs blue L* = 46, dL* = 46), linestyle separates the models
(solid = concave, dashed = linearized). One legend serves both panels and is
keyed by linestyle as well as colour.

2026-08-21, two changes Prof. Dowling asked for in the margin:

  * "move here to avoid overlap" -- the "fixed charge" callout on the left
    panel sat on top of reactor II's two curves. It is now in the empty band
    above them, and the arrow does the pointing instead of the text.
  * "include inset here", boxing x_r in [0, 5] on the right panel -- so the
    right panel now carries an inset zoomed on the origin. At full scale the
    jump from 0 to bbar_r is a few pixels tall, which hides the one feature
    that makes a binary necessary; in the inset it is the whole picture.
"""

import numpy as np
import matplotlib.pyplot as plt

# BGW Example 15.3, pp. 510-511. Vessel cost coefficients, then the
# fixed-charge linearization of the same vessel, then the shared feed price.
REACTORS = {
    "I": dict(c_power=5.5, c_fixed=7.5, c_slope=1.4, color="black"),
    "II": dict(c_power=4.0, c_fixed=5.5, c_slope=1.0, color="#0072B2"),
}
FEED_PRICE = 5.0  # $/kmol, BGW p. 510
X_MAX = 20.0  # the big-M bound of eqns (15.10)-(15.11), p. 512


def _panel(ax, feed, title):
    """Draw both reactors, both cost models. `feed` adds the $5/kmol feed term."""
    x = np.linspace(0.0, X_MAX, 401)
    x_pos = x[x > 0]
    extra = FEED_PRICE if feed else 0.0

    for name, p in REACTORS.items():
        col = p["color"]

        ax.plot(
            x,
            p["c_power"] * x**0.6 + extra * x,
            color=col,
            linestyle="-",
            label=f"reactor {name}, concave",
        )
        ax.plot(
            x_pos,
            p["c_fixed"] + (p["c_slope"] + extra) * x_pos,
            color=col,
            linestyle="--",
            label=f"reactor {name}, linearized",
        )

        # The jump at the origin: open circle at the fixed charge the linear
        # model would demand, filled dot at the zero cost it actually charges.
        ax.plot(
            [0.0],
            [p["c_fixed"]],
            marker="o",
            markersize=7,
            markerfacecolor="white",
            markeredgecolor=col,
            markeredgewidth=1.6,
            linestyle="none",
            zorder=5,
        )
        ax.plot(
            [0.0],
            [0.0],
            marker="o",
            markersize=6,
            color=col,
            linestyle="none",
            zorder=5,
        )

    ax.set_xlabel("$x_r$ (kmol/hr)")
    ax.set_xlim(0, X_MAX)
    ax.set_ylim(bottom=0)
    ax.set_title(title, fontsize=14)


def _origin_inset(ax):
    """Zoom the jump at x_r = 0 on the right (vessel + feed) panel.

    "include inset here" -- Prof. Dowling, 2026-08-21, boxing x_r in [0, 5].
    The discontinuity is what forces a binary variable into the model and it is
    invisible at full scale.
    """
    x_hi, y_hi = 1.6, 19.0
    axins = ax.inset_axes([0.46, 0.05, 0.52, 0.38])
    x = np.linspace(0.0, x_hi, 200)
    x_pos = x[x > 0]

    for name, p in REACTORS.items():
        col = p["color"]
        axins.plot(x, p["c_power"] * x**0.6 + FEED_PRICE * x,
                   color=col, linestyle="-", linewidth=2.0)
        axins.plot(x_pos, p["c_fixed"] + (p["c_slope"] + FEED_PRICE) * x_pos,
                   color=col, linestyle="--", linewidth=2.0)
        axins.plot([0.0], [p["c_fixed"]], marker="o", markersize=6,
                   markerfacecolor="white", markeredgecolor=col,
                   markeredgewidth=1.6, linestyle="none", zorder=5)
        axins.plot([0.0], [0.0], marker="o", markersize=5, color=col,
                   linestyle="none", zorder=5)

    # The jump itself, measured: a double-headed arrow from zero cost up to
    # the fixed charge reactor II would pay the instant it is switched on.
    axins.annotate("", xy=(0.08, REACTORS["II"]["c_fixed"]), xytext=(0.08, 0.0),
                   arrowprops=dict(arrowstyle="<->", lw=1.1, color="black"))
    axins.annotate("jump $= \\bar b_r$", xy=(0.22, 0.1), fontsize=12,
                   ha="left", va="bottom")
    axins.set_xlim(-0.08, x_hi)
    axins.set_ylim(-0.8, y_hi)
    axins.tick_params(labelsize=11)
    axins.set_xticks([0, 1])
    axins.set_yticks([0, 5, 10, 15])
    ax.indicate_inset_zoom(axins, edgecolor="black", linewidth=0.9, alpha=0.9)
    return axins


def make_figure():
    fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(9.6, 4.2))

    _panel(ax_l, feed=False, title="vessel cost only")
    _panel(ax_r, feed=True, title="vessel $+$ \\$5/kmol feed")

    ax_l.set_ylabel("cost (\\$/hr)")

    # MOVED 2026-08-21: was xytext=(4.2, 3.0), which put the text across
    # reactor II's concave and linearized curves.
    ax_l.annotate(
        "fixed charge:\npaid only if\nthe unit exists",
        xy=(0.35, 7.0),
        xytext=(5.2, 26.0),
        fontsize=12,
        arrowprops=dict(arrowstyle="->", lw=1.1, color="black"),
    )

    _origin_inset(ax_r)
    ax_r.annotate(
        "adding the linear feed\nterm to both models\nhides the difference",
        xy=(11.0, 79.0),
        xytext=(2.0, 105.0),
        fontsize=12,
        arrowprops=dict(arrowstyle="->", lw=1.1, color="black"),
    )

    # One legend for both panels, below them: four entries will not fit inside
    # either axes without covering a curve.
    handles, labels = ax_l.get_legend_handles_labels()
    fig.legend(
        handles,
        labels,
        loc="lower center",
        ncol=2,
        fontsize=12,
        bbox_to_anchor=(0.5, -0.12),
    )

    fig.tight_layout()
    return fig
