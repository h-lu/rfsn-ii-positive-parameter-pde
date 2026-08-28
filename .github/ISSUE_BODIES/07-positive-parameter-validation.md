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

## Local staged progress (2026-08-29)

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
- [x] P2d `V2.CHART.ANALYTIC_NORMAL_FORM` local mathematical pass: all-orders
      second-jet majorant, explicit domains and two-sided maps, exact primitive,
      joint state--parameter \(C^2\) tails, and 38 authenticated source-bound
      checks
- [x] P2d `V2.CHART.ZERO_ENERGY` local mathematical pass: one uniform analytic
      nonlinear zero-energy fiber with strict rational Krawczyk inclusion
- [x] P2d `V2.CHART.EXACT_SECTIONS` local mathematical pass: frozen nonlinear
      radial sections, exact gauges, and signed action preservation
- [x] P2d `V2.CHART.WEIGHTED_PASSAGE` local mathematical pass: signed
      logarithmic time/phase laws, absolute Kato deck, all-finite-order
      generator, clock inversion, and local radial winding/time comparison
- [x] P2d `V2.CHART.PHYSICAL_SLIDES` local mathematical pass: inherited
      radius-1/100 faces, event-free unique first-hit slides, complete
      state-C3/parameter-C2 bounds, and (D12) with `C_phys=7`
- [x] P2d `V2.CHART.OVERLAPS` local mathematical pass: a two-member finite
      cover with common domains, identity exact-symplectic overlap cocycle and
      gauges, signed-axis and blow-up compatibility, bounded marking changes,
      and phase-boundary degree `+1`; all seven children give the local parent
      `V2.EXACT_CHART` mathematical pass
- [ ] P2e event atlas
- [ ] P3--P5 positive pole, outer channel, matching/finite parts, and V6 census
- [ ] Independent replay on a genuinely distinct machine (currently 1/2)

P2c, all seven P2d children, and the local parent `V2.EXACT_CHART` now have
scoped local mathematical `PASS`.  The P2d chain is documented in the
[`frame`](https://github.com/h-lu/rfsn-ii-positive-parameter-pde/blob/main/validation/rigorous/P2D_FRAME_REPORT.md),
[`normal-form`](https://github.com/h-lu/rfsn-ii-positive-parameter-pde/blob/main/validation/rigorous/P2D_NORMAL_FORM_REPORT.md),
[`zero-energy`](https://github.com/h-lu/rfsn-ii-positive-parameter-pde/blob/main/validation/rigorous/P2D_ZERO_ENERGY_REPORT.md),
[`exact-sections`](https://github.com/h-lu/rfsn-ii-positive-parameter-pde/blob/main/validation/rigorous/P2D_EXACT_SECTIONS_REPORT.md),
[`weighted-passage`](https://github.com/h-lu/rfsn-ii-positive-parameter-pde/blob/main/validation/rigorous/P2D_WEIGHTED_PASSAGE_REPORT.md),
[`physical-slide`](https://github.com/h-lu/rfsn-ii-positive-parameter-pde/blob/main/validation/rigorous/P2D_PHYSICAL_SLIDES_REPORT.md),
and [`chart-overlap`](https://github.com/h-lu/rfsn-ii-positive-parameter-pde/blob/main/validation/rigorous/P2D_CHART_OVERLAPS_REPORT.md)
reports.  Every aggregate remains `INCONCLUSIVE`, `claim_bearing=false`, and
`release_eligible=false`; independent replay remains 1/2.  The bounded
incoming/outgoing slides now close the physical comparison with `C_phys=7`.
The next active gate is the P2e event atlas.  This work makes no claim of
temporal stability, Turing selection, or canard identification.

## Outcome

P2c, all seven P2d child atoms, and the local parent `V2.EXACT_CHART` are
locally `PASS`; their aggregate status remains `INCONCLUSIVE` under the
provenance and independent-replay policy.  The active mathematical path is
P2e `V2.EVENT_ATLAS`, followed by P3--P5.  Every new scope must freeze its theorem
objects before its claim-bearing run; computation must not choose the theorem
after seeing the output.
