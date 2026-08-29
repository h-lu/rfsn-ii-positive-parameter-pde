# Frozen v2 Laurent--log pole action tail

The local action calculation closes the mathematical integrability and
moving-cut parts requested from V3(45)--(50), but it gives a strict negative
answer to the separately frozen numerical quality gates.  No parameter,
section, label rectangle, formula, or gate was changed after the first
decision output.

For

\[
 Y=1+h-Dh,\qquad q=W-\ell\epsilon\log\sigma,
\]

the regularized density is exactly

\[
 \rho_{\rm reg}=6\epsilon\delta^3\sigma^{-4}
 \left(Y^2-1+2x_2\sigma^2+4x_3\sigma^3\right)
 -\delta^{-1}q^2.
\]

The symbolic jet calculation cancels every nonintegrable term.  The
authenticated fixed-point image bound from the preceding local-end
certificate then gives, uniformly on the complete v2 box and frozen label
rectangle,

\[
 |\rho_{\rm reg}(\sigma)|
 \le 2.765102554\times10^6
       (1+|\log\sigma|)^2,
 \qquad 0<\sigma\le10^{-12}.
\]

Consequently

\[
 \left|\int_0^{10^{-12}}\rho_{\rm reg}(t)\,dt\right|
 \le 2.491358\times10^{-3}.
\]

These are finite, explicit (C^0) bounds, so density integrability and
existence of the local Laurent--log tail pass.  First label derivatives also
pass.  The tail-derivative upper bounds for ((c_4,Z_0,W_0)) are respectively

\[
 2.492\times10^{-18},\qquad
 6.060\times10^{-11},\qquad
 4.531\times10^{-6}.
\]

The first coarse implementation used the ambient remainder ball (10^{30})
instead of the already authenticated self-map image
(1.041696684\times10^{19}).  That implementation error was corrected and
is disclosed in the result; the frozen data and gates were unchanged.

## Strict negative quality result

The frozen targets (C_0<1000) and tail error (<10^{-6}) are false on the
full label rectangle.  At the declared point

\[
 (r,a_2,\epsilon,Z_0,W_0,c_4)
 =\left(\frac1{50},0,\frac65,-\frac34,0,10^{15}\right),
\]

the interval calculation proves

\[
 \frac{|\rho_{\rm reg}(10^{-12})|}
 {(1+|\log10^{-12}|)^2}>3286.8541
\]

and

\[
 \left|\int_0^{10^{-12}}\rho_{\rm reg}(t)\,dt\right|
 >2.7642403\times10^{-6}.
\]

The unique dominant obstruction is the root-four contribution

\[
 -36\epsilon\delta^3c_4
\]

in the integrable (sigma^0) density coefficient.  It is not a failure of
the Fuchsian remainder or of Laurent--log subtraction.  The label rectangle
was intentionally broad, and the one-shot rule forbids shrinking it or
loosening the quality gates after this result.

For any two cuts using the same physical (sigma), (F_{\rm div}), and
local tail, those common terms cancel.  Ordinary line-integral additivity
therefore gives exactly

\[
 \mathscr A_{{\rm fp},C_0}
 =\int_{C_0}^{C_1}\lambda_\delta+\mathscr A_{{\rm fp},C_1}.
\]

Thus the moving-cut identity passes exactly.  The parent `V3.POLE_TAIL`
remains `INCONCLUSIVE`: mixed external-parameter (C^2) bounds and global
arrival in the label rectangle are still absent, and the frozen action
quality gates have the strict counterexample above.

Reproduce with

```bash
python3 -B validation/rigorous/p3_pole_action_tail_v2.py --check
python3 -m unittest validation.rigorous.tests.test_p3_pole_action_tail_v2 -v
```
