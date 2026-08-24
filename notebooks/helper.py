import shutil
import sys
import os.path
import os
import requests
import urllib

import subprocess


#!/usr/bin/env python
###############################################################################
# The Institute for the Design of Advanced Energy Systems Integrated Platform
# Framework (IDAES IP) was produced under the DOE Institute for the
# Design of Advanced Energy Systems (IDAES).
#
# Copyright (c) 2018-2023 by the software owners: The Regents of the
# University of California, through Lawrence Berkeley National Laboratory,
# National Technology & Engineering Solutions of Sandia, LLC, Carnegie Mellon
# University, West Virginia University Research Corporation, et al.
# All rights reserved.  Please see the files COPYRIGHT.md and LICENSE.md
# for full copyright and license information.
###############################################################################
# This package was further modified by Alex Dowling for use in the course
# It is available under the IDAES license.

"""
Install IDAES, Ipopt, and other solvers on Google Colab

Created by Alex Dowling (adowling@nd.edu) and Jeff Kantor at the University of Notre Dame
with input from John Siirola at Sandia National Laboratories.

To use this script, add the following to a code block in a Jupyter notebook:

```
import sys
if "google.colab" in sys.modules:
    !wget "https://raw.githubusercontent.com/ndcbe/optimization/main/notebooks/helper.py"
    import helper
    helper.easy_install()
else:
    sys.path.insert(0, '../')
    import helper
helper.set_plotting_style()
```
"""

__version__ = "2026.08.24"

import shutil
import sys
import os.path
import os
import re

import subprocess

import matplotlib.pyplot as plt

# The house figure style. ONE source of style, shared with the LaTeX lecture
# handouts -- see figures/README.md. On Colab only the notebook is present (this
# file itself is fetched by raw URL), so the repo copy cannot be assumed on disk.
_STYLE_URL = (
    "https://raw.githubusercontent.com/ndcbe/optimization/main/figures/dowling.mplstyle"
)
_STYLE_LOCAL = "../../figures/dowling.mplstyle"

# figure.figsize is DELIBERATELY not taken from the style file. See the docstring
# of set_plotting_style below; 6.4 x 4.8 is matplotlib's own default, which is
# what every notebook in this repo has always rendered at.
NOTEBOOK_FIGSIZE = (6.4, 4.8)


def set_plotting_style(figsize=NOTEBOOK_FIGSIZE):
    """Apply the course house figure style to every subsequent matplotlib figure.

    Loads ``figures/dowling.mplstyle`` -- the single source of figure style,
    shared with the LaTeX lecture handouts -- so a notebook figure and a handout
    figure look like they came from the same course. That brings in the
    Okabe-Ito colour cycle paired element-wise with a linestyle cycle (so every
    series carries a redundant, colour-free identity and survives greyscale
    printing), viridis as the default colormap, inward ticks on all four sides,
    and the guide's font and line weights. Read the header of the style file for
    why each of those is the way it is.

    Arguments:
        figsize: default figure size in inches, or None to accept the style
            file's own ``figure.figsize``.

    Notes:
        **Why figsize is overridden.** The style file sets ``figure.figsize: 4, 4``,
        which is calibrated for a single-column figure in the printed handout.
        A notebook figure is rendered inline in a browser at its native size, and
        at 4 x 4 the style's own 16 pt bold axis labels and 15 pt tick labels no
        longer fit: x tick labels get dropped and legends collide with the data.
        Canvas size is layout, and layout is per-medium; everything that is
        figure *identity* -- colour, linestyle, colormap, fonts, ticks -- is
        taken from the style file unchanged. Individual figures should still set
        their own ``figsize`` when the aspect ratio matters, exactly as the
        scripts in ``figures/plots/`` do.

        **Grid.** The style sets ``axes.grid: False``. A notebook that calls
        ``plt.grid(True)`` still gets a grid; the house convention is to leave it
        off and use light ``axvline`` rules where a reading aid is needed.
    """
    style = _STYLE_URL if on_colab() else _STYLE_LOCAL

    try:
        plt.style.use(style)
    except (OSError, ValueError) as e:
        # Never let a missing style file break a notebook: a wrong-looking plot
        # is recoverable, a stopped notebook in front of a class is not.
        print(f"WARNING: could not load the house style from {style} ({e}).")
        print("Falling back to matplotlib defaults with the course line width.")
        plt.rc("lines", linewidth=3)

    if figsize is not None:
        plt.rc("figure", figsize=figsize)


def _check_available(executable_name):
    """Utility to check in an executable is available"""
    return shutil.which(executable_name) or os.path.isfile(executable_name)


def package_available(package_name):
    """Utility to check if a package/executable is available

    This supports customization, e.g., glpk, for special package names
    """

    if package_name == "glpk":
        return _check_available("glpsol")
    else:
        return _check_available(package_name)


def on_colab():
    """Utility returns True if executed on Colab, False otherwise"""
    return "google.colab" in sys.modules

def install_idaes(verbose=False):
    """Installs latest version of IDAES-PSE via pip

    Argument:
        verbose: bool, if True, display console output from pip install

    """

    try:
        import idaes

        print("idaes was found! No need to install.")
    except ImportError:
        print("Installing idaes via pip...")
        v = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", "idaes_pse"],
            check=True,
            capture_output=True,
            text=True,
        )
        if verbose:
            print(v.stdout)
            print(v.stderr)
        print("idaes was successfully installed")
        v = subprocess.run(
            ["idaes", "--version"], check=True, capture_output=True, text=True
        )
        print(v.stdout)
        print(v.stderr)


def install_ipopt(verbose=False, try_conda_as_backup=False):
    """Install Ipopt and possibly other solvers.

    If running on Colab, this will install Ipopt, k_aug, and other COIN-OR
    solvers via idaes get-extensions.

    Arguments:
        verbose: bool, if True, display console output from idaes get-extensions and conda
        try_conda_as_backup: bool, if True, install ipopt via conda if idaes get-extensions fails
    """

    # Check if Ipopt (solver) is available. If not, install it.
    if not package_available("ipopt"):
        print("Running idaes get-extensions to install Ipopt, k_aug, and more...")
        v = subprocess.run(
            ["idaes", "get-extensions"], check=True, capture_output=True, text=True
        )
        if verbose:
            print(v.stdout)
            print(v.stderr)
        _update_path()
        print("Checking solver versions:")
        _print_solver_versions()

    # Check again if Ipopt is available. If not, try conda
    if try_conda_as_backup and not package_available("ipopt"):
        print("Installing Ipopt via conda...")
        v = subprocess.run(
            [sys.executable, "-m", "conda", "install", "-c", "conda-forge", "ipopt"],
            check=True,
            capture_output=True,
            text=True,
        )
        if verbose:
            print(v.stdout)
            print(v.stderr)
        print("Checking ipopt version:")
        _print_single_solver_version("ipopt")

def install_glpk():
    """Install GLPK via apt-get on Colab

    Deprecated: HiGHS (see install_highs) is the course default LP/MILP solver.
    This function is kept for the handful of older contributed notebooks that
    still call glpsol.
    """
    if not package_available("glpk") and on_colab():
        print("Installing glpk via apt-get...")
        os.system('apt-get install -y -qq glpk-utils')


def install_highs(verbose=False):
    """Installs HiGHS via pip

    HiGHS is the default LP/MILP solver for this course. It is distributed as
    the Python package `highspy` and is used from Pyomo via
    `pyo.SolverFactory('appsi_highs')`.

    Argument:
        verbose: bool, if True, display console output from pip install

    """

    try:
        import highspy

        print("highspy was found! No need to install.")
    except ImportError:
        print("Installing highspy via pip...")
        v = subprocess.run(
            [sys.executable, "-m", "pip", "install", "-q", "highspy"],
            check=True,
            capture_output=True,
            text=True,
        )
        if verbose:
            print(v.stdout)
            print(v.stderr)
        print("highspy was successfully installed")


def easy_install(verbose=False):
    """Install IDAES and solvers in one step"""

    install_idaes(verbose=verbose)
    install_ipopt(verbose=verbose, try_conda_as_backup=True)
    install_highs(verbose=verbose)

def _update_path():
    """Add idaes executables to PATH"""
    if not re.search(re.escape("/root/.idaes/bin/"), os.environ["PATH"]):
        os.environ["PATH"] = "/root/.idaes/bin/:" + os.environ["PATH"]


def _print_single_solver_version(solvername):
    """Print the version for a single solver
    Arg:
        solvername: solver executable name (string)
    """
    v = subprocess.run([solvername, "-v"], check=True, capture_output=True, text=True)
    print(v.stdout)
    print(v.stderr)


def _print_solver_versions():
    """Print versions of solvers in idaes get-extensions

    This is the primary check that solvers installed correctly and are callable
    """

    # This does not work for cbc and clp; calling --version with these solvers,
    # enters their scripting language mode.
    for s in ["ipopt", "k_aug", "couenne", "bonmin", "ipopt_l1", "dot_sens"]:
        _print_single_solver_version(s)

