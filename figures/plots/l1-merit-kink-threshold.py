r"""Why the exact penalty is exact: the kink, and the threshold on rho.

    figures/plots/l1-merit-kink-threshold.py
        ->  media/figures/l1-merit-kink-threshold.{png,pdf}

Placed in `lecture-notes/lectures/constrained-globalization.tex` (Biegler Ch. 5,
Sections 5.5-5.8). There is NO notebook behind this one --
`notebooks/6/Globalization.ipynb` is the UNCONSTRAINED twin and stops before
merit functions, so this figure is authored for the handout.

The worked example is the lecture's own:

    min  f(x) = x1 + x2   s.t.  h(x) = x1^2 + x2^2 - 2 = 0
    x* = (-1, -1)^T,  v* = 1/2  (from grad f + J^T v = 0, i.e. (1,1) + v(-2,-2) = 0)

Walking radially, x = c(-1,-1)^T, gives f = -2c and h = 2c^2 - 2, so

    phi_1(c; rho) = -2c + rho |2c^2 - 2|,     phi_1(1; rho) = -2 for EVERY rho.

That last identity is why the picture works: all three curves pass through the
same point, so the only thing that changes between them is the SLOPE on each
side of the kink.

    D+ = d phi_1 / dc |_{c -> 1+} = -2 + 4 rho
    D- = d phi_1 / dc |_{c -> 1-} = -2 - 4 rho     (negative for every rho > 0)

so c = 1 is a strict local minimiser once rho > 1/2 = |v*|. That is Biegler's
threshold, verified against the book: the bullet on printed p. 111 reads "for
rho > rho* = ||v*||_q and 1/p + 1/q = 1, x* is a strict local minimizer for
phi_p(x, rho)". For p = 1 the dual index is q = infinity and rho* = max_i
|v*_i|. The condition is STRICT and the figure does not claim more: at
rho = rho* exactly, D+ = 0 and the minimum is degenerate rather than
first-order strict -- 400,000 sampled 2-D neighbours at rho = 0.5 put the
smallest excess at +5e-14, i.e. flat to within round-off. Nocedal & Wright
state the same threshold as mu* = max{|lambda*_i|} on p. 435 -- with absolute
values, which is why their opposite sign convention (L = f - lambda^T c) does
not matter here.

What the two panels are for
---------------------------
LEFT is the mechanism: a kink whose two one-sided slopes disagree is what pins
the minimiser onto the constraint. A SMOOTH penalty has no kink to hold it
there, which is Biegler (5.56), p. 110 -- no smooth penalty is exact.

RIGHT is the threshold itself, and it is the panel that makes eq:cg-threshold a
picture rather than a formula: D+ is a straight line in rho crossing zero at
exactly |v*| = 1/2, and D- never crosses at all.

Deliberate departures
---------------------
1. The radial slice is a 1-D slice of a 2-D problem, so the left panel proves
   less than the lecture claims. It was checked separately, by sampling 200,000
   random neighbours of x* in the plane: the fraction with lower phi_1 is
   ~0.47-0.50 for rho < 1/2 and EXACTLY ZERO for rho > 1/2. So the 2-D claim
   holds; the slice is an honest illustration of it, not a proof. The self-check
   below re-runs a smaller version of that sampling.
2. rho = 1/2 exactly is drawn, not just values either side. The boundary case
   (D+ = 0, flat to first order) is the one students ask about.
"""

import numpy as np
import matplotlib.pyplot as plt

from _house import HATCH_CYCLE, SHADE_ALPHA

# The example. x* = (-1,-1), v* = 1/2, so rho* = |v*| = 1/2.
V_STAR = 0.5
RHO_STAR = abs(V_STAR)

# Three penalty weights straddling the threshold, one of them ON it.
RHOS = (0.25, 0.50, 1.00)
RHO_LABELS = (
    r"$\rho = \frac{1}{4} < \rho^*$",
    r"$\rho = \rho^* = \frac{1}{2}$",
    r"$\rho = 1 > \rho^*$",
)

CLO, CHI = 0.62, 1.38


def phi1(c, rho):
    """l_1 merit function along the ray x = c(-1,-1)^T."""
    return -2.0 * c + rho * np.abs(2.0 * c**2 - 2.0)


def make_figure():
    fig, (axL, axR) = plt.subplots(1, 2, figsize=(9.2, 4.2))

    # ---------------------------------------------------------------- LEFT
    c = np.linspace(CLO, CHI, 601)
    for rho, label in zip(RHOS, RHO_LABELS):
        axL.plot(c, phi1(c, rho), linewidth=2.6)
        # Direct label at the right edge, vertically centred on the curve end.
        axL.annotate(
            label,
            xy=(CHI - 0.015, phi1(CHI, rho)),
            xytext=(-4, 0),
            textcoords="offset points",
            ha="right",
            va="center",
            fontsize=12.5,
            bbox=dict(facecolor="white", edgecolor="none", pad=1.2),
        )

    # The kink. Every curve passes through it, which is the point.
    axL.axvline(1.0, color="0.6", linestyle=":", linewidth=1.4, zorder=0)
    axL.plot([1.0], [-2.0], marker="o", markersize=9, color="black", linestyle="none",
             zorder=6)
    axL.annotate(
        r"kink at $x^*$" "\n" r"($\|h\|_1$ not differentiable)",
        xy=(1.0, -2.0),
        xytext=(0.655, -1.62),
        fontsize=12,
        ha="left",
        va="center",
        arrowprops=dict(arrowstyle="->", lw=1.3, color="black",
                        shrinkA=2, shrinkB=6),
    )

    axL.set_xlabel(r"$c$   along   $x = c\,(-1,-1)^{\mathsf{T}}$")
    axL.set_ylabel(r"$\varphi_1(x;\rho) = f + \rho\,|h|$")
    axL.set_xlim(CLO, CHI)
    axL.set_ylim(-2.45, 0.32)
    axL.set_title("the kink is what makes it exact", fontsize=13.5)

    # --------------------------------------------------------------- RIGHT
    r = np.linspace(0.0, 1.35, 400)
    dplus = -2.0 + 4.0 * r
    dminus = -2.0 - 4.0 * r

    # Exactness region: rho above the threshold.
    axR.axvspan(
        RHO_STAR,
        1.35,
        facecolor="0.55",
        alpha=SHADE_ALPHA,
        hatch=HATCH_CYCLE[0],
        edgecolor=plt.rcParams["hatch.color"],
        linewidth=0.0,
        zorder=0,
    )

    axR.axhline(0.0, color="0.6", linestyle=":", linewidth=1.4, zorder=1)
    axR.plot(r, dplus, linewidth=2.6, color="#000000", linestyle="-")
    axR.plot(r, dminus, linewidth=2.6, color="#0072B2", linestyle="--")

    axR.annotate(
        r"$D^{+} = -2 + 4\rho$",
        xy=(1.31, dplus[-1]),
        xytext=(-4, -2),
        textcoords="offset points",
        ha="right",
        va="top",
        fontsize=13,
        bbox=dict(facecolor="white", edgecolor="none", pad=1.2),
    )
    axR.annotate(
        r"$D^{-} = -2 - 4\rho$",
        xy=(1.31, dminus[-1]),
        xytext=(-4, 4),
        textcoords="offset points",
        ha="right",
        va="bottom",
        fontsize=13,
        color="#0072B2",
        bbox=dict(facecolor="white", edgecolor="none", pad=1.2),
    )

    axR.plot([RHO_STAR], [0.0], marker="o", markersize=9, color="black",
             linestyle="none", zorder=6)
    axR.annotate(
        r"$\rho^* = |v^*| = \frac{1}{2}$",
        xy=(RHO_STAR, 0.0),
        xytext=(RHO_STAR + 0.05, 2.15),
        fontsize=13,
        ha="left",
        va="center",
        arrowprops=dict(arrowstyle="->", lw=1.3, color="black",
                        shrinkA=2, shrinkB=6),
    )
    axR.annotate(
        "exact here",
        xy=(0.93, -4.4),
        fontsize=12.5,
        ha="center",
        va="center",
        bbox=dict(facecolor="white", edgecolor="none", pad=1.5),
    )

    axR.set_xlabel(r"penalty weight $\rho$")
    axR.set_ylabel(r"one-sided slope at $c = 1$")
    axR.set_xlim(0.0, 1.35)
    axR.set_ylim(-7.6, 3.6)
    axR.set_title(r"$\rho^*$ is where $D^{+}$ changes sign", fontsize=13.5)

    fig.tight_layout()
    return fig


if __name__ == "__main__":
    # ---- every number in the figure, reproduced independently ------------
    import numpy as _np

    # 1. The solution and its multiplier, from stationarity, not from prose.
    #    grad f + J^T v = 0  with  grad f = (1,1), J = (2x1, 2x2) = (-2,-2).
    v = _np.linalg.lstsq(
        _np.array([[-2.0], [-2.0]]), _np.array([-1.0, -1.0]), rcond=None
    )[0][0]
    assert abs(v - 0.5) < 1e-12, v
    assert abs(RHO_STAR - abs(v)) < 1e-12

    # 2. Every curve passes through (1, -2), independent of rho.
    for rho in RHOS:
        assert abs(phi1(1.0, rho) - (-2.0)) < 1e-12

    # 3. One-sided slopes, by finite difference on phi1 itself.
    eps = 1e-7
    for rho in RHOS:
        dp = (phi1(1.0 + eps, rho) - phi1(1.0, rho)) / eps
        dm = (phi1(1.0, rho) - phi1(1.0 - eps, rho)) / eps
        assert abs(dp - (-2 + 4 * rho)) < 1e-4, (rho, dp)
        assert abs(dm - (-2 - 4 * rho)) < 1e-4, (rho, dm)
        assert dm < 0.0
        print(f"  rho = {rho:.2f}:  D- = {dm:+.4f}   D+ = {dp:+.4f}")

    # 4. The 2-D claim the 1-D slice only illustrates: is x* = (-1,-1) really a
    #    local minimiser of phi_1 in the PLANE iff rho > 1/2?
    rng = _np.random.default_rng(0)
    xs = _np.array([-1.0, -1.0])

    def phi_2d(z, rho):
        return z[..., 0] + z[..., 1] + rho * _np.abs(z[..., 0] ** 2 + z[..., 1] ** 2 - 2)

    for rho in (0.40, 0.49, 0.51, 1.00):
        d = rng.normal(size=(40000, 2))
        d /= _np.linalg.norm(d, axis=1, keepdims=True)
        eps_r = rng.uniform(1e-6, 1e-2, size=(40000, 1))
        z = xs + eps_r * d
        frac = _np.mean(phi_2d(z, rho) < phi_2d(xs[None, :], rho)[0] - 1e-15)
        print(f"  rho = {rho:.2f}:  fraction of 2-D neighbours below phi_1 = {frac:.4f}")
        if rho > 0.5:
            assert frac == 0.0, (rho, frac)
        else:
            assert frac > 0.3, (rho, frac)
    print("l1-merit-kink-threshold: all self-checks passed")
