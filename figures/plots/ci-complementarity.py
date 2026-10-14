"""Complementarity proof mechanism; analytic illustration, not solver output."""
import numpy as np
import matplotlib.pyplot as plt


def make_figure():
    fig, axs = plt.subplots(1, 2, figsize=(6.8, 1.9), layout="constrained")
    values = [np.array([-.5, 0., -.3]), np.zeros(3)]
    assert all(np.all(v <= 0) for v in values)
    assert values[0].sum() < 0 and values[1].sum() == 0
    for ax, v, title in zip(axs, values, ["Product vector A", "Product vector B"]):
        ax.bar([1, 2, 3], v, width=.55, facecolor="none", edgecolor="black", hatch="//", linewidth=1.2)
        ax.plot([1, 2, 3], v, "o", color="black", markersize=4)
        ax.axhline(0, color="black", linewidth=.8)
        ax.set(xlim=(.4, 3.6), ylim=(-.65, .12), xticks=[1, 2, 3], xlabel="constraint index i", title=title)
    axs[0].set_ylabel(r"$g_i(\mathbf{x}^*)u_i^*$")
    return fig
