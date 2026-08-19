"""Optimal energy arbitrage for a 24 h battery: price, power, state of charge.

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

Greyscale: ONE series per panel, all black, told apart by the panel they are
in and by their y-axis label. Nothing is keyed by colour. Shaded charge and
discharge bands were tried and dropped -- twelve bands across three panels read
as noise at handout size, and the vertical alignment of the panels already
makes the point they were meant to make.
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
    fig, axes = plt.subplots(3, 1, figsize=(6.6, 6.0), sharex=True)
    ax_p, ax_u, ax_e = axes

    # --- panel 1: the data ------------------------------------------------
    ax_p.step(hours, price, where="mid", color="black")
    ax_p.set_ylabel("price\n[\\$/MWh]")

    # --- panel 2: the decision --------------------------------------------
    net = c - d
    ax_u.step(hours, net, where="mid")
    ax_u.axhline(0.0, color="0.7", linewidth=0.8, zorder=0)
    ax_u.set_ylabel("$c_t - d_t$\n[MW]")
    ax_u.set_ylim(-1.7, 1.7)
    # Direct labelling: the sign of c - d is the decision, and "charge" above
    # the axis / "discharge" below it says so without a legend.
    ax_u.annotate("charge", xy=(0.4, 1.25), fontsize=12, va="center")
    ax_u.annotate("discharge", xy=(0.4, -1.3), fontsize=12, va="center")

    # --- panel 3: the state -----------------------------------------------
    # NOT a step plot: energy is the integral of power, so it is piecewise
    # linear in time. This is the modelling lesson the notebook flags in a
    # comment on cell 114, and it is the reason this panel exists.
    ax_e.plot(np.concatenate([[0], hours]), np.concatenate([[E0], energy]),
              marker="o", markersize=5, color="black")
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
