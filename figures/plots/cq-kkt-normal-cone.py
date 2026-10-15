"""Prepared Lecture 20 geometry/proof sketch; analytic inputs, no solver results.
One source serves the handout and Constraint-Qualifications website reference.
Direct labels, line styles and hatches preserve meaning in greyscale.
"""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,ax=plt.subplots(figsize=(5.8,3.2))
    ax.fill_between([0,2.6],0,1.9,facecolor='0.9',edgecolor='0.7',hatch='//',alpha=.4)
    for v,label,col,off in [((-1,0),r'$\nabla g_1=(-1,0)^T$','#0072B2',(-.2,.18)),((0,-1),r'$\nabla g_2=(0,-1)^T$','#D55E00',(.1,-.15)),((2,1),r'$\nabla f=(2,1)^T$','black',(-.9,.2))]:
        ax.annotate('',xy=v,xytext=(0,0),arrowprops=dict(arrowstyle='->',color=col,lw=3))
        ax.text(v[0]+off[0],v[1]+off[1],label,fontsize=11)
    ax.set(xlim=(-1.6,2.7),ylim=(-1.7,1.9),xlabel='$x_1$',ylabel='$x_2$');ax.set_aspect('equal')
    ax.axhline(0,color='black',lw=.7);ax.axvline(0,color='black',lw=.7)
    ax.text(1,.25,r'$S:\ x_1,x_2\geq0$',fontsize=12);fig.tight_layout();return fig
