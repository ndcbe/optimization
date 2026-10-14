"""Analytic barrier definitions and proof mechanisms; solver figures are notebook-owned."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

def interior():
 fig,ax=plt.subplots(figsize=(7.6,2.9))
 ax.axhspan(0,1.25,color='#009E73',alpha=.10,hatch='///')
 x=np.linspace(0,1,100);ax.plot(x,1-x,color='black',label=r'equality $x_1+x_2=1$')
 ax.scatter([0,1],[1,0],facecolors='white',edgecolors='black',s=60,zorder=3)
 ax.scatter(.2,.7,color='#D55E00',marker='s',s=60,label='positive-coordinate current point')
 ax.axvline(0,color='black',lw=1);ax.axhline(0,color='black',lw=1)
 ax.annotate('(.2, .7)',(.2,.7),xytext=(5,-18),textcoords='offset points',fontsize=11)
 ax.set(xlabel='$x_1$',ylabel='$x_2$',xlim=(-.08,1.25),ylim=(-.08,1.25))
 ax.legend(loc='upper right',fontsize=10);fig.tight_layout();return fig

def chain(labels):
 fig,ax=plt.subplots(figsize=(7.6,2.1));ax.axis('off')
 for i,label in enumerate(labels):
  pos=.015+.25*i;ax.add_patch(Rectangle((pos,.22),.215,.57,fc='#E9F2F7',ec='black',lw=1))
  ax.text(pos+.1075,.505,label,ha='center',va='center',fontsize=11)
  if i<3:ax.annotate('',(pos+.247,.505),(pos+.22,.505),arrowprops={'arrowstyle':'->','lw':1.5})
 fig.tight_layout();return fig

def local_proof():return chain(['product row\nfixes active dx\nand inactive du','active-tangent\nSOSC forces\ndx = 0','LICQ forces\nremaining\ndual steps = 0','invertible Jacobian\ngives local\npath by IFT'])
def elimination():return chain(['linearize all\nthree residual\nblocks','solve product\nrow for\nbound-dual step','substitute and\ncancel current\nbound dual','solve smaller\nsymmetric system;\nrecover dual step'])

def residual_shift():
 fig,ax=plt.subplots(figsize=(7.6,2.9));z=np.linspace(0,12,200)
 ax.plot(z,z,color='#0072B2',ls='-',label=r'original product residual $E_0/\mu$')
 ax.plot(z,abs(z-1),color='#D55E00',ls='--',label=r'inner residual $E_\mu/\mu$')
 ax.axhline(10,color='black',ls=':',label=r'tolerance / $\mu=10$')
 ax.scatter([11,11],[11,10],marker='s',color=['#0072B2','#D55E00'],s=55)
 ax.axvline(11,color='.6',ls='-.',lw=1)
 ax.set(xlabel=r'positive product $xu/\mu$',ylabel='unscaled residual / barrier weight',xlim=(0,12),ylim=(0,12))
 ax.legend(loc='upper left',fontsize=10);fig.tight_layout();return fig

def complement_linearization():
 fig,ax=plt.subplots(figsize=(7.6,2.8));x=np.linspace(.08,1.2,200);mu=.1
 ax.plot(x,mu/x,color='#0072B2',label=r'product curve $xu=.1$')
 ax.plot(x,.4-.4*x,color='#D55E00',ls='--',label='product-row tangent')
 ax.scatter(.5,.2,color='black',marker='s',s=55)
 ax.annotate('current (.5, .2)',(.5,.2),xytext=(25,18),textcoords='offset points',arrowprops={'arrowstyle':'->'},fontsize=11)
 ax.axhline(0,color='black',lw=1)
 ax.set(xlabel='coordinate $x_i$',ylabel='bound dual $u_i$',xlim=(.05,1.2),ylim=(-.1,.7))
 ax.legend(loc='upper right',fontsize=10);fig.tight_layout();return fig
