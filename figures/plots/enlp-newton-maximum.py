"""Prepared Lecture 21 definition/proof illustration; analytic toy inputs.
Shared public figure pipeline; no independent recomputation of notebook results.
Line styles, markers, direct labels and hatches retain meaning in greyscale.
"""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,ax=plt.subplots(figsize=(6.3,2.7));t=np.linspace(-1.2,1.2,160)
    ax.plot(t,-t*t,color='#0072B2',ls='-');ax.scatter([1,0],[-1,0],color=['#D55E00','black'],marker='o',zorder=5)
    ax.annotate('',xy=(0,.21),xytext=(1,.21),arrowprops=dict(arrowstyle='->',color='#D55E00',lw=2));ax.text(.30,.28,'step in $x_1$',fontsize=12);ax.plot([1,1],[-1,.21],color='black',ls=':',lw=.8)
    ax.text(.72,-1.25,r'$x_1^0=a$',fontsize=12);ax.annotate('stationarity\nroot',xy=(0,0),xytext=(-1.1,-.15),fontsize=12,va='top',arrowprops=dict(arrowstyle='-',color='black',lw=.7));ax.axhline(0,color='black',lw=.7);ax.axvline(0,color='black',lw=.7)
    ax.set(xlabel=r'feasible coordinate $x_1$ ($x_2=0$)',ylabel=r'$f=-x_1^2$',ylim=(-1.55,.43));fig.tight_layout();return fig
