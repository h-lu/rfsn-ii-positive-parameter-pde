# P2d weighted Kato-passage report

**Local mathematical status:** `PASS` for
`V2.CHART.WEIGHTED_PASSAGE`.

**Aggregate status:** `INCONCLUSIVE`; `claim_bearing=false`;
`release_eligible=false`; independent replay remains `1/2`;
`V2.EXACT_CHART=OPEN`.

## Evidence chain

1. The symplectic frame, analytic normal form, nonlinear zero-energy fiber,
   and exact radial sections have separately proof-bound local passes.
2. The authenticated 59-check exact-chart audit fixes the action convention,
   positive angular speed, negative logarithmic phase slope, and linear clock.
3. The separately hash-bound P2bK exact audit supplies the checked identity
   `alpha_beta_spectral_relations`, hence
   \(\alpha_\mu^2+\beta_\mu^2=1\).
4. [`EXPLICIT_WEIGHTED_KATO_PASSAGE.md`](../../theory/EXPLICIT_WEIGHTED_KATO_PASSAGE.md)
   proves contract `rfsn-vdp-p2d-explicit-weighted-kato-passage/1`; its
   SHA-256 is
   `78023f2c1511b2037b07ad9fa6a70504abb8734ee9f73103a00634c91f315f1c`.
5. [`check_p2d_weighted_passage.py`](check_p2d_weighted_passage.py)
   authenticates that chain and checks every new domain, branch, Cauchy,
   clock, and status gate with exact rational arithmetic.

## Passage laws

On the complete normalized parameter bridge, both signs, and

\[
 0<|\nu|\le\nu_{\rm p}:=\frac{25}{2^{58}},
\]

the exact auxiliary radial passage satisfies

\[
 \begin{aligned}
 T_\mu(\nu)
 &=-\alpha_\mu^{-1}\log|\nu|+t^\mathrm K_\mu
   +\tau^\mathrm K_\mu(\nu),\\
 \Delta_{\mu,\sigma}(\nu)
 &=-\frac{\beta_\mu}{\alpha_\mu}\log|\nu|
   +b^\mathrm K_{\mu,\sigma}
   +\rho^\mathrm K_{\mu,\sigma}(\nu).
 \end{aligned}
\]

The negative phase sign comes from the positive Kato angular speed and the
explicit radial flow.  The same signed action
\(I_2^{\rm K}=\nu\) is preserved exactly.

The branch construction uses the larger analytic disk
\(R=25/2^{57}\).  There

\[
 |p(\nu)-p(0)|\le\frac{79}{1152}<\frac18,
 \qquad p=q/\nu,
\]

and the relative variation of \(1+p^2\) is less than \(1/10\).  Hence the
two logarithms and both lifted argument branches are defined without a
floating phase decision.  On the real slice \(p\le-105/128<0\), and the
absolute positive-Kato deck is frozen by

\[
 \gamma_{\mu,+}=-\pi+\arctan(\alpha_\mu/\beta_\mu),\qquad
 \gamma_{\mu,-}=\arctan(\alpha_\mu/\beta_\mu).
\]

Thus \(|\arg_\sigma|<\pi<4\); no hidden \(2\pi\) shift enters the winding
constant.

## Weighted generator and parameter rectangle

For every fixed finite \(m\ge0\), the checker implements the finite
Stirling-number generator from the proof and returns

\[
 \nu_{*,m}=\frac{25}{2^{58}},\qquad C_m<\infty.
\]

It proves the bound required in Theorem V2(3) for every
\(D_\mu^{|\ell|\le2}D_{\log\nu}^j\), \(0\le j\le m\).  The table through
\(m=3\) contains all pure and cross second derivatives in the original
parameters \((r,a_2,\epsilon)\), not only normalized or total-order
derivatives.  The first four exact logarithmic Cauchy weights are

\[
 1,\quad2,\quad6,\quad26,
\]

and the emitted order-seven witness is `94586`.  This executable recurrence,
not the finite table, discharges the all-finite-order quantifier.  The
generator explicitly doubles the individual analytic envelopes when they
are used for centered differences, including the parameter derivatives of
the lifted-argument variation.

## Clock inversion and downstream signs

The sharp local estimates are

\[
 |\tau^\mathrm K|<\frac1{16},
 \qquad
 |\alpha D_{\log\nu}\tau^\mathrm K|<\frac1{16}.
\]

These constants use \(|F(\nu)|\le K|\nu|\) for every centered factor and the
monotonicity of \(x|\log x|\).  The numbers 58 and 59 are endpoint weights;
they are not a false uniform bound on \(|\log|\nu||\) in the punctured collar.

The same exact clock constant gives

\[
 c^\mathrm K_\mu=e^{\alpha_\mu t^\mathrm K_\mu}
 =\alpha_\mu\rho_0^2
 \ge c_*:=\frac{35}{2^{53}}.
\]

For \(0\le\theta<2\pi\) (with estimates valid at the closed endpoint), both
signs, and every integer \(n\ge2\), the
positive clock equation has one unique signed root.  Its uniform upper bound
is a rational prefactor times \(16^{-n}\); at \(n=2\), the bound is only
\(12/61\) of the validated passage radius.  The checker also emits exact
first- and second-derivative polynomial generators for the root.

The downstream dictionary is therefore fixed as

\[
 \widetilde b^\mathrm K=b^\mathrm K-\beta t^\mathrm K
 =\gamma_{\mu,\sigma},
 \qquad
 \varrho^\mathrm K=\rho^\mathrm K(\nu_n)
 -\beta\tau^\mathrm K(\nu_n),
\]

with limiting phase
\(\phi+\theta+\widetilde b^\mathrm K\), finite matching row

\[
 \psi-\phi-\theta-\widetilde b^\mathrm K-\varrho^\mathrm K=0,
\]

and an explicit original-parameter \(C^2\) bound of the form
\(C_\varrho(n+1)^3 16^{-n}\).

## Current chart status

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

The next mathematical gate is `V2.CHART.PHYSICAL_SLIDES`.

## Claim boundary

The local radial passage gives a turn-count/time comparison with constant
two.  The physical saddle-block residence time also contains the incoming
and outgoing finite slide times.  Its comparison remains open until those
slides are validated; this report does not silently close that later gate.
It also proves no overlap atlas, event atlas, positive end, temporal
stability, Turing selection, or canard identification.

## Reproduction

```bash
python3 -B validation/rigorous/check_p2d_weighted_passage.py
python3 -B -m unittest \
  validation.rigorous.tests.test_p2d_weighted_passage -v
```

The checker emits one canonical JSON line.  A proof mismatch leaves valid
rational source gates visible, returns the local atom to `OPEN`, reports
`INCONCLUSIVE`, and exits one.  Malformed or unauthenticated input is
`INPUT_REJECTED` with exit two.
