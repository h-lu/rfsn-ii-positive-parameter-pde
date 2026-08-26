## Objective

Prove, for \(A=B=1\) and all sufficiently small \(d>0\), a symmetric
homoclinic orbit of the full Brusselator stationary spatial system that remains
in the positive-concentration region and hence gives a localized stationary PDE
profile.

This is the first, relatively short model-level application.  It is not an
exact-action or all-winding theorem.

## Proof obligations

- [ ] Freeze the PDE, the fast spatial coordinate, \(r=d^{1/4}\), and every
      blow-up transformation.
- [ ] State the transverse core homoclinic result imported from the flagship
      repository, including the fixed energy/parameter normalization.
- [ ] Prove parameter-dependent stable and unstable manifolds with uniform
      weighted tail estimates.
- [ ] Formulate the reversible matching as an intersection with
      \(\operatorname{Fix}\mathcal R\) and prove its derivative is invertible.
- [ ] Apply the implicit-function theorem uniformly for \(0<r\le r_0\).
- [ ] Rescale to the original PDE and prove localization at both spatial
      infinities.
- [ ] Prove \(u_d,v_d>0\) along the entire orbit.
- [ ] Prove the claimed \(d^{1/4}\) width, \(d^{1/2}\) activator amplitude, and
      \(d\) inhibitor amplitude estimates.
- [ ] State explicitly that temporal stability is not proved.

## Acceptance

Claims B1 and B2 may be changed to **Proved** only when every item above is
discharged in a written proof.  Numerical continuation alone is insufficient.

## Stop or reduce scope if

The matching determinant is not uniformly separated from zero, the orbit
leaves the positive-concentration region, or uniform full-system tails cannot
be proved.  Report the maximal parameter subrange actually established; do not
move a failed preselected range merely to obtain a positive outcome.
