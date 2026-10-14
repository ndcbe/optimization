"""Four functions at zero with vanishing first and second derivatives.
Actual function plots, fixed domain, individual axis scales stated by ticks.
All candidate points are black circles; no answer is encoded only by hue.
"""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,axes=plt.subplots(2,2,figsize=(9,4),layout='constrained')
    x=np.linspace(-1,1,400)
    for ax,y,title in zip(axes.flat,[x**4,-x**4,x**3,np.zeros_like(x)],['$x^4$','$-x^4$','$x^3$','$0$']):
        ax.plot(x,y,color='#0072B2',linestyle='-',linewidth=2)
        ax.plot(0,0,marker='o',color='black',markersize=5)
        ax.axhline(0,color='0.6',linewidth=.6)
        ax.axvline(0,color='0.6',linestyle=':',linewidth=.6)
        ax.set(xlim=(-1,1),ylim=(-1.1,1.1),title=title,xlabel='$x$')
        ax.set_ylabel('$f(x)$',fontsize=11)
        ax.tick_params(labelsize=9)
    return fig
