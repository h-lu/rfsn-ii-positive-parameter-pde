# P2e v2 B.RET and stable-cut census

The retained run used the prospectively frozen center
`phi_h=5.861458108702215` and offsets

```text
-1/500, -1/1000, -1/2000, 0, 1/2000, 1/1000, 1/500.
```

The stencil, tolerances, event definitions, and no-retry rule were committed
before the retained run in `52a3f29` and `f0d91e3`.  The latter discloses the
unretained interface audit: the unrestricted `rho_s=1/100` level has a remote
projection crossing, so the already bound P2d local-block condition
`rho_u<=1/100` must be part of the physical-face candidate.

## Application-owned definitions

The source and incoming face use the same finite-horizon nonlinear-`Wu` Kato
frame and the same radius `R=1/100`.  The numerical incoming candidate is

```text
rho_s=R,  rho_u<=R,  d(rho_s)/dxi<0.
```

This is an actual central-ODE event, but it is not identified with the P2d
exact-Moser theorem face.  On this candidate, apply the central reverser and
the existing inverse nonlinear-Kato source coordinates.  The scalar

```text
c_stable(Z)=nu(R Z)
```

is an independent application-owned stable-cut label: its zero set is the
reverser image of the computed nonlinear-`Wu` spine.  It does not reuse the
old `deep_stable_cut`/`stable_cut_proxy`.

## First-event result

| offset | first qualifying event | time | cooriented speed | `H` drift | `dT/dphi` |
|---:|---|---:|---:|---:|---:|
| -1/500 | pole `x=10` carrier | 16.486881 | 27.9203 | 1.63e-12 | 350.239 |
| -1/1000 | pole `x=10` carrier | 16.982178 | 27.3957 | 1.07e-12 | 728.101 |
| -1/2000 | algebraic | 17.094796 | 8.12875 | 5.71e-14 | 1464.83 |
| 0 | `B.RET` candidate | 19.275936 | 0.00703211 | 3.79e-14 | 34798.0 |
| 1/2000 | algebraic | 15.869285 | 5.71385 | 6.32e-14 | -3587.10 |
| 1/1000 | algebraic | 14.892409 | 6.00000 | 5.32e-14 | -1162.62 |
| 1/500 | algebraic | 14.177764 | 6.05000 | 3.93e-14 | -462.808 |

The `-1/1000` orbit also crosses the unrestricted `rho_s=R` level, but there
`rho_u=3.03464`; it is outside the local block by two orders of magnitude and
is therefore retained as a rejected projection crossing, not a return hit.
The algebraic `Q<0` sign stratum and the pole definition `x=-U=10` are exactly
the same as in the preceding C.A census.

At the center hit,

- `rho_s=0.01`, `rho_u=1.28580e-5`, giving local-block margin `0.00998714`;
- the incoming Kato phase is `5.861458108688916`;
- the reflected nonlinear-Kato inverse reconstructs the state to
  `1.46e-17`;
- `c_stable=nu_s=-1.66e-13` and the inverse status is successful;
- the variational derivative is tangent to the hit surface to `1.74e-12`.

All predeclared floating QA thresholds pass.  The very large center
`dT/dphi`, together with algebraic first hits already at the nearest sampled
offsets, shows why this stencil does not resolve a two-sided `B.RET` aperture.
There is only one `B.RET` sample, so no return-phase monotonicity is claimed.

## Exact conclusion

The computation supplies an actual same-source `B.RET` carrier germ and an
independent same-source stable-cut label candidate at the selected homoclinic.
It does not supply a sampled return band around that point.  These numerical
algebraic-frame objects are not frozen exact-Moser faces, an exhaustive return
census, or `V2.EVENT_ATLAS`.

```bash
python3 -m numerics.vdp_p2e_bret_scout
python3 -m unittest numerics.test_vdp_p2e_bret_scout -v
```
