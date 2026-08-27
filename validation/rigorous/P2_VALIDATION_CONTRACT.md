# Issue #7 P2 validation contract

**Status:** frozen implementation contract; no P2 parent obligation is marked
complete by this document.

P2 turns the qualitative small-parameter continuation in Theorem V2 into an
explicit certificate on the target box.  The target is

\[
 B_+=[1/25,2/25]\times[-1/4,1/4]\times[4/5,6/5],
\]

but branch selection must be certified on the connected comparison bridge

\[
 B_0=[0,2/25]\times[-1/4,1/4]\times[4/5,6/5].
\]

The exact rational bridge is frozen in
[`config/vdp_bridge_v1.json`](config/vdp_bridge_v1.json).  A root proved only
on \(B_+\) need not be the selected continuation of the frozen core root and
therefore cannot discharge V2(2).

## 1. Staged obligations

The four parent obligations in `obligations.json` remain the theorem-facing
interface.  Their executable refinements are:

| Stage | Executable object | Required conclusion |
|---|---|---|
| P2a | `V2.WU.FRAME_BLOCK` | A nonsingular parameter-dependent real eigenframe, an isolating local block, and a strict difference cone on all of \(B_0\). |
| P2a | `V2.WU.COARSE_GRAPH` | True local \(W^u\) and \(W^s=\mathcal RW^u\) graphs on the radius-\(.01\) disk, Lipschitz at most one, with an explicit quadratic value bound and backward decay rate. |
| P2b | `V2.WU.JETS` | Validated \(D_b^{\le3}D_\mu^{\le2}\) graph bounds and the weighted half-orbit/tail constants actually consumed downstream. |
| P2c | `V2.HOM.BRANCH` | A gap-free parameter cover from the complete \(r=0\) anchor face through \(B_+\), with interval Newton/Krawczyk inclusion for the same selected \((\phi,T)\) branch. |
| P2c | `V2.HOM.FIRST_HIT` | No earlier nonzero hit of \(\operatorname{Fix}\mathcal R=\{P=Q=0\}\), proved by sign tubes and a final flow-box argument. |
| P2c | `V2.HOM.TRANSVERSE` | Nonzero endpoint, regular zero-energy level, sign/rank control of the phase column, and \(0\notin\det D_{(\phi,T)}M\). |
| P2c | `V2.HOM.TAILS` | Explicit \(\eta,C,T_*\) and all external derivatives through order two on both infinite tails. |
| P2d | `V2.CHART.*` | A finite exact marked saddle-chart cover, zero-energy fiber solve, exact action, overlap compatibility, and weighted-log passage bounds at a declared log-derivative order \(m\). |
| P2e | `V2.ATLAS.*` | Machine-readable physical event faces, incidences, priority, margins, connected box complex, complete first-event census, transported traces, and the three phase gaps. |

The parent `V2.WU_GRAPH` may pass only after both P2a and P2b pass.  Likewise,
partial success in P2c, P2d, or P2e does not pass its parent obligation.

## 2. Exact moving eigenframe for P2a

Write

\[
 a=1+\sqrt\epsilon r^3a_2,\qquad
 b=\frac{\sqrt\epsilon r^2}{3},\qquad
 c=2ra_2+\sqrt\epsilon r^4a_2^2,
\]

and

\[
 \alpha=\frac12\sqrt{2+c},\quad
 \beta=\frac12\sqrt{2-c},\quad
 h=2\alpha\beta=\frac12\sqrt{4-c^2}.
\]

For \(z=(u_1,u_2,s_1,s_2)\), define \(Z=T_\mu z=(U,P,V,Q)\) by

\[
\begin{aligned}
 U&=u_1+s_1,\\
 P&=\alpha u_1-\beta u_2-\alpha s_1+\beta s_2,\\
 V&=\tfrac c2u_1+hu_2+\tfrac c2s_1+hs_2,\\
 Q&=\alpha u_1+\beta u_2-\alpha s_1-\beta s_2.
\end{aligned}
\]

Direct algebra using
\(\alpha^2=(2+c)/4\), \(\beta^2=(2-c)/4\), and
\(h=2\alpha\beta\) gives

\[
 \det T_\mu=-(4-c^2),
 \qquad \mathcal R T_\mu(u,s)=T_\mu(s,u),
\]

and block-diagonalizes the linear field as

\[
 u'=\begin{pmatrix}\alpha&-\beta\\ \beta&\alpha\end{pmatrix}u,
 \qquad
 s'=\begin{pmatrix}-\alpha&\beta\\-\beta&-\alpha\end{pmatrix}s.
\]

Only the physical \(P'\) component is nonlinear.  If
\(n(U)=-aU^2+bU^3\), then

\[
 u'=B_u u+w_\mu n(U),\qquad
 s'=B_s s-w_\mu n(U),\qquad
 w_\mu=\left(\frac1{4\alpha},-\frac1{4\beta}\right),
\]

and the Euclidean operator norm used below is exactly

\[
 k_\mu=\lVert w_\mu\rVert
       =\frac1{\sqrt{4-c^2}}.
\]

The executable kernel independently clears denominators after the rational
circle parameterization
\(\alpha=(1-t^2)/(1+t^2)\),
\(\beta=2t/(1+t^2)\), and checks the block, reverser, and nonlinear-split
relations as exact polynomial identities over \(\mathbb Q[t]\).

This frame agrees with the frozen core linear coordinates at \(r=0\).  It is
used only for the local graph proof.  It is not silently identified with the
Kato-transported absolute phase required by V2(5).

## 3. Scalar interval gates for the coarse true graph

Let \(R=1/100\) and work on
\(\lVert u\rVert,\lVert s\rVert\le R\).  Put

\[
 C_0=4|a|+8|b|R,
 \qquad L_0=4|a|R+12|b|R^2.
\]

On the whole block, \(|U|\le2R\).  On a slope-one graph this sharpens to
\(|U|\le2\lVert u\rVert\), hence
\(|n(U)|\le C_0\lVert u\rVert^2\).  The executable probe must prove the
strict outward/inward face margin

\[
 m_{\rm face}=\alpha R-k C_0R^2>0
\]

and the secant difference-cone margin

\[
 m_{\rm cone}=2\alpha-4kL_0>0.
\]

Here is the precise block-extension lemma used by the certificate.  Let a
\(C^1\) vector field on
\(\{\lVert u\rVert,\lVert s\rVert\le R\}\) have a hyperbolic equilibrium at
zero and a local unstable-manifold germ tangent to the \(u\)-plane.  Suppose:

1. \(D\lVert u\rVert>0\) on \(\lVert u\rVert=R\), while
   \(D\lVert s\rVert<0\) on \(\lVert s\rVert=R\);
2. for any two block points with
   \(\lVert\Delta u\rVert=\lVert\Delta s\rVert=q>0\),

   \[
    \frac12D\bigl(\lVert\Delta u\rVert^2
                 -\lVert\Delta s\rVert^2\bigr)>0;
   \]

3. along the continued unstable germ inside the slope-one cone,
   \(D\lVert u\rVert\ge\gamma\lVert u\rVert\) for one \(\gamma>0\).

Then the component of the true unstable manifold obtained by flowing out the
germ until its first block exit is a graph over the complete closed
\(u\)-disk, has Lipschitz constant at most one, and exits only through
\(\lVert u\rVert=R\).  Indeed, the tangent of the germ starts strictly inside
the difference cone.  At a first cone-boundary contact condition 2 gives the
wrong sign for leaving it, so the cone persists.  It makes the projection to
the \(u\)-plane locally nonsingular and prevents two continued-germ points
from lying in one \(u\)-fiber.  Condition 1 excludes a first stable-face exit,
and condition 3 forces every nonzero germ orbit to reach the unstable face in
finite forward time.  The projected disk contains a neighborhood of zero,
has no interior boundary, and has its boundary on \(\lVert u\rVert=R\);
degree one of the tangent germ therefore makes its image the complete closed
disk.  This proves the stated graph extension without assuming a quadratic
bound.  Applying the reverser gives the stable graph.  The same argument is
uniform for a compact parameter family when the three margins have common
strict lower bounds.

For completeness, the first radial rate and variation-of-constants bound are

\[
 \gamma_0=\alpha-kC_0R,
 \qquad
 K_0=\frac{kC_0}{\alpha+2\gamma_0}.
\]

The frame/block probe supplies conditions 1--2.  Its interval
\(\gamma_0>0\) supplies condition 3 after the cone has first given
\(\lVert s\rVert\le\lVert u\rVert\).  Along a true unstable half-orbit,

\[
 s(t)=-\int_{-\infty}^t e^{B_s(t-\tau)}w_\mu n(U(\tau))\,d\tau,
 \qquad
 \lVert u(\tau)\rVert\le
 e^{\gamma_0(\tau-t)}\lVert u(t)\rVert .
\]

The displayed integral yields the stated \(K_0\).  The probe must first show
\(K_0<1\).  Only then may it use
\(\lVert s\rVert\le K_0\lVert u\rVert^2\), put

\[
 q=1+K_0R,\quad
 C_1=|a|q^2+|b|Rq^3,
\]

and bootstrap to

\[
 \gamma_1=\alpha-kC_1R,\qquad
 K_1=\frac{kC_1}{\alpha+2\gamma_1}.
\]

The frozen gates require \(K_1<1/4\) and \(\gamma_1>2/3\).  Consequently

\[
 \lVert H_\mu(u)\rVert\le K_1\lVert u\rVert^2,
 \qquad
 \lVert u(t)\rVert\le
 e^{(2/3)t}\lVert u(0)\rVert\quad(t\le0).
\]

The order of these tests prevents the circular use of a quadratic graph
estimate to prove the cone that creates the graph.

## 4. What P2a does and does not settle

A P2a `PASS` is a genuine uniform positive-parameter result: it supplies a
true local source disk and a rigorous value enclosure on all of \(B_0\), not
a finite-horizon approximation.  It also removes the unspecified-small-
\(r_*\) ambiguity for this local domain.

It is not yet the parent `V2.WU_GRAPH` result.  P2b must additionally validate
the state derivatives through order three, the parameter derivatives through
order two, their mixed bounds, and the constants for the parameter-dependent
weighted half-orbits.  The frozen core \(H_{10}\) table may be used as a
center for a positive-parameter residual tube, but its zero-parameter
\(10^{-20}\)/\(10^{-18}\) error bounds cannot be copied to \(B_0\).

## 5. Homoclinic, chart, and atlas boundaries

The selected homoclinic stage must use a validated true-graph source and a
gap-free interval parameter cover.  The symmetry section is codimension two,
so a simultaneous zero of \((P,Q)\), a no-earlier-hit proof, and endpoint
transversality are separate checks.  The core determinant interval is an
anchor, not a positive-parameter conclusion.

The exact-chart stage cannot infer exact symplecticity from a nearly
symplectic floating map.  It must validate the hypotheses of the frozen exact
saddle-coordinate theorem or construct a generating-function/Moser chart
with a certified analytic remainder.

Finally, the current paper text does not contain executable definitions for
the complete event cells, artificial faces, incidence/priority table, or a
numeric lower bound for \(m_0\).  P2e therefore begins by constructing and
freezing those objects in this repository.  Nine sampled pole phases or
affine proxy events cannot substitute for a connected interval cell census.

All stages retain `claim_bearing: false` until the repository's independent-
machine replay policy is satisfied.  None of P2 concerns temporal stability,
Turing selection, or canard identification.
