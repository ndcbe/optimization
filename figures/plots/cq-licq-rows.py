"""Prepared Lecture 20 geometry/proof sketch; analytic inputs, no solver results.
One source serves the handout and Constraint-Qualifications website reference.
Direct labels, line styles and hatches preserve meaning in greyscale.
"""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,axes=plt.subplots(1,3,figsize=(7.8,2.8))
    for number,(ax,vs,title) in enumerate(zip(axes,[[(1,0),(0,1)],[(1,0),(1.6,0)],[(0,1),(0,-1)]],['(1)','(2)','(3)'])):
        for i,v in enumerate(vs):
            ax.annotate('',xy=v,xytext=(0,0),arrowprops=dict(arrowstyle='->',color=['#0072B2','#D55E00'][i],lw=3))
            off=[(0,.16),(.13,0)][i]
            if number==1:off=[(0,.2),(0,-.3)][i]
            ax.text(v[0]+off[0],v[1]+off[1],rf'$\mathbf{{a}}_{i+1}$',fontsize=13)
        ax.axhline(0,color='black',lw=.7);ax.axvline(0,color='black',lw=.7)
        ax.set(xlim=(-.5,2),ylim=(-1.5,1.6));ax.set_aspect('equal');ax.set_xticks([]);ax.set_yticks([])
        ax.set_title(title,fontsize=11)
    fig.tight_layout();return fig
