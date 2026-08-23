r"""The input data for the Markowitz portfolio example: five market indices over
1,259 trading days, rebased so they can share one axis.

    figures/plots/portfolio-index-prices.py
        ->  media/figures/portfolio-index-prices.{png,pdf}

Drawn for folio 2-8, green ink: "visualization of stock data goes here," and
the typed note "For the portfolio example, let's show the input data (stock
timeseries)."

Data: `notebooks/data/Stock_Data.csv`, five columns of daily adjusted closing
prices -- DJI (Dow Jones Industrial Average), GSPC (S&P 500), IXIC (NASDAQ
Composite), RUT (Russell 2000), VIX (CBOE Volatility Index). 1,259 closes, so
1,258 one-day returns. No solve and no random numbers: this figure is the data.

WHY REBASED TO 100
------------------
The five series differ by three orders of magnitude -- DJI opens the file at
14,447.75 and VIX at 13.74 -- so plotted raw, four of the five are a flat line
along the bottom. Each series is divided by its own first close and multiplied
by 100, which is the standard way to put indices on one axis and is also the
right transformation for THIS model: the optimization is over one-day RETURNS,
which are scale-free, so the rebasing throws away nothing the model uses.

WHAT THE PICTURE IS FOR
-----------------------
It shows, before any algebra, the two facts the model turns on. The four equity
indices rise together -- that is the covariance the objective is minimizing --
and VIX does neither: it is far more volatile and moves against them, which is
exactly why the optimizer keeps buying a slice of it. The lecture's frontier
table has VIX in every portfolio from rho = 0.0008 upward, and this is why.

Greyscale: five series, taken in order from `dowling.mplstyle`'s prop_cycle,
which pairs colour with linestyle element-wise, so each has a colour-free
identity. Each is also DIRECTLY LABELLED at its right-hand end, which is the
channel that actually carries the identity here.
"""

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

DATA = Path(__file__).resolve().parents[2] / "notebooks" / "data" / "Stock_Data.csv"

# Ticker -> the name the lecture's table uses.
NAMES = {
    "DJI": "Dow Jones",
    "GSPC": "S&P 500",
    "IXIC": "NASDAQ",
    "RUT": "Russell 2000",
    "VIX": "VIX",
}

# Minimum vertical separation between two right-hand labels, in points. Four of
# the five series finish within 7 index points of each other (DJI 165.8,
# RUT 163.2, VIX 169.9, GSPC 170.4), so the labels MUST be spread or they
# overprint -- which the first render did.
LABEL_GAP_PT = 17.0


def _spread(values, gap):
    """Push labels apart, smallest first, keeping their order.

    ``values`` are y positions in points. Returns adjusted positions such that
    consecutive entries differ by at least ``gap``, moving only upward, which
    keeps every label above the curve it names rather than crossing another.
    """
    order = sorted(range(len(values)), key=lambda i: values[i])
    out = list(values)
    for prev, cur in zip(order[:-1], order[1:]):
        if out[cur] - out[prev] < gap:
            out[cur] = out[prev] + gap
    return out


def make_figure():
    prices = pd.read_csv(DATA)
    rebased = 100.0 * prices / prices.iloc[0]
    days = np.arange(len(rebased))

    fig, ax = plt.subplots(figsize=(8.4, 4.4))

    colors, ends = [], []
    for column in prices.columns:
        series = rebased[column].to_numpy()
        (line,) = ax.plot(days, series, linewidth=1.6)
        colors.append(line.get_color())
        ends.append(series[-1])

    ax.set_xlabel("trading day")
    ax.set_ylabel("index level\n(first close $= 100$)")
    ax.set_xlim(0, len(rebased) - 1)
    ax.axhline(100.0, color="0.75", linewidth=0.8, linestyle=":", zorder=0)

    # Direct labelling in each series' own colour, at the right-hand end. The
    # dashes from the prop_cycle are invisible on data this noisy, so the label
    # -- not the linestyle -- is what actually carries the identity here.
    lo, hi = ax.get_ylim()
    span_pt = ax.get_window_extent().height
    ends_pt = [(v - lo) / (hi - lo) * span_pt for v in ends]
    for column, color, y_pt in zip(prices.columns, colors, _spread(ends_pt, LABEL_GAP_PT)):
        ax.annotate(
            NAMES[column],
            xy=(1.0, y_pt / span_pt),
            xycoords="axes fraction",
            xytext=(8, 0),
            textcoords="offset points",
            fontsize=12,
            color=color,
            ha="left",
            va="center",
            annotation_clip=False,
        )

    fig.tight_layout()
    # Leave room outside the axes for the five labels.
    fig.subplots_adjust(right=0.80)
    return fig
