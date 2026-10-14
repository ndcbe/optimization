"""The two exact bound examples; prepared decision-space comparisons."""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig, axs = plt.subplots(1, 2, figsize=(7.2, 2.7), layout="constrained")
    x = np.linspace(-.35, 1.25, 240)
    for ax, lower in zip(axs, [.5, 0]):
        ax.axvspan(lower, 1, facecolor="#56B4E9", alpha=.17,
                   hatch="//", edgecolor="0.7")
        ax.plot(x, x*x, color="black", linestyle="-", lw=1.5)
        ax.axvline(lower, color="#0072B2", linestyle="-", lw=1.5)
        ax.axvline(1, color="0.4", linestyle="--", lw=1)
        ax.plot(lower, lower*lower, 'o', color="black", ms=5)
        ax.set(xlim=(-.35, 1.25), ylim=(-.12, 1.45), xlabel="x",
               title=rf"$\min x^2,\quad {lower:g}\leq x\leq1$")
    axs[0].set_ylabel("objective")
    return fig
