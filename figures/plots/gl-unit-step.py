"""A quadratic model gives half the initial linear-model decrease at a unit step."""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    a=np.linspace(0,1.7,250);phi=-a+.5*a*a
    fig,ax=plt.subplots(figsize=(6.,2.8),layout='constrained')
    ax.plot(a,phi,color='black',linestyle='-',linewidth=2,label=r'$\phi(\alpha)-\phi(0)$')
    ax.plot(a,-.25*a,color='#0072B2',linestyle='--',linewidth=1.6,label=r'$\eta=1/4$')
    ax.plot(a,-.6*a,color='#D55E00',linestyle=':',linewidth=1.6,label=r'$\eta=3/5$')
    ax.axvline(1,color='black',linestyle='--',linewidth=.8)
    ax.plot(1,-.5,'ko',ms=5)
    ax.annotate(r'$\phi(1)-\phi(0)=-1/2$',xy=(1,-.5),xytext=(.14,-.85),arrowprops=dict(arrowstyle='->'),fontsize=11)
    ax.set(xlim=(0,1.7),ylim=(-1.15,.1),xlabel=r'step length $\alpha$',ylabel='objective change')
    ax.legend(loc='upper right',fontsize=10,frameon=False)
    return fig
