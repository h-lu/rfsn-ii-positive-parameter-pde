# CAPD toolchain metadata audit

This package is a non-claim-bearing metadata addendum for
the Paper A interval certificates.  It resolves one provenance-label error:
the historical value `2.5.1` came from

```text
capd-config --version
```

but the generated `capd-config` is a wrapper around the pkg-config frontend.
Thus `--version` reports **pkgconf 2.5.1**, not the CAPD library version.  The
CAPD version is **6.1.0**, independently read from `CAPDVersion.txt` and from

```text
capd-config --modversion
```

at source commit
`731079217a9254ea2948d742df2b170895effe7f`.

## Audited evidence

`verify.py` checks all of the following against the retained build:

| item | audited value |
|---|---|
| CAPD source version | `6.1.0` |
| CAPD source commit | `731079217a9254ea2948d742df2b170895effe7f` |
| `capd-config --modversion` | `6.1.0` |
| `capd-config --version` | `2.5.1` |
| pkg-config frontend identity | `pkgconf 2.5.1` |
| `libcapd.a` SHA-256 | `316b2c480f1ce36b293602da9978eb43560646991a4a906d72ee893b3c557119` |
| interval backend | `FILIB` |
| `libfilib.a` SHA-256 | `ce5cdf8f22d4a6737461774211053a3df360178194e431e4f7ad2b2ada5caa7e` |

The FILIB check is redundant by design: the script requires
`CAPD_INTERVAL_TYPE=FILIB` in `CMakeCache.txt`, the FILIB compile definitions
in `capd-config --cflags`, and `-lfilib` in `capd-config --libs`.

The static `libcapd.a` hash is intentionally stricter than a source-commit
check and is path-sensitive.  `CAPDSmithForm.h` contributes an `__FILE__`
string to `intMatrixAlgorithms.cpp.o`; consequently a byte-identical rebuild
must place the pinned checkout at
`/tmp/papera-capd.bKwHIQ/CAPD`.  Building the same commit and options elsewhere
preserves the interval implementation but does not reproduce the locked
archive bytes, and the release preflight therefore rejects it.

## Affected historical certificate fields

The following values are retained byte-for-byte in the claim certificates,
but `2.5.1` must be interpreted as the pkgconf frontend version returned by
`capd-config --version`, never as the CAPD source/library version.

| certificate | JSON path |
|---|---|
| `validation/finite-source-intermediate-collar/certificate.json` | `$.replay_pins.capd_pkg_config_version` |
| `validation/finite-source-intermediate-collar/spiral_extension_certificate.json` | `$.replay_pins.capd_pkg_config_version` |
| `validation/fixed-fold-event-bridge/certificate.json` | `$.environment.capd_config_version` |
| `validation/fundamental-annulus-overlap/certificate.json` | `$.build.capd_version` |
| `validation/future-target-fold/certificate.json` | `$.pins.capd_pkg_config_version` |
| `validation/origin-algebraic-heteroclinic/certificate.json` | `$.toolchain.capd` |
| `validation/origin-unstable-pole-entry/certificate.json` | `$.replay.capd_version` |
| `validation/universal-core-periodic-return/certificate.json` | `$.implementation.capd_version` |
| `validation/universal-core-symmetric-homoclinic/certificate.json` | `$.replay.capd_version` |

Some package READMEs repeat the shorthand “CAPD 2.5.1”; this audit supplies
the same correction for that prose.  The correctly labelled
`pkg-config version 2.5.1` line in `future-target-fold/README.md` is already
consistent with the audit.

No historical claim certificate is rewritten.  Rewriting would change its
byte hash and could trigger an irrelevant certificate/source-hash cascade.
This addendum changes no interval enclosure, cover, source hash, proof status,
or replay output, and it does not pretend to replay those claim probes.

## Replay

The explicit and preferred invocation is

```bash
python3 validation/toolchain-metadata-audit/verify.py \
  --capd-source /tmp/papera-capd.bKwHIQ/CAPD \
  --capd-config /tmp/papera-capd.bKwHIQ/CAPD/build/bin/capd-config
```

For local convenience, the script also respects `CAPD_SOURCE` and
`CAPD_CONFIG`, then tries `capd-config` on `PATH`, and finally searches an
existing `/tmp/papera-capd.*/CAPD` build.  Discovery paths and timestamps are
not written to `certificate.json` and are not claim data.

The tracked certificate is compared by default.  Its deterministic JSON can
be inspected or rebuilt with

```bash
python3 validation/toolchain-metadata-audit/verify.py --print-json
python3 validation/toolchain-metadata-audit/verify.py --write-certificate
```

The second command is a deliberate maintenance operation; ordinary audits
should use the default read-only comparison.
