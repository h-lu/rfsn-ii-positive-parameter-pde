# P2d reversible-symplectic-frame certificate report

The archived certificate
[`results/vdp_bridge_v1_p2d_symplectic_frame.json`](results/vdp_bridge_v1_p2d_symplectic_frame.json)
records the first locally mathematically discharged child of
`V2.EXACT_CHART`.  It was generated
from the clean source revision recorded in the certificate and passes the
repository's source-bound checker.

## Verdict

| Item | Status |
|---|---|
| Source, configuration, toolchain, and prerequisite integrity | `PASS` |
| Archived P2bK local prerequisite | `PASS` |
| Exact symbolic audit | `PASS` (59 checks) |
| Strict interval frame probe | `PASS` (20 gates on a \(16\times8\times4\) cover) |
| `V2.CHART.SYMPLECTIC_FRAME` | local mathematical `PASS` |
| Other six `V2.CHART.*` atoms | `OPEN` |
| Parent `V2.EXACT_CHART` | `OPEN` |
| Independent replay | `PENDING_REQUIRED` (1 of 2 distinct machines) |
| Aggregate certificate | `INCONCLUSIVE`, `claim_bearing=false`, `release_eligible=false` |

The local frame certificate remains aggregate `INCONCLUSIVE` because
independent replay is 1/2, not because a frozen frame gate failed.  Separately,
the parent `V2.EXACT_CHART` stays open because its other six theorem atoms are
not yet discharged.

## Mathematical scope

The certificate combines three separately checked inputs: the archived P2bK
positive-Kato frame prerequisite, the 59-check exact-algebra audit, and an
outward-rounded interval computation over

\[
0\le r\le \frac{2}{25},\qquad
-\frac14\le a_2\le\frac14,\qquad
\frac45\le\epsilon\le\frac65.
\]

The 512-cell probe archives componentwise value, three first-derivative, and
six symmetric second-derivative enclosures for every entry of \(L\) and
\(L^{-1}\), in normalized and original parameters.  Its 20 frozen gates check
the scalar branch margins, anchor conditioning, and the prescribed matrix-jet
norms.  Exact symplectic, inverse, reverser, action-sign, and
quadratic-conjugacy identities come from the symbolic audit rather than from
small numerical residuals.

This closes only `V2.CHART.SYMPLECTIC_FRAME`.  It does not construct the
nonlinear analytic normal form, nonlinear zero-energy branch, exact nonlinear
sections, weighted passage, physical slides, or overlap atlas.  It also makes
no claim about temporal stability, dynamic Turing-pattern selection, or
finite-parameter canard identification.

## Recheck

From the repository root, run

```bash
python3 -B validation/rigorous/p2d_frame_certificate.py check \
  validation/rigorous/results/vdp_bridge_v1_p2d_symplectic_frame.json
```

The checker replays the exact audit and rebuilds and reruns the bound interval
probe in a temporary directory with the recorded reference toolchain.  This is
a same-machine source-bound replay; it is not the still-required second-machine
replay.  The flagship abstract-theory repository remains a read-only frozen
input and was not modified.
