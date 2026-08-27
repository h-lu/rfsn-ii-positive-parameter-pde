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
| P2b0 | `V2.WU.H10_C0_TUBE` | A uniform \(C^0\) tube around the frozen degree-ten core graph, with a symbolically differenced parameter residual. |
| P2b0 | `V2.WU.H10_C1_TUBE` | A uniform state-\(C^1\) tube around the same graph, using a transformed tangent Riccati cone. |
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

## 4. H10-centered C0/C1 refinement for P2b

Let \(p=H_{10}\) be the frozen degree-ten core graph, put

\[
 y=s-p(u),\qquad x_0=u_1+p_1(u),\qquad
 q_\mu=\left(\frac1{4\alpha},-\frac1{4\beta}\right),
 \qquad G_\mu(x)=q_\mu n_\mu(x).
\]

In the moving frame, \(B_s=-B_u\), and the exact transformed residual is

\[
 R_\mu(u)=B_{s,\mu}p-G_\mu(x_0)
           -Dp\bigl(B_{u,\mu}u+G_\mu(x_0)\bigr).
\]

The residual dynamics are therefore

\[
 y'=B_{s,\mu}y+R_\mu(u)
 -(I+Dp)\bigl(G_\mu(x_0+y_1)-G_\mu(x_0)\bigr).
\]

Direct interval evaluation of \(R_\mu\) is forbidden because it destroys the
degree-ten core cancellations.  The executable probe must instead use

\[
 R_\mu=R_0+\Delta B_s p-\Delta G
       -Dp\bigl(\Delta B_u u+\Delta G\bigr),
 \qquad \Delta G=G_\mu(x_0)-G_0(x_0),
\]

where \(R_0\) is the exact frozen defect table.

For the scalar implementation, if \(\delta_B\) bounds both block
differences, \(F_0\) and \(F_1\) bound \(\Delta G\) and its scalar
derivative, and \(D_0,D_1\) bound the core defect and its derivative, the
probe first fixes

\[
\begin{gathered}
 X_0=R+\lVert p\rVert,\qquad X=X_0+\rho,\\
 C_q=\delta_q(1+\delta_a)+\tfrac12\delta_a,\\
 F_0=(C_q+kbX_0)X_0^2,\qquad
 F_1=2C_qX_0+3kbX_0^2,
\end{gathered}
\]

where \(k\ge\lVert q_\mu\rVert\),
\(\delta_q\ge\lVert q_\mu-q_0\rVert\), and
\(\delta_a\ge|a-1|\).  It then uses

\[
\begin{aligned}
 E_0&=D_0+\delta_B(\lVert p\rVert+dR)+(1+d)F_0,\\
 E_1&=D_1+\delta_B(2d+d_2R)+d_2F_0+(1+d)^2F_1.
\end{aligned}
\]

The two occurrences of \(\delta_Bd\) in \(E_1\) come from differentiating
\(\Delta B_sp\) and \(Dp\,\Delta B_uu\), respectively; neither may be
dropped.  Moreover the quadratic coefficient in \(\Delta G\) is
\(\lVert a q_\mu-q_0\rVert\), bounded by

\[
 \lVert q_\mu-q_0\rVert(1+|a-1|)
 +\tfrac12|a-1|,
\]

not merely by \(\lVert q_\mu-q_0\rVert\).

Before evaluating any interval bound, the runner must read the generator and
term table from the frozen flagship Git commit, rerun the exact homological
recursion over \(\mathbb Q(\sqrt2)\), and require a byte-identical generated
header.  It must also reject repeated monomials, nonpositive denominators, or
an unexpected degree.  A table hash establishes provenance but is not, by
itself, the exact invariance calculation.

Write \(d=\lVert Dp\rVert\), \(d_2=\lVert D^2p\rVert\), and, on the
complete value tube \(|x|\le R+\lVert p_1\rVert+\rho\), set

\[
 \ell=\lVert q_\mu\rVert\sup|n_\mu'(x)|,
 \qquad m=\lVert q_\mu\rVert\sup|n_\mu''(x)|,
 \qquad \kappa=\alpha-(1+d)\ell.
\]

If \(E_0\ge\sup\lVert R_\mu\rVert\), then on
\(\lVert y\rVert=\rho\),

\[
 \frac12D\lVert y\rVert^2
 \le-\rho\bigl(\kappa\rho-E_0\bigr).
\]

Thus \(m_{C^0}=\kappa\rho-E_0>0\) prevents a first exit of the
true graph, which starts at \(y=0\) at the origin.

For the derivative tube put \(K=D(H_\mu-p)\) and
\(C=q_\mu n_\mu'(x)e_1^T\), with \(x=x_0+y_1\).  Differentiating the graph
equation gives the matrix Riccati equation

\[
 \dot K=M+[B_s-(I+Dp)C]K
 -K[B_u+C(I+Dp)]-KCK.
\]

The forcing satisfies

\[
 \lVert M\rVert_F\le
 G_u:=E_1+\bigl(d_2\ell+(1+d)^2m\bigr)\rho,
 \qquad E_1\ge\sup\lVert DR_\mu\rVert_F.
\]

The rotational parts of \(B_sK-KB_u\) are skew for the Frobenius inner
product, while its real part is exactly \(-2\alpha\lVert K\rVert_F^2\).
Consequently

\[
 \frac12D\lVert K\rVert_F^2
 \le \lVert K\rVert_FG_u
 -2\kappa\lVert K\rVert_F^2
 +\ell\lVert K\rVert_F^3.
\]

The frozen values are

\[
 \rho=\frac1{200000},\qquad \eta=\frac3{10000},
\]

and the second no-first-exit gate is

\[
 m_{C^1}=2\kappa\eta-G_u-\ell\eta^2>0.
\]

Along every nonzero unstable orbit, backward time tends to the origin and
\(y,K\to0\), because both graphs have the same value and tangent plane there.
P2a supplies the analytic germ, its finite smooth continuation, and the cone
that keeps the \(u\)-projection nonsingular on the complete radial disk.  The
two nested no-first-exit arguments therefore apply to that already-existing
true graph.  A pass proves

\[
 \lVert H_\mu-H_{10}\rVert_2\le5\cdot10^{-6},\qquad
 \lVert D H_\mu-DH_{10}\rVert_{2\to2}
 \le\lVert\cdot\rVert_F\le3\cdot10^{-4}
\]

on the complete bridge, plus the reversible stable analogue.  It still does
not bound \(D_b^2,D_b^3,D_\mu,D_\mu^2\), their mixed derivatives, or the
weighted half-orbit constants.  Therefore neither `V2.WU.JETS` nor its parent
passes at P2b0.

The radii, rational budgets, imported term-table hashes, and exact formula
strings are preregistered in
[`config/vdp_p2_h10_c01_v1.json`](config/vdp_p2_h10_c01_v1.json).

## 5. What P2a and P2b0 do and do not settle

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

## 6. Homoclinic, chart, and atlas boundaries

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
