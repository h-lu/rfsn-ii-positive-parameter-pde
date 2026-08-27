# Issue #7 phase-1 local validation report

The first clean-source phase-1 kernel run completed on 2026-08-27.  Its
machine-readable certificate is
[`results/vdp_box_v1_phase1.json`](results/vdp_box_v1_phase1.json).

## Verdict

| Layer | Status | Meaning |
|---|---|---|
| Source, dependency, box, and rounding integrity | `PASS` | The local source commit, read-only flagship Git objects, strict CAPD/FILIB build, rounding tests, and frozen box all matched their locks. |
| Phase-1 mathematical obligations | `PASS` | The encoded V1 exact identities and V2(1) explicit inequalities hold on the whole frozen box. |
| Independent replay | `PENDING_REQUIRED` | One of the two policy-required distinct machines has been observed. |
| Aggregate | `INCONCLUSIVE` | The local result is not upgraded to a claim-bearing certificate before independent replay. |

Thus `claim_bearing=false` and `release_eligible=false`.  `INCONCLUSIVE` here
does not mean that a phase-1 inequality crossed zero: every implemented local
mathematical obligation passed.  It records the deliberately stronger
two-machine evidence policy.

## Frozen domain and strict margins

The immutable exact rational box is

\[
 r\in[1/25,2/25],\qquad
 a_2\in[-1/4,1/4],\qquad
 \epsilon\in[4/5,6/5].
\]

Representative outward-rounded enclosures from the certificate are

\[
\begin{aligned}
1-2|a_2|r-\sqrt\epsilon\,a_2^2r^4
  &\in[0.95999719566050545,1],\\
\tfrac12-\sqrt\epsilon\,|a_2|r^3
  &\in[0.49985978302527867,0.5],\\
a&\in[0.99985978302527867,1.0001402169747213],\\
2-c&\in[1.9599971956605053,2.04],\\
2+c&\in[1.96,2.0400028043394949],\\
\alpha-\tfrac12&\in[0.19999999999999996,0.21414333371170946],\\
\beta-\tfrac12&\in[0.199999499224911,0.2141428428542852].
\end{aligned}
\]

The source-only exact kernel also verified reversibility, the primitive and
Hamiltonian identities, conservation of the first integral, and

\[
 \det(\zeta I-A)=\zeta^4-c\zeta^2+1.
\]

## Reproducibility boundary

The certificate was generated from clean source commit `5ec37bb2deed`, using
the pinned CAPD source commit `731079217a92` with FILIB and GCC 15.2.0.  All
90 entries in `compile_commands.json` contain the required strict flags; all
13 rounding/environment tests pass.  The flagship repository was read only
through locked Git objects at commit `d54add098545` and was not modified.

The build requires `-fno-ipa-pure-const` in addition to the usual strict
rounding flags.  Without it, GCC 15 can incorrectly eliminate repeated CAPD
rounding-mode checks across floating-environment changes.

## Scope not yet validated

Phase 1 does **not** validate the V2 homoclinic continuation, exact local
charts, or event atlas; the V3 pole end; the V4 outer graph; V5/V5A matching
and finite parts; or the exhaustive V6 return/exit system.  These are the
pending P2--P5 stages in [`obligations.json`](obligations.json).  It also makes
no temporal-stability, Turing-selection, nonlinear pattern-selection, or
maximal-canard claim.
