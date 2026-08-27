# Issue #7 P2c selected-homoclinic scout report

**Evidence status: strict design-scout results plus floating candidate data.**
This report does not mark `V2.HOM.BRANCH`, `V2.HOM.FIRST_HIT`,
`V2.HOM.TRANSVERSE`, or `V2.HOM.TAILS` as passed.  It records the
completed feasibility work and the remaining steps between the present
one-parameter slice and the full P2c claim.

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

## Proof boundary

The following remain open and are not consequences of the results above:

- a gap-free three-parameter cover connecting the slice branch to the
  complete `r=0` anchor face, hence identification of the selected branch on
  the full comparison bridge;
- exclusion of any other zero in the fixed larger shooting sub-box;
- the no-earlier-symmetry-hit sign tubes and final flow box;
- explicit first and second parameter bounds for \((\phi_h,T_h)\), needed
  to compose the already certified P2b weighted half-orbits into the full
  weight-\(1/5\) homoclinic tail estimate.

The H10 table used in the strict rerun was materialized with `git archive`
from the frozen flagship commit
`d54add098545063d5efe8f1d6f062d4cfc116a0d`; its SHA-256 is
`d617587ea1b9037c1c7575ccdde5029529ec5b736dee259baff9a2a162001e96`.
The flagship working tree was not an input and was not modified.
