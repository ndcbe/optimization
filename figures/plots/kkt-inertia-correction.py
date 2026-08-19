r"""Why the inertia correction is a THRESHOLD -- Biegler (5.12) and Thm. 5.4, p. 97.

    figures/plots/kkt-inertia-correction.py
        ->  media/figures/kkt-inertia-correction.{png,pdf}

The equality-constrained-Newton handout states the corrected KKT system

    [ W^k + delta_W I   J_h^T      ] [ d_x ]      [ grad_x L ]
    [ J_h              -delta_A I  ] [ d_v ]  = - [ h(x^k)   ]      (5.12), p. 97

then asserts Theorem 5.4 -- "for any delta_A > 0 there exist suitable values of
delta_W such that the corrected KKT matrix has inertia (n, m, 0)" -- and stops.
Nothing in the handout tells a student what delta_W actually DOES to the matrix,
and the natural (wrong) reading of the Levenberg--Marquardt analogy is that
delta_W is a dial that trades accuracy for robustness continuously.

It is not a dial. It is a threshold, and the threshold is a number you can name:

    delta_W* = -lambda_min( Z^T W^k Z ),   Z an orthonormal null basis of J_h.

Below it the inertia is wrong no matter how close you get; at it exactly one
eigenvalue of the KKT matrix is zero; above it the inertia is (n, m, 0) and
stays there. That is what this figure shows, and it is the reason Algorithm 5.2
(p. 98) can search by INCREASING delta_W monotonically -- there is nothing to
tune back down.

Why delta_W* has that value
---------------------------
Biegler derives the inertia result on p. 95 via (5.10): with J_h full row rank
the KKT matrix is congruent to a block diagonal matrix whose blocks are m
copies of [[0,1],[1,0]] -- each contributing one + and one - -- and the reduced
Hessian Z^T W Z. By Sylvester's law of inertia (Thm. 5.2, p. 94) congruence
preserves inertia, so

    inertia(K) = (n, m, 0)   <=>   Z^T W Z  positive definite.

Replacing W by W + delta_W I and taking Z ORTHONORMAL (Z^T Z = I) gives
Z^T (W + delta_W I) Z = Z^T W Z + delta_W I, so every reduced eigenvalue is
shifted by exactly delta_W and the condition is delta_W > -lambda_min(Z^T W Z).
Hence the threshold. Note this shift-by-exactly-delta_W step needs Z
orthonormal; with the coordinate basis (5.23) it is only a bound.

The example (n = 3, m = 1)
--------------------------
    W   = [[2, 1, 0], [1, -1, 1], [0, 1, 1]]        symmetric, INDEFINITE
    J_h = [1, 1, 1]                                 full row rank
    delta_A = 0                                     J_h is not rank deficient

VERIFIED (recomputed on every run; the assertions in _report() are the check)
----------------------------------------------------------------------------
    eig(Z^T W Z)          = -1.527525, +1.527525
    delta_W*              =  1.5275252316519468
    eig(K) at delta_W = 0 = -1.7520, -0.8698, +1.4467, +3.1750  -> inertia (2,2,0)  WRONG
    eig(K) at delta_W*    = -0.8053,  0.0000, +2.9287, +4.4592  -> inertia (2,1,1)  singular
    eig(K) at delta_W = 3 = -0.5656, +1.3946, +4.3744, +5.7966  -> inertia (3,1,0)  CORRECT

The zero at delta_W* is exact to 8 decimals -- asserted, not eyeballed. Note
also what does NOT happen: the negative eigenvalue never crosses. It cannot,
because the m copies of [[0,1],[1,0]] contribute their one negative eigenvalue
regardless of delta_W, which is why the target inertia has an m in it at all.

What delta_A is for, and why it is NOT in this figure
----------------------------------------------------
delta_A treats a DIFFERENT failure: J_h rank deficient, which puts an exact
zero eigenvalue in K that no delta_W can move. Checked numerically while
building this figure, with J_h = [[1,1,1],[2,2,2]] (rank 1, m = 2): the
eigenvalue nearest zero is 0.0 to machine precision for every delta_W in
[0, 3], and setting delta_A = 0.1 moves it to -0.1. That is a one-line fact and
a flat line; it is stated in the caption rather than plotted, because a second
panel showing a horizontal line at zero would earn no space.

Greyscale
---------
Four eigenvalue curves = the four-series limit in figures/README.md, and each
carries the style cycle's linestyle. But colour is not doing the work: the one
curve that matters is drawn heavy and black and labelled in place, the other
three are thin and grey, and the correct-inertia region is identified by
HATCHING (via _house.shade), not by tint.
"""

import numpy as np
import matplotlib.pyplot as plt

from _house import HATCH_CYCLE, SHADE_ALPHA

W = np.array([[2.0, 1.0, 0.0], [1.0, -1.0, 1.0], [0.0, 1.0, 1.0]])
JH = np.array([[1.0, 1.0, 1.0]])
N, M = 3, 1
DW_MAX = 3.0


def kkt(dw, da=0.0):
    return np.block([[W + dw * np.eye(N), JH.T], [JH, -da * np.eye(M)]])


def threshold():
    """delta_W* = -lambda_min(Z^T W Z), with Z an ORTHONORMAL null basis."""
    Z = np.linalg.svd(JH)[2][M:].T
    return -np.linalg.eigvalsh(Z.T @ W @ Z)[0], np.linalg.eigvalsh(Z.T @ W @ Z)


def _report(dstar):
    print(f"    delta_W* = {dstar:.10f}")
    for dw in (0.0, dstar, DW_MAX):
        e = np.linalg.eigvalsh(kkt(dw))
        inertia = (int((e > 1e-9).sum()), int((e < -1e-9).sum()), int((abs(e) <= 1e-9).sum()))
        print(f"      delta_W = {dw:6.4f}  eig = {np.round(e, 4)}  inertia = {inertia}")
    assert abs(np.linalg.eigvalsh(kkt(dstar))[M]) < 1e-8, "no zero eigenvalue at the threshold"
    e0 = np.linalg.eigvalsh(kkt(0.0))
    assert int((e0 < 0).sum()) == 2, "example is supposed to START with wrong inertia"
    eh = np.linalg.eigvalsh(kkt(DW_MAX))
    assert (int((eh > 0).sum()), int((eh < 0).sum())) == (N, M)
    # delta_A is what a rank-deficient Jacobian needs; recorded, not plotted.
    jh2 = np.array([[1.0, 1.0, 1.0], [2.0, 2.0, 2.0]])
    for da in (0.0, 0.10):
        near = [
            min(np.linalg.eigvalsh(np.block([[W + dw * np.eye(3), jh2.T],
                                             [jh2, -da * np.eye(2)]])), key=abs)
            for dw in np.linspace(0, DW_MAX, 13)
        ]
        print(f"      rank-deficient J_h, delta_A = {da:.2f}: "
              f"|eig| nearest zero in [{min(map(abs, near)):.3g}, {max(map(abs, near)):.3g}]")


def make_figure():
    dstar, red = threshold()
    _report(dstar)

    dw = np.linspace(0.0, DW_MAX, 601)
    eig = np.array([np.linalg.eigvalsh(kkt(d)) for d in dw])  # ascending, 4 columns

    fig, ax = plt.subplots(figsize=(6.4, 4.4))

    # The region where the inertia is (n, m, 0). Hatched, not tinted.
    ax.axvspan(dstar, DW_MAX, facecolor="0.55", alpha=SHADE_ALPHA,
               hatch=HATCH_CYCLE[0], edgecolor=plt.rcParams["hatch.color"],
               linewidth=0.0, zorder=0)

    ax.axhline(0.0, color="0.35", lw=1.0, ls=(0, (1, 2)), zorder=1)

    # Columns 0, 2, 3 never change sign; column 1 is the one that crosses.
    for j in (0, 2, 3):
        ax.plot(dw, eig[:, j], color="0.55", lw=1.6, ls="-", zorder=2)
    ax.plot(dw, eig[:, 1], color="black", lw=3.0, ls="-", zorder=4)

    ax.plot([dstar], [0.0], "o", ms=11, color="black", mfc="white", mew=2.2, zorder=6)
    ax.axvline(dstar, color="black", lw=1.2, ls="--", ymin=0.0, ymax=0.52, zorder=3)

    box = dict(boxstyle="round,pad=0.12", fc="white", ec="none", alpha=0.9)

    # Direct labelling, not a legend: each curve is named where it starts.
    for j, name in enumerate((r"$\lambda_1$", r"$\lambda_2$", r"$\lambda_3$", r"$\lambda_4$")):
        ax.annotate(name, xy=(0.07, eig[0, j] + 0.10), fontsize=13.5, ha="left",
                    va="bottom", zorder=8, bbox=box)

    ax.annotate("only $\\lambda_2$ changes sign; the $m = 1$\nnegative eigenvalue never does",
                xy=(0.66, -2.45), fontsize=12, ha="left", va="center", zorder=8, bbox=box)
    ax.annotate("inertia $(3,1,0)$", xy=(2.28, 5.45), fontsize=14, ha="center",
                va="center", zorder=8, bbox=box)
    ax.annotate("inertia $(2,2,0)$\nWRONG", xy=(0.62, 5.30), fontsize=13, ha="center",
                va="center", zorder=8, bbox=box)
    ax.annotate(r"$\delta_W^{\,*} = -\lambda_{\min}(Z^{T} W^k Z) = %.4f$" % dstar,
                xy=(dstar, 0.0), xytext=(0.13, 1.05), fontsize=11.5,
                ha="left", va="center", zorder=8,
                bbox=dict(boxstyle="round,pad=0.16", fc="white", ec="0.55", lw=0.8),
                arrowprops=dict(arrowstyle="-", lw=0.9, color="black"))

    ax.set_xlabel(r"$\delta_W$")
    ax.set_ylabel("eigenvalues of the KKT matrix")
    ax.set_xlim(0.0, DW_MAX)
    ax.set_ylim(-3.1, 6.4)
    fig.tight_layout()
    return fig
