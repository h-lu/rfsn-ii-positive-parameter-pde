# Positive-parameter PDE application: continuation plan

This document fixes the next-stage organization of this repository.  It is a
research and publication plan, not a theorem, certificate, or change to the
statuses in `CLAIM_REGISTER.md`.  The claim register and research contract
remain authoritative.

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
| Explicit box `vdp-positive-box-v1` | frozen validation candidate, not a certified theorem box | Issue #7 and `validation/` |
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

Do not silently replace the frozen commit with a branch name or the newest
flagship commit.  If a required imported clause is unavailable to referees,
the dependent application theorem remains conditional in publication prose.

## 7. Phase 3: van der Pol proof audit

Do not begin a polished van der Pol manuscript until this audit is closed.
The current proof dossiers are valuable source material, not yet a paper.

### Principal mathematical unit

The reader-facing conclusion is V7: bounded spatial itineraries produce
periodic, localized multipulse, and aperiodic stationary solutions of the
positive-parameter van der Pol reaction--diffusion PDE.  V6 is the dynamical
mechanism: an exhaustive local high-winding return--first-exit relation with
two positive-parameter singular ends and compatible action finite parts.

### Required seam audits

1. **V2 to V3:** verify that the finite central pole gate is connected to the
   genuine positive-parameter pole on a uniform nonempty source window, with
   the stated parameter derivatives and no use of a singular-core pole
   persistence claim.
2. **V4 to V5 and V5A:** verify the resolved
   `K2 -> K1 -> outer` matching, the imported base comparison data, the
   exchange coefficient, uniform inverse, moving-cut covariance, and the
   same-physical-orbit finite-part construction.
3. **V5 to V6:** replace the compressed H2 discussion by a finite audit table
   listing the actual defining functions, ambient domains, allowed
   incidences, empty-incidence gaps, event order, side faces, and anchors.
4. **Finite-atlas descent:** verify that all local return, terminal,
   exact-action, and coding modules are constructed before descent; do not
   assert one global chart, raw winding alphabet, or unmodified local symbol.
5. **V6 to V7:** verify that periodic, finite-word homoclinic, and aperiodic
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
the singular RFSN-II end geometry does not persist automatically at positive
parameter
    -> construct the pole and outer algebraic channel directly from the full
       positive-parameter equations and match the latter through K2 and K1
    -> apply the local exhaustive return--exit mechanism
    -> obtain stationary PDE pattern families.
```

Do not reproduce the full validation ledger, GitHub issue history, or every
exploratory numerical figure in the paper.  Those belong to a supplement.

## 9. Phase 5: explicit parameter validation

Issue #7 is a separate strengthening project.  It is not a prerequisite for
an existential analytic theorem unless the paper advertises the explicit
candidate box.

Continue the interval lane only under the existing fail-closed policy:

- complete the remaining five P2d exact-chart children and parent
  `V2.EXACT_CHART`;
- complete P2e and P3--P5;
- validate the full event census, cross forms, two terminal channels, and
  finite-part remainders rather than finitely many representative orbits;
- perform the required independent-machine replay;
- bind source, configuration, environment, certificate, and report hashes in
  one immutable release.

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

## 12. Immediate next task

The next task is Phase 0, not new mathematics.  Once synchronization and the
test repair are complete, open the Brusselator literature audit.  Only after
that audit should the first manuscript file be created.
