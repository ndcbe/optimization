"""Prepared globalization teaching geometry; numerical checks are in make_figure."""
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import brentq

def make_figure():

    k=np.arange(9);long=(-1.)**k*(1+2.**(-k));short=1+2.**(-k)
    assert np.allclose(short[1:]-short[:-1],-2.**(-k[:-1]-1))
    assert np.all(np.diff(long**2)<0) and np.all(np.diff(short**2)<0)
    fig,axs=plt.subplots(1,2,figsize=(7.8,3.4),layout='constrained')
    axs[0].plot(k,long,color='#0072B2',linestyle='-',marker='o',ms=5)
    axs[0].axhline(1,color='0.5',linestyle='--');axs[0].axhline(-1,color='0.5',linestyle='--')
    axs[1].plot(k,short,color='#D55E00',linestyle='-',marker='s',ms=5)
    axs[1].axhline(1,color='0.5',linestyle='--')
    for ax in axs:
        ax.axhline(0,color='black',linewidth=.8);ax.set(xlim=(-.25,8.25),ylim=(-2,2.55),xlabel='iteration $k$',ylabel='$x^k$')
        ax.set_xticks([0,2,4,6,8])
    axs[0].set_title('Long steps: two limit points',fontsize=12)
    axs[1].set_title('Short steps: summable movement',fontsize=12)
    axs[0].text(.3,2.2,r'$x^k=(-1)^k(1+2^{-k})$',fontsize=11)
    axs[1].text(.3,2.2,r'$x^k=1+2^{-k}$',fontsize=11)
    return fig
