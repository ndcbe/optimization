"""Prepared Lecture 21 definition/proof illustration; analytic toy inputs.
Shared public figure pipeline; no independent recomputation of notebook results.
Line styles, markers, direct labels and hatches retain meaning in greyscale.
"""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig=plt.figure(figsize=(6.4,3.3));ax=fig.add_subplot(111,projection='3d')
    s,t=np.meshgrid(np.linspace(-1,1,6),np.linspace(-1,1,6))
    ax.plot_wireframe(s,-s,t,color='#0072B2',rstride=1,cstride=1,linewidth=.65)
    ax.plot_wireframe(t,s,-s,color='#D55E00',rstride=1,cstride=1,linewidth=.65,linestyle='--')
    q=np.linspace(-1,1,80);ax.plot(-q,q,-q,color='black',lw=3)
    ax.text(-.9,.9,-.9,r'$\ker A$',fontsize=13)
    ax.text(.65,-.8,.95,r'$x_1+x_2=0$',fontsize=11)
    ax.text(.85,.9,-.7,r'$x_2+x_3=0$',fontsize=11)
    ax.set(xlabel='$x_1$',ylabel='$x_2$',zlabel='$x_3$');ax.view_init(23,35);ax.set_box_aspect([1,1,1]);fig.tight_layout();return fig
