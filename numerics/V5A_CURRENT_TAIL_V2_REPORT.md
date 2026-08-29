# V5A finite-`Q` tail on the current v2 matched orbit

This computation supplies the previously missing V5A numerical object on the
energy-preserving matched centerline at

\[
 (r,a_2,\epsilon)=(3/200,0,1).
\]

Its evidence status is `COMPUTED/E1_NON_RIGOROUS`.  It evaluates the exact
common-coordinate densities from V5A(9), a real reference tail, and finite
cut/reference/gauge balances.  It does not prove the improper limits in
V5A(12).

## Same physical cut and orbit binding

The archived outer leg contains a node nearest the predeclared target
`Q=100`; the actual saved cut is

\[
 Q_*=100.17114220546152.
\]

From this cut to `Q_end=200`, three members of the same exact finite-energy
outer BVP are resolved in the positive-`pi` chart:

- the actual saved arrival label;
- the V5A reference label `beta(Q_*)=0`;
- a nonzero alternate reference halfway between them.

The energy used is the matched orbit's saved near-zero value
`1.88303e-25`, not an assertion of exact arithmetic zero.  The reconstructed
actual member agrees with all 219 archived outer nodes after `Q_*` to
`1.78e-17` in `(beta,alpha)` and `2.23e-16` in `(chi,pi)`.  The largest BVP
RMS residual is `2.00e-9`, the largest energy residual is `5.56e-17`, and
`pi` stays above `1.47e-4`.

## Finite reference subtraction

On the common physical coordinate, the exact densities are

\[
 \mathcal T={\delta\over2\Pi}Q^{-1/2},\qquad
 \mathcal A=-{\Chi^2\over2\Pi}Q^{3/2}
              +{\epsilon\Pi\over2}Q^{-1/2}.
\]

The actual/reference difference is concentrated in the resolved inflow layer
immediately after `Q_*`.  At `Q=200`, the finite-cut values are

\[
 R_{\mathsf x}=-1.13057889765\times10^{-7},\qquad
 R_{\mathsf A}=2.14446326497.
\]

For comparison, the raw reference action accumulated on the same finite
interval is `-2.72782153453e8`.  The last two grids contain 51,201 and
102,401 union nodes; their length and action changes are respectively
`1.21e-14` and `2.30e-7`.  After the first `0.01` units of `Q`, the remaining
changes are `6.38e-19` and `1.19e-10`.
An archive-only Simpson cross-check differs from the retained trapezoid values
by `4.04e-15` and `7.67e-8`, respectively.

These numbers show that the finite layer and the large reference
counterterm have been numerically resolved.  The apparent plateau is still
finite-horizon evidence: all tails share the artificial terminal condition
`alpha(200)=0`, so it cannot establish exponential flatness or convergence
as `Q` tends to infinity.

## Covariance checks and boundary

On the same computed tails:

- three finite cut splits close for both densities;
- insertion of the real alternate reference closes the reference cocycle;
- the exact gauge `psi=0.1 z+0.03 w` closes after its endpoint correction,
  with residual `1.02e-11`.

These are finite-grid identities.  No independent admissible compactifying
coordinate was available, so coordinate covariance is explicitly
`NOT_COMPUTED`.  Mixed parameter/label two-jets, a uniform V5 arrival
interval, removal of the terminal condition, and both improper limits remain
unresolved.  Hence `theorem_status=INCONCLUSIVE` and `claim_bearing=false`.

```bash
python3 -m numerics.vdp_v5a_current_tail
python3 -m unittest numerics.test_vdp_v5a_current_tail -v
```
