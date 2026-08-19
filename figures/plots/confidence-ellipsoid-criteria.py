r"""The confidence ellipsoid, and what each OED criterion measures on it.

    figures/plots/confidence-ellipsoid-criteria.py
        ->  media/figures/confidence-ellipsoid-criteria.{png,pdf}

Drawn for lectures/parameter-estimation-doe.tex, which asks for it by name:

    \revision[Figure]{This section wants the confidence-ellipsoid diagram ---
    one picture with the four criteria annotated on its axes. It is the
    highest-value figure in the lecture ...}

The lecture defines the region at (4.eq:ellipsoid),

    (theta - theta_hat)^T V^-1 (theta - theta_hat) <= chi^2_{p,alpha},

"whose axes point along the eigenvectors of V and whose semi-axis lengths scale
as sqrt(lambda_i(V))", and then lists five criteria that are all statements
about the SHAPE of that region.  Prose can say "A-optimality prioritizes the
directions you know least about"; only a picture shows that A, E and ME are
reading three different features of one ellipse and can therefore disagree.

GEOMETRY -- derived, not eyeballed
----------------------------------
With V = M^-1 (eqn (4.eq:VM), M the FIM) the region is

    (theta - theta_hat)^T M (theta - theta_hat) <= chi^2 .

Let M have eigenpairs (lambda_i, v_i).  Along v_i the boundary sits at
distance a_i where lambda_i a_i^2 = chi^2, so

    a_i = sqrt(chi^2 / lambda_i).                                        (*)

Every criterion in the lecture's table is then an exact statement about the
a_i, and these four identities are what the figure annotates:

    D   max det M          area   = pi a_1 a_2 = pi chi^2 / sqrt(det M)
    E   max lambda_min(M)  longest semi-axis a_max = sqrt(chi^2/lambda_min)
    A   min tr(M^-1)       a_1^2 + a_2^2 = chi^2 tr(M^-1)
    ME  min cond(M)        a_max / a_min = sqrt(cond M)

Each is an identity, not an analogy.  Note the direction of each arrow: D, E
and ME all SHRINK the region as their objective improves, and A does too.

pseudo-A (max tr M = max sum lambda_i) has NO such reading -- it is not a
statement about the ellipse at all, which is exactly why it is the trap the
lecture's "Class Activity --- the trap" is about, and why it is labelled that
way in panel (b) rather than given an arrow.

THE TWO DESIGNS IN PANEL (b) -- chosen so the criteria disagree
--------------------------------------------------------------
    design A:  eig(M) = {16, 1}      design B:  eig(M) = {4, 3}

    criterion       design A            design B          winner
    D   max det        16                  12             A
    pA  max tr         17                   7             A
    A   min tr(M^-1)   1/16 + 1   = 1.0625  1/4+1/3 = 0.5833   B
    E   max lam_min     1                   3              B
    ME  min cond       16                   1.3333         B

So D and pseudo-A recommend the elongated design and A, E, ME recommend the
round one, on the same pair of candidates.  This is the lecture's own text made
visible: "D increases total information volume but can bias the design toward
directions already well known."  All eight numbers above are recomputed in
_verify() below and asserted at import time, so the caption cannot drift from
the drawing.

Both ellipses are drawn at the SAME principal-axis orientation (35 degrees).
A real design change would rotate them too; holding the orientation fixed
isolates the one thing being compared, which is shape.

GREYSCALE
---------
Two series: design A is BLACK and SOLID, design B is #0072B2 and DASHED
(dL* = 46.0, well past the warn threshold, and redundantly keyed by linestyle
and by direct labelling).  The shaded interiors carry HATCH_CYCLE textures, not
tints, per the rule in _house.py.  No hue anywhere carries meaning on its own.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Ellipse

from _house import HATCH_CYCLE, SHADE_ALPHA

# chi^2 with p = 2 degrees of freedom at alpha = 0.05.  scipy.stats.chi2.ppf
# (0.95, 2) = 5.991464547107979; for p = 2 it is available in closed form,
# chi^2 = -2 ln(alpha) = -2 ln 0.05, which is what is used here so the figure
# has no scipy dependency.  Checked: -2*ln(0.05) = 5.991464547107979.
CHI2 = -2.0 * np.log(0.05)

TILT_DEG = 35.0                     # orientation of v_1, both designs

EIG_A = (16.0, 1.0)                 # design A: lots of information, badly balanced
EIG_B = (4.0, 3.0)                  # design B: less information, well balanced

BLACK = "black"
BLUE = "#0072B2"


def semi_axes(eigs):
    """(*) above: a_i = sqrt(chi^2 / lambda_i), returned (long, short)."""
    lam_max, lam_min = max(eigs), min(eigs)
    return np.sqrt(CHI2 / lam_min), np.sqrt(CHI2 / lam_max)


def _verify():
    """Recompute every number the docstring and the lecture caption assert."""
    for eigs, det, tr, tr_inv, cond in (
        (EIG_A, 16.0, 17.0, 1.0 / 16.0 + 1.0, 16.0),
        (EIG_B, 12.0, 7.0, 1.0 / 4.0 + 1.0 / 3.0, 4.0 / 3.0),
    ):
        lam = np.array(eigs)
        assert np.isclose(lam.prod(), det)
        assert np.isclose(lam.sum(), tr)
        assert np.isclose((1.0 / lam).sum(), tr_inv)
        assert np.isclose(lam.max() / lam.min(), cond)

        # the four identities the figure annotates
        a_long, a_short = semi_axes(eigs)
        assert np.isclose(np.pi * a_long * a_short, np.pi * CHI2 / np.sqrt(det))
        assert np.isclose(a_long, np.sqrt(CHI2 / lam.min()))
        assert np.isclose(a_long**2 + a_short**2, CHI2 * tr_inv)
        assert np.isclose(a_long / a_short, np.sqrt(cond))

    # the disagreement itself
    assert EIG_A[0] * EIG_A[1] > EIG_B[0] * EIG_B[1]            # D  picks A
    assert sum(EIG_A) > sum(EIG_B)                              # pA picks A
    assert sum(1.0 / np.array(EIG_A)) > sum(1.0 / np.array(EIG_B))   # A  picks B
    assert min(EIG_A) < min(EIG_B)                              # E  picks B
    assert max(EIG_A) / min(EIG_A) > max(EIG_B) / min(EIG_B)    # ME picks B


_verify()


def _ellipse(ax, eigs, *, color, linestyle, hatch_index, zorder=3):
    a_long, a_short = semi_axes(eigs)
    e = Ellipse(
        (0.0, 0.0),
        width=2 * a_long,
        height=2 * a_short,
        angle=TILT_DEG,
        facecolor="0.55",
        alpha=SHADE_ALPHA,
        hatch=HATCH_CYCLE[hatch_index],
        edgecolor=plt.rcParams["hatch.color"],
        linewidth=0.0,
        zorder=zorder - 1,
    )
    ax.add_patch(e)
    ax.add_patch(
        Ellipse(
            (0.0, 0.0),
            width=2 * a_long,
            height=2 * a_short,
            angle=TILT_DEG,
            facecolor="none",
            edgecolor=color,
            linestyle=linestyle,
            linewidth=2.4,
            zorder=zorder,
        )
    )
    return a_long, a_short


def _panel_a(ax):
    a_long, a_short = _ellipse(ax, EIG_A, color=BLACK, linestyle="-", hatch_index=0)

    t = np.deg2rad(TILT_DEG)
    v1 = np.array([np.cos(t), np.sin(t)])          # long axis, lambda_min
    v2 = np.array([-np.sin(t), np.cos(t)])         # short axis, lambda_max

    # the two semi-axes, drawn and named
    for vec, length, text, off in (
        (v1, a_long, r"$a_{\max}=\sqrt{\chi^2/\lambda_{\min}}$", (0.10, -0.28)),
        (v2, a_short, r"$a_{\min}=\sqrt{\chi^2/\lambda_{\max}}$", (0.12, 0.10)),
    ):
        tip = length * vec
        ax.annotate(
            "",
            xy=tuple(tip),
            xytext=(0.0, 0.0),
            arrowprops=dict(arrowstyle="-|>", color=BLACK, linewidth=1.6,
                            shrinkA=0, shrinkB=0),
            zorder=6,
        )
        ax.annotate(
            text,
            xy=(tip[0] + off[0], tip[1] + off[1]),
            fontsize=11,
            ha="left",
            va="center",
            bbox=dict(facecolor="white", edgecolor="none", pad=1.0),
            zorder=7,
        )

    ax.plot([0.0], [0.0], marker="*", markersize=16, color=BLACK,
            linestyle="none", zorder=8)
    ax.annotate(r"$\hat{\theta}$", xy=(0.12, -0.34), fontsize=14, zorder=8,
                bbox=dict(facecolor="white", edgecolor="none", pad=1.0))

    ax.annotate(
        "\n".join(
            [
                r"$\mathbf{D}$:  area $=\pi\chi^2/\sqrt{\det M}$",
                r"$\mathbf{E}$:  the long semi-axis $a_{\max}$",
                r"$\mathbf{A}$:  $a_{\max}^2+a_{\min}^2=\chi^2\,\mathrm{tr}(M^{-1})$",
                r"$\mathbf{ME}$: $a_{\max}/a_{\min}=\sqrt{\mathrm{cond}\,M}$",
            ]
        ),
        xy=(-2.80, -3.80),
        fontsize=10.5,
        ha="left",
        va="bottom",
        linespacing=1.5,
        bbox=dict(facecolor="white", edgecolor="0.6", pad=3.5),
        zorder=9,
    )

    ax.set_title("(a) one region, four readings", fontsize=13)


def _panel_b(ax):
    _ellipse(ax, EIG_A, color=BLACK, linestyle="-", hatch_index=0)
    _ellipse(ax, EIG_B, color=BLUE, linestyle="--", hatch_index=1, zorder=5)

    a_long_A, _ = semi_axes(EIG_A)
    t = np.deg2rad(TILT_DEG)
    ax.annotate(
        "design A\n$\\lambda=\\{16,\\,1\\}$",
        xy=(a_long_A * np.cos(t) + 0.10, a_long_A * np.sin(t) + 0.18),
        fontsize=11,
        color=BLACK,
        ha="center",
        va="bottom",
        bbox=dict(facecolor="white", edgecolor="none", pad=1.0),
        zorder=9,
    )
    ax.annotate(
        "design B\n$\\lambda=\\{4,\\,3\\}$",
        xy=(-1.95, 1.35),
        fontsize=11,
        color=BLUE,
        ha="center",
        va="bottom",
        bbox=dict(facecolor="white", edgecolor="none", pad=1.0),
        zorder=9,
    )

    ax.annotate(
        "\n".join(
            [
                r"$\mathbf{D}$   $\det M$: 16 vs 12  $\Rightarrow$ A",
                r"$\mathbf{pA}$  $\mathrm{tr}\,M$: 17 vs 7  $\Rightarrow$ A",
                r"$\mathbf{A}$   $\mathrm{tr}\,M^{-1}$: 1.06 vs 0.58 $\Rightarrow$ B",
                r"$\mathbf{E}$   $\lambda_{\min}$: 1 vs 3  $\Rightarrow$ B",
                r"$\mathbf{ME}$  $\mathrm{cond}$: 16 vs 1.3  $\Rightarrow$ B",
            ]
        ),
        xy=(-2.80, -3.80),
        fontsize=10.5,
        ha="left",
        va="bottom",
        linespacing=1.5,
        bbox=dict(facecolor="white", edgecolor="0.6", pad=3.5),
        zorder=9,
    )

    ax.set_title("(b) the criteria disagree", fontsize=13)


def make_figure():
    fig, axes = plt.subplots(1, 2, figsize=(10.4, 5.4))

    for ax in axes:
        ax.axhline(0.0, color="0.8", linewidth=0.8, zorder=0)
        ax.axvline(0.0, color="0.8", linewidth=0.8, zorder=0)
        ax.set_xlim(-2.9, 2.9)
        ax.set_ylim(-3.95, 2.6)
        ax.set_aspect("equal", adjustable="box")
        ax.set_xlabel(r"$\theta_1 - \hat{\theta}_1$")
        ax.set_xticks([-2, -1, 0, 1, 2])
        ax.set_yticks([-2, -1, 0, 1, 2])

    axes[0].set_ylabel(r"$\theta_2 - \hat{\theta}_2$")

    _panel_a(axes[0])
    _panel_b(axes[1])

    fig.tight_layout()
    return fig
