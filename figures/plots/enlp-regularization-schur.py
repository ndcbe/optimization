"""Prepared Lecture 21 definition/proof illustration; analytic toy inputs.
Shared public figure pipeline; no independent recomputation of notebook results.
Line styles, markers, direct labels and hatches retain meaning in greyscale.
"""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,ax=plt.subplots(figsize=(7.2,2.5));ax.set_axis_off()
    ax.add_patch(plt.Rectangle((.01,.29),.57,.56,transform=ax.transAxes,facecolor='white',edgecolor='#0072B2',hatch='//',lw=1.8))
    ax.add_patch(plt.Rectangle((.68,.29),.3,.56,transform=ax.transAxes,facecolor='white',edgecolor='#D55E00',hatch='..',lw=1.8))
    ax.text(.295,.68,'Primal Schur complement',ha='center',fontsize=12,transform=ax.transAxes,bbox=dict(facecolor="white",edgecolor="none",pad=2))
    ax.text(.295,.47,r'$\widehat{\mathbf{W}}=\mathbf{W}+\delta_W\mathbf{I}+\delta_A^{-1}\mathbf{J}^T\mathbf{J}$',ha='center',fontsize=14,transform=ax.transAxes,bbox=dict(facecolor="white",edgecolor="none",pad=2))
    ax.text(.83,.68,'Dual block',ha='center',fontsize=12,transform=ax.transAxes,bbox=dict(facecolor="white",edgecolor="none",pad=2))
    ax.text(.83,.47,r'$-\delta_A\mathbf{I}$',ha='center',fontsize=17,transform=ax.transAxes,bbox=dict(facecolor="white",edgecolor="none",pad=2))
    ax.text(.63,.5,'+',ha='center',fontsize=23,transform=ax.transAxes)
    ax.text(.5,.09,r'$\delta_A>0$: invertible block elimination separates these quadratic forms.',ha='center',fontsize=12,transform=ax.transAxes,bbox=dict(facecolor="white",edgecolor="none",pad=2))
    fig.tight_layout();return fig
