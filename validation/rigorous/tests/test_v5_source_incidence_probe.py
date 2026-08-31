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
GROUPED_RESULTS = (
    RIGOROUS
    / "results"
    / "vdp_v5_source_incidence_grouped_lower_cell.json",
    RIGOROUS
    / "results"
    / "vdp_v5_source_incidence_grouped_center_cell.json",
    RIGOROUS
    / "results"
    / "vdp_v5_source_incidence_grouped_upper_cell.json",
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
            "rfsn-vdp-v5-source-incidence-cell/2",
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
            "anchor_interval_newton",
            "anchor_root_boxes_contain_zero",
            "exact_source_zero_energy_identity",
            "theta_coordinate_regular",
            "complete_graph_error_half_union",
            "complete_anchor_graph_error_slice_union",
            "complete_phase_slab_union",
            "continuation_faces",
            "phase_monotonicity_on_continuation_cover",
            "root_derivatives",
            "fixed_eta_n_theta_negative",
            "exterior_seam_P_negative",
            "source_slope_below_one_half",
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
        self.assertEqual(phase_cover["anchor_graph_error_slices"], 8)
        self.assertTrue(
            all(self.result["gates"]["anchor_interval_newton_by_slice"])
        )
        self.assertTrue(
            all(self.result["gates"]["anchor_root_contains_zero_by_slice"])
        )
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
            endpoint(enclosures["continuation_n_theta"], "upper"), 0.0
        )
        self.assertLessEqual(
            endpoint(enclosures["anchor_root_normal"], "lower"), 0.0
        )
        self.assertGreaterEqual(
            endpoint(enclosures["anchor_root_normal"], "upper"), 0.0
        )
        self.assertLess(
            endpoint(enclosures["source_abs_db_over_minus_dn"], "upper"),
            1.0 / 2.0,
        )
        contract = self.result["target_graph_contract"]
        self.assertEqual(contract["base_half_width"], "13/100000")
        self.assertEqual(contract["normal_half_width"], "1/10000")
        self.assertEqual(contract["slope_bound"], "7/10")
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


class V5SourceIncidenceGroupedKernelSampleTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.results = [
            json.loads(path.read_text(encoding="utf-8"))
            for path in GROUPED_RESULTS
        ]

    def test_three_disclosed_samples_pass_without_claiming_a_cover(self) -> None:
        self.assertEqual(
            [result["cell_index"] for result in self.results],
            [[0, 0, 0], [32, 64, 20], [63, 127, 39]],
        )
        for result in self.results:
            self.assertEqual(
                result["schema_version"],
                "rfsn-vdp-v5-source-incidence-merged-cell/1",
            )
            self.assertEqual(result["status"], "PASS")
            self.assertEqual(result["mathematical_status"], "PASS")
            self.assertFalse(result["claim_bearing"])
            self.assertEqual(result["box_id"], "vdp-positive-box-v2")
            self.assertEqual(result["grid"], [64, 128, 40])
            self.assertEqual(
                result["rounding_self_test"]["status"], "PASS"
            )
            self.assertIn(
                "complete v2 parameter cover",
                result["claim_boundary"]["open_scope"],
            )
            self.assertGreater(
                endpoint(
                    result["enclosures"]["incidence_base_margin"],
                    "lower",
                ),
                0.0,
            )

    def test_grouped_candidate_hulls_pass_the_cover_consistency_gates(self) -> None:
        for result in self.results:
            phase_cover = result["phase_cover"]
            grouped = result["merged_root_exterior"]
            self.assertEqual(
                grouped["route"],
                "UNIFORM_PHASE_GROUPS_PER_GRAPH_ERROR_HALF",
            )
            self.assertEqual(grouped["group_count_per_half"], 8)
            self.assertEqual(grouped["slabs_per_group"], 2)
            self.assertTrue(grouped["candidate_hull_consistency_gate"])
            self.assertTrue(grouped["kernel_gate"])
            self.assertLess(
                phase_cover["exterior_evaluations"],
                phase_cover["zero_candidate_evaluations"],
            )
            initialized_count = sum(
                sum(half) for half in grouped[
                    "candidate_hull_initialized_by_half_and_group"
                ]
            )
            self.assertEqual(
                phase_cover["exterior_evaluations"], initialized_count
            )
            self.assertEqual(
                phase_cover["terminal_affine_subbox_evaluations"],
                phase_cover["terminal_affine_subboxes_per_evaluation"]
                * phase_cover["exterior_evaluations"],
            )
            initialized = grouped[
                "candidate_hull_initialized_by_half_and_group"
            ]
            phase_hulls = grouped[
                "candidate_phase_hull_by_half_and_group"
            ]
            normal_image_contains_zero = grouped[
                "candidate_hull_normal_image_contains_zero_by_half_and_group"
            ]
            selected_masks = grouped["selected_slab_mask_by_half"]
            self.assertEqual(len(initialized), 2)
            self.assertEqual(len(phase_hulls), 2)
            self.assertEqual(len(normal_image_contains_zero), 2)
            self.assertEqual(len(selected_masks), 2)
            continuation_face = 1.0 / 25000.0
            for half_index, (
                initialized_half,
                phase_hull_half,
                normal_image_half,
                selected_mask,
            ) in enumerate(
                zip(
                    initialized,
                    phase_hulls,
                    normal_image_contains_zero,
                    selected_masks,
                    strict=True,
                )
            ):
                self.assertEqual(len(initialized_half), 8)
                self.assertEqual(len(phase_hull_half), 8)
                self.assertEqual(len(normal_image_half), 8)
                self.assertEqual(len(selected_mask), 16)
                self.assertEqual(
                    sum(selected_mask),
                    phase_cover["zero_candidate_evaluations_by_half"][
                        half_index
                    ],
                )
                self.assertTrue(any(initialized_half))
                for group in range(8):
                    self.assertEqual(
                        initialized_half[group],
                        any(selected_mask[2 * group:2 * group + 2]),
                    )
                self.assertTrue(
                    all(
                        hull is not None if selected else hull is None
                        for selected, hull in zip(
                            initialized_half, phase_hull_half, strict=True
                        )
                    )
                )
                self.assertTrue(
                    all(
                        compatible is True if selected else compatible is None
                        for selected, compatible in zip(
                            initialized_half,
                            normal_image_half,
                            strict=True,
                        )
                    )
                )
                for slab_index, selected in enumerate(selected_mask):
                    if not selected:
                        continue
                    group = slab_index // grouped["slabs_per_group"]
                    self.assertTrue(initialized_half[group])
                    hull = phase_hull_half[group]
                    slab_lower = (
                        -continuation_face
                        + 2.0 * continuation_face * slab_index / 16.0
                    )
                    slab_upper = (
                        -continuation_face
                        + 2.0
                        * continuation_face
                        * (slab_index + 1)
                        / 16.0
                    )
                    self.assertLessEqual(endpoint(hull, "lower"), slab_lower)
                    self.assertGreaterEqual(endpoint(hull, "upper"), slab_upper)

            for name, value in result["gates"].items():
                if isinstance(value, list):
                    self.assertTrue(all(value), name)
                else:
                    self.assertTrue(value, name)


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
            "rfsn-vdp-v5-source-incidence-probe/2",
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
            1.0 / 2.0,
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
