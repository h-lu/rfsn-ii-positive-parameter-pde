# Direct Hamiltonian check for the stationary van der Pol system

This note records the sign and scaling calculation behind claim V1.  It is an
algebraic derivation, not the positive-parameter return--first-exit theorem.

## Spatial system

Start from

\[
u_t=v-f(u)+d u_{xx},\qquad
v_t=\epsilon(a-u)+v_{xx},\qquad
f(u)=\frac13u^3-u.
\]

Let \(\delta=\sqrt d\), \(y=x/\delta\), \(p=u_y\), and \(q=v_x\).  A stationary
solution satisfies

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

Hence (1) is exact Hamiltonian with the convention
\(\iota_X\omega=dH\).  This fixes the sign of both the Hamiltonian and the
action primitive used by the project.

The momentum variables

\[
P=\epsilon p,qquad Q=\delta^{-1}q
\]

give the parameter-independent primitive

\[
\lambda=P\,du-Q\,dv
\]

and

\[
\mathcal G_\delta
=\frac{P^2}{2\epsilon}-\frac{\delta^2Q^2}{2}
-\epsilon\bigl(F(u)+(a-u)v\bigr).
\]

All later changes of spatial clock must transform the action integral derived
from this physical primitive explicitly.

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

## Dependency boundary

This calculation establishes only the exact Hamiltonian structure of the full
positive-parameter stationary ODE.  It does not establish persistence of the
homoclinic orbit, either noncompact end, the first-hit arrangement, or any
action finite part.  Those are claims V2--V7 and remain Proposed.
