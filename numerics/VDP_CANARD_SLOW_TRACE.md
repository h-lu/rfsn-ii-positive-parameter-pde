# Boundary-selected finite-parameter canard BVP

## Outcome

The formal-entry scout has now been replaced, on the frozen slice

\[
 (r,\epsilon,a_2)=(0.08,1,-1/120),
\]

by collocation solutions of the exact finite-\(r\) central-chart field.  The
calculation follows the saddle-slow-manifold construction in Appendix A.2 of
the published
[Vo--Doelman--Kaper paper](https://doi.org/10.1137/24M1690722) and continues
the endpoint family through its reversible representative by a weighted
pseudo-arclength condition.

The strongest honest status is

```text
COMPUTED/E1_BOUNDARY_SELECTED_A2_COINCIDENCE_CANDIDATE
INCONCLUSIVE_INTRINSIC_SLOW_TRACE_AND_TARGET_BRANCH_NOT_VALIDATED
```

This is a real advance over the projected formal jet: the saved entry and
coincidence candidate lie on collocation solutions of the exact finite-
\(r\) vector field.  It is not yet a finite-parameter maximal-canard result.

## Finite-\(r\) BVP solved numerically

For \(\epsilon=1\), the translated central system is

\[
 u_2'=p_2,\qquad
 p_2'=u_2^2-v_2+\frac{r^2}{3}u_2^3,\qquad
 v_2'=q_2,\qquad
 q_2'=u_2-ra_2,
\]

with

\[
 H_2=\frac12(p_2^2-q_2^2)+(u_2-ra_2)v_2
      -\frac13u_2^3-\frac{r^2}{12}u_2^4.
\]

The outside A.2 family uses the frozen boundary \(q_2=-80\), starts on the
\(p_2\)-nullcline

\[
 v_2=u_2^2+\frac{r^2}{3}u_2^3,
\]

and terminates on \(p_2=u_2=0\).  Natural continuation in the left endpoint,
followed by continuation in terminal \(q_2\), selects the primary reversible
representative.  Reflection supplies its other half.  No formal-jet point is
inserted into this BVP.

The selected half has flight time

\[
 T_-=14.2846437516
\]

and begins at

\[
 (u_2,p_2,v_2,q_2)
 \approx(16.64508336,-2.25634508,286.89702279,-80).
\]

Its descending crossing of the fixed normally hyperbolic comparison section
\(u_2=16\) is

\[
 E_{\mathrm{A.2}}
 \approx(16,-2.23427997,264.61740703,-75.31620241).
\]

This is a branch-identified finite-boundary saddle-slow entry candidate.  Its
energy is \(H_2\approx-1.116\times10^{-4}\), so it is not the desired
zero-energy trace.

## Pseudo-arclength and the zero-energy BVP candidate

Directly varying an endpoint at the reversible representative is singular.
The code therefore solves the linearized BVP for the endpoint-family tangent,
normalizes it in the scaled \((u_2,p_2,v_2,q_2,T)\) norm, and adds an integral
pseudo-arclength equation.  Writing

\[
 g_r(u)=u^2+\frac{r^2}{3}u^3,
 \qquad u_*=16.6450833648,
\]

the continued full-orbit family holds

\[
 u_L=u_*,\qquad v_L=g_r(u_L),\qquad v_R=g_r(u_R),
 \qquad q_L+q_R=0,
\]

and treats the flight time \(T\) and the remaining endpoint data as unknowns.
The refined candidate replaces the pseudo-arclength equation by

\[
 H_2(z_L)=0.
\]

In particular, it does not fix \(q_L=-80\) and it does not impose
\(p_L+p_R=0\); the latter parity, together with the remaining reversible
endpoint relations, is checked a posteriori.  This continuation brackets
\(H_2=0\):

\[
 H_2=-0.0230847\quad(T=24.28753),\qquad
 H_2= 0.0285804\quad(T=24.06504).
\]

Imposing \(H_2=0\) as a boundary condition in a refined collocation solve gives

\[
 T=24.1783767041,
\]

with maximum interval RMS relative residual \(1.99\times10^{-8}\), sampled
Hamiltonian drift below \(10^{-9}\), and observed reversibility residual below
\(10^{-15}\).  Its
\(u_2=16\) entry is

\[
 E_0\approx(16,-2.23427993,264.61740701,-75.31620092).
\]

The collocation orbit reaches its first increasing \(p_2=0\) hit after this
entry at

\[
 (u_2,p_2,v_2,q_2)
 \approx(0.77309182,0,0.19929822,0),
 \qquad p_2'\approx0.39936.
\]

Thus the boundary-selected BVP has a numerically closed, apparently reversible
coincidence candidate.  Unlike the old scout, its zero splitting is not
produced by projecting a formal entry.

## Why Issue #13 remains open

The coincidence above is not automatically the maximal canard of Lemma 6.4.
The order-three published algebraic-canard jet has central point

\[
 (-6.67\times10^{-4},0,-0.166667,0),
\]

whereas the computed root hits the reverser at
\((0.77309,0,0.19930,0)\).  It therefore fails the frozen central-localization
diagnostic by an \(O(1)\) margin.  This is a branch warning, not a rigorous
separation theorem, because the formal jet is asymptotic and not an interval
enclosure.

More importantly, Appendix A.2 selects a finite-boundary representative.  To
complete C1 and C2 one must still isolate the symmetry-breaking slow-sheet
direction, prove or validate independence from that finite boundary, transport
the resulting \(H_2=0\) trace to \(u_2=16\), and then evaluate

\[
 S(r,a_2)=q_2\big|_{\text{first increasing }p_2=0}
\]

as a genuine two-parameter splitting.  A simple zero of this function, with
\(\partial_{a_2}S\ne0\), has not yet been computed or enclosed.

Consequently this record does not classify \(a_2=0\), enclose the remainder in
\(a_{2,c}(r)\), or connect the frozen high-winding target to a canard.

## Reproduction

```bash
python3 -B numerics/vdp_canard_slow_trace.py
python3 -B -m unittest numerics.test_vdp_canard_slow_trace -v
```

The machine-readable outputs are

- `numerics/results/vdp_canard_slow_trace/fixed_r_candidate.json`;
- `numerics/results/vdp_canard_slow_trace/fixed_r_candidate.npz`.
