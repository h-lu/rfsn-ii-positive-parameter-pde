# P2e v2 C.A phase-carrier census

At the exact center `(r,a2,epsilon)=(3/200,0,1)`, seven predeclared source
phases `phi_a+[-0.04,-0.02,-0.01,0,0.01,0.02,0.04]` were integrated from the
same finite-horizon nonlinear-`Wu`/Kato provider as the matched algebraic
centerline.  The central ODE and its analytic variational equation were
integrated together.  This is `COMPUTED/E1_QA_NON_RIGOROUS`.

## Carrier definitions and sign correction

The algebraic scout carrier is `U=-4`, counted only when `P<0,Q<0`.  A
crossing with `Q>0` is a through-state, not an algebraic outcome.  This seam
is still a numerical carrier candidate and is not being identified with an
already frozen V2 theorem face.

The repository's frozen pole carrier is `x=-U=10`, hence **central `U=-10`**,
as bound by `vdp_p2e_channel_scout_v2.json` (`central_gate_U=-10`) and
`CENTRAL_CORE_IMPORT.md`, equations (13)--(14).  The task shorthand `U=+10`
was a sign error and was not used.

No third return/stable-cut event was added.  The available
`vdp_return_coding.integrate_first_event` uses an independent linear numerical
zero-energy source section and explicitly calls its deep cut a
`stable_cut_proxy`.  Reusing it here would change the source/event definition.
The one missing object is an application-owned physical `B.RET` return section
and stable-cut embedding pulled back to this same nonlinear-`Wu`/Kato source.

## Census

| offset | first qualifying event | time | `P` at hit | `Q` at hit | sampled `H` drift | `dT/dphi` |
|---:|---|---:|---:|---:|---:|---:|
| -0.04 | algebraic | 8.495834 | -4.319775 | -5.380586 | 2.86e-14 | 9.2353 |
| -0.02 | algebraic | 8.742135 | -3.890673 | -5.916087 | 3.37e-14 | 17.0302 |
| -0.01 | algebraic | 8.967410 | -3.456352 | -6.453283 | 2.20e-14 | 30.9091 |
| 0 | algebraic | 9.895162 | -1.154369 | -9.239197 | 4.82e-14 | 835.046 |
| 0.01 | pole `x=10` carrier | 14.765545 | -25.782919 | 4.773144 | 9.43e-13 | -39.2902 |
| 0.02 | pole `x=10` carrier | 14.566761 | -27.383843 | 5.149205 | 1.27e-12 | -9.48358 |
| 0.04 | pole `x=10` carrier | 14.517851 | -28.693887 | 4.882138 | 2.66e-12 | 2.16687 |

Each positive-offset orbit first crosses `U=-4` with `P<0,Q>0`, then reaches
`x=-U=10`; those crossings are retained in the JSON with their time gaps.
Reaching this carrier alone is not a certification that the hit lies in the
V3 pole product aperture or reaches the pole end.
Every selected hit is transverse, and the other carrier function has absolute
gap `6` at the hit.  On the four algebraic samples, hit time and `P` increase
with phase while hit `Q` decreases; the pointwise variational derivatives have
the same signs.  The pole hit times are ordered on the three-point stencil,
but their local `dT/dphi` changes sign, so no uniform pole monotonicity is
claimed.

## Exact conclusion

The selected matched phase is a genuine transverse oriented hit of this
numerical C.A carrier, and the stencil supplies a one-sided sampled algebraic
trace from offset `-0.04` through `0`.  Offset `0.01` is already in the pole
outcome, so the fixed stencil does **not** certify a two-sided same-outcome
C.A aperture around `phi_a`; it only brackets an outcome change in `(0,0.01)`.
No offsets or thresholds were moved to conceal this result.

Thus this is an actual phase-carrier germ and a useful aperture diagnostic,
not a frozen carrier, a return census, a complete first-event atlas, or a
validation of `V2.EVENT_ATLAS`.

```bash
python3 -m numerics.vdp_p2e_ca_carrier_census
python3 -m unittest numerics.test_vdp_p2e_ca_carrier_census -v
```
