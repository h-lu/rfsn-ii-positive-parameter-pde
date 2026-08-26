# Positive-parameter pole compactification and action finite part

**Evidence status: Proved.**  This note proves the local and global parts of
claim V3 on a compact parameter box strictly inside the positive part of the
V2 wedge.

The pole constructed here is a pole of the full positive-parameter spatial
system.  It is not obtained by persisting the singular core pole.  In
particular, its leading balance, indicial roots, logarithms, and action
subtraction are derived from the physical equations with \(\delta>0\).

## 1. Positive parameter class and theorem

Retain the constants \(A,\epsilon_-,\epsilon_+\) and the V2 wedge from
[CENTRAL_CONTINUATION.md](CENTRAL_CONTINUATION.md).  After decreasing its
upper radius once more, choose \(r_{\rm p}>0\) so that

\[
 \sqrt{\epsilon_+}A r_{\rm p}^3\le \frac14,
 \qquad
 2Ar_{\rm p}+\sqrt{\epsilon_+}A^2r_{\rm p}^4\le1,
\tag{1}
\]

and fix the nonempty compact positive box

\[
 \mathcal P_{\rm p}
 =\left[\frac12r_{\rm p},r_{\rm p}\right]
   \times[-A,A]\times[\epsilon_-,\epsilon_+],
 \qquad \mu=(r,a_2,\epsilon).
\tag{2}
\]

Throughout this note

\[
 \delta=r^2,\qquad
 a=1+\sqrt\epsilon\,r^3a_2,\qquad
 \ell=\sqrt6\,\delta.
\tag{3}
\]

The use of (2), rather than a box meeting \(r=0\), is deliberate.  Claim V3
requires a nonempty positive parameter range.  All estimates below are
uniform because \(\delta\) is bounded away from zero on (2); no uniform pole
claim at the cusp tip is being made.

Let \(I_{\rm p}=[-0.2,0.2]\) be the pole-directed phase arc in the common
transported lift fixed by V2, and let \(S_\mu(\phi)\) be the continued source
circle.  Physical spatial position is denoted by \(\mathsf x\), reserving
\(x\) for a central pole coordinate.

### Theorem V3

After the choice above, the following statements hold.

1. **A genuine positive pole and a nonempty source window.**  For every
   \((\mu,\phi)\in\mathcal P_{\rm p}\times I_{\rm p}\), the forward orbit
   from \(S_\mu(\phi)\) follows the V2 pole-gate branch to a unique
   straightened first hit of the exact section \(x=10\), then remains
   in the invariant pole cone defined in (12), and reaches
   \(u=+\infty\) at a finite physical position
   \(\mathsf x_{\rm b}(\mu,\phi)\).  It has no pole before that gate.  The
   gate first-hit margin, the cone-entry margin, and the hit speed of a
   common local pole section are positive and uniform.

2. **Regular-singular compactification.**  With physical remaining time

   \[
   \sigma=\mathsf x_{\rm b}-\mathsf x,
   \tag{4}
   \]

   the exact variables in (25) extend the pole to a two-dimensional boundary
   equilibrium manifold.  This manifold is normally hyperbolic, with
   normalized power spectrum

   \[
     \{-1,0,0,1,4\},
   \tag{5}
   \]

   and positive admissible indicial roots \(1,4\).  The local stable
   manifold of this normally hyperbolic equilibrium manifold includes its
   two label directions and projects diffeomorphically to an open local pole
   basin in the four physical state variables.

   The PDE is already in nondimensional physical \(\mathsf x\)-units.  In
   every logarithm below, \(\log\sigma\) means
   \(\log(\sigma/\sigma_{\rm ref})\) with the frozen reference
   \(\sigma_{\rm ref}=1\) in those units.

3. **Normalized resonant expansion.**  Every orbit in that local basin has
   unique labels \((Z_0,W_0,\kappa)\), and its compact variables have the
   mixed-parameter \(C^2\) expansion (36)--(39).  The raw center logarithm,
   the induced \(\sigma\log \sigma\) term, the order-four resonance, and
   the resulting \(\sigma^4(\log \sigma)^2\) term are all included
   explicitly.

4. **Action finite part.**  Let \(C\) be any fixed compact \(C^2\)
   transverse cut after the pole gate and before the local pole end.  For the
   frozen physical primitive

   \[
    \lambda_\delta=\epsilon p\,du-\delta^{-1}q\,dv,
   \tag{6}
   \]

   the action density and truncated action satisfy, at fixed physical
   remaining time,

   \[
   \begin{aligned}
    \lambda_\delta(\partial_{\mathsf x})
      &={6\epsilon\delta^3\over \sigma^4}
        -{2\epsilon\delta\over \sigma^2}
        -{\sqrt6\,\epsilon Z_0\over \sigma}
        +O_{C^2}\!\left((1+|\log \sigma|)^2\right),\\
    \mathscr A_{{\rm tr},C}(\sigma)
      &=2\epsilon\delta^3\sigma^{-3}
        -2\epsilon\delta \sigma^{-1}
        +\sqrt6\,\epsilon Z_0\log \sigma
        +\mathscr A_{{\rm fp},C}+o_{C^2}(1).
   \end{aligned}
   \tag{7}
   \]

   Consequently the finite Laurent--log subtraction

   \[
    \mathscr A_{{\rm fp},C}
     =\lim_{\sigma\downarrow0}\left[
       \mathscr A_{{\rm tr},C}(\sigma)
       -2\epsilon\delta^3\sigma^{-3}
       +2\epsilon\delta \sigma^{-1}
       -\sqrt6\,\epsilon Z_0\log \sigma\right]
   \tag{8}
   \]

   exists and is \(C^2\) jointly in the external parameters and source
   phase.  For fixed \(C\), it is unique for the physical normalization
   (4), (6), and the frozen logarithmic reference, and it obeys the exact
   moving-cut identity (50) when \(C\) changes.

Items 1--4 prove only the forward positive pole target.  They do not
construct the outer algebraic target, match that target through \(K_1\), or
give an exhaustive return--first-exit theorem.

## 2. Exact central cone and uniform gate entry

Write the exact central field (V2, equation (5)) as

\[
\begin{aligned}
 U'&=P,\\
 P'&=cU-V-BU^2+bU^3,\\
 V'&=Q,\\
 Q'&=U,
\end{aligned}
\qquad
\begin{aligned}
 B&=1+\sqrt\epsilon\,r^3a_2,\\
 b&={\sqrt\epsilon\over3}r^2,\\
 c&=2ra_2+\sqrt\epsilon\,r^4a_2^2.
\end{aligned}
\tag{9}
\]

The prime in this section is the universal central clock
\(\xi=\epsilon^{1/4}\mathsf x/r\).  Put

\[
 x=-U,\qquad y=-P,\qquad z=-V,\qquad \zeta=-Q,
\tag{10}
\]

and define

\[
 D={1\over2}x^2-z,\qquad K=xy-\zeta,
\tag{11}
\]

\[
 \mathcal K_\mu
  =\{x\ge10,\ y>0,\ D\ge0,\ K\ge0\}.
\tag{12}
\]

Equations (9) give the exact identities

\[
\begin{aligned}
 x'&=y,\\
 y'&=D+(B-\tfrac12)x^2+cx+bx^3,\\
 z'&=\zeta,\qquad \zeta'=x,\\
 D'&=K,\\
 K'&=y^2+xy'-x.
\end{aligned}
\tag{13}
\]

By (1), \(B\ge3/4\), \(|c|\le1\), and \(b>0\).  Hence, on
\(\mathcal K_\mu\),

\[
 y'\ge D+\frac14x^2-x+bx^3>0,
 \qquad
 K'\ge x\left(\frac14x^2-x\right)-x>0.
\tag{14}
\]

At \(D=0\), equation (13) gives \(D'=K\ge0\); at \(K=0\), (14)
points strictly inward; and at \(x=10\) or \(y=0\), the remaining displayed
derivatives point inward.  Thus (12) is forward invariant.

At \(r=0\), the interval data frozen in
[CENTRAL_CORE_IMPORT.md](CENTRAL_CORE_IMPORT.md) give, throughout the whole
closed phase arc \(I_{\rm p}\), a first hit of \(x=10\) with

\[
 y>26.31,\quad D>52.17,\quad K>262.34,
 \quad x'>26.31,\quad y'>102.17,\quad K'>1704.01.
\tag{15}
\]

V2 continues the physical gate germ, but its ambient isotopy need not leave
the equation \(x=10\) literally fixed.  We therefore record the first-hit
part of the straightening, rather than appeal only to a local slide.  Inside
the common V2 flow-domain buffer of the frozen compact pre-gate tube, choose
a two-sided terminal flowbox collar
\(\mathcal C_{\rm term}\) and put \(g=x-10\).  The certified first hit and
compactness give numbers \(\eta_g,\eta_y>0\) such that

\[
 g\le-\eta_g
 \quad\hbox{off }\mathcal C_{\rm term},
 \qquad
 F_0g=y\ge\eta_y
 \quad\hbox{on }\mathcal C_{\rm term}.
\tag{15a}
\]

Treat \(g\) and \(F_\mu g\) as two additional observables on the V2 compact
flow tube.  Its state-\(C^1\) continuation retains the respective bounds
\(-\eta_g/2\) and \(\eta_y/2\).  The moving gate lies in the continued
terminal collar.  The implicit-function theorem now gives a unique short
\(C^2\) orbit slide from it to \(g=0\); monotonicity inside the collar and
the negative bound outside it show that this is the source orbit's genuine
first hit of \(x=10\), not merely a nearby intersection.  Decreasing
\(r_{\rm p}\) makes the slide uniformly short, event-free, and small enough
to consume at most half of every strict inequality in (15).

The resulting first-hit map is \(C^2\), and its earlier-event exclusion has
the normalized margin \(m_0/4\).  Compactness and one further decrease of
\(r_{\rm p}\) therefore retain, for example,

\[
 y\ge13,\quad D\ge26,\quad K\ge131,
 \quad x'\ge13,\quad y'\ge51,\quad K'\ge852
\tag{16}
\]

at the continued gate, together with the earlier-event margin \(m_0/4\).
The entire pre-gate flow tube is compact in physical state space, so no pole
can occur before this hit.
This proves a parameter-uniform, nonempty entry into the interior of (12);
it does not infer entry merely from the name of the V2 gate.
The open interval \(I_{\rm p}^{\circ}=(-0.2,0.2)\) is therefore a nonempty
source phase window; its closure is used in the theorem to obtain uniform
margins.

## 3. Finite-time blow-up and the dominant physical balance

Every V2 source orbit lies in \(\widehat H_\mu^{-1}(0)\), equivalently in
the physical level \(\mathcal G=\mathcal G(O)\), because it belongs to the
unstable manifold of the homogeneous equilibrium.  Let such an orbit start
in the compact gate family (16).  Since
\(x'=y>0\), use \(x\) as an independent variable.  From (13)--(14),

\[
 y{dy\over dx}=y'\ge bx^3,
 \qquad
 y(x)^2\ge y(x_0)^2+{b\over2}(x^4-x_0^4).
\tag{17}
\]

The gate bound \(y\ge13\) and \(y'>0\) show that an orbit existing for all
forward \(\xi\) would have \(x\to\infty\).  On the other hand, a finite
maximal orbit cannot stop while \(x\) stays bounded: then (13) bounds
\(\zeta\), next \(z\), and then \(y\), so the polynomial ODE continuation
theorem extends the solution.  Thus in either case \(x\) tends to infinity
at the maximal forward time.  Because \(b\) has a positive minimum on (2),
(17) bounds the time required to reach infinity by the convergent integral

\[
 \xi_{\rm b}-\xi
   =\int_x^\infty{dX\over y(X)}<\infty
\tag{18}
\]

uniformly for the compact gate family.

The exact zero-energy identity, obtained by substituting (10) in
\(\widehat H_\mu=0\), is

\[
 y^2=\zeta^2-2xz+cx^2+{2B\over3}x^3+{b\over2}x^4.
\tag{19}
\]

The lower bound in (17) first gives

\[
 {d\zeta\over dx}={x\over y}=O(x^{-1}),
 \qquad
 {dz\over dx}={\zeta\over y}=O((1+\log x)x^{-2}).
\tag{20}
\]

Thus \(z\to z_\infty\), \(\zeta=O(1+\log x)\), and (19) then closes the
sharp estimates

\[
 {y\over x^2}\longrightarrow k:=\sqrt{b/2}
 ={\epsilon^{1/4}r\over\sqrt6},
 \qquad
 \zeta-{1\over k}\log x
    =\zeta_\infty+O(x^{-1}),
 \qquad
 z_\infty-z=O((1+\log x)x^{-1}).
\tag{21}
\]

Indeed, (19) gives \(y=kx^2(1+O(x^{-1}))\); substituting this in the
first equation of (20) makes the difference from \((kx)^{-1}\) integrable.
All constants and convergences in (20)--(21) are uniform on the compact
parameter and gate family.  A second integration yields

\[
 \xi_{\rm b}-\xi={1\over kx}+O(x^{-2}),
\tag{22}
\]

again uniformly.

The exact physical inverse scaling is

\[
\begin{aligned}
 u&=a+\sqrt\epsilon\,r^2x,&
 p&=\epsilon^{3/4}r^3y,\\
 v&=f(a)+\epsilon r^4z,&
 q&=\epsilon^{5/4}r^3\zeta,\\
 d\mathsf x&=r\epsilon^{-1/4}d\xi.
\end{aligned}
\tag{23}
\]

Consequently \(\mathsf x_{\rm b}<\infty\).  With
\(\sigma=r\epsilon^{-1/4}(\xi_{\rm b}-\xi)\), equations (21)--(23) give

\[
 {\sigma u\over\ell}\to1,\qquad
 {\sigma^2p\over\ell\delta}\to1,\qquad
 q+\ell\epsilon\log \sigma\to W_0,\qquad
 v-\ell\epsilon \sigma\log \sigma\to Z_0,
\tag{24}
\]

for finite constants \(W_0,Z_0\).  Notice that \(Z_0=\lim v\), whereas
the logarithmic subtraction is essential in the definition of \(W_0\).
More explicitly,

\[
 Z_0=f(a)+\epsilon r^4z_\infty,
 \qquad
 W_0=\epsilon^{5/4}r^3\zeta_\infty
       +\ell\epsilon\log\!\left({\sqrt6\over\sqrt\epsilon}\right).
\]

This proves the positive-parameter dominant balance directly from the full
system; it has not used a singular-core pole asymptotic.

## 4. Exact regular-singular compactification

For \(\sigma>0\), define the physical, normalized variables

\[
 X={\sigma u\over\ell},\qquad
 Y={\sigma^2p\over\ell\delta},\qquad
 W=q+\ell\epsilon\log \sigma,
 \qquad
 Z=v-\ell\epsilon \sigma\log \sigma.
\tag{25}
\]

Use the desingularized derivative

\[
 \dot{\ }=\sigma{d\over d\mathsf x},
 \qquad \dot \sigma=-\sigma.
\tag{26}
\]

Direct substitution in the physical stationary system

\[
 \delta u_{\mathsf x}=p,\quad
 \delta p_{\mathsf x}=\frac13u^3-u-v,\quad
 v_{\mathsf x}=q,\quad q_{\mathsf x}=\epsilon(u-a)
\tag{27}
\]

gives the exact field

\[
\begin{aligned}
 \dot \sigma&=-\sigma,\\
 \dot X&=-X+Y,\\
 \dot Y&=-2Y+2X^3-{\sigma^2\over\delta^2}X
       -{\sigma^3\over\ell\delta^2}Z
       -{\epsilon\over\delta^2}\sigma^4\log \sigma,\\
 \dot W&=\ell\epsilon(X-1)-a\epsilon \sigma,\\
 \dot Z&=\sigma(W+\ell\epsilon).
\end{aligned}
\tag{28}
\]

The function \(\sigma^4\log \sigma\), extended by zero at \(\sigma=0\), is \(C^3\).
Thus (28) is a state-\(C^3\), parameter-smooth vector field on the positive
half-space; using \(\sigma^4\log|\sigma|\) gives a local signed \(C^3\) extension.
This is the regular-singular regularity needed for two external parameter
derivatives.  No false \(C^4\) assertion is made.

For each fixed \(\mu\), the positive pole boundary over an enlarged label
rectangle \(\mathcal B^+\subset\mathbb R^2\) is the two-dimensional
equilibrium manifold

\[
 \mathcal N_{\mu,\mathcal B^+}
 =\{\sigma=0,\ X=Y=1,\ (Z,W)\in\mathcal B^+\}.
\tag{29}
\]

The coordinates of a point of (29) are denoted \((Z_0,W_0)\).  The gate
limits form a compact set; choose
\(\mathcal B\Subset\operatorname{int}\mathcal B^+\) containing it.  Extend
the label directions and cut off the extended field outside a still larger
rectangle before applying the compact NHIM theorem.  The original and
extended fields agree near \(\mathcal B\), where every construction below
takes place.  Linearization at a point
of (29), in \((\sigma,X-1,Y-1,W-W_0,Z-Z_0)\), is triangular with the
\((X,Y)\)-block

\[
 \begin{pmatrix}-1&1\\6&-2\end{pmatrix},
\tag{30}
\]

and spectrum

\[
 \{-1,-4,0,0,+1\}.
\tag{31}
\]

The zero eigenvalues are tangent to the label manifold; the normal rates
are \(-1,-4,+1\), uniformly separated from zero.  Therefore every compact
subrectangle of (29) is contained in a normally hyperbolic equilibrium
manifold.  Its unique local stable set

\[
 \mathcal W^s_\mu
 :=W^s_{\rm loc}(\mathcal N_{\mu,\mathcal B^+})
 =\{z:\ \Phi_\tau(z)\hbox{ stays local and }
       \operatorname{dist}(\Phi_\tau(z),\mathcal N_{\mu,\mathcal B^+})
       \to0\}
\]

is a state-\(C^3\), parameter-\(C^2\) manifold of dimension four: two
directions are tangent label directions and two are stable fibers.

The flow time in (26) is \(\tau=-\log \sigma+\text{constant}\).  Hence an
eigenvalue \(\lambda\) corresponds to a power \(\sigma^{-\lambda}\), and (31)
becomes the normalized power spectrum (5).  The root \(-1\) is the excluded
growing solution, \(0,0\) are the two end labels, and the admissible positive
roots are \(1,4\).

The asymptotics (24) show that every orbit from the gate family converges to
the interior of \(\mathcal B\) in (29).  The defining local-stable-set
characterization therefore puts those orbits in \(\mathcal W^s_\mu\).
Uniformity in Section 3 and compactness give a common finite cover by local
stable-manifold projection charts.  A common pole section is selected after
these charts are inverted in Section 6.

## 5. Indicial resonances and the normalized polyhomogeneous jet

Set \(h=X-1\), \(L=\log \sigma\), and use
\(Y=X-\sigma X_\sigma\), which follows exactly
from the second equation of (28).  The last two equations of (28) integrate
to

\[
\begin{aligned}
 W(\sigma)&=W_0+a\epsilon \sigma
       -\ell\epsilon\int_0^\sigma{h(t)\over t}\,dt,\\
 Z(\sigma)&=Z_0-\int_0^\sigma(W(t)+\ell\epsilon)\,dt.
\end{aligned}
\tag{32}
\]

Eliminating \(Y\) gives the exact scalar regular-singular equation

\[
 \mathcal Lh
 =6h^2+2h^3-{\sigma^2\over\delta^2}(1+h)
  -{\sigma^3\over\ell\delta^2}Z
  -{\epsilon\over\delta^2}\sigma^4L,
 \qquad
 \mathcal L=(\sigma\partial_\sigma-4)(\sigma\partial_\sigma+1).
\tag{33}
\]

Uniform entry and the finite NHIM atlas from Section 4 put the source-tail
intersections in a compact stable-fiber block.  Fix a finite
stable-coordinate bound \(K_\kappa>0\) containing that block and work on
\(\mathcal P_{\rm p}\times\mathcal B\times[-K_\kappa,K_\kappa]\).  The fixed-section
argument below identifies this stable coordinate with \(\kappa\); the common
small \(\sigma_0\) is chosen for this compact set.

Thus the scalar indicial roots are \(-1,4\).  The order-two and order-three
forcings are nonresonant.  At order four the constant forcing and the
explicit logarithmic forcing lie at the root \(4\).  Put

\[
\begin{aligned}
 x_2&={1\over6\delta^2},&
 x_3&={Z_0\over4\ell\delta^2},\\
 m_2&=-{\epsilon\over10\delta^2},&
 m_1&={W_0\over5\ell\delta^2}
          +{6\epsilon\over25\delta^2}.
\end{aligned}
\tag{34}
\]

For \(g(L)=m_2L^2+m_1L+\kappa\),

\[
 \mathcal L(\sigma^4g(L))
 =\sigma^4\bigl(g''+5g'\bigr).
\tag{35}
\]

The coefficient of \(\sigma^4L\) in (33) gives \(10m_2=-\epsilon/\delta^2\).
The constant coefficient gives

\[
 2m_2+5m_1={W_0+\ell\epsilon\over\ell\delta^2}.
\]

This proves (34).  The cancellation
\(6x_2^2-x_2/\delta^2=0\) is why no omitted constant appears in this
identity.

The resulting unique normalized jet on \(\mathcal W^s_\mu\) is

\[
 X=1+x_2\sigma^2+x_3\sigma^3
   +\sigma^4\{m_2L^2+m_1L+\kappa\}
   +O_{C^2}\!\left(\sigma^5(1+|L|)^2\right),
\tag{36}
\]

\[
 Y=1-x_2\sigma^2-2x_3\sigma^3
   +\sigma^4\{-3g(L)-g'(L)\}
   +O_{C^2}\!\left(\sigma^5(1+|L|)^2\right),
\tag{37}
\]

\[
 W=W_0+a\epsilon \sigma-{\ell\epsilon x_2\over2}\sigma^2
      -{\ell\epsilon x_3\over3}\sigma^3
      +O_{C^2}\!\left(\sigma^4(1+|L|)^2\right),
\tag{38}
\]

\[
\begin{aligned}
 Z={}&Z_0-(W_0+\ell\epsilon)\sigma-{a\epsilon\over2}\sigma^2
       +{\ell\epsilon x_2\over6}\sigma^3
       +{\ell\epsilon x_3\over12}\sigma^4\\
    &+O_{C^2}\!\left(\sigma^5(1+|L|)^2\right).
\end{aligned}
\tag{39}
\]

Here \(O_{C^2}\) means that the same bound holds after every mixed
derivative of total order at most two in
\((\mu,Z_0,W_0,\kappa)\), with \(\sigma\) held fixed.

For completeness, these are all nontrivial resonances activated by the exact
field through the pole normalization:

1. In raw variables, \(\sigma q_{\mathsf x}\to\ell\epsilon\) forces the center
   logarithm \(-\ell\epsilon\log \sigma\) in \(q\); subtracting it defines
   \(W\).
2. Integrating \(v_{\mathsf x}=q\) then forces
   \(\ell\epsilon \sigma\log \sigma\); subtracting it defines \(Z\).
3. The positive roots satisfy the integer relation \(4=4\cdot1\).  The
   constant order-four forcing produces \(\sigma^4\log \sigma\), while the exact
   \(\sigma^4\log \sigma\) forcing in (33) produces
   \(\sigma^4(\log \sigma)^2\).  The coefficient \(\kappa \sigma^4\) is the free stable
   root-four mode.

Relations involving a zero root merely make the displayed coefficients
depend on the center labels.  The scalar indicial polynomial has no root
above four, so later logarithms are nonresonant propagation of those already
displayed, not new indicial resonances.  In particular, the order-two and
order-three terms in (36) are forced terms, not indicial roots.

To justify the remainder rather than use (36) formally, insert
\(h=x_2\sigma^2+x_3\sigma^3+\sigma^4g(L)+R\) in (32)--(33).  After the displayed
cancellations, the residual is
\(O_{C^2}(\sigma^5(1+|L|)^2)\); the same algebraic bound holds after
\(D_\sigma^j\), \(j\le2\), because the displayed jet is polyhomogeneous.
On the weighted space with norm

\[
 D_\sigma=\sigma\partial_\sigma,
 \qquad
 \|R\|_{*,2}
 =\max_{0\le j\le2}\sup_{0<\sigma\le \sigma_0}
 { |D_\sigma^jR(\sigma)|
   \over \sigma^5(1+|\log \sigma|)^2},
\tag{40}
\]

the inverse of
\((D_\sigma-4)(D_\sigma+1)\), with the growing
\(\sigma^{-1}\) mode removed and the \(\sigma^4\) coefficient fixed by
\(\kappa\), is bounded.  Indeed, for a residual \(f\) that inverse is the
explicit Green operator

\[
 (\mathscr Kf)(\sigma)
 =\sigma^{-1}\int_0^\sigma t^4
     \left(\int_0^t\rho^{-5}f(\rho)\,d\rho\right)dt.
\]

It maps the conormal weight in (40) to itself; applying
\(D_\sigma^j\), \(j\le2\), to the two factored first-order equations gives
the same bound.  Equations (32) are Volterra operators on this conormal
space.  Their nonlinear composition has Lipschitz constant
\(O(\sigma_0)\); choosing \(\sigma_0\) uniformly small gives a contraction.
Differentiate that fixed-point equation up to twice in
\((\mu,Z_0,W_0,\kappa)\).  The differentiated equations have the same
bounded Green inverse and a contraction term with norm less than one, so
every mixed derivative of total external order at most two satisfies (40).
In particular \(D_\sigma R\), which enters \(Y=X-D_\sigma X\), has the
claimed order.  This proves (36)--(39), including their mixed conormal
regularity and the density remainder used below.

The Fuchsian family stays local and converges to (29), hence is contained in
\(\mathcal W^s_\mu\).  Conversely, take any orbit in that local stable set.
NHIM exponential tracking first gives \(h=O(\sigma^\eta)\) for some
\(\eta>0\).  Applying variation of constants to (32)--(33) repeatedly
improves the exponent to \(h=O(\sigma^2)\), after which
\(W-W_0=O(\sigma)\) and \(Z-Z_0=O(\sigma)\).  Successively subtracting the
nonresonant order-two and order-three solutions and then the two resonant
logarithmic terms in (36) leaves \(\widetilde h\) satisfying

\[
 \widetilde h(\sigma)
 =\kappa\sigma^4+(\mathscr Kf_{\widetilde h})(\sigma),
 \qquad
 f_{\widetilde h}
 =O\!\left(\sigma^5(1+|\log\sigma|)^2\right).
\]

The Green estimate following (40) shows that
\(\sigma^{-4}\widetilde h\to\kappa\) and that the remainder obeys (40).
This proves existence and uniqueness of \(\kappa\) for every local stable
orbit; fixed-point uniqueness then identifies that orbit with the Fuchsian
solution carrying \((Z_0,W_0,\kappa)\).

This exhaustion is nondegenerate on a fixed positive section, not at the
boundary where the root-four mode vanishes.  For every sufficiently small
fixed \(\sigma_*>0\), the map
\((Z_0,W_0,\kappa)\mapsto(X,Y,Z,W)|_{\sigma_*}\) has

\[
 \partial_\kappa(X,Y,Z,W)
 =\sigma_*^4(1,-3,0,-\ell\epsilon/4)+
   O\!\left(\sigma_*^5(1+|\log\sigma_*|)^2\right),
\]

while the \((Z_0,W_0)\)-block in \((Z,W)\) tends to the identity.  It has
rank three and is therefore a local coordinate chart on the
three-dimensional section
\(\mathcal W^s_\mu\cap\{\sigma=\sigma_*\}\).  Flow saturation proves that
the Fuchsian family exhausts the required branch of \(\mathcal W^s_\mu\).
The same Green representation at \(\sigma_*\) shows that \(\kappa\) is
\(C^2\) in the stable-manifold point and in \(\mu\).

In the full four-dimensional pole basin, \(\kappa\) is a free stable-fiber
coordinate.  Substitution of (36)--(39) into the physical conserved quantity
\(\mathcal G\) cancels every power and logarithmic divergence and gives the
finite identity

\[
 \mathcal G
 ={7\epsilon\over12}-{186\over25}\epsilon^2\delta^2
  -30\epsilon\delta^4\kappa-\epsilon aZ_0
  -{6\over5}\ell\epsilon W_0-{1\over2}W_0^2.
\]

In particular,

\[
 {\partial\mathcal G\over\partial\kappa}
   =-30\epsilon\delta^4\ne0.
\tag{41}
\]

The two contributions are \(-18\epsilon\delta^4\) from
\(\epsilon p^2/2\) and \(-12\epsilon\delta^4\) from
\(-\epsilon u^4/12\); all other \(\kappa\)-terms vanish in the limit.
Thus on the fixed source energy
\(\mathcal G=\mathcal G(O)=-\epsilon F(a)\), \(\kappa\) is a unique
\(C^2\) function of
\((\mu,Z_0,W_0)\).  The action subtraction below is unchanged by this
constraint.

The parameters \((\sigma,Z_0,W_0,\kappa)\) are genuine physical-state
coordinates.  Indeed, the inverse of (25), restricted to (36)--(39), is

\[
 u={\ell X\over \sigma},\quad
 p={\ell\delta Y\over \sigma^2},\quad
 q=W-\ell\epsilon\log \sigma,\quad
 v=Z+\ell\epsilon \sigma\log \sigma.
\tag{42}
\]

The leading determinant of its \((u,p)\) derivatives with respect to
\((\sigma,\kappa)\) is

\[
 \det
 \begin{pmatrix}
  -\ell \sigma^{-2}+O(1)&\ell \sigma^3+o(\sigma^3)\\
  -2\ell\delta \sigma^{-3}+O(1)&-3\ell\delta \sigma^2+o(\sigma^2)
 \end{pmatrix}
 =5\ell^2\delta+o(1).
\tag{43}
\]

The cross blocks must also be controlled because \(q_\sigma\) is singular.
With rows ordered as \((u,p;v,q)\) and columns as
\((\sigma,\kappa;Z_0,W_0)\), write the full Jacobian in blocks
\(\bigl(\begin{smallmatrix}\mathsf A&\mathsf B\\
\mathsf C&\mathsf D\end{smallmatrix}\bigr)\).  Equations (36)--(39) give

\[
 \mathsf B=
 \begin{pmatrix}
  O(\sigma^2)&O(\sigma^3|L|)\\
  O(\sigma)&O(\sigma^2|L|)
 \end{pmatrix},
 \qquad
 \mathsf C=
 \begin{pmatrix}
  O(|L|)&O(\sigma^5)\\
  O(\sigma^{-1})&O(\sigma^4)
 \end{pmatrix},
 \qquad
 \mathsf D=I+o(1).
\]

Here \(\mathsf A\) is the matrix in (43).  Its explicit inverse and the
displayed orders imply
\(\mathsf C\mathsf A^{-1}\mathsf B=o(1)\).  Hence the Schur formula gives,
uniformly on the positive compact parameter box,

\[
 \det D_{(\sigma,\kappa,Z_0,W_0)}(u,p,v,q)
 =\det\mathsf A\,
   \det(\mathsf D-\mathsf C\mathsf A^{-1}\mathsf B)
 =5\ell^2\delta+o(1)\ne0.
\]

The inverse-function theorem now proves the local diffeomorphism and the
open pole-basin assertion in Theorem V3.

## 6. Uniform global entry and mixed regularity of end data

The proof so far gives more than convergence.  By the uniform estimates in
Section 3, a single sufficiently large central section \(x=M\) lies inside
the physical image (42) of the local pole basin for every point of the
compact source and parameter family.  Its hit is unique and transverse
because \(x'=y\ge \underline cM^2\) for a constant
\(\underline c>0\).  The compact central flow to \(x=M\), the hit
time, and the hit state are \(C^2\) in \((\mu,\phi)\).

Apply the finite family of inverses of (42) at that hit.  On overlaps they
agree because the physical remaining time and the three normalized end
labels are unique; hence they glue to a single \(C^2\) map

\[
 (\mu,\phi)\longmapsto
 (\sigma_M,Z_0,W_0,\kappa).
\tag{44}
\]

The local-stable-set characterization and the choice of \(M\) ensure that
the whole forward segment from the \(x=M\) hit to the boundary stays in the
finite projection atlas.  The compact domain and positivity give
\(\underline\sigma_M:=\min\sigma_M>0\).  Fix
\(0<\sigma_0<\underline\sigma_M/2\).
The pole position equals the physical position at \(x=M\) plus
\(\sigma_M\), so \(\mathsf x_{\rm b}\) is \(C^2\).  Each orbit hits the
common local section \(\sigma=\sigma_0\) exactly once, after a physical
flight of at least \(\underline\sigma_M/2\).  Since
\(d\sigma/d\mathsf x=-1\), its physical hit speed is exactly one; compact
containment supplies a uniform flow-domain margin.  Together with (16) and
the V2 earlier-event margin, this proves the global and uniform first-hit
assertion in item 1 of Theorem V3 without differentiating an improper flight
integral.

## 7. Exact action density and finite Laurent--log subtraction

Along a physical orbit, (6) and (27) give the exact density

\[
\begin{aligned}
 \lambda_\delta(\partial_{\mathsf x})
 &=\epsilon p u_{\mathsf x}-\delta^{-1}qv_{\mathsf x}
  ={\epsilon p^2-q^2\over\delta}\\
 &=6\epsilon\delta^3\sigma^{-4}Y^2
   -\delta^{-1}(W-\ell\epsilon\log \sigma)^2.
\end{aligned}
\tag{45}
\]

From (34), (37),

\[
 Y^2=1-2x_2\sigma^2-4x_3\sigma^3
       +O_{C^2}(\sigma^4(1+|\log \sigma|)^2).
\tag{46}
\]

Using \(x_2=1/(6\delta^2)\),
\(x_3=Z_0/(4\ell\delta^2)\), and \(\ell=\sqrt6\delta\) in
(45)--(46) proves the density expansion in (7).  The \(q^2\) term is only
\(O_{C^2}((1+|\log \sigma|)^2)\), which is integrable at \(\sigma=0\).  In
particular, \(W_0\) and \(\kappa\) first enter the integrable remainder;
\(Z_0\) is the only end label in a nonintegrable subleading term.

Let \(C\) be any compact transverse cut before the pole, oriented toward
the pole, and define

\[
 \mathscr A_{{\rm tr},C}(\sigma)
 =\int_{C}^{\mathsf x_{\rm b}-\sigma}\lambda_\delta.
\tag{47}
\]

Since \(d\mathsf x=-d\sigma\), integration of (7) proves (8).  More explicitly,
put

\[
 F_{\rm div}(\sigma)=2\epsilon\delta^3\sigma^{-3}
 -2\epsilon\delta \sigma^{-1}+\sqrt6\epsilon Z_0\log \sigma.
\tag{48}
\]

Then \(-F_{\rm div}'\) is exactly the three-term singular density in (7),
and

\[
 \mathscr A_{{\rm fp},C}
 =\int_C^{\{\sigma=\sigma_0\}}\lambda_\delta-F_{\rm div}(\sigma_0)
  +\int_0^{\sigma_0}
   \left[\lambda_\delta(\partial_{\mathsf x})
          +F_{\rm div}'(t)\right]dt.
\tag{49}
\]

The last integrand, with two mixed derivatives and fixed \(t\), is bounded
by \(C(1+|\log t|)^2\).  Formula (49), dominated convergence, and Section 6
prove that \(\mathscr A_{{\rm fp},C}\) is \(C^2\) jointly in
\((\mu,\phi)\).  The same formula applies to every compact \(C^2\) family
of cuts.

If \(C_0\) and \(C_1\) are two such cuts, with \(C_1\) later along the same
oriented branch, exact additivity of the line integral gives

\[
 \boxed{\quad
 \mathscr A_{{\rm fp},C_0}
 =\int_{C_0}^{C_1}\lambda_\delta
  +\mathscr A_{{\rm fp},C_1}.
 \quad}
\tag{50}
\]

Thus a finite central action followed by the pole finite part is independent
of the chosen matching cut.  This is an exact identity, not an asymptotic
comparison.

Finally, the subtraction is coordinate-unique under the normalization of
the theorem.  The remaining time \(\sigma=\mathsf x_{\rm b}-\mathsf x\) is a
physical quantity, \(\ell=\sqrt6\delta\) is forced by the dominant balance,
and

\[
 W_0=\lim_{\sigma\downarrow0}(q+\ell\epsilon\log \sigma),
 \qquad
 Z_0=\lim_{\sigma\downarrow0}(v-\ell\epsilon \sigma\log \sigma)
\tag{51}
\]

are physical limits.  The free root-four coordinate is fixed by

\[
 \kappa=\lim_{\sigma\downarrow0}\sigma^{-4}
 \left[X-1-x_2\sigma^2-x_3\sigma^3
       -\sigma^4(m_2(\log \sigma)^2+m_1\log \sigma)\right].
\tag{52}
\]

Equations (4), (6), and (51), together with the frozen logarithmic reference
following (4), rather than an arbitrary rescaling of \(\sigma\) or addition
of an unfrozen exact differential to the primitive, determine the finite
constant in (8).  Any auxiliary compactification respecting those physical
normalizations computes the same limit.

## 8. Dependency boundary

The proof uses V2 only up to the compact pole gate, its transported source
arc, and its strict first-hit margins.  Everything after that gate--cone
invariance, finite-time blow-up, boundary normal hyperbolicity, resonant
expansion, basin entry, and action renormalization--is proved here for the
full \(\delta>0\) equations.

The following claims are not consequences of Theorem V3:

- an outer algebraic future-staying hypersurface;
- \(K_2\)--\(K_1\)--outer matching;
- an algebraic action finite part;
- exhaustiveness of all high-winding source phases;
- symbolic coding or temporal stability.

Those remain the separate obligations V4--V7 and S1.
