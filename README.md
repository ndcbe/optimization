# Optimization for Decision Science

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

Verified 2026-08-17 and again 2026-08-22 on macOS (Apple Silicon), the second time from this file alone on
a machine that had never had the environment: Python 3.13.15, Pyomo 6.10.1, NumPy 2.5.2, pandas 3.0.5,
Ipopt 3.13.2, GLPK 5.0. Pyomo reports `glpk`, `cbc`, `ipopt`, `couenne`, `bonmin`, `appsi_highs` and `k_aug`
all available; `gurobi` needs its own licence and is not expected to work out of the box.

> **If a solver seems missing, check your `PATH` before believing it.** `SolverFactory("glpk").available()`
> returns `False` when `glpsol` is installed but not visible — most often because the interpreter was called
> by its full path instead of activating the environment. The two directories are separate: conda solvers
> (`glpsol`, HiGHS) come from `conda activate`, and the IDAES binaries (`ipopt`, `k_aug`, `dot_sens`, `cbc`,
> `bonmin`, `couenne`) come from `~/.idaes/bin`, which is never added automatically. Nothing about the error
> distinguishes "not installed" from "not on the path".

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

### The prose baseline

The notebooks are a **pre-LLM corpus written in human voices** — mostly Prof. Dowling's, and past students'
in `notebooks/contrib/`. The LaTeX course pack in `../optimization-private/lecture-notes/` is the opposite: a
large amount of AI-drafted prose currently being revised. Because Pyomo models are single-sourced from the
notebooks into the handouts, an editor refining a handout is regularly in both files on the same afternoon,
and handout phrasing can drift backwards into notebook markdown. `scripts/prose_baseline.json` freezes every
markdown cell so that drift is detected rather than hoped against. It has two layers: `anchor`, read with
`git show feb00d2:<path>` from the last commit before agent editing of `-dev` notebooks began on 2026-08-18
and never updated, and `current`, a moving snapshot of the working tree. Each notebook also carries a
**voice** — `dowling`, `contributed`, `ai-drafted`, or `unknown` — with the evidence behind it, because the
goal is to preserve *the voices, plural*: rewriting a student's notebook into Prof. Dowling's voice is as
much a loss as rewriting it into an AI's.

```bash
python ./scripts/check_prose_baseline.py            # vs current; exit 1 on any drift
python ./scripts/check_prose_baseline.py --audit    # vs the anchor: the standing audit
python ./scripts/check_prose_baseline.py --selftest
```

A **CHANGED** cell is the alarm — substitution is how one voice replaces another — while ADDED and REMOVED
cells are usually legitimate. Re-baselining is legitimate too, since prose is meant to be refined, but it
requires `--update --reason "..."`, which records the reason and the date in the JSON; the `anchor` layer
cannot be moved at all. Only markdown cells are covered. Code cells are deliberately excluded, and that
leaves one gap worth naming: `../optimization-private/lecture-notes/check_code_sync.py` asserts that notebook
code cells still match the `\pyomocode{}` listings in the handouts, and the intended direction is
**notebook → handout**. If you change a handout listing and then "fix" the resulting sync failure by editing
the notebook, you have pushed handout content backwards into the pre-LLM corpus. **Resolve a code-sync
failure by re-extracting from the notebook, never by editing the notebook to match the handout.** This
checker will not catch that for you.

### Building the site

The site is built with [JupyterBook 2 / MyST](https://next.jupyterbook.org), configured by `myst.yml`.

```bash
python ./scripts/process_notebooks.py
BASE_URL=/optimization jupyter-book build --html
```

The output lands in `_build/html`. `BASE_URL` matters because the site is served from
`https://ndcbe.github.io/optimization` rather than a domain root; without it every asset and internal link
resolves one level too high and the page renders unstyled.

No `npm install -g mystmd` is needed: the `jupyter-book` pip package in `environment.yml` manages its own
Node toolchain. The bare `myst` command is therefore not on your `PATH`, which is expected — GitHub Actions
installs `mystmd` from npm and calls `myst build --html` instead, and the two are equivalent.

> **Do not delete `_build/`.** The site theme is downloaded at build time, and a GitHub rate-limit response
> fails the build with no diagnostics at all. An incremental rebuild is also far faster.

A clean build currently emits around 115 warnings and no errors. Most are a single mechanical class —
`Duplicate identifier in project`, meaning two notebook cells share an id — so a warning count in that
neighbourhood is the status quo rather than something you broke.

Publishing to GitHub Pages happens automatically from `main` via GitHub Actions.
