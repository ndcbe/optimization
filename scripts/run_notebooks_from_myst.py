#!/usr/bin/env python3
"""Execute the notebooks listed in ``myst.yml`` and report what passes.

Ported from ``~/DowlingLab/Teaching/pyomo-doe/scripts/run_notebooks_from_myst.py``
and adapted to this repository's ``-dev`` / published split.

Which copy gets executed
------------------------
``myst.yml`` lists the *published* notebooks (``notebooks/<N>/``), but those are
generated output: ``scripts/process_notebooks.py`` strips ``### BEGIN SOLUTION``
blocks out of them and rewrites ``../data/`` to a raw.githubusercontent URL.
Executing a published copy therefore tests neither the notebook an author would
fix nor the code an author wrote.  The default (``--source dev``) maps each
published path back to its ``notebooks/<N>-dev/`` source, and maps
``notebooks/assignments/`` back to the private instructor repo.  Use
``--source published`` to test the site copies as students receive them.

Solver binaries
---------------
``~/.idaes/bin`` is prepended to ``PATH`` so ``ipopt``, ``k_aug`` and
``dot_sens`` resolve, exactly as in the pyomo-doe harness.

Each notebook runs in its own subprocess so that a kernel crash or a hang is
reported as such instead of taking the whole pass down.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
import time
from pathlib import Path

NOTEBOOK_FILE_RE = re.compile(r"^-?\s*file:\s*['\"]?([^'\"]+\.ipynb)['\"]?\s*$")
SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DEFAULT_MYST_FILE = REPO_ROOT / "myst.yml"
IDAES_BIN_DIR = Path("~/.idaes/bin").expanduser()
PRIVATE_REPO = REPO_ROOT.parent / "optimization-private"

# published directory -> source directory, applied to the parent of each entry
SOURCE_DIR_MAP = {
    **{f"notebooks/{n}": f"notebooks/{n}-dev" for n in list("12345678") + ["contrib"]},
    "notebooks/assignments": None,  # handled specially: lives in the private repo
}


def log(message: str, *, stream=None) -> None:
    print(message, file=stream, flush=True)


def parse_active_notebooks(myst_file: Path) -> list[Path]:
    """Return the notebooks listed in the TOC, skipping commented-out lines."""
    notebooks: list[Path] = []
    seen: set[Path] = set()

    for raw_line in myst_file.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        match = NOTEBOOK_FILE_RE.match(line)
        if not match:
            continue

        notebook_path = Path(match.group(1).strip())
        if not notebook_path.is_absolute():
            notebook_path = (myst_file.parent / notebook_path).resolve()

        if notebook_path not in seen:
            notebooks.append(notebook_path)
            seen.add(notebook_path)

    return notebooks


def to_source_path(published: Path) -> Path:
    """Map a published notebook path to the source that generated it."""
    try:
        rel = published.relative_to(REPO_ROOT)
    except ValueError:
        return published

    parent = rel.parent.as_posix()
    if parent == "notebooks/assignments":
        return PRIVATE_REPO / "notebooks" / "assignments" / rel.name
    mapped = SOURCE_DIR_MAP.get(parent)
    if mapped:
        return REPO_ROOT / mapped / rel.name
    return published


def prepend_idaes_bin_to_path() -> None:
    if not IDAES_BIN_DIR.exists():
        return
    current_path = os.environ.get("PATH", "")
    idaes_bin = str(IDAES_BIN_DIR)
    if idaes_bin in (current_path.split(os.pathsep) if current_path else []):
        return
    os.environ["PATH"] = (
        f"{idaes_bin}{os.pathsep}{current_path}" if current_path else idaes_bin
    )


# --------------------------------------------------------------------------
# child process: execute exactly one notebook and emit a JSON result line
# --------------------------------------------------------------------------


def execute_one(path: Path, timeout: int, kernel_name: str | None) -> dict:
    import nbformat
    from nbclient import NotebookClient
    from nbclient.exceptions import CellExecutionError

    with path.open(encoding="utf-8") as fh:
        notebook = nbformat.read(fh, as_version=4)

    resolved_kernel = (
        kernel_name
        or notebook.get("metadata", {}).get("kernelspec", {}).get("name")
        or "python3"
    )

    client = NotebookClient(
        notebook,
        timeout=timeout,
        kernel_name=resolved_kernel,
        resources={"metadata": {"path": str(path.parent)}},
        allow_errors=False,
    )
    try:
        client.execute()
    except CellExecutionError as err:
        return {
            "status": "FAIL",
            "error_type": type(err).__name__,
            "ename": getattr(err, "ename", None),
            "evalue": getattr(err, "evalue", None),
            "cell_index": _failing_cell_index(notebook),
            "source_head": _failing_cell_source(notebook),
            "traceback_tail": _traceback_tail(notebook),
        }
    except Exception as err:  # kernel death, timeout, nbformat problems
        return {
            "status": "ERROR",
            "error_type": type(err).__name__,
            "evalue": str(err)[:500],
            "cell_index": _failing_cell_index(notebook),
        }
    return {"status": "PASS"}


def _failing_cell_index(notebook) -> int | None:
    for idx, cell in enumerate(notebook.cells):
        for output in cell.get("outputs", []) or []:
            if output.get("output_type") == "error":
                return idx
    return None


def _failing_cell_source(notebook) -> str | None:
    idx = _failing_cell_index(notebook)
    if idx is None:
        return None
    return "\n".join(notebook.cells[idx].source.splitlines()[:6])


def _traceback_tail(notebook) -> str | None:
    idx = _failing_cell_index(notebook)
    if idx is None:
        return None
    for output in notebook.cells[idx].get("outputs", []) or []:
        if output.get("output_type") == "error":
            tb = output.get("traceback") or []
            clean = [re.sub(r"\x1b\[[0-9;]*m", "", line) for line in tb]
            return "\n".join(clean)[-1500:]
    return None


# --------------------------------------------------------------------------


def run_in_subprocess(path: Path, cell_timeout: int, wall_timeout: int,
                      kernel_name: str | None) -> dict:
    cmd = [sys.executable, str(Path(__file__).resolve()),
           "--_exec", str(path), "--timeout", str(cell_timeout)]
    if kernel_name:
        cmd += ["--kernel-name", kernel_name]
    try:
        proc = subprocess.run(
            cmd, capture_output=True, text=True, timeout=wall_timeout,
            env=os.environ.copy(),
        )
    except subprocess.TimeoutExpired:
        return {"status": "TIMEOUT",
                "evalue": f"exceeded wall timeout of {wall_timeout}s"}

    for line in reversed(proc.stdout.splitlines()):
        if line.startswith("__RESULT__"):
            return json.loads(line[len("__RESULT__"):])
    return {"status": "ERROR", "error_type": "HarnessError",
            "evalue": (proc.stderr or proc.stdout)[-800:]}


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Execute the active notebooks listed in myst.yml.")
    parser.add_argument("myst_file", nargs="?", default=str(DEFAULT_MYST_FILE))
    parser.add_argument("--source", choices=["dev", "published"], default="dev",
                        help="Which copy to execute (default: dev sources).")
    parser.add_argument("--timeout", type=int, default=900,
                        help="Per-cell execution timeout in seconds.")
    parser.add_argument("--wall-timeout", type=int, default=1200,
                        help="Per-notebook wall-clock timeout in seconds.")
    parser.add_argument("--kernel-name", default=None)
    parser.add_argument("--list-only", action="store_true")
    parser.add_argument("--only", default=None,
                        help="Substring filter on the notebook path.")
    parser.add_argument("--json-out", default=None,
                        help="Write the per-notebook results to this JSON file.")
    parser.add_argument("--_exec", default=None, help=argparse.SUPPRESS)
    args = parser.parse_args()

    prepend_idaes_bin_to_path()

    # child mode
    if args._exec:
        result = execute_one(Path(args._exec), args.timeout, args.kernel_name)
        print("__RESULT__" + json.dumps(result), flush=True)
        return 0

    myst_file = Path(args.myst_file).resolve()
    if not myst_file.exists():
        log(f"[ERROR] MyST file not found: {myst_file}", stream=sys.stderr)
        return 2

    published = parse_active_notebooks(myst_file)
    entries = []
    for pub in published:
        src = to_source_path(pub) if args.source == "dev" else pub
        entries.append((pub, src))
    if args.only:
        entries = [e for e in entries if args.only in str(e[0])]

    if args.list_only:
        for pub, src in entries:
            mark = "" if src.exists() else "   <-- MISSING"
            log(f"{pub.relative_to(REPO_ROOT)}  ->  {src}{mark}")
        log(f"[INFO] {len(entries)} notebooks")
        return 0

    log(f"[INFO] Running {len(entries)} notebooks from {myst_file} "
        f"(source={args.source})")
    results = []
    started_all = time.time()

    for idx, (pub, src) in enumerate(entries, start=1):
        rel = pub.relative_to(REPO_ROOT).as_posix()
        if not src.exists():
            log(f"[SKIP {idx}/{len(entries)}] {rel}: source not found ({src})")
            results.append({"notebook": rel, "executed": str(src),
                            "status": "NOT RUN", "duration": 0.0,
                            "evalue": "source file not found"})
            continue

        log(f"[RUN {idx}/{len(entries)}] {rel}")
        started = time.time()
        result = run_in_subprocess(src, args.timeout, args.wall_timeout,
                                   args.kernel_name)
        duration = time.time() - started
        result.update({"notebook": rel, "executed": str(src),
                       "duration": round(duration, 1)})
        results.append(result)
        log(f"[{result['status']}] {rel} ({duration:.1f}s) "
            f"{result.get('ename') or result.get('error_type') or ''} "
            f"{(result.get('evalue') or '')[:160]}")

    log(f"[DONE] Completed in {time.time() - started_all:.1f}s")

    if args.json_out:
        Path(args.json_out).write_text(json.dumps(results, indent=2),
                                       encoding="utf-8")
        log(f"[INFO] Results written to {args.json_out}")

    counts: dict[str, int] = {}
    for result in results:
        counts[result["status"]] = counts.get(result["status"], 0) + 1
    log("[SUMMARY] " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))

    return 1 if counts.get("PASS", 0) != len(results) else 0


if __name__ == "__main__":
    raise SystemExit(main())
