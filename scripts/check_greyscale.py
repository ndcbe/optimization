#!/usr/bin/env python3
"""Check that a figure's series stay distinguishable when printed in black and white.

Course policy (see figures/README.md): colour first, greyscale guaranteed. The
colour version is designed to be as good as possible; this script is the
pass/fail floor that guarantees the student who prints the handout on a mono
laser printer can still read it.

Three modes, all of which gate on exit status so this can run in CI:

  --style FILE          check the axes.prop_cycle of a matplotlib style file
  --colors C1 C2 ...    check an explicit list of colours
  PATH [PATH ...]       check rendered images (PNG/JPG) or directories of them

Measurement
-----------
Colours are converted to CIE L* (perceptual lightness, 0=black, 100=white) via
linearised sRGB relative luminance Y = 0.2126R + 0.7152G + 0.0722B. Greyscale
printing preserves Y, so two colours with the same L* print as the same grey no
matter how different they look on screen.

  dL* <  FAIL_THRESHOLD (default 10)  -> FAIL. The pair collapses.
  dL* <  WARN_THRESHOLD (default 20)  -> WARN. Legible only because linestyle,
                                         marker or direct labelling carries a
                                         redundant, colour-free identity.
  dL* >= WARN_THRESHOLD               -> OK.

Honest limitation of image mode
-------------------------------
You cannot recover "which pixels are series 3" from a finished PNG. Image mode
therefore quantises the image, discards background/greys/axis ink, and checks
pairwise L* separation among the *saturated colours actually present*. It will
flag a figure that uses two same-luminance colours anywhere. It will NOT know
whether those two colours are two data series or one series and a shaded band,
and it cannot see that a legend is keyed by colour alone. Style/colour mode is
the authoritative check; image mode is a net for figures whose source is lost
(screenshots, contributed notebooks, legacy PNGs).

Exit status: 0 all OK (warnings allowed unless --strict), 1 at least one FAIL
(or, with --strict, at least one WARN), 2 usage/IO error.
"""

from __future__ import annotations

import argparse
import itertools
import os
import sys
from typing import Iterable, Sequence

FAIL_THRESHOLD = 10.0
WARN_THRESHOLD = 20.0

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
    return tuple(int(h[i : i + 2], 16) / 255.0 for i in (0, 2, 4))


def saturation(rgb: Sequence[float]) -> float:
    return max(rgb[:3]) - min(rgb[:3])


# --------------------------------------------------------------------------
# Reporting
# --------------------------------------------------------------------------
class Report:
    def __init__(self) -> None:
        self.fails: list[str] = []
        self.warns: list[str] = []
        self.oks = 0

    def record(self, label: str, a: str, b: str, d: float) -> str:
        if d < FAIL_THRESHOLD:
            self.fails.append(f"{label}: {a} vs {b}  dL* = {d:5.2f}")
            return "FAIL"
        if d < WARN_THRESHOLD:
            self.warns.append(f"{label}: {a} vs {b}  dL* = {d:5.2f}")
            return "WARN"
        self.oks += 1
        return "OK"


def check_palette(colors: Sequence, label: str, report: Report, verbose: bool) -> None:
    """Pairwise L* separation over a list of colours."""
    entries = []
    for c in colors:
        try:
            rgb = to_rgb(c)
        except ValueError as exc:
            print(f"  ! {exc}", file=sys.stderr)
            continue
        entries.append((str(c), rgb, lstar(rgb)))

    if verbose:
        for name, _rgb, L in entries:
            print(f"    {name:>28}  L* = {L:6.2f}")

    for (na, _ra, La), (nb, _rb, Lb) in itertools.combinations(entries, 2):
        d = abs(La - Lb)
        verdict = report.record(label, na, nb, d)
        if verbose or verdict != "OK":
            print(f"    [{verdict:4}] {na:>18} vs {nb:<18} dL* = {d:6.2f}")


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


def style_has_redundant_encoding(path: str) -> tuple[bool, list]:
    import matplotlib
    import matplotlib.style

    with matplotlib.rc_context():
        matplotlib.style.use(path)
        keys = list(matplotlib.rcParams["axes.prop_cycle"].by_key())
    redundant = [k for k in keys if k in ("linestyle", "ls", "marker", "dashes")]
    return bool(redundant), keys


# --------------------------------------------------------------------------
# Image mode
# --------------------------------------------------------------------------
def dominant_colors(path: str, max_colors: int = 8, min_saturation: float = 0.12,
                    min_pixel_fraction: float = 0.0008) -> list:
    """Saturated colours occupying a meaningful share of the image.

    Greys (low saturation) are dropped: they are background, axes, text and
    gridlines, not data series.
    """
    from PIL import Image

    img = Image.open(path).convert("RGB")
    # Cap work on large images; nearest-neighbour keeps colours exact.
    img.thumbnail((600, 600), Image.Resampling.NEAREST)
    total = img.size[0] * img.size[1]
    # Quantise so antialiased edge pixels merge into their parent colour.
    quant = img.quantize(colors=64, method=Image.Quantize.FASTOCTREE).convert("RGB")

    counts: dict = {}
    for count, rgb in quant.getcolors(maxcolors=1 << 20) or []:
        counts[rgb] = counts.get(rgb, 0) + count

    picked = []
    for rgb, count in sorted(counts.items(), key=lambda kv: -kv[1]):
        f = (rgb[0] / 255.0, rgb[1] / 255.0, rgb[2] / 255.0)
        if saturation(f) < min_saturation:
            continue
        if count / total < min_pixel_fraction:
            continue
        picked.append(("#%02X%02X%02X" % rgb, count / total))
        if len(picked) >= max_colors:
            break
    return picked


def white_border_fraction(path: str, tol: int = 250) -> float:
    """Fraction of the image area that is uniform white margin around the content.

    Catches PDF-crop screenshots that arrive padded with dead space.
    """
    from PIL import Image, ImageChops

    img = Image.open(path).convert("RGB")
    bg = Image.new("RGB", img.size, (255, 255, 255))
    diff = ImageChops.difference(img, bg).convert("L").point(lambda p: 255 if p > (255 - tol) else 0)
    bbox = diff.getbbox()
    if bbox is None:
        return 1.0
    area = img.size[0] * img.size[1]
    content = (bbox[2] - bbox[0]) * (bbox[3] - bbox[1])
    return 1.0 - content / area


def iter_images(paths: Iterable[str]) -> Iterable[str]:
    for p in paths:
        if os.path.isdir(p):
            for root, _dirs, files in os.walk(p):
                for f in sorted(files):
                    if os.path.splitext(f)[1].lower() in IMAGE_EXTS:
                        yield os.path.join(root, f)
        else:
            yield p


# --------------------------------------------------------------------------
def main(argv: Sequence[str] | None = None) -> int:
    global FAIL_THRESHOLD, WARN_THRESHOLD

    ap = argparse.ArgumentParser(
        description="Check that figure series survive black-and-white printing.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("paths", nargs="*", help="image files or directories to check")
    ap.add_argument("--style", help="matplotlib style file; checks its axes.prop_cycle")
    ap.add_argument("--colors", nargs="+", help="explicit colour list to check")
    ap.add_argument("-n", "--n-series", type=int, default=4,
                    help="how many entries of the style cycle to check (default 4)")
    ap.add_argument("--fail-threshold", type=float, default=FAIL_THRESHOLD)
    ap.add_argument("--warn-threshold", type=float, default=WARN_THRESHOLD)
    ap.add_argument("--min-fraction", type=float, default=0.0008,
                    help="image mode: ignore colours covering less than this fraction of "
                         "the image (default 0.0008). Raise to ~0.005 on screenshots, whose "
                         "subpixel/JPEG fringing produces phantom colours at 0.1-0.4%%.")
    ap.add_argument("--min-saturation", type=float, default=0.12,
                    help="image mode: treat colours below this max-min RGB spread as grey "
                         "(background, axes, text) and ignore them (default 0.12)")
    ap.add_argument("--strict", action="store_true", help="treat warnings as failures")
    ap.add_argument("-v", "--verbose", action="store_true")
    args = ap.parse_args(argv)

    FAIL_THRESHOLD = args.fail_threshold
    WARN_THRESHOLD = args.warn_threshold

    if not (args.style or args.colors or args.paths):
        ap.error("give --style, --colors, or one or more image paths")

    report = Report()

    if args.colors:
        print(f"Colour list ({len(args.colors)} entries)")
        check_palette(args.colors, "colors", report, verbose=True)
        print()

    if args.style:
        try:
            cycle = colors_from_style(args.style)
        except Exception as exc:
            print(f"error: {exc}", file=sys.stderr)
            return 2
        redundant, keys = style_has_redundant_encoding(args.style)
        n = min(args.n_series, len(cycle))
        print(f"Style: {args.style}")
        print(f"  prop_cycle keys: {', '.join(keys)}")
        if redundant:
            print("  [OK  ] cycle carries a redundant non-colour encoding")
        else:
            report.fails.append(
                f"{args.style}: axes.prop_cycle cycles colour only "
                "(no linestyle/marker) — series are unidentifiable in greyscale"
            )
            print("  [FAIL] cycle carries NO redundant non-colour encoding")
        print(f"  first {n} of {len(cycle)} cycle colours:")
        check_palette(cycle[:n], f"{os.path.basename(args.style)}[:{n}]", report,
                      verbose=args.verbose)
        print()

    images = list(iter_images(args.paths))
    if images:
        print(f"Images ({len(images)})")
    for path in images:
        try:
            cols = dominant_colors(path, min_saturation=args.min_saturation,
                                   min_pixel_fraction=args.min_fraction)
            wb = white_border_fraction(path)
        except Exception as exc:
            print(f"  {path}: error: {exc}", file=sys.stderr)
            report.fails.append(f"{path}: unreadable ({exc})")
            continue
        rel = path
        if len(cols) < 2:
            note = "greyscale/monochrome already" if not cols else "single data colour"
            print(f"  [OK  ] {rel}  ({note}; white border {wb:5.1%})")
            report.oks += 1
            continue
        print(f"  ---- {rel}  ({len(cols)} data colours; white border {wb:5.1%})")
        check_palette([c for c, _f in cols], rel, report, verbose=args.verbose)

    print()
    print("=" * 68)
    print(f"OK {report.oks}   WARN {len(report.warns)}   FAIL {len(report.fails)}")
    for w in report.warns:
        print(f"  WARN  {w}")
    for f in report.fails:
        print(f"  FAIL  {f}")

    if report.fails:
        print("\nRESULT: FAIL — pairs above are the same grey once printed.")
        return 1
    if args.strict and report.warns:
        print("\nRESULT: FAIL (--strict) — warnings present.")
        return 1
    if report.warns:
        print("\nRESULT: PASS with warnings — those pairs are legible ONLY because "
              "linestyle/marker/direct labelling distinguishes them. Confirm they do.")
    else:
        print("\nRESULT: PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
