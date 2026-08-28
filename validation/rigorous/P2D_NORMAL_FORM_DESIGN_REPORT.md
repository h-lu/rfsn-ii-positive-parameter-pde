# P2d explicit normal-form design report

**Status:** exact finite-prefix audit `PASS`; global-Moser gate evaluation
`DESIGN_CANDIDATE_ONLY`; mathematical status `INCONCLUSIVE`;
`claim_bearing=false`.

This report records the first constructive layer beyond
`V2.CHART.SYMPLECTIC_FRAME`.  It deliberately creates no certificate and
closes no claim atom.  The proposed analytic theorem and its complete proof
interface are in
[`theory/EXPLICIT_GLOBAL_MOSER_MAJORANT.md`](../../theory/EXPLICIT_GLOBAL_MOSER_MAJORANT.md).

## Authenticated prerequisite

The design scout consumes the archived frame certificate
[`results/vdp_bridge_v1_p2d_symplectic_frame.json`](results/vdp_bridge_v1_p2d_symplectic_frame.json)
only after checking all of the following bindings:

- certificate id `vdp-p2d-frame-c80e11ed5065`;
- source commit `c80e11ed5065c86161d6b3ad482a76db613e9983`;
- SHA-256
  `5fabbcf01dc9b2f818f34525010332c76ff40190ea9a3d5ab166072397397847`;
- local mathematical `PASS` for `V2.CHART.SYMPLECTIC_FRAME`; and
- `OPEN` status for `V2.CHART.ANALYTIC_NORMAL_FORM` and `V2.EXACT_CHART`.

The frame certificate itself remains aggregate `INCONCLUSIVE` and
non-claim-bearing because independent replay is 1/2.  The present design layer
does not change that boundary.

## Exact finite Lie prefix

[`audit_p2d_normal_form_exact.py`](audit_p2d_normal_form_exact.py) performs 26
deterministic symbolic checks with no sampling or floating-point arithmetic.
It fixes the unitary complex symplectic dictionary, Poisson and reverser signs,
and the normalized homological equation.  It then computes the exact first two
normalization steps:

\[
 \chi_3=-\frac{H_3}{\Delta},\qquad
 K_4=H_4+\frac12\{H_3,\chi_3\},\qquad
 \chi_4=-\frac{(I-\Pi)K_4}{\Delta},\qquad
 Z_4=\Pi K_4.
\]

The audit verifies exact cancellation of the cubic block, exact quartic
normalization, real structure, reversibility, and zero resonant gauge for both
generators.  At the frozen core \(r=0\), it obtains

\[
 K_{20}=K_{02}=-\frac1{60},\qquad K_{11}=0,qquad
 Z_4=\frac{(I_2^{\rm K})^2-I_1^2}{120}.
\]

On the linear zero-energy action direction \(I_1=-I_2^{\rm K}\), this quartic
term vanishes.  Conditional on continuation of a formal zero-energy action
graph, coefficient comparison through action degree two gives

\[
 I_1=-\nu+c_2\nu^2+\cdots\quad\Longrightarrow\quad c_2=0.
\]

This is a conditional low-order formal consequence only: if such a formal
graph is constructed, it has no quadratic bending term.  The audit constructs
neither a full formal graph nor an analytic zero-energy branch, and it proves
no existence, uniqueness, uniformity, or positive-parameter continuation.

## Candidate global majorants

[`design/p2d_normal_form_scout.py`](design/p2d_normal_form_scout.py)
authenticates the frame input and converts every archived binary64 hexadecimal
endpoint to its exact rational value.  Dyadic rational square-root upper bounds
are used for the four complex coefficients of \(U\).  The resulting proposed
input bounds are

\[
 \begin{aligned}
 E&=3.265104260366031<4,\\
 h_{\rm in}&=0.009256962067152971<\frac1{64},\\
 \kappa_J&=1.488562126122909<\frac53.
 \end{aligned}
\]

The fixed schedule

\[
 \overline B=2^{20},\qquad \overline G=8,\qquad
 \varepsilon_{\rm nf}=2^{-22},\qquad
 \vartheta=\overline B\varepsilon_{\rm nf}=\frac14
\]

passes every implemented rational domain inequality.  In particular,

\[
 B_z=\frac{37}{691200}<\frac1{16384},\qquad
 A_z=(1-B_z)^{-1}=\frac{691200}{691163},
\]

and the forward displacement satisfies

\[
 A_zS_0=\frac{75}{23191581884416}
 <\frac{\varepsilon_{\rm nf}}8.
\]

The explicit complex radii are

\[
 \operatorname{rad}\mathcal D_\infty=\frac5{33554432},\qquad
 \operatorname{rad}\mathcal D_{\rm inv}=\frac1{8388608},\qquad
 \operatorname{rad}\mathcal D_{\rm src}=\frac3{33554432},\qquad
 \operatorname{rad}\mathcal D_{\rm phys}=\frac1{33554432}.
\]

The additional rational gate (44a) verifies that the proposed physical inverse
image lies in \(\mathcal D_{\rm src}\), the domain used for the final primitive
and normal-form identities.

For the exact \(q=1,2\) prefix, the proposed inverse/raw coordinate tail is
\(1/3092376453120\); the forward tail includes the required Lipschitz
amplification and is \(15/46383163768832\).

These evaluations show that the proposed constants are numerically feasible on
the complete archived bridge input.  They are not a proof of the proposed
majorant theorem and are not an outward-rounded source-bound run of that theorem.

## Proof-design corrections made before freezing

The design audit exposed and corrected five points that would otherwise have
invalidated a later formal claim:

1. the real first-row norm of \(L\) was replaced by the correct four-coefficient
   complex norm \(4\sqrt{(p^2+q^2)/2}\), including every parameter derivative;
2. forward Lie-map Cauchy differences are amplified by the earlier maps, so the
   raw displacement sum \(S_0\) was supplemented by \(B_z\) and \(A_z\);
3. forward and inverse compositions now use distinct explicit source and target
   domains and prove both inverse identities conditionally;
4. the parameter-\(C^2\) comparison system includes the state Hessian and the
   mixed state--parameter chain rule; and
5. the physical-domain inclusion uses the fixed unitary map
   \(S\circ L_\mu^{-1}\), rather than identifying real and complex coordinates.

## Exact claim boundary and next gate

`V2.CHART.ANALYTIC_NORMAL_FORM` remains `OPEN`.  Closing it still requires:

1. a complete proof of the Giorgilli-type all-orders recurrence and the stated
   constants in the normalized parameter-two-jet Banach algebra;
2. outward-rounded source bounds for the proposed input gates on the entire
   bridge;
3. summable state, parameter, and mixed \(C^2\) tails for the map and inverse;
4. convergence and normalization of the exact primitive; and
5. verification that every parameter cell bounds restrictions of one global
   formula, not independently chosen local charts.

Only after that analytic-normal-form atom passes should the construction move
to the nonlinear zero-energy graph, exact radial sections, weighted passage,
physical slides, and overlaps.  Temporal stability, Turing selection, and
canard identification remain later research questions.

## Reproduction

```bash
python3 -B validation/rigorous/audit_p2d_normal_form_exact.py
python3 -B validation/rigorous/design/p2d_normal_form_scout.py --pretty
python3 -m unittest \
  validation.rigorous.tests.test_p2d_normal_form_exact_audit \
  validation.rigorous.tests.test_p2d_normal_form_scout
```
