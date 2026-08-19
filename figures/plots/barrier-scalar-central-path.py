"""The scalar log-barrier family, and the central path it traces to the bound.

    figures/plots/barrier-scalar-central-path.py
        ->  media/figures/barrier-scalar-central-path.{png,pdf}

This is Biegler (2010) Figure 6.1, printed p. 152, redrawn: barrier solutions
for mu = 0.1, 0.05, 0.01, 0.001 of

    min  phi_mu(x) = x - mu ln(x)      s.t.  x >= 0,

whose original problem (mu = 0) is `min x s.t. x >= 0` with x* = 0.

Why it exists: Prof. Dowling's 2018 lecture notes carry a margin note beside
(6.49) reading "Need to show picture"
(transcriptions/Lecture17_InequalityConstrainedNLPs.md, scan p. 3). This is that
picture. There is no notebook behind it -- the lecture cites the book figure.

Everything here is closed form, so the figure is exact rather than solved:

    phi_mu'(x) = 1 - mu/x = 0   =>   x(mu) = mu
    phi_mu(x(mu)) = mu - mu ln(mu) = mu (1 - ln mu)

which is conclusion (v) of Biegler's Theorem 6.7, pp. 152-153, in its sharpest
possible form: for this problem ||x(mu) - x*|| = mu exactly, not merely O(mu).

Deliberate departures from the book figure
------------------------------------------
1. The minimizers are marked and joined by a dotted path. Biegler plots the
   four curves only. The point of the lecture is the *trajectory* x(mu) -> x*,
   which is invisible if the minima are not marked.
2. The line f(x) = x -- the mu = 0 objective the family converges to -- is drawn
   as a grey reference. It is background, not a fifth series, so it is drawn in
   grey at reduced width like the contours in kkt-geometry.py, and the four
   colour-cycle slots stay inside the course's four-series greyscale cap.
3. Direct labels at the minima rather than a legend, per figures/README.md.
"""

import numpy as np
import matplotlib.pyplot as plt

from _house import label_curve

MUS = (0.1, 0.05, 0.01, 0.001)

XLO, XHI = 1e-4, 0.32
YLO, YHI = 0.0, 0.52

# Label offsets, hand-tuned against the rendered PNG so no label sits on a
# curve or on its neighbour. Order matches MUS.
LABEL_OFFSETS = ((0.012, 0.028), (0.012, 0.028), (0.014, 0.030), (0.016, 0.026))


def phi(x, mu):
    return x - mu * np.log(x)


def x_star(mu):
    """Exact minimizer of phi_mu on x > 0."""
    return mu


def make_figure():
    fig, ax = plt.subplots(figsize=(5.6, 4.6))

    x = np.linspace(XLO, XHI, 4000)

    # mu = 0 reference: the objective the whole family is converging to.
    ax.plot(x, x, color="0.62", linewidth=1.4, linestyle="-", zorder=1)
    ax.annotate(
        r"$f(x) = x$",
        xy=(0.243, 0.205),
        fontsize=12.5,
        color="0.35",
        rotation=13,
        zorder=2,
    )

    mins_x, mins_y = [], []
    for i, mu in enumerate(MUS):
        ax.plot(x, phi(x, mu), zorder=3)
        xm = x_star(mu)
        ym = phi(xm, mu)
        mins_x.append(xm)
        mins_y.append(ym)
        ax.plot(
            [xm], [ym], marker="o", markersize=8, color="black",
            linestyle="none", zorder=6,
        )
        dx, dy = LABEL_OFFSETS[i]
        label_curve(
            ax, xm, ym, rf"$\mu = {mu:g}$", dx=dx, dy=dy,
            fontsize=12.5, zorder=7,
            bbox=dict(facecolor="white", edgecolor="none", pad=1.0),
        )

    # The central path: the minimizers, joined, running down to the bound.
    ax.plot(
        [0.0] + mins_x[::-1], [0.0] + mins_y[::-1],
        linestyle=":", linewidth=1.8, color="black", zorder=5,
    )
    ax.plot([0.0], [0.0], marker="*", markersize=17, color="black",
            linestyle="none", zorder=7, clip_on=False)
    ax.annotate(
        r"$x^{*} = 0$",
        xy=(0.008, 0.045),
        fontsize=12.5,
        zorder=7,
        bbox=dict(facecolor="white", edgecolor="none", pad=1.0),
    )
    ax.annotate(
        r"$x(\mu) = \mu$",
        xy=(0.083, 0.108),
        fontsize=13,
        zorder=7,
        bbox=dict(facecolor="white", edgecolor="none", pad=1.0),
    )
    ax.annotate(
        "", xy=(0.004, 0.012), xytext=(0.030, 0.088),
        arrowprops=dict(arrowstyle="-|>", color="black", linewidth=1.6),
        zorder=6,
    )

    ax.set_xlim(YLO, XHI)
    ax.set_ylim(YLO, YHI)
    ax.set_xlabel("$x$")
    ax.set_ylabel(r"$\varphi_{\mu}(x) = x - \mu \ln x$")
    fig.tight_layout()
    return fig


if __name__ == "__main__":
    # Every number in the figure, reproduced independently of the prose.
    for mu in MUS:
        # 1. The closed-form minimizer really is the minimizer: check against a
        #    dense numerical argmin, and against the first-order condition.
        grid = np.linspace(mu / 20, mu * 20, 400001)
        num = grid[np.argmin(phi(grid, mu))]
        assert abs(num - mu) < 1e-6, (mu, num)
        assert abs(1.0 - mu / x_star(mu)) < 1e-12          # phi' = 1 - mu/x = 0
        assert phi(mu, mu) == mu * (1.0 - np.log(mu))      # value at the min
        print(f"mu={mu:<7g} x(mu)={x_star(mu):<8g} "
              f"phi={phi(mu, mu):.6f}  numeric argmin={num:.6g}")
    # 2. Theorem 6.7(v): ||x(mu) - x*|| = O(mu). Here it is exactly mu.
    errs = np.array([abs(x_star(m) - 0.0) for m in MUS])
    assert np.allclose(errs, MUS)
    print("Thm 6.7(v): ||x(mu) - x*|| / mu =", np.round(errs / np.array(MUS), 12))
