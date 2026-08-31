from __future__ import annotations

import copy
import hashlib
import importlib.util
import json
import os
import stat
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


RIGOROUS = Path(__file__).resolve().parents[1]
DRIVER = RIGOROUS / "v5_source_incidence_cover.py"
CONFIG = RIGOROUS / "config" / "vdp_v5_source_incidence_cover_v1.json"
SPEC = importlib.util.spec_from_file_location("v5_cover_driver", DRIVER)
assert SPEC is not None and SPEC.loader is not None
COVER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = COVER
SPEC.loader.exec_module(COVER)


def sha256(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


class V5SourceIncidenceCoverDriverTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory(prefix="v5-cover-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name)
        self.run_dir = self.root / "run"
        (self.run_dir / "cells").mkdir(parents=True)
        self.config = COVER._load_config()

    def payload(self, status: str = "PASS") -> dict[str, object]:
        interval = {
            "lower_hex": "0x0p+0", "upper_hex": "0x1p+0",
            "endpoint_format": "IEEE754_BINARY64_HEX",
        }
        gates: dict[str, object] = {
            name: [True] if name.endswith("_by_slice") or
            name == "continuation_faces_by_half" else True
            for name in COVER.REQUIRED_GATES
        }
        if status == "INCONCLUSIVE":
            gates["base_budget"] = False
        enclosure_names = {item[1] for item in COVER.EXTREMA_SPECS}
        return {
            "schema_version": COVER.CELL_SCHEMA,
            "status": status, "mathematical_status": status,
            "claim_bearing": False, "box_id": "vdp-positive-box-v2",
            "cell_index": [0, 0, 0], "grid": list(COVER.GRID),
            "exterior_propagation_mode": COVER.OUTPUT_MODES[COVER.FAST_MODE],
            "target_graph_contract": copy.deepcopy(COVER.TARGET_GRAPH_CONTRACT),
            "rounding_self_test": {"status": "PASS"}, "gates": gates,
            "merged_root_exterior": {
                "candidate_hull_consistency_gate": status == "PASS",
                "kernel_gate": status == "PASS",
            },
            "enclosures": {name: copy.deepcopy(interval)
                           for name in enclosure_names},
        }

    def make_probe(self, behavior: str, log: Path) -> Path:
        path = self.root / f"probe-{behavior.lower()}"
        source = f'''#!/usr/bin/python3
import json, os, sys
p=json.loads({json.dumps(json.dumps(self.payload()))})
mode=sys.argv[1]
with open(os.environ["V5_FAKE_LOG"], "a", encoding="utf-8") as f: f.write(mode+"\\n")
p["cell_index"]=[int(v) for v in sys.argv[-3:]]
p["exterior_propagation_mode"]={{
  "{COVER.FAST_MODE}": "{COVER.OUTPUT_MODES[COVER.FAST_MODE]}",
  "{COVER.ROBUST_MODE}": "{COVER.OUTPUT_MODES[COVER.ROBUST_MODE]}"}}[mode]
behavior=os.environ["V5_FAKE_BEHAVIOR"]
if behavior=="RETRY" and mode=="{COVER.FAST_MODE}":
  print("not-json"); raise SystemExit(2)
if behavior in ("BAD_RC", "MATH") and (behavior=="MATH" or mode=="{COVER.FAST_MODE}"):
  p["status"]=p["mathematical_status"]="INCONCLUSIVE"
  p["gates"]["base_budget"]=False
  p["merged_root_exterior"]["candidate_hull_consistency_gate"]=False
  p["merged_root_exterior"]["kernel_gate"]=False
  print(json.dumps(p)); raise SystemExit(0 if behavior=="BAD_RC" else 1)
print(json.dumps(p)); raise SystemExit(0)
'''
        path.write_text(source, encoding="utf-8")
        path.chmod(path.stat().st_mode | stat.S_IXUSR)
        return path

    def invoke(self, index: tuple[int, int, int], behavior: str):
        log = self.root / f"{behavior}-{index}.log"
        probe = self.make_probe(behavior, log)
        with mock.patch.dict(os.environ, {
            "V5_FAKE_LOG": str(log), "V5_FAKE_BEHAVIOR": behavior,
        }, clear=False):
            outcome = COVER._invoke_cell(
                probe, self.config, index, self.run_dir
            )
        return outcome, log.read_text(encoding="utf-8").splitlines()

    def test_fixed_grid_and_mathematical_contract_reject_drift(self) -> None:
        changed = copy.deepcopy(self.config)
        changed["grid"] = [64, 128, 56]
        with self.assertRaisesRegex(COVER.IntegrityError, "exactly"):
            COVER._validate_config(changed)
        changed = copy.deepcopy(self.config)
        changed["cell_contract"]["required_gates"].pop()
        with self.assertRaisesRegex(COVER.IntegrityError, "mathematical"):
            COVER._validate_config(changed)

    def test_atomic_pass_resume_and_exact_gate_inventory(self) -> None:
        index = (0, 0, 0)
        outcome, modes = self.invoke(index, "PASS")
        self.assertEqual((outcome.kind, modes), ("PASS", [COVER.FAST_MODE]))
        cell = self.run_dir / "cells" / COVER._cell_name(index)
        self.assertTrue(cell.is_file())
        self.assertFalse(list((self.run_dir / "cells").glob(".*.tmp")))
        seen, stops, extrema = COVER._scan_cells(
            self.run_dir, self.config, collect_extrema=True
        )
        self.assertEqual((seen, stops), ({index}, ()))
        self.assertIn("min_incidence_base_margin", extrema)
        payload = json.loads(cell.read_text(encoding="utf-8"))
        payload["gates"].pop("base_budget")
        cell.write_text(json.dumps(payload), encoding="utf-8")
        with self.assertRaisesRegex(COVER.CellFormatError, "inventory"):
            COVER._scan_cells(self.run_dir, self.config)

    def test_infrastructure_or_bad_return_protocol_uses_rect2_once(self) -> None:
        for index, behavior in (((0, 0, 1), "RETRY"),
                                ((0, 0, 2), "BAD_RC")):
            outcome, modes = self.invoke(index, behavior)
            self.assertEqual(outcome.kind, "PASS")
            self.assertEqual(modes, [COVER.FAST_MODE, COVER.ROBUST_MODE])
            payload = json.loads((
                self.run_dir / "cells" / COVER._cell_name(index)
            ).read_text(encoding="utf-8"))
            self.assertEqual(payload["driver_execution_provenance"][
                "attempted_modes"], modes)

    def test_mathematical_inconclusive_stops_without_fallback(self) -> None:
        index = (0, 0, 3)
        outcome, modes = self.invoke(index, "MATH")
        self.assertEqual(outcome.kind, "INCONCLUSIVE")
        self.assertEqual(modes, [COVER.FAST_MODE])
        seen, stops, _ = COVER._scan_cells(self.run_dir, self.config)
        self.assertEqual((seen, stops), ({index}, (index,)))

    def test_missing_duplicate_and_binary_hash_drift_are_rejected(self) -> None:
        index = (0, 0, 0)
        self.invoke(index, "PASS")
        seen, _, _ = COVER._scan_cells(self.run_dir, self.config)
        count, sample = COVER._missing_cells(seen)
        self.assertEqual(count, COVER.CELL_COUNT - 1)
        self.assertEqual(sample[0], [0, 0, 1])
        cell = self.run_dir / "cells" / COVER._cell_name(index)
        duplicate = self.run_dir / "cells" / "duplicate.json"
        duplicate.write_bytes(cell.read_bytes())
        with self.assertRaisesRegex(COVER.IntegrityError, "noncanonical"):
            COVER._scan_cells(self.run_dir, self.config)
        duplicate.unlink()

        config_payload = CONFIG.read_bytes()
        (self.run_dir / "config.json").write_bytes(config_payload)
        binary = self.run_dir / "probe"
        binary.write_bytes(b"fake-binary")
        binary.chmod(0o755)
        manifest = {
            "schema_version": COVER.MANIFEST_SCHEMA,
            "grid": list(COVER.GRID), "cell_count": COVER.CELL_COUNT,
            "config": {"path": "config.json", "sha256": sha256(config_payload)},
            "binary": {"path": "probe", "sha256": sha256(b"fake-binary")},
            "input_hashes": self.config["frozen_inputs"],
        }
        manifest_payload = COVER._json_bytes(manifest)
        (self.run_dir / COVER.MANIFEST_NAME).write_bytes(manifest_payload)
        (self.run_dir / COVER.MANIFEST_HASH_NAME).write_text(
            f"{sha256(manifest_payload)}  {COVER.MANIFEST_NAME}\n", encoding="ascii"
        )
        COVER._validate_run(self.run_dir)
        binary.write_bytes(b"changed")
        with self.assertRaisesRegex(COVER.IntegrityError, "binary hash drift"):
            COVER._validate_run(self.run_dir)


if __name__ == "__main__":
    unittest.main()
