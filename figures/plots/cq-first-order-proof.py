"""Prepared Lecture 20 geometry/proof sketch; analytic inputs, no solver results.
One source serves the handout and Constraint-Qualifications website reference.
Direct labels, line styles and hatches preserve meaning in greyscale.
"""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig, ax = plt.subplots(figsize=(6.3,3.0))
    r=np.linspace(0,.42,200)
    ax.plot(r,-r,color='#0072B2',ls='--',label=r'first-order term: $-r$')
    ax.plot(r,-r+2*r*r,color='#D55E00',ls='-',label=r'actual change: $-r+2r^2$')
    ax.fill_between(r,-r,-r+2*r*r,facecolor='0.8',edgecolor='0.4',hatch='//',alpha=.3)
    ax.axhline(0,color='black',lw=1)
    ax.set(xlabel=r'distance $r$ from the proposed minimum',ylabel=r'$f(\mathbf{x}(r))-f(\mathbf{x}^*)$')
    ax.set_ylim(-.46,.18);ax.axvline(0,color='black',lw=.7);ax.legend(fontsize=11,loc='upper right');fig.tight_layout();return fig
