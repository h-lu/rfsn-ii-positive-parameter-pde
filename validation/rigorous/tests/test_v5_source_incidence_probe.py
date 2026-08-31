from __future__ import annotations

import json
import math
import os
import shlex
import subprocess
import tempfile
import unittest
from pathlib import Path


RIGOROUS = Path(__file__).resolve().parents[1]
REPOSITORY = RIGOROUS.parents[1]
SOURCE = RIGOROUS / "src" / "vdp_v5_source_incidence_probe.cpp"
RESULT = (
    RIGOROUS
    / "results"
    / "vdp_v5_source_incidence_representative_cell.json"
)
FROZEN_ORIGIN = (
    REPOSITORY
    / "frozen-imports"
    / "rfsn-ii-d54add098545063d5efe8f1d6f062d4cfc116a0d"
    / "source"
    / "validation"
    / "origin-algebraic-heteroclinic"
)
DEFAULT_CAPD_CONFIG = (
    REPOSITORY
    / ".cache/capd-731079217a9254ea-strict/build-strict/bin/capd-config"
)


def endpoint(interval: dict[str, str], side: str) -> float:
    value = float.fromhex(interval[f"{side}_hex"])
    if not math.isfinite(value):
        raise ValueError("non-finite interval endpoint")
    return value


class V5SourceIncidenceRepresentativeCellTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(RESULT.read_text(encoding="utf-8"))

    def test_representative_cell_pass_has_an_explicit_claim_boundary(self) -> None:
        self.assertEqual(
            self.result["schema_version"],
            "rfsn-vdp-v5-source-incidence-cell/1",
        )
        self.assertEqual(self.result["status"], "PASS")
        self.assertEqual(self.result["mathematical_status"], "PASS")
        self.assertFalse(self.result["claim_bearing"])
        self.assertEqual(self.result["box_id"], "vdp-positive-box-v2")
        self.assertEqual(self.result["grid"], [64, 128, 40])
        self.assertEqual(self.result["cell_index"], [32, 64, 20])
        self.assertIn(
            "complete v2 parameter cover",
            self.result["claim_boundary"]["open_scope"],
        )

    def test_all_local_incidence_gates_and_margin_are_strict(self) -> None:
        required_gates = {
            "anchor_faces",
            "exact_source_zero_energy_identity",
            "theta_coordinate_regular",
            "complete_graph_error_half_union",
            "complete_phase_slab_union",
            "continuation_faces",
            "root_derivatives",
            "fixed_eta_n_theta_negative",
            "exterior_seam_P_negative",
            "source_slope_below_17_over_50",
            "graph_slope_contraction",
            "negative_K1_sheet_patch",
            "regular_source_to_terminal_passage",
            "base_budget",
            "nonempty_candidates",
        }
        gates = self.result["gates"]
        self.assertTrue(required_gates.issubset(gates))
        self.assertTrue(all(gates[name] is True for name in required_gates))
        self.assertEqual(self.result["rounding_self_test"]["status"], "PASS")

        phase_cover = self.result["phase_cover"]
        self.assertEqual(phase_cover["slab_count"], 16)
        self.assertEqual(phase_cover["graph_error_halves"], 2)
        self.assertTrue(
            all(
                count > 0
                for count in phase_cover[
                    "zero_candidate_evaluations_by_half"
                ]
            )
        )
        self.assertTrue(
            all(
                count > 0
                for count in phase_cover[
                    "graph_tube_candidate_evaluations_by_half"
                ]
            )
        )

        enclosures = self.result["enclosures"]
        self.assertGreater(
            endpoint(enclosures["incidence_base_margin"], "lower"), 0.0
        )
        self.assertLess(
            endpoint(enclosures["source_abs_db_over_minus_dn"], "upper"),
            17.0 / 50.0,
        )
        terminal_q = enclosures["candidate_terminal_Q"]
        self.assertGreater(endpoint(terminal_q, "lower"), -9.5)
        self.assertLess(endpoint(terminal_q, "upper"), -9.0)
        self.assertEqual(
            len(enclosures["fixed_eta_b_on_n_zero_parameter_derivative"]),
            3,
        )
        self.assertLess(
            endpoint(enclosures["fixed_eta_n_theta"], "upper"), 0.0
        )
        self.assertLess(
            endpoint(enclosures["exterior_seam_P"], "upper"), 0.0
        )


class V5SourceIncidenceSlabSmokeTests(unittest.TestCase):
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
                [str(capd_config), "--cflags"],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            ).stdout
        )
        libraries = shlex.split(
            subprocess.run(
                [str(capd_config), "--libs"],
                check=True,
                text=True,
                stdout=subprocess.PIPE,
            ).stdout
        )
        cls.temporary = tempfile.TemporaryDirectory(prefix="vdp-v5-incidence-")
        cls.addClassCleanup(cls.temporary.cleanup)
        binary = Path(cls.temporary.name) / "probe"
        compile_command = [
            "/usr/bin/g++",
            "-std=c++17",
            f"-I{RIGOROUS / 'include'}",
            f"-I{FROZEN_ORIGIN}",
            "-O2",
            "-DNDEBUG",
            "-fno-fast-math",
            "-frounding-math",
            "-ffp-contract=off",
            "-fno-tree-vectorize",
            "-fno-ipa-pure-const",
            "-Wall",
            "-Wextra",
            "-Werror",
            "-Wno-overloaded-virtual",
            str(SOURCE),
            "-o",
            str(binary),
            *cflags,
            *libraries,
        ]
        subprocess.run(
            compile_command,
            check=True,
            cwd=REPOSITORY,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=240,
        )
        completed = subprocess.run(
            [
                str(binary),
                "slab",
                "64",
                "128",
                "40",
                "32",
                "64",
                "20",
                "7",
            ],
            check=False,
            cwd=REPOSITORY,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=90,
            env={
                **os.environ,
                "OMP_NUM_THREADS": "1",
                "OPENBLAS_NUM_THREADS": "1",
                "LC_ALL": "C.UTF-8",
            },
        )
        if completed.returncode not in (0, 1):
            raise RuntimeError(completed.stderr)
        cls.result = json.loads(completed.stdout)

    def test_candidate_slab_exercises_the_exterior_derivative_route(self) -> None:
        self.assertEqual(
            self.result["schema_version"],
            "rfsn-vdp-v5-source-incidence-probe/1",
        )
        self.assertFalse(self.result["claim_bearing"])
        self.assertFalse(self.result["cover"]["complete_v2_cover"])

        enclosures = self.result["enclosures"]
        self.assertLessEqual(endpoint(enclosures["full_strip_n"], "lower"), 0)
        self.assertGreaterEqual(endpoint(enclosures["full_strip_n"], "upper"), 0)
        self.assertTrue(enclosures["root_derivative_computed"])
        self.assertEqual(
            len(enclosures["fixed_eta_b_on_n_zero_parameter_derivative"]),
            3,
        )
        self.assertLess(endpoint(enclosures["dn_dtheta"], "upper"), 0.0)
        self.assertLess(
            endpoint(enclosures["source_abs_db_over_minus_dn"], "upper"),
            17.0 / 50.0,
        )

    def test_candidate_slab_satisfies_the_local_hard_gates(self) -> None:
        for name in (
            "theta_coordinate_regular",
            "slope_7_10_separation",
            "negative_K1_sheet_patch",
            "source_phase_domain",
            "source_positive_U",
            "no_earlier_finite_seam_hit",
            "reduced_x_clock_regular",
        ):
            self.assertTrue(self.result["gates"][name])
        terminal_q = self.result["enclosures"]["terminal_Q"]
        self.assertGreater(endpoint(terminal_q, "lower"), -9.5)
        self.assertLess(endpoint(terminal_q, "upper"), -9.0)


if __name__ == "__main__":
    unittest.main()
