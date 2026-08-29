from __future__ import annotations

import json
import unittest
from fractions import Fraction

from validation.rigorous import p3_pole_analytic_v2 as pole


def q(item: dict[str, str]) -> Fraction:
    return Fraction(int(item["numerator"]), int(item["denominator"]))


class P3PoleAnalyticV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = pole.build_certificate()

    def test_stored_certificate_is_deterministic(self) -> None:
        stored = json.loads(pole.DEFAULT_OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(stored, self.certificate)

    def test_v2_is_exactly_the_v3_positive_box_shape(self) -> None:
        target = self.certificate["target"]["exact_identification"]
        self.assertEqual(q(target["A"]), Fraction(1, 4))
        self.assertEqual(q(target["r_p"]), Fraction(1, 50))
        self.assertTrue(target["r_interval_equals_half_rp_to_rp"])
        radius = self.certificate["local_lemma_atoms"][0]["inequalities"]
        self.assertEqual(
            q(radius["sqrt_epsilon_plus_A_rp_cubed_lhs"]),
            Fraction(11, 5_000_000),
        )
        self.assertGreater(q(radius["margin_to_one_quarter"]), 0)
        self.assertGreater(q(radius["margin_to_one"]), 0)

    def test_cone_and_conditional_gate_margins_are_strict(self) -> None:
        atoms = {item["id"]: item
                 for item in self.certificate["local_lemma_atoms"]}
        cone = atoms["V3.POLE.CONE_INWARD"]["boundary_lower_bounds"]
        self.assertEqual(q(cone["y_prime_at_D_zero"]), Fraction(2029, 135))
        self.assertEqual(q(cone["K_prime_at_K_zero"]), Fraction(3788, 27))
        self.assertGreater(q(cone["derivative_of_y_prime_lower_polynomial"]), 0)
        self.assertGreater(q(cone["derivative_of_K_prime_lower_polynomial"]), 0)
        gate = atoms["V3.POLE.GATE_MARGIN_IMPLICATION"]["consequent"]
        self.assertGreater(q(gate["margin_above_51"]), 0)
        self.assertGreater(q(gate["margin_above_852"]), 0)

    def test_finite_time_bound_is_exactly_conditional(self) -> None:
        atoms = {item["id"]: item
                 for item in self.certificate["local_lemma_atoms"]}
        tail = atoms["V3.POLE.FINITE_TIME_TAIL_IMPLICATION"]
        self.assertEqual(tail["scope"], "CONDITIONAL_LEMMA_ONLY")
        self.assertEqual(
            q(tail["bounds"]["remaining_physical_time_from_gate_upper"]),
            Fraction(208, 375),
        )

    def test_parent_obligations_fail_closed(self) -> None:
        self.assertEqual(self.certificate["mathematical_status"], "INCONCLUSIVE")
        self.assertFalse(self.certificate["claim_bearing"])
        self.assertEqual(
            {item["id"]: item["status"]
             for item in self.certificate["parent_obligations"]},
            {"V3.SOURCE_TO_POLE": "INCONCLUSIVE",
             "V3.POLE_TAIL": "INCONCLUSIVE"},
        )
        self.assertEqual(len(self.certificate["required_interfaces"]), 2)


if __name__ == "__main__":
    unittest.main()
