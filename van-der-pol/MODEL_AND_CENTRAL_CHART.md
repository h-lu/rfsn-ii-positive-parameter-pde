# Van der Pol model, clocks, and the exact central bridge

**Evidence status: Derived.**  The source equations and blow-up weights are
frozen to the published version of Vo--Doelman--Kaper.  Every further formula
in this note is obtained from them by exact substitution.  No positive-end,
first-exit, finite-part, or coding statement is asserted here.

## 1. PDE convention and positive parameter wedge

The PDE is

\[
\begin{aligned}
 u_t&=v-f(u)+d u_{xx},\\
 v_t&=\epsilon(a-u)+v_{xx},
 \qquad f(u)=\frac13u^3-u,
\end{aligned}
\tag{1}
\]

where \(d>0\) and \(\epsilon>0\).  Its homogeneous state is
\((u,v)=(a,f(a))\).  We write

\[
 \delta=\sqrt d,\qquad r=r_2=\sqrt\delta=d^{1/4},
 \qquad s=\sqrt\epsilon,\qquad \kappa=\epsilon^{1/4}.
\tag{2}
\]

Fix once and for all

\[
 0<\epsilon_-<\epsilon_+<\infty,
 \qquad A>0.
\tag{3}
\]

The blown-up parameter box and its physical image are

\[
\begin{aligned}
 \mathcal W_{r_*}
 &=\{(r,a_2,\epsilon):0\le r\le r_*,\ |a_2|\le A,
       \ \epsilon_-\le\epsilon\le\epsilon_+\},\\
 d&=r^4,\qquad \delta=r^2,\qquad
 a=1+\sqrt\epsilon\,r^3a_2.
\end{aligned}
\tag{4}
\]

The box \(\mathcal W_{r_*}\) is a repository-defined derived parameter
domain, not a wedge theorem quoted from Vo--Doelman--Kaper.  Its size is
decreased by the compact central continuation proof.

Its positive part \(r>0\) is a nonempty cusp wedge in the original
parameters.  All parameter differentiability at the singular face means
differentiability in \((r,a_2,\epsilon)\), not in the degenerate coordinates
\((d,a)\).

## 2. Physical and fast spatial systems

Put

\[
 p=\delta u_x,\qquad q=v_x,qquad y=\frac{x}{\delta}.
\tag{5}
\]

The stationary equation is equivalent to the physical-\(x\) system

\[
 \delta u_x=p,\qquad \delta p_x=f(u)-v,
 \qquad v_x=q,\qquad q_x=\epsilon(u-a),
\tag{6}
\]

and to the fast-\(y\) system

\[
 u_y=p,\qquad p_y=f(u)-v,
 \qquad v_y=\delta q,\qquad q_y=\epsilon\delta(u-a).
\tag{7}
\]

Let

\[
 F(u)=\frac1{12}u^4-\frac12u^2,
 \qquad
 \mathcal G=\frac12(\epsilon p^2-q^2)
 -\epsilon\bigl(F(u)+(a-u)v\bigr).
\tag{8}
\]

Direct differentiation along (7) gives \(d\mathcal G/dy=0\).  The
state-space primitive

\[
 \lambda_\delta=\epsilon p\,du-\delta^{-1}q\,dv,
 \qquad \omega_\delta=d\lambda_\delta
\tag{9}
\]

has the two clock-dependent Hamiltonians

\[
 \iota_{X_y}\omega_\delta=d(-\mathcal G),
 \qquad
 \iota_{X_x}\omega_\delta=d(-\mathcal G/\delta),
 \qquad X_x=\delta^{-1}X_y.
\tag{10}
\]

Thus changing the clock rescales the Hamiltonian but not the action integral
\(\int\lambda_\delta\).  The reverser

\[
 \mathcal R(u,p,v,q)=(u,-p,v,-q)
\tag{11}
\]

satisfies
\(D\mathcal R X=-X\circ\mathcal R\) and
\(\mathcal R^*\lambda_\delta=-\lambda_\delta\).

For reference, the clocks used in the model analysis are related by

| clock | exact relation | scope |
|---|---|---|
| physical \(x\) | base spatial variable | full stationary PDE |
| fast \(y\) | \(y=x/\delta\) | full fast--slow system |
| reduced \(x_d\) | \(dx=f'(u)\,dx_d\) | only on the critical manifold; orientation reverses where \(f'(u)<0\) |
| central \(y_2\) | \(y_2=ry=x/r\) | physical equality for \(r>0\); desingularized extension at \(r=0\) |
| universal \(\xi\) | \(\xi=\kappa y_2=\epsilon^{1/4}x/r\) | physical equality for \(r>0\); exact core-clock extension at \(r=0\) |
| entry/exit \(y_1\) | \(dy_1=r_1\,dy\) | chart \(K_1\) |
| energy-reduced \(\eta_2\) | \(dy_2=u_2\,d\eta_2\) | only after restricting to the singular zero-energy problem; orientation reverses with \(u_2\) |

The last two time changes are dynamic.  Neither may be substituted into a
physical length or action formula without its displayed clock factor.

## 3. Translation and quasi-homogeneous blow-up

The published-source crosswalk for this section is: translation (6.1),
p. 2642; blow-up and the \(K_1,K_2\) charts (6.4)--(6.6), p. 2643;
\(K_2\) field and conserved quantity (6.7)--(6.8), p. 2644; \(K_1\)
field (6.16), p. 2646; and chart transitions (6.28)--(6.29), p. 2651.
All clock, sign, equilibrium-shift, and flagship-conjugacy statements beyond
those displayed source formulas are derived here.

Translate the RFSN-II point by

\[
 (u,p,v,q,a,\delta)
 =(1+\widetilde u,\widetilde p,-\tfrac23+\widetilde v,
   \widetilde q,1+\widetilde a,\widetilde\delta).
\tag{12}
\]

The published weights are

\[
\begin{aligned}
 \widetilde u&=\sqrt\epsilon\,\rho^2\bar u,&
 \widetilde p&=\epsilon\rho^3\bar p,&
 \widetilde v&=\epsilon\rho^4\bar v,\\
 \widetilde q&=\epsilon^{3/2}\rho^3\bar q,&
 \widetilde a&=\sqrt\epsilon\,\rho^3\bar a,&
 \widetilde\delta&=\rho^2\bar\delta.
\end{aligned}
\tag{13}
\]

In the central chart \(K_2=\{\bar\delta=1\}\),

\[
\begin{aligned}
 \widetilde u&=\sqrt\epsilon\,r^2u_2,&
 \widetilde p&=\epsilon r^3p_2,&
 \widetilde v&=\epsilon r^4v_2,\\
 \widetilde q&=\epsilon^{3/2}r^3q_2,&
 \widetilde a&=\sqrt\epsilon\,r^3a_2,&
 \widetilde\delta&=r^2.
\end{aligned}
\tag{14}
\]

With \(y_2=ry\), the exact central system and its conserved quantity are

\[
\begin{aligned}
 u_2'&=\sqrt\epsilon\,p_2,\\
 p_2'&=u_2^2-v_2+\frac{\sqrt\epsilon}{3}r^2u_2^3,\\
 v_2'&=\sqrt\epsilon\,q_2,\\
 q_2'&=u_2-ra_2,
\end{aligned}
\tag{15}
\]

\[
 H_2=\frac{\sqrt\epsilon}{2}(p_2^2-q_2^2)
 +(u_2-ra_2)v_2-\frac13u_2^3
 -\frac{\sqrt\epsilon}{12}r^2u_2^4,
\tag{16}
\]

where a prime denotes \(d/dy_2\).  The translated conserved quantity obeys

\[
 \widetilde{\mathcal G}=\epsilon^{5/2}r^6H_2.
\tag{17}
\]

Equations (14)--(17), rather than the prose immediately following the
published central scaling, fix the parameter relation

\[
 \widetilde a=\sqrt\epsilon\,\delta^{3/2}a_2.
\tag{18}
\]

That prose prints both a different power of \(\epsilon\) and \(q_2\) in
place of \(a_2\); it is not used here.

In the entry/exit chart \(K_1=\{\bar u=1\}\), the coordinates are

\[
\begin{aligned}
 \widetilde u&=\sqrt\epsilon\,r_1^2,&
 \widetilde p&=\epsilon r_1^3p_1,&
 \widetilde v&=\epsilon r_1^4v_1,\\
 \widetilde q&=\epsilon^{3/2}r_1^3q_1,&
 \widetilde a&=\sqrt\epsilon\,r_1^3a_1,&
 \widetilde\delta&=r_1^2\delta_1.
\end{aligned}
\tag{19}
\]

With \(dy_1=r_1dy\), direct substitution gives

\[
\begin{aligned}
 \dot r_1&=\tfrac12\sqrt\epsilon\,p_1r_1,&
 \dot\delta_1&=-\sqrt\epsilon\,p_1\delta_1,\\
 \dot p_1&=1-v_1-\tfrac32\sqrt\epsilon\,p_1^2
              +\tfrac13\sqrt\epsilon\,r_1^2,&
 \dot v_1&=\sqrt\epsilon(-2p_1v_1+\delta_1q_1),\\
 \dot q_1&=-\tfrac32\sqrt\epsilon\,p_1q_1
              +\delta_1(1-r_1a_1),&
 \dot a_1&=-\tfrac32\sqrt\epsilon\,p_1a_1,
\end{aligned}
\tag{20}
\]

where a dot denotes \(d/dy_1\).  On the positive overlap \(u_2>0\),

\[
\begin{aligned}
 r_1&=r\sqrt{u_2},& \delta_1&=u_2^{-1},\\
 p_1&=u_2^{-3/2}p_2,& v_1&=u_2^{-2}v_2,\\
 q_1&=u_2^{-3/2}q_2,& a_1&=u_2^{-3/2}a_2,
\end{aligned}
\tag{21}
\]

and the clocks satisfy

\[
 dy_2=\frac r{r_1}dy_1=\sqrt{\delta_1}\,dy_1
      =u_2^{-1/2}dy_1.
\tag{22}
\]

## 4. Fixed-equilibrium universal coordinates

For \(r>0\), introduce the exact physical change of variables

\[
\begin{aligned}
 u&=a-\sqrt\epsilon\,r^2U,&
 p&=-\epsilon^{3/4}r^3P,\\
 v&=f(a)-\epsilon r^4V,&
 q&=-\epsilon^{5/4}r^3Q,\\
 \xi&=\epsilon^{1/4}\frac{x}{r}.
\end{aligned}
\tag{23}
\]

Equivalently, in \(K_2\),

\[
\begin{aligned}
 U&=ra_2-u_2,& P&=-\epsilon^{1/4}p_2,\\
 V&=r^2a_2^2+\frac{\sqrt\epsilon}{3}r^5a_2^3-v_2,&
 Q&=-\epsilon^{1/4}q_2.
\end{aligned}
\tag{24}
\]

This affine conjugacy places the homogeneous equilibrium at the fixed origin.
Set

\[
 c(r,a_2,\epsilon)=2ra_2+\sqrt\epsilon\,r^4a_2^2.
\tag{25}
\]

The full positive-parameter central vector field is exactly

\[
\begin{aligned}
 U'&=P,\\
 P'&=cU-V-(1+\sqrt\epsilon\,r^3a_2)U^2
       +\frac{\sqrt\epsilon}{3}r^2U^3,\\
 V'&=Q,\\
 Q'&=U,
\end{aligned}
\tag{26}
\]

where now a prime denotes \(d/d\xi\).  It is exact Hamiltonian for the
parameter-independent primitive and shifted Hamiltonian

\[
 \lambda=P\,dU-Q\,dV,
 \qquad \omega=d\lambda,
\tag{27}
\]

\[
\begin{aligned}
 \widehat H={}&\frac12(Q^2-P^2)-UV+\frac c2U^2
 -\frac{1+\sqrt\epsilon\,r^3a_2}{3}U^3
 +\frac{\sqrt\epsilon}{12}r^2U^4,\\
 &\hspace{35mm}\iota_{F_{r,a_2,\epsilon}}\omega=d\widehat H.
\end{aligned}
\tag{28}
\]

The central equilibrium before (24) has

\[
 H_2(O)=-\frac13r^3a_2^3
         -\frac{\sqrt\epsilon}{12}r^6a_2^4,
 \qquad \widehat H=-(H_2-H_2(O)).
\tag{29}
\]

Thus \(H_2=0\) is not the equilibrium energy level when \(a_2\ne0\).
The energy subtraction in (29) is mandatory for any homoclinic statement.
The reverser remains

\[
 \mathcal R(U,P,V,Q)=(U,-P,V,-Q),
 \qquad \mathcal R^*\lambda=-\lambda.
\tag{30}
\]

On each fixed-parameter state fiber, the primitive and energy scale back to
the physical variables as

\[
 \lambda_\delta=\epsilon^{9/4}r^5\lambda,
 \qquad
 -\mathcal G+\mathcal G(O)=\epsilon^{5/2}r^6\widehat H,
\tag{31}
\]

and, for the physical \(x\)-clock,

\[
 \frac{-\mathcal G+\mathcal G(O)}{\delta}
 =\epsilon^{5/2}r^4\widehat H,
 \qquad dx=r\epsilon^{-1/4}d\xi.
\tag{32}
\]

These identities freeze both the physical action normalization and the
physical spatial-length normalization for later finite-part calculations.

## 5. Core identity and uniform saddle-focus wedge

At \(r=0\), (26)--(28) reduce, independently of \(a_2\) and \(\epsilon\), to

\[
 U'=P,\qquad P'=-U^2-V,\qquad V'=Q,\qquad Q'=U,
\tag{33}
\]

\[
 H_0=\frac12(Q^2-P^2)-\frac13U^3-UV,
 \qquad \lambda_0=P\,dU-Q\,dV.
\tag{34}
\]

This is exactly the flagship RFSN-II core, with the same coordinate order,
clock, primitive, Hamiltonian sign, and reverser.

The characteristic polynomial at the origin of (26) is

\[
 \chi(\mu)=\mu^4-c\mu^2+1.
\tag{35}
\]

Choose \(r_*>0\) so that, throughout \(\mathcal W_{r_*}\),

\[
 |c(r,a_2,\epsilon)|\le2-\gamma
\tag{36}
\]

for some \(\gamma>0\), and also \(a>0\).  Then the spectrum is the uniform
saddle-focus quartet

\[
 \{\alpha+i\beta,\alpha-i\beta,-\alpha+i\beta,-\alpha-i\beta\},
 \quad
 \alpha=\tfrac12\sqrt{2+c},\quad
 \beta=\tfrac12\sqrt{2-c}.
\tag{37}
\]

On every fixed compact state set, (26) converges to (33) in every state
\(C^k\) norm uniformly in \(|a_2|\le A\) and
\(\epsilon\in[\epsilon_-,\epsilon_+]\), with size
\(O(rA+\sqrt{\epsilon_+}r^2)\).  The family is smooth, in particular
\(C^2\), in the blown-up parameters on the closed box (4).

## 6. Dependency boundary

This note establishes the complete model bridge required by V1 and the model
part of V2.  The analytic obligations in the first two bullets below are
discharged by [CENTRAL_CONTINUATION.md](CENTRAL_CONTINUATION.md), and the
positive pole entry and finite part are discharged by
[POSITIVE_POLE_FINITE_PART.md](POSITIVE_POLE_FINITE_PART.md).  This algebraic
note itself does not establish:

- the selected positive-parameter homoclinic or its weighted tails;
- continuation of the source cell or any compact first-event arrangement;
- entry into a positive-parameter pole or outer algebraic end;
- either action finite part;
- an exhaustive return--first-exit relation or coding; or
- temporal stability of any stationary PDE pattern.

Those are separate obligations discharged, or still to be discharged, in
V2--V7 as recorded in [CLAIM_REGISTER.md](../CLAIM_REGISTER.md).
