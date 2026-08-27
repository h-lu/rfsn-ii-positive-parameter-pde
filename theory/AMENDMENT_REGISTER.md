# Local amendment and dependency register

**Snapshot date:** 2026-08-27

**Flagship comparison baseline:**
`d54add098545063d5efe8f1d6f062d4cfc116a0d`

Here “amendment” means a companion derivation, theorem, proof, clarification,
or computation developed in this repository relative to the frozen comparison
baseline.  It does **not** mean an edit to the flagship repository.  Every row
below has upstream impact `none`; no local conclusion is represented as having
been incorporated into the flagship manuscript.

`CLAIM_REGISTER.md` remains authoritative for claim status.  This file records
provenance and dependency edges and must be updated after, not instead of, an
authorized claim-register change.

## Classification key

### Provenance relation

- `FROZEN-BASELINE-INPUT`: a precisely bounded statement imported from the
  immutable flagship revision in [BASELINE.md](BASELINE.md).
- `EXTERNAL-MODEL-SOURCE`: equations or facts imported from another cited
  primary source, such as Vo--Doelman--Kaper.
- `LOCAL-AMENDMENT`: work whose statement and evidence belong to this
  repository alone.

### Evidence status

- `Proposed`: theorem-sized work still requiring proof.
- `Derived`: exact symbolic consequence of frozen equations.
- `Numerically observed`: supported by non-rigorous computation.
- `Computer-assisted`: supported by an archived, independently replayable
  interval-rigorous computation.
- `Proved`: supported by a complete mathematical proof in this repository.
- `Imported`: used from an exactly identified external result.
- `Deferred`: a separate research objective, not a proved present claim.

The two axes are independent.  In particular, `LOCAL-AMENDMENT / Proved` does
not alter the baseline, and `LOCAL-AMENDMENT / Numerically observed` does not
establish an analytic theorem.

## Registered local results

| ID | Local result and evidence | Relation / status | Required dependency chain | Upstream impact |
|---|---|---|---|---|
| T1 | Relative overflowing saddle-NHIM theorem on a compact manifold with corners, including fixed-extension uniqueness and mixed parameter regularity; [RELATIVE_OVERFLOWING_NHIM.md](RELATIVE_OVERFLOWING_NHIM.md) | LOCAL-AMENDMENT / Proved | Classical compact boundaryless NHIM section theorem, restated with exact HPS chapter DOIs, followed by the local doubling, restriction, and parameter-as-center proof | None |
| T2 | Descent of a finite compatible atlas of already constructed local marked return/coding presentations to one physical return/first-event relation and invariant closed observables; [FINITE_MARKED_ATLAS_DESCENT.md](FINITE_MARKED_ATLAS_DESCENT.md), Proposition 1 | LOCAL-AMENDMENT / Proved | Frozen finite-atlas covariance modules in RETURN_EXIT_CODING_IMPORT.md plus local marked presentations to which the return/coding theorems already apply; for van der Pol those inputs are constructed chartwise in V6 from V1--V5A before T2 is invoked | None |
| T2G | One globally normalized exact saddle chart, zero deck recoding, and one parameter-global winding alphabet; [FINITE_MARKED_ATLAS_DESCENT.md](FINITE_MARKED_ATLAS_DESCENT.md), Proposition 2 | LOCAL-AMENDMENT / Proposed | T2 plus a normalized analytic Moser construction which trivializes the nonlinear exact-chart cocycle and aligns the global cut | None |
| B1 | Positive-diffusion symmetric Brusselator homoclinic; [`LOCALIZED_PROFILE_PROOF.md`](../brusselator/LOCALIZED_PROFILE_PROOF.md) | `LOCAL-AMENDMENT / Proved` | Frozen core homoclinic import from the baseline, then the local parameter-dependent invariant-manifold and reversible matching proof | None |
| B2 | Positive-concentration localized stationary PDE profile and amplitude/width scales; [`LOCALIZED_PROFILE_PROOF.md`](../brusselator/LOCALIZED_PROFILE_PROOF.md) | `LOCAL-AMENDMENT / Proved` | B1 plus the local exact inverse scaling and positivity estimates | None |
| B3 | Fixed finite-winding or multipulse Brusselator core patterns | `LOCAL-AMENDMENT / Proposed` | B1--B2 plus separate finite-family transverse matching arguments; B1 alone is insufficient | None |
| V1 | Reversible exact-Hamiltonian van der Pol spatial system, primitive, clocks, and exact central bridge; [`HAMILTONIAN_CHECK.md`](../van-der-pol/HAMILTONIAN_CHECK.md), [`MODEL_AND_CENTRAL_CHART.md`](../van-der-pol/MODEL_AND_CENTRAL_CHART.md) | `LOCAL-AMENDMENT / Derived` | Published van der Pol model equations as `EXTERNAL-MODEL-SOURCE`; algebraic verification in this repository | None |
| V2 | Uniform positive-wedge saddle-focus, selected transverse homoclinic, local passage, and compact central event continuation; [`CENTRAL_CONTINUATION.md`](../van-der-pol/CENTRAL_CONTINUATION.md) | `LOCAL-AMENDMENT / Proved` | V1 plus the strictly bounded frozen central-core input; the proof supplies the positive-parameter continuation and two external derivatives locally | None |
| V3 | Genuine positive pole, source window, regular-singular expansion, and pole action finite part; [`POSITIVE_POLE_FINITE_PART.md`](../van-der-pol/POSITIVE_POLE_FINITE_PART.md) | `LOCAL-AMENDMENT / Proved` | V1--V2 and the frozen finite pole-gate certificate; everything after the finite gate is derived from the full positive-parameter equations locally | None |
| V4 | Positive-parameter outer algebraic compactification and future-staying hypersurface; [`OUTER_FUTURE_STAYING.md`](../van-der-pol/OUTER_FUTURE_STAYING.md) | `LOCAL-AMENDMENT / Proved` | V1 and the local positive parameter class; no flagship positive end is imported | None |
| V5 | Resolved K2 → K1 → outer matching, exchange coefficient, source connection, and cut covariance; [`CENTRAL_OUTER_MATCHING.md`](../van-der-pol/CENTRAL_OUTER_MATCHING.md) | `LOCAL-AMENDMENT / Proved` | V1--V2, V4, T1, and only the frozen singular comparison data itemized in that proof; the positive-parameter matching theorem is local | None |
| V5A | Reference-normalized outer physical-length and action finite parts, including strict containment of the V5 arrival labels; [`OUTER_ALGEBRAIC_FINITE_PART.md`](../van-der-pol/OUTER_ALGEBRAIC_FINITE_PART.md) | `LOCAL-AMENDMENT / Proved` | V4--V5 and the fixed physical primitive; singular-core counterterms are not imported | None |
| V6 | Exhaustive high-winding positive-parameter physical return/first-exit relation with compatible finite-atlas data and two finite parts; [`TWO_END_RETURN_EXIT_AND_PDE.md`](../van-der-pol/TWO_END_RETURN_EXIT_AND_PDE.md) | `LOCAL-AMENDMENT / Proved` | V1--V5A, T2, and only the abstract frozen modules in `RETURN_EXIT_CODING_IMPORT.md`; both concrete ends are local, and T2G is not assumed | None |
| V7 | Periodic, multipulse, and aperiodic stationary spatial PDE patterns from bounded V6 itineraries; [`TWO_END_RETURN_EXIT_AND_PDE.md`](../van-der-pol/TWO_END_RETURN_EXIT_AND_PDE.md) | `LOCAL-AMENDMENT / Proved` | V6, frozen abstract coding module, and the exact inverse PDE scaling from V1 | None |
| S1 | Temporal spectral or nonlinear stability of any B2 or V7 profile | `LOCAL-AMENDMENT / Deferred` | New Bloch/Evans spectral analysis and nonlinear stability theorem; no current analytic or numerical row supplies it | None |
| E1 | Calibrated experimental observation | `LOCAL-AMENDMENT / Deferred` | Dimensional calibration, preregistered observables, and experimental data | None |

The van der Pol analytic dependency graph is

\[
\begin{gathered}
 \mathrm{V1}\longrightarrow\mathrm{V2}\longrightarrow\mathrm{V3},\\
 \mathrm{V1}\longrightarrow\mathrm{V4},\\
 (\mathrm{V2}+\mathrm{V4}+\mathrm{T1})
    \longrightarrow\mathrm{V5}\longrightarrow\mathrm{V5A},\\
 (\mathrm{V2}+\mathrm{V3}+\mathrm{V5A}+\mathrm{T2})
    \longrightarrow\mathrm{V6}\longrightarrow\mathrm{V7}.
\end{gathered}
\]

The baseline central-core input enters V2, the bounded singular comparison
data enter V5, and the abstract return--exit/coding modules enter V6--V7.  No
baseline concrete singular end is substituted for V3, V4, V5, or V5A.  T2G
is an optional stronger globalization claim and is not an input to V6--V7.

## Numerical companion work

| ID | Local object and evidence | Relation / status | Analytic dependency | Claim boundary | Upstream impact |
|---|---|---|---|---|---|
| N-VAN-DER-POL-ATLAS | Reproducible V1--V7 numerical atlas, actual finite-time trajectories, periodic and finite-truncation multipulse profiles, and QA artifacts; [`numerics/README.md`](../numerics/README.md) | `LOCAL-AMENDMENT / Numerically observed` | Uses the local V1 equations and the V2--V7 theorem architecture for observable selection and interpretation | Does not certify the existential positive theorem box, replace any proof, prove temporal stability or Turing selection, or identify a canard on a computed global orbit | None |

Numerical work can later become `Computer-assisted` only if every
claim-bearing bound is interval rigorous, tied to immutable source and
environment versions, and independently replayable.  Until then it remains a
valuable local numerical companion without changing an analytic evidence
status.

## Entry template for future local work

Add a row only after recording all of the following:

| Field | Required content |
|---|---|
| Local ID | Stable claim or artifact identifier |
| Statement | Exact scope, parameter class, and nonclaims |
| Relation | One provenance label from this file |
| Evidence status | One repository evidence label |
| Local evidence | Theorem, proof, derivation, certificate, or reproducible numerical artifact |
| Frozen inputs | Exact source revision, theorem locations, hashes when relevant, and retained hypotheses |
| Local prerequisites | Complete dependency chain of earlier claim IDs |
| Upstream impact | `None` unless a separately audited upstream change has actually been accepted |

Never use this register to backdate a local result into the frozen baseline or
to infer that an upstream conclusion has changed.
