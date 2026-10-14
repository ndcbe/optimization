"""Scalar directional slices used in the necessary-condition proofs."""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,axes=plt.subplots(1,2,figsize=(10,2.65),layout='constrained')
    s=np.linspace(-.7,.7,300)
    ys=[.5*(1-s)**2,-s*s]
    titles=[r'Nonzero slope: $\psi(s)=\frac{1}{2}(1-s)^2$',r'Negative curvature: $\psi(s)=-s^2$']
    for j,(ax,y,title) in enumerate(zip(axes,ys,titles)):
        ax.plot(s,y,color='#0072B2',linestyle='-',linewidth=2)
        y0=.5 if j==0 else 0
        ax.plot(0,y0,marker='o',color='black',markersize=6)
        target=(.4,.18) if j==0 else (.4,-.16)
        ax.annotate('Lower value',xy=target,xytext=(.10,1.10) if j==0 else (-.62,.13),
                    arrowprops={'arrowstyle':'->','color':'#D55E00'},fontsize=10)
        ax.set(xlabel='$s$',ylabel=r'$\psi(s)$',title=title)
        if j==1: ax.set_ylim(-.53,.23)
        ax.axvline(0,color='black',linestyle=':',linewidth=.8)
        ax.tick_params(labelsize=9)
    return fig
