# Project 2

Summary: With a partner, further explore an optimization problem, modeling technique, or algorithm.

## Learning Goals

By completing this project, you will:
* Develop deeper expertise in at least one optimization topic
* Develop mastery in Python and Pyomo
* Analyze and discuss optimization results
* Make publication quality figures

## Choosing a Topic

Select topic of interest to your team. Here are a few general ideas:
1. Create another optimization problem example similar to Project 1
2. Significantly enhance at least one page/notebook on the class website
3. Develop a *simple* optimization problem related to your research or interests

Here is a list of ideas for *significant enhancements* to the class website:
* Create a notebook that explains common modeling strategies for multi-objective optimization including scalarization and epsilon-constraint methods. In your notebook, include Pyomo code for a *simple* example. As a starting point, read [this paper](https://www.sciencedirect.com/science/article/pii/S0098135416300965) and then the first two chapters of [Nonlinear Multiobjective Optimization](https://link.springer.com/book/10.1007/978-1-4615-5563-6) which is available as a PDF from the library.
* Contribute a notebook on solving Suduko as a mixed integer program. Here is [starter code](https://colab.research.google.com/drive/1OYX5I2Af_uoNME3eJrz2u_5ekNE08B7v?usp=sharing). You can also find the optimization model in our scanned class notes on integer programming. As part of the project, you need to make the notebook standalone, i.e., typset and expand upon the class notes. You should also create code to visualize the solutions. Finally, you should perform a scaling study to see how the solution time scales with problem size for at least two MILP solvers.
* Enhance the [](../notebooks/2/Modeling_Disjunctions_Strip_Packing.ipynb) example by creating a function to visualize the intial guess and solution, similar to the circle example in [](../notebooks/1/NLP.ipynb). Next, find or develop a test set of different instances of the problem. Use this test set to benchmark the solve times for the Big-M and convex hull reformations as a function of the problem size (e.g., number of items).
* Split [](../notebooks/4/RiskMeasures.ipynb) into two notebooks. In the first notebok, introduce risk measures using the Farmer's example. In the second notebook, introduce and analyze the sugar mill production problem. For the Farmer's problem, use the improved Pyomo implementation available at [](../notebooks/4/blocks.ipynb)
* Enhance the notebook on [](../notebooks/4/AdvancedTopics.ipynb) by adding examples. See Prof. Dowling's scanned notes from previous years for more details related to sample average approximation. Use the Farmer's problem to develop examples. Hint: You will need to assume a probability distribution for the crop yield.
* Extend the Farmer's example to consider uncertainty in more than just weather. For example, consider the correlation between crop prices and product yields. If possible, find realworld data (although this may be too difficult). Use the improved Pyomo implementation available at [](../notebooks/4/blocks.ipynb).
* Develop a tutorial notebook on using [OMLT](https://github.com/cog-imperial/OMLT) to embed a machine learning surrogate model into Pyomo. Your notebook should include the entire workflow: (1) choose a moderately nonlinear function with a few inputs and at least one output, (2) using this function, generate synthetic data with modest measurement error, (3) training one or more machine learning models, (4) solving optimization problems using the ML surrogate as constraints to replace the moderately nonlinear function, (4) comparing your result to the `ground truth' optimization problem where you directly use the nonlinear function you selected in step (1).
* Revise the tutorial material for [ParmEst and Pyomo.DoE](../notebooks/5/data.md) using the new interface developed this summer. This means you need to change the modeling interface to eliminate the warning/depreciation warnings.
* Develop a tutorial notebook on using [PyNumero](https://pyomo.readthedocs.io/en/stable/contributed_packages/pynumero/index.html) to implement optimization algorithms in Pyomo. Compare two optimization algorithms in class on a set of test problems, similar to [](../notebooks/assignments/Algorithms3.ipynb).
* Develop a tutorial notebook on using the [Sensitivity Toolbox](https://pyomo.readthedocs.io/en/stable/contributed_packages/sensitivity_toolbox.html). Include an explanation of the underlying mathematics. You will need to read and summarize a few references on nonlinear programming sensitivity theory.
* Develop a tutorial notebook to explain the [Model Predictive Control](https://pyomo.readthedocs.io/en/stable/contributed_packages/mpc/index.html) extension using the [](../notebooks/1/Pyomo-Nuts-and-Bolts.ipynb) example. As part of this tutorial notebook, provide an introduction to model predictive control.
* Develop a tutorial on sequential quadratic programming with a simple solver implementation, similar to our interior point examples on the class website. Demonstrate this code on a few simple test problems.
* Enhance the notebook on [](../notebooks/8/MILP.ipynb) by implementing a simple branch-and-bound solver as a function. Demonstrate the code using the test problem currently analyzed in the notebook. This should be new sections in the notebook, not a replacement of the current manual search through the tree.
* Populate the current placeholder notebook on [](../notebooks/8/MINLP-Algorithms.ipynb). Write a brief background on different MINLP algorithms. See Prof. Dowling's scanned notes a starting point. Then show using a Pyomo example how to call these different algorithm options using `Bonmin` or `SCIP` or a similar solver available in Pyomo.
* Populate the current placeholder notebook on [](../notebooks/8/Global-Opt.ipynb). Write a brief background on global optimization algoirhtms. See Prof. Dowling's scanned notes a starting point. Then show how to use `BARON` or `SCIP` with an example in Pyomo. You will want to use the NEOS server to access these solvers. See [here](https://github.com/ndandanov/pyomo_simple_minlp) and [here](https://groups.google.com/g/pyomo-forum/c/auK_1QIWeKk) as a starting point for accessing NEOS.


Your project must enhance or extend the source reference material. For example, if you reproduced an optimization example from a textbook, you should perform a small additional analysis to gain a new insight about the problem not already discussed in the reference. If you choose an example that already has a Pyomo implementation, you need to extend the model in some way; this ensures that everyone gets some Pyomo practice in the project.

## Deliverable: Jupyter Notebook or Written Report

Most groups should develop a Jupyter notebook to contribute to the class website. Please follow the same formatting guidelines as [](./project1.md). For this project, please use sensible subsection and subsubsection titles. You do not need to the use same organization as Project 1.

If you developed an optimization problem related to your research, you may instead prepare a private Jupyter notebook or written report. This flexibility is because you and your research advisor may not want pre-publication data released on the class website. If you write a research report, you also need to submit commented code for brief review. 

## Deliverable: Class Presentation

You and your partner will give a 5-minute presentation to the class. Your presentation should:
* Briefly motivate your problem
* Summarize your project goals/key findings/contributions
* Show 1 or 2 exciting results or insights
* Your slides should be professionally formatted including:
  * Slide numbers
  * References for all sources for data, figures, models, codes, etc. you did not create
  * Publication quality figures
  * Font large enough to see from the back of our classroom on the projector





