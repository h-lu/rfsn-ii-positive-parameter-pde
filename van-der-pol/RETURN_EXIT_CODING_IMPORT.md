# Frozen return--exit and coding modules for Track V

**Evidence status: Imported (analytic theorems from an immutable source).**
This note freezes only the model-independent high-winding, first-event,
exact-action, and coding modules used in V6--V7.  In particular, it does
**not** import either singular end of the flagship normal form.  The genuine
positive-parameter pole and algebraic end used in this repository remain the
objects proved in V3--V5A.

The 2026-08-28 read-only crosswalk to the fixed-system focused paper is
recorded in
[`../theory/FLAGSHIP_IMPORT_AUDIT_2026-08-28.md`](../theory/FLAGSHIP_IMPORT_AUDIT_2026-08-28.md).
It identifies the compact-family passage/whole-cell theorem and the genuine
positive NHIM-pole terminal theorem as local obligations; the frozen revision
below remains the normative modular source.

## 1. Immutable source

The source is H. Lu, *First returns, singular exits, and action finite parts
near a reversible Hamiltonian saddle-focus*, repository
<https://github.com/h-lu/reversible-rfsn-ii-waves>, at commit

\[
 \mathtt{d54add098545063d5efe8f1d6f062d4cfc116a0d}.
\tag{1}
\]

The imported manuscript is

    papers/paper-a/manuscript/main.tex
    0baf6335aad72d5893479d8876d2613671ecb8ac2ccd73664405dea4381e6a20

and has 9163 lines at (1).  The precise source objects used below are:

- Proposition 2.11, labelled
  `prop:transverse-homoclinic-produces-h1` (around lines 2034--2070): a
  transverse Hamiltonian saddle-focus homoclinic gives the compact limiting
  matching graph and the uniform inverse/range margins in H1;
- Lemma `lem:mixed-passage` (line 3168): the opposite-endpoint saddle
  passage and its mixed two-jet exponential estimates;
- Lemma `lem:action-gluing` (line 3497): convergence of the local
  saddle-passage action after splitting it into stable and unstable half-tail
  actions;
- Proposition `prop:selector` (line 3625): uniform solution of the
  finite-dimensional winding matching equation;
- the simultaneous section shear and completed cross forms in equations
  `eq:simultaneous-section-shear` through
  `eq:scaled-seam-bounds` (around lines 3790--3910);
- Proposition `prop:first-exit-family` (line 4188): the complete local
  return--first-exit decomposition under H1--H2;
- Proposition `prop:section-gauge-covariance` (line 4470): exact section
  and primitive-gauge coboundaries;
- Theorem `thm:terminal-extension` (line 5057): coding for a countable
  Markov family with strict first-exit sets; and
- Corollaries `cor:physical-covariance` and
  `cor:period-action-asymptotics` (lines 2653 and 2691), only for their
  finite-atlas descent and finite-composition consequences.

These are analytic statements.  No interval certificate from the flagship
is imported by this note.  The separate frozen central data used in V2 are
listed, with their own evidence boundary, in
[CENTRAL_CORE_IMPORT.md](CENTRAL_CORE_IMPORT.md).

## 2. Input package retained from the source

We restate the hypotheses actually used in V6.  This prevents the phrase
"apply the flagship theorem" from hiding a mismatch between its concrete
end compactifications and the positive-parameter ends proved here.

Let a compact parameter family of reversible exact Hamiltonian fields have a
regular zero-energy saddle-focus with eigenvalues

\[
 \pm\alpha_\mu\pm i\beta_\mu,
 \qquad \inf_\mu\min\{\alpha_\mu,\beta_\mu\}>0.
\tag{2}
\]

The local zero-energy passage is written in exact action--angle sections as

\[
 \begin{aligned}
 T_{\mu,\sigma}(\nu)
   &=-\alpha_\mu^{-1}\log|\nu|+t_{\mu,\sigma}
      +\tau_{\mu,\sigma}(\nu),\\
 \Delta_{\mu,\sigma}(\nu)
   &=(\beta_\mu/\alpha_\mu)\log|\nu|+b_{\mu,\sigma}
      +\rho_{\mu,\sigma}(\nu),
 \end{aligned}
\tag{3}
\]

where the transverse action \(\nu\) is preserved exactly and the remainders,
including mixed state/parameter derivatives through total order two, are
\(O(|\nu|(1+|\log|\nu||))\) in the weighted logarithmic derivatives
\(D_{\log\nu}=\nu\partial_\nu\).
Equation (3) retains the frozen manuscript's local Darboux phase convention.
It is retained here only to identify the frozen input; it is not inserted
verbatim into the V2 phase normalization.  The full coordinate conjugation
used in V2 is

\[
 \mathcal T=\operatorname{diag}(C_0,C_0),
 \qquad I_1(\mathcal Tz)=I_1(z),
 \qquad I_2^{\rm F}(\mathcal Tz)=I_2^{\rm K}(z).
\]

It is symplectic and commutes with the standard reverser.  In particular,
the transverse action and its sign \(\sigma\) are unchanged.  Direct
quadrature on the explicit Kato-oriented radial sections in V2 gives the
chartwise data used by the present application:

\[
 \begin{aligned}
 T^{\rm K}_{\mu,\sigma}(\nu)
   &=-\alpha_\mu^{-1}\log|\nu|+t^{\rm K}_{\mu,\sigma}
      +\tau^{\rm K}_{\mu,\sigma}(\nu),\\
 \Delta^{\rm K}_{\mu,\sigma}(\nu)
   &=-\frac{\beta_\mu}{\alpha_\mu}\log|\nu|
      +b^{\rm K}_{\mu,\sigma}
      +\rho^{\rm K}_{\mu,\sigma}(\nu).
 \end{aligned}
\tag{3K}
\]

The same weighted-log bounds hold.  The opposite leading sign in (3K) is
proved from the Kato normal-form flow; it is not obtained from a
two-dimensional phase--action reversal of (3).

The return and first-exit modules must also be conjugated consistently.  Use
the positive clock lift

\[
 \beta_\mu T^{\rm K}_{\mu,\sigma}(\nu)=2\pi n+\theta
\]

and set

\[
 c^{\rm K}_{\mu,\sigma}
   =e^{\alpha_\mu t^{\rm K}_{\mu,\sigma}}\ge c_*>0,
 \qquad
 \widetilde b^{\rm K}_{\mu,\sigma}
   =b^{\rm K}_{\mu,\sigma}
      -\beta_\mu t^{\rm K}_{\mu,\sigma}.
\tag{3K-a}
\]

Clock inversion is unchanged:

\[
 \nu_{\mu,\sigma,n}(\theta)
 =\sigma c^{\rm K}_{\mu,\sigma}
   e^{-\alpha_\mu(2\pi n+\theta)/\beta_\mu}
   \exp\!\left\{\alpha_\mu
       \tau^{\rm K}_{\mu,\sigma}
          (\nu_{\mu,\sigma,n}(\theta))\right\}.
\tag{3K-b}
\]

Substitution into the phase law gives

\[
 \Delta^{\rm K}_{\mu,\sigma}
       (\nu_{\mu,\sigma,n}(\theta))
 =2\pi n+\theta+\widetilde b^{\rm K}_{\mu,\sigma}
   +\varrho^{\rm K}_{\mu,\sigma,n}(\theta),
\quad
 \varrho^{\rm K}_{\mu,\sigma,n}
 =\rho^{\rm K}_{\mu,\sigma}(\nu_{\mu,\sigma,n})
  -\beta_\mu\tau^{\rm K}_{\mu,\sigma}
       (\nu_{\mu,\sigma,n}).
\tag{3K-c}
\]

Consequently the Kato limiting local exit template and the lifted finite
matching row are

\[
 \pi^{{\rm loc},{\rm K}}_{\mu,\sigma,\infty}(\phi,\theta)
  =\bigl(\phi+\theta+\widetilde b^{\rm K}_{\mu,\sigma},0\bigr),
\tag{3K-d}
\]

\[
 \psi-\phi-\theta-\widetilde b^{\rm K}_{\mu,\sigma}
       -\varrho^{\rm K}_{\mu,\sigma,n}(\theta)=0.
\tag{3K-e}
\]

At the limiting cut the last residual is omitted.  Thus the limiting
matching relation has second row
\(\psi-\phi-\theta-\widetilde b^{\rm K}_{\mu,\sigma}\).  Equations
(3K-a)--(3K-e) are the convention used whenever V6 invokes a signed limiting
template, selector, or first-exit module.  The proof is transported as
follows.  Reflect the compact residual-angle coordinate only inside the
frozen proof charts, conjugate both section phase charts and the finite
homoclinic map by the induced phase reflections and constant translations,
and then rewrite the exact clock and matching equations as (3K-b)--(3K-e).
If reflection crosses the chosen half-open endpoint, translate the residual
angle by \(2\pi\) and change the local deck integer by at most one.  This is
the bounded winding recoding already allowed on a finite marked atlas; the
physical positive clock integer is still defined by
\(\beta_\mu T=2\pi n+\theta\), not by a reflected clock equation.

These finite coordinate conjugacies may change individual conormal signs but
not ranks, least singular values, strict gaps, contraction norms, or
connected incidences.  Repeating the clock contraction and matching
calculation with (3K) therefore gives the same estimates and coding
conclusions with the displayed Kato signs.  The actual clean event
arrangement is still an input to be checked for the Kato template in P2e; it
is not inferred to be literally the frozen raw arrangement.  This is a local
covariant restatement of the module, not an equality of raw templates.  The
source and target action signs are not relabelled.

The finite homoclinic transition must be transverse in the regular energy
surface.  After choosing compact source and target intervals, Proposition
2.11 turns this into:

1. a \(C^2\) limiting matching graph over one fixed rectangle;
2. a uniform inverse bound for the matching derivative;
3. a target-action interval contained strictly in the transition range; and
4. a positive lifted-angle boundary margin.

The first-exit input is formulated on one fixed compact source rectangle

\[
 Z_{\rm exit}=I_s\times\overline J_0
\]

and two signed limiting source-exit templates
\(\Pi_{\mu,\sigma,\infty}:Z_{\rm exit}\to B^u_\mu\),
\(\sigma\in\{+,-\}\).  The vector-field and finite-flight atlas used by
the module are at least state-\(C^5\) and parameter-\(C^2\).  The event
faces and their finite first-hit pullbacks are state-\(C^3\),
parameter-\(C^2\), with the spare uniform mixed bound

\[
 \sup_{i+j\le3,\ j\le2}
  \|D_Z^iD_\mu^j h_{k,\mu,\sigma}\|<\infty.
\]

All outgoing faces and, inside the homoclinic aperture, all re-entry,
target-sign, stable-cut, and return-lateral faces must be pulled back through
the corresponding compact flights and the *same* signed template before H2
is checked.  On \(Z_{\rm exit}\) these functions must form one finite
clean, neat arrangement.  Its labelled connected sign strata must be
literally exhaustive.  Every active pullback conormal family, together with
the active boundary conormals of \(Z_{\rm exit}\), has a positive least
singular value; every reference-empty incidence, inactive sign,
earlier-event exclusion, event order, hit speed, flow-domain buffer, and
selected-anchor distance has a positive compact margin.  The closures of
the algebraic, homoclinic, and pole apertures are pairwise disjoint.  Compact
pre-event tubes cover every assigned relative interior; their complement is
partitioned by named lateral faces, rather than left as an implicit residual
set.  Interior algebraic and pole anchors carry fixed current-sign and
connected-component labels with positive boundary distance.  The permitted
outcomes are

\[
 \{\mathrm{return}\}\sqcup
 \{\mathrm p,\mathrm a,\mathrm{out},\mathrm{rbox},\mathrm{cut}\}.
\tag{4}
\]

The algebraic member of (4) is a cooriented hypersurface event.  The pole
member is an open aperture.  The two need only have genuine, strictly
controlled terminal behavior after their compact first hit; their particular
compactifications do not enter the modules imported here.

Finally, for exact-action conclusions, the primitive is fixed on the
physical state space.  In a local exact gauge at the equilibrium its action
density vanishes to second order.  Every terminal counterterm is subtracted
only from its terminal segment after exact finite-cut composition.

## 3. Imported high-winding conclusions

Fix a compact family satisfying Section 2 and choose

\[
 0<\kappa<\inf_\mu {2\pi\alpha_\mu\over\beta_\mu}.
\tag{5}
\]

The mixed-passage and selector modules give one integer \(N\), a section
width \(\nu_N>0\), and, for every

\[
 a=(\sigma,n,\sigma'),\qquad
 \sigma,\sigma'\in\{+,-\},\qquad n\ge N,
\tag{6}
\]

a completed return strip.  In fixed vertex rectangles its return map has
the cross form

\[
 x'=f_a(x,y'),\qquad y=g_a(x,y'),
\tag{7}
\]

with

\[
 \varepsilon_{\mu,a}=\nu_N^{-1}
   \exp\!\left(-{2\pi\alpha_\mu\over\beta_\mu}n\right),
 \qquad \widetilde g_a=g_a/\varepsilon_{\mu,a}.
\tag{8}
\]

There are uniform constants \(0<\vartheta<1\), \(m>0\), and \(C<\infty\)
such that the cross-form contraction is at most \(\vartheta\), its angular
image has an absolute interior margin, and

\[
 m\le\widetilde g_a\le m^{-1},\qquad
 g_a\le1-m,\qquad
 \|Dg_a\|_{C^1}\le C\varepsilon_{\mu,a}.
\tag{9}
\]

For each fixed sign pair there are mixed-\(C^2\) limiting cross forms and

\[
 \|f_a-f_{\mu,\sigma,\sigma',\infty}\|_{C^2}
 +\|\widetilde g_a-
       \widetilde g_{\mu,\sigma,\sigma',\infty}\|_{C^2}
 \le C(1+n)^3e^{-\kappa n}.
\tag{10}
\]

The completed parent strip is cut by the target zero-action face.  Its two
regular sides give both target signs, while the intervening face is labelled
`cut`; it is never counted as a return.  Proposition
`prop:first-exit-family` gives the disjoint identity

\[
 \begin{aligned}
 \Sigma_N={}&
 \bigsqcup_{\substack{\sigma,\sigma'\in\{+,-\}\\n\ge N}}
     \mathcal V_{\sigma,n}^{\sigma'}
 \ \sqcup\!
 \bigsqcup_{\substack{\sigma\in\{+,-\}\\n\ge N}}
     \mathcal I_{\sigma,n}\\
 &\sqcup
 \bigsqcup_{\substack{\mathsf t\in
       \{\mathrm p,\mathrm a,\mathrm{out},\mathrm{rbox}\}\\
       \sigma\in\{+,-\},\ n\ge N,\ \ell}}
       E_{\mathsf t,\sigma,n,\ell},
 \end{aligned}
\tag{11}
\]

where every union ranges only over nonempty connected components.  Each
point has one winding, one current sign, and one first-event label.  Each
return has one next sign.  The finite component label \(\ell\) is retained;
there is no unlabeled residual component.  A selected interior anchor for
each of \(\mathsf t=\mathrm a,\mathrm p\) produces one nonempty component
for every \(n\ge N\).  No theorem asserts that every other end label or
every source sign is nonempty.

## 4. Imported action, covariance, and coding conclusions

On every finite branch \(P_a:\Sigma_a^-\to\Sigma_a^+\), its physical
orbit integral \(B_a\) obeys

\[
 P_a^*(\lambda|_{\Sigma_a^+})-\lambda|_{\Sigma_a^-}
   =d_{\Sigma_a^-}B_a.
\tag{12}
\]

For composable finite branches,

\[
 B_{a_2\circ a_1}=B_{a_1}+B_{a_2}\circ P_{a_1}.
\tag{13}
\]

The action-gluing lemma gives mixed-\(C^2\) limits of the return action with
error \(C(1+n)e^{-\kappa n}\).  The same statement holds for the
renormalized local-clock remainder.  For a terminal family, composition of
the finite central branch with an independently proved mixed-\(C^2\)
terminal finite part gives mixed-\(C^2\) convergence on a compact label
set, but mixed \(C^2\) alone does not retain a linear quantitative rate after
composition.  The explicit
\(C(1+n)^3e^{-\kappa n}\) mixed-\(C^2\) rate requires the terminal potential
to have one spare state derivative (or an equivalent \(C^{2,1}\) bound),
with the corresponding mixed parameter bounds.  V5A supplies that spare
derivative at the algebraic end, and V6 proves it separately at the positive
pole.  These are finite-composition consequences; this import neither
identifies nor proves a terminal counterterm.

Orbit-following changes of section and changes
\(\lambda\mapsto\lambda+d\psi\) alter branch potentials by endpoint
coboundaries.  These cancel under composition and telescope around a closed
orbit.  A finite compatible marked atlas therefore descends to one physical
first-event relation; local winding labels may be refined by bounded integer
recodings on overlaps.

The simultaneous section shear also retains two selected traces in each
completed vertex rectangle:

\[
 \Gamma^u_{\rm prim}=\{x=0\}
    \subset W^u(O_\mu)\cap\overline\Sigma,
 \qquad
 \Gamma^s_{\rm loc}=\{y=0\}
    \subset W^s_{\rm loc}(O_\mu)\cap\overline\Sigma.
\]

They are the selected primary unstable-image and local stable traces; these
inclusions are not equalities with all global stable or unstable
intersections.  This is the boundary datum used for finite-word homoclinic
solutions.

Under (7)--(11), Theorem `thm:terminal-extension` gives the two-vertex full
countable graph with all edges (6).  Its two-sided edge shift is homeomorphic
to the trapped return set, one-sided future words give stable plaques, and
every nontrapped point has a finite return word followed by one unique
first-exit component.  The roof and action potentials have summable
variations.  A primitive cyclic word gives one periodic orbit; finite
composition gives its period and closed action asymptotics.

## 5. Import boundary

The following flagship conclusions are deliberately **not** imported:

- its concrete algebraic factorization, same-\(e\) flatness theorem, or
  algebraic time/action counterterm;
- its pole compactification, fixed indicial matrix, Laurent--log recursion,
  or pole action counterterm;
- its computer-assisted verification of the normal-form end channels;
- any claim that the positive-parameter van der Pol family belongs to the
  flagship's full marked end coefficient class;
- a global labelled shift across arbitrary marking changes; or
- any PDE temporal stability, temporal chaos, or experimental conclusion.

This restriction matters.  The V3 positive-parameter pole has admissible
indicial roots \(1,4\), whereas the flagship's concrete normal-form pole
module uses a different marked principal class.  V6 therefore applies only
the modular conclusions in Sections 2--4 and supplies both terminal modules
from V3 and V5A.
