from __future__ import annotations

import json
import os
import shlex
import subprocess
import tempfile
import unittest
from pathlib import Path


RIGOROUS = Path(__file__).resolve().parents[1]
REPOSITORY = RIGOROUS.parents[1]
SOURCE = RIGOROUS / "src" / "vdp_v5_k1_tube_probe.cpp"
DEFAULT_CAPD_CONFIG = (
    REPOSITORY
    / ".cache/capd-731079217a9254ea-strict/build-strict/bin/capd-config"
)


def endpoint(interval: dict[str, str], side: str) -> float:
    return float.fromhex(interval[f"{side}_hex"])


class V5K1TubeProbeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        configured = os.environ.get("RFSN_CAPD_CONFIG")
        capd_config = Path(configured) if configured else DEFAULT_CAPD_CONFIG
        if not capd_config.is_file():
            raise unittest.SkipTest(
                "set RFSN_CAPD_CONFIG to run the compiled CAPD/FILIB probe"
            )
        cflags = shlex.split(
            subprocess.run(
                [str(capd_config), "--cflags"], check=True, text=True,
                stdout=subprocess.PIPE,
            ).stdout
        )
        libraries = shlex.split(
            subprocess.run(
                [str(capd_config), "--libs"], check=True, text=True,
                stdout=subprocess.PIPE,
            ).stdout
        )
        cls.temporary = tempfile.TemporaryDirectory(prefix="vdp-v5-k1-")
        binary = Path(cls.temporary.name) / "probe"
        subprocess.run(
            [
                "/usr/bin/g++", "-std=c++17",
                f"-I{RIGOROUS / 'include'}", "-O2", "-DNDEBUG",
                "-fno-fast-math", "-frounding-math", "-ffp-contract=off",
                "-fno-tree-vectorize", "-fno-ipa-pure-const",
                str(SOURCE), "-o", str(binary), *cflags, *libraries,
            ],
            check=True, cwd=REPOSITORY, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180,
        )
        completed = subprocess.run(
            [str(binary)], check=True, cwd=REPOSITORY, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180,
            env={
                **os.environ,
                "OMP_NUM_THREADS": "1",
                "OPENBLAS_NUM_THREADS": "1",
                "LC_ALL": "C.UTF-8",
            },
        )
        cls.result = json.loads(completed.stdout)

    @classmethod
    def tearDownClass(cls) -> None:
        if hasattr(cls, "temporary"):
            cls.temporary.cleanup()

    def test_scope_and_gap_free_cover(self) -> None:
        self.assertEqual(
            self.result["schema_version"],
            "rfsn-vdp-v5-k1-tube-probe/2",
        )
        self.assertEqual(self.result["box_id"], "vdp-positive-box-v2")
        self.assertEqual(
            self.result["scope"], "ZERO_ENERGY_FINITE_RESOLVED_K1_TUBE"
        )
        self.assertEqual(
            self.result["cover"],
            {
                "r_slabs": 8,
                "a2_slabs": 32,
                "epsilon_slabs": 8,
                "r1_slabs": 32,
                "b_slabs": 16,
                "cell_count": 1_048_576,
            },
        )
        tube = self.result["tube"]
        for coordinate in ("b", "n"):
            self.assertLessEqual(endpoint(tube[coordinate], "lower"), -1e-4)
            self.assertGreaterEqual(endpoint(tube[coordinate], "upper"), 1e-4)
        self.assertLessEqual(endpoint(tube["graph_slope"], "lower"), 0.7)
        self.assertGreaterEqual(endpoint(tube["graph_slope"], "upper"), 0.7)

    def test_positive_root_clock_and_face_scale(self) -> None:
        obligations = {item["id"]: item for item in self.result["obligations"]}
        branch = obligations["V5.K1.POSITIVE_ROOT_AND_CLOCK"]
        self.assertEqual(branch["status"], "PASS")
        for key in (
            "q1_radicand", "q1", "Pi", "r1_speed",
            "positive_face_time_scale",
        ):
            self.assertGreater(endpoint(branch["enclosures"][key], "lower"), 0)

    def test_all_isolating_faces_and_slope_seven_tenths_cone_pass(self) -> None:
        obligations = {item["id"]: item for item in self.result["obligations"]}
        faces = obligations["V5.K1.TUBE_FACES"]
        cone = obligations["V5.K1.PROJECTIVE_CONE"]
        self.assertEqual(faces["status"], "PASS")
        self.assertEqual(cone["status"], "PASS")
        for enclosure in faces["enclosures"].values():
            self.assertGreater(endpoint(enclosure, "lower"), 0)
        self.assertLess(endpoint(cone["enclosures"]["C_upper"], "upper"), 0)
        self.assertGreater(
            endpoint(cone["enclosures"]["a_normal_lower"], "lower"), 0
        )
        self.assertGreater(
            endpoint(cone["enclosures"]["cone_margin"], "lower"), 0
        )
        slope = endpoint(cone["enclosures"]["graph_slope"], "lower")
        conservative = slope * (
            endpoint(cone["enclosures"]["a_normal_lower"], "lower")
            - endpoint(cone["enclosures"]["C_upper"], "upper")
            - slope * endpoint(
                cone["enclosures"]["B_cross_upper"], "upper"
            )
        ) - endpoint(cone["enclosures"]["D_cross_upper"], "upper")
        self.assertGreater(conservative, 0)

    def test_status_and_claim_boundary_remain_local(self) -> None:
        self.assertEqual(self.result["rounding_self_test"]["status"], "PASS")
        self.assertEqual(self.result["mathematical_status"], "PASS")
        self.assertEqual(self.result["status"], "PASS")
        self.assertFalse(self.result["claim_bearing"])
        self.assertEqual(
            self.result["claim_boundary"]["open_scope"],
            [
                "central regraph",
                "source first hit",
                "V5 incidence",
            ],
        )


if __name__ == "__main__":
    unittest.main()
