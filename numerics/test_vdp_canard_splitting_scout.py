from __future__ import annotations

import unittest

import numpy as np

from numerics.vdp_canard_splitting_scout import (
    BRANCH_STATUS,
    C4_STATUS,
    CANARD_STATUS,
    ScoutConfiguration,
    build_report,
    central_field,
    central_hamiltonian,
    evaluate_splitting,
    zero_energy_projected_entry,
)


class CanardSplittingScoutTests(unittest.TestCase):
    def test_zero_energy_projection_and_hamiltonian_identity(self) -> None:
        configuration = ScoutConfiguration()
        state = zero_energy_projected_entry(
            -2.0,
            r=configuration.r,
            a2=configuration.leading_a2,
            order=3,
        )
        self.assertLess(
            abs(
                central_hamiltonian(
                    state, r=configuration.r, a2=configuration.leading_a2
                )
            ),
            2.0e-16,
        )
        step = 1.0e-7
        gradient = np.asarray(
            [
                (
                    central_hamiltonian(
                        state + step * np.eye(4)[index],
                        r=configuration.r,
                        a2=configuration.leading_a2,
                    )
                    - central_hamiltonian(
                        state - step * np.eye(4)[index],
                        r=configuration.r,
                        a2=configuration.leading_a2,
                    )
                )
                / (2.0 * step)
                for index in range(4)
            ]
        )
        self.assertLess(
            abs(
                float(
                    gradient
                    @ central_field(
                        state,
                        r=configuration.r,
                        a2=configuration.leading_a2,
                    )
                )
            ),
            2.0e-9,
        )

    def test_local_surrogate_root_is_numerically_well_posed(self) -> None:
        configuration = ScoutConfiguration()
        left = evaluate_splitting(
            -0.00835,
            comparison_time=1.0,
            order=3,
            configuration=configuration,
        )
        right = evaluate_splitting(
            -0.00832,
            comparison_time=1.0,
            order=3,
            configuration=configuration,
        )
        self.assertLess(left.splitting * right.splitting, 0.0)
        self.assertGreater(left.event_p_derivative, 0.1)
        self.assertGreater(right.event_p_derivative, 0.1)
        self.assertAlmostEqual(left.event_time, 1.0, places=4)
        self.assertAlmostEqual(right.event_time, 1.0, places=4)

    def test_report_preserves_the_no_go_boundary(self) -> None:
        report = build_report()
        self.assertFalse(report["claim_bearing"])
        decision = report["decision"]
        self.assertEqual(decision["branch_construction_status"], BRANCH_STATUS)
        self.assertEqual(
            decision["finite_parameter_maximal_canard_status"], CANARD_STATUS
        )
        self.assertEqual(decision["high_winding_connection_status"], C4_STATUS)
        self.assertEqual(
            decision["current_sample_a2_zero_classification"], "INCONCLUSIVE"
        )
        rows = report["rows"]
        self.assertTrue(all(row["root"] is not None for row in rows))
        cluster = report["descriptive_order_3_core_cluster"]
        self.assertLess(cluster["width"], 5.0e-5)
        self.assertLess(cluster["minimum"], configuration_leading := -1.0 / 120.0)
        self.assertLess(configuration_leading, cluster["maximum"] + 2.0e-6)
        stress = next(
            row
            for row in rows
            if row["formal_truncation_order"] == 3
            and row["comparison_time_Y"] == 4.0
        )
        self.assertGreater(
            abs(
                float(stress["root"]["a2"])
                - float(cluster["midpoint"])
            ),
            1.0e-3,
        )


if __name__ == "__main__":
    unittest.main()
