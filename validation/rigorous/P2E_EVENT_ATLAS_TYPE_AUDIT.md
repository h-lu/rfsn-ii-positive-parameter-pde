# P2e event-atlas type and phase-interface audit

**Status:** application-owned schema `/3` correction and prospective
refreeze; no atlas atom is passed.  It supersedes the unmaterialized `/2`
phase interface at commit `4e2e3f0`.

The first structural gate treated all nine carrier domains as physical
zero-energy embeddings.  That is not the type of the focused theorem's
normalized source cells.  In the notation of the read-only focused paper,

\[
 Z_{\rm exit}=I_s\times[0,1],\qquad
 \Pi_{\sigma,\infty}:Z_{\rm exit}\longrightarrow B^u,
\]

and the restricted homoclinic cells are pullback domains for the return-band
functions.  They are compact manifolds with corners on which functions are
composed with prescribed maps.  They are not asserted to embed injectively in
the physical zero-energy hypersurface.  In particular, the limiting map may
lose rank in the physical image while its pulled-back scalar arrangement is
still the object used by the clean/neat isotopy argument.

The corrected application inventory therefore has two types.

1. `C.H`, `C.A`, `C.P`, `B.OUT`, and `B.RET` are physical carriers.  Their
   realizations are required to be zero-energy physical embeddings in
   `(U,P,V,Q)` on the full v2 bridge.
2. `Z.PLUS`, `Z.MINUS`, `Z.HOM.PLUS`, and `Z.HOM.MINUS` are normalized
   pullback domains.  They carry a certified map to `B.OUT` or `B.RET`; no
   physical-embedding, injectivity, or zero-energy claim is attached to the
   domain itself.

This distinction is forced by the types in the theorem and is not a weakening
of an atlas conclusion.  The physical first-event relation still lives on the
five physical carriers.  The four `Z` domains are used only to prove that the
limiting source-cell and homoclinic pullback arrangements have the required
clean/neat component census.

The P2d incoming and outgoing saddle sections are already bound physical
section objects.  They are not codimension-one boundary faces *inside* the
two-dimensional carriers `B.OUT` and `B.RET`.  The corrected P2e face
inventory therefore imports those sections through the P2d source binding and
does not duplicate them as carrier-boundary event functions.  The P2e face
records start with the three channel terminals, three lateral walls, four
aperture boundaries, and the stable cut.

## Corrected outgoing phase interface

The theorem compares the algebraic, homoclinic, and pole traces in the common
source phase \(\phi\) carried by the true P2bK source circle.  The exact P2d
outgoing section instead has coordinates \((\psi,\nu)\).  These markings are
related by the already proved orientation-preserving circle diffeomorphism

\[
 \phi=\kappa_\mu(\psi),\qquad
 \psi=\lambda_\mu(\phi)=\kappa_\mu^{-1}(\phi).
\]

They are not assumed to differ by a constant shift.  Thus the previous
structural version, which wrote `B.OUT` in \(\psi\) but inserted the direct
\(\phi\)-labels as aperture centers, did not define one typed object.  It was
discovered before any full atlas run and did not support an atlas claim.

We retain the P2d exact section and reparameterize only the outgoing carrier:

\[
 \mathcal E_{\mu}^{u,\mathrm{dir}}(\phi,\nu)
 =\mathcal E_{\mu}^{u,\mathrm{P2d}}
   (\lambda_\mu(\phi),\nu).
\]

For \(\nu\ne0\), \(\phi\) is the product extension of the boundary source
label along the P2d \(\nu\)-fibres; it is not asserted to equal the Euclidean
angle of the off-axis unstable coordinate.  Thus this definition needs only
the boundary map \(\lambda_\mu\), not a new two-variable angular inversion.

Consequently \(I_2^{\rm K}=\nu\) and its sign are unchanged.  In general,

\[
 (\mathcal E_{\mu}^{u,\mathrm{dir}})^*\omega
 =\partial_\phi\lambda_\mu(\phi)\,d\phi\wedge d\nu,
\]

so \((\phi,\nu)\) is a physical carrier chart, not a claimed standard
Darboux pair.  This is sufficient for the physical embeddings and event
arrangement in V2(4)--(5); the underlying exact \((\psi,\nu)\) chart remains
unchanged for V2(3), the local passage, and later cross-form arguments.

This reparameterization does **not** leave the physical embedding as a new
numerical prerequisite.  Put

\[
 F_\mu(\phi,\nu)=(\lambda_\mu(\phi),\nu).
\]

The P2d chart-overlap atom already proves that \(\lambda_\mu\) is the
parameter-dependent \(C^2\) inverse of an orientation-preserving circle
diffeomorphism, while the physical-slide atom proves that
\(\mathcal E_\mu^{u,\mathrm{P2d}}\) is a \(C^2\) zero-energy embedding.
Moreover the whole displayed band lies inside the proved P2d collar because

\[
 2^{-54}=\frac{16}{2^{58}}<\frac{25}{2^{58}}.
\]

Hence \(F_\mu\) is a \(C^2\) diffeomorphism on the frozen band and
\(\mathcal E_\mu^{u,\mathrm{dir}}
=\mathcal E_\mu^{u,\mathrm{P2d}}\circ F_\mu\) is automatically a \(C^2\)
zero-energy embedding.  This is an imported mathematical `PASS`; it does not
require a standalone 4096-cell table of \(\lambda_\mu\).  What remains
computationally open is narrower and different.  The proof-bound direct chart
in [`P2E_AXIS_CHART_REPORT.md`](P2E_AXIS_CHART_REPORT.md) now supplies a
rigorous exact zero-energy enclosure of the true \(\nu=0\) source curve.
The exterior ALG/POLE first-hit maps, rather than a numerical seam table or a
pointwise evaluator for the unknown graph, are the next new calculations.

The corrected outgoing band is

\[
 B^u:\quad 57/10\leq\phi_u\leq13/2,
 \qquad |\nu_u|\leq2^{-54}.
\]

It contains three protected phase collars.  Their centers and radii are

\[
\begin{array}{c|c|c}
\text{channel}&c_i&\text{protected radius}\\ \hline
\mathrm{alg}&\phi_{\rm a}^0&1/100\\
\mathrm{hom}&\phi_{\rm h}(\mu)&1/100\\
\mathrm{pole}&2\pi&3/20.
\end{array}
\]

Here \(\phi_{\rm a}^0\) is the fixed direct source label of the V2 finite-gate
anchor, while \(\phi_{\rm h}(\mu)\) is the selected P2c branch in the same
lift.  The strict
phase enclosures prove that the protected collar closures are uniformly
disjoint and lie inside one proper lifted phase arc.  The algebraic cut
\(e=(-U)^{-1}=23/400\) is both the frozen core finite gate and the section
later reused by V4/V5.  Its use in P2e does not assert that a
positive-parameter orbit already enters the algebraic infinite end.

The protected collars are not the flowbox entrance discs.  A direct scout at
\((r,a_2,\epsilon)=(3/200,0,1)\) shows that the homoclinic return is much more
sensitive in phase: offsets \(\pm10^{-7}\) still hit the radius-\(10^{-2}\)
incoming face with more than \(5.2\times10^{-3}\) sampled containment margin,
whereas larger exploratory offsets can leave that face.  After an additional
safety factor, freeze the entrance phase radii

\[
 R_{\rm a}^{\rm ent}=10^{-7},\qquad
 R_{\rm h}^{\rm ent}=10^{-8},\qquad
 R_{\rm p}^{\rm ent}=10^{-5},
\]

and the common action radius \(R_\nu^{\rm ent}=2^{-55}\).  These choices were
informed by a non-evidentiary scout; they are not certified margins.

The action radius in this frozen design is an available upper ceiling, not a
claim that the entire disc must have one certified event outcome.  The
axis-skeleton criterion proves that a complete strict \(\nu=0\) arrangement
with margin \(m_{\rm ax}>0\) persists on some uniform restriction
\(0<\delta_{\rm ent}\le2^{-55}\).  No numerical value of
\(\delta_{\rm ent}\), and in particular no equality
\(\delta_{\rm ent}=2^{-55}\), is asserted.

For each channel use normalized entrance coordinates \(x=(x_1,x_2)\) in
the corresponding direct-phase/exact-action disc on
\(\mathcal E_{\mu}^{u,\mathrm{dir}}\).  The algebraic internal label
\(w_{\rm alg}\) is a separate pulled-back scalar function and is not
identified with \(x_2\).  On the larger carrier cylinder

\[
 x_1^2+x_2^2\leq5/4,
 \qquad -1/8\leq t\leq9/8,
\]

take

\[
 g_i=t-1,
 \qquad
 h_i^{\rm side}=x_1^2+x_2^2-1+t/4.
\]

At the entrance, \(a_i=x_1^2+x_2^2-1\).  The side and terminal times are
\(4(1-x_1^2-x_2^2)\) and \(1\), hence

\[
 q_i=3-4(x_1^2+x_2^2).
\]

Thus \(q_i=0\) is a genuine side/terminal tie.  The active conormals of
\(g_i\) and \(h_i^{\rm side}\) are independent there, and priority selects
the physical terminal while retaining simultaneous incidence.  No fictitious
positive time gap is assigned.

The physical carrier maps are

\[
 \mathcal E_{i,\mu}(x,t)
 =\Phi_\mu^{t\tau_{i,\mu}(x)}\mathcal E^u_{i,\mu}(x),
\]

where \(\tau_{i,\mu}\) is the first hit of the P2d incoming face for `C.H`,
the finite cut \(e=23/400\) for `C.A`, or \(-U=10\) for `C.P`.  An equivalent
terminal-disc/backward-hit formulation may be preferable for interval
implementation.  The strict run must prove existence and uniqueness of every
hit, embedding and flow domain, event speed, containment, and disjointness;
the frozen formulas do not assume those inequalities.

The source-cell maps to `B.OUT` are displayed as
\((\kappa_\mu,\mathrm{id})\circ\Pi_{\sigma,\infty}^{\rm P2d}\).
This changes only their target coordinates.  `B.RET` remains in the exact
P2d incoming coordinates \((\psi_r,\nu_r)\).

## Consequence for the gate

The gate must accept a `PHYSICAL_ZERO_ENERGY_CARRIER` realization only for
the five physical carriers and a `NORMALIZED_PULLBACK_DOMAIN` realization
for the four `Z` domains.  A later full run may still be authorized only
after the zero-action exterior ALG/POLE first-hit maps, incidence/census,
normalization, numeric \(m_{\rm ax}\), and transported traces are
materialized.  The proved compactness criterion then supplies an existential
uniform exact-action subcollar; materializing the entire frozen design radius
is not a completion condition.  This audit by itself remains `INCONCLUSIVE`,
`claim_bearing=false`, and does not change the three already validated scalar
phase gaps.
