#!/usr/bin/env python3
"""Fail-closed structural gate for the application-owned v2 P2e event atlas.

This checker never runs CAPD and never awards a mathematical PASS.  It either
reports that the prospectively frozen materialization is structurally ready
for its first full run, or stops before that run with an INCONCLUSIVE verdict.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import re
import subprocess
import sys
from fractions import Fraction
from pathlib import Path
from typing import Any, Iterable


HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[1]
DEFAULT_CONFIG = HERE / "config" / "vdp_p2e_event_atlas_v2.json"

MISSING = "MISSING"
FROZEN = "FROZEN"
MATERIALIZATION_NAMES = (
    "carriers",
    "physical_event_faces",
    "defining_functions",
    "ambient_function_lists",
    "incidence_complex",
    "corner_priority",
    "first_event_census",
    "normalization",
    "numeric_m0",
    "transported_traces",
    "numerical_method",
)
OUTCOMES = {"return", "alg", "pole", "lat", "cut"}
TIME_DIFFERENCES = {"q_h", "q_alg", "q_pole", "q_ret"}
SELECTED_TERMINALS = {"g_h", "g_alg", "g_pole"}
SELECTED_APERTURES = {"a_h", "a_alg", "a_pole"}
SIDE_FUNCTIONS = {"h_side_h", "h_side_alg", "h_side_pole"}
SHA256_RE = re.compile(r"[0-9a-f]{64}\Z")
COMMIT_RE = re.compile(r"[0-9a-f]{40}\Z")
PLACEHOLDER_RE = re.compile(
    r"(?:\bTBD\b|\bTODO\b|\bMISSING\b|\bPLACEHOLDER\b|\bPROXY\b|AFFINE_PROXY)",
    re.IGNORECASE,
)

EXPECTED_BINDINGS = {
    "CORE_IMPORT": (
        "van-der-pol/CENTRAL_CORE_IMPORT.md",
        "037abc2fc9e54ebd8ec645489a5d62ba8e3cd06013360dfad82351e6eb442a56",
    ),
    "V2_THEOREM": (
        "van-der-pol/CENTRAL_CONTINUATION.md",
        "e02d067595f89ea7f19dfac81a7eba84ea0bdda17e4bbe12f569e776ba775026",
    ),
    "P2_CONTRACT": (
        "validation/rigorous/P2_VALIDATION_CONTRACT.md",
        "4216cd677e766637705b08edd58af1a768b4822fe1eebdf2dd19fa3ce376e02b",
    ),
    "TARGET_BOX": (
        "validation/rigorous/config/vdp_box_v2.json",
        "43ff2ee14db2e9d42abe484e9d415176cc92836fb2956a27cb6b9f72a751b1ed",
    ),
    "COMPARISON_BRIDGE": (
        "validation/rigorous/config/vdp_bridge_v2.json",
        "ee45e35157075805f89e12d9eb89a82e9203167d22109d4f2b9e83ee2bd12de9",
    ),
    "PHASE_GAP_CONTRACT": (
        "validation/rigorous/config/vdp_p2e_phase_order_v2.json",
        "3abc9b0ae0a6d2d383798954231dc255fefcc8eda426237c47383b0d0fb8ea7d",
    ),
    "PHASE_GAP_RESULT": (
        "validation/rigorous/results/vdp_box_v2_p2e_phase_order.json",
        "45e55e81817612af8ddbdd44f256ee6309e7e1df6328ff6945cd00a89a1e00ff",
    ),
    "FLOWBOX_SCOUT_NON_EVIDENTIARY": (
        "numerics/results/vdp_p2e_channel_scout_v2/terminal_flowbox_scout.json",
        "a7617fe8eed0e4dcdc700cb19e9792a33338124960e17cf339211304c87f9d8e",
    ),
    "PHYSICAL_SADDLE_FACE_CONTRACT": (
        "validation/rigorous/config/vdp_p2d_physical_slides_v1.json",
        "fa7daa1273b508951e081378d938342f985271722bf4871669a30f4ab44a8f16",
    ),
    "PHYSICAL_SOURCE_PHASE_SEAM_PROOF": (
        "theory/EXPLICIT_FINITE_CHART_OVERLAPS.md",
        "4afe3faa733eb20bac87978bbaaa8bd746248fd90e52d195c9d1ee4cc551d918",
    ),
    "PHYSICAL_SOURCE_PHASE_SEAM_CONTRACT": (
        "validation/rigorous/config/vdp_p2d_overlaps_v1.json",
        "698f5979f021e3702fd733169d71178fd06fd103647dff1a2bf87456edad407a",
    ),
    "DEPENDENCY_LOCK": (
        "validation/rigorous/dependency.lock.json",
        "4d486a63cddf0902cc9fc4dedacc5a172527f6e167e2d311afa680c077a45b68",
    ),
    "FLAGSHIP_IMPORT_LOCK": (
        "validation/rigorous/flagship_import.lock.json",
        "6c1752d6ee78d4b670c74ecb85e776eddcb4459e0b0e7f7ae14cae2325e0476e",
    ),
}

EXPECTED_CARRIERS = {
    "C.H": (3, ["x_h_1", "x_h_2", "t_h"], "HOMOCLINIC_CHANNEL_FLOWBOX"),
    "C.A": (3, ["x_a_1", "x_a_2", "t_a"], "ALGEBRAIC_CHANNEL_FLOWBOX"),
    "C.P": (3, ["x_p_1", "x_p_2", "t_p"], "POLE_CHANNEL_FLOWBOX"),
    "B.OUT": (2, ["phi_u", "nu_u"], "OUTGOING_AND_PRE_EVENT_BAND"),
    "B.RET": (2, ["psi_r", "nu_r"], "RETURN_AND_PRE_EVENT_BAND"),
    "Z.PLUS": (2, ["phi", "theta_bar"], "POSITIVE_SOURCE_SIGN_CELL"),
    "Z.MINUS": (2, ["phi", "theta_bar"], "NEGATIVE_SOURCE_SIGN_CELL"),
    "Z.HOM.PLUS": (
        2, ["phi", "theta_bar"], "POSITIVE_RESTRICTED_HOMOCLINIC_PULLBACK"),
    "Z.HOM.MINUS": (
        2, ["phi", "theta_bar"], "NEGATIVE_RESTRICTED_HOMOCLINIC_PULLBACK"),
}

PHYSICAL_CARRIERS = {"C.H", "C.A", "C.P", "B.OUT", "B.RET"}
PULLBACK_TARGETS = {
    "Z.PLUS": "B.OUT",
    "Z.MINUS": "B.OUT",
    "Z.HOM.PLUS": "B.RET",
    "Z.HOM.MINUS": "B.RET",
}

EXPECTED_APERTURE_CENTERS = {
    "ALG": (
        "phi_a^0, the fixed direct P2bK common source-phase label of the "
        "V2 finite-gate anchor"),
    "HOM": "phi_h(mu), the selected P2c homoclinic source trace",
    "POLE": "2*pi in the fixed lifted phase coordinate",
}

EXPECTED_PHASE_INTERFACE = {
    "displayed_coordinates": ["phi_u", "nu_u"],
    "underlying_exact_section_coordinates": ["psi_u", "nu_u"],
    "forward_boundary_seam": "phi_u=kappa_mu(psi_u)",
    "inverse_boundary_seam": (
        "psi_u=lambda_mu(phi_u)=kappa_mu^(-1)(phi_u)"),
    "displayed_carrier_embedding": (
        "E_out_mu^dir(phi_u,nu_u)="
        "E_out_mu^P2d(lambda_mu(phi_u),nu_u)"),
    "exact_action_preserved": True,
    "standard_canonical_pair_claim": False,
    "return_band_uses_underlying_p2d_coordinates": True,
    "numeric_seam_materialization_status": "PENDING",
}
EXPECTED_ENTRY_PHASE_RADII = {
    "ALG": Fraction(1, 10_000_000),
    "HOM": Fraction(1, 100_000_000),
    "POLE": Fraction(1, 100_000),
}

EXPECTED_FUNCTIONS = {
    "g_h": ("SELECTED_TERMINAL", "PHYSICAL_FACE"),
    "g_alg": ("SELECTED_TERMINAL", "PHYSICAL_FACE"),
    "g_pole": ("SELECTED_TERMINAL", "PHYSICAL_FACE"),
    "w_alg": ("ALGEBRAIC_INTERNAL_LABEL", "LABEL_ONLY"),
    "h_side_h": ("AUXILIARY_LATERAL_FACE", "PHYSICAL_FACE"),
    "h_side_alg": ("AUXILIARY_LATERAL_FACE", "PHYSICAL_FACE"),
    "h_side_pole": ("AUXILIARY_LATERAL_FACE", "PHYSICAL_FACE"),
    "a_h": ("OUTGOING_APERTURE", "PHYSICAL_FACE"),
    "a_alg": ("OUTGOING_APERTURE", "PHYSICAL_FACE"),
    "a_pole": ("OUTGOING_APERTURE", "PHYSICAL_FACE"),
    "a_ret": ("RETURN_APERTURE", "PHYSICAL_FACE"),
    "c_stable": ("STABLE_MANIFOLD_CUT", "LABEL_ONLY"),
    "q_h": ("PAIRWISE_EVENT_TIME_DIFFERENCE", "TIME_DIFFERENCE"),
    "q_alg": ("PAIRWISE_EVENT_TIME_DIFFERENCE", "TIME_DIFFERENCE"),
    "q_pole": ("PAIRWISE_EVENT_TIME_DIFFERENCE", "TIME_DIFFERENCE"),
    "q_ret": ("PAIRWISE_EVENT_TIME_DIFFERENCE", "TIME_DIFFERENCE"),
}

EXPECTED_TIME_DIFFERENCE_BINDINGS = {
    "q_h": ("u_h", "g_h"),
    "q_alg": ("u_alg", "g_alg"),
    "q_pole": ("u_pole", "g_pole"),
    "q_ret": ("u_r", "a_ret"),
}
TIME_DIFFERENCE_OUTCOMES = {
    "q_h": "return",
    "q_alg": "alg",
    "q_pole": "pole",
    "q_ret": "return",
}

EXPECTED_LISTS = {
    "L.C.H": ("C.H", ["g_h", "h_side_h", "a_ret", "c_stable"], 0),
    "L.C.A": ("C.A", ["g_alg", "w_alg", "h_side_alg"], 0),
    "L.C.P": ("C.P", ["g_pole", "h_side_pole"], 0),
    "L.B.OUT.H": (
        "B.OUT", ["a_h", "a_alg", "a_pole", "w_alg", "q_h"], 1),
    "L.B.OUT.A": (
        "B.OUT", ["a_h", "a_alg", "a_pole", "w_alg", "q_alg"], 1),
    "L.B.OUT.P": (
        "B.OUT", ["a_h", "a_alg", "a_pole", "w_alg", "q_pole"], 1),
    "L.B.RET": ("B.RET", ["a_ret", "c_stable", "q_ret"], 1),
    "L.Z.PLUS.H": (
        "Z.PLUS", ["a_h", "a_alg", "a_pole", "w_alg", "q_h"], 1),
    "L.Z.PLUS.A": (
        "Z.PLUS", ["a_h", "a_alg", "a_pole", "w_alg", "q_alg"], 1),
    "L.Z.PLUS.P": (
        "Z.PLUS", ["a_h", "a_alg", "a_pole", "w_alg", "q_pole"], 1),
    "L.Z.MINUS.H": (
        "Z.MINUS", ["a_h", "a_alg", "a_pole", "w_alg", "q_h"], 1),
    "L.Z.MINUS.A": (
        "Z.MINUS", ["a_h", "a_alg", "a_pole", "w_alg", "q_alg"], 1),
    "L.Z.MINUS.P": (
        "Z.MINUS", ["a_h", "a_alg", "a_pole", "w_alg", "q_pole"], 1),
    "L.Z.HOM.PLUS": (
        "Z.HOM.PLUS", ["a_ret", "c_stable", "q_ret"], 1),
    "L.Z.HOM.MINUS": (
        "Z.HOM.MINUS", ["a_ret", "c_stable", "q_ret"], 1),
}

REQUIRED_FACE_ROLES = {
    "HOM_TERMINAL": "g_h",
    "ALG_TERMINAL": "g_alg",
    "POLE_TERMINAL": "g_pole",
    "HOM_SIDE": "h_side_h",
    "ALG_SIDE": "h_side_alg",
    "POLE_SIDE": "h_side_pole",
    "OUT_H_APERTURE": "a_h",
    "OUT_ALG_APERTURE": "a_alg",
    "OUT_POLE_APERTURE": "a_pole",
    "RETURN_APERTURE": "a_ret",
    "STABLE_CUT": "c_stable",
}

EXPECTED_DIRECT_FLOWBOX_EMBEDDINGS = {
    "C.H": (
        "E_H,mu(x,t)=Phi_mu^(t tau_H,mu(x))(E_out_mu^dir("
        "phi_h(mu)+10^-8 x_h_1,2^-55 x_h_2)); tau_H,mu is the first "
        "hit of the P2d incoming face and the retained coordinate domain "
        "is x_h_1^2+x_h_2^2<=5/4"),
    "C.A": (
        "E_A,mu(x,t)=Phi_mu^(t tau_A,mu(x))(E_out_mu^dir("
        "phi_a^0+10^-7 x_a_1,2^-55 x_a_2)); tau_A,mu is the first hit "
        "of e=(-U)^(-1)=23/400 and the retained coordinate domain is "
        "x_a_1^2+x_a_2^2<=5/4; w_alg is a separate pulled-back label "
        "and is not x_a_2"),
    "C.P": (
        "E_P,mu(x,t)=Phi_mu^(t tau_P,mu(x))(E_out_mu^dir("
        "2*pi+10^-5 x_p_1,2^-55 x_p_2)); tau_P,mu is the first hit of "
        "-U=10 and the retained coordinate domain is "
        "x_p_1^2+x_p_2^2<=5/4"),
}

EXPECTED_B_OUT_EMBEDDING = (
    "E_out_mu^dir(phi_u,nu_u)=E_out_mu^P2d(lambda_mu(phi_u),nu_u), "
    "the direct common-source-phase reparameterization of the "
    "Kato-oriented exact P2d outgoing radial section")

EXPECTED_B_RET_EMBEDDING = (
    "E_in_mu(psi_r,nu_r), the Kato-oriented exact P2d incoming radial "
    "section with psi_r=0 on the transported stable trace")

EXPECTED_B_OUT_COORDINATE_SEMANTICS = {
    "displayed_phase": "DIRECT_P2BK_COMMON_SOURCE_PHASE_PHI",
    "transverse_coordinate": "EXACT_P2D_SIGNED_ACTION_NU",
    "underlying_exact_section_coordinates": ["psi_u", "nu_u"],
    "exact_action_preserved": True,
    "standard_canonical_pair_claim": False,
}

EXPECTED_DIRECT_SOURCE_PULLBACKS = {
    "Z.PLUS": (
        "Pi_{+,infty,mu}^dir=(kappa_mu,id) o "
        "Pi_{+,infty,mu}^P2d:Z.PLUS->B.OUT in the direct common "
        "source-phase lift"),
    "Z.MINUS": (
        "Pi_{-,infty,mu}^dir=(kappa_mu,id) o "
        "Pi_{-,infty,mu}^P2d:Z.MINUS->B.OUT in the direct common "
        "source-phase lift"),
}

EXPECTED_DIRECT_LIST_PULLBACKS = {
    "Z.PLUS": (
        "Pi_{+,infty,mu}^dir=(kappa_mu,id) o "
        "Pi_{+,infty,mu}^P2d:Z.PLUS->B.OUT"),
    "Z.MINUS": (
        "Pi_{-,infty,mu}^dir=(kappa_mu,id) o "
        "Pi_{-,infty,mu}^P2d:Z.MINUS->B.OUT"),
}

EXPECTED_DIRECT_FACE_FORMULAS = {
    "OUT_H_APERTURE": (
        "((phi_u-phi_h(mu))/10^-8)^2+(nu_u/2^-55)^2-1=0"),
    "OUT_ALG_APERTURE": (
        "((phi_u-phi_a^0)/10^-7)^2+(nu_u/2^-55)^2-1=0"),
    "OUT_POLE_APERTURE": (
        "((phi_u-2*pi)/10^-5)^2+(nu_u/2^-55)^2-1=0"),
}

EXPECTED_DIRECT_FUNCTION_FORMULAS = {
    "w_alg": (
        "On C.A and B.OUT, w_alg is the transported core algebraic "
        "finite-gate label pulled back through E_A,mu and E_out,mu^dir; "
        "on Z domains it is pulled back by Pi_sigma,infty^dir. It is not "
        "identified with the signed action x_a_2."),
    "a_h": (
        "((phi_u-phi_h(mu))/10^-8)^2+(nu_u/2^-55)^2-1, with "
        "composition by Pi_sigma,infty^dir on Z.PLUS and Z.MINUS"),
    "a_alg": (
        "((phi_u-phi_a^0)/10^-7)^2+(nu_u/2^-55)^2-1, with "
        "composition by Pi_sigma,infty^dir on Z.PLUS and Z.MINUS; "
        "w_alg remains a separate label function"),
    "a_pole": (
        "((phi_u-2*pi)/10^-5)^2+(nu_u/2^-55)^2-1, with "
        "composition by Pi_sigma,infty^dir on Z.PLUS and Z.MINUS"),
    "q_h": (
        "tau_side_h-tau_terminal_h=3-4[((phi_u-phi_h(mu))/10^-8)^2+"
        "(nu_u/2^-55)^2] on its disjoint competing overlap and after "
        "Pi_sigma,infty^dir pullback"),
    "q_alg": (
        "tau_side_alg-tau_terminal_alg=3-4[((phi_u-phi_a^0)/10^-7)^2+"
        "(nu_u/2^-55)^2] on its disjoint competing overlap and after "
        "Pi_sigma,infty^dir pullback"),
    "q_pole": (
        "tau_side_pole-tau_terminal_pole=3-4[((phi_u-2*pi)/10^-5)^2+"
        "(nu_u/2^-55)^2] on its disjoint competing overlap and after "
        "Pi_sigma,infty^dir pullback"),
}

REQUIRED_MARGINS = {
    "ACTIVE_CONORMAL_RANK",
    "EVENT_SPEED",
    "EMPTY_INCIDENCE",
    "INACTIVE_FACE",
    "EARLIER_EVENT_EXCLUSION",
    "STRICT_ORDER_AWAY_FROM_DECLARED_TIES",
    "FLOW_DOMAIN_BUFFER",
    "CONTAINMENT",
    "APERTURE_SEPARATION",
    "ANCHOR_TO_BOUNDARY",
    "PROPER_PHASE_CUT",
}

EXPECTED_EMPTY_SECTIONS: dict[str, dict[str, Any]] = {
    "carriers": {"status": MISSING, "design_geometry": None, "records": []},
    "physical_event_faces": {"status": MISSING, "records": []},
    "defining_functions": {"status": MISSING, "records": []},
    "ambient_function_lists": {"status": MISSING, "records": []},
    "incidence_complex": {"status": MISSING, "records": []},
    "corner_priority": {"status": MISSING, "records": []},
    "first_event_census": {
        "status": MISSING, "records": [], "cell_complexes": [],
        "exhaustion": None,
    },
    "normalization": {
        "status": MISSING, "carrier_metrics": [], "function_scales": [],
        "time_scales": [], "phase_scale": None,
    },
    "numeric_m0": {
        "status": MISSING, "value": None, "margin_lowers": [],
        "bridge_half_bound": None, "simultaneous_tie_policy": None,
    },
    "transported_traces": {
        "status": MISSING, "records": [],
        "phase_gap_certificate_binding": None, "proper_phase_arc": None,
    },
    "numerical_method": {
        "status": MISSING,
        "carrier_domains": [],
        "state_partition": None,
        "ode_taylor_order": None,
        "precision": {
            "backend": "FILIB",
            "format": "IEEE_754_BINARY64",
            "significand_bits": 53,
            "multiprecision": False,
            "source": "validation/rigorous/dependency.lock.json",
        },
        "high_winding_N_policy":
            "NOT_A_P2E_V2_4_5_MATERIALIZATION_CHOICE",
        "legacy_ambiguous_fields_forbidden": ["D", "N", "precision"],
    },
}


class AuditError(ValueError):
    """The structural freeze contract is malformed or overclaims its scope."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise AuditError(message)


def load_json(path: Path) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        raise AuditError(f"cannot load JSON {path}: {error}") from error
    require(isinstance(value, dict), f"{path} is not a JSON object")
    return value


def sha256_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def repository_path(relative: str) -> Path:
    path = (REPOSITORY / relative).resolve()
    require(path.is_relative_to(REPOSITORY.resolve()),
            f"path escapes repository: {relative}")
    return path


def exact_fraction(value: Any, label: str, *, positive: bool = False) -> Fraction:
    require(isinstance(value, str), f"{label} is not an exact rational string")
    try:
        result = Fraction(value)
    except (ValueError, ZeroDivisionError) as error:
        raise AuditError(f"{label} is not an exact rational string") from error
    if positive:
        require(result > 0, f"{label} is not strictly positive")
    return result


def exact_interval(value: Any, label: str) -> tuple[Fraction, Fraction]:
    require(isinstance(value, list) and len(value) == 2,
            f"{label} is not an exact interval")
    lower = exact_fraction(value[0], f"{label} lower")
    upper = exact_fraction(value[1], f"{label} upper")
    require(lower < upper, f"{label} is not a nondegenerate interval")
    return lower, upper


def exact_keys(value: dict[str, Any], keys: Iterable[str], label: str) -> None:
    expected = set(keys)
    require(set(value) == expected,
            f"{label} keys differ: expected {sorted(expected)}, "
            f"observed {sorted(value)}")


def unique_records_by(
        records: Any, key: str, label: str) -> dict[str, dict[str, Any]]:
    require(isinstance(records, list), f"{label} is not a list")
    result: dict[str, dict[str, Any]] = {}
    for record in records:
        require(isinstance(record, dict), f"{label} contains a non-object")
        identifier = record.get(key)
        require(isinstance(identifier, str) and identifier,
                f"{label} contains a record without {key}")
        require(identifier not in result,
                f"duplicate {label} {key}: {identifier}")
        result[identifier] = record
    return result


def unique_records(records: Any, label: str) -> dict[str, dict[str, Any]]:
    return unique_records_by(records, "id", label)


def nonplaceholder(value: Any, label: str) -> str:
    require(isinstance(value, str) and value.strip(), f"{label} is empty")
    require(PLACEHOLDER_RE.search(value) is None,
            f"{label} contains a placeholder or proxy")
    return value


def validate_static_contract(config: dict[str, Any]) -> None:
    exact_keys(config, {
        "schema_version", "scope", "box_id", "comparison_bridge_id",
        "status", "base_revision", "gate_semantics", "coordinate_correction",
        "source_bindings",
        "read_only_theory_design_reference", "parameter_cover",
        "inventory_contract", "materialization", "full_run_gate",
        "obligations", "nonclaims",
    }, "top-level configuration")
    require(config["schema_version"] ==
            "rfsn-vdp-p2e-event-atlas-structure-gate/3",
            "event-atlas gate schema version changed")
    require(config["scope"] ==
            "V2_P2E_EXECUTABLE_EVENT_ATLAS_STRUCTURE_GATE_V3",
            "event-atlas gate scope changed")
    require(config["box_id"] == "vdp-positive-box-v2" and
            config["comparison_bridge_id"] ==
            "vdp-core-to-positive-bridge-v2",
            "event-atlas gate is not bound to the v2 box and bridge")
    require(config["status"] ==
            "STRUCTURAL_GATE_FROZEN_AFTER_PHASE_INTERFACE_CORRECTION_"
            "PENDING_MATERIALIZATION",
            "structural gate status changed")
    require(config["base_revision"] ==
            "4e2e3f097fbac75cf2ef2d149d7f002a25b8ea80",
            "structural gate base revision changed")

    semantics = config["gate_semantics"]
    require(semantics == {
        "structure_verdict": "READY_TO_SCOUT_NON_EVIDENTIARY",
        "structure_verdict_is_not_claim_bearing": True,
        "current_verdict": "STOP_BEFORE_FULL_RUN",
        "current_mathematical_status": "INCONCLUSIVE",
        "stop_reason": (
            "MISSING_EXECUTABLE_CORE_ATLAS_NUMERIC_M0_AND_DIRECT_CARRIER_SEAM"),
        "ready_verdict": "READY_FOR_FIRST_FULL_RUN",
        "ready_is_not_a_mathematical_pass": True,
        "full_capd_run_in_scope": False,
        "purpose": (
            "Freeze the coordinate-corrected application-owned atlas "
            "instance and its numerical execution choices before, but do "
            "not perform, the first full event-atlas run."),
    }, "gate semantics changed")

    require(config["coordinate_correction"] == {
        "supersedes_schema_version": (
            "rfsn-vdp-p2e-event-atlas-structure-gate/2"),
        "supersedes_commit": (
            "4e2e3f097fbac75cf2ef2d149d7f002a25b8ea80"),
        "reason": "P2D_PSI_AND_DIRECT_P2BK_PHI_WERE_CONFLATED",
        "superseded_object": (
            "B.OUT was written in the exact P2d transported section phase "
            "psi_u while its three aperture centers and the phase-gap "
            "certificate were direct P2bK common source-phase labels phi."),
        "corrected_object": (
            "B.OUT uses the direct common source phase phi_u and exact P2d "
            "signed action nu_u through E_out_mu^dir(phi_u,nu_u)="
            "E_out_mu^P2d(lambda_mu(phi_u),nu_u)."),
        "underlying_exact_section_coordinates": ["psi_u", "nu_u"],
        "boundary_seam": (
            "phi_u=kappa_mu(psi_u), psi_u=lambda_mu(phi_u)"),
        "exact_action_preserved": True,
        "standard_canonical_pair_claim": False,
        "discovered_before_first_full_run": True,
        "prior_atlas_materialization_executed": False,
        "prior_atlas_claim_passed": False,
        "mathematical_certificate_invalidated": False,
        "phase_gap_result_reused_without_recomputation": True,
        "reason_phase_gap_is_reusable": (
            "The retained strict phase-gap certificate already compares "
            "the direct P2bK common source labels phi_a^0, phi_h(mu), and "
            "the pole arc."),
    }, "phase-interface correction record changed")

    base = config["base_revision"]
    exists = subprocess.run(
        ["git", "-C", str(REPOSITORY), "cat-file", "-e", f"{base}^{{commit}}"],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    require(exists.returncode == 0, "base revision is unavailable")
    ancestor = subprocess.run(
        ["git", "-C", str(REPOSITORY), "merge-base", "--is-ancestor",
         base, "HEAD"], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    require(ancestor.returncode == 0,
            "base revision is not an ancestor of the current source")

    bindings = unique_records_by(
        config["source_bindings"], "role", "source binding")
    require(set(bindings) == set(EXPECTED_BINDINGS),
            "source-binding roles changed")
    for role, (relative, digest) in EXPECTED_BINDINGS.items():
        binding = bindings[role]
        exact_keys(binding, {"role", "path", "sha256"},
                   f"source binding {role}")
        require((binding["path"], binding["sha256"]) == (relative, digest),
                f"source binding changed: {role}")
        path = repository_path(relative)
        require(path.is_file(), f"bound source is missing: {relative}")
        require(sha256_file(path) == digest, f"bound source hash mismatch: {role}")

    theory = config["read_only_theory_design_reference"]
    require(theory == {
        "repository": "https://github.com/h-lu/reversible-rfsn-ii-waves",
        "commit": "fe992556dd5398ee1dd71aed0482cd1a1705394a",
        "path": "papers/paper-a/focused/sections/02_setting_and_theorem.tex",
        "sha256": "91bb0bb12e798d8a31150025221f3a2bd47222e028181189a7d196ed9875dce3",
        "role": (
            "READ_ONLY_B1_B5_AND_FUNCTION_INVENTORY_DESIGN_REFERENCE_"
            "NOT_AN_EXECUTABLE_ATLAS_IMPORT"),
    }, "read-only theory design reference changed")

    require(config["parameter_cover"] == {
        "status": FROZEN,
        "axes": [
            {"id": "r", "face_formula": "i/400",
             "index_range_inclusive": [0, 8], "cells": 8},
            {"id": "a2", "face_formula": "-1/4+j/256",
             "index_range_inclusive": [0, 128], "cells": 128},
            {"id": "epsilon", "face_formula": "4/5+k/10",
             "index_range_inclusive": [0, 4], "cells": 4},
        ],
        "bridge_cell_count": 4096,
        "target_r_cell_indices": [4, 5, 6, 7],
        "base_census_policy":
            "ONE_COMPLETE_R0_CENSUS_THEN_UNIFORM_NEAT_ISOTOPY_ON_THE_BRIDGE",
    }, "4096-cell parameter cover changed")

    inventory = config["inventory_contract"]
    exact_keys(inventory, {
        "carrier_specs", "function_specs", "time_difference_bindings",
        "ambient_list_specs",
        "allowed_outcomes", "priority_rules", "required_margin_categories",
    }, "inventory contract")
    carrier_specs = {
        item["id"]: (item["dimension"], item["coordinates"], item["role"])
        for item in inventory["carrier_specs"]
    }
    require(carrier_specs == EXPECTED_CARRIERS,
            "required carrier inventory changed")
    function_specs = {
        item["id"]: (item["role"], item["clock_role"])
        for item in inventory["function_specs"]
    }
    require(function_specs == EXPECTED_FUNCTIONS,
            "required defining-function inventory changed")
    time_bindings = {
        item["function_id"]: (
            item["side_occurrence_id"],
            item["associated_terminal_function_id"])
        for item in inventory["time_difference_bindings"]
    }
    require(time_bindings == EXPECTED_TIME_DIFFERENCE_BINDINGS and
            len(inventory["time_difference_bindings"]) ==
            len(EXPECTED_TIME_DIFFERENCE_BINDINGS),
            "side/time-difference occurrence bindings changed")
    list_specs = {
        item["id"]: (
            item["carrier_id"], item["required_functions"],
            item["maximum_time_difference_functions"])
        for item in inventory["ambient_list_specs"]
    }
    require(list_specs == EXPECTED_LISTS,
            "required ambient function-list inventory changed")
    require(inventory["allowed_outcomes"] ==
            ["return", "alg", "pole", "lat", "cut"],
            "allowed first-event outcomes changed")
    require(inventory["priority_rules"] == [
        "STABLE_CUT_HAS_OUTCOME_CUT",
        "SELECTED_TERMINAL_OR_RETURN_PRECEDES_AUXILIARY_LATERAL",
        "DECLARED_PAIRWISE_TIME_TIE_SELECTS_ITS_BOUND_PHYSICAL_TERMINAL",
        "SELECTED_PHYSICAL_CHANNEL_TIES_ARE_EMPTY",
        "SIMULTANEOUS_ACTIVE_FACE_SET_IS_RETAINED",
    ], "corner-priority contract changed")
    require(set(inventory["required_margin_categories"]) == REQUIRED_MARGINS and
            len(inventory["required_margin_categories"]) == len(REQUIRED_MARGINS),
            "normalized margin inventory changed")

    obligations = config["obligations"]
    require(obligations == [
        {"id": "V2.ATLAS.CORE_MANIFEST", "status": "PENDING"},
        {"id": "V2.ATLAS.INCIDENCE_COMPLEX", "status": "PENDING"},
        {"id": "V2.ATLAS.FIRST_EVENT_CENSUS", "status": "PENDING"},
        {"id": "V2.ATLAS.TRANSPORTED_TRACES", "status": "PENDING"},
        {"id": "V2.EVENT_ATLAS", "status": "PENDING"},
    ], "a structural freeze may not pass an atlas obligation")
    require(config["nonclaims"] == [
        "The carrier and pullback-domain formulas are prospectively frozen, but no physical carrier embedding has an interval certificate and no event-face, incidence, census, or m0 certificate exists.",
        "READY_FOR_FIRST_FULL_RUN, if reached later, authorizes only a prospectively frozen computation and is not a mathematical PASS.",
        "The three phase-gap subatoms cannot pass V2.EVENT_ATLAS without the complete transported traces and event census.",
        "The frozen flagship prose proves existence of a suitable atlas but does not serialize the application-owned atlas required here.",
        "The return-side occurrence is represented on return and pullback lists only through q_ret bound to the distinct occurrence u_r; it is not h_side_h and is not duplicated as a second side-hit function.",
        "The corrected B.OUT coordinates (phi_u,nu_u) preserve the exact P2d signed action through lambda_mu but are not claimed to be a standard canonical pair; the seam and physical carrier remain pending materialization.",
        "The earlier structural /2 gate was corrected before any full run or atlas PASS, so no mathematical certificate is invalidated and the direct-phase scalar gap certificate is retained.",
        "The bound terminal-flowbox scout is non-evidentiary design lineage only; no sampled orbit, affine proxy event, temporal-stability, Turing-selection, or canard conclusion is promoted.",
    ], "event-atlas structural nonclaim boundary changed")


def validate_carrier_design_geometry(geometry: dict[str, Any]) -> dict[str, Any]:
    exact_keys(geometry, {
        "phase_coordinate", "phase_interface", "proper_phase_arc",
        "two_pi_enclosure",
        "normal_band_half_width", "channel_normal_radius", "apertures",
        "required_relations",
    }, "carrier design geometry")
    require(geometry["phase_coordinate"] ==
            "DIRECT_P2BK_COMMON_SOURCE_PHASE_LIFT_WITH_P2D_SIGNED_ACTION",
            "carrier apertures use the wrong phase coordinate")
    require(geometry["phase_interface"] == EXPECTED_PHASE_INTERFACE,
            "direct/P2d phase interface changed or lost its noncanonical flag")
    phase_arc = exact_interval(geometry["proper_phase_arc"],
                               "proper carrier phase arc")
    two_pi = exact_interval(geometry["two_pi_enclosure"],
                            "two-pi enclosure")
    require(two_pi == (Fraction(103993, 16551), Fraction(208696, 33215)),
            "the frozen rational two-pi enclosure changed")
    band_half_width = exact_fraction(
        geometry["normal_band_half_width"], "normal band half width",
        positive=True)
    channel_radius = exact_fraction(
        geometry["channel_normal_radius"], "channel normal radius",
        positive=True)
    require(channel_radius < band_half_width,
            "channel normal radius is not strictly inside the band")
    require(geometry["required_relations"] == [
        "ALG_AND_HOM_ANCHORS_STRICTLY_INSIDE_THEIR_COLLARS",
        "POLE_COLLAR_STRICTLY_INSIDE_THE_LIFTED_CERTIFIED_OPEN_WINDOW",
        "COLLAR_CLOSURES_PAIRWISE_DISJOINT",
        "ALL_COLLARS_STRICTLY_INSIDE_THE_PROPER_PHASE_ARC",
        "CHANNEL_NORMAL_RADIUS_STRICTLY_INSIDE_THE_BAND",
    ], "carrier aperture relation inventory changed")

    apertures = unique_records(geometry["apertures"], "carrier aperture")
    require(set(apertures) == {"ALG", "HOM", "POLE"},
            "carrier aperture inventory changed")
    phase_result = load_json(repository_path(
        "validation/rigorous/results/vdp_box_v2_p2e_phase_order.json"))
    require(phase_result.get("integrity_status") ==
            "PASS_STRICT_BINARY_REPLAY" and
            phase_result.get("local_subatom_status") ==
            "PASS_THREE_PHASE_GAPS_ONLY",
            "phase-gap prerequisite is not the retained strict result")
    source_hulls = {
        "ALG": phase_result["phase_hulls"]["algebraic"],
        "HOM": phase_result["phase_hulls"][
            "homoclinic_comparison_bridge_hull"],
        "POLE": phase_result["phase_hulls"]["pole_closed_cover_mod_2pi"],
    }
    source_names = {
        "ALG": "PHASE_GAP_RESULT.phase_hulls.algebraic",
        "HOM": (
            "PHASE_GAP_RESULT.phase_hulls."
            "homoclinic_comparison_bridge_hull"),
        "POLE": "PHASE_GAP_RESULT.phase_hulls.pole_closed_cover_mod_2pi",
    }
    collars: dict[str, tuple[Fraction, Fraction]] = {}
    anchors: dict[str, tuple[Fraction, Fraction]] = {}
    for identifier, record in apertures.items():
        exact_keys(record, {
            "id", "center_definition", "center_enclosure",
            "protected_phase_radius", "entry_phase_radius",
            "entry_action_radius", "entry_map_definition",
            "anchor_enclosure", "anchor_source",
        }, f"carrier aperture {identifier}")
        require(record["center_definition"] ==
                EXPECTED_APERTURE_CENTERS[identifier],
                f"carrier aperture {identifier} center definition changed")
        nonplaceholder(record["entry_map_definition"],
                       f"carrier aperture {identifier} entry map")
        center = exact_interval(
            record["center_enclosure"],
            f"carrier aperture {identifier} center enclosure")
        radius = exact_fraction(
            record["protected_phase_radius"],
            f"carrier aperture {identifier} protected phase radius",
            positive=True)
        entry_radius = exact_fraction(
            record["entry_phase_radius"],
            f"carrier aperture {identifier} entry phase radius",
            positive=True)
        entry_action_radius = exact_fraction(
            record["entry_action_radius"],
            f"carrier aperture {identifier} entry action radius",
            positive=True)
        require(entry_radius == EXPECTED_ENTRY_PHASE_RADII[identifier] and
                entry_radius < radius,
                f"carrier aperture {identifier} entry phase scale changed")
        require(entry_action_radius == channel_radius,
                f"carrier aperture {identifier} entry action scale changed")
        collars[identifier] = (center[0] - radius, center[1] + radius)
        anchors[identifier] = exact_interval(
            record["anchor_enclosure"],
            f"carrier aperture {identifier} anchor")
        require(anchors[identifier] == exact_interval(
                    source_hulls[identifier],
                    f"strict phase-result {identifier} hull") and
                record["anchor_source"] == source_names[identifier],
                f"carrier aperture {identifier} is not bound to the strict phase result")

    for identifier in ("ALG", "HOM"):
        require(exact_interval(
                    apertures[identifier]["center_enclosure"],
                    f"{identifier} moving center") == anchors[identifier] and
                collars[identifier][0] < anchors[identifier][0] and
                anchors[identifier][1] < collars[identifier][1],
                f"{identifier} moving anchor is not strictly inside its collar")
    require(exact_interval(
                apertures["POLE"]["center_enclosure"],
                "POLE center") == two_pi,
            "pole aperture is not centered at the frozen two-pi lift")
    pole_window_mod = anchors["POLE"]
    require(collars["POLE"][0] > two_pi[1] + pole_window_mod[0] and
            collars["POLE"][1] < two_pi[0] + pole_window_mod[1],
            "pole collar is not uniformly inside the lifted certified window")

    ordered = [collars["ALG"], collars["HOM"], collars["POLE"]]
    require(all(left[1] < right[0]
                for left, right in zip(ordered, ordered[1:])),
            "selected aperture closures are not pairwise disjoint")
    require(all(phase_arc[0] < collar[0] and collar[1] < phase_arc[1]
                for collar in ordered),
            "a selected aperture is not strictly inside the proper phase arc")
    return {
        "proper_phase_arc": [str(value) for value in phase_arc],
        "aperture_phase_intervals": {
            identifier: [str(value) for value in collars[identifier]]
            for identifier in ("ALG", "HOM", "POLE")
        },
        "anchor_to_collar_margin_lowers": {
            "ALG": apertures["ALG"]["protected_phase_radius"],
            "HOM": apertures["HOM"]["protected_phase_radius"],
            "POLE": str(min(
                collars["POLE"][0] - (two_pi[1] + pole_window_mod[0]),
                two_pi[0] + pole_window_mod[1] - collars["POLE"][1])),
        },
        "aperture_separation_lowers": {
            "ALG_HOM": str(collars["HOM"][0] - collars["ALG"][1]),
            "HOM_POLE": str(collars["POLE"][0] - collars["HOM"][1]),
        },
        "proper_arc_boundary_margin_lower": str(min(
            collars["ALG"][0] - phase_arc[0],
            phase_arc[1] - collars["POLE"][1])),
        "normal_band_margin": str(band_half_width - channel_radius),
        "entry_phase_radii": {
            identifier: apertures[identifier]["entry_phase_radius"]
            for identifier in ("ALG", "HOM", "POLE")
        },
    }


def validate_carriers(section: dict[str, Any]) -> tuple[
        dict[str, dict[str, Any]], dict[str, Any]]:
    exact_keys(section, {"status", "design_geometry", "records"},
               "carriers section")
    require(isinstance(section["design_geometry"], dict),
            "carrier design geometry is missing")
    geometry_summary = validate_carrier_design_geometry(
        section["design_geometry"])
    records = unique_records(section["records"], "carrier")
    require(set(records) == set(EXPECTED_CARRIERS),
            "frozen carriers do not match the complete required inventory")
    for identifier, (dimension, coordinates, _) in EXPECTED_CARRIERS.items():
        record = records[identifier]
        exact_keys(record, {
            "id", "kind", "dimension", "coordinates", "coordinate_domain",
            "realization",
            "parameter_domain_id", "boundary_function_ids",
            "boundary_strata", "boundary_strata_complete", "frozen",
        }, f"carrier {identifier}")
        require(record["dimension"] == dimension and
                record["coordinates"] == coordinates,
                f"carrier {identifier} coordinate type changed")
        domain = record["coordinate_domain"]
        require(isinstance(domain, dict) and set(domain) == set(coordinates),
                f"carrier {identifier} lacks an exact coordinate domain")
        for coordinate in coordinates:
            exact_interval(domain[coordinate],
                           f"carrier {identifier} coordinate {coordinate}")
        realization = record["realization"]
        require(isinstance(realization, dict),
                f"carrier {identifier} realization is not explicit")
        if identifier in PHYSICAL_CARRIERS:
            require(record["kind"] == "PHYSICAL_ZERO_ENERGY_CARRIER",
                    f"physical carrier {identifier} changed type")
            expected_realization_keys = {
                "type", "definition", "certificate_id", "state_coordinates",
                "zero_energy", "immersion_required", "injectivity_required",
            }
            if identifier == "B.OUT":
                expected_realization_keys.add("coordinate_semantics")
            exact_keys(realization, expected_realization_keys,
                       f"physical carrier {identifier} realization")
            require(realization["type"] == "PHYSICAL_EMBEDDING",
                    f"physical carrier {identifier} lacks an embedding")
            nonplaceholder(realization["definition"],
                           f"carrier {identifier} embedding definition")
            nonplaceholder(realization["certificate_id"],
                           f"carrier {identifier} embedding certificate")
            require(realization["state_coordinates"] == ["U", "P", "V", "Q"],
                    f"carrier {identifier} does not use physical state coordinates")
            require(realization["zero_energy"] is True and
                    realization["immersion_required"] is True and
                    realization["injectivity_required"] is True,
                    f"carrier {identifier} weakens its physical embedding claim")
            if identifier in EXPECTED_DIRECT_FLOWBOX_EMBEDDINGS:
                require(realization["definition"] ==
                        EXPECTED_DIRECT_FLOWBOX_EMBEDDINGS[identifier],
                        f"carrier {identifier} bypasses the direct outgoing face")
            elif identifier == "B.OUT":
                require(realization["definition"] == EXPECTED_B_OUT_EMBEDDING,
                        "B.OUT does not compose the inverse phase seam with P2d")
                require(realization["certificate_id"] ==
                        "V2.ATLAS.CARRIER.B.OUT.EMBEDDING_AND_PHASE_SEAM",
                        "B.OUT phase seam is absent from its certificate obligation")
                require(realization["coordinate_semantics"] ==
                        EXPECTED_B_OUT_COORDINATE_SEMANTICS,
                        "B.OUT action or noncanonical coordinate semantics changed")
            elif identifier == "B.RET":
                require(realization["definition"] == EXPECTED_B_RET_EMBEDDING,
                        "B.RET no longer uses the exact P2d incoming coordinates")
        else:
            require(record["kind"] == "NORMALIZED_PULLBACK_DOMAIN",
                    f"pullback carrier {identifier} changed type")
            exact_keys(realization, {
                "type", "definition", "target_carrier_id", "map_definition",
                "certificate_id", "zero_energy_claim",
                "injective_embedding_claim",
            }, f"pullback carrier {identifier} realization")
            require(realization["type"] == "PULLBACK_DOMAIN" and
                    realization["target_carrier_id"] ==
                    PULLBACK_TARGETS[identifier],
                    f"pullback carrier {identifier} has the wrong target")
            nonplaceholder(realization["definition"],
                           f"pullback carrier {identifier} definition")
            nonplaceholder(realization["map_definition"],
                           f"pullback carrier {identifier} map")
            nonplaceholder(realization["certificate_id"],
                           f"pullback carrier {identifier} certificate")
            require(realization["zero_energy_claim"] is False and
                    realization["injective_embedding_claim"] is False,
                    f"pullback carrier {identifier} was promoted to a physical embedding")
            if identifier in EXPECTED_DIRECT_SOURCE_PULLBACKS:
                require(realization["map_definition"] ==
                        EXPECTED_DIRECT_SOURCE_PULLBACKS[identifier],
                        f"pullback carrier {identifier} bypasses kappa_mu")
        require(record["parameter_domain_id"] ==
                "vdp-core-to-positive-bridge-v2",
                f"carrier {identifier} is not defined on the full v2 bridge")
        boundary_ids = record["boundary_function_ids"]
        require(isinstance(boundary_ids, list) and boundary_ids and
                len(boundary_ids) == len(set(boundary_ids)),
                f"carrier {identifier} boundary functions are incomplete")
        strata = unique_records(record["boundary_strata"],
                                f"carrier {identifier} boundary stratum")
        require("INTERIOR" in strata and
                strata["INTERIOR"].get("active_boundary_function_ids") == [],
                f"carrier {identifier} lacks its interior boundary stratum")
        for stratum in strata.values():
            exact_keys(stratum, {"id", "active_boundary_function_ids"},
                       f"carrier {identifier} boundary stratum {stratum['id']}")
            active = stratum["active_boundary_function_ids"]
            require(isinstance(active, list) and
                    len(active) == len(set(active)) and
                    set(active) <= set(boundary_ids),
                    f"carrier {identifier} has an invalid boundary stratum")
        require(record["boundary_strata_complete"] is True and
                record["frozen"] is True,
                f"carrier {identifier} is not prospectively frozen")
    return records, geometry_summary


def validate_functions(section: dict[str, Any]) -> dict[str, dict[str, Any]]:
    exact_keys(section, {"status", "records"}, "defining-functions section")
    records = unique_records(section["records"], "defining function")
    require(set(records) == set(EXPECTED_FUNCTIONS),
            "frozen defining functions do not match the complete inventory")
    for identifier, (role, clock_role) in EXPECTED_FUNCTIONS.items():
        record = records[identifier]
        exact_keys(record, {
            "id", "role", "clock_role", "formula", "formula_type",
            "domain_ids", "coorientation", "is_carrier_boundary",
            "time_difference", "frozen",
        }, f"defining function {identifier}")
        require((record["role"], record["clock_role"]) == (role, clock_role),
                f"defining function {identifier} changed mathematical role")
        nonplaceholder(record["formula"],
                       f"defining function {identifier} formula")
        if identifier in EXPECTED_DIRECT_FUNCTION_FORMULAS:
            require(record["formula"] ==
                    EXPECTED_DIRECT_FUNCTION_FORMULAS[identifier],
                    f"defining function {identifier} reintroduces the wrong phase interface")
        require(record["formula_type"] in
                {"EXACT_EXPRESSION", "CERTIFIED_MAP_COMPOSITION"},
                f"defining function {identifier} formula type is not exact")
        domains = record["domain_ids"]
        require(isinstance(domains, list) and domains and
                len(domains) == len(set(domains)) and
                set(domains) <= set(EXPECTED_CARRIERS),
                f"defining function {identifier} has invalid domains")
        nonplaceholder(record["coorientation"],
                       f"defining function {identifier} coorientation")
        require(record["is_carrier_boundary"] is False,
                f"defining function {identifier} duplicates a carrier boundary")
        if identifier in TIME_DIFFERENCES:
            difference = record["time_difference"]
            require(isinstance(difference, dict),
                    f"{identifier} lacks its two event-time operands")
            exact_keys(difference, {
                "left_event_time_id", "right_event_time_id",
                "side_occurrence_id", "associated_terminal_function_id",
                "tie_policy"},
                f"time difference {identifier}")
            nonplaceholder(difference["left_event_time_id"],
                           f"{identifier} left event time")
            nonplaceholder(difference["right_event_time_id"],
                           f"{identifier} right event time")
            require(difference["left_event_time_id"] !=
                    difference["right_event_time_id"],
                    f"{identifier} subtracts one event time from itself")
            expected_occurrence, expected_terminal = (
                EXPECTED_TIME_DIFFERENCE_BINDINGS[identifier])
            require((difference["side_occurrence_id"],
                     difference["associated_terminal_function_id"]) ==
                    (expected_occurrence, expected_terminal),
                    f"{identifier} changed its side/terminal occurrence binding")
            require(difference["tie_policy"] ==
                    "RANK_ON_NONEMPTY_TIE_GAP_ONLY_IF_EMPTY",
                    f"{identifier} has a false positive time-gap policy")
        else:
            require(record["time_difference"] is None,
                    f"non-time function {identifier} carries an event clock")
        require(record["frozen"] is True,
                f"defining function {identifier} is not frozen")
    require(records["w_alg"]["clock_role"] == "LABEL_ONLY",
            "w_alg was promoted from a label to an event clock")
    return records


def validate_faces(section: dict[str, Any],
                   functions: dict[str, dict[str, Any]] | None) -> None:
    exact_keys(section, {"status", "records"}, "physical-event-faces section")
    records = unique_records(section["records"], "physical event face")
    roles: dict[str, dict[str, Any]] = {}
    for record in records.values():
        exact_keys(record, {
            "id", "role", "carrier_id", "defining_function_id", "formula",
            "domain", "coorientation", "is_carrier_boundary", "physical",
            "frozen",
        }, f"physical event face {record['id']}")
        role = record["role"]
        require(role in REQUIRED_FACE_ROLES, f"unknown physical face role: {role}")
        require(role not in roles, f"duplicate physical face role: {role}")
        roles[role] = record
        require(record["carrier_id"] in EXPECTED_CARRIERS,
                f"face {record['id']} has an unknown carrier")
        nonplaceholder(record["formula"], f"face {record['id']} formula")
        if role in EXPECTED_DIRECT_FACE_FORMULAS:
            require(record["formula"] == EXPECTED_DIRECT_FACE_FORMULAS[role],
                    f"face {role} reintroduces the P2d phase in a direct aperture")
        nonplaceholder(record["domain"], f"face {record['id']} domain")
        nonplaceholder(record["coorientation"],
                       f"face {record['id']} coorientation")
        require(record["physical"] is True and record["frozen"] is True,
                f"face {record['id']} is not a frozen physical face")
        expected_function = REQUIRED_FACE_ROLES[role]
        if expected_function is None:
            require(record["defining_function_id"] is None and
                    record["is_carrier_boundary"] is True,
                    f"physical saddle face {role} is not a carrier boundary")
        else:
            require(record["defining_function_id"] == expected_function and
                    record["is_carrier_boundary"] is False,
                    f"face {role} is not tied to its required interior function")
            if functions is not None:
                require(expected_function in functions,
                        f"face {role} uses an unmaterialized function")
    require(set(roles) == set(REQUIRED_FACE_ROLES),
            "physical event-face inventory is incomplete")


def validate_lists(section: dict[str, Any],
                   carriers: dict[str, dict[str, Any]] | None) -> dict[str, dict[str, Any]]:
    exact_keys(section, {"status", "records"}, "ambient-function-lists section")
    records = unique_records(section["records"], "ambient function list")
    require(set(records) == set(EXPECTED_LISTS),
            "ambient function-list inventory is incomplete")
    for identifier, (carrier_id, required_functions, maximum_q) in EXPECTED_LISTS.items():
        record = records[identifier]
        exact_keys(record, {
            "id", "carrier_id", "function_ids", "function_domains",
            "boundary_strata", "pullback_map", "disjoint_competing_overlap",
            "frozen",
        }, f"ambient function list {identifier}")
        require(record["carrier_id"] == carrier_id,
                f"ambient list {identifier} moved to another carrier")
        require(record["function_ids"] == required_functions,
                f"ambient list {identifier} changed its complete function list")
        require(set(record["function_domains"]) == set(required_functions),
                f"ambient list {identifier} lacks occurrence domains")
        for function_id, domain in record["function_domains"].items():
            nonplaceholder(domain,
                           f"ambient list {identifier} domain for {function_id}")
        q_count = len(set(required_functions) & TIME_DIFFERENCES)
        require(q_count <= maximum_q and q_count <= 1,
                f"ambient list {identifier} permits a triple competing time")
        strata = record["boundary_strata"]
        require(isinstance(strata, list) and strata and
                len(strata) == len(set(strata)),
                f"ambient list {identifier} has no boundary-stratum census")
        if carriers is not None:
            available = {item["id"] for item in carriers[carrier_id]["boundary_strata"]}
            require(set(strata) == available,
                    f"ambient list {identifier} omits a carrier boundary stratum")
        nonplaceholder(record["pullback_map"],
                       f"ambient list {identifier} pullback map")
        if carrier_id in EXPECTED_DIRECT_LIST_PULLBACKS:
            require(record["pullback_map"] ==
                    EXPECTED_DIRECT_LIST_PULLBACKS[carrier_id],
                    f"ambient list {identifier} bypasses the direct phase map")
        require(record["disjoint_competing_overlap"] is (q_count == 1),
                f"ambient list {identifier} has an incorrect overlap declaration")
        require(record["frozen"] is True,
                f"ambient list {identifier} is not frozen")
    return records


def sign_key(list_id: str, boundary_id: str,
             functions: list[str], signs: Iterable[int]) -> tuple[Any, ...]:
    return (list_id, boundary_id, *zip(functions, signs))


def validate_incidence(
        section: dict[str, Any],
        carriers: dict[str, dict[str, Any]],
        lists: dict[str, dict[str, Any]]) -> tuple[
            dict[str, dict[str, Any]], dict[str, tuple[str, set[str]]]]:
    exact_keys(section, {"status", "records"}, "incidence-complex section")
    records = unique_records(section["records"], "incidence row")
    observed: dict[tuple[Any, ...], dict[str, Any]] = {}
    components: dict[str, tuple[str, set[str]]] = {}
    for record in records.values():
        exact_keys(record, {
            "id", "list_id", "boundary_stratum_id", "sign_vector", "status",
            "expected_dimension", "component_ids", "rank_certificate_id",
            "empty_margin_id", "declared_tie",
        }, f"incidence row {record['id']}")
        list_id = record["list_id"]
        require(list_id in lists, f"incidence row {record['id']} has unknown list")
        ambient = lists[list_id]
        function_ids = ambient["function_ids"]
        sign_vector = record["sign_vector"]
        require(isinstance(sign_vector, dict) and
                list(sign_vector) == function_ids and
                all(value in (-1, 0, 1) for value in sign_vector.values()),
                f"incidence row {record['id']} has an incomplete sign vector")
        boundary_id = record["boundary_stratum_id"]
        require(boundary_id in ambient["boundary_strata"],
                f"incidence row {record['id']} has unknown boundary stratum")
        key = sign_key(list_id, boundary_id, function_ids,
                       [sign_vector[item] for item in function_ids])
        require(key not in observed,
                f"duplicate incidence sign stratum in {list_id}/{boundary_id}")
        observed[key] = record

        carrier = carriers[ambient["carrier_id"]]
        boundary = {
            item["id"]: item for item in carrier["boundary_strata"]
        }[boundary_id]
        active = {item for item, sign in sign_vector.items() if sign == 0}
        expected_dimension = (
            carrier["dimension"] - len(active)
            - len(boundary["active_boundary_function_ids"]))
        require(record["expected_dimension"] == expected_dimension,
                f"incidence row {record['id']} has the wrong expected dimension")
        require(record["status"] in {"EMPTY", "NONEMPTY"},
                f"incidence row {record['id']} has an invalid status")
        if len(active & SELECTED_APERTURES) >= 2:
            require(record["status"] == "EMPTY",
                    "selected physical channel tie was declared nonempty")
        q_active = bool(active & TIME_DIFFERENCES)
        if record["status"] == "EMPTY":
            require(record["component_ids"] == [] and
                    record["rank_certificate_id"] is None,
                    f"empty incidence row {record['id']} has nonempty geometry")
            nonplaceholder(record["empty_margin_id"],
                           f"empty incidence row {record['id']} margin")
            require(record["declared_tie"] is False,
                    f"empty incidence row {record['id']} declares a tie")
        else:
            component_ids = record["component_ids"]
            require(expected_dimension >= 0 and isinstance(component_ids, list) and
                    component_ids and len(component_ids) == len(set(component_ids)),
                    f"nonempty incidence row {record['id']} lacks components")
            require(record["empty_margin_id"] is None,
                    f"nonempty incidence row {record['id']} claims an empty gap")
            if active or boundary["active_boundary_function_ids"]:
                nonplaceholder(record["rank_certificate_id"],
                               f"incidence row {record['id']} rank certificate")
            else:
                require(record["rank_certificate_id"] is None,
                        f"open stratum {record['id']} has a spurious rank row")
            require(record["declared_tie"] is q_active,
                    f"incidence row {record['id']} mishandles a q=0 tie")
            for component_id in component_ids:
                require(component_id not in components,
                        f"component id appears in two strata: {component_id}")
                components[component_id] = (record["id"], active)

    expected_keys = set()
    for list_id, ambient in lists.items():
        for boundary_id in ambient["boundary_strata"]:
            for signs in itertools.product((-1, 0, 1),
                                           repeat=len(ambient["function_ids"])):
                expected_keys.add(sign_key(
                    list_id, boundary_id, ambient["function_ids"], signs))
    require(set(observed) == expected_keys,
            "incidence complex does not enumerate every sign/boundary stratum")
    return records, components


def validate_priority(
        section: dict[str, Any], incidence: dict[str, dict[str, Any]],
        components: dict[str, tuple[str, set[str]]]) -> dict[str, dict[str, Any]]:
    exact_keys(section, {"status", "records"}, "corner-priority section")
    records = unique_records(section["records"], "priority row")
    by_component: dict[str, dict[str, Any]] = {}
    required_components: set[str] = set()
    for component_id, (row_id, active) in components.items():
        if len(active) >= 2 or active & TIME_DIFFERENCES:
            required_components.add(component_id)
        if len(active & SELECTED_TERMINALS) >= 2:
            raise AuditError("selected physical terminal tie was declared nonempty")
        if component_id not in required_components:
            continue
        row = incidence[row_id]
        require(row["status"] == "NONEMPTY", "priority refers to an empty row")
    for record in records.values():
        exact_keys(record, {
            "id", "component_id", "active_function_ids", "outcome",
            "priority_witness_function_id",
            "selected_physical_event_function_id",
            "preserves_full_active_set", "frozen",
        }, f"priority row {record['id']}")
        component_id = record["component_id"]
        require(component_id in required_components,
                f"priority row {record['id']} is not a simultaneous component")
        require(component_id not in by_component,
                f"duplicate priority for component {component_id}")
        by_component[component_id] = record
        active = components[component_id][1]
        require(set(record["active_function_ids"]) == active,
                f"priority row {record['id']} erases simultaneous incidence data")
        require(record["outcome"] in OUTCOMES and
                record["priority_witness_function_id"] in active,
                f"priority row {record['id']} has no active witness")
        selected_event = record["selected_physical_event_function_id"]
        require(selected_event in EXPECTED_FUNCTIONS and
                selected_event not in TIME_DIFFERENCES and
                selected_event != "w_alg",
                f"priority row {record['id']} does not name a physical event")
        require(record["preserves_full_active_set"] is True and
                record["frozen"] is True,
                f"priority row {record['id']} does not retain the active set")
        if "c_stable" in active:
            require(record["outcome"] == "cut" and
                    record["priority_witness_function_id"] == "c_stable" and
                    selected_event == "c_stable",
                    "stable cut does not retain cut priority")
        else:
            active_q = active & TIME_DIFFERENCES
            if active_q:
                require(len(active_q) == 1,
                        "priority row contains more than one event-time tie")
                q_id = next(iter(active_q))
                bound_terminal = EXPECTED_TIME_DIFFERENCE_BINDINGS[q_id][1]
                require(record["outcome"] == TIME_DIFFERENCE_OUTCOMES[q_id] and
                        record["priority_witness_function_id"] == q_id and
                        selected_event == bound_terminal,
                        "pairwise time tie does not select its bound physical terminal")
            for terminal, outcome in (
                    ("g_h", "return"), ("g_alg", "alg"),
                    ("g_pole", "pole")):
                if terminal in active and active & SIDE_FUNCTIONS:
                    require(record["outcome"] == outcome and
                            record["priority_witness_function_id"] == terminal and
                            selected_event == terminal,
                            "selected terminal does not precede an auxiliary lateral")
    require(set(by_component) == required_components,
            "corner priority does not assign every simultaneous component")
    return by_component


def validate_census(
        section: dict[str, Any], lists: dict[str, dict[str, Any]],
        incidence: dict[str, dict[str, Any]],
        components: dict[str, tuple[str, set[str]]],
        priorities: dict[str, dict[str, Any]]) -> None:
    exact_keys(section, {"status", "records", "cell_complexes", "exhaustion"},
               "first-event-census section")
    records = unique_records(section["records"], "census row")
    component_rows: dict[str, dict[str, Any]] = {}
    for record in records.values():
        exact_keys(record, {
            "id", "component_id", "list_id", "outcome",
            "first_event_function_id", "cell_complex_id", "frozen",
        }, f"census row {record['id']}")
        component_id = record["component_id"]
        require(component_id in components,
                f"census row {record['id']} refers to an unknown component")
        require(component_id not in component_rows,
                f"component {component_id} receives two first-event labels")
        component_rows[component_id] = record
        incidence_row = incidence[components[component_id][0]]
        require(record["list_id"] == incidence_row["list_id"],
                f"census row {record['id']} moved between ambient lists")
        require(record["outcome"] in OUTCOMES,
                f"census row {record['id']} has an invalid outcome")
        nonplaceholder(record["first_event_function_id"],
                       f"census row {record['id']} first event")
        require(record["frozen"] is True,
                f"census row {record['id']} is not frozen")
        active = components[component_id][1]
        if "c_stable" in active:
            require(record["outcome"] == "cut",
                    "stable-cut component is not labelled cut")
        if component_id in priorities:
            require(record["outcome"] == priorities[component_id]["outcome"],
                    f"census row {record['id']} conflicts with corner priority")
            require(record["first_event_function_id"] == priorities[
                component_id]["selected_physical_event_function_id"],
                f"census row {record['id']} changed the selected physical event")
    require(set(component_rows) == set(components),
            "first-event census has a residual or duplicated component")

    complexes = unique_records(section["cell_complexes"], "cell complex")
    covered: list[str] = []
    for complex_record in complexes.values():
        exact_keys(complex_record, {
            "id", "component_ids", "box_ids", "connected_certificate_id",
            "exact_cover_certificate_id", "frozen",
        }, f"cell complex {complex_record['id']}")
        component_ids = complex_record["component_ids"]
        require(isinstance(component_ids, list) and component_ids and
                len(component_ids) == len(set(component_ids)) and
                set(component_ids) <= set(components),
                f"cell complex {complex_record['id']} has invalid components")
        boxes = complex_record["box_ids"]
        require(isinstance(boxes, list) and boxes and len(boxes) == len(set(boxes)),
                f"cell complex {complex_record['id']} has no connected box cover")
        nonplaceholder(complex_record["connected_certificate_id"],
                       f"cell complex {complex_record['id']} connectedness")
        nonplaceholder(complex_record["exact_cover_certificate_id"],
                       f"cell complex {complex_record['id']} exact cover")
        require(complex_record["frozen"] is True,
                f"cell complex {complex_record['id']} is not frozen")
        covered.extend(component_ids)
    require(len(covered) == len(set(covered)) and set(covered) == set(components),
            "connected box complexes omit or duplicate a census component")
    for record in component_rows.values():
        require(record["cell_complex_id"] in complexes and
                record["component_id"] in
                complexes[record["cell_complex_id"]]["component_ids"],
                f"census row {record['id']} has a broken cell-complex link")

    exhaustion = section["exhaustion"]
    require(isinstance(exhaustion, dict), "first-event exhaustion is missing")
    exact_keys(exhaustion, {
        "covered_list_ids", "no_residual", "no_duplicate_assignment",
        "common_face_gluing_certificate_id", "base_r0_census_certificate_id",
        "bridge_isotopy_certificate_id",
    }, "first-event exhaustion")
    require(set(exhaustion["covered_list_ids"]) == set(lists) and
            len(exhaustion["covered_list_ids"]) == len(lists),
            "first-event exhaustion omits an ambient list")
    require(exhaustion["no_residual"] is True and
            exhaustion["no_duplicate_assignment"] is True,
            "first-event exhaustion does not prove a disjoint total census")
    for key in (
            "common_face_gluing_certificate_id", "base_r0_census_certificate_id",
            "bridge_isotopy_certificate_id"):
        nonplaceholder(exhaustion[key], f"first-event exhaustion {key}")


def validate_normalization(
        section: dict[str, Any], carriers: dict[str, dict[str, Any]],
        functions: dict[str, dict[str, Any]]) -> None:
    exact_keys(section, {
        "status", "carrier_metrics", "function_scales", "time_scales",
        "phase_scale",
    }, "normalization section")
    metrics = {item.get("carrier_id"): item for item in section["carrier_metrics"]}
    require(set(metrics) == set(carriers) and
            len(metrics) == len(section["carrier_metrics"]),
            "normalization lacks one metric per carrier")
    for carrier_id, record in metrics.items():
        exact_keys(record, {
            "carrier_id", "metric", "coordinate_scales", "frozen"},
            f"carrier metric {carrier_id}")
        require(record["metric"] == "EUCLIDEAN_AFTER_AFFINE_SCALING",
                f"carrier {carrier_id} has an unrecognized metric")
        coordinates = carriers[carrier_id]["coordinates"]
        require(set(record["coordinate_scales"]) == set(coordinates),
                f"carrier {carrier_id} metric omits a coordinate scale")
        for coordinate, scale in record["coordinate_scales"].items():
            exact_fraction(scale, f"carrier {carrier_id} scale {coordinate}",
                           positive=True)
        require(record["frozen"] is True,
                f"carrier metric {carrier_id} is not frozen")

    scales = {item.get("function_id"): item for item in section["function_scales"]}
    require(set(scales) == set(functions) and
            len(scales) == len(section["function_scales"]),
            "normalization lacks one scale per defining function")
    for function_id, record in scales.items():
        exact_keys(record, {"function_id", "scale", "frozen"},
                   f"function scale {function_id}")
        exact_fraction(record["scale"], f"function scale {function_id}",
                       positive=True)
        require(record["frozen"] is True,
                f"function scale {function_id} is not frozen")

    time_scales = {item.get("carrier_id"): item for item in section["time_scales"]}
    require(set(time_scales) == set(carriers) and
            len(time_scales) == len(section["time_scales"]),
            "normalization lacks one time scale per carrier")
    for carrier_id, record in time_scales.items():
        exact_keys(record, {"carrier_id", "scale", "frozen"},
                   f"time scale {carrier_id}")
        exact_fraction(record["scale"], f"time scale {carrier_id}", positive=True)
        require(record["frozen"] is True,
                f"time scale {carrier_id} is not frozen")
    exact_fraction(section["phase_scale"], "phase scale", positive=True)


def validate_m0(section: dict[str, Any],
                components: dict[str, tuple[str, set[str]]]) -> None:
    exact_keys(section, {
        "status", "value", "definition", "margin_lowers",
        "bridge_half_bound", "simultaneous_tie_policy",
    }, "numeric-m0 section")
    m0 = exact_fraction(section["value"], "numeric m0", positive=True)
    require(section["definition"] ==
            "MINIMUM_OF_FROZEN_DIMENSIONLESS_CERTIFIED_LOWERS",
            "numeric m0 does not use the frozen normalized minimum")
    categories: dict[str, list[dict[str, Any]]] = {}
    for record in section["margin_lowers"]:
        exact_keys(record, {
            "id", "category", "status", "lower", "normalized",
            "certificate_id",
        }, f"m0 margin {record.get('id')}")
        category = record["category"]
        require(category in REQUIRED_MARGINS,
                f"m0 contains an unknown margin category: {category}")
        categories.setdefault(category, []).append(record)
        require(record["status"] in {"PRESENT", "VACUOUS"},
                f"m0 margin {record['id']} has an invalid status")
        require(record["normalized"] is True,
                f"m0 margin {record['id']} is dimensionful")
        nonplaceholder(record["certificate_id"],
                       f"m0 margin {record['id']} certificate")
        if record["status"] == "PRESENT":
            lower = exact_fraction(record["lower"],
                                   f"m0 margin {record['id']}", positive=True)
            require(lower >= m0,
                    f"m0 exceeds certified margin {record['id']}")
        else:
            require(record["lower"] is None,
                    f"vacuous m0 margin {record['id']} has a numerical lower")
    require(set(categories) == REQUIRED_MARGINS,
            "numeric m0 omits a required normalized margin category")
    bridge_half = exact_fraction(
        section["bridge_half_bound"], "m0 bridge half bound", positive=True)
    require(bridge_half >= m0 / 2,
            "bridge margin is smaller than m0/2")

    tie_components = {
        component_id for component_id, (_, active) in components.items()
        if active & TIME_DIFFERENCES
    }
    policy = section["simultaneous_tie_policy"]
    require(isinstance(policy, dict), "numeric m0 tie policy is missing")
    exact_keys(policy, {
        "nonempty_ties_use_conormal_rank_not_time_gap",
        "empty_ties_require_absolute_q_lower", "excluded_component_ids",
    }, "numeric m0 tie policy")
    require(policy["nonempty_ties_use_conormal_rank_not_time_gap"] is True and
            policy["empty_ties_require_absolute_q_lower"] is True,
            "numeric m0 claims a false gap at a simultaneous tie")
    require(set(policy["excluded_component_ids"]) == tie_components and
            len(policy["excluded_component_ids"]) == len(tie_components),
            "numeric m0 does not exclude exactly the declared tie components")


def validate_traces(section: dict[str, Any]) -> None:
    exact_keys(section, {
        "status", "records", "phase_gap_certificate_binding",
        "proper_phase_arc",
    }, "transported-traces section")
    records = unique_records(section["records"], "transported trace")
    roles = {record.get("role") for record in records.values()}
    require(roles == {
        "ALGEBRAIC_ANCHOR", "HOMOCLINIC_ANCHOR", "POLE_CLOSED_ARC",
        "RESIDUAL_PLUS", "RESIDUAL_MINUS",
    }, "transported trace inventory is incomplete")
    require(len(records) == len(roles), "transported trace roles are duplicated")
    for record in records.values():
        exact_keys(record, {
            "id", "role", "carrier_id", "coordinate_lift", "exact_enclosure",
            "certificate_id", "frozen",
        }, f"transported trace {record['id']}")
        require(record["carrier_id"] in EXPECTED_CARRIERS,
                f"trace {record['id']} has an unknown carrier")
        nonplaceholder(record["coordinate_lift"],
                       f"trace {record['id']} coordinate lift")
        require(record["coordinate_lift"] ==
                "DIRECT_P2BK_COMMON_SOURCE_PHASE_LIFT",
                f"trace {record['id']} is not in the theorem's common source phase")
        exact_interval(record["exact_enclosure"],
                       f"trace {record['id']} enclosure")
        nonplaceholder(record["certificate_id"],
                       f"trace {record['id']} certificate")
        require(record["frozen"] is True,
                f"trace {record['id']} is not frozen")

    binding = section["phase_gap_certificate_binding"]
    require(isinstance(binding, dict), "phase-gap certificate binding is missing")
    exact_keys(binding, {"path", "sha256", "required_pass_atoms"},
               "phase-gap certificate binding")
    require(SHA256_RE.fullmatch(binding["sha256"]) is not None,
            "phase-gap certificate hash is malformed")
    require(binding["required_pass_atoms"] == [
        "V2.ATLAS.PHASE_GAP_AH",
        "V2.ATLAS.PHASE_GAP_AP",
        "V2.ATLAS.PHASE_GAP_HP",
    ], "phase-gap atom list changed")
    certificate_path = repository_path(binding["path"])
    require(certificate_path.is_file(), "phase-gap certificate is missing")
    require(sha256_file(certificate_path) == binding["sha256"],
            "phase-gap certificate hash mismatch")
    certificate = load_json(certificate_path)
    atom_status = {
        item.get("id"): item.get("status")
        for item in certificate.get("obligations", [])
        if isinstance(item, dict)
    }
    for atom in binding["required_pass_atoms"]:
        require(atom_status.get(atom) == "PASS",
                f"phase-gap prerequisite {atom} is not PASS")

    arc = section["proper_phase_arc"]
    require(isinstance(arc, dict), "proper phase arc is missing")
    exact_keys(arc, {
        "lift_interval", "cut_interval", "complementary_gap_lower",
        "contains_trace_ids", "certificate_id", "frozen",
    }, "proper phase arc")
    exact_interval(arc["lift_interval"], "proper phase lift interval")
    exact_interval(arc["cut_interval"], "proper phase cut interval")
    exact_fraction(arc["complementary_gap_lower"],
                   "proper phase complementary gap", positive=True)
    require(set(arc["contains_trace_ids"]) == set(records) and
            len(arc["contains_trace_ids"]) == len(records),
            "proper phase arc omits a transported trace")
    nonplaceholder(arc["certificate_id"], "proper phase arc certificate")
    require(arc["frozen"] is True, "proper phase arc is not frozen")


def validate_numerical_method(
        section: dict[str, Any], carriers: dict[str, dict[str, Any]]) -> None:
    exact_keys(section, {
        "status", "carrier_domains", "state_partition", "ode_taylor_order",
        "precision", "high_winding_N_policy",
        "legacy_ambiguous_fields_forbidden",
    }, "numerical-method section")
    domains = {item.get("carrier_id"): item for item in section["carrier_domains"]}
    require(set(domains) == set(carriers) and
            len(domains) == len(section["carrier_domains"]),
            "numerical method lacks one exact domain per carrier")
    for carrier_id, record in domains.items():
        exact_keys(record, {"carrier_id", "coordinate_domain", "frozen"},
                   f"numerical carrier domain {carrier_id}")
        require(record["coordinate_domain"] ==
                carriers[carrier_id]["coordinate_domain"] and
                record["frozen"] is True,
                f"numerical carrier domain {carrier_id} differs from the atlas")
    partition = section["state_partition"]
    require(isinstance(partition, dict), "state partition is undefined")
    exact_keys(partition, {
        "initial_box_counts", "max_bisection_depths",
        "unresolved_box_verdict", "adaptation_after_output_forbidden",
    }, "state partition")
    for key in ("initial_box_counts", "max_bisection_depths"):
        values = partition[key]
        require(isinstance(values, dict) and set(values) == set(carriers) and
                all(isinstance(value, int) and value > 0
                    for value in values.values()),
                f"state partition {key} is not a positive per-carrier budget")
    require(partition["unresolved_box_verdict"] == "INCONCLUSIVE" and
            partition["adaptation_after_output_forbidden"] is True,
            "state-partition refinement is not fail-closed")
    require(isinstance(section["ode_taylor_order"], int) and
            2 <= section["ode_taylor_order"] <= 100,
            "CAPD Taylor order is not an explicit reasonable integer")
    require(section["precision"] == EXPECTED_EMPTY_SECTIONS[
        "numerical_method"]["precision"],
        "precision differs from the locked FILIB binary64 backend")
    require(section["high_winding_N_policy"] ==
            "NOT_A_P2E_V2_4_5_MATERIALIZATION_CHOICE",
            "a high-winding threshold was inserted into P2e")
    require(section["legacy_ambiguous_fields_forbidden"] ==
            ["D", "N", "precision"],
            "ambiguous D/N/precision policy changed")


def validate_full_run_gate(gate: dict[str, Any], *, ready: bool) -> bool:
    exact_keys(gate, {
        "status", "all_required_sections_must_equal",
        "frozen_before_first_full_run", "first_full_run_started",
        "materialization_commit", "authorized_binary_sha256",
        "budget_exhaustion_verdict",
    }, "full-run gate")
    require(gate["all_required_sections_must_equal"] == FROZEN and
            gate["budget_exhaustion_verdict"] == "INCONCLUSIVE",
            "full-run fail-closed policy changed")
    require(gate["first_full_run_started"] is False,
            "structural freeze checker cannot certify an already-started run")
    if not ready:
        require(gate == {
            "status": "PROHIBITED_BEFORE_MATERIALIZATION_FREEZE",
            "all_required_sections_must_equal": FROZEN,
            "frozen_before_first_full_run": False,
            "first_full_run_started": False,
            "materialization_commit": None,
            "authorized_binary_sha256": None,
            "budget_exhaustion_verdict": "INCONCLUSIVE",
        }, "full run was authorized while materialization is incomplete")
        return False
    require(gate["status"] == "READY_FOR_FIRST_FULL_RUN" and
            gate["frozen_before_first_full_run"] is True,
            "complete materialization lacks a prospective freeze record")
    require(isinstance(gate["materialization_commit"], str) and
            COMMIT_RE.fullmatch(gate["materialization_commit"]) is not None,
            "materialization commit is not an exact Git revision")
    require(isinstance(gate["authorized_binary_sha256"], str) and
            SHA256_RE.fullmatch(gate["authorized_binary_sha256"]) is not None,
            "authorized strict binary hash is missing")
    return True


def audit(config_path: Path = DEFAULT_CONFIG) -> dict[str, Any]:
    config = load_json(config_path)
    validate_static_contract(config)
    materialization = config["materialization"]
    exact_keys(materialization, MATERIALIZATION_NAMES, "materialization")

    missing: list[str] = []
    for name in MATERIALIZATION_NAMES:
        section = materialization[name]
        require(isinstance(section, dict), f"materialization {name} is not an object")
        status = section.get("status")
        require(status in {MISSING, FROZEN},
                f"materialization {name} has invalid status {status!r}")
        if status == MISSING:
            require(section == EXPECTED_EMPTY_SECTIONS[name],
                    f"missing materialization {name} contains unreviewed payload")
            missing.append(name)

    carriers = None
    carrier_geometry = None
    functions = None
    lists = None
    incidence = None
    components = None
    priorities = None
    if materialization["carriers"]["status"] == FROZEN:
        carriers, carrier_geometry = validate_carriers(
            materialization["carriers"])
    if materialization["defining_functions"]["status"] == FROZEN:
        functions = validate_functions(materialization["defining_functions"])
    if materialization["physical_event_faces"]["status"] == FROZEN:
        require(carriers is not None and functions is not None,
                "physical event faces were frozen before carriers/functions")
        validate_faces(materialization["physical_event_faces"], functions)
    if materialization["ambient_function_lists"]["status"] == FROZEN:
        require(carriers is not None and functions is not None,
                "ambient function lists were frozen before carriers/functions")
        lists = validate_lists(materialization["ambient_function_lists"], carriers)
    if materialization["incidence_complex"]["status"] == FROZEN:
        require(carriers is not None and lists is not None and functions is not None,
                "incidence complex was frozen before carriers/functions/lists")
        incidence, components = validate_incidence(
            materialization["incidence_complex"], carriers, lists)
    if materialization["corner_priority"]["status"] == FROZEN:
        require(incidence is not None and components is not None,
                "corner priority was frozen before the incidence complex")
        priorities = validate_priority(
            materialization["corner_priority"], incidence, components)
    if materialization["first_event_census"]["status"] == FROZEN:
        require(lists is not None and incidence is not None and
                components is not None and priorities is not None,
                "first-event census was frozen before incidence and priority")
        validate_census(
            materialization["first_event_census"], lists, incidence,
            components, priorities)
    if materialization["normalization"]["status"] == FROZEN:
        require(carriers is not None and functions is not None,
                "normalization was frozen before carriers and functions")
        validate_normalization(
            materialization["normalization"], carriers, functions)
    if materialization["numeric_m0"]["status"] == FROZEN:
        require(materialization["normalization"]["status"] == FROZEN and
                components is not None,
                "numeric m0 was frozen before normalization and incidence")
        validate_m0(materialization["numeric_m0"], components)
    if materialization["transported_traces"]["status"] == FROZEN:
        validate_traces(materialization["transported_traces"])
    if materialization["numerical_method"]["status"] == FROZEN:
        require(carriers is not None,
                "numerical method was frozen before carrier domains")
        validate_numerical_method(materialization["numerical_method"], carriers)

    ready = not missing
    full_run_authorized = validate_full_run_gate(
        config["full_run_gate"], ready=ready)
    verdict = ("READY_FOR_FIRST_FULL_RUN" if full_run_authorized
               else "STOP_BEFORE_FULL_RUN")
    stop_reason = (None if full_run_authorized
                   else (
                       "MISSING_EXECUTABLE_CORE_ATLAS_NUMERIC_M0_AND_"
                       "DIRECT_CARRIER_SEAM"))
    return {
        "schema_version": "rfsn-vdp-p2e-event-atlas-structure-gate-result/2",
        "scope": config["scope"],
        "box_id": config["box_id"],
        "comparison_bridge_id": config["comparison_bridge_id"],
        "status": verdict,
        "structure_status": "READY_TO_SCOUT_NON_EVIDENTIARY",
        "integrity_status": "STRUCTURE_SCHEMA_VALID",
        "atlas_claim_status": "PENDING",
        "mathematical_status": "INCONCLUSIVE",
        "full_run_authorized": full_run_authorized,
        "full_capd_executed": False,
        "missing_materialization_sections": missing,
        "stop_reason": stop_reason,
        "parameter_cells": 4096,
        "outgoing_phase_interface":
            "DIRECT_P2BK_OVER_P2D_EXACT_SECTION_NONCANONICAL_PAIR",
        "frozen_carrier_geometry": carrier_geometry,
        "obligations": config["obligations"],
        "claim_bearing": False,
        "release_eligible": False,
        "nonclaims": config["nonclaims"],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--pretty", action="store_true")
    arguments = parser.parse_args(argv)
    try:
        result = audit(arguments.config)
    except AuditError as error:
        print(json.dumps({
            "status": "INVALID_STRUCTURE_GATE",
            "mathematical_status": "INCONCLUSIVE",
            "full_run_authorized": False,
            "error": str(error),
        }, sort_keys=True), file=sys.stderr)
        return 2
    print(json.dumps(
        result, indent=2 if arguments.pretty else None, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
