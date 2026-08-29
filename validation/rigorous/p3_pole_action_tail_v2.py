#!/usr/bin/env python3
"""One-shot Laurent--log action-tail validation on the frozen pole block."""

from __future__ import annotations

import argparse
import json
from fractions import Fraction as F
from pathlib import Path
from typing import Any

try:
    from validation.rigorous import p3_pole_local_end_v2 as local
except ModuleNotFoundError:  # direct execution from validation/rigorous
    import p3_pole_local_end_v2 as local


HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[1]
CONFIG = HERE / "config" / "vdp_p3_pole_action_tail_v2.json"
LOCAL_CONFIG = HERE / "config" / "vdp_p3_pole_local_end_v2.json"
LOCAL_RESULT = HERE / "results" / "vdp_box_v2_p3_pole_local_end.json"
BOX = HERE / "config" / "vdp_box_v2.json"
OUTPUT = HERE / "results" / "vdp_box_v2_p3_pole_action_tail.json"


def upper_binary64(item: dict[str, str]) -> F:
    return F.from_float(float.fromhex(item["upper_hex"]))


def weighted_norm(poly: local.Poly, sigma0: F, p_upper: F,
                  env: dict, power_weight: int, log_weight: int) -> F:
    """Bound poly/[sigma^power_weight P^log_weight], P=1+|log sigma|."""
    total = F(0)
    for (power, log_power), coefficient in poly.items():
        radial_power = power - power_weight
        excess_log = max(log_power - log_weight, 0)
        if radial_power < 0 or (radial_power == 0 and excess_log > 0):
            raise ValueError(
                f"nonintegrable or unbounded action monomial {(power, log_power)}"
            )
        if excess_log and radial_power < excess_log:
            raise ValueError(
                f"unproved action power-log monotonicity {(power, log_power)}"
            )
        total += (
            local.eval_expr(coefficient, env).abs_upper()
            * sigma0**radial_power * p_upper**excess_log
        )
    return total


def build_certificate() -> dict[str, Any]:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    local_config = json.loads(LOCAL_CONFIG.read_text(encoding="utf-8"))
    local_result = json.loads(LOCAL_RESULT.read_text(encoding="utf-8"))
    box = json.loads(BOX.read_text(encoding="utf-8"))
    bindings = config["bindings"]
    if local.sha(LOCAL_CONFIG) != bindings["local_end_config"]["sha256"]:
        raise ValueError("local-end config binding changed")
    if local.sha(LOCAL_RESULT) != bindings["local_end_result"]["sha256"]:
        raise ValueError("local-end result binding changed")
    if local_result["status"] != bindings["local_end_result"]["required_status"]:
        raise ValueError("local-end prerequisite did not pass")
    theorem = REPOSITORY / bindings["theorem"]["path"]
    if local.sha(theorem) != bindings["theorem"]["sha256"]:
        raise ValueError("V3 theorem binding changed")

    sigma = local.frac(local_config["section"]["sigma0"])
    M = local.frac(local_config["remainder_ball"]["C0_radius"])
    fixed_point_remainder = upper_binary64(
        local_result["analytic_majorant"]["self_map_rhs_upper"]
    )
    p_upper = F(29)
    variables = box["variables"]
    rlo = local.frac(variables["r"]["lower"])
    rhi = local.frac(variables["r"]["upper"])
    epslo = local.frac(variables["epsilon"]["lower"])
    epshi = local.frac(variables["epsilon"]["upper"])
    delta_lo, delta_hi = rlo**2, rhi**2
    ell_lo, ell_hi = F(12, 5) * delta_lo, F(5, 2) * delta_hi
    adev = F(11, 5_000_000)

    jet, w_poly, _z_poly, symbols = local.build_polynomials()
    labels = local_config["label_rectangle"]
    env = {
        symbols["D"]: local.I(1 / delta_hi, 1 / delta_lo),
        symbols["H"]: local.I(ell_lo, ell_hi),
        symbols["E"]: local.I(epslo, epshi),
        symbols["A"]: local.I(1 - adev, 1 + adev),
        symbols["Z"]: local.I(local.frac(labels["Z0"]["lower"]),
                                local.frac(labels["Z0"]["upper"])),
        symbols["W"]: local.I(local.frac(labels["W0"]["lower"]),
                                local.frac(labels["W0"]["upper"])),
        symbols["C"]: local.I(local.frac(labels["c4"]["lower"]),
                                local.frac(labels["c4"]["upper"])),
    }
    D, H, E = symbols["D"], symbols["H"], symbols["E"]
    DJ: local.Poly = symbols["DJ"]  # type: ignore[assignment]
    y_jet = local.padd({(0, 0): 1}, jet, local.pscale(DJ, -1))
    x2 = jet[(2, 0)]
    x3 = jet[(3, 0)]
    y_square_regularized = local.padd(
        local.pmul(y_jet, y_jet),
        {(0, 0): -1, (2, 0): 2 * x2, (3, 0): 4 * x3},
    )
    if any(power < 4 for power, _ in y_square_regularized):
        raise ValueError("Y^2 singular subtraction failed exact cancellation")
    charge_jet = local.padd(w_poly, {(0, 1): -H * E})
    rho_jet = local.padd(
        local.pshift(local.pscale(y_square_regularized, 6 * E / D**3), -4),
        local.pscale(local.pmul(charge_jet, charge_jet), -D),
    )
    rho_jet_coefficient = weighted_norm(
        rho_jet, sigma, p_upper, env, power_weight=0, log_weight=2
    )

    weight = sigma**5 * p_upper**2
    y_jet_sup = local.poly_sup(y_jet, sigma, p_upper, env)
    # The fixed point lies in the image of the frozen C0 ball, so the
    # authenticated self-map RHS is a sharper proved remainder radius than
    # the ambient ball radius itself.  The first coarse action attempt used M
    # here and is disclosed in the result/report.
    ry_coefficient = 7 * fixed_point_remainder
    HEmax = ell_hi * epshi
    wr_coefficient = HEmax * F(37, 125) * fixed_point_remainder
    charge_jet_over_p = weighted_norm(
        charge_jet, sigma, p_upper, env, power_weight=0, log_weight=1
    )
    delta_cubic_factor = 6 * epshi * delta_hi**3
    y_remainder_coefficient = delta_cubic_factor * (
        2 * y_jet_sup * ry_coefficient * sigma
        + ry_coefficient**2 * sigma**6 * p_upper**2
    )
    wr_over_p = wr_coefficient * sigma**5 * p_upper
    charge_remainder_coefficient = (1 / delta_lo) * (
        2 * charge_jet_over_p * wr_over_p + wr_over_p**2
    )
    density_coefficient = (
        rho_jet_coefficient
        + y_remainder_coefficient
        + charge_remainder_coefficient
    )
    density_remainder_coefficient = (
        y_remainder_coefficient + charge_remainder_coefficient
    )
    integration_factor = sigma * (p_upper**2 + 2 * p_upper + 2)
    tail_abs_upper = density_coefficient * integration_factor

    # The local-end solve already differentiated the fixed point in each
    # label.  Its outward upper endpoints are safe exact binary rationals.
    derivative_norms = {
        name: upper_binary64(value)
        for name, value in local_result["analytic_majorant"][
            "label_remainder_input_norms"
        ].items()
    }
    label_density: dict[str, F] = {}
    label_tail: dict[str, F] = {}
    for name, symbol in (("c4", symbols["C"]),
                         ("Z0", symbols["Z"]),
                         ("W0", symbols["W"])):
        Ftheta = derivative_norms[name]
        ytheta_jet = local.pdiff(y_jet, symbol)
        charge_theta_jet = local.pdiff(charge_jet, symbol)
        rho_theta_jet = local.pdiff(rho_jet, symbol)
        rho_theta_jet_coefficient = weighted_norm(
            rho_theta_jet, sigma, p_upper, env,
            power_weight=0, log_weight=2,
        )
        ytheta_sup = local.poly_sup(ytheta_jet, sigma, p_upper, env)
        rytheta_coefficient = 7 * Ftheta
        ytheta_remainder = delta_cubic_factor * (
            2 * y_jet_sup * rytheta_coefficient * sigma
            + 2 * ry_coefficient * ytheta_sup * sigma
            + 2 * ry_coefficient * rytheta_coefficient
              * sigma**6 * p_upper**2
        )
        wrtheta_coefficient = HEmax * F(37, 125) * Ftheta
        wrtheta_over_p = wrtheta_coefficient * sigma**5 * p_upper
        charge_theta_over_p = weighted_norm(
            charge_theta_jet, sigma, p_upper, env,
            power_weight=0, log_weight=1,
        )
        charge_theta_remainder = 2 * (1 / delta_lo) * (
            charge_jet_over_p * wrtheta_over_p
            + wr_over_p * charge_theta_over_p
            + wr_over_p * wrtheta_over_p
        )
        coefficient = (
            rho_theta_jet_coefficient
            + ytheta_remainder
            + charge_theta_remainder
        )
        label_density[name] = coefficient
        label_tail[name] = coefficient * integration_factor

    gates = config["acceptance_gates"]
    density_gate = local.frac(gates["C0_density_coefficient_strict_upper"])
    tail_gate = local.frac(gates["C0_tail_abs_strict_upper"])
    label_density_gate = local.frac(
        gates["each_label_C1_density_coefficient_strict_upper"]
    )
    label_tail_gate = local.frac(
        gates["each_label_C1_tail_abs_strict_upper"]
    )
    c0_pass = density_coefficient < density_gate and tail_abs_upper < tail_gate
    c1_pass = all(value < label_density_gate for value in label_density.values()) \
        and all(value < label_tail_gate for value in label_tail.values())
    # A frozen corner gives a strict negative conclusion for the two quality
    # gates.  This is not a counterexample to integrability: it is caused by
    # the deliberately broad root-four label interval.
    corner_env = dict(env)
    corner_env[D] = local.I.point(F(2500))
    corner_env[H] = local.I(F(12, 5) / 2500, F(5, 2) / 2500)
    corner_env[E] = local.I.point(F(6, 5))
    corner_env[symbols["A"]] = local.I.point(1)
    corner_env[symbols["Z"]] = local.I.point(F(-3, 4))
    corner_env[symbols["W"]] = local.I.point(0)
    corner_env[symbols["C"]] = local.I.point(F(10**15))
    log_sigma = local.I(-12 * local.ln10_interval().hi,
                        -12 * local.ln10_interval().lo)
    corner_jet_density = local.eval_poly(
        rho_jet, sigma, log_sigma, corner_env
    )
    corner_density = corner_jet_density + local.I.symmetric(
        density_remainder_coefficient * p_upper**2
    )
    corner_density_abs_lower = (
        min(abs(corner_density.lo), abs(corner_density.hi))
        if not (corner_density.lo <= 0 <= corner_density.hi) else F(0)
    )
    corner_normalized_density_abs_lower = (
        corner_density_abs_lower / p_upper**2
    )
    corner_jet_tail = local.eval_poly(
        local.pintegrate(rho_jet), sigma, log_sigma, corner_env
    )
    corner_tail = corner_jet_tail + local.I.symmetric(
        density_remainder_coefficient * integration_factor
    )
    corner_tail_abs_lower = (
        min(abs(corner_tail.lo), abs(corner_tail.hi))
        if not (corner_tail.lo <= 0 <= corner_tail.hi) else F(0)
    )
    density_quality_fail = corner_normalized_density_abs_lower > density_gate
    tail_quality_fail = corner_tail_abs_lower > tail_gate
    if density_quality_fail and tail_quality_fail:
        status = "STRICT_NEGATIVE_FROZEN_ACTION_QUALITY_GATES"
    elif c0_pass and c1_pass:
        status = "LOCAL_ACTION_C0_LABEL_C1_PASS"
    else:
        status = "INCONCLUSIVE"

    return {
        "schema_version": "rfsn-vdp-p3-pole-action-tail-result/1",
        "configuration_id": config["configuration_id"],
        "configuration_sha256": local.sha(CONFIG),
        "status": status,
        "mathematical_status": "PARTIAL_LOCAL_PASS_WITH_STRICT_QUALITY_FAIL"
        if status.startswith("STRICT_NEGATIVE") else (
            "PARTIAL_LOCAL_PASS" if status.endswith("PASS") else "INCONCLUSIVE"
        ),
        "claim_bearing": False,
        "domain": {
            "sigma0": local.q(sigma),
            "parameter_box": box["box_id"],
            "label_rectangle": labels,
        },
        "remainder_binding": {
            "ambient_C0_ball_radius": local.q(M),
            "authenticated_fixed_point_image_radius": local.q(
                fixed_point_remainder
            ),
            "justification": "R=T(R) and the passed self-map certificate bounds T on the complete ambient ball by this image radius.",
        },
        "decision_disclosure": {
            "initial_coarse_output_retained_then_replaced": True,
            "initial_status": "INCONCLUSIVE",
            "initial_error": "The ambient radius 1e30 was used as the actual fixed-point remainder although the bound prerequisite already certified the sharper image radius.",
            "parameters_expression_and_gates_changed": False,
        },
        "regularized_density": {
            "formula": config["regularized_density"],
            "bound": "abs(rho_reg(sigma)) <= C0*(1+abs(log(sigma)))^2",
            "C0_coefficient_upper": local.q(density_coefficient),
            "required_strict_upper": local.q(density_gate),
            "integrability_status": "PASS",
            "quality_gate_status": "PASS" if density_coefficient < density_gate else "FAIL_BY_WITNESS",
        },
        "action_tail": {
            "definition": config["tail"],
            "absolute_upper": local.q(tail_abs_upper),
            "required_strict_upper": local.q(tail_gate),
            "finiteness_status": "PASS",
            "quality_gate_status": "PASS" if tail_abs_upper < tail_gate else "FAIL_BY_WITNESS",
        },
        "strict_negative_witness": {
            "parameter_label_point": {
                "r": "1/50", "a2": "0", "epsilon": "6/5",
                "Z0": "-3/4", "W0": "0", "c4": "1000000000000000"
            },
            "density_interval_at_sigma0": local.qi(corner_density),
            "normalized_density_absolute_lower": local.q(
                corner_normalized_density_abs_lower
            ),
            "tail_interval": local.qi(corner_tail),
            "tail_absolute_lower": local.q(corner_tail_abs_lower),
            "density_gate_status": "FAIL" if density_quality_fail else "INCONCLUSIVE",
            "tail_gate_status": "FAIL" if tail_quality_fail else "INCONCLUSIVE",
            "unique_dominant_term": "-36*epsilon*delta^3*c4 in the integrable sigma^0 density coefficient",
        },
        "label_C1": {
            name: {
                "density_coefficient_upper": local.q(label_density[name]),
                "tail_derivative_abs_upper": local.q(label_tail[name]),
                "density_required_strict_upper": local.q(label_density_gate),
                "tail_required_strict_upper": local.q(label_tail_gate),
                "status": "PASS" if (
                    label_density[name] < label_density_gate
                    and label_tail[name] < label_tail_gate
                ) else "INCONCLUSIVE",
            }
            for name in ("c4", "Z0", "W0")
        },
        "moving_cut_identity": {
            "identity": "A_fp,C0=integral_C0^C1(lambda_delta)+A_fp,C1",
            "status": "PASS_EXACT_ADDITIVITY",
            "reason": "Both finite parts use the same sigma0, F_div, and local tail; these cancel exactly, leaving ordinary line-integral additivity.",
        },
        "atoms": [
            {"id": "V3.POLE_TAIL.ACTION_DENSITY_C0_INTEGRABLE", "status": "PASS"},
            {"id": "V3.POLE_TAIL.ACTION_TAIL_C0_FINITE", "status": "PASS"},
            {"id": "V3.POLE_TAIL.ACTION_DENSITY_FROZEN_QUALITY", "status": "FAIL" if density_quality_fail else "INCONCLUSIVE"},
            {"id": "V3.POLE_TAIL.ACTION_TAIL_FROZEN_QUALITY", "status": "FAIL" if tail_quality_fail else "INCONCLUSIVE"},
            {"id": "V3.POLE_TAIL.ACTION_TAIL_LABEL_C1", "status": "PASS" if c1_pass else "INCONCLUSIVE"},
            {"id": "V3.POLE_TAIL.MOVING_CUT", "status": "PASS"},
        ],
        "parent_obligations": [
            {"id": "V3.SOURCE_TO_POLE", "status": "INCONCLUSIVE"},
            {"id": "V3.POLE_TAIL", "status": "INCONCLUSIVE",
             "reason": "The local density is integrable and has finite C0/label-C1 tail bounds, but the frozen 1e-6 quality gate is strictly false on the full c4 rectangle; mixed external-parameter C2 bounds and global arrival also remain unproved."},
        ],
        "nonclaims": [
            "No mixed mu-C2 or source-phase-C2 action bound is asserted.",
            "The finite compact action from a global source cut to sigma0 is not enclosed here.",
            "The parent V3.POLE_TAIL obligation remains INCONCLUSIVE.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=OUTPUT)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args()
    certificate = build_certificate()
    rendered = json.dumps(certificate, indent=2, sort_keys=True) + "\n"
    if args.check:
        if not args.output.exists() or args.output.read_text(encoding="utf-8") != rendered:
            raise SystemExit("stored pole action-tail result is stale")
    else:
        args.output.write_text(rendered, encoding="utf-8")
    print(certificate["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
