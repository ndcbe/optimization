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
    ax.plot(x,4-2*x,color='0.35',linestyle=':',linewidth=1.5,label=r'$\ell_1=0$')
    ax.plot(x,(4-x)/2,color='0.35',linestyle='-.',linewidth=1.5,label=r'$\ell_2=0$')
    root=(np.sqrt(13)-1)/2
    ax.plot(1,1,marker='s',color='black',markersize=6)
    ax.plot(4/3,4/3,marker='o',color='black',markersize=6)
    ax.plot(root,root,marker='*',color='#009E73',markeredgecolor='black',markersize=12)
    ax.annotate('Current iterate',xy=(1,1),xytext=(1.05,.84),fontsize=11, bbox=dict(facecolor='white',edgecolor='none',pad=1.5))
    ax.annotate('Newton iterate',xy=(4/3,4/3),xytext=(1.65,1.54),fontsize=11,ha='right', bbox=dict(facecolor='white',edgecolor='none',pad=1.5),
                arrowprops={'arrowstyle':'->','color':'black'})
    ax.annotate('True root',xy=(root,root),xytext=(.85,1.18),fontsize=11, bbox=dict(facecolor='white',edgecolor='none',pad=1.5),
                arrowprops={'arrowstyle':'->','color':'black'})
    ax.set(xlim=(.75,1.7),ylim=(.75,1.7),xlabel='$x_1$',ylabel='$x_2$',aspect='equal')
    ax.tick_params(labelsize=11)
    ax.legend(fontsize=10,loc='lower center',bbox_to_anchor=(.5,1.01),ncol=4,handlelength=2,columnspacing=1)
    return fig
