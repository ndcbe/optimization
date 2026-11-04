"""Local-to-global contradiction: Biegler Thm. 4.3, p. 65; N&W Thm. 2.5, p. 16.

Original geometry and normalized convex objective slice q(theta).
xa is a putative local minimizer: a better feasible xb contradicts that premise.
"""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Ellipse


def make_figure():
    fig, (geom, values) = plt.subplots(
        1, 2, figsize=(7.2, 2.35), layout="constrained",
        gridspec_kw={"width_ratios": [1.1, 1.35]})
    a = np.array([-.85, .25])
    b = np.array([1.05, -.4])
    theta, epsilon = .83, .4
    v = theta*a + (1-theta)*b
    geom.add_patch(Ellipse((0, 0), 3.4, 1.4, facecolor="#56B4E9",
                          alpha=.16, hatch="//", edgecolor="#0072B2", linewidth=1.3))
    geom.add_patch(Circle(a, epsilon, facecolor="none", edgecolor="black",
                         linestyle="--", linewidth=1.5))
    geom.plot([a[0], b[0]], [a[1], b[1]], color="black", linewidth=1.5)
    geom.plot([a[0], b[0]], [a[1], b[1]], "o", color="black", ms=5)
    geom.plot(*v, "s", color="#D55E00", ms=6)
    geom.text(a[0]-.27, a[1]+.12, r"$\mathbf{x}_a$", fontsize=12)
    geom.text(b[0]+.10, b[1]-.13, r"$\mathbf{x}_b$", fontsize=12)
    geom.annotate(r"$\bar{\mathbf{x}}$", xy=v, xytext=(.0, .46), fontsize=12,
                  arrowprops={"arrowstyle": "-", "linewidth": .8})
    geom.text(-1.7, -.75, r"dashed: $\mathcal{N}_{\epsilon}(\mathbf{x}_a)$", fontsize=11)
    geom.text(.55, .62, r"$\mathcal{F}$ convex", fontsize=11)
    geom.set(xlim=(-1.9, 1.9), ylim=(-.87, .87), aspect="equal")
    geom.set_title("Stay feasible and approach $\\mathbf{x}_a$", fontsize=12)
    geom.axis("off")

    t = np.linspace(0, 1, 201)
    q = lambda s: s - .6*s*(1-s)
    cutoff = 1 - epsilon/np.linalg.norm(b-a)
    values.axvspan(cutoff, 1, facecolor=".92", hatch="///", edgecolor=".65", linewidth=0)
    values.axhline(1, color="black", linestyle=":", linewidth=1.3)
    values.plot(t, t, "--", color="#0072B2", linewidth=1.8)
    values.plot(t, q(t), color="black", linewidth=2)
    values.plot([0, 1], [0, 1], "o", color="black", ms=5)
    values.plot(theta, q(theta), "s", color="#D55E00", ms=6)
    values.plot([theta, theta], [q(theta), 1], color="#D55E00", linewidth=1.1)
    values.text(.06, 1.04, r"$f(\mathbf{x}_a)$", fontsize=12)
    values.text(.06, .84, "endpoint mixture", fontsize=11)
    values.annotate(r"$f(\bar{\mathbf{x}})$", xy=(theta, q(theta)),
                    xytext=(.32, .08), fontsize=12,
                    arrowprops={"arrowstyle": "-", "linewidth": .8})
    values.set(xlim=(-.02, 1.04), ylim=(-.07, 1.22),
               xticks=[0, theta, 1], xticklabels=["0", "0.83", "1"],
               yticks=[0, 1], xlabel=r"weight $\theta$")
    values.set_title("Nearby point has lower value", fontsize=12)
    values.xaxis.label.set_size(12)
    values.tick_params(labelsize=10)
    return fig
