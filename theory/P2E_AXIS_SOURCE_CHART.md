# A direct zero-energy source chart and the axis-skeleton criterion

**Proof contract:** `rfsn-vdp-p2e-axis-source-chart/1`

**Status.**  This note proves a local, application-owned lemma used to
materialize the P2e first-event arrangement.  It does not prove any first-hit
assignment.  Its purpose is twofold: to give a nonsingular physical
zero-energy enclosure of the true outgoing source circle, and to record why a
strict event census on the zero-action skeleton is enough for Theorem V2.

## 1. Setting

Work on the v2 comparison bridge

\[
 0\le r\le \frac1{50},\qquad |a_2|\le\frac14,
 \qquad \frac45\le\epsilon\le\frac65.
\tag{1}
\]

The P2b coordinates are \((u,s)=(u_1,u_2,s_1,s_2)\).  Write

\[
 a_\mu=1+\sqrt{\epsilon}\,r^3a_2,
 \qquad
 b_\mu=\frac{\sqrt{\epsilon}\,r^2}{3},
 \qquad
 c_\mu=2ra_2+\sqrt{\epsilon}\,r^4a_2^2,
 \qquad
 h_\mu=2\alpha_\mu\beta_\mu>0.
\]

The restricted P2bK bounds give
\(h_\mu>2(699/1000)^2=488601/500000\).  The shifted Hamiltonian
pulled back by the linear map (3) below is

\[
 (\widehat H_\mu\circ T_\mu)(u,s)
 =-2h_\mu(u_1s_2+u_2s_1)
   -\frac {a_\mu}3(u_1+s_1)^3
   +\frac {b_\mu}4(u_1+s_1)^4.
\tag{2}
\]

The physical central variables are obtained by the invertible linear map

\[
 T_\mu(u,s)=
 \begin{pmatrix}
 u_1+s_1\\
 \alpha_\mu u_1-\beta_\mu u_2-\alpha_\mu s_1+\beta_\mu s_2\\
 \frac {c_\mu}2(u_1+s_1)+h_\mu(u_2+s_2)\\
 \alpha_\mu u_1+\beta_\mu u_2-\alpha_\mu s_1-\beta_\mu s_2
 \end{pmatrix}
 =:(U,P,V,Q).
\tag{3}
\]

Indeed, its determinant in the ordered variables
\((u_1,u_2,s_1,s_2)\) is
\(-8\alpha_\mu\beta_\mu h_\mu\), hence is nonzero on
(1).  These are the same coordinates and Hamiltonian convention used by the
P2b0, P2bK, and P2c calculations.

Let \(H_{10}=(H_{10,1},H_{10,2})\) be the frozen degree-ten graph centre.
The restricted P2b0 result gives

\[
 \lVert H_\mu-H_{10}\rVert_2\le \frac1{200000}
\tag{4}
\]

on the radius-\(1/100\) unstable disk.  The restricted P2bK result fixes the
direct source phase and gives

\[
 |\chi(\mu)|<\frac1{80},\qquad
 u(\theta,\mu)=\frac1{100}R_{\chi(\mu)}e_\theta.
\tag{5}
\]

## 2. The direct chart

For

\[
 \frac{57}{10}\le\theta\le\frac{13}{2},
 \qquad |\eta|<\frac1{100000},
\tag{6}
\]

put

\[
 \begin{aligned}
 u&=\frac1{100}R_{\chi(\mu)}e_\theta,\\
 s_1&=H_{10,1}(u)+\eta,\\
 X&=u_1+s_1,\\
 s_2&=-\frac{u_2}{u_1}s_1
      -\frac{a_\mu X^3}{6h_\mu u_1}
      +\frac{b_\mu X^4}{8h_\mu u_1},\\
 \mathcal E_\mu^0(\theta,\eta)&=T_\mu(u,s).
 \end{aligned}
\tag{7}
\]

### Proposition 1 (zero-energy source chart)

The map \(\mathcal E_\mu^0\) is well defined on (6), analytic in
\((\theta,\eta)\), and \(C^2\) in \(\mu\).  It is an embedding into
\(\widehat H_\mu^{-1}(0)\).  The true P2bK source circle over the proper
phase arc is the graph

\[
 S_\mu(\theta)=\mathcal E_\mu^0
   \bigl(\theta,\eta_\mu(\theta)\bigr),
 \qquad
 \eta_\mu(\theta)
 =H_{\mu,1}(u(\theta,\mu))-H_{10,1}(u(\theta,\mu)),
\tag{8}
\]

and \(|\eta_\mu(\theta)|\le1/200000<1/100000\).

#### Proof

The rational enclosure

\[
 \frac{103993}{16551}<2\pi<\frac{208696}{33215}
\tag{9}
\]

implies, throughout (6),

\[
 |\theta-2\pi|<\frac7{12}.
\]

Together with (5),

\[
 |\theta+\chi-2\pi|
 <\frac7{12}+\frac1{80}
 =\frac{143}{240}<\frac35.
\tag{10}
\]

Since \(\cos x\ge1-x^2/2\), (10) gives

\[
 u_1=\frac1{100}\cos(\theta+\chi-2\pi)
 >\frac1{100}\left(1-\frac12\frac9{25}\right)
 =\frac{41}{5000}>0.
\tag{11}
\]

Thus the denominator in (7) is uniformly separated from zero.
Substituting (7) into (2), the \(u_2s_1\) terms cancel and the remaining
cubic and quartic coefficients are respectively

\[
 -2\left(-\frac16\right)-\frac13=0,
 \qquad
 -2\left(\frac18\right)+\frac14=0.
\]

Hence \(\widehat H_\mu\circ\mathcal E_\mu^0=0\) exactly.

The interval in (6) has length \(4/5<2\pi\), so \(u\) determines
\(\theta\) there.  At fixed \(u\), \(s_1-H_{10,1}(u)=\eta\); consequently
the map in (7) is injective.  Its \(\theta\)-derivative has a nonzero
\(u\)-component, while its \(\eta\)-derivative has zero \(u\)-component and
\(s_1\)-component one.  The two derivatives are independent.  Equation (3)
then preserves injectivity and rank.  This proves the embedding and the
stated regularity.

Finally, the true unstable graph lies on zero energy because energy is
constant on each backward half-orbit and tends to
\(\widehat H_\mu(0)=0\).  At fixed \(u\) and \(s_1\), equation (2) is affine
in \(s_2\), with nonzero coefficient \(-2h_\mu u_1\).  Therefore its unique
zero-energy value of \(s_2\) is exactly (7).  Bound (4) gives (8) and the
strict chart containment.  \(\square\)

## 3. Why the zero-action skeleton is sufficient

The direct chart above is not an off-axis exact-action chart: \(\eta\) is a
graph-error coordinate, not the P2d action \(\nu\).  The exact outgoing
carrier remains

\[
 E_{\rm out}^{\rm dir}(\phi,\nu)
 =E_{\rm out}^{\rm P2d}(\lambda_\mu(\phi),\nu),
\tag{12}
\]

whose \(C^2\) zero-energy embedding and exact signed action have already been
proved.  On \(\nu=0\), (12) is the same true source circle as (8).

The following elementary criterion is the reason no full numerical
materialization of the preselected action radius is needed.

### Proposition 2 (axis-skeleton thickening)

Suppose the finite P2e source cells, return cells, event germs, and finite
pre-event flow tubes have been pulled back to fixed compact domains.  Assume
that, on \(\nu=0\) and uniformly for (1), a rigorous calculation proves:

1. every source point has its declared unique first event;
2. all active conormal ranks, event speeds, containment and flow-domain
   buffers, inactive-face signs, earlier-event exclusions, order gaps away
   from declared ties, aperture separations, anchor-to-boundary distances,
   and the proper-phase-cut gap have a common positive lower bound
   \(m_{\rm ax}>0\);
3. the complete connected-component incidence census and the stated corner
   priority hold, with no unnamed residual component.

Then there is a number

\[
 0<\delta_{\rm ent}\le2^{-55}
\tag{13}
\]

such that the same first-event assignment, incidence complex, priority, and
component census hold on the restriction of (12) to
\(|\nu|<\delta_{\rm ent}\), with all strict normalized margins at least
\(m_{\rm ax}/2\).

#### Proof

There are only finitely many compact domains and normalized quantities in the
hypotheses.  The physical carrier (12), the finite flow, and the pulled-back
event functions are continuous in all variables and have the state-\(C^3\),
parameter-\(C^2\) regularity required by the event theorem.  Uniform
continuity therefore gives one open action neighborhood on which every
strict quantity changes by less than \(m_{\rm ax}/2\).  Positive event speed
and the implicit-function theorem continue each first-hit time uniquely;
the earlier-hit and inactive-face margins prevent a new first event.  The
active-rank and empty-incidence margins give the same neat isotopy and hence
the same connected-component census and corner priority.  Intersect this
finite collection of neighborhoods and then restrict its radius by
\(2^{-55}\).  The result is (13).  \(\square\)

In the high-winding construction, the exact local passage produces action
values tending to zero as the winding label tends to infinity.  After (13)
has been obtained, the winding threshold is increased so that every retained
branch enters this collar.  Thus Theorem V2 and the imported return--exit
theorem require existence of a positive uniform subcollar, not certification
of the whole disk \(|\nu|\le2^{-55}\).

## 4. Claim boundary and next computation

Proposition 1 supplies the missing **exact zero-energy interval enclosure of
the zero-action true source**; it does not pointwise evaluate the unknown
graph \(H_\mu\).  Proposition 2 is a conditional compactness implication.  This
note does not yet provide any of the three exterior first-hit calculations,
the incidence complex, the exhaustive census, the value of \(m_{\rm ax}\),
or the transported traces.  It therefore does not pass
`V2.EVENT_ATLAS`.

The next claim-bearing mathematical computation is the complete
zero-action first-event skeleton.  The selected homoclinic channel is already
available from P2c.  The remaining new integrations are the algebraic and
pole channels, initialized with (7)--(8).  Only if the existing \(H_{10}\)
graph tube wraps too widely should the corresponding local true-graph spine
be tightened by additional shooting.

No temporal-stability, dynamical Turing-selection, or finite-parameter canard
claim follows from either proposition.
