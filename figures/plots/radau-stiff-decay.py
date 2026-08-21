r"""Stiff decay: why Radau, not Gauss-Legendre, for a stiff model -- Biegler p. 293.

    figures/plots/radau-stiff-decay.py
        ->  media/figures/radau-stiff-decay.{png,pdf}

The collocation handout asks, in an activity: "Your reactor model is stiff.
Which collocation family do you reach for, and why?" The answer it gives is

    "Radau because it has stiff decay: the fast modes are damped out rather
     than merely kept stable, so a large h_i still produces a sensible answer
     on the slow time scale. Gauss-Legendre is A-stable and one order more
     accurate, but without stiff decay a large step leaves the fast transient
     oscillating in the solution."

Every word of that is a claim about a picture, and the handout has none. Both
families are A-stable, so a stability-region plot -- which the course already
has, in numeric-integration -- cannot tell them apart. What separates them is
the behaviour of the stability function R at the FAR end of the left half
plane, and its consequence for a trajectory. Both are drawn here.

The tableau is DERIVED, not looked up
-------------------------------------
The handout's own equation for collocation-as-implicit-Runge-Kutta,

    n_s = K,  c_k = tau_k,  a_kj = Omega_j(tau_k),  b_k = Omega_k(1)   p. 293

is used literally: Omega_j(tau) = int_0^tau lbar_j, with lbar_j the Lagrange
basis polynomial on the nodes tau. So this script starts from the collocation
POINTS the handout prints and produces the Butcher tableau by integration, and
the figure cannot disagree with the equations on the page.

    Gauss-Legendre K = 3: tau = 1/2 -+ sqrt(15)/10, 1/2  (0.112702, 0.5, 0.887298)
    Radau IIA     K = 3: tau = 0.155051, 0.644949, 1     <- the handout's own
                                                            numbers, from
                                                            Biegler Table 10.1, p. 292

VERIFIED against published tableaux (asserted in _report(), every run)
---------------------------------------------------------------------
  Gauss-Legendre K=3 weights b = (5/18, 4/9, 5/18) = (0.277778, 0.444444, 0.277778)
  Radau IIA     K=3 weights b = ((16-sqrt(6))/36, (16+sqrt(6))/36, 1/9)
                              = (0.376403, 0.512486, 0.111111)
  Radau's LAST ROW of A equals b -- the stiffly accurate property, which is
  exactly what tau_K = 1 buys and is why R_Radau(-inf) = 0.
  Both satisfy sum(b) = 1 (consistency) and match exp(z) closely for small |z|:
  R(-1) = 0.367876 (Gauss) and 0.367925 (Radau) against e^-1 = 0.367879.

  R(z) = 1 + z b^T (I - zA)^{-1} 1        the standard IRK stability function
  R_Gauss(-10^4) = -0.997603  ->  |R| -> 1: the fast mode is NOT damped, and
                                  the sign flip is the ringing.
  R_Radau(-10^4) = +0.000299  ->  R -> 0: stiff decay.
  |R| <= 1 on the whole negative real axis for both: both ARE A-stable, which
  is the point -- A-stability is not the property that distinguishes them.

The trajectory (right panel)
----------------------------
    y' = -lambda (y - cos t) - sin t,   y(0) = 2,   lambda = 1000
    exact:  y(t) = cos t + e^{-lambda t}

A slow mode (cos t) plus a fast transient that is gone by t = 0.01. Step
h = 0.25, so h*lambda = 250: the fast mode is unresolved by design, which is
what "stiff" means and what collocation's A-stability is supposed to survive.

  Radau: 0.9801, 0.8777, 0.7317, 0.5403, ...  vs exact 0.9689, 0.8776, 0.7317,
         0.5403, ...  -- on the slow solution from the second step onward,
         agreeing to four decimals.
  Gauss: 0.0604, 1.7029, -0.0181, 1.2214, -0.3035, ...  -- the transient is
         still there, alternating in sign, decaying only as |R(-250)|^n.

Neither method is unstable. That is the pedagogical trap this figure exists to
spring: a student who has only seen stability regions expects A-stable to mean
"fine at large h", and the left curve shows precisely which A-stable methods
are not.

Caveat kept honest: Biegler's blanket "collocation methods are A-stable"
(p. 293) is over-general -- the one-stage c_1 = 0 collocation method is forward
Euler -- and the handout's \rewrite{} block already flags it. Nothing here
depends on the general claim; both families drawn are A-stable, checked.

Colour and greyscale (recoloured 2026-08-21)
-------------------------------------------
    Radau IIA        #0072B2 blue   (L* = 46.0)  solid,  lw 2.6, filled circles
    Gauss-Legendre   #E69F00 orange (L* = 70.6)  dashed, lw 2.6, open squares
    exact solution   black          (L* =  0.0)  dotted, lw 1.3, no marker
    |R| = 1 guide    grey 0.75                   dotted, lw 1.0

Pairwise dL*: blue-orange 24.6, black-blue 46.0, black-orange 70.6 -- all clear
20. Colour is the third channel, never the first: all three linestyles differ
(solid / dashed / dotted), all three markers differ (filled circle / open square
/ none), and every curve is DIRECTLY LABELLED in place rather than by legend.

TWO OVERPLOTTING DEFECTS were fixed here at the same time, and both were hidden
by the old all-black palette rather than caused by it.

1. The exact solution was a thin grey SOLID line drawn UNDERNEATH Radau, which
   agrees with it to 1.3e-4 from the second step onward. It was therefore
   completely invisible, and the "exact:" leader line pointed at the Radau
   curve. It is now black, DOTTED and drawn ON TOP, so the reader sees a dotted
   reference running along the Radau curve -- which is the panel's whole claim
   made visible -- and sees the two separate at the first step, where they do.
2. In the left panel both stability functions match exp(z) for small |z| and so
   coincide below -h*lambda ~ 3. Gauss was drawn under Radau and vanished there.
   The DASHED curve is now on top, so the solid one shows through its gaps and
   the coincidence reads as coincidence instead of as a missing curve.

The |R| = 1 guide was lightened from 0.6 to 0.75 so it stays subordinate to the
curve that asymptotes onto it. Note honestly that this does NOT buy luminance
separation from the orange Gauss curve -- 0.75 is L* ~ 75.6 against orange's
70.6, and 0.6 was L* ~ 62 -- and `check_greyscale.py media/figures` reports that
5-point gap as a warning. It is the right call anyway, because the guide is not
a series: it is 1.0 pt, DOTTED and exactly horizontal, against a 2.8 pt DASHED
curve, so the reader can never mistake one for the other. Image mode cannot see
a linestyle and says so; source mode, which can, passes the figure.
"""

import numpy as np
import matplotlib.pyplot as plt
from numpy.polynomial import polynomial as P

# See "Colour and greyscale" in the docstring above for the L* budget.
RADAU = "#0072B2"
GAUSS = "#E69F00"
EXACT = "black"

TAU_GL = np.array([0.5 - np.sqrt(15) / 10, 0.5, 0.5 + np.sqrt(15) / 10])
TAU_RA = np.array([0.15505102572168219, 0.64494897427831781, 1.0])

LAM = 1000.0
H = 0.25
NSTEP = 16


def tableau(tau):
    """a_kj = Omega_j(tau_k), b_k = Omega_k(1), with Omega_j = int_0^tau lbar_j."""
    K = len(tau)
    A = np.zeros((K, K))
    b = np.zeros(K)
    for j in range(K):
        coef = np.array([1.0])
        for m in range(K):
            if m != j:
                coef = P.polymul(coef, [-tau[m], 1.0]) / (tau[j] - tau[m])
        om = P.polyint(coef)
        for k in range(K):
            A[k, j] = P.polyval(tau[k], om)
        b[j] = P.polyval(1.0, om)
    return A, b


def stability(tau, z):
    A, b = tableau(tau)
    K = len(tau)
    one = np.ones(K)
    return np.array([1.0 + zz * b @ np.linalg.solve(np.eye(K) - zz * A, one) for zz in np.atleast_1d(z)])


def integrate(tau):
    """y' = -LAM (y - cos t) - sin t, y(0) = 2. Linear in y, so solve directly."""
    A, b = tableau(tau)
    K = len(tau)
    y = 2.0
    ts, ys = [0.0], [y]
    M = np.eye(K) + H * LAM * A
    for n in range(NSTEP):
        tn = n * H
        tc = tn + H * tau
        q = LAM * np.cos(tc) - np.sin(tc)  # the non-y part of f
        Y = np.linalg.solve(M, y * np.ones(K) + H * (A @ q))
        y = y + H * b @ (-LAM * Y + q)
        ts.append(tn + H)
        ys.append(y)
    return np.array(ts), np.array(ys)


def _report():
    Ag, bg = tableau(TAU_GL)
    Ar, br = tableau(TAU_RA)
    print(f"    Gauss b = {np.round(bg, 6)}  (published 5/18, 4/9, 5/18)")
    print(f"    Radau b = {np.round(br, 6)}  (published (16-+sqrt6)/36, 1/9)")
    assert np.allclose(bg, [5 / 18, 4 / 9, 5 / 18], atol=1e-12)
    assert np.allclose(br, [(16 - np.sqrt(6)) / 36, (16 + np.sqrt(6)) / 36, 1 / 9], atol=1e-12)
    assert np.allclose(Ar[-1], br, atol=1e-12), "Radau IIA must be stiffly accurate"
    assert abs(bg.sum() - 1) < 1e-12 and abs(br.sum() - 1) < 1e-12
    for tau, name in ((TAU_GL, "Gauss"), (TAU_RA, "Radau")):
        r1 = stability(tau, -1.0)[0]
        rinf = stability(tau, -1e4)[0]
        big = stability(tau, -np.logspace(-2, 6, 400))
        print(f"    {name}: R(-1) = {r1:.6f} (e^-1 = 0.367879)   R(-1e4) = {rinf:+.6f}"
              f"   max|R| on (-inf,0) = {np.abs(big).max():.6f}")
        assert abs(r1 - np.exp(-1.0)) < 2e-4
        assert np.abs(big).max() <= 1.0 + 1e-12, "both families must be A-stable"
    assert abs(stability(TAU_RA, -1e6)[0]) < 1e-5, "Radau must have stiff decay"
    assert abs(abs(stability(TAU_GL, -1e6)[0]) - 1.0) < 1e-3, "Gauss must NOT"
    tg, yg = integrate(TAU_GL)
    tr, yr = integrate(TAU_RA)
    ex = np.cos(tr) + np.exp(-LAM * tr)
    print(f"    h*lambda = {H * LAM:g};  R(-h lambda): Gauss {stability(TAU_GL, -H*LAM)[0]:+.4f}, "
          f"Radau {stability(TAU_RA, -H*LAM)[0]:+.4f}")
    print(f"    max |Radau - exact| after the first step = {np.abs(yr[2:] - ex[2:]).max():.2e}")
    print(f"    max |Gauss - exact| after the first step = {np.abs(yg[2:] - ex[2:]).max():.2e}")
    assert np.abs(yr[2:] - ex[2:]).max() < 1e-3
    assert np.abs(yg[2:] - ex[2:]).max() > 0.5


BOX = dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.9)


def make_figure():
    _report()
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(9.6, 4.3))

    # ---- left: the stability function on the negative real axis ------------
    z = -np.logspace(-1, 4, 700)
    # The DASHED curve goes on top: the two coincide for small |z|, and only a
    # dashed line over a solid one lets both be seen where they do.
    axL.semilogx(-z, np.abs(stability(TAU_RA, z)), color=RADAU, lw=2.8, ls="-", zorder=4)
    axL.semilogx(-z, np.abs(stability(TAU_GL, z)), color=GAUSS, lw=2.8, ls="--", zorder=5)
    axL.axhline(1.0, color="0.75", lw=1.0, ls=(0, (1, 2)), zorder=1)

    axL.annotate("Gauss-Legendre", xy=(430.0, 0.865), fontsize=13, ha="center",
                 va="center", zorder=8, bbox=BOX)
    axL.annotate("$|R| \\to 1$: the fast mode\nis never damped",
                 xy=(430.0, 0.665), fontsize=11.5, ha="center", va="center",
                 zorder=8, bbox=BOX)
    axL.annotate("$R \\to 0$: stiff decay", xy=(430.0, 0.275), fontsize=11.5,
                 ha="center", va="center", zorder=8, bbox=BOX)
    axL.annotate("Radau IIA", xy=(430.0, 0.115), fontsize=13, ha="center",
                 va="center", zorder=8, bbox=BOX)
    axL.annotate(r"$|R| \leq 1$: both A-stable", xy=(0.16, 1.045), fontsize=11.5,
                 ha="left", va="bottom", zorder=8, bbox=BOX)
    axL.set_xlabel(r"$-h\lambda$")
    axL.set_ylabel(r"$|R(h\lambda)|$")
    axL.set_xlim(0.1, 1e4)
    axL.set_ylim(-0.04, 1.20)

    # ---- right: what that does to a trajectory -----------------------------
    tg, yg = integrate(TAU_GL)
    tr, yr = integrate(TAU_RA)
    tf = np.linspace(0.0, NSTEP * H, 2000)
    axR.plot(tg, yg, color=GAUSS, lw=2.6, ls="--", marker="s", ms=6,
             mfc="white", mec=GAUSS, mew=1.6, zorder=4)
    axR.plot(tr, yr, color=RADAU, lw=2.6, ls="-", marker="o", ms=6,
             mfc=RADAU, mec=RADAU, zorder=5)
    # ON TOP of Radau, and dotted: see defect 1 in the docstring.
    axR.plot(tf, np.cos(tf) + np.exp(-LAM * tf), color=EXACT, lw=1.3,
             ls=(0, (1, 4.0)), zorder=6)

    axR.annotate("Gauss-Legendre", xy=(0.55, 1.80), fontsize=13, ha="left",
                 va="center", zorder=8, bbox=BOX)
    axR.annotate("Radau IIA", xy=(2.0, yr[8]), xytext=(2.12, 1.36), fontsize=13,
                 ha="left", va="center", zorder=8, bbox=BOX,
                 arrowprops=dict(arrowstyle="-", lw=0.9, color="black"))
    axR.annotate("exact:  $\\cos t + e^{-\\lambda t}$", xy=(2.55, float(np.cos(2.55))),
                 xytext=(1.30, -1.42), fontsize=12, ha="left", va="center",
                 zorder=8, bbox=BOX,
                 arrowprops=dict(arrowstyle="-", lw=0.9, color="black"))
    axR.annotate(r"$\lambda = 1000$,  $h = 0.25$,  $h\lambda = 250$",
                 xy=(0.10, -1.82), fontsize=12, ha="left", va="center", zorder=8,
                 bbox=dict(boxstyle="round,pad=0.16", fc="white", ec="0.55", lw=0.8))
    axR.set_xlabel(r"$t$")
    axR.set_ylabel(r"$z(t)$")
    axR.set_xlim(0.0, NSTEP * H)
    axR.set_ylim(-2.05, 2.25)

    fig.tight_layout()
    return fig
