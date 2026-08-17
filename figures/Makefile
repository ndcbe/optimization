# Render TikZ course diagrams to web assets.
#
#   make          rebuild any figure whose source changed
#   make all      same
#   make clean    remove intermediates (keeps committed output)
#   make list     show the figures this Makefile knows about
#
# Source:  figures/tikz/<name>.tex      a bare tikzpicture environment
# Output:  ../media/figures/<name>.png  referenced by the notebooks
#          ../media/figures/<name>.svg  higher quality, for future use
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
BUILD_DIR := build
OUT_DIR   := ../media/figures

SOURCES := $(wildcard $(TIKZ_DIR)/*.tex)
NAMES   := $(notdir $(basename $(SOURCES)))
PNGS    := $(addprefix $(OUT_DIR)/,$(addsuffix .png,$(NAMES)))
SVGS    := $(addprefix $(OUT_DIR)/,$(addsuffix .svg,$(NAMES)))

# 300 dpi keeps small text legible when a diagram is scaled up in a notebook.
PNG_DPI := 300

.PHONY: all clean list
all: $(PNGS) $(SVGS)

list:
	@echo "Figures:"; for n in $(NAMES); do echo "  $$n"; done

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

clean:
	rm -rf $(BUILD_DIR)

.PRECIOUS: $(BUILD_DIR)/%.pdf $(BUILD_DIR)/%.tex
