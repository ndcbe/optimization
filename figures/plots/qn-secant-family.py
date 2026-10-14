"""Prepared quasi-Newton teaching visual; all geometry is given in make_figure."""
import numpy as np
import matplotlib.pyplot as plt

def arrow(ax,start,end,label,offset=(0,0),color='black'):
    ax.annotate('',xy=end,xytext=start,arrowprops=dict(arrowstyle='->',color=color,linewidth=2))
    end=np.asarray(end);ax.text(*(end+offset),label,fontsize=11,color=color)

def axes(ax,lim=(-2,3),ylim=(-2,3)):
    ax.axhline(0,color='0.7',linewidth=.7);ax.axvline(0,color='0.7',linewidth=.7)
    ax.set(xlim=lim,ylim=ylim,aspect='equal');ax.tick_params(labelsize=10)

def make_figure():
    fig,axs=plt.subplots(1,3,figsize=(8,3.0),layout='constrained')
    for ax,c in zip(axs,[0,1,3]):
        axes(ax,(-.3,2.8),(-.4,3.5))
        arrow(ax,[0,0],[2,1],r'$\mathbf{B}\mathbf{e}_1$',(.05,.05),'#0072B2')
        arrow(ax,[0,0],[1,c],r'$\mathbf{B}\mathbf{e}_2$',(.05,.18),'#D55E00')
        ax.set_title('$c='+str(c)+'$',fontsize=12);ax.set_xlabel('output component 1',fontsize=10)
        ax.set_ylabel('output component 2',fontsize=10)
    return fig
