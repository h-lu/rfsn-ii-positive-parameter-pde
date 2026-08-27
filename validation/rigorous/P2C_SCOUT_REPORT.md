# Issue #7 P2c selected-homoclinic scout report

**Evidence status: strict design-scout results plus floating candidate data.**
This report does not mark `V2.HOM.BRANCH`, `V2.HOM.FIRST_HIT`, or
`V2.HOM.TAILS` as passed.  It records the completed feasibility work and the
single remaining obstruction found when enlarging a parameter cell.

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

## Parameter-cell diagnosis

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

The completed seven-dimensional affine experiment retained a common static
\(a_2\) coordinate, phase correction, and graph error through every segment
and through the Poincare map.  The CAPD affine-set construction worked.  For
the normal test cell

\[
 r=.08,\qquad a_2\in[-.03125,.03125],\qquad\epsilon=1,
\]

the experiment remained inconclusive because the initial nonlinear source
was enclosed as `natural interval - affine hull`.  That operation produced
source remainders of order \(10^{-4}\), a base event residual about
\([-0.1644,0.1632]\), and a phase-correction box about
\([-0.1097,0.1097]\).  The final Poincare input then had an `U` enclosure
containing zero, so CAPD correctly rejected the crossing.  This is a
wrapping diagnosis, not evidence that the homoclinic branch fails to exist.

The next mathematical step, when work resumes, is a rigorous first-order
source expansion with a second-order parameter remainder.  Only after that
should the affine cell be enlarged and a gap-free cover attempted.

## Proof boundary

The following remain open and are not consequences of the results above:

- common-face containment connecting every cell to the complete `r=0`
  anchor, hence identification of one selected branch;
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
