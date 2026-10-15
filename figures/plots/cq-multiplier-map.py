"""Prepared Lecture 20 geometry/proof sketch; analytic inputs, no solver results.
One source serves the handout and Constraint-Qualifications website reference.
Direct labels, line styles and hatches preserve meaning in greyscale.
"""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,axes=plt.subplots(1,2,figsize=(7.5,2.8))
    for ax,title,matrix,line in zip(axes,['Independent active rows','Dependent active rows'],[r'$J_{\mathcal{A}}^T=I_2$',r'$J_{\mathcal{A}}^T=\left[\begin{smallmatrix}1&1\\0&0\end{smallmatrix}\right]$'],['one input for each image','different inputs can share an image']):
        ax.set_axis_off();ax.set_title(title,fontsize=12)
        # Mathtext has no smallmatrix environment; draw the matrix entries as text.
        mat = '$I_2$' if title.startswith('Independent') else '[[1, 1], [0, 0]]'
        ax.text(.5,.77,r'$\mathbf{J}_{\mathcal{A}}^T=$ '+mat,ha='center',fontsize=13,transform=ax.transAxes)
        ax.text(.12,.42,r'$\boldsymbol{\lambda}$',ha='center',fontsize=17,transform=ax.transAxes)
        ax.annotate('',xy=(.65,.46),xytext=(.28,.46),xycoords='axes fraction',arrowprops=dict(arrowstyle='->',lw=2,color='#0072B2'))
        ax.text(.84,.42,r'$-\nabla f$',ha='center',fontsize=15,transform=ax.transAxes)
        ax.text(.5,.12,line,ha='center',fontsize=10,transform=ax.transAxes)
    fig.tight_layout();return fig
