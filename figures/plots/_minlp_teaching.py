"""Analytic MINLP definitions and proof mechanisms; solver plots stay in the notebook."""
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle


def assignment_growth():
    """Count binary assignments before any constraint propagation."""
    t = np.arange(0, 41)
    fig, ax = plt.subplots(figsize=(7.6, 2.8))
    ax.semilogy(t, 2.0**t, color='black', linestyle='-', label=r'$2^t$ bit assignments')
    selected = np.array([10, 20, 25, 30, 35])
    ax.semilogy(selected, 2.0**selected, 's', color='#0072B2', markersize=6)
    ax.set(xlabel='number of binary variables', ylabel='bit assignments',
           xlim=(0, 40), ylim=(.8, 2e12))
    ax.legend(loc='upper left', fontsize=11)
    fig.tight_layout()
    return fig


def bound_inclusion():
    """An exact quadratic example of restriction/original/relaxation bounds."""
    x = np.linspace(-2, 2, 401)
    fig, ax = plt.subplots(figsize=(7.6, 3.1))
    ax.plot(x, (x-1.5)**2, color='black', label=r'$f(x)=(x-1.5)^2$')
    rows = [('relaxation R', -2, 2, -1.9, 'o', 'black', 1.5, 0),
            ('original S', -1, 1, -1.1, 's', '#0072B2', 1, .25),
            ('restriction T', -.5, .5, -.3, '^', '#D55E00', .5, 1)]
    for label, lo, hi, level, marker, color, point, value in rows:
        ax.plot([lo, hi], [level, level], marker=marker, color=color, linewidth=2)
        ax.text(hi+.05, level, label, fontsize=11, va='center')
        ax.scatter([point], [value], marker=marker, color=color, s=55, zorder=4)
    ax.text(-1.85, 4.5, r'$\min_R f=0\ \leq\ \min_S f=.25\ \leq\ \min_T f=1$', fontsize=12,
            bbox={'facecolor':'white','edgecolor':'none','pad':2})
    ax.text(.98, .96, r'$f(x)=(x-1.5)^2$', transform=ax.transAxes,
            ha='right', va='top', fontsize=11)
    ax.set(xlabel='coordinate x', ylabel='objective value',
           xlim=(-2.1, 3.1), ylim=(-2.4, 6.5))
    fig.tight_layout()
    return fig


def fathom_proof():
    """Show the distinct logical reasons for closing a node when seeking one optimum."""
    fig, ax = plt.subplots(figsize=(7.6, 2.65))
    ax.axis('off')
    cases = [('certified infeasible', 'descendants add\nrestrictions; no\nfeasible point returns', 'close node'),
             (r'certified $\ell_j\geq U$', 'every descendant\ncost is at least\nthe incumbent value', 'close node'),
             ('optimal relaxation\npoint is integer', 'original feasibility\nand cost attain\nthe node lower bound', 'update U; close node')]
    for i, (condition, reason, action) in enumerate(cases):
        left = .015 + i/3
        ax.add_patch(Rectangle((left, .13), .305, .78, facecolor='#E9F2F7', edgecolor='black'))
        ax.text(left+.1525, .80, condition, ha='center', va='center', fontsize=11, fontweight='bold')
        ax.text(left+.1525, .52, reason, ha='center', va='center', fontsize=11)
        ax.annotate('', (left+.1525, .28), (left+.1525, .38), arrowprops={'arrowstyle':'->'})
        ax.text(left+.1525, .20, action, ha='center', va='center', fontsize=11)
    fig.tight_layout()
    return fig


def pure_mixed_cut():
    """The pure Gomory cut need not preserve a mixed row's feasible points."""
    fig, ax = plt.subplots(figsize=(7.6, 2.9))
    x = np.linspace(0, 1, 101)
    ax.plot(x, 1.5-1.5*x, color='black', label=r'row $x_B+1.5x_N=1.5$')
    ax.axvspan(1, 1.15, facecolor='#0072B2', alpha=.12, hatch='///', edgecolor='black')
    ax.axvline(1, color='#0072B2', linestyle='--', label=r'proposed cut $x_N\geq1$')
    ax.scatter([1], [0], color='black', marker='s', s=65, zorder=4)
    ax.scatter([1/3], [1], facecolors='white', edgecolors='black', marker='o', s=65, zorder=4)
    ax.annotate('integer point\n(1, 0)', (1, 0), xytext=(-80, 25), textcoords='offset points',
                arrowprops={'arrowstyle':'->'}, fontsize=11)
    ax.annotate('mixed point\n(1/3, 1)', (1/3, 1), xytext=(-65, -45), textcoords='offset points',
                arrowprops={'arrowstyle':'->'}, fontsize=11)
    ax.set(xlabel=r'nonbasic coordinate $x_N$', ylabel=r'basic coordinate $x_B$',
           xlim=(-.03, 1.15), ylim=(-.08, 1.65))
    ax.legend(loc='upper right', fontsize=10)
    fig.tight_layout()
    return fig


def phase_one():
    """Minimize the largest affine violation on the compact interval [0,2]."""
    fig, axes = plt.subplots(1, 2, figsize=(7.6, 3.0))
    x = np.linspace(0, 2, 401)
    for y, ax in enumerate(axes):
        first, second = x-1, -x-.2+1.7*y
        point, value = (.4, -.6) if y == 0 else (1.25, .25)
        ax.plot(x, first, color='#0072B2', linestyle='-', label=r'$g_1=x-1$')
        ax.plot(x, second, color='#D55E00', linestyle='--', label=r'$g_2=-x-.2+1.7y$')
        ax.plot(x, np.maximum(first, second), color='black', linestyle=':', linewidth=2.5,
                label='largest violation')
        ax.axhline(0, color='black', linewidth=.8)
        ax.scatter([point], [value], marker='s', color='black', s=45, zorder=4)
        ax.set(xlabel='continuous x', title=f'fixed y = {y}', xlim=(0, 2), ylim=(-1.5, 1.8))
        ax.text(.10, -1.2, rf'$\eta^*={value:g}$: '+('feasible' if y == 0 else 'infeasible'), fontsize=11,
                bbox={'facecolor':'white','edgecolor':'none','pad':2})
    axes[0].set_ylabel('normalized violation')
    axes[0].legend(loc='upper left', fontsize=10)
    fig.tight_layout(w_pad=2.0)
    return fig


def bound_partition():
    """Evaluated and remaining sets contribute different pieces of the full bound."""
    fig, ax = plt.subplots(figsize=(7.6, 2.7))
    ax.axis('off')
    boxes = [(.02, .52, .43, .40, 'evaluated design\nretained interval [7, 8]'),
             (.55, .52, .43, .40, 'remaining designs\ncertified lower value 9'),
             (.16, .04, .68, .28, r'full $L=\min(7,9)=7$; feasible $U=8$'+'\n'+r'gap $U-L=1$, although $U-L_{\rm rem}=-1$')]
    for left, bottom, width, height, text in boxes:
        ax.add_patch(Rectangle((left,bottom),width,height,facecolor='#E9F2F7',edgecolor='black'))
        ax.text(left+width/2,bottom+height/2,text,ha='center',va='center',fontsize=12)
    for start in [.235,.765]:
        ax.annotate('', (.5,.33), (start,.51), arrowprops={'arrowstyle':'->','linewidth':1.3})
    fig.tight_layout()
    return fig


def search_flow():
    """The status-aware exclusion loop retains certificates before excluding designs."""
    fig, ax = plt.subplots(figsize=(7.6, 2.6))
    ax.axis('off')
    labels = ['evaluate design;\ncheck solver status', 'store its interval;\nadd valid cuts', 'exclude only after\nretaining its value',
              'stop, select new\ndesign, or report stall', 'compute full lower\nvalue and global gap', 'solve remaining\nmaster; check status']
    positions = [(0,.58),(.34,.58),(.68,.58),(0,.08),(.34,.08),(.68,.08)]
    for (left,bottom), label in zip(positions,labels):
        ax.add_patch(Rectangle((left,bottom),.30,.31,facecolor='#E9F2F7',edgecolor='black'))
        ax.text(left+.15,bottom+.155,label,ha='center',va='center',fontsize=11)
    for y in [.735,.235]:
        for x in [.305,.645]:
            ends = ((x+.025,y),(x,y)) if y>.5 else ((x,y),(x+.025,y))
            ax.annotate('',*ends,arrowprops={'arrowstyle':'->','linewidth':1.3})
    ax.annotate('',(.83,.40),(.83,.57),arrowprops={'arrowstyle':'->','linewidth':1.3})
    fig.tight_layout()
    return fig


def surrogate_proof():
    """A domain correction yields a valid reduced cut without exact stationarity."""
    fig, ax = plt.subplots(figsize=(7.6, 2.05))
    ax.axis('off')
    labels = [r'$C\geq L(\mathbf{x},\mathbf{y};\mathbf{u})$'+'\nfeasible rows,\n'+r'$\mathbf{u}\geq0$',
              'convex tangent\n'+r'$L\geq q(\mathbf{y})+\mathbf{a}^{\mathsf{T}}(\mathbf{x}-\mathbf{x}^k)$',
              'minimize over X\n'+r'$\delta=\min_X\mathbf{a}^{\mathsf{T}}(\mathbf{x}-\mathbf{x}^k)$',
              r'$C\geq q(\mathbf{y})+\delta$'+'\nvalid reduced\nobjective cut']
    for i,label in enumerate(labels):
        left=.015+.25*i
        ax.add_patch(Rectangle((left,.18),.215,.65,facecolor='#E9F2F7',edgecolor='black'))
        ax.text(left+.1075,.505,label,ha='center',va='center',fontsize=10)
        if i<3:ax.annotate('',(left+.247,.505),(left+.22,.505),arrowprops={'arrowstyle':'->','linewidth':1.3})
    fig.tight_layout()
    return fig
