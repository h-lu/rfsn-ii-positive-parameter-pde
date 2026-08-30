from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path


DESIGN = Path(__file__).resolve().parents[1] / "design"
sys.path.insert(0, str(DESIGN))

import p2e_pole_axis_cover_scout as scout  # noqa: E402


class P2EPoleAxisCoverScoutTests(unittest.TestCase):
    def test_r_leaf_paths_are_exact_inverse_codes(self) -> None:
        for leaf in range(64):
            path = scout.r_split_path(leaf)
            self.assertEqual(len(path), 3)
            self.assertEqual(scout.r_local_index(path), leaf % 8)

    def test_binary_prefix_cover_accepts_only_complete_partitions(self) -> None:
        self.assertTrue(scout.binary_prefix_cover([()]))
        self.assertTrue(scout.binary_prefix_cover([(0,), (1,)]))
        self.assertTrue(
            scout.binary_prefix_cover([(0, 0), (0, 1), (1,)]))
        self.assertFalse(scout.binary_prefix_cover([(0,), (1, 0)]))
        self.assertFalse(scout.binary_prefix_cover([(0, 0), (1, 1)]))
        self.assertFalse(scout.binary_prefix_cover([(), (0,), (1,)]))

    def test_terminal_command_binds_route_split_and_eta(self) -> None:
        argv = scout.terminal_argv(
            Path("/tmp/probe"), (3, 4, 2), (("r", 1), ("phase", 0)),
            (-1.0e-8, 2.0e-8), "V_STEPS")
        self.assertEqual(argv[:5], ["/tmp/probe", "POLE", "3", "4", "2"])
        self.assertEqual(
            argv[5:], [
                "r", "1", "phase", "0", "pole_route", "V_STEPS",
                "eta_box", "-1e-08", "2e-08",
            ])

    def test_terminal_parser_requires_sequence_and_cone(self) -> None:
        record = {
            "status": "PASS",
            "event_sequence_passed": True,
            "escape_cone_entry": {"applicable": True, "passed": True},
            "pre_escape_no_pole_guard": {
                "applicable": True, "passed": True,
                "escape_section_residual": [-1.0e-15, 1.0e-15]},
            "pole_cone": {"applicable": True, "passed": True},
            "p3_zero_action_entry_bounds": {
                "applicable": True, "passed": True},
        }
        self.assertEqual(scout.parse_terminal(json.dumps(record)), record)
        record["event_sequence_passed"] = False
        with self.assertRaisesRegex(ValueError, "event-sequence"):
            scout.parse_terminal(json.dumps(record))

    def test_terminal_response_is_bound_to_request(self) -> None:
        parent = (3, 4, 2)
        path = (("r", 1), ("phase", 0))
        eta = (-1.0e-8, 2.0e-8)
        parameter_boxes, phase_box, graph_box = scout.expected_request_boxes(
            parent, path, eta)
        record = {
            "scope": "P2E_AXIS_POLE_TERMINAL_FIRST_HIT_CELL_SCOUT",
            "claim_bearing": False,
            "cell": {
                "r_index": 3, "a2_index": 4, "epsilon_index": 2},
            "pole_route": "V_STEPS",
            "split_path": "r:1,phase:0,pole_route:V_STEPS,eta_box",
            "event_sequence_labels": scout.V_STEPS_LABELS,
            "event_sequence_passed": True,
            "leg_return_times": [
                [float(index + 1), float(index + 1) + 0.01]
                for index in range(len(scout.V_STEPS_LABELS))],
            "leg_section_residuals": [
                [-1.0e-15, 1.0e-15]
                for _ in scout.V_STEPS_LABELS],
            "leg_section_speeds": [
                ([-2.0, -1.0] if sign < 0 else [1.0, 2.0])
                for sign in scout.V_STEPS_SIGNS],
            "parameter_box": {
                key: [float(box[0]), float(box[1])]
                for key, box in parameter_boxes.items()},
            "phase": [float(phase_box[0]), float(phase_box[1])],
            "graph_error": list(graph_box),
            "return_time": [20.0, 20.1],
            "escape_cone_entry": {
                "applicable": True, "passed": True,
                "y": [3.0, 4.0], "D": [1.0, 2.0], "K": [1.0, 2.0],
                "gamma": [0.1, 0.2],
                "K_prime_boundary_margin": [1.0, 2.0]},
            "pre_escape_no_pole_guard": {
                "applicable": True, "passed": True,
                "minimum_time": [5.0, 5.1], "minimum_U": [-0.5, -0.4],
                "minimum_P_prime": [1.0, 2.0],
                "maximum_time": [8.0, 8.1], "maximum_U": [0.1, 0.2],
                "maximum_P_prime": [-2.0, -1.0],
                "escape_time": [10.0, 10.1], "escape_P": [-2.0, -1.0],
                "escape_section_residual": [-1.0e-15, 1.0e-15]},
            "pole_cone": {
                "applicable": True, "passed": True,
                "y": [14.0, 15.0], "D": [27.0, 28.0],
                "K": [132.0, 133.0], "y_prime": [1.0, 2.0],
                "K_prime": [1.0, 2.0]},
            "p3_zero_action_entry_bounds": {
                "applicable": True, "passed": True},
            "terminal_U": [-10.0, -10.0],
            "section_residual": [-1.0e-15, 1.0e-15],
            "terminal_speed_strictly_negative": True,
        }
        scout.validate_terminal_response(
            record, parent, path, eta, "V_STEPS")
        record["cell"]["r_index"] = 2
        with self.assertRaisesRegex(ValueError, "cell"):
            scout.validate_terminal_response(
                record, parent, path, eta, "V_STEPS")


if __name__ == "__main__":
    unittest.main()
