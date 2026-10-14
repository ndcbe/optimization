"""Two nonlinear equations and their simultaneous linearization at (1,1).
The dotted lines intersect at the Newton iterate (4/3,4/3), not the true
positive symmetric root ((sqrt(13)-1)/2,(sqrt(13)-1)/2).
Colors are redundant with solid/dashed identities and shape markers.
"""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,ax=plt.subplots(figsize=(5.0,4.2),layout='constrained')
    x=np.linspace(.75,1.7,400)
    ax.plot(x,3-x*x,color='#0072B2',linestyle='-',linewidth=2,label='$F_1=0$')
    y=np.linspace(.75,1.7,400)
    ax.plot(3-y*y,y,color='#D55E00',linestyle='--',linewidth=2,label='$F_2=0$')
    ax.plot(x,4-2*x,color='0.5',linestyle=':',linewidth=1.5)
    ax.plot(x,(4-x)/2,color='0.5',linestyle=':',linewidth=1.5)
    root=(np.sqrt(13)-1)/2
    ax.plot(1,1,marker='s',color='black',markersize=6)
    ax.plot(4/3,4/3,marker='o',color='black',markersize=6)
    ax.plot(root,root,marker='*',color='#009E73',markeredgecolor='black',markersize=12)
    ax.annotate('Current iterate',xy=(1,1),xytext=(.8,.84),fontsize=12)
    ax.annotate('Newton iterate',xy=(4/3,4/3),xytext=(.80,1.58),fontsize=11,
                arrowprops={'arrowstyle':'->','color':'black'})
    ax.annotate('True root',xy=(root,root),xytext=(1.37,1.04),fontsize=11,
                arrowprops={'arrowstyle':'->','color':'black'})
    ax.set(xlim=(.75,1.7),ylim=(.75,1.7),xlabel='$x_1$',ylabel='$x_2$',aspect='equal')
    ax.tick_params(labelsize=11)
    ax.legend(fontsize=11,loc='upper right')
    return fig
