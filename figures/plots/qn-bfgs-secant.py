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
    fig,ax=plt.subplots(figsize=(6.5,3.1),layout='constrained')
    axes(ax,(-.3,3.8),(-.4,1.8))
    arrow(ax,[0,0],[1,0],r'$\mathbf{B}\mathbf{s}$',(-.35,-.27),'black')
    arrow(ax,[1,0],[3,1],r'$+\mathbf{y}$',(.05,-.12),'#D55E00')
    arrow(ax,[3,1],[2,1],r'$-\mathbf{B}\mathbf{s}$',(.1,.2),'#009E73')
    arrow(ax,[0,0],[2,1],r'$\mathbf{y}$',(-.32,-.22),'#0072B2')
    ax.set_xlabel('component 1',fontsize=12);ax.set_ylabel('component 2',fontsize=12)
    return fig
