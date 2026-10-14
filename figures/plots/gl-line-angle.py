"""Prepared globalization teaching geometry; numerical checks are in make_figure."""
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import brentq

def make_figure():

    g=np.array([1.,0.]);matrices=[np.array([[1.,.2],[.2,1.]]),np.array([[100.,10.],[10.,1.1]])]
    fig,axs=plt.subplots(1,2,figsize=(7.8,3.3),layout='constrained')
    for ax,B,title in zip(axs,matrices,['Well-conditioned model','Poorly conditioned model']):
        p=-np.linalg.solve(B,g);cos=-g@p/(np.linalg.norm(g)*np.linalg.norm(p));kap=np.linalg.cond(B)
        assert cos>=1/kap-1e-12 and np.linalg.eigvalsh(B).min()>0
        v=p/np.linalg.norm(p)
        ax.annotate('',xy=(-1,0),xytext=(0,0),arrowprops=dict(arrowstyle='->',color='black',linewidth=2))
        ax.annotate('',xy=v,xytext=(0,0),arrowprops=dict(arrowstyle='->',color='#0072B2',linewidth=2))
        ax.text(-1.08,-.18,r'$-\mathbf{g}$',fontsize=11);ax.text(v[0]+.08,v[1]+.04,r'$\mathbf{p}/\|\mathbf{p}\|$',fontsize=11)
        angle=np.arctan2(v[1],v[0]);t=np.linspace(angle,np.pi,100)
        ax.plot(.32*np.cos(t),.32*np.sin(t),color='#D55E00',linestyle='--',linewidth=1.5)
        ax.text(-.5,.23,r'$\vartheta$',fontsize=12)
        ax.text(-1.13,.94,f'$\\cos\\vartheta={cos:.3f}$',fontsize=11)
        ax.set(xlim=(-1.3,.55),ylim=(-.3,1.25),aspect='equal');ax.axis('off');ax.set_title(title,fontsize=12)
    return fig
