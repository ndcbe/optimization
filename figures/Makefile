# Render course figures to web + print assets. TWO source languages, ONE
# output directory, one command.
#
#   make          rebuild any figure whose source changed
#   make all      same
#   make check    verify the matplotlib house style survives greyscale printing
#   make clean    remove intermediates (keeps committed output)
#   make list     show the figures this Makefile knows about
#
# Source:  figures/tikz/<name>.tex      a bare tikzpicture environment
#          figures/plots/<name>.py      a make_figure() -> Figure; see render.py
#          a NOTEBOOK CELL tagged `figure:<name>`, re-rendered from the
#          committed figures/results/<name>.json -- see render_from_notebook.py.
#          THREE source languages now. A figure that a notebook generates has
#          the notebook as its only source (Prof. Dowling, 2026-08-24: "If the
#          figure is generated in a notebook ... we should use the version from
#          the notebook in the lecture notes"); `make` re-renders it from the
#          archive so a style change does not need Pyomo or a solver binary.
# Output:  ../media/figures/<name>.png  referenced by the notebooks (300 dpi)
#          ../media/figures/<name>.svg  vector, TikZ diagrams
#          ../media/figures/<name>.pdf  vector, matplotlib plots, for the handouts
#
# Rendered output is COMMITTED. Neither the website build nor a student
# cloning the repo needs a TeX installation. Only edit-and-regenerate needs it.
#
# The same figures/tikz/<name>.tex files are \input directly by the LaTeX
# lecture handouts in ../../optimization-private/lecture-notes, so a diagram is
# authored once and appears identically on the website and in the course pack.
#
# Requires: pdflatex (TeX Live), pdftocairo (poppler).

TIKZ_DIR  := tikz
PLOT_DIR  := plots
BUILD_DIR := build
OUT_DIR   := ../media/figures

SOURCES := $(wildcard $(TIKZ_DIR)/*.tex)
NAMES   := $(notdir $(basename $(SOURCES)))
PNGS    := $(addprefix $(OUT_DIR)/,$(addsuffix .png,$(NAMES)))
SVGS    := $(addprefix $(OUT_DIR)/,$(addsuffix .svg,$(NAMES)))

# plots/_*.py are shared helpers (see plots/_house.py), not figures.
PSOURCES  := $(filter-out $(PLOT_DIR)/_%,$(wildcard $(PLOT_DIR)/*.py))
PNAMES    := $(notdir $(basename $(PSOURCES)))
PLOT_PNGS := $(addprefix $(OUT_DIR)/,$(addsuffix .png,$(PNAMES)))
PLOT_PDFS := $(addprefix $(OUT_DIR)/,$(addsuffix .pdf,$(PNAMES)))


# 300 dpi keeps small text legible when a diagram is scaled up in a notebook.
PNG_DPI := 300

PYTHON := python3
# Figures whose source is a notebook cell tagged `figure:<name>`. The list is
# asked for rather than written down, so tagging a cell is the ONLY step needed
# to put a figure in the build -- a registry file here would be one more thing
# to forget to update. Every notebook is a prerequisite because make cannot
# know which one carries which tag; re-rendering is deterministic and takes
# seconds, so a spurious rebuild costs nothing and changes no committed bytes.
NB_NAMES  := $(shell $(PYTHON) render_from_notebook.py --list 2>/dev/null)
NB_SOURCES := $(wildcard ../notebooks/*-dev/*.ipynb)
NB_PNGS   := $(addprefix $(OUT_DIR)/,$(addsuffix .png,$(NB_NAMES)))
NB_PDFS   := $(addprefix $(OUT_DIR)/,$(addsuffix .pdf,$(NB_NAMES)))

.PHONY: all clean list check names
all: names $(PNGS) $(SVGS) $(PLOT_PNGS) $(PLOT_PDFS) $(NB_PNGS) $(NB_PDFS)

# Both source languages write <name>.png into the SAME OUT_DIR, which is what
# lets a notebook reference media/figures/<name>.png without caring how it was
# drawn. The cost is that tikz/foo.tex and plots/foo.py would silently
# overwrite each other's PNG, with whichever ran last winning and no error
# anywhere. Fail loudly instead. This is cheap and runs before every build.
names:
	@dupes=$$(printf '%s\n' $(NAMES) $(PNAMES) $(NB_NAMES) | sort | uniq -d); \
	if [ -n "$$dupes" ]; then \
	  echo "ERROR: one figure name claimed by more than one source:"; \
	  for d in $$dupes; do echo "  $$d  (tikz/$$d.tex, plots/$$d.py, or a cell tagged figure:$$d)"; done; \
	  echo "All three write $(OUT_DIR)/<name>.png. Rename one, or -- if a"; \
	  echo "notebook has taken over a plots/<name>.py -- delete the script."; \
	  exit 1; \
	fi

# Gate on the greyscale floor. Exits non-zero on failure, so this is CI-safe.
# See README.md; the style file itself is dowling.mplstyle in this directory.
check:
	cd .. && $(PYTHON) scripts/check_greyscale.py --style figures/dowling.mplstyle -n 4
	cd .. && $(PYTHON) scripts/check_greyscale.py media/figures
	cd .. && $(PYTHON) scripts/check_results_fresh.py

list:
	@echo "TikZ diagrams (tikz/*.tex -> .png + .svg):"; \
	for n in $(NAMES); do echo "  $$n"; done; \
	echo "matplotlib plots (plots/*.py -> .png + .pdf):"; \
	for n in $(PNAMES); do echo "  $$n"; done; \
	echo "notebook figures (cell tagged figure:<name> + results/<name>.json):"; \
	for n in $(NB_NAMES); do echo "  $$n"; done

# Wrap a bare tikzpicture in a standalone document. `border` keeps the
# rendered image from being cropped flush against the drawing.
$(BUILD_DIR)/%.tex: $(TIKZ_DIR)/%.tex preamble.tex
	@mkdir -p $(BUILD_DIR)
	@printf '%s\n' \
	  '\documentclass[border=4pt]{standalone}' \
	  '\input{../preamble}' \
	  '\begin{document}' \
	  '\input{../$<}' \
	  '\end{document}' > $@

$(BUILD_DIR)/%.pdf: $(BUILD_DIR)/%.tex
	cd $(BUILD_DIR) && pdflatex -interaction=nonstopmode -halt-on-error $*.tex >/dev/null

$(OUT_DIR)/%.png: $(BUILD_DIR)/%.pdf
	@mkdir -p $(OUT_DIR)
	pdftocairo -png -r $(PNG_DPI) -singlefile $< $(basename $@)

$(OUT_DIR)/%.svg: $(BUILD_DIR)/%.pdf
	@mkdir -p $(OUT_DIR)
	pdftocairo -svg $< $@

# One run of render.py writes BOTH the .png and the .pdf. Expressing that as
# two pattern rules would run the script twice; grouped targets (`&:`) would
# say it properly but need GNU make 4.3, and macOS ships 3.81. So the real work
# hangs off a stamp file and the two outputs just depend on the stamp.
$(BUILD_DIR)/%.plotstamp: $(PLOT_DIR)/%.py dowling.mplstyle $(PLOT_DIR)/_house.py render.py
	@mkdir -p $(BUILD_DIR) $(OUT_DIR)
	$(PYTHON) render.py $< $(OUT_DIR)
	@touch $@

$(OUT_DIR)/%.png: $(BUILD_DIR)/%.plotstamp ;
$(OUT_DIR)/%.pdf: $(BUILD_DIR)/%.plotstamp ;

# Notebook-sourced figures, same stamp trick. The prerequisite is the ARCHIVE,
# not the notebook's solve: re-rendering here must never need Pyomo or a solver
# binary, which is the promise the whole directory makes. If the model in the
# notebook changed and the archive did not, check_results_fresh.py says so --
# make cannot see that, and must not pretend to.
$(BUILD_DIR)/%.nbstamp: results/%.json render_from_notebook.py dowling.mplstyle $(NB_SOURCES)
	@mkdir -p $(BUILD_DIR) $(OUT_DIR)
	$(PYTHON) render_from_notebook.py --out-dir $(OUT_DIR) $*
	@touch $@

$(OUT_DIR)/%.png: $(BUILD_DIR)/%.nbstamp ;
$(OUT_DIR)/%.pdf: $(BUILD_DIR)/%.nbstamp ;

clean:
	rm -rf $(BUILD_DIR)

.PRECIOUS: $(BUILD_DIR)/%.pdf $(BUILD_DIR)/%.tex $(BUILD_DIR)/%.plotstamp $(BUILD_DIR)/%.nbstamp
