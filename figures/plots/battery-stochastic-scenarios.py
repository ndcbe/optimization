r"""Two-stage battery arbitrage under price uncertainty: the scenario set, the
here-and-now bid, and what non-anticipativity does to the state of charge.

    figures/plots/battery-stochastic-scenarios.py
        ->  media/figures/battery-stochastic-scenarios.{png,pdf}

Drawn for folio 1-17, where the purple *Figure -- future work* box carries blue
ink "let's include" and red ink "we can sample 20 weeks to get scenarios."

The model, the scenario construction and the numbers below all come from
`notebooks/1-dev/Pyomo-Nuts-and-Bolts.ipynb` (cells 129-140), which builds this
in Pyomo. This script is NOT a second modelling effort: it re-solves the same
LP with `scipy.optimize.linprog` (HiGHS) so the figure pipeline needs no solver
binary, per figures/README.md, and it is a genuine cross-check of the notebook
because the two go through different solvers.

THE MODEL
---------
    max  sum_s pi_s sum_t p[s,t] (d[s,t] - c[s,t]) dt
    s.t. E[s,t] = E[s,t-1] + (c[s,t] sqrt(eta) - d[s,t]/sqrt(eta)) dt
         E[s,-1] = E[s,T-1] = E0 = 0
         c[s,t] = c[0,t] and d[s,t] = d[0,t]  for all s, t < n_commit
         0 <= c, d <= 1 MW,   0 <= E <= 4 MWh,   eta = 0.88,  dt = 1 h

The third block is non-anticipativity: the first `n_commit` hours are ONE
schedule, committed before the scenario is revealed. Everything after may react.

SCENARIOS. |T| = 168 h (one week), |S| = 20 weeks drawn without replacement
from the 52 whole weeks in the CAISO year, `np.random.default_rng(0)` -- the
SAME seed and the same sampler as the notebook, so the two show the same twenty
weeks. An unseeded scenario set gives a different figure every build.

NUMBERS, and they agree with the notebook's Pyomo + CBC solve:

    n_commit = 1     expected profit  $554.28
    n_commit = 24    expected profit  $540.97   (2.45% below perfect foresight)
    perfect foresight (each week solved knowing its own prices)   $554.53

`n_commit = 24` is what the figure draws, because that is a real day-ahead bid
and because at `n_commit = 1` there are 167 hours left to recover from a bad
guess -- the commitment has to bite before uncertainty costs anything visible.

WHAT THE THREE PANELS SAY
-------------------------
(a) the scenario set: twenty weeks of prices that actually happened, and their
    mean. This is the "ensemble of price forecasts" folio 1-16 asks for.
(b) the committed day, and folio 1-17's request for "the deterministic schedule
    and the here-and-now schedule on the same axes." The DETERMINISTIC schedule
    solves the same LP once against the mean price -- the expected-value
    problem, one forecast treated as truth. The HERE-AND-NOW schedule is the
    first stage of the stochastic program.

    🔴 ON THIS INSTANCE THEY ARE IDENTICAL, to 1.1e-16 MW, and the figure says
    so rather than hiding it. The value of the stochastic solution is therefore
    $0.00 here: the expected-value bid is already optimal against the full
    scenario set. This is a fact about the instance, not a theorem and not a
    bug -- at n_commit = 6 the same two schedules differ by 0.472 MW. It is
    worth a sentence in class, because the reflex is to assume the stochastic
    program must move the answer, and the only way to know is to solve both.
(c) the state of charge over the first 48 hours, all twenty scenarios. Through
    the committed day they lie on ONE trajectory -- that is non-anticipativity,
    visible rather than asserted -- and they fan out the moment the commitment
    ends.

Greyscale: in (a) and (c) the twenty scenarios are a single thin grey ensemble,
not twenty series, so there is nothing to tell apart. The two schedules in (b)
differ in colour, in linestyle AND in direct label. The commitment boundary is
a black rule in both (b) and (c).
"""

from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import linprog
from scipy.sparse import coo_matrix

DATA = Path(__file__).resolve().parents[2] / "notebooks" / "data" / (
    "Prices_DAM_ALTA2G_7_B1.csv"
)

SEED = 0  # the notebook's seed. Do not change without changing it there too.
HOURS_PER_WEEK = 168
N_SCENARIOS = 20
N_COMMIT = 24

ETA = 0.88
E0 = 0.0
C_MAX = D_MAX = 1.0
E_MAX = 4.0
DT = 1.0

BLUE = "#0072B2"  # Okabe-Ito -- the here-and-now (stochastic) schedule
VERMILLION = "#D55E00"  # the deterministic (expected-value) schedule
ENSEMBLE = "0.62"  # the twenty scenarios: one grey ensemble, not 20 series


def sample_scenarios():
    """The notebook's cell 129, verbatim in effect: 20 distinct weeks, seed 0."""
    prices_year = np.loadtxt(DATA)
    n_weeks = len(prices_year) // HOURS_PER_WEEK
    rng = np.random.default_rng(SEED)
    weeks = np.sort(rng.choice(n_weeks, size=N_SCENARIOS, replace=False))
    return np.array(
        [prices_year[w * HOURS_PER_WEEK : (w + 1) * HOURS_PER_WEEK] for w in weeks]
    )


def solve_stochastic(price, n_commit=1, prob=None):
    """Solve the two-stage LP. `price` has shape (|S|, |T|).

    Variable layout, flattened: c[s, t] then d[s, t] then E[s, t], each
    row-major in (s, t). Returns (expected_profit, c, d, E) with the three
    arrays shaped (|S|, |T|).
    """
    n_s, n_t = price.shape
    n = n_s * n_t
    sq = np.sqrt(ETA)
    if prob is None:
        prob = np.full(n_s, 1.0 / n_s)

    def ic(s, t):
        return s * n_t + t

    def idd(s, t):
        return n + s * n_t + t

    def ie(s, t):
        return 2 * n + s * n_t + t

    # linprog minimizes; the objective is expected profit, so negate it.
    cost = np.zeros(3 * n)
    for s in range(n_s):
        for t in range(n_t):
            cost[ic(s, t)] = prob[s] * price[s, t] * DT
            cost[idd(s, t)] = -prob[s] * price[s, t] * DT

    rows, cols, vals, rhs = [], [], [], []

    def add_row(entries, b):
        r = len(rhs)
        for col, v in entries:
            rows.append(r)
            cols.append(col)
            vals.append(v)
        rhs.append(b)

    for s in range(n_s):
        for t in range(n_t):
            entries = [(ie(s, t), 1.0), (ic(s, t), -sq * DT), (idd(s, t), DT / sq)]
            if t > 0:
                entries.append((ie(s, t - 1), -1.0))
                add_row(entries, 0.0)
            else:
                add_row(entries, E0)
        add_row([(ie(s, n_t - 1), 1.0)], E0)  # periodic: end where you started

    # Non-anticipativity. Rather than introducing first-stage variables and
    # equating them, tie every scenario's committed hours to scenario 0's --
    # the same feasible set with 2*n_commit fewer columns.
    for s in range(1, n_s):
        for t in range(min(n_commit, n_t)):
            add_row([(ic(s, t), 1.0), (ic(0, t), -1.0)], 0.0)
            add_row([(idd(s, t), 1.0), (idd(0, t), -1.0)], 0.0)

    a_eq = coo_matrix((vals, (rows, cols)), shape=(len(rhs), 3 * n)).tocsr()
    bounds = (
        [(0.0, C_MAX)] * n + [(0.0, D_MAX)] * n + [(0.0, E_MAX)] * n
    )
    res = linprog(cost, A_eq=a_eq, b_eq=np.array(rhs), bounds=bounds,
                  method="highs")
    assert res.status == 0, res.message
    x = res.x
    return (
        -res.fun,
        x[:n].reshape(n_s, n_t),
        x[n : 2 * n].reshape(n_s, n_t),
        x[2 * n :].reshape(n_s, n_t),
    )


def make_figure():
    price = sample_scenarios()
    mean_price = price.mean(axis=0)

    # (i) the stochastic program, committing the first day
    profit_sp, c_sp, d_sp, e_sp = solve_stochastic(price, n_commit=N_COMMIT)

    # (ii) the DETERMINISTIC schedule: one forecast -- the scenario mean --
    # treated as if it were the truth. This is the expected-value problem.
    _, c_ev, d_ev, _ = solve_stochastic(mean_price[None, :], n_commit=1)

    hours = np.arange(HOURS_PER_WEEK)
    commit_h = np.arange(N_COMMIT)

    fig, axes = plt.subplots(3, 1, figsize=(7.4, 8.4))
    ax_p, ax_u, ax_e = axes

    # --- (a) the scenario set ---------------------------------------------
    for s in range(N_SCENARIOS):
        # linestyle pinned: without it the prop_cycle dashes each of the
        # twenty differently, which reads as twenty SERIES rather than as one
        # ensemble -- and there is nothing here to tell apart.
        ax_p.plot(hours, price[s], color=ENSEMBLE, linestyle="-",
                  linewidth=0.7, alpha=0.75, zorder=2)
    ax_p.plot(hours, mean_price, color="black", linestyle="-", linewidth=2.2,
              zorder=4)
    ax_p.annotate(f"{N_SCENARIOS} sampled weeks", xy=(0.02, 0.95),
                  xycoords="axes fraction", fontsize=11, color="0.35",
                  ha="left", va="top")
    ax_p.annotate("scenario mean", xy=(0.02, 0.80), xycoords="axes fraction",
                  fontsize=11, color="black", ha="left", va="top")
    ax_p.set_ylabel("price\n[\\$/MWh]")
    ax_p.set_xlim(0, HOURS_PER_WEEK)
    ax_p.set_xticks(range(0, HOURS_PER_WEEK + 1, 24))
    ax_p.set_xlabel("hour of the week")
    ax_p.set_title("(a) the scenario set", fontsize=13)

    # --- (b) the committed day: deterministic vs here-and-now --------------
    net_ev = (c_ev[0] - d_ev[0])[:N_COMMIT]
    net_sp = (c_sp[0] - d_sp[0])[:N_COMMIT]
    # Solid blue wide, dashed vermillion narrower ON TOP. On this instance the
    # two schedules are IDENTICAL to machine precision, so the only honest way
    # to draw them is one showing through the other's dashes.
    ax_u.step(commit_h, net_sp, where="mid", color=BLUE, linestyle="-",
              linewidth=4.2, zorder=3, solid_joinstyle="miter")
    ax_u.step(commit_h, net_ev, where="mid", color=VERMILLION, linestyle="--",
              linewidth=1.8, zorder=4)
    ax_u.axhline(0.0, color="0.7", linewidth=0.8, zorder=0)
    ax_u.annotate("here-and-now (stochastic), thick solid", xy=(0.02, 0.96),
                  xycoords="axes fraction", fontsize=10.5, color=BLUE,
                  ha="left", va="top")
    ax_u.annotate("deterministic (mean forecast), thin dashed",
                  xy=(0.02, 0.83), xycoords="axes fraction", fontsize=10.5,
                  color=VERMILLION, ha="left", va="top")
    gap = float(np.max(np.abs(net_sp - net_ev)))
    ax_u.annotate(
        "on this instance the two coincide exactly (max difference\n"
        f"${gap:.0e}$ MW): here, knowing the distribution buys nothing\n"
        "over the mean. At $n_{\\mathrm{commit}} = 6$ they differ by 0.47 MW.",
        xy=(0.02, 0.03), xycoords="axes fraction", fontsize=10,
        ha="left", va="bottom", linespacing=1.15,
    )
    ax_u.set_ylabel("$c_t - d_t$\n[MW]")
    ax_u.set_xlim(0, N_COMMIT - 1)
    ax_u.set_xticks(range(0, N_COMMIT, 3))
    ax_u.set_xlabel("hour of the committed day")
    # Extra room BELOW the trace for the coincidence note; the schedule
    # itself never goes under -1 MW.
    ax_u.set_ylim(-3.4, 2.75)
    ax_u.set_yticks([-2, -1, 0, 1, 2])
    ax_u.set_title("(b) the first-stage bid", fontsize=13)

    # --- (c) non-anticipativity, made visible ------------------------------
    horizon = 48
    for s in range(N_SCENARIOS):
        ax_e.plot(np.arange(horizon), e_sp[s, :horizon], color=ENSEMBLE,
                  linestyle="-", linewidth=1.0, alpha=0.8, zorder=2)
    ax_e.axvline(N_COMMIT - 1, color="black", linestyle=":", linewidth=1.4,
                 zorder=3)
    ax_e.annotate("commitment ends", xy=(N_COMMIT - 1, 0.96),
                  xycoords=("data", "axes fraction"), xytext=(6, 0),
                  textcoords="offset points", fontsize=11, ha="left", va="top")
    ax_e.annotate("one trajectory:\nall 20 scenarios agree", xy=(0.03, 0.96),
                  xycoords="axes fraction", fontsize=10.5, ha="left", va="top",
                  linespacing=1.1)
    ax_e.set_ylabel("$E_{t,s}$\n[MWh]")
    ax_e.set_xlim(0, horizon - 1)
    ax_e.set_xticks(range(0, horizon, 6))
    ax_e.set_xlabel("hour of the week")
    ax_e.set_title("(c) state of charge, first 48 h", fontsize=13)

    fig.suptitle(
        f"expected profit $\\${profit_sp:,.2f}$ committing the first "
        f"{N_COMMIT} hours",
        fontsize=13,
    )
    fig.tight_layout(rect=(0.0, 0.0, 1.0, 0.975))
    return fig
