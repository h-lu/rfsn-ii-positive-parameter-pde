# P2d zero-energy fiber report

**Local mathematical status:** `PASS` for `V2.CHART.ZERO_ENERGY`.

**Aggregate status:** `INCONCLUSIVE`; `claim_bearing=false`;
`release_eligible=false`; independent replay remains `1/2`;
`V2.EXACT_CHART=OPEN`.

This stage is a rational consequence of the already authenticated P2d frame
and analytic normal form.  It does not introduce a new C++/CAPD lane, a new
certificate schema, or a second-machine replay mechanism.

## Evidence chain

1. The archived P2d frame certificate has SHA-256
   `5fabbcf01dc9b2f818f34525010332c76ff40190ea9a3d5ab166072397397847`
   and locally passes `V2.CHART.SYMPLECTIC_FRAME`.
2. The analytic normal-form proof contract has SHA-256
   `069d109a22fa502c2e6970de7e3ef4c60234e327138b9052df764b6f36cf8245`;
   its authenticated source checker and the 26-check exact audit locally pass
   `V2.CHART.ANALYTIC_NORMAL_FORM`.
3. [`EXPLICIT_ZERO_ENERGY_FIBER.md`](../../theory/EXPLICIT_ZERO_ENERGY_FIBER.md)
   proves contract `rfsn-vdp-p2d-explicit-zero-energy-fiber/1`.  Its SHA-256
   is
   `ac1cac62e56acf59e2ae2bfb79ae10730756673bf86775d50c8196d47c2c3342`.
4. [`check_p2d_zero_energy.py`](check_p2d_zero_energy.py) authenticates those
   inputs, reads the outward binary64 frame hulls as exact rationals, and
   verifies the action-domain, orientation, Krawczyk, mixed-jet, and Cauchy
   gates without floating-point decisions.

## Certified fiber

On the complete normalized parameter bridge

\[
 0\le r\le\frac2{25},\qquad |a_2|\le\frac14,\qquad
 \frac45\le\epsilon\le\frac65,
\]

the nonlinear Kato normal form has one analytic zero-energy fiber

\[
 I_1=q_\mu(\nu),\qquad \nu=I_2^{\rm K},qquad
 |\nu|\le\nu_*:=\frac{25}{2^{54}}.
\]

It satisfies

\[
 h_\mu(q_\mu(\nu),\nu)=0,qquad
 q_\mu(0)=0,qquad
 q_\mu'(0)=-\frac{\beta_\mu}{\alpha_\mu},
\]

and

\[
 \partial_{I_1}h_\mu(q_\mu(\nu),\nu)>\frac23.
\]

The interval is common, nonzero, and two-sided.  The Krawczyk argument is
performed on the larger complex disk

\[
 |\nu|\le\nu_{\rm out}:=\frac{25}{2^{53}},
\]

leaving a Cauchy gap equal to \(\nu_*\).

## Exact gates

The state-to-action majorant is controlled on
\(\mathcal D_\infty=\Delta_{5/2^{25}}\) and gives

\[
 s=\frac{25}{2^{50}},\qquad
 \overline M=\frac1{3\,2^{62}},\qquad
 \sup|\partial_{I_1}N|\le\frac1{153600}.
\]

The archived frame hulls verify

\[
 \alpha\ge\frac7{10},\qquad |\beta|\le\frac{18}{25},
\]

and bound every individual normalized first and second parameter derivative
of \(\alpha,\beta\) by \(1/100\).  The resulting orientation lower bound is
approximately `0.6999934896`.  On the complex fiber box this is first a
nonvanishing modulus bound; on the real fiber it is the displayed oriented
positive derivative.

With the linear center \(c=-(\beta/\alpha)\nu\), the common Krawczyk radius
is approximately `2.065147e-19`; the Krawczyk image radius is approximately
`1.032593e-19`, strictly less than the former.  The complete fiber box has
action radius approximately `2.855066e-15`, strictly inside the certified
inner action domain.  More importantly, its actions satisfy

\[
 \max(|J_1|,|J_2|)
 \le\frac{Q_0+\nu_{\rm out}}2
 =\frac{19475}{3\,2^{61}}
 <\frac9{2^{50}}.
\]

Thus the complete fiber box lifts strictly into the smaller exact-conjugacy
domain \(\mathcal D_{\rm src}=\Delta_{3/2^{25}}\); the majorant domain and
the exact chart domain are not conflated.

## Mixed derivatives

The outer-disk implicit estimates are

\[
 Q_0\approx2.855066\times10^{-15},\qquad
 Q_1\approx8.456777\times10^{-17},\qquad
 Q_2\approx8.721489\times10^{-17}.
\]

For every normalized parameter multi-index \(|\gamma|=j\le2\), every fixed
finite \(m\ge0\), and \(|\nu|\le\nu_*\), the checker records the exact
rational rule

\[
 |D_\theta^\gamma D_\nu^m q_\mu(\nu)|
 \le \frac{m!Q_j}{\nu_*^m}.
\]

It explicitly emits the complete table through \(m=3\).  Original parameter
derivatives use the exact factor
\(25^{\gamma_r}4^{\gamma_a}5^{\gamma_\epsilon}\).

## Current repository chart status

The zero-energy checker itself is deliberately scoped and therefore reports
downstream children as `OPEN`.  The separately bound exact-sections and
weighted-passage artifacts have since supplied the fourth and fifth local
child passes recorded here.

```text
V2.CHART.SYMPLECTIC_FRAME       PASS
V2.CHART.ANALYTIC_NORMAL_FORM   PASS
V2.CHART.ZERO_ENERGY            PASS
V2.CHART.EXACT_SECTIONS         PASS
V2.CHART.WEIGHTED_PASSAGE       PASS
V2.CHART.PHYSICAL_SLIDES        OPEN
V2.CHART.OVERLAPS               OPEN
V2.EXACT_CHART                  OPEN
```

The next mathematical gate is `V2.CHART.PHYSICAL_SLIDES`; see
[`P2D_EXACT_SECTIONS_REPORT.md`](P2D_EXACT_SECTIONS_REPORT.md) and
[`P2D_WEIGHTED_PASSAGE_REPORT.md`](P2D_WEIGHTED_PASSAGE_REPORT.md) for the
intervening local passes.

## Claim boundary

This local child pass alone does not prove the exact nonlinear radial
sections or weighted passage; those are supplied by the separately bound
artifacts just cited.  It does not prove physical slides, overlap atlas,
compact event atlas, positive ends, exhaustive V6 census, temporal stability,
Turing selection, or canard identification.  It does not alter any historical
frame certificate.  Repository-level claim-bearing status remains unavailable
until every required child and the independent replay policy pass.

## Reproduction

```bash
python3 -B validation/rigorous/check_p2d_zero_energy.py
python3 -B -m unittest \
  validation.rigorous.tests.test_p2d_zero_energy -v
```

The checker emits one canonical JSON line.  A proof-contract digest mismatch
leaves the rational source gates visible, returns the zero-energy atom to
`OPEN`, reports top-level `INCONCLUSIVE`, and exits nonzero.
