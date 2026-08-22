#!/usr/bin/env python3
"""Check that a COLOUR figure still reads when it is printed in black and white.

⚠ THIS SCRIPT WAS INVERTED ON 2026-08-21. READ THIS BEFORE CHANGING IT.
------------------------------------------------------------------------
Prof. Dowling, 2026-08-19, on the previous version:

    "Our greyscale test is way too strict."
    "I do not want the figures to be greyscale. I want the figures to be okay
     if they are printed in greyscale."
    "let's use some color"   ...   "Make this colorful!?"

The old rule failed any figure containing two colours within dL* = 10, whether
or not anything else told the two series apart. The rational response to that
rule was to stop using colour, and several figures did exactly that -- the
right-hand panel of `mccormick-envelopes.py` says so in its own docstring: "All
three curves are BLACK... a coloured curve here would collide in greyscale."
The gate was steering the work away from what he wanted.

THE NEW RULE, in one sentence: a distinction may be carried by colour, but it
must not be carried by colour ALONE.

Concretely, a figure FAILS only when both of these hold:

  1. two series are identified by chromatic colours that collapse to the same
     grey (dL* below the fail threshold), AND
  2. neither of those two series carries a non-colour identity -- no linestyle,
     no dash pattern, no marker, no hatch.

Either one on its own is fine, and that is the whole point:

  * Sky blue and orange differ by dL* = 0.8 and print as the same grey. Two
    curves in those colours, one dashed and one dotted, PASS. The reader with
    the colour PDF uses the hue; the reader with the photocopy uses the dashes.
  * A figure using four well-separated luminances and no linestyles passes on
    separation, with a warning that it is one editing decision away from not.

And monochrome is no longer a way to score well. A figure with two or more
series and no chromatic colour at all is reported as RECOLOUR -- an
informational verdict, never a failure -- because it is very likely a figure
that was flattened to satisfy the old rule and can now have its colour back.
`--recolour` lists exactly those.

MODES
-----
  --source PATH ...   figure scripts (figures/plots/*.py). THE AUTHORITATIVE
                      MODE, because whether an encoding is redundant is a fact
                      about the source, not about the pixels.
  --style FILE        a matplotlib style file: does its prop_cycle pair colour
                      with a non-colour key, and how far apart are the colours?
  --colors C1 C2 ...  an ad-hoc palette. Add --redundant to assert that the
                      figure using it also varies linestyle/marker/hatch.
  PATH ...            rendered images. Triage only -- see the limitation below.

MEASUREMENT
-----------
Colours go to CIE L* (perceptual lightness, 0 = black, 100 = white) through
linearised sRGB relative luminance Y = 0.2126R + 0.7152G + 0.0722B. Greyscale
printing preserves Y, so two colours with equal L* print as the same grey no
matter how far apart they look on a screen.

    dL* <  FAIL_THRESHOLD (10)   the pair collapses in print
    dL* <  WARN_THRESHOLD (20)   close; fine when something else distinguishes
    dL* >= WARN_THRESHOLD        separated by luminance alone

HONEST LIMITATIONS
------------------
* Image mode cannot know which pixels are which series, cannot see a linestyle,
  and cannot read a legend. A grey collapse in an image is therefore reported as
  a WARNING and never a failure: the source is what settles it. (This is a
  change -- image mode used to fail.) Use it on figures whose source is lost:
  screenshots, contributed notebooks, legacy PNGs.
* Source mode reads the AST and understands literal keyword arguments. A colour
  or linestyle chosen inside a loop, pulled from a dict, or computed is reported
  as UNKNOWN rather than guessed at. UNKNOWN never fails; it is listed so a
  human can look.
* Nothing here checks colour-blind safety. That is a different property, it is
  handled by using Okabe-Ito in `figures/dowling.mplstyle`, and a palette can
  pass one test and fail the other.

USAGE
-----
    python3 scripts/check_greyscale.py --source figures/plots
    python3 scripts/check_greyscale.py --source figures/plots --recolour
    python3 scripts/check_greyscale.py --style figures/dowling.mplstyle
    python3 scripts/check_greyscale.py --colors '#0072B2' '#E69F00' --redundant
    python3 scripts/check_greyscale.py media/figures
    python3 scripts/check_greyscale.py --selftest

Exit status: 0 when nothing fails, 1 on a failure (or on a warning with
--strict), 2 on a usage or IO error.
"""

from __future__ import annotations

import argparse
import ast
import itertools
import os
import sys
from typing import Iterable, Sequence

FAIL_THRESHOLD = 10.0
WARN_THRESHOLD = 20.0
MIN_SATURATION = 0.12          # below this a colour is grey: axes, text, ink

IMAGE_EXTS = {".png", ".jpg", ".jpeg", ".tif", ".tiff", ".bmp"}


# --------------------------------------------------------------------------
# Colour science
# --------------------------------------------------------------------------
def _srgb_to_linear(c: float) -> float:
    return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4


def relative_luminance(rgb: Sequence[float]) -> float:
    """Y in [0, 1] from an (r, g, b) triple in [0, 1]."""
    r, g, b = (_srgb_to_linear(float(c)) for c in rgb[:3])
    return 0.2126 * r + 0.7152 * g + 0.0722 * b


def lstar(rgb: Sequence[float]) -> float:
    """CIE L* in [0, 100] from an (r, g, b) triple in [0, 1]."""
    y = relative_luminance(rgb)
    return 116.0 * (y ** (1.0 / 3.0)) - 16.0 if y > 216.0 / 24389.0 else y * 24389.0 / 27.0


def to_rgb(color) -> tuple:
    """Accept '#RRGGBB', 'RRGGBB', a named matplotlib colour, or an rgb tuple."""
    if isinstance(color, (tuple, list)):
        return tuple(float(c) for c in color[:3])
    s = str(color).strip()
    try:
        from matplotlib.colors import to_rgb as mpl_to_rgb

        return tuple(mpl_to_rgb(s))
    except Exception:
        pass
    h = s.lstrip("#")
    if len(h) == 3:
        h = "".join(c * 2 for c in h)
    if len(h) != 6:
        raise ValueError(f"cannot parse colour {color!r}")
    return tuple(int(h[i: i + 2], 16) / 255.0 for i in (0, 2, 4))


def saturation(rgb: Sequence[float]) -> float:
    return max(rgb[:3]) - min(rgb[:3])


def is_chromatic(color) -> bool:
    """True for a real colour; False for black, white, '0.55', 'k', 'grey'.

    Structural ink -- axes, arrows, guide lines, shaded backgrounds -- is drawn
    in greys on purpose and is not a series competing for a hue.
    """
    try:
        rgb = to_rgb(color)
    except ValueError:
        return False
    return saturation(rgb) >= MIN_SATURATION


# Sequential colormaps that are NOT monotone in luminance, so they cannot be
# read once printed: the same grey appears twice at different data values.
# figures/README.md makes viridis the house default for exactly this reason.
BAD_CMAPS = {"jet", "rainbow", "gist_rainbow", "hsv", "nipy_spectral",
             "coolwarm", "bwr", "seismic", "RdYlBu", "RdYlGn", "Spectral",
             "PiYG", "PRGn", "BrBG", "RdBu", "RdGy", "turbo"}


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------
class Report:
    """Verdict tally. FAIL is the only thing that gates; the rest inform."""

    def __init__(self) -> None:
        self.fails: list[str] = []
        self.warns: list[str] = []
        self.recolour: list[str] = []
        self.unknown: list[str] = []
        self.oks = 0

    def fail(self, msg):
        self.fails.append(msg)

    def warn(self, msg):
        self.warns.append(msg)

    def note_recolour(self, msg):
        self.recolour.append(msg)

    def note_unknown(self, msg):
        self.unknown.append(msg)

    def ok(self):
        self.oks += 1


def pairwise_lstar(colors):
    """[(name_a, name_b, dL*)] over every pair, skipping unparseable entries."""
    entries = []
    for c in colors:
        try:
            entries.append((str(c), lstar(to_rgb(c))))
        except ValueError:
            continue
    return [(a, b, abs(la - lb))
            for (a, la), (b, lb) in itertools.combinations(entries, 2)]


# --------------------------------------------------------------------------
# Source mode -- the authoritative check
# --------------------------------------------------------------------------
# Calls that put a data series on the axes. Structural helpers (annotate, text,
# axline for a guide) are not series and are not checked for redundancy.
SERIES_CALLS = {
    "plot", "step", "semilogx", "semilogy", "loglog", "scatter", "errorbar",
    "stem", "bar", "barh", "hist", "fill", "fill_between", "fill_betweenx",
    "axvspan", "axhspan", "hlines", "vlines", "contour", "contourf",
    "pcolormesh", "imshow", "quiver", "arrow", "annotate",
}
# ...but of those, the ones that draw a *comparable series* -- two of these in
# one figure are two things the reader must tell apart. annotate/arrow/imshow
# are excluded: an arrow is labelled in place (see _house.label_curve) and an
# image is one field, not two series.
COMPARABLE = SERIES_CALLS - {"annotate", "arrow", "imshow", "hist"}

COLOR_KW = {"color", "c", "facecolor", "fc", "edgecolor", "ec", "colors",
            "markerfacecolor", "mfc"}
# A non-colour identity: something that survives the loss of hue.
ENCODING_KW = {"linestyle", "ls", "dashes", "linestyles", "marker", "hatch",
               "fmt", "markevery"}
# Positional format strings: 'k--', 'o', 'C0:' -- linestyle/marker inside a str.
FMT_STYLE_CHARS = set("-.:,ovs^<>1234spP*hH+xXDd|_")


class SeriesCall:
    """One plotting call, reduced to the two questions this script asks."""

    def __init__(self, func, lineno, colors, encodings, unknown_color,
                 unknown_encoding, cmap):
        self.func = func
        self.lineno = lineno
        self.colors = colors                  # literal colours passed
        self.encodings = encodings            # literal non-colour encodings
        self.unknown_color = unknown_color    # colour= given, not a literal
        self.unknown_encoding = unknown_encoding
        self.cmap = cmap

    @property
    def chromatic(self):
        return [c for c in self.colors if is_chromatic(c)]

    @property
    def redundant(self):
        return bool(self.encodings) or self.unknown_encoding

    @property
    def color_wholly_unknown(self):
        """A computed colour AND no literal colour to go with it.

        ⚠ The distinction matters. `fill_between(facecolor="0.55",
        hatch=HATCH_CYCLE[0], edgecolor=plt.rcParams["hatch.color"])' -- the
        house shaded-region idiom, used in a dozen figures -- has a computed
        edgecolor and a perfectly legible literal facecolor. Treating that as
        "colour unknown" made every hatched figure unclassifiable, which in turn
        hid cone-nesting-2d.py (nine series, all black) from the recolour list.
        """
        return self.unknown_color and not self.colors

    @property
    def from_cycle(self):
        """No colour given at all -> it comes from axes.prop_cycle.

        In this repo that is automatically redundant: dowling.mplstyle cycles
        colour AND linestyle together, so a bare ax.plot(x, y) gets a distinct
        dash pattern along with its distinct hue. Passing color= explicitly is
        what steps outside that guarantee -- and is therefore the only thing
        this script has to police.
        """
        return not self.colors and not self.unknown_color


def _fmt_encodings(node) -> list:
    """Style characters inside a positional format string, e.g. plot(x, y, 'k--')."""
    out = []
    for arg in node.args:
        if isinstance(arg, ast.Constant) and isinstance(arg.value, str):
            s = arg.value
            if s and len(s) <= 5 and set(s) <= FMT_STYLE_CHARS | set("bgrcmykw"):
                style = "".join(ch for ch in s if ch in FMT_STYLE_CHARS)
                if style:
                    out.append(style)
    return out


def _literal(node, names=None):
    """Python value of a literal node, or None when it is not a literal.

    ``names`` resolves a bare identifier through the module-level constant table
    built by ``_module_constants``. Every figure script in this repo names its
    colours (``BLUE = "#0072B2"``, ``LOCAL = "#E69F00"``) rather than inlining
    the hex, so without this the authoritative mode would report the most
    carefully coloured figures as "computed colour, unreadable" -- and then, on
    finding no literal chromatic colour, misfile them as monochrome.
    """
    try:
        return ast.literal_eval(node)
    except (ValueError, SyntaxError, TypeError):
        pass
    if names is not None and isinstance(node, ast.Name):
        return names.get(node.id)
    return None


def _module_constants(tree) -> dict:
    """{NAME: literal} for module-level ``NAME = <literal>`` assignments."""
    out = {}
    for node in tree.body:
        if not isinstance(node, ast.Assign):
            continue
        try:
            value = ast.literal_eval(node.value)
        except (ValueError, SyntaxError, TypeError):
            continue
        for target in node.targets:
            if isinstance(target, ast.Name):
                out[target.id] = value
    return out


def _source_text(path: str) -> str:
    """Python source for `path`.

    ⚠ A .ipynb needs its code cells extracted first. Notebook JSON is itself a
    valid Python dict literal, so `ast.parse` SUCCEEDS on a raw .ipynb, finds
    zero plotting calls, and the file is scored OK -- a *vacuously clean* PASS
    that looks identical to a real one. That happened on 2026-08-21: five audit
    shards were told to invoke `--source <notebook>.ipynb` and every greyscale
    result they reported was unverified. RiskMeasures.ipynb passed as a
    notebook and produced 36 FAILs once its cells were extracted.

    Jupyter line magics (`!pip`, `%matplotlib`) are not Python, so they are
    blanked rather than dropped -- keeping line numbers aligned with the cell.
    """
    if not path.endswith(".ipynb"):
        return open(path, encoding="utf-8").read()
    import json as _json
    nb = _json.load(open(path, encoding="utf-8"))
    lines = []
    for cell in nb.get("cells", []):
        if cell.get("cell_type") != "code":
            continue
        for line in "".join(cell.get("source", [])).split("\n"):
            stripped = line.lstrip()
            if stripped.startswith(("!", "%", "?")):
                # keep the original indentation, or a magic inside an if/try
                # block turns into an IndentationError and the whole notebook
                # is scored "unparseable" -- another silent non-result.
                indent = line[: len(line) - len(stripped)]
                lines.append(f"{indent}pass  # magic")
            else:
                lines.append(line)
    return "\n".join(lines)


def analyse_source(path: str) -> tuple[list, list]:
    """(series calls, complaints) for one figure script or notebook."""
    try:
        tree = ast.parse(_source_text(path), filename=path)
    except (SyntaxError, OSError, ValueError) as exc:
        return [], [f"{path}: unparseable ({exc})"]

    names = _module_constants(tree)
    calls = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or not isinstance(node.func, ast.Attribute):
            continue
        name = node.func.attr
        if name not in SERIES_CALLS:
            continue

        colors, encodings, cmap = [], [], None
        unknown_color = unknown_encoding = False
        for kw in node.keywords:
            if kw.arg in COLOR_KW:
                v = _literal(kw.value, names)
                if v is None:
                    unknown_color = True
                elif isinstance(v, (list, tuple)) and v and isinstance(v[0], str):
                    colors.extend(v)               # colors=['r', 'b']
                else:
                    colors.append(v)
            elif kw.arg in ENCODING_KW:
                v = _literal(kw.value, names)
                if v is None:
                    unknown_encoding = True
                elif isinstance(v, (list, tuple)):
                    encodings.extend(str(x) for x in v)
                elif v not in (None, "", "none", "None"):
                    encodings.append(str(v))
            elif kw.arg == "cmap":
                cmap = _literal(kw.value)
        encodings.extend(_fmt_encodings(node))
        calls.append(SeriesCall(name, node.lineno, colors, encodings,
                                unknown_color, unknown_encoding, cmap))
    return calls, []


def check_source(path: str, report: Report, verbose: bool = False) -> str:
    """Apply the new rule to one figure script. Returns the verdict."""
    calls, problems = analyse_source(path)
    for p in problems:
        report.fail(p)
    if problems:
        return "ERROR"

    comparable = [c for c in calls if c.func in COMPARABLE]
    coloured = [c for c in comparable if c.chromatic]
    cycled = [c for c in comparable if c.from_cycle]

    # Bad colormap -- a hard fail whatever else the figure does, because a
    # non-monotone ramp maps two different values to one grey.
    bad = [(c.func, c.lineno, c.cmap) for c in calls
           if c.cmap and str(c.cmap).rstrip("_r") in BAD_CMAPS]
    for func, line, cmap in bad:
        report.fail(f"{path}:{line}: {func}(cmap={cmap!r}) is not monotone in "
                    f"luminance -- two data values print as the same grey")

    # THE central test: a grey collapse between two series that have nothing
    # else to tell them apart.
    collapses = []
    for a, b in itertools.combinations(coloured, 2):
        for ca in a.chromatic:
            for cb in b.chromatic:
                if ca == cb:
                    continue
                try:
                    d = abs(lstar(to_rgb(ca)) - lstar(to_rgb(cb)))
                except ValueError:
                    continue
                if d < FAIL_THRESHOLD:
                    collapses.append((a, b, ca, cb, d))

    hard = [(a, b, ca, cb, d) for a, b, ca, cb, d in collapses
            if not a.redundant and not b.redundant]
    soft = [(a, b, ca, cb, d) for a, b, ca, cb, d in collapses
            if (a.redundant or b.redundant)]

    for a, b, ca, cb, d in hard:
        report.fail(f"{path}: {ca} (line {a.lineno}) vs {cb} (line {b.lineno}) "
                    f"dL* = {d:.1f} and NEITHER carries a linestyle, marker or "
                    f"hatch -- these two differ only in hue")

    # A chromatic series with no non-colour identity, but no collapse either.
    lonely = [c for c in coloured if not c.redundant]
    if lonely and not hard:
        for c in lonely:
            report.warn(f"{path}:{c.lineno}: {c.func}(color={c.chromatic}) has "
                        f"no linestyle/marker/hatch -- legible in greyscale "
                        f"only by luminance")

    # A computed colour is only worth a human's attention when nothing else
    # identifies the series. `facecolor="0.55", hatch=HATCH_CYCLE[0]' is a
    # computed ENCODING as well, and that is a non-colour identity -- reporting
    # it produced 22 lines of noise on the first run, every one of them a
    # correctly hatched shaded region.
    for c in comparable:
        if c.color_wholly_unknown and not c.redundant:
            report.note_unknown(f"{path}:{c.lineno}: {c.func} takes a computed "
                                f"colour and no encoding -- read it")

    # Monochrome: no chromatic colour anywhere, and none deferred to a computed
    # value either. Two sub-cases, and they are not the same finding.
    unresolved = any(c.color_wholly_unknown for c in comparable)
    monochrome = len(comparable) >= 2 and not coloured and not cycled and not unresolved
    distinct = {e for c in comparable for e in c.encodings}
    if monochrome and len(distinct) >= 2:
        # RECOLOUR: already told apart without colour, so adding hue cannot
        # break greyscale legibility. Exactly the figures the old rule pushed
        # into monochrome, and the list Prof. Dowling asked for.
        report.note_recolour(
            f"{os.path.basename(path)}: {len(comparable)} series, no colour, "
            f"already distinguished by {sorted(distinct)}")
    elif monochrome:
        # Monochrome AND fewer than two distinct non-colour encodings. This is
        # not a recolour candidate, it is a figure whose series may not be
        # distinguishable at all -- in colour or out of it.
        report.warn(f"{path}: {len(comparable)} series, no colour, and only "
                    f"{len(distinct)} distinct non-colour encoding(s) "
                    f"{sorted(distinct)} -- check the series are told apart "
                    f"by position or direct labelling")

    if verbose:
        print(f"    {len(calls)} plotting call(s); {len(comparable)} comparable, "
              f"{len(coloured)} explicitly coloured, {len(cycled)} from the cycle")
        for c in comparable:
            print(f"      line {c.lineno:>4}  {c.func:<14} "
                  f"colour={c.chromatic or ([str(x) for x in c.colors] or ('<computed>' if c.unknown_color else '<cycle>'))} "
                  f"encoding={c.encodings or ('<computed>' if c.unknown_encoding else '-')}")

    if hard or bad:
        return "FAIL"
    if monochrome:
        return "RECOLOUR" if len(distinct) >= 2 else "MONO"
    if lonely:
        return "WARN"
    report.ok()
    return "OK"


# --------------------------------------------------------------------------
# Style-file mode
# --------------------------------------------------------------------------
def colors_from_style(path: str) -> list:
    import matplotlib
    import matplotlib.style

    with matplotlib.rc_context():
        matplotlib.style.use(path)
        cycle = matplotlib.rcParams["axes.prop_cycle"]
    try:
        return list(cycle.by_key()["color"])
    except KeyError:
        raise ValueError(f"{path} has no 'color' in axes.prop_cycle")


def style_keys(path: str) -> list:
    import matplotlib
    import matplotlib.style

    with matplotlib.rc_context():
        matplotlib.style.use(path)
        return list(matplotlib.rcParams["axes.prop_cycle"].by_key())


def check_style(path: str, n: int, report: Report, verbose: bool) -> None:
    """A style passes when its cycle pairs colour with a non-colour key.

    ⚠ Under the OLD rule this mode also failed the palette on dL*, which is how
    a paired colour+linestyle cycle -- the correct construction -- could be
    reported as a failure. Sky blue and orange are dL* = 0.8 apart and the
    cycle gives them '(0, (5, 1))' and '-.'; that is a pass, and the dL* numbers
    below are printed for information.
    """
    cycle = colors_from_style(path)
    keys = style_keys(path)
    redundant = [k for k in keys if k in ("linestyle", "ls", "dashes", "marker")]
    print(f"  style: {path}")
    print(f"    prop_cycle keys: {', '.join(keys)}")
    if redundant:
        print(f"    [OK  ] cycle pairs colour with {', '.join(redundant)} -- "
              f"every series gets a non-colour identity automatically")
        report.ok()
    else:
        report.fail(f"{path}: axes.prop_cycle cycles colour ONLY. Every series "
                    f"drawn from it is identified by hue alone.")
        print("    [FAIL] cycle carries NO redundant non-colour encoding")

    k = min(n, len(cycle))
    print(f"    first {k} of {len(cycle)} cycle colours, pairwise dL*"
          f"{' (informational -- linestyle carries the identity)' if redundant else ''}:")
    for a, b, d in pairwise_lstar(cycle[:k]):
        tag = "collapse" if d < FAIL_THRESHOLD else ("close" if d < WARN_THRESHOLD else "clear")
        if verbose or d < WARN_THRESHOLD:
            print(f"      {a:>10} vs {b:<10} dL* = {d:6.2f}  {tag}")
        if d < FAIL_THRESHOLD and not redundant:
            report.fail(f"{path}: {a} vs {b} dL* = {d:.2f} with no redundant "
                        f"encoding")


# --------------------------------------------------------------------------
# Explicit palette mode
# --------------------------------------------------------------------------
def check_palette(colors, label, report, redundant: bool, verbose: bool) -> None:
    print(f"  palette {label} ({len(colors)} entries)"
          f"{'  [caller asserts redundant encoding]' if redundant else ''}")
    if verbose:
        for c in colors:
            try:
                print(f"      {str(c):>24}  L* = {lstar(to_rgb(c)):6.2f}")
            except ValueError as exc:
                print(f"      ! {exc}", file=sys.stderr)
    for a, b, d in pairwise_lstar(colors):
        if d < FAIL_THRESHOLD:
            if redundant:
                report.warn(f"{label}: {a} vs {b} dL* = {d:.2f} -- one grey in "
                            f"print; the declared linestyle/marker carries it")
                verdict = "WARN"
            else:
                report.fail(f"{label}: {a} vs {b} dL* = {d:.2f} and no "
                            f"redundant encoding declared")
                verdict = "FAIL"
        elif d < WARN_THRESHOLD:
            report.ok()
            verdict = "close"
        else:
            report.ok()
            verdict = "OK"
        if verbose or verdict in ("FAIL", "WARN"):
            print(f"      [{verdict:<5}] {a:>18} vs {b:<18} dL* = {d:6.2f}")


# --------------------------------------------------------------------------
# Image mode -- triage only
# --------------------------------------------------------------------------
def dominant_colors(path: str, max_colors: int = 8,
                    min_saturation: float = MIN_SATURATION,
                    min_pixel_fraction: float = 0.0008) -> list:
    """Saturated colours occupying a meaningful share of the image."""
    from PIL import Image

    img = Image.open(path).convert("RGB")
    img.thumbnail((600, 600), Image.Resampling.NEAREST)
    total = img.size[0] * img.size[1]
    quant = img.quantize(colors=64, method=Image.Quantize.FASTOCTREE).convert("RGB")

    counts: dict = {}
    for count, rgb in quant.getcolors(maxcolors=1 << 20) or []:
        counts[rgb] = counts.get(rgb, 0) + count

    picked = []
    for rgb, count in sorted(counts.items(), key=lambda kv: -kv[1]):
        f = (rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0)
        if saturation(f) < min_saturation or count / total < min_pixel_fraction:
            continue
        picked.append(("#%02X%02X%02X" % rgb, count / total))
        if len(picked) >= max_colors:
            break
    return picked


def check_image(path: str, report: Report, min_sat: float, min_frac: float,
                verbose: bool) -> str:
    """Report, never fail: pixels cannot say whether an encoding is redundant."""
    try:
        cols = dominant_colors(path, min_saturation=min_sat,
                               min_pixel_fraction=min_frac)
    except Exception as exc:                                    # noqa: BLE001
        report.fail(f"{path}: unreadable ({exc})")
        return "ERROR"
    if len(cols) < 2:
        if not cols:
            report.note_recolour(f"{os.path.basename(path)}: rendered with no "
                                 f"chromatic colour at all")
            return "RECOLOUR"
        report.ok()
        return "OK"
    worst = min((d for _a, _b, d in pairwise_lstar([c for c, _f in cols])),
                default=None)
    if worst is not None and worst < FAIL_THRESHOLD:
        report.warn(f"{path}: two rendered colours are dL* = {worst:.1f} apart. "
                    f"Check the SOURCE for a linestyle/marker/hatch; pixels "
                    f"cannot tell.")
        return "WARN"
    report.ok()
    return "OK"


def iter_images(paths: Iterable[str]) -> Iterable[str]:
    for p in paths:
        if os.path.isdir(p):
            for root, _dirs, files in os.walk(p):
                for f in sorted(files):
                    if os.path.splitext(f)[1].lower() in IMAGE_EXTS:
                        yield os.path.join(root, f)
        else:
            yield p


def iter_sources(paths: Iterable[str]) -> Iterable[str]:
    for p in paths:
        if os.path.isdir(p):
            for f in sorted(os.listdir(p)):
                # figures/plots/_*.py are shared helpers, not figures -- the
                # Makefile's wildcard skips them and so does this.
                if f.endswith(".py") and not f.startswith("_"):
                    yield os.path.join(p, f)
        else:
            yield p


# --------------------------------------------------------------------------
def main(argv: Sequence[str] | None = None) -> int:
    global FAIL_THRESHOLD, WARN_THRESHOLD

    ap = argparse.ArgumentParser(
        description="Check that colour figures survive black-and-white printing.",
        formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    ap.add_argument("paths", nargs="*", help="rendered images or directories")
    ap.add_argument("--source", nargs="+", default=None,
                    help="figure scripts or a directory of them (authoritative)")
    ap.add_argument("--style", help="matplotlib style file to check")
    ap.add_argument("--colors", nargs="+", help="explicit colour list")
    ap.add_argument("--redundant", action="store_true",
                    help="with --colors: assert the figure also varies "
                         "linestyle/marker/hatch, so a grey collapse is a "
                         "warning rather than a failure")
    ap.add_argument("--recolour", "--recolor", dest="recolour",
                    action="store_true",
                    help="list only the figures that are candidates for having "
                         "colour put back")
    ap.add_argument("-n", "--n-series", type=int, default=4,
                    help="how many cycle entries to report (default 4)")
    ap.add_argument("--fail-threshold", type=float, default=FAIL_THRESHOLD)
    ap.add_argument("--warn-threshold", type=float, default=WARN_THRESHOLD)
    ap.add_argument("--min-fraction", type=float, default=0.0008,
                    help="image mode: ignore colours below this area fraction")
    ap.add_argument("--min-saturation", type=float, default=MIN_SATURATION,
                    help="treat colours below this max-min RGB spread as grey")
    ap.add_argument("--strict", action="store_true", help="warnings fail too")
    ap.add_argument("-v", "--verbose", action="store_true")
    ap.add_argument("--selftest", action="store_true",
                    help="prove the checker passes colour and fails hue-only")
    args = ap.parse_args(argv)

    if args.selftest:
        return selftest()

    FAIL_THRESHOLD = args.fail_threshold
    WARN_THRESHOLD = args.warn_threshold

    if not (args.style or args.colors or args.paths or args.source):
        ap.error("give --source, --style, --colors, or image paths")

    report = Report()

    if args.colors:
        check_palette(args.colors, "colors", report, args.redundant, True)
        print()

    if args.style:
        try:
            check_style(args.style, args.n_series, report, args.verbose)
        except Exception as exc:                                # noqa: BLE001
            print(f"error: {exc}", file=sys.stderr)
            return 2
        print()

    if args.source:
        sources = list(iter_sources(args.source))
        print(f"Figure sources ({len(sources)})")
        for path in sources:
            verdict = check_source(path, report, verbose=args.verbose)
            if args.recolour and verdict != "RECOLOUR":
                continue
            print(f"  [{verdict:<8}] {os.path.relpath(path)}")
        print()

    images = list(iter_images(args.paths))
    if images:
        print(f"Rendered images ({len(images)})  -- triage only")
        for path in images:
            verdict = check_image(path, report, args.min_saturation,
                                  args.min_fraction, args.verbose)
            if args.recolour and verdict != "RECOLOUR":
                continue
            print(f"  [{verdict:<8}] {os.path.relpath(path)}")
        print()

    print("=" * 72)
    print(f"OK {report.oks}   WARN {len(report.warns)}   "
          f"FAIL {len(report.fails)}   RECOLOUR {len(report.recolour)}   "
          f"UNKNOWN {len(report.unknown)}")
    for m in report.fails:
        print(f"  FAIL      {m}")
    for m in report.warns:
        print(f"  WARN      {m}")
    for m in report.unknown:
        print(f"  UNKNOWN   {m}")
    if report.recolour:
        print()
        print("RECOLOUR CANDIDATES -- monochrome, and already distinguished "
              "without colour.")
        print("  These are safe to re-colourise: the non-colour encoding is "
              "already in place,")
        print("  so adding hue cannot break greyscale legibility. "
              "Not a failure; a suggestion.")
        for m in report.recolour:
            print(f"  RECOLOUR  {m}")

    if report.fails:
        print("\nRESULT: FAIL -- above, a distinction is carried by colour ALONE.")
        return 1
    if args.strict and report.warns:
        print("\nRESULT: FAIL (--strict) -- warnings present.")
        return 1
    print("\nRESULT: PASS -- every distinction is carried by something other "
          "than hue.")
    return 0


# --------------------------------------------------------------------------
def selftest() -> int:
    """Prove BOTH directions, on synthetic figure scripts.

    The old script had no self-test at all, and its rule was the opposite of
    the one now wanted, so "it passes" would have meant nothing. Case 1 below
    is the exact figure the old rule REJECTED and the new rule must accept.
    """
    import tempfile

    print("Self-test: check_greyscale.py\n")
    ok = True

    def case(label, script, want):
        nonlocal ok
        with tempfile.TemporaryDirectory() as tmp:
            p = os.path.join(tmp, "fig.py")
            open(p, "w").write(script)
            r = Report()
            got = check_source(p, r)
        good = got == want
        ok &= good
        print(f"  {'OK  ' if good else 'FAIL'} {label}: {got} (expected {want})")
        if not good:
            for m in r.fails + r.warns + r.recolour:
                print(f"         {m}")
        return r

    # 1. THE CASE THE OLD RULE GOT WRONG. Sky blue and orange are dL* = 0.8
    #    apart -- one grey in print -- but the two curves are dashed and dotted,
    #    so the greyscale reader is fine and the colour reader gets colour.
    case("colourful WITH redundant encoding", '''
import matplotlib.pyplot as plt
def make_figure():
    fig, ax = plt.subplots()
    ax.plot(x, y1, color="#56B4E9", linestyle="--", label="a")
    ax.plot(x, y2, color="#E69F00", linestyle=":", label="b")
    return fig
''', "OK")

    # 2. The same two colours with nothing else: hue is the only difference.
    case("two colours differing only in hue", '''
import matplotlib.pyplot as plt
def make_figure():
    fig, ax = plt.subplots()
    ax.plot(x, y1, color="#56B4E9", label="a")
    ax.plot(x, y2, color="#E69F00", label="b")
    return fig
''', "FAIL")

    # 3. Markers are a non-colour identity just as linestyles are.
    case("same collapse, told apart by MARKER", '''
import matplotlib.pyplot as plt
def make_figure():
    fig, ax = plt.subplots()
    ax.plot(x, y1, color="#56B4E9", marker="o")
    ax.plot(x, y2, color="#E69F00", marker="s")
    return fig
''', "OK")

    # 4. Hatching does it for filled regions.
    case("shaded regions told apart by HATCH", '''
import matplotlib.pyplot as plt
def make_figure():
    fig, ax = plt.subplots()
    ax.fill_between(x, a, b, facecolor="#56B4E9", hatch="///")
    ax.fill_between(x, c, d, facecolor="#E69F00", hatch="...")
    return fig
''', "OK")

    # 5. Well-separated luminances, no linestyle: allowed, with a warning.
    #    Blue L* = 46.0, yellow L* = 89.1.
    case("separated luminance, no encoding", '''
import matplotlib.pyplot as plt
def make_figure():
    fig, ax = plt.subplots()
    ax.plot(x, y1, color="#0072B2")
    ax.plot(x, y2, color="#F0E442")
    return fig
''', "WARN")

    # 6. The house cycle: no colour given, so colour AND linestyle both come
    #    from dowling.mplstyle. Nothing to police.
    case("series drawn from the prop_cycle", '''
import matplotlib.pyplot as plt
def make_figure():
    fig, ax = plt.subplots()
    ax.plot(x, y1, label="a")
    ax.plot(x, y2, label="b")
    return fig
''', "OK")

    # 7. Monochrome with two linestyles -- the shape of a figure flattened to
    #    satisfy the old rule. Must be flagged, must NOT fail.
    r = case("monochrome, two linestyles", '''
import matplotlib.pyplot as plt
def make_figure():
    fig, ax = plt.subplots()
    ax.plot(x, y1, color="k", linestyle="-")
    ax.plot(x, y2, color="0.45", linestyle="--")
    return fig
''', "RECOLOUR")
    good = bool(r.recolour) and not r.fails
    ok &= good
    print(f"  {'OK  ' if good else 'FAIL'} ...and it is listed as a recolour "
          f"candidate, not a failure")

    # 8. Greys are structural ink, not series: axes furniture must not trip it.
    case("grey guide lines are not series", '''
import matplotlib.pyplot as plt
def make_figure():
    fig, ax = plt.subplots()
    ax.axhline(0, color="0.6")
    ax.axvline(0, color="0.7")
    ax.plot(x, y, color="#0072B2", linestyle="--")
    return fig
''', "OK")

    # 9. A non-monotone colormap fails outright: two data values, one grey.
    case("cmap=jet", '''
import matplotlib.pyplot as plt
def make_figure():
    fig, ax = plt.subplots()
    ax.contourf(X, Y, Z, cmap="jet")
    return fig
''', "FAIL")
    case("cmap=viridis", '''
import matplotlib.pyplot as plt
def make_figure():
    fig, ax = plt.subplots()
    ax.contourf(X, Y, Z, cmap="viridis")
    return fig
''', "OK")

    # 10. Positional format strings count as encoding: plot(x, y, '--').
    case("format string carries the linestyle", '''
import matplotlib.pyplot as plt
def make_figure():
    fig, ax = plt.subplots()
    ax.plot(x, y1, "--", color="#56B4E9")
    ax.plot(x, y2, ":", color="#E69F00")
    return fig
''', "OK")

    # --- colour science, checked against the numbers in figures/README.md ---
    for hexv, want in [("#000000", 0.0), ("#0072B2", 46.0), ("#E69F00", 70.6),
                       ("#56B4E9", 69.8), ("#F0E442", 89.1)]:
        got = lstar(to_rgb(hexv))
        good = abs(got - want) < 0.15
        ok &= good
        print(f"  {'OK  ' if good else 'FAIL'} L*({hexv}) = {got:.1f} "
              f"(README says {want})")
    d = abs(lstar(to_rgb("#56B4E9")) - lstar(to_rgb("#E69F00")))
    good = d < 1.0
    ok &= good
    print(f"  {'OK  ' if good else 'FAIL'} sky blue vs orange dL* = {d:.2f} "
          f"-- the collapse the whole rule is about")

    # --- chromatic vs structural ------------------------------------------
    for c, want in [("#0072B2", True), ("k", False), ("black", False),
                    ("0.55", False), ("white", False), ("#E69F00", True),
                    ("tab:red", True)]:
        got = is_chromatic(c)
        good = got == want
        ok &= good
        print(f"  {'OK  ' if good else 'FAIL'} is_chromatic({c!r}) = {got} "
              f"(expected {want})")

    # --- palette mode, both directions ------------------------------------
    r = Report()
    check_palette(["#56B4E9", "#E69F00"], "hue-only", r, redundant=False,
                  verbose=False)
    good = bool(r.fails)
    ok &= good
    print(f"  {'OK  ' if good else 'FAIL'} --colors without --redundant FAILS "
          f"a collapsing pair")
    r = Report()
    check_palette(["#56B4E9", "#E69F00"], "declared", r, redundant=True,
                  verbose=False)
    good = not r.fails and bool(r.warns)
    ok &= good
    print(f"  {'OK  ' if good else 'FAIL'} --colors --redundant downgrades it "
          f"to a warning")

    # --- style mode, on the real house style if it is here -----------------
    style = os.path.join(os.path.dirname(os.path.dirname(
        os.path.abspath(__file__))), "figures", "dowling.mplstyle")
    if os.path.exists(style):
        try:
            r = Report()
            check_style(style, 4, r, verbose=False)
            good = not r.fails
            ok &= good
            print(f"  {'OK  ' if good else 'FAIL'} the house style PASSES "
                  f"(colour paired with linestyle) despite dL* = 0.8 in the cycle")
        except Exception as exc:                                # noqa: BLE001
            print(f"  note  style mode not exercised: {exc}")
    else:
        print(f"  note  {style} not found; style mode not exercised")

    print()
    print("SELF-TEST PASSED" if ok else "SELF-TEST FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
