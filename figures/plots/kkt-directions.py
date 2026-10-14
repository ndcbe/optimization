"""The exact log-example's equality rail, tangent fence, and feasible inward step."""
import numpy as np
import matplotlib.pyplot as plt
def make_figure():
    fig,axs=plt.subplots(1,2,figsize=(7.2,3.0),layout="constrained")
    a=np.sqrt(2);x=np.linspace(.8,2.05,250)
    axs[0].plot(x,4/x,color="#D55E00",linestyle="--",linewidth=1.8)
    axs[0].plot(x,2*x,color="#0072B2",linestyle="-",linewidth=1.8)
    axs[0].plot(a,2*a,'o',color="black",ms=5)
    axs[0].annotate("",xy=(a+.3,2*a+.6),xytext=(a,2*a),arrowprops=dict(arrowstyle='->',color="#0072B2",lw=2))
    axs[0].annotate(r"$g=0$",xy=(.98,4/.98),xytext=(1.10,4.75),fontsize=12,arrowprops=dict(arrowstyle="-",color="black"))
    axs[0].annotate(r"$h=0$",xy=(1.8,3.6),xytext=(1.60,4.75),fontsize=12,arrowprops=dict(arrowstyle="-",color="black"))
    axs[0].set(xlim=(.8,2.1),ylim=(1.6,5.15),xlabel=r"$x_1$",ylabel=r"$x_2$",title="constraints in x space")
    q=np.linspace(-1.2,1.2,50)
    axs[1].plot(q,2*q,color="#0072B2",linestyle="-",lw=1.5)
    axs[1].plot(q,-2*q,color="#D55E00",linestyle="--",lw=1.5)
    axs[1].plot(0,0,'o',color="black",ms=5)
    axs[1].annotate("",xy=(.65,1.3),xytext=(0,0),arrowprops=dict(arrowstyle='->',color="black",lw=2))
    axs[1].text(.10,1.90,r"$\mathbf{p}=(1,2)^T$",fontsize=11)
    axs[1].text(-1.13,-.95,r"$\nabla h^T\mathbf{p}=0$",fontsize=10)
    axs[1].text(-1.1,.55,r"$\nabla g^T\mathbf{p}=0$",fontsize=10)
    axs[1].set(xlim=(-1.25,1.25),ylim=(-2.4,2.4),xlabel=r"$p_1$",ylabel=r"$p_2$",title="first-order directions")
    for ax in axs:
        ax.axhline(0,color="black",lw=.7,zorder=0)
        ax.axvline(0,color="black",lw=.7,zorder=0)
    return fig
