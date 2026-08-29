# Finite-\(r\) invariant-graph scout: numerical STOP

## Result

The first direct physical graph experiment for Issue #13 C1 stopped without
an intrinsic entry or \(a_2\) tangent.  Its status is
`STOP_GRAPH_PDE_RESIDUAL_AND_NEWTON_CONDITIONING`, with
`claim_bearing=false`.  This is **not** evidence that \(W^{cu}\) fails to
exist.

The frozen ansatz is

\[
 p=P(u,q),\qquad v=V(u,q),
\]

for the physical fast system at \(\epsilon=1\).  Invariance requires

\[
 P_uP+P_q\delta(u-a)=f(u)-V,
 \qquad
 V_uP+V_q\delta(u-a)=\delta q,
 \quad f(u)=u^3/3-u.
\]

Before the first solve, two overlapping Chebyshev rectangles were frozen:

| rectangle | \(u\) range | \(q\) range | grid |
|---|---:|---:|---:|
| `outer_wide` | \([1.075,1.14]\) | \([-0.05,-0.03]\) | \(29\times25\) |
| `outer_inner` | \([1.085,1.125]\) | \([-0.046,-0.033]\) | \(25\times23\) |

Their common interior contains the target section
\(u=1+r^2u_2=1.1024\), \(u_2=16\), and the frozen negative-\(q\) bracket.
Both are away from the singular fold: the minimum of \(f'(u)=u^2-1\) is
respectively \(0.155625\) and \(0.177225\).  The finite normal-gap diagnostics
at the best iterates are also positive, approximately \(0.3764\) and
\(0.4095\).  Normal hyperbolicity was therefore not the failing gate.

## Stopping diagnostics

The Chebyshev Fraser--Roussel iteration initially reduces the collocation
residual, then develops a high-frequency instability:

| rectangle | best iteration | best invariance \(L^\infty\) residual | frozen stop |
|---|---:|---:|---:|
| `outer_wide` | 21 | \(4.2371261\times10^{-6}\) | \(2\times10^{-9}\) |
| `outer_inner` | 15 | \(2.3404262\times10^{-6}\) | \(2\times10^{-9}\) |

At those best iterates, the collocation Newton Jacobians have LU-based
one-norm condition diagnostics of about \(6.7\times10^{16}\) and
\(2.1\times10^{16}\).  Full Newton steps increase the residual by orders of
magnitude.  A 21-level dyadic line search produces only negligible decreases
at tiny step sizes.

This is the expected numerical signature of a first-order two-dimensional
invariance PDE posed without the inflow, gauge, or global branch data needed
to select one solution.  The experiment therefore does not promote a local
collocation fixed point into the intrinsic \(W^{cu}\) branch.  In particular,
it does not compute the \(H_2=0\) intersection on \(u_2=16\), compare entries
between rectangles, or form an \(a_2\) finite-difference tangent.

No Appendix-A.2 finite-boundary orbit BVP was used, and no rectangle or
threshold was changed after seeing the result.  The frozen configuration is
[`vdp_canard_invariant_graph_scout_v1.json`](config/vdp_canard_invariant_graph_scout_v1.json),
the replay script is
[`vdp_canard_invariant_graph_scout.py`](vdp_canard_invariant_graph_scout.py),
and the saved output is
[`stop_report.json`](results/vdp_canard_invariant_graph_scout/stop_report.json).

```bash
python3 -B numerics/vdp_canard_invariant_graph_scout.py \
  --output /tmp/vdp-canard-invariant-graph-stop.json
python3 -B -m unittest numerics.test_vdp_canard_invariant_graph_scout -v
```
