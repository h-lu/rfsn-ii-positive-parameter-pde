# Issue #7 staged rigorous validation

This directory is the claim-isolated, outward-rounded validation lane for the
van der Pol application.  It does not upgrade the floating candidate contract
in `validation/`, and it does not modify or silently import the read-only
flagship repository.

The runner has six executable scopes:

1. `preflight` verifies the pinned source/toolchain bindings and executes a
   CAPD/FILIB rounding self-test;
2. `kernel` additionally verifies the exact V1 polynomial identities and the
   V2(1) wedge, positivity, and saddle-focus inequalities on the frozen
   positive-width rational parameter box;
3. `local-graph` verifies the P2a moving eigenframe, isolating block,
   difference cone, true coarse local stable/unstable graphs, quadratic value
   bound, and backward decay rate on the frozen comparison bridge from
   `r=0` through the target box;
4. `h10-c01` reruns the frozen exact H10 homological recursion and verifies
   the P2b0 Euclidean \(C^0\) and Frobenius \(C^1\) tubes for those true graphs
   on the same bridge;
5. `p2-jets` verifies the P2b pure state \(C^2/C^3\) tensor bounds, the full
   rectangular \(D_b^{\le3}D_\theta^{\le2}\) weighted half-orbit recurrence,
   the induced mixed graph jets, and their physical-coordinate composition.
6. `p2-kato` fixes the absolute normalized source phase by exact Kato
   transport, verifies the physical (non-orthonormal) frame change and its
   \(C^2\) parameter bounds, and composes the already certified P2b graph jets
   with the radius-`.01` true source circle on the triangular source-jet set
   frozen for P2c.

The mathematical result of a local kernel run can be `PASS`, `FAIL`, or
`INCONCLUSIVE`.  The aggregate `final_status` remains `INCONCLUSIVE` while the
independent-machine replay required by the repository policy is pending.
Consequently every current local certificate has `claim_bearing: false`, even
when its mathematical obligations all pass.

The first clean local kernel certificate is archived at
[`results/vdp_box_v1_phase1.json`](results/vdp_box_v1_phase1.json) and explained
in [`PHASE1_REPORT.md`](PHASE1_REPORT.md).  It records integrity `PASS`,
mathematical `PASS`, aggregate `INCONCLUSIVE`, and `claim_bearing: false`.

The P2 obligation map, exact moving frame, non-circular graph bootstrap, and
the boundary between the staged local-graph obligations are frozen in
[`P2_VALIDATION_CONTRACT.md`](P2_VALIDATION_CONTRACT.md).
The first clean P2a certificate is archived at
[`results/vdp_bridge_v1_p2a_local_graph.json`](results/vdp_bridge_v1_p2a_local_graph.json)
and explained in [`P2A_REPORT.md`](P2A_REPORT.md).  Its two P2a mathematical
subobligations and all integrity checks pass; its aggregate status remains
`INCONCLUSIVE` and non-claim-bearing for the reasons above.

The first clean P2b0 certificate is archived at
[`results/vdp_bridge_v1_p2b_h10_c01.json`](results/vdp_bridge_v1_p2b_h10_c01.json)
and explained in [`P2B0_REPORT.md`](P2B0_REPORT.md).  Exact H10 regeneration,
the \(C^0\) tube, the \(C^1\) tube, and all integrity checks pass.  The parent
mixed-jet and weighted-half-orbit obligations remain pending, and the local
certificate remains non-claim-bearing while independent replay is 1/2.

The first clean P2b mixed-jet certificate is archived at
[`results/vdp_bridge_v1_p2b_jets.json`](results/vdp_bridge_v1_p2b_jets.json)
and explained in [`P2B_JETS_REPORT.md`](P2B_JETS_REPORT.md).  Every P2b
coefficient, higher-state-tensor, complete mixed-jet, and weighted-half-orbit
obligation passes, so the local parents `V2.WU.JETS` and `V2.WU_GRAPH` pass as
well.  Its aggregate remains `INCONCLUSIVE` and non-claim-bearing solely
because the current-computer-only lane supplies one of two required
independent machines.  The subsequent `p2-kato` scope now implements the
separate normalized Kato source-phase interface: exact symbolic identities,
outward-rounded frame and parameter bounds, and the frozen true-source jet
triangle.  Its clean result is archived separately only after the
implementation source is committed; P2c remains the next unimplemented
scope.

## Frozen phase-1 box

[`config/vdp_box_v1.json`](config/vdp_box_v1.json) freezes

\[
 r\in[1/25,2/25],\qquad
 a_2\in[-1/4,1/4],\qquad
 \epsilon\in[4/5,6/5].
\]

The box was selected before interval validation from the already frozen
floating slices.  A failed or inconclusive validation must not rewrite it.
A changed box requires a new versioned file and an explicit reason.

## Frozen P2 comparison bridge

[`config/vdp_bridge_v1.json`](config/vdp_bridge_v1.json) freezes

\[
 r\in[0,2/25],\qquad
 a_2\in[-1/4,1/4],\qquad
 \epsilon\in[4/5,6/5].
\]

The `r=0` face is the desingularized selected core anchor.  It is not a
positive PDE parameter value.  A gap-free bridge is needed to prove that a
positive-parameter root is the continuation of the selected core branch,
rather than an unrelated root found only inside the target box.  The P2a
block and its acceptance gates are independently frozen in
[`config/vdp_p2_local_graph_v1.json`](config/vdp_p2_local_graph_v1.json).
The P2b0 center, \(C^0/C^1\) radii, symbolically differenced residual,
and acceptance margins were preregistered independently in
[`config/vdp_p2_h10_c01_v1.json`](config/vdp_p2_h10_c01_v1.json).  Freezing
that file was not itself a validation result; the later clean result is the
separately archived certificate cited above.
The P2b coefficient grid, norms, complete jet rectangle, state-tensor radii,
parameter normalization, and all acceptance gates are separately frozen in
[`config/vdp_p2_jets_v1.json`](config/vdp_p2_jets_v1.json).  The P2b kernel
uses the already archived P2a and P2b0 certificates as immutable
prerequisites; it does not reinterpret the H10 second or third derivatives as
true-graph bounds.
The P2bK Kato normalization, parameter grid, 28 interval gates, nine
true-source gates, source radius and admissible source multiindices are
independently frozen in
[`config/vdp_p2_kato_v1.json`](config/vdp_p2_kato_v1.json).  Its exact audit
proves the symbolic projector, Kato transport, frame-change, reverser and
source-circle identities before any interval outcome is known.  Its Python
executable and cache-free SymPy source tree form a separate P0 trust boundary:
their versions, executable hash, deterministic length-prefixed source-tree
digest, and file count are frozen in `dependency.lock.json`; `__pycache__`
and `.pyc` are excluded from the digest and bypassed at execution through a
fresh empty `PYTHONPYCACHEPREFIX`.  The interval probe then imports only the
immutable physical P2b jet upper endpoints from
the archived P2b certificate, and the checker independently recomputes the
declared composition recurrences.  This scope deliberately does not claim a
full rectangular fourth-order source jet, an orthonormal physical frame, or
the later full symplectic completion.

## Strict replay

Build the pinned CAPD source in a separate build directory using every flag
and CMake option in `dependency.lock.json`, including
`CMAKE_EXPORT_COMPILE_COMMANDS=ON`.  The runner rejects a mismatched source,
backend, compiler, build mode, or archive provenance, and scans every entry of
`compile_commands.json` for the mandatory and forbidden flags.  With
`CAPD_SOURCE`, `CAPD_BUILD`, and `FLAGSHIP_REPOSITORY` replaced by local paths,
the replay commands are:

```bash
python3 validation/rigorous/run_validation.py preflight \
  --allow-dirty \
  --capd-source CAPD_SOURCE \
  --capd-config CAPD_BUILD/bin/capd-config \
  --flagship-repository FLAGSHIP_REPOSITORY \
  --report /tmp/rfsn-vdp-rigorous-preflight.json

python3 validation/rigorous/run_validation.py kernel \
  --allow-dirty \
  --capd-source CAPD_SOURCE \
  --capd-config CAPD_BUILD/bin/capd-config \
  --flagship-repository FLAGSHIP_REPOSITORY \
  --report /tmp/rfsn-vdp-rigorous-kernel.json

python3 validation/rigorous/run_validation.py local-graph \
  --allow-dirty \
  --capd-source CAPD_SOURCE \
  --capd-config CAPD_BUILD/bin/capd-config \
  --flagship-repository FLAGSHIP_REPOSITORY \
  --report /tmp/rfsn-vdp-rigorous-p2a-local-graph.json

python3 validation/rigorous/run_validation.py h10-c01 \
  --allow-dirty \
  --capd-source CAPD_SOURCE \
  --capd-config CAPD_BUILD/bin/capd-config \
  --flagship-repository FLAGSHIP_REPOSITORY \
  --report /tmp/rfsn-vdp-rigorous-p2b-h10-c01.json

python3 validation/rigorous/run_validation.py p2-jets \
  --allow-dirty \
  --capd-source CAPD_SOURCE \
  --capd-config CAPD_BUILD/bin/capd-config \
  --flagship-repository FLAGSHIP_REPOSITORY \
  --report /tmp/rfsn-vdp-rigorous-p2b-jets.json

python3 validation/rigorous/run_validation.py p2-kato \
  --allow-dirty \
  --capd-source CAPD_SOURCE \
  --capd-config CAPD_BUILD/bin/capd-config \
  --flagship-repository FLAGSHIP_REPOSITORY \
  --report /tmp/rfsn-vdp-rigorous-p2b-kato.json

python3 validation/rigorous/check_certificate.py \
  /tmp/rfsn-vdp-rigorous-kernel.json

python3 validation/rigorous/check_certificate.py \
  /tmp/rfsn-vdp-rigorous-p2a-local-graph.json

python3 validation/rigorous/check_certificate.py \
  /tmp/rfsn-vdp-rigorous-p2b-h10-c01.json

python3 validation/rigorous/check_certificate.py \
  /tmp/rfsn-vdp-rigorous-p2b-jets.json

python3 validation/rigorous/check_certificate.py \
  /tmp/rfsn-vdp-rigorous-p2b-kato.json
```

Omit `--allow-dirty` for a clean replay.  A report path is observed only after
the source-dirty check and is explicitly excluded from that pre-write
observation in the certificate; the report is never a source input.  A dirty
development run cannot be release-eligible.

For a P2b jets or P2bK certificate, the checker also materializes the probe and
its local support files from the certificate's frozen source commit,
reconstructs the recorded strict compile command, reruns the exact frozen
argument vector, and compares stdout byte-for-byte.  For P2bK it additionally
replays the 56 exact symbolic checks and recursively validates the archived
P2b prerequisite.  This same-machine replay prevents coordinated edits of a
certificate's raw atomics, stored stdout, and stored stdout hash.  It is an
integrity check of one run, not the policy's second independent-machine
replay: a current-computer-only result still records one of two required
machines and remains non-claim-bearing.

The pinned GCC toolchain must compile both CAPD/FILIB and the probes with
`-fno-ipa-pure-const`.  Without it, GCC 15 interprocedural analysis can treat
CAPD's floating-environment-sensitive `DoubleRounding::test()` as pure and
eliminate calls across successive rounding-mode changes; the optimized
`DoubleRounding::isWorking()` then returns false even though separately called
mode probes report up/down/cut/nearest correctly.  The legacy self-test is a
mandatory test: such a build is `INCONCLUSIVE`, not silently accepted.

## Evidence boundary

A phase-1 kernel `mathematical_status: PASS` supports only:

- the exact V1 reversibility, anti-symplectic primitive, and Hamiltonian
  polynomial identities encoded by the source-only kernel; and
- the explicit V2(1) parameter inequalities and saddle-focus spectral gap on
  the frozen box.

A P2a local-graph `mathematical_status: PASS` additionally supports only:

- the nonsingular closed-form moving real eigenframe and strict local block
  faces/difference cone on the complete comparison bridge; and
- true reversible local stable/unstable graphs on the radius-`.01` disk with
  Lipschitz constant at most one, a quadratic value coefficient below `1/4`,
  and backward coordinate decay rate above `2/3`.

A P2b0 H10-centered `mathematical_status: PASS` additionally supports only:

- byte-identical regeneration and structural audit of the frozen degree-ten
  exact center and its exact invariance-defect term table; and
- the uniform bounds
  \(\lVert H_\mu-H_{10}\rVert_2\le5\times10^{-6}\) and
  \(\lVert DH_\mu-DH_{10}\rVert_F\le3\times10^{-4}\) on the complete
  comparison bridge, plus the reversible stable analogue.

A P2b jets `mathematical_status: PASS` additionally supports only:

- true-graph state derivative bounds through order three and the full
  rectangular parameter/mixed bounds through order two in the frozen norm;
- weighted unstable and reversible stable half-orbit jet bounds at weight
  `1/4`, in moving and physical coordinates; and
- the local parent `V2.WU_GRAPH`, conditional on the immutable P2a and P2b0
  prerequisite certificates.

A P2bK `mathematical_status: PASS` additionally supports only:

- exact normalized Riesz-projector and Kato-transport identities tied to the
  frozen flagship definitions, with the transported direction anchored at the
  selected core face;
- uniform value and first/second parameter bounds for the physical Kato frame
  and its change from the algebraic P2b frame; and
- the radius-`.01` true graph-boundary source and the nine frozen
  parameter/source derivatives obtained from the certified P2b graph jets.

Before a P2b jets pass, neither P2a nor P2b0 alone supplies those bounds.  In
particular, a bound on \(D^2H_{10}\) is a bound on the polynomial center, not
on \(D^2H_\mu\).

Even a P2bK pass does not assert that its physical frame is orthonormal, does
not supply the later symplectic completion, and does not validate the
positive-parameter homoclinic, exact saddle chart, event atlas, either
noncompact end, V5 matching, V6 component census, all winding numbers,
temporal stability, Turing selection, or canard identification.  Those
obligations are enumerated in `obligations.json`.
