# Research contract

## Objective

Establish a genuine positive-parameter PDE application of the RFSN-II
spatial-dynamics mechanism while treating the existing flagship manuscript as
a read-only, revision-pinned source.  When the application exposes a missing
abstract lemma or an unnecessarily narrow abstract formulation, state and
prove the required amendment in this repository.  Such a result belongs to
this repository only and does not alter the flagship manuscript or its claim
status.

The programme has one local theory layer and two model tracks.

### Track T: local abstract amendments

Maintain the exact boundary between the frozen RFSN-II inputs and abstract
results proved here.  The first seam obligations are:

1. a parameter-dependent relative overflowing invariant-manifold result with
   the boundary, regularity, uniformity, and local-uniqueness clauses actually
   used at the resolved \(K_1\) corner; and
2. a precise marked-coordinate interface from V2 to V6.  The default route is
   descent from the finite compatible marked atlas already supplied by the
   frozen source.  A single global angle/action chart may be used only if a
   separate globalization criterion is proved for this parameter family.

The provenance and status rules for this layer are fixed in
[`theory/`](theory/README.md).  A local abstract theorem is not an upstream
edit and must not be attributed to the flagship baseline.

### Track B: Brusselator localized stationary pattern

For the classical Brusselator with positive diffusion, prove the existence of
a symmetric homoclinic orbit of the stationary spatial system, lying in the
positive-concentration region, for every sufficiently small value of the
singular diffusion parameter.  Translate the orbit back to a localized
stationary PDE solution and prove its amplitude and width scales.

This track does **not** claim an exact-action identity.  The positive-parameter
four-dimensional stationary system is reversible and volume preserving, but
the cited model analysis supplies no conserved Hamiltonian of the type required
by the flagship theorem.

### Track V: van der Pol two-end exact-action theorem

For the van der Pol reaction--diffusion system, prove for a nonempty positive
parameter range that:

1. the stationary spatial system is a reversible exact Hamiltonian system;
2. the saddle-focus and transverse homoclinic structure persist;
3. all sufficiently high-winding initial conditions in a fixed source cell are
   exhausted by first return or a labelled first exit;
4. the positive-parameter pole and outer algebraic ends admit the required
   compactifications and action finite parts;
5. flight length and physical Hamiltonian action have uniform mixed-parameter
   asymptotics and obey exact branch composition;
6. bounded symbolic itineraries yield stationary spatial PDE patterns.

The first decisive problem is the central-to-outer matching

\[
K_2\longrightarrow K_1\longrightarrow \text{outer slow invariant manifold}.
\]

The proof must establish a common physical matching section, a nonzero exchange
coefficient, a uniformly invertible finite-dimensional matching operator,
two parameter derivatives, and covariance of the truncated action under a
change of cut.

## Proof order

### Local theory layer

1. Freeze the exact flagship revision and the imported theorem clauses.
2. State each locally needed abstract amendment independently of the van der
   Pol formulas, with its full boundary and parameter hypotheses.
3. Prove the amendment or retain it as Proposed; do not repair a missing
   implication by strengthening prose in the application.
4. Give a clause-by-clause application map before using the result in V2--V7.
5. Use finite compatible marked charts unless a global marked trivialization
   has itself been proved.

### Brusselator

1. Derive the positive-parameter stationary system and blow-up coordinates.
2. State the transverse symmetric core homoclinic result being imported.
3. Prove parameter-dependent stable/unstable manifolds with uniform exponential
   tails in a weighted space.
4. Apply the implicit-function theorem to the reversible matching problem.
5. Rescale to the original PDE, prove positivity, localization, and the stated
   amplitude/width estimates.
6. Only then consider fixed finite-winding or multipulse continuations.

### van der Pol

1. Freeze the PDE, parameter wedge, scales, exact primitive, energy level,
   physical spatial variable, and desingularized clocks.
2. Prove the central-chart persistence of the saddle-focus, transverse
   homoclinic, compact first-hit geometry, and source-phase margins.
3. Construct the positive-parameter pole compactification and prove its
   indicial and action orders rather than importing the singular-core values.
4. Construct the outer algebraic compactification and its normally expanding,
   third-order-bunched future-staying invariant hypersurface.
5. Prove the \(K_2\)--\(K_1\)--outer matching theorem.
6. Prove the algebraic finite-part theorem for the new clock and action weights.
7. Pull both end targets back to the source and prove clean first-hit
   stratification, ordering margins, and absence of unlabelled components.
8. Apply the return--first-exit mechanism and translate the resulting bounded
   spatial orbits to stationary PDE patterns.
9. Select a fixed positive-parameter box for rigorous numerical verification
   only after the analytic hypotheses and observables have been frozen.

## Completion criteria

Track T is complete for a particular seam only when the abstract statement,
proof, frozen-source boundary, and model-specific hypothesis map all appear in
this repository.  A theorem name, a generic citation to normal hyperbolicity,
or a numerical example does not discharge an abstract seam.

Track B is complete only when the theorem is stated in original PDE variables,
all small-parameter quantifiers are explicit, the orbit is proved homoclinic in
the full positive-parameter system, both concentrations are positive, and the
proof contains uniform tail estimates.  Simulations alone are insufficient.

Track V is complete only when the two positive-parameter ends, their matching,
the exhaustive first-event relation, and both action finite parts are proved in
one consistent parameter class.  A finite outer cut is not a two-end theorem.

## Honest fallback results

If the van der Pol outer algebraic matching fails, the admissible fallback is a
finite-cut theorem: replace the outer algebraic end by a fixed canard or
intermediate-chart exit section, while retaining the transverse homoclinic,
exhaustive return/finite-exit/pole census, and exact finite-branch action.  Such
a result must be titled and stated as finite-cut, not two-end.

If the Brusselator symmetric matching determinant loses transversality, the
claim is reduced to the parameter subrange where a nonzero determinant is
proved.  The parameter interval may not be moved after looking at a failed
rigorous validation merely to obtain a positive result.

## Stopping conditions

The full van der Pol two-end route is genuinely blocked if, after testing the
stated directed matching construction and one mathematically justified
redesign, at least one of the following is proved unavoidable:

- no normally expanding outer future-staying hypersurface exists in the chosen
  physical channel;
- the exchange coefficient vanishes structurally;
- every admissible matching formulation has an unbounded trace or inverse in
  the required parameter-uniform norm;
- the pulled-back algebraic and pole event windows cannot remain disjoint with
  positive first-hit margins;
- the renormalized action cannot be made compatible across matching cuts.

A difficult estimate, a failed implementation, or a single inconclusive
numerical run is not by itself a mathematical obstruction.

## Explicit nonclaims

The first-stage projects do not claim:

- temporal spectral or nonlinear stability of the stationary PDE patterns;
- that a stationary spatial entropy is temporal chaos;
- experimental observation or material-parameter calibration;
- that Hamiltonian action is a chemical free energy;
- a global phase-space partition outside the fixed source cell;
- a positive-parameter Brusselator exact-action theorem.
- incorporation of any local abstract amendment into the read-only flagship
  manuscript.

Temporal stability requires a separate Bloch/Evans and nonlinear-semigroup
analysis.  Experimental validation requires a specified physical system,
dimensional parameter map, measurement protocol, and data.
