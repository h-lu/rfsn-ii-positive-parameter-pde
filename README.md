# Positive-parameter PDE applications of the RFSN-II theory

This repository develops two model-level applications of the
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
Its independently buildable companion manuscript is under
[`papers/brusselator/`](papers/brusselator/README.md), with the current
[rendered PDF](output/pdf/brusselator-localized-stationary-profiles.pdf).
The analytic continuation is proved relative to the stated computer-assisted
Core Lemma.  Its frozen source, certificate, environment, and replay manifest
are included in the
[public frozen snapshot](frozen-imports/rfsn-ii-d54add098545063d5efe8f1d6f062d4cfc116a0d/README.md);
this repository does not claim a new independent-machine replay.
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

Conditional on the named frozen inputs, the analytic van der Pol track is
closed on a nonempty compact positive annular parameter box.
[Theorems V6--V7](van-der-pol/TWO_END_RETURN_EXIT_AND_PDE.md)
prove the exhaustive physical high-winding return--first-exit relation, both
compatible finite parts, exact branch composition, and the resulting
periodic, multipulse, and aperiodic stationary spatial PDE patterns.  The
relative \(K_1\) NHIM interface and finite marked-atlas descent are proved
locally in [theory/](theory/README.md).  Raw winding labels remain chartwise;
the physical relation, profiles, periods, and closed actions agree on
overlaps.  The compact-family step is a conditional transfer of the frozen
fixed-system endpoint, matching, cross-form, and finite-event data, as stated
in the [publication proof audit](proof-audit/VDP_PUBLICATION_PROOF_AUDIT_2026-08-28.md).
Their reusable
high-winding and coding inputs are isolated in a strictly bounded
[frozen modular import](van-der-pol/RETURN_EXIT_CODING_IMPORT.md); neither
positive end is imported from the flagship model.

The reader-facing synthesis is the
[van der Pol companion manuscript](papers/van-der-pol/README.md):
[main PDF](output/pdf/van-der-pol-positive-two-end-spatial-dynamics.pdf) and
[provenance supplement](output/pdf/van-der-pol-positive-two-end-spatial-dynamics-supplement.pdf).
It states the theorem directly in the original PDE variables, compresses
V1--V7 into one proof spine, and moves hashes, replay instructions, and the
claim crosswalk to the supplement.

| Workstream | First rigorous target | Structure retained | Main obstruction |
|---|---|---|---|
| [Brusselator](brusselator/README.md) | A positive-concentration, symmetric, localized stationary solution for all sufficiently small positive diffusion | Reversibility and the transverse core homoclinic | Localized-branch tail continuation and positivity are discharged in Theorem B; exact Hamiltonian action is unavailable, and temporal stability and multipulses remain separate questions |
| [van der Pol](van-der-pol/README.md) | A positive-parameter exhaustive high-winding return/first-exit theorem with two action finite parts | Exact Hamiltonian structure, selected transverse homoclinic, clean whole-cell first-event stratification, two genuine positive-parameter end finite parts, and stationary spatial coding | Analytic obligations are discharged in V6--V7; outward-rounded validation of a preselected explicit numerical box is the active separate task #7 |

The precise scientific boundary, proof order, fallback results, and stopping
conditions are fixed in [RESEARCH_CONTRACT.md](RESEARCH_CONTRACT.md).

## Evidence language

Every claim is assigned one of the following ordinary descriptions:

- **Proposed**: a theorem or construction to be proved;
- **Derived**: a symbolic consequence checked from explicitly stated equations;
- **Numerically observed**: supported by non-rigorous computation only;
- **Local mathematical PASS**: supported by an outward-rounded computation on
  the locked current-machine toolchain, with independent replay still pending;
- **Computer-assisted**: supported by an archived, replayable rigorous computation;
- **Proved**: supported by a complete mathematical proof in this repository;
- **Imported**: used from a precisely cited external theorem.

Numerical continuation never changes a mathematical statement from Proposed to
Proved.  A local interval `PASS` is kept distinct from a claim-bearing,
independently replayed computer-assisted result.  PDE temporal stability and
experimental realization are not completion criteria for either first-stage
project.

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
Bloch/finite-window spectra.  Those broad screens remain `COMPUTED/E1`; only
the separately validated A2 and `pulse_1` targets have theorem-level local
consequences.  The saved profiles cross the
positive fold and the singular reduction is FSN-II-degenerate there, but no
finite-parameter slow-manifold intersection has been computed; no canard is
identified.  A separate
[fixed-\(r\) surrogate splitting scout](numerics/VDP_CANARD_SPLITTING_SCOUT.md)
finds eight floating-point simple roots from formal entries and is explicitly
`GO_FOR_CANDIDATE_GENERATION_ONLY`; without an invariant slow-manifold entry,
the true maximal-canard root, the classification of \(a_2=0\), and the
high-winding connection all remain `INCONCLUSIVE`.

The subsequent [Appendix-A.2 BVP computation](numerics/VDP_CANARD_SLOW_TRACE.md)
now replaces that projected formal entry by collocation solutions of the
exact finite-\(r\) field on a branch-continued finite-boundary saddle-slow
representative.  It also produces an \(H_2=0\) BVP candidate with maximum
interval RMS relative residual below \(2\times10^{-8}\) and numerically
observed reversibility.  That candidate reaches
the reverser near \(u_2=0.773\), not near the published algebraic RFSN-II
central point, and the finite A.2 boundary has not been shown to define the
intrinsic \(W^{cu}\) trace.  It is therefore a branch-discriminating
coincidence candidate, not a maximal-canard identification or C1/C2 result.

For the frozen periodic target `A2`, the analytic problem has now been reduced
further.  A proved
[self-adjoint operator-pencil moment criterion](van-der-pol/A2_PERIODIC_SPECTRAL_INSTABILITY.md)
shows that a strict scalar inequality implies a real co-periodic temporal
eigenvalue in \((0.01,2)\).  The target-specific
[CAPD validator](validation/a2_periodic/README.md) now encloses a true periodic
profile in the frozen A2 shooting box and proves

\[
 M_{0.01}\in
 [-8.827356014769,-8.827356014754]\times10^{-7}<0.
\]

This is a local outward-rounded mathematical `PASS`, so a full Evans/Bloch
validation is not needed for this target.  It remains non-claim-bearing under
the repository policy only because the independent-machine replay is pending.

The same scalar mechanism now closes the frozen whole-line `pulse_1` target,
with the two corrections required on \(\mathbb R\): the stationary PDE itself
supplies the trial-direction inverse of \(-\partial_x^2\), and the far-field
Fourier symbol gives a uniform positive essential-spectrum edge for the
self-adjoint pencil.  The [whole-line theorem and application](van-der-pol/PULSE_1_SPECTRAL_INSTABILITY.md)
and its [target validator](validation/pulse_1/README.md) prove

\[
 M_{0.01}\in[-8.876883,-8.777882]\times10^{-7}<0,
 \qquad \lambda_*\in(0.01,2).
\]

The target-point Krawczyk image is explicitly contained in the already
selected P2c grid-cell uniqueness tube, so this is the true P2c primary
homoclinic represented by `pulse_1`, not an unrelated near-seed orbit.  This
local mathematical `PASS` has the same remaining release boundary:
independent-machine replay.

### Evidence layers at a glance

| Layer | Current status | Boundary and detailed record |
|---|---|---|
| Analytic applications | B1--B2 are **Proved**; V1 is **Derived**; V2--V7 are **Proved**, relative to the frozen inputs named in the claim register | These are existential positive-parameter results, not certification of the displayed numerical box.  The publication-facing import crosswalk, conditional compact-family/pole-interface audit, and exact frozen evidence snapshot are versioned with the companion release. |
| Floating atlas | `COMPUTED/E1` and `COMPUTED/QA` | Finite explanatory samples only; they do not prove a uniform census, temporal stability, Turing-branch selection, or canard identification.  See the [numerical report](numerics/VAN_DER_POL_NUMERICAL_REPORT.md). |
| A2 and `pulse_1` spectral/nonlinear orbital instability (#11) | Two local mathematical `PASS` results; `claim_bearing=false` | Each true target has a positive real temporal eigenvalue in \((0.01,2)\).  The general semilinear bridge therefore gives A2 co-periodic and `pulse_1` whole-line localized nonlinear orbital instability.  Independent replay is pending, and no pattern-selection conclusion is made.  See the [nonlinear theorem](van-der-pol/NONLINEAR_ORBITAL_INSTABILITY.md), [A2](validation/a2_periodic/README.md), and [`pulse_1`](validation/pulse_1/README.md) records. |
| Canard splitting scout (#13) | `COMPUTED/E1`; `claim_bearing=false` | Exact central-chart integration and first-hit root finding work at \((r,\epsilon)=(0.08,1)\), but the entry uses a projected finite formal jet, not a computed invariant slow manifold.  It is a candidate generator, not a maximal-canard identification.  See the [scout record](numerics/VDP_CANARD_SPLITTING_SCOUT.md). |
| Finite-boundary A.3-compatible canard BVP (#13) | `COMPUTED/E1`; `claim_bearing=false` | With the A.2 outer value \(u_*\) frozen, a six-condition exact-field half-orbit BVP solves jointly for \(T\) and \(a_2\), giving \(a_2\approx-0.008338195267\) and a central/no-loop reverser endpoint within \(1.5\times10^{-6}\) of the order-three formal state.  The older A.2 endpoint-family root is retained as a wrong-branch diagnostic.  Boundary independence, the intrinsic \(W^{cu}\) trace, and the simple-zero graph remain unresolved.  See the [BVP record](numerics/VDP_CANARD_SLOW_TRACE.md). |
| Explicit-box validation (#7) | v1 mathematical `FAIL`; v2 target and comparison bridge frozen before their first retained evidentiary output; `claim_bearing=false` | The immutable v1 box is \([0.04,0.08]\times[-0.25,0.25]\times[0.8,1.2]\); its strict P2e phase-order failure remains the verdict for v1.  The versioned v2 target is \([0.01,0.02]\times[-0.25,0.25]\times[0.8,1.2]\), with comparison bridge \([0,0.02]\times[-0.25,0.25]\times[0.8,1.2]\).  Freezing v2 makes no mathematical `PASS`: P1 must be rerun, any P2a--P2d inheritance requires an exact restriction audit, and the complete P2e event manifest and numeric materialization choices remain pending.  See the [v1 fail-fast report](validation/rigorous/P2E_PHASE_ORDER_FAIL_REPORT.md) and [v2 freeze record](validation/rigorous/P2E_V2_BOX_FREEZE.md). |

Closing an analytic construction issue records completion under the current
frozen-import repository contract.  Public availability of that contract does
not constitute an independent certificate replay, certify the explicit box,
or establish temporal stability, Turing selection, canard identification, or
experimental realization.

## Repository map

- [Frozen theory baseline and local amendments](theory/README.md)
- [Brusselator programme](brusselator/README.md)
- [Brusselator companion paper](papers/brusselator/README.md)
- [van der Pol programme](van-der-pol/README.md)
- [van der Pol companion paper and provenance supplement](papers/van-der-pol/README.md)
- [Frozen RFSN-II source and evidence snapshot](frozen-imports/rfsn-ii-d54add098545063d5efe8f1d6f062d4cfc116a0d/README.md)
- [Research contract](RESEARCH_CONTRACT.md)
- [Continuation and publication plan](CONTINUATION_PLAN.md)
- [Current exact-chart overlap validation](validation/rigorous/P2D_CHART_OVERLAPS_REPORT.md)
- [`pulse_1` whole-line spectral-instability proof and validation](van-der-pol/PULSE_1_SPECTRAL_INSTABILITY.md)
- [Claim register](CLAIM_REGISTER.md)
- [Proof-seam audit](proof-audit/SEAM_AUDIT_2026-08-27.md)
- [Van der Pol publication proof audit](proof-audit/VDP_PUBLICATION_PROOF_AUDIT_2026-08-28.md)
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
- [Issue #7 P2c selected-homoclinic scout report](validation/rigorous/P2C_SCOUT_REPORT.md)
- [Issue #7 P2d symplectic-frame report](validation/rigorous/P2D_FRAME_REPORT.md)
- [Issue #7 P2d analytic-normal-form report](validation/rigorous/P2D_NORMAL_FORM_REPORT.md)
- [Issue #7 P2d zero-energy-fiber report](validation/rigorous/P2D_ZERO_ENERGY_REPORT.md)
- [Issue #7 P2d exact-radial-sections report](validation/rigorous/P2D_EXACT_SECTIONS_REPORT.md)
- [Issue #7 P2d weighted-Kato-passage report](validation/rigorous/P2D_WEIGHTED_PASSAGE_REPORT.md)
- [Issue #7 P2d physical-slide report](validation/rigorous/P2D_PHYSICAL_SLIDES_REPORT.md)
- [Issue #7 P2d finite chart-overlap report](validation/rigorous/P2D_CHART_OVERLAPS_REPORT.md)
- [Issue #7 frozen-v1 P2e phase-order failure](validation/rigorous/P2E_PHASE_ORDER_FAIL_REPORT.md)

## Issue map

- [#1: Brusselator localized stationary profile](https://github.com/h-lu/rfsn-ii-positive-parameter-pde/issues/1) — analytic construction complete under the frozen core input.
- [#2: van der Pol Hamiltonian bridge and compact persistence](https://github.com/h-lu/rfsn-ii-positive-parameter-pde/issues/2) — V1--V2 construction complete under the frozen central input.
- [#3: positive-parameter pole and action finite part](https://github.com/h-lu/rfsn-ii-positive-parameter-pde/issues/3) — local NHIM-pole construction complete.
- [#4: central--outer matching theorem](https://github.com/h-lu/rfsn-ii-positive-parameter-pde/issues/4) — V4--V5 matching construction complete; publication dependency audit remains separate.
- [#5: outer algebraic action finite part](https://github.com/h-lu/rfsn-ii-positive-parameter-pde/issues/5) — V5A construction complete.
- [#6: exhaustive two-end theorem](https://github.com/h-lu/rfsn-ii-positive-parameter-pde/issues/6) — V6--V7 construction complete under the pinned modular imports.
- [#7: rigorous explicit-box validation](https://github.com/h-lu/rfsn-ii-positive-parameter-pde/issues/7) — open; the frozen v1 box has a strict non-claim-bearing phase-order `FAIL`, so any replacement must be a new explicit target.
- [#8: explanatory numerical atlas and dynamics prescreen](https://github.com/h-lu/rfsn-ii-positive-parameter-pde/issues/8) — open; numerical evidence remains separate from theorem status.
- [#9: independent expert cold read](https://github.com/h-lu/rfsn-ii-positive-parameter-pde/issues/9) — open; the neutral review packet is public, but no human report is claimed before one is returned.
- [#10: explicit-box and post-existence research roadmap](https://github.com/h-lu/rfsn-ii-positive-parameter-pde/issues/10) — open; records execution order, mathematical dependencies, and stop rules.
- [#11: rigorous temporal spectral instability](https://github.com/h-lu/rfsn-ii-positive-parameter-pde/issues/11) — both targets have local outward-rounded positive eigenvalues and therefore nonlinear orbital instability by V11; independent replay remains before claim-bearing release.
- [#12: classical stationary Turing exclusion](https://github.com/h-lu/rfsn-ii-positive-parameter-pde/issues/12) — exact theorem and frozen-box corollary proved; mathematically independent of #7.
- [#13: finite-parameter maximal-canard curve and high-winding connection](https://github.com/h-lu/rfsn-ii-positive-parameter-pde/issues/13) — the finite-boundary A.3-compatible central/no-loop candidate is computed at \(r=0.08\); the intrinsic \(W^{cu}\) trace, simple-zero graph, sample classification, and high-winding connection remain open.

The source theory was developed in the historical repository
`h-lu/reversible-rfsn-ii-waves`.  This application repository leaves that
repository unchanged and publishes the exact imported source and evidence at
the [frozen snapshot](frozen-imports/rfsn-ii-d54add098545063d5efe8f1d6f062d4cfc116a0d/README.md).
It imports only explicitly cited results; it does not silently strengthen
them.
