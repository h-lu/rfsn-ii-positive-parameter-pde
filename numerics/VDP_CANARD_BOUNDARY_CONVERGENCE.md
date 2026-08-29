# Three-boundary finite canard comparison

## Outcome

This floating experiment predeclared the Appendix-A.2 outer boundaries

\[
q_0=-60,-80,-100
\]

at \((r,\epsilon)=(0.08,1)\).  It reused the existing primary no-loop A.2
continuation and, without changing boundaries after the run, applied the same
A.3-compatible zero-energy reversible half-BVP to each returned outer pair
\((u_*,q_*)\).  The status is
`COMPUTED/E1_PARTIAL_THREE_BOUNDARY_SCOUT`, not a maximal- or intrinsic-canard
claim.

The \(q_0=-60\) slice failed during the frozen A.2 continuation at
\(u_2=14\): the collocation solver exceeded its 220,000-node limit.  It was
not retargeted.  The other two slices succeeded:

| \(q_0\) | \(u_*\) | \(a_{2,c}\) | A.3 residual | no-loop/localized |
|---:|---:|---:|---:|:---:|
| \(-80\) | 16.6450833648 | -0.00833819526706 | \(1.9984\times10^{-8}\) | yes/yes |
| \(-100\) | 19.2773562135 | -0.00833693853356 | \(1.9648\times10^{-8}\) | yes/yes |

Both candidates cross the common section \(u_2=16\).  Their entries are

\[
\begin{aligned}
q_0=-80:&\quad
(16,-2.2342799685,264.6174070084,-75.3162022872),\\
q_0=-100:&\quad
(16,-2.2387535662,264.5910034000,-75.3107252231).
\end{aligned}
\]

The entry difference in max norm is \(2.64036\times10^{-2}\), while the
critical-parameter difference is \(1.25673\times10^{-6}\) and the reverser
endpoint difference is \(1.01969\times10^{-7}\).  These are one finite-cut
comparison only.  Since the \(-60\) slice is missing, there is no three-point
sequence from which to diagnose decreasing successive differences; the
convergence status remains `NOT_TESTED_MISSING_SLICE`.

## Splitting derivative

For each successful outer pair, a fixed-\(a_2\) BVP was defined by keeping
the left zero-energy boundary and terminating at \(p_2=0\), with
\(S(a_2)=q_2\) at that endpoint.  Symmetric resolves were attempted at
\(a_{2,c}\pm2\times10^{-5}\) and
\(a_{2,c}\pm10^{-5}\).  All eight perturbed collocation problems stopped with
a singular Jacobian, so no derivative value is reported.  The formal jet is
used only by the pre-existing central-localization diagnostic; it is never
used as an entry replacement.

Thus the actual new information is limited but useful: the \(-80\) and
\(-100\) finite-boundary candidates are close in \(a_{2,c}\) and at their
reverser endpoints, but their common-section entries have not stabilized to
the same accuracy, the third slice failed, and the local splitting graph has
not been shown to be well posed.

The frozen configuration is
[`vdp_canard_boundary_convergence_v1.json`](config/vdp_canard_boundary_convergence_v1.json),
the computation is
[`vdp_canard_boundary_convergence.py`](vdp_canard_boundary_convergence.py),
and the saved data are
[`report.json`](results/vdp_canard_boundary_convergence/report.json).

```bash
python3 -B numerics/vdp_canard_boundary_convergence.py \
  --output /tmp/vdp-canard-boundary-convergence.json
python3 -B -m unittest numerics.test_vdp_canard_boundary_convergence -v
```
