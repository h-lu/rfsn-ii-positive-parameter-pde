# P2e v2 algebraic-coordinate diagnosis

At the fixed exploratory point

\[
  (r,a_2,\epsilon)=(3/200,0,1),
\]

the archived first attempt stopped with
`Q is not a forward coordinate when pi is nonpositive`.  That message did
not diagnose the selected orbit.  It diagnosed an intermediate collocation
iterate: the old unknowns `(beta,alpha)` do not keep Newton iterates inside
the required component `pi>0` when `delta=r^2=0.000225` makes the outer BVP
strongly stiff.

The opt-in repair uses the exact change of coordinates

\[
  \eta=\log(\pi/\delta),\qquad \omega=w/\delta .
\]

Every finite iterate then has `pi=delta exp(eta)>0`; no equation, parameter,
phase bracket, leaf, or terminal condition is changed.  On the leading
resolved-`K1` seam, the reconstructed value is
`pi=1.3693063938e-4>0`.  The positive-`pi` outer continuation reaches the
same-section graph with exact-energy residual at roundoff.

The resulting coupled floating-point BVP converges, but it is **rejected** as
a matched orbit.  Its main diagnostics are:

- source phase `5.756850585799922`;
- minimum outer `pi = 1.3693063937936708e-4`;
- outer energy residual `2.22e-16`;
- collocation residual `4.94e-5` and boundary/interface residual `8.88e-16`;
- central energy residual `1.50e-4`;
- resolved-`K1` energy residual `4.15e-3`;
- central--`K1` `q1` seam defect `-3.4708200278`.

Thus the original exception was a coordinate-domain artifact, but removing
it does not supply an algebraic centerline.  The next missing object is an
energy-preserving, small-`r`-scaled central--`K1` coupling that includes the
`q1` seam equation.  A separate tightened trial at tolerance `1e-8` exhausted
60,000 nodes, so this diagnosis stops here rather than retuning parameters or
calling the rejected candidate evidence for V5 or the V2 event atlas.

The original one-attempt scout and its saved STOP remain unchanged.  The new
solver is opt-in through `positive_pi_outer=True`.  Reproduce the diagnostic
and its focused tests with:

```bash
python3 -m numerics.vdp_p2e_algebraic_coordinate_diagnosis
python3 -m unittest numerics.test_vdp_p2e_algebraic_coordinate_diagnosis -v
```

## Subsequent resolution

The next, separately frozen calculation replaces the defective central
collocation leg and explicitly restores the missing `q1` row.  It succeeds at
the same parameter point; see
[`P2E_V2_ENERGY_MATCHED_REPORT.md`](P2E_V2_ENERGY_MATCHED_REPORT.md).  This
follow-up does not alter the historical STOP or the rejected intermediate
candidate recorded above.
