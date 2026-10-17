"""The supplied affine quadratic: same primal Newton step, two multiplier forms."""
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    fig,axs=plt.subplots(1,2,figsize=(6.4,2.25),gridspec_kw={'width_ratios':[1,1.5]},layout='constrained')
    ax=axs[0];a=np.linspace(-.05,1.18,100);ax.plot(a,1-a,color='black',lw=1.4)
    start=np.array([1.,1.]);end=np.array([2/3,1/3])
    ax.plot(*start,'o',color='black',ms=5);ax.plot(*end,'s',color='#0072B2',ms=5)
    ax.annotate('',xy=end,xytext=start,arrowprops=dict(arrowstyle='->',color='#0072B2',lw=2))
    ax.annotate(r'$\mathbf{x}^k$',xy=start,xytext=(.72,1.15),fontsize=12,arrowprops=dict(arrowstyle='-',color='black',lw=.7))
    ax.annotate(r'$\mathbf{x}^k+\mathbf{d}_x$',xy=end,xytext=(.02,.12),fontsize=12,arrowprops=dict(arrowstyle='-',color='black',lw=.7))
    ax.annotate(r'$h=0$',xy=(.2,.8),xytext=(.02,.55),fontsize=12,arrowprops=dict(arrowstyle='-',color='black',lw=.7));ax.set(xlim=(-.08,1.25),ylim=(-.08,1.27),xlabel='$x_1$',ylabel='$x_2$');ax.set_aspect('equal')
    ax.axhline(0,color='black',lw=.7);ax.axvline(0,color='black',lw=.7)
    ax=axs[1];ax.set_axis_off();ax.text(.03,.88,'Same primal step',fontsize=12,transform=ax.transAxes)
    ax.text(.03,.65,r'$\mathbf{K}(\mathbf{d}_x,\mathbf{d}_v)=-\mathbf{F}$',fontsize=12,transform=ax.transAxes)
    ax.text(.03,.40,r'$\mathbf{K}(\mathbf{d}_x,\bar{\mathbf{v}})=-(\nabla f,\mathbf{h})$',fontsize=12,transform=ax.transAxes)
    ax.text(.03,.12,r'$\bar v=v^k+d_v$',fontsize=12,transform=ax.transAxes)
    return fig
