# V4 future-staying graph slice at the v2 center

At the fixed point

\[
 (r,a_2,\epsilon)=(3/200,0,1),
\]

the matched algebraic centerline reaches the outer seam `Q=25` at
`beta=2.7385502869454753e-6`.  This computation resolves the three-point
slice with beta offsets `(-1e-6,0,1e-6)`.  It is
`COMPUTED/E1_NON_RIGOROUS_WITH_QA`, not an interval validation of V4.

## Construction

The old finite-horizon calculation imposed the artificial condition
`alpha(Q_end)=0`.  Here both numerical formulations instead use the root of
the exact normal equation `alpha_dot=0` at the terminal cut.  That nullcline
has the correct `alpha -> 0` boundary limit, while remaining explicitly only
an asymptotic terminal model at finite `Q`.

1. Positive-`pi` collocation was continued across the three beta values on
   the predeclared horizon ladder `Q_end=(60,100,200)`.
2. An independent positive-`pi` initial-alpha shooting solve used the frozen
   short window `25 <= Q <= 25.002` and the same terminal nullcline.  The
   shooting bracket and all tolerances were fixed before the run.

The three horizon values of `Gamma(25,beta)` differ by at most
`2.965e-21`.  Shooting and the longest collocation agree at the seam within
`2.838e-14`, and their full common `(beta,alpha)` arrays agree within
`3.609e-11`.

## Geometry checked on the slice

- exact outer-energy residual: at most `2.220e-16`;
- minimum positive-`pi` margin: `1.115e-4`;
- clearance from the fixed sampled `|beta|,|alpha| <= 1e-5` faces:
  `6.261e-6`;
- minimum sampled inward/exit face margin: `8.916e-7`;
- fixed-energy graph invariance residual: `5.061e-20`;
- maximum tangent logarithmic rate: `1.247e-6`;
- minimum normal quotient rate: `0.9797991`;
- minimum third-order bunching proxy `lambda_n-3 lambda_t`: `0.9797953`.

The last four rates are Euclidean fixed-energy slice proxies computed from
the exact V4 Jacobian and the numerically reconstructed tangent plane.  They
are useful evidence that this selected slice lies in the geometry used by
V4, but they are not uniform intrinsic cocycle bounds on the theorem's full
three-dimensional base.

## Scope

This closes one concrete numerical gap: the matched seam now lies on a
horizon-converged, independently reproduced future-staying graph *slice*,
rather than only on a single `alpha(Q_end)=0` proxy.  It does not establish
the maximal graph, local uniqueness, the non-explicit uniform corridor,
mixed state/parameter regularity, infinite-end asymptotics, or the Issue #7
parameter-box theorem.

Reproduce and check with:

```bash
python3 -m numerics.vdp_v4_future_graph_slice
python3 -m unittest numerics.test_vdp_v4_future_graph_slice -v
```

The raw arrays and machine-readable QA are in
`numerics/results/vdp_v4_future_graph_slice_v2/`.
