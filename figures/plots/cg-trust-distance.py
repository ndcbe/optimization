"""Lecture 22 prepared analytic diagram. Single shared public figure source.
Distinct styles/markers/direct labels retain meaning in greyscale.
These are specified analytic toy inputs, not independent notebook result solves.
"""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,axes=plt.subplots(1,2,figsize=(7.3,2.9))
    t=np.linspace(0,2*np.pi,301)
    for ax,radius in zip(axes,[.6,.8]):
        ax.plot(radius*np.cos(t),radius*np.sin(t),'k-',lw=1.5,label=f'radius {radius}')
        a=np.linspace(-1.1,.2,150);ax.plot(a,-1-a,'--',color='#0072B2',label='linearized equality')
        ax.plot([0,-.5],[0,-.5],'-o',color='#D55E00',ms=4,label='minimum normal')
        ax.scatter(-1,0,marker='s',color='black');ax.annotate('coordinate normal',(-1,0),xytext=(3,8),textcoords='offset points',fontsize=9)
        ax.set(xlabel='d1',ylabel='d2',xlim=(-1.15,1),ylim=(-1.15,1),aspect='equal');ax.legend(fontsize=8,loc='upper right')
    fig.tight_layout();return fig
