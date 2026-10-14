"""Prepared globalization teaching geometry; numerical checks are in make_figure."""
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import brentq

def make_figure():

    B=np.diag([1.,10.]);g=np.array([2.,6.]);D=1.0
    pN=-np.linalg.solve(B,g)
    delta=brentq(lambda d:np.linalg.norm(np.linalg.solve(B+d*np.eye(2),g))-D,0,20)
    pT=-np.linalg.solve(B+delta*np.eye(2),g)
    pL=D*pN/np.linalg.norm(pN)
    assert np.linalg.norm(pT-pL)>.05 and abs(np.linalg.norm(pT)-D)<1e-10
    fig,axs=plt.subplots(1,2,figsize=(7.8,3.4),layout='constrained')
    x,y=np.meshgrid(np.linspace(-2.5,1.6,200),np.linspace(-1.6,1.6,180))
    z=2*x+6*y+.5*x*x+5*y*y
    t=np.linspace(0,2*np.pi,200)
    for ax in axs:
        ax.contour(x,y,z,levels=[-3.5,-3,-2,-1,0,1],colors='0.65',linewidths=.7)
        ax.plot(0,0,'ko',ms=4);ax.plot(*pN,'ks',ms=5)
        ax.text(pN[0]-.25,pN[1]-.3,r'$\mathbf{p}^N$',fontsize=11)
        ax.set(xlim=(-2.5,1.6),ylim=(-1.6,1.6),aspect='equal',xlabel='$p_1$',ylabel='$p_2$')
    axs[0].plot([0,pN[0]],[0,pN[1]],color='#0072B2',linestyle='--',linewidth=2)
    axs[0].plot(*pL,'o',color='#0072B2',ms=7)
    axs[0].text(pL[0]+.08,pL[1]+.15,r'$\alpha\mathbf{p}^N$',fontsize=11)
    axs[0].set_title('Line search: one fixed ray',fontsize=12)
    axs[1].fill(D*np.cos(t),D*np.sin(t),facecolor='#56B4E9',alpha=.12)
    axs[1].plot(D*np.cos(t),D*np.sin(t),color='0.35',linestyle='--',linewidth=1.2)
    axs[1].plot(*pT,'D',color='#D55E00',ms=7)
    axs[1].annotate(r'$\mathbf{p}^{TR}$',xy=pT,xytext=(-.75,-1.15),arrowprops=dict(arrowstyle='->'),fontsize=11)
    axs[1].text(.03,1.2,r'$\|\mathbf{p}\|\leq\Delta$',fontsize=11)
    axs[1].set_title('Trust region: choose within a ball',fontsize=12)
    return fig
