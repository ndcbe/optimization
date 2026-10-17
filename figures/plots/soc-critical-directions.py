"""Critical directions for f=-x1+x2^2 with g1=x1, g2=x2 at zero."""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,axs=plt.subplots(1,2,figsize=(7.2,1.9),layout="constrained")
    for ax in axs:
        ax.set(xlim=(-1.2,.5),ylim=(-1.15,.45),xlabel='$p_1$',ylabel='$p_2$')
        ax.set_aspect('equal');ax.axhline(0,color='black',lw=.8);ax.axvline(0,color='black',lw=.8)
        ax.set_xticks([-1,0]);ax.set_yticks([-1,0])
    axs[0].fill_between([-1.2,0],[-1.15,-1.15],[0,0],facecolor='0.88',edgecolor='0.6',hatch='//')
    axs[0].set_title(r'$C_1$: first-order feasibility',fontsize=12)
    axs[1].annotate('',xy=(0,-1.05),xytext=(0,0),arrowprops=dict(arrowstyle='->',color='#0072B2',lw=2.8))
    axs[1].plot(0,0,'o',color='black',ms=4)
    axs[1].set_title(r'$C_2$: also zero objective slope',fontsize=12)
    return fig
