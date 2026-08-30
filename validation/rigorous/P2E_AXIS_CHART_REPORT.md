# P2e zero-action true-source chart report

The application-owned proof
[P2E_AXIS_SOURCE_CHART.md](../../theory/P2E_AXIS_SOURCE_CHART.md)
and deterministic checker
[check_p2e_axis_chart.py](check_p2e_axis_chart.py) close the physical
initial-set problem on the zero-action source skeleton.  They do not perform
an exterior first-hit integration and do not pass V2.EVENT_ATLAS.

## Verdict

| Item | Status | Meaning |
|---|---|---|
| P2b0/P2bK source authentication | PASS | The immutable certificates, their configurations, required local atoms, exact Kato phase facts, and the exact inclusion of the v2 bridge in their proved bridge are authenticated. |
| P2E.ZERO_ACTION_TRUE_SOURCE_CHART | local mathematical PASS | The true \(\nu=0\) source curve lies in one nonsingular exact zero-energy chart on the full proper phase arc and v2 bridge. |
| P2E.AXIS_SKELETON_THICKENING_CRITERION | local mathematical PASS | A complete strict zero-action event skeleton with \(m_{\rm ax}>0\) persists on some uniform action subcollar. |
| Zero-action first-event skeleton | OPEN | ALG and POLE still require rigorous first-hit, incidence, census, and margin calculations; HOM is imported from P2c. |
| V2.EVENT_ATLAS | OPEN | No atlas claim is promoted by this lemma. |
| Release status | claim_bearing=false | The imported source certificates retain independent replay \(1/2\). |

The checker therefore reports

    status               PASS
    mathematical_status  LOCAL_MATHEMATICAL_PASS
    claim_bearing        false
    V2.EVENT_ATLAS       OPEN

## The chart

For the direct source phase
\(\theta\in[57/10,13/2]\), set

\[
 u=\frac1{100}R_{\chi(\mu)}e_\theta,\qquad
 s_1=H_{10,1}(u)+\eta,\qquad X=u_1+s_1,
\]

and solve the exact zero-energy equation by

\[
 s_2=-\frac{u_2s_1}{u_1}
      -\frac{a_\mu X^3}{6h_\mu u_1}
      +\frac{b_\mu X^4}{8h_\mu u_1}.
\]

This is not the P2d exact-action coordinate: \(\eta\) is the first graph
error relative to \(H_{10}\).  The actual zero-action true source is the
moving curve

\[
 \eta_\mu(\theta)
 =(H_\mu-H_{10})_1(u(\theta,\mu)),
 \qquad |\eta_\mu(\theta)|\le\frac1{200000},
\]

which lies strictly inside the chosen chart
\(|\eta|<1/100000\).

The exact checks give

\[
 |\theta+\chi-2\pi|<\frac{143}{240}<\frac35,
 \qquad
 u_1>\frac{41}{5000}>0.
\]

Thus the zero-energy solve never divides by zero.  Exact symbolic
substitution cancels the Hamiltonian identically, and the physical linear
map has determinant
\(-8\alpha_\mu\beta_\mu h_\mu\ne0\).  The checker also validates the
frozen rational \(2\pi\) enclosure independently from Machin's identity and
alternating rational series, rather than treating the decimal value of
\(\pi\) as input.

## Consequence for the P2e computation

The fixed value \(2^{-55}\) is now only an available design ceiling.  It is
not a radius that must be completely integrated.  If the rigorous
\(\nu=0\) event calculation supplies the full first-event assignment,
incidence/corner census, no-residual conclusion, and a uniform
\(m_{\rm ax}>0\), compactness and first-hit stability give

\[
 0<\delta_{\rm ent}\le2^{-55}
\]

on which the same arrangement persists with margins at least
\(m_{\rm ax}/2\).  The later high-winding threshold can then be increased
until every retained local-passage branch has
\(|\nu|<\delta_{\rm ent}\).

No numerical value of \(\delta_{\rm ent}\) is asserted.  In particular, this
result does not certify the whole fixed \(2^{-55}\) disk.

## Remaining mathematical work

The next calculation is deliberately narrow:

1. import the already validated selected-homoclinic first-hit branch;
2. rigorously integrate the true-source enclosure above through the
   algebraic and pole channels at \(\nu=0\);
3. certify event speeds, no-earlier-hit gaps, active conormal ranks,
   containment, all incidences and corner priorities;
4. enumerate every connected first-event component, exclude unnamed
   residuals, and take the minimum positive \(m_{\rm ax}\);
5. apply the proved subcollar criterion and bind the transported traces.

Only failure of the existing \(H_{10}\) graph tube through interval wrapping
would justify a local raw-\(W^u\) tightening calculation.

## Reproduction

    python3 -B validation/rigorous/check_p2e_axis_chart.py
    python3 -B -m unittest \
      validation.rigorous.tests.test_p2e_axis_chart -v

The result is a proof-bound local lemma.  It establishes no temporal
stability, dynamical Turing selection, or finite-parameter canard
identification.
