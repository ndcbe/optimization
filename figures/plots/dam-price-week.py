"""One calendar week of day-ahead electricity price: the diurnal cycle a
battery is paid to exploit.

    figures/plots/dam-price-week.py  ->  media/figures/dam-price-week.{png,pdf}

`notebooks/1-dev/Pyomo-Nuts-and-Bolts.ipynb` cell 15. CAISO day-ahead market
(node ALTA2G_7_B1), calendar year 2015, hourly. January 1, 2015 was a Thursday,
so the notebook's `offset = 4` days starts the window on Monday, January 5 --
one full Monday-to-Sunday week. Committed data, no solve: the file is
`notebooks/data/Prices_DAM_ALTA2G_7_B1.csv`, read from this script's location.

ANNOTATED 2026-08-22, folio 1-10: "Let's annotate the figure" -- Prof. Dowling
drew four arrows on this plot, marking the MORNING, NIGHT, MIDDAY and EVENING
features of the daily cycle, and struck the x-axis label "Monday 5 January 2015
onward". Both are done here: the arrows are part of the figure, and the axis
label is gone (the day names under the axis already say what the window is, and
the caption carries the date).

The four features he named, measured on the Monday of this window (index 0 of
the plotted week) -- the day on which all four are cleanest:

    hour  3   $28.72/MWh   night     -- the overnight trough the battery buys into
    hour  7   $56.71/MWh   morning   -- the morning peak
    hour 13   $30.29/MWh   midday    -- the midday dip, the second buying window
    hour 18   $61.76/MWh   evening   -- the evening peak, and the week's maximum

His four words are used verbatim as the labels. They are also the shortest
labels that fit: "morning peak" and "evening peak" collide with each other at
this aspect ratio, because the two features are 11 hours apart on a 168 hour
axis.

They are annotated on Monday only. The same four recur every day of the week --
that is the point of showing seven days -- but seven copies of four labels is
noise, so the pattern is named once and left for the eye to repeat.

Greyscale: ONE series, and the annotations are black text with black arrows.
The only other ink is the day grid, drawn as light rules rather than as a
second series. Nothing is keyed by colour.
"""

from pathlib import Path

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.ticker import MultipleLocator

DATA = Path(__file__).resolve().parents[2] / "notebooks" / "data" / (
    "Prices_DAM_ALTA2G_7_B1.csv"
)

OFFSET_DAYS = 4  # Jan 1 2015 was a Thursday; +4 days lands on Monday Jan 5
N_DAYS = 7
DAY_NAMES = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

BLUE = "#0072B2"  # Okabe-Ito; the same blue battery-arbitrage.py uses for price

# (hour within the plotted week, label, text offset in points, alignment).
# Hours are Monday's, verified against the data in the docstring; the text
# offsets were set by looking at the rendered PNG, not guessed.
ANNOTATIONS = [
    (3, "night", (8, -40), "left", "top"),
    (7, "morning", (8, 42), "left", "bottom"),
    (13, "midday", (8, -14), "left", "top"),
    (18, "evening", (10, 14), "left", "bottom"),
]


def make_figure():
    price = np.loadtxt(DATA)
    week = price[OFFSET_DAYS * 24 : (OFFSET_DAYS + N_DAYS) * 24]
    hours = np.arange(week.size)

    fig, ax = plt.subplots(figsize=(8.0, 4.0))
    # Blue, not black: folio 1-13 asks for the price series in colour, and
    # this is the same price. One series, so nothing depends on the hue.
    ax.plot(hours, week, linewidth=2.0, color=BLUE, linestyle="-")

    ax.xaxis.set_major_locator(MultipleLocator(24))
    ax.xaxis.set_minor_locator(MultipleLocator(6))
    for boundary in range(24, N_DAYS * 24, 24):
        ax.axvline(boundary, color="0.75", linewidth=0.8, zorder=0)

    # Day names sit under the axis in place of a second set of tick labels:
    # "hour 96" means nothing, "Thu" means something.
    ax.set_xticks(24 * np.arange(N_DAYS) + 12, minor=False)
    ax.set_xticklabels(DAY_NAMES)
    ax.xaxis.set_minor_locator(MultipleLocator(24))
    ax.tick_params(axis="x", which="major", length=0)

    ax.set_xlim(0, N_DAYS * 24)
    ax.set_ylabel("DAM price\n[\\$/MWh]")
    # No x-axis label: struck on folio 1-10.

    # Headroom above and below so the four labels clear the axes. All four
    # features sit inside Monday, only 15 hours apart on a 168 hour axis, so
    # the labels are STAGGERED vertically as well as offset horizontally --
    # side by side they overlap, which the first render showed.
    lo, hi = week.min(), week.max()
    ax.set_ylim(lo - 0.42 * (hi - lo), hi + 0.42 * (hi - lo))

    # --- the four arrows --------------------------------------------------
    # An arrow is not a series: it gets no linestyle from the colour cycle, so
    # colour would be all it had. These are black, and each is labelled in
    # place with the feature it points at (figures/README.md).
    for hour, text, (dx, dy), ha, va in ANNOTATIONS:
        ax.annotate(
            text,
            xy=(hour, week[hour]),
            xytext=(dx, dy),
            textcoords="offset points",
            fontsize=11,
            ha=ha,
            va=va,
            color="black",
            linespacing=0.95,
            arrowprops=dict(
                arrowstyle="->",
                color="black",
                linewidth=1.1,
                shrinkA=1.0,
                shrinkB=3.0,
            ),
        )

    fig.tight_layout()
    return fig
