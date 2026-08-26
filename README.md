# Positive-parameter PDE applications of the RFSN-II theory

This private repository develops two model-level applications of the
return--first-exit theory proved for the RFSN-II Hamiltonian core:

1. a positive-diffusion localized stationary pattern for the Brusselator;
2. a positive-parameter two-end exact-action theorem for the van der Pol
   reaction--diffusion system.

The projects are deliberately separate from the flagship manuscript.  A
statement proved here may be cited by a later companion paper or supplement,
but it does not alter the claims of the existing paper until it has a complete
proof and a separately audited dependency chain.

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
[Theorem V5](van-der-pol/CENTRAL_OUTER_MATCHING.md).  Every later
theorem-sized claim retains the status in the
[claim register](CLAIM_REGISTER.md).

| Workstream | First rigorous target | Structure retained | Main obstruction |
|---|---|---|---|
| [Brusselator](brusselator/README.md) | A positive-concentration, symmetric, localized stationary solution for all sufficiently small positive diffusion | Reversibility and the transverse core homoclinic | Localized-branch tail continuation and positivity are discharged in Theorem B; exact Hamiltonian action is unavailable, and temporal stability and multipulses remain separate questions |
| [van der Pol](van-der-pol/README.md) | A positive-parameter exhaustive high-winding return/first-exit theorem with two action finite parts | Exact Hamiltonian structure, selected transverse homoclinic, compact central first-hit arrangement, a genuine positive pole with action finite part, and a matched normally expanding positive outer tail | Constructing the outer algebraic action finite part with mixed \(C^2\) control and cut-independent exact composition |

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

## Repository map

- [Brusselator programme](brusselator/README.md)
- [van der Pol programme](van-der-pol/README.md)
- [Research contract](RESEARCH_CONTRACT.md)
- [Claim register](CLAIM_REGISTER.md)
- [Primary sources](references/PRIMARY_SOURCES.md)

## Initial work queue

- [#1: Brusselator localized stationary profile](https://github.com/h-lu/rfsn-ii-positive-parameter-pde/issues/1)
- [#2: van der Pol Hamiltonian bridge and compact persistence](https://github.com/h-lu/rfsn-ii-positive-parameter-pde/issues/2)
- [#3: positive-parameter pole and action finite part](https://github.com/h-lu/rfsn-ii-positive-parameter-pde/issues/3)
- [#4: central--outer matching theorem](https://github.com/h-lu/rfsn-ii-positive-parameter-pde/issues/4), the decisive mathematical go/no-go task
- [#5: outer algebraic action finite part](https://github.com/h-lu/rfsn-ii-positive-parameter-pde/issues/5)
- [#6: exhaustive two-end theorem](https://github.com/h-lu/rfsn-ii-positive-parameter-pde/issues/6)
- [#7: rigorous validation](https://github.com/h-lu/rfsn-ii-positive-parameter-pde/issues/7), deliberately deferred until the analytic statements are frozen

The source theory remains in
[`h-lu/reversible-rfsn-ii-waves`](https://github.com/h-lu/reversible-rfsn-ii-waves).
This repository imports only explicitly cited results from it; it does not copy
or silently strengthen them.
