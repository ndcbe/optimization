"""Analytic barrier definitions and proof mechanisms; solver figures are notebook-owned."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

def interior():
 fig,ax=plt.subplots(figsize=(7.6,2.9))
 ax.add_patch(Rectangle((0,0),1.25,1.25,facecolor='#009E73',alpha=.10,hatch='///'))
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
 ax.plot([11,11],[10,11],color='.6',ls='-.',lw=1)
 ax.set(xlabel=r'positive product $xu/\mu$',ylabel=r'unscaled residual / $\mu$',xlim=(0,12),ylim=(0,12))
 ax.legend(loc='lower right',fontsize=10);fig.tight_layout();return fig

def complement_linearization():
 fig,ax=plt.subplots(figsize=(7.6,2.8));x=np.linspace(.08,1.2,200);mu=.1
 ax.plot(x,mu/x,color='#0072B2',label=r'product curve $xu=.1$')
 ax.plot(x,.4-.4*x,color='#D55E00',ls='--',label='product-row tangent')
 ax.scatter(.5,.2,color='black',marker='s',s=55)
 ax.annotate('current (.5, .2)',(.5,.2),xytext=(25,18),textcoords='offset points',arrowprops={'arrowstyle':'->'},fontsize=11)
 ax.axhline(0,color='black',lw=1)
 ax.set(xlabel='coordinate $x_i$',ylabel='bound dual $u_i$',xlim=(.05,1.2),ylim=(-.1,.7))
 ax.legend(loc='upper right',fontsize=10);fig.tight_layout();return fig


def regularization_defect():
 fig,ax=plt.subplots(figsize=(7.6,2.6))
 a=1.;delta=.1;dv=2.;exact=-1.;modified=-.8
 ax.axhline(0,color='black',lw=1)
 ax.axvline(0,color='black',lw=1)
 xs=np.linspace(-1.25,.1,100)
 ax.plot(xs,a+xs,color='#0072B2',label=r'original affine residual $h+Jd_x=1+d_x$')
 ax.plot([exact],[0],marker='o',mfc='white',mec='black',ms=8)
 ax.plot([modified],[delta*dv],marker='s',color='#D55E00',ms=7)
 ax.annotate(r'$\delta_A d_v$',(modified,.1),xytext=(-.35,.2),
             arrowprops={'arrowstyle':'->','color':'black'},fontsize=12)
 ax.plot([modified,modified],[0,.2],color='black',ls='--')
 ax.annotate('exact row',(-1,0),xytext=(-1.21,.32),fontsize=11,
             arrowprops={'arrowstyle':'->','color':'black'})
 ax.set(xlabel=r'primal step $d_x$',ylabel='original affine residual',xlim=(-1.25,.1),ylim=(-.28,1.2))
 ax.legend(loc='upper left',fontsize=10);fig.tight_layout();return fig

def teaching_loop():
 fig,ax=plt.subplots(figsize=(7.6,2.65));ax.axis('off');ax.set(xlim=(0,1),ylim=(0,1))
 boxes=[(.02,.59,.25,.32,'test original residual\nand primal/dual signs'),
        (.36,.59,.27,.32,'if inner test passes,\nupdate barrier weight'),
        (.72,.59,.26,.32,'solve Newton system;\nrecover bound-dual\nstep'),
        (.72,.08,.26,.32,'apply positivity cap;\nresidual-merit\nbacktracking'),
        (.36,.08,.27,.32,'accept and update\nall three variable blocks')]
 for x,y,w,h,t in boxes:
  ax.add_patch(Rectangle((x,y),w,h,fc='#E9F2F7',ec='black'));ax.text(x+w/2,y+h/2,t,ha='center',va='center',fontsize=11)
 for a,b in [((.27,.75),(.36,.75)),((.63,.75),(.72,.75)),((.85,.59),(.85,.4)),((.72,.24),(.63,.24))]:
  ax.annotate('',xy=b,xytext=a,arrowprops={'arrowstyle':'->','lw':1.3})
 ax.annotate('',xy=(.145,.59),xytext=(.36,.24),arrowprops={'arrowstyle':'->','connectionstyle':'angle,angleA=180,angleB=-90,rad=4','lw':1.3})
 ax.text(.02,.97,'original test passes: success',fontsize=10,ha='left')
 ax.text(.43,.44,'always take a direction\nif original test fails',fontsize=10,ha='center')
 ax.text(.85,.005,'retries exhausted: failure',fontsize=10,ha='center')
 fig.tight_layout();return fig

def splitter_flow_cone():
 fig,(ax,bx)=plt.subplots(1,2,figsize=(7.6,2.7),gridspec_kw={'width_ratios':[1,1.05]})
 ax.add_patch(Rectangle((0,0),1.4,1.4,fc='#E9F2F7',hatch='///',ec='none',alpha=.18))
 ax.axhline(0,color='black',lw=1);ax.axvline(0,color='black',lw=1)
 ax.annotate('',(1,1),(0,0),arrowprops={'arrowstyle':'->','color':'#D55E00','lw':2})
 ax.text(.13,1.19,r'$d_F=d_{f_1}+d_{f_2}$',fontsize=11,bbox={'fc':'white','ec':'none','pad':1})
 ax.annotate(r'$(d_{f_1},d_{f_2})=(1,1)$',(.8,.8),xytext=(.04,.43),fontsize=10,bbox={'fc':'white','ec':'none','pad':1},
             arrowprops={'arrowstyle':'->','color':'black'})
 ax.set(xlim=(-.12,1.4),ylim=(-.12,1.4),xlabel=r'outlet direction $d_{f_1}$',ylabel=r'outlet direction $d_{f_2}$',xticks=[0,1],yticks=[0,1])
 bx.axis('off')
 bx.text(.02,.93,'At zero flow, the active bound rows are',fontsize=11)
 bx.text(.08,.72,r'$\mathbf{r}_1=(-1,0,0)$',fontsize=12)
 bx.text(.08,.53,r'$\mathbf{r}_2=(0,-1,0)$',fontsize=12)
 bx.text(.08,.34,r'$\mathbf{r}_3=(0,0,-1)$',fontsize=12)
 bx.text(.02,.09,'The balance row is $(1,-1,-1)$.',fontsize=11)
 fig.tight_layout();return fig
