# Issue #7 P2bK normalized Kato phase validation report

The first clean-source P2bK run completed on 2026-08-27.  Its
machine-readable certificate is
[`results/vdp_bridge_v1_p2b_kato.json`](results/vdp_bridge_v1_p2b_kato.json).

## Verdict

| Layer | Status | Meaning |
|---|---|---|
| Source, toolchain, bridge, configuration, and rounding integrity | `PASS` | The clean local source, read-only flagship objects, CAPD/FILIB build, frozen bridge and Kato gates all match their recorded hashes. |
| Exact symbolic backend | `PASS` | The Python executable and cache-free 1,561-file SymPy source tree match the dependency lock. |
| Archived P2b true-graph prerequisite | `PASS` | The immutable P2b certificate is recursively valid and supplies `V2.WU_GRAPH` on the same bridge. |
| Exact Kato algebra | `PASS` | All 56 projector, transport, frame, reverser, core-face, and phase-orientation identities hold exactly. |
| `P2.KATO.RIESZ_TRANSPORT` | `PASS` | The expanding Riesz projector and signed Kato transport are uniformly defined and tied to the selected core vector. |
| `P2.KATO.FRAME_CHANGE` | `PASS` | The physical Kato frame is oriented and uniformly nondegenerate, and its change from the algebraic P2b frame has the frozen positive phase convention. |
| `P2.KATO.C2_LIFT` | `PASS` | All declared first and symmetric second parameter bounds pass on the gap-free bridge grid, including exact 25/625 conversion to original parameters. |
| `P2.KATO.SOURCE_PARAMETERIZATION` | `PASS` | The coordinate circle, exact audit, and immutable P2b true graph jointly identify the same radius-0.01 true source boundary. |
| `V2.PHASE.TRUE_SOURCE` and `V2.PHASE.KATO_INTERFACE` | `PASS` | The nine declared source jets and the complete local Kato phase interface are discharged. |
| Independent replay | `PENDING_REQUIRED` | One of two policy-required distinct machines has been observed. |
| Aggregate certificate | `INCONCLUSIVE` | The local mathematical result is not claim-bearing before the second independent-machine replay. |

Thus `mathematical_status=PASS`, `integrity_status=PASS`,
`final_status=INCONCLUSIVE`, `claim_bearing=false`, and
`release_eligible=false`.  Here `INCONCLUSIVE` does not mean that an interval
crossed a P2bK gate: every implemented P2bK mathematical and integrity
obligation passed.  It records only the repository's stronger two-machine
release policy.

## What was fixed and verified

The complete comparison bridge is

\[
 r\in[0,2/25],\qquad
 a_2\in[-1/4,1/4],\qquad
 \epsilon\in[4/5,6/5],
\]

subdivided into the frozen gap-free \(16\times8\times4=512\) rational cells.
The source radius is \(R=1/100\).  The exact audit proves the normalized
expanding projector and Kato transport identities, their core-face anchor,
the positive phase sign, and the frame-change identities without sampling or
tolerances.  The interval kernel supplies uniform nondegeneracy and parameter
derivative bounds over the entire bridge.

Representative outward-rounded enclosures are

\[
\begin{aligned}
 |c|&\le 0.04000280433949446,\\
 \alpha&\ge0.7000001776660754,\qquad
 \beta\ge0.699999499224911,\\
 N^2&\in[1.9682235040744827,,2.0319762357433904],\\
 \sigma&\in[0.7015384346551256,,0.7128274595624934],\\
 \det C_{AK}&\in[0.49215617529836386,,0.5081229871063182],\\
 \lVert C_{AK}^{-1}\rVert_2&\le1.4254386511148138,\\
 \lVert K\rVert_2&\le1.024029468046225,\qquad
 s_{\min}(K)\ge0.975972249329584.
\end{aligned}
\]

The last two bounds prove that the physical Kato frame is uniformly well
conditioned.  They do **not** say that this frame is orthonormal.  Its later
positive radial symplectic completion is not part of P2bK.

For normalized parameters, selected first/second derivative bounds are

| Object | First order | Second order |
|---|---:|---:|
| \(c\) | 0.04472888445348044 | 0.02830013681038239 |
| \(P_u\) | 0.020282936081800304 | 0.012814166373290073 |
| \(\chi\) | 0.011320817569346385 | 0.0072481082521855394 |
| \(R_\chi\) | 0.016010552114087542 | 0.010252789230912013 |
| \(C_{AK}\) | 0.013231058183648278 | 0.00809764634891768 |
| \(K\) | 0.023364034656358407 | 0.013784739357482388 |

The corresponding original blown-up-parameter bounds are recorded after the
exact operator factors 25 and 625.  The larger converted numbers are a change
of parameter coordinates, not a failed gate.

All preregistered margins are strictly positive.  The smallest lower margin
within each principal group is

| Gate group | Smallest certified lower margin |
|---|---:|
| Riesz/transport | 0.0009971956605055246 |
| Frame change | 0.0009493318957868313 |
| \(C^2\) lift | 0.0016359653436415836 |
| Source parameterization | 0.000027507587669905312 |

## The true source and its jet triangle

The Kato phase defines the direct coordinate circle

\[
 b(\phi,\theta)=R,R_{\chi(\theta)}e_\phi,
 \qquad \lVert b\rVert_2=R,
 \qquad \lVert\partial_\phi b\rVert_2=R.
\]

The interval bounds give

\[
 B_1\le1.1320817569346389\times10^{-4},\qquad
 B_2\le7.249241233009465\times10^{-5}.
\]

At \(r=0\), the exact identities reduce this circle pointwise to the frozen
core source with the same positive degree-one phase.  Away from the core
face, the archived P2b certificate supplies the true graph; the checker then
independently recomputes every declared chain-rule recurrence.  This
dependency is explicit: a source-coordinate calculation by itself is not a
proof that the circle lies on a true invariant graph.

For

\[
 S(\phi,\theta)=T_\theta
   \bigl(b(\phi,\theta),H_\theta(b(\phi,\theta))\bigr),
\]

the normalized true-source jet upper bounds are

| Jet | Upper bound | Jet | Upper bound |
|---|---:|---|---:|
| \(S_{00}\) | 0.040059932163616224 | \(S_{01}\) | 0.0021069681812134556 |
| \(S_{02}\) | 0.0014699660576700448 | \(S_{10}\) | 0.042885558444982694 |
| \(S_{11}\) | 0.0023778474338025522 | \(S_{12}\) | 0.0016806334207098293 |
| \(S_{20}\) | 0.04719435169132889 | \(S_{21}\) | 0.0029762667838186397 |
| \(S_{30}\) | 0.05711132267275075 |  |  |

This is exactly the frozen total-order-three triangle

\[
 (i,j)\in\{(0,0),(0,1),(0,2),(1,0),(1,1),(1,2),
             (2,0),(2,1),(3,0)\}.
\]

It is not the full rectangle \(0\le i\le3\), \(0\le j\le2\).  In
particular, no unavailable fourth or fifth state derivative of the true graph
has been inferred.

## Integrity and reproducibility boundary

The certificate was generated from clean source commit
`91007a88395290a594ba88047ff6ae45b9cebb80`, using the pinned CAPD source
commit `731079217a92`, FILIB, and GCC 15.2.0.  The flagship repository was
accessed only through read-only Git objects at commit `d54add098545`; it was
not modified.  The archived certificate SHA-256 is
`c67cce575caa396eba5b4388e8ba9a0c9d73fd702f69911d64c878f57f27bff3`.

The exact audit ran with the frozen Python 3.14.4 executable and SymPy 1.14.0
source tree.  The source-tree digest is
`b2c5c7e0d9a169a6b69a3137fb0af363a06a69a2b5d6b2b912a43525560c8b42`;
bytecode caches are excluded from that digest and bypassed at execution by a
fresh empty `PYTHONPYCACHEPREFIX`.

The checker does not trust certificate-local derived fields.  It

1. recursively verifies the P2b prerequisite and all frozen source bindings;
2. independently recomputes the gates, margins, 25/625 conversions, and nine
   source recurrences;
3. materializes the probe from the frozen source commit, reconstructs the
   strict compile command, and compares its output byte-for-byte; and
4. materializes and reruns the 56-identity exact audit under the locked
   symbolic backend, again comparing output byte-for-byte.

This is deterministic same-machine integrity replay, not the policy's second
independent machine.  Under the current-computer-only constraint the recorded
replay count therefore remains \(1/2\).

## Relation to the paper and remaining boundary

P2bK implements the local phase/source interface used by Theorem V2: it turns
the earlier algebraic local graph bounds into a fixed, positive-orientation
Kato phase and a rigorously bounded true source circle.  This makes the source
objects needed by the later selected-homoclinic validation explicit and
machine checkable.

It does not prove the selected positive-parameter homoclinic, its first
symmetry hit or transversality; those are P2c.  It also does not validate the
exact saddle chart, event atlas, either noncompact end, V5 matching, V6
component census, temporal stability, dynamical Turing selection, or a
finite-parameter canard.  None of those later stages was started as part of
this archive.

The proof mechanism and frozen formulas are in
[`P2_VALIDATION_CONTRACT.md`](P2_VALIDATION_CONTRACT.md).  Reproduction uses
the `p2-kato` command documented in [`README.md`](README.md).
