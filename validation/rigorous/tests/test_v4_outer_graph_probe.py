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
SOURCE = RIGOROUS / "src" / "vdp_v4_outer_graph_probe.cpp"
DEFAULT_CAPD_CONFIG = (
    REPOSITORY
    / ".cache/capd-731079217a9254ea-strict/build-strict/bin/capd-config"
)


def endpoint(interval: dict[str, str], side: str) -> float:
    return float.fromhex(interval[f"{side}_hex"])


class V4OuterGraphProbeTests(unittest.TestCase):
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
        cls.temporary = tempfile.TemporaryDirectory(prefix="vdp-v4-outer-")
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
            "rfsn-vdp-v4-outer-graph-probe/2",
        )
        self.assertEqual(self.result["box_id"], "vdp-positive-box-v2")
        self.assertEqual(self.result["scope"], "FULL_ENERGY_COLLAR")
        self.assertFalse(self.result["claim_bearing"])
        boundary = self.result["claim_boundary"]
        self.assertEqual(
            boundary["parent_obligation"],
            (
                "V4.OUTER_GRAPH local mathematical PASS; "
                "Issue #7 aggregate remains PENDING"
            ),
        )
        self.assertEqual(
            boundary["open_scope"],
            [
                "V5 incidence",
                "outer action finite part",
                "Issue #7 aggregate and release",
            ],
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
             "energy_slabs": 2, "z_slabs": 64, "cell_count": 16384},
        )
        corridor = self.result["corridor"]
        self.assertLessEqual(endpoint(corridor["E"], "lower"), -1e-3)
        self.assertGreaterEqual(endpoint(corridor["E"], "upper"), 1e-3)
        self.assertLessEqual(endpoint(corridor["z"], "lower"), 0.0)
        self.assertGreaterEqual(endpoint(corridor["z"], "upper"), 2.0 / 9.0)
        for coordinate in ("beta", "alpha"):
            self.assertLessEqual(
                endpoint(corridor[coordinate], "lower"), -1e-5
            )
            self.assertGreaterEqual(
                endpoint(corridor[coordinate], "upper"), 1e-5
            )
        self.assertLessEqual(endpoint(corridor["nu"], "lower"), 1.0 / 32.0)
        self.assertGreaterEqual(endpoint(corridor["nu"], "upper"), 1.0 / 32.0)
        self.assertLessEqual(
            endpoint(corridor["graph_slope_kappa"], "lower"), 1.0 / 32.0
        )
        self.assertGreaterEqual(
            endpoint(corridor["graph_slope_kappa"], "upper"), 1.0 / 32.0
        )

    def test_positive_energy_root_and_all_corridor_faces_pass(self) -> None:
        obligations = {item["id"]: item for item in self.result["obligations"]}
        self.assertEqual(
            set(obligations),
            {
                "V4.OUTER_GRAPH.POSITIVE_BRANCH",
                "V4.OUTER_GRAPH.CORRIDOR_FACES",
                "V4.OUTER_GRAPH.GENERATOR_BLOCKS",
                "V4.OUTER_GRAPH.CONE_AND_BUNCHING",
                "V4.OUTER_GRAPH.SLOPE_1_32",
            },
        )
        root = obligations["V4.OUTER_GRAPH.POSITIVE_BRANCH"]
        faces = obligations["V4.OUTER_GRAPH.CORRIDOR_FACES"]
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
        for key in ("z_dot_at_z_zero", "E_dot_on_energy_faces"):
            enclosure = faces["enclosures"][key]
            self.assertEqual(endpoint(enclosure, "lower"), 0.0)
            self.assertEqual(endpoint(enclosure, "upper"), 0.0)
        for key, enclosure in faces["enclosures"].items():
            if key in {"z_dot_at_z_zero", "E_dot_on_energy_faces"}:
                continue
            self.assertGreater(endpoint(enclosure, "lower"), 0.0)

    def test_nu_blocks_slope_one_cone_and_third_bunching_pass(self) -> None:
        obligations = {item["id"]: item for item in self.result["obligations"]}
        blocks = obligations["V4.OUTER_GRAPH.GENERATOR_BLOCKS"]
        rates = obligations["V4.OUTER_GRAPH.CONE_AND_BUNCHING"]
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

    def test_graph_slope_one_over_32_cone_is_strict(self) -> None:
        obligations = {item["id"]: item for item in self.result["obligations"]}
        slope = obligations["V4.OUTER_GRAPH.SLOPE_1_32"]
        self.assertEqual(slope["status"], "PASS")
        self.assertLessEqual(
            endpoint(slope["enclosures"]["kappa"], "lower"), 1.0 / 32.0
        )
        self.assertGreaterEqual(
            endpoint(slope["enclosures"]["kappa"], "upper"), 1.0 / 32.0
        )
        self.assertGreater(
            endpoint(slope["enclosures"]["kappa_cone_margin"], "lower"),
            0.0,
        )

    def test_strict_toolchain_run_is_locally_passed(self) -> None:
        self.assertEqual(self.result["rounding_self_test"]["status"], "PASS")
        self.assertEqual(self.result["mathematical_status"], "PASS")
        self.assertEqual(self.result["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
