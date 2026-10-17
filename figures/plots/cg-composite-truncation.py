"""Lecture 22 prepared analytic diagram. Single shared public figure source.
Distinct styles/markers/direct labels retain meaning in greyscale.
These are specified analytic toy inputs, not independent notebook result solves.
"""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,ax=plt.subplots(figsize=(7.1,3.1))
    a=np.linspace(0,2*np.pi,301)
    ax.plot(np.cos(a),np.sin(a),'k-',lw=1.5,label='trust radius 1')
    ax.plot(.8*np.cos(a),.8*np.sin(a),'k:',lw=1.5,label='normal radius .8')
    ax.axvline(-2,color='black',ls='--',label='full linearized equality: d1 = -2')
    ax.plot([0,-.8],[0,0],'-o',color='#0072B2',ms=5,label=r'normal $\mathbf{n}=(-.8,0)$')
    ax.plot([-.8,-.8],[0,.5],'--s',color='#D55E00',ms=5,label=r'tangent $\mathbf{t}=(0,.5)$')
    ax.plot([0,-.8],[0,.5],':',color='0.3',label=r'total step $\mathbf{d}$')
    ax.set(xlabel='$d_1$',ylabel='$d_2$',xlim=(-2.2,1.15),ylim=(-1.1,1.1),aspect='equal');ax.legend(fontsize=9,loc='upper left',bbox_to_anchor=(1.01,1))
    fig.tight_layout();return fig
