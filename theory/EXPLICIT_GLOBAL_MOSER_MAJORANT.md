# Explicit global Moser majorant for the van der Pol saddle

**Evidence status: LOCAL-AMENDMENT / Proved and locally source-bound.**  This
note proves a computable sufficient criterion for the obligation
`V2.CHART.ANALYTIC_NORMAL_FORM`.  The proof includes the all-orders
parameter-two-jet Lie majorant, explicit map and inverse tails, and the fixed
primitive gauge.  The source-bound checker
`validation/rigorous/check_p2d_normal_form_source_bounds.py` authenticates the
complete continuation bridge and verifies every stated input and
domain-containment inequality.  Together they give this child atom a local
mathematical `PASS`.  The result remains non-claim-bearing under the separate
independent-replay policy, and it does not close `V2.EXACT_CHART`.

**Proof contract:** `rfsn-vdp-p2d-explicit-global-moser-majorant/1`.
Changing a formula, envelope, domain, or claim boundary requires a new proof
contract version and a newly bound source-check run.

The abstract input is Lemmas 2.4--2.6 and Proposition 2.7 in the frozen
flagship manuscript

```text
/home/hblu/Documents/Codex/2026-08-22/reversible-rfsn-ii-waves
commit d54add098545063d5efe8f1d6f062d4cfc116a0d
papers/paper-a/manuscript/main.tex
```

That repository is a read-only source.  The frozen parameter-majorant lemma
proves convergence after an unspecified state shrink and leaves its constants
implicit.  The purpose of the present local amendment is to prove one
van-der-Pol-specific shrink, all majorant constants, the inverse domain, and
the exact primitive gauge with explicit tails.  The model-specific inputs are
validated separately in this repository.

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

More precisely, let

\[
 \mathscr J_2
 =\mathbb C[\eta_r,\eta_a,\eta_\epsilon]/
   (\eta_r,\eta_a,\eta_\epsilon)^3,
 \qquad
 \left\|\sum_{|b|\le2}c_b\eta^b\right\|_{\mathscr J_2}
 =\sum_{|b|\le2}|c_b|,
\tag{11a}
\]

and define the factorial-weighted jet

\[
 \mathfrak j_\theta^2c
 =\sum_{|b|\le2}\frac{\partial_\theta^bc(\theta)}{b!}\eta^b.
\]

The uniform series norm used below is

\[
 \|J^2G\|_{R}^{\#}
 :=\sup_{\theta\in[-1,1]^3}
   \sum_{p,q}\|\mathfrak j_\theta^2G_{pq}\|_{\mathscr J_2}
   R^{|p|+|q|}.
\tag{11b}
\]

Thus (11) is not a pointwise shorthand with independently chosen derivative
maxima: it is the norm of one coefficient jet, followed by the supremum over
the common parameter box.  Truncated multiplication satisfies
\(\mathfrak j^2(fg)=\mathfrak j^2f\,\mathfrak j^2g\), and the norm in
(11a) is submultiplicative with constant one.

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

The source-bound checker establishes, from the gap-free exact-rational cover
of (8), the three frozen input gates

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

The thresholds in (18) were frozen before the source-bound run.  The older
design-only scout evaluated them from authenticated archived inputs but did
not establish them as theorem gates; the formal checker now does.  A future
failure after any source or formula change requires a new versioned contract
or sharper interval evaluation; it must not be hidden by shrinking the
already frozen parameter bridge.

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

The schedule has \(d_q>0\), \(\sum_{q\ge1}d_q=3/8<1/2\), and uses only the
lower gap bound (27).  The source index estimate, proved below in the
parameter-jet algebra, gives

\[
 T_{r,s}\le\left(\frac{16}{b_0^2}\right)^{s-1}.
\tag{28}
\]

The corresponding bound, including the off-diagonal indices needed for the
remainders, is

\[
 \mu_{q,s}\le\mu_{s,s}\le8^{s-1}
 \qquad(0\le q\le s).
\tag{29}
\]

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
\(\mathcal P^\natural\) and \(\mathcal P^\flat\) sectors are absent.  The
estimates corresponding to equations (35), (37), and (39) of that proof are

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

No factor \(d_q^{-1}\) is needed in (33)--(34).  Keeping that factor would be
a valid but unnecessarily weaker generic estimate.

### 4.1 Uniform second-parameter-jet majorant

We now prove the all-orders statement used above.  The formulation is kept
slightly more general so that every constant and every imported source step is
visible.

**Lemma 4.1 (two-degree-of-freedom \(J^2\) Giorgilli majorant).**  Suppose
\(E>0\), \(h\ge0\), and \(\kappa>0\), and suppose

\[
 \|J^2P_s^{(0)}\|_1^\#\le h^{s-1}E\quad(s\ge1),
 \qquad
 \|\mathfrak j_\theta^2(\Delta_{k,\theta}^{-1})\|_{\mathscr J_2}
 \le\frac\kappa{|k|_1}\quad(k\ne0),
\tag{34a}
\]

uniformly on a compact parameter box.  Let \(d_q>0\),
\(\delta_q=\sum_{j\le q}d_j\), and \(R_q=1-\delta_q\), and assume

\[
 \delta_\infty<\frac12,
 \qquad d_q\ge\frac b{q^2},
 \qquad 0<b\le1.
\tag{34b}
\]

Set

\[
 C_0=h+4e^2E\kappa,
 \qquad B_0=\frac{128}{b^2}C_0,
 \qquad G_0=E\kappa.
\tag{34c}
\]

Then the normalized recursion (22)--(24) satisfies, for \(q\ge1\) and
\(s>q\),

\[
 \|J^2\chi_q\|_{R_{q-1}}^\#\le G_0B_0^{q-1},
 \qquad
 \|J^2Z_q\|_{R_{q-1}}^\#\le EB_0^{q-1},
\tag{34d}
\]

\[
 \|J^2P_s^{(q)}\|_{R_q}^\#\le EB_0^{s-1}.
\tag{34e}
\]

**Proof.**  Work in the commutative Banach algebra \(\mathscr J_2\) from
(11a).  Products, the fixed projection \(\Pi\), and Poisson brackets obey
the same coefficient-majorant inequalities as in the scalar proof:
projection is contractive and all placements of one or two parameter
derivatives are already coefficients of the single truncated product.  Thus
there is no marked-tree or polynomial-in-\(q\) loss.

On a nonresonant monomial the homological inverse multiplies its jet
coefficient by the jet of \(\Delta_k^{-1}\).  The second inequality in (34a)
therefore gives the same \(|k|_1^{-1}\) gain as the scalar divisor estimate,
with the scalar \(\gamma^{-1}\) replaced by \(\kappa\) and the unscaled
polydisc constant \(\Lambda\) equal to one.  Giorgilli's generalized Cauchy
estimates (20), (21), and (23), and the coefficientwise induction of his
Lemma 3, consequently hold in \(\mathscr J_2\).  Since in two degrees of
freedom the sharp sector is the whole polynomial space, its equations (35),
(37), and (39) give

\[
 \begin{aligned}
 \|J^2\chi_q\|_{R_{q-1}}^\#
 &\le \mu_{q-1,q}T_{q-1,q}C_0^{q-1}E\kappa,\\
 \|J^2Z_q\|_{R_{q-1}}^\#
 &\le \mu_{q-1,q}T_{q-1,q}C_0^{q-1}E,\\
 \|J^2P_s^{(q)}\|_{R_q}^\#
 &\le \mu_{q,s}T_{q,s}C_0^{s-1}E.
 \end{aligned}
\tag{34f}
\]

The source constant is exactly \(h+4e^2E/(\gamma\Lambda^2)\), which is
(34c) under this replacement.  This is the complete parameter-jet lift of
the source induction.

It remains to bound its two scalar sequences.  Every index multiset \(J\) in
the source family \(\mathcal J_{r,s}\) satisfies

\[
 \#J\le2(s-1),
 \qquad
 \sum_{j\in J}\log_2j\le2(s-1-\log_2s).
\]

Using only (34b),

\[
 \begin{aligned}
 \prod_{j\in J}d_j^{-1}
 &\le b^{-\#J}\prod_{j\in J}j^2\\
 &\le b^{-2(s-1)}2^{2\sum_{j\in J}\log_2j}
 \le \left(\frac{16}{b^2}\right)^{s-1}.
 \end{aligned}
\tag{34g}
\]

This proves (28) without assuming \(d_j=b/j^2\).

For completeness, the nonnegative source recurrence is

\[
 \mu_{0,0}=0,
 \quad \mu_{0,s}=1\ (s>0),
 \quad
 \mu_{r,\ell r+m}
 =\sum_{p=0}^{\ell}\mu_{r-1,r}^{p}
  \mu_{r-1,(\ell-p)r+m},
 \quad0\le m<r.
\tag{34h}
\]

It gives monotonicity up to the diagonal and stabilization afterwards, hence
\(\mu_{q,s}\le\mu_{s,s}\).  It also gives

\[
 \mu_{s,s}\le s+\sum_{j=2}^{s-1}\mu_{j,j}\mu_{s-j,s-j}.
\tag{34i}
\]

Let \(\nu_1=1\), \(\nu_2=2\), and define the right-hand side of (34i)
recursively as \(\nu_s\).  If \(\lambda_1=1\) and
\(\lambda_s=\sum_{j=1}^{s-1}\lambda_j\lambda_{s-j}\), then
\(\lambda_s=C_{s-1}\le4^{s-1}\).  Induction gives
\(\nu_s\le2^{s-1}\lambda_s\): after applying the induction hypothesis to
the convolution, the remaining inequality is
\(s\le2^{s-2}(\lambda_s+\lambda_{s-1})\), which follows from
\(2^{s-1}\ge s\).  Therefore (29) holds.  Combining (34f), (34g), and
(29) proves (34d)--(34e), because
\(8(16/b^2)=128/b^2\).  The use of the source's sharp estimates also proves
that no factor \(d_q^{-1}\) is missing.  \(\square\)

For the schedule (26),

\[
 \frac{d_q}{3/(16q^2)}=\frac{2q}{q+1}\ge1,
\]

so Lemma 4.1 applies with \(b=b_0=3/16\).  The polynomial input has
\(h=h_{\rm in}\); its blocks of excess degree greater than two vanish.
Finally \(4e^2<30\) gives \(C_0\le C_*\), \(B_0\le B_*\), and
\(G_0=G_*\).  Thus the gates (18) imply (31)--(34) with the fixed envelopes
(32).

## 5. Frozen state shrink and domain-containment gates

Throughout this section, assume the model-specific gates (18).  Lemma 4.1
then supplies (33)--(34) in the parameter-two-jet algebra.  The following
calculations reduce the analytic-flow and domain parts of the source-bound
check to explicit rational inequalities.

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
 &\le\frac{512}{9}\varepsilon_{\rm nf}^2=:\overline S_0
 <\frac{\varepsilon_{\rm nf}}8.
 \end{aligned}
\tag{39}
\]

The displayed gate and envelope in (38)--(39) are exact rationals.  The
actual sum \(S_0\) directly controls successive negative-flow displacements
in the inverse order below.
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

Set \(\overline B_z:=37/691200\).  Since \(R_{q-1}\ge5/8\), the exact
generating-function identity

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
 &=\overline B_z
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
 \le\frac1{1-\overline B_z}=:A_z
 =\frac{691200}{691163}
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
 \le A_zS_0\le A_z\overline S_0
 =\frac{75}{23191581884416}
 =\frac{75}{5529304}\varepsilon_{\rm nf}
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

For the second-derivative Cauchy argument below, also freeze the intermediate
polydisc

\[
 \mathcal D_{\rm mid}
 =\Delta_{7\varepsilon_{\rm nf}/16}.
\tag{42d}
\]

The exact displacement quotient is

\[
 \frac{A_zS_0}{\varepsilon_{\rm nf}}
 \le\frac{A_z\overline S_0}{\varepsilon_{\rm nf}}
 =\frac{75}{5529304}<\frac1{16}.
\tag{42e}
\]

Consequently every finite \(\Theta_N\), as well as \(\Theta\), maps
\(\mathcal D_{\rm src}\) into \(\mathcal D_{\rm mid}\).  The latter is
compactly contained in \(\mathcal D_{\rm inv}\), with the explicit state
Cauchy gap \(\varepsilon_{\rm nf}/16\).

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
\tag{42f}
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
 \le\frac{2\varepsilon_{\rm nf}}7+\overline S_0
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
generators.  We next propagate those derivatives through every time-one map
and through the infinite composition.

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

We now turn (50)--(51) into explicit tails.  Write
\(\varepsilon=\varepsilon_{\rm nf}\), \(t=\vartheta=1/4\), and note that

\[
 R_{q-1}=\frac{5q+3}{8q}.
\]

In addition to \(\widehat v_q\) and \(b_q\), set

\[
 c_q
 =\frac{q(q+1)(q+2)\overline Gt^{q-1}}{R_{q-1}^3}.
\tag{51a}
\]

Equations (48)--(50) allow

\[
 a_0,a_1\le\widehat v_q,
 \qquad a_2\le2\widehat v_q,
 \qquad \ell_0,\ell_1\le b_q,
 \qquad c_0\le c_q.
\tag{51b}
\]

Put \(\widehat s_q=(1-b_q)^{-1}\).  Variation of constants in (50), and
\(e^{b_q}\le\widehat s_q\), give for both \(T_q\) and \(T_q^{-1}\)

\[
 \begin{array}{ll}
 \|D_zT_q^{\pm1}\|\le\widehat s_q,
 &\|D_zT_q^{\pm1}-I\|\le\sigma_q:=\widehat s_qb_q,\\[2mm]
 p_q\le\widehat s_q\widehat v_q,
 &h_q\le\widehat s_q^2c_q,\\[1mm]
 m_q\le\widehat s_q^2b_q+
          \widehat s_q^3c_q\widehat v_q,
 &q_q^{(2)}\le2\widehat s_q\widehat v_q
   +2\widehat s_q^2b_q\widehat v_q
   +\widehat s_q^3c_q\widehat v_q^2.
 \end{array}
\tag{51c}
\]

Here \(p_q,h_q,m_q,q_q^{(2)}\) bound the four nontrivial derivatives in
(50).  Since
\(\prod_j(1-b_j)\ge1-\sum_jb_j\), every finite Lipschitz product is bounded
by \(A_z\), and \(\sigma_q\le A_zb_q\).

For \(N\ge0\), the three basic positive tails have the following exact
rational upper bounds:

\[
 \begin{aligned}
 \sum_{q>N}\widehat v_q
 &\le V_N:=\frac{256(3N+10)}{45\,4^N}\varepsilon^2,\\
 \sum_{q>N}b_q
 &\le B_N:=\frac{2048(9N^2+51N+74)}{675\,4^N}\varepsilon,\\
 \sum_{q>N}c_q
 &\le C_N:=\frac{16384(9N^3+63N^2+150N+128)}
              {3375\,4^N}.
 \end{aligned}
\tag{51d}
\]

In particular,

\[
 V_0=\frac1{309237645312},
 \qquad B_0=\frac{37}{691200},
 \qquad C_0=\frac{2097152}{3375},
\tag{51e}
\]

where the symbols in (51e) are tail bounds and should not be confused with
the majorant constants in (34c).  Define the single-flow derivative tails

\[
 \begin{aligned}
 \Sigma_N&=A_zB_N,& P_N^{\rm f}&=A_zV_N,
 &H_N^{\rm f}&=A_z^2C_N,\\
 M_N^{\rm f}&=A_z^2B_N+A_z^3C_NV_N,
 &Q_N^{\rm f}&=2A_zV_N+2A_z^2B_NV_N+A_z^3C_NV_N^2.
 \end{aligned}
\tag{51f}
\]

The products \(C_NV_N\), \(B_NV_N\), and \(C_NV_N^2\) bound the
corresponding sums term by term because all summands are nonnegative.

For a composition \(F\circ G\), if \((S,P,H,M,Q)\) denotes the five
operator bounds in the order used in (50), (51) gives the executable scalar
recurrence

\[
 \begin{aligned}
 S&=S_FS_G,&
 P&=P_F+S_FP_G,\\
 H&=H_FS_G^2+S_FH_G,&
 M&=M_FS_G+H_FS_GP_G+S_FM_G,\\
 Q&=Q_F+2M_FP_G+H_FP_G^2+S_FQ_G.
 \end{aligned}
\tag{51g}
\]

For the inverse order \(\Psi_q=T_q^{-1}\circ\Psi_{q-1}\), (51g) gives
the uniform accumulated bounds

\[
 \begin{aligned}
 \overline S&=A_z,\\
 \overline P&=A_zP_0^{\rm f}=A_z^2V_0,\\
 \overline H&=A_z^3H_0^{\rm f}=A_z^5C_0,\\
 \overline M&=A_z^2
   \bigl(M_0^{\rm f}+\overline P H_0^{\rm f}\bigr),\\
 \overline Q&=A_z
   \bigl(Q_0^{\rm f}+2\overline P M_0^{\rm f}
                  +\overline P^2H_0^{\rm f}\bigr).
 \end{aligned}
\tag{51h}
\]

This is boundedness; the following difference calculation supplies the
needed Cauchy statement.  Subtracting \(\Psi_{q-1}\) from
\(T_q^{-1}\circ\Psi_{q-1}\) in the five exact chain rules gives, after
summing over \(q>N\),

\[
 \begin{aligned}
 E_N^S&=A_z\Sigma_N,\\
 E_N^P&=P_N^{\rm f}+\overline P\Sigma_N,\\
 E_N^H&=A_z^2H_N^{\rm f}+\overline H\Sigma_N,\\
 E_N^M&=A_zM_N^{\rm f}
       +A_z\overline P H_N^{\rm f}+\overline M\Sigma_N,\\
 E_N^Q&=Q_N^{\rm f}+2\overline P M_N^{\rm f}
       +\overline P^2H_N^{\rm f}+\overline Q\Sigma_N.
 \end{aligned}
\tag{51i}
\]

More precisely, \(E_N^S,E_N^P,E_N^H,E_N^M,E_N^Q\) bound the tails of
\(D_z,D_\theta,D_z^2,D_zD_\theta,D_\theta^2\), respectively, while
\(\|\Psi-\Psi_N\|\le V_N\).  Every right-hand side is a rational function
of \(N\) times a polynomial in \(N\) times \(4^{-N}\), and tends to zero.
Thus \(\Psi_N\) is genuinely joint state--parameter \(C^2\)-Cauchy on
\(\mathcal D_{\rm inv}\); (51h) alone would not have been sufficient.

It remains to transfer this result to the forward maps without introducing
a third variational system.  Put

\[
 E_N^1=E_N^S+E_N^P,
 \qquad E_N^2=E_N^H+2E_N^M+E_N^Q,
 \qquad D_\Psi=\overline H+2\overline M+\overline Q.
\tag{51j}
\]

Differentiating \(\Psi(\Theta(z,\theta),\theta)=z\) gives

\[
 \begin{aligned}
 D_z\Theta&=(D_z\Psi)^{-1},\\
 D_\theta\Theta&=-(D_z\Psi)^{-1}D_\theta\Psi,\\
 D_z^2\Theta&=-(D_z\Psi)^{-1}
   D_z^2\Psi[D_z\Theta,D_z\Theta],\\
 D_zD_\theta\Theta&=-(D_z\Psi)^{-1}
 \{D_z^2\Psi[D_z\Theta,D_\theta\Theta]
                 +D_zD_\theta\Psi D_z\Theta\},\\
 D_\theta^2\Theta&=-(D_z\Psi)^{-1}
 \{D_\theta^2\Psi+2D_zD_\theta\Psi D_\theta\Theta
       +D_z^2\Psi[D_\theta\Theta,D_\theta\Theta]\}.
 \end{aligned}
\tag{51k}
\]

The same identities hold for every finite inverse pair.  Since the finite
forward Lipschitz products are at most \(A_z\), set

\[
 \begin{aligned}
 \overline P_\Theta&=A_z\overline P,
 &\overline H_\Theta&=A_z^3\overline H,\\
 \overline M_\Theta&=A_z^2
   (\overline M+\overline H\overline P_\Theta),
 &\overline Q_\Theta&=A_z
   (\overline Q+2\overline M\overline P_\Theta
          +\overline H\overline P_\Theta^2),\\
 L_\Theta&=A_z+\overline P_\Theta,
 &D_\Theta&=\overline H_\Theta+2\overline M_\Theta+
             \overline Q_\Theta.
 \end{aligned}
\tag{51l}
\]

The intermediate domain (42d) is essential here.  Its gap to
\(\mathcal D_{\rm inv}\) and the four complex state variables give the
Cauchy bound \(64D_\Psi/\varepsilon\) for the state derivative of the joint
second derivative of every \(\Psi_N\) and of \(\Psi\).  With
\(d_N^0=A_zV_N\), the matrix-inverse identity and (51k) therefore give the
fully explicit forward tails on \(\mathcal D_{\rm src}\):

\[
 E_N^{\Theta,1}
 \le L_\Theta^2
   \{E_N^1+(\overline H+\overline M)d_N^0\},
\tag{51m}
\]

\[
 E_N^{\Theta,2}
 \le3D_\Psi L_\Theta^2E_N^{\Theta,1}
 +L_\Theta^3
  \left\{E_N^2+\frac{64}{\varepsilon}D_\Psi d_N^0\right\}.
\tag{51n}
\]

To see the factor three in (51n), apply the augmented inverse formula to
\((z,\theta)\mapsto(\Psi(z,\theta),\theta)\): its second derivative is one
second derivative of \(\Psi\) multiplied by three inverse first-derivative
factors.  Equations (51m)--(51n) compare those four factors one at a time;
the shifted evaluation is controlled by the state Cauchy bound.  Hence
\(\Theta_N\to\Theta\) through joint order two in analytic norms on
\(\mathcal D_{\rm src}\).  This inverse-first argument avoids the invalid
shortcut of comparing a forward prefix Hessian at \(T_q(z)\) and at \(z\)
without a third-state-derivative modulus.

For scale only, the exact rational constants in (51h)--(51l) evaluate to

\[
 \begin{aligned}
 \overline P&<3.235\times10^{-12},&
 \overline H&<621.545,&
 \overline M&<5.355\times10^{-5},&
 \overline Q&<6.469\times10^{-12},\\
 D_\Psi&<621.545,&
 L_\Theta&<1.000054,&
 D_\Theta&<621.645.
 \end{aligned}
\tag{51o}
\]

These decimals are explanatory only; the checker evaluates the defining
rational expressions.  The comparatively large state Hessian never enters
the near-identity or domain gates.

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

The convergence proof is again cleanest in the inverse order.  Conservation
of \(\chi_q\) along its own flow gives

\[
 (T_q^{-1})^*\lambda_0-\lambda_0
 =d\left(\frac q2\chi_q\right).
\tag{54a}
\]

Define

\[
 \mathcal B_0=0,
 \qquad
 \mathcal B_q=\mathcal B_{q-1}
 +\left(\frac q2\chi_q\right)\circ\Psi_{q-1}.
\tag{54b}
\]

Then exactly, at every finite stage,

\[
 \Psi_q^*\lambda_0-\lambda_0=d\mathcal B_q,
 \qquad
 \mathcal A_q=-\mathcal B_q\circ\Theta_q.
\tag{54c}
\]

The second identity is algebraically equivalent to (54), not a different
choice of gauge.

For an explicit \(C^2\) proof, let

\[
 \alpha_q=4q\varepsilon^3t^{q-1},
 \qquad g_q=\frac q2\widehat v_q,
 \qquad k_q=\frac q2b_q.
\tag{54d}
\]

These bound, respectively, the parameter-two-jet value, its state gradient,
and its state Hessian for \(q\chi_q/2\).  Their rational tails are

\[
 \begin{aligned}
 \sum_{q>N}\alpha_q
 &\le A_N^\chi:=\frac{16(3N+4)}{9\,4^N}\varepsilon^3,\\
 \sum_{q>N}g_q
 &\le G_N^\chi:=\frac{128(9N^2+42N+44)}{135\,4^N}\varepsilon^2,\\
 \sum_{q>N}k_q
 &\le K_N^\chi:=\frac{1024(9N^3+63N^2+150N+128)}
                 {675\,4^N}\varepsilon.
 \end{aligned}
\tag{54e}
\]

At \(N=0\),

\[
 A_0^\chi=\frac1{10376293541461622784},
 \qquad G_0^\chi=\frac{11}{4638564679680},
 \qquad K_0^\chi=\frac1{21600}.
\tag{54f}
\]

Applying the scalar chain rule to each summand in (54b), with the inverse
bounds (51h), gives the five primitive tails

\[
 \begin{aligned}
 e_N^{B,0}&=A_N^\chi,\\
 e_N^{B,z}&=\overline S G_N^\chi,\\
 e_N^{B,\theta}&=A_N^\chi+\overline P G_N^\chi,\\
 e_N^{B,zz}&=\overline S^2K_N^\chi+\overline H G_N^\chi,\\
 e_N^{B,z\theta}&=(\overline S+\overline M)G_N^\chi
                  +\overline S\overline P K_N^\chi,\\
 e_N^{B,\theta\theta}&=2A_N^\chi
    +(2\overline P+\overline Q)G_N^\chi
    +\overline P^2K_N^\chi.
 \end{aligned}
\tag{54g}
\]

All six quantities tend to zero, so \(\mathcal B_q\) converges jointly
through state--parameter order two on \(\mathcal D_{\rm inv}\).  Write the
limit as \(\mathcal B\) and define on \(\mathcal D_{\rm src}\)

\[
 \mathcal A=-\mathcal B\circ\Theta.
\tag{54h}
\]

For a machine-readable tail of the forward primitive, put

\[
 \begin{aligned}
 b_{1,N}&=e_N^{B,z}+e_N^{B,\theta},\\
 b_{2,N}&=e_N^{B,zz}+2e_N^{B,z\theta}+e_N^{B,\theta\theta},\\
 b_1&=b_{1,0},\qquad b_2=b_{2,0},
 \qquad C_B=\frac{64}{\varepsilon}b_2.
 \end{aligned}
\tag{54i}
\]

The same intermediate-domain Cauchy gap used in (51n), followed by the
second-order scalar composition rule, gives

\[
 \begin{aligned}
 e_N^{A,0}
 &\le e_N^{B,0}+b_1d_N^0,\\
 e_N^{A,1}
 &\le L_\Theta(b_{1,N}+b_2d_N^0)
       +b_1E_N^{\Theta,1},\\
 e_N^{A,2}
 &\le L_\Theta^2(b_{2,N}+C_Bd_N^0)
       +2b_2L_\Theta E_N^{\Theta,1}\\
 &\quad+D_\Theta(b_{1,N}+b_2d_N^0)
       +b_1E_N^{\Theta,2}.
 \end{aligned}
\tag{54j}
\]

Thus \(\mathcal A_q\to\mathcal A\) jointly through order two on the fixed
\(\mathcal D_{\rm src}\), and (54c) passes to the limit.  All generators
have degree at least three, so the origin is fixed and every additive
constant in (54b)--(54h) is zero.  Moreover
\(\chi_q\circ\mathcal R_0=-\chi_q\), every flow commutes with
\(\mathcal R_0\), and induction gives the normalization and reverser parity

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
coordinates (2).  For the type-correct real chart, use (42f) and put
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
parameter-two-jet bounds from (50)--(51), the already certified jets of
\(L_\mu\), and the finite chain rule for the quadratic polynomial
\(g_{\rm phys}\), is the primitive object required by the obligation; an
unfixed additive gauge is not sufficient.

## 8. The proved implication and global gluing

Sections 3--7 prove the analytic implication.  The bound checker named at the
start of this note validates (17)--(19) and the resulting rational gates in
(37)--(58).  Therefore the complex-coordinate limits satisfy, on
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

## 9. Exact claim boundary

The proof contract in this note, the exact \(q=1,2\) symbolic audit, and the
source-bound checker together establish a local mathematical `PASS` for
`V2.CHART.ANALYTIC_NORMAL_FORM`.  In particular, the checker authenticates the
complete outward-rounded bridge input, verifies (17)--(19),
(30)--(44a), and the machine-evaluated tails, binds this proof version, and
checks that the 512 grid cells bound one global normalized construction.

This is a child-atom result, not a pass for the full local passage.  It does
not establish the zero-energy graph, exact radial sections, weighted time and
phase laws, physical event-free slides, the physical overlap atlas, or
`V2.EXACT_CHART`; those five remaining child atoms stay `OPEN`.  The aggregate
status is `INCONCLUSIVE` and `claim_bearing=false` while independent replay is
one of two required machines.  It also makes no claim about temporal
stability, Turing selection, or canard identification.
