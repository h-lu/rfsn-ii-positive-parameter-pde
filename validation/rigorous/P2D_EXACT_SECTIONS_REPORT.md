# P2d exact radial-sections report

**Local mathematical status:** `PASS` for `V2.CHART.EXACT_SECTIONS`.

**Aggregate status:** `INCONCLUSIVE`; `claim_bearing=false`;
`release_eligible=false`; independent replay remains `1/2`;
`V2.EXACT_CHART=OPEN`.

## Evidence chain

1. `V2.CHART.SYMPLECTIC_FRAME`,
   `V2.CHART.ANALYTIC_NORMAL_FORM`, and `V2.CHART.ZERO_ENERGY` have local
   mathematical passes under their separately bound proof contracts.
2. The archived exact-chart audit source has SHA-256
   `050cfd00d49412e9404c17b0eed680bf17e88798bfce48d0e1ec0920770c52d1`.
   Its 59-check report includes the arbitrary-\(q\) incoming/outgoing action,
   section-form, and primitive identities used here.
3. [`EXPLICIT_EXACT_RADIAL_SECTIONS.md`](../../theory/EXPLICIT_EXACT_RADIAL_SECTIONS.md)
   proves contract `rfsn-vdp-p2d-explicit-exact-radial-sections/1`; its
   SHA-256 is
   `df3ff1e0c23871ffc050183e941c63a9d93d57179eecb38efa3db8dd161a6d55`.
4. [`check_p2d_exact_sections.py`](check_p2d_exact_sections.py) authenticates
   those inputs and verifies every new domain and positive-flight decision by
   exact rational arithmetic.

## Frozen section block

On the complete parameter bridge, use

\[
 \rho=\frac5{2^{26}},\qquad
 \rho_{\rm src}=\frac3{2^{25}},\qquad
 |\nu|\le\nu_*:=\frac{25}{2^{54}}.
\]

With the conservative zero-energy bound \(|q_\mu(\nu)|\le Q_0\), the exact
margins are

\[
 \frac{\rho}{\rho_{\rm src}}=\frac56,qquad
 \frac{Q_0+\nu_*}{\rho^2}=\frac{587}{768},qquad
 \frac{Q_0+\nu_*}{\rho\rho_{\rm src}}
 =\frac{2935}{4608}.
\]

All three are strictly less than one.  Thus both nonlinear radial sections
lie in the exact normal-form source chart, and every nonzero incoming point
has strictly smaller expanding radius than the frozen outgoing radius.

## Exact forms and gauges

Both Kato-oriented sections satisfy

\[
 I_1=q_\mu(\nu),\qquad I_2^{\rm K}=\nu,qquad
 \iota^*\omega=d(\text{phase})\wedge d\nu.
\]

If \(f_\mu\) is the already fixed primitive of the nonlinear exact chart, the
physical section gauges are fixed as

\[
 G^{\rm in}_\mu=f_\mu\circ s^{\rm in}_\mu-\frac12q_\mu,
 \qquad
 G^{\rm out}_\mu=f_\mu\circ s^{\rm out}_\mu+\frac12q_\mu.
\]

The two physical primitive pullbacks are exactly

\[
 -\nu\,d\phi+dG^{\rm in}_\mu,
 \qquad
 -\nu\,d\psi+dG^{\rm out}_\mu.
\]

For \(0<|\nu|\le\nu_*\), the real orientation bound
\(\partial_{I_1}h>2/3\) makes the expanding radius strictly increasing.
The first reach of the outgoing radial face is unique, and the normal-form
actions give exact preservation of the same signed value
\(I_2^{\rm K}=\nu\).  At \(\nu=0\), only the stable/unstable axis boundary
circles are recorded; no finite passage time is claimed.

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

The separately proof-bound weighted-passage artifact has since supplied the
fifth local child pass.  The next mathematical gate is
`V2.CHART.PHYSICAL_SLIDES`; see
[`P2D_WEIGHTED_PASSAGE_REPORT.md`](P2D_WEIGHTED_PASSAGE_REPORT.md).

## Claim boundary

This exact-sections child alone does not prove the weighted-passage result;
that is supplied by the separately bound artifact just cited.  Neither child
proves physical slides, overlap transitions, the compact event atlas,
positive ends, the exhaustive V6 census, temporal stability, Turing
selection, or canard identification.

## Reproduction

```bash
python3 -B validation/rigorous/check_p2d_exact_sections.py
python3 -B -m unittest \
  validation.rigorous.tests.test_p2d_exact_sections -v
```

The checker emits one canonical JSON line.  A proof digest mismatch returns
top-level `INCONCLUSIVE`, keeps the exact-sections atom `OPEN`, and exits
nonzero.
