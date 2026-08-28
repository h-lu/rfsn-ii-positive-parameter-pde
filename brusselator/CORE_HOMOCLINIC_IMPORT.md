# Imported transverse symmetric core homoclinic

**Evidence status: Imported (computer-assisted at the frozen source).**  This
note freezes one result from the independent flagship repository.  It does
not import a positive-parameter theorem.  The source certificate reports a
successful interval proof; this repository has checked the frozen source and
hashes but has not claimed an independent-machine replay.

The 2026-08-28 read-only crosswalk to the compressed flagship paper, static
hash audit, and current public-access limitation are recorded in
[CORE_IMPORT_AUDIT.md](CORE_IMPORT_AUDIT.md). The frozen baseline below remains
normative until an explicit baseline-update commit says otherwise.

## 1. Frozen source

The source is H. Lu, *First returns, singular exits, and action finite parts
near a reversible Hamiltonian saddle-focus*, in the repository
<https://github.com/h-lu/reversible-rfsn-ii-waves>, at commit

\[
\mathtt{d54add098545063d5efe8f1d6f062d4cfc116a0d}.
\tag{1}
\]

The local and remote main branches were both at (1) when this import was
recorded.  The citation-level entry is:

- Proposition 8.6, *Intrinsic realization by the normal-form system*;
- specifically, the verification of Definition 2.1(I2), *Transverse
  homoclinic tube*; and
- the quantitative enclosures (8.36)--(8.40).

The source has no separately numbered theorem titled “symmetric homoclinic.”
The remainder of Proposition 8.6 verifies the other intrinsic two-ended
input clauses, while Corollary 1.2 gives the return--exit, action, and coding
outputs.  None of those additional inputs or outputs is used here.

The relevant frozen files have SHA-256 hashes:

    papers/paper-a/manuscript/main.tex
    0baf6335aad72d5893479d8876d2613671ecb8ac2ccd73664405dea4381e6a20

    validation/universal-core-symmetric-homoclinic/README.md
    34f3e15f475d22be939020bde2b8480ae33ba60a9c043f577088ab5d70253610

    validation/universal-core-symmetric-homoclinic/certificate.json
    ed0f9f58f8ba5f1d5c36dc7c3a72bb725599c4172a3cd610d890b88699fecfbd

    validation/universal-core-symmetric-homoclinic/homoclinic_interval_probe.cpp
    655cfe16e2cdb24185f11cbb314e7c0b2f029705d4588fdcbaf5a9f0993298f3

## 2. Core system and conventions

Throughout the import the ordered coordinate is fixed by

\[
 z=(U,P,V,Q).
\tag{2}
\]

The imported result concerns exactly

\[
 U'=P,\qquad P'=-U^2-V,\qquad V'=Q,\qquad Q'=U,
\tag{3}
\]

in this coordinate, with no external parameter and with the prime denoting
the time of (3).  Its reverser, primitive, and
Hamiltonian are

\[
\begin{aligned}
 \mathcal R(U,P,V,Q)&=(U,-P,V,-Q),\\
 \lambda_0&=P\,dU-Q\,dV,\\
 H_0&=\frac12(Q^2-P^2)-\frac13U^3-UV.
\end{aligned}
\tag{4}
\]

The origin is a saddle-focus with eigenvalues
\((\pm1\pm i)/\sqrt2\), and the nonconstant part of the imported orbit lies
in the regular part of \(H_0^{-1}(0)\).  The limiting equilibrium itself is a
critical point of \(H_0\).

The exact linear hyperbolic coordinates
\(u=(u_1,u_2)\), \(s=(s_1,s_2)\) used by the source are

\[
\begin{aligned}
 U&=u_1+s_1,& V&=u_2+s_2,\\
 P&=2^{-1/2}(u_1-s_1-u_2+s_2),&
 Q&=2^{-1/2}(u_1-s_1+u_2-s_2).
\end{aligned}
\tag{5}
\]

In these coordinates the reverser exchanges \(u\) and \(s\).  The true local
unstable manifold is written \(s=h^u_{\rm true}(u)\), and the source curve is

\[
 u_\rho(\phi)=0.01(\cos\phi,\sin\phi),\qquad
 z_\rho(\phi)=\bigl(u_\rho(\phi),
 h^u_{\rm true}(u_\rho(\phi))\bigr),
\tag{6}
\]

with (5) used to return to \(z=(U,P,V,Q)\).  Time \(T\) below is the finite
flight time from (6) to the symmetry section.  It is not the infinite time
from the equilibrium to that section.

## 3. Imported statement

There is a unique zero in the source shooting box of

\[
 \mathcal M_0(\phi,T)
   =(P,Q)\!\left(\Phi_0^T(z_\rho(\phi))\right),
\tag{7}
\]

where \(\Phi_0\) is the flow of (3).  Its enclosures are

\[
\begin{aligned}
 \phi_0&\in
 [5.8615055856447817,5.8615055856450482],\\
 T_0&\in
 [9.6374420678958099,9.6374420678971511],\\
 U(T_0)&\in
 [4.8785234574459304,4.8785234988116768],\\
 V(T_0)&\in
 [-7.9333304994224827,-7.933330385013492].
\end{aligned}
\tag{8}
\]

At the exact endpoint, \(P(T_0)=Q(T_0)=0\).  The half-orbit has no earlier
nonzero hit of \(\operatorname{Fix}\mathcal R\), and reflection at the
endpoint gives a nonconstant \(\mathcal R\)-symmetric homoclinic orbit
\(\Gamma_0\) to the origin.  The uniqueness in this statement is local to
the reported shooting box; no global uniqueness of core homoclinics is
imported.

The source also proves

\[
 \det D_{(\phi,T)}\mathcal M_0(\phi_0,T_0)
 \in[149.56393055300413,149.56404227745782],
\tag{9}
\]

and

\[
\begin{aligned}
 \partial_\phi U(T_0)&\in
 [-10.889708535478462,-10.8897049543477],\\
 \partial_\phi V(T_0)&\in
 [35.417125972639965,35.417127394127888].
\end{aligned}
\tag{10}
\]

The manuscript's equations (8.36)--(8.40) give the phase, flight-time,
determinant, and tangent-row enclosures and identify the event as the first
positive symmetry hit.  The endpoint \(U,V\) enclosures in (8), local
uniqueness in the shooting box, and the interval sign checks excluding an
earlier hit are recorded in the frozen certificate and its README.  This
distinction is retained so that certificate-only data are not misattributed
to a displayed manuscript equation.

For Track B, (9) is the decisive datum.  To make the transversality bridge
explicit, set

\[
 G(\phi,T)=\Phi_0^T(z_\rho(\phi)),\qquad
 N(U,P,V,Q)=(P,Q).
\]

Then \(\mathcal M_0=N\circ G\),
\(\ker DN=T\operatorname{Fix}\mathcal R\), and the image of \(DG\) is
contained in \(T_cW^u_0(0)\), where
\(c:=G(\phi_0,T_0)\).  Since (9) says that
\(D(N\circ G)\) is invertible, \(DG\) has rank two, so its image is all of
\(T_cW^u_0(0)\).  If \(DG a\in T_c\operatorname{Fix}\mathcal R\), then
\(0=DN\,DG a=D\mathcal M_0 a\), and hence \(a=0\).  Both tangent spaces
have dimension two, and consequently

\[
 W^u_0(0)\pitchfork\operatorname{Fix}\mathcal R
 \quad\text{at the symmetry endpoint}.
\tag{11}
\]

The additional rows (10), together with energy conservation, imply the
source paper's Hamiltonian formulation

\[
 T_cW^u_0(0)\cap T_cW^s_0(0)
 =\operatorname{span}\{F_0(c)\}
\tag{12}
\]

inside the regular zero-energy hypersurface.  Equation (12) is not ambient
transversality of \(W^u\) and \(W^s\) in four dimensions.  The
positive-parameter Brusselator proof uses the reversible matching
transversality (11), not a positive-parameter energy surface.

## 4. Computer-assisted content

On the complete disk \(\|u\|_2\le0.01\), the source encloses the actual
unstable graph relative to its degree-ten polynomial approximation by

\[
 \|h^u_{\rm true}-h^u_{10}\|_2\le10^{-20},\qquad
 \|D(h^u_{\rm true}-h^u_{10})\|_{2\to2}\le10^{-18}.
\tag{13}
\]

The interval proof uses outward-rounded CAPD/FILIB flow and first-variation
enclosures, a two-dimensional Krawczyk inclusion, the determinant and phase
rows (9)--(10), and interval sign checks excluding an earlier symmetry hit.
The certificate status is
PASS-ROBUST-SYMMETRIC-HOMOCLINIC.  The bounds (13) enclose the one fixed
invariant graph; they do not assert that arbitrary independent
\(C^0/C^1\) perturbations are invariant.

The frozen environment lists g++ 15.2, CAPD commit
731079217a9254ea2948d742df2b170895effe7f, and FILIB.  During this import,
the frozen static source and dependency hashes were checked.  No statement
of an independent-machine or publication-archive replay is made here.

## 5. Exact crosswalk to the Brusselator

The \(A=B=1\) scaled Brusselator family in
[MODEL_AND_SCALING.md](MODEL_AND_SCALING.md) reduces at \(r=0\) exactly to
(3), with the same coordinate order, reverser, and time

\[
 \xi=x/r=x_2.
\tag{14}
\]

Thus no sign, constant coordinate factor, or clock factor intervenes in the
base matching determinant (9).

This import supplies only the base orbit and the nonzero derivative for the
positive-\(r\) implicit-function argument.  It does not supply:

- parameter-dependent stable or unstable manifolds;
- continuation to the non-Hamiltonian positive-\(r\) vector field;
- uniform full-orbit tails;
- positive concentrations or inverse-scaling estimates;
- finite-winding, multipulse, or all-winding continuation;
- a positive-parameter action identity; or
- temporal stability.
