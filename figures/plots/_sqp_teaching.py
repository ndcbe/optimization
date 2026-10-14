"""Analytic SQP concept diagrams. Actual solver figures remain notebook-owned."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle

def frame(ax,x,y):
 ax.set(xlabel=x,ylabel=y);ax.axhline(0,color='.6',lw=.7);ax.axvline(0,color='.6',lw=.7)

def flat_face():
 fig,ax=plt.subplots(figsize=(7.6,3.0))
 x=np.linspace(0,1,100);y=np.linspace(-.8,.8,101);X,Y=np.meshgrid(x,y)
 ax.contour(X,Y,Y**2,levels=[.04,.16,.36,.64],colors='.65')
 ax.plot(x,0*x,color='#0072B2',lw=5,label=r'QP objective $d_2^2=0$')
 ax.scatter([0,1],[0,0],color='black',marker='s',s=45)
 ax.annotate('current KKT point',(0,0),xytext=(.08,.5),arrowprops={'arrowstyle':'->'},fontsize=11)
 ax.annotate('selected QP endpoint',(1,0),xytext=(.55,-.5),arrowprops={'arrowstyle':'->'},fontsize=11)
 ax.set(xlabel=r'$d_1$',ylabel=r'$d_2$',xlim=(-.06,1.06),ylim=(-.85,.85))
 ax.legend(loc='upper center',fontsize=11);fig.tight_layout();return fig

def active_identification():
 fig,axes=plt.subplots(1,2,figsize=(7.6,3.1))
 for ax,center,title in zip(axes,[-1,0],['strictly weighted bound','weakly weighted bound']):
  x=np.linspace(-1.4,1.6,201);ax.plot(x,(x-center)**2,color='#0072B2')
  ax.axvspan(0,1.6,color='#009E73',alpha=.12,hatch='///');ax.axvline(0,color='black',ls='--')
  for perturb,marker in [(-.25,'s'),(.25,'^')]:
   minimum=max(0,center+perturb);ax.scatter(minimum,(minimum-center)**2,marker=marker,s=60,color='#D55E00')
  ax.set(xlabel='$x$',ylabel='objective model',title=title,xlim=(-1.4,1.6),ylim=(-.1,7))
 fig.tight_layout();return fig

def inconsistent():
 fig,axes=plt.subplots(1,2,figsize=(7.6,3.0))
 x=np.linspace(-2.7,2.7,300);axes[0].plot(x,x*x-4,color='#0072B2',label=r'$x^2-4$')
 axes[0].axhline(0,color='black',lw=1);axes[0].axvline(1,color='black',ls=':')
 axes[0].axvspan(-2.7,-2,color='#009E73',alpha=.2,hatch='///');axes[0].scatter(-2,0,marker='s',color='black')
 axes[0].set(xlabel='$x$',ylabel='nonlinear inequality',ylim=(-4.5,4))
 axes[0].legend(fontsize=10)
 axes[1].plot([-1.5,0],[.5,.5],lw=6,color='#0072B2',label=r'bound $d\leq0$')
 axes[1].plot([1.5,3],[1,1],lw=6,color='#D55E00',ls='--',label=r'affine row $d\geq1.5$')
 axes[1].set(xlabel='$d$',yticks=[],xlim=(-1.5,3),ylim=(0,1.5));axes[1].legend(loc='lower right',fontsize=10)
 fig.tight_layout();return fig

def elastic_cap():
 fig,axes=plt.subplots(1,2,figsize=(7.6,3.0))
 r=np.linspace(-2,2,101);axes[0].plot(r,abs(r),color='#0072B2');axes[0].set(xlabel='affine residual',ylabel='elastic cost / weight')
 for val,txt in [(-1,'negative residual'),(1,'positive residual')]:axes[0].scatter(val,abs(val),marker='s',color='black');axes[0].annotate(txt,(val,abs(val)),xytext=(4,10),textcoords='offset points',fontsize=9)
 axes[1].axhspan(-1,1,color='#009E73',alpha=.15,hatch='///')
 axes[1].plot([-1,1],[1,1],color='black',ls='--');axes[1].plot([-1,1],[-1,-1],color='black',ls=':')
 axes[1].scatter([-.65,0,.65],[-1,0,1],marker='s',color='#D55E00')
 axes[1].set(xlabel='example residual sign',ylabel=r'$\bar v/\rho_{\rm pen}$',xticks=[-.65,0,.65],xticklabels=['negative','zero','positive'],ylim=(-1.5,1.5),xlim=(-1,1))
 fig.tight_layout();return fig

def chain(labels):
 fig,ax=plt.subplots(figsize=(7.6,2.3));ax.axis('off')
 for i,txt in enumerate(labels):
  x=.015+i*.25;ax.add_patch(Rectangle((x,.24),.215,.56,fill=True,fc='#E9F2F7',ec='black',lw=1))
  ax.text(x+.1075,.52,txt,ha='center',va='center',fontsize=11)
  if i<3:ax.annotate('',(x+.25,.52),(x+.218,.52),arrowprops={'arrowstyle':'->','lw':1.5})
 fig.tight_layout();return fig

def descent():return chain(['actual affine\ncontraction','QP stationarity\n+ bound signs','dual-norm\nweight bound','negative\nmerit slope'])
def convergence():return chain(['uniform slope\n+ accepted alpha','sum of decreases\nis finite','steps + violation\ntend to zero','QP residuals\npass to KKT limit'])

def coordinates():
 fig,axes=plt.subplots(1,2,figsize=(7.6,3.2))
 ax=axes[0];ax.add_patch(Circle((0,0),.6,fill=False,ec='black',ls='--'))
 q=np.linspace(-.25,.25,100);dx=-.3-2*q;dz=q
 ax.plot(dx,dz,color='#0072B2',label='bounded coordinate candidates')
 ax.scatter(-.7,.2,marker='s',color='#D55E00',s=60);ax.annotate('$q=.2$',(-.7,.2),xytext=(5,10),textcoords='offset points',fontsize=11)
 ax.set(xlabel='$d_y$',ylabel='$d_z$',xlim=(-.9,.7),ylim=(-.65,.65));ax.set_aspect('equal');ax.legend(loc='lower left',fontsize=8)
 axes[1].plot(q,np.sqrt(.09+1.2*q+5*q*q),color='#0072B2',label='total step norm')
 axes[1].axhline(.6,color='black',ls='--',label='radius .6');axes[1].scatter(.2,np.sqrt(.53),color='#D55E00',marker='s')
 axes[1].set(xlabel='independent coordinate $q$',ylabel='Euclidean length');axes[1].legend(fontsize=9)
 fig.tight_layout();return fig

def rates():
 fig,axes=plt.subplots(1,2,figsize=(7.6,3.0));e=[];a=.5
 for j in range(5):e.extend([a,a/2]);a=a*a
 one=np.array(e[1:])/e[:-1];two=np.array(e[2:])/e[:-2]
 axes[0].semilogy(range(len(e)),e,'o-',color='#0072B2');axes[0].set(xlabel='index $k$',ylabel='constructed error $e_k$')
 axes[1].plot(range(len(one)),one,'s--',color='#D55E00',label='one-step ratio');axes[1].plot(range(len(two)),two,'o-',color='#0072B2',label='two-step ratio')
 axes[1].set(xlabel='starting index $k$',ylabel='error ratio',ylim=(-.03,.58));axes[1].legend(fontsize=9)
 fig.tight_layout();return fig
