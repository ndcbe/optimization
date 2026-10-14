"""Lecture 22 prepared analytic diagram. Single shared public figure source.
Distinct styles/markers/direct labels retain meaning in greyscale.
These are specified analytic toy inputs, not independent notebook result solves.
"""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,axes=plt.subplots(1,2,figsize=(7.3,2.8))
    a=np.linspace(-.6,.6,241)
    axes[0].plot(a,np.abs(a),ls='-',color='#0072B2',label=r'$|\alpha|$')
    axes[0].plot(a,a,'--',color='#D55E00',label='forward slope +1')
    axes[0].plot(a,-a,':',color='0.3',label='backward slope -1')
    axes[0].set(xlabel='alpha',ylabel='zero-component norm');axes[0].legend(fontsize=9)
    a=np.linspace(0,.7,150)
    axes[1].plot(a,1-a,'--',color='#0072B2',label='exact linear residual')
    axes[1].plot(a,1-a+.3*a*a,'-',color='#D55E00',label='nonlinear residual')
    axes[1].set(xlabel='forward alpha',ylabel='residual norm');axes[1].legend(fontsize=9)
    fig.tight_layout();return fig
