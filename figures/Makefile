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

.PHONY: all clean list check names
all: names $(PNGS) $(SVGS) $(PLOT_PNGS) $(PLOT_PDFS)

# Both source languages write <name>.png into the SAME OUT_DIR, which is what
# lets a notebook reference media/figures/<name>.png without caring how it was
# drawn. The cost is that tikz/foo.tex and plots/foo.py would silently
# overwrite each other's PNG, with whichever ran last winning and no error
# anywhere. Fail loudly instead. This is cheap and runs before every build.
names:
	@dupes=$$(printf '%s\n' $(NAMES) $(PNAMES) | sort | uniq -d); \
	if [ -n "$$dupes" ]; then \
	  echo "ERROR: same figure name in both tikz/ and plots/:"; \
	  for d in $$dupes; do echo "  $$d  (tikz/$$d.tex and plots/$$d.py)"; done; \
	  echo "Both write $(OUT_DIR)/<name>.png. Rename one."; \
	  exit 1; \
	fi

# Gate on the greyscale floor. Exits non-zero on failure, so this is CI-safe.
# See README.md; the style file itself is dowling.mplstyle in this directory.
check:
	cd .. && $(PYTHON) scripts/check_greyscale.py --style figures/dowling.mplstyle -n 4
	cd .. && $(PYTHON) scripts/check_greyscale.py media/figures

list:
	@echo "TikZ diagrams (tikz/*.tex -> .png + .svg):"; \
	for n in $(NAMES); do echo "  $$n"; done; \
	echo "matplotlib plots (plots/*.py -> .png + .pdf):"; \
	for n in $(PNAMES); do echo "  $$n"; done

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

clean:
	rm -rf $(BUILD_DIR)

.PRECIOUS: $(BUILD_DIR)/%.pdf $(BUILD_DIR)/%.tex $(BUILD_DIR)/%.plotstamp
