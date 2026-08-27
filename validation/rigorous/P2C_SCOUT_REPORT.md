# Issue #7 P2c selected-homoclinic scout report

**Evidence status: strict design-scout results plus floating candidate data.**
The strict computations below complete, at design level, the selected root
branch, endpoint transversality, selected-source-to-symmetry-event first-hit
gates, actual-root parameter two-jets, and both infinite weighted tails on the
full three-parameter bridge.  This report nevertheless does not mark
`V2.HOM.BRANCH`, `V2.HOM.FIRST_HIT`, `V2.HOM.TRANSVERSE`, or `V2.HOM.TAILS`
as claim-bearing passes: the P2c configuration, certificate, checker, and
policy replay have not yet been frozen.  In addition, one explicit
continuous-time (C^2) bound on the compact middle segment is still needed
to turn the tail constants into a single numerical constant for the global
(X_\eta) estimate in Theorem V2(9)--(11).  The remaining obligations are
separated explicitly at the end.

## Correct source and shooting problem

The numerical and interval scouts use the direct P2bK source circle

\[
 b_\mu(\phi)=10^{-2}R_{\chi(\mu)}(\cos\phi,\sin\phi)
\]

in the algebraic unstable coordinates.  This is not the older
unit-normalized numerical eigenframe section.  On the true zero-energy graph,
the first stable-coordinate error

\[
 e=(H_\mu-H_{10})_1
\]

obeys \(|e|\le5\times10^{-6}\) and
\(|\partial_\phi e|\le3\times10^{-6}\).  The zero-energy equation then
determines the second stable coordinate exactly:

\[
 s_2=-\frac{s_1u_2}{u_1}
      -\frac{aU^3}{6hu_1}
      +\frac{bU^4}{8hu_1},\qquad U=u_1+s_1.
\]

The strict scout represents this one graph error by one unknown and uses nine
short shooting segments followed by the `Q=0` Poincare map.  This avoids the
long-flow wrapping caused by treating the two stable graph errors as
independent boxes.

## Completed results

The floating direct-source scout reproduces the frozen core intervals and
continues the same candidate root to the primary point
\((r,a_2,\epsilon)=(.08,0,1)\).  A separate \(3\times3\times3\) target-grid
scout found 27 out of 27 roots without a phase jump or determinant sign
change.  Across those sampled points,

\[
 \phi\in[5.750637610334,5.968103821339],\quad
 T\in[9.611342280093,9.696095647133],
\]

and the floating shooting determinant lies in
\([140.637389352,169.675830979]\).  The sampled first-hit sign partition also
passes at all 27 points.  These are `COMPUTED/FLOAT` candidate data, not a
parameter-uniform proof.

Using outward-rounded CAPD/FILIB integration and the full certified P2b0
graph-error budgets, the multiple-shooting Krawczyk test passes at the core,
the primary point, and all 27 target-grid points.  The strict fixed-point
grid has maximum inclusion ratio `0.853476843`; every determinant interval is
positive, with the total rigorous hull contained in

\[
 [131.722152731031,179.183601709910].
\]

At the primary point the strict enclosures include

\[
\begin{aligned}
 U(T)&\in[4.925093849406,4.926040615888],\\
 \partial_\phi P\big|_{Q=0}
   &\in[29.506659410389,33.215621193618],\\
 \det D_{(\phi,T)}(P,Q)
   &\in[145.323066778614,163.621499081699].
\end{aligned}
\]

Thus the current strict core is not merely a zero-parameter toy: at each
tested fixed positive parameter it encloses a locally unique symmetric
shooting root for the actual true graph and verifies endpoint
nondegeneracy.  It does not by itself identify roots at different parameter
points as one global selected branch.

## Parameter-cell result at the primary slice

In the direct interval-cell mode, the cell

\[
 r\in[.075,.08],\quad
 a_2\in[-0.000244140625,0.000244140625],\quad
 \epsilon\in[.95,1.05]
\]

passes with inclusion ratio `0.970386526`, contraction ratio `0.477941768`,
and positive determinant interval
\([64.5333352524,249.122407663]\).  A normally sized \(a_2\) cell fails if
the same parameter is repeatedly interval-hulled across the nine segments.

The seven-dimensional affine experiment retains a common static \(a_2\)
coordinate, phase correction, and graph error through every segment and
through the Poincare map.  The source is enclosed by the first-order form

\[
 S(x)\in \bar S+Lx+R,
 \qquad
 R=(S(0)-\bar S)+\sum_j(D_jS(X)-L_j)X_j,
\]

where the interval first jet is evaluated jointly on the complete source
box.  This is the multivariable mean-value enclosure, not a floating Taylor
approximation.  It includes the nonlinear zero-energy solve and all
dependencies of the physical saddle-focus frame.  In particular,
\(h=\frac12\sqrt{4-c^2}\) is evaluated without first separating its common
\(c\)-dependence.  At the final section, the equivalent residual
\(P+\lambda Q=P\) on \(Q=0\) suppresses the dominant return-time wrapping.

For the unsplit test cell

\[
 r=2/25,\qquad a_2\in[-.03125,.03125],\qquad\epsilon=1,
\]

the zero-correction source remainder is reduced to at most
\(2.2\times10^{-6}\) (and remains below \(3.38\times10^{-6}\) on the full
shooting box), but the single-cell Krawczyk test is still inconclusive: its
maximum inclusion and contraction ratios are approximately `2.776` and
`2.119`.  The remaining loss is whole-cell shooting and phase curvature,
rather than the former source dependency loss.

Splitting only the \(a_2\) direction into four equal closed cells gives the
following outward-rounded strict results at
\((r,\epsilon)=(2/25,1)\).  The source, center orbits, and augmented flow
derive \(r^2,r^3,r^4,2r\), and \(b=r^2/3\) from the same outward enclosure
of the exact rational \(r=2/25\); no separately rounded decimal coefficient
is used.  The radius factor is `1.5` in every row.

| \(a_2\) cell | phase centre | max. inclusion | max. contraction | shooting determinant |
|---|---:|---:|---:|---:|
| \([-0.03125,-0.015625]\) | 5.8499630981148290 | 0.880601 | 0.233777 | \([81.861890,225.386008]\) |
| \([-0.015625,0]\) | 5.8567555213821878 | 0.875084 | 0.227768 | \([82.619181,226.363758]\) |
| \([0,0.015625]\) | 5.8635419626078198 | 0.872921 | 0.225132 | \([83.183986,227.554336]\) |
| \([0.015625,0.03125]\) | 5.8703224431258789 | 0.873950 | 0.225704 | \([83.550710,228.964809]\) |

All four Krawczyk images lie strictly in their shooting boxes, all four
contraction bounds are below one, the endpoint has \(U>1\), and every
determinant interval is strictly positive.  The zero-correction source
remainders are between approximately \(6.9\times10^{-8}\) and
\(1.33\times10^{-7}\); after inserting the full phase-correction and graph
error boxes, their largest source remainder is below
\(2.02\times10^{-7}\).  Hence the four parameter cells form a gap-free
existence, local-uniqueness, and endpoint-transversality cover of

\[
 r=2/25,\qquad a_2\in[-0.03125,0.03125],\qquad \epsilon=1
\]

within the declared true-graph \(C^0/C^1\) error budgets.  This resolves the
earlier affine-source obstruction and shows that the failed unsplit run was
an interval-curvature effect, not disappearance of the orbit.

## Common-face root identification

Cell \(i\) represents the physical phase and shooting nodes by

\[
 \phi=\bar\phi_i+\kappa\eta_i+\delta_i,
 \qquad
 z_n=\bar z_{i,n}+A_{i,n}\eta_i+B_{i,n}\delta_i
      +E_{i,n}e_i+\xi_{i,n}.
\]

On a common face, equality of the physical phase determines an exact affine
shift \(\delta_j=\delta_i+d_{ij}\), while \(e_j=e_i\).  Equality of every
physical node then gives the affine change

\[
 \xi_{j,n}=\xi_{i,n}+c_{ij,n}
 +(B_{i,n}-B_{j,n})\delta_i+(E_{i,n}-E_{j,n})e_i.
\]

Let \(K_i\) be the complete 38-dimensional Krawczyk image for cell \(i\),
and let \(X_j\) be the neighboring cell's proven uniqueness box.  The
implemented common-face gate checks the coordinatewise strict containment

\[
 T_{ij}(K_i)\subset\operatorname{int}X_j.
\]

This is stronger than overlap of two root boxes.  A root enclosed by
\(K_i\) is thereby placed inside a box in which cell \(j\) has exactly one
root of the same physical shooting problem, so the two roots coincide.  The
same actual P2b true-graph error function is used on both sides of the face;
the two cells do not choose independent graph errors.

Both directions pass on all three exact dyadic faces:

| common face | left to right max. ratio | right to left max. ratio |
|---:|---:|---:|
| \(-1/64\) | 0.897795 | 0.935687 |
| \(0\) | 0.890512 | 0.932416 |
| \(1/64\) | 0.887678 | 0.933968 |

Every coordinate is strictly contained; the worst case is the final-node
\(U\) correction on the face \(a_2=-1/64\).  Consequently, on the exact
slice

\[
 r=2/25,\qquad a_2\in[-1/32,1/32],\qquad\epsilon=1,
\]

the four locally unique transverse root families join into one common slice
branch.  This still does not identify that branch as the continuation of the
selected \(r=0\) core branch, because the one-dimensional slice does not
cover the full \((r,a_2,\epsilon)\) comparison bridge.

## Three-parameter affine engine

The mu-affine mode carries the three common static parameters together with
the phase correction and graph error in the nine-dimensional augmented flow

\[
 (U,P,V,Q,\delta r,\delta a_2,\delta\epsilon,\delta,e).
\]

Its source enclosure uses one joint five-column interval first jet in
\((\delta r,\delta a_2,\delta\epsilon,\delta,e)\).  All appearances of
\(\sqrt\epsilon\) and all derived coefficients \(a,b,c\) therefore retain a
single common parameter dependency.  The three parameter columns are chart
coordinates, not Newton unknowns, so the Krawczyk system remains
38-dimensional.

The following three axial cells pass with radius factor 1.5:

| parameter cell | max. inclusion | max. contraction | shooting determinant |
|---|---:|---:|---:|
| \(r\in[3/40,2/25],\ a_2=0,\ \epsilon=1\) | 0.746713 | 0.157917 | \([134.472485,173.988270]\) |
| \(r=2/25,\ a_2\in[-1/128,1/128],\ \epsilon=1\) | 0.873494 | 0.225937 | \([82.945245,226.910024]\) |
| \(r=2/25,\ a_2=0,\ \epsilon\in[19/20,21/20]\) | 0.709555 | 0.115552 | \([139.998125,169.008198]\) |

The unsplit product of these three widths is inconclusive: its inclusion and
contraction ratios are approximately 1.77803 and 1.11964, and its determinant
enclosure crosses zero.  The worst coordinate is the phase correction.  This
is a whole-cell dependency obstruction, not evidence that the orbit
disappears; all eight floating corner roots converge, and smaller
three-parameter cells pass.

## Selected core-to-primary \(r\)-spine

At \(a_2=0,\epsilon=1\), the exact rational cells

\[
 I_i=[i/200,(i+1)/200],\qquad i=0,\ldots,15,
\]

form a gap-free cover of \(r\in[0,2/25]\).  A fixed quadratic phase predictor
is used only to precondition the shooting charts.  With radius factor 1.5,
all 16 Krawczyk tests pass.  Their maximum inclusion ratios range from
0.689963 to 0.760747, their maximum contraction ratios are at most 0.172188,
and their determinant intervals have a total hull contained in

\[
 [134.15885866230818,174.27948575755255].
\]

On each of the 15 exact common faces \(r=i/200\), both directional maps of
the complete root-bearing Krawczyk enclosure into the neighboring uniqueness
box pass.  Thus all 30 full 38-dimensional face checks pass; the worst ratio
is 0.823315541.  These checks retain the same physical phase, the same graph
error value, and all nine four-dimensional shooting nodes.

The \(r=0\) point chart also passes robustly for the positive-bridge graph
budgets, with inclusion 0.665794924, contraction 0.053093769, and determinant

\[
 [140.2609204687493,158.88026879006134].
\]

The first \(r\)-cell maps into this core uniqueness box with ratio
0.952380951.  This alone would identify only an unspecified local core root,
so the scout also imports the frozen selected-root data.  Starting from the
frozen phase box

\[
 [5.8615055856447817,5.8615055856450482]
\]

and the frozen core true-graph value error \(10^{-20}\), it rigorously
propagates the source to all nine shooting times and expresses the result in
the present 38-dimensional core chart.  The imported enclosure lies in the
interior of the core uniqueness box with maximum coordinate ratio
\(4.23052\times10^{-8}\).  The phase convention agrees pointwise by the
already validated P2bK core-face identity, and the H10 table is the same
frozen object.

Consequently, at design-scout status, the 16 locally unique transverse roots
on

\[
 a_2=0,\qquad\epsilon=1,\qquad r\in[0,2/25]
\]

are one common physical branch and that branch is the continuation of the
frozen selected core homoclinic.  The full parameter-box computation below
extends this selected branch off the spine.

## Full three-parameter selected-branch cover

The strict design kernel covers

\[
 B_0=[0,2/25]\times[-1/4,1/4]\times[4/5,6/5]
\]

by the exact rational cells

\[
 \begin{aligned}
 R_i&=[i/400,(i+1)/400],&0\le i<32,\\
 A_j&=[(j-64)/256,(j-63)/256],&0\le j<128,\\
 E_k&=[(8+k)/10,(9+k)/10],&0\le k<4.
 \end{aligned}
\]

Thus 16,384 closed cells cover \(B_0\) without gaps.  The fitted phase chart
used at their centers is only a floating preconditioner: the phase correction
remains one of the interval unknowns in every Krawczyk problem.  With
shooting-box radius factor \(3\), all 16,384 cells pass.  The worst inclusion ratio is
0.8116307051006466 and the worst contraction ratio is 0.48505318768286615,
both in

\[
 [31/400,2/25]\times[-1/4,-63/256]\times[4/5,9/10].
\]

The Krawczyk inclusions and contraction bounds give existence and local
uniqueness in every root box.  The endpoint shooting-determinant intervals
over all cells have total hull

\[
 [35.18937930508395,287.4889566796052].
\]

The strictly positive determinant intervals, together with the checked
endpoint phase-column and nonzero-endpoint gates, record endpoint
transversality throughout the design cover.  Every internal common face also
passes the root-enclosure-to-neighbor-uniqueness-box test:

| face normal | passed / total | worst containment ratio |
|---|---:|---:|
| \(a_2\) | 16,256 / 16,256 | 0.8446835766577023 |
| \(\epsilon\) | 12,288 / 12,288 | 0.8310863705829250 |
| \(r\) | 15,872 / 15,872 | 0.8357241454291467 |

These 44,416 tests use the same actual P2bK \(C^2\) true-source family
satisfying the uniform graph budgets, and represent each physical parameter
on a common face by one shared outward-rounded interval variable, rather than
evaluating the same parameter twice as independent intervals.  One directed
inclusion per face is sufficient: for each fixed parameter value on the face,
the source root lies
in the source Krawczyk image; the face-coordinate transform of that image
lies in the neighboring uniqueness box; and the neighboring box has exactly
one root.  Hence the two local root sections agree pointwise on the shared
face.  Connectivity of the grid identifies all cellwise roots as one branch.
More precisely, the cell boxes and their chart reconstructions form a finite
parameter-following lifted 38-dimensional multiple-shooting tube.  For every
fixed parameter and every actual P2bK true-graph error function satisfying the
certified budgets, the Krawczyk argument gives exactly one physical zero
record represented in this tube.  No tube-exterior uniqueness is claimed: a
direct-shooting zero whose intermediate-node record leaves the lifted tube is
not excluded, even if its \((\phi,T)\)-projection lies in a larger shooting
box.

The corner \((r,a_2,\epsilon)=(0,0,1)\) is anchored separately.  The frozen
selected core enclosure maps into a point-core uniqueness box with ratio
\(7.95637\times10^{-7}\); the point-core Krawczyk test passes with inclusion
0.726100604 and contraction 0.726100285; and its root enclosure maps into the
adjacent grid-cell uniqueness box with ratio 0.333117151.  The already
validated P2bK complete-anchor-face identity and local true-graph uniqueness
use these same coordinates.  At \(r=0\) the desingularized central shooting
problem is independent of the dummy \(a_2,\epsilon\) coordinates, so the
glued root section is exactly the frozen core root on the entire \(r=0\)
face.  This supplies an anchor for the connected grid; it does not interpret
\(r=0\) as an additional physical positive-\(d\) PDE parameter.

The strict run is bound to repository source commit
`2c60e4930bb585a24d7a8945c1b5b3e7469a1cf8`, CAPD commit
`731079217a9254ea2948d742df2b170895effe7f`, and the frozen H10 table named
below.  It used the strict flags `-fno-fast-math`, `-frounding-math`,
`-ffp-contract=off`, `-fno-tree-vectorize`, and `-fno-ipa-pure-const`.
The executable SHA-256 was
`46cc65468a7082f5adaa5902d76c962ead8a123653f3bfd39959769650ee63dc`;
the fixed-order concatenation of the anchor summary followed by slab summaries
0 through 31 had SHA-256
`73afc5b9a365ea7ab505095feb7098154a0ab5f83cfe7c6dbd0e8788a275e364`.
These bindings make the design result locally auditable and reproducibly
bound, but they are not a frozen machine-readable P2c certificate or an
independent replay.

## Full selected source-to-symmetry-event first-hit cover

At source commit `25ff53a7f4fa2457a09767d2cad992aff245bcea`, the strict
first-hit mode was run on the same exact \(32\times128\times4\) grid with
shooting-box radius factor `3`.  For every cell it first reconstructs an
affine nine-dimensional CAPD set from the root-bearing Krawczyk enclosure
\(K\), retaining the same three parameter coordinates, phase correction, and
true-graph scalar error.  It then checks the outward continuous-time
enclosure returned after every internal CAPD step, rather than checking only
sampled endpoints.  All 16,384 out of 16,384 cells pass, comprising 306,287
dense internal steps; each of the 32 fixed-\(r\) slabs reports 512 out of 512
passing cells.

The source-to-final-node sign partition and the global strict hulls are:

| nominal time interval | required sign | global strict hull | signed margin | worst grid cell \((i,j,k)\) |
|---|---:|---:|---:|---:|
| \([0,1.55]\) | \(P>0\) | \([0.0003775768276043477,0.01702678138346261]\) | 0.0003775768276043477 | \((31,127,0)\) |
| \([1.55,1.90]\) | \(Q>0\) | \([0.028827241320954836,0.03775272909037046]\) | 0.028827241320954836 | \((31,0,3)\) |
| \([1.90,7.35]\) | \(P<0\) | \([-0.45162005597156318,-0.0028529044239452655]\) | 0.0028529044239452655 | \((31,0,3)\) |
| \([7.35,9.55]\) | \(Q<0\) | \([-3.3579979633164085,-0.26930389071300026]\) | 0.26930389071300026 | \((31,127,0)\) |
| \([9.55,9.55+1/5]\) | \(U>0\) | \([4.6910804196918061,5.1507399310104942]\) | 4.6910804196918061 | \((31,0,0)\) |

At both switching times the implementation continues the same CAPD set: the
set used to verify \(Q>0\) through time 1.90 is then used to verify
\(P<0\), and the set used to verify \(P<0\) through time 7.35 is then used
to verify \(Q<0\).  Thus the displayed endpoints conceal no unchecked time
seam.

Here \((i,j,k)\) denotes the \((r,a_2,\epsilon)\)-cell indices from the
exact grid above.  Thus the two recurring worst cells are

\[
 \begin{aligned}
 (31,127,0)&:\quad [31/400,2/25]\times[63/256,1/4]
                    \times[4/5,9/10],\\
 (31,0,3)&:\quad [31/400,2/25]\times[-1/4,-63/256]
                    \times[11/10,6/5],
 \end{aligned}
\]

while the worst final-flow-box margin occurs on
\([31/400,2/25]\times[-1/4,-63/256]\times[4/5,9/10]\).
The complete physical-state hull accumulated over all five tubes is

\[
 \begin{aligned}
 U&\in[-1.2754209644411874,5.1507399310104942],\\
 P&\in[-2.2821367541046569,6.3575562290451844],\\
 V&\in[-8.2282751545401851,0.15319307702947269],\\
 Q&\in[-3.3579979633164085,0.71646821916526104].
 \end{aligned}
\]

Starting from the final node at time 9.55, the outward final duration is
\([0.19999999999999998,0.20000000000000001]\).  The selected \(Q=0\)
Poincare return-time hull is

\[
 [0.05509623487633783,0.15246186152197719],
\]

strictly below the left endpoint of that duration, and the corresponding
half-time hull is

\[
 [9.6050962348763385,9.7024618615219786].
\]

The four consecutive sign tubes prevent \(P=Q=0\) from the selected source
through time 9.55.  In the final tube, \(Q'=U>0\), the initial \(Q\) is
strictly negative, and the selected root has \(Q=0\) and \(P=0\) at its
Poincare event.  The return-time bound places that event strictly inside the
\(U>0\) tube, where strict monotonicity of \(Q\) makes its zero unique.  This
is a one-dimensional final flow-box argument for the already selected root;
it does not replace the codimension-two symmetry condition by a scalar
section.  Before the source face, the imported P2a/P2bK true-graph estimate
and backward decay exclude a nonzero symmetry hit: on the radius-\(1/100\)
graph disk, the physical frame gives
\(P=Q=0\Rightarrow u=s=H_\mu(u)\), whereas
\(\|H_\mu(u)\|<\frac14\|u\|^2\) excludes this equality for
\(0<\|u\|\le1/100\).  This imported local gate was not reevaluated by the
first-hit CLI.  Together, the imported pre-source gate and the full-grid
dense tubes complete the no-earlier-symmetry-hit argument at strict design
level.

The first-hit run is bound to source commit
`25ff53a7f4fa2457a09767d2cad992aff245bcea`; the SHA-256 of
`p2c_homoclinic_multishoot_scout.cpp` at that commit is
`3aa6368471ced8afc37e73128149548e7756caa04505ebcb615a3451bf6beabd`.
It used CAPD commit `731079217a9254ea2948d742df2b170895effe7f` and the same
strict compiler flags listed above, together with the frozen H10 input bound
below; the flagship working tree was not an input.  The executable SHA-256 was
`b6d27a618146ea90db1310c1f0b510190a573b35bd8d5d669f5e354d6f6f0fd0`;
the fixed numeric-order concatenation of slab logs 0 through 31 had SHA-256
`09f3e809b4651a3ed8dfc5482b9900aadf35367b08202dbc17a3a79af5f6b5f3`.
These hashes bind the completed strict design run, but do not promote it to a
frozen machine-readable certificate or policy replay.

## Actual selected-root parameter two-jets

The root-jet mode differentiates the actual 37-dimensional residual whose
unknowns are the absolute P2bK source phase and the nine physical shooting
nodes.  It does not differentiate the quadratic phase predictor used to
centre the boxes.  The three external variables are

\[
 \theta_r=25r-1,\qquad \theta_a=4a_2,\qquad
 \theta_\epsilon=5(\epsilon-1).
\]

The field is augmented by these three constant variables.  CAPD (C^2)
flow and Poincare maps enclose the complete first and second residual jets.
CAPD stores normalized Taylor coefficients, so the implementation multiplies
only diagonal Hessian coefficients by two; mixed coefficients are already
the actual mixed derivatives.  For each parameter direction and symmetric
pair, the implicit first- and second-derivative equations are solved with the
same interval inverse gate.  Positive diagonal weights choose the norm, but
the final weighted contraction and every componentwise strict solve
inclusion are recomputed with interval arithmetic.

With shooting radius factor (3), all (16{,}384/16{,}384) cells pass.  The
global strict hulls are

\[
 \phi_h\in[5.7499112495191298,5.9687447739269208],
\]

\[
 T_h\in[9.6050962330163951,9.7024614326336689],\qquad
 T_{\rm return}\in[0.055096233016395574,0.15246143263366643].
\]

The worst weighted inverse contraction is
`0.23585865367990907` at cell ((31,0,0)).  The unweighted diagnostic can be
as large as `2.305500383584993`; it is not the proof norm.  The worst strict
componentwise solve inclusion is `0.99868362757418572` at ((31,127,0)),
still below one.  The event has the uniform lower bound
(U\ge4.8357887375448962), so the same (Q=0) event remains transverse.

Uniform componentwise absolute bounds for the derivatives of
((\phi_h,T_h)) are:

| derivative | (\theta_r) | (\theta_a) | (\theta_\epsilon) |
|---|---:|---:|---:|
| (D\phi_h) | 0.716655010 | 0.774508400 | 0.654720583 |
| (DT_h) | 0.962690243 | 0.980647712 | 0.909346129 |

| second derivative | (rr) | (ra) | (r\epsilon) | (aa) | (a\epsilon) | (\epsilon\epsilon) |
|---|---:|---:|---:|---:|---:|---:|
| (D^2\phi_h) | 13.013242 | 13.817020 | 12.193663 | 14.631550 | 12.946996 | 11.300571 |
| (D^2T_h) | 36.415307 | 37.992701 | 34.857794 | 39.532881 | 36.394716 | 32.579159 |

Exact squared comparisons of the binary64 upper endpoints give the short
rational bounds

\[
 \|D\phi_h\|_2\le\frac{621}{500},\quad
 \|DT_h\|_2\le\frac{206}{125},\quad
 \|D^2\phi_h\|_F\le\frac{39059}{1000},\quad
 \|D^2T_h\|_F\le\frac{109163}{1000}.
\]

The full-grid run is bound to source commit
`0f35363264d29a8b4b3b39ab10317273aff35fab`, source SHA-256
`d3fe590fd64da02e18941d32e8d43a3b50e018f37d59513e37a41d1d32cf7a2f`,
strict executable SHA-256
`b7235063abff295b0d0e51a0587e5c8dd871af35a1c5d4af7a060e3e6cde0f04`,
CAPD commit `731079217a9254ea2948d742df2b170895effe7f`, and the frozen H10 header
listed below.  The fixed numeric-order concatenation of slab logs 0 through
31 has SHA-256
`b503e777183e6a5f759978b081828b70119bbfb95f48e643649857a89cace969`.
The exact binary endpoint summary consumed downstream is
[`design/p2c_root_jet_summary_v1.json`](design/p2c_root_jet_summary_v1.json).

## Explicit weight-one-fifth infinite tails

Write (p=\phi_h), (T=T_h),

\[
 b_s(\theta)=R R_{\chi(\theta)}(\cos p(\theta),\sin p(\theta)),
 \qquad \tau(\theta)=T(\theta)-11,
\]

and let (Z(\theta,b,t)) be the already certified P2b moving-coordinate
unstable half-orbit.  Since (T^+<10), one has (\tau<-1).  The P2b weight
is (\omega=1/4), and

\[
 e^{-1/4}<\frac45
\]

follows strictly from (e^{1/4}>1+1/4).  Hence, with (Z_{ij}) denoting
the archived P2b weighted jets,

\[
 A_{ij}:=\frac45Z_{ij},\qquad
 b_-(\theta)=\pi_u Z(\theta,b_s(\theta),\tau(\theta))
\]

satisfies (|b_-\|\le0.008000000000000004<R=0.01).  Thus it lies strictly
inside the same certified local disk.

Let (p_1,p_2,t_1,t_2) be the four rational root-jet bounds above, and let
(B_1,B_2) be the P2bK fixed-phase source-coordinate bounds.  The phase
composition gives

\[
 s_1\le B_1+Rp_1,\qquad
 s_2\le B_2+2B_1p_1+R(p_1^2+p_2).
\]

If (L=1+L_{10}), then

\[
 f_0=LA_{00},\quad
 w_\theta=L_{11}A_{00}+LA_{01},\quad
 w_b=LA_{10},\quad
 w_t=Lf_0.
\]

The full second-order chain rule is bounded by

\[
\begin{aligned}
 B^-_0={}&A_{00},\\
 B^-_1={}&A_{01}+A_{10}s_1+f_0t_1,\\
 B^-_2={}&A_{02}+2A_{11}s_1+A_{20}s_1^2+A_{10}s_2\\
 &+2(w_\theta+w_bs_1)t_1+w_tt_1^2+f_0t_2.
\end{aligned}
\]

The exact-fraction scout obtains

\[
 (B^-_0,B^-_1,B^-_2)
 \le(0.00800001,0.0245290,1.310289).
\]

Composing with the archived physical half-orbit bounds (P_{ij}) gives

\[
 K_0=P_{00},\quad
 K_1=P_{01}+P_{10}B^-_1,
\]

\[
 K_2=P_{02}+2P_{11}B^-_1+P_{20}(B^-_1)^2+P_{10}B^-_2,
\]

with

\[
 (K_0,K_1,K_2)
 \le(0.0400600,0.106816,5.655330).
\]

Choose (T_*=11) and (eta=1/5<1/4).  The exact integer comparison
(5^{11}<27\,4^{11}), together with
(e^{1/5}<1/(1-1/5)=5/4), proves (e^{11/5}<27).  Therefore both tails
satisfy

\[
 \sup_{|\xi|\ge11}e^{|\xi|/5}
   |D_\theta^j\Gamma_\theta(\xi)|
 \le C_j^{(\theta)},\qquad |j|=0,1,2,
\]

where

\[
 (C_0^{(\theta)},C_1^{(\theta)},C_2^{(\theta)})
 \le(1.081619,2.884016,152.693890).
\]

Since (D_\mu=(25,4,5)D_\theta) componentwise, the coarse operator
conversion gives

\[
 (C_0^{(\mu)},C_1^{(\mu)},C_2^{(\mu)})
 \le(1.081619,72.100399,95433.681137).
\]

Thus the single integer (C_{\rm tail}=95434) is valid for all derivatives
through order two on both infinite tails.  The positive tail has the same
constants because the reverser is a fixed Euclidean isometry.  This closes
the design-level `V2.HOM.TAILS` atom as it is scoped in
[`P2_VALIDATION_CONTRACT.md`](P2_VALIDATION_CONTRACT.md); it is not yet the
single global constant in Theorem V2(11).

The algebraic computation is
[`design/p2c_tail_composition_scout.py`](design/p2c_tail_composition_scout.py)
at commit `53292dd93a26b901d3395400389cd37faa6b7826`.  It uses exact nonnegative
`Fraction` arithmetic and no additional ODE integration.  The script,
root-summary input, and canonical JSON output have SHA-256 values
`e6a9a7ea6373939d010dcd67466587268f3410571534829f976d342fbb2d040c`,
`13e5c345a8c762c707ae19455ca67510e587a97c526f718f175e59da2657d2fd`,
and `f14cae57be56a668a87097c59fd2ced85347720fb28d6e840b3d75d8786f6af1`,
respectively.

## Proof boundary

The following remain open and are not consequences of the results above:

- a continuous-time parameter-(C^2) enclosure on the finite middle
  \([-11,11]\).  The true-root calculation encloses the phase, time, and
  shooting-node jets, while the tail calculation encloses both infinite
  tails.  It does not yet provide one numerical bound for every intermediate
  time in the compact middle, so Theorem V2(9)--(11) must not yet be reported
  as a fully explicit global weighted bound;
- a frozen P2c configuration, machine-readable certificate and checker, and
  eventually the policy-required independent replay.  The latter is a
  release gate, not the current computational priority.

In particular, the selected-source first-hit design is no longer an open
item, and exclusion of zeros outside the declared lifted multiple-shooting
tube is not part of the proved uniqueness statement.

The H10 table used in the strict rerun was materialized with `git archive`
from the frozen flagship commit
`d54add098545063d5efe8f1d6f062d4cfc116a0d`; its SHA-256 is
`d617587ea1b9037c1c7575ccdde5029529ec5b736dee259baff9a2a162001e96`.
The imported symmetric-core certificate at the same commit has SHA-256
`ed0f9f58f8ba5f1d5c36dc7c3a72bb725599c4172a3cd610d890b88699fecfbd`.
The flagship working tree was not an input and was not modified.
