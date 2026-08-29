# V4 future-staying graph slice at the v2 center

At the fixed point

\[
 (r,a_2,\epsilon)=(3/200,0,1),
\]

the current axis/log(`Pi`) replay of the matched algebraic centerline reaches
the outer seam `Q=25` at
`(beta,alpha)=(2.7385502869454787e-6,2.738675286945456e-6)`.  This
computation resolves the three-point slice with beta offsets
`(-1e-6,0,1e-6)`.  It is
`COMPUTED/E1_NON_RIGOROUS_WITH_QA`, not an interval validation of V4.

## Input replay update

The first slice run was bound to the superseded centerline artifacts with
`H=2.1287391499046257e-14` and seam
`beta=2.7385502869454753e-6`.  The centerline was subsequently replayed in
exactly conjugate axis/log(`Pi`) coordinates, giving
`H=1.6531401306609465e-14` and seam
`beta=2.7385502869454787e-6`.  The input JSON/NPZ hashes, seam, and energy in
the frozen slice configuration now bind this replay.

No beta offset, horizon, common cut, terminal model, solver tolerance, or QA
threshold was changed.  Because the outer energy is `E=r^6 H` here, it moved
only from `2.4247669379382373e-25` to `1.883029930080984e-25`.  The largest
raw-array changes relative to commit `b87d806` were `2.7483e-17` in shooting
`alpha`, `2.1073e-13` in the rate/bunching array, and at most
`1.4824e-20` in collocation `(beta,alpha)`.  All pre-existing twelve QA
decisions stayed `true`.  The machine-readable result and NPZ record
old/current headline metrics and their differences.

The subsequent audit represented by the present version adds one new QA
threshold only: it binds the centerline's seam `alpha` and checks its
coincidence with the computed graph.  It does not alter the numerical solve.

## Construction

The old finite-horizon calculation imposed the artificial condition
`alpha(Q_end)=0`.  Here both numerical formulations instead use the root of
the exact normal equation `alpha_dot=0` at the terminal cut.  That nullcline
has the correct `alpha -> 0` boundary limit, while remaining explicitly only
an asymptotic terminal model at finite `Q`.

1. Positive-`pi` collocation was continued across the three beta values on
   the predeclared horizon ladder `Q_end=(60,100,200)`.
2. An algorithmically distinct positive-`pi` initial-alpha shooting solve
   used the frozen short window `25 <= Q <= 25.002` and the same terminal
   nullcline.  The shooting bracket and all tolerances were fixed before the
   run.  It shares the exact field, coordinate transforms, and terminal
   evaluator with the collocation code, so this is a cross-method check rather
   than an independent implementation.

The three horizon values of `Gamma(25,beta)` differ by at most
`5.506e-21`, which is at double-precision rounding scale here and is recorded
only as "below numerical resolution," not as a resolved convergence rate.
Shooting and the longest collocation agree at the seam within
`2.838e-14`, and their full common `(beta,alpha)` arrays agree within
`3.609e-11`.

The bound matched centerline has
`alpha(25)=2.738675286945456e-6`; its difference from the longest-horizon
graph value is `-1.694e-21`.  This coincidence is now an explicit QA item.

## Geometry checked on the slice

- exact outer-energy residual: at most `2.220e-16`;
- minimum positive-`pi` margin: `1.115e-4`;
- clearance from the fixed sampled `|beta|,|alpha| <= 1e-5` faces:
  `6.261e-6`;
- minimum sampled inward/exit face margin: `8.916e-7`;
- fixed-energy graph invariance residual: `5.209e-20`;
- maximum tangent logarithmic rate: `1.247e-6`;
- minimum Euclidean orthogonal-quotient rate: `0.9797991`;
- minimum third-order bunching proxy `lambda_n-3 lambda_t`: `0.9797953`.

The last four rates are desingularized-`tau` Euclidean fixed-energy slice
proxies computed from the exact V4 Jacobian and the numerically reconstructed
tangent plane.  They are useful evidence that this selected slice lies in the
geometry used by V4, but they are not uniform intrinsic cocycle bounds on the
theorem's full three-dimensional base.

## Scope

This closes one concrete numerical gap: the matched seam agrees, within the
stated floating tolerance, with a terminal-insensitive cross-method
future-staying graph *slice*, rather than only with a single
`alpha(Q_end)=0` proxy.  It does not establish the maximal graph, local
uniqueness, the non-explicit uniform corridor, mixed state/parameter
regularity, infinite-end asymptotics, or the Issue #7 parameter-box theorem.

Reproduce and check with:

```bash
python3 -m numerics.vdp_v4_future_graph_slice
python3 -m unittest numerics.test_vdp_v4_future_graph_slice -v
```

The raw arrays and machine-readable QA are in
`numerics/results/vdp_v4_future_graph_slice_v2/`.
