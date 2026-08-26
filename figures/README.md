# Figures — one source, two outputs

Everything in this directory exists so a figure is **authored once** and appears identically on the
website and in the printed course pack. There is **one** figure pipeline, not two.

🔴 **A figure has exactly one source, and if a notebook makes it, the notebook IS that source.**
Prof. Dowling, 2026-08-24: *"If the figure is generated in a notebook, such as showing algorithm
results in Part II, we should use the version from the notebook in the lecture notes."* See
**[Solve → extract → plot](#solve--extract--plot-the-notebook-is-the-source)** below; it changes how
about 25 of the 44 figures here are built, and it retires the rule that a plot script may re-derive
a notebook's answer with `scipy`.

| File | Role |
| --- | --- |
| `preamble.tex` | shared TikZ setup — loaded by `Makefile` *and* `\input` by the handouts |
| `tikz/<name>.tex` | a bare `tikzpicture`; the single source for one diagram |
| `plots/<name>.py` | a `make_figure() -> Figure`; the single source for one plot **that no notebook makes** |
| `plots/_house.py` | conventions a style file cannot encode — hatch cycle, direct labelling |
| `render.py` | runs one `plots/<name>.py` and writes its PNG **and** PDF |
| **a notebook cell tagged `figure:<name>`** | the single source for one plot **that a notebook makes** |
| **`results/<name>.json`** | that notebook's extracted results, committed, so a **style** change re-renders with no solver |
| **`render_from_notebook.py`** | re-runs one tagged cell against `results/<name>.json` → PNG **and** PDF |
| **`../scripts/check_results_fresh.py`** | has the model changed since the archive was written? |
| `../notebooks/helper.py` | Colab setup, the house style, **and** the extract / archive / save-the-figure plumbing |
| `Makefile` | renders all three source languages → `../media/figures/` at 300 dpi |
| `dowling.mplstyle` | shared matplotlib style — the exact analogue of `preamble.tex`, for plots |
| `dowling-markers.mplstyle` | optional overlay adding a cycled marker (sparse data only) |
| `../scripts/check_greyscale.py` | the enforcement tool: does this figure survive black-and-white printing? |

`dowling.mplstyle` lives **here, in the public repo**, for the same three reasons `preamble.tex`
does:

1. the notebooks that consume it are in this repo, and students can see and reuse it;
2. the private repo's `lecture-notes/` already reaches across with `../../optimization/figures/`,
   so one copy serves both — a copy in each repo is exactly the drift W6 is trying to prevent;
3. student-contributed notebooks inherit the house style without being told about a repo they
   cannot clone.

The two repos must stay **sibling directories on disk**.

---

## Using the style

```python
import matplotlib.pyplot as plt
plt.style.use("../../figures/dowling.mplstyle")     # from notebooks/<n>-dev/
```

On Colab, where only the notebook is present, fall back to the raw URL:

```python
plt.style.use("https://raw.githubusercontent.com/ndcbe/optimization/main/figures/dowling.mplstyle")
```

For sparse data where a marker per point is wanted:

```python
plt.style.use(["../../figures/dowling.mplstyle", "../../figures/dowling-markers.mplstyle"])
```

---

## Where the numbers come from

`dowling.mplstyle` encodes Prof. Dowling's own guide, **"Preparing Publication Quality Figures in
Python"** — CBE 60258 / *data-and-computing*, notebook `01/Publication-Quality-Figures`
(<https://ndcbe.github.io/data-and-computing/notebooks/01/Publication-Quality-Figures.html>;
source at `~/DowlingLab/Teaching/data-and-computing/notebooks/01-dev/`). That guide derives its
recommendations from P. Kamat, G. V. Hartland & G. C. Schatz (2014), *Graphical Excellence*,
*J. Phys. Chem. Lett.* **5**(12), 2118–2120.

Recorded here so it never needs re-deriving:

| Area | Guide's rule | rcParam |
| --- | --- | --- |
| Figure size | 4×4 in (4×6.4 for wide) | `figure.figsize: 4, 4` |
| DPI | 300 | `savefig.dpi: 300` |
| Line width | 3 | `lines.linewidth: 3` |
| Marker size | 8 | `lines.markersize: 8` |
| Tick label font | 15 | `xtick.labelsize` / `ytick.labelsize: 15` |
| Axis label font | 16, **bold** | `axes.labelsize: 16`, `axes.labelweight: bold` |
| Major tick direction | in | `xtick.direction` / `ytick.direction: in` |
| Minor tick direction | in | same rcParam (minor ticks off by default) |
| Ticks on all sides | `tick_params(top=True, right=True)` | `xtick.top: True`, `ytick.right: True` |
| Saving | `savefig(f+'.png', dpi=300, bbox_inches='tight')` | `savefig.bbox: tight` |
| Colour | colour-blind-friendly palettes | Okabe-Ito `axes.prop_cycle` |

Things the guide demonstrates but a style file cannot encode — do these by hand:

- **Direct labelling.** The guide's flagship example annotates "Retentate" and "Permeate" onto the
  curves with `ax.annotate(...)` rather than relying on the legend. Prefer this.
- **Axis limits anchored at the data**: `plt.xlim(left=0)`, `plt.ylim(bottom=0)`.
- **`label_outer()`** on subplot grids to drop repeated tick labels.
- **Square aspect** where the axes are commensurate (`plt.axis('square')`).
- **A plotting *function* with toggle arguments** (`plot_pred=True, lg=False`) so a figure can be
  regenerated with or without decoration. This is also what makes a figure reusable by the handout.
- **Save PNG *and* PDF** when the figure goes into print: `savefig(f+'.pdf')`.

---

## Course additions: use colour, and make it survive greyscale

⚠ **The rule was RELAXED on 2026-08-21 and `check_greyscale.py` was rewritten to match. If you are
reading an older figure's docstring that says "all three curves are BLACK because
`check_greyscale.py` fails a coloured one", that constraint is gone.**

**Prof. Dowling, 2026-08-19:**

> **"Our greyscale test is way too strict."**
> **"I do not want the figures to be greyscale. I want the figures to be okay if they are printed
> in greyscale."**

and, on individual figures, *"let's use some color"* and *"Make this colorful!?"*

**The governing decision (Prof. Dowling, 2026-08-17), which still stands:**

> **Colour first — design the figure to be as good as it can be in colour.
> Then guarantee it still works in black and white.**

This is a **priority ordering, not an equal both-and requirement.** The colour version is the main
viewing mode: the website is on screen, and Prof. Dowling prints both the instructor and student
copies in colour. The greyscale case is the **student who prints the student handout on a mono
laser printer** — real and common, but secondary. So greyscale is a **pass/fail floor**, not an
optimisation target. Do **not** flatten the palette to maximise luminance separation, and do
**not** drop colour to make the checker quieter — a monochrome figure with two or more series is
now *reported* by `check_greyscale.py --recolour` as a candidate for having its colour put back.

**The rule, in one sentence: a distinction may be carried by colour, but never by colour ALONE.**

A figure fails only when *both* of these hold:

1. two series are identified by chromatic colours that collapse to the same grey (ΔL\* < 10), **and**
2. **neither** of those series carries a non-colour identity — no linestyle, dash pattern, marker,
   or hatch.

Either one alone is fine. Sky blue and orange print as the same grey; one dashed and one dotted,
they pass, because the colour reader uses the hue and the photocopy reader uses the dashes.

The source guide addresses **colour-blindness** and says nothing about greyscale. They are
different properties: a palette can be perfectly distinguishable to a colour-blind reader and
collapse to identical greys on a photocopier. Okabe-Ito does exactly that. Measured CIE L\*:

| Colour | Hex | L\* |
| --- | --- | --- |
| black | `#000000` | 0.0 |
| blue | `#0072B2` | 46.0 |
| vermillion | `#D55E00` | 54.2 |
| bluish green | `#009E73` | 57.7 |
| reddish purple | `#CC79A7` | 61.1 |
| sky blue | `#56B4E9` | 69.8 |
| orange | `#E69F00` | 70.6 |
| yellow | `#F0E442` | 89.1 |

**Sky blue and orange differ by ΔL\* = 0.8.** In print they are the same grey. So:

| Rule | Status |
| --- | --- |
| Every series carries a **non-colour** identity — linestyle, marker, hatch, or direct label | **required**, and automatic via `axes.prop_cycle`, which pairs colour with linestyle |
| Greyscale **verified by measurement**, not by eye | **required** — `scripts/check_greyscale.py --source` |
| **Direct labelling** preferred over a legend where it fits | strong preference |
| Sequential colour maps must be **monotone in luminance** (`viridis`, not `jet`/`coolwarm`) | **required** |
| ~~At most **four** series per axes~~ | **withdrawn 2026-08-21** — see below |
| **Monochrome** where colour would help | **discouraged** — reported as a recolour candidate |

**Why the four-series cap is gone.** It was never about the number four; it was a consequence of
requiring luminance separation *from colour alone*. The cycle in `dowling.mplstyle` is ordered so
its first four entries have the widest luminance spread Okabe-Ito allows (ΔL\* ≥ 11.8, verified by
brute force over all subsets); five entries cannot exceed ΔL\* = 6.9 under *any* ordering. Under the
new rule the fifth series does not need luminance headroom, because it gets the fifth **linestyle**
from the same cycle. **Four is still a good default for readability** — past four curves a plot is
usually crowded whatever the palette — but it is a design preference now, not a gate.

⚠ The **one place the cap still binds** is a sequential colormap, where there is no linestyle to
fall back on: `viridis` bands must be far enough apart in L\* to be told apart in print, which is
what forced the contour lines in `mccormick-envelopes.py`.

Instructor-only figures may use colour freely.

---

## Verifying

```bash
# figure SOURCES -- the authoritative check, because whether an encoding is
# redundant is a fact about the source, not about the pixels
python scripts/check_greyscale.py --source figures/plots

# just the list of monochrome figures that could have their colour back
python scripts/check_greyscale.py --source figures/plots --recolour

# the house style: does its prop_cycle pair colour with a non-colour key?
python scripts/check_greyscale.py --style figures/dowling.mplstyle -n 4

# an ad-hoc palette. --redundant asserts the figure also varies
# linestyle/marker/hatch, which downgrades a grey collapse to a warning
python scripts/check_greyscale.py --colors '#0072B2' '#E69F00' --redundant

# rendered images, or a directory of them (triage only — image mode cannot see a
# linestyle, so a collapse there is a WARNING and never a failure)
python scripts/check_greyscale.py media/figures

# prove the checker can fail, not just pass
python scripts/check_greyscale.py --selftest
```

Exit status is 0 on pass, 1 on fail, so it gates in CI. `--strict` promotes warnings to failures.

---

## Adding a figure

🔴 **First: does a notebook generate this figure?** If so it is not a script at all — see
[Solve → extract → plot](#solve--extract--plot-the-notebook-is-the-source).

**Diagram** → `tikz/<name>.tex`, then `make`. The handout `\input`s the same file.

**Plot** → a committed script under `plots/<name>.py`, then `make`. Write **one** function:

```python
def make_figure():
    fig, ax = plt.subplots()
    ...
    return fig          # do NOT savefig, do NOT plt.style.use
```

`render.py` applies `dowling.mplstyle` and writes `../media/figures/<name>.png` (300 dpi, what the
notebooks display) and `<name>.pdf` (vector, what the handouts `\includegraphics`). Style, DPI and
bounding box are therefore set in exactly one place, and a script cannot quietly opt out of the
house style. Files named `plots/_*.py` are shared helpers, not figures; `make` skips them.

The notebook and the handout both *display* the rendered output rather than each generating their
own copy — that is what makes drift impossible. Where a notebook needs a live, executed plot for
teaching, that is a *different* figure and should look different. In practice the pattern that
works is: show the rendered figure in a markdown cell as the canonical picture, then keep the live
cells below it for exploration.

⚠ **One output directory, two source languages.** `tikz/foo.tex` and `plots/foo.py` would both write
`../media/figures/foo.png`. `make` refuses to run if any name appears in both.

⚠ **`make` still needs no solver — but a figure must no longer be re-derived to achieve that.**
This paragraph used to read *"Do not make a plot script depend on a solver... re-derive their data
with `numpy`/`scipy` rather than Pyomo + Ipopt."* **That rule was reversed on 2026-08-24**, and the
reversal is the subject of the next section. Its *intent* survives intact: nothing in this
directory ever calls a solver. What changed is how. A figure a notebook makes is now re-rendered
from that notebook's **archived results**, not recomputed by a second implementation. See
[Solve → extract → plot](#solve--extract--plot-the-notebook-is-the-source).

---

## Solve → extract → plot: the notebook is the source

**Added 2026-08-24. This is the contract. If you are retrofitting a figure, everything you need is
in this section.**

### The rule, and where it came from

Prof. Dowling:

> *"If it is for a Pyomo example, I want to plot the results from Pyomo. … I do not want to
> recreate figures with scipy for the Pyomo sections. That seems very confusing."*
>
> *"What I do like is to separate the Pyomo solve from the analysis. For example, we could extract
> the results from Pyomo and then make functions that plot those results."*
>
> *"For research code, I encourage my students to pickle or otherwise extract and store the
> optimization results. That way, they can use archived results to adjust their plotting scripts.
> Thus, adjusting the plotting script does not require resolving the model. We can teach the same
> separation in the notebooks by separating the solve and analyze as different steps in different
> cells."*
>
> *"If the figure is generated in a notebook, such as showing algorithm results in Part II, we
> should use the version from the notebook in the lecture notes."*
>
> *"But Python generated plots that visualize Pyomo related data — those should live in the
> notebooks."*

**One question decides which pipeline a figure uses: does a notebook generate it?**

| | Source | Built by |
| --- | --- | --- |
| A notebook generates it (**~25 of 44**) | the notebook cell tagged `figure:<name>` | running the notebook; `make` re-renders from `results/<name>.json` |
| No notebook generates it (**~19 of 44**) | `plots/<name>.py` | `render.py`, exactly as before — **unchanged, do not touch these** |

There is no Part I / Part II split in this rule. *"Do not rely on Pyomo for most of the examples
and plots in Part II"* is about **Pyomo**, not about notebooks: a Part II notebook makes its figures
with numpy and scipy while implementing an algorithm, and those figures are the ones the lecture
should use.

⚠ **`figures/tikz/` is untouched by all of this.** Diagrams authored in TikZ keep their pipeline
exactly as it is (Prof. Dowling, 2026-08-24: *"I am okay with not changing how we handle tikz
figure infrastructure right now."*).

### Why the plotting code lives in the notebook cell and not in a shared module

Because **a notebook is a teaching artifact.** If the student sees only `plot_frontier(m)` imported
from somewhere, the plotting has been hidden from the person who is supposed to be learning it.

So there is deliberately **no library of `plot_*()` functions** in `notebooks/helper.py`, and
adding one would be a regression. That module holds only the parts that are the same for every
figure and teach nothing: extraction, archiving, and saving at the right dpi to the right path.

⚠ **Merging the plumbing into `helper.py` (2026-08-25) did not change this.** Prof. Dowling asked
for one helper file — *"Let's have helper contain all of the useful scripts/colab add-ons"* — and in
the same breath restated the other half: *"Python generated plots that visualize Pyomo related data —
those should live in the notebooks."* **Plumbing merges; plots do not.**

There is also nothing left to share. The figure has **one** implementation — the notebook cell —
and `render_from_notebook.py` runs that same cell rather than reimplementing it.

### Why the archive still exists now that the notebook writes the PDF

**Because the common regeneration is a STYLE change, not a model change.** The house style was
reworked across every figure in this repo on 2026-08-24. Doing that again with notebook-only
generation means running ~20 notebooks with Ipopt and HiGHS; from the archive it is

```bash
python3 figures/render_from_notebook.py --all      # seconds, no solver, works in CI
```

That is the archive's only job. It is also what keeps `make` solver-free, which is a promise this
directory has always made.

### The three stages, in cells

```
cell N     build + solve the Pyomo model            <- the only cell that needs a solver
cell N+1   results = {...}  ->  helper.save_results()  <- extract to plain Python, archive as JSON
cell N+2   def plot_<name>(results): ...            <- tagged figure:<name>; the figure's ONLY source
           fig = plot_<name>(results)
           helper.save_figure(fig, "<name>")     <- returns None, so it prints no path
```

Worked end to end in **`notebooks/1-dev/Portfolio-Optimization.ipynb`**, section "Step 5. Solve,
extract, plot — three separate steps". Read that before retrofitting your first figure.

### The cell contract — `figure:<name>`

A cell that generates a handout figure carries the notebook tag **`figure:<name>`**, where `<name>`
is the figure name shared by `media/figures/<name>.{png,pdf}`, `figures/results/<name>.json`, and
the handout's `\includegraphics`.

**ON ENTRY** the cell may assume exactly these names are bound, and no others:

| name | is |
| --- | --- |
| `results` | the `"data"` block of `figures/results/<name>.json` |
| `np`, `pd`, `plt` | numpy, pandas, matplotlib.pyplot |
| `helper` | `notebooks/helper.py` — **the going-forward name** |

**ON EXIT** the cell must leave **`fig`** bound to the matplotlib `Figure`.

**The cell MUST NOT** solve, import Pyomo, read a data file, use an unseeded random number, or use
any name from an earlier cell other than the five above. Everything the plot needs must be inside
`results`. That restriction is what makes the cell runnable in both places — and it is the
"separate the solve from the analysis" discipline enforced rather than requested.

⚠ **The cell MUST set its own `figsize`.** `helper.set_plotting_style()` overrides
`figure.figsize` for on-screen readability and `render_from_notebook.py` does not, so a figure
relying on the default renders at two different aspect ratios depending on who generated it.

⚠ **The cell MUST NOT `import _house`.** `plots/_house.py` is not on disk on Colab. If a notebook
figure needs the hatch sequence, copy the literal into the cell with a comment pointing at
`plots/_house.py`. (`HATCH_CYCLE = ("///", "\\\\\\", "...", "xxx", "|||", "---")`, `SHADE_ALPHA = 0.18`.)

The cell **SHOULD** end with `helper.save_figure(fig, "<name>")`. That is what makes the notebook the
generator. It is a no-op on Colab, and `render_from_notebook.py` disables it (the driver owns where
its output goes and must never rewrite the archive it just read).

🔴 **`save_figure` and `save_results` return `None`, and this contract is why.** Because the call is
the *last statement of the cell*, anything it returned became the cell's `execute_result` — and the
published page displayed an absolute path out of the maintainer's home directory:

```
'/Users/adowling/DowlingLab/Teaching/optimization/figures/results/portfolio-efficient-frontier.json'
```

13 cells across 5 notebooks, all introduced by the conversions of 2026-08-24. **The contract induced
the bug**, so it was fixed in the contract's own terms rather than by asking every future author to
remember a `;` or a `_ =`. Both writers still *print* what they wrote, which is the part a maintainer
reads. **Do not "restore" the return value.**

### The API — `notebooks/helper.py`

⚠ **Moved here from `notebooks/pyomo_results.py` on 2026-08-25**, on Prof. Dowling's instruction that
`helper` hold all the Colab add-ons. The remaining callers migrated on 2026-08-26 and the temporary
compatibility shim was deleted. `helper` is now the only course module students download.

The reason the merge is worth doing is the install cell: it is the first thing a student runs and the
first thing that can fail, and **every extra module costs a `wget` line that can 404**. One file is
one failure mode. The install cell is now:

```python
import sys

if "google.colab" in sys.modules:
    !wget "https://raw.githubusercontent.com/ndcbe/optimization/main/notebooks/helper.py"
    import helper

    helper.easy_install()
else:
    sys.path.insert(0, "../")
    import helper
helper.set_plotting_style()
```

⚠ **The Colab `wget` resolves against `main`.** Everything merged into `helper.py` **404s on Colab
until it is pushed** — which was already true of `pyomo_results.py` and is still an open item. Colab
does not work for these notebooks today; that is a push away, not a code change.

| call | does |
| --- | --- |
| `helper.extract(m, x=m.x, obj=m.OBJ)` | solved components → `{'x': {'DJI': 0.31, …}, 'obj': 1.8e-05}` |
| `helper.value_of(component)` | one component → float, or `{index: float}` |
| `helper.table(df)` | DataFrame → `{"columns": […], "rows": [[…]]}` |
| `helper.as_dataframe(tbl)` / `helper.column(tbl, "rho")` | the inverses |
| `helper.save_results(name, data, notebook=…, source_tag=…, description=…, solver=…)` | writes `figures/results/<name>.json` |
| `helper.load_results(name)` | reads it; falls back to the raw URL on Colab |
| `helper.save_figure(fig, name)` | writes `media/figures/<name>.{png,pdf}` at 300 dpi |

`extract` is deliberately small. **If extracting your model needs more than it offers, write that
extraction in the notebook** — do not grow an abstraction here.

**Both writers are no-ops when the repo is not on disk**, and print a one-line note saying so. A
Colab session has nowhere to commit to; the student still sees the figure inline. Verified by
simulation, not assumed.

### The on-disk format — JSON, not pickle

Prof. Dowling's decision, and the reason matters: in research code `pickle` is the right reach, and
the notebook narrative says so. A **committed** artifact is different. A pickle in git is an
unreviewable binary that stops loading on a library upgrade and whose diff nobody can read.

```jsonc
{
 "meta": {
  "schema": 1,
  "figure": "portfolio-efficient-frontier",
  "notebook": "notebooks/1-dev/Portfolio-Optimization.ipynb",   // ALWAYS the -dev copy
  "description": "…",
  "generated": "2026-08-24",
  "generator": "helper 2026.08.25",
  "source_tag": "handout:portfolio-model",   // the model cell; null if there is no model
  "source_digest": "39ac1cbc9c1c8c0f",       // what makes staleness detectable
  "solver": "Ipopt (tol 1e-12) via Pyomo"
 },
 "data": { … }
}
```

A **table** is stored split, `{"columns": [...], "rows": [[...]]}`, not as a list of records:
records repeat every column name on every row (the portfolio sweep is 60 × 7, so 420 repetitions of
seven strings) and the git diff of a re-solve stops being readable. Floats are written at full
precision — `json` round-trips them exactly, and rounding to make the file pretty would make the
figure differ from the notebook.

### Naming, and where things live

| thing | path |
| --- | --- |
| the tagged cell | `notebooks/<n>-dev/<Notebook>.ipynb`, tag `figure:<name>` |
| the archive | `figures/results/<name>.json` — **committed** |
| the outputs | `media/figures/<name>.png` and `.pdf` — **committed** |
| the handout | `\includegraphics{\figout <name>.pdf}` — unchanged |

`<name>` is one string, used everywhere, and it stays the same as the retired `plots/<name>.py` so
no lecture `\includegraphics` has to change. `make` refuses to run if two sources claim one name,
which is what catches a script that should have been deleted.

🔴 **`notebooks/<n>/` is GENERATED output that `process_notebooks.py` overwrites. Always retrofit
`notebooks/<n>-dev/`.** Two scripts cite the generated copy — `l1-merit-kink-threshold.py` cites
`notebooks/6/Globalization.ipynb` and `pendulum-drift.py` cites `notebooks/3/DAE_background.ipynb`.
Both are citation bugs; fix them while you are there.

### Retrofitting one figure — the checklist

1. **Find the notebook** that already solves this problem, in `notebooks/<n>-dev/`. Confirm it
   really generates the figure's content; a script *citing* a notebook is not proof.
2. **Nothing to add to the install cell** — `helper` is already imported there.
3. **Split the cells**: solve, then extract + `save_results`, then a tagged plot cell.
4. **Move the script's plotting body into the tagged cell**, converting it to read from `results`.
   Keep the script's docstring insight — the *why* — as comments or as the function's docstring;
   several of those docstrings record a real subtlety that must not be lost.
5. **Run the notebook.** It writes `media/figures/<name>.*` and `figures/results/<name>.json`.
6. 🔴 **Compare the regenerated figure with the committed one as an IMAGE**, before and after.
   Rasterise both PDFs (`pdftocairo -png -r 150 -singlefile`) and diff the arrays. `portfolio-`
   `efficient-frontier` came out byte-identical at 150 dpi. **An unintended change means the
   retrofit is wrong**; an intended one must be stated.
7. **Delete `plots/<name>.py`** and record it in the private repo's `claude/deleted_notebooks.md`
   (path, reason, commit).
8. **Verify**:
   ```bash
   python3 scripts/check_results_fresh.py                    # archive vs model cell
   python3 figures/render_from_notebook.py <name>            # solver-free path works
   python3 scripts/check_greyscale.py --source notebooks/<n>-dev/<Notebook>.ipynb
   cd ../optimization-private/lecture-notes && python3 check_code_sync.py
   ```
9. **Commit** the notebook, the archive, the two `media/figures/` files and the script deletion.

### The freshness checker

`figures/results/<name>.json` is a committed generated artifact, and one that nothing polices goes
stale silently — someone tightens a bound in the notebook, nobody re-runs it, and the pack ships
last term's answer with every build green. `scripts/check_results_fresh.py` pins each archive to
the `handout:<tag>` model cell it names, using the same normalisation and digest as
`lecture-notes/check_code_sync.py` (imported, not restated). Verdicts: `OK`, `STALE`, `ORPHAN`,
`MISSING`, `MALFORMED`, and `UNVERIFIED` (a data figure with no model cell to pin — a warning, never
a failure).

⚠ **It sees the MODEL cell, not the solve.** Change the sweep range, the solver options or the
input data and the digest is unchanged. That is accepted and argued in the script's docstring: a
change to the sweep is one you are making *while looking at the figure*, and a change to the model
is one made for an unrelated reason with no thought of the figure at all. The second is the case
that needs a machine to notice.

Run `--selftest` on both `check_results_fresh.py` and `render_from_notebook.py` before believing
either a red or a green result. A checker that cannot fail is indistinguishable from one that passes.

---

## Style details

### Shaded regions need hatching

`hatch.color` and `hatch.linewidth` are in `dowling.mplstyle`; the hatch *sequence* is
`HATCH_CYCLE` in `plots/_house.py`, because matplotlib's `prop_cycle` has no hatch entry. An `alpha`
fill on its own greys to mush, and two overlapping tints produce a third tint that means nothing in
black and white:

```python
from _house import HATCH_CYCLE, SHADE_ALPHA
ax.axvspan(a, b, facecolor="0.55", alpha=SHADE_ALPHA, hatch=HATCH_CYCLE[0],
           edgecolor=plt.rcParams["hatch.color"], linewidth=0.0)
```

### Arrows are not series

An arrow gets no linestyle from the colour cycle, so colour is *all* it has. Label each arrow in
place with the symbol it carries (`$\nabla f$`, `$\nabla g$`) — see `plots/kkt-geometry.py`.

**Math or text** → never a screenshot. Native LaTeX in the handout, MathJax in the notebook.
