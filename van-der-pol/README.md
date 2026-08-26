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

[Theorem V4](OUTER_FUTURE_STAYING.md) independently constructs that outer
end from the full positive-parameter physical system.  In the exact
compactification \(z=1/u\), its maximal forward-staying set is a unique
codimension-one graph.  It is normally expanding, third-order bunched in
intrinsic quotient norms, has mixed-total-three regularity with two external
parameter derivatives, and reaches \(u=+\infty\) only at infinite physical
spatial distance.  [Theorem V5](CENTRAL_OUTER_MATCHING.md) now attaches the
V2 finite gate through \(K_2\) and \(K_1\) to that same graph.  It proves the
global future-staying tube, endpoint-anchored adjoint and nonzero exchange
coefficient, uniformly invertible matching operator, two external parameter
derivatives, and exact covariance of every finite truncated action under a
moving matching cut.  Thus the algebraic-directed label is a genuine matched
outer exit; only its infinite-end action renormalization remains to be built.

## Principal theorem target

For a fixed compact range of \(\epsilon>0\) and a nonempty RFSN-II parameter
wedge with \(0<\delta\leq\delta_0\), prove an exhaustive high-winding
first-return/first-exit theorem for the stationary spatial Hamiltonian.  The
theorem must include the outer algebraic exit and finite-time pole exit,
uniform mixed-parameter asymptotics for physical spatial length and action,
compatible finite parts at both ends, exact branch composition, and the
stationary PDE patterns produced by bounded codes.

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
[Theorem V5](CENTRAL_OUTER_MATCHING.md).  The remaining local end theorem is
the algebraic action finite part: it must identify the exact outer clock and
action density, prove the renormalized limit with two parameter derivatives,
and establish coordinate, cut, and exact-coboundary covariance.

## Fallback theorem

If the outer algebraic matching is genuinely obstructed, replace that end by a
fixed intermediate-chart or canard exit section.  The fallback target is then
an exhaustive finite-cut return/exit/pole theorem with exact finite-branch
action and stationary PDE patterns.  It must not be described as a two-end
finite-part theorem.

## Interpretation boundary

Periodic or localized spatial orbits are stationary solutions of the original
PDE.  Spatial symbolic dynamics and spatial entropy do not imply temporal
chaos, and existence does not imply temporal stability.
