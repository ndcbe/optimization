"""Corrected Biegler p.28 example: strict at zero, nearby minima accumulate.
Analytic objective and derivative; each displayed minimum is found by bracketing
in u=1/x around an odd multiple of pi. Two explicit magnifications, not a schematic.
Direct labels, dotted envelopes, and black-edged circle minima survive greyscale.
"""
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import brentq

def make_figure():
    fig, axes = plt.subplots(1, 2, figsize=(10, 2.8), layout='constrained')
    for ax, upper in zip(axes, [0.12, 0.028]):
        x=np.linspace(0.0002, upper, 20000)
        y=x**4*(2+np.cos(1/x))
        ax.plot(x,y,color='#0072B2',linestyle='-',linewidth=1.6)
        ax.plot(x,x**4,color='#D55E00',linestyle=':',linewidth=1.3)
        ax.plot(x,3*x**4,color='#D55E00',linestyle=':',linewidth=1.3)
        roots=[]
        for k in range(1,150):
            u=brentq(lambda u: np.sin(u)+4/u*(2+np.cos(u)),
                     (2*k+1)*np.pi, (2*k+1.5)*np.pi)
            z=1/u
            assert abs(np.sin(u)+4/u*(2+np.cos(u)))<1e-9
            if upper*0.23<z<upper*0.96: roots.append(z)
        roots=np.array(roots)
        ax.plot(roots,roots**4*(2+np.cos(1/roots)),linestyle='none',marker='o',
                markersize=4,markerfacecolor='#D55E00',markeredgecolor='black')
        ax.plot(0,0,marker='*',color='black',markersize=9)
        ax.set(xlim=(-upper*.05,upper),ylim=(-upper**4*.12,upper**4*3.3),xlabel='$x$')
        ax.set_ylabel('$f(x)$',fontsize=12)
        ax.set_title('Near zero' if upper>.1 else 'Magnified again',fontsize=12)
        ax.tick_params(labelsize=9)
        ax.ticklabel_format(axis='y',style='sci',scilimits=(0,0))
        ax.yaxis.get_offset_text().set_fontsize(9)
        ax.annotate('$x^4$',xy=(upper*.87,(upper*.87)**4),fontsize=10,
                    xytext=(upper*.70,upper**4*.15))
        ax.text(.05,.88,'Dots: local minima',transform=ax.transAxes,fontsize=10)
    return fig
