# Universal-core periodic-return certificate

> **Certificate status: PASS.** This source-only bundle validates one
> nonconstant periodic orbit of the universal limiting core and the local
> analytic curve of first reversible returns through it. It is an
> obstruction certificate for a pole-only source-block classification, not
> a global periodic-family cover.

## 1. Certified statement

Consider

\[
 U'=P,\qquad P'=-U^2-V,\qquad V'=Q,\qquad Q'=U
\]

with reverser

\[
 \mathcal R(U,P,V,Q)=(U,-P,V,-Q).
\]

For the exact source value \(V_0=0.08\), define

\[
 F(U_0,T)=
 \begin{pmatrix}P(T;U_0,0,V_0,0)\\Q(T;U_0,0,V_0,0)\end{pmatrix}.
\]

The interval Krawczyk test proves a unique zero in

\[
\begin{aligned}
 U_0&\in
 [0.041783787871385494,\ 0.041783788271385514],\\
 T&\in
 [7.5096097217978439,\ 7.5096097221978457].
\end{aligned}
\]

The endpoint of the whole Krawczyk box is enclosed by

\[
\begin{aligned}
 U(T)&\in[4.8791826426000533,\ 4.8791827107482701],\\
 P(T)&\in[-1.8857889563825820\,10^{-7},
            1.8857942123703354\,10^{-7}],\\
 V(T)&\in[-7.9347845613908898,\ -7.9347843429571459],\\
 Q(T)&\in[-8.6962308512105784\,10^{-8},
            8.6962302773426372\,10^{-8}].
\end{aligned}
\]

The actual root has \(P(T)=Q(T)=0\). Its endpoint is separated from its
source by more than one unit in \(U\), so this is not the trivial
\(T=0\) root.

The exact source energy is enclosed by

\[
 \mathcal E_0\in
 [-0.0067340392484958661,\ -0.0067340391830991502].
\]

Thus this orbit lies on a genuinely nonzero signed-energy level; it is not
one of the zero-energy heteroclinic classes of the desingularized
half-space.

## 2. First positive reversible hit

The root above is not merely an arbitrary later return. It is the first
positive hit of

\[
 \operatorname {Fix}\mathcal R=\{P=Q=0\}.
\]

For \(0\le t\le0.05\), use the fixed block

\[
 [0.041,0.043]\times[-0.005,0]\times
 [0.079,0.081]\times[0,0.003].
\]

On this block,

\[
 -0.082849\le P'=-U^2-V\le-0.080681.
\]

The integral changes over time \(0.05\) are at most \(0.00025\) in
\(U\), \(0.00414245\) in \(P\), \(0.00015\) in \(V\), and \(0.00215\)
in \(Q\). They are strictly smaller than the corresponding face
margins. A no-first-exit argument therefore keeps the orbit in the block
and gives \(P(t)<0\) for \(0<t\le0.05\).

The outward-rounded CAPD tube cover then proves

\[
\begin{aligned}
 P(t)&\in[-0.19951202994639897,-0.0040880219580392112],
       &&0.05\le t\le2,\\
 Q(t)&\in[-3.1557213128281569,-0.033687513004263044],
       &&2\le t\le7.49.
\end{aligned}
\]

Finally, on the complete tube

\[
 7.49\le t\le 7.5096097221978457
\]

the certificate gives

\[
 U(t)\in[4.8522803334469549,4.9059502139315816].
\]

At the exact root \(Q(T)=0\), and \(Q'=U>0\) on this final tube.
Consequently \(Q(t)<0\) for \(7.49\le t<T\). The four intervals cover
all \(0<t<T\), and on each one either \(P\) or \(Q\) is strictly nonzero.
There is no earlier simultaneous symmetry hit.

## 3. Transversality and the periodic extension

On the complete root box,

\[
 D_{(U_0,T)}F\subset
 \begin{pmatrix}
 [925.94486566632031,925.945113365471]&
 [-15.871639581907692,-15.871638698458748]\\
 [-429.77469249063961,-429.77463929054551]&
 [4.8791826426000533,4.8791827107482701]
 \end{pmatrix},
\]

and

\[
 \det D_{(U_0,T)}F
 \in[-2303.3749040728944,-2303.372408345318].
\]

The determinant excludes zero. Since the field is analytic, the implicit
function theorem gives a locally unique analytic curve
\((U_0(V_0),V_0)\) of first reversible returns and an analytic half-period
\(T(V_0)\). The strict first-hit margins persist on a smaller
neighborhood.

Let \(z_0,z_1\in\operatorname {Fix}\mathcal R\) be the source and endpoint
of the certified half-orbit. For \(T\le t\le2T\), define

\[
 \widetilde z(t)=\mathcal R z(2T-t).
\]

Reversibility gives

\[
 D\mathcal R\,X(z)=-X(\mathcal R z).
\]

Hence the one-sided derivatives at \(t=T\) agree. The reflected path is a
\(C^1\) solution of the same ODE, and uniqueness identifies it with the
forward continuation from \(z_1\). At \(2T\) it returns to \(z_0\), with
matching derivative for the next period. The certified period enclosure is

\[
 2T\in[15.019219443595688,15.019219444395691].
\]

No assertion that this is the least period is needed.

## 4. Krawczyk and tube implementation

periodic_return_probe.cpp uses FILIB outward-rounded intervals and CAPD
high-order sets. It evaluates the center residual, encloses the full
two-variable Jacobian, and verifies

\[
 K(X)\subset\operatorname {int}X
\]

with maximum component ratio

~~~text
0.0020827689725154432
~~~

The time column is the exact field at the enclosed endpoint. The
initial-\(U\) column is the CAPD first variation. The same source box is
then replayed through byte-adjacent time cells for the first-hit sign
cover. Every failure exits nonzero; PASS is printed only after all
existence, sign, endpoint-separation, determinant and energy checks pass.

## 5. Clean replay

The recorded environment is

~~~text
g++ 15.2.0
CAPD 2.5.1, git 731079217a9254ea2948d742df2b170895effe7f
CAPD_INTERVAL_TYPE=FILIB
~~~

From the repository root:

~~~bash
PAPERA_CAPD_CONFIG=/tmp/papera-capd.bKwHIQ/CAPD/build/bin/capd-config

g++ -std=c++17 \
  validation/universal-core-periodic-return/periodic_return_probe.cpp \
  $("$PAPERA_CAPD_CONFIG" --cflags) \
  $("$PAPERA_CAPD_CONFIG" --libs) \
  -O2 -o /tmp/papera-periodic-return-probe

/tmp/papera-periodic-return-probe
~~~

The claim-bearing source hash is recorded in certificate.json.
Executables and caches are rebuild products and are not tracked.

## 6. Evidence boundary

This bundle proves one first-return point and its local analytic
periodic-return stratum. It does not continue that stratum across a source
block, locate all of its folds or endpoints, or exclude additional
periodic, multipulse, homoclinic or pole-boundary strata. Those are now
mandatory parts of any complete source-block itinerary theorem which
contains this source point.
