SHELL=/bin/sh

# LaTeX options
TEX_COMPILER=pdflatex
TEX_OPTIONS=--interaction=nonstopmode
TEX=$(TEX_COMPILER) $(TEX_OPTIONS)

# Text to Tex options
PYTHON_CMD_OPTIONS=--dont-escape-content #--name-as-header
PYTHON_CMD=python text_to_tex.py $(PYTHON_CMD_OPTIONS)

#----------------------------------------
# Build the lists of dependencies
INPUT_DIR=./csv/
TEX_DIR=./tex/

# The list of all CSV files that are inputs to text_to_tex.py
ALL_CSV_FILES=$(wildcard $(INPUT_DIR)*.csv)

# The list of all required tex files to build the document.
ALL_TEX_FILES=$(addprefix $(TEX_DIR),$(addsuffix .tex, $(basename $(notdir $(ALL_CSV_FILES)))))
ALL_TEX_FILES+=$(wildcard *.tex)

.SILENT:
.IGNORE:

all: example.pdf preview

# Install the script as an executable in ~/.local/bin
install: text_to_tex.py
	echo Installing to ~/.local/bin/
	cp ./text_to_tex.py ~/.local/bin/
	chmod 744 ~/.local/bin/text_to_tex.py

# Pattern rule to build tex/*.tex from csv/*.csv
$(TEX_DIR)%.tex: $(INPUT_DIR)%.csv
	mkdir -p $(TEX_DIR)
	echo "$^ --> $@"
	$(PYTHON_CMD) --input $^ --output $@

# Pattern rule to build *.pdf from *.tex and all generated tex files
%.pdf: $(addsuffix .tex, $(basename $(@))) $(ALL_TEX_FILES)
# Compile three times since this seems to be required for the parchment background to render correctly
	$(TEX) $(addsuffix .tex, $(basename $(@)))
	$(TEX) $(addsuffix .tex, $(basename $(@)))
	$(TEX) $(addsuffix .tex, $(basename $(@)))

# Convenience rule to build all tex files at once without compiling the PDF
tex: $(ALL_TEX_FILES)

# Generate a preview image for the README
preview: example.pdf
	pdftoppm -jpeg -rx 120 -ry 120 -f 1 -l 1 example.pdf preview
	mv preview-1.jpg preview.jpg

.PHONY: clean
clean:
	echo Cleaning ...
	rm -rf *.gz *.aux *.log *.out *.bbl *.blg *.bak *.bcf *.xml *.toc *.lot *.lof tex/
	echo ... done