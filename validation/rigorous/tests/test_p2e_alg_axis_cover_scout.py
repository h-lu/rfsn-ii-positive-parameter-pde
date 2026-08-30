from __future__ import annotations

import json
import sys
import unittest
from pathlib import Path
from unittest import mock


DESIGN = Path(__file__).resolve().parents[1] / "design"
sys.path.insert(0, str(DESIGN))

import p2e_alg_axis_cover_scout as scout  # noqa: E402


def source_record(leaf: tuple[int, int, int]) -> dict:
    boxes = scout.source_parameter_boxes(leaf)
    return {
        "status": "PASS",
        "claim_bearing": False,
        "scope": "P2E_DIRECT_SOURCE_ROOT_CONDITIONED_LEAF",
        "target_kind": scout.TARGET_KIND,
        "leaf": list(leaf),
        "split_path": "",
        "parameter_box": {
            key: [float(box[0]), float(box[1])]
            for key, box in boxes.items()},
        "target_phase": [
            float(scout.ALG_PHASE_LO), float(scout.ALG_PHASE_HI)],
        "theta0": [1.0, 1.0],
        "theta_parameter_slopes": [[0.0, 0.0]] * 3,
        "trial_delta": [-4.0e-4, 4.0e-4],
        "interval_newton": [-2.0e-5, 2.0e-5],
        "phase_derivative": [0.8, 1.2],
        "log_radial_rate": [0.6, 0.8],
        "phase_rate": [0.5, 0.7],
        "root_eta": [-2.0e-8, 3.0e-8],
        "root_stable_coordinates": [[-1.0e-5, 1.0e-5]] * 2,
        "root_return_time": [11.0, 12.0],
        "root_phase_residual": [-1.0e-14, 1.0e-14],
    }


def terminal_record(parent: tuple[int, int, int], r_path: tuple[int, ...],
                    a2_path: tuple[int, ...], eta=None) -> dict:
    boxes = scout.terminal_request_boxes(parent, r_path, a2_path)
    tail = {
        "applicable": True,
        "passed": True,
        "seam_time": [8.0, 9.0],
        "seam_P": [-2.0, -1.0],
        "seam_Q": [-1.0, 0.0],
        "tail_clock": [1.0, 2.0],
        "dense_step_count": 100,
        "dense_w_hull": [0.01, 4.0],
        "tau_nodes": [
            [77 * index / 6000, 77 * index / 6000]
            for index in range(1, 16)],
        "w_nodes": [[0.1, 1.0] for _ in range(15)],
        "q_nodes": [[-2.0, 2.0] for _ in range(15)],
        "energy_reconstruction_identity": True,
        "energy_reconstruction_identity_kind":
            "BY_EXACT_ZERO_ENERGY_FORMULA_CONSTRUCTION",
        "naive_interval_energy_diagnostic_nonpredicate": [-1.0, 1.0],
    }
    path_parts = [*(f"r:{bit}" for bit in r_path),
                  *(f"a2:{bit}" for bit in a2_path)]
    if eta is not None:
        path_parts.append("eta_box")
    return {
        "status": "PASS",
        "scope": "P2E_AXIS_ALG_TERMINAL_FIRST_HIT_CELL_SCOUT",
        "claim_bearing": False,
        "cell": {"r_index": parent[0], "a2_index": parent[1],
                 "epsilon_index": parent[2]},
        "split_path": ",".join(path_parts),
        "pole_route": "BASE",
        "parameter_box": {
            key: [float(box[0]), float(box[1])]
            for key, box in boxes.items()},
        "phase": [float(scout.ALG_PHASE_LO), float(scout.ALG_PHASE_HI)],
        "graph_error": list(scout.PROVED_ETA if eta is None else eta),
        "return_time": [9.0, 11.0],
        "event_sequence_labels": scout.ALG_LABELS,
        "leg_return_times": [[0.1, 1.0] for _ in range(7)],
        "leg_section_residuals": [[-1.0e-14, 1.0e-14] for _ in range(7)],
        "leg_section_speeds": [[-3.0, -0.1] for _ in range(7)],
        "event_sequence_passed": True,
        "terminal_U": [float(scout.ALG_TERMINAL_U),
                       float(scout.ALG_TERMINAL_U)],
        "terminal_P": [-20.0, -1.0],
        "terminal_V": [-100.0, 100.0],
        "terminal_Q": [-20.0, 20.0],
        "section_residual": [-1.0e-14, 1.0e-14],
        "terminal_speed_strictly_negative": True,
        "alg_reduced_zero_energy_tail": tail,
    }


class P2EAlgAxisCoverScoutTests(unittest.TestCase):
    def test_r_leaf_codes_and_exact_prefix_cover(self) -> None:
        for local_r in range(8):
            self.assertEqual(
                scout.r_local_index(scout.r_split_path(local_r)), local_r)
        self.assertTrue(scout.exact_binary_prefix_cover([()]))
        self.assertTrue(scout.exact_binary_prefix_cover([(0,), (1,)]))
        self.assertTrue(scout.exact_binary_prefix_cover(
            [(0, 0), (0, 1), (1,)]))
        self.assertFalse(scout.exact_binary_prefix_cover([(0,)]))
        self.assertFalse(scout.exact_binary_prefix_cover(
            [(), (0,), (1,)]))

    def test_terminal_command_binds_only_r_a2_and_optional_eta(self) -> None:
        argv = scout.terminal_argv(
            Path("/tmp/probe"), (3, 4, 2), (1, 0, 1), (0, 1), None)
        self.assertEqual(argv, [
            "/tmp/probe", "ALG", "3", "4", "2",
            "r", "1", "r", "0", "r", "1", "a2", "0", "a2", "1",
        ])
        argv = scout.terminal_argv(
            Path("/tmp/probe"), (3, 4, 2), (1, 0, 1), (),
            (-1.0e-8, 2.0e-8))
        self.assertEqual(argv[-3:], ["eta_box", "-1e-08", "2e-08"])

    def test_source_parser_is_strictly_bound_to_alg_leaf(self) -> None:
        leaf = (25, 4, 2)
        record = source_record(leaf)
        predictor = [25, 4, 2, "1", "0", "0", "0", "0", "0.0004"]
        stdout = "diagnostic\n" + scout.SOURCE_PREFIX + json.dumps(record)
        self.assertEqual(scout.parse_source(stdout, leaf, predictor), record)
        record["theta0"] = [0.9, 0.9]
        with self.assertRaisesRegex(ValueError, "theta0"):
            scout.validate_source_response(record, leaf, predictor)
        record["theta0"] = [1.0, 1.0]
        record["target_kind"] = "DIRECT_POLE_CENTER"
        with self.assertRaisesRegex(ValueError, "target kind"):
            scout.validate_source_response(record, leaf)

    def test_matching_intervals_cannot_narrow_requests(self) -> None:
        scout.require_matching_interval("same", [0.0, 1.0], [0.0, 1.0])
        with self.assertRaisesRegex(ValueError, "does not match"):
            scout.require_matching_interval(
                "narrow", [1.0e-15, 1.0], [0.0, 1.0])
        scout.interval_subset([0.25, 0.75], [0.0, 1.0], "contained")
        with self.assertRaisesRegex(ValueError, "not contained"):
            scout.interval_subset([-1.0e-15, 0.75], [0.0, 1.0], "outside")

    def test_terminal_validator_checks_seven_legs_and_weighted_tail(self) -> None:
        parent = (3, 4, 2)
        r_path = (1, 0, 1)
        a2_path = (0, 1)
        eta = (-1.0e-8, 2.0e-8)
        record = terminal_record(parent, r_path, a2_path, eta)
        scout.validate_terminal_response(
            record, parent, r_path, a2_path, eta)
        record["alg_reduced_zero_energy_tail"]["dense_w_hull"] = [-0.1, 4.0]
        with self.assertRaisesRegex(ValueError, "dense w hull"):
            scout.validate_terminal_response(
                record, parent, r_path, a2_path, eta)

    def test_adaptive_cover_returns_an_exact_a2_partition(self) -> None:
        parent = (3, 4, 2)

        def fake_run(job, _executable, _timeout):
            requested_parent, r_path, a2_path, eta = job
            if not a2_path:
                return requested_parent, r_path, a2_path, 10, None, "wrap"
            value = terminal_record(
                requested_parent, r_path, a2_path, eta)
            return requested_parent, r_path, a2_path, 0, value, ""

        with mock.patch.object(scout, "run_terminal_job", side_effect=fake_run):
            passed, failed, stats = scout.adaptive_terminal_cover(
                [(parent, (), None)], Path("/tmp/probe"), 1.0, 2, 1)
        self.assertFalse(failed)
        records = passed[(parent, ())]
        self.assertTrue(scout.exact_binary_prefix_cover(
            tuple(record["a2_path"]) for record in records))
        self.assertEqual(stats["terminal_attempts"], 3)


if __name__ == "__main__":
    unittest.main()
