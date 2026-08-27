# Issue #7 P2c selected-homoclinic certificate report

The retrospective local P2c certificate was assembled on 2026-08-28 from
clean source commit `15664b600316d97ddef8487a279367495f4f1ed9`.  Its
machine-readable result is
[`results/vdp_bridge_v1_p2c_homoclinic.json`](results/vdp_bridge_v1_p2c_homoclinic.json),
with SHA-256
`38709fac54569f190f3663df95baedbdb6e0c646d3ec372385a1373dfaf34d34`.

## Verdict

| Layer | Status | Meaning |
|---|---|---|
| Frozen source and evidence bindings | `PASS` | The certificate materializes its clean Git source snapshot and verifies every declared file and historical strict-run source/log digest. |
| Historical P2a, P2b, and P2bK prerequisites | `PASS` | Each prerequisite is schema-valid and hash-bound at its own recorded source commit; the P2bK local-graph/source interface is byte-identical to the P2c snapshot. |
| `V2.HOM.BRANCH` | `PASS` | All 16,384 cells and all 44,416 internal parameter faces pass, with the frozen core anchor and uniqueness in the declared lifted multiple-shooting tube. |
| `V2.HOM.FIRST_HIT` | `PASS` | All 16,384 cells and 306,287 continuous steps pass the source-to-first-symmetry-hit gates. |
| `V2.HOM.TRANSVERSE` | `PASS` | The selected endpoint and shooting/event determinants have strict margins. |
| `V2.HOM.TAILS` | `PASS` | The exact-Fraction replay closes both infinite tails and the local pre-source pieces with (T_*=11) and (eta=1/5). |
| `V2.HOM.MIDDLE_C2` | `PASS` | All 16,384 cells, 262,144 continuous steps, and 163,840 initial-section enclosures close the compact middle and its seams. |
| Local `V2.HOMOCLINIC` parent | `PASS` | The selected (C^2) symmetric homoclinic family, first hit, transversality, lifted-tube uniqueness, and full-line weighted parameter-two-jet bound are explicit. |
| Independent replay | `PENDING_REQUIRED` | One of two policy-required distinct machines has been observed. |
| Aggregate certificate | `INCONCLUSIVE` | The local result is deliberately non-claim-bearing until independent replay. |

Thus `integrity_status=PASS`, `mathematical_status=PASS`,
`final_status=INCONCLUSIVE`, `claim_bearing=false`, and
`release_eligible=false`.  Here `INCONCLUSIVE` records the repository's
release policy; it does not mean that one of the implemented P2c gates crossed
zero.

## Explicit parameter box and global bound

The gap-free comparison bridge is

\[
 r\in[0,2/25],\qquad a_2\in[-1/4,1/4],\qquad
 \epsilon\in[4/5,6/5].
\]

The strict runs use a (32\times128\times4) rational cover.  The complete
weighted profile estimate has

\[
 T_*=11,\qquad \eta=1/5,\qquad
 C_{\mathrm{hom}}^{(\theta)}=114395,\qquad
 C_{\mathrm{hom}}^{(\mu)}=71496600,
\]

where the last integer controls the profile and all original-parameter
derivatives through order two.  Its underlying order-two fraction is

\[
 \frac{78611342260591861875}{1099511627776}
 <71496600.
\]

The full-line coverage is derived rather than accepted from a summary flag.
Every compact-middle slab reaches its source seam and the symmetry seam and
stays strictly inside \(|\xi|<11\).  The checker verifies the exact positive
tail/source margin

\[
 11-1-\sup T_h
 =\frac{10468707664995}{35184372088832}>0.
\]

It then joins

\[
 \xi\le-11,\qquad -11\le\xi\le-T_h,\qquad
 -T_h\le\xi\le0,
\]

and obtains the positive half-line from the fixed parameter-independent
Euclidean-isometric reverser.

## Evidence and trust boundary

The certificate parses four archived fixed-order summary logs.  It does not
compile or rerun the 16,384-cell CAPD grids.  The strict executable bytes,
compiler flags, and linked-library archive bytes are not archived here;
therefore the certificate uses the narrow obligation
`ENV.P2C_HISTORICAL_RUN_RECORDS`, not the stronger `ENV.CAPD_BINDING`.
Recorded executable and CAPD hashes remain provenance records only.

The inexpensive exact-Fraction tail composition is materialized from the
frozen source commit and replayed byte-for-byte.  Both the dedicated checker
and the repository-wide checker reconstruct the complete certificate from its
source snapshot and reject changes to evidence, counts, margins, constants,
or claim boundaries.

This is a local strict summary certificate, not an independent-machine replay.
The read-only flagship theory repository remains fixed at
`d54add098545063d5efe8f1d6f062d4cfc116a0d` and was not modified.

## Relation to the paper and next step

This closes the implemented numerical interface for Theorem V2(2) and the
global weighted homoclinic bounds in V2(9)--(11), within the explicitly stated
finite parameter-following lifted tube.  It does not prove uniqueness outside
that tube, temporal stability, dynamic Turing selection, or finite-parameter
canard identification.

The next theorem object is P2d `V2.EXACT_CHART`: a positive radial reversible
symplectic completion, finite exact saddle charts, zero-energy fiber solve,
overlap compatibility, and weighted logarithmic passage bounds.  P2e
`V2.EVENT_ATLAS` follows because its event cells and transport templates use
those exact chart coordinates.
