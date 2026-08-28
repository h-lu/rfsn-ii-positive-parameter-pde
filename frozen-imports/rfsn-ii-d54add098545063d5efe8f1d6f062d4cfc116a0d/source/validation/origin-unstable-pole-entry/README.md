# True origin-unstable pole-entry sector

> **Certificate status: PASS.**
>
> This source-only CAPD/FILIB package proves one open phase interval on the
> true local unstable manifold of the origin.  It is not an all-phase
> classification, does not use the raw-crest source family, and does not
> identify either of the separately certified algebraic or homoclinic
> phases with a pole orbit.

## Certified statement

For

\[
 U'=P,\qquad P'=-U^2-V,\qquad V'=Q,\qquad Q'=U,
\]

use the exact saddle-focus coordinates

\[
\begin{aligned}
 U&=u_1+s_1,&V&=u_2+s_2,\\
 P&=2^{-1/2}(u_1-s_1-u_2+s_2),&
 Q&=2^{-1/2}(u_1-s_1+u_2-s_2).
\end{aligned}
\]

Let the true local unstable manifold be `s=H(u)` on
`||u||_2<=0.01`, and parameterize its fundamental circle by

\[
 u=.01(\cos\phi,\sin\phi),\qquad s=H(u).                \tag{1.1}
\]

Every source in the closed cover

\[
 -.2\le\phi\le .2                                      \tag{1.2}
\]

has a first encounter with the section `x=-U=10` in forward time.  In pole
coordinates `(x,y,q,w)=(-U,-P,-Q,-V)`, the complete cover satisfies

\[
\begin{aligned}
 \tau_{10}&\in[10.885720013440157,11.579632102474379],\\
 y&\in[26.310478749525817,27.494382470947933],\\
 q&\in[0.53346508756932065,0.75493829392450185],\\
 w&\in[-4.0349622880941558,-2.1775266426859745].        \tag{1.3}
\end{aligned}
\]

For `theta=1/2`, put

\[
 D=\tfrac12x^2-w,\qquad H_{\rm cone}=xy-q.              \tag{1.4}
\]

At the first event,

\[
\begin{aligned}
 D&\in[52.17752664268594,54.034962288094192],\\
 H_{\rm cone}&\in[262.34984920133354,274.32955885053792],\\
 x'=y&>26.31,\qquad y'=100-w>102.17,\\
 H_{\rm cone}'&>1704.01.                                \tag{1.5}
\end{aligned}
\]

Thus the first section encounter is a strict inward crossing of the
`x=10` face and lies strictly inside every other defining face of the
forward-invariant cone `K_{1/2,10}`.  The analytic cone theorem then gives a
finite forward pole for every phase in (1.2), and hence in the robust open
interval `(-.2,.2)` modulo `2*pi`.

## True-graph and tangent budgets

The sibling source proof
[`origin-algebraic-heteroclinic`](../origin-algebraic-heteroclinic/README.md)
constructs the exact degree-ten polynomial `H10` and validates on the full
disk `||u||_2<=.01`

\[
 \|H-H_{10}\|_2\le10^{-20},\qquad
 \|D(H-H_{10})\|_{2\to2}\le10^{-18}.                  \tag{2.1}
\]

The entry proof reruns that graph certificate.  For C0 propagation it
encloses the Euclidean residual ball by the component square
`[-1e-20,1e-20]^2`.  Since the phase tangent in (1.1) has Euclidean norm
`.01`, the C1 propagation uses component directional error at most

\[
 10^{-18}\cdot .01=10^{-20}.                            \tag{2.2}
\]

These are uncertainty budgets for the true graph and its true tangent, not
floating-point fitting errors.

The C1 first-event calculation gives

\[
 \partial_\phi\tau_{10}
 \in[-2.8932872001945009,-1.2302008618944771],           \tag{2.3}
\]

and finite interval enclosures for every component of the phase derivative
of the event map; all values are recorded in `certificate.json`.  This is
only C1 control of this finite first-event map.

## Phase and source separation

The new interval is disjoint modulo `2*pi` from the certified
origin-to-algebraic phase

```text
[5.7566913947049203, 5.7566913967948983]
```

and the certified symmetric-homoclinic phase

```text
[5.8615055856447817, 5.8615055856450482].
```

This is the same linearizing phase gauge used in (1.1), not a separately
fitted angle. On the common lift centered at zero the last two boxes are
obtained by subtracting `2*pi`. Using the conservative elementary bound
`2*pi>6.28318`, their strict separations from the closed pole cover
`[-.2,.2]` are respectively

```text
algebraic-to-pole gap  > 0.32648
homoclinic-to-pole gap > 0.22167.
```

The source hull in pole coordinates is

```text
x in [-0.010010031791811595, -0.009809645045468305]
y in [-0.008319910765767885, -0.005505202615104120]
q in [-0.008341887233240431, -0.005529021304629892]
w in [-0.001968560064300114,  0.002000942130359127].
```

In particular `y,q<-.005`, whereas the raw-crest family starts on `y=q=0`.
The present sources also have exact energy zero because they lie in
`W^u(0)`; nonzero raw crests have energy `-4r^3/3`.  These are distinct
source families.

## Finite cover and first-event logic

The phase interval (1.2) is the union of 400 exact-decimal boxes

\[
 [i/1000,(i+1)/1000],\qquad i=-200,\ldots,199.          \tag{4.1}
\]

For every box the probe:

1. encloses the true graph source using (2.1);
2. integrates a `C0HOTripletonSet` to the coordinate section `x=10`;
3. requests `poincare::Both`, so no crossing is discarded because of its
   orientation;
4. checks that this first returned section encounter occurs in `(10,12)`
   and has all strict margins in (1.5);
5. integrates a `C1HORect2Set`, multiplies the ambient first variation by
   the interval phase tangent from (2.2), and applies the event-time
   correction.

The source has `x<0`, while the event has `x=10` and `x'=y>25`; therefore
the returned encounter is the first inward hit of the declared face.  Any
failed C0 margin, failed C1 bound, or CAPD exception exits nonzero.

## Clean replay

The recorded environment is

```text
g++ 15.2.0
CAPD 2.5.1, git 731079217a9254ea2948d742df2b170895effe7f
FILIB interval backend, -frounding-math
```

From the repository root, run

```bash
PAPERA_CAPD_CONFIG=/absolute/path/to/capd-config \
  validation/origin-unstable-pole-entry/run_validation.sh
```

The script creates a fresh build directory under `/tmp`, rebuilds the local
unstable-graph proof and the pole-entry probe from source, parses both JSON
outputs, rechecks the declared margins, and prints the source hashes.  No
executable or generated numerical output is written to the repository.

The exact audited values, dependency hashes and toolchain hashes are frozen
in [`certificate.json`](certificate.json).
