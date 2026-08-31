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
SOURCE = RIGOROUS / "src" / "vdp_v4_adapted_zero_tube_probe.cpp"
DEFAULT_CAPD_CONFIG = (
    REPOSITORY
    / ".cache/capd-731079217a9254ea-strict/build-strict/bin/capd-config"
)


def endpoint(interval: dict[str, str], side: str) -> float:
    return float.fromhex(interval[f"{side}_hex"])


class V4AdaptedZeroTubeProbeTests(unittest.TestCase):
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
        cls.temporary = tempfile.TemporaryDirectory(prefix="vdp-v4-ad-zero-")
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

    def test_scope_product_cover_and_coordinates_are_explicit(self) -> None:
        self.assertEqual(
            self.result["schema_version"],
            "rfsn-vdp-v4-adapted-zero-tube-probe/3",
        )
        self.assertEqual(self.result["box_id"], "vdp-positive-box-v2")
        self.assertEqual(
            self.result["scope"], "ZERO_ENERGY_ADAPTED_SPECTRAL_TUBE"
        )
        self.assertFalse(self.result["claim_bearing"])
        self.assertEqual(
            self.result["cover"],
            {"r_slabs": 4, "a2_slabs": 8, "epsilon_slabs": 4,
             "z_slabs": 64, "b_slabs": 8, "cell_count": 65536},
        )
        corridor = self.result["corridor"]
        self.assertEqual(endpoint(corridor["H"], "lower"), 0.0)
        self.assertEqual(endpoint(corridor["H"], "upper"), 0.0)
        self.assertLessEqual(endpoint(corridor["z"], "lower"), 0.0)
        self.assertGreaterEqual(endpoint(corridor["z"], "upper"), 2 / 9)
        self.assertLessEqual(endpoint(corridor["b"], "lower"), -1 / 16)
        self.assertGreaterEqual(endpoint(corridor["b"], "upper"), 1 / 16)
        self.assertLessEqual(endpoint(corridor["n"], "lower"), -1e-5)
        self.assertGreaterEqual(endpoint(corridor["n"], "upper"), 1e-5)
        self.assertEqual(
            self.result["coordinate_map"],
            {"C": "C0(z,epsilon)+b+n",
             "D": "sqrt(1-z^2)*(n-b)", "A": "(C+D)/2",
             "B": "(C-D)/2", "alpha": "delta*A",
             "beta": "delta*B"},
        )

    def test_root_faces_and_adapted_graph_tube_pass(self) -> None:
        obligations = {item["id"]: item for item in self.result["obligations"]}
        root = obligations["V4.AD_ZERO.POSITIVE_BRANCH"]
        faces = obligations["V4.AD_ZERO.CORRIDOR_FACES"]
        self.assertEqual(root["status"], "PASS")
        self.assertEqual(faces["status"], "PASS")
        for key in (
            "lambda", "chi_zero", "quadratic_leading",
            "quadratic_constant", "quarter_discriminant", "chi",
            "implicit_chi_derivative", "S", "pi",
        ):
            self.assertGreater(endpoint(root["enclosures"][key], "lower"), 0)
        self.assertLess(
            endpoint(root["enclosures"]["negative_root"], "upper"), 0
        )
        z_zero = faces["enclosures"]["z_dot_at_z_zero"]
        self.assertEqual(endpoint(z_zero, "lower"), 0.0)
        self.assertEqual(endpoint(z_zero, "upper"), 0.0)
        for key, enclosure in faces["enclosures"].items():
            if key != "z_dot_at_z_zero":
                self.assertGreater(endpoint(enclosure, "lower"), 0.0)

    def test_common_cone_rates_and_third_bunching_pass(self) -> None:
        obligations = {item["id"]: item for item in self.result["obligations"]}
        blocks = obligations["V4.AD_ZERO.GENERATOR_BLOCKS"]
        rates = obligations["V4.AD_ZERO.CONE_AND_BUNCHING"]
        self.assertEqual(blocks["status"], "PASS")
        self.assertEqual(rates["status"], "PASS")
        for key in (
            "nu_minus_mu2_C", "nu_minus_B_norm", "nu_minus_D_norm",
            "a_minus_lambda_floor_plus_nu",
        ):
            self.assertGreater(endpoint(blocks["enclosures"][key], "lower"), 0)
        for key in (
            "slope_one_cone_lower", "slope_half_cone_lower",
            "normal_rate_lower", "gamma_0_lower", "gamma_1_lower",
            "gamma_2_lower", "gamma_3_lower",
        ):
            self.assertGreater(endpoint(rates["enclosures"][key], "lower"), 0)

    def test_r2_attachment_enclosure_and_toolchain_pass(self) -> None:
        obligations = {item["id"]: item for item in self.result["obligations"]}
        attachment = obligations["V4.AD_ZERO.R2_ATTACHMENT_TUBE"]
        coverage = obligations[
            "V4.AD_ZERO.R2_K1_TERMINAL_GRAPH_COVERAGE"
        ]
        cone = obligations["V4.AD_ZERO.R2_K1_CONE_COMPATIBILITY"]
        self.assertEqual(attachment["status"], "PASS")
        self.assertEqual(coverage["status"], "PASS")
        self.assertEqual(cone["status"], "PASS")
        self.assertGreater(
            endpoint(attachment["enclosures"]["z_R2"], "lower"), 0
        )
        self.assertGreater(
            endpoint(
                attachment["enclosures"]["z_max_minus_z_R2"], "lower"
            ), 0,
        )
        for key in ("Pi_R2", "q1_R2"):
            self.assertGreater(
                endpoint(attachment["enclosures"][key], "lower"), 0
            )
        tube = attachment["enclosures"]["normal_graph_tube"]
        self.assertLessEqual(endpoint(tube, "lower"), -1e-5)
        self.assertGreaterEqual(endpoint(tube, "upper"), 1e-5)
        for key in (
            "K1_left_coverage_margin", "K1_right_coverage_margin",
            "K1_n_boundary_margin",
        ):
            self.assertGreater(
                endpoint(coverage["enclosures"][key], "lower"), 0
            )
        self.assertLess(
            endpoint(
                coverage["enclosures"]["K1_b_at_outer_minus"], "upper"
            ),
            -13.5e-5,
        )
        self.assertGreater(
            endpoint(
                coverage["enclosures"]["K1_b_at_outer_plus"], "lower"
            ),
            13.5e-5,
        )
        k1_n = coverage["enclosures"]["K1_n"]
        self.assertGreaterEqual(endpoint(k1_n, "lower"), -8e-5)
        self.assertLessEqual(endpoint(k1_n, "upper"), 8e-5)
        self.assertGreater(
            endpoint(cone["enclosures"]["K1_base_tangent"], "lower"), 0
        )
        for key in (
            "K1_slope_7_10_minus_normal_margin",
            "K1_slope_7_10_plus_normal_margin",
        ):
            self.assertGreater(
                endpoint(cone["enclosures"][key], "lower"), 0
            )
        self.assertEqual(self.result["rounding_self_test"]["status"], "PASS")
        self.assertEqual(self.result["mathematical_status"], "PASS")
        self.assertEqual(self.result["status"], "PASS")


if __name__ == "__main__":
    unittest.main()
