from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import numpy as np

from numerics.check_vdp_dynamics_screening import (
    REQUIRED_QA_CHECKS,
    check_manifest_decision_consistency,
    check_qa_record,
    check_run_provenance,
    check_source_files,
    recompute_qa_checks,
)
from numerics.render_vdp_dynamics_figures import validate_render_contract
from numerics.run_vdp_dynamics_screening import (
    DEVELOPMENT_RUN_MODE,
    OFFICIAL_RUN_MODE,
    ROOT,
    _bloch_qa,
    _grid,
    _pulse_qa,
    baseline_git_blob_hashes,
    build_decision_record,
    git_blob_sha256,
    git_text,
    resolve_candidate_baseline,
    sha256,
    source_file_hashes,
    source_files_for,
    run,
    validate_config,
    verify_baseline_git_blobs,
    verify_unchanged_source_snapshot,
)


ROOT = Path(__file__).resolve().parents[1]
CONFIG = ROOT / "numerics/config/vdp_dynamics_screening.json"


class DynamicsScreeningContractTests(unittest.TestCase):
    def test_frozen_configuration_contract(self) -> None:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        validate_config(config)
        box = config["issue_7_preselected_box"]
        self.assertEqual(box["r"], [0.04, 0.08])
        self.assertEqual(box["a2"], [-0.25, 0.25])
        self.assertEqual(box["epsilon"], [0.8, 1.2])
        self.assertIn("Do not move", box["immutability_rule"])

    def test_unknown_configuration_field_is_rejected(self) -> None:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        config["silently_ignored"] = True
        with self.assertRaisesRegex(ValueError, "configuration drift"):
            validate_config(config)

    def test_every_v1_value_and_nonclaim_is_frozen(self) -> None:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        config["canard"]["fold_collar"] = 0.003
        with self.assertRaisesRegex(ValueError, "frozen v1 configuration values"):
            validate_config(config)

        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        config["nonclaims"][0] += " changed"
        with self.assertRaisesRegex(ValueError, "frozen v1 configuration values"):
            validate_config(config)

    def test_grid_contract_rejects_bad_counts_and_endpoints(self) -> None:
        with self.assertRaises(ValueError):
            _grid([0.0, 1.0, 1], name="bad")
        with self.assertRaises(ValueError):
            _grid([1.0, 0.0, 5], name="bad")
        with self.assertRaises(ValueError):
            _grid([0.0, 1.0, 4.5], name="bad")

    def test_decision_keeps_existence_and_stability_scopes_separate(self) -> None:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        turing = {
            "primary": {
                "stationary": {"obstruction": "opposite signs"},
            }
        }
        bloch = {
            "screening_outcome": "SAMPLED_BLOCH_INSTABILITY_DETECTED",
            "profiles": [
                {
                    "label": "A0",
                    "screening_outcome": "SAMPLED_BLOCH_INSTABILITY_DETECTED",
                }
            ],
        }
        pulses = {
            "profiles": [
                {"profile": "pulse_1", "screen_signal": "POSITIVE_GROWTH_CANDIDATE"}
            ]
        }
        canard = {
            "canard_identification_status": "NO_CANARD_IDENTIFICATION_FROM_CURRENT_DATA",
            "positive_fold_singular_reduced_classification": "FSN_DEGENERATE_SINGULAR_LIMIT",
            "required_before_canard_claim": ["slow manifolds"],
        }
        decision = build_decision_record(config, turing, bloch, pulses, canard)
        self.assertFalse(decision["claim_bearing"])
        self.assertEqual(
            decision["conclusions"]["issue_7"]["status"],
            "PROCEED_WITH_EXISTENCE_VALIDATION_ON_PRESELECTED_BOX",
        )
        self.assertIn("not a temporal-stability box", decision["conclusions"]["issue_7"]["scope"])

    def test_source_census_is_complete_and_strictly_hashed(self) -> None:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        paths = source_files_for(CONFIG, config)
        relative = {str(path.relative_to(ROOT)) for path in paths}
        self.assertTrue(
            {
                "numerics/vdp_bridge.py",
                "numerics/vdp_outer.py",
                "numerics/vdp_pole.py",
                "numerics/rfsn_numerics.py",
                "numerics/check_vdp_dynamics_screening.py",
                "numerics/VDP_DYNAMICS_FIGURE_CONTRACTS.md",
                "numerics/results/vdp_v1_v7/v7_periodic.npz",
                "numerics/results/vdp_v1_v7/v7_multipulses.npz",
                "numerics/results/vdp_v1_v7/v4_v5_matched_candidate.npz",
            }
            <= relative
        )
        self.assertNotIn("numerics/VDP_DYNAMICS_SCREENING_REPORT.md", relative)
        contract = {"source_files": source_file_hashes(CONFIG, config)}
        self.assertEqual(check_source_files(contract, CONFIG, config), [])
        stale_key = "numerics/vdp_turing.py"
        contract["source_files"][stale_key] = "0" * 64
        self.assertIn(
            f"source SHA-256 mismatch: {stale_key}",
            check_source_files(contract, CONFIG, config),
        )

    def test_baseline_inputs_equal_the_frozen_tag_blobs(self) -> None:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        resolved = resolve_candidate_baseline(config)
        self.assertTrue(resolved.startswith("61ac680"))
        blobs = baseline_git_blob_hashes(config, resolved_revision=resolved)
        self.assertEqual(blobs, verify_baseline_git_blobs(config, resolved_revision=resolved))
        self.assertEqual(len(blobs), 3)
        for relative, digest in blobs.items():
            self.assertEqual(digest, sha256(ROOT / relative))

        contract = {
            "run_mode": DEVELOPMENT_RUN_MODE,
            "source_dirty_at_run_start": True,
            "source_revision_at_run_start": git_text("rev-parse", "HEAD"),
            "source_revision_at_run_end": git_text("rev-parse", "HEAD"),
            "candidate_tag_resolved": resolved,
            "candidate_baseline_git_blobs": dict(blobs),
        }
        self.assertEqual(
            check_run_provenance(
                contract, config, allow_development_artifact=True
            ),
            [],
        )
        first = next(iter(blobs))
        contract["candidate_baseline_git_blobs"][first] = "0" * 64
        self.assertIn(
            "candidate baseline Git-blob binding differs from frozen tag",
            check_run_provenance(
                contract, config, allow_development_artifact=True
            ),
        )

    def test_official_clean_policy_and_development_override_are_distinct(self) -> None:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        revision = git_text("rev-parse", "HEAD")
        baseline_revision = resolve_candidate_baseline(config)
        blobs = baseline_git_blob_hashes(
            config, resolved_revision=baseline_revision
        )
        contract = {
            "run_mode": OFFICIAL_RUN_MODE,
            "source_dirty_at_run_start": True,
            "source_revision_at_run_start": revision,
            "source_revision_at_run_end": revision,
            "candidate_tag_resolved": baseline_revision,
            "candidate_baseline_git_blobs": blobs,
        }
        self.assertIn(
            "official artifact did not start from a clean repository",
            check_run_provenance(contract, config),
        )
        contract["run_mode"] = DEVELOPMENT_RUN_MODE
        self.assertIn(
            "development-only dirty-source artifact rejected by official checker",
            check_run_provenance(contract, config),
        )
        self.assertEqual(
            check_run_provenance(
                contract, config, allow_development_artifact=True
            ),
            [],
        )

    def test_runner_default_refuses_dirty_source_before_computation(self) -> None:
        def fake_git_text(*arguments: str) -> str:
            if arguments == ("rev-parse", "HEAD"):
                return "1" * 40
            if arguments == ("status", "--porcelain", "--untracked-files=all"):
                return " M numerics/vdp_turing.py"
            raise AssertionError(f"unexpected Git query: {arguments}")

        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary) / "result"
            with patch(
                "numerics.run_vdp_dynamics_screening.git_text",
                side_effect=fake_git_text,
            ):
                with self.assertRaisesRegex(RuntimeError, "clean repository"):
                    run(CONFIG, output)
            self.assertFalse(output.exists())

    def test_official_source_hashes_must_equal_recorded_commit_blobs(self) -> None:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        revision = git_text("rev-parse", "HEAD")
        baseline_revision = resolve_candidate_baseline(config)
        baseline_blobs = baseline_git_blob_hashes(
            config, resolved_revision=baseline_revision
        )
        relative = "numerics/results/vdp_v1_v7/v7_periodic.npz"
        digest = git_blob_sha256(revision, relative)
        contract = {
            "run_mode": OFFICIAL_RUN_MODE,
            "source_dirty_at_run_start": False,
            "source_revision_at_run_start": revision,
            "source_revision_at_run_end": revision,
            "source_revision_git_blobs": {relative: digest},
            "source_files": {relative: digest},
            "candidate_tag_resolved": baseline_revision,
            "candidate_baseline_git_blobs": baseline_blobs,
        }
        self.assertEqual(check_run_provenance(contract, config), [])
        contract["source_files"][relative] = "0" * 64
        self.assertIn(
            "official source hashes differ from source-revision Git blobs",
            check_run_provenance(contract, config),
        )

    def test_source_snapshot_drift_is_rejected(self) -> None:
        hashes = {"source.py": "a" * 64, "input.npz": "b" * 64}
        verify_unchanged_source_snapshot(
            hashes,
            dict(hashes),
            start_revision="1" * 40,
            end_revision="1" * 40,
            start_baseline_revision="2" * 40,
            end_baseline_revision="2" * 40,
        )
        changed = dict(hashes)
        changed["source.py"] = "c" * 64
        with self.assertRaisesRegex(RuntimeError, "source.py"):
            verify_unchanged_source_snapshot(
                hashes,
                changed,
                start_revision="1" * 40,
                end_revision="1" * 40,
                start_baseline_revision="2" * 40,
                end_baseline_revision="2" * 40,
            )

    def test_new_resolution_boundary_and_time_qa_gates_are_active(self) -> None:
        limits = json.loads(CONFIG.read_text(encoding="utf-8"))["qa"]
        sensitivity = {
            "leading_mode_complex_eigenpair_relative_residual": 0.0,
            "spectral_grid_abscissa_difference": 0.0,
            "spectral_boundary_abscissa_difference": 0.0,
            "time_step_final_state_difference_over_initial_rms": 0.0,
            "grid_final_state_difference_over_initial_rms": 0.0,
            "boundary_final_state_difference_over_initial_rms": 0.0,
            "leading_mode_expected_linear_envelope_amplification": 1.0,
            "leading_mode_observed_nonlinear_amplification": 1.0,
        }
        pulse_report = {
            "homogeneous_fourier_validation": {
                "finite_volume_matrix_vs_analytic_discrete_modes": {
                    "neumann": {"maximum_eigenvalue_matching_error": 0.0},
                    "periodic": {"maximum_eigenvalue_matching_error": 0.0},
                }
            },
            "profiles": [
                {
                    "sensitivity": sensitivity,
                    "short_time_runs": {
                        "fine": {"zero_perturbation_defect_inf": 0.0}
                    },
                }
            ],
        }
        pulse_checks = _pulse_qa(pulse_report, limits)
        self.assertTrue(all(row["passed"] for row in pulse_checks.values()))
        sensitivity["time_step_final_state_difference_over_initial_rms"] = (
            1.01 * limits["pulse_time_step_final_state_difference_max"]
        )
        self.assertFalse(
            _pulse_qa(pulse_report, limits)["time_step_final_state_sensitivity"][
                "passed"
            ]
        )

        bloch_result = SimpleNamespace(
            conjugacy_defects=np.array([0.0]),
            translation_residuals=np.array([0.0]),
            refinement_defects=np.array([[0.0]]),
            constant_dispersion_defect=0.0,
        )
        self.assertTrue(all(row["passed"] for row in _bloch_qa(bloch_result, limits).values()))
        bloch_result.refinement_defects[0, 0] = (
            1.01 * limits["bloch_refinement_defect_max"]
        )
        self.assertFalse(
            _bloch_qa(bloch_result, limits)["grid_refinement_matching_defect"][
                "passed"
            ]
        )

    def test_checker_recomputes_every_qa_value_and_rejects_tampering(self) -> None:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary)
            (output / "bloch_report.json").write_text(
                json.dumps(
                    {"constant_profile_dispersion_matching_defect": 1.0e-12}
                )
                + "\n",
                encoding="utf-8",
            )
            np.savez_compressed(
                output / "bloch_arrays.npz",
                constant_dispersion_defect=np.asarray([1.0e-12]),
                conjugacy_defects=np.asarray([2.0e-12]),
                translation_residuals=np.asarray([3.0e-12]),
                refinement_defects=np.asarray([[4.0e-12]]),
            )
            sensitivity = {
                "leading_mode_complex_eigenpair_relative_residual": 5.0e-12,
                "spectral_grid_abscissa_difference": 6.0e-6,
                "spectral_boundary_abscissa_difference": 7.0e-12,
                "time_step_final_state_difference_over_initial_rms": 8.0e-4,
                "grid_final_state_difference_over_initial_rms": 9.0e-6,
                "boundary_final_state_difference_over_initial_rms": 1.0e-12,
                "leading_mode_expected_linear_envelope_amplification": 1.01,
                "leading_mode_observed_nonlinear_amplification": 1.01001,
            }
            pulse = {
                "homogeneous_fourier_validation": {
                    "finite_volume_matrix_vs_analytic_discrete_modes": {
                        "neumann": {"maximum_eigenvalue_matching_error": 1.0e-13},
                        "periodic": {"maximum_eigenvalue_matching_error": 2.0e-13},
                    }
                },
                "profiles": [
                    {
                        "sensitivity": sensitivity,
                        "short_time_runs": {
                            "fine": {"zero_perturbation_defect_inf": 0.0}
                        },
                    }
                ],
            }
            (output / "pulse_temporal_report.json").write_text(
                json.dumps(pulse) + "\n", encoding="utf-8"
            )
            (output / "turing_report.json").write_text(
                json.dumps(
                    {
                        "primary": {"homogeneous_status": "HOPF_BOUNDARY_K0"},
                        "wide_diagnostic_domain": {
                            "scan": {"classical_stationary_turing_point_count": 0}
                        },
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            (output / "canard_report.json").write_text(
                json.dumps(
                    {
                        "canard_identification_status": (
                            "NO_CANARD_IDENTIFICATION_FROM_CURRENT_DATA"
                        ),
                        "outer_diagnostics": {"crosses_a_fold": False},
                    }
                )
                + "\n",
                encoding="utf-8",
            )
            recomputed = recompute_qa_checks(output, config)
            self.assertEqual(set(recomputed), REQUIRED_QA_CHECKS)
            self.assertTrue(all(row["passed"] for row in recomputed.values()))
            qa = {
                "schema_version": "vdp-dynamics-screening-qa/1",
                "status": "PASS_COMPUTATIONAL_QA_NOT_A_THEOREM",
                "claim_bearing": False,
                "checks": copy.deepcopy(recomputed),
                "passed_count": 17,
                "check_count": 17,
            }
            self.assertEqual(check_qa_record(qa, recomputed), [])
            first = "pulse.time_step_final_state_sensitivity"
            qa["checks"][first]["value"] = 0.0
            qa["checks"][first]["passed"] = True
            self.assertIn(
                f"QA row differs from independent recomputation: {first}",
                check_qa_record(qa, recomputed),
            )

    def test_manifest_status_and_decision_tampering_is_rejected(self) -> None:
        qa = {"status": "PASS_COMPUTATIONAL_QA_NOT_A_THEOREM"}
        decision = {"conclusions": {"issue_7": {"status": "PROCEED"}}}
        render_contract = {"qa_status": qa["status"]}
        manifest = {
            "final_status": qa["status"],
            "screening_decision": copy.deepcopy(decision["conclusions"]),
        }
        self.assertEqual(
            check_manifest_decision_consistency(
                manifest, render_contract, qa, decision
            ),
            [],
        )
        manifest["final_status"] = "PASS"
        manifest["screening_decision"]["issue_7"]["status"] = "ALTERED"
        failures = check_manifest_decision_consistency(
            manifest, render_contract, qa, decision
        )
        self.assertIn("manifest final status differs from QA record", failures)
        self.assertIn(
            "manifest screening decision differs from decision record", failures
        )

    def test_renderer_rejects_stale_configuration_hash(self) -> None:
        config = json.loads(CONFIG.read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            contract = {
                "configuration_version": config["configuration_version"],
                "configuration_sha256": "0" * 64,
                "claim_bearing": False,
                "source_files": source_file_hashes(CONFIG, config),
            }
            (directory / "render_contract.json").write_text(
                json.dumps(contract) + "\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, "configuration hash"):
                validate_render_contract(directory, CONFIG)

            contract["configuration_sha256"] = hashlib.sha256(
                CONFIG.read_bytes()
            ).hexdigest()
            (directory / "render_contract.json").write_text(
                json.dumps(contract) + "\n", encoding="utf-8"
            )
            returned = validate_render_contract(directory, CONFIG)
            self.assertEqual(returned["configuration_version"], 1)

            stale_key = "numerics/vdp_turing.py"
            contract["source_files"][stale_key] = "0" * 64
            (directory / "render_contract.json").write_text(
                json.dumps(contract) + "\n", encoding="utf-8"
            )
            with self.assertRaisesRegex(ValueError, "source hash differs"):
                validate_render_contract(directory, CONFIG)


if __name__ == "__main__":
    unittest.main()
