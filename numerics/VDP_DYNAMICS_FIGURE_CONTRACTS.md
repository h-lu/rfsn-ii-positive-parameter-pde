# Van der Pol temporal and slow--fast screening figure contracts

These contracts govern the figures produced after the frozen configuration-v4
V1--V7 candidate atlas.  Unless a panel is explicitly labelled `EXACT/DERIVED`,
its evidence level is `COMPUTED/E1`: ordinary floating-point prescreening used
to choose the next rigorous or analytical task.  None of these figures is an
Issue #7 interval certificate.

## Figure D1: homogeneous dispersion and the stationary-Turing obstruction

- **Reader question and result served:** Can the computed stationary patterns
  be interpreted as a classical stationary Turing branch selected from a
  temporally stable homogeneous state?  The exact trace/determinant inequalities
  answer no for this two-component diffusion matrix; the sampled dispersion
  curves locate the current point and one deliberately remote nonclassical
  finite-wave-number example.
- **Status:** `MIXED` -- exact algebraic identities and a floating-point scan.
- **System, parameters, coordinates, and time convention:** Physical PDE time
  (t), physical Fourier wave number (k),
  (d=r^4), (a=1+sqrt\epsilon r^3a_2).  The primary point is
  ((r,a_2,\epsilon)=(0.08,0,1)); the remote diagnostic example changes only
  (a_2) and is not a continuation of a V7 profile.
- **Objects, directions, and representative choices:** The spectral abscissa
  derived from the two homogeneous-symbol eigenvalue branches (both branches
  remain in the saved data, while the figure displays the leading rate), the
  determinant-zero threshold in (a_2), and the frozen (3^3) parameter
  classification.
- **Panels and reading order:** (a) exact implication diagram/inequalities;
  (b) primary dispersion; (c) remote finite-(k) real-unstable band;
  (d) threshold and sampled parameter locations.
- **Line, marker, fill, color, and arrow meanings:** Solid blue is the primary
  spectral abscissa; dashed orange is the remote diagnostic example; a black
  zero line is temporal neutrality.  Markers denote evaluated points.  No
  filled region may be drawn between sparse parameter samples as if certified.
- **What the figure must not imply:** No nonlinear Turing branch, temporal
  pattern selection, stability of a nonconstant profile, or experimental
  observability.  A finite-(k) real-unstable band when (k=0) is already
  unstable must not be labelled a classical Turing instability.
- **Caption draft:** *Exact homogeneous-symbol inequalities exclude a
  stationary Turing instability from a stable homogeneous state.  The frozen
  V7 point lies on the (k=0) Hopf boundary and has no finite-(k) stationary
  band; a remote example illustrates a nonclassical finite-(k) band after the
  zero mode has already destabilized.*
- **Production route and editable source:** Matplotlib from
  `numerics/render_vdp_dynamics_figures.py`; PDF and SVG are the editable
  vector outputs.
- **Data, solver, and reproduction command, if computed:** Analytic quadratic
  formulas and `numerics.vdp_turing`; reproduced by
  `python3 numerics/run_vdp_dynamics_screening.py`.
- **Final placement and size:** Standalone landscape figure, at most four
  panels, readable at full manuscript text width.
- **Checks needed before delivery:** Direct eigensolver cross-check; zero line
  visible; primary/remote parameters printed on-panel; exact and computed
  badges distinct; SVG text and PNG rendering inspected.

## Figure D2: Bloch/Floquet spectrum of saved periodic profiles

- **Reader question and result served:** Do the saved V7 periodic stationary
  profiles show a robust candidate spectral gap, a resolved instability, or
  only a discretization-sensitive signal under Bloch perturbations?
- **Status:** `COMPUTED`.
- **System, parameters, coordinates, and time convention:** Linearization of
  the physical time-dependent PDE about each saved periodic physical profile;
  Bloch phase or exponent is a spatial boundary twist, not time.
- **Objects, directions, and representative choices:** Rightmost computed
  eigenvalues over the Brillouin zone, the translational eigenvalue at the
  co-periodic point, leading spectral abscissa versus Bloch phase, and at least
  two spatial resolutions.
- **Panels and reading order:** (a) spectral clouds for representative short
  and long periods; (b) rightmost real part versus Bloch phase for all saved
  profiles; (c) co-periodic translation-mode residual; (d) refinement and
  decision labels.
- **Line, marker, fill, color, and arrow meanings:** One color per saved
  numerical family; markers are computed Bloch samples; line segments only
  guide the eye.  Open symbols denote the expected translation-neutral mode.
- **What the figure must not imply:** Finite Fourier/collocation matrices do not
  prove spectral completeness, sideband stability, Evans-function winding,
  nonlinear orbital stability, or dynamic selection.  A missing positive
  eigenvalue is not a stability proof.  Current `A/B` labels are numerical
  family labels, not certified V7 edge words.
- **Caption draft:** *Candidate Bloch spectra of the saved periodic stationary
  profiles.  Resolution comparisons and the translation mode diagnose the
  finite-dimensional calculation; all stability labels remain prescreening
  signals rather than spectral or nonlinear theorems.*
- **Production route and editable source:** Matplotlib from
  `numerics/render_vdp_dynamics_figures.py`.
- **Data, solver, and reproduction command, if computed:** Saved
  `v7_periodic.npz` profiles and `numerics.vdp_bloch_stability`; reproduced by
  the dynamics-screening master command.
- **Final placement and size:** Full text width; complex spectral panels use
  equal semantic scales where comparison is intended.
- **Checks needed before delivery:** Refinement agreement reported rather than
  hidden; conjugate symmetry checked; co-periodic translation mode located;
  positive real half-plane visibly shaded but not called a proof region;
  parameter and evidence badges included.

## Figure D3: localized-pulse finite-window spectra and perturbation growth

- **Reader question and result served:** What temporal signals are visible for
  the one- through four-pulse saved profiles, and are they insensitive to a
  first change of grid, boundary condition, and time step?
- **Status:** `COMPUTED`.
- **System, parameters, coordinates, and time convention:** Physical PDE time
  about saved finite-window multipulse profiles.  Boundary conditions apply to
  perturbations.  The nonlinear run uses the frozen-profile residual-subtracted
  perturbation equation so that zero perturbation remains exactly fixed in the
  discrete model.
- **Objects, directions, and representative choices:** Leading finite-window
  eigenvalues under Neumann and periodic perturbation boundary conditions;
  grid refinement; deterministic small perturbations; dominant-mode
  perturbations; RMS perturbation versus physical PDE time.
- **Panels and reading order:** (a) physical pulse profiles; (b) rightmost
  spectral values and boundary/grid variation; (c) RMS histories;
  (d) observed versus linear-envelope amplification.
- **Line, marker, fill, color, and arrow meanings:** Color encodes pulse count;
  marker shape encodes grid/boundary choice.  In the time panel, solid marked
  curves are leading-mode perturbations and dashed curves are the deterministic
  generic perturbations; both use the finer half time step.  Error bars, if
  present, are sensitivity ranges, never probability or rigorous enclosures.
- **What the figure must not imply:** A truncated-window spectrum is not a
  whole-line Evans spectrum.  Residual-subtracted evolution is a perturbation
  diagnostic, not direct evolution of the original approximate profile.
  Short-time growth/decay is not nonlinear asymptotic stability or pattern
  selection.
- **Caption draft:** *Finite-window temporal screening of the saved localized
  profiles.  Boundary, grid, and time-step comparisons support a leading
  positive-growth candidate, while generic perturbations initially decay
  because their projection on that mode is small.  These finite-window and
  finite-time signals do not establish spectral or nonlinear stability.*
- **Production route and editable source:** Matplotlib from
  `numerics/render_vdp_dynamics_figures.py`.
- **Data, solver, and reproduction command, if computed:** Saved
  `v7_multipulses.npz` profiles and `numerics.vdp_temporal_screen`; reproduced
  by the dynamics-screening master command.
- **Final placement and size:** Full text width, four panels maximum.
- **Checks needed before delivery:** Zero-perturbation defect displayed;
  initial amplitude and final time stated; leading-mode eigensolver residual
  recorded; boundary and grid sensitivity not collapsed into one number;
  physical profile truncation endpoints visible.

## Figure D4: fold passage, FSN-II degeneracy, and canard stop rule

- **Reader question and result served:** Which parts of the computed geometry
  are genuinely visible near the positive fold, and why is that still not a
  maximal-canard identification?
- **Status:** `MIXED` -- exact critical-manifold/desingularized identities,
  one published leading canard curve, and finite-profile diagnostics.
- **System, parameters, coordinates, and time convention:** Stationary spatial
  fast time (y=x/r^2), physical space (x), and reduced desingularized time
  are named separately.  The critical manifold is (p=0,v=f(u)), with folds
  (u=\pm1).
- **Objects, directions, and representative choices:** Physical periodic and
  multipulse profiles near (u=1); fold crossings; the fast normal quantity
  (f'(u)=u^2-1); the reduced linear product
  (2\epsilon u_f(u_f-a)); the leading published maximal-canard curve
  (a_{2,c}=-(5\sqrt\epsilon/48)r+O(r^3)); and the saved outer leg, which stays
  at (u\ge5).
- **Panels and reading order:** (a) profile/fold intersections; (b) critical
  manifold with saddle/elliptic fast-normal regions; (c) parameter comparison
  with the leading maximal-canard curve; (d) explicit evidence ladder and stop
  rule.
- **Line, marker, fill, color, and arrow meanings:** The fold is black dashed;
  computed profiles are colored; saddle-type normally hyperbolic portions and
  elliptic portions use different light backgrounds; published leading curve
  is dashed with an explicitly labelled unknown (O(r^3)) remainder.
- **What the figure must not imply:** Crossing a fold level is not following a
  repelling slow manifold; singular FSN-II degeneracy at (a=1) is not a
  finite-parameter maximal canard; proximity to a leading asymptotic curve is
  not an enclosure; saddle-focus winding near the central equilibrium is not
  canard rotation.  The far outer segment alone cannot demonstrate a fold
  canard.
- **Caption draft:** *The saved finite-parameter profiles repeatedly cross the
  positive fold level and the current singular reduced problem is FSN-II
  degenerate.  The sample does not equal the displayed leading maximal-canard
  curve, whose remainder is not enclosed, and no finite-parameter slow-manifold
  intersection has been continued.  The evidence therefore stops at fold
  passage, not canard identification.*
- **Production route and editable source:** Matplotlib from
  `numerics/render_vdp_dynamics_figures.py`.
- **Data, solver, and reproduction command, if computed:** Saved V7 profiles,
  the V4--V5 outer candidate, and `numerics.vdp_canard_diagnostics`; reproduced
  by the dynamics-screening master command.
- **Final placement and size:** Full text width; the stop-rule panel must remain
  legible in grayscale.
- **Checks needed before delivery:** Physical and desingularized clocks not
  conflated; exact/derived/computed elements labelled; asymptotic remainder
  not drawn as a numerical confidence band; fold crossing counts spot-checked
  against profiles; final PNG and SVG visually inspected.
