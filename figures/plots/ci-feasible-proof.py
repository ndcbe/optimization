"""Convex feasible-set proof sketch; Biegler (2010), Thm. 4.2, pp. 64–65.

Original model: g(x)=x1**2+x2**2-1, h(x)=x2, xb=(-.7,0), xa=(.8,0).
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle


def make_figure():
    fig, (geom, values) = plt.subplots(
        1, 2, figsize=(7.2, 2.0), layout="constrained",
        gridspec_kw={"width_ratios": [1, 1.45]})
    geom.add_patch(Circle((0, 0), 1, facecolor="#56B4E9", alpha=.16,
                          hatch="//", edgecolor="#0072B2", linewidth=1.3))
    geom.plot([-1.3, 1.3], [0, 0], "--", color="black", linewidth=1)
    geom.plot([-.7, .8], [0, 0], "o-", color="black", linewidth=2.5, ms=5)
    geom.plot(-.1, 0, "s", color="#D55E00", ms=6)
    geom.text(-.9, -.32, r"$\mathbf{x}_b$", fontsize=12)
    geom.text(.71, -.32, r"$\mathbf{x}_a$", fontsize=12)
    geom.text(-.24, .17, r"$\bar{\mathbf{x}}$", fontsize=12)
    geom.text(.45, .65, r"$g\leq 0$", fontsize=11)
    geom.text(-1.28, -.63, r"$h=0$", fontsize=11)
    geom.set(xlim=(-1.4, 1.4), ylim=(-1.08, 1.08), aspect="equal")
    geom.set_title("Feasible endpoints and segment", fontsize=12)
    geom.axis("off")

    t = np.linspace(0, 1, 201)
    g = (-.7 + 1.5*t)**2 - 1
    chord = (1-t)*(-.51) + t*(-.36)
    values.plot(t, g, color="black", linewidth=2)
    values.plot(t, chord, "--", color="#0072B2", linewidth=1.8)
    values.axhline(0, color="black", linestyle=":", linewidth=1.5)
    values.plot([0, 1], [-.51, -.36], "o", color="black", ms=5)
    values.plot(.4, -.99, "s", color="#D55E00", ms=6)
    values.text(.38, -.71, r"$g(\bar{\mathbf{x}})$", fontsize=12)
    values.text(.08, -.31, "endpoint mixture", fontsize=11)
    values.text(.08, .025, "feasibility bound", fontsize=11)
    values.set(xlim=(-.02, 1.02), ylim=(-1.08, .16),
               xticks=[0, .4, 1], xticklabels=["0", "0.4", "1"],
               yticks=[-1, 0], xlabel=r"weight $\theta$")
    values.set_title("Constraint ≤ chord ≤ 0", fontsize=12)
    values.xaxis.label.set_size(12)
    values.tick_params(labelsize=10)
    return fig
