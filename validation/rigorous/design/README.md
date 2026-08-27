# Rigorous-validation design scouts

Files in this directory are pre-registration design tools.  They may use
outward-rounded intervals to choose rational budgets, but their output is not
a validation certificate and does not discharge any obligation.

`p2b_jets_scout.cpp` evaluates the algebraic coefficient bounds and the
labelled-set Faà di Bruno recurrence proposed for the P2b mixed-jet
certificate.  Its default weight is (1/4); an alternative decimal weight
may be supplied only for sensitivity scouting.  The formal probe will accept
only the exact rational weight frozen in its versioned configuration.

The scout distinguishes two domains:

- the already-certified true-graph tube
  \(|u_1+H_{\mu,1}(u)|\le251/25000\), used for derivatives of the
  Lyapunov--Perron equation along the true half-orbit; and
- the radius-(1/100) source disk, used for the explicit block term.

It does not claim contraction of the nonlinear fixed-point map on a full
four-dimensional product ball.  The Neumann gate concerns only the
linearized Green operator along the true graph already supplied by P2a and
P2b0.

For an explicit parameter derivative with no (Z)-derivative slot, the
weighted bound uses (D_\theta^jR_\theta(0)=0) and the mean-value estimate

\[
 \|D_\theta^jR_\theta(Z)\|_\omega
 \le L_{1j}\|Z\|_\omega.
\]

An unweighted supremum of (D_\theta^jR_\theta(Z)) is reported only as a
diagnostic and is not inserted into the weighted recurrence.

Any formal use requires a separately committed frozen configuration, a clean
strict-source run, schema and semantic checking, and the repository's
independent-replay policy.

`p2b_kato_scout.cpp` evaluates the closed-form normalized-Kato phase on the
same normalized \(16\times8\times4\) bridge grid.  It reports design bounds
for the algebraic-to-Kato conformal change, the normalized first Kato vector
and oriented \((k_1,\mathfrak J_\mu k_1)\) frame, phase shift, and parameter
derivatives of the fixed-radius source circle.  The oriented physical frame
is not asserted to be orthonormal.  The scout also combines the archived P2b
physical half-orbit budgets with the Kato circle only for the total-order
three source-jet triangle; a full phase-three/parameter-two rectangle would
require unavailable fourth and fifth state derivatives of the true graph.
Its output selects rational gates only; the later formal kernel must
separately verify the exact Kato identities, the complete gap-free bridge,
the frozen P2b prerequisite, and the anchor-face phase convention.

`p2c_homoclinic_multishoot_scout.cpp` tests the selected symmetric
homoclinic shooting core using nine short segments and an event-reduced
Krawczyk map.  It preserves the zero-energy correlation between the two
stable graph coordinates instead of treating their errors independently.
Fixed-parameter strict tests pass at the core, the primary positive point,
and a 27-point target grid.  Its parameter-affine mode uses a joint interval
first jet and mean-value remainder for the nonlinear source.  Its
three-parameter mode retains common `r`, `a2`, and `epsilon` coordinates
throughout all nine segments while leaving the Newton system 38-dimensional.
Four closed
cells strictly cover \(a_2\in[-0.03125,0.03125]\) at
\((r,\epsilon)=(2/25,1)\), with all flow coefficients derived from the same
outward enclosure of the exact rational \(r\), and with local uniqueness and
endpoint transversality in every cell.  Its common-face mode maps the complete
Krawczyk root enclosure into the neighboring uniqueness box; all six
directional checks pass, so the four cells form one common slice branch.  This
is now supplemented by a gap-free exact-rational \(32\times128\times4\)
cover of the full bridge.  All 16,384 cells, all 44,416 internal common-face
identifications, and the strict frozen-core anchor pass.  The result therefore
identifies one locally unique selected root branch over the whole bridge.
The root is unique as a physical record represented in the resulting finite
parameter-following lifted 38-dimensional multiple-shooting tube; the scout
does not claim uniqueness for a direct trajectory whose intermediate nodes
leave that tube.  The `mu-grid-first-hit` and
`mu-grid-first-hit-slab` modes continue each Krawczyk root set through dense,
overlapping sign tubes.  On all 16,384 cells they prove, in order,
\(P>0\), \(Q>0\), \(P<0\), \(Q<0\), and a final outward \(U>0\)
event, with selected return time below \(1/5\).  Together with the P2a
true-graph exclusion before the source face, this is the complete first-hit
argument at design level.  The `mu-grid-root-jets` and
`mu-grid-root-jets-slab` modes then differentiate the actual 37-dimensional
true-source residual, rather than the fitted phase predictor.  On the same
16,384 cells they validate first and second normalized-parameter derivatives
of the selected root, phase, and half time through CAPD C2 flow/Poincare maps
and strict weighted Neumann solves.

`p2c_root_jet_summary_v1.json` records the binary64 upper endpoints and exact
run bindings consumed by the small `p2c_tail_composition_scout.py` algebraic
combiner.  The latter imports the archived P2b/P2bK half-orbit bounds, proves
the exact exponential comparison gates, and supplies

\[
 T_*=11,\qquad \eta=1/5,\qquad C_{\rm tail}=95434
\]

for all original-parameter derivatives through order two on both infinite
tails.  It uses exact rational arithmetic and performs no further ODE
integration.  These results close the infinite-tail atom at design level.

The `mu-grid-middle-jets` and `mu-grid-middle-jets-slab` modes use continuous
CAPD C2 flow enclosures, the actual selected-root jets, and the event-time
centering terms to bound derivatives at fixed spatial coordinate \(\xi\).
They pass on the full 16,384-cell bridge and close the design atom
`V2.HOM.MIDDLE_C2`: the compact middle \([-11,11]\), the local pre-source
pieces, and both infinite tails compose to

\[
 T_*=11,\qquad \eta=1/5,\qquad C_{\rm hom}=71496600
\]

for all original-parameter derivatives through order two on the full real
line.  This completes the strict P2c design run.  It does not produce the
frozen formal P2c certificate/checker, change `obligations.json`, provide
independent replay, or address temporal stability, Turing selection, or
canard identification.
The exact binary endpoints, worst-cell indices, run bindings, and rational
global composition are recorded in
[`p2c_middle_jet_summary_v1.json`](p2c_middle_jet_summary_v1.json).
Results and the proof boundary are recorded in
[`../P2C_SCOUT_REPORT.md`](../P2C_SCOUT_REPORT.md).  The H10 header supplied
at compile time must be extracted from the Git object named by
`flagship_import.lock.json`, never from the flagship working tree.
