"""The branch and bound search tree for (MIPEX).

    figures/plots/branch-and-bound-tree.py
        -> media/figures/branch-and-bound-tree.{png,pdf}

    min  z = x + y1 + 3 y2 + 2 y3
    s.t. -x + 3 y1 + 2 y2 + y3 <= 0
         -5 y1 - 8 y2 - 3 y3 <= -9
         x >= 0,   y in {0,1}^3

Problem (MIPEX) of Biegler, Grossmann & Westerberg (1997), Appendix A, §A.3.2;
the tree drawn here is their Figure A.10. Reproduced from
`notebooks/8-dev/MINLP-Algorithms.ipynb` cells 6 and 10.

Why the picture earns its place: chapter 8 of the course had no plot and no
image at all until this week, and branch and bound is the one algorithm in the
course whose *shape* is the explanation. The table of nine rows says what
happened; the tree says why only nine rows were needed. Six of the fifteen
nodes are never solved, and at thirty-five binaries that ratio is the
difference between minutes and centuries.

What the drawing encodes, all of it colour-free so it survives a mono printer:

* a FILLED node is case 2 -- the relaxation landed on an integer point, so the
  node is a candidate solution and the descent stops;
* an OPEN node is case 1 (fathomed: infeasible, or bounded out) or case 3
  (branched);
* the node's LP value is written beside it, or "infeas.";
* the double ring marks the optimum, node 9.

No solver: the relaxations are small LPs and `scipy.optimize.linprog` (HiGHS
via scipy, no separate binary) solves them. The tree is built by the SAME
breadth-first loop as the notebook -- popped from the front of a FIFO queue --
rather than typed in by hand, so the drawing cannot drift from the algorithm.
"""

import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import linprog

INT_TOL = 1e-6

# variables ordered [x, y1, y2, y3]
C = np.array([1.0, 1.0, 3.0, 2.0])
A_UB = np.array([[-1.0, 3.0, 2.0, 1.0],
                 [0.0, -5.0, -8.0, -3.0]])
B_UB = np.array([0.0, -9.0])


def solve_node(fixed):
    """LP relaxation of (MIPEX) with some binaries fixed. y in [0,1] otherwise."""
    bounds = [(0.0, None)]
    for j in (1, 2, 3):
        v = fixed.get(j)
        bounds.append((v, v) if v is not None else (0.0, 1.0))
    r = linprog(C, A_ub=A_UB, b_ub=B_UB, bounds=bounds, method="highs")
    if not r.success:
        return {"status": "infeasible", "z": None, "y": None, "x": None}
    return {"status": "optimal", "z": float(r.fun),
            "y": np.asarray(r.x[1:]), "x": float(r.x[0])}


def branch_and_bound():
    """Breadth-first branch and bound. Returns (nodes, edges, incumbent)."""
    incumbent_z, incumbent = np.inf, None
    queue = [{"fixed": {}, "parent": None, "label": ""}]      # FIFO -> breadth first
    nodes, edges, node_id = [], [], 0

    while queue:
        node = queue.pop(0)
        node_id += 1
        r = solve_node(node["fixed"])
        if node["parent"] is not None:
            edges.append((node["parent"], node_id, node["label"]))
        rec = {"node": node_id, "z_LP": r["z"]}

        if r["status"] == "infeasible":                       # case 1a
            rec.update(case=1, outcome="infeasible")
        elif r["z"] > incumbent_z - INT_TOL:                  # case 1b
            rec.update(case=1, outcome="bounded out")
        else:
            frac = [j for j in (1, 2, 3)
                    if abs(r["y"][j - 1] - round(r["y"][j - 1])) > INT_TOL]
            if not frac:                                      # case 2
                incumbent_z, incumbent = r["z"], {**r, "node": node_id}
                rec.update(case=2, outcome="integral")
            else:                                             # case 3
                j = frac[0]
                rec.update(case=3, outcome=f"branch on y{j}")
                for value in (0, 1):
                    queue.append({"fixed": {**node["fixed"], j: value},
                                  "parent": node_id, "label": f"$y_{j}$={value}"})
        nodes.append(rec)
    return nodes, edges, incumbent


def _layout(edges):
    """Tidy tree layout: leaves take consecutive slots, a parent sits at their midpoint."""
    depth, children = {1: 0}, {}
    for parent, child, _ in edges:
        depth[child] = depth[parent] + 1
        children.setdefault(parent, []).append(child)
    x_of, slot = {}, [0.0]

    def place(n):
        kids = children.get(n, [])
        if not kids:
            x_of[n] = slot[0]
            slot[0] += 1.0
        else:
            for k in kids:
                place(k)
            x_of[n] = 0.5 * (x_of[kids[0]] + x_of[kids[-1]])

    place(1)
    return {n: (x_of[n], -depth[n]) for n in depth}, depth, x_of


def make_figure():
    nodes, edges, incumbent = branch_and_bound()
    table = {n["node"]: n for n in nodes}
    pos, depth, x_of = _layout(edges)

    fig, ax = plt.subplots(figsize=(8.6, 4.6))

    for parent, child, label in edges:
        (x0, y0), (x1, y1) = pos[parent], pos[child]
        ax.plot([x0, x1], [y0, y1], color="0.45", lw=1.5, ls="-", zorder=1)
        ax.annotate(label, xy=(x0 + 0.62 * (x1 - x0), y0 + 0.62 * (y1 - y0)),
                    ha="center", va="center", fontsize=11, zorder=2,
                    bbox=dict(boxstyle="round,pad=0.12", fc="white", ec="none"))

    for node_id, (x, y) in pos.items():
        rec = table[node_id]
        filled = rec["case"] == 2
        if node_id == incumbent["node"]:                      # the optimum
            ax.plot(x, y, marker="o", ms=32, mfc="none", mec="black",
                    mew=1.4, ls="none", zorder=3)
        ax.plot(x, y, marker="o", ms=25, ls="none", zorder=3,
                mfc="black" if filled else "white", mec="black", mew=1.8)
        ax.annotate(str(node_id), xy=(x, y), ha="center", va="center",
                    fontsize=13, zorder=4,
                    color="white" if filled else "black")
        text = "infeas." if rec["z_LP"] is None else f"$z={rec['z_LP']:g}$"
        ax.annotate(text, xy=(x + 0.22, y), ha="left", va="center",
                    fontsize=12, zorder=4)

    ax.annotate("filled $=$ integral relaxation (case 2)\n"
                "double ring $=$ optimum, $z^{*}=8$",
                xy=(0.015, 0.97), xycoords="axes fraction", fontsize=11,
                ha="left", va="top")

    ax.set_xlim(min(x_of.values()) - 0.6, max(x_of.values()) + 1.0)
    ax.set_ylim(-max(depth.values()) - 0.5, 0.5)
    ax.axis("off")
    fig.tight_layout()
    return fig


if __name__ == "__main__":                                    # a self-check
    nodes, edges, inc = branch_and_bound()
    for n in nodes:
        z = "infeasible" if n["z_LP"] is None else f"{n['z_LP']:.4f}"
        print(f"node {n['node']}  case {n['case']}  z_LP = {z:>10}   {n['outcome']}")
    print(f"\nz* = {inc['z']:.4f}   y* = {np.round(inc['y']).astype(int)}  "
          f"x* = {inc['x']:.4f}   (node {inc['node']})")
    print(f"{len(nodes)} nodes examined out of the 15 in the full tree")

    # independent check: complete enumeration of all 8 binary points
    best = (np.inf, None)
    for y in np.ndindex(2, 2, 2):
        y = np.array(y, dtype=float)
        # given y, x is driven to its smallest feasible value
        need = 3 * y[0] + 2 * y[1] + y[2]
        if -5 * y[0] - 8 * y[1] - 3 * y[2] > -9 + 1e-9:
            continue
        x = max(0.0, need)
        z = x + y[0] + 3 * y[1] + 2 * y[2]
        print(f"  y={y.astype(int)}  x={x:g}  z={z:g}")
        if z < best[0]:
            best = (z, (x, y))
    print(f"enumeration says z* = {best[0]:g} at x={best[1][0]:g}, "
          f"y={best[1][1].astype(int)}")
