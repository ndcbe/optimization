"""Prepared Lecture 21 definition/proof illustration; analytic toy inputs.
Shared public figure pipeline; no independent recomputation of notebook results.
Line styles, markers, direct labels and hatches retain meaning in greyscale.
"""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,axes=plt.subplots(1,2,figsize=(7.2,2.8))
    k=np.arange(2,10);rr=1/k;th=.9+.4/k;pp=np.c_[np.cos(th),np.sin(th)]
    axes[0].scatter(*(rr[:,None]*pp).T,color='#0072B2',marker='o',label=r'points $\mathbf{z}^k$')
    axes[0].plot([0,.32],[0,.32*np.tan(.9)],color='#D55E00',ls='--',label=r'limit direction $\mathbf{p}$')
    axes[0].scatter([0],[0],color='black',marker='*',s=65);axes[0].text(.025,-.03,r'$\mathbf{x}^*$',fontsize=12)
    axes[0].set(xlim=(-.06,.37),ylim=(-.06,.51),xlabel='$x_1$',ylabel='$x_2$');axes[0].axhline(0,color='black',lw=.7);axes[0].axvline(0,color='black',lw=.7)
    x=np.arange(2,14);axes[1].plot(x,.5+1/x,color='#0072B2',marker='o',label=r'$\frac{1}{2}\mathbf{p}_k^T\mathbf{W}\mathbf{p}_k+o(1)$')
    axes[1].axhline(.5,color='#D55E00',ls='--',label=r'positive limit $\frac{1}{2}\mathbf{p}^T\mathbf{W}\mathbf{p}$')
    axes[1].axhline(0,color='black',lw=1.4);axes[1].fill_between(x,-.18,0,facecolor='0.85',edgecolor='0.5',hatch='//',alpha=.4)
    axes[1].text(3,-.13,'required by lower-value points',fontsize=10)
    axes[1].set(xlabel=r'subsequence index $k$',ylabel='scaled change',ylim=(-.23,1.05))
    fig.tight_layout()
    for ax in axes:
        ax.legend(fontsize=10,loc='upper center',bbox_to_anchor=(.5,-.36),frameon=False)
    return fig
