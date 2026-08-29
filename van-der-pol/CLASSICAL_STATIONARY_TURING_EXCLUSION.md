# Exact exclusion of classical stationary Turing onset

Consider the temporal van der Pol reaction--diffusion system

\[
 u_t=v-f(u)+d u_{xx},\qquad
 v_t=\epsilon(a-u)+v_{xx},\qquad
 f(u)=\frac13u^3-u,
\]

with \(d>0\) and \(\epsilon>0\).  Its homogeneous equilibrium is
\((a,f(a))\).  This note records the elementary exact result needed to keep
the stationary spatial patterns in this repository separate from a classical
diffusion-driven Turing bifurcation.

## Proposition

Put \(\alpha=f'(a)=a^2-1\), \(q=k^2\), and linearize a Fourier mode
\(e^{\lambda t+ikx}\).  Then

\[
 L(k)=
 \begin{pmatrix}
  -\alpha-dq&1\\
  -\epsilon&-q
 \end{pmatrix},\qquad
 \operatorname{tr}L=-\alpha-(1+d)q,
 \quad
 \det L=dq^2+\alpha q+\epsilon.
\]

The following statements hold.

1. The homogeneous mode \(k=0\) is strictly spectrally stable if and only if
   \(\alpha>0\).  In that case every Fourier mode is strictly stable.
2. A stationary zero eigenvalue at some positive wavenumber exists if and
   only if
   \[
   \alpha\leq-2\sqrt{d\epsilon}<0.
   \]
   At equality the zero is double as a function of \(q\), with
   \(q_c=\sqrt{\epsilon/d}\); below equality there are two positive roots and
   a real unstable band between them.
3. Consequently, this system has no classical stationary Turing onset from a
   stable homogeneous equilibrium.

For the positive-cusp coordinates

\[
 d=r^4,\qquad a=1+\sqrt\epsilon\,r^3a_2,
\]

the whole frozen box

\[
 \frac1{25}\le r\le\frac2{25},\qquad
 -\frac14\le a_2\le\frac14,\qquad
 \frac45\le\epsilon\le\frac65
\]

lies strictly away from every positive-wavenumber stationary zero.  Indeed,

\[
 \begin{aligned}
 \alpha+2r^2\sqrt\epsilon
 &=\sqrt\epsilon\,r^2
   \left(2+2ra_2+\sqrt\epsilon\,r^4a_2^2\right),\\
 2+2ra_2+\sqrt\epsilon\,r^4a_2^2
 &\ge 2-\frac1{25}=\frac{49}{25}.
 \end{aligned}
\]

When \(2r^2\sqrt\epsilon<1\), the two stationary-neutral branches are

\[
 a_{2,\mathrm T}^{\pm}(r,\epsilon)
 =\frac{\pm\sqrt{1-2r^2\sqrt\epsilon}-1}
        {\sqrt\epsilon\,r^3},
 \qquad
 k_c=\frac{\epsilon^{1/4}}r.
\]

The branch near the positive fold is \(a_{2,\mathrm T}^{+}\).  On the frozen
box, \(a_{2,\mathrm T}^{+}<-1/r\le-25/2\), and the minus branch is still more
negative, so neither meets \([-1/4,1/4]\).  Both lie on a homogeneously
unstable background.

## Proof

At \(q=0\), the characteristic polynomial is
\(\lambda^2+\alpha\lambda+\epsilon\).  Since \(\epsilon>0\), the
Routh--Hurwitz criterion gives strict stability exactly when \(\alpha>0\).
For such \(\alpha\), both \(\operatorname{tr}L(k)<0\) and
\(\det L(k)>0\) for every \(q\ge0\), proving stability of all Fourier modes.

A stationary zero is equivalent to
\(p(q)=dq^2+\alpha q+\epsilon=0\).  Because \(d,\epsilon>0\), this convex
quadratic has a zero with \(q>0\) exactly when its minimizer
\(-\alpha/(2d)\) is positive and its minimum
\(\epsilon-\alpha^2/(4d)\) is nonpositive.  These two conditions combine to
\(\alpha\le-2\sqrt{d\epsilon}\).  The double-root and two-root statements
follow from the discriminant.  The frozen-box factorization and bound above
then prove the stated corollary, while solving
\((1+\sqrt\epsilon r^3a_2)^2=1-2r^2\sqrt\epsilon\) gives the two branches.
The estimate for the positive branch follows from
\(\sqrt{1-y}<1-y/2\) for \(0<y<1\).

At \(\alpha=0\), the zero mode is the Hopf pair
\(\lambda=\pm i\sqrt\epsilon\), while every \(q>0\) has negative trace and
positive determinant.  At \(\alpha<0\), the homogeneous mode is already
unstable, whether or not a finite-wavenumber stationary band is present.

## Terminology and claim boundary

Vo--Doelman--Kaper call the spatial reversible \(1{:}1\) curve at the same
algebraic threshold a singular Turing bifurcation.  The proposition above
uses the narrower classical temporal definition: diffusion destabilizes a
homogeneous equilibrium whose reaction kinetics are strictly stable.  The
two descriptions are compatible; on the spatial \(1{:}1\) curve here, the
temporal homogeneous mode is already unstable.

This proposition excludes only local classical **stationary** Turing onset in
the stated parameter set.  It does not exclude a branch born outside the box
and globally continued into it, a finite-wavenumber unstable band on an
already unstable background, a Hopf--Turing or nonlinear mechanism,
wavelength selection, or temporal selection of any nonconstant stationary
profile.  In particular, it neither proves nor disproves that the
high-winding stationary patterns are dynamically observed.
