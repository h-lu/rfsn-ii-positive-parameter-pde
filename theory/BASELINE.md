# Frozen flagship baseline

## Identity

The external source-theory baseline used by this repository is:

| Field | Frozen value |
|---|---|
| Repository | [`h-lu/reversible-rfsn-ii-waves`](https://github.com/h-lu/reversible-rfsn-ii-waves) |
| Commit | `d54add098545063d5efe8f1d6f062d4cfc116a0d` |
| Manuscript | `papers/paper-a/manuscript/main.tex` |
| Manuscript SHA-256 | `0baf6335aad72d5893479d8876d2613671ecb8ac2ccd73664405dea4381e6a20` |
| PDF SHA-256 | `67888cf8b61b34c923cf55bd69ee41cab69493be6fc275533c8f5a074f1e96c5` |

The title frozen by the import notes is H. Lu, *First returns, singular exits,
and action finite parts near a reversible Hamiltonian saddle-focus*.

This identifier is an immutable comparison point.  “Baseline” does not mean
that the flagship repository is vendored here, that its current default branch
is interchangeable with this commit, or that later upstream changes are
automatically imported.

## Read-only boundary

The baseline may be inspected and cited, but it must not be modified from this
worktree.  This repository does not alter the flagship manuscript.  Local
files may restate an imported result only when they retain its hypotheses,
coordinate and clock conventions, evidence level, exact source location, and
frozen revision.

No conclusion proved only in this repository is part of the baseline.  In
particular, a local positive-parameter theorem is not a correction, new
edition, or strengthened version of a theorem at the frozen flagship commit.

## Imported modules

The following files are the normative dependency boundaries.  Their detailed
statements take precedence over this summary.

| Baseline module used locally | Normative import record | Permitted role | Explicitly not imported |
|---|---|---|---|
| Selected Brusselator core homoclinic and its transverse shooting derivative | [`brusselator/CORE_HOMOCLINIC_IMPORT.md`](../brusselator/CORE_HOMOCLINIC_IMPORT.md) | Base-point input for the local positive-diffusion implicit-function proof | Any positive-parameter Brusselator theorem, exact-action theorem, multipulse theorem, or temporal stability |
| Universal RFSN-II core used in Track V: saddle-focus, one selected symmetric homoclinic, and the compact central event package | [`van-der-pol/CENTRAL_CORE_IMPORT.md`](../van-der-pol/CENTRAL_CORE_IMPORT.md) | Zero-parameter input for V2 and the finite pole/algebraic gate anchors | Either noncompact positive-parameter end, positive-parameter matching, an action finite part, return--exit exhaustiveness, coding, or temporal stability |
| Model-independent high-winding, first-event, exact-action gluing, and coding modules | [`van-der-pol/RETURN_EXIT_CODING_IMPORT.md`](../van-der-pol/RETURN_EXIT_CODING_IMPORT.md) | Abstract modules applied only after the local V1--V5A hypotheses are established | The flagship's concrete singular end compactifications or an automatic positive-parameter application |
| Singular algebraic comparison hypersurface, Jost normalization, and limiting transverse source intersection | Section 2 of [`van-der-pol/CENTRAL_OUTER_MATCHING.md`](../van-der-pol/CENTRAL_OUTER_MATCHING.md) | Frozen comparison data for the locally proved resolved V5 matching problem | Persistence of the singular end, a positive-parameter outer graph, or the positive-parameter matching theorem itself |

The exact source locations and certificate hashes are maintained in those
four records.  The central-core record expressly says that this repository
checked the immutable source and hashes but did not perform an independent
machine replay of the reported interval certificates.  Freezing a hash is a
provenance guarantee; it does not by itself upgrade the evidence class.

The clause-by-clause comparison with the compressed focused manuscript,
including the decision not to repin this baseline and the two local van der
Pol theorem obligations exposed by that comparison, is recorded in
[FLAGSHIP_IMPORT_AUDIT_2026-08-28.md](FLAGSHIP_IMPORT_AUDIT_2026-08-28.md).

## Other external model sources

The van der Pol reaction--diffusion equations and blow-up charts are also
compared with Vo--Doelman--Kaper, *Les Canards de Turing*.  That is an
`EXTERNAL-MODEL-SOURCE`, not part of the flagship baseline.  The published
version, equation locations, and audit hashes are recorded in
[`references/PRIMARY_SOURCES.md`](../references/PRIMARY_SOURCES.md).  Exact
bridges derived locally from those equations remain local derivations.

## Baseline exclusions

At commit `d54add098545063d5efe8f1d6f062d4cfc116a0d`, this project does not
attribute any of the following local results to the flagship:

- the positive-diffusion Brusselator results B1--B2;
- the positive-parameter van der Pol results V1--V7 and V5A;
- the concrete positive pole, positive outer channel, or their matching;
- the local numerical atlas or any selected numerical parameter box;
- temporal stability, Turing-branch selection, canard identification for a
  computed pattern, or experimental validation.

The exact local statuses and dependencies are recorded in
[AMENDMENT_REGISTER.md](AMENDMENT_REGISTER.md) and, authoritatively, in
[`CLAIM_REGISTER.md`](../CLAIM_REGISTER.md).

## Updating the baseline

A future source revision may replace this baseline only through an explicit
repository change which records the new commit, hashes, changed theorem
statements, hypothesis differences, and the effect on every dependent local
claim.  Updating a URL, fetching a branch, or observing a newer flagship
commit does not update the baseline.

The 2026-08-28 audit inspected focused revisions `8e04dc3` and `3516a2e`
and made no baseline update.
