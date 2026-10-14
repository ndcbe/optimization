"""exp(x) and its first/second Taylor models at 0. Models are approximations;
the handout separately states the exact intermediate-point identities.
Line identities are redundant in color, linestyle, and direct labels.
"""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,ax=plt.subplots(figsize=(9,2.5),layout='constrained')
    x=np.linspace(-1,1.1,400)
    ax.plot(x,np.exp(x),color='#0072B2',linestyle='-',linewidth=2)
    ax.plot(x,1+x,color='#D55E00',linestyle='--',linewidth=1.8)
    ax.plot(x,1+x+x*x/2,color='#009E73',linestyle=':',linewidth=2.5)
    ax.plot(0,1,marker='o',color='black',markersize=5)
    ax.text(.82,2.96,'$e^x$',fontsize=11)
    ax.text(.80,2.46,'Quadratic',fontsize=11)
    ax.text(.81,1.70,'Tangent',fontsize=11)
    ax.set(xlabel='$x$',ylabel='$f(x)$',xlim=(-1,1.1),ylim=(0,3.2))
    ax.tick_params(labelsize=10)
    return fig
