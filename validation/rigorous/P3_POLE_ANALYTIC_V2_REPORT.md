# V3 positive-pole analytic audit on the frozen v2 box

This audit isolates what can already be closed exactly in Theorem V3 from
what still requires interval flow and regular-singular remainder bounds.  Its
result is `PARTIAL_ANALYTIC_PASS`, while both registered parent obligations
remain `INCONCLUSIVE`.

The non-explicit choices in the proof have the following precise status.

| V3 proof choice | Computable condition | v2 status |
|---|---|---|
| Radius choice in (1) | the two displayed scalar inequalities | `PASS` |
| Gate collar and short slide in (15a)--(16) | all-window pre-hit sign, hit speed, entry state and event buffer | `PENDING` |
| Positive (b) and finite time in (17)--(18) | (b\ge1/33750), followed by the comparison below | conditional `PASS` |
| Label rectangles and (K_{c_4}) in Sections 4--5 | interval bounds for (Z_0,W_0,c_4) | `PENDING` |
| Small \(\sigma_0\) in the Green/Volterra contraction | explicit operator, nonlinear and mixed-jet constants with norm (<1) | `PENDING` |
| Small \(\sigma_*\) and the coordinate inverse | full determinant lower bound including the remainder | `PENDING` |
| Large common section (x=M) in Section 6 | whole gate image inside one finite local pole atlas | `PENDING` |
| Action (O_{C^2}) remainder in Section 7 | integrable density constant and tail error | `PENDING` |

## What closes on the whole box

The frozen target is exactly the positive box used in the V3 theorem with

\[
 A=\frac14,\qquad r_{\rm p}=\frac1{50},\qquad
 r\in\left[\frac12r_{\rm p},r_{\rm p}\right].
\]

Using the exact rational brackets

\[
 \frac89\le\sqrt\epsilon\le\frac{11}{10},\qquad
 \frac{12}{5}\le\sqrt6\le\frac52,
\]

the two explicit radius hypotheses in V3(1) have lower margins

\[
 \frac14-\sqrt{\epsilon_+}Ar_{\rm p}^3
 \ge \frac{1249989}{5000000},
\]

and

\[
 1-\left(2Ar_{\rm p}+\sqrt{\epsilon_+}A^2r_{\rm p}^4\right)
 \ge\frac{989999989}{1000000000}.
\]

Thus the coefficient reductions used by the pole cone are uniform:

\[
 B-\frac12\ge\frac{2499989}{5000000},\qquad
 |c|\le\frac{10000011}{10^9},\qquad
 b\ge\frac1{33750}>0.
\]

On the complete cone (x\ge10, y>0, D\ge0, K\ge0), the coarse
inequalities actually used in the paper give

\[
 y'\ge\frac{2029}{135}>0,qquad
 K'\ge\frac{3788}{27}>0
\]

at the worst boundary point.  Hence cone invariance is no longer hidden
behind a “sufficiently small” radius choice on this box.

There is also a useful exact conditional result.  If an interval event tube
supplies the paper's gate state inequalities

\[
 x=10,quad y\ge13,quad D\ge26,quad K\ge131,
\]

then the actual v2 coefficient bounds imply

\[
 y'\ge75.9294095\ldots>51,qquad
 K'\ge918.2940951\ldots>852.
\]

Moreover equation (17) yields, for every later (x\ge10),

\[
 y(x)^2\ge \frac{x^4}{67500}+\frac{4559}{27}
 >\frac{x^4}{260^2}.
\]

Consequently the remaining central time is less than (260/x), and the
remaining physical time from the gate is uniformly less than

\[
 \frac1{50}\frac{16}{15}\,26=\frac{208}{375}.
\]

This proves finite-time pole formation from the stated cone entry.  It does
not prove that the source family reaches that entry.

At the exact-formula level the regular-singular boundary spectrum remains

\[
 \{-1,-4,0,0,1\},
\]

and on the v2 box

\[
 \left|\partial_{c_4}\mathcal G\right|
 =30\epsilon\delta^4\ge\frac3{1250000000000000}>0,
\]

while the leading coordinate determinant satisfies

\[
 5\ell^2\delta=30\delta^3\ge\frac3{10^{11}}>0.
\]

These are exact structural and transversality facts.  The second inequality
does not yet control the `o(1)` term in the full coordinate determinant.

## What remains genuinely missing

`V3.SOURCE_TO_POLE` needs one gap-free interval cover of the complete source
window and parameter box.  It must prove strict pre-hit sign, unique first
hit of (x=10), positive hit speed, and the lower bounds
(y\ge13,D\ge26,K\ge131), with mixed parameter/phase two-jets.  The current
single-point scout at ((3/200,0,1)) reaches the gate with sampled
(y\approx27.14,D\approx53.46,K\approx270.85); that is useful feasibility
evidence but enters no PASS decision.

`V3.POLE_TAIL` additionally needs an explicit downstream section and a
validated local end block: bounded rectangles for (Z_0,W_0,c_4), a numeric
\(\sigma_0\), contraction and conormal remainder constants through mixed
external order two, a positive full Jacobian bound after the remainder, and
an integrable action-density remainder with a tail-error bound.  The paper's
existential choices of the label rectangles, (K_{c_4}), \(\sigma_0\), and
the large section (M) do not provide those numbers.

Thus the event entry is not the only Issue #7 gap: it is the first global
interface, and the explicit regular-singular remainder block is the second.
No V3 parent claim, V4--V6 claim, or action finite-part enclosure is asserted.

Reproduce the exact audit with

```bash
python3 -B validation/rigorous/p3_pole_analytic_v2.py --check
python3 -m unittest validation.rigorous.tests.test_p3_pole_analytic_v2 -v
```
