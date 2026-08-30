# Theory provenance and local-amendment policy

This directory records how the mathematical results developed in this
repository relate to the independent flagship repository
[`h-lu/reversible-rfsn-ii-waves`](https://github.com/h-lu/reversible-rfsn-ii-waves).
It is a provenance layer, not a second claim register and not a copy of the
flagship manuscript.

## Independence rule

The flagship repository is a **read-only external dependency** for this
project.  Its frozen comparison revision is identified in
[BASELINE.md](BASELINE.md).  Work in this repository must not edit, rewrite,
commit to, or silently reinterpret that revision.  A local proof, derivation,
computation, correction, or clarification is a result of this repository only;
it does not change a flagship theorem, proof, abstract, or evidence status.

The dependency is citation-based and revision-pinned.  It is not a live
submodule, sibling-worktree dependency, or permission to take unpublished
changes from the flagship working tree.  If a result developed here is ever
ported upstream, that must be a separate, explicitly authorized change with a
new source revision and a fresh dependency audit.

## Two independent classifications

Every registered item has two labels which must not be conflated.

1. **Provenance relation** says where the content belongs:
   `FROZEN-BASELINE-INPUT`, `LOCAL-AMENDMENT`, or
   `EXTERNAL-MODEL-SOURCE`.
2. **Evidence status** uses the repository vocabulary: `Proposed`, `Derived`,
   `Numerically observed`, `Computer-assisted`, `Proved`, `Imported`, or the
   planning status `Deferred` used by the claim register.

For example, `LOCAL-AMENDMENT / Proved` means that this repository contains a
proof of a companion result.  It does **not** mean that the flagship baseline
has been amended, that the result appeared at the frozen flagship commit, or
that the upstream authors have adopted it.  Likewise, a numerical observation
cannot upgrade an analytic claim to `Proved`.

## Authority order

When records differ, use the following order.

1. [`AGENTS.md`](../AGENTS.md) controls repository independence and working
   practice.
2. [`CLAIM_REGISTER.md`](../CLAIM_REGISTER.md) is authoritative for the
   mathematical status of claim IDs.
3. [`RESEARCH_CONTRACT.md`](../RESEARCH_CONTRACT.md) fixes scope, completion
   conditions, fallbacks, and nonclaims.
4. The model-specific import notes fix the exact external statements,
   hypotheses, revisions, hashes, and evidence boundaries actually used.
5. [BASELINE.md](BASELINE.md) and
   [AMENDMENT_REGISTER.md](AMENDMENT_REGISTER.md) summarize provenance and
   dependencies; they cannot enlarge a theorem or override the files above.

## Files in this directory

- [BASELINE.md](BASELINE.md) identifies the immutable flagship comparison
  revision, its role, the allowed imports, and the excluded conclusions.
- [FLAGSHIP_IMPORT_AUDIT_2026-08-28.md](FLAGSHIP_IMPORT_AUDIT_2026-08-28.md)
  maps every imported clause to the frozen long draft and compressed focused
  paper, records the evidence-access boundary, and identifies the two local
  theorem interfaces required before the van der Pol manuscript.
- [AMENDMENT_REGISTER.md](AMENDMENT_REGISTER.md) records local companion
  results and numerical work, their evidence status, and their complete
  dependency chain.
- [EXPLICIT_GLOBAL_MOSER_MAJORANT.md](EXPLICIT_GLOBAL_MOSER_MAJORANT.md)
  proves the van-der-Pol-specific global Moser majorant, including the exact
  \(q=1,2\) Lie prefix, the all-orders parameter-two-jet recurrence, explicit
  map/inverse domains and tails, and the fixed primitive gauge.  Combined
  with the bound source checker, it gives
  `V2.CHART.ANALYTIC_NORMAL_FORM` a local mathematical `PASS` and supplies the
  common normalized family used by the later P2d results.  The repository
  aggregate remains non-claim-bearing.
- [EXPLICIT_ZERO_ENERGY_FIBER.md](EXPLICIT_ZERO_ENERGY_FIBER.md) transfers
  the resonant state majorant to the action variables, proves a strict common
  Krawczyk enclosure for the nonlinear zero-energy fiber, and supplies the
  mixed parameter-two-jet and all-finite-\(\nu\)-order Cauchy bounds.  Together
  with its exact-rational checker, it gives `V2.CHART.ZERO_ENERGY` a local
  mathematical `PASS` and supplies the nonlinear fiber used downstream.
- [EXPLICIT_EXACT_RADIAL_SECTIONS.md](EXPLICIT_EXACT_RADIAL_SECTIONS.md)
  combines that nonlinear fiber with the authenticated arbitrary-\(q\)
  radial-section identities, freezes a strict source-domain radius, fixes the
  incoming/outgoing primitive gauges, and proves exact preservation of the
  same signed Kato action.  Its exact-rational checker gives
  `V2.CHART.EXACT_SECTIONS` a local mathematical `PASS` and supplies the
  input to the weighted-passage result below.
- [EXPLICIT_WEIGHTED_KATO_PASSAGE.md](EXPLICIT_WEIGHTED_KATO_PASSAGE.md)
  proves the signed Kato time/phase laws on an explicit punctured action
  collar, freezes the absolute lifted-argument deck, supplies parameter-two-jet
  and all-finite-log-order bounds, and inverts the positive clock.  Its
  proof-bound exact-rational checker gives `V2.CHART.WEIGHTED_PASSAGE` a local
  mathematical `PASS`; its physical comparison is completed by the next item.
- [EXPLICIT_PHYSICAL_SLIDES.md](EXPLICIT_PHYSICAL_SLIDES.md) joins the exact
  auxiliary Kato sections to the inherited radius-\(1/100\) physical faces,
  proves event-free unique first hits with slide times below \(19\), supplies
  the complete state-\(C^3\)/parameter-\(C^2\) rectangle, and closes (D12) with
  \(C_{\rm phys}=7\).  Its proof-bound checker gives
  `V2.CHART.PHYSICAL_SLIDES` a local mathematical `PASS` and supplies the
  physical markings used in the overlap result below.
- [EXPLICIT_FINITE_CHART_OVERLAPS.md](EXPLICIT_FINITE_CHART_OVERLAPS.md)
  constructs a two-member finite parameter cover with common chart and inverse
  domains, proves that its nonlinear exact-chart cocycle and primitive-gauge
  differences are identities, and compares the transported and direct physical
  source markings with degree \(+1\) and mixed derivative bounds through total
  order three (parameter order at most two).  Its
  proof-bound checker
  [`check_p2d_chart_overlaps.py`](../validation/rigorous/check_p2d_chart_overlaps.py)
  gives `V2.CHART.OVERLAPS` a local mathematical `PASS`.  All seven P2d chart
  children therefore give the local parent `V2.EXACT_CHART` a mathematical
  `PASS`.  The aggregate remains `INCONCLUSIVE` and non-claim-bearing because
  P2e and later obligations remain open and independent replay is 1/2.
- [P2E_AXIS_SOURCE_CHART.md](P2E_AXIS_SOURCE_CHART.md) gives a direct
  zero-energy radial chart containing the complete true \(\nu=0\) source
  curve on the v2 proper phase arc.  It also proves the compactness criterion
  that thickens any complete strict zero-action event skeleton to some
  uniform action subcollar.  Its proof-bound checker gives these two local
  lemmas mathematical `PASS`; exterior first hits, incidence, census,
  \(m_{\rm ax}\), and `V2.EVENT_ATLAS` remain open.
- [COMPACT_FAMILY_FIRST_HIT_THEOREM.md](COMPACT_FAMILY_FIRST_HIT_THEOREM.md)
  proves compact-family persistence and transfer of the already supplied
  passage, selector, cross forms, and physical event arrangement.  It is
  conditional on the frozen fixed-system endpoint/matching maps and finite
  physical rows.  It transports every imported competing event-time
  difference on a finite marked cover; it neither produces a new global
  block nor asserts a global winding label.
- [RELATIVE_OVERFLOWING_NHIM.md](RELATIVE_OVERFLOWING_NHIM.md) proves the
  relative doubling and parameter bridge needed for the auxiliary saddle-type
  center graph at the resolved \(K_1\) corner, using the precisely restated
  classical compact boundaryless NHIM theorem.
- [FINITE_MARKED_ATLAS_DESCENT.md](FINITE_MARKED_ATLAS_DESCENT.md) proves the
  finite-atlas physical descent used by V6--V7 and records, separately, the
  still-conditional criterion for one global exact marked chart.

## Registration rule

Before a new local theorem-sized result is described as extending the source
theory, its register entry must state:

- the local claim ID and exact evidence file;
- every imported theorem or certificate, with frozen revision and hypotheses;
- all preceding local claims on which it depends;
- whether it is analytic, non-rigorous numerical, or interval-rigorous; and
- the upstream impact, which is `none` unless and until a separate upstream
  change is actually accepted.

Status changes remain governed by `CLAIM_REGISTER.md`: a provenance record by
itself proves nothing.
