# P2e event-atlas type audit and corrected minimal realization

**Status:** application-owned design correction; no atlas atom is passed.

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

## Minimal physical realization to freeze

Use transported Kato phase and exact signed action on the P2d physical
outgoing and incoming faces.  The wide band

\[
 B^u:\quad 57/10\leq\psi_u\leq13/2,
 \qquad |\nu_u|\leq2^{-54}
\]

contains three protected phase collars.  Their centers and radii are

\[
\begin{array}{c|c|c}
\text{channel}&c_i&\text{protected radius}\\ \hline
\mathrm{alg}&\phi_{\rm a}^0&1/100\\
\mathrm{hom}&\phi_{\rm h}(\mu)&1/100\\
\mathrm{pole}&2\pi&3/20.
\end{array}
\]

Here \(\phi_{\rm a}^0\) is the fixed transported label of the V2 finite-gate
anchor, while \(\phi_{\rm h}(\mu)\) is the selected P2c branch.  The strict
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

For each channel use normalized entrance coordinates \(x=(x_1,x_2)\) in
the corresponding phase--action disc.  The algebraic internal label
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

## Consequence for the gate

The gate must accept a `PHYSICAL_ZERO_ENERGY_CARRIER` realization only for
the five physical carriers and a `NORMALIZED_PULLBACK_DOMAIN` realization
for the four `Z` domains.  A later full run may still be authorized only
after the frozen physical faces and carrier maps have interval certificates,
and after incidence/census, normalization, numeric \(m_0\), and transported
traces are materialized.  The numerical budgets are already prospectively
frozen.  This audit by itself remains `INCONCLUSIVE`,
`claim_bearing=false`, and does not change the three already validated scalar
phase gaps.
