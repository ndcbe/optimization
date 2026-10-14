"""Lecture 22 prepared analytic diagram. Single shared public figure source.
Distinct styles/markers/direct labels retain meaning in greyscale.
These are specified analytic toy inputs, not independent notebook result solves.
"""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,axes=plt.subplots(1,2,figsize=(7.3,2.8))
    r=np.linspace(0,.5,150)
    axes[0].plot(r,r*r,'-',color='#0072B2',label=r'residual bound $Cr^2$')
    axes[0].plot(r,r,'--',color='#D55E00',label=r'distance $r$')
    axes[0].set(xlabel='distance r',ylabel='scale');axes[0].legend(fontsize=9)
    axes[1].plot(r,r*r,'-',color='#0072B2',label=r'positive tangent term $r^2$')
    axes[1].plot(r,-r**3,'--',color='#D55E00',label=r'possible remainder $-r^3$')
    axes[1].plot(r,r*r-r**3,':',color='black',label='positive total near zero')
    axes[1].axhline(0,lw=1,color='0.5');axes[1].set(xlabel='distance r',ylabel='merit change model');axes[1].legend(fontsize=9)
    fig.tight_layout();return fig
