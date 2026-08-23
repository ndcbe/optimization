"""Optimal energy arbitrage for a 24 h battery: price, charging, discharging,
state of charge.

    figures/plots/battery-arbitrage.py  ->  media/figures/battery-arbitrage.{png,pdf}

`notebooks/1-dev/Pyomo-Nuts-and-Bolts.ipynb` cells 15/114/115, carried as ONE
three-panel figure because the argument is the alignment between the panels:
the battery charges through the overnight trough and discharges into the two
price peaks, and the state of charge is the running integral of what it did.
Printing any panel alone loses that.

Model (the notebook's, which adds a periodic condition E_N = E_0 to the
lecture's statement):

    max  sum_t  pi_t (d_t - c_t)
    s.t. E_t = E_{t-1} + c_t sqrt(eta) - d_t / sqrt(eta),  t = 1..24
         E_0 = E_24 = 2 MWh,  eta = 0.88
         0 <= c_t, d_t <= 1 MW,   0 <= E_t <= 4 MWh

SOLVER-FREE in the sense the figures README means: no Pyomo and no Ipopt
binary. It IS an optimization, but a linear one, so `scipy.optimize.linprog`
(HiGHS) re-derives it in milliseconds from the committed price file. Optimal
profit is $71.44 for this day.

⚠ This LP has alternative optima -- charging one hour earlier at the same price
costs nothing -- so a different solver may return a different schedule with the
same objective. Ipopt (an interior-point method) tends to return an interior,
"spread out" point; HiGHS returns a vertex. The teaching content is the same:
buy in the trough, sell in the peaks, and end where you started.

COLOUR, restored 2026-08-22 on Prof. Dowling's folio 1-13 note: "Let's move
back to color plots for price, charging, discharging, and energy level. In the
git history, you will find a prior version of the plots that were in color."
That prior version is the pre-figure-pipeline notebook -- `04e85dc4` and
earlier, cells 119/120 of `notebooks/1-dev/Pyomo-Nuts-and-Bolts.ipynb`:

    plt.plot(t, E_control, 'b.-')       # state of charge, BLUE
    plt.step(t_, c_control_, 'r.-')     # charging,        RED
    plt.step(t_, d_control_, 'g.-')     # discharging,     GREEN

Two changes to that scheme, both required by this course's figure policy and
neither of them a change of meaning:

  * matplotlib's bare 'r' / 'g' are the one pair a red-green colour-blind
    reader cannot separate at all. The Okabe-Ito members of the same two hue
    families -- vermillion #D55E00 and bluish green #009E73 -- carry the same
    "red = buying, green = selling" reading and are safe. Blue is #0072B2.
  * vermillion (L* = 54.2) and bluish green (L* = 57.7) collapse to the same
    grey, so charging and discharging ALSO differ in linestyle and in marker.
    Colour is never the only channel; see figures/README.md.

The two power series were previously netted into a single black `c_t - d_t`
trace. They are drawn separately again because Prof. Dowling's note names
charging and discharging as two of the four things he wants in colour, and
because that is what the historical version plotted.
"""

from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import linprog

DATA = Path(__file__).resolve().parents[2] / "notebooks" / "data" / (
    "Prices_DAM_ALTA2G_7_B1.csv"
)

DAY = 1  # day 0 is 1 January 2015; the notebook optimizes day 1
N = 24
ETA = 0.88
E0 = 2.0
C_MAX = D_MAX = 1.0
E_MAX = 4.0

# Okabe-Ito. See the module docstring for why these three and not 'b'/'r'/'g'.
BLUE = "#0072B2"  # L* = 46.0 -- price, and state of charge
VERMILLION = "#D55E00"  # L* = 54.2 -- charging  (was 'r')
BLUISH_GREEN = "#009E73"  # L* = 57.7 -- discharging (was 'g')


def solve_arbitrage(price):
    """Return (c, d, E, profit). Variable order: [c(0..N-1), d, E]."""
    n = price.size
    sq = np.sqrt(ETA)

    # linprog minimizes, so negate the profit objective.
    cost = np.concatenate([price, -price, np.zeros(n)])

    a_eq = np.zeros((n + 1, 3 * n))
    b_eq = np.zeros(n + 1)
    for t in range(n):
        a_eq[t, 2 * n + t] = 1.0  # E_t
        a_eq[t, t] = -sq  # -c_t sqrt(eta)
        a_eq[t, n + t] = 1.0 / sq  # +d_t / sqrt(eta)
        if t > 0:
            a_eq[t, 2 * n + t - 1] = -1.0  # -E_{t-1}
        else:
            b_eq[t] = E0
    a_eq[n, 2 * n + n - 1] = 1.0  # periodic: E_N = E_0
    b_eq[n] = E0

    bounds = [(0.0, C_MAX)] * n + [(0.0, D_MAX)] * n + [(0.0, E_MAX)] * n
    res = linprog(cost, A_eq=a_eq, b_eq=b_eq, bounds=bounds, method="highs")
    assert res.status == 0, res.message
    return res.x[:n], res.x[n : 2 * n], res.x[2 * n :], -res.fun


def make_figure():
    price = np.loadtxt(DATA)[DAY * N : (DAY + 1) * N]
    c, d, energy, profit = solve_arbitrage(price)
    assert np.isclose(energy[-1], E0)

    hours = np.arange(1, N + 1)
    fig, axes = plt.subplots(3, 1, figsize=(6.6, 6.4), sharex=True)
    ax_p, ax_u, ax_e = axes

    # --- panel 1: the data ------------------------------------------------
    ax_p.step(hours, price, where="mid", color=BLUE, linestyle="-")
    ax_p.set_ylabel("price\n[\\$/MWh]")

    # --- panel 2: the decision --------------------------------------------
    # Charging and discharging as two series, as the notebook drew them before
    # the figure pipeline existed. Three redundant channels per series --
    # colour, linestyle, marker -- so neither the colour-blind reader nor the
    # photocopier reader loses the distinction.
    ax_u.step(hours, c, where="mid", color=VERMILLION, linestyle="-",
              linewidth=2.6)
    ax_u.step(hours, d, where="mid", color=BLUISH_GREEN, linestyle="--",
              linewidth=2.6)
    ax_u.axhline(0.0, color="0.7", linewidth=0.8, zorder=0)
    ax_u.set_ylabel("power\n[MW]")
    ax_u.set_ylim(-0.15, 1.95)

    # Direct labelling, in the series colour -- preferred over a legend
    # (figures/README.md). Pinned in axes coordinates rather than to a data
    # point: c_t and d_t both max out at 1 MW and the two labels landed on top
    # of each other when placed at their argmax.
    ax_u.annotate("charge $c_t$ (solid)", xy=(0.02, 0.90),
                  xycoords="axes fraction", color=VERMILLION, fontsize=12,
                  ha="left", va="top")
    ax_u.annotate("discharge $d_t$ (dashed)", xy=(0.98, 0.90),
                  xycoords="axes fraction", color=BLUISH_GREEN, fontsize=12,
                  ha="right", va="top")

    # --- panel 3: the state -----------------------------------------------
    # NOT a step plot: energy is the integral of power, so it is piecewise
    # linear in time. This is the modelling lesson the notebook flags in a
    # comment on cell 114, and it is the reason this panel exists.
    ax_e.plot(np.concatenate([[0], hours]), np.concatenate([[E0], energy]),
              marker="o", markersize=5, color=BLUE, linestyle="-")
    ax_e.set_ylabel("$E_t$\n[MWh]")
    ax_e.set_ylim(-0.3, E_MAX + 0.4)
    ax_e.axhline(E_MAX, color="0.7", linewidth=0.8, linestyle=":", zorder=0)
    ax_e.annotate("$E_{\\max}$", xy=(0.4, E_MAX + 0.08), fontsize=12)

    ax_e.set_xlabel("hour of day")
    ax_e.set_xlim(0, N)
    ax_e.set_xticks(range(0, 25, 3))

    ax_p.set_title(f"optimal profit $\\${profit:,.2f}$ per day", fontsize=14)

    fig.tight_layout()
    return fig
