# Primary sources and dependency boundary

## RFSN-II source theory

- H. Lu, *First returns, singular exits, and action finite parts near a
  reversible Hamiltonian saddle-focus* (current flagship manuscript and
  supporting repository):
  <https://github.com/h-lu/reversible-rfsn-ii-waves>.

Import only results with an exact theorem or proposition reference, a fixed
source revision, and all hypotheses restated.  In particular, the singular
core theorem does not itself prove positive-parameter persistence of either
noncompact end.

For the Brusselator localized-profile track, the frozen source revision is
d54add098545063d5efe8f1d6f062d4cfc116a0d.  The imported result is
Proposition 8.6, specifically its verification of Definition 2.1(I2),
together with the quantitative enclosures (8.36)--(8.40).  There is no
separately numbered “symmetric homoclinic theorem” in that revision.  The
precise statement, coordinates, evidence level, and hashes are recorded in
[the core-homoclinic import note](../brusselator/CORE_HOMOCLINIC_IMPORT.md).
No two-end, action, return--exit, or coding conclusion is imported into the
Brusselator track.

## van der Pol reaction--diffusion model

- T. Vo, A. Doelman, T. J. Kaper, *Les Canards de Turing*, SIAM Journal on
  Applied Dynamical Systems (2025), DOI:
  <https://doi.org/10.1137/24M1690722>, arXiv:
  <https://arxiv.org/abs/2409.02400>.

Use the published equations for the PDE, the blow-up charts, the Hamiltonian
central problem, and the established canard/homoclinic results.  Do not infer
the exhaustive return/exit relation, action finite parts, transverse margins,
or temporal stability unless the cited result states them.

## Brusselator model

- R. Jencks, A. Doelman, T. J. Kaper, T. Vo, *Stable and Unstable
  Spatially-Periodic Canards Created in Singular Subcritical Turing
  Bifurcations in the Brusselator System*, Journal of Nonlinear Science 36,
  article 55 (2026), DOI:
  <https://doi.org/10.1007/s00332-026-10268-6>, arXiv:
  <https://arxiv.org/abs/2509.04835>.

Before a manuscript draft is opened, record the precise equations and theorem
numbers used.  The source's reversible non-Hamiltonian spatial system must not
be described as exact Hamiltonian merely because its singular core is
Hamiltonian.

The Brusselator model convention is frozen to the published open-access
version (published online 19 May 2026, 66 pages), whose downloaded PDF had
SHA-256
4bed16d16cd0e8256d6ce328c193ef9326f94142258c862eca13f5be4d862357.
The present track uses:

- equations (1.1)--(1.2) for the PDE and homogeneous state;
- equations (2.5)--(2.9) for the two spatial clocks, momenta, reverser, and
  spatial spectrum;
- equations (5.1)--(5.5) for the translation and blow-up weights; and
- equations (5.7)--(5.8) for the \(K_2\) vector field and its higher-order
  term.

The exact specialization to \(A=B=1\), including all signs and clocks, is
derived in
[the model-and-scaling note](../brusselator/MODEL_AND_SCALING.md).
Proposition 2.1 of the source paper is not used: its neighborhood of the
reversible \(1{:}1\) resonance is not stated uniformly as
\(\varepsilon=\sqrt d\to0\) along \(A=B=1\).

Two apparent typesetting errors in the published version are not imported.
Equation (5.6) writes the \(K_1\) scaling of \(V\) with \(P_1\) where the
subsequent equations require \(V_1\).  More importantly, the signs printed
in the central Hamiltonian (8.2) do not differentiate to zero along (8.1).
The present project derives the limiting first integral directly from the
core vector field and uses the independently frozen flagship convention.

## Literature work still required

A submission-level project bibliography must also cover, using primary sources:

- parameter-dependent stable/unstable manifolds in weighted spaces;
- geometric blow-up and chart matching in reaction--diffusion spatial dynamics;
- normally hyperbolic or normally expanding invariant manifolds with boundary;
- regular-singular and polyhomogeneous finite-part expansions;
- rigorous continuation of connecting orbits and invariant-manifold entry;
- Bloch/Evans stability only if temporal stability becomes a separate project.

References are to be added because they discharge a mathematical dependency or
locate novelty, not to inflate the bibliography.
