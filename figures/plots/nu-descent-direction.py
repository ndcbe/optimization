"""A positive-definite quadratic model at the origin.
g=[2,1], H=diag(1,4), Newton p=[-2,-.25], and g^T p=-4.25.
The picture illustrates the sign proof; arrows have direct vector labels.
"""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,ax=plt.subplots(figsize=(7.5,3),layout='constrained')
    x=np.linspace(-3,2.5,250);y=np.linspace(-1.5,1.6,250);X,Y=np.meshgrid(x,y)
    cs=ax.contour(X,Y,2*X+Y+.5*X*X+2*Y*Y,levels=[-2,-1,0,2,4,7],colors='0.7',linewidths=.8)
    ax.clabel(cs,fontsize=9)
    for dest,color,label,offset in [((2,1),'#0072B2',r'$\mathbf{g}$',(2.1,1.1)),((-2,-.25),'#D55E00',r'$\mathbf{p}$',(-2.5,-.45))]:
        ax.annotate('',xy=dest,xytext=(0,0),arrowprops={'arrowstyle':'->','lw':2.5,'color':color})
        ax.text(*offset,label,fontsize=15)
    ax.plot(0,0,marker='o',color='black',markersize=5)
    ax.text(.1,-.3,'Current iterate',fontsize=11)
    ax.set(xlim=(-3,2.5),ylim=(-1.5,1.6),xlabel='$p_1$',ylabel='$p_2$',aspect='equal')
    ax.tick_params(labelsize=11)
    return fig
