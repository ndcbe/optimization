"""Illustrative rate sequences, not solver output: e(k+1)=.5e(k) and e(k+1)=e(k)^2.
Both start at .25; semilog axis shows a fixed digit gain versus doubling digits.
"""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,ax=plt.subplots(figsize=(8,2.7),layout='constrained')
    k=np.arange(6);linear=.25*.5**k;quad=.25**(2**k)
    ax.semilogy(k,linear,color='#0072B2',linestyle='-',marker='o',markersize=5,label='Linear: factor 0.5')
    ax.semilogy(k,quad,color='#D55E00',linestyle='--',marker='s',markersize=5,label='Quadratic: square the error')
    ax.set(xlabel='Iteration $k$',ylabel='Error $e_k$',xticks=k,ylim=(1e-20,1))
    ax.tick_params(labelsize=11)
    ax.grid(True, which='major', color='0.85', linewidth=0.6)
    ax.set_axisbelow(True)
    ax.legend(fontsize=11,loc='lower left')
    return fig
