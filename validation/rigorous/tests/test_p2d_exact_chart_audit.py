from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


RIGOROUS = Path(__file__).resolve().parents[1]
REPOSITORY = RIGOROUS.parents[1]
AUDIT = RIGOROUS / "audit_p2d_exact_chart.py"

EXPECTED_CHECKS = {
    "omega_is_skew_and_nondegenerate",
    "reverser_is_anti_symplectic_involution",
    "hamiltonian_vector_field_identity",
    "hamiltonian_is_reverser_invariant",
    "vector_field_is_reversible",
    "linearization_is_hamiltonian_and_reversible",
    "kato_frame_equals_algebraic_frame_times_change",
    "first_kato_column_is_transported_vector_over_normalizer",
    "second_kato_column_is_positive_complex_partner",
    "kato_frame_has_expanding_block",
    "kato_expanding_plane_is_lagrangian",
    "normalizer_squared_is_exact_transported_vector_norm",
    "normalized_first_kato_vector_has_unit_euclidean_norm",
    "kato_euclidean_gram_has_exact_nonorthogonal_closed_form",
    "current_kato_complex_frame_is_not_euclidean_orthonormal_in_general",
    "reverser_maps_expanding_to_stable",
    "cross_pairing_is_symmetric_traceless",
    "cross_pairing_closed_form_d_e",
    "kappa_positive_closed_form",
    "kappa_squared_is_d_squared_plus_e_squared",
    "cross_pairing_determinant_is_minus_kappa_squared",
    "half_angle_unit_circle_and_positive_cosine",
    "half_angle_double_angle_formulas",
    "half_angle_is_special_orthogonal",
    "half_angle_diagonalizes_cross_pairing",
    "actual_half_angle_branch_diagonalizes_physical_cross_pairing",
    "actual_completion_L_is_exact_symplectic",
    "actual_completion_intertwines_physical_and_standard_reversers",
    "actual_completion_inverse_conjugates_physical_linearization_to_kato_blocks",
    "quadratic_hamiltonian_uses_I2K",
    "flagship_I2F_is_minus_I2K",
    "FK_dictionary_T_is_symplectic_involution",
    "FK_dictionary_T_commutes_with_standard_reverser",
    "FK_dictionary_T_preserves_I1",
    "FK_dictionary_T_sends_I2F_to_I2K_without_action_flip",
    "FK_dictionary_C0_sends_phase_phi_to_minus_phi",
    "FK_dictionary_C0_reverses_J_phase_orientation",
    "FK_dictionary_transports_flagship_H2_to_kato_H2",
    "kato_expanding_phase_speed_is_plus_beta",
    "linear_zero_energy_h2_is_alpha_tau_plus_beta_nu",
    "linear_zero_energy_q_is_minus_beta_over_alpha_nu",
    "linear_zero_energy_partial_tau_is_alpha",
    "outgoing_scout_expanding_radius_is_rho",
    "outgoing_scout_I1_is_tau",
    "outgoing_scout_I2K_is_nu",
    "outgoing_scout_pullback_is_dphi_wedge_dnu",
    "outgoing_scout_primitive_is_minus_nu_dphi_plus_half_dq",
    "incoming_scout_stable_radius_is_rho",
    "incoming_scout_I1_is_tau",
    "incoming_scout_I2K_is_nu",
    "incoming_scout_pullback_is_dphi_wedge_dnu",
    "incoming_scout_primitive_is_minus_nu_dphi_minus_half_dq",
    "linear_incoming_expanding_radius_squared_is_nu_squared_over_alpha_squared_rho_squared",
    "linear_positive_flight_domain_is_zero_less_abs_nu_less_alpha_rho_squared",
    "linear_reach_time_hits_rho_and_has_Dlog_minus_one_over_alpha",
    "linear_phase_Dlog_from_plus_beta_speed_is_minus_beta_over_alpha",
    "physical_primitive_gauge_is_exact",
    "actual_linear_symplectic_frame_preserves_symmetric_primitive",
}

EXPECTED_EXACT_FORMULAS = {
    "kato_euclidean_gram": [
        [
            "1",
            "2*alpha*(alpha^2-1/2)/(N^2*beta)",
        ],
        [
            "2*alpha*(alpha^2-1/2)/(N^2*beta)",
            "6*(alpha^4-(2*sqrt(2)/3)*alpha^3-alpha^2/2+1/2)/(N^2*beta^2)",
        ],
    ],
    "kato_euclidean_status": (
        "The current normalized Kato complex frame has a unit first column "
        "but is not Euclidean orthonormal in general."
    ),
    "linear_phase_increment": (
        "Delta_lin=(beta/alpha)*log(alpha*rho^2/|nu|)"
    ),
    "linear_phase_log_slope": "D_log(Delta_lin)=-beta/alpha",
    "linear_positive_flight_domain": "0<|nu|<alpha*rho^2",
    "linear_positive_flight_parameterization": (
        "|nu|=alpha*rho^2/(1+sigma), sigma>0"
    ),
    "linear_reach_time": (
        "T_lin=(1/alpha)*log(alpha*rho^2/|nu|)"
    ),
    "normalizer_squared": "6*alpha^2-4*sqrt(2)*alpha+3",
}

EXPECTED_OPEN_SCOPE = [
    "nonlinear analytic Moser normal form",
    "nonlinear zero-energy fiber existence and uniqueness",
    "weighted-log local passage bounds",
    "exact nonlinear chart gauges and overlap compatibility",
    "frozen-box positive-radial branch margins",
    "parameter two-jets of the symplectic completion",
]

EXPECTED_ATOMS = {
    "V2.CHART.SYMPLECTIC_FRAME",
    "V2.CHART.ANALYTIC_NORMAL_FORM",
    "V2.CHART.ZERO_ENERGY",
    "V2.CHART.EXACT_SECTIONS",
    "V2.CHART.WEIGHTED_PASSAGE",
    "V2.CHART.PHYSICAL_SLIDES",
    "V2.CHART.OVERLAPS",
}


def execute(cwd: Path, *, cache_prefix: Path | None = None) -> subprocess.CompletedProcess[bytes]:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    if cache_prefix is not None:
        environment["PYTHONPYCACHEPREFIX"] = str(cache_prefix)
    return subprocess.run(
        [sys.executable, "-B", str(AUDIT)],
        cwd=cwd,
        env=environment,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=30,
        check=False,
    )


class P2DExactChartAuditTests(unittest.TestCase):
    def test_check_set_is_frozen_true_and_byte_deterministic(self) -> None:
        first = execute(REPOSITORY)
        second = execute(REPOSITORY)
        self.assertEqual(first.returncode, 0, first.stderr.decode())
        self.assertEqual(second.returncode, 0, second.stderr.decode())
        self.assertEqual(first.stdout, second.stdout)
        self.assertEqual(first.stderr, b"")
        self.assertEqual(first.stdout.count(b"\n"), 1)

        report = json.loads(first.stdout)
        self.assertEqual(
            report["schema_version"],
            "rfsn-vdp-p2d-exact-chart-audit/2",
        )
        self.assertEqual(report["status"], "PASS")
        self.assertEqual(
            report["method"],
            "exact-symbolic-identities-no-sampling-no-file-inputs",
        )
        self.assertEqual(report["backend"]["name"], "sympy")
        self.assertEqual(set(report["checks"]), EXPECTED_CHECKS)
        self.assertTrue(all(report["checks"].values()))

    def test_claim_boundary_keeps_parent_open(self) -> None:
        completed = execute(REPOSITORY)
        self.assertEqual(completed.returncode, 0, completed.stderr.decode())
        report = json.loads(completed.stdout)
        boundary = report["claim_boundary"]
        self.assertFalse(boundary["claim_bearing"])
        self.assertEqual(
            boundary["parent_obligation"], "V2.EXACT_CHART remains OPEN"
        )
        self.assertEqual(boundary["open_scope"], EXPECTED_OPEN_SCOPE)
        self.assertEqual(set(boundary["v2_chart_atoms"]), EXPECTED_ATOMS)
        self.assertEqual(set(boundary["v2_chart_atoms"].values()), {"OPEN"})
        self.assertNotIn(
            "nonlinear zero-energy fiber existence and uniqueness",
            boundary["exact_identity_scope_only"],
        )
        self.assertNotEqual(
            boundary["v2_chart_atoms"]["V2.CHART.SYMPLECTIC_FRAME"],
            "PASS",
        )

    def test_exact_formula_payload_is_fully_frozen(self) -> None:
        completed = execute(REPOSITORY)
        self.assertEqual(completed.returncode, 0, completed.stderr.decode())
        report = json.loads(completed.stdout)
        formulas = report["exact_formulas"]
        self.assertEqual(formulas, EXPECTED_EXACT_FORMULAS)

    def test_has_no_working_tree_or_bytecode_cache_input_dependency(self) -> None:
        baseline = execute(REPOSITORY)
        self.assertEqual(baseline.returncode, 0, baseline.stderr.decode())
        with tempfile.TemporaryDirectory(prefix="p2d-exact-audit-") as temporary:
            root = Path(temporary)
            poison_cache = root / "__pycache__"
            poison_cache.mkdir()
            (poison_cache / "audit_p2d_exact_chart.cpython-314.pyc").write_bytes(
                b"not valid bytecode and deliberately unrelated"
            )
            (root / "audit_p2d_exact_chart.py").write_text(
                "raise RuntimeError('cwd poison must not be imported')\n",
                encoding="utf-8",
            )
            (root / "config.json").write_text(
                '{"poison":"must not be read"}\n', encoding="utf-8"
            )
            before = sorted(
                path.relative_to(root).as_posix()
                for path in root.rglob("*")
            )
            poisoned = execute(root, cache_prefix=root / "cache-prefix")
            after = sorted(
                path.relative_to(root).as_posix()
                for path in root.rglob("*")
            )
        self.assertEqual(poisoned.returncode, 0, poisoned.stderr.decode())
        self.assertEqual(poisoned.stdout, baseline.stdout)
        self.assertEqual(poisoned.stderr, b"")
        self.assertEqual(after, before)
        report = json.loads(poisoned.stdout)
        self.assertEqual(report["input_policy"], {
            "external_files": [],
            "floating_point": False,
            "sampling": False,
        })

    def test_missing_sympy_is_one_line_machine_readable_fail(self) -> None:
        completed = subprocess.run(
            [sys.executable, "-S", "-B", str(AUDIT)],
            cwd=REPOSITORY,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=30,
            check=False,
        )
        self.assertEqual(completed.returncode, 1)
        self.assertEqual(completed.stderr, b"")
        self.assertEqual(completed.stdout.count(b"\n"), 1)
        report = json.loads(completed.stdout)
        self.assertEqual(report["status"], "FAIL")
        self.assertEqual(report["backend"], {"name": "sympy", "version": None})
        self.assertEqual(
            report["claim_boundary"]["parent_obligation"],
            "V2.EXACT_CHART remains OPEN",
        )


if __name__ == "__main__":
    unittest.main()
