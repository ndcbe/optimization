"""Prepared constrained-optimization geometry; no notebook-generated results."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle


def make_figure():
    fig,axs=plt.subplots(1,2,figsize=(7.4,3),layout="constrained")
    x=np.linspace(-.7,1.5,250);axs[0].plot(x,(x*x-1)**2,color="black",linewidth=2)
    axs[0].plot([-.7,.7],[.2601,.2601],color="#0072B2",linestyle="--",linewidth=1.4,marker="o",ms=4)
    axs[0].set(xlim=(-.8,1.6),ylim=(-.75,1.65),title=r"(a) $(x^2-1)^2$")
    axs[0].plot([-.7,1.5],[-.12,-.12],color="#0072B2",linestyle="--",linewidth=2)
    axs[0].text(.32,-.29,"(i)",fontsize=11)
    axs[0].plot([.7,1.5],[-.4,-.4],color="#D55E00",linestyle=":",linewidth=2)
    axs[0].text(1.01,-.56,"(ii)",fontsize=11)
    x=np.linspace(0,2,200);axs[1].plot(x,np.maximum(0,1-x)**2,color="black",linewidth=2)
    axs[1].plot([2,2.7],[1,1],color="black",linewidth=2)
    axs[1].plot(2,0,"o",color="black",ms=5);axs[1].plot(2,1,"o",mfc="white",mec="black",ms=5)
    axs[1].set(xlim=(-.1,2.8),ylim=(-.75,1.2),title="(b) one upward jump")
    axs[1].plot([0,1.8],[-.12,-.12],color="#0072B2",linestyle="--",linewidth=2)
    axs[1].text(.8,-.29,"(i)",fontsize=11)
    axs[1].plot([1.5,2.5],[-.4,-.4],color="#D55E00",linestyle=":",linewidth=2)
    axs[1].text(1.9,-.56,"(ii)",fontsize=11)
    for ax in axs:ax.set(xlabel="x",ylabel="f(x)")
    return fig
