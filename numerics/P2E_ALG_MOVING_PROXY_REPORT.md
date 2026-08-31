# P2e sampled algebraic BVP root chain

**Status:** `COMPUTED/E1`, `mathematical_status=INCONCLUSIVE`,
`claim_bearing=false`.

This calculation separates two objects that must not be conflated.  The V2
finite algebraic gate carries the fixed transported label
\(\phi_{\rm a}^0\).  A later V5 source-to-graph coincidence would instead
select a parameter-dependent phase.  Here we report only 17 separately
corrected floating roots of a finite-horizon algebraic BVP on a predeclared
center-to-corner path.  They do not alter or complete the fixed-label V2 gate
cover, and they do not identify the roots with the V5 branch.

## Computation

At node \(k=0,\ldots,16\), the parameters lie on the straight path

\[
 \mu_k=(3/200,0,1)+\frac{k}{16}
 ((1/100,-1/4,4/5)-(3/200,0,1)).
\]

Each solve uses the existing energy-preserving solver with its default BVP
state initialization and the frozen `E1` phase seed

\[
 \phi_{\rm seed}=\phi_c+\phi_r(r-0.015)+\phi_{a_2}a_2
 +\phi_\epsilon(\epsilon-1)+5.76(r-0.015)a_2.
\]

The three axial coefficients are the centered finite-difference phase
quotients archived in `axis_continuation.json`.  The cross coefficient
`5.76` is an empirical convergence seed selected during the corner scout,
not a derived sensitivity.  The entire formula only initializes the
corrector; it enters neither the BVP equations nor the QA acceptance tests.

The solver starts on the floating nonlinear
unstable graph, reaches the first central section \(U=-4\), and solves the
central--\(K_1\)--outer matching equations for source phase and a numerical
energy coordinate.  Its six rows are the three central--\(K_1\) state seams
\((\Pi,\Omega,q_1)\), the two \(K_1\)--outer seams, and the finite-horizon
outer terminal equation.  At the two endpoints only, a separate V4 graph
solve reuses the same
exact positive-\(\pi\) outer-equation implementation with the exact
\(\dot\alpha=0\) terminal nullcline at
\(Q_{\rm end}=40,60,80,100\).  It is a horizon and boundary-condition
cross-check, not an independent implementation replay.

On the resolved \(K_1\) leg,

\[
 U=ra_2-(r_1/r)^2,
 \qquad
 P=-\epsilon^{1/4}\sigma^{-1}\Pi,
 \qquad
 Q=-\epsilon^{1/4}\sigma^{-3}q_1,
 \qquad \sigma=r/r_1.
\]

Thus positive \(\Pi\), positive \(q_1\), and positive \(r_1\)-speed give a
direct numerical route from \(U=-4\) to the declared algebraic level
\(U=-400/23\), without unstable long forward shooting in the central chart.

## Results

All 17 bottom-level BVP QA bundles pass.  The largest adjacent corrected-root
phase step is \(1.3284338121\times10^{-3}\).  The old center initialization
bracket is recorded at every node as a diagnostic only; leaving it is not a
failure criterion for these separately seeded solves.

| endpoint | corrected source phase | phase minus fixed V2 midpoint | terminal \(P\) | terminal \(Q\) |
|---|---:|---:|---:|---:|
| \((3/200,0,1)\) | 5.756767223285 | \(7.583\times10^{-5}\) | -2.404777 | -83.808187 |
| \((1/100,-1/4,4/5)\) | 5.742275509159 | \(-1.442\times10^{-2}\) | -2.406634 | -83.762102 |

At the second endpoint—the corner where the distinct fixed-phase interval
representation is presently inconclusive—an unidentified finite-horizon
algebraic BVP root survives: its resolved route has positive \(\Pi,q_1\),
negative \(P,Q\), and reaches \(U=-400/23\).  The endpoint K1 checks pass,
and the four finite-horizon V4 seam values agree with the matched seam to
floating resolution at both endpoints.

This is a `SAMPLED_FLOATING_ROOT_CHAIN_CANDIDATE`, not numerical branch
continuation.  Because every root is corrected separately from a
data-informed seed, the samples cannot exclude a fold or a jump to another
root between nodes.  In particular, they do not identify one V5 branch, prove
that the corner root is the V5 incidence root, enclose that root, identify the
maximal V4 graph, or provide an Issue #7 certificate.  The V4 endpoint check
also shares the outer-equation implementation, so it is a boundary-condition
cross-check rather than an independent replay.

Reproduce and test with:

```bash
python3 -m numerics.vdp_p2e_alg_moving_proxy
python3 -m unittest numerics.test_vdp_p2e_alg_moving_proxy -v
```
