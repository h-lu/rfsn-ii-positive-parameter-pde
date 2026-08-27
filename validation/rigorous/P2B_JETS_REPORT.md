# Issue #7 P2b mixed-jet and weighted-half-orbit validation report

The first clean-source P2b mixed-jet run completed on 2026-08-27.  Its
machine-readable certificate is
[`results/vdp_bridge_v1_p2b_jets.json`](results/vdp_bridge_v1_p2b_jets.json).

## Verdict

| Layer | Status | Meaning |
|---|---|---|
| Source, dependency, bridge, configurations, prerequisites, and rounding integrity | `PASS` | The clean local source commit, read-only flagship Git objects, strict CAPD/FILIB build, frozen bridge and gates, and immutable P2a/P2b0 certificates match their recorded hashes. |
| `P2.JETS.COEFFICIENTS` | `PASS` | A gap-free (16\times8\times4\times2) exact-rational grid encloses all normalized-parameter coefficient derivatives through order two on the P2b0 true-orbit tube. |
| `V2.WU.STATE_C23` | `PASS` | The true local graph has uniform Hilbert--Schmidt state-(C^2/C^3) bounds on the radius-(1/100) disk; the stable analogue follows by reversibility. |
| `V2.WU.MIXED_JETS` | `PASS` | The complete rectangle (D_b^iD_\theta^j), (0\le i\le3), (0\le j\le2), is bounded in the labelled multilinear norm. |
| `V2.WU.WEIGHTED_HALF_ORBITS` | `PASS` | The same complete jet rectangle is bounded in the weight-(1/4) half-orbit space, in moving and physical coordinates. |
| Parent `V2.WU.JETS` and `V2.WU_GRAPH` | `PASS` | The P2a true graph, P2b0 tube, higher state tensors, mixed jets, and weighted half-orbit constants are now jointly discharged locally. |
| Normalized Kato source phase | `PENDING` | The absolute phase, (C^2) Kato frame, and degree-one true source circle are a separate interface before P2c. |
| Independent replay | `PENDING_REQUIRED` | One of the two policy-required distinct machines has been observed. |
| Aggregate certificate | `INCONCLUSIVE` | The local mathematical result is not claim-bearing before the required independent-machine replay. |

Thus `mathematical_status=PASS`, `integrity_status=PASS`,
`final_status=INCONCLUSIVE`, `claim_bearing=false`, and
`release_eligible=false`.  Here `INCONCLUSIVE` does not indicate a failed or
crossing P2b gate: every implemented P2b mathematical and integrity
obligation passed.  It records only the stronger two-machine release policy.

## Domain, norms, and proof mechanism

The complete comparison bridge is

\[
 r\in[0,2/25],\qquad
 a_2\in[-1/4,1/4],\qquad
 \epsilon\in[4/5,6/5],
\]

with unstable disk radius (R=1/100).  Parameters are normalized by

\[
 \theta_r=25r-1,\qquad \theta_a=4a_2,\qquad
 \theta_\epsilon=5(\epsilon-1).
\]

P2a supplies the actual parameter-dependent analytic graph family, while
P2b0 sharpens the true-orbit domain to

\[
 |x|\le\frac{251}{25000},\qquad
 \lVert DH_\mu\rVert_F\le\frac{111}{20000}.
\]

The coefficient grid is evaluated only on that true-orbit tube.  The
Lyapunov--Perron estimate is therefore an a posteriori Neumann bound along the
actual half-orbit family; it is not a contraction claim on a full
four-dimensional radius-(R) product ball.

The frozen local weight is (\omega=1/4).  Representative outward-rounded
enclosures are

\[
\begin{aligned}
 K_\omega&\le2.1876726427121103,\\
 q_{\rm LP}&\le0.06588759442159081<0.067,\\
 (1-q_{\rm LP})^{-1}&\le1.0705349741938102<1.075,\\
 \bar\kappa&\ge0.6898861848838853>0.68.
\end{aligned}
\]

The positive lower margins for the state-tensor no-first-exit inequalities
are

\[
 3\bar\kappa\sigma_2-M_2
 \ge0.016210801846244793,
 \qquad
 4\bar\kappa\sigma_3-M_3
 \ge0.05077566457633287,
\]

with frozen radii (\sigma_2=1/2) and (\sigma_3=9/8).  The corresponding
origin homological margins are at least (0.048155259645402015) and
(0.13744347407497637).  Consequently

\[
 \lVert D_b^2H_\mu\rVert_{HS}\le\frac12,
 \qquad
 \lVert D_b^3H_\mu\rVert_{HS}\le\frac98
\]

uniformly on the true graph disk.  These are true-graph estimates, not bounds
copied from the H10 polynomial center.

## Complete weighted jet rectangle

For

\[
 Z_{ij}=\lVert D_b^iD_\theta^jZ_{\theta,b}\rVert_\omega,
 \qquad 0\le i\le3,\quad0\le j\le2,
\]

the labelled-set Faà di Bruno recurrence contains every required target and
all three first and six symmetric second parameter multiindices.  Its
outward-rounded moving-coordinate upper bounds are

| (i\backslash j) | (0) | (1) | (2) |
|---:|---:|---:|---:|
| 0 | 0.010000000000000004 | 0.00026765887077342146 | 0.00018474263237410482 |
| 1 | 1.0705349741938102 | 0.03134303757848096 | 0.021923616738766465 |
| 2 | 10.755867555511195 | 1.0660946394000146 | 0.8151390440662017 |
| 3 | 324.3601320697227 | 54.95678060727521 | 45.79884648487769 |

Every preregistered jet gate has positive margin; the smallest is the
(Z_{00}) upper-gate margin,
(9.999999999999246\times10^{-5}).  The complete recurrence and its term
counts are independently reconstructed with exact rational arithmetic by the
Python checker.

The physical frame derivative bounds are

\[
 T_0\le4.005993216361619,\qquad
 T_1\le0.05492289770809256,\qquad
 T_2\le0.03473057347499278.
\]

After the complete Leibniz composition

\[
 \lVert D_b^iD_\theta^j(T_\theta Z)\rVert_\omega
 \le\sum_{k=0}^j{j\choose k}T_kZ_{i,j-k},
\]

the physical-coordinate upper bounds are

| (i\backslash j) | (0) | (1) | (2) |
|---:|---:|---:|---:|
| 0 | 0.04005993216361621 | 0.0016214685976982635 | 0.001116784668373685 |
| 1 | 4.288555844498266 | 0.18435687880014423 | 0.1284490544059658 |
| 2 | 43.08793246346188 | 4.86151130694908 | 3.7561049429984985 |
| 3 | 1299.384488729468 | 237.9712886600671 | 200.7718530141321 |

The certificate also records the original blown-up-parameter bounds, using
the exact coarse operator factors (25) and (625) for first and second
parameter order.  Their larger numerical size is a coordinate conversion,
not a loss of a gate; for example the conservative physical
(D_b^3D_\mu^2) upper bound is (125482.4081338326).

## Integrity and reproducibility boundary

The certificate was generated from clean source commit `ae88ae0fb47d`, using
the pinned CAPD source commit `731079217a92`, FILIB, and GCC 15.2.0 with the
strict floating-environment flags.  The flagship repository was accessed
only through read-only Git objects at commit `d54add098545`; it was not
modified.  The archived certificate SHA-256 is
`07b0949a3d403c0c0a85a4a157b86d7b32cce3ff0348aeffa1db474d441fca07`.

In addition to independently recomputing every serialized formula, margin,
status aggregation, recurrence, normalization scale, and physical-coordinate
composition, the checker materializes the frozen P2b probe and local headers,
verifies the locked compiler and linked archives, reconstructs the only
allowed strict compile command, and reruns the exact 106-argument probe.  The
new output must match the archived stdout byte-for-byte.  Regression tests
confirm rejection of coordinated edits to an atomic coefficient, all frame
and physical bounds, stored stdout and its hash, or the compile command.

This is deterministic same-machine integrity replay.  It does not count as a
second independent machine; under the user-imposed current-computer-only
constraint the recorded replay count remains (1/2).

The proof mechanism and every frozen formula are in
[`P2_VALIDATION_CONTRACT.md`](P2_VALIDATION_CONTRACT.md).  Reproduction uses
the `p2-jets` command documented in [`README.md`](README.md).

## Scope not yet validated

P2b closes the local true-graph mixed-jet and weighted-half-orbit interface
used later, but it does not yet fix the normalized Kato absolute source phase.
That separate linear/frame interface is the next ordered stage before the
selected positive-parameter homoclinic validation P2c.

The certificate does not validate the selected homoclinic and first-hit
branch, exact marked saddle chart, complete event atlas, either noncompact
end, V5 matching, V6 component census, temporal stability, dynamic Turing
selection, or finite-parameter canard identification.  Those remain later
Issue #7 or subsequent research questions and are not consequences of this
local `V2.WU_GRAPH` pass.
