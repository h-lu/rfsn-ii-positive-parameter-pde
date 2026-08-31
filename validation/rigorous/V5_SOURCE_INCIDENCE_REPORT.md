# V5 true-source incidence: representative-cell interval proof

**Result.**  The source-incidence kernel gives mathematical **PASS** on one
representative parameter cell.  On that cell, the exact zero-energy true
source crosses every lower V5 graph satisfying the already certified bounds
at one strictly secant-separated point.  The crossing is transverse when the
target graph is \(C^1\), in particular for the actual \(C^3\) finite-\(K_1\)
pullback graph:

\[
 |b|\le B=1.35\times10^{-4}=\frac{27}{200000},
 \qquad |g(b)|<N=10^{-4},
 \qquad \operatorname{Lip}(g)\le \frac7{10}.
 \tag{1}
\]

The calculation is a local, non-claim-bearing proof unit.  A grouped
candidate-hull version of the same kernel also passes at the lower, centre,
and upper disclosed grid cells.  These three samples exercise that kernel and
establish a feasibility milestone for a future full cover, but are not a
cover of the complete
`vdp-positive-box-v2`.  The calculation also does not yet invoke the separate
finite-\(K_1\) pullback theorem in a claim-bearing composite V5 theorem.  The
machine field `claim_bearing=false` is therefore essential.

## Certified cell and source chart

The tested cell is the zero-based cell \((32,64,20)\) of a
\(64\times128\times40\) grid, namely

\[
 r\in\left[\frac{96}{6400},\frac{97}{6400}\right],
 \qquad
 a_2\in\left[0,\frac1{256}\right],
 \qquad
 \epsilon\in\left[1,\frac{101}{100}\right].
 \tag{2}
\]

On the radius-\(1/100\) source circle, let \(u=(u_1,u_2)\), put

\[
 s_1=H_{10,1}(u)+\eta,
 \qquad U=u_1+s_1,
 \qquad |\eta|\le\frac1{200000},
 \qquad |\partial_\varphi\eta|\le\frac3{1000000},
 \tag{3}
\]

and use the slanted phase coordinate

\[
 \varphi=\Phi(\mu)+\theta-\frac{11}{8}\eta,
 \qquad \mu=(r,a_2,\epsilon).
 \tag{4}
\]

Here \(\Phi\) is a disclosed degree-four numerical predictor.  It only
centres interval boxes: no fit residual or accuracy assertion for \(\Phi\)
is used in any proof gate.  The two closed half-tubes in \(\eta\) cover all
of (3).  The bound on \(\eta_\varphi\) gives

\[
 \frac{d\varphi}{d\theta}
   =\frac1{1+(11/8)\eta_\varphi}>0,
 \tag{5}
\]

so the slanted coordinate neither reverses nor loses the true-source phase.

## Exact zero-energy identity

Write

\[
 A_\mu=1+\sqrt\epsilon\,r^3a_2,
 \qquad B_\mu=\frac{\sqrt\epsilon\,r^2}{3},
 \qquad 2\alpha_\mu\beta_\mu=h_\mu,
\]

and define the fourth source coordinate by

\[
 s_2=-\frac{s_1u_2}{u_1}
      -\frac{A_\mu U^3}{6h_\mu u_1}
      +\frac{B_\mu U^4}{8h_\mu u_1}.
 \tag{6}
\]

The interval gates keep \(u_1>0\), so (6) is regular.  After the exact
linear source-to-physical change of variables, substitution into the
Hamiltonian gives

\[
 H_\mu
 =2h_\mu(u_1s_2+s_1u_2)
   +\frac{A_\mu U^3}{3}-\frac{B_\mu U^4}{4}=0
 \tag{7}
\]

identically.  Thus the source tube propagated by the program lies on
\(H=0\) by algebra, not because an interval evaluation happens to contain
zero.  The latter check is retained only as a consistency guard against an
implementation error.

The central orbit is enclosed through its first crossing of
\(U=-1/20\), with \(P<0\) and a verified no-earlier-hit margin.  It then uses

\[
 x=-U,\qquad W=P^2,
 \]

as regular reduced variables up to \(x=4\), i.e. the physical section
\(U=-4\).  At that endpoint the cancellation-prone V5 normal coordinate is
evaluated using the exact \(H=0\) identity

\[
 m\Omega
 =\frac{W-Q^2}{8}+\frac{32}{3}+4ra_2
  +\sqrt\epsilon\left(
      2r^4a_2^2+\frac{32}{3}r^3a_2+16r^2\right),
 \qquad m=4+ra_2.
 \tag{8}
\]

No asymptotic truncation enters (7) or (8).

## Exterior-product derivative transport

Let

\[
 X_\mu(U,P,V,Q)=(P,f_\mu(U)-V,Q,U),
\]

where

\[
 f_\mu(U)=
 (2ra_2+\sqrt\epsilon\,r^4a_2^2)U
 -(1+\sqrt\epsilon\,r^3a_2)U^2
 +\frac{\sqrt\epsilon\,r^2}{3}U^3.
\]

For a parameter \(\mu_j\), let \(v=\partial_\theta z\) be the phase
tangent and let \(s_j\) be the parameter tangent at fixed \((\varphi,\eta)\).
Put \(k=f_{\mu,U}\), \(L_j=\partial_{\mu_j}f_\mu\), and
\(w=s_j\wedge v\), ordered as

\[
 (w_{UP},w_{UV},w_{UQ},w_{PV},w_{PQ},w_{VQ}).
\]

The code integrates the following exact closed system together with the
orbit and \(v\):

\[
\begin{aligned}
 \dot w_{UP}&=-w_{UV}-L_jv_U, &
 \dot w_{UV}&=w_{PV}+w_{UQ},\\
 \dot w_{UQ}&=w_{PQ}, &
 \dot w_{PV}&=k w_{UV}+w_{PQ}+L_jv_V,\\
 \dot w_{PQ}&=-w_{UP}+k w_{UQ}-w_{VQ}+L_jv_Q, &
 \dot w_{VQ}&=-w_{UV}.
\end{aligned}
\tag{9}
\]

This formulation removes the irrelevant phase gauge.  Indeed, differentiating
at fixed \(\theta\) instead of fixed physical phase changes the parameter
tangent by a multiple of the phase tangent,

\[
 s_j^{\,\theta}=s_j^{\,\varphi}+\Phi_{\mu_j}v,
 \qquad
 s_j^{\,\theta}\wedge v=s_j^{\,\varphi}\wedge v.
 \tag{10}
\]

Consequently the derivative certificate is independent of the numerical
predictor.  It is also explicitly a **fixed-\(\eta\)** derivative.  This is
sufficient for the actual moving graph \(\eta_\mu(\varphi)\): all estimates
are uniform over the full \(\eta\)-tube, so a point at a new parameter is
compared with the centre parameter while holding that point's value of
\(\eta\) fixed.  No unavailable bound on \(\partial_\mu\eta\) is inferred.
The phase-slope calculation, separately, uses (3) and the exact chain rule
from (4), so it applies to the actual source curve rather than merely to a
fixed-\(\eta\) surrogate.

At the first \(U=-1/20\) event, event-time projection and the change to
\((W,Q)\) give the parameter/phase determinant

\[
 D_j=2\{P w_{PQ}-\dot P\,w_{UQ}+U w_{UP}\}.
 \tag{11}
\]

This division-free formula is propagated in the reduced system

\[
 W_x=F(x,W,Q;\mu),\qquad Q_x=-\frac{x}{\sqrt W},
\]

for which

\[
 D_j'=\frac{D_j}{x}+F_{\mu_j}v_Q,
 \qquad
 d_j:=\frac{D_j}{x},qquad
 d_j'=\frac{F_{\mu_j}}{x}v_Q.
 \tag{12}
\]

The proof checks \(W>0\) densely throughout this passage.

## The \(n=0\) branch and incidence budget

At \(U=-4\), let \((b,n)\) be the exact V5 spectral coordinates and set

\[
 E=b+n,
 \qquad c=b+\frac{n}{32}.
 \tag{13}
\]

The anchor is located by a parameterized one-dimensional interval Newton
argument rather than by fixed narrow phase faces.  Let

\[
 X=[-1/25000,1/25000],
 \qquad F(\theta,\eta)=n(\mu_c,\theta,\eta),
\]

where \(\mu_c\) is the cell centre.  The eight exact phase slabs and two closed
\(\eta\) half-tubes give one enclosure

\[
 D\supset F_\theta(X,[-1/200000,1/200000]),
 \qquad \sup D<0.
\]

Split the \(\eta\)-tube into four exact, gap-free slices \(E_i\).  On every
slice the program verifies

\[
 K_i=-\frac{F(0,E_i)}{D}\Subset X.
 \tag{14}
\]

The parameterized interval Newton theorem therefore gives, for every
\(\eta\in E_i\), exactly one zero of \(F(\cdot,\eta)\) in \(K_i\).  The
derivative enclosure \(D\) allows the full interval of admissible
\(\eta_\varphi\); since that interval contains zero, it also encloses the
fixed-\(\eta\) derivative required in (14).  On the Newton root \(c=b\), so
evaluating the aligned coordinate on the entire root box supplies the anchor
bound without cancellation.  The four closed slices cover the same complete
\(\eta\)-tube as the preceding eight-slice implementation and reduce the
anchor stage from sixteen to eight interval evaluations; every slice retains
a strict Newton inclusion and a root-image enclosure containing zero.
When the parameter cell is an exact point cell, the implementation also
checks that all three offset intervals equal \([0,0]\) before reusing the
already verified terminal enclosure as its centre-parameter enclosure.  If
any offset is nonzero, the independent centre propagation is retained.  This
removes a literally duplicated propagation in the anchor stage; it does not
replace any nondegenerate parameter enclosure.

For each parameter, \(n_\theta<0\).  Eliminating the root's phase derivative
using (11)--(12) gives

\[
 \left.\frac{db}{d\mu_j}\right|_{n=0,\eta}
 =E_W\frac{n_QD_j-v_Wn^0_{\mu_j}}{n_\theta}
   +E^0_{\mu_j}.
 \tag{15}
\]

Here the superscript \(0\) denotes explicit differentiation of the terminal
coordinate at fixed \((W,Q)\).  Every division in (14)--(15), including
those in the terminal affine subdivisions, is made only after proving
\(n_\theta<0\).

The continuation strip \(|\theta|\le1/25000\) is covered by eight exact slabs
and both \(\eta\) half-tubes.  Twelve slab/half-tube evaluations meet
\(n=0\), and the same twelve meet \(|n|\le N\).  The resulting outward-rounded
enclosures can be summarized conservatively as follows.

| Quantity | Rigorous enclosure or one-sided bound |
|---|---:|
| centre-cell anchor \(c=b\) on the Newton root | \([-3.476\times10^{-6},-2.591\times10^{-6}]\) |
| anchor root phase over all four \(\eta\)-slices | \([-8.873,8.528]\times10^{-8}\) |
| \(n_\theta\) on the continuation cover | \([-2117.29,-912.95]\) |
| \(\partial_r b\) on \(n=0\), fixed \(\eta\) | \([-0.014693,0.010124]\) |
| \(\partial_{a_2} b\) on \(n=0\), fixed \(\eta\) | \([-0.000978,0.000703]\) |
| \(\partial_\epsilon b\) on \(n=0\), fixed \(\eta\) | \([-0.012341,0.009694]\) |
| \(|db/dn|\) along the true source for \(|n|\le N\) | at most \(0.394739<1/2\) |
| terminal \(Q\) on candidate slabs | \([-9.418,-9.095]\subset(-19/2,-9)\) |
| parameter-variation budget | at most \(6.477\times10^{-5}\) |
| source excursion \(\rho_{\rm src}N\) | at most \(3.948\times10^{-5}\) |
| remaining base margin | at least \(2.728\times10^{-5}>0\) |

More explicitly, (15) and the half-widths of (2) imply

\[
 \Delta_{\mu}b\le6.477\times10^{-5}.
\]

Together with the anchor and source-slope bounds,

\[
 |b|
 \le 3.476\times10^{-6}
     +6.477\times10^{-5}
     +0.394739\times10^{-4}
 <1.35\times10^{-4}=B.
 \tag{16}
\]

Thus the entire relevant source segment stays in the base domain of every
graph in (1).  The wide continuation faces lie respectively above \(n=N\)
and below \(n=-N\).  Since \(n_\theta<0\), there are unique intermediate
phases with \(n=N\) and \(n=-N\).  Estimate (16) puts the intervening source
segment inside \(|b|\le B\), where \(g\) is defined.  Consequently
\(h(\theta)=n(\theta)-g(b(\theta))\) is positive at \(n=N\) and negative at
\(n=-N\).  On this graph tube, the two cone bounds give, almost everywhere,

\[
 h_\theta
 \le -(1-\tfrac7{10}\rho_{\rm src})(-n_\theta)<0,
 \qquad \rho_{\rm src}\le0.394739.
 \tag{17}
\]

The same conclusion follows directly from the corresponding secant cones
when \(g\) is only Lipschitz.  Hence the crossing exists uniquely with
strict secant separation.  When \(g\) is \(C^1\), the derivative inequality
in (17) makes the crossing transverse; this applies in particular to the
actual \(C^3\) pullback graph supplied by the finite-\(K_1\) lemma.  Since
the estimates are uniform in \(\eta\), the conclusion includes the actual
true-source graph from (3).

### Grouped candidate-hull exterior kernel

The expensive part of the cell proof is the exterior-product propagation
used in (15).  It need not be repeated on every zero-candidate slab.  For
each fixed \((\mu,\eta)\), the two continuation-face signs and
\(n_\theta<0\) give exactly one zero \(\theta_*(\mu,\eta)\).  The complete
eight-slab cover contains that zero in at least one slab.  A valid interval
evaluation on this slab necessarily contains \(0\) in its image of \(n\), so
the slab is selected by the test `n.contains(0)`.

The implementation assigns the eight slabs to eight fixed groups inside each
\(\eta\) half-tube.  Within every group it takes the hull of all selected
slabs and performs (15) once on that hull.  Taking a hull can only enlarge the
selected set, so the resulting derivative enclosures cover the entire root
branch.  Groups without a selected slab are skipped.  With the present
eight-slab cover each group contains one slab; the grouped representation is
retained because the proof remains valid if later refinements place several
adjacent slabs in one group.  No exterior-evaluation reduction is claimed for
the three certificates below.  This is a covering argument, not a heuristic
root predictor; the phase predictor still enters only as the coordinate
centring described above.

The program also re-evaluates \(n\) on every selected hull and requires its
interval image to contain zero.  This is a conservative consistency gate,
not the existence proof for a root in each selected group: some selected
slabs may be interval false positives.  Fibrewise root existence and
uniqueness come from the continuation-face signs and monotonicity; the hull
construction ensures that whichever group contains the root is propagated.
This re-evaluation is carried by the same augmented exterior system that
transports (11)--(12).  It rebuilds the complete source and finite seam on the
selected hull, retains all three exterior-event propagations, and returns the
terminal spectral \(n\) together with the fixed-\(\eta\) derivatives.  The
ordinary terminal and centre-terminal trajectories, already verified on the
complete slab cover, are therefore not replayed inside the derivative stage.

The same uniform eight-group rule was run on three disclosed cells:

| cell | exterior evaluations | parameter budget | strict base margin |
|---|---:|---:|---:|
| lower \((0,0,0)\) | 12 | \(9.002\times10^{-5}\) | \(1.579\times10^{-6}\) |
| centre \((32,64,20)\) | 12 | \(6.477\times10^{-5}\) | \(2.728\times10^{-5}\) |
| upper \((63,127,39)\) | 12 | \(7.082\times10^{-5}\) | \(1.080\times10^{-5}\) |

All local gates pass at all three cells.  In particular, the narrow positive
margin at the lower corner is retained with outward rounding.  Relative to
the preceding 16-slab implementation, the complete ordinary phase scan has
been halved while all proof gates remain strict.  These results
establish the feasibility of the grouped kernel for the next adaptive-cover
step.  They are three cell-level certificates, not point samples, but the
cells are disjoint and control no untested cell.  They therefore do not
interpolate between the three cells, change `claim_bearing=false`, or
establish the complete parameter-box theorem and its claim-bearing
finite-(K_1) composition.

## Reproduction and exact claim boundary

The implementation is
[`src/vdp_v5_source_incidence_probe.cpp`](src/vdp_v5_source_incidence_probe.cpp).
The archived machine result is
[`results/vdp_v5_source_incidence_representative_cell.json`](results/vdp_v5_source_incidence_representative_cell.json).
The three grouped samples are archived as
[`lower`](results/vdp_v5_source_incidence_grouped_lower_cell.json),
[`centre`](results/vdp_v5_source_incidence_grouped_center_cell.json), and
[`upper`](results/vdp_v5_source_incidence_grouped_upper_cell.json) cells.
The current source SHA-256 is
`ef3b8c01f915adbd1a8cc0a04ed828e741d51f6115e56def3f42fecae9c6bff5`.
The original representative result's pretty-printed SHA-256 is
`3b4b885646de3e25ea52c0e6c696cb200f5c0cda05d4ff400f95329a1af38901`.
After compiling it against the repository's pinned strict CAPD/FILIB build,
the representative certificate is generated by

    vdp_v5_source_incidence_probe incidence-cell \
      64 128 40 32 64 20

The three grouped-kernel samples are generated by replacing
`incidence-cell` with `incidence-merged-cell` and using respectively
`0 0 0`, `32 64 20`, and `63 127 39` as the final indices.  Their archived
result SHA-256 values are, in that order,
`8c45d84f179f23d64b32d19179a154d6a71fb29d07f81f24d82cd0343c33f635`,
`b6507631ba3181b6578eb32ddefa16f29b723a9e545400f43e66068fb03eb6fa`,
and `0ef5e1f96459cff2f9110ff655d7a13e3242a62df7c8d27d4d9762d0733ba8f0`.
Each reports schema `rfsn-vdp-v5-source-incidence-merged-cell/1`, eight
uniform phase groups per error half, and `claim_bearing=false`.

The output must report schema
`rfsn-vdp-v5-source-incidence-cell/2`, mathematical status `PASS`, a passing
rounding self-test, all incidence gates true, and `claim_bearing=false`.  Its
anchor stage proves four parameterized interval-Newton inclusions.  Its
continuation stage finds six zero candidates in each closed error half-tube
and runs 2,048 terminal affine subboxes on each of the resulting 12 exterior
evaluations.

What is established is precisely the representative-cell statement at the
start of this report, conditional only on the admissible-graph contract
(1).  The separately proved finite-\(K_1\) terminal pullback supplies such a
graph, but that import has not yet been assembled here into a released V5
composite theorem.  A complete claim requires at least:

1. the same incidence gates on a gap-free cover of the entire frozen v2
   parameter box; and
2. a claim-bearing composition with the finite-\(K_1\) pullback and its V4
   terminal graph.

The \(64\times128\times40\) labels in this run define the representative
cell; they do **not** assert that all 327,680 cells have been checked.  No
time stability, dynamical Turing selection, canard identification, or global
stationary-PDE branch conclusion is made by this certificate.
