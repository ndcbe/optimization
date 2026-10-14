"""Bounded sublevel set of x^2 versus escaping sublevel ray of exp(x).
The horizontal level 1 and hatch mark the set on the x axis. The exp curve
never reaches 0; the left-arrow explicitly continues the sublevel ray.
"""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig, axes=plt.subplots(1,2,figsize=(10,2.5),layout='constrained')
    x=np.linspace(-2.5,1.5,500)
    for ax, y, title, interval in zip(axes,[x*x,np.exp(x)],['$f(x)=x^2$','$f(x)=e^x$'],[(-1,1),(-2.5,0)]):
        ax.plot(x,y,color='#0072B2',linestyle='-',linewidth=2)
        ax.axhline(1,color='#D55E00',linestyle='--',linewidth=1.6)
        ax.axvspan(*interval,facecolor='#56B4E9',alpha=.12,hatch='///',edgecolor='0.6',linewidth=0)
        ax.set(xlim=(-2.5,1.5),ylim=(0,4),xlabel='$x$',title=title)
        ax.set_ylabel('$f(x)$',fontsize=12)
        ax.tick_params(labelsize=9)
        ax.text(-2.3,1.2,'Level 1',fontsize=10)
    axes[0].plot([-1,1],[0,0],color='black',linewidth=4,marker='o',markersize=4)
    axes[0].text(-.7,.4,'$S=[-1,1]$',fontsize=11)
    axes[1].annotate('',xy=(-2.5,0.06),xytext=(0,0.06),arrowprops={'arrowstyle':'->','lw':3})
    axes[1].text(-2.2,.4,r'$S=(-\infty,0]$',fontsize=11)
    return fig
