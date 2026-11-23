"""Prepared Lecture 20 geometry/proof sketch; analytic inputs, no solver results.
One source serves the handout and Constraint-Qualifications website reference.
Direct labels, line styles and hatches preserve meaning in greyscale.

Problem  min x1  s.t.  h = x2 = 0,  g1 = -x1 <= 0,  g2 = -2 x1 <= 0.
Left: the equality line, the (identical) inequality half-planes, the feasible
ray, objective contours and the active gradients at the origin.
Right (small): the nonnegative multipliers u1 + 2 u2 = 1.
"""
import numpy as np
import matplotlib.pyplot as plt

BLUE, ORANGE = '#0072B2', '#D55E00'

def make_figure():
    fig = plt.figure(figsize=(7.6, 3.0))
    gs = fig.add_gridspec(1, 2, width_ratios=[1.9, 1.0], wspace=.32)
    ax = fig.add_subplot(gs[0])
    ax.fill_between([0, 2.6], -1.3, 1.3, facecolor='0.92', edgecolor='none',
                    hatch='//', alpha=.45)
    ax.axvline(0, color='black', lw=.8)
    for c in (.7, 1.4, 2.1):
        ax.plot([c, c], [-1.3, 1.3], color='0.45', ls='--', lw=1)
    ax.text(.78, 1.05, r'$f=x_1$ contours', fontsize=9, color='0.2', zorder=6,
            bbox=dict(fc='white', ec='none', alpha=.85, pad=1.5))
    ax.plot([-2.2, 2.6], [0, 0], color='black', lw=1.6, zorder=3)
    ax.plot([0, 2.6], [0, 0], color='black', lw=5, solid_capstyle='butt', zorder=4)
    ax.text(1.0, .12, r'feasible set', fontsize=10, zorder=6,
            bbox=dict(fc='white', ec='none', alpha=.85, pad=1.5))
    ax.text(-2.1, .1, r'$h=x_2=0$', fontsize=10)
    ax.text(.1, -1.2, r'$g_1=g_2=0$', fontsize=10, zorder=6,
            bbox=dict(fc='white', ec='none', alpha=.85, pad=1.5))
    for v, col, dy, lab in [((-1, .35), BLUE, .12, r'$\nabla g_1$'),
                            ((-2, -.35), ORANGE, -.3, r'$\nabla g_2$')]:
        ax.annotate('', xy=v, xytext=(0, v[1]),
                    arrowprops=dict(arrowstyle='->', lw=3, color=col))
        ax.text(v[0] + .02, v[1] + dy, lab, fontsize=11, color=col)
    ax.annotate('', xy=(0, .9), xytext=(0, 0),
                arrowprops=dict(arrowstyle='->', lw=3, color='0.3'))
    ax.text(.08, .55, r'$\nabla h$', fontsize=11)
    ax.scatter([0], [0], color='black', s=40, zorder=5)
    ax.set(xlim=(-2.3, 2.7), ylim=(-1.35, 1.35), xlabel='$x_1$', ylabel='$x_2$')
    ax.set_title('Constraints, feasible set and objective contours', fontsize=10)
    ax2 = fig.add_subplot(gs[1])
    u = np.linspace(0, 1, 100)
    ax2.plot(u, (1 - u) / 2, color=BLUE, ls='-')
    ax2.scatter([0, 1], [.5, 0], color='black', marker='o', s=30, zorder=4)
    ax2.set(xlim=(-.1, 1.1), ylim=(-.05, .62), xlabel='$u_1$', ylabel='$u_2$')
    ax2.axhline(0, color='black', lw=.7)
    ax2.axvline(0, color='black', lw=.7)
    ax2.set_title(r'$u_1+2u_2=1,\ u_i\geq0$', fontsize=9)
    ax2.tick_params(labelsize=8)
    return fig
