"""Prepared constrained-optimization geometry; no notebook-generated results."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle


def make_figure():
    fig,axs=plt.subplots(1,2,figsize=(6.8,2.9),layout="constrained")
    axs[0].plot([-.1,1.1],[1.1,-.1],color="#0072B2",linewidth=2)
    axs[0].plot([0,1],[1,0],color="black",linestyle="--",marker="o",ms=5)
    axs[0].plot(.5,.5,"s",color="#D55E00",ms=6)
    axs[0].set(xlim=(-.2,1.2),ylim=(-.2,1.2),title=r"$h=x_1+x_2-1=0$")
    axs[1].add_patch(Circle((0,0),1,facecolor="none",edgecolor="#0072B2",linewidth=2))
    axs[1].plot([-1,1],[0,0],color="black",linestyle="--",marker="o",ms=5)
    axs[1].plot(0,0,"s",color="#D55E00",ms=6)
    axs[1].set(xlim=(-1.2,1.2),ylim=(-1.2,1.2),title=r"$h=x_1^2+x_2^2-1=0$")
    for ax in axs:ax.set(aspect="equal",xlabel=r"$x_1$",ylabel=r"$x_2$")
    return fig
