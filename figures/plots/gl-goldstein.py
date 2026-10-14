"""Value-based acceptance geometry for a quadratic profile, eta=1/4."""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    a=np.linspace(0,1.8,250);phi=-a+.5*a*a
    fig,ax=plt.subplots(figsize=(6.,2.5),layout='constrained')
    ax.plot(a,phi,color='black',linestyle='-',linewidth=2,label=r'$\phi(\alpha)-\phi(0)$')
    ax.plot(a,-.25*a,color='#0072B2',linestyle='--',linewidth=1.5,label='Armijo upper line')
    ax.plot(a,-.75*a,color='#D55E00',linestyle=':',linewidth=1.5,label='Goldstein lower line')
    ax.fill_between(a,-.75*a,-.25*a,facecolor='#56B4E9',alpha=.09,hatch='//',edgecolor='0.8')
    ax.set(xlim=(0,1.8),ylim=(-1.35,.12),xlabel=r'step length $\alpha$',ylabel='objective change')
    ax.legend(loc='lower left',fontsize=10,frameon=False)
    return fig
