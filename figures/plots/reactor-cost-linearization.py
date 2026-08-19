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


def make_figure():
    fig, (ax_l, ax_r) = plt.subplots(1, 2, figsize=(9.6, 4.2))

    _panel(ax_l, feed=False, title="vessel cost only")
    _panel(ax_r, feed=True, title="vessel $+$ \\$5/kmol feed")

    ax_l.set_ylabel("cost (\\$/hr)")

    ax_l.annotate(
        "fixed charge:\npaid only if\nthe unit exists",
        xy=(0.55, 7.5),
        xytext=(4.2, 3.0),
        fontsize=12,
        arrowprops=dict(arrowstyle="->", lw=1.1, color="black"),
    )
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
