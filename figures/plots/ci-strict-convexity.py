"""Strict-convexity uniqueness contradiction; Biegler Thm. 4.3, p. 65.

Original normalized slice q(t)=-t(1-t). Endpoints are hypothetical minimizers,
not actual minima of this illustrative curve: the midpoint disproves that premise.
"""
import numpy as np
import matplotlib.pyplot as plt


def make_figure():
    fig, ax = plt.subplots(figsize=(5.4, 1.7), layout="constrained")
    t = np.linspace(0, 1, 201)
    ax.axhline(0, color="#0072B2", linestyle="--", linewidth=1.6)
    ax.plot(t, -t*(1-t), color="black", linewidth=2)
    ax.plot([0, 1], [0, 0], "o", color="black", ms=5)
    ax.plot(.5, -.25, "s", color="#D55E00", ms=6)
    ax.annotate("below the proposed minimum", xy=(.5, -.25),
                xytext=(.52, -.10), ha="center", fontsize=11,
                arrowprops={"arrowstyle": "-", "linewidth": .8})
    ax.text(.10, .022, r"equal endpoint values $f^*$", fontsize=11)
    ax.set(xlim=(-.04, 1.04), ylim=(-.30, .09), yticks=[-.25, 0],
           xticks=[0, .5, 1],
           xticklabels=[r"$\mathbf{y}$", r"$\frac{1}{2}(\mathbf{y}+\mathbf{z})$", r"$\mathbf{z}$"])
    ax.tick_params(labelsize=11)
    return fig
