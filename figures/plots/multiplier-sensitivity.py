r"""The multiplier is the SLOPE of the value function -- Biegler Example 4.7, pp. 73-74.

    figures/plots/multiplier-sensitivity.py
        ->  media/figures/multiplier-sensitivity.{png,pdf}

The KKT-multipliers handout derives

    lim_{eps -> 0} [ f(x^eps) - f(x*) ] / eps  =  u*_ihat            Biegler p. 73

then checks it on Example 4.7 and its weak-activity variation. The two panels
compare the exact value function with its first-order prediction at eps=0.

  * the multiplier is the slope at zero in both panels;
  * the curve/line gap shows the finite-change error;
  * the left active-set transition is at eps=-1/2. The original tangent at
    zero predicts negative values there, while the true value is zero;
  * both value functions remain C1 at their active-set transitions. Recheck
    the local branch and derivative rather than assuming a kink;
  * in the weak case, loosening costs nothing while tightening costs eps^2.

The two problems (both Biegler's; the handout works both)
---------------------------------------------------------
LEFT, Example 4.7, p. 73.  Perturb the LOWER bound by eps:

    min x^2  s.t.  1/2 + eps <= x <= 1
    x*   = 1/2,  u*_L = 1,  u*_U = 0,  strict complementarity HOLDS
    V(eps) = (1/2 + eps)^2     for -1/2 <= eps <= 1/2   lower bound active
           = 0                 for eps <= -1/2       lower bound goes SLACK
    upper end eps = 1/2: beyond it 1/2 + eps > 1 and the problem is infeasible.

RIGHT, the variation, p. 74.  The lower bound is moved to the origin:

    min x^2  s.t.  eps <= x <= 1
    x*   = 0,    u*_L = 0,  u*_U = 0,  strict complementarity FAILS
    V(eps) = eps^2   for eps >= 0     (tightening: costs O(eps^2))
           = 0       for eps <= 0     (loosening: buys exactly nothing)

VERIFIED (recomputed on every run; see _report(), whose asserts are the check)
-----------------------------------------------------------------------------
Both value functions are evaluated by BRUTE FORCE -- a fine scan of feasible x
for each eps, taking the smallest x^2 -- and compared against the closed forms
above to 1e-9. So the curves drawn are not the algebra retyped; they are an
independent numerical solution that happens to agree with it.

    left  V(0) = 0.250000, V'(0+) = V'(0-) = 1.000000 = u*_L     matches p. 74
    right V(0) = 0.000000, V'(0+) = V'(0-) = 0.000000 = u*_L     matches p. 74
    left  transition at eps = -0.5, where the active set changes; the
          original tangent at eps=0 predicts -0.25 and the truth is 0.
    right at eps = 0.15 the tangent predicts 0 and the truth is 0.0225 = eps^2.

The handout's own arithmetic check, lim (eps + eps^2)/eps = 1, is the left
panel's slope; it is reproduced here as a finite-difference derivative of the
brute-force curve, not assumed.

Colour and greyscale (recoloured 2026-08-21)
-------------------------------------------
Two series per panel, and they are the two the whole figure compares: the TRUTH
and the LINEARIZATION the multiplier predicts. So they get the two hues.

    V(eps), the value function   #0072B2 blue   (L* = 46.0)  solid,  lw 3.2
    tangent, slope u*            #E69F00 orange (L* = 70.6)  dashed, lw 2.2
    (0, V(0))                    open circle, blue edge
    the active-set transition at eps = -1/2       filled black square

dL* = 24.6 between the two, and each additionally keeps its linestyle (solid vs
dashed) and its own weight (3.2 vs 2.2 pt), so the pair survives a photocopier
three separate ways. The tangent is the lighter hue and therefore got 0.6 pt
heavier than it was, so it does not read fainter in print than the grey axis
guides it crosses. The transition marker stays black: it is the one point where the
multiplier's prediction is no longer a reliable finite-change prediction, and black is the strongest ink
available for it. Both panels share axes limits, so the difference in slope
between them is a real visual comparison and not a scale artefact.
"""

import numpy as np
import matplotlib.pyplot as plt

# See "Colour and greyscale" in the docstring above for the L* budget.
VALUE = "#0072B2"     # V(eps), the truth
TANGENT = "#E69F00"   # V(0) + u* eps, the linearization

EPS_LO, EPS_HI = -0.75, 0.42
NX = 400001  # brute-force grid over x


def value(eps, lower0):
    """min x^2 over [lower0 + eps, 1], by brute force. None if infeasible."""
    lo = lower0 + eps
    if lo > 1.0:
        return None
    x = np.linspace(lo, 1.0, NX)
    return float(np.min(x**2))


def curve(lower0, eps):
    return np.array([value(e, lower0) for e in eps], dtype=float)


def _report():
    for name, lower0, mult in (("left  (Ex 4.7)", 0.5, 1.0), ("right (variation)", 0.0, 0.0)):
        v0 = value(0.0, lower0)
        d = 1e-6
        fwd = (value(d, lower0) - v0) / d
        bwd = (v0 - value(-d, lower0)) / d
        print(f"    {name}: V(0) = {v0:.8f}  V'(0+) = {fwd:.6f}  V'(0-) = {bwd:.6f}  u* = {mult}")
        assert abs(fwd - mult) < 5e-6 and abs(bwd - mult) < 5e-6
    # closed forms, checked against the brute-force solutions
    for e in np.linspace(EPS_LO, 0.4, 47):
        exact_l = (0.5 + e) ** 2 if e >= -0.5 else 0.0
        exact_r = e**2 if e >= 0.0 else 0.0
        assert abs(value(e, 0.5) - exact_l) < 1e-9, e
        assert abs(value(e, 0.0) - exact_r) < 1e-9, e
    print(f"    active-set change at eps = -0.5: V = {value(-0.5, 0.5):.6f}, "
          f"tangent predicts {0.25 + 1.0 * (-0.5):.6f}")
    print(f"    weak case at eps = 0.15: V = {value(0.15, 0.0):.6f}, tangent predicts 0.0")


BOX = dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.9)


def _panel(ax, lower0, mult, title, kink=None):
    eps = np.linspace(EPS_LO, EPS_HI, 1201)
    v = curve(lower0, eps)
    v0 = value(0.0, lower0)

    ax.axhline(0.0, color="black", lw=0.9, zorder=0)
    ax.axvline(0.0, color="black", lw=0.9, zorder=0)

    # The tangent the multiplier predicts: V(0) + u* eps.
    ax.plot(eps, v0 + mult * eps, color=TANGENT, lw=2.2, ls="--", zorder=3)
    ax.plot(eps, v, color=VALUE, lw=3.2, ls="-", zorder=4)
    ax.plot([0.0], [v0], "o", ms=11, color=VALUE, mfc="white", mew=2.2, zorder=6)

    if kink is not None:
        ax.plot([kink], [value(kink, lower0)], "s", ms=9, color="black",
                mfc="black", mew=0, zorder=6)

    ax.set_title(title, fontsize=13.5)
    ax.set_xlabel(r"$\epsilon$")
    ax.set_xlim(EPS_LO, EPS_HI)
    ax.set_ylim(-0.30, 0.72)
    return v0


def make_figure():
    _report()
    eps = np.linspace(EPS_LO, EPS_HI, 1201)
    fig, axes = plt.subplots(1, 2, figsize=(8.1, 2.8), sharey=True)
    titles = [r"$\min x^2,\quad \frac{1}{2}+\epsilon\leq x\leq1$",
              r"$\min x^2,\quad \epsilon\leq x\leq1$"]
    for ax, lower0, mult, title in zip(axes, [.5, 0.], [1., 0.], titles):
        v0 = value(0., lower0)
        ax.plot(eps, curve(lower0, eps), color=VALUE, lw=2.2, ls="-",
                label="exact objective value", zorder=3)
        ax.plot(eps, v0+mult*eps, color=TANGENT, lw=1.8, ls="--",
                label="first-order approximation", zorder=4)
        ax.plot(0., v0, "o", color="black", ms=4, zorder=5)
        ax.axhline(0., color="black", lw=.6, zorder=0)
        ax.axvline(0., color="black", lw=.6, zorder=0)
        ax.set(xlim=(EPS_LO,EPS_HI),ylim=(-.30,.72),xlabel=r"$\epsilon$",title=title)
        ax.title.set_fontsize(12)
    axes[0].set_ylabel(r"$f(x^\epsilon)$")
    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc="upper center", bbox_to_anchor=(.5,1.02),
               ncol=2, frameon=False, fontsize=10)
    fig.tight_layout()
    return fig
