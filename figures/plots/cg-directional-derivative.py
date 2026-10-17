"""Lecture 22 prepared analytic diagram. Single shared public figure source.
Distinct styles/markers/direct labels retain meaning in greyscale.
These are specified analytic toy inputs, not independent notebook result solves.
"""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,axes=plt.subplots(1,2,figsize=(7.3,2.8))
    a=np.linspace(-.6,.6,241)
    axes[0].plot(a,np.abs(a),ls='-',color='#0072B2',label=r'$|\alpha|$')
    axes[0].plot(a,a,'--',color='#D55E00',label=r'$D_+=1$')
    axes[0].plot(a,-a,':',color='0.3',label=r'$D_-=-1$')
    axes[0].set(xlabel='alpha',ylabel='zero-component norm')
    a=np.linspace(0,.7,150)
    axes[1].plot(a,1-a,'--',color='#0072B2',label=r'$1-\alpha$')
    axes[1].plot(a,1-a+.3*a*a,'-',color='#D55E00',label=r'$1-\alpha+.3\alpha^2$')
    axes[1].set(xlabel='forward alpha',ylabel='residual norm')
    fig.tight_layout()
    for ax in axes:
        ax.legend(fontsize=9,loc='upper center',bbox_to_anchor=(.5,-.34),frameon=False,ncol=3,handlelength=1.1,columnspacing=.8)
    return fig
