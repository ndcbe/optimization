"""Backward-compatible shim. The implementation now lives in ``helper.py``.

    import pyomo_results as pyr     # still works, unchanged
    import helper                   # ...and this is where the code is

WHY THIS FILE STILL EXISTS
--------------------------
Prof. Dowling, 2026-08-25: *"Let's have helper contain all of the useful
scripts/colab add-ons. After the worker lands and we confirm the approach for
this notebook, we can expand this to a class-wide strategy."*

So the merge into ``helper.py`` is a **pilot**, proven on
``notebooks/1-dev/NLP.ipynb`` first. This shim is what makes the pilot
incremental rather than a flag day: five notebooks and two scripts spell the
import ``pyomo_results``, and none of them had to change on the day the code
moved.

    notebooks/1-dev/NLP.ipynb                 -> migrated: imports helper
    notebooks/1-dev/Milk-Pooling.ipynb        -> still `import pyomo_results as pyr`
    notebooks/1-dev/Portfolio-Optimization.ipynb
    notebooks/1-dev/Pyomo-Introduction.ipynb
    notebooks/1-dev/Pyomo-Nuts-and-Bolts.ipynb
    scripts/check_results_fresh.py            -> uses REQUIRED_META and _extractor
    figures/render_from_notebook.py           -> wraps save_* in _ReadOnlyResults

⚠ **A shim with no end date is a second name for one thing forever**, which is
the drift this repo's ``figures/`` directory exists to prevent. The class-wide
pass repoints the four remaining notebooks and the two scripts at ``helper``
and **deletes this file**; record the deletion in the private repo's
``claude/deleted_notebooks.md``, as the never-delete-without-recording rule
requires.

⚠ NOT deleted in the pilot on purpose. Doing it now would mean editing four
notebooks that are not under review in the same change as the module move, and
a half-merged module is worse than either end state.

WHAT CHANGED BEHIND THE SHIM
----------------------------
One thing, and it is a fix rather than a move: ``save_results`` and
``save_figure`` **no longer return the path they wrote**. They used to, and
because the cell contract puts ``pyr.save_figure(fig, name)`` last in a
notebook cell, that return value was published on the course website as an
absolute path inside the maintainer's home directory. See the "NEITHER WRITER
RETURNS A VALUE" note in ``helper.py``. Nothing consumed the value.
"""

import os
import sys

# This file and helper.py are siblings. A caller that can import this one can
# not be assumed to have the directory on sys.path -- `import pyomo_results`
# may have been reached via a path entry that is now gone, and on Colab this
# file is fetched into the working directory. Adding it here is cheap and makes
# the shim work everywhere the real module did.
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import helper as _helper  # noqa: E402

# The public API, re-exported by name rather than with `import *`, so this list
# IS the record of what the module ever promised.
from helper import (  # noqa: E402,F401
    FIGURE_TAG_PREFIX,
    FIGURES_SUBDIR,
    PNG_DPI,
    RAW_BASE,
    REQUIRED_META,
    RESULTS_SUBDIR,
    SCHEMA,
    as_dataframe,
    column,
    digest_of_tag,
    extract,
    have_repo,
    load_results,
    on_colab,
    results_dir,
    save_figure,
    save_results,
    table,
    value_of,
)

# Private names that other modules in this repo genuinely reach for:
#   scripts/check_results_fresh.py  -> pyomo_results._extractor()
# Re-exported explicitly rather than left to chance, because `import *` would
# silently drop them and the failure would surface as a checker self-test
# breaking, not as an import error here.
from helper import (  # noqa: E402,F401
    _HERE,
    _REPO,
    _extractor,
    _jsonable,
    _scalar,
)

__version__ = _helper.__version__
