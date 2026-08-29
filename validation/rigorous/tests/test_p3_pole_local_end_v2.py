from __future__ import annotations

import json
import unittest

from validation.rigorous import p3_pole_local_end_v2 as local_end


def lower(item: dict[str, str]) -> float:
    return float.fromhex(item["lower_hex"])


def upper(item: dict[str, str]) -> float:
    return float.fromhex(item["upper_hex"])


class P3PoleLocalEndV2Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate = local_end.build_certificate()

    def test_stored_one_shot_result_is_deterministic(self) -> None:
        stored = json.loads(local_end.OUTPUT.read_text(encoding="utf-8"))
        self.assertEqual(stored, self.certificate)

    def test_c0_self_map_and_contraction_pass(self) -> None:
        atoms = {item["id"]: item["status"]
                 for item in self.certificate["atoms"]}
        self.assertEqual(atoms["V3.POLE_TAIL.LOCAL_C0_SELF_MAP"], "PASS")
        self.assertEqual(atoms["V3.POLE_TAIL.LOCAL_C0_CONTRACTION"], "PASS")
        majorant = self.certificate["analytic_majorant"]
        self.assertGreater(lower(majorant["self_map_margin"]), 0.0)
        self.assertLess(upper(majorant["contraction_upper"]), 0.5)

    def test_full_coordinate_jacobian_excludes_zero(self) -> None:
        jacobian = self.certificate["full_coordinate_jacobian"]
        self.assertEqual(jacobian["status"], "PASS")
        self.assertGreater(lower(jacobian["interval"]), 4.99)
        self.assertLess(upper(jacobian["interval"]), 5.01)
        self.assertGreater(lower(jacobian["absolute_lower"]), 0.01)

    def test_flow_and_power_spectra_are_not_conflated(self) -> None:
        spectra = self.certificate["regular_singular_spectra"]
        self.assertEqual(
            spectra["desingularized_flow_spectrum"],
            ["-1", "-4", "0", "0", "+1"],
        )
        self.assertEqual(
            spectra["normalized_power_spectrum"],
            ["-1", "0", "0", "1", "4"],
        )

    def test_parent_claims_remain_inconclusive(self) -> None:
        self.assertEqual(self.certificate["status"], "LOCAL_C1_BLOCK_PASS")
        self.assertEqual(self.certificate["mathematical_status"],
                         "PARTIAL_LOCAL_PASS")
        self.assertFalse(self.certificate["claim_bearing"])
        self.assertEqual(
            {item["id"]: item["status"]
             for item in self.certificate["parent_obligations"]},
            {"V3.SOURCE_TO_POLE": "INCONCLUSIVE",
             "V3.POLE_TAIL": "INCONCLUSIVE"},
        )


if __name__ == "__main__":
    unittest.main()
