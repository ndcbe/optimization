"""Prepared Lecture 21 definition/proof illustration; analytic toy inputs.
Shared public figure pipeline; no independent recomputation of notebook results.
Line styles, markers, direct labels and hatches retain meaning in greyscale.
"""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,ax=plt.subplots(figsize=(7.2,2.5));ax.set_axis_off()
    for x,w,title,body,col,hatch in [(0,.28,'Tangent coordinates',r'$\mathbf{q}^T\mathbf{H}_R\mathbf{q}$','#0072B2','//'),(.38,.62,'Constraint / multiplier pairs',r'$2r_1\widetilde v_1+\cdots+2r_m\widetilde v_m$','#D55E00','..')]:
        ax.add_patch(plt.Rectangle((x,.26),w,.56,transform=ax.transAxes,facecolor='white',edgecolor=col,hatch=hatch,lw=1.8))
        ax.text(x+w/2,.69,title,ha='center',fontsize=11,transform=ax.transAxes,bbox=dict(facecolor="white",edgecolor="none",pad=2));ax.text(x+w/2,.47,body,ha='center',fontsize=15,transform=ax.transAxes,bbox=dict(facecolor="white",edgecolor="none",pad=2))
    ax.text(.33,.51,'+',ha='center',fontsize=23,transform=ax.transAxes)
    ax.text(.5,.08,r'Invertible coordinates eliminate coupling: $\mathbf{v}=\widetilde{\mathbf{v}}-\mathbf{G}^T\mathbf{q}-\frac{1}{2}\mathbf{H}_N\mathbf{r}$',ha='center',fontsize=12,transform=ax.transAxes)
    fig.tight_layout();return fig
