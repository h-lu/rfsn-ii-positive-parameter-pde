# A2 periodic pattern: co-periodic spectral instability

## Status and exact scope

This note treats the periodic `A2` target in Issue #11.  It proves a general
moment criterion for a real positive co-periodic eigenvalue and reduces the
A2-specific computer-assisted input to one reversible periodic shooting
enclosure and one augmented integral.

The target-specific computation in Section 5 now supplies both inputs with
outward-rounded CAPD/FILIB intervals on the locked local toolchain.  It
therefore gives a local mathematical proof for a true periodic profile in the
frozen A2 shooting box.  Under the repository's evidence policy, the result is
still **non-claim-bearing** until it has an independent-machine replay; this is
a release/provenance boundary, not an unclosed mathematical inequality in the
local run.  This spectral note alone does not prove nonlinear instability;
the separate [semilinear bridge](NONLINEAR_ORBITAL_INSTABILITY.md) now turns
its positive eigenvalue into co-periodic nonlinear orbital instability.  No
statement concerns temporal pattern selection, a continuum of Bloch phases,
the `pulse_1` target, Turing selection, or canard identification.

## 1. Physical equation and co-periodic operator

Consider

\[
 u_t=v-f(u)+d u_{xx},\qquad
 v_t=\epsilon(a-u)+v_{xx},\qquad
 f(u)=\frac{u^3}{3}-u,
 \tag{1}
\]

where \(d,\epsilon>0\).  Let \((U,V)\) be a smooth \(L\)-periodic stationary
solution.  On the complexification of
\(L^2_{\rm per}(0,L;\mathbb R)^2\), with domain
\(H^2_{\rm per}(0,L)^2\), its co-periodic temporal linearization is

\[
 \mathcal L\binom{\phi}{\psi}
 =
 \binom{d\phi_{xx}-f'(U)\phi+\psi}
       {-\epsilon\phi+\psi_{xx}}.
 \tag{2}
\]

Differentiating the stationary equations gives the translation mode
\((U',V')\in\ker\mathcal L\).  The objective here is not to remove that
neutral eigenvalue, but to prove a second spectral point strictly to its
right.

## 2. A self-adjoint operator pencil

Put \(A=-\partial_x^2\) on periodic functions and, for real \(\lambda>0\),
put

\[
 R_\lambda=(\lambda+A)^{-1},\qquad
 K_\lambda=\lambda+f'(U)+dA+\epsilon R_\lambda .
 \tag{3}
\]

The second equation in \(\mathcal L(\phi,\psi)=\lambda(\phi,\psi)\)
gives \(\psi=-\epsilon R_\lambda\phi\).  Substitution in the first equation
therefore yields

\[
 \lambda>0\text{ is a real eigenvalue of }\mathcal L
 \quad\Longleftrightarrow\quad
 \ker K_\lambda\ne\{0\}.
 \tag{4}
\]

Each \(K_\lambda\) is self-adjoint with compact resolvent.  Its associated
closed quadratic form,
with form domain \(H^1_{\rm per}\), is

\[
 k_\lambda[\phi]
 =d\|\phi'\|_2^2
  +\int_0^L\bigl(f'(U)+\lambda\bigr)|\phi|^2\,dx
  +\epsilon\langle\phi,R_\lambda\phi\rangle .
 \tag{5}
\]

On any compact positive \(\lambda\)-interval, the resolvent identity makes
\(K_\lambda\) norm-resolvent continuous.  The lowest eigenvalue
\(\mu(\lambda)=\min_{\|\phi\|_2=1}k_\lambda[\phi]\) is consequently
continuous.

## 3. Moment criterion

**Proposition (periodic van der Pol moment criterion).**  Let \((U,V)\) be as
above.  If, for some \(0<\lambda_0<2\),

\[
 M_{\lambda_0}(U)
 :=\int_0^L\left[
 \lambda_0(U-a)^2+a(U-a)^3+\frac23(U-a)^4
 \right]dx<0,
 \tag{6}
\]

then \(\mathcal L\) has a real co-periodic eigenvalue
\(\lambda_*\in(\lambda_0,2)\).  In particular, the periodic profile is
linearly spectrally unstable and \(\lambda_*\) is separated from the
translation eigenvalue at zero.

**Proof.**  Integrating the second stationary equation shows that
\(w:=U-a\) has mean zero.  Let \(A_0\) be the restriction of \(A\) to the
mean-zero subspace.  Only on this subspace do we take the \(\lambda\downarrow0\)
limit: \(R_\lambda\le A_0^{-1}\) as quadratic forms and
\(R_\lambda w\to A_0^{-1}w\).  No full-space limit is asserted; the constant
Fourier mode of \(R_\lambda\) diverges.

The stationary equations give

\[
 A_0^{-1}w=-\frac{V-\overline V}{\epsilon},\qquad
 V=f(U)-dU''.
 \tag{7}
\]

Integration by parts, followed by the two exact cubic identities

\[
 \begin{aligned}
 f(a+w)&=f(a)+f'(a)w+aw^2+\tfrac13w^3,\\
 f'(a+w)&=f'(a)+2aw+w^2,
 \end{aligned}
 \tag{8}
\]

therefore gives

\[
 \begin{aligned}
 &d\|w'\|_2^2+\int_0^L f'(U)w^2\,dx
   +\epsilon\langle w,A_0^{-1}w\rangle\\
 &\hspace{35mm}=a\int_0^Lw^3\,dx+\frac23\int_0^Lw^4\,dx.
 \end{aligned}
 \tag{9}
\]

The resolvent order and (6) imply

\[
 k_{\lambda_0}[w]
 \le a\int_0^Lw^3\,dx+\frac23\int_0^Lw^4\,dx
       +\lambda_0\|w\|_2^2
 =M_{\lambda_0}(U)<0.
\tag{10}
\]

In particular, (6) implies \(w\ne0\), and therefore
\(\mu(\lambda_0)\le k_{\lambda_0}[w]/\|w\|_2^2<0\).  On the other hand,
\(f'(U)=U^2-1\ge-1\), so

\[
 k_2[\phi]\ge \|\phi\|_2^2
 \tag{11}
\]

and \(\mu(2)\ge1\).  Continuity supplies
\(\lambda_*\in(\lambda_0,2)\) with \(\mu(\lambda_*)=0\).  Compact
resolvent then gives a nonzero kernel vector of \(K_{\lambda_*}\), and (4)
reconstructs the eigenfunction of \(\mathcal L\).  Since
\(\lambda_*>\lambda_0>0\), it is separated from the translation zero mode.
\(\square\)

For the same periodic coefficients on the whole line, this proposition says
that the \(\theta=0\) Bloch fibre enters the open right half-plane.  The
periodic eigenfunction is not described as an \(L^2(\mathbb R)\) point
eigenfunction.

## 4. Frozen A2 calculation

The S0 contract is
[`numerics/config/vdp_a2_periodic_spectral_v1.json`](../numerics/config/vdp_a2_periodic_spectral_v1.json).
It fixes

\[
 (r,a_2,\epsilon)=(0.08,0,1),\qquad a=1,\qquad d=r^4,
 \qquad \lambda_0=0.01.
 \tag{12}
\]

The SHA-256-bound seed
`v7_periodic.npz::A2_*` has physical period
\(L=2.159661039071366\).  Composite periodic trapezoidal quadrature on its
saved 6001-point grid gives

\[
 \begin{aligned}
 \int_0^Lw^2dx&=9.477648606084774\times10^{-5},\\
 \int_0^Lw^3dx&=-1.8673672385999236\times10^{-6},\\
 \int_0^Lw^4dx&=5.530016477305500\times10^{-8},\\
 M_{0.01}(U)&=-8.827356014760763\times10^{-7}.
 \end{aligned}
 \tag{13}
\]

The sign is unchanged, to about \(2.1\times10^{-21}\) in the displayed
numerator, when the saved grid is thinned from 6001 to 301 points.  This is
excellent numerical QA, not an outward-rounded error bound.  Independently,
the existing 127-point Fourier screen gives the compatible candidate

\[
 \lambda_{\rm Fourier}=0.02138145204436229.
 \tag{14}
\]

The scalar moment route does not use (14) in its proof.

In the central variables of the A2 shooting problem,
\(w=-r^2U_c\) and \(dx=r\,d\xi\).  On the reversible half-orbit it is enough
to augment

\[
 z'=0.01U_c^2-r^2U_c^3+\frac23r^4U_c^4,
 \qquad z(0)=0,
 \tag{15}
\]

because

\[
 M_{0.01}(U)=2r^5z(T).
 \tag{16}
\]

The seed gives \(z(T)=-0.13469476340882486\).  The contract deliberately
freezes the much wider strict gate \(z(T)<-0.1\).

## 5. Target-specific A2 enclosure

The true profile is enclosed below without completing the repository-wide
Issue #7 box.  At the fixed parameters, start on the reversible zero-energy
section

\[
y_0(s)=\left(s,0,-\frac{s^2}{3}+\frac{r^2s^3}{12},0\right).
\tag{17}
\]

The displayed third component is the exact solution of the central
zero-energy equation on \(\operatorname{Fix}\mathcal R\), so (17) imposes
no floating projection onto the energy surface.  The corresponding boundary
conditions are

\[
F(s,T)=(P(T;s),Q(T;s))=(0,0)
\tag{18}
\]

for the exact central system

\[
 U_c'=P,\qquad
 P'=-V_c-U_c^2+\frac{r^2}{3}U_c^3,\qquad
 V_c'=Q,\qquad
 Q'=U_c .
 \tag{18a}
\]

Its reverser is
\((U_c,P,V_c,Q)\mapsto(U_c,-P,V_c,-Q)\).  A zero of (18) begins and ends
in its fixed set; reflection therefore gives a central orbit of period
\(2T\).  The exact inverse scaling at \(a_2=0,\epsilon=1\) is

\[
 x=r\xi,\qquad
 U_{\rm physical}=1-r^2U_c,\qquad
 V_{\rm physical}=f(1)-r^4V_c,
 \tag{18b}
\]

so the reflected orbit gives a stationary solution of (1), with
\(d=r^4\) and physical period \(L=2rT\).  The same scaling proves
(15)--(16) directly: the density in (15) depends only on \(U_c\), which is
unchanged by the reverser, so the two half-orbit integrals agree.

The frozen preselection box is

\[
 s\in[4.92556665,4.92556669],\qquad
 T\in[13.49788,13.49789].
 \tag{19}
\]

Floating diagnostics show that the long single-shooting map is severely
ill-conditioned.  The validator therefore lifts (18) to a 53-dimensional map
consisting of the seed and thirteen four-dimensional shooting nodes.  The
last node is followed by a rigorous Poincare map to the decreasing \(Q=0\)
section.  Strict Krawczyk inclusion and

\[
 \lVert I-CDF(X)\rVert_\infty
 <0.020642<1
 \tag{19a}
\]

prove existence and uniqueness in the hard-coded lifted outer box (X).
Every root in (X) lies in the smaller Krawczyk image (K(X)), whose scaled
components give the root enclosures below.  No uniqueness is claimed for every
possible root in the wider preselection box (19).

On the same root enclosure, the validator propagates (15) segment by segment
with outward rounding.  The local run gives

| quantity | outward-rounded enclosure |
|---|---:|
| seed \(s\) | \([4.9255666661290,4.9255666661292]\) |
| central half-period \(T\) | \([13.497881036840,13.497882046339]\) |
| physical period \(L=2rT\) | \([2.1596609658944,2.1596611274142]\) |
| last-node \(Q\) | \([6.574049912794,6.574058418102]\times10^{-4}\) |
| final-section \(U_c\) | \([-0.001321034222611,-0.001321033106519]\) |
| half moment \(z(T)\) | \([-0.1346947634090,-0.1346947634087]\) |
| physical \(M_{0.01}\) | \([-8.827356014769,-8.827356014754]\times10^{-7}\) |

The positive last-node (Q) and negative final-section (U_c=Q') select a
transverse return distinct from the initial point.  In addition,

\[
 z(T)<-0.1
 \quad\Longrightarrow\quad
 M_{0.01}(U)<2(0.08)^5(-0.1)
 =-6.5536\times10^{-7}<-5\times10^{-7}.
 \tag{19b}
\]

Thus reversible reflection gives a true nonconstant periodic stationary
profile, and the proposition gives the local mathematical conclusion

\[
 \boxed{\lambda_*\in(0.01,2)}.
 \tag{20}
\]

The source, toolchain, gates, and output are recorded in
[`validation/a2_periodic`](../validation/a2_periodic/README.md).  No rigorous
spectral matrix, Evans contour, eigenvalue multiplicity, or
continuum-in-\(\theta\) enclosure is required.

This target-specific enclosure defines “the true periodic orbit in the frozen
A2 seed box.”  Calling it a certified V6 cell or V7 symbolic edge would need
additional itinerary and exact-marking work; that stronger identity is not a
hypothesis of the spectral theorem.  The archived local run is not promoted
to a repository-level computer-assisted claim until the independent replay
required by `CLAIM_REGISTER.md` is available.

## 6. Why the closest published theorems do not close A2

- Glebsky and Lerman's Theorems 1--2 give localized-wave instability and an
  Eckhaus description for a small-amplitude local reversible-Hopf periodic
  family.  Its stable-background and local branch hypotheses are
  not satisfied or identified for the numerically constructed,
  homoclinic-shadowing A2 candidate;
  its periodic conclusion also does not force a positive eigenvalue in the
  co-periodic fibre.  At the finite-wavenumber Turing threshold of (1), the
  homogeneous zero mode already has positive real part
  \(\sqrt{\epsilon d}\), while at the A2 value \(a=1\) it is the Hopf pair
  \(\pm i\sqrt\epsilon\); neither is the stable background required there.
  See L. Yu. Glebsky and L. M. Lerman, *Nonlinearity*
  **10** (1997), 389--407, DOI
  [10.1088/0951-7715/10/2/005](https://doi.org/10.1088/0951-7715/10/2/005).

- Section 11 of Vo--Doelman--Kaper contains direct PDE simulations and
  explicitly exploratory stability discussion, not a Bloch theorem for A2.
  Their Proposition 2.1 is a spatial existence result, not a temporal spectral
  result.
  See T. Vo, A. Doelman, and T. J. Kaper, *SIAM J. Appl. Dyn. Syst.*
  **24** (2025), 2618--2684, DOI
  [10.1137/24M1690722](https://doi.org/10.1137/24M1690722).

- Gardner's Theorem 1.2 could transfer an
  already isolated positive homoclinic eigenvalue to all sufficiently long
  periodic waves, but the required pulse eigenvalue, family identification,
  and an explicit threshold covering winding two are absent here.  See
  R. A. Gardner, *J. Reine Angew. Math.* **491** (1997), 149--182, DOI
  [10.1515/crll.1997.491.149](https://doi.org/10.1515/crll.1997.491.149).

Thus the operator-pencil moment criterion is the shortest target-specific
route presently available; it is not a substitute for a theorem already
known to apply.

## Reproduction

Run

```bash
python3 -B numerics/vdp_a2_variational_instability.py \
  --output numerics/results/vdp_a2_spectral_instability/variational_report.json
python3 -B -m unittest numerics.test_vdp_a2_variational_instability -v
```

for the floating seed calculation.  Its JSON intentionally remains
`claim_bearing=false`: it is QA for the saved arrays, not the proof object.
Build and run the CAPD validator as documented in
[`validation/a2_periodic/README.md`](../validation/a2_periodic/README.md).
The resulting local interval proof is archived separately from the floating
report and remains non-claim-bearing only because independent replay is
pending.
