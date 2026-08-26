# A positive-diffusion localized Brusselator profile

**Evidence status: Proved.**  The only external mathematical input is the
frozen core result in
[CORE_HOMOCLINIC_IMPORT.md](CORE_HOMOCLINIC_IMPORT.md); every
positive-parameter continuation, tail, positivity, and scaling conclusion is
proved analytically below.  The dependency and quantifier audit in Section 6
is complete.

## 1. Statement in scaled and PDE variables

Let \(F_r\) be the polynomial vector field

\[
\begin{aligned}
 U'&=P,\\
 P'&=-U^2-V-2r^2UV-r^4U^2V,\\
 V'&=Q,\\
 Q'&=U+r^2(U^2+V)+2r^4UV+r^6U^2V,
\end{aligned}
\tag{1}
\]

with reverser
\(\mathcal R(U,P,V,Q)=(U,-P,V,-Q)\).  For
\(0<\eta<2^{-1/2}\), write

\[
 X_\eta=\left\{Z\in C^0(\mathbb R,\mathbb R^4):
 \|Z\|_\eta:=\sup_{\xi\in\mathbb R}
 e^{\eta|\xi|}|Z(\xi)|<\infty\right\}.
\tag{2}
\]

### Theorem B

There are \(r_0>0\), \(C>0\), and
\(0<\eta<2^{-1/2}\), and a \(C^1\) map

\[
 [0,r_0]\longrightarrow X_\eta,\qquad r\longmapsto Z_r,
\tag{3}
\]

with the following properties.

1. \(Z_0\) is the selected transverse symmetric core homoclinic imported in
   [CORE_HOMOCLINIC_IMPORT.md](CORE_HOMOCLINIC_IMPORT.md).  For every
   \(0<r\le r_0\), \(Z_r\) is a nonconstant
   \(\mathcal R\)-symmetric homoclinic orbit of (1), normalized by
   \(Z_r(0)\in\operatorname{Fix}\mathcal R\).

2. The tails are uniform:

   \[
   |Z_r(\xi)|\le C e^{-\eta|\xi|}
   \quad
   (0\le r\le r_0,\ \xi\in\mathbb R),
   \tag{4}
   \]

   and \(\|Z_r-Z_0\|_\eta\to0\) as \(r\to0\).

3. Put \(d=r^4\).  Then

   \[
   u_d(x)=1+r^2U_r(x/r),\qquad
   v_d(x)=1+r^4V_r(x/r)
   \tag{5}
   \]

   is a smooth, nonconstant, even stationary solution of

   \[
   u_t=d u_{xx}-2u+1+u^2v,\qquad
   v_t=v_{xx}+u-u^2v
   \tag{6}
   \]

   on \(\mathbb R\).  It satisfies

   \[
   u_d(x)>0,\qquad v_d(x)>0,\qquad
   (u_d(x),v_d(x))\longrightarrow(1,1)
   \quad\text{as }|x|\to\infty.
   \tag{7}
   \]

4. The amplitudes have nonzero limiting coefficients:

   \[
   \begin{aligned}
   d^{-1/2}\|u_d-1\|_\infty
     &\longrightarrow\|U_0\|_\infty>0,\\
   d^{-1}\|v_d-1\|_\infty
     &\longrightarrow\|V_0\|_\infty>0.
   \end{aligned}
   \tag{8}
   \]

   In particular, the activator and inhibitor amplitudes are respectively
   \(\Theta(d^{1/2})\) and \(\Theta(d)\).

5. The uniform physical localization estimate is

   \[
   d^{-1/2}|u_d(x)-1|+d^{-1}|v_d(x)-1|
   \le C e^{-\eta |x|/d^{1/4}}.
   \tag{9}
   \]

   To give “width” an unambiguous meaning, let \(W_u(d)\), respectively
   \(W_v(d)\), be the length of the connected component containing \(x=0\)
   of

   \[
   \begin{aligned}
   \{x:|u_d(x)-1|&\ge\tfrac12|u_d(0)-1|\},\\
   \{x:|v_d(x)-1|&\ge\tfrac12|v_d(0)-1|\}.
   \end{aligned}
   \tag{10}
   \]

   There are constants \(0<c<C_w<\infty\), independent of \(d\), such
   that

   \[
   c\,d^{1/4}\le W_u(d),W_v(d)\le C_w\,d^{1/4}
   \qquad(0<d\le r_0^4).
   \tag{11}
   \]

No uniqueness outside the continued local branch, temporal stability,
exact-action identity, or multipulse conclusion is part of the theorem.

## 2. Uniform hyperbolic manifolds

We first record the parameter-dependent local result needed for the tails.
It is included with its fixed-point proof so that no uniformity in \(r\) is
hidden in a citation.

### Lemma 2.1

After decreasing \(r_0>0\), the origin of \(F_r\) has two-dimensional local
stable and unstable manifolds \(W^s_{\rm loc}(r)\) and
\(W^u_{\rm loc}(r)\) for \(|r|\le r_0\).  There are fixed two-dimensional
parameter spaces for which the local graph maps and their half-orbit
parameterizations are \(C^1\) in both the parameter and \(r\).  The half
orbits and their first \(r\)-derivatives satisfy exponential estimates with
constants independent of \(r\).  A compact patch may be flowed for any
bounded time on which its base flowout stays in a compact set; the continued
flowout has the same \(C^1\) parameter dependence.

#### Proof

Write

\[
 F_r(Z)=A_rZ+N_r(Z),\qquad N_r(0)=D N_r(0)=0.
\tag{12}
\]

By the calculation in
[MODEL_AND_SCALING.md](MODEL_AND_SCALING.md), the eigenvalues of \(A_r\)
are

\[
 \pm\alpha(r)\pm i\beta(r),\qquad
 \alpha(r)=\tfrac12\sqrt{2+r^2},\quad
 \beta(r)=\tfrac12\sqrt{2-r^2}.
\tag{13}
\]

Extend the polynomial family to negative \(r\), and choose \(r_0<1\).
The stable and unstable Riesz projections \(\Pi_r^s,\Pi_r^u\) then depend
smoothly on \(r\).  Fix rates

\[
 0<\eta<\eta_1<a_0<\inf_{|r|\le r_0}\alpha(r).
\tag{14}
\]

After decreasing \(r_0\), if necessary, the restrictions

\[
 J_r^u:=\Pi_r^u|_{E_0^u}:E_0^u\longrightarrow E_r^u,
 \qquad
 J_r^s:=\Pi_r^s|_{E_0^s}:E_0^s\longrightarrow E_r^s
\tag{15}
\]

are smooth linear isomorphisms with uniformly bounded norms and inverses.
They give fixed parameter spaces for the moving spectral subspaces.  Uniform
finite-dimensional spectral calculus, followed once by the Duhamel formula
for the \(r\)-derivative, gives constants \(K_j\) such that, for \(j=0,1\),

\[
\begin{aligned}
 \|\partial_r^j(e^{A_rt}\Pi_r^s)\|
   &\le K_j(1+t)^j e^{-a_0t}
 &&(t\ge0),\\
 \|\partial_r^j(e^{A_rt}\Pi_r^u)\|
   &\le K_j(1+|t|)^j e^{a_0t}
 &&(t\le0).
\end{aligned}
\tag{16}
\]

For the unstable manifold, work on the fixed Banach space

\[
 X_{\eta_1}^-=\left\{Z\in C^0((-\infty,0],\mathbb R^4):
 \|Z\|_{\eta_1,-}:=
 \sup_{t\le0}e^{-\eta_1t}|Z(t)|<\infty\right\}.
\tag{17}
\]

Choose a smooth radial cutoff which is one on \(|Z|\le\delta\) and zero on
\(|Z|\ge2\delta\), and apply it to \(N_r\).  Denote the resulting
nonlinearity by \(\widetilde N_r\).  The cutoff is
\(\mathcal R\)-invariant, so the cutoff vector field remains reversible.
There is a uniform Lipschitz constant \(L_\delta\to0\) as
\(\delta\to0\), and

\[
 |\widetilde N_r(Z)-\widetilde N_r(\widetilde Z)|
 \le L_\delta|Z-\widetilde Z|.
\tag{18}
\]

For \(b\in E_0^u\), define

\[
\begin{aligned}
 (\mathcal T_{r,b}Z)(t)
 ={}&e^{A_rt}J_r^u b
 +\int_0^t e^{A_r(t-s)}\Pi_r^u
       \widetilde N_r(Z(s))\,ds\\
 &+\int_{-\infty}^t e^{A_r(t-s)}\Pi_r^s
       \widetilde N_r(Z(s))\,ds .
\end{aligned}
\tag{19}
\]

Let

\[
 D_0=(a_0-\eta_1)^{-1}+(a_0+\eta_1)^{-1},
 \qquad K=\max(K_0,1).
\]

Equations (16)--(19) give, on the closed radius-\(\delta\) ball of
\(X_{\eta_1}^-\),

\[
\begin{aligned}
 \|\mathcal T_{r,b}Z\|_{\eta_1,-}
 &\le K\|J_r^u\|\,|b|+KL_\delta D_0\delta,\\
 \|\mathcal T_{r,b}Z-\mathcal T_{r,b}\widetilde Z\|_{\eta_1,-}
 &\le KL_\delta D_0
 \|Z-\widetilde Z\|_{\eta_1,-}.
\end{aligned}
\tag{20}
\]

Choose \(\delta\) so that \(KL_\delta D_0\le1/2\), and then choose
\(b_*>0\) so that

\[
 K\sup_{|r|\le r_0}\|J_r^u\|\,b_*\le\delta/2.
\tag{21}
\]

Thus (19) maps the fixed closed ball into itself and is a uniform strict
contraction for every \(|b|\le b_*\) and \(|r|\le r_0\).  Its fixed point
is denoted by \(z^u(r,b)\).

The estimates (16), with the strict gaps in (14), show that (19) is a
\(C^1\) map of \((r,b,Z)\) into \(X_{\eta_1}^-\).  Indeed, the new factors
after differentiating in \(r\) are bounded by
\((1+|t-s|)e^{-a_0|t-s|}\), whose weighted integrals are finite because
\(a_0>\eta_1\); the term
\(\partial_r\widetilde N_r(Z)\) is uniformly \(O(|Z|^2)\) in the cutoff
ball.  The parameterized contraction theorem therefore gives

\[
 (r,b)\longmapsto z^u(r,b)\in X_{\eta_1}^-
 \quad\text{of class }C^1,
\tag{22}
\]

with uniform bounds for the orbit and its first \(r\)-derivative.  The
value

\[
 G^u(r,b):=z^u(r,b)(0)
\tag{23}
\]

parameterizes the local unstable manifold.  The Lyapunov--Perron
characterization also shows that the fixed point remains in
\(|Z|\le\delta\), where the cutoff vector field equals the original one.

The stable construction is the forward-time analogue.  Since the cutoff was
chosen reversible, uniqueness of the local invariant manifolds also gives

\[
 W^s_{\rm loc}(r)=\mathcal R W^u_{\rm loc}(r).
\tag{24}
\]

Finally, let a compact local patch and its base flowout over a bounded time
lie in a compact subset of the flow domain.  The common-flow-domain theorem
and smooth finite-time dependence of an ODE on its initial state and
parameter give the continued patch for all sufficiently small \(|r|\), with
the claimed \(C^1\) dependence.  This proves the lemma. \(\square\)

## 3. Reversible matching

Let \(\Gamma_0\) be the imported core orbit.  In the source coordinates,
the selected unstable source curve is \(S_0(\phi)=z_\rho(\phi)\), and its
matching map is

\[
 M_0(\phi,T)
 =(P,Q)\bigl(\Phi_0^T(S_0(\phi))\bigr).
\tag{25}
\]

The import gives a zero \((\phi_0,T_0)\) and

\[
 \det D_{(\phi,T)}M_0(\phi_0,T_0)
 \ge149.56393055300413.
\tag{26}
\]

Choose a compact interval \(I\) of source phases with \(\phi_0\) in its
interior.  The compact curve \(S_0(I)\) lies on the true unstable manifold
and converges to the origin under backward flow.  Hence one can choose a
single \(\tau>0\), after shrinking \(I\), so that

\[
 \widehat S_0(\phi):=\Phi_0^{-\tau}(S_0(\phi))
   =G^u(0,b_0(\phi)),
 \qquad |b_0(\phi)|<b_*,
\tag{27}
\]

for a \(C^1\) map \(b_0:I\to E_0^u\), with the image strictly inside the
Lyapunov--Perron parameter disk.  Define

\[
 \widehat S(r,\phi)=G^u(r,b_0(\phi)),\qquad
 S(r,\phi)=\Phi_r^\tau(\widehat S(r,\phi)).
\tag{28}
\]

Lemma 2.1 and compactness of the base flowout make (28) a \(C^1\) family of
embeddings after decreasing \(r_0\).  It satisfies exactly

\[
 S(r,\phi)\in W^u_r(0),\qquad S(0,\phi)=S_0(\phi).
\tag{29}
\]

Denote the flow of \(F_r\) by \(\Phi_r\).  Choose a compact interval
\(J\Subset(0,\infty)\) containing \(T_0\) in its interior.  By shrinking
\(I\) and \(J\), the base trajectories
\(\Phi_0^T(S_0(\phi))\), \((\phi,T)\in I\times J\), exist in a common
compact tube.  The common-flow-domain theorem gives the same conclusion for
all sufficiently small \(|r|\).  Thus

The map

\[
 M(r,\phi,T)
 =(P,Q)\bigl(\Phi_r^T(S(r,\phi))\bigr)
\tag{30}
\]

is \(C^1\) on a fixed neighborhood of
\((0,\phi_0,T_0)\).  Equations (26)--(30) and the
finite-dimensional implicit-function theorem give \(C^1\) functions
\(\phi(r)\), \(T(r)\), with

\[
 M(r,\phi(r),T(r))=0,\qquad
 \phi(0)=\phi_0,\quad T(0)=T_0.
\tag{31}
\]

After decreasing \(r_0\) once more, continuity and (26) give the uniform
matching bound

\[
 \left|\det D_{(\phi,T)}
 M(r,\phi(r),T(r))\right|\ge70
 \qquad (|r|\le r_0).
\tag{32}
\]

Put

\[
 c_r=\Phi_r^{T(r)}(S(r,\phi(r))).
\tag{33}
\]

Then \(c_r\in\operatorname{Fix}\mathcal R\).  The endpoint enclosures in
the import and continuity show, after another decrease of \(r_0\), that
\(c_r\ne0\).  Since \(c_r\in W^u_r(0)\),

\[
 \Phi_r^\xi(c_r)\longrightarrow0\quad\text{as }\xi\to-\infty.
\tag{34}
\]

The negative half-orbit in (34) exists for every \(\xi\le0\) by the
construction of \(W^u_r(0)\).  Define the positive half by reflection,
rather than presupposing forward global existence:

\[
 Z_r(\xi)=
 \begin{cases}
  \Phi_r^\xi(c_r),&\xi\le0,\\
  \mathcal R\Phi_r^{-\xi}(c_r),&\xi\ge0.
 \end{cases}
\tag{35}
\]

Because \(c_r\in\operatorname{Fix}\mathcal R\) and
\(D\mathcal R F_r=-F_r\circ\mathcal R\), the two pieces have the same value
and derivative at zero, and the reflected piece solves (1).  ODE uniqueness
then makes (35) a global solution; polynomial regularity bootstraps it to a
smooth solution.  It is nonconstant, symmetric, and homoclinic.  This step
uses no positive-parameter first integral.

It remains to verify the asserted Banach-space dependence without hiding a
moving time shift.  The local entry-to-center time
\(\sigma(r)=\tau+T(r)\) is bounded.  Choose a fixed
\(T_*>\sup_{|r|\le r_0}\sigma(r)\) sufficiently large that the uniform
negative-time estimate in (22), applied to the compact family
\(b_0(\phi(r))\), puts

\[
 a_r:=z^u\!\left(r,b_0(\phi(r))\right)
       \left(-(T_*-\sigma(r))\right)=Z_r(-T_*)
\]

strictly inside the graph parameter disk.  This formula, (22), and the ODE
equation show directly that \(r\mapsto a_r\) is \(C^1\); no
Banach-space regularity of the full orbit is being presupposed here.  More
explicitly, \(T_*\) is chosen so that

\[
 b_r:=(J_r^u)^{-1}\Pi_r^u a_r
 \quad\text{satisfies}\quad |b_r|<b_*
 \quad (|r|\le r_0).
\]

The maps in this formula are \(C^1\), and the Lyapunov--Perron formula at
time zero gives \(a_r=G^u(r,b_r)\).  Thus \(b_r\) is the fixed graph
coordinate of \(a_r\), and uniqueness gives

\[
 Z_r(\xi)=z^u(r,b_r)(\xi+T_*)
 \qquad(\xi\le-T_*).
\tag{36}
\]

Equation (22), the fixed shift in (36), and \(\eta<\eta_1\) imply

\[
 \sup_{|r|\le r_0}\sup_{\xi\le-T_*}
 e^{-\eta\xi}
 \bigl(|Z_r(\xi)|+|\partial_rZ_r(\xi)|\bigr)<\infty.
\tag{37}
\]

On \([-T_*,0]\), common finite-time flow dependence gives the same bound
after increasing the constant.  Reflection in (35) transfers it to the
positive half-line.  Gluing the two restrictions at the fixed point
\(-T_*\) is a bounded operation on the corresponding weighted spaces, so

\[
 r\longmapsto Z_r\in X_\eta\quad\text{is }C^1,
 \qquad
 \sup_{|r|\le r_0}\sup_{\xi\in\mathbb R}
 e^{\eta|\xi|}
 \bigl(|Z_r(\xi)|+|\partial_rZ_r(\xi)|\bigr)<\infty.
\tag{38}
\]

In particular, (4) holds and \(\|Z_r-Z_0\|_\eta\to0\).  This proves items
1 and 2 of Theorem B.

## 4. Return to the PDE and positivity

The change of variables derived in
[MODEL_AND_SCALING.md](MODEL_AND_SCALING.md) is exact.  Substitution of
(35) into (5) therefore gives a stationary solution of (6).
Equation (35) implies

\[
 U_r(-\xi)=U_r(\xi),\qquad V_r(-\xi)=V_r(\xi),
\tag{39}
\]

so \(u_d\) and \(v_d\) are even.  The uniform bound in \(X_\eta\) gives a
constant \(M\) such that

\[
 \sup_{0\le r\le r_0}
 \bigl(\|U_r\|_\infty+\|V_r\|_\infty\bigr)\le M.
\tag{40}
\]

Decrease \(r_0\) so that

\[
 r_0^2M<\frac12,\qquad r_0^4M<\frac12.
\tag{41}
\]

Then (5), (40), and (41) imply

\[
 u_d(x)\ge\frac12,\qquad v_d(x)\ge\frac12
\tag{42}
\]

for every \(x\in\mathbb R\) and \(0<r\le r_0\).  The exponential
convergence in (4) gives the limit in (7).  This proves item 3.

## 5. Amplitude and width

Convergence in \(X_\eta\) implies uniform convergence of each component.
The exact identities

\[
\begin{aligned}
 d^{-1/2}\|u_d-1\|_\infty&=\|U_r\|_\infty,\\
 d^{-1}\|v_d-1\|_\infty&=\|V_r\|_\infty
\end{aligned}
\tag{43}
\]

therefore give the limits in (8).  They are nonzero because the imported
symmetry endpoint satisfies

\[
 U_0(0)>4.8785,\qquad |V_0(0)|>7.9333.
\tag{44}
\]

Replacing \(\xi\) by \(x/r\) in (4), and using \(r=d^{1/4}\), gives (9).

It remains to verify the explicit width observable (10).  By (44) and
uniform convergence, there is \(m>0\) such that

\[
 |U_r(0)|\ge m,\qquad |V_r(0)|\ge m
\quad (0\le r\le r_0).
\tag{45}
\]

The \(X_\eta\) bound applied to \(P_r=U_r'\) and \(Q_r=V_r'\) gives a
uniform derivative bound \(M_1\ge1\).  Hence, for
\(\ell=m/(4M_1)\),

\[
 |U_r(\xi)|\ge\tfrac12|U_r(0)|,\qquad
 |V_r(\xi)|\ge\tfrac12|V_r(0)|
 \quad (|\xi|\le\ell),
\tag{46}
\]

after reducing \(m\), if necessary, to a common lower bound for the two
center values.

On the other hand, choose \(L>0\), independent of \(r\), so that
\(Ce^{-\eta L}<m/2\).  Equations (4) and (45) then show that the two
half-height inequalities fail for \(|\xi|\ge L\), whereas (46) shows that
both scaled half-height components contain \([-\ell,\ell]\).  Each such
component is therefore contained in \([-L,L]\) and has length between
\(2\ell\) and \(2L\).  Multiplication by \(r=d^{1/4}\) proves (11).
Items 4 and 5, and therefore Theorem B, follow. \(\square\)

## 6. Claim and dependency audit

The proof has four distinct evidence layers.

1. **Derived:** the PDE convention, exact scaling, polynomial family,
   reverser, divergence, spectrum, and inverse scaling are checked in
   [MODEL_AND_SCALING.md](MODEL_AND_SCALING.md).
2. **Imported:** existence, first-hit geometry, and the nonzero base matching
   determinant for one core orbit are computer-assisted at the frozen source
   and recorded in
   [CORE_HOMOCLINIC_IMPORT.md](CORE_HOMOCLINIC_IMPORT.md).
3. **Analytic proof in this repository:** Lemma 2.1, the matching
   implicit-function argument, reversible reflection, uniform tails,
   positivity, and the amplitude and width estimates.
4. **Absent and not claimed:** non-rigorous numerics, positive-parameter
   rigorous numerics, temporal stability, exact action, all-winding
   recurrence, and experimental validation.

The completed audit confirms:

- the published source equation numbers and the flagship commit and hashes;
- the identity of the \(r=0\) vector field, coordinate order, reverser, and
  clock;
- the interpretation of (26), using equation (9) of
  [CORE_HOMOCLINIC_IMPORT.md](CORE_HOMOCLINIC_IMPORT.md), as
  \(W^u_0(0)\pitchfork\operatorname{Fix}\mathcal R\);
- all uses of parameter-uniform constants in Lemma 2.1;
- the quantifier order
  \(\exists r_0,C,\eta,c,C_w\ \forall r\in(0,r_0]\ \forall x\in\mathbb R\);
  and
- preservation of the nonclaims in the research contract.

Accordingly B1 and B2 are Proved.  B3 is not a consequence of Theorem B and
remains Proposed.
