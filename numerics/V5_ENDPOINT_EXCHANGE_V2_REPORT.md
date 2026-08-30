# V5 endpoint adjoint and matching derivative at the v2 center

This computation evaluates the endpoint mechanism of V5(49)--(58) at

\[
 (r,a_2,\epsilon)=(3/200,0,1).
\]

It is bound to the energy-preserving matched centerline and the passing,
finite-`Q` V4 future-staying graph proxy.  Its status is
`COMPUTED/E1_NON_RIGOROUS_WITH_QA`: it is one floating-point object, not the
uniform positive exchange or uniqueness assertion proved in V5.

## Endpoint row and transport

On the three predeclared beta points at the outer seam `Q=25`, a quadratic
fit gives

\[
 \partial_B\Gamma=0.010201028954390597.
\]

The first audit of this calculation exposed a missing direction: a fixed-H
slice cannot determine the full V5 conormal.  The corrected calculation
differentiates the positive-`pi` two-point BVP, including its terminal
normal-nullcline equation, at fixed seam beta.  It gives

\[
 \partial_H\Gamma=6.428815898784465\times10^{-16}.
\]

The sensitivity BVP has maximum RMS residual `2.62e-16`; its boundary
residual is `5.60e-30`.  A separate symmetric finite difference agrees to
relative error `8.74e-8`.  Thus the full scaled row
`L_o=dA-Gamma_B dB-Gamma_H dH`, normalized by
`L_o(partial_A)=1`, annihilates both fitted graph tangents (in beta and in
energy) to `4.97e-15` and zero, respectively.  It is pulled through the
exact V5(37) interface and then
backward along the saved resolved-`K1` centerline.  The raw adjoint gains a
logarithmic norm of `93162.24`, so direct floating-point transport would
overflow.  The archived calculation transports the same line in two
projective representations:

- unit covector plus logarithmic scale;
- a fixed-component ratio chart plus logarithmic scale.

Their maximum directional difference is `9.37e-9`; their maximum log-scale
difference is `7.49e-9`.  The exact K1 energy column agrees with two finite
differences to relative error `1.59e-8`.  After the exact fixed-`U` V5(38)
pullback, now including `dH` from V5(28), the
intrinsic V5(54) row pairs with the central flow at relative size
`4.54e-18`.

The singular endpoint identity is also evaluated directly:

\[
 \ell_+\mathcal T_+=1.64\times10^{-16}.
\]

This is the V5(50) compatibility vanishing.  It is deliberately recorded
separately from the exchange coefficient.

## Directed Jost exchange

The frozen Jost solutions are integrated in the paper's universal central
clock to `t_c=2 sqrt(3M)=4 sqrt(3)`, with symplectic row

\[
 \psi=\omega(\mathbf s,\cdot)
     =(s_P,-s_U,-s_Q,s_V).
\]

The immutable identities are recovered as

\[
 B_2B_3=6\sqrt3,
 \qquad
 \psi(\mathbf u)=24B_2B_3=144\sqrt3
                 =249.4153162899183,
\]

with pairing drift `1.05e-12` along the numerical Jost integration.  The
positive-parameter row is normalized on the frozen section-tangent Jost
normal, exactly as frozen in the configuration.  Its pairing with the
declared growing continuation is

\[
 L_{c,\mu}^{J}(\mathbf u_\mu)=249.4535908216958>0,
\]

only `0.01535%` from the frozen comparison.  The normalized row has cosine
`0.9999999962` with the frozen Jost row; this close agreement is lost if the
energy direction is omitted.  This remains a center-point floating exchange
candidate for the finite-`Q=200` graph proxy; using the fixed-universal-chart
continuation here does not identify the maximal graph or supply a
parameter-uniform continuation theorem.

## Source-phase/flight-time derivative

For the matching operator `(g_tilde(y(phi,t)), h_c(y(phi,t)))`, the
flow-constant target extension gives the triangular V5(58) derivative

\[
 D_{(\phi,t)}\mathcal M=
 \begin{pmatrix}
  1.525280577459381 & 0\\
  963.9509955168572 & -1.1543688668786538
 \end{pmatrix}.
\]

Thus the source incidence is nonzero, the section speed is nonzero, and

\[
 \det D\mathcal M=-1.7607364118738031
 =s_\mu\chi_\mu
\]

to relative error `6.31e-16`.  The singular values are

\[
 \sigma_{\max}=963.9528934563788,
 \qquad
 \sigma_{\min}=0.0018265793109047707,
\]

with condition number `5.277366757093609e5`.  A forward variational phase
tangent agrees with Richardson finite differences to relative error
`4.71e-11`; the exact flow time tangent agrees with its finite difference to
`3.25e-11`.

All twenty-one predeclared QA checks pass.  No section, finite-difference step,
solver tolerance, or QA threshold was altered after the formal run.

## Scope

This resolves the previously missing *full-energy center-point numerical
object*: an outer-anchored adjoint line, a Jost-normalized positive exchange
candidate, and an invertible two-variable matching derivative using the
paper's chart and clock crosswalk.  It does not identify the finite-horizon
proxy with the maximal graph, validate the full graph tube or mixed parameter
jets, or prove a uniform exchange lower bound, an inverse bound over a
parameter box, nonlinear uniqueness, or the Issue #7 theorem.

Reproduce and check with:

```bash
python3 -m numerics.vdp_v5_endpoint_exchange
python3 -m unittest numerics.test_vdp_v5_endpoint_exchange -v
```

Machine-readable diagnostics and arrays are in
`numerics/results/vdp_v5_endpoint_exchange_v2/`.
