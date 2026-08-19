r"""EEV <= RP <= WS: where EVPI and VSS live, and which scenario pays for them.

    figures/plots/evpi-vss-ladder.py
        ->  media/figures/evpi-vss-ladder.{png,pdf}

Drawn for lectures/stochastic-programming-advanced.tex, sections "Perfect
information", "The stochastic program", "Expected value of perfect information"
and "Value of the stochastic solution".  Those four sections define six dollar
figures and two differences and never put them on one axis.  The lecture then
asks the class, in an \activity, to compare EVPI = $7,016 with VSS = $1,150 and
say "where to spend effort" -- a question about the RELATIVE SIZE of two gaps,
which is precisely the thing a table of six numbers hides and a scale drawing
shows.  The 6:1 ratio is invisible in prose and unmissable here.

PANEL (a) -- the ladder, drawn to scale
---------------------------------------
Three rungs on one expected-profit axis:

    EEV = $107,240   plant for the average year, live in the real one
    RP  = $108,390   the two-stage recourse plan
    WS  = $115,406   a different plan per scenario -- the perfect-information fiction

    VSS  = RP  - EEV = $1,150     what solving the right model is worth
    EVPI = WS  - RP  = $7,016     what a perfect forecast would be worth

SIGNS.  The lecture's tables report PROFITS as positive numbers while
eq. (eq:ws)-(eq:evpi) minimise a COST, so the lecture writes EVPI = RP - WS with
both entered as negative costs.  This figure plots profits, on which the same
two quantities read as WS - RP and RP - EEV, and the ordering is
EEV <= RP <= WS.  Both conventions give EVPI, VSS >= 0; the lecture's own
"Watch the signs" paragraph is the reason this is spelled out here rather than
left implicit.

PANEL (b) -- where the gap opens
--------------------------------
The same comparison per scenario.  The lecture's \fillin says "the gap opens up
in the low-yield scenario, where the compromise allocation is badly exposed";
paired bars make that a measurement rather than an assertion:

    scenario     wait-and-see   recourse   gap
    low            $59,950      $48,820    $11,130
    average       $118,600     $109,350     $9,250
    high          $167,667     $167,000       $667

so nearly all of EVPI is bought in the two bad scenarios, and the high-yield
scenario contributes almost nothing.  A student who has only seen the averages
cannot know that.

SOURCES for every number
------------------------
The six book figures (59,950 / 118,600 / 167,667 / 115,406 / 108,390 / 7,016)
and EEV = 107,240 are Birge & Louveaux, 2nd ed., stated in prose on p. 9, with
the WS/RP/EVPI and EV/EEV/VSS definitions at S4.1-S4.2, pp. 163-165.  The three
per-scenario recourse profits (48,820 / 109,350 / 167,000) are NOT in the book
-- the lecture's own \rewrite note records that they were derived for this
course -- so they are reproduced here from the lecture and not attributed to
Birge & Louveaux.

_verify() recomputes both averages and both gaps from the per-scenario numbers
and asserts they reproduce the six aggregates to the dollar (WS rounds:
346,217/3 = 115,405.67, which the book and the lecture both print as 115,406,
so EVPI is 7,015.67 printed as 7,016).

GREYSCALE
---------
Two bar series, distinguished by HATCH texture (HATCH_CYCLE[0] vs [1]) and by a
white vs grey face, not by hue; the legend is keyed by the hatch.  Panel (a) is
entirely black, grey and #0072B2 (dL* = 46.0).  No hue carries meaning alone.
"""

import numpy as np
import matplotlib.pyplot as plt

from _house import HATCH_CYCLE

# --- Birge & Louveaux, 2nd ed., p. 9 (wait-and-see, per scenario) -----------
WS_SCEN = np.array([59_950.0, 118_600.0, 167_667.0])
# --- derived for this course; see lectures/stochastic-programming-advanced.tex
RP_SCEN = np.array([48_820.0, 109_350.0, 167_000.0])

SCEN_NAMES = ("low", "average", "high")

WS = WS_SCEN.mean()          # 115,405.67 -> printed 115,406
RP = RP_SCEN.mean()          # 108,390 exactly
EEV = 107_240.0              # B&L S4.2, p. 165 (as a profit)

EVPI = WS - RP               # 7,015.67 -> printed 7,016
VSS = RP - EEV               # 1,150 exactly

BLACK = "black"
BLUE = "#0072B2"


def _verify():
    assert abs(WS_SCEN.sum() - 346_217.0) < 1e-9
    assert abs(WS - 115_405.6667) < 1e-3, WS
    assert round(WS) == 115_406
    assert abs(RP_SCEN.sum() - 325_170.0) < 1e-9
    assert abs(RP - 108_390.0) < 1e-9, RP
    assert abs(VSS - 1_150.0) < 1e-9, VSS
    assert round(EVPI) == 7_016, EVPI
    assert EEV <= RP <= WS, "on a PROFIT axis the ordering must be EEV <= RP <= WS"
    # the per-scenario gaps quoted in the docstring
    gaps = WS_SCEN - RP_SCEN
    assert np.allclose(gaps, [11_130.0, 9_250.0, 667.0])
    assert abs(gaps.mean() - EVPI) < 1e-9, "per-scenario gaps must average to EVPI"
    # every wait-and-see profit dominates its recourse counterpart -- the
    # lecture's \fillin claims this and it is why EVPI >= 0
    assert np.all(WS_SCEN >= RP_SCEN)


_verify()


def _panel_a(ax):
    rungs = ((EEV, "EEV"), (RP, "RP"), (WS, "WS"))

    for value, name in rungs:
        ax.plot([0.12, 0.88], [value, value], color=BLACK, linestyle="-",
                linewidth=2.4, zorder=4)
        ax.annotate(
            f"$\\mathbf{{{name}}}$ = \\${value:,.0f}".replace("\\$", "\\$"),
            xy=(0.09, value),
            fontsize=11.5,
            ha="right",
            va="center",
            zorder=6,
        )

    # the two gaps, drawn as double-headed arrows to the same vertical scale
    for lo, hi, name, amount, xpos in (
        (EEV, RP, "VSS", VSS, 0.62),
        (RP, WS, "EVPI", EVPI, 0.62),
    ):
        ax.annotate(
            "",
            xy=(xpos, hi),
            xytext=(xpos, lo),
            arrowprops=dict(arrowstyle="<|-|>", color=BLUE, linewidth=1.8,
                            shrinkA=0, shrinkB=0),
            zorder=5,
        )
        ax.annotate(
            f"{name} = \\${amount:,.0f}",
            xy=(xpos + 0.05, 0.5 * (lo + hi)),
            fontsize=12,
            color=BLUE,
            ha="left",
            va="center",
            bbox=dict(facecolor="white", edgecolor="none", pad=1.0),
            zorder=7,
        )

    ax.annotate(
        "one plan per scenario\n(perfect forecast)",
        xy=(0.90, WS),
        fontsize=10.5,
        ha="left",
        va="center",
        zorder=6,
    )
    ax.annotate("one plan, all scenarios", xy=(0.90, RP), fontsize=10.5,
                ha="left", va="center", zorder=6)
    ax.annotate("plan for the mean year", xy=(0.90, EEV), fontsize=10.5,
                ha="left", va="center", zorder=6)

    ax.set_xlim(-0.80, 1.68)
    ax.set_ylim(105_500, 117_200)
    ax.set_xticks([])
    ax.set_ylabel("expected profit (\\$)")
    ax.set_yticks([106_000, 108_000, 110_000, 112_000, 114_000, 116_000])
    ax.set_yticklabels(["106k", "108k", "110k", "112k", "114k", "116k"])
    ax.set_title("(a) two gaps, to scale", fontsize=13)


def _panel_b(ax):
    idx = np.arange(3)
    w = 0.36

    ax.bar(idx - w / 2, WS_SCEN / 1000.0, width=w, facecolor="white",
           edgecolor=BLACK, linewidth=1.6, hatch=HATCH_CYCLE[0],
           label="wait-and-see (WS)", zorder=3)
    ax.bar(idx + w / 2, RP_SCEN / 1000.0, width=w, facecolor="0.82",
           edgecolor=BLACK, linewidth=1.6, hatch=HATCH_CYCLE[1],
           label="recourse plan (RP)", zorder=3)

    for i, gap in enumerate(WS_SCEN - RP_SCEN):
        ax.annotate(
            f"$-$\\${gap:,.0f}",
            xy=(float(i), WS_SCEN[i] / 1000.0 + 4.0),
            fontsize=11,
            color=BLUE,
            ha="center",
            va="bottom",
            zorder=6,
        )

    ax.set_xticks(idx)
    ax.set_xticklabels(SCEN_NAMES)
    ax.set_xlabel("yield scenario")
    ax.set_ylabel("profit (thousand \\$)")
    ax.set_ylim(0, 205)
    ax.legend(loc="upper left", fontsize=11, handlelength=1.6)
    ax.set_title("(b) the gap is bought in the bad years", fontsize=13)


def make_figure():
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.4))
    _panel_a(axes[0])
    _panel_b(axes[1])
    fig.tight_layout()
    return fig
