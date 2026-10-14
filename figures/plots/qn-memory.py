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
    from matplotlib.patches import Rectangle
    fig,axs=plt.subplots(1,2,figsize=(7,2.8),layout='constrained')
    for ax in axs:ax.axis('off');ax.set(xlim=(0,6),ylim=(0,5))
    for i in range(4):
        for j in range(4):axs[0].add_patch(Rectangle((1+i*.7,1+j*.7),.7,.7,facecolor='#c9e8f2',edgecolor='white'))
    axs[0].text(2.4,4.35,'Full matrix',ha='center',fontsize=12)
    axs[0].text(2.4,.35,r'$n^2$ values',ha='center',fontsize=12)
    for i in range(3):
        axs[1].add_patch(Rectangle((.7,1+i*.9),1.8,.55,facecolor='#c9e8f2',edgecolor='black'))
        axs[1].add_patch(Rectangle((3.0,1+i*.9),1.8,.55,facecolor='#f8d3b3',edgecolor='black'))
    axs[1].text(1.6,3.65,r'$\mathbf{s}$ vectors',ha='center',fontsize=11)
    axs[1].text(3.9,3.65,r'$\mathbf{y}$ vectors',ha='center',fontsize=11)
    axs[1].text(2.75,4.35,'Last $m$ pairs',ha='center',fontsize=12)
    axs[1].text(2.75,.35,r'$2mn$ values',ha='center',fontsize=12)
    return fig
