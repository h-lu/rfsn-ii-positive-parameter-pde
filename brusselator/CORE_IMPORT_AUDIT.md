# Audit of the imported Brusselator core homoclinic

**Audit date:** 2026-08-28  
**Evidence status:** provenance and interface audit; no new certificate run

This note records whether the compressed flagship paper still supplies the
single model-specific input used by Theorem B and whether that input is
presently accessible to an external referee. The flagship repository was
inspected read-only and was not modified.

## 1. Mathematical crosswalk

The frozen application baseline is flagship commit
d54add098545063d5efe8f1d6f062d4cfc116a0d. Its Proposition 8.6, in the
verification of Definition 2.1(I2), and equations (8.36)--(8.40) provide the
selected symmetric core homoclinic, first symmetry hit, and transverse
shooting derivative used in
[CORE_HOMOCLINIC_IMPORT.md](CORE_HOMOCLINIC_IMPORT.md).

The focused flagship paper at inspected commit 8e04dc3 retains the same
object. Section 6, item V3, states the same shooting box, first symmetry hit,
and interval

\[
 \det D_{(\phi,T)}(P,Q)
 \in[149.56393055300413,149.56404227745782],
\tag{1}
\]

and its RFSN-II realization theorem uses V3 to verify its core homoclinic
hypothesis. The central field, coordinate order \((U,P,V,Q)\), reverser, and
clock agree exactly with the \(r=0\) Brusselator system. No sign, coordinate
factor, or time factor is missing.

The application requires only the following compressed Core Lemma:

> The core system
> \(U'=P,\ P'=-U^2-V,\ V'=Q,\ Q'=U\) has the selected nonconstant symmetric
> homoclinic \(\Gamma_0\), centered at
> \(c_0\in\operatorname{Fix}\mathcal R\), such that
> \(W^u_0(0)\pitchfork\operatorname{Fix}\mathcal R\) at \(c_0\), and the
> center values of both profile components are nonzero.

The flagship's return--exit, two-end, action, and coding conclusions are not
used by the Brusselator theorem.

## 2. Frozen evidence identity

The following M3 files have the same bytes at the frozen baseline, the
inspected archive commit 5c1de755, and focused commit 8e04dc3:

| Object | SHA-256 |
|---|---|
| M3 README | 34f3e15f475d22be939020bde2b8480ae33ba60a9c043f577088ab5d70253610 |
| M3 certificate | ed0f9f58f8ba5f1d5c36dc7c3a72bb725599c4172a3cd610d890b88699fecfbd |
| M3 interval probe | 655cfe16e2cdb24185f11cbb314e7c0b2f029705d4588fdcbaf5a9f0993298f3 |

The M3 closure also depends on the rigorously enclosed local unstable graph,
including its source, certificate, and recorded dependency hashes. A
standalone copy of the M3 JSON would therefore not be a complete evidence
bundle.

The focused repository's `validation/replay_manifest.json` classifies M3 as
**source-verifiable-only**. On 2026-08-28 the command

~~~text
python3 validation/replay_all.py --profile main-theorem --dry-run
~~~

passed all static source and dependency hash checks in the read-only
flagship checkout. The dry run explicitly executes no certificates. It is
not a mathematical replay, a second implementation, or an independent
machine reproduction.

## 3. Public-access finding

At the audit date, anonymous requests for the flagship repository, raw M3
certificate, and archive-tag locations returned HTTP 404. Authorized git
access and immutable hashes preserve provenance for the author, but they do
not give a referee a stable public object to inspect.

Consequently:

- the current private GitHub URL is not a publication-ready evidence locator;
- B1--B2 are proved **relative to the imported computer-assisted Core Lemma**,
  while the current publication package is not yet externally auditable; and
- the focused manuscript retains the V3 statement and evidence mapping used
  here, but does not by itself solve external accessibility.

## 4. Minimal publication closure

No new core computation is needed for the analytic continuation proof.
Independent replay remains a separate reproducibility option, but is not a
prerequisite for drafting the application argument. The minimal closure is:

1. state the compressed Core Lemma, including its evidence status, immediately
   before the continuation theorem;
2. cite the final stable focused-paper theorem location when that manuscript
   is frozen;
3. retain the historical baseline and hashes as provenance; and
4. before submission, make either the frozen flagship tag and evidence public
   or attach a complete M3 evidence closure, including the local-unstable-graph
   dependency and replay metadata, to a stable release/archive.

Until the focused flagship worktree has a final commit or tag, this
application repository must not silently repin its normative baseline. Any
future baseline update requires the explicit hash and downstream-effect audit
specified in [theory/BASELINE.md](../theory/BASELINE.md).

This accessibility item blocks an externally auditable, self-contained
submission package, but it does not alter the mathematical implication from
the Core Lemma or block drafting and checking the local positive-parameter
proof.
