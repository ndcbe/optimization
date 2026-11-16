"""Prepared constrained-optimization geometry; no notebook-generated results."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle


def make_figure():
    fig,axs=plt.subplots(1,3,figsize=(7.8,2.7),layout="constrained")
    x=np.linspace(-1.5,1.7,200)
    axs[0].plot(x,x*x,color="0.7",linestyle="--",linewidth=1)
    xf=np.linspace(1,1.7,70);axs[0].plot(xf,xf*xf,color="#0072B2",linestyle="-",linewidth=2)
    axs[0].plot(1,1,"o",color="black",ms=6);axs[0].set_title(r"(1) $f=x^2,\ \mathcal{F}=[1,\infty)$",fontsize=11)
    axs[1].plot(x,x,color="0.7",linestyle="--",linewidth=1);axs[1].plot(0,0,"o",color="#0072B2",ms=7)
    axs[1].set_title(r"(2) $f=x,\ \mathcal{F}=\{0\}$",fontsize=11)
    axs[2].plot([-1.5,1.5],[0,0],color="#0072B2",linestyle="-",linewidth=2);axs[2].plot(0,0,"o",color="black",ms=6)
    axs[2].set_title(r"(3) $f=0,\ \mathcal{F}=\mathbb{R}$",fontsize=11)
    for ax in axs:
        ax.axhline(0,color="black",linewidth=.6);ax.set(xlabel="decision x",ylabel="f(x)",xlim=(-1.5,1.7))
    # Annotations replace a prose key below the figure (instructor markup, 2026-11-16).
    note=dict(fontsize=8.5,ha="center",va="center")
    arrow=dict(arrowstyle="->",color="0.25",linewidth=.8)
    out=r"objective, $x\notin\mathcal{F}$"
    axs[0].annotate(out,xy=(-.75,.5625),xytext=(-.2,2.55),arrowprops=arrow,**note)
    axs[0].annotate(r"candidate $x^*$",xy=(1,1),xytext=(.35,1.55),arrowprops=arrow,**note)
    axs[0].annotate("feasible",xy=(1.45,2.1),xytext=(.75,2.1),arrowprops=arrow,**note)
    axs[1].annotate(r"candidate $x^*$",xy=(0,0),xytext=(-.55,1.1),arrowprops=arrow,**note)
    axs[1].annotate(out,xy=(.9,.9),xytext=(.55,-1.0),arrowprops=arrow,**note)
    axs[2].annotate(r"candidate $x^*$",xy=(0,0),xytext=(.1,.028),arrowprops=arrow,**note)
    axs[2].annotate("every point is feasible",xy=(-.9,0),xytext=(-.1,-.03),arrowprops=arrow,**note)
    return fig
