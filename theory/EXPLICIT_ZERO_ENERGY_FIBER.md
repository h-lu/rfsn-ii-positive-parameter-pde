# Explicit zero-energy fiber in the Kato action chart

**Proof contract:** `rfsn-vdp-p2d-explicit-zero-energy-fiber/1`

**Local conclusion:** this note, together with the authenticated P2d
symplectic-frame certificate and the proved analytic normal-form contract,
discharges `V2.CHART.ZERO_ENERGY`.  It does not construct the exact radial
sections, the weighted passage, the physical slides, the overlap atlas, or
the parent `V2.EXACT_CHART`.

## 1. Input and notation

Use the normalized parameter bridge

\[
 0\le r\le \frac2{25},\qquad |a_2|\le\frac14,\qquad
 \frac45\le\epsilon\le\frac65
\]

and the normalized parameters

\[
 \theta_r=25r-1,\qquad \theta_a=4a_2,\qquad
 \theta_\epsilon=5(\epsilon-1).
\]

The contract
`rfsn-vdp-p2d-explicit-global-moser-majorant/1` gives a resonant function
\(h_\mu\) whose series is controlled on the positive-Kato majorant domain

\[
 \mathcal D_\infty=\Delta_{\rho_\infty},\qquad
 \rho_\infty=\frac58\,2^{-22}=\frac5{2^{25}}.
\]

The exact conjugacy is asserted on the smaller source domain

\[
 \mathcal D_{\rm src}=\Delta_{\rho_{\rm src}},\qquad
 \rho_{\rm src}=\frac38\,2^{-22}=\frac3{2^{25}},
 \qquad
 \widehat H_\mu\circ\Phi_\mu^{\rm K}
 =h_\mu(I_1,I_2^{\rm K}),
 \quad dh_\mu(0)=(\alpha_\mu,\beta_\mu).
\]

The two radii must not be identified: \(\mathcal D_\infty\) supplies the
coefficient majorant, whereas \(\mathcal D_{\rm src}\) is the domain on which
an action root lifts back through the proved exact chart.

Put \(\nu=I_2^{\rm K}\), \(I=I_1\), and

\[
 h_\mu(I,\nu)=\alpha_\mu I+\beta_\mu\nu+N_\mu(I,\nu).
\tag{1}
\]

The resonant remainder satisfies

\[
 N_\mu(0,0)=0,\qquad dN_\mu(0,0)=0.
\tag{2}
\]

All parameter estimates below use the factorial-weighted normalized
parameter-two-jet norm of the normal-form contract.  Original-parameter
derivatives are obtained at the end from the exact factors \(25,4,5\).

## 2. From the state majorant to an action majorant

In the fixed complex convention,

\[
 J_1=\frac{I-i\nu}{2},\qquad J_2=\frac{I+i\nu}{2}.
\tag{3}
\]

Every resonant state monomial is an action monomial in \(J_1,J_2\), with
the same coefficient.  If \(|I|,|\nu|\le s:=\rho_\infty^2\), then
\(|J_1|,|J_2|\le s\).  Conversely, a point of the \(J\)-bidisc of radius
\(s\) can be represented by complex state coordinates of radius
\(\rho_\infty\), by choosing square roots separately in each canonical pair.
Thus the
coefficient majorant for the resonant state series transfers without a
dimension-dependent constant to the action series.

The normal-form bounds

\[
 \|J^2 Z_q\|_{R_{q-1}}^\#\le E\,\overline B^{q-1},
 \qquad E\le4,\qquad \overline B=2^{20},
\]

and \(\varepsilon_{\rm nf}=2^{-22}\) therefore give

\[
 \|J^2N\|_s^\#
 \le \sum_{q\ge1}E\varepsilon_{\rm nf}^{q+2}
                  \overline B^{q-1}
 \le \overline M:=\frac1{3\,2^{62}}.
\tag{4}
\]

This deliberately retains the harmless \(q=1\) envelope although the exact
audit proves that the cubic resonant block vanishes.

Set

\[
 s=\frac{25}{2^{50}},\qquad d=\frac{s}{2}.
\tag{5}
\]

Cauchy's estimate from the action bidisc of radius \(s\) to the bidisc of
radius \(d\) yields

\[
 L:=\sup |\partial_I N|\le\frac{\overline M}{s-d}
 =\frac1{153600},
 \qquad
 L_2:=\sup |\partial_I^2N|
 \le\frac{2\overline M}{(s-d)^2}.
\tag{6}
\]

The same bounds hold for every first normalized parameter derivative of
\(N\); every pure or mixed second parameter derivative is bounded by
\(2\overline M\) before state differentiation.  The factor two covers the
factorial weight of a pure second derivative in the jet norm.

## 3. A strict common Krawczyk enclosure

The authenticated frame hulls give the rational gates

\[
 \alpha_\mu\ge\frac7{10},\qquad
 |\beta_\mu|\le\frac{18}{25},
\tag{7}
\]

and every individual first or second normalized parameter derivative of
\(\alpha\) and \(\beta\) has absolute value at most \(1/100\).  In
particular, on the inner action bidisc,

\[
 |\partial_Ih_\mu|\ge\alpha_\mu-|\partial_IN_\mu|
 \ge\frac7{10}-L
 =\frac{107519}{153600}>\frac23=:a_*.
\tag{8}
\]

This is the complex nonvanishing estimate.  On the real slice,
\(\partial_Ih_\mu\) is real, and hence the same bounds give the oriented
inequality
\(\partial_Ih_\mu\ge7/10-L>2/3\).

Choose

\[
 \nu_{\rm out}=\frac{s}{8}=\frac{25}{2^{53}},\qquad
 \nu_* =\frac{s}{16}=\frac{25}{2^{54}},
\tag{9}
\]

and, for \(|\nu|\le\nu_{\rm out}\), set

\[
 c_\mu(\nu)=-\frac{\beta_\mu}{\alpha_\mu}\nu,\qquad
 W=\frac{2\overline M}{7/10}
 =\frac5{24211351596743786496}.
\tag{10}
\]

The disk \(X=c_\mu(\nu)+\overline B_W\) lies in \(|I|<d\), because

\[
 |c_\mu(\nu)|+W
 \le\frac{36}{35}\nu_{\rm out}+W<d.
\tag{11}
\]

Use the exact parameter-dependent preconditioner \(C_\mu=1/\alpha_\mu\).
In the centered coordinate \(w=I-c_\mu(\nu)\), the scalar Krawczyk image is
contained in

\[
 -\frac{N_\mu(c_\mu(\nu),\nu)}{\alpha_\mu}
 -\frac{\partial_IN_\mu(X,\nu)}{\alpha_\mu}\overline B_W.
\]

Its radius is at most

\[
 \frac{\overline M}{7/10}
 +\frac{L}{7/10}W
 =\frac W2+\frac{W}{107520}<W.
\tag{12}
\]

Thus the Krawczyk image is strictly inside \(\overline B_W\), uniformly in
the complete parameter bridge and on both signs of \(\nu\).  Equivalently,
the map

\[
 w\longmapsto-\alpha_\mu^{-1}
 N_\mu(c_\mu(\nu)+w,\nu)
\]

is a strict contraction of that disk.  It has a unique fixed point, and the
analytic implicit-function theorem gives one function \(I=q_\mu(\nu)\) that
is holomorphic in the complex variable \(\nu\) and \(C^2\) in the real
parameter \(\mu\), for \(|\nu|<\nu_{\rm out}\).  Reality of the normal form
gives a real branch on the real two-sided interval.  Equations (1)--(2) and
uniqueness give

\[
 q_\mu(0)=0,\qquad q_\mu'(0)=-\frac{\beta_\mu}{\alpha_\mu}.
\tag{13}
\]

Put \(Q_0=(36/35)\nu_{\rm out}+W\).  This root also lies in the domain of the
exact conjugacy.  Indeed, throughout the complete complex Krawczyk box,

\[
 \max(|J_1|,|J_2|)
 \le\frac{Q_0+\nu_{\rm out}}2
 =\frac{19475}{3\,2^{61}}
 <\frac9{2^{50}}=\rho_{\rm src}^2,
 \tag{14}
\]

where the ratio of the left side to \(\rho_{\rm src}^2\) is
\(19475/55296<1\).  Choosing square roots in the two canonical pairs lifts
every such action point strictly into \(\mathcal D_{\rm src}\).  Therefore the
root is a zero-energy fiber of \(\widehat H_\mu\circ\Phi_\mu^{\rm K}\), not
only a zero of a majorant-domain series.  The oriented real bound (8) holds
along the entire real fiber.

## 4. Explicit mixed jets and the all-finite-order rule

For compact formulas set

\[
 \begin{aligned}
 Q_0&=\frac{36}{35}\nu_{\rm out}+W,\\
 Q_1&=\frac{(Q_0+\nu_{\rm out})/100+\overline M}{a_*},\\
 Q_2&=\frac{(Q_0+\nu_{\rm out})/100+2\overline M
       +L_2Q_1^2+2(1/100+L)Q_1}{a_*}.
 \end{aligned}
\tag{15}
\]

Implicit differentiation of \(h(q(\nu),\nu)=0\) gives, for a normalized
parameter index \(i\),

\[
 h_Iq_i+h_i=0,
\]

and for a pair \(i,j\),

\[
 h_Iq_{ij}+h_{II}q_iq_j+h_{Ij}q_i+h_{Ii}q_j+h_{ij}=0.
\tag{16}
\]

Using (4), (6)--(8) in (16) proves, throughout the outer \(\nu\)-disk,

\[
 |q|\le Q_0,qquad |q_i|\le Q_1,qquad |q_{ij}|\le Q_2.
\tag{17}
\]

Let \(\Delta_\nu=\nu_{\rm out}-\nu_*=\nu_*\).  Cauchy's formula now gives
the required constructive generator: for every fixed \(m\ge0\), every
normalized parameter multi-index \(\gamma\) with \(|\gamma|=j\le2\), and
\(|\nu|\le\nu_*\),

\[
 \left|D_\theta^\gamma D_\nu^m q_\mu(\nu)\right|
 \le \frac{m!\,Q_j}{\Delta_\nu^m}.
\tag{18}
\]

In particular (18) explicitly supplies all mixed derivatives with
\(m\le3\).  For derivatives in \(\mu=(r,a_2,\epsilon)\), multiply the
right-hand side by

\[
 25^{\gamma_r}4^{\gamma_a}5^{\gamma_\epsilon}.
\tag{19}
\]

Equations (9), (15), (18), and (19) are a machine-usable rule for every
fixed finite \(\nu\)-derivative order; no finite list is substituted for the
analytic quantifier.

## 5. Claim boundary

The argument proves only the nonlinear zero-energy fiber of the already
validated analytic normal form.  It establishes a local mathematical
`PASS` for `V2.CHART.ZERO_ENERGY`, with `claim_bearing=false` until the
repository's independent replay policy is satisfied.  The exact sections,
weighted passage, physical slides, overlaps, event atlas, all later
positive-end obligations, temporal stability, Turing selection, and canard
identification are not consequences of this note.
