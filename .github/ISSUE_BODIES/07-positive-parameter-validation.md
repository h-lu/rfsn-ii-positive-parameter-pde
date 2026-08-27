## Objective

After the analytic hypotheses are frozen, rigorously verify one nonempty
positive-parameter box for each claim-bearing model theorem that requires
quantitative margins.

## Prerequisites

- [ ] The relevant analytic result, [#1](https://github.com/h-lu/rfsn-ii-positive-parameter-pde/issues/1)
      or [#6](https://github.com/h-lu/rfsn-ii-positive-parameter-pde/issues/6),
      has fixed hypotheses and conclusion.
- [ ] The analytic proposition and every observable have fixed definitions.
- [ ] The parameter box was selected before the first claim-bearing run.
- [ ] The required signs, inclusions, transversality constants, and first-hit
      margins are enumerated.

## Validation obligations

- [ ] Outward-rounded interval implementation
- [ ] Source-only rebuild from a clean commit
- [ ] Complete dependency and rounding-mode manifest
- [ ] Machine-readable certificates and top-level report
- [ ] Hash binding among source, report, manuscript, and certificates
- [ ] Independent-machine replay before publication

## Local staged progress (2026-08-28)

- [x] Freeze `vdp-positive-box-v1` and the gap-free `r=0` comparison bridge
- [x] P1 exact identities and explicit V2(1) interval inequalities
- [x] P2a moving frame, local block, difference cone, and true coarse graphs
- [x] P2b0 exact H10 regeneration and true-graph C0/C1 tubes
- [x] P2b1 true-graph state derivatives through order three
- [x] P2b2 parameter derivatives through order two and required mixed jets
- [x] P2b3 weighted half-orbit constants
- [x] P2bK normalized Riesz/Kato source phase and source-jet triangle
- [ ] P2c--P2e homoclinic, exact charts, and complete central event atlas
- [ ] P3--P5 positive pole, outer channel, matching/finite parts, and V6 census
- [ ] Independent replay on a genuinely distinct machine (currently 1/2)

The clean certificates through P2bK have local integrity and mathematical
`PASS`, but their aggregate status is `INCONCLUSIVE` and
`claim_bearing=false` while independent replay and the later scoped
obligations remain open.  The P2c design scout already passes a full
16,384-cell selected-branch cover and all 44,416 internal common faces, but
the P2c checkbox remains open until large-box exclusion, first hit, parameter
jets, tails, and a formal archived certificate are complete.

## Outcome

Record `PASS`, `FAIL`, or `INCONCLUSIVE`.  This issue is deliberately deferred
until the analytic theorem contract is stable; computation must not choose the
theorem after seeing the output.
