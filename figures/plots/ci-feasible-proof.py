"""Prepared constrained-optimization geometry; no notebook-generated results."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle


def make_figure():
    fig,axs=plt.subplots(1,2,figsize=(7.2,3),layout="constrained")
    axs[0].add_patch(Circle((0,0),1,facecolor="#56B4E9",alpha=.16,hatch="//",edgecolor="#0072B2",linewidth=1.5))
    axs[0].plot([-1.25,1.25],[0,0],color="black",linestyle="--",linewidth=1.2)
    axs[0].plot([-.7,.8],[0,0],color="black",linewidth=2,marker="o",ms=5)
    axs[0].plot(-.1,0,"s",color="#D55E00",ms=6)
    axs[0].text(-.95,-.24,r"$\mathbf{x}_b$",fontsize=11);axs[0].text(.72,-.24,r"$\mathbf{x}_a$",fontsize=11)
    axs[0].text(-.28,.18,r"$\bar{\mathbf{x}}$",fontsize=11)
    axs[0].set(xlim=(-1.3,1.3),ylim=(-1.1,1.1),aspect="equal",title="Segment stays on h=0");axs[0].axis("off")
    t=np.linspace(0,1,160);v=(-.7+1.5*t)**2-1;chord=(1-t)*(-.51)+t*(-.36)
    axs[1].plot(t,v,color="black",linewidth=2,label=r"$g(\bar{\mathbf{x}})$")
    axs[1].plot(t,chord,color="#0072B2",linestyle="--",linewidth=1.5,label="endpoint mixture")
    axs[1].axhline(0,color="black",linestyle=":",linewidth=1.5,label="feasibility bound")
    axs[1].set(xlim=(0,1),ylim=(-1.08,.1),xlabel=r"weight $\theta$",ylabel="constraint value",title="g stays below its chord")
    axs[1].text(.33,-.83,r"$g(\bar{\mathbf{x}})$",fontsize=10)
    axs[1].text(.04,-.31,"endpoint mixture",fontsize=10)
    axs[1].text(.04,.025,"feasibility bound",fontsize=10)
    return fig
