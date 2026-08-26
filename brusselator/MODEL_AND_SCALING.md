# Brusselator model, spatial clocks, and central scaling

**Evidence status: Derived.**  Every assertion in this note is an exact
algebraic consequence of the displayed PDE or a direct linear calculation.
The note does not establish a positive-diffusion homoclinic orbit, positivity
of a profile, or any temporal-stability statement.

## 1. Frozen PDE convention

We use the convention of Jencks--Doelman--Kaper--Vo, equations (1.1) and
(1.2):

\[
\begin{aligned}
 u_t&=d u_{xx}-(B+1)u+A+u^2v,\\
 v_t&=v_{xx}+Bu-u^2v,
\end{aligned}
\qquad x\in\mathbb R,
\tag{1}
\]

where \(d>0\) is the activator diffusion coefficient and the inhibitor
diffusion coefficient has been normalized to one.  The homogeneous state is

\[
 (u,v)=\left(A,\frac BA\right).
\tag{2}
\]

Thus \(d\), rather than \(d^2\), is the coefficient of \(u_{xx}\).  This
choice fixes every fractional power of the small parameter below.

Put

\[
 \varepsilon=\sqrt d,\qquad
 p=\varepsilon u_x,\qquad q=v_x,\qquad y=\frac{x}{\varepsilon}.
\tag{3}
\]

The stationary equation for (1) is equivalent, for every
\(\varepsilon>0\), to the physical-\(x\) system

\[
\begin{aligned}
 \varepsilon u_x&=p,&
 \varepsilon p_x&=-A+(B+1)u-u^2v,\\
 v_x&=q,&
 q_x&=-Bu+u^2v,
\end{aligned}
\tag{4}
\]

and to the fast-\(y\) system

\[
\begin{aligned}
 u_y&=p,&
 p_y&=-A+(B+1)u-u^2v,\\
 v_y&=\varepsilon q,&
 q_y&=\varepsilon(-Bu+u^2v).
\end{aligned}
\tag{5}
\]

Equations (3)--(5) agree with equations (2.5)--(2.6) of the published
source.  In particular, \(q=v_x\), not \(v_y\).

## 2. Reversibility and volume preservation

Both spatial formulations are reversed by

\[
 \mathcal R(u,p,v,q)=(u,-p,v,-q),\qquad
 \operatorname{Fix}\mathcal R=\{p=q=0\}.
\tag{6}
\]

Indeed, if \(F_\varepsilon\) denotes the right-hand side of (5), then

\[
 D\mathcal R\,F_\varepsilon=-F_\varepsilon\circ\mathcal R.
\tag{7}
\]

The divergence of (5) in the ordered coordinates \((u,p,v,q)\) is zero:

\[
 \partial_u p+
 \partial_p[-A+(B+1)u-u^2v]+
 \partial_v(\varepsilon q)+
 \partial_q[\varepsilon(-Bu+u^2v)]=0.
\tag{8}
\]

The same calculation applies to (4).  Thus the spatial flow is reversible
and volume preserving.  No Hamiltonian or first integral for the
positive-parameter system is asserted.

## 3. Specialization to \(A=B=1\)

From now on fix \(A=B=1\).  The homogeneous state is \((u,v)=(1,1)\), and
(5) becomes

\[
\begin{aligned}
 u_y&=p,& p_y&=2u-1-u^2v,\\
 v_y&=\varepsilon q,& q_y&=\varepsilon(-u+u^2v).
\end{aligned}
\tag{9}
\]

Set

\[
 r=\sqrt\varepsilon=d^{1/4},\qquad
 \xi=ry=\frac{x}{r},
\tag{10}
\]

and introduce the weighted central variables

\[
\begin{aligned}
 u&=1+r^2U,& p&=r^3P,\\
 v&=1+r^4V,& q&=r^3Q.
\end{aligned}
\tag{11}
\]

This is precisely the \(A=B=1\), \(\mathcal B_2=0\) specialization of the
published \(K_2\) weights (5.4)--(5.5).  The independent variable \(\xi\)
is the published \(x_2=r_2y\); there is no additional constant rescaling of
time.

Direct expansion gives

\[
\begin{aligned}
 2u-1-u^2v
   &=-r^4(U^2+V)-2r^6UV-r^8U^2V,\\
 -u+u^2v
   &=r^2U+r^4(U^2+V)+2r^6UV+r^8U^2V.
\end{aligned}
\tag{12}
\]

Consequently the stationary problem is exactly

\[
\begin{aligned}
 U'&=P,\\
 P'&=-U^2-V-2r^2UV-r^4U^2V,\\
 V'&=Q,\\
 Q'&=U+r^2(U^2+V)+2r^4UV+r^6U^2V,
\end{aligned}
\tag{13}
\]

where a prime denotes \(d/d\xi\).  Formula (13), not merely its leading
terms, is the full positive-diffusion stationary spatial system in central
coordinates.

It is a polynomial family for \(r\) in a neighborhood of zero and is
reversed by

\[
 \mathcal R(U,P,V,Q)=(U,-P,V,-Q).
\tag{14}
\]

At \(r=0\), (13) reduces without a further conjugacy to the RFSN-II core

\[
 U'=P,\qquad P'=-U^2-V,\qquad V'=Q,\qquad Q'=U.
\tag{15}
\]

The limiting system (15) has

\[
 \lambda_0=P\,dU-Q\,dV,\qquad
 H_0=\frac12(Q^2-P^2)-\frac13U^3-UV,
\tag{16}
\]

with \(\iota_{F_0}d\lambda_0=dH_0\).  Equation (16) is used only for
identifying the imported core result.  It is not promoted to a
positive-\(r\) Hamiltonian claim.

The identity in (16) is checked directly from (15).  It is not copied from
equation (8.2) of the published Brusselator paper: the signs printed there
do not give a conserved quantity for its displayed equation (8.1).

## 4. Spatial spectrum

The origin is an equilibrium of (13) for every \(r\).  Its linearization
has characteristic polynomial

\[
 \chi_r(\mu)=\mu^4-r^2\mu^2+1.
\tag{17}
\]

For \(0\le r<\sqrt2\), the four eigenvalues form a saddle-focus quartet

\[
 \{\alpha(r)+i\beta(r),\ \alpha(r)-i\beta(r),\
   -\alpha(r)+i\beta(r),\ -\alpha(r)-i\beta(r)\},
\tag{18}
\]

where

\[
 \alpha(r)=\frac12\sqrt{2+r^2},\qquad
 \beta(r)=\frac12\sqrt{2-r^2}.
\tag{19}
\]

In particular, the stable and unstable dimensions are both two and the
spectral gap from the imaginary axis is uniform on every fixed
\(0\le r\le r_*<\sqrt2\).  At \(r=0\),
\(\alpha(0)=\beta(0)=2^{-1/2}\), as in the source core.

Because \(\xi=x/r\), the physical-\(x\) eigenvalues are those in (18)
divided by \(r\).  Their decay length is therefore

\[
 \frac{r}{\alpha(r)}=\Theta(r)=\Theta(d^{1/4}).
\tag{20}
\]

Equation (20) identifies the linear tail scale.  A nonlinear homoclinic
with uniform tails is still required before it becomes a width statement
for an actual PDE profile.

## 5. Inverse scaling and conditional size identities

If \(Z_r=(U_r,P_r,V_r,Q_r)\) is any solution of (13), then

\[
 u_d(x)=1+r^2U_r(x/r),\qquad
 v_d(x)=1+r^4V_r(x/r),\qquad d=r^4,
\tag{21}
\]

solves the stationary PDE (1) at \(A=B=1\).  This is an exact equivalence
for every \(r>0\).  Whenever the displayed norms are finite,

\[
\begin{aligned}
 \|u_d-1\|_\infty&=d^{1/2}\|U_r\|_\infty,\\
 \|v_d-1\|_\infty&=d\|V_r\|_\infty.
\end{aligned}
\tag{22}
\]

Thus the expected amplitude powers follow from a uniformly bounded,
nonzero limiting scaled orbit.  Existence, nontriviality, global bounds,
positive concentrations, and uniform exponential tails are supplied only
by the separate localized-profile argument.

## 6. Dependency boundary

This note establishes:

- the PDE and diffusion convention;
- both spatial clocks and both momentum conventions;
- the exact positive-\(r\) central vector field;
- reversibility, volume preservation, and the saddle-focus spectrum; and
- the exact inverse scaling.

It does not establish B1, B2, or B3 in the claim register.  It also does
not use Proposition 2.1 of the primary Brusselator paper: that proposition
does not state a neighborhood uniform as
\(\varepsilon=\sqrt d\to0\) along \(A=B=1\).
