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

## Scope and Project Types

Please choose from the following options. As a rough guide, your project should require 20 (undergraduate) to 30 (graduate) hours of time investment over the entire semester.

### Optional 1: Make significant revisions to two class notebooks

Many of our class notebooks would benefit for enhancements such as:
* Replacing screenshots with typeset equations
* Updating figures to be publication quality
* Creating new examples
* Adding discussion questions to better explain current results
* Add sections on new concepts

By completing this project, you will 

A.	Develop and solve an optimization model related to your research

This is the most opened ended project format and intended for PhD students that plan to apply optimization to their research. When choosing this type of project, be sure to set clear and achievable goals for the semester; it will take you 3 to 5-times longer than you think. The best projects have a clear path to a promising proof-of-concept result in ~10 hours of work. A poor project requires 20+ hours of model development and coding before you have any indication if it will work. In past semesters, some students have jumped into projects like this without a clear plan, which caused stress and anxiety; the best way to avoid this is spending ~5 hours developing your project proposal. Think though your ideas and make a timeline. What are interesting research questions you can address quickly with optimization? How can you gradually grow the complexity of the model as the semester progresses?

You are encouraged to use your current or past research for this project. If you plan to reuse code you have previously developed, you need to clearly articulate the extensions you will make as part of this class project (e.g., implement new programming feature, add complexity to the model, perform new analysis). These extensions should require the same amount of work as your peers over the semester, i.e., 50 hours.    

B.	Implement an optimization model from literature. Either reproduce a case study or develop a new one.

This is perhaps the best project for a PhD student planning to use optimization in their research. Reproducing results from literature is a great way to get started because the model already exists. This allows you to focus on understanding the model, implementing it in Python/Pyomo (or a similar computing environment), and performing some analysis. Be judicious in your choice of paper to reproduce. Choose a model that is interesting but not too complicated. Make sure all of the parameters (input data) are well-defined and available.

C.	Implement an algorithm that we skip or only briefly cover in lecture/homework and perform some benchmark comparisons

This is a great project choice for students that plan to use optimization via other packages, e.g., scikit-learn for machine learning, and do not see themselves developing optimization models or using Pyomo. This project structure allows you to understand what is “under the hood”.

Here are some algorithms we will not cover in detail:
•	Stochastic gradient descent
•	Numeric integration for DAE systems (e.g., extend backward Euler code for ODEs into an implicit Runge-Kutta integrator for DAEs).
•	Sequential quadratic programming
•	Branch and bound for integer programming
•	Branch and cut for deterministic global optimization
•	Bayesian optimization
•	Surrogate assisted optimization
•	Sequential DAE optimization

During March, we will start implementing optimization algorithms in Python using numpy. Youshould follow a similar approach for prototyping one of the algorithms above. You will also need to benchmark your algorithm with several test problems to show it is working.

D.	Develop a new mini project (similar to the battery example)

This is a great choice for students that want more Pyomo experience (and practice making instructional materials). Below are some project ideas (homework problems from Fall 2018). Ultimately, you will create a notebook similar to our mini project that walks the reader through model development, Pyomo implementation, visualizing results, and performing analysis. You should include both discussion questions and their answers. Prof. Dowling will add your notebook (with attribution to you) to the class website at the end of the semester.

HW Problem 1: Consider a cannon located a x=0 and a getaway car at position x=300 m and at rest (vcar=0) at t=0. The cannon is stationary, but the getaway car is moving away from the cannon as fast as possible on a flat, straight road (x-axis). The car can be modeled with the same physics as the race car example from class. Starting at t=0 the driver applies acceleration u to the wheels and she doesn’t look back. The car’s engine has a governor that limits the maximum driving speed to vmax = 50 m/s. At time t=0, the gunner fires a cannon ball with initial velocity vfire. Assume the cannon ball is subject to aerodynamic drag, similar to the car.
a.	Formulate an optimize problem to calculate the angle of the cannon relative to the ground such that the cannon ball strikes the car. Typeset the model in your Juypter notebook. Perform degree of freedom analysis.
b.	With <5 minutes of internet searching, determine reasonable guesses for the mass of the car, initial cannon ball velocity, maximum acceleration of a car, aerodynamic drag of a car, and aerodynamic drag of a cannon ball. Report the assumed values, units, and a reference (URLs are fine) in your solution.
c.	Solve the model using Pyomo.DAE.
d.	Make a plot to visualize your solution.
e.	Describe how you should modify the model to account for uncertainty in the wind.

HW Problem 2: Revisit the “farmer’s problem” stochastic programming example. Implement the two-stage stochastic programming version of the Farmer’s problem in Pyomo. Hints: Create the model in a function where N, the number of scenarios, is an input. Making a parameter mutable allows it to be changed after the model is declared.
a.	Solve your Pyomo for the following cases and verify against the lecture notes / handout:
i.	Perfect information for three scenarios from class. Hint: solve the optimization problem for each scenario separately
ii.	Two-stage stochastic program from class.
b.	Make up a version of the Farmer’s problem with 5 scenarios. Calculate the following:
a.	Wait-and-See (perfect information) solutions and objective values (WS)
b.	Recourse Problem (stochastic program) solutions and objective values (RP)
c.	Expected Value solution (EV)
d.	Expected result using Expected Value solution (EEV)
e.	Value of Stochastic Solution (VSS)
c.	Use Sample Average Approximation to solve the Farmer’s problem assuming yields follow a uniform distribution between -50% and +50% (scaling all yields together, like in class).
a.	Calculate upper and lower bound confidence intervals using N = 10.
b.	Repeat for N = 100 scenarios.

HW Problem 3: Create a Python computer program that solves an arbitrary Sudoku puzzle using Pyomo. Test your code on two Sudoku puzzles of different sizes. Prof. Dowling can also provide a page on notes on the Sudoku puzzle as an integer program. These articles will be helpful:
a.	https://towardsdatascience.com/using-integer-linear-programming-to-solve-sudoku-puzzles-15e9d2a70baa
b.	https://www.mathworks.com/help/optim/examples/solve-sudoku-puzzles-via-integer-programming.html

Each of these above homework problems could be extended into a separate mini project. You can propose other ideas too! You will need to add new analysis and discussion questions, similar to the battery mini-project.

E.	Improve or contribute two (CBE 40499) or three (CBE 60499) notebooks to the class website 

This is another great choice for students wishing to deepen their knowledge in one specific area. Prof. Dowling will provide the original notebooks and scanned copies of his handwritten notes. Your responsibility will be to (1) read the notes and the recommended reference material, (2) typeset equations in the notebook, and (3) make enhancements or create new class examples. The ultimate goal is for the repository/website to be an excellent lasting reference for our current and future classes. Below are some ideas for existing notebooks. You can also propose new notebook ideas (e.g., sequential DAE optimization, parmest tutorial). 

2.2 Integer Programs
•	Add introduction section with general problem formulation, summarize main references
•	Typeset the model for the example, add explanations
•	Enumerate through the solution with Pyomo (fixing integer decisions) and solve the continuous relaxation. Print the results to the screen

2.3 Logical Modeling and Generalized Disjunctive Programming
•	Typeset the example from class. (Tip: read the explanation in the book in addition to your class notes)
•	Replace with screenshots for the steps and table via a table and LaTeX in markdown
•	Typeset the strip packing problem model and description
•	Remove the pprint() for the strip packing problem – too long
•	Solve the strip packing problem with GDPopt (you’ll need to Google this)
•	Revist the reactor selection example from 2.2. Implement with Pyomo.GDP and solve with GDPopt.

2.4 Differential Algebraic Equations
•	Typeset general notation (from textbook and notes)
•	Typeset index reduction algorithm 8.1 (and include attribution)
•	Typeset pendulum example analysis and index reduction

2.5 Numeric Integration for DAEs
•	Read reference chapters
•	Typeset notes from Prof. Dowling
•	Extend backwards Euler to integrate index 1 DAE system
•	Suggest changes to quadrature section to clarify any outstanding questions

2.6 Dynamic optimization with Pyomo.DAE
•	Typeset notes on collocation (see notes from Prof. Dowling and textbook)
•	Add illustrations from textbook that highlight collocation main ideas
•	Add comments to Pyomo code

2.7 Stochastic Programming (counts as two notebooks)
•	Typeset notes from class
•	Add farmer’s example (code link in class notebook)
•	Calculate value of stochastic solution for farmer’s example
•	Add code for sparse grids, use it in farmer’s example

You can choose notebooks we have not covered yet in class! There is much more material in the class reference textbook to add to the notebooks.

II.	Peer Mentor Groups

While this is an individual project, you will collaborate with an assigned group of 3-4 students. Throughout the semester, you will give and receive feedback to/from your peer mentor group on project concepts, mathematical model/algorithm details, results, and draft reports.

We are using the peer mentor strategy for several reasons:
-	Each student is responsible for their own project (compared to a team model), which helps develop skills as an independent researcher.
-	Help build collaborative communities that will last beyond the semester.
-	Peer mentors can give more frequent feedback than with a traditional instructor-driven model. Moreover, peer mentors are likely better suited to give domain-specific feedback for topics outside chemical engineering.
-	Peer mentoring deliverables are structured to introduce you to aspects of the peer review process for academic publications. 

III.	Milestones, Deliverables and Timeline

Date	Deliverable/Milestone	Estimated Effort
Friday, March 19	Project proposal due	5 hours
Friday, April 16	Progress report due	15 to 20 hours
Thursday, April 22	Peer review due, discuss as groups	3 hours
Monday, May 11	Final report/notebooks due	15 to 20 hours
Wednesday, May 13	Peer view due	2 hours
Monday, May 17	(Optional) final report revisions due	2 hours
Wednesday, May 19	Final presentations during exam timeslot	3 hours
		
	Total	45 to 55 hours

IV.	Project Proposal

The project proposal should be no more than 3 pages and includes the following sections.

Introduction (1 paragraph)
1.	Motivate the project and provide context for an interdisciplinary audience.
2.	Project type A or B: What are you trying to accomplish with optimization?
3.	Project type C: Why is the algorithm important? What type of problems is it used for?
4.	Project type D or E: What skills do you anticipate your educational material will help future classes master? Why is this important?
5.	What is the final deliverable for this project? What defines “success”?

Problem Formulation (1/3 page)
[Project type A, B, or D]
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

Finally, please attempt to classify the optimization problem. Are any of the decision variables discrete? Are the constraints (equations) algebraic or (partial) differential equations or a mixture of both? Are the constraints all linear? Is the objective linear or nonlinear? Are any of the model parameters uncertain? Depending on this information, we may reorder some of the later lectures to better prepare for the projects.

[Project type C]
Summarize the main algorithm and identify the key steps (similar to examples in class). Explain the extensions you will explore that are beyond homework/in class activities.

[Project type E]
Not needed.

Model Development Plan (1 paragraph) [Project type A or B]
1.	Is the complete mathematical model available in literature? If so, please cite. If not, what parts will you need to derive? How can you simplify the model to ask meaningful research questions faster?
2.	Where will the input data come from? If literature, please cite. If from your research lab, please elaborate. Does data need to be collected? What is your backup plan if you cannot find the necessary input data?

Algorithm Development Plan (1 paragraph) [Project type C]
1.	Identify 2-5 references you will consult for the algorithm details.
2.	What problems will you use for testing and benchmarking? How do these problems highlight advantages of the algorithm? [For example, if you consider trust region extensions that deal with the “hard case” for nonconvex problems, you should identify a test problem for which simple trust region algorithms fail. You can find many of these examples in literature.]

Educational Material Development Plan (1 paragraph) [Project type D or E]
1.	What are the main skills/concepts your materials will emphasize?
2.	What references will you consult?
3.	What is the main idea for the mini project? OR Please rank order up to four class notebooks you would like to modify. Prof. Dowling will make the assignments to avoid duplicates.

You need to include one of the following sections: Model Development Plan, Algorithm Development Plan, or Educational Material Development Plan.

Timeline (<1/2 page) [all projects]
1.	Define measurable and specific weekly goals for your project. Estimate the number of hours for each goal. (Consider putting this in a table or Gantt chart.)
2.	Is your project feasible to finish by May?
3.	What parts of the project do you anticipate will be most challenging?
4.	Based on the lecture schedule in the syllabus, will you need to learn material before the rest of the class? If so, factor this into your weekly goals.
5.	How can you structure your project to have the model ready by the progress report (~15 hours of technical work)? This will ensure you have enough time to focus on analysis and refinement.

New Technical Expertise (1 short paragraph) [all projects]
In a few sentences, highlight the new technical expertise are you going to learn/refine/master through this project. In this context, new means knowledge or skills related to computational optimization that you were unaware of or had not mastered before the start of the semester.

References
Please choose a reference style consistent with journals in your field of study.

V.	Status Update

About 1 month into the project, you should have either identified the complete mathematical model and have preliminary results (project types A or B), identified the complete algorithm pseudocode (type C), or have read all of the reference materials and developed a complete plan (type D and E). This deliverable helps ensure you are on track. You will prepare a small report with the following sections:

A.	Executive Summary (1 paragraph)
-	What system are you optimizing? Or what algorithm are you studying? Or what concepts/skills are you helping others master?
-	Is the complete mathematical model/algorithm pseudocode ready?
-	Has all of the necessary input data been identified?
-	Is the project on time to be complete?
-	Summarize any changes to the project scope. What defines “success” now?
-	What help do you need from your peer mentors, TA, or course instructor?

B.	Updated Timeline (<1/2 page)
-	Revise the weekly timeline from your project proposal.
-	What challenges do you anticipate?
-	Explain any changes to the project scope. What was the original final deliverable? What is the new final deliverable?

C.	Draft Notebook(s) (or Report) with Model/Algorithm Details (2+ pages)
Explain the complete mathematical model (types A or B) or algorithm (type C). Or provide a draft of the educational materials (types D and E). This acts as a draft for your final report.

D.	References (at least 3). Choose a style that fits with the norms of your research community.



VI.	Final Report or Jupyter Notebook(s). 

You will prepare either a final report (mincing a short conference paper with optional appendix) or well-annotated Jupyter notebook(s) documenting your model/algorithm, results, and conclusions. For project Types D and E, your Jupyter notebook(s) should mimic the style of class materials. Be sure to budget enough time to write up the results and discussion; it is better to simplify your project scope (simplify the model, simply the algorithm, etc.) and focus on telling a complete research story (through results and discussion) than be overly ambitious with the project scope and only present preliminary computational results.

Type A, B, or C reports should contain the following sections:
•	Abstract. Summarize the motivation (why is it important?), methods (what did you do?), key results (what did you find?), and conclusions (what does it mean?) in a paragraph. Also include a sentence either identifying what you learned from the project and how it relates to the class content. (For example, “This project helped me master modeling in Pyomo which I had not used previously.”)
•	Introduction / Background / Problem Statement. (Choose the section title that fits best for your report.) In 1 or 2 paragraphs, explain the engineering problem or algorithm considered. Review the related literature. How is the approach studied similar and different to other approaches in literature? For Type C project, how does the algorithm compare to other algorithms we studied in class?
•	Methods. In 1 to 3 pages, summarize the methods. For Type A and B projects, present the optimization formulation similar to the mini project. Identify the decision variables, parameters, objective(s), and constraints. For Type C projects, provide the algorithm pseudocode (similar to the textbook) and identify acceptable ranges and typical values for algorithm tuning parameters. Summarize convergence properties, failure modes, and limitations of the algorithm. Discuss important notes for large-scale implementation such as special linear algebra techniques commonly used. Give references for further details.
•	Results and Discussion. In 1 to 3 pages, present and discuss the key results and findings. Include at least two graphical elements (e.g., figures, tables). Include details about model size, algorithm implementation, solvers, CPU times, and number of iterations. For Type A and B, interpret the results using domain knowledge. For Type C, compare the implemented algorithm against other algorithms (e.g., from class). Include number of model and gradient evaluations, computational time, number of iterations, and final solution (objective, gradient, smallest Hessian eigenvalue). Interpret and explain results using mathematical properties from class. For example, do any of the test problems highlight superior convergence properties?
•	Conclusions. Summarize key findings in 1 or 2 paragraphs. What are the one or two most important things you learned in this project? How did this project incorporate knowledge you gained from the class (i.e., did not know beforehand)?
•	Appendix 1: Computer Code. Please turn-in complete, working, and extensively commented code.
•	Appendix 2: Mathematical Models or Test Problems. For Types A and B, turn in a complete mathematical model with annotations consistent with your field of study (i.e., similar format, similar amount of explanation). At a minimum, you need to list all of the equations and include a nomenclature table WITH UNITS. Include the appropriate citations for the model and input data. For Type C, Write out the complete test problems. Include the appropriate citations.
For Type D projects, prepare a Jupyter notebook formatted similar to the Python Mini-Project. Provide working code and answers to all questions.

For Type E projects, prepare 2 or 3 Jupyter notebooks that are modified version of the class notebooks.

VII.	Final Presentation

You will give a 3-minute final presentation (long “elevator pitch”) to the class on your research findings. Your presentation should highlight i) motivation, ii) problem formulation, and iii) results. During the final presentations, you will be asked to give brief written feedback to most of the presenters.

VIII.	Formatting Guidelines

You may typeset the status report, final report, and appendices in LaTeX, MS Word, Juypter notebooks, or similar software. Please thoughtfully choose between these options to maximize your ability to reuse the material. For example, what software does your advisor prefer to use for writing manuscripts?
