# Pyomo Mini Project

Summary: with a partner, formulate, implement, and defend an optimization model of your own choosing.

Worth **10% of the course grade**. See the [semester calendar](./calendar.md) for the due date.

## What changed for Fall 2026, and why

A capable AI coding assistant will turn a clear problem statement into a working Pyomo model in a
couple of minutes. That is a real change, and pretending otherwise would waste your semester. So the
code is no longer the scarce thing, and this project no longer grades it as though it were.

What an AI tool cannot do for you is **decide what to model**, **justify the formulation you chose over
the ones you rejected**, **interpret the answer**, and — the hard one — **notice when the answer is
wrong**. Those four things are what this project is now about, they are what the two midterms and the
final will ask you to do without a computer, and they are what practicing engineers are actually paid
for.

You may use AI tools throughout. See the
[Artificial Intelligence Policy](./syllabus.md#artificial-intelligence-policy), and note that this
project asks you to *disclose and critique* that use as part of the deliverable.

## Learning Goals

By completing this project, you will:
* Formulate an optimization problem on paper, in set notation, before you write any code
* Perform and interpret a degree-of-freedom analysis
* Defend a modelling choice against a specific alternative
* Develop proficiency in Python and Pyomo
* Analyze and interpret optimization results, and check whether they are believable
* Make publication quality figures
* Critique output from an AI tool rather than trusting it

## Choosing a Problem

Select an optimization problem of interest to your team. Recommendation: choose a *simple* optimization
problem from the literature or a textbook. You want a problem where all of the input data and
parameters are available and a model has already been formulated. Recommended resources:
* [Hands-On Mathematical Optimization with Python](https://mobook.github.io/MO-book/intro.html)
* [ND Pyomo Cookbook](https://jckantor.github.io/ND-Pyomo-Cookbook/README.html)
* [Pyomo — Optimization Modeling in Python](https://link.springer.com/book/10.1007/978-3-030-68928-5)
* [Applications of Optimization with Xpress-MP](https://examples.xpress.fico.com/example.pl#mosel_app)
* [Introduction to Stochastic Programming](https://link.springer.com/book/10.1007/978-1-4614-0237-4)

**Your project must go beyond the source material.** If you reproduce an example from a textbook, you
must perform an additional analysis that yields an insight the reference does not discuss. If your
source already includes a Pyomo implementation, you must extend the model — this ensures everyone gets
genuine Pyomo practice. The same applies if your problem is one we studied in class or in a course
notebook: you may use it, but reproducing the class treatment is not a project.

```{tip}
Small and finished beats ambitious and broken. A ten-variable model you can defend line by line will
earn a better grade than a two-hundred-variable model you cannot explain. Pick something you can
formulate on one page.
```

## Deliverable: a Jupyter notebook in four parts

Your notebook follows **the same four steps we use for every model in this course**: set notation,
degree-of-freedom analysis, results, then Pyomo code. That order is deliberate and it is the order the
lecture handouts use. The code comes last because it is the consequence of the first three steps, not a
substitute for them.

Open with a title, `**Prepared by:**` line, and one or two paragraphs of motivation that a reader
outside your field can follow. Describe your data and where it came from. Include a diagram if one
helps explain the problem — see [](contribute.md) and [](pyomo-style-guide.md) for formatting.

### Part 1 — Formulation in set notation

Typeset the complete model in LaTeX, in a markdown cell, organized exactly as the handouts do it:

* **Sets** — name each index set and say what it indexes
* **Parameters** — every one, **with units**
* **Variables** — every one, with units and domain
* **Constraints** — grouped and *named for the physics or the requirement they express*, not `con1`
* **Objective** — with its sense and its units

Write it **in symbols, not in numbers**: $|\mathcal{T}|$ timesteps, not 168 timesteps. Symbolic
formulations stay valid when the data changes, and they are what you will be asked for on the exams.

No screenshots of mathematics. Ever.

### Part 2 — Degree-of-freedom analysis

Count your model with the six-row table we use in class, **in symbols**:

| Count | Number |
| --- | --- |
| continuous variables | |
| discrete or binary variables | |
| linear equality constraints | |
| nonlinear equality constraints | |
| linear inequality constraints | |
| nonlinear inequality constraints | |

There is **no bottom-line total, deliberately**. Netting inequalities and bounds against variables
requires knowing which inequalities are *active* at the solution, and we do not have the tools for that
until the constrained-optimization lectures. Count; do not subtract.

Then **classify your problem** and say how you know: LP, MILP, NLP, MINLP? Convex? Are any constraints
differential? Are any parameters uncertain? Finally, report the counts your Pyomo model actually
produces (`m.pprint()` or the IDAES diagnostics toolbox) and **reconcile them with your hand count**.
If the two disagree, one of them is wrong, and finding out which is the single most useful debugging
habit in this course.

### Part 3 — Results, interpretation, and whether to believe them

* At least one **publication quality figure** of the solution — labeled axes, units, appropriate
  significant figures
* A discussion of what the solution *means* in the language of the original problem, not in the
  language of the solver
* **At least one defensible conclusion**, stated as a sentence someone could disagree with
* **A sanity check.** Show one independent reason to believe the answer: a limiting case you can solve
  by hand, a bound the objective must respect, a conservation check, a comparison to the reference.
* **A failure mode.** Name one plausible error that would make your answer wrong while the solver still
  reported `optimal`, and say how a reader could rule it out.

That last pair is the heart of the assignment. A solver returning `optimal` is a statement about the
model you wrote, not about the problem you meant.

### Part 4 — Pyomo implementation

The model, built by a function, following [](pyomo-style-guide.md) — including the solver termination
check before any `pyo.value()` call, a seeded random number generator if anything is random, and
comments *in your own words*.

## Deliverable: modelling choices, defended

A short section — half a page is plenty — titled **Modelling Choices**. Identify **three decisions** you
made in Part 1 that a reasonable person could have made differently. For each one:

1. State the choice.
2. State the specific alternative you rejected.
3. Say what the alternative would have cost or bought you — a different problem class, more variables,
   a nonconvexity, a loss of fidelity, a longer solve.

Good candidates: modelling a limit as a bound versus a constraint; binary variables versus a
disjunction; a linearization versus the nonlinear form; the time discretization; which parameters you
treated as certain.

Also state, in a short paragraph, **how your project goes beyond the reference material**.

## Deliverable: AI disclosure and critique

Every submission ends with a section titled **AI Disclosure**, whether or not you used an AI tool.

If you used one, report:
* **Which tool**, and which parts of the project you used it for
* **What it got wrong.** Something will be wrong: a hallucinated Pyomo keyword, a constraint with the
  inequality reversed, a plot with unlabeled axes, a confident explanation of a result that does not
  follow, an objective that quietly changed units.
* **How you knew it was wrong** — this is the graded part

If you did not use an AI tool, write one sentence saying so. That is a complete and full-credit answer.

```{warning}
"It worked, so I did not check" is not an answer to the third question, and a submission whose AI
critique reports nothing wrong will be read very carefully. Two contributed notebooks already on this
website ran without error for years while being, respectively, **infeasible** and **unbounded** — see
§7 and §8 of [](pyomo-style-guide.md). Running is not the same as correct.
```

Per the [Artificial Intelligence Policy](./syllabus.md#artificial-intelligence-policy), your code
comments and your answers to discussion questions must be **in your own words**, and you are
responsible for understanding everything you submit. The exams are in person and without a computer.

## Deliverable: a three-minute recorded defence

Submit a **three-minute screen recording** with your notebook. There is no class session reserved for
project presentations this semester — every meeting is a lecture or an exam — so this replaces the
in-class talk.

Show your notebook and say, in your own voice:
* what you are optimizing, and what the decision variables are
* one modelling choice and the alternative you rejected
* one result and why you believe it

**Both partners speak.** Slides are not required and neither is polish; a screen recording with audio is
exactly what is wanted. Reading a script aloud defeats the purpose.

## References

A reference list covering **every** source of data, models, figures, and code, in a citation style
standard for your field. Failure to disclose source material you used is an honor code violation.

## Grading

| Component | Weight |
| --- | --- |
| Formulation in set notation (Part 1) | 25% |
| Degree-of-freedom analysis and classification (Part 2) | 15% |
| Results, figures, interpretation, sanity check, failure mode (Part 3) | 25% |
| Modelling choices, defended | 15% |
| Pyomo implementation (Part 4) | 10% |
| AI disclosure and critique | 5% |
| Recorded defence | 5% |

**Yes, the implementation is 10%.** It either runs and follows the style guide or it does not; that is
the part a tool can help you with, so it is not where the points are. The other 90% is the work of
deciding what to model and knowing what the answer means.

You are graded as a pair, and **either partner must be able to explain any part of the submission.** If
you cannot defend a section, do not submit it.

## Contributing your notebook to the class website

Strong notebooks may be invited to join the class website as contributed examples. This is optional and
happens after grading, by pull request — see [](contribute.md). It is not part of the project grade, and
nothing is published without review.

## Checklist

Work down this list before you submit.

- [ ] Complete model typeset in LaTeX, in symbols, with units on every parameter and variable
- [ ] Constraints named for what they mean
- [ ] No screenshots of mathematics anywhere
- [ ] Six-row degree-of-freedom table, in symbols, with no total row
- [ ] Problem classified, with a reason
- [ ] Hand count reconciled against the model Pyomo actually built
- [ ] At least one publication quality figure — axes labeled, units, sensible significant figures
- [ ] At least one defensible conclusion
- [ ] A sanity check and a named failure mode
- [ ] Three modelling choices, each with the rejected alternative and what it would have cost
- [ ] A paragraph on how the project goes beyond the reference
- [ ] AI disclosure section present (even if it says "none")
- [ ] Every `solve()` followed by a termination check before any `pyo.value()`
- [ ] `black` has been run; the notebook passes **Restart & Run All** from a fresh kernel
- [ ] References for all data, models, figures, and code
- [ ] Three-minute recording, both partners speaking
