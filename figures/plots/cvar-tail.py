r"""Value at risk, conditional value at risk, and the epigraph variables gamma_j.

    figures/plots/cvar-tail.py  ->  media/figures/cvar-tail.{png,pdf}

Drawn for lectures/stochastic-programming-advanced.tex, section "Conditional
value at risk", which states three things in prose that a picture settles at
once:

  1. "CVaR at level alpha is the expected cost CONDITIONAL on being in the
     worst alpha fraction of outcomes";
  2. "the optimal nu is the (1-alpha)-quantile of the loss" -- i.e. the
     auxiliary variable of (eq:cvar) is not an artefact, it IS the VaR;
  3. the epigraph reformulation (eq:cvar-lp): gamma_j >= phi(pi,xi_j) - nu and
     gamma_j >= 0 together reproduce [.]_+, and at the optimum gamma_j equals
     the positive part exactly.

The website's only picture of this is media/contrib/cvar_diagram.png, a screenshot that
figure_inventory.md lists under trap 1 and that fails the greyscale gate. This
replaces it from committed code.

PANEL (a) -- the continuous statement
-------------------------------------
Loss is lognormal, ln(phi) ~ N(mu, sigma^2), with sigma = 0.5 and mu chosen so
that E[phi] = exp(mu + sigma^2/2) = 1.  A skewed loss is the honest choice: the
lecture's motivation is "a farmer who is bankrupted by one poor harvest does not
get to enjoy the long-run average", and on a symmetric distribution VaR and
CVaR sit almost on top of each other and the figure says nothing.

Closed forms for the lognormal, both checked against 1-d quadrature in
_verify():

    VaR_alpha  = exp(mu + sigma z_{1-alpha})
    CVaR_alpha = E[phi | phi > VaR] = exp(mu + sigma^2/2) Phi(sigma - z_{1-alpha}) / alpha

With alpha = 0.20:  E[phi] = 1.000, VaR = 1.344, CVaR = 1.832.  So the ordering
E <= VaR <= CVaR is visible, and the gap CVaR - VaR is the part of the tail
that VaR alone cannot see -- the standard reason VaR is not a coherent risk
measure and CVaR is.

Phi and z_{1-alpha} are computed from math.erf and a bisection, so this script
needs no scipy (nothing else in figures/plots/ imports it).

PANEL (b) -- the same statement on a finite scenario set, which is (eq:cvar-lp)
------------------------------------------------------------------------------
20 i.i.d. draws from the same distribution, seeded, sorted, plotted as points.
For a finite sample the CVaR linear program's optimum is attained at an order
statistic: with N = 20 and alpha = 0.2 the minimiser of

    F(nu) = nu + (1/(alpha N)) sum_j [phi_j - nu]_+

is nu* = phi_(16) (the ceil((1-alpha)N)-th smallest), and then

    CVaR = phi_(16) + (1/4) sum_{j=17}^{20} (phi_j - phi_(16))
         = mean(phi_(17), ..., phi_(20)),

which is literally "the average of the worst 20% of scenarios".  _verify()
minimises F over a dense grid of nu and confirms both the argmin and the value,
so the identity is checked numerically rather than asserted.

The vertical stubs above nu* are the gamma_j of (eq:cvar-lp) -- one per tail
scenario, zero for every other scenario.  That is the figure's real payload:
students can see which gamma_j are nonzero, and the count is exactly alpha N.

NOTATION.  The loss is written f(pi,xi), matching \obj in the course pack --
NOT phi.  The pack renders \obj as f, and a figure that said phi beside a
lecture that says f would be a second symbol for one object.

GREYSCALE
---------
Nothing is keyed by hue.  The tail region is identified by HATCH_CYCLE[0]
texture rather than a tint; the three vertical rules are separated by
linestyle (E dotted, VaR dashed, CVaR solid) as well as by direct labels;
scenario markers are open circles outside the tail and filled circles inside.
Only black, #0072B2 (dL* = 46.0) and greys appear.
"""

import math

import numpy as np
import matplotlib.pyplot as plt

from _house import HATCH_CYCLE, SHADE_ALPHA

ALPHA = 0.20            # risk level: the worst 20% of outcomes
SIGMA = 0.5
MU = -0.5 * SIGMA**2    # so that E[phi] = exp(mu + sigma^2/2) = 1
N_SCEN = 20
SEED = 40499            # the course number; any fixed seed would do

BLACK = "black"
BLUE = "#0072B2"


def _Phi(z):
    """Standard normal CDF, from math.erf -- no scipy dependency."""
    return 0.5 * (1.0 + math.erf(z / math.sqrt(2.0)))


def _z(p, lo=-10.0, hi=10.0):
    """Standard normal quantile by bisection.  60 halvings ~ 1e-17 absolute."""
    for _ in range(200):
        mid = 0.5 * (lo + hi)
        if _Phi(mid) < p:
            lo = mid
        else:
            hi = mid
    return 0.5 * (lo + hi)


Z_1MA = _z(1.0 - ALPHA)
VAR = math.exp(MU + SIGMA * Z_1MA)
CVAR = math.exp(MU + 0.5 * SIGMA**2) * _Phi(SIGMA - Z_1MA) / ALPHA
MEAN = math.exp(MU + 0.5 * SIGMA**2)


def _pdf(x):
    out = np.zeros_like(x)
    pos = x > 0
    xp = x[pos]
    out[pos] = np.exp(-((np.log(xp) - MU) ** 2) / (2 * SIGMA**2)) / (
        xp * SIGMA * math.sqrt(2 * math.pi)
    )
    return out


def _scenarios():
    rng = np.random.default_rng(SEED)
    return np.sort(np.exp(MU + SIGMA * rng.standard_normal(N_SCEN)))


# numpy renamed trapz -> trapezoid in 2.0 and the course environment is not
# pinned across both; bind whichever this interpreter has.
_trapz = getattr(np, "trapezoid", None) or np.trapz


def _verify():
    # --- panel (a): the two closed forms, against quadrature ----------------
    grid = np.linspace(1e-6, 60.0, 2_000_001)
    dens = _pdf(grid)
    assert abs(_trapz(dens, grid) - 1.0) < 1e-6, "density does not integrate to 1"
    assert abs(_trapz(grid * dens, grid) - MEAN) < 1e-5, "mean mismatch"

    # start the tail EXACTLY at VaR: taking the first grid point above VaR
    # instead drops up to one panel of mass (~1.5e-5 here) and the check then
    # measures the grid, not the formula.
    tgrid = np.concatenate(([VAR], grid[grid > VAR]))
    tdens = _pdf(tgrid)
    mass = _trapz(tdens, tgrid)
    assert abs(mass - ALPHA) < 1e-5, f"tail mass {mass}, expected {ALPHA}"
    cond_mean = _trapz(tgrid * tdens, tgrid) / mass
    assert abs(cond_mean - CVAR) < 1e-4, f"CVaR {CVAR} vs quadrature {cond_mean}"

    assert MEAN < VAR < CVAR, "the ordering E <= VaR <= CVaR must hold"

    # --- panel (b): the finite-scenario LP optimum --------------------------
    phi = _scenarios()

    def F(nu):
        return nu + np.maximum(phi - nu, 0.0).sum() / (ALPHA * N_SCEN)

    nu_grid = np.linspace(phi.min() - 0.5, phi.max() + 0.5, 20001)
    vals = np.array([F(nu) for nu in nu_grid])
    nu_star = phi[int(math.ceil((1 - ALPHA) * N_SCEN)) - 1]      # phi_(16)
    assert abs(nu_grid[vals.argmin()] - nu_star) < 5e-3, "argmin is not phi_(16)"

    k = int(round(ALPHA * N_SCEN))                                # 4 tail scenarios
    assert k == 4
    assert abs(F(nu_star) - phi[-k:].mean()) < 1e-12, \
        "discrete CVaR is not the mean of the worst alpha*N scenarios"


_verify()


def _panel_a(ax):
    x = np.linspace(1e-4, 4.0, 2000)
    y = _pdf(x)

    xt = x[x >= VAR]
    ax.fill_between(
        xt,
        0.0,
        _pdf(xt),
        facecolor="0.55",
        alpha=SHADE_ALPHA,
        hatch=HATCH_CYCLE[0],
        edgecolor=plt.rcParams["hatch.color"],
        linewidth=0.0,
        zorder=1,
    )
    ax.plot(x, y, color=BLACK, linestyle="-", linewidth=2.6, zorder=4)

    ymax = y.max()
    for value, text, style, height in (
        (MEAN, f"$\\mathbb{{E}}[f] = {MEAN:.2f}$", ":", 0.97),
        (VAR, f"$\\mathrm{{VaR}} = \\nu^* = {VAR:.2f}$", "--", 0.80),
        (CVAR, f"$\\mathrm{{CVaR}} = {CVAR:.2f}$", "-", 0.63),
    ):
        ax.plot([value, value], [0.0, height * ymax], color=BLUE,
                linestyle=style, linewidth=2.2, zorder=5)
        ax.annotate(
            text,
            xy=(value + 0.06, height * ymax),
            fontsize=11,
            color=BLUE,
            ha="left",
            va="center",
            bbox=dict(facecolor="white", edgecolor="none", pad=1.0),
            zorder=8,
        )

    ax.annotate(
        f"worst {ALPHA:.0%} of outcomes\n(area $=\\alpha$)",
        xy=(2.20, 0.085),
        xytext=(3.05, 0.34),
        fontsize=11,
        ha="center",
        va="center",
        arrowprops=dict(arrowstyle="->", color=BLACK, linewidth=1.2),
        bbox=dict(facecolor="white", edgecolor="none", pad=1.0),
        zorder=9,
    )

    ax.set_xlim(0.0, 4.0)
    ax.set_ylim(0.0, 1.10 * ymax)
    ax.set_xlabel(r"loss $f(\pi,\xi)$")
    ax.set_ylabel("probability density")
    ax.set_title("(a) VaR sees the threshold, CVaR sees the tail", fontsize=13)


def _panel_b(ax):
    phi = _scenarios()
    j = np.arange(1, N_SCEN + 1)
    k = int(round(ALPHA * N_SCEN))
    nu_star = phi[N_SCEN - k - 1]                 # phi_(16) with N=20, k=4
    cvar = phi[-k:].mean()

    ax.axhline(nu_star, color=BLUE, linestyle="--", linewidth=2.2, zorder=3)
    ax.axhline(cvar, color=BLUE, linestyle="-", linewidth=2.2, zorder=3)

    # the epigraph variables: gamma_j = [phi_j - nu*]_+, nonzero only in the tail
    for jj, p in zip(j, phi):
        if p > nu_star:
            ax.plot([jj, jj], [nu_star, p], color=BLACK, linestyle="-",
                    linewidth=1.6, zorder=4)

    inside = phi > nu_star
    ax.plot(j[~inside], phi[~inside], marker="o", markersize=8,
            markerfacecolor="white", markeredgecolor=BLACK,
            linestyle="none", zorder=6)
    ax.plot(j[inside], phi[inside], marker="o", markersize=8,
            markerfacecolor=BLACK, markeredgecolor=BLACK,
            linestyle="none", zorder=6)

    ax.annotate(
        f"$\\nu^* = f_{{({N_SCEN - k})}} = {nu_star:.2f}$",
        xy=(0.6, nu_star - 0.07),
        fontsize=11,
        color=BLUE,
        ha="left",
        va="top",
        bbox=dict(facecolor="white", edgecolor="none", pad=1.0),
        zorder=8,
    )
    ax.annotate(
        f"$\\mathrm{{CVaR}} = {cvar:.2f}$\n= mean of the {k} filled points",
        xy=(0.6, cvar + 0.07),
        fontsize=11,
        color=BLUE,
        ha="left",
        va="bottom",
        bbox=dict(facecolor="white", edgecolor="none", pad=1.0),
        zorder=8,
    )

    tail_j = j[inside]
    ax.annotate(
        r"$\gamma_j = [f_j - \nu]_+ > 0$" + "\nhere, and $=0$ everywhere else",
        xy=(tail_j[0], 0.5 * (nu_star + phi[inside][0])),
        xytext=(11.0, 0.62),
        fontsize=11,
        ha="center",
        va="center",
        arrowprops=dict(arrowstyle="->", color=BLACK, linewidth=1.2),
        bbox=dict(facecolor="white", edgecolor="none", pad=1.0),
        zorder=9,
    )

    ax.set_xlim(0.0, N_SCEN + 1.0)
    ax.set_ylim(0.0, 1.15 * phi.max())
    ax.set_xlabel(r"scenario $j$, sorted by loss")
    ax.set_ylabel(r"loss $f(\pi,\xi_j)$")
    ax.set_xticks([1, 5, 10, 15, 20])
    ax.set_title(r"(b) the same thing as the LP (eq. cvar-lp)", fontsize=13)


def make_figure():
    fig, axes = plt.subplots(1, 2, figsize=(11.0, 4.6))
    _panel_a(axes[0])
    _panel_b(axes[1])
    fig.tight_layout()
    return fig
