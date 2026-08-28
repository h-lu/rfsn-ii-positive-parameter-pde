#!/usr/bin/env python3
"""Rebuild and validate the six isolated extension pilot boxes."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import shlex
import subprocess
import tempfile


HERE = Path(__file__).resolve().parent
CASES = (
    (0, "u", 5e-6),
    (0, "v", 5e-6),
    (1, "v", 1e-6),
    (1, "u", 1e-6),
    (2, "u", 2e-7),
    (2, "v", 2e-7),
)


def flags(capd_config: Path, option: str):
    return shlex.split(
        subprocess.run(
            [str(capd_config), option], check=True, text=True, capture_output=True
        ).stdout
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--capd-config",
        type=Path,
        default=Path(os.environ.get("CAPD_CONFIG", "capd-config")),
    )
    parser.add_argument(
        "--seeds", type=Path, default=HERE / "extension_pilot_seeds_108.txt"
    )
    parser.add_argument(
        "--manifest", type=Path, default=HERE / "extension_pilots_108.jsonl"
    )
    args = parser.parse_args()
    rows = [json.loads(line) for line in args.manifest.read_text().splitlines()]
    segment_counts = {int(row["segments"]) for row in rows}
    if len(segment_counts) != 1:
        raise RuntimeError("pilot manifest mixes shooting segment counts")
    segments = segment_counts.pop()
    with tempfile.TemporaryDirectory(prefix="papera-extension-pilots-") as directory:
        binary = Path(directory) / "source_cover_probe_108"
        subprocess.run(
            [
                os.environ.get("CXX", "g++"),
                "-O0",
                "-std=c++17",
                f"-DPAPERA_SEGMENTS={segments}",
                str(HERE / "source_cover_probe.cpp"),
                f"-I{HERE}",
                *flags(args.capd_config, "--cflags"),
                *flags(args.capd_config, "--libs"),
                "-o",
                str(binary),
            ],
            check=True,
        )
        records = []
        for index, chart, width in CASES:
            run = subprocess.run(
                [
                    str(binary),
                    "--seed-file",
                    str(args.seeds),
                    "--seed-offset",
                    str(rows[index]["seed_offset"]),
                    "--parameter",
                    chart,
                    "--half-width",
                    repr(width),
                ],
                check=True,
                text=True,
                capture_output=True,
            )
            record = json.loads(run.stdout)
            record.update(
                {
                    "pilot_index": index,
                    "pilot_name": rows[index]["name"],
                    "requested_chart": chart,
                    "requested_half_width": width,
                }
            )
            records.append(record)
    print(
        json.dumps(
            {
                "status": "PASS-SIX-ISOLATED-EXTENSION-PILOTS-NOT-A-COVER",
                "records": records,
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
