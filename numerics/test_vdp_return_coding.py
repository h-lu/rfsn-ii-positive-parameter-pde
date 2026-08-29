from __future__ import annotations

import unittest
from pathlib import Path

import numpy as np

from numerics.rfsn_numerics import (
    REVERSER,
    continue_homoclinics,
    origin_matrix,
    vdp_hamiltonian,
)
from numerics.vdp_return_coding import (
    extract_numerical_section_itinerary,
    homoclinic_source_anchor,
    integrate_first_event,
    numerical_source_coordinates,
    reversible_saddle_frame,
    solve_symmetric_multipulse,
    zero_energy_source_state,
)


R = 0.08
A2 = 0.0
EPSILON = 1.0
SOURCE_RADIUS = 0.01


class NumericalSectionItineraryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        archive = (
            Path(__file__).resolve().parent
            / "results/vdp_v1_v7/v7_periodic.npz"
        )
        cls.periodic = np.load(archive)

    def extract(self, label: str) -> dict[str, object]:
        return extract_numerical_section_itinerary(
            self.periodic[f"{label}_xi"],
            self.periodic[f"{label}_state"],
            r=R,
            a2=A2,
            epsilon=EPSILON,
            source_radius=SOURCE_RADIUS,
            stable_width=SOURCE_RADIUS,
            cyclic=True,
        )

    def test_a0_and_b0_do_not_reach_the_numerical_source_face(self) -> None:
        for label in ("A0", "B0"):
            with self.subTest(label=label):
                itinerary = self.extract(label)
                self.assertEqual(itinerary["status"], "NOT_NUMERICALLY_RESOLVED")
                self.assertEqual(itinerary["reason"], "NO_OUTGOING_CROSSING")
                self.assertEqual(itinerary["outgoing_crossing_count"], 0)
                self.assertEqual(itinerary["edges"], [])
                self.assertFalse(itinerary["exact_v6_word_binding"])
                self.assertIsNone(itinerary["absolute_winding_n"])
                self.assertFalse(itinerary["claim_bearing"])

    def test_a1_crossings_are_rejected_by_the_stable_width(self) -> None:
        itinerary = self.extract("A1")

        self.assertEqual(itinerary["status"], "NOT_NUMERICALLY_RESOLVED")
        self.assertEqual(itinerary["reason"], "STABLE_WIDTH_EXCEEDED")
        self.assertEqual(itinerary["outgoing_crossing_count"], 1)
        self.assertEqual(itinerary["incoming_crossing_count"], 1)
        self.assertEqual(itinerary["edges"], [])
        self.assertEqual(
            itinerary["rejections"][0]["reason"], "STABLE_WIDTH_EXCEEDED"
        )
        self.assertGreater(
            itinerary["rejections"][0]["maximum_complementary_radius"],
            SOURCE_RADIUS,
        )

    def test_b1_and_a2_each_give_one_signed_numerical_edge(self) -> None:
        expected = {
            "B1": ("negative", (0.24, 0.27)),
            "A2": ("positive", (0.74, 0.77)),
        }
        for label, (sign, turns) in expected.items():
            with self.subTest(label=label):
                itinerary = self.extract(label)
                self.assertEqual(
                    itinerary["coordinate_status"],
                    "numerical_linear_reversible_eigenframe_not_exact_V2_chart",
                )
                self.assertEqual(
                    itinerary["status"],
                    "COMPUTED/E1_NUMERICAL_SECTION_ITINERARY",
                )
                self.assertEqual(itinerary["reason"], "WORD_UNRESOLVED")
                self.assertFalse(itinerary["exact_v6_word_binding"])
                self.assertIsNone(itinerary["absolute_winding_n"])
                self.assertFalse(itinerary["claim_bearing"])
                self.assertEqual(len(itinerary["edges"]), 1)

                edge = itinerary["edges"][0]
                self.assertEqual(edge["source"]["transverse_sign_proxy"], sign)
                self.assertEqual(edge["target"]["transverse_sign_proxy"], sign)
                self.assertLess(edge["source_rho_u_face_residual"], 1.0e-10)
                self.assertLess(edge["incoming_rho_s_face_residual"], 1.0e-10)
                self.assertLess(edge["target_rho_u_face_residual"], 1.0e-10)
                self.assertLess(edge["incoming_event_speed"], -1.0e-4)
                self.assertGreater(edge["target_event_speed"], 1.0e-4)
                self.assertGreater(edge["local_residence_turns_proxy"], turns[0])
                self.assertLess(edge["local_residence_turns_proxy"], turns[1])
                self.assertLess(edge["energy_drift"], 1.0e-10)
                self.assertFalse(edge["exact_v6_word_binding"])
                self.assertIsNone(edge["absolute_winding_n"])


class VdpReturnCodingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        # One accurately continued positive-parameter homoclinic is shared by
        # the anchor, stable-cut, and two-pulse tests.  These are E1 floating-
        # point checks; they are not interval validation of V2 or V6.
        cls.homoclinic = continue_homoclinics(
            "vdp",
            [R],
            a2=A2,
            epsilon=EPSILON,
            domain=25.0,
            tolerance=2.0e-9,
        )[0]

    def test_reversible_saddle_frame_resolves_both_invariant_planes(self) -> None:
        frame = reversible_saddle_frame(R, A2, EPSILON)
        matrix = origin_matrix("vdp", R, A2, EPSILON)
        basis = np.column_stack((frame.unstable, frame.stable))

        self.assertAlmostEqual(frame.alpha, 1.0 / np.sqrt(2.0), places=13)
        self.assertAlmostEqual(frame.beta, 1.0 / np.sqrt(2.0), places=13)
        np.testing.assert_allclose(frame.inverse @ basis, np.eye(4), atol=2.0e-14)
        np.testing.assert_allclose(
            frame.stable,
            REVERSER[:, None] * frame.unstable,
            atol=2.0e-14,
        )

        unstable_reduced = frame.inverse[:2] @ matrix @ frame.unstable
        stable_reduced = frame.inverse[2:] @ matrix @ frame.stable
        self.assertLess(
            np.linalg.norm(matrix @ frame.unstable - frame.unstable @ unstable_reduced),
            2.0e-13,
        )
        self.assertLess(
            np.linalg.norm(matrix @ frame.stable - frame.stable @ stable_reduced),
            2.0e-13,
        )

    def test_numerical_source_section_is_on_zero_energy(self) -> None:
        frame = reversible_saddle_frame(R, A2, EPSILON)
        phase = 0.37
        transverse_coordinate = 2.0e-5
        state, diagnostics = zero_energy_source_state(
            frame=frame,
            phase=phase,
            transverse_coordinate=transverse_coordinate,
            radius=SOURCE_RADIUS,
            r=R,
            a2=A2,
            epsilon=EPSILON,
        )
        coordinates = frame.coordinates(state)
        recovered = numerical_source_coordinates(
            state,
            frame=frame,
            r=R,
            a2=A2,
            epsilon=EPSILON,
        )

        self.assertAlmostEqual(np.linalg.norm(coordinates[:2]), SOURCE_RADIUS, places=14)
        self.assertLess(
            abs(vdp_hamiltonian(state.reshape(4, 1), R, A2, EPSILON)[0]),
            2.0e-17,
        )
        self.assertLess(float(diagnostics["energy_residual"]), 2.0e-17)
        self.assertAlmostEqual(float(recovered["phase"]), phase, places=13)
        self.assertAlmostEqual(
            float(recovered["transverse_coordinate"]),
            transverse_coordinate,
            places=13,
        )
        self.assertLess(float(recovered["reconstruction_defect"]), 2.0e-13)
        self.assertIn("not_exact_action", str(diagnostics["transverse_name"]))

    def test_phase_zero_hits_the_positive_pole_gate_proxy(self) -> None:
        sample = integrate_first_event(
            phase=0.0,
            transverse_coordinate=0.0,
            r=R,
            a2=A2,
            epsilon=EPSILON,
            source_radius=SOURCE_RADIUS,
            maximum_time=20.0,
            terminal_u=-10.0,
            rtol=2.0e-10,
            atol=2.0e-12,
            max_step=0.04,
        )

        self.assertEqual(sample.event, "pole_gate_proxy")
        self.assertTrue(sample.diagnostics["solver_success"])
        self.assertAlmostEqual(sample.event_state[0], -10.0, places=10)
        self.assertLess(sample.event_speed, -13.0)
        # These strict inequalities are the numerical x=10 cone-entry checks;
        # they do not identify the paper's entire open pole source window.
        self.assertGreater(float(sample.diagnostics["pole_y"]), 13.0)
        self.assertGreater(float(sample.diagnostics["pole_D"]), 26.0)
        self.assertGreater(float(sample.diagnostics["pole_H"]), 131.0)
        self.assertLess(float(sample.diagnostics["energy_abs_max"]), 5.0e-9)
        self.assertIn("not the exhaustive V6", str(sample.diagnostics["event_semantics"]))

    def test_homoclinic_anchor_reconstructs_and_reaches_actual_stable_cut(self) -> None:
        anchor = homoclinic_source_anchor(
            self.homoclinic,
            source_radius=SOURCE_RADIUS,
        )
        frame = reversible_saddle_frame(R, A2, EPSILON)
        anchor_coordinates = frame.coordinates(np.asarray(anchor["state"], dtype=float))

        self.assertLess(float(anchor["reconstruction_defect"]), 2.0e-12)
        self.assertLess(float(anchor["energy_residual"]), 2.0e-9)
        self.assertAlmostEqual(
            np.linalg.norm(anchor_coordinates[:2]),
            SOURCE_RADIUS,
            places=11,
        )

        sample = integrate_first_event(
            phase=float(anchor["phase"]),
            transverse_coordinate=float(anchor["transverse_coordinate"]),
            r=R,
            a2=A2,
            epsilon=EPSILON,
            source_radius=SOURCE_RADIUS,
            maximum_time=35.0,
            terminal_u=-10.0,
            rtol=1.0e-10,
            atol=1.0e-12,
            max_step=0.03,
        )
        terminal_coordinates = frame.coordinates(sample.event_state)

        self.assertEqual(sample.event, "stable_cut_proxy")
        self.assertTrue(sample.diagnostics["solver_success"])
        # Checking the cut equation distinguishes a genuine event hit from a
        # mere time-limit fallback carrying the same current string label.
        self.assertAlmostEqual(
            np.linalg.norm(terminal_coordinates),
            SOURCE_RADIUS * 5.0e-2,
            delta=2.0e-10,
        )
        self.assertLess(sample.event_time_xi, 34.0)
        self.assertGreater(
            float(sample.diagnostics["terminal_stable_radius"]),
            10.0 * float(sample.diagnostics["terminal_unstable_radius"]),
        )
        self.assertLess(float(sample.diagnostics["energy_abs_max"]), 2.0e-9)

    def test_two_pulse_is_an_actual_full_ode_collocation_solution(self) -> None:
        orbit = solve_symmetric_multipulse(
            self.homoclinic,
            2,
            separation=18.0,
            padding=28.0,
            tolerance=1.5e-6,
            max_nodes=60_000,
        )

        self.assertTrue(orbit.diagnostics["solver_success"])
        self.assertEqual(orbit.pulse_count_requested, 2)
        self.assertEqual(orbit.pulse_count_observed, 2)
        self.assertEqual(
            orbit.diagnostics["evidence_status"],
            "COMPUTED/E1 actual full-ODE multipulse",
        )
        self.assertLess(float(orbit.diagnostics["normalized_ode_residual_inf"]), 3.0e-6)
        self.assertLess(float(orbit.diagnostics["boundary_residual_inf"]), 1.0e-10)
        self.assertLess(float(orbit.diagnostics["tail_norm"]), 2.0e-6)
        self.assertLess(float(orbit.diagnostics["hamiltonian_drift"]), 2.0e-6)
        self.assertLess(
            float(orbit.diagnostics["physical_stationary_u_residual_inf"]),
            3.0e-6,
        )
        self.assertLess(
            float(orbit.diagnostics["physical_stationary_v_residual_inf"]),
            3.0e-6,
        )
        np.testing.assert_allclose(
            orbit.state,
            REVERSER[:, None] * orbit.state[:, ::-1],
            atol=2.0e-12,
        )
        self.assertTrue(np.all(np.diff(orbit.physical_x) > 0.0))


if __name__ == "__main__":
    unittest.main()
