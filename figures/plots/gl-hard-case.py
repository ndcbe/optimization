"""Prepared globalization teaching geometry; numerical checks are in make_figure."""
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import brentq

def make_figure():

    B=np.diag([-1.,2.]);g=np.array([0.,1.]);base=np.array([0.,-1/3]);tau=np.sqrt(8/9)
    candidates=[base+np.array([sgn*tau,0]) for sgn in [-1,1]]
    model=lambda p:g@p+.5*p@B@p
    for p in candidates:
        assert abs(np.linalg.norm(p)-1)<1e-12
        assert np.linalg.norm((B+np.eye(2))@p+g)<1e-12
        assert abs(model(p)+2/3)<1e-12
    fig,axs=plt.subplots(1,2,figsize=(7.8,3.4),layout='constrained')
    d=np.linspace(1,5,200);axs[0].plot(d,1/(2+d),color='#0072B2',linestyle='-',linewidth=2)
    axs[0].axhline(1,color='#D55E00',linestyle='--',linewidth=1.5)
    axs[0].plot(1,1/3,'o',color='#0072B2',ms=6,mfc='white')
    axs[0].text(2.7,.87,r'target radius $\Delta=1$',fontsize=10)
    axs[0].text(2.5,.32,r'$\|\mathbf{p}(\delta)\|=1/(2+\delta)$',fontsize=10)
    axs[0].set(xlim=(.85,5.1),ylim=(0,1.15),xlabel=r'shift $\delta>1$',ylabel='step norm')
    axs[0].set_title('Shifted solve stays inside',fontsize=11)
    x,y=np.meshgrid(np.linspace(-1.2,1.2,200),np.linspace(-1.2,1.2,200));z=y-.5*x*x+y*y
    axs[1].contour(x,y,z,levels=[-.66,-.6,-.5,-.3,0,.5,1],colors='0.65',linewidths=.7)
    t=np.linspace(0,2*np.pi,250);axs[1].plot(np.cos(t),np.sin(t),color='0.3',linestyle='--')
    axs[1].plot(*base,'s',color='#0072B2',ms=6)
    for p in candidates:
        axs[1].annotate('',xy=p,xytext=base,arrowprops=dict(arrowstyle='->',color='#D55E00',linewidth=2))
        axs[1].plot(*p,'D',color='#D55E00',ms=6)
    axs[1].annotate(r'$\widehat{\mathbf{p}}$',xy=base,xytext=(.2,.12),arrowprops=dict(arrowstyle='->'),fontsize=11)
    axs[1].text(-1.12,-.93,r'add $\pm\sqrt{8/9}\,\mathbf{e}_1$',fontsize=11,bbox=dict(facecolor='white',edgecolor='none',alpha=.85))
    axs[1].set(xlim=(-1.2,1.2),ylim=(-1.2,1.2),aspect='equal',xlabel='$p_1$',ylabel='$p_2$')
    axs[1].set_title('Add negative curvature',fontsize=11)
    return fig
