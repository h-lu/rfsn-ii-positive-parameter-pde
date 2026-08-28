# Frozen RFSN-II input snapshot

This directory is an exact, read-only extraction from
`h-lu/reversible-rfsn-ii-waves` at commit

```text
d54add098545063d5efe8f1d6f062d4cfc116a0d
```

whose Git tree is

```text
b9cd34b1bae1c29bdd722d9ed3c33402c4b3ee89
```

The upstream repository remains read-only for this application project.  The
snapshot was extracted with `git archive`; no frozen file below `source/` was
edited.  It contains:

- the complete frozen Paper A manuscript directory, including source, PDF,
  bibliography, figures, and literature matrix;
- the complete frozen `validation/` directory, including certificates,
  validation source, the environment lock, and `replay_manifest.json`.

The purpose is stable anonymous inspection of Hypothesis H in the van der Pol
companion.  The evidence status is unchanged: the frozen source reports the
computer-assisted results recorded in its certificates, while the application
repository has verified the exact bytes and hashes but does not claim a new
independent second-machine replay.

From a full Git clone of the application release, change to `source/` and
run the lightweight fail-closed source/hash audit:

```bash
python3 validation/replay_all.py \
  --profile main-theorem \
  --dry-run \
  --report /tmp/rfsn-main-theorem-dry-run.json
```

This command deliberately reports `PASS-DRY-RUN-NO-CERTIFICATES-EXECUTED`;
it is not a mathematical replay.  The frozen script invokes Git and therefore
is not advertised for a GitHub source ZIP or a standalone snapshot copy
without `.git`.  Its report field `git_commit` identifies the enclosing
application checkout; the upstream identity is the `upstream_commit` in
`RELEASE_MANIFEST.json`.  A full replay requires the CAPD/FILIB
toolchain pinned by `validation/environment.lock.json` and the corresponding
`--capd-source` and `--capd-config` arguments.  Use the `main-theorem` profile;
the companion does not import the ancillary packages as new application
claims.

No license file was present in the frozen source.  This snapshot therefore
does not invent or broaden reuse rights; it provides public inspection and
citation access while preserving the author's original source bytes.
