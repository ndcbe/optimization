"""Directional slices illustrating the two necessary-condition contradictions.
Left: nonzero slope (1+t)^2 at 0, a descent step to negative t.
Right: zero slope but negative curvature -t^2, with descent in either direction.
Neither pictured candidate is a local minimizer.
"""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,axes=plt.subplots(1,2,figsize=(10,2.65),layout='constrained')
    t=np.linspace(-.7,.7,300)
    for ax,y,title in zip(axes,[(1+t)**2,-t*t],['Nonzero slope','Negative curvature at stationarity']):
        ax.plot(t,y,color='#0072B2',linestyle='-',linewidth=2)
        y0=1 if title=='Nonzero slope' else 0
        ax.plot(0,y0,marker='o',color='black',markersize=6)
        target=(-.4,.6**2) if y0 else (.4,-.16)
        ax.annotate('Lower value',xy=target,xytext=(-.6,2.25) if y0 else (-.62,-.35),
                    arrowprops={'arrowstyle':'->','color':'#D55E00'},fontsize=10)
        ax.set(xlabel='$t$',title=title)
        ax.set_ylabel(r'$\psi(t)$',fontsize=12)
        ax.axvline(0,color='0.6',linestyle=':',linewidth=.8)
        ax.tick_params(labelsize=9)
    return fig
