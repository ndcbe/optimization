"""Prepared constrained-optimization geometry; no notebook-generated results."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle


def make_figure():
    fig,axs=plt.subplots(1,2,figsize=(7.4,3),layout="constrained")
    for center,style in [(-.55,"-"),(.55,"--")]:
        axs[0].add_patch(Circle((center,0),1,facecolor="none",edgecolor="#0072B2",linestyle=style,linewidth=1.5))
    x=np.linspace(-.45,.45,160);y=np.sqrt(1-(abs(x)+.55)**2)
    axs[0].fill_between(x,-y,y,facecolor=(.337,.706,.914,.18),hatch="//",edgecolor="0.5",linewidth=.5)
    p=np.array([[-.15,.35],[.2,-.3]])
    axs[0].plot(p[:,0],p[:,1],color="black",linewidth=2,marker="o",ms=4)
    arrow=dict(arrowstyle="->",color="black",linewidth=.8)
    axs[0].annotate(r"$\mathbf{x}_a$",xy=p[0],xytext=(-1.15,.72),fontsize=11,arrowprops=arrow)
    axs[0].annotate(r"$\mathbf{x}_b$",xy=p[1],xytext=(.85,-.82),fontsize=11,arrowprops=arrow)
    for center in [-1.05,1.05]:
        axs[1].add_patch(Circle((center,0),.65,facecolor=(.337,.706,.914,.18),hatch="//",edgecolor="#0072B2",linewidth=1.5))
    axs[1].plot([-1.05,1.05],[0,0],color="black",linestyle="--",linewidth=1.5,marker="o",ms=4)
    axs[1].plot(0,0,"s",color="#D55E00",ms=5)
    axs[1].text(-1.35,-.23,r"$\mathbf{x}_a$",fontsize=11);axs[1].text(1.06,-.23,r"$\mathbf{x}_b$",fontsize=11)
    for ax,title in zip(axs,["Intersection","Union"]):
        ax.set(xlim=(-1.8,1.8),ylim=(-1.15,1.15),aspect="equal",title=title);ax.axis("off")
    return fig
