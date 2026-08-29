# P2e v2 thick source-patch census

At the frozen interior point

\[
 (r,a_2,\epsilon)=(3/200,0,1),
\]

this retained run thickens the three previous `nu=0` carrier scouts in the
same finite-horizon nonlinear-\(W^u\), Kato-compatible numerical source
coordinates.  It computes 100 actual zero-energy source points: 20 frozen
phases times the five transverse values

```text
-8e-6, -4e-6, 0, 4e-6, 8e-6.
```

The configuration, grid, thresholds, and no-retry rule were committed before
the retained run.  The evidence class is `COMPUTED/E1_QA_NON_RIGOROUS`; these
coordinates are not identified with the proof-bound exact Moser chart.

## Result

Every source construction and every resolved event passed its predeclared
floating QA gate.  There were no source failures, integration guards, or
unresolved trajectories.  The actual first-event count is

| first event | count |
|---|---:|
| algebraic carrier `U=-4`, `P<0`, `Q<0` | 40 |
| pole carrier `x=-U=10` | 59 |
| local-block `B.RET` candidate | 1 |

The rows below are ordered by increasing source phase and the columns by
increasing \(\nu\).  `A`, `P`, and `R` mean algebraic, pole, and return.

```text
algebraic patch A
phase offset   -8e-6 -4e-6 0 +4e-6 +8e-6
-1/25           A     A   A   A     A
-1/50           A     A   A   A     A
-1/100          A     A   A   A     A
0               P     P   A   A     A
+1/200          P     P   P   P     P
+1/100          P     P   P   P     P
+1/50           P     P   P   P     P
+1/25           P     P   P   P     P

homoclinic patch H
phase offset   -8e-6 -4e-6 0 +4e-6 +8e-6
-1/500          P     P   P   P     P
-1/1000         A     A   P   P     P
-1/2000         P     A   A   P     P
0               A     A   R   A     A
+1/2000         A     A   A   P     A
+1/1000         A     A   A   A     A
+1/500          A     A   A   A     A

pole patch P
all 25 entries are P.
```

The unique sampled return is precisely the selected homoclinic center
`(phase offset,nu)=(0,0)`.  It reaches the incoming candidate at time
`19.2759361067`, with

\[
 \rho_s=10^{-2},\qquad
 \rho_u=1.28580067\times10^{-5},\qquad
 \dot\rho_s=-7.03210735\times10^{-3}.
\]

After reflection and inversion in the same numerical source chart, its
stable label is

\[
 c_{\rm stable}=-2.87\times10^{-13},
\]

with zero stored reconstruction defect.  Across all 100 trajectories, the
largest source-energy defect is `1.19e-16`, the largest source \(\nu\)
round-trip defect is `1.19e-20`, the largest sampled Hamiltonian drift is
`2.73e-12`, the smallest absolute selected-event speed is `7.03e-3`, and the
largest hit residual is `6.93e-14`.

## Interpretation

The pole patch is a robust sampled two-dimensional pole aperture on this
finite grid.  The algebraic patch shows a single resolved outcome boundary
whose location changes with \(\nu\).  The much finer homoclinic patch contains
several alternating algebraic/pole brackets and only the central return
sample.  This is the expected numerical signature of a thin high-winding
return geometry: a one-dimensional centerline picture is not enough to infer
a two-sided return band.

This computation is therefore a genuine two-dimensional candidate generator
for the later carrier and incidence boxes.  It is **not** an exhaustive source
circle, an interval enclosure of any displayed cell, a proof that the
alternations persist between samples, a numerical \(m_0\), or
`V2.EVENT_ATLAS`.  In particular, the result remains
`mathematical_status=INCONCLUSIVE` and `claim_bearing=false`.

```bash
python3 -m numerics.vdp_p2e_source_patch_census
python3 -m unittest numerics.test_vdp_p2e_source_patch_census -v
```
