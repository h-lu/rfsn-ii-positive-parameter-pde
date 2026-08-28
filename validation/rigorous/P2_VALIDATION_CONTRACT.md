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
| P2bK | `V2.PHASE.KATO_INTERFACE` | A normalized Kato expanding phase, an orientation-preserving change from the algebraic graph frame, and a degree-one true source circle on the same graph disk. |
| P2c | `V2.HOM.BRANCH` | A gap-free finite parameter cover from the complete \(r=0\) anchor face through \(B_+\), with 38-dimensional interval Newton/Krawczyk uniqueness in parameter-following lifted multiple-shooting boxes and common-face identification of the same physical selected record.  No uniqueness outside the resulting lifted tube is required or asserted. |
| P2c | `V2.HOM.FIRST_HIT` | No earlier nonzero hit of \(\operatorname{Fix}\mathcal R=\{P=Q=0\}\): P2a excludes such a hit before the true source face, and dense outward-rounded sign tubes plus a final flow-box argument exclude one from that face to the selected event. |
| P2c | `V2.HOM.TRANSVERSE` | Nonzero endpoint, regular zero-energy level, sign/rank control of the phase column, and \(0\notin\det D_{(\phi,T)}M\). |
| P2c | `V2.HOM.TAILS` | Explicit \(\eta,C,T_*\) and all external derivatives through order two on both infinite tails. |
| P2c | `V2.HOM.MIDDLE_C2` | A fixed-\(\xi\), continuous-time \(C^2\) enclosure on the compact middle \([-T_*,T_*]\), including the event-time centering terms, composed with the local pre-source pieces and both infinite tails to give one explicit global weighted bound for all external derivatives through order two. |
| P2d | `V2.CHART.SYMPLECTIC_FRAME` | The normalized Kato expanding phase has an exact positive-radial reversible symplectic completion, with its sign branch and parameter two-jets fixed. |
| P2d | `V2.CHART.ANALYTIC_NORMAL_FORM` | On every member of a finite parameter cover, a convergent reversible Moser construction gives an exact symplectic chart and inverse, an exact primitive gauge, and \(\widehat H_\mu\circ\Phi_\mu^{\rm K}=h_\mu^{\rm K}(I_1,I_2^{\rm K})\) on one certified complex domain. |
| P2d | `V2.CHART.ZERO_ENERGY` | The normal-form equation \(h_\mu^{\rm K}(I_1,\nu)=0\), \(\nu=I_2^{\rm K}\), has one certified two-sided solution \(I_1=q_\mu(\nu)\) on a common nonzero action interval, with the origin branch and its first jet fixed and \(\partial_{I_1}h_\mu^{\rm K}\) uniformly positive. |
| P2d | `V2.CHART.EXACT_SECTIONS` | Incoming/outgoing section forms are exactly \(d\phi\wedge d\nu\), the primitive gauges are fixed, and the passage preserves the same transverse action \(\nu\) exactly. |
| P2d | `V2.CHART.WEIGHTED_PASSAGE` | The time and Kato-oriented phase laws, including \(\widetilde b^{\rm K}=b^{\rm K}-\beta t^{\rm K}\) and the residual \(\rho^{\rm K}-\beta\tau^{\rm K}\), have an analytic all-finite-\(m\) Cauchy-bound generator and explicit machine-usable constants through \(D_{\log\nu}^3D_\mu^{\le2}\). |
| P2d | `V2.CHART.PHYSICAL_SLIDES` | Exact auxiliary and physical faces, event-free slides, first-hit speed/uniqueness, residence-time correction, and state-\(C^3\)/parameter-\(C^2\) bounds are certified. |
| P2d | `V2.CHART.OVERLAPS` | A finite cover has common chart/inverse domains, exact-symplectic overlap gauges, signed-axis preservation, oriented-blow-up extensions, state-\(C^3\)/parameter-\(C^2\) mixed bounds, and phase-boundary degree \(+1\). |
| P2e | `V2.ATLAS.*` | Machine-readable physical event faces, incidences, priority, margins, connected box complex, complete first-event census, transported traces, and the three phase gaps. |

The parent `V2.WU_GRAPH` may pass only after both P2a and P2b pass.  Likewise,
partial success in P2c, P2d, or P2e does not pass its parent obligation.  In
particular, a finite-order almost-symplectic normal form or a certificate only
through one fixed log order cannot pass the full `V2.EXACT_CHART` parent.

The current strict design implementation passes every scoped P2c atom,
including `V2.HOM.MIDDLE_C2`, on the full bridge and obtains

\[
 T_*=11,\qquad \eta=1/5,\qquad C_{\rm hom}=71496600.
\]

The `V2.HOM.MIDDLE_C2` row is a retrospective proof-interface amendment: it
was added after the proof audit identified that infinite-tail constants alone
do not close Theorem V2(9)--(11).  It was not a preregistered claim-bearing
gate.  The narrow
[`vdp_p2_homoclinic_v1.json`](config/vdp_p2_homoclinic_v1.json) contract now
records that history explicitly as
`FROZEN_POST_STRICT_DESIGN_PRE_CERTIFICATE`.  Its local summary-certificate
checker parses the archived fixed-order strict logs and reruns only the exact
Fraction tail composition; it does not pretend that this retrospective freeze
is an independent full-grid replay.  The five atoms aggregate exactly to
`V2.HOMOCLINIC`, while the certificate remains non-claim-bearing until the
independent-machine policy is met.

The first P2d child atom has an archived formal local certificate.  The
archived P2bK result supplies the normalized expanding Kato frame; the
deterministic audit proves all 59 exact linear, symplectic, reverser,
action-sign, section, and anchor identities; and the separate formal interval
probe verifies the 20 frozen branch, conditioning, and parameter-\(C^2\)
gates on the complete \(16\times8\times4\) bridge cover.  Together these give
local mathematical `PASS` for `V2.CHART.SYMPLECTIC_FRAME`.  The clean-source
certificate
[`results/vdp_bridge_v1_p2d_symplectic_frame.json`](results/vdp_bridge_v1_p2d_symplectic_frame.json)
has integrity and mathematical status `PASS`; its final status remains
`INCONCLUSIVE`, `claim_bearing=false`, and `release_eligible=false` because
independent replay is still 1 of 2.  Separately, the other six P2d child atoms
were initially `OPEN`.  The second child,
`V2.CHART.ANALYTIC_NORMAL_FORM`, now has a local mathematical `PASS` from the
proved contract in
[`EXPLICIT_GLOBAL_MOSER_MAJORANT.md`](../../theory/EXPLICIT_GLOBAL_MOSER_MAJORANT.md),
the exact 26-check prefix, and the bound 38-check source run documented in
[`P2D_NORMAL_FORM_REPORT.md`](P2D_NORMAL_FORM_REPORT.md).  Its aggregate is
also `INCONCLUSIVE` and non-claim-bearing at replay 1/2.  The third child,
`V2.CHART.ZERO_ENERGY`, now has a local mathematical `PASS` from
[`EXPLICIT_ZERO_ENERGY_FIBER.md`](../../theory/EXPLICIT_ZERO_ENERGY_FIBER.md)
and [`P2D_ZERO_ENERGY_REPORT.md`](P2D_ZERO_ENERGY_REPORT.md).  The fourth
child, `V2.CHART.EXACT_SECTIONS`, now also has a local mathematical
`PASS` from
[`EXPLICIT_EXACT_RADIAL_SECTIONS.md`](../../theory/EXPLICIT_EXACT_RADIAL_SECTIONS.md)
and [`P2D_EXACT_SECTIONS_REPORT.md`](P2D_EXACT_SECTIONS_REPORT.md).  The fifth
child, `V2.CHART.WEIGHTED_PASSAGE`, now has a local mathematical `PASS` from
[`EXPLICIT_WEIGHTED_KATO_PASSAGE.md`](../../theory/EXPLICIT_WEIGHTED_KATO_PASSAGE.md)
and [`P2D_WEIGHTED_PASSAGE_REPORT.md`](P2D_WEIGHTED_PASSAGE_REPORT.md).  The
sixth child, `V2.CHART.PHYSICAL_SLIDES`, now has a local mathematical `PASS`
from
[`EXPLICIT_PHYSICAL_SLIDES.md`](../../theory/EXPLICIT_PHYSICAL_SLIDES.md) and
[`P2D_PHYSICAL_SLIDES_REPORT.md`](P2D_PHYSICAL_SLIDES_REPORT.md), including
(D12) with \(C_{\rm phys}=7\).  The seventh child,
`V2.CHART.OVERLAPS`, now has a local mathematical `PASS` from
[`EXPLICIT_FINITE_CHART_OVERLAPS.md`](../../theory/EXPLICIT_FINITE_CHART_OVERLAPS.md),
its proof-bound checker, and
[`P2D_CHART_OVERLAPS_REPORT.md`](P2D_CHART_OVERLAPS_REPORT.md).  Since all seven
children pass locally, the parent `V2.EXACT_CHART` also has a local
mathematical `PASS`.  The repository aggregate remains `INCONCLUSIVE` and
non-claim-bearing: P2e and later obligations remain open, and independent
replay is still 1 of 2.

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

## 5. Higher graph jets and weighted half-orbits for P2b

P2b retains the literal rectangular regularity in the proof of V2,

\[
 H_\mu\in C^2_\mu(C^3_b),\qquad
 D_b^iD_\mu^jH_\mu,\quad 0\le i\le3,\quad |j|\le2.
\]

Thus the largest mixed derivative has total order five.  Replacing this by
the smaller mixed-total-three triangle would be enough for several later
consumers, but would not validate the theorem as written.

### 5.1 Pure state tensors

On the already-existing true graph write

\[
 f=B_uu+q_\mu n_\mu(x),\qquad
 g=B_sH-q_\mu n_\mu(x),\qquad
 x=e_1^T(u+H(u)),
\]

and put \(A=DH\), \(J_2=D^2H\), \(J_3=D^3H\),
\(X_1=e_1^T(I+A)\), and
\(C=q_\mu n_\mu'(x)e_1^T\).  The top-order linear operator is

\[
 \mathcal L_kT=
 [B_s-(I+A)C]T-
 \sum_{a=1}^kT(\ldots,[B_u+C(I+A)]\,\cdot,\ldots).
\]

Direct differentiation along the true reduced flow gives the closed
triangular equations

\[
 \dot J_2=\mathcal L_2J_2
 -(I+A)q_\mu n_\mu''(x)X_1^{\otimes2},
\]

and

\[
\begin{aligned}
 \dot J_3={}&\mathcal L_3J_3
 -(I+A)q_\mu\left[n_\mu'''X_1^{\otimes3}
 +n_\mu''\sum_{\rm cyc}(e_1^TJ_2)X_1\right]\\
 &-\sum_{\rm cyc}J_2(F_2,\cdot),\qquad
 F_2=q_\mu\left[n_\mu''X_1^{\otimes2}
 +n_\mu'e_1^TJ_2\right].
\end{aligned}
\]

No fourth or fifth state derivative occurs.  With

\[
 D_*=\frac{111}{20000},\qquad
 \bar\kappa=\alpha-(1+D_*)\ell,qquad
 t=\|q_\mu\|\sup|n_\mu'''|,
\]

the Hilbert--Schmidt tensor inequalities are

\[
 \frac12D\|J_k\|_{HS}^2
 \le-(k+1)\bar\kappa\|J_k\|_{HS}^2
 +M_k\|J_k\|_{HS},
\]

where

\[
 M_2=m(1+D_*)^3
\]

and, on \(\|J_2\|_{HS}\le\sigma_2\),

\[
\begin{aligned}
 M_3={}&(1+D_*)
 \left[t(1+D_*)^3+3m\sigma_2(1+D_*)\right]\\
 &+3\sigma_2\left[m(1+D_*)^2+\ell\sigma_2\right].
\end{aligned}
\]

The frozen radii are \(\sigma_2=1/2\) and \(\sigma_3=9/8\).  The probe must
check both origin homological margins

\[
 3\alpha\sigma_2-m>0,\qquad
 4\alpha\sigma_3-(t+6m\sigma_2)>0,
\]

and both full-disk no-first-exit margins

\[
 3\bar\kappa\sigma_2-M_2>0,\qquad
 4\bar\kappa\sigma_3-M_3>0.
\]

The origin equations put the analytic germ strictly inside the tensor
balls.  The forward no-first-exit argument then follows the same true graph
already supplied by P2a; it does not use \(D^2H_{10}\) as a true-graph
bound.  A pass proves \(\|D^2H_\mu\|_{HS}\le1/2\) and
\(\|D^3H_\mu\|_{HS}\le9/8\), not \(C^2/C^3\) closeness to \(H_{10}\).

### 5.2 Fixed-core Lyapunov--Perron recurrence

Normalize the bridge exactly by

\[
 \theta_r=25r-1,\qquad \theta_a=4a_2,\qquad
 \theta_\epsilon=5(\epsilon-1),
\]

so \(\theta\in[-1,1]^3\).  In the moving graph coordinates use the fixed
core blocks \(B_{u,0},B_{s,0}\), let

\[
 \mathcal R_\theta(u,s)=
 \binom{\Delta B_\theta u+q_\theta n_\theta(u_1+s_1)}
       {-\Delta B_\theta s-q_\theta n_\theta(u_1+s_1)},
\]

and write the true unstable half-orbit as

\[
 Z_{\theta,b}=Eb+\mathcal K\mathcal R_\theta(Z_{\theta,b}).
\]

The fixed weight for this certificate is

\[
 \omega=\frac14,\qquad
 \|Z\|_\omega=\sup_{t\le0}e^{-\omega t}
 \max\{\|u(t)\|_2,\|s(t)\|_2\}.
\]

P2a's \(\gamma_1>2/3\), its quadratic graph estimate, and P2b0 imply

\[
 \|Z_{\theta,b}\|_\omega\le R=\frac1{100},\qquad
 |u_1+H_{\theta,1}(u)|\le\frac{251}{25000}.
\]

This is a bound along the true graph; it is not a claim that a full
four-dimensional product ball has the sharpened \(x\)-bound.

At fixed \(x\), outward interval automatic differentiation on the frozen
\(16\times8\times4\times2\) exact-rational grid bounds

\[
 B_j,\quad h_j=\|D_\theta^j(qn)\|,
 \quad\ell_j=\|D_\theta^j(qn')\|,
 \quad m_j=\|D_\theta^j(qn'')\|,
 \quad t_j=\|D_\theta^j(qn''')\|,
 \qquad 0\le j\le2.
\]

In the max-of-two-Euclidean-blocks norm set

\[
 L_{1j}=B_j+2\ell_j,\qquad
 L_{2j}=4m_j,\qquad L_{3j}=8t_j.
\]

Every explicit parameter derivative of \(\mathcal R_\theta\) vanishes at
\(Z=0\).  Therefore the required weighted zero-slot estimate is the
fixed-\(Z\) mean-value bound

\[
 \|D_\theta^j\mathcal R_\theta(Z)\|_\omega
 \le L_{1j}\|Z\|_\omega,
\]

not an unweighted constant \(h_j\).  Since the state polynomial is cubic,
\(D_Z^p\mathcal R_\theta=0\) for \(p\ge4\).

The fixed Green operator obeys

\[
 K_\omega=(1/\sqrt2-\omega)^{-1},\qquad
 q_{\rm LP}=K_\omega L_{10}<1,\qquad
 \|(I-\mathcal KD_Z\mathcal R)^{-1}\|
 \le(1-q_{\rm LP})^{-1}.
\]

For \(Z_{ij}=\|D_b^iD_\theta^jZ\|_\omega\), use the multilinear operator
norm on labelled Euclidean state and parameter directions, together with the
max-of-two-Euclidean-blocks state norm.  In particular, the derivative of
the injection \(b\mapsto Eb\) has norm one, which explains the direct term
below.  This is distinct from the Hilbert--Schmidt norm used for the separate
pure graph tensors \(D_b^2H,D_b^3H\); the finite-dimensional coefficient
Hilbert--Schmidt bounds dominate every labelled operator norm used here.

Use labelled derivative sets.  Choose the labels acting explicitly on
\(\mathcal R\), partition all
remaining labels into one, two, or three nonempty \(Z\)-blocks, and remove
exactly the single unpartitioned target term
\(D_Z\mathcal R\,Z_{ij}\).  Calling the resulting lower-order sum
\(\mathfrak B_{ij}\), the machine-generated recurrence is

\[
 Z_{ij}\le
 \frac{\mathbf1_{(i,j)=(1,0)}
 +K_\omega\mathfrak B_{ij}}{1-q_{\rm LP}}.
\]

The analytic parameter-dependent unstable-manifold theorem, followed by the
P2a cone continuation, first supplies the actual
\(C^2_\theta(C^3_b)\) true half-orbit family.  P2a's (2/3) backward decay
and the strict gap to the weight (1/4) place its derivatives in the fixed
weighted space (equivalently one may take finite backward truncations and
pass to the uniform limit).  Along that true family, and only there, P2b0
gives the sharpened (x)-tube used by the coefficient grid.  Thus
(q_{\rm LP}<1) bounds the linearization
(\mathcal K D_Z\mathcal R_\theta(Z_{\theta,b})) and its Neumann inverse.
Differentiating the true fixed-point identity then bounds the actual
derivatives; the recurrence is not a formal jet calculation.  No contraction
claim is made on the entire radius-(R) four-dimensional product ball, where
the sharpened (x)-bound need not hold.  Set partitions of labelled directions generate every Faà di Bruno
multiplicity and make the recurrence triangular through the complete
rectangle \(0\le i\le3, 0\le j\le2\).  Taking the stable component at
\(t=0\) gives the mixed graph jets.  The original blown-up parameter bounds
follow from the exact diagonal change; the coarse operator factors are
\(25\) and \(625\) for first and second parameter order.

The moving-coordinate bounds are then composed with the exact frame from
Section 2.  If \(T_k\) bounds the \(k\)-th normalized-parameter derivative of
\(T_\theta\), measured from the max-block norm to physical Euclidean norm,
the physical half-orbit satisfies the complete Leibniz bound

\[
 \|D_b^iD_\theta^j(T_\theta Z_{\theta,b})\|_\omega
 \le \sum_{k=0}^j {j\choose k}T_k Z_{i,j-k},
 \qquad 0\le i\le3,\quad 0\le j\le2.
\]

The executable kernel uses a conservative
\(\sqrt2\)-times-Frobenius/Hilbert--Schmidt enclosure for \(T_k\), records
both moving and physical bounds, and applies the same exact \(25/625\)
operator factors to obtain original blown-up-parameter bounds.  The fixed
isometric reverser supplies the stable graph and half-orbit bounds.

The certificate checker does not trust the C++ atomics merely because the
certificate also stores a matching stdout string and hash.  For this scope it
materializes the probe and local support headers from the recorded source
revision, reconstructs the strict compile command, and reruns the exact
argument vector on the checking machine.  Exact stdout, stderr hashes, and
exit status must agree.  This closes certificate-local coordinated-tampering
attacks; it is deliberately described as same-machine deterministic replay,
not as the second independent-machine execution required for a claim-bearing
release.

The smaller weight \(1/5\) is reserved for the selected full homoclinic in
P2c.  The number \(1/4\) is a deliberate quantitative choice satisfying
Theorem V2's existential \(0<\eta<1/\sqrt2\); it is unrelated to the P2b0
first-derivative tube radius \(3/10000\).

### 5.3 Aggregation and phase boundary

`V2.WU.JETS` passes only if `P2.JETS.COEFFICIENTS`,
`V2.WU.STATE_C23`, `V2.WU.MIXED_JETS`, and
`V2.WU.WEIGHTED_HALF_ORBITS` all pass.  `V2.WU_GRAPH` additionally binds
the immutable P2a and P2b0 passes.

These graph coordinates still do not fix the absolute source phase.  The
following separate P2bK contract must be discharged before P2c.

### 5.4 P2bK normalized Kato interface

All formulas, norms, rational gates, parameter cells, prerequisite hashes,
and source-jet targets for this stage are frozen in
[`config/vdp_p2_kato_v1.json`](config/vdp_p2_kato_v1.json) before the formal
outward-rounded run.  The design scout named there selected gates only and is
not certificate evidence.

Let \(A=A(c)\) be the physical linearization

\[
 A(c)=
 \begin{pmatrix}
 0&1&0&0\\ c&0&-1&0\\0&0&0&1\\1&0&0&0
 \end{pmatrix},
 \qquad
 \alpha=\frac{\sqrt{2+c}}2,
 \qquad
 \beta=\frac{\sqrt{2-c}}2.
\]

The expanding Riesz projector is required to satisfy the closed formula

\[
 P^u(c)=\frac12I+\frac{A(c)+A(c)^{-1}}{4\alpha}.
\tag{K1}
\]

Merely evaluating (K1) is not enough to identify the selected bundle.  The
exact-algebra part of the probe must also prove

\[
 (P^u)^2=P^u,\qquad AP^u=P^uA,\qquad \operatorname{tr}P^u=2,
\]

\[
 (A^2-2\alpha A+I)P^u=0,qquad
 (A^2+2\alpha A+I)(I-P^u)=0,
\tag{K2}
\]

together with \(\alpha,\beta>0\) on every parameter cell.  Thus the range of
\(P^u\), rather than an unlabelled rank-two invariant plane, is the expanding
\(\alpha\pm i\beta\) plane; the complementary factor in (K2) identifies the
stable plane.  The reverser identity
\(\mathcal RP^u\mathcal R=I-P^u\) is checked separately.

Put

\[
 M=\begin{pmatrix}
 -1&0&0&0\\0&1&0&2\\2&0&1&0\\0&0&0&-1
 \end{pmatrix}.
\]

Exact differentiation gives

\[
 [\partial_cP^u,P^u]=\frac{M}{4(2+c)},
 \qquad M^2=I.
\tag{K3}
\]

Along \(\gamma_\mu(s)=(sr,a_2,\epsilon)\), the sign convention is

\[
 \partial_sW=[\partial_sP^u,P^u]W,qquad W(0)=I.
\tag{K4}
\]

The transport therefore has the closed form

\[
 \tau(c)=\frac14\log\frac{2+c}{2},
 \qquad
 W(c)=\cosh\tau\,I+\sinh\tau\,M,
 \qquad P^u(c)W(c)=W(c)P^u(0).
\tag{K5}
\]

This identity, including its sign and initial value, is replayed by exact
algebra.  Since (2+c) stays strictly positive, (K5) itself gives the
(C^2) regularity of (W) without a separate numerical (W)-jet budget.
Interval arithmetic supplies the frozen first- and second-parameter bounds
for (c), (P^u), and the normalized frame and phase objects actually used
downstream.

The normalization after Kato transport is an explicit, separate operation.
With

\[
 \alpha_0=\frac1{\sqrt2},\qquad
 k_*=\left(\frac1{\sqrt2},\frac12,0,\frac12\right)^T,
 \qquad q=\left(\frac{2+c}{2}\right)^{1/4}>0,
\]

define

\[
 g=(1,2\alpha-\alpha_0,\sqrt2\alpha-1,\alpha_0)^T,
 \qquad N^2=6\alpha^2-4\sqrt2\alpha+3=\lVert g\rVert_2^2.
\]

The bridge from (K5) to the unit vector used by the phase convention is

\[
 Wk_*=\frac{q^{-1}}{\sqrt2}g,qquad
 \lVert Wk_*\rVert_2=\frac{q^{-1}}{\sqrt2}N,qquad
 k_1=\frac gN=\frac{Wk_*}{\lVert Wk_*\rVert_2}.
\tag{K6}
\]

In particular, \(W\) solves the unnormalized Kato equation (K4); the
normalized vector \(k_1\) is not asserted to solve that same equation.

On \(\operatorname{ran}P^u\), and only there, put

\[
 \mathfrak J_u=\frac{A-\alpha I}{\beta},
 \qquad \mathfrak J_u^2=-I,
 \qquad k_2=\mathfrak J_uk_1.
\]

Let \(E\) denote the algebraic expanding frame from Section 2.  Then

\[
 K=(k_1,k_2)=E C_{\rm AK},
 \qquad
 C_{\rm AK}=\frac1N
 \begin{pmatrix}1&-y\\y&1\end{pmatrix},
 \qquad
 y=\frac{\alpha_0-\alpha}{\beta},
\tag{K7}
\]

and

\[
 C_{\rm AK}=\sigma R_\chi,qquad
 \sigma=\frac{\sqrt{1+y^2}}N>0,qquad
 R_\chi=\frac1{\sqrt{1+y^2}}
 \begin{pmatrix}1&-y\\y&1\end{pmatrix},
 \qquad \tan\chi=y,\quad\cos\chi>0,\quad\chi(0)=0.
\tag{K8}
\]

The direction in (K7) is part of the contract: \(C_{\rm AK}\) sends Kato
coordinates to algebraic unstable coordinates, and
\(C_{\rm AK}^{-1}\) sends algebraic coordinates back.  Hence the algebraic
angle is \(\phi+\chi\), not \(\phi-\chi\).  The probe must bound the values
of \(\sigma\), \(\sigma^{-1}\), and
\(\det C_{\rm AK}=\sigma^2\) away from degeneracy.  The complete first and
second parameter-jet bounds for the matrix \(C_{\rm AK}\) provide the
declared derivative control; no separate scalar derivative gates for these
three derived quantities are claimed.  Although \(C_{\rm AK}\) is a positive
conformal change in the two coordinate planes, the physical matrix
\(K=(k_1,\mathfrak J_uk_1)\) is only an oriented rank-two frame with unit
first column.  It is **not** declared Euclidean-orthonormal; its operator norm
and smallest singular value are enclosed directly.

For \(R=1/100\), \(e_\phi=(\cos\phi,\sin\phi)^T\), define the source in the
algebraic graph disk by

\[
 b(\phi,\theta)=R R_{\chi(c(\theta))}e_\phi
 =R\frac{C_{\rm AK}e_\phi}{\lVert C_{\rm AK}e_\phi\rVert_2},
 \qquad
 S(\phi,\theta)=T_\theta
       \bigl(b(\phi,\theta),H_\theta(b(\phi,\theta))\bigr).
\tag{K9}
\]

Thus \(\lVert b\rVert_2=R\),
\(\partial_\phi^ib=\mathfrak J_0^ib\),
\(\lVert\partial_\phi b\rVert_2=R\), and the phase map has degree \(+1\).
Equation (K9) is the direct boundary of the same radius-(.01\) true graph
certified by P2a--P2b; it does not introduce an unchecked backward flow time
or a surrogate orbit.  On the complete \(r=0\) dummy face,
\(c=y=\chi=0\), \(W=I\), \(R_\chi=I\), and
\(C_{\rm AK}=I/\sqrt2\), so \(b=Re_\phi\) pointwise.  The vector field is
dummy-parameter independent there, and uniqueness of the true local graph in
the same coordinates identifies \(H_\theta\) with the imported core graph.
Consequently (K9), not just its degree, is exactly the frozen core source
circle on that entire face.

The true-source jet aggregation consumes the immutable P2b certificate; it
does not recalculate or assume graph derivatives.  Write

\[
 F_\theta(b)=T_\theta(b,H_\theta(b)),
\]

let \(F_{ij}\) be its certified nonnegative
\(D_b^iD_\theta^j\) norm bound from P2b, and let \(\chi_j\) bound the
normalised-parameter derivatives of \(\chi\).  Define

\[
 B_1=R\chi_1,qquad
 B_2=R\sqrt{\chi_2^2+\chi_1^4},
\]

\[
 G_1=F_{11}+F_{20}B_1,qquad
 G_2=F_{12}+2F_{21}B_1+F_{30}B_1^2+F_{20}B_2.
\]

The frozen chain-rule upper bounds are

\[
\begin{aligned}
 S_{00}&=F_{00},\\
 S_{01}&=F_{01}+F_{10}B_1,\\
 S_{02}&=F_{02}+2F_{11}B_1+F_{20}B_1^2+F_{10}B_2,\\
 S_{10}&=F_{10}R,\\
 S_{11}&=G_1R+F_{10}B_1,\\
 S_{12}&=G_2R+2G_1B_1+F_{10}B_2,\\
 S_{20}&=F_{20}R^2+F_{10}R,\\
 S_{21}&=(F_{21}+F_{30}B_1)R^2
          +2F_{20}B_1R+G_1R+F_{10}B_1,\\
 S_{30}&=F_{30}R^3+3F_{20}R^2+F_{10}R.
\end{aligned}
\tag{K10}
\]

Here \(S_{ij}\) bounds \(D_\phi^iD_\theta^jS\) in the declared labelled
multilinear Hilbert--Schmidt norm.  The certified target is exactly the
total-order-three triangle

\[
 (i,j)\in\{(0,0),(0,1),(0,2),(1,0),(1,1),(1,2),
             (2,0),(2,1),(3,0)\}.
\tag{K11}
\]

It is not the full \(0\le i\le3\), \(0\le j\le2\) rectangle: for example,
the omitted corner jets would require fourth and fifth state derivatives of
the graph, while P2b certifies only \(D_b^{\le3}D_\theta^{\le2}\).  The
triangle includes \(S_{12}\), the highest mixed source jet reserved for the
P2c matching stage.  Original blown-up-parameter bounds are obtained only
through the frozen exact operator factors \(25\) and \(625\).

The certificate dependency graph is also frozen.  The prerequisite atoms
`ENV.EXACT_SYMBOLIC_BACKEND` must bind the frozen Python executable and the
cache-free SymPy source-tree digest before the exact-algebra audit can enter
the P2bK aggregate.  The atoms
`P2.P2B_JETS_PREREQUISITE` and `P2.KATO_CONFIG_FROZEN` must bind the exact
P2a/P2b configurations and certificates, the local core/source definitions,
and the read-only flagship import at the recorded revisions and hashes.  The
formal kernel may then prove only the raw atoms
`P2.KATO.RIESZ_TRANSPORT`, `P2.KATO.FRAME_CHANGE`, and
`P2.KATO.SOURCE_PARAMETERIZATION`, together with `P2.KATO.C2_LIFT` for the
complete normalized-parameter first and second jets, symmetric interval-AD
Hessians, and exact \(25/625\) conversion to the original blown-up
parameters.  The raw probe's source-parameterization verdict covers the
coordinate calculation, while the certificate-level
`P2.KATO.SOURCE_PARAMETERIZATION` verdict additionally requires the immutable
P2b true-graph prerequisite and the exact audit.  The runner may derive
`V2.PHASE.TRUE_SOURCE` only from the
source-parameterization and \(C^2\)-lift atoms, the immutable P2b
`V2.WU_GRAPH` pass, and every gate in (K10)--(K11).  Finally,
`V2.PHASE.KATO_INTERFACE` requires the Riesz-transport, frame-change,
\(C^2\)-lift, and true-source atoms together.  In particular, a
source-coordinate calculation alone cannot certify that (K9) lies on a true
invariant graph.

P2bK ends at this source interface.  It does not prove the selected
positive-parameter homoclinic, first-hit or endpoint transversality in P2c;
the positive radial reversible symplectic completion or exact saddle charts
in P2d; the event atlas in P2e; V3--V6 or either noncompact end.  It also makes
no claim of temporal stability, dynamical Turing-pattern selection, or a
finite-parameter canard.  Every claim-bearing status remains false until the
repository's independent-machine replay policy is met.

### 5.5 P2d reversible exact saddle-chart interface

P2d applies Definition 2.1(I1), Lemmas 2.4--2.6, and Proposition 2.7 of the
frozen flagship manuscript at commit
`d54add098545063d5efe8f1d6f062d4cfc116a0d`.  The imported manuscript blob is
`papers/paper-a/manuscript/main.tex`, SHA-256
`0baf6335aad72d5893479d8876d2613671ecb8ac2ccd73664405dea4381e6a20`.
Those results provide a qualitative analytic existence theorem.  A P2d
machine certificate must additionally expose the radii, cover, overlap
domains, action width, and downstream derivative constants that it consumes.
The two evidence layers must not be conflated:

1. exact verification of the I1 hypotheses invokes the frozen theorem and
   proves existence for every fixed finite log-derivative order;
2. a constructive analytic certificate supplies explicit machine-usable
   constants, initially through log order three and parameter order two.

There are correspondingly three distinct status fields.  `PASS` from an
auxiliary exact-identity audit means only that its enumerated identities hold;
an atom remains `OPEN` until its full mathematical predicate is discharged;
and `claim_bearing` remains false until the repository-level replay and
provenance policy is satisfied.  None of these statuses substitutes for
another.

Log order three is the first constructive target because the frozen marked
class has state regularity at least five and its passage interface consumes
orders through \(k-2\).  It does not replace the all-finite-order analytic
quantifier in Theorem V2(3).  The latter must be supplied by one Cauchy-bound
generator valid for arbitrary finite \(m\).

#### Exact Kato-oriented symplectic completion

In the physical order \((U,P,V,Q)\), freeze

\[
 \Omega=
 \begin{pmatrix}
  0&-1&0&0\\1&0&0&0\\0&0&0&1\\0&0&-1&0
 \end{pmatrix},
 \qquad C_0=\operatorname{diag}(1,-1).
\tag{D1}
\]

For the P2bK expanding frame \(K=(k_1,k_2)\),
\(k_2=\mathfrak J_uk_1\), exact algebra gives

\[
 B:=K^T\Omega\mathcal RK
   =\begin{pmatrix}d&e\\e&-d\end{pmatrix},
 \quad
 d=\frac{2\alpha}{N^2},
 \quad
 e=\frac{2\alpha(3\alpha-2\sqrt2)}{N^2\beta},
\tag{D2}
\]

and

\[
 \kappa=\sqrt{-\det B}=\sqrt{d^2+e^2}
 =4\alpha\beta\frac{1+y^2}{N^2}>0,
 \qquad y=\frac{2^{-1/2}-\alpha}{\beta}.
\tag{D3}
\]

The branch is fixed by

\[
 c_\vartheta=\sqrt{\frac{\kappa+d}{2\kappa}}>0,
 \qquad
 s_\vartheta=\frac{e}{\sqrt{2\kappa(\kappa+d)}},
 \qquad
 A_\vartheta=
 \begin{pmatrix}c_\vartheta&-s_\vartheta\\
                 s_\vartheta&c_\vartheta\end{pmatrix}.
\tag{D4}
\]

Then \(A_\vartheta^TBA_\vartheta=\kappa C_0\).  Define

\[
 Y=\kappa^{-1/2}KA_\vartheta,
 \qquad X=\mathcal RYC_0,
 \qquad L=(X,Y).
\tag{D5}
\]

The combined P2d evidence must prove

\[
 L^T\Omega L=
 \begin{pmatrix}0&-I\\I&0\end{pmatrix},
 \qquad
 \mathcal RL(x,y)=L(C_0y,C_0x),
\tag{D6}
\]

together with the stable/expanding spectral blocks and invertibility.  The
exact symbolic audit verifies these identities and the branch formula; a
separate outward-rounded interval layer must supply uniform positive branch
margins and the complete first and second parameter bounds on the frozen box.
The rotation in (D4) changes the Kato phase origin but has degree \(+1\).

That interval layer is frozen by
[`vdp_p2d_symplectic_frame_v1.json`](config/vdp_p2d_symplectic_frame_v1.json)
and implemented independently of the design scout in
[`vdp_p2d_symplectic_frame_probe.cpp`](src/vdp_p2d_symplectic_frame_probe.cpp).
Its reference strict run covers all 512 exact-rational cells and places the
value, three first derivatives, and six symmetric second derivatives of every
listed scalar and every entry of \(L,L^{-1}\) in explicit enclosures, in both
normalized and original parameters.  The frozen gates separately bound the
scalar branches, anchor conditioning, and prescribed matrix-jet norms.  The
inverse is evaluated from
\(L^{-1}=-\Omega_0L^T\Omega\), not by interval Gaussian elimination.  With
the P2bK prerequisite and the 59-check audit, this establishes the local
mathematical `PASS` stated above.  Exact identities are supplied by the audit,
not inferred from small interval residuals.

This result is archived in the clean-source certificate
[`results/vdp_bridge_v1_p2d_symplectic_frame.json`](results/vdp_bridge_v1_p2d_symplectic_frame.json).
Its integrity and mathematical status are `PASS`, but its final status is
`INCONCLUSIVE`, `claim_bearing=false`, and `release_eligible=false` while the
second-machine replay is open.  The separately version-bound analytic
majorant and source checker now also establish local mathematical `PASS` for
`V2.CHART.ANALYTIC_NORMAL_FORM`; see
[`P2D_NORMAL_FORM_REPORT.md`](P2D_NORMAL_FORM_REPORT.md).  The transferred
action majorant and strict rational Krawczyk/implicit-jet check also establish
local mathematical `PASS` for `V2.CHART.ZERO_ENERGY`; see
[`P2D_ZERO_ENERGY_REPORT.md`](P2D_ZERO_ENERGY_REPORT.md).  The frozen radial
section radius, exact arbitrary-\(q\) identities, and physical primitive
gauges also establish local mathematical `PASS` for
`V2.CHART.EXACT_SECTIONS`; see
[`P2D_EXACT_SECTIONS_REPORT.md`](P2D_EXACT_SECTIONS_REPORT.md).  The signed
weighted passage, all-finite-order generator, and clock inversion likewise
establish local mathematical `PASS` for `V2.CHART.WEIGHTED_PASSAGE`; see
[`P2D_WEIGHTED_PASSAGE_REPORT.md`](P2D_WEIGHTED_PASSAGE_REPORT.md).  The
proof-bound physical slides likewise establish local mathematical `PASS` for
`V2.CHART.PHYSICAL_SLIDES`; see
[`P2D_PHYSICAL_SLIDES_REPORT.md`](P2D_PHYSICAL_SLIDES_REPORT.md).  The
finite-overlap proof and checker now also establish local mathematical `PASS`
for `V2.CHART.OVERLAPS`; see
[`P2D_CHART_OVERLAPS_REPORT.md`](P2D_CHART_OVERLAPS_REPORT.md).  Thus all seven
chart atoms and their local parent `V2.EXACT_CHART` pass mathematically on the
declared common domain.  P2e, the later validation obligations, and the second-
machine replay remain open.

There is a mandatory sign dictionary.  With the positive Kato orientation,

\[
 \widehat H_{2,\mu}\circ L
 =\alpha I_1+\beta I_2^{\rm K},
 \quad I_1=x\mathbin\cdot y,
 \quad I_2^{\rm K}=x_2y_1-x_1y_2.
\tag{D7}
\]

The frozen flagship notation uses
\(I_2^{\rm F}=x_1y_2-x_2y_1\).  Its exact transport to the Kato-tangent
chart is the four-dimensional conjugation

\[
 \mathcal T=\operatorname{diag}(C_0,C_0),
 \qquad
 \mathcal T^T\Omega_0\mathcal T=\Omega_0,
 \qquad
 \mathcal T\mathcal R_0=\mathcal R_0\mathcal T,
 \qquad
 I_2^{\rm F}(\mathcal Tz)=I_2^{\rm K}(z).
\tag{D8}
\]

It also preserves \(I_1\).  Hence the action value and its sign component
are unchanged; the formal two-dimensional map
\((\phi,\nu)\mapsto(-\phi,-\nu)\) is symplectic but is **not** the chart
dictionary used here.

The Kato phase sign is fixed directly.  With
\(J=\left(\begin{smallmatrix}0&-1\\1&0\end{smallmatrix}\right)\), the exact
incoming and outgoing radial sections are

\[
 \begin{aligned}
 (x,y)_{\rm in}
  &=\left(\rho e_\phi,
      \rho^{-1}\{q_\mu(\nu)e_\phi-\nu Je_\phi\}\right),\\
 (x,y)_{\rm out}
  &=\left(\rho^{-1}\{q_\mu(\nu)e_\psi+\nu Je_\psi\},
      \rho e_\psi\right).
 \end{aligned}
\]

Each has \(I_1=q_\mu(\nu)\), \(I_2^{\rm K}=\nu\), and pullback
\(d\phi\wedge d\nu\).  The normal-form equations rotate both the stable and
expanding factors with positive Kato angular speed
\(\partial_2h_\mu(q_\mu(\nu),\nu)\).  Since
\(q_\mu(\nu)=-(\beta_\mu/\alpha_\mu)\nu+O(\nu^2)\), their direct quadrature,
not a phase-only coordinate reversal, gives

\[
 \Delta_{\mu,\sigma}(\nu)
 =-\frac{\beta_\mu}{\alpha_\mu}\log|\nu|
  +b_{\mu,\sigma}+\rho_{\mu,\sigma}(\nu).
\tag{D9}
\]

The time law retains its usual negative logarithm.  Any probe or figure using the opposite sign must
label itself as using the frozen local Darboux convention rather than the
common Kato phase.

#### Constructive analytic gates

`V2.CHART.ANALYTIC_NORMAL_FORM` may pass only if a finite Lie/Moser prefix and
a strict scalar majorant prove convergence of the infinite sequence on an
explicit complex polydisc.  Every finite step must be Hamiltonian, reversible,
and exact symplectic; the summable tail must give the limit chart, inverse,
parameter two-jets, exact primitive gauge, image containment, and

\[
 \widehat H_\mu\circ\Phi_\mu^{\rm K}
   =h_\mu^{\rm K}(I_1,I_2^{\rm K})
\tag{D10}
\]

as an identity.  A small numerical symplectic defect or a finite normal-form
truncation is not a substitute for (D10).

These analytic conditions are now satisfied by proof contract
`rfsn-vdp-p2d-explicit-global-moser-majorant/1` and the authenticated
source-bound checker.  In particular, the pass uses an infinite majorant and
joint \(C^2\) tails; it is not inferred from the audited degree-four prefix.
The exact domains, rational envelopes, and claim boundary are recorded in
[`P2D_NORMAL_FORM_REPORT.md`](P2D_NORMAL_FORM_REPORT.md).

Here and below \(\nu=I_2^{\rm K}\).  The zero-energy atom applies to the
nonlinear normal form in (D10), not to
the raw polynomial Hamiltonian in the linear tangent frame.  On both signs of
\(\nu\), a frozen interval Newton/Krawczyk gate must prove

\[
 h_\mu^{\rm K}(q_\mu(\nu),\nu)=0,
 \qquad q_\mu(0)=0,
 \qquad q_\mu'(0)=-\frac{\beta_\mu}{\alpha_\mu},
 \qquad
 \partial_{I_1}h_\mu^{\rm K}(q_\mu(\nu),\nu)\ge a_*>0,
\tag{D11}
\]

with one common action width, an explicit bound for
\(D_\mu^{\le2}D_\nu^{\le3}q_\mu\), and a Cauchy-bound rule for every fixed
finite \(\nu\)-derivative order.  These conditions lock
the interval solve to the equilibrium zero-energy branch and fix the forward
time orientation used in the passage law; merely excluding zero from
\(\partial_{I_1}h_\mu^{\rm K}\) would not suffice.  The section pullback
must be exactly \(d\phi\wedge d\nu\), with a fixed primitive gauge, so that
the equality of incoming and outgoing \(\nu\) is exact action preservation.

The weighted-passage atom must provide the time and phase constants, a
single explicit uniform lower bound
\(e^{\alpha_\mu t_{\mu,\sigma}}\ge c_*>0\), the Kato-oriented sign in (D9), and the
explicit \(D_\mu^{\le2}D_{\log\nu}^{\le3}\) bounds.  The analytic majorant
must also expose the rule producing both \(\nu_{*,m}>0\) and \(C_m<\infty\)
for every fixed \(m\ge0\).  At the auxiliary radial sections it must imply
the bounded comparison

\[
 \left|n^{\rm K}-\frac{\beta_\mu}{2\pi}T^{\rm K}_\mu\right|
 \le C_{\rm rad}.
\]

This is the weighted-passage child obligation.  The full physical
winding/residence statement is

\[
 \left|n^{\rm K}-\frac{\beta_\mu}{2\pi}
 \mathcal T_{{\rm sf},\mu}\right|\le C.
\tag{D12}
\]

It additionally uses
\(\mathcal T_{{\rm sf},\mu}=T^{\rm K}_\mu+T^{\rm in}_{\rm slide}
+T^{\rm out}_{\rm slide}\).  Therefore (D12) closes only after the
physical-slide atom supplies uniform bounds for both finite slide times.  A
local pass for the radial comparison must not be reported as a pass for
(D12).

For the positive clock lift \(\beta_\mu T=2\pi n+\theta\), it must also
export the convention-dependent but downstream-essential combinations

\[
 \widetilde b^{\rm K}_{\mu,\sigma}
  =b^{\rm K}_{\mu,\sigma}-\beta_\mu t^{\rm K}_{\mu,\sigma},
 \qquad
 \varrho^{\rm K}_{\mu,\sigma,n}
  =\rho^{\rm K}_{\mu,\sigma}(\nu_{\mu,\sigma,n})
    -\beta_\mu\tau^{\rm K}_{\mu,\sigma}(\nu_{\mu,\sigma,n}),
\]

so that the limiting phase is
\(\phi+\theta+\widetilde b^{\rm K}_{\mu,\sigma}\) and the finite matching
row has the signs frozen in equations (3K-d)--(3K-e) of the return/coding
import note.

The physical-slide atom begins by freezing the exact physical incoming and
outgoing faces and the local event germs excluded from the punctured saddle
collar.  It then verifies face transversality, block containment, flow-domain
buffers, event-free slides, first-hit uniqueness and speed, and the required
state-\(C^3\)/parameter-\(C^2\) bounds.  The complete connected event-cell
census remains P2e; only the local collar exclusion needed by P2d is frozen
here.  Its bounded slide times combine with the radial comparison above to
close (D12).  The proof-bound local result now supplies slide times below
\(19\) on both sides and closes (D12) with the explicit uniform choice
\(C_{\rm phys}=7\); see
[`P2D_PHYSICAL_SLIDES_REPORT.md`](P2D_PHYSICAL_SLIDES_REPORT.md).

Finally, the overlap atom must validate a finite cover
\(V_i\Subset U_i\), not silently replace it by one global nonlinear chart.
It checks chart and inverse domains, exact primitive gauges, preservation of
the signed axes, oriented-blow-up extensions of transitions and inverses,
state-\(C^3\)/parameter-\(C^2\) mixed bounds, and degree \(+1\) on the Kato
phase boundary.  Only after all seven P2d atoms pass may
`V2.EXACT_CHART` pass.

The proof in
[`EXPLICIT_FINITE_CHART_OVERLAPS.md`](../../theory/EXPLICIT_FINITE_CHART_OVERLAPS.md)
and the bound checker
[`check_p2d_chart_overlaps.py`](check_p2d_chart_overlaps.py) now discharge these
requirements locally.  Together with the six preceding child results, they
give `V2.EXACT_CHART` a local mathematical `PASS`; this does not discharge P2e
or the repository replay policy.

## 6. What P2a and P2b0 do and do not settle

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

## 7. Homoclinic, chart, and atlas boundaries

The selected homoclinic stage must use a validated true-graph source and a
gap-free interval parameter cover.  The symmetry section is codimension two,
so a simultaneous zero of \((P,Q)\), a no-earlier-hit proof, and endpoint
transversality are separate checks.  The core determinant interval is an
anchor, not a positive-parameter conclusion.

Branch uniqueness is required only in the finite parameter-following lifted
multiple-shooting tube specified by `V2.HOM.BRANCH`.  No additional
large-box exclusion or exclusion of direct-shooting roots outside that lifted
tube is a P2c obligation.

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
