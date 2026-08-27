# Issue #7 P2b0 H10-centered C0/C1 validation report

The first clean-source P2b0 run completed on 2026-08-27.  Its
machine-readable certificate is
[`results/vdp_bridge_v1_p2b_h10_c01.json`](results/vdp_bridge_v1_p2b_h10_c01.json).

## Verdict

| Layer | Status | Meaning |
|---|---|---|
| Source, dependency, bridge, configurations, prerequisite, and rounding integrity | `PASS` | The clean local source commit, read-only flagship Git objects, strict CAPD/FILIB build, rounding tests, frozen bridge, immutable P2a prerequisite, and preregistered P2b0 gates match their recorded hashes. |
| `P2.H10_CENTER_EXACT` | `PASS` | The frozen exact homological recursion was rerun over \(\mathbb Q(\sqrt2)\); its generated header is byte-identical to the frozen H10 table and has the declared term structure. |
| `V2.WU.H10_C0_TUBE` | `PASS` | The true parameter-dependent local graphs remain in the frozen Euclidean \(C^0\) tube about H10 on the complete comparison bridge. |
| `V2.WU.H10_C1_TUBE` | `PASS` | Their state derivatives remain in the frozen Frobenius \(C^1\) tube about \(DH_{10}\) on that bridge. |
| Parent `V2.WU.JETS` and `V2.WU.GRAPH` | `PENDING` | True-graph state derivatives through order three, parameter derivatives through order two, required mixed derivatives, and weighted half-orbit constants are not P2b0 conclusions. |
| Independent replay | `PENDING_REQUIRED` | One of the two policy-required distinct machines has been observed. |
| Aggregate certificate | `INCONCLUSIVE` | The local mathematical result is not claim-bearing before the required independent replay. |

Thus `mathematical_status=PASS`, `integrity_status=PASS`,
`final_status=INCONCLUSIVE`, `claim_bearing=false`, and
`release_eligible=false`.  Here `INCONCLUSIVE` does not mean that a P2b0
bound crossed a gate: every implemented integrity and mathematical
obligation passed.  It records the deliberately stronger replay policy.

## Exact center and true-graph tubes

The comparison bridge remains

\[
 r\in[0,2/25],\qquad
 a_2\in[-1/4,1/4],\qquad
 \epsilon\in[4/5,6/5],
\]

and the unstable disk has radius \(R=1/100\).  Before the interval result was
inspected, the tube radii were frozen as

\[
 \rho_{C^0}=\frac1{200000}=5\times10^{-6},\qquad
 \rho_{C^1}=\frac3{10000}=3\times10^{-4}.
\]

The exact audit regenerated the four arrays byte-for-byte from flagship
commit `d54add098545`: H1/H2 contain 54/63 terms of total degrees 2--10,
and the two exact invariance-defect arrays contain 361 terms each of total
degrees 11--29.  There are no repeated monomials or nonpositive
denominators.  The regenerated and frozen header SHA-256 is
`d617587ea1b9037c1c7575ccdde5029529ec5b736dee259baff9a2a162001e96`.

Representative outward-rounded upper bounds are

\[
\begin{aligned}
 \lVert H_{10}\rVert_2&\le3.2961536609720856\times10^{-5},\\
 \lVert DH_{10}\rVert_F&\le5.2379054813578903\times10^{-3},\\
 \lVert D^2H_{10}\rVert_F&\le4.2657343764993072\times10^{-1},\\
 \lVert R_0\rVert_2&\le2.2689612291787094\times10^{-24},\\
 \lVert DR_0\rVert_F&\le2.0210645060702415\times10^{-21},\\
 E_0&\le1.3797729130196999\times10^{-6},\\
 E_1&\le2.5311298632347602\times10^{-4},\\
 \ell&\le1.0041731066881686\times10^{-2},\\
 m&\le1.0004107218227647,\\
 \kappa&\ge6.8990567129492064\times10^{-1}.
\end{aligned}
\]

The two no-first-exit quantities satisfy

\[
\begin{aligned}
 \kappa\rho-E_0
 &\ge2.0697554434549019\times10^{-6}
  >1.9\times10^{-6},\\
 2\kappa\rho_{C^1}-G_u-\ell\rho_{C^1}^2
 &\ge1.5575350360721478\times10^{-4}
  >1.25\times10^{-4}.
\end{aligned}
\]

Their preregistered positive-margin lower bounds are respectively
\(1.6975544345490105\times10^{-7}\) and
\(3.0753503607214722\times10^{-5}\).  Consequently the already-existing
P2a true graph satisfies

\[
 \lVert H_\mu-H_{10}\rVert_2\le5\times10^{-6},\qquad
 \lVert D H_\mu-DH_{10}\rVert_{2\to2}
 \le\lVert\cdot\rVert_F\le3\times10^{-4}
\]

uniformly on the complete bridge.  Reversibility gives the corresponding
stable graph statement.

## Integrity and reproducibility boundary

The certificate was generated from clean source commit `13483e418c02`, using
the pinned CAPD source commit `731079217a92`, FILIB, and GCC 15.2.0 with the
strict floating-environment flags.  The H10 term table was read only through
`git show` at the frozen flagship commit.  The compiler consumed that exact
materialized object through an absolute forced-include argument, eliminating
same-name include shadowing.  The archived certificate SHA-256 is
`91c1762329a9e19e8db69052f9397532512d8031f361f0b6eeb43edbeda5d5ac`.

The semantic checker recomputes the three-valued obligation statuses from
the serialized margins.  A nonpositive sufficient-condition lower bound is
`INCONCLUSIVE`, not a purported mathematical counterexample; a malformed or
wrong materialized term table is `FAIL`.  The checker also binds the P2a
certificate, exact-audit output, forced include, probe arguments, source
hashes, and audit/probe exit codes.

The proof mechanism and every frozen formula are in
[`P2_VALIDATION_CONTRACT.md`](P2_VALIDATION_CONTRACT.md).  Reproduction uses
the `h10-c01` command documented in [`README.md`](README.md).

## Scope not yet validated

P2b0 does not bound \(D^2H_\mu\), \(D^3H_\mu\), any parameter derivative,
or any mixed state--parameter derivative of the true graph.  In particular,
the displayed \(D^2H_{10}\) bound belongs to the polynomial center and is not
a true-graph \(C^2\) error estimate.  P2b0 also does not establish the Kato
absolute-phase convention or the weighted half-orbit constants used later.

It therefore does not pass `V2.WU.JETS` or `V2.WU.GRAPH`, and it makes no
claim about the selected homoclinic, exact charts, event atlas, V3--V6,
temporal stability, Turing selection, or canard identification.  The next
ordered work is P2b1--P2b3: higher state jets, parameter/mixed jets, and the
explicit weighted half-orbit bounds.

The frozen probe's short formula strings call the \(C^1\) tube radius
`eta`; this is not the exponential tail weight denoted by \(\eta\) in V2.
Future configurations use distinct semantic names for those two quantities.
