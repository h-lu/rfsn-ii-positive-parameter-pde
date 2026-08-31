# V4 zero-energy corridor and cone probe

**Result:** local mathematical `PASS` on the complete frozen v2 parameter
box.  This is a current-computer, non-claim-bearing interval probe of the
$E=0$ slice only.

## Verified object

The probe evaluates the exact compactified field from
[`OUTER_FUTURE_STAYING.md`](../../van-der-pol/OUTER_FUTURE_STAYING.md),
equations (14)--(21), on

\[
 r\in[1/100,1/50],\quad a_2\in[-1/4,1/4],\quad
 \epsilon\in[4/5,6/5],
\]

and

\[
 E=0,\qquad z\in[0,1/5],\qquad
 |\beta|,|\alpha|\le10^{-5}.
\]

Writing $w=\alpha-\beta$, $s=\alpha+\beta$, and
$\pi=\delta\chi+s$, the energy identity becomes

\[
 A\chi^2-2b\chi-D=0,
 \qquad
 \chi_+=\frac{b+\sqrt{b^2+AD}}{A}.
\]

Here $b^2+AD$ is the quarter-discriminant; the standard quadratic
discriminant is $4(b^2+AD)$.  Outward-rounded bounds prove $A>0$, $D>0$,
a positive quarter-discriminant, one negative root, one regular positive
root $\chi_+$, and $\pi>0$.  The implicit derivative
$\partial_\chi(A\chi^2-2b\chi-D)=2\sqrt{b^2+AD}$ at $\chi_+$ is uniformly
positive.

The product cover uses the frozen $4\times8\times4$ parameter parents and
64 exact-rational $z$-slabs, for 8,192 cells.  No sampled point enters a
PASS decision.

## Uniform margins

| Quantity | Rigorous bound |
|---|---:|
| $A$ | $\ge 0.9999999996928$ |
| $D$ | $\ge 0.2550074206726621$ |
| $\chi_+$ | $[0.5049825944126813, 0.7745967165201608]$ |
| $2\sqrt{b^2+AD}$ | $\ge 1.0099651885696266$ |
| $\pi$ | $\ge 3.0498275937393915\times10^{-5}$ |
| inward $z=1/5$ margin | $\ge 2.4445380404017295\times10^{-7}$ |
| inward $\beta=+10^{-5}$ margin | $\ge 4.347768765669677\times10^{-6}$ |
| inward $\beta=-10^{-5}$ margin | $\ge 9.999999999999997\times10^{-6}$ |
| exit $\alpha=+10^{-5}$ margin | $\ge 4.34723636380015\times10^{-6}$ |
| exit $\alpha=-10^{-5}$ margin | $\ge 9.999999999999997\times10^{-6}$ |

On the invariant slice the graph base is $X=(z,\beta)$, not
$(z,E,\beta)$.  For the generator splitting

\[
 DY=\begin{pmatrix}C&B\\D&a_{\rm n}\end{pmatrix}
\]

relative to $X\oplus\alpha$, the probe obtains

\[
 \mu_2(C)\le0.003995712743350482,
 \quad \|B\|\le0.021555696677199393,
 \quad \|D\|\le0.019997965892632696,
 \quad a_{\rm n}\ge0.9799995150220824.
\]

All four required comparisons with $\nu=1/32$ are strict.  The resulting
slope-one cone margin is at least 0.9344595433623469; the normal rate is
at least 0.9584458814074024; and the generator bunching gaps are

\[
 (\gamma_0,\gamma_1,\gamma_2,\gamma_3)
 \ge(0.9584458814, 0.9329112162, 0.9073692105, 0.8818272047).
\]

Thus the explicit zero-energy corridor satisfies the quantitative
face/cone/rate mechanism used in V4, uniformly over the whole v2 parameter
box.

The positive square-root formula is smooth jointly in the slice variables
and parameters on this verified corridor.  Therefore the corridor graph
lemma in `OUTER_FUTURE_STAYING.md`, applied with base $X=(z,\beta)$, now
gives a unique locally maximal future-staying graph

\[
 \alpha=\Gamma^0_\mu(z,\beta)
\]

on $E=0$, normally expanding and third-order bunched, with the lemma's
mixed total-order-three regularity.  This is the mathematical consequence
of the four validated obligations; it is stronger than the earlier
finite-horizon slice plots but strictly weaker than full V4.

## Reproduction and claim boundary

The source is
[`vdp_v4_zero_energy_graph_probe.cpp`](src/vdp_v4_zero_energy_graph_probe.cpp)
and its compiled-output checks are in
[`test_v4_zero_energy_graph_probe.py`](tests/test_v4_zero_energy_graph_probe.py).
Run

```bash
python3 -B -m unittest \
  validation.rigorous.tests.test_v4_zero_energy_graph_probe -v
```

with the pinned strict CAPD/FILIB build, or set `RFSN_CAPD_CONFIG` to its
`capd-config`.  The strict local run passes the rounding self-test and all
four mathematical obligations.

The machine field `claim_bearing=false` records that this scoped local result
is not an Issue #7 release certificate for the complete V4 object; it does
not negate the zero-energy graph conclusion above.

This result does **not** enclose an $E$-collar and therefore is not a
certificate for the complete three-dimensional-base `V4.OUTER_GRAPH`.
It also does not validate the V5 central--outer seam, select a matched
algebraic source orbit, or prove the full asymptotic tail and finite parts.
