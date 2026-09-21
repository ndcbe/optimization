"""Compare perfect-information and two-stage farmer solutions.

Birge & Louveaux, Introduction to Stochastic Programming, 2nd ed.,
Chapter 1, Tables 2--5 (pp. 5--8). LPs are re-solved with SciPy/HiGHS.
The recourse allocation is neither a scenario optimum nor their average.
Color identifies each plan consistently across both panels; distinct hatches
and direct profit labels preserve readability in black and white.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import linprog

from _house import HATCH_CYCLE

# Color first, with redundant textures for monochrome printing.
FILLS = ("#0072B2", "#E69F00", "#009E73", "#CC79A7")
# Vertical lines distinguish adjacent bars more clearly than mirrored slashes.
HATCHES = (HATCH_CYCLE[0], HATCH_CYCLE[4], HATCH_CYCLE[2], HATCH_CYCLE[3])

CROPS = ("wheat", "corn", "sugar beets")
PLANT = np.array([150.0, 230.0, 260.0])          # $/acre
BASE = np.array([2.5, 3.0, 20.0])                # T/acre at average yield
REQ = np.array([200.0, 240.0])                   # T of wheat, corn for cattle
SELL = np.array([170.0, 150.0])                  # $/T
BUY = np.array([238.0, 210.0])                   # $/T
BEET_HI, BEET_LO, QUOTA = 36.0, 10.0, 6000.0
LAND = 500.0


def _solve(mults, probs):
    """Two-stage program over the given yield multipliers. One scenario gives
    the perfect-information (wait-and-see) solution for that yield."""
    n_s = len(mults)
    n = 3 + 6 * n_s                              # x(3); then w1 w2 y1 y2 w3 w4
    c = np.zeros(n)
    c[:3] = PLANT
    for s, p in enumerate(probs):
        o = 3 + 6 * s
        c[o + 0], c[o + 1] = -p * SELL[0], -p * SELL[1]
        c[o + 2], c[o + 3] = p * BUY[0], p * BUY[1]
        c[o + 4], c[o + 5] = -p * BEET_HI, -p * BEET_LO

    rows, rhs = [], []
    r = np.zeros(n)
    r[:3] = 1.0
    rows.append(r)
    rhs.append(LAND)                             # plant at most 500 acres

    for s, m in enumerate(mults):
        t = BASE * m
        o = 3 + 6 * s
        for k in (0, 1):                         # grown + bought - sold >= req
            r = np.zeros(n)
            r[k] = -t[k]
            r[o + 2 + k] = -1.0
            r[o + k] = 1.0
            rows.append(r)
            rhs.append(-REQ[k])
        r = np.zeros(n)                          # beets sold <= beets grown
        r[o + 4] = r[o + 5] = 1.0
        r[2] = -t[2]
        rows.append(r)
        rhs.append(0.0)
        r = np.zeros(n)                          # favourable price up to quota
        r[o + 4] = 1.0
        rows.append(r)
        rhs.append(QUOTA)

    res = linprog(c, A_ub=np.array(rows), b_ub=np.array(rhs),
                  bounds=[(0, None)] * n, method="highs")
    if not res.success:                          # never silently plot a bad solve
        raise RuntimeError(f"farmer LP failed: {res.message}")
    return res.x[:3], -res.fun


def solutions():
    """The four rows of the figure, in the order the lecture develops them."""
    out = []
    for label, mult in (("perfect info,\n$+20\\%$ yield", 1.2),
                        ("perfect info,\naverage yield", 1.0),
                        ("perfect info,\n$-20\\%$ yield", 0.8)):
        acres, profit = _solve([mult], [1.0])
        out.append((label, acres, profit))
    acres, profit = _solve([1.2, 1.0, 0.8], [1 / 3] * 3)
    out.append(("two-stage\nrecourse", acres, profit))
    return out


def make_figure():
    data = solutions()
    n = len(data)
    fig, (ax_a, ax_p) = plt.subplots(
        1, 2, figsize=(9.6, 4.3), gridspec_kw={"width_ratios": [1.85, 1.0]}
    )

    # ---- left: acres per crop, grouped by crop, one bar per solution
    idx = np.arange(len(CROPS))
    width = 0.8 / n
    for i, (label, acres, _) in enumerate(data):
        ax_a.bar(idx + (i - (n - 1) / 2) * width, acres, width,
                 facecolor=FILLS[i], hatch=HATCHES[i], edgecolor="black",
                 linewidth=0.7, label=label.replace("\n", " "))
    ax_a.set_xticks(idx)
    ax_a.set_xticklabels(CROPS)
    ax_a.set_ylabel("acres planted")
    ax_a.set_ylim(0, 430)

    # 300 acres is where 20 T/acre x 300 = 6000 T, i.e. the quota at average
    # yield. Every beet decision in the problem is really about this line.
    ax_a.axhline(300, color="0.45", linewidth=1.0, linestyle=(0, (1, 2)),
                 zorder=0)
    # Placed over the corn group, which is empty up there. Over the beet group
    # it collided with the 375-acre bar.
    ax_a.annotate("$6000\\,$T quota $=300$ acres\nat average yield",
                  xy=(0.62, 307), fontsize=9.5, color="0.25", ha="left",
                  va="bottom")

    # ---- right: the resulting profit, direct-labelled
    for i, (_, _, profit) in enumerate(data):
        ax_p.bar(i, profit / 1000.0, 0.68, facecolor=FILLS[i],
                 hatch=HATCHES[i], edgecolor="black", linewidth=0.7)
        ax_p.annotate(f"{profit/1000.0:,.1f}", xy=(i, profit / 1000.0 + 4),
                      ha="center", va="bottom", fontsize=10.5)
    ax_p.set_xticks(range(n))
    ax_p.set_xticklabels(["$+20\\%$", "avg.", "$-20\\%$", "recourse"],
                         fontsize=11)
    ax_p.set_ylabel("profit (\\$1000)")
    ax_p.set_ylim(0, 205)

    for ax in (ax_a, ax_p):
        ax.tick_params(top=False, right=False)

    handles, labels = ax_a.get_legend_handles_labels()
    fig.legend(handles, labels, fontsize=10, ncol=2, loc="upper center",
               bbox_to_anchor=(0.5, 1.0), frameon=False)
    fig.tight_layout(rect=(0, 0, 1, 0.84))
    return fig
