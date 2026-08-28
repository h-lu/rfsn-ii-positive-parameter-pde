# Explicit weighted Kato passage and clock inversion

**Proof contract:** `rfsn-vdp-p2d-explicit-weighted-kato-passage/1`

**Local conclusion:** on one uniform punctured action interval, this note
proves the logarithmic time and positive-Kato phase laws, their complete
parameter-two-jet weighted bounds, an all-finite-log-order Cauchy generator,
and the signed clock inversion used downstream.  Together with the bound
source checker, it discharges `V2.CHART.WEIGHTED_PASSAGE`.  It does not
construct the physical face slides or chart overlaps and does not close
`V2.EXACT_CHART`.

## 1. Exact passage formula

Work in the exact Kato normal form and on the nonlinear zero-energy fiber
already established in the preceding two proof contracts.  Put

\[
 \rho_0=\frac5{2^{26}},\qquad
 a_\mu(\nu)=\partial_{I_1}h_\mu(q_\mu(\nu),\nu),\qquad
 \omega_\mu(\nu)=\partial_{I_2^{\rm K}}
 h_\mu(q_\mu(\nu),\nu).
\tag{1}
\]

The exact section calculation gives, for
\(0<|\nu|\le25/2^{54}\),

\[
 \begin{aligned}
 T_\mu(\nu)
  &=a_\mu(\nu)^{-1}
    \log\!\frac{\rho_0^2}
    {\sqrt{q_\mu(\nu)^2+\nu^2}},\\
 \Delta_{\mu,\sigma}(\nu)
  &=\omega_\mu(\nu)T_\mu(\nu)
    +\arg_\sigma(q_\mu(\nu)-i\nu),
 \qquad \sigma\nu>0.
 \end{aligned}
\tag{2}
\]

Here `arg` denotes the lifted branch fixed by the positive Kato section
phase.  The action and its sign are unchanged.  The expanding Kato plane
rotates with speed \(+\omega_\mu\); together with the positive flight time
in (2), this is what produces the negative logarithmic phase coefficient
below.

The quotient

\[
 p_\mu(\nu)=\begin{cases}q_\mu(\nu)/\nu,&\nu\ne0,\\
 -\beta_\mu/\alpha_\mu,&\nu=0,
 \end{cases}
\tag{3}
\]

is analytic.  Define

\[
 A=\frac1a,\qquad \Omega=\frac\omega a,\qquad
 C=\log\rho_0^2-\frac12\Log(1+p^2),
\tag{4}
\]

where the logarithm is fixed to be real at \(\nu=0\).  On either signed
component, the variation of the lifted argument is the imaginary part of

\[
 \Log\frac{p_\mu(\nu)-i}{p_\mu(0)-i}.
\tag{5}
\]

The lift is fixed absolutely, not only modulo \(2\pi\).  On the real
parameter slice, \(p_\mu(0)=-\beta_\mu/\alpha_\mu\).  Freeze

\[
 \gamma_{\mu,+}=-\pi+\arctan(\alpha_\mu/\beta_\mu),
 \qquad
 \gamma_{\mu,-}=\arctan(\alpha_\mu/\beta_\mu),
\]

with the principal arctangent, and define \(\arg_\sigma\) to be the unique
continuous lift on the signed collar with this one-sided limit.  This is the
positive-Kato deck convention used everywhere below.

Thus (2) is exactly

\[
 T=-A\log|\nu|+AC,
 \qquad
 \Delta=-\Omega\log|\nu|+\Omega C+\arg_\sigma(q-i\nu).
\tag{6}
\]

The characteristic identity \(\alpha_\mu^2+\beta_\mu^2=1\), already used
in the authenticated linear Kato audit, and (3) give

\[
 C_\mu(0)=\log(\alpha_\mu\rho_0^2).
\tag{7}
\]

Consequently the constants and remainders are fixed, rather than selected
after a passage computation, by

\[
 \begin{aligned}
 t^\mathrm K_\mu
  &=\alpha_\mu^{-1}\log(\alpha_\mu\rho_0^2),\\
 b^\mathrm K_{\mu,\sigma}
  &=\beta_\mu t^\mathrm K_\mu+\gamma_{\mu,\sigma},\\
 \tau^\mathrm K_\mu(\nu)
  &=-\{A_\mu(\nu)-A_\mu(0)\}\log|\nu|
    +\{(AC)_\mu(\nu)-(AC)_\mu(0)\},\\
 \rho^\mathrm K_{\mu,\sigma}(\nu)
  &=-\{\Omega_\mu(\nu)-\Omega_\mu(0)\}\log|\nu|\\
  &\quad+\{(\Omega C)_\mu(\nu)-(\Omega C)_\mu(0)\}
    +\arg_\sigma(q_\mu(\nu)-i\nu)-\gamma_{\mu,\sigma},
 \end{aligned}
\tag{8}
\]

where \(\gamma_{\mu,\sigma}\) is the one-sided limiting lifted argument.
Equations (6)--(8) prove the required laws

\[
 \begin{aligned}
 T_\mu(\nu)&=-\alpha_\mu^{-1}\log|\nu|
   +t^\mathrm K_\mu+\tau^\mathrm K_\mu(\nu),\\
 \Delta_{\mu,\sigma}(\nu)&=-\frac{\beta_\mu}{\alpha_\mu}\log|\nu|
   +b^\mathrm K_{\mu,\sigma}
   +\rho^\mathrm K_{\mu,\sigma}(\nu).
 \end{aligned}
\tag{9}
\]

## 2. One complex collar for both signs

Let

\[
 R_q=\frac{25}{2^{53}},\qquad
 R=\frac{R_q}{16}=\frac{25}{2^{57}},\qquad
 \nu_\mathrm p=\frac R2=\frac{25}{2^{58}}.
\tag{10}
\]

The zero-energy proof supplies, on \(|\nu|\le R_q\),

\[
 Q_0=\frac{9875}{3\,2^{60}},\qquad
 Q_1=\frac{195}{2^{61}},\qquad
 Q_2=\frac{10543632881}{25\,2^{82}},
\tag{11}
\]

for the normalized parameter jets of orders zero, one, and two.  Schwarz's
lemma, applied also after one or two parameter differentiations, gives

\[
 P_0=\frac{Q_0}{R_q}=\frac{395}{384},\quad
 P_1=\frac{Q_1}{R_q}=\frac{39}{1280},\quad
 P_2=\frac{Q_2}{R_q}=\frac{10543632881}{335544320000}
\tag{12}
\]

as bounds for the corresponding jets of \(p\).  The authenticated frame
hulls imply

\[
 \frac23\le\alpha_\mu,\beta_\mu\le\frac34,qquad
 \frac89\le |p_\mu(0)|\le\frac98.
\tag{13}
\]

For \(|\nu|\le R\), coefficient summation gives

\[
 |p_\mu(\nu)-p_\mu(0)|
 \le P_0\frac{1/16}{1-1/16}
 =\frac{79}{1152}<\frac18.
\tag{14}
\]

Hence \(p-i\), \(p+i\), and \(1+p^2\) do not vanish there.  More
quantitatively,

\[
 \left|\frac{1+p(\nu)^2}{1+p(0)^2}-1\right|
 \le\frac{211009}{2375680}<\frac1{10}.
\tag{15}
\]

Equations (14)--(15) construct both logarithms in (4)--(5) on one complex
disk and therefore settle the branch issue simultaneously for
\(\sigma=+\) and \(\sigma=-\).  They also give the conservative bounds

\[
 |p|\le\frac54,qquad |C|\le54,qquad
 \left|\Log\frac{p-i}{p(0)-i}\right|\le\frac17.
\tag{16}
\]

On the real slice, (13)--(14) also give
\(p\le-8/9+79/1152<0\).  The frozen lifts therefore remain in the third
quadrant for \(\nu>0\) and the first quadrant for \(\nu<0\); in particular
\(|\arg_\sigma|<\pi<4\).  This supplies the absolute argument bound used in
the winding comparison, without an unrecorded \(2\pi\)-deck choice.

## 3. Explicit parameter-two-jet envelopes

Put \(s=25/2^{50}\), \(g=s/2\), and
\(\overline M=(3\,2^{62})^{-1}\).  The action Cauchy estimates are

\[
 M_1=\frac{\overline M}{g},\qquad
 M_2=\frac{2\overline M}{g^2},\qquad
 M_3=\frac{6\overline M}{g^3}.
\tag{17}
\]

Every normalized first or second parameter derivative of \(\alpha,\beta\)
is bounded by \(1/100\).  Chain differentiation of
\(a=\alpha+N_{I_1}(q,\nu)\) and
\(\omega=\beta+N_{I_2}(q,\nu)\) therefore gives, for parameter order
\(j=0,1,2\), the common bounds

\[
 \begin{aligned}
 H_0&=\frac34+M_1,\\
 H_1&=\frac1{100}+M_1+M_2Q_1,\\
 H_2&=\frac1{100}+2M_1+2M_2Q_1+M_3Q_1^2+M_2Q_2.
 \end{aligned}
\tag{18}
\]

Since \(|a|>2/3\) on the complex fiber, define the following rational
majorants:

\[
 \begin{aligned}
 A_0&=\frac32,&
 A_1&=\frac{H_1}{(2/3)^2},&
 A_2&=\frac{2H_1^2}{(2/3)^3}+\frac{H_2}{(2/3)^2},\\
 W_0&=H_0A_0,&
 W_1&=H_1A_0+H_0A_1,&
 W_2&=H_2A_0+2H_1A_1+H_0A_2.
 \end{aligned}
\tag{19}
\]

These bound the parameter jets of \(A\) and \(\Omega\), respectively.
With \(Z^{-1}=64/49\), the jets of \(C\) are bounded by

\[
 \begin{aligned}
 C_0&=54,\\
 C_1&=\frac54P_1Z^{-1},\\
 C_2&=(P_1^2+\tfrac54P_2)Z^{-1}
       +2(\tfrac54)^2P_1^2(Z^{-1})^2,
 \end{aligned}
\tag{20}
\]

and those of the argument variation by

\[
 D_0=\frac17,\qquad
 D_1=\frac87P_1,qquad
 D_2=\frac87P_2+\frac{64}{49}P_1^2.
\tag{21}
\]

Finally set, with the usual complete product rule,

\[
 \begin{aligned}
 B_0&=A_0C_0,&
 B_1&=A_1C_0+A_0C_1,&
 B_2&=A_2C_0+2A_1C_1+A_0C_2,\\
 E_0&=W_0C_0,&
 E_1&=W_1C_0+W_0C_1,&
 E_2&=W_2C_0+2W_1C_1+W_0C_2.
 \end{aligned}
\tag{22}
\]

Thus \(B_j\) and \(E_j\) bound the parameter jets of \(AC\) and
\(\Omega C\).  All quantities in (17)--(22) are explicit rationals; no
sampled maximum enters their definition.  Since the remainders in (8)
contain centered differences, set

\[
 \widehat A_j=2A_j,\quad \widehat B_j=2B_j,\quad
 \widehat W_j=2W_j,\quad \widehat E_j=2E_j,
 \qquad
 (\widehat D_0,\widehat D_1,\widehat D_2)
 =(D_0,2D_1,2D_2).
\]

The factors two bound the difference between the value at \(\nu\) and
the value at zero.  The exception \(\widehat D_0=D_0\) is valid because
\(D_0\) already bounds the argument variation in (5), whereas
\(D_1,D_2\) first bound one parameter jet of the logarithmic composite.

## 4. The all-finite-order weighted generator

For \(m\ge0\), let

\[
 \Lambda_m
 =\sum_{j=0}^m{m\choose j}
   \sum_{k=0}^j
   \left\{\!\!\begin{matrix}j\\k\end{matrix}\!\!\right\}k!.
\tag{23}
\]

These integers are computed by the finite Stirling recurrence; in particular,

\[
 \Lambda_0,\Lambda_1,\Lambda_2,\Lambda_3=1,2,6,26.
\tag{24}
\]

To see the estimate encoded by (23), let \(F(0)=0\) and
\(\sup_{|\nu|\le R}|F|\le M\).  Schwarz's lemma writes \(F=\nu G\)
with \(|G|\le M/R\).  On \(|\nu|\le R/2\), Cauchy's estimate for
\(G^{(k)}\), followed by
\(D_{\log\nu}^j=\sum_k\left\{\begin{smallmatrix}j\\k\end{smallmatrix}\right\}
\nu^k\partial_\nu^k\), gives
\(|D_{\log\nu}^mF|\le(M/R)\Lambda_m|\nu|\).
For parameter order \(j=0,1,2\), define

\[
 \begin{aligned}
 \mathcal C^T_{j,m}
 &=\frac1R\left[
 \widehat A_j\{\Lambda_m+m\Lambda_{m-1}\}
 +\widehat B_j\Lambda_m\right],\\
 \mathcal C^\Delta_{j,m}
 &=\frac1R\left[
 \widehat W_j\{\Lambda_m+m\Lambda_{m-1}\}
 +(\widehat E_j+\widehat D_j)\Lambda_m\right],
 \end{aligned}
\tag{25}
\]

where the term containing \(\Lambda_{m-1}\) is omitted at \(m=0\).
Coefficientwise application of \(D_{\log\nu}=\nu\partial_\nu\) to (8)
now proves, for every normalized parameter multi-index \(|\gamma|=j\le2\),
every fixed finite \(m\), and \(0<|\nu|\le\nu_\mathrm p\),

\[
 \begin{aligned}
 |D_\theta^\gamma D_{\log\nu}^m\tau^\mathrm K_\mu(\nu)|
 &\le\mathcal C^T_{j,m}|\nu|(1+|\log|\nu||),\\
 |D_\theta^\gamma D_{\log\nu}^m
       \rho^\mathrm K_{\mu,\sigma}(\nu)|
 &\le\mathcal C^\Delta_{j,m}|\nu|(1+|\log|\nu||).
 \end{aligned}
\tag{26}
\]

Indeed,

\[
 D_{\log\nu}^m(F\log|\nu|)
 =(D_{\log\nu}^mF)\log|\nu|
  +mD_{\log\nu}^{m-1}F,
\tag{27}
\]

and every analytic difference in (8) vanishes at zero.  Equations
(23)--(27) are the promised constructive generator.  One may take

\[
 \nu_{*,m}=\nu_\mathrm p,qquad
 C_m=625\max_{0\le j\le2}
 (\mathcal C^T_{j,m}+\mathcal C^\Delta_{j,m}).
\tag{28}
\]

The factor 625 is the largest original-parameter factor through order two.
More precisely, derivatives in \((r,a_2,\epsilon)\) multiply (25) by
\(25^{\gamma_r}4^{\gamma_a}5^{\gamma_\epsilon}\).  Thus (25) supplies the
complete rectangular family
\(D_\mu^{|\gamma|\le2}D_{\log\nu}^{m}\), not merely a total-order list.

## 5. A uniform clock root

The previous generator is designed for arbitrary order and is intentionally
coarse.  A sharper order-zero estimate gives a useful uniform clock
contraction.  On \(|\nu|\le\nu_\mathrm p\), direct rational estimates from
(17) first bound every centered analytic factor by \(K|\nu|\), with its
displayed endpoint constant obtained at \(|\nu|=\nu_\mathrm p\).  Now
\(\nu_\mathrm p<1/4<e^{-1}\) (using \(e<4\)), and
\(-\log\nu_\mathrm p<58\) because \(e>2\) and
\(\nu_\mathrm p=25/2^{58}>2^{-58}\).  Since
\(x|\log x|\) and \(x(1+|\log x|)\) are increasing on the required
interval, the endpoint weights 58 and 59 control the entire punctured
collar.  They are not assertions that \(|\log|\nu||\) itself is bounded.
The resulting exact estimate is

\[
 |\tau^\mathrm K_\mu(\nu)|
 \le\frac{47190032286432199}{1421420709753651200}<\frac1{16},
\tag{29}
\]

and

\[
 |D_{\log\nu}\tau^\mathrm K_\mu(\nu)|
 \le\frac{800437431495572029}{12562311043402956800}.
\tag{30}
\]

Since \(\alpha_\mu\le3/4\), (30) implies

\[
 \kappa_*:=\sup|\alpha_\mu D_{\log\nu}\tau^\mathrm K_\mu|<\frac1{16}.
\tag{31}
\]

The authenticated frame also gives the sharper real lower gate
\(\alpha_\mu\ge7/10\), beyond the coarse complex-domain bound in (13).
The same clock constant as in (8) therefore satisfies the exact identity

\[
 c^\mathrm K_\mu=e^{\alpha_\mu t^\mathrm K_\mu}
 =\alpha_\mu\rho_0^2,qquad
 \frac{35}{2^{53}}=:c_*\le c^\mathrm K_\mu
 \le\frac34\rho_0^2.
\tag{32}
\]

For \(n\ge2\), \(0\le\theta<2\pi\), and either sign, put

\[
 U_{\mu,n}(\theta)
 =\frac{\alpha_\mu}{\beta_\mu}(2\pi n+\theta)
  -\log c^\mathrm K_\mu.
\tag{33}
\]

All estimates below also hold on the closed endpoint \(\theta=2\pi\), which
is included only to make the uniform inequalities convenient.

The logarithmic clock equation is the fixed-point equation

\[
 u=U_{\mu,n}(\theta)
   -\alpha_\mu\tau^\mathrm K_\mu(\sigma e^{-u}).
\tag{34}
\]

For every \(u\) in the trial interval
\([U-\alpha/16,U+\alpha/16]\), one has

\[
 |\sigma e^{-u}|
 \le \overline\nu_n
 :=\frac34\rho_0^2\frac{64}{61}\,16^{-n},qquad
 \frac{\overline\nu_2}{\nu_\mathrm p}=\frac{12}{61}<1.
\tag{35}
\]

Here \(\alpha/\beta\ge8/9\), \(2\pi>6\), and
\(e^{16/3}>16\) give the factor \(16^{-n}\); the last inequality follows,
for example, from \(16/3>4\) and the exponential series at 4.  We also used
\(e^x\le(1-x)^{-1}\) for \(0\le x<1\).  The ratio in (35) puts the complete
trial interval inside the validated action collar before any remainder bound
is invoked.  The estimates (29)--(31) then show that the right side of (34)
maps that interval into itself and has Lipschitz constant below \(1/16\).
Thus (34) has one and only one root there, and

\[
 \nu_{\mu,\sigma,n}(\theta)
 =\sigma c^\mathrm K_\mu
 e^{-\alpha_\mu(2\pi n+\theta)/\beta_\mu}
 \exp\{\alpha_\mu\tau^\mathrm K_\mu
        (\nu_{\mu,\sigma,n}(\theta))\}.
\tag{36}
\]

For completeness, the checker exports an exact derivative generator for
this root.  Let \(K_{U,1},K_{U,2}\) be the rational bounds obtained by
differentiating (33), and let \(R_1,R_2,R_{u1},R_{uu}\) be the corresponding
bounds for parameter derivatives of
\(\alpha\tau(\sigma e^{-u})\), obtained from (25).  With \(J=16/15\), set

\[
 \begin{aligned}
 u_1(n)&=J\{K_{U,1}(n+1)+R_1\},\\
 u_2(n)&=J\{K_{U,2}(n+1)+R_2
   +2R_{u1}u_1(n)+R_{uu}u_1(n)^2\}.
 \end{aligned}
\tag{37}
\]

Implicit differentiation of (34) gives, for every first and second
derivative in \((\theta,\theta_r,\theta_a,\theta_\epsilon)\),

\[
 |D\nu_n|\le\overline\nu_n\,u_1(n),\qquad
 |D^2\nu_n|\le\overline\nu_n\{u_1(n)^2+u_2(n)\}.
\tag{38}
\]

The factors \(25,4,5\) again convert these to the original parameters.
All constants in (37) are displayed as exact rationals by the checker.

## 6. Downstream Kato combinations

The positive clock is \(\beta_\mu T=2\pi n+\theta\).  Substitution of
(9) and (36) fixes the downstream combinations

\[
 \widetilde b^\mathrm K_{\mu,\sigma}
 =b^\mathrm K_{\mu,\sigma}-\beta_\mu t^\mathrm K_\mu,
\qquad
 \varrho^\mathrm K_{\mu,\sigma,n}(\theta)
 =\rho^\mathrm K_{\mu,\sigma}(\nu_n)
  -\beta_\mu\tau^\mathrm K_\mu(\nu_n).
\tag{39}
\]

In particular, the first identity in (39) and (8) give the exact
chartwise equality \(\widetilde b^\mathrm K_{\mu,\sigma}
=\gamma_{\mu,\sigma}\).  The finite residual also has the useful exact form

\[
 \varrho^\mathrm K
 =-(\omega-\beta)A\log|\nu_n|
   +(\omega-\beta)AC
   +\arg_\sigma(q-i\nu_n)-\gamma_{\mu,\sigma}.
\tag{39a}
\]

Therefore

\[
 \Delta^\mathrm K(\nu_n)
 =2\pi n+\theta+\widetilde b^\mathrm K+\varrho^\mathrm K,
\tag{40}
\]

the limiting local phase is
\(\phi+\theta+\widetilde b^\mathrm K\), and the finite lifted matching row is

\[
 \psi-\phi-\theta-\widetilde b^\mathrm K-\varrho^\mathrm K=0.
\tag{41}
\]

Applying (26) and (37)--(38) to (39) gives explicit parameter/\(\theta\)
derivative bounds through order two.  Since
\(\alpha/\beta\le9/8\), \(2\pi<8\),
\(c^\mathrm K\ge35/2^{53}\), and \(|\alpha\tau|<3/64\), formula (36)
gives \(1+|\log|\nu_n||<28(n+1)<64(n+1)\) for \(n\ge2\).  The resulting
recurrence has the form

\[
 |D^{\le2}_{\theta,\mu}\varrho^\mathrm K_{\mu,\sigma,n}|
 \le C_\varrho(1+n)^3\,16^{-n},
\tag{42}
\]

with the exact rational \(C_\varrho\) generated from (25), (35), and (37).
In particular \(\varrho^\mathrm K\to0\) uniformly with two parameter
derivatives.  This is weighted-log regularity; it is not ordinary smooth
extension of the remainders through \(\nu=0\).

Finally, (2), (17), the weighted-log endpoint argument above, and
\(|\arg_\sigma|<4\) give the auxiliary-section comparison

\[
 |\Delta^\mathrm K-\beta_\mu T|<5.
\tag{43}
\]

Freeze the turn count by
\(\Delta^\mathrm K=2\pi n^\mathrm K+\vartheta\),
\(\vartheta\in[0,2\pi)\).  Then
\(|n^\mathrm K-\Delta^\mathrm K/(2\pi)|<1\), so

\[
 \left|n^\mathrm K-\frac{\beta_\mu}{2\pi}T\right|<2.
\tag{44}
\]

This is the local radial-section input to the physical residence comparison.
The latter also contains the two finite slide times and is closed only after
`V2.CHART.PHYSICAL_SLIDES`; (44) is not stated as that later physical result.

## 7. Claim boundary

Equations (9), (26), (28), (32), (36), and (39)--(44) establish a local
mathematical `PASS` for `V2.CHART.WEIGHTED_PASSAGE` on the complete frozen
parameter bridge and both signed components.  They do not validate physical
face transversality or slide times, a finite overlap atlas, the physical
winding/residence comparison, the event atlas, positive ends, temporal
stability, Turing selection, or canard identification.  The parent
`V2.EXACT_CHART` remains open and the repository aggregate remains
non-claim-bearing until all required children and the independent replay
policy pass.
