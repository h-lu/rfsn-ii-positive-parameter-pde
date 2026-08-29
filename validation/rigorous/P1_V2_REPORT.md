# Issue #7 v2 P1 interval-kernel report

**Evidence status:** implementation and freeze semantics complete; the clean
source-bound certificate is generated only after this checker revision is
committed.  A dirty development run has passed and is not retained as
mathematical evidence.

## Scope

The P1 target is the frozen replacement box

\[
 [1/100,1/50]\times[-1/4,1/4]\times[4/5,6/5].
\]

The unchanged C++ kernel checks the exact V1 reversibility and Hamiltonian
identities and the three V2(1) interval atoms: the two wedge inequalities,
positivity of the physical parameters, and the uniform saddle-focus bounds.
It receives the exact argument vector

```text
1 100 1 50 -1 4 1 4 4 5 6 5
```

This run is necessary: the v1 positive interval
\([1/25,2/25]\) and the v2 positive interval
\([1/100,1/50]\) are disjoint, so the v1 P1 certificate cannot be restricted
to v2.

## Freeze and evidence semantics

The v2 target was chosen after the disclosed historical P2c exploratory log
had been inspected.  Its integrity atom is therefore
`BOX.V2.FROZEN_DISCLOSED`: the one allowed replacement target was frozen
before the first retained v2-target-specific outward-rounded output.  The old
`BOX.FROZEN` predicate, which says selection preceded interval inspection, is
not used.

Certificate schema version `/2` is restricted to `V1_V2_1_KERNEL` and to
`vdp-positive-box-v2`; schema version `/1` remains restricted to v1.  All P2
runner scopes reject `--box-version v2` until their separate restriction
certificate is supplied.

## Checker closure

The v2 path checks all of the following rather than trusting coordinated JSON
fields:

- the v2 freeze audit, exact box path, identifier, endpoints, hashes, tag, and
  replacement-box disclosure;
- the exact raw top-level field set and raw enclosure-name sets;
- containment of all three exact rational parameter intervals by the raw
  outward-rounded enclosures;
- independent strict-positive reduction of every V2(1) margin atom;
- equality of duplicate raw/top-level enclosures and statuses;
- the exact stored stdout and its digest; and
- reconstruction, recompilation, and byte-for-byte replay of the frozen C++
  source with the locked compiler, CAPD/FILIB archives, flags, environment,
  and argument vector.

The last check is same-machine run integrity, not the policy-required replay
on a genuinely distinct machine.

## Claim boundary

A local mathematical `PASS` closes only V1 and V2(1) on the v2 positive box.
It does not close V2(2)--(5), the event atlas, either noncompact end,
matching, V6, temporal stability, Turing selection, or canard identification.
Until a second independent machine is archived, the final status remains
`INCONCLUSIVE`, `claim_bearing=false`, and `release_eligible=false`.

## Reproduction

After committing the source lane, run from a clean checkout:

```bash
python3 -B validation/rigorous/run_validation.py kernel \
  --box-version v2 \
  --capd-source /tmp/rfsn-vdp-capd-strict-7310792 \
  --capd-config /tmp/rfsn-vdp-capd-strict-7310792/build-strict/bin/capd-config \
  --flagship-repository /home/hblu/Documents/Codex/2026-08-22/reversible-rfsn-ii-waves \
  --report validation/rigorous/results/vdp_box_v2_phase1.json

python3 -B validation/rigorous/check_certificate.py \
  validation/rigorous/results/vdp_box_v2_phase1.json
```

