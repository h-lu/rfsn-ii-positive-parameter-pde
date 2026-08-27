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

## Local staged progress (2026-08-27)

- [x] Freeze `vdp-positive-box-v1` and the gap-free `r=0` comparison bridge
- [x] P1 exact identities and explicit V2(1) interval inequalities
- [x] P2a moving frame, local block, difference cone, and true coarse graphs
- [x] P2b0 exact H10 regeneration and true-graph C0/C1 tubes
- [ ] P2b1 true-graph state derivatives through order three
- [ ] P2b2 parameter derivatives through order two and required mixed jets
- [ ] P2b3 weighted half-orbit constants
- [ ] P2c--P2e homoclinic, exact charts, and complete central event atlas
- [ ] P3--P5 positive pole, outer channel, matching/finite parts, and V6 census
- [ ] Independent replay on a genuinely distinct machine (currently 1/2)

The clean P2b0 certificate has local integrity and mathematical `PASS`, but
its aggregate status is `INCONCLUSIVE` and `claim_bearing=false` while the
last item and the later scoped obligations remain open.  A bound on the
degree-ten polynomial center is not a bound on the missing higher derivatives
of the true graph.

## Outcome

Record `PASS`, `FAIL`, or `INCONCLUSIVE`.  This issue is deliberately deferred
until the analytic theorem contract is stable; computation must not choose the
theorem after seeing the output.
