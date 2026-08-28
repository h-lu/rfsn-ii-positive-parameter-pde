# Flagship import audit: frozen long draft versus focused paper

**Audit date:** 2026-08-28  
**Evidence status:** provenance, theorem-interface, and accessibility audit;
no certificate was rerun  
**Flagship boundary:** read-only

This audit closes Phase 2 of the continuation plan at the level of theorem
provenance.  It compares every flagship input used by this repository with
the immutable long-draft baseline and with the compressed focused paper.  It
does not prove an application theorem, upgrade a certificate, or change a
claim status.

## 1. Revisions inspected and baseline decision

| Role | Revision | Object inspected |
|---|---|---|
| Normative application baseline | `d54add098545063d5efe8f1d6f062d4cfc116a0d` | `papers/paper-a/manuscript/main.tex`, 9163 lines |
| Current remote flagship `main` | `8e04dc3` | split focused manuscript under `papers/paper-a/focused/` |
| Current read-only local focused work | `3516a2ee499fc74a46d0ec204736bde8d3782c59` | sentence-compressed focused manuscript |

The normative baseline remains `d54add098545063d5efe8f1d6f062d4cfc116a0d`.
There is no repin.  The reasons are mathematical rather than administrative:

1. the long draft contains compact-parameter and mixed state/parameter
   versions that the focused paper deliberately specializes to one fixed
   Hamiltonian;
2. the optional Jost identification used by the van der Pol singular
   comparison is present only in the long draft;
3. the focused pole theorem assumes an isolated boundary sink with three
   simple positive indicial roots, whereas the positive-parameter van der Pol
   pole has a two-dimensional boundary equilibrium NHIM; and
4. the focused working revision has not been frozen as a stable public
   release.

The focused paper is therefore a valuable current cross-reference, not an
interchangeable replacement for the import contract.

## 2. Classification convention

The classification below concerns use in this application.

- **Directly applicable:** the cited statement has the same object,
  hypotheses, regularity, and quantifier order.
- **Adapted locally:** the proof mechanism survives, but this repository must
  add parameter-uniform, coordinate-specific, or model-specific work.
- **Not applicable:** a decisive geometric object or hypothesis differs.

The separate column “retention” records whether the compressed focused paper
still contains the clause.  Thus a clause can be directly applicable from the
frozen baseline yet be archive-only in the current paper.

## 3. Complete crosswalk

### 3.1 Selected core homoclinic used by both applications

| Imported clause | Frozen source | Focused source | Retention | Application class and boundary |
|---|---|---|---|---|
| Universal core field, reverser, saddle-focus spectrum, and true unstable source circle | Definition 2.1(I1), Proposition 8.6, equations (8.31)--(8.35) | Section 6, the RFSN-II field and item V3 | retained | **Directly applicable** at the zero-parameter core only. No positive-parameter conclusion is imported. |
| Selected symmetric homoclinic, first symmetry hit, local uniqueness, and determinant enclosure | Proposition 8.6(I2), equations (8.36)--(8.40), M3 certificate | Section 6, item V3, and `thm:rfsn-realization` | retained with the same shooting box and determinant | **Directly applicable** as the computer-assisted Core Lemma. Brusselator use is audited separately in [`../brusselator/CORE_IMPORT_AUDIT.md`](../brusselator/CORE_IMPORT_AUDIT.md). |
| Transversality modulo the flow direction in the regular energy surface | Proposition 8.6(I2), using the determinant and tangent rows | Section 6, item V3 | retained | **Directly applicable**. It is not ambient transversality in four dimensions and does not assert global uniqueness. |

### 3.2 Central compact package used by V2

| Imported clause | Frozen source | Focused source | Retention | Application class and local obligation |
|---|---|---|---|---|
| Reversible exact saddle coordinates and weighted-log passage | Proposition 2.7 | `lem:normal-form-to-passage` and `lem:mixed-passage` | retained for one fixed Hamiltonian | **Adapted locally.** V2 must supply a common analytic domain, one compact parameter box, mixed parameter two-jets, the Kato-oriented phase sign, exact sections, and one uniform winding threshold. |
| Transverse homoclinic implies a finite limiting matching graph with inverse and range margins | Proposition 2.11, `prop:transverse-homoclinic-produces-h1` | `lem:simultaneous-fixed-choice`, `prop:winding-selector` | retained at fixed system | **Adapted locally** only for uniform parameter dependence; the zero-parameter transversality itself is direct. V2 supplies continuation and V6 supplies the final common box. |
| Finite clean/neat labelled event arrangement and component-preserving stability | Definition 2.8(H2), Proposition 5.2 | `prop:block-production`, `prop:neat-arrangement-stability` | retained and strengthened in fixed-system exposition | **Adapted locally.** The focused construction is fixed-system. V6 must establish the finite compact-family census after pulling every actual face through the same signed template. |
| Compact first-hit stability, including prescribed simultaneous faces | Lemma 5.3 | `lem:first-hit`, used in `prop:complete-census` | retained | **Adapted locally** for the compact family and mixed parameter bounds; direct after those uniform hypotheses are checked. |
| Certified algebraic, homoclinic, and pole-directed finite source anchors and strict base-point gate inequalities | Proposition 8.4, Proposition 8.6(I3), equations (8.41), (8.49)--(8.52) | Section 6, items V2--V4 and the phase-gap paragraph | retained | **Directly applicable** only as finite zero-parameter anchors. Entry into either positive-parameter noncompact end is not imported. |
| Aggregate margin $m_0>0$ used by the application import | no named flagship constant; obtained by normalizing and taking the minimum of the finite strict margins in I3/H2, Proposition 5.2, and Lemma 5.3 | the focused block and arrangement have the same finite strict-margin mechanism | local definition | **Adapted locally.** It has no reported numerical lower bound and is not a flagship interval certificate. The frozen source supplies existence of suitable finite faces and tubes, not a serialized numerical face atlas. |

The normative statement and its exclusions remain
[`../van-der-pol/CENTRAL_CORE_IMPORT.md`](../van-der-pol/CENTRAL_CORE_IMPORT.md).
The focused normal-form lemma explicitly says that all its constants concern
the fixed Hamiltonian.  It therefore cannot, by itself, justify the mixed
parameter estimates asserted by V2--V7.

### 3.3 Singular algebraic comparison used by V5

| Imported clause | Frozen source | Focused source | Retention | Application class and boundary |
|---|---|---|---|---|
| Canonical locally maximal algebraic future hypersurface, weighted tail, and finite saturation | Proposition 8.1, `prop:core-algebraic-future`; four rate gaps and the following finite-saturation display give the $C^4$ version | `prop:rfsn-algebraic-graph`, Section 6 item V1 | the $C^3$, third-order-bunched geometric core is retained; the stronger $C^4$/fourth-gap wording is long-draft only | **Directly applicable from the frozen baseline** at the singular comparison system $r=0$. The compressed paper alone supports only the stated $C^3$ version. The positive-parameter outer graph is V4, not an imported persistence conclusion. |
| Exact Jost basis, symplectic pairings, growing/recessive splitting, and identification of the canonical tangent | optional appendix `app:jost-source-arm`; basis and Cauchy data in `eq:exact-jost-basis` and `eq:jost-cauchy-data`, pairings in `eq:jost-symplectic-pairings`, and tangent equality proved just after `eq:weighted-horizontal-tangent` | no corresponding Jost module in the focused manuscript | long-draft only | **Directly applicable from the frozen baseline** to the exact singular orbit, but archive-only. The normalization \(\psi=\omega(\mathbf s,\cdot)\) and \(\psi(\mathbf u)=24B_2B_3=144\sqrt3\) are explicit local algebraic consequences of the frozen basis, Cauchy data, symplectic form, and \(B_2B_3=6\sqrt3\), rather than a verbatim flagship display. No positive-parameter Jost theorem is imported. |
| Locally unique transverse intersection of the source with the canonical algebraic hypersurface, including source phase and bordered nonsingularity | Proposition 8.4, `prop:core-origin-algebraic`, M2 certificate | Section 6 item V2 and `thm:rfsn-realization` | retained | **Directly applicable** at $r=0$. V5 proves the resolved $K_2\to K_1\to$ outer continuation and uniform matching separately. |

Section 2 of
[`../van-der-pol/CENTRAL_OUTER_MATCHING.md`](../van-der-pol/CENTRAL_OUTER_MATCHING.md)
is correctly bounded: it imports three singular comparison facts and no
positive-parameter end, matching theorem, or action finite part.

### 3.4 High-winding return, first-event, action, and coding modules

| Imported clause | Frozen source | Focused source | Retention | Application class and local obligation |
|---|---|---|---|---|
| Opposite-endpoint mixed passage and weighted exponential estimates | `lem:mixed-passage` | `lem:mixed-passage` | retained for the fixed system | **Adapted locally** for a compact parameter family and mixed parameter two-jets. |
| Stable/unstable half-tail action gluing | `lem:action-gluing` | `lem:action-gluing` | retained | Fixed-system identity is **directly applicable** after a local exact chart exists; the uniform mixed-family estimate is **adapted locally**. |
| Uniform winding selector and completed cross forms | `prop:selector` and the simultaneous section-shear equations | `prop:winding-selector` | retained, renamed | **Adapted locally** to the Kato convention, compact parameter box, finite marked atlas, and one physical residence-time threshold. |
| Whole normalized-cell convergence | completed cross-form and scaled-seam estimates used by `prop:first-exit-family` | `prop:whole-cell-exit-convergence` | retained and made explicit | **Adapted locally** for parameter uniformity and composition with the concrete V3/V5 face functions. |
| Persistence of the complete labelled first-event census | `prop:first-exit-family` | `prop:neat-arrangement-stability`, `lem:first-hit`, `prop:complete-census`, items (i)--(ii) of `thm:focused-main` | retained and reorganized | **Adapted locally.** V6 must construct the physical end apertures and every auxiliary lateral face before applying the abstract persistence mechanism. |
| Exact finite-branch action, gluing, singular-end composition, and section/gauge covariance | `prop:section-gauge-covariance`, `cor:physical-covariance`, finite-composition clauses | `prop:finite-flight-action`, `prop:return-time-action-limits`, `prop:renormalized-action-composition`, `prop:end-covariance` | retained and expanded | Finite exact identities are **directly applicable**. Terminal counterterms are **not imported**; V3 and V5A supply them, with the spare derivative needed for a quantitative mixed-$C^2$ rate. |
| Countable coding, stable plaques, finite terminal words, and periodic-orbit composition | `thm:terminal-extension`, `cor:period-action-asymptotics` | `cor:focused-coding`, `cor:terminal-itinerary-action` | retained in fixed-system form | **Adapted locally** to a finite compatible atlas and a compact parameter family. T2 supplies physical descent after all chartwise modules are constructed. |
| Descent from finitely many compatible marked charts to one physical first-event relation and invariant closed observables | `cor:physical-covariance` and the long-draft chart-production/covariance architecture | no standalone finite-atlas theorem in the focused paper | not retained as a focused theorem | **Adapted locally.** Proposition T2 in [`FINITE_MARKED_ATLAS_DESCENT.md`](FINITE_MARKED_ATLAS_DESCENT.md) supplies only descent of already constructed local modules; it cannot create a missing passage, event census, terminal map, or coding branch. |

The precise application interface remains
[`../van-der-pol/RETURN_EXIT_CODING_IMPORT.md`](../van-der-pol/RETURN_EXIT_CODING_IMPORT.md).
The frozen long draft contains a compact-parameter theorem architecture, so
the historical import is not fabricated.  The current focused paper does not
state that family theorem; its complete-census proof explicitly says that it
concerns the fixed system and asserts no differentiable dependence on an
additional system parameter.  Publication prose must therefore either cite an
accessible frozen version or present the local compact-family proposition in
this repository.

### 3.5 Clauses that must not be imported

| Focused result | Decisive mismatch | Classification here |
|---|---|---|
| Focused H3 pole: isolated hyperbolic boundary sink, simple roots 1, 4, 6, and fixed action order 6 | The positive-parameter van der Pol boundary object is a two-dimensional equilibrium NHIM with normalized spectrum $\{-1,0,0,1,4\}$ and admissible roots 1, 4 | **Not applicable.** V3 needs a local NHIM-pole terminal theorem, including its open aperture, mixed end labels, Laurent--log finite part, and finite-branch composition. |
| Focused RFSN-II algebraic and pole compactifications | The full positive-parameter equations change both dominant end balances | **Not applicable.** V3--V5A construct the two ends and their matching locally. |
| A single fixed exact saddle chart and raw winding label | The application parameter box may require a finite chart cover and bounded deck recodings | **Not applicable as a global claim.** V6 works chartwise and invokes T2 only after construction; optional T2G is not assumed. |
| Focused temporal or physical pattern selection | The flagship theorem is spatial-dynamical and stationary | **Not applicable.** Temporal stability, Turing selection, canard identification on a computed orbit, and experiments remain separate claims. |

## 4. Evidence closure and external accessibility

The following four claim-bearing certificates, replay graph, and environment
lock are byte-identical at the frozen baseline, remote focused `main`, and
the inspected local focused revision:

| Object | SHA-256 | Replay-manifest role |
|---|---|---|
| `validation/replay_manifest.json` | `15905f5a20b24a0ae0d298d9d14aa940177a006cc2cce3f2a39fd2e1cf4dac9b` | binds packages, dependencies, commands, comparison policy, and source-hash contracts |
| `validation/environment.lock.json` | `6240ebdbf0f296738534c07a33aea40202883f6abf37e1ff28e43dad47aa0cba` | locks CPU platform, compiler, CAPD/FILIB, Python packages, and replay policy |
| symmetric core homoclinic certificate | `ed0f9f58f8ba5f1d5c36dc7c3a72bb725599c4172a3cd610d890b88699fecfbd` | `source-verifiable-only`; M3 homoclinic and matching input |
| origin--algebraic certificate | `60882ee1d3b2b18264b85764288505ae8b47d00bc826a2bddec152898f690fbe` | `source-verifiable-only`; algebraic anchor and transverse connection |
| future-target certificate | `88fa64035bb4352f5e25aa8d1627b191936264958c125dface59c5a767f6b3ce` | `source-verifiable-only`; canonical graph and target margins |
| pole-entry certificate | `7f325a87810f8b0dda2542aed90263b39f9a9f4bd2e8ebb3abcc238d032eb6e2` | `source-verifiable-only`; finite pole-directed gate and source window |

The replay manifest binds the exact probe sources through each certificate's
`source_sha256` map and declares `validation/replay_all.py` as the driver.
It also says that historical certificate JSON alone is never a replay pass.
This audit checked the immutable files and their hashes; it deliberately did
not perform a second computation or an independent-machine replay.

Anonymous HTTP access to both the flagship repository and the raw frozen
manifest returned `404` on the audit date.  Therefore the chain is currently:

```text
immutable local source + certificates + environment + replay graph
    -> author-verifiable frozen provenance
    -/-> externally accessible referee evidence closure.
```

This is a publication-access blocker, not evidence that any locally proved
analytic implication is false.  Until a stable release or archive exposes the
complete closure, the application papers must state that their theorems are
conditional on the cited frozen RFSN-II inputs.

## 5. Local theorem obligations exposed by the audit

Only two theorem-sized interfaces must be closed before a polished van der
Pol paper is justified.

1. **Compact-family passage and whole-cell theorem.** Assemble the existing
   local exact frame and analytic normal form with the zero-energy graph,
   exact incoming/outgoing sections, weighted passage, finite flights,
   selector, and complete first-event arrangement. State common domains,
   mixed derivatives, strict margins, and one uniform physical residence-time
   threshold on the final parameter box.
2. **Positive NHIM-pole terminal theorem.** State the genuine V3 boundary
   NHIM, stable-fiber projection, open pole aperture, roots 1 and 4,
   Laurent--log action subtraction, mixed label/parameter derivatives, and
   compatibility with first-event labels and exact finite-branch
   composition. Do not cite focused H3 as this theorem.

The existing local sources already contain most ingredients, but those
ingredients must be assembled and audited as theorem interfaces rather than
treated as consequences of similarly named focused clauses.

## 6. Downstream decision

- Keep `d54add098545063d5efe8f1d6f062d4cfc116a0d` as the normative baseline.
- Do not change B1--B2 or V1--V7 claim statuses in this audit.
- Keep both application papers conditional on frozen inputs until external
  accessibility is repaired.
- Proceed to the Phase 3 seam audit, beginning with the two local theorem
  obligations in Section 5.
- Do not begin explicit-box interval validation merely to compensate for a
  missing analytic interface; Issue #7 remains the later strengthening lane.
