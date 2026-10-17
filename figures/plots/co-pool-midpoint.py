"""A chord between feasible pooling plans misses the fat-balance surface."""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,ax=plt.subplots(figsize=(7.8,3.4),layout='constrained')
    q=np.linspace(100,200,401);p=.033+.00017*(q-100)
    fat_in=3.3+.067*(q-100);fat_out=p*q
    ax.plot(q,fat_in,color='#0072B2',ls='--',lw=2.5,label='fat in along the chord')
    ax.plot(q,fat_out,color='#D55E00',ls='-',lw=2.5,label='fat out: $p(Q)Q$')
    ax.scatter([100,200],[3.3,10],marker='o',color='black',s=35,zorder=4)
    ax.plot([150,150],[6.225,6.65],color='black',lw=1.4)
    ax.annotate('midpoint imbalance = 0.425',xy=(150,6.44),xytext=(113,9.3),fontsize=11,
                arrowprops={'arrowstyle':'->','color':'black'})
    ax.text(101,2.9,'A: pure C',fontsize=11);ax.text(199,10.3,'B: pure D',ha='right',fontsize=11)
    ax.set(xlabel='total pooled amount $Q$',ylabel='fat amount',xlim=(96,204),ylim=(2.4,11))
    ax.legend(fontsize=10,loc='lower right');ax.tick_params(colors='black',labelsize=10)
    for spine in ax.spines.values():spine.set_color('black')
    return fig
