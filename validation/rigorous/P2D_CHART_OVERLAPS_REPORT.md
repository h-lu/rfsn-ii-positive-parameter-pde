# P2d finite-chart-overlap validation report

Date: 2026-08-29

## Outcome

The proof-bound checker gives local mathematical `PASS` for
`V2.CHART.OVERLAPS` on the frozen comparison bridge.  Since the preceding six
P2d chart atoms also pass locally, the parent `V2.EXACT_CHART` now has a
scoped local mathematical `PASS` for \(|\nu|\le 25/2^{58}\).

| Item | Status |
|---|---|
| Two-member relative finite cover | `PASS` |
| Common chart, inverse, primitive gauge, and signed axes | exact identity on overlaps |
| Oriented-blow-up and transported-slide transitions | full state-\(C^3\), parameter-\(C^2\) rectangle; `PASS` |
| Physical source-phase seam and inverse | mixed total order \(\le3\), parameter order \(\le2\), degree \(+1\); `PASS` |
| `V2.CHART.OVERLAPS` | local mathematical `PASS` |
| Parent `V2.EXACT_CHART` | local mathematical `PASS` |
| Complete event atlas `V2.EVENT_ATLAS` (P2e) | `OPEN` |
| Repository aggregate | `INCONCLUSIVE`, `claim_bearing=false`, replay `1/2` |

## What was proved

Normalize the bridge by

\[
 r=(1+\theta_r)/25,
 \qquad a_2=\theta_a/4,
 \qquad \epsilon=1+\theta_\epsilon/5.
\]

The closed members \(V_0=\{\theta_r\le1/4\}\) and
\(V_+=\{\theta_r\ge0\}\) cover the normalized cube and are relatively
compact in \(U_0=\{\theta_r<1/2\}\) and
\(U_+=\{\theta_r>-1/4\}\), respectively.  Their normalized collar is
\(1/4\), their original \(r\)-collar is \(1/100\), and their closed overlap
has \(0\le\theta_r\le1/4\).

Both members are restrictions of the same normalized exact Moser family.
Thus the chart transition, inverse transition, primitive-gauge coboundary,
oriented-blow-up transition, and transported-slide transition are exact
identities.  The checker records all twelve entries of the full
state-order \(0,\ldots,3\) by parameter-order \(0,\ldots,2\) rectangle.

The comparison between the transported physical source phase and the direct
positive-Kato source phase is not assumed to be a constant phase shift.  It
is a general orientation-preserving circle diffeomorphism \(\kappa_\mu\).
The exact section form, the authenticated endpoint bound, the true-graph
bound, and the positive Kato orientation give

\[
 \partial_\psi\kappa_\mu>2^{-9441},
 \qquad \deg\kappa_\mu=+1.
\]

The checker verifies the nine admissible colored derivative slots with
phase order at most three, parameter order at most two, and mixed total order
at most three.  It deliberately makes no full rectangular regularity claim
for this boundary-only seam.  The corresponding forward and inverse exponent
budgets are

\[
 (k_1,k_2,k_3)=(46518441,93036891,279110683),
\]

\[
 (\ell_1,\ell_2,\ell_3)
 =(279120125,837360385,2791201291).
\]

## Frozen bindings

| Source | SHA-256 |
|---|---|
| Finite-overlap proof | `4afe3faa733eb20bac87978bbaaa8bd746248fd90e52d195c9d1ee4cc551d918` |
| Finite-overlap configuration | `698f5979f021e3702fd733169d71178fd06fd103647dff1a2bf87456edad407a` |
| Global Moser proof | `069d109a22fa502c2e6970de7e3ef4c60234e327138b9052df764b6f36cf8245` |
| Physical-slide proof | `7fa2fc45827f7c8b41a0dabb3a2bd872f66088e61d3c26ed55d8c78bc80e187b` |
| P2b mixed-jet certificate | `07b0949a3d403c0c0a85a4a157b86d7b32cce3ff0348aeffa1db474d441fca07` |
| P2bK Kato certificate | `c67cce575caa396eba5b4388e8ba9a0c9d73fd702f69911d64c878f57f27bff3` |

## Reproduction

```bash
python3 -B validation/rigorous/check_p2d_chart_overlaps.py
python3 -B -m unittest \
  validation.rigorous.tests.test_p2d_chart_overlaps -v
```

The checker returns `PASS` with exit code zero; the nine focused tests pass.
Changing the proof, configuration, or a frozen prerequisite fails closed.
This result completes only the local P2d chart package.  It does not complete
P2e, the later positive-end validation, independent replay, temporal
stability, Turing selection, or canard identification.
