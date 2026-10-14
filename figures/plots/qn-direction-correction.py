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
    fig,axs=plt.subplots(1,2,figsize=(7.8,3.3),layout='constrained')
    xx,yy=np.meshgrid(np.linspace(-3,3,220),np.linspace(-2,2,200))
    for ax,B,title,p in zip(axs,[np.diag([-2.,4.]),np.diag([1.,7.])],['Exact Hessian model','Shifted model'],[[-1.,0.],[2.,0.]]):
        z=-2*xx+.5*B[0,0]*xx**2+.5*B[1,1]*yy**2
        ax.contour(xx,yy,z,levels=[-3,-1,0,1,3,6],colors='0.65',linewidths=.8)
        axes(ax,(-3,3),(-2,2));ax.plot(0,0,'ko',markersize=4)
        arrow(ax,[0,0],[-2,0],r'$\mathbf{g}$',(.05,.25),'#0072B2')
        arrow(ax,[0,0],p,r'$\mathbf{p}$',(.1,-.45),'#D55E00')
        ax.set_title(title,fontsize=12);ax.set_xlabel('$p_1$',fontsize=12);ax.set_ylabel('$p_2$',fontsize=12)
    return fig
