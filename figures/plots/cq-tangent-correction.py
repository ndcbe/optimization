"""Prepared Lecture 20 geometry/proof sketch; analytic inputs, no solver results.
One source serves the handout and Constraint-Qualifications website reference.
Direct labels, line styles and hatches preserve meaning in greyscale.
"""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,ax=plt.subplots(figsize=(5.5,3.6))
    t=np.linspace(-.9,.9,250);x=1-np.sqrt(1-t*t)
    ax.plot(x,t,color='#0072B2',ls='-',label=r'$h=(x_1-1)^2+x_2^2-1=0$')
    ax.plot([0,0],[-.9,.9],color='0.4',ls='--',label='linearized tangent')
    a=.7;xc=1-np.sqrt(1-a*a)
    ax.plot([0,xc],[a,a],color='#D55E00',ls=':',lw=3)
    ax.scatter([0,xc],[a,a],color=['black','#D55E00'],marker='o',s=40,zorder=5)
    ax.annotate('straight step',xy=(0,a),xytext=(-.78,.5),fontsize=11)
    ax.annotate('corrected point',xy=(xc,a),xytext=(.55,.8),fontsize=11)
    ax.scatter([0],[0],color='black',s=35)
    ax.annotate(r'$\bar{\mathbf{x}}$',xy=(0,0),xytext=(-.52,-.15),fontsize=12)
    ax.annotate(r'$O(t^2)$ correction',xy=(.14,.7),xytext=(.45,.18),fontsize=11,arrowprops=dict(arrowstyle='-',color='black',lw=.8))
    ax.axhline(0,color='black',lw=.7);ax.axvline(0,color='black',lw=.7)
    ax.set(xlim=(-.85,1.65),ylim=(-1,1),xlabel='$x_1$',ylabel='$x_2$');ax.set_aspect('equal')
    ax.text(.78,-.35,'circle',color='#0072B2',fontsize=12)
    ax.text(-.78,-.7,'tangent',color='0.4',fontsize=12)
    fig.tight_layout();return fig
