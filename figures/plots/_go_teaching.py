"""Analytic global-optimization proof mechanisms; actual solver plots remain notebook-owned."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


def regional_relaxation():
    """A containing interval and a globally smaller convex objective give a lower value."""
    fig, ax = plt.subplots(figsize=(7.6, 3.0))
    x=np.linspace(-.5,1.5,401)
    ax.plot(x,(x-.6)**2+.2,color='black',linestyle='-',label=r'$f(x)=(x-.6)^2+.2$')
    ax.plot(x,.5*(x-.6)**2,color='#0072B2',linestyle='--',label=r'$q(x)=.5(x-.6)^2$')
    ax.plot([-.5,1.5],[-.65,-.65],color='#0072B2',marker='s',linestyle='-',linewidth=2)
    ax.plot([0,1],[-.35,-.35],color='black',marker='o',linestyle='-',linewidth=2)
    ax.text(.5,-.36,'original S',ha='center',va='top',fontsize=11)
    ax.text(.5,-.66,'relaxed R',ha='center',va='top',fontsize=11)
    ax.scatter([.6,.6],[0,.2],color=['#0072B2','black'],marker='s',s=55,zorder=4)
    ax.set(xlabel='coordinate x',ylabel='objective value',xlim=(-.6,1.6),ylim=(-.9,1.5))
    ax.legend(loc='upper center',fontsize=11)
    fig.tight_layout();return fig


def fathom_bound():
    """Compare certified regional lower values with a feasible incumbent."""
    fig,ax=plt.subplots(figsize=(7.6,2.7))
    ax.axhline(10,color='black',linestyle='--',label='feasible incumbent U = 10')
    ax.plot([.3,.8],[8,8],color='#0072B2',linestyle='-',marker='s',label='regional lower value')
    ax.plot([1.3,1.8],[12,12],color='#0072B2',linestyle='-',marker='s')
    for x,lower in [(.55,8),(1.55,12)]:
        ax.annotate('',(x,13.4),(x,lower+.15),arrowprops={'arrowstyle':'->','color':'#0072B2'})
        ax.text(x,13.7,'possible regional costs',fontsize=10,ha='center',va='bottom')
    ax.set(xticks=[.55,1.55],xticklabels=['region A','region B'],ylabel='objective value',xlim=(-.1,2.2),ylim=(7,14.5))
    ax.legend(loc='lower right',fontsize=10)
    fig.tight_layout();return fig


def cover_ledger():
    """Keep lower certificates even after every region is tolerance-closed."""
    fig,ax=plt.subplots(figsize=(7.6,2.4));ax.axis('off')
    ax.text(.5,.97,r'Root domain $[0,3]$; feasible $U=10$; tolerance $.3$',ha='center',va='top',fontsize=12)
    for i,(lb,hatch) in enumerate([(9.7,'///'),(10.2,'...'),(11,'xxx')]):
        left=.04+.31*i
        ax.add_patch(Rectangle((left,.40),.30,.26,facecolor='#E9F2F7',edgecolor='black',hatch=hatch))
        ax.text(left+.15,.53,rf'$[{i},{i+1}]$',ha='center',va='center',fontsize=12,bbox={'facecolor':'white','edgecolor':'none','pad':2})
        ax.text(left+.15,.25,rf'retained $\ell_{i+1}={lb}$',ha='center',fontsize=12)
    ax.text(.5,.04,'No active boxes remain; every part of the root still has a lower certificate.',ha='center',fontsize=11)
    fig.tight_layout();return fig


def status_flow():
    """Separate bound closure, tolerance closure, splitting and certificate accounting."""
    fig,ax=plt.subplots(figsize=(7.6,3.8));ax.axis('off');ax.set(xlim=(0,1),ylim=(0,1.10))
    boxes=[(.02,.80,.42,.16,'Select region; compute lower / status'),
           (.02,.56,.42,.16,'Certified infeasible or lower >= U?'),
           (.02,.32,.42,.16,'Check feasible candidate; update U.\nRegional gap <= tolerance?'),
           (.02,.08,.42,.16,'Split domain; children cover parent\nand inherit lower certificate'),
           (.63,.58,.34,.16,'Close by certified bound\nor infeasibility'),
           (.63,.32,.34,.16,'Close by tolerance;\nretain lower certificate'),
           (.63,.05,.34,.16,'Compute full L and gap;\nstop or select next region')]
    for left,bottom,width,height,label in boxes:
        ax.add_patch(Rectangle((left,bottom),width,height,facecolor='#E9F2F7',edgecolor='black'))
        ax.text(left+width/2,bottom+height/2,label,ha='center',va='center',fontsize=10)
    def arrow(end,start,label='',pos=None):
        ax.annotate('',end,start,arrowprops={'arrowstyle':'->','linewidth':1.3})
        if label:ax.text(*pos,label,fontsize=10,ha='center',va='center',bbox={'facecolor':'white','edgecolor':'none','pad':1})
    arrow((.23,.73),(.23,.80))
    arrow((.23,.49),(.23,.56),'no',(.26,.525))
    arrow((.23,.25),(.23,.32),'no',(.26,.285))
    arrow((.63,.66),(.44,.64),'yes',(.53,.67))
    arrow((.63,.40),(.44,.40),'yes',(.53,.425))
    arrow((.63,.13),(.44,.16))
    arrow((.80,.22),(.80,.32))
    ax.plot([.97,.99,.99],[.66,.66,.13],color='black',linestyle='-',linewidth=1.3)
    arrow((.97,.13),(.99,.13))
    ax.text(.5,1.07,'A solver limit / failure leaves its region unresolved.',ha='center',va='top',fontsize=10)
    fig.tight_layout();return fig


def mccormick_signs():
    """Four nonnegative distances yield the four valid product inequalities."""
    fig,(ax,txt)=plt.subplots(1,2,figsize=(7.6,2.8),gridspec_kw={'width_ratios':[1,1.3]})
    ax.add_patch(Rectangle((0,0),1,1,facecolor='#E9F2F7',edgecolor='black',hatch='...'))
    ax.plot([.4,.4],[0,1],color='#0072B2',linestyle='--')
    ax.plot([0,1],[.6,.6],color='#D55E00',linestyle=':')
    ax.scatter([.4],[.6],color='black',marker='o',s=45,zorder=4)
    ax.set(xticks=[0,.4,1],xticklabels=[r'$x^L$',r'$x$',r'$x^U$'],yticks=[0,.6,1],yticklabels=[r'$y^L$',r'$y$',r'$y^U$'],xlim=(-.05,1.05),ylim=(-.05,1.05));ax.set_aspect(1)
    txt.axis('off')
    rows=[r'$(x-x^L)(y-y^L)\geq0$',r'$(x^U-x)(y^U-y)\geq0$',r'$(x^U-x)(y-y^L)\geq0$',r'$(x-x^L)(y^U-y)\geq0$']
    for i,row in enumerate(rows):txt.text(.02,.86-.22*i,row,fontsize=14,va='center')
    fig.tight_layout(w_pad=2);return fig


def hull_weights():
    """The four graph corners generate the single-product hull under normalization."""
    fig=plt.figure(figsize=(7.6,3.0));ax=fig.add_subplot(121,projection='3d');txt=fig.add_subplot(122);txt.axis('off')
    vertices=np.array([[0,0,0],[1,0,0],[0,1,0],[1,1,1]])
    for i in range(4):
        for j in range(i+1,4):
            pair=vertices[[i,j]];ax.plot(pair[:,0],pair[:,1],pair[:,2],color='#0072B2',linestyle='--',linewidth=1.4)
    ax.scatter(vertices[:,0],vertices[:,1],vertices[:,2],color='black',marker='s',s=30)
    ax.scatter([.4],[.6],[.2],color='#D55E00',marker='o',s=45)
    ax.set(xlabel='a',ylabel='b',zlabel='q',xticks=[0,1],yticks=[0,1],zticks=[0,1]);ax.tick_params(labelsize=10);ax.view_init(elev=19,azim=-62)
    txt.text(.02,.86,r'$\max(0,a+b-1)\leq q\leq\min(a,b)$',fontsize=12)
    txt.text(.02,.61,r'Weights: $(1-a-b+q,\ a-q,\ b-q,\ q)$',fontsize=11)
    txt.text(.02,.36,'Corners: (0,0,0), (1,0,0),\n(0,1,0), (1,1,1)',fontsize=11)
    txt.text(.02,.09,'The marked point is (.4, .6, .2).',fontsize=11)
    fig.tight_layout();return fig


def alphabb_curvature():
    """On [-1,1], the alpha=1 shift of f=-x^2 is constant and convex."""
    fig,(ax,tx)=plt.subplots(1,2,figsize=(7.6,2.9),gridspec_kw={'width_ratios':[1,1]})
    x=np.linspace(-1,1,401)
    ax.plot(x,-x*x,color='black',linestyle='-',label=r'$f(x)=-x^2$')
    ax.plot(x,np.full_like(x,-1),color='#0072B2',linestyle='--',label=r'$\phi(x)=f(x)-(1-x)(x+1)$')
    ax.set(xlabel='coordinate x',ylabel='function value',xlim=(-1,1),ylim=(-1.18,.12))
    ax.text(.45,-.05,r'$f=-x^2$',fontsize=12)
    ax.text(.25,-.92,r'$\phi=-1$',color='#0072B2',fontsize=12)
    tx.axis('off');tx.text(.02,.81,r'$\phi(x)=f(x)-\alpha(b-x)(x-a)$',fontsize=12)
    tx.text(.02,.57,r'$\phi^{\prime\prime}=f^{\prime\prime}+2\alpha$',fontsize=14)
    tx.text(.02,.32,'Here a = -1, b = 1, alpha = 1:\n'+r'$\phi=-1,\quad\phi^{\prime\prime}=0$',fontsize=12)
    tx.text(.02,.06,'Curvature must be valid throughout the box.',fontsize=10)
    fig.tight_layout(w_pad=2);return fig


def safe_tightening():
    """The equality x+y=3 inside [0,4]^2 projects onto [0,3] on each axis."""
    fig,(ax,txt)=plt.subplots(1,2,figsize=(7.6,2.9));txt.axis('off')
    ax.add_patch(Rectangle((0,0),4,4,fill=False,edgecolor='black',linestyle='--'))
    ax.add_patch(Rectangle((0,0),3,3,facecolor='#E9F2F7',edgecolor='#0072B2',hatch='///'))
    ax.plot([0,3],[3,0],color='black',linestyle='-')
    ax.scatter([1],[2],marker='o',color='#D55E00',s=55)
    ax.set(xlabel='x',ylabel='y',xticks=[0,1,3,4],yticks=[0,2,3,4],xlim=(-.2,4.2),ylim=(-.2,4.2));ax.set_aspect(1)
    txt.text(.02,.86,'Dashed box: original bounds [0,4]²',fontsize=11)
    txt.text(.02,.63,'Solid line: original row x + y = 3',fontsize=11)
    txt.text(.02,.40,'Hatched box: bounds [0,3]²',fontsize=11)
    txt.text(.02,.17,'Marked feasible point: (1,2)',fontsize=11)
    fig.tight_layout(w_pad=2);return fig
