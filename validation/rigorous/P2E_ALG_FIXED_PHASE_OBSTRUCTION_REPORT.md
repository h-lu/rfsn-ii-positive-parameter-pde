# P2e ALG fixed-phase finite-gate cover obstruction

**Status:** `COMPUTED_INTERVAL_DESIGN_INCONCLUSIVE`, `claim_bearing=false`.
This report records where the present interval representation fails to cover
one V2 finite-gate cell. It is neither a proof that this finite-gate trace is
absent nor a proof that the positive-parameter algebraic channel is absent.

## The checked target cell

The fixed-phase ALG runner was tested on the exact parent

\[
 [1/100,1/80]\times[-1/4,-63/256]\times[4/5,9/10],
\]

which is the lower-\(r\), lower-\(a_2\), lower-\(\epsilon\) corner cell of
the frozen v2 theorem box. Each of its eight canonical \(r\)-leaves passed
the true-\(W^u\) source interval Newton. After root conditioning, however,
all 128 terminal leaves at the predeclared maximum \(a_2\)-depth four failed
to give an exact ALG cover. The failures occur when the reduced zero-energy
enclosure can no longer separate \(W=P^2\) from zero before the frozen
algebraic cut. The resulting parent has all eight \(r\)-leaves uncovered.

The raw 47,799-byte result is intentionally outside Git:

```text
/tmp/p2e-alg-target-corner-r4-a0-e0-fixed-phase.json
SHA-256 ed4b9fd7b85b165e3d3bd8fe6134dcc7dd3fbf8bbb954ba10eb8d9445ee53d61
```

It records `status=INCONCLUSIVE`, eight passing root-conditioned sources,
128 terminal failures, and one exact-cover error. The bound executable
hashes are `644765e1...f96b` for the terminal kernel and
`866c3871...86cf` for the source kernel.

## What this run does and does not test

The zero-parameter anchor enclosure is

\[
 [5.7566913947049203,5.7566913967948983]
\]

and the runner tests its full fixed protected aperture

\[
 [5.7566912822049203,5.7566915092948983],
\]

obtained by adding the frozen radius \(9/80000000\) at both ends. This fixed
label is an authorized V2 object:
Theorem V2 continues the finite-gate anchors as points carrying the same
transported labels on the moving source circle. Thus the current runner is
a legitimate attempt to validate the zero-action axis of the fixed
`C.A`/`ALG_GATE_V2` aperture. Its failure is computationally
`INCONCLUSIVE`: the independent interval enclosure loses the separation
\(W>0\), and no orbit nonexistence statement follows.

The word *gate* is essential. V2 does not assert that this finite-gate anchor
enters the positive-parameter infinite algebraic end. That stronger object is
selected later in V5 by the two-dimensional incidence equation

\[
 \mathfrak M_\mu(\phi,t)=0,
\]

which yields a generally moving phase \(\phi_a(\mu)\) and flight time
\(t_a(\mu)\). No theorem identifies \(\phi_a(\mu)\) with the fixed V2 label
\(\phi_a^0\).

The repository's existing
[energy-preserving matched calculation](../../numerics/P2E_V2_ENERGY_MATCHED_REPORT.md)
and [seven-point axis continuation](../../numerics/P2E_V2_AXIS_CONTINUATION_REPORT.md)
expose the same interface numerically. At
\((r,a_2,\epsilon)=(3/200,0,1)\) the matched algebraic phase is approximately
`5.7567672233`; at the two \(a_2\) endpoints it is approximately
`5.7350866190` and `5.7783800372`. These floating centerlines show that the
V5 matched anchor moves substantially; they are candidate evidence, not
interval enclosures.

Deeper \(a_2\) subdivision could still be useful if the sole target were the
V2 fixed-label finite-gate axis. It is not the recommended next calculation:
the present loss comes from discarded source-to-terminal correlations, and
even a successful fixed-label cover would not prove the distinct V5 matched
coincidence or the infinite algebraic exit.

## The two objects that must remain separate

The validation ledger must retain both of the following rows.

1. `ALG_GATE_V2`: the fixed transported label \(\phi_a^0\), its V2 finite
   gate aperture, and a finite first-hit cover. The current run is an
   unsuccessful cover attempt for this row, not a refutation of it.
2. `ALG_MATCH_V5`: the moving solution \((\phi_a(\mu),t_a(\mu))\) of
   \(\mathfrak M_\mu=0\), followed into the V4 future-staying graph and
   pulled back as the actual algebraic label used in V6.

For the V5/V6 matched exit, the next claim-relevant calculation is the second
row. On the actual target \(r\in[1/100,1/50]\), rather than the unused lower
half of the comparison bridge, it must bind:

1. the parameter-dependent true-\(W^u\) source trace;
2. the finite-\(r\) future-staying algebraic graph at a fixed outer section;
3. the transverse two-variable source-to-graph coincidence, followed by the
   finite-cut first-hit and sign checks.

Only after that coincidence is enclosed may a moving phase tube be used for
`ALG_MATCH_V5`; it must not silently replace the fixed label in
`ALG_GATE_V2`. The explicit-box validation of `ALG_GATE_V2` remains open and
must be closed independently if it is retained in the V2 atlas. The POLE
full-bridge result is unchanged: its protected phase
aperture is a different robust finite channel and does not supply the missing
algebraic coincidence.
