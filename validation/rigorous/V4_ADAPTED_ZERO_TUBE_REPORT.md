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
slope-one cone margin is at least \(0.9678153484510067\), the normal rate
is at least \(0.9749774325505001\), and

\[
 (\gamma_0,\gamma_1,\gamma_2,\gamma_3)
 \ge(0.9749774326,0.9678373946,0.9606971309,0.9535568672).
\]

The corridor graph lemma therefore gives a unique maximal future-staying
graph

\[
 n=\Gamma_{\rm ad}(z,b;r,a_2,\epsilon)
\tag{6}
\]

inside (3), normally expanding and third-order bunched. This is the exact
scaled V4 field. For \(r>0\), blowing down by
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
actual parameter-dependent \(R=2\) section. They do not select a point of
that graph, transport it through the resolved \(K_1\) block, or prove the
V5 scalar coincidence root.

## Reproduction and claim boundary

The source is
[vdp_v4_adapted_zero_tube_probe.cpp](src/vdp_v4_adapted_zero_tube_probe.cpp),
and its compiled-output checks are in
[test_v4_adapted_zero_tube_probe.py](tests/test_v4_adapted_zero_tube_probe.py).
Run

    python3 -B -m unittest \
      validation.rigorous.tests.test_v4_adapted_zero_tube_probe -v

with the pinned strict CAPD/FILIB build, or set RFSN_CAPD_CONFIG to its
capd-config. All five mathematical obligations and all four tests pass.

The machine field **claim_bearing=false** records that this local theorem is
not yet the aggregate Issue #7 release certificate. V5 incidence and its
scalar root, resolved-\(K_1\) graph transport, and the aggregate release
remain open.
