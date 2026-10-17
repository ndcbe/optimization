"""Convex chord geometry and a strictly convex zero-curvature example."""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,axes=plt.subplots(1,2,figsize=(8.4,3.0),layout='constrained')
    x=np.linspace(-1.25,1.25,400)
    for ax,power,title in zip(axes,[2,4],[r'$f(x)=x^2$',r'$g(x)=x^4$']):
        ax.plot(x,x**power,color='#0072B2',ls='-',lw=2.4,label='function')
        ax.plot([-1,1],[1,1],color='#D55E00',ls='--',lw=2,label='endpoint chord')
        ax.scatter([-1,1],[1,1],color='black',s=22,zorder=4)
        ax.set(xlabel='$x$',ylabel='value',title=title,xlim=(-1.3,1.3),ylim=(-.15,2))
        ax.axvline(0,color='black',lw=.7);ax.axhline(0,color='black',lw=.7)
        ax.tick_params(colors='black',labelsize=10)
        for spine in ax.spines.values():spine.set_color('black')
    axes[0].legend(fontsize=9,loc='upper center')
    axes[1].annotate(r'$g^{\prime\prime}(0)=0$',xy=(0,0),xytext=(.15,.50),fontsize=11,
                     arrowprops={'arrowstyle':'->','color':'black'})
    return fig
