# Issue #7 rigorous validation: phase 1

This directory is the claim-isolated, outward-rounded validation lane for the
van der Pol application.  It does not upgrade the floating candidate contract
in `validation/`, and it does not modify or silently import the read-only
flagship repository.

Phase 1 has two executable scopes:

1. `preflight` verifies the pinned source/toolchain bindings and executes a
   CAPD/FILIB rounding self-test;
2. `kernel` additionally verifies the exact V1 polynomial identities and the
   V2(1) wedge, positivity, and saddle-focus inequalities on the frozen
   positive-width rational parameter box.

The mathematical result of a local kernel run can be `PASS`, `FAIL`, or
`INCONCLUSIVE`.  The aggregate `final_status` remains `INCONCLUSIVE` while the
independent-machine replay required by the repository policy is pending.
Consequently a phase-1 local certificate has `claim_bearing: false`, even when
its mathematical obligations all pass.

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

python3 validation/rigorous/check_certificate.py \
  /tmp/rfsn-vdp-rigorous-kernel.json
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

It does not validate the positive-parameter homoclinic, exact saddle chart,
event atlas, either noncompact end, V5 matching, V6 component census, all
winding numbers, temporal stability, Turing selection, or canard
identification.  Those obligations are enumerated in `obligations.json`.
