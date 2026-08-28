# Explicit finite overlaps for the positive-Kato saddle chart

**Proof contract:** `rfsn-vdp-p2d-explicit-finite-chart-overlaps/1`

**Local conclusion.** This note closes `V2.CHART.OVERLAPS` on the frozen
P2 bridge. Together with the six preceding P2d atoms, it gives a local
mathematical pass for the parent `V2.EXACT_CHART`. The conclusion is about
the saddle chart and its physical incoming/outgoing markings. It does not
prove the complete P2e event census, any positive-end validation gate,
independent replay, temporal stability, Turing selection, or a canard
connection.

## 1. The finite cover and the statement

Write the normalized bridge parameters as

\[
 \theta=(\theta_r,\theta_a,\theta_\epsilon)\in
 \mathcal P=[-1,1]^3,
 \qquad
 r=\frac{1+\theta_r}{25},\quad
 a_2=\frac{\theta_a}{4},\quad
 \epsilon=1+\frac{\theta_\epsilon}{5}.
\tag{1}
\]

Use two cover members, one containing the anchor face and one equal to the
positive target box in the \(r\)-direction:

\[
 \begin{aligned}
 V_0&=\{\theta\in\mathcal P:\theta_r\le\tfrac14\},&
 U_0&=\{\theta\in\mathcal P:\theta_r<\tfrac12\},\\
 V_+&=\{\theta\in\mathcal P:\theta_r\ge0\},&
 U_+&=\{\theta\in\mathcal P:\theta_r>-\tfrac14\}.
 \end{aligned}
\tag{2}
\]

The sets \(U_0,U_+\) are open in the relative topology of the compact
parameter box. Both \(V_0,V_+\) are compactly contained in their
corresponding open sets, with normalized collar \(1/4\), or \(r\)-collar
\(1/100\). The model and chart formulas have the already certified analytic
extension through the parameter faces, so this relative cover retains the
stated two external derivatives. Moreover

\[
 \mathcal P=V_0\cup V_+,\qquad
 V_0\cap V_+=\{0\le\theta_r\le\tfrac14\}\times[-1,1]^2.
\tag{3}
\]

Thus the cover has a genuine overlap joining the anchor member to the
positive member. The \(16\times8\times4\) interval grid remains only the
outward-bound partition used to certify uniform coefficients.

Let

\[
 \varepsilon_{\rm nf}=2^{-22},\qquad
 \mathcal D_{\rm src}=\Delta_{3\varepsilon_{\rm nf}/8},\qquad
 \mathcal D_{\rm inv}=\Delta_{\varepsilon_{\rm nf}/2},\qquad
 \mathcal D_{\rm phys}=\Delta_{\varepsilon_{\rm nf}/8},
\tag{4}
\]

and let

\[
 \rho=\frac5{2^{26}},\qquad
 \nu_p=\frac{25}{2^{58}}.
\tag{5}
\]

We prove that the restrictions to \(U_0,U_+\) have common chart and
inverse domains, fixed exact primitive gauges, compatible physical slides,
and a finite overlap cocycle. Every transition and inverse preserves the
stable/unstable axes and the sign of \(I_2^{\rm K}=\nu\), extends to the
oriented real blow-up with state-\(C^3\), parameter-\(C^2\) bounds, and has
degree \(+1\) on its positive-Kato phase boundary.

## 2. The nonlinear chart overlaps are identities

The contract
`rfsn-vdp-p2d-explicit-global-moser-majorant/1` constructs one normalized
family

\[
 \Phi_\mu^{\rm K}=L_\mu\circ\Theta_\mu^{\mathbb R}
\tag{6}
\]

on \(\mathcal D_{\rm src}\), not 512 independently normalized charts. The
same positive square-root branches, Kato frame, homological projection,
Lie-map order, and zero-normalized primitive are used on every coefficient
cell. It also constructs the two-sided inverse on the domains in (4) and a
single gauge

\[
 (\Phi_\mu^{\rm K})^*\lambda=\lambda_0+df_\mu,
 \qquad f_\mu(0)=0.
\tag{7}
\]

For \(i\in\{0,+\}\), define only restrictions,

\[
 \Phi_i=\Phi^{\rm K}|_{U_i},\qquad
 \Psi_i=(\Phi^{\rm K})^{-1}|_{U_i},\qquad
 f_i=f|_{U_i}.
\tag{8}
\]

Consequently, on \(U_i\cap U_j\),

\[
 \Psi_j\circ\Phi_i=\operatorname{id},\qquad
 \Psi_i\circ\Phi_j=\operatorname{id},\qquad
 f_i=f_j.
\tag{9}
\]

These are exact identities on the common domains, not small numerical
overlap residuals. In particular, the chart transition and its inverse are
exact symplectic, their primitive difference is exactly zero, and they
preserve \(x=0\), \(y=0\), \(I_2^{\rm K}=0\), and both signs of
\(I_2^{\rm K}\). They extend as the identity to the oriented blow-up. Their
first state derivative is the identity and every state derivative of order
two or three, every positive parameter derivative, and every mixed
state-parameter derivative vanishes.

This explicitly produces a finite cover; it does not infer the overlap
claim merely from the existence of a global formula.

## 3. Auxiliary and physical section markings

Let \(\iota_\mu^{\rm in/out}\) be the exact radial sections at radius \(\rho\)
and let \(S_\mu^{\rm in/out}\) be the event-free first-hit slides proved in
`rfsn-vdp-p2d-explicit-physical-slides/1`. The physical embeddings were
defined by

\[
 \iota_\mu^{\rm in/out,phys}
 =S_\mu^{\rm in/out}\circ\iota_\mu^{\rm in/out},
\tag{10}
\]

using the same action \(\nu\) and the phase transported by the Hamiltonian
flow. Therefore the coordinate representative of (10) is exactly

\[
 (\phi,\nu)\longmapsto(\phi,\nu)
\tag{11}
\]

on both incoming and outgoing faces. First-hit uniqueness and no recrossing
make (10) an embedding and identify the inverse on its image. In the
transported coordinates, that inverse is again (11).

After restriction to tangent vectors of the two zero-energy sections, the
variable-time Hamiltonian identity gives

\[
 (S_\mu^{\rm in/out})^*\omega=\omega,
 \qquad
 (S_\mu^{\rm in/out})^*\lambda-\lambda=d\mathcal A_\mu^{\rm in/out}.
\tag{12}
\]

Combining (12) with the already fixed auxiliary gauges gives fixed physical
gauges, rather than gauges chosen separately on cover members. Restriction
to \(U_i\cap U_j\) therefore leaves both the embedding and its gauge
unchanged. Equation (11) proves exact symplecticity, preservation of the
signed action, extension through \(\nu=0\), and degree \(+1\) on the phase
circle. The physical-slide proof supplies the full state-\(C^3\),
parameter-\(C^2\) bounds for the ambient embeddings. The transition and its
inverse in the marked coordinates have the sharper identity bounds from
(11).

## 4. The physical source-phase seam

The transported phase need not equal the direct P2bK phase by a constant
shift: the nonlinear Moser map and the finite slide may change it
nonlinearly. We now compare the two markings without making that
identification.

Write the outgoing physical endpoint in algebraic coordinates as

\[
 \widehat E_\mu(\psi,\nu)
 =T_\mu^{-1}\iota_\mu^{\rm out,phys}(\psi,\nu)
 =(u_\mu(\psi,\nu),s_\mu(\psi,\nu)).
\tag{13}
\]

On \(\nu=0\), it lies on the true unstable graph,
\(s_\mu=H_\mu(u_\mu)\), and \(|u_\mu|=R=1/100\). The direct P2bK source
parameterization uses

\[
 u=R\,R_{\chi(\mu)}e_\phi,\qquad R_{\chi(\mu)}\in SO(2).
\tag{14}
\]

Define the circle map \(\kappa_\mu\) exactly by

\[
 e_{\kappa_\mu(\psi)}
 =R_{-\chi(\mu)}\,\frac{u_\mu(\psi,0)}R .
\tag{15}
\]

Both sides parameterize the same complete true-source circle. To fix the
relative orientation without assuming the desired conclusion, inspect the
unstable axis at the equilibrium. The already audited tangent map from the
positive Kato plane to the algebraic unstable plane has the form

\[
 \varkappa_\mu^{-1/2}C_{{\rm AK},\mu}A_{\vartheta,\mu},
 \qquad
 \det(\varkappa_\mu^{-1/2}C_{{\rm AK},\mu}A_{\vartheta,\mu})
 =\varkappa_\mu^{-1}\sigma_\mu^2>0.
\]

The exact chart is nondegenerate on the connected local unstable disk.
The unique outward first-hit slide, with no recrossing, continues its
boundary orientation to the radius-\(R\) graph circle. Finally,
\(R_{\chi(\mu)}\in SO(2)\) is orientation preserving. Hence
\(\kappa_\mu\) is an orientation-preserving circle diffeomorphism and

\[
 \deg\kappa_\mu=+1.
\tag{16}
\]

A continuous real lift is fixed by one value on the contractible parameter
box. Changing that value by an integer deck constant changes none of the
derivative bounds or the physical marking.

### 4.1 A quantitative inverse margin

The exact section identity at the physical face gives

\[
 1=|\omega(E_\psi,E_\nu)|
 \le |E_\psi|\,|E_\nu|.
\tag{17}
\]

The first-order endpoint gate gives \(|E_\nu|<2^{9443}\), and therefore
\(|E_\psi|>2^{-9443}\). At \(\nu=0\),

\[
 E_\psi=T_\mu(u_\psi,DH_\mu(u)u_\psi).
\]

The authenticated bounds \(\|T_\mu\|<2^3\) and \(\|DH_\mu\|\le1\) imply
\(|E_\psi|<2^4|u_\psi|\). Since (15) gives
\(|u_\psi|=R|\partial_\psi\kappa_\mu|\), we obtain

\[
 \partial_\psi\kappa_\mu
 >100\,2^{-9447}>2^{-9441}.
\tag{18}
\]

The sign is positive by (16). Thus both the map and its inverse have one
uniform quantitative nondegeneracy margin.

### 4.2 The complete finite derivative budget

The physical-slide recurrence before the terminal \(T_\mu\) multiplication
gives the complete algebraic endpoint rectangle

\[
 \|D_\psi^iD_\mu^j u_\mu(\psi,0)\|<2^{46518425},
 \qquad 0\le i\le3,\quad0\le j\le2.
\tag{19}
\]

This is the existing proof-bound recurrence, not a new ODE integration.
Multiplication by \(R^{-1}=100<2^7\), the value and two parameter jets of
\(R_{-\chi}\), and at most four parameter Leibniz allocations give

\[
 \|D_\psi^iD_\mu^j e_{\kappa_\mu(\psi)}\|<2^{K_v},
 \qquad K_v:=46518440.
\tag{20}
\]

For an allowed colored derivative with \(i\le3\), \(j\le2\), and mixed total
order \(n=i+j\le3\), differentiate \(v=e^{J\kappa}\), isolate the unique top
derivative of \(\kappa\), and bound the fewer than \(B_3=5<2^3\) lower
Faà di Bruno terms. The deliberately coarser explicit
recurrence

\[
 k_1=K_v+1,\qquad
 k_n=7+\max\{K_v,\ n(1+k_{n-1})\},\quad2\le n\le3,
\tag{21}
\]

therefore bounds every required derivative of \(\kappa_\mu\) by \(2^{k_n}\).
This is precisely the mixed-total-order-three boundary-marking requirement
of the frozen admissible-change definition. No fourth or fifth state
derivative of the true unstable graph is inferred.

Fix the real lift at one base point with
\(\widetilde\kappa_{\mu_0}(0)\in[0,2\pi)\). Since the normalized cube has
diameter below \(4\), \(2\pi<8\), and the degree-one displacement is
periodic, the first-derivative bound also gives the explicit zeroth-order
estimate

\[
 |\widetilde\kappa_\mu(\psi)-\psi|<2^{k_1+4}.
\tag{21a}
\]

For \(\lambda_\mu=\kappa_\mu^{-1}\), differentiate
\(\kappa_\mu(\lambda_\mu(\vartheta),\mu)=\vartheta\), use (18), and isolate
the unique top derivative of \(\lambda_\mu\). The similarly explicit
recurrence

\[
 \ell_1=9442+k_3,\qquad
 \ell_n=9450+k_3+n(1+\ell_{n-1}),\quad2\le n\le3,
\tag{22}
\]

bounds all mixed derivatives of its inverse through total order three. The
incoming comparison is its reversible image and has the same degree and
bounds. With the inverse lift chosen compatibly,

\[
 |\widetilde\lambda_\mu(\vartheta)-\vartheta|<2^{\ell_1+4}.
\tag{22a}
\]

The map \(\kappa_\mu\) is only the common source-boundary marking
comparison. Exact symplecticity, primitive gauges, signed-axis preservation,
and the oriented-blow-up transition are already the identity chart
statements (9)--(12), with their full state-\(C^3\), parameter-\(C^2\)
rectangle. No new two-dimensional symplectic collar, and no stronger
rectangular regularity for the boundary-only seam, is being asserted here.

## 5. Cocycle and parent conclusion

All chart transitions in (9) are identities. All auxiliary-to-physical
coordinate transitions in (11) are identities. The boundary comparison
\(\kappa_\mu\) in (15) is one globally defined physical map, so its
restrictions from \(U_0\) and \(U_+\) agree on their overlap. It follows that
every pairwise inverse identity and every triple cocycle identity holds
exactly. The fixed primitive gauges agree around each cocycle, and no sign or
phase orientation changes on an overlap.

The finite cover (2), common domains (4), exact identities (9), exact slide
gauges (12), signed-axis preservation, identity blow-up extensions, seam
bounds (18)--(22), and degree calculation (16) discharge
`V2.CHART.OVERLAPS`. Since

\[
 \begin{gathered}
 \texttt{SYMPLECTIC_FRAME},\quad
 \texttt{ANALYTIC_NORMAL_FORM},\quad
 \texttt{ZERO_ENERGY},\quad
 \texttt{EXACT_SECTIONS},\\
 \texttt{WEIGHTED_PASSAGE},\quad
 \texttt{PHYSICAL_SLIDES},\quad
 \texttt{OVERLAPS}
 \end{gathered}
\]

have now all passed locally, the P2d parent `V2.EXACT_CHART` also passes
locally on \(|\nu|\le25/2^{58}\). This is a mathematical completion of the
local chart package. The repository-wide explicit-box certificate remains
`INCONCLUSIVE`, `claim_bearing=false`, and `release_eligible=false` while
later validation inputs and the second-machine replay are absent.
