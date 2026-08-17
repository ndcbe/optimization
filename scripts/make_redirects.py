#!/usr/bin/env python3
"""Emit redirect stubs for the old JupyterBook 1 URLs.

The site moved from JupyterBook 1 to MyST in August 2026. That changed every
page URL:

    old (JB1)   notebooks/4/SP.html
    new (MyST)  notebooks/4/sp/

MyST lowercases page slugs and converts underscores to hyphens, so essentially
no old link survives. Canvas pages, the legacy CBE60499 site, student
bookmarks, and any external citation would all 404.

This script writes a small HTML stub at each old path that redirects to the new
one. Run it AFTER `myst build --html`, since it writes into the build output:

    myst build --html
    python ./scripts/make_redirects.py

The mapping lives in scripts/legacy_redirects.tsv, one `old<TAB>new` pair per
line, derived from the final _toc.yml (recoverable at c4e9622^) checked against
the actually-deployed page tree. It is a committed data file rather than
computed at build time so the slug rules never have to be re-guessed.

BASE_URL must match the workflow (the site is served from /optimization, not a
domain root), otherwise the stubs redirect to the wrong place.
"""

import os
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
REPO = os.path.dirname(HERE)
MAPPING = os.path.join(HERE, "legacy_redirects.tsv")
BUILD = os.path.join(REPO, "_build", "html")
BASE_URL = os.environ.get("BASE_URL", "").rstrip("/")

TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>Page moved</title>
<link rel="canonical" href="{target}">
<meta http-equiv="refresh" content="0; url={target}">
<meta name="robots" content="noindex">
</head>
<body>
<p>This page has moved to <a href="{target}">{target}</a>.</p>
</body>
</html>
"""


def main():
    if not os.path.isdir(BUILD):
        sys.exit(f"error: {BUILD} not found. Run `myst build --html` first.")

    written = 0
    with open(MAPPING, encoding="utf8") as fp:
        for lineno, raw in enumerate(fp, 1):
            line = raw.rstrip("\n")
            if not line.strip() or line.lstrip().startswith("#"):
                continue

            parts = line.split("\t")
            if len(parts) != 2:
                sys.exit(f"error: {MAPPING}:{lineno}: expected 2 tab-separated fields")
            old, new = parts[0].strip(), parts[1].strip()
            if not old:
                sys.exit(f"error: {MAPPING}:{lineno}: empty old path")

            # A trailing slash matters: MyST serves pages as directories.
            target = f"{BASE_URL}/{new}/" if new else f"{BASE_URL}/"

            dest = os.path.join(BUILD, old)
            # Never let a stub clobber a real page.
            if os.path.exists(dest):
                print(f"  skip (exists): {old}")
                continue

            os.makedirs(os.path.dirname(dest), exist_ok=True)
            with open(dest, "w", encoding="utf8") as out:
                out.write(TEMPLATE.format(target=target))
            written += 1

    print(f"wrote {written} redirect stubs into {BUILD} (BASE_URL={BASE_URL!r})")


if __name__ == "__main__":
    main()
