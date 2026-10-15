"""Compactness step in the multiplier proof, illustrated in two dimensions."""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,axs=plt.subplots(1,2,figsize=(7.2,2.6),layout="constrained")
    angles=np.deg2rad([60,50,44]);radii=[1.4,2.3,3.2]
    for i,(a,r) in enumerate(zip(angles,radii)):
        point=r*np.array([np.cos(a),np.sin(a)])
        axs[0].plot([0,point[0]],[0,point[1]],color='0.55',ls='--',lw=.8)
        axs[0].plot(*point,'o',color='#0072B2',ms=5)
        texts=[(.1,1.75),(.65,2.7),(2.3,2.8)]
        axs[0].annotate(rf'$\boldsymbol{{\lambda}}^{{{i+1}}}$',xy=point,xytext=texts[i],fontsize=12,arrowprops=dict(arrowstyle='-',color='black',lw=.7))
    theta=np.linspace(0,2*np.pi,200);axs[1].plot(np.cos(theta),np.sin(theta),color='black',ls='--',lw=1)
    for a in angles:axs[1].plot(np.cos(a),np.sin(a),'o',color='#0072B2',ms=5)
    a=np.deg2rad(40);end=(np.cos(a),np.sin(a));axs[1].plot(*end,'*',color='black',ms=10)
    axs[1].annotate(r'$\widehat{\boldsymbol{\lambda}}$',xy=end,xytext=(.93,.91),fontsize=13,arrowprops=dict(arrowstyle='-',color='black',lw=.8))
    axs[0].set(xlim=(-.15,3.5),ylim=(-.15,3.2),title='hypothetical unbounded sequence',xlabel=r'$\lambda_1$',ylabel=r'$\lambda_2$')
    axs[1].set(xlim=(-1.2,1.45),ylim=(-1.2,1.3),title=r'divide by $\|\boldsymbol{\lambda}^k\|$',xlabel=r'$\widehat{\lambda}_1$',ylabel=r'$\widehat{\lambda}_2$')
    for ax in axs:ax.set_aspect('equal');ax.axhline(0,color='black',lw=.7);ax.axvline(0,color='black',lw=.7)
    return fig
