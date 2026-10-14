"""Armijo proof picture: illustrative quadratic profile with known initial slope."""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    a=np.linspace(0,1.8,250);phi=-a+.5*a*a
    fig,ax=plt.subplots(figsize=(6.0,2.9),layout='constrained')
    ax.plot(a,phi,color='black',linestyle='-',linewidth=2,label=r'$\phi(\alpha)-\phi(0)=-\alpha+\frac{1}{2}\alpha^2$')
    ax.plot(a,-.25*a,color='#0072B2',linestyle='--',linewidth=1.5,label=r'Armijo line: $\eta=1/4$')
    ax.plot(a,-a,color='#D55E00',linestyle=':',linewidth=1.5,label=r'initial linear model: $\phi^{\prime}(0)=-1$')
    ax.plot(0,0,'ko',ms=4);ax.axhline(0,color='0.6',linewidth=.7)
    ax.set(xlim=(-.03,1.8),ylim=(-1.4,.2),xlabel=r'step length $\alpha$',ylabel='objective change')
    ax.legend(loc='lower left',fontsize=10,frameon=False)
    return fig
