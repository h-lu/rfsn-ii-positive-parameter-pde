# Exact Kato radial sections on the nonlinear zero-energy fiber

**Proof contract:** `rfsn-vdp-p2d-explicit-exact-radial-sections/1`

**Local conclusion:** this note, together with the authenticated exact-chart
audit, the proved analytic normal form, and the locally passed zero-energy
fiber, discharges `V2.CHART.EXACT_SECTIONS`.  It does not prove the
weighted-log time/phase estimates, physical event slides, chart overlaps, or
the parent `V2.EXACT_CHART`.

## 1. Inputs and frozen radii

Use the positive-Kato normal-form coordinates
\((x,y)\in\mathbb R^2\times\mathbb R^2\), with

\[
 I_1=x\mathbin\cdot y,
 \qquad
 I_2^{\rm K}=x_2y_1-x_1y_2.
\tag{1}
\]

The contract `rfsn-vdp-p2d-explicit-global-moser-majorant/1` supplies one
parameter-\(C^2\), reversible, exact symplectic chart
\(\Phi_\mu^{\rm K}\) on \(S^{-1}\mathcal D_{\rm src}\), where

\[
 \mathcal D_{\rm src}=\Delta_{\rho_{\rm src}},
 \qquad \rho_{\rm src}=\frac3{2^{25}},
\tag{2}
\]

and one fixed primitive \(f_\mu\) satisfying

\[
 (\Phi_\mu^{\rm K})^*\lambda=\lambda_0+df_\mu,
 \qquad
 \lambda_0=\frac12(y\mathbin\cdot dx-x\mathbin\cdot dy).
\tag{3}
\]

The contract `rfsn-vdp-p2d-explicit-zero-energy-fiber/1` supplies

\[
 h_\mu(q_\mu(\nu),\nu)=0,
 \qquad
 \partial_{I_1}h_\mu(q_\mu(\nu),\nu)>\frac23
\tag{4}
\]

for real \(|\nu|\le\nu_*:=25/2^{54}\), with the conservative bound

\[
 |q_\mu(\nu)|\le Q_0
 :=\frac{36}{35}\frac{25}{2^{53}}
   +\frac5{24211351596743786496}.
\tag{5}
\]

Freeze the section radius

\[
 \rho:=\frac5{2^{26}}.
\tag{6}
\]

No radius or action interval is selected after inspecting a section run.

## 2. Strict inclusion in the exact chart

The exact rational comparisons are

\[
 \frac{\rho}{\rho_{\rm src}}=\frac56<1,
 \qquad
 \frac{Q_0+\nu_*}{\rho^2}=\frac{587}{768}<1,
 \qquad
 \frac{Q_0+\nu_*}{\rho\rho_{\rm src}}
 =\frac{2935}{4608}<1.
\tag{7}
\]

Thus both a fixed real radial factor of Euclidean length \(\rho\) and a
complementary factor bounded by \((Q_0+\nu_*)/\rho\) are strictly smaller
than the source radius (2).  Under the fixed unitary real-to-complex map
\(S\), each corresponding \(z_j\) or \(w_j\) has modulus equal to the
appropriate real two-vector norm divided by \(\sqrt2\).  Hence these stronger
bounds place the sections strictly in \(S^{-1}\mathcal D_{\rm src}\).  The
middle inequality will also make the nonzero passage time positive.

Put

\[
 J=\begin{pmatrix}0&-1\\1&0\end{pmatrix},
 \qquad e_\phi=(\cos\phi,\sin\phi).
\]

For \(|\nu|\le\nu_*\), define the auxiliary normal-form sections

\[
 \begin{aligned}
 s^{\rm in}_\mu(\phi,\nu)
  &=\left(\rho e_\phi,
      \rho^{-1}\{q_\mu(\nu)e_\phi-\nu Je_\phi\}\right),\\
 s^{\rm out}_\mu(\psi,\nu)
  &=\left(\rho^{-1}\{q_\mu(\nu)e_\psi+\nu Je_\psi\},
      \rho e_\psi\right).
 \end{aligned}
\tag{8}
\]

Equation (7) proves, without a floating-point decision, that both images are
strictly contained in \(S^{-1}\mathcal D_{\rm src}\).  Hence the physical sections

\[
 \iota^{\rm in/out}_\mu
 :=\Phi_\mu^{\rm K}\circ s^{\rm in/out}_\mu
\tag{9}
\]

are defined on the complete parameter bridge and the same two-sided action
interval.  They are parameter-\(C^2\) embeddings: \(q_\mu\) and
\(\Phi_\mu^{\rm K}\) are parameter-\(C^2\), the fixed radial factor recovers
the phase, and (10) below recovers \(\nu\).

## 3. Actions, section forms, and fixed gauges

Direct substitution in (1) gives, on both sections,

\[
 I_1=q_\mu(\nu),\qquad I_2^{\rm K}=\nu.
\tag{10}
\]

The arbitrary-\(q\) identities in the authenticated 59-check exact-chart
audit give

\[
 (s^{\rm in}_\mu)^*\omega_0
 =(s^{\rm out}_\mu)^*\omega_0
 =d\phi\wedge d\nu
\tag{11}
\]

(with \(\psi\) in place of \(\phi\) on the outgoing section), and

\[
 \begin{aligned}
 (s^{\rm in}_\mu)^*\lambda_0
   &=-\nu\,d\phi-\frac12\,dq_\mu(\nu),\\
 (s^{\rm out}_\mu)^*\lambda_0
   &=-\nu\,d\psi+\frac12\,dq_\mu(\nu).
 \end{aligned}
\tag{12}
\]

Combining (3), (9), and (12) fixes, rather than merely postulates, the
physical primitive gauges

\[
 \begin{aligned}
 G^{\rm in}_\mu
  &=f_\mu\circ s^{\rm in}_\mu-\frac12q_\mu,\\
 G^{\rm out}_\mu
  &=f_\mu\circ s^{\rm out}_\mu+\frac12q_\mu,
 \end{aligned}
\tag{13}
\]

for which

\[
 (\iota^{\rm in}_\mu)^*\lambda
   =-\nu\,d\phi+dG^{\rm in}_\mu,
 \qquad
 (\iota^{\rm out}_\mu)^*\lambda
   =-\nu\,d\psi+dG^{\rm out}_\mu.
\tag{14}
\]

The gauges inherit parameter-\(C^2\) regularity from \(f_\mu\) and
\(q_\mu\).  Taking exterior derivatives in (14) recovers (11) in physical
coordinates exactly; no numerical symplectic-defect tolerance is used.

Let \(C_0=\operatorname{diag}(1,-1)\) and
\(\mathcal R_0(x,y)=(C_0y,C_0x)\).  Since
\(C_0e_\phi=e_{-\phi}\) and \(C_0Je_\phi=-Je_{-\phi}\), direct substitution
gives

\[
 \mathcal R_0s^{\rm in}_\mu(\phi,\nu)
 =s^{\rm out}_\mu(-\phi,\nu).
\tag{15}
\]

The chart intertwines \(\mathcal R_0\) with the physical reverser
\(\mathcal R\), so the same relation holds for \(\iota^{\rm in/out}\).
Moreover \(f_\mu\circ\mathcal R_0=-f_\mu\), and (13) therefore fixes the
gauge constants compatibly:

\[
 G^{\rm out}_\mu(-\phi,\nu)=-G^{\rm in}_\mu(\phi,\nu).
\tag{16}
\]

## 4. Exact preservation by the nonzero passage

At an arbitrary point of the normal-form chart, put

\[
 a=\partial_{I_1}h_\mu(I_1,I_2^{\rm K}),
 \qquad
 \omega=\partial_{I_2^{\rm K}}h_\mu(I_1,I_2^{\rm K}).
\]

Then the equations are

\[
 \dot x=-a x+\omega Jx,
 \qquad
 \dot y=a y+\omega Jy.
\tag{17}
\]

The actions Poisson commute, so explicitly

\[
 \{I_2^{\rm K},h_\mu(I_1,I_2^{\rm K})\}
 =\partial_{I_1}h_\mu\{I_2^{\rm K},I_1\}
  +\partial_{I_2^{\rm K}}h_\mu\{I_2^{\rm K},I_2^{\rm K}\}=0.
\tag{18}
\]

The same calculation gives \(\dot I_1=0\).  Thus both actions in (1) are
exact first integrals without first assuming that the coefficients in (17)
are constant.  On the zero-energy orbit, they consequently reduce to the
constants

\[
 a_\mu(\nu)=\partial_{I_1}h_\mu(q_\mu(\nu),\nu)>\frac23,
 \qquad
 \omega_\mu(\nu)=\partial_{I_2^{\rm K}}
 h_\mu(q_\mu(\nu),\nu).
\tag{19}
\]

For
\(0<|\nu|\le\nu_*\), the incoming expanding radius is

\[
 \frac{\sqrt{q_\mu(\nu)^2+\nu^2}}{\rho}
 \le\frac{Q_0+\nu_*}{\rho}<\rho
\tag{20}
\]

by (7).  Since \(a_\mu(\nu)>2/3\), that radius grows strictly and reaches
\(\rho\) exactly once in positive time.  At this first reach, invariance of
\((I_1,I_2^{\rm K})=(q_\mu(\nu),\nu)\) forces the state to have the outgoing
form (8) for a unique phase modulo \(2\pi\).  Consequently the local passage
preserves the same number

\[
 \nu_{\rm out}=I_2^{\rm K}=\nu_{\rm in}
\tag{21}
\]

exactly and does not relabel its sign.  The singular boundary \(\nu=0\)
records the stable and unstable axis circles; no finite passage time is
asserted there.

The complete finite flow segment stays in the exact chart.  Before the first
outgoing reach, (17)--(19) give

\[
 \|x(t)\|\le\rho,\qquad \|y(t)\|\le\rho.
\tag{22}
\]

The unitary map \(S\) therefore places every point of the segment strictly in
\(S^{-1}\mathcal D_{\rm src}\), with the conservative state-radius buffer
\(\rho_{\rm src}-\rho=2^{-26}\).

## 5. Claim boundary

Equations (7), (11), (14), and (21)--(22) establish a local mathematical `PASS`
for `V2.CHART.EXACT_SECTIONS`.  They do not provide the logarithmic time and
phase remainders, the all-order weighted-log generator, physical event-face
slides, a finite overlap atlas, or `V2.EXACT_CHART`.  Those remain separate
fail-closed obligations.
