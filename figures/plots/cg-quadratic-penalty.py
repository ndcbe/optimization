"""Lecture 22 prepared analytic diagram. Single shared public figure source.
Distinct styles/markers/direct labels retain meaning in greyscale.
These are specified analytic toy inputs, not independent notebook result solves.
"""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,axes=plt.subplots(1,2,figsize=(7.3,2.9))
    c=np.linspace(.7,1.7,301)
    for rho,ls,col in [(.5,'-','#0072B2'),(2,'--','#D55E00'),(10,':','#009E73')]:
        axes[0].plot(c,-2*c+.5*rho*(2*c*c-2)**2,ls=ls,color=col,label=rf'$\rho_{{\rm pen}}={rho:g}$')
    axes[0].axvline(1,color='0.4',lw=1);axes[0].set(xlabel='radial coordinate c',ylabel='quadratic penalty Q',ylim=(-2.4,1.4));axes[0].legend(fontsize=9)
    a=np.linspace(0,2*np.pi,301)
    axes[1].plot(np.cos(a),np.sin(a),ls='-',color='#0072B2',label='tangent curvature 1')
    axes[1].plot(np.cos(a)/4,np.sin(a),color='#D55E00',ls='--',label='normal curvature 16')
    axes[1].set(xlabel='normal coordinate',ylabel='tangent coordinate',aspect='equal');axes[1].legend(fontsize=9,loc='upper left')
    fig.tight_layout();return fig
