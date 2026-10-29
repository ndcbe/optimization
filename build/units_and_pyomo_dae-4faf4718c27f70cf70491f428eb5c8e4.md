# Units in `Pyomo.dae` Models

Pyomo can check that your model is dimensionally consistent. This catches a whole
class of modeling mistakes -- a missing factor of 1000, a rate constant written per
hour and used per second, a term that was normalized on paper and then un-normalized
in code -- **before** you ever call a solver.

For a steady-state model the recipe is simple: declare `units=` on every `Var` and
`Param`, then call

```python
from pyomo.util.check_units import assert_units_consistent

assert_units_consistent(m)
```

Dynamic models built with `Pyomo.dae` have one important wrinkle. This page explains
it once so the notebooks in this section do not have to repeat it.

## The rule: assert *before* you discretize

```{warning}
`assert_units_consistent` **passes on a units-correct `Pyomo.dae` model before
discretization and fails after it**, whenever the `ContinuousSet` represents a
physical quantity such as time in seconds.

Put the assertion in your model-building function, *before*
`TransformationFactory("dae.finite_difference")` or `"dae.collocation"`.
```

Here is the whole story in ten lines. Run it yourself:

```python
import pyomo.environ as pyo
import pyomo.dae as dae
from pyomo.util.check_units import assert_units_consistent

u = pyo.units

m = pyo.ConcreteModel()
m.t = dae.ContinuousSet(bounds=(0, 10))               # seconds... we think
m.x = pyo.Var(m.t, initialize=1.0, units=u.m)
m.dxdt = dae.DerivativeVar(m.x, wrt=m.t, units=u.m / u.s)
m.k = pyo.Param(initialize=0.5, units=1 / u.s)

@m.Constraint(m.t)
def ode(m, t):
    return m.dxdt[t] == -m.k * m.x[t]

assert_units_consistent(m)                            # passes

pyo.TransformationFactory("dae.finite_difference").apply_to(m, nfe=5)

assert_units_consistent(m)                            # raises
```

The second call raises:

```text
InconsistentUnitsError: Error in units found in expression:
  dxdt[2.0] - 0.5*(x[2.0] - x[0]): meter / second not compatible with meter.
```

## Why it fails

The model above is dimensionally *right*. The **discretization equation** that Pyomo
writes for you is what fails the check.

A backward-difference approximation of $\frac{dx}{dt}$ at time $t_i$ is

$$
\dot{x}_i \approx \frac{x_i - x_{i-1}}{\Delta t}.
$$

Pyomo evaluates $1/\Delta t$ numerically and writes the constraint as

```text
dxdt[2.0] == 0.5*(x[2.0] - x[0])
```

That `0.5` **is** the reciprocal $\Delta t$. It should carry units of $\mathrm{s}^{-1}$.
It does not, because a `ContinuousSet` holds plain Python floats and **cannot carry
units at all**. So Pyomo sees a dimensionless coefficient times a length, i.e. a
length, set equal to a `DerivativeVar` declared in $\mathrm{m}/\mathrm{s}$ -- and
correctly reports that meters are not meters per second.

This is [Pyomo issue #1790](https://github.com/Pyomo/pyomo/issues/1790), *"Add units
support to `ContinuousSet` / `Pyomo.dae`"*, which is **still open**. Nothing is wrong
with your model, and nothing is wrong with the discretization arithmetic. The units
container simply has no place to record what the time domain is measured in.

The same limitation shows up in three other places you will meet in these notebooks:

* **`dae.collocation` fails too**, not just `dae.finite_difference`. The collocation
  coefficients are reciprocal-time in exactly the same way.
* **`m.Integral` returns the wrong dimension.** Integrating a squared height error
  $(h - r)^2$ over time should give $\mathrm{m}^2\,\mathrm{s}$; Pyomo reports
  $\mathrm{m}^2$, because the quadrature weights are dimensionless for the same
  reason. The objective is still *internally* consistent, so the check passes.
* **The raw index `t` inside a rule is a bare `float`.** When you write a path
  constraint or a reference trajectory such as `8*(t - 0.5)**2` or `2.5*t`, that `t`
  is the Python number Pyomo passed into your rule, not a quantity. You have to
  multiply the result by the units you intend.

## Two things the check does *not* catch

```{note}
`assert_units_consistent` inspects **expressions** -- constraints, objectives,
expressions. It does **not** check `Var` bounds, nor values passed to `.fix()`.
```

Both of the following pass the check even though the bare numbers are being read as
kelvin and as meters per second:

```python
m.Th = pyo.Var(m.t, units=u.K)
m.Th[0].fix(300)                       # 300 what? Not checked.

m.v = pyo.Var(m.t, bounds=(-2, 5), units=u.m / u.s)   # bounds not checked.
```

So units are a strong check on your *equations* and no check at all on your *numbers*.
Keep writing the units in a comment next to any bare bound or fixed value.

## Two ways to live with it

### 1. Assert early, then discretize

This is what the notebooks in this section do. The assertion goes inside the
model-building function:

```python
def create_model():
    m = pyo.ConcreteModel()
    ...
    # Units are checked here, on the continuous model, because the
    # discretization equations added below cannot pass the check.
    # See https://github.com/Pyomo/pyomo/issues/1790
    assert_units_consistent(m)
    return m


m = create_model()
pyo.TransformationFactory("dae.collocation").apply_to(m, nfe=15, ncp=3)
```

You lose nothing. The discretization equations are generated by Pyomo, not by you,
so they are not where your modeling errors live. Checking the continuous model checks
everything you actually wrote.

### 2. Scale time so the `ContinuousSet` is dimensionless

The time-scaling trick used in [](./PyomoDAE_car.ipynb) has a side benefit that is
worth noticing. Substituting $t = \tau \, t_f$ with $\tau \in [0, 1]$ makes the
`ContinuousSet` genuinely dimensionless, and moves $t_f$ into an ordinary Pyomo `Var`
carrying `units.s`. Now

$$
\frac{dx}{d\tau} = t_f \, v
$$

has $\mathrm{m}$ on the left and $\mathrm{s} \cdot \mathrm{m}/\mathrm{s} =
\mathrm{m}$ on the right, and the finite-difference coefficient *should* be
dimensionless -- which is exactly what Pyomo makes it. **These models pass the check
both before and after discretization.**

Do not read too much into that. It is a happy accident of a modeling choice made for
other reasons (a free final time), not a fix.

## How IDAES works around it

If you go on to use [IDAES](https://idaes-pse.readthedocs.io/), you will meet the
production-grade version of this workaround. `FlowsheetBlock` takes a `time_units`
configuration argument, and for a dynamic flowsheet it is **mandatory** -- omit it and
you get

```text
ConfigurationError: fs - no units were specified for the time domain.
Units must be specified for dynamic models.
```

IDAES carries the time units *out of band*, on the flowsheet, precisely because the
`ContinuousSet` cannot hold them. That is issue #1790 seen from the other side.

## A common trap: `DerivativeVar` does not inherit units

`DerivativeVar` defaults to **dimensionless**. It does *not* infer its units from the
state variable it differentiates:

```python
m.x = pyo.Var(m.t, units=u.m)
m.dx = dae.DerivativeVar(m.x, wrt=m.t)

pyo.units.get_units(m.dx[0])      # dimensionless -- not m/s!
```

A model can therefore look thoroughly units-annotated and still fail the very first
check. Always declare the derivative's units explicitly:

```python
m.dx = dae.DerivativeVar(m.x, wrt=m.t, units=u.m / u.s)
```

When the domain is a dimensionless scaled time $\tau$, the derivative has the *same*
units as the state:

```python
m.tau = dae.ContinuousSet(bounds=(0, 1))
m.x = pyo.Var(m.tau, units=u.m)
m.dx = dae.DerivativeVar(m.x, wrt=m.tau, units=u.m)      # m per dimensionless tau
```

## Where units genuinely cannot be added

Not every model in this section carries units, and that is deliberate. Two honest
reasons appear here:

* **Deliberately normalized models.** [](./DAE_background.ipynb) studies index
  reduction on a pendulum with mass and length set to unity, so the constraint is
  written $x^2 + y^2 = 1$ against a dimensionless literal. The tension variable $T$
  in that formulation is not a force but a force divided by $m L$, with units
  $\mathrm{s}^{-2}$. Restoring dimensions would rewrite the very equations whose
  *algebraic structure* is the lesson.
* **Abstract test problems.** The optimal control problem in
  [](./DAE_numeric_integration.ipynb) comes from the Pyomo book, where $x_1$, $x_2$,
  $x_3$ are mathematical states with no physical referent. Any units assigned to them
  would be invented, and inventing units is worse than omitting them -- it makes a
  check that looks meaningful and is not.

The rule of thumb: **add units when the quantities are physical and the check earns
its keep. Say so plainly when they are not.** A forced, arbitrary set of units is a
false negative waiting to happen.
