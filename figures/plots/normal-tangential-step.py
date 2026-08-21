r"""Normal and tangential components of one Newton step -- Biegler Figure 5.1, p. 100.

    figures/plots/normal-tangential-step.py
        ->  media/figures/normal-tangential-step.{png,pdf}

The equality-constrained-Newton handout states the reduced-space decomposition

    d_x = Y^k p_Y + Z^k p_Z                                   Biegler (5.15), p. 99

in words -- "decompose the step into normal and tangential components" -- and
never draws it. Biegler does draw it (Figure 5.1, printed p. 100), and his
caption carries a second claim the prose in our handout drops entirely:

    "Note also that if a coordinate basis (Y^c) is chosen, the normal and
     tangential steps may not be orthogonal and the steps Y^c p_Yc are longer
     than Y p_Y."

That length comparison is the reason the book bothers to list THREE choices of
basis ((5.23) coordinate, (5.26) orthogonal, and the QR option on p. 101), so
it is drawn here to scale and MEASURED rather than asserted -- see VERIFIED
below.

The example
-----------
Everything is recomputed from these five lines; no coordinate in this file was
placed by hand.

    min  f(x) = 1/2 (x - c)^T Q (x - c),   c = (0.95, 0.62), Q = diag(2, 1.2)
    s.t. h(x) = x1^2 + x2^2 - 1 = 0                       (the unit circle)
    x^k = (0.70, 1.07)                                    (infeasible, outside)

so h(x^k) = 0.6349 and J_h(x^k) = grad h(x^k)^T = [1.40, 2.14].

    Y   = A/||A||,  Z = the unit vector orthogonal to it   (the QR option, p. 101)
    p_Y = -[J_h Y]^{-1} h(x^k)                             (5.17), p. 100
    p_Z from  Z^T W Z p_Z = -[Z^T grad f + Z^T W Y p_Y]    (5.19), p. 100
    W   = grad^2 f + v grad^2 h  with v from               (5.21), p. 101

The multiplier estimate is the FIRST ORDER one, (5.21), not (5.20): the handout
never introduces (5.20), and Biegler notes the two are asymptotically the same.
Z^T W Z = 1.621 > 0, so (5.19) is solvable without the delta_R modification the
book mentions on the same page -- i.e. this iterate needs no correction and the
picture shows the clean case.

VERIFIED (recomputed by this script every time it runs; see _report())
---------------------------------------------------------------------
  |Y p_Y|    = 0.2482       orthogonal normal step
  |Y^c p_Yc| = 0.4535       coordinate normal step, x1 basic  -- 1.83x LONGER
  |Z p_Z|    = 0.4970       tangential step
  ratio      = ||A|| / |A_1| = 2.5573 / 1.40 = 1.8266, exactly, because with
               Y^c = [1, 0]^T (5.24) gives p_Yc = -h/A_1 while p_Y = -h/||A||.

So Biegler's "longer" is not a generic caution: it is sec(angle between grad h
and the basic coordinate axis), and it blows up as the basis choice becomes
ill-conditioned. Drawn on EQUAL ASPECT axes, so a reader can measure the two
arrows on the page and get 1.83; a figure that asserted this while stretching
one axis would be lying.

Both normal steps land ON the linearized constraint, which is the whole point:
J_h (Y p_Y) = J_h (Y^c p_Yc) = -h(x^k) = -0.6349, checked to 1e-12 below. The
tangential step then slides ALONG that line (J_h Z = 0), so x^k + d_x is on the
linearization and NOT on h(x) = 0 -- visible in the figure, and the reason a
Newton step has to be repeated.

Colour and greyscale (recoloured 2026-08-21)
-------------------------------------------
Colour is spent on exactly one thing: the COMPARISON the figure exists to make,
Biegler's "the steps Y^c p_Yc are longer than Y p_Y". Those two arrows are the
only coloured marks in the picture.

    Y p_Y      orthogonal normal step    #0072B2 blue   (L* = 46.0)
    Y^c p_Yc   coordinate normal step    #E69F00 orange (L* = 70.6)
    Z p_Z, d_x, h(x) = 0, linearization  black
    f-contours                           grey 0.80, context only

dL* = 24.6 between the pair, which is the only pair a reader is asked to
compare, and each arrow keeps everything it had before: a different STARTING
POINT, a different DIRECTION, a different marker shape at its tip (square vs
diamond, now filled in the arrow's own hue) and an in-place label carrying its
symbol -- per figures/README.md, "an arrow gets no linestyle from the colour
cycle". Nothing else is coloured, so nothing else can collide: the constraint
and its linearization stay black and keep being told apart by linestyle, and
the contours stay thin grey with nothing claimed about which is which.
"""

import numpy as np
import matplotlib.pyplot as plt

# See "Colour and greyscale" in the docstring above for the L* budget.
NORMAL = "#0072B2"    # Y p_Y, the orthogonal normal step
NORMAL_C = "#E69F00"  # Y^c p_Yc, the coordinate normal step -- 1.83x longer

# --- the example ----------------------------------------------------------
XK = np.array([0.70, 1.07])
CVEC = np.array([0.95, 0.62])
QMAT = np.diag([2.0, 1.2])


def _f(x1, x2):
    d1, d2 = x1 - CVEC[0], x2 - CVEC[1]
    return 0.5 * (QMAT[0, 0] * d1**2 + QMAT[1, 1] * d2**2)


def solve():
    """Recompute every vector in the figure from the model above."""
    xk = XK
    hk = xk @ xk - 1.0  # h(x^k)
    a = 2.0 * xk  # grad h(x^k), the n x m matrix A^k (m = 1)
    jh = a.reshape(1, 2)  # J_h = (A^k)^T, m x n
    gf = QMAT @ (xk - CVEC)  # grad f(x^k)

    # Orthonormal bases: Y spans range(A), Z spans null(J_h).   Biegler p. 101
    Y = a / np.linalg.norm(a)
    Z = np.array([-Y[1], Y[0]])

    p_y = -hk / (jh @ Y)[0]  # (5.17)
    normal = Y * p_y

    # Coordinate basis Y^c = [I; 0], i.e. x1 basic.             (5.23)/(5.24)
    p_yc = -hk / a[0]
    normal_c = np.array([p_yc, 0.0])

    v = -(Y @ gf) / (jh @ Y)[0]  # (5.21)
    W = QMAT + v * 2.0 * np.eye(2)  # grad^2 f + v grad^2 h
    ztwz = Z @ W @ Z
    p_z = -(Z @ gf + Z @ (W @ normal)) / ztwz  # (5.19)
    tangential = Z * p_z

    return dict(
        xk=xk, hk=hk, a=a, jh=jh, Y=Y, Z=Z, v=v, W=W, ztwz=ztwz,
        normal=normal, normal_c=normal_c, tangential=tangential,
        dx=normal + tangential,
    )


def _report(s):
    """Printed by `make`; this is the audit trail for the length claim."""
    ln, lc, lt = (np.linalg.norm(s[k]) for k in ("normal", "normal_c", "tangential"))
    print(f"    h(x^k) = {s['hk']:.6f}   J_h = {s['jh'][0]}   Z^T W Z = {s['ztwz']:.4f}")
    print(f"    |Y p_Y| = {ln:.4f}   |Y^c p_Yc| = {lc:.4f}   ratio = {lc/ln:.4f}")
    print(f"    ||A||/|A_1| = {np.linalg.norm(s['a'])/s['a'][0]:.4f}   |Z p_Z| = {lt:.4f}")
    for name in ("normal", "normal_c", "dx"):
        resid = float(s["jh"] @ s[name]) + s["hk"]
        assert abs(resid) < 1e-12, (name, resid)
    assert abs(s["jh"] @ s["tangential"]) < 1e-12
    assert s["ztwz"] > 0


BOX = dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.9)


def _arrow(ax, base, vec, *, lw=2.2, color="black"):
    ax.annotate(
        "",
        xy=tuple(np.asarray(base) + np.asarray(vec)),
        xytext=tuple(base),
        arrowprops=dict(arrowstyle="-|>,head_width=0.20,head_length=0.42",
                        lw=lw, color=color, shrinkA=0, shrinkB=0),
        zorder=6,
    )


def _text(ax, xy, label, *, ha="left", va="bottom", size=14, rot=0.0, box=True,
          color="black"):
    ax.annotate(label, xy=xy, ha=ha, va=va, fontsize=size, rotation=rot,
                color=color, zorder=9, bbox=BOX if box else None)


def make_figure():
    s = solve()
    _report(s)
    xk, Z = s["xk"], s["Z"]
    n_end = xk + s["normal"]
    c_end = xk + s["normal_c"]
    d_end = xk + s["dx"]

    fig, ax = plt.subplots(figsize=(6.6, 4.6))

    # f contours: context, thin and grey, no colour meaning.
    g1, g2 = np.meshgrid(np.linspace(0.0, 1.6, 400), np.linspace(0.20, 1.45, 400))
    ax.contour(g1, g2, _f(g1, g2), levels=6, colors="0.80", linewidths=0.8, zorder=0)

    # h(x) = 0, the unit circle.
    th = np.linspace(0.0, np.pi / 2, 400)
    ax.plot(np.cos(th), np.sin(th), color="black", lw=2.6, ls="-", zorder=3)

    # Its linearization at x^k: J_h (x - x^k) = -h(x^k). Drawn from the two
    # normal-step endpoints, both of which lie on it by construction.
    t = np.linspace(-0.87, 0.85, 2)
    line = n_end[None, :] + t[:, None] * Z[None, :]
    ax.plot(line[:, 0], line[:, 1], color="black", lw=1.8, ls="--", zorder=3)

    # Each marker keeps its SHAPE and picks up the hue of the arrow that ends
    # there, so the endpoint and its step read as one object in either mode.
    # Written out rather than looped on purpose: check_greyscale.py --source
    # reads the AST and cannot see a colour chosen through a loop variable, so a
    # loop here made the file report as monochrome when it is not.
    ax.plot(*xk, "o", color="black", mfc="black", ms=9, mew=1.6, zorder=8)
    ax.plot(*n_end, "s", color="black", mfc=NORMAL, ms=9, mew=1.6, zorder=8)
    ax.plot(*c_end, "D", color="black", mfc=NORMAL_C, ms=9, mew=1.6, zorder=8)
    ax.plot(*d_end, "*", color="black", mfc="black", ms=15, mew=1.6, zorder=8)

    _arrow(ax, xk, s["normal"], lw=2.6, color=NORMAL)
    _arrow(ax, xk, s["normal_c"], lw=3.0, color=NORMAL_C)
    _arrow(ax, n_end, s["tangential"])
    _arrow(ax, xk, s["dx"], lw=1.3)

    # Every label is placed in absolute data coordinates, checked against the
    # rendered PNG. The two curves are named ALONG themselves at the angle they
    # run, so no leader line has to cross the picture.
    # Both labels stay BLACK. The comparison is symmetric, and orange text at
    # L* = 70.6 is not readable at 15 pt on white -- colouring only one of the
    # pair would make the figure look like it was claiming something about it.
    _text(ax, (0.648, 0.985), r"$Y p_Y$", size=15)
    _text(ax, (0.470, 1.093), r"$Y^{c} p_{Y^c}$", ha="center", size=15)
    _text(ax, (0.775, 0.780), r"$Z p_Z$", size=15)
    _text(ax, (0.885, 0.885), r"$d_x$", size=15)
    _text(ax, tuple(xk + np.array([0.030, 0.026])), r"$x^k$", size=15, box=False)
    _text(ax, (0.995, 0.660), r"$x^k + d_x$", size=13, box=False)
    _text(ax, (0.155, 0.905), r"$h(x)=0$", va="top", size=14, rot=-13.0)
    ax.annotate(
        "linearized constraint\n" r"$h(x^k) + J_h(x^k)(x - x^k) = 0$",
        xy=(1.152, 0.449), xytext=(1.045, 1.16), fontsize=12, ha="left", va="center",
        arrowprops=dict(arrowstyle="-", lw=0.9, color="black"), zorder=9,
        bbox=dict(boxstyle="round,pad=0.16", fc="white", ec="0.55", lw=0.8),
    )

    ax.set_aspect("equal")
    ax.set_xlim(0.10, 1.60)
    ax.set_ylim(0.32, 1.36)
    ax.set_xlabel(r"$x_1$")
    ax.set_ylabel(r"$x_2$")
    fig.tight_layout()
    return fig
