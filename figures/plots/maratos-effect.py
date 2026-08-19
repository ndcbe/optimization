"""The Maratos effect, and the second-order correction that cures it.

    figures/plots/maratos-effect.py  ->  media/figures/maratos-effect.{png,pdf}

Nocedal & Wright (2006), **Example 15.4, printed p. 441**, attributed there to
Powell [255]; their own Figure 15.8 draws the left panel. Verified by reading
p. 441 directly, not from a secondary source -- this pack previously cited the
example as "18.1", which is wrong.

    min  f(x) = 2(x1^2 + x2^2 - 1) - x1     s.t.  c(x) = x1^2 + x2^2 - 1 = 0

with x* = (1, 0), and Hessian of the Lagrangian exactly I at the solution.

⚠ MULTIPLIER SIGN. N&W print lambda* = 3/2 under their Lagrangian f - lambda*c.
This course writes L = f + lambda^T h, so the SAME solution has
**lambda* = -3/2** here. The multiplier negates; the Hessian of the Lagrangian
does not (it is I either way). Anything imported from p. 441 must be translated.

From any feasible iterate x_k = (cos t, sin t), the SQP step is
p_k = (sin^2 t, -sin t cos t), and N&W give the two norms in closed form:

    ||x_k + p_k - x*|| = 2 sin^2(t/2),     ||x_k - x*|| = 2 |sin(t/2)|

so ||x_k + p_k - x*|| = (1/2) ||x_k - x*||^2 EXACTLY -- textbook quadratic
convergence. Re-derived here symbolically and confirmed numerically at five
values of t: the ratio is 0.500000 every time.

And yet the step is rejected. Both f AND the constraint violation get WORSE,
and -- re-derived symbolically here, a detail N&W do not print -- they get worse
by exactly the SAME amount:

    c(x_k + p_k) = sin^2 t        f(x_k + p_k) - f(x_k) = sin^2 t

with c(x_k) = 0. Any merit function built from those two quantities, and any
filter, refuses a step that is quadratically converging. That is the Maratos
effect, and it is why a globalization strategy can destroy the very convergence
rate SQP was chosen for.

Left panel  -- the geometry. The circle is the constraint; the light circles
are contours of f (level sets of f are circles centred at (1/4, 0)). The step
leaves the constraint and climbs the objective, while landing much closer to x*.

Right panel -- the rejection itself, which is the part a geometry picture
cannot show. The l1 merit function

    phi(alpha) = f(x) + rho |c(x)|,     rho = 2 > |lambda*| = 3/2

is plotted along the SQP step, x_k + alpha p_k, and along the second-order
corrected arc, x_k + alpha p_k + alpha^2 phat. Along the plain step phi turns
around near alpha = 0.2 and ends ABOVE phi(0): a backtracking line search
accepts only a tiny step and throws the full one away. Along the corrected arc
phi is below phi(0) at alpha = 1, so the full step is accepted and the
quadratic rate survives.

rho = 2 is not arbitrary: the l1 penalty is exact only for rho > |lambda*|, and
lambda* is 3/2 in magnitude. A figure drawn with rho below that threshold would
be demonstrating a different failure.

The SECOND-ORDER CORRECTION is drawn on the left panel: it is the smallest
step restoring feasibility to second order,

    phat = -grad c_k * c(x_k + p_k) / ||grad c_k||^2

Note honestly what it does NOT do: it does not return the iterate to the
circle. The correction restores feasibility only to SECOND order, so |c| after
it is small but nonzero. That is all that is needed for the merit function to
accept the step, which the right panel shows.

No solver: every quantity is closed form.
"""

import numpy as np
import matplotlib.pyplot as plt

XSTAR = np.array([1.0, 0.0])


def f(x):
    return 2.0 * (x[0] ** 2 + x[1] ** 2 - 1.0) - x[0]


def c(x):
    return x[0] ** 2 + x[1] ** 2 - 1.0


def sqp_step(t):
    """N&W (15.35): the SQP step from the feasible iterate (cos t, sin t)."""
    return np.array([np.sin(t) ** 2, -np.sin(t) * np.cos(t)])


def soc_step(xk, pk):
    """Second-order correction: smallest phat with grad c_k . phat + c(xk+pk) = 0."""
    gc = 2.0 * xk
    return -gc * c(xk + pk) / float(gc @ gc)


def make_figure():
    fig, (ax0, ax1) = plt.subplots(1, 2, figsize=(9.6, 4.2))

    # ------------------------------------------------------- panel 1: geometry
    t = 1.0                                   # large enough to draw; the effect
    xk = np.array([np.cos(t), np.sin(t)])     # is worse as t -> 0, not better
    pk = sqp_step(t)
    xtrial = xk + pk
    ph = soc_step(xk, pk)
    xsoc = xtrial + ph

    ang = np.linspace(0, 2 * np.pi, 400)
    ax0.plot(np.cos(ang), np.sin(ang), color="black", ls="-", lw=2.2)

    # contours of f: level sets are circles centred at (1/4, 0)
    for lev in (-1.0, -0.75, -0.4, 0.0, 0.5):
        r2 = (lev + 2.0) / 2.0 + 1.0 / 16.0
        if r2 > 0:
            r = np.sqrt(r2)
            ax0.plot(0.25 + r * np.cos(ang), r * np.sin(ang),
                     color="0.62", ls=":", lw=1.1, zorder=0)

    ax0.annotate("", xy=xtrial, xytext=xk,
                 arrowprops=dict(arrowstyle="-|>", color="black", lw=2.0))
    ax0.annotate("", xy=xsoc, xytext=xtrial,
                 arrowprops=dict(arrowstyle="-|>", color="#0072B2", lw=2.0,
                                 linestyle="--"))

    ax0.plot(*xk, marker="o", color="black", ms=9, ls="none")
    ax0.plot(*xtrial, marker="s", color="black", ms=9, ls="none", mfc="white",
             mew=1.8)
    ax0.plot(*xsoc, marker="^", color="#0072B2", ms=10, ls="none")
    ax0.plot(*XSTAR, marker="*", color="black", ms=17, ls="none")

    ax0.annotate("$x^k$", xy=(xk[0] - 0.10, xk[1] + 0.10), fontsize=13,
                 ha="right", va="bottom")
    ax0.annotate("$x^k + p^k$\noff the circle,\nand $f$ has risen",
                 xy=(xtrial[0] + 0.10, xtrial[1] + 0.16), fontsize=11,
                 ha="left", va="bottom")
    ax0.annotate("second-order\ncorrection", xy=xsoc,
                 xytext=(1.42, -0.78), fontsize=11, ha="left", va="center",
                 color="#0072B2",
                 arrowprops=dict(arrowstyle="->", color="#0072B2", lw=1.2))
    ax0.annotate("$x^{*}$", xy=(XSTAR[0] - 0.12, XSTAR[1] - 0.14), fontsize=14,
                 ha="right", va="top")
    ax0.annotate("constraint $x_1^2+x_2^2=1$", xy=(-1.42, 1.34), fontsize=11,
                 ha="left", va="top")
    ax0.annotate("contours of $f$", xy=(-0.05, -1.44), fontsize=11,
                 ha="center", va="bottom", color="0.35")

    ax0.set_xlabel("$x_1$")
    ax0.set_ylabel("$x_2$")
    ax0.set_aspect(1)
    ax0.set_xlim(-1.45, 2.05)
    ax0.set_ylim(-1.60, 1.45)

    # ------------------- panel 2: the merit function, and what it rejects
    RHO = 2.0                       # exact only for rho > |lambda*| = 3/2
    phi = lambda z: f(z) + RHO * abs(c(z))

    al = np.linspace(0.0, 1.0, 201)
    plain = np.array([phi(xk + a * pk) for a in al])
    # the corrected arc is x_k + alpha p + alpha^2 phat, not a straight line
    corrected = np.array([phi(xk + a * pk + a**2 * ph) for a in al])

    ax1.axhline(plain[0], color="0.62", ls=":", lw=1.4)
    ax1.plot(al, plain, color="black", ls="-", lw=2.4)
    ax1.plot(al, corrected, color="#0072B2", ls="--", lw=2.4)
    ax1.plot([1.0], [plain[-1]], marker="s", color="black", ms=10, ls="none",
             mfc="white", mew=1.8)
    ax1.plot([1.0], [corrected[-1]], marker="^", color="#0072B2", ms=11,
             ls="none")

    ax1.annotate(r"along the SQP step $x^k + \alpha p^k$",
                 xy=(0.30, plain[60] + 0.045), fontsize=11, ha="left",
                 va="bottom")
    ax1.annotate("with the second-order correction,\n"
                 r"$x^k + \alpha p^k + \alpha^2 \hat{p}$",
                 xy=(0.045, -1.02), fontsize=11, ha="left",
                 va="top", color="#0072B2")
    ax1.annotate(r"$\phi(0)$", xy=(0.015, plain[0] + 0.02), fontsize=11,
                 ha="left", va="bottom", color="0.35")
    ax1.annotate("full step REJECTED", xy=(1.0, plain[-1]),
                 xytext=(0.86, plain[-1] + 0.16), fontsize=11, ha="right",
                 va="bottom",
                 arrowprops=dict(arrowstyle="->", color="0.35", lw=1.2))
    ax1.annotate("accepted", xy=(1.0, corrected[-1]),
                 xytext=(0.80, corrected[-1] + 0.40), fontsize=11, ha="right",
                 va="bottom", color="#0072B2",
                 arrowprops=dict(arrowstyle="->", color="#0072B2", lw=1.2))

    ax1.set_xlabel(r"step fraction $\alpha$")
    ax1.set_ylabel(r"$\phi(\alpha) = f + \rho\,|c|$,  $\rho = 2$")
    ax1.set_xlim(0, 1.08)
    ax1.set_ylim(-1.55, 1.95)

    fig.tight_layout()
    return fig


if __name__ == "__main__":                                    # a self-check
    print("  theta    |xk-x*|    |xk+pk-x*|   ratio/e^2      df        |c| after")
    for t in (0.75, 0.6, 0.3, 0.1, 0.03, 0.01):
        xk = np.array([np.cos(t), np.sin(t)])
        pk = sqp_step(t)
        xt = xk + pk
        e0, e1 = np.linalg.norm(xk - XSTAR), np.linalg.norm(xt - XSTAR)
        print(f"  {t:5.3f}  {e0:9.6f}  {e1:11.3e}  {e1 / e0**2:9.6f}  "
              f"{f(xt) - f(xk):+9.3e}  {abs(c(xt)):9.3e}")
        # N&W's closed forms, printed on p. 441
        assert abs(e1 - 2 * np.sin(t / 2) ** 2) < 1e-12
        assert abs(e0 - 2 * abs(np.sin(t / 2))) < 1e-12
        assert f(xt) > f(xk) and abs(c(xt)) > abs(c(xk))      # BOTH get worse

    print("\nsecond-order correction, from theta = 0.75:")
    t = 0.75
    xk = np.array([np.cos(t), np.sin(t)])
    pk = sqp_step(t)
    xs = xk + pk + soc_step(xk, pk)
    print(f"  f:   {f(xk):+.6f} -> {f(xk + pk):+.6f} (worse) -> {f(xs):+.6f} "
          f"({'better' if f(xs) < f(xk) else 'WORSE'} than x^k)")
    print(f"  |c|: {abs(c(xk)):.3e} -> {abs(c(xk + pk)):.3e} (worse) -> "
          f"{abs(c(xs)):.3e}")
    print(f"  |x-x*|: {np.linalg.norm(xk - XSTAR):.6f} -> "
          f"{np.linalg.norm(xs - XSTAR):.6f}")
