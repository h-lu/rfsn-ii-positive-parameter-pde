# P2d analytic normal-form report

**Local mathematical status:** `PASS` for
`V2.CHART.ANALYTIC_NORMAL_FORM`.

**Aggregate status:** `INCONCLUSIVE`; `claim_bearing=false`;
`V2.EXACT_CHART=OPEN`.  Independent replay remains one of the two machines
required by the repository release policy.

This report supersedes the status, but not the historical content, of
[`P2D_NORMAL_FORM_DESIGN_REPORT.md`](P2D_NORMAL_FORM_DESIGN_REPORT.md).  The
older exact prefix and design scout did not close an atom by themselves.  The
local pass recorded here comes from the complete analytic proof plus the
source-bound run described below.

## Bound evidence chain

1. The archived P2d frame certificate
   [`results/vdp_bridge_v1_p2d_symplectic_frame.json`](results/vdp_bridge_v1_p2d_symplectic_frame.json)
   has SHA-256
   `5fabbcf01dc9b2f818f34525010332c76ff40190ea9a3d5ab166072397397847`.
   Its outward-rounded probe covers the gap-free
   (16\times8\times4=512) parameter cells and supplies the value, three
   first derivatives, and six symmetric second derivatives of
   \(\alpha,\beta,L,L^{-1}\).
2. [`audit_p2d_normal_form_exact.py`](audit_p2d_normal_form_exact.py) passes
   26 deterministic exact checks for the fixed complex dictionary and the
   normalized \(q=1,2\) Lie prefix.
3. [`EXPLICIT_GLOBAL_MOSER_MAJORANT.md`](../../theory/EXPLICIT_GLOBAL_MOSER_MAJORANT.md)
   proves contract
   `rfsn-vdp-p2d-explicit-global-moser-majorant/1`.  Its bound SHA-256 is
   `069d109a22fa502c2e6970de7e3ef4c60234e327138b9052df764b6f36cf8245`.
   The proof includes the all-orders \(J^2\) Giorgilli recurrence, explicit
   source and inverse domains, joint state--parameter \(C^2\) tails, and the
   normalized exact primitive.
4. [`check_p2d_normal_form_source_bounds.py`](check_p2d_normal_form_source_bounds.py)
   authenticates those three prerequisites and passes all 38 exact checks in
   five groups.  It reuses the already archived outward interval hulls and
   propagates them with exact rational arithmetic; it does not create a new
   C++ lane, certificate schema, or independent-replay mechanism.

The exact checker output is one deterministic JSON line.  Its top-level
status is `PASS`, its mathematical status is `LOCAL_MATHEMATICAL_PASS`, and
its local chart table records

```text
V2.CHART.SYMPLECTIC_FRAME       PASS
V2.CHART.ANALYTIC_NORMAL_FORM   PASS
V2.CHART.ZERO_ENERGY            OPEN
V2.CHART.EXACT_SECTIONS         OPEN
V2.CHART.WEIGHTED_PASSAGE       OPEN
V2.CHART.PHYSICAL_SLIDES        OPEN
V2.CHART.OVERLAPS               OPEN
V2.EXACT_CHART                  OPEN
```

## Validated input and majorant constants

The normalized parameter box is

\[
 0\le r\le\frac2{25},\qquad |a_2|\le\frac14,
 \qquad \frac45\le\epsilon\le\frac65.
\]

The source-bound coefficient and divisor estimates are

\[
 \begin{aligned}
 E&=3.265104260366031<4,\\
 h_{\rm in}&=0.009256962067152971<\frac1{64},\\
 \kappa_J&=1.488562126122909<\frac53.
 \end{aligned}
\]

They give

\[
 C_*=145.8185731567700,\qquad
 B_*=530909.2228001155<2^{20},\qquad
 G_*=4.860310539823428<8.
\]

The fixed all-orders schedule is therefore

\[
 \overline B=2^{20},\qquad \overline G=8,
 \qquad \varepsilon_{\rm nf}=2^{-22},
 \qquad \vartheta=\frac14.
\]

All displayed decimals are explanatory renderings of exact rational
checker values; the gates are decided only from their numerator and
denominator strings.

## Explicit domains, maps, and tails

The principal scalar envelopes are

\[
 \overline B_z=\frac{37}{691200},\qquad
 A_z=\frac{691200}{691163},\qquad
 A_z\overline S_0=\frac{75}{23191581884416}.
\]

The common complex polydiscs have radii

\[
 \begin{array}{c|c}
 \text{domain}&\text{radius}\\ \hline
 \mathcal D_\infty&5/33554432\\
 \mathcal D_{\rm inv}&1/8388608\\
 \mathcal D_{\rm mid}&7/67108864\\
 \mathcal D_{\rm src}&3/33554432\\
 \mathcal D_{\rm phys}&1/33554432.
 \end{array}
\]

The checker verifies both inverse identities on their stated domains, the
physical image containment through the archived strict bound
\(\|L^{-1}\|_2<8/7\), and the intermediate Cauchy gap
\(\varepsilon_{\rm nf}/16\).

The inverse-first proof gives finite joint derivative envelopes

\[
 D_\Psi<621.545,\qquad
 L_\Theta<1.000054,\qquad
 D_\Theta<621.645,
\]

and exact tails of the form rational-polynomial\((N)4^{-N}\) for every
state/parameter derivative through joint order two.  At the audited
\(q=1,2\) prefix, the normal-form and transformed-remainder tail is less than
\(3.688\times10^{-21}\); the inverse coordinate tail is
\(1/3092376453120\), and the forward coordinate tail is
\(15/46383163768832\).  These are rigorous infinite-tail bounds, not a claim
that the degree-four truncation is exact.  The coarser second-derivative tail
at this short prefix is used only to prove convergence; it is not advertised
as a sharp numerical approximation.

For the primitive, the proof constructs the inverse primitive
\(\mathcal B_N\) first and then sets

\[
 \mathcal A=-\mathcal B\circ\Theta.
\]

It proves

\[
 \Theta^*\lambda_0-\lambda_0=d\mathcal A,\qquad
 \mathcal A(0)=0,\qquad
 \mathcal A\circ\mathcal R_0=-\mathcal A
\]

through parameter order two.  Combining this with the certified frame jets
and the fixed physical gauge gives the type-correct chart

\[
 \Phi_\mu^{\rm K}=L_\mu\circ\Theta_\mu^{\mathbb R},
 \qquad
 \widehat H_\mu\circ\Phi_\mu^{\rm K}
 =h_\mu^{\rm K}(I_1,I_2^{\rm K})
\]

on the certified common source domain, with a two-sided analytic inverse and
a fixed exact primitive gauge.

## Exact claim boundary

This result closes only `V2.CHART.ANALYTIC_NORMAL_FORM` locally.  It does not
construct the nonlinear zero-energy graph, the exact nonlinear radial
sections, the weighted time/phase passage, the physical event-free slides,
or the complete overlap atlas.  Those five atoms and their parent
`V2.EXACT_CHART` remain `OPEN`.

It also proves nothing about temporal stability, Turing pattern selection,
or canard identification.  Those remain later research questions and are not
silently inferred from the existence of a local analytic normal form.

## Reproduction

```bash
python3 -B validation/rigorous/check_p2d_normal_form_source_bounds.py
python3 -B -m unittest \
  validation.rigorous.tests.test_p2d_normal_form_source_bounds -v
```

No second-machine replay is performed by these commands.
