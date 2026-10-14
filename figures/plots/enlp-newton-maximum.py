"""Prepared Lecture 21 definition/proof illustration; analytic toy inputs.
Shared public figure pipeline; no independent recomputation of notebook results.
Line styles, markers, direct labels and hatches retain meaning in greyscale.
"""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,ax=plt.subplots(figsize=(6.3,2.7));t=np.linspace(-1.2,1.2,160)
    ax.plot(t,-t*t,color='#0072B2',ls='-');ax.scatter([1,0],[-1,0],color=['#D55E00','black'],marker='o',zorder=5)
    ax.annotate('Newton step',xy=(0,0),xytext=(.75,-.3),fontsize=12,arrowprops=dict(arrowstyle='->',color='#D55E00',lw=2))
    ax.text(.91,-1.15,r'$x_1^0=a$',fontsize=12);ax.text(-.43,.05,'stationarity root',fontsize=12)
    ax.set(xlabel=r'feasible coordinate $x_1$ ($x_2=0$)',ylabel=r'$f=-x_1^2$',ylim=(-1.55,.3));fig.tight_layout();return fig
