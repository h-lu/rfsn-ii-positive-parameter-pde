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
SOURCE = RIGOROUS / "src" / "vdp_v5_central_attachment_probe.cpp"
DEFAULT_CAPD_CONFIG = (
    REPOSITORY
    / ".cache/capd-731079217a9254ea-strict/build-strict/bin/capd-config"
)


def endpoint(interval: dict[str, str], side: str) -> float:
    return float.fromhex(interval[f"{side}_hex"])


class V5CentralAttachmentProbeTests(unittest.TestCase):
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
        cls.temporary = tempfile.TemporaryDirectory(prefix="vdp-v5-central-")
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
            "rfsn-vdp-v5-central-attachment-probe/2",
        )
        self.assertEqual(self.result["box_id"], "vdp-positive-box-v2")
        self.assertEqual(
            self.result["scope"],
            "ZERO_ENERGY_K1_TO_CENTRAL_LOWER_FACE",
        )
        self.assertEqual(self.result["section"], "U=-4")
        self.assertEqual(
            self.result["cover"],
            {
                "r_slabs": 8,
                "a2_slabs": 32,
                "epsilon_slabs": 8,
                "b_slabs": 8,
                "n_slabs": 8,
                "cell_count": 131_072,
            },
        )
        b_tube = self.result["tube"]["b"]
        self.assertLessEqual(endpoint(b_tube, "lower"), -13.5e-5)
        self.assertGreaterEqual(endpoint(b_tube, "upper"), 13.5e-5)
        n_tube = self.result["tube"]["n"]
        self.assertLessEqual(endpoint(n_tube, "lower"), -8e-5)
        self.assertGreaterEqual(endpoint(n_tube, "upper"), 8e-5)
        slope = self.result["tube"]["graph_slope"]
        self.assertLessEqual(endpoint(slope, "lower"), 0.7)
        self.assertGreaterEqual(endpoint(slope, "upper"), 0.7)

    def test_positive_root_and_fixed_patch_pass(self) -> None:
        obligations = {item["id"]: item for item in self.result["obligations"]}
        root = obligations["V5.CENTRAL.POSITIVE_ROOT"]
        patch = obligations["V5.CENTRAL.FIXED_PATCH"]
        self.assertEqual(root["status"], "PASS")
        self.assertEqual(patch["status"], "PASS")
        for key in ("q1_radicand", "q1", "Pi"):
            self.assertGreater(endpoint(root["enclosures"][key], "lower"), 0)
        for key in (
            "P_lower_margin", "P_upper_margin",
            "V_lower_margin", "V_upper_margin",
            "Q_lower_margin", "Q_upper_margin",
        ):
            self.assertGreater(endpoint(patch["enclosures"][key], "lower"), 0)
        p = patch["enclosures"]["P"]
        v = patch["enclosures"]["V"]
        q = patch["enclosures"]["Q"]
        self.assertGreaterEqual(endpoint(p, "lower"), -6 / 5)
        self.assertLessEqual(endpoint(p, "upper"), -11 / 10)
        self.assertGreaterEqual(endpoint(v, "lower"), -16)
        self.assertLessEqual(endpoint(v, "upper"), -31 / 2)
        self.assertGreaterEqual(endpoint(q, "lower"), -19 / 2)
        self.assertLessEqual(endpoint(q, "upper"), -9)

    def test_transition_and_regraph_are_uniformly_transverse(self) -> None:
        obligations = {item["id"]: item for item in self.result["obligations"]}
        transverse = obligations["V5.CENTRAL.TRANSVERSALITY"]
        regularity = obligations["V5.CENTRAL.CHART_REGULARITY"]
        regraph = obligations["V5.CENTRAL.SLOPE_7_10_REGRAPH"]
        for obligation in (transverse, regularity, regraph):
            self.assertEqual(obligation["status"], "PASS")
        for enclosure in transverse["enclosures"].values():
            self.assertGreater(endpoint(enclosure, "lower"), 0)
        self.assertGreater(
            endpoint(
                regularity["enclosures"][
                    "chart_determinant_kappa_sigma_minus_3"
                ],
                "lower",
            ),
            0,
        )
        self.assertGreater(
            endpoint(
                regularity["enclosures"][
                    "spectral_block_abs_determinant_2AK"
                ],
                "lower",
            ),
            0,
        )
        self.assertGreater(
            endpoint(
                regraph["enclosures"]["minus_dV_db_lower_bound"],
                "lower",
            ),
            0,
        )
        self.assertLess(
            endpoint(regraph["enclosures"]["abs_G_V_upper_bound"], "upper"),
            2.221,
        )
        self.assertGreater(
            endpoint(regraph["enclosures"]["abs_G_V_cap_margin"], "lower"),
            0,
        )

    def test_status_and_claim_boundary_are_honest(self) -> None:
        self.assertEqual(self.result["rounding_self_test"]["status"], "PASS")
        self.assertEqual(self.result["mathematical_status"], "PASS")
        self.assertEqual(self.result["status"], "PASS")
        self.assertFalse(self.result["claim_bearing"])
        self.assertEqual(
            self.result["claim_boundary"]["open_scope"],
            [
                "complete-box canonical-source incidence",
                "claim-bearing V5 composition",
            ],
        )


if __name__ == "__main__":
    unittest.main()
