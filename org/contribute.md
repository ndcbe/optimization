# Contribution Instructions

## Step 1: Create a GitHub Account

Keep the username professional and do not include personal identifying information such as your birthday or birthyear.

## Step 2: Create a Fork in GitHub

On GitHub for the [class repository](https://github.com/ndcbe/optimization), find the bottom to create a fork:

![](/media/contrib_instructions/fork1.png)

Then create a fork under your username. It is best to keep the default settings:

![](/media/contrib_instructions/fork2.png)


## Step 3: Create a Branch in GitHub

On GitHub, find the drop down box containing "Branch:".

![](/media/contrib_instructions/create-branch.png)

To create a branch, type a meaningful name such as your project description or your last names. Do not include spaces.

## Step 4: Upload your .ipynb File

First, rename your `.ipynb` file to contain a few descriptive words. You may use `-` instead of spaces. For example, `Systems-Bio-Regression.ipynb`.

Select your new branch from the dropdown menu. Then navigate to the `/notebooks/contrib-dev` folder and choose the **Upload files button**.

![](/media/contrib_instructions/upload-files.png)

### Step 5: Create a Pull Request

On the [main class repository](https://github.com/ndcbe/data-and-computing), create a pull request to merge your branch on your fork into the `contributed-notebooks` branch on the main class repository. After uploading the new notebook file to your branch, you should see an orange/yellow box with your branch name.

![](/media/contrib_instructions/pull-request1.png)

Choose **Compare & pull request**.

This should take you to a screen with the title **Open a pull request**:

![](/media/contrib_instructions/pull-request2.png)

Make sure you see **main <-- your branch name**. Then add a descriptive comment (what did you change) and click **Create pull request**.

Tag `@adowling2` in the comments of your pull request.

### Step 6: Run JypyterBook to Publish to the Class Website