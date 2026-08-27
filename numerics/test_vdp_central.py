from __future__ import annotations

import json
import unittest

import numpy as np

from numerics.vdp_central import (
    AffineEventProxy,
    compute_homoclinic_continuation,
    local_passage_log_law,
    saddle_focus_spectrum,
    symbolic_hamiltonian_checks,
    trace_affine_event_proxies,
)


class VdpCentralFastTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # This deliberately small exploratory slice keeps the test fast.  It is
        # floating-point regression data, not an explicit V2 theorem wedge.
        cls.continuation = compute_homoclinic_continuation(
            [0.04],
            domain=12.0,
            tolerance=1.0e-6,
            transversality_rtol=1.0e-9,
            transversality_atol=1.0e-11,
            transversality_max_step=0.05,
        )

    def test_symbolic_hamiltonian_reverser_and_primitive_checks(self) -> None:
        report = symbolic_hamiltonian_checks()
        self.assertTrue(report.passed)
        self.assertGreaterEqual(len(report.residuals), 9)
        self.assertTrue(all(value == "0" for value in report.residuals.values()))
        json.dumps(report.as_json_dict())

    def test_saddle_focus_spectrum_matches_closed_formula(self) -> None:
        report = saddle_focus_spectrum(0.08, 0.0, 1.0)
        expected = 1.0 / np.sqrt(2.0)
        self.assertTrue(report.is_saddle_focus)
        self.assertAlmostEqual(report.alpha, expected, places=14)
        self.assertAlmostEqual(report.beta, expected, places=14)
        self.assertLess(report.characteristic_residual_inf, 1.0e-12)
        self.assertLess(report.quartet_match_error, 1.0e-12)
        json.dumps(report.as_json_dict())

    def test_positive_homoclinic_slice_and_transversality_proxy(self) -> None:
        continuation = self.continuation
        self.assertEqual(len(continuation.results), 1)
        sample = continuation.report.samples[0]
        self.assertGreater(sample.r, 0.0)
        self.assertTrue(sample.diagnostics["solver_success"])
        self.assertTrue(sample.diagnostics["nontrivial_branch"])
        self.assertGreater(sample.transversality.quotient_sine, 0.2)
        self.assertGreater(
            sample.transversality.rank_three_singular_value, 0.1
        )
        self.assertLess(sample.transversality.rank_defect_singular_value, 1.0e-5)
        self.assertLess(sample.transversality.flow_to_stable_distance, 1.0e-4)
        self.assertIn("not an interval lower bound", sample.transversality.scope_note)

        payload = continuation.as_npz_payload(points=101)
        self.assertEqual(payload["state_half"].shape, (1, 4, 101))
        self.assertEqual(payload["quotient_sine_proxy"].shape, (1,))
        json.dumps(continuation.as_json_dict())

    def test_local_passage_time_and_phase_log_law_proxy(self) -> None:
        report = local_passage_log_law(
            self.continuation.results[0],
            [3.0e-4, 1.0e-4, 3.0e-5, 1.0e-5],
            incoming_stable_radius=0.06,
            outgoing_difference_radius=0.015,
            rtol=1.0e-9,
            atol=1.0e-11,
            max_step=0.05,
        )
        self.assertEqual(len(report.samples), 8)
        for sign in ("-1", "1"):
            self.assertLess(
                abs(report.fitted_time_slopes[sign] - report.expected_time_slope),
                0.02,
            )
            self.assertLess(
                abs(
                    report.fitted_phase_slopes[sign]
                    - report.expected_phase_slope
                ),
                0.02,
            )
        self.assertLess(max(sample.event_residual for sample in report.samples), 1.0e-12)
        self.assertLess(
            max(sample.energy_difference_drift for sample in report.samples),
            1.0e-12,
        )
        self.assertIn("not the exact V2 action coordinate", report.scope_note)
        payload = report.as_npz_payload()
        self.assertEqual(payload["nu_proxy"].shape, (8,))
        json.dumps(report.as_json_dict())

    def test_affine_finite_events_are_explicitly_proxy_only(self) -> None:
        report = trace_affine_event_proxies(
            [0.0, 0.2, 0.0, 0.0],
            [
                AffineEventProxy("u=.01 proxy", (1.0, 0.0, 0.0, 0.0), 0.01, 1),
                AffineEventProxy("u=.02 proxy", (1.0, 0.0, 0.0, 0.0), 0.02, 1),
            ],
            r=0.04,
            maximum_time=1.0,
        )
        self.assertEqual(report.selected_label, "u=.01 proxy")
        self.assertIsNotNone(report.hit_speed)
        self.assertGreater(float(report.hit_speed), 0.1)
        self.assertIsNotNone(report.competing_time_gap)
        self.assertGreater(float(report.competing_time_gap), 0.0)
        self.assertIn("not the V2 clean event faces", report.scope_note)
        self.assertEqual(report.as_npz_payload()["hit_state"].shape, (4,))
        json.dumps(report.as_json_dict())


if __name__ == "__main__":
    unittest.main()
