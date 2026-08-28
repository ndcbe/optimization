#!/usr/bin/env bash
# Run the public repository's verification tools through one honest entry point.
#
# USAGE
#   ./scripts/verify_all.sh --fast      repository-local deterministic checks
#   ./scripts/verify_all.sh --full      --fast, then sibling/code-sync and solvers
#   ./scripts/verify_all.sh --selftest  prove every checker with a self-test fails
#   ./scripts/verify_all.sh --help
#
# `--fast` is suitable for CI: it does not require optimization-private or a
# solver. It does require the Python dependencies from environment.yml.
# `--full` is the maintainer gate: it additionally reads the sibling private
# repository and executes the authored notebooks with their solver calls.
set -uo pipefail
cd "$(dirname "$0")/.."

OPTIMIZATION_ENV_BIN="${CONDA_PREFIX:-$HOME/opt/anaconda3/envs/optimization_fall2026}/bin"
[ -d "$OPTIMIZATION_ENV_BIN" ] && export PATH="$OPTIMIZATION_ENV_BIN:$PATH"
export PATH="$HOME/.idaes/bin:$PATH"

MODE="${1:-}"
case "$MODE" in
  --fast|--full|--selftest) ;;
  -h|--help)
    sed -n '2,13p' "$0" | sed 's/^# \{0,1\}//'
    exit 0
    ;;
  "")
    echo "verify_all.sh: choose --fast, --full, or --selftest" >&2
    exit 2
    ;;
  *)
    echo "verify_all.sh: unknown argument '$MODE'" >&2
    exit 2
    ;;
esac

FAILED=()

run_check() {
  local label="$1"
  shift
  printf '\n==> %s\n' "$label"
  if "$@"; then
    echo "PASS: $label"
  else
    local status=$?
    echo "FAIL ($status): $label"
    FAILED+=("$label")
  fi
}

finish() {
  printf '\n------------------------------------------------------------\n'
  if [ ${#FAILED[@]} -eq 0 ]; then
    echo "ALL GREEN"
    exit 0
  fi
  echo "FAILING (${#FAILED[@]}):"
  printf '  %s\n' "${FAILED[@]}"
  exit ${#FAILED[@]}
}

if [ "$MODE" = "--selftest" ]; then
  run_check "notebook publisher self-test" python scripts/process_notebooks.py --selftest
  run_check "solution-leak self-test" python scripts/check_solution_leaks.py --selftest
  run_check "notebook-content self-test" python scripts/check_notebook_content.py --selftest
  run_check "prose-baseline self-test" python scripts/check_prose_baseline.py --selftest
  run_check "AI-review-status self-test" python scripts/build_ai_review_status.py --selftest
  run_check "Pyomo-code extraction self-test" python scripts/extract_pyomo_code.py --selftest
  run_check "result-freshness self-test" python scripts/check_results_fresh.py --selftest
  run_check "live-page media self-test" python scripts/check_media.py --selftest
  run_check "greyscale self-test" python scripts/check_greyscale.py --selftest
  run_check "archived-result renderer self-test" python figures/render_from_notebook.py --selftest
  finish
fi

run_check "published notebook content" python scripts/check_notebook_content.py
run_check "solution-leak scan" python scripts/check_solution_leaks.py
run_check "prose baseline" python scripts/check_prose_baseline.py
run_check "AI review registry" python scripts/build_ai_review_status.py --check
run_check "deterministic Sudoku data" python scripts/generate_sudoku_puzzles.py --check
run_check "archived result freshness" python scripts/check_results_fresh.py
run_check "live-page media references" python scripts/check_media.py
run_check "figure source-name collisions" make -C figures names
run_check "figure style in greyscale" python scripts/check_greyscale.py --style figures/dowling.mplstyle -n 4
run_check "committed figures in greyscale" python scripts/check_greyscale.py media/figures

if [ "$MODE" = "--full" ]; then
  PRIVATE_REPO="$(cd .. && pwd)/optimization-private"
  if [ -d "$PRIVATE_REPO/lecture-notes/code" ]; then
    run_check "notebook-to-handout Pyomo code sync" python scripts/extract_pyomo_code.py --check
  else
    echo "FAIL: sibling repository not found at $PRIVATE_REPO"
    FAILED+=("sibling repository")
  fi
  run_check "authored notebook execution" python scripts/run_notebooks_from_myst.py --source dev
fi

finish
