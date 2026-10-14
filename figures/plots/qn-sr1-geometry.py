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
    fig,axs=plt.subplots(1,2,figsize=(7,3.0),layout='constrained')
    for ax,u,title in zip(axs,[[1,1],[-1,1]],['Positive projection','Negative projection']):
        axes(ax,(-1.6,1.6),(-.3,1.7))
        arrow(ax,[0,0],[1,0],r'$\mathbf{s}$',(.12,0),'black')
        arrow(ax,[0,0],u,r'$\mathbf{u}$',(.04,.12),'#0072B2')
        ax.plot([u[0],u[0]],[0,u[1]],':',color='0.5')
        ax.plot(u[0],0,'s',color='#D55E00',markersize=5)
        ax.set_title(title,fontsize=12)
    return fig
