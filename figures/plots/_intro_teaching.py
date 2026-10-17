"""Analytic introduction sketches; no notebook results are recomputed here."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle, Ellipse, FancyArrowPatch
BLUE = "#0072B2"
ORANGE = "#D55E00"


def axes(ax, xlabel, ylabel):
    ax.set(xlabel=xlabel, ylabel=ylabel)
    ax.tick_params(colors="black")
    for spine in ax.spines.values():
        spine.set_color("black")


def box(ax, xy, width, height, text, color=BLUE, linestyle="-"):
    ax.add_patch(Rectangle(xy, width, height, fill=False, edgecolor=color,
                           linewidth=2, linestyle=linestyle))
    ax.text(xy[0]+width/2, xy[1]+height/2, text, ha="center", va="center", fontsize=13)


def feasible_objective():
    fig, ax = plt.subplots(figsize=(7.8, 2.8), layout="constrained")
    x=np.linspace(0, 2, 160)
    ax.fill_between(x, 0, 2-x, color=BLUE, alpha=.12, hatch="//", edgecolor=BLUE)
    ax.plot(x, 2-x, color=BLUE, linestyle="-", label="$x_1+x_2=2$")
    for z in (.5,1.5,2.5):
        ax.plot(x, z-2*x, color="0.4", linestyle="--", lw=1.2)
    ax.annotate("Smaller $2x_1+x_2$", xy=(.35,.2), xytext=(1.05,1.65),
                arrowprops={"arrowstyle":"->","color":"black"}, fontsize=12)
    ax.text(.12,.9,"Feasible set",fontsize=12, bbox={"facecolor":"white","edgecolor":"none","alpha":.85,"pad":1.5})
    ax.set(xlim=(0,2.2),ylim=(0,2.2))
    axes(ax,"$x_1$","$x_2$")
    ax.legend(loc="upper right",fontsize=11)
    return fig


def tank_cost():
    fig,(a,b)=plt.subplots(1,2,figsize=(8,2.9),layout="constrained")
    a.add_patch(Ellipse((0,1.9),1.5,.35,fill=False,edgecolor=BLUE,lw=2))
    a.plot([-.75,-.75],[.2,1.9],color=BLUE,linestyle="-")
    a.plot([.75,.75],[.2,1.9],color=BLUE,linestyle="-")
    th=np.linspace(np.pi,2*np.pi,80)
    a.plot(.75*np.cos(th),.2+.175*np.sin(th),color=BLUE,linestyle="-")
    a.annotate("",xy=(-.75,2.35),xytext=(.75,2.35),arrowprops={"arrowstyle":"<->"})
    a.text(0,2.4,"Diameter $D$",ha="center",fontsize=12)
    a.annotate("",xy=(1.1,.2),xytext=(1.1,1.9),arrowprops={"arrowstyle":"<->"})
    a.text(1.2,1.05,"$L$",fontsize=14)
    a.set(xlim=(-1.6,1.6),ylim=(-.2,2.8));a.axis("off")
    q=np.linspace(.35,2.1,250)
    b.plot(q,(2/q+q*q)/3,color=BLUE,linestyle="-")
    b.scatter([1],[1],color="black",zorder=3)
    b.axvline(1,color="black",linestyle=":",lw=1)
    b.annotate("Unique minimum",xy=(1,1),xytext=(1.1,1.8),fontsize=11,
                arrowprops={"arrowstyle":"->","color":"black"})
    axes(b,"$D/D^*$","Cost / minimum cost")
    b.set(ylim=(.8,2.1),xticks=[.5,1,1.5,2])
    return fig


def actions_information():
    fig,ax=plt.subplots(figsize=(8.2,2.6),layout="constrained")
    for y,title,example in [(2,"Action","Choose a schedule"),(1,"Inference","Fit model parameters"),(0,"Information","Choose an experiment")]:
        box(ax,(0,y),2.3,.65,title)
        ax.annotate("",xy=(3,y+.325),xytext=(2.35,y+.325),arrowprops={"arrowstyle":"->"})
        ax.text(3.1,y+.325,example,va="center",fontsize=14)
    ax.set(xlim=(-.1,8),ylim=(-.1,2.8));ax.axis("off")
    return fig


def lp_qp():
    fig,aa=plt.subplots(1,2,figsize=(8,2.7),layout="constrained")
    x=np.linspace(0,2,150)
    for a in aa:
        a.fill_between(x,0,2-x,alpha=.1,color=BLUE,hatch="//",edgecolor=BLUE)
        a.plot(x,2-x,color=BLUE,linestyle="-")
        a.set(xlim=(0,2.2),ylim=(0,2.2),aspect="equal")
        axes(a,"$x_1$","$x_2$")
    for k in (.5,1.5,2.5):aa[0].plot(x,k-2*x,color=ORANGE,linestyle="--",lw=1.5)
    aa[0].set_title("LP: linear objective levels",fontsize=13)
    for r in (.3,.6,1.):aa[1].add_patch(plt.Circle((.55,.65),r,fill=False,color=ORANGE,linestyle="--",lw=1.5))
    aa[1].set_title("QP: quadratic objective levels",fontsize=13)
    return fig


def nlp_milp():
    fig,(a,b)=plt.subplots(1,2,figsize=(8,2.8),layout="constrained")
    x=np.linspace(0,1.4,180)
    a.fill_between(x,x*x,2,color=BLUE,alpha=.12,hatch="//",edgecolor=BLUE)
    a.plot(x,x*x,color=BLUE,linestyle="-")
    a.text(.1,1.65,"$x_2\\geq x_1^2$",fontsize=12)
    a.set(xlim=(0,1.6),ylim=(0,2.1));axes(a,"$x_1$","$x_2$")
    a.set_title("NLP: curved constraint",fontsize=13)
    for y in (0,1):b.plot([0,2],[y,y],color=BLUE,linestyle="-",marker="o")
    b.axhline(.5,color="0.5",linestyle="--",lw=1.2)
    b.text(.15,.57,"Fractional $y$ excluded",fontsize=11)
    b.set(xlim=(-.1,2.1),ylim=(-.2,1.3),yticks=[0,1]);axes(b,"Continuous $x$","Binary $y$")
    b.set_title("MILP: two feasible line segments",fontsize=13)
    return fig


def dynamic_timeline():
    fig,ax=plt.subplots(figsize=(8.2,1.9),layout="constrained")
    ax.annotate("",xy=(4.3,0),xytext=(-.2,0),arrowprops={"arrowstyle":"->","lw":1.5})
    for t,label in [(0,"Initial state"),(1,"Control choice"),(2,"State evolves"),(4,"Terminal condition")]:
        ax.plot([t,t],[-.12,.12],color="black",linestyle="-")
        ax.text(t,-.3,label,ha="center",fontsize=11)
    ax.text(0,.35,"$\\mathbf{x}(0)=\\mathbf{x}_{\\rm init}$",ha="center",fontsize=14)
    ax.text(2.3,.35,"$\\dot{\\mathbf{x}}=\\mathbf{f}(\\mathbf{x},\\mathbf{u},\\mathbf{z})$",ha="center",fontsize=14)
    ax.text(4.4,.12,"$t$",fontsize=14)
    ax.set(xlim=(-.55,4.75),ylim=(-.8,.9));ax.axis("off")
    return fig


def storage_network():
    fig,ax=plt.subplots(figsize=(8.2,2.3),layout="constrained")
    box(ax,(0,.4),2,1.2,"Market\n$p_t$ [\\$/MWh]",color="black")
    box(ax,(5,.4),2.6,1.2,"Storage\n$E_{t-1}\\to E_t$ [MWh]")
    ax.annotate("",xy=(5,1.35),xytext=(2,1.35),arrowprops={"arrowstyle":"->","color":BLUE,"lw":2})
    ax.annotate("",xy=(2,.65),xytext=(5,.65),arrowprops={"arrowstyle":"->","color":ORANGE,"lw":2,"linestyle":"--"})
    ax.text(3.5,1.6,"Charge $c_t$ [MW]",ha="center",fontsize=12,color=BLUE)
    ax.text(3.5,.25,"Discharge $d_t$ [MW]",ha="center",fontsize=12,color=ORANGE)
    ax.text(4,-.15,"Energy change: $(\\sqrt{\\eta} c_t-d_t/\\sqrt{\\eta})\\Delta t$",ha="center",fontsize=12)
    ax.set(xlim=(-.1,8),ylim=(-.4,2.1));ax.axis("off")
    return fig


def cycle_removal():
    fig,aa=plt.subplots(1,2,figsize=(8,2.8),layout="constrained")
    for a,p in zip(aa,(1,-1)):
        c=np.linspace(0,1,150)
        a.plot(c,.88*c,color=BLUE,linestyle="-",label="Same energy change: zero")
        a.scatter([0,1],[0,.88],color="black",zorder=3)
        a.annotate("",xy=(.2,.176),xytext=(.8,.704),arrowprops={"arrowstyle":"->","color":ORANGE,"lw":2})
        a.text(.04,1.01,"Remove overlap",fontsize=11,color=ORANGE)
        a.set(xlim=(-.05,1.1),ylim=(-.05,1.1),aspect="equal")
        axes(a,"Charge $c$ [MW]","Discharge $d$ [MW]")
        a.set_title(f"Price $p={p}$, $\\eta=0.88$",fontsize=13)
    fig.suptitle("Move along an energy-balance line",fontsize=14)
    return fig


def uncertainty_tree():
    fig,ax=plt.subplots(figsize=(8.2,2.5),layout="constrained")
    box(ax,(0,.6),2.2,1,"One shared\nfirst action")
    for y,txt in [(2,"Low-price recourse"),(1,"Middle-price recourse"),(0,"High-price recourse")]:
        ax.annotate("",xy=(4,y+.25),xytext=(2.2,1.1),arrowprops={"arrowstyle":"->","color":"black"})
        box(ax,(4,y),3.7,.5,txt,color=BLUE,linestyle=["-","--",":"][2-y])
    ax.text(2.6,-.3,"Scenario revealed",ha="center",fontsize=12)
    ax.set(xlim=(-.1,8),ylim=(-.6,2.7));ax.axis("off")
    return fig


def inference_residuals():
    fig,ax=plt.subplots(figsize=(7.8,2.8),layout="constrained")
    x=np.arange(5);y=np.array([1.1,1.8,3.2,3.7,5.2]);pred=1+x
    ax.plot(x,pred,color=BLUE,linestyle="-",label="$m(x,\\boldsymbol{\\theta})=\\theta_0+\\theta_1x$")
    ax.scatter(x,y,color="black",marker="o",label="Measurements")
    for xx,yy,pp in zip(x,y,pred):ax.plot([xx,xx],[pp,yy],color=ORANGE,linestyle="--",lw=2)
    ax.annotate("Residual $y_i-m(x_i,\\boldsymbol{\\theta})$",xy=(2,3.1),xytext=(.1,4.8),arrowprops={"arrowstyle":"->"},fontsize=12)
    axes(ax,"Condition $x_i$","Response $y_i$");ax.legend(loc="lower right",fontsize=11)
    return fig


def decision_process():
    fig,ax=plt.subplots(figsize=(8.2,2.4),layout="constrained")
    names=["Problem","Model","Optimize","Interpret","Decision"]
    for i,n in enumerate(names):
        box(ax,(i*1.65,1),1.42,.8,n)
        if i<4:ax.annotate("",xy=((i+1)*1.65,1.4),xytext=(i*1.65+1.42,1.4),arrowprops={"arrowstyle":"->","color":"black"})
    ax.plot([7.2,7.2,1.9],[1,.45,.45],color=ORANGE,linestyle="--",lw=1.5)
    ax.annotate("",xy=(1.9,1),xytext=(1.9,.45),arrowprops={"arrowstyle":"->","color":ORANGE,"linestyle":"--"})
    ax.text(4.5,.1,"Check outcomes and revise assumptions",ha="center",fontsize=12)
    ax.set(xlim=(-.1,8.2),ylim=(-.15,2));ax.axis("off")
    return fig
