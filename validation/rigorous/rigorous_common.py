#!/usr/bin/env python3
"""Shared, dependency-light helpers for staged rigorous validation."""

from __future__ import annotations

import hashlib
import json
import subprocess
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable

VERDICTS = ("PASS", "FAIL", "INCONCLUSIVE")

LOCAL_GRAPH_FORMULAS = [
    "alpha=sqrt(2+c)/2",
    "beta=sqrt(2-c)/2",
    "h=2*alpha*beta",
    "U=u1+s1",
    "P=alpha*u1-beta*u2-alpha*s1+beta*s2",
    "V=(c/2)*u1+h*u2+(c/2)*s1+h*s2",
    "Q=alpha*u1+beta*u2-alpha*s1-beta*s2",
    "N_u=(1/(4*alpha),-1/(4*beta))*n(U)",
    "N_s=-N_u",
    "n(U)=-a*U^2+(sqrt(epsilon)*r^2/3)*U^3",
]

LOCAL_GRAPH_ACCEPTANCE_GATES = {
    "frame_determinant_absolute_lower": "0",
    "unstable_face_outward_margin_lower": "0",
    "stable_face_inward_margin_lower": "0",
    "difference_cone_margin_lower": "0",
    "first_quadratic_coefficient_upper": "1",
    "refined_quadratic_coefficient_upper": "1/4",
    "backward_decay_rate_lower": "2/3",
}

H10_C01_FORMULAS = [
    "q_mu=(1/(4*alpha),-1/(4*beta))",
    "G_mu(x)=q_mu*n_mu(x)",
    "x0=u1+H10_1(u)",
    "y=s-H10(u)",
    "R_mu=Bs_mu*H10-G_mu(x0)-DH10*(Bu_mu*u+G_mu(x0))",
    "R_mu=R_0+DeltaBs*H10-DeltaG-DH10*(DeltaBu*u+DeltaG)",
    "X0=R+H",
    "X=X0+rho",
    "Cq=norm(a*q_mu-q_0)<=delta_q*(1+delta_a)+(1/2)*delta_a",
    "delta_G=(Cq+k*b*X0)*X0^2",
    "delta_G_prime=2*Cq*X0+3*k*b*X0^2",
    "E0=D0+delta_B*H+(1+d)*delta_G+d*delta_B*R",
    "E1=D1+delta_B*d+(1+d)*delta_G_prime+d2*(delta_B*R+delta_G)+d*(delta_B+(1+d)*delta_G_prime)",
    "ell=k*(2*(1+delta_a)*X+3*b*X^2)",
    "m=k*(2*(1+delta_a)+6*b*X)",
    "kappa=alpha-(1+norm(DH10))*ell",
    "c0_margin=kappa*rho-E0",
    "Gu=E1+(norm(D2H10)*ell+(1+norm(DH10))^2*m)*rho",
    "c1_margin=2*kappa*eta-Gu-ell*eta^2",
]

H10_C01_REFERENCE_BOUNDS = {
    "h10_euclidean": Fraction(33, 10**6),
    "dh10_frobenius": Fraction(21, 4000),
    "d2h10_frobenius": Fraction(427, 1000),
    "core_defect_euclidean": Fraction(23, 10**25),
    "core_defect_derivative_frobenius": Fraction(21, 10**22),
}

H10_C01_PARAMETER_GATES = {
    "absolute_a_minus_one_upper": Fraction(11, 78125),
    "b_upper": Fraction(22, 9375),
    "absolute_c_upper": Fraction(156261, 3906250),
    "alpha_lower": Fraction(699, 1000),
    "q_norm_upper": Fraction(501, 1000),
    "delta_block_operator_upper": Fraction(101, 10000),
    "delta_q_norm_upper": Fraction(51, 10000),
}

H10_C01_ACCEPTANCE_GATES = {
    "center_residual_euclidean_upper": Fraction(3, 2000000),
    "center_residual_derivative_frobenius_upper": Fraction(27, 100000),
    "weighted_nonlinear_lipschitz_upper": Fraction(101, 10000),
    "weighted_nonlinear_second_upper": Fraction(101, 100),
    "normal_contraction_lower": Fraction(17, 25),
    "c0_inward_margin_lower": Fraction(19, 10000000),
    "c1_cone_margin_lower": Fraction(1, 8000),
}


def load_json(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"expected a JSON object: {path}")
    return value


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def run_checked(arguments: list[str], cwd: Path | None = None,
                timeout: int = 120) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        arguments,
        cwd=cwd,
        check=True,
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        timeout=timeout,
    )


def git_output(repository: Path, *arguments: str) -> str:
    return run_checked(["git", "-C", str(repository), *arguments]).stdout.strip()


def combine_verdicts(statuses: Iterable[str]) -> str:
    values = list(statuses)
    if any(status == "FAIL" for status in values):
        return "FAIL"
    if any(status == "INCONCLUSIVE" for status in values):
        return "INCONCLUSIVE"
    if any(status not in VERDICTS for status in values):
        raise ValueError(f"invalid verdict in {values!r}")
    return "PASS"


def fraction(value: dict[str, str]) -> Fraction:
    return Fraction(int(value["numerator"]), int(value["denominator"]))


def validate_exact_box(box: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    expected = {
        "r": (Fraction(1, 25), Fraction(2, 25)),
        "a2": (Fraction(-1, 4), Fraction(1, 4)),
        "epsilon": (Fraction(4, 5), Fraction(6, 5)),
    }
    variables = box.get("variables", {})
    for name, bounds in expected.items():
        try:
            observed = (fraction(variables[name]["lower"]),
                        fraction(variables[name]["upper"]))
        except (KeyError, TypeError, ValueError, ZeroDivisionError) as error:
            errors.append(f"invalid exact interval for {name}: {error}")
            continue
        if observed != bounds:
            errors.append(f"frozen {name} interval changed: {observed!r} != {bounds!r}")
        if observed[0] >= observed[1]:
            errors.append(f"{name} is not a positive-width interval")
    if box.get("selected_before_interval_validation") is not True:
        errors.append("box is not marked selected_before_interval_validation")
    if box.get("status") != "FROZEN_PREVALIDATION":
        errors.append("box status is not FROZEN_PREVALIDATION")
    return errors


def validate_exact_bridge(bridge: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    expected = {
        "r": (Fraction(0, 1), Fraction(2, 25)),
        "a2": (Fraction(-1, 4), Fraction(1, 4)),
        "epsilon": (Fraction(4, 5), Fraction(6, 5)),
    }
    variables = bridge.get("variables", {})
    for name, bounds in expected.items():
        try:
            observed = (fraction(variables[name]["lower"]),
                        fraction(variables[name]["upper"]))
        except (KeyError, TypeError, ValueError, ZeroDivisionError) as error:
            errors.append(f"invalid bridge interval for {name}: {error}")
            continue
        if observed != bounds:
            errors.append(
                f"frozen bridge {name} interval changed: {observed!r} != {bounds!r}")
        if observed[0] >= observed[1]:
            errors.append(f"bridge {name} is not a positive-width interval")
    if bridge.get("selected_before_p2_interval_validation") is not True:
        errors.append("bridge is not marked selected_before_p2_interval_validation")
    if bridge.get("status") != "FROZEN_PRE_P2_VALIDATION":
        errors.append("bridge status is not FROZEN_PRE_P2_VALIDATION")
    if bridge.get("anchor_face", {}).get("equation") != "r=0":
        errors.append("bridge does not retain the exact r=0 anchor face")
    return errors


def validate_local_graph_configuration(configuration: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if configuration.get("configuration_id") != "vdp-p2-local-graph-v1":
        errors.append("unexpected local-graph configuration identifier")
    if configuration.get("status") != "FROZEN_PREVALIDATION":
        errors.append("local-graph configuration is not frozen")
    if configuration.get("frozen_before_interval_run") is not True:
        errors.append("local-graph configuration was not frozen before validation")
    block = configuration.get("coordinate_block", {})
    expected_radius = Fraction(1, 100)
    for key in ("unstable_radius", "stable_radius", "source_circle_radius"):
        try:
            observed = fraction(block[key])
        except (KeyError, TypeError, ValueError, ZeroDivisionError) as error:
            errors.append(f"invalid local-graph {key}: {error}")
            continue
        if observed != expected_radius:
            errors.append(
                f"local-graph {key} changed: {observed!r} != {expected_radius!r}")
    frame = configuration.get("closed_form_frame", {})
    if frame.get("formulas") != LOCAL_GRAPH_FORMULAS:
        errors.append("local-graph closed-form frame formulas changed")
    if frame.get("phase_scope") != \
            "local-graph-only-not-V2-transported-absolute-phase":
        errors.append("local-graph phase-scope boundary changed")
    if configuration.get("acceptance_gates") != LOCAL_GRAPH_ACCEPTANCE_GATES:
        errors.append("local-graph acceptance gates changed")
    if configuration.get("proved_subobligations") != [
            "V2.WU.FRAME_BLOCK", "V2.WU.COARSE_GRAPH"]:
        errors.append("local-graph subobligation list changed")
    if configuration.get("pending_parent_obligation") != "V2.WU_GRAPH":
        errors.append("local-graph parent-obligation boundary changed")
    return errors


def _validate_rational_map(
        observed: Any, expected: dict[str, Fraction], label: str) -> list[str]:
    errors: list[str] = []
    if not isinstance(observed, dict):
        return [f"{label} is not an object"]
    if set(observed) != set(expected):
        errors.append(
            f"{label} keys changed: {sorted(observed)} != {sorted(expected)}")
    for name in set(observed) & set(expected):
        try:
            value = fraction(observed[name])
        except (KeyError, TypeError, ValueError, ZeroDivisionError) as error:
            errors.append(f"invalid {label}.{name}: {error}")
            continue
        if value != expected[name]:
            errors.append(
                f"{label}.{name} changed: {value!r} != {expected[name]!r}")
    return errors


def validate_h10_c01_configuration(configuration: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if configuration.get("configuration_id") != "vdp-p2-h10-c01-v1":
        errors.append("unexpected H10 C0/C1 configuration identifier")
    if configuration.get("status") != "FROZEN_PRE_P2B_CERTIFICATE":
        errors.append("H10 C0/C1 configuration is not frozen")
    if configuration.get("frozen_before_outward_rounded_p2b_run") is not True:
        errors.append(
            "H10 C0/C1 configuration was not frozen before the P2b run")
    domain = configuration.get("coordinate_domain", {})
    try:
        if fraction(domain["unstable_radius"]) != Fraction(1, 100):
            errors.append("H10 C0/C1 unstable radius changed")
    except (KeyError, TypeError, ValueError, ZeroDivisionError) as error:
        errors.append(f"invalid H10 C0/C1 unstable radius: {error}")
    radii = configuration.get("tube_radii", {})
    expected_radii = {
        "value_euclidean": Fraction(1, 200000),
        "first_derivative_frobenius": Fraction(3, 10000),
    }
    errors.extend(_validate_rational_map(radii, expected_radii, "tube_radii"))
    errors.extend(_validate_rational_map(
        configuration.get("reference_upper_bounds"),
        H10_C01_REFERENCE_BOUNDS, "reference_upper_bounds"))
    errors.extend(_validate_rational_map(
        configuration.get("parameter_auxiliary_gates"),
        H10_C01_PARAMETER_GATES, "parameter_auxiliary_gates"))
    errors.extend(_validate_rational_map(
        configuration.get("acceptance_gates"),
        H10_C01_ACCEPTANCE_GATES, "acceptance_gates"))
    if configuration.get("proof_formulas") != H10_C01_FORMULAS:
        errors.append("H10 C0/C1 proof formulas changed")
    if configuration.get("proved_subobligations") != [
            "V2.WU.H10_C0_TUBE", "V2.WU.H10_C1_TUBE"]:
        errors.append("H10 C0/C1 subobligations changed")
    if configuration.get("pending_obligations") != [
            "V2.WU.JETS", "V2.WU_GRAPH"]:
        errors.append("H10 C0/C1 parent-obligation boundary changed")
    basis = configuration.get("selection_basis", {})
    if basis.get("repository_commit") != \
            "b5596ee2726863b5f9002721a72766d3a59235ca":
        errors.append("H10 C0/C1 selection commit changed")
    if basis.get("repository_tag") != "vdp-issue7-p2a-v1":
        errors.append("H10 C0/C1 selection tag changed")
    expected_selection_files = {
        "continuation_bridge": (
            "validation/rigorous/config/vdp_bridge_v1.json",
            "2b62e6fc5625d3f5634d986f7e9cbe8199abfc45c7b97ca29e5efd464b5b69c7"),
        "p2a_configuration": (
            "validation/rigorous/config/vdp_p2_local_graph_v1.json",
            "b11ecadb088e8fbd686ed4834335f96c460bee9a18b0d1edab4222da645e199b"),
        "p2a_certificate": (
            "validation/rigorous/results/vdp_bridge_v1_p2a_local_graph.json",
            "192b351c3f153080d82bc856fa3c667388dc16c7b4cf0cfa8568fa347bcaf6be"),
    }
    for name, (path, digest) in expected_selection_files.items():
        item = basis.get(name, {})
        if item.get("path") != path or item.get("sha256") != digest:
            errors.append(f"H10 C0/C1 selection {name} binding changed")
    center = configuration.get("imported_core_center", {})
    if center.get("commit") != "d54add098545063d5efe8f1d6f062d4cfc116a0d":
        errors.append("H10 C0/C1 core commit changed")
    expected_imports = {
        "generator": (
            "validation/origin-algebraic-heteroclinic/"
            "generate_polynomial_header.py",
            "7c612d51b357569b64a51f0bb36c59e215e26c8d14b584419c24e32ffed5bfcb"),
        "term_table": (
            "validation/origin-algebraic-heteroclinic/unstable_graph_terms.hpp",
            "d617587ea1b9037c1c7575ccdde5029529ec5b736dee259baff9a2a162001e96"),
        "reference_probe": (
            "validation/origin-algebraic-heteroclinic/unstable_graph_probe.cpp",
            "a2102394a7afbb70331e810a4676f19ec9a79dd3492509ab3c7aad2464e2d2c2"),
        "reference_readme": (
            "validation/origin-algebraic-heteroclinic/README.md",
            "96241bcfc7481f12c0dacfc33246a142b257388653c4be7590e7924e151d9cae"),
        "source_certificate": (
            "validation/origin-algebraic-heteroclinic/certificate.json",
            "60882ee1d3b2b18264b85764288505ae8b47d00bc826a2bddec152898f690fbe"),
    }
    for name, (path, digest) in expected_imports.items():
        item = center.get(name, {})
        if item.get("path") != path or item.get("sha256") != digest:
            errors.append(f"H10 C0/C1 imported {name} binding changed")
    if configuration.get("exact_center_audit") != {
            "regenerate_term_table_from_frozen_generator": True,
            "require_byte_identical_term_table": True,
            "coefficient_field": "Q(sqrt(2))",
            "center_minimum_total_degree": 2,
            "center_maximum_total_degree": 10,
            "h1_term_count": 54,
            "h2_term_count": 63,
            "require_center_degrees_zero_and_one_to_vanish": True,
            "defect_minimum_total_degree": 11,
            "defect_maximum_total_degree": 29,
            "defect1_term_count": 361,
            "defect2_term_count": 361,
            "require_defect_degrees_zero_through_ten_to_vanish": True,
            "require_unique_monomials_positive_denominators": True,
            }:
        errors.append("H10 C0/C1 exact-center audit protocol changed")
    return errors


def box_arguments(box: dict[str, Any]) -> list[str]:
    arguments: list[str] = []
    for name in ("r", "a2", "epsilon"):
        interval = box["variables"][name]
        for endpoint in ("lower", "upper"):
            arguments.extend([
                interval[endpoint]["numerator"],
                interval[endpoint]["denominator"],
            ])
    return arguments


def safe_repository_path(repository: Path, relative: str) -> Path:
    candidate = (repository / relative).resolve()
    root = repository.resolve()
    if candidate != root and root not in candidate.parents:
        raise ValueError(f"path escapes repository: {relative}")
    return candidate
