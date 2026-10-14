"""Prepared Lecture 21 definition/proof illustration; analytic toy inputs.
Shared public figure pipeline; no independent recomputation of notebook results.
Line styles, markers, direct labels and hatches retain meaning in greyscale.
"""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,axes=plt.subplots(1,2,figsize=(7.2,2.8))
    t=np.linspace(0,.45,150)
    axes[0].plot(t,.6*t*t,color='#0072B2',ls='-',label='feasible corrected path')
    axes[0].plot(t,0*t,color='#D55E00',ls='--',label='linear tangent')
    axes[0].set(xlabel='$x_1$',ylabel='$x_2$');axes[0].legend(fontsize=10,loc='upper left')
    axes[1].plot(t,-t*t,color='#0072B2',ls='--',label=r'quadratic: $-t^2$')
    axes[1].plot(t,-t*t+t**3,color='#D55E00',ls='-',label=r'change: $-t^2+t^3$')
    axes[1].axhline(0,color='0.5',lw=1);axes[1].set(xlabel=r'path scale $t$',ylabel=r'$f(\mathbf{z}(t))-f(\mathbf{x}^*)$')
    axes[1].legend(fontsize=10,loc='lower left');fig.tight_layout();return fig
