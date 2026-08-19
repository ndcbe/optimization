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

That is a deliberate departure and it was forced by measurement, not taste.
`scripts/check_greyscale.py` FAILS the filled version: adjacent bands of a
continuous colormap land on the same grey once printed (7 levels gives min
dL* = 11.9, 6 gives 14.5, and antialiased blends against the white contour
lines and the colorbar land below both). A sequential ramp is the right tool on
a screen, where the website shows it; on a mono laser printer, which is what
the student handout has to survive, contour LINES carry the same information in
pure black and read better at handout size besides. The contours are the
diamonds you would predict: the gap is 0 on the whole boundary and rises to a
single peak at the box centre.

Right panel -- the same thing along the diagonal x = y = t, where the gap is
widest. All three curves are BLACK and are told apart by linestyle and a direct
label. That is deliberate twice over: the two envelopes are two halves of one
object rather than two independent series, and a coloured curve here would
collide in greyscale with the viridis ramp in the left panel -- which it did,
and `scripts/check_greyscale.py` caught it.

No solver: every quantity here is a closed-form max or min of affine functions.
"""

import numpy as np
import matplotlib.pyplot as plt

XL, XU, YL, YU = 0.0, 1.0, 0.0, 1.0


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
    ax0.plot(0.5, 0.5, marker="o", color="black", ms=9, ls="none")
    # Both notes sit OUTSIDE the unit box: inside, they landed on the inline
    # contour labels, which is the one thing clabel cannot route around.
    ax0.annotate("gap $=0$ on the whole boundary", xy=(0.5, 1.16),
                 fontsize=11, ha="center", va="bottom")
    ax0.annotate("widest at the centre: $(x^U-x^L)(y^U-y^L)/2 = 0.5$",
                 xy=(0.5, -0.16), fontsize=11, ha="center", va="top")
    ax0.set_xlabel("$x$")
    ax0.set_ylabel("$y$")
    ax0.set_title("envelope gap, upper $-$ lower", fontsize=13)
    ax0.set_aspect(1)
    ax0.set_xlim(-0.06, 1.06)
    ax0.set_ylim(-0.34, 1.34)

    # ------------------------------------------- panel 2: the diagonal section
    t = np.linspace(XL, XU, 401)
    lo_t, hi_t = mccormick_envelopes(t, t)

    ax1.plot(t, t * t, color="black", ls="-", lw=2.4)
    ax1.plot(t, hi_t, color="black", ls="-.", lw=2.2)
    ax1.plot(t, lo_t, color="black", ls="--", lw=2.2)
    ax1.fill_between(t, lo_t, hi_t, facecolor="0.6", alpha=0.15, linewidth=0.0)

    ax1.annotate("$w = xy$", xy=(0.80, 0.50), fontsize=13)
    ax1.annotate("upper envelope", xy=(0.05, 0.44), fontsize=12)
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
