# Proof-interface audit for Theorem B

**Audit date:** 2026-08-28  
**Verdict:** PASS relative to the imported computer-assisted Core Lemma

This is an independent reconstruction of the proof spine in
[LOCALIZED_PROFILE_PROOF.md](LOCALIZED_PROFILE_PROOF.md). It records whether
each conclusion follows with the stated quantifiers; it is not a second
computer-assisted proof of the core orbit.

## 1. Required imported statement

Only one model-specific external statement is required:

\[
\begin{gathered}
 \Gamma_0\text{ is the selected nonconstant symmetric homoclinic of }F_0,\\
 c_0=\Gamma_0(0)\in\operatorname{Fix}\mathcal R,\qquad
 W^u_0(0)\pitchfork\operatorname{Fix}\mathcal R\text{ at }c_0,\\
 U_0(0)\ne0,\qquad V_0(0)\ne0.
\end{gathered}
\tag{1}
\]

The first-hit information and shooting box locate this selected orbit and
support the certificate, but the local positive-parameter argument uses the
intersection and its transversality. It does not use a Hamiltonian
\(W^u\)-\(W^s\) intersection, action, return--exit map, or two-end theorem.

## 2. Clause-by-clause reconstruction

| Interface | Check | Result |
|---|---|---|
| PDE to scaled family | Substitution of \(r=d^{1/4}\), \(\xi=x/r\), \(u=1+r^2U\), \(v=1+r^4V\), and the momentum scalings gives the full polynomial field \(F_r\), not only a leading expansion. The clock agrees with the core source. | PASS |
| Uniform hyperbolicity | The four eigenvalues are \(\pm\alpha(r)\pm i\beta(r)\), with a fixed spectral gap for small \(|r|\). Smooth Riesz projections identify the moving stable and unstable spaces with fixed two-dimensional parameter spaces. | PASS |
| Parameter-dependent local manifolds | The cutoff Lyapunov--Perron operator is a strict contraction on one fixed weighted half-line space. Spectral gaps control the \(r\)-derivative kernels, so the fixed point and local graph are \(C^1\) in \((r,b)\) with uniform tails. | PASS |
| Finite flowout | A compact source patch and bounded flight-time interval lie in a common compact flow tube at \(r=0\); smooth ODE dependence supplies a common positive-\(r\) flow domain and \(C^1\) dependence. | PASS |
| Reversible matching | The imported shooting determinant is exactly the derivative of the projection normal to \(\operatorname{Fix}\mathcal R\). Its invertibility is equivalent to \(W^u_0(0)\pitchfork\operatorname{Fix}\mathcal R\) for the selected two-dimensional patch. The finite-dimensional implicit-function theorem continues one local intersection \(c_r\). | PASS |
| Full homoclinic | The negative half-orbit exists by the unstable-manifold construction. Reflection at \(c_r\in\operatorname{Fix}\mathcal R\) produces the positive half-orbit; reversibility and ODE uniqueness make the glued curve a smooth global homoclinic. No positive-\(r\) first integral is used. | PASS |
| Full-line weighted family | A fixed time cut before the center removes the moving flight-time shift. The half-line \(C^1\) estimate, finite-time dependence, and reflection give \(r\mapsto Z_r\in X_\eta\) of class \(C^1\), with constants uniform in \(r\). | PASS |
| Positivity | Uniform boundedness of \(U_r,V_r\), combined with the exact factors \(r^2,r^4\), yields \(u_d,v_d\ge1/2\) after an existential reduction of \(r_0\). No sign assumption on the scaled core profile is needed. | PASS |
| Amplitudes | Uniform convergence \(Z_r\to Z_0\) and exact inverse scaling give the limits \(d^{-1/2}\|u_d-1\|_\infty\to\|U_0\|_\infty\) and \(d^{-1}\|v_d-1\|_\infty\to\|V_0\|_\infty\). The certified center bounds make both limits nonzero. | PASS |
| Widths | Nonzero center values and uniform derivative bounds give a fixed inner half-height interval in \(\xi\); exponential tails give a fixed outer interval. Multiplication by \(x=r\xi\) yields the central connected half-height widths \(\Theta(d^{1/4})\). | PASS |

The resulting quantifier order is

\[
 \exists\,r_0,C,\eta,c,C_w,\ \exists\,Z\in C^1([0,r_0],X_\eta)
 \quad
 \forall\,r\in(0,r_0]\ \forall\,x\in\mathbb R.
\tag{2}
\]

The constants and branch depend on the selected core orbit but not on
\(r,d,x\). The differentiability in (2) is with respect to \(r=d^{1/4}\).
The number \(d_0=r_0^4\) is not explicit.

## 3. Presentation obligations for the paper

The audit found no missing mathematical arrow, but the companion paper must
make the following interfaces explicit:

1. state (1) as the complete Core Lemma and label it computer-assisted;
2. either retain the weighted Lyapunov--Perron proof or cite an exact
   parameter-dependent invariant-manifold theorem and verify its hypotheses;
3. say “centered at the locally continued intersection” rather than implying
   a global phase normalization or global uniqueness;
4. call the observable in the theorem the **central connected half-height
   width** throughout;
5. distinguish the existential continuation neighborhood from an explicit
   validated diffusion interval; and
6. state that the result gives stationary existence only.

The evidence-access issue for (1) is separate from this analytic audit and is
tracked in [CORE_IMPORT_AUDIT.md](CORE_IMPORT_AUDIT.md).
