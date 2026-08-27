"""Analytic/numeric cross-checks for the temporal van der Pol prescreen."""

from __future__ import annotations

import io
import json
import tempfile
import unittest
from contextlib import redirect_stdout
from pathlib import Path

import numpy as np

from numerics.vdp_turing import (
    HOPF_BOUNDARY_K0,
    LONG_WAVE_OSCILLATORY,
    SCHEMA_VERSION,
    STABLE_ALL_K,
    TemporalParameters,
    build_prescreen_report,
    dispersion_curve,
    dispersion_eigenvalues,
    fourier_symbol,
    homogeneous_equilibrium,
    homogeneous_status,
    main,
    parameter_diagnostics,
    reaction_residual,
    scan_parameter_grid,
    spectral_abscissa,
    stationary_band_a2_interval,
    stationary_turing_diagnostics,
    symbol_trace_determinant,
    threshold_curve,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "numerics" / "config" / "vdp_dynamics_screening.json"


class FormulaCrossChecks(unittest.TestCase):
    def test_homogeneous_equilibrium_annuls_reaction(self) -> None:
        for parameters in (
            TemporalParameters(0.08, 0.0, 1.0),
            TemporalParameters(0.12, -2.0, 0.7),
            TemporalParameters(0.04, 0.25, 1.2),
        ):
            equilibrium = homogeneous_equilibrium(parameters)
            np.testing.assert_allclose(
                reaction_residual(equilibrium, parameters), 0.0, atol=2.0e-16
            )

    def test_analytic_dispersion_matches_direct_eigensolver(self) -> None:
        parameters = TemporalParameters(0.13, -3.2, 0.73)
        for k in (0.0, 0.03, 0.7, 4.0, 17.0):
            analytic = np.sort_complex(dispersion_eigenvalues(parameters, k))
            direct = np.sort_complex(np.linalg.eigvals(fourier_symbol(parameters, k)))
            np.testing.assert_allclose(analytic, direct, rtol=2.0e-14, atol=2.0e-14)

    def test_trace_determinant_are_characteristic_invariants(self) -> None:
        parameters = TemporalParameters(0.07, 0.2, 1.3)
        wavenumbers = np.array([-3.0, 0.0, 0.5, 11.0])
        symbols = fourier_symbol(parameters, wavenumbers)
        trace, determinant = symbol_trace_determinant(parameters, wavenumbers)
        np.testing.assert_allclose(trace, np.trace(symbols, axis1=-2, axis2=-1))
        np.testing.assert_allclose(determinant, np.linalg.det(symbols), rtol=2e-14)
        np.testing.assert_allclose(
            dispersion_eigenvalues(parameters, -wavenumbers),
            dispersion_eigenvalues(parameters, wavenumbers),
        )


class BoundaryAndRegimeTests(unittest.TestCase):
    def test_current_point_is_k0_hopf_boundary_with_no_turing_band(self) -> None:
        parameters = TemporalParameters(0.08, 0.0, 1.0)
        diagnosis = parameter_diagnostics(parameters)
        self.assertEqual(homogeneous_status(parameters), HOPF_BOUNDARY_K0)
        self.assertEqual(diagnosis["temporal_regime"], HOPF_BOUNDARY_K0)
        self.assertAlmostEqual(diagnosis["zero_mode_spectral_abscissa"], 0.0)
        self.assertFalse(
            diagnosis["stationary"]["has_stationary_real_unstable_band"]
        )
        self.assertFalse(
            diagnosis["stationary"][
                "classical_stationary_turing_from_stable_homogeneous_state"
            ]
        )
        self.assertLess(float(spectral_abscissa(parameters, 0.1)), 0.0)

    def test_positive_a2_is_stable_for_every_fourier_mode(self) -> None:
        parameters = TemporalParameters(0.08, 0.25, 1.0)
        self.assertEqual(homogeneous_status(parameters), STABLE_ALL_K)
        k = np.linspace(0.0, 80.0, 2001)
        self.assertLess(float(np.max(spectral_abscissa(parameters, k))), 0.0)
        stationary = stationary_turing_diagnostics(parameters)
        self.assertGreater(stationary["minimum_determinant"], 0.0)
        self.assertFalse(stationary["has_stationary_real_unstable_band"])

    def test_small_negative_a2_is_long_wave_not_stationary_turing(self) -> None:
        parameters = TemporalParameters(0.08, -0.25, 1.0)
        self.assertEqual(homogeneous_status(parameters), LONG_WAVE_OSCILLATORY)
        stationary = stationary_turing_diagnostics(parameters)
        self.assertFalse(stationary["has_stationary_real_unstable_band"])
        self.assertGreater(float(spectral_abscissa(parameters, 0.0)), 0.0)

    def test_exact_stationary_threshold_has_double_positive_zero(self) -> None:
        r = 0.08
        epsilon = 1.0
        interval = stationary_band_a2_interval(r, epsilon)
        self.assertIsNotNone(interval)
        assert interval is not None
        near_plus_threshold = interval[1]
        parameters = TemporalParameters(r, near_plus_threshold, epsilon)
        stationary = stationary_turing_diagnostics(
            parameters, absolute_tolerance=2.0e-12
        )
        self.assertEqual(stationary["stationary_zero_status"], "DOUBLE_POSITIVE_ZERO")
        self.assertEqual(len(stationary["q_roots"]), 1)
        q_critical = stationary["onset_q_critical"]
        k_critical = stationary["onset_k_critical"]
        self.assertAlmostEqual(q_critical, np.sqrt(epsilon / r**4), places=12)
        self.assertAlmostEqual(k_critical, epsilon**0.25 / r, places=12)
        _, determinant = symbol_trace_determinant(parameters, k_critical)
        # Reconstructing ``a`` through the blown-up ``a2`` coordinate loses a
        # few ulps at this double root; the analytic threshold is still closed
        # to near-machine precision.
        self.assertLess(abs(float(determinant)), 5.0e-14)
        self.assertFalse(
            stationary["classical_stationary_turing_from_stable_homogeneous_state"]
        )

    def test_wide_negative_a2_has_stationary_real_band_but_k0_is_unstable(self) -> None:
        parameters = TemporalParameters(0.08, -20.0, 1.0)
        stationary = stationary_turing_diagnostics(parameters)
        self.assertTrue(stationary["has_stationary_real_unstable_band"])
        q_lower, q_upper = stationary["q_roots"]
        self.assertGreater(q_lower, 0.0)
        self.assertGreater(q_upper, q_lower)
        midpoint_k = np.sqrt((q_lower + q_upper) / 2.0)
        _, determinant_inside = symbol_trace_determinant(parameters, midpoint_k)
        _, determinant_below = symbol_trace_determinant(
            parameters, np.sqrt(q_lower) * 0.5
        )
        _, determinant_above = symbol_trace_determinant(
            parameters, np.sqrt(q_upper) * 1.5
        )
        self.assertLess(float(determinant_inside), 0.0)
        self.assertGreater(float(determinant_below), 0.0)
        self.assertGreater(float(determinant_above), 0.0)
        self.assertGreater(float(spectral_abscissa(parameters, 0.0)), 0.0)
        self.assertFalse(
            stationary["classical_stationary_turing_from_stable_homogeneous_state"]
        )

    def test_inaccessible_stationary_threshold_boundary(self) -> None:
        # 2*r^2*sqrt(epsilon)>1 makes alpha<=-2*r^2*sqrt(epsilon)
        # impossible because alpha=a^2-1>=-1.
        self.assertIsNone(stationary_band_a2_interval(1.0, 1.0))
        # Equality gives a single endpoint, not the strict open interval
        # required for a real-unstable stationary band.
        self.assertIsNone(stationary_band_a2_interval(1.0, 0.25))

    def test_invalid_parameters_and_wavenumbers_are_rejected(self) -> None:
        with self.assertRaises(ValueError):
            TemporalParameters(0.0, 0.0, 1.0)
        with self.assertRaises(ValueError):
            TemporalParameters(0.08, 0.0, 0.0)
        with self.assertRaises(ValueError):
            TemporalParameters(0.08, np.nan, 1.0)
        with self.assertRaises(ValueError):
            fourier_symbol(TemporalParameters(0.08), np.inf)


class ScanAndFigureContractTests(unittest.TestCase):
    def test_frozen_cartesian_slices_have_no_stationary_band(self) -> None:
        configuration = json.loads(CONFIG.read_text(encoding="utf-8"))
        values = configuration["turing"]["frozen_parameter_slices"]
        scan = scan_parameter_grid(
            values["r"], values["a2"], values["epsilon"]
        )
        self.assertEqual(scan["shape"], [3, 3, 3])
        self.assertEqual(scan["point_count"], 27)
        self.assertEqual(scan["classical_stationary_turing_point_count"], 0)
        self.assertIsNone(scan["first_stationary_band_witness"])
        self.assertEqual(scan["regime_counts"][STABLE_ALL_K], 9)
        self.assertEqual(scan["regime_counts"][HOPF_BOUNDARY_K0], 9)
        self.assertEqual(scan["regime_counts"][LONG_WAVE_OSCILLATORY], 9)

    def test_report_wide_scan_finds_only_nonclassical_stationary_witnesses(self) -> None:
        configuration = json.loads(CONFIG.read_text(encoding="utf-8"))
        report = build_prescreen_report(configuration)
        primary = report["primary"]
        self.assertEqual(primary["homogeneous_status"], HOPF_BOUNDARY_K0)
        self.assertFalse(
            primary["stationary"]["has_stationary_real_unstable_band"]
        )
        wide = report["wide_diagnostic_domain"]["scan"]
        self.assertIsNotNone(wide["first_stationary_band_witness"])
        self.assertEqual(wide["classical_stationary_turing_point_count"], 0)
        witness = report["wide_stationary_band_witness_at_primary_r_epsilon"]
        self.assertTrue(
            witness["stationary"]["has_stationary_real_unstable_band"]
        )
        self.assertIn("not classical", witness["interpretation"])
        self.assertEqual(
            report["wide_diagnostic_domain"]["r"],
            configuration["turing"]["wide_r_grid"],
        )
        self.assertEqual(
            report["wide_diagnostic_domain"]["a2"],
            configuration["turing"]["wide_a2_grid"],
        )
        self.assertEqual(
            report["wide_diagnostic_domain"]["epsilon_log_grid"],
            configuration["turing"]["wide_epsilon_log_grid"],
        )
        self.assertAlmostEqual(
            witness["parameters"]["a2"],
            configuration["turing"]["remote_nonclassical_a2"],
        )

    def test_plot_quantity_contracts_have_aligned_lengths(self) -> None:
        parameters = TemporalParameters(0.08, 0.0, 1.0)
        k = np.linspace(0.0, 25.0, 101)
        curve = dispersion_curve(parameters, k)
        self.assertTrue(all(len(values) == k.size for values in curve.values()))
        threshold = threshold_curve(np.array([0.04, 0.08, 0.12]), 1.0)
        self.assertTrue(all(len(values) == 3 for values in threshold.values()))
        self.assertAlmostEqual(threshold["onset_k_critical"][1], 12.5)

    def test_independent_runner_writes_json_schema_and_concise_stdout(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            output = Path(directory) / "prescreen.json"
            stdout = io.StringIO()
            with redirect_stdout(stdout):
                return_code = main(
                    ["--config", str(CONFIG), "--output", str(output)]
                )
            self.assertEqual(return_code, 0)
            report = json.loads(output.read_text(encoding="utf-8"))
            concise = json.loads(stdout.getvalue())
            self.assertEqual(report["schema_version"], SCHEMA_VERSION)
            self.assertEqual(concise["schema_version"], SCHEMA_VERSION)
            self.assertIn("model", report)
            self.assertIn("claim_boundary", report)
            self.assertIn("primary", report)
            self.assertIn("frozen_cartesian_slice_scan", report)
            self.assertIn("wide_diagnostic_domain", report)
            self.assertIn("recommended_figure_quantities", report)
            self.assertFalse(
                report["primary"]["stationary"][
                    "classical_stationary_turing_from_stable_homogeneous_state"
                ]
            )


if __name__ == "__main__":
    unittest.main()
