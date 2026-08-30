# P2e terminal-centered flowbox scout

**Status:** `COMPUTED/E1_NON_EVIDENTIARY`; no P2e atom passes.

At the representative v2 point

\[
 (r,a_2,\epsilon)=(3/200,0,1),
\]

the finite algebraic gate \(e=(-U)^{-1}=23/400\), the pole gate
\(-U=10\), and the selected homoclinic return all have usable local
center germs.  The calculation corrects one design error in the first P2e
draft: the relatively wide phase collars used to separate the three channels
cannot simultaneously be used as the transverse radii of the full physical
flowboxes.

For the algebraic and pole center germs, the numerical source section was
varied in transported Kato phase and signed action, flowed to the fixed
terminal section, and differentiated by centered differences in the terminal
coordinates \((V,Q)\).  Both \(2\times2\) terminal maps have nonzero sampled
determinant.  This supports defining each carrier from a small terminal disc
and its backward first-hit map to the outgoing band.  It is not an interval
inverse-function proof.

The homoclinic channel is much narrower.  At source-phase offsets
\(\pm10^{-7}\), the two sampled incoming hits have unstable radius below
\(4.8\times10^{-3}\), leaving more than \(5.2\times10^{-3}\) inside the
radius-\(10^{-2}\) incoming face.  Earlier probes showed that offsets
\(5\times10^{-7}\) already leave that face.  Thus \(10^{-7}\) is the largest
radius explicitly probed at both endpoints in the committed scout, not a
certified admissible radius.  The structural freeze applies one further
factor of ten and uses entrance phase radii

\[
 R_{\rm a}^{\rm ent}=10^{-7},\qquad
 R_{\rm h}^{\rm ent}=10^{-8},\qquad
 R_{\rm p}^{\rm ent}=10^{-5}.
\]

The wider radii \(10^{-6},10^{-7},10^{-4}\) stored in the scout JSON are
therefore probe scales only.  The radius-\(10^{-2}\) homoclinic phase collar
remains a protected separation neighborhood, not a flowbox entrance disc.

The finite V2 algebraic gate anchor and the later positive outer matched
candidate are deliberately kept distinct.  At this point their sampled
source-phase displacement is about \(7.58\times10^{-5}\), so the latter lies
well inside the protected radius-\(10^{-2}\) collar.  This is only an
interface diagnostic; it neither identifies the two objects nor validates
V4/V5.

The next mathematical step is now narrow: freeze the terminal-disc charts
and backward entrance maps with these separated scales, then validate their
flow domains, embeddings, terminal speeds, and containment on the full v2
parameter cover.  The artificial side/corner census can then be derived in
the normalized flowbox coordinates rather than sampled as a large raw sign
table.

Reproduce with

```bash
python3 -m numerics.vdp_p2e_terminal_flowbox_scout
python3 -m unittest numerics.test_vdp_p2e_terminal_flowbox_scout -v
```
