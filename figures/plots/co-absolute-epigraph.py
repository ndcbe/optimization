"""A feasible epigraph point can be lowered at fixed x until t=abs(x)."""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,ax=plt.subplots(figsize=(7.5,3.1),layout='constrained')
    x=np.linspace(-6,6,401)
    ax.fill_between(x,abs(x),8,color='#56B4E9',alpha=.18,hatch='///',edgecolor='0.65')
    ax.plot(x,abs(x),color='#0072B2',ls='-',lw=2.5)
    ax.scatter([3,3],[7,3],color='black',s=25,zorder=4)
    ax.annotate('',xy=(3,3.25),xytext=(3,6.75),arrowprops={'arrowstyle':'->','color':'#D55E00','lw':2})
    ax.text(3.3,5,'decrease $t$\nkeep $x$ fixed',fontsize=11)
    ax.text(-5.6,6.6,r'$t\geq x,\ t\geq-x$',fontsize=12)
    ax.set(xlabel='$x$',ylabel='$t$',xlim=(-6,6),ylim=(-.4,8))
    ax.axhline(0,color='black',lw=.7);ax.axvline(0,color='black',lw=.7)
    ax.tick_params(colors='black',labelsize=10)
    for spine in ax.spines.values():spine.set_color('black')
    return fig
