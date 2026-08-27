# Issue #7 staged rigorous validation

This directory is the claim-isolated, outward-rounded validation lane for the
van der Pol application.  It does not upgrade the floating candidate contract
in `validation/`, and it does not modify or silently import the read-only
flagship repository.

The runner has four executable scopes:

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
   on the same bridge.

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
the boundary between P2a and the still-pending mixed-jet parent obligation are
frozen in [`P2_VALIDATION_CONTRACT.md`](P2_VALIDATION_CONTRACT.md).
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

python3 validation/rigorous/check_certificate.py \
  /tmp/rfsn-vdp-rigorous-kernel.json

python3 validation/rigorous/check_certificate.py \
  /tmp/rfsn-vdp-rigorous-p2a-local-graph.json

python3 validation/rigorous/check_certificate.py \
  /tmp/rfsn-vdp-rigorous-p2b-h10-c01.json
```

Omit `--allow-dirty` for a clean replay.  A report path is observed only after
the source-dirty check and is explicitly excluded from that pre-write
observation in the certificate; the report is never a source input.  A dirty
development run cannot be release-eligible.

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

Neither P2a nor P2b0 encloses the true-graph state derivatives through order
three, parameter derivatives through order two, their required mixed jets,
or the weighted half-orbit constants.  The parent `V2.WU.GRAPH` obligation
therefore remains pending.  In particular, a bound on \(D^2H_{10}\) is a
bound on the polynomial center, not on \(D^2H_\mu\).

These local scopes do not validate the positive-parameter homoclinic, exact
saddle chart, event atlas, either noncompact end, V5 matching, V6 component census, all
winding numbers, temporal stability, Turing selection, or canard
identification.  Those obligations are enumerated in `obligations.json`.
