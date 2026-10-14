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
    fig,ax=plt.subplots(figsize=(5.6,3.1),layout='constrained')
    axes(ax,(-2.5,2.5),(-1.8,1.8))
    x=np.linspace(-2.5,2.5,100)
    ax.plot(x,.5*x,color='#0072B2',linewidth=2,label=r'$\mathbf{w}=0$')
    ax.plot([0,0],[-1.8,1.8],color='#D55E00',linestyle='--',linewidth=2,label=r'$\mathbf{s}^{T}\mathbf{z}=0$')
    ax.plot(0,0,'ko',markersize=5);ax.annotate('only common point: origin',xy=(0,0),xytext=(-2.2,-1.45),fontsize=11,arrowprops={'arrowstyle':'->'})
    ax.set_xlabel('$z_1$',fontsize=12);ax.set_ylabel('$z_2$',fontsize=12);ax.legend(loc='upper left',fontsize=11)
    return fig
