from __future__ import annotations

import json
import math
import sys
import unittest
from fractions import Fraction
from pathlib import Path


DESIGN = Path(__file__).resolve().parents[1] / "design"
sys.path.insert(0, str(DESIGN))

import p2e_pole_axis_cover_scout as scout  # noqa: E402


def outward_float_interval(
        box: tuple[Fraction, Fraction]) -> list[float]:
    lower, upper = float(box[0]), float(box[1])
    if Fraction.from_float(lower) > box[0]:
        lower = math.nextafter(lower, -math.inf)
    if Fraction.from_float(upper) < box[1]:
        upper = math.nextafter(upper, math.inf)
    return [lower, upper]


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

    def test_extra_r_bits_retain_the_exact_requested_rational_cell(self) -> None:
        parent = (3, 4, 2)
        bits = (1, 0, 1, 1, 0, 1, 0)
        path = tuple(("r", bit) for bit in bits)
        parameter_boxes, _phase, _eta = scout.expected_request_boxes(
            parent, path, None)
        local_index = sum(bit << (len(bits) - 1 - index)
                          for index, bit in enumerate(bits))
        subdivisions = 1 << len(bits)
        self.assertEqual(parameter_boxes["r"], (
            Fraction(parent[0] * subdivisions + local_index,
                     400 * subdivisions),
            Fraction(parent[0] * subdivisions + local_index + 1,
                     400 * subdivisions),
        ))
        argv = scout.terminal_argv(
            Path("/tmp/probe"), parent, path, None, "BASE")
        self.assertEqual(
            [argv[index + 1] for index, value in enumerate(argv[:-1])
             if value == "r"],
            [str(bit) for bit in bits],
        )

    def test_matching_interval_rejects_inward_exact_r_endpoint(self) -> None:
        exact = (Fraction(7, 800), Fraction(1, 100))
        inward = [float(exact[0]), outward_float_interval(exact)[1]]
        self.assertGreater(Fraction.from_float(inward[0]), exact[0])
        with self.assertRaisesRegex(ValueError, "does not match"):
            scout.require_matching_interval("exact r", inward, exact)
        scout.require_matching_interval(
            "exact r", outward_float_interval(exact), exact)

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
        v_steps_times = [
            [float(index + 1), float(index + 1) + 0.01]
            for index in range(len(scout.V_STEPS_LABELS))]
        v_steps_times[0] = [1.0, 1.0]
        record = {
            "scope": "P2E_AXIS_POLE_TERMINAL_FIRST_HIT_CELL_SCOUT",
            "claim_bearing": False,
            "cell": {
                "r_index": 3, "a2_index": 4, "epsilon_index": 2},
            "pole_route": "V_STEPS",
            "split_path": "r:1,phase:0,pole_route:V_STEPS,eta_box",
            "event_sequence_labels": scout.V_STEPS_LABELS,
            "event_sequence_passed": True,
            "leg_return_times": v_steps_times,
            "leg_section_residuals": [
                [-1.0e-15, 1.0e-15]
                for _ in scout.V_STEPS_LABELS],
            "leg_section_speeds": [
                ([-2.0, -1.0] if sign < 0 else [1.0, 2.0])
                for sign in scout.V_STEPS_SIGNS],
            "parameter_box": {
                key: outward_float_interval(box)
                for key, box in parameter_boxes.items()},
            "phase": outward_float_interval(phase_box),
            "graph_error": list(graph_box),
            "return_time": [20.0, 20.1],
            "pole_first_down_entry": {
                "applicable": True, "passed": True,
                "method": "DIRECT_U_MINUS_ONE_TWENTIETH_POINCARE",
                "fallback_triggered": False,
                "target_U": [-0.05, -0.05],
                "anchor_U": [0.001, 0.001],
                "anchor_time": [0.0, 0.0],
                "anchor_section_residual": [0.0, 0.0],
                "anchor_P": [0.0, 0.0],
                "pre_zero_clock": [0.0, 0.0],
                "pre_zero_dense_P_hull": [0.0, 0.0],
                "pre_zero_step_count": 0,
                "zero_time": [0.0, 0.0],
                "zero_P": [0.0, 0.0], "zero_Q": [0.0, 0.0],
                "zero_branch_Q": [0.0, 0.0],
                "h0_branch_identity_kind": "NOT_APPLICABLE",
                "post_zero_clock": [0.0, 0.0],
                "post_zero_dense_P_hull": [0.0, 0.0],
                "post_zero_step_count": 0,
                "first_down_time": [1.0, 1.0],
                "first_down_section_residual": [-1.0e-15, 1.0e-15],
                "first_down_P": [-2.0, -1.0],
            },
            "escape_cone_entry": {
                "applicable": True, "passed": True,
                "y": [3.0, 4.0], "D": [1.0, 2.0], "K": [1.0, 2.0],
                "gamma": [0.1, 0.2],
                "K_prime_boundary_margin": [1.0, 2.0]},
            "pre_escape_no_pole_guard": {
                "applicable": True, "passed": True,
                "minimum_time": [5.0, 5.0], "minimum_U": [-0.5, -0.4],
                "minimum_P_prime": [1.0, 2.0],
                "maximum_time": [8.0, 8.0], "maximum_U": [0.1, 0.2],
                "maximum_P_prime": [-2.0, -1.0],
                "escape_time": [10.0, 10.0], "escape_P": [-2.0, -1.0],
                "escape_section_residual": [-1.0e-15, 1.0e-15],
                "method": "DIRECT_SEGMENTED_POINCARE",
                "monotone_passages": {
                    "applicable": False, "passed": True}},
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
        record["pole_first_down_entry"] = {
            "applicable": True, "passed": True,
            "method": "U_POSITIVE_ANCHOR_H0_X_TIME",
            "fallback_triggered": True,
            "target_U": [-0.05, -0.05], "anchor_U": [0.001, 0.001],
            "anchor_time": [0.125, 0.125],
            "anchor_section_residual": [-1.0e-15, 1.0e-15],
            "anchor_P": [-0.04, -0.03],
            "pre_zero_clock": [0.125, 0.125],
            "pre_zero_dense_P_hull": [-0.05, -0.02],
            "pre_zero_step_count": 2,
            "zero_time": [0.25, 0.25],
            "zero_P": [-0.04, -0.03], "zero_Q": [0.035, 0.036],
            "zero_branch_Q": [0.035, 0.036],
            "h0_branch_identity_kind":
                "U_ZERO_P_EQUALS_MINUS_Q_BY_H0_AND_SIGNS",
            "post_zero_clock": [0.75, 0.75],
            "post_zero_dense_P_hull": [-0.09, -0.03],
            "post_zero_step_count": 3,
            "first_down_time": [1.0, 1.0],
            "first_down_section_residual": [-1.0e-15, 1.0e-15],
            "first_down_P": [-2.0, -1.0],
        }
        scout.validate_terminal_response(
            record, parent, path, eta, "V_STEPS")
        record["pole_first_down_entry"]["post_zero_clock"] = [0.5, 0.5]
        with self.assertRaisesRegex(ValueError, "terminal time sum"):
            scout.validate_terminal_response(
                record, parent, path, eta, "V_STEPS")
        record["pole_first_down_entry"]["post_zero_clock"] = [0.75, 0.75]
        record["pole_first_down_entry"]["post_zero_dense_P_hull"] = [
            -0.09, 0.0]
        with self.assertRaisesRegex(ValueError, "post-zero"):
            scout.validate_terminal_response(
                record, parent, path, eta, "V_STEPS")
        record["pole_first_down_entry"]["post_zero_dense_P_hull"] = [
            -0.09, -0.03]
        record["pre_escape_no_pole_guard"].update({
            "method": "H0_RECONDITIONED_MONOTONE_INDEPENDENT_VARIABLES",
            "monotone_passages": {
                "applicable": True,
                "passed": True,
                "labels": scout.MONOTONE_GUARD_LABELS,
                "clocks": [
                    [2.0, 2.0], [2.0, 2.0],
                    [1.0, 1.0], [1.0, 1.0], [1.0, 1.0],
                    [0.5, 0.5], [0.5, 0.5], [1.0, 1.0]],
                "step_counts": [1] * 8,
                "dense_sign_hulls": {
                    "down_P": [-2.0, -1.0],
                    "minimum_approach_F": [1.0, 2.0],
                    "minimum_approach_U": [-0.9, -0.4],
                    "minimum_exit_F": [1.0, 2.0],
                    "rise_P": [1.0, 2.0],
                    "maximum_approach_F": [-2.0, -1.0],
                    "maximum_approach_U": [1.0, 2.0],
                    "maximum_exit_F": [-2.0, -1.0],
                    "post_max_to_zero_P": [-3.0, -0.1],
                    "zero_P": [-3.0, -2.0],
                    "zero_Q": [2.0, 3.0],
                    "zero_branch_Q": [2.0, 3.0],
                    "escape_x_P": [-2.0, -1.0],
                },
            },
        })
        scout.validate_terminal_response(
            record, parent, path, eta, "V_STEPS")
        record["pre_escape_no_pole_guard"]["monotone_passages"][
            "clocks"][0] = [100.0, 101.0]
        with self.assertRaisesRegex(ValueError, "minimum time sum"):
            scout.validate_terminal_response(
                record, parent, path, eta, "V_STEPS")
        record["pre_escape_no_pole_guard"]["monotone_passages"][
            "clocks"][0] = [2.0, 2.0]
        record["pre_escape_no_pole_guard"]["monotone_passages"][
            "dense_sign_hulls"]["escape_x_P"] = [-1.0, 0.0]
        with self.assertRaisesRegex(ValueError, "escape_x_P"):
            scout.validate_terminal_response(
                record, parent, path, eta, "V_STEPS")
        record["pre_escape_no_pole_guard"]["monotone_passages"][
            "dense_sign_hulls"]["escape_x_P"] = [-2.0, -1.0]
        record["pre_escape_no_pole_guard"]["monotone_passages"][
            "dense_sign_hulls"]["zero_branch_Q"] = [0.0, 3.0]
        with self.assertRaisesRegex(ValueError, "zero_branch_Q"):
            scout.validate_terminal_response(
                record, parent, path, eta, "V_STEPS")
        record["pre_escape_no_pole_guard"]["monotone_passages"][
            "dense_sign_hulls"]["zero_branch_Q"] = [2.0, 3.0]
        record["pre_escape_no_pole_guard"]["monotone_passages"][
            "dense_sign_hulls"]["zero_branch_Q"] = [2.0, 3.5]
        with self.assertRaisesRegex(ValueError, "not an intersection"):
            scout.validate_terminal_response(
                record, parent, path, eta, "V_STEPS")
        record["pre_escape_no_pole_guard"]["monotone_passages"][
            "dense_sign_hulls"]["zero_branch_Q"] = [2.0, 3.0]
        turn_times = [
            [float(index + 1), float(index + 1) + 0.01]
            for index in range(len(scout.TURN_REDUCED_LABELS))]
        turn_times[0] = [1.0, 1.0]
        turn_times[3] = [4.0, 4.0]
        turn_times[4] = [5.0, 5.0]
        record.update({
            "pole_route": "TURN_REDUCED",
            "split_path":
                "r:1,phase:0,pole_route:TURN_REDUCED,eta_box",
            "event_sequence_labels": scout.TURN_REDUCED_LABELS,
            "leg_return_times": turn_times,
            "leg_section_residuals": [
                [-1.0e-15, 1.0e-15]
                for _ in scout.TURN_REDUCED_LABELS],
            "leg_section_speeds": [
                ([-2.0, -1.0] if sign < 0 else [1.0, 2.0])
                for sign in scout.TURN_REDUCED_SIGNS],
            "pole_upper_turn_reduced_passage": {
                "applicable": True, "passed": True,
                "seam_U": [-0.05, -0.05],
                "seam_time": [4.0, 4.0],
                "terminal_U": [2.75, 2.75],
                "terminal_time": [5.0, 5.0], "clock": [1.0, 1.0],
                "dense_P_hull": [1.0, 3.0], "dense_step_count": 2},
            "pole_escape_reduced_passage": {
                "applicable": True, "passed": True,
                "method":
                    "PMAX_H0_M_TO_U_ZERO_H0_BRANCH_X_TO_ONE_FIFTH",
                "seam_P": [0.0, 0.0], "seam_time": [5.0, 5.0],
                "pmax_U": [2.0, 3.0], "pmax_V_H0": [-3.0, -2.0],
                "pmax_Q": [1.0, 2.0], "pmax_F": [-6.0, -5.0],
                "m_terminal": [0.1, 0.1], "m_clock": [0.25, 0.25],
                "m_dense_step_count": 2,
                "m_dense_F_hull": [-6.0, -5.0],
                "U_terminal": [0.0, 0.0], "U_clock": [1.0, 1.0],
                "U_dense_step_count": 2,
                "U_dense_P_hull": [-3.0, -0.1],
                "zero_P": [-3.2, -3.0], "zero_Q": [3.0, 3.2],
                "zero_H0_branch_Q": [3.0, 3.2],
                "zero_H0_branch_identity":
                    "P_EQUALS_MINUS_Q_BY_H0_AND_STRICT_SIGNS",
                "terminal_x": [0.2, 0.2],
                "terminal_time": [6.375, 6.375],
                "x_clock": [0.125, 0.125],
                "x_dense_P_hull": [-3.0, -1.0],
                "x_dense_step_count": 2},
        })
        scout.validate_terminal_response(
            record, parent, path, eta, "TURN_REDUCED")
        record["pole_upper_turn_reduced_passage"]["terminal_time"] = [
            5.25, 5.25]
        with self.assertRaisesRegex(ValueError, "terminal time sum"):
            scout.validate_terminal_response(
                record, parent, path, eta, "TURN_REDUCED")
        record["pole_upper_turn_reduced_passage"]["terminal_time"] = [
            5.0, 5.0]
        record["pole_escape_reduced_passage"]["terminal_time"] = [
            6.5, 6.5]
        with self.assertRaisesRegex(ValueError, "terminal time sum"):
            scout.validate_terminal_response(
                record, parent, path, eta, "TURN_REDUCED")
        record["pole_escape_reduced_passage"].update({
            "x_clock": [-0.1, 0.0], "terminal_time": [6.15, 6.25],
        })
        with self.assertRaisesRegex(ValueError, "x clock"):
            scout.validate_terminal_response(
                record, parent, path, eta, "TURN_REDUCED")
        record["pole_escape_reduced_passage"].update({
            "x_clock": [0.125, 0.125],
            "terminal_time": [6.375, 6.375],
        })
        record["cell"]["r_index"] = 2
        with self.assertRaisesRegex(ValueError, "cell"):
            scout.validate_terminal_response(
                record, parent, path, eta, "TURN_REDUCED")


if __name__ == "__main__":
    unittest.main()
