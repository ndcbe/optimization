"""The original nonsmooth objective and its smooth complementarity lift."""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,axes=plt.subplots(1,2,figsize=(8.2,3.1),layout='constrained')
    x=np.linspace(-10,10,401);ax=axes[0]
    ax.plot(x,abs(x)+.5*x,color='#0072B2',ls='-',lw=2.5)
    ax.set(xlabel='$x$',ylabel=r'$|x|+\frac{1}{2} x$',xlim=(-11,11),ylim=(-1,16))
    ax.axvline(0,color='black',lw=.7);ax.axhline(0,color='black',lw=.7)
    ax=axes[1]
    ax.plot([0,2.4],[0,0],color='#0072B2',ls='-',lw=3,label='allowed sign parts')
    ax.plot([0,0],[0,2.4],color='#0072B2',ls='-',lw=3)
    ax.plot([0,2],[2,0],ls='--',color='#D55E00',lw=1.5)
    ax.scatter([0,2],[2,0],color='black',s=30,zorder=4)
    ax.scatter([1],[1],marker='x',color='#D55E00',s=65,zorder=4)
    ax.text(1.08,1.2,'midpoint',fontsize=10)
    ax.set(xlabel='$S_1$',ylabel='$S_2$',xlim=(-.15,2.6),ylim=(-.15,2.6),aspect='equal')
    ax.set_title(r'$S_1S_2=0,\quad S_1,S_2\geq0$',fontsize=11)
    for ax in axes:
        ax.tick_params(colors='black',labelsize=10)
        for spine in ax.spines.values():spine.set_color('black')
    return fig
