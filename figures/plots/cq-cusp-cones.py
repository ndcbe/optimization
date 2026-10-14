"""Prepared Lecture 20 geometry/proof sketch; analytic inputs, no solver results.
One source serves the handout and Constraint-Qualifications website reference.
Direct labels, line styles and hatches preserve meaning in greyscale.
"""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,axes=plt.subplots(1,2,figsize=(7.2,2.8),sharex=True,sharey=True)
    t=np.linspace(0,1,200)
    for ax in axes:
        ax.fill_between(t,-t**3,t**3,facecolor='0.85',edgecolor='0.5',hatch='//',alpha=.4)
        ax.plot(t,t**3,color='#0072B2',ls='-');ax.plot(t,-t**3,color='#D55E00',ls='--')
        ax.scatter([0],[0],color='black',s=35,zorder=4)
        ax.set(xlim=(-1.15,1.15),ylim=(-1.15,1.15),xlabel='$x_1$',ylabel='$x_2$')
        ax.set_aspect('equal');ax.set_xticks([-1,0,1]);ax.set_yticks([-1,0,1])
    axes[0].annotate('',xy=(1,0),xytext=(0,0),arrowprops=dict(arrowstyle='->',color='black',lw=3))
    axes[0].set_title(r'Actual tangent cone $T_S$',fontsize=12)
    axes[1].annotate('',xy=(1,0),xytext=(-1,0),arrowprops=dict(arrowstyle='<->',color='black',lw=3))
    axes[1].set_title(r'Linearized cone $L_S$',fontsize=12)
    fig.tight_layout();return fig
