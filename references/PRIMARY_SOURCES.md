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
  Applied Dynamical Systems **24**(4) (2025), 2618--2684, DOI:
  <https://doi.org/10.1137/24M1690722>, arXiv:
  <https://arxiv.org/abs/2409.02400>.

The normative source for this track is the 67-page published version
(published online 8 October 2025), not arXiv v1.  A downloaded published PDF
used for the equation audit had SHA-256
62fa70adf923f0c3323e3cc8bbcba4c502dd9afcbf7460af931bcbd17f8ac325;
the download carried a user-specific watermark, so this is an audit hash, not
a canonical publisher checksum.  The 66-page arXiv v1 file had SHA-256
9c36b663312721c3e187f1c1f57efa838dc4db9f74040ab7951fd6229dc4e30e.
The 10-page published supplement used in the same audit had SHA-256
df1b04fee7bed2ded2b6d0b1a9ae8b72491fac1b97f6be14400a0e5a63b3ab0f.

The present track uses the following published locations:

- PDE (1.1), p. 2619; physical-\(x\) systems (1.2), p. 2621, and (2.4),
  p. 2627; fast-\(y\) system, reverser, and first integral (2.6)--(2.8),
  p. 2628;
- the RFSN-II translation (6.1), p. 2642; translated field and integral
  (6.2)--(6.3), p. 2643; and blow-up/charts (6.4)--(6.6), p. 2643;
- the \(K_2\) field, Hamiltonian, and core (6.7)--(6.9), p. 2644;
- the \(K_1\) field (6.16), p. 2646;
- the \(K_1\)--\(K_2\) transitions (6.28)--(6.29), p. 2651; and
- Appendix C, pp. 2679--2681, as an independent check of the parameter
  scaling used in Lemma 6.4.

Equation (6.6) and Appendix C agree that
\[
 \widetilde a=\sqrt\epsilon\,r_2^3a_2
 =\sqrt\epsilon\,\delta^{3/2}a_2.
\]
The prose immediately after (6.6) instead prints
\(\epsilon^{3/2}\delta^{3/2}q_2\).  Both the variable and the power of
\(\epsilon\) are wrong in that sentence; the repository follows the
displayed equation and Appendix C.

The published primitive is not stated for the full stationary system.  The
repository therefore derives
\(\lambda_\delta=\epsilon p\,du-\delta^{-1}q\,dv\), the Hamiltonian sign,
and every clock factor directly in
[HAMILTONIAN_CHECK.md](../van-der-pol/HAMILTONIAN_CHECK.md).  The complete
chart crosswalk and the repository-defined cusp box are in
[MODEL_AND_CENTRAL_CHART.md](../van-der-pol/MODEL_AND_CENTRAL_CHART.md).

The source does **not** supply V2.  Proposition 2.2 is a local bounded-orbit
classification without a common \(\epsilon\)-uniform neighborhood.  Remark
5.1 explicitly places ordinary canard persistence away from the RFSN-II
degeneracy.  Proposition 6.2 treats the singular \(r_2=0\) reduced
heteroclinic problem.  Lemma 6.4 gives the maximal-canard coincidence curve
\[
 a_c=1-\frac{5\epsilon}{48}\delta^2+O(\delta^3),
\]
but the published statement gives neither the transverse homoclinic margin,
compact first-hit package, two external derivatives, nor the uniform wedge
required here.  In arXiv v1, “unique up to translations” appeared in prose
after the lemma, and “transverse intersection” appeared only in the section
roadmap; neither was a stronger clause of the lemma itself.  Both pieces of
prose were removed from the published version and are not imported.

Use the published equations for the model and charts, but do not infer a
positive-parameter end, exhaustive return/exit relation, action finite part,
transverse margin, or temporal stability unless a separate repository proof
discharges it.

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
