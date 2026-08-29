# P2a--P2d restriction contract for the v2 bridge

## Purpose

This lane records a logical restriction of already certified statements; it
is not a second interval computation.  Its source domain is the frozen v1
comparison bridge

\[
[0,2/25]\times[-1/4,1/4]\times[4/5,6/5],
\]

and its target is the frozen v2 comparison bridge

\[
[0,1/50]\times[-1/4,1/4]\times[4/5,6/5].
\]

Every inherited P2 statement is uniform on the source bridge.  Hence it
remains true, with the same constants, on the exact target subset.  The
checker does not use a heuristic monotonicity of interval output, recompute a
hull, integrate an ODE, or change normalized coordinates.

## Frozen inputs and derived scope

[`config/vdp_p2_v2_restriction.json`](config/vdp_p2_v2_restriction.json)
binds the annotated freeze tag `vdp-issue7-box-v2-freeze`, tag object
`13acd7095a7fbe8bb24985acf0dd449ee6049041`, and peeled commit
`8ba7ffc0bb2cdced0c904ff6dfa319e4a5bd9b2b`.  It also binds every v1
certificate, bridge and box, relevant historical validator, P2d proof source,
and P2d lightweight checker to the corresponding Git blob at that commit.
The v1 generic validator is loaded directly from its authenticated baseline
blob because the v2 P1 lane legitimately extends the current file at the same
path.  Every other frozen input must still match both baseline and current
bytes.  The new checker and result schema are self-bound by SHA-256.

The derived scope has 32 atoms:

- P2a: 2 local-graph atoms;
- P2b0: 3 exact-center and \(C^0/C^1\)-tube atoms;
- P2b: 6 coefficient, state-jet, mixed-jet, half-orbit, and graph atoms;
- P2bK: 7 Kato/source-interface atoms;
- P2c: 6 homoclinic-branch atoms;
- P2d: 7 chart children and the parent `V2.EXACT_CHART`.

The checker recursively validates the six historical certificates.  P2a
through P2bK use the historical generic checker; P2c uses its schema and
semantic reconstruction.  The P2d frame's historical compile command embeds
an absolute path, so worktree relocation cannot reproduce that path string.
The restriction checker instead applies the downstream relocation-safe frame
authentication: schema, exact certificate bytes, embedded raw stdout,
source hashes, bridge, grid, margins, and exact-algebra audit.  It then runs
the lightweight terminal P2d checker, which recursively checks the remaining
six chart children and the parent.

## Exact domain and cover checks

The old normalization is retained:

\[
\theta_r=25r-1,\qquad \theta_a=4a_2,\qquad
\theta_\epsilon=5(\epsilon-1).
\]

Thus the v2 bridge has \(\theta_r\in[-1,-1/2]\), and the v2 positive box
has \(\theta_r\in[-3/4,-1/2]\).  The old v1 positive box is disjoint from
the v2 positive box and is explicitly not inherited.  P1 must therefore be
validated separately on v2.

The old P2d two-member cover restricts differently from the other universal
statements.  Only its anchor member meets the v2 bridge.  The positive member
and the old nonempty overlap \(\theta_r\in[0,1/4]\) are disjoint from v2.
Consequently the transition condition on v2 is vacuous: this is a one-chart
restriction, not a claim that a nonempty two-chart overlap exists inside v2.
The parent exact-chart result is inherited because all cover members were
already restrictions of one global normalized Moser family and all seven
restricted child statements pass.

Grid arithmetic is checked only to make the restriction auditable.  The v2
subset selects 256 P2b cells, 128 P2bK cells, 128 P2d-frame cells, and 4096
P2c cells with 10,720 internal faces.  These counts identify exact subcomplexes
of the historical covers; they are not new numerical enclosures or sharper
worst-cell claims.

## Status and nonclaims

A successful deterministic reconstruction reports
`RESTRICTED_LOCAL_MATHEMATICAL_PASS`.  It deliberately remains
`final_status=INCONCLUSIVE`, `claim_bearing=false`, and
`release_eligible=false`, because the inherited evidence still has only one
of the two required independent-machine replays.

This lane does not establish P1 on `vdp-positive-box-v2`, P2e phase order or
the complete event atlas, sharper v2 constants, or a new interval/ODE run.
No result certificate is checked in at this source-freeze stage.

## Deterministic check

Build a disposable preview and validate it by exact reconstruction:

```bash
python3 -B validation/rigorous/p2_v2_restriction.py build \
  > /tmp/vdp-p2-v2-restriction-preview.json
python3 -B validation/rigorous/p2_v2_restriction.py check \
  /tmp/vdp-p2-v2-restriction-preview.json
python3 -B -m unittest \
  validation.rigorous.tests.test_p2_v2_restriction -v
```

The result schema is
[`p2_v2_restriction.schema.json`](p2_v2_restriction.schema.json).  A later
archival result must be generated from a clean, committed source snapshot and
must not change the claim or replay boundary above.
