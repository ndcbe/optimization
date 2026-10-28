"""Local Newton model of the pre-August website's scalar polynomial.
The function and derivatives are loaded from the canonical Globalization cell.
This prepared two-panel comparison adds no independent model implementation.
"""
import json
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

def make_figure():
    path=Path(__file__).resolve().parents[2]/"notebooks/6-dev/Globalization.ipynb"
    cells=json.loads(path.read_text())["cells"]
    cell=next(c for c in cells if c.get("id")=="gl-904d581543155af1")
    scope={}
    exec("".join(cell["source"]),scope)
    f,df,ddf=(scope[k] for k in ("f","df","ddf"))
    x0=-3.0
    p=-df(x0)/ddf(x0)
    x1=x0+p
    x=np.linspace(-3.2,-1.25,400)
    model=f(x0)+df(x0)*(x-x0)+0.5*ddf(x0)*(x-x0)**2
    slope=df(x0)+ddf(x0)*(x-x0)
    fig,axs=plt.subplots(1,2,figsize=(8.8,3.1),layout="constrained")
    for ax,truth,approx,ylabel in zip(axs,(f(x),df(x)),(model,slope),("Value","Slope")):
        ax.plot(x,truth,color="#0072B2",linestyle="-",label="$f$" if ylabel=="Value" else "$f'$")
        ax.plot(x,approx,color="black",linestyle="--",label="Quadratic model" if ylabel=="Value" else "Model slope")
        ax.axhline(0,color="black",linewidth=.6)
        ax.axvline(x1,color=".45",linestyle=":",linewidth=1)
        ax.set(xlabel="$x$",ylabel=ylabel,xlim=(-3.2,-1.25))
        ax.tick_params(labelsize=10)
        ax.legend(fontsize=10,loc="upper center")
    axs[0].plot([x0,x1],[f(x0),f(x1)],color="#0072B2",linestyle="none",marker="o",markersize=5)
    axs[1].plot([x1],[0],color="black",marker="s",markersize=5)
    axs[1].plot([x1],[df(x1)],color="#0072B2",marker="o",markersize=5)
    axs[0].annotate("$x^{k+1}$",(x1,-12),xytext=(x1,-21),ha="center",fontsize=11)
    axs[0].set_ylim(-23,55)
    axs[1].set_ylim(-72,80)
    return fig
