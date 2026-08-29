# `pulse_1` whole-line CAPD validator

This directory contains the target-specific validated input for the
whole-line spectral-instability theorem in
[`PULSE_1_SPECTRAL_INSTABILITY.md`](../../van-der-pol/PULSE_1_SPECTRAL_INSTABILITY.md).
The parameter point is

\[
 (r,a_2,\epsilon)=(2/25,0,1).
\]

The calculation is deliberately small.  It does not discretize an
infinite-domain spectral problem or compute an Evans function.  It reuses the
P2c true-homoclinic multiple-shooting code, adds one scalar moment integral,
and combines it with the already validated exponential tail.

## What is proved

The validator performs four linked checks.

1. It runs a fixed-parameter Krawczyk enclosure for a true symmetric
   homoclinic issuing from the P2b true unstable graph.
2. It maps that point-root Krawczyk image into P2c selected grid cell
   `(31,64,2)`.  The containment ratio is below one, so the grid-cell
   uniqueness theorem identifies the point root with the frozen, connected,
   core-anchored P2c branch.
3. On the same point-root image, it integrates

   \[
   z'=0.01U^2-r^2U^3+\frac23r^4U^4
   \]

   across the nine fixed shooting segments and the last validated Poincare
   flight to the symmetry section.
4. It imports both pieces of the P2c outer-half estimate: the
   `tail_weight_one_fifth_constants.normalized_parameters.C0` bound on the
   infinite tail and the identical
   `compact_local_pre_source_segment.weight_one_fifth_compact_constants.normalized_parameters.C0`
   bound on `[-11,-T_h]`.  Together they give

   \[
   |\Gamma(\xi)|\le1.082e^{-|\xi|/5}
   \quad\text{outside the source-to-symmetry segment},\qquad T_h>9.6.
   \]

Termwise integration bounds the omitted half-tail by `0.000672`.  Since
physical `w=U_physical-1=-r^2 U` and `dx=r dxi`, symmetry gives

\[
 M_{0.01}=2r^5z_+.
\]

The strict negative moment and the analytic whole-line operator-pencil
theorem imply a real temporal \(L^2\) eigenvalue
\(\lambda_*\in(0.01,2)\).

## Build and run

Use the CAPD/FILIB commit and strict flags in
`validation/rigorous/dependency.lock.json`.  The P2c source also requires the
hash-frozen H10 table through a forced include:

```bash
CAPD_CONFIG=/tmp/rfsn-vdp-capd-strict-7310792/build-strict/bin/capd-config
H10_HEADER="$PWD/frozen-imports/rfsn-ii-d54add098545063d5efe8f1d6f062d4cfc116a0d/source/validation/origin-algebraic-heteroclinic/unstable_graph_terms.hpp"

/usr/bin/g++ validation/pulse_1/pulse_1_capd.cpp \
  -include "$H10_HEADER" \
  $($CAPD_CONFIG --cflags) \
  -DNDEBUG -fno-fast-math -ffp-contract=off \
  -fno-tree-vectorize -fno-ipa-pure-const \
  $($CAPD_CONFIG --libs) \
  -o /tmp/rfsn-pulse-1-capd

OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1 LC_ALL=C.UTF-8 \
  /tmp/rfsn-pulse-1-capd
```

The complete rounding probe must pass before any mathematical gate is used.
The wrapper source intentionally includes the existing P2c implementation;
the local run record therefore binds the wrapper, the included P2c source,
the forced H10 table, and the P2c certificate and tail evidence separately.

## Validated local run

On the locked local toolchain, the 2026-08-29 run returned:

| quantity | outward-rounded enclosure or upper bound |
|---|---:|
| point-root Krawczyk inclusion ratio | `0.76034508383926735` |
| point root into selected cell ratio | `0.33311716340064657` |
| shooting determinant | `[145.4403, 163.5047]` |
| source-to-symmetry time | `[9.6525533866, 9.6527260181]` |
| symmetry-centre `U` | `[4.9254133667, 4.9257201238]` |
| symmetry-centre `V` | `[-8.0238302003, -8.0228410797]` |
| compact half moment | `[-0.134778800, -0.134611534]` |
| absolute omitted half-tail | `< 0.000671676` |
| full half moment | `[-0.135450475, -0.133939858]` |
| physical full-line `M_0.01` | `[-8.876883e-7, -8.777882e-7]` |

Every gate returned `PASS`.  The centre and time boxes contain the frozen
`pulse_1` seed; independently, the selected-cell containment proves that the
validated point root is the P2c selected primary homoclinic rather than an
unidentified near-seed orbit.

The concise local run record is
[`results/pulse_1_local_pass.json`](results/pulse_1_local_pass.json).  Its
`claim_bearing=false` label records only the missing independent-machine
replay.  It does not weaken the local outward-rounded inequalities.

## Claim boundary

This calculation proves one positive real whole-line point eigenvalue.  It
does not give the complete point spectrum, a nonlinear instability theorem,
dynamical pattern selection, a Turing bifurcation, or canard identification.
The finite-window eigenvalue near `0.0214` is a compatible numerical
cross-check and is not used by the proof.
