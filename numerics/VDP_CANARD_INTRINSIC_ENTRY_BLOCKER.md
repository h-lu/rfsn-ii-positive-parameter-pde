# Intrinsic finite-parameter canard entry: blocker audit

## Outcome

Issue #13 C1 is **not computed**.  The present status is
`BLOCKED_MISSING_FINITE_R_WCU_BRANCH_SELECTOR`, with
`claim_bearing=false`.  This is not evidence of an error in the abstract or
van der Pol theory.  It identifies one missing application-level input: a
numerically authenticated finite-\(r\) trace of the relevant outer saddle
slow manifold (equivalently, the selected \(W^{cu}\) branch) on a fixed
central-chart section.

The audit is intentionally lightweight.  It performs no collocation or
continuation and emits neither a splitting value nor an \(a_2\) derivative.
The executable record is
[`vdp_canard_intrinsic_entry.py`](vdp_canard_intrinsic_entry.py), its frozen
configuration is
[`vdp_canard_intrinsic_entry_v1.json`](config/vdp_canard_intrinsic_entry_v1.json),
and the deterministic output is
[`blocker_audit.json`](results/vdp_canard_intrinsic_entry/blocker_audit.json).

## Exact coordinate interface checked

At \(\epsilon=1\), the repository uses the same central-chart field and
Hamiltonian as equations (6.8)--(6.10) of Vo--Doelman--Kaper:

\[
 u_2'=p_2,\qquad
 p_2'=u_2^2-v_2+\frac{r^2}{3}u_2^3,\qquad
 v_2'=q_2,\qquad
 q_2'=u_2-r a_2,
\]

\[
 H_2=\frac12(p_2^2-q_2^2)+(u_2-r a_2)v_2
      -\frac13u_2^3-\frac1{12}r^2u_2^4.
\]

The chart transition in equations (6.31)--(6.32) is

\[
 (r_2,u_2,p_2,v_2,q_2,a_2)
 =\left(r_1\sqrt{\delta_1},\frac1{\delta_1},
 \frac{p_1}{\delta_1^{3/2}},\frac{v_1}{\delta_1^2},
 \frac{q_1}{\delta_1^{3/2}},\frac{a_1}{\delta_1^{3/2}}\right),
\]

with the inverse obtained from \(\delta_1=1/u_2\).  Thus the fixed source
section \(u_2=16\), \(p_2<0\), \(q_2<0\) has an exact K1--K2 meaning.  The
target is the first increasing zero of \(p_2\), with \(p_2'>0\), and the
signed splitting convention is \(S=q_2\).

The source audited here is Vo, Doelman, and Kaper, *SIAM Journal on Applied
Dynamical Systems* 24 (2025), DOI
[`10.1137/24M1690722`](https://doi.org/10.1137/24M1690722), arXiv
[`2409.02400v1`](https://arxiv.org/abs/2409.02400).  The equation and appendix
locators are part of the audit record; the paper is not copied into this
repository.

## What the cited results do and do not select

Appendix A.2 computes subsets of saddle slow manifolds by finite-boundary
BVPs.  Its outer boundary is selected by a fixed \(q_0<0\) or a fixed
\(u_0>1\).  It then finds maximal-canard candidates as saddle nodes of those
BVPs.  It does not state a canonical finite-boundary limit, an independence
theorem for \(q_0\) or \(u_0\), or a finite-\(r\) parameterization of the
specific \(W^{cu}\) trace needed here.

Appendix A.3 continues central-chart solutions with reverser parity
\(p_2(0)+p_2(1)=q_2(0)+q_2(1)=0\) and an integral \(H_2=0\) constraint.  Those
conditions do not impose membership in an outer saddle slow manifold.

The K1 analysis proves a center manifold and its stable/unstable foliations.
It also singles out a unique branch of the limiting manifold \(N\) in the
invariant set \(r_1=0\), \(p_1<0\), \(\delta_1>0\).  That limiting uniqueness
does not itself give a numerical finite-\(r\) graph at \(r=0.08\).  Hence the
missing selector is an application interface, not a contradiction or gap in
the stated theorem.

## Why the two existing candidates cannot be promoted

The current slow-trace computation freezes the Appendix-A.2 boundary
\(u_*=16.64508336484338\) (and \(q_0=-80\)).  It gives a useful exact-field,
finite-boundary BVP candidate, but no boundary-independence or invariant-
manifold membership certificate.

The splitting scout instead projects a truncated formal jet onto \(H_2=0\).
That gives a useful local root finder, but a formal-jet projection is not a
finite-\(r\) invariant slow manifold.

There is also a direct nonuniqueness check.  At
\(r=0.08\), \(a_2=-1/120\), \(u_2=16\), and \(p_2=-2.24\), two different
choices of \(v_2\) can be completed with the negative square root to distinct
states satisfying \(H_2=0\) and \(q_2<0\).  The executable audit verifies both
Hamiltonian residuals.  It makes no claim that either state lies on
\(W^{cu}\); precisely that membership remains undetermined.  Therefore
energy, section, and orientation constraints cannot serve as the missing
branch selector.

## Minimum input that would unblock an E1 C1 scout

The checker refuses an intrinsic-entry manifest unless it records all of the
following:

1. a finite-\(r\) K1 \(W^{cu}\) disk or finite-\(r\) outer saddle-slow graph,
   with an invariance residual and an authenticated K1--K2 trace on \(u_2=16\);
2. continuation from \(\Gamma_0^-\) identifying the primary no-loop branch;
3. a complete event census verifying that the selected target is the first
   increasing \(p_2=0\) hit;
4. at least two distinct outer cuts or section positions, with their entry
   states, invariance residuals, \(S\), \(dS/da_2\), and the observed
   entry/\(S\)/\(dS\) differences;
5. the entry tangent \(d(u_2,p_2,v_2,q_2)/da_2\).

This interface is a gate, not a proof certificate.  Passing it would permit a
non-claim-bearing `COMPUTED/E1` scout; C1/C2 would still need their stated
mathematical validation before being called proved.

## Parameter-domain boundary

Issue #13 fixes \((r,\epsilon)=(0.08,1)\) and studies
\(a_2\in[-1/80,0]\).  The Issue #7 v2 box has
\(r\in[0.01,0.02]\), so it is disjoint and cannot certify the C1/C4 slice.
The old v1 wide-box phase-order failure occurred elsewhere and has no logical
implication for this narrow slice.

A separate eight-cell strict-binary probe over
\(r\in[31/400,2/25]\), \(a_2\in[-1/64,0]\), and
\(\epsilon\in[0.9,1.1]\) passed its root-C2 jet checks.  It is recorded only
as `NON_EVIDENTIARY_STRICT_BINARY_SCOUT`: no authenticated manifest was frozen,
it closes no atom, and C4 still requires a dedicated narrow-slice
branch-identification/event-atlas certificate.

## Reproduction

```bash
python3 -B numerics/vdp_canard_intrinsic_entry.py \
  --output /tmp/vdp-canard-intrinsic-entry-blocker.json
python3 -B -m unittest numerics.test_vdp_canard_intrinsic_entry -v
```

The command is expected to report the blocker and exit successfully.  A
missing or malformed future entry manifest, a frozen-boundary anchor, a formal
jet anchor, nondistinct independence replays, or a changed audited input is
rejected fail-closed.
