# Paper A fixed-fold/event-chart bridge

This source-only package closes one endpoint seam between two promoted
validation bundles for

\[
 U'=P,\qquad P'=-U^2-V,\qquad V'=Q,\qquad Q'=U.
\]

Its conclusion is deliberately specific to the **same canonical physical
future graph**:

> The unique physical fold orbit in the robust fixed-\(T=15\) fold box has
> a first \(e=-1/U=0.0575\) event. Its complete 36-piece event-chart
> representation lies strictly inside box 0 of the finite
> intermediate-collar cover. Hence the fold orbit and the box-0 orbit are
> one and the same root.

This is not inferred from the closeness of their numerical centres, nor from
the intersection of two independent error boxes.

## Matching the target quantifier

The upstream fold certificate is uniform under

\[
 |\eta|\le10^{-8},\qquad
 \|D\eta\|_2\le10^{-5},\qquad
 \|D^2\eta\|_2\le10^{-3}.
\]

For this bridge, prepare_sharp_fold.py mechanically rebuilds the same
248-dimensional fold program with the sharper physical value budget

\[
 |\eta|\le2(0.06)^8=3.359232\times10^{-10},
\]

while retaining the first- and second-derivative budgets. This contains the
canonical physical graph because its weighted representation satisfies
\(\eta=e^8\Gamma\), \(|\Gamma|\le2\), throughout \(0\le e\le0.06\).
Three further applications of the already validated Krawczyk operator shrink
the root enclosure; every iterate is justified inside the original
uniqueness box.

The collar box uses the sharper pointwise value budget
\(|\eta|\le2e^8\) and the same \(C^1\) bound. The common-root conclusion is
made only for the canonical invariant graph, so the target at \(T=15\) and
the target at the event are not independent interval parameters.

## Same-orbit containment

fold_event_flow_bridge_probe.cpp captures the sharpened fold Krawczyk image
and applies the exact core flow to it. A CAPD Poincare map to

\[
 U=-1/0.0575
\]

preserves the correlation between the crossing time and the crossing state.
The return time after \(T=15\) is

\[
 [0.0030059706773684328,\;0.0030059724778218307].
\]

The program also proves

\[
\begin{aligned}
 e(15+0.003004)&\in
 [0.057500015687599458,0.057500015701931854]
 \subset(0.0575,\infty),\\
 e(15+0.003008)&\in
 [0.057499983845560952,0.057499983859893661]
 \subset(-\infty,0.0575),
\end{aligned}
\]

and \(P<0\) on this bracket. Thus this is the unique next event after
\(T=15\).

For every one of the 37 event nodes, all four state coordinates obtained
from the captured fold root enclosure are strictly inside the corresponding
collar box-0 interval. The common flight-time interval is strictly inside
all 37 time-coordinate intervals. The smallest absolute component margin is

\[
 2.999881659867495\,10^{-8}.
\]

The largest propagated-image radius divided by its collar radius is
\(0.013136319938984245\).

## Krawczyk, first-event and tangent gates

The replay independently reruns collar box 0:

- root Krawczyk ratio \(0.7604664676756359\);
- contraction ratio \(0.16802038029318725\);
- tangent Krawczyk ratio \(0.10037347894287656\);
- strict first-event test: PASS.

The captured fold tangent has \(V\)-chart normalization

\[
 \frac{dU}{dV}\in
 [-0.39842384494363481,-0.39842384490415239],
\]

strictly inside the collar tangent enclosure

\[
 [-0.39902198777056247,-0.39782570616752944].
\]

For the canonical graph, invariance carries the fixed-time target point to
the event target. Exact IVP uniqueness makes the propagated orbit a root of
the box-0 BVP; strict containment and box-0 Krawczyk uniqueness identify it
with the box-0 root. The box-0 first-event and tangent certificates therefore
apply to the fold orbit.

## Clean replay

From this directory, with CAPD 2.5.1/FILIB available:

~~~bash
python3 replay.py --capd-config /path/to/capd-config
~~~

The replay:

1. deterministically generates only the first three collar centres, so the
   box-0 endpoint tangent uses the same second-order finite difference as the
   full cover;
2. generates the sharpened fold source in a temporary build directory;
3. rebuilds and runs the sharpened fold/flow-containment probe;
4. rebuilds and runs the promoted collar box-0 Krawczyk/tangent probe;
5. checks strict tangent and parameter containment and writes
   [certificate.json](certificate.json).

All binaries, generated seeds and modified build sources live in a temporary
directory. They are not evidence artifacts and are not committed. The
certificate pins every source and upstream dependency hash.

## Scope

This package closes only the fixed-\(T\) fold/event-chart seam. It does not
cover the inward spiral from the intermediate collar to the local annulus,
and it does not cover the other side of the fold to the exact algebraic
source \(c_0=(0,1/6)\).
