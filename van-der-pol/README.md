# van der Pol: positive-parameter two-end exact-action application

## Stationary spatial Hamiltonian

For

\[
u_t=v-f(u)+d u_{xx},\qquad
v_t=\epsilon(a-u)+v_{xx},\qquad
f(u)=\frac13u^3-u,
\]

put \(\delta=\sqrt d\), \(y=x/\delta\), and set

\[
u_y=p,\quad p_y=f(u)-v,\quad
v_y=\delta q,\quad q_y=\epsilon\delta(u-a).
\]

Writing \(F'(u)=f(u)\), the candidate first integral and primitive are

\[
\mathcal G_\delta
=\frac12(\epsilon p^2-q^2)
-\epsilon\bigl(F(u)+(a-u)v\bigr),
\]

\[
\lambda_\delta=\epsilon p\,du-\delta^{-1}q\,dv.
\]

All signs and the Hamiltonian convention are checked directly in
[HAMILTONIAN_CHECK.md](HAMILTONIAN_CHECK.md).  The reverser is
\((u,p,v,q)\mapsto(u,-p,v,-q)\).  A rescaled momentum choice may be used to make
the primitive independent of \(\delta\), provided all clocks and action
integrals are transformed explicitly.

## Completed central and two-end local foundations

The precise PDE parameters, all spatial clocks, the published \(K_1,K_2\)
charts, the equilibrium-energy subtraction, and the exact conjugacy to the
flagship core are frozen in
[MODEL_AND_CENTRAL_CHART.md](MODEL_AND_CENTRAL_CHART.md).  The base
homoclinic and compact source/event package are imported, with immutable
hashes and explicit exclusions, in
[CENTRAL_CORE_IMPORT.md](CENTRAL_CORE_IMPORT.md).

[Theorem V2](CENTRAL_CONTINUATION.md) proves on a nonempty cusp wedge:

- a uniform saddle-focus and \(C^2\) local invariant manifolds;
- a selected symmetric homoclinic with two-derivative weighted tails and
  transversality inside the regular zero-energy surface;
- reversible exact local passage with the correct weighted-log parameter
  estimates; and
- continuation of the complete compact labelled first-hit arrangement,
  source phases, and strict ordering margins.

At the end of V2, the two labels are only finite algebraic-directed and
pole-directed **gates**.  [Theorem V3](POSITIVE_POLE_FINITE_PART.md) upgrades
the latter, on a nonempty compact positive subbox of the V2 wedge, to a
genuine positive-parameter pole.  It proves:

- a uniform first hit from a nonempty transported source phase window into
  an exact forward-invariant pole cone;
- finite physical-distance blow-up and entry into the local pole basin;
- the normally hyperbolic regular-singular boundary, complete indicial and
  resonant expansion, and mixed two-derivative end coordinates; and
- the finite Laurent--log action subtraction in fixed physical remaining
  distance, including coordinate uniqueness and exact moving-cut additivity.

V6, Section 3.2 and Lemma V6.1 record the two extra interfaces actually
needed later: the source-trace identity from the V3 one-dimensional window
to the V6 two-dimensional aperture, and one spare entry derivative for
terminal composition.  Both come from the full positive-parameter equations,
not an isolated boundary-sink theorem.

[Theorem V4](OUTER_FUTURE_STAYING.md) independently constructs that outer
end from the full positive-parameter physical system.  In the exact
compactification \(z=1/u\), its maximal forward-staying set is a unique
codimension-one graph.  It is normally expanding, third-order bunched in
intrinsic quotient norms, has mixed-total-three regularity with two external
parameter derivatives, and reaches \(u=+\infty\) only at infinite physical
spatial distance.  [Theorem V5](CENTRAL_OUTER_MATCHING.md) now attaches the
V2 finite gate through \(K_2\) and \(K_1\) to that same graph.  It proves the
future-staying physical tube, endpoint-anchored adjoint and nonzero exchange
coefficient, uniformly invertible matching operator, two external parameter
derivatives, and exact covariance of every finite truncated action under a
moving matching cut.  Its auxiliary saddle-type center graph now uses the
[local relative overflowing NHIM theorem](../theory/RELATIVE_OVERFLOWING_NHIM.md),
and its final annulus is selected before V3--V4 are rerun.  Thus the
algebraic-directed label is a genuine matched
outer exit; V5 deliberately leaves its infinite-end action renormalization
as the next theorem.

[Theorem V5A](OUTER_ALGEBRAIC_FINITE_PART.md) completes that
renormalization.  In the common physical coordinate
\(Q=z^{-2}\), it selects a reference orbit at a fixed outer cut, proves
exponentially flat same-\(Q\) shadowing with two parameter derivatives, and
subtracts the reference orbit's complete physical length and action tails.
The resulting finite parts have mixed two-jets, are covariant under
admissible section, compactification, reference, and exact-gauge changes,
compose strictly with every finite V5 branch, and contain the V5 arrival
labels with a proved scaled-coordinate margin.

[Theorems V6--V7](TWO_END_RETURN_EXIT_AND_PDE.md) complete the physical
obligation on a finite compatible marked atlas.  In every marking they pull
every actual end, return, cut, and lateral face through the same limiting
template; verify clean/neat incidences, first-hit margins, and a component
census with no residual cell; attach both finite parts to the exact branch
cocycle; and translate the recurrent and finite-word codes to stationary PDE
patterns.  The
[compact-family first-hit theorem](../theory/COMPACT_FAMILY_FIRST_HIT_THEOREM.md)
supplies the coverwise rate and relative whole-cell persistence used in this
step, conditional on the fixed finite V2 event arrangement and its complete
event-time-difference list.  V6 keeps that physical block, subdivides the
algebraic carrier, and replaces the protected pole gate by the partitioned
V3 \(x=10\) carrier.  The
[finite-atlas descent theorem](../theory/FINITE_MARKED_ATLAS_DESCENT.md)
identifies the physical first-event relation, trapped system, periods, and
closed actions on overlaps.  Conditional on the frozen modules, V6 constructs
every chartwise presentation required for that descent, and its final coding
truncation lies inside the common physical residence-time domain.  Raw
winding labels remain local and may undergo a bounded recoding.  The
high-winding, action-gluing, and coding
inputs
used in that proof are frozen, with their model-specific exclusions, in
[RETURN_EXIT_CODING_IMPORT.md](RETURN_EXIT_CODING_IMPORT.md).

The arrow-by-arrow publication audit, including the remaining external
evidence-accessibility blocker, is
[`VDP_PUBLICATION_PROOF_AUDIT_2026-08-28.md`](../proof-audit/VDP_PUBLICATION_PROOF_AUDIT_2026-08-28.md).

## Completed principal theorem

For some \(r_{\rm V}>0\), \(A>0\), and
\(0<\epsilon_-<\epsilon_+\), the completed theorem works on the nonempty
compact positive annular box

\[
 r\in[\tfrac12r_{\rm V},r_{\rm V}],\qquad
 a_2\in[-A,A],\qquad
 \epsilon\in[\epsilon_-,\epsilon_+],
\]

with \(d=r^4\), \(\delta=r^2\), and
\(a=1+\sqrt\epsilon\,r^3a_2\).  Theorem V6 proves the exhaustive
physical high-winding first-return/first-exit relation, including the outer algebraic
exit, finite-distance pole exit, uniform mixed-parameter spatial-length and
action asymptotics, compatible finite parts, and exact branch composition.
Theorem V7 proves, in every local marking, the periodic, multipulse, and
aperiodic stationary spatial PDE patterns supported by the physical relation
actually established in V6; the profiles and closed observables agree on
overlaps.  This is an
existence theorem on a fixed positive subbox; it does not claim one uniform
two-end arrangement for every \(0<\delta\le\delta_0\), nor one global exact
saddle chart or immutable winding alphabet over the parameter box.

## Completed decisive theorem: central-to-outer matching

The first issue is not the local saddle passage.  It is the construction and
matching of the positive-parameter outer future-staying invariant hypersurface
through

\[
K_2\longrightarrow K_1\longrightarrow \text{outer chart}.
\]

A successful theorem must supply:

- common physical matching sections and unambiguous chart transitions;
- a normally expanding, third-order-bunched outer invariant hypersurface;
- an endpoint-anchored adjoint row and nonzero exchange coefficient;
- a uniformly invertible finite-dimensional matching operator;
- two derivatives in the external parameters without hidden trace loss;
- covariance of truncated Hamiltonian action under moving the matching cut.

These requirements are discharged by
[Theorem V5](CENTRAL_OUTER_MATCHING.md).  That theorem deliberately stops
before choosing counterterms at \(z=0\).

## Positive-parameter ends

The zero-parameter end models cannot be imported by ordinary persistence.  At
positive \(\delta\), the pole has a different dominant balance and the
algebraic channel passes to an outer slow regime.  Candidate compactifications,
indicial spectra, clock weights, and action orders must therefore be derived
and proved afresh.

The positive pole calculation and its action renormalization are proved in
[Theorem V3](POSITIVE_POLE_FINITE_PART.md) on the fixed positive compact box
that later stages must retain.  The outer compactification and its invariant
hypersurface are proved in [Theorem V4](OUTER_FUTURE_STAYING.md) on that same
box, and the central--outer matching is proved in
[Theorem V5](CENTRAL_OUTER_MATCHING.md).  The algebraic physical-length and
action finite parts are proved in
[Theorem V5A](OUTER_ALGEBRAIC_FINITE_PART.md), including exact outer
weights, two parameter derivatives, and coordinate, cut, and
exact-coboundary covariance.  Both positive-parameter local ends and their
action normalizations are used in the completed V6 first-event and
exact-action assembly.

## Fallback theorem

If the outer algebraic matching is genuinely obstructed, replace that end by a
fixed intermediate-chart or canard exit section.  The fallback target is then
an exhaustive finite-cut return/exit/pole theorem with exact finite-branch
action and stationary PDE patterns.  It must not be described as a two-end
finite-part theorem.  The fallback was not invoked: V4--V6 establish the
genuine outer algebraic end and its finite part.

## Interpretation boundary

Periodic or localized spatial orbits are stationary solutions of the original
PDE.  Spatial symbolic dynamics and spatial entropy do not imply temporal
chaos, and existence does not imply temporal stability.

The first post-existence temporal result is now isolated in
[the A2 co-periodic instability note](A2_PERIODIC_SPECTRAL_INSTABILITY.md).
It proves a general centered-moment criterion for a real positive temporal
eigenvalue.  The frozen A2 arrays pass that criterion numerically with
\(M_{0.01}\approx-8.83\times10^{-7}\), consistently with the independent
Fourier candidate \(\lambda\approx0.02138145\).  A target-specific
[CAPD enclosure](../validation/a2_periodic/README.md) now proves a true periodic
orbit in the frozen shooting box and the strict interval moment, hence a real
co-periodic eigenvalue \(\lambda_*\in(0.01,2)\).  This is a local mathematical
`PASS`; independent replay remains before claim-bearing release.  It supplies
neither nonlinear instability nor temporal selection.
