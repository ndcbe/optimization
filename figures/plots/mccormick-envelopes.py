"""McCormick envelopes of the bilinear term w = xy on the unit box.

    figures/plots/mccormick-envelopes.py
        -> media/figures/mccormick-envelopes.{png,pdf}

`notebooks/8-dev/Global-Opt.ipynb` cells 14 and 15, carried as ONE two-panel
figure. The two panels answer two different questions and are useless apart:
the left says *where* the relaxation is loose, the right says *how* loose and
in which direction.

The four envelopes, from four sign-definite products such as
(x - x^L)(y - y^L) >= 0:

    lower:  w >= x^L y + x y^L - x^L y^L        w >= x^U y + x y^U - x^U y^U
    upper:  w <= x^U y + x y^L - x^U y^L        w <= x^L y + x y^U - x^L y^U

They are the CONVEX and CONCAVE envelopes of xy on the box -- the tightest
possible linear relaxation -- and they are exact on the whole boundary. The
separation is largest at the box centre, where it equals
(x^U - x^L)(y^U - y^L) / 2; on the unit box that is 0.5, which the left panel
shows and the self-check below asserts. Verified on three boxes, including one
straddling the origin and one with y^U < 0 -- the /2, not /4, is right.

Left panel  -- the gap, upper minus lower, over the box, as LABELLED CONTOUR
LINES rather than the notebook's filled `viridis` ramp with a colorbar.

That is a deliberate departure and it survives the 2026-08-21 relaxation of the
greyscale rule, but for a narrower reason than the one first recorded here. A
sequential colormap is the ONE place figures/README.md still caps the number of
bands, because a filled ramp has no linestyle to fall back on: adjacent bands
of a continuous map land on the same grey once printed (7 levels gives min
dL* = 11.9, 6 gives 14.5, and antialiased blends against the contour lines and
the colorbar land below both). Contour LINES carry the same information, are
each labelled with their own numeric value, and read better at handout size.
The gap is 0 on the whole boundary and rises to a single peak at the box
centre, so the contours are NESTED SQUARES, concentric with the box and
axis-aligned. ⚠ Not diamonds -- that word stood here and in the handout's note
until 2026-08-22, and the figure refutes it. The gap works out to
min(x, y, 1-x, 1-y) on the unit box, i.e. the L-infinity distance to the
boundary, whose level sets are the squares this panel draws. A DIAMOND would be
the level set of the L-1 distance |x - 1/2| + |y - 1/2|, which is not what
either envelope produces.

Right panel -- the same thing along the diagonal x = y = t, where the gap is
widest.

Colour (added 2026-08-21; supersedes the "all three curves are BLACK" note)
--------------------------------------------------------------------------
⚠ This file used to argue that a coloured curve here would collide in greyscale
and that the whole figure therefore had to be monochrome. That argument was a
consequence of the OLD `check_greyscale.py`, which failed any two colours
within dL* = 10 whether or not anything else told them apart. Prof. Dowling
called that rule "way too strict" and it was rewritten; the constraint is gone.
There is also no viridis left anywhere in this figure to collide with.

    w = xy            black    (L* =  0.0)  solid,    lw 2.4  -- the truth
    upper envelope    #0072B2  (L* = 46.0)  dash-dot, lw 2.2
    lower envelope    #E69F00  (L* = 70.6)  dashed,   lw 2.6
    centre peak       #0072B2  (L* = 46.0)  marker, black-edged (left panel)

Pairwise dL*: black-blue 46.0, blue-orange 24.6, black-orange 70.6 -- all clear
20. Every curve additionally keeps its own linestyle AND its direct label, so
the two envelopes are told apart three independent ways. The lower envelope is
the lighter hue and so gets the heavier stroke, which is what keeps it from
reading fainter than the grey relaxation band underneath it in print.

No solver: every quantity here is a closed-form max or min of affine functions.
"""

import numpy as np
import matplotlib.pyplot as plt

from _house import HATCH_CYCLE, SHADE_ALPHA

XL, XU, YL, YU = 0.0, 1.0, 0.0, 1.0

# See "Colour" in the docstring above for the L* budget.
TRUE = "black"       # w = xy
UPPER = "#0072B2"    # upper (concave) envelope
LOWER = "#E69F00"    # lower (convex) envelope


def mccormick_envelopes(X, Y, xl=XL, xu=XU, yl=YL, yu=YU):
    """Lower and upper McCormick envelopes of w = x*y, evaluated on a mesh."""
    lower = np.maximum(xl * Y + X * yl - xl * yl, xu * Y + X * yu - xu * yu)
    upper = np.minimum(xu * Y + X * yl - xu * yl, xl * Y + X * yu - xl * yu)
    return lower, upper


def make_figure():
    fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(9.4, 4.0))

    # ------------------------------------------------- panel 1: the gap surface
    g = np.linspace(XL, XU, 161)
    X, Y = np.meshgrid(g, g)
    lo, hi = mccormick_envelopes(X, Y)
    gap = hi - lo

    levels = [0.05, 0.15, 0.25, 0.35, 0.45]
    cs = ax0.contour(X, Y, gap, levels=levels, colors="black", linewidths=1.3)
    ax0.clabel(cs, inline=True, fontsize=10, fmt="%.2f")
    ax0.plot([XL, XU, XU, XL, XL], [YL, YL, YU, YU, YL],
             color="black", lw=1.8, ls="-")
    ax0.plot(0.5, 0.5, marker="o", mfc=UPPER, mec="black", mew=1.2, ms=10,
             ls="none")
    # Both notes sit OUTSIDE the unit box: inside, they landed on the inline
    # contour labels, which is the one thing clabel cannot route around.
    #
    # ⚠ THEY MUST ALSO FIT THE AXES BOX, and until 2026-08-22 they did not.
    # `set_aspect(1)` makes this panel's WIDTH a consequence of its height and
    # of the y-range, so padding the y-limits to make room above and below the
    # unit box is what squeezed the box to 188 px while the two notes rendered
    # at 244 px and 352 px -- 1.3x and 1.9x the width of the panel they label,
    # spilling across both spines (the upper note had the left spine drawn
    # through the word "gap"). Fixed by shortening the first note, breaking the
    # second over two lines, dropping to 10 pt, and trimming the y-padding,
    # which widens the box to 216 px. Measured after the change: 176 px and
    # 171 px, i.e. 20 px and 23 px of clearance on each side.
    # If you edit either string, re-measure -- nothing in the build catches it.
    ax0.annotate("gap $=0$ on the boundary", xy=(0.5, 1.09),
                 fontsize=10, ha="center", va="bottom")
    ax0.annotate("widest at the centre:\n$(x^U-x^L)(y^U-y^L)/2 = 0.5$",
                 xy=(0.5, -0.065), fontsize=10, ha="center", va="top",
                 linespacing=1.35, color=UPPER)
    ax0.set_xlabel("$x$")
    ax0.set_ylabel("$y$")
    ax0.set_title("envelope gap, upper $-$ lower", fontsize=13)
    ax0.set_aspect(1)
    ax0.set_xlim(-0.06, 1.06)
    ax0.set_ylim(-0.26, 1.20)
    # Ticks named explicitly: the y-padding that makes room for the notes is
    # outside the box and the auto-locator would put a tick at -0.25 in it,
    # which is not a coordinate of anything.
    ax0.set_xticks([0.0, 0.5, 1.0])
    ax0.set_yticks([0.0, 0.5, 1.0])

    # ------------------------------------------- panel 2: the diagonal section
    t = np.linspace(XL, XU, 401)
    lo_t, hi_t = mccormick_envelopes(t, t)

    # The relaxation gap. Hatched as well as tinted, per figures/README.md.
    #
    # HATCH_CYCLE[2] ("...", dots), and the reason is NOT the one that used to
    # be recorded here. That reason was a matplotlib 3.5.1 rendering defect in
    # which every backslash hatch came out at the forward-slash slope, so [0]
    # and [1] were "one texture, not two". It does not reproduce under the
    # matplotlib 3.11.1 in optimization_fall2026, where [0] ("///", +45 deg)
    # and [1] ("\\\", -45 deg) are by the hatch spec the most SEPARATED line
    # pair the cycle offers. Do not reintroduce that workaround.
    #
    # Dots are kept for a reason of this figure's own, checked by rendering
    # both: this is the ONLY hatched region in the figure, so nothing has to be
    # separated from it and the index is free -- but three curves run THROUGH
    # the region (solid, dashed, dash-dot). A line hatch competes with them;
    # rendered with [1], the fill reads as a fourth set of strokes crossing the
    # envelopes, worst near the right-hand tip where the region narrows. Dots
    # stay in the background, which is what a shaded region is (_house.py).
    ax1.fill_between(t, lo_t, hi_t, facecolor="0.6", alpha=SHADE_ALPHA,
                     hatch=HATCH_CYCLE[2], edgecolor=plt.rcParams["hatch.color"],
                     linewidth=0.0, zorder=0)

    ax1.plot(t, t * t, color=TRUE, ls="-", lw=2.4, zorder=4)
    ax1.plot(t, hi_t, color=UPPER, ls="-.", lw=2.2, zorder=3)
    ax1.plot(t, lo_t, color=LOWER, ls="--", lw=2.6, zorder=3)

    ax1.annotate("$w = xy$", xy=(0.80, 0.50), fontsize=13, color=TRUE)
    ax1.annotate("upper envelope", xy=(0.05, 0.44), fontsize=12, color=UPPER)
    ax1.annotate("lower envelope", xy=(0.50, 0.03), fontsize=12)
    ax1.set_xlabel("$x = y = t$")
    ax1.set_ylabel("$w$")
    ax1.set_xlim(0, 1)
    ax1.set_ylim(-0.03, 1.02)

    fig.tight_layout()
    return fig


if __name__ == "__main__":                                    # a self-check
    g = np.linspace(XL, XU, 401)
    X, Y = np.meshgrid(g, g)
    W = X * Y
    lo, hi = mccormick_envelopes(X, Y)
    print(f"lower envelope violated by at most {np.max(lo - W):.2e}  (<= 0)")
    print(f"upper envelope violated by at most {np.max(W - hi):.2e}  (<= 0)")
    print(f"max separation      = {np.max(hi - lo):.6f}")
    print(f"(xU-xL)(yU-yL)/2    = {0.5 * (XU - XL) * (YU - YL):.6f}")
    # exact on the boundary
    edge = np.isclose(X, XL) | np.isclose(X, XU) | np.isclose(Y, YL) | np.isclose(Y, YU)
    print(f"max gap on the box boundary = {np.max((hi - lo)[edge]):.2e}  (must be 0)")
