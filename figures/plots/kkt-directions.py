"""Constraint geometry and its linearization for Biegler Example 4.5."""
import numpy as np
import matplotlib.pyplot as plt
def make_figure():
    fig,axs=plt.subplots(1,2,figsize=(7.2,3.0),layout="constrained")
    a=np.sqrt(2);x=np.linspace(.8,2.05,250)
    axs[0].fill_between(x,4/x,5.15,facecolor=(.337,.706,.914,.18),hatch='//',edgecolor='0.6',linewidth=0)
    axs[0].plot(x,4/x,color="#D55E00",linestyle="--",linewidth=1.8)
    axs[0].plot(x,2*x,color="#0072B2",linestyle="-",linewidth=1.8)
    axs[0].plot(a,2*a,'o',color="black",ms=5)
    axs[0].annotate("",xy=(a+.3,2*a+.6),xytext=(a,2*a),arrowprops=dict(arrowstyle='->',color="#0072B2",lw=2))
    axs[0].annotate(r"$g=0$",xy=(.98,4/.98),xytext=(1.10,4.75),fontsize=12,arrowprops=dict(arrowstyle="->",color="black"))
    axs[0].annotate(r"$h=0$",xy=(1.8,3.6),xytext=(1.32,3.95),fontsize=12,arrowprops=dict(arrowstyle="->",color="black"))
    axs[0].text(1.72,4.70,"feasible\n"+r"$g\leq0$",fontsize=9,bbox=dict(facecolor="white",edgecolor="none",pad=1))
    axs[0].annotate(r"step $0.3\mathbf{p}$",xy=(a+.25,2*a+.5),xytext=(1.14,1.91),fontsize=9,arrowprops=dict(arrowstyle='->',lw=.8))
    axs[0].set(xlim=(.8,2.1),ylim=(1.6,5.15),xlabel=r"$x_1$",ylabel=r"$x_2$",title="constraints in x space")
    q=np.linspace(-1.2,1.2,50)
    axs[1].fill_between(q,-2*q,2.4,facecolor=(.337,.706,.914,.18),hatch='//',edgecolor='0.6',linewidth=0)
    axs[1].plot(q,2*q,color="#0072B2",linestyle="-",lw=1.5)
    axs[1].plot(q,-2*q,color="#D55E00",linestyle="--",lw=1.5)
    axs[1].plot(0,0,'o',color="black",ms=5)
    axs[1].annotate("",xy=(1,2),xytext=(0,0),arrowprops=dict(arrowstyle='->',color="black",lw=2))
    axs[1].text(.05,2.12,r"$\mathbf{p}=(1,2)^T$",fontsize=10,bbox=dict(facecolor="white",edgecolor="none",pad=1))
    axs[1].annotate(r"$2p_1-p_2=0$",xy=(-.7,-1.4),xytext=(-1.15,-.50),fontsize=9,arrowprops=dict(arrowstyle='->',lw=.8))
    axs[1].annotate(r"$2p_1+p_2=0$",xy=(-.7,1.4),xytext=(-1.18,.6),fontsize=9,arrowprops=dict(arrowstyle='->',lw=.8))
    axs[1].text(.35,-.40,"feasible side\nof inequality",fontsize=8,bbox=dict(facecolor="white",edgecolor="none",pad=1))
    axs[1].set(xlim=(-1.25,1.25),ylim=(-2.4,2.4),xlabel=r"$p_1$",ylabel=r"$p_2$",title="first-order directions")
    for ax in axs:
        ax.axhline(0,color="black",lw=.7,zorder=0)
        ax.axvline(0,color="black",lw=.7,zorder=0)
    return fig
