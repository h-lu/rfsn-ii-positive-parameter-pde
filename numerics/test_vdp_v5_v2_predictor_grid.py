from __future__ import annotations

import json
import math
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULT_DIRECTORY = HERE / "results/vdp_v5_v2_predictor_grid"
RESULT = RESULT_DIRECTORY / "result.json"


class V2V5PredictorGridTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(RESULT.read_text(encoding="utf-8"))
        cls.points = cls.result["points"]
        cls.by_id = {point["point_id"]: point for point in cls.points}

    def test_full_grid_and_claim_boundary_are_explicit(self) -> None:
        self.assertEqual(
            self.result["status"], "V2_V5_PREDICTOR_GRID_COMPUTED"
        )
        self.assertEqual(
            self.result["evidence_status"], "COMPUTED/E1_NON_RIGOROUS"
        )
        self.assertFalse(self.result["claim_bearing"])
        self.assertEqual(self.result["grid"]["shape"], [5, 9, 5])
        self.assertEqual(self.result["grid"]["point_count"], 225)
        self.assertEqual(len(self.points), 225)
        self.assertEqual(len(self.by_id), 225)
        self.assertIn("fold or root jump", self.result["nonclaim"])
        self.assertIn("prove V5", self.result["nonclaim"])

    def test_exact_levels_cover_the_frozen_v2_box(self) -> None:
        self.assertEqual(
            self.result["grid"]["levels_exact"],
            {
                "r": ["1/100", "1/80", "3/200", "7/400", "1/50"],
                "a2": [
                    "-1/4",
                    "-3/16",
                    "-1/8",
                    "-1/16",
                    "0",
                    "1/16",
                    "1/8",
                    "3/16",
                    "1/4",
                ],
                "epsilon": ["4/5", "9/10", "1", "11/10", "6/5"],
            },
        )
        triples = {
            (
                point["grid_indices"]["r"],
                point["grid_indices"]["a2"],
                point["grid_indices"]["epsilon"],
            )
            for point in self.points
        }
        self.assertEqual(len(triples), 5 * 9 * 5)

    def test_fixed_continuation_tree_uses_an_adjacent_predecessor(self) -> None:
        roots = []
        for point in self.points:
            predecessor_id = point["continuation"]["predecessor"]
            if predecessor_id is None:
                roots.append(point)
                continue
            predecessor = self.by_id[predecessor_id]
            current_indices = point["grid_indices"]
            predecessor_indices = predecessor["grid_indices"]
            manhattan_distance = sum(
                abs(current_indices[key] - predecessor_indices[key])
                for key in ("r", "a2", "epsilon")
            )
            self.assertEqual(manhattan_distance, 1, point["point_id"])
            self.assertTrue(math.isfinite(point["continuation"]["phase_predictor"]))
        self.assertEqual(len(roots), 1)
        self.assertEqual(roots[0]["parameters_exact"], {
            "r": "3/200",
            "a2": "0",
            "epsilon": "1",
        })
        self.assertEqual(
            self.result["point_order"],
            [point["point_id"] for point in self.points],
        )

    def test_every_existing_qa_passes_and_endpoint_data_are_finite(self) -> None:
        self.assertTrue(self.result["aggregate"]["all_existing_qa_pass"])
        for point in self.points:
            self.assertTrue(all(point["qa"].values()), point["point_id"])
            central = point["central_U_minus_4"]
            outer = point["outer_R_2"]
            for value in (
                point["source_phase"],
                point["energy_H"],
                central["Pi"],
                central["Omega"],
                outer["Pi"],
                outer["Omega"],
                outer["alpha"],
                outer["beta"],
            ):
                self.assertTrue(math.isfinite(value), point["point_id"])
            self.assertGreater(point["qa_diagnostics"]["minimum_k1_Pi"], 0.0)
            self.assertGreater(point["qa_diagnostics"]["minimum_k1_q1"], 0.0)
            self.assertGreater(point["qa_diagnostics"]["minimum_outer_pi"], 0.0)

    def test_spectral_coordinates_recompute_from_the_saved_reference(self) -> None:
        b_values = []
        n_values = []
        lambda_values = []
        for point in self.points:
            central = point["central_U_minus_4"]
            reference = central["leading_reference"]
            spectral = central["spectral_coordinates"]
            delta_pi = central["Pi"] - reference["Pi"]
            delta_omega_over_lambda = (
                central["Omega"] - reference["Omega"]
            ) / spectral["lambda"]
            self.assertAlmostEqual(
                spectral["b"],
                0.5 * (delta_pi - delta_omega_over_lambda),
                delta=2.0e-18,
            )
            self.assertAlmostEqual(
                spectral["n"],
                0.5 * (delta_pi + delta_omega_over_lambda),
                delta=2.0e-18,
            )
            b_values.append(spectral["b"])
            n_values.append(spectral["n"])
            lambda_values.append(spectral["lambda"])

        aggregate = self.result["aggregate"]["central_U_minus_4"]
        self.assertEqual(aggregate["b_hull"], [min(b_values), max(b_values)])
        self.assertEqual(aggregate["n_hull"], [min(n_values), max(n_values)])
        self.assertEqual(
            aggregate["lambda_hull"], [min(lambda_values), max(lambda_values)]
        )
        half_widths = aggregate["sampled_symmetric_half_widths"]
        self.assertEqual(
            half_widths["b"], max(abs(min(b_values)), abs(max(b_values)))
        )
        self.assertEqual(
            half_widths["n"], max(abs(min(n_values)), abs(max(n_values)))
        )
        self.assertIn("sampled design lower bounds", half_widths["interpretation"])
        candidate = aggregate["next_strict_corridor_candidate"]
        self.assertEqual(candidate["b_half_width_exact"], "1/100000")
        self.assertEqual(candidate["n_half_width_exact"], "1/200000")
        self.assertGreater(candidate["sampled_b_margin"], 0.0)
        self.assertGreater(candidate["sampled_n_margin"], 0.0)
        self.assertEqual(
            candidate["status"], "DESIGN_CANDIDATE_NOT_INTERVAL_VALIDATED"
        )

    def test_all_sampled_points_have_positive_patch_and_collar_margins(self) -> None:
        patch_minima = []
        collar_minima = []
        for point in self.points:
            patch = point["signed_margins"]["central_patch"]
            collar = point["signed_margins"]["V4_outer_collar"]
            self.assertEqual(patch["minimum"], min(patch["Pi"], patch["Omega"]))
            self.assertEqual(
                collar["minimum"],
                min(
                    collar["energy_E"],
                    collar["z_upper"],
                    collar["alpha"],
                    collar["beta"],
                ),
            )
            self.assertGreater(patch["minimum"], 0.0, point["point_id"])
            self.assertGreater(collar["minimum"], 0.0, point["point_id"])
            patch_minima.append(patch["minimum"])
            collar_minima.append(collar["minimum"])
        aggregate = self.result["aggregate"]
        self.assertEqual(
            aggregate["minimum_signed_central_patch_margin"], min(patch_minima)
        )
        self.assertEqual(
            aggregate["minimum_signed_V4_outer_collar_margin"],
            min(collar_minima),
        )

    def test_archive_intentionally_contains_no_orbit_arrays(self) -> None:
        self.assertFalse(self.result["saved_orbit_arrays"])
        self.assertEqual(list(RESULT_DIRECTORY.glob("*.npz")), [])


if __name__ == "__main__":
    unittest.main()
