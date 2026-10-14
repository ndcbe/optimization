"""Prepared constrained-optimization geometry; no notebook-generated results."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle


def make_figure():
    fig,axs=plt.subplots(1,2,figsize=(6.8,2.5),layout="constrained")
    x=np.linspace(-1.2,1.2,200)
    for ax,y,title in zip(axs,[x,x**3],[r"$g(x)=x$",r"$g(x)=x^3$"]):
        ax.axvspan(-1.2,0,facecolor="#56B4E9",alpha=.16,hatch="//",edgecolor="0.7")
        ax.plot(x,y,color="black",linewidth=2);ax.axhline(0,color="#D55E00",linestyle="--",linewidth=1.2)
        ax.set(xlim=(-1.2,1.2),ylim=(-1.8,1.8),xlabel="x",ylabel="g(x)",title=title)
    return fig
