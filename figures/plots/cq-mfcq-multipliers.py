"""Prepared Lecture 20 geometry/proof sketch; analytic inputs, no solver results.
One source serves the handout and Constraint-Qualifications website reference.
Direct labels, line styles and hatches preserve meaning in greyscale.
"""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,axes=plt.subplots(1,2,figsize=(7.5,3))
    ax=axes[0];ax.axhline(0,color='black',lw=2,label='$h=x_2=0$')
    ax.annotate('',xy=(1.7,0),xytext=(0,0),arrowprops=dict(arrowstyle='->',color='black',lw=3))
    ax.text(.6,.16,r'$\mathbf{d}=(1,0)^T$',fontsize=12)
    for end,col,dy,lab in [(-1,'#0072B2',.18,r'$\nabla g_1$'),(-2,'#D55E00',-.32,r'$\nabla g_2$')]:
        ax.annotate('',xy=(end,0),xytext=(0,0),arrowprops=dict(arrowstyle='->',lw=3,color=col))
        ax.text(end,dy,lab,fontsize=12)
    ax.set(xlim=(-2.3,2),ylim=(-1,1),xlabel='$x_1$',ylabel='$x_2$');ax.set_title('A shared strict inward direction',fontsize=11)
    ax=axes[1];u=np.linspace(0,1,100);ax.plot(u,(1-u)/2,color='#0072B2',ls='-')
    ax.scatter([0,1],[.5,0],color='black',marker='o',s=40,zorder=4)
    ax.set(xlim=(-.1,1.1),ylim=(-.05,.65),xlabel='$u_1$',ylabel='$u_2$')
    ax.axhline(0,color='black',lw=.7);ax.axvline(0,color='black',lw=.7)
    ax.set_title(r'$u_1+2u_2=1,\quad u_1,u_2\geq0$',fontsize=11)
    fig.tight_layout();return fig
