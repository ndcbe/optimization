"""exp(x) and its first/second Taylor models at 0. Models are approximations;
the handout separately states the exact intermediate-point identities.
Line identities are redundant in color, linestyle, and direct labels.
"""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,ax=plt.subplots(figsize=(9,2.5),layout='constrained')
    x=np.linspace(-1,1.1,400)
    ax.plot(x,np.exp(x),color='#0072B2',linestyle='-',linewidth=2,label='$e^x$')
    ax.plot(x,1+x,color='#D55E00',linestyle='--',linewidth=1.8,label='Tangent: $1+x$')
    ax.plot(x,1+x+x*x/2,color='#009E73',linestyle=':',linewidth=2.5,label='Quadratic: $1+x+x^2/2$')
    ax.plot(0,1,marker='o',color='black',markersize=5)
    ax.legend(loc='upper left',fontsize=10,frameon=False)
    ax.set(xlabel='$x$',ylabel='$f(x)$',xlim=(-1,1.1),ylim=(0,3.2))
    ax.tick_params(labelsize=10)
    return fig
