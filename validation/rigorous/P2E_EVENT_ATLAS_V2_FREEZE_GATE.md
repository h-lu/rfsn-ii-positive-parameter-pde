# P2e v2-box event-atlas structural freeze gate (schema `/3`)

This gate freezes the data model for one application-owned realization of
`V2.EVENT_ATLAS`.  It is not an event-atlas certificate and it does not run
CAPD.  Its committed verdict is deliberately

```text
structure_status     READY_TO_SCOUT_NON_EVIDENTIARY
status               STOP_BEFORE_FULL_RUN
atlas_claim_status   PENDING
mathematical_status  INCONCLUSIVE
```

`READY_TO_SCOUT_NON_EVIDENTIARY` means only that exploratory calculations may
be used to test the frozen compact carriers and artificial lateral faces.
Neither it nor the later `READY_FOR_FIRST_FULL_RUN` state is a mathematical
`PASS`.

Schema `/3` supersedes the unmaterialized `/2` structure at commit
`4e2e3f0`.  The earlier file used the P2d section phase \(\psi_u\) as the
`B.OUT` coordinate but centered its apertures at direct common-source labels
\(\phi_{\rm a}^0\), \(\phi_{\rm h}(\mu)\), and \(2\pi\).  The corrected
carrier is

\[
 E_{\rm out}^{\rm dir}(\phi_u,\nu_u)
 =E_{\rm out}^{\rm P2d}(\lambda_\mu(\phi_u),\nu_u).
\]

It preserves the exact signed action, while the displayed pair is not claimed
to be Darboux.  `B.RET` remains in the exact P2d coordinates
\((\psi_r,\nu_r)\).  No full atlas run had begun, so this correction
invalidates no mathematical certificate; the three strict phase gaps already
live in the direct \(\phi\)-lift and are retained.

The manifest fixes the v2 comparison bridge and its 4096-cell rational cover,
the required carrier and function inventories, the complete ambient-domain
lists, the incidence/priority/census fields, the normalization and margin
categories, and the locked binary64 FILIB execution policy.  The five
physical carriers, four normalized pullback domains, eleven physical faces,
sixteen defining functions, fifteen ambient lists, and numerical method are
now prospectively frozen.  Their type correction and exact flowbox design are
recorded in [`P2E_EVENT_ATLAS_TYPE_AUDIT.md`](P2E_EVENT_ATLAS_TYPE_AUDIT.md).
The `B.OUT` and `B.RET` physical embeddings are already mathematical
consequences of the proved P2d seam and physical-slide atoms; no separate
numeric \(\lambda\)-table is required for that qualitative conclusion.  The
three exterior flowbox embeddings still lack executable physical
initial-state and interval first-hit certificates.  The
incidence complex, corner priority, first-event census, normalization,
transported traces, and numerical `m0` remain absent.  A missing section must
have an empty payload, all atlas obligations remain `PENDING`, and the checker
refuses to authorize the first full run until every section is explicit and
prospectively frozen.  The bound terminal-flowbox scout records design
lineage only; it contributes no certified margin.

The return-band interface follows the focused theory inventory.  Its adjustable
side is the distinct occurrence `u_r`; on the return and homoclinic-pullback
lists it is represented only by the bound difference `q_ret`.  It is neither
the homoclinic-channel side `h_side_h` nor a duplicated return side-hit defining
function.  At a nonempty `q_ret=0` stratum, priority selects the bound physical
return event `a_ret` while retaining `q_ret` as incidence data.

## Minimal materialization route

1. Reuse the real, frozen source objects already bound by
   `vdp_p2e_phase_order_v2.json`: the origin--algebraic certificate, the
   origin--pole-entry certificate, and the P2c selected-homoclinic certificate.
   Do not replace them by sampled curves or affine proxy events.
2. Use the prospectively frozen minimal carriers in the type audit: the three
   shrinking flowbox cylinders, the outgoing and return bands, and the four
   normalized pullback domains.  Scout whether their physical embeddings have
   the required flow buffers and disjointness.  This scouting remains
   non-evidentiary.
3. Import the proved \(\kappa_\mu/\lambda_\mu\) seam and the resulting
   `B.OUT` embedding.  Do not construct a standalone 4096-cell
   \(\lambda\)-table.  Before treating an off-zero flowbox as evidence,
   rigorously enclose the composed physical initial state only on each of the
   three entrance discs actually integrated.  The earlier floating flowbox
   scout uses a design coordinate only and cannot serve as this certificate.
4. The terminal/aperture/label/cut functions, the four distinct side
   occurrences, all pullback maps, and the per-carrier subdivision and
   Taylor-order budgets are now frozen prospectively.  Run the structural
   checker before each complete rigorous calculation and reject any mutation
   of these objects.
5. Validate the three narrow channels and artificial laterals on the v2 bridge:
   event speeds, containment and flow-domain buffers, inactive-face gaps,
   conormal rank, and every empty/nonempty sign incidence.  A nonempty
   pairwise-time tie uses conormal rank, never a fictitious positive time gap.
6. Compute one exhaustive connected-component first-event census at `r=0`,
   then certify common-face gluing and a uniform neat isotopy across the fixed
   4096 bridge cells.  Any residual, duplicate component, failed box, or budget
   exhaustion yields `INCONCLUSIVE`.
7. Freeze dimensionless scales and take `m0` only as the minimum of the actual
   certified positive lower bounds, with the bridge margin at least `m0/2`.
   Finally bind the transported algebraic, homoclinic, pole, and residual traces
   and the proper phase arc.
8. Only after all sections pass the structural audit may the frozen binary make
   the first full run.  Its resulting certificates require a separate checker
   before any `V2.EVENT_ATLAS` claim can become `PASS`.

This route constructs the smallest physical van der Pol atlas suggested by the
three existing rigorous source objects.  It does not attempt to reproduce an
arbitrary atlas from the abstract existence proof.

## Structural checks

```bash
python3 validation/rigorous/check_p2e_event_atlas_v2.py --pretty
python3 -m unittest validation.rigorous.tests.test_p2e_event_atlas_v2 -v
```
