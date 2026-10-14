"""Exact one-dimensional local/global role of an inactive constraint."""
import numpy as np
import matplotlib.pyplot as plt
def make_figure():
    fig,ax=plt.subplots(figsize=(6.6,2.8),layout="constrained")
    x=np.linspace(-1.65,1.65,600);f=lambda x:(x*x-1)**2+.1*(3*x-x**3)
    ax.axvspan(0,1.65,facecolor="#56B4E9",alpha=.17,hatch="//",edgecolor="0.7")
    ax.plot(x,f(x),color="black",linestyle="-",linewidth=1.7)
    ax.axvline(0,color="0.4",linestyle="--",linewidth=1)
    ax.plot(1,f(1),'o',color="#0072B2",ms=7);ax.plot(-1,f(-1),'s',color="#D55E00",ms=7)
    ax.plot([.7,1.3],[-.4,-.4],color="#0072B2",linestyle="--",linewidth=2)
    ax.text(.55,1.85,r"$g(x)=-x\leq0$",fontsize=12)
    ax.annotate(r"$x^*=1$",xy=(1,f(1)),xytext=(.8,.8),arrowprops=dict(arrowstyle='->'),fontsize=12)
    ax.annotate(r"$x=-1$",xy=(-1,f(-1)),xytext=(-1.5,.5),arrowprops=dict(arrowstyle='->'),fontsize=12)
    ax.set(xlim=(-1.65,1.65),ylim=(-.6,2.9),xlabel="decision x",ylabel="objective f(x)")
    for ax in [ax]:
        ax.axhline(0,color="black",lw=.7,zorder=0)
        ax.axvline(0,color="black",lw=.7,zorder=0)
    return fig
