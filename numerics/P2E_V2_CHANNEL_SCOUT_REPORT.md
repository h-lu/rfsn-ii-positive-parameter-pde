# Minimal v2 P2e channel scout

The single frozen exploratory point is

\[
  (r,a_2,\epsilon)=(3/200,0,1),
\]

strictly inside `vdp-positive-box-v2`.  The result is
`PARTIAL_SCOUT_SUCCESS / ALGEBRAIC_CHANNEL_STOP / NON_EVIDENTIARY`.
It does not materialize any part of `V2.EVENT_ATLAS`.

The old pole and matched candidates were first rejected as v2 data because
both use `r=0.08`, outside the v2 bridge.  Their hashes remain recorded only
as design lineage.  The new computations instead use the direct
finite-horizon nonlinear unstable graph in the P2bK algebraic frame, with the
same `R_chi` Kato phase convention used by the P2c direct-source scout.

Two centerlines were obtained:

- The selected homoclinic solve gives
  `phi=5.861458108702215`, `T=9.637968053355097`, shooting residual
  `8.64e-15`, Kato-source cross-check defect `3.91e-18`, positive joint
  symmetry-hit speed, and sampled energy drift `3.94e-14`.
- The phase-zero source reaches the real physical ODE section
  `g_pole=U_central+10=0` at physical `x=0.16755617272915507`.
  The section residual is `3.79e-13`, event speed is `0.4070971`, all sampled
  pre-hit values have the strict incoming sign, and sampled energy drift is
  `1.67e-16`.

The one authorized algebraic/matched attempt stopped before the coupled BVP.
The leading outer continuation raised

```text
ValueError: Q is not a forward coordinate when pi is nonpositive
```

in `normal_outer_rhs_q`.  No phase bracket, outer leaf, or solver parameter
was retuned after this output.  Consequently there is no algebraic centerline
and no three-channel scout.

The saved state bounds are sampled trajectory bounds, not tubes.  The real
symmetry and pole sections are diagnostic hit functions, not theorem faces.
No artificial lateral, incidence complex, component census, normalization,
numeric `m0`, or mathematical `PASS` is present.

Reproduce and test with:

```bash
python3 numerics/vdp_p2e_channel_scout.py
python3 -m unittest numerics.test_vdp_p2e_channel_scout -v
```
