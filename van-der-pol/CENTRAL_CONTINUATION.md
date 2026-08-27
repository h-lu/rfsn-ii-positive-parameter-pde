# Uniform continuation of the compact van der Pol central package

**Evidence status: Proved.**  The only imported interval input is the
zero-parameter package frozen in
[CENTRAL_CORE_IMPORT.md](CENTRAL_CORE_IMPORT.md).  The positive-parameter
continuation, two-derivative estimates, weighted tails, local passage, and
compact first-event continuation are proved below.  This is not a persistence
theorem for the two noncompact ends or their matching.

## 1. Parameter wedge, phase convention, and theorem

Fix

\[
 0<\epsilon_-<\epsilon_+<\infty,
 \qquad A>0.
\tag{1}
\]

Choose \(r_{\rm w}>0\) so small that

\[
 2Ar_{\rm w}+\sqrt{\epsilon_+}A^2r_{\rm w}^4\le1,
 \qquad
 \sqrt{\epsilon_+}Ar_{\rm w}^3\le\frac12.
\tag{2}
\]

For \(0<r_*\le r_{\rm w}\), put

\[
 \mathcal P_{r_*}=[0,r_*]\times[-A,A]
                   \times[\epsilon_-,\epsilon_+],
 \qquad \mu=(r,a_2,\epsilon),
\tag{3}
\]

and map its positive part to the PDE parameters by

\[
 d=r^4,\qquad \delta=r^2,\qquad
 a=1+\sqrt\epsilon\,r^3a_2.
\tag{4}
\]

The closed box (3) is used to state uniformity; the physical wedge is its
nonempty part \(r>0\).  A \(C^2\) family on (3) means the restriction of a
\(C^2\) family on a neighborhood in
\(\mathbb R\times\mathbb R\times(0,\infty)\).  No regularity in the singular
inverse coordinates \((\delta,a)\) at \(r=0\) is implied.

Let \(F_\mu\), \(\widehat H_\mu\), \(\lambda\), and \(\mathcal R\) be the
universal central objects in equations (26)--(30) of
[MODEL_AND_CENTRAL_CHART.md](MODEL_AND_CENTRAL_CHART.md).  Thus

\[
\begin{aligned}
 U'&=P,\\
 P'&=c_\mu U-V-(1+\sqrt\epsilon r^3a_2)U^2
       +\frac{\sqrt\epsilon}{3}r^2U^3,\\
 V'&=Q,\qquad Q'=U,
\end{aligned}
\tag{5}
\]

where

\[
 c_\mu=2ra_2+\sqrt\epsilon r^4a_2^2,
 \qquad
 \lambda=P\,dU-Q\,dV,
 \qquad \iota_{F_\mu}d\lambda=d\widehat H_\mu.
\tag{6}
\]

For \(\eta>0\), set

\[
 X_\eta=\left\{Z\in C^0(\mathbb R,\mathbb R^4):
 \|Z\|_\eta=
 \sup_{\xi\in\mathbb R}e^{\eta|\xi|}|Z(\xi)|<\infty\right\}.
\tag{7}
\]

We also freeze one phase convention.  On the expanding plane put
\(\mathfrak J_\mu=(A_\mu-\alpha_\mu I)/\beta_\mu\), so
\(\mathfrak J_\mu^2=-I\).  Continue one
exact core unit vector by normalized Kato transport in the expanding Riesz
bundle, along the segment from \((0,a_2,\epsilon)\) to
\((r,a_2,\epsilon)\), take that vector and its \(\mathfrak J_\mu\)-image as the
oriented expanding frame, and use the reverser plus a positive radial
symplectic normalization to complete it to a reversible symplectic frame.
The family at \(r=0\) is independent of the dummy
parameters, so this gives one \(C^2\) oriented frame on (3).  The complete
core source circle is continued using this frame and the true unstable graph;
its transported label \(\phi\) is declared to be the common source phase.
Every local exact saddle chart is tangent-normalized to the same frame, and
its oriented-blow-up boundary phase is compared with \(\phi\) by its
\(C^3\)-in-phase, \(C^2\)-in-parameter, degree-one transition map.  This
fixes the lift in which numerical
phase gaps are compared; it is not an invariant claim about Euclidean angular
distance under arbitrary phase reparametrizations.

### Theorem V2

There are \(r_*>0\), \(0<\eta<1/\sqrt2\), and \(C<\infty\) for which the
following statements hold on (3).

1. **Uniform saddle-focus.**  The origin is the fixed homogeneous
   equilibrium, \(\widehat H_\mu(0)=0\), and

   \[
    \operatorname{spec}DF_\mu(0)
      =\{\alpha_\mu\pm i\beta_\mu,
           -\alpha_\mu\pm i\beta_\mu\},
    \quad
    \alpha_\mu=\tfrac12\sqrt{2+c_\mu},
    \quad
    \beta_\mu=\tfrac12\sqrt{2-c_\mu},
   \tag{8}
   \]

   with \(\alpha_\mu,\beta_\mu\ge1/2\).  Its local stable and unstable
   manifolds, fixed-domain graph parameterizations, and half-orbit
   parameterizations are \(C^2\) in \(\mu\), with two parameter derivatives
   satisfying uniform exponential estimates.

2. **Selected transverse homoclinic.**  There is a \(C^2\) map

   \[
    \mathcal P_{r_*}\longrightarrow X_\eta,
    \qquad \mu\longmapsto\Gamma_\mu,
   \tag{9}
   \]

   such that \(\Gamma_{(0,a_2,\epsilon)}=\Gamma_0\), the frozen selected
   core orbit, for every dummy pair \((a_2,\epsilon)\).  Each
   \(\Gamma_\mu\) is nonconstant, satisfies

   \[
    \Gamma_\mu(-\xi)=\mathcal R\Gamma_\mu(\xi),
    \qquad \Gamma_\mu(0)\in\operatorname{Fix}\mathcal R,
    \qquad \widehat H_\mu(\Gamma_\mu(\xi))=0,
   \tag{10}
   \]

   and is homoclinic to the origin.  For every multi-index
   \(|j|\le2\),

   \[
    |D_\mu^j\Gamma_\mu(\xi)|\le C e^{-\eta|\xi|}.
   \tag{11}
   \]

   The homoclinic is transverse modulo flow in the regular zero-energy
   hypersurface:

   \[
    T_zW^u_\mu(0)+T_zW^s_\mu(0)
       =T_z\widehat H_\mu^{-1}(0),
    \quad z\in\Gamma_\mu\setminus\{0\}.
   \tag{12}
   \]

   It is the unique symmetric orbit in one fixed continued sub-box of the
   frozen shooting box; no global uniqueness is asserted.

3. **Local exact passage with two external derivatives.**  A finite
   parameter cover carries \(C^2\) families of reversible exact symplectic
   saddle coordinates, exact incoming and outgoing section coordinates, and
   event-free slides to the physical saddle faces.  The charts are
   tangent-normalized to the phase frame fixed above.  On every overlap, the
   chart transition is exact symplectic and extends to the oriented real
   blow-up as a state-\(C^3\), parameter-\(C^2\) diffeomorphism with uniform
   mixed bounds; it preserves the signed axis faces and has degree one on the
   phase boundary.  For
   \(\sigma\in\{+,-\}\), the zero-energy passage preserves the transverse
   action \(\nu\) exactly and has universal-clock time and phase

   \[
   \begin{aligned}
    T_{\mu,\sigma}(\nu)
       &=-\alpha_\mu^{-1}\log|\nu|+t_{\mu,\sigma}
          +\tau_{\mu,\sigma}(\nu),\\
    \Delta_{\mu,\sigma}(\nu)
       &=\frac{\beta_\mu}{\alpha_\mu}\log|\nu|
          +b_{\mu,\sigma}+\rho_{\mu,\sigma}(\nu).
   \end{aligned}
   \tag{13}
   \]

   The notation in (13)--(14) is chartwise: on a cover member \(U_k\) we
   suppress the chart index \(k\).  For each fixed \(m\ge0\), there are
   \(\nu_{*,m}>0\) and \(C_m<\infty\), common on the finite cover, such that

   \[
    \max_{\substack{|\ell|\le2\\0\le j\le m}}
    \sup_{\substack{\mu\in U_k\\
                     0<|\nu|\le\nu_{*,m}}}
    \frac{|D_\mu^\ell D_{\log\nu}^j\tau_{\mu,\sigma}(\nu)|
          +|D_\mu^\ell D_{\log\nu}^j\rho_{\mu,\sigma}(\nu)|}
         {|\nu|(1+|\log|\nu||)}
    \le C_m,
    \qquad D_{\log\nu}=\nu\partial_\nu.
   \tag{14}
   \]

   This is weighted-log \(C^2\), not ordinary \(C^2\) in \(\nu\) at
   \(\nu=0\).

4. **Compact central event arrangement.**  The frozen reference source
   cell, homoclinic tube, two finite gate apertures, lateral faces, return
   aperture, stable cut, and all pre-event tubes have \(C^2\)
   parameter-dependent physical embeddings.  Their descriptions on the
   finite saddle-chart cover are \(C^2\) and agree through the physical
   overlap maps.  Their connected sign strata retain the same finite labelled
   clean stratification, neat boundary incidences, first-hit assignment, and
   fixed corner priority.  After the normalization used to define \(m_0\) in
   the import note, every rank, speed, separation, phase-cut, containment,
   inactive-face, empty-incidence, and strict event-order margin is at least
   \(m_0/2\).  The continued cells still exhaust the same fixed central
   outgoing and return bands; there is no unlabelled residual component.

5. **Source phases and order.**  In the fixed phase lift, the selected
   homoclinic phase, the two gate-anchor phase traces, the pole-gate source
   arc, and the residual-phase templates depend \(C^2\) on \(\mu\).  Their
   cyclic order is unchanged.  The continued algebraic-directed--homoclinic,
   algebraic-directed--pole-directed, and homoclinic--pole-directed gaps are
   respectively greater than

   \[
    0.052407,\qquad 0.16324,\qquad 0.110835.
   \tag{15}
   \]

   All represented traces remain in a proper phase arc with a complementary
   cut gap at least \(m_0/2\).

The word “gate” in items 4--5 is essential.  This theorem does not say that
an orbit passing either finite gate enters a positive-parameter pole or a
positive-parameter algebraic future-staying channel.

## 2. Uniform \(C^2\) stable and unstable manifolds

Write

\[
 F_\mu(Z)=A_\mu Z+N_\mu(Z),
 \qquad N_\mu(0)=D_ZN_\mu(0)=0.
\tag{16}
\]

By (2), \(|c_\mu|\le1\), and (8) follows directly from the characteristic
polynomial \(\zeta^4-c_\mu\zeta^2+1\).  The second inequality in (2) also
gives \(a\ge1/2>0\) on the physical wedge.

The polynomial family (5) extends smoothly to negative \(r\) and is \(C^2\)
in \(\mu\) on an open neighborhood of (3).  Its stable and unstable Riesz
projections \(\Pi_\mu^s,\Pi_\mu^u\) are therefore \(C^2\).  Choose fixed
rates

\[
 0<\eta<\eta_1<a_0<
 \inf_{\mu\in\mathcal P_{r_{\rm w}}}\alpha_\mu.
\tag{17}
\]

After shrinking \(r_{\rm w}\), if necessary, restriction of the moving
projections to the core stable and unstable planes gives \(C^2\) linear
isomorphisms

\[
 J_\mu^{s,u}:E_0^{s,u}\longrightarrow E_\mu^{s,u}
\tag{18}
\]

whose norms and inverse norms are uniform.  Repeated Duhamel differentiation
and finite-dimensional spectral calculus give, for \(|j|\le2\),

\[
\begin{aligned}
 \|D_\mu^j(e^{A_\mu t}\Pi_\mu^s)\|
   &\le K_j(1+t)^{|j|}e^{-a_0t},&&t\ge0,\\
 \|D_\mu^j(e^{A_\mu t}\Pi_\mu^u)\|
   &\le K_j(1+|t|)^{|j|}e^{a_0t},&&t\le0.
\end{aligned}
\tag{19}
\]

Cut off \(N_\mu\) by one \(\mathcal R\)-invariant radial cutoff, equal to one
on a ball of radius \(\delta_0\), and call the result
\(\widetilde N_\mu\).  Its common Lipschitz constant
\(L_{\delta_0}\) tends to zero with \(\delta_0\).  On

\[
 X^-_{\eta_1}=
 \left\{Z:(-\infty,0]\to\mathbb R^4:
  \sup_{t\le0}e^{-\eta_1t}|Z(t)|<\infty\right\},
\tag{20}
\]

define, for \(b\in E_0^u\),

\[
\begin{aligned}
 (\mathcal T_{\mu,b}Z)(t)={}&e^{A_\mu t}J_\mu^u b
 +\int_0^t e^{A_\mu(t-s)}\Pi_\mu^u
       \widetilde N_\mu(Z(s))\,ds\\
 &+\int_{-\infty}^t e^{A_\mu(t-s)}\Pi_\mu^s
       \widetilde N_\mu(Z(s))\,ds.
\end{aligned}
\tag{21}
\]

Let \(D_0<\infty\) be the sum of the two weighted convolution constants
coming from the gaps \(a_0-\eta_1\) and \(a_0+\eta_1\), and let
\(K=\max\{K_0,1\}\).  On the closed radius-\(\delta_0\) ball,

\[
\begin{aligned}
 \|\mathcal T_{\mu,b}Z\|_{\eta_1,-}
   &\le K\sup_\mu\|J_\mu^u\|\,|b|
       +K L_{\delta_0}D_0\delta_0,\\
 \|\mathcal T_{\mu,b}Z-\mathcal T_{\mu,b}\widetilde Z\|_{\eta_1,-}
   &\le K L_{\delta_0}D_0
          \|Z-\widetilde Z\|_{\eta_1,-}.
\end{aligned}
\tag{22}
\]

Choose \(\delta_0\) so that \(K L_{\delta_0}D_0\le1/2\), and then choose
\(b_*>0\) so that

\[
 K\sup_\mu\|J_\mu^u\|b_*\le\delta_0/2.
\tag{23}
\]

Thus (21) is a uniform self-map and contraction.  After one or two parameter
derivatives, the kernels in (19) contain at most quadratic polynomial factors
in \(|t-s|\); the gaps in (17) make their weighted integrals finite.  The
terms containing \(D_\mu\widetilde N_\mu\),
\(D_\mu^2\widetilde N_\mu\), and the state derivatives of
\(\widetilde N_\mu\) are uniformly bounded on the cutoff ball.  Hence
\((\mu,b,Z)\mapsto\mathcal T_{\mu,b}Z\) is \(C^2\) into
\(X^-_{\eta_1}\).  The parameterized contraction theorem gives a \(C^2\)
fixed point \(z^u(\mu,b)\).

The value

\[
 G_\mu^u(b)=z^u(\mu,b)(0)
\tag{24}
\]

parameterizes \(W^u_{\rm loc,\mu}(0)\).  Moreover,

\[
 b=(J_\mu^u)^{-1}\Pi_\mu^uG_\mu^u(b),
\tag{25}
\]

so the inverse graph coordinate is explicitly \(C^2\).  The fixed point and
its two parameter derivatives satisfy uniform exponential bounds.  The
analytic state dependence permits the same Lyapunov--Perron equation to be
differentiated three times in \(b\) and twice in \(\mu\); the convolution
gaps are unchanged.  Thus the trace graphs used below are
\(C^2_\mu(C^3_b)\), with uniform mixed bounds.  The
forward construction gives the stable manifold.  Uniqueness and the
reversible cutoff give

\[
 W^s_{\rm loc,\mu}(0)=\mathcal R W^u_{\rm loc,\mu}(0).
\tag{26}
\]

This proves item 1.

## 3. Reversible matching and weighted full-orbit tails

Let \(S_0(\phi)\), \(\phi\in\mathbb R/2\pi\mathbb Z\), be the complete
certified radius-\(R\), \(R=1/100\), source circle in equation (7) of the
import note.  Use the algebraic unstable graph coordinates from the exact
moving frame, and write the change from the normalized Kato frame to that
algebraic frame as

\[
 C_{\rm AK}(\mu)=\sigma(\mu)R_{\chi(\mu)},
 \qquad \sigma(\mu)>0,\qquad R_{\chi(\mu)}\in SO(2).
\tag{27}
\]

The scalar factor in (27) changes radial normalization but not phase.  Define

\[
 u_R(\mu,\phi)=R R_{\chi(\mu)}
       \binom{\cos\phi}{\sin\phi},\qquad
 S_\mu(\phi)=T_\mu\bigl(u_R(\mu,\phi),
                         H_\mu(u_R(\mu,\phi))\bigr).
\tag{28}
\]

The radius is exactly \(R\), and the phase map has degree \(+1\).  The true
graph and exact moving frame make (28) a \(C^2\) family of embeddings.  On
the complete \(r=0\) face, \(c=\chi=0\), the moving vector field is
independent of the dummy parameters, and local unstable-graph uniqueness in
the same coordinates identifies the selected graph with the imported core
graph.  Hence (28) is pointwise the frozen circle \(S_0\).  This direct
graph-boundary definition replaces an
unquantified backward-flow source construction: the validated radius-\(R\)
graph is already a common source domain.  By definition of the common Kato
source phase, \(\theta_\mu(S_\mu(\phi))=\phi\).  Now choose a compact phase
interval \(I\) about the selected homoclinic root and put

\[
 M(\mu,\phi,T)
  =(P,Q)\bigl(\Phi_\mu^T(S_\mu(\phi))\bigr).
\tag{29}
\]

At \(r=0\), (29) is independent of \(a_2,\epsilon\) and is exactly the
frozen matching map.  Choose a closed sub-box \(B_{\rm sh}\) of the
validated shooting box with the core zero in its interior.  Choose a smaller
root neighborhood \(B_{\rm root}\Subset B_{\rm sh}\).  Frozen local
uniqueness and compactness give

\[
 \inf_{B_{\rm sh}\setminus B_{\rm root}}|M(0,\phi,T)|>0.
\tag{30}
\]

The derivative in \((\phi,T)\) at the root has determinant in the interval
(9) of the import note.  The uniform \(C^2\) implicit-function theorem over
the compact dummy base gives a unique \(C^2\) pair

\[
 \phi_{\rm h}(\mu),\qquad T_{\rm h}(\mu)
\tag{31}
\]

inside \(B_{\rm root}\).  Uniform \(C^0\) closeness and (30) exclude another
zero in \(B_{\rm sh}\).  After decreasing \(r_*\),

\[
 \left|\det D_{(\phi,T)}M
       (\mu,\phi_{\rm h}(\mu),T_{\rm h}(\mu))\right|
 \ge\frac{149.56393055300413}{2}.
\tag{32}
\]

Let

\[
 z_\mu^{\rm sym}=\Phi_\mu^{T_{\rm h}(\mu)}
              (S_\mu(\phi_{\rm h}(\mu))).
\tag{33}
\]

Then \(z_\mu^{\rm sym}\in\operatorname{Fix}\mathcal R\).  To retain the
no-earlier-symmetry property, do not treat this codimension-two section as a
scalar event face.  On a fixed compact subinterval ending before the core hit,
the frozen certificate gives a positive minimum of \(P^2+Q^2\); this minimum
remains positive.  Near the endpoint,

\[
 \partial_T(P,Q)\bigl(\Phi_\mu^T(S_\mu(\phi_{\rm h}(\mu)))\bigr)
   =(P',Q')
\tag{34}
\]

is nonzero at the core endpoint and remains uniformly nonzero.  A fixed
one-dimensional flow-box coordinate then shows that \((P,Q)\) has no second
zero in the final time interval.  Thus (33) is still the first symmetry hit
after the selected source face inside the continued tube.

Define

\[
 \Gamma_\mu(\xi)=
 \begin{cases}
   \Phi_\mu^\xi(z_\mu^{\rm sym}),&\xi\le0,\\
   \mathcal R\Gamma_\mu(-\xi),&\xi\ge0.
 \end{cases}
\tag{35}
\]

The negative half reaches \(S_\mu(\phi_{\rm h}(\mu))\) at
\(-T_{\rm h}(\mu)\).  That source lies on the true local unstable graph, so
its negative orbit converges to the origin.  Reversibility and uniqueness
make (35) a smooth full solution, and (26) puts its positive half in
\(W^s_\mu(0)\).  Compact separation of (33) from the origin makes it
nonconstant.

Both invariant manifolds lie on zero energy: energy is constant along a half
orbit and tends to \(\widehat H_\mu(0)=0\) at its infinite end.  This proves
(10), including the mandatory equilibrium-energy subtraction built into
\(\widehat H_\mu\).

We now close the full weighted-tail statement.  Choose a fixed

\[
 T_*>\sup_{\mu\in\mathcal P_{r_*}}T_{\rm h}(\mu)+1.
\tag{36}
\]

The uniform backward contraction on the true graph makes
\(z_\mu^-:=\Gamma_\mu(-T_*)\) lie strictly inside the local unstable graph
domain.  Define its fixed-domain graph coordinate by the explicit inverse
(25):

\[
 b_-(\mu)=(J_\mu^u)^{-1}\Pi_\mu^u z_\mu^-.
\tag{37}
\]

The finite middle flow and (31) make \(z_\mu^-\) and \(b_-(\mu)\) \(C^2\).
The Lyapunov--Perron characterization, together with uniqueness of the
original flow, gives the exact tail identities

\[
\begin{aligned}
 \Gamma_\mu(\xi)
   &=z^u(\mu,b_-(\mu))(\xi+T_*),
       &&\xi\le-T_*,\\
 \Gamma_\mu(\xi)
   &=\mathcal Rz^u(\mu,b_-(\mu))(T_*-\xi),
       &&\xi\ge T_*.
\end{aligned}
\tag{38}
\]

The fixed point in (38) remains inside the radius-\(\delta_0\) ball, so the
cutoff and original vector fields agree on the entire represented tails.
Equations (19)--(23), (37), and the fixed shifts in (38) give \(C^2\)
dependence in \(X_{\eta_1}\) on both tails.  Finite-time variational
equations give \(C^2\) dependence on \([-T_*,T_*]\).  Restricting to
\(\eta<\eta_1\) proves (9) and (11), including the two parameter derivatives.

At the core, equation (11) of the import note gives transversality in the
regular energy surface.  On a compact fundamental segment, regularity of the
energy level and the least angle between the two tangent planes modulo the
flow direction have positive minima.  The \(C^1\) dependence of invariant
manifolds and finite flow retains those minima after a further decrease of
\(r_*\).  Flow invariance transports the result along the rest of each
nonconstant orbit.  This proves (12) and completes item 2.

## 4. Reversible exact saddle passage

The physical saddle data required by the imported local theorem are continued
before that theorem is applied.  The compact closures of the frozen incoming
and outgoing physical faces lie in the regular part of \(H_0^{-1}(0)\).
Choose fixed ambient defining functions and a finite tubular cover.  On each
piece choose a transverse field \(Y\) with
\(dH_0(Y)\ge\kappa_H>0\).  The equation

\[
 \widehat H_\mu(\Phi_Y^{s_\mu(z)}z)=0
\tag{39}
\]

has a unique \(C^2\) solution \(s_\mu(z)\) by the uniform implicit-function
theorem.  A fixed tubular gluing gives \(C^2\) embeddings of the physical
faces into \(\widehat H_\mu^{-1}(0)\).  The frozen flow transversality,
block-containment, and event-free collar distances have positive compact
margins, so the same faces bound a common saddle block and the punctured
long-passage collar remains event-free.  The finite orbit slides within the
frozen flow boxes continue by their transverse scalar first-hit equations;
their times and endpoint maps are \(C^2\) in \(\mu\).

The other hypotheses of the imported saddle-coordinate theorem are now
explicit:

- the state primitive \(\lambda\), symplectic form \(d\lambda\), and reverser
  \(\mathcal R\) are fixed;
- (5)--(6) are polynomial in the state and \(C^2\) in \(\mu\), hence analytic
  on one common complex state ball with \(C^2\) analytic-norm dependence; and
- (8) supplies the uniform saddle-focus gap.

Proposition 2.7 of the frozen source, with regularity order two, gives
parameter-local reversible exact symplectic saddle charts.  Postcomposition
with the unique linear symplectic phase rotation and radial normalization
makes every chart tangent-normalized to the Kato frame fixed in Section 1.
This normalization does not change the normal form, exact transverse action,
or weighted-log estimates.

On an overlap, the transition is the composition of one analytic exact
symplectic saddle chart with the inverse of the other.  It preserves the
stable and unstable axes, and tangent normalization gives a uniformly
invertible axis derivative.  Taylor division by the corresponding radial
variables therefore lifts the transition and its inverse to the oriented real
blow-up.  The analytic state norm and its two parameter derivatives are
uniform on a smaller common ball, so the lifted maps have the state-\(C^3\),
parameter-\(C^2\) mixed bounds required by the admissible-marking change.
Their boundary circle maps have degree one.  Separately, each transition from
a normalized local boundary phase to the transported source phase is a
\(C^2\) degree-one circle diffeomorphism, equal to the frozen transition at
\(r=0\).  All source-phase comparisons below are made after this transition;
no local angle gauge is silently identified with another.

Compactness of (3) gives a finite parameter cover.  Taking the minimum section
width and maximum constant on that finite cover, for each fixed \(m\), gives
(13)--(14).  The auxiliary radial faces lie in the common event-free saddle
collar.  Their orbit slides to the physical faces have the \(C^2\) dependence
obtained from the scalar first-hit equations above.  This proves item 3.

The clock in (13) is \(\xi\).  For \(r>0\), physical PDE length and central
action are recovered only through

\[
 dx=r\epsilon^{-1/4}d\xi,
 \qquad
 \lambda_\delta=\epsilon^{9/4}r^5\lambda.
\tag{40}
\]

No clock factor is absorbed into (13).

## 5. Continuation of the compact first-event arrangement

We spell out the compactness and mixed-parameter argument because continuing
a few sample orbits would not prove the exhaustive labelled arrangement in
item 4.

Freeze the finite cell, corner, and flow-box atlases from Section 4 of the
import note.  Away from the critical point, use the energy-normal projection
(39) to embed the fixed abstract source, event, and return cells in the moving
zero-energy surface.  Include the moving stable and unstable trace functions,
obtained from Section 2, among the pulled-back defining functions.  Keep the
ambient cooriented event germs in the fixed central state coordinates,
shrinking their flow boxes if necessary.

The resulting cell embeddings, finite flows, and pulled-back defining
functions are \(C^3\) in the state variables and \(C^2\) in \(\mu\).  As
\(r\to0\), their state \(C^3\) values converge uniformly to the core objects,
uniformly in the dummy parameters.  Their mixed parameter derivatives through
order two are uniformly bounded; they are not asserted to converge to zero.

There are finitely many normalized quantities entering \(m_0\):

- least singular values of active conormal matrices, including boundary
  conormals at neat incidences;
- distances excluding every reference-empty incidence;
- event speeds and common flow-domain buffers;
- strict inactive-face signs and no-earlier-hit gaps on the whole compact
  pre-event tubes;
- strict event-order gaps away from specified simultaneous faces;
- distances between aperture closures and from anchors to cell boundaries;
  and
- the proper phase-arc and angular-cut gaps.

Uniform state-norm convergence and compactness let us decrease \(r_*\) so that
each perturbed normalized quantity differs from its base value by less than
\(m_0/2\).  The active ranks and every strict inequality therefore retain the
lower bound \(m_0/2\).  At a simultaneous corner, active ranks and the fixed
priority remain; no positive separation between simultaneous event times is
asserted.

For each assigned cell, the positive event speed and earlier-hit margins give
a unique first-hit time by Lemma 5.3 of the frozen source.  The
implicit-function formula makes that time \(C^3\) in the source state and
\(C^2\) in \(\mu\).  It retains the assigned event, inactive signs, and
ordering inequalities on the whole compact pre-event tube.

It remains to continue every incidence and connected component with two
parameter derivatives.  On a fixed reference cell let \(h_j^0\) be the
finite defining functions and \(h_{j,\mu}\) their moving pullbacks.  Put

\[
 H_j(z,t,\mu)=(1-t)h_j^0(z)+t h_{j,\mu}(z),
 \qquad 0\le t\le1.
\tag{41}
\]

The conormal and empty-incidence margins put (41) in the setting of
Proposition 5.2 of the frozen source for every fixed \(\mu\).  Its controlled
lift can be chosen \(C^2\) in \(\mu\), as follows.  Freeze a common finite
active-star cover and boundary-tangent partition of unity from the core
arrangement.  On a star \(\mathcal U_\alpha\), let
\(A_{\alpha,t,\mu}\) be the matrix of all face conormals which can vanish
there, restricted to the tangent space of the active boundary stratum.  The
uniform neat-rank bound gives the right inverse

\[
 R_{\alpha,t,\mu}
  =A_{\alpha,t,\mu}^*
    (A_{\alpha,t,\mu}A_{\alpha,t,\mu}^*)^{-1},
\tag{42}
\]

with uniform state derivatives and two parameter derivatives.  The local
boundary-tangent lift

\[
 W_{\alpha,t,\mu}
   =-R_{\alpha,t,\mu}\,\partial_tH_{\alpha,t,\mu}
\tag{43}
\]

satisfies
\(\partial_tH_j+dH_j(W_{\alpha,t,\mu})=0\) for every face which can be
active on its support.  The fixed controlled partition of unity therefore
glues (43) to a global boundary-tangent field \(W_{t,\mu}\) satisfying the
same identity on every zero face.  Equations (41)--(43) show directly that
\(W_{t,\mu}\) is \(C^2\) in \(\mu\).  The parameter variational equations for
its compact-time flow give a \(C^2\) family of ambient isotopies.

The isotopy carries every labelled zero face of \(h^0\) to that of
\(h_\mu\), preserves boundary faces and signs, and gives a bijection of
connected components.  It transports the finite disjoint sign-cell identity
at the core to the moving cells.  Lemma 5.3 supplies the retained event
assignment on each transported component.  Consequently the outgoing and
return bands are still exhausted and no residual component can appear.
Descriptions on two local saddle-chart patches agree because both represent
this same physical isotopy and physical first-hit relation.  This proves
item 4.

## 6. Phase traces and ordering margins

The transported full source circle (28) carries the common lifted label
\(\theta_\mu(S_\mu(\phi))=\phi\).  Hence the homoclinic phase is exactly the
\(C^2\) function in (31), rather than an unrecorded reparametrization of it.
Define the two continued anchors and the closed pole-gate arc as the points
and phase subarc with the same transported labels on \(S_\mu\).  The
first-hit continuation and the physical isotopy in Section 5 put these
subsets in the corresponding moving gate strata.  Their phase traces are
therefore \(C^2\).  The signed residual-phase templates combine the \(C^2\) saddle
coefficients in (13) with bounded \(C^2\) event-free slides, so they have the
same regularity after composition with the degree-one boundary transition
fixed in Section 4.

The certified base gaps may therefore be compared in one lift.  At \(r=0\),
the algebraic-directed--homoclinic, algebraic-directed--pole-directed, and
homoclinic--pole-directed gaps exceed respectively

\[
 0.104814,\qquad 0.32648,\qquad 0.22167.
\tag{44}
\]

Uniform continuity on the compact parameter box, followed by the final
decrease of \(r_*\), retains half of each bound, giving (15).  The normalized
proper-arc cut margin is one of the quantities already retained at
\(m_0/2\).  Thus none of the cyclic orders, cuts, signs, or anchor labels
changes.  Item 5 follows.

## 7. Parameter and dependency audit

Every object used above has the following regularity in the blown-up
parameters:

| object | state regularity used | parameter regularity proved |
|---|---:|---:|
| central vector field and Hamiltonian | analytic | \(C^2\) (indeed smooth) |
| local invariant graphs and homoclinic in \(X_\eta\) | smooth | \(C^2\) |
| local saddle passage at \(\nu=0\) | weighted-log | \(D_\mu^\ell\), \(|\ell|\le2\) |
| compact event faces and cell embeddings | \(C^3\) | \(C^2\) |
| compact first-hit times and maps | \(C^3\) | \(C^2\) |
| phase traces, cuts, and compact margins | finite-dimensional | \(C^2\) |

The inverse parameter map is singular at \(r=0\): for example,

\[
 a_2=\frac{a-1}{\sqrt\epsilon\,\delta^{3/2}}.
\tag{45}
\]

Accordingly, the table does not claim unweighted \(C^2\) bounds in
\((\delta,a)\) at the cusp tip.  Equations (40) and (45), rather than an
unstated chain-rule uniformity, are the interface for later physical
time/action estimates.

This theorem discharges V2 only.  It proves no positive-parameter pole
compactification, outer future-staying hypersurface, central--outer matching,
end action finite part, exhaustive return--first-exit theorem, coding, or
temporal stability.  Those remain the separate obligations V3--V7 and S1.
