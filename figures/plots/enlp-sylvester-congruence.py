"""Prepared Lecture 21 definition/proof illustration; analytic toy inputs.
Shared public figure pipeline; no independent recomputation of notebook results.
Line styles, markers, direct labels and hatches retain meaning in greyscale.
"""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,axes=plt.subplots(1,2,figsize=(7.1,2.9));a=np.linspace(-1.3,1.3,220);X,Y=np.meshgrid(a,a)
    S=np.array([[1,.7],[0,1.]])
    axes[0].contour(X,Y,X*X-Y*Y,levels=[-1,-.3,.3,1],colors=['#D55E00','#D55E00','#0072B2','#0072B2'],linestyles=['--','--','-','-'])
    U=X+.7*Y;V=Y
    axes[1].contour(X,Y,U*U-V*V,levels=[-1,-.3,.3,1],colors=['#D55E00','#D55E00','#0072B2','#0072B2'],linestyles=['--','--','-','-'])
    for ax,title in zip(axes,[r'$B=\mathrm{diag}(1,-1)$',r'Sheared form $S^TBS$']):
        ax.set_aspect('equal');ax.set_title(title,fontsize=12);ax.axhline(0,color='0.65',lw=.7);ax.axvline(0,color='0.65',lw=.7)
        ax.set(xlabel='first coordinate',ylabel='second coordinate');ax.set_xticks([-1,0,1]);ax.set_yticks([-1,0,1])
    fig.text(.5,.01,'Solid: positive levels. Dashed: negative levels. Coordinates change; sign dimensions persist.',ha='center',fontsize=10)
    fig.tight_layout(rect=(0,.04,1,1));return fig
