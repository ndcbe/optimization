"""Lecture22 supplied objective/violation pairs; one shared plotting owner."""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,ax=plt.subplots(figsize=(7.2,2.1))
    v=np.linspace(0,4.6,150)
    ax.plot(v,7-2*v,color='black',ls='--',label='_nolegend_')
    points=[('Current',2,3,'*','black',(.05,1.4)),('A',4,1,'^','#0072B2',(-.5,1.25)),('B',1,4,'s','#D55E00',(-.5,.72)),('C',1.8,2.5,'o','#009E73',(-.3,-1.2))]
    for label,x,y,marker,color,offset in points:
        ax.scatter(x,y,s=75,marker=marker,color=color,zorder=3)
        ax.annotate(f'{label} ({x:g}, {y:g})',xy=(x,y),xytext=(x+offset[0],y+offset[1]),fontsize=10,arrowprops=dict(arrowstyle='-',lw=.7,color='black'))
    ax.set(xlabel=r'violation $\|\mathbf{h}\|_1$',ylabel=r'objective $f$',xlim=(0,4.65),ylim=(-.2,5.1))
    ax.annotate(r'$f+2\|\mathbf{h}\|_1=7$',xy=(2.8,1.4),xytext=(3.0,3.8),fontsize=10,arrowprops=dict(arrowstyle='-',lw=.7,color='black'));fig.tight_layout();return fig
