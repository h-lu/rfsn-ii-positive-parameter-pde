# From a positive temporal eigenvalue to nonlinear orbital instability

## 1. Status and scope

This note supplies the nonlinear-semiflow bridge for the two temporal
eigenvalues proved in
[`A2_PERIODIC_SPECTRAL_INSTABILITY.md`](A2_PERIODIC_SPECTRAL_INSTABILITY.md)
and
[`PULSE_1_SPECTRAL_INSTABILITY.md`](PULSE_1_SPECTRAL_INSTABILITY.md).
It proves that a positive temporal eigenvalue makes a stationary profile
nonlinearly unstable, even after translations of the profile are factored
out.

The conclusion is deliberately local.  It says that arbitrarily small
perturbations can leave a fixed neighbourhood of the translation orbit.  It
does not identify the state reached after exit, the behaviour of generic
perturbations, a basin boundary, nonlinear saturation, or a dynamically
selected pattern.  In particular, it is not a Turing-selection or canard
theorem.

The analytic implication proved here is unconditional.  Its two
target-specific inputs retain their existing evidence status: the A2 and
`pulse_1` eigenvalue enclosures are local mathematical `PASS` results but are
non-claim-bearing until the independent-machine replay required by the
repository policy has been archived.

## 2. Equation, perturbation space, and translation orbit

Write the PDE as

\[
 q_t=Dq_{xx}+F(q),\qquad
 q=\binom uv,\qquad
 D=\begin{pmatrix}d&0\\0&1\end{pmatrix},
 \tag{1}
\]

where

\[
 F(u,v)=\binom{v-f(u)}{\epsilon(a-u)},\qquad
 f(u)=\frac{u^3}{3}-u,qquad d,\epsilon>0.
 \tag{2}
\]

Let \(Q=(U,V)\) be a nonconstant smooth stationary solution.  We use one of
the following phase spaces:

\[
 X_\Omega=H^1(\Omega;\mathbb R^2),\qquad
 \Omega=\mathbb T_L:=\mathbb R/L\mathbb Z
 \quad\hbox{or}\quad \Omega=\mathbb R.
 \tag{3}
\]

On the line we assume that \(Q-Q_\infty\) is exponentially localized for a
constant far-field state \(Q_\infty\).  The PDE is then considered on the
affine space \(Q+X_{\mathbb R}\).  If
\((\tau_s q)(x)=q(x+s)\), the translation orbit is

\[
 \mathcal O(Q)=\{\tau_sQ:s\in G_\Omega\},\qquad
 G_{\mathbb T_L}=\mathbb R/L\mathbb Z,
 \quad G_{\mathbb R}=\mathbb R.
 \tag{4}
\]

In the line case

\[
 \tau_sQ-Q
 =\tau_s(Q-Q_\infty)-(Q-Q_\infty)\in H^1(\mathbb R)^2,
 \tag{5}
\]

so (4) is meaningful in the affine phase space.

For a solution \(q(t)\), define

\[
 \operatorname{dist}_{X_\Omega}(q(t),\mathcal O(Q))
 :=\inf_{s\in G_\Omega}\|q(t)-\tau_sQ\|_{X_\Omega}.
 \tag{6}
\]

We call \(Q\) *orbitally Lyapunov unstable in \(X_\Omega\)* if there is an
\(\eta>0\) such that, for every \(\delta>0\), some initial value \(q_0\)
and finite time \(t_\delta>0\) satisfy

\[
 \|q_0-Q\|_{X_\Omega}<\delta,
 \qquad
 \operatorname{dist}_{X_\Omega}
       (q(t_\delta;q_0),\mathcal O(Q))\geq\eta,
 \tag{7}
\]

with the solution defined on \([0,t_\delta]\).  This finite-exit definition
does not require a separate global-existence result.

## 3. Corrected fixed-equilibrium-manifold instability lemma

The standard discrete linearized-instability argument needs a small but
important correction when the equilibrium belongs to a symmetry family.  A
time map fixes every point of the equilibrium manifold; it does not vanish
there.

**Lemma 1 (fixed-equilibrium-manifold map lemma).**
Let \(X\) be a real Banach space, let \(\mathcal V\subset X\) be an open
neighbourhood of \(0\), and let \(\mathcal E\subset\mathcal V\) be a
finite-dimensional \(C^2\) embedded manifold through \(0\).  Let
\(T:\mathcal V\to X\) be continuous and suppose that

\[
 T(e)=e\quad(e\in\mathcal E),
 \tag{8}
\]

and, for some \(M\in\mathcal L(X)\), \(C>0\), and \(\sigma>1\),

\[
 \|T(x)-Mx\|_X\leq C\|x\|_X^\sigma
 \quad\hbox{for all sufficiently small }x.
 \tag{9}
\]

Assume

\[
 r(M)>1,
 \qquad
 T_0\mathcal E\subset\ker(M-I),
 \tag{10}
\]

where \(r(M)\) is the spectral radius of the complexification of \(M\).
Then \(0\) is orbitally unstable with respect to \(\mathcal E\): there are
\(\eta,\rho>0\) such that, for every \(\delta>0\), there are
\(x_\delta\in X\) and \(N\in\mathbb N\) for which

\[
 \|x_\delta\|_X<\delta,
 \qquad T^n(x_\delta)\in B_\rho(0)\quad(0\leq n<N),
 \qquad
 \operatorname{dist}_X(T^N(x_\delta),\mathcal E)\geq\eta.
 \tag{11}
\]

**Proof.**  Put \(Y=T_0\mathcal E\) and choose a closed complement \(Z\).
A local \(C^2\) chart straightens \(\mathcal E\) to \(\{z=0\}\) in
\(Y\oplus Z\), and distance to \(\mathcal E\) is locally equivalent to
\(\|z\|\).  In these coordinates the remainder exponent may be replaced by
\(\widehat\sigma=\min\{\sigma,2\}>1\).  Conditions (8)--(10) give the
triangular derivative

\[
 M=\begin{pmatrix}I&B\\0&A\end{pmatrix},
 \qquad \sigma(M)=\{1\}\cup\sigma(A),
 \qquad r(A)=r(M)>1.
 \tag{12}
\]

Thus every expanding spectral packet is transverse to the fixed manifold.
Apply the discrete linearized-instability argument of the reference below to
the transverse block \(A\).  Its approximate-spectral-packet construction and
discrete variation-of-constants estimate give constants \(c,C_0>0\), a fixed
sufficiently small \(\alpha>0\), and, for arbitrarily large \(N\), initial
points \(x_N\) such that

\[
 \|x_N\|\le C_0\alpha r(A)^{-N},\qquad
 \max_{0\le n<N}\|T^nx_N\|\le C_0\alpha,qquad
 \|\pi_ZT^Nx_N\|\ge c\alpha .
 \tag{13}
\]

The only nonlinear estimate used to close that iteration is the geometric
sum obtained from \(O(\|x\|^{\widehat\sigma})\); choosing
\(\gamma>0\) with
\(r(A)+\gamma<r(A)^{\widehat\sigma}\) makes the sum uniform in \(N\).
As \(N\to\infty\), the first bound in (13) is smaller than any prescribed
\(\delta\), while the last bound and local equivalence of \(\|z\|\) with
distance to \(\mathcal E\) give a fixed exit radius.  This proves (11).
\(\square\)

Lemma 1 is the corrected form of the equilibrium-manifold extension of
Henry's discrete instability theorem.  The corresponding argument appears
in Section 5.3 of M. Meyries, J. D. M. Rademacher, and E. Siero,
*SIAM J. Appl. Dyn. Syst.* **13** (2014), 249--275,
[doi:10.1137/130925633](https://doi.org/10.1137/130925633).  Its proof gives
the estimates summarized in (13).  In the printed statement, the fixed-point
identity and the centred time map contain the same evident typographical slip
corrected in (8)--(9).

## 4. Semiflow bridge for the van der Pol PDE

Let \(p=q-Q=(p_1,p_2)\).  Direct subtraction of the stationary equations
gives

\[
 p_t=\mathcal L_Qp+\mathcal N_Q(p),
 \tag{20}
\]

where

\[
 \mathcal L_Q\binom{p_1}{p_2}
 =\binom{dp_1''-f'(U)p_1+p_2}
              {-\epsilon p_1+p_2''},
 \qquad
 \mathcal N_Q(p)
 =\binom{-Up_1^2-\frac13p_1^3}{0}.
 \tag{21}
\]

The following facts close the nonlinear bridge.

1. In one dimension \(H^1(\Omega)\) is a Banach algebra.  Since \(U\) and
   its first derivative are bounded,

   \[
   \|\mathcal N_Q(p)\|_{H^1}
   \leq C_Q\bigl(\|p\|_{H^1}^2+\|p\|_{H^1}^3\bigr).
   \tag{22}
   \]

   Thus \(\mathcal N_Q:X_\Omega\to X_\Omega\) is \(C^\infty\), with
   \(\mathcal N_Q(0)=D\mathcal N_Q(0)=0\).

2. On \(X_\Omega\), with domain \(H^3(\Omega)^2\), the diagonal operator
   \(D\partial_x^2\) generates an analytic semigroup.  The remaining
   coefficient matrix is bounded on \(H^1\), so the bounded-perturbation
   theorem shows that \(\mathcal L_Q\) also generates an analytic
   semigroup.

3. Standard semilinear theory therefore gives a local \(C^2\) semiflow.
   For any fixed sufficiently small \(T>0\), its perturbation time map
   \(\Phi_T\) satisfies

   \[
   \Phi_T(p)=e^{T\mathcal L_Q}p+R_T(p),
   \qquad
   \|R_T(p)\|_{H^1}\leq C_T\|p\|_{H^1}^2.
   \tag{23}
   \]

   Indeed, (23) follows directly from variation of constants, (22), and a
   uniform finite-time bound \(\sup_{0\leq t\leq T}\|p(t)\|_{H^1}\leq
   C\|p(0)\|_{H^1}\) for small data.

4. Translation invariance makes

   \[
   \mathcal E_Q=\{\tau_sQ-Q:s\hbox{ near }0\}
   \tag{24}
   \]

   a local \(C^2\) manifold of fixed points of \(\Phi_T\).  Differentiating
   the stationary equation yields

   \[
   Q'\in\ker\mathcal L_Q,
   \qquad e^{T\mathcal L_Q}Q'=Q'.
   \tag{25}
   \]

5. If \(\mathcal L_Q\phi=\lambda\phi\) in the \(L^2\) realization and
   \(\lambda>0\), elliptic bootstrapping in (21) gives
   \(\phi\in H^3(\Omega)^2\).  Real coefficients and real \(\lambda\) let
   us choose \(\phi\) real.  Hence

   \[
   e^{T\mathcal L_Q}\phi=e^{T\lambda}\phi,
   \qquad e^{T\lambda}>1.
   \tag{26}
   \]

Equations (23)--(26) verify every hypothesis of Lemma 1.

**Theorem 2 (positive eigenvalue implies nonlinear orbital instability).**
Let \(\Omega=\mathbb T_L\) or \(\mathbb R\), and let \(Q\) satisfy the
assumptions of Section 2.  If the \(L^2\) temporal linearization
\(\mathcal L_Q\), with domain \(H^2(\Omega)^2\), has a real eigenvalue
\(\lambda>0\), then \(Q\) is orbitally Lyapunov unstable in
\(H^1(\Omega;\mathbb R^2)\) in the sense of (7).

**Proof.**  Lemma 1 applied to \(T=\Phi_T\) gives exit from the local
translation manifold (24).  It remains only to compare that local manifold
with the full orbit in (4).

On the torus, the translation orbit is compact.  Since \(Q\) is nonconstant,
its stabilizer is discrete; outside small neighbourhoods of the stabilizer,
\(\|\tau_sQ-Q\|_{H^1}\) has a positive minimum.

On the line, put \(P=Q-Q_\infty\).  A nonzero \(L^2\) function cannot have a
nonzero period, and translations converge weakly to zero at infinity.
Consequently

\[
 \|\tau_sP-P\|_{H^1}>0\quad(s\ne0),
 \qquad
 \|\tau_sP-P\|_{H^1}^2
 \longrightarrow2\|P\|_{H^1}^2
 \quad(|s|\to\infty).
 \tag{27}
\]

Continuity then gives a positive separation from all shifts outside any
fixed neighbourhood of zero.  In either setting the exit radius from Lemma
1 may therefore be decreased so that exit from the local manifold is exit
from the full translation orbit.  This proves (7).  Since \(Q\in\mathcal
O(Q)\), (7) also implies Lyapunov instability of \(Q\) as an individual
equilibrium. \(\square\)

## 5. The frozen A2 profile

Let \(Q_{A2}\) be the true nonconstant periodic stationary profile enclosed
in the frozen A2 shooting box at

\[
 (r,a_2,\epsilon)=(0.08,0,1),\qquad a=1,\qquad d=r^4,
 \tag{28}
\]

and let \(L_*\) denote its true physical period.  The A2 moment validation
and self-adjoint-pencil theorem give a real co-periodic temporal eigenvalue

\[
 \lambda_{A2}\in(0.01,2).
 \tag{29}
\]

Theorem 2 therefore gives

\[
 \boxed{Q_{A2}\text{ is nonlinearly orbitally unstable in }
 H^1(\mathbb T_{L_*};\mathbb R^2).}
 \tag{30}
\]

This is a **co-periodic** nonlinear statement.  It neither encloses the full
Bloch spectrum nor turns the periodic eigenfunction into a localized
\(L^2(\mathbb R)\) perturbation of a wavetrain on the line.

## 6. The frozen `pulse_1` profile

Let \(Q_{p}\) be the P2c selected primary homoclinic represented by the
frozen `pulse_1` seed at the same parameter point (28).  The whole-line
moment theorem and target validation give a real isolated eigenvalue

\[
 \lambda_p\in(0.01,2)
 \tag{31}
\]

with an \(L^2(\mathbb R)^2\) eigenfunction.  Theorem 2 gives

\[
 \boxed{Q_p\text{ is nonlinearly orbitally unstable in }
 H^1(\mathbb R;\mathbb R^2)
 \text{ under localized perturbations}.}
 \tag{32}
\]

The far-field temporal essential spectrum touches the imaginary axis at
\(\pm i\) for this target.  Equivalently, the essential spectrum of a fixed
time map touches the unit circle.  This prevents an exponential-stability
or asymptotic-phase argument, but it does not affect (32): the eigenvector in
(31) gives the time map the spectral value
\(e^{T\lambda_p}>1\), and Lemma 1 requires no gap between the remaining
spectrum and the unit circle.

## 7. What is and is not obtained

No Evans function is needed for (30) or (32).  Such a construction could
later count unstable eigenvalues, determine algebraic multiplicities, or
continue spectral curves in parameters, but nonlinear orbital instability
uses only the existence of one positive temporal eigenvalue.

The two conclusions prove the following and no more:

- arbitrarily small admissible perturbations exist that leave a fixed
  neighbourhood of the translation orbit;
- A2 cannot be a Lyapunov-stable attractor for the co-periodic flow;
- `pulse_1` cannot be an orbitally stable attractor under localized
  \(H^1\) perturbations.

They do **not** prove that every or a generic perturbation grows, determine an
unstable dimension, provide a nonlinear exit-time asymptotic, identify the
post-exit state, or show selection of another stationary pattern.  They also
do not connect the exit dynamics to a Turing bifurcation or a finite-parameter
canard curve.
