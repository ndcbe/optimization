# Syllabus

CBE 60499, ACMS 60499, CBE 40499, CBE 60499: Nonlinear and Stochastic Optimization

University of Notre Dame, Spring 2023

## Course Description

This course provides a practical introduction to models, algorithms, and modern software for **large-scale numerical optimization**. Topics include (nonconvex) nonlinear programming, deterministic global optimization, integer programming, dynamic optimization, and stochastic programming. Multi-objective optimization and mathematical programs with complementarity constraints may be covered based on time and student interests. The class is design for advanced undergraduate/graduate students from engineering, science, and mathematics who wish to incorporate optimization methods into their research. The course will begin with an introduction to modeling and the Python-based Pyomo computational environment. Optimization theory and algorithms are emphasized.

Graduate students (60499): A background in linear algebra and numerical methods will be helpful but is not necessary. Students should be comfortable programming in Julia, Python, MATLAB, C, or a similar language. EE 60551: Mathematical Programming is not a prerequisite for this course.

Undergraduate students (40499): Students must be comfortable with linear algebra and programming in Julia, Python, MATLAB, C, or a similar language. CBE 20258 or a similar undergraduate class on numerical methods is strongly recommended as a prerequisite. Please contact the instructor for any questions about preparation.

Everyone: You should satisfy at least TWO of the following advisory prerequisites:
- Have at least one year of programming experience in Python (ideal), MATLAB, Julia, C, or a similar language.
- Comfortable with matrix operations such as inverses, transposes, basic matrix algebra rules, basic matrix calculus, eigenvalues and eigenvectors, rank, definiteness
- Completed a class in numerical methods or computational linear algebra. (For CBE undergraduates, enjoyed CBE 20258 Numerical and Statistical Analysis.)
- Previously studied mathematical programming (optimization) theory
- Comfortable using Pyomo modeling environment
- High motivated to learn about optimization; plan to apply it to your research.


## Instructor and Teaching Assistants

| | Prof. Alexander (Alex) Dowling | Ms. Nicole Cortes | Mr. Xinhe Chen|
| ----------- | ----------- | ----------- | ----------- |
| | ![](https://dowlinglab.nd.edu/assets/320333/200x200/dowling_alex_sq.jpg) | ![](https://dowlinglab.nd.edu/assets/477743/200x200/img_5301_square_sized.jpg) | ![](https://dowlinglab.nd.edu/assets/477378/200x200/xinhe.jpg) |
| Office Hours | 9-10am on Fridays in 366 or 369 Nieuwland Hall | 3-4pm on Wednesdays in 366 Nieuwland Hall | 3-4pm on Wednesdays in 366 Nieuwland Hall  |

(Office hours are tentative, still need to be confirmed.)

## Discussuion Board (Canvas) and Email Correspondance
* Post your questions to the **discussion board in Canvas**
* Instructor only: adowling@nd.edu, **'60499' or '40499' in the subject**, private official matters (e.g., excused absence, testing accommodations)

We encourage you to post all your questions including your mathematical models, pseudocode, and code screenshots to the public **discussion board in Canvas**. We are doing this for a few reasons:
1. As professionals, you'll need to be comfortable asking questions in front of a team. We would like to cultivate a positive and friendly learning environment where everyone can practice this skill during the semester.
2. By answering questions in the public discussion board, everyone in the class will have access to the same information.
3. We would like to cultivate a learning community with peer instruction; as professionals, you'll need to answer your peers' questions.
4. Many scientific software have online discussion boards to ask technical questions and report bugs. Using the **discussion board in Canvas** will help you develop comfort asking questions in this way.

## Textbook and Reference Materials

Primary References:
1. *Nonlinear Programming: Concepts, Algorithms, and Applications to Chemical Processes* by Lorenz T. Biegler [Chapter PDFs are available on SIAM website for free (on campus)](https://epubs.siam.org/doi/book/10.1137/1.9780898719383)
2. *Pyomo - Optimization Modeling in Python* by William E. Hart, Carl D. Laird, Jean-Paul Watson, David L. Woodruff, Gabriel A. Hackebeil, Bethany L. Nicholson, John D. Siirola. [A PDF is available via the campus library.](https://link-springer-com.proxy.library.nd.edu/book/10.1007%2F978-3-319-58821-6)

Additional References:
1. *Numeric Optimization* by Jorge Nocedal and Stephen J. Wright, 2nd edition.
2. *Global Optimization: Theory, Algorithms, and Applications* by Marco Locatelli and Fabio Schoen. [Chapter PDFs are available on SIAM website for free (on campus)](https://epubs-siam-org.proxy.library.nd.edu/doi/book/10.1137/1.9781611972672)
3. *Systematic Methods of Chemical Process Design* by Lorenz Biegler, Ignacio Grossmann, Arthur Westerberg. (Yes, this has really good sections on modeling applicable outside chemical engineering.)
5. *Lectures on Stochastic Programming: Modeling and Theory* by Alexander Shapiro, Darinka Dentcheva, Andrzej Ruszczynski. [Chapter PDFs are available on SIAM website for free (on campus)](https://epubs.siam.org/doi/book/10.1137/1.9780898718751)

## Classroom Meetings

Classroom meetings are a mix of i) traditional chalk board instruction, ii) computer demonstrations, and iii) in-class activities. Please bring an internet connected laptop computer. You are expected to have completed the assigned reading and at home activities for each topic (posted on Canvas/Vocareum) before each class session. 

## Focus and Final Grades

As an advanced technical elective, this class aims to prepare you to apply computational optimization methods in your immediate research or future careers by focusing on:
- Basic algorithms and theory
- Model formulations
- Using research/commercial optimization solvers
- Applications, especially in the class project

Final grades will be determined as follows:

Homework: 30%
Midterm Exam: 30%
Final Project: 40%

Grade scale for 60499:
- A : demonstrated mastery of main concepts
- A- : comfort with most concepts
- B+ : comfort with many concepts but struggled in a few areas
- B or below : struggled with main concepts or missing assignments or both

The median grade in 60499 will likely be an A- or B+.

Grading scale for 40499:
- A : demonstrated mastery of main concepts
- A- / B+ : comfort with most concepts
- B / B - : comfort with many concepts but struggled in a few areas
- C+ or below: struggled with main concepts or missing assignments or both

The median grade in 40499 will likely be an A- or B+.


## Homework

Problem set homework assignments are a collection of 2 to 5 problems designed to reinforce specific concepts and skills from class. Most problems include *pencil and paper analysis* (i.e., derive a model, determine degrees of freedom, write pseudocode, complete a proof), computer programming aspects, and interpretation of calculated results. These problems, especially the analysis and interpretation parts, are good practice for the exams. Many students receive near full credit on the problem sets.

## Collaboration Policy and Honor Code

You are permitted (and encouraged) to discuss solution approaches to the weekly homework assignments with classmates, however there is to be no wholesale copying or paraphrasing of code, solutions, or written discussions. You are encouraged to ask questions, including posting pseudocode or code screenshots, on the disccsion board on Canvas. Likewise, you may use any material posted by the instructors or your classmates in the discussion board on Canvas that you understand. Copying of code from classmates or the discussion board that you do not understand is not permitted. This policy is meant to facilitate collaboration while ensuring everyone in the class has the same access. Students MAY NOT use old HW files and solutions for the homework assignments: if you cannot do the problems for homework, you will not be able to do them on the exams either.

*As a guiding principle, if you are not comfortable explaining your solution strategy to an instructor or TA, you should not turn in the work as your own.*

Your work may be electronically tested for plagiarized content. For example, Vocareum and Gradescope have sophisticated capabilities to detect highly similar code (i.e., plagiarism for computer code) while distinguishing from provided templates. Plagiarism is a serious offense and will result in severe consequences per University, College, and Department procedures.

To remove ambiguity, the following is a non-exhaustive list of collaborative scenarios that are PERMITTED under the above policies:
* You work with a group of classmate to write pseudocode together. Each person in the group participates at least once (e.g., asks a question). One person in the group takes a picture and emails it to everyone. Then each person rewrites the pseudocode on their own for the homework submission. You rewrite the comments in your own words (to be more clear). You also decide to replace a `while` loop with a `for` loop. This is permitted by the collaboration policy because the work is your own. You made a clear intellectual contribution.
* You are working on a homework assignment and get stuck on an error message. After consulting the class notes and Google for 5 minutes, you post a screenshot of your code and the error message to Canvas. A classmate posts some alternate code that fixes your error. You reply by thanking the student and asking for clarification on why the alternate code works and your approach was wrong. This leads to a good discussion, with the instructor explaining a concept and clearing up your confusion. The solution you turn in includes the changes suggested by your classmates. This is permitted by the collaboration policy because you are comfortable explaining your solution strategy, including why the proposed modification was necessary to fix the error.
* You are working on the homework assignment a little closer to the deadline than you would like to admit. You get stuck on an error message, but quickly find a discussion thread on Canvas. You read through the suggestions from your classmates and the instructor. The post answers your major questions and the proposed fix works! You adopt it into your code and add a comment acknowledging your classmates on Canvas for help. You still have a minor question about if there is an alternate way to solve the problem, so you post on Canvas and continue with the assignment. This is permitted by the collaboration policy because you made a good faith effort to understand the proposed solution. Even though you have an outstanding minor doubt, you sought out help from the TAs, instructor, and classmates. You also acknowledged the source (Canvas discussion) for the code you used, and thus are not presenting it as your own.  

The following is a non-exhaustive list of collaborative scenarios that are PROHIBITED under the above policies:
* You are working on your homework alone in the library but two tables away there is a group of your classmates. They work through the pseudocode on a white board and do not erase it after leaving. You take a picture “just in case”. You later get stuck and frustrated. You end up copying a majority of their pseudocode, line by line, and turn this in. You have some doubts about the approach, but ran out of time. This is prohibited by the collaboration policy because the work is not your own. Moreover, you would be unable to explain your solution approach with confidence to the TA or instructor.
* It is late at night, you are frustrated with syntax errors, and you just cannot get one of the homework problems to work. You find a screenshot on Canvas of code from a classmate and an associated discussion. Desperate to finish the assignment, you start adapting your code to follow the screenshot. To keep it simple, you copy line-by-line, do not change variable names, and copy some comments but skip others. You end up submitted code that looks almost identical to your classmate. You remember the instructor keeps emphasizing the comments should be in our own words to show that you understand the solution. We decide to go to bed and add those comments in the morning. You oversleep and submit code without any comments or acknowledgments of your classmates. This is prohibited by the collaboration policy because you submitted work that is not your own. You did not acknowledge sources, and you can not explain with confidence the solution procedure to the instructor or TA.
* You have no prior programming experience and feel like you are falling behind. You feel like the homework takes you three times as long as your classmates. You conclude the only way you can keep up is to do the homework with a partner. They do half the assignment and you do the other half. You then exchange solutions. The person who completed each problem then explains the solution to the partner. Each person changes the comments, adds some extra white spaces, and changes a few variable names to ensure the solutions are not identical. This is prohibited by the collaboration policy because each person did not make an honest effort to solve every problem on their own. Although each person either explained or had the solutions explained to them, they likely cannot defend all of their solutions on their own to the TA or instructor. 

## Midterm Exam

The midterm exam will take place during class as indicated on the [semester schedule](./schedule.md). The exam will be closed book with no access to a computer. Students will be permitted to bring 2 sheets of letter size paper filled with handwritten notes.

## Projects

More details will be shared soon.

## Grading Standards

All computer code must be commented. No exceptions.

All graphs must have labeled axes with UNITS. Likewise, all final answers need UNITS and should be rounded to the appropriate number of significant digits.

Be sure to answer the questions that are asked. When discussing results, only report the appropriate number of significant figures.

**Problem Sets:** Not all (sub)questions on problem sets will be graded in detail. You may lose points for missing comments, missing units, unlabeled graphs, and non-sensible significant figures (digits) for final answers, even for problems only graded for completion.

**Formatting**: The expectation is that your submission includes neatly written code with extensive comments, well-labeled graphs, and answers to any discussion questions. Your project submissions should be professionally formatted, like a laboratory report. Your response to discussion questions and code comments MUST be written in your own words.

**Pseudocode:** Some assignments require you to write brief pseudocode. Your pseudocode needs to reflect all the main steps and logic of your solution. You do not need to rewrite your pseudocode if your final solution has different main steps or logic. Instead, you should update your pseudocode with a few notes showing the change. In our experience, rewriting the pseudocode is very helpful if you find a mistake in your logic but get stuck making modifications. Prof. Dowling has been programming in Python for 20 years. He writes pseudocode and so do other professional software developers.

See the [Pseudocode Guidelines](https://ndcbe.github.io/data-and-computing/notebooks/01/Pseudocode.html#pseudocode-guidlines) and [Python and Commenting Guidelines](https://ndcbe.github.io/data-and-computing/notebooks/01/Pseudocode.html#python-and-commenting-guidelines) for additional details.

## Assignment Submission

Assignments should be submitted electronically via Gradescope. For Jupyter Notebooks, you will need to upload the `.ipynb` file to Gradescope. Likewise, handwritten analysis should be scanned to a PDF and submitted via Gradescope.

## Regrade Requests

Mistakes can be made during grading. Regrades to correct these mistakes will be considered for **up to ONE week after assignment grades are posted online**. 

Regrade requests must be submitted in writing via Gradescope. Please include a 1-3 sentence explanation of the grading mistake. We will not consider adjustments to the grading point distribution.

All regrade requests will result in a reevaluation of the entire assignment. For rubric selection mistakes in Gradescope, this means we will recheck all rubric selections. For more substantial requests, the grader may choose to reexamine the entire problem (including all subparts) and possibly the entire assignment.

## Late Policy

The following policy will apply to all assignments (homework, projects, etc.):
* Up to 1 hour late: grace period with no penalty
* 1 hour to 24 hours late: 10% penalty of total available points
* 24 to 48 hours late: 20% penalty of total available points
* 48 to 72 hours: 30% penalty of total available points
* Beyond 72 hours: assignment not accepted

If there is an extenuating circumstance, please **email the instructor with 60499 or 40499 in the subject**. Please send your requests for extensions at least 24 hours in advance of the deadline (unless your specific circumstance prevents this). When requesting an extension, please briefly explain the extenuating circumstance and propose an alternate deadline.

## Software

We will use Python 3 in this class. You have three options to use Python:
1. (Recommended for Most People.) Use Google Colab. This allows you to complete all assignments from any internet accessible computer.
2. (Recommended for Advanced Users.) Install [anaconda3](https://www.anaconda.com/download/) on your own computer. This is a free distribution of Python that includes common packages for data analysis and scientific computing. You will need to install popular packages such as `numpy`, `scipy`, `pandas`, `matplotlib`, and `pyomo`.
3. Use anaconda3 installed on any ESC maintained computer, e.g., B19 in Fitzpatrick Hall.

## Inclusiveness, Mental Health, and Disabilities

The University of Notre Dame is committed to social justice. We share that commitment and strive to maintain a positive learning environment based on open communication, mutual respect, and non-discrimination. In this class we will not discriminate on the basis of race, sex, age, economic class, disability, veteran status, religion, sexual orientation, color, or national origin. Any suggestions as to how to further such a positive and open environment will be appreciated and given serious consideration.

Diminished mental health can interfere with optimal academic performance. The source of symptoms might be related to your course work; if so, please speak with us. However, problems with other parts of your life can also contribute to decreased academic performance. The University Counseling Center (UCC) provides cost-free and confidential mental health services to help you manage personal challenges that threaten your emotional or academic well-being. Remember, getting help is a smart and courageous thing to do — for yourself and for those who care about you. For more resources please see ucc.nd.edu. The UCC is located on the third floor of Saint Liam Hall Phone: 574-631-7336. Hours: Monday-Friday 8:30am – 5:00pm. Urgent Crisis Line 24/7. 

Any student who has a documented disability and is registered with Disability Services should speak with the professor as soon as possible regarding accommodations. Students who are not registered should contact the [Office of Disability Services](https://sarabeadisabilityservices.nd.edu/). 






