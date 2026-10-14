"""Prepared constrained-optimization geometry; no notebook-generated results."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle


def make_figure():
    fig,ax=plt.subplots(figsize=(5.8,3.1),layout="constrained")
    ax.add_patch(Rectangle((0,-1.4),1.6,2.8,facecolor="#56B4E9",alpha=.16,hatch="//",edgecolor="0.7"))
    ax.add_patch(Circle((0,0),1,facecolor="none",edgecolor="black",linestyle="--",linewidth=1.5))
    ax.plot([0,0],[-1.4,1.4],color="#0072B2",linestyle="-",linewidth=2)
    ax.plot(0,0,"o",color="black",ms=5);ax.text(-.36,-.22,r"$\mathbf{x}^*$",fontsize=12)
    ax.plot(.6,.4,"s",color="#D55E00",ms=6);ax.text(.67,.4,r"$\mathbf{x}$",fontsize=12)
    ax.annotate("",xy=(.6,.4),xytext=(0,0),arrowprops=dict(arrowstyle="->",color="black",linewidth=1))
    ax.text(.10,.64,r"$\mathbf{x}-\mathbf{x}^*$",fontsize=11)
    ax.text(-1.3,.98,r"$\mathcal{N}_{1}(\mathbf{x}^*)$",fontsize=12)
    ax.text(.22,-1.16,r"$\mathcal{F}=\{x_1\geq0\}$",fontsize=12)
    ax.set(xlim=(-1.4,1.6),ylim=(-1.4,1.4),aspect="equal",xlabel=r"$x_1$",ylabel=r"$x_2$")
    return fig
