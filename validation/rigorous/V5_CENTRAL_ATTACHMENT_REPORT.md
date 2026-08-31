# V5 resolved-(K_1)-to-central attachment interval proof

**Result:** local mathematical **PASS** on the complete frozen v2 parameter
box.  This current-computer, non-claim-bearing certificate proves the exact
zero-energy lower-face coordinate attachment at \(U=-4\).  It supplies a
fixed central patch, strict transition and section transversality, and a
uniform central regraph for every lower \(K_1\) graph whose slope is at most
\(7/10\).  It does not compute that transported graph or prove a source
incidence.

## Exact transition being checked

Put

\[
 m=4+ra_2,\qquad \sigma=m^{-1/2},\qquad
 r_1=r\sqrt m,\qquad s=\sqrt\epsilon,\qquad
 \kappa=\epsilon^{1/4}.
\]

The lower face of the resolved \(K_1\) corridor is therefore exactly the
fixed central section \(U=-4\).  For

\[
 x=sr^2m,\qquad D=2+x,\qquad
 q_0=\sqrt{\frac{8+3x}{6s}},\qquad P_0=\frac{q_0}{D},
\]

\[
 K=\frac{ra_2(x+3)}{3smq_0D},\qquad
 W=\frac{x+4}{3mD^3},
\]

set

\[
 \Pi=P_0-K+b+n,\qquad
 \Omega=W+\lambda(n-b),\qquad
 \lambda=\sqrt{sD}.
\]

the exact \(K_1\to K_2\) transition is

\[
\begin{aligned}
 P&=-\kappa\sqrt m\,\Pi,\\
 V&=r^2a_2^2+\frac{s}{3}r^5a_2^3-m^2
       -\frac{s}{3}r^2m^3+m\Omega,\\
 Q&=-\kappa m^{3/2}q_1,\qquad \widehat H=H.
\end{aligned}
\tag{1}
\]

Here \(q_1>0\) is the exact \(H=0\) root of V5(34), not a leading-order
replacement.  The code first sets \(r_1=r\sqrt m\) and
\(\sigma=m^{-1/2}\), then evaluates the same cancellation-free
\(\bar q^2+R\) representation used by the finite-\(K_1\) corridor.  In
particular, powers such as \(r_1\sigma^7=r/m^3\) are simplified before
interval evaluation.  This prevents artificial dependence width at the
lower face.

The verified domain is

\[
 r\in[1/100,1/50],\quad a_2\in[-1/4,1/4],\quad
 \epsilon\in[4/5,6/5],\quad |b|,|n|\le10^{-4},\quad H=0.
\tag{2}
\]

## Gap-free FILIB cover and fixed patch

The outward-rounded cover uses \(8\times32\times8\) parameter slabs and
\(8\times8\) spectral-coordinate slabs, for 131,072 cells.  It gives

| Quantity | Rigorous enclosure |
|---|---:|
| \(q_1^2\) | \([1.2153861649718485,1.4945695264767829]\) |
| \(q_1\) | \([1.1024455383246141,1.2225258796756753]\) |
| \(\Pi\) | \([0.5505700885800305,0.6110404847818331]\) |
| \(P\) | \([-1.172895988468279,-1.1359083921385433]\) |
| \(V\) | \([-15.884308229274515,-15.799158040040863]\) |
| \(Q\) | \([-9.391877098118364,-9.090723367061457]\) |

Thus every point lies strictly in the parameter-independent rectangle

\[
 P\in[-6/5,-11/10],\qquad
 V\in[-16,-31/2],\qquad
 Q\in[-19/2,-9].
\tag{3}
\]

The smallest signed boundary margins in the \((P,V,Q)\) directions are,
respectively,

\[
 0.027104011531720484,\qquad
 0.1156917707254852,\qquad
 0.09072336706145734.
\]

The fixed section and the energy coordinate are uniformly transverse:

\[
 |P|\ge1.1359083921385433,
 \qquad |Q|\ge9.090723367061457.
\tag{4}
\]

## Regular transition and central regraph

At fixed \((r,a_2,\epsilon)\), the \((\Pi,\Omega)\mapsto(P,V)\) chart
block has absolute determinant

\[
 \kappa\sigma^{-3}=\kappa m^{3/2}
 \in[7.5517511819781555,8.388785547308327].
\tag{5}
\]

Because \(\widehat H=H\), the energy direction introduces no further
degeneracy.  In the spectral coordinates \((b,n)\), write

\[
 A=\kappa\sqrt m,\qquad K=m\lambda.
\]

The \((b,n)\mapsto(P,V)\) derivative has rows
\((-A,-A)\) and \((-K,K)\).  Its absolute determinant satisfies

\[
 2AK\in[20.20698465058045,24.84447648071631].
\tag{6}
\]

Now let the lower trace be any \(C^1\) graph \(n=g(b)\) in the certified
\(K_1\) cone, so \(|g'|\le\rho=7/10\).  Then

\[
 -\frac{dV}{db}=K(1-g')\ge K(1-\rho)
 \ge1.6034738513045657>0,
\tag{7}
\]

and it can be regraphed in the universal central coordinates as \(P=G(V)\).
Monotonicity of \((1+g')/(1-g')\) gives

\[
 |G_V|\le \frac AK\frac{1+\rho}{1-\rho}
 \le2.0348531377655257<2.221.
\tag{8}
\]

This is a universal cone-to-regraph statement, so it applies in particular
to the actual lower graph once its backward transport through the separate
finite-(K_1) corridor is invoked.  It does not replace an enclosure of the
values of that graph.

## Reproduction and claim boundary

The source is
[vdp_v5_central_attachment_probe.cpp](src/vdp_v5_central_attachment_probe.cpp),
and its compiled checks are in
[test_v5_central_attachment_probe.py](tests/test_v5_central_attachment_probe.py).
Run

    python3 -B -m unittest \
      validation.rigorous.tests.test_v5_central_attachment_probe -v

with the pinned strict CAPD/FILIB build, or set `RFSN_CAPD_CONFIG` to its
`capd-config`.

The machine field `claim_bearing=false` is deliberate.  The certificate
closes the exact value, regularity, transversality, and cone-to-regraph
parts of the lower coordinate transition.  Still open are an explicit
enclosure of the transported lower graph, its first hit by the canonical
source manifold, and the V5 scalar incidence equation.  No time stability,
Turing selection, or canard conclusion is asserted here.
