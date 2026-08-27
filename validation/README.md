# Issue #7 validation workspace

This directory is the local staging area for the deferred outward-rounded
validation in [Issue #7](https://github.com/h-lu/rfsn-ii-positive-parameter-pde/issues/7).
Nothing currently stored here is a computer-assisted proof or a validation
certificate.  The only implemented layer is a deliberately non-claim-bearing
candidate-contract and replay scaffold.

## Two evidence lanes

The lanes must remain separate.

1. **Floating candidate generation.**  SciPy trajectories locate useful
   branches, sections, cutoffs, coordinate scales, and likely margins.  The
   evidence label is `COMPUTED/E1_NONRIGOROUS_CANDIDATE`.
2. **Claim-bearing interval validation.**  A future source-only executable must
   use outward-rounded intervals, enclose truncation and rounding error, bind
   every result to a clean frozen source revision, and return exactly `PASS`,
   `FAIL`, or `INCONCLUSIVE`.

A small residual, tolerance refinement, schema success, or matching SHA-256
does not move an object from lane 1 to lane 2.

Neither lane, by itself, establishes temporal stability, dynamic Turing
selection, connection to a Turing bifurcation branch, or identification of a
computed segment as a canard.  Those are separate model questions from the
stationary spatial return/exit validation staged here.

## Implemented candidate objects

[`numerics/vdp_complete_branches.py`](../numerics/vdp_complete_branches.py)
constructs complete finite return candidates.  The configuration-v4 master
uses the current periodic source anchors to save B1 and A2, which realize
negative and positive target transverse-sign proxies, respectively.  Each
record differs from the broad first-event sampler in three important ways:

- the source and return target are the same numerical face
  \(\rho_u=\lVert(x_u,y_u)\rVert=0.01\);
- the source state is used directly, avoiding an exponentially amplified
  phase/transverse reconstruction perturbation;
- physical length and the physical action

  \[
  L'=r\epsilon^{-1/4},\qquad
  \mathscr A'=\epsilon^{9/4}r^5(P^2-Q^2)
  \]

  are augmented ODE variables across both the global and local-passage
  segments.

The target sign is the sign of the target **numerical transverse coordinate**,
not the sign of the first unstable eigen-coordinate.  It remains a proxy
because this numerical coordinate is not V2's exact action coordinate.  The
record stores saddle residence turns but intentionally assigns no integer V6
winding.

Run its regression tests with

```bash
python3 -m unittest numerics.test_vdp_complete_branches
```

The module exposes `as_candidate_record()` for JSON metadata and
`as_npz_payload()` for dense numeric arrays.  The master writes the combined
arrays to
[`v6_complete_branches.npz`](../numerics/results/vdp_v1_v7/v6_complete_branches.npz)
and one `v6_complete_*.json` record per return.  In the frozen run, B1 has
physical length approximately \(1.804227066\) and action
\(4.790934975\times10^{-5}\); A2 has length approximately \(2.159739115\) and
action \(4.790930102\times10^{-5}\).  These are ordinary finite returns with
zero end counterterms, not certified V6 edge labels or all-winding data.

The same master run also binds three end/matching candidate layers:

- [`numerics/vdp_source_to_pole.py`](../numerics/vdp_source_to_pole.py)
  produces a finite-horizon nonlinear-\(W^u\) source window and a same-orbit
  source--gate--pole/action record in
  [`v3_pole.json`](../numerics/results/vdp_v1_v7/v3_pole.json);
- [`numerics/vdp_matched_outer.py`](../numerics/vdp_matched_outer.py) produces
  the coupled nonlinear-\(W^u\)--central--resolved-\(K_1\)--finite-horizon
  outer candidate in
  [`v4_v5_matched_candidate.json`](../numerics/results/vdp_v1_v7/v4_v5_matched_candidate.json);
- V5A finite same-\(Q\) subtraction uses that saved outer leg and is recorded in
  [`v5a_outer_finite_part.json`](../numerics/results/vdp_v1_v7/v5a_outer_finite_part.json).

All of these inputs remain `COMPUTED/E1` and `NOT_INTERVAL_VALIDATED`.

## Candidate contract

[`candidate_contract.schema.json`](candidate_contract.schema.json) is a JSON
Schema Draft 2020-12 contract for one pre-validation candidate package.  It
requires:

- a full repository commit, dirty-state declaration, and explicit dirty-tree
  reproducibility status;
- SHA-256 bindings to the exact local V2--V6 theorem text, configuration,
  generator sources, and every candidate file;
- parameter endpoints as exact base-ten rational strings;
- fixed observable definitions and normalizations;
- an enumerated obligation list with hash-bound candidate evidence and explicit
  blockers; the generated schema-v2 contract records aggregate candidate replay and
  blocked outward-rounded validation, while future contracts must refine that
  list into sign, inclusion, transversality, first-event, derivative, length,
  and action clauses;
- explicit nonclaims, `claim_bearing: false`, and `final_status: NOT_RUN`.

The allowed obligation statuses are only `UNASSESSED`, `CANDIDATE_READY`, and
`BLOCKED`.  The schema deliberately cannot encode a claim-bearing `PASS`.

Check the scaffold itself with

```bash
python3 validation/check_candidate_contract.py
```

and a future contract with

```bash
python3 validation/check_candidate_contract.py path/to/candidate-contract.json
```

The checker validates the schema, orders exact decimal endpoints with decimal
arithmetic, resolves every path inside the repository before reading it,
verifies all referenced SHA-256 hashes, and confirms that embedded branch
records remain non-claim-bearing.  It also cross-checks branch parameters,
NPZ prefixes, required array shapes, finite values, endpoints, observables,
Git HEAD, and dirty state.  A dirty source tree produces
`PASS_WITH_DIRTY_SOURCE_WARNING`, not an unqualified reproducibility claim;
every success message explicitly says that no interval validation was
performed.

[`build_vdp_candidate_contract.py`](build_vdp_candidate_contract.py) is the
deterministic builder used by `numerics/run_vdp_master.py`.  It hashes the
local V2--V6 theorem texts, configuration, direct generator sources,
environment lock, candidate evidence, both branch records, and their shared
dense array file before atomically writing
[`v6_candidate_contract.json`](../numerics/results/vdp_v1_v7/v6_candidate_contract.json).
The generated contract deliberately retains `claim_bearing: false` and
`final_status: NOT_RUN`; a passing schema/hash replay says only that the
floating inputs are internally bound.

## Environment lock status

[`environment.lock.json`](environment.lock.json) records the exact exploratory
Python versions used on this workstation and pins the proposed rigorous source
backend to CAPD::DynSys `v6.0.0`, commit
`693998cd6d73a0c4e1b141bfb79fcad1c40c3cbe`.  CAPD supplies validated ODE and
Poincare-map machinery, including derivative propagation, but it is not yet
installed or executed here.  The lock therefore carries the literal status
`INCOMPLETE_SCAFFOLD_NOT_CLAIM_BEARING`.

Before the first claim-bearing run, this inventory must be replaced or
extended by all of the following:

- a clean committed source revision and immutable theorem/report hashes;
- an installable dependency lock with source/archive hashes;
- a pinned compiler and system environment, preferably a container image by
  digest as well as a native-build manifest;
- flags excluding fast-math and uncontrolled contraction;
- a rounding self-test recording the process and thread floating-point
  environment;
- interval endpoints serialized losslessly (binary64 hexadecimal endpoints or
  exact multiprecision decimal/rational strings);
- a claim-bearing executable hash, full stdout/stderr log, and independent
  machine replay.

## Required interval checks for V6

The future V6 certificate must not be a rerun of the finite grid.  At minimum
it must discharge the following classes of obligations on a preselected
positive parameter box.

1. Validate the parameter-dependent saddle frame or exact local chart, its
   inverse, phase convention, and source parameterization.  Interval Newton
   must prove existence and uniqueness of the zero-energy fiber solve.
2. Cover each source cell by boxes and rigorously integrate each box to its
   first physical event.  The active event speed, all inactive-face margins,
   event order, flow-domain buffer, and boundary priority must be enclosed.
3. Prove the boxes form the required disjoint connected component census; an
   adaptive plot cannot prove exhaustion, no gaps, or no overlap.
4. Enclose return maps and their state/parameter derivatives through order two
   on fixed chart rectangles, then verify the cross-form contraction and
   scaled thin-direction bounds.
5. Integrate length and action as augmented variables.  Every finite cut must
   join the same enclosed physical orbit, and interval composition residuals
   must contain zero with a declared width bound.
6. For pole and algebraic exits, turn the current connected floating V3 and
   coupled V5/V5A candidates into outward-rounded source-to-tail enclosures.
   Only the terminal tail receives its prescribed counterterm.  A connected
   SciPy trajectory or collocation solution cannot be inserted into a
   claim-bearing branch without truncation, interface, and infinite-tail error
   bounds.
7. Reduce the all-\(n\ge N\) conclusion to finitely many validated uniform
   inequalities and analytic tail bounds; checking finitely many winding
   samples is insufficient.

CAPD's interval ODE and Poincare-map routines are a suitable kernel for the
compact finite-flow clauses.  The V3/V5A infinite-end remainders and the
all-winding reduction still require model-specific interval estimates around
the analytic constructions.

## Current blockers to a claim-bearing run

- The numerical directory and local theory amendments are not yet bound to a
  clean immutable repository revision.
- The exploratory point \((r,a_2,\epsilon)=(0.08,0,1)\) is not an explicitly
  certified theorem box.
- The existing finite event faces are proxies rather than the complete V6
  physical arrangement and finite marked atlas; B1/A2 do not prove a component
  census, cross form, bounded overlap recoding, or every \(n\ge N\).
- The connected V3 and V5/V5A candidates are explicit floating objects, but
  the certified source window/parameter box, infinite V4 graph, V5 uniform
  tube, endpoint adjoint/exchange, matching uniqueness, parameter jets, and
  infinite finite-part remainders are not interval enclosures.
- No outward-rounded backend, rounding manifest, interval certificate, or
  independent replay exists yet.

These blockers do not make the floating repository a toy.  Its deterministic
raw outputs and complete B1/A2 return records provide candidate centers,
scales, event ordering, interfaces, and observable checks for the rigorous
implementation.  They do mean that the first Issue #7 status is still
`NOT_RUN`, not `PASS`.
