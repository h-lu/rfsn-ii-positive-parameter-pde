# Issue #7 P2e phase-order fail-fast report

**Result: `vdp-positive-box-v1` fails the frozen V2(5) phase-order gate.**

Theorem V2(5) requires, in one transported Kato phase lift,

\[
 \phi_h-\phi_a>0.052407.
\]

The already selected P2c homoclinic branch was reevaluated by the bound
CAPD/FILIB executable on one exact cell of the previously archived P2c
rational grid,

\[
 r\in[31/400,2/25],\qquad
 a_2\in[-1/4,-63/256],\qquad
 \epsilon\in[11/10,6/5].
\]

The strict multiple-shooting/Krawczyk computation passes and encloses its
absolute P2bK source phase by

\[
 \phi_h\in
 [5.7499112495191298,5.7566768761372131].
\]

The immutable algebraic certificate gives

\[
 \phi_a\in
 [5.7566913947049203,5.7566913967948983].
\]

Both numbers are labels in the common transported Kato source-phase lift.
The formula `phi_algebraic=phi+chi(c)` instead describes how that label is
embedded in the algebraic graph coordinates; adding `chi` to the logged
number would compare the wrong quantities.  The continued algebraic-directed
anchor is defined by retaining its frozen transported Kato label on the
moving source circle.  Therefore the complete cell satisfies

\[
 \sup\phi_h<\inf\phi_a,
 \qquad
 \inf\phi_a-\sup\phi_h
 \ge 0.0000145185677072.
\]

Thus the cyclic order is reversed on this cell; the requested positive gap
does not merely lack a proof.  Its best possible value on the two enclosures
is at most `-0.0000145185677072`, leaving a shortfall of at least
`0.0524215185677072`.  The mathematical status of
`V2.ATLAS.PHASE_GAP_AH` and hence of the frozen v1 box is `FAIL`.

The raw one-cell output is archived in
[`design/logs/p2e_phase_order_fail_v1.log`](design/logs/p2e_phase_order_fail_v1.log).
[`p2e_phase_order_fail.py`](p2e_phase_order_fail.py) verifies the source,
binary/log bindings, P2c prerequisite, immutable algebraic certificate,
common phase convention, and strict interval comparison.  On 2026-08-29 the
bound strict binary was rerun locally and reproduced the archived stdout
byte for byte.

The target box and comparison bridge were frozen before interval validation;
the P2c grid evidence itself was frozen retrospectively before its local
certificate, as its own configuration records.  This result stops full P2e
and P3--P5 computation for
`vdp-positive-box-v1`.  It does **not** contradict the analytic theorem for
sufficiently small positive \(r\), and it does not authorize silently
shrinking the box.  A replacement v2 box or a theorem with changed event
ordering is a new, explicitly versioned target.  Independent-machine replay
is still pending, so this certificate remains non-claim-bearing under the
repository release policy.

Recheck the committed evidence with

```bash
python3 -B validation/rigorous/p2e_phase_order_fail.py \
  --check-result validation/rigorous/results/vdp_box_v1_p2e_phase_order_fail.json
```

When the exact recorded executable is available, add
`--strict-binary PATH` to rerun the cell and demand byte-identical stdout.
