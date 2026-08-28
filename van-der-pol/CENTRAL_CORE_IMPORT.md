# Frozen central core package for Track V

**Evidence status: Imported (frozen source-verifiable interval
certificates).**  This
note freezes exactly the saddle-focus, one selected symmetric homoclinic, and
one compact central first-event arrangement used at the base point of V2.  It
does not import either noncompact end, a positive-parameter theorem, a return
map, an action finite part, or symbolic dynamics.  The frozen source reports
successful outward-rounded interval certificates.  This repository has
checked the immutable source and hashes, but does not claim an independent
machine replay.

## 1. Immutable source and citation-level location

The source is H. Lu, *First returns, singular exits, and action finite parts
near a reversible Hamiltonian saddle-focus*, repository
<https://github.com/h-lu/reversible-rfsn-ii-waves>, at commit

\[
 \mathtt{d54add098545063d5efe8f1d6f062d4cfc116a0d}.
\tag{1}
\]

The imported statements are located as follows in the manuscript frozen at
(1):

- Definition 2.1(I1)--(I3): analytic saddle block, transverse homoclinic
  tube, and compact physical event arrangement;
- Proposition 2.7: parameter-local reversible exact saddle-focus
  coordinates and the weighted-log local-passage estimates;
- Proposition 2.11: transverse homoclinics produce the finite matching
  hypothesis;
- Definition 2.8(H2) and Proposition 5.2: the finite clean/neat event
  arrangement and its component-preserving stability;
- Lemma 5.3: compact first-hit stability;
- Proposition 8.4 and equation (8.41): the certified finite source anchor;
- equations (8.49)--(8.52): the pole-gate first-hit interval and strict
  gate inequalities;
- Proposition 8.6, only its verification of Definition 2.1(I1)--(I3); and
- equations (8.36)--(8.40) and the finite incidence check immediately after
  the validated source-phase figure.

The relevant frozen hashes are

    papers/paper-a/manuscript/main.tex
    0baf6335aad72d5893479d8876d2613671ecb8ac2ccd73664405dea4381e6a20

    papers/paper-a/manuscript/main.pdf
    67888cf8b61b34c923cf55bd69ee41cab69493be6fc275533c8f5a074f1e96c5

    validation/replay_manifest.json
    15905f5a20b24a0ae0d298d9d14aa940177a006cc2cce3f2a39fd2e1cf4dac9b

    validation/environment.lock.json
    6240ebdbf0f296738534c07a33aea40202883f6abf37e1ff28e43dad47aa0cba

    validation/universal-core-symmetric-homoclinic/certificate.json
    ed0f9f58f8ba5f1d5c36dc7c3a72bb725599c4172a3cd610d890b88699fecfbd

    validation/origin-algebraic-heteroclinic/certificate.json
    60882ee1d3b2b18264b85764288505ae8b47d00bc826a2bddec152898f690fbe

    validation/future-target-fold/certificate.json
    88fa64035bb4352f5e25aa8d1627b191936264958c125dface59c5a767f6b3ce

    validation/origin-unstable-pole-entry/certificate.json
    7f325a87810f8b0dda2542aed90263b39f9a9f4bd2e8ebb3abcc238d032eb6e2

The last three packages are used here only to certify finite source anchors,
the finite target graph needed to define one gate, and strict first hits of
fixed central gates.  Their subsequent noncompact conclusions are outside
this import.

## 2. Exact core conventions

The ordered state is \(z=(U,P,V,Q)\), and the core vector field is

\[
 U'=P,\qquad P'=-U^2-V,\qquad V'=Q,\qquad Q'=U,
\tag{2}
\]

and the prime is the universal core clock.  The fixed primitive,
Hamiltonian, and reverser are

\[
 \lambda_0=P\,dU-Q\,dV,
 \qquad
 H_0=\frac12(Q^2-P^2)-\frac13U^3-UV,
\tag{3}
\]

\[
 \mathcal R(U,P,V,Q)=(U,-P,V,-Q),
 \qquad \mathcal R^*\lambda_0=-\lambda_0,
 \qquad \iota_{F_0}d\lambda_0=dH_0.
\tag{4}
\]

The origin has spectrum

\[
 \{(1+i)/\sqrt2,(1-i)/\sqrt2,
       (-1+i)/\sqrt2,(-1-i)/\sqrt2\}.
\tag{5}
\]

In the exact linear hyperbolic coordinates \(u=(u_1,u_2)\) and
\(s=(s_1,s_2)\),

\[
\begin{aligned}
 U&=u_1+s_1,&V&=u_2+s_2,\\
 P&=2^{-1/2}(u_1-s_1-u_2+s_2),&
 Q&=2^{-1/2}(u_1-s_1+u_2-s_2).
\end{aligned}
\tag{6}
\]

The reverser exchanges \(u\) and \(s\).  The certified source circle is the
radius-\(0.01\) circle on the true unstable graph

\[
 u_\rho(\phi)=0.01(\cos\phi,\sin\phi),\qquad
 s=h^u_{\rm true}(u_\rho(\phi)).
\tag{7}
\]

The graph remainder budgets relative to the frozen degree-ten polynomial
are \(10^{-20}\) in value and \(10^{-18}\) in first derivative on the whole
source disk.  These are enclosures of one invariant graph, not a perturbation
budget for arbitrary graphs.

## 3. Selected transverse symmetric homoclinic

Let \(S_0(\phi)\) denote (7) in the state variables (6), let \(\Phi_0\) be
the flow of (2), and put

\[
 \mathcal M_0(\phi,T)
 =(P,Q)\bigl(\Phi_0^T(S_0(\phi))\bigr).
\tag{8}
\]

The frozen interval proof gives a locally unique zero in its stated shooting
box with

\[
\begin{aligned}
 \phi_{\rm h}&\in
 [5.8615055856447817,5.8615055856450482],\\
 T_{\rm h}&\in
 [9.6374420678958099,9.6374420678971511],\\
 \det D_{(\phi,T)}\mathcal M_0
 &\in[149.56393055300413,149.56404227745782].
\end{aligned}
\tag{9}
\]

The endpoint is the first positive hit of
\(\operatorname{Fix}\mathcal R=\{P=Q=0\}\).  Reflection gives a
nonconstant symmetric homoclinic \(\Gamma_0\).  The tangent enclosures are

\[
\begin{aligned}
 \partial_\phi U(T_{\rm h})&\in
 [-10.889708535478462,-10.8897049543477],\\
 \partial_\phi V(T_{\rm h})&\in
 [35.417125972639965,35.417127394127888].
\end{aligned}
\tag{10}
\]

Consequently, at every non-equilibrium point \(z\in\Gamma_0\),

\[
 T_zW^u_0(0)+T_zW^s_0(0)=T_zH_0^{-1}(0),
 \qquad
 T_zW^u_0(0)\cap T_zW^s_0(0)
 =\operatorname{span}\{F_0(z)\}.
\tag{11}
\]

Equation (11) is transversality modulo the common flow direction inside the
regular three-dimensional energy surface.  It is not ambient transversality
of two surfaces in four dimensions.  Local uniqueness in (9) is only in the
frozen shooting box; no global uniqueness of core homoclinics is imported.

## 4. Frozen compact central event package

We freeze one compact source cell, its physical pre-event tubes, and a finite
collection of cooriented \(C^3\) event-face germs.  The package has all of the
following properties at the core:

1. The cell boundary is transverse to the oriented-blow-up phase fibers.  It
   contains the homoclinic projection and two designated gate-anchor
   projections in its interior.  The two signed residual-phase traces and
   the anchor traces lie in a proper open phase arc; its complementary arc
   has positive length.
2. The outgoing band is exhausted by the homoclinic aperture, two finite
   gate apertures, and named lateral strata.  At the end of the compact
   homoclinic tube, the return band is exhausted by re-entry strata, the
   stable cut, and named lateral strata.  Connected relative interiors,
   faces, and corners form a finite clean stratification, neat at the cell
   boundary.  A fixed priority labels simultaneous faces and corners.
3. Every assigned first hit is transverse.  Active conormals have a positive
   least singular value; empty incidences, inactive faces, earlier-event
   exclusion, strict event order, flow-domain containment, anchor-to-boundary
   distance, and the proper-arc cut all have positive margins on the relevant
   compact sets.
4. The homoclinic flight from the outgoing saddle face to the incoming saddle
   face has a common compact tube and a positive first-hit margin.
5. A fixed analytic physical saddle block has transverse incoming and
   outgoing faces.  Its punctured long-passage collar is disjoint from all
   event faces by a positive compact buffer.  The auxiliary radial faces may
   be joined to the physical faces by fixed compact event-free orbit-slide
   tubes with bounded times and mixed state derivatives through order three.

The certified source data used to place the three disjoint apertures are

\[
 \phi_{\rm a}\in
 [5.7566913947049203,5.7566913967948983],
 \qquad
 \phi_{\rm h}\text{ as in (9)},
\tag{12}
\]

and a closed pole-gate source cover

\[
 [-0.2,0.2]\pmod {2\pi}.
\tag{13}
\]

The algebraic-directed--homoclinic phase gap is greater than \(0.104814\);
the algebraic-directed--pole-directed and homoclinic--pole-directed gaps are
respectively greater than
\(0.32648\) and \(0.22167\) in the frozen lift.  For every phase in (13),
the base orbit has a strict first hit of the fixed gate \(x=-U=10\), with

\[
\begin{aligned}
 T_{10}&\in[10.885720013440157,11.579632102474379],\\
 y&>26.31,\qquad D>52.17,\qquad H_{\rm cone}>262.34,\\
 x'&>26.31,\qquad y'>102.17,\qquad H_{\rm cone}'>1704.01.
\end{aligned}
\tag{14}
\]

Here \(x,y,D,H_{\rm cone}\) are the pole-gate coordinates/functions of the
frozen source, not the physical PDE variable \(x\).  In V2, (12)--(14) name
only finite central gates and their source phases.  Calling them
positive-parameter pole or algebraic ends requires the separate V3 and V4
theorems.

Because the list of strict inequalities is finite after choosing the fixed
flow-box and corner atlases, divide each dimensional quantity by its fixed
reference scale and let

\[
 m_0>0
\tag{15}
\]

be the minimum of the resulting dimensionless rank, speed, separation,
containment, phase-cut, and event-order margins.  At a prescribed
simultaneous corner, (15) refers to active-conormal rank and the fixed
priority, not to a nonexistent positive time gap between simultaneous hits.
No numerical lower bound for the aggregate \(m_0\) is claimed.

## 5. Imported analytic tools and their hypotheses

The following general results from the same frozen manuscript may be used in
V2 because their hypotheses are restated here.

**Reversible saddle coordinates.**  For a compact \(C^r\) parameter family,
\(r\le2\), of exact Hamiltonians whose saddle-focus germs are uniformly real
analytic in the state, \(C^r\) in the parameter in analytic norms, reversible
for a fixed anti-symplectic involution, and have
\(\inf\min\{\alpha,\beta\}>0\), Proposition 2.7 gives parameter-local
reversible exact symplectic coordinates.  On zero energy the local passage
preserves the transverse action \(\nu\) exactly and its time and phase have
the form below in the frozen manuscript's local Darboux convention
\((\phi^{\rm F},\nu^{\rm F})\):

\[
 T_{\mu,\sigma}(\nu)=-\alpha_\mu^{-1}\log|\nu|
   +t_{\mu,\sigma}
   +O\bigl(|\nu|(1+|\log|\nu||)\bigr),
\tag{16}
\]

\[
 \Delta_{\mu,\sigma}(\nu)=
   (\beta_\mu/\alpha_\mu)\log|\nu|
   +b_{\mu,\sigma}
   +O\bigl(|\nu|(1+|\log|\nu||)\bigr).
\tag{17}
\]

For \(0\le\ell\le r\) and fixed \(j\), the remainder after
\(D_\mu^\ell D_{\log\nu}^j\), where
\(D_{\log\nu}=\nu\partial_\nu\), is bounded by the same weighted-log order.
The theorem does not assert ordinary \(C^2\) extension in \(\nu\) through
\(\nu=0\).  The Darboux angle in this frozen statement is not silently
identified with the positive Kato phase used by V2.  The latter is obtained
by the full symplectic conjugation
\(\mathcal T=\operatorname{diag}(C_0,C_0)\), which satisfies
\(I_2^{\rm F}(\mathcal Tz)=I_2^{\rm K}(z)\); hence it does not reverse the
action value or exchange its sign components.  V2 then freezes explicit
Kato-oriented incoming and outgoing radial sections and recomputes their
normal-form quadrature.  That calculation gives the opposite logarithmic
phase sign, while the time law and all absolute weighted-log bounds are
unchanged.  No phase-only dictionary is used to infer this sign.

**Compact first hits.**  Lemma 5.3 applies to a compact pre-event tube when
each \(z\) already has a first-event time
\(\tau(z)\in[\tau_-,\tau_+]\), the event function is \(C^3\), the hit speed
has a positive lower bound, all
inactive inequalities and earlier-hit exclusions have strict common margins,
and any simultaneous faces are specified in advance.  It gives a unique
\(C^3\) first-hit time on a neighborhood and retains the event labels and
margins.

**Finite clean arrangements.**  Proposition 5.2 applies to a finite family
of \(C^{s+1}\) defining functions, \(s\in\{1,2\}\), on a compact
manifold with corners when every nonempty incidence is neat, active
conormals together with boundary conormals are independent, and
reference-empty incidences have positive gaps.  A sufficiently small
state-\(C^s\) perturbation has the same incidences, sign strata, connected
components, and labels under a boundary-preserving controlled ambient
isotopy.  The frozen proposition is state-parametric only; the two external
parameter derivatives needed here are established separately in Section 5
of the continuation proof.

These are theorem-level analytic inputs.  Their application to the concrete
positive-parameter family, including its two external derivatives, is proved
in [CENTRAL_CONTINUATION.md](CENTRAL_CONTINUATION.md); it is not part of this
import.

## 6. Import boundary

The following parts of the flagship source are deliberately excluded:

- the full Definition 2.1(I4)--(I5) compactifications, their rates,
  basin-entry conclusions, and any positive-parameter continuation; only the
  finite base target germ and anchors explicitly frozen above are retained;
- the conclusion that a finite gate point actually enters either
  noncompact positive-parameter end;
- Corollary 8.7 and every relative-openness statement that presupposes both
  compactified ends;
- high-winding strips, recurrence, first-exit exhaustiveness beyond the
  fixed central tube, action finite parts, and coding; and
- any temporal claim for the PDE.

Thus this frozen package can discharge only the base-point and compact
analytic inputs of V2.
