# Positive-parameter outer future-staying hypersurface

**Evidence status: Proved.**  This note proves claim V4.  It constructs the
outer algebraic compactification directly from the positive-parameter
stationary equations; it does not persist the singular-core algebraic end.
The resulting future-staying set is a parameter-dependent codimension-one
hypersurface, normally expanding in forward desingularized time and bunched
through order three in intrinsic quotient norms.

The central--intermediate--outer attachment is not part of V4.  In
particular, this note does not assert that the finite algebraic-directed gate
from V2 lies on the hypersurface constructed here.  That is the separate V5
matching problem.

## 1. Parameter box and theorem

Retain without alteration the positive compact box fixed in V3,

\[
 \mathcal P_{\rm p}
 =\left[\frac12r_{\rm p},r_{\rm p}\right]
   \times[-A,A]\times[\epsilon_-,\epsilon_+],
 \qquad \mu=(r,a_2,\epsilon),
\tag{1}
\]

and put

\[
 \delta=r^2,\qquad
 a=1+\sqrt\epsilon\,r^3a_2,\qquad
 q_*(\epsilon)=\sqrt{\epsilon/2}.
\tag{2}
\]

All constants below are uniform on (1).  In particular,

\[
 \delta_-=(r_{\rm p}/2)^2>0,
 \qquad q_- =\sqrt{\epsilon_-/2}>0.
\tag{3}
\]

### Theorem V4

There are positive constants
\(z_0,E_0,b_0,\alpha_0\), independent of \(\mu\in\mathcal P_{\rm p}\),
and an outer compactification \(\overline{\mathcal O}_\mu\) with the
following properties.

1. On the fixed corridor

   \[
   \mathcal Q=
   [0,z_0]\times[-E_0,E_0]\times[-b_0,b_0]
       \times[-\alpha_0,\alpha_0],
   \tag{4}
   \]

   the positive-parameter spatial field extends smoothly to \(z=0\).
   The first three coordinates \((z,E,\beta)\) are base coordinates and
   \(\alpha\) is an oriented normal coordinate.

2. The maximal forward-staying set in (4) is the graph of a unique function

   \[
    \mathcal W^{\rm tail}_{\mathrm{out},\mu}
      =\{\alpha=\Gamma_\mu(z,E,\beta)\}.
   \tag{5}
   \]

   It is a compact, locally maximal, codimension-one \(C^3\)
   manifold with corners.  The faces \(z=0\) and \(E=\pm E_0\) are
   structurally invariant, and every other base face is strictly inward.

3. Let \(\pi_B:(z,E,\beta,\alpha)\mapsto(z,E,\beta)\) be the fixed base
   projection.  On a graph plane \(P\), use the adapted tangent norm

   \[
    \|v\|_P=\|d\pi_Bv\|,
   \]

   and identify the normal quotient with the vertical line through the map
   induced by \(q_P|_{\ker d\pi_B}\), where \(q_P:T\mathcal Q\to
   T\mathcal Q/P\) is the quotient map.  Let \(\Phi_\mu^T\) be one fixed
   sufficiently small positive-time map, defined on the ambient corridor
   collar constructed below.  Write

   \[
   A^T_{\mu,Z}=D\Phi_\mu^T|_{T_Z\mathcal W^{\rm tail}_{\mathrm{out},\mu}},
   \qquad
   N^T_{\mu,Z}:T_Z\overline{\mathcal O}_\mu/
       T_Z\mathcal W^{\rm tail}_{\mathrm{out},\mu}
       \longrightarrow
       T_{\Phi_\mu^T Z}\overline{\mathcal O}_\mu/
       T_{\Phi_\mu^T Z}\mathcal W^{\rm tail}_{\mathrm{out},\mu}.
   \tag{6}
   \]

   With the quotient norm induced by the fixed base--normal splitting,

   \[
    \sup_{\mu,Z}
       \|(N^T_{\mu,Z})^{-1}\|\,\|A^T_{\mu,Z}\|^j<1,
       \qquad j=0,1,2,3.
   \tag{7}
   \]

   Thus (5) is normally expanding in forward time and third-order bunched.
   Formula (7) is intrinsic: the displayed identifications merely put
   adapted metrics on the actual tangent and quotient cocycles.  Changing
   the graph trivialization changes those adapted metrics by a uniformly
   equivalent family, not the cocycles themselves.

4. The graph has the mixed regularity

   \[
   \sup_{\substack{i+j\le3\\j\le2}}
    \|D_{(z,E,\beta)}^iD_\mu^j\Gamma_\mu\|<\infty.
   \tag{8}
   \]

   Equivalently,

   \[
    \Gamma\in C^0_\mu C^3_{z,E,\beta}
       \cap C^1_\mu C^2_{z,E,\beta}
       \cap C^2_\mu C^1_{z,E,\beta}.
   \tag{9}
   \]

5. Every orbit of (5) with \(z>0\) stays in the positive outer channel,
   satisfies \(u=1/z\to+\infty\), and reaches \(z=0\) only at infinite
   physical spatial distance.  Along each such orbit,

   \[
   \begin{aligned}
    u_x&=q_*(\epsilon)+O(u^{-1}),\\
    q&=q_*(\epsilon)u^2+O(u),\\
    v&=f(u)+O(u^{-1}),\\
    p&=\delta q_*(\epsilon)+O(u^{-1}).
   \end{aligned}
   \tag{10}
   \]

   as \(u\to\infty\).  The constants are uniform for families of orbit
   germs whose initial points range over a compact subset of one fixed
   positive cut \(\mathcal W^{\rm tail}_{\mathrm{out},\mu}\cap
   \{z=z_c\}\), \(0<z_c\le z_0\), and whose parameters range over (1).

The graph in (5), rather than the full energy surface or a formal slow
series, is what is meant below by the positive-parameter outer algebraic
channel.

## 2. Exact outer compactification

Use the fast spatial system

\[
 u_y=p,\qquad p_y=f(u)-v,\qquad
 v_y=\delta q,\qquad q_y=\epsilon\delta(u-a),
 \qquad f(u)=\frac13u^3-u.
\tag{11}
\]

On the positive outer half-space \(u>0\), set

\[
 z=u^{-1},\qquad \pi=p,\qquad
 w=z\{f(u)-v\},\qquad \chi=z^2q,
 \qquad \frac d{d\tau}=z\frac d{dy}.
\tag{12}
\]

The last identity is a clock definition.  Since \(y=x/\delta\),

\[
 \frac{dx}{d\tau}=\delta z.
\tag{13}
\]

Direct substitution in (11) gives the exact field

\[
\begin{aligned}
 \dot z&=-\pi z^3,\\
 \dot\pi&=w,\\
 \dot w&=(1-z^2)\pi-\delta\chi-\pi wz^2,\\
 \dot\chi&=z^2\{\epsilon\delta(1-az)-2\pi\chi\},
\end{aligned}
\tag{14}
\]

where a dot denotes \(d/d\tau\).  No term in (14) is asymptotic or
truncated.

The fast normal pair is diagonalized exactly by

\[
 h=\pi-\delta\chi,\qquad
 \alpha=\frac{h+w}{2},\qquad
 \beta=\frac{h-w}{2}.
\tag{15}
\]

Thus

\[
 \pi=\delta\chi+\alpha+\beta,
 \qquad w=\alpha-\beta,
\tag{16}
\]

and (14) implies

\[
\begin{aligned}
 \dot\beta={}&-\beta+\frac{z^2}{2}
 \{-\delta^2\epsilon(1-az)+2\delta\chi\pi
       +\pi+\pi w\},\\
 \dot\alpha={}&\alpha+\frac{z^2}{2}
 \{-\delta^2\epsilon(1-az)+2\delta\chi\pi
       -\pi-\pi w\}.
\end{aligned}
\tag{17}
\]

In particular, \(\beta\) is the future-stable fast coordinate and
\(\alpha\) is the future-unstable fast coordinate.

## 3. Energy as a regular boundary coordinate

Let \(\mathcal G\) be the physical first integral from V1 and let
\(O=(a,0,f(a),0)\).  The shifted energy

\[
 E=-\mathcal G+\mathcal G(O)
   =-\mathcal G-\epsilon F(a),
 \qquad F(u)=\frac1{12}u^4-\frac12u^2,
\tag{18}
\]

vanishes on the homogeneous-equilibrium energy level.  Substituting
(12), (15), and (16) into (18), and solving only algebraically for
\(\chi^2\), gives

\[
\begin{aligned}
 \chi^2={}&\frac\epsilon2-\frac{2a\epsilon}{3}z
 -\epsilon(2w+1)z^2+2a\epsilon(w+1)z^3\\
 &\quad+\{\epsilon\pi^2+2E+2\epsilon F(a)\}z^4.
\end{aligned}
\tag{19}
\]

Although \(\pi\) in (19) contains \(\chi\), the equation is regular at
the boundary.  At \(z=0\) its positive root is

\[
 \chi=q_*(\epsilon)=\sqrt{\epsilon/2},
\tag{20}
\]

and the derivative of the left side minus the right side with respect to
\(\chi\) is \(2q_*(\epsilon)\).  By (3), the parameter-dependent implicit
function theorem therefore gives, on one fixed neighborhood,

\[
 \chi=\Chi(z,E,\beta,\alpha;\mu)>0,
\tag{21}
\]

smooth jointly in all its arguments.  For \(z>0\), (21) is merely the
positive-\(q\) branch of the exact change of variables; at \(z=0\) it
defines the compactification.  Since \(E\) is a first integral,
\(\dot E=0\).

Equations (14), (17), and (21) now define a smooth vector field in
\((z,E,\beta,\alpha)\).  Its boundary restriction is exactly

\[
 (\dot z,\dot E,\dot\beta,\dot\alpha)
   =(0,0,-\beta,\alpha).
\tag{22}
\]

This is the decisive distinction from a compactification of the singular
core: the positive cubic balance is already contained in (19), and no
coefficient singular in \(r\) appears at \(z=0\).

## 4. A uniform isolating corridor

We choose the constants in (4) in an order that makes every margin strict.
First take \(E_0,b_0,\alpha_0>0\) so small that (21) is defined on a
slightly enlarged product neighborhood and

\[
 b_0+\alpha_0<\frac14\delta_-q_-.
\tag{23}
\]

Then decrease \(z_0\).  Uniform continuity of (21), together with
(16), yields constants \(0<\pi_*<\pi^*<\infty\) such that

\[
 \pi_*\le\pi=\delta\Chi+\alpha+\beta\le\pi^*
 \quad\hbox{on the enlarged corridor.}
\tag{24}
\]

Consequently \(\dot z<0\) on \(z=z_0\), while \(z=0\) is invariant.
The two energy faces are structurally invariant because \(\dot E=0\).
By (17), after one further decrease of \(z_0\),

\[
 \dot\beta<0\ \hbox{on }\beta=b_0,
 \qquad
 \dot\beta>0\ \hbox{on }\beta=-b_0,
\tag{25}
\]

so both stable faces are inward.  Likewise,

\[
 \dot\alpha>0\ \hbox{on }\alpha=\alpha_0,
 \qquad
 \dot\alpha<0\ \hbox{on }\alpha=-\alpha_0,
\tag{26}
\]

so the normal faces are strict exits.  These statements continue to hold
on a fixed ambient collar of (4).  Smoothness and compactness give a fixed
\(T>0\) for which the time-\(t\) maps on that collar are defined whenever
\(|t|\le T\); decrease \(T\), but not the corridor, if necessary.

Use \(X=(z,E,\beta)\) as the base and \(\alpha\) as the normal fiber, and
write the derivative of the field in block form

\[
 DY_\mu=\begin{pmatrix}C_\mu&B_\mu\\D_\mu&a_\mu\end{pmatrix}.
\tag{27}
\]

At \(z=0\), equation (22) gives

\[
 C_\mu=\operatorname{diag}(0,0,-1),\qquad
 B_\mu=D_\mu=0,\qquad a_\mu=1.
\tag{28}
\]

Fix \(0<\nu<1/16\).  Smoothness, compactness of (1), and (28) permit a
final decrease of \(z_0\) such that, in the product Euclidean metric,

\[
 \mu_2(C_\mu)\le\nu,\qquad
 \|B_\mu\|\le\nu,\qquad
 \|D_\mu\|\le\nu,\qquad
 a_\mu\ge1-\nu.
\tag{29}
\]

Here \(\mu_2\) is the logarithmic norm of the symmetric part.  Notice that
the estimates are taken in one fixed product chart; unrelated extrema from
different charts are not combined.

For graph slope at most one, the vertical-cone, normal-growth, and jet-gap
margins following from (29) are

\[
 q_{\rm cone}\ge1-4\nu>0,
 \qquad \lambda_{\rm n}\ge1-2\nu>0,
\tag{30}
\]

and

\[
 \gamma_j\ge1-(2j+2)\nu\ge\frac12,
 \qquad j=0,1,2,3.
\tag{31}
\]

Thus all corridor faces and all rate conditions have positive margins
uniformly in \(\mu\).

## 5. Corridor graph lemma and its application

For completeness, the finite-dimensional graph result used here is recorded
in the precise relative-boundary form needed by (4).

**Corridor graph lemma.**  Let a compact \(C^5\) base with corners carry an
oriented \(C^5\) interval bundle, and let a fixed larger interval collar
support the time-\(t\) maps for \(|t|\le T\).  Let the vector fields be
\(C^5\) in the state and form a compact \(C^2\) parameter family in that
topology.  Suppose invariant or strictly inward base faces, strict normal
exit faces retained on the larger collar, a forward-invariant vertical
secant cone, and a backward-invariant horizontal projectivized cone have
uniform margins.

Call a horizontal plane \(P\) at \(Z\) admissible when its whole orbit of
planes \(D\Phi_\mu^tP\), \(0\le t\le T\), stays in the horizontal cone and
the corresponding state orbit stays in the ambient collar.  If, for every
admissible plane and one fixed time \(T>0\),

\[
 \|(N^T)^{-1}\|\,\|A^T\|^j<1,
 \qquad 0\le j\le3,
\tag{32}
\]

then the maximal forward-staying set is the graph of a unique \(C^3\)
section.  It is locally maximal and normally expanding.  For a \(C^2\)
compact parameter family, its mixed derivatives of total order at most
three, with at most two parameter derivatives, are uniformly bounded.

To prove the lemma, fix a base fiber.  Strict exit signs divide the points
that first leave through the lower and upper normal faces into two disjoint
relatively open sets containing the two endpoints.  Connectedness of the
fiber supplies a staying point.  Strict vertical-cone invariance makes two
distinct staying points separate beyond the corridor width, so the point is
unique.  The same secant estimate makes the resulting section Lipschitz and
places its tangent planes in the horizontal cone.

On that closed cone of graphs, pull terminal graphs backward by the time
\(T\) map.  Work first in doubled coordinate collars at the base faces;
strict inwardness permits restriction back to the original base, while an
invariant face is preserved by the transform.  Uniqueness makes the local
constructions agree at every corner.  The zeroth through third homogeneous
jet maps are

\[
 (N^T)^{-1}\circ K\circ(A^T)^{\otimes j},
 \qquad 0\le j\le3.
\tag{33}
\]

Their norms are strictly below one by (32).  The graph transform is therefore
a uniform contraction first on continuous Lipschitz sections and then on
each affine jet bundle through order three.  Successive finite-horizon
transforms converge in the nested jet spaces to one \(C^3\) fixed graph.
The inhomogeneous terms in the differentiated transforms contain only lower
state jets and the state-\(C^5\), parameter-\(C^2\) coefficients.  Hence the
same uniform contractions at state orders two and one solve the equations
obtained after one and two parameter differentiations.  This gives
\(C^1_\mu C^2_X\) and \(C^2_\mu C^1_X\), respectively.  The base and all
corner charts are fixed, so there is no shifted-base-point or boundary trace
term.  This also proves local maximality and the asserted relative-boundary
statement.

For (27), the Dini cone calculation associated with (29) gives (30).
Along every admissible graph plane the tangent logarithmic norm is at most
\(\nu+\nu\), while the normal quotient conorm rate is at least
\(1-\nu-\nu\).  Integration for time \(T\) and (31) give

\[
 \|(N^T)^{-1}\|\,\|A^T\|^j
 \le e^{-\gamma_jT}<1,
 \qquad 0\le j\le3.
\tag{34}
\]

The corridor graph lemma now proves (5)--(9).  At \(z=0\), the only
forward-staying solution of \(\dot\alpha=\alpha\) inside the fixed normal
interval is \(\alpha=0\); hence

\[
 \Gamma_\mu(0,E,\beta)=0.
\tag{35}
\]

Because (34) is stated on the actual tangent and normal quotient cocycles,
normal expansion and bunching do not depend on the auxiliary graph slope
used to verify them.

## 6. Algebraic asymptotics and physical length

Let an orbit lie on (5) with \(z>0\).  From (14) and (24),

\[
 \frac d{d\tau}z^{-2}=2\pi,
 \qquad
 z(\tau)\asymp(1+\tau)^{-1/2}.
\tag{36}
\]

Thus \(z\downarrow0\).  This is an orbitwise statement.  In particular, it
does not assert that arbitrary graph points approaching the boundary with a
fixed nonzero \(\beta\) already have tail asymptotics.  Boundedness of a
forward-staying solution removes
the growing homogeneous mode in the \(\alpha\) equation, while variation
of constants in (17) gives

\[
 \alpha(\tau)=O(z(\tau)^2),
 \qquad \beta(\tau)=O(z(\tau)^2).
\tag{37}
\]

Using (37) in the exact energy relation (19) yields

\[
 \chi=q_*(\epsilon)-\frac{2a}{3}q_*(\epsilon)z+O(z^2),
 \qquad
 \pi=\delta q_*(\epsilon)+O(z).
\tag{38}
\]

Since \(w=\alpha-\beta=O(z^2)\), the definitions (12) give (10).
Moreover, (13) and (36) imply

\[
 x(\tau)-x(0)=\delta\int_0^\tau z(s)\,ds\longrightarrow+\infty.
\tag{39}
\]

The boundary is therefore an infinite-physical-distance algebraic end, not
a finite-time pole in another chart.

## 7. Primitive and finite-cut covariance

The pullback of the fixed physical primitive is useful for the subsequent
matching and finite-part stages.  Since

\[
 v=f(z^{-1})-wz^{-1},\qquad q=\chi z^{-2},
\]

direct differentiation gives

\[
\begin{aligned}
 \lambda_\delta
 ={}&\left\{\delta^{-1}\chi z^{-6}
       -\delta^{-1}\chi(1+w)z^{-4}
       -\epsilon\pi z^{-2}\right\}dz
       +\delta^{-1}\chi z^{-3}dw.
\end{aligned}
\tag{40}
\]

For any two transverse cuts \(C_0,C_1\) in the regular part of the same
outer orbit, ordinary additivity gives the exact identity

\[
 \int_{C_0}^{C}\lambda_\delta
 =\int_{C_0}^{C_1}\lambda_\delta
  +\int_{C_1}^{C}\lambda_\delta.
\tag{41}
\]

No limit is taken in (41).  It is the finite-cut covariance that V5 must
preserve through its chart transitions.  This note does not yet choose or
prove the divergent subtraction at \(z=0\); that is the distinct outer
action-finite-part obligation.

## 8. Source boundary and exclusions

Vo--Doelman--Kaper supply the physical and fast systems in their published
equations (2.4) and (2.6), the singular reduced slow flow in (5.3)--(5.5),
and the \(K_2\) and \(K_1\) charts beginning at (6.5)--(6.7).  Their
Remark 5.1 is a compact-away-from-the-fold Fenichel statement; it does not
construct the noncompact positive-parameter tail above.  Their Appendix C
expansion is stated on fixed finite central-time intervals and cannot replace
the corridor proof or its mixed parameter estimates.  Equations
(12)--(40) are new exact derivations from the model equations.

The theorem proves V4 and only V4.  It does not prove:

- arrival of the V2 algebraic-directed gate at (5);
- the \(K_2\)--\(K_1\)--outer exchange coefficient or matching operator;
- an outer action finite part;
- an exhaustive return--first-exit relation or symbolic coding; or
- temporal stability of any stationary PDE pattern.

Those claims retain their separate statuses in the claim register.
