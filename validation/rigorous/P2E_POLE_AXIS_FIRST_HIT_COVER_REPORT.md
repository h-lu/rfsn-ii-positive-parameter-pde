# P2e pole-axis first-hit cover

## Result and scope

The interval calculation gives a complete design-level cover of the
zero-action pole entrance on

\[
  (r,a_2,\epsilon)\in
  [0,1/50]\times[-1/4,1/4]\times[4/5,6/5].
\]

For every parameter in this bridge, the calculation starts from the exact
zero-energy source chart on

\[
  \theta\in
  [2\pi-9/800000,2\pi+9/800000],\qquad
  |\eta|\le 1/200000,
\]

where \(\eta\) is the first graph coordinate relative to the frozen
\(H_{10}\) polynomial, not an action variable. The true \(\nu=0\) unstable
source curve is contained in this chart. Every accepted interval enclosure
has a directed first encounter with \(U=-10\), with \(P<0\), after the
bounded global turn. A separate enclosure from the first downward
\(U=-1/20\) crossing excludes an earlier pole encounter.

The machine verdict is

```text
status               PASS
mathematical_status  COMPUTED_INTERVAL_DESIGN_PASS_FULL_BRIDGE
claim_bearing        false
parent cells         4096
hard failures        0
coverage errors      0
```

This closes the pole component of the zero-action exterior first-hit
calculation at design level. It does not by itself prove the complete P2e
event atlas.

## Why the enclosure closes

The obstruction was not a missing orbit but interval growth near three
changes of direction. The final calculation uses the physical flow only
where its coordinates remain well conditioned and changes independent
variables at the turning points.

First, the orbit is followed from the source through its first downward
\(U=-1/20\) crossing, the first minimum of \(U\), and the subsequent
maximum. When a direct section enclosure wraps, the calculation passes
through \(U=0\) with \(x=-U\) as independent variable and uses

\[
  H=0,\qquad P<0<Q
  \quad\Longrightarrow\quad P=-Q
\]

to recondition the interval without removing a true zero-energy orbit.

Second, on the upward leg the calculation uses \(U\) as independent
variable up to \(U=11/4\) and verifies \(P>0\) on every accepted CAPD
enclosure. The following directed \(P=0\) section is therefore the next
maximum.

Third, at that maximum the zero-energy identity determines \(V\). With
\(m=-P\), the calculation advances from \(m=0\) to \(m=1/10\) while
checking \(P'=F<0\). It then uses the increasing coordinate \(x=-U\) to
reach \(U=0\), checks \(P<0<Q\), reconditions again by \(P=-Q\), and
continues to \(x=1/5\) while checking \(P<0\). This replaces the
parameter-dependent fixed seam \(V=4/5\) that caused the earlier wrapping
failures.

Finally, at \(x=1/5\) the independent no-earlier-hit calculation verifies
strict positivity of

\[
  y=-P,\qquad D=\frac{x^2}{2}+V,
  \qquad K=xy+Q.
\]

Together with the boundary estimate for \(K'\), these inequalities give a
forward-invariant pole cone and make \(x\) strictly increasing through
\(x=10\). The terminal enclosure is then tested against the zero-action P3
gate

\[
  y\ge13,\qquad D\ge26,\qquad K\ge131.
\]

## Exhaustive cover

The bridge contains \(8\times128\times4=4096\) closed parent cells. Of
these, 4095 pass without subdivision. The single remaining parent,
\((7,41,3)\), is covered by its eight exact canonical \(r\)-children. Thus
the final result contains 4103 accepted records and no uncovered face or
binary-prefix gap.

The accepted routes are:

| route | records |
|---|---:|
| physical directed sections (`BASE`) | 3661 |
| zero-energy upper-turn and post-maximum reduction (`TURN_REDUCED`) | 375 |
| additional fixed \(V\)-sections (`V_STEPS`) | 67 |

The direct first downward \(U=-1/20\) map is sufficient for 4096 records;
seven refined records use the \(U=0\), \(P=-Q\) entry representation. The
independent physical no-earlier-hit guard passes directly for 3796 records;
307 use its monotone independent-variable form. No root-conditioned source
calculation and no extra adaptive \(r\)-bisection is needed in the final
cover.

## Uniform strict bounds

All numbers below are outward-rounded aggregate endpoints over the accepted
cover.

| quantity | strict bound |
|---|---:|
| return time | \([11.1052049388,11.2360657358]\) |
| acceleration at the final maximum | \(F<-5.6198684752\) |
| acceleration during the \(m\)-passage | \(F<-5.6198178896\) |
| momentum on the passage to \(U=0\) | \(P<-0.0999999999998\) |
| positive \(U=0\) branch | \(Q>3.3081924934\) |
| momentum from \(U=0\) to \(x=1/5\) | \(P<-3.3081924934\) |
| guard minimum | \(U>-0.5270843721\), \(P'>0.4608549324\) |
| guard maximum | \(U>2.8072602565\), \(P'<-5.4447719945\) |
| cone entry at \(x=1/5\) | \(y>2.6362890617\), \(D>0.1934031454\), \(K>3.4197688979\) |
| cone boundary margin | \(K'>4.4703613771\) |
| terminal \(x=10\) | \(y>24.1552524499\), \(D>53.2003816264\), \(K>240.6762253222\) |
| terminal derivatives | \(y'>103.2859186333\), \(K'>1607.1327321392\) |
| P3 gate margins | \(y-13>11.1552524499\), \(D-26>27.2003816264\), \(K-131>109.6762253222\) |

## Evidence binding and reproduction

The compact machine record is
[`design/p2e_pole_axis_full_bridge_summary_v1.json`](design/p2e_pole_axis_full_bridge_summary_v1.json).
It binds the run to the terminal source, runner, tests, frozen \(H_{10}\)
header, executables, and raw result by SHA-256.

The uncompressed raw result is 25,959,506 bytes and has SHA-256

```text
0ea67a60b10c987f720b69460da872c1ec1847e5d4cd5907571fc44f313f3315
```

It remains outside Git and should be published as an immutable release
attachment rather than committed as a 26 MB repository artifact.

The interval-cover invocation was:

```bash
python3 validation/rigorous/design/p2e_pole_axis_cover_scout.py \
  --terminal-executable /tmp/p2e-axis-terminal-pole-v5 \
  --source-executable /tmp/p2e-source-trace-audit \
  --workers 28 --predictor-workers 16 \
  --max-extra-r-depth 4 --timeout 180 \
  --output /tmp/p2e-pole-axis-full-v5-schema3.json
```

A representative build of the current terminal source is:

```bash
g++ validation/rigorous/design/p2e_axis_terminal_first_hit_scout.cpp \
  -I frozen-imports/rfsn-ii-d54add098545063d5efe8f1d6f062d4cfc116a0d/source/validation/origin-algebraic-heteroclinic \
  -o /tmp/p2e-axis-terminal-pole-v5 \
  $(CAPD_BUILD/bin/capd-config --cflags) \
  $(CAPD_BUILD/bin/capd-config --libs)

python3 -m unittest \
  validation.rigorous.tests.test_p2e_pole_axis_cover_scout
```

Here `CAPD_BUILD` is a placeholder for the local CAPD 2.5.1 build directory.
The representative rebuild reproduces checked sample output but is not
asserted to reproduce the bound executable byte for byte: the exact
source-to-binary build provenance of that executable was not retained. This
is one reason the run is not a release certificate. The source executable
was supplied and hashed but was not invoked because the broad \(H_{10}\)
tube already covered every cell after the one canonical subdivision.

## What remains open

The evidence is deliberately labelled `claim_bearing=false`. The present
run does not authenticate the CAPD/FILIB build as an immutable public
release, and the 26 MB raw result has not yet been published. More
importantly, a zero-action pole cover is only one part of P2e. The following
remain open:

- the complete algebraic-axis cover;
- the off-axis exact-action collar and its mixed derivatives;
- the full incidence and corner census, exclusion of unnamed residual
  events, transported traces, and a numerical \(m_{\rm ax}\);
- `V2.EVENT_ATLAS` and the full P3 source-window conclusion.

No temporal stability, dynamical Turing selection, or canard identification
follows from this calculation.
