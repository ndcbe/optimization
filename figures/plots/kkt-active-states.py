"""Three exact lower-bound examples; classification is left to the student."""
import numpy as np
import matplotlib.pyplot as plt
def make_figure():
    fig,axs=plt.subplots(1,3,figsize=(7.2,2.6),layout="constrained")
    x=np.linspace(-1.4,1.9,300)
    for index,(ax,a) in enumerate(zip(axs,[-1,0,1]),1):
        ax.axvspan(0,1.9,facecolor=(.337,.706,.914,.17),hatch="//",edgecolor="0.5",linewidth=0)
        ax.plot(x,(x-a)**2,color="black",linestyle="-",lw=1.5)
        ax.axvline(0,color="0.5",linestyle="--",lw=1)
        star=max(a,0);ax.plot(star,(star-a)**2,'o',color="#0072B2",ms=6)
        ax.set(xlim=(-1.4,1.9),ylim=(-.15,4.4),xlabel="x",title=rf"({index}) $f=(x-({a}))^2$")
        ax.title.set_fontsize(11)
        ax.text(.10,3.2,"feasible\n"+r"$x\geq0$",fontsize=10,bbox=dict(facecolor="white",edgecolor="none",pad=1))
    axs[0].set_ylabel("f(x)")
    for ax in axs:
        ax.axhline(0,color="black",lw=.7,zorder=0)
        ax.axvline(0,color="black",lw=.7,zorder=0)
    return fig
