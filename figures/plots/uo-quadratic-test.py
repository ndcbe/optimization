"""Exact contours of (x1-1)^2+4(x2+2)^2. Axes use equal units.
The semi-axis ratio is 2, while the Hessian eigenvalue ratio is 4.
"""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,ax=plt.subplots(figsize=(7.5,2.7),layout='constrained')
    x1=np.linspace(-2.5,4.5,400); x2=np.linspace(-3.8,-.2,300)
    X,Y=np.meshgrid(x1,x2)
    levels=[.5,2,4,8]
    cs=ax.contour(X,Y,(X-1)**2+4*(Y+2)**2,levels=levels,colors=['#0072B2'],linewidths=1.4)
    ax.clabel(cs,fontsize=9,inline=True)
    ax.plot(1,-2,marker='*',color='#D55E00',markeredgecolor='black',markersize=12)
    ax.text(1.15,-1.87,r'$\mathbf{x}^*$',fontsize=11)
    ax.set(xlabel='$x_1$',ylabel='$x_2$',aspect='equal',xlim=(-2.5,4.5),ylim=(-3.8,-.2))
    ax.tick_params(labelsize=10)
    return fig
