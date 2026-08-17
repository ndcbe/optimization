# Nonlinear and Stochastic Optimization

CBE/ACMS 40499 and 60499 at the University of Notre Dame

Prof. Alexander Dowling (dowlinglab.nd.edu)

https://ndcbe.github.io/optimization

---

## Running the notebooks

Most students should use **Google Colab** — every notebook has an "Open in Colab" button, and nothing needs to
be installed. The instructions below are for running the notebooks locally, or for contributing to this website.

### 1. Install conda

[Miniforge](https://github.com/conda-forge/miniforge) (recommended) or
[Anaconda](https://www.anaconda.com/download).

### 2. Create the environment

One environment covers both jobs: running the notebooks and building the website.

```bash
conda env create -f environment.yml
conda activate optimization_fall2026
```

### 3. Install the optimization solvers

IDAES distributes prebuilt binaries for Ipopt and friends:

```bash
idaes get-extensions
```

They install to `~/.idaes/bin`. Add that directory to your `PATH` so Pyomo can find them:

```bash
export PATH="$HOME/.idaes/bin:$PATH"
```

Add that line to your `~/.zshrc` or `~/.bashrc` to make it permanent. Verify with:

```bash
ipopt --version
```

### 4. Launch JupyterLab

```bash
jupyter lab
```

Verified 2026-08-17 on macOS (Apple Silicon): Python 3.13.15, Pyomo 6.10.1, Ipopt 3.13.2.

---

## Contributing to the website

See the [contribution instructions](https://ndcbe.github.io/optimization/org/contribute.html) for the fork,
branch, and pull request workflow.

### Repository layout

Notebooks are authored in `notebooks/<N>-dev/` and **published** to `notebooks/<N>/` by a processing script.

> **Edit the `-dev` copy.** Anything you change in `notebooks/<N>/` is overwritten on the next build.

The script strips in-class activity solutions, rewrites relative data and media paths to absolute URLs so the
notebooks run in Colab, and converts the coloured activity boxes into admonitions.

```bash
python ./scripts/process_notebooks.py
```

Assignment notebooks come from a separate private repository that must be checked out as a **sibling
directory** (`../optimization-private`). Without it, the assignment step of the script will fail.

### Building the site

> **Note:** the site is mid-migration from JupyterBook 1 to
> [JupyterBook 2 / MyST](https://next.jupyterbook.org). The `environment.yml` above installs JupyterBook 2,
> which requires the `myst.yml` configuration that is still being written. Until that lands, the build
> commands here will not work against the `_config.yml` / `_toc.yml` files currently in the repository.

Once the migration is complete:

```bash
python ./scripts/process_notebooks.py
jupyter-book build --html
```

Publishing to GitHub Pages happens automatically from `main` via GitHub Actions.
