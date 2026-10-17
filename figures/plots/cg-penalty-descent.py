"""Analytic merit changes for the printed full/reduced-curvature counterexample."""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,ax=plt.subplots(figsize=(7.2,1.8));a=np.linspace(0,.2,201)
    for rho,style,color in [(101,'-','#0072B2'),(301,'--','#D55E00')]:
        ax.plot(a,(300-rho)*a-100*a*a,ls=style,color=color,label=rf'$\rho_{{\rm pen}}={rho}$')
    ax.axhline(0,color='black',lw=.8);ax.axvline(0,color='black',lw=.8)
    ax.set(xlabel=r'step length $\alpha$',ylabel=r'merit change $\Delta\phi$')
    ax.legend(fontsize=10,loc='upper left',bbox_to_anchor=(.02,1.0),frameon=False,ncol=2);fig.tight_layout();return fig
