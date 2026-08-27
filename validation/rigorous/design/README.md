# Rigorous-validation design scouts

Files in this directory are pre-registration design tools.  They may use
outward-rounded intervals to choose rational budgets, but their output is not
a validation certificate and does not discharge any obligation.

`p2b_jets_scout.cpp` evaluates the algebraic coefficient bounds and the
labelled-set Faà di Bruno recurrence proposed for the P2b mixed-jet
certificate.  Its default weight is (1/4); an alternative decimal weight
may be supplied only for sensitivity scouting.  The formal probe will accept
only the exact rational weight frozen in its versioned configuration.

The scout distinguishes two domains:

- the already-certified true-graph tube
  \(|u_1+H_{\mu,1}(u)|\le251/25000\), used for derivatives of the
  Lyapunov--Perron equation along the true half-orbit; and
- the radius-(1/100) source disk, used for the explicit block term.

It does not claim contraction of the nonlinear fixed-point map on a full
four-dimensional product ball.  The Neumann gate concerns only the
linearized Green operator along the true graph already supplied by P2a and
P2b0.

Any formal use requires a separately committed frozen configuration, a clean
strict-source run, schema and semantic checking, and the repository's
independent-replay policy.
