# Brusselator: positive-diffusion localized stationary pattern

## Proved theorem

The precise literature positioning is recorded in
[LITERATURE_AND_CONTRIBUTION_AUDIT.md](LITERATURE_AND_CONTRIBUTION_AUDIT.md):
localized Brusselator states and fixed-diffusion Turing homoclinics are not
new. The contribution claimed here is the singularly uniform continuation
along \(A=B=1\), \(d\to0^+\), together with the quantitative positive-profile
conclusions below. The status and current public-access limitation of the
computer-assisted core input are recorded in
[CORE_IMPORT_AUDIT.md](CORE_IMPORT_AUDIT.md).
The independent clause-by-clause reconstruction of the local proof is in
[PROOF_INTERFACE_AUDIT.md](PROOF_INTERFACE_AUDIT.md).

At \(A=B=1\), [Theorem B](LOCALIZED_PROFILE_PROOF.md) proves that for every
sufficiently small positive diffusion parameter \(d\), the stationary spatial
system has a symmetric homoclinic orbit that remains in the
positive-concentration region.  In the original PDE variables this orbit
gives a localized stationary profile converging to the homogeneous state at
both spatial infinities.

With \(r=d^{1/4}\), the expected leading scales are

\[
u_d(x)=1+r^2U_r(x/r),\qquad
v_d(x)=1+r^4V_r(x/r),
\]

so that the central connected half-height width is of order \(d^{1/4}\), the
activator amplitude is of order \(d^{1/2}\), and the inhibitor amplitude is
of order \(d\). Theorem B proves these powers uniformly, with nonzero limiting
amplitude coefficients, uniform exponential tails, and central connected
half-height widths \(\Theta(d^{1/4})\).

## Proof architecture

1. Derive the stationary four-dimensional reversible system from the PDE.
2. Write the weighted blow-up in which the zero-parameter central system is the
   RFSN-II Hamiltonian core.
3. Import the rigorously transverse symmetric core homoclinic with its exact
   hypotheses and parameter normalization.
4. Establish smooth positive-parameter stable and unstable manifolds in a
   weighted space, including uniform exponential tails.
5. Solve the intersection of the unstable manifold with the reverser fixed set
   by the implicit-function theorem.
6. Rescale back to the PDE and prove localization and positive concentrations.

The positive-parameter Brusselator spatial system is not treated as an exact
Hamiltonian system.  No claim involving the flagship paper's generating
function or exact-action cocycle is permitted in this track.

## Acceptance checks

- The PDE convention and the definition of \(d\) agree with the cited source.
- The scaling from physical space to the central chart is invertible for every
  fixed \(d>0\).
- The matching determinant stays nonzero on an existential continuation
  neighborhood; no explicit positive-\(d\) interval is certified here.
- Tail estimates hold in the full positive-parameter system, not only at the
  singular core.
- Positivity is proved for both concentrations along the whole orbit.
- The theorem says stationary existence only; temporal stability is absent
  unless separately proved.

## Later, separate questions

After the localized-profile theorem, one may study a fixed finite collection
of multipulses or finite-winding patterns.  An all-winding theorem would require
a new return/first-exit theory for reversible non-Hamiltonian four-dimensional
systems and is not part of the first milestone.
