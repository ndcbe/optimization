# Figures — one source, two outputs

Everything in this directory exists so a figure is **authored once** and appears identically on the
website and in the printed course pack. There is **one** figure pipeline, not two.

| File | Role |
| --- | --- |
| `preamble.tex` | shared TikZ setup — loaded by `Makefile` *and* `\input` by the handouts |
| `tikz/<name>.tex` | a bare `tikzpicture`; the single source for one diagram |
| `plots/<name>.py` | a `make_figure() -> Figure`; the single source for one plot |
| `plots/_house.py` | conventions a style file cannot encode — hatch cycle, direct labelling |
| `render.py` | runs one `plots/<name>.py` and writes its PNG **and** PDF |
| `Makefile` | renders both source languages → `../media/figures/` at 300 dpi |
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

## Course additions: greyscale is a strict requirement

**The governing decision (Prof. Dowling, 2026-08-17):**

> **Colour first — design the figure to be as good as it can be in colour.
> Then guarantee it still works in black and white.**

This is a **priority ordering, not an equal both-and requirement.** The colour version is the main
viewing mode: the website is on screen, and Prof. Dowling prints both the instructor and student
copies in colour. The greyscale case is the **student who prints the student handout on a mono
laser printer** — real and common, but secondary. So greyscale is a **pass/fail floor**, not an
optimisation target. Do **not** flatten the palette to maximise luminance separation.

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
| Every series carries a **non-colour** identity — linestyle, marker, or direct label | **required**, and automatic for linestyle via `axes.prop_cycle` |
| Greyscale **verified by measurement**, not by eye | **required** — `scripts/check_greyscale.py` |
| **Direct labelling** preferred over a legend where it fits | strong preference |
| At most **four** series per axes | **required** — see below |
| Sequential colour maps must be **monotone in luminance** (`viridis`, not `jet`/`coolwarm`) | **required** |

**Why four.** The cycle in `dowling.mplstyle` is ordered so its first four entries have the widest
luminance spread the palette allows: ΔL\* ≥ 11.8, verified by brute force over all subsets. Five
entries cannot exceed ΔL\* = 6.9 under *any* ordering of Okabe-Ito. Past four series, colour has
run out of greyscale headroom and you must switch to markers, direct labelling, or small multiples.
This is the concrete consequence of putting colour first: linestyle is load-bearing, not decoration.

Instructor-only figures may use colour freely.

---

## Verifying

```bash
# the house style itself (the authoritative check)
python scripts/check_greyscale.py --style figures/dowling.mplstyle -n 4

# an ad-hoc palette
python scripts/check_greyscale.py --colors '#0072B2' '#E69F00' tab:red

# rendered images, or a directory of them (triage only — see the script's docstring
# for why image mode over-reports on photographs and UI screenshots)
python scripts/check_greyscale.py media/figures
```

Exit status is 0 on pass, 1 on fail, so it gates in CI. `--strict` promotes warnings to failures.

---

## Adding a figure

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

⚠ **Do not make a plot script depend on a solver.** Two of the three migrated plots re-derive their
data with `numpy`/`scipy` rather than Pyomo + Ipopt, so `make` needs no solver binary and finishes
in seconds. If a figure genuinely needs a long solve, commit the solved trajectory as data and read
it.

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
