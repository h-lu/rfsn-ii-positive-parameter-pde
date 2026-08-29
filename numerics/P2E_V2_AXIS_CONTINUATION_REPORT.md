# Seven-point v2 axis continuation

The energy-preserving matched solve was repeated at the fixed center and the
six axial endpoints of

\[
 [0.01,0.02]\times[-0.25,0.25]\times[0.8,1.2].
\]

Every run kept `U=-4`, `r1=2`, `Q_label=100`, `Q_end=200`, the same reduced
equations, and the centerline QA thresholds.  The center phase was the default
predictor.  The negative `a2` endpoint used the symmetric secant predictor
from the already successful center and positive `a2` endpoint; this changed
only the Newton initial value, not a target or acceptance threshold.

The narrow phase bracket stored by the original one-point scout is recorded
at every endpoint but is not used as an axis acceptance test: phase is a
solved output, and that bracket froze only the center calculation's Newton
initialization.  In particular, the two `a2` endpoint phases naturally lie on
opposite sides of it while retaining the same algebraic first-hit orientation.

All seven centerlines pass:

| point | algebraic phase | H | solver residual | six-row BC | min outer pi |
|---|---:|---:|---:|---:|---:|
| center | 5.7567672233 | 1.65e-14 | 9.90e-7 | 1.47e-12 | 1.369e-4 |
| r=0.01 | 5.7567250999 | -2.41e-14 | 9.91e-7 | 4.82e-13 | 6.086e-5 |
| r=0.02 | 5.7568261835 | 2.28e-15 | 9.92e-7 | 1.38e-12 | 2.434e-4 |
| a2=-0.25 | 5.7350866190 | 8.68e-14 | 9.90e-7 | 1.55e-12 | 1.369e-4 |
| a2=0.25 | 5.7783800372 | -9.11e-14 | 9.90e-7 | 6.71e-13 | 1.369e-4 |
| epsilon=0.8 | 5.7567592191 | -3.92e-15 | 9.99e-7 | 5.61e-13 | 1.206e-4 |
| epsilon=1.2 | 5.7567744594 | -7.58e-15 | 9.93e-7 | 1.41e-13 | 1.518e-4 |

Across all points, the central energy is below `7e-14`, the resolved-`K1`
energy-equation residual is `3.56e-15`, the outer energy residual is below
`1.12e-16`, the full central--`K1` seam is below `5.5e-12`, and the
independent same-section residual is below `1.7e-21`.  All `Pi`, `q1`, and
outer `pi` margins are positive.

The scalar diagnostic order

\[
 \phi_{\rm algebraic}<\phi_{\rm homoclinic}<2\pi-0.2
\]

holds at all seven points.  The algebraic-to-homoclinic gaps range from
`0.10337` to `0.10603`; the homoclinic-to-pole-left proxy gaps range from
`0.20143` to `0.24208`.  These are sampled scalars, not event faces.

Paired endpoint differences at the center are:

| derivative proxy | r | a2 | epsilon |
|---|---:|---:|---:|
| source phase | 1.01084e-2 | 8.65868e-2 | 3.81007e-5 |
| H | 2.63534e-12 | -3.55847e-13 | -9.14031e-15 |
| central flight time | 8.50459e-2 | -2.91143e-2 | 3.20553e-4 |

The result is `COMPUTED/E1_QA_NON_RIGOROUS`.  Seven axial samples are not a
box cover, a channel tube, derivative enclosures, or a V2 event atlas.
The solved `H` values are themselves near the floating energy noise floor, so
their displayed endpoint quotients are archived but should not be interpreted.

```bash
python3 -m numerics.vdp_p2e_axis_continuation
python3 -m unittest numerics.test_vdp_p2e_axis_continuation -v
```
