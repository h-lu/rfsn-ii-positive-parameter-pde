# Proof-seam audit: 2026-08-27

This record separates the logical proof audit from the floating-point
numerical atlas.  It does not change a claim status by itself.  The
authoritative statuses remain in [`CLAIM_REGISTER.md`](../CLAIM_REGISTER.md).

## V2 to V3

The connection is logically closed in the present text.  V2 stops at a finite
gate and says so explicitly.  V3 separately straightens that moving gate to
the exact section \(x=10\), proves entry into a positive invariant cone, and
derives the positive-parameter pole compactification and finite part from the
full equations.

The remaining limitation is quantitative rather than logical: the final
radius, event margins, cone-entry constants, and finite-part remainder bounds
are existential.  Consequently, a floating-point run at a selected value of
\(r\) does not yet certify that this value lies in the theorem box.

## V4 to V5 and V5A

The audit found three interfaces.  They are now closed in the supported
finite-atlas formulation.

1. The resolved \(K_1\) construction invoked a relative overflowing NHIM
   result for an auxiliary center graph.  The precise relative theorem,
   classical boundaryless input, parameter proof, and \(K_1\) hypothesis map
   are now in
   [RELATIVE_OVERFLOWING_NHIM.md](../theory/RELATIVE_OVERFLOWING_NHIM.md)
   and are applied clause by clause in V5.
2. Decreasing the upper radius and then redefining
   \([r_{\rm p}/2,r_{\rm p}]\) does not produce a subset of the preceding
   annulus.  V5 now collects its small-\(r\) thresholds on the closed
   comparison wedge, freezes one final radius, and reruns V3--V4 on that
   annulus; it no longer uses the false inclusion.
3. The V5 arrival labels at the V5A cut had to lie in the interval on which
   the terminal finite parts are defined.  V5A now uses the exact transition
   \(\beta=\delta B=r^2B\), a uniform scaled \(B\)-collar, the ratio
   \(\delta_+/\delta_-=4\), and a subordinate-patch choice to obtain the
   explicit interior margin in (7c).

No sign, clock, energy, action, or Jost-pairing contradiction was found.

## V5 to V6

V2 constructs exact saddle charts on a finite parameter cover, whereas the
former opening of V6 wrote a single global \((\phi,\nu)\) chart and fixed raw
winding labels.  The frozen abstract source expressly provides descent from a
finite compatible marked atlas and expressly does not require a global angle
lift or winding function.  The implemented repair is:

- state the return strips, cross forms, and raw labels chartwise on a finite
  cover;
- prove H1--H2, terminal regularity, the local first-event relation, cross
  forms, and coding separately in every chart before invoking descent;
- take common thresholds and estimates over that finite cover; and
- descend the physical first-event relation, trapped dynamics, periods, and
  closed actions using the imported overlap covariance.

The proof and application map are in
[FINITE_MARKED_ATLAS_DESCENT.md](../theory/FINITE_MARKED_ATLAS_DESCENT.md),
and V6--V7 now use exactly that formulation.  A single global marked chart is
a stronger optional claim T2G.  It remains Proposed and is not needed for V6
or V7.

The descent proposition is therefore a pure covariance statement: it assumes
the local marked return/coding presentations already exist and does not call
V6 to construct them.  Conversely, V6 Section 4 completes the local
construction before calling the proposition.  V2 now also records the full
state-\(C^3\), parameter-\(C^2\) oriented-blow-up transition required by the
admissible-marking theorem.  A second threshold choice places every local V7
branch retained in the final alphabets inside the common physical
residence-time domain, while allowing bounded recoding on overlaps.

The H2 construction should retain its explicit finite census of every event,
boundary, empty incidence, first-hit margin, and corner priority.  The present
text contains the needed construction; its role is to verify exhaustiveness,
not merely local transversality.

## Consequence for computation

The numerical repository is not a proof substitute and is not a toy.  Its
research role is to turn the existential objects above into explicit
candidates and, later, replayable interval certificates.  The immediate
targets are the actual V3 source-window connection, the V4 future-staying
graph, the V5 matching tube and arrival label, the complete sampled V6
branches, and an explicit positive parameter box.  Temporal stability,
Turing-branch selection, and canard identification remain separate claims.
