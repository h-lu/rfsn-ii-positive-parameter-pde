# Claim register

This table is the authoritative statement of what the repository may claim.
Change a status only in the same commit that adds the cited proof or archived
certificate.

| ID | Statement | Status | Required evidence |
|---|---|---|---|
| T1 | A compact saddle-type NHIM on a fixed doubled collar persists as a parameter-dependent relative overflowing invariant graph on the original manifold with corners, with the stated mixed regularity and fixed-extension uniqueness. | Proved | [Local relative overflowing NHIM theorem and K1 corollary](theory/RELATIVE_OVERFLOWING_NHIM.md) |
| T2 | A finite compatible atlas of already constructed local marked return/coding presentations satisfying the frozen covariance hypotheses descends to one physical return/first-event relation, compatible mixed two-jets, and marking-independent closed periods and actions. | Proved | [Finite marked-atlas descent, Proposition 1](theory/FINITE_MARKED_ATLAS_DESCENT.md) |
| T2G | The van der Pol family admits one globally normalized nonlinear exact saddle chart with zero deck recoding and one parameter-global winding alphabet. | Proposed | [Conditional global-cut criterion; the saddle-chart cocycle is now locally trivialized, but the full event cut and zero deck recoding remain open](theory/FINITE_MARKED_ATLAS_DESCENT.md) |
| B1 | For all sufficiently small positive diffusion, the Brusselator stationary spatial system has a symmetric homoclinic orbit continuing the transverse RFSN-II core orbit. | Proved | [Theorem B, items 1--2 and Sections 2--3](brusselator/LOCALIZED_PROFILE_PROOF.md), using the [frozen core import](brusselator/CORE_HOMOCLINIC_IMPORT.md) |
| B2 | The orbit in B1 gives a positive-concentration localized stationary PDE profile with explicit amplitude and width scales. | Proved | [Theorem B, items 3--5 and Sections 4--5](brusselator/LOCALIZED_PROFILE_PROOF.md), with the [exact inverse scaling](brusselator/MODEL_AND_SCALING.md) |
| B3 | Fixed finite-winding or multipulse core patterns persist in the positive-parameter Brusselator. | Proposed | Separate finite family of transverse matching arguments; B1 alone does not imply this |
| V1 | The positive-parameter van der Pol stationary spatial system is reversible exact Hamiltonian with the stated first integral and primitive. | Derived | [Direct calculation](van-der-pol/HAMILTONIAN_CHECK.md) with conventions and primary-source comparison |
| V2 | The saddle-focus, selected transverse homoclinic, and compact central first-hit data continue uniformly in a positive parameter wedge. | Proved | [Theorem V2 and its \(C^2\) continuation proof](van-der-pol/CENTRAL_CONTINUATION.md), using the [frozen core package](van-der-pol/CENTRAL_CORE_IMPORT.md) and [exact central bridge](van-der-pol/MODEL_AND_CENTRAL_CHART.md) |
| V3 | On a nonempty compact positive subbox of the V2 wedge, the pole admits a regular-singular compactification and action finite part, and a nonempty source window enters it uniformly. | Proved | [Theorem V3, global cone entry, indicial expansion, and finite-part proof](van-der-pol/POSITIVE_POLE_FINITE_PART.md) |
| V4 | The positive-parameter outer algebraic channel has a normally expanding, third-order-bunched future-staying invariant hypersurface. | Proved | [Theorem V4, exact outer compactification, intrinsic quotient estimates, and parameter-dependent corridor graph](van-der-pol/OUTER_FUTURE_STAYING.md) |
| V5 | The future-staying hypersurface in V4 matches through the intermediate chart to the central algebraic sheet with two parameter derivatives and action-cut covariance. | Proved | [Theorem V5, including the T1 corner application, final-annulus rerun, endpoint adjoint, and matching operator](van-der-pol/CENTRAL_OUTER_MATCHING.md) |
| V5A | The matched positive-parameter algebraic end has reference-normalized physical length and action finite parts with mixed two-jets, strict V5-arrival containment, admissible-coordinate covariance, and strict finite-branch composition. | Proved | [Theorem V5A, fixed-\(Q\) flat shadowing, arrival-label estimate, and reference-tail subtraction](van-der-pol/OUTER_ALGEBRAIC_FINITE_PART.md) |
| V6 | The positive-parameter van der Pol system has an exhaustive physical high-winding return/first-exit relation with finite-atlas mixed data and two compatible action finite parts. | Proved | [Theorem V6 and the whole-cell pullback, finite-atlas descent, stratification, and exact-action proof](van-der-pol/TWO_END_RETURN_EXIT_AND_PDE.md), using T2 and the strictly bounded [frozen modular import](van-der-pol/RETURN_EXIT_CODING_IMPORT.md) |
| V7 | In every local marking, bounded V6 itineraries yield stationary periodic, multipulse, or aperiodic spatial PDE patterns; the physical profiles and closed observables agree on marking overlaps. | Proved | [Theorem V7, finite-atlas covariance, completed-section coding, and exact inverse PDE scaling](van-der-pol/TWO_END_RETURN_EXIT_AND_PDE.md), using V6, the frozen coding module, and the V1 inverse scaling |
| V8 | Any smooth periodic stationary van der Pol profile satisfying the strict moment inequality (6) has a real positive co-periodic temporal eigenvalue; for the frozen choice \(\lambda_0=0.01\), the eigenvalue lies in \((0.01,2)\). | Proved | [Self-adjoint operator-pencil reduction and moment criterion](van-der-pol/A2_PERIODIC_SPECTRAL_INSTABILITY.md) |
| V8A | At \((r,a_2,\epsilon)=(0.08,0,1)\), a true periodic stationary profile in the frozen A2 shooting box satisfies the V8 moment inequality and is therefore co-periodically spectrally unstable, with a real eigenvalue \(\lambda_*\in(0.01,2)\). | Local mathematical PASS; non-claim-bearing | The [CAPD multiple-shooting and interval-moment validator](validation/a2_periodic/README.md) proves the two mathematical inputs locally.  Independent-machine replay is still required before promotion to `Computer-assisted` under this register. |
| V9 | Any exponentially localized stationary van der Pol homoclinic satisfying the whole-line strict moment inequality (5), the displayed essential-spectrum gap, and the large-endpoint positivity condition has a real positive whole-line \(L^2\) temporal eigenvalue. | Proved | [Whole-line self-adjoint operator pencil, moment identity, and essential-spectrum isolation](van-der-pol/PULSE_1_SPECTRAL_INSTABILITY.md) |
| V9A | At \((r,a_2,\epsilon)=(0.08,0,1)\), the P2c selected primary homoclinic represented by the frozen `pulse_1` seed satisfies the V9 hypotheses and has a real whole-line \(L^2\) eigenvalue \(\lambda_*\in(0.01,2)\). | Local mathematical PASS; non-claim-bearing | The [target-point P2c containment and augmented interval-moment validator](validation/pulse_1/README.md) proves the compact moment and imports the hash-bound P2c exponential tail.  Independent-machine replay is still required before promotion to `Computer-assisted`. |
| V10 | No stable homogeneous equilibrium of the temporal van der Pol PDE can undergo a classical stationary finite-wavenumber Turing onset; the frozen positive box is separated from the stationary-neutral curve by the exact bracket margin \(49/25\). | Proved | [Exact Fourier-symbol proposition, frozen-box corollary, and terminology boundary](van-der-pol/CLASSICAL_STATIONARY_TURING_EXCLUSION.md), also stated in the companion manuscript |
| S1 | One or more patterns from B2 or V7 are temporally stable under the PDE flow. | Deferred | Bloch/Evans spectral analysis and nonlinear stability theorem |
| E1 | A predicted pattern is observed in a calibrated physical or chemical experiment. | Deferred | Dimensional model calibration, preregistered observable, and experimental data |

## Rules

- A formal asymptotic calculation is not a proof of existence or entry into an
  end channel.
- A non-rigorous computation may change a status only to Numerically observed.
- A local mathematical PASS records an outward-rounded proof on the locked
  current-machine toolchain, but is not a public computer-assisted claim until
  the required independent replay is archived.
- Computer-assisted means that every claim-bearing computation is interval
  rigorous, fixed to an immutable source version, and independently replayable.
- A result imported from the flagship paper must retain all of its hypotheses;
  positive-parameter persistence is never implicit.
