"""Exact Newton step on (x1-1)^2+4(x2+2)^2, from (3,0) to (1,-2).
Contours and arrow use equal coordinate scales. Direction and endpoint are
independently checked from gradient [4,16] and Hessian diag(2,8).
"""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,ax=plt.subplots(figsize=(7.5,3.2),layout='constrained')
    x=np.linspace(-2,4.5,300);y=np.linspace(-4,1,300);X,Y=np.meshgrid(x,y)
    cs=ax.contour(X,Y,(X-1)**2+4*(Y+2)**2,levels=[1,4,10,20,30],colors=['#0072B2'],linestyles='solid',linewidths=1)
    ax.clabel(cs,fontsize=10)
    ax.plot(3,0,marker='s',color='black',markersize=6)
    ax.plot(1,-2,marker='*',color='#D55E00',markeredgecolor='black',markersize=13)
    ax.annotate('',xy=(1,-2),xytext=(3,0),arrowprops={'arrowstyle':'->','lw':2,'color':'#D55E00'})
    ax.text(3.12,.03,r'$\mathbf{x}^0$',fontsize=13)
    ax.text(1.1,-2.3,r'$\mathbf{x}^1$',fontsize=13)
    ax.text(1.7,-.7,r'$\mathbf{p}^0$',fontsize=13)
    ax.set(xlim=(-2,4.5),ylim=(-4,1),xlabel='$x_1$',ylabel='$x_2$',aspect='equal')
    ax.tick_params(labelsize=11)
    return fig
