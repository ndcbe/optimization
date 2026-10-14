"""Directional agreement need not imply agreement in every matrix entry.
G=diag(1,2), B=diag(1,10). On p=e1 both give (1,0); on e2 they differ.
This illustrates a matrix-action condition, not an observed convergence rate.
"""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,axs=plt.subplots(1,2,figsize=(8.2,2.8),layout='constrained')
    G=np.diag([1.,2.]);B=np.diag([1.,10.])
    for ax,v,title in zip(axs,[np.array([1.,0.]),np.array([0.,1.])],
                         [r'Step $\mathbf{p}=\mathbf{e}_1$',r'Other direction $\mathbf{v}=\mathbf{e}_2$']):
        ax.axhline(0,color='black',linewidth=.7)
        ax.axvline(0,color='black',linewidth=.7)
        for matrix,color,ls,label,lw in [(G,'#0072B2','-',r'$\mathbf{G}$ action',3.),
                                       (B,'#D55E00','--',r'$\mathbf{B}$ action',1.8)]:
            q=matrix@v
            ax.plot([0,q[0]],[0,q[1]],color=color,linestyle=ls,linewidth=lw,label=label)
            ax.plot(*q,marker='o' if matrix is G else 's',markerfacecolor='none',
                    markeredgecolor=color,markersize=7,markeredgewidth=1.5)
        ax.set_title(title,fontsize=12)
        ax.tick_params(labelsize=10)
        ax.set_xlabel('action component 1',fontsize=11)
        ax.set_ylabel('action component 2',fontsize=11)
    axs[0].set(xlim=(-.15,1.3),ylim=(-.5,.65));axs[0].set_yticks([0,.5])
    axs[0].text(.5,.36,r'$\mathbf{G p}=\mathbf{B p}=(1,0)^{T}$',ha='center',fontsize=11)
    axs[0].legend(loc='lower left',fontsize=10)
    axs[1].set(xlim=(-.55,.85),ylim=(-.6,11));axs[1].set_xticks([0,.5])
    axs[1].text(.12,2,r'$\mathbf{Gv}=(0,2)^T$',fontsize=11,va='center')
    axs[1].text(.12,9.6,r'$\mathbf{Bv}=(0,10)^T$',fontsize=11,va='center')
    return fig
