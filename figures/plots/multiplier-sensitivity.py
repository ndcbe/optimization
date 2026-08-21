r"""The multiplier is the SLOPE of the value function -- Biegler Example 4.7, pp. 73-74.

    figures/plots/multiplier-sensitivity.py
        ->  media/figures/multiplier-sensitivity.{png,pdf}

The KKT-multipliers handout derives

    lim_{eps -> 0} [ f(x^eps) - f(x*) ] / eps  =  u*_ihat            Biegler p. 73

then checks it twice by hand -- once on Example 4.7, once on the weak-activity
variation -- and then lists two limitations in a box: "only a linearization"
and "loses meaning when the active set changes". Three separate algebraic
verifications, no picture, and the two limitations are asserted rather than
shown.

All five statements are the SAME picture: the optimal value as a function of
the perturbation, and a straight line of slope u* through it.

  * the multiplier IS the slope at eps = 0, in both panels;
  * "only a linearization" is the gap between the curve and the line;
  * "loses meaning when the active set changes" is the kink at eps = -1/2 in
    the left panel, past which the tangent predicts a NEGATIVE objective while
    the truth is flat at zero;
  * and the asymmetry the handout points out in the weak case -- "the one-sided
    behaviour is invisible to a single number" -- is the right panel, where one
    side of the tangent is exact and the other is not.

The two problems (both Biegler's; the handout works both)
---------------------------------------------------------
LEFT, Example 4.7, p. 73.  Perturb the LOWER bound by eps:

    min x^2  s.t.  1/2 + eps <= x <= 1
    x*   = 1/2,  u*_L = 1,  u*_U = 0,  strict complementarity HOLDS
    V(eps) = (1/2 + eps)^2     for eps >= -1/2       lower bound active
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
    left  kink at eps = -0.5, where the active set changes; the tangent there
          predicts -0.25 and the truth is 0.
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
    the kink at eps = -1/2       filled black square

dL* = 24.6 between the two, and each additionally keeps its linestyle (solid vs
dashed) and its own weight (3.2 vs 2.2 pt), so the pair survives a photocopier
three separate ways. The tangent is the lighter hue and therefore got 0.6 pt
heavier than it was, so it does not read fainter in print than the grey axis
guides it crosses. The kink marker stays black: it is the one point where the
multiplier's prediction stops meaning anything, and black is the strongest ink
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

    ax.axhline(0.0, color="0.7", lw=0.9, zorder=0)
    ax.axvline(0.0, color="0.7", lw=0.9, zorder=0)

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
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 4.3), sharey=True)

    # ---- left: Example 4.7, strongly active lower bound, u*_L = 1 ----------
    ax = axes[0]
    _panel(ax, 0.5, 1.0, r"$\min\ x^2$   s.t.   $\frac{1}{2} + \epsilon \leq x \leq 1$", kink=-0.5)
    ax.set_ylabel(r"$f(x^{\epsilon})$")
    ax.annotate(r"slope $= u^*_L = 1$", xy=(0.285, 0.535), xytext=(-0.245, 0.635),
                fontsize=13, ha="left", va="center", zorder=8, bbox=BOX,
                arrowprops=dict(arrowstyle="-", lw=0.9, color="black"))
    ax.annotate("active set changes here:\nthe lower bound goes slack,\n"
                "and the tangent goes negative",
                xy=(-0.5, 0.0), xytext=(-0.72, 0.44), fontsize=11.5, ha="left",
                va="center", zorder=8,
                bbox=dict(boxstyle="round,pad=0.14", fc="white", ec="0.55", lw=0.8),
                arrowprops=dict(arrowstyle="-", lw=0.9, color="black"))
    ax.annotate(r"$f(x^*) = \frac{1}{4}$", xy=(0.035, 0.215), fontsize=12.5, ha="left",
                va="top", zorder=8, bbox=BOX)
    ax.annotate("strongly active:\n$u^*_L > 0$", xy=(-0.70, -0.215), fontsize=12.5,
                ha="left", va="center", zorder=8, bbox=BOX)

    # ---- right: the variation, weakly active lower bound, u*_L = 0 ---------
    ax = axes[1]
    _panel(ax, 0.0, 0.0, r"$\min\ x^2$   s.t.   $\epsilon \leq x \leq 1$")
    ax.annotate(r"tangent, slope $= u^*_L = 0$", xy=(0.32, 0.0), xytext=(-0.30, -0.13),
                fontsize=12.5, ha="left", va="center", zorder=8, bbox=BOX,
                arrowprops=dict(arrowstyle="-", lw=0.9, color="black"))
    ax.annotate("tighten: costs $\\epsilon^2$,\nnot $0\\cdot\\epsilon$",
                xy=(0.30, 0.095), xytext=(-0.12, 0.47), fontsize=12, ha="left",
                va="center", zorder=8, bbox=BOX,
                arrowprops=dict(arrowstyle="-", lw=0.9, color="black"))
    ax.annotate("loosen: the tangent\nis exact", xy=(-0.35, 0.0), xytext=(-0.72, 0.32),
                fontsize=12, ha="left", va="center", zorder=8, bbox=BOX,
                arrowprops=dict(arrowstyle="-", lw=0.9, color="black"))
    ax.annotate("weakly active:\n$u^*_L = 0$", xy=(-0.70, -0.215), fontsize=12.5,
                ha="left", va="center", zorder=8, bbox=BOX)

    fig.tight_layout()
    return fig
