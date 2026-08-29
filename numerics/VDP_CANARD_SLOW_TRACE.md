# Boundary-selected finite-parameter canard BVP

## Outcome

The formal-entry scout has now been replaced, at

\[
 (r,\epsilon)=(0.08,1),
\]

by collocation solutions of the exact finite-\(r\) central-chart field.  The
calculation uses Appendix A.2 of the published
[Vo--Doelman--Kaper paper](https://doi.org/10.1137/24M1690722) and continues
its half-orbit as the seed for an A.3-compatible, central-localized
zero-energy BVP in which \(a_2\) is an unknown.  The older endpoint-family
pseudo-arclength root is retained separately as a wrong-branch diagnostic.

The strongest honest status is

```text
COMPUTED/E1_FINITE_BOUNDARY_A3_COMPATIBLE_PRIMARY_CANDIDATE
INCONCLUSIVE_INTRINSIC_SLOW_TRACE_AND_TARGET_BRANCH_NOT_VALIDATED
```

This is a real advance over the projected formal jet: the saved entry and
central-localized candidate lie on a collocation solution of the exact
finite-\(r\) vector field and satisfy the six A.3-compatible boundary
conditions.  It is still a finite-boundary candidate, not a finite-parameter
maximal-canard result.

> **Superseded for orbit shadowing.**  A later
> [direct-IVP check](VDP_CANARD_DIRECT_SPLITTING.md) starts from the unique
> negative zero-energy root at the same frozen outer data and does not reach
> the reverser candidate: its first increasing \(p_2=0\) hit has \(q_2\) far
> from zero, and the tighter replay also fails.  The low collocation residual
> therefore does not validate a nearby IVP orbit.  This object remains useful
> as a BVP numerical seed, but is no longer classified as a reliable orbit
> candidate; the failure does not prove that a canard is absent.

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

## Strongest computed object: frozen-boundary A.3 half orbit

Freeze the outer data

\[
 u_*=16.64508336484338,
 \qquad q_*=-80,
 \qquad g_r(u)=u^2+\frac{r^2}{3}u^3.
\]

Here \(u_*\) is an explicit value taken from the previously computed A.2
half orbit; it is not recomputed as \(a_2\) varies.  For the half orbit
\(z_s=T F_{K_2}(z;r,a_2)\), the unknowns are the function \(z\) and the two
scalars \((T,a_2)\).  The six boundary conditions are

\[
 u_L=u_*,\qquad v_L=g_r(u_L),\qquad q_L=q_*,
 \qquad p_R=0,\qquad q_R=0,\qquad H_2(z_L;r,a_2)=0.
\]

Starting from the A.2 half-orbit shape and \(a_2=-1/120\), the solve gives

\[
 T=14.2905556259,
 \qquad
 a_2=-0.0083381952670,
\]

and reaches the reverser at

\[
 z_R\approx
 (-0.0006670525,0,-0.1666684089,0).
\]

The maximum boundary residual is \(5.41\times10^{-13}\), the maximum
mesh-interval RMS relative residual is \(2.00\times10^{-8}\), and the sampled
Hamiltonian drift is \(5.70\times10^{-10}\).  On the sampled open half orbit,
both \(p_2\) and \(q_2\) stay negative.  At the reverser,

\[
 p_2'=g_r(u_2)-v_2\approx0.166669>0,
\]

so \(p_2=0\) is the well-conditioned event section; \(q_2=0\) would be
nearly tangent because \(q_2'=u_2-ra_2\approx3.1\times10^{-9}\).

The order-three Appendix-C formal state at the computed \(a_2\) differs from
the endpoint by only

\[
 (1.98\times10^{-7},0,-1.45\times10^{-6},0),
\]

and

\[
 \frac{a_2+5r/48}{r^3}\approx-0.009496.
\]

Reflection gives a full reversible segment of flight time \(2T\); it is not
called a periodic orbit.  These diagnostics identify the intended
central/no-loop candidate at floating level, but do not prove intrinsic
slow-manifold membership, boundary independence, or uniqueness.

## A.2 saddle-slow seed

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

## Legacy endpoint-family wrong-branch diagnostic

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

Thus the older boundary-selected endpoint family has a numerically closed,
apparently reversible coincidence candidate.  Unlike the original formal
scout, its zero splitting is not produced by projection, but its central
endpoint shows that it follows the wrong A.2 branch for the primary canard.

## Why Issue #13 remains open

The legacy endpoint-family coincidence is not the maximal canard of Lemma
6.4.  The order-three published algebraic-canard jet has central point

\[
 (-6.67\times10^{-4},0,-0.166667,0),
\]

whereas that legacy root hits the reverser at
\((0.77309,0,0.19930,0)\).  It therefore fails the frozen central-localization
diagnostic by an \(O(1)\) margin.  This is a branch warning, not a rigorous
separation theorem, because the formal jet is asymptotic and not an interval
enclosure.

The new A.3-compatible root avoids the observed wrong-branch diagnostic, but it freezes the
outer value \(u_*\).  Independence from that choice has not been established,
so it does not by itself define the intrinsic \(W^{cu}\) trace.  A first
strict step can enclose this frozen-boundary root with CAPD multiple shooting,
using \(p_2=0\) as its terminal Poincare section.  To complete intrinsic C1
and C2 one must anchor the relevant \(W^{cu}\) disk at the equator, transport
its \(H_2=0\) trace through the K1--K2 transition, and then evaluate

\[
 S(r,a_2)=q_2\big|_{\text{first increasing }p_2=0}
\]

as a genuine two-parameter splitting on the primary no-loop branch continued
from \(\Gamma_0\).  A simple zero of this function, with
\(\partial_{a_2}S\ne0\), has not yet been enclosed.

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
