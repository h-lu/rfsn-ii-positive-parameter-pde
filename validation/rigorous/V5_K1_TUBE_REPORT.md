# V5 finite resolved-\(K_1\) tube interval proof

**Result:** local mathematical **PASS** on the complete frozen v2 parameter
box.  This is a current-computer, non-claim-bearing interval proof of the
finite zero-energy resolved-\(K_1\) tube from the physical \(U=-4\) cut to
\(r_1=2\).  Together with the certified V4 terminal graph, the tube has a
unique complete lower pullback graph on every parameter slice.  This is one
component of V5, not yet the V5 incidence theorem.

## Exact object

Write

\[
 s=\sqrt\epsilon,\qquad \sigma=r/r_1,\qquad x=sr_1^2,
 \qquad D=2+x,
\]

and use the singular branch and its displayed finite-\(\sigma\) correction
from the V5 construction,

\[
 Q=\sqrt{\frac{8+3x}{6s}},\qquad P=\frac QD,
\]

\[
 K=\frac{\sigma^3a_2r_1(x+3)}{3sQD},\qquad
 W=\frac{\sigma^2(x+4)}{3D^3},\qquad
 \lambda=\sqrt{sD}.
\]

The probe evaluates the exact energy-reduced V5(33)--(34) field in the
spectral coordinates

\[
 \Pi=P-K+b+n,
 \qquad \Omega=W+\lambda(n-b),
 \tag{1}
\]

on

\[
\begin{gathered}
 r\in[1/100,1/50],\qquad a_2\in[-1/4,1/4],\qquad
 \epsilon\in[4/5,6/5],\\
 r\sqrt{4+ra_2}\le r_1\le2,qquad
 |b|\le1.3\times10^{-4},\qquad |n|\le10^{-4},\qquad H=0.
\end{gathered}
\tag{2}
\]

The lower \(r_1\) face is the exact \(U=-4\) representation obtained by
setting \(M=4\) in the central-to-\(K_1\) transition.  The upper face is the
same physical \(R=2\) cut used by the V4 attachment.

## Cancellation-free root and field

Direct interval evaluation of the raw field subtracts correlated
\(O(1)\) terms and then divides by

\[
 r_1'=\frac{s}{2}\sigma^2\Pi r_1.
\]

That representation is exact but unusably wide near the singular branch.
The probe instead uses identities before interval evaluation.  Put
\(\bar q=Q-DK\).  The \(O(\sigma^3a_2)\) contribution in V5(34) is exactly
\(-2QDK\).  Hence

\[
 q_{1,\mathrm{ref}}^2=\bar q^2+R,
 \qquad
 q_{1,\mathrm{ref}}-\bar q
 =\frac{R}{q_{1,\mathrm{ref}}+\bar q},
\tag{3}
\]

where the remainder is evaluated as

\[
\begin{aligned}
R={}&\frac{\sigma^4x(3x+10)}{6sD^3}
-\frac{2a_2r_1\sigma^7(x^2+4x+2)}{3sD^3}
+K^2(\sigma^4-D^2)\\
&+\frac{2a_2^3r_1^3\sigma^9}{3s}
+\frac{a_2^4r_1^6\sigma^{12}}6.
\end{aligned}
\tag{4}
\]

For \(e=b+n\), \(y=\lambda(n-b)\), the remaining change in \(q_1^2\)
is

\[
 -\frac{2y\sigma^2}{s}
 +e\{2(P-K)+e\}\sigma^4
 +\frac{2ya_2r_1\sigma^5}{s},
\tag{5}
\]

and is rationalized once more.  Equations (3)--(5), together with
\(Q=PD\) and \(\lambda^2=sD\), give an exact centered \(r_1\)-time field in
which the stable and unstable leading terms are combined before rounding.

For the four isolating faces, the code evaluates the algebraically
distributed positive multiple

\[
 s\sigma^2r_1P\Pi\lambda\,(b',n').
\tag{6}
\]

The scale in (6) is strictly positive on (2), so it preserves all face
orientations.  The projective cone is evaluated separately for the genuine,
unscaled \(r_1\)-time field; no time-scaled Jacobian is substituted for it.

Each face enclosure also uses the rigorous one-dimensional mean-value
identity

\[
 F(I)\subset F(m)+\partial_{r_1}F(I)(I-m),
\tag{7}
\]

with \(m\) the binary64 midpoint contained in the corresponding \(r_1\)
cell.  Formula (7) changes only the interval representation, not the field
or the covered set.

## Gap-free cover and margins

The parameter cover has 8 \(r\)-slabs, 32 \(a_2\)-slabs, and 8
\(\epsilon\)-slabs.  Each physical interval from
\(r\sqrt{4+ra_2}\) to 2 is covered by 32 quadratically placed
\(r_1\)-slabs, and the stable coordinate by 16 slabs.  The resulting
1,048,576 core cells are gap-free and use outward-rounded FILIB intervals.

The positive branch and clocks satisfy

| Quantity | Rigorous enclosure |
|---|---:|
| \(q_1^2\) | \([1.2146765761716976,3.5522684449708906]\) |
| \(q_1\) | \([1.1021236664602105,1.884746254796887]\) |
| \(\Pi\) | \([0.2686218927886684,0.611245132169846]\) |
| \(r_1'\) | \([6.555218919036329\!\times10^{-6},0.0037540388792403944]\) |
| positive scale (6) | \([8.794774425385345\!\times10^{-6},0.0061974749936906355]\) |

The oriented face margins for (6) are

| Face | Rigorous lower margin |
|---|---:|
| \(b=+1.3\times10^{-4}\), inward | \(1.3127700554053793\times10^{-4}\) |
| \(b=-1.3\times10^{-4}\), inward | \(1.3310569826198603\times10^{-4}\) |
| \(n=+10^{-4}\), outward | \(7.863414504722722\times10^{-5}\) |
| \(n=-10^{-4}\), outward | \(7.477194903315319\times10^{-5}\) |

Write the Jacobian of the unscaled \(r_1\)-time \((b,n)\) generator as

\[
 D_{(b,n)}F=\begin{pmatrix}c&\beta\\ \delta&a\end{pmatrix}.
\]

On every cover cell the probe evaluates the correlated pointwise margin

\[
 M=\rho(a-c)-\rho^2|\beta|-|\delta|,
 \qquad \rho=7/10.
\]

The minimum over the complete gap-free cover is

\[
 M\ge308.53197710214516>0.
 \tag{8}
\]

For diagnostics, the four extrema aggregated independently over the whole
cover are

\[
 c\le-343.44786957761136,\quad |\beta|\le403.21795637619476,
\]

\[
 |\delta|\le310.553324271202,\quad a\ge335.13918837250856.
\]

Those extrema occur in different cells and are not recombined into a proof
bound.  The proof gate is the cellwise pointwise minimum (8), which retains
the correlations needed after the base enlargement.

### Finite terminal pullback lemma

The preceding gates close the finite graph statement without an additional
normal-growth hypothesis.  We record the argument because the conclusion is
stronger than saying that a graph is unique only for as long as it happens to
remain in the tube.

Let

\[
 B=1.3\times10^{-4},\qquad N=10^{-4},\qquad \rho=7/10,\qquad
 r_-(\mu)=r\sqrt{4+ra_2},
\]

where \(\mu=(r,a_2,\epsilon)\) belongs to the frozen v2 box, and let
\(\mathcal R=[-B,B]\times[-N,N]\) in the \((b,n)\) coordinates, with
\(\operatorname{int}_n\mathcal R=[-B,B]\times(-N,N)\).  The V4
seam certificate supplies, for each \(\mu\), a fixed terminal graph

\[
 \Gamma^+_\mu=\{(b,g^+_\mu(b)):\ |b|\le B\}\subset\operatorname{int}_n
 \mathcal R
 \quad\hbox{at }r_1=2,
 \tag{9}
\]

over the entire base.  In fact its terminal normal values satisfy
\(|g^+_\mu|\le6.637293639326057\times10^{-6}<N\).  The cancellation-free
seam derivatives in (12) of
[`V4_ADAPTED_ZERO_TUBE_REPORT.md`](V4_ADAPTED_ZERO_TUBE_REPORT.md) give a
positive base derivative and put every tangent strictly inside the
slope-\(7/10\) cone.  The terminal graph is \(C^3\), so the mean-value
theorem puts all its secants in

\[
 \mathcal C_\rho
   =\{(\delta b,\delta n):|\delta n|\le\rho|\delta b|\}.
 \tag{10}
\]

**Lemma.**  For every \(\mu\) there is a unique \(C^3\) function
\(g^-_\mu:[-B,B]\to(-N,N)\), with one-sided regularity at the endpoints,
such that the forward orbit from
\((b,g^-_\mu(b))\) at \(r_1=r_-(\mu)\) stays in \(\mathcal R\) and reaches
\(\Gamma^+_\mu\) at \(r_1=2\).  Moreover,

\[
 \operatorname{Lip}(g^-_\mu)\le\rho=7/10.
 \tag{11}
\]

Thus the set of lower points whose forward orbits stay in \(\mathcal R\) and
reach the actual V4 terminal graph is a complete lower pullback graph on the
physical \(U=-4\) section.  This wording does not assert that every point of
the larger terminal graph has a backward orbit that remains in the tube.

**Proof.**  The positive lower bound for \(r_1'\) makes \(r_1\) a regular
forward time on the whole compact tube.  Fix \(\mu\) and a lower base point
\(b_0\in[-B,B]\), and vary the initial value \(n_0\) along \([-N,N]\).
The two \(b\)-faces are forward inward, so an orbit cannot leave through
them.  Classify an initial value as lower if its orbit first exits through
\(n=-N\), or if it reaches \(r_1=2\) strictly below \(\Gamma^+_\mu\);
classify it as upper by the analogous alternatives at \(n=+N\) and above
\(\Gamma^+_\mu\).  Strict outward orientation of the two \(n\)-faces,
continuous dependence of the flow, and the strict interior inclusion in
(9) make the lower and upper classes disjoint and relatively open.  They
contain \(n_0=-N\) and \(n_0=N\), respectively.  Since \([-N,N]\) is
connected, the two classes cannot cover it.  Any unclassified initial value
therefore remains in the tube up to \(r_1=2\) and lands on
\(\Gamma^+_\mu\).  This proves existence for every \(b_0\); strict exit at
the \(n\)-faces also gives \(|n_0|<N\).

It remains to prove uniqueness and the graph bound.  For two orbits in the
tube, their difference satisfies a linear equation whose coefficient matrix
\(\bar J\) is the Jacobian averaged over the segment joining the two orbit
points.  The tube is convex, so that segment is covered by the same gap-free
cell family.  If
\(p=\delta n/\delta b\), its projective equation is

\[
 p'=\delta+(a-c)p-\beta p^2.
\]

At each point on the segment, (8) bounds the right-hand side from below by
\(M\) when \(p=\rho\), and from above by \(-M\) when \(p=-\rho\).
Averaging preserves these bounds: the diagonal terms are linear and
\(|\int f|\le\int|f|\) controls both cross terms.  Thus the vector field
points out of
the horizontal cone in forward time, and the cone is strictly invariant in
backward time.  Hence the cellwise pointwise margin in (8) makes
\(\mathcal C_\rho\) backward invariant for these **secants**, not merely for
individual tangent vectors.  Two terminal points on (9) have their
difference in \(\mathcal C_\rho\), so their lower difference also belongs to
\(\mathcal C_\rho\).  If they have the same lower \(b_0\), this forces
\(|\delta n_0|\le\rho|\delta b_0|=0\), proving uniqueness.  Applying the
same estimate to arbitrary lower base points gives
\(|g^-_\mu(b_2)-g^-_\mu(b_1)|\le\rho|b_2-b_1|\), which is (11).

For completeness, the terminal graph and finite-time flow are \(C^3\), so
their inverse image is locally a \(C^3\) curve.  Its nonzero tangent belongs
to \(\mathcal C_\rho\) by the same backward-cone argument and is therefore
not vertical.  The local curves are graphs over \(b\); pointwise uniqueness
glues them into the stated global \(C^3\) graph.  \(\square\)

This is a finite terminal-value shooting argument.  It uses only the
positive \(r_1\)-clock, the four face orientations, the secant-cone margin
(8), and the complete V4 terminal graph; no stronger normally expanding
corridor theorem is invoked.

## Reproduction and claim boundary

The source is
[vdp_v5_k1_tube_probe.cpp](src/vdp_v5_k1_tube_probe.cpp), and the compiled
checks are in
[test_v5_k1_tube_probe.py](tests/test_v5_k1_tube_probe.py).  Run

    python3 -B -m unittest \
      validation.rigorous.tests.test_v5_k1_tube_probe -v

with the pinned strict CAPD/FILIB build, or set `RFSN_CAPD_CONFIG` to its
`capd-config`.

The machine field `claim_bearing=false` is deliberate.  This calculation,
together with the separate V4 seam certificate, proves that its **fixed** V4
terminal graph pulls back on every parameter slice to the complete graph
\(n=g^-_\mu(b)\) on \(|b|\le1.3\times10^{-4}\) at \(U=-4\), with
\(|g^-_\mu|<10^{-4}\) and
\(\operatorname{Lip}(g^-_\mu)\le7/10\).  Uniqueness is relative to that
fixed terminal graph; it is not a uniqueness assertion for every invariant
or slow graph that might meet the tube.  The proof is confined to \(H=0\),
and it gives no pointwise enclosure of \(g^-_\mu(b)\) narrower than the
displayed normal tube.  The central-coordinate regraph, the first hit by the
source manifold, and the V5 scalar incidence equation are separate
interfaces and are not proved here.
