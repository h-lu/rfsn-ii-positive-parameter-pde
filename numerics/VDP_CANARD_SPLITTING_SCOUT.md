# Fixed-parameter canard splitting scout

## Outcome

At

\[
 (r,\epsilon)=(0.08,1),\qquad a_2\in[-1/80,0],
\]

the proposed reversible splitting is numerically usable as a **candidate
generator**, but the current data do not define the finite-parameter maximal
canard.  The result is therefore

```text
COMPUTED/E1_SURROGATE_SPLITTING_SCOUT
GO_FOR_CANDIDATE_GENERATION_ONLY
INCONCLUSIVE_MISSING_INVARIANT_SLOW_MANIFOLD_ENTRY
```

In particular, this scout neither classifies the sample \(a_2=0\) nor connects
the frozen high-winding target to a canard.

## The tested scalar splitting

For \(\epsilon=1\), the exact central-chart field is

\[
 u'=p,\qquad
 p'=u^2-v+\frac{r^2}{3}u^3,\qquad
 v'=q,\qquad
 q'=u-ra_2,
\]

with Hamiltonian

\[
 H_2=\frac12(p^2-q^2)+(u-ra_2)v-\frac13u^3-\frac{r^2}{12}u^4.
\]

The intended eventual construction starts on the selected zero-energy trace
of the outer saddle slow manifold, flows toward the fold, and defines

\[
 S(r,a_2)=q\quad\hbox{at the first hit of }\{p=0,\ p'>0\}.
\]

If the entry really lies on the selected invariant branch, \(S=0\) means that
the orbit reaches \(\operatorname{Fix}\mathcal R=\{p=q=0\}\).  Reversibility
then supplies the matching half.  This implication is the reason the scalar
is useful; the present scout does not yet provide its invariant entry.

Instead, the code takes the formal algebraic-canard jet from Appendix C of the
published [Vo--Doelman--Kaper paper](https://doi.org/10.1137/24M1690722)
(Appendix E in arXiv v1), sets its free formal phase parameters to zero,
truncates at order \(r^2\) or \(r^3\),
and changes only \(q\) to impose the exact equation \(H_2=0\).  This is the
energy level imposed in the published canard-coincidence calculation; when
\(a_2\ne0\), it is not the energy of the homogeneous equilibrium and is not
a homoclinic-energy condition.  From the resulting point at central time
\(y=-Y\), it integrates the exact field and
records

\[
 S_Y^{[m]}(a_2)=q\big|_{\text{first increasing }p=0}.
\]

Thus \(S_Y^{[m]}\) is a surrogate splitting attached to a stated formal-entry
convention, not the splitting of a computed finite-\(r\) slow manifold.

## Numerical result and the no-go diagnostic

The published leading value in the repository scaling is

\[
 a_{2,c}^{\rm lead}=-\frac{5r}{48}=-\frac1{120}
 =-0.008333333333\ldots .
\]

All eight combinations \(Y=1,2,3,4\) and \(m=2,3\) have a floating-point
simple surrogate zero inside the frozen interval, as indicated by a nonzero
centered finite-difference slope.  For the order-three rows with
\(Y=1,2,3\), the roots are approximately

| \(Y\) | order-three surrogate root | \(\partial_{a_2}S_Y^{[3]}\) |
|---:|---:|---:|
| 1 | \(-0.0083348245\) | \(2.30\times10^{-1}\) |
| 2 | \(-0.0083607939\) | \(9.81\times10^{-3}\) |
| 3 | \(-0.0083671331\) | \(-2.26\times10^{-2}\) |

Their descriptive range has width about \(3.23\times10^{-5}\), and every
first hit has \(p'>0.166\).  This shows that exact integration, event
selection, and scalar root finding are computationally feasible.

It does **not** provide an error estimate.  The entry-curve invariance defects
are between roughly \(10^{-6}\) and \(10^{-5}\), the derivative even changes
orientation across the comparison sections, and the order-three \(Y=4\)
root moves to approximately \(-0.00969\).  These effects are larger than a
legitimate finite-parameter canard claim can tolerate.  They arise because a
finite formal jet, even after exact energy projection, is not the selected
finite-(r) invariant slow manifold.  A small entry error is amplified while
following a saddle slow branch.

Consequently the scout records a useful candidate cluster but leaves all of
the following `INCONCLUSIVE`:

- existence and local uniqueness of a finite-parameter coincidence root;
- an enclosure of the \(O(r^3)\) remainder in \(a_{2,c}(r)\);
- whether \(a_2=0\) lies off the true coincidence curve;
- connection or separation of the preregistered high-winding orbit.

## Next mathematical object

The next step is not another formal order or a denser root grid.  It is a
branch-identified finite-\(r\) saddle-slow zero-energy trace on a fixed,
normally hyperbolic entry section, including its \(a_2\)-derivative.  The same
first-hit map can then define the genuine splitting.  Only after that object
exists should the scalar root be continued in (r) or enclosed with interval
arithmetic.

The first finite-boundary implementation of that step is now recorded in the
[A.2 slow-trace report](VDP_CANARD_SLOW_TRACE.md).  It replaces the projected
jet with collocation solutions of the exact finite-\(r\) Appendix-A.2 field
and imposes zero energy in a numerically reversible BVP candidate.  The
candidate fails the frozen central-branch localization
diagnostic, however, and the A.2 finite boundary has not been replaced by an
intrinsic slow-sheet graph.  Thus it is a boundary-selected coincidence
candidate, not completion of C1 or C2.

Issue #13's high-winding comparison remains separately blocked until the
frozen numerical return target is identified as the exact intended
\((+,2,+)\) branch.  No substitute edge is used here.

## Reproduction

```bash
python3 -B numerics/vdp_canard_splitting_scout.py
python3 -B -m unittest numerics.test_vdp_canard_splitting_scout -v
```

The machine-readable result is
`numerics/results/vdp_canard_splitting_scout/fixed_r_report.json`.
