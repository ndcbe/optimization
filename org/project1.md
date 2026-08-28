# Pyomo Mini Project

```{warning}
**This is a draft assignment. It is still being updated for Fall 2026.**
```

Summary: choose a published optimization model from the literature. Use an AI tool to extract the
mathematical model from its source. Then **check the AI's work against the source, on paper, with a pencil.** Correct it,
implement it, and try to reproduce a published result.

Worth **10% of the course grade**. See the [semester calendar](./calendar.md) for the due date.

## What changed for Fall 2026, and why

The previous version of this project asked you to build a Pyomo model of a problem you chose. That was
mainly a programming assignment, and a programming assignment no longer measures much: a capable AI tool
turns a clear problem statement into a working Pyomo model in a couple of minutes.

So the code is not the assignment. **The assignment is the verification loop:**

1. An AI tool produces a plausible artifact --- a formulation, a degree-of-freedom analysis, an implementation.
2. You check that artifact against the primary source, by hand, the old fashioned way.
3. You correct it, and you can say exactly what was wrong and how you knew.

Step 2 is the one nobody does, and it is the entire point. A tool will hand you something that looks
right, reads fluently, and runs. **You are the one accountable for whether it is true.**

```{note}
You are **required** to use an AI tool on this project. That makes the
[Artificial Intelligence Policy](./syllabus.md#artificial-intelligence-policy) central rather than a
caveat: everything you submit is disclosed, and your own words are still your own words.
```

Before starting, read both the [Artificial Intelligence Policy](./syllabus.md#artificial-intelligence-policy)
and the [Collaboration Policy and Honor Code](./syllabus.md#collaboration-policy-and-honor-code).
This assignment adds more specific rules. Each stage is labeled:

* **No AI:** complete the stage without an AI tool.
* **AI required:** use an AI tool and retain the requested evidence.
* **AI permitted after independent work:** first make and record your own attempt; then you may use AI,
  provided you disclose and verify its contribution.

## Learning goals

By completing this project, you will:

* Read a published technical source closely enough to find what it does not say
* Extract a mathematical program from prose, and write it in set notation
* Perform and interpret a degree-of-freedom analysis on someone else's model
* Audit an AI tool's technical output against a primary source, and correct it
* Attempt a reproduction, and diagnose why one fails
* Judge what a source must report for its results to be reproducible at all

## Choosing a published model

Pick a citable, published source --- for example, a journal or conference paper, book, or technical
report --- that **contains a complete optimization model and numerical results you can analyze.** A
course notebook, blog post, or undocumented code repository is not a published model for this purpose.

### The test your source must pass

Before you commit, confirm all three:

1. **The model is printed in the source.** You can point to specific equations or clearly identified
   passages that give the objective, constraints, and definitions needed to reconstruct it.
2. **There is a numerical result you can name.** A specific table entry, a figure, or a number in the
   text that you intend to reproduce.
3. **The model is small enough to finish.** Roughly: the full model fits in under about thirty numbered
   equations, and the formulation fits on two pages in your own notation.

**Rejected by construction:** review and survey papers without a complete model; sources where the
optimization is done inside a commercial black box with no printed model; sources reporting only
qualitative results; sources whose model
is stated only as "we solved the standard formulation, see reference [14]".

```{tip}
Small and specific beats important and vague. A three-set, six-constraint scheduling model from a 2019
journal paper is a much better choice than a landmark paper with a forty-page appendix.
```

### If the source ships code

Published code is permitted and useful for validation, but it does not replace your implementation.
**Do not upload, paste, or otherwise share the published code with your AI agent.** Build your model from
the published document first. Only after your implementation is complete may you inspect and run the
published code to validate your model and investigate discrepancies.

### Where to look

Search the literature in your own area first; a source you have a reason to care about is easier to read
closely. If you need a starting point, these collections cite the papers their examples come from:

* [Hands-On Mathematical Optimization with Python](https://mobook.github.io/MO-book/intro.html)
* [ND Pyomo Cookbook](https://jckantor.github.io/ND-Pyomo-Cookbook/README.html)
* [Pyomo --- Optimization Modeling in Python](https://link.springer.com/book/10.1007/978-3-030-68928-5)
* [Applications of Optimization with Xpress-MP](https://examples.xpress.fico.com/example.pl#mosel_app)
* [Introduction to Stochastic Programming](https://link.springer.com/book/10.1007/978-1-4614-0237-4)

Follow the citation and read the original published source. The collection is the index, not the source.

### Proposal --- due Friday, October 2, 2026

**AI category: No AI.** This is your choice, motivation, and plan.

Post your proposal in the designated **Canvas Discussion by 5pm on Friday, October 2**. Earlier posts are
strongly encouraged: everyone can see what classmates are studying, find shared interests, and avoid
unintended overlap.

Keep the proposal to less than one page and answer these four questions concisely:

1. Which optimization model from the published literature do you want to analyze? Give the complete
   citation and identify the equations or passages containing the model and the result you will target.
2. Why did you choose this model?
3. Do you have all necessary input data? If not, how will you obtain it quickly? List likely sources and
   any assumptions you expect to make.
4. What do you hope to learn by completing this mini project?

A bulleted response to each question is welcome. A few sentences or a short paragraph per question is
also fine.

Posting is not an approval process, and you do not need explicit permission to continue. The instructor
will contact you if there are concerns about scope, missing information, or substantial overlap with
another project.

## The steps

### Step 1 --- Read the source on paper

**AI category: No AI.**

**Print it. Read it with a pencil or a highlighter in your hand.** Mark the equations, the parameter
definitions, the data sources, and the result you plan to reproduce. Mark the places you do not follow.

Keep this copy. It is where your questions in Step 2 come from.

### Step 2 --- Interrogate the source with an AI tool

**AI category: AI required.**

Give the source to an AI tool and ask it **at least five clarifying questions that you drafted yourself,**
from your marked-up copy. Questions about this source, not questions about optimization in general.

Good questions come from the margins: *what are the units of $\alpha$ in equation (7)?* --- *is the
capacity limit per period or cumulative?* --- *equation (12) has an index $j$ that never appears in the
set definitions; what is it?*

Submit the questions and the full transcript.

### Step 3 --- Reflect on the interaction

**AI category: No AI.** Write this reflection yourself after reviewing the transcript.

A short paragraph. What did the tool do well? Where did it fail, stall, or make something up? Did it
answer a question the source does not actually answer, and if so, how did you notice?

One honest paragraph is worth more than a page of praise.

### Step 4 --- Extract the model with the AI tool, and export a report

**AI category: AI required.**

Working with the tool, extract the optimization problem from the source and put it in **set notation, in
the form we use in class:**

* **Sets** --- each index set, and what it indexes
* **Parameters** --- every one, **with units**
* **Variables** --- every one, with units and domain
* **Constraints** --- grouped and named for the physics or requirement they express, not `con1`
* **Objective** --- with its sense and its units

In **symbols, not numbers**: $|\mathcal{T}|$ periods, not 168 periods.

Then perform a **degree-of-freedom analysis** with the six-row table, counted in symbols:

| Count | Number |
| --- | --- |
| continuous variables | |
| discrete or binary variables | |
| linear equality constraints | |
| nonlinear equality constraints | |
| linear inequality constraints | |
| nonlinear inequality constraints | |

There is **no bottom-line total, deliberately.** Netting inequalities and bounds against variables
requires knowing which inequalities are *active* at the solution, and we do not have the tools for that
until the constrained-optimization lectures. Count; do not subtract.

Also classify the problem and say how you know: LP, MILP, NLP, MINLP? Convex? Any differential
constraints? Any uncertain parameters?

Iterate with the tool until the analysis is coherent. Then **ask it to export a report** documenting the
model and the degree-of-freedom analysis.

**Submit that report exactly as the tool produced it.** Do not clean it up. It is the "before" half of
the evidence, and without it there is no way to see what you corrected.

### Step 5 --- Check the report against the source, in pencil

**AI category: No AI.**

**Print the report. Sit down with it and the printed source. Go through it by hand.**

You are checking, line by line:

* Does every set in the report exist in the source, with the same meaning?
* Does every constraint in the report correspond to an equation in the source --- and does every equation
  in the source appear in the report?
* Are the inequality directions right? Are any $\le$ and $\ge$ swapped?
* Are the sums over the right index sets?
* Are the units consistent, and do they match the source's?
* Are the six counts right? Recount them yourself.
* Did the tool invent a constraint the source does not have, or quietly drop one it does?

Mark every correction on the printout. Then **scan or photograph the annotated pages and submit them.**

```{warning}
**A clean printout with no marks scores poorly.** Finding nothing is almost always evidence of not
looking. Every AI-extracted formulation that has been checked carefully in the preparation of this course
had something wrong with it --- a dropped constraint, a sum over the wrong set, an index that does not
exist, a variable count off by a factor of two.

This is the deliverable that cannot be produced by a tool, and it is weighted accordingly.
```

### Step 6 --- Correct it, and typeset the corrected model yourself

**AI category: AI permitted after independent work.** Decide and record every technical correction from
your comparison with the source before asking AI for help. AI may help with formatting after that point,
but it may not replace your source-based judgment.

Typeset the **corrected** model and degree-of-freedom analysis in LaTeX, in a markdown cell, in the
format of Step 4. **No screenshots of mathematics. Ever.**

Then a **change list**: every correction you made, in a short table.

| What the report said | What the source says | Where in the source |
| --- | --- | --- |
| | | |

The third column is the graded one. A correction you cannot point to a page, equation, or table for is
an opinion, not a correction.

### Step 7 --- Implement, and try to reproduce a result

**AI category: AI required for your implementation; no AI when inspecting published code.**

Ask the AI tool to help generate a Pyomo implementation **of your corrected model** --- not of its own
uncorrected version. Then attempt to reproduce the result you named in your proposal. You remain
responsible for testing every equation and interpreting the result.

The implementation follows [](pyomo-style-guide.md): built in a function, a termination check before any
`pyo.value()` call, a seeded random number generator if anything is random, and comments **in your own
words**.

If the source distributes code, wait until your own model is implemented. Then, without sharing that
code with the AI tool, use it as an independent validation source: run it if practical, compare its
equations, data, assumptions, and results with yours, and document any discrepancy. Cite the code and
respect its license.

#### The reproducibility audit

Report what happened, plainly:

* **The target.** Which number, from which table or figure.
* **What you got.** The value, and how far off.
* **What the source does not tell you.** Go through the list and say which items are missing: the data
  itself, parameter values, units, bounds, the solver and its version, tolerances, the initial point, a
  random seed, which variant of the model produced the reported number.
* **Your conclusion.** Is the result reproducible from the published source alone? If not, what is the smallest
  thing the authors could have added to make it so?

A failed reproduction that is diagnosed carefully is a full-credit answer. An unexplained match is not.

```{note}
**Finding a discrepancy between the published model and the code is a success, not a problem with your
paper.** You would be surprised how many papers contain a small disagreement between the methods section
and what the software actually does.

This course has hit exactly that in its own materials. MO-book notebook 5.1 sums the blending constraints
over the wrong index set and swaps two constants in its markdown, while its code is right both times. An
earlier problem set in this course stated a return constraint with $\ge$ and coded it as $=$ --- which
agrees at the parameter value where the constraint is active and differs by 45% where it is not. And two
contributed notebooks on this website ran without error for years while being, respectively,
**infeasible** and **unbounded** --- see §7 and §8 of [](pyomo-style-guide.md).

Running is not the same as correct. Neither is published.
```

## What you submit

Upload **one ZIP file to Canvas**. Keep its contents simple and flat; no required data folder. The
notebook is the main narrative and should open and run with paths relative to the ZIP contents.

Include:

* one Jupyter notebook containing the narrative, corrected model, implementation, results, and disclosure;
* the full AI transcript and the AI-exported report in readable PDF, HTML, Markdown, or text form;
* one PDF containing the scanned handwritten/annotated work; and
* any input data files needed to run the notebook.

Use descriptive filenames, and do not include environments, caches, solver scratch files, or unrelated
downloads. Published source code is not a required submission; include it only when redistribution is
permitted and it is necessary to understand your validation.

| # | Deliverable | What it is evidence of |
| --- | --- | --- |
| 1 | Full citation of the source, and your reproduction target | You chose a source this assignment can be done on |
| 2 | Your five clarifying questions, and the full AI transcript | The questions came from your reading, not from the tool |
| 3 | Reflection paragraph on the AI interaction | You noticed how the tool behaved |
| 4 | The AI-exported model and DOF report, **unedited** | The "before" state --- without it, no correction is visible |
| 5 | **Scan of the annotated printout** | You checked it by hand. Cannot be faked by a tool |
| 6 | Corrected formulation, DOF table, and change list with citations | You were right about what was wrong |
| 7 | Your Pyomo implementation, plus published-code validation when available | The corrected model, in code |
| 8 | Reproducibility audit and any model-versus-code discrepancy | You know what the source does and does not support |
| 9 | AI disclosure | Disclosed, per the syllabus |
| 10 | References | Everything you used, cited |

Items 4, 5 and 6 are one chain: the artifact, the check, the correction. **Submitting 6 without 4 and 5
is not a corrected model; it is an unsourced claim.**

The notebook is the grading entry point. Put the AI-exported report, transcript, and handwritten scan in
separate readable files within the same ZIP and link to their filenames from the notebook.

## AI disclosure

Every submission ends with a section titled **AI Disclosure**, reporting:

* **Which tool or tools**, and which steps you used each one for
* **What it got wrong** --- across the whole project, not just Step 5
* **How you knew** --- this is the graded part

Per the [Artificial Intelligence Policy](./syllabus.md#artificial-intelligence-policy), your code
comments and your written answers must be **in your own words**, and you are responsible for
understanding everything you submit. The exams are in person and without a computer.

## References

A reference list covering **every** source of data, models, figures, and code, in a citation style
standard for your field. Failure to disclose source material you used is an honor code violation.

## Grading

| Component | Weight |
| --- | --- |
| Paper selection and proposal | 5% |
| Five clarifying questions and the reflection (Steps 2--3) | 10% |
| AI-exported model and DOF report, submitted unedited (Step 4) | 5% |
| **Annotated printout --- the check by hand (Step 5)** | 25% |
| Corrected formulation, DOF analysis, and cited change list (Step 6) | 25% |
| Pyomo implementation and published-code validation when available (Step 7) | 15% |
| Reproducibility audit and discrepancy findings (Step 7) | 10% |
| AI disclosure and references | 5% |

**Half the grade is Steps 5 and 6** --- the check and the correction. That is deliberate. Extracting a
model and writing Pyomo are things a tool does; establishing that the extraction is faithful to the
source is not.

You are graded individually, and **you must be able to explain any part of your submission.** If you
cannot defend a section, do not submit it.

## Contributing to the class website

A strong verified notebook may be invited to join the class website as a contributed example. This is
optional, happens after grading, and goes through review --- see [](contribute.md). It is not part of the
project grade.

## Checklist

Work down this list before you submit.

- [ ] Proposal posted in the Canvas Discussion by October 2 (earlier encouraged)
- [ ] Paper passes all three selection tests
- [ ] Paper printed and read with a pencil
- [ ] Five or more clarifying questions, drafted by you, with the full transcript
- [ ] Reflection paragraph on what the AI tool did well and badly
- [ ] AI-exported report included **unedited**
- [ ] Report printed, checked against the source by hand, and **the annotated scan submitted**
- [ ] Corrected model typeset in LaTeX, in symbols, units on every parameter and variable
- [ ] Constraints named for what they mean
- [ ] No screenshots of mathematics anywhere
- [ ] Six-row degree-of-freedom table, in symbols, with no total row
- [ ] Problem classified, with a reason
- [ ] Change list, with a source citation for every correction
- [ ] Pyomo implementation of the **corrected** model built from the published document
- [ ] Published code, if available, kept away from the AI agent and used only for later validation
- [ ] Every `solve()` followed by a termination check before any `pyo.value()`
- [ ] Reproduction attempted, with the target named and the gap reported
- [ ] Missing information the source would need for reproducibility, listed
- [ ] AI disclosure section present
- [ ] References for all data, models, figures, and code
- [ ] All submission files packaged in one simple ZIP; notebook links to supporting files
- [ ] `black` has been run; the notebook passes **Restart & Run All** from a fresh kernel
