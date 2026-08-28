#!/usr/bin/env python3
"""Audit media used by live MyST pages.

Hard failures are deliberately narrow: a local image referenced by a live page
is missing, has the wrong filename case, or escapes the repository. Matters
that require editorial judgement are warnings.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
from dataclasses import asdict, dataclass
from pathlib import Path
from urllib.parse import unquote, urlparse


SCRIPT_DIR = Path(__file__).resolve().parent
REPO_ROOT = SCRIPT_DIR.parent
DEFAULT_MYST = REPO_ROOT / "myst.yml"
FILE_RE = re.compile(r"^-?\s*file:\s*['\"]?([^'\"#]+?)['\"]?\s*$")
MD_IMAGE_RE = re.compile(r"!\[([^]]*)\]\(([^)]+)\)")
HTML_IMAGE_RE = re.compile(r"<img\b(?P<attrs>[^>]*)>", re.I | re.S)
ATTR_RE = re.compile(
    r"\b(?P<name>src|alt)\s*=\s*(?P<quote>['\"])(?P<value>.*?)(?P=quote)",
    re.I | re.S,
)
MEDIA_EXTS = {
    ".avif", ".bmp", ".gif", ".jpeg", ".jpg", ".pdf", ".png", ".svg",
    ".tif", ".tiff", ".webp",
}
RAW_PREFIXES = (
    "https://raw.githubusercontent.com/ndcbe/optimization/main/",
    "https://github.com/ndcbe/optimization/raw/main/",
)
SUSPICIOUS_RE = re.compile(
    r"\b(screenshot|textbook|book crop|figure from|bieglerfigure)\b", re.I
)


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    page: str
    location: str
    reference: str
    detail: str


def parse_live_pages(myst_file: Path) -> list[Path]:
    """Read active ``file:`` entries from MyST without needing PyYAML."""
    pages: list[Path] = []
    seen: set[Path] = set()
    for raw in myst_file.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        match = FILE_RE.match(line)
        if not match:
            continue
        candidate = (myst_file.parent / match.group(1).strip()).resolve()
        if candidate.suffix in {".ipynb", ".md"} and candidate not in seen:
            pages.append(candidate)
            seen.add(candidate)
    return pages


def source_for_page(page: Path, repo_root: Path) -> Path:
    """Map a generated chapter notebook to its ``-dev`` golden copy."""
    try:
        rel = page.relative_to(repo_root)
    except ValueError:
        return page
    if page.suffix != ".ipynb" or len(rel.parts) < 3:
        return page
    parent = rel.parent
    if parent.name.isdigit() or parent.name == "contrib":
        candidate = repo_root / parent.parent / f"{parent.name}-dev" / rel.name
        if candidate.exists():
            return candidate
    return page


def extract_refs(text: str) -> list[tuple[str, str]]:
    """Return ``(alt, src)`` pairs for Markdown and HTML images."""
    refs: list[tuple[str, str]] = []
    for match in MD_IMAGE_RE.finditer(text):
        target = match.group(2).strip()
        if not target.startswith("<"):
            target = re.split(r"\s+(?=['\"])", target, maxsplit=1)[0]
        refs.append((match.group(1).strip(), target.strip("<>")))
    for match in HTML_IMAGE_RE.finditer(text):
        attrs = {
            item.group("name").lower(): item.group("value")
            for item in ATTR_RE.finditer(match.group("attrs"))
        }
        if "src" in attrs:
            refs.append((attrs.get("alt", "").strip(), attrs["src"].strip()))
    return refs


def page_text_and_metadata(path: Path) -> tuple[str, list[tuple[str, str]], int, int]:
    if path.suffix == ".md":
        text = path.read_text(encoding="utf-8", errors="replace")
        return text, extract_refs(text), 0, 0
    notebook = json.loads(path.read_text(encoding="utf-8"))
    chunks: list[str] = []
    attachments = 0
    png_outputs = 0
    for cell in notebook.get("cells", []):
        if cell.get("cell_type") == "markdown":
            chunks.append("".join(cell.get("source", [])))
            attachments += len(cell.get("attachments", {}))
        png_outputs += sum(
            "image/png" in output.get("data", {})
            for output in cell.get("outputs", []) or []
        )
    text = "\n".join(chunks)
    return text, extract_refs(text), attachments, png_outputs


def exact_case_status(path: Path) -> tuple[bool, str | None]:
    """Check existence and exact case one path component at a time."""
    current = Path(path.anchor) if path.is_absolute() else Path(".")
    parts = path.parts[1:] if path.is_absolute() else path.parts
    for part in parts:
        if not current.is_dir():
            return False, "parent directory is missing"
        names = {entry.name for entry in current.iterdir()}
        if part not in names:
            folded = [name for name in names if name.casefold() == part.casefold()]
            if folded:
                return False, f"case mismatch; disk has {folded[0]!r}"
            return False, "path component is missing"
        current /= part
    return current.is_file(), None if current.is_file() else "file is missing"


def local_target(src: str, source: Path, repo_root: Path) -> Path | None:
    """Resolve a media reference when it names this repository."""
    for prefix in RAW_PREFIXES:
        if src.startswith(prefix):
            tail = unquote(src[len(prefix):].split("?", 1)[0])
            return (repo_root / tail).resolve()
    parsed = urlparse(src)
    if parsed.scheme in {"http", "https", "data"} or src.startswith("//"):
        return None
    if src.startswith("attachment:"):
        return None
    clean = unquote(src.split("#", 1)[0].split("?", 1)[0])
    if not clean:
        return None
    if clean.startswith("/"):
        return (repo_root / clean.lstrip("/")).resolve()
    return (source.parent / clean).resolve()


def relative(path: Path, root: Path) -> str:
    try:
        return path.relative_to(root).as_posix()
    except ValueError:
        return str(path)


def audit(myst_file: Path, repo_root: Path) -> tuple[list[Finding], dict]:
    myst_file = myst_file.resolve()
    repo_root = repo_root.resolve()
    findings: list[Finding] = []
    referenced_media: set[Path] = set()
    pages = parse_live_pages(myst_file)
    explicit_refs = attachments = png_outputs = 0

    for published in pages:
        source = source_for_page(published, repo_root)
        page_name = relative(published, repo_root)
        source_name = relative(source, repo_root)
        if not published.exists():
            findings.append(Finding(
                "ERROR", "missing-page", page_name, source_name, "",
                "MyST page does not exist",
            ))
            continue
        text, refs, attachment_count, output_count = page_text_and_metadata(source)
        explicit_refs += len(refs)
        attachments += attachment_count
        png_outputs += output_count
        if attachment_count:
            findings.append(Finding(
                "WARN", "notebook-attachment", page_name, source_name, "",
                f"{attachment_count} embedded notebook attachment(s)",
            ))
        if SUSPICIOUS_RE.search(text):
            snippets = sorted({m.group(0) for m in SUSPICIOUS_RE.finditer(text)})
            findings.append(Finding(
                "WARN", "provenance-language", page_name, source_name, "",
                "suspicious provenance wording: " + ", ".join(snippets),
            ))

        for alt, src in refs:
            if not alt:
                findings.append(Finding(
                    "WARN", "missing-alt", page_name, source_name, src[:180],
                    "image has empty alt text",
                ))
            if src.startswith("data:"):
                findings.append(Finding(
                    "WARN", "embedded-data-image", page_name, source_name,
                    src[:32] + "…", "base64/data image is embedded in page source",
                ))
                continue
            if src.startswith("attachment:"):
                findings.append(Finding(
                    "WARN", "attachment-reference", page_name, source_name, src,
                    "image uses a notebook attachment rather than a repository asset",
                ))
                continue
            target = local_target(src, source, repo_root)
            if target is None:
                if urlparse(src).scheme in {"http", "https"} or src.startswith("//"):
                    findings.append(Finding(
                        "WARN", "remote-image", page_name, source_name, src[:240],
                        "externally hosted image; availability and licence need review",
                    ))
                continue
            try:
                target.relative_to(repo_root)
            except ValueError:
                findings.append(Finding(
                    "ERROR", "path-escape", page_name, source_name, src,
                    f"local image resolves outside repository: {target}",
                ))
                continue
            ok, why = exact_case_status(target)
            if not ok:
                findings.append(Finding(
                    "ERROR", "broken-local-image", page_name, source_name, src,
                    why or "unresolved local image",
                ))
            elif target.suffix.lower() in MEDIA_EXTS:
                referenced_media.add(target)

    media_root = repo_root / "media"
    media_files = {
        path.resolve() for path in media_root.rglob("*")
        if path.is_file() and path.suffix.lower() in MEDIA_EXTS
    } if media_root.exists() else set()

    myst_text = myst_file.read_text(encoding="utf-8")
    for raw in re.findall(r"(?:logo|favicon):\s*['\"]?([^'\"\s]+)", myst_text):
        candidate = (repo_root / raw).resolve()
        if candidate in media_files:
            referenced_media.add(candidate)

    orphans = sorted(media_files - referenced_media)
    for path in orphans:
        findings.append(Finding(
            "INFO", "unreferenced-media", "", relative(path, repo_root), "",
            "not referenced by an active MyST page; may be archival or used outside page bodies",
        ))

    hashes: dict[tuple[int, str], list[Path]] = {}
    for path in media_files:
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        hashes.setdefault((path.stat().st_size, digest), []).append(path)
    duplicate_groups = [sorted(group) for group in hashes.values() if len(group) > 1]
    for group in sorted(duplicate_groups, key=lambda value: str(value[0])):
        findings.append(Finding(
            "INFO", "duplicate-media", "", relative(group[0], repo_root), "",
            "byte-identical to " + ", ".join(relative(p, repo_root) for p in group[1:]),
        ))

    summary = {
        "live_pages": len(pages),
        "notebooks": sum(page.suffix == ".ipynb" for page in pages),
        "markdown_pages": sum(page.suffix == ".md" for page in pages),
        "explicit_image_references": explicit_refs,
        "notebook_attachments": attachments,
        "stored_png_outputs": png_outputs,
        "media_files": len(media_files),
        "referenced_media_files": len(referenced_media),
        "unreferenced_media_files": len(orphans),
        "duplicate_media_groups": len(duplicate_groups),
        "errors": sum(f.severity == "ERROR" for f in findings),
        "warnings": sum(f.severity == "WARN" for f in findings),
        "info": sum(f.severity == "INFO" for f in findings),
    }
    return findings, summary


def print_report(findings: list[Finding], summary: dict) -> None:
    print("Live-page media audit")
    print("  " + " · ".join(
        f"{key.replace('_', ' ')}: {value}" for key, value in summary.items()
    ))
    for finding in findings:
        if finding.severity == "INFO":
            continue
        where = finding.page or finding.location
        ref = f" -> {finding.reference}" if finding.reference else ""
        print(f"  [{finding.severity}] {finding.code}: {where}{ref}")
        print(f"          {finding.detail}")
    print("\nINFO findings are available with --json-out.")


def selftest() -> int:
    with tempfile.TemporaryDirectory() as tmp:
        root = Path(tmp)
        (root / "notebooks/1-dev").mkdir(parents=True)
        (root / "notebooks/1").mkdir(parents=True)
        (root / "media").mkdir()
        (root / "media/Good.png").write_bytes(b"good")
        notebook = {
            "cells": [{
                "cell_type": "markdown", "metadata": {},
                "source": [
                    "![good](../../media/Good.png)\n",
                    "![](../../media/good.png)\n",
                    "![missing](../../media/missing.png)\n",
                    "![remote](https://example.com/figure.png)\n",
                    "![embedded](data:image/png;base64,AAAA)\n",
                ],
            }],
            "metadata": {}, "nbformat": 4, "nbformat_minor": 5,
        }
        payload = json.dumps(notebook)
        (root / "notebooks/1-dev/test.ipynb").write_text(payload)
        (root / "notebooks/1/test.ipynb").write_text(payload)
        myst = root / "myst.yml"
        myst.write_text("- file: notebooks/1/test.ipynb\n")
        findings, summary = audit(myst, root)
        codes = [finding.code for finding in findings]
        checks = {
            "valid local image passes": summary["referenced_media_files"] == 1,
            "case mismatch fails": any(
                finding.code == "broken-local-image"
                and "case mismatch" in finding.detail
                for finding in findings
            ),
            "missing image fails": codes.count("broken-local-image") == 2,
            "remote image warns": "remote-image" in codes,
            "embedded image warns": "embedded-data-image" in codes,
            "empty alt warns": "missing-alt" in codes,
            "hard findings produce nonzero": summary["errors"] == 2,
        }
        failed = [name for name, passed in checks.items() if not passed]
        for name, passed in checks.items():
            print(f"  {'OK  ' if passed else 'FAIL'} {name}")
        if failed:
            print("SELF-TEST FAILED: " + ", ".join(failed))
            return 1
        print("SELF-TEST PASSED")
        return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--myst", type=Path, default=DEFAULT_MYST)
    parser.add_argument("--json-out", type=Path)
    parser.add_argument("--selftest", action="store_true")
    args = parser.parse_args()
    if args.selftest:
        return selftest()
    if not args.myst.is_file():
        parser.error(f"MyST configuration does not exist: {args.myst}")
    myst = args.myst.resolve()
    findings, summary = audit(myst, myst.parent)
    print_report(findings, summary)
    if args.json_out:
        payload = {
            "summary": summary,
            "findings": [asdict(finding) for finding in findings],
        }
        args.json_out.write_text(json.dumps(payload, indent=2) + "\n", encoding="utf-8")
        print(f"Wrote {args.json_out}")
    return 1 if summary["errors"] else 0


if __name__ == "__main__":
    sys.exit(main())
