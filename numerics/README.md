# Numerical theorem-to-PDE atlas

**Evidence status: COMPUTED/E1, non-rigorous floating-point numerics.**  This
directory illustrates and stress-tests the analytic claims.  It is not the
deferred task #7 interval validation, and none of its concrete parameter
samples is claimed to lie in an explicitly certified positive theorem box.

## What is computed

1. The universal RFSN-II core homoclinic is reconstructed from the midpoint
   of the immutable certified root

   \[
   \phi\in[5.8615055856447817,5.8615055856450482],\qquad
   T\in[9.63744206789581,9.637442067897151].
   \]

   The copied floating source state is the midpoint evaluation of the frozen
   degree-ten unstable graph.  Its original certificate is
   `reversible-rfsn-ii-waves/validation/universal-core-symmetric-homoclinic`;
   the present code has no runtime dependency on that repository.

2. A symmetric half-line collocation BVP continues that orbit in the exact
   scaled Brusselator and van der Pol vector fields.  At the symmetry point it
   imposes \(P=Q=0\); at the far endpoint it projects onto the two-dimensional
   linear stable space.  Continuation is performed in \(r=d^{1/4}\).

3. For van der Pol at \((r,a_2,\epsilon)=(0.08,0,1)\), several zero-energy
   initial points on \(\operatorname{Fix}\mathcal R\) are bracketed.  A scalar
   transverse-event shooting condition selects the next simultaneous
   \(P=Q=0\) hit: family A uses a \(Q=0\) event and \(P\) residual, while
   family B uses a \(P=0\) event and \(Q\) residual because its target makes
   \(Q=0\) nontransverse.  Reflection produces the full periodic orbit.  The
   labels `A` and `B` distinguish two numerically sampled reversible families;
   their decreasing initial offsets and increasing periods are consistent with
   the V7 accumulation law.  `relative_winding` is an offset within a family,
   not an absolute V7 graph label.

## Van der Pol V1--V7 master atlas

The model-specific master run follows the analytic order V1, V2, V3, V4,
V5, V5A, V6, and V7 at the frozen exploratory parameters in
[`config/vdp_v1_v7.json`](config/vdp_v1_v7.json).  It computes exact symbolic
checks, finite parameter slices and local-passage experiments, and the
following configuration-v4 candidate objects:

- a finite-horizon nonlinear-\(W^u\) source window and one connected physical
  source--gate--pole orbit, including orbit-fitted pole labels and a
  source-anchored Laurent--log finite-cut action ladder;
- one coupled nonlinear-\(W^u\)--central--resolved-\(K_1\)--finite-horizon
  outer BVP candidate, an independent 161-point \(\Gamma(\beta)\) grid with
  three terminal horizons, plus a V5A same-\(Q\) subtraction using that saved
  outer leg;
- a finite numerical first-event atlas and complete B1/A2 return records whose
  two segments share one physical IVP and carry augmented physical length and
  action; and
- actual full-ODE periodic and symmetric multipulse stationary profiles,
  together with a hash-bound, non-claim-bearing Issue #7 replay contract.

It then renders nine contract-driven figures without promoting any candidate
to a proof or interval certificate.

```bash
python3 numerics/run_vdp_master.py
```

All machine-readable diagnostics, compressed profile arrays, editable
PDF/SVG figures, PNG previews, QA summary, and provenance
manifest are written to
[`results/vdp_v1_v7/`](results/vdp_v1_v7/).  The interpretation and stopping
rules are recorded separately in:

- [V1--V7 numerical coverage matrix](VAN_DER_POL_COVERAGE_MATRIX.md);
- [V1--V7 numerical report](VAN_DER_POL_NUMERICAL_REPORT.md);
- [V1--V7 figure contracts](VAN_DER_POL_FIGURE_CONTRACTS.md).

The candidate layer closes several former *finite-computation* seams: V3 now
uses a nonlinear-\(W^u\) source and the same orbit through the pole overlap;
V4/V5 now has a connected three-piece BVP and a finite-horizon same-section
root; V5A uses its actual saved outer leg at common \(Q\); and V6 now stores two
complete finite returns with opposite target transverse-sign proxies.  The
principal artifacts are
[`v3_pole.json`](results/vdp_v1_v7/v3_pole.json),
[`v4_v5_matched_candidate.json`](results/vdp_v1_v7/v4_v5_matched_candidate.json),
[`v4_v5_matched_candidate.npz`](results/vdp_v1_v7/v4_v5_matched_candidate.npz),
[`v6_complete_branches.npz`](results/vdp_v1_v7/v6_complete_branches.npz), and
[`v6_candidate_contract.json`](results/vdp_v1_v7/v6_candidate_contract.json).

At the frozen point, the connected V3 fit gives
\((Z_0,W_0,\kappa)\approx(-0.6664297671,-0.06889853233,
1.6524678712\times10^7)\), with global/local overlap about
\(6.4\times10^{-8}\).  Its source-anchored finite-cut subtraction is about
\(-7.45692005\), while the last-three-cut spread is still about
\(1.46\times10^{-2}\); the latter is displayed as finite-horizon sensitivity,
not suppressed.  The V5 candidate solves at phase approximately
\(5.75883888346\) and central flight time \(9.91261798229\), with interface
residual \(2.22\times10^{-16}\), independent same-section root residual
\(1.67\times10^{-13}\), and passing arrival margins.  Full precision and all
other diagnostics remain in the JSON files rather than in this overview.

The master atlas remains intentionally incomplete where the proved theorem is
uniform, infinite, exhaustive, or uniqueness-bearing.  It does not certify a
positive parameter box; construct the infinite V4 future-staying graph with
uniform normal/bunching bounds; compute the theorem's endpoint adjoint,
exchange and uniqueness mechanisms or parameter jets; prove exhaustive V6
cells, overlap descent, cross forms, or all-\(n\) bounds; or perform
outward-rounded validation.  The V7 periodic and multipulse profiles are
genuine stationary full-ODE profiles, but their theorem-edge words and a
nonperiodic bi-infinite numerical orbit are not resolved.  These are limits of
the numerical realization, not gaps in the proved analytic V1--V7 results.
The plotted phase/transverse coordinates are one exploratory local
presentation.  They neither construct the optional global marking T2G nor
compare the bounded winding recodings on overlaps of the analytic finite
marked atlas.

## Temporal dynamics, Turing, and canard prescreen

The follow-up screening run starts from the saved V7 profiles and keeps exact
algebra separate from floating-point spectral evidence:

```bash
python3 numerics/run_vdp_dynamics_screening.py
python3 numerics/check_vdp_dynamics_screening.py
```

The default pair is the official path: the runner refuses a dirty repository,
binds every source/input hash to its start commit, verifies the three V1--V7
NPZ inputs against the `vdp-v4-screening-baseline` Git blobs, and checks that
the census is unchanged after computation and rendering.  A temporary
development run must opt in with `--allow-dirty-source`; its result is marked
`DEVELOPMENT_ALLOW_DIRTY_SOURCE` and the official checker rejects it unless
`--allow-development-artifact` is also supplied explicitly.

Its homogeneous Fourier symbol exactly excludes the **classical stationary
Turing mechanism** for this van der Pol PDE.  A temporally stable homogeneous
state requires \(f'(a)>0\), while a stationary zero eigenvalue at \(k>0\)
requires \(f'(a)\leq-2r^2\sqrt{\epsilon}<0\).  This exact incompatibility does
not exclude a finite-wavenumber unstable band when \(k=0\) is already unstable,
nor does it construct or select a nonlinear patterned branch.

The numerical part finds positive-growth candidates for each of the five
saved periodic profiles in sampled Fourier--Bloch matrices and for each of the
one- through four-pulse profiles in finite-window matrices.  These results are
`COMPUTED/E1`, not a complete Bloch/Evans spectral theorem and not a nonlinear
instability theorem.  Short-time residual-subtracted perturbation evolution
checks the leading pulse modes but is not an unmodified full-PDE selection
experiment.

The same run records positive-fold passages and the FSN-II degeneracy of the
singular reduced problem.  It does not compute an intersection of the relevant
finite-parameter slow manifolds, so it does **not** identify a maximal canard.
Its proposed Issue #7 box

\[
 (r,a_2,\epsilon)\in
 [0.04,0.08]\times[-0.25,0.25]\times[0.8,1.2]
\]

is formally frozen for Issue #7.  The local phase-1 interval kernel passes the
implemented V1 and V2(1) obligations on the box, while V2 continuation through
V6 and independent replay remain pending.  Detailed numerical
values, stopping rules, and figure semantics are in the
[screening report](VDP_DYNAMICS_SCREENING_REPORT.md) and
[dynamics figure contracts](VDP_DYNAMICS_FIGURE_CONTRACTS.md).

## Reproduce

The current environment requires NumPy, SciPy, and Matplotlib.

```bash
python3 numerics/run_atlas.py
python3 numerics/check_convergence.py
python3 numerics/run_vdp_master.py
python3 numerics/check_vdp_master.py
python3 numerics/run_vdp_dynamics_screening.py
python3 numerics/check_vdp_dynamics_screening.py
python3 validation/check_candidate_contract.py numerics/results/vdp_v1_v7/v6_candidate_contract.json
python3 -m unittest numerics/test_numerics.py
python3 -m unittest discover -s numerics -p 'test_*.py'
python3 -m unittest discover -s validation -p 'test_*.py'
```

The command writes editable vector figures (`.pdf`, `.svg`), PNG previews,
compressed arrays, and a complete `manifest.json` to
`numerics/results/atlas/`.

The numerical outcomes and their theorem-level interpretation are summarized
in [NUMERICAL_REPORT.md](NUMERICAL_REPORT.md).

## Numerical gates

Every continued homoclinic records:

- normalized scaled-ODE collocation residual;
- boundary residual and tail norm;
- branch nontriviality;
- physical positivity for the Brusselator;
- Hamiltonian drift for van der Pol.

Every periodic orbit records the reversible closure residual, zero-energy
drift, a step-halved independent closure check, central and physical actions,
both central and physical periods, and the event component, event index, and
transversality used for branch selection.
Raw physical Brusselator residuals are not used as the main accuracy metric:
their small diffusion prefactors can conceal a poor scaled solution.

## Interpretation boundary

- Scaling collapse and fitted powers test the visible consequences of
  Theorem B; a plot does not prove the homoclinic branch.
- The van der Pol period slope tests the leading coefficient in V7 after an
  unknown integer offset is absorbed into a family-dependent intercept.
- The sampled Bloch and finite-window spectra supply non-rigorous positive
  growth candidates for all five periodic and all four multipulse profiles;
  they do not prove the complete spectrum or nonlinear instability.
- Classical stationary Turing onset is exactly excluded for this PDE, but the
  computation does not supply a nonlinear branch or an alternative dynamical
  pattern-selection mechanism.
- Fold passage and singular FSN-II degeneracy do not identify a canard.
  Saddle-focus winding and canard-organized outer geometry remain distinct
  mechanisms.
