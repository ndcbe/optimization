"""Prepared constrained-optimization geometry; no notebook-generated results."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Rectangle, Ellipse


def make_figure():
    fig,ax=plt.subplots(figsize=(6.6,2.4),layout="constrained")
    ax.add_patch(Ellipse((0,0),width=3.4,height=1.4,facecolor="#56B4E9",alpha=.13,hatch="//",edgecolor="#0072B2",linewidth=1.4))
    a=np.array([-.85,.25]);b=np.array([1.05,-.4]);v=.83*a+.17*b
    ax.add_patch(Circle(a,.40,facecolor="none",edgecolor="black",linestyle="--",linewidth=1.5))
    ax.plot([a[0],b[0]],[a[1],b[1]],color="black",linewidth=1.4)
    ax.plot(a[0],a[1],"o",color="black",ms=6);ax.plot(b[0],b[1],"o",color="black",ms=6)
    ax.plot(v[0],v[1],"s",color="#D55E00",ms=6)
    ax.text(a[0]-.25,a[1]+.15,r"$\mathbf{x}_a$",fontsize=12)
    ax.text(b[0]+.08,b[1]-.06,r"$\mathbf{x}_b$",fontsize=12)
    ax.text(v[0]+.15,v[1]+.30,r"$\bar{\mathbf{x}}$",fontsize=12)
    ax.annotate("",xy=v,xytext=(v[0]+.18,v[1]+.26),arrowprops=dict(arrowstyle="-",color="black",linewidth=.8))
    ax.text(-1.7,.76,r"$\mathcal{N}_{\epsilon}(\mathbf{x}_a)$",fontsize=12)
    ax.text(.8,.70,r"$\mathcal{F}$ convex",fontsize=12)
    ax.set(xlim=(-1.9,1.9),ylim=(-.9,.9),aspect="equal");ax.axis("off")
    return fig
