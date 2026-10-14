"""Positive curvature and a descent direction do not guarantee full-step decrease.
f=sqrt(1+x^2), x0=2, p=-10; x(alpha=1)=-8 versus x(alpha=.1)=1.
Exact objective and tangent-matching quadratic model are directly labelled and
solid/dashed, while endpoints use distinct markers.
"""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,ax=plt.subplots(figsize=(8.5,3),layout='constrained')
    x=np.linspace(-9,3,500);f=np.sqrt(1+x*x);p=x-2
    m=np.sqrt(5)+(2/np.sqrt(5))*p+.5/(5*np.sqrt(5))*p*p
    ax.plot(x,f,color='#0072B2',linestyle='-',linewidth=2,label='Objective')
    ax.plot(x,m,color='#D55E00',linestyle='--',linewidth=2,label='Quadratic model')
    for v,mark in [(2,'s'),(1,'o'),(-8,'*')]:ax.plot(v,np.sqrt(1+v*v),marker=mark,color='black',markersize=9)
    ax.annotate('Full step',xy=(-8,np.sqrt(65)),xytext=(-6.9,8.5),fontsize=12,
                arrowprops={'arrowstyle':'->'})
    ax.annotate('Short step',xy=(1,np.sqrt(2)),xytext=(-1.8,3.1),fontsize=12,
                arrowprops={'arrowstyle':'->'})
    ax.legend(loc='upper right',fontsize=11)
    ax.set(xlabel='$x$',ylabel='Function value',xlim=(-9,3),ylim=(-3,10))
    ax.tick_params(labelsize=11)
    return fig
