# Paper A finite intermediate-collar cover

This directory is a source-only, replayable audit bundle for the reversible
core

\[
 U'=P,\qquad P'=-U^2-V,\qquad V'=Q,\qquad Q'=U,
 \qquad \operatorname{Fix}R=\{P=Q=0\}.
\]

The bundle now contains two consecutive rigorous event-chart covers.  Their
common endpoint is identified by strict 36-to-108-segment root containment:

> For every physical future target satisfying the promoted value and first
> derivative budgets, 6,316 first-stage boxes followed by 9,725 spiral-
> extension boxes validate one connected **inward event-chart arc**.  It runs
> from the numerical first-fold neighbourhood
> \((U,V)\approx(0.0415270,0.1025037)\), through the intermediate collar
> \((U,V)\approx(0.0237998,-0.00770460)\), to the promoted fixed radial seam
> \(R=2.4\times10^{-4}\).  The seam root is the selected local saddle-focus
> arm by the independently validated fixed-radius/exit-chart uniqueness
> contract.

This bundle itself does not connect the separate fixed-time fold certificate
to the event chart or cover the outer arc to the exact algebraic source
\(c_0=(0,1/6)\).  The sibling `fixed-fold-event-bridge` and
`exact-source-outer-fold` packages now supply those two seams.  See
`certificate.json` for the first-stage claim and
`spiral_extension_certificate.json` for the finite-to-local seam.

## Formulation and dimensions

The orbit is divided into 36 normalized-time shooting pieces.  Each of the 37
nodes carries \((U,P,V,Q,T)\), with \(T'=0\), so there are 185 unknowns and
185 equations:

- 180 multiple-shooting continuity equations;
- source equations \(P_0=Q_0=0\) and either \(V_0=v\) or \(U_0=u\);
- terminal event \(e=-1/U_N=0.0575\);
- terminal physical-target equation
  \(p-h_7(e,d,\omega)-\eta(e,c,\omega)=0\).

Here

\[
 p=Pe^{3/2},\quad q=Qe^{3/2},\quad
 d=q+2/\sqrt3,\quad \omega=1+Ve^2,
 \quad c=d-\sqrt3\,\omega/2.
\]

The floating seed uses the centre \(\eta=0\), but the interval proof does
not.  It propagates

\[
 |\eta|\le 2e^8,\qquad \|D\eta\|_2\le10^{-5}
\]

through the residual and target row.  Thus the result concerns the promoted
physical graph \(h_7+e^8\Gamma\), not merely the polynomial centre \(h_7\).
Every terminal evaluation box is also checked inside the independently
validated signed physical corridor

\[
 0<e<0.06,\qquad |a|<0.0065,\qquad |b|<0.01,
 \qquad |E|<0.012,\qquad |\zeta|\le2,
\]

where \(a=d/e^3\), \(b=(\omega-e^2/6)/e^4\), and
\(p=h_7+e^8\zeta\).

## What was validated

The deterministic work list uses 4,919 fixed-\(V\) boxes followed by 1,397
fixed-\(U\) boxes.  The chart switch is at

\[
 (U,V)=(0.03426454453805599,0).
\]

The smallest scalar-parameter overlaps are
\(2.5037481\times10^{-6}\) in the \(V\) chart and
\(2.5037779\times10^{-6}\) in the \(U\) chart.  Parameter overlap alone was
not accepted as adjacency evidence.  For every consecutive pair the validator
chooses one common parameter, computes a point-parameter Krawczyk root in the
current box, proves that root enclosure lies strictly inside the next
uniqueness box, and proves its next-chart parameter lies strictly inside the
next parameter interval.  The same test is used at the \(V\)-to-\(U\) switch.

The completed run gave:

- boxes: 6,316/6,316 PASS;
- true adjacency bridges: 6,315/6,315 PASS;
- first-event checks: 6,316/6,316 PASS;
- tangent linear Krawczyk checks: 6,316/6,316 PASS;
- maximum root Krawczyk ratio: 0.8456983578086148;
- maximum weighted contraction ratio: 0.7155493759061057;
- maximum tangent Krawczyk ratio: 0.6733191700153359.

The terminal unions were

\[
 a\in[-0.000475813,0.004036073],\qquad
 b\in[-0.005308519,0.005412223],
\]

and, uniformly for \(|\zeta|\le2\),

\[
 E_{\rm graph}\in[-0.009924623,0.001721345].
\]

The energy derivative is not sign-resolved in boxes 0 and 1, which overlap
the outer fold.  It is strictly negative in boxes 2 through 6,315.  This is a
diagnostic for the validated event-chart arc; it is not a substitute for the
separate fixed-time-fold/event-chart bridge.

## Why the first-stage cover is finite and connected

For one chart interval \(I_j\), the uniform parametric Krawczyk inclusion
gives a unique BVP root in \(X_j\) for every scalar parameter in \(I_j\),
uniformly over the target contract.  The interval Jacobian is nonsingular, so
the implicit branch is continuous (and is \(C^1\) for the physical target).
The common-parameter containment test gives a root belonging to both
successive local branches.  Induction over all 6,315 certified intersections
therefore makes the union one connected arc.  Merely checking
\(I_j\cap I_{j+1}\ne\varnothing\) would not establish this.

## Reproducible replay

The recorded environment is Python 3.14.4 with NumPy 2.5.2, SciPy 1.18.0,
SymPy 1.14.0, g++ 15.2.0, and CAPD 2.5.1 at commit
`731079217a9254ea2948d742df2b170895effe7f` using FILIB.  Install the Python
pins in `requirements.txt` and expose CAPD's `capd-config` either on `PATH` or
through `CAPD_CONFIG`.

From this directory:

```bash
python3 cover_plan.py
python3 generate_full_cover.py --fresh
python3 validate_full_cover.py --workers 16 --capd-config /path/to/capd-config
python3 build_certificate.py
```

`generate_full_cover.py` constructs \(h_7\) symbolically, bootstraps from the
algebraic orbit, follows the prescribed fixed-\(V\)/fixed-\(U\) work list, and
serializes every floating centre and finite-difference tangent with 17 digits.
Those centres are preconditioner data only.  All evidentiary statements come
from the CAPD/FILIB replay.

The large replay products are intentionally absent from this source bundle.
The hashes of the completed run are retained in `certificate.json`; compare
the regenerated files against its `bulk_replay_hashes`.  In particular, do
not commit `cover_seeds.txt`, the JSONL result files, NPZ checkpoints, compiled
executables, debug outputs, or `__pycache__`.

The validator includes the promoted sibling headers
`../future-target-fold/tail_graph_generated.hpp` and
`../future-target-fold/weighted_tail_generated.hpp`.  Their provenance and
hashes are in `target_provenance.json`; no external temporary package is
required.

## Promoted inward spiral extension

The earlier reconnaissance located three isolated floating centres,

\[
\begin{array}{c|c|c|c}
 &U&V&T\\ \hline
U=0&0&-0.0070364116384&18.8904412\\
V=0&-0.00146338443326&0&21.1125770\\
U=0&0&0.000304368592600&23.3333283
\end{array}
\]

The third point, at \(R\approx3.04\times10^{-4}\), is outside the local seam
and has **not** been used as an endpoint.  It is now a strictly bridged
interior \(U\)-to-\(V\) chart switch in a complete chain continuing to
\(R=2.4\times10^{-4}\).

The promoted extension uses 108 shooting pieces, hence 545 unknowns and
equations per box.  A deterministic 9,616-box base mesh was audited first.
Sixty-eight base widths failed in localized FILIB/CAPD propagation windows;
another 22 successful boxes had root Krawczyk ratio at least 0.95.  The
checked refinement plan halves those 90 widths and inserts 109 interpolated
preconditioner centres wherever needed to retain at least one quarter of the
smaller half-width as scalar-parameter overlap.  Every interpolated centre is
only a preconditioner: it receives proof status solely from the subsequent
interval replay.

The final cover contains

\[
3991+2535+2957+241+1=9725
\]

boxes in successive \(U,V,U,V,R\) charts and 9,724 adjacent common-root
bridges.  The completed replay gives:

- boxes: 9,725/9,725 PASS;
- adjacent common-root bridges: 9,724/9,724 PASS;
- first-event and tangent checks: 9,725/9,725 PASS;
- maximum root Krawczyk ratio: 0.9492402114706467;
- maximum contraction ratio: 0.7733951226387051;
- maximum tangent Krawczyk ratio: 0.9991041442254496;
- minimum current/next state containment margins:
  \(5.9868503\times10^{-9}\) and \(1.7765608\times10^{-9}\);
- minimum next-chart parameter containment margin:
  \(2.5013613\times10^{-8}\).

The first fine root lies strictly in the promoted 36-segment intermediate-
collar uniqueness box with margin \(2.9999992\times10^{-8}\).  The final
event root lies strictly in the promoted fixed radial source box with margin
\(1.9847633\times10^{-9}\).  The fixed-radial package then identifies that
root with the unique local selected arm through its nonlinear first-exit and
common target-chart argument.

The source-only replay keeps all large products outside the repository:

```bash
CAPD_CONFIG=/path/to/capd-config bash run_spiral_extension_validation.sh \
  /tmp/papera-spiral-replay \
  /tmp/promoted-cover-boxes.jsonl \
  /tmp/promoted-cover-seeds.txt \
  24
```

This runs base generation, deterministic refinement, compilation, all box and
bridge checks, both endpoint containments, certificate construction, and
SHA-256 reporting.  The base and refined replay hashes are pinned in
`spiral_extension_certificate.json`; seeds, JSONL products, binaries and
`__pycache__` remain untracked.

## Separately certified endpoint gates

1. **Outer fold bridge:** `../fixed-fold-event-bridge` propagates the
   fixed-\(T\) robust fold enclosure to the first \(e=0.0575\) event and
   contains the resulting root in box 0.
2. **Outer component:** `../exact-source-outer-fold` covers the other side
   of the fold to \(c_0=(0,1/6)\) and proves the exact algebraic/Jost
   endpoint bridge.

This package alone is not a complete source-component cover.  In composition
with the two endpoint packages it proves one selected
\(c_0\)-to-local-spiral arm, not a classification of every component or an
origin-to-future-target heteroclinic.
