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

`p2d_symplectic_frame_scout.cpp` reuses the small interval `Jet2` algebra
from `p2b_kato_scout.cpp` without modifying that historical scout.  On the
same exact-rational \(16\times8\times4\) normalized bridge grid it evaluates
the closed forms for \(d,e,\kappa\), the selected positive half-angle branch,
its phase origin, and the physical blocks \(Y,X,L,L^{-1}\).  The JSON output
contains component hulls and complete normalized- and original-parameter
first/second jet summaries, together with deliberately broad rational gate
suggestions.  Original derivatives are converted componentwise using
\(D_{(r,a_2,\epsilon)}=\operatorname{diag}(25,4,5)D_\theta\), with the
corresponding product of scales on every Hessian entry.

The inverse is evaluated from the exact symplectic formula
\(L^{-1}=-\Omega_0L^T\Omega\), not by interval Gaussian elimination.
Reported symplectic, inverse, diagonalization, and reverser residuals are
dependency-prone interval diagnostics only, not identity evidence; the exact
evidence is `../audit_p2d_exact_chart.py`.  This scout does not construct the
nonlinear normal-form chart and cannot discharge
`V2.CHART.SYMPLECTIC_FRAME` or any other obligation.  Formal use still
requires a separately frozen configuration, strict probe, schema, semantic
checks, and repository-level provenance/replay work.  The conditioning
estimates derived from \(L-L_0\) use the elementary \(c=0\) orthogonality
identity for \(L_0\), now included in that exact audit.

`p2d_normal_form_scout.py` authenticates the archived P2d frame certificate
by its byte hash, certificate id, clean source commit, and local mathematical
`PASS` for `V2.CHART.SYMPLECTIC_FRAME`.  From its normalized component
intervals the script extracts conservative value and parameter-two-jet
bounds for \(\alpha,\beta\) and for \(p=L_{00}\), \(q=-L_{01}\).  Following
equations (5) and (11) of
[`EXPLICIT_GLOBAL_MOSER_MAJORANT.md`](../../../theory/EXPLICIT_GLOBAL_MOSER_MAJORANT.md),
it bounds the four complex coefficients of \(U\) by exact dyadic rational
upper enclosures of

\[
 4\sqrt{(p^2+q^2)/2}
\]

separately for the value and every normalized first and second parameter
derivative.  It then evaluates the theorem note's \(J^2\) bounds
\(E=\gamma_JU_J^3/3\),
\(h_{\rm in}=D_JU_J^4/E\), and the divisor factor \(\kappa_J\) term by term
from equation (17).  The only reported input gates are
\(E\le4\), \(h_{\rm in}\le1/64\), and \(\kappa_J\le5/3\).  The subsequent
schedule is fixed to \(\overline B=2^{20}\),
\(\varepsilon_{\rm nf}=2^{-22}\), \(\vartheta=1/4\).  In addition to the
domain checks of equations (38)--(39), the scout evaluates the forward
Lipschitz sum in (39a)--(39c), obtaining
\(B_z=37/691200<1/16384\) and \(A_z=(1-B_z)^{-1}\), and checks the amplified
forward displacement \(A_zS_0<\varepsilon_{\rm nf}/8\) from (40b).  For the
reported \(q=2\) coordinate tail, the inverse bound remains the raw (47)
sum while the forward bound is multiplied by \(A_z\), as required by
(47a).  It also checks (44a), so the physical inverse image lies inside the
fixed source domain on which the proposed primitive is asserted.  The script
does not introduce a competing recurrence or schedule.
Hexadecimal interval endpoints are combined as exact rational numbers, but
this remains a numerical design evaluation of a proposed theorem, not its
proof or an outward-rounded formal run.  In the complex-coordinate
metadata, \(z\) comes from \(x\), \(w\) comes from \(y\), and
\(\{z_j,w_k\}=-\delta_{jk}\).  The output is always non-claim-bearing,
leaves `V2.CHART.ANALYTIC_NORMAL_FORM` and `V2.EXACT_CHART` open, and creates
no certificate or replay layer.

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
line.  This completes the strict P2c design run.  The separate retrospective
local certificate lane archives and parses the four fixed-order log snapshots
in [`logs/`](logs/) and reruns the exact tail algebra; it does not rerun this
full grid.  Neither the design modes nor that local certificate provide
independent replay or address temporal stability, Turing selection, or canard
identification.
The exact binary endpoints, worst-cell indices, run bindings, and rational
global composition are recorded in
[`p2c_middle_jet_summary_v1.json`](p2c_middle_jet_summary_v1.json).
Results and the proof boundary are recorded in
[`../P2C_SCOUT_REPORT.md`](../P2C_SCOUT_REPORT.md).  The H10 header supplied
at compile time must be extracted from the Git object named by
`flagship_import.lock.json`, never from the flagship working tree.

`p2e_axis_terminal_first_hit_scout.cpp` and the two axis-cover runners form
the design lane for the zero-action algebraic and pole entrances.  The
terminal kernel starts from the exact zero-energy axis chart.  For the pole
channel it uses directed \((U,P,Q,V)\) sections through the bounded global
turn and supports three complementary interval representations of the same
orbit and terminal event.  The base route uses only the frozen event
sections.  A light fallback adds exact \(V=1/2,3/4,4/5\) sections after the
final \(P=0\) maximum.  The strongest fallback reconditions the exact
zero-energy image at the upward \(U=-1/20\) hit, uses \(U\) as independent
variable through the long upper turn while checking \(P>0\) on every CAPD
step, and then uses \(V\) as independent variable from \(V=0\) to \(V=4/5\)
while checking \(Q>0\).  From the first downward \(U=-1/20\) hit, a separate
guard takes the
first \(P=0\) minimum, the next \(P=0\) maximum, and the first subsequent
\(U=-1/5\) hit.  At \(x=-U=1/5\), the kernel verifies a forward-invariant
positive \((y,D,K)\) cone, which makes \(x\) strictly increasing through
\(x=10\).  The phase aperture covers the retained disk on its zero-action
axis; it is not a claim about a larger rectangular carrier.

For the algebraic channel the physical enclosure is reconditioned at its
first \(U=-4\) hit.  With

\[
 e=\frac14-\tau=-\frac1U,\qquad
 w=(P e^{3/2})^2,\qquad q=Qe^{3/2},
\]

the kernel integrates the exact weighted \((w,q)\) dynamics, carries only
the three static parameters and physical clock, and checks \(w>0\) on every
accepted CAPD step through \(e=23/400\).  The negative branch
\(P=-\sqrt w/e^{3/2}\) and \(dU/d\tau=-e^{-2}<0\) then identify
\(U=-400/23\) as the first post-seam terminal hit.  The terminal \(V\) is
reconstructed from the zero-energy identity; a dependency-prone numerical
energy interval is diagnostic only.

The pole runner first tries the full proved
\(|\eta|\le1/200000\) graph tube on each frozen bridge cell.  It refines only
wrapping failures into the eight canonical \(r\)-leaves and invokes the
root-conditioned true-\(W^u\) source trace only when the broad leaf still
wraps.  Any further \(r\)-bisections of a root-conditioned canonical leaf
are checked as an exact binary-prefix cover; phase is never split, so every
accepted record covers the complete retained phase aperture.  The algebraic
runner uses the same root-conditioned source binding
and adaptively bisects only failed \(a_2\) leaves; accepted leaves must form
an exact binary-prefix cover.

These remain non-claim-bearing design computations.  Even complete axis
covers do not supply the off-axis event carrier, incidence census, numerical
\(m_{\rm ax}\), transported traces, or `V2.EVENT_ATLAS`.
