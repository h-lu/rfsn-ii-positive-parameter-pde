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
- [x] Full strict P2c design run, including `V2.HOM.MIDDLE_C2` and global
      composition with \(T_*=11\), \(\eta=1/5\), and
      \(C_{\rm hom}=71496600\)
- [x] Retrospective local P2c summary certificate/checker (non-claim-bearing)
- [x] P2d exact-interface scout: 59 symbolic checks for the positive-Kato
      reversible symplectic completion, action dictionary, radial section
      forms/gauges, and linear logarithmic time/phase slopes
- [x] P2d formal local `V2.CHART.SYMPLECTIC_FRAME` certificate: archived P2bK
      prerequisite, 59 exact checks, and all 20 strict frame/parameter-\(C^2\)
      gates on the exact-rational \(16\times8\times4\) bridge cover
- [x] P2d exact \(q=1,2\) normal-form audit: 26 symbolic checks, including
      \(Z_4=((I_2^{\rm K})^2-I_1^2)/120\) at \(r=0\) and the conditional
      formal coefficient \(c_2=0\) for an ansatz
      \(I_1=-\nu+c_2\nu^2+\cdots\); no formal branch is constructed
- [x] P2d Proposed global-Moser design evaluation: authenticated frame input,
      candidate \(E,h_{\rm in},\kappa_J\) gates, fixed nested domains, and
      forward Lipschitz-amplified tail gates all pass; non-claim-bearing and
      no atom closed
- [ ] Remaining six P2d chart atoms and the P2e event atlas
- [ ] P3--P5 positive pole, outer channel, matching/finite parts, and V6 census
- [ ] Independent replay on a genuinely distinct machine (currently 1/2)

The clean certificates through P2c, together with the P2d frame-child
certificate, have local integrity and mathematical `PASS`, but their aggregate
status is `INCONCLUSIVE` and
`claim_bearing=false` while independent replay remains open.  Separately, the
later scoped obligations remain open.  The full strict P2c run passes the
16,384-cell selected-branch cover, all 44,416 internal common faces, first
hit, transversality, actual-root parameter two-jets, both infinite tails, and
the fixed-\(\xi\) continuous \(C^2\) compact middle.  Their global composition
has \(T_*=11\), \(\eta=1/5\), and \(C_{\rm hom}=71496600\).  No large-box
exclusion outside the validated parameter-following lifted tube is required.
The local P2c summary certificate/checker parses the archived strict logs and
replays the exact tail composition, so all five P2c atoms and their local
parent now pass.  Its aggregate remains `INCONCLUSIVE` and non-claim-bearing;
P2d--P5 and independent replay remain pending.  The certificate was generated
from clean source commit `15664b600316d97ddef8487a279367495f4f1ed9`; its
SHA-256 is
`38709fac54569f190f3663df95baedbdb6e0c646d3ec372385a1373dfaf34d34`.
See
[`P2C_CERTIFICATE_REPORT.md`](https://github.com/h-lu/rfsn-ii-positive-parameter-pde/blob/main/validation/rigorous/P2C_CERTIFICATE_REPORT.md).
This work makes no claim of temporal stability, Turing selection, or canard
identification.

P2d now has one formally archived local child certificate.  The archived P2bK
mathematical pass, all 59 deterministic exact checks, and the separately
implemented strict interval frame run together give local mathematical `PASS`
for `V2.CHART.SYMPLECTIC_FRAME`.  The clean-source certificate
[`vdp_bridge_v1_p2d_symplectic_frame.json`](https://github.com/h-lu/rfsn-ii-positive-parameter-pde/blob/main/validation/rigorous/results/vdp_bridge_v1_p2d_symplectic_frame.json)
has integrity and mathematical status `PASS`; its source revision and byte
bindings are recorded inside it.  Its final status remains `INCONCLUSIVE`,
`claim_bearing=false`, and `release_eligible=false`, with independent replay at
1 of 2 distinct machines.  See
[`P2D_FRAME_REPORT.md`](https://github.com/h-lu/rfsn-ii-positive-parameter-pde/blob/main/validation/rigorous/P2D_FRAME_REPORT.md).

The exact finite-prefix audit now passes 26 checks, and the design-only global
Moser scout passes the candidate input and domain inequalities recorded in
[`P2D_NORMAL_FORM_DESIGN_REPORT.md`](https://github.com/h-lu/rfsn-ii-positive-parameter-pde/blob/main/validation/rigorous/P2D_NORMAL_FORM_DESIGN_REPORT.md).
Neither artifact is a certificate or closes an obligation.  In particular,
the all-orders parameter-\(C^2\) convergence and tail estimates remain open.

The other six `V2.CHART.*` atoms and `V2.EXACT_CHART` remain `OPEN`.  The
current result proves no nonlinear Moser chart, nonlinear zero-energy branch,
exact nonlinear sections, weighted passage constants, physical slides, or
overlap atlas.  It does fix the Kato action and phase conventions: the full
four-dimensional frozen-to-Kato conjugation preserves the action value and
its sign, while direct Kato-section quadrature gives the negative logarithmic
phase coefficient.  The next active gate is the constructive analytic normal
form on an explicit complex domain.

## Outcome

P2c and the P2d symplectic-frame child atom are locally `PASS`; their aggregate
status remains `INCONCLUSIVE` under the provenance and independent-replay
policy.  The exact \(q=1,2\) prefix and the Proposed normal-form design gates
are complete, but they do not change any claim status.  The active mathematical
path is the six remaining children of P2d
`V2.EXACT_CHART`, beginning with `V2.CHART.ANALYTIC_NORMAL_FORM`, then P2e
`V2.EVENT_ATLAS`, followed by P3--P5.  Every new scope must freeze its theorem
objects before its claim-bearing run; computation must not choose the theorem
after seeing the output.
