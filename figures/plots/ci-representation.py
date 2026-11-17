"""Prepared constrained-optimization geometry; no notebook-generated results."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle


def make_figure():
    fig,axs=plt.subplots(1,2,figsize=(7.2,2.7),layout="constrained")
    x=np.linspace(-1.2,1.2,200)
    titles=[r"Alternate constraint: $g_1(x)=x\leq0$",r"Original constraint: $g_2(x)=x^3\leq0$"]
    for ax,y,title in zip(axs,[x,x**3],titles):
        ax.axvspan(-1.2,0,facecolor=(.337,.706,.914,.18),hatch="//",edgecolor="0.5",linewidth=0)
        ax.plot(x,y,color="black",linestyle="-",linewidth=2);ax.axhline(0,color="#D55E00",linestyle="--",linewidth=1.2)
        ax.text(-1.08,1.12,r"feasible: $x\leq0$",fontsize=10)
        ax.set(xlim=(-1.2,1.2),ylim=(-1.8,1.8),xlabel="x",ylabel="g(x)",title=title)
        ax.title.set_fontsize(10)
    return fig
