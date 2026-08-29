# Issue #7: frozen v2 positive-parameter target

The new target `vdp-positive-box-v2` is

\[
 r\in[1/100,1/50],\qquad
 a_2\in[-1/4,1/4],\qquad
 \epsilon\in[4/5,6/5].
\]

It does not replace `vdp-positive-box-v1`.  The v1 box and its strict P2e
phase-order `FAIL` remain immutable.  The v2 box is the exact image of v1
under \(r\mapsto r/4\) with the two transverse intervals fixed; it is not a
subset of the positive v1 box.  It is a strict subset of the already certified
comparison bridge `vdp-core-to-positive-bridge-v1`.

## Selection rule and evidence disclosure

The v2 target keeps the complete transverse \(a_2\)- and \(\epsilon\)-ranges
of v1 and applies one exact radial contraction by a factor of four to both
v1 endpoints.  This is the parameter direction singled out by the analytic
argument: the three source-phase gaps are established at \(r=0\), after
which the theorem decreases the sufficiently-small positive radius.  The
choice therefore tests the stated perturbative mechanism without deleting
the failed corner in \((a_2,\epsilon)\).

The four resulting radial cells are exactly cells 4--7 of the already frozen
P2c rational grid.  The historical full-bridge P2c log, including its
`phase_hull` values on these slabs, was available and inspected before this
selection.  The configuration therefore classifies v2 as a confirmatory
target selected after disclosed exploratory evidence, not as blinded
validation.  That log certifies its historical P2c root-jet scope only; it is
not relabelled as a v2 P2e result.

The parameter choice, the \(r=0\) and continuation theorem hashes, the three
unchanged phase-gap thresholds, the predecessor failure, and the containing
bridge are fixed in
[`config/vdp_box_v2.json`](config/vdp_box_v2.json).  The target was selected
before every v2-target-specific outward-rounded attempt.  The final phase
contract is frozen before the first retained evidentiary v2 output, not merely
before a future release-eligible aggregate.

One pre-freeze execution attempt was accidentally started and interrupted.
All eight stdout and eight stderr placeholders were verified to contain zero
bytes; no numerical output was emitted, inspected, or retained, and the empty
placeholders were removed.  It is recorded as
`ABORTED_ZERO_OUTPUT_NON_EVIDENCE`, not described as a completed run.  Parser
tests use blocks from the disclosed historical P2c log only as temporary test
fixtures and never promote them to v2 evidence.

The derived comparison bridge
[`config/vdp_bridge_v2.json`](config/vdp_bridge_v2.json) is the exact
rectangular hull from the complete \(r=0\) anchor face to the v2 upper face.
It is bound to the box in one direction, so the two files have no cyclic hash
dependency.  Freezing that derived bridge creates no new mathematical `PASS`.

## Inheritance and fail-closed rule

The old v1 positive-box P1 certificate cannot be restricted to v2 because the
two positive radial intervals are disjoint.  P1 must be rerun on v2.  Results
proved uniformly on the larger comparison bridge may be restricted to v2
only after their exact domains and hashes are checked.  No P2e or later
target-specific result is inherited.

This v2 target consumes the single smaller-box redesign allowed after the v1
failure.  After the first v2 result, no endpoint or transverse slice may be
tuned and no v3 shrink is allowed under the current programme.  A strict
mathematical failure stops every dependent v2 computation.  An integrity or
enclosure failure is `INCONCLUSIVE` and permits only a refinement schedule
frozen for this same target.  A genuinely different application theorem
would first require its own proof and validation scope; it is not another
shrink of v2.

The next computation is only the separately frozen P2e source-phase-order
gate.  Passing that gate will not by itself prove the complete event atlas or
any V3--V6 result.

Recheck the frozen selection contract with

```bash
python3 -B validation/rigorous/check_vdp_box_v2_freeze.py
python3 -B -m unittest validation.rigorous.tests.test_vdp_box_v2_freeze -v
```
