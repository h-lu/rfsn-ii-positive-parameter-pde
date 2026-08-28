# Theory provenance and local-amendment policy

This directory records how the mathematical results developed in this
repository relate to the independent flagship repository
[`h-lu/reversible-rfsn-ii-waves`](https://github.com/h-lu/reversible-rfsn-ii-waves).
It is a provenance layer, not a second claim register and not a copy of the
flagship manuscript.

## Independence rule

The flagship repository is a **read-only external dependency** for this
project.  Its frozen comparison revision is identified in
[BASELINE.md](BASELINE.md).  Work in this repository must not edit, rewrite,
commit to, or silently reinterpret that revision.  A local proof, derivation,
computation, correction, or clarification is a result of this repository only;
it does not change a flagship theorem, proof, abstract, or evidence status.

The dependency is citation-based and revision-pinned.  It is not a live
submodule, sibling-worktree dependency, or permission to take unpublished
changes from the flagship working tree.  If a result developed here is ever
ported upstream, that must be a separate, explicitly authorized change with a
new source revision and a fresh dependency audit.

## Two independent classifications

Every registered item has two labels which must not be conflated.

1. **Provenance relation** says where the content belongs:
   `FROZEN-BASELINE-INPUT`, `LOCAL-AMENDMENT`, or
   `EXTERNAL-MODEL-SOURCE`.
2. **Evidence status** uses the repository vocabulary: `Proposed`, `Derived`,
   `Numerically observed`, `Computer-assisted`, `Proved`, `Imported`, or the
   planning status `Deferred` used by the claim register.

For example, `LOCAL-AMENDMENT / Proved` means that this repository contains a
proof of a companion result.  It does **not** mean that the flagship baseline
has been amended, that the result appeared at the frozen flagship commit, or
that the upstream authors have adopted it.  Likewise, a numerical observation
cannot upgrade an analytic claim to `Proved`.

## Authority order

When records differ, use the following order.

1. [`AGENTS.md`](../AGENTS.md) controls repository independence and working
   practice.
2. [`CLAIM_REGISTER.md`](../CLAIM_REGISTER.md) is authoritative for the
   mathematical status of claim IDs.
3. [`RESEARCH_CONTRACT.md`](../RESEARCH_CONTRACT.md) fixes scope, completion
   conditions, fallbacks, and nonclaims.
4. The model-specific import notes fix the exact external statements,
   hypotheses, revisions, hashes, and evidence boundaries actually used.
5. [BASELINE.md](BASELINE.md) and
   [AMENDMENT_REGISTER.md](AMENDMENT_REGISTER.md) summarize provenance and
   dependencies; they cannot enlarge a theorem or override the files above.

## Files in this directory

- [BASELINE.md](BASELINE.md) identifies the immutable flagship comparison
  revision, its role, the allowed imports, and the excluded conclusions.
- [AMENDMENT_REGISTER.md](AMENDMENT_REGISTER.md) records local companion
  results and numerical work, their evidence status, and their complete
  dependency chain.
- [EXPLICIT_GLOBAL_MOSER_MAJORANT.md](EXPLICIT_GLOBAL_MOSER_MAJORANT.md)
  proves the van-der-Pol-specific global Moser majorant, including the exact
  \(q=1,2\) Lie prefix, the all-orders parameter-two-jet recurrence, explicit
  map/inverse domains and tails, and the fixed primitive gauge.  Combined
  with the bound source checker, it gives
  `V2.CHART.ANALYTIC_NORMAL_FORM` a local mathematical `PASS`; the aggregate
  remains non-claim-bearing and `V2.EXACT_CHART` remains open.
- [RELATIVE_OVERFLOWING_NHIM.md](RELATIVE_OVERFLOWING_NHIM.md) proves the
  relative doubling and parameter bridge needed for the auxiliary saddle-type
  center graph at the resolved \(K_1\) corner, using the precisely restated
  classical compact boundaryless NHIM theorem.
- [FINITE_MARKED_ATLAS_DESCENT.md](FINITE_MARKED_ATLAS_DESCENT.md) proves the
  finite-atlas physical descent used by V6--V7 and records, separately, the
  still-conditional criterion for one global exact marked chart.

## Registration rule

Before a new local theorem-sized result is described as extending the source
theory, its register entry must state:

- the local claim ID and exact evidence file;
- every imported theorem or certificate, with frozen revision and hypotheses;
- all preceding local claims on which it depends;
- whether it is analytic, non-rigorous numerical, or interval-rigorous; and
- the upstream impact, which is `none` unless and until a separate upstream
  change is actually accepted.

Status changes remain governed by `CLAIM_REGISTER.md`: a provenance record by
itself proves nothing.
