# `vdp-companion-v1` baseline and current working revision

The immutable `vdp-companion-v1` release is the first publication-facing van
der Pol companion package.  Its contents and hashes are recorded first and
are not retroactively changed by later manuscript revisions.

It contains:

- the 21-page main paper, stated in the original reaction--diffusion PDE
  variables;
- the one-page schematic separating high winding, the finite-distance pole,
  the infinite-distance algebraic end, and the K2-to-K1-to-outer matching
  bridge;
- the 4-page provenance supplement and neutral expert cold-read packet;
- the complete V1--V7 proof archive in this repository; and
- an exact 102-file extraction of the frozen RFSN-II manuscript and
  validation package at commit
  `d54add098545063d5efe8f1d6f062d4cfc116a0d`.

The principal theorem is conditional on the frozen Hypothesis H stated in the
paper. This release does not claim an independent second-machine replay,
certification of the proposed Issue #7 box, temporal stability, Turing
selection, canard identification, or experimental realization.
An independent human expert cold read is requested in
[Issue #9](https://github.com/h-lu/rfsn-ii-positive-parameter-pde/issues/9);
no human report is claimed before one is returned.

SHA-256:

```text
8b4fdf8fa97fb46ca9115d5de16709c6185ac2670dc25f21d7e77b33f7d21b2d
  van-der-pol-positive-two-end-spatial-dynamics.pdf
a856def1e73cca6a3cb7e76c77503dde0762fe90054f552dedeca4d069aa6e07
  van-der-pol-positive-two-end-spatial-dynamics-supplement.pdf
```

## Current working revision (September 1, 2026)

The current branch contains a later reader-facing revision, not a replacement
of the immutable v1 tag.  It has a 26-page main paper and an 8-page supplement.
The analytic proof now separates resolved $K_1$ graph transport from
true-source phase--time incidence, and the supplement records their rigorous
representative-cell finite-$K_1$ composition at its non-claim-bearing evidence
level.  The 393,216-cell full-box extension is deferred to Issue #14 and is
not a manuscript completion condition.

Current working PDF SHA-256 values are:

```text
94ae77d94c3d4f718fe5e791cebe2d6b13ce07df62d021379509aad8a68719d1
  van-der-pol-positive-two-end-spatial-dynamics.pdf
7c07bd1d9e7130dc8b0263d07ba1e0820ad818752d9bfc6a8c869e23e1b36d8e
  van-der-pol-positive-two-end-spatial-dynamics-supplement.pdf
```

No new immutable release tag is claimed by this working-revision record.

No license file was present in either repository. The release makes the
materials inspectable and citable without inventing reuse rights.
