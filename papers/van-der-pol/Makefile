PYTHON ?= python3
LATEXMK ?= latexmk

.PHONY: all figure main supplement clean

all: main supplement

figure: figures/positive_two_end_geometry.pdf figures/computed_stationary_profiles.pdf

figures/positive_two_end_geometry.pdf: figures/positive_two_end_geometry.py
	$(PYTHON) figures/positive_two_end_geometry.py

figures/computed_stationary_profiles.pdf: figures/computed_stationary_profiles.py ../../numerics/results/vdp_v1_v7/v7_periodic.npz ../../numerics/results/vdp_v1_v7/v7_multipulses.npz
	$(PYTHON) figures/computed_stationary_profiles.py

main: figure
	$(LATEXMK) -pdf -interaction=nonstopmode -halt-on-error main.tex

supplement:
	$(LATEXMK) -pdf -interaction=nonstopmode -halt-on-error supplement.tex

clean:
	$(LATEXMK) -C main.tex
	$(LATEXMK) -C supplement.tex
