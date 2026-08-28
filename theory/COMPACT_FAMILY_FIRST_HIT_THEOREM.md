# Conditional compact-family first-hit transfer

**Status:** `LOCAL-AMENDMENT / Proved conditional transfer`  
**Scope:** uniformity of already constructed local objects.  This note does
not produce a first-hit block, endpoint solution, selector, matching map, or
cross form, and it does not certify an explicit numerical parameter box.

The inputs are the parameter-local saddle passages and fixed-system modules
bounded in
[`RETURN_EXIT_CODING_IMPORT.md`](../van-der-pol/RETURN_EXIT_CODING_IMPORT.md),
together with one already constructed finite physical event arrangement.
The conclusion is only compact-family persistence and finite-atlas descent.
No generic perturbation is used to manufacture lateral walls, fibrewise
transversality, or the absence of triple ties.

## 1. Inputs

Let \(\mathcal P=\bigcup_{i=1}^M V_i\), \(V_i\Subset U_i\), be a finite
marked cover of a compact parameter set.  Assume the following four packages.

### P. Passage and endpoint maps

On \(U_i\), the saddle-focus rates satisfy

\[
 \inf_{\mathcal P}\min\{\alpha_\mu,\beta_\mu\}>0.
\tag{1}
\]

An already constructed Kato-oriented exact saddle chart preserves the
transverse action \(\nu\) and gives

\[
\begin{aligned}
 T_{\mu,\sigma}(\nu)
  &=-\alpha_\mu^{-1}\log|\nu|+t_{\mu,\sigma}
      +\tau_{\mu,\sigma}(\nu),\\
 \Delta_{\mu,\sigma}(\nu)
  &=-{\beta_\mu\over\alpha_\mu}\log|\nu|+b_{\mu,\sigma}
      +\rho_{\mu,\sigma}(\nu),
\end{aligned}
\tag{2}
\]

with, for every fixed \(m\),

\[
 \max_{|\ell|\le2,\ 0\le j\le m}
 \frac{|D_\mu^\ell D_{\log\nu}^j\tau|
             +|D_\mu^\ell D_{\log\nu}^j\rho|}
 {|\nu|(1+|\log|\nu||)}\le C_m,
 \qquad D_{\log\nu}=\nu\partial_\nu.
\tag{3}
\]

The fixed-system mixed-endpoint package has already supplied, on one fixed
rectangle \(Z_{{\rm exit},i}\), maps

\[
 \Pi_{\mu,\sigma,\infty},\qquad
 \Pi_{\mu,\sigma,n},\quad n\ge N_i^{\rm ep},
\tag{4}
\]

and its uniform remote-trace estimates with two parameter derivatives at
every state contraction rate \(\alpha_{*,i}<\inf_{U_i}\alpha\).  Existence
and endpoint solvability in (4) are assumptions here.

### M. Matching package

On fixed compact source and target intervals, the imported fixed-system
package has already supplied the limiting and finite matching equations, an
isolated solution tube with uniform inverse bound, a target-action range and
angular-cut margin, the selector, and completed fixed-domain cross forms with
their contraction margin and mixed two-jets.  None of these follows here
from (2) alone.

### E. Physical event arrangement

Before the high-winding limit, one finite physical first-hit arrangement is
fixed and has these properties.

1. Its labelled sign strata, faces, corners, and fixed priorities form a
   disjoint exhaustive decomposition, with no residual component.
2. After pullback through the same \(\Pi_{\mu,\sigma,\infty}\), its finite
   defining list \(\mathscr h_{\mu,\sigma}\) is state-\(C^3\),
   parameter-\(C^2\), clean and neat.  All active ranks, empty-incidence
   gaps, inactive signs, hit speeds, earlier-event exclusions, flow buffers,
   and anchor distances have one positive normalized lower bound.
3. Competing finite hit times are indexed by one specified finite physical
   set \(\mathfrak Q\).  Each imported
   \(q_{ef}=t_e-t_f\) has either a positive empty-tie gap or a nonzero tie
   conormal whose signs give the adjacent orders.  Any triple-tie exclusion
   is part of this input.
4. A carrier and a label inside it are distinct.  A label such as the
   algebraic face has no artificial hit time.  Every carrier refinement is
   an exact partition and adds no \(q_{ef}\) unless two different finite hit
   times genuinely compete.
5. Every composed row has the spare bound

   \[
    \sup_{a+b\le3,\ b\le2}
       \|D_Z^aD_\mu^b h_{k,\mu,\sigma}\|<\infty.
   \tag{5}
   \]

### O. Overlap compatibility

The carriers, labels, first-hit maps, imported order rows, terminal data, and
physical primitive are the same physical objects on \(U_i\cap U_j\).  The
markings satisfy the hypotheses of
[`FINITE_MARKED_ATLAS_DESCENT.md`](FINITE_MARKED_ATLAS_DESCENT.md).  In
particular, no auxiliary face is chosen independently on an overlap.

## 2. Conditional transfer

### Proposition 2.1

Assume P, M, E, and O, and choose

\[
 0<\varkappa<
   \inf_{\mu\in\mathcal P}{2\pi\alpha_\mu\over\beta_\mu}.
\tag{6}
\]

After refining the cover, choose

\[
 \varkappa<\varkappa_i^+
  <{2\pi\inf_{\mu\in U_i}\alpha_\mu
       \over\sup_{\mu\in U_i}\beta_\mu}.
\tag{7}
\]

Then there are \(N_i^0\), \(C_i<\infty\), and one physical residence
threshold \(T_*\) such that, for \(n\ge N_i^0\),

\[
 \|\Pi_{\mu,\sigma,n}-\Pi_{\mu,\sigma,\infty}\|_{C^2_{Z,\mu}}
 \le C_i(1+n)^3e^{-\varkappa_i^+n}.
\tag{8}
\]

Every composed event row has the same estimate.  Hence the exact cell is
stratified-isotopic to the given limiting arrangement, preserving its
exhaustive component census, faces, corners, imported ties, and strict
orders.  The selector and cross forms supplied by M persist on one common
finite-cover threshold.  The resulting local relations descend to one
physical relation on the residence-time domain.  The proposition creates
none of the objects in P, M, E, or O.

#### Proof

Continuity and compactness give (7).  Choose
\(\alpha_{*,i}<\inf_{U_i}\alpha\) so close to the infimum that

\[
 \varkappa_i^+<2\pi\alpha_{*,i}/\sup_{U_i}\beta.
\tag{9}
\]

Clock inversion in (2) gives
\(|\nu|\asymp e^{-2\pi\alpha_\mu n/\beta_\mu}\).  Invoke the endpoint
estimate assumed in P at rate \(\alpha_{*,i}\).  Its imported polynomial
loss from two parameter derivatives is absorbed by (9), proving (8).

The chain rule and (5) give (8) after composition with every row.  Increasing
\(N_i^0\) puts this perturbation below the uniform clean/neat isotopy
threshold in E.  All ranks, gaps, first-hit inequalities, imported
\(q_{ef}\), and the exhaustive census persist.  The strict matching margins
in M persist under the same increase; this makes the already supplied
selector and cross forms uniform, rather than reconstructing them.

Finally the passage time and finite section slides give

\[
 \left|n_i-{\beta_\mu\over2\pi}
       \mathcal T_{{\rm sf},\mu}\right|\le C_i'.
\tag{10}
\]

A finite maximum produces \(T_*\).  Hypothesis O is exactly the input needed
for finite marked-atlas descent. \(\square\)

## 3. Van der Pol inputs

V2 and the bounded import supply P and M.  V6, Sections 3.1--4, verifies E by
refining the existing V2 physical block: the algebraic hypersurface is a
label inside a transverse carrier, while the V3 event-free slide replaces
the protected pole gate before the \(x=10\) aperture is partitioned.  V2 and
the finite-atlas descent note supply O.  The proposition asserts no global
winding label, temporal stability, Turing selection, canard identification,
or interval-certified box.
