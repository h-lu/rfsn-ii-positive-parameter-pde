#!/usr/bin/env python3
"""Check the proof-bound finite overlaps of the P2d saddle chart."""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[1]
sys.path.insert(0, str(HERE))

import check_p2d_physical_slides as physical  # noqa: E402


SCHEMA_VERSION = "rfsn-vdp-p2d-chart-overlaps-check/1"
SCOPE = "V2_CHART_OVERLAPS_LOCAL_PROOF_BOUND_GATES"
PROOF_CONTRACT = "rfsn-vdp-p2d-explicit-finite-chart-overlaps/1"
PROOF_RELATIVE = "theory/EXPLICIT_FINITE_CHART_OVERLAPS.md"
PROOF_PATH = REPOSITORY / PROOF_RELATIVE
PROOF_SHA256 = (
    "4afe3faa733eb20bac87978bbaaa8bd746248fd90e52d195c9d1ee4cc551d918"
)

CONFIG_RELATIVE = "validation/rigorous/config/vdp_p2d_overlaps_v1.json"
CONFIG_PATH = REPOSITORY / CONFIG_RELATIVE
CONFIG_SHA256 = (
    "698f5979f021e3702fd733169d71178fd06fd103647dff1a2bf87456edad407a"
)

P2B_CONFIG_RELATIVE = "validation/rigorous/config/vdp_p2_jets_v1.json"
P2B_CONFIG_PATH = REPOSITORY / P2B_CONFIG_RELATIVE
P2B_CONFIG_SHA256 = (
    "b8123dff51f7444277f71b1b8a5b0cdbbc94df46a848af05e8288751bb6681e0"
)
KATO_CONFIG_RELATIVE = "validation/rigorous/config/vdp_p2_kato_v1.json"
KATO_CONFIG_PATH = REPOSITORY / KATO_CONFIG_RELATIVE
KATO_CONFIG_SHA256 = (
    "676de23609a66b9a6fa35d2cc476878018bc84b4615460719f9c2f87eb1823e3"
)

EXPECTED_SOURCE_BINDINGS = {
    physical.MOSER_RELATIVE: physical.MOSER_SHA256,
    physical.PROOF_RELATIVE: physical.PROOF_SHA256,
    P2B_CONFIG_RELATIVE: P2B_CONFIG_SHA256,
    physical.CONFIG_RELATIVE: physical.CONFIG_SHA256,
    KATO_CONFIG_RELATIVE: KATO_CONFIG_SHA256,
    physical.P2B_JETS_RELATIVE: physical.P2B_JETS_SHA256,
    physical.KATO_RELATIVE: physical.KATO_SHA256,
}

FIRST_SIX_CHILDREN = (
    "V2.CHART.SYMPLECTIC_FRAME",
    "V2.CHART.ANALYTIC_NORMAL_FORM",
    "V2.CHART.ZERO_ENERGY",
    "V2.CHART.EXACT_SECTIONS",
    "V2.CHART.WEIGHTED_PASSAGE",
    "V2.CHART.PHYSICAL_SLIDES",
)
KATO_SEAM_FACTS = (
    "C_AK_conformal_gram_identity",
    "C_AK_determinant_is_sigma_squared",
    "C_AK_orientation_is_positive",
    "C_AK_positive_radial_rotation_factorization",
    "R_chi_is_special_orthogonal",
    "same_graph_boundary_normalized_C_AK_direction",
    "source_phase_degree_plus_one",
    "source_phase_derivative_J0_identity",
)

EXPECTED_K = (46518441, 93036891, 279110683)
EXPECTED_ELL = (279120125, 837360385, 2791201291)


class ChartOverlapsCheckError(ValueError):
    """A source binding, finite-cover datum, or exact gate is malformed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ChartOverlapsCheckError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def canonical_json(value: Any) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":")) + "\n"


def rational(value: Fraction | int) -> dict[str, str]:
    value = Fraction(value)
    return {
        "numerator": str(value.numerator),
        "denominator": str(value.denominator),
    }


def as_fraction(record: Any, label: str) -> Fraction:
    require(isinstance(record, dict), f"{label} is not a rational record")
    try:
        return Fraction(int(record["numerator"]), int(record["denominator"]))
    except (KeyError, TypeError, ValueError, ZeroDivisionError) as error:
        raise ChartOverlapsCheckError(
            f"{label} is not a valid rational record: {error}"
        ) from error


def _load_bound_json(
    path: Path, expected_sha256: str, relative: str
) -> tuple[dict[str, Any], str]:
    source = path.read_bytes()
    digest = sha256_bytes(source)
    require(digest == expected_sha256, f"frozen source changed: {relative}")
    value = json.loads(source)
    require(isinstance(value, dict), f"{relative} is not a JSON object")
    return value, digest


def proof_binding(path: Path = PROOF_PATH) -> dict[str, Any]:
    source = path.read_bytes()
    digest = sha256_bytes(source)
    text = source.decode("utf-8")
    contract_present = PROOF_CONTRACT in text
    return {
        "path": PROOF_RELATIVE,
        "expected_sha256": PROOF_SHA256,
        "observed_sha256": digest,
        "proof_contract": PROOF_CONTRACT,
        "proof_contract_present": contract_present,
        "matched": digest == PROOF_SHA256 and contract_present,
    }


def _obligation(certificate: dict[str, Any], identifier: str) -> None:
    matches = [
        item
        for item in certificate.get("obligations", [])
        if isinstance(item, dict) and item.get("id") == identifier
    ]
    require(len(matches) == 1, f"obligation {identifier} is not unique")
    require(matches[0].get("status") == "PASS", f"{identifier} is not PASS")


def authenticate_physical_report(report: dict[str, Any]) -> dict[str, Any]:
    require(isinstance(report, dict), "physical-slides report is missing")
    require(report.get("schema_version") == physical.SCHEMA_VERSION,
            "physical-slides checker schema changed")
    require(report.get("scope") == physical.SCOPE,
            "physical-slides checker scope changed")
    require(report.get("status") in {"PASS", "INCONCLUSIVE", "FAIL"},
            "physical-slides status is malformed")
    require(report.get("claim_bearing") is False,
            "physical-slides prerequisite became claim-bearing")

    source = report.get("source_authentication", {})
    require(isinstance(source, dict), "physical source authentication is missing")
    for relative, digest in (
        (physical.P2B_JETS_RELATIVE, physical.P2B_JETS_SHA256),
        (physical.KATO_RELATIVE, physical.KATO_SHA256),
        (physical.MOSER_RELATIVE, physical.MOSER_SHA256),
        (physical.CONFIG_RELATIVE, physical.CONFIG_SHA256),
    ):
        require(source.get(relative) == digest,
                f"physical prerequisite binding changed: {relative}")

    statuses = report.get("local_chart_status", {})
    require(isinstance(statuses, dict), "physical local-chart table is missing")
    for child in FIRST_SIX_CHILDREN:
        require(statuses.get(child) in {"PASS", "OPEN"},
                f"physical child status is malformed: {child}")
    require(statuses.get("V2.CHART.OVERLAPS") == "OPEN",
            "physical prerequisite changed the overlap boundary")
    require(statuses.get("V2.EXACT_CHART") == "OPEN",
            "physical prerequisite changed the parent boundary")

    exact = report.get("exact_values", {})
    checks = exact.get("checks", {})
    require(isinstance(checks, dict) and checks,
            "physical exact checks are missing")
    rectangle = exact.get("mixed_jet_bounds", {})
    normalized = rectangle.get("normalized_4_by_3_rectangle", {})
    original = rectangle.get("original_parameter_rectangle", {})
    require(set(normalized) == {
        "state_order_0", "state_order_1", "state_order_2", "state_order_3"
    } and all(isinstance(row, list) and len(row) == 3
              for row in normalized.values()),
            "physical normalized 4 by 3 rectangle is incomplete")
    require(isinstance(original, dict) and "D_r_r" in original and
            len(original["D_r_r"]) == 4,
            "physical original-parameter rectangle is incomplete")

    binding = report.get("proof_binding", {})
    local_pass = (
        report.get("status") == "PASS"
        and report.get("mathematical_status") == "LOCAL_MATHEMATICAL_PASS"
        and binding.get("matched") is True
        and all(statuses.get(child) == "PASS" for child in FIRST_SIX_CHILDREN)
        and all(value is True for value in checks.values())
    )
    return {
        "local_pass": local_pass,
        "source_gate_status": report.get("source_gate_status"),
        "proof_sha256": binding.get("observed_sha256"),
        "normalized_rectangle": normalized,
        "original_rectangle": original,
        "constants": exact.get("constants", {}),
        "terminal_frame_budget": exact.get("terminal_frame_budget", {}),
    }


def authenticate_sources(config_path: Path = CONFIG_PATH) -> dict[str, Any]:
    config, config_digest = _load_bound_json(
        config_path, CONFIG_SHA256, CONFIG_RELATIVE
    )
    require(config.get("schema_version") ==
            "rfsn-vdp-p2d-overlaps-config/1",
            "overlap configuration schema changed")
    require(config.get("configuration_id") == "vdp-p2d-overlaps-v1",
            "overlap configuration id changed")
    require(config.get("status") == "FROZEN_PROOF_BOUND",
            "overlap configuration is not proof-bound")
    bindings = config.get("source_bindings")
    require(bindings == EXPECTED_SOURCE_BINDINGS,
            "overlap source-binding table changed")
    for relative, expected in EXPECTED_SOURCE_BINDINGS.items():
        require(sha256_bytes((REPOSITORY / relative).read_bytes()) == expected,
                f"overlap source binding no longer matches: {relative}")

    p2b_config, _ = _load_bound_json(
        P2B_CONFIG_PATH, P2B_CONFIG_SHA256, P2B_CONFIG_RELATIVE
    )
    kato_config, _ = _load_bound_json(
        KATO_CONFIG_PATH, KATO_CONFIG_SHA256, KATO_CONFIG_RELATIVE
    )
    p2b, _ = _load_bound_json(
        physical.P2B_JETS_PATH,
        physical.P2B_JETS_SHA256,
        physical.P2B_JETS_RELATIVE,
    )
    kato, _ = _load_bound_json(
        physical.KATO_PATH, physical.KATO_SHA256, physical.KATO_RELATIVE
    )
    require(p2b.get("scope") == "V2_P2_JETS_KERNEL" and
            p2b.get("integrity_status") == "PASS" and
            p2b.get("mathematical_status") == "PASS",
            "P2b mixed-jet certificate is not a local mathematical PASS")
    require(kato.get("scope") == "V2_P2_KATO_KERNEL" and
            kato.get("integrity_status") == "PASS" and
            kato.get("mathematical_status") == "PASS",
            "P2bK certificate is not a local mathematical PASS")
    require(p2b.get("p2_jets_configuration", {}).get("sha256") ==
            P2B_CONFIG_SHA256,
            "P2b certificate/configuration binding changed")
    require(kato.get("p2_kato_configuration", {}).get("sha256") ==
            KATO_CONFIG_SHA256,
            "P2bK certificate/configuration binding changed")
    _obligation(p2b, "V2.WU.JETS")
    _obligation(kato, "V2.PHASE.KATO_INTERFACE")

    graph_gate = as_fraction(
        p2b_config.get("coordinate_domain", {}).get(
            "true_graph_first_derivative_upper"
        ),
        "P2b true-graph first-derivative gate",
    )
    require(graph_gate < 1, "the authenticated P2b graph DH gate is not < 1")

    source_circle = kato_config.get("source_circle_contract", {})
    require(source_circle.get("phase_degree") == 1,
            "the Kato source phase does not have degree +1")
    require(source_circle.get("require_same_p2b_true_graph_disk") is True,
            "the Kato source is not bound to the P2b graph disk")
    require(source_circle.get("phase_lift_formula") ==
            "phi_algebraic=phi+chi(c(theta))",
            "the Kato source phase-lift formula changed")
    audit = kato.get("kato_exact_algebra_audit", {})
    audit_checks = audit.get("checks", {})
    require(audit.get("status") == "PASS" and
            all(audit_checks.get(name) is True for name in KATO_SEAM_FACTS),
            "the Kato SO(2)/orientation/degree facts are incomplete")

    return {
        "config": config,
        "config_sha256": config_digest,
        "p2b_graph_DH_upper": graph_gate,
        "kato_seam_facts": {name: True for name in KATO_SEAM_FACTS},
    }


def _cover_bounds(member: dict[str, Any], field: str) -> tuple[Fraction, Fraction]:
    record = member.get(field)
    require(isinstance(record, dict), f"cover member {field} is missing")
    return (
        as_fraction(record.get("lower"), f"{field}.lower"),
        as_fraction(record.get("upper"), f"{field}.upper"),
    )


def compute_cover(config: dict[str, Any]) -> dict[str, Any]:
    cover = config.get("normalized_parameter_cover", {})
    require(cover.get("coordinates") ==
            ["theta_r", "theta_a", "theta_epsilon"],
            "normalized overlap-coordinate order changed")
    ambient = cover.get("ambient_box", {})
    ambient_lower = as_fraction(ambient.get("lower"), "ambient lower")
    ambient_upper = as_fraction(ambient.get("upper"), "ambient upper")
    require((ambient_lower, ambient_upper) == (Fraction(-1), Fraction(1)),
            "normalized overlap ambient box changed")
    require(cover.get("relative_topology") is True,
            "overlap cover is not relative-open in the bridge")
    buffer = as_fraction(
        cover.get("relative_compact_containment_buffer"),
        "relative compact-containment buffer",
    )
    original_buffer = as_fraction(
        cover.get("original_r_compact_containment_buffer"),
        "original-r compact-containment buffer",
    )
    require(buffer == Fraction(1, 4) and original_buffer == buffer / 25,
            "overlap compact-containment collar changed")

    members = cover.get("members")
    require(isinstance(members, list) and len(members) == 2,
            "the overlap cover does not have exactly two members")
    by_id = {item.get("id"): item for item in members if isinstance(item, dict)}
    require(set(by_id) == {"anchor", "positive"},
            "overlap member ids changed")
    anchor_v = _cover_bounds(by_id["anchor"], "V_theta_r")
    anchor_u = _cover_bounds(by_id["anchor"], "U_theta_r")
    positive_v = _cover_bounds(by_id["positive"], "V_theta_r")
    positive_u = _cover_bounds(by_id["positive"], "U_theta_r")
    require(anchor_v == (-1, Fraction(1, 4)) and
            anchor_u == (-1, Fraction(1, 2)) and
            positive_v == (0, 1) and
            positive_u == (Fraction(-1, 4), 1),
            "the two-member cover endpoints changed")
    require(by_id["anchor"]["V_theta_r"].get("upper_closed") is True and
            by_id["anchor"]["U_theta_r"].get("upper_closed") is False and
            by_id["positive"]["V_theta_r"].get("lower_closed") is True and
            by_id["positive"]["U_theta_r"].get("lower_closed") is False,
            "relative-open/closed face flags changed")

    checks = {
        "two_relative_open_members": True,
        "anchor_and_positive_members_cover_bridge": (
            anchor_v[0] == ambient_lower
            and positive_v[1] == ambient_upper
            and anchor_v[1] >= positive_v[0]
        ),
        "anchor_compactly_contained": anchor_u[1] - anchor_v[1] == buffer,
        "positive_compactly_contained": positive_v[0] - positive_u[0] == buffer,
        "genuine_closed_overlap": (
            min(anchor_v[1], positive_v[1])
            - max(anchor_v[0], positive_v[0]) == Fraction(1, 4)
        ),
        "normalized_to_original_r_collar": original_buffer == buffer / 25,
    }
    return {
        "coordinates": cover["coordinates"],
        "ambient_theta_interval": {
            "lower": rational(ambient_lower), "upper": rational(ambient_upper)
        },
        "relative_topology": True,
        "member_count": 2,
        "members": {
            "anchor": {
                "V_theta_r": [rational(anchor_v[0]), rational(anchor_v[1])],
                "U_theta_r": [rational(anchor_u[0]), rational(anchor_u[1])],
            },
            "positive": {
                "V_theta_r": [rational(positive_v[0]), rational(positive_v[1])],
                "U_theta_r": [rational(positive_u[0]), rational(positive_u[1])],
            },
        },
        "relative_compact_containment_buffer": rational(buffer),
        "original_r_compact_containment_buffer": rational(original_buffer),
        "closed_overlap_theta_r": {
            "lower": rational(0), "upper": rational(Fraction(1, 4))
        },
        "checks": checks,
    }


def compute_common_chart(config: dict[str, Any], physical_info: dict[str, Any]) -> dict[str, Any]:
    chart = config.get("common_chart", {})
    epsilon = as_fraction(chart.get("epsilon_nf"), "epsilon_nf")
    source_radius = as_fraction(
        chart.get("source_polydisc_radius"), "source polydisc radius"
    )
    inverse_radius = as_fraction(
        chart.get("inverse_polydisc_radius"), "inverse polydisc radius"
    )
    target_radius = as_fraction(
        chart.get("physical_target_polydisc_radius"),
        "physical target polydisc radius",
    )
    require(epsilon == Fraction(1, 2**22), "epsilon_nf changed")
    require(source_radius == 3 * epsilon / 8 and
            inverse_radius == epsilon / 2 and
            target_radius == epsilon / 8,
            "common chart/inverse domain radii changed")
    require(chart.get("family_formula") ==
            "Phi_mu_K=L_mu composed with Theta_mu_R" and
            chart.get("inverse_formula") ==
            "Psi_mu_R composed with inverse(L_mu)",
            "the global chart or inverse formula changed")
    require(chart.get(
        "all_cover_members_are_restrictions_of_one_normalized_family"
    ) is True, "cover members are not restrictions of one normalized chart")
    require(chart.get("primitive_gauge") == "f_mu with f_mu(0)=0" and
            chart.get("cover_overlap_transition") == "identity" and
            chart.get("cover_overlap_inverse") == "identity",
            "identity transition/inverse or primitive gauge changed")

    markings = config.get("section_markings", {})
    constants = physical_info["constants"]
    auxiliary_radius = as_fraction(
        markings.get("auxiliary_radius"), "auxiliary radius"
    )
    physical_radius = as_fraction(
        markings.get("physical_radius"), "physical radius"
    )
    action_collar = as_fraction(markings.get("action_collar"), "action collar")
    require(auxiliary_radius == as_fraction(
        constants.get("section_radius_rho"), "physical prerequisite rho"
    ), "overlap auxiliary radius differs from physical slides")
    require(physical_radius == as_fraction(
        constants.get("physical_face_radius"), "physical prerequisite radius"
    ), "overlap physical radius differs from physical slides")
    require(action_collar == as_fraction(
        constants.get("weighted_radius_nu_p"), "physical prerequisite nu_p"
    ), "overlap action collar differs from physical slides")
    require(markings.get("transported_slide_coordinate_transition") ==
            "(phase,nu)->(phase,nu)" and
            markings.get("transported_slide_coordinate_inverse") ==
            "(phase,nu)->(phase,nu)",
            "transported slide coordinates are not identity markings")
    require(markings.get(
        "seam_is_not_assumed_to_be_a_constant_phase_translation"
    ) is True, "the physical source seam was collapsed to a phase translation")
    require(markings.get("physical_source_seam_inverse") ==
            "lambda_mu=kappa_mu^(-1)",
            "the physical source seam inverse changed")

    return {
        "family": "one_global_normalized_family_restricted_to_two_members",
        "formula": chart["family_formula"],
        "inverse_formula": chart["inverse_formula"],
        "epsilon_nf": rational(epsilon),
        "source_polydisc_radius": rational(source_radius),
        "inverse_polydisc_radius": rational(inverse_radius),
        "physical_target_polydisc_radius": rational(target_radius),
        "transition": "identity",
        "inverse_transition": "identity",
        "primitive_gauge_difference": rational(0),
        "signed_axes_preserved": True,
        "auxiliary_radius": rational(auxiliary_radius),
        "physical_radius": rational(physical_radius),
        "action_collar": rational(action_collar),
        "transported_slide_transition": "identity",
        "checks": {
            "common_chart_and_inverse_domains": True,
            "one_normalized_family_not_independent_cell_charts": True,
            "identity_transition_and_inverse": True,
            "fixed_zero_normalized_primitive_gauge": True,
            "signed_action_and_axes_preserved": True,
            "physical_slide_marking_is_identity_in_transported_coordinates": True,
        },
    }


def compute_identity_transition(config: dict[str, Any]) -> dict[str, Any]:
    regularity = config.get("regularity_contract", {})
    max_state = regularity.get("maximum_state_order")
    max_parameter = regularity.get("maximum_external_parameter_order")
    first_norm = as_fraction(
        regularity.get("identity_transition_first_state_derivative_norm"),
        "identity first-state derivative norm",
    )
    require((max_state, max_parameter) == (3, 2) and
            regularity.get("full_rectangular_claim") is True,
            "identity transition does not claim the full 4 by 3 rectangle")
    require(regularity.get("full_rectangular_scope") ==
            "identity chart, oriented-blow-up, and transported-slide transitions only",
            "the full 4 by 3 rectangle escaped the identity-transition scope")
    require(first_norm == 1 and
            regularity.get("identity_transition_higher_state_derivatives") == 0 and
            regularity.get(
                "positive_mixed_derivatives_of_transition_displacement"
            ) == 0,
            "identity transition derivative contract changed")

    rectangle: dict[str, list[dict[str, Any]]] = {}
    for state_order in range(max_state + 1):
        row = []
        for parameter_order in range(max_parameter + 1):
            if (state_order, parameter_order) == (0, 0):
                map_derivative = "identity_map"
            elif (state_order, parameter_order) == (1, 0):
                map_derivative = "identity_linear_map_norm_1"
            else:
                map_derivative = "zero"
            row.append({
                "state_order": state_order,
                "parameter_order": parameter_order,
                "map_derivative": map_derivative,
                "transition_displacement_derivative_norm_upper": rational(0),
                "inverse_has_same_bound": True,
            })
        rectangle[f"state_order_{state_order}"] = row
    return {
        "oriented_real_blow_up_transition": "identity",
        "oriented_real_blow_up_inverse": "identity",
        "exact_symplectic": True,
        "primitive_coboundary": rational(0),
        "stable_axis_preserved": True,
        "unstable_axis_preserved": True,
        "signed_I2K_faces_preserved": True,
        "positive_Kato_boundary_degree": 1,
        "full_state3_by_parameter2_rectangle": rectangle,
        "rectangle_entry_count": 12,
        "checks": {
            "identity_extends_to_oriented_real_blow_up": True,
            "identity_and_inverse_are_exact_symplectic": True,
            "primitive_gauge_difference_is_zero": True,
            "full_4_by_3_rectangle_is_explicit": (
                sum(len(row) for row in rectangle.values()) == 12
            ),
            "all_transition_displacement_derivatives_vanish": all(
                as_fraction(item[
                    "transition_displacement_derivative_norm_upper"
                ], "identity displacement") == 0
                for row in rectangle.values() for item in row
            ),
        },
    }


def _forward_recurrence(K_v: int, maximum_order: int) -> tuple[int, ...]:
    require(maximum_order == 3, "forward seam order must be exactly three")
    values = [K_v + 1]
    for order in range(2, maximum_order + 1):
        values.append(7 + max(K_v, order * (1 + values[-1])))
    return tuple(values)


def _inverse_recurrence(k_top: int, maximum_order: int) -> tuple[int, ...]:
    require(maximum_order == 3, "inverse seam order must be exactly three")
    values = [9442 + k_top]
    for order in range(2, maximum_order + 1):
        values.append(9450 + k_top + order * (1 + values[-1]))
    return tuple(values)


def compute_boundary_seam(
    config: dict[str, Any],
    physical_info: dict[str, Any],
    source_info: dict[str, Any],
) -> dict[str, Any]:
    markings = config.get("section_markings", {})
    gates = config.get("physical_source_seam_gates", {})
    require(markings.get(
        "seam_is_not_assumed_to_be_a_constant_phase_translation"
    ) is True, "general seam was replaced by a constant translation")
    require(gates.get("mixed_total_order") == 3 and
            gates.get("maximum_parameter_order") == 2 and
            gates.get("full_rectangular_claim") is False,
            "the boundary seam regularity contract is not total-order three")
    require(gates.get("seam_scope") ==
            "source phase boundary only; mixed derivatives of total order at most three",
            "the seam was extended beyond its boundary-only scope")
    require(gates.get("boundary_degree") == 1,
            "physical source seam degree changed")

    endpoint_D1 = gates.get("endpoint_first_state_derivative_exponent")
    terminal_T = gates.get("terminal_frame_operator_exponent")
    lower_exponent = gates.get("phase_derivative_strict_lower_exponent")
    algebraic_exponent = gates.get("algebraic_endpoint_full_rectangle_exponent")
    K_v = gates.get("unit_vector_full_rectangle_exponent")
    require(all(isinstance(value, int) for value in (
        endpoint_D1, terminal_T, lower_exponent, algebraic_exponent, K_v
    )), "a seam exponent is not an integer")
    require((endpoint_D1, terminal_T, lower_exponent,
             algebraic_exponent, K_v) ==
            (9443, 3, -9441, 46518425, 46518440),
            "frozen physical-source seam exponents changed")

    normalized = physical_info["normalized_rectangle"]
    physical_D1 = normalized["state_order_1"][0]
    require(int(physical_D1["endpoint_power_of_two_exponent"]) == endpoint_D1,
            "physical endpoint first-state exponent changed")
    original_corner = physical_info["original_rectangle"]["D_r_r"][3]
    require(int(original_corner["endpoint_power_of_two_exponent"]) ==
            algebraic_exponent,
            "physical full-rectangle endpoint exponent changed")
    terminal = physical_info["terminal_frame_budget"]
    require(int(terminal.get("operator_power_of_two_exponent")) == terminal_T and
            all(terminal.get("checks", {}).values()),
            "terminal T_mu exponent/table changed")
    graph_gate = source_info["p2b_graph_DH_upper"]
    coarse_graph_bound = as_fraction(
        gates.get("unstable_graph_first_derivative_upper"),
        "coarse unstable-graph derivative upper",
    )
    require(graph_gate < coarse_graph_bound == 1,
            "P2b graph DH gate does not imply the coarse seam bound")
    require(K_v == algebraic_exponent + 15,
            "unit-vector exponent is not the proof's +15 composition budget")

    # 1=|omega(E_psi,E_nu)| and |E_nu|<2^9443 give
    # |E_psi|>2^-9443.  T<2^3 and DH<=1 cost one more factor two,
    # hence |u_psi|>2^-9447.  Division by R=1/100 gives the strict gate.
    derived_lower = Fraction(100, 2**9447)
    target_lower = Fraction(1, 2**9441)
    require(derived_lower > target_lower,
            "the quantitative seam derivative margin is not strict")

    forward_contract = gates.get("forward_phase_recurrence", {})
    inverse_contract = gates.get("inverse_phase_recurrence", {})
    require(forward_contract == {
        "k1_offset": 1,
        "higher_partition_offset": 7,
        "lift_displacement_offset": 4,
        "maximum_total_order": 3,
    }, "forward seam recurrence contract changed")
    require(inverse_contract == {
        "ell1_denominator_offset": 9442,
        "higher_denominator_and_partition_offset": 9450,
        "lift_displacement_offset": 4,
        "maximum_total_order": 3,
    }, "inverse seam recurrence contract changed")
    k_values = _forward_recurrence(K_v, 3)
    ell_values = _inverse_recurrence(k_values[-1], 3)
    require(k_values == EXPECTED_K, "forward seam recurrence changed")
    require(ell_values == EXPECTED_ELL, "inverse seam recurrence changed")

    colored = []
    excluded = []
    for phase_order in range(4):
        for parameter_order in range(3):
            total_order = phase_order + parameter_order
            slot = {
                "phase_order": phase_order,
                "parameter_order": parameter_order,
                "mixed_total_order": total_order,
            }
            if total_order > 3:
                excluded.append(slot)
                continue
            if total_order == 0:
                slot.update({
                    "quantity": "lift_displacement",
                    "forward_power_of_two_exponent": str(k_values[0] + 4),
                    "inverse_power_of_two_exponent": str(ell_values[0] + 4),
                })
            else:
                slot.update({
                    "quantity": "mixed_derivative",
                    "forward_power_of_two_exponent": str(
                        k_values[total_order - 1]
                    ),
                    "inverse_power_of_two_exponent": str(
                        ell_values[total_order - 1]
                    ),
                })
            colored.append(slot)

    return {
        "type": "general_orientation_preserving_circle_diffeomorphism",
        "definition": markings.get("physical_source_seam"),
        "inverse": markings.get("physical_source_seam_inverse"),
        "constant_phase_translation_assumed": False,
        "scope": gates["seam_scope"],
        "boundary_degree": 1,
        "inverse_boundary_degree": 1,
        "authenticated_P2b_graph_DH_upper": rational(graph_gate),
        "authenticated_Kato_SO2_and_degree_facts":
            source_info["kato_seam_facts"],
        "endpoint_first_state_derivative_exponent": str(endpoint_D1),
        "terminal_frame_operator_exponent": str(terminal_T),
        "phase_derivative_strict_lower": {
            "coefficient": "1",
            "power_of_two_exponent": str(lower_exponent),
            "derived_coefficient_before_normalization": "100",
            "derived_power_of_two_exponent": "-9447",
            "strict_integer_margin_after_common_scaling": "36",
        },
        "algebraic_endpoint_full_rectangle_exponent": str(algebraic_exponent),
        "unit_vector_full_rectangle_exponent_K_v": str(K_v),
        "forward_recurrence_k": [str(value) for value in k_values],
        "inverse_recurrence_ell": [str(value) for value in ell_values],
        "forward_lift_displacement_exponent": str(k_values[0] + 4),
        "inverse_lift_displacement_exponent": str(ell_values[0] + 4),
        "colored_mixed_total_order_3_triangle": colored,
        "colored_entry_count": len(colored),
        "excluded_nonadmissible_rectangle_slots": excluded,
        "full_state3_parameter2_rectangle_claimed_for_seam": False,
        "checks": {
            "seam_is_general_not_constant_translation": True,
            "P2b_graph_DH_gate_is_strictly_below_one": graph_gate < 1,
            "Kato_SO2_orientation_and_degree_facts_pass": True,
            "phase_derivative_is_strictly_above_2_pow_minus_9441": True,
            "K_v_matches_physical_endpoint_composition": True,
            "forward_recurrence_matches_proof": k_values == EXPECTED_K,
            "inverse_recurrence_matches_proof": ell_values == EXPECTED_ELL,
            "zero_order_displacement_offsets_are_plus_four": (
                colored[0]["forward_power_of_two_exponent"] ==
                str(k_values[0] + 4)
                and colored[0]["inverse_power_of_two_exponent"] ==
                str(ell_values[0] + 4)
            ),
            "only_colored_total_order_at_most_three_is_claimed": (
                len(colored) == 9
                and all(item["mixed_total_order"] <= 3 for item in colored)
                and {(item["phase_order"], item["parameter_order"])
                     for item in excluded} == {(2, 2), (3, 1), (3, 2)}
            ),
        },
    }


def compute_exact_bounds(
    config: dict[str, Any],
    physical_info: dict[str, Any],
    source_info: dict[str, Any],
) -> dict[str, Any]:
    return {
        "finite_cover": compute_cover(config),
        "common_chart_and_markings": compute_common_chart(config, physical_info),
        "identity_chart_and_blow_up_transition":
            compute_identity_transition(config),
        "boundary_source_phase_seam":
            compute_boundary_seam(config, physical_info, source_info),
    }


def _all_exact_checks(exact: dict[str, Any]) -> bool:
    return all(
        value is True
        for component in exact.values()
        for value in component.get("checks", {}).values()
    )


def build_report(
    proof_path: Path = PROOF_PATH,
    config_path: Path = CONFIG_PATH,
    physical_report: dict[str, Any] | None = None,
) -> dict[str, Any]:
    prerequisite = (
        physical.build_report() if physical_report is None else physical_report
    )
    physical_info = authenticate_physical_report(prerequisite)
    source_info = authenticate_sources(config_path)
    config = source_info["config"]
    binding = proof_binding(proof_path)
    exact = compute_exact_bounds(config, physical_info, source_info)
    exact_pass = _all_exact_checks(exact)
    prerequisite_pass = physical_info["local_pass"]
    local_atom_pass = exact_pass and prerequisite_pass and binding["matched"]

    chart_status = {
        child: ("PASS" if prerequisite_pass else "OPEN")
        for child in FIRST_SIX_CHILDREN
    }
    chart_status["V2.CHART.OVERLAPS"] = (
        "PASS" if local_atom_pass else "OPEN"
    )
    chart_status["V2.EXACT_CHART"] = (
        "PASS" if local_atom_pass and
        all(chart_status.get(child) == "PASS" for child in FIRST_SIX_CHILDREN)
        else "OPEN"
    )

    claim_boundary = config.get("claim_boundary", {})
    require(claim_boundary == {
        "V2.CHART.OVERLAPS": "LOCAL_PASS_IF_PROOF_BINDING_MATCHES",
        "V2.EXACT_CHART": "LOCAL_PASS_IF_ALL_SEVEN_CHILDREN_PASS",
        "V2.EVENT_ATLAS": "OPEN",
        "independent_replay": "1/2",
        "claim_bearing": False,
        "release_eligible": False,
    }, "overlap claim boundary changed")

    return {
        "schema_version": SCHEMA_VERSION,
        "scope": SCOPE,
        "status": (
            "PASS" if local_atom_pass else
            "INCONCLUSIVE" if exact_pass else "FAIL"
        ),
        "source_gate_status": "PASS" if exact_pass else "FAIL",
        "mathematical_status": (
            "LOCAL_MATHEMATICAL_PASS" if local_atom_pass else
            "INCONCLUSIVE" if exact_pass else "FAIL"
        ),
        "mathematical_pass_scope": (
            "LOCAL_OVERLAPS_ATOM_AND_V2_EXACT_CHART_PARENT"
            if local_atom_pass else "NONE"
        ),
        "claim_bearing": False,
        "release_eligible": False,
        "independent_replay": "1/2",
        "source_authentication": {
            "physical_checker_schema": prerequisite.get("schema_version"),
            "physical_status": prerequisite.get("status"),
            "physical_local_pass": prerequisite_pass,
            "physical_proof_sha256": physical_info["proof_sha256"],
            "overlap_configuration_sha256": source_info["config_sha256"],
            "frozen_source_bindings": EXPECTED_SOURCE_BINDINGS,
            "P2b_graph_DH_gate_authenticated": True,
            "Kato_SO2_and_degree_facts_authenticated": True,
        },
        "proof_binding": binding,
        "exact_values": exact,
        "local_chart_status": chart_status,
        "claim_boundary": {
            "local_child_and_parent_only": True,
            "claim_bearing": False,
            "release_eligible": False,
            "independent_replay": "1/2",
            "V2_EVENT_ATLAS_P2e": "OPEN",
            "T2G_GLOBAL_CUT_AND_ALPHABET": "OPEN",
            "later_positive_end_validation": "OPEN",
            "temporal_stability_Turing_selection_canard": "OPEN",
        },
    }


def emit(value: dict[str, Any]) -> None:
    sys.stdout.write(canonical_json(value))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proof", type=Path, default=PROOF_PATH)
    parser.add_argument("--configuration", type=Path, default=CONFIG_PATH)
    arguments = parser.parse_args(argv)
    try:
        report = build_report(
            arguments.proof.resolve(), arguments.configuration.resolve()
        )
    except (
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        ChartOverlapsCheckError,
        physical.PhysicalSlidesCheckError,
        physical.weighted.WeightedPassageCheckError,
        physical.weighted.exact_sections.ExactSectionsCheckError,
        physical.weighted.zero_energy.ZeroEnergyCheckError,
        physical.weighted.zero_energy.normal_form.SourceCheckError,
        physical.weighted.zero_energy.normal_form.scout.ScoutInputError,
        subprocess.SubprocessError,
        KeyError,
        TypeError,
    ) as error:
        emit({
            "schema_version": SCHEMA_VERSION,
            "scope": SCOPE,
            "status": "INPUT_REJECTED",
            "mathematical_status": "INCONCLUSIVE",
            "error": str(error),
            "claim_bearing": False,
            "local_chart_status": {
                "V2.CHART.OVERLAPS": "OPEN",
                "V2.EXACT_CHART": "OPEN",
            },
            "claim_boundary": {
                "V2_EVENT_ATLAS_P2e": "OPEN",
                "T2G_GLOBAL_CUT_AND_ALPHABET": "OPEN",
            },
        })
        return 2
    emit(report)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    sys.exit(main())
