# Issue #7 staged rigorous validation

This directory is the claim-isolated, outward-rounded validation lane for the
van der Pol application.  It does not upgrade the floating candidate contract
in `validation/`, and it does not modify or silently import the read-only
flagship repository.

The compiled runner has six executable scopes:

1. `preflight` verifies the pinned source/toolchain bindings and executes a
   CAPD/FILIB rounding self-test;
2. `kernel` additionally verifies the exact V1 polynomial identities and the
   V2(1) wedge, positivity, and saddle-focus inequalities on the frozen
   positive-width rational parameter box;
3. `local-graph` verifies the P2a moving eigenframe, isolating block,
   difference cone, true coarse local stable/unstable graphs, quadratic value
   bound, and backward decay rate on the frozen comparison bridge from
   `r=0` through the target box;
4. `h10-c01` reruns the frozen exact H10 homological recursion and verifies
   the P2b0 Euclidean \(C^0\) and Frobenius \(C^1\) tubes for those true graphs
   on the same bridge;
5. `p2-jets` verifies the P2b pure state \(C^2/C^3\) tensor bounds, the full
   rectangular \(D_b^{\le3}D_\theta^{\le2}\) weighted half-orbit recurrence,
   the induced mixed graph jets, and their physical-coordinate composition.
6. `p2-kato` fixes the absolute normalized source phase by exact Kato
   transport, verifies the physical (non-orthonormal) frame change and its
   \(C^2\) parameter bounds, and composes the already certified P2b graph jets
   with the radius-`.01` true source circle on the triangular source-jet set
   frozen for P2c.

The mathematical result of a local kernel run can be `PASS`, `FAIL`, or
`INCONCLUSIVE`.  The aggregate `final_status` remains `INCONCLUSIVE` while the
independent-machine replay required by the repository policy is pending.
Consequently every current local certificate has `claim_bearing: false`, even
when its mathematical obligations all pass.

The first clean local kernel certificate is archived at
[`results/vdp_box_v1_phase1.json`](results/vdp_box_v1_phase1.json) and explained
in [`PHASE1_REPORT.md`](PHASE1_REPORT.md).  It records integrity `PASS`,
mathematical `PASS`, aggregate `INCONCLUSIVE`, and `claim_bearing: false`.

The P2 obligation map, exact moving frame, non-circular graph bootstrap, and
the boundary between the staged local-graph obligations are frozen in
[`P2_VALIDATION_CONTRACT.md`](P2_VALIDATION_CONTRACT.md).
The first clean P2a certificate is archived at
[`results/vdp_bridge_v1_p2a_local_graph.json`](results/vdp_bridge_v1_p2a_local_graph.json)
and explained in [`P2A_REPORT.md`](P2A_REPORT.md).  Its two P2a mathematical
subobligations and all integrity checks pass; its aggregate status remains
`INCONCLUSIVE` and non-claim-bearing for the reasons above.

The first clean P2b0 certificate is archived at
[`results/vdp_bridge_v1_p2b_h10_c01.json`](results/vdp_bridge_v1_p2b_h10_c01.json)
and explained in [`P2B0_REPORT.md`](P2B0_REPORT.md).  Exact H10 regeneration,
the \(C^0\) tube, the \(C^1\) tube, and all integrity checks pass.  The parent
mixed-jet and weighted-half-orbit obligations remain pending, and the local
certificate remains non-claim-bearing while independent replay is 1/2.

The first clean P2b mixed-jet certificate is archived at
[`results/vdp_bridge_v1_p2b_jets.json`](results/vdp_bridge_v1_p2b_jets.json)
and explained in [`P2B_JETS_REPORT.md`](P2B_JETS_REPORT.md).  Every P2b
coefficient, higher-state-tensor, complete mixed-jet, and weighted-half-orbit
obligation passes, so the local parents `V2.WU.JETS` and `V2.WU_GRAPH` pass as
well.  Its aggregate remains `INCONCLUSIVE` and non-claim-bearing solely
because the current-computer-only lane supplies one of two required
independent machines.

The first clean P2bK certificate is archived at
[`results/vdp_bridge_v1_p2b_kato.json`](results/vdp_bridge_v1_p2b_kato.json)
and explained in [`P2B_KATO_REPORT.md`](P2B_KATO_REPORT.md).  Its locked
exact-algebra audit passes all 56 identities; the Riesz/Kato transport,
physical frame change, complete \(C^2\) parameter lift, radius-`.01` true
source circle, and nine-jet total-order-three source triangle all pass on the
complete bridge.  Its aggregate remains `INCONCLUSIVE` and non-claim-bearing
solely because independent replay remains 1/2.

The design-only P2c multiple-shooting scout is documented in
[`P2C_SCOUT_REPORT.md`](P2C_SCOUT_REPORT.md).  Its three-parameter affine
engine now validates all 16,384 exact rational cells covering
`[0,2/25] x [-1/4,1/4] x [4/5,6/5]`, all 44,416 internal common faces, and
the frozen selected-core anchor through 38-dimensional Krawczyk problems.
This is strict feasibility evidence for one selected `V2.HOM.BRANCH` over
the full bridge.  The same scout also proves strict dense sign tubes from the
true source face to the selected symmetry event on all 16,384 cells; combined
with the already certified P2a local-graph exclusion, this closes the P2c
first-hit design argument.  The uniqueness statement is deliberately limited
to the finite parameter-following lifted multiple-shooting tube: no direct
shooting zero outside that tube is excluded.  The actual-root C2 mode also
passes on all 16,384 cells and validates the phase/half-time parameter
two-jets.  The fixed-\(\xi\) continuous-time C2 middle mode then passes on the
same full grid.  It supplies the `V2.HOM.MIDDLE_C2` design atom by enclosing
the compact middle \([-11,11]\) and composing it with the local pre-source
pieces and the already enclosed infinite tails.  The full strict design run
therefore gives

\[
 T_*=11,\qquad \eta=1/5,\qquad C_{\rm hom}=71496600
\]

as one global original-parameter bound through derivative order two.

The four fixed-order strict summary logs are now archived under
[`design/logs/`](design/logs/).  The deliberately narrow retrospective
configuration
[`config/vdp_p2_homoclinic_v1.json`](config/vdp_p2_homoclinic_v1.json) and
[`p2_homoclinic_certificate.py`](p2_homoclinic_certificate.py) parse those
logs, verify the historical source/certificate bindings at their recorded Git
commits, and rerun the exact-Fraction tail composition.  This closes a local
P2c mathematical certificate without compiling or rerunning the full grid.
Its aggregate remains `INCONCLUSIVE` and non-claim-bearing because independent
replay is still 1/2.  The freeze is explicitly post-design and therefore is
not represented as preregistration.
The archived verdict and exact claim boundary are summarized in
[`P2C_CERTIFICATE_REPORT.md`](P2C_CERTIFICATE_REPORT.md), with the
machine-readable certificate in
[`results/vdp_bridge_v1_p2c_homoclinic.json`](results/vdp_bridge_v1_p2c_homoclinic.json).

The full-grid binary endpoints and exact rational composition are archived in
[`design/p2c_middle_jet_summary_v1.json`](design/p2c_middle_jet_summary_v1.json).

P2d has a deliberately narrow exact-algebra audit:
[`audit_p2d_exact_chart.py`](audit_p2d_exact_chart.py).  It performs 59
deterministic symbolic checks of the physical Hamiltonian convention, the
positive-Kato physical reversible symplectic completion, the frozen-to-Kato action
dictionary, the linear zero-energy branch, both radial section forms and
primitive gauges, and the linear time/phase logarithmic slopes.  Run it with

```bash
python3 validation/rigorous/audit_p2d_exact_chart.py
python3 -m unittest validation.rigorous.tests.test_p2d_exact_chart_audit
```

The exact audit is now paired with the separately implemented interval
frame layer frozen in
[`config/vdp_p2d_symplectic_frame_v1.json`](config/vdp_p2d_symplectic_frame_v1.json),
with source
[`src/vdp_p2d_symplectic_frame_probe.cpp`](src/vdp_p2d_symplectic_frame_probe.cpp)
and separate configuration/raw schemas.  On the same exact-rational
\(16\times8\times4\) bridge cover, the strict reference-toolchain run archives
componentwise normalized/original parameter-\(C^2\) enclosures for \(L\) and
\(L^{-1}\), and passes all 20 frozen scalar-branch, conditioning, and
matrix-jet-norm gates.  Combining this interval
result with the archived local P2bK mathematical pass and all 59 exact checks
gives a local mathematical `PASS` for
`V2.CHART.SYMPLECTIC_FRAME`.

The formal clean-source certificate is archived at
[`results/vdp_bridge_v1_p2d_symplectic_frame.json`](results/vdp_bridge_v1_p2d_symplectic_frame.json);
its source revision and all byte bindings are recorded inside the certificate.
The certificate has integrity and mathematical status `PASS`, while its final
status is `INCONCLUSIVE`, `claim_bearing=false`, and `release_eligible=false`.
Independent replay remains `PENDING_REQUIRED` at 1 of 2 distinct machines.
At the scope frozen by this frame certificate, the other six `V2.CHART.*`
atoms and the parent `V2.EXACT_CHART` were `OPEN`; in particular, the frame
result by itself supplied no nonlinear analytic normal form, nonlinear
zero-energy branch, exact nonlinear sections, weighted passage, physical
slides, or finite-cover overlaps.  See
[`P2D_FRAME_REPORT.md`](P2D_FRAME_REPORT.md) for that certificate's formal
claim boundary.

The next P2d design layer consists of two deliberately non-claim-bearing
artifacts.  [`audit_p2d_normal_form_exact.py`](audit_p2d_normal_form_exact.py)
passes 26 exact symbolic checks for the \(q=1,2\) Lie prefix.  At the core it
finds

\[
 Z_4=\frac{(I_2^{\rm K})^2-I_1^2}{120},
\]

and therefore only the conditional formal coefficient consequence
\(I_1=-\nu+c_2\nu^2+\cdots\Rightarrow c_2=0\), if a formal zero-energy graph
is continued.  It constructs neither that full formal graph nor an analytic
zero-energy branch.

[`design/p2d_normal_form_scout.py`](design/p2d_normal_form_scout.py)
authenticates the archived frame certificate and evaluates the proposed
majorant with exact rational arithmetic.  Its candidate bounds

\[
 E=3.265104260366031<4,\qquad
 h_{\rm in}=0.009256962067152971<1/64,\qquad
 \kappa_J=1.488562126122909<5/3
\]

pass, as do the fixed-schedule domain checks with
\(\overline B=2^{20}\), \(\varepsilon_{\rm nf}=2^{-22}\),
\(B_z=37/691200<1/16384\), and the required forward Lipschitz
amplification.  These are design evaluations of the then-Proposed theorem,
not a certificate and not, by themselves, a closed atom.  See the historical
[`P2D_NORMAL_FORM_DESIGN_REPORT.md`](P2D_NORMAL_FORM_DESIGN_REPORT.md).

The required all-orders result is now proved in
[`EXPLICIT_GLOBAL_MOSER_MAJORANT.md`](../../theory/EXPLICIT_GLOBAL_MOSER_MAJORANT.md).
Its second-Taylor-jet Banach-algebra recurrence gives explicit common domains,
two-sided analytic maps, an exact primitive with fixed gauge, and joint
state--parameter \(C^2\) tails.  The lightweight
[`check_p2d_normal_form_source_bounds.py`](check_p2d_normal_form_source_bounds.py)
authenticates the archived frame bytes and exact prefix, propagates the
outward-rounded source endpoints by exact rational arithmetic, and passes all
38 source-bound checks.  Together these give local mathematical `PASS` for
`V2.CHART.ANALYTIC_NORMAL_FORM`.  The proof contract
[`EXPLICIT_ZERO_ENERGY_FIBER.md`](../../theory/EXPLICIT_ZERO_ENERGY_FIBER.md)
and exact-rational checker
[`check_p2d_zero_energy.py`](check_p2d_zero_energy.py) now also give local
mathematical `PASS` for `V2.CHART.ZERO_ENERGY`, with the common interval
\(|\nu|\le25/2^{54}\), strict Krawczyk inclusion, orientation bound
\(\partial_{I_1}h>2/3\), and an all-finite-order Cauchy generator.  The proof
contract
[`EXPLICIT_EXACT_RADIAL_SECTIONS.md`](../../theory/EXPLICIT_EXACT_RADIAL_SECTIONS.md)
and checker [`check_p2d_exact_sections.py`](check_p2d_exact_sections.py)
then freeze \(\rho=5/2^{26}\), verify strict inclusion of both nonlinear
sections, fix their primitive gauges, and prove exact preservation of the
same signed \(I_2^{\rm K}=\nu\).  They give local mathematical `PASS` for
`V2.CHART.EXACT_SECTIONS`.  Finally,
[`EXPLICIT_WEIGHTED_KATO_PASSAGE.md`](../../theory/EXPLICIT_WEIGHTED_KATO_PASSAGE.md)
and [`check_p2d_weighted_passage.py`](check_p2d_weighted_passage.py) prove and
check the signed logarithmic time/phase law, absolute Kato deck, complete
parameter-two-jet bounds, all-finite-log-order generator, and clock inversion.
They give local mathematical `PASS` for `V2.CHART.WEIGHTED_PASSAGE`.  The
aggregate remains `INCONCLUSIVE` and `claim_bearing=false` because independent
replay is 1/2; physical slides, overlaps, and `V2.EXACT_CHART` remain `OPEN`.
The next mathematical gate is `V2.CHART.PHYSICAL_SLIDES`.  See
[`P2D_NORMAL_FORM_REPORT.md`](P2D_NORMAL_FORM_REPORT.md) and
[`P2D_ZERO_ENERGY_REPORT.md`](P2D_ZERO_ENERGY_REPORT.md), and
[`P2D_EXACT_SECTIONS_REPORT.md`](P2D_EXACT_SECTIONS_REPORT.md), and
[`P2D_WEIGHTED_PASSAGE_REPORT.md`](P2D_WEIGHTED_PASSAGE_REPORT.md).

Run the two design checks with

```bash
python3 -B validation/rigorous/audit_p2d_normal_form_exact.py
python3 -B validation/rigorous/design/p2d_normal_form_scout.py --pretty
python3 -m unittest \
  validation.rigorous.tests.test_p2d_normal_form_exact_audit \
  validation.rigorous.tests.test_p2d_normal_form_scout
```

Run the formal source-bound normal-form check with

```bash
python3 -B validation/rigorous/check_p2d_normal_form_source_bounds.py
python3 -B -m unittest \
  validation.rigorous.tests.test_p2d_normal_form_source_bounds -v
```

Run the zero-energy-fiber check with

```bash
python3 -B validation/rigorous/check_p2d_zero_energy.py
python3 -B -m unittest \
  validation.rigorous.tests.test_p2d_zero_energy -v
```

Run the exact-radial-sections check with

```bash
python3 -B validation/rigorous/check_p2d_exact_sections.py
python3 -B -m unittest \
  validation.rigorous.tests.test_p2d_exact_sections -v
```

Run the weighted-passage check with

```bash
python3 -B validation/rigorous/check_p2d_weighted_passage.py
python3 -B -m unittest \
  validation.rigorous.tests.test_p2d_weighted_passage -v
```

Check the archived certificate with

```bash
python3 -B validation/rigorous/p2d_frame_certificate.py check \
  validation/rigorous/results/vdp_bridge_v1_p2d_symplectic_frame.json
```

Build and check the lightweight local P2c certificate from a clean source
snapshot with

```bash
python3 validation/rigorous/p2_homoclinic_certificate.py build \
  validation/rigorous/results/vdp_bridge_v1_p2c_homoclinic.json
python3 validation/rigorous/check_certificate.py \
  validation/rigorous/results/vdp_bridge_v1_p2c_homoclinic.json
```

The builder does not rerun the 16,384-cell CAPD grid.  It verifies the four
archived log concatenations and performs the inexpensive exact tail audit.

## Frozen phase-1 box

[`config/vdp_box_v1.json`](config/vdp_box_v1.json) freezes

\[
 r\in[1/25,2/25],\qquad
 a_2\in[-1/4,1/4],\qquad
 \epsilon\in[4/5,6/5].
\]

The box was selected before interval validation from the already frozen
floating slices.  A failed or inconclusive validation must not rewrite it.
A changed box requires a new versioned file and an explicit reason.

## Frozen P2 comparison bridge

[`config/vdp_bridge_v1.json`](config/vdp_bridge_v1.json) freezes

\[
 r\in[0,2/25],\qquad
 a_2\in[-1/4,1/4],\qquad
 \epsilon\in[4/5,6/5].
\]

The `r=0` face is the desingularized selected core anchor.  It is not a
positive PDE parameter value.  A gap-free bridge is needed to prove that a
positive-parameter root is the continuation of the selected core branch,
rather than an unrelated root found only inside the target box.  The P2a
block and its acceptance gates are independently frozen in
[`config/vdp_p2_local_graph_v1.json`](config/vdp_p2_local_graph_v1.json).
The P2b0 center, \(C^0/C^1\) radii, symbolically differenced residual,
and acceptance margins were preregistered independently in
[`config/vdp_p2_h10_c01_v1.json`](config/vdp_p2_h10_c01_v1.json).  Freezing
that file was not itself a validation result; the later clean result is the
separately archived certificate cited above.
The P2b coefficient grid, norms, complete jet rectangle, state-tensor radii,
parameter normalization, and all acceptance gates are separately frozen in
[`config/vdp_p2_jets_v1.json`](config/vdp_p2_jets_v1.json).  The P2b kernel
uses the already archived P2a and P2b0 certificates as immutable
prerequisites; it does not reinterpret the H10 second or third derivatives as
true-graph bounds.
The P2bK Kato normalization, parameter grid, 28 interval gates, nine
true-source gates, source radius and admissible source multiindices are
independently frozen in
[`config/vdp_p2_kato_v1.json`](config/vdp_p2_kato_v1.json).  Its exact audit
proves the symbolic projector, Kato transport, frame-change, reverser and
source-circle identities before any interval outcome is known.  Its Python
executable and cache-free SymPy source tree form a separate P0 trust boundary:
their versions, executable hash, deterministic length-prefixed source-tree
digest, and file count are frozen in `dependency.lock.json`; `__pycache__`
and `.pyc` are excluded from the digest and bypassed at execution through a
fresh empty `PYTHONPYCACHEPREFIX`.  The interval probe then imports only the
immutable physical P2b jet upper endpoints from
the archived P2b certificate, and the checker independently recomputes the
declared composition recurrences.  This scope deliberately does not claim a
full rectangular fourth-order source jet, an orthonormal physical frame, or
the later full symplectic completion.

## Strict replay

Build the pinned CAPD source in a separate build directory using every flag
and CMake option in `dependency.lock.json`, including
`CMAKE_EXPORT_COMPILE_COMMANDS=ON`.  The runner rejects a mismatched source,
backend, compiler, build mode, or archive provenance, and scans every entry of
`compile_commands.json` for the mandatory and forbidden flags.  With
`CAPD_SOURCE`, `CAPD_BUILD`, and `FLAGSHIP_REPOSITORY` replaced by local paths,
the replay commands are:

```bash
python3 validation/rigorous/run_validation.py preflight \
  --allow-dirty \
  --capd-source CAPD_SOURCE \
  --capd-config CAPD_BUILD/bin/capd-config \
  --flagship-repository FLAGSHIP_REPOSITORY \
  --report /tmp/rfsn-vdp-rigorous-preflight.json

python3 validation/rigorous/run_validation.py kernel \
  --allow-dirty \
  --capd-source CAPD_SOURCE \
  --capd-config CAPD_BUILD/bin/capd-config \
  --flagship-repository FLAGSHIP_REPOSITORY \
  --report /tmp/rfsn-vdp-rigorous-kernel.json

python3 validation/rigorous/run_validation.py local-graph \
  --allow-dirty \
  --capd-source CAPD_SOURCE \
  --capd-config CAPD_BUILD/bin/capd-config \
  --flagship-repository FLAGSHIP_REPOSITORY \
  --report /tmp/rfsn-vdp-rigorous-p2a-local-graph.json

python3 validation/rigorous/run_validation.py h10-c01 \
  --allow-dirty \
  --capd-source CAPD_SOURCE \
  --capd-config CAPD_BUILD/bin/capd-config \
  --flagship-repository FLAGSHIP_REPOSITORY \
  --report /tmp/rfsn-vdp-rigorous-p2b-h10-c01.json

python3 validation/rigorous/run_validation.py p2-jets \
  --allow-dirty \
  --capd-source CAPD_SOURCE \
  --capd-config CAPD_BUILD/bin/capd-config \
  --flagship-repository FLAGSHIP_REPOSITORY \
  --report /tmp/rfsn-vdp-rigorous-p2b-jets.json

python3 validation/rigorous/run_validation.py p2-kato \
  --allow-dirty \
  --capd-source CAPD_SOURCE \
  --capd-config CAPD_BUILD/bin/capd-config \
  --flagship-repository FLAGSHIP_REPOSITORY \
  --report /tmp/rfsn-vdp-rigorous-p2b-kato.json

python3 validation/rigorous/check_certificate.py \
  /tmp/rfsn-vdp-rigorous-kernel.json

python3 validation/rigorous/check_certificate.py \
  /tmp/rfsn-vdp-rigorous-p2a-local-graph.json

python3 validation/rigorous/check_certificate.py \
  /tmp/rfsn-vdp-rigorous-p2b-h10-c01.json

python3 validation/rigorous/check_certificate.py \
  /tmp/rfsn-vdp-rigorous-p2b-jets.json

python3 validation/rigorous/check_certificate.py \
  /tmp/rfsn-vdp-rigorous-p2b-kato.json
```

Omit `--allow-dirty` for a clean replay.  A report path is observed only after
the source-dirty check and is explicitly excluded from that pre-write
observation in the certificate; the report is never a source input.  A dirty
development run cannot be release-eligible.

For a P2b jets or P2bK certificate, the checker also materializes the probe and
its local support files from the certificate's frozen source commit,
reconstructs the recorded strict compile command, reruns the exact frozen
argument vector, and compares stdout byte-for-byte.  For P2bK it additionally
replays the 56 exact symbolic checks and recursively validates the archived
P2b prerequisite.  This same-machine replay prevents coordinated edits of a
certificate's raw atomics, stored stdout, and stored stdout hash.  It is an
integrity check of one run, not the policy's second independent-machine
replay: a current-computer-only result still records one of two required
machines and remains non-claim-bearing.

The pinned GCC toolchain must compile both CAPD/FILIB and the probes with
`-fno-ipa-pure-const`.  Without it, GCC 15 interprocedural analysis can treat
CAPD's floating-environment-sensitive `DoubleRounding::test()` as pure and
eliminate calls across successive rounding-mode changes; the optimized
`DoubleRounding::isWorking()` then returns false even though separately called
mode probes report up/down/cut/nearest correctly.  The legacy self-test is a
mandatory test: such a build is `INCONCLUSIVE`, not silently accepted.

## Evidence boundary

A phase-1 kernel `mathematical_status: PASS` supports only:

- the exact V1 reversibility, anti-symplectic primitive, and Hamiltonian
  polynomial identities encoded by the source-only kernel; and
- the explicit V2(1) parameter inequalities and saddle-focus spectral gap on
  the frozen box.

A P2a local-graph `mathematical_status: PASS` additionally supports only:

- the nonsingular closed-form moving real eigenframe and strict local block
  faces/difference cone on the complete comparison bridge; and
- true reversible local stable/unstable graphs on the radius-`.01` disk with
  Lipschitz constant at most one, a quadratic value coefficient below `1/4`,
  and backward coordinate decay rate above `2/3`.

A P2b0 H10-centered `mathematical_status: PASS` additionally supports only:

- byte-identical regeneration and structural audit of the frozen degree-ten
  exact center and its exact invariance-defect term table; and
- the uniform bounds
  \(\lVert H_\mu-H_{10}\rVert_2\le5\times10^{-6}\) and
  \(\lVert DH_\mu-DH_{10}\rVert_F\le3\times10^{-4}\) on the complete
  comparison bridge, plus the reversible stable analogue.

A P2b jets `mathematical_status: PASS` additionally supports only:

- true-graph state derivative bounds through order three and the full
  rectangular parameter/mixed bounds through order two in the frozen norm;
- weighted unstable and reversible stable half-orbit jet bounds at weight
  `1/4`, in moving and physical coordinates; and
- the local parent `V2.WU_GRAPH`, conditional on the immutable P2a and P2b0
  prerequisite certificates.

A P2bK `mathematical_status: PASS` additionally supports only:

- exact normalized Riesz-projector and Kato-transport identities tied to the
  frozen flagship definitions, with the transported direction anchored at the
  selected core face;
- uniform value and first/second parameter bounds for the physical Kato frame
  and its change from the algebraic P2b frame; and
- the radius-`.01` true graph-boundary source and the nine frozen
  parameter/source derivatives obtained from the certified P2b graph jets.

Before a P2b jets pass, neither P2a nor P2b0 alone supplies those bounds.  In
particular, a bound on \(D^2H_{10}\) is a bound on the polynomial center, not
on \(D^2H_\mu\).

Even a P2bK pass does not assert that its physical frame is orthonormal, does
not supply the later symplectic completion, and does not validate the
positive-parameter homoclinic, exact saddle chart, event atlas, either
noncompact end, V5 matching, V6 component census, all winding numbers,
temporal stability, Turing selection, or canard identification.  Those
obligations are enumerated in `obligations.json`.
