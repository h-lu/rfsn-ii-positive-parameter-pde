# V4 full-energy outer graph interval proof

**Result:** local mathematical **PASS** on the complete frozen v2 parameter
box. This is a current-computer, non-claim-bearing interval proof of an
explicit full-energy V4 corridor.

## Verified object

The probe evaluates the exact compactified field from
[OUTER_FUTURE_STAYING.md](../../van-der-pol/OUTER_FUTURE_STAYING.md),
equations (14)--(21), on

\[
 r\in[1/100,1/50],\quad a_2\in[-1/4,1/4],\quad
 \epsilon\in[4/5,6/5],
\]

and on the newly declared application corridor

\[
 |E|\le1/1000,\qquad 0\le z\le2/9,\qquad
 |\beta|,|\alpha|\le10^{-5}.
\]

The value \(E_0=1/1000\) is an explicit constant selected in this
application repository, not a constant imported from the flagship theorem.
It contains the scaled range used by the existing V5 energy-sensitivity
diagnostic: if \(|H|\le10^6\), then on the full v2 box

\[
 |E|=\epsilon^{5/2}r^6|H|
 \le \frac{198}{125}\,50^{-6}\,10^6
 =\frac{198}{1953125}<\frac1{1000}.
\]

This comparison is only on the V4 energy coordinate. It does not turn the
large floating \(H\)-difference step into a validated resolved-\(K_1\)
energy collar.

The outer cut used by the V5 predictors has \(R=2\), hence
\(z_R=(1+4\sqrt\epsilon)^{-1}\). Since
\(4/5>49/64\), one has \(\sqrt\epsilon>7/8\) and therefore
\(z_R<2/9\) throughout the v2 box. The strict V4 corridor consequently
contains the \(z\)-location of that parameter-dependent cut and covers its
intersection with the displayed \((E,\beta,\alpha)\) collar; it is not
silently replaced by the center-only shorthand \(Q=25\). In particular, the
older floating candidate in
`numerics/results/vdp_v1_v7/v4_v5_matched_candidate.json`, with
\(|\alpha|,|\beta|\simeq 7.8\times10^{-5}\), lies outside this
\(10^{-5}\) collar. Its V5 incidence is therefore not certified here.

Writing \(w=\alpha-\beta\), \(s=\alpha+\beta\), and
\(\pi=\delta\chi+s\), the energy identity becomes

\[
 A\chi^2-2b\chi-D=0,
 \qquad
 \chi_+=\frac{b+\sqrt{b^2+AD}}{A}.
\]

Here \(b^2+AD\) is the quarter-discriminant. Outward-rounded bounds prove
\(A>0\), \(D>0\), one negative root, one regular positive root
\(\chi_+\), and \(\pi>0\). The implicit derivative at the positive root is
\(2\sqrt{b^2+AD}>0\).

The gap-free product cover uses the frozen \(4\times8\times4\) parameter
parents, the two exact energy slabs
\([-1/1000,0]\), \([0,1/1000]\), and 64 exact-rational \(z\)-slabs. Thus
all 16,384 cells are evaluated by interval arithmetic; no sampled point
enters a PASS decision.

## Uniform margins

| Quantity | Rigorous bound |
|---|---:|
| \(A\) | \(\ge0.9999999995317786\) |
| \(D\) | \(\ge0.23713404462603768\) |
| \(\chi_+\) | \([0.48696411018384606,0.7745967340956351]\) |
| \(2\sqrt{b^2+AD}\) | \(\ge0.9739282202354838\) |
| \(\pi\) | \(\ge2.869642993236748\times10^{-5}\) |
| inward \(z=2/9\) margin | \(\ge3.158249826823556\times10^{-7}\) |
| inward \(\beta=+10^{-5}\) margin | \(\ge3.1713912171582626\times10^{-6}\) |
| inward \(\beta=-10^{-5}\) margin | \(\ge9.999999999999997\times10^{-6}\) |
| exit \(\alpha=+10^{-5}\) margin | \(\ge3.1706289643111917\times10^{-6}\) |
| exit \(\alpha=-10^{-5}\) margin | \(\ge9.999999999999997\times10^{-6}\) |

For the full graph base \(X=(z,E,\beta)\), the generator splitting

\[
 DY=\begin{pmatrix}C&B\\D&a_{\rm n}\end{pmatrix}
\]

satisfies

\[
 \mu_2(C)\le0.0054827859197928265,\qquad
 \|B\|\le0.027037942327639567,
\]
\[
 \|D\|\le0.024689034553742637,\qquad
 a_{\rm n}\ge0.9753080249069818.
\]

All four comparisons with \(\nu=1/32\) are strict. The resulting
slope-one cone margin is at least \(0.9181093330361222\), the normal rate
is at least \(0.9482725777780716\), and

\[
 (\gamma_0,\gamma_1,\gamma_2,\gamma_3)
 \ge(0.9482725778,0.9157714962,0.8832618389,0.8507521816).
\]

The same block bounds give the sharper invariant graph-slope cone

\[
 \|D_{(z,E,\beta)}\Gamma_\mu\|\le\kappa,
 \qquad \kappa=\frac1{32}.
\]

Indeed, the outward-rounded lower bound for

\[
 \kappa\{a_{\rm n}-\mu_2(C)-\|B\|\kappa\}-\|D\|
\]

is \(0.005591599924052667>0\). Thus the boundary of the
\(\kappa\)-projectivized cone is strictly inward on every cell. This sharper
slope is the useful output for transporting the graph conormal toward the
resolved \(K_1\) matching problem; it still does not perform that transport.

The root formula is smooth jointly in state and parameters on this
corridor. The proved corridor graph lemma therefore gives a unique locally
maximal graph

\[
 \alpha=\Gamma_\mu(z,E,\beta)
\]

on the full displayed corridor, normally expanding and third-order bunched,
with the mixed total-order-three regularity stated in V4. The analytic
argument in Section 6 of the source theorem then gives the orbitwise
algebraic asymptotics and infinite physical distance. Thus the local
mathematical obligation **V4.OUTER_GRAPH** is closed on the v2 box.

## Reproduction and claim boundary

The source is
[vdp_v4_outer_graph_probe.cpp](src/vdp_v4_outer_graph_probe.cpp), and its
compiled-output checks are in
[test_v4_outer_graph_probe.py](tests/test_v4_outer_graph_probe.py). Run

    python3 -B -m unittest \
      validation.rigorous.tests.test_v4_outer_graph_probe -v

with the pinned strict CAPD/FILIB build, or set RFSN_CAPD_CONFIG to its
capd-config. The strict run passes the rounding self-test and all five
mathematical obligations.

The machine field **claim_bearing=false** records that this local result is
not yet the aggregate Issue #7 release certificate. It does not weaken the
full-corridor conclusion above. The calculation does not validate V5
central--outer incidence, exchange or inverse bounds, select a matched source
orbit, construct the outer action finite part, or satisfy the independent
release-replay policy.
