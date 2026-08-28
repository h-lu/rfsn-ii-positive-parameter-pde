# Explicit global Moser majorant for the van der Pol saddle

**Evidence status: LOCAL-AMENDMENT / Proposed.**  This note proposes a
computable candidate sufficient criterion for the obligation
`V2.CHART.ANALYTIC_NORMAL_FORM`.  It does not assert that the interval gates
below have rigorously passed.  The obligation remains open until the analytic
lemmas and recurrences stated below are proved in this repository **and** a
source-bound rigorous certificate verifies every stated input and
domain-containment inequality on the complete continuation bridge.

The abstract input is Lemmas 2.4--2.6 and Proposition 2.7 in the frozen
flagship manuscript

```text
/home/hblu/Documents/Codex/2026-08-22/reversible-rfsn-ii-waves
commit d54add098545063d5efe8f1d6f062d4cfc116a0d
papers/paper-a/manuscript/main.tex
```

That repository is a read-only source.  The frozen parameter-majorant lemma
proves convergence after an unspecified state shrink and leaves its constants
implicit.  The purpose of the present local amendment is to make one
van-der-Pol-specific shrink, all majorant constants, the inverse domain, and
the exact primitive gauge explicit.  The additional estimates needed for that
purpose must be proved and validated in this repository.

## 1. Global Kato input and the single complex convention

Use the physical state order \((U,P,V,Q)\), the fixed physical primitive

\[
 \lambda=P\,dU-Q\,dV,
\]

and the Kato coordinates \((x_1,x_2,y_1,y_2)\) constructed in the P2d
symplectic-frame certificate.  Thus

\[
 \omega_0=dy_1\wedge dx_1+dy_2\wedge dx_2,
 \qquad
 \lambda_0=\frac12\sum_{j=1}^2(y_j\,dx_j-x_j\,dy_j),
\]

\[
 \mathcal R_0(x,y)=(C_0y,C_0x),
 \qquad C_0=\operatorname{diag}(1,-1),
\]

and the certified linear map \(L_\mu=(X_\mu,Y_\mu)\) satisfies

\[
 L_\mu^*d\lambda=d\lambda_0,
 \qquad
 \mathcal R L_\mu=L_\mu\mathcal R_0,
 \qquad
 \widehat H_{\mu,2}\circ L_\mu
   =\alpha_\mu I_1+\beta_\mu I_2^{\rm K},
\]

where

\[
 I_1=x_1y_1+x_2y_2,
 \qquad
 I_2^{\rm K}=x_2y_1-x_1y_2.
\tag{1}
\]

There is no nonlinear Darboux correction at this stage: the central van der
Pol symplectic form is constant and \(L_\mu\) is already exactly symplectic.
This is the model-specific simplification of frozen Lemma 2.4.

Fix, once on the whole bridge, the complex coordinates used by the P2d
exact-algebra audit:

\[
 \begin{aligned}
 z_1&=\frac{x_1-i x_2}{\sqrt2},&
 z_2&=\frac{x_1+i x_2}{\sqrt2},\\
 w_1&=\frac{y_1+i y_2}{\sqrt2},&
 w_2&=\frac{y_1-i y_2}{\sqrt2}.
 \end{aligned}
\tag{2}
\]

Then

\[
 \omega_0=dw_1\wedge dz_1+dw_2\wedge dz_2,
 \qquad
 \lambda_0=\frac12\sum_{j=1}^2(w_j\,dz_j-z_j\,dw_j).
\]

The reverser is

\[
 \mathcal R_0(z_1,z_2,w_1,w_2)=(w_1,w_2,z_1,z_2),
\]

and the real locus is \(z_2=\overline z_1\),
\(w_2=\overline w_1\).  Equivalently, the associated Poisson bracket has
\(\{z_j,w_k\}=-\delta_{jk}\).  Most importantly, this convention has the
same action sign as (1):

\[
 J_1=z_1w_1=\frac{I_1-iI_2^{\rm K}}2,
 \qquad
 J_2=z_2w_2=\frac{I_1+iI_2^{\rm K}}2.
\tag{3}
\]

Consequently

\[
 F_{2,\mu}=\lambda_{1,\mu}J_1+\lambda_{2,\mu}J_2,
 \qquad
 \lambda_{1,\mu}=\alpha_\mu+i\beta_\mu,
 \quad
 \lambda_{2,\mu}=\alpha_\mu-i\beta_\mu,
\tag{4}
\]

is exactly \(\alpha_\mu I_1+\beta_\mu I_2^{\rm K}\).  No later action
relabelling is allowed.

Write the first row of \(Y_\mu\) as \((a_\mu,b_\mu)\).  Since
\(X_\mu=\mathcal RY_\mu C_0\), the physical coordinate \(U\) becomes

\[
 U=a_\mu(x_1+y_1)+b_\mu(-x_2+y_2)
   =u_{-,\mu}(z_1+w_1)+u_{+,\mu}(z_2+w_2),
\tag{5}
\]

where

\[
 u_{-,\mu}=\frac{a_\mu-i b_\mu}{\sqrt2},
 \qquad
 u_{+,\mu}=\frac{a_\mu+i b_\mu}{\sqrt2}.
\]

Let \(S\) denote the fixed complex change (2).  To keep real and complex
coordinate types explicit, define

\[
 K_\mu^{\mathbb R}:=\widehat H_\mu\circ L_\mu,
 \qquad
 K_\mu^{\mathbb C}:=K_\mu^{\mathbb R}\circ S^{-1}.
\]

The complete complex-coordinate Hamiltonian is the degree-four polynomial

\[
 K_\mu^{\mathbb C}
 =F_{2,\mu}-\frac{A_\mu}{3}U^3+D_\mu U^4,
\tag{6}
\]

with

\[
 A_\mu=1+\sqrt\epsilon\,r^3a_2,
 \qquad
 D_\mu=\frac{\sqrt\epsilon\,r^2}{12}.
\tag{7}
\]

Equations (2)--(7), including the positive square-root branches, are one
global formula on the connected bridge

\[
 0\le r\le\frac2{25},
 \qquad |a_2|\le\frac14,
 \qquad \frac45\le\epsilon\le\frac65.
\tag{8}
\]

## 2. Coefficient and parameter-two-jet norms

Use the normalized parameters

\[
 \theta_r=25r-1,
 \qquad \theta_a=4a_2,
 \qquad \theta_\epsilon=5(\epsilon-1),
\tag{9}
\]

whose bridge is \([-1,1]^3\).  For

\[
 G=\sum_{p,q\in\mathbb N^2}G_{pq}z^pw^q
\]

and a scalar radius \(R>0\), put

\[
 \|G\|_R^\#
 =\sum_{p,q}|G_{pq}|R^{|p|+|q|}.
\tag{10}
\]

The unscaled reference polydisc is \(\Delta_1\subset\mathbb C^4\); hence
the \(\Lambda\) in the Giorgilli estimate equals one.  The fixed-parameter
source is Antonio Giorgilli, *Unstable equilibria of Hamiltonian systems*,
Discrete and Continuous Dynamical Systems **7** (2001), 855--871,
[doi:10.3934/dcds.2001.7.855](https://doi.org/10.3934/dcds.2001.7.855).

For a coefficient \(c(\theta)\), define its normalized parameter-two-jet
majorant by

\[
 \begin{aligned}
 |J^2c|
 :={}&|c|+\sum_{i=1}^3|\partial_i c|
 +\frac12\sum_{i=1}^3|\partial_{ii}c|
 +\sum_{1\le i<j\le3}|\partial_{ij}c|.
 \end{aligned}
\tag{11}
\]

For a polynomial or convergent series, replace \(|G_{pq}|\) in (10) by
\(|J^2G_{pq}|\).  Formula (11) is the coefficient norm of the truncated
Taylor jet with multi-index factorials.  The Leibniz rule therefore makes
it submultiplicative.  All interval evaluations must enclose the individual
value, three first derivatives, and six symmetric second derivatives before
forming (11).  Original-parameter bounds are obtained only afterwards, by
the exact first-derivative factors \((25,4,5)\) and their pairwise products
for second derivatives.

For \(k=(k_1,k_2)\ne0\), define

\[
 \Delta_{k,\mu}=k_1\lambda_{1,\mu}+k_2\lambda_{2,\mu}
 =\alpha_\mu(k_1+k_2)+i\beta_\mu(k_1-k_2).
\tag{12}
\]

Let \(m\) be a certified lower bound for
\(\min(\alpha_\mu,\beta_\mu)\).  On every parameter cell let

\[
 M_i\ge |\partial_i\alpha|+|\partial_i\beta|,
 \qquad
 N_{ij}\ge |\partial_{ij}\alpha|+|\partial_{ij}\beta|.
\tag{13}
\]

The identity

\[
 |\Delta_k|^2
 =\alpha^2(k_1+k_2)^2+\beta^2(k_1-k_2)^2
\]

and the two-dimensional norm inequality give

\[
 |\Delta_k|\ge m|k|_1.
\tag{14}
\]

Moreover,

\[
 \partial_i\Delta_k^{-1}
 =-\frac{\partial_i\Delta_k}{\Delta_k^2},
\tag{15}
\]

\[
 \partial_{ij}\Delta_k^{-1}
 =2\frac{(\partial_i\Delta_k)(\partial_j\Delta_k)}{\Delta_k^3}
  -\frac{\partial_{ij}\Delta_k}{\Delta_k^2}.
\tag{16}
\]

Thus the parameter-jet norm of every inverse divisor is bounded by
\(\kappa_J/|k|_1\), where

\[
 \begin{aligned}
 \kappa_J={}&\frac1m+\sum_i\frac{M_i}{m^2}\\
 &+\frac12\sum_i
   \left(\frac{2M_i^2}{m^3}+\frac{N_{ii}}{m^2}\right)
 +\sum_{i<j}
   \left(\frac{2M_iM_j}{m^3}+\frac{N_{ij}}{m^2}\right).
 \end{aligned}
\tag{17}
\]

The future source-bound checker must establish, on every cell of a gap-free
exact-rational cover of (8), the three proposed input gates

\[
 E\le4,
 \qquad h_{\rm in}\le\frac1{64},
 \qquad \kappa_J\le\frac53,
\tag{18}
\]

where

\[
 \left\|J^2\!\left(\frac{A_\mu U^3}{3}\right)\right\|_1^\#\le E,
 \qquad
 \|J^2(D_\mu U^4)\|_1^\#\le h_{\rm in}E.
\tag{19}
\]

The numerical values in (18) are candidate rational gates, not results of
this note.  The design-only scout evaluates them from authenticated archived
inputs but does not establish them as rigorous theorem gates.  Failure of any
one of them in the future source-bound checker requires a new versioned
contract or sharper interval evaluation; it must not be hidden by shrinking
the already frozen parameter bridge.

## 3. Fixed normalized Lie recursion

For

\[
 \{F,G\}=\sum_{j=1}^2
 \left(\partial_{w_j}F\,\partial_{z_j}G
       -\partial_{z_j}F\,\partial_{w_j}G\right),
\tag{20}
\]

put \(\operatorname{ad}_\chi F=\{F,\chi\}\).  On a monomial
\(z^pw^q\),

\[
 \{F_2,z^pw^q\}=\Delta_{p-q}z^pw^q.
\tag{21}
\]

Let \(\Pi\) be the fixed projection onto monomials with \(p=q\).  Write
the homogeneous excess-degree blocks as

\[
 P_0^{(0)}=F_2,
 \qquad P_1^{(0)}=-\frac{A_\mu U^3}{3},
 \qquad P_2^{(0)}=D_\mu U^4,
 \qquad P_s^{(0)}=0\quad(s\ge3).
\]

At normalization step \(q\ge1\), set

\[
 Z_q=\Pi P_q^{(q-1)},
 \qquad \Pi\chi_q=0,
\tag{22}
\]

and, for \(p-q'\ne0\),

\[
 (\chi_q)_{p q'}
 =-\frac{(P_q^{(q-1)})_{p q'}}
         {\Delta_{p-q'}}.
\tag{23}
\]

This sign is fixed by (20)--(21):
\(P_q^{(q-1)}+\operatorname{ad}_{\chi_q}F_2=Z_q\).
The exact homogeneous recursion is

\[
 P_s^{(q)}
 =\sum_{j=0}^{\lfloor s/q\rfloor}
   \frac1{j!}\operatorname{ad}_{\chi_q}^{\,j}
          P_{s-jq}^{(q-1)}.
\tag{24}
\]

For \(s=q\), (24) is precisely (22)--(23).  The finite-prefix part of the
present atom requires only the exact steps \(q=1,2\), sufficient to audit the
input cubic and quartic normalization and its sign convention.  It must implement
(22)--(24), not replace \(P_q^{(q-1)}\) by the original Taylor block.
Computing through \(N=12\) may later sharpen the zero-energy calculation,
but it is not a condition for the present atom.  Convergence from \(q=1\)
onward would be supplied only after the infinite majorant below is proved; it
cannot be replaced by any finite cutoff.

The projection, division rule, and order of the Lie maps are global and
fixed.  They also give exact induction rules

\[
 \chi_q\circ\mathcal R_0=-\chi_q,
 \qquad Z_q\circ\mathcal R_0=Z_q,
\tag{25}
\]

and preserve the real structure in (2).  These symmetry statements are
algebraic checks; small interval residuals are not substitutes for them.

## 4. Explicit Giorgilli constants and the infinite tail

Use the rational cumulative radius loss

\[
 d_q=\frac{3}{8q(q+1)},
 \qquad
 \delta_q=\sum_{j=1}^q d_j=\frac{3q}{8(q+1)},
 \qquad
 R_q=1-\delta_q=\frac{5q+8}{8(q+1)}.
\tag{26}
\]

Thus \(R_0=1\), \(R_\infty=5/8\), and

\[
 d_q\ge\frac{b_0}{q^2},
 \qquad b_0=\frac3{16}.
\tag{27}
\]

The local proof obligation is to repeat the source estimate and verify that it
uses only the lower gap bound (27) together with the total radius shrink.  Under
that still-to-be-discharged verification, the proposed schedule gives

\[
 T_{r,s}\le\left(\frac{16}{b_0^2}\right)^{s-1}.
\tag{28}
\]

The corresponding proposed Catalan bound is

\[
 \mu_{q,q}\le8^{q-1}.
\tag{29}
\]

To use (28)--(29) for parameter jets, their proof must be repeated in the
normed truncated-jet algebra (11).  Equations (15)--(17) retain the required
\(|k|_1^{-1}\) gain, and the first- and second-parameter bracket recursions
are the exact Leibniz identities.  This parameter-jet extension is a new
proof obligation in this repository; it is not a numerical corollary of the
frozen fixed-parameter theorem.

Using the rational estimate \(4e^2<30\), define

\[
 C_*=h_{\rm in}+30E\kappa_J,
 \qquad
 B_*:=\frac{128}{b_0^2}C_*=\frac{32768}{9}C_*,
 \qquad
 G_*:=E\kappa_J.
\tag{30}
\]

If (18) holds, then

\[
 C_*\le\frac{12801}{64},
 \qquad
 B_*\le\frac{6554112}{9}<2^{20},
 \qquad
 G_*\le\frac{20}{3}<8.
\tag{31}
\]

Set the simple certificate envelopes

\[
 \overline B=2^{20},
 \qquad \overline G=8.
\tag{32}
\]

Because the present problem has exactly two degrees of freedom, every
monomial belongs to Giorgilli's \(\mathcal P^\sharp\); the
\(\mathcal P^\natural\) and \(\mathcal P^\flat\) sectors are absent.  Once the
preceding Banach-algebra recurrence has been proved, the target estimates
corresponding to equations (35), (37), and (39) of that proof are

\[
 \|J^2\chi_q\|_{R_{q-1}}^\#
 \le \overline G\,\overline B^{q-1},
 \qquad
 \|J^2Z_q\|_{R_{q-1}}^\#
 \le E\,\overline B^{q-1},
\tag{33}
\]

and, for \(s>q\),

\[
 \|J^2P_s^{(q)}\|_{R_q}^\#
 \le E\,\overline B^{s-1}.
\tag{34}
\]

Under that proof, no factor \(d_q^{-1}\) is needed in (33)--(34).  Keeping
that factor would be a valid but unnecessarily weaker generic estimate.

## 5. Frozen state shrink and domain-containment gates

Throughout this section, assume conditionally that the proposed bounds
(33)--(34) have first been proved in the parameter-two-jet algebra.  The
following calculations then reduce the analytic-flow and domain parts of the
future certificate to explicit rational inequalities.

Freeze

\[
 \varepsilon_{\rm nf}=2^{-22},
 \qquad
 \vartheta=\overline B\varepsilon_{\rm nf}=\frac14,
 \qquad
 \mathcal D_q=\Delta_{\varepsilon_{\rm nf}R_q},
 \qquad
 \mathcal D_\infty=\Delta_{5\varepsilon_{\rm nf}/8}.
\tag{35}
\]

Let \(T_q=\Phi_{\chi_q}^1\) be the time-one Hamiltonian map.  Homogeneity
and (33) give the componentwise vector-field bound

\[
 \widehat v_q:=
 \frac{(q+2)\overline G\varepsilon_{\rm nf}^2
       \vartheta^{q-1}}{R_{q-1}}.
\tag{36}
\]

As long as an orbit remains in \(\mathcal D_{q-1}\), its displacement in
unit time is at most \(\widehat v_q\).  The strict gate below and a
first-exit argument therefore prove both existence of the time-one map on
\(\mathcal D_q\) and
\(\sup_{\mathcal D_q}|T_q-\operatorname{id}|\le\widehat v_q\).  Applying
the same argument to \(-X_{\chi_q}\) gives

\[
 T_q^{\pm1}(\mathcal D_q)\subset\mathcal D_{q-1},
 \qquad
 \sup_{\mathcal D_q}|T_q^{\pm1}-\operatorname{id}|
 \le\widehat v_q.
\tag{36a}
\]

The first all-orders domain gate is

\[
 \widehat v_q<\varepsilon_{\rm nf}d_q
 \qquad(q\ge1).
\tag{37}
\]

It follows from one rational inequality.  Indeed,

\[
 \max_{q\ge1}q(q+1)(q+2)4^{1-q}=6,
\]

so (37) follows from

\[
 \frac{128}{5}\overline G\varepsilon_{\rm nf}<1.
\tag{38}
\]

The raw all-orders displacement sum is

\[
 \begin{aligned}
 S_0:=\sum_{q\ge1}\widehat v_q
 &\le\frac{8\overline G}{5}\varepsilon_{\rm nf}^2
       \frac{3-2\vartheta}{(1-\vartheta)^2}\\
 &\le\frac{512}{9}\varepsilon_{\rm nf}^2
 <\frac{\varepsilon_{\rm nf}}8.
 \end{aligned}
\tag{39}
\]

All quantities in (38)--(39) are exact rationals.  The sum \(S_0\) directly
controls successive negative-flow displacements in the inverse order below.
It does **not** by itself control the Cauchy differences of the forward
composition, because a new \(T_q\) is inserted on the right and its
displacement is propagated through all earlier maps.

To control that propagation, homogeneity and (33) give, on the outer domain
\(\mathcal D_{q-1}\),

\[
 \sup_{\mathcal D_{q-1}}\|D_zX_{\chi_q}\|_{\infty\to\infty}
 \le b_q:=
 \frac{(q+2)(q+1)\overline G\varepsilon_{\rm nf}
       \vartheta^{q-1}}{R_{q-1}^2}.
\tag{39a}
\]

Since \(R_{q-1}\ge5/8\), the exact generating-function identity

\[
 \sum_{q\ge1}(q+2)(q+1)t^{q-1}
 =\frac{2(t^2-3t+3)}{(1-t)^3}
\]

gives

\[
 \begin{aligned}
 B_z:=\sum_{q\ge1}b_q
 &\le \frac{64}{25}\overline G\varepsilon_{\rm nf}
       \frac{2(\vartheta^2-3\vartheta+3)}
            {(1-\vartheta)^3}\\
 &=\frac{37}{691200}
 <\frac1{16384}.
 \end{aligned}
\tag{39b}
\]

The last strict inequality is the second exact all-orders gate.  Gronwall's
inequality and \(-\log(1-x)\ge x\) for \(0\le x<1\) now yield

\[
 \operatorname{Lip}(T_q^{\pm1})\le e^{b_q},
 \qquad
 \prod_{q\ge1}\operatorname{Lip}(T_q^{\pm1})
 \le e^{B_z}
 \le\frac1{1-B_z}=:A_z
 <\frac{16384}{16383}.
\tag{39c}
\]

The domain gate (37) first shows that

\[
 \Theta_N=T_1\circ T_2\circ\cdots\circ T_N
\tag{40}
\]

is defined on \(\mathcal D_N\): the maps are applied from right to left,
and \(T_q(\mathcal D_q)\subset\mathcal D_{q-1}\).  For
\(z\in\mathcal D_\infty\), both \(z\) and \(T_N(z)\) lie in
\(\mathcal D_{N-1}\), and (39c) gives the missing forward Cauchy estimate

\[
 \begin{aligned}
 |\Theta_N(z)-\Theta_{N-1}(z)|
 &=|\Theta_{N-1}(T_N(z))-\Theta_{N-1}(z)|\\
 &\le A_z\widehat v_N.
 \end{aligned}
\tag{40a}
\]

Consequently \(\Theta_N\) converges uniformly on
\(\mathcal D_\infty\), and its total forward displacement is bounded by

\[
 \sup_{\mathcal D_\infty}|\Theta-\operatorname{id}|
 \le A_zS_0
 <\frac{16384}{16383}\frac{512}{9}\varepsilon_{\rm nf}^2
 =\frac{2}{147447}\varepsilon_{\rm nf}
 <\frac{\varepsilon_{\rm nf}}8.
\tag{40b}
\]

The inverse sequence

\[
 \Psi_N:=\Theta_N^{-1}
 =T_N^{-1}\circ\cdots\circ T_2^{-1}\circ T_1^{-1}
\tag{41}
\]

is defined and uniformly Cauchy on the common target polydisc

\[
 \mathcal D_{\rm inv}=\Delta_{\varepsilon_{\rm nf}/2}.
\tag{42}
\]

Indeed, after the first \(q-1\) negative flows, every point that starts in
\(\mathcal D_{\rm inv}\) has radius at most

\[
 \frac{\varepsilon_{\rm nf}}2+
 \sum_{j<q}\widehat v_j
 <\frac{5\varepsilon_{\rm nf}}8
 <\varepsilon_{\rm nf}R_q.
\]

Thus (37) protects the next negative-time step and

\[
 \sup_{\mathcal D_{\rm inv}}|\Psi_N-\Psi_{N-1}|
 \le\widehat v_N.
\tag{42a}
\]

Here the raw sum \(S_0\) is valid because the new negative-flow map is
inserted on the left and is evaluated directly at the preceding image.  The
limit \(\Psi\) maps \(\mathcal D_{\rm inv}\) into
\(\mathcal D_\infty\).  The finite identities, uniform convergence, and the
common Lipschitz bound (39c) give

\[
 \Theta\circ\Psi=\operatorname{id}
 \quad\hbox{on }\mathcal D_{\rm inv}.
\tag{42b}
\]

Moreover, (40b) maps
\(\mathcal D_{\rm src}:=\Delta_{3\varepsilon_{\rm nf}/8}\) into
\(\mathcal D_{\rm inv}\).  Passing to the limit in
\(\Psi_N\circ\Theta_N=\operatorname{id}\), again using (39c), gives

\[
 \Psi\circ\Theta=\operatorname{id}
 \quad\hbox{on }\mathcal D_{\rm src}.
\tag{42c}
\]

This constructs a two-sided analytic inverse on explicit domains; it does
not infer invertibility from a sampled determinant.

Recall that \(S:(x_1,x_2,y_1,y_2)\mapsto(z_1,z_2,w_1,w_2)\) is the fixed
unitary complex change (2).  The domains \(\mathcal D_q\),
\(\mathcal D_{\rm inv}\), and \(\mathcal D_{\rm src}\) in this section are
complex \((z,w)\)-polydiscs.  Write

\[
 \Theta^{\mathbb R}:=S^{-1}\circ\Theta\circ S,
 \qquad
 \Psi^{\mathbb R}:=S^{-1}\circ\Psi\circ S
\tag{42d}
\]

for their real Kato-coordinate representatives.

The P2d frame gate
\(\|L_\mu-L_0\|_{\rm F}<1/8\), with \(L_0\) orthogonal, gives

\[
 \|L_\mu^{-1}\|_2<\frac87.
\tag{43}
\]

Hence the common physical complex polydisc

\[
 \mathcal D_{\rm phys}=\Delta_{\varepsilon_{\rm nf}/8}
\tag{44}
\]

is mapped by \(S\circ L_\mu^{-1}\) into \(\mathcal D_{\rm inv}\): if the
four physical components are bounded by \(\varepsilon_{\rm nf}/8\), then
their Euclidean norm is at most \(\varepsilon_{\rm nf}/4\), and (43) bounds
the Euclidean norm after \(L_\mu^{-1}\) by
\(2\varepsilon_{\rm nf}/7\).  The unitary map \(S\) does not change this
two-norm, so the resulting complex point has every component bounded by
less than \(\varepsilon_{\rm nf}/2\).  Equation (42b) therefore gives the
inverse candidate \(\Psi_\mu^{\mathbb R}\circ L_\mu^{-1}\).  In fact its
complex-coordinate value lies in \(\mathcal D_{\rm src}\), because (39)
gives

\[
 \frac{2\varepsilon_{\rm nf}}7+S_0
 <\frac{3\varepsilon_{\rm nf}}8.
\tag{44a}
\]

Consequently every point of \(\mathcal D_{\rm phys}\) lies in
\(L_\mu\circ\Theta_\mu^{\mathbb R}(S^{-1}\mathcal D_{\rm src})\), with
inverse \(\Psi_\mu^{\mathbb R}\circ L_\mu^{-1}\).

For a finite prefix ending at \(N\), the two useful tail bounds are

\[
 \left\|J^2\sum_{q>N}Z_q\right\|_{\mathcal D_\infty}^\#
 \le
 E\varepsilon_{\rm nf}^3
 \frac{\vartheta^N}{1-\vartheta},
\tag{45}
\]

and

\[
 \left\|J^2\sum_{s>N}P_s^{(N)}\right\|_{\mathcal D_N}^\#
 \le
 E\varepsilon_{\rm nf}^3
 \frac{\vartheta^N}{1-\vartheta}.
\tag{46}
\]

The raw tail of the single-flow displacement bounds is

\[
 \sum_{q>N}\widehat v_q
 \le\frac{8\overline G}{5}\varepsilon_{\rm nf}^2
 \frac{\vartheta^N
       \bigl((N+3)-(N+2)\vartheta\bigr)}
      {(1-\vartheta)^2}.
\tag{47}
\]

It directly bounds the inverse tail.  The forward tail carries the
Lipschitz amplification:

\[
 \sup_{\mathcal D_\infty}|\Theta-\Theta_N|
 \le A_z\frac{8\overline G}{5}\varepsilon_{\rm nf}^2
 \frac{\vartheta^N
       \bigl((N+3)-(N+2)\vartheta\bigr)}
      {(1-\vartheta)^2}.
\tag{47a}
\]

Thus (45)--(47a) are machine-readable infinite-tail estimates, rather than
a claim that a finite-order truncation is exact.

## 6. Parameter-\(C^2\) maps and inverse maps

The jet majorant in (33) already controls the parameter derivatives of the
generators.  The certificate must additionally propagate those derivatives
through every time-one map and through the infinite composition.

For a generator of degree \(n=q+2\), evaluated on the outer domain
\(\mathcal D_{q-1}\), obtain outward bounds

\[
 \begin{array}{lll}
 a_0\ge\|X_{\chi_q}\|,&
 a_1\ge\|D_\theta X_{\chi_q}\|,&
 a_2\ge\|D_\theta^2X_{\chi_q}\|,\\
 \ell_0\ge\|D_zX_{\chi_q}\|,&
 \ell_1\ge\|D_zD_\theta X_{\chi_q}\|,&
 c_0\ge\|D_z^2X_{\chi_q}\|.
 \end{array}
\tag{48}
\]

Here state vectors use the componentwise \(\ell^\infty\) norm, state
derivatives use its induced multilinear operator norms, and normalized
parameter directions also use \(\ell^\infty\).  Parameter Hessians are bounded
by the full ordered bilinear majorant; this is twice the second-derivative
contribution in the factorial-weighted jet norm (11).

They are computed from the corresponding coefficient-jet norms by the
homogeneous factors

\[
 \frac{n}{\varepsilon_{\rm nf}R_{q-1}},
 \qquad
 \frac{n(n-1)}{(\varepsilon_{\rm nf}R_{q-1})^2},
 \qquad
 \frac{n(n-1)(n-2)}
      {(\varepsilon_{\rm nf}R_{q-1})^3}.
\tag{49}
\]

For use with the combined norm (11), one may take the universal envelopes
\(a_0,a_1\le\widehat v_q\), \(a_2\le2\widehat v_q\), with the analogous first- and
second-state factors from (49).  Componentwise interval jets may be sharper.
The explicit choice \(\ell_0=b_q\) from (39a) is admissible.

On \(0\le t\le1\), the following scalar comparison system gives an
executable enclosure of the required variational equations:

\[
 \begin{aligned}
 \dot s&=\ell_0s,&s(0)&=1,\\
 \dot p&=\ell_0p+a_1,&p(0)&=0,\\
 \dot h&=\ell_0h+c_0s^2,&h(0)&=0,\\
 \dot m&=\ell_0m+(c_0p+\ell_1)s,&m(0)&=0,\\
 \dot q_2&=\ell_0q_2+a_2+2\ell_1p+c_0p^2,&q_2(0)&=0.
 \end{aligned}
\tag{50}
\]

At \(t=1\), \(s,p,h,m,q_2\) bound, respectively,
\(D_zT_q\), \(D_\theta T_q\), \(D_z^2T_q\),
\(D_zD_\theta T_q\), and \(D_\theta^2T_q\).  The negative-time map has
the same absolute majorants.  The finite compositions (40)--(41) are
updated with the exact chain rules; in particular,

\[
 \begin{aligned}
 D_z^2(F\circ G)
 &=(D_z^2F\circ G)[D_zG,D_zG]
   +(D_zF\circ G)D_z^2G,\\
 D_zD_\theta(F\circ G)
 &=(D_zD_\theta F\circ G)D_zG
   +(D_z^2F\circ G)[D_zG,D_\theta G]\\
 &\quad +(D_zF\circ G)D_zD_\theta G,\\
 D_\theta(F\circ G)
 &=D_\theta F\circ G+(D_zF\circ G)D_\theta G,\\
 D_\theta^2(F\circ G)[u,v]
 &=(D_\theta^2F\circ G)[u,v]
   +(D_zD_\theta F\circ G)[D_\theta G[u],v]\\
 &\quad +(D_zD_\theta F\circ G)[D_\theta G[v],u]
   +(D_z^2F\circ G)[D_\theta G[u],D_\theta G[v]]\\
 &\quad +(D_zF\circ G)D_\theta^2G[u,v].
 \end{aligned}
\tag{51}
\]

In (51), every derivative of \(F\) is evaluated at
\((G(z,\theta),\theta)\), and \(u,v\) are arbitrary normalized parameter
directions.  Thus the last identity is the full bilinear Hessian chain rule,
not only its repeated-direction specialization.

The five comparison quantities \(s,p,h,m,q_2\) all enter the finite
composition recurrences.  Their increments are bounded by a polynomial in
\(q\) times \(\vartheta^{q-1}\), so the corresponding tails are summable
rational geometric tails.  The certificate must record both the
finite-prefix accumulation and analytic tail bounds for all five
quantities.  Coefficient-jet convergence alone is not sufficient evidence
for parameter-\(C^2\) convergence of the chart and inverse.

## 7. Exact primitive gauge

For a homogeneous generator \(\chi_q\) of degree \(q+2\), Euler's identity
and the convention \(\iota_{X_{\chi_q}}d\lambda_0=d\chi_q\) give

\[
 \lambda_0(X_{\chi_q})=-\frac{q+2}{2}\chi_q.
\tag{52}
\]

Cartan's formula and conservation of \(\chi_q\) along its own Hamiltonian
flow therefore give the exact, not approximate, identity

\[
 T_q^*\lambda_0-\lambda_0=da_q,
 \qquad
 a_q=-\frac q2\chi_q.
\tag{53}
\]

For (40), define

\[
 \mathcal A_0=0,
 \qquad
 \mathcal A_q=\mathcal A_{q-1}\circ T_q-\frac q2\chi_q.
\tag{54}
\]

Then

\[
 \Theta_q^*\lambda_0-\lambda_0=d\mathcal A_q.
\]

Once the outstanding map, parameter-jet, and primitive-tail recurrences are
proved, they also prove convergence of \(\mathcal A_q\) on the fixed
\(\mathcal D_{\rm src}\) (and on any other certified polydisc compactly
contained in \(\mathcal D_\infty\)).  Its
normalization and reverser parity are fixed:

\[
 \mathcal A_\mu(0)=0,
 \qquad
 \mathcal A_\mu\circ\mathcal R_0=-\mathcal A_\mu.
\tag{55}
\]

To return to the fixed physical primitive, set

\[
 g_{\rm phys}(U,P,V,Q)=\frac{UP-VQ}{2}.
\tag{56}
\]

The exact physical gauge identity already audited in P2d is

\[
 \lambda=\lambda_{\rm sym}+dg_{\rm phys},
 \qquad L_\mu^*\lambda_{\rm sym}=\lambda_0.
\]

The Lie maps and \(\mathcal A_\mu\) above are written in the complex
coordinates (2).  For the type-correct real chart, use (42d) and put
\(\mathcal A_\mu^{\mathbb R}:=\mathcal A_\mu\circ S\).  Thus the notation
\(L_\mu\circ\Theta_\mu\) used informally means
\(L_\mu\circ\Theta_\mu^{\mathbb R}\), not the composition of \(L_\mu\)
directly with a complex-coordinate map.

Thus the final Kato-tangent chart

\[
 \Phi_\mu^{\rm K}=L_\mu\circ\Theta_\mu^{\mathbb R}
\tag{57}
\]

has the fixed physical primitive gauge

\[
 f_\mu
 =\mathcal A_\mu^{\mathbb R}
  +g_{\rm phys}\circ L_\mu\circ\Theta_\mu^{\mathbb R},
 \qquad
 (\Phi_\mu^{\rm K})^*\lambda=\lambda_0+df_\mu.
\tag{58}
\]

On \(S^{-1}\mathcal D_{\rm src}\), it satisfies \(f_\mu(0)=0\) and
\(f_\mu\circ\mathcal R_0=-f_\mu\).  Formula (58), together with the
parameter-two-jet bounds from (50)--(51), is the primitive object required
by the obligation; an unfixed additive gauge is not sufficient.

## 8. Conditional conclusion and global gluing

Assume that the recurrence (22)--(24), the parameter-jet extension behind
(33)--(34), and the analytic map/inverse/primitive estimates have been proved
in this repository, and that a rigorous source-bound run validates
(17)--(19) and every resulting gate in (37)--(58).  Then the
complex-coordinate limits satisfy, on
\(\mathcal D_{\rm src}\),

\[
 K_\mu^{\mathbb C}\circ\Theta_\mu
 =g_\mu(J_1,J_2),
\tag{59}
\]

where

\[
 g_\mu(J_1,J_2)
 =\lambda_{1,\mu}J_1+\lambda_{2,\mu}J_2
   +\sum_{q\ge1}Z_{q,\mu}(J_1,J_2).
\]

Equivalently, using (3), there is a real analytic function
\(h_\mu^{\rm K}\) such that

\[
 \widehat H_\mu\circ\Phi_\mu^{\rm K}
 =h_\mu^{\rm K}(I_1,I_2^{\rm K}),
 \qquad
 dh_\mu^{\rm K}(0)=(\alpha_\mu,\beta_\mu).
\tag{60}
\]

The chart and its inverse are parameter-\(C^2\) in analytic norms, are real
and reversible, and have the exact primitive gauge (58).  More precisely,
\(\Psi^{\mathbb R}\) is a two-sided inverse on the source/target domains in
(42)--(42c), the physical chart image contains the common polydisc (44), and
the inverse there is
\(\Psi_\mu^{\mathbb R}\circ L_\mu^{-1}\).

The parameter grid is only an outward-bound partition.  A **single global
chart** is certified only if every grid cell evaluates the same formulas
(2), (5), and (22)--(24), with the same positive square-root branches,
projection \(\Pi\), divisor sign, Lie-map order, radius schedule,
\(\varepsilon_{\rm nf}\), and gauge normalizations.  Under those conditions,
the normalized homological solution is unique on shared faces.  Hence the
cellwise bounds certify restrictions of one global \(C^2\) family; they do
not define a 512-chart atlas, and no separate numerical overlap residual is
needed.

If a future implementation introduces cell-dependent frames,
preconditioners, homological projections, or gauge choices, the preceding
uniqueness argument no longer applies.  Such an implementation may at most
certify a finite-cover version after proving common domains and exact overlap
identities.  It cannot claim that the nonlinear chart cocycle has been
trivialized.

## 9. Claim boundary and outstanding proof obligations

This proposed amendment does not itself discharge
`V2.CHART.ANALYTIC_NORMAL_FORM`.  Before that atom can receive a local
mathematical `PASS`, the current repository must supply:

1. an outward-rounded proof of (18)--(19) and (17) on the complete bridge;
2. a proof that the Giorgilli recursion and constants (26)--(34) remain
   valid in the normalized parameter-two-jet Banach algebra;
3. a source-bound implementation of the exact \(q=1,2\) prefix and the
   all-orders tails (45)--(47a); an optional deeper prefix is not a PASS
   gate;
4. the analytic-flow and composition proof encoded by (37)--(51), including
   the exact \(B_z<1/16384\) gate, the \(A_z\)-amplified forward tail, the
   two-sided source/target domain identities, and the five
   \(s,p,h,m,q_2\) state/parameter variational tails;
5. the exact primitive construction (52)--(58); and
6. a check that all parameter cells are restrictions of the single global
   normalized construction described in Section 8.

Even after those six items pass, this amendment establishes only the
analytic normal-form atom and the analytic/gauge part of the stronger global
marking criterion.  It does not establish the zero-energy graph, exact
radial sections, weighted time and phase laws, physical event-free slides,
the complete physical overlap atlas, or `V2.EXACT_CHART`.  It also makes no
claim about temporal stability, Turing selection, or canard identification.
