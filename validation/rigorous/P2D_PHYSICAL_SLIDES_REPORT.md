# P2d physical-slide validation report

Date: 2026-08-29

## Outcome

The proof-bound checker gives local mathematical `PASS` for
`V2.CHART.PHYSICAL_SLIDES` on the frozen target box

\[
 B_+=[1/25,2/25]\times[-1/4,1/4]\times[4/5,6/5].
\]

The gap-free certificates also cover the comparison bridge from the complete
\(r=0\) anchor face.  The result joins the exact auxiliary Kato sections to
the inherited radius-\(1/100\) physical saddle faces for
\(|\nu|\le25/2^{58}\).

| Item | Status |
|---|---|
| Source and exact-rational gates | `PASS` |
| `V2.CHART.PHYSICAL_SLIDES` | local mathematical `PASS` |
| Physical winding/residence comparison (D12) | `PASS`, \(C_{\rm phys}=7\) |
| `V2.CHART.OVERLAPS` | `OPEN` |
| Parent `V2.EXACT_CHART` | `OPEN` |
| Complete event atlas `V2.EVENT_ATLAS` (P2e) | `OPEN` |
| Repository aggregate | `INCONCLUSIVE`, `claim_bearing=false`, replay `1/2` |

## Certified bounds

- The auxiliary face lies strictly in the P2a forward cone.  The outgoing
  expanding radius lies between
  \(72565815/1484261240602624\) and
  \(673942425/11874089924820992\), while the stable radius is smaller than
  one thirty-second of the lower expanding radius.
- The chart-exit expanding radius exceeds every auxiliary-face radius by
  \(2063589/1079462720438272>0\); this supplies the no-recross margin.
- Each physical slide has a unique first hit in time strictly below \(19\).
  The normalized face function has hit speed strictly above \(4/3\).
- The incoming and outgoing slide times sum to less than \(38\).  Combining
  this with the weighted Kato comparison gives
  \(27/4<7\), hence (D12) with \(C_{\rm phys}=7\).
- The complete rectangle
  \(0\le i\le3\), \(0\le j\le2\) is bounded for both hit times and physical
  endpoints.  The typed source-DAG budget is \(2762<4096\); the terminal
  physical-frame overhead is explicit.  Uniform original-parameter bounds
  are \(2^{9180037}\) for hit-time jets and \(2^{46518425}\) for endpoint
  jets.  These deliberately coarse constants certify finiteness only.

The local event-support configuration has empty non-saddle event-germ
restriction on the closed saddle block.  This proves only the event exclusion
needed by this slide atom; it does not certify exterior extensions, incidences,
or the connected event-cell census assigned to P2e.

## Frozen bindings

| Source | SHA-256 |
|---|---|
| Physical-slide proof | `7fa2fc45827f7c8b41a0dabb3a2bd872f66088e61d3c26ed55d8c78bc80e187b` |
| Physical-slide configuration | `fa7daa1273b508951e081378d938342f985271722bf4871669a30f4ab44a8f16` |
| P2a local graph | `192b351c3f153080d82bc856fa3c667388dc16c7b4cf0cfa8568fa347bcaf6be` |
| P2b mixed jets | `07b0949a3d403c0c0a85a4a157b86d7b32cce3ff0348aeffa1db474d441fca07` |
| P2bK Kato source | `c67cce575caa396eba5b4388e8ba9a0c9d73fd702f69911d64c878f57f27bff3` |
| P2d symplectic frame | `5fabbcf01dc9b2f818f34525010332c76ff40190ea9a3d5ab166072397397847` |
| Global Moser proof | `069d109a22fa502c2e6970de7e3ef4c60234e327138b9052df764b6f36cf8245` |
| P2c source configuration | `a1aca97d2fcf76f336dc06734c1ced25aeb9bd6b1bfa69b9dc8a6545846ce9ac` |
| Weighted-passage proof | `78023f2c1511b2037b07ad9fa6a70504abb8734ee9f73103a00634c91f315f1c` |

## Reproduction

```bash
python3 -B validation/rigorous/check_p2d_physical_slides.py
python3 -B -m unittest validation.rigorous.tests.test_p2d_physical_slides -v
```

The checker must return `PASS` with exit code zero.  Mutating the proof,
configuration, or any frozen prerequisite fails closed.  No conclusion about
temporal stability, Turing selection, or canard identification is made here.
