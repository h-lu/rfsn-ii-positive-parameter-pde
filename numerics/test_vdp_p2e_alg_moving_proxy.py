from __future__ import annotations

import json
import unittest
from pathlib import Path


HERE = Path(__file__).resolve().parent
RESULT = HERE / "results/vdp_p2e_channel_scout_v2/alg_moving_proxy.json"


class MovingAlgebraicProxyTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.result = json.loads(RESULT.read_text(encoding="utf-8"))
        cls.root_chain = cls.result["root_chain"]
        cls.nodes = cls.root_chain["nodes"]
        cls.points = {
            point["id"]: point for point in cls.result["points"]
        }

    def test_scope_is_explicitly_nonrigorous_and_nonclaim_bearing(self) -> None:
        self.assertEqual(self.result["schema_version"], "ALG-MOVING-PROXY/1")
        self.assertEqual(self.result["evidence_status"], "COMPUTED/E1")
        self.assertEqual(self.result["mathematical_status"], "INCONCLUSIVE")
        self.assertFalse(self.result["claim_bearing"])
        self.assertFalse(self.result["strict_validation"])

    def test_only_the_two_predeclared_points_are_present(self) -> None:
        self.assertEqual(
            self.result["point_order"],
            ["center", "fixed_phase_obstruction_corner"],
        )
        self.assertEqual(set(self.points), set(self.result["point_order"]))

    def test_every_predeclared_qa_check_passes(self) -> None:
        self.assertEqual(
            self.result["status"],
            "COMPUTED/E1_QA_SAMPLED_FLOATING_ROOT_CHAIN_CANDIDATE",
        )
        self.assertTrue(self.root_chain["all_node_matched_qa_passed"])
        self.assertTrue(
            self.root_chain["all_legacy_bracket_diagnostics_consistent"]
        )
        self.assertTrue(self.root_chain["phase_step_passed"])
        for point in self.points.values():
            self.assertTrue(point["all_qa_passed"])
            self.assertTrue(all(point["qa"].values()))

    def test_predeclared_root_chain_has_all_17_passing_nodes(self) -> None:
        expected_qa = {
            "solver_residual",
            "boundary_residual",
            "central_energy",
            "central_energy_alignment",
            "k1_energy",
            "outer_energy",
            "central_k1_seam",
            "k1_outer_seam",
            "same_section",
            "positive_branches",
            "algebraic_orientation",
        }
        self.assertEqual(self.root_chain["segment_count"], 16)
        self.assertEqual(self.root_chain["node_count"], 17)
        self.assertEqual(len(self.nodes), 17)
        self.assertEqual(
            self.root_chain["chain_status"],
            "SAMPLED_FLOATING_ROOT_CHAIN_CANDIDATE",
        )
        for index, node in enumerate(self.nodes):
            self.assertEqual(node["index"], index)
            self.assertEqual(node["continuation_fraction"], f"{index}/16")
            self.assertEqual(set(node["matched_qa"]), expected_qa)
            self.assertTrue(all(node["matched_qa"].values()))
            self.assertTrue(node["all_matched_qa_passed"])
            self.assertTrue(node["default_bvp_state_initialization"])
            self.assertEqual(
                node["phase_predictor_kind"],
                "FROZEN_DATA_INFORMED_E1_SEED",
            )

    def test_root_chain_endpoints_are_the_declared_center_and_corner(
        self,
    ) -> None:
        self.assertEqual(
            self.nodes[0]["parameter_point"],
            {"r": 3.0 / 200.0, "a2": 0.0, "epsilon": 1.0},
        )
        self.assertEqual(
            self.nodes[-1]["parameter_point"],
            {"r": 1.0 / 100.0, "a2": -1.0 / 4.0, "epsilon": 4.0 / 5.0},
        )
        self.assertEqual(
            self.nodes[0]["source_phase"], self.points["center"]["source_phase"]
        )
        self.assertEqual(
            self.nodes[-1]["source_phase"],
            self.points["fixed_phase_obstruction_corner"]["source_phase"],
        )

    def test_frozen_predictor_and_adjacent_root_steps_are_recorded(self) -> None:
        predictor = self.root_chain["phase_predictor"]
        self.assertEqual(
            predictor["status"],
            "FROZEN_EMPIRICAL_E1_SEED_NOT_A_BRANCH_MODEL",
        )
        self.assertIn("axis_continuation.json", predictor["provenance"])
        self.assertIn("empirical convergence seed", predictor["provenance"])
        self.assertIn("neither the BVP equations nor QA", predictor["provenance"])
        derivatives = predictor["axis_derivatives"]
        interaction = predictor["r_a2_interaction_coefficient"]
        observed_steps = []
        for previous, current in zip(
            self.nodes[:-1], self.nodes[1:], strict=True
        ):
            expected_step = current["source_phase"] - previous["source_phase"]
            self.assertAlmostEqual(
                current["root_step_from_previous_node"], expected_step
            )
            observed_steps.append(abs(expected_step))
        for node in self.nodes:
            parameter = node["parameter_point"]
            expected_predictor = (
                predictor["center_phase"]
                + derivatives["r"] * (parameter["r"] - 0.015)
                + derivatives["a2"] * parameter["a2"]
                + derivatives["epsilon"] * (parameter["epsilon"] - 1.0)
                + interaction
                * (parameter["r"] - 0.015)
                * parameter["a2"]
            )
            self.assertAlmostEqual(node["phase_predictor"], expected_predictor)
        self.assertAlmostEqual(
            self.root_chain["maximum_absolute_phase_step"],
            max(observed_steps),
        )
        self.assertLessEqual(
            self.root_chain["maximum_absolute_phase_step"],
            self.result["thresholds"]["continuation_maximum_phase_step_upper"],
        )

    def test_legacy_bracket_is_diagnostic_only(self) -> None:
        self.assertFalse(
            self.root_chain["legacy_bracket_is_acceptance_condition"]
        )
        inside_values = []
        for node in self.nodes:
            diagnostic = node[
                "legacy_center_initialization_bracket_diagnostic"
            ]
            self.assertFalse(diagnostic["acceptance_condition"])
            self.assertTrue(diagnostic["diagnostic_consistent"])
            inside_values.append(diagnostic["inside"])
        self.assertIn(True, inside_values)
        self.assertIn(False, inside_values)
        self.assertIn("root jump", self.root_chain["nonclaim"])
        self.assertIn("not a numerical continuation", self.root_chain["nonclaim"])

    def test_moving_phase_is_not_silently_identified_with_fixed_v2_label(
        self,
    ) -> None:
        center_shift = self.points["center"][
            "source_phase_minus_fixed_v2_label"
        ]
        corner_shift = self.points["fixed_phase_obstruction_corner"][
            "source_phase_minus_fixed_v2_label"
        ]
        self.assertGreater(abs(center_shift), 1.0e-5)
        self.assertGreater(abs(corner_shift), 1.0e-2)

    def test_both_k1_routes_reach_the_declared_terminal_with_negative_pq(
        self,
    ) -> None:
        for point in self.points.values():
            route = point["k1_algebraic_route"]
            self.assertAlmostEqual(route["target_U"], -400.0 / 23.0)
            self.assertLess(abs(route["target_U_residual"]), 1.0e-10)
            self.assertGreater(route["minimum_Pi"], 0.0)
            self.assertGreater(route["minimum_q1"], 0.0)
            self.assertGreater(route["minimum_r1_speed"], 0.0)
            self.assertLess(route["maximum_P"], 0.0)
            self.assertLess(route["maximum_Q"], 0.0)

    def test_exact_nullcline_graph_ladders_agree_with_matched_seams(self) -> None:
        for point in self.points.values():
            graph = point["v4_graph_seam_ladder"]
            self.assertEqual(graph["Q_end_ladder"], [40.0, 60.0, 80.0, 100.0])
            self.assertEqual(
                graph["terminal_condition"],
                "exact alpha_dot=0 normal nullcline",
            )
            self.assertLess(graph["horizon_seam_spread"], 1.0e-12)
            self.assertLess(
                graph["matched_alpha_difference_abs_max"], 5.0e-10
            )
            self.assertGreater(graph["minimum_pi"], 0.0)


if __name__ == "__main__":
    unittest.main()
