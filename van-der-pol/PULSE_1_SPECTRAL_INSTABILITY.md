# `pulse_1`: whole-line spectral instability

## Status and conclusion

This note treats the second target in Issue #11.  It proves a whole-line
moment criterion and applies it to the primary symmetric homoclinic at

\[
 (r,a_2,\epsilon)=(0.08,0,1),\qquad a=1,\qquad d=r^4.
\]

The true profile is not inferred from the truncated `pulse_1` array.  It is
the selected first-hit homoclinic already enclosed by the P2c validation.  A
target-specific outward-rounded calculation on that same Krawczyk root proves
the strict moment inequality below.  Consequently the temporal linearization
has a real, positive, whole-line \(L^2\) eigenvalue

\[
 \boxed{\lambda_*\in(0.01,2)}.
\]

This is a local mathematical `PASS`.  It remains non-claim-bearing under the
repository policy until independent-machine replay.  This note proves the
linear spectral input; the separate
[semilinear bridge](NONLINEAR_ORBITAL_INSTABILITY.md) turns that input into
whole-line nonlinear orbital instability.  Neither result proves selection,
a Turing connection, or canard identification.

## 1. Whole-line operator pencil

For

\[
 u_t=v-f(u)+d u_{xx},\qquad
 v_t=\epsilon(a-u)+v_{xx},\qquad
 f(u)=\frac{u^3}{3}-u,
 \tag{1}
\]

let \((U,V)\) be a nonconstant stationary homoclinic to
\((a,f(a))\), with exponential decay.  On
\(L^2(\mathbb R;\mathbb C)^2\), with domain \(H^2(\mathbb R)^2\), its
temporal linearization is

\[
 \mathcal L\binom{\phi}{\psi}
 =\binom{d\phi''-f'(U)\phi+\psi}
             {-\epsilon\phi+\psi''}.
 \tag{2}
\]

Put \(A=-\partial_x^2\).  For real \(\lambda>0\), define the self-adjoint
operator

\[
 K_\lambda=dA+f'(U)+\lambda+\epsilon(\lambda+A)^{-1}.
 \tag{3}
\]

Schur elimination of the second component gives

\[
 \lambda\in\sigma_{\rm p}(\mathcal L)
 \quad\Longleftrightarrow\quad
 0\in\sigma_{\rm p}(K_\lambda),
 \qquad
 \psi=-\epsilon(\lambda+A)^{-1}\phi.
 \tag{4}
\]

The periodic argument cannot simply be copied here: \(A^{-1}\) is not a
bounded whole-line operator, and a zero of the bottom of the spectrum could
otherwise be only an essential-spectrum edge.  The next two steps resolve
exactly those issues.

## 2. Whole-line moment criterion

**Proposition (localized van der Pol moment criterion).**  Let
\(d,\epsilon>0\).  Suppose the homoclinic above has exponential decay and,
for some
\(0<\lambda_0<\Lambda\),

\[
 M_{\lambda_0}(U):=
 \int_{\mathbb R}
 \left[\lambda_0(U-a)^2+a(U-a)^3+\frac23(U-a)^4\right]dx<0.
 \tag{5}
\]

Assume also

\[
 \inf_{\lambda\in[\lambda_0,\Lambda]}m_\infty(\lambda)>0,
 \qquad
 \Lambda+\inf_x f'(U(x))>0,
 \tag{6}
\]

where

\[
 m_\infty(\lambda)=f'(a)+
 \min_{t\ge0}\left(dt+\lambda+\frac{\epsilon}{\lambda+t}\right).
 \tag{7}
\]

Then \(\mathcal L\) has a real positive isolated \(L^2\) eigenvalue
\(\lambda_*\in(\lambda_0,\Lambda)\).

**Proof.**  Write \(w=U-a\), \(g=V-f(a)\), and \(h=-g/\epsilon\).  The
second stationary equation gives

\[
 Ah=w.
 \tag{8}
\]

This identity replaces the invalid use of a bounded whole-line \(A^{-1}\).
By the spectral theorem for \(A\),

\[
 \langle w,(\lambda+A)^{-1}w\rangle
 =\langle Ah,(\lambda+A)^{-1}Ah\rangle
 \le \langle Ah,h\rangle=\langle w,h\rangle.
 \tag{9}
\]

The first stationary equation gives
\(g=f(a+w)-f(a)-dw''\).  Integration by parts and the exact cubic identities

\[
 \begin{aligned}
 f(a+w)-f(a)&=f'(a)w+aw^2+\tfrac13w^3,\\
 f'(a+w)&=f'(a)+2aw+w^2
 \end{aligned}
 \tag{10}
\]

then yield

\[
 d\|w'\|_2^2+\int_{\mathbb R}f'(U)w^2dx
 +\epsilon\langle w,h\rangle
 =a\int_{\mathbb R}w^3dx+\frac23\int_{\mathbb R}w^4dx.
 \tag{11}
\]

Combining (9)--(11) with the quadratic form of \(K_{\lambda_0}\) gives

\[
 k_{\lambda_0}[w]\le M_{\lambda_0}(U)<0.
 \tag{12}
\]

Thus \(\inf\sigma(K_{\lambda_0})<0\).  At the other endpoint,
\(K_\Lambda\ge(\Lambda+\inf f'(U))I>0\).  Moreover

\[
 \|K_\lambda-K_\nu\|
 \le |\lambda-\nu|
 \left(1+\frac{\epsilon}{\lambda\nu}\right),
 \tag{13}
\]

so \(\lambda\mapsto\inf\sigma(K_\lambda)\) is continuous on compact
positive intervals.

Since \(f'(U)-f'(a)\to0\), this multiplication operator is relatively
compact with respect to \(A\).  The constant-coefficient Fourier symbol
therefore gives

\[
 \sigma_{\rm ess}(K_\lambda)=[m_\infty(\lambda),\infty),
 \tag{14}
\]

with

\[
 m_\infty(\lambda)=f'(a)+
 \begin{cases}
 2\sqrt{d\epsilon}+(1-d)\lambda,
   &0<\lambda\le\sqrt{\epsilon/d},\\
 \lambda+\epsilon/\lambda,
   &\lambda\ge\sqrt{\epsilon/d}.
 \end{cases}
 \tag{15}
\]

Continuity supplies a \(\lambda_*\in(\lambda_0,\Lambda)\) at which the
spectral bottom is zero.  Assumption (6) puts zero strictly below the
essential spectrum, so it is an isolated eigenvalue of \(K_{\lambda_*}\),
not merely a threshold.  Equation (4) reconstructs the corresponding
eigenfunction of \(\mathcal L\).  Finally,
if \(\mathcal L_\infty\) denotes (2) with \(U\equiv a\), then
\(\mathcal L-\mathcal L_\infty\) is a relatively compact decaying
multiplication perturbation, while (6) makes the far-field Schur complement
invertible at the positive real number \(\lambda_*\).  Thus
\(\lambda_*\) is outside the far-field, and hence the full, essential
spectrum.  Standard analytic Fredholm theory therefore makes this eigenvalue
isolated and of finite algebraic multiplicity.
\(\square\)

## 3. Explicit gap at the frozen target

At \(a=1\), \(d=0.08^4=0.00004096\), and \(\epsilon=1\),
\(f'(a)=0\) and \(\sqrt{\epsilon/d}=156.25\).  Hence, throughout
\(\lambda\in[0.01,2]\),

\[
 m_\infty(\lambda)
 =0.0128+0.99995904\lambda
 \ge0.0227995904>0.
 \tag{16}
\]

Also \(f'(U)=U^2-1\ge-1\), so \(K_2\ge I\).  The only
profile-specific numerical obligation is therefore (5) at
\(\lambda_0=0.01\).

For context, the far-field temporal essential spectrum itself is

\[
 \nu_\pm(t)=-\frac{(d+1)t}{2}
 \pm\frac12\sqrt{(d-1)^2t^2-4\epsilon},\qquad t\ge0.
 \tag{17}
\]

It touches the imaginary axis at \(\nu_\pm(0)=\pm i\).  Thus the positive
eigenvalue proved here is isolated, but there is no spectral gap for the full
temporal semigroup.  Such a gap is not needed by the separate nonlinear
orbital-instability bridge.

## 4. The true `pulse_1` and its strict moment

The frozen seed is
`numerics/results/vdp_v1_v7/v7_multipulses.npz::pulse_1_*`, with SHA-256
`28303dc49bdf1fa69b828fd6f6ccb955f4418adbfe0c789985d1332a58bac340`.
Its floating truncation gives

\[
 M_{0.01}\approx-8.82736\times10^{-7},\qquad
 \lambda_{\rm window}\approx0.02139762,
 \tag{18}
\]

but neither number is used as proof.

P2c already proves a selected symmetric first-hit homoclinic over the full
positive parameter box, including the target point.  It also gives the
weighted outer-half estimate, which at the target may be weakened to

\[
 |\Gamma(\xi)|\le1.082e^{-|\xi|/5}
 \quad\text{outside the source-to-symmetry compact segment},
 \qquad T_h>9.6.
 \tag{19}
\]

In central coordinates,

\[
 U_{\rm physical}-1=-r^2U_c,qquad dx=r\,d\xi,
 \tag{20}
\]

and symmetry gives

\[
 M_{0.01}=2r^5 Z_+,qquad
 Z_+=\int_0^\infty
 \left[0.01U_c^2-r^2U_c^3+\frac23r^4U_c^4\right]d\xi.
 \tag{21}
\]

The target validator reuses the P2c multiple-shooting implementation and
encloses the same fixed-parameter root.  On its source-to-symmetry segment it
obtains

\[
 Z_{\rm compact}\in
 [-0.134778800,-0.134611534].
 \tag{22}
\]

Using (19) term by term gives the outward-rounded half-tail bound

\[
 |Z_{\rm tail}|<0.000671676.
 \tag{23}
\]

Consequently

\[
 Z_+\in[-0.135450475,-0.133939858],
 \qquad
 M_{0.01}\in
 [-8.876883,-8.777882]\times10^{-7}<0.
 \tag{24}
\]

The validator also returns strict Krawczyk inclusion, transverse shooting
determinant, source-to-symmetry time in
\([9.652553,9.652727]\), and symmetry-centre
\(U_c\in[4.925413,4.925721]\).  The P2c branch uniqueness in its declared
lifted tube identifies this root with the selected primary homoclinic and the
saved `pulse_1` representative.

Equations (16), (24), and the proposition prove
\(\lambda_*\in(0.01,2)\).  No Evans contour or whole-line spectral
discretization is needed.

## Reproduction and trust boundary

The frozen contract is
[`numerics/config/vdp_pulse_1_spectral_v1.json`](../numerics/config/vdp_pulse_1_spectral_v1.json),
and the target validator is documented in
[`validation/pulse_1`](../validation/pulse_1/README.md).  The local run uses
outward-rounded CAPD/FILIB arithmetic and imports the hash-bound P2c profile
and tail records.  Independent replay remains the sole evidence-policy gate
before this local result can be promoted to a claim-bearing
computer-assisted statement.
