"""Prepared Lecture 21 definition/proof illustration; analytic toy inputs.
Shared public figure pipeline; no independent recomputation of notebook results.
Line styles, markers, direct labels and hatches retain meaning in greyscale.
"""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,ax=plt.subplots(figsize=(6.3,2.9));e=np.logspace(-10,-5,140)
    # Analytic identity for the ideal J=[[1,1],[1,1+eps]]; stable singular value from det/product.
    tr=4+2*e+e*e;disc=np.sqrt(tr*tr-4*e*e);smax=np.sqrt((tr+disc)/2);smin=e/smax
    mag=smin*smin/(1+np.sqrt(1+smin*smin))
    ax.loglog(e,mag,color='#0072B2',ls='-',label=r'$|\lambda_-|=\sigma_{\min}^2/(1+\sqrt{1+\sigma_{\min}^2})$')
    ax.axhline(np.finfo(float).eps,color='#D55E00',ls='--',label='double precision unit-scale spacing')
    ax.set(xlabel=r'row difference $\varepsilon$',ylabel=r'$|\lambda_-|$')
    ax.legend(fontsize=10,loc='upper left');fig.tight_layout();return fig
