from __future__ import annotations

import copy
import json
import sys
import tempfile
import unittest
from fractions import Fraction
from pathlib import Path


DESIGN = Path(__file__).resolve().parents[1] / "design"
sys.path.insert(0, str(DESIGN))

import p2d_normal_form_scout as scout  # noqa: E402


def record_fraction(record: dict[str, str]) -> Fraction:
    return Fraction(int(record["numerator"]), int(record["denominator"]))


class P2DNormalFormScoutTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.certificate, cls.digest = scout.load_frame_certificate()

    def test_archived_frame_identity_and_pass_are_required(self) -> None:
        raw = scout.authenticate_frame_certificate(
            self.certificate, self.digest)
        self.assertEqual(raw["status"], "PASS")

        changed_id = copy.deepcopy(self.certificate)
        changed_id["certificate_id"] = "vdp-p2d-frame-changed"
        with self.assertRaisesRegex(scout.ScoutInputError, "certificate id"):
            scout.authenticate_frame_certificate(
                changed_id, scout.FRAME_SHA256)

        changed_atom = copy.deepcopy(self.certificate)
        changed_atom["chart_status"][
            "V2.CHART.SYMPLECTIC_FRAME"] = "OPEN"
        with self.assertRaisesRegex(scout.ScoutInputError, "prerequisite"):
            scout.authenticate_frame_certificate(
                changed_atom, scout.FRAME_SHA256)

        changed_payload = copy.deepcopy(self.certificate)
        changed_payload["raw_probe"]["L_jets"]["entries"][0][0][
            "normalized"
        ]["value"]["lower_hex"] = "0x0.0p+0"
        with tempfile.TemporaryDirectory() as directory:
            changed_path = Path(directory) / "changed-frame.json"
            changed_path.write_text(
                json.dumps(changed_payload), encoding="utf-8"
            )
            with self.assertRaisesRegex(
                scout.ScoutInputError, "SHA-256 changed"
            ):
                scout.build_report(changed_path)

    def test_component_endpoints_feed_theory_majorants(self) -> None:
        raw = self.certificate["raw_probe"]
        scalars = raw["scalar_jets"]
        alpha = scout.normalized_jet_components(
            scalars["alpha"], "alpha")
        beta = scout.normalized_jet_components(
            scalars["beta"], "beta")
        U = scout.complex_u_coefficient_jet(raw["L_jets"])
        coefficients = scout.model_coefficient_jets()
        divisor = scout.divisor_jet_majorant(alpha, beta)

        E = coefficients["gamma"]["J2"] * U["J2"]**3 / 3
        h_in = coefficients["D"]["J2"] * U["J2"]**4 / E

        # The value must dominate the 8/3 nonlinear core instead of the
        # underbound obtained by treating a real L row as a complex norm.
        self.assertGreater(E, Fraction(8, 3))
        self.assertLessEqual(E, Fraction(4))
        self.assertLessEqual(h_in, Fraction(1, 64))
        self.assertLessEqual(divisor["kappa_J"], Fraction(5, 3))

        sqrt_two = scout.rational_sqrt_upper(Fraction(2))
        self.assertGreaterEqual(sqrt_two * sqrt_two, Fraction(2))

    def test_report_is_explicitly_design_only_and_closes_nothing(self) -> None:
        report = scout.build_report()
        self.assertEqual(report["status"], "DESIGN_CANDIDATE_ONLY")
        self.assertEqual(report["mathematical_status"], "INCONCLUSIVE")
        self.assertEqual(
            report["coordinate_convention"]["complex_roles"],
            "z_from_x__w_from_y",
        )
        self.assertEqual(
            report["coordinate_convention"]["poisson_coordinate_bracket"],
            "{z_j,w_k}=-delta_jk",
        )
        self.assertTrue(report["candidate_gates"]["all_input_gates_pass"])
        self.assertTrue(all(
            report["candidate_gates"]["input"].values()))
        schedule = report["fixed_theory_schedule"]
        self.assertEqual(schedule["Bbar"]["numerator"], str(2**20))
        self.assertEqual(schedule["epsilon_nf"]["denominator"], str(2**22))
        self.assertEqual(schedule["theta"]["numerator"], "1")
        self.assertEqual(schedule["theta"]["denominator"], "4")
        self.assertTrue(schedule["all_domain_gates_pass"])
        self.assertTrue(all(schedule["domain_gates"].values()))
        lipschitz = schedule["equations_39a_to_39c"]
        B_z = record_fraction(lipschitz["B_z"])
        A_z = record_fraction(lipschitz["A_z"])
        self.assertEqual(B_z, Fraction(37, 691200))
        self.assertLess(B_z, Fraction(1, 16384))
        self.assertEqual(A_z, 1 / (1 - B_z))
        self.assertLess(A_z, Fraction(16384, 16383))
        forward_displacement = record_fraction(
            schedule["equation_40b"][
                "forward_displacement_A_z_times_S0"])
        epsilon_over_8 = record_fraction(
            schedule["equation_40b"]["epsilon_over_8"])
        self.assertLess(forward_displacement, epsilon_over_8)
        physical_preimage = record_fraction(
            schedule["equation_44a"][
                "physical_preimage_radius_2epsilon_over_7_plus_S0"
            ]
        )
        source_radius = record_fraction(
            schedule["equation_44a"]["source_radius_3epsilon_over_8"]
        )
        self.assertLess(physical_preimage, source_radius)
        tails = schedule["coordinate_tails_q2"]
        inverse_tail = record_fraction(tails["inverse_raw_equation_47"])
        forward_tail = record_fraction(tails["forward_equation_47a"])
        self.assertEqual(tails["prefix_order"], 2)
        self.assertEqual(forward_tail, A_z * inverse_tail)
        self.assertGreater(forward_tail, inverse_tail)
        boundary = report["claim_boundary"]
        self.assertFalse(boundary["claim_bearing"])
        self.assertFalse(boundary["design_output_is_certificate_evidence"])
        self.assertEqual(boundary["closed_obligations"], [])
        self.assertEqual(
            boundary["V2_CHART_ANALYTIC_NORMAL_FORM"], "OPEN")
        self.assertEqual(boundary["V2_EXACT_CHART"], "OPEN")


if __name__ == "__main__":
    unittest.main()
