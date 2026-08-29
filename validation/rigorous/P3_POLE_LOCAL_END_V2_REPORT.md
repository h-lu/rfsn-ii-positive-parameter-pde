# Frozen v2 regular-singular pole end block

The one-shot frozen block at

\[
 \sigma_0=10^{-12},\qquad
 Z_0\in[-1,-1/2],\quad W_0\in[-1/4,1/4],\quad
 c_4\in[0,10^{15}]
\]

passes the requested local (C^0) self-map, contraction, label-(C^1), and
full physical coordinate-Jacobian tests.  It is a genuine local result on the
entire v2 parameter box and the entire frozen label rectangle; it is not a
source-to-pole arrival result.

The displayed resonant jet was inserted symbolically into the exact scalar
Fuchsian equation.  All terms below order
\(\sigma^5(1+|\log\sigma|)^2\) cancel exactly.  The remaining finite
Laurent-log polynomial is bounded using exact rational interval arithmetic.
The Green operator has the analytic norm bound

\[
 \|\mathscr K\|\le \frac{103}{108}<1
\]

in the frozen weighted (C^0) norm; the certificate uses the simpler upper
bound one.  The exact `atanh` series for
\(\log 10=2\operatorname{atanh}(9/11)\) encloses the only transcendental
quantity at the section.

The resulting normalized residual is at most
\(1.041666684\times10^{19}\).  Against the frozen weighted radius
\(10^{30}\), the full self-map right side is at most
\(1.041696684\times10^{19}\), and the contraction constant is at most

\[
 3.000000013\times10^{-16}<\frac12.
\]

Although the weighted radius looks large, at the frozen section it means

\[
 |R(\sigma_0)|
 \le 10^{30}\sigma_0^5(1+|\log\sigma_0|)^2
 <8.41\times10^{-28}.
\]

Differentiating the fixed-point equation in (c_4,Z_0,W_0) gives explicit
first-label-derivative bounds with the same contraction denominator.  After
including those remainder bounds, the complete physical Jacobian satisfies

\[
 \frac{\det D_{(\sigma,c_4,Z_0,W_0)}(u,p,v,q)}{\ell^2\delta}
 \in[4.99999999999924,5.00000000000076].
\]

Thus it is uniformly nonzero, not merely nonzero at leading order.

Two different spectra occur here.  The desingularized-flow spectrum is

\[
 \{-1,-4,0,0,+1\},
\]

while the normalized power spectrum is

\[
 \{-1,0,0,1,4\}.
\]

They are related by \(\lambda\mapsto\sigma^{-\lambda}\); the admissible
positive power roots are (1,4).

This result remains partial.  It does not prove that the global V2 source
image arrives in the frozen label rectangle.  It also does not yet enclose
mixed parameter two-jets or the (C^2) action-density remainder.  Therefore
both registered parent obligations `V3.SOURCE_TO_POLE` and `V3.POLE_TAIL`
remain `INCONCLUSIVE`.

Reproduce with

```bash
python3 -B validation/rigorous/p3_pole_local_end_v2.py --check
python3 -m unittest validation.rigorous.tests.test_p3_pole_local_end_v2 -v
```
