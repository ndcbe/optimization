#!/usr/bin/env bash

# Build the packaged MyST book theme consumed by this repository.
#
# Run from the repository root:
#   bash scripts/build_theme_dist.sh
#
# Source of truth:
#   vendor/myst-theme
#
# Generated artifact:
#   themes/pyomo-book-theme-dist
#
# This script intentionally keeps the raw vendored theme source separate from
# the packaged theme directory used by `myst.yml`.

set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
SOURCE_ROOT="${ROOT_DIR}/vendor/myst-theme"
TEMPLATE_STUB_DIR="${SOURCE_ROOT}/template"
BOOK_THEME_SRC_DIR="${SOURCE_ROOT}/themes/book"
DIST_THEME_DIR="${ROOT_DIR}/themes/pyomo-book-theme-dist"

# Remix v1 attempts to reserve a dev websocket port during config loading,
# even for production builds. In constrained environments that bind can fail,
# so we provide a fixed port value to skip the probe entirely.
REMIX_DEV_SERVER_WS_PORT_VALUE="${REMIX_DEV_SERVER_WS_PORT_VALUE:-8002}"

# Use the maintainer environment's npm when available rather than assuming PATH
# resolution will remain stable in every subshell.
NPM_BIN="${NPM_BIN:-$(command -v npm || true)}"

require_file() {
    local path="$1"
    if [[ ! -e "${path}" ]]; then
        echo "Required path not found: ${path}" >&2
        exit 1
    fi
}

require_command() {
    local path="$1"
    local name="$2"
    if [[ -z "${path}" ]]; then
        echo "Required command not found on PATH: ${name}" >&2
        exit 1
    fi
}

echo "Preparing distributable theme from vendored myst-theme subtree"

require_file "${SOURCE_ROOT}/package.json"
require_file "${BOOK_THEME_SRC_DIR}/package.json"
require_file "${BOOK_THEME_SRC_DIR}/template.yml"
require_file "${TEMPLATE_STUB_DIR}/package.json"
require_file "${TEMPLATE_STUB_DIR}/server.js"
require_command "${NPM_BIN}" "npm"

echo "Installing/updating vendored theme workspace dependencies"
(cd "${SOURCE_ROOT}" && "${NPM_BIN}" install)

echo "Building required myst-theme workspace packages"
(cd "${SOURCE_ROOT}" && "${NPM_BIN}" run build -- --filter='./packages/*')

echo "Building production book theme assets"
(cd "${BOOK_THEME_SRC_DIR}" && REMIX_DEV_SERVER_WS_PORT="${REMIX_DEV_SERVER_WS_PORT_VALUE}" "${NPM_BIN}" run prod:build)

require_file "${BOOK_THEME_SRC_DIR}/public"
require_file "${BOOK_THEME_SRC_DIR}/build"

rm -rf "${DIST_THEME_DIR}"
mkdir -p "${DIST_THEME_DIR}"

# Copy the packaged template shell and generated theme assets into the
# repository-local distributable directory that MyST will consume.
cp "${TEMPLATE_STUB_DIR}/server.js" "${DIST_THEME_DIR}/server.js"
cp "${BOOK_THEME_SRC_DIR}/template.yml" "${DIST_THEME_DIR}/template.yml"
cp -R "${BOOK_THEME_SRC_DIR}/public" "${DIST_THEME_DIR}/public"
cp -R "${BOOK_THEME_SRC_DIR}/build" "${DIST_THEME_DIR}/build"

echo "Generating distributable package.json"
python - "${TEMPLATE_STUB_DIR}/package.json" "${SOURCE_ROOT}/packages/site/package.json" "${DIST_THEME_DIR}/package.json" <<'PY'
from pathlib import Path
import json
import sys

template_path = Path(sys.argv[1])
version_path = Path(sys.argv[2])
output_path = Path(sys.argv[3])

template = json.loads(template_path.read_text())
site_pkg = json.loads(version_path.read_text())

template["name"] = "@myst-theme/book"
template["version"] = site_pkg["version"]

output_path.write_text(json.dumps(template, indent=2) + "\n")
PY

echo "Generating distributable package-lock.json"
(cd "${DIST_THEME_DIR}" && "${NPM_BIN}" install)

# The lockfile is needed by MyST, but vendoring node_modules would add a large
# amount of noise to this repository, so remove it after the lockfile is written.
rm -rf "${DIST_THEME_DIR}/node_modules"

echo "Theme artifact ready at:"
echo "  ${DIST_THEME_DIR}"
echo
echo "myst.yml should reference:"
echo "  site.template: themes/pyomo-book-theme-dist"
