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

No positive-parameter application theorem is claimed as proved at repository
creation.  The equations and candidate scalings below are research inputs;
each theorem-sized claim remains **Proposed** in the
[claim register](CLAIM_REGISTER.md) until its proof obligations are discharged.

| Workstream | First rigorous target | Structure retained | Main obstruction |
|---|---|---|---|
| [Brusselator](brusselator/README.md) | A positive-concentration, symmetric, localized stationary solution for all sufficiently small positive diffusion | Reversibility and the transverse core homoclinic | Uniform weighted-tail continuation and positivity; exact Hamiltonian action is unavailable |
| [van der Pol](van-der-pol/README.md) | A positive-parameter exhaustive high-winding return/first-exit theorem with two action finite parts | Reversible exact Hamiltonian structure | Matching the central chart through the intermediate chart to the outer algebraic end |

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
