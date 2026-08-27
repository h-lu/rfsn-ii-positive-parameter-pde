# Relative overflowing saddle NHIMs on a manifold with corners

**Provenance:** LOCAL-AMENDMENT in this repository. This note does not alter
the frozen flagship baseline identified in [BASELINE.md](BASELINE.md).

**Role:** supporting analytic lemma for the auxiliary center graph in the
resolved \(K_1\) corner of
[CENTRAL_OUTER_MATCHING.md](../van-der-pol/CENTRAL_OUTER_MATCHING.md). It is
not the codimension-one future-staying graph theorem used later in that file.

**Evidence boundary.** The reduction from a relative domain with corners to a
compact boundaryless problem, the parameter bookkeeping, and the precise
application to the \(K_1\) variables are given below. The one imported
analytic input is the classical compact boundaryless \(C^k\) normally
hyperbolic invariant-manifold section theorem, applied to a time-\(T\) map.
The version used is restated in Section 2. Its standard sources are the
(C^r) section theorem (pp. 25--38,
[DOI](https://doi.org/10.1007/BFb0092045)) and the local compact-NHIM theorem
(pp. 39--53, [DOI](https://doi.org/10.1007/BFb0092046)) in
Hirsch--Pugh--Shub, *Invariant Manifolds*, Lecture Notes in Mathematics 583,
and Fenichel, *Persistence and Smoothness of Invariant Manifolds for Flows*
([DOI](https://doi.org/10.1512/IUMJ.1972.21.21017)). This note does not
reprove that boundaryless section theorem. A submission bibliography must
contain those sources, or the full boundaryless graph-transform proof must be
inserted instead.

## 1. Relative local invariance and admissible doubles

Let \(B\) be a compact \(C^{k+1}\) manifold with corners and let
\(\Lambda\) be a compact parameter manifold with corners. In the present
application both are rectangles. Let

\[
 E=E^{\rm s}\oplus E^{\rm u}\longrightarrow B\times\Lambda
\tag{1}
\]

be a \(C^k\) vector bundle, and let \(\pi:E\to B\times\Lambda\) be its
projection. A section \(h\) over \(B\times\Lambda\) is **locally invariant
relative to \(B\)** for a parameter family \(X_\lambda\) if, whenever

\[
 Z(0)=(c,h(c,\lambda)),\qquad
 Z(t)=\Phi_\lambda^t Z(0)
\tag{2}
\]

is defined in the selected tubular neighborhood and
\(0\in[t_0,t_1]\) and
\(\pi Z([t_0,t_1])\subset B\times\{\lambda\}\), one has

\[
 Z(t)\in\operatorname{graph}h
 \quad\text{for every }t\in[t_0,t_1].
\tag{3}
\]

Thus (3) is an orbit-segment statement. It does not say that an orbit remains
over \(B\) after it reaches an outgoing face. This is the sense in which the
manifold may be overflowing.

An **admissible doubled extension** consists of the following fixed data.

1. Each face of \(B\) and \(\Lambda\) has a two-sided collar. Iterated
   doubling gives compact boundaryless manifolds \(\widehat B\) and
   \(\widehat\Lambda\), and (1) extends to a bundle
   \(\widehat E\to\widehat B\times\widehat\Lambda\).
2. The vector fields extend to one fixed tubular neighborhood
   \(\widehat{\mathcal U}\subset\widehat E\). Their flows are defined there
   for \(|t|\le T\), for one \(T>0\), whenever the relevant orbit segment
   remains in a fixed slightly smaller tube.
3. On the original relative tube the extension is exactly the given vector
   field. If a face has been designated structurally invariant, the extension
   preserves that face on its doubled collar. No tangency condition is imposed
   on a face designated incoming or outgoing.

For a rectangular finite-dimensional problem with a smooth field on a
two-sided coordinate collar, these data are obtained by ordinary smooth
extension and doubling. The choice of extension is part of the construction;
it is not intrinsic to the relative vector field.

## 2. Boundaryless input used below

We use the following standard form of compact NHIM persistence. It is stated
here so that no stronger conclusion is silently imported.

**Boundaryless NHIM section theorem.** Let \(\widehat{\mathcal M}_0\) be a
compact boundaryless invariant \(C^k\) manifold of a \(C^k\) vector field,
\(k\ge2\). Suppose its tangent bundle has an invariant splitting

\[
 T_{\widehat{\mathcal M}_0}\widehat{\mathcal U}
 =T\widehat{\mathcal M}_0\oplus E^{\rm s}\oplus E^{\rm u}.
\tag{4}
\]

For the derivative of one time-\(T\) map write \(C^T,S^T,U^T\) for the
three cocycles in (4). Assume that, in fixed bundle metrics, there is
\(0<\varkappa<1\) such that for \(0\le j\le k\),

\[
 \sup_{\widehat{\mathcal M}_0}
 \|S^T\|\,\|(C^T)^{-1}\|^j\le\varkappa,
 \qquad
 \sup_{\widehat{\mathcal M}_0}
 \|(U^T)^{-1}\|\,\|C^T\|^j\le\varkappa.
\tag{5}
\]

Then every sufficiently state-\(C^1\)-small \(C^k\) perturbation, on a fixed
tubular neighborhood and with a fixed \(C^k\) bound, has a \(C^k\) locally
invariant manifold which is a section of the fixed normal bundle. In a
sufficiently small fixed tube this section is unique for that extended
problem among locally invariant \(C^1\) sections sufficiently close to the
zero section. The strict inequalities (5) persist with weakened margins.

For a compact family with common \(T,\varkappa\), tube, \(C^1\)-smallness, and
\(C^k\) bounds, the tube and all resulting \(C^k\) bounds may be chosen
uniformly. The parameter-dependent section transform gives the following
more general conclusion without requiring the parameter derivatives of the
perturbation to be small. If the extended field has bounded mixed derivatives

\[
 D_c^iD_\lambda^jX_\lambda,\qquad
 i+j\le k,\quad j\le q\le k,
\tag{6}
\]

then the fixed section has the corresponding mixed derivatives. If the
extended field is jointly \(C^k\) in \((c,\lambda)\), the section is jointly
\(C^k\).

The two inequalities in (5) are both needed. The first controls the stable
normal direction against backward center growth, and the second controls the
unstable normal direction against forward center growth. A one-sided normally
expanding graph theorem does not by itself imply this saddle-type statement.

For orientation, the graph-transform proof of the boundaryless theorem uses
the time-\(T\) transform on sections of \(E^{\rm s}\oplus E^{\rm u}\). On the
\(j\)-jet bundle its two homogeneous normal parts have norms bounded by the
two quantities in (5). The lower-order differentiated terms are
inhomogeneous and contain only previously constructed jets and derivatives of
the field. Contraction successively on the zeroth through \(k\)th jet bundles
gives the stated regularity. Treating \(\lambda'=0\) makes parameter
directions center directions when the perturbation is jointly \(C^1\)-small.
In the general compact-family formulation, differentiating the uniformly
contracting section transform in \(\lambda\) gives (6); parameter derivatives
enter as bounded inhomogeneous terms. This paragraph explains the regularity
mechanism but is not a replacement for the cited boundaryless section theorem.

## 3. Relative overflowing persistence theorem

**Theorem 1 (relative overflowing saddle NHIM).** Let \(k\ge2\), let
\(B,\Lambda,E\) be as in Section 1, and fix an admissible doubled extension.
Suppose the doubled reference field has the zero section

\[
 \widehat{\mathcal M}_{0,\lambda}
 =\{(c,\lambda,0,0):c\in\widehat B\}
\tag{7}
\]

as a compact invariant manifold for every
\(\lambda\in\widehat\Lambda\), and suppose (4)--(5) hold through order \(k\)
with one common strict factor.

Let \(X_\lambda\) be a family whose doubled field is sufficiently
state-\(C^1\)-close to the reference field, with the fixed mixed bounds (6).
Then, after decreasing the normal tube but not \(B\) or \(\Lambda\), there is
a section

\[
 h=(h^{\rm s},h^{\rm u}):B\times\Lambda
      \longrightarrow E^{\rm s}\oplus E^{\rm u}
\tag{8}
\]

with the following properties.

1. Its graph is locally invariant relative to \(B\) in the sense of (2)--(3).
2. It has every mixed derivative in (6), uniformly for a compact family with
   common margins and bounds. In particular, a jointly \(C^k\) field gives a
   jointly \(C^k\) graph up to every face and corner of \(B\times\Lambda\).
3. The section is \(C^1\)-close to the zero section. Any strict open
   inequality holding on the reference zero section therefore persists after
   decreasing the perturbation size.
4. For the fixed admissible doubled extension, (8) is the restriction of the
   unique boundaryless NHIM in the chosen tube.
5. If a designated face is structurally invariant and its doubled extension
   preserves that face, the trace of (8) on the face is locally invariant for
   the restricted field.

The theorem makes no extension-independent uniqueness claim. Two admissible
doubled extensions which agree on the relative tube but differ beyond an
incoming or outgoing face may produce different relative center manifolds.
That difference may be flat at an invariant face. A model-specific invariance
equation, a boundary condition, or a maximal-staying condition is required to
select one of them intrinsically.

*Proof.* Double \(B\) and \(\Lambda\) and extend the normal bundle and both
fields using the fixed data of Section 1. For each
\(\lambda\in\widehat\Lambda\), apply the boundaryless NHIM section theorem to
\(\widehat{\mathcal M}_{0,\lambda}\). The common factor in (5), the uniform
state-\(C^1\) perturbation size, the common flow collar, and compactness give
one normal tube and one contraction factor for all parameters. Thus the
resulting sections \(\widehat h_\lambda\) are uniquely defined in that tube.

Let \(\mathcal G_\lambda\) denote the corresponding section transform. It is a
uniform contraction in the section variable, and its mixed derivatives are
bounded by (6). Differentiating
\(\widehat h_\lambda=\mathcal G_\lambda(\widehat h_\lambda)\) once gives a
linear equation with invertible left side
\(I-D_h\mathcal G_\lambda\). Repeated differentiation gives the same left side
and inhomogeneous terms containing only lower jets. Induction proves precisely
the mixed bounds (6). This is the parameter-dependent part of the cited
section theorem. All constants are uniform because the base, parameter set,
and time-\(T\) orbit collar are compact.

Set \(h(c,\lambda)=\widehat h_\lambda(c)\) and restrict it to
\(B\times\Lambda\). An orbit segment of the original
field whose base remains in \(B\) is also an orbit segment of the doubled
field. Invariance of \(\operatorname{graph}\widehat h_\lambda\) therefore gives
(3). Smooth restriction from the double gives the asserted regularity at
every face and corner; no trace theorem is being invoked.

If a designated face is invariant, perform its doubling with a
face-preserving extension. The time-\(T\) graph transform restricts to the
face. Uniqueness of its fixed section in the doubled tube identifies that
restriction with the trace of \(\widehat h_\lambda\). This proves item 5.

Finally, uniqueness is only uniqueness for the fixed doubled problem. The
boundaryless theorem does not compare two different extensions, and
restriction cannot create such a comparison. This proves the last paragraph
as well as items 1--4. \(\square\)

## 4. A directly usable corollary for the resolved \(K_1\) corner

The application in
[CENTRAL_OUTER_MATCHING.md](../van-der-pol/CENTRAL_OUTER_MATCHING.md)
eliminates \(q_1>0\) by the exact energy root and uses

\[
 c=(r_1,\sigma,H),\qquad
 \lambda=(a_2,\epsilon),\qquad
 (b,n)=\text{stable and unstable spectral coordinates of }(\Pi,\Omega).
\tag{9}
\]

Let

\[
 B=[0,R]\times[0,\sigma_0]\times[-H_0,H_0],\qquad
 \Lambda=[-A,A]\times[\epsilon_-,\epsilon_+].
\tag{10}
\]

The reference field in that proof freezes \(c\) and has

\[
 \mathcal M_0=\{(\Pi,\Omega)=(\Pi_0(r_1,\epsilon),0)\},\qquad
 \operatorname{spec}_{\rm normal}
 =\{-\lambda_1(r_1,\epsilon),+\lambda_1(r_1,\epsilon)\},
\tag{11}
\]

where

\[
 \lambda_1(r_1,\epsilon)
 =\sqrt{\sqrt\epsilon\,(2+\sqrt\epsilon\,r_1^2)}
 \ge \lambda_*>0.
\tag{12}
\]

The center time-\(T\) cocycle of this reference problem is the identity, while
the stable and unstable factors are bounded by
\(e^{-\lambda_*T}\) and \(e^{\lambda_*T}\). Therefore (5) holds for every
finite \(k\), uniformly on (10).

**Corollary 2 (the auxiliary \(K_1\) center graph).** Suppose the following
four application-specific facts have been verified on a fixed doubled
positive-root collar:

1. the implicit energy root is \(C^5\) with its required mixed parameter
   derivatives;
2. the energy-reduced \(K_1\) field is \(o_{C^1}(1)\)-close to the reference
   field as \(\sigma_0\downarrow0\), uniformly on (10);
3. its state and mixed derivatives through total order five are uniformly
   bounded on that collar; and
4. all required orbit segments of length \(|t|\le T\) remain in the doubled
   collar used to form the time-\(T\) map.

Then for sufficiently small \(\sigma_0,H_0\), and normal radius there is a
relative locally invariant graph

\[
 (\Pi,\Omega,q_1)
 =(\Pi_{\rm c},\Omega_{\rm c},q_{\rm c})
    (r_1,\sigma,H,a_2,\epsilon)
\tag{13}
\]

which is jointly \(C^5\). In particular it has all state derivatives through
order five and all mixed derivatives with at most two external derivatives
used in V5. Since \(\Pi_0\) has a positive minimum on the compact reference
cylinder, \(C^0\) closeness permits the uniform choice

\[
 \Pi_{\rm c}\ge c_\Pi>0.
\tag{14}
\]

*Proof.* Conditions 1 and 3 give the regularity and common high-derivative
bounds required by Theorem 1. Condition 2 supplies its \(C^1\)-smallness,
and condition 4 supplies the fixed flow collar. Equations (11)--(12) verify
the boundaryless normal-hyperbolicity inequalities (5) through \(k=5\).
Theorem 1 gives the \((\Pi,\Omega)\) graph. Composition with the positive
energy root gives \(q_{\rm c}\), and compact positivity gives (14).
\(\square\)

The block estimates displayed in the current V5 proof,

\[
 \max\{\mu_2(D_cF_c),\mu_2(-D_cF_c)\}\le\theta_{\rm c},
 \quad
 \mu_2(D_bF_b)\le-\lambda_*+\theta_{\rm c},
 \quad
 \partial_nF_n\ge\lambda_*-\theta_{\rm c},
\tag{15}
\]

together with small cross blocks and
\(12\theta_{\rm c}<\lambda_*\), are a quantitative way to retain the
two-sided fifth-order gaps and cone margins after the \(C^1\)-closeness and
flow-collar hypotheses have been checked. Corollary 2 does not itself prove
the closeness, the flow-domain containment, or these model-specific
inequalities; they must still be derived from the exact reduced equations on
the stated collar.

## 5. What this lemma does and does not close

For the resolved \(K_1\) argument, Theorem 1 and Corollary 2 justify exactly:

- existence of one auxiliary saddle-type center graph across the doubled
  \(r_1,\sigma,H\) cylinder;
- ordinary joint \(C^5\) regularity and hence the state and two-external-
  parameter derivatives used later;
- smooth traces at the invariant faces without a boundary trace loss; and
- the strict lower bound \(\Pi_{\rm c}\ge c_\Pi>0\).

They do **not** prove any of the following.

1. **Intrinsic uniqueness of the relative center graph.** Only a fixed
   doubled extension has a unique persistent NHIM. Different overflowing
   extensions may give graphs differing by flat terms.
2. **The model-specific weighted five-jet.** The coefficients and the claim
   that all other monomials of weighted degree at most four vanish must come
   from the exact \(K_1\) invariance equation, the two axis restrictions, and
   a joint Taylor calculation. Normal hyperbolicity alone does not supply
   those coefficients.
3. **The directed corner crossing.** Positivity of \(\Pi_{\rm c}\), the exact
   identity \((r_1\sigma)'=0\), and the three blow-up charts must still be used
   to prove that positive-\(r\) characteristics cross from entry to exit.
4. **Identification with either terminal hypersurface.** Equality with the
   frozen canonical core graph or with the V4 outer future-staying graph uses
   the separate maximal-staying graph and its uniqueness; it is not a
   consequence of this auxiliary NHIM lemma.
5. **Numerical constants.** The theorem is existential. It supplies no
   computable value of \(\sigma_0,H_0,c_\Pi\), the normal radius, or the
   permissible \(C^1\) perturbation size.

The frozen flagship baseline contains a related persistence proposition for a
normally expanding codimension-one hypersurface and cites the same classical
boundaryless theory. That proposition is useful precedent, but it is not
imported here as a proof of Corollary 2: the auxiliary \(K_1\) object has both
a stable and an unstable normal direction, and the relative doubling and
local-uniqueness boundary above are local work of this repository.
