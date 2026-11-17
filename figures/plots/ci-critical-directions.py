"""Prepared constrained-optimization geometry; no notebook-generated results."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle


def make_figure():
    fig,axs=plt.subplots(1,2,figsize=(7.2,2.9),layout="constrained")
    for ax in axs:
        ax.add_patch(Rectangle((-1.2,0),2.4,1.15,facecolor=(.337,.706,.914,.18),hatch="//",edgecolor="0.5",linewidth=.5))
        ax.plot([-1.2,1.2],[0,0],color="black",linewidth=1.2)
        ax.plot(0,0,"o",color="black",ms=5)
        ax.set(xlim=(-1.25,1.25),ylim=(-.25,1.2),aspect="equal",xlabel=r"$p_1$",ylabel=r"$p_2$")
    axs[0].plot([-1.1,1.1],[0,0],color="#D55E00",linestyle="--",linewidth=3)
    axs[0].annotate("",xy=(0,1),xytext=(0,0),arrowprops=dict(arrowstyle="->",color="#0072B2",linewidth=1.7))
    axs[0].text(.10,.82,r"$\mathbf{p}=(0,1)^T$",fontsize=10)
    axs[0].text(-1.1,-.18,"critical directions",fontsize=10)
    axs[0].set_title(r"$f=x_1^2+x_2,\quad u^*=1$",fontsize=11)
    axs[1].add_patch(Rectangle((-1.1,0),2.2,1.05,facecolor="none",hatch="..",edgecolor="#D55E00",linewidth=1))
    axs[1].set_title(r"$f=x_1^2+x_2^2,\quad u^*=0$",fontsize=11)
    axs[1].text(-1.02,.82,"critical directions",fontsize=10,
                bbox=dict(facecolor="white",edgecolor="none",pad=2))
    return fig
