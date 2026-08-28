# Explicit slides to the radius-\(10^{-2}\) physical saddle faces

**Proof contract:** `rfsn-vdp-p2d-explicit-physical-slides/1`

**Local conclusion.**  On the complete frozen positive-parameter bridge and
on

\[
 |\nu|\le \nu_{\rm p}:=\frac{25}{2^{58}},
\tag{1}
\]

this note joins the exact auxiliary Kato sections to the already frozen
radius-\(10^{-2}\) physical saddle faces.  It proves block containment,
local event exclusion, unique first hits, a uniform hit speed, slide times
smaller than \(19\), and a complete state-\(C^3\)/parameter-\(C^2\)
rectangle of finite bounds.  It also closes the physical
winding/residence comparison with the uniform constant \(C_{\rm phys}=7\).
Together with its proof-bound rational checker, this discharges only
`V2.CHART.PHYSICAL_SLIDES`.  The overlap atlas and `V2.EXACT_CHART` remain
open.

The radius below is the radius used by the existing P2bK source and P2c
event interface.  In particular, no smaller radial face is renamed
``physical'' in this argument.

## 1. Frozen local interfaces

Use the algebraic moving coordinates \(z=(u,s)\in\mathbb R^2\times
\mathbb R^2\) of P2a and the frozen linear map
\(Z=T_\mu z=(U,P,V,Q)\) to the physical central coordinates.  Denote the
physical Hamiltonian flow by \(\varphi_\mu^t\) and its algebraic conjugate by

\[
 \widehat\varphi_\mu^t
 :=T_\mu^{-1}\circ\varphi_\mu^t\circ T_\mu.
\tag{2a}
\]

Put

\[
 R_0=\frac1{100},\qquad
 \mathcal B=\{\|u\|_2\le R_0,\ \|s\|_2\le R_0\}.
\tag{2}
\]

The exact auxiliary Kato radius is

\[
 \rho=\frac5{2^{26}}.
\tag{3}
\]

Let \(\iota^{\rm out}_{\mu}(\psi,\nu)\) be the exact outgoing auxiliary
section in physical central coordinates constructed in the exact-sections
atom, and set

\[
 \widehat\iota^{\rm out}_\mu
 :=T_\mu^{-1}\circ\iota^{\rm out}_\mu.
\tag{3a}
\]

The inherited outgoing physical surface is

\[
 \Sigma^{\rm out}_\mu
 :=\{Z\in\widehat H_\mu^{-1}(0):
       \|\pi_uT_\mu^{-1}Z\|_2=R_0,
       \ \|\pi_sT_\mu^{-1}Z\|_2<R_0,
       \ X_\mu(g^u\circ T_\mu^{-1})>0\}.
\tag{3b}
\]

Thus the radius-\(R_0\) surface is selected before a trajectory is
computed.  Let \(\tau^{\rm out}_\mu(\psi,\nu)\) be the first positive time
at which

\[
 g^u\!\left(\widehat\varphi_\mu^t
       (\widehat\iota^{\rm out}_\mu(\psi,\nu))\right)=0,
 \qquad g^u(u,s):=10^4\|u\|_2^2-1.
\tag{4}
\]

The outgoing physical face and its transported marking are defined by

\[
 \begin{aligned}
 \iota^{\rm out,phys}_\mu(\psi,\nu)
 &=\varphi_\mu^{\tau^{\rm out}_\mu(\psi,\nu)}
      \bigl(\iota^{\rm out}_\mu(\psi,\nu)\bigr),\\
 P^{\rm out}_\mu
 &=\operatorname{image}\iota^{\rm out,phys}_\mu
   \subset\Sigma^{\rm out}_\mu.
 \end{aligned}
\tag{5}
\]

Define the incoming face and slide by reversibility.  Equivalently, the
incoming forward slide begins on the radius-\(R_0\) stable face and ends on
the exact auxiliary incoming section.  The same action label \(\nu\), and
the phase label transported by the Hamiltonian flow, are used at both ends.

At \(\nu=0\), the exact normal-form unstable axis maps to the true unstable
manifold.  Uniqueness of that manifold and first-hit uniqueness below show
that the image set in (5) is exactly the radius-\(R_0\) P2bK source circle.
The transported phase and the algebraic boundary angle can differ by a
degree-one circle reparametrization; certifying all such marking changes is
the next `V2.CHART.OVERLAPS` atom and is not assumed here.

The hash-bound configuration
`vdp-p2d-physical-slides-v1` freezes the local event-support family
`V2.P2E.CENTRAL_EVENT_GERMS`: its restriction to the closed block (2) is
the empty list, the two physical faces are block boundaries rather than
members of that excluded family, and every non-saddle germ is supported in
an exterior flow box beyond a physical face.  This is the allowed shrinking
of the ambient event flow boxes already used in the V2 construction.  Every
segment used in (5) is therefore event-free once block containment is
proved.  The same configuration hash-binds the existing P2c source
interface.  P2e must still validate the exterior extensions, all incidences,
and the complete connected event-cell census; the present local support
contract is not a P2e claim.

## 2. The auxiliary face lies in the P2a cone

Write \(C_{\rm AK}=\sigma R_\chi\) for the proved Kato-to-algebraic
expanding-plane change.  The P2bK certificate and the P2d symplectic-frame
certificate give

\[
 \frac23<\sigma<\frac34,\qquad
 \frac{63}{64}<\kappa^{-1/2}<\frac{65}{64}.
\tag{6}
\]

If \((\widetilde x,\widetilde y)\) denotes the point after the Moser map,
the authenticated completion and Kato-direction identities read, up to the
fixed orthogonal reverser factor on the stable block,

\[
 u=\kappa^{-1/2}C_{\rm AK}A_\vartheta\widetilde y,
 \qquad
 s=\kappa^{-1/2}C_{\rm AK}A_\vartheta C_0\widetilde x.
\tag{6a}
\]

All matrices following the two positive scalar factors are orthogonal.

The normal-form-to-algebraic radial factor is therefore
\(\sigma\kappa^{-1/2}\), not either factor separately, and

\[
 \frac{21}{32}<\sigma\kappa^{-1/2}<\frac{195}{256}.
\tag{7}
\]

Let

\[
 d_\Theta=\frac{75}{23191581884416}
\tag{8}
\]

be the authenticated forward Moser displacement.  Twice this value bounds
either real two-dimensional block after the fixed real/complex unitary
identification.  On (1), the weighted-passage atom also proves
\(|q_\mu(\nu)/\nu|<5/4\).  Hence the complementary normal-form radius on
the outgoing face is smaller than

\[
 \frac{13}{8}\frac{|\nu|}{\rho}
 \le \frac{65}{2^{35}}.
\tag{9}
\]

Consequently the algebraic coordinates of every outgoing auxiliary point
satisfy

\[
 \begin{aligned}
 \|u_0\|_2&>u_-:=\frac{21}{32}(\rho-2d_\Theta)
   =\frac{72565815}{1484261240602624},\\
 \|u_0\|_2&<u_+:=\frac{195}{256}(\rho+2d_\Theta)
   =\frac{673942425}{11874089924820992},\\
 \|s_0\|_2&<s_+:=\frac{195}{256}
   \left(\frac{65}{2^{35}}+2d_\Theta\right)
   =\frac{8790443025}{6079534041508347904}.
\end{aligned}
\tag{10}
\]

Exact rational subtraction gives

\[
 \begin{gathered}
 u_- -2^{-25}
 =\frac{28331383}{1484261240602624}>0,\qquad
 2^{-24}-u_+
 =\frac{33808487}{11874089924820992}>0,\\
 \frac{u_-}{32}-s_+
 =\frac{497981295}{6079534041508347904}>0.
\end{gathered}
\tag{11}
\]

The outer normal-form source-chart radius is
\(\rho_{\rm src}=3/2^{25}\).  If an outgoing orbit leaves that chart, its
expanding factor reaches \(\rho_{\rm src}\) first, because the stable factor
is decreasing there.  At that moment

\[
 \|u\|_2>u_{\rm exit}:=\frac{21}{32}
       (\rho_{\rm src}-2d_\Theta)
 =\frac{43540119}{742130620301312},
\tag{11a}
\]

and

\[
 u_{\rm exit}-u_+
 =\frac{2063589}{1079462720438272}>0.
\tag{11b}
\]

Thus every auxiliary point is strictly inside (2) and starts in the
individual forward cone

\[
 \|s\|_2<\|u\|_2.
\tag{12}
\]

## 3. Block containment, first hit, and time

In the coordinates of (2), the exact polynomial field is

\[
 \begin{aligned}
 u'&=B_u u+w_\mu n_\mu(U),\\
 s'&=B_s s-w_\mu n_\mu(U),\\
 U&=u_1+s_1,\qquad
 n_\mu(U)=-a_\mu U^2+b_\mu U^3.
\end{aligned}
\tag{13}
\]

The hash-bound P2a certificate proves on the whole block (2)

\[
 m_{\rm cone}>1,\qquad
 \gamma_0>\frac23,\qquad
 m_{\rm face}>\frac1{150}.
\tag{14}
\]

Apply the P2a difference-cone inequality to the current point and the
equilibrium.  It makes (12) forward invariant until the first block exit.
Inside that cone,

\[
 \frac{d}{dt}\|u(t)\|_2\ge\gamma_0\|u(t)\|_2
 >\frac23\|u(t)\|_2.
\tag{15}
\]

The stable face cannot be the first exit, while the unstable radius is
strictly increasing.  Therefore any exit is the unique first hit of (4).
The target speed satisfies

\[
 Xg^u
 =2\cdot10^4R_0\frac{d}{dt}\|u\|_2
 >2\cdot10^4R_0\frac1{150}
 =\frac43.
\tag{16}
\]

It remains only to prove that the hit occurs.  The elementary exponential
series gives

\[
 e>\frac83,\qquad e^{2/3}>\frac{17}{9},
\tag{17}
\]

because the displayed right sides are strict finite partial sums.  Hence

\[
 e^{38/3}>
 \left(\frac83\right)^{12}\frac{17}{9}
 =\frac{1168231104512}{4782969}.
\tag{18}
\]

The exact reach margin is

\[
 \frac{1168231104512}{4782969}u_- -R_0
 =\frac{213923044351}{110193706764900}>0.
\tag{19}
\]

If the target had not been reached by time \(19\), (15), (18), and (19)
would put \(\|u(19)\|_2>R_0\), a contradiction.  Thus

\[
 0<\tau^{\rm out}_\mu<19.
\tag{20}
\]

Reversibility gives the identical statements for the incoming slide:

\[
 0<\tau^{\rm in}_\mu<19,\qquad
 \tau^{\rm in}_\mu+\tau^{\rm out}_\mu<38.
\tag{21}
\]

The argument includes both signs of \(\nu\) and \(\nu=0\).  Only the
intervening stable-to-unstable saddle passage, not either finite slide,
becomes infinite on the zero-action axes.

## 4. Exact section data

The source embedding is exact symplectic and has section form
\(d\psi\wedge d\nu\).  A variable-time map is not symplectic on the whole
ambient four-space.  Here both sections lie in the same zero-energy surface:
with the repository convention \(\iota_{X_H}\omega=dH\), the variable-time
map \(P(z)=\varphi^{\tau(z)}(z)\) satisfies

\[
 P^*\omega=\omega+d\tau\wedge dH,
 \qquad
 P^*\lambda=\lambda+d\mathcal A-H\,d\tau,
\tag{21a}
\]

where

\[
 \mathcal A(z)=\int_0^{\tau(z)}
   \bigl(H+\lambda(X_H)\bigr)(\varphi^s(z))\,ds.
\tag{21b}
\]

On tangent vectors to the common zero-energy surface, \(dH=0\), and on the
surface itself \(H=0\).  Thus (21a) transports the source primitive gauge to
a fixed primitive gauge on (5), and

\[
 (\iota^{\rm out,phys}_\mu)^*\omega
   =d\psi\wedge d\nu.
\tag{22}
\]

The incoming formula follows by reversibility.  Thus \(\nu\) is the same
signed transverse action at the auxiliary and physical faces, and each
transported phase marking has degree \(+1\).  This is exact action
preservation, not a numerical symplectic-defect estimate.

The first-hit map is a local diffeomorphism by (16).  It is also globally
injective on the marked auxiliary face.  Inside the exact chart the
normal-form expanding radius is strictly increasing, so that face cannot be
crossed twice.  If an orbit first leaves the chart, (11a)--(11b) put its
algebraic expanding radius strictly above the largest radius of any
auxiliary-face point; (15) then keeps it above that value.  Thus the orbit
cannot return to the auxiliary face.  Two source points with one endpoint
would contradict this no-recross property.  Hence (5) is the reachable
marked patch of the inherited surface (3b), and its image is an embedded
physical face rather than a newly selected radial interface.

## 5. Complete regularity rectangle

Use the normalized external parameters

\[
 r=\frac{1+\theta_r}{25},\qquad
 a_2=\frac{\theta_a}{4},\qquad
 \epsilon=1+\frac{\theta_\epsilon}{5},\qquad
 \theta\in[-1,1]^3.
\tag{23}
\]

We record one deliberately coarse finite generator, because no downstream
smallness condition uses the size of these slide jets.

The authenticated P2b coefficient table bounds the normalized
parameter-two-jets of the linear blocks and of
\(G_\mu(U)=w_\mu n_\mu(U)\).  Its rational gates include

\[
 \begin{array}{c|ccc}
  &j=0&j=1&j=2\\ \hline
 B-B_{\rm core}&101/10000&3/250&3/400\\
 D_U^2G&101/100&23/2000&3/400\\
 D_U^3G&3/400&3/400&3/800.
 \end{array}
\tag{24}
\]

Here the first row records the value deviation from the unit-norm core block
and the first two parameter derivatives; the exact spectral identity gives
\(\|B_{u,s}\|=1\).  The last two rows were certified first on the
true-orbit tube \(|U|\le X_*=251/25000\), not silently on all of (2).
Because \(X_*>R_0\), cubicity and the third row extend the second derivative
to \(|U|\le2R_0\) by the explicit bounds

\[
 m_j^{\rm block}
 :=m_j+(2R_0-X_*)t_j
 \le m_j+R_0t_j,
 \qquad 0\le j\le2.
\tag{24a}
\]

Taylor's formula from \(G(0)=D_UG(0)=0\), now using (24a), bounds the value
and first state derivative on the entire block.  The map
\((u,s)\mapsto U\) has norm at most two in the
max-of-two-Euclidean-block norm.  Put
\(\widetilde B_0=1+B_0\) and \(\widetilde B_j=B_j\) for \(j=1,2\).
The checker reconstructs all twelve bounds

\[
 \begin{aligned}
 M_{0j}&=\widetilde B_jR_0
          +\tfrac12(2R_0)^2m_j^{\rm block},\\
 M_{1j}&=\widetilde B_j+4R_0m_j^{\rm block},\\
 M_{2j}&=4m_j^{\rm block},\qquad M_{3j}=8t_j,
 \end{aligned}
\tag{24b}
\]

Every entry is strictly below \(16\).  Thus

\[
 \|D_z^iD_\theta^jX_\theta(z)\|<K:=16,
 \qquad 0\le i\le3,\quad 0\le j\le2,\quad z\in\mathcal B,
\tag{25}
\]

and all fourth state derivatives vanish.

For the algebraic auxiliary embeddings
\(\widehat\iota=T_\mu^{-1}\iota\), the zero-energy checker first reconstructs
the complete \(C^3_\nu/C^2_\theta\) table.  Its largest entry is

\[
 \frac{801155179344240981745916425797632}{125}<2^{103}.
\tag{25a}
\]

Combining that table with the explicit trigonometric section formula,
\(\rho^{-1}<2^{24}\), and all Leibniz allocations gives a complete
\(4\)-by-\(3\) section-jet rectangle below \(2^{130}\).  The remaining source
map has exactly four typed layers:

\[
 s^{\rm out}\longmapsto
 \Theta_\mu(s^{\rm out})\longmapsto
 C_{{\rm AK},\mu}\Theta_\mu(s^{\rm out})\longmapsto
 \kappa_\mu^{-1/2}A_{\vartheta,\mu}
 C_{{\rm AK},\mu}\Theta_\mu(s^{\rm out}).
\tag{25b}
\]

The stable block has only the additional fixed orthogonal factor \(C_0\).
The exact completion identity proves that \(T_\mu^{-1}\) has already cancelled
in (25b); physical-frame jets of \(T_\mu\) are therefore not used as inverse
jets.  The checker reads the forward Moser majorant, the value and two
parameter jets of \(C_{\rm AK}\), and the value and two parameter jets of
\(\kappa^{-1/2},\cos\vartheta,\sin\vartheta\) from their authenticated
sources.  Product and Cauchy rules then give the uniform source bound

\[
 \|D_{(\psi,\nu)}^iD_\theta^j
       \widehat\iota^{\rm out}_\theta\|
 <S:=2^{4096},\qquad 0\le i\le3,\quad0\le j\le2.
\tag{26}
\]

Here is the finite count reconstructed by the checker.  Every typed source
object is below \(2^{130}\).  The four layers in (25b) give, successively, at
most \(3\), \(1+5\cdot3=16\), \(17\), and \(19\) factors in any colored
derivative term of total order at most five.  The product budget is therefore
\(19\cdot130=2470\).  The authenticated state and action gaps are
\(2^{-26}\) and \(25/2^{58}\); using strict power-of-two exponents and
\(5!<2^7\) gives the conservative Cauchy/factorial cost
\(3(27+54)+7=250\).  Finally, the four rules, \(B_5=52<2^6\), the four
components, and the colored allocations cost another \(42\) exponents.  Thus
the checker obtains

\[
 2470+250+42=2762<4096,
\tag{26a}
\]

which proves (26).  The external-parameter identity component in the
augmented initial map has norm one and is covered by the same bound.  The
incoming estimate follows by reversibility.

For completeness, the following power-of-two recurrence turns (25)--(26)
into a directly checkable full rectangle.  Replace variable terminal time by
the fixed unit-interval problem

\[
 \partial_sY(s)=tX_\theta(Y(s)),\qquad
 Y(0)=\widehat\iota_\theta(p),\qquad
 0\le s\le1,\qquad 0\le t<19.
\tag{26b}
\]

Treat the state, external-parameter, and \(t\) labels as colored labels,
never using more than three state or two external labels.  Differentiating
(26b) makes every allowed time partial an ordinary parameter partial of a
fixed-time ODE.  Up to total order five there are fewer than
\(B_5=52<2^6\) set partitions.  Since \(19K<304\) and
\(e^{19K}<4^{304}=2^{608}\), Gronwall and the colored Faà di Bruno formula
bound the fixed-time flow composed with the augmented source by \(2^{a_n}\),
where

\[
 a_1=4704,\qquad
 a_n=609+\max\{4096,\ 14+n(1+a_{n-1})\},\quad2\le n\le5.
\tag{27}
\]

Thus

\[
 (a_1,a_2,a_3,a_4,a_5)
 =(4704,10033,30725,123527,618263).
\tag{28}
\]

For
\(G(p,t)=g^u(\widehat\varphi^t
(\widehat\iota^{\rm out}(p)))\), the only nonzero state
derivatives of \(g^u\) have norms below \(2^{15}\).  Its derivatives are
therefore bounded by \(2^{b_n}\), with

\[
 b_n=21+n(1+a_n),\qquad
 (b_1,\ldots,b_5)=(4726,20089,92199,494133,3091341).
\tag{29}
\]

At the first hit, (16) gives \(|G_t|^{-1}<1\).  Differentiating
\(G(p,\tau(p))=0\) and isolating the unique top-order occurrence of
\(D^n\tau\) gives

\[
 \begin{aligned}
 c_1&=b_1,\\
 c_n&=16+\max_{1\le k\le n}b_k+n(1+c_{n-1}),
       \quad2\le n\le5,
 \end{aligned}
\tag{30}
\]

and hence

\[
 (c_1,\ldots,c_5)=(4726,29559,180895,1217733,9180027).
\tag{31}
\]

The zeroth-order entries are recorded separately:
\(\tau<19<2^5\), while the algebraic block bound and the terminal frame give
\(\|\iota^{\rm phys}\|<3/25<1\).  For positive derivative order, substituting
the time jet back into the algebraic flow first costs the exponent \(7\).
The authenticated terminal-frame table gives
\(\|D_\theta^jT_\theta\|<2^3\) for \(0\le j\le2\), and at most four parameter
Leibniz allocations add two more exponents.  Consequently the physical
endpoint exponents satisfy

\[
 d_n=12+a_n+n(1+c_n),
\tag{32}
\]

namely

\[
 (d_1,\ldots,d_5)
 =(9443,69165,573425,4994475,46518415).
\tag{33}
\]

The original-parameter conversion costs at most
\(25^2<2^{10}\).  Equations (31)--(33) therefore give, in particular, the
single explicit bounds

\[
 \begin{aligned}
 \|D_{(\psi,\nu)}^iD_\mu^j\tau^{\rm out/in}_\mu\|
 &<2^{9180037},\\
 \|D_{(\psi,\nu)}^iD_\mu^j
       \iota^{\rm out/in,phys}_\mu\|
 &<2^{46518425},
 \end{aligned}
\quad 0\le i\le3,\quad0\le j\le2.
\tag{34}
\]

This is the complete rectangular \(C^2_\mu(C^3_{\rm state})\) claim; in
particular it includes the total-order-five corner \((i,j)=(3,2)\).  The
large constants only certify finiteness uniformly on the frozen box.

## 6. Physical winding versus residence time

The weighted-passage atom supplies the auxiliary comparison

\[
 \left|n^{\rm K}-\frac{\beta_\mu}{2\pi}T^{\rm K}_\mu\right|<2,
 \qquad \beta_\mu<\frac34.
\tag{35}
\]

Use on the physical faces the integer marking transported through the two
slides.  Since

\[
 \mathcal T_{{\rm sf},\mu}
 =T^{\rm K}_\mu+\tau^{\rm in}_\mu+\tau^{\rm out}_\mu,
\tag{36}
\]

and \(2\pi>6\), equations (21), (35), and the triangle inequality give

\[
 \left|n^{\rm K}-\frac{\beta_\mu}{2\pi}
       \mathcal T_{{\rm sf},\mu}\right|
 <2+\frac{3/4}{6}\,38
 =\frac{27}{4}<7.
\tag{37}
\]

Thus (D12) holds with the frozen uniform choice

\[
 \boxed{C_{\rm phys}=7}.
\tag{38}
\]

## 7. Claim boundary

The proof-bound checker authenticates the P2a cone/face certificate, the
P2b rectangular-jet certificate, the P2bK direction and radial scale, the
P2d symplectic completion, and the preceding exact-sections, Moser, and
weighted-passage proof chain.  It then checks (7)--(11), (14), (18)--(19),
(24)--(34), and (37) by exact arithmetic.

A pass establishes local mathematical `PASS` for
`V2.CHART.PHYSICAL_SLIDES` and for the physical comparison (D12).  It does
not establish the finite overlap cocycle, the complete event atlas, any
positive-end result, temporal stability, Turing selection, or canard
identification.  `V2.CHART.OVERLAPS`, `V2.EXACT_CHART`, and every later
obligation remain open; the repository aggregate remains non-claim-bearing
at independent replay `1/2`.
