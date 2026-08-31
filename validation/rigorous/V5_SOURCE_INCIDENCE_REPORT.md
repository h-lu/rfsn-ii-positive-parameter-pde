# V5 true-source incidence: representative-cell interval proof

**Result.**  The source-incidence kernel gives mathematical **PASS** on one
representative parameter cell.  On that cell, the exact zero-energy true
source crosses, once and transversely, every lower V5 graph satisfying the
already certified bounds

\[
 |g(b)|<N,
 \qquad \operatorname{Lip}(g)\le \frac7{10},
 \qquad B=N=10^{-4}.
 \tag{1}
\]

The calculation is a local, non-claim-bearing proof unit.  It is not a cover
of the complete `vdp-positive-box-v2`, and it does not yet invoke the separate
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

The narrow anchor faces bracket a simple \(n=0\) root.  Since \(c=b\) on
that root, the aligned coordinate avoids the cancellation that made a direct
full-strip bound too wide.  For each parameter, \(n_\theta<0\).  Eliminating
the root's phase derivative using (11)--(12) gives

\[
 \left.\frac{db}{d\mu_j}\right|_{n=0,\eta}
 =E_W\frac{n_QD_j-v_Wn^0_{\mu_j}}{n_\theta}
   +E^0_{\mu_j}.
 \tag{14}
\]

Here the superscript \(0\) denotes explicit differentiation of the terminal
coordinate at fixed \((W,Q)\).  Every division in (14), including those in
the terminal affine subdivisions, is made only after proving
\(n_\theta<0\).

The continuation strip \(|\theta|\le1/25000\) is covered by 16 exact slabs
and both \(\eta\) half-tubes.  Twenty slab/half-tube evaluations meet
\(n=0\), and twenty meet \(|n|\le N\).  The resulting outward-rounded
enclosures can be summarized conservatively as follows.

| Quantity | Rigorous enclosure or one-sided bound |
|---|---:|
| centre-cell anchor \(c\) | \([-5.044\times10^{-6},-0.985\times10^{-6}]\) |
| \(\partial_r b\) on \(n=0\), fixed \(\eta\) | \([-0.012317,0.009023]\) |
| \(\partial_{a_2} b\) on \(n=0\), fixed \(\eta\) | \([-0.000801,0.000582]\) |
| \(\partial_\epsilon b\) on \(n=0\), fixed \(\eta\) | \([-0.010001,0.008185]\) |
| \(|db/dn|\) along the true source for \(|n|\le N\) | at most \(0.3373<17/50\) |
| terminal \(Q\) on candidate slabs | \([-9.394,-9.110]\subset(-19/2,-9)\) |
| parameter-variation budget | at most \(5.253\times10^{-5}\) |
| source excursion \((17/50)N\) | \(3.4\times10^{-5}\) |
| remaining base margin | at least \(8.427\times10^{-6}>0\) |

More explicitly, (14) and the half-widths of (2) imply

\[
 \Delta_{\mu}b\le5.253\times10^{-5}.
\]

Together with the anchor and source-slope bounds,

\[
 |b|
 \le 5.044\times10^{-6}
     +5.253\times10^{-5}
     +\frac{17}{50}10^{-4}
 <10^{-4}=B.
 \tag{15}
\]

Thus the entire relevant source segment stays in the base domain of every
graph in (1).  The wide continuation faces lie respectively above \(n=N\)
and below \(n=-N\), so \(h(\theta)=n(\theta)-g(b(\theta))\) changes sign.
On the graph tube, the two cone bounds give, almost everywhere,

\[
 h_\theta
 \le -(1-\tfrac7{10}\tfrac{17}{50})(-n_\theta)<0.
 \tag{16}
\]

The same conclusion follows directly from the corresponding secant cones
when \(g\) is only Lipschitz.  Hence the crossing exists, is unique, and is
transverse.  Since the estimates are uniform in \(\eta\), this includes the
actual true-source graph from (3).

## Reproduction and exact claim boundary

The implementation is
[`src/vdp_v5_source_incidence_probe.cpp`](src/vdp_v5_source_incidence_probe.cpp).
The archived machine result is
[`results/vdp_v5_source_incidence_representative_cell.json`](results/vdp_v5_source_incidence_representative_cell.json).
For this run the source SHA-256 is
`f506d3cdaf8a26c030b58f95260e26d925f68f61712b3d1996d2f219efcef6b3`
and the pretty-printed result SHA-256 is
`b68030c804865ef190a514a4892fac7941093cd115c7815fda29eb38ab4ea310`.
After compiling it against the repository's pinned strict CAPD/FILIB build,
the representative certificate is generated by

    vdp_v5_source_incidence_probe incidence-cell \
      64 128 40 32 64 20

The output must report schema
`rfsn-vdp-v5-source-incidence-cell/1`, mathematical status `PASS`, a passing
rounding self-test, all incidence gates true, and `claim_bearing=false`.  Its
two-stage cover finds ten zero candidates in each closed error half-tube and
runs 2,048 terminal affine subboxes on each of the resulting 20 exterior
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
