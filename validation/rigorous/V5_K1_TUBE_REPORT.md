# V5 finite resolved-\(K_1\) tube interval proof

**Result:** local mathematical **PASS** on the complete frozen v2 parameter
box.  This is a current-computer, non-claim-bearing interval proof of the
finite zero-energy resolved-\(K_1\) tube from the physical \(U=-4\) cut to
\(r_1=2\).  It is one component of V5, not yet the V5 incidence theorem.

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
 |b|\le10^{-4},\qquad |n|\le10^{-4},\qquad H=0.
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
| \(q_1^2\) | \([1.2147027942678423,3.5522684275717453]\) |
| \(q_1\) | \([1.1021355607491494,1.8847462501811076]\) |
| \(\Pi\) | \([0.26865189278866836,0.6112151321698459]\) |
| \(r_1'\) | \([6.555848880819688\!\times10^{-6},0.003753837125189916]\) |
| positive scale (6) | \([8.795619610244871\!\times10^{-6},0.006197141921572062]\) |

The oriented face margins for (6) are

| Face | Rigorous lower margin |
|---|---:|
| \(b=+10^{-4}\), inward | \(7.079754225107172\times10^{-5}\) |
| \(b=-10^{-4}\), inward | \(7.262719803114818\times10^{-5}\) |
| \(n=+10^{-4}\), outward | \(8.513314921150174\times10^{-5}\) |
| \(n=-10^{-4}\), outward | \(8.127032365657862\times10^{-5}\) |

For the unscaled \(r_1\)-time \((b,n)\) generator, the global bounds are

\[
 C\le-343.5528533649025,qquad
 |B|\le310.4813181359855,
\]

\[
 |D|\le310.48370091830685,qquad
 A\ge335.15650142092244.
\]

Combining these four independently aggregated extrema gives the conservative
slope-one projective-cone margin

\[
 A-C-|B|-|D|
 \ge57.744335731532544>0.
\tag{8}
\]

Direct cellwise evaluation, which retains the correlations within each
cell, gives the stronger lower bound \(477.89068514283\).

Consequently (2) supplies a strict finite graph-transform corridor with a
common cooriented slope-one backward-invariant cone.  Once an admissible
terminal graph is identified at \(r_1=2\), its backward transport through
this corridor is unique while it remains in the displayed tube.  The finite
corridor alone does not select that terminal graph; this is precisely why the
V4 attachment remains open below.

## Reproduction and claim boundary

The source is
[vdp_v5_k1_tube_probe.cpp](src/vdp_v5_k1_tube_probe.cpp), and the compiled
checks are in
[test_v5_k1_tube_probe.py](tests/test_v5_k1_tube_probe.py).  Run

    python3 -B -m unittest \
      validation.rigorous.tests.test_v5_k1_tube_probe -v

with the pinned strict CAPD/FILIB build, or set `RFSN_CAPD_CONFIG` to its
`capd-config`.

The machine field `claim_bearing=false` is deliberate.  This calculation
proves the finite resolved-\(K_1\) tube, but does not yet prove that the
actual V4 graph enters it at \(R=2\), identify its central \(U=-4\) cut,
connect that cut to the source manifold, or solve the V5 scalar incidence
equation.  Those are separate remaining interfaces.
