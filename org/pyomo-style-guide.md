# Pyomo Style Guide

This is the house style for every notebook on this website — the ones Prof. Dowling writes, the ones
you write for [Project 1](project1.md), and the ones you
[contribute to the class repository](contribute.md).

It exists so that a reader who has seen one notebook can read any other one without relearning
conventions, and so that a notebook that ran in 2026 still runs in 2030.

**How to use it.** Work down the checklist at the bottom before you submit or open a pull request.
Every rule below has a short right/wrong pair; that is the whole rule. Nothing here is subtle.

Most of the modeling conventions follow the
[MO-book Pyomo style guide](https://mobook.github.io/MO-book/notebooks/appendix/pyomo-style-guide-update.html)
by Postek, Zocca, Gromicho and Kantor. The sections on **solver status**, **reproducibility**, the
**Colab setup cell** and the **solution markers** are specific to this course.

---

## 1. Imports and namespace

Import Pyomo under the `pyo` alias. Never import its contents into the global namespace: `Var`,
`Set`, `value` and `minimize` are all common English words, and a bare `from ... import *` makes it
impossible to tell Pyomo objects from your own.

```python
# YES
import pyomo.environ as pyo

m.x = pyo.Var(domain=pyo.NonNegativeReals)
```

```python
# NO
from pyomo.environ import *

m.x = Var(domain=NonNegativeReals)
```

Companion packages follow the same pattern: `import pyomo.dae as dae`, `import numpy as np`,
`import pandas as pd`, `import matplotlib.pyplot as plt`.

:::{note}
Some older notebooks on this site still use `from pyomo.environ import *`. They predate this guide
and are being converted. Do not copy them.
:::

---

## 2. Build the model in a function

Every model is built by a function that takes data and returns a fresh `ConcreteModel`.

```python
# YES
def build_storage_model(price, e0=0.0):
    """Build the energy-arbitrage LP.

    Arguments:
        price: NumPy array of hourly energy prices
        e0: initial storage level [MWh]

    Returns:
        a Pyomo ConcreteModel
    """
    m = pyo.ConcreteModel()
    ...
    return m


m = build_storage_model(price=ca_data["price"].to_numpy(), e0=0.0)
```

```python
# NO — model assembled across ten cells, mutating a global `m`
m = pyo.ConcreteModel()
# ... cell 4 ...
m.x = pyo.Var()
# ... cell 9 ...
m.con = pyo.Constraint(expr=m.x >= 1)
```

Why: re-running one cell out of order silently corrupts a model built at notebook scope, and Pyomo
raises confusing errors when a component is redefined. A build function is re-runnable, is trivially
reusable for a second scenario, and makes the data dependencies explicit.

**Use `ConcreteModel`, not `AbstractModel`.** `AbstractModel` exists for a workflow (separate `.dat`
files) that this course does not use.

---

## 3. Naming

| Object | Convention | Example |
| --- | --- | --- |
| Model | short — bare `m` is fine and preferred | `m`, `m_relaxed` |
| Sets | **UPPER CASE** | `m.FOODS`, `m.HORIZON`, `m.TIME` |
| Params | `snake_case` | `m.unit_cost`, `m.sqrt_eta` |
| Vars | `snake_case` | `m.servings`, `m.charge_rate` |
| Constraints | `snake_case`, named for the physics or the requirement | `m.energy_balance` |
| Rule functions (legacy form) | `<constraint_name>_rule` | `def energy_balance_rule(m, t):` |

UPPER CASE set names are a deliberate deviation from PEP 8. They make index sets visually distinct
from the data indexed over them, which is worth the inconsistency. Everything else follows PEP 8.

Single-letter variable names are acceptable **only** where they match the mathematics printed
immediately above them in the notebook. If the handout calls it $x_i$, call it `m.x`.

---

## 4. Sets and indexing

Declare a `pyo.Set` or `pyo.RangeSet` rather than indexing over a raw Python list or `range`.

```python
# YES
m.HORIZON = pyo.RangeSet(0, n_hours - 1)
m.charge = pyo.Var(m.HORIZON, domain=pyo.NonNegativeReals)
```

```python
# NO
m.charge = pyo.Var(range(n_hours), domain=pyo.NonNegativeReals)
```

Why: a `Set` is part of the model, so `m.pprint()` shows it, the IDAES diagnostics tools can reason
about it, and one edit changes every component indexed over it.

---

## 5. Variables: `domain=` and `bounds=`

Use the keyword `domain=`, not the older synonym `within=`. They do the same thing; pick one, and
the house choice is `domain=`.

Put bounds you know in `bounds=` rather than writing them as constraints. Bound handling inside a
solver is much cheaper than a general inequality, and it keeps the constraint list about the model
rather than about the box.

```python
# YES
m.servings = pyo.Var(m.FOODS, domain=pyo.NonNegativeReals, bounds=(0, 10))
```

```python
# NO
m.servings = pyo.Var(m.FOODS, within=pyo.Reals)


@m.Constraint(m.FOODS)
def lower(m, f):
    return m.servings[f] >= 0


@m.Constraint(m.FOODS)
def upper(m, f):
    return m.servings[f] <= 10
```

Bounds that depend on a decision, or that you want a dual variable for, are genuine constraints —
write them as constraints.

---

## 6. Constraints: decorators are the house style

Pyomo offers two equivalent ways to attach a constraint rule. **Prefer the decorator.** The rule
function is the form you will meet in older code, in the Pyomo book, and in about half the notebooks
on this site — you need to be able to read it, but write the decorator in new work.

```python
# YES — house style
@m.Constraint(m.HORIZON)
def energy_balance(m, t):
    if t == m.HORIZON.first():
        return m.E[t] == m.E0 + m.charge[t] * m.sqrt_eta - m.discharge[t] / m.sqrt_eta
    return m.E[t] == m.E[t - 1] + m.charge[t] * m.sqrt_eta - m.discharge[t] / m.sqrt_eta


@m.Objective(sense=pyo.minimize)
def total_cost(m):
    return sum(m.price[t] * (m.charge[t] - m.discharge[t]) for t in m.HORIZON)
```

```python
# ALSO CORRECT — rule-function form; you will see this in older notebooks
def energy_balance_rule(m, t):
    if t == m.HORIZON.first():
        return m.E[t] == m.E0 + m.charge[t] * m.sqrt_eta - m.discharge[t] / m.sqrt_eta
    return m.E[t] == m.E[t - 1] + m.charge[t] * m.sqrt_eta - m.discharge[t] / m.sqrt_eta


m.energy_balance = pyo.Constraint(m.HORIZON, rule=energy_balance_rule)
```

The decorator wins because the name is written once instead of three times (function name, `_rule`
suffix, component name), and the component name cannot drift out of sync with the function that
defines it. The same decorators exist for `@m.Objective`, `@m.Expression`, `@m.Param` and
`@m.Integral`.

:::{warning}
**The decorator form is not in the course textbook.** *Pyomo — Optimization Modeling in Python*
(Bynum et al., 3rd ed., 2021) discusses Python decorators in general on p. 212 but never shows
`@m.Constraint`; every constraint in the book uses the `rule=` form. If you are working from the
book, translate as you go. Both forms are fully supported in current Pyomo and produce identical
models.
:::

**Prefer `pyo.Constraint` over `pyo.ConstraintList`** whenever the constraints are indexed by
something. A `ConstraintList` gives you `m.con[1]`, `m.con[2]`, … with no record of what index 7
meant; an indexed `Constraint` gives you `m.energy_balance[t]`. `ConstraintList` is fine for a
genuinely heterogeneous handful of one-off constraints, and for cutting-plane loops where
constraints are added as the algorithm runs.

For a single, non-indexed constraint, `expr=` is clearer than a one-line rule:

```python
m.periodic_boundary = pyo.Constraint(expr=m.E0 == m.E[m.HORIZON.last()])
```

---

## 7. Always check the solver result

**This is a hard rule, and it is the one most often broken.**

`solver.solve(m)` returns a results object. It does **not** raise when the solve fails. If the
problem was infeasible or unbounded, the variables are left uninitialized, and the *next* line that
touches them dies with

```
ValueError: No value for uninitialized ScalarVar EP
```

which reads like a bug in your code and sends you looking in the wrong place entirely.

This is not hypothetical. In the August 2026 audit of this site, two contributed notebooks failed
exactly this way — `contrib/portfolio_optimization_extended.ipynb` (the model is genuinely
infeasible) and `contrib/race_car_extended.ipynb` (a dropped ODE constraint left the model
unbounded). In both cases the real diagnosis took much longer than it should have, because the
traceback pointed at a `pyo.value()` call rather than at the failed solve.

```python
# YES
solver = pyo.SolverFactory("ipopt")
results = solver.solve(m, tee=True)

assert pyo.check_optimal_termination(results), (
    f"Solve failed: status={results.solver.status}, "
    f"termination={results.solver.termination_condition}"
)

print(f"total cost = {pyo.value(m.total_cost):.4f}")
```

```python
# NO
solver = pyo.SolverFactory("ipopt")
solver.solve(m)
print(pyo.value(m.total_cost))  # blows up somewhere else if the solve failed
```

`pyo.check_optimal_termination(results)` is the short form. When you want to distinguish outcomes —
which you often do in this course, because *why* a solve failed is frequently the point — branch on
the termination condition:

```python
results = solver.solve(m, tee=False)
tc = results.solver.termination_condition

if pyo.check_optimal_termination(results):
    print(f"optimal: {pyo.value(m.total_cost):.4f}")
elif tc == pyo.TerminationCondition.infeasible:
    print("infeasible — check the constraints and bounds")
elif tc == pyo.TerminationCondition.unbounded:
    print("unbounded — the objective is missing a constraint")
elif tc == pyo.TerminationCondition.maxIterations:
    print("hit the iteration limit — try a better initial point or scaling")
else:
    print(f"solver status={results.solver.status}, termination={tc}")
```

`pyo.TerminationCondition`, `pyo.SolverStatus` and `pyo.check_optimal_termination` are all available
from `pyomo.environ`; you do not need `from pyomo.opt import ...`.

:::{note}
**A notebook that deliberately demonstrates a failed solve still checks.** Several notebooks here
show non-convergence, infeasibility or a singular KKT system on purpose. That is exactly the case
where you want an explicit, labelled report of the termination condition — not an unrelated
traceback three cells later.
:::

Use `tee=True` while you are developing so you can see the solver log. Turn it off in a cell whose
output is a figure.

---

## 7a. Which solver to call

| Problem class | Solver | `SolverFactory` name |
| --- | --- | --- |
| LP, MILP | [HiGHS](https://highs.dev/) | `"appsi_highs"` |
| NLP | Ipopt | `"ipopt"` |
| MINLP | Bonmin / Couenne | `"bonmin"`, `"couenne"` |

**HiGHS is the course default for anything linear.** GLPK was the default through Fall 2024 and has
been retired: HiGHS is faster, is actively developed, and installs everywhere with
`pip install highspy` — no `apt-get`, so it works on Colab, macOS and Windows identically. If you
are reading an older notebook that calls `pyo.SolverFactory("glpk")`, replace it with
`pyo.SolverFactory("appsi_highs")`.

```python
# YES
solver = pyo.SolverFactory("appsi_highs")
results = solver.solve(m, tee=True)
assert pyo.check_optimal_termination(results)
```

Two details that bite:

- **`tee` is a keyword of `solve()`, not of `SolverFactory()`.** The shell-based solvers (`glpk`,
  `cbc`, `ipopt`) silently swallow `SolverFactory("glpk", tee=True)` and print nothing;
  `SolverFactory("appsi_highs", tee=True)` raises instead. Put `tee=` on the `solve()` call, where it
  has always belonged.
- **The results object is the ordinary Pyomo one.** In Pyomo 6.10, `SolverFactory("appsi_highs")`
  returns a legacy-compatible wrapper, so `pyo.check_optimal_termination(results)` and
  `results.solver.termination_condition` work exactly as in §7. You only need the APPSI-native
  `results.termination_condition` form if you construct the solver directly from
  `pyomo.contrib.appsi`, which this course does not do.

HiGHS may report a binary variable as `-0.0` rather than `0.0`. Compare with a tolerance
(`if pyo.value(m.x[i]) >= 0.5:`), never with `== 0`.

**Alternate optima are real.** Several course models have ties — the knapsack has two distinct
selections worth 25, and the integer-cut exercise in `assignments/Pyomo2.ipynb` has two worth 14.
Different solvers (and different versions of the same solver) may return different members of a tied
set. The *objective value* is what you check and what you grade on; do not write a test that asserts
one particular argmin.

---

## 8. Reproducibility: seed every random number generator

If a notebook uses randomness anywhere — sampled scenarios, random restarts, a train/test split,
initial points — **seed it at the top, in the same cell as the imports.**

```python
# YES
import numpy as np

rng = np.random.default_rng(seed=0)
returns = rng.normal(loc=mu, scale=sigma, size=(n_scenarios, n_assets))
```

```python
# NO
returns = np.random.normal(loc=mu, scale=sigma, size=(n_scenarios, n_assets))
```

`np.random.seed(0)` before legacy `np.random.*` calls is acceptable in existing notebooks; prefer
`default_rng` in new work.

Why: `contrib/portfolio_optimization_extended.ipynb` has no seed anywhere, and two consecutive runs
reported an expected profit of **59.6 M USD** and **33.02 M USD**. A reader cannot tell whether they
have reproduced your result or broken it. A notebook whose numbers change run to run cannot be
graded, cannot be reviewed, and cannot be debugged.

---

## 9. The Colab setup cell

**Every notebook starts with the same setup cell**, before any other code. It installs solvers on
Google Colab and does nothing on a local machine with the course environment already installed.

Copy it exactly:

```python
# This code cell installs packages on Colab

import sys

if "google.colab" in sys.modules:
    !wget "https://raw.githubusercontent.com/ndcbe/optimization/main/notebooks/helper.py"
    import helper

    helper.easy_install()
else:
    sys.path.insert(0, "../")
    import helper

helper.set_plotting_style()
```

Details that matter:

- **`import sys` must be inside the cell.** The guard tests `sys.modules`, so the cell cannot rely
  on an import from anywhere else. A missing `import sys` breaks the notebook on the very first
  cell — this really happened in `assignments/Pyomo3.ipynb` and was only caught by the 2026
  execution audit.
- **It must be the first code cell**, so every install finishes before anything needs it.
- **`helper.easy_install()`** installs IDAES plus Ipopt, `k_aug`, `cbc`, `bonmin`, `couenne` and
  `dot_sens`, and pip-installs **HiGHS** (`highspy`). Use it unless you have a reason not to. You do
  not need to add anything extra to use HiGHS.
- **`helper.install_glpk()` is deprecated.** GLPK has been retired in favour of HiGHS (see §7a). The
  function is still in `helper.py` for a handful of older contributed notebooks that have not been
  converted yet. Do not call it in new work.
- **Extra packages go inside the `if` branch**, as `!pip install ...`, so a local run is untouched:

  ```python
  if "google.colab" in sys.modules:
      !wget "https://raw.githubusercontent.com/ndcbe/optimization/main/notebooks/helper.py"
      !pip install casadi
      import helper

      helper.easy_install()
  ```

  If the package is one the whole course needs, say so in your pull request so it can be added to
  `environment.yml` instead.
- **Put all remaining imports in the second cell**, together, rather than scattering them through
  the notebook.

`helper.py` lives at `notebooks/helper.py` in this repository. Read it if you are curious about what
`easy_install` actually does.

---

## 10. Data files and media

`scripts/process_notebooks.py` rewrites two kinds of path when it publishes a notebook, so that the
published copy works on Colab where only the `.ipynb` file is present:

| You write | Published as |
| --- | --- |
| `"./data/file.csv"` or `"../data/file.csv"` | `https://raw.githubusercontent.com/ndcbe/optimization/main/notebooks/data/file.csv` |
| `../../media/figure.png` | `https://raw.githubusercontent.com/ndcbe/optimization/main/media/figure.png` |

So:

- **Data files go in `notebooks/data/`** and are referenced as `"../data/<name>"`. Commit the data
  file. Three notebooks in the 2026 audit failed because their data was never committed.
- **Images go in `media/`** (student contributions: `media/contrib/`) and are referenced as
  `../../media/<name>`.
- **File names are case-sensitive on the web server and not on macOS.** `Alg3-2.png` referencing
  `alg3-2.png` on disk looks fine locally and 404s on the live site. Match the case exactly.
- **A notebook should not write files into the source tree** when it runs. If it must produce an
  artifact, write it to a temporary directory, or add the output pattern to `.gitignore`.

---

## 11. Solution markers

Notebooks with in-class or homework activities put the answer between two marker comments.
`scripts/process_notebooks.py` replaces everything between them with `# Add your solution here`
before the notebook is published.

```python
# Compute the optimal charging schedule.

### BEGIN SOLUTION
m = build_storage_model(price, e0=0.0)
results = solver.solve(m)
assert pyo.check_optimal_termination(results)
### END SOLUTION
```

Formatting requirements — all four, every time:

1. The markers are **bare comments on their own lines**: `### BEGIN SOLUTION` and
   `### END SOLUTION`. No trailing text, no extra indentation, no `#### BEGIN SOLUTION`.
2. They must be **correctly paired**, in order, and **inside a code cell**. A marker in a markdown
   cell does nothing.
3. Both markers must be in the **same cell**. The stripper works cell by cell.
4. Do not nest them.

Why this matters more than it looks: the published notebook is *generated*. Nobody re-reads it. A
`BEGIN` without an `END` leaves the solution visible on the public website; an `END` without a
`BEGIN` leaves a stripped, broken notebook. Both failure modes are silent.

The same rules apply to `### BEGIN HIDDEN TESTS` / `### END HIDDEN TESTS`, which are replaced by
`# Removed autograder test. You may delete this cell.`

:::{important}
**Never edit a notebook under `notebooks/<n>/` — edit `notebooks/<n>-dev/`.** The numbered folders
are generated output and are overwritten on the next build. Student contributions go in
`notebooks/contrib-dev/`.
:::

---

## 12. Model diagnostics

When a model will not solve, or solves to something implausible, reach for the IDAES diagnostics
toolbox before you start deleting constraints at random.

```python
from idaes.core.util.diagnostics_tools.diagnostics_toolbox import DiagnosticsToolbox

dt = DiagnosticsToolbox(m)
dt.report_structural_issues()  # before solving: degrees of freedom, empty constraints, unit consistency
dt.report_numerical_issues()  # after solving: bad scaling, variables at bounds, near-parallel constraints
```

`report_structural_issues()` costs seconds and catches the most common modelling errors — the wrong
number of degrees of freedom, a variable that appears in no constraint, an inconsistency in units.
Run it in the cell before your first solve.

When the structural report flags a **degenerate** model — more constraints active at the solution
than the problem can independently support — the degeneracy hunter identifies which ones:

```python
dh = dt.prepare_degeneracy_hunter(solver="cbc")
dh.report_irreducible_degenerate_sets()
```

Each *irreducible degenerate set* is a smallest group of constraints that are linearly dependent at
the solution. That is usually a modelling mistake: a balance written twice in different units, or a
specification that the rest of the model already implies.

We cover this material in **[](../notebooks/7/degeneracy_hunter.ipynb)**, alongside constraint
qualifications — that is where it belongs conceptually. LICQ says the active constraint gradients
must be linearly independent; the degeneracy hunter is the computational tool that tells you when
they are not.

:::{note}
Some existing notebooks import `DiagnosticsToolbox` from `idaes.core.util.model_diagnostics`. That
path still works but is deprecated as of IDAES 2.12. Use the path shown above in new work.
:::

---

## 13. Figures

Figures follow the course figure style, which is documented once, in
[`figures/README.md`](https://github.com/ndcbe/optimization/blob/main/figures/README.md). Do not
re-derive it here. The short version:

```python
import matplotlib.pyplot as plt

plt.style.use("../../figures/dowling.mplstyle")  # from notebooks/<n>-dev/
```

On Colab, where only the notebook is present, use the raw URL form given in that README.

Three rules from it that catch people out, because they are not things a style file can enforce:

- **At most four series per axes**, and every series carries a non-colour identity (linestyle,
  marker, or a direct label). Students print the handouts in black and white.
- **Label the axes, with units.** Bold, per the style file — that is automatic.
- **Never a screenshot of mathematics.** Use LaTeX in a markdown cell.

`helper.set_plotting_style()` in the setup cell sets sensible font sizes and line widths. It is not
the same thing as `dowling.mplstyle`, which is the full house style; for a figure that will appear
in the course pack, use `dowling.mplstyle`.

---

## 14. Formatting

Run [`black`](https://black.readthedocs.io/) on every notebook before you submit it. It is already
in `environment.yml`.

```bash
black notebooks/contrib-dev/my_notebook.ipynb
```

That settles line length, quote style, spacing around operators and trailing commas, so nobody has
to review them.

:::{warning}
`black` reformats the code *inside* `### BEGIN SOLUTION` blocks too. That is fine, but check
afterwards that the markers are still on their own lines and still paired.
:::

Beyond `black`:

- **Comment the modelling, not the Python.** `# [MWh] = [MW] * [1 hr]` above an energy balance is
  worth ten lines of `# loop over t`.
- **Every model-building function gets a docstring** listing arguments and returns.
- Organise the notebook with `##` sections and `###` subsections. Avoid `####` — it renders badly on
  this site.
- The first markdown cell is `# Informative Title`, followed by
  `**Prepared by:** Your Name (netid@nd.edu, 2026)`. See [](contribute.md).

---

## Checklist

Run through this before you submit an assignment or open a pull request.

- [ ] `import pyomo.environ as pyo`; no `from pyomo.environ import *`
- [ ] The Colab setup cell is the first code cell, verbatim, with `import sys` inside it
- [ ] Every random number generator is seeded
- [ ] The model is built by a function that returns a `ConcreteModel`
- [ ] Index sets are `pyo.Set` / `pyo.RangeSet`, named in UPPER CASE
- [ ] `domain=` not `within=`; known bounds in `bounds=`
- [ ] Constraints use the `@m.Constraint` decorator and are named for what they mean
- [ ] LP and MILP models call `pyo.SolverFactory("appsi_highs")`, not `"glpk"`; `tee=` is on `solve()`
- [ ] **Every `solve()` is followed by a termination-condition check before any `pyo.value()`**
- [ ] `### BEGIN SOLUTION` / `### END SOLUTION` markers are bare, paired, and inside code cells
- [ ] Data in `notebooks/data/`, images in `media/`, both committed, case matched exactly
- [ ] Figures use the house style; at most four series per axes
- [ ] `black` has been run
- [ ] The notebook runs top to bottom from a fresh kernel — **Restart & Run All**

That last one is not a formality. Of the 66 notebooks on this site, 26 did not pass it in August
2026.
