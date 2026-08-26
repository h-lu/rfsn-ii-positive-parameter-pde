# Claim register

This table is the authoritative statement of what the repository may claim.
Change a status only in the same commit that adds the cited proof or archived
certificate.

| ID | Statement | Status | Required evidence |
|---|---|---|---|
| B1 | For all sufficiently small positive diffusion, the Brusselator stationary spatial system has a symmetric homoclinic orbit continuing the transverse RFSN-II core orbit. | Proved | [Theorem B, items 1--2 and Sections 2--3](brusselator/LOCALIZED_PROFILE_PROOF.md), using the [frozen core import](brusselator/CORE_HOMOCLINIC_IMPORT.md) |
| B2 | The orbit in B1 gives a positive-concentration localized stationary PDE profile with explicit amplitude and width scales. | Proved | [Theorem B, items 3--5 and Sections 4--5](brusselator/LOCALIZED_PROFILE_PROOF.md), with the [exact inverse scaling](brusselator/MODEL_AND_SCALING.md) |
| B3 | Fixed finite-winding or multipulse core patterns persist in the positive-parameter Brusselator. | Proposed | Separate finite family of transverse matching arguments; B1 alone does not imply this |
| V1 | The positive-parameter van der Pol stationary spatial system is reversible exact Hamiltonian with the stated first integral and primitive. | Derived | [Direct calculation](van-der-pol/HAMILTONIAN_CHECK.md) with conventions and primary-source comparison |
| V2 | The saddle-focus, selected transverse homoclinic, and compact central first-hit data continue uniformly in a positive parameter wedge. | Proved | [Theorem V2 and its \(C^2\) continuation proof](van-der-pol/CENTRAL_CONTINUATION.md), using the [frozen core package](van-der-pol/CENTRAL_CORE_IMPORT.md) and [exact central bridge](van-der-pol/MODEL_AND_CENTRAL_CHART.md) |
| V3 | On a nonempty compact positive subbox of the V2 wedge, the pole admits a regular-singular compactification and action finite part, and a nonempty source window enters it uniformly. | Proved | [Theorem V3, global cone entry, indicial expansion, and finite-part proof](van-der-pol/POSITIVE_POLE_FINITE_PART.md) |
| V4 | The positive-parameter outer algebraic channel has a normally expanding, third-order-bunched future-staying invariant hypersurface. | Proved | [Theorem V4, exact outer compactification, intrinsic quotient estimates, and parameter-dependent corridor graph](van-der-pol/OUTER_FUTURE_STAYING.md) |
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
