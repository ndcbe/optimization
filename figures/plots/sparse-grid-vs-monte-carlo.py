"""Conceptual comparison of nested sparse-grid and Monte Carlo points.

The sparse set is the union of two-dimensional tensor products of nested
Clenshaw--Curtis nodes for level pairs l1+l2 <= 7. It has 145 unique points;
the comparison uses the same number of seeded uniform Monte Carlo samples.
This is an original course figure, not a reproduction of a published plot.
"""

import numpy as np
import matplotlib.pyplot as plt


def _nodes(level):
    if level == 1:
        return np.array([0.0])
    n = 2 ** (level - 1) + 1
    return np.cos(np.pi * np.arange(n) / (n - 1))


def _sparse_points(max_level_sum=7):
    points = set()
    for level_1 in range(1, max_level_sum):
        for level_2 in range(1, max_level_sum):
            if level_1 + level_2 <= max_level_sum:
                for x_1 in _nodes(level_1):
                    for x_2 in _nodes(level_2):
                        points.add((round(float(x_1), 12), round(float(x_2), 12)))
    return np.array(sorted(points))


def make_figure():
    sparse = _sparse_points()
    rng = np.random.default_rng(seed=2026)
    monte_carlo = rng.uniform(-1.0, 1.0, size=(len(sparse), 2))

    fig, axes = plt.subplots(1, 2, figsize=(8.2, 3.8), sharex=True, sharey=True)
    for ax, points, title, marker in (
        (axes[0], sparse, f"Nested sparse grid ({len(sparse)} points)", "o"),
        (axes[1], monte_carlo, f"Monte Carlo ({len(sparse)} points)", "x"),
    ):
        ax.scatter(points[:, 0], points[:, 1], color="black", marker=marker, s=17)
        ax.set(title=title, xlabel=r"$\xi_1$", xlim=(-1.05, 1.05), ylim=(-1.05, 1.05))
        ax.set_aspect("equal", adjustable="box")
    axes[0].set_ylabel(r"$\xi_2$")
    fig.tight_layout()
    return fig
