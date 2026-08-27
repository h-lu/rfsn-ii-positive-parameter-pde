"""Regression tests for the floating P2c direct-source branch scout."""

from __future__ import annotations

import json
from pathlib import Path
import unittest

import numpy as np

from numerics.rfsn_numerics import CORE_SOURCE_STATE
from numerics.vdp_p2c_branch_scout import (
    CORE_SEED,
    DEFAULT_OUTPUT,
    P2CParameters,
    P2CScoutConfiguration,
    PRIMARY_PARAMETERS,
    SCHEMA_VERSION,
    solve_direct_source_branch,
)


# Immutable flagship certificate intervals, copied here as regression anchors.
CORE_PHASE_INTERVAL = (5.8615055856447817, 5.8615055856450482)
CORE_TIME_INTERVAL = (9.6374420678958099, 9.6374420678971511)
CORE_ENDPOINT_U_INTERVAL = (4.8785234574459304, 4.8785234988116768)
CORE_ENDPOINT_V_INTERVAL = (-7.9333304994224827, -7.933330385013492)
CORE_DETERMINANT_INTERVAL = (149.56393055300413, 149.56404227745782)
CORE_PHASE_U_INTERVAL = (-10.889708535478462, -10.8897049543477)
CORE_PHASE_V_INTERVAL = (35.417125972639965, 35.417127394127888)


class DirectSourceP2CBranchScoutTests(unittest.TestCase):
    """The scout must retain the P2bK source normalization and core anchor."""

    @classmethod
    def setUpClass(cls) -> None:
        cls.configuration = P2CScoutConfiguration()
        cls.core = solve_direct_source_branch(
            P2CParameters(r=0.0, a2=0.0, epsilon=1.0),
            CORE_SEED,
            configuration=cls.configuration,
        )
        cls.primary = solve_direct_source_branch(
            P2CParameters(*PRIMARY_PARAMETERS),
            (cls.core.phase, cls.core.half_time),
            configuration=cls.configuration,
        )

    def test_core_reproduces_flagship_interval_anchor(self) -> None:
        core = self.core
        self.assertTrue(CORE_PHASE_INTERVAL[0] <= core.phase <= CORE_PHASE_INTERVAL[1])
        self.assertTrue(
            CORE_TIME_INTERVAL[0] <= core.half_time <= CORE_TIME_INTERVAL[1]
        )
        self.assertTrue(
            CORE_ENDPOINT_U_INTERVAL[0]
            <= core.endpoint_state[0]
            <= CORE_ENDPOINT_U_INTERVAL[1]
        )
        self.assertTrue(
            CORE_ENDPOINT_V_INTERVAL[0]
            <= core.endpoint_state[2]
            <= CORE_ENDPOINT_V_INTERVAL[1]
        )
        self.assertTrue(
            CORE_DETERMINANT_INTERVAL[0]
            <= core.shooting_determinant
            <= CORE_DETERMINANT_INTERVAL[1]
        )
        self.assertTrue(
            CORE_PHASE_U_INTERVAL[0]
            <= core.endpoint_phase_column[0]
            <= CORE_PHASE_U_INTERVAL[1]
        )
        self.assertTrue(
            CORE_PHASE_V_INTERVAL[0]
            <= core.endpoint_phase_column[2]
            <= CORE_PHASE_V_INTERVAL[1]
        )
        np.testing.assert_allclose(
            np.asarray(core.source_state), CORE_SOURCE_STATE, rtol=0.0, atol=2.0e-15
        )
        self.assertLess(core.shooting_residual_inf, 1.0e-11)
        self.assertTrue(core.first_hit_common_segments_passed)

    def test_primary_direct_source_regression(self) -> None:
        primary = self.primary
        self.assertAlmostEqual(primary.phase, 5.860149488413829, delta=5.0e-10)
        self.assertAlmostEqual(
            primary.half_time, 9.65263970139728, delta=5.0e-10
        )
        self.assertAlmostEqual(
            primary.shooting_determinant, 154.4688491467, delta=5.0e-5
        )
        self.assertAlmostEqual(
            primary.endpoint_state[0], 4.92556668567844, delta=2.0e-9
        )
        self.assertAlmostEqual(
            primary.endpoint_state[2], -8.02333562165332, delta=2.0e-9
        )
        self.assertLess(primary.shooting_residual_inf, 1.0e-9)
        self.assertLess(primary.source_radius_error, 1.0e-14)
        self.assertAlmostEqual(
            primary.source_algebraic_unstable_radius,
            self.configuration.source_radius,
            delta=1.0e-14,
        )
        self.assertTrue(primary.first_hit_common_segments_passed)

        # Padded candidate gates from the shared common time partition.
        gates = (1.0 / 2500.0, 1.0 / 50.0, 1.0 / 500.0, 1.0 / 4.0, 4.0)
        self.assertEqual(len(primary.first_hit_segments), len(gates))
        for segment, gate in zip(primary.first_hit_segments, gates, strict=True):
            self.assertGreater(segment.sampled_signed_margin, gate)

    def test_saved_scout_matches_current_regression(self) -> None:
        path = Path(DEFAULT_OUTPUT)
        self.assertTrue(path.is_file())
        saved = json.loads(path.read_text(encoding="utf-8"))
        self.assertEqual(saved["schema_version"], SCHEMA_VERSION)
        self.assertFalse(
            saved["source_contract"][
                "historical_normalized_eigenframe_anchor_reused"
            ]
        )
        samples = saved["samples"]
        saved_core = samples["core"]
        saved_primary = samples["primary_r_0p08_a2_0_epsilon_1"]
        self.assertAlmostEqual(saved_core["phase"], self.core.phase, delta=1.0e-13)
        self.assertAlmostEqual(
            saved_core["shooting_determinant"],
            self.core.shooting_determinant,
            delta=1.0e-9,
        )
        self.assertAlmostEqual(
            saved_primary["phase"], self.primary.phase, delta=1.0e-13
        )
        self.assertAlmostEqual(
            saved_primary["shooting_determinant"],
            self.primary.shooting_determinant,
            delta=1.0e-9,
        )


if __name__ == "__main__":
    unittest.main()
