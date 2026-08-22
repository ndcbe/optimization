"""The farmer's problem: four solutions to the same 500 acres.

    figures/plots/farmer-solutions.py -> media/figures/farmer-solutions.{png,pdf}

Birge & Louveaux, *Introduction to Stochastic Programming*, 2nd ed., Ch. 1
(Tables 2-5, printed pp. 5-8). Three of these four solutions assume the yield
is KNOWN before the land is planted -- one per scenario -- and the fourth does
not. The point of the picture is that the two-stage recourse allocation is not
any of the three, and is not their average either: it hedges, planting more
wheat than any perfect-information solution would while stopping beets short of
the 6000 T quota so the quota is still reachable in a good year.

Everything here is RE-SOLVED, not transcribed. The linear programs are built
and solved below with scipy's HiGHS, so the figure cannot drift away from the
model it illustrates. No Pyomo, no Ipopt: `make` needs no solver binary and
this finishes in well under a second.

Reproduced exactly (see lecture-notes/verification/stochastic-programming-
intro.md): 183.33/66.67/250 -> $167,667; 120/80/300 -> $118,600;
100/25/375 -> $59,950; recourse 170/80/250 -> $108,390.

Greyscale: four series, and NOTHING here is encoded by hue at all -- see the
note on FILLS below. Each bar carries a hatch and a step on a luminance ramp,
and the profit panel is direct-labelled on top of that.

(The "four is the house cap" clause that used to sit in this sentence is gone:
figures/README.md WITHDREW the four-series cap on 2026-08-21. Four is still the
right number here, but because four is what the data has, not because a rule
says so.)

⚠ THE 2026-08-21 NOTE THAT USED TO SIT HERE IS RETRACTED (2026-08-22). It said
the four bars could not walk HATCH_CYCLE 0 to 3 because in matplotlib 3.5.1 the
backslash hatch leaned the same way as the forward slash, making indices 0 and
1 one texture. That was a real defect, but it is DEAD: it does not reproduce
under the matplotlib 3.11.1 in optimization_fall2026, where index 0 is +45 deg
and index 1 is -45 deg -- by the hatch spec the most SEPARATED line pair the
cycle offers. Do not reintroduce the workaround.

HATCHES below still skips index 1, and the reason is now this figure's own,
established by rendering the walk-the-cycle version and looking at it:

  ⚠ MIRRORED SLOPES ON BARS THAT TOUCH MERGE INTO A HERRINGBONE. The bars
  within a group abut, so with index 1 restored the +20% and average bars meet
  along a shared edge where a +45 texture runs into a -45 one. The rendered
  result is a single chevron-folded ribbon rather than two categories, most
  obviously in the sugar-beets group where both bars are tall. On top of that,
  the legend stacks the two swatches one directly above the other, each only a
  few lines wide, so the reader is asked to judge the SIGN of a slope on the
  smallest patch in the figure. Index 4 ("|||") cannot be read as a slash at
  any size and does not fuse across an edge.

So the hatch that replaced index 1 is kept on its merits, not out of fear of
the old defect. See plots/evpi-vss-ladder.py, which is the same figure shape and
reached the same conclusion, and contrast plots/licq-cusp.py, where the regions
OVERLAP rather than abut and the mirrored pair is therefore exactly right.

`scripts/check_greyscale.py --source` reports this file as
"2 series, no colour, 0 distinct non-colour encodings". That is a false
positive: the fill and the hatch are both chosen by subscript rather than by a
literal, so the AST reader cannot see either (the script says as much under
HONEST LIMITATIONS). Both channels are present and measured.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import linprog

from _house import HATCH_CYCLE

# Bars are told apart by HATCH and by a LUMINANCE RAMP, not by hue.
#
# This is a deliberate departure from the house colour cycle and it is the
# right call here. Hatching over a saturated fill antialiases into a family of
# intermediate colours -- a green fill under black hatch lines reads to
# scripts/check_greyscale.py as four separate greens, several of which collapse
# into the same grey. Measured: the Okabe-Ito version of this figure produced
# EIGHT data colours and SIX failing pairs, none of which a reader would ever
# have perceived as series. A grey ramp has no such blend problem, the four
# steps are far enough apart to survive any printer, and the hatch carries the
# identity independently. Greyscale is a pass/fail FLOOR (figures/README.md),
# and for a four-category bar chart this is simply the correct encoding.
FILLS = ("0.94", "0.80", "0.62", "0.42")

# ⚠ NOT a straight walk down HATCH_CYCLE, and NOT because of the matplotlib
# 3.5.1 same-slope defect that used to be cited here -- that defect is dead
# under 3.11.1, where "///" (+45) and "\\\" (-45) are the most separated line
# pair in the cycle. See the retraction in the module docstring.
#
# Index 1 is skipped because the bars within a group ABUT: rendered, a +45
# texture running into a -45 one across a shared edge fuses into a herringbone,
# and the stacked legend swatches ask the reader to judge the sign of a slope on
# a patch a few lines wide. "|||" cannot be read as a slash at any size.
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
        1, 2, figsize=(9.6, 3.9), gridspec_kw={"width_ratios": [1.85, 1.0]}
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
    ax_a.legend(fontsize=9.5, ncol=2, loc="upper center", frameon=False)

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

    fig.tight_layout()
    return fig
