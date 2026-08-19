"""Outer approximation: the two bounds closing on a convex MINLP.

    figures/plots/outer-approximation-bounds.py
        -> media/figures/outer-approximation-bounds.{png,pdf}

`notebooks/8-dev/MINLP-Algorithms.ipynb` cell 27, on the multilayer building
insulation design problem:

    min  alpha / (R0 + sum_n x_n / k_n)  +  beta * sum_n (a_n y_n + b_n x_n)
    s.t. x_n <= tmax_n y_n,   sum_n x_n <= T,   x_n >= 0,   y_n in {0,1}

Why this figure earns its place: outer approximation is stated in the handout
as a flowchart, and a flowchart cannot show the one property the method turns
on -- that z^L is a valid LOWER bound that increases monotonically while z^u is
a valid UPPER bound that decreases, so the gap is a certificate and the loop
must terminate. The picture is that certificate.

Which bound is which, and why:

* the NLP subproblem fixes y, so it is a RESTRICTION of the MINLP. Its solution
  is an implementable design, hence z^u is an UPPER bound on the minimum.
* the MILP master replaces every nonlinear function by tangent planes at the
  points visited. f is convex here, so every tangent lies BELOW f, the master's
  feasible set CONTAINS the MINLP's, and z^L is a LOWER bound.

The final z^L lands slightly ABOVE z^u, and that is not a defect -- it is the
termination signal, and the figure shows it deliberately. The integer cuts have
removed every design already evaluated, so from iteration 2 onward z^L bounds
only the designs NOT YET TRIED. Once that exceeds the best design in hand,
nothing untried can beat it and the search is over. State the property
carefully in class: z^L bounds the un-cut remainder, not the whole MINLP.
Verified here by complete enumeration -- the true optimum over all 32 binary
points is 9.07000, the returned z^u is 9.07000, and the final z^L is 9.09808.

Convexity is not decoration. If f were nonconvex a tangent plane could cut into
the feasible region, z^L would not bound anything, and the method could
converge confidently to the wrong answer. f = alpha/R is convex here because
alpha/R is convex and decreasing in R > 0, composed with an affine increasing
function of x; the rest is linear.

Source and licence: the application, the physical model and the material data
are adapted from *Hands-On Mathematical Optimization with Python* by Postek,
Zocca, Gromicho and Kantor (Cambridge University Press, 2025), notebook 6.4,
"Optimal Design of Multilayered Building Insulation". MO-book code is MIT.

No solver binary. The NLP subproblem is convex in five variables and is solved
by `scipy.optimize.minimize` (SLSQP); the MILP master has only 2^5 = 32 binary
points, so it is solved EXACTLY by enumerating them and running
`scipy.optimize.linprog` on each -- which is a stronger guarantee than a
branch-and-bound solver gives, not a weaker one.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize, linprog

NAMES = ["Fiberglass batt", "Mineral wool", "Rigid foam (low R)",
         "Rigid foam (high R)", "Aerogel blanket"]
K = np.array([0.040, 0.030, 0.030, 0.015, 0.013])      # W/m/K
A = np.array([4.0, 5.0, 8.0, 8.0, 12.0])               # $/m^2 fixed
B = np.array([60.0, 150.0, 120.0, 180.0, 900.0])       # $/m^3 installed
TMAX = np.array([0.06, 0.06, 0.05, 0.05, 0.02])        # m

ALPHA = 60.0      # annualized energy cost per unit U  [$ K / W / m^2]
BETA = 0.05       # equivalent annual cost factor on capital
R0 = 2.0          # resistance of the structural elements [m^2 K / W]
T_TOTAL = 0.15    # thickness the wall cavity allows [m]
N = len(K)


def resistance(x):
    return R0 + float(np.dot(x, 1.0 / K))


def f_cont(x):
    """The nonlinear part of the objective: energy cost plus material cost."""
    return ALPHA / resistance(x) + BETA * float(np.dot(B, x))


def grad_f_cont(x):
    """d/dx_n [alpha / R] = -alpha / R^2 / k_n, plus the linear material term."""
    R = resistance(x)
    return -ALPHA / R**2 / K + BETA * B


def solve_nlp(y):
    """NLP subproblem: minimise the design cost with the layers y fixed.

    A restriction of the MINLP, so its value is an upper bound.
    """
    ub = TMAX * y
    x0 = 0.5 * ub
    if ub.sum() > T_TOTAL:
        x0 = x0 * T_TOTAL / max(ub.sum(), 1e-12)
    res = minimize(
        lambda x: f_cont(x) + BETA * float(np.dot(A, y)),
        x0, jac=lambda x: grad_f_cont(x), method="SLSQP",
        bounds=[(0.0, float(u)) for u in ub],
        constraints=[{"type": "ineq",
                      "fun": lambda x: T_TOTAL - x.sum(),
                      "jac": lambda x: -np.ones(N)}],
        options={"maxiter": 500, "ftol": 1e-12},
    )
    assert res.success, f"NLP subproblem failed for y={y}: {res.message}"
    return res.x, float(res.fun)


def solve_master(points, tried):
    """MILP master: minimise the epigraph variable over all tangent planes.

    Solved exactly by enumerating the 32 binary points and solving the LP in
    (x, epi) for each. `tried` supplies the integer cuts -- those y are excluded.
    """
    best_z, best_y = np.inf, None
    for bits in np.ndindex(*([2] * N)):
        y = np.array(bits, dtype=float)
        if any(np.array_equal(y, yk) for yk in tried):
            continue                                   # integer cut
        # variables [x_1..x_N, epi];  minimise epi
        c = np.zeros(N + 1)
        c[-1] = 1.0
        rows, rhs = [], []
        for xk in points:
            gk, fk = grad_f_cont(xk), f_cont(xk)
            # epi >= beta a.y + f_k + gk.(x - x_k)  ->  gk.x - epi <= gk.x_k - f_k - beta a.y
            row = np.zeros(N + 1)
            row[:N] = gk
            row[-1] = -1.0
            rows.append(row)
            rhs.append(float(np.dot(gk, xk)) - fk - BETA * float(np.dot(A, y)))
        row = np.zeros(N + 1)
        row[:N] = 1.0
        rows.append(row)
        rhs.append(T_TOTAL)                            # thickness budget
        bounds = [(0.0, float(TMAX[n] * y[n])) for n in range(N)] + [(None, None)]
        r = linprog(c, A_ub=np.array(rows), b_ub=np.array(rhs),
                    bounds=bounds, method="highs")
        if r.success and r.fun < best_z:
            best_z, best_y = float(r.fun), y
    return best_y, best_z


def outer_approximation(y_start, eps=1e-4, max_iter=20):
    """The handout's flowchart, as a loop. Returns the per-iteration bound history."""
    y = np.array(y_start, dtype=float)
    points, tried, history = [], [], []
    z_upper, z_lower, best = np.inf, -np.inf, None

    for _ in range(max_iter):
        xk, z_nlp = solve_nlp(y)                       # upper bound
        if z_nlp < z_upper:
            z_upper, best = z_nlp, (y.copy(), xk.copy())
        points.append(xk)
        tried.append(y.copy())

        y_new, z_master = solve_master(points, tried)  # lower bound
        if y_new is None:                              # every y cut off
            z_lower = z_upper
            history.append((z_upper, z_lower))
            break
        z_lower = max(z_lower, z_master)
        history.append((z_upper, z_lower))
        if z_upper - z_lower <= eps:
            break
        y = y_new
    return np.array(history), best


# The deliberately poor start: aerogel alone. Highest resistance per unit
# thickness in the table, and by far the highest cost per unit of resistance --
# the specification a catalogue leads you to and an optimizer talks you out of.
Y_START = np.array([0.0, 0.0, 0.0, 0.0, 1.0])


def make_figure():
    history, best = outer_approximation(Y_START)
    it = np.arange(1, len(history) + 1)

    fig, ax = plt.subplots(figsize=(6.8, 4.2))
    ax.plot(it, history[:, 0], color="black", ls="-", lw=2.4, marker="o", ms=8)
    ax.plot(it, history[:, 1], color="#0072B2", ls="--", lw=2.4, marker="s", ms=8)
    ax.fill_between(it, history[:, 1], history[:, 0], facecolor="0.6",
                    alpha=0.15, linewidth=0.0)

    ax.annotate("upper bound $z^{u}$\nNLP subproblem,\na restriction",
                xy=(1.12, 20.5), fontsize=11.5, va="top", ha="left")
    ax.annotate("lower bound $z^{L}$\nMILP master,\na relaxation",
                xy=(1.12, -5.4), fontsize=11.5, va="top", ha="left",
                color="#0072B2")
    ax.annotate("the gap is\nthe certificate", xy=(1.46, 8.2),
                fontsize=11.5, ha="center", va="center")
    # The crossing at the last iteration is the termination signal, not an
    # error: the integer cuts mean z^L now bounds only the UNTRIED designs.
    ax.annotate("$z^{L}$ crosses $z^{u}$:\nnothing untried\ncan win",
                xy=(3.0, 9.1), xytext=(2.62, 18.5),
                fontsize=11.5, ha="center", va="top",
                arrowprops=dict(arrowstyle="->", color="0.35", lw=1.2))

    ax.set_xlabel("outer approximation iteration")
    ax.set_ylabel("annualized cost [\\$/m$^2$]")
    ax.set_xticks(it)
    ax.set_xlim(0.88, 3.22)
    ax.set_ylim(-13.0, 22.5)
    fig.tight_layout()
    return fig


if __name__ == "__main__":                                    # a self-check
    history, best = outer_approximation(Y_START)
    print(" k   z^u (upper)   z^L (lower)      gap")
    for k, (zu, zl) in enumerate(history, 1):
        print(f"{k:2d}   {zu:10.5f}   {zl:10.5f}   {zu - zl:9.2e}")
    y, x = best
    print("\noptimal design:")
    for n, name in enumerate(NAMES):
        if y[n] > 0.5:
            print(f"  {name:<22} x = {x[n] * 1000:6.2f} mm")
    print(f"  total thickness {x.sum() * 1000:.2f} mm  (budget "
          f"{T_TOTAL * 1000:.0f} mm)")
    print(f"  cost {f_cont(x) + BETA * float(np.dot(A, y)):.5f} $/m^2/yr")

    # bounds must actually bound: exhaustive check over all 32 binary points
    zs = []
    for bits in np.ndindex(*([2] * N)):
        yy = np.array(bits, dtype=float)
        _, z = solve_nlp(yy)
        zs.append(z)
    print(f"\ntrue optimum by complete enumeration of all 32 y: {min(zs):.5f}")
    print(f"monotone upper bound: {np.all(np.diff(history[:, 0]) <= 1e-9)}")
    print(f"monotone lower bound: {np.all(np.diff(history[:, 1]) >= -1e-9)}")
