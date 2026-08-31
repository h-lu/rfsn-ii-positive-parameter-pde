# V5 v2 parameter-grid predictor

**Result:** `COMPUTED/E1_NON_RIGOROUS` on all 225 prescribed nodes.  This is
a deterministic seed set for a later interval V5 incidence calculation, not
a V5 validation result.

## Computed object

The frozen v2 box was sampled on the exact tensor grid

\[
 r\in\{1/100,1/80,3/200,7/400,1/50\},
\]
\[
 a_2\in\{-1/4,-3/16,-1/8,-1/16,0,1/16,1/8,3/16,1/4\},
\]
\[
 \epsilon\in\{4/5,9/10,1,11/10,6/5\}.
\]

At each node the existing energy-preserving central--resolved-\(K_1\)--outer
BVP was recomputed.  The traversal starts at the box centre and follows a
fixed nearest-neighbour tree.  A first positive step uses the preceding
phase, subsequent steps use a two-neighbour secant, and the first negative
step is predicted by reflection across the centre.  No point was manually
reseeded, and all 225 solves passed the existing residual, seam, energy,
orientation, and positive-branch QA.

Only the following endpoint record is retained at each point:

- \((r,a_2,\epsilon)\), source phase, \(H\), predecessor and phase predictor;
- \((\Pi,\Omega)\) on \(U=-4\);
- \((\Pi,\Omega,\alpha,\beta)\) on the resolved-\(K_1\) cut \(R=2\);
- existing QA diagnostics and signed patch/collar margins.

No orbit NPZ or figure atlas is created.

## Numerical ranges

| quantity | 225-point hull or minimum |
|---|---:|
| source phase | \([5.727889049804,\ 5.785641605195]\) |
| \(H\) | \([-1.17546,\ 1.20412]\times10^{-13}\) |
| scaled outer energy \(E=\epsilon^{5/2}r^6H\) | \([-7.45612,\ 7.70632]\times10^{-24}\) |
| \(\Pi\) at \(U=-4\) | \([0.550799264730,\ 0.610772721833]\) |
| \(\Omega\) at \(U=-4\) | \([0.041528101296,\ 0.041677051844]\) |
| \(\Pi\) at \(R=2\) | \([0.281056997404,\ 0.334966462601]\) |
| \(\Omega\) at \(R=2\) | \([2.68739\times10^{-7},\ 1.45563\times10^{-6}]\) |
| \(\alpha\) at \(R=2\) | \([1.16447,\ 5.11532]\times10^{-6}\) |
| \(\beta\) at \(R=2\) | \([1.16445,\ 5.11491]\times10^{-6}\) |
| minimum signed \(U=-4\) patch margin | \(1.0278101296\times10^{-2}\) |
| minimum signed strict-V4-collar margin | \(4.8846863876\times10^{-6}\) |

The displayed central patch is
\(\Pi\in[1/2,2/3]\), \(\Omega\in[1/32,1/16]\).  The outer margins compare
against the already declared strict V4 corridor
\(|E|\le10^{-3}\), \(z\le2/9\), and
\(|\alpha|,|\beta|\le10^{-5}\).  These positive values say that all sampled
endpoint candidates lie inside those displayed sets.  They do not provide
inter-node enclosures.

The largest recorded QA quantities were

\[
 \|R_{\rm BVP}\|_{\rm rms}\le9.99838\times10^{-7},\qquad
 \|R_{\partial}\|_\infty\le5.31364\times10^{-12},
\]
\[
 \|R_{\rm central/K1}\|_\infty\le1.86731\times10^{-11},\qquad
 \|R_{\rm K1/outer}\|_\infty\le6.86097\times10^{-20}.
\]

## Resolved-\(K_1\) spectral corridor choice

At the \(U=-4\) cut, let \((\Pi_{\rm ref},\Omega_{\rm ref})\) be the explicit
leading resolved-\(K_1\) centre-graph reference and set

\[
 \lambda=\sqrt{\sqrt\epsilon\,(2+\sqrt\epsilon\,r_1^2)},
\]
\[
 b=\frac12\left[(\Pi-\Pi_{\rm ref})-
 \frac{\Omega-\Omega_{\rm ref}}{\lambda}\right],\qquad
 n=\frac12\left[(\Pi-\Pi_{\rm ref})+
 \frac{\Omega-\Omega_{\rm ref}}{\lambda}\right].
\]

The sampled hulls are

\[
 b\in[-5.662356,-1.437255]\times10^{-6},\qquad
 n\in[-2.239430,0.387141]\times10^{-6}.
\]

Accordingly, the next strict resolved-\(K_1\) run has the exact design
candidate

\[
 |b|\le 1/100000,\qquad |n|\le1/200000.
\]

Its sampled margins are respectively
\(4.33764\times10^{-6}\) and \(2.76057\times10^{-6}\).  This selects a
concrete interval target; it does **not** certify that target.  The strict run
must still absorb interval integration error and all variation between grid
nodes.

The subsequent strict calculation did not need to retain this narrow first
choice: it certified the broader product tube \(|b|,|n|\le10^{-4}\) on the
whole v2 box.  See
[`V5_K1_TUBE_REPORT.md`](../validation/rigorous/V5_K1_TUBE_REPORT.md).
The grid remains useful as an independent branch locator and endpoint census;
its evidence status is unchanged.

## Claim boundary and reproduction

A finite root grid cannot exclude an interior fold or root jump, prove that
all nodes belong to one V5 branch, enclose the source-to-graph incidence, or
prove V5.  Its mathematical use is narrower and concrete: it supplies a
box-wide set of corrected centres, verifies that the proposed coordinate
patches are numerically plausible, and fixes the first strict \(b/n\)
corridor to test.

The machine-readable result is
[`result.json`](results/vdp_v5_v2_predictor_grid/result.json).  Reproduce and
check it with

    python3 -m numerics.vdp_v5_v2_predictor_grid
    python3 -B -m unittest numerics.test_vdp_v5_v2_predictor_grid -v
