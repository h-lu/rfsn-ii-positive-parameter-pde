# Exact algebraic source to the outer fold

This source-only bundle proves the missing outer arc for the reversible
fourth-order system

\[
 U'=P,\qquad P'=-U^2-V,\qquad V'=Q,\qquad Q'=U,
\]

with first integral

\[
 \mathcal E=Q^2-P^2-\frac23U^3-2UV.
\]

All claim-bearing numerical operations use outward-rounded FILIB/CAPD
intervals.  SciPy boundary-value solves provide centres and approximate
inverses only.  The generated centres, detailed JSONL output, and compiled
binaries are bulk replay artifacts and are not stored in the repository.

## Certified statement

Let \(\mathcal W_{\rm a}^{\rm tail}\) be the unique maximal
forward-staying graph only on the validated weighted tail corridor of
`validation/future-target-fold`.  Let \(\mathcal T_{\rm a}\) be the union
of the declared exact-source/algebraic shooting tubes whose unique first
\(e=.06\) entry is certified below, let \(\tau_{\rm a}\) be that first-hit
time, and put

\[
 \mathcal W_{\rm a}
 =\{z\in\mathcal T_{\rm a}:
       \Phi^{\tau_{\rm a}(z)}z\in\mathcal W_{\rm a}^{\rm tail}\}.
\]

No saturation or classification outside \(\mathcal T_{\rm a}\) is part of
this statement.  Also let

\[
 \operatorname {Fix}\mathcal R=\{P=Q=0\}.
\]

There is a connected \(C^2\) arc

\[
 c(U)=(U,0,V(U),0)\in
 \mathcal W_{\rm a}\cap\operatorname {Fix}\mathcal R,
 \qquad 0\le U\le U_f,
\]

with

\[
 c(0)=(0,0,1/6,0),
 \qquad
 U_f\in
 [0.041527012176079285,0.041527012805834346].
\]

The endpoint \(c(U_f)\), including its complete orbit and differentiated
orbit on the 31-node mesh, is the robust fold already certified in
`validation/future-target-fold`.  Along this selected arc the restriction
\(\mathcal E(c(U))\) has no critical point before \(U_f\), and its critical
point at \(U_f\) is unique in the certified terminal cap.  In particular,
this is the first energy fold encountered when the selected arc is followed
from the exact algebraic source.

This statement concerns one selected arc in
\(\mathcal W_{\rm a}\cap\operatorname {Fix}\mathcal R\).  It neither
classifies other arcs or components of that intersection nor asserts that
every reversible source belongs to this arc.

## The exact Jost tangent at the algebraic endpoint

The endpoint tangent is identified analytically; it is not named from a
numerical slope match.

### Lemma (finite-saturation tangent equals the future Jost subspace)

Along the part of the exact algebraic orbit \(\Gamma _0\) contained in the
declared finite saturation, its tangent space is

\[
 T_{\Gamma _0(t)}\mathcal W_{\rm a}
 =\operatorname {span}\{\mathcal T(t),\mathcal Z(t),\mathbf s(t)\}.
\]

Consequently,

\[
 T_{c(0)}\mathcal W_{\rm a}\cap
 T_{c(0)}\operatorname {Fix}\mathcal R
 =\operatorname {span}\{(1,0,-2k_0,0)\},
\]

where

\[
 k_0=\frac{\sqrt\pi\,\Gamma(1/4)}
 {4\sqrt6\,\Gamma(3/4)}.
\]

Thus the canonical source derivative is

\[
 \boxed{V'(0)=-2k_0}.
\]

#### Proof

The exact invariant splitting in
[`LIMITING_JOST_THEORY.md`](../../archive/research-history/papers/paper-a/LIMITING_JOST_THEORY.md)
is

\[
 \operatorname {span}\{\mathbf s\}\oplus
 \operatorname {span}\{\mathcal T,\mathcal Z\}\oplus
 \operatorname {span}\{\mathbf u\}.
\]

The four-rate graph transform certified in `future-target-fold` makes the
linearization of \(\mathcal W_{\rm a}^{\rm tail}\) an invariant rank-three
horizontal graph in the regular weighted frame
\((e,\mathcal A,b_{\rm w},\zeta)\), with uniformly bounded slope
\(\delta\zeta=L(t)(\delta e,\delta\mathcal A,\delta b_{\rm w})\).  This
determines which part of the exact splitting is tangent without using the
computed source slope.

The recessive solution \(\mathbf s\) decays exponentially, \(\mathcal T\)
is polynomial, and the exact algebraic decomposition of \(\mathcal Z\) in
`LIMITING_JOST_THEORY.md` shows that it is at most polynomial after the
weighted coordinate change.  For the remaining solution, put
\(x=t^2/(2\sqrt6)\).  Its positive Bessel representation and the linear
part

\[
 h_7(e,d,\omega)=-e/\sqrt3+\omega/\sqrt2
   +\text{terms of total degree at least two}
\]

give, along \(e=12t^{-2},d=0,\omega=e^2/6\),

\[
 \begin{aligned}
 \delta e_{\mathbf u}
  &=1728\sqrt3\,e^x t^{-9/2}(1+O(t^{-2})),\\
 \delta\mathcal A_{\mathbf u}&=0,\\
 \delta b_{{\rm w},\mathbf u}
  &=-\frac{\sqrt3}{72}e^x t^{11/2}(1+O(t^{-2})),\\
 \delta\zeta_{\mathbf u}
  &=\frac{288\sqrt6}{12^8}e^x t^{27/2}(1+O(t^{-2})).
 \end{aligned}
\]

Thus its normal-to-base ratio is asymptotic to a positive constant times
\(t^8\).  In any variational solution a nonzero constant
growing-\(\mathbf u\) coefficient eventually dominates the other three
components and enters the strict vertical cone, contradicting the tangent
horizontal graph.  Every tangent vector therefore has zero
\(\mathbf u\) coefficient; equality with
\(\operatorname{span}\{\mathcal T,\mathcal Z,\mathbf s\}\) follows from
rank three.  Exact variational pullback through the declared finite tube
then gives the displayed tangent space of \(\mathcal W_{\rm a}\).  Thus the
Jost condition comes from the tail graph and finite flow, not from an
independent tempered boundary condition or from the interval slope check.

At \(t=0\), the exact Cauchy data are

\[
 \begin{aligned}
 \mathcal T(0)&=(0,1,0,0),\\
 \mathcal Z(0)&=(1,0,-2k_0,0),\\
 \mathbf s(0)&=(0,-12B_2k_0,-2B_3,6B_2),
 \end{aligned}
\]

with \(B_2>0\).  If
\(a\mathcal T(0)+b\mathcal Z(0)+d\mathbf s(0)\) has \(P=Q=0\), then the
\(Q\)-equation gives \(d=0\), and the \(P\)-equation then gives \(a=0\).
The intersection is therefore the \(\mathcal Z(0)\)-line, proving the
claim. \(\square\)

`verify_jost_constant.py` independently uses 256-bit directed MPFR
rounding to prove

```text
k0 in [0.53522525701880774, 0.53522525701880797]
-2 k0 in [-1.0704505140376159, -1.0704505140376155].
```

The first tangent Krawczyk image strictly contains the latter interval.  The
interval check therefore identifies the computed tangent with the analytic
Jost line supplied by the lemma.

## Fixed-time formulation and the mixed chart

The regular arc is continued with physical time \(T=15\), divided into 30
segments.  Nodes 0 through 3 use the raw coordinates \((U,P,V,Q)\).  At
time \(t=2\), the exact change of variables

\[
 e=-U^{-1},\quad p=Pe^{3/2},\quad
 d=Qe^{3/2}+\frac2{\sqrt3},\quad
 \omega=1+Ve^2
\]

is applied, and nodes 4 through 30 use \((e,p,d,\omega)\).  The compact
physical-time equations are

\[
 \begin{aligned}
 e'&=p\sqrt e,\\
 p'&=(\tfrac32p^2-\omega)/\sqrt e,\\
 d'&=(\tfrac32p(d-2/\sqrt3)-e)/\sqrt e,\\
 \omega'&=(e(d-2/\sqrt3)+2p(\omega-1))/\sqrt e.
 \end{aligned}
\]

The differentiated equations are included in the 248-dimensional fold
problem.  In raw variables, the terminal tangent has components of order
\(10^3\), so an axis-aligned fixed-time enclosure suffers artificial
terminal amplification.  The exact transition at \(t=2\) places the tail
in its natural compact variables and keeps the terminal tangent of order
one.  This is why the mixed fixed-time cap closes without changing the
orbit, time, or boundary condition.

The terminal equation is

\[
 p-h_7(e,d,\omega)-\eta(e,d,\omega)=0,
\]

uniformly for the predeclared jet bounds

\[
 |\eta|\le2e^8,\qquad
 |D\eta|_\infty\le10^{-5},\qquad
 |D^2\eta|_\infty\le10^{-3}.
\]

No subdivision of the slope cube is used: every ordinary box treats the
whole \(C^1\) cube, and the augmented cap treats the whole \(C^2\) cube.
The future-target construction proves that
\(\mathcal W_{\rm a}^{\rm tail}\) has these bounds on the padded physical
corridor.  Exact finite-flow pullback through \(\mathcal T_{\rm a}\) defines
\(\mathcal W_{\rm a}\), so the terminal graph used by every shooting box is
the same canonical tail graph rather than a separately chosen polynomial
perturbation.

Every ordinary box also proves that its orbit has a unique first entry into
\(e=.06\).  Before the chart switch one has \(U>-1/.06\); afterwards one has
\(e>0\), \(p<0\), a switch value above .06, and a terminal value below .06.
The first-entry time lies in either \([14,14.5]\) or \([14.5,15]\).

## Interval cover and first-fold argument

The main cover contains 17,345 fixed-\(U\) boxes.  All 17,344 adjacent
interfaces are proved by a Krawczyk image at a common parameter lying
strictly inside both full 124-dimensional uniqueness boxes.  Scalar
parameter overlap is never used as a substitute for common-root
containment.

Near the fold, a second 2,002-box cover of half-width \(10^{-8}\) resolves
the sign of

\[
 \frac{d}{dU}\mathcal E(c(U))
 =(-2U^2-2V)\,U_U-2U\,V_U.
\]

Its first box is identified with main-cover box 17,307 by a separate true
common-root Krawczyk bridge.  On the first 1,867 fine boxes the derivative is
strictly negative; the largest verified upper endpoint is

```text
-2.9561716261977677e-5.
```

The final 140 fine boxes, five of which overlap the strict-negative
subcover, begin at

```text
U = 0.04152493249032178,
```

have their complete base and tangent uniqueness boxes strictly inside one
248-dimensional augmented fold domain.  Their parameter cover overlaps the
strict-negative cover by `9.000000178449596e-8`.  Hence every zero of the
energy derivative on the unresolved terminal part of this selected arc is
an augmented zero inside that domain.

The mixed augmented Krawczyk calculation proves a unique zero in the domain,
uniformly over the full target \(C^2\) jet cube.  The complete Krawczyk image
of the previously certified robust fold is transformed to the mixed chart
and lies strictly inside the same domain.  Finally, that robust fold image
lies inside a radius-scale-five replay of the last fixed-\(U\) base and
tangent uniqueness boxes, and its source parameter lies strictly inside the
last parameter interval.  These three full-state identifications show that
the unique augmented zero is the old fold and that the regular fixed-time arc
ends at the same root.

## Numerical margins

The locked clean replay gives:

| gate | result |
|---|---:|
| main boxes / adjacent bridges | 17,345 / 17,344 |
| maximum main base Krawczyk ratio | 0.9346496017290783 |
| maximum main contraction ratio | 0.5879445541958938 |
| maximum main tangent Krawczyk ratio | 0.5630408814315386 |
| minimum main bridge current / next margin | 1.0772801314599769e-9 / 1.0403570778281791e-9 |
| fine boxes / adjacent bridges | 2,002 / 2,001 |
| maximum fine base / tangent ratio | 0.7400311789593388 / 0.009213797245811863 |
| main-to-fine full-state margins | 2.8561634311170243e-9 / 2.8624491838829684e-9 |
| minimum fine-family-to-cap margin | 1.0001554357993005e-9 |
| augmented cap Krawczyk / contraction ratio | 0.912135743122722 / 0.9120134920812052 |
| augmented cap minimum Krawczyk margin | 5.000063524161638e-10 |
| old fold to cap full-state margin | 1.947670835849842e-9 |
| old fold to final fixed-family margin | 6.390445225832979e-9 |
| old fold parameter to final interval margin | 9.683432583562634e-9 |

## Reproduction

Before generating a cover or compiling either probe, `replay.py` performs a
fail-closed preflight against the retained audited toolchain: CAPD source
version `6.1.0` at commit
`731079217a9254ea2948d742df2b170895effe7f`, the
`capd-config --modversion` value, the pkgconf frontend version, the
`libcapd.a` and `libfilib.a` SHA-256 hashes, the FILIB compile/link markers,
and `-frounding-math`.  It also pins Python `3.14.4`, NumPy `2.5.2`, SciPy
`1.18.0`, gmpy2 `2.2.2`, MPFR `4.2.1`, and g++ `15.2.0`.  These values are
written into the rebuilt certificate.

Set `CAPD_CONFIG` to the `capd-config` executable of a FILIB-enabled CAPD
build, then run

```bash
PYTHONDONTWRITEBYTECODE=1 \
  CAPD_CONFIG=/path/to/capd-config \
  python3 replay.py --workers 28
```

The replay regenerates the two floating covers in a temporary directory,
compiles both interval probes from source, runs every box and every adjacent
bridge, checks all three endpoint identifications, rebuilds the deterministic
certificate, and compares it with the committed certificate.  The expected
wall time on the declared 32-thread host is about fifteen minutes.  No GPU,
remote host, or repository-stored bulk artifact is used.

The detailed generated files are intentionally absent from this directory.
Their SHA256 values and all proof margins are recorded in `certificate.json`.
