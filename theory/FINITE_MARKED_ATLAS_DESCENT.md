# Finite marked-atlas descent and the global-marking question

**Provenance:** local proof-interface note relative to the frozen flagship
baseline.
**Evidence boundary:** the finite-atlas bridge below is a direct application of
the frozen marking-covariance results after the chartwise model hypotheses and
local return/coding modules have already been established.  It does not prove
those local modules.  The stronger global marked trivialization is **not
proved** by the present repository data.
**Upstream impact:** none. This note neither edits nor strengthens the frozen
flagship manuscript. Its local evidence status is governed by
[CLAIM_REGISTER.md](../CLAIM_REGISTER.md), and changes no flagship status.

## 1. The issue

The final positive parameter box used in V6 is

\[
 \mathcal P_{\rm V}
 =\left[\frac12r_{\rm V},r_{\rm V}\right]
   \times[-A,A]\times[\epsilon_-,\epsilon_+].
\tag{1}
\]

It is a compact contractible manifold with corners. As in V2, parameter
regularity on (1) means restriction of a family defined on an open
neighborhood of the box, so derivatives at its boundary faces have their
ordinary meaning.

The phase convention in
[CENTRAL_CONTINUATION.md](../van-der-pol/CENTRAL_CONTINUATION.md) supplies a
global \(C^2\) reversible symplectic eigenframe by normalized Kato transport,
a common transported source phase, and a proper phase arc with a positive cut
margin. Its local-passage theorem, however, states only that a **finite
parameter cover** carries \(C^2\) families of exact saddle charts and exact
incoming and outgoing action--angle coordinates. The passage estimates are
explicitly chartwise.

By contrast, a former draft of
[TWO_END_RETURN_EXIT_AND_PDE.md](../van-der-pol/TWO_END_RETURN_EXIT_AND_PDE.md)
used notation suggesting one family of coordinates

\[
 (\phi,\nu),\qquad
 \Sigma_\sigma=I_s^\circ\times\{0<\sigma\nu<\nu_N\},
\tag{2}
\]

one half-open angular lift, and one integer label \(n\) over all of (1). It
also wrote the mixed-\(C^2\) cross forms on one fixed pair of vertex
rectangles.  The current V6 text instead implements route 2 below.

There are two mathematically different ways to justify such notation.

1. Prove a global normalized exact saddle chart, global section coordinates,
   and a globally aligned angular cut on (1).
2. Keep the finite marked atlas, formulate all labels and cross forms
   chartwise, and descend only the physical first-event relation and its
   coordinate-invariant consequences.

The frozen flagship baseline proves the second route and explicitly does not
assume or conclude a global eigenframe, angle lift, or winding label for a
general intrinsic family. The van der Pol family has more global structure
than that general setting, but the current V2 proof does not carry out the
additional normalized analytic construction needed for the first route.

This note therefore proves the finite-atlas bridge, records the exact extra
hypothesis under which the global notation would become valid, and checks
which V6--V7 conclusions are unaffected.

## 2. Frozen baseline used here

The immutable source is the manuscript

    h-lu/reversible-rfsn-ii-waves
    commit d54add098545063d5efe8f1d6f062d4cfc116a0d
    papers/paper-a/manuscript/main.tex
    sha256 0baf6335aad72d5893479d8876d2613671ecb8ac2ccd73664405dea4381e6a20

Only the following coordinate-independent or marking-covariant statements are
used.

- Proposition prop:local-reversible-moser-passage gives parameter-local
  reversible exact saddle charts, exact section coordinates, weighted-log
  passage estimates, and degree-one transition maps on the oriented blow-up.
- Theorem thm:local-chart-production produces a finite parameter-local marked
  atlas from one physical intrinsic configuration.
- Definition def:compatible-marking-change states the overlap hypotheses:
  event-free section slides, exact gauges, exact symplectic oriented-blow-up
  transitions, and finite clean cut refinements.
- Theorem thm:change-of-marking identifies the physical return/first-event
  relation and corrected potentials under such changes. Winding labels on an
  overlap need agree only up to a bounded integer recoding.
- Corollary cor:physical-covariance descends a finite marked atlas to one
  physical first-event relation. It expressly retains only local full
  labelled shifts unless the stronger cut-avoidance comparison applies.

The bounded local import used by this repository is recorded in
[RETURN_EXIT_CODING_IMPORT.md](../van-der-pol/RETURN_EXIT_CODING_IMPORT.md).
No concrete flagship end compactification is used in this note.

## 3. What contractibility does and does not provide

Let \(E^u\to\mathcal P_{\rm V}\) be the oriented expanding real two-plane
bundle of the saddle-focus. Since (1) is contractible, \(E^u\) and its unit
circle bundle are topologically trivial. V2 does more: its Kato construction
already gives an explicit \(C^2\) oriented frame. Consequently:

- the phase-circle bundle has no monodromy over the parameter box;
- a degree-one family of boundary phase maps admits a parameter-continuous
  lift after one value is fixed; and
- a proper phase arc with a positive complementary gap can be cut and lifted
  to a family of ordinary intervals.

These facts remove a **topological** obstruction to global phase notation.
They do not select a unique nonlinear exact saddle chart. Even on one fixed
section with form \(d\phi\wedge d\nu\), the time-one Hamiltonian map generated
by

\[
 G(\phi,\nu)=\frac13a(\phi)\nu^3
\tag{3}
\]

is an exact symplectic germ which fixes the zero-action curve pointwise and
has the identity first jet there, but changes the nonlinear section
coordinates. Such gauges can depend \(C^2\) on the parameter. Thus a global
Kato frame and a global boundary phase do not, by themselves, make two local
exact Moser charts identical on their overlap.

This distinction is the reason that the flagship baseline treats a marked
presentation as extra coordinate data and proves covariance under changes of
marking instead of silently gluing all markings.

## 4. The proved bridge: finite marked-atlas descent

### Proposition 1 (physical descent from a finite marked atlas)

Assume the V1--V5A conclusions on the final box (1), and retain the V2 finite
cover

\[
 \mathcal P_{\rm V}=\bigcup_{i=1}^m V_i,
 \qquad V_i\Subset U_i,
\tag{4}
\]

with the following data on each \(U_i\).

1. There is a \(C^2\) family of reversible exact saddle charts, auxiliary
   incoming and outgoing radial sections, exact section coordinates
   \((\phi_i,\nu_i)\), and event-free slides to the fixed physical saddle
   faces.
2. The charts are tangent-normalized to the V2 Kato frame. Their transitions
   extend \(C^3\) to the oriented blow-up, have degree one on the phase
   boundary, preserve the signed zero-action faces, and have the mixed bounds
   stated in V2.
3. Every chart describes the same physical homoclinic tube, actual V3 pole
   aperture, actual V5 algebraic event, return faces, lateral faces, and fixed
   physical primitive. On overlaps these objects agree through the physical
   section maps.
4. The common transported phase arc and its cut have the positive V2 margin,
   and all overlap cut/event families satisfy the finite clean-intersection
   condition of the frozen admissible-marking theorem.
5. In each marked family, the model-specific H1--H2 conditions, the two
   terminal regularity packages, and the spare mixed derivative needed for
   finite-part composition have already been verified. Consequently the
   frozen local selector, first-exit, cross-form, exact-action, and coding
   modules apply on \(\overline V_i\), with an initial local threshold
   \(N_i^0\), a local width, an exhaustive local relation, a local full shift,
   and compatible mixed-\(C^2\) branch data.

The last item is an input to this descent proposition, not one of its
conclusions. Then there is a single intrinsic saddle-residence threshold
\(T_*>0\) such that:

1. every point of the fixed source collar with residence at least \(T_*\)
   lies above every applicable initial threshold \(N_i^0\);
2. the already constructed initial local partitions descend to one physical
   exhaustive first-event
   relation on the part of the fixed source collar whose physical saddle-block
   residence time is at least \(T_*\);
3. on an overlap, winding labels satisfy

   \[
    |n_j-n_i|\le K_{ij}
   \tag{5}
   \]

   on every connected component of a finite common refinement; the bound is
   uniform on the compact overlap;
4. return maps, roof and action functions, and terminal finite parts form a
   compatible atlas of mixed-\(C^2\) data. They need not be one globally
   labelled collection of functions on one fixed rectangle;
5. the physical trapped Poincaré system, every closed spatial period, and
   every closed action for the fixed physical primitive are independent of
   the marked chart; and
6. for each fixed \(\mu\in\mathcal P_{\rm V}\), any chart containing \(\mu\)
   supplies the V7 periodic, aperiodic, and finite-word homoclinic spatial
   orbits. Charts on an overlap describe the same physical orbits, possibly
   with recoded winding words, whenever the words lie above the corresponding
   local applicability thresholds.

After \(T_*\) and the finitely many overlap recoding bounds are fixed, the
displayed coding thresholds may be increased and the local widths decreased
so that every branch retained for V7 lies entirely in the residence-time
domain of item 2. This final truncation preserves all six conclusions; it
need not make the local integer origins identical.

#### Proof

By item 5, the local return, first-exit, cross-form, action, and coding
conclusions have already been constructed in every marked family. The exact
local passage relates winding to the physical
saddle-block residence time by

\[
 \left|n_i-\frac{\beta_\mu}{2\pi}
       \mathcal T_{{\rm sf},\mu}\right|\le C_i.
\tag{6}
\]

There are finitely many \(i\), while \(\beta_\mu\) is uniformly bounded above
and away from zero. A single \(T_*\) can consequently be chosen so that every
point with residence at least \(T_*\) lies beyond every \(N_i^0\). This
defines the common high-winding source collar without first choosing a global
integer label.

On \(U_i\cap U_j\), both marked families describe the same physical flow and
the same cooriented event germs. Their physical faces are related by the V2
event-free orbit slides. Because the physical primitive is fixed, a chart
primitive differs only by the exact local gauge induced by its exact
symplectic coordinate map; the slide and gauge endpoint functions have the
required mixed bounds on the compact sections. The oriented-blow-up
transition is degree one with the V2 \(C^3\) bounds. The proper-arc and clean
cut margins give the remaining admissible-marking hypotheses. Thus the
frozen change-of-marking theorem applies.

That theorem first intersects the two finite cut/event arrangements. On each
connected refined stratum the lifted angular transition has one constant deck
integer. Its periodic displacement is bounded on the compact overlap, which
gives (5). The same theorem identifies both local partitions with the same
physical first-event relation. Since the cover is finite, these pairwise
identifications satisfy the cocycle identity automatically: all of them are
induced by equality of the underlying physical orbit segments. The local
relations therefore descend to the physical relation in item 2.

For a finite branch, the variable-time identity

\[
 P^*\lambda-\lambda=dB+T\,dH
\tag{7}
\]

restricts on zero energy to the exact branch primitive. An event-free slide
or exact chart gauge changes \(B\) by endpoint terms. These telescope along a
finite path and around a closed orbit. At a noncompact end, V3 and V5A impose
the counterterm only after exact finite-cut composition; the same endpoint
calculation therefore survives the terminal limit. This proves items 4--5.

Finally fix \(\mu\) and choose any \(i\) with \(\mu\in V_i\). The local full
two-vertex graph and its cross-form contraction give all V7 orbit types in
that chart. On an overlap, marking covariance conjugates the physical
Poincaré maps, and the exact inverse PDE scaling is a physical coordinate
identity. Hence the resulting stationary PDE solution is independent of the
chosen marking. This proves item 6.

For the final-truncation statement, (6) and the uniform upper bound for
\(\beta_\mu\) imply

\[
 n_i\ge N^\sharp
 \quad\Longrightarrow\quad
 \mathcal T_{{\rm sf},\mu}
 \ge \frac{2\pi}{\sup\beta_\mu}(N^\sharp-C_i).
\]

Choose \(N^\sharp\) above every initial threshold and large enough that the
right side is at least \(T_*\), then shrink each punctured-section width to
retain only \(n_i\ge N^\sharp\). The bounded overlap recodings ensure that
the same physical orbit remains above the other chart's initial applicability
threshold after one further finite increase of \(N^\sharp\). Using the same
numerical lower bound does not align the local integer origins or make the
two truncated physical domains identical. \(\square\)

### Consequence for asymptotic formulas

Formula (5) does not alter the leading spatial-period slope. If, on one
overlap component, \(n_j=n_i+k\), then the same physical branch can be written
schematically as

\[
 c_{\rm wind}(\mu)n_i+L_i
 =c_{\rm wind}(\mu)n_j+L_j,
 \qquad
 c_{\rm wind}(\mu)=\frac{2\pi r}{\epsilon^{1/4}\beta_\mu},
 \qquad L_j=L_i-c_{\rm wind}(\mu)k,
\tag{8}
\]

with the corresponding section-slide correction included in \(L_j\).
Thus the coefficient of the large winding is intrinsic, whereas the bounded
constant and the raw integer origin are marked representatives. Closed
actions are unchanged because their endpoint coboundaries telescope.

## 5. A conditional criterion for the stronger global notation

### Proposition 2 (global marking, conditional)

The global notation (2) and one globally labelled full shift are justified if
the following additional data are supplied.

1. A \(C^2\) family over all of (1) of normalized reversible exact saddle
   charts on one common analytic domain, with the same normalization of every
   resonant Moser step.
2. One pair of global auxiliary radial sections and \(C^2\) event-free slides
   to the fixed physical faces. Transport of the auxiliary section
   coordinates through these slides gives global exact section coordinates
   whose zero-action curves and coorientations agree with the V2 physical
   traces.
3. A global lift of the boundary phase, aligned with the transported V2 phase,
   and one half-open cut avoided by all represented limiting residual-phase
   images by a positive margin.
4. On every old cover overlap, the newly supplied global coordinates agree
   with the local marked data by an admissible change whose deck recoding is
   fixed to zero. Equivalently, the local exact-chart cocycle has been
   explicitly trivialized in the normalized exact-symplectic gauge, not merely
   shown to be degree one on the boundary.

Under these assumptions, one may choose fixed \(I_s,\nu_N,N\), use one pair
of vertex rectangles, and index every branch globally by
\((\sigma,n,\sigma')\). All local mixed-\(C^2\) cross forms and terminal data
then are restrictions of one globally marked family.

#### Proof

The common chart and slides give one exact incoming/outgoing section pair.
The normalized saddle passage preserves the single transverse action exactly.
The global phase lift and its cut assign every punctured passage one sign and
one deck integer without overlap recoding. Compactness of (1) supplies a
common section width, a common rate gap, and a common maximum threshold.
Every local construction in Proposition 1 is therefore the restriction of
the same marked construction. Uniqueness of physical first-hit maps and of
the cross-form solution identifies the restrictions on overlaps. \(\square\)

Proposition 2 is a criterion, not a claim that its hypotheses have already
been verified.

## 6. Application audit for the van der Pol family

The current repository proves the following relevant facts.

| Requirement | Current evidence | Status |
|---|---|---|
| Compact parameter box with derivatives defined through its faces | V2 parameter convention and (1) | Verified |
| Trivial oriented eigenplane/phase-circle bundle | global V2 Kato frame | Verified |
| Common transported phase and proper cut gap | V2 phase convention and Theorem V2(5) | Verified |
| Finite \(C^2\) exact-chart cover with common weighted estimates | Theorem V2(3) | Verified |
| Physical overlap agreement of sections, event faces, and first-hit maps | Theorem V2(3)--(4) | Verified |
| Admissible degree-one oriented-blow-up transitions with bounded jets | V2 saddle-passage proof and frozen local theorem | Verified |
| One globally normalized analytic Moser chart on a common domain | not stated or proved in V2 | **Open interface** |
| Exact trivialization of the nonlinear chart cocycle, with zero deck recoding | not stated or proved in V2 | **Open interface** |

There is no evident topological obstruction to the two open items. A
plausible proof route would rerun the frozen normalized analytic Moser scheme
over the entire box using the global Kato frame, a fixed homological
projection, and a fixed normalized inverse, then prove common-radius
convergence and uniqueness on every old overlap. It would next transport the
resulting exact section coordinates through the V2 physical slides and align
the single angular cut. That argument is not present in the current files,
so it is not supplied here by assertion.

The **minimal unresolved step** is therefore analytic/gauge compatibility,
not the topology of the parameter box or of the phase circle bundle:

> Prove that the locally normalized exact saddle charts form a trivial
> \(C^2\) cocycle in a normalization which preserves the exact passage,
> physical section slides, and the chosen residual-phase cut.

Until that step is proved, Proposition 1 is the supported formulation.

## 7. Required wording of V6--V7 under the supported formulation

Without the extra global-marking lemma, the following distinctions must be
retained.

1. The coordinates \((\phi_i,\nu_i)\), final widths \(\nu_{N,i}\), cross forms,
   winding labels \(n_i\), and limiting sign-pair functions are chartwise
   representatives on a finite parameter atlas.
2. The globally defined object is the physical return/first-event relation on
   the intrinsic residence-time collar, not one globally labelled edge set.
3. Every local marking has a full two-vertex countable graph. On the common
   represented physical domain, the graphs describe the same physical
   Poincaré system; in general their words compare by bounded winding recoding
   and a finite realized-itinerary refinement.
4. Mixed-\(C^2\) parameter dependence means a compatible finite atlas of mixed
   two-jets. It does not mean that raw chart functions with different
   markings are literally equal.
5. For every fixed \(\mu\), all V7 periodic, aperiodic, and multipulse
   existence conclusions remain valid. The physical profiles, closed
   periods, and closed actions do not depend on the chosen local marking.
6. No parameter-global symbolic conjugacy with one immutable integer alphabet
   is asserted until Proposition 2 is discharged.

These corrections concern coordinate bookkeeping and the quantifiers of the
symbolic labels. They do not replace either positive end by a surrogate, do
not weaken the componentwise physical first-event census, and do not affect
the evidence boundary excluding temporal PDE stability, Turing selection, or
canard identification.
