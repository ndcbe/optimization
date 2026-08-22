# Maintaining this site

Notes for whoever builds and deploys the course website. Student-facing setup lives in
[`README.md`](README.md).

**Companion:** `pyomo-doe` (Prof. Dowling's ACC 2026 workshop repo) is the reference implementation this
site's theme arrangement was copied from. Its `DEVELOPER.md` is the more detailed original. ⚠ Its path
differs per machine — `~/DowlingLab/Teaching/pyomo-doe` on one, `~/DowlingLab/IDAES/pyomo-doe` on another —
so resolve it by name:

```bash
find ~ -maxdepth 5 -type d -name pyomo-doe -not -path '*/.git/*' 2>/dev/null
```

---

## Building

```bash
conda activate optimization_fall2026
python ./scripts/process_notebooks.py            # -dev sources -> published copies
BASE_URL=/optimization jupyter-book build --html # -> _build/html
```

`BASE_URL` matters: the site is served from `https://ndcbe.github.io/optimization`, not a domain root.
Without it every asset and internal link resolves one level too high and the page renders unstyled.

No `npm install -g mystmd` is needed locally — the `jupyter-book` 2.x pip package manages its own Node
toolchain. **The bare `myst` command is therefore not on your `PATH`, and that is correct.** CI installs
`mystmd` from npm and calls `myst build --html` instead. **The two paths differ by command name on purpose;
do not edit either to match the other.**

> **Do not delete `_build/`.** The MyST site theme is fetched at build time and a GitHub rate-limit response
> (HTTP 429) fails the build with *no diagnostics at all*. An incremental rebuild is also far faster.

A clean build emits **~115 warnings and 0 errors**. That is the status quo, not damage you caused. 98 of them
are one mechanical class — `Duplicate identifier in project`, meaning two notebook cells share an id — and 87
of those sit in four notebooks (`PyomoDAE_car`, `Logical_Modeling_GDP`, `RiskMeasures`,
`Stochastic-Gradient-Descent-1`).

---

## The custom theme and the "Open in Colab" button

### Why a fork is necessary

The stock MyST `book-theme` has **no Colab support of any kind**. Grepping its bundled `build/index.js` for
`colab.research` returns `0`, and its `template.yml` exposes no option to switch one on. There is nothing to
configure — the feature does not exist upstream.

[`dowlinglab/myst-theme`](https://github.com/dowlinglab/myst-theme) is a fork that adds one, on branch
**`colab-button`**. The whole mechanism is a `ColabLink` component in
`packages/frontmatter/src/FrontmatterBlock.tsx`:

```tsx
export function ColabLink({ sourceUrl }: { sourceUrl?: string }) {
  if (!sourceUrl || !/\.ipynb(?:$|[?#])/.test(sourceUrl)) return null;
  const colabUrl = sourceUrl.replace(
    /^https?:\/\/github\.com\//,
    'https://colab.research.google.com/github/',
  );
  ...
}
```

**Everything it needs was already present.** MyST derives `source_url` from `project.github` in `myst.yml`,
so a page already carried
`https://github.com/ndcbe/optimization/blob/main/notebooks/1/LP.ipynb`, and the rewrite turns that into
`https://colab.research.google.com/github/ndcbe/optimization/blob/main/notebooks/1/LP.ipynb`.

**So the theme was the only missing piece.** No per-notebook frontmatter, no `downloads:` entries, and no
change to `process_notebooks.py`. The guard on `.ipynb` is why markdown pages correctly get no button.

### Architecture — two layers, and why

| Layer | Path | Committed? |
| --- | --- | --- |
| Source of truth (`git subtree` of the fork) | `vendor/myst-theme` | ✅ yes — 441 files, 4.2 MB |
| Packaged artifact that `myst.yml` consumes | `themes/pyomo-book-theme-dist` | ✅ yes — 125 files, 23 MB |

`myst.yml` points at the **packaged artifact**, never the raw subtree:

```yaml
site:
  template: themes/pyomo-book-theme-dist
```

The split is not optional. MyST requires a template directory containing `template.yml`, `server.js`,
`package.json`, `package-lock.json`, `public/` and `build/`; the raw subtree is a development workspace and
has none of that assembled.

⚠ **`node_modules` is never committed.** `myst build` runs `npm install` inside the packaged theme on first
use, creating a **29 MB** tree there. It was not covered by any pre-existing ignore rule and would have been
committed; `.gitignore` now excludes it in both layers. It is regenerated on demand — deleting it is safe.

⚠ **The `pyomo-book-theme-dist` name is deliberate, not a copy-paste slip.** `scripts/build_theme_dist.sh`,
the `.gitignore` rules and `pyomo-doe`'s own documentation all reference it. Matching names mean a future
improvement can be **copied** between the two repos rather than translated. Renaming it here would buy
tidiness and cost interoperability.

### How this was set up (2026-08-22)

1. `git subtree add --prefix=vendor/myst-theme https://github.com/dowlinglab/myst-theme colab-button --squash`
2. Copied `scripts/build_theme_dist.sh` and the packaged `themes/pyomo-book-theme-dist` from `pyomo-doe`.
3. Changed `myst.yml`'s `site.template` from `book-theme` to `themes/pyomo-book-theme-dist`.
4. Added the `node_modules` ignore rules.
5. Rebuilt and **verified the button actually rendered** — see below.

Recorded provenance: `vendor/myst-theme` is `dowlinglab/myst-theme` branch `colab-button` at commit
`c4ced699329ae9f103452ec40cce97aaac85a897`. `git log` carries it as `git-subtree-split`, so
`git subtree pull` works without arguments beyond the branch.

---

## Updating the theme after improving the upstream fork

This is the path to use when you have made theme changes in
[`dowlinglab/myst-theme`](https://github.com/dowlinglab/myst-theme) and want them on the course site.

**1. Make and push the change in the fork**, on the branch this repo tracks (`colab-button`), and test it
there first. Do **not** edit `vendor/myst-theme` in this repo directly — the next subtree pull will conflict
with or clobber local edits, and the fork is where the change belongs.

**2. Pull the updated source into the subtree:**

```bash
cd ~/DowlingLab/Teaching/optimization
git subtree pull --prefix=vendor/myst-theme \
    https://github.com/dowlinglab/myst-theme colab-button --squash
```

**3. Regenerate the packaged artifact.** The subtree is source; `myst.yml` reads the artifact, so a subtree
pull alone changes nothing the site can see:

```bash
bash scripts/build_theme_dist.sh
```

This installs the vendored workspace dependencies, builds the production book theme, assembles
`themes/pyomo-book-theme-dist`, and regenerates its `package-lock.json`. It takes several minutes and prints
a wall of npm deprecation warnings — those are normal.

**4. Rebuild and verify** (next section). **Do not skip this.**

**5. Commit both layers together:**

```bash
git add vendor/myst-theme themes/pyomo-book-theme-dist
git commit -m "Update the vendored MyST theme to <upstream sha>"
```

⚠ **Committing one without the other is the failure mode to avoid.** A new subtree with a stale artifact
deploys the *old* theme while `git log` claims the new one — and nothing errors.

### If you would rather not rebuild

`pyomo-doe` holds an already-built artifact for the same fork. Copying it over is legitimate and skips the
npm build entirely:

```bash
PD=$(find ~ -maxdepth 5 -type d -name pyomo-doe -not -path '*/.git/*' 2>/dev/null | head -1)
rm -rf themes/pyomo-book-theme-dist
(cd "$PD" && git archive HEAD themes) | tar xf -
```

Use this only when the two repos want the *same* theme version. It is how this site's artifact was first
obtained.

---

## Verifying the theme actually took effect

🔴 **`exit 0` does not mean the custom theme was used.** A build that silently falls back to the stock theme
also succeeds, also emits 115 warnings, and also produces a complete site. Check the output, not the exit
code.

```bash
# 1. The fork-specific class names. Absent => the stock theme rendered.
grep -o 'myst-fm-colab-link\|myst-fm-colab-icon' \
     _build/html/notebooks/1/lp/index.html | sort -u

# 2. A correctly rewritten Colab URL.
grep -o 'colab.research.google.com/github/[^"]*' \
     _build/html/notebooks/1/lp/index.html | head -1

# 3. Every notebook page has a button, and no page is silently missed.
python3 - <<'PY'
import json, glob, os
missing = []
for f in glob.glob('_build/html/*.json'):
    fm = json.load(open(f)).get('frontmatter', {})
    if (fm.get('source_url') or '').endswith('.ipynb'):
        slug = os.path.basename(f)[:-5].replace('.', '/')
        html = f'_build/html/{slug}/index.html'
        if not (os.path.exists(html) and
                'myst-fm-colab-link' in open(html, errors='ignore').read()):
            missing.append(slug)
print(f"notebook pages missing the Colab button: {len(missing)}")
for s in missing: print("   ", s)
PY
```

Expected on a good build: both class names present, a URL of the form
`colab.research.google.com/github/ndcbe/optimization/blob/main/...`, and **0 pages missing**. Check 3 is the
one that matters — checks 1 and 2 pass on a single lucky page.

Baseline recorded 2026-08-22: **71 pages** carry a Colab link, **0 notebook pages missing**, markdown pages
correctly carry none.

---

## Continuous integration

[`.github/workflows/build-and-publish.yml`](.github/workflows/build-and-publish.yml) runs on every push to
`main`: Node 22, `npm install -g mystmd`, `myst build --html`, then `scripts/make_redirects.py`, then
`ghp-import` to `gh-pages`.

**No CI change was needed for the theme.** The packaged artifact is committed and `myst build` installs its
`node_modules` itself; the theme declares `node >= 16` and ships a committed `package-lock.json`, so CI's
Node 22 is fine.

⚠ **CI does not run `scripts/process_notebooks.py`** — it cannot, because that script reads assignment
notebooks from `../optimization-private`, a private repo CI cannot see. **Run it locally and commit the
result before pushing**, or the published notebooks go stale silently.

⚠ **CI does not rebuild the theme either.** `pyomo-doe`'s CI does, which is why its workflow has an extra
step. Here the committed artifact is the deployed artifact — which is exactly why step 5 above insists both
layers are committed together.
