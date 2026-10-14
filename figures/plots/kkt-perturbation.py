"""Exact moving fence and fixed equality rail for f=x1 squared+x2 squared."""
import numpy as np
import matplotlib.pyplot as plt
def make_figure():
    fig,ax=plt.subplots(figsize=(5.7,3.0),layout="constrained")
    q=np.linspace(.55,1.75,80)
    ax.plot(q,q,color="black",linestyle="-",lw=1.5)
    ax.axvline(1,color="#0072B2",linestyle="-",lw=2)
    ax.axvline(1.3,color="#D55E00",linestyle="--",lw=2)
    ax.plot(1,1,'o',color="#0072B2",ms=7);ax.plot(1.3,1.3,'s',color="#D55E00",ms=7)
    ax.annotate("",xy=(1.29,1.29),xytext=(1.01,1.01),arrowprops=dict(arrowstyle='->',color="black",lw=2))
    ax.text(.64,1.45,r"$g=b-x_1=0$",fontsize=11)
    ax.text(1.31,.69,r"$g+\epsilon=0$",fontsize=11)
    ax.text(.60,1.68,r"$h=x_2-x_1=0$",fontsize=11)
    ax.text(.7,.84,r"$\mathbf{x}^*$",fontsize=12);ax.text(1.36,1.17,r"$\mathbf{x}^{\epsilon}$",fontsize=12)
    ax.text(.74,.61,r"$b=1,\quad\epsilon=0.3$",fontsize=11)
    ax.set(xlim=(.55,1.85),ylim=(.55,1.8),xlabel=r"$x_1$",ylabel=r"$x_2$")
    for ax in [ax]:
        ax.axhline(0,color="black",lw=.7,zorder=0)
        ax.axvline(0,color="black",lw=.7,zorder=0)
    return fig
