from __future__ import annotations

import unittest

import numpy as np

from numerics.rfsn_numerics import vdp_field
from numerics.vdp_bridge import (
    BridgeParameters,
    bridge_diagnostics,
    central_to_physical,
    physical_to_central,
)


class VanDerPolBridgeTests(unittest.TestCase):
    def test_state_roundtrip_for_nonzero_a2(self) -> None:
        parameters = BridgeParameters(r=0.08, a2=0.2, epsilon=1.1)
        state = np.array(
            [[0.2, -0.4], [0.1, 0.3], [-0.5, 0.25], [0.7, -0.2]]
        )
        reconstructed = physical_to_central(
            central_to_physical(state, parameters), parameters
        )
        self.assertLess(float(np.max(np.abs(reconstructed - state))), 2.0e-12)

    def test_field_energy_clock_and_action_scaling(self) -> None:
        parameters = BridgeParameters(r=0.08, a2=0.0, epsilon=1.0)
        xi = np.linspace(-0.8, 0.8, 801)
        initial = np.array([0.1, 0.03, -0.02, 0.04])
        # A short RK-quality sample is enough: bridge_diagnostics compares the
        # exact vector fields pointwise and the same discrete action rule in
        # both coordinates.
        from scipy.integrate import solve_ivp

        integration = solve_ivp(
            lambda time, state: vdp_field(
                parameters.r, parameters.a2, parameters.epsilon
            )(np.array([time]), state[:, None])[:, 0],
            (float(xi[0]), float(xi[-1])),
            initial,
            t_eval=xi,
            method="DOP853",
            rtol=2.0e-12,
            atol=2.0e-14,
        )
        report = bridge_diagnostics(xi, integration.y, parameters)
        self.assertLess(report["roundtrip_state_defect_inf"], 2.0e-12)
        self.assertLess(report["physical_pushforward_defect_inf"], 2.0e-14)
        self.assertLess(report["fast_clock_pushforward_defect_inf"], 2.0e-14)
        self.assertLess(report["energy_scaling_defect_inf"], 2.0e-15)
        self.assertLess(report["action_scaling_endpoint_defect"], 2.0e-18)


if __name__ == "__main__":
    unittest.main()
