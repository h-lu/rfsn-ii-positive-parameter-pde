# Direct Hamiltonian check for the stationary van der Pol system

**Evidence status: Derived.**  This note records the sign and scaling
calculation behind claim V1.  It is an algebraic derivation, not the
positive-parameter return--first-exit theorem.  Its notation is reconciled
with every blow-up chart in
[MODEL_AND_CENTRAL_CHART.md](MODEL_AND_CENTRAL_CHART.md).

## Spatial system

Start from

\[
u_t=v-f(u)+d u_{xx},\qquad
v_t=\epsilon(a-u)+v_{xx},\qquad
f(u)=\frac13u^3-u.
\]

Assume \(\epsilon>0\) and \(\delta=\sqrt d>0\).  Let
\(y=x/\delta\), \(p=u_y=\delta u_x\), and \(q=v_x\).  A stationary solution
satisfies

\[
u_y=p,\qquad p_y=f(u)-v,\qquad
v_y=\delta q,\qquad q_y=\epsilon\delta(u-a).
\tag{1}
\]

Let \(F'(u)=f(u)\), for example

\[
F(u)=\frac1{12}u^4-\frac12u^2.
\]

Define

\[
\mathcal G_\delta
=\frac12(\epsilon p^2-q^2)
-\epsilon\bigl(F(u)+(a-u)v\bigr).
\tag{2}
\]

Along (1),

\[
\begin{aligned}
\frac{d}{dy}\mathcal G_\delta
={}&\epsilon p(f(u)-v)
-\epsilon\delta q(u-a)\\
&-\epsilon\bigl(f(u)p-pv+(a-u)\delta q\bigr)=0.
\end{aligned}
\]

Thus (2) is a first integral for every \(\delta>0\).

## Exact Hamiltonian convention

Set

\[
\lambda_\delta=\epsilon p\,du-\delta^{-1}q\,dv,
\qquad
\omega_\delta=d\lambda_\delta,
\qquad
H_\delta=-\mathcal G_\delta.
\tag{3}
\]

For the vector field \(X_\delta\) in (1), direct contraction gives

\[
\begin{aligned}
\iota_{X_\delta}\omega_\delta
={}&\epsilon(f(u)-v)\,du-\epsilon p\,dp\\
&-\epsilon(u-a)\,dv+q\,dq
=dH_\delta.
\end{aligned}
\]

Hence the \(y\)-flow (1) is exact Hamiltonian with the convention
\(\iota_X\omega=dH\).  For the physical \(x\)-flow,
\(X_x=\delta^{-1}X_y\), so the same primitive has Hamiltonian
\(-\mathcal G_\delta/\delta\).  This fixes the sign of both the Hamiltonian
and the action primitive used by the project.

The momentum variables

\[
\Pi=\epsilon p,\qquad \Theta=\delta^{-1}q
\]

give the parameter-independent primitive

\[
\lambda=\Pi\,du-\Theta\,dv
\]

and

\[
\mathcal G_\delta
=\frac{\Pi^2}{2\epsilon}-\frac{\delta^2\Theta^2}{2}
-\epsilon\bigl(F(u)+(a-u)v\bigr).
\]

The symbols \(\Pi,\Theta\) are physical canonical momenta and are not the
central variables \(P,Q\) used after blow-up.  All later changes of spatial
clock must transform the action integral derived from this primitive
explicitly.

## Reversibility

For

\[
\mathcal R(u,p,v,q)=(u,-p,v,-q),
\]

one checks

\[
D\mathcal R\,X_\delta=-X_\delta\circ\mathcal R,
\qquad
\mathcal R^*\lambda_\delta=-\lambda_\delta,
\qquad
\mathcal R^*\omega_\delta=-\omega_\delta.
\]

Thus the spatial flow is reversible and the reverser is anti-symplectic.

## Primary-source crosswalk

In the published version of Vo--Doelman--Kaper, the PDE is equation (1.1)
on p. 2619, the introductory and main physical stationary systems are
equations (1.2) on p. 2621 and (2.4) on p. 2627, and the fast system,
reverser, and conserved quantity are equations (2.6)--(2.8) on p. 2628.
The source states \(\mathcal G\), but not the full-system primitive (3).
Equations (2)--(3) above independently derive that primitive and fix this
repository's convention \(\iota_X\omega=dH\).

The central weights, clocks, shifted equilibrium energy, and exact conjugacy
to the flagship core are derived in
[MODEL_AND_CENTRAL_CHART.md](MODEL_AND_CENTRAL_CHART.md).  In particular, a
clock change rescales the Hamiltonian but leaves \(\int\lambda\) unchanged.

## Dependency boundary

This calculation alone establishes only the exact Hamiltonian structure of
the full positive-parameter stationary ODE.  The selected homoclinic and
compact central arrangement are proved separately in
[CENTRAL_CONTINUATION.md](CENTRAL_CONTINUATION.md).  Neither noncompact end,
either action finite part, nor the final return--exit theorem follows from
this calculation; those are V3--V7.
