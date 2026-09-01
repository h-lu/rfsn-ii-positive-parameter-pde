# V5 finite-\(K_1\) plus true-source incidence: representative-cell composition

**Result.**  Three V5 interval proof units, together with the previously
certified source interface, compose to a local mathematical **PASS** on one
explicit parameter cell.  For every parameter in that cell, the canonical
true source meets the *actual* finite-\(K_1\)
pullback of the V4 future-staying graph once and transversely, within the
specified source-phase component.  This note performs only the logical
composition; it does not add a numerical run.

The result remains current-computer and non-claim-bearing.  In particular, it
is supplementary evidence for the mechanism used in the analytic V5 theorem,
not an explicit-box proof of that theorem.

## Domains and common interface

Let

\[
 \mathcal B_{\rm v2}
 =\left[\frac1{100},\frac1{50}\right]
  \times\left[-\frac14,\frac14\right]
  \times\left[\frac45,\frac65\right]
\]

and let the representative grid cell be

\[
 \mathcal C_*
 =\left[\frac{96}{6400},\frac{97}{6400}\right]
  \times\left[0,\frac1{256}\right]
  \times\left[1,\frac{121}{120}\right]
 \subset\mathcal B_{\rm v2}.
\tag{1}
\]

This is cell \((32,64,24)\) of the disclosed
\(64\times128\times48\) grid.  All three proof units use the same zero-energy
\(U=-4\) section, the same spectral coordinates \((b,n)\), and the contract

\[
 B=\frac{27}{200000},\qquad
 N=\frac1{12500},\qquad
 \rho=\frac7{10}.
\tag{2}
\]

## Composed statement

Fix \(\mu\in\mathcal C_*\), and let \(\Gamma^+_\mu\) be the certified V4
terminal graph at \(r_1=2\).  Then the following statements hold.

1. There is a unique \(C^3\) lower graph

   \[
    \Gamma^-_\mu
      =\{(b,g^-_\mu(b)):|b|\le B\}
   \]

   whose forward orbit remains in the finite resolved-\(K_1\) tube and
   reaches \(\Gamma^+_\mu\).  It satisfies

   \[
    |g^-_\mu(b)|<N,qquad
    \operatorname{Lip}(g^-_\mu)\le\rho.
   \tag{3}
   \]

   Uniqueness is relative to the fixed terminal graph
   \(\Gamma^+_\mu\); it is not a uniqueness assertion for every invariant
   graph that may meet the tube.

2. The exact \(K_1\)-to-central transformation at \(U=-4\) sends
   \(\Gamma^-_\mu\) to a \(C^3\) graph \(P=G_\mu(V)\) over its image interval
   \(J_\mu\), with

   \[
    |G_\mu'(V)|\le2.0348531377655257<2.221.
   \tag{4}
   \]

   The graph lies in the fixed patch

   \[
    P\in[-6/5,-11/10],\quad
    V\in[-16,-31/2],\quad
    Q\in[-19/2,-9],\quad H=0.
   \tag{5}
   \]

   The statement is over \(J_\mu\); it does not assert that the graph is
   defined over the entire rectangle in (5).

3. Let \(S_\mu\) be the canonical true-source trace on \(U=-4\) in the
   slanted phase component used by the incidence certificate.  There is a
   unique

   \[
    \theta_\mu\in\left(-\frac1{25000},\frac1{25000}\right)
   \tag{6}
   \]

   such that \(S_\mu(\theta_\mu)\in\Gamma^-_\mu\).  The phase change in the
   source chart is orientation preserving, so this is equivalently a unique
   physical source phase in the same component.  The intersection is
   transverse on the \(U=-4\) section.  Its forward orbit stays in the
   finite-\(K_1\) tube, reaches the actual V4 terminal graph, and therefore
   enters the certified future-staying algebraic sheet.

The quantifier is

\[
 \forall\mu\in\mathcal C_*\quad\exists!\,\theta_\mu
 \quad\text{in the specified source-phase component}.
\tag{7}
\]

No regularity of \(\mu\mapsto\theta_\mu\) is asserted by this composition.

## Why the composition is valid

The finite-\(K_1\) pullback theorem holds for every
\(\mu\in\mathcal B_{\rm v2}\), hence also after restriction to
\(\mathcal C_*\).  Its actual graph satisfies exactly the value and slope
contract (2)--(3).

The incidence proof on \(\mathcal C_*\) is uniform both in \(\mu\) and over
**every** lower graph satisfying that contract.  It may therefore be
instantiated pointwise with the parameter-dependent graph \(g^-_\mu\); no
parameter derivative of \(g^-_\mu\) is required.  The source-face signs give
opposite signs for

\[
 h(\theta)=n(\theta)-g^-_\mu(b(\theta)),
\]

while the certified bounds

\[
 \left|\frac{db}{dn}\right|\le0.394231,qquad
 \operatorname{Lip}(g^-_\mu)\le0.7
\]

make \(h\) strictly secant-monotone.  This proves existence and uniqueness.
Since \(g^-_\mu\) is \(C^3\), the same strict cone inequality gives
transversality.

Finally, both proof units use the same \(H=0\), \(U=-4\), \((b,n)\)
coordinates.  The certified negative-\(Q\), positive-root sheet and the
nonzero coordinate determinant show that the incidence is the same physical
point after the exact central regraph.  The finite-\(K_1\) definition of
\(\Gamma^-_\mu\) then supplies its future.

## Evidence and exact boundary

The three V5 inputs are:

- [`V5_K1_TUBE_REPORT.md`](V5_K1_TUBE_REPORT.md), a complete-v2-box local
  mathematical PASS for the actual V4 terminal pullback;
- [`V5_CENTRAL_ATTACHMENT_REPORT.md`](V5_CENTRAL_ATTACHMENT_REPORT.md), a
  complete-v2-box local mathematical PASS for the exact central attachment
  and universal regraph;
- [`V5_SOURCE_INCIDENCE_REPORT.md`](V5_SOURCE_INCIDENCE_REPORT.md), with the
  archived representative result
  [`vdp_v5_source_incidence_representative_cell.json`](results/vdp_v5_source_incidence_representative_cell.json),
  a local mathematical PASS on \(\mathcal C_*\).

The identification of the source tube with the canonical true source also
imports [`P2B0_REPORT.md`](P2B0_REPORT.md),
[`P2B_KATO_REPORT.md`](P2B_KATO_REPORT.md), and
[`P2E_AXIS_CHART_REPORT.md`](P2E_AXIS_CHART_REPORT.md).  These prove the
true-graph error bounds, the positive-Kato radius-\(1/100\) source
parameterization, and the exact zero-energy chart on a bridge containing the
v2 box.  The standalone incidence manifest freezes only its executable,
configuration, and toolchain and remains explicitly conditional on the
target graph.  It binds neither these source certificates nor the
V4/finite-\(K_1\)/central target-graph certificates, and no verified full-cover
summary exists.  These dependencies are stated explicitly rather than hidden
inside the word ``source.''

The source-interface identities used here are:

- P2b0 result SHA-256
  `91c1762329a9e19e8db69052f9397532512d8031f361f0b6eeb43edbeda5d5ac`;
- P2bK result SHA-256
  `c67cce575caa396eba5b4388e8ba9a0c9d73fd702f69911d64c878f57f27bff3`;
- P2e axis-chart proof SHA-256
  `1e95cee5dc9fbc4341285912c767cd97a39bc9cd64bb4f0e6c74227725064f01`
  and checker SHA-256
  `2c644d43357304353c8d16dd8434360a228d03cc0b18d69eb5a3712d2cc0aeae`.

The representative result SHA-256 is
`2e1d57a331298d3c340413ea1c99753eeb0a128e55f6635370db66d1e4c58b3e`.
Each input deliberately records `claim_bearing=false`, and this composition
does not change that field.  The three additional lower/centre/upper grouped
cells are useful kernel checks, but their union is not a cover.

The 393,216-cell full incidence run is deferred to GitHub Issue #14.  The
following are **not** established here:

- true-source incidence on all of \(\mathcal B_{\rm v2}\);
- a claim-bearing explicit-box V5 theorem or the mixed parameter regularity
  and moving-cut covariance of the analytic V5 theorem;
- uniqueness outside the specified phase component, or uniqueness among
  arbitrary slow or invariant graphs;
- a nonzero-action branch, a global stationary-PDE branch, temporal
  stability, dynamic Turing selection, or canard identification;
- an independent-machine replay.

The analytic companion theorem remains proved on its separate existential
positive annulus under Hypothesis H.  It does not use this numerical cell.
