"""Lecture 22 prepared analytic diagram. Single shared public figure source.
Distinct styles/markers/direct labels retain meaning in greyscale.
These are specified analytic toy inputs, not independent notebook result solves.
"""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,axes=plt.subplots(1,2,figsize=(7.3,2.8))
    r=np.linspace(0,.5,150)
    axes[0].plot(r,r*r,'-',color='#0072B2',label=r'$Cr^2$')
    axes[0].plot(r,r,'--',color='#D55E00',label=r'$r$')
    axes[0].set(xlabel='distance r',ylabel='scale')
    axes[1].plot(r,r*r,'-',color='#0072B2',label=r'$r^2$')
    axes[1].plot(r,-r**3,'--',color='#D55E00',label=r'$-r^3$')
    axes[1].plot(r,r*r-r**3,':',color='black',label=r'$r^2-r^3$')
    axes[1].axhline(0,lw=1,color='black');axes[1].set(xlabel='distance r',ylabel='merit change model')
    fig.tight_layout()
    for ax in axes:
        ax.legend(fontsize=9,loc='upper center',bbox_to_anchor=(.5,-.34),frameon=False,ncol=3,handlelength=1.1,columnspacing=.8)
    return fig
