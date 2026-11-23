"""Prepared Lecture 20 worked example: checking LICQ and MFCQ at three points.
Analytic inputs only; no solver results. One source serves the handout and the
Constraint-Qualifications website reference.

   min x1 + 3 x2
   s.t. g1 = -x1 <= 0,  g2 = x1 - x2 <= 0,  g3 = x1 + x2 - 2 <= 0,
        g4 = -x1 - x2 <= 0.
Feasible set: the triangle with vertices (0,0), (0,2), (1,1).
Points: A=(1/2,3/2) on g3 only; B=(0,2) on g1,g3; C=(0,0) on g1,g2,g4.
Line styles and labels (not only colour) identify each constraint.
"""
import numpy as np
import matplotlib.pyplot as plt

C1, C2, C3, C4 = '#0072B2', '#D55E00', '#009E73', '#CC79A7'

def make_figure():
    fig, ax = plt.subplots(figsize=(6.2, 4.3))
    tri = plt.Polygon([(0, 0), (0, 2), (1, 1)], closed=True, facecolor='0.9',
                      edgecolor='none', hatch='//', alpha=.5)
    ax.add_patch(tri)
    s = np.linspace(-1.1, 2.3, 10)
    ax.plot([0, 0], [-.9, 2.5], color=C1, ls='-', lw=2)
    ax.plot(s, s, color=C2, ls='--', lw=2)
    ax.plot(s, 2 - s, color=C3, ls='-.', lw=2)
    ax.plot(s, -s, color=C4, ls=':', lw=2.4)
    for c in (1, 3, 5, 7):
        t = np.linspace(-.5, 2.2, 5)
        ax.plot(t, (c - t) / 3, color='0.55', ls=(0, (1, 3)), lw=.9)
    ax.text(1.45, .1, r'$f=$ const', fontsize=11, color='0.2',
            bbox=dict(fc='white', ec='none', alpha=.9, pad=1.5))
    ax.text(-.95, 2.35, r'$g_1=0$', color=C1, fontsize=12, bbox=dict(fc='white', ec='none', alpha=.9, pad=1.5))
    ax.text(.95, 1.95, r'$g_2=0$', color=C2, fontsize=12, bbox=dict(fc='white', ec='none', alpha=.9, pad=1.5))
    ax.text(1.55, .72, r'$g_3=0$', color=C3, fontsize=12, bbox=dict(fc='white', ec='none', alpha=.9, pad=1.5))
    ax.text(-1.15, 1.15, r'$g_4=0$', color=C4, fontsize=12, bbox=dict(fc='white', ec='none', alpha=.9, pad=1.5))
    for (x, y, lab, dx, dy) in [(.5, 1.5, 'A', .08, .1), (0, 2, 'B', .09, .06),
                                (0, 0, 'C', -.2, .12)]:
        ax.scatter([x], [y], color='black', s=45, zorder=6)
        ax.text(x + dx, y + dy, lab, fontsize=14, weight='bold')
    for v, col, lab, pos in [((-.6, 0), C1, r'$\nabla g_1$', (-.98, .13)),
                             ((.55, -.55), C2, r'$\nabla g_2$', (.66, -.46)),
                             ((-.5, -.5), C4, r'$\nabla g_4$', (-1.28, -.3))]:
        ax.annotate('', xy=v, xytext=(0, 0), zorder=5,
                    arrowprops=dict(arrowstyle='->', lw=2.6, color=col))
        ax.text(pos[0], pos[1], lab, color=col, fontsize=13, zorder=7,
                bbox=dict(fc='white', ec='none', alpha=.9, pad=1.2))
    ax.set_aspect('equal')
    ax.set(xlim=(-1.3, 2.4), ylim=(-1.0, 2.6), xlabel='$x_1$', ylabel='$x_2$')
    ax.axhline(0, color='black', lw=.6)
    fig.tight_layout()
    return fig
