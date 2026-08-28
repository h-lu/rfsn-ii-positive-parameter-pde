# Paper A: nonlinear future-target / fold certificate prototype

This directory is an audit bundle for the future-tempered source curve of

\[
 U'=P,\qquad P'=-U^2-V,\qquad V'=Q,\qquad Q'=U,
\]

with reversible section `FixR = {P=Q=0}` and first integral

\[
 E=Q^2-P^2-\frac23U^3-2UV.
\]

This is the source-only validation package. Generated floating-point centres
are seeds only; every claim carrying evidentiary weight is re-enclosed by
FILIB/CAPD intervals. Executables are rebuild products and are not tracked.

## Claim contract

The bundle currently establishes the following statements.

1. **Exact algebra.** `build_prototype.py` constructs, over
   \(\mathbb Q(\sqrt2,\sqrt3)\), the unique degree-seven formal graph
   \(p=h_7(e,d,\omega)\) satisfying the compactified invariance equation
   through degree seven. The generated C++ header evaluates every coefficient
   with outward-rounded interval arithmetic; oversized integers are assembled
   exactly in base \(10^6\).

2. **Verified graph-transform budgets on the physical tail box.** On

   \[
   D_{\rm tail}=[0,0.06]\times[-0.001,0.001]\times[-0.01,0.02],
   \]

   `graph_transform_probe.cpp` verifies the vertical-exit, cone, one-rate and
   two-rate inequalities needed for

   \[
   |\eta|\le10^{-8},\qquad
   \|D\eta\|_2\le10^{-5},\qquad
   \|D^2\eta\|_2\le10^{-3}
   \]

   in the sheared base coordinates

   \[
   \bar y=(e,c,\omega),\qquad c=d-\frac{\sqrt3}{2}\omega.
   \]

3. **A graph-error-uniform interval fold.** At \(T=15\), with thirty
   length-\(1/2\) shooting intervals, `fold_interval_probe.cpp --robust`
   performs one 248-dimensional bordered Krawczyk test. The target value,
   target row and target Hessian are not frozen at \(h_7\): independent
   interval parameters covering all three graph budgets above are propagated
   through the Krawczyk residual and Jacobian. The test proves, for every
   \(C^2\) target graph satisfying those budgets, a unique regular augmented
   fold root in the reported shooting box. The source enclosure is

   \[
   \begin{aligned}
   U_0&\in[0.041527012176079285,\;0.041527012805834346],\\
   V_0&\in[0.10250373793858371,\;0.10250373825911163],\\
   E_0&\in[-0.008561090125517956,\;-0.008561089967620306].
   \end{aligned}
   \]

   Its endpoint is strictly inside the certified tail box:

   \[
   \begin{aligned}
   e_T&\in[0.057523936307391124,\;0.057523936765536819],\\
   d_T&\in[6.9951521641,\;7.1513233114]10^{-7},\\
   \omega_T&\in[0.0005514929754175,\;0.0005515106730686].
   \end{aligned}
   \]

4. **Verified physical forward confinement.** `weighted_corridor_probe.cpp`
   removes the artificial-completion ambiguity. With

   \[
   a=d/e^3,\qquad b=(\omega-e^2/6)/e^4,\qquad
   p=h_7+e^8\zeta,
   \]

   it verifies a forward-invariant physical base and an isolating normal strip

   \[
   \begin{gathered}
   0\le e\le0.06,\quad 0.001\le a\le0.0065,\quad |b|\le0.01,\\
   -0.012\le E\le-0.005,\qquad |\zeta|\le2.
   \end{gathered}
   \]

   Energy conservation excludes both \(a\)-faces, the \(b\)-faces are strictly
   inward, the \(\zeta\)-faces are strictly outward, and a cone inequality in
   \((e,-\sqrt3E/4,b;\zeta)\) gives a unique maximal forward-staying graph.
   On that graph \(e\downarrow0\), the compact variables tend to the algebraic
   end, and the original physical time tends to \(+\infty\).

5. **Physical fold conclusion.** The robust Krawczyk evaluation box was shrunk
   and revalidated. Its entire terminal target-evaluation range satisfies

   \[
   a\in[0.0032003730,0.0042315719],\qquad
   b\in[-0.0087469688,0.0089804775],
   \]

   and, for every \(|\zeta|\le2\),

   \[
   E_{\rm graph}\in[-0.0107970901,-0.0063250927].
   \]

   It is therefore strictly contained in the verified physical corridor. The
   weighted graph supplies existence and confinement; the unweighted cone/rate
   bounds supply the \(C^1/C^2\) target budgets used by the Krawczyk test.
   Hence the fold in item 3 is a fold of the canonical physical future target,
   not of an arbitrary completed graph.

6. **Signed-energy physical graph, including the exact algebraic orbit.**
   `signed_corridor_probe.cpp` enlarges the physical construction to

   \[
   0\le e\le0.06,\quad |a|\le0.0065,\quad |b|\le0.01,
   \quad |E|\le0.012,\quad |\zeta|\le2.
   \]

   This nondegenerate action slab includes \(E=0\). The generator constructs
   the exact polynomial

   \[
   \zeta_{\rm alg}(e)=
   \frac{-e/\sqrt3-h_7(e,0,e^2/6)}{e^8}
   \]

   and checks its energy and tangency identities symbolically. Interval
   evaluation places it strictly inside the normal strip. Positive
   one-through-four rate gaps give a unique \(C^4\) maximal physical
   future-staying graph on the whole signed-energy slab.

7. **Ambient target coverage for the current heteroclinic BVP.**
   `terminal_physical_contract_probe.cpp` checks the entire terminal node box
   used for target evaluation, not only the final root enclosure. It lies in
   the signed corridor and its full \(|\zeta|\le2\) graph-energy range is

   \[
   [-0.001850408298773085,\;0.0018504082847746351].
   \]

   The weighted \(C^4\) graph is the physical existence/confinement theorem;
   its reparameterization in the unweighted chart is the same physical target
   and inherits the explicit \(C^0/C^1/C^2\) budgets in item 2. These are not
   two competing target hypersurfaces.

This package does not by itself determine the complete connected FixR source
component, its endpoints, or an intersection with \(W^u(0)\). In particular,
the source-to-target orbit belongs to a separate heteroclinic Krawczyk
certificate; the present package supplies its canonical physical target.

## Compactified equations

For \(U<0\), put

\[
 e=(-U)^{-1},\quad p=Pe^{3/2},\quad q=Qe^{3/2},\quad
 \omega=1+Ve^2,\quad d=q+\frac2{\sqrt3}.
\]

In desingularized future time,

\[
 \begin{aligned}
 e'&=ep,\\
 d'&=\frac32p\left(d-\frac2{\sqrt3}\right)-e,\\
 \omega'&=e\left(d-\frac2{\sqrt3}\right)+2p(\omega-1),\\
 p'&=\frac32p^2-\omega.
 \end{aligned}
\]

Write \(p=h_7(e,d,\omega)+\xi\), \(q=d-2/\sqrt3\). The transformed system
is exactly

\[
 y'=F_0(y)+B(y)\xi,
 \qquad
 \xi'=R(y)+A(y)\xi+\frac32\xi^2,
\]

where

\[
 B=(e,\tfrac32q,2(\omega-1))^T,
\]

\[
 R=\frac32h_7^2-\omega
   -Dh_7\!\cdot\!\left(eh_7,\frac32h_7q-e,
                         eq+2h_7(\omega-1)\right),
\]

\[
 A=3h_7-eh_{7,e}-\frac32q h_{7,d}
   -2(\omega-1)h_{7,\omega}.
\]

These identities, rather than a linear Jost row, define the nonlinear target
error used by the certificate.

## Quantitative graph theorem used by the contract

Let \(M\) be a compact boundaryless three-dimensional base (a fixed smooth
completion of the physical base), and consider a complete \(C^3\) field on
\(M\times[-\rho,\rho]\) that agrees with the compactified field on a padded
physical tail region. In \((\bar y,\xi)\) coordinates write

\[
 D(F,G)=\begin{pmatrix}C&B\\D&a\end{pmatrix}.
\]

Assume throughout the completed tube that

\[
 \mu_2(C)\le c_*,\qquad \|B\|\le b_*,\qquad
 \|D\|\le d_*,\qquad a\ge a_*,
\]

and that the vertical faces point strictly outward:

\[
 \sup_MG(\bar y,-\rho)<0<\inf_MG(\bar y,\rho).
\]

If some \(\alpha>0\) satisfies

\[
 \kappa=\alpha(a_*-c_*)-d_*-b_*\alpha^2>0,
 \qquad \lambda_u=a_*-d_*/\alpha>0,
\]

\[
 \beta_1=a_*-c_*-2b_*\alpha>0,
 \qquad
 \beta_2=a_*-2c_*-3b_*\alpha>0,
\]

then the maximal forward-staying set in the completed tube is the graph of a
unique \(C^2\) function \(\xi=\gamma(\bar y)\), with

\[
 \|\gamma\|_\infty<\rho,
 \qquad \|D\gamma\|_\infty\le\alpha.
\]

For \(s=D\gamma\), \(E_su=(u,su)\), define

\[
 K_s=(D^2G-sD^2F)[E_s\,\cdot,E_s\,\cdot],
 \qquad
 K_0=\sup_{\|s\|\le\alpha}\|K_s\|.
\]

Then

\[
 \|D^2\gamma\|_\infty\le K_0/\beta_2.
\]

For the affine-in-\(\xi\) field in this bundle, the program bounds \(K_0\) by

\[
 \begin{aligned}
 K_0\le{}&\|R_{\bar y\bar y}\|
 +\rho\|A_{\bar y\bar y}\|+2\alpha\|A_{\bar y}\|+3\alpha^2\\
 &+\alpha\bigl(\|(F_0)_{\bar y\bar y}\|
 +\rho\|B_{\bar y\bar y}\|+2\alpha\|B_{\bar y}\|\bigr),
 \end{aligned}
\]

with \(B_{\bar y\bar y}=0\) exactly.

### Proof sketch with quantitative constants

For a variational difference \((u,v)\), on the vertical cone boundary
\(|v|=\alpha|u|\), logarithmic-norm estimates give

\[
 D^-|v|\ge a_*|v|-d_*|u|,
 \qquad
 D^+|u|\le c_*|u|+b_*|v|.
\]

Therefore

\[
 D^-\bigl(|v|-\alpha|u|\bigr)\ge\kappa|u|>0.
\]

The vertical cone is strictly forward invariant, and inside it
\(D^-|v|\ge\lambda_u|v|\). Flow the zero section backward for time \(T\).
The two vertical faces are inward for reversed time. The cone condition makes
the base projection a degree-one local diffeomorphism, hence each backward
image is a graph \(\gamma_T\) with Lipschitz constant at most \(\alpha\).
Compactness and Arzela--Ascoli give a limiting forward-staying graph. Two
forward-staying points in one fiber would have a vertical separation growing
at least as \(e^{\lambda_ut}\), contradicting the width \(2\rho\); this proves
uniqueness and convergence of the whole family.

Along the graph let \(L=C+Bs\), \(n=a-sB\). Then

\[
 \mu_2(L)\le c_*+b_*\alpha,
 \qquad n\ge a_*-b_*\alpha.
\]

The first derivative graph transform contracts with gap \(\beta_1\). For
\(H=D^2\gamma\) and the base variational equation \(\Psi'=L\Psi\), the tensor
graph transform has normal-versus-two-base gap

\[
 n-2\mu_2(L)\ge\beta_2.
\]

Variation of constants yields

\[
 \|H\|\le K_0\int_0^\infty e^{-\beta_2t}\,dt=K_0/\beta_2.
\]

This proves the theorem. Its compact-completion hypothesis is essential; two
vertical face inequalities on a box with lateral escape do not imply existence
of a graph over every base point.

## Weighted physical-corridor theorem

The physical certificate avoids that hypothesis. Substitute

\[
 d=e^3a,\qquad \omega=e^2/6+e^4b,\qquad \xi=e^8\zeta
\]

in the exact compactified equations. `build_prototype.py` cancels all apparent
negative powers of \(e\) symbolically and generates a polynomial field

\[
 (e,a,b,\zeta)'=\mathcal F(e,a,b,\zeta)
\]

that is regular at \(e=0\). The normal equation is

\[
 \zeta'=e^{-8}R+A\zeta+\frac32e^8\zeta^2-8p\zeta.
\]

The last term is \(-8p\zeta\), not \(-8(p/e)\zeta\). The generator verifies
symbolically, before writing C++, that

\[
 D\mathcal E\cdot\mathcal F\equiv0,
\qquad
\mathcal E=e^{-3}(q^2-p^2+2\omega-4/3).
\]

FILIB proves that \(\partial_a\mathcal E<0\) on the corridor and that

\[
 \begin{aligned}
 \mathcal E(e,0.001,b,\zeta)
   &\subset[-0.003536946,-0.001078110],\\
 \mathcal E(e,0.0065,b,\zeta)
   &\subset[-0.016229569,-0.013768759].
 \end{aligned}
\]

Thus, for every

\[
 (e,E,b,\zeta)\in[0,.06]\times[-.012,-.005]
                    \times[-.01,.01]\times[-2,2],
\]

the energy equation has a unique solution \(a\in(.001,.0065)\). It defines a
regular coordinate change from \((e,a,b,\zeta)\) to

\[
 x=(e,\mathcal A,b,\zeta),\qquad \mathcal A=-\sqrt3E/4.
\]

In this coordinate the base is compact and forward invariant: \(E'=0\), the
two \(b\)-faces are inward, \(e'=0\) at \(e=0\), and \(e'<0\) at \(e=.06\).
The two \(\zeta\)-faces are strictly outward. For each fixed initial base point,
the initial \(\zeta\)-interval has an open lower-exit set and an open upper-exit
set. Connectedness leaves at least one initial value whose orbit never exits.

For two staying orbits, the verified vertical-cone inequality gives strict
forward invariance and normal growth. Two distinct staying values over one
base point would therefore separate beyond the width of the strip, a
contradiction. Hence the maximal physical forward-staying set is one graph

\[
 \zeta=\Gamma(e,\mathcal A,b),\qquad |\Gamma|<2.
\]

No vector-field extension is used in this argument. The old
\((e,c,\omega;\xi)\) cone and rate inequalities apply along this physical
graph. Because the verified interval for \(\partial_a\mathcal E\) excludes
zero, the ambient change

\[
 (e,a,b,\zeta)\longleftrightarrow(e,-\sqrt3E/4,b,\zeta)
\]

is a \(C^2\) local diffeomorphism throughout the terminal evaluation
neighborhood. The unweighted vertical cone rules out a kernel in the
projection of the staying manifold to \((e,c,\omega)\). Hence the physical
weighted graph reparameterizes there as the unweighted graph
\(\xi=\eta(e,c,\omega)\), and the unweighted rate estimates give exactly the
value/row/Hessian budgets used by the robust fold test.

The fold program additionally evaluates the *whole* terminal Krawczyk box,
not only its final root enclosure. For every base point in that box and every
\(|\zeta|\le2\), the graph energy remains in \([-0.012,-0.005]\). Thus each
unweighted vertical fiber used by the target residual lies inside the weighted
action block. The same two-exit/connectedness argument gives a staying point
on every such fiber, and the unweighted vertical cone makes it unique. This is
the precise coverage statement needed for the interval Jacobian evaluation.

Finally the weighted certificate bounds

\[
 -K\le p/e\le-k<0
\]

with positive \(k,K\). Hence

\[
 -Ke^2\le e'\le-ke^2,
\]

so \(e\asymp\tau^{-1}\) in compact time and \(e\to0\). Since
\(dt/d\tau=\sqrt e\),

\[
 \int_0^\infty\sqrt{e(\tau)}\,d\tau=\infty;
\]

the endpoint is at physical time \(t=+\infty\), not a finite-time pole. The
regular weighted formulas also give \(p/e\to-1/\sqrt3\), and therefore

\[
 U\sim-t^2/12,\qquad P\sim-t/6,\qquad
 V\sim-t^4/144,\qquad Q\sim-t^3/36.
\]

## Signed-energy and zero-energy extension

The negative-energy corridor above is retained because it is the smallest
block used by the first-fold proof. The same exact weighted field also admits
a single symmetric physical corridor containing that fold and the
zero-energy algebraic end:

\[
 \mathcal C_0=\{0\le e\le.06,\ |a|\le.0065,\ |b|\le.01,
                  \ |E|\le.012,\ |\zeta|\le2\}.
\]

The generator now verifies the exact algebraic reference

\[
 a=b=0,\qquad p=-e/\sqrt3,\qquad E=0,
\]

including the identity

\[
 \zeta_{\rm alg}(e)
 =\frac{-e/\sqrt3-h_7(e,0,e^2/6)}{e^8}
\]

as a polynomial and its exact tangency to the weighted field. FILIB gives

\[
 \zeta_{\rm alg}([0,.06])
 \subset[-1.0314380350086394,-1.0083599083642838]\subset(-2,2).
\]

On \(\mathcal C_0\), the action coordinate is regular because

\[
 \partial_aE\in[-2.3094011373136727,-2.3073894635767043].
\]

The two \(a\)-faces strictly bracket the full signed energy slab:

\[
 \begin{aligned}
 E(e,-.0065,b,\zeta)
  &\subset[.0137688621606626,.0162296710663035],\\
 E(e, .0065,b,\zeta)
  &\subset[-.0162295683074354,-.0137687595003354].
 \end{aligned}
\]

The remaining physical face and cone data are

```
p/e                         in [-0.57735248064508804,-0.57734805337315032]
b_dot at b=-0.01            >=  0.012815359139113863
b_dot at b= 0.01            <= -0.012859991059044963
zeta_dot at zeta=-2         <= -1.3523766005713447
zeta_dot at zeta= 2         >=  4.2870367289074984
mu_2(C)                     <= 0.022876876257191
||B||                       <= 2.591943887076e-5
||D||                       <= 11.269134128863
normal expansion            >= 1.4142085902521
cone margin                 >= 2.6415910672
vertical growth             >= 0.2872951773659
```

For weighted graph slope \(\alpha=10\), the verified rate gaps

\[
 \gamma_r=n-r\mu_2(C)-(r+1)\|B\|\alpha,
 \qquad r=1,2,3,4,
\]

are

\[
 (1.3908133252175,1.3676772545716,
   1.3445411839257,1.3214051132798).
\]

The two-exit connectedness argument gives a staying point over every physical
base point; the cone gives uniqueness; and the four positive rate gaps give
\(C^4\) regularity. No boundaryless completion is used. The exact algebraic
reference stays in the corridor, so uniqueness places it on this graph.

For enlarged terminal interval boxes, the program also checks the padded
corridor

\[
 |a|\le.012,\qquad |b|\le.06,
\]

with the same \(e,E,\zeta\) ranges. It has cone margin
\(2.3419437033441239\), vertical growth
\(0.28709509966616387\), and rate gaps

\[
 (1.3610486662045735,1.3081479368728217,
   1.2552472075410701,1.2023464782093183).
\]

Even this padded block is strictly inside the unweighted tube:

\[
 \begin{aligned}
 |d|&\le2.5920000000000016\,10^{-6},\\
 \omega&\in[-7.776000000000005\,10^{-7},
              6.0077760000000024\,10^{-4}],\\
 |\xi|&\le3.3592320000000047\,10^{-10}.
 \end{aligned}
\]

This explains the relation between the two graph calculations. The weighted
construction proves that the physical maximal-staying hypersurface exists and
is unique. Because \(\partial_aE\ne0\) and the unweighted vertical cone rules
out a kernel in the projection, that same hypersurface reparameterizes as
\(\xi=\eta(e,c,\omega)\). The unweighted calculation then gives the explicit
target budgets

\[
 \|\eta\|_\infty\le10^{-8},\qquad
 \|D\eta\|_2\le10^{-5},\qquad
 \|D^2\eta\|_2\le10^{-3},
\]

with the sharper computed Hessian bound
\(8.7380424946040209\,10^{-5}\). Thus the old \(h_7+\eta\) target and the
weighted \(C^4\) graph are two charts and two estimates for the same physical
object.

Finally, the complete terminal evaluation box supplied with the current
origin-heteroclinic BVP satisfies

\[
 \begin{aligned}
 e&\in[.057499998340262551,.057500001659737551],\\
 a&\in[-.00040856190871630305,.00040780247295930716],\\
 b&\in[-.0077092414472739561,.0076936304274827332],\\
 E_{|\zeta|\le2}
  &\in[-.001850408298773085,.0018504082847746351].
 \end{aligned}
\]

Hence every ambient target value and derivative evaluation in that box is
inside the signed physical corridor. This is a target-coverage statement; the
heteroclinic root itself is certified in a separate validation package.

## What the interval programs check

`graph_transform_probe.cpp` uses second-order automatic differentiation on
FILIB intervals. It tiles the decimal tail box into \(24\times8\times24\)
overlapping outward-rounded cells. On each cell it differentiates with respect
to \((e,c,\omega)\), applies a symmetric-part Gershgorin bound for
\(\mu_2(C)\), and uses Frobenius bounds for vectors, matrices and third-order
tensors. The expected certificate includes

```
defect_bound                 <= 1.15102025394e-9
normal_expansion_lower       >= 1.36032138086
base_log_norm_upper          <= 0.05635722239
B_norm_upper                 <= 2.02097852822
D_norm_upper                 <= 2.64739246330e-7
vertical_exit_margin         >= 1.24521934046e-8
cone_margin                  >= 1.27747002406e-5
C2_gap                       >= 1.24754630674
C2_bound_required            <= 8.73804249461e-5
```

`weighted_corridor_probe.cpp` evaluates the regular weighted field and the
implicit action-coordinate Jacobian on a
\(12\times3\times8\times4\) outward-rounded subdivision. Its expected
certificate includes

```
energy at a=0.001       subset [-0.003536946,-0.001078110]
energy at a=0.0065      subset [-0.016229569,-0.013768759]
energy_da               subset [-2.309402,-2.307389]
p_over_e                 subset approximately [-0.577352,-0.577348]
b lower face             >=  0.0131573
b upper face             <= -0.0128654
zeta lower face          <= -1.35238
zeta upper face          >=  4.28704
weighted cone margin     >=  2.64385
weighted vertical growth >=  0.287521
```

`signed_corridor_probe.cpp` uses the same generated exact field on a
\(12\times4\times8\times4\) outward-rounded subdivision. Its first invocation
checks the main signed block; its second checks the padded block. In addition
to the face and cone tests, it evaluates the exact algebraic reference,
verifies one-through-four rate gaps, and checks that the whole weighted block
lies inside the unweighted \(D_{\rm tail}\) and \(|\xi|\le10^{-8}\) budgets.

`terminal_physical_contract_probe.cpp` maps the complete terminal BVP node box
to \((e,a,b)\), then evaluates the graph energy for the full interval
\(|\zeta|\le2\). Passing means that ambient value/row/Hessian target
evaluations are covered by the physical signed action slab.

`fold_interval_probe.cpp` integrates the 8-dimensional extended system
\((z,w)'=(f(z),Df(z)w)\). The left boundary conditions are

\[
 P_0=Q_0=0,\qquad w_{U,0}=1,\quad w_{P,0}=w_{Q,0}=0.
\]

At \(T=15\), with

\[
 g_\eta(z_T)=p_T-h_7(e_T,d_T,\omega_T)
              -\eta(e_T,c_T,\omega_T),
\]

it imposes

\[
 g_\eta(z_T)=0,\qquad Dg_\eta(z_T)w_T=0,
 \qquad dE(z_0)w_0=0.
\]

The derivative of the tangent target contains the full Hessian

\[
 D^2(g_7-\eta\circ y)
 =D^2g_7-Dy^T(D^2\eta)Dy-\sum_a(D_a\eta)D^2y_a.
\]

Every entry of \(\eta,D\eta,D^2\eta\) is intervalized independently. This is
an over-enclosure of the admissible graph family, so a successful Krawczyk
test is uniform in the true correlated jets. The robust run reports

```
newton_ratio       = 0.267540491489
contraction_ratio  = 0.0520905148751
```

The second number bounds the weighted interval remainder
\((I-CDF(X))(X-x_*)\). Its strict inequality below one proves uniform
nonsingularity of the bordered derivative; the enclosed energy critical point
is therefore a simple fold for every admissible target graph.

## Reproduction pins

The audit was run with:

```
CAPD repository       https://github.com/CAPDGroup/CAPD.git
CAPD commit           731079217a9254ea2948d742df2b170895effe7f
pkg-config version    2.5.1
interval backend      FILIB
CMake cache version   4.2.3
compiler              g++ (Ubuntu 15.2.0-16ubuntu1) 15.2.0
Python                3.14.4
NumPy                 2.5.2
SciPy                 1.18.0
SymPy                 1.14.0
```

CAPD was configured in Release mode with tests/examples/multiprecision off and
`CAPD_INTERVAL_TYPE=FILIB`. The exact CMake invocation should be recorded when
the temporary build is promoted; the current cache records those options.

With the existing temporary build, reproduce from this directory via

```bash
PAPERA_CAPD_CONFIG=/tmp/papera-capd.bKwHIQ/CAPD/build/bin/capd-config

python3 build_prototype.py

g++ graph_transform_probe.cpp \
  $("$PAPERA_CAPD_CONFIG" --cflags) \
  $("$PAPERA_CAPD_CONFIG" --libs) \
  -O2 -std=c++17 -o graph_transform_probe
./graph_transform_probe

g++ weighted_corridor_probe.cpp \
  $("$PAPERA_CAPD_CONFIG" --cflags) \
  $("$PAPERA_CAPD_CONFIG" --libs) \
  -O0 -std=c++17 -o weighted_corridor_probe
./weighted_corridor_probe

g++ signed_corridor_probe.cpp \
  $("$PAPERA_CAPD_CONFIG" --cflags) \
  $("$PAPERA_CAPD_CONFIG" --libs) \
  -O0 -std=c++17 -o signed_corridor_probe
./signed_corridor_probe 0.0065 0.012 0.01 2 0.06
./signed_corridor_probe 0.012 0.012 0.06 2 0.06

g++ terminal_physical_contract_probe.cpp \
  $("$PAPERA_CAPD_CONFIG" --cflags) \
  $("$PAPERA_CAPD_CONFIG" --libs) \
  -O0 -std=c++17 -o terminal_physical_contract_probe
./terminal_physical_contract_probe

g++ fold_interval_probe.cpp \
  $("$PAPERA_CAPD_CONFIG" --cflags) \
  $("$PAPERA_CAPD_CONFIG" --libs) \
  -O2 -std=c++17 -o fold_interval_probe
./fold_interval_probe
./fold_interval_probe --robust
```

`build_prototype.py` must run before compilation because it regenerates
`tail_graph_generated.hpp`, `weighted_tail_generated.hpp`, and the \(T=15\),
30-segment shooting centres. It also rechecks exact energy conservation and
all algebraic-reference tangency identities. Use `--tails-only` when only the
two exact tail headers are required. `-O0` keeps compilation of the large exact
weighted polynomial header short; it does not change directed-rounding
semantics.
The SciPy solve is deterministic on the pinned stack but is not trusted as a
proof step.

The current static libraries have SHA256 hashes

```
libcapd.a   316b2c480f1ce36b293602da9978eb43560646991a4a906d72ee893b3c557119
libfilib.a  ce5cdf8f22d4a6737461774211053a3df360178194e431e4f7ad2b2ada5caa7e
```

The final source/generated-file hash manifest appears at the end of this file
after the last audit run. Executables are intentionally excluded: binaries
must be rebuilt locally and must not be committed or archived as evidence.

## Promotion checklist

- [x] exact degree-seven jet and generated interval evaluator;
- [x] outward-rounded tail-block exit/cone/rate/C2 inequalities;
- [x] target value, row and Hessian error propagation;
- [x] enlarged anisotropic 248-dimensional Krawczyk box;
- [x] uniform bordered nonsingularity/simple-fold check;
- [x] endpoint strictly inside \(D_{\rm tail}\);
- [x] exact regular weighted system and symbolic energy-conservation identity;
- [x] physical action corridor with inward base faces and outward normal faces;
- [x] weighted cone uniqueness and infinite physical-time confinement;
- [x] entire robust target-evaluation box inside the weighted corridor;
- [x] signed \(|E|\le0.012\) physical corridor containing \(E=0\);
- [x] exact algebraic-reference polynomial and tangency identities;
- [x] weighted one-through-four rate gaps and \(C^4\) regularity;
- [x] padded signed corridor and complete heteroclinic terminal-box coverage;
- [ ] continue the complete FixR source component and certify its endpoint
      alternatives (a separate global theorem);
- [ ] combine with the separate \(W^u(0)\)-to-target Krawczyk package; no
      heteroclinic root claim is part of this target/fold certificate.

## Source hash manifest

These are the final claim-bearing source/generated artifacts. Generated
executables are deliberately absent.

```
3423a66fb26488fb88d88adcbf87d10a5b71296bc8e9859d4506dc1cd014caf0  build_prototype.py
f9f9070c748c684533b779b921f524069c2dac5238e0872bb6f8a1f87552f0b8  tail_graph_generated.hpp
b3f286def464dde6fb5f9641ca74b1cb6d50ef4d571e4e148233e4c5cf56e9d5  weighted_tail_generated.hpp
b7dc18823832dbc5ab6869aecc91abdde2c74a4f66fc8eff08e545e2d6fedec3  fold_centres_generated.hpp
7b5460846d296b905852f68f3c05b1c5adedcc507a163bfbed9f05a7340864d2  graph_transform_probe.cpp
6f335006e4d3ebe2d28ae31ed30a9c06577f013d0eedc6861efd4c675a218e59  weighted_corridor_probe.cpp
42b67431dc70023a469012799e81969da747d85e7bb06a49632bc0aa6b6a2732  signed_corridor_probe.cpp
ec742fb46763f29703157bee7d19dac60d161c2227e09cf5b3bcb1da41977c1d  heteroclinic_centres.hpp
73c3dddc9e82074862351e2d504cb4610723cdfcbad8ceabbdec5e83f869639b  terminal_physical_contract_probe.cpp
c34d26ea85f0c7b6611939569a0a911ff3c2013583fa5ce7f24f18d6b1132319  fold_interval_probe.cpp
f95bea4b8efed4e11d03ce185ca62522e8febcbafc0af73762ee33eaefd4bfab  certificate.json
```
