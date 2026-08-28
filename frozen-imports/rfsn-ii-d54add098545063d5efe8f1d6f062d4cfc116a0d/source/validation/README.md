# Rigorous validation boundary

## Unified replay entry point

The machine-readable dependency graph is
[`replay_manifest.json`](replay_manifest.json), and the required software and
library hashes are recorded in
[`environment.lock.json`](environment.lock.json).  The fail-closed driver is
[`replay_all.py`](replay_all.py).  It distinguishes the certificates used by
the normal-form realization of the main theorem, the additional selected-
branch certificates, and two ancillary certificates which are not used by the
manuscript's main theorem.

From the repository root, inspect the graph and perform the source/dependency
audit without running CAPD via

```bash
python3 validation/replay_all.py --list
python3 validation/replay_all.py --profile main-theorem --dry-run
```

A dry run never reports a certificate replay PASS.  A pinned toolchain
preflight is

```bash
PATH=/tmp/cmake-4.2.3-clean/bin:$PATH \
PYTHONDONTWRITEBYTECODE=1 \
python3 validation/replay_all.py \
  --profile main-theorem \
  --preflight-only \
  --capd-source /tmp/papera-capd.bKwHIQ/CAPD \
  --capd-config /tmp/papera-capd.bKwHIQ/CAPD/build/bin/capd-config \
  --report /tmp/paper-a-preflight.json
```

The source checkout path in this command is part of the pinned byte-level
contract, not a replaceable example.  One CAPD translation unit records an
absolute `__FILE__` string, so rebuilding the same CAPD commit and options at a
different path changes `libcapd.a`.  The required commit, build options,
compiler and library hashes are recorded in `environment.lock.json`; the
[toolchain audit README](toolchain-metadata-audit/README.md) gives the exact
rebuild procedure.

Omit `--preflight-only` to execute the selected profile.  Available profiles
are `main-theorem`, `selected-branch`, `ancillary`, and `all`.  Every build and
bulk replay product is written below a temporary directory outside the
repository.  A normal run requires a clean checkout unless the explicitly
development-only `--allow-dirty` option is supplied.  A dirty run may execute
all probes for diagnosis, but it finishes with
`PASS-DEVELOPMENT-DIRTY-NOT-RELEASE-ELIGIBLE`, keeps
`profile_replay_pass=false`, and can never serve as release evidence.

The release trust boundary is intentionally narrow.  The driver accepts only
the repository's fixed `replay_manifest.json` and `environment.lock.json`,
checks their two-way path binding, rejects package-ID path syntax and runner
remapping, and requires a source/dependency hash contract for every
mathematical package.  Each run uses a newly created empty work directory
outside the repository; an existing path or symbolic-link target is refused.
Inherited compiler, Python-import, linker, shell-startup, and `PAPERA_*`
overrides are removed.  Preflight then pins the actual compiler executable and
hash, exact version banner, C++ standard, CAPD/FILIB library hashes, CMake cache,
rounding flag, compile markers, and link markers before any claim probe runs.
The worktree is checked again after the last package, so a probe that writes
back into the repository turns the run into `FAIL` rather than `PASS`.

Run the adversarial trust-boundary regressions with

```bash
PYTHONDONTWRITEBYTECODE=1 python3 validation/test_replay_all.py
```

The former stale-source and archived-path blockers have been repaired by
source-only rebuilds in the pinned CAPD/FILIB environment.  In particular, the
future graph/corridor probes, the exact-source 17,345-box plus 2,002-box cover,
the finite collar, both endpoint bridges, and the 9,725-box spiral extension
have all been regenerated and compared with their tracked certificates.  A
development execution of the complete `selected-branch` profile made every
package return `PASS`.  Because that execution used the explicitly dirty mode
while the candidate was being edited, its top-level status was correctly
`PASS-DEVELOPMENT-DIRTY-NOT-RELEASE-ELIGIBLE`; it is diagnostic evidence, not
a release replay.  Release evidence still requires a committed clean checkout,
omits `--allow-dirty`, and must finish with top-level `PASS`,
`profile_replay_pass=true`, and `release_eligible=true`.  Historical JSON and
the successful dirty report are never promoted to a clean-checkout PASS.

The current validation packages are:

- [pole-cone-entry](pole-cone-entry/README.md) certifies, with CAPD/FILIB,
  that the limiting raw-crest family \(r\in[1/20,2]\) enters one analytic
  invariant pole cone. Combined with the analytic tail theorem, it proves a
  finite pole on that interval.

- [origin-unstable-pole-entry](origin-unstable-pole-entry/README.md)
  certifies one robust open phase interval \((-0.2,0.2)\) on the true local
  \(W^u(0)\) circle of radius \(.01\). Uniformly over the independently
  proved \(C^0/C^1\) graph and tangent budgets, all 400 phase boxes have a
  strict first inward hit of \(x=10\) inside the analytic pole cone. This
  zero-energy sector is disjoint from the certified algebraic and homoclinic
  phases and is not the raw-crest source family; no all-phase claim is made.

- [future-target-fold](future-target-fold/README.md) certifies, with exact
  symbolic generation and CAPD/FILIB interval arithmetic, the unique physical
  future-staying algebraic graph on both the original negative-energy corridor
  and a signed \(|E|\le0.012\) corridor containing the exact \(E=0\)
  algebraic orbit. Weighted one-through-four rate gaps give \(C^4\)
  regularity, while the unweighted chart supplies explicit \(C^2\) target
  budgets. The package also certifies one regular simple negative-energy fold of its
  \(\operatorname{Fix}\mathcal R\) source trace.  The target graph is selected
  by forward confinement in the unextended physical field; the 248-dimensional
  Krawczyk test is uniform in its declared \(C^2\) jet bounds.  The package
  does not continue the full source component or prove an origin
  heteroclinic.

- [exact-source-outer-fold](exact-source-outer-fold/README.md) certifies one
  selected \(C^2\) arc of the declared finite saturation
  \(\mathcal W_{\rm a}\cap\operatorname{Fix}\mathcal R\) from the exact
  algebraic source \((U,V)=(0,1/6)\) to the previously certified robust
  outer energy fold.  A 17,345-box mixed-chart fixed-time cover and a 2,002-box
  sign tail have true common-root containment at every adjacency.  An
  analytic tail-graph/Jost pullback lemma identifies the exact source tangent,
  and a 248-dimensional \(C^2\) cap excludes a second fold before the known
  robust fold.  The conclusion is limited to this selected arc in the
  declared flow tube; it does not classify other reversible source branches
  or saturate the tail graph globally.

- [finite-source-intermediate-collar](finite-source-intermediate-collar/README.md)
  certifies a connected first-stage event-chart segment of the canonical
  future-target source trace.  It contains 6,316 uniform root boxes and 6,315
  common-parameter root-containment bridges, including a fixed-\(V\) to
  fixed-\(U\) chart switch; every orbit has the declared first event and every
  root/tangent inclusion is strict.  The inward endpoint has source radius
  about \(0.025\), so the first-stage certificate by itself is an
  intermediate collar.  Its source-only spiral extension now reaches the
  fixed radial local seam; the outer continuation is supplied separately by
  `exact-source-outer-fold`.

- [fixed-fold-event-bridge](fixed-fold-event-bridge/README.md) identifies the
  robust fixed-\(T=15\) physical fold root with box 0 of the finite
  intermediate-collar cover.  A sharpened 248-dimensional fold Krawczyk
  enclosure is propagated by a CAPD Poincare map; all 37 event nodes and the
  flight time lie strictly inside the box-0 uniqueness tube.  The replay also
  checks box-0 first-event and tangent certificates.  This closes only that
  endpoint seam, not the inward spiral or the outer algebraic endpoint.

- [fundamental-annulus-overlap](fundamental-annulus-overlap/README.md)
  certifies the quantitative local saddle-focus collar
  \(0<R\le2.4\times10^{-4}\), its unique first unstable exit, one uniform
  exit-to-target chart, and a fixed radial seam with rigorous phase and
  energy derivatives. The seam root is identified with the same selected
  local arm. This package does not itself fill the source-component gap from
  the preceding intermediate collar at \(R\simeq.025\); the separate
  finite-to-local seam certificate supplies that adjacency chain.

- [origin-algebraic-heteroclinic](origin-algebraic-heteroclinic/README.md)
  certifies the missing local incidence: a 148-dimensional robust Krawczyk
  enclosure proves one zero-energy orbit from the true local
  \(W^u(0)\) graph to the canonical signed-energy algebraic future graph.
  The intersection is locally unique modulo time translation and transverse
  modulo the common flow direction. It does not classify or continue the
  complete source component.

- [universal-core-periodic-return](universal-core-periodic-return/README.md)
  certifies one nonconstant negative-energy reversible periodic orbit in the
  locked source block, including the complete first-positive-symmetry-hit
  cover and a nonzero return determinant.  It proves only a local analytic
  return curve, not its global branch placement.

- [universal-core-symmetric-homoclinic](universal-core-symmetric-homoclinic/README.md)
  certifies, uniformly over the true local unstable-graph \(C^0/C^1\)
  budgets, a primary symmetric zero-energy homoclinic.  It proves the global
  first nonzero symmetry hit and energy-level nondegeneracy.  The conclusion
  is box-local uniqueness, not global homoclinic uniqueness or a bridge to
  the separately validated \(V=.08\) periodic-return point.

- [toolchain-metadata-audit](toolchain-metadata-audit/README.md) is a
  non-claim-bearing provenance addendum.  It verifies that the historical
  `capd-config --version` value `2.5.1` is the pkgconf frontend version, while
  the pinned CAPD source/library version is `6.1.0`; it preserves all existing
  claim-certificate bytes and hashes.

Floating exploration outside a named certificate remains E1.

The [future-branch reconnaissance](../archive/research-history/validation/future-branch-reconnaissance/README.md)
is intentionally such an E1 computation: it supplies fold and
saddle-focus seeds, not theorem evidence.

The newer
[physical future-branch continuation reconnaissance](../archive/research-history/validation/physical-future-branch-reconnaissance/README.md)
uses the nonlinear degree-seven tail centre on a moving compactified event.
It reproduces the certified first fold, resolves an alternating sequence of
shrinking E1 fold candidates with the saddle-focus ratios, and tests event
section dependence.  Only the externally cited first fold is interval
evidence; the continued component, later folds and candidate endpoints remain
floating-point theorem-design data.

The [origin unstable-manifold reconnaissance](../archive/research-history/validation/origin-unstable-reconnaissance/README.md)
tests the proposed origin-to-algebraic connection in the opposite
direction. Its exact formal jet plus floating phase scan supplied the critical
heteroclinic seed, but is not itself theorem evidence. In particular, the old
candidate assertion that every nonzero origin-unstable phase enters the pole
channel has been rejected; it must not be inferred from sampled phases.

Computer-assisted work may enter this repository only after the analytic
objects, gauges, continuous operator bridge and parameter box are fixed. A
certificate must prove a named lemma on a predeclared domain and include all
discretization, truncation and interval errors. Solver convergence or sampled
signs are not certificates.
