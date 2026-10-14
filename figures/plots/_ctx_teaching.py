"""Prepared coda diagrams. Computed scaling/tradespace figures remain notebook-owned."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle

BLUE='#0072B2'

def box(ax,left,bottom,width,height,text,fontsize=11,dashed=False):
    ax.add_patch(Rectangle((left,bottom),width,height,facecolor='white',edgecolor='black',
                           linestyle='--' if dashed else '-',linewidth=1.1))
    ax.text(left+width/2,bottom+height/2,text,ha='center',va='center',fontsize=fontsize)

def arrow(ax,start,end):
    ax.annotate('',xy=end,xytext=start,arrowprops={'arrowstyle':'->','color':'black','linewidth':1.3})

def quality_loop():
    fig,ax=plt.subplots(figsize=(7.6,2.6));ax.axis('off');ax.set(xlim=(0,1),ylim=(0,1))
    for i,text in enumerate(['Represent\nmodel / data','Compute\nfeasible result','Choose\nwith preferences','Implement\nand observe']):
        left=.01+i*.25;box(ax,left,.38,.23,.35,text)
        if i<3:arrow(ax,(left+.23,.55),(left+.25,.55))
    ax.text(.13,.89,'Model checks',ha='center',fontsize=12)
    ax.text(.38,.89,'Solve checks',ha='center',fontsize=12)
    ax.text(.76,.89,'Decision checks',ha='center',fontsize=12)
    ax.plot([.88,.88,.13,.13],[.37,.19,.19,.37],color='black',linestyle='--')
    arrow(ax,(.13,.22),(.13,.38));ax.text(.5,.02,'Use observed performance to revisit the representation.',ha='center',fontsize=11)
    fig.tight_layout();return fig

def evidence_map():
    fig,ax=plt.subplots(figsize=(7.6,2.9));ax.axis('off');ax.set(xlim=(0,1),ylim=(0,1))
    pairs=[('Scale differences','Inspect units and numerical scales'),('Kink / domain issue','Inspect expressions and derivatives'),
           ('Dependent active rows','Inspect rank and physical meaning'),('Missing physical limits','Inspect domain and objective behavior'),
           ('Nonconvex structure','Inspect local versus global evidence')]
    for i,(left,right) in enumerate(pairs):
        y=.91-i*.18;ax.text(.01,y,left,fontsize=11,va='center');arrow(ax,(.34,y),(.43,y));ax.text(.46,y,right,fontsize=11,va='center')
    ax.text(.5,.01,'A feature suggests a test; it does not establish the cause.',ha='center',fontsize=11)
    fig.tight_layout();return fig

def conditioning_bound():
    fig,ax=plt.subplots(figsize=(7.6,2.6));ax.axis('off');ax.set(xlim=(0,1),ylim=(0,1))
    box(ax,.02,.48,.28,.30,'relative RHS change\n'+r'$10^{-16}$')
    box(ax,.37,.48,.25,.30,r'$\kappa(A)=10^{10}$'+'\nworst-case factor')
    box(ax,.70,.48,.28,.30,'relative solution error\n'+r'bound $10^{-6}$')
    arrow(ax,(.30,.63),(.37,.63));arrow(ax,(.62,.63),(.70,.63))
    ax.text(.5,.26,'Same induced norm; fixed nonsingular matrix; RHS perturbation.',ha='center',fontsize=11)
    ax.text(.5,.09,'The realized error can be smaller than the upper bound.',ha='center',fontsize=11)
    fig.tight_layout();return fig

def smooth_epigraph():
    fig,(ax,tx)=plt.subplots(1,2,figsize=(7.6,2.8),gridspec_kw={'width_ratios':[1,1.2]})
    x=np.linspace(-1.2,1.2,401)
    ax.fill_between(x,np.abs(x),1.7,facecolor='#E9F2F7',hatch='...',edgecolor='0.7')
    ax.plot(x,x,color='black',linestyle='-',label=r'$t=x$')
    ax.plot(x,-x,color=BLUE,linestyle='--',label=r'$t=-x$')
    ax.set(xlabel='x',ylabel='t',xlim=(-1.2,1.2),ylim=(-.3,1.7));ax.legend(loc='upper center',fontsize=10,frameon=True,facecolor='white',framealpha=1)
    tx.axis('off');tx.text(.03,.81,r'$t\geq x,\quad t\geq-x$',fontsize=14)
    tx.text(.03,.54,'Hatched region: both affine rows hold.',fontsize=11)
    tx.text(.03,.29,r'At fixed $x$: smallest $t$ is $|x|$.',fontsize=11)
    tx.text(.03,.08,'This is an epigraph, not a general equality.',fontsize=11)
    fig.tight_layout(w_pad=2);return fig

def dependent_rows():
    fig,(ax,tx)=plt.subplots(1,2,figsize=(7.6,2.8),gridspec_kw={'width_ratios':[1,1.25]})
    x=np.linspace(0,2,201);ax.plot(x,x-1,color='black',linestyle='-',label='row 1: x - 1')
    ax.plot(x,2*x-2,color=BLUE,linestyle='--',label='row 2: 2x - 2')
    ax.axhline(0,color='0.5',linewidth=.8);ax.plot(1,0,color='black',marker='o',linestyle='none',ms=7)
    ax.set(xlabel='x',ylabel='equality residual',xlim=(0,2),ylim=(-2.2,2.2));ax.legend(fontsize=10)
    tx.axis('off');tx.text(.02,.83,'Both vanish at x = 1.',fontsize=12)
    tx.text(.02,.57,'Active gradients: 1 and 2.',fontsize=12)
    tx.text(.02,.33,'One independent row direction.',fontsize=12)
    tx.text(.02,.08,'A sensitivity statement needs\na specified perturbation.',fontsize=11)
    fig.tight_layout(w_pad=2);return fig

def bounds_domains():
    fig,axes=plt.subplots(1,2,figsize=(7.6,2.8));x=np.linspace(-2,2,201)
    axes[0].plot(x,x*x,color='black',linestyle='-');axes[0].plot(0,0,color=BLUE,marker='o',linestyle='none')
    axes[0].set(xlabel='x',ylabel='objective value');axes[0].set_title(r'$\min_{x\in\mathbb{R}}x^2$',fontsize=14,pad=14)
    axes[1].plot(x,-x,color='black',linestyle='-');axes[1].annotate('',xy=(1.9,-1.9),xytext=(1.1,-1.1),arrowprops={'arrowstyle':'->','color':BLUE,'linewidth':2})
    axes[1].set(xlabel='x',ylabel='objective value');axes[1].set_title(r'$\min_{x\in\mathbb{R}}(-x)$',fontsize=14,pad=14)
    fig.tight_layout();return fig

def diagnostics_flow():
    fig,ax=plt.subplots(figsize=(7.6,3.0));ax.axis('off');ax.set(xlim=(0,1),ylim=(0,1))
    boxes=[(.02,.62,'Save model / data / log'),(.37,.62,'Check domains\nand units'),(.72,.62,'Inspect structural\nissues'),
           (.72,.17,'Initialize; inspect\nresiduals / derivatives'),(.37,.17,'Choose a justified\nchange'),(.02,.17,'Recheck original\nmodel')]
    for x,y,t in boxes:box(ax,x,y,.26,.25,t,fontsize=10)
    for start,end in [((.28,.745),(.37,.745)),((.63,.745),(.72,.745)),((.85,.62),(.85,.42)),((.72,.295),(.63,.295)),((.37,.295),(.28,.295))]:arrow(ax,start,end)
    ax.text(.5,.02,'Example workflow: use the evidence to adapt the order.',ha='center',fontsize=11)
    fig.tight_layout();return fig

def certificate_scope():
    fig,(ax,tx)=plt.subplots(1,2,figsize=(7.6,2.6),gridspec_kw={'width_ratios':[1.1,1]})
    ax.plot([9.8,10],[.5,.5],color=BLUE,linestyle='-',linewidth=3)
    ax.plot(9.8,.5,marker='s',color=BLUE,linestyle='none',ms=8);ax.plot(10,.5,marker='o',color='black',linestyle='none',ms=8)
    ax.text(9.8,.66,'global L = 9.8',ha='center',fontsize=11);ax.text(10,.27,'feasible U = 10',ha='center',fontsize=11)
    ax.set(xlabel='objective value',yticks=[],xlim=(9.65,10.15),ylim=(0,1))
    tx.axis('off');tx.text(.02,.81,'Interval width: 0.2',fontsize=12)
    tx.text(.02,.52,'A local first-order residual\nanswers a different question.',fontsize=11)
    tx.text(.02,.13,'Global bounds must cover\nthe full feasible domain.',fontsize=11)
    fig.tight_layout(w_pad=2);return fig

def model_boundary():
    fig,ax=plt.subplots(figsize=(7.6,2.9));ax.axis('off');ax.set(xlim=(0,1),ylim=(0,1))
    box(ax,.27,.20,.46,.62,'Represented farmer model\n\nthree crops / acreage\nthree yield scenarios\nexpected profit + recourse',fontsize=11)
    labels=[(.01,.82,'crop insurance'),(.01,.26,'land sale'),(.77,.82,'debt-risk requirement'),(.77,.26,'a fourth crop')]
    for x,y,t in labels:ax.text(x,y,t,fontsize=11,va='center')
    ax.text(.5,.04,'Outside the boundary: assess separately or extend the model.',ha='center',fontsize=11)
    fig.tight_layout();return fig

def recommendation_handoff():
    fig,ax=plt.subplots(figsize=(7.6,2.8));ax.axis('off');ax.set(xlim=(0,1),ylim=(0,1))
    box(ax,.02,.43,.28,.40,'Objective owner\nand stated values')
    box(ax,.36,.43,.28,.40,'Model assumptions\nuncertainty / evidence')
    box(ax,.70,.43,.28,.40,'Recommendation\nand implementation')
    arrow(ax,(.30,.63),(.36,.63));arrow(ax,(.64,.63),(.70,.63))
    ax.text(.5,.25,'Keep a reproducible quantitative result and its limitations.',ha='center',fontsize=11)
    ax.text(.5,.07,'Specify who will act, what will be checked and when to revisit.',ha='center',fontsize=11)
    fig.tight_layout();return fig
