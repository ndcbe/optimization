"""Prepared quasi-Newton teaching visual; all geometry is given in make_figure."""
import numpy as np
import matplotlib.pyplot as plt

def arrow(ax,start,end,label,offset=(0,0),color='black'):
    ax.annotate('',xy=end,xytext=start,arrowprops=dict(arrowstyle='->',color=color,linewidth=2))
    end=np.asarray(end);ax.text(*(end+offset),label,fontsize=11,color=color)

def axes(ax,lim=(-2,3),ylim=(-2,3)):
    ax.axhline(0,color='black',linewidth=.7);ax.axvline(0,color='black',linewidth=.7)
    ax.set(xlim=lim,ylim=ylim,aspect='equal');ax.tick_params(labelsize=10)

def make_figure():
    fig,ax=plt.subplots(figsize=(6.2,3.2),layout='constrained')
    axes(ax,(-1.6,1.7),(-.3,1.6))
    ax.axvspan(.2,1.7,facecolor='0.94',hatch='///',edgecolor='0.8')
    ax.axvline(.2,color='0.5',linestyle='--');ax.text(.27,1.4,r'$\mathbf{s}^{T}\bar{\mathbf{y}}\geq0.2$',fontsize=11)
    ax.plot([-1,1],[1,0],color='#0072B2',linestyle='-',linewidth=2)
    for xy,label,off in [([-1,1],r'$\mathbf{y}$',(-.25,.12)),([1,0],r'$\mathbf{B}\mathbf{s}$',(.04,.1)),([.2,.4],r'$\bar{\mathbf{y}}$',(.13,.03))]:
        ax.plot(*xy,'o',color='black',markersize=5);ax.text(xy[0]+off[0],xy[1]+off[1],label,fontsize=12)
    ax.set_xlabel(r'component along $\mathbf{s}=\mathbf{e}_1$',fontsize=12);ax.set_ylabel('second component',fontsize=12)
    return fig
