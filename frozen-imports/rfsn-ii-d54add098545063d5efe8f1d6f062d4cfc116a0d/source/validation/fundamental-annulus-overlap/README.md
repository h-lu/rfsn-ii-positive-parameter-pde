# Quantitative fundamental-annulus overlap

## Status and scope

This source-only package certifies the **local** part of the saddle-focus
overlap gate for the universal core

```text
U' = P,   P' = -U^2-V,   V' = Q,   Q' = U.
```

It proves, for the canonical true future graph used by Paper A:

1. the selected local arm continues with one root at every physical source
   radius `0 < R <= 2.4e-4` and has a unique first crossing of `|u|=.01`;
2. the crossing lies in one validated two-parameter exit-to-target chart,
   with a strictly positive intersection derivative;
3. at the fixed outer seam `R=2.4e-4`, a robust fixed-time multiple-shooting
   root exists uniquely in its validation box, its radial tangent and energy
   derivative are enclosed, and its rigorous nonlinear Poincare image is
   strictly contained in the exit chart.

This package itself does **not** certify the separate finite continuation
from the existing inner finite-cover endpoint near `R=.025` down to
`R=2.4e-4`.  The sibling
`../finite-source-intermediate-collar/spiral_extension_certificate.json`
now supplies all 9,725 boxes, 9,724 common-root bridges, and the endpoint
containment needed for that adjacency chain.

The analytic saddle-focus theorem already supplies `C^2_log` regularity of
the selected arm.  The new explicit bounds certify its finite cutoff and
uniform `C^1` transversality.  No numerical second-variation constant is
claimed here.

## Audited dependencies

The package reuses only the following already validated source contracts:

- `../origin-algebraic-heteroclinic`: the true unstable graph
  `s=H(u)` on `|u|<=.01`, including
  `|H(u)|<|u|^2/4` and
  `||DH||<=0.005237905481357891` after the certified residual allowance;
- `../future-target-fold`: the canonical signed-energy future graph and its
  generated value/gradient budgets on the complete physical target box;
- the robust heteroclinic source enclosure, which places the true
  heteroclinic stable coordinate within `1.19e-11` of the exit-chart centre.

The centre tables in this directory are floating-point preconditioner data.
They carry no proof status.  Every theorem-level conclusion comes from a
strict interval inclusion in the three C++ probes.

## What each probe proves

### `local_annulus_bounds_probe.cpp`

In exact hyperbolic coordinates, `Fix(R)` is `u=s` and the physical radius
is `R=2|u|`.  The probe evaluates with outward-rounded intervals the local
passage inequalities for

```text
delta    = .01,
rho_plus = 1.2e-4,
R_plus   = 2.4e-4.
```

The key certified numbers are

```text
|w_exit|                         <= 1.584003296758119e-6
exit-target stable-square margin >= 4.157712566534325e-7
d_phi(exit phase - target phase) >= 0.7816287889826323
```

Here `w=s-H(u)`.  The strict radial inequality proves that the exit is the
unique first crossing, not a later Poincare return.  The stable-square
margin prevents the selected arm from leaving the validated target chart,
and the last derivative gives uniqueness and compatible orientation.

Two convenient fixed logarithmic subannuli are also printed:

```text
R in [R_plus exp(-pi/2), R_plus]
  = [4.9891098324182828e-5, 2.4e-4],

R in [R_plus exp(-2pi), R_plus]
  = [4.4818625560991678e-7, 2.4e-4].
```

These names describe their declared logarithmic widths.  The package does
not infer an exact fold count merely from those endpoint ratios.

### `exit_target_chart_probe.cpp`

This is a 185-dimensional robust Krawczyk problem with 36 flow segments.
Its source rows are

```text
|u|^2 = .01^2,   s1 = sigma1,   s2 = sigma2,
```

and its terminal rows are the first event `e=.0575` and the ambient
canonical future-graph row.  On the full parameter square

```text
sigma1 =  6.038629937610632e-6 +/- 2e-6,
sigma2 = -8.974511235257388e-6 +/- 2e-6,
```

it certifies

```text
Krawczyk ratio                  <= .96284
weighted derivative contraction <= .2281691793139122
d(exit phase)/d sigma1 in [-1.209084078,-.798036]
d(exit phase)/d sigma2 in [-.829376691,-.42054]
dE/d sigma1 in [.01988243,.02002015]
dE/d sigma2 in [-.03465109,-.03451392]
```

The program also verifies the complete terminal physical corridor and that
`e=.0575` is the first terminal event.  A separate `1e-12` centre run gives
the sharp phase enclosure used to audit the centre placement.

### `fixed_radial_source_probe.cpp`

This is a 196-dimensional robust Krawczyk problem with 48 fixed-time flow
segments.  The source rows are

```text
P=0,   Q=0,   sqrt(U^2+V^2)=R,
```

and the final row is the ambient canonical future-graph equation.  The
parameter interval `R=2.4e-4 +/- 1e-12` includes the exact outer seam.  It
certifies

```text
Krawczyk ratio          <= .316977
tangent Krawczyk ratio  <= .027569
dU/dR in [-.745531,-.727381]
dV/dR in [1.202412,1.212041]
d phase/dR in [4112.558,4219.786]
dE/dR in [.000202424,.000211979]
```

It then rigorously flows the whole source-root enclosure to the nonlinear
section `|u|=.01`.  The first-crossing image satisfies

```text
s1 in [ 4.600552962362100e-6, 4.600987316500695e-6]
s2 in [-9.042264714143305e-6,-9.041919363023207e-6]
```

and lies strictly inside the exit chart with minimum componentwise margin
`5.61923e-7`.  Invariance of the future graph and uniqueness of
the exit chart identify this source root with the selected local arm.

## Clean replay

Build CAPD with FILIB interval arithmetic, then run

```bash
PAPERA_ANNULUS_CAPD_CONFIG=/absolute/path/to/capd-config \
  ./run_validation.sh
```

To retain results at a chosen location, set

```bash
PAPERA_ANNULUS_OUTPUT=/absolute/output/directory
```

The script compiles into that output directory (or a fresh `mktemp`
directory), runs all four checks, validates their JSON syntax when Python 3
is available, and writes `source.sha256` and `dependency.sha256`.  It never
writes binaries or caches into the repository.

## Evidence boundary

`certificate.json` records the package-local clean replay and the interface
that was E0 when this certificate was built.  That interface has since been
closed by the sibling spiral-extension certificate, which supplies a
verified source-component cover from the existing finite endpoint

```text
R in [.025010308718855751,.025021372991159356]
```

to the radial seam box

```text
R in [.000239999999,.00024000000100000003],
```

including every individual Krawczyk inclusion, every adjacent-root
containment, the required chart changes, and final containment in this
package's seam root.  The historical warning remains valid: radius proximity
or an unconnected pilot is not an overlap proof.
