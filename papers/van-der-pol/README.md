# Van der Pol companion manuscript

This directory contains the reader-facing companion to the detailed V1--V7
proof archive in `../../van-der-pol/` and `../../theory/`.

Build both PDFs with

```bash
make
```

The principal source is `main.tex`.  `supplement.tex` contains provenance,
frozen-source hashes, the proof-location crosswalk, and replay information.
The manuscript has two reproducible figures:

- `figures/positive_two_end_geometry.py` generates the explanatory schematic,
  which is not numerical evidence;
- `figures/computed_stationary_profiles.py` reads the archived V7 NPZ arrays
  and generates the `COMPUTED/E1`, non-claim-bearing physical-profile panel.

Regenerate both figures and compile the manuscript with `make main`; use
`make figure` for the figures alone.

Rendered artifacts:

- [main paper](../../output/pdf/van-der-pol-positive-two-end-spatial-dynamics.pdf);
- [provenance supplement](../../output/pdf/van-der-pol-positive-two-end-spatial-dynamics-supplement.pdf);
- [exact frozen input snapshot](../../frozen-imports/rfsn-ii-d54add098545063d5efe8f1d6f062d4cfc116a0d/README.md).

The immutable publication version is
[vdp-companion-v1](https://github.com/h-lu/rfsn-ii-positive-parameter-pde/releases/tag/vdp-companion-v1).

The paper is conditional on the frozen RFSN-II inputs stated as Hypothesis H.
The current manuscript also proves the exact V10 exclusion of a classical
stationary Turing onset and the V11 bridge from a real positive temporal
eigenvalue to nonlinear orbital instability.  The A2 and `pulse_1`
applications of V11 retain local, non-claim-bearing status pending independent
replay.  The paper does not claim temporal stability, dynamic pattern
selection, canard identification, an explicit interval-validated positive
parameter box, or experimental realization.
