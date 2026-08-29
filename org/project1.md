# Pyomo Project


Summary: choose a published optimization model from the literature, e.g., paper, report, book.
Use an AI tool to extract the mathematical model from its source. Then **check the AI's work against the source, on paper, with a pencil.** Correct it,
implement it, and try to reproduce a published result.

Worth **10% of the course grade**. See the [semester calendar](./calendar.md) for the due date.

This is an **individual assignment**. Each paper or specific model from a longer source is reserved by the
first student who posts it in the Canvas proposal discussion. Two students may not analyze the same paper
or the same model from a book or report.

## This is an AI-forward assignment

The previous version of this project asked you to build a Pyomo model of a problem you chose. That was
mainly a programming assignment. Arguably, with modern AI tools, mastering programming aspects are
less important, and instead this assignment can focus on promiting curiosity and practicing critical 
assessment skils.

This assignment focuses on verification of AI modeling output. You will:

1. Use an AI tool to produce an optimization formulation, a degree-of-freedom analysis, and computational (Pyomo) implementation.
2. Check the AI outputs against the primary source, by hand, the old fashioned way.
3. Correct the AI output, explain what was wrong and how you knew, and explore an optimization model

We expect the AI tool(s) you use will give you something that looks
right, reads fluently, and runs. **You are the one accountable for whether it is true.**

Before starting, read both the [Artificial Intelligence Policy](./syllabus.md#artificial-intelligence-policy)
and the [Collaboration Policy and Honor Code](./syllabus.md#collaboration-policy-and-honor-code).
This assignment adds more specific rules. Each stage is labeled:

* **No AI:** complete the stage without an AI tool.
* **AI required:** use an AI tool and retain the requested evidence.
* **AI permitted after independent work:** first make and record your own attempt; then you may use AI,
  provided you disclose and verify its contribution.

## Learning goals

By completing this project, you will:

* Read a published technical source closely enough to reproduce the results
* Extract a mathematical program from prose, and write it in set notation
* Perform and interpret a degree-of-freedom analysis on someone else's model
* Audit an AI tool's technical output against a primary source, and correct it
* Attempt a reproduction, and diagnose why one fails
* Judge what a source must report for its results to be reproducible at all

## Choosing a published model

Pick a citable, published source --- for example, a journal or conference paper, book, or technical
report --- that **contains a complete optimization model and numerical results you can analyze.** A
course notebook, blog post, or undocumented code repository is not a published model for this purpose.
Moreover, if a paper, report, or book includes a computer implementation of the model (e.g., as supporting 
information), you are not allowed to use that until the final verification step, after you have done
extensive \emph{manual/human guided} verification. The purpose of this assignment is to practice 
reproducing someoneelse's results when you are not given the code.

### The test your source must pass

Before you commit to a literature source, confirm:

1. **The model is printed in the source.** You can point to specific equations or clearly identified
   passages that give the objective, constraints, and definitions needed to reconstruct it. You might need to
   check if the paper has a supporting information.
2. **There is a numerical result you can try to reproduce.** A specific table entry, a figure, or a number in the
   text that you intend to reproduce.
3. **The model is small enough to finish.** Roughly: the full model fits in under about thirty numbered
   equations, and the formulation fits on two pages in your own notation.

**Do not choose a literature source** that is:
* a review and survey papers without a complete model
* a source where the optimization is done inside a commercial black box with accessible model
* a sources reporting only qualitative results
* a sources whose model is stated only as "we solved the standard formulation, see reference..."

Note: Some dynamic optimization papers rely on sequential optimization methods, such as multiple shooting. while
this is a valid optimization approach and perhaps the best choice for certain classes of problems, we will not
cover the basics of these modeling methods: sensitivity or adjoint equations, dynamic modeling environments such as 
CasADi or Modelica. For this assignment, we recommend choosing a dynamic optimization problem that was successfully solved
with a simultanous method, such as orthagonal collocation on finite elements.

```{tip}
Small and specific beats important and vague. A three-set, six-constraint scheduling model from a solid but niche
journal paper is a much better choice than a landmark paper with a forty-page appendix.
```

### If the source ships code

Published code is permitted and useful for validation, but it does not replace your implementation.
**Do not upload, paste, or otherwise share the published code with your AI agent.** Build your model from
the published document first. Only after your implementation is complete and you have done some 
validation by yourself may you inspect and run the published code to validate your model and investigate discrepancies.

### Where to look

Search the literature in your own area first; a source you have a reason to care about is easier to read
closely. If you need a starting point, these collections cite the papers their examples come from:

* [Hands-On Mathematical Optimization with Python](https://mobook.github.io/MO-book/intro.html)
* [ND Pyomo Cookbook](https://jckantor.github.io/ND-Pyomo-Cookbook/README.html)
* [Pyomo --- Optimization Modeling in Python](https://link.springer.com/book/10.1007/978-3-030-68928-5)
* [Applications of Optimization with Xpress-MP](https://examples.xpress.fico.com/example.pl#mosel_app)
* [Introduction to Stochastic Programming](https://link.springer.com/book/10.1007/978-1-4614-0237-4)

Follow the citation and read the original published source. The collection is the index, not the source.

### Proposal --- due Monday, September 21, 2026

**AI category: No AI.** This is your choice, motivation, and plan.

Post your proposal using the instructor's template in the designated **Canvas Discussion by 5pm on
Monday, September 21**. Posts are visible to the class in chronological order. Earlier posts are strongly
encouraged: everyone can see what classmates are studying, find shared interests, and avoid unintended
overlap. A paper or specific model belongs to the first student who posts it; check the existing posts
before choosing.

Keep the proposal to less than one page and answer these four questions concisely:

1. Which optimization model from the published literature do you want to analyze? Give the complete
   citation and identify the equations or passages containing the model and the result you will target.
2. Why did *you* choose this model?
3. Do you have all necessary input data? If not, how will you obtain it quickly? List likely sources and
   any assumptions you expect to make.
4. What do you hope to learn by completing this mini project?

A bulleted response to each question is welcome. A few sentences or a short paragraph per question is
also fine.

 The instructor
will contact you if there are concerns about scope, missing information, or substantial overlap with
another project.

Use only public or otherwise nonconfidential data that may be submitted with the project. Proprietary or
confidential data are not permitted. If required data are unavailable, use documented public sources or
clearly stated assumptions rather than restricted data.

## The steps

### Step 1: Read the source on paper

**AI category: No AI.**

**Print it. Read it with a pencil or a highlighter in your hand.** Mark the equations, the parameter
definitions, the data sources, and the result you plan to reproduce. Mark the places you do not follow.

Keep this copy. It is where your questions in Step 2 come from.

### Step 2: Interrogate the source with an AI tool

**AI category: AI required.**

Give the source to an AI tool and ask it **at least five clarifying questions that you drafted yourself,**
from your marked-up copy. The questions should be about this source, not optimization in general.

Good questions come from your notes in the margins:
* *What are the units of $\alpha$ in equation (7)?*
* *Is the capacity limit per period or cumulative?* 
* *Equation (12) has an index $j$ that never appears in the set definitions. What is it?*

Keep the questions and document the interaction using either the full transcript(s) or the detailed
AI-session report described under **AI disclosure** below.

### Step 3: Reflect on the interaction

**AI category: No AI.** Write this reflection yourself after reviewing the documented interaction.

A short paragraph. What did the tool do well? Where did it fail, stall, or make something up? Did it
answer a question the source does not actually answer, and if so, how did you notice?

One honest paragraph is worth more than a page of praise. This paragraph should be written by you. 

### Step 4: Extract the model with the AI tool, and export a report

**AI category: AI required.**

Working with an AI tool, extract the optimization problem from the source and put it in **set notation, in
the form we use in class:**

* **Sets** --- each index set, and what it indexes
* **Parameters** --- every one, **with units**
* **Variables** --- every one, with units and domain
* **Constraints** --- grouped and named for the physics or requirement they express, not `con1`
* **Objective** --- with its sense and its units

Use **symbols, not numbers**. For example, $|\mathcal{T}|$ periods, not 168 periods.

Then perform a **degree-of-freedom analysis** with the six-row table, counted in symbols:

% TODO: Update this to count variables with bounds. See Lecture 2.

| Count | Number |
| --- | --- |
| continuous variables | |
| discrete or binary variables | |
| linear equality constraints | |
| nonlinear equality constraints | |
| linear inequality constraints | |
| nonlinear inequality constraints | |



Also classify the problem and say how you know: LP, MILP, NLP, MINLP? Convex? Any differential
constraints? Any uncertain parameters?

Iterate with the tool until the analysis is coherent. Then **ask it to export a report** documenting the
model and the degree-of-freedom analysis.

**Submit that report exactly as the tool produced it.** Do not clean it up. It is the "before" half of
the evidence, and without it there is no way to see what you corrected.

### Step 5: Check the report against the source, in pencil on paper

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
In the unlikely event your AI generated model and analysis is perfect, you should submit evidence that
you checked it in detail with a pencil.
```

### Step 6: Correct it, and typeset the corrected model yourself

**AI category: AI permitted after independent work.** Decide and record every technical correction from
your comparison with the source before asking AI for help. AI may help with formatting after that point,
but it may not replace your source-based judgment.

Typeset the **corrected** model and degree-of-freedom analysis in LaTeX, in a markdown cell, in the
format of Step 4. **No screenshots of mathematics.** You may use the typeset model from Step 5 as a starting point.

Then a **change list**: every correction you made, in a short table.

| What the report said | What the source says | Where in the source |
| --- | --- | --- |
| | | |

The third column is the graded one. A correction you cannot point to a page, equation, or table for is
an opinion, not a correction.

### Step 7: Implement, and try to reproduce a result

**AI category: AI required for your implementation; no AI when inspecting published code.**

Ask the AI tool to help generate a Pyomo implementation **of your corrected model**. Then attempt to 
reproduce the result you named in your proposal. You remain
responsible for testing every equation and interpreting the result.

The implementation follows [](pyomo-style-guide.md): built in a function, a termination check before any
`pyo.value()` call, a seeded random number generator if anything is random, and comments **in your own
words**.

If the source distributes code, wait until your own model is implemented. Then, try to reproduce the
published result without using the published code. After try this by yourself, without sharing the published code
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
```

## What you submit

Upload **one ZIP file to Canvas**. Keep its contents simple and flat; no required data folder. The
notebook is the main narrative and should open and run with paths relative to the ZIP contents.

Include:

* one Jupyter notebook containing the narrative, corrected model, implementation, results, and disclosure;
* AI-session documentation --- either full transcript(s) or a detailed report --- plus the AI-exported
  model/DOF report, in readable PDF, HTML, Markdown, or text form;
* one PDF containing the scanned handwritten/annotated work; and
* any input data files needed to run the notebook
* text file named README.md or README.txt that described each file in the submitted zip archive

Use descriptive filenames, and do not include environments, caches, solver scratch files, or unrelated
downloads. Published source code is not a required submission; include it only when redistribution is
permitted and it is necessary to understand your validation.

| # | Deliverable | What it is evidence of |
| --- | --- | --- |
| 1 | Full citation of the source, and your reproduction target | You chose a source this assignment can be done on |
| 2 | Your five clarifying questions and AI-session documentation | The questions came from your reading, and the interaction's trajectory is visible |
| 3 | Reflection paragraph on the AI interaction | You noticed how the tool behaved |
| 4 | The AI-exported model and DOF report, **unedited** | The "before" state --- without it, no correction is visible |
| 5 | **Scan of the annotated printout** | You checked it by hand. Cannot be faked by a tool |
| 6 | Corrected formulation, DOF table, and change list with citations | You were right about what was wrong |
| 7 | Your Pyomo implementation, plus published-code validation when available | The corrected model, in code |
| 8 | Reproducibility audit and any model-versus-code discrepancy | You know what the source does and does not support |
| 9 | AI disclosure | Disclosed, per the syllabus |
| 10 | References | Everything you used, cited |

Items 4, 5 and 6 are one chain: the artifact, the check, the correction. **Submitting 6 without 4 and 5
is not a corrected model. It is an unsourced claim.**

## AI disclosure

Every submission ends with a section titled **AI Disclosure**, reporting:

* **Which tool or tools**, and which steps you used each one for. Please use model names or version numbers.
* **The key points and trajectory** of the AI session or sessions: the important questions, changes in
  direction, and outputs you adopted or rejected
* **What it got wrong** --- across the whole project, not just Step 5
* **How you knew** --- this is the graded part

Even if you submitting full transcript(s) or by writing a detailed,
accurate report of your AI sessions, you should still describe in a few sentences here the overall trajectory of
your use of AI for this assignment. Raw prompts and transcripts are not required when the report provides enough detail to
understand how the work developed.

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
optional, happens after grading, and goes through review: see [](contribute.md). It is not part of the
project grade.

## Checklist

Work down this list before you submit.

- [ ] Individual proposal posted in the Canvas Discussion by September 21 (earlier encouraged)
- [ ] Paper or specific model was not already claimed in an earlier Canvas post
- [ ] Paper passes all three selection tests
- [ ] Paper printed and read with a pencil
- [ ] Five or more clarifying questions, drafted by you, with transcript(s) or a detailed session report
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
- [ ] No proprietary or confidential data used
- [ ] AI tools and session trajectory documented by transcript(s) or a detailed report
- [ ] All submission files packaged in one simple ZIP; notebook links to supporting files
- [ ] `black` has been run; the notebook passes **Restart & Run All** from a fresh kernel
