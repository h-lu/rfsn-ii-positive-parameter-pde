# Figure contract: positive two-end geometry

- **Reader question and result served:** From the physical source collar, how
  does high winding near the saddle-focus lead to return, a finite-distance
  pole, or an infinite-distance algebraic end, and where does the
  central \(K_2\) gate--resolved \(K_1\) bridge--outer future-staying sheet
  matching enter?
- **Status:** `SCHEMATIC`.
- **Coordinates and time:** qualitative projection of stationary spatial
  dynamics in the physical spatial orientation; no Euclidean distance or
  curvature is quantitative.
- **Objects:** source and return sections; the saddle-focus equilibrium;
  representative high-winding passage; physical first-event carriers; pole
  and algebraic terminal branches.  The enlarged matching-chart inset
  separately identifies the central \(K_2\) gate, the resolved \(K_1\) bridge,
  and the outer future-staying sheet.
- **Panels and reading order:** read the main geometry from the source collar
  through the outgoing first-event cell; then use the lower-right inset to
  read the analytic continuation from the central gate through the resolved
  chart to the outer sheet.
- **Encoding:** return is blue/solid, pole is red/dash-dot, algebraic is
  green/dashed, and auxiliary finite exits are gray/dotted.  Every color has
  a redundant line-style or direct-label cue.  Green dashed arrows in the
  inset denote chart matching/continuation, not physical spatial-time flow.
- **Must not imply:** temporal stability or selection, a Turing bifurcation,
  canard tracking, a global phase-space partition, quantitative basin size,
  equality of the pole and algebraic compactifications, or that the three
  inset boxes are successive points on one plotted physical trajectory.
- **Production:** vector PDF and review PNG from
  `figures/positive_two_end_geometry.py`.
- **Placement:** before the main theorem at full text width.
- **Checks:** arrow orientation, distinct end types, grayscale legibility,
  readable labels at manuscript size, explicit `schematic` disclosure.

# Figure contract: computed stationary profiles

- **Reader question and result served:** What do representative periodic and
  localized stationary solutions produced by the V1--V7 chain look like after
  returning to the original PDE variables?
- **Status:** `COMPUTED/E1`, non-claim-bearing.
- **System, parameters, and coordinates:** the physical van der Pol PDE at
  \((r,a_2,\epsilon)=(0.08,0,1)\), equivalently
  \((d,a,\epsilon)=(4.096\times10^{-5},1,1)\); horizontal coordinate
  \(\mathsf x\), vertical coordinate \(u-a\).
- **Objects and panels:** panel (a) shows the saved B1 and A2 numerical-family
  periodic profiles over one physical period; panel (b) shows the saved
  one- through four-pulse full-ODE candidates on their truncated physical
  domains.
- **Encoding:** every family is distinguished by line style as well as color;
  the horizontal dotted line is the homogeneous state, not a separatrix.
- **Must not imply:** placement of the parameter point in a certified theorem
  box, exact V6/V7 word identification, temporal stability, Turing selection,
  canard tracking, uniqueness, or experimental observability.
- **Production and data:**
  `figures/computed_stationary_profiles.py`, reading
  `numerics/results/vdp_v1_v7/v7_periodic.npz` and
  `v7_multipulses.npz`; reproduce with `make figure`.
- **Placement:** after the interpretation of the main theorem, at full text
  width.
- **Checks:** saved full-state closure/energy and stationary-PDE residuals;
  vector PDF; grayscale-redundant line styles; final manuscript-page render.
