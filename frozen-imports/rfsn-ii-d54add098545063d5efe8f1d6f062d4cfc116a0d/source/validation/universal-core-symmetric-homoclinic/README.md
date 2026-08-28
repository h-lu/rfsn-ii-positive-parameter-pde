# Paper A symmetric saddle-focus homoclinic certificate

This source-only bundle validates a primary reversible homoclinic orbit for

\[
 U'=P,\qquad P'=-U^2-V,\qquad V'=Q,\qquad Q'=U,
 \qquad \mathcal R(U,P,V,Q)=(U,-P,V,-Q).
\]

The first integral is

\[
 \mathcal E=Q^2-P^2-\frac23U^3-2UV.
\]

The conclusion is local to one shooting box.  It does not claim global
uniqueness of homoclinic orbits or identify the independently validated
periodic-return point at \(V=.08\) with a particular member of the local
blue-sky family.

## Certified statement

Let \(H_{\mathrm{true}}\) be the actual local unstable graph over
\(\|u\|_2\le.01\) in the exact hyperbolic coordinates used by the sibling
[origin-algebraic-heteroclinic](../origin-algebraic-heteroclinic/README.md)
certificate.  On the source circle

\[
 u_\rho(\phi)=.01(\cos\phi,\sin\phi),\qquad
 s_\rho(\phi)=H_{\mathrm{true}}(u_\rho(\phi)),
\]

there is a unique root in the reported box of

\[
 (P,Q)\bigl(\Phi^T(z_\rho(\phi))\bigr)=0.
\]

The root satisfies

\[
\begin{aligned}
 \phi&\in[5.8615055856447817,5.8615055856450482],\\
 T&\in[9.6374420678958099,9.6374420678971511],
\end{aligned}
\]

and its nonzero symmetry endpoint obeys

\[
\begin{aligned}
 U(T)&\in[4.8785234574459304,4.8785234988116768],\\
 V(T)&\in[-7.9333304994224827,-7.933330385013492].
\end{aligned}
\]

There is no earlier nonzero hit of \(\operatorname {Fix}\mathcal R\) on the
half-orbit from the origin.  Reflection at the endpoint therefore gives a
symmetric orbit homoclinic to the saddle-focus at the origin.

The shooting determinant and the endpoint phase column satisfy

\[
\begin{aligned}
 \det D_{(\phi,T)}(P,Q)(T)
 &\in[149.56393055300413,149.56404227745782],\\
 \partial_\phi U(T)
 &\in[-10.889708535478462,-10.8897049543477],\\
 \partial_\phi V(T)
 &\in[35.417125972639965,35.417127394127888].
\end{aligned}
\]

Consequently \(W^u(0)\) and \(W^s(0)\) meet precisely in the flow direction
inside the regular zero-energy hypersurface along this orbit.  This is the
standard nondegeneracy condition for a reversible bifocal homoclinic.

## Robust true-graph quantifier

The sibling local-graph theorem proves, on the complete disk,

\[
 \|H_{\mathrm{true}}-H_{10}\|_2\le10^{-20},\qquad
 \|D(H_{\mathrm{true}}-H_{10})\|_{2\to2}\le10^{-18}.
\]

The probe does not replace \(H_{\mathrm{true}}\) by \(H_{10}\).  Its center
residual starts from the full \(C^0\) uncertainty box.  Its interval
Jacobian starts from the full phase box and includes both the \(C^0\)
uncertainty and the directional derivative error

\[
 10^{-18}\|\partial_\phi u_\rho\|_2=10^{-20}.
\]

CAPD encloses the flow and first variation for every state in these boxes and
every time in the time box.  Thus the reported Krawczyk inclusion is uniform
over the proved true-graph budgets and applies, in particular, to the fixed
actual invariant graph.  The maximum component inclusion ratio is

~~~text
0.00075317389968221045
~~~

The corresponding weighted Krawczyk contraction ratio is

~~~text
0.000001754824157736503
~~~

The independent error boxes are an enclosure device for this one fixed
invariant graph.  They are not a claim that an arbitrary, independently
chosen \(C^0/C^1\) perturbation is invariant or has zero energy.

## First symmetry hit

For the complete Krawczyk phase box and true-graph uncertainty, outward-
rounded trajectory tubes give

\[
\begin{array}{c|c|c}
 \text{time interval}&\text{strict component}&\text{validated hull}\\ \hline
 [0,1.65]&P>0&
 [0.00077888803393185845,0.01080525704061586]\\
 [1.65,1.75]&Q>0&
 [0.031929280244111596,0.034312536807053172]\\
 [1.75,7.35]&P<0&
 [-0.42925878222161701,-0.0016014894439174334]\\
 [7.35,9.55]&Q<0&
 [-3.1601535680919888,-0.42289548940031896].
\end{array}
\]

The point \(t=0\) is checked directly.  Because CAPD interprets an interval
time with left endpoint zero as a zero-time request, the whole first cell is
instead covered by stepwise dense output from the point time \(0\) to the
point time \(.05\), checking every last-step enclosure.  The subsequent
ordinary cells begin at \(.05\).  Thus the table genuinely covers the whole
interval and does not silently replace \((0,.05]\) by the initial state.

On the final tube from \(9.55\) through the upper time endpoint,

\[
 U\in[4.7311247770137683,5.0218508349719926].
\]

Since \(Q'=U>0\) there and the exact root has \(Q(T)=0\), it follows that
\(Q(t)<0\) for \(9.55\le t<T\).

The portion before the source circle is excluded analytically.  In the local
coordinates, \(P=Q=0\) implies \(u=s\), while the sibling graph proof gives
\(\|s\|_2<\frac14\|u\|_2^2\) for
\(0<\|u\|_2\le.01\).  Hence the local unstable orbit cannot meet
\(\operatorname {Fix}\mathcal R\) away from the origin.

## Nondegeneracy

At the endpoint let

\[
 L=\operatorname {Fix}D\mathcal R,\qquad
 K=\operatorname {Fix}(-D\mathcal R),\qquad
 E=T_cW^u(0).
\]

The two shooting columns are the \(K\)-projections of the transported phase
tangent and the vector field.  The nonzero determinant makes
\(\pi_K|_E\) an isomorphism, so \(E\) is the graph of a map
\(A:K\to L\).  Energy conservation forces \(\operatorname {rank}A\le1\);
the sign-definite \(L\)-phase column forces \(\operatorname {rank}A=1\).
Since \(D\mathcal R\) changes the sign of \(K\),

\[
 E\cap D\mathcal R(E)=\ker A=\operatorname {span}\{X(c)\}.
\]

The orbit lies on \(\mathcal E=0\) because it lies in \(W^u(0)\).  At its
nonzero symmetry endpoint this also gives the exact relation
\(V=-U^2/3\); the displayed correlation-blind energy interval in the replay
is not used to infer conservation.

## Clean replay

The recorded environment is

~~~text
g++ 15.2.0
CAPD 2.5.1, git 731079217a9254ea2948d742df2b170895effe7f
CAPD_INTERVAL_TYPE=FILIB
~~~

From the repository root:

~~~bash
PAPERA_CAPD_CONFIG=/path/to/capd-config
PAPERA_BUILD_DIR=$(mktemp -d)

g++ -std=c++17 \
  validation/universal-core-symmetric-homoclinic/homoclinic_interval_probe.cpp \
  -Ivalidation/origin-algebraic-heteroclinic \
  $($PAPERA_CAPD_CONFIG --cflags) -O0 \
  $($PAPERA_CAPD_CONFIG --libs) \
  -o "$PAPERA_BUILD_DIR/homoclinic_interval_probe"

"$PAPERA_BUILD_DIR/homoclinic_interval_probe"
~~~

The executable is built outside the source directory.  Every failed
Krawczyk, determinant, phase-column, endpoint or first-hit test exits
nonzero.
