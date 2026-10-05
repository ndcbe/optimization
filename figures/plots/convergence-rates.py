r"""Linear, superlinear and quadratic convergence on one set of axes.

    figures/plots/convergence-rates.py
        ->  media/figures/convergence-rates.{png,pdf}

Lecture 13 (Real Analysis Review), the rates table. Three synthetic error
sequences e^k = ||x^k - x*||, all starting at e^0 = 0.5:

    linear       e^{k+1} = 0.5 e^k              ratio e^{k+1}/e^k = 0.5 (fixed r)
    superlinear  e^{k+1} = (e^k)^{3/2}          ratio = (e^k)^{1/2} -> 0
    quadratic    e^{k+1} = (e^k)^2              e^{k+1} / (e^k)^2 = 1  (L-hat = 1)

Closed forms: 0.5^(k+1), 0.5^(1.5^k), 0.5^(2^k). On a semilog axis the linear
sequence is a straight line (a fixed number of digits gained per iteration:
log10(2) = 0.30), the superlinear one bends down, and the quadratic one roughly
doubles the digits each step: 0.5, 0.25, 6.3e-2, 3.9e-3, 1.5e-5, 2.3e-10, and
5.4e-20 at k = 6, which is below unit roundoff u = 1.1e-16 and is not drawn
(the dotted floor marks u).

Greyscale: colour AND linestyle AND marker AND a direct label per series.
numpy only, no solver.
"""

import numpy as np
import matplotlib.pyplot as plt

from _house import label_curve

U = 1.1e-16
K = np.arange(0, 9)


def sequences():
    lin = 0.5 ** (K + 1.0)
    sup = 0.5 ** (1.5 ** K)
    quad = 0.5 ** (2.0 ** K)
    out = []
    for e in (lin, sup, quad):
        e = e.astype(float)
        e[e < U] = np.nan
        out.append(e)
    return out


def make_figure():
    lin, sup, quad = sequences()
    fig, ax = plt.subplots(figsize=(6.6, 4.2))
    for e, marker in ((lin, "s"), (sup, "o"), (quad, "^")):
        ax.semilogy(K, e, marker=marker, markersize=7, linewidth=2.0)
    ax.axhline(U, color="0.5", linestyle=":", linewidth=1.2)
    ax.set_ylim(1e-17, 2)
    ax.set_xlim(-0.2, 11.4)
    ax.set_xlabel(r"iteration $k$")
    ax.set_ylabel(r"error $e^k = \|\mathbf{x}^k - \mathbf{x}^*\|$")
    label_curve(ax, 8.2, 4e-3, "linear (□)\n" r"$e^{k+1} = 0.5\,e^k$",
                color="0.2", va="center")
    label_curve(ax, 6.0, 3e-11, "superlinear (○)\n" r"$e^{k+1} = (e^k)^{3/2}$",
                color="0.2", va="top")
    label_curve(ax, 0.3, 1e-11, "quadratic (△)\n" r"$e^{k+1} = (e^k)^2$",
                color="0.2", va="top")
    label_curve(ax, 0.0, 1.6e-17, r"unit roundoff $u$", color="0.4",
                va="bottom", fontsize=11)
    return fig
