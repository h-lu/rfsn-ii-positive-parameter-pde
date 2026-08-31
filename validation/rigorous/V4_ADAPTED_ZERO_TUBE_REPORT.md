# V4 zero-energy adapted spectral tube interval proof

**Result:** local mathematical **PASS** on the complete frozen v2 parameter
box. This is a current-computer, non-claim-bearing interval proof of a
scaled V4 subgraph designed for the \(R=2\) V5 attachment.

## Object and exact coordinates

On \(H=0\), write the V5 scaled V4 coordinates as

\[
 A=\alpha/\delta,\qquad B=\beta/\delta,\qquad
 C=A+B,\qquad D=A-B,
\]

and set

\[
 \lambda=\sqrt{1-z^2},\qquad
 \chi_0=\sqrt{\frac{\epsilon}{6}(1-z)^3(5z+3)},\qquad
 C_0=\frac{z^2\chi_0}{1-z^2}.
\]

The interval probe uses the spectral coordinates

\[
 C=C_0+b+n,\qquad D=\lambda(n-b),
\tag{1}
\]

or equivalently

\[
 b=\frac{(C-C_0)-D/\lambda}{2},\qquad
 n=\frac{(C-C_0)+D/\lambda}{2}.
\tag{2}
\]

The verified product corridor is

\[
\begin{gathered}
 r\in[1/100,1/50],\qquad a_2\in[-1/4,1/4],\qquad
 \epsilon\in[4/5,6/5],\\
 0\le z\le2/9,\qquad -1/16\le b\le1/16,
 \qquad |n|\le10^{-5},\qquad H=0.
\end{gathered}
\tag{3}
\]

The positive root \(\chi\) is obtained from the exact scaled energy equation
V5(25), not from an asymptotic truncation. With \(S=\chi+C\), the exact
scaled V4 field V5(24) gives

\[
 \dot z=-\delta Sz^3,\qquad
 \dot C=D+\delta z^2\{-\epsilon(1-az)+2\chi S\},
\]

\[
 \dot D=C-z^2S-\delta z^2SD.
\tag{4}
\]

The pullback of (4) through (1) includes the moving-frame terms

\[
 \dot b+\dot n=\dot C-C_{0,z}\dot z,
\qquad
 \dot n-\dot b=
 \frac{\dot D-\lambda_z\dot z(n-b)}{\lambda}.
\tag{5}
\]

Both \(C_{0,z}\) and \(\lambda_z=-z/\lambda\), and all first derivatives of
the resulting \((z,b,n)\) field, are evaluated by interval automatic
differentiation. To retain the exact spectral cancellation in interval
arithmetic, the implementation simplifies (5) to its diagonal
\(-\lambda b,+\lambda n\) part plus explicit perturbations. It also uses

\[
 \chi-\chi_0=\frac{\chi^2-\chi_0^2}{\chi+\chi_0}
\]

with the numerator expanded exactly in \(\delta\) and \(a-1\). Thus no
small face margin is inferred by subtracting two broad, correlated interval
expressions.

The gap-free cover has \(4\times8\times4\) parameter parents, 64 exact
rational \(z\)-slabs, and eight exact rational \(b\)-slabs: 65,536 product
cells. Every PASS margin uses outward-rounded FILIB intervals.

## Verified margins

The exact positive-root checks give

| Quantity | Rigorous enclosure or lower bound |
|---|---:|
| \(\lambda\) | \([0.974996043043569,1.0000000000000002]\) |
| \(\chi_0\) | \([0.5067728301887013,0.7768347457614284]\) |
| positive \(\chi\) | \([0.48696930116020215,0.7745967340959595]\) |
| implicit \(\chi\)-derivative | \(\ge0.9739386021790929\) |
| \(S=\chi+C\) | \(\ge0.44992788442096754\) |
| \(\pi=\delta S\) | \(\ge4.499292684411786\times10^{-5}\) |

The isolating faces satisfy

| Face | Rigorous oriented margin |
|---|---:|
| \(z=2/9\), inward | \(\ge4.956634102721107\times10^{-7}\) |
| \(b=+1/16\), inward | \(\ge0.06093609722412052\) |
| \(b=-1/16\), inward | \(\ge0.060934688613695595\) |
| \(n=+10^{-5}\), outward | \(\ge6.58714247519958\times10^{-6}\) |
| \(n=-10^{-5}\), outward | \(\ge7.95713862997435\times10^{-6}\) |

The face \(z=0\) is exactly invariant. For base \(X=(z,b)\) and normal
fiber \(n\), the generator blocks obey

\[
 \mu_2(C)\le0.007123583231771524,\qquad
 \lVert B\rVert\le2.0596734224566705\times10^{-5},
\]

\[
 \lVert D\rVert\le4.2607741453642645\times10^{-5},\qquad
 a_n\ge0.9749960629973755.
\]

All comparisons with \(\nu=1/64\) and
\(\lambda_*=\sqrt{1-(2/9)^2}\) are strict. The directly evaluated
slope-one cone margin is at least \(0.9678153484510067\), while the sharper
slope-\(1/2\) cone margin is at least \(0.48389149165198553\).  The normal
rate is at least \(0.9749774325505001\), and

\[
 (\gamma_0,\gamma_1,\gamma_2,\gamma_3)
 \ge(0.9749774326,0.9678373946,0.9606971309,0.9535568672).
\]

The corridor graph lemma, run in the invariant slope-\(1/2\) cone,
therefore gives a unique maximal future-staying graph

\[
 n=\Gamma_{\rm ad}(z,b;r,a_2,\epsilon)
\tag{6}
\]

inside (3), normally expanding and third-order bunched, with
\(\lvert\partial_b\Gamma_{\rm ad}\rvert\le1/2\). This is the exact scaled
V4 field. For \(r>0\), blowing down by
\(\alpha=\delta A,\ \beta=\delta B\) makes (6) a V4 subgraph; wherever it
overlaps the previously certified unscaled V4 corridor, uniqueness
identifies the two graphs. The present calculation does **not** claim that
the whole broad \(b\)-tube blows down into the earlier
\(|\alpha|,|\beta|\le10^{-5}\) product collar.

## \(R=2\) attachment enclosure

At the resolved-\(K_1\) cut \(r_1=R=2\), the exact transition V5(37) is

\[
 z_R=(1+4\sqrt\epsilon)^{-1},\qquad
 C=2\epsilon\Pi-\chi,\qquad D=4\epsilon z_R\Omega,
\]

and
\(\chi=8z_R^2\epsilon^{3/2}q_1\). Evaluating these identities on the
graph tube gives

\[
 z_R\in[0.18581211318908392,0.21844989525420885]
 \subset(0,2/9),
\]

\[
 \Pi\in[0.23461655885573995,0.4107118470903572],
\]

\[
 \Omega\in[-0.09160240283250262,0.09160240283250262],
\qquad
 q_1\in[1.4991597239504855,2.277067671626218].
\tag{7}
\]

Thus (6)--(7) provide a strict narrow-normal V4 attachment tube on the
actual parameter-dependent \(R=2\) section.

### Full-base terminal graph for the strict \(K_1\) corridor

Restrict the stable V4 coordinate at \(R=2\) to

\[
 |b_{\rm out}|\le1/3000,qquad |n_{\rm out}|\le10^{-5}.
\tag{8}
\]

Because (6) is a graph over \((z,b_{\rm out})\), its restriction to (8)
is an actual subordinate piece of the V4 graph.  Let \(P-K,W\) and
\(\lambda_1\) be the finite-\(\sigma\) \(K_1\) reference used in the strict
K1 corridor.  The exact seam identities include

\[
 \sqrt{1-z_R^2}=2z_R\lambda_1,
 \qquad \frac{C_0+\chi_0}{2\epsilon}=P.
\tag{9}
\]

The code rationalizes both \(\chi-\chi_0\) and the change from
\((C_0,0)\) to \((C,D)\) before applying (9).  It therefore evaluates the
K1 spectral coordinates without subtracting broad \(\Pi\)- and
\(\Omega\)-boxes.  On the whole v2 parameter box and the full product (8),

\[
 b_{K_1}\in[-2.082790310696704,2.087206773674565]\times10^{-4},
\]

\[
 n_{K_1}\in[-6.637293639326057,6.195704783142731]\times10^{-6}.
\tag{10}
\]

The broad \(b_{K_1}\) interval in (10) is deliberately **not** claimed to
lie inside the K1 tube.  What is needed is base coverage.  At the two
outer endpoints of (8), interval evaluation for every
\(|n_{\rm out}|\le10^{-5}\) gives

\[
 b_{K_1}(-1/3000)
 \subset[-2.082790310696698,-1.3862182635633312]\times10^{-4},
\]

\[
 b_{K_1}(1/3000)
 \subset[1.3892821778600141,2.0872067736744997]\times10^{-4}.
\tag{11}
\]

Thus the left and right endpoints strictly cross
\(-27/200000=-1.35\times10^{-4}\) and
\(+27/200000=+1.35\times10^{-4}\), with respective margins
\(3.62182635633312\times10^{-6}\) and
\(3.92821778600141\times10^{-6}\).  Throughout (8), the normal coordinate
stays inside the K1 tube \(|n_{K_1}|<1/12500\) with margin
\(7.33627063606739\times10^{-5}\).

It remains to verify that this crossing is a graph crossing.  Let
\(p=dn_{\rm out}/db_{\rm out}\), and put
\(h_b=\partial_{b_{\rm out}}\chi\),
\(h_n=\partial_{n_{\rm out}}\chi\).  Differentiating only after using the
first identity in (9) gives the cancellation-free exact formulas

\[
 \frac{db_{K_1}}{db_{\rm out}}
 =\frac{2+h_b+p h_n}{4\epsilon},\qquad
 \frac{dn_{K_1}}{db_{\rm out}}
 =\frac{2p+h_b+p h_n}{4\epsilon}.
 \tag{12}
\]

For every \(|p|\le1/2\), the first derivative in (12) is at least
\(0.4166663644575796\).  With \(\kappa=7/10\), the two light-cone margins

\[
 \kappa\frac{db_{K_1}}{db_{\rm out}}
 \mp\frac{dn_{K_1}}{db_{\rm out}}
\]

are at least \(0.08333094850154998\) and
\(0.08333281957788538\).  Consequently the seam map is strictly monotone
on the actual V4 graph and sends its tangent strictly into the K1
slope-\(7/10\) cone.  Taking the unique inverse image of
\(|b_{K_1}|\le27/200000=1.35\times10^{-4}\) therefore yields an admissible terminal graph over
the **entire** K1 top base, with \(|n_{K_1}|<1/12500\).  This closes the
value, domain-coverage, and tangent parts of the V4-to-K1 seam.  It does not
yet transport that graph to the central cut, identify the source first hit,
or prove the V5 scalar coincidence root.

## Reproduction and claim boundary

The source is
[vdp_v4_adapted_zero_tube_probe.cpp](src/vdp_v4_adapted_zero_tube_probe.cpp),
and its compiled-output checks are in
[test_v4_adapted_zero_tube_probe.py](tests/test_v4_adapted_zero_tube_probe.py).
Run

    python3 -B -m unittest \
      validation.rigorous.tests.test_v4_adapted_zero_tube_probe -v

with the pinned strict CAPD/FILIB build, or set RFSN_CAPD_CONFIG to its
capd-config. All seven mathematical obligations and all four tests pass.

The machine field **claim_bearing=false** records that this local theorem is
not by itself the aggregate Issue #7 release certificate.  Separate
non-claim-bearing certificates now treat the resolved-\(K_1\) backward graph
transport, central regraph, and representative source incidence.  Their
complete-box claim-bearing composition and the aggregate release remain open.
