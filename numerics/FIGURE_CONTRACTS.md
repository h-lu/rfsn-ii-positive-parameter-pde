# Figure contracts

## Figure 1: theorem-to-pattern dictionary

- Reader question and result served: how an orbit of the stationary spatial
  ODE becomes a visible PDE profile.
- Status: `SCHEMATIC`.
- System, parameters, coordinates, and time convention: generic stationary
  PDE; the orbit time is the independent spatial variable, not PDE time.
- What the figure must not imply: stationary symbolic dynamics is not temporal
  chaos, and an exit orbit is not a bounded stationary pattern.
- Production route: `numerics/run_atlas.py`, Matplotlib vector output.
- Final placement and size: standalone landscape figure, designed at
  \(10.2\times5.6\) inches; do not reduce below about 9.5 inches wide without
  splitting the dictionary into panels.

## Figure 2: Brusselator scaling

- Reader question and result served: do computed positive-diffusion pulses
  exhibit the amplitudes and widths stated in Theorem B?
- Status: `COMPUTED/E1`.
- System and parameters: \(A=B=1\), \(d=r^4\); exact central coordinate
  \(\xi=x/r\).
- Objects: symmetric nontrivial collocation solutions continued from the
  certified core midpoint.
- What the figure must not imply: no explicit analytic \(r_0\), temporal
  stability, uniqueness, or interval validation.
- Checks: scaled ODE and boundary residuals, tail norm, positivity, branch
  identity, small-parameter power fits.
- Final placement and size: full landscape figure, designed at
  \(11.2\times6.7\) inches and intended to remain at least 10.5 inches wide.
  Color and line style both encode the same parameter across profile panels.

## Figure 3: van der Pol winding and period

- Reader question and result served: what does increasing the high-winding
  label do to a concrete stationary PDE profile and its spatial period?
- Status: `COMPUTED/E1`.
- System and parameters: \(r=0.08\), \(a_2=0\), \(\epsilon=1\),
  \(d=r^4\), \(a=1\); universal time
  \(\xi=\epsilon^{1/4}x/r\).
- Objects: finite samples from two reversible zero-energy periodic families;
  their approach to the numerically continued homoclinic is an observed trend,
  not a numerical proof of the infinite-family limit.
- Line meaning: color and style encode relative winding in the upper panels;
  marker, color, and style encode family in the lower panels.  The two
  families receive separate intercepts and one fitted period slope.
- What the figure must not imply: the plotted relative labels are not
  certified absolute V7 labels; the profiles are not proved temporally stable.
- Checks: closure, energy drift, event order, period slope, and action trend.
- Final placement and size: full landscape figure, designed at
  \(10.6\times7.0\) inches and intended to remain at least 10 inches wide.

## Figure 4: Turing and canard context

- Reader question and result served: how the stationary theorem is related to
  finite-wavenumber neutral/Turing curves and canard-organized geometry.
- Status: `MIXED` (`EXACT` neutral-curve formulas plus `SCHEMATIC` geometry and
  `COMPUTED` parameter markers).
- What the figure must not imply: the theorem branch is not proved to emerge
  from the Turing point; high winding is not itself a canard; existence does
  not decide temporal selection or experimental observability.
- Checks: parameter conventions, threshold formulas, visual separation of
  return and exit, final PDF/SVG/PNG inspection.
- Final placement and size: full landscape figure, designed at
  \(10.8\times7.0\) inches and intended to remain at least 10 inches wide.

## Figure 5: numerical convergence

- Reader question and result served: are the displayed Brusselator quantities
  stable under enlargement of the truncated half-line?
- Status: `COMPUTED/QA`.
- System and parameters: \(A=B=1\), \(r=0.1\),
  \(L_\xi\in\{16,20,24,28\}\).
- What the figure must not imply: convergence of ordinary floating-point
  collocation is not an interval enclosure.
- Checks: common-observable differences, normalized scaled-ODE residual, and
  tail norm.
- Final placement and size: full-width QA figure, designed at
  \(8.8\times3.5\) inches and intended to remain at least 8 inches wide.
