from __future__ import annotations

import json
import unittest

from validation.rigorous import p3_pole_action_tail_v2 as action


def lower(item: dict[str, str]) -> float:
    return float.fromhex(item["lower_hex"])


def upper(item: dict[str, str]) -> float:
    return float.fromhex(item["upper_hex"])


class P3PoleActionTailV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = action.build_certificate()

    def test_stored_result_is_deterministic(self) -> None:
        stored = json.loads(action.OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(stored, self.certificate)

    def test_density_is_integrable_and_tail_is_finite(self) -> None:
        density = self.certificate["regularized_density"]
        tail = self.certificate["action_tail"]
        self.assertEqual(density["integrability_status"], "PASS")
        self.assertEqual(tail["finiteness_status"], "PASS")
        self.assertLess(upper(tail["absolute_upper"]), 0.003)

    def test_frozen_quality_gates_have_a_strict_counterexample(self) -> None:
        witness = self.certificate["strict_negative_witness"]
        self.assertEqual(witness["density_gate_status"], "FAIL")
        self.assertEqual(witness["tail_gate_status"], "FAIL")
        self.assertGreater(
            lower(witness["normalized_density_absolute_lower"]), 1000.0
        )
        self.assertGreater(lower(witness["tail_absolute_lower"]), 1.0e-6)
        tail_interval = witness["tail_interval"]
        self.assertLess(upper(tail_interval), 0.0)

    def test_each_label_C1_tail_bound_passes(self) -> None:
        self.assertTrue(all(
            item["status"] == "PASS"
            and upper(item["tail_derivative_abs_upper"]) < 1.0e-5
            for item in self.certificate["label_C1"].values()
        ))

    def test_moving_cut_is_exact_but_parent_remains_open(self) -> None:
        self.assertEqual(
            self.certificate["moving_cut_identity"]["status"],
            "PASS_EXACT_ADDITIVITY",
        )
        self.assertEqual(
            self.certificate["status"],
            "STRICT_NEGATIVE_FROZEN_ACTION_QUALITY_GATES",
        )
        self.assertEqual(
            {item["id"]: item["status"]
             for item in self.certificate["parent_obligations"]},
            {"V3.SOURCE_TO_POLE": "INCONCLUSIVE",
             "V3.POLE_TAIL": "INCONCLUSIVE"},
        )


if __name__ == "__main__":
    unittest.main()
