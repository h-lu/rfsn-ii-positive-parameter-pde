# Repository instructions

- Keep this repository independent of `reversible-rfsn-ii-waves`; do not edit
  the flagship manuscript from this worktree.
- Treat every checkout of `reversible-rfsn-ii-waves` as read-only: do not
  modify, commit, push, or use its uncommitted files as an implicit input.
  Abstract corrections and extensions motivated by this project belong under
  `theory/` in this repository and must retain an exact frozen-source boundary.
- Distinguish a frozen flagship input, a local abstract amendment, and a
  model-specific application in every theorem dependency.  A local amendment
  changes no upstream theorem or status.
- Preserve the statuses and nonclaims in `CLAIM_REGISTER.md` and
  `RESEARCH_CONTRACT.md`.
- Do not call a positive-parameter result a persistence result until both end
  compactifications and their matching have been proved in the claimed class.
- Separate formal asymptotics, non-rigorous numerics, rigorous numerics, and
  proof in every report and commit.
- Use standard terminology from dynamical systems and singular perturbation
  theory.  Do not introduce project-specific names where established terms
  suffice.
- Prefer primary papers and exact theorem citations.  Record scale, time, sign,
  symplectic, and parameter conventions whenever importing a formula.
- PDE temporal stability and experimental validation are separate projects and
  are not completion conditions here.
