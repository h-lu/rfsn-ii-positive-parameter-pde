# Positive-parameter PDE application: continuation plan

This document fixes the next-stage organization of this repository.  It is a
research and publication plan, not a theorem, certificate, or change to the
statuses in `CLAIM_REGISTER.md`.  The claim register and research contract
remain authoritative.

## Execution status on 2026-08-29

- Phase 0 is complete: the snapshot, remote synchronization, candidate
  contract refresh, issue reconciliation, and 181-test pass are recorded on
  `main`.
- Phase 1 is complete as a conditional publication draft: the primary-source
  novelty audit, frozen-core crosswalk, independent proof-interface audit,
  companion-paper source, clean independent build, and page-by-page PDF review
  are present in this repository.
- The imported Core Lemma's complete frozen source, certificate,
  environment, and replay manifest are now included in the versioned public
  snapshot.  This supplies inspectability, not a new independent replay.
- Phase 2 is complete: every imported flagship clause has been mapped to the
  frozen long draft and compressed focused paper in
  `theory/FLAGSHIP_IMPORT_AUDIT_2026-08-28.md`. The frozen baseline was not
  repinned.
- Phase 3 is complete at the deliberately minimal, conditional interface
  level.  The compact-family note proves only persistence/transfer of the
  frozen endpoint, matching, cross-form, and finite physical-event data.  V6
  keeps the exhaustive V2 block, refines the algebraic carrier, replaces the
  protected pole gate by the V3 \(x=10\) carrier, and proves the one spare
  pole-composition derivative.  It does not introduce a general block-
  production theorem.
- Phase 4 is complete as a compact conditional companion: the theorem is
  stated in the original PDE variables, V1--V7 are compressed into one proof
  spine, one schematic geometry figure is included, and hashes/provenance are
  separated into a supplement.
- Issue #7 interval validation has reached local mathematical `PASS` through
  P2c and all seven P2d chart children, including the local parent
  `V2.EXACT_CHART`.  A strict P2e fail-fast cell reverses the required
  algebraic/homoclinic phase order, so `vdp-positive-box-v1` has mathematical
  status `FAIL` and its P2e/P3--P5 computation has stopped.  The negative
  result remains non-claim-bearing at independent replay 1/2.
- Post-existence work has begun under separate issues.  #11 now gives local
  positive temporal eigenvalues for A2 and `pulse_1` and a proved nonlinear
  orbital-instability bridge; #12 proves exact classical stationary Turing
  exclusion; #13 now has a central-localized frozen-boundary A.3-compatible
  half-orbit candidate at \(a_2\approx-0.008338195267\).  It remains
  candidate-only because the intrinsic \(W^{cu}\) entry and simple-zero graph
  are missing.
  Temporal stability, dynamic pattern selection, and maximal-canard
  identification remain open.  An independent human expert report is requested
  in Issue #9 and is not claimed before it is returned.

## 1. Decision

Continue the application programme in this repository.  Do not create a
third research repository and do not move any application result into the
flagship repository.

Use this repository for three different objects, kept visibly separate:

1. the proof dossiers and frozen imports from which claims are audited;
2. concise, independently readable paper manuscripts under `papers/`; and
3. non-rigorous numerical and outward-rounded validation supplements.

The intended publication units are:

- a short Brusselator paper centred on the positive-diffusion localized
  stationary profile;
- a later van der Pol companion paper centred on positive-parameter two-end
  spatial dynamics and stationary PDE patterns.

They share the same frozen RFSN-II input and therefore remain in one research
repository.  They must not be combined into one omnibus paper.

## 2. Repository state at this handoff

The state inspected on 2026-08-28 was:

| Item | State |
|---|---|
| Local research head | `8e9960791e35178087af51a068160e368e3fc580` |
| Remote `origin/main` | `cd65d7a` |
| Local commits not yet on the remote | 52 |
| Local worktree before this document | clean |
| Changed files relative to `origin/main` | 268 |
| Open GitHub issues | #1--#8 |
| Open pull requests | none |
| Unit tests | 109 pass, 1 fails because a candidate-contract hash is stale |

The one failing test is
`numerics.test_vdp_master.VdpMasterContractTests.test_saved_master_artifact_and_stop_rule_statuses`.
It reports outdated SHA-256 bindings for
`van-der-pol/CENTRAL_CONTINUATION.md` and
`van-der-pol/TWO_END_RETURN_EXIT_AND_PDE.md` in the saved V6 candidate
contract.  This is a reproducibility inconsistency, not evidence that a
mathematical theorem or numerical trajectory failed.

The remote repository is therefore not an accurate public or collaborator
view of the present local research.  No further theorem development should
precede preservation and synchronization of this state.

## 3. Evidence and claim boundary

Keep the following distinctions in every issue, commit, manuscript, and
release.

| Layer | Current interpretation | Authoritative location |
|---|---|---|
| Analytic claims B1--B2 and V1--V7 | statuses recorded by the repository; several conclusions depend on frozen imported RFSN-II theorems and certificates | `CLAIM_REGISTER.md` and the cited proof dossiers |
| Floating numerical atlas | explanatory candidate evidence only | `numerics/` |
| Staged interval work | local mathematical passes for completed atoms; aggregate remains non-claim-bearing | `validation/rigorous/` |
| Explicit box `vdp-positive-box-v1` | strict mathematical `FAIL` at the P2e phase-order gate; not a certified theorem box | Issue #7 and `validation/rigorous/P2E_PHASE_ORDER_FAIL_REPORT.md` |
| Temporal PDE stability | deferred | S1 |
| Experimental realization | deferred | E1 |

For publication prose, “proved” must not be read as “proved without imported
inputs.”  The Brusselator theorem imports one rigorously transverse core
homoclinic.  V2--V7 import the frozen central core, algebraic comparison data,
and abstract return--exit/coding modules described in their import records.
Until those inputs have a stable version that an editor and referee can
inspect, manuscript statements must say explicitly that the result is proved
under the cited frozen RFSN-II inputs.

The incomplete outward-rounded validation does not refute the existential
analytic small-parameter theorems.  Conversely, those analytic theorems do
not certify the displayed numerical box.

## 4. Phase 0: preserve and synchronize before new mathematics

### Tasks

1. Verify that local `main` still points to `8e99607` and that the worktree is
   clean.
2. Create an annotated research-snapshot tag at that exact commit, for
   example `application-research-snapshot-2026-08-28`.
3. Push the 52 local commits and the snapshot tag to the private remote only
   after confirming that the push is a fast-forward.
4. Rebuild the V6 candidate contract deterministically so that its theory
   hashes match the current sources.  Do not edit hashes by hand.
5. Run the complete unit-test suite and require zero failures.
6. Add completion comments with proof links and commit identifiers to issues
   #1--#6.  Close an issue only when its current GitHub acceptance criteria
   match the local proved claim.  Keep #7 and #8 open.
7. Replace the long validation changelog in the root README by a compact
   three-layer status table; retain the detailed stage history under
   `validation/rigorous/`.

### Completion gate

Phase 0 is complete only when:

- the local research snapshot exists on the remote;
- `main` is synchronized and clean;
- the full unit-test suite passes;
- GitHub issue status agrees with the claim register; and
- no numerical or interval artifact has been upgraded beyond its recorded
  evidence class.

## 5. Phase 1: Brusselator publication unit

This is the first paper to develop.  It is mathematically smaller, has one
clear theorem, and does not require the van der Pol two-end machinery.

### Mathematical question

For the classical Brusselator at the fixed parameter values used in the
repository, does the transverse RFSN-II core homoclinic continue, for every
sufficiently small positive diffusion parameter, to a positive-concentration
localized stationary PDE profile with controlled amplitude and width?

### Supported principal result

Theorem B in `brusselator/LOCALIZED_PROFILE_PROOF.md` states, subject to its
frozen imported core input, the existence of a nonconstant even localized
stationary solution with

\[
 \|u_d-1\|_\infty=\Theta(d^{1/2}),\qquad
 \|v_d-1\|_\infty=\Theta(d),\qquad
 \text{width}=\Theta(d^{1/4}),
\]

uniform exponential localization, and positive concentrations.

### Proof spine to preserve

```text
frozen transverse symmetric core homoclinic
    -> uniform parameter-dependent local stable/unstable manifolds
    -> reversible matching by the implicit-function theorem
    -> a full positive-diffusion homoclinic with uniform tails
    -> exact inverse PDE scaling
    -> positivity and amplitude/width estimates.
```

### Required work before drafting

1. Perform a primary-literature novelty audit for localized stationary
   Brusselator profiles in the same parameter and diffusion regime.  Decide
   whether Theorem B is new, an explicit strengthening, or a direct corollary
   of an existing continuation theorem.
2. Audit the imported determinant and its stable public/frozen locator.
3. Independently check the parameter-uniform Lyapunov--Perron estimate,
   matching transversality, reflected global orbit, positivity, and width
   observable.
4. Fix the exact theorem quantifiers and the role of the fixed model
   parameters before writing the abstract.

### Manuscript boundary

Create the eventual source under:

```text
papers/brusselator/
```

The paper should contain one sustained line of argument:

1. PDE, scaling, and the main theorem;
2. the imported core result and the exact transversality it supplies;
3. uniform invariant manifolds and reversible matching;
4. return to PDE variables, positivity, localization, and scale laws;
5. an honest discussion of what is not proved.

Do not include:

- Hamiltonian action or the two-end theory;
- van der Pol material;
- temporal stability, Turing selection, canards, or experiments;
- B3 multipulses unless a separate proof is completed;
- the numerical atlas as theorem evidence.

A numerical profile may be used as an illustration only if it is labelled as
computed and does explanatory work that the equations do not already do.

### Completion gate

The Brusselator paper is ready for an independent cold read only when:

- the novelty comparison is documented with primary sources;
- every imported hypothesis appears in the theorem or immediately before it;
- the main proof can be reconstructed without consulting the van der Pol
  dossier;
- the paper builds independently from its own source directory; and
- the abstract distinguishes stationary existence from temporal stability.

## 6. Phase 2: audit the frozen flagship input

The current application baseline is the flagship commit
`d54add098545063d5efe8f1d6f062d4cfc116a0d`.  At the time of this plan, the
focused flagship `main` was `8e04dc3` and contained the 79-page submission
candidate.  These are not interchangeable.

Before the van der Pol paper is drafted:

1. make a clause-by-clause crosswalk from every imported theorem in
   `theory/BASELINE.md`, `CENTRAL_CORE_IMPORT.md`,
   `CORE_HOMOCLINIC_IMPORT.md`, `CENTRAL_OUTER_MATCHING.md`, and
   `RETURN_EXIT_CODING_IMPORT.md` to a stable theorem and proof source;
2. record whether the current focused flagship contains the clause, whether
   only the archived long draft contains it, or whether the application
   repository proves a local replacement;
3. bind every computer-assisted imported statement to accessible source,
   certificate, environment, and replay records;
4. update the baseline only in one explicit audit commit containing new
   hashes, theorem locations, hypothesis differences, and downstream effects.

Classify every imported clause as one of the following:

- **directly applicable:** the focused theorem has the same objects,
  hypotheses, regularity, and quantifier order;
- **adapted locally:** the focused proof mechanism is reused, but this
  repository must prove an additional parameter-uniform or model-specific
  statement; or
- **not applicable:** a decisive object or hypothesis differs, so the local
  theorem must not be presented as an application of that focused clause.

Two adaptations are already known and must appear as theorem-level local
obligations rather than editorial qualifications:

1. the focused paper treats one fixed Hamiltonian, whereas V6 uses a compact
   parameter family, one uniform high-winding threshold, and the mixed
   state/parameter derivatives claimed in V2--V7; and
2. the focused pole hypothesis has an isolated boundary sink with three
   simple positive indicial roots, whereas the V3 positive-parameter pole has
   a two-dimensional boundary equilibrium NHIM with normalized spectrum
   `{-1,0,0,1,4}` and admissible positive roots `1,4`.

The first difference requires a local compact-family passage, selector, and
whole-cell uniformization result unless an accessible stable source supplies
exactly those clauses.  The second requires a local NHIM-pole terminal result
and its interface with first-event coding and exact-action composition.  A
similar name or proof pattern does not make either focused theorem directly
applicable.

Do not silently replace the frozen commit with a branch name or the newest
flagship commit.  If a required imported clause is unavailable to referees,
the dependent application theorem remains conditional in publication prose.

## 7. Phase 3: van der Pol proof audit

Do not begin a polished van der Pol manuscript until this audit is closed.
The current proof dossiers are valuable source material, not yet a paper.

**Current disposition.**  The conditional audit is recorded in
`proof-audit/VDP_PUBLICATION_PROOF_AUDIT_2026-08-28.md`.  It preserves the
frozen-input boundary: the compact-family result is a transfer proposition,
not an independent reconstruction of the fixed-system block.

### Principal mathematical unit

The reader-facing conclusion is V7: bounded spatial itineraries produce
periodic, localized multipulse, and aperiodic stationary solutions of the
positive-parameter van der Pol reaction--diffusion PDE.  V6 is the dynamical
mechanism: an exhaustive local high-winding return--first-exit relation with
two positive-parameter singular ends and compatible action finite parts.

### Required seam audits

1. **Compact-family transfer:** state the frozen endpoint, matching,
   selector, cross-form, finite-event, and overlap data as hypotheses; then
   prove only the coverwise rate, controlled persistence, and finite-atlas
   transfer on the compact parameter box.
2. **Positive-pole terminal interface:** use V3 for the two-dimensional
   equilibrium NHIM and Laurent--log finite part, and record in V6 only the
   source-trace identity and spare entry derivative consumed by terminal
   composition.  Do not identify this result with the focused paper's
   isolated-sink H3.
3. **V2 to V3:** verify that the finite central pole gate is connected to the
   genuine positive-parameter pole on a uniform nonempty source window, with
   the stated parameter derivatives and no use of a singular-core pole
   persistence claim.
4. **V4 to V5 and V5A:** verify the resolved
   `K2 -> K1 -> outer` matching, the imported base comparison data, the
   exchange coefficient, uniform inverse, moving-cut covariance, and the
   same-physical-orbit finite-part construction.
5. **V5 to V6 whole-cell geometry:** retain the already exhaustive finite V2
   block and its imported competing-time rows.  Partition the algebraic
   carrier by the V5 label; replace the protected pole gate by the V3
   event-free slide to \(x=10\), then partition that carrier by the pole
   aperture.  Verify the new source pullbacks and introduce no artificial
   side face or event-time difference.
6. **Finite-atlas descent:** verify that all local return, terminal,
   exact-action, and coding modules are constructed before descent; do not
   assert one global chart, raw winding alphabet, or unmodified local symbol.
7. **V6 to V7:** verify that periodic, finite-word homoclinic, and aperiodic
   spatial solutions use only completed branch domains and that the exact
   inverse scaling returns them to the original PDE.

### Status wording during the audit

Preserve `CLAIM_REGISTER.md`; do not change a status merely because a
reviewer asks a question.  In audit reports and draft theorem prefaces, use
language of the form:

> Assuming the frozen RFSN-II core and modular return--exit results recorded
> in the import statements, the present repository proves ...

This wording may be shortened only after the imported results have become
stable, accessible cited theorems.

### Completion gate

The proof audit is complete only when every arrow

\[
 \mathrm{V1}\to\mathrm{V2}\to\mathrm{V3},\qquad
 \mathrm{V1}\to\mathrm{V4},\qquad
 (\mathrm{V2}+\mathrm{V4}+\mathrm{T1})\to\mathrm{V5}\to\mathrm{V5A},
\]

\[
 (\mathrm{V2}+\mathrm{V3}+\mathrm{V5A}+\mathrm{T2})
 \to\mathrm{V6}\to\mathrm{V7}
\]

has an explicit input, output, decisive estimate or transversality statement,
and source location.  An outline, analogy with the flagship, or successful
floating computation does not close an arrow.

The current audit discharges the two local interfaces in this minimal form.
V6--V7 nevertheless remain conditional in publication prose on the frozen
endpoint, matching, event-arrangement, and coding inputs; the audit does not
upgrade those imports to local independent proofs.

## 8. Phase 4: van der Pol companion paper

Create the paper only after Phase 3 under:

```text
papers/van-der-pol/
```

The paper should begin with the PDE patterns, not with the repository's V1--V7
administrative numbering.  A suitable mathematical order is:

1. PDE, positive parameter class, principal stationary-pattern theorem, and
   explicit nonclaim about temporal stability;
2. exact spatial Hamiltonian structure and continuation of the compact
   saddle-focus/homoclinic package;
3. construction of the genuine positive pole and outer algebraic channel;
4. central-to-outer matching and the two finite parts;
5. whole-cell first-event geometry and finite-atlas descent;
6. coding and translation to periodic, multipulse, and aperiodic stationary
   PDE solutions;
7. technical appendices containing only indispensable estimates.

The abstract should identify one obstruction and one resolution:

```text
the fixed-system RFSN-II mechanism supplies neither the claimed compact-family
uniformity nor the NHIM pole occurring at positive parameter
    -> prove the uniform saddle-passage and whole-cell statements, construct
       the positive pole and outer algebraic channel directly from the full
       equations, and match the latter through K2 and K1
    -> apply the local exhaustive return--exit mechanism
    -> obtain stationary PDE pattern families.
```

Do not reproduce the full validation ledger, GitHub issue history, or every
exploratory numerical figure in the paper.  Those belong to a supplement.

**Completion record.**  The paper source, one-page geometry, provenance
supplement, neutral cold-read packet, rendered PDFs, and exact frozen input
snapshot are now under `papers/van-der-pol/`, `output/pdf/`, and
`frozen-imports/`.  The theorem remains conditional on Hypothesis H, and
the supplement preserves the claim register's evidence boundaries.

## 9. Phase 5: explicit parameter validation

Issue #7 is a separate strengthening project.  It is not a prerequisite for
an existential analytic theorem unless the paper advertises the explicit
candidate box.

The active post-companion dependency map is GitHub Issue #10.  It keeps the
agreed execution order #7 (explicit box), #11 (spectral instability), #12
(classical stationary Turing exclusion), and #13 (finite-parameter canard
connection or separation) distinct from their actual mathematical
dependencies.  No downstream issue is a completion condition for #7.

Continue the interval lane only under the existing fail-closed policy:

- retain the strict `vdp-positive-box-v1` failure permanently; do not relabel
  it `INCONCLUSIVE`, overwrite the box, or continue its downstream P2e/P3--P5
  run;
- before further positive-box work, choose explicitly between a new versioned
  smaller target and a revised application theorem allowing the observed
  event-order change;

- first refactor the Issue #7 obligation map around the hypotheses of the
  publication-facing analytic propositions, preserving every archived
  certificate and its evidence status;
- use the locally passed P2d exact-chart package as the saddle input to the P2e
  finite event atlas, retaining only the event faces and incidences required by
  the common block and marked atlas;
- validate the model-specific finite inputs that determine the explicit box:
  the selected homoclinic and its transversality, positive-pole entry and
  terminal bounds, outer graph cone and bunching, exchange coefficient and
  matching inverse, and the strict physical-channel arrangement margins;
- derive cross forms, the retained finite-event census, and coding from the
  proved analytic propositions rather than independently recreating every
  conclusion as a separate interval subsystem;
- perform the required independent-machine replay;
- bind source, configuration, environment, certificate, and report hashes in
  one immutable release.

Existing P2d, P2e, and P3--P5 atoms may remain as validation implementation
details when they discharge one of these inputs.  They are not the paper's
proof spine, and no new schema, dashboard, or per-atom governance layer should
be introduced unless it is needed for a claim-bearing predicate that is not
already covered.

Until all parent obligations and replay requirements pass, retain
`final_status: INCONCLUSIVE` and `claim_bearing: false`.

Issue #8 remains the explanatory numerical-atlas track.  Its outputs may
guide candidate selection and figures but do not close Issue #7 or any
analytic proof seam.

## 10. Branch and issue discipline

After Phase 0, use one branch and one issue for each bounded task.  Suggested
branch names are:

```text
codex/brusselator-literature-audit
codex/brusselator-paper
codex/flagship-import-audit
codex/vdp-proof-audit
codex/vdp-paper
codex/issue-7-validation
```

Do not develop papers or validation directly on `main`.  Merge only after the
task's acceptance checks pass.  Generated caches, local CAPD builds, temporary
figures, and exploratory outputs not covered by a manifest remain ignored.

## 11. Stop rules

Pause the affected paper rather than strengthening prose if any of the
following occurs:

- the closest literature already proves the same PDE theorem with the same
  uniformity and scales;
- an imported flagship clause cannot be made accessible or cannot be mapped
  to its stated use;
- a seam audit reveals a missing existence, nonemptiness, first-hit,
  transversality, or uniformity argument;
- the van der Pol H2 event family cannot be given a finite auditable census;
- a numerical candidate is being used to replace an analytic or interval
  obligation.

Temporal stability and experimental realization remain separate projects.
They must not be added to either first submission merely to make the PDE
application sound more physical.

## 12. Current bounded next task

The earlier publication-only handoff has been superseded by the explicit
post-existence decision recorded in Issues #10--#13.  The next canard object is
a branch-identified finite-\(r\) saddle-slow zero-energy trace on one fixed
normally hyperbolic entry section, including its \(a_2\)-derivative.  Only then
should the first-hit splitting be promoted from a surrogate to a genuine local
coincidence problem.  A full Evans function is deferred unless a complete
unstable count, multiplicity, Bloch continuation, or multipulse splitting is
needed; it is not required for the already proved positive-eigenvalue
instability consequences.  Dynamic selection remains a separate nonlinear
evolution problem.
