"""Lecture 22 prepared analytic diagram. Single shared public figure source.
Distinct styles/markers/direct labels retain meaning in greyscale.
These are specified analytic toy inputs, not independent notebook result solves.
"""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,axes=plt.subplots(1,2,figsize=(7.3,2.8))
    k=np.arange(1,21);R=1/(k*(k+1));phi=1/k
    axes[0].plot(k,phi,'-o',ms=4,color='#0072B2',label=r'merit tail $1/k$')
    axes[0].plot(k,R,'--s',ms=4,color='#D55E00',label=r'decrease $1/[k(k+1)]$')
    axes[0].set(xlabel='iteration k',ylabel='value');axes[0].legend(fontsize=9)
    k=np.arange(1,501);x=np.sin(np.log(k+1))
    axes[1].plot(k,x,ls='-',color='#D55E00',label=r'$x_1^k=\sin(\log(k+1))$')
    axes[1].axhline(0,color='black',lw=1);axes[1].set(xlabel='$k$',ylabel=r'$x_1$ ($x_2=0$)');axes[1].legend(fontsize=9,loc='upper right')
    fig.tight_layout();return fig
