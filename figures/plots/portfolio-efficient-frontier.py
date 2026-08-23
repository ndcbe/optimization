r"""The Markowitz efficient frontier: risk against return, traced by sweeping the
required-return parameter rho.

    figures/plots/portfolio-efficient-frontier.py
        ->  media/figures/portfolio-efficient-frontier.{png,pdf}

Drawn for folio 2-8, Prof. Dowling's typed note: "For the portfolio example,
let's show the input data (stock timeseries) and let's show the Pareto optimal
trade-off. This is a great way to introduce epsilon-constrained methods."

The companion figure with the raw data is `portfolio-index-prices.py`.

THE MODEL, AND WHICH SENSE OF THE RETURN CONSTRAINT
---------------------------------------------------
    min_x  x^T Sigma_r x     s.t.   rbar^T x >= rho,   sum_i x_i = 1,   x >= 0

⚠ The INEQUALITY, `>= rho`. The problem set this example descends from states
the inequality but its solution code writes `== rho`; folio 2-9 marks that
"yes, let's fix this," and `notebooks/1-dev/Portfolio-Optimization.ipynb`
already uses `>=`. The two forms differ exactly where the constraint is
inactive: at rho = 0.0005 the inequality gives a standard deviation of 0.004294
and the equality 0.006241, 45% worse. This figure is the inequality throughout,
and the flat left end of the frontier IS that fact drawn -- see below.

Data: `notebooks/data/Stock_Data.csv`, 1,259 daily closes -> 1,258 one-day
returns for DJI, GSPC, IXIC, RUT and VIX. rbar and Sigma_r are the sample mean
and sample covariance, exactly as the notebook computes them.

SOLVER-FREE, and DETERMINISTIC. This is a small convex QP, so
`scipy.optimize.minimize(method="SLSQP")` with the analytic gradient re-derives
each point in milliseconds; no Pyomo, no Ipopt binary, per figures/README.md.
The start point is the equal-weight portfolio, fixed, so there is nothing random
to seed. Reproduces the lecture's table to the digits it prints:

    rho       sqrt(z*)     lecture table
    0.0005    0.004294     0.004295   (constraint INACTIVE; see below)
    0.0008    0.004580     0.004580
    0.0010    0.006010     0.006010
    0.0020    0.033663     0.033663
    0.0037    0.085332     0.085332

WHY THE FRONTIER IS FLAT ON THE LEFT
------------------------------------
The minimum-variance portfolio has standard deviation 0.004294 per day and
already returns 0.000678 per day. For any rho below 0.000678 the constraint
rbar^T x >= rho is slack, the solver returns that same portfolio, and the
frontier is a single point rather than a curve. So the efficient frontier
proper starts at (0.004294, 0.000678); everything below is dominated. That
corner is the lecture's "an inequality constraint you wrote down need not cost
you a degree of freedom," and it is only there because the constraint is an
inequality.

THE EPSILON-CONSTRAINT READING
------------------------------
Two objectives -- minimize risk, maximize return -- and no single answer. The
epsilon-constraint method optimizes one and constrains the other at a level
epsilon, here rho, then sweeps epsilon. Each solve is one point of the Pareto
set; the curve is the trade-off. One rho is drawn out in full on the figure to
make that mechanical.

Greyscale: the frontier is one series. The five individual indices are open
markers with direct labels, the swept points are filled markers on the curve,
and the epsilon-constraint construction is black rules and arrows. Nothing is
keyed by colour.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import minimize

DATA = Path(__file__).resolve().parents[2] / "notebooks" / "data" / "Stock_Data.csv"

NAMES = {
    "DJI": "Dow Jones",
    "GSPC": "S&P 500",
    "IXIC": "NASDAQ",
    "RUT": "Russell 2000",
    "VIX": "VIX",
}

# The five rho values the lecture tabulates, marked on the curve.
RHO_MARKS = [0.0008, 0.0010, 0.0020, 0.0037]

# The rho drawn out in full as the epsilon-constraint construction.
RHO_DEMO = 0.0020

BLUE = "#0072B2"  # Okabe-Ito


def _load():
    returns = pd.read_csv(DATA).pct_change().dropna()
    return returns.mean().to_numpy(), returns.cov().to_numpy(), list(returns.columns)


def solve_qp(rho, mu, cov):
    """min x'Sigma x  s.t.  mu'x >= rho, sum x = 1, x >= 0.  Returns (sd, x)."""
    n = mu.size
    res = minimize(
        lambda x: x @ cov @ x,
        np.full(n, 1.0 / n),  # equal weights: fixed, so nothing is random
        jac=lambda x: 2.0 * cov @ x,
        bounds=[(0.0, None)] * n,
        constraints=[
            {"type": "eq", "fun": lambda x: x.sum() - 1.0,
             "jac": lambda x: np.ones(n)},
            {"type": "ineq", "fun": lambda x: mu @ x - rho, "jac": lambda x: mu},
        ],
        method="SLSQP",
        options={"ftol": 1e-16, "maxiter": 500},
    )
    assert res.success, f"QP failed at rho = {rho}: {res.message}"
    return np.sqrt(max(res.fun, 0.0)), res.x


def make_figure():
    mu, cov, tickers = _load()

    # The minimum-variance portfolio: the return constraint dropped entirely.
    # A rho far below any achievable return is the same thing and needs no
    # second code path. (-inf is NOT the same thing: SLSQP evaluates
    # mu@x - rho and inf - inf is a nan, which it reports as an incompatible
    # constraint.)
    sd_min, x_min = solve_qp(-1.0, mu, cov)
    ret_min = float(mu @ x_min)

    # Sweep rho over the range in which it BINDS: from the minimum-variance
    # return up to the largest single-asset mean, beyond which the problem is
    # infeasible (no short selling).
    rho_grid = np.linspace(ret_min, mu.max(), 60)
    sds = np.array([solve_qp(r, mu, cov)[0] for r in rho_grid])

    fig, ax = plt.subplots(figsize=(7.6, 5.2))

    ax.plot(sds, rho_grid, color=BLUE, linestyle="-", linewidth=2.6, zorder=3)

    sd_each = np.sqrt(np.diag(cov))

    def draw_assets(axis, placement, fontsize=11):
        """The five indices as open squares, directly labelled.

        Every one of them is to the RIGHT of the frontier at its own return:
        that gap is diversification, and it is the reason to solve the QP at
        all. ``placement`` maps ticker -> (dx, dy, ha) in points; a ticker
        absent from it is not drawn on this axis.
        """
        for ticker, s, m in zip(tickers, sd_each, mu):
            if ticker not in placement:
                continue
            dx, dy, ha = placement[ticker]
            axis.plot([s], [m], marker="s", markersize=8,
                      markerfacecolor="white", markeredgecolor="black",
                      markeredgewidth=1.4, linestyle="none", zorder=4)
            axis.annotate(NAMES[ticker], xy=(s, m), xytext=(dx, dy),
                          textcoords="offset points", fontsize=fontsize,
                          ha=ha, va="center")

    draw_assets(ax, {"VIX": (-10, 0, "right")})

    # --- the tabulated rho values ------------------------------------------
    for rho in RHO_MARKS:
        sd, _ = solve_qp(rho, mu, cov)
        ax.plot([sd], [rho], marker="o", markersize=7, color="black",
                linestyle="none", zorder=5)

    # --- the minimum-variance corner ---------------------------------------
    ax.plot([sd_min], [ret_min], marker="o", markersize=10, color="black",
            linestyle="none", zorder=5)

    # --- INSET: the four equity indices and the corner of the frontier ------
    # VIX is ten times as volatile as any of the others, so on one linear axis
    # the whole interesting part of the frontier -- and four of the five data
    # points -- collapses into the bottom-left corner. The first render had all
    # four labels printed on top of one another. The inset is the fix, and it
    # is also where the min-variance argument is legible.
    axin = ax.inset_axes([0.52, 0.07, 0.45, 0.40])
    x_in = (0.0028, 0.0155)
    y_in = (0.00030, 0.00120)
    keep = rho_grid <= y_in[1]
    axin.plot(sds[keep], rho_grid[keep], color=BLUE, linestyle="-",
              linewidth=2.2, zorder=3)
    # ha chosen per point: the four sit within 0.0024 of each other in risk and
    # within 0.00025 in return, so every label needs its own side.
    draw_assets(
        axin,
        {
            "DJI": (-10, -9, "right"),
            "GSPC": (-10, 10, "right"),
            "RUT": (10, 0, "left"),
            "IXIC": (10, 0, "left"),
        },
        fontsize=10,
    )
    axin.plot([sd_min], [ret_min], marker="o", markersize=9, color="black",
              linestyle="none", zorder=5)
    axin.annotate("min-variance\nportfolio", xy=(sd_min, ret_min),
                  xytext=(0.34, 0.88), textcoords="axes fraction", fontsize=10,
                  ha="left", va="top", linespacing=1.05,
                  arrowprops=dict(arrowstyle="->", color="black",
                                  linewidth=1.0, shrinkB=7.0))
    for rho in (0.0008, 0.0010):
        sd, _ = solve_qp(rho, mu, cov)
        axin.plot([sd], [rho], marker="o", markersize=6, color="black",
                  linestyle="none", zorder=5)
    axin.set_xlim(*x_in)
    axin.set_ylim(*y_in)
    axin.tick_params(labelsize=9)
    axin.set_xticks([0.004, 0.008, 0.012])
    axin.set_yticks([0.0005, 0.0010])
    ax.indicate_inset_zoom(axin, edgecolor="0.4", linewidth=1.0)

    ax.annotate(
        f"$\\sigma = {sd_min:.6f}$ at return ${ret_min:.6f}$;\n"
        r"below that, $\bar{r}^{\top} x \geq \rho$ is INACTIVE",
        xy=(0.05, 0.96),
        xycoords="axes fraction",
        fontsize=10.5,
        ha="left",
        va="top",
        linespacing=1.15,
    )

    # --- one epsilon-constraint solve, drawn out ---------------------------
    sd_demo, _ = solve_qp(RHO_DEMO, mu, cov)
    ax.axhline(RHO_DEMO, color="0.45", linewidth=1.0, linestyle="--", zorder=1)
    ax.annotate(
        f"$\\rho = {RHO_DEMO:.4f}$",
        xy=(ax.get_xlim()[0], RHO_DEMO),
        xytext=(6, 5),
        textcoords="offset points",
        fontsize=11,
        ha="left",
        va="bottom",
        color="0.25",
    )
    ax.annotate(
        "fix $\\rho$, minimize risk:\none point of the Pareto set",
        xy=(sd_demo, RHO_DEMO),
        xytext=(0.10, 0.72),
        textcoords="axes fraction",
        fontsize=10.5,
        ha="left",
        va="center",
        linespacing=1.15,
        arrowprops=dict(arrowstyle="->", color="black", linewidth=1.1,
                        shrinkB=7.0),
    )

    ax.set_xlabel("risk: std. dev. of return [per day]")
    ax.set_ylabel("return: $\\bar{r}^{\\top} x$ [per day]")
    ax.set_xlim(0.0, 1.06 * max(sd_each.max(), sds.max()))
    ax.set_ylim(0.0, 1.10 * mu.max())

    fig.tight_layout()
    return fig
