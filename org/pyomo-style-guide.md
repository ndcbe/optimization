# Pyomo Style Guide

This is the house style for every notebook on this website — the ones Prof. Dowling writes, the ones
you write for the [Pyomo Mini Project](project1.md), and the ones you
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

## 2a. The five-step spine

A notebook that applies optimization to a problem is organised on the same five steps used in
lecture, as `##` headings, in this order and with these names:

```
## Step 0: Problem statement          what is being decided, and why
## Step 1: Mathematical model         sets, parameters, variables, objective, constraints
## Step 2: Degree of freedom analysis variables minus equality constraints
## Step 3: Pyomo implementation       the build function, and nothing else
## Step 4: Analyze results            solve, tabulate, interpret
```

The point is that Step 2 sits between the mathematics and the code. **Do not implement a model in
Pyomo until it is written down and counted** — most mistakes in an optimization project are made at
the formulation step, and they are far cheaper to find on paper.

**Variants of one problem are `###` subsections, not extra steps.** When a notebook compares several
options, scenarios or formulations, the *steps stay the top-level spine* and each variant gets an
`###` subsection inside every step, with the same name each time:

```
## Step 1: Mathematical model
### Option 1: business as usual
### Option 2: a second truck
### Option 3: pool the remote farms
## Step 2: Degree of freedom analysis
### Option 1: business as usual
...
```

so that a reader can go down a step comparing the variants, or across the variants following one.
[](../notebooks/1/Milk-Pooling.ipynb) is the worked template. Two things it does that are the
substance of the convention, not decoration:

- **One build function, taking the variant as an argument.** Three options, one
  `create_milk_model(local, pooled)`. If two build functions differ by a set or a flag, they are one
  function, and saying so is usually the most interesting sentence in the notebook.
- **Steps 2 and 3 check each other.** Step 2 counts by hand; Step 3 prints the same counts out of
  Pyomo. A disagreement is a real finding, in either direction.

Do not pad. Variants rarely deserve equal space — in the template, Options 1 and 2 get a paragraph
each and Option 3 gets the whole of the hard analysis. **Manufactured symmetry is worse than an
honest two-line subsection.**

:::{note}
**When this does not apply.** The spine is for notebooks that *solve a problem*. Do not force it
onto:

- **tutorials and reference notebooks**, whose organising principle is the software, not a problem —
  [](../notebooks/1/Pyomo-Nuts-and-Bolts.ipynb) is arranged by Pyomo component and should stay that
  way;
- **theory and algorithm notebooks**, where there is no single model to count;
- **notebooks with one model and no variants**, which keep the five steps but take no `###`
  subsections at all — the subsection layer exists only to hold the variants.

Existing notebooks are not being converted wholesale. Use the spine for new work, and when a
notebook is being substantially rewritten anyway.
:::

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

### Names are verbose. The mathematical symbol goes in a comment, not in the name.

It is tempting to name a component after the symbol in the notes — `milp.abar` for $\bar{a}_r$ — so
that the code and the formulation line up character for character. **Don't.** Research code, which is
what you will be reading and writing after this course, uses names you can say out loud, and a reader
who does not have the handout open beside them has nothing else to go on.

Put the correspondence in a comment instead, on **one line**, giving the **meaning**, the **symbol
from the notes**, and the **units**:

```python
# YES
# Marginal (linear) cost of reactor r, abar_r [$/kmol]
milp.reactor_cost_linear = pyo.Param(milp.REACTORS, initialize=cost_coefficient1)
```

```python
# NO — the name is the symbol, so the reader has to go and find the notes
milp.abar = pyo.Param(milp.REACTORS, initialize=cost_coefficient1)
```

:::{warning}
**That comment has to carry the units, and it has to fit on one line.**
`scripts/extract_pyomo_code.py`, which lifts a tagged cell into the LaTeX course pack, strips every
comment *except* the ones with a unit annotation in them. A gloss with no `[...]` is deleted on the
way into the handout, and the symbol correspondence is lost exactly where a student reading the pack
without the notebook needs it most. A unit comment split over two lines loses its second line the
same way.
:::

Long names are not an excuse for long lines: `black` wraps them, and the handout listings are set at
`\footnotesize`, which fits about 94 characters. Decorators (§6) shorten the lines that matter.

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
def lower(b, f):
    return b.servings[f] >= 0


@m.Constraint(m.FOODS)
def upper(b, f):
    return b.servings[f] <= 10
```

Bounds that depend on a decision, or that you want a dual variable for, are genuine constraints —
write them as constraints.

---

## 6. Constraints: decorators are the default

Pyomo offers two equivalent ways to attach a constraint rule. **Write the decorator.** It is the
default for every model in this course; the `rule=` form is the older one, and you will meet it in the
Pyomo book and in most existing research code, so you need to be able to *read* it. The two build
identical models. [](../notebooks/1/LP.ipynb) writes the same constraint both ways, once, side by side.

```python
# YES — house style
@m.Constraint(m.HORIZON)
def energy_balance(b, t):
    if t == b.HORIZON.first():
        return b.E[t] == b.E0 + b.charge[t] * b.sqrt_eta - b.discharge[t] / b.sqrt_eta
    return b.E[t] == b.E[t - 1] + b.charge[t] * b.sqrt_eta - b.discharge[t] / b.sqrt_eta


@m.Objective(sense=pyo.minimize)
def total_cost(b):
    return sum(b.price[t] * (b.charge[t] - b.discharge[t]) for t in b.HORIZON)
```

```python
# OLDER FORM — read it, don't write it
def energy_balance_rule(m, t):
    if t == m.HORIZON.first():
        return m.E[t] == m.E0 + m.charge[t] * m.sqrt_eta - m.discharge[t] / m.sqrt_eta
    return m.E[t] == m.E[t - 1] + m.charge[t] * m.sqrt_eta - m.discharge[t] / m.sqrt_eta


m.energy_balance = pyo.Constraint(m.HORIZON, rule=energy_balance_rule)
```

The decorator wins because the name is written once instead of three times (function name, `_rule`
suffix, component name), the component name cannot drift out of sync with the function that defines
it, and the lines are shorter — which matters once a model has to fit in a handout. The same
decorators exist for `@m.Objective`, `@m.Expression`, `@m.Disjunction`, `@m.Param` and `@m.Integral`.

### Name the first argument `b`, not `m`

A decorated rule is handed the **block** Pyomo is currently building, not the variable you happen to
have called `m`. Call it `b` and use it for every component you reference inside the rule.

```python
# YES — `b` is the block, and every reference goes through it
@model.Constraint(model.CIRCLES)
def right_x_con(b, c):
    return b.x[c] <= b.box_width - b.R[c]
```

```python
# NO — the parameter is `m`, but the body reaches for the enclosing `model`
@model.Constraint(model.CIRCLES)
def right_x_con(m, c):
    return m.x[c] <= model.box_width - model.R[c]
```

The wrong version usually *runs*, because the enclosing name is in scope — and then breaks the day the
rule is reused on a sub-block, or silently builds the wrong model when two models are in flight. This
is not hypothetical: exactly that mismatch was found and fixed in a notebook on this site in August
2026. Naming the argument `b` makes the mistake visible while you are typing it.

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

For a single, non-indexed constraint whose expression fits on one line, `expr=` is clearer than any
rule:

```python
m.periodic_boundary = pyo.Constraint(expr=m.E0 == m.E[m.HORIZON.last()])
```

Once the expression is a `sum(...)` that has to wrap, go back to the decorator — `@m.Constraint()`
with no index set is the scalar form:

```python
@m.Constraint()
def pool_balance(b):
    return sum(b.x[r] for r in b.REMOTE) == sum(b.y[k] for k in b.CUSTOMERS)
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

**HiGHS is the course default for anything linear.** GLPK was the default through Fall 2024 and
**CBC through Fall 2026**; both have been retired. HiGHS is faster, is actively developed, and
installs everywhere with `pip install highspy` — no `apt-get`, no separate executable — so it works
on Colab, macOS and Windows identically. If you are reading an older notebook that calls
`pyo.SolverFactory("glpk")` or `pyo.SolverFactory("cbc")`, replace it with
`pyo.SolverFactory("appsi_highs")`.

:::{note}
**There is exactly one sanctioned exception in this repo**, and it is not a style choice:
`notebooks/7-dev/NLP-Diagnostics.ipynb` still calls CBC, because IDAES's legacy `DegeneracyHunter`
raises when its internal MILP is infeasible under HiGHS. See the fourth bullet below. A notebook
whose *subject* is comparing solvers — `Sudoku_Solver.ipynb` benchmarks HiGHS against CBC — is also
free to name others; that is the point of it.
:::

```python
# YES
solver = pyo.SolverFactory("appsi_highs")
results = solver.solve(m, tee=True)
assert pyo.check_optimal_termination(results)
```

Details that bite — the last three were all found switching this repo off CBC:

- **`tee` is a keyword of `solve()`, not of `SolverFactory()`.** The shell-based solvers (`glpk`,
  `cbc`, `ipopt`) silently swallow `SolverFactory("glpk", tee=True)` and print nothing;
  `SolverFactory("appsi_highs", tee=True)` raises instead. Put `tee=` on the `solve()` call, where it
  has always belonged.
- **The results object is the ordinary Pyomo one.** In Pyomo 6.10, `SolverFactory("appsi_highs")`
  returns a legacy-compatible wrapper, so `pyo.check_optimal_termination(results)` and
  `results.solver.termination_condition` work exactly as in §7. You only need the APPSI-native
  `results.termination_condition` form if you construct the solver directly from
  `pyomo.contrib.appsi`, which this course does not do.
- 🔴 **On an infeasible model HiGHS RAISES, where a shell solver returns.** This is the one real
  behavioural difference. `SolverFactory("cbc").solve(m)` on an infeasible model hands back a
  warning-status results object you can branch on; `appsi_highs` raises `RuntimeError` from inside
  `solve()`, because it is asked to load a solution that does not exist. **If a failed solve is a
  possible or intended outcome — a branch-and-bound node, an infeasibility demo, a library that
  probes with MILPs — pass `load_solutions=False` and load explicitly:**

  ```python
  results = opt.solve(m, load_solutions=False)
  if pyo.check_optimal_termination(results):
      m.solutions.load_from(results)   # only now are the variables populated
      print(pyo.value(m.obj))
  elif results.solver.termination_condition == pyo.TerminationCondition.infeasible:
      print("infeasible")
  ```

  This is what forces the CBC exception in `NLP-Diagnostics.ipynb`: IDAES's legacy
  `DegeneracyHunter` makes the bare `solver.solve(milp, tee=tee)` call internally, so there is no
  way to pass the flag from the notebook. The current `DiagnosticsToolbox` API is fine.
- **`tee=True` shows you nothing in Jupyter.** HiGHS writes its log to the process's stdout rather
  than through Python, so the notebook never captures it — the cell just renders empty. Print the
  objective yourself instead of relying on the solver log.

HiGHS may report a binary variable as `-0.0` rather than `0.0`. Compare with a tolerance
(`if pyo.value(m.x[i]) >= 0.5:`), never with `== 0`.

**Format numbers before printing them.** CBC's shell interface rounded its solution file to about 8
decimals, which flattered every `print(pyo.value(x))` in the repo. HiGHS returns full double
precision, so the same line now prints `83.75000000000003`, `6.999999999999998`, or an integer
vehicle count of `10.99999999999997`. None of that is information. Use `f"{...:.4g}"`, `round()` for
a value you know is integral, and snap to zero below the feasibility tolerance
(`if abs(gap) < 1e-9: gap = 0.0`) rather than publishing `1.1e-16`.

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
- [ ] A problem-solving notebook uses the five-step spine, with variants as `###` subsections
- [ ] Index sets are `pyo.Set` / `pyo.RangeSet`, named in UPPER CASE
- [ ] `domain=` not `within=`; known bounds in `bounds=`
- [ ] Constraints and objectives use the `@m.Constraint` / `@m.Objective` decorator, not `rule=`
- [ ] Every decorated rule names its first argument `b` (the block), and its body goes through `b`
- [ ] Component names are verbose; the symbol from the notes and the **units** are in a one-line comment
- [ ] LP and MILP models call `pyo.SolverFactory("appsi_highs")`, not `"glpk"`; `tee=` is on `solve()`
- [ ] **Every `solve()` is followed by a termination-condition check before any `pyo.value()`**
- [ ] `### BEGIN SOLUTION` / `### END SOLUTION` markers are bare, paired, and inside code cells
- [ ] Data in `notebooks/data/`, images in `media/`, both committed, case matched exactly
- [ ] Figures use the house style; at most four series per axes
- [ ] `black` has been run
- [ ] The notebook runs top to bottom from a fresh kernel — **Restart & Run All**

That last one is not a formality. Of the 66 notebooks on this site, 26 did not pass it in August
2026.
