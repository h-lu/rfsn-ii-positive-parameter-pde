# A2 periodic-profile CAPD validator

This directory contains a deliberately narrow validated computation for the
saved van der Pol `A2` target at

\[
(r,a_2,\epsilon)=(2/25,0,1).
\]

It uses a 13-node multiple-shooting Krawczyk operator, with radius `1e-7` on
each four-dimensional node box.  The final flight is a validated Poincare map
to the decreasing `q=0` section, so the half-period is not treated as a poorly
conditioned Newton variable.  Positivity of `q` at the last fixed-time node
and negativity of `u=q'` at the endpoint validate the selected crossing and
its transversality.  Reversibility then closes the half orbit to a true
periodic stationary profile.

On the same root enclosure it validates

\[
z'=\frac1{100}u^2-r^2u^3+\frac23r^4u^4,
\qquad z(T)<-\frac1{10}.
\]

Since physical `w=U-1=-r^2u` and `dx=r dxi`, the physical moment in the
self-adjoint-pencil criterion is `2*r^5*z(T)`.  Thus the strict inequality
implies a real co-periodic temporal eigenvalue `lambda>0.01`.

Strict inclusion and contraction prove existence and uniqueness in the
hard-coded lifted 53-dimensional outer box (X).  They do not assert that the
wider S0 preselection box contains no other roots.  The validator also does not compute a Bloch
continuum, an Evans function, or an eigenvalue contour, and it does not provide
a release certificate or an independent-machine replay.

Every zero in the outer normalized box lies in the Krawczyk image, so the
scaled image is a valid root subbox for the moment step.  Each exact orbit-node
component is then propagated separately with the augmented interval flow and
the resulting segment intervals are added.  Discarding correlations can widen
the sum, but cannot remove the exact total moment from its enclosure.

## Build

Use the CAPD/FILIB commit and strict compiler flags frozen in
`validation/rigorous/dependency.lock.json`.  For a configured CAPD build:

```bash
CAPD_CONFIG=/absolute/path/to/capd-config
/usr/bin/g++ validation/a2_periodic/a2_periodic_capd.cpp \
  $($CAPD_CONFIG --cflags) \
  -DNDEBUG -fno-fast-math -ffp-contract=off \
  -fno-tree-vectorize -fno-ipa-pure-const \
  $($CAPD_CONFIG --libs) \
  -o /tmp/a2-periodic-capd
OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 LC_ALL=C.UTF-8 \
  /tmp/a2-periodic-capd
```

The executable requires the repository's complete rounding probe to pass,
including the CAPD mode checks, directed arithmetic, exact-rational interval
checks, serialization, and the SSE FTZ/DAZ check.  A mathematical `PASS`
additionally requires:

- strict Krawczyk inclusion and
  `||I-C*DF(X)||_infinity < 1`;
- the seed and half-period enclosures to lie strictly in the frozen S0 boxes;
- `q>0` at the last fixed-time node and `u<0` at the final section;
- outward-rounded bounds `z(T)<-0.1` and
  `M_0.01=2*r^5*z(T)<-5e-7`.

## Validated local run

Using the frozen CAPD commit
`731079217a9254ea2948d742df2b170895effe7f`, its FILIB backend, GCC 15.2.0,
and the strict flags above, the 2026-08-29 local run returned:

| quantity | outward-rounded enclosure or upper bound |
|---|---:|
| `||I-C*DF(X)||_infinity` | `< 0.020642` |
| seed `s` | `[4.9255666661290, 4.9255666661292]` |
| central half-period `T` | `[13.497881036840, 13.497882046339]` |
| physical period `L=2*r*T` | `[2.1596609658944, 2.1596611274142]` |
| last-node `q` | `[0.0006574049912794, 0.0006574058418102]` |
| final-section `u` | `[-0.001321034222611, -0.001321033106519]` |
| half moment `z(T)` | `[-0.1346947634090, -0.1346947634087]` |
| physical `M_0.01` | `[-8.827356014769e-7, -8.827356014754e-7]` |

All stated gates returned `PASS`.  Consequently this local outward-rounded
run establishes a true A2-near periodic stationary profile and, through the
self-adjoint-pencil criterion, a real co-periodic temporal eigenvalue
`lambda` in `(0.01,2)`.  This is the mathematical target result; the absence
of an independent-machine replay is a publication/provenance limitation, not
an unvalidated floating-point step in this run.

The concise machine-readable local record is
[`results/a2_periodic_local_pass.json`](results/a2_periodic_local_pass.json).
It binds the source, contract, dependency lock, complete compiler arguments,
local binary and raw-output hashes, the locked CAPD/FILIB libraries, all strict
gates, and the exact binary64 interval endpoints in hexadecimal form.  The
table above uses slightly widened outward decimal displays.  The record is
intentionally labelled `claim_bearing=false`; no general certificate or replay
framework was added.
