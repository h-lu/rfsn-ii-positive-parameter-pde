# Issue #7: v2 three-phase-gap strict replay report

**Result: all three frozen scalar phase gaps pass on the v2 comparison
bridge, but the complete P2e event-atlas claim remains pending.**

The frozen positive target is

\[
 r\in[1/100,1/50],\qquad
 a_2\in[-1/4,1/4],\qquad
 \epsilon\in[4/5,6/5],
\]

and its comparison bridge extends the radial interval to
\(r\in[0,1/50]\).  The eight predeclared radial slabs cover that bridge
without gaps.  Each slab contains \(128\times4=512\) transverse cells, so
the retained strict replay covers all 4096 frozen cells.

## Retained formal replay

The first complete retained formal replay was run from repository commit
`8ba7ffc0bb2cdced0c904ff6dfa319e4a5bd9b2b` with the bound executable

```text
sha256(/tmp/p2c-homoclinic-audit)
= 1d5b8092148d2a9cf1892e0880c01bd122edf03421f168142585818a5f3e9c7e
```

using

```bash
python3 -B validation/rigorous/p2e_phase_order_v2.py \
  --strict-binary /tmp/p2c-homoclinic-audit \
  --output validation/rigorous/results/vdp_box_v2_p2e_phase_order.json
```

The checker reran every slab and required the executable stdout to agree
byte for byte with the eight retained logs.  All eight slab terminals were
`PASS`.  The complete checker invocation exited with code zero after
5516.96 seconds (about 91 minutes 57 seconds); the measured peak resident
set size was 28,980 kB.  No second strict replay was used to obtain this
report.

The resulting certificate is
[`results/vdp_box_v2_p2e_phase_order.json`](results/vdp_box_v2_p2e_phase_order.json),
with SHA-256

```text
45e55e81817612af8ddbdd44f256ee6309e7e1df6328ff6945cd00a89a1e00ff
```

## Strict phase inequalities

All phases below use the same transported Kato source-phase lift.  The
strict replay gives

\[
 \phi_a\in
 [5.7566913947049203,5.7566913967948983],
\]

\[
 \phi_h\in
 [5.8339105054727822,5.8888259815044703],
\]

on both the complete comparison bridge and the positive v2 target, together
with the frozen lifted lower pole endpoint \(\phi_p^->6.08318\).  Hence:

| local subatom | required lower bound | strict lower bound | certified margin | status |
|---|---:|---:|---:|---|
| `V2.ATLAS.PHASE_GAP_AH` | `0.052407` | `0.0772191086778839` | `0.0248121086778839` | `PASS` |
| `V2.ATLAS.PHASE_GAP_AP` | `0.16324` | `0.3264886032051017` | `0.1632486032051017` | `PASS` |
| `V2.ATLAS.PHASE_GAP_HP` | `0.110835` | `0.1943540184955297` | `0.0835190184955297` | `PASS` |

Thus the local certificate status is
`PASS_THREE_PHASE_GAPS_ONLY`, and its integrity status is
`PASS_STRICT_BINARY_REPLAY`.

## Attempt and evidence disclosure

After the freeze and before the complete retained formal replay, two
executions were started and terminated before producing usable numerical
output.  Their stdout artifacts were zero bytes.  They are
zero-output non-evidence attempts: they were not parsed, retained as
certificates, or used to select or modify the target.  They must not be
confused with the first complete retained formal replay documented above.

The frozen configuration already records its separate pre-freeze accidental
attempt and its zero-output classification.  This report does not alter that
hash-bound configuration, nor does it retroactively promote any incomplete
attempt to evidence.

## Claim boundary

This computation proves only the three frozen scalar phase-gap subatoms.  It
does not prove `V2.SOURCE_PHASES_AND_ORDER`, `V2.EVENT_ATLAS`, or any of the
four proposed local atlas parent atoms, because the complete event-face
manifest, incidence complex, first-event census, transported traces, and
numeric materialization choices remain pending.  Consequently the aggregate
certificate correctly remains

```text
status = INCONCLUSIVE
mathematical_status = INCONCLUSIVE
claim_bearing = false
release_eligible = false
```

Independent-machine replay is also still pending.  No P3--P5, temporal
stability, Turing-selection, Evans-function, or canard conclusion follows
from this local result.

