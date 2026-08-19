"""One calendar week of day-ahead electricity price: the diurnal cycle a
battery is paid to exploit.

    figures/plots/dam-price-week.py  ->  media/figures/dam-price-week.{png,pdf}

`notebooks/1-dev/Pyomo-Nuts-and-Bolts.ipynb` cell 15. CAISO day-ahead market
(node ALTA2G_7_B1), calendar year 2015, hourly. January 1, 2015 was a Thursday,
so the notebook's `offset = 4` days starts the window on Monday, January 5 --
one full Monday-to-Sunday week. Committed data, no solve: the file is
`notebooks/data/Prices_DAM_ALTA2G_7_B1.csv`, read from this script's location.

Greyscale: ONE series. The only other ink is the day grid, which is drawn as
light rules rather than as a second series.
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


def make_figure():
    price = np.loadtxt(DATA)
    week = price[OFFSET_DAYS * 24 : (OFFSET_DAYS + N_DAYS) * 24]
    hours = np.arange(week.size)

    fig, ax = plt.subplots(figsize=(8.0, 3.2))
    ax.plot(hours, week, linewidth=2.0)

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
    ax.set_xlabel("Monday 5 January 2015 onward")

    fig.tight_layout()
    return fig
