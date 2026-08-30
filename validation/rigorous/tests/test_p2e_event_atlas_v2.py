from __future__ import annotations

import copy
import json
import tempfile
import unittest
from pathlib import Path

from validation.rigorous.check_p2e_event_atlas_v2 import (
    AuditError,
    DEFAULT_CONFIG,
    EXPECTED_FUNCTIONS,
    EXPECTED_TIME_DIFFERENCE_BINDINGS,
    EXPECTED_LISTS,
    REQUIRED_MARGINS,
    TIME_DIFFERENCES,
    audit,
    validate_census,
    validate_full_run_gate,
    validate_incidence,
    validate_lists,
    validate_m0,
    validate_normalization,
    validate_numerical_method,
    validate_priority,
)


def base_config() -> dict:
    return json.loads(DEFAULT_CONFIG.read_text(encoding="utf-8"))


def audit_copy(config: dict) -> dict:
    with tempfile.TemporaryDirectory() as temporary:
        path = Path(temporary) / "event-atlas-gate.json"
        path.write_text(json.dumps(config), encoding="utf-8")
        return audit(path)


def frozen_function_records() -> list[dict]:
    records = []
    for identifier, (role, clock_role) in EXPECTED_FUNCTIONS.items():
        time_difference = None
        if identifier in TIME_DIFFERENCES:
            side_occurrence, terminal = EXPECTED_TIME_DIFFERENCE_BINDINGS[
                identifier]
            time_difference = {
                "left_event_time_id": f"tau_left_{identifier}",
                "right_event_time_id": f"tau_right_{identifier}",
                "side_occurrence_id": side_occurrence,
                "associated_terminal_function_id": terminal,
                "tie_policy": "RANK_ON_NONEMPTY_TIE_GAP_ONLY_IF_EMPTY",
            }
        records.append({
            "id": identifier,
            "role": role,
            "clock_role": clock_role,
            "formula": f"exact_formula_{identifier}",
            "formula_type": "EXACT_EXPRESSION",
            "domain_ids": ["C.A"],
            "coorientation": "POSITIVE_IS_FORWARD",
            "is_carrier_boundary": False,
            "time_difference": time_difference,
            "frozen": True,
        })
    return records


def simple_carrier(dimension: int = 2) -> dict:
    return {
        "dimension": dimension,
        "boundary_strata": [
            {"id": "INTERIOR", "active_boundary_function_ids": []},
        ],
    }


def incidence_row(
        identifier: str, functions: list[str], signs: tuple[int, ...],
        *, status: str = "EMPTY", component_ids: list[str] | None = None,
        empty_margin_id: str | None = "empty-gap-cert",
        rank_certificate_id: str | None = None,
        declared_tie: bool = False, dimension: int = 2) -> dict:
    active_count = sum(sign == 0 for sign in signs)
    return {
        "id": identifier,
        "list_id": "L.TEST",
        "boundary_stratum_id": "INTERIOR",
        "sign_vector": dict(zip(functions, signs)),
        "status": status,
        "expected_dimension": dimension - active_count,
        "component_ids": component_ids or [],
        "rank_certificate_id": rank_certificate_id,
        "empty_margin_id": empty_margin_id,
        "declared_tie": declared_tie,
    }


class P2eEventAtlasV2StructuralGateTest(unittest.TestCase):
    def test_committed_gate_is_ready_only_for_non_evidentiary_scouting(self) -> None:
        result = audit()

        self.assertEqual(result["structure_status"],
                         "READY_TO_SCOUT_NON_EVIDENTIARY")
        self.assertEqual(result["status"], "STOP_BEFORE_FULL_RUN")
        self.assertEqual(result["mathematical_status"], "INCONCLUSIVE")
        self.assertEqual(result["integrity_status"], "STRUCTURE_SCHEMA_VALID")
        self.assertEqual(result["atlas_claim_status"], "PENDING")
        self.assertFalse(result["claim_bearing"])
        self.assertFalse(result["full_run_authorized"])
        self.assertFalse(result["full_capd_executed"])
        self.assertEqual(result["parameter_cells"], 4096)
        self.assertEqual(len(result["missing_materialization_sections"]), 6)
        self.assertNotIn("carriers", result["missing_materialization_sections"])
        self.assertTrue(all(item["status"] == "PENDING"
                            for item in result["obligations"]))

    def test_source_hash_tamper_is_rejected(self) -> None:
        config = base_config()
        config["source_bindings"][0]["sha256"] = "0" * 64
        with self.assertRaisesRegex(AuditError, "source binding changed"):
            audit_copy(config)

    def test_parameter_cover_tamper_is_rejected(self) -> None:
        config = base_config()
        config["parameter_cover"]["bridge_cell_count"] = 4095
        with self.assertRaisesRegex(AuditError, "4096-cell parameter cover"):
            audit_copy(config)

    def test_structural_gate_cannot_pass_an_atlas_atom(self) -> None:
        config = base_config()
        config["obligations"][-1]["status"] = "PASS"
        with self.assertRaisesRegex(AuditError, "may not pass"):
            audit_copy(config)

    def test_incomplete_gate_cannot_authorize_full_run(self) -> None:
        config = base_config()
        config["full_run_gate"].update({
            "status": "READY_FOR_FIRST_FULL_RUN",
            "frozen_before_first_full_run": True,
            "materialization_commit": "0" * 40,
            "authorized_binary_sha256": "0" * 64,
        })
        with self.assertRaisesRegex(AuditError,
                                    "authorized while materialization"):
            audit_copy(config)

    def test_missing_section_cannot_hide_payload(self) -> None:
        config = base_config()
        config["materialization"]["incidence_complex"]["records"].append({
            "id": "unreviewed-incidence",
        })
        with self.assertRaisesRegex(AuditError, "unreviewed payload"):
            audit_copy(config)

    def test_normalized_pullback_domain_cannot_be_promoted_to_embedding(self) -> None:
        config = base_config()
        carrier = next(
            item for item in config["materialization"]["carriers"]["records"]
            if item["id"] == "Z.PLUS"
        )
        carrier["realization"]["injective_embedding_claim"] = True
        with self.assertRaisesRegex(AuditError,
                                    "promoted to a physical embedding"):
            audit_copy(config)

    def test_faces_cannot_freeze_before_carriers_and_functions(self) -> None:
        config = base_config()
        config["materialization"]["carriers"] = {
            "status": "MISSING", "design_geometry": None, "records": [],
        }
        with self.assertRaisesRegex(AuditError,
                                    "before carriers/functions"):
            audit_copy(config)

    def test_lists_cannot_freeze_before_carriers_and_functions(self) -> None:
        config = base_config()
        config["materialization"]["physical_event_faces"] = {
            "status": "MISSING", "records": [],
        }
        config["materialization"]["carriers"] = {
            "status": "MISSING", "design_geometry": None, "records": [],
        }
        with self.assertRaisesRegex(AuditError,
                                    "before carriers/functions"):
            audit_copy(config)

    def test_w_alg_cannot_be_promoted_to_an_event_clock(self) -> None:
        config = base_config()
        section = config["materialization"]["defining_functions"]
        section.update({"status": "FROZEN", "records": frozen_function_records()})
        next(item for item in section["records"]
             if item["id"] == "w_alg")["clock_role"] = "PHYSICAL_FACE"
        with self.assertRaisesRegex(AuditError, "changed mathematical role"):
            audit_copy(config)

    def test_return_side_cannot_reuse_the_homoclinic_side_occurrence(self) -> None:
        config = base_config()
        section = config["materialization"]["defining_functions"]
        section.update({"status": "FROZEN", "records": frozen_function_records()})
        q_ret = next(item for item in section["records"]
                     if item["id"] == "q_ret")
        q_ret["time_difference"]["side_occurrence_id"] = "u_h"
        with self.assertRaisesRegex(AuditError,
                                    "side/terminal occurrence binding"):
            audit_copy(config)

    def test_affine_proxy_and_carrier_boundary_duplication_are_rejected(self) -> None:
        for mutation, message in (
                ({"formula": "AFFINE_PROXY"}, "placeholder or proxy"),
                ({"is_carrier_boundary": True}, "duplicates a carrier boundary")):
            with self.subTest(mutation=mutation):
                config = base_config()
                section = config["materialization"]["defining_functions"]
                section.update({
                    "status": "FROZEN",
                    "records": frozen_function_records(),
                })
                next(item for item in section["records"]
                     if item["id"] == "g_alg").update(mutation)
                with self.assertRaisesRegex(AuditError, message):
                    audit_copy(config)

    def test_ambient_lists_cannot_introduce_a_second_competing_time(self) -> None:
        records = []
        for identifier, (carrier_id, functions, maximum_q) in EXPECTED_LISTS.items():
            del maximum_q
            records.append({
                "id": identifier,
                "carrier_id": carrier_id,
                "function_ids": copy.deepcopy(functions),
                "function_domains": {item: "FULL_DOMAIN" for item in functions},
                "boundary_strata": ["INTERIOR"],
                "pullback_map": f"exact_pullback_{identifier}",
                "disjoint_competing_overlap": bool(
                    set(functions) & TIME_DIFFERENCES),
                "frozen": True,
            })
        changed = next(item for item in records if item["id"] == "L.B.OUT.H")
        changed["function_ids"].append("q_alg")
        changed["function_domains"]["q_alg"] = "FULL_DOMAIN"
        with self.assertRaisesRegex(AuditError, "complete function list"):
            validate_lists({"status": "FROZEN", "records": records}, None)

    def test_incidence_requires_every_sign_and_boundary_stratum(self) -> None:
        functions = ["g_alg"]
        rows = [
            incidence_row("negative", functions, (-1,)),
            incidence_row("positive", functions, (1,)),
        ]
        with self.assertRaisesRegex(AuditError, "enumerate every sign"):
            validate_incidence(
                {"status": "FROZEN", "records": rows},
                {"C.TEST": simple_carrier()},
                {"L.TEST": {
                    "carrier_id": "C.TEST",
                    "function_ids": functions,
                    "boundary_strata": ["INTERIOR"],
                }},
            )

    def test_selected_physical_aperture_tie_must_be_empty(self) -> None:
        functions = ["a_h", "a_alg"]
        rows = []
        counter = 0
        for first in (-1, 0, 1):
            for second in (-1, 0, 1):
                counter += 1
                if first == second == 0:
                    rows.append(incidence_row(
                        f"row-{counter}", functions, (first, second),
                        status="NONEMPTY", component_ids=["bad-tie"],
                        empty_margin_id=None, rank_certificate_id="rank-cert",
                    ))
                else:
                    rows.append(incidence_row(
                        f"row-{counter}", functions, (first, second)))
        with self.assertRaisesRegex(AuditError,
                                    "channel tie was declared nonempty"):
            validate_incidence(
                {"status": "FROZEN", "records": rows},
                {"C.TEST": simple_carrier()},
                {"L.TEST": {
                    "carrier_id": "C.TEST",
                    "function_ids": functions,
                    "boundary_strata": ["INTERIOR"],
                }},
            )

    def test_nonempty_q_tie_cannot_claim_an_empty_time_gap(self) -> None:
        functions = ["q_h"]
        rows = [
            incidence_row("negative", functions, (-1,)),
            incidence_row(
                "tie", functions, (0,), status="NONEMPTY",
                component_ids=["q-tie"], empty_margin_id="false-gap",
                rank_certificate_id="rank-cert", declared_tie=True),
            incidence_row("positive", functions, (1,)),
        ]
        with self.assertRaisesRegex(AuditError, "claims an empty gap"):
            validate_incidence(
                {"status": "FROZEN", "records": rows},
                {"C.TEST": simple_carrier()},
                {"L.TEST": {
                    "carrier_id": "C.TEST",
                    "function_ids": functions,
                    "boundary_strata": ["INTERIOR"],
                }},
            )

    def test_priority_cannot_erase_simultaneous_active_faces(self) -> None:
        components = {"component": ("row", {"g_alg", "h_side_alg"})}
        section = {"status": "FROZEN", "records": [{
            "id": "priority",
            "component_id": "component",
            "active_function_ids": ["g_alg"],
            "outcome": "alg",
            "priority_witness_function_id": "g_alg",
            "selected_physical_event_function_id": "g_alg",
            "preserves_full_active_set": True,
            "frozen": True,
        }]}
        with self.assertRaisesRegex(AuditError,
                                    "erases simultaneous incidence"):
            validate_priority(section, {"row": {"status": "NONEMPTY"}},
                              components)

    def test_return_time_tie_selects_return_not_lateral(self) -> None:
        components = {"return-tie": ("row", {"q_ret"})}
        section = {"status": "FROZEN", "records": [{
            "id": "priority",
            "component_id": "return-tie",
            "active_function_ids": ["q_ret"],
            "outcome": "lat",
            "priority_witness_function_id": "q_ret",
            "selected_physical_event_function_id": "a_ret",
            "preserves_full_active_set": True,
            "frozen": True,
        }]}
        with self.assertRaisesRegex(AuditError,
                                    "bound physical terminal"):
            validate_priority(section, {"row": {"status": "NONEMPTY"}},
                              components)

    def test_first_event_census_cannot_leave_a_residual_component(self) -> None:
        components = {
            "component-a": ("row-a", {"g_alg"}),
            "component-b": ("row-b", {"g_pole"}),
        }
        section = {
            "status": "FROZEN",
            "records": [{
                "id": "census-a",
                "component_id": "component-a",
                "list_id": "L.TEST",
                "outcome": "alg",
                "first_event_function_id": "g_alg",
                "cell_complex_id": "complex-a",
                "frozen": True,
            }],
            "cell_complexes": [],
            "exhaustion": None,
        }
        incidence = {
            "row-a": {"list_id": "L.TEST"},
            "row-b": {"list_id": "L.TEST"},
        }
        with self.assertRaisesRegex(AuditError, "residual or duplicated"):
            validate_census(section, {"L.TEST": {}}, incidence,
                            components, {})

    def test_normalization_scales_must_be_exact_and_positive(self) -> None:
        carriers = {"C.TEST": {"coordinates": ["x"]}}
        functions = {"g_alg": {}}
        section = {
            "status": "FROZEN",
            "carrier_metrics": [{
                "carrier_id": "C.TEST",
                "metric": "EUCLIDEAN_AFTER_AFFINE_SCALING",
                "coordinate_scales": {"x": "1"},
                "frozen": True,
            }],
            "function_scales": [{
                "function_id": "g_alg", "scale": "0", "frozen": True,
            }],
            "time_scales": [{
                "carrier_id": "C.TEST", "scale": "1", "frozen": True,
            }],
            "phase_scale": "1",
        }
        with self.assertRaisesRegex(AuditError, "not strictly positive"):
            validate_normalization(section, carriers, functions)

    def test_m0_cannot_use_a_false_gap_at_a_nonempty_time_tie(self) -> None:
        section = {
            "status": "FROZEN",
            "value": "1/10",
            "definition": "MINIMUM_OF_FROZEN_DIMENSIONLESS_CERTIFIED_LOWERS",
            "margin_lowers": [{
                "id": f"margin-{category.lower()}",
                "category": category,
                "status": "PRESENT",
                "lower": "1",
                "normalized": True,
                "certificate_id": f"cert-{category.lower()}",
            } for category in sorted(REQUIRED_MARGINS)],
            "bridge_half_bound": "1/20",
            "simultaneous_tie_policy": {
                "nonempty_ties_use_conormal_rank_not_time_gap": False,
                "empty_ties_require_absolute_q_lower": True,
                "excluded_component_ids": ["tie-component"],
            },
        }
        components = {"tie-component": ("row", {"q_h"})}
        with self.assertRaisesRegex(AuditError, "false gap"):
            validate_m0(section, components)

    def test_numerical_method_cannot_change_locked_precision(self) -> None:
        carriers = {"C.TEST": {"coordinate_domain": {"x": ["-1", "1"]}}}
        section = {
            "status": "FROZEN",
            "carrier_domains": [{
                "carrier_id": "C.TEST",
                "coordinate_domain": {"x": ["-1", "1"]},
                "frozen": True,
            }],
            "state_partition": {
                "initial_box_counts": {"C.TEST": 1},
                "max_bisection_depths": {"C.TEST": 1},
                "unresolved_box_verdict": "INCONCLUSIVE",
                "adaptation_after_output_forbidden": True,
            },
            "ode_taylor_order": 20,
            "precision": {
                "backend": "FILIB",
                "format": "IEEE_754_BINARY64",
                "significand_bits": 64,
                "multiprecision": False,
                "source": "validation/rigorous/dependency.lock.json",
            },
            "high_winding_N_policy":
                "NOT_A_P2E_V2_4_5_MATERIALIZATION_CHOICE",
            "legacy_ambiguous_fields_forbidden": ["D", "N", "precision"],
        }
        with self.assertRaisesRegex(AuditError, "locked FILIB"):
            validate_numerical_method(section, carriers)

    def test_ready_gate_only_authorizes_the_first_run_not_a_claim(self) -> None:
        gate = base_config()["full_run_gate"]
        gate.update({
            "status": "READY_FOR_FIRST_FULL_RUN",
            "frozen_before_first_full_run": True,
            "materialization_commit": "0" * 40,
            "authorized_binary_sha256": "0" * 64,
        })
        self.assertTrue(validate_full_run_gate(gate, ready=True))


if __name__ == "__main__":
    unittest.main()
