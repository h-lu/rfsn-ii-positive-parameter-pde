# Claim register

This table is the authoritative statement of what the repository may claim.
Change a status only in the same commit that adds the cited proof or archived
certificate.

| ID | Statement | Status | Required evidence |
|---|---|---|---|
| B1 | For all sufficiently small positive diffusion, the Brusselator stationary spatial system has a symmetric homoclinic orbit continuing the transverse RFSN-II core orbit. | Proposed | Weighted stable/unstable-manifold theorem and reversible implicit-function argument |
| B2 | The orbit in B1 gives a positive-concentration localized stationary PDE profile with explicit amplitude and width scales. | Proposed | Uniform bounds, inverse scaling, positivity and tail estimates |
| B3 | Fixed finite-winding or multipulse core patterns persist in the positive-parameter Brusselator. | Proposed | Separate finite family of transverse matching arguments; B1 alone does not imply this |
| V1 | The positive-parameter van der Pol stationary spatial system is reversible exact Hamiltonian with the stated first integral and primitive. | Derived | Direct calculation recorded with conventions and primary-source comparison |
| V2 | The saddle-focus, transverse homoclinic, and compact central first-hit data persist uniformly in a positive parameter wedge. | Proposed | Analytic persistence theorem and, if quantitative bounds are claimed, rigorous validation |
| V3 | The positive-parameter pole admits a regular-singular compactification with a well-defined action finite part. | Proposed | Compactified vector field, invariant set, indicial calculation, entry theorem, and finite-part proof |
| V4 | The positive-parameter outer algebraic channel has a normally expanding, third-order-bunched future-staying invariant hypersurface. | Proposed | Outer compactification and parameter-dependent invariant-manifold theorem |
| V5 | The future-staying hypersurface in V4 matches through the intermediate chart to the central algebraic sheet with two parameter derivatives and action-cut covariance. | Proposed | Full central--intermediate--outer matching theorem |
| V6 | The positive-parameter van der Pol system has an exhaustive high-winding return/first-exit relation with two compatible action finite parts. | Proposed | V2--V5 plus clean stratified persistence and exact-action assembly |
| V7 | Bounded symbolic itineraries in V6 yield stationary periodic, multipulse, or aperiodic spatial PDE patterns. | Proposed | Coding theorem and a precise translation to the original spatial variable |
| S1 | One or more patterns from B2 or V7 are temporally stable under the PDE flow. | Deferred | Bloch/Evans spectral analysis and nonlinear stability theorem |
| E1 | A predicted pattern is observed in a calibrated physical or chemical experiment. | Deferred | Dimensional model calibration, preregistered observable, and experimental data |

## Rules

- A formal asymptotic calculation is not a proof of existence or entry into an
  end channel.
- A non-rigorous computation may change a status only to Numerically observed.
- Computer-assisted means that every claim-bearing computation is interval
  rigorous, fixed to an immutable source version, and independently replayable.
- A result imported from the flagship paper must retain all of its hypotheses;
  positive-parameter persistence is never implicit.
