"""Complete supplied Armijo trial values in backtracking order; no solver."""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,ax=plt.subplots(figsize=(7.2,1.9));x=np.arange(3);trial=np.array([5.02,4.85,4.93]);bound=np.array([4.8,4.9,4.95])
    ax.plot(x,trial,'o-',color='#0072B2',label=r'trial $\phi$');ax.plot(x,bound,'s--',color='#D55E00',label='Armijo bound')
    for pos,y in zip(x,trial):
        target=[(.2,5.03),(1.05,4.7),(2.04,4.78)][pos]
        ax.annotate(f'{y:g}',(pos,y),xytext=target,fontsize=10)
    for pos,y in zip(x,bound):
        target=[(.05,4.7),(1.05,5.0),(2.04,5.03)][pos]
        ax.annotate(f'{y:g}',(pos,y),xytext=target,fontsize=10)
    ax.set(xticks=x,xticklabels=['1','.5','.25'],xlabel=r'trial order $\rightarrow$  (step length $\alpha$)',ylabel='merit',xlim=(-.2,2.35),ylim=(4.65,5.15))
    fig.tight_layout()
    ax.legend(fontsize=10,loc='lower center',bbox_to_anchor=(.5,1.35),ncol=2,frameon=False)
    return fig
