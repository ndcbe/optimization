# Semester Project

Although homework is helpful for learning concepts, the goal of the class is to prepare you to apply optimization methods in your research or future careers. A project is the best way to accomplish this.

During the semester project, you will develop mastery of a handful of concepts introduced in this class through an application of your choice. The semester project is the main evaluation criteria for the semester (instead of a final exam).

Everyone is encouraged to structure their class projects to be aligned with their research. If you reuse any prior work, include a short paragraph in your project proposal and final report explaining the specific extensions you added for this class. (In other words, you should not completely recycle work you have already done; there needs to be something new.) Undergraduate students: please notify Prof. Dowling if you want to convert work from a previous/current class (including undergraduate research credit) into your semester project. Graduate students: please notify Prof. Dowling and other course instructors if you plan to “double count” a project for two current classes. This is likely fine as long as all instructors agree, but each version of the project should be tailored to each class.

## Learning Goals

By completing this project, you will:
* Practice formulating and analyzing optimization problems on paper
* Develop proficiency in Python, Pyomo, or other computational optimization enviroments
* Write well-documented code and use best practices (e.g., functions to minimize redundant code)
* Analyze and discuss optimization results
* Make publication quality figures

## Scope and Main Deliverable

Please choose from the following options. As a rough guide, your project should require 25 (undergraduate) to 35 (graduate) hours of time investment over the entire semester.

### Option 1: Make significant revisions to two class notebooks

Many of our class notebooks would benefit for enhancements such as:
* Replace screenshots with typeset equations
* Add equations from class lecture to notebooks (typeset)
* Update the figures to be publication quality
* Add discussion questions to better explain current results
* Add sections on new concepts or create new examples
* Update all code to use `import pyomo.environ as pyo` instead of `from pyomo.environ import *`
* Add comments to code including doc strings for all functions

By completing this type of project, you will deep dive on two class topics. In addition to helping future classes, you will practice making educational material. The expectation are:
* For the selected notebooks, complete all of the applicable improvements identified above.
* Add at least one section (i.e., topic) to a notebook on a new topic. The new section should include a concise description of the theory or model (e.g., governing equations) and a computational example.

Below are some specific enhancement requests/ideas:

Integer Programs
* Add introduction section with general problem formulation, summarize main references
* Typeset the model for the example, add explanations
* Enumerate through the solution with Pyomo (fixing integer decisions) and solve the continuous relaxation. Print the results to the screen

Logical Modeling and Generalized Disjunctive Programming
* Typeset the example from class. (Tip: read the explanation in the book in addition to your class notes)
* Replace with screenshots for the steps and table via a table and LaTeX in markdown
* Typeset the strip packing problem model and description
* Remove the pprint() for the strip packing problem – too long
* Solve the strip packing problem with GDPopt (you’ll need to Google this)
* Revist the reactor selection example from 2.2. Implement with Pyomo.GDP and solve with GDPopt.

Differential Algebraic Equations
* Typeset general notation from textbook and notes in LaTex (not screenshots)
* Typeset index reduction algorithm 8.1 in LaTex (not screenshot)
* Typeset pendulum example analysis and index reduction in LaTeX (not screenshot)
* Create new image for pendulum example, add source .pptx file to media folder

Numeric Integration for DAEs
* Read reference chapters
* Typeset notes from Prof. Dowling
* Extend backwards Euler to integrate index 1 DAE system
* Suggest changes to quadrature section to clarify any outstanding questions

Dynamic optimization with Pyomo.DAE
* Typeset notes on collocation (see notes from Prof. Dowling and textbook)
* Add illustrations from textbook that highlight collocation main ideas
* Add comments to Pyomo code

### Option 2: Create a new notebook for the class website

#### Algorithms and Theory

Our class website would also benefit from additional content, such as:
* Stochastic gradient descent
* Numeric integration for DAE systems (e.g., extend backward Euler code for ODEs into an implicit Runge-Kutta integrator for DAEs).
* Sequential quadratic programming
* Branch and bound for integer programming
* Branch and cut for deterministic global optimization
* Bayesian optimization
* Surrogate assisted optimization
* Sequential DAE optimization

This is a great project choice for students that plan to use optimization via other packages, e.g., scikit-learn for machine learning, and do not see themselves developing optimization models or using Pyomo. This project structure allows you to understand what is “under the hood”.

The contributed notebooks should include:
* Introduction
  * Summarize main concepts and theory
  * How does this algorithm compare to other algorithms from class?
* Methods
  * Typeset governing equations
  * Provide algorithm pseudocode (similar to the textbook) and identify acceptable ranges and typical values for algorithm tuning parameters
  * Summarize convergence properties, failure modes, and limitations of the algorithm
  * Provide Python code for algorithm
* Results: demonstate algorithm properties with one or more computational case studies (e.g., toy problems)
  * Report the number of model and gradient evaluations, computational time, number of iterations, and final solution (objective, gradient, smallest Hessian eigenvalue)
  * Interpret and explain results using mathematical properties from class. 
  * If applicable, compare the optimization algorithm to other algorithms from class. For example, do any of the test problems highlight superior convergence properties?
* Conclusions
* References: all source material (equations, models, example code) and a few key sources to learn more
* (For report only) Appendix: Python code

#### Pyomo Examples

Alternately, you may reproduce a simple optimization problem from literature as an illustrative case study, similar to the Pyomo Mini Project.

The contributed notebooks should include:
* Motivation for the problem suitable for diverse audience (1 or 2 paragraphs)
* Typeset model equations
* Degree of freedom analysis
* Pyomo implementation
* Analysis of solutions
* Brief activity with discussion questions
* References to all source material (equations, models, example code)

Your notebook must go beyond the reference material. For example, if you find Pyomo code already shared online, you must do more than just reproducing the results. For a paper with equations (and perhaps a model in another language, e.g., GAMS, Julia), translating the model to Pyomo and reproducing results is acceptable. Failure to disclose source material you used is considered an honor code violation.

### Option 3: Apply optimization to your research problem

This is the most opened ended project format and intended for PhD students that plan to apply optimization to their research. When choosing this type of project, be sure to set clear and achievable goals for the semester; it will take you 3 to 5-times longer than you think. The best projects have a clear path to a promising proof-of-concept result in ~10 hours of work. A poor project requires 20+ hours of model development and coding before you have any indication if it will work. In past semesters, some students have jumped into projects like this without a clear plan, which caused stress and anxiety; the best way to avoid this is spending a few hours developing your project proposal. Think though your ideas and make a timeline. What are interesting research questions you can address quickly with optimization? How can you gradually grow the complexity of the model as the semester progresses?

You are encouraged to use your current or past research for this project. If you plan to reuse code you have previously developed, you need to clearly articulate the extensions you will make as part of this class project (e.g., implement new programming feature, add complexity to the model, perform new analysis). These extensions should require the same amount of work as your peers over the semester.   

As a final deliverable, you should turn either a Jupyter notebook or short report (e.g., 4 to 6 page conference paper) with the following information:
* Abstract. Summarize the motivation (why is it important?), methods (what did you do?), key results (what did you find?), and conclusions (what does it mean?) in a paragraph. Also include a sentence either identifying what you learned from the project and how it relates to the class content. (For example, “This project helped me master modeling in Pyomo which I had not used previously.”)
* Introduction / Background / Problem Statement. (Choose the section title that fits best for your report.) In 1 or 2 paragraphs, explain the engineering problem or algorithm considered. Review the related literature. How is the approach studied similar and different to other approaches in literature? For Type C project, how does the algorithm compare to other algorithms we studied in class?
* Methods. For example, present the optimization formulation similar to the mini project. Identify the decision variables, parameters, objective(s), and constraints.
* Results and Discussion. Present and discuss the key results and findings. Include at least two graphical elements (e.g., figures, tables). Include details about model size, algorithm implementation, solvers, CPU times, and number of iterations. Interpret the results using domain knowledge.
* Conclusions. Summarize key findings in 1 or 2 paragraphs. What are the one or two most important things you learned in this project? How did this project incorporate knowledge you gained from the class (i.e., did not know beforehand)?

## Peer Mentor Groups

While this is an individual project, you will collaborate with an assigned group of 3 or 4 students. Throughout the semester, you will give and receive feedback to/from your peer mentor group on project concepts, mathematical model/algorithm details, results, and draft reports.

We are using the peer mentor strategy for several reasons:
* Each student is responsible for their own project (compared to a team model), which helps develop skills as an independent researcher.
* Help build collaborative communities that will last beyond the semester.
* Peer mentors can give more frequent feedback than with a traditional instructor-driven model. Moreover, peer mentors are likely better suited to give domain-specific feedback for topics outside chemical engineering.
* Peer mentoring deliverables are structured to introduce you to aspects of the peer review process for academic publications. 

## Project Proposal

The project proposal should be 1 to 3 pages and includes the following sections.

**Introduction** (1 paragraph):
1.	Motivate the project and provide context for an interdisciplinary audience.
2.	Option 2 (new Pyomo example) or Option 3: What are you trying to accomplish with optimization?
3.	Option 2 (new algorithm): Why is the algorithm important? What type of problems is it used for?
4.	Option 1: What skills do you anticipate your educational material will help future classes master? Why is this important?
5.	All: What is the final deliverable for this project? What defines “success”?

**Details** (1/2 to 1 page):

For a new Pyomo example (option 2) or research problem (option 3):

Write down the optimization problem without equations. Identify the decision variables and required input data. For the battery example in Mini Project 1:

Maximize Market revenue over finite time horizon
s.t.		Battery physics (efficiency, energy balance)
		Bounds/limitations (power, state-of-charge)

Decision variables:
a.	Charge/discharge power for each timestep
b.	Energy in battery at end of each timestep

Input data/parameters:
a.	Timeseries market prices
b.	Round trip efficiency
c.	Initial state-of-charge

Attempt to classify the optimization problem. Are any of the decision variables discrete? Are the constraints (equations) algebraic or (partial) differential equations or a mixture of both? Are the constraints all linear? Is the objective linear or nonlinear? Are any of the model parameters uncertain? Depending on this information, we may reorder some of the later lectures to better prepare for the projects.

Is the complete mathematical model available in literature? If so, please cite. If not, what parts will you need to derive? How can you simplify the model to ask meaningful research questions faster?

Where will the input data come from? If literature, please cite. If from your research lab, please elaborate. Does data need to be collected? What is your backup plan if you cannot find the necessary input data?

For new algorithm page (option 2):

Summarize the main algorithm and identify the key steps (similar to examples in class). Explain the extensions you will explore that are beyond homework/in class activities.

Identify 2-5 references you will consult for the algorithm details.

What problems will you use for testing and benchmarking? How do these problems highlight advantages of the algorithm? [For example, if you consider trust region extensions that deal with the “hard case” for nonconvex problems, you should identify a test problem for which simple trust region algorithms fail. You can find many of these examples in literature.]

For notebook enhancements (option 1):

Identify three notebooks you would like edit rank ordered from greatest to least preference. Prof. Dowling will make the assignments to avoid duplicates.

For each selected notebook, make a list of the planned enhancements.

Describe in 1 paragraph the new content you plan to add to one of the notebooks. Identify this specific notebook. If you will add an example, describe the model (and if from literature, cite) and justify your choice. Explain why the content you plan to add will enhance the notebook.

**Timeline** (<1/2 page):
1.	Define measurable and specific weekly goals for your project. Estimate the number of hours for each goal. (Consider putting this in a table or Gantt chart.)
2.	Is your project feasible to finish by May?
3.	What parts of the project do you anticipate will be most challenging?
4.	Based on the lecture schedule in the syllabus, will you need to learn material before the rest of the class? If so, factor this into your weekly goals.
5.	Options 2 and 3: How can you structure your project to have the model or algorithm prototype ready by the progress report (~10 hours of technical work)? This will ensure you have enough time to focus on analysis and refinement.

**New Technical Expertise** (few sentences):
Highlight the new technical expertise are you going to learn/refine/master through this project. In this context, *new* means knowledge or skills related to computational optimization that you were unaware of or had not mastered before the start of the semester.

**References**:
Please choose a reference style consistent with journals in your field of study.

## Status Update

About 1 month into the project, you should be about 30% to 40% done with the project. You will prepare a small report with the following sections:

**Executive Summary** (1 paragraph):
* What system are you optimizing? Or what algorithm are you studying? Or what concepts/skills are you helping others master?
* Is the complete mathematical model/algorithm pseudocode ready?
* Has all of the necessary input data been identified?
* Is the project on time to be complete?
* Summarize any changes to the project scope. What defines “success” now?
* What help do you need from your peer mentors, TA, or course instructor?

**Updated Timeline** (<1/2 page):
* Revise the weekly timeline from your project proposal.
* What challenges do you anticipate?
* Explain any changes to the project scope. What was the original final deliverable? What is the new final deliverable?

**References**
* As needed to support the other sections

**Draft Notebook(s) or Report**:
* Explain the complete mathematical model (option 2: new example, option 3: research) or algorithm (option 2: theory).
* Provide a near complete draft of one of the notebooks (option 1)

## Final Presentation

You will give a 3-minute final presentation (long “elevator pitch”) to the class on your project. For new notebooks or research projects, highlight the i) motivation, ii) problem formulation or algorithm, and iii) a key result. For notebook revisions, i) summarize changes, ii) emphasize the new content you added. During the final presentations, you will be asked to give brief written feedback to most of the presenters.