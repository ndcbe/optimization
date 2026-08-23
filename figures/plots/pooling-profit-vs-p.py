r"""Milk pooling: profit as a function of the pool composition p, and the three
local maxima you cannot reformulate away.

    figures/plots/pooling-profit-vs-p.py
        ->  media/figures/pooling-profit-vs-p.{png,pdf}

Drawn for folio 2-13, "Nonconvexity you cannot reformulate away," where Prof.
Dowling wrote in red: "let's show this in a figure."

Source of the model and the data: `notebooks/1-dev/Milk-Pooling.ipynb`, cells 4
and 12, adapted from notebook 5.1 of Postek, Zocca, Gromicho & Kantor,
*Hands-On Mathematical Optimization with Python* (the late Jeff Kantor's
example, MIT licence), which is in turn the Haverly (1978) pooling benchmark.

WHY THIS FIGURE IS A SWEEP AND NOT A SOLVE
------------------------------------------
The full model is a bilinear NLP: the products p*y_k and p*sum_r x_r are what
make it nonconvex. FIX p and every remaining term is linear, so the restricted
problem is an LP and its optimal value is a function of p alone. That function
is what is plotted. It is exactly the argument the lecture makes -- the
nonconvexity lives in one scalar -- and it means this script needs no Pyomo and
no Ipopt binary, only `scipy.optimize.linprog` (HiGHS), per figures/README.md.

WHAT WAS VERIFIED, NOT ASSUMED
------------------------------
The lecture says the profit has three local maxima "near p = 0.033, 0.040 and
0.045". Swept at 1e-5 over the model's own bounds on p, [0.033, 0.050]:

    p = 0.033   profit 102,833.33   <- the LOWER BOUND on p, not an interior
                                       stationary point. It is a local (and the
                                       global) maximum, and it is a boundary one.
    p = 0.040   profit 100,088.24   <- interior, a KINK: the profit rises to it
                                       and falls away, with a corner at the top
    p = 0.045   profit 101,392.16   <- interior, and a JUMP DISCONTINUITY:
                                       87,275.65 just below, 101,392.16 at and
                                       just above

So all three exist, at the stated values. Two things the lecture's phrasing does
not say, and the figure now shows:

  * the best of the three sits ON the lower bound, so it is not found by setting
    a derivative to zero;
  * the function is neither smooth nor even continuous. The kink at p = 0.040 is
    Customer 3's minimum fat fraction (0.040) and the jump at p = 0.045 is
    Customer 1's (0.045): at p = 0.045 the pool on its own can finally satisfy
    the largest, best-paying customer, and 6,000 units of demand become servable
    in one step. The discontinuity is drawn as a discontinuity -- two segments,
    an open circle for the limit from the left and a filled one for the value
    attained -- because joining them with a line would draw a claim that is
    false.

The two Ipopt runs the lecture tabulates are marked where they LAND:

    bound_frac = 0.01  starts p at 0.033170, converges to p = 0.0330, 102,833
    bound_frac = 0.50  starts p at 0.041500, converges to p = 0.0450, 101,392

and the second is the point of the whole example: it starts nearer the maximum
at 0.040 than the one at 0.045, and walks to 0.045 anyway. The starting point is
twelve numbers, not one.

Greyscale: the profit curve is one series. The three maxima are filled black
circles with direct labels; the open circle at p = 0.045 is the value NOT
attained; the two triangles on the x-axis are the two Ipopt starting values,
each marked p_0. Nothing is keyed by colour.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import FuncFormatter
from scipy.optimize import linprog

# --- the instance, copied from Milk-Pooling.ipynb cell 4 --------------------
LOCAL = ["Farm A", "Farm B"]
REMOTE = ["Farm C", "Farm D"]
CUSTOMERS = ["Customer 1", "Customer 2", "Customer 3"]

FAT = {"Farm A": 0.045, "Farm B": 0.030, "Farm C": 0.033, "Farm D": 0.050}
COST = {"Farm A": 45.0, "Farm B": 42.0, "Farm C": 37.0, "Farm D": 45.0}
PRICE = {"Customer 1": 52.0, "Customer 2": 48.0, "Customer 3": 50.0}
DEMAND = {"Customer 1": 6000.0, "Customer 2": 2500.0, "Customer 3": 4000.0}
MIN_FAT = {"Customer 1": 0.045, "Customer 2": 0.030, "Customer 3": 0.040}

# The model's own bounds on p: a pool is no richer than its richest input and
# no leaner than its leanest.
P_LO = min(FAT[r] for r in REMOTE)  # 0.033
P_HI = max(FAT[r] for r in REMOTE)  # 0.050

# Variable layout: z[l, k] (|L||K|), then x[r] (|R|), then y[k] (|K|).
NZ = len(LOCAL) * len(CUSTOMERS)
NX = len(REMOTE)
NY = len(CUSTOMERS)
NVAR = NZ + NX + NY

BLUE = "#0072B2"  # Okabe-Ito


def _iz(l, k):
    return LOCAL.index(l) * len(CUSTOMERS) + CUSTOMERS.index(k)


def _ix(r):
    return NZ + REMOTE.index(r)


def _iy(k):
    return NZ + NX + CUSTOMERS.index(k)


def profit_at_fixed_p(p):
    """Optimal profit of the pooling model with the pool composition fixed.

    With p fixed this is a linear program:

        max  sum_{l,k} (pi_k - kappa_l) z_{l,k} + sum_k pi_k y_k
                                                - sum_r kappa_r x_r
        s.t. sum_l z_{l,k} + y_k <= d_k                          (demand)
             sum_r x_r = sum_k y_k                               (pool balance)
             sum_r phi_r x_r = p sum_r x_r                       (pool fat)
             sum_l (phi_l - phi^min_k) z_{l,k}
                   + (p - phi^min_k) y_k >= 0                    (blend quality)
             z, x >= 0,  0 <= y_k <= d_k

    Returns np.nan if the LP is infeasible, so a sweep can be plotted as is.
    """
    # linprog minimizes.
    c = np.zeros(NVAR)
    for l in LOCAL:
        for k in CUSTOMERS:
            c[_iz(l, k)] = -(PRICE[k] - COST[l])
    for k in CUSTOMERS:
        c[_iy(k)] = -PRICE[k]
    for r in REMOTE:
        c[_ix(r)] = COST[r]

    a_ub, b_ub = [], []
    for k in CUSTOMERS:  # demand
        row = np.zeros(NVAR)
        for l in LOCAL:
            row[_iz(l, k)] = 1.0
        row[_iy(k)] = 1.0
        a_ub.append(row)
        b_ub.append(DEMAND[k])
    for k in CUSTOMERS:  # blend quality, negated into <= form
        row = np.zeros(NVAR)
        for l in LOCAL:
            row[_iz(l, k)] = -(FAT[l] - MIN_FAT[k])
        row[_iy(k)] = -(p - MIN_FAT[k])
        a_ub.append(row)
        b_ub.append(0.0)

    a_eq, b_eq = [], []
    row = np.zeros(NVAR)  # pool balance
    for r in REMOTE:
        row[_ix(r)] = 1.0
    for k in CUSTOMERS:
        row[_iy(k)] = -1.0
    a_eq.append(row)
    b_eq.append(0.0)
    row = np.zeros(NVAR)  # pool fat balance, with p a constant
    for r in REMOTE:
        row[_ix(r)] = FAT[r] - p
    a_eq.append(row)
    b_eq.append(0.0)

    bounds = (
        [(0.0, None)] * NZ
        + [(0.0, None)] * NX
        + [(0.0, DEMAND[k]) for k in CUSTOMERS]
    )
    res = linprog(
        c,
        A_ub=np.array(a_ub),
        b_ub=np.array(b_ub),
        A_eq=np.array(a_eq),
        b_eq=np.array(b_eq),
        bounds=bounds,
        method="highs",
    )
    return -res.fun if res.status == 0 else np.nan


# The two breakpoints are the two distinct customer fat requirements that lie
# inside [P_LO, P_HI]. Derived from the data, not hard-coded, so the figure
# follows the instance if the instance ever changes.
BREAKS = sorted({v for v in MIN_FAT.values() if P_LO < v < P_HI})


def make_figure():
    eps = 1e-7
    # One segment per interval between breakpoints, so the discontinuity at
    # p = 0.045 is drawn as a discontinuity rather than as a steep line.
    edges = [P_LO] + BREAKS + [P_HI]
    segments = []
    for lo, hi in zip(edges[:-1], edges[1:]):
        grid = np.linspace(lo, hi - eps, 400)
        segments.append((grid, np.array([profit_at_fixed_p(p) for p in grid])))
    # The right endpoint of the last segment is attained, so include it.
    grid, vals = segments[-1]
    segments[-1] = (
        np.append(grid, P_HI),
        np.append(vals, profit_at_fixed_p(P_HI)),
    )

    fig, ax = plt.subplots(figsize=(7.2, 4.6))

    for grid, vals in segments:
        ax.plot(grid, vals, color=BLUE, linestyle="-", linewidth=2.4)

    # --- the three local maxima -------------------------------------------
    maxima = [(P_LO, profit_at_fixed_p(P_LO))] + [
        (b, profit_at_fixed_p(b)) for b in BREAKS
    ]
    for p_star, f_star in maxima:
        ax.plot([p_star], [f_star], marker="o", markersize=9, color="black",
                zorder=5, linestyle="none")

    # Open circle: the limit from the left at the jump, which is NOT attained.
    p_jump = BREAKS[-1]
    ax.plot([p_jump], [profit_at_fixed_p(p_jump - eps)], marker="o",
            markersize=9, markerfacecolor="white", markeredgecolor="black",
            markeredgewidth=1.6, linestyle="none", zorder=5)

    # --- direct labels on the maxima --------------------------------------
    label_offsets = [(10, 4), (-4, 14), (8, 4)]
    label_align = ["left", "center", "left"]
    for (p_star, f_star), (dx, dy), ha in zip(maxima, label_offsets, label_align):
        ax.annotate(
            # {,} rather than a bare comma: mathtext sets a bare comma as
            # punctuation and inserts a space, giving "$102, 833".
            f"$p = {p_star:.3f}$\n$\\${f_star:,.0f}$".replace(",", "{,}"),
            xy=(p_star, f_star),
            xytext=(dx, dy),
            textcoords="offset points",
            fontsize=11,
            ha=ha,
            va="bottom",
            linespacing=1.05,
        )

    ax.annotate(
        "the best of the three is\non the LOWER BOUND of $p$",
        xy=(P_LO, maxima[0][1]),
        xytext=(0.05, 0.60),
        textcoords="axes fraction",
        fontsize=11,
        ha="left",
        va="center",
        arrowprops=dict(arrowstyle="->", color="black", linewidth=1.1,
                        shrinkB=8.0),
    )

    # --- where the two documented Ipopt runs started, and where they went ---
    # Starting values read back from Ipopt with max_iter = 0; see the lecture's
    # source comments in lectures/continuous-optimization.tex.
    starts = [(0.033170, "bound\\_frac $=0.01$", P_LO),
              (0.041500, "bound\\_frac $=0.5$", BREAKS[-1])]
    y_lo, y_hi = ax.get_ylim()
    tick = y_lo + 0.035 * (y_hi - y_lo)
    for p0, text, p_land in starts:
        ax.plot([p0], [tick], marker="^", markersize=8, color="black",
                linestyle="none", clip_on=False, zorder=6)
        ax.annotate("$p_0$", xy=(p0, tick), xytext=(0, 9),
                    textcoords="offset points", fontsize=10, ha="center",
                    va="bottom")
    ax.annotate(
        "starts here $\\rightarrow$ lands at $0.045$,\n"
        "though $0.040$ is nearer",
        xy=(starts[1][0], tick),
        xytext=(0.05, 0.30),
        textcoords="axes fraction",
        fontsize=11,
        ha="left",
        va="center",
        arrowprops=dict(arrowstyle="->", color="black", linewidth=1.1,
                        shrinkB=6.0),
    )

    # Headroom at the top for the two labels that sit above their markers.
    y_lo2, y_hi2 = ax.get_ylim()
    ax.set_ylim(y_lo2, y_hi2 + 0.13 * (y_hi2 - y_lo2))

    ax.yaxis.set_major_formatter(
        FuncFormatter(lambda v, _pos: f"{v:,.0f}")
    )
    ax.set_xlabel("pool composition $p$")
    ax.set_ylabel("profit [\\$]")
    ax.set_xlim(P_LO - 0.0004, P_HI + 0.0004)
    ax.set_xticks(np.arange(0.033, 0.0501, 0.003))

    fig.tight_layout()
    return fig
