# Paper A origin-to-algebraic heteroclinic certificate

This source-only bundle validates one transverse, zero-energy orbit from the
origin unstable manifold to the canonical algebraic future target for

\[
 U'=P,\qquad P'=-U^2-V,\qquad V'=Q,\qquad Q'=U,
\]

with first integral

\[
 \mathcal E=Q^2-P^2-\frac23U^3-2UV.
\]

All claim-bearing numerical operations use outward-rounded FILIB/CAPD
intervals. Floating-point shooting centres are seeds only. The final
conclusion is local: the certified box contains one orbit modulo time
translation, and that intersection is transverse. This bundle makes **no**
all-phase pole-cover claim, no claim about the full connected source
component, and no global classification or global uniqueness claim.

## Certified statement

Let `Wfuture_loc` be the canonical maximal forward-staying graph in the
signed weighted corridor described below, and let `Wfuture` denote the
regular branch of its finite backward-flow saturation. There is an orbit in

\[
 W^u(0)\cap W_{\rm future}\cap\{\mathcal E=0\}.
\]

It is locally unique up to time translation and the invariant manifolds meet
transversely modulo their common flow direction. Its source phase and the two
reported endpoint boxes are contained in `certificate.json`. In particular,

```text
phase in [5.7566913947049203, 5.7566913967948983]
source U in [0.0086517807045863506, 0.0086517807245419503]
terminal e in [0.057499999788182196, 0.057500000211817802]
Krawczyk inclusion ratio <= 0.18217055712874344
```

The interval energy evaluations are deliberately correlation-blind and hence
nonzero-width. The exact orbit energy is nevertheless exactly zero: every
point of `W^u(0)` has the conserved value of the equilibrium, namely zero.

## 1. The true local unstable graph

Put `c=1/sqrt(2)` and use the exact linear coordinates

\[
\begin{aligned}
 U&=u_1+s_1,&V&=u_2+s_2,\\
 P&=c(u_1-s_1-u_2+s_2),&
 Q&=c(u_1-s_1+u_2-s_2).
\end{aligned}
\]

The symmetric parts of the unstable and stable linear blocks are `c I` and
`-c I`. Both nonlinear blocks have the exact Euclidean norm

\[
 \|N_u\|_2=\|N_s\|_2=\frac12|u_1+s_1|^2.
\]

On the block `||u||<=0.01`, `||s||<=0.01`, the unstable boundary is outward
and the stable boundary is inward:

\[
 D^-\|u\|\ge(c-.02)\|u\|>.68\|u\|,
 \qquad
 D^+\|s\|\le-(c-.02)\|s\|<0.
\]

The first inequality is asserted on the face `||u||=.01` and the second on
the face `||s||=.01`. They are not a homogeneous stable estimate at `s=0`.
Inside the block one keeps the exact quadratic forcing:

\[
 D^+\|s\|\le-c\|s\|+\frac12(\|u\|+\|s\|)^2.
\]

On the boundary `||delta s||=||delta u||`, the difference cone has the strict
margin `2(c-.04)>1.33`. The isolating-block graph transform therefore gives
one local `W^u` graph with Lipschitz constant at most one. This conclusion is
obtained before using a quadratic bootstrap, so there is no circular
assumption `||s||<=||u||^2`.

The coarse graph yields `||s||<=||u||`. Variation of constants and the radial
rate `.68`, including the nonhomogeneous forcing displayed above, then give

\[
 \|s\|\le \frac{2}{c+1.36}\|u\|^2<\|u\|^2.
\]

Using this improved estimate gives the radial rate `.69` and then

\[
 \|s\|\le
 \frac{\tfrac12(1.01)^2}{c+1.38}\|u\|^2
 <\frac14\|u\|^2.
\]

Thus the full fundamental source circle `||u||=0.01` lies in the coarse
stable disk `||s||<2.5e-5`.

`generate_polynomial_header.py` independently performs the exact degree-ten
homological recursion over `Q(sqrt(2))`. Let `H10` be the generated polynomial
and put `w=s-H10(u)`. Analyticity of the true unstable manifold and uniqueness
of every homological solve imply `w=o(||u||^10)` and
`Dw=o(||u||^9)` at the origin. `unstable_graph_probe.cpp` then proves on the
whole disk `||u||<=.01`:

```text
||H10||                         <= 3.2961536609720836e-05
||DH10||_F                      <= 0.0052379054813578886
||D2H10||_F                     <= 0.42657343764993072
invariance defect              <= 2.2689612291787061e-24
normal contraction             >= 0.69704094506851677
inward residual-sphere margin  >= 6.9681404894559853e-21
unstable exit margin           >= 7.0209338528236264e-05
difference-cone margin         >= 1.3840685031933619
small C1 cone margin           >= 1.3819130787158866e-18
```

The exact residual equation has an inward vector field on the Euclidean
sphere `||w||_2=1e-20`. Since the true graph starts inside that tube near the
origin, a first exit before `||u||=.01` is impossible. The small derivative
cone gives the same no-first-exit argument for `Dw`. Consequently

\[
 \|H-H_{10}\|_2\le10^{-20},\qquad
 \|D(H-H_{10})\|_{2\to2}\le10^{-18}.
\]

The robust shooting code encloses the Euclidean residual ball by the
component square `[-1e-20,1e-20]^2`. This is a conservative containment; no
missing `sqrt(2)` factor is used.

## 2. The physical signed-energy future graph

For `U<0`, set

\[
 e=-U^{-1},\quad p=Pe^{3/2},\quad q=Qe^{3/2},\quad
 d=q+2/\sqrt3,\quad\omega=1+Ve^2.
\]

The canonical sibling bundle `../future-target-fold` constructs the exact
degree-seven formal graph `p=h7(e,d,omega)`. Its
`graph_transform_probe.cpp` verifies on

\[
 0\le e\le.06,\quad |d|\le.001,\quad -.01\le\omega\le.02
\]

that the true graph error `xi=p-h7` satisfies the uniform budgets

\[
 |\xi|\le10^{-8},\qquad \|D\xi\|_2\le10^{-5},
 \qquad\|D^2\xi\|_2\le10^{-3}.
\]

Existence is tied to the physical flow, rather than to an arbitrary compact
completion, by the regular weighted variables

\[
 a=d/e^3,\qquad b=(\omega-e^2/6)/e^4,\qquad \xi=e^8\zeta.
\]

Its `signed_corridor_probe.cpp` proves a maximal forward-staying graph on

\[
 0\le e\le.06,\quad |a|\le.0065,\quad |b|\le.01,
 \quad |\mathcal E|\le.012,\quad |\zeta|\le2.
\]

The strict face and cone data include

```text
energy at a=-.0065       in [ .013768862160662696, .016229671066303420]
energy at a= .0065       in [-.016229568307435376,-.013768759500335470]
dE/da                    <= -2.3073894635767043
b lower/upper margins    >= .012815359139113863 / <= -.012859991059044963
zeta lower/upper margins <= -1.3523766005713447 / >= 4.2870367289074980
weighted cone margin     >= 2.6415910672006830
```

Energy monotonicity makes `(e,A,b,zeta)`, `A=-sqrt(3) E/4`, a regular
coordinate system. Energy conservation excludes the two `a` faces, the `b`
faces are inward, and the `zeta` faces are outward. Connectedness plus the
strict vertical cone gives one and only one staying value in each fiber.

The graph is qualitatively `C4`, not merely `C2`. If `alpha=10`, the verified
normal-versus-`r`-base graph-transform gaps are

\[
 a_*-r\mu_2(C)-(r+1)\|B\|\alpha,
\]

and their lower bounds for `r=1,2,3,4` are respectively

```text
1.3908133252175652
1.3676772545716670
1.3445411839257686
1.3214051132798703
```

The weighted field is polynomial on the compact block, so all forcing
derivatives required by the `C4` graph transform are bounded. The strict
four-rate gap therefore yields a `C4` physical graph. The nonzero energy
Jacobian and the unweighted cone reparameterize it locally as the `C4` graph
`xi=eta(e,cbar,omega)`, `cbar=d-sqrt(3)omega/2`; the quantitative unweighted
probe supplies the smaller `C0/C1/C2` budgets actually used in shooting.

The terminal-contract block inside `heteroclinic_interval_probe.cpp` evaluates
the **entire terminal Krawczyk box**, not just the root image. It proves

```text
e              in [.057499998340262551,.057500001659737551]
a              in [-.00040856190871630305,.00040780247295930716]
b              in [-.0077092414472739561,.0076936304274827332]
graph energy   in [-.001850408298773085,.0018504082847746351]
               for every |zeta|<=2
```

Hence every target value and derivative evaluated by the shooting proof lies
in the signed physical corridor. This is the contract that identifies the
abstract unweighted graph with the canonical physical future target at and
around energy zero.

## 3. Uniform 148-dimensional Krawczyk proof

There are 37 state nodes and 148 unknowns. With fixed
`T=17.412624804302453` and 36 equal steps, the equations are

\[
\begin{cases}
 z_{j+1}-\Phi_{T/36}(z_j)=0,&j=0,\ldots,35,\\
 \|u(z_0)\|^2-.01^2=0,\\
 s(z_0)-H_{\rm true}(u(z_0))=0,&\text{two rows},\\
 p(z_{36})-g_{\rm true}(e,d,\omega)=0.&
\end{cases}
\]

`heteroclinic_interval_probe.cpp --robust` encloses CAPD flow maps and first
variations on every shooting box. At the source it uses the just-proved true
graph budgets `C0=1e-20`, `C1=1e-18`; at the target it uses
`C0=1e-8`, `C1=1e-5`. Values and rows are intervalized independently, which
is deliberately broader than the true correlated jets. Therefore every
actual correlated source/target jet is contained in the evaluated family.

For midpoint `zbar`, interval box `X`, and numerical inverse `A`, the program
checks

\[
 z_{\rm bar}-AF(z_{\rm bar})+
 (I-A[DF(X)])(X-z_{\rm bar})\subset\operatorname{int}X.
\]

The componentwise inclusion ratio is `0.18217055712874344`; the corresponding
weighted-max contraction ratio is `0.18216932777866471<1`. Thus, for the true
graphs (indeed uniformly for every admissible fixed graph pair), the box has
one and only one zero.

The three source rows cut the two-dimensional unstable manifold by the radial
section `||u||=.01`, leaving its one-dimensional phase curve. Eliminating the
36 nonsingular continuity blocks reduces the bordered Jacobian to the
derivative of the terminal graph equation along the transported phase
tangent. Hence bordered nonsingularity says precisely that this tangent is not
in the target tangent space. Both invariant manifolds contain the flow
direction, while the radial source section is transverse to that direction.
Therefore bordered nonsingularity is equivalent to ambient transversality of
`W^u(0)` and the future target modulo their common flow direction. The fixed
time is a gauge choice; it does not manufacture transversality.

Since `W^u(0)` has exact energy zero and the signed-energy physical graph is
valid at zero, the certified zero is a true origin-to-algebraic heteroclinic.
The weighted bounds also give `p/e<0`, so its forward orbit remains in the
physical corridor, tends to the algebraic end as `e` tends to zero, and does
so at infinite original time.

## Rebuild and verify

Validated toolchain for the included certificate:

```text
g++ 15.2.0
CAPD 2.5.1, git 731079217a9254ea2948d742df2b170895effe7f
FILIB interval backend, -frounding-math
```

Run exactly from the repository root:

```bash
CAPD_CONFIG=/tmp/papera-capd.bKwHIQ/CAPD/build/bin/capd-config
BUILD_DIR=$(mktemp -d /tmp/papera-origin-heteroclinic.XXXXXX)

g++ -std=c++17 validation/origin-algebraic-heteroclinic/unstable_graph_probe.cpp \
  -Ivalidation/origin-algebraic-heteroclinic \
  $($CAPD_CONFIG --cflags) -O2 $($CAPD_CONFIG --libs) \
  -o "$BUILD_DIR/unstable_graph_probe"

g++ -std=c++17 \
  validation/origin-algebraic-heteroclinic/heteroclinic_interval_probe.cpp \
  -Ivalidation/origin-algebraic-heteroclinic \
  $($CAPD_CONFIG --cflags) -O0 $($CAPD_CONFIG --libs) \
  -o "$BUILD_DIR/heteroclinic_interval_probe"

"$BUILD_DIR/unstable_graph_probe"
"$BUILD_DIR/heteroclinic_interval_probe" --robust
```

The canonical future-graph and signed-corridor commands are listed in
`../future-target-fold/README.md`; their outputs and source hashes are imported
verbatim into this bundle's `certificate.json`. No executable is written into
either source directory.

To audit the exact degree-ten table independently (this symbolic solve takes
several minutes), run

```bash
python3 generate_polynomial_header.py \
  --output /tmp/unstable_graph_terms.rebuilt.hpp
cmp unstable_graph_terms.hpp /tmp/unstable_graph_terms.rebuilt.hpp
```

`../future-target-fold/build_prototype.py` contains the exact
`Q(sqrt(2),sqrt(3))` degree-seven recursion and weighted cancellation used to
create the canonical checked tail headers.
