# Van der Pol V1--V7 numerical figure contracts

This document fixes the mathematical and visual contract for the van der Pol
numerical atlas requested in Issue #8.  It is a production specification, not
a report of completed runs.  A panel may be rendered as evidence-bearing only
when every acceptance test listed for that panel has a machine-readable value.
If a required analytic object is not explicit enough to compute, the panel must
display `NOT NUMERICALLY RESOLVED` and the obstruction; a schematic substitute
does not satisfy the contract.

## Shared conventions

- **Frozen exploratory parameters.**  Unless a panel states otherwise, use

  \[
  (r,a_2,\epsilon)=(0.08,0,1),\qquad
  d=r^4,\quad \delta=r^2,\quad a=1+\sqrt\epsilon r^3a_2,
  \]

  from `numerics/config/vdp_v1_v7.json`.  Parameter slices, cutoffs, section
  radii, event thresholds, solver tolerances, and acceptance thresholds must
  also come from that versioned file.  A changed threshold requires a new
  configuration version and must not silently replace a failed run.
- **Coordinates and clocks.**  Capital letters \((U,P,V,Q)\) and \(\xi\)
  denote the fixed-equilibrium universal central system.  Lowercase
  \((u,p,v,q)\) and \(\mathsf x\) denote the physical stationary system.
  Pole remaining distance is \(\sigma=\mathsf x_{\rm b}-\mathsf x\), and the
  outer common coordinate is \(\mathfrak q=z^{-2}=u^2\).  These clocks and
  coordinates must not share an unlabeled axis.
- **Evidence labels.**  Every panel carries one visible badge:
  `EXACT/DERIVED`, `COMPUTED/E1`, `COMPUTED/QA`, `MIXED`, or
  `NOT NUMERICALLY RESOLVED`.  `COMPUTED/E1` means explanatory
  floating-point evidence; every configuration-v5 end or return candidate
  also carries `NOT_INTERVAL_VALIDATED`.  A successful schema check remains
  `claim_bearing: false` and is not the interval validation of Issue #7.
- **Common visual vocabulary.**  Exact formulas and predicted asymptotic
  slopes are black; computed primary objects are blue; independent checks are
  orange; reference objects and counterterms are gray; unresolved objects are
  white with a dark hatched border.  Solid, dashed, dotted, and dash-dot styles
  redundantly encode these roles so that no mathematical distinction depends
  on color alone.  Numerical samples use markers.  A line through samples is
  used only for an explicitly named interpolation or fitted/predicted law.
- **Return/exit vocabulary.**  Use the same redundant encoding in every V6--V7
  panel: `return+` = blue circle; `return-` = orange upward triangle;
  `stable_cut_proxy` = black vertical bar; `pole_gate_proxy` = red diamond;
  `algebraic_gate_proxy` = purple square; `escape_unresolved` = gray cross;
  `time_limit_unresolved` or an unresolved boundary band = unfilled marker or
  light-gray hatching.  The words “pole end” and “algebraic end” are reserved
  for trajectories actually continued through V3 or V5/V5A, not for the
  finite \(U\)-gate classifier.  A connected floating candidate is named
  “pole-end candidate” or “algebraic-tail candidate,” never “certified end.”
- **Direction and status.**  Flow arrows mean increasing stated spatial clock.
  Map arrows mean one completed first-event/return operation.  Discrete source
  samples must not be connected so as to look like a flow orbit.  Schematic
  guides, if any, are thin gray dash-dot lines and are named in the caption.
- **Exports and provenance.**  The intended stems are the nine names from
  Issue #8 under `numerics/results/vdp_v1_v7/`, exported as editable PDF/SVG
  and a PNG preview.  Each figure must be reproducible from saved arrays and
  diagnostics plus the configuration and manifest hashes; rendering must not
  rerun a solver implicitly.  Captions must give the parameter tuple,
  coordinate/clock, evidence status, and the principal nonclaim.
- **Global nonclaims.**  No figure proves a uniform theorem box, exhaustive
  cells for all windings, uniqueness beyond the frozen local construction,
  temporal stability or selection, temporal chaos, a Turing bifurcation, or
  experimental observability.  Saddle-focus winding and canard-organized
  outer geometry are distinct mechanisms and must not be merged visually.
- **Forbidden visual semantics.**  Solid trajectories may join panels only
  when their arrays come from one saved orbit or coupled solve.  Hatching is
  retained for the infinite/uniform theorem object and for Issue #7 even when
  a nearby finite candidate exists.  A finite terminal boundary must be drawn;
  fading it into infinity, drawing a filled parameter box around one point, or
  using a theorem/checkmark badge for `COMPUTED/E1` is forbidden.

## Figure 1 — V1 exact structure and clock/coordinate consistency

**Output stem:** `figure_01_v1_structure`

**Mathematical claim.**  The displayed physical and central stationary vector
fields obey the frozen Hamiltonian and reverser sign conventions exactly.  On
the finite test orbit, coordinate/clock conversion preserves the physical
state and the state-space action, while the Hamiltonian rescales by the
displayed clock factor.  The exact identities are V1 identities; the orbit
comparison is only a floating-point consistency check.

**Evidence source.**

- Analytic definitions: `van-der-pol/HAMILTONIAN_CHECK.md` and
  `van-der-pol/MODEL_AND_CENTRAL_CHART.md`, especially the physical and fast
  systems, primitive \(\lambda_\delta\), reverser, central bridge, and clock
  table.
- Exact residuals: `numerics.vdp_central.symbolic_hamiltonian_checks()`.
  The named residuals include the physical first integral, Hamiltonian
  contraction, reverser action on the vector field/primitive/two-form, and
  their central counterparts.
- Numerical orbit data may be accepted only if the master run saves the same
  orbit in physical, fast, and central variables together with round-trip
  state error, energy error, action difference, and refinement level.  There
  is currently no dedicated public clock-round-trip function in the numerical
  modules, so this part remains a required runner diagnostic rather than an
  inferred result.

**Plot recipe.**

1. Panel (a), `EXACT/DERIVED`: render a compact residual table with one row per
   symbolic identity and the exact simplified value.  Do not encode the exact
   zeros on a logarithmic axis.
2. Panel (b), `EXACT/DERIVED`: draw the coordinate/clock crosswalk as a vector
   dependency diagram: physical \(\mathsf x\) \(\leftrightarrow\) fast \(y\)
   \(\leftrightarrow\) central \(y_2\) \(\leftrightarrow\) universal \(\xi\).
   Put the exact scale factor on every arrow; this is a diagram, not an orbit.
3. Panel (c), `COMPUTED/QA`: for the same initial state, plot the maximum
   round-trip state defect, energy defect, and action difference versus step
   size or tolerance.  Normalize each quantity explicitly and include the
   frozen acceptance threshold as a horizontal line.

**Visual grammar.**  Algebraic arrows are black and labeled by formulas;
numerical QA sequences use blue circles and orange triangles for the two
independent formulations.  The physical and universal clocks use different
axis labels even if their sampled curves visually coincide.  A shaded band is
allowed only for a numerical tolerance band, never for an exact identity.

**Acceptance test.**

- Every output of `symbolic_hamiltonian_checks()` is the literal string `0`
  and `passed` is true.
- The central and physical Hamiltonian/primitive signs agree with the frozen
  manuscript convention; equilibrium subtraction and the reverser are
  included, not merely energy conservation.
- The independently integrated orbit comparisons improve under refinement,
  and their final state, energy, and action discrepancies meet the versioned
  thresholds.  If these arrays are absent, panel (c) must say
  `NOT NUMERICALLY RESOLVED` and the full figure does not satisfy V1's
  numerical acceptance item.
- The displayed action comparison is a state-space line integral and is not
  multiplied by a clock factor.

**Forbidden overclaim.**  Exact symbolic cancellation does not validate a
positive parameter box, and conservation on one orbit does not establish
global existence, uniqueness, or stability.  Do not say that all clock
changes preserve Hamiltonian values; the Hamiltonian rescales with the vector
field, whereas the action integral does not.

## Figure 2 — V2 central continuation and local saddle passage

**Output stem:** `figure_02_v2_central_passage`

**Mathematical claim.**  On the predeclared positive-parameter slices, the
selected numerical symmetric homoclinic persists as a well-resolved
zero-energy BVP and the origin has the predicted saddle-focus quartet.  A
paired-orbit experiment in a deterministic linear eigenframe exhibits the
leading logarithmic passage-time and phase slopes for both signs of a raw
transverse amplitude.  This experiment is a proxy for, not a reconstruction
of, V2's exact symplectic saddle chart and transported action coordinate.

**Evidence source.**

- Theorem source: `van-der-pol/CENTRAL_CONTINUATION.md`, Theorem V2(1)--(3).
- Continuation, spectrum, residuals, weighted-tail samples, and finite-tail
  transversality proxies:
  `numerics.vdp_central.compute_homoclinic_continuation()`,
  `saddle_focus_spectrum()`, `transversality_proxy()`, and
  `homoclinic_npz_payload()`.
- Signed passage samples and predicted/fitted slopes:
  `numerics.vdp_central.local_passage_log_law()` and
  `local_passage_npz_payload()`.
- Frozen slices and \(|\nu|\) ladder:
  `numerics/config/vdp_v1_v7.json` under `parameters` and `central`.

**Plot recipe.**

1. Panel (a), `COMPUTED/E1`: overlay the continued symmetric homoclinic
   profiles \(U(\xi)\) on a common universal-clock axis for the frozen
   \(r\)-slice.  An inset may show exponential tail magnitude versus
   \(|\xi|\); the truncation boundary must be marked.
2. Panel (b), `COMPUTED/QA`: show \(\alpha_\mu\) and \(\beta_\mu\) from the
   exact spectrum formula together with the numerical eigenvalues, and show
   BVP residual, tail norm, energy drift, and the two transversality proxies
   as separate quantities.  Do not combine quantities with unlike units on
   one unlabeled axis.
3. Panels (c,d), `COMPUTED/E1`: plot passage time and oriented phase change
   against \(-\log|\nu_{\rm proxy}|\), with the two signs separated by
   marker and line style.  Overlay the predicted slopes \(1/\alpha_\mu\) and
   \(-\beta_\mu/\alpha_\mu\), after deriving the sign from the displayed
   horizontal-axis convention.  State the fitted interval and show the
   scaled or absolute remainder in an inset.

**Visual grammar.**  The homoclinic is a solid trajectory with increasing
\(\xi\) arrows on one half and its reversible image on the other.  The two
transverse signs use circle/triangle markers.  Predicted slopes are black
dashed lines; fitted slopes, if shown, are colored dotted lines and labeled
“fit.”  The linear numerical eigenframe is never drawn as the theorem's exact
transported phase frame.

**Acceptance test.**

- Each displayed continuation sample reports successful collocation, small
  normalized ODE and boundary residuals, controlled energy drift, and a tail
  norm that decreases when the domain is enlarged.
- The numerical quartet matches
  \(\{\alpha\pm i\beta,-\alpha\pm i\beta\}\) within the stored eigenvalue
  residual and lies in the saddle-focus regime.
- Both signs complete the same declared incoming/outgoing passage experiment;
  event residuals and energy-difference drift are reported.
- Fitted leading slopes approach the predicted slopes on the frozen
  \(|\nu|\) ladder under at least one refinement.  A visually straight line
  without slope and remainder diagnostics is not accepted.
- The transversality quantities are labeled “finite-tail proxy”; they are not
  compared to an invented theorem lower bound.

**Forbidden overclaim.**  The plotted slices do not prove the uniform V2
wedge, \(C^2\) parameter dependence, weighted-tail estimates, or uniqueness
outside the frozen shooting box.  The raw `nu_proxy` and numerical canonical
eigenplane phase
are not V2's exact action and absolute transported phase.  High angular
variation near the saddle-focus is not a canard.

## Figure 3 — V3 connected source-window pole candidate and finite-cut action

**Output stem:** `figure_03_v3_pole_finite_part`

**Mathematical claim.**  At the frozen exploratory point, a predeclared phase
window on a finite-horizon nonlinear-\(W^u\) source approximation crosses the
physical pole gate with positive sampled cone margins.  One representative
source is continued on the same physical IVP through increasing \(u\)-levels,
used to fit \((Z_0,W_0,c_4)\), and compared with the exact local pole chart.
The action is augmented from that source cut and receives the V3 Laurent--log
subtraction on the same orbit.  This is a connected `COMPUTED/E1` candidate,
not a certified open source window, pole basin, or improper limit.

**Evidence source.**

- Theorem source: `van-der-pol/POSITIVE_POLE_FINITE_PART.md`, Theorem V3 and
  equations for the compactification, resonant jet, and action subtraction.
- Nonlinear source, phase window, same-orbit connection, label fit, overlap,
  and action data:
  `numerics.vdp_source_to_pole.compute_v2_source_candidate()`,
  `compute_pole_window_candidate()`, `compute_source_to_pole_connection()`,
  and `same_orbit_moving_cut_balance()`.
- Exact transforms, fields, asymptotic jet and counterterm:
  `numerics.vdp_pole.physical_to_compact()`, `compact_sigma_field()`,
  `physical_field()`, `realize_local_pole()`, `divergent_action()`,
  `resonance_identity_residuals()`, and `indicial_spectra()`.
- Saved record and arrays: `numerics/results/vdp_v1_v7/v3_pole.json` and
  `v3_pole.npz`.

**Plot recipe.**

1. Panel (a), `COMPUTED/E1`: show every predeclared source phase and its gate
   values \(y,D,K,y',K'\); mark the frozen cone thresholds and the representative
   phase.  This is a sampled phase window, not a filled certified interval.
2. Panel (b), `COMPUTED/E1`: plot the representative physical orbit from its
   nonlinear-\(W^u\) source through the \(-U=10\) gate and high-\(u\) labels.
   In an aligned overlap view, compare its compact variables with the locally
   realized pole jet versus \(\sigma\).  Draw a continuous line only for this
   same saved orbit and give the direction \(\sigma\downarrow0\).
3. Panel (c), `COMPUTED/QA`: show the blow-up-position, \(Z_0\), and \(W_0\)
   ladders and the global/local physical and compact relative defects.  Print
   the fitted labels from the data; do not substitute the old hand-selected
   labels.
4. Panel (d), `COMPUTED/E1`/`COMPUTED/QA`: plot the source-anchored raw action,
   complete Laurent--log divergent part, and subtraction versus cutoff.  Show
   the last-three spread and moved-gate cut residual.  The visible footer is
   `CONNECTED FLOATING CANDIDATE — NOT_INTERVAL_VALIDATED (#7)`.

**Visual grammar.**  Source-window samples are blue circles without a line or
filled region.  The representative same-orbit trajectory is blue solid, its
local-jet realization orange dashed, and the exact asymptotic reference black
dotted.  Raw action is dark gray, the complete counterterm gray dashed, and
their subtraction blue circles.  A hatched band labeled “uniform/certified
window not validated” remains separate from the sampled phases.

**Acceptance test.**

- The exact resonance identities simplify to zero and the displayed indicial
  roots agree with the V3 convention.
- Every predeclared phase is generated by the nonlinear-\(W^u\) construction,
  reaches the declared gate once, and records positive cone margins, energy
  drift, event speed, and gate residual.
- The representative trajectory uses one physical IVP from source to the last
  \(u\)-level; its global/local overlap and fitted-label spreads are reported.
- Normalized asymptotic residuals have the predicted order on a nontrivial
  cutoff range and are not dominated by the initialization point.
- The raw action follows the displayed Laurent--log divergence, the
  regularized density remains integrable on the computed segment, and the
  subtracted value's tail change decreases on the cutoff ladder.
- The moving-cut residual is no larger than the frozen candidate threshold,
  and the physical/compact action-density cross-check is shown.
- Passing these finite gates changes the numerical status to a connected
  candidate only; the theorem window and limit remain `NOT_INTERVAL_VALIDATED`.

**Forbidden overclaim.**  Do not fill the sampled phase interval as if every
phase and nearby parameter were enclosed, draw the trajectory through the
boundary point \(\sigma=0\), or label the fitted endpoint “proved blow-up.”  A
finite plateau does not prove the \(\sigma\downarrow0\) finite-part limit,
unique labels, or mixed \(C^2\) regularity.  A spatial pole candidate is not
temporal blow-up of the PDE.

## Figure 4 — V4/V5 coupled nonlinear-\(W^u\)--\(K_1\)--outer candidate

**Output stem:** `figure_04_v4_v5_outer_matching`

**Mathematical claim.**  One coupled collocation solve starts on the
finite-horizon nonlinear-\(W^u\) source, follows a central segment to
\(U=-M\), crosses an explicitly resolved \(K_1\) energy sheet, and joins an
outer solution satisfying the finite condition \(\alpha(Q_{\rm end})=0\).
The source phase and central flight time are unknowns; an independent
finite-horizon \(\Gamma(\beta)\) solve checks the same-section outer root.  This
is a reproducible finite candidate, not the infinite V4 graph or V5's uniform
matching/adjoint theorem.

**Evidence source.**

- Theorem sources: `van-der-pol/OUTER_FUTURE_STAYING.md`, Theorem V4, and
  `van-der-pol/CENTRAL_OUTER_MATCHING.md`, Theorem V5.
- Coupled candidate and independent same-section graph:
  `numerics.vdp_matched_outer.compute_matched_outer_candidate()`,
  `finite_horizon_gamma_continuation()`, `central_to_resolved_k1()`,
  `resolved_k1_rhs_r1()`, and `resolved_k1_to_outer_normal()`.
- Nonlinear source: `numerics.vdp_source_to_pole.compute_v2_source_candidate()`.
- Exact outer densities and diagnostics: `numerics.vdp_outer`, including
  `energy_equation_residual()` and `outer_asymptotic_diagnostics()`.
- Saved record and arrays:
  `numerics/results/vdp_v1_v7/v4_v5_matched_candidate.json`,
  `v4_v5_matched_candidate.npz`, and `v4_v5_outer_matching.json`.

**Plot recipe.**

1. Panel (a), `COMPUTED/E1`: display the three saved pieces in separate named
   coordinates, with explicit interface markers: nonlinear-\(W^u\) source to
   central \(U=-M\), resolved \(K_1\) from its central cut to \(r_1=R\), and
   outer \((\beta,\alpha)\) from \(Q_R\) to \(Q_{\rm end}\).  Use a broken-axis
   layout; never put unlike clocks on one continuous unlabeled axis.
2. Panel (b), `COMPUTED/QA`: show boundary/interface, central/\(K_1\)/outer
   energy, independent \(q_1\)-interface, minimum-\(\pi\), and arrival-collar
   diagnostics.  Print the solved source phase and flight time.
3. Panel (c), `COMPUTED/E1`/`COMPUTED/QA`: plot the candidate seam point in
   \((\beta,\alpha)\) together with the independent finite-horizon
   \(\Gamma(\beta)\) continuation and the same-section root residual.  Mark the
   artificial \(Q_{\rm end}\) boundary and any shorter-horizon comparison.
4. Panel (d), `MIXED`: show finite-horizon asymptotic trends and a hatched list
   of theorem objects still absent: infinite/maximal V4 graph, uniform tube,
   endpoint adjoint, positive exchange bound, invertible matching derivative,
   uniqueness, and parameter jets.  The analytic \(144\sqrt3\) value remains
   “frozen exact comparison.”

**Visual grammar.**  The single coupled candidate is blue solid across three
coordinate-specific panels; interface states share a distinctive double-ring
marker.  The independent \(\Gamma\) solve is orange dashed, exact chart arrows
black, and terminal-horizon alternatives gray dotted.  The theorem graph/tube
is a hatched box, not a thickening of the candidate trajectory.  A caption
must state `COMPUTED/E1_MATCHED_CANDIDATE — NOT_INTERVAL_VALIDATED`.

**Acceptance test.**

- The coupled solve succeeds and its boundary/interface residual, independent
  same-section root residual, three energy residuals, and resolved-\(K_1\)
  interface residual meet the frozen candidate thresholds.
- \(Q_R<Q_{\rm label}<Q_{\rm end}\), \(\pi>0\), and both scaled and unscaled
  arrival margins are recorded and pass.
- Terminal-horizon sensitivity is displayed rather than hidden; a finite
  \(\Gamma\) curve is never renamed the infinite graph.
- The source model string explicitly names the finite-horizon nonlinear
  unstable graph, and the saved arrays reproduce all plotted pieces.
- Panel (d) remains visible even when all finite candidate residuals pass.

**Forbidden overclaim.**  The terminal condition
\(\alpha(Q_{\rm end})=0\) is not the theorem's graph \(\Gamma_\mu\).  Do not
draw the finite outer curve continuing to \(Q=\infty\), thicken one candidate
into an invariant tube, or use a uniqueness/checkmark glyph.  A small BVP/root
residual does not compute the endpoint adjoint, exchange coefficient,
invertible theorem operator, normal expansion, third-order bunching, or mixed
parameter jets.

## Figure 5 — V5A outer algebraic length/action finite parts

**Output stem:** `figure_05_v5a_algebraic_finite_part`

**Mathematical claim.**  On a common finite \(Q\)-grid, the neighboring tail is
the actual saved outer leg of the configuration-v5 coupled V4/V5 candidate;
the reference is an independently solved finite-horizon \(\beta=0\) tail
normalized at the fixed post-matching cut \(Q_*=Q_{\rm label}=100\), not at
the internal seam \(Q_R=25\).
Their exact physical length/action densities, complete reference
counterterms, same-\(Q\) differences, and finite-cut balances are evaluated.
This upgrades the calculation from a disconnected proxy to a candidate-based
finite subtraction, but it does not verify the infinite V5A limits.

**Evidence source.**

- Theorem source: `van-der-pol/OUTER_ALGEBRAIC_FINITE_PART.md`, Theorem V5A.
- Candidate-based common-grid tails and exact densities:
  `numerics.run_vdp_master.matched_outer_tail_pair()` and
  `numerics.vdp_outer.outer_physical_densities()`.
- Cutoff arrays and leading terms:
  `reference_subtracted_integrals()` and
  `leading_counterterm_differences()`.
- Diagnostics and covariance checks: `outer_asymptotic_diagnostics()`,
  `numerical_cut_balance()`, `reference_change_balance()`,
  `gauge_composition_balance()`, and `terminal_potential_transfer()`.
- Full finite V5 action split and reference-corrected composition:
  `matched_action_decomposition()` and `strict_v5a_composition()`.
- Frozen \(Q\)-ladder: `numerics/config/vdp_v1_v7.json` under
  `matched_outer.finite_part_output_ladder` and `matched_outer.candidate_q_end`.
- Saved arrays and status: `numerics/results/vdp_v1_v7/v4_v5a_outer.npz` and
  `v5a_outer_finite_part.json`.

**Plot recipe.**

1. Panel (a), `COMPUTED/E1`: plot the independent reference and matched-candidate
   \(\mathcal T(Q)\) and \(\mathcal A(Q)\) densities after scaling by the
   powers that have finite predicted limits.  Below them, show the signed
   same-\(Q\) density differences on a log-magnitude axis with sign encoded by
   marker fill.
2. Panel (b), `COMPUTED/E1`: plot the raw neighboring length and reference
   length counterterm separately, and their reference-subtracted difference,
   versus \(Q^{1/2}\).  Use an inset for the final cutoff changes.
3. Panel (c), `COMPUTED/E1`: repeat for action versus \(Q^{5/2}\).  Keep the
   negative sign of the leading action counterterm visible; do not take an
   unsigned logarithm.
4. Panel (d), `COMPUTED/QA`: show a residual table or log-scale dot plot for
   cut additivity, reference change, gauge coboundary cancellation, terminal
   potential transfer, quadrature refinement, and finite-horizon sensitivity.

**Visual grammar.**  Reference densities/counterterms are gray dashed; the
matched-candidate outer leg is the same blue solid used in Figure 4;
reference-subtracted quantities are blue circles.  Predicted leading powers
are black dotted guides with formulas, never fitted laws.  All compared tails
share the same \(Q\)-grid, and the finite \(Q_{\rm end}\) boundary is a visible
vertical line.  A hatched continuation beyond it is labeled “not computed.”

**Acceptance test.**

- Reference and neighboring tails share exactly the same physical \(Q\)-grid,
  begin at \(Q_*=Q_{\rm label}>Q_R\), use the same parameter tuple, satisfy
  \(\beta_{\rm ref}(Q_*)=0\), and maintain \(\pi>0\) and small energy/BVP
  residuals.
- Scaled reference densities approach
  \(1/(2q_*)\) and \(-q_*/(2\delta)\), respectively, and the raw counterterms
  grow with the predicted \(Q^{1/2}\) and \(-Q^{5/2}\) leading orders.
- Same-\(Q\) density gaps decrease across the tail; the final changes of both
  reference-subtracted integrals decrease on the frozen \(Q\)-ladder and
  under a larger finite horizon.
- Independent density pullbacks, the resolved-\(K_1\) pullback integral, and
  the output-grid ladder satisfy their declared numerical tolerances.
  Finite-cut composition on the same cumulative arrays is shown only as
  `EXACT/DERIVED` bookkeeping.  It includes the reference endpoint correction
  beyond \(Q_*\), together with a nonzero omitted-correction control; it is not
  presented as independent evidence for covariance of an improper limit.
- The caption states `MATCHED FINITE-HORIZON SAME-Q CANDIDATE` and
  `NOT_INTERVAL_VALIDATED`; the plot cannot be counted as V5A's improper-limit
  computation until an infinite graph/tail enclosure is supplied.

**Forbidden overclaim.**  An apparent plateau at one finite \(Q\) does not
prove an improper finite part, exponential flatness, mixed parameter
derivatives, or coordinate/reference covariance at infinity.  Do not subtract
only a leading polynomial and call the remainder V5A's finite part: the
theorem subtracts the complete reference tail.  Do not draw the finite curve
to infinity or use its finite-cut value as a certified V6 algebraic-exit value.

## Figure 6 — V6 finite numerical first-event section

**Output stem:** `figure_06_v6_first_event_cells`

**Mathematical claim.**  On the deterministic numerical zero-energy outgoing
section, direct exact-ODE integrations have reproducible finite first-event
labels.  In addition, the B1 and A2 periodic anchors are continued as complete
two-segment source-to-source returns and realize negative and positive target
transverse-sign proxies.  The picture is a finite sample atlas in numerical
eigenframe coordinates; it is not V6's transported source cell, literal
component census, or proof of exhaustiveness.

**Evidence source.**

- Theorem source and distinction between interiors/faces:
  `van-der-pol/TWO_END_RETURN_EXIT_AND_PDE.md`, Theorem V6(1)--(3).
- Numerical section and anchors:
  `numerics.vdp_return_coding.reversible_saddle_frame()`,
  `zero_energy_source_state()`, `homoclinic_source_anchor()`,
  `numerical_source_coordinates()`, and `periodic_source_anchor()`.
- Direct first events: `integrate_first_event()`,
  `sample_first_event_atlas()`, and `event_sample_record()`.
- Complete B1/A2 records:
  `numerics.vdp_complete_branches.integrate_complete_return_branch()`,
  `CompleteReturnBranch.as_candidate_record()`, and `as_npz_payload()`; output
  in `v6_complete_branches.npz` and the two `v6_complete_*.json` files.
- Event sampling and finite thresholds:
  `numerics/config/vdp_v1_v7.json` under `central` and `events`.

**Plot recipe.**

1. Panel (a), `COMPUTED/E1`: scatter every sampled pair
   \((\phi_{\rm numerical},\nu_{\rm numerical})\) with the shared categorical
   event marker.  If raster cells are used, each pixel must represent one
   evaluated sample or an explicitly stated nearest-neighbor bin; never smooth
   categorical data.
2. Panel (b), `COMPUTED/QA`: magnify neighborhoods of label changes.  Show the
   coarse samples, refined samples, and a hatched unresolved band whose width
   is determined by the configured uncertainty margin or by the last
   refinement spacing.  Do not draw a continuous boundary through unresolved
   points.
3. Panel (c), `COMPUTED/E1`: show the homoclinic source anchor and the periodic
   outgoing anchors on the same section.  Next to each anchor list family,
   relative winding metadata, reconstruction defect, and actual returned
   label.  Highlight B1/A2 and their opposite target sign proxies.  An
   orbit that never reaches the chosen source radius is labeled
   `NOT NUMERICALLY RESOLVED`, not omitted.
4. Panel (d), `COMPUTED/QA`: plot first-event time, hit speed magnitude, energy
   drift, and local absolute angular variation for resolved samples.  Add the
   B1/A2 source/target phase and transverse proxy as paired points, but do not
   interpolate a cell boundary between them.

**Visual grammar.**  Use the shared return/exit marker dictionary from this
document.  Section axes are labeled `numerical_canonical_eigenplane_phase` and
`numerical_transverse_coordinate_not_exact_action`.  A vertical seam at
phase \(0\equiv2\pi\) is a coordinate seam, not a component boundary.
Flow paths, if shown in an inset, have time arrows; atlas samples do not.  B1
and A2 retain the periodic-family styling but acquire an outer ring denoting a
complete return record, not a certified V6 edge.

**Acceptance test.**

- Every source state has a recorded zero-energy residual, and every resolved
  integration records solver success, one selected first event, event speed,
  terminal state, and energy drift.
- The homoclinic anchor reconstructs from the numerical section within the
  frozen tolerance and reaches `stable_cut_proxy` rather than a spurious
  numerical return.
- The provisional finite-atlas panel retains every observed label and verifies
  selected labels under step halving/local refinement.  The frozen run shows
  one `return+`, one `return-`, 163 `pole_gate_proxy`, and one
  `stable_cut_proxy`; B1/A2 independently provide opposite complete-return
  target-sign proxies.
- Samples near a label change are either stable under refinement or are shown
  in the unresolved band.  Empty or failed integrations are retained.
- A `pole_gate_proxy` or `algebraic_gate_proxy` counts only as a finite central
  gate.  The separate V3/V5 candidate connections do not turn all 163 gate
  samples into completed exit branches.

**Forbidden overclaim.**  Finite samples do not prove no gaps, no overlaps,
connectedness, neat incidence, all \(n\ge N\), or exactly one event on the
whole cell.  The local absolute angular-variation statistic is a winding
proxy, not an absolute V6 label.  Gate proxies are not end orbits, and the
sampled spatial return relation is neither temporal chaos nor Turing pattern
selection.  Do not shade a region between two complete anchors as a connected
return cell, assign B1/A2 integer V6 winding labels, or replace the unresolved
boundary bands by smooth curves.

## Figure 7 — V6/V7 sampled length and action trends

**Output stem:** `figure_07_v6_length_action`

**Mathematical claim.**  The computed reversible periodic families exhibit a
finite-sample physical-period trend consistent with the V6/V7 leading
saddle-focus scale.  B1 and A2 now also have complete finite return records:
both their global and local-passage pieces share one IVP, and physical length
and action are augmented across the split.  The V3 pole and V5A algebraic-tail
candidates add same-orbit/same-tail finite-cut checks.  These data validate
finite candidate composition, not the exact V6 cocycle over exhaustive edge
families or either infinite end value.

**Evidence source.**

- Theorem source: `van-der-pol/TWO_END_RETURN_EXIT_AND_PDE.md`, V6(4)--(5) and
  V7 formula (29).
- Periodic length/action data: `numerics.rfsn_numerics.compute_periodic_orbit()`
  and `common_slope_fit()`, plus
  `numerics.vdp_return_coding.periodic_profile_diagnostics()`.
- Predicted one-winding physical slope:
  \(2\pi r/(\epsilon^{1/4}\beta_\mu)\), with \(\beta_\mu\) from
  `numerics.vdp_central.saddle_focus_spectrum()`.
- End-segment identities:
  `numerics.vdp_source_to_pole.same_orbit_moving_cut_balance()`,
  `numerics.vdp_outer.numerical_cut_balance()`, and
  `gauge_composition_balance()`.
- Complete returns and augmented observables:
  `numerics.vdp_complete_branches.integrate_complete_return_branch()` and
  `CompleteReturnBranch`; saved in `v6_complete_branches.npz` and the two
  `v6_complete_*.json` records.

**Plot recipe.**

1. Panel (a), `COMPUTED/E1`: plot physical period against declared *relative*
   winding for families A and B.  Overlay the theorem-predicted slope as a
   black dashed line with separate fitted intercepts, and show period residuals
   below.  List the fitting range and number of points.
2. Panel (b), `COMPUTED/E1`: plot closed physical action against relative
   winding for each family.  Emphasize B1/A2 with their complete-record totals
   and target sign proxies; display their augmented length and action in a
   compact inset.  Do not force a common limiting intercept.
3. Panel (c), `COMPUTED/QA`: for B1/A2 show global plus local-passage segment
   contributions, direct augmented totals, resampled-action differences, and
   segment composition residuals.  Periodic closure/energy/PDE residuals may
   remain as secondary context.
4. Panel (d), `MIXED`: show V3 same-orbit moving-cut and V5A matched-tail
   cut/gauge residuals.  Beside them place two separate status rows:
   `finite two-segment returns: COMPUTED/E1` and
   `exhaustive V6 edge cocycle/all-n bounds: NOT_INTERVAL_VALIDATED`.

**Visual grammar.**  Families A/B use circle/triangle markers and solid/dashed
lines.  The predicted slope is black dashed and the regression is colored
dotted; the legend distinguishes “predicted” from “fit.”  QA residuals are on
log axes with the frozen thresholds as horizontal rules.  Segment-level end
identities and branch-level candidates occupy visually separate boxes.  A
complete-return bar may be divided into two stacked segment contributions;
it may not be extended into a chain of uncomputed edges.

**Acceptance test.**

- Every displayed periodic point passes full-state closure, independent
  step-halving, energy-drift, and physical stationary-residual checks.
- The fitted period slope and its residual are reported next to the predicted
  value.  “Consistent” may be used only when refinement and omission of the
  lowest-winding point do not qualitatively change the comparison.
- Actions use the physical primitive and scaling fixed in V1; no central and
  physical action values are mixed.
- B1/A2 each begin and end on the declared numerical \(\rho_u\) face; their
  target transverse-sign proxies are opposite, their two segment totals equal
  the direct augmented totals, and an independently resampled action check is
  reported.
- V3/V5A cut and gauge checks close within recorded numerical error.
- The figure may claim complete finite B1/A2 return accounting.  It may not
  claim the V6 cocycle theorem until certified edge families, their pullback
  maps, composable itineraries, exit counterterms, and all-winding bounds are
  supplied.

**Forbidden overclaim.**  Five relative-winding samples do not prove the
\(n\to\infty\) asymptotics or identify the absolute V6 labels.  A closed-orbit
action trend or two segment-composition checks do not validate the exhaustive
branch cocycle or either infinite end finite part.  Do not call the plotted
action a temporal action, stability functional, or pattern-selection
criterion; do not depict B1/A2 as a whole symbolic graph.

## Figure 8 — V7 periodic and multipulse stationary PDE profiles

**Output stem:** `figure_08_v7_patterns`

**Mathematical claim.**  The displayed reversible shooting solutions are
actual bounded periodic orbits of the full positive-parameter central ODE.
The displayed symmetric collocation outputs are accepted one- through
four-pulse finite-domain solutions of that full ODE when their solver,
boundary, tail, energy, pulse-count, and PDE-residual gates pass; this does not
by itself certify infinite-domain homoclinicity or uniqueness.  Their
reconstruction in physical \((\mathsf x,u,v)\) variables satisfies the
stationary PDE to the recorded finite-difference tolerance.  Current A/B
labels and finite words are numerical family or requested-word metadata unless
a V6 section-itinerary check has verified them.

**Evidence source.**

- Theorem source: `van-der-pol/TWO_END_RETURN_EXIT_AND_PDE.md`, Theorem V7.
- Reversible periodic solutions:
  `numerics.rfsn_numerics.compute_periodic_orbit()` with the five frozen
  branch specifications in `numerics/config/vdp_v1_v7.json`.
- Full-ODE multipulses and physical reconstruction:
  `numerics.vdp_return_coding.solve_symmetric_multipulse()`,
  `stationary_pde_residual()`, and `periodic_profile_diagnostics()`.
- Finite-window packaging and its explicit coding caveat:
  `finite_window_approximants()`.

**Plot recipe.**

1. Panel (a), `COMPUTED/E1`: show representative periodic central profiles
   \(U(\xi)\) for both numerical families and increasing relative winding,
   aligned at the same reversibility section.  Mark one period and the
   direction of increasing \(\xi\).
2. Panel (b), `COMPUTED/E1`: show the corresponding physical stationary
   profiles \(u(\mathsf x)\) and \(v(\mathsf x)\), with separate axes or clear
   normalization.  Do not animate or label \(\mathsf x\) as PDE time.
3. Panel (c), `COMPUTED/E1`: overlay or vertically offset the accepted
   one- through four-pulse physical profiles on their full truncated
   domains.  Mark the homogeneous state and both boundary truncations.
4. Panel (d), `COMPUTED/QA`: tabulate requested versus observed pulse count,
   solver status, ODE/boundary/tail residuals, energy drift, and two physical
   stationary PDE residuals.  If finite-window records are included, plot
   their common central windows only after actual arrays are saved; print
   `word metadata only` beside each unverified itinerary.

**Visual grammar.**  Periodic families retain the A/B circle/triangle and
solid/dashed encodings from Figure 7.  Multipulse count is encoded by line
style and direct label.  The homogeneous state is a thin black dotted line;
truncation boundaries are gray vertical lines.  A requested symbolic word is
shown in square brackets, whereas a verified section itinerary, if later
available, is shown with arrow-separated event symbols; these notations may
not be interchanged.

**Acceptance test.**

- Every periodic sample has a converged reversible shooting root, full-state
  closure/step-halving diagnostics, controlled Hamiltonian drift, and a
  physical stationary PDE residual below the versioned threshold.
- Every displayed multipulse has solver success, observed pulse count equal to
  requested count, controlled boundary/tail defects and energy drift, and a
  passing physical stationary PDE residual.  An `INCONCLUSIVE` solution is
  retained in QA but not drawn as an accepted profile.
- At least three distinct primitive periodic *words*, including a multi-edge
  word, count toward the full V7 acceptance item only after their source
  section itineraries are verified.  The five current single-family shooting
  labels do not automatically meet that requirement.
- A finite-window sequence counts toward the aperiodic numerical item only if
  at least four growing computed windows have saved state arrays and their
  common central-window differences decrease.  It must still be called a
  sequence of finite-window approximants.

**Forbidden overclaim.**  Do not call numerical A/B family labels certified
V7 edge codes without an itinerary check.  Do not call a superposition initial
guess a multipulse; only the converged full-ODE solution is evidence.  Finite
windows are not a constructed nonperiodic bi-infinite orbit.  Stationary
spatial patterns are not temporally stable, temporally selected, temporal
chaos, or a demonstrated Turing branch.

## Figure 9 — Numerical QA, convergence, and coverage boundary

**Output stem:** `figure_09_numerical_qa`

**Mathematical claim.**  The displayed numerical objects have transparent
residual, refinement, and cross-formulation diagnostics, and the atlas states
which V1--V7/V5A obligations are computed, exact, rigorous-only, failed,
inconclusive, or not numerically resolved.  This is quality control for the
artifacts, not an independent proof of any theorem.

**Evidence source.**

- Frozen thresholds and nonclaims:
  `numerics/config/vdp_v1_v7.json`.
- Per-stage diagnostic dictionaries and saved arrays produced by
  `numerics.vdp_central`, `numerics.vdp_source_to_pole`,
  `numerics.vdp_matched_outer`, `numerics.vdp_complete_branches`,
  `numerics.vdp_pole`, `numerics.vdp_outer`,
  `numerics.vdp_return_coding`, and `numerics.rfsn_numerics`.
- Top-level `manifest.json`, stage diagnostics, test output, and the companion
  `numerics/VAN_DER_POL_COVERAGE_MATRIX.md` when produced by the master run.
- Candidate and analytic-only flags must be read separately from the data:
  V3's connected/window status and interval stop rule, the V4/V5 candidate
  status plus `v5_matching_status()`, the B1/A2 branch records, and the
  candidate contract's `claim_bearing: false`/`final_status: NOT_RUN`.

**Plot recipe.**

1. Panel (a), `COMPUTED/QA`: plot normalized residuals
   \(\text{measured}/\text{threshold}\) by object and stage on a log axis.
   A value of one is the frozen pass boundary.  Use separate rows for ODE,
   boundary/closure, energy, event, independent-method, PDE, and quadrature
   checks.
2. Panel (b), `COMPUTED/QA`: show convergence ratios or last-step changes for
   domain, cutoff, grid, tolerance/precision, finite horizon, and step-halving
   ladders.  Missing refinements are explicitly marked `NOT RUN`.
3. Panel (c), `MIXED`: render the V1--V7/V5A coverage matrix with the exact
   status strings `EXACT/DERIVED`, `COMPUTED/E1`, `COMPUTED/QA`,
   `NOT_INTERVAL_VALIDATED`, `RIGOROUS-ONLY (#7)`, `FAIL`, `INCONCLUSIVE`, and
   `NOT NUMERICALLY RESOLVED`.  A theorem-level row may have several status
   cells; never collapse a computed proxy and unresolved target into one
   green cell.
4. Panel (d), `EXACT/DERIVED`: print the configuration version, source/config/
   result hashes, environment summary, reproduction command, and global
   nonclaims in a compact provenance box.

**Visual grammar.**  Pass is a filled blue circle, failure a red cross,
inconclusive an orange triangle, not run an open gray circle, rigorous-only a
black outlined square, and not-resolved a hatched cell.  Green is not used as
the sole pass cue.  Residuals exceeding the plotting range are clipped only
with an outward arrow and their numerical value printed.

**Acceptance test.**

- Every evidence-bearing figure has a corresponding raw array, diagnostics
  record, configuration hash, source hash, and reproduction command in the
  manifest.
- No `NaN`, failed solve, missing refinement, or threshold violation is
  silently omitted; it receives an explicit status.
- Threshold normalization uses the configuration frozen before the
  claim-bearing run.  Changed thresholds are shown as a different
  configuration version rather than overwriting the old comparison.
- At least one central observable and one end observable have an independent
  formulation or step-halving check; all required domain/cutoff/grid/tolerance
  checks are represented.
- PDF/SVG/PNG exports have consistent content, readable labels at final size,
  nonvanishing dash/marker distinctions in grayscale, embedded/searchable
  fonts where possible, and no accidental rasterization of line art.
- The coverage matrix and this figure agree exactly that V3's connected orbit,
  V4/V5's coupled root, V5A's matched-tail subtraction, and B1/A2 finite
  returns are computed candidates, while the certified V3 box/limit, infinite
  V4 graph, uniform V5 adjoint/exchange/uniqueness, exhaustive V6 cells/cross
  forms/cocycle, and V7 verified coding remain unresolved.

**Forbidden overclaim.**  A residual below a tolerance is not interval
certification, theorem-box membership, or proof of an infinite/uniform
assertion.  A high percentage of green cells is not a completeness theorem.
Do not relabel `RIGOROUS-ONLY (#7)` as numerically passed, and do not convert
`NOT NUMERICALLY RESOLVED` to `SCHEMATIC` merely to fill a panel.

## Final-page review checklist

- Read every caption against the theorem item it serves and against the
  companion coverage matrix; the caption must ask the reader to see no more
  than the plotted evidence supports.
- Inspect standalone PDF/SVG and the rendered manuscript page at final size.
  Check panel order, coordinates, clock direction, signs, section orientation,
  cut direction, labels, crop, font embedding, line weight, markers, and
  grayscale meaning.
- Verify that the same object keeps the same line/marker semantics across all
  nine figures and that `proxy`, `relative winding`, `finite window`, and
  `NOT_INTERVAL_VALIDATED`/`NOT NUMERICALLY RESOLVED` qualifiers remain visible
  after reduction.
- Figures 3 and 4 may now show the connections realized by the saved V3 orbit
  and coupled V4/V5 solve.  Verify that they do not extend those finite arrays
  to an infinite end, parameter box, invariant tube, adjoint, or uniqueness
  claim.
- Preserve the raw and failed data used during review.  A visually attractive
  curve never overrides a failed diagnostic or an analytic provenance gap.
