# Positive-parameter PDE applications of the RFSN-II theory

This private repository develops two model-level applications of the
return--first-exit theory proved for the RFSN-II Hamiltonian core:

1. a positive-diffusion localized stationary pattern for the Brusselator;
2. a positive-parameter two-end exact-action theorem for the van der Pol
   reaction--diffusion system.

The projects are deliberately separate from the flagship manuscript, which is
a read-only, revision-pinned source for this repository.  Missing abstract
lemmas or strengthened formulations needed by the applications are developed
locally in [`theory/`](theory/README.md).  They may support this repository's
theorems, but they do not edit or alter the claims of the flagship paper.

## Present status

The Brusselator localized-profile theorem is **Proved** in
[Theorem B](brusselator/LOCALIZED_PROFILE_PROOF.md), using the
[frozen imported transverse core result](brusselator/CORE_HOMOCLINIC_IMPORT.md).
For the van der Pol track, the exact model bridge is **Derived** and the
compact central continuation theorem V2 is **Proved** in
[CENTRAL_CONTINUATION.md](van-der-pol/CENTRAL_CONTINUATION.md), using the
strictly bounded [frozen core import](van-der-pol/CENTRAL_CORE_IMPORT.md).
The genuine positive-parameter pole, its uniform source window, and its
action finite part are **Proved** in
[Theorem V3](van-der-pol/POSITIVE_POLE_FINITE_PART.md).  The
positive-parameter outer algebraic tail, its locally maximal future-staying
hypersurface, and intrinsic third-order bunching are **Proved** in
[Theorem V4](van-der-pol/OUTER_FUTURE_STAYING.md).  The attachment of that
tail through \(K_1\) to the central algebraic-directed sheet, including its
nonzero exchange coefficient and moving-cut covariance, is **Proved** in
[Theorem V5](van-der-pol/CENTRAL_OUTER_MATCHING.md).  The outer algebraic
physical-length and action finite parts, with mixed two-jets and exact
finite-branch composition, are **Proved** in
[Theorem V5A](van-der-pol/OUTER_ALGEBRAIC_FINITE_PART.md).  Every later
theorem-sized claim retains the status in the
[claim register](CLAIM_REGISTER.md).

The analytic van der Pol track is now closed on a nonempty compact positive
annular parameter box.  [Theorems V6--V7](van-der-pol/TWO_END_RETURN_EXIT_AND_PDE.md)
prove the exhaustive physical high-winding return--first-exit relation, both
compatible finite parts, exact branch composition, and the resulting
periodic, multipulse, and aperiodic stationary spatial PDE patterns.  The
relative \(K_1\) NHIM interface and finite marked-atlas descent are proved
locally in [theory/](theory/README.md).  Raw winding labels remain chartwise;
the physical relation, profiles, periods, and closed actions agree on
overlaps.  Their reusable
high-winding and coding inputs are isolated in a strictly bounded
[frozen modular import](van-der-pol/RETURN_EXIT_CODING_IMPORT.md); neither
positive end is imported from the flagship model.

| Workstream | First rigorous target | Structure retained | Main obstruction |
|---|---|---|---|
| [Brusselator](brusselator/README.md) | A positive-concentration, symmetric, localized stationary solution for all sufficiently small positive diffusion | Reversibility and the transverse core homoclinic | Localized-branch tail continuation and positivity are discharged in Theorem B; exact Hamiltonian action is unavailable, and temporal stability and multipulses remain separate questions |
| [van der Pol](van-der-pol/README.md) | A positive-parameter exhaustive high-winding return/first-exit theorem with two action finite parts | Exact Hamiltonian structure, selected transverse homoclinic, clean whole-cell first-event stratification, two genuine positive-parameter end finite parts, and stationary spatial coding | Analytic obligations are discharged in V6--V7; outward-rounded validation of a preselected explicit numerical box remains the separate deferred task #7 |

The precise scientific boundary, proof order, fallback results, and stopping
conditions are fixed in [RESEARCH_CONTRACT.md](RESEARCH_CONTRACT.md).

## Evidence language

Every claim is assigned one of the following ordinary descriptions:

- **Proposed**: a theorem or construction to be proved;
- **Derived**: a symbolic consequence checked from explicitly stated equations;
- **Numerically observed**: supported by non-rigorous computation only;
- **Computer-assisted**: supported by an archived, replayable rigorous computation;
- **Proved**: supported by a complete mathematical proof in this repository;
- **Imported**: used from a precisely cited external theorem.

Numerical continuation never changes a mathematical statement from Proposed to
Proved.  PDE temporal stability and experimental realization are not completion
criteria for either first-stage project.

## Numerical atlas

The [reproducible theorem-to-PDE atlas](numerics/README.md) now supplies
**Numerically observed** positive-parameter profiles, scaling-collapse tests,
zero-energy reversible periodic orbits, a high-winding period-law test, and
domain-convergence diagnostics.  Every computed figure is labelled
`COMPUTED/E1` or `COMPUTED/QA`; the Turing/canard context figure explicitly
separates exact formulas, computed samples, and schematic geometry.

The atlas is explanatory evidence only.  In particular, it does not replace
task #7, certify an explicit positive theorem box, prove temporal stability,
or calibrate an experiment.

A second, van der Pol-specific master run follows the paper's full V1--V7
order:

```bash
python3 numerics/run_vdp_master.py
```

It writes the nine editable figures, PNG previews, machine-readable stage
diagnostics, profile arrays, QA summary, and provenance manifest to
[`numerics/results/vdp_v1_v7/`](numerics/results/vdp_v1_v7/).  Its scope and
interpretation are fixed by the
[coverage matrix](numerics/VAN_DER_POL_COVERAGE_MATRIX.md),
[numerical report](numerics/VAN_DER_POL_NUMERICAL_REPORT.md), and
[figure contracts](numerics/VAN_DER_POL_FIGURE_CONTRACTS.md).

Configuration v4 adds a stronger, still non-rigorous candidate layer.  It now
samples a finite-horizon nonlinear-\(W^u\) source window to the V3 gate and
continues one representative on the same physical orbit into the pole chart;
solves a coupled nonlinear-\(W^u\)--central--resolved-\(K_1\)--finite-horizon
outer V4/V5 candidate, together with a frozen 161-point independent
\(\Gamma(\beta)\) grid and three terminal horizons; evaluates V5A same-\(Q\)
finite-cut subtraction on that saved outer
leg; and records complete B1 and A2 finite returns with augmented physical
length and action.  The generated Issue #7 schema-v2 contract binds the
configuration and direct generator sources as well as the candidate data, but
remains `claim_bearing: false` with `final_status: NOT_RUN`.

The master run still does not numerically certify the paper's global and
uniform objects.  The actual infinite V4 future-staying graph, uniform V5
tube, adjoint/exchange and uniqueness statements, parameter jets, exhaustive
V6 cells and cross forms for all windings, and every outward-rounded interval
obligation remain unresolved.  The computed V7 periodic and multipulse
stationary profiles are not assigned proved theorem-edge itineraries and do
not construct a bi-infinite aperiodic orbit.  These explicit numerical
boundaries neither weaken the analytic V1--V7 theorems nor establish their
temporal stability.

### Temporal-dynamics, Turing, and canard prescreen

A separate [dynamics screening report](numerics/VDP_DYNAMICS_SCREENING_REPORT.md)
now distinguishes one exact conclusion from two numerical diagnostics.  The
homogeneous Fourier symbol gives an exact algebraic exclusion of the
**classical stationary Turing mechanism** for this PDE: temporal stability of
the homogeneous state requires \(f'(a)>0\), whereas a positive-wavenumber
stationary zero eigenvalue requires
\(f'(a)\leq-2r^2\sqrt{\epsilon}<0\).  This does not exclude finite-wavenumber
growth when the homogeneous mode is already unstable, and it does not connect
the V7 profiles to a nonlinear local bifurcation.

At the current sample, all five saved periodic profiles and all four saved
multipulse profiles have positive-growth **candidates** in the computed
Bloch/finite-window spectra.  These remain `COMPUTED/E1`: they are evidence
against prioritizing a stability proof at this parameter, not a complete
spectral or nonlinear-instability theorem.  The saved profiles cross the
positive fold and the singular reduction is FSN-II-degenerate there, but no
finite-parameter slow-manifold intersection has been computed; no canard is
identified.

For Issue #7, the box

\[
 [0.04,0.08]\times[-0.25,0.25]\times[0.8,1.2]
\]

in \((r,a_2,\epsilon)\) is now formally frozen as
`vdp-positive-box-v1`, before the first outward-rounded run.  It is an input
to the existence/coding validation, not a temporal-stability box.  The first
local phase-1 kernel now passes every implemented integrity and mathematical
obligation on this box; its aggregate status remains `INCONCLUSIVE` and
non-claim-bearing because the required independent replay and later stages
are still pending.  The subsequent P2a kernel also passes its exact moving
frame, isolating-block/difference-cone, and true coarse local-graph
subobligations on the full connected bridge
\([0,0.08]\times[-0.25,0.25]\times[0.8,1.2]\).  It certifies the complete
radius-`.01` local source disk.  The clean P2b0 kernel now also regenerates
the frozen exact H10 center byte-for-byte and proves uniform true-graph tubes

\[
 \lVert H_\mu-H_{10}\rVert_2\le5\times10^{-6},\qquad
 \lVert DH_\mu-DH_{10}\rVert_F\le3\times10^{-4}
\]

on that bridge.  Its integrity and mathematical statuses pass locally, while
the aggregate remains `INCONCLUSIVE` and non-claim-bearing because independent
replay is still 1/2.  The subsequent clean P2b mixed-jet kernel now also
passes the true-graph state-(C^2/C^3) bounds, the complete rectangular
state/parameter jets, and the weight-(1/4) half-orbit bounds in moving and
physical coordinates.  Consequently its local parent obligations
`V2.WU.JETS` and `V2.WU_GRAPH` pass.  Its aggregate remains `INCONCLUSIVE` and
non-claim-bearing solely because independent replay remains 1/2.  The
subsequent clean P2bK kernel also passes its locked 56-identity exact audit,
normalized Riesz/Kato transport, physical frame change, complete \(C^2\)
parameter lift, degree-one radius-`.01` true source circle, and the nine-jet
total-order-three source triangle.  Its aggregate likewise remains
`INCONCLUSIVE` and non-claim-bearing solely because independent replay is
1/2.  P2c--P5 remain unimplemented.

## Repository map

- [Frozen theory baseline and local amendments](theory/README.md)
- [Brusselator programme](brusselator/README.md)
- [van der Pol programme](van-der-pol/README.md)
- [Research contract](RESEARCH_CONTRACT.md)
- [Claim register](CLAIM_REGISTER.md)
- [Proof-seam audit](proof-audit/SEAM_AUDIT_2026-08-27.md)
- [Primary sources](references/PRIMARY_SOURCES.md)
- [Numerical atlas and reproduction instructions](numerics/README.md)
- [Numerical results and interpretation](numerics/NUMERICAL_REPORT.md)
- [Van der Pol V1--V7 numerical coverage](numerics/VAN_DER_POL_COVERAGE_MATRIX.md)
- [Van der Pol V1--V7 numerical report](numerics/VAN_DER_POL_NUMERICAL_REPORT.md)
- [Van der Pol V1--V7 figure contracts](numerics/VAN_DER_POL_FIGURE_CONTRACTS.md)
- [Van der Pol dynamics screening report](numerics/VDP_DYNAMICS_SCREENING_REPORT.md)
- [Van der Pol dynamics figure contracts](numerics/VDP_DYNAMICS_FIGURE_CONTRACTS.md)
- [Issue #7 candidate-contract workspace](validation/README.md)
- [Issue #7 staged rigorous-validation lane](validation/rigorous/README.md)
- [Issue #7 phase-1 local report](validation/rigorous/PHASE1_REPORT.md)
- [Issue #7 P2a local-graph report](validation/rigorous/P2A_REPORT.md)
- [Issue #7 P2b0 H10 C0/C1 report](validation/rigorous/P2B0_REPORT.md)
- [Issue #7 P2b mixed-jet report](validation/rigorous/P2B_JETS_REPORT.md)
- [Issue #7 P2bK normalized Kato phase report](validation/rigorous/P2B_KATO_REPORT.md)

## Initial work queue

- [#1: Brusselator localized stationary profile](https://github.com/h-lu/rfsn-ii-positive-parameter-pde/issues/1)
- [#2: van der Pol Hamiltonian bridge and compact persistence](https://github.com/h-lu/rfsn-ii-positive-parameter-pde/issues/2)
- [#3: positive-parameter pole and action finite part](https://github.com/h-lu/rfsn-ii-positive-parameter-pde/issues/3)
- [#4: central--outer matching theorem](https://github.com/h-lu/rfsn-ii-positive-parameter-pde/issues/4), the decisive mathematical go/no-go task
- [#5: outer algebraic action finite part](https://github.com/h-lu/rfsn-ii-positive-parameter-pde/issues/5)
- [#6: exhaustive two-end theorem](https://github.com/h-lu/rfsn-ii-positive-parameter-pde/issues/6)
- [#7: rigorous validation](https://github.com/h-lu/rfsn-ii-positive-parameter-pde/issues/7), with phase 1, P2a, P2b0, P2b mixed jets, and the P2bK normalized Kato/true-source interface passing locally; P2c--P5 and independent replay remain pending

The source theory remains in
[`h-lu/reversible-rfsn-ii-waves`](https://github.com/h-lu/reversible-rfsn-ii-waves).
This repository imports only explicitly cited results from it; it does not copy
or silently strengthen them.
