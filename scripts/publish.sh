#!/usr/bin/env bash
# PUBLISHING IS AUTOMATIC. This script no longer publishes anything.
#
# ---------------------------------------------------------------------------
# Neutralised 2026-08-18. It used to run:
#
#     jb build ../optimization/          # JupyterBook 1, no longer exists
#     ghp-import -n -p -f _build/html    # FORCE-PUSH to gh-pages
#
# Both halves were hazards. `jb build` fails on the JupyterBook 2 toolchain, and
# the force-push would then have published whatever stale _build/html happened
# to be lying around -- silently clobbering the live site from a local machine,
# bypassing CI entirely.
#
# The site now deploys from .github/workflows/build-and-publish.yml on every
# push to main.
# ---------------------------------------------------------------------------
set -euo pipefail
cat <<'MSG'
This script does not publish. The site deploys automatically from CI
(.github/workflows/build-and-publish.yml) on every push to main.

To publish:

  1. conda activate optimization_fall2026
  2. python ./scripts/process_notebooks.py     # CI cannot do this: it reads
                                               # ../optimization-private
  3. Confirm no solutions leaked. BOTH checks, not just the first -- a solution
     leaks through a cell's stored OUTPUTS as readily as through its source, and
     the grep sees only the source:

       grep -rl "BEGIN SOLUTION" notebooks/ | grep -v -- "-dev/"

       python - <<'PY'
       import json, glob
       bad = [(f, i) for f in glob.glob("notebooks/assignments/*.ipynb")
              for i, c in enumerate(json.load(open(f))["cells"])
              if c["cell_type"] == "code"
              and "Add your solution here" in "".join(c["source"])
              and c.get("outputs")]
       print(bad or "clean")
       PY

     Both must print nothing / "clean".
  4. Commit the regenerated notebooks/N/ output.
  5. git push origin main

To preview locally first: ./scripts/build_local.sh
MSG
exit 0
