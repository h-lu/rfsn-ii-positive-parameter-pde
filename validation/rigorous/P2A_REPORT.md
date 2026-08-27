# Issue #7 P2a local-graph validation report

The first clean-source P2a run completed on 2026-08-27.  Its machine-readable
certificate is
[`results/vdp_bridge_v1_p2a_local_graph.json`](results/vdp_bridge_v1_p2a_local_graph.json).

## Verdict

| Layer | Status | Meaning |
|---|---|---|
| Source, dependency, bridge, configuration, and rounding integrity | `PASS` | The clean local source commit, read-only flagship Git objects, strict CAPD/FILIB build, 13 rounding tests, frozen target box, complete comparison bridge, and preregistered P2a gates all match their recorded hashes. |
| `V2.WU.FRAME_BLOCK` | `PASS` | The exact moving-frame identities, nonsingularity, radius-`.01` isolating faces, and strict difference cone hold on the whole bridge. |
| `V2.WU.COARSE_GRAPH` | `PASS` | The non-circular block-extension and variation-of-constants bootstrap give true reversible local graphs, the declared quadratic value bound, and the declared backward decay rate on the whole bridge. |
| Parent `V2.WU_GRAPH` | `PENDING` | The required state-three/parameter-two mixed jets and weighted half-orbit constants are P2b, not P2a. |
| Independent replay | `PENDING_REQUIRED` | One of the two policy-required distinct machines has been observed. |
| Aggregate | `INCONCLUSIVE` | The local mathematical result is not upgraded to a claim-bearing certificate before independent replay and completion of its parent obligation. |

Thus `mathematical_status=PASS`, `integrity_status=PASS`,
`final_status=INCONCLUSIVE`, `claim_bearing=false`, and
`release_eligible=false`.  The aggregate `INCONCLUSIVE` does not mean that a
P2a interval crossed a decision boundary; every implemented P2a mathematical
gate passed.

## Frozen domain and strict margins

The selected-continuation bridge is

\[
 r\in[0,2/25],\qquad
 a_2\in[-1/4,1/4],\qquad
 \epsilon\in[4/5,6/5].
\]

Its complete `r=0` face is the desingularized selected-core anchor.  The
positive target box is the subbox with \(r\ge1/25\).  Representative
outward-rounded enclosures are

\[
\begin{aligned}
4-c^2&\in[3.9983997756449758,4],\\
\alpha&\in[0.69999999999999996,0.71414333371170946],\\
\beta&\in[0.699999499224911,0.7141428428542852],\\
m_{\rm face}&\in[0.0067999225837089604,
                   0.0069414613805120423],\\
m_{\rm cone}&\in[1.319967163549846,
                   1.3482978847813969],\\
K_0&\in[0.9511442617866226,0.9712568937532169],\\
K_1&\in[0.2389436259648727,0.2440161679672436],\\
\gamma_1&\in[0.694900547450087,0.70904848143278365],\\
\gamma_1-\tfrac23&\in[0.02823388078342004,
                        0.042381814766117243].
\end{aligned}
\]

In particular, the complete radius-`.01` true unstable graph has Lipschitz
constant at most one and

\[
 \lVert H_\mu(u)\rVert\le K_1\lVert u\rVert^2
 <\tfrac14\lVert u\rVert^2,
\]

uniformly on the bridge.  Reversibility supplies the corresponding stable
graph, and the unstable coordinate has certified backward decay rate greater
than \(2/3\).

## Reproducibility boundary

The certificate was generated from clean source commit `83bd821847e7`, using
the pinned CAPD source commit `731079217a92` with FILIB and GCC 15.2.0.  All
90 CAPD compilation-database entries satisfy the strict floating-environment
flag policy.  The flagship repository was accessed read-only through locked
Git objects at commit `d54add098545` and was not modified.

The proof contract, including the exact frame and the radial block-extension
lemma that closes the true-graph argument, is
[`P2_VALIDATION_CONTRACT.md`](P2_VALIDATION_CONTRACT.md).  The certificate
binds the exact bridge, configuration, probe source, obligation predicates,
compiler invocation, linked archives, and hexadecimal interval endpoints.

## Scope not yet validated

P2a does not validate the mixed graph jets, selected parametric homoclinic,
first symmetry hit, exact marked saddle charts, event atlas, V3--V6 objects,
temporal stability, Turing pattern selection, or a finite-parameter canard.
The next ordered stage is P2b, followed by P2c--P2e; the later dynamics
questions remain downstream of Issue #7.
