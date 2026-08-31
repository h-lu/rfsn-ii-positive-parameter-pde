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
SOURCE = RIGOROUS / "src" / "vdp_v4_zero_energy_graph_probe.cpp"
DEFAULT_CAPD_CONFIG = (
    REPOSITORY
    / ".cache/capd-731079217a9254ea-strict/build-strict/bin/capd-config"
)


def endpoint(interval: dict[str, str], side: str) -> float:
    return float.fromhex(interval[f"{side}_hex"])


class V4ZeroEnergyGraphProbeTests(unittest.TestCase):
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
        cls.temporary = tempfile.TemporaryDirectory(prefix="vdp-v4-zero-")
        binary = Path(cls.temporary.name) / "probe"
        compile_command = [
            "/usr/bin/g++", "-std=c++17", f"-I{RIGOROUS / 'include'}",
            "-O2", "-DNDEBUG", "-fno-fast-math", "-frounding-math",
            "-ffp-contract=off", "-fno-tree-vectorize",
            "-fno-ipa-pure-const", str(SOURCE), "-o", str(binary),
            *cflags, *libraries,
        ]
        subprocess.run(
            compile_command, check=True, cwd=REPOSITORY, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=180,
        )
        completed = subprocess.run(
            [str(binary)], check=True, cwd=REPOSITORY, text=True,
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, timeout=60,
            env={**os.environ, "OMP_NUM_THREADS": "1",
                 "OPENBLAS_NUM_THREADS": "1", "LC_ALL": "C.UTF-8"},
        )
        cls.result = json.loads(completed.stdout)

    @classmethod
    def tearDownClass(cls) -> None:
        if hasattr(cls, "temporary"):
            cls.temporary.cleanup()

    def test_scope_and_gap_free_product_cover_are_explicit(self) -> None:
        self.assertEqual(
            self.result["schema_version"],
            "rfsn-vdp-v4-zero-energy-graph-probe/1",
        )
        self.assertEqual(self.result["box_id"], "vdp-positive-box-v2")
        self.assertEqual(self.result["scope"], "ZERO_ENERGY_SLICE_ONLY")
        self.assertFalse(self.result["claim_bearing"])
        boundary = self.result["claim_boundary"]
        self.assertEqual(
            boundary["parent_obligation"], "V4.OUTER_GRAPH remains PENDING"
        )
        self.assertEqual(
            boundary["open_scope"],
            ["nonzero-E collar", "V5 incidence", "outer asymptotics"],
        )
        parameter_box = self.result["parameter_box"]
        self.assertLessEqual(endpoint(parameter_box["r"], "lower"), 0.01)
        self.assertGreaterEqual(endpoint(parameter_box["r"], "upper"), 0.02)
        self.assertLessEqual(endpoint(parameter_box["a2"], "lower"), -0.25)
        self.assertGreaterEqual(endpoint(parameter_box["a2"], "upper"), 0.25)
        self.assertLessEqual(endpoint(parameter_box["epsilon"], "lower"), 0.8)
        self.assertGreaterEqual(endpoint(parameter_box["epsilon"], "upper"), 1.2)
        self.assertEqual(
            self.result["cover"],
            {"r_slabs": 4, "a2_slabs": 8, "epsilon_slabs": 4,
             "z_slabs": 64, "cell_count": 8192},
        )
        corridor = self.result["corridor"]
        self.assertEqual(endpoint(corridor["E"], "lower"), 0.0)
        self.assertEqual(endpoint(corridor["E"], "upper"), 0.0)
        self.assertLessEqual(endpoint(corridor["z"], "lower"), 0.0)
        self.assertGreaterEqual(endpoint(corridor["z"], "upper"), 0.2)
        for coordinate in ("beta", "alpha"):
            self.assertLessEqual(
                endpoint(corridor[coordinate], "lower"), -1e-5
            )
            self.assertGreaterEqual(
                endpoint(corridor[coordinate], "upper"), 1e-5
            )
        self.assertLessEqual(endpoint(corridor["nu"], "lower"), 1.0 / 32.0)
        self.assertGreaterEqual(endpoint(corridor["nu"], "upper"), 1.0 / 32.0)

    def test_positive_energy_root_and_all_corridor_faces_pass(self) -> None:
        obligations = {item["id"]: item for item in self.result["obligations"]}
        self.assertEqual(
            set(obligations),
            {
                "V4.ZERO_ENERGY_GRAPH.POSITIVE_BRANCH",
                "V4.ZERO_ENERGY_GRAPH.CORRIDOR_FACES",
                "V4.ZERO_ENERGY_GRAPH.GENERATOR_BLOCKS",
                "V4.ZERO_ENERGY_GRAPH.CONE_AND_BUNCHING",
            },
        )
        root = obligations["V4.ZERO_ENERGY_GRAPH.POSITIVE_BRANCH"]
        faces = obligations["V4.ZERO_ENERGY_GRAPH.CORRIDOR_FACES"]
        self.assertEqual(root["status"], "PASS")
        self.assertEqual(faces["status"], "PASS")
        for key in (
            "quadratic_leading", "quadratic_constant_D",
            "quarter_discriminant",
            "chi", "implicit_chi_derivative", "pi",
        ):
            self.assertGreater(endpoint(root["enclosures"][key], "lower"), 0.0)
        self.assertLess(
            endpoint(root["enclosures"]["negative_root"], "upper"), 0.0
        )
        for key in ("z_dot_at_z_zero", "E_dot_at_E_zero"):
            enclosure = faces["enclosures"][key]
            self.assertEqual(endpoint(enclosure, "lower"), 0.0)
            self.assertEqual(endpoint(enclosure, "upper"), 0.0)
        for key, enclosure in faces["enclosures"].items():
            if key in {"z_dot_at_z_zero", "E_dot_at_E_zero"}:
                continue
            self.assertGreater(endpoint(enclosure, "lower"), 0.0)

    def test_nu_blocks_slope_one_cone_and_third_bunching_pass(self) -> None:
        obligations = {item["id"]: item for item in self.result["obligations"]}
        blocks = obligations["V4.ZERO_ENERGY_GRAPH.GENERATOR_BLOCKS"]
        rates = obligations["V4.ZERO_ENERGY_GRAPH.CONE_AND_BUNCHING"]
        self.assertEqual(blocks["status"], "PASS")
        self.assertEqual(rates["status"], "PASS")
        for key in (
            "nu_minus_mu2_C", "nu_minus_B_norm", "nu_minus_D_norm",
            "a_minus_one_minus_nu",
        ):
            self.assertGreater(endpoint(blocks["enclosures"][key], "lower"), 0.0)
        for key in (
            "slope_one_cone_lower", "normal_rate_lower", "gamma_0_lower",
            "gamma_1_lower", "gamma_2_lower", "gamma_3_lower",
        ):
            self.assertGreater(endpoint(rates["enclosures"][key], "lower"), 0.0)

    def test_strict_toolchain_run_is_locally_passed(self) -> None:
        self.assertEqual(self.result["rounding_self_test"]["status"], "PASS")
        self.assertEqual(self.result["mathematical_status"], "PASS")
        self.assertEqual(self.result["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
