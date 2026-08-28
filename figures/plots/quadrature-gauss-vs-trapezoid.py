"""Two-point Gauss--Legendre and trapezoidal quadrature on a cubic.

Original course figure replacing a third-party raster. Both approximations use
two function evaluations; Gauss--Legendre is exact here because a two-node
rule integrates polynomials through degree three.
"""

import numpy as np
import matplotlib.pyplot as plt


def make_figure():
    f = lambda x: 7 * x**3 - 8 * x**2 - 3 * x + 3
    x = np.linspace(-1.0, 1.0, 401)
    gauss_x = np.array([-1 / np.sqrt(3), 1 / np.sqrt(3)])
    endpoint_x = np.array([-1.0, 1.0])

    fig, ax = plt.subplots(figsize=(7.2, 4.3))
    ax.plot(x, f(x), linewidth=2.2, label=r"$f(x)=7x^3-8x^2-3x+3$")
    ax.plot(endpoint_x, f(endpoint_x), marker="s", label="trapezoidal interpolant")
    ax.plot(gauss_x, f(gauss_x), marker="o", label="two-point Gauss interpolant")
    ax.axhline(0.0, color="0.65", linewidth=0.8, zorder=0)
    for node in gauss_x:
        ax.axvline(node, color="0.65", linewidth=0.8, linestyle=":", zorder=0)

    ax.text(-0.96, 2.8, r"$Q_{\mathrm{trap}}=-10$", fontsize=13)
    ax.text(0.10, 2.8, r"$Q_{\mathrm{GL2}}=2/3=\int_{-1}^{1}f(x)\,dx$", fontsize=13)
    ax.set(xlabel="$x$", ylabel="$f(x)$", xlim=(-1, 1), ylim=(-10, 4))
    ax.legend(loc="lower right", fontsize=11)
    fig.tight_layout()
    return fig
