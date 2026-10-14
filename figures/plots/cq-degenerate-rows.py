"""Prepared Lecture 20 geometry/proof sketch; analytic inputs, no solver results.
One source serves the handout and Constraint-Qualifications website reference.
Direct labels, line styles and hatches preserve meaning in greyscale.
"""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,ax=plt.subplots(figsize=(5.5,3.1))
    for v,lab,col,off in [((1,0),r'$\mathbf{r}_1=(1,0)$','#0072B2',(-.3,-.24)),((0,1),r'$\mathbf{r}_2=(0,1)$','#D55E00',(-.1,.12)),((1,1),r'$\mathbf{r}_3=(1,1)$','black',(.12,0))]:
        ax.annotate('',xy=v,xytext=(0,0),arrowprops=dict(arrowstyle='->',lw=3,color=col))
        ax.text(v[0]+off[0],v[1]+off[1],lab,fontsize=12)
    ax.plot([1,1],[0,1],color='0.5',ls='--');ax.plot([0,1],[1,1],color='0.5',ls=':')
    ax.set(xlim=(-.3,2),ylim=(-.35,1.45));ax.set_aspect('equal');ax.set_xticks([]);ax.set_yticks([])
    ax.set_title('Rows of a balance Jacobian',fontsize=13);fig.tight_layout();return fig
