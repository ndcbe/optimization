# Syllabus

CBE 60499 / ACMS 60499: Optimization for Decision Science

University of Notre Dame, Fall 2026

**Lectures:** Mondays and Wednesdays, 12:30 - 1:45 pm, 184 Nieuwland Science Hall

**Dates:** August 24 -- December 9, 2026

## Prerequisites 

A background in linear algebra and numericalmethods is strongly recommended but not required. Students must be comfortable programming in Python (preferred), MATLAB, Julia, C, or a similar language. Topics in EE 60551 and ACMS 60880 are complementary to CBE/ACMS 60499. These courses are not prerequisites for CBE/ACMS 60499.

## Instructor

**Prof. Alexander (Alex) Dowling** --- office hours 30 minutes after class in 256 Nieuwland Science Hall.

To schedule a meeting with Prof. Dowling:
* Check his availability on [Google calendar](https://calendar.google.com/calendar/u/0?cid=YWRvd2xpbmdAbmQuZWR1)
* Send him an email with ~3 proposed times (that work for both you and his Google calendar)
* Include 60499 in the subject of your email
* Once Prof. Dowling agrees to the time, please send him a Google calendar invite

## Discussuion Board (Canvas) and Email Correspondance
* Post your questions to the **discussion board in Canvas**
* Instructor only: adowling@nd.edu, **'60499' in the subject**, private official matters (e.g., excused absence, testing accommodations, schedule a meeting per guidelines above)

We encourage you to post all your questions including your mathematical models, pseudocode, and code screenshots to the public **discussion board in Canvas**. We are doing this for a few reasons:
1. As professionals, you'll need to be comfortable asking questions in front of a team. We would like to cultivate a positive and friendly learning environment where everyone can practice this skill during the semester.
2. By answering questions in the public discussion board, everyone in the class will have access to the same information.
3. We would like to cultivate a learning community with peer instruction; as professionals, you'll need to answer your peers' questions.
4. Many scientific software have online discussion boards to ask technical questions and report bugs. Using the **discussion board in Canvas** will help you develop comfort asking questions in this way.

## Textbook and Reference Materials

This list matches the *Main references* and *Additional recommended references* in the front matter of
the printed course pack.

Main References:
1. *Nonlinear Programming: Concepts, Algorithms, and Applications to Chemical Processes* by Lorenz T. Biegler, SIAM (2010). The primary reference for most of the course. [Chapter PDFs are free from SIAM on campus.](https://epubs.siam.org/doi/book/10.1137/1.9780898719383)
2. *Numerical Optimization* by Jorge Nocedal and Stephen J. Wright, 2nd edition, Springer (2006). A phenomenal reference on optimization algorithms and theory. [A digital copy is available via the campus library.](https://link.springer.com/book/10.1007/978-0-387-40065-5)
3. *Hands-On Mathematical Optimization with Python* by Krzysztof Postek, Alessandro Zocca, Joaquim Gromicho, and Jeffrey Kantor, Cambridge University Press (2025). Introduces optimization modeling and theory with extensive Pyomo examples. If you are primarily interested in applications, buy this book. [It has an excellent companion website.](https://mobook.github.io/MO-book/)

Additional References:
1. *Pyomo --- Optimization Modeling in Python* by Michael L. Bynum, Gabriel A. Hackebeil, William E. Hart, Carl D. Laird, Bethany L. Nicholson, John D. Siirola, Jean-Paul Watson, and David L. Woodruff, 3rd edition, Springer (2021). [A PDF is available via the campus library.](https://link.springer.com/book/10.1007/978-3-030-68928-5)
2. *Introduction to Stochastic Programming* by John R. Birge and François Louveaux, 2nd edition, Springer (2011). [A PDF is available via the campus library.](https://link.springer.com/book/10.1007/978-1-4614-0237-4)
3. *Global Optimization: Theory, Algorithms, and Applications* by Marco Locatelli and Fabio Schoen, SIAM (2013). [Chapter PDFs are free from SIAM on campus.](https://epubs.siam.org/doi/book/10.1137/1.9781611972672)
4. *Systematic Methods of Chemical Process Design* by Lorenz Biegler, Ignacio Grossmann, and Arthur Westerberg, Prentice Hall (1997). (Yes, this has really good sections on modeling applicable outside chemical engineering, including a great chapter on logical modeling.)
5. *Nonlinear Multiobjective Optimization* by Kaisa Miettinen, Springer (1998). [A PDF is available via the campus library.](https://link.springer.com/book/10.1007/978-1-4615-5563-6)
6. *Decision Making in Systems Engineering and Management* edited by Patrick J. Driscoll, Gregory S. Parnell, and Dale L. Henderson, 3rd edition, Wiley (2023). Broader framing for *decision science* beyond optimization. [Available digitally via the campus library.](https://findit.library.nd.edu/EdsRecord/cat10922a,und.ebs102843868e)

## Classroom Meetings

Classroom meetings are a mix of i) traditional chalk board instruction, ii) computer demonstrations, and iii) in-class activities. You are encouraged to review the [relevant notebooks](./calendar.md) and chapters in reference textbooks before and after each class meeting.

This semester, Prof. Dowling is creating a coursepack. For each lecture, we will bring printed handouts with gaps for note taking. A PDF will also be posted before each lecture on Canvas.

You are expected to attend and actively participate in all class sessions.  If you miss class for an official University excused function (e.g., illness, conference travel), please find notes for that lecture, do the reading, and avail yourself of office hours to catch up on the missed material.

## Final Grades

As an advanced technical elective, this class aims to prepare you to apply computational optimization methods in your immediate research or future careers by focusing on:
- Basic algorithms and theory
- Model formulations
- Using research/commercial optimization solvers
- Applications, especially in the class project

Final grades will be determined as follows:

| Category    | Weight |
| ------ | ----- |
| Homework (best 9 of 10, completion based) | 15% |
| Pyomo Project | 10% |
| Midterm 1 | 22.5% |
| Midterm 2 | 22.5% |
| Final exam | 30% |

Grade scale for 60499 (graduate):
- A : demonstrated mastery of main concepts
- A- : comfort with most concepts
- B+ : comfort with many concepts but struggled in a few areas
- B or below : struggled with main concepts or missing assignments or both

The median grade in 60499 will likely be an A- or B+.

Senior graduate students may audit this course with the permission of the instructor. The expectations for auditing are:
1. Attend and participate in at least 75% of the class sessions. 
2. Attempt each homework assignment. 

## Homework

There are **ten homework assignments**, which contain a mix of pencil and paper analysis problems and computer implementation.

**Grading is completion based.** Full credit is awarded for a genuine, complete attempt at every part --
not for getting every answer right. The point of the homework is practice, and practice you are afraid to
get wrong is not practice.

**Your lowest homework score is dropped.** For many
students this makes the final assignment effectively optional, which is deliberate: Prof. Dowling knows that
the last week of the semester can be crazy.

Homework is designed around an **independent attempt followed by critical use of assistance**. Unless an
assignment gives a different time, begin each problem by working for approximately **30 minutes without
generative AI, solution pages, or help from another person**. Stop the independent period early if you
complete the problem. During this period, you may consult lecture notes, textbooks, and the course website;
bias toward those course sources, and do not open solution pages on the course website. After that attempt,
you may use AI and the collaboration permitted below unless the assignment says otherwise. The 30-minute
guideline applies **once per top-level problem**, not separately to every subpart, unless the assignment
explicitly says otherwise. Each assignment may impose additional problem-specific rules, including a
different time limit or a requirement that a particular stage be completed with or without AI.

Each homework problem includes a required, concise **AI and independent-work report**. State approximately
how long the independent attempt took, how far you got, where you became stuck, what AI or collaborative
help you used afterward, and how you verified it. If you used no AI, say so. The time estimate is not a
speed test; it gives the instructor useful data for improving the length and design of future assignments.

See the [Artificial Intelligence Policy](#artificial-intelligence-policy) below. What does not change is
that **you are responsible for understanding and verifying everything you submit.** The exams are
individual, in person, and without a computer, so anything you hand in without understanding is a debt that
comes due in September, November, and December.

Most problems include *pencil and paper analysis* (derive a model, count degrees of freedom, write
pseudocode, complete a proof), a computational part, and interpretation of the results. The analysis and
interpretation parts are the best available practice for the exams.

## Collaboration Policy and Honor Code

You are permitted and encouraged to discuss solution approaches, debug together, compare numerical
results, and write code together after the required independent attempt. Everyone who submits jointly
developed ideas or code must have made a genuine intellectual contribution and must be able to explain the
work. One student writing a solution and distributing it to classmates who did not intellectually
contribute is not collaboration; it is prohibited sharing and copying. Wholesale copying or paraphrasing
of code, solutions, or written discussions is not permitted.

You are encouraged to ask questions, including posting pseudocode or code screenshots, on the discussion
board on Canvas. You may use material posted there by instructors or classmates when you understand it,
acknowledge the help, and comply with the assignment's disclosure instructions. Students may not use old
homework files or solutions: if you cannot do the problems for homework, you will not be able to do them on
the exams either.

*As a guiding principle, if you are not comfortable explaining your solution strategy to the instructor, you should not turn in the work as your own.*

Your work may be electronically tested for plagiarized content. For example, Vocareum and Gradescope have sophisticated capabilities to detect highly similar code (i.e., plagiarism for computer code) while distinguishing from provided templates. Plagiarism is a serious offense and will result in severe consequences per University, College, and Department procedures.

To remove ambiguity, the following is a non-exhaustive list of collaborative scenarios that are PERMITTED under the above policies:
* You work with a group of classmate to write pseudocode together. Each person in the group participates at least once (e.g., asks a question). One person in the group takes a picture and emails it to everyone. Then each person rewrites the pseudocode on their own for the homework submission. You rewrite the comments in your own words (to be more clear). You also decide to replace a `while` loop with a `for` loop. This is permitted by the collaboration policy because the work is your own. You made a clear intellectual contribution.
* You are working on a homework assignment and get stuck on an error message. After consulting the class notes and Google for 5 minutes, you post a screenshot of your code and the error message to Canvas. A classmate posts some alternate code that fixes your error. You reply by thanking the student and asking for clarification on why the alternate code works and your approach was wrong. This leads to a good discussion, with the instructor explaining a concept and clearing up your confusion. The solution you turn in includes the changes suggested by your classmates. This is permitted by the collaboration policy because you are comfortable explaining your solution strategy, including why the proposed modification was necessary to fix the error.
* You are working on the homework assignment a little closer to the deadline than you would like to admit. You get stuck on an error message, but quickly find a discussion thread on Canvas. You read through the suggestions from your classmates and the instructor. The post answers your major questions and the proposed fix works! You adopt it into your code and add a comment acknowledging your classmates on Canvas for help. You still have a minor question about if there is an alternate way to solve the problem, so you post on Canvas and continue with the assignment. This is permitted by the collaboration policy because you made a good faith effort to understand the proposed solution. Even though you have an outstanding minor doubt, you sought out help from the instructor and your classmates. You also acknowledged the source (Canvas discussion) for the code you used, and thus are not presenting it as your own.  

The following is a non-exhaustive list of collaborative scenarios that are PROHIBITED under the above policies:
* You are working on your homework alone in the library but two tables away there is a group of your classmates. They work through the pseudocode on a white board and do not erase it after leaving. You take a picture “just in case”. You later get stuck and frustrated. You end up copying a majority of their pseudocode, line by line, and turn this in. You have some doubts about the approach, but ran out of time. This is prohibited by the collaboration policy because the work is not your own. Moreover, you would be unable to explain your solution approach with confidence to the instructor.
* It is late at night, you are frustrated with syntax errors, and you just cannot get one of the homework problems to work. You find a screenshot on Canvas of code from a classmate and an associated discussion. Desperate to finish the assignment, you start adapting your code to follow the screenshot. To keep it simple, you copy line-by-line, do not change variable names, and copy some comments but skip others. You end up submitted code that looks almost identical to your classmate. You remember the instructor keeps emphasizing the comments should be in our own words to show that you understand the solution. You decide to go to bed and add those comments in the morning. You oversleep and submit code without any comments or acknowledgments of your classmates. This is prohibited by the collaboration policy because you submitted work that is not your own. You did not acknowledge sources, and you can not explain with confidence the solution procedure to the instructor.
* You have no prior programming experience and feel like you are falling behind. You feel like the homework takes you three times as long as your classmates. You conclude the only way you can keep up is to do the homework with a partner. They do half the assignment and you do the other half. You then exchange solutions. The person who completed each problem then explains the solution to the partner. Each person changes the comments, adds some extra white spaces, and changes a few variable names to ensure the solutions are not identical. This is prohibited by the collaboration policy because each person did not make an honest effort to solve every problem on their own. Although each person either explained or had the solutions explained to them, they likely cannot defend all of their solutions on their own to the instructor. 

## Artificial Intelligence Policy

Please review Notre Dame's current
[Generative AI Policy for Students](https://honorcode.nd.edu/generative-ai-policy-for-students-august-2023/).
CBE/ACMS 60499 is an **AI-forward course**: you will practice both solving technical problems yourself and
using AI tools critically as a scientist or engineer. The following principles apply throughout the course.

1. **Assignment-specific instructions control.** Every assignment may add more specific rules. A problem
   or project step may be labeled **No AI**, **AI permitted after the independent attempt**, or
   **AI required**. Follow the most specific instruction that applies.
2. **Begin independently.** Unless an assignment specifies another time, work on each homework problem for
   approximately 30 minutes without generative AI, solution pages, or help from another person. If you
   complete the problem sooner, the independent period is complete. You may consult lecture notes,
   textbooks, and nonsolution pages of the course website, with a preference for these course sources.
   The default is once per top-level problem, not once per subpart. The purpose is to discover what you can
   do and where you become stuck before asking a tool to intervene.
3. **Use assistance critically.** When AI is permitted or required, treat its output as an unverified
   proposal. Check mathematical claims against course or primary sources, test code, inspect units and
   assumptions, and decide for yourself whether the result is correct. Code that runs is not necessarily
   correct.
4. **Disclose use.** Every homework problem ends with a concise AI and independent-work report; prompts and
   transcripts are not required for ordinary homework. Follow any more detailed format stated in the
   assignment. At minimum, estimate the independent time, describe how far you got, identify the tool,
   describe what you used it for and adopted, and explain how you verified it. If you did not use AI, say
   so. AI-powered editing tools, including tools that suggest rewritten prose, count as AI use and must be
   disclosed when used.
5. **Your understanding and voice remain yours.** You must be able to explain every equation, line of code,
   and conclusion you submit. Code comments, interpretations, reflections, and answers to discussion
   questions must communicate your own understanding in your own words. Use descriptive variable names and
   comment all submitted code.
6. **Do not misrepresent authorship.** Material generated or materially revised by an AI tool must not be
   presented as solely your own work. Some assignments intentionally require an unedited AI artifact or
   transcript as evidence; those clearly labeled artifacts are quotations for analysis, not
   student-authored answers.
7. **Exams are independent.** The two midterms and final exam are individual, on paper, and permit no
   electronic device other than a scientific or graphing calculator (thus no AI, no computer, and no internet). See
   [Exams](#exams).

The [Collaboration Policy and Honor Code](#collaboration-policy-and-honor-code) still applies when AI is
permitted. AI assistance does not excuse wholesale copying, replace the required independent attempt, or
remove your responsibility to understand, verify, and disclose the submitted work.

## Exams

There are **three in-person exams**: two midterms during class and a final exam during the University final
exam period. Dates are on the [semester calendar](./calendar.md).

| Exam | When | Notes permitted |
| --- | --- | --- |
| Midterm 1 | Wednesday, September 30, in class | open course pack / open binder |
| Midterm 2 | Wednesday, November 4, in class | open course pack / open binder |
| Final | Tuesday, December 15, 7:30--9:30 pm | open course pack / open binder |

All exams are **individual**. The only electronic device permitted is a scientifi or graphing calculator (no network access 
or communication). No laptops, tablets, phones, smart watches, e-readers, or
any other electronic device may be out during an exam.

**Your notes must be on paper.** Students who take notes on a tablet during class should print them before
each exam. Reading notes from a tablet is not permitted even with connectivity switched off. This is a new
recommendation for the College.

## Pyomo Project

In the [Pyomo Project](../org/project1.md) you choose a paper from the optimization literature, extract its model with the
help of an AI tool, and then **check that extraction against the paper by hand, on paper, in pencil**. You
then implement the corrected model and try to
reproduce one of their results. It is worth 10% of the course grade; see the
[semester calendar](./calendar.md) for the due date.

About half the grade is the checking and the correcting. Finding a discrepancy between a paper's printed model and
its own code is a **success**, not a problem with your choice of paper.

```{note}
**Project 2 has been retired.** In previous years a second, larger project ran through the second half of the
semester. It is replaced by an extra in-class midterm and the in-person final. With capable AI coding tools
widely available, an in-person exam is a more honest measure of engagement with the topic.
```

## Grading Standards

All computer code must be commented. No exceptions.

All graphs must have labeled axes with UNITS. Likewise, all final answers need UNITS and should be rounded to the appropriate number of significant digits. For the projects, please prepare [publication quality graphics](https://ndcbe.github.io/data-and-computing/notebooks/01/Publication-Quality-Figures.html)

Be sure to answer the questions that are asked. When discussing results, only report the appropriate number of significant figures.

**Formatting**: The expectation is that your submission includes neatly written code with extensive comments, well-labeled graphs, and answers to any discussion questions. Your project submissions should be professionally formatted, like a laboratory report. Your response to discussion questions and code comments MUST be written in your own words.

**Pseudocode:** Some assignments require you to write brief pseudocode. Your pseudocode needs to reflect all the main steps and logic of your solution. You do not need to rewrite your pseudocode if your final solution has different main steps or logic. Instead, you should update your pseudocode with a few notes showing the change. In our experience, rewriting the pseudocode is very helpful if you find a mistake in your logic but get stuck making modifications. Prof. Dowling has been programming in Python for 20 years. He writes pseudocode and so do other professional software developers.

See the [Pseudocode Guidelines](https://ndcbe.github.io/data-and-computing/notebooks/01/Pseudocode.html#pseudocode-guidlines) and [Python and Commenting Guidelines](https://ndcbe.github.io/data-and-computing/notebooks/01/Pseudocode.html#python-and-commenting-guidelines) for additional details.

## Assignment Submission

Assignments should be submitted electronically through Canvas in the format stated on each assignment.
For Jupyter notebooks, upload the `.ipynb` file; handwritten analysis should be scanned into one readable
PDF unless the assignment specifies a different package.

## Regrade Requests

Mistakes can be made during grading. Regrades to correct these mistakes will be considered for **up to ONE week after assignment grades are posted online**. 

Regrade requests must be submitted in writing via Gradescope. Please include a 1-3 sentence explanation of the grading mistake. We will not consider adjustments to the grading point distribution.

All regrade requests will result in a reevaluation of the entire assignment. For rubric selection mistakes in Gradescope, this means we will recheck all rubric selections. For more substantial requests, the grader may choose to reexamine the entire problem (including all subparts) and possibly the entire assignment.

## Late Policy

**Students are expected to submit work on time.** Late work is accepted at the discretion of the instructor.

If there is an extenuating circumstance, please **email the instructor with 60499 in the subject**, ideally
at least 24 hours before the deadline. Briefly explain the circumstance and propose an alternate deadline.

Note that the lowest homework score is dropped, which is intended to absorb the ordinary bad week without
anyone needing to ask.

## Software

We will use Python 3 in this class. You have three options to use Python:
1. (Recommended for Most People.) Use Google Colab. This allows you to complete all assignments from any internet accessible computer.
2. (Recommended for Advanced Users.) Install [anaconda3](https://www.anaconda.com/download/) on your own computer. This is a free distribution of Python that includes common packages for data analysis and scientific computing. You will need to install popular packages such as `numpy`, `scipy`, `pandas`, `matplotlib`, and `pyomo`.
3. Use anaconda3 installed on any ESC-maintained computer.

## Inclusiveness, Mental Health, and Disabilities

The University of Notre Dame is committed to social justice. We share that commitment and strive to maintain a positive learning environment based on open communication, mutual respect, and non-discrimination. In this class we will not discriminate on the basis of race, sex, age, economic class, disability, veteran status, religion, sexual orientation, color, or national origin. Any suggestions as to how to further such a positive and open environment will be appreciated and given serious consideration.

Diminished mental health can interfere with optimal academic performance. The source of symptoms might be related to your course work; if so, please speak with us. However, problems with other parts of your life can also contribute to decreased academic performance. The University Counseling Center (UCC) provides cost-free and confidential mental health services to help you manage personal challenges that threaten your emotional or academic well-being. Remember, getting help is a smart and courageous thing to do — for yourself and for those who care about you. For more resources please see ucc.nd.edu. The UCC is located on the third floor of Saint Liam Hall Phone: 574-631-7336. Hours: Monday-Friday 8:30am – 5:00pm. Urgent Crisis Line 24/7. 

Any student who has a documented disability and is registered with Disability Services should speak with the professor as soon as possible regarding accommodations. Students who are not registered should contact the [Office of Disability Services](https://sarabeadisabilityservices.nd.edu/). 
