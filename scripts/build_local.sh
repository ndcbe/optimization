#!/usr/bin/env bash
# Build the site locally, for preview only.
#
#     ./scripts/build_local.sh
#
# Publishing is NOT done from here -- see scripts/publish.sh and
# .github/workflows/build-and-publish.yml.
#
# ---------------------------------------------------------------------------
# Updated 2026-08-18 for JupyterBook 2. It previously called `jb build`, a
# JupyterBook 1 command that no longer exists in this environment, so the
# script could not work at all.
#
# THREE THINGS THAT BITE:
#
# 1. node lives in the conda environment's bin and is NOT on the default PATH.
#    Without it, jupyter-book stops with a "Node.js not found" install prompt.
#
# 2. process_notebooks.py must run BEFORE the build. It generates notebooks/N/
#    from notebooks/N-dev/ and strips the solution blocks. CI deliberately does
#    NOT run it -- it reads assignments from ../optimization-private, which CI
#    cannot see -- so a local build is the only place it happens.
#
# 3. scripts/build_theme_dist.sh must also run BEFORE the build. The packaged
#    theme's build/ bundle is not committed (see DEVELOPER.md) -- it is a
#    build artifact, regenerated fresh from vendor/myst-theme every run, in
#    CI and locally alike. Skipping this does not error; myst falls back to
#    the stock theme silently, and the Colab button just isn't there.
# ---------------------------------------------------------------------------
set -euo pipefail
cd "$(dirname "$0")/.."

ENV_BIN="${CONDA_PREFIX:-$HOME/opt/anaconda3/envs/optimization_fall2026}/bin"
[ -d "$ENV_BIN" ] && export PATH="$ENV_BIN:$PATH"

command -v jupyter-book >/dev/null 2>&1 || {
  echo "jupyter-book not found. Activate the environment first:"
  echo "    conda activate optimization_fall2026"
  exit 1
}

command -v npm >/dev/null 2>&1 || {
  echo "npm not found. Needed to build themes/pyomo-book-theme-dist (see DEVELOPER.md)."
  exit 1
}

echo "==> Building packaged custom theme from vendor/myst-theme"
bash ./scripts/build_theme_dist.sh

echo "==> Generating published notebooks from -dev sources"
python ./scripts/process_notebooks.py

echo "==> Checking no solutions leaked into published notebooks"
# NOT a grep. A solution leaks through a cell's stored OUTPUTS as readily as
# through its source, and `grep -r "BEGIN SOLUTION"` sees only the source -- it
# was clean throughout the 2026-08-21 leak, while 32 cells published their
# answers as output. check_solution_leaks.py checks both, plus the drop-output
# tag; run it with --selftest to watch it fail on purpose.
python ./scripts/check_solution_leaks.py || {
  echo "FAIL: solution content found in PUBLISHED notebooks. Not building."
  exit 1
}

echo "==> Building"
jupyter-book build --html

echo
echo "Built. Open _build/html/index.html"
