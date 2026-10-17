"""Analytic SQP concept diagrams. Actual solver figures remain notebook-owned."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Circle

def frame(ax,x,y):
 ax.set(xlabel=x,ylabel=y);ax.axhline(0,color='black',lw=.8);ax.axvline(0,color='black',lw=.8)

def flat_face():
 fig,ax=plt.subplots(figsize=(7.6,3.0))
 x=np.linspace(0,1,100);y=np.linspace(-.8,.8,101);X,Y=np.meshgrid(x,y)
 ax.contour(X,Y,Y**2,levels=[.04,.16,.36],colors='.65')
 ax.plot(x,0*x,color='#0072B2',lw=5,label=r'QP objective $d_2^2=0$')
 ax.scatter([0,1],[0,0],color='black',marker='s',s=45)
 ax.annotate('current KKT point',(0,0),xytext=(.08,.73),arrowprops={'arrowstyle':'->'},fontsize=11)
 ax.annotate('selected QP endpoint',(1,0),xytext=(.50,-.73),arrowprops={'arrowstyle':'->'},fontsize=11)
 ax.set(xlabel=r'$d_1$',ylabel=r'$d_2$',xlim=(-.06,1.06),ylim=(-.85,.85))
 ax.legend(loc='upper center',bbox_to_anchor=(.5,1.22),fontsize=11);fig.tight_layout();return fig

def active_identification():
 fig,axes=plt.subplots(1,2,figsize=(7.6,3.1))
 for ax,center,title in zip(axes,[-1,0],['strictly weighted bound','weakly weighted bound']):
  x=np.linspace(-1.4,1.6,201);ax.plot(x,(x-center)**2,color='#0072B2')
  ax.axvspan(0,1.6,color='#009E73',alpha=.12,hatch='///');ax.axvline(0,color='black',ls='--')
  for perturb,marker in [(-.25,'s'),(.25,'^')]:
   minimum=max(0,center+perturb);ax.scatter(minimum,(minimum-center)**2,marker=marker,s=60,color='#D55E00')
  ax.axhline(0,color='black',lw=.8)
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
 r=np.linspace(-2,2,101);axes[0].plot(r,abs(r),color='#0072B2');axes[0].set(xlabel='affine residual',ylabel='elastic cost / weight',ylim=(-.1,2.5));axes[0].axhline(0,color='black',lw=.8);axes[0].axvline(0,color='black',lw=.8)
 for val,txt in [(-1,r'$t_j>0$'),(1,r'$s_j>0$')]:axes[0].scatter(val,abs(val),marker='s',color='black');axes[0].annotate(txt,(val,abs(val)),xytext=(.5*val,1.85),ha='center',arrowprops={'arrowstyle':'-'},fontsize=11)
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
def convergence():return chain(['Armijo +\nstep bound','finite sum\nof decreases','steps/residuals\nvanish','QP limits\nsatisfy KKT'])

def coordinates():
 fig,axes=plt.subplots(1,2,figsize=(7.6,3.2))
 ax=axes[0];ax.add_patch(Circle((0,0),.6,fill=False,ec='black',ls='--'))
 q=np.linspace(-.25,.25,100);dx=-.3-2*q;dz=q
 ax.plot(dx,dz,color='#0072B2',label='bounded coordinate candidates')
 ax.scatter(-.7,.2,marker='s',color='#D55E00',s=60);ax.annotate('$q=.2$',(-.7,.2),xytext=(-.83,.43),arrowprops={'arrowstyle':'-'},fontsize=11)
 ax.set(xlabel='$d_y$',ylabel='$d_z$',xlim=(-.9,.7),ylim=(-.65,.65));ax.set_aspect('equal');ax.legend(loc='lower left',bbox_to_anchor=(-.1,-.47),fontsize=10)
 axes[1].plot(q,np.sqrt(.09+1.2*q+5*q*q),color='#0072B2',label='total step norm')
 axes[1].axhline(.6,color='black',ls='--',label='radius .6');axes[1].scatter(.2,np.sqrt(.53),color='#D55E00',marker='s')
 axes[1].set(xlabel='independent coordinate $q$',ylabel='Euclidean length');axes[1].legend(fontsize=10)
 fig.tight_layout();return fig

def rates():
 fig,axes=plt.subplots(1,2,figsize=(7.6,3.0));e=[];a=.5
 for j in range(5):e.extend([a,a/2]);a=a*a
 one=np.array(e[1:])/e[:-1];two=np.array(e[2:])/e[:-2]
 axes[0].semilogy(range(len(e)),e,'o-',color='#0072B2');axes[0].set(xlabel='index $k$',ylabel='constructed error $e_k$')
 axes[1].plot(range(len(one)),one,'s--',color='#D55E00',label='one-step ratio');axes[1].plot(range(len(two)),two,'o-',color='#0072B2',label='two-step ratio')
 axes[1].set(xlabel='starting index $k$',ylabel='error ratio',ylim=(-.03,1.08))
 fig.tight_layout();handles,labels=axes[1].get_legend_handles_labels();fig.legend(handles,labels,loc='upper center',bbox_to_anchor=(.5,.08),ncol=2,fontsize=10);return fig


def iqp_geometry():
 fig,axes=plt.subplots(1,2,figsize=(7.6,2.3),gridspec_kw={'width_ratios':[1.25,1]})
 ax=axes[0];x=np.linspace(-.8,.8,150)
 ax.plot(x,1-x*x,color='#0072B2',label=r'$h=x_1^2+x_2-1=0$')
 ax.axhline(1,color='black',ls='--',label=r'affine row at $(0,1)$')
 ax.scatter([0,.65],[1,1],s=45,marker='s',color='#D55E00')
 ax.annotate('QP trial',(.65,1),xytext=(.08,1.30),arrowprops={'arrowstyle':'-'},fontsize=11)
 ax.set(xlabel='$x_1$',ylabel='$x_2$',xlim=(-.85,.85),ylim=(.25,1.5))
 ax.axvline(0,color='black',lw=.8)
 ax=axes[1];ax.add_patch(Rectangle((0,0),1,1,fc='#009E73',alpha=.12,hatch='///',ec='black'))
 ax.plot([0,1],[0,0],color='#0072B2',lw=4,label='candidate bound face')
 ax.scatter([.25,.8],[.35,0],color='black',marker='s',s=40)
 ax.annotate('',(.8,0),(.25,.35),arrowprops={'arrowstyle':'->','lw':1.8})
 ax.set(xlabel='$d_1$',ylabel='$d_2$',xlim=(-.2,1.2),ylim=(-.2,1.2));ax.set_aspect('equal')
 fig.tight_layout()
 axes[0].legend(loc='upper center',bbox_to_anchor=(.5,-.48),fontsize=10)
 axes[1].legend(loc='upper center',bbox_to_anchor=(.5,-.48),fontsize=10)
 return fig

def working_set_flow():
 fig,ax=plt.subplots(figsize=(7.6,2.05));ax.axis('off')
 rows=[('IQP','inequality QP','read active set'),('EQP','estimate working set','equality QP'),('SLQP','penalty LP estimate','EQP refinement')]
 for y,(name,left,right) in zip([.83,.5,.17],rows):
  ax.text(.015,y,name,weight='bold',ha='left',va='center',fontsize=12)
  for x,txt in [(.17,left),(.62,right)]:ax.text(x+.18,y,txt,ha='center',va='center',fontsize=11,bbox={'boxstyle':'round,pad=.35','fc':'#E9F2F7','ec':'black'})
  ax.annotate('',(.61,y),(.535,y),arrowprops={'arrowstyle':'->','lw':1.4})
 fig.tight_layout();return fig

def update_checks():
 fig,ax=plt.subplots(figsize=(7.6,1.9));ax.axis('off')
 for x,txt in [(.12,'accepted primal\ntrial in D'),(.47,'specified\ndual update'),(.83,'actual new-point\nKKT residuals')]:
  ax.text(x,.62,txt,ha='center',va='center',fontsize=12,bbox={'boxstyle':'round,pad=.4','fc':'#E9F2F7','ec':'black'})
 for a,b in [(.26,.33),(.61,.68)]:ax.annotate('',(b,.62),(a,.62),arrowprops={'arrowstyle':'->','lw':1.5})
 ax.text(.5,.15,'feasibility  •  stationarity  •  dual signs  •  complementarity',ha='center',fontsize=11)
 fig.tight_layout();return fig

def trust_box():
 fig,axes=plt.subplots(1,2,figsize=(7.6,2.3))
 for ax in axes:
  ax.add_patch(Rectangle((-1,-1),2,2,fill=False,ec='black',lw=1.5))
  x=np.linspace(-1,3,100);ax.plot(x,2.04-x,color='#0072B2',lw=3,label=r'$d_1+d_2=2.04$')
  ax.scatter([1],[1],s=45,marker='s',color='black',label='box corner')
  ax.scatter([1.02],[1.02],s=50,marker='o',facecolor='white',edgecolor='#D55E00',linewidth=2,label='minimum infinity norm')
  ax.set(xlabel='$d_1$',ylabel='$d_2$');ax.set_aspect('equal')
 axes[0].set(xlim=(-1.2,1.5),ylim=(-1.2,1.5),title='trust box: radius 1')
 axes[1].set(xlim=(.96,1.08),ylim=(.96,1.08),title='corner detail',xticks=[1,1.08],yticks=[.96,1,1.04,1.08])
 fig.tight_layout()
 handles,labels=axes[1].get_legend_handles_labels();fig.legend(handles,labels,loc='upper center',bbox_to_anchor=(.5,.12),ncol=3,fontsize=10)
 return fig
