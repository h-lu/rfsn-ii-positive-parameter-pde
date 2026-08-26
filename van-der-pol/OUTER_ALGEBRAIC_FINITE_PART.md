# Positive-parameter outer algebraic length and action finite parts

**Evidence status: Proved.**  This note carries
out the noncompact-end obligation following V5.  It uses the physical outer
channel constructed in V4 and attached to the central problem in V5; it does
not import the singular-core counterterms.  The normalization is a fixed
physical outer cut and a reference orbit on the same positive-parameter
future-staying sheet.  Actual and reference tails are compared at the same
value of the natural physical boundary coordinate \(z=1/u\).

The finite parts below are relative end potentials.  A normalization is
unavoidable: the stable outer coordinate has an exponentially flat freedom
which no finite boundary jet can select.  We choose a reference
normalization at one finite cut; this removes that freedom and makes all
later cut and coordinate changes covariant.  Other admissible
normalizations are related by the endpoint corrections proved below.

## 1. Parameter class, normalization, and theorem

Retain the final compact positive box of V5,

\[
 \mathcal P_{\rm p}
 =\left[\frac12r_{\rm p},r_{\rm p}\right]
   \times[-A,A]\times[\epsilon_-,\epsilon_+],
 \qquad \mu=(r,a_2,\epsilon),
\tag{1}
\]

and

\[
 \delta=r^2,\qquad
 a=1+\sqrt\epsilon\,r^3a_2,\qquad
 q_*(\epsilon)=\sqrt{\epsilon/2}.
\tag{2}
\]

In the V4 outer chart use

\[
 z=u^{-1},\qquad \pi=p,\qquad
 w=z\{f(u)-v\},\qquad \chi=z^2q,
 \qquad {d\over d\tau}=z{d\over dy},
\tag{3}
\]

and the exact normal coordinates

\[
 h=\pi-\delta\chi,\qquad
 \alpha={h+w\over2},\qquad
 \beta={h-w\over2}.
\tag{4}
\]

Write the V4 graph on the zero-energy face as

\[
 \alpha=\Gamma_\mu(z,0,\beta).
\tag{5}
\]

Choose a fixed \(z_*>0\), smaller than every V5 outer matching cut and
small enough for the strict V4 corridor estimates, and put

\[
 e=z^2,\qquad \mathfrak q=e^{-1}=z^{-2},\qquad
 \mathfrak q_*=z_*^{-2}.
\tag{6}
\]

Here \(e\) is only a convenient squared magnitude and \(\mathfrak q\) is
the fixed half-line variable.  The genuine smooth boundary defining
function in the V4 compactification is \(z\); no smoothness of the field in
\(e=z^2\) is assumed.

Every matched orbit reaches \(z=z_*\) uniquely because
\(\dot z=-\pi z^3<0\).  On that cut, the reference orbit is selected by

\[
 E=0,\qquad \beta=0,qquad
 \alpha=\Gamma_\mu(z_*,0,0).
\tag{7}
\]

The choice (7), not merely future boundedness, is part of the
normalization.

### Theorem V5A

After decreasing \(z_*>0\) and then a fixed interval
\(I_\beta=[-b_*,b_*]\) if necessary, the following hold uniformly for
\((b_0,\mu)\in I_\beta\times\mathcal P_{\rm p}\).

1. **Exact outer weights.**  Let \(b(\mathfrak q;b_0,\mu)\) be the orbit on
   (5) with \(b(\mathfrak q_*)=b_0\).  Physical spatial length and the
   action of the fixed primitive

   \[
    \lambda_\delta=\epsilon p\,du-\delta^{-1}q\,dv
   \tag{8}
   \]

   have the exact common-coordinate densities

   \[
   \begin{aligned}
    \mathcal T(\mathfrak q,b;\mu)
      &={\delta\over2\Pi(\mathfrak q,b;\mu)}
          \mathfrak q^{-1/2},\\
    \mathcal A(\mathfrak q,b;\mu)
      &=-{\Chi(\mathfrak q,b;\mu)^2
             \over2\Pi(\mathfrak q,b;\mu)}\mathfrak q^{3/2}
        +{\epsilon\Pi(\mathfrak q,b;\mu)\over2}
             \mathfrak q^{-1/2},
   \end{aligned}
   \tag{9}
   \]

   where \(\Chi\) is the positive energy root from V4 and

   \[
    \Pi=\delta\Chi+\Gamma_\mu(\mathfrak q^{-1/2},0,b)+b.
   \tag{10}
   \]

2. **Reference-subtracted limits.**  Let
   \(b_{\rm ref}(\mathfrak q;\mu)=b(\mathfrak q;0,\mu)\) and define, at
   every finite cutoff \(Q\ge\mathfrak q_*\),

   \[
   \begin{aligned}
    R_{\mathsf x}(Q;b_0,\mu)
      &=\int_{\mathfrak q_*}^{Q}
        \{\mathcal T(\mathfrak q,b;\mu)
           -\mathcal T(\mathfrak q,b_{\rm ref};\mu)\}
           \,d\mathfrak q,\\
    R_{\mathsf A}(Q;b_0,\mu)
      &=\int_{\mathfrak q_*}^{Q}
        \{\mathcal A(\mathfrak q,b;\mu)
           -\mathcal A(\mathfrak q,b_{\rm ref};\mu)\}
           \,d\mathfrak q.
   \end{aligned}
   \tag{11}
   \]

   The limits

   \[
    \mathscr L_{\rm fp}(b_0,\mu)
      =\lim_{Q\to\infty}R_{\mathsf x}(Q;b_0,\mu),\qquad
    \mathscr A_{\rm fp}(b_0,\mu)
      =\lim_{Q\to\infty}R_{\mathsf A}(Q;b_0,\mu)
   \tag{12}
   \]

   exist.  They have every mixed derivative
   \(D_{b_0}^iD_\mu^j\) with \(i+j\le2\), \(j\le2\), and these derivatives
   are obtained by differentiating (11) under the improper integral.
   In fact the proof supplies one spare total derivative.

3. **True end subtraction.**  If

   \[
   \begin{aligned}
    C_{\mathsf x,\mu}(Q)
       &=\int_{\mathfrak q_*}^{Q}
          \mathcal T(\mathfrak q,b_{\rm ref};\mu)
          \,d\mathfrak q,\\
    C_{\mathsf A,\mu}(Q)
       &=\int_{\mathfrak q_*}^{Q}
          \mathcal A(\mathfrak q,b_{\rm ref};\mu)
          \,d\mathfrak q,
   \end{aligned}
   \tag{13}
   \]

   then both counterterms diverge and

   \[
   \begin{aligned}
    C_{\mathsf x,\mu}(Q)
      &=q_*(\epsilon)^{-1}Q^{1/2}+O_{C^2_\mu}(\log Q),\\
    C_{\mathsf A,\mu}(Q)
      &=-{q_*(\epsilon)\over5\delta}Q^{5/2}
          +O_{C^2_\mu}(Q^2).
   \end{aligned}
   \tag{14}
   \]

   Additive constants depending on \(\mathfrak q_*\) are absorbed in the
   remainders.  Thus (12) is not a finite-cut action renamed as a finite
   part: it is the limit after subtracting the complete, field-dependent
   noncompact reference tail.

4. **Covariance and strict composition.**  Moving any finite matching cut
   transfers exactly the physical segment between the two terminal
   potentials.  Changing the reference cut, an admissible compactifying
   coordinate, or the primitive by an exact differential changes the
   normalized potentials only by the endpoint corrections in
   (44) and (47) below.  At every finite cutoff the central branch and outer
   tail compose by ordinary length and line-integral additivity; subtracting
   (13) only from the terminal segment and then taking \(Q\to\infty\)
   preserves the equality exactly.

Items 1--4 are the outer algebraic length/action finite-part theorem needed
before the exhaustive V6 assembly.  They do not prove that all high-winding
source points have a labelled first event.

## 2. Exact reduced equation and physical densities

On (5) abbreviate

\[
 \begin{aligned}
  \Gamma&=\Gamma_\mu(z,0,b),&
  \Chi&=\Chi(z,0,b,\Gamma;\mu),\\
  \Pi&=\delta\Chi+\Gamma+b,&
  W&=\Gamma-b.
 \end{aligned}
\tag{15}
\]

Equations V4(14) and V4(17) give

\[
 {d\mathfrak q\over d\tau}=2\Pi
\tag{16}
\]

and

\[
 {db\over d\mathfrak q}=G(\mathfrak q,b;\mu),
\tag{17}
\]

where, with \(z=\mathfrak q^{-1/2}\),

\[
 G(\mathfrak q,b;\mu)
 ={1\over2\Pi}\left[
 -b+{z^2\over2}
 \{-\delta^2\epsilon(1-az)+2\delta\Chi\Pi
       +\Pi+\Pi W\}\right].
\tag{18}
\]

This equation is exact.  The V4 corridor gives
\(0<\pi_*\le\Pi\le\pi^*\), so \(\mathfrak q\) is a valid physical
coordinate on every tail under consideration.

Since \(y=\mathsf x/\delta\), V4(13) and (16) imply

\[
 {d\mathsf x\over d\mathfrak q}
 ={d\mathsf x/d\tau\over d\mathfrak q/d\tau}
 ={\delta z\over2\Pi}
 ={\delta\over2\Pi}\mathfrak q^{-1/2}.
\tag{19}
\]

This proves the first line of (9).  For the action, the physical equations
give

\[
 u_{\mathsf x}=\delta^{-1}p,\qquad v_{\mathsf x}=q,
\tag{20}
\]

and hence the exact density

\[
 \lambda_\delta(\partial_{\mathsf x})
 ={\epsilon\pi^2-q^2\over\delta}
 ={\epsilon\Pi^2-\Chi^2\mathfrak q^2\over\delta}.
\tag{21}
\]

Multiplication by (19) yields the second line of (9).  Equivalently, (21)
is obtained by evaluating the outer pullback V4(40) on the exact reduced
field.  Thus no term arising from \(dw\), no clock factor, and no sign has
been discarded.

At the boundary,

\[
 \Gamma_\mu(0,0,b)=0,qquad
 \Chi(0,0,b,0;\mu)=q_*(\epsilon).
\tag{22}
\]

Consequently

\[
 \ell_\infty(\mu)
 :=\partial_bG(\infty,0;\mu)
 =-{1\over2\delta q_*(\epsilon)}\le-c_0<0
\tag{23}
\]

on (1).  Smoothness of the positive energy root and the mixed regularity
of \(\Gamma\) give, with the corresponding mixed derivatives through total
order three and at most two parameter derivatives,

\[
 \begin{aligned}
  G(\mathfrak q,b;\mu)-\ell_\infty(\mu)b
   ={}&O(\mathfrak q^{-1})
      +O(\mathfrak q^{-1/2}|b|+b^2),\\
  \partial_bG(\mathfrak q,b;\mu)-\ell_\infty(\mu)
   ={}&O(\mathfrak q^{-1/2}+|b|).
 \end{aligned}
\tag{24}
\]

The first forcing is \(O(\mathfrak q^{-1})\), rather than merely
\(O(\mathfrak q^{-1/2})\), because every term in (18) which survives at
\(b=0\) carries the explicit factor \(z^2\).

## 3. The fixed-cut reference and exponentially flat shadowing

The following lemma is the analytic core of the construction.

**Lemma 1 (same-\(z\) outer phase).**  After increasing
\(\mathfrak q_*\) and decreasing \(b_*\), there are
\(c_1>0\), \(0<\eta<\min\{c_0,c_1\}\), and \(C<\infty\) such that

\[
 \sup_{\mathfrak q\ge\mathfrak q_*}
 \mathfrak q\,|D_\mu^j b_{\rm ref}(\mathfrak q;\mu)|\le C,
 \qquad 0\le j\le2,
\tag{25}
\]

and, for \(d=b-b_{\rm ref}\),

\[
 \max_{\substack{i+j\le3\\j\le2}}
 \sup_{\mathfrak q\ge\mathfrak q_*}
 e^{\eta(\mathfrak q-\mathfrak q_*)}
 |D_{b_0}^iD_\mu^j d(\mathfrak q;b_0,\mu)|\le C.
\tag{26}
\]

In particular, at the same physical compactifying coordinate,

\[
 |D_{b_0}^iD_\mu^j
   \{b(z;b_0,\mu)-b_{\rm ref}(z;\mu)\}|
 \le C_{i,j,m}z^m
\tag{27}
\]

for every fixed \(m\ge1\), \(i+j\le3\), \(j\le2\).

*Proof.*  Equation (24) first permits \(\mathfrak q_*\) and \(b_*\) to be
chosen so that \(G_b\le-c_1<0\) on the whole reference-and-tail tube.  Fix
\(0<\eta<\min\{c_0,c_1\}\), and use the spaces

\[
 \begin{aligned}
  \mathcal Y_1
   &=\{r\in C[\mathfrak q_*,\infty):r(\mathfrak q_*)=0,
       \ \|r\|_1=\sup \mathfrak q|r(\mathfrak q)|<\infty\},\\
  \mathcal X_\eta
   &=\{d\in C[\mathfrak q_*,\infty):
       \ \|d\|_\eta=\sup
       e^{\eta(\mathfrak q-\mathfrak q_*)}|d(\mathfrak q)|<\infty\}.
 \end{aligned}
\tag{28}
\]

The reference is the fixed point in \(\mathcal Y_1\) of

\[
 (\mathcal R_\mu r)(\mathfrak q)
 =\int_{\mathfrak q_*}^{\mathfrak q}
 e^{\ell_\infty(\mu)(\mathfrak q-s)}
 \{G(s,r(s);\mu)-\ell_\infty(\mu)r(s)\}\,ds.
\tag{29}
\]

The elementary exponential-convolution bounds following from (24) give,
on a fixed ball of \(\mathcal Y_1\),

\[
 \|\mathcal R_\mu r\|_1
 \le C_1+C\mathfrak q_*^{-1/2}
       (\|r\|_1+\|r\|_1^2),
 \qquad
 \|D_r\mathcal R_\mu\|
 \le C\mathfrak q_*^{-1/2}(1+\|r\|_1).
\tag{30}
\]

Increasing \(\mathfrak q_*\) makes the second quantity smaller than one.
The parameter-dependent contraction theorem, applied to the same fixed
space, proves (25).  Derivatives of the kernel contain only
\((\mathfrak q-s)^k e^{-c_0(\mathfrak q-s)}\), \(k\le2\), so the same
convolution estimate controls both parameter derivatives.

For \(d=b-b_{\rm ref}\), use the fixed point equation

\[
 \begin{aligned}
 (\mathcal D_{b_0,\mu}d)(\mathfrak q)
 ={}&e^{\ell_\infty(\mu)(\mathfrak q-\mathfrak q_*)}b_0\\
 &+\int_{\mathfrak q_*}^{\mathfrak q}
 e^{\ell_\infty(\mu)(\mathfrak q-s)}
 \{G(s,b_{\rm ref}+d;\mu)-G(s,b_{\rm ref};\mu)
       -\ell_\infty(\mu)d\}\,ds.
 \end{aligned}
\tag{31}
\]

Equations (24)--(25) imply, on a sufficiently small ball of
\(\mathcal X_\eta\),

\[
 \|D_d\mathcal D_{b_0,\mu}\|
 \le {C\over c_0-\eta}
       (\mathfrak q_*^{-1/2}+\|d\|_\eta)<1.
\tag{32}
\]

This constructs every actual tail on the same half-line.  Differentiating
the ODE for \(d\), the first variations solve equations of the form

\[
 h'-G_b(\mathfrak q,b;\mu)h=k,
\tag{33}
\]

where either the initial value is \(1\) and \(k=0\), or the initial value
is zero and \(k\in\mathcal X_\eta\).  After the preceding shrinkage,
\(G_b\le-c_1<0\), and the zero-initial-value inverse has norm at most
\((c_1-\eta)^{-1}\) on \(\mathcal X_\eta\).  At every higher mixed
derivative through total order three, the Faà di Bruno forcing is a finite
sum of lower variations and coefficient differences.  Every term created
by a parameter derivative of
\(G(b_{\rm ref}+d)-G(b_{\rm ref})\) contains \(d\) or one of its already
controlled variations.  Induction in the total derivative order therefore
keeps the forcing in \(\mathcal X_\eta\) and proves (26).

Finally,
\(e^{-\eta/z^2}\le C_mz^m\) for every \(m\), which proves (27).  The fixed
half-line equations restrict identically to every finite cutoff; hence no
limit solution has been substituted into a finite-flight identity.  ∎

The flat estimate also explains why a boundary Taylor expansion cannot
choose the reference.  Two solutions with different \(b_0\) have identical
jets at \(z=0\) to every algebraic order, but remain different physical
orbits at every finite cut.

## 4. Convergence and mixed two-jets

The functions \(\Pi\) and \(\Chi\) in (9) are smooth on the fixed corridor,
\(\Pi\ge\pi_*>0\), and their mixed derivatives have the same total-three
bounds as \(\Gamma\).  The mean-value formula and Lemma 1 therefore give

\[
 \begin{aligned}
 &|D_{b_0}^iD_\mu^j
   \{\mathcal T(\mathfrak q,b;\mu)
      -\mathcal T(\mathfrak q,b_{\rm ref};\mu)\}|
 \le C\mathfrak q^{-1/2}
       e^{-\eta(\mathfrak q-\mathfrak q_*)},\\
 &|D_{b_0}^iD_\mu^j
   \{\mathcal A(\mathfrak q,b;\mu)
      -\mathcal A(\mathfrak q,b_{\rm ref};\mu)\}|
 \le C(1+\mathfrak q)^{3/2}
       e^{-\eta(\mathfrak q-\mathfrak q_*)},
 \end{aligned}
\tag{34}
\]

for \(i+j\le3\), \(j\le2\).  Both right sides are integrable and are
independent of \((b_0,\mu)\).  The Cauchy criterion and dominated
convergence prove (12), justify all derivatives claimed in Theorem V5A(2),
and give the explicit tail bounds

\[
 \begin{aligned}
 |D_{b_0}^iD_\mu^j
   \{\mathscr L_{\rm fp}-R_{\mathsf x}(Q)\}|
   &\le C(1+Q)^{-1/2}e^{-\eta(Q-\mathfrak q_*)},\\
 |D_{b_0}^iD_\mu^j
   \{\mathscr A_{\rm fp}-R_{\mathsf A}(Q)\}|
   &\le C(1+Q)^{3/2}e^{-\eta(Q-\mathfrak q_*)}.
 \end{aligned}
\tag{35}
\]

The first polynomial factor in (35) may harmlessly be replaced by one; its
displayed form records the exact density weight.  Composition with any
mixed-\(C^2\) arrival label \(b_0=b_0(\zeta,\mu)\) is therefore mixed
\(C^2\).  The spare derivative in (34) controls the mean-value remainder
when a family of finite first-hit labels converges in \(C^2\).

For the reference orbit, V4(37)--(38) and (25) give

\[
 \Pi_{\rm ref}=\delta q_*(\epsilon)+O_{C^2_\mu}(Q^{-1/2}),
 \qquad
 \Chi_{\rm ref}=q_*(\epsilon)+O_{C^2_\mu}(Q^{-1/2}).
\tag{36}
\]

Substitution into (9) gives

\[
 \mathcal T_{\rm ref}
 ={1\over2q_*}Q^{-1/2}+O_{C^2_\mu}(Q^{-1}),
 \qquad
 \mathcal A_{\rm ref}
 =-{q_*\over2\delta}Q^{3/2}+O_{C^2_\mu}(Q),
\tag{37}
\]

and integration proves (14).  The reference integrals (13), rather than a
truncated list of powers, are the counterterms.  Hence every lower power or
logarithm forced by the full positive-parameter field is included
automatically.

## 5. Moving cuts and exact branch composition

Let \(C\) be any compact \(C^2\) transverse cut on the matched
future-staying family whose forward orbits reach this channel, either
before \(z=z_*\) or later inside the outer corridor.  Follow an orbit to the point
\(Z_Q\) with \(z=Q^{-1/2}\).  With the single frozen reference counterterm
(13), define

\[
 \begin{aligned}
  \mathscr L_{{\rm fp},C}
   &=\lim_{Q\to\infty}
      \left\{\int_C^{Z_Q}d\mathsf x-C_{\mathsf x,\mu}(Q)\right\},\\
  \mathscr A_{{\rm fp},C}
   &=\lim_{Q\to\infty}
      \left\{\int_C^{Z_Q}\lambda_\delta
                   -C_{\mathsf A,\mu}(Q)\right\}.
 \end{aligned}
\tag{38}
\]

The finite part from \(C\) to \(z=z_*\), if that segment is traversed in
the opposite direction, is interpreted with its oriented sign.  If \(C_1\)
is later than \(C_0\) on the same branch, finite-cut additivity gives for
every \(Q\)

\[
 \int_{C_0}^{Z_Q}\lambda_\delta
 =\int_{C_0}^{C_1}\lambda_\delta
  +\int_{C_1}^{Z_Q}\lambda_\delta,
\tag{39}
\]

and the identical identity for \(d\mathsf x\).  Subtracting the same
reference term and taking the limit proves the exact moving-cut laws

\[
 \boxed{
 \begin{aligned}
  \mathscr L_{{\rm fp},C_0}
   &=\int_{C_0}^{C_1}d\mathsf x
      +\mathscr L_{{\rm fp},C_1},\\
  \mathscr A_{{\rm fp},C_0}
   &=\int_{C_0}^{C_1}\lambda_\delta
      +\mathscr A_{{\rm fp},C_1}.
 \end{aligned}}
\tag{40}
\]

In particular, (40) applies to the parameter-dependent V5 outer cut and
the fixed cut \(z=z_*\); the intervening flight is compact and mixed
\(C^2\).

More generally, let \(P_1:C_0\to C_1\) and \(P_2:C_1\to C_2\) be finite
physical first-hit maps on the shifted zero-energy surface, and let

\[
 B_{P_j}(Z)=\int_Z^{P_j(Z)}\lambda_\delta.
\tag{41}
\]

Before renormalization,

\[
 B_{P_2\circ P_1}=B_{P_1}+B_{P_2}\circ P_1.
\tag{42}
\]

If \(P_2\) is followed by the algebraic end, replace only its final outer
integral by (38).  Equation (42) holds at each finite \(Q\); the one
counterterm (13) occurs once on both sides.  Passing to the limit proves
strict additivity of the finite central branches and the algebraic finite
part.  On an energy-thick flowbox the ambient first-variation identity
retains the term \(\tau\,dH_{\rm ph}\) from V5(65); restriction to the
zero-energy sections gives the usual exact branch primitive.  No
energy-thick term is silently dropped in obtaining (42).

## 6. Admissible coordinate, reference, section, and gauge changes

We record the precise sense in which the finite part is intrinsic.  Two
outer presentations are called admissibly equivalent on this channel when:

1. they describe the same physical flow, the same zero-energy
   future-staying sheet, and the same end coorientation;
2. their natural boundary defining functions are related by a mixed-\(C^3\)
   \(b\)-diffeomorphism

   \[
    \widetilde z=U_\mu(z,E,\beta)z,
    \qquad 0<U_*\le U_\mu\le U^*;
   \tag{43}
   \]

3. their finite source or matching sections are related by event-free
   physical-flow slides
   \(S(Z)=\Phi_{\mathsf x}^{\sigma(Z)}Z\) with mixed derivatives through
   total order three;
4. their reference cuts, stable-coordinate charts, and selected reference
   points form compact mixed-\(C^3\) parameter families.  After
   physical-flow transport to one common cut, the selected stable labels
   remain in a fixed interior interval and have uniformly bounded mixed
   derivatives through total order three; and
5. their primitives satisfy
   \(\lambda_1=\lambda_0+d\psi\), where \(\psi\) has a genuine mixed-
   \(C^2\) limit on the compactified end face and mixed derivatives through
   total order three on the tube.

The spare derivative is used only for composition with moving labels; the
output remains mixed \(C^2\).

Put \(C^j_{\mathsf x},C^j_{\mathsf A}\) for the two reference
counterterms in presentation \(j\), now regarded as functions of that
presentation's boundary-coordinate value.  In the original presentation
this is merely the reparametrization \(Q=z^{-2}\) of (13).  Align cutoffs
at the same physical point \(Z\) of any actual tail and denote the two
boundary-coordinate values there by \(z_j(Z)\).  Then

\[
 \begin{aligned}
  \Gamma_{\mathsf x}(\mu)
   &=\lim_{Z\to\partial_{\rm a}}
       \{C^0_{\mathsf x}(z_0(Z))-C^1_{\mathsf x}(z_1(Z))\},\\
  \Gamma_{\mathsf A}(\mu)
   &=\lim_{Z\to\partial_{\rm a}}
       \{C^0_{\mathsf A}(z_0(Z))-C^1_{\mathsf A}(z_1(Z))
          +\psi(Z)\}
 \end{aligned}
\tag{44}
\]

The limits in (44) exist with mixed two parameter derivatives.  They do
not depend on the chosen actual tail.  If the reference orbit, cut,
coordinate, and primitive are unchanged, both constants vanish.

Here \(C^j_\bullet(z_j(Z))\) means that the reference orbit in presentation
\(j\) is stopped where its own boundary coordinate equals the scalar
\(z_j(Z)\) read from the actual point.  The counterterm is never evaluated
on the actual orbit.

To prove this, first put the two reference orbits in either one of the
physical \(z\)-coordinates after a finite common cut.  Lemma 1, now with
one reference used as the initial datum for the other, shows that their
stable coordinates and all required derivatives differ by
\(O(e^{-\eta\mathfrak q})\).  Equations (9) and (34) make the differences
of their physical length and action densities absolutely integrable.
The finite portions before the common cut contribute smooth constants.

For the cutoff coordinates, (43) and the implicit-function theorem show
that imposing the same \(\widetilde z\) on two flat-shadowing orbits changes
their physical \(\mathfrak q\)-values by at most a polynomial in
\(\mathfrak q\) times \(e^{-\eta\mathfrak q}\).  Multiplication by either
weight in (9) still tends to zero.  Thus (43) is used only to reparametrize
the same finite physical integrals; cancellation of two unrelated formal
singular series is never assumed.  Finally,

\[
 \int d\psi=\psi(\hbox{terminal point})-
             \psi(\hbox{initial point}),
\tag{45}
\]

and the terminal values on the actual and reference orbits agree because
both converge to \((z,E,\beta,\alpha)=(0,0,0,0)\).  This proves (44).

For the orbit slide in item 3 define

\[
 K(Z)=\int_0^{\sigma(Z)}
       \lambda_0(X_{\mathsf x})(\Phi^{t}_{\mathsf x}Z)\,dt,
 \qquad C(Z)=K(Z)+\psi(S(Z)).
\tag{46}
\]

The two normalized terminal potentials then satisfy

\[
 \boxed{
 \begin{aligned}
  \mathscr L_{\rm fp}^{\,1}\circ S
    &=\mathscr L_{\rm fp}^{\,0}-\sigma+\Gamma_{\mathsf x},\\
  \mathscr A_{\rm fp}^{\,1}\circ S
    &=\mathscr A_{\rm fp}^{\,0}-C+\Gamma_{\mathsf A}.
 \end{aligned}}
\tag{47}
\]

These are endpoint coboundaries.  When a finite central branch is attached,
the \(+\sigma\) or \(+C\) contributed by moving its terminal section cancels
the corresponding negative term in (47).  For a closed spatial orbit the
endpoint action terms telescope.  The statement concerns exact changes of
primitive; no invariance is claimed under addition of a non-exact closed
one-form.

## 7. Compatibility with V5 and evidence boundary

V5 supplies a mixed-\(C^2\) arrival map from the fixed central matching
section through \(K_2\), \(K_1\), and the outer overlap.  Flowing that map
to \(z=z_*\) is a compact first-hit operation with a uniform hit-speed
margin, so its stable label \(b_0\) is mixed \(C^2\).  Composing it with
(12) and using (40) gives a mixed-\(C^2\) central-plus-algebraic spatial
length and action potential independent of every subordinate matching cut.
This closes issue #5's noncompact-end obligation.

The theorem does not prove:

- exhaustiveness or connectedness of all high-winding first-event strata;
- separation of the pulled-back algebraic and pole event windows;
- the complete return/first-exit branch census;
- symbolic coding of bounded itineraries; or
- temporal stability of any stationary PDE pattern.

Those are the V6--V7 and S1 obligations in the claim register.
