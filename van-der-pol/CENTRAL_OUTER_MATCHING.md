# Central--intermediate--outer matching at positive parameter

**Evidence status: Proved.**  This note proves
the analytic bridge required in claim V5.  It resolves the corner at which
the universal central chart, the published entry/exit chart, and the positive
outer compactification meet.  The resolution is essential: ordinary
Fenichel persistence on a compact slow segment does not control two parameter
derivatives through this corner.

The result is a continuation theorem for one algebraic channel.  It is not
an outer action-finite-part theorem and it is not an exhaustive
return--first-exit theorem.

## 1. Final common parameter box and theorem

The annulus is selected by a rerun, not by a nesting argument.  Work first on
the closed V2 comparison wedge \(0\le r\le r_*\).  The scaled outer field in
Section 4 and the resolved \(K_1\) field in Section 5 extend to this closed
wedge, so their graph-transform, overlap, exchange, and source-incidence
estimates produce a smallness threshold without using a positive lower
endpoint for \(r\).  After every such threshold has been collected, choose
\(r_{\rm p}>0\) once and freeze

\[
 \mathcal P_{\rm p}
 =\left[\frac12r_{\rm p},r_{\rm p}\right]
   \times[-A,A]\times[\epsilon_-,\epsilon_+],
 \qquad \mu=(r,a_2,\epsilon),
\tag{1}
\]

with

\[
 \delta=r^2,\qquad
 a=1+\sqrt\epsilon\,r^3a_2.
\tag{2}
\]

V3 and V4 are then rerun on this exact annulus.  In particular, the box above
is not asserted to be a subset of an earlier box
\([r_{\rm old}/2,r_{\rm old}]\), which would generally be false after changing
the upper radius.  Every small-\(r\) condition below is one of the thresholds
collected before this final choice; the annulus is not changed after V3--V4
have been rerun.  The collection includes V3's internal cone-entry,
source-window, compact-flow, and regular-singular small-\(r\) thresholds, not
only the new V5 overlap and matching estimates.

For the limiting argument only, the resolved vector field is considered on
the closed extension \(0\le r\le r_{\rm p}\).  No positive-parameter result
is inferred from compactness at \(r=0\); that face supplies the
comparison problem.

### Theorem V5

For this final choice of \(r_{\rm p}>0\), the following statements hold
for every \(\mu\in\mathcal P_{\rm p}\).

1. **Matched future sheet.**  A fixed subordinate patch of the V4 outer
   future-staying graph has a unique backward saturation through a prescribed
   outer tube, the resolved \(K_1\) corner, and the \(K_2\) overlap.  Its cut
   in a fixed universal central flowbox is a cooriented codimension-one
   \(C^3\) graph

   \[
    \mathcal W^{\rm match}_{\mathrm{out},\mu}.
   \tag{3}
   \]

   On the outer overlap it is the V4 graph itself, not a second invariant
   hypersurface.  Uniqueness is relative to the fixed matching tube.

2. **Central limit and two parameter derivatives.**  Let
   \(\mathcal W^0_{\rm a}\) be the frozen canonical core algebraic
   hypersurface.  On a fixed central section, (3) and
   \(\mathcal W^0_{\rm a}\) are graphs \(G_\mu\) and \(G_0\) over the same
   compact base.  Their resolved normalization satisfies

   \[
    \|G_{r,a_2,\epsilon}-G_0\|_{C^2}
       \le C r,
    \qquad 0\le r\le r_{\rm p},
   \tag{4}
   \]

   uniformly for \((a_2,\epsilon)\in[-A,A]\times
   [\epsilon_-,\epsilon_+]\).  Moreover

   \[
    \sup_{i+j\le2}
      \|D_Z^iD_{(r,a_2,\epsilon)}^jG_{r,a_2,\epsilon}\|<\infty.
   \tag{5}
   \]

   The estimate is in the universal central chart and includes the exact
   parameter-dependent chart embedding.  Thus there is neither a discarded
   shifted-base term nor a boundary trace in a weaker space.

3. **Exchange and source connection.**  The endpoint-anchored adjoint line
   extends through the same resolved atlas.  With the frozen Jost
   normalization, the frozen pairing and its positive-parameter
   continuation satisfy

   \[
    \chi_{\rm ex}^0=144\sqrt3,\qquad
    \chi_{{\rm ex},\mu}=144\sqrt3+O(r)\ge72\sqrt3>0.
   \tag{6}
   \]

   This exchange pairing is distinct from the source-phase incidence.  The
   latter is nonzero by the frozen origin-to-algebraic certificate.  A
   two-dimensional operator in source phase and central flight time is
   therefore uniformly invertible on (1).  It selects a unique \(C^2\)
   source phase near the frozen algebraic phase.  The selected orbit crosses
   the same finite gate as in V2, enters (3), and remains in the V4
   future-staying channel to \(u=+\infty\).

4. **Moving-cut covariance.**  Every chart uses the same physical primitive

   \[
    \lambda_\delta=\epsilon p\,du-\delta^{-1}q\,dv.
   \tag{7}
   \]

   The truncated matching action is \(C^2\) on the final box and satisfies
   exact first-hit composition.  Moving a subordinate \(K_2\), \(K_1\), or
   outer cut transfers exactly one finite physical orbit segment between
   adjacent terms, with no cut-dependent remainder.

Items 1--4 discharge V5.
They do not choose counterterms at \(z=0\).

## 2. Frozen comparison data and import boundary

At \(r=0\) the universal system is

\[
 U'=P,\qquad P'=-U^2-V,\qquad V'=Q,\qquad Q'=U,
\tag{8}
\]

with

\[
 \lambda_0=P\,dU-Q\,dV,
 \qquad
 H_0=\frac12(Q^2-P^2)-\frac13U^3-UV.
\tag{9}
\]

We use three facts from H. Lu, *First returns, singular exits, and action
finite parts near a reversible Hamiltonian saddle-focus*, frozen at

\[
 \mathtt{d54add098545063d5efe8f1d6f062d4cfc116a0d}.
\tag{10}
\]

They are imported only as singular comparison facts.

- Proposition 8.1 constructs the locally maximal \(C^4\) canonical
  algebraic future hypersurface \(\mathcal W^0_{\rm a}\), with a
  fourth-order-bunched weighted tail and a regular finite saturation.
- The optional Jost module proves along the exact algebraic orbit that

  \[
   T\mathcal W^0_{\rm a}
    =\operatorname{span}\{\mathcal T,\mathcal Z,\mathbf s\},
   \qquad \psi=\omega(\mathbf s,\,\cdot),
  \tag{11}
  \]

  and gives the exact growing solution \(\mathbf u\) used in (6).
- Proposition 8.4 proves a locally unique, modulo flow, transverse
  intersection of \(W^u_0(O)\) with
  \(\mathcal W^0_{\rm a}\cap\{H_0=0\}\).  Its source phase lies in

  \[
   [5.7566913947049203,5.7566913967948983].
  \tag{12}
  \]

The immutable source files used here have hashes

    papers/paper-a/manuscript/main.tex
    0baf6335aad72d5893479d8876d2613671ecb8ac2ccd73664405dea4381e6a20

    validation/future-target-fold/certificate.json
    88fa64035bb4352f5e25aa8d1627b191936264958c125dface59c5a767f6b3ce

    validation/origin-algebraic-heteroclinic/certificate.json
    60882ee1d3b2b18264b85764288505ae8b47d00bc826a2bddec152898f690fbe

The last certificate has a weighted Krawczyk contraction ratio below
\(0.183\), identifies the target row with the canonical physical graph,
and proves bordered nonsingularity.  We do not import a
positive-parameter end, matching theorem, or action finite part.

Relative to the deliberately narrower V2 boundary in
CENTRAL_CORE_IMPORT.md, this note adds only the frozen canonical-tail
statement, the full transverse conclusion of Proposition 8.4, and the
optional Jost appendix.  In the immutable source these are labelled
prop:core-algebraic-future, prop:core-origin-algebraic, and
app:jost-source-arm; equations eq:jost-symplectic-pairings through
eq:weighted-horizontal-tangent contain (11) and (51).  All
positive-parameter attachment statements are proved here.

The model equations and the \(K_1\)--\(K_2\) transitions come from the
published Vo--Doelman--Kaper paper at equations (6.4)--(6.8), (6.16), and
(6.28)--(6.29), with the sign, clock, and energy audits recorded in
MODEL_AND_CENTRAL_CHART.md.  The published paper supplies no
positive-parameter outer matching theorem.

## 3. Common physical sections and exact transitions

The frozen shooting target is \(e=0.0575\), where
\(e=(-U)^{-1}\).  Flow it forward inside the already certified canonical
tail to a fixed section

\[
 \Sigma_{\rm c}=\{h_{\rm c}=0\},
 \qquad h_{\rm c}=U+M,
 \qquad M>0.
\tag{13}
\]

We choose \(M\) large only after the corner estimates below have fixed their
small collar.  This finite frozen slide is regular, stays inside the
canonical tail, and preserves the nonzero adjoint pairing.  At the frozen
orbit \(P<0\) on (13); after shrinking a fixed flowbox,

\[
 |dh_{\rm c}(F_\mu)|=|P|\ge s_*>0.
\tag{14}
\]

Transport the frozen certificate defining function as a flow-constant
function through this finite slide.  Below, \(Dg_{\rm a}\) denotes its row
on \(\Sigma_{\rm c}\); with this convention its pairing with the transported
source-phase vector is exactly the certified pairing, not merely a
nonzero scalar multiple.

The section is fixed in universal coordinates.  In physical and \(K_2\)
coordinates it is exactly

\[
 \Sigma_{{\rm c},\mu}
 =\{u=a+\sqrt\epsilon\,r^2M\}
 =\{u_2=M+ra_2\}.
\tag{15}
\]

The final choice \(r_{\rm p}A<M/2\) keeps this overlap uniformly in
\(u_2>0\).

On its \(K_1\) representation,

\[
 \sigma=(M+ra_2)^{-1/2},\qquad
 r_1=r\sqrt{M+ra_2},\qquad
 \delta_1=\sigma^2,\qquad a_1=\sigma^3a_2,
\tag{16}
\]

and

\[
 p_1=\sigma^3p_2,\qquad
 v_1=\sigma^4v_2,\qquad
 q_1=\sigma^3q_2.
\tag{17}
\]

The embedding (16) is \(C^\infty\) at \(r=0\).  It is kept in every
derivative estimate.

Choose \(0<z_*<1\) in the scaled outer construction of Section 4, and then
choose one \(R>0\) such that

\[
 z_R(\epsilon)=(1+\sqrt\epsilon R^2)^{-1}<z_*
 \quad\hbox{for all }\epsilon\in[\epsilon_-,\epsilon_+].
\tag{18}
\]

The outer cut is the single physical family

\[
 \Sigma_{{\rm o},\mu}
 =\{r_1=R\}
 =\{u=1+\sqrt\epsilon R^2\}
 =\{z=z_R(\epsilon)\}.
\tag{19}
\]

On a physical leaf,

\[
 \sigma=r/R,\qquad \delta_1=(r/R)^2,
 \qquad a_1=(r/R)^3a_2.
\tag{20}
\]

The exact \(K_1\)-to-outer map is

\[
\begin{aligned}
 z&=(1+\sqrt\epsilon r_1^2)^{-1},
 &\pi&=\epsilon r_1^3p_1,\\
 w&=z\epsilon r_1^4
       \left(1-v_1+\frac{\sqrt\epsilon}{3}r_1^2\right),
 &\chi&=z^2\epsilon^{3/2}r_1^3q_1,\\
 h&=\epsilon r_1^3
       \{p_1-\sqrt\epsilon r_1^2\delta_1z^2q_1\},
 &\alpha&=(h+w)/2,\qquad \beta=(h-w)/2.
\end{aligned}
\tag{21}
\]

The clocks obey

\[
 \frac d{d\tau}=r_1z\frac d{dy_1}
 =\epsilon^{1/4}rz\frac d{d\xi}.
\tag{22}
\]

These identities show that (13) and (19) are common physical sections,
not independently selected chart cuts.

## 4. The scaled outer trace through \(\delta=0\)

V4 used unscaled variables on a positive box.  To approach the corner we
must first remove their vanishing powers.  Put

\[
 A=\alpha/\delta,\qquad B=\beta/\delta,
 \qquad H=\frac{E}{\epsilon^{5/2}r^6},
 \qquad S=\chi+A+B,\qquad D=A-B.
\tag{23}
\]

Thus \(\pi=\delta S\), \(w=\delta D\).  Direct substitution into the
exact V4 equations gives

\[
\begin{aligned}
 \dot z&=-\delta S z^3,& \dot H&=0,\\
 \dot A&=A-\frac{z^2}{2}S
 +\frac{\delta z^2}{2}
   \{-\epsilon(1-az)+2\chi S-SD\},\\
 \dot B&=-B+\frac{z^2}{2}S
 +\frac{\delta z^2}{2}
   \{-\epsilon(1-az)+2\chi S+SD\}.
\end{aligned}
\tag{24}
\]

The positive energy root is exactly

\[
\begin{aligned}
 \chi^2={}&\frac\epsilon2-\frac{2a\epsilon}{3}z
 -\epsilon(1+2\delta D)z^2
 +2a\epsilon(1+\delta D)z^3\\
 &+\{\epsilon\delta^2S^2
       +2\epsilon^{5/2}\delta^3H+2\epsilon F(a)\}z^4,
 \qquad F(a)=\frac{a^4}{12}-\frac{a^2}{2}.
\end{aligned}
\tag{25}
\]

It is \(C^\infty\) at \(\delta=0\).  On the physical total-family face
\((\delta,a)=(0,1)\),

\[
 \chi_0^2
 =\frac\epsilon6(1-z)^3(5z+3).
\tag{26}
\]

Writing \(C=A+B\), the normal subsystem at \(\delta=0\) is

\[
 \dot C=D,\qquad
 \dot D=(1-z^2)C-z^2\chi_0.
\tag{27}
\]

Its equilibrium and two normal rates are

\[
 C_0=\frac{z^2\chi_0}{1-z^2},\qquad D_0=0,
 \qquad \lambda_\pm=\pm\sqrt{1-z^2}.
\tag{28}
\]

On \(0\le z\le z_*\), the gap is uniform.  Straighten (28), put the
stable coordinate into the base, and use the unstable coordinate as the
graph fiber.  After decreasing the state and \(H\) collars, adapted
quotient metrics give, for some \(\theta>0\),

\[
 \mu_2(C_{\rm tan})\le\theta,\qquad
 \|B_{\rm cr}\|,\|D_{\rm cr}\|\le\theta,
 \qquad a_{\rm n}\ge\sqrt{1-z_*^2}-\theta,
 \qquad 8\theta<\sqrt{1-z_*^2}.
\tag{29}
\]

Choose the corridor around (28) in this order.  The two stable-coordinate
faces are inward and the two unstable-coordinate faces are outward at
\(\delta=0\); strictness persists for small \(r\).  The faces \(z=0\)
and \(H=\mathrm{const}\) are invariant.  On \(z=z_*\), shrink the collar
so that \(S\ge c_S>0\); then \(\dot z=-\delta Sz^3\le0\), strictly for
\(\delta>0\).  Hence all base and normal face conditions hold on a fixed
doubled collar.

The same backward graph-transform calculation as in V4, now applied to
(24), gives a unique \(C^3\) graph

\[
 A=\Gamma^{\rm sc}(z,H,B;\delta,a,\epsilon)
\tag{30}
\]

through \(\delta=0\), with mixed total order three and at most two
external derivatives.  The jet contraction rates are bounded below by

\[
 \sqrt{1-z_*^2}-(2j+2)\theta>0,
 \qquad 0\le j\le3.
\tag{31}
\]

For the corner attachment, substitute
\(\delta=r^2\), \(a=1+\sqrt\epsilon r^3a_2\), promote \(r\) to an
invariant base coordinate \(r'=0\), and run the order-three graph transform
once more on this extended field.  The substituted coefficients are
\(C^\infty\) in \(r\), and (29) and all face margins are unchanged.
This directly gives a joint \(C^3\) graph on the total-family base
\((z,r,H,B)\); it is not inferred by taking three \(r\)-derivatives of a
family for which only two external derivatives were asserted.  For
\(r>0\), uniqueness identifies the new graph with (30).  On the \(K_1\)
overlap its invariant coordinate is exactly \(r=r_1\sigma\).  Fixed
positive-parameter sheets are recovered only after the total-family graph
has been constructed.

For \(\delta>0\), blowing down (30) gives the maximal forward-staying graph
in the subordinate V4 corridor.  V4 uniqueness therefore identifies it
with \(\mathcal W^{\rm tail}_{\mathrm{out},\mu}\) on the overlap.  This
proves the required finite outer trace without using a V4 constant that
degenerates when its positive box is moved to \(r=0\).

## 5. Exact resolution of the \(K_1\) corner

Write \(s=\sqrt\epsilon\), and set

\[
 \sigma=\sqrt{\delta_1},\qquad
 \Pi=p_1/\delta_1,\qquad
 \Omega=\frac{1-v_1+(s/3)r_1^2}{\delta_1},
 \qquad a_1=\sigma^3a_2,qquad r=r_1\sigma.
\tag{32}
\]

The ambient coordinate is \(\Omega\), not
\((1-v_1+(s/3)r_1^2)/\delta_1^2\); the latter would discard the finite
stable fiber.  On the positive energy branch, use the same \(H\) as in
(23).  The exact resolved field in \(y_1\)-time is

\[
\begin{aligned}
 r_1'&=\frac{s}{2}\sigma^2\Pi r_1,&
 \sigma'&=-\frac{s}{2}\sigma^3\Pi,& H'&=0,\\
 \Pi'&=\Omega-\frac{s}{2}\sigma^2\Pi^2,\\
 \Omega'&=(2s+\epsilon r_1^2)\Pi-sq_1
              -s\sigma^2\Pi\Omega,\\
 q_1'&=\sigma^2
    \{1-r_1\sigma^3a_2-\tfrac32s\Pi q_1\}.
\end{aligned}
\tag{33}
\]

Here \(q_1>0\) is eliminated by the exact algebraic root

\[
\begin{aligned}
 6s q_1^2={}&8+3sr_1^2-12\Omega\sigma^2
 -(4sa_2r_1^3+12a_2r_1)\sigma^3\\
 &+6s\Pi^2\sigma^4+12\Omega a_2r_1\sigma^5
 +12H\sigma^6+4a_2^3r_1^3\sigma^9
 +sa_2^4r_1^6\sigma^{12}.
\end{aligned}
\tag{34}
\]

Equations (33)--(34) are \(C^\infty\) on a full quadrant collar.  At
\(\sigma=0\),

\[
 q_{10}(r_1)=\sqrt{\frac{8+3sr_1^2}{6s}},\qquad
 \Pi_0(r_1)=\frac{q_{10}(r_1)}{2+sr_1^2},\qquad \Omega_0=0,
\tag{35}
\]

and the two normal rates are

\[
 \pm\lambda_1(r_1,\epsilon),\qquad
 \lambda_1=\sqrt{s(2+sr_1^2)}
 \ge\lambda_*:=\sqrt2\,\epsilon_-^{1/4}>0.
\tag{36}
\]

In the raw \(K_1\) variables, (35) is precisely the singular outgoing
branch

\[
 \delta_1=0,\qquad p_1=0,\qquad
 v_1=1+\frac{s}{3}r_1^2,\qquad
 q_1=\frac2{\sqrt3\epsilon^{1/4}}
       \sqrt{1+\frac{3sr_1^2}{8}},\qquad a_1=0.
\]

The incoming core branch obtained from (39) is

\[
 r_1=0,\qquad p_1=\frac{q^+}{2}\delta_1,\qquad
 v_1=1-\frac{\delta_1^2}{6},\qquad
 q_1=q^+,\qquad a_1=a_2\delta_1^{3/2}.
\]

Both meet \(Z_+=(0,0,0,1,q^+,0)\).  They are the two axes of the
resolved directed chain, not one ordinary orbit before resolution.

The two transitions are exact and nonsingular on their positive overlaps:
\(r_1>0\) for the scaled outer chart and \(\sigma>0\) for \(K_2\).
Their boundary blowdowns are deliberately degenerate; the resolved field
(33)--(34), rather than either blowdown, is the regular corner chart.  To
the scaled outer chart,

\[
\begin{aligned}
 z&=(1+sr_1^2)^{-1},&
 \chi&=z^2\epsilon^{3/2}r_1^3q_1,\\
 A+B&=\epsilon r_1\Pi-\chi,&
 A-B&=\epsilon z r_1^2\Omega,
 \qquad H=H.
\end{aligned}
\tag{37}
\]

For \(\sigma>0\), the universal \(K_2\) variables are

\[
\begin{aligned}
 U&=r_1\sigma a_2-\sigma^{-2},&
 P&=-\epsilon^{1/4}\sigma^{-1}\Pi,\\
 Q&=-\epsilon^{1/4}\sigma^{-3}q_1,\\
 V&=(r_1\sigma)^2a_2^2
 +\frac{s}{3}(r_1\sigma)^5a_2^3
 -\sigma^{-4}\{1+(s/3)r_1^2-\sigma^2\Omega\},\\
 \widehat H&=H,\qquad
 \frac d{dy_1}=\epsilon^{1/4}\sigma\frac d{d\xi}.
\end{aligned}
\tag{38}
\]

On the invariant face \(r_1=0\), the exact core algebraic orbit is

\[
 \Pi=\frac1{\sqrt3\,\epsilon^{1/4}},\qquad
 \Omega=\frac{\sigma^2}{6},\qquad
 q_1=\frac2{\sqrt3\,\epsilon^{1/4}},\qquad H=0.
\tag{39}
\]

Substitution in (38) gives

\[
 (U,P,V,Q)=
 \left(-\sigma^{-2},-\frac1{\sqrt3\sigma},
       \frac16-\sigma^{-4},-\frac2{\sqrt3\sigma^3}\right),
\tag{40}
\]

which is the algebraic reference
\((-t^2/12,-t/6,1/6-t^4/144,-t^3/36)\) with
\(t=2\sqrt3/\sigma\).

### Resolved corner graph lemma

Choose \(M\) so large that the central slice (16) lies in
\(0<\sigma\le\sigma_0\), where \(\sigma_0\) is fixed below.  There are
fixed \(H\)- and stable-fiber collars on

\[
 0\le r_1\le R,\qquad 0\le\sigma\le\sigma_0,
\tag{41}
\]

and a unique codimension-one invariant graph over
\((r_1,\sigma,H,b_{\rm s})\) with the following properties.

- On \(r_1=R\) it is the pullback of (30) under (37).
- On a fixed positive-\(\sigma\) central overlap band, its \(r_1=0\)
  restriction is the resolved canonical core graph.
- It is state-\(C^3\), has mixed total order three with at most two
  derivatives in \((a_2,\epsilon)\), and its graph and normalized conormal
  extend jointly to both invariant faces.
- Restriction to \(r_1\sigma=r\), followed by either exact slice (16) or
  (20), preserves two derivatives in \(r\).

We prove the lemma rather than invoking an unscaled exchange principle.
First, the implicit derivative of (34) with respect to \(q_1\) is
\(12sq_1>0\) on a fixed positive-root collar.  The energy reduction and
all its state and parameter derivatives are therefore bounded there.
Straighten (35) and diagonalize the \((\Pi,\Omega)\) block.  Put the stable
coordinate \(b_{\rm s}\) in the base and call the unstable coordinate
\(n\).  Adapted metrics and a decrease of \(\sigma_0\), the \(H\)-width,
and the normal collar give

\[
 \mu_2(C_{\rm tan})\le\theta,\qquad
 \|B_{\rm cr}\|,\|D_{\rm cr}\|\le\theta,
 \qquad a_n\ge\lambda_*-\theta,
 \qquad 8\theta<\lambda_*.
\tag{42}
\]

The bounds hold on doubled collars of the invariant faces; no trace theorem
is used.  The continuous jet gaps are

\[
 \gamma_j\ge\lambda_*-(2j+2)\theta>0,
 \qquad 0\le j\le3.
\tag{43}
\]

These are the one-sided quotient gaps for the final codimension-one
matched hypersurface.  A separate two-sided estimate is needed for the
\(C^5\) auxiliary center graph used below.  There is also a small
dimensional point: the set (35) on \(\sigma=0\) does not itself contain the
zero-eigenvalue \(\sigma\)-direction.  We therefore compare with a reference
field on the whole strip \(0\le\sigma\le\sigma_0\).

After eliminating \(q_1\) by (34), freeze the base
\((r_1,\sigma,H)\) and define

\[
 r_1'=\sigma'=H'=0,\qquad
 \Pi'=\Omega,\qquad
 \Omega'=s(2+sr_1^2)\Pi-sq_{10}(r_1).
\]

This reference field has the compact saddle NHIM

\[
 \mathcal M_0=\{(\Pi,\Omega)=(\Pi_0(r_1),0)\}
\]

over \((r_1,\sigma,H)\), with normal rates (36).  Double its
\(r_1,\sigma,H\) faces.  On a fixed normal collar, the energy-reduced
field (33)--(34) differs from this reference field by
\(o_{C^1}(1)\) as \(\sigma_0\downarrow0\), while all derivatives through
order five remain bounded.  The \(a_2\)-term starts at order \(\sigma^3\)
and the \(H\)-term at order \(\sigma^6\).

In spectral coordinates \(c=(r_1,\sigma,H)\), \(b\) stable, and \(n\)
unstable, choose an independently adapted metric and shrink the collar so
that

\[
\begin{gathered}
 \max\{\mu_2(D_cF_c),\mu_2(-D_cF_c)\}\le\theta_{\rm c},\\
 \mu_2(D_bF_b)\le-\lambda_*+\theta_{\rm c},\qquad
 \partial_nF_n\ge \lambda_*-\theta_{\rm c},\\
 \text{every center--normal and stable--unstable cross block has norm }
 \le\theta_{\rm c},\qquad
 12\theta_{\rm c}<\lambda_* .
\end{gathered}
\]

The stable and unstable blocks are one-dimensional.  Their
normal-versus-center gaps
\(\lambda_*-(2j+2)\theta_{\rm c}\) are positive for \(0\le j\le5\).
Choose one sufficiently small time \(T>0\).  The doubled collar above and a
slightly smaller working collar give the common \(|t|\le T\) flow-domain
buffer required in
[the local relative overflowing NHIM theorem](../theory/RELATIVE_OVERFLOWING_NHIM.md).
Apply its Corollary 2 with

\[
 c=(r_1,\sigma,H),\qquad
 \lambda=(a_2,\epsilon),\qquad k=5.
\]

The positive-root calculation following (34), the displayed
\(o_{C^1}(1)\) comparison, the uniform fifth-derivative bounds, the doubled
flow collar, and the two-sided gaps above verify its four hypotheses.  That
result therefore gives a \(C^5\) locally invariant center graph

\[
 \mathcal S^{\rm c}:
 (\Pi,\Omega,q_1)
 =(\Pi_{\rm c},\Omega_{\rm c},q_{\rm c})
       (r_1,\sigma,H,a_2,\epsilon),
 \qquad \Pi_{\rm c}\ge c_\Pi>0.
\]

It is an auxiliary reference graph; uniqueness of the codimension-one
future sheet will come from the global staying graph below.  If
\(x=sr_1^2\) and
\(q_0=\sqrt{(8+3x)/(6s)}\), its invariance equation and (34) give

\[
\begin{aligned}
 \Pi_{\rm c}
 &=\frac{q_0}{2+x}
 -\sigma^3
   \frac{a_2r_1(x+3)}{3s q_0(2+x)}+O(\sigma^4),\\
 \Omega_{\rm c}
 &=\sigma^2\frac{x+4}{3(x+2)^3}+O(\sigma^4),\\
 q_{\rm c}
 &=q_0-\sigma^3\frac{a_2r_1(x+3)}{3s q_0}
   +O(\sigma^4).
\end{aligned}
\]

The remainders have the state and two external derivatives used below,
uniformly on the fixed compact cylinder.  The center graph is unique only for
the fixed doubled extension used in the local theorem.  It is not claimed
intrinsically unique: along the cubic \(\sigma\)-drift, different overflowing
extensions may differ by \(C^\infty\)-flat terms.  Its invariance recursion
nevertheless fixes the joint weighted five-jet.  On \(H=0,r_1=0\), that
jet agrees with (39); on \(\sigma=0\), algebraic equilibrium uniqueness
gives (35), and hence

\[
\begin{aligned}
 q_{10}(r_1)
 &=\frac2{\sqrt3\kappa}
   +\frac{\sqrt3\kappa}{8}r_1^2+O(r_1^4),\\
 \Pi_0(r_1)
 &=\frac1{\sqrt3\kappa}
   -\frac{5\sqrt3\kappa}{48}r_1^2+O(r_1^4).
\end{aligned}
\]

The axis jets and the joint \(C^5\) Taylor formula exclude all
other monomials of weighted degree at most four for weights
\(\operatorname{wt}(r_1,\sigma)=(2,1)\).  Terms involving \(H\) first
enter (34) at weighted degree six, and the first \(a_2\)-term has weighted
degree five.

Second, this actual center graph crosses the blown-up corner.  To see the
center flow without dividing by a vanishing hit speed, put

\[
 r=\varrho^3,\qquad r_1=\varrho^2X,\qquad
 \sigma=\varrho Y,\qquad XY=1,\qquad
 \mathfrak s=\varrho^2y_1.
\tag{44}
\]

This is the \(r\)-chart of the weight-\((2,1,3)\) blow-up.  Its adjacent
directional charts are

\[
\begin{array}{c|ccc}
 &r_1&\sigma&r\\ \hline
 \sigma\text{-chart}&\rho_{\rm e}^2x&\rho_{\rm e}
       &\rho_{\rm e}^3x\\
 r_1\text{-chart}&\rho_{\rm o}^2&\rho_{\rm o}y
       &\rho_{\rm o}^3y .
\end{array}
\]

On the entry overlap,
\(\varrho=\rho_{\rm e}x^{1/3}\),
\(X=x^{1/3}\), \(Y=x^{-1/3}\).  On the exit overlap,
\(\varrho=\rho_{\rm o}y^{1/3}\),
\(X=y^{-2/3}\), \(Y=y^{2/3}\).  We take the overlap faces at fixed
positive \(x\) and \(y\), so all transition maps and their required jets
are bounded.

The directional clocks
\(\mathfrak s_{\rm e}=\rho_{\rm e}^2y_1\) and
\(\mathfrak s_{\rm o}=\rho_{\rm o}^2y_1\) give, exactly,

\[
\begin{aligned}
 \frac{d\rho_{\rm e}}{d\mathfrak s_{\rm e}}
 &=-\frac{s}{2}\rho_{\rm e}\Pi,
 &\frac{dx}{d\mathfrak s_{\rm e}}
 &=\frac{3s}{2}\Pi x,\\
 \frac{d\rho_{\rm o}}{d\mathfrak s_{\rm o}}
 &=\frac{s}{4}\rho_{\rm o}y^2\Pi,
 &\frac{dy}{d\mathfrak s_{\rm o}}
 &=-\frac{3s}{4}y^3\Pi.
\end{aligned}
\]

The clock transitions are
\(\mathfrak s_{\rm e}=Y^2\mathfrak s\) and
\(\mathfrak s_{\rm o}=X\mathfrak s\).  Thus the signs on all common
faces agree whenever \(\Pi>0\).

With \(\kappa=\epsilon^{1/4}\), restriction of (33) to
\(\mathcal S^{\rm c}\), followed by the displayed invariance expansion,
gives the directed connector

\[
\begin{aligned}
 \Pi&=\frac1{\sqrt3\kappa}
 -\varrho^4\frac{5\sqrt3\kappa}{48}X^2+O(\varrho^5),\\
 \Omega&=\varrho^2\frac{Y^2}{6}+O(\varrho^4),\\
 q_1&=\frac2{\sqrt3\kappa}
 +\varrho^4\frac{\sqrt3\kappa}{8}X^2+O(\varrho^5),\\
 \frac{dX}{d\mathfrak s}
 &=\frac{\kappa}{2\sqrt3}XY^2+O(\varrho),
 &\frac{dY}{d\mathfrak s}
 &=-\frac{\kappa}{2\sqrt3}Y^3+O(\varrho).
\end{aligned}
\tag{45}
\]

The exact identity \((r_1\sigma)'=0\), together with
\(\Pi_{\rm c}\ge c_\Pi\), proves that the physical leaves of this graph
cross from entry to exit.  In the balance chart \(XY\) is preserved,
\(X\) increases and \(Y\) decreases.  Hence the displayed fixed overlap
faces are transverse.  The entry axis is identified by (39); the exit
axis is identified by (35) and then by (37).  No limit with
\(X\to0\) or \(Y\to0\) is taken inside the balance chart.  This explicit
three-chart calculation supplies the center-base transition that a normal
contraction estimate alone would miss.

Third, glue the resolved \(K_1\) block to the scaled outer block of
Section 4 along an open overlap collar about \(r_1=R\), using (37) and
the positive bounded clock factor in (22).  The face \(r_1=R\) is an
internal atlas interface, not an allowed exit.  On the \(K_1\) side use
\((r_1,\sigma,H,b_{\rm s})\) as base variables and the future-unstable
normal \(n\) as graph fiber.  On the outer side use
\((z,r,H,B)\) and the base--normal splitting of (29).

First fix one global positive clock.  It equals the \(\tau\)-field on the
outer block and equals
\(\rho_{\rm clk}X_{y_1}\) on the \(K_1\) block, where
\(\rho_{\rm clk}=\rho_{\rm clk}(r_1,\epsilon)>0\) is smooth, equals
\(r_1z\) on the overlap, and equals one near the core face.  Equation
(22) makes the definitions identical on the overlap.  Positive time
change preserves the oriented orbits and the staying set.

Next pull the outer cooriented unstable cone back by (37).  After shrinking
the overlap, it has a strict common subcone with the \(K_1\) unstable cone.
The agreement at the singular overlap is exact.  Put \(C=A+B\).  At
\(\sigma=0\), on a normal fiber of the energy-reduced field,

\[
 dC=\epsilon r_1\,d\Pi,\qquad
 dD=\epsilon z r_1^2\,d\Omega,\qquad
 d\Omega=\pm\lambda_1\,d\Pi,
\]

and

\[
 r_1z\lambda_1=\sqrt{1-z^2}.
\]

Thus the \(K_1\) stable and unstable eigenlines, after the clock conversion,
map exactly to the two eigenlines of (27).  Continuity gives common strict
secant and projective cones for small \(\sigma_0\) and small tube widths.
The glued tube is contractible, so this subcone has a global cooriented
line subbundle.  Choose a tubular fibration transverse to it and use its
fiber as the single normal graph coordinate; pull the two base projections
to the resulting common quotient.  Only after these graph projections have
been fixed do we use a partition of unity to glue the adapted metrics.
Thus the corridor charts, not just their norms, are compatible under (37).

For the clock transition,
\[
 D(\rho_{\rm clk}F)
 =\rho_{\rm clk}DF+F\otimes d\rho_{\rm clk}.
\]
Because \(\rho_{\rm clk}\) depends only on \(r_1\),
\(r_1'=O(\sigma^2)\) on the center graph, and the off-graph stable and
normal components are bounded by their tube widths \(w_{\rm s}\) and
\(w_{\rm n}\).  Hence every additional tangent or cross-block bound is at
most
\[
 C(\sigma_0^2+w_{\rm s}+w_{\rm n}).
\]
If \(c_0=\inf\rho_{\rm clk}>0\) on the transition collar, the common
order-\(j\) gap therefore satisfies

\[
 \gamma^{\rm glue}_j
 \ge
 \min\{\gamma^{\rm out}_j,\,
        c_0\gamma^{K_1}_j\}
 -C(\sigma_0^2+w_{\rm s}+w_{\rm n})>0,
 \qquad 0\le j\le3.
\]

Choose \(\sigma_0\) first and then \(w_{\rm s},w_{\rm n}\).  The strict
last inequality follows uniformly.  This estimate, rather than the
partition of unity by itself, proves the common vertical secant cone,
backward projective contraction, and three jet gaps.

Call the glued physical block \(\mathcal Q_{\rm match}\).  Its upper
\(\sigma\)-face is incoming, \(r_1=0\), \(\sigma=0\), \(z=0\), and the
energy faces are invariant, and the stable-fiber faces are inward.  The
total-family coordinate satisfies \(r'=0\), so the faces \(r=0\) and
\(r=r_*\) are invariant as well.  The two global unstable-normal faces
are outward by the strict common cone, and the seam \(r_1=R\) is not a
face.  All technical doubled faces are restricted back after the
construction.  Thus every positive-\(r\)
center characteristic that crosses \(r_1=R\) continues inside the outer
block; it is not discarded at the seam.  The maximal-forward-staying
graph theorem on \(\mathcal Q_{\rm match}\), with (31), (42), and (43),
gives

\[
 \mathcal W_{\rm match}
 =\{n=\mathcal N(r_1,\sigma,H,b_{\rm s};a_2,\epsilon)\}.
\tag{46}
\]

It is the unique staying graph in the glued physical block, is
state-\(C^3\), and has
mixed total order three with at most two derivatives in
\((a_2,\epsilon)\).  Parameter differentiation is performed on this fixed
doubled atlas; no moving hit time is differentiated.  On the outer
subblock, (46) and (30) have the same maximal-staying definition, so V4
uniqueness identifies them.  This is what supplies the terminal selection
through the \(K_1\) passage.

It remains to identify the \(r_1=0\) graph where it is actually used.
Put \(\sigma_{\rm c}=M^{-1/2}\) and fix a compact band
\(I_{\rm c}\Subset(0,\sigma_0]\) containing \(\sigma_{\rm c}\).  For
\(\sigma>0\), the exact crosswalk to the frozen weighted coordinates is

\[
\begin{aligned}
 e&=\sigma^2,&
 p_{\rm w}&=-\epsilon^{1/4}\Pi\sigma^2,&
 q_{\rm w}&=-\epsilon^{1/4}q_1,\\
 d&=q_{\rm w}+2/\sqrt3,&
 \omega&=\sigma^2\Omega,& E_{\rm flag}&=2H,\\
 a_{\rm w}&=d/\sigma^6,&
 b_{\rm w}&=(\Omega-\sigma^2/6)/\sigma^6,\\
 \zeta&=\{-\epsilon^{1/4}\Pi\sigma^2
       -h_7(\sigma^2,d,\sigma^2\Omega)\}/\sigma^{16}.
\end{aligned}
\tag{47}
\]

Use (47) in the safe direction: pull the already constructed frozen graph
\(\mathcal W^0_{\rm a}\) into the resolved chart, rather than trying to
deduce weighted divisibility from ordinary \(C^3\) bounds.  On
\(I_{\rm c}\), all powers of \(\sigma\) in (47) are bounded away from
zero, so this pullback is an ordinary \(C^4\) graph over a fixed base
patch.  The validated weighted corridor bounds place it strictly inside
the isolating block used for (46), and its positive orbit remains there.
It is therefore contained in the maximal-forward-staying graph (46).
Both sets are codimension-one graphs over the same restricted base;
uniqueness gives

\[
 \mathcal W_{\rm match}\cap
   \{r_1=0,\ \sigma\in I_{\rm c}\}
 =
 \mathcal W^0_{\rm a}\cap
   \{r_1=0,\ \sigma\in I_{\rm c}\}.
\]

This is a nonlinear staying-set identification.  The Jost tangent identity
(11) is used later to normalize its conormal, not to infer equality of two
nonlinear center manifolds.  No divisibility by \(\sigma^6\) or
\(\sigma^{16}\) is inferred from an ordinary \(C^3\) graph.  This
completes the proof of the resolved corner graph lemma.

On the fixed central section (16),

\[
 r_1=r\sqrt{M+ra_2}=O(r),\qquad
 \sigma=(M+ra_2)^{-1/2}=M^{-1/2}+O(r).
\tag{48}
\]

On \(I_{\rm c}\), the map (38) and its inverse have bounded \(C^3\)
jets.  The frozen graph is transverse to the fixed universal target
projection; that strict angle persists.  We therefore regraph every
nearby cut over that same universal base before taking a norm.  Evaluating
the total-family \(C^3\) graph and its first two base derivatives on (48)
then gives

\[
 \|G_{r,a_2,\epsilon}-G_0\|_{C^2}\le Cr
\]

and the mixed bounds in (5), with every derivative of (48) included.
Evaluation on \(r_1=R,\sigma=r/R\) is the exact outer restriction already
contained in the glued graph.  This proves Theorem V5(1)--(2).

## 6. Endpoint row and directed exchange

The endpoint calculation is a compatibility check, not the exchange
pairing.  In the state order
\((r_1,\delta_1,p_1,v_1,q_1,a_1)\), a left unstable row at the singular
point \(Z_+=(0,0,0,1,q^+,0)\) is

\[
 \ell_+=
 \left(0,-\sqrt{\frac23},\sqrt2\,\epsilon^{1/4},-1,0,0\right),
 \qquad q^+=\frac2{\sqrt3\epsilon^{1/4}}.
\tag{49}
\]

It has left eigenvalue \(+\sqrt2\,\epsilon^{1/4}\).

The incoming algebraic tangent is

\[
 \mathcal T_+=(0,1,q^+/2,0,0,0),
 \qquad \ell_+\mathcal T_+=0.
\tag{50}
\]

This vanishing is necessary because the algebraic tangent lies in the
future sheet.  It is not an exchange coefficient.

Along the exact core orbit, the immutable Jost calculation gives

\[
 B_2B_3=6\sqrt3,
 \qquad
 \psi(\mathbf u)=\omega(\mathbf s,\mathbf u)
 =24B_2B_3=144\sqrt3.
\tag{51}
\]

The overlap (38), together with the weighted crosswalk (47), sends the
projective limit of \(\psi\) to the line spanned by \(\ell_+\).  Thus
(50) and (51) refer to the same transported adjoint line but to different
tangent directions.

To anchor that line for positive parameters, write the scaled outer graph
as

\[
 g_{{\rm o},\mu}=A-\Gamma^{\rm sc}_\mu(z,H,B)=0,
 \qquad
 L_{{\rm o},\mu}^{\rm raw}=dA-D\Gamma^{\rm sc}_\mu,
 \qquad L_{{\rm o},\mu}^{\rm raw}(\partial_A)=1.
\tag{52}
\]

Transport this one row backward over the entire resolved graph tube.  If
\(P_\mu^{\rm o,c}\) denotes the graph-tube first-hit map from the central
cut to the outer cut, define

\[
 L_{{\rm c},\mu}^{\rm raw}
 =L_{{\rm o},\mu}^{\rm raw}\,DP_\mu^{\rm o,c}.
\tag{53}
\]

Equivalently it solves \(L'=-LDF_\mu\).  At chart changes it is pulled
back; it is never reselected.  The definition uses the already constructed
graph tube and does not presuppose a source connection.

For an arbitrary local extension \(\widetilde g\) of a section defining
function \(g\), the intrinsic section row is

\[
 L=d\widetilde g-
   \frac{d\widetilde g(F_\mu)}{dh(F_\mu)}\,dh.
\tag{54}
\]

It satisfies \(L(F_\mu)=0\) and is independent of the extension.  Three
normalizations of this same one-dimensional conormal line must be kept
separate:

1. \(L_{{\rm o},\mu}^{\rm raw}(\partial_A)=1\) is the raw outer endpoint
   normalization;
2. \(Dg_{\rm a}\) is the frozen certificate normalization on the central
   cut; and
3. \(\psi=\omega(\mathbf s,\cdot)\) is the frozen Jost normalization.

At \(r=0\), \(Dg_{\rm a}\) and \(\psi_{\rm c}\) annihilate the same
rank-three tangent space, so there is one fixed scalar \(c_{\rm J}\ne0\)
such that

\[
 \psi_{\rm c}=c_{\rm J}Dg_{\rm a}.
\]

Choose a fixed \(C^2\) transverse normal field \(N_{\rm c}(Z)\) with
\(Dg_{\rm a}(N_{\rm c})=1\).  The resolved graph lemma first gives a
central defining function \(\overline g_{{\rm c},\mu}\), chosen directly
in the fixed graph chart, whose intrinsic section row obeys

\[
 \overline L_{{\rm c},\mu}(N_{\rm c})=1,\qquad
 \overline L_{{\rm c},\mu}=Dg_{\rm a}+O_{C^1}(r).
\tag{55}
\]

For every \(r>0\), the raw transported row (53) spans the same line, so
there is a unique smooth nonzero multiplier on the final positive patch,

\[
 L_{{\rm c},\mu}^{\rm raw}
   =m(Z,\mu)\overline L_{{\rm c},\mu},
 \qquad
 m(Z,\mu)=L_{{\rm c},\mu}^{\rm raw}(N_{\rm c}).
\]

Its sign is fixed by (52).  No bounded extension of \(m\) to \(r=0\) is
asserted or needed: the matching operator uses the directly conditioned
row (55), while the raw row retains the exact endpoint cocycle.
The Jost-conditioned continuation is
\(L_{{\rm c},\mu}^{\rm J}=c_{\rm J}\overline L_{{\rm c},\mu}\).
Choose a \(C^2\) continuation \(\mathbf u_\mu\) of the frozen growing
complement on the fixed central cut.  At \(r=0\), (51) gives
\(L_{{\rm c},0}^{\rm J}(\mathbf u_0)=144\sqrt3\).  By (55),

\[
 L_{{\rm c},\mu}^{\rm J}(\mathbf u_\mu)
 =144\sqrt3+O(r)\ge72\sqrt3
\]

after imposing the corresponding threshold in the final choice of
\(r_{\rm p}\).  This proves (6).
For the source operator we retain the certificate-conditioned row (55).

## 7. Uniform finite-dimensional matching

Let \(S_\mu(\phi)\) be the V2 true-unstable source circle, represented in
the universal central chart, and let

\[
 y_\mu(\phi,t)=\Phi_\mu^t(S_\mu(\phi)),
 \qquad A_\mu(\phi,t)=D_\phi y_\mu(\phi,t).
\tag{56}
\]

Choose a defining function \(\overline g_{{\rm c},\mu}\) for the normalized
matched target in the fixed central flowbox, with section row
\(\overline L_{{\rm c},\mu}\) from (54)--(55).  Define, before solving for a
connection,

\[
 \mathfrak M_\mu(\phi,t)=
 \begin{pmatrix}
  \widetilde{\overline g}_{{\rm c},\mu}(y_\mu(\phi,t))\\
  h_{\rm c}(y_\mu(\phi,t))
 \end{pmatrix}.
\tag{57}
\]

Put \(s_\mu=dh_{\rm c}(F_\mu)=P\).  At a zero, exact row reduction gives

\[
\begin{aligned}
 \det D_{(\phi,t)}\mathfrak M_\mu
 &=s_\mu\,\chi_\mu,\\
 \chi_\mu
 &=\overline L_{{\rm c},\mu}A_\mu
 =\overline L_{{\rm c},\mu}
   \left(A_\mu-
    \frac{dh_{\rm c}(A_\mu)}{s_\mu}F_\mu\right).
\end{aligned}
\tag{58}
\]

This factorization is invariant under changing the extension in (54).
The first factor is the section speed, not an exchange coefficient.  The
second is the source-phase incidence, not the Jost pairing (51).

At \(r=0\), Proposition 8.4 and its bordered certificate prove

\[
 \chi_0
 =Dg_{\rm a}(z_N)D\Phi_0^T(z_0)v_0\ne0.
\tag{59}
\]

Transport from the certificate cut to (13) leaves this pairing unchanged.
Fix a closed phase--time product neighborhood of the certified zero before
varying \(r\).  V2 gives \(C^2\) convergence of the source and finite
central flow, while (55) gives \(C^1\) convergence of the target row.
Include in the final choice of \(r_{\rm p}\) the requirement that throughout
this preselected neighborhood

\[
 |\chi_\mu-\chi_0|<\frac12|\chi_0|,
 \qquad |s_\mu|\ge s_*>0.
\tag{60}
\]

The choice precedes the solution and is therefore noncircular.  All entries
of the \(2\times2\) matrix are bounded on the compact extended box; (58)--
(60) give a uniform inverse bound.  The parameter implicit-function theorem
produces unique \(C^2\) functions \(\phi_{\rm a}(\mu)\) and
\(t_{\rm a}(\mu)\).

The finite V2 gate anchor, inactive faces, event ordering, and
source-to-boundary distances have strict compact margins.  Under the same
final smallness requirement, the selected orbit stays in that first-hit
component.  Once it reaches (3), invariance and V4 local maximality keep it
in the positive future-staying channel.  This proves Theorem V5(3).

## 8. Truncated action and moving cuts

The chart primitives are pullbacks of (7), not independent choices.  On a
fixed-parameter state fiber, the universal pullback is

\[
 \lambda_\delta
 =\epsilon^{9/4}r^5(P\,dU-Q\,dV).
\tag{61}
\]

In \(K_1\), direct substitution gives

\[
\begin{aligned}
 \lambda_\delta
 =\epsilon^{5/2}r_1^4
 \bigl\{&(2p_1-4\delta_1^{-1}q_1v_1)\,dr_1\\
 &-r_1\delta_1^{-1}q_1\,dv_1\bigr\}.
\end{aligned}
\tag{62}
\]

Substitution of (21) into (62) gives the outer pullback recorded in V4,
and substitution of the \(K_2\)--\(K_1\) overlap into (62) gives (61).
Thus the forms agree exactly on both overlaps.

Let

\[
 H_{\rm ph}=\frac{-\mathcal G+\mathcal G(O)}{\delta}
 =\epsilon^{5/2}r^4\widehat H,
 \qquad \iota_{X_x}d\lambda_\delta=dH_{\rm ph}.
\tag{63}
\]

For a physical first-hit map \(P_\mu^{j,i}:C_i\to C_j\), define

\[
 \mathcal B_\mu^{j,i}(z)
 =\int_z^{P_\mu^{j,i}(z)}\lambda_\delta.
\tag{64}
\]

The variable-time first-variation identity is

\[
 (P_\mu^{j,i})^*\lambda_\delta-\lambda_\delta
 =d_Z\mathcal B_\mu^{j,i}
  +\tau_\mu^{j,i}\,d_ZH_{\rm ph}.
\tag{65}
\]

The last term must be retained on an energy-thick target.  For three ordered
cuts,

\[
 P_\mu^{k,i}=P_\mu^{k,j}\circ P_\mu^{j,i},
 \qquad
 \mathcal B_\mu^{k,i}
 =\mathcal B_\mu^{j,i}
  +\mathcal B_\mu^{k,j}\circ P_\mu^{j,i}.
\tag{66}
\]

Hence moving a subordinate cut adds one finite segment to one term and
subtracts the identical segment from its neighbor.  The raw
endpoint-anchored row is covariant for the same reason: if \(Q\) moves
the cut, then

\[
 L_{\rm c}^{\rm raw}=(L_{\rm c}^{\rm raw})'DQ,
 \qquad v_{\rm c}'=DQv_{\rm c},
 \qquad
 L_{\rm c}^{\rm raw}v_{\rm c}
 =(L_{\rm c}^{\rm raw})'v_{\rm c}'.
\tag{67}
\]

Conditioned rows acquire the corresponding ratio of normalization
multipliers; only the raw pairing in (67) is exactly cut-invariant.
The resolved graph, finite hit maps, section embeddings, and integrands have
the mixed \(C^2\) bounds established above.  Equations (65)--(67) may
therefore be differentiated twice in the external parameters.  This proves
Theorem V5(4) without taking \(z\downarrow0\) or asserting an action finite
part.

## 9. Evidence boundary

This proof closes the \(K_2\)--\(K_1\)--outer attachment and upgrades the V2
finite algebraic-directed label to a positive-parameter outer algebraic
exit.  It proves neither

- the divergent outer action subtraction or its finite part;
- an exhaustive two-end return--first-exit relation;
- symbolic coding of all bounded itineraries; nor
- temporal stability of any stationary PDE solution.

Those are the later V6--V7 and S1 obligations in the claim register.
