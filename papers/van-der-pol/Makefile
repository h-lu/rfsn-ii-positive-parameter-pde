PYTHON ?= python3
LATEXMK ?= latexmk

.PHONY: all figure main supplement clean

all: main supplement

figure: figures/positive_two_end_geometry.pdf

figures/positive_two_end_geometry.pdf: figures/positive_two_end_geometry.py
	$(PYTHON) figures/positive_two_end_geometry.py

main: figure
	$(LATEXMK) -pdf -interaction=nonstopmode -halt-on-error main.tex

supplement:
	$(LATEXMK) -pdf -interaction=nonstopmode -halt-on-error supplement.tex

clean:
	$(LATEXMK) -C main.tex
	$(LATEXMK) -C supplement.tex
