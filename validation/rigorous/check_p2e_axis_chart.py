#!/usr/bin/env python3
"""Check the direct P2e zero-action true-source chart.

This is a small proof-bound checker.  It authenticates the existing P2b0 and
P2bK certificates, verifies the exact chart algebra and rational phase-sector
gates, and binds the application-owned compactness criterion.  It performs no
ODE integration and does not pass the P2e event atlas.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any


HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[1]
sys.path.insert(0, str(HERE))

import check_certificate as historical  # noqa: E402


SCHEMA_VERSION = "rfsn-vdp-p2e-axis-source-chart-check/1"
SCOPE = "P2E_ZERO_ACTION_TRUE_SOURCE_CHART_AND_THICKENING_CRITERION"

PROOF_CONTRACT = "rfsn-vdp-p2e-axis-source-chart/1"
PROOF_RELATIVE = "theory/P2E_AXIS_SOURCE_CHART.md"
PROOF_PATH = REPOSITORY / PROOF_RELATIVE
PROOF_SHA256 = (
    "1e95cee5dc9fbc4341285912c767cd97"
    "a39bc9cd64bb4f0e6c74227725064f01"
)

P2B0_RELATIVE = (
    "validation/rigorous/results/vdp_bridge_v1_p2b_h10_c01.json"
)
P2B0_PATH = REPOSITORY / P2B0_RELATIVE
P2B0_SHA256 = (
    "91c1762329a9e19e8db69052f9397532"
    "512d8031f361f0b6eeb43edbeda5d5ac"
)
P2BK_RELATIVE = "validation/rigorous/results/vdp_bridge_v1_p2b_kato.json"
P2BK_PATH = REPOSITORY / P2BK_RELATIVE
P2BK_SHA256 = (
    "c67cce575caa396eba5b4388e8ba9a0c"
    "9d73fd702f69911d64c878f57f27bff3"
)

H10_CONFIG_RELATIVE = "validation/rigorous/config/vdp_p2_h10_c01_v1.json"
H10_CONFIG_PATH = REPOSITORY / H10_CONFIG_RELATIVE
H10_CONFIG_SHA256 = (
    "d09cf22c5ce382e31d2388a86b87a493"
    "01840cdd8698bf92135b9667d387ca96"
)
KATO_CONFIG_RELATIVE = "validation/rigorous/config/vdp_p2_kato_v1.json"
KATO_CONFIG_PATH = REPOSITORY / KATO_CONFIG_RELATIVE
KATO_CONFIG_SHA256 = (
    "676de23609a66b9a6fa35d2cc4768780"
    "18bc84b4615460719f9c2f87eb1823e3"
)
V2_BRIDGE_RELATIVE = "validation/rigorous/config/vdp_bridge_v2.json"
V2_BRIDGE_PATH = REPOSITORY / V2_BRIDGE_RELATIVE
V2_BRIDGE_SHA256 = (
    "ee45e35157075805f89e12d9eb89a82"
    "e9203167d22109d4f2b9e83ee2bd12de9"
)

P2B0_ATOMS = (
    "P2.H10_CENTER_EXACT",
    "V2.WU.H10_C0_TUBE",
)
P2BK_ATOMS = (
    "P2.KATO.EXACT_ALGEBRA",
    "P2.KATO.SOURCE_PARAMETERIZATION",
    "V2.PHASE.TRUE_SOURCE",
    "V2.PHASE.KATO_INTERFACE",
)
KATO_EXACT_CHECKS = (
    "coordinate_direction_is_phi_plus_chi",
    "source_coordinate_fixed_radius",
    "source_phase_degree_plus_one",
)

SOURCE_RADIUS = Fraction(1, 100)
GRAPH_TUBE_RADIUS = Fraction(1, 200000)
ETA_CHART_RADIUS = Fraction(1, 100000)
PHASE_SHIFT_BOUND = Fraction(1, 80)
ALPHA_BETA_LOWER = Fraction(699, 1000)
THETA_LOWER = Fraction(57, 10)
THETA_UPPER = Fraction(13, 2)
TWO_PI_LOWER = Fraction(103993, 16551)
TWO_PI_UPPER = Fraction(208696, 33215)
THETA_DEVIATION = Fraction(7, 12)
TOTAL_ANGLE_BOUND = Fraction(143, 240)
ANGLE_GATE = Fraction(3, 5)
COSINE_LOWER = Fraction(41, 50)
U1_LOWER = Fraction(41, 5000)
ACTION_DESIGN_CEILING = Fraction(1, 2**55)


class AxisChartCheckError(ValueError):
    """A proof binding, prerequisite, or exact source gate failed closed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AxisChartCheckError(message)


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


def as_fraction(value: Any, label: str) -> Fraction:
    require(isinstance(value, dict), f"{label} is not a rational record")
    try:
        return Fraction(int(value["numerator"]), int(value["denominator"]))
    except (KeyError, TypeError, ValueError, ZeroDivisionError) as error:
        raise AxisChartCheckError(f"{label} is malformed: {error}") from error


def load_bound_json(
    path: Path,
    expected_sha256: str,
    label: str,
) -> tuple[dict[str, Any], str]:
    try:
        source = path.read_bytes()
        value = json.loads(source)
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise AxisChartCheckError(f"cannot read {label}: {error}") from error
    digest = sha256_bytes(source)
    require(digest == expected_sha256, f"{label} source hash changed")
    require(isinstance(value, dict), f"{label} is not a JSON object")
    return value, digest


def source_binding(
    certificate: dict[str, Any],
    relative: str,
    expected_sha256: str,
    label: str,
) -> None:
    matches = [
        item for item in certificate.get("source_bindings", [])
        if isinstance(item, dict) and item.get("path") == relative
    ]
    require(len(matches) == 1, f"{label} does not uniquely bind {relative}")
    require(matches[0].get("sha256") == expected_sha256,
            f"{label} recorded the wrong hash for {relative}")


def obligation_statuses(certificate: dict[str, Any], label: str) -> dict[str, str]:
    result: dict[str, str] = {}
    for item in certificate.get("obligations", []):
        require(isinstance(item, dict), f"{label} has a malformed obligation")
        identifier = item.get("id")
        status = item.get("status")
        require(isinstance(identifier, str) and isinstance(status, str),
                f"{label} has an unlabelled obligation")
        require(identifier not in result,
                f"{label} duplicates obligation {identifier}")
        result[identifier] = status
    return result


def authenticate_certificate(
    path: Path,
    expected_sha256: str,
    scope: str,
    required_atoms: tuple[str, ...],
    label: str,
) -> tuple[dict[str, Any], str]:
    certificate, digest = load_bound_json(path, expected_sha256, label)
    errors = historical.check_certificate(path, REPOSITORY)
    require(not errors, f"{label} failed semantic authentication: {'; '.join(errors)}")
    require(certificate.get("scope") == scope, f"{label} scope changed")
    require(certificate.get("integrity_status") == "PASS",
            f"{label} integrity is not PASS")
    require(certificate.get("mathematical_status") == "PASS",
            f"{label} mathematical status is not PASS")
    require(certificate.get("final_status") == "INCONCLUSIVE",
            f"{label} replay boundary changed")
    require(certificate.get("claim_bearing") is False,
            f"{label} unexpectedly became claim-bearing")
    replay = certificate.get("independent_replay", {})
    require(replay == {
        "observed_distinct_machines": 1,
        "required_distinct_machines": 2,
        "status": "PENDING_REQUIRED",
    }, f"{label} independent-replay record changed")
    statuses = obligation_statuses(certificate, label)
    for atom in required_atoms:
        require(statuses.get(atom) == "PASS", f"{label} atom {atom} is not PASS")
    return certificate, digest


def exact_variables(record: dict[str, Any], label: str) -> dict[str, tuple[Fraction, Fraction]]:
    raw = record.get("variables")
    require(isinstance(raw, dict) and set(raw) == {"r", "a2", "epsilon"},
            f"{label} variables changed")
    result: dict[str, tuple[Fraction, Fraction]] = {}
    for name in ("r", "a2", "epsilon"):
        interval = raw[name]
        require(isinstance(interval, dict), f"{label}.{name} is malformed")
        result[name] = (
            as_fraction(interval.get("lower"), f"{label}.{name}.lower"),
            as_fraction(interval.get("upper"), f"{label}.{name}.upper"),
        )
    return result


def binary64_fraction(text: str, label: str) -> Fraction:
    require(isinstance(text, str), f"{label} is not a hexadecimal endpoint")
    try:
        value = float.fromhex(text)
        numerator, denominator = value.as_integer_ratio()
    except (ValueError, OverflowError) as error:
        raise AxisChartCheckError(f"{label} is malformed: {error}") from error
    return Fraction(numerator, denominator)


def authenticate_sources(
    p2b0_path: Path = P2B0_PATH,
    p2bk_path: Path = P2BK_PATH,
    h10_config_path: Path = H10_CONFIG_PATH,
    kato_config_path: Path = KATO_CONFIG_PATH,
    v2_bridge_path: Path = V2_BRIDGE_PATH,
) -> dict[str, Any]:
    p2b0, p2b0_digest = authenticate_certificate(
        p2b0_path, P2B0_SHA256, "V2_H10_C01_KERNEL", P2B0_ATOMS, "P2b0")
    p2bk, p2bk_digest = authenticate_certificate(
        p2bk_path, P2BK_SHA256, "V2_P2_KATO_KERNEL", P2BK_ATOMS, "P2bK")

    h10, h10_digest = load_bound_json(
        h10_config_path, H10_CONFIG_SHA256, "P2b0 configuration")
    kato, kato_digest = load_bound_json(
        kato_config_path, KATO_CONFIG_SHA256, "P2bK configuration")
    v2_bridge, bridge_digest = load_bound_json(
        v2_bridge_path, V2_BRIDGE_SHA256, "v2 comparison bridge")
    source_binding(p2b0, H10_CONFIG_RELATIVE, h10_digest, "P2b0")
    source_binding(p2bk, KATO_CONFIG_RELATIVE, kato_digest, "P2bK")

    h10_radius = as_fraction(
        h10["coordinate_domain"]["unstable_radius"], "H10 unstable radius")
    graph_tube = as_fraction(
        h10["tube_radii"]["value_euclidean"], "H10 C0 tube")
    kato_radius = as_fraction(
        kato["coordinate_domain"]["source_radius"], "Kato source radius")
    gates = kato["acceptance_gates"]
    phase_shift = as_fraction(
        gates["phase_shift_absolute_upper"], "Kato phase-shift gate")
    alpha_lower = as_fraction(gates["alpha_lower"], "Kato alpha gate")
    beta_lower = as_fraction(gates["beta_lower"], "Kato beta gate")
    require(h10_radius == kato_radius == SOURCE_RADIUS,
            "source-radius contracts do not agree")
    require(graph_tube == GRAPH_TUBE_RADIUS, "H10 C0 tube changed")
    require(phase_shift == PHASE_SHIFT_BOUND, "Kato phase-shift gate changed")
    require(alpha_lower == beta_lower == ALPHA_BETA_LOWER,
            "Kato hyperbolicity gates changed")

    chi = p2bk["raw_probe"]["scalar_enclosures"]["chi"]
    chi_lower = binary64_fraction(chi["lower_hex"], "chi.lower")
    chi_upper = binary64_fraction(chi["upper_hex"], "chi.upper")
    require(chi_lower > -PHASE_SHIFT_BOUND and chi_upper < PHASE_SHIFT_BOUND,
            "strict Kato phase-shift enclosure no longer passes")
    alpha = p2bk["raw_probe"]["scalar_enclosures"]["alpha"]
    beta = p2bk["raw_probe"]["scalar_enclosures"]["beta"]
    require(binary64_fraction(alpha["lower_hex"], "alpha.lower") >
            ALPHA_BETA_LOWER, "strict alpha lower enclosure no longer passes")
    require(binary64_fraction(beta["lower_hex"], "beta.lower") >
            ALPHA_BETA_LOWER, "strict beta lower enclosure no longer passes")

    audit = p2bk.get("kato_exact_algebra_audit", {})
    require(audit.get("status") == "PASS", "Kato exact audit is not PASS")
    audit_checks = audit.get("checks", {})
    for name in KATO_EXACT_CHECKS:
        require(audit_checks.get(name) is True,
                f"Kato exact check {name} is not true")

    bridge_variables = exact_variables(v2_bridge, "v2 bridge")
    for certificate, label in ((p2b0, "P2b0"), (p2bk, "P2bK")):
        source_variables = exact_variables(
            certificate["continuation_bridge"], f"{label} bridge")
        for axis, (lower, upper) in bridge_variables.items():
            source_lower, source_upper = source_variables[axis]
            require(source_lower <= lower <= upper <= source_upper,
                    f"v2 bridge is not contained in the {label} bridge")

    return {
        "P2b0_certificate_sha256": p2b0_digest,
        "P2bK_certificate_sha256": p2bk_digest,
        "H10_configuration_sha256": h10_digest,
        "Kato_configuration_sha256": kato_digest,
        "v2_bridge_sha256": bridge_digest,
        "P2b0_required_atoms": list(P2B0_ATOMS),
        "P2bK_required_atoms": list(P2BK_ATOMS),
        "Kato_exact_checks": list(KATO_EXACT_CHECKS),
        "strict_chi_enclosure": {
            "lower": rational(chi_lower),
            "upper": rational(chi_upper),
        },
        "v2_bridge": {
            axis: {
                "lower": rational(interval[0]),
                "upper": rational(interval[1]),
            }
            for axis, interval in bridge_variables.items()
        },
        "independent_replay": "1/2",
    }


def arctangent_bounds(x: Fraction, term_count: int) -> tuple[Fraction, Fraction]:
    require(Fraction(0) < x < Fraction(1), "arctangent input is outside (0,1)")
    require(term_count >= 2, "at least two alternating terms are required")
    partial = Fraction(0)
    last_two: list[Fraction] = []
    for index in range(term_count):
        term = x ** (2 * index + 1) / (2 * index + 1)
        partial += term if index % 2 == 0 else -term
        if index >= term_count - 2:
            last_two.append(partial)
    return min(last_two), max(last_two)


def machin_two_pi_bounds(term_count: int = 8) -> tuple[Fraction, Fraction]:
    """Return a rigorous rational enclosure from Machin's identity."""

    five_lower, five_upper = arctangent_bounds(Fraction(1, 5), term_count)
    two_three_nine_lower, two_three_nine_upper = arctangent_bounds(
        Fraction(1, 239), term_count)
    # 2*pi = 32*atan(1/5) - 8*atan(1/239).
    return (
        32 * five_lower - 8 * two_three_nine_upper,
        32 * five_upper - 8 * two_three_nine_lower,
    )


def exact_symbolic_checks() -> dict[str, bool]:
    try:
        import sympy as sp
    except Exception as error:
        raise AxisChartCheckError(f"cannot import exact symbolic backend: {error}") \
            from error

    u1, u2, s1 = sp.symbols("u1 u2 s1", real=True)
    a, b, h = sp.symbols("a b h", real=True, nonzero=True)
    alpha, beta, c = sp.symbols("alpha beta c", real=True)
    x = u1 + s1
    s2 = -u2 * s1 / u1 - a * x**3 / (6 * h * u1) \
        + b * x**4 / (8 * h * u1)
    hamiltonian = (
        -2 * h * (u1 * s2 + u2 * s1)
        - a * x**3 / 3
        + b * x**4 / 4
    )
    transform = sp.Matrix([
        [1, 0, 1, 0],
        [alpha, -beta, -alpha, beta],
        [c / 2, h, c / 2, h],
        [alpha, beta, -alpha, -beta],
    ])
    return {
        "zero_energy_substitution_is_exact":
            sp.cancel(sp.factor(hamiltonian)) == 0,
        "physical_linear_transform_determinant":
            sp.factor(transform.det() + 8 * alpha * beta * h) == 0,
    }


def compute_exact_values() -> dict[str, Any]:
    machin_lower, machin_upper = machin_two_pi_bounds()
    symbolic = exact_symbolic_checks()
    h_lower = 2 * ALPHA_BETA_LOWER**2
    left_deviation = TWO_PI_UPPER - THETA_LOWER
    right_deviation = THETA_UPPER - TWO_PI_LOWER
    cosine_from_gate = 1 - ANGLE_GATE**2 / 2
    checks = {
        "Machin_interval_is_nonempty": machin_lower < machin_upper,
        "frozen_two_pi_enclosure_contains_Machin_interval":
            TWO_PI_LOWER < machin_lower < machin_upper < TWO_PI_UPPER,
        "proper_arc_left_deviation_below_7_over_12":
            left_deviation < THETA_DEVIATION,
        "proper_arc_right_deviation_below_7_over_12":
            right_deviation < THETA_DEVIATION,
        "phase_and_Kato_shift_sum_is_143_over_240":
            THETA_DEVIATION + PHASE_SHIFT_BOUND == TOTAL_ANGLE_BOUND,
        "total_angle_bound_below_3_over_5":
            TOTAL_ANGLE_BOUND < ANGLE_GATE,
        "quadratic_cosine_lower_is_41_over_50":
            cosine_from_gate == COSINE_LOWER,
        "u1_lower_is_41_over_5000":
            SOURCE_RADIUS * COSINE_LOWER == U1_LOWER,
        "u1_is_strictly_positive": U1_LOWER > 0,
        "proper_phase_arc_has_no_repeated_angle":
            THETA_UPPER - THETA_LOWER < machin_lower,
        "graph_C0_tube_strictly_inside_eta_chart":
            GRAPH_TUBE_RADIUS < ETA_CHART_RADIUS,
        "h_uniform_lower_is_positive": h_lower > 0,
        "action_design_ceiling_is_positive": ACTION_DESIGN_CEILING > 0,
        **symbolic,
    }
    return {
        "constants": {
            "source_radius": rational(SOURCE_RADIUS),
            "graph_C0_tube_radius": rational(GRAPH_TUBE_RADIUS),
            "eta_chart_radius": rational(ETA_CHART_RADIUS),
            "phase_shift_absolute_upper": rational(PHASE_SHIFT_BOUND),
            "proper_phase_lower": rational(THETA_LOWER),
            "proper_phase_upper": rational(THETA_UPPER),
            "frozen_two_pi_lower": rational(TWO_PI_LOWER),
            "frozen_two_pi_upper": rational(TWO_PI_UPPER),
            "Machin_two_pi_lower": rational(machin_lower),
            "Machin_two_pi_upper": rational(machin_upper),
            "left_phase_deviation": rational(left_deviation),
            "right_phase_deviation": rational(right_deviation),
            "theta_deviation_gate": rational(THETA_DEVIATION),
            "total_angle_bound": rational(TOTAL_ANGLE_BOUND),
            "angle_gate": rational(ANGLE_GATE),
            "cosine_lower": rational(COSINE_LOWER),
            "u1_strict_lower": rational(U1_LOWER),
            "alpha_beta_lower": rational(ALPHA_BETA_LOWER),
            "h_strict_lower": rational(h_lower),
            "action_design_ceiling": rational(ACTION_DESIGN_CEILING),
        },
        "checks": checks,
        "exact_chart": {
            "unstable_coordinate":
                "u=(1/100) R_chi(mu) (cos(theta),sin(theta))",
            "first_stable_coordinate": "s1=H10_1(u)+eta",
            "zero_energy_solve":
                "s2=-(u2/u1)s1-a_mu(u1+s1)^3/(6h_mu u1)"
                "+b_mu(u1+s1)^4/(8h_mu u1)",
            "true_source_graph":
                "eta_mu(theta)=(H_mu-H10)_1(u(theta,mu))",
            "true_source_graph_bound": "|eta_mu(theta)|<=1/200000",
            "eta_is_action_coordinate": False,
            "true_source_has_P2d_action": "nu=0",
        },
        "thickening_criterion": {
            "input":
                "complete strict zero-action first-event/incidence/census "
                "skeleton with m_ax>0 on finitely many compact domains",
            "output":
                "there exists delta_ent in (0,2^-55] preserving the "
                "arrangement with margins at least m_ax/2",
            "delta_ent_numeric_value_produced": False,
            "full_fixed_2^-55_disc_certified": False,
        },
    }


def proof_binding(path: Path = PROOF_PATH) -> dict[str, Any]:
    try:
        source = path.read_bytes()
        text = source.decode("utf-8")
    except (OSError, UnicodeError) as error:
        raise AxisChartCheckError(f"cannot read axis-chart proof: {error}") \
            from error
    digest = sha256_bytes(source)
    contract_present = PROOF_CONTRACT in text
    return {
        "path": PROOF_RELATIVE,
        "expected_sha256": PROOF_SHA256,
        "observed_sha256": digest,
        "proof_contract": PROOF_CONTRACT,
        "proof_contract_present": contract_present,
        "matched": digest == PROOF_SHA256 and contract_present,
    }


def build_report(
    proof_path: Path = PROOF_PATH,
    p2b0_path: Path = P2B0_PATH,
    p2bk_path: Path = P2BK_PATH,
    h10_config_path: Path = H10_CONFIG_PATH,
    kato_config_path: Path = KATO_CONFIG_PATH,
    v2_bridge_path: Path = V2_BRIDGE_PATH,
) -> dict[str, Any]:
    sources = authenticate_sources(
        p2b0_path, p2bk_path, h10_config_path, kato_config_path, v2_bridge_path)
    exact = compute_exact_values()
    binding = proof_binding(proof_path)
    exact_pass = all(exact["checks"].values())
    local_pass = exact_pass and binding["matched"]
    return {
        "schema_version": SCHEMA_VERSION,
        "scope": SCOPE,
        "status": (
            "PASS" if local_pass else
            "INCONCLUSIVE" if exact_pass else "FAIL"
        ),
        "source_gate_status": "PASS",
        "mathematical_status": (
            "LOCAL_MATHEMATICAL_PASS" if local_pass else
            "INCONCLUSIVE" if exact_pass else "FAIL"
        ),
        "mathematical_pass_scope": (
            SCOPE if local_pass else "NONE"
        ),
        "claim_bearing": False,
        "release_eligible": False,
        "independent_replay": "1/2",
        "source_authentication": sources,
        "proof_binding": binding,
        "exact_values": exact,
        "local_status": {
            "P2E.ZERO_ACTION_TRUE_SOURCE_CHART":
                "PASS" if local_pass else "OPEN",
            "P2E.AXIS_SKELETON_THICKENING_CRITERION":
                "PASS" if local_pass else "OPEN",
            "P2E.ZERO_ACTION_FIRST_EVENT_SKELETON": "OPEN",
            "V2.EVENT_ATLAS": "OPEN",
        },
        "claim_boundary": {
            "local_proof_bound_lemma_only": True,
            "pointwise_true_graph_evaluator_claimed": False,
            "first_hit_calculation_performed": False,
            "incidence_complex_certified": False,
            "connected_component_census_certified": False,
            "numeric_m_ax_produced": False,
            "numeric_delta_ent_produced": False,
            "full_fixed_2^-55_disc_certified": False,
            "temporal_stability_Turing_selection_canard": "NOT_IN_SCOPE",
        },
        "next_required_result":
            "rigorous complete zero-action first-event skeleton for the "
            "algebraic and pole channels, with the P2c homoclinic imported",
    }


def emit(value: dict[str, Any]) -> None:
    sys.stdout.write(canonical_json(value))


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--proof", type=Path, default=PROOF_PATH)
    parser.add_argument("--p2b0-certificate", type=Path, default=P2B0_PATH)
    parser.add_argument("--p2bk-certificate", type=Path, default=P2BK_PATH)
    parser.add_argument("--h10-configuration", type=Path,
                        default=H10_CONFIG_PATH)
    parser.add_argument("--kato-configuration", type=Path,
                        default=KATO_CONFIG_PATH)
    parser.add_argument("--v2-bridge", type=Path, default=V2_BRIDGE_PATH)
    arguments = parser.parse_args(argv)
    try:
        report = build_report(
            arguments.proof.resolve(),
            arguments.p2b0_certificate.resolve(),
            arguments.p2bk_certificate.resolve(),
            arguments.h10_configuration.resolve(),
            arguments.kato_configuration.resolve(),
            arguments.v2_bridge.resolve(),
        )
    except (
        OSError,
        UnicodeError,
        json.JSONDecodeError,
        AxisChartCheckError,
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
            "local_status": {
                "P2E.ZERO_ACTION_TRUE_SOURCE_CHART": "OPEN",
                "P2E.AXIS_SKELETON_THICKENING_CRITERION": "OPEN",
                "V2.EVENT_ATLAS": "OPEN",
            },
        })
        return 2
    emit(report)
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
