#!/usr/bin/env python3
"""Derive the P2a--P2d v2-bridge results by exact domain restriction.

This checker performs no interval integration and does not recompute sharper
enclosures.  It authenticates the frozen v1 certificates and the lightweight
P2d proof checker, proves the exact inclusion of the v2 bridge in the v1
bridge, and retains every inherited bound unchanged.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
import sys
import types
from fractions import Fraction
from pathlib import Path
from typing import Any

import jsonschema


HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[1]
sys.path.insert(0, str(HERE))

import check_p2d_chart_overlaps as p2d_overlaps  # noqa: E402
import check_p2d_normal_form_source_bounds as p2d_normal_form  # noqa: E402
import p2_homoclinic_certificate as p2c  # noqa: E402
import p2d_frame_certificate as p2d_frame  # noqa: E402


SCHEMA_VERSION = "rfsn-vdp-p2-v2-restriction-certificate/1"
SCOPE = "P2A_THROUGH_P2D_V2_BRIDGE_THEOREM_RESTRICTION"
RESTRICTION_STATUS = "RESTRICTED_LOCAL_MATHEMATICAL_PASS"
CONFIG_RELATIVE = "validation/rigorous/config/vdp_p2_v2_restriction.json"
CONFIG_PATH = REPOSITORY / CONFIG_RELATIVE
SCHEMA_RELATIVE = "validation/rigorous/p2_v2_restriction.schema.json"
SCHEMA_PATH = REPOSITORY / SCHEMA_RELATIVE
CHECKER_RELATIVE = "validation/rigorous/p2_v2_restriction.py"
HISTORICAL_CHECKER_RELATIVE = "validation/rigorous/check_certificate.py"

BASELINE_TAG = "vdp-issue7-box-v2-freeze"
BASELINE_TAG_OBJECT = "13acd7095a7fbe8bb24985acf0dd449ee6049041"
BASELINE_COMMIT = "8ba7ffc0bb2cdced0c904ff6dfa319e4a5bd9b2b"

V1_BRIDGE_RELATIVE = "validation/rigorous/config/vdp_bridge_v1.json"
V2_BRIDGE_RELATIVE = "validation/rigorous/config/vdp_bridge_v2.json"
V1_BOX_RELATIVE = "validation/rigorous/config/vdp_box_v1.json"
V2_BOX_RELATIVE = "validation/rigorous/config/vdp_box_v2.json"
OVERLAP_CONFIG_RELATIVE = "validation/rigorous/config/vdp_p2d_overlaps_v1.json"

HISTORICAL_CERTIFICATES = {
    "P2a": (
        "validation/rigorous/results/vdp_bridge_v1_p2a_local_graph.json",
        (
            "V2.WU.FRAME_BLOCK",
            "V2.WU.COARSE_GRAPH",
        ),
    ),
    "P2b0": (
        "validation/rigorous/results/vdp_bridge_v1_p2b_h10_c01.json",
        (
            "P2.H10_CENTER_EXACT",
            "V2.WU.H10_C0_TUBE",
            "V2.WU.H10_C1_TUBE",
        ),
    ),
    "P2b": (
        "validation/rigorous/results/vdp_bridge_v1_p2b_jets.json",
        (
            "P2.JETS.COEFFICIENTS",
            "V2.WU.STATE_C23",
            "V2.WU.MIXED_JETS",
            "V2.WU.WEIGHTED_HALF_ORBITS",
            "V2.WU.JETS",
            "V2.WU_GRAPH",
        ),
    ),
    "P2bK": (
        "validation/rigorous/results/vdp_bridge_v1_p2b_kato.json",
        (
            "P2.KATO.EXACT_ALGEBRA",
            "P2.KATO.RIESZ_TRANSPORT",
            "P2.KATO.FRAME_CHANGE",
            "P2.KATO.C2_LIFT",
            "P2.KATO.SOURCE_PARAMETERIZATION",
            "V2.PHASE.TRUE_SOURCE",
            "V2.PHASE.KATO_INTERFACE",
        ),
    ),
    "P2c": (
        "validation/rigorous/results/vdp_bridge_v1_p2c_homoclinic.json",
        (
            "V2.HOM.BRANCH",
            "V2.HOM.FIRST_HIT",
            "V2.HOM.TRANSVERSE",
            "V2.HOM.TAILS",
            "V2.HOM.MIDDLE_C2",
            "V2.HOMOCLINIC",
        ),
    ),
    "P2d-frame": (
        "validation/rigorous/results/vdp_bridge_v1_p2d_symplectic_frame.json",
        ("V2.CHART.SYMPLECTIC_FRAME",),
    ),
}

P2D_PROOF_SOURCES = {
    "V2.CHART.SYMPLECTIC_FRAME":
        "validation/rigorous/results/vdp_bridge_v1_p2d_symplectic_frame.json",
    "V2.CHART.ANALYTIC_NORMAL_FORM":
        "theory/EXPLICIT_GLOBAL_MOSER_MAJORANT.md",
    "V2.CHART.ZERO_ENERGY":
        "theory/EXPLICIT_ZERO_ENERGY_FIBER.md",
    "V2.CHART.EXACT_SECTIONS":
        "theory/EXPLICIT_EXACT_RADIAL_SECTIONS.md",
    "V2.CHART.WEIGHTED_PASSAGE":
        "theory/EXPLICIT_WEIGHTED_KATO_PASSAGE.md",
    "V2.CHART.PHYSICAL_SLIDES":
        "theory/EXPLICIT_PHYSICAL_SLIDES.md",
    "V2.CHART.OVERLAPS":
        "theory/EXPLICIT_FINITE_CHART_OVERLAPS.md",
    "V2.EXACT_CHART":
        "validation/rigorous/check_p2d_chart_overlaps.py",
}

P2D_ATOMS = tuple(P2D_PROOF_SOURCES)
ALL_REQUIRED_ATOMS = tuple(
    atom
    for _, atoms in HISTORICAL_CERTIFICATES.values()
    for atom in atoms
) + tuple(atom for atom in P2D_ATOMS if atom != "V2.CHART.SYMPLECTIC_FRAME")


class RestrictionError(ValueError):
    """A frozen input or exact restriction condition failed closed."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise RestrictionError(message)


def sha256_bytes(value: bytes) -> str:
    return hashlib.sha256(value).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


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
        raise RestrictionError(f"{label} is malformed: {error}") from error


def load_json(path: Path, label: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        raise RestrictionError(f"cannot read {label}: {error}") from error
    require(isinstance(value, dict), f"{label} is not a JSON object")
    return value


def git_output(*arguments: str) -> str:
    try:
        return subprocess.check_output(
            ["git", "-C", str(REPOSITORY), *arguments],
            stderr=subprocess.PIPE,
            text=True,
        ).strip()
    except subprocess.CalledProcessError as error:
        stderr = error.stderr.strip() if isinstance(error.stderr, str) else ""
        raise RestrictionError(
            f"git {' '.join(arguments)} failed: {stderr}"
        ) from error


def git_blob(commit: str, relative: str) -> bytes:
    try:
        return subprocess.check_output(
            ["git", "-C", str(REPOSITORY), "show", f"{commit}:{relative}"],
            stderr=subprocess.PIPE,
        )
    except subprocess.CalledProcessError as error:
        stderr = error.stderr.decode("utf-8", errors="replace").strip()
        raise RestrictionError(
            f"cannot read frozen Git blob {commit}:{relative}: {stderr}"
        ) from error


def load_historical_checker() -> types.ModuleType:
    """Load the authenticated baseline validator, not the extended P1 file."""

    source = git_blob(BASELINE_COMMIT, HISTORICAL_CHECKER_RELATIVE)
    module = types.ModuleType("_vdp_frozen_v1_check_certificate")
    module.__file__ = str(REPOSITORY / HISTORICAL_CHECKER_RELATIVE)
    module.__package__ = None
    exec(
        compile(
            source,
            f"{BASELINE_COMMIT}:{HISTORICAL_CHECKER_RELATIVE}",
            "exec",
        ),
        module.__dict__,
    )
    return module


def exact_interval(record: Any, label: str) -> tuple[Fraction, Fraction]:
    require(isinstance(record, dict), f"{label} is not an interval object")
    return (
        as_fraction(record.get("lower"), f"{label}.lower"),
        as_fraction(record.get("upper"), f"{label}.upper"),
    )


def variables(record: dict[str, Any], label: str) -> dict[str, tuple[Fraction, Fraction]]:
    raw = record.get("variables")
    require(isinstance(raw, dict), f"{label}.variables is missing")
    require(set(raw) == {"r", "a2", "epsilon"},
            f"{label} variable set changed")
    return {name: exact_interval(raw[name], f"{label}.{name}") for name in raw}


def obligation_statuses(certificate: dict[str, Any], label: str) -> dict[str, str]:
    result: dict[str, str] = {}
    obligations = certificate.get("obligations")
    require(isinstance(obligations, list), f"{label} obligations are missing")
    for obligation in obligations:
        require(isinstance(obligation, dict), f"{label} has a malformed obligation")
        identifier = obligation.get("id")
        status = obligation.get("status")
        require(isinstance(identifier, str) and isinstance(status, str),
                f"{label} has an unlabelled obligation")
        require(identifier not in result, f"{label} obligation {identifier} is duplicated")
        result[identifier] = status
    return result


def config_semantics(config: dict[str, Any]) -> None:
    require(config.get("schema_version") ==
            "rfsn-vdp-p2-v2-restriction-config/1",
            "restriction configuration schema changed")
    require(config.get("configuration_id") == "vdp-p2-v2-restriction-v1",
            "restriction configuration id changed")
    require(config.get("status") == "FROZEN_SOURCE_PRE_RESULT",
            "restriction configuration is not source-frozen")
    baseline = config.get("baseline")
    require(baseline == {
        "tag": BASELINE_TAG,
        "tag_object": BASELINE_TAG_OBJECT,
        "commit": BASELINE_COMMIT,
    }, "v2 baseline binding changed")
    policy = config.get("restriction_policy")
    require(policy == {
        "kind": "UNIVERSAL_THEOREM_DOMAIN_RESTRICTION",
        "retain_v1_constants_unchanged": True,
        "recompute_tighter_hulls": False,
        "reparameterize_normalized_coordinates": False,
        "new_interval_or_ode_run": False,
    }, "restriction policy changed")
    boundary = config.get("claim_boundary")
    require(boundary == {
        "mathematical_status": RESTRICTION_STATUS,
        "final_status": "INCONCLUSIVE",
        "claim_bearing": False,
        "release_eligible": False,
        "independent_replay": "1/2",
        "excluded": [
            "P1 on vdp-positive-box-v2",
            "P2e event atlas and phase order",
            "v2-specific sharper bounds or worst cells",
            "a nonempty two-chart overlap internal to the v2 bridge",
        ],
    }, "restriction claim boundary changed")
    stages = config.get("stages")
    require(isinstance(stages, list), "restriction stage table is missing")
    require(all(isinstance(item, dict) for item in stages),
            "restriction stage table contains a malformed entry")
    observed = {
        item.get("id"): (item.get("source"), tuple(item.get("atoms", ())))
        for item in stages
    }
    expected = {
        stage: (source, atoms)
        for stage, (source, atoms) in HISTORICAL_CERTIFICATES.items()
    }
    expected["P2d-proof-chain"] = (
        "validation/rigorous/check_p2d_chart_overlaps.py",
        tuple(atom for atom in P2D_ATOMS if atom != "V2.CHART.SYMPLECTIC_FRAME"),
    )
    require(len(observed) == len(stages),
            "restriction stage table contains a duplicate stage id")
    require(observed == expected, "restriction stage/atom table changed")
    require(len(ALL_REQUIRED_ATOMS) == len(set(ALL_REQUIRED_ATOMS)),
            "the required restriction atom list contains duplicates")


def authenticate_baseline(config: dict[str, Any]) -> list[dict[str, str]]:
    require(git_output("rev-parse", f"refs/tags/{BASELINE_TAG}") ==
            BASELINE_TAG_OBJECT, "baseline annotated-tag object changed")
    require(git_output("rev-parse", f"{BASELINE_TAG}^{{commit}}") ==
            BASELINE_COMMIT, "baseline tag no longer peels to the frozen commit")
    require(git_output("rev-parse", f"{BASELINE_COMMIT}^{{commit}}") ==
            BASELINE_COMMIT, "baseline commit is unavailable")
    head = git_output("rev-parse", "HEAD")
    ancestor = subprocess.run(
        ["git", "-C", str(REPOSITORY), "merge-base", "--is-ancestor",
         BASELINE_COMMIT, head],
        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
    )
    require(ancestor.returncode == 0,
            "the restriction source is not descended from the v2 freeze")

    bindings = config.get("source_bindings")
    require(isinstance(bindings, list) and bindings,
            "restriction source bindings are missing")
    required_paths = {
        V1_BRIDGE_RELATIVE, V2_BRIDGE_RELATIVE, V1_BOX_RELATIVE,
        V2_BOX_RELATIVE, OVERLAP_CONFIG_RELATIVE,
        *(source for source, _ in HISTORICAL_CERTIFICATES.values()),
        HISTORICAL_CHECKER_RELATIVE,
        "validation/rigorous/p2_homoclinic_certificate.py",
        "validation/rigorous/p2d_frame_certificate.py",
        "validation/rigorous/check_p2d_normal_form_source_bounds.py",
        "validation/rigorous/check_p2d_zero_energy.py",
        "validation/rigorous/check_p2d_exact_sections.py",
        "validation/rigorous/check_p2d_weighted_passage.py",
        "validation/rigorous/check_p2d_physical_slides.py",
        "validation/rigorous/check_p2d_chart_overlaps.py",
        "validation/rigorous/design/p2d_normal_form_scout.py",
        "validation/rigorous/audit_p2d_normal_form_exact.py",
        "validation/rigorous/audit_p2d_exact_chart.py",
        "validation/rigorous/config/vdp_p2_jets_v1.json",
        "validation/rigorous/config/vdp_p2_kato_v1.json",
        "validation/rigorous/config/vdp_p2_homoclinic_v1.json",
        "validation/rigorous/config/vdp_p2d_physical_slides_v1.json",
        *P2D_PROOF_SOURCES.values(),
    }
    observed_paths: set[str] = set()
    authenticated: list[dict[str, str]] = []
    for binding in bindings:
        require(isinstance(binding, dict), "a restriction binding is malformed")
        relative = binding.get("path")
        expected_hash = binding.get("sha256")
        role = binding.get("role")
        require(isinstance(relative, str) and isinstance(expected_hash, str)
                and isinstance(role, str), "a restriction binding is incomplete")
        require(relative not in observed_paths,
                f"duplicate restriction binding: {relative}")
        observed_paths.add(relative)
        baseline_hash = sha256_bytes(git_blob(BASELINE_COMMIT, relative))
        historical_validator = (
            relative == HISTORICAL_CHECKER_RELATIVE and
            role == "historical-validator-baseline"
        )
        if historical_validator:
            require(baseline_hash == expected_hash,
                    f"source is not the frozen baseline blob: {relative}")
            current_blob = "SUPERSEDED_BY_V2_COMPATIBLE_VALIDATOR"
        else:
            current_hash = sha256_file(REPOSITORY / relative)
            require(current_hash == expected_hash,
                    f"current source binding changed: {relative}")
            require(baseline_hash == expected_hash,
                    f"source is not the frozen baseline blob: {relative}")
            current_blob = "MATCH"
        authenticated.append({
            "path": relative,
            "role": role,
            "sha256": expected_hash,
            "baseline_blob": "MATCH",
            "current_blob": current_blob,
        })
    require(observed_paths == required_paths,
            "restriction source-binding path set changed")

    self_binding = config.get("generated_source_bindings")
    require(isinstance(self_binding, dict),
            "generated restriction source bindings are missing")
    require(self_binding.get("checker") == {
        "path": CHECKER_RELATIVE,
        "sha256": sha256_file(Path(__file__).resolve()),
    }, "restriction checker self-binding changed")
    require(self_binding.get("result_schema") == {
        "path": SCHEMA_RELATIVE,
        "sha256": sha256_file(SCHEMA_PATH),
    }, "restriction result-schema binding changed")
    return authenticated


def domain_restriction() -> tuple[dict[str, Any], dict[str, tuple[Fraction, Fraction]]]:
    v1_bridge = load_json(REPOSITORY / V1_BRIDGE_RELATIVE, "v1 bridge")
    v2_bridge = load_json(REPOSITORY / V2_BRIDGE_RELATIVE, "v2 bridge")
    v1_box = load_json(REPOSITORY / V1_BOX_RELATIVE, "v1 box")
    v2_box = load_json(REPOSITORY / V2_BOX_RELATIVE, "v2 box")
    source = variables(v1_bridge, "v1 bridge")
    target = variables(v2_bridge, "v2 bridge")
    old_box = variables(v1_box, "v1 box")
    new_box = variables(v2_box, "v2 box")
    require(source == {
        "r": (Fraction(0), Fraction(2, 25)),
        "a2": (Fraction(-1, 4), Fraction(1, 4)),
        "epsilon": (Fraction(4, 5), Fraction(6, 5)),
    }, "v1 bridge endpoints changed")
    require(target == {
        "r": (Fraction(0), Fraction(1, 50)),
        "a2": (Fraction(-1, 4), Fraction(1, 4)),
        "epsilon": (Fraction(4, 5), Fraction(6, 5)),
    }, "v2 bridge endpoints changed")
    require(new_box == {
        "r": (Fraction(1, 100), Fraction(1, 50)),
        "a2": target["a2"],
        "epsilon": target["epsilon"],
    }, "v2 positive box endpoints changed")
    require(old_box["r"] == (Fraction(1, 25), Fraction(2, 25)),
            "v1 positive box endpoints changed")
    for name in source:
        require(source[name][0] <= target[name][0] <= target[name][1]
                <= source[name][1], f"v2 bridge is not contained in v1: {name}")
        require(target[name][0] <= new_box[name][0] <= new_box[name][1]
                <= target[name][1], f"v2 box is not contained in v2 bridge: {name}")
    require(target["a2"] == source["a2"] and
            target["epsilon"] == source["epsilon"],
            "v2 transverse ranges differ from v1")
    require(v1_bridge.get("anchor_face") == v2_bridge.get("anchor_face"),
            "the v1/v2 anchor faces differ")
    require(old_box["r"][0] > new_box["r"][1],
            "the v1 and v2 positive radial boxes unexpectedly overlap")

    theta_v2 = (25 * target["r"][0] - 1,
                25 * target["r"][1] - 1)
    theta_box = (25 * new_box["r"][0] - 1,
                 25 * new_box["r"][1] - 1)
    require(theta_v2 == (Fraction(-1), Fraction(-1, 2)),
            "the inherited v1 theta_r interval for v2 changed")
    require(theta_box == (Fraction(-3, 4), Fraction(-1, 2)),
            "the inherited v1 theta_r interval for the v2 box changed")
    return ({
        "source_bridge": {
            "path": V1_BRIDGE_RELATIVE,
            "sha256": sha256_file(REPOSITORY / V1_BRIDGE_RELATIVE),
            "variables": v1_bridge["variables"],
        },
        "restricted_bridge": {
            "path": V2_BRIDGE_RELATIVE,
            "sha256": sha256_file(REPOSITORY / V2_BRIDGE_RELATIVE),
            "variables": v2_bridge["variables"],
        },
        "source_positive_box": {
            "path": V1_BOX_RELATIVE,
            "sha256": sha256_file(REPOSITORY / V1_BOX_RELATIVE),
            "variables": v1_box["variables"],
            "inheritance": "NOT_INHERITED_DISJOINT_FROM_V2_TARGET",
        },
        "restricted_positive_box": {
            "path": V2_BOX_RELATIVE,
            "sha256": sha256_file(REPOSITORY / V2_BOX_RELATIVE),
            "variables": v2_box["variables"],
        },
        "relations": {
            "restricted_bridge_is_strict_subset": True,
            "transverse_ranges_equal": True,
            "anchor_face_equal": True,
            "restricted_positive_box_is_subset": True,
            "source_and_restricted_positive_boxes_are_disjoint": True,
        },
        "inherited_parameter_normalization": {
            "formulas": [
                "theta_r=25*r-1",
                "theta_a=4*a2",
                "theta_epsilon=5*(epsilon-1)",
            ],
            "v2_bridge_theta_r": {
                "lower": rational(theta_v2[0]),
                "upper": rational(theta_v2[1]),
            },
            "v2_box_theta_r": {
                "lower": rational(theta_box[0]),
                "upper": rational(theta_box[1]),
            },
            "reparameterized": False,
        },
    }, target)


def authenticate_historical_certificates(
        target: dict[str, tuple[Fraction, Fraction]],
        ) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    historical = load_historical_checker()
    authentication: list[dict[str, Any]] = []
    atoms: list[dict[str, Any]] = []
    for stage, (relative, required_atoms) in HISTORICAL_CERTIFICATES.items():
        path = REPOSITORY / relative
        certificate = load_json(path, f"{stage} certificate")
        if stage in {"P2a", "P2b0", "P2b", "P2bK"}:
            errors = historical.check_certificate(path, REPOSITORY)
            validator = "check_certificate.check_certificate"
        elif stage == "P2c":
            errors = p2c.schema_errors(certificate) + \
                p2c.semantic_errors(certificate, REPOSITORY)
            validator = "p2_homoclinic_certificate.schema_errors+semantic_errors"
        else:
            # The original frame semantic checker records an absolute build
            # argv and is therefore intentionally not relocatable to a Git
            # worktree.  Validate its schema, exact bytes, embedded raw stdout,
            # source hashes, bridge, grid, margins, and exact audit through the
            # relocation-safe downstream authenticator used by every later
            # P2d child.
            errors = p2d_frame.certificate_schema_errors(certificate)
            try:
                p2d_normal_form.authenticate_frame_source(
                    certificate, sha256_file(path))
            except Exception as error:
                errors.append(f"relocation-safe frame authentication: {error}")
            validator = (
                "p2d_frame_certificate.certificate_schema_errors+"
                "check_p2d_normal_form_source_bounds.authenticate_frame_source"
            )
        require(not errors, f"{stage} recursive certificate audit failed: {'; '.join(errors)}")
        require(certificate.get("integrity_status") == "PASS" and
                certificate.get("mathematical_status") == "PASS",
                f"{stage} is not a local mathematical/integrity PASS")
        require(certificate.get("claim_bearing") is False and
                certificate.get("release_eligible") is False,
                f"{stage} historical claim boundary changed")
        replay = certificate.get("independent_replay", {})
        require(replay.get("observed_distinct_machines") == 1 and
                replay.get("required_distinct_machines") == 2 and
                replay.get("status") == "PENDING_REQUIRED",
                f"{stage} historical replay boundary changed")
        cert_bridge = variables(certificate.get("continuation_bridge", {}),
                                f"{stage} certificate bridge")
        require(cert_bridge == {
            "r": (Fraction(0), Fraction(2, 25)),
            "a2": (Fraction(-1, 4), Fraction(1, 4)),
            "epsilon": (Fraction(4, 5), Fraction(6, 5)),
        }, f"{stage} certificate is not on the v1 bridge")
        for name in cert_bridge:
            require(cert_bridge[name][0] <= target[name][0] and
                    target[name][1] <= cert_bridge[name][1],
                    f"{stage} does not contain the v2 {name} interval")
        statuses = obligation_statuses(certificate, stage)
        if stage == "P2d-frame":
            chart_status = certificate.get("chart_status", {})
            require(chart_status.get("V2.CHART.SYMPLECTIC_FRAME") == "PASS",
                    "P2d frame chart atom is not PASS")
        for atom in required_atoms:
            require(statuses.get(atom) == "PASS",
                    f"{stage} source atom {atom} is not PASS")
            atoms.append({
                "id": atom,
                "stage": stage,
                "source": relative,
                "source_sha256": sha256_file(path),
                "source_status": "PASS",
                "restriction_status": RESTRICTION_STATUS,
                "restriction_kind": "UNIVERSAL_STATEMENT_ON_SUPERSET",
                "constants": "INHERITED_UNCHANGED",
            })
        authentication.append({
            "stage": stage,
            "path": relative,
            "sha256": sha256_file(path),
            "source_commit": certificate.get("source_revision", {}).get("commit"),
            "validator": validator,
            "validator_status": "PASS",
            "integrity_status": certificate["integrity_status"],
            "mathematical_status": certificate["mathematical_status"],
            "claim_bearing": False,
            "independent_replay": "1/2",
        })
    return authentication, atoms


def grid_restrictions(certificates: dict[str, dict[str, Any]]) -> list[dict[str, Any]]:
    records: list[dict[str, Any]] = []
    for stage, subdivisions, extra, expected_cells in (
        ("P2b", [16, 8, 4, 2], 2, 256),
        ("P2bK", [16, 8, 4], 1, 128),
        ("P2d-frame", [16, 8, 4], 1, 128),
    ):
        grid = certificates[stage].get("raw_probe", {}).get("grid", {})
        require(grid.get("subdivisions") == subdivisions,
                f"{stage} grid subdivisions changed")
        selected = 4
        cell_count = selected * 8 * 4 * extra
        require(cell_count == expected_cells, f"{stage} v2 cell count changed")
        records.append({
            "stage": stage,
            "source_r_subdivisions": 16,
            "selected_r_indices": list(range(selected)),
            "selected_cell_count": cell_count,
            "role": "ALIGNMENT_CHECK_ONLY_NO_RECOMPUTED_HULL",
        })
    p2c_certificate = certificates["P2c"]
    grid = p2c_certificate.get("raw_evidence", {}).get(
        "branch_cover", {}).get("grid_geometry", {})
    require(grid.get("r_cells") ==
            "R_i=[i/400,(i+1)/400], 0<=i<32",
            "P2c exact r-cell formula changed")
    cells = 8 * 128 * 4
    faces = {
        "r": 7 * 128 * 4,
        "a2": 8 * 127 * 4,
        "epsilon": 8 * 128 * 3,
    }
    require(cells == 4096 and sum(faces.values()) == 10720,
            "P2c restricted complex counts changed")
    records.append({
        "stage": "P2c",
        "source_r_subdivisions": 32,
        "selected_r_indices": list(range(8)),
        "restricted_positive_target_r_indices": list(range(4, 8)),
        "selected_cell_count": cells,
        "selected_internal_face_count": sum(faces.values()),
        "selected_internal_faces_by_axis": faces,
        "role": "ALIGNMENT_CHECK_ONLY_NO_RECOMPUTED_HULL",
    })
    return records


def overlap_restriction(
        target: dict[str, tuple[Fraction, Fraction]]) -> dict[str, Any]:
    config = load_json(REPOSITORY / OVERLAP_CONFIG_RELATIVE,
                       "P2d overlap configuration")
    cover = config.get("normalized_parameter_cover", {})
    members = cover.get("members")
    require(isinstance(members, list) and len(members) == 2,
            "the v1 overlap cover does not have two members")
    by_id = {item.get("id"): item for item in members if isinstance(item, dict)}
    require(set(by_id) == {"anchor", "positive"},
            "the v1 overlap member ids changed")

    theta = (25 * target["r"][0] - 1, 25 * target["r"][1] - 1)
    anchor_v = (
        as_fraction(by_id["anchor"]["V_theta_r"]["lower"], "anchor V lower"),
        as_fraction(by_id["anchor"]["V_theta_r"]["upper"], "anchor V upper"),
    )
    anchor_u = (
        as_fraction(by_id["anchor"]["U_theta_r"]["lower"], "anchor U lower"),
        as_fraction(by_id["anchor"]["U_theta_r"]["upper"], "anchor U upper"),
    )
    positive_v = (
        as_fraction(by_id["positive"]["V_theta_r"]["lower"], "positive V lower"),
        as_fraction(by_id["positive"]["V_theta_r"]["upper"], "positive V upper"),
    )
    positive_u = (
        as_fraction(by_id["positive"]["U_theta_r"]["lower"], "positive U lower"),
        as_fraction(by_id["positive"]["U_theta_r"]["upper"], "positive U upper"),
    )
    require(anchor_v[0] <= theta[0] <= theta[1] <= anchor_v[1],
            "the anchor chart does not cover the v2 bridge")
    require(anchor_u[0] <= theta[0] <= theta[1] < anchor_u[1],
            "the v2 bridge is not in the anchor extension domain")
    require(theta[1] < positive_v[0] and theta[1] < positive_u[0],
            "a positive v1 chart member unexpectedly meets the v2 bridge")
    old_overlap = (max(anchor_v[0], positive_v[0]),
                   min(anchor_v[1], positive_v[1]))
    require(old_overlap == (Fraction(0), Fraction(1, 4)) and
            theta[1] < old_overlap[0],
            "the v1 nonempty overlap is not disjoint from v2")
    common = config.get("common_chart", {})
    require(common.get(
        "all_cover_members_are_restrictions_of_one_normalized_family") is True,
        "the v1 charts are not restrictions of one global family")
    require(common.get("cover_overlap_transition") == "identity" and
            common.get("cover_overlap_inverse") == "identity",
            "the v1 transition identities changed")
    return {
        "v2_theta_r": {"lower": rational(theta[0]), "upper": rational(theta[1])},
        "nonempty_v2_members": ["anchor"],
        "anchor_member_covers_v2": True,
        "positive_member_intersects_v2": False,
        "v1_nonempty_overlap_theta_r": {
            "lower": rational(old_overlap[0]),
            "upper": rational(old_overlap[1]),
        },
        "v1_nonempty_overlap_intersects_v2": False,
        "transition_obligation_on_v2": "VACUOUS_SINGLE_ANCHOR_CHART",
        "parent_exact_chart_basis":
            "RESTRICTION_OF_ONE_GLOBAL_NORMALIZED_MOSER_FAMILY",
        "nonclaim":
            "The v1 two-member nonempty overlap and its collar are not relabelled as a v2-internal overlap.",
    }


def authenticate_p2d_chain() -> tuple[dict[str, Any], list[dict[str, Any]]]:
    try:
        report = p2d_overlaps.build_report()
    except Exception as error:  # fail closed across the nested checker types
        raise RestrictionError(f"P2d proof-chain replay failed: {error}") from error
    statuses = report.get("local_chart_status")
    require(report.get("status") == "PASS" and
            report.get("mathematical_status") == "LOCAL_MATHEMATICAL_PASS",
            "P2d terminal checker is not a local mathematical PASS")
    require(report.get("claim_bearing") is False and
            report.get("release_eligible") is False and
            report.get("independent_replay") == "1/2",
            "P2d terminal claim/replay boundary changed")
    require(isinstance(statuses, dict), "P2d terminal chart-status table is missing")
    for atom in P2D_ATOMS:
        require(statuses.get(atom) == "PASS",
                f"P2d terminal atom {atom} is not PASS")
    atoms = []
    for atom in P2D_ATOMS:
        if atom == "V2.CHART.SYMPLECTIC_FRAME":
            continue
        source = P2D_PROOF_SOURCES[atom]
        atoms.append({
            "id": atom,
            "stage": "P2d-proof-chain",
            "source": source,
            "source_sha256": sha256_file(REPOSITORY / source),
            "source_status": "PASS",
            "restriction_status": RESTRICTION_STATUS,
            "restriction_kind": (
                "SINGLE_ANCHOR_CHART_VACUOUS_TRANSITION"
                if atom == "V2.CHART.OVERLAPS" else
                "ALL_SEVEN_RESTRICTED_CHILDREN"
                if atom == "V2.EXACT_CHART" else
                "UNIVERSAL_STATEMENT_ON_SUPERSET"
            ),
            "constants": "INHERITED_UNCHANGED",
        })
    return ({
        "terminal_checker": "validation/rigorous/check_p2d_chart_overlaps.py",
        "terminal_checker_sha256": sha256_file(
            REPOSITORY / "validation/rigorous/check_p2d_chart_overlaps.py"),
        "terminal_report_sha256": sha256_bytes(canonical_json(report).encode("utf-8")),
        "status": report["status"],
        "mathematical_status": report["mathematical_status"],
        "local_chart_status": statuses,
        "claim_bearing": False,
        "independent_replay": "1/2",
    }, atoms)


def schema_errors(certificate: dict[str, Any]) -> list[str]:
    schema = load_json(SCHEMA_PATH, "restriction result schema")
    validator = jsonschema.Draft202012Validator(schema)
    return [
        f"{'.'.join(str(part) for part in error.absolute_path) or '<root>'}: "
        f"{error.message}"
        for error in sorted(validator.iter_errors(certificate),
                            key=lambda item: tuple(str(part) for part in item.path))
    ]


def build_certificate(config_path: Path = CONFIG_PATH) -> dict[str, Any]:
    config = load_json(config_path, "restriction configuration")
    config_semantics(config)
    source_authentication = authenticate_baseline(config)
    domains, target = domain_restriction()
    certificates = {
        stage: load_json(REPOSITORY / relative, f"{stage} certificate")
        for stage, (relative, _) in HISTORICAL_CERTIFICATES.items()
    }
    historical_authentication, atoms = authenticate_historical_certificates(target)
    grid = grid_restrictions(certificates)
    overlap = overlap_restriction(target)
    p2d_authentication, p2d_atoms = authenticate_p2d_chain()
    atoms.extend(p2d_atoms)
    require(tuple(item["id"] for item in atoms) == ALL_REQUIRED_ATOMS,
            "derived atom order or coverage changed")

    config_hash = sha256_file(config_path)
    certificate = {
        "schema_version": SCHEMA_VERSION,
        "certificate_id": f"vdp-p2-v2-restriction-{config_hash[:12]}",
        "scope": SCOPE,
        "restriction_status": RESTRICTION_STATUS,
        "source_freeze": {
            "tag": BASELINE_TAG,
            "tag_object": BASELINE_TAG_OBJECT,
            "commit": BASELINE_COMMIT,
        },
        "configuration": {
            "path": CONFIG_RELATIVE,
            "sha256": config_hash,
            "configuration_id": config["configuration_id"],
            "status": config["status"],
        },
        "checker": config["generated_source_bindings"]["checker"],
        "result_schema": config["generated_source_bindings"]["result_schema"],
        "domains": domains,
        "source_authentication": source_authentication,
        "historical_certificate_authentication": historical_authentication,
        "p2d_proof_chain_authentication": p2d_authentication,
        "grid_restrictions": grid,
        "p2d_overlap_restriction": overlap,
        "atoms": atoms,
        "restriction_principle": {
            "logic":
                "A uniform mathematical statement on the v1 bridge remains true on its exact v2 subset.",
            "interval_monotonicity_assumed": False,
            "new_numerical_enclosures_claimed": False,
            "all_v1_constants_retained_unchanged": True,
            "parameter_reparameterization": False,
        },
        "integrity_status": "PASS",
        "mathematical_status": RESTRICTION_STATUS,
        "independent_replay": {
            "required_distinct_machines": 2,
            "observed_distinct_machines": 1,
            "status": "PENDING_REQUIRED",
        },
        "final_status": "INCONCLUSIVE",
        "claim_bearing": False,
        "release_eligible": False,
        "nonclaims": [
            "This restriction certificate does not validate P1 on vdp-positive-box-v2.",
            "It does not validate the P2e event atlas or phase ordering.",
            "It does not create tighter v2 enclosures, margins, or worst-cell claims.",
            "It does not turn one-machine historical evidence into independent replay.",
            "It does not claim that the v1 nonempty two-chart overlap lies inside v2.",
        ],
    }
    errors = schema_errors(certificate)
    require(not errors, "derived restriction certificate violates schema: " +
            "; ".join(errors))
    return certificate


def check_result(path: Path, config_path: Path = CONFIG_PATH) -> list[str]:
    try:
        observed = load_json(path, "restriction result")
        errors = schema_errors(observed)
        if errors:
            return errors
        expected = build_certificate(config_path)
        if observed != expected:
            return ["restriction result differs from deterministic reconstruction"]
        return []
    except (OSError, RestrictionError, json.JSONDecodeError,
            subprocess.SubprocessError) as error:
        return [str(error)]


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    build = subparsers.add_parser("build", help="emit the deterministic certificate")
    build.add_argument("--configuration", type=Path, default=CONFIG_PATH)
    build.add_argument("--output", type=Path)
    check = subparsers.add_parser("check", help="reconstruct and check a result")
    check.add_argument("result", type=Path)
    check.add_argument("--configuration", type=Path, default=CONFIG_PATH)
    arguments = parser.parse_args(argv)
    try:
        if arguments.command == "check":
            errors = check_result(arguments.result.resolve(),
                                  arguments.configuration.resolve())
            if errors:
                for error in errors:
                    print(f"INVALID: {error}", file=sys.stderr)
                return 1
            print(
                "VALID: P2a--P2d restricted local mathematical PASS; "
                "final_status=INCONCLUSIVE; claim_bearing=false"
            )
            return 0
        certificate = build_certificate(arguments.configuration.resolve())
        output = canonical_json(certificate)
        if arguments.output is None:
            sys.stdout.write(output)
        else:
            arguments.output.parent.mkdir(parents=True, exist_ok=True)
            arguments.output.write_text(output, encoding="utf-8")
            print(
                f"wrote {arguments.output}: {RESTRICTION_STATUS}; "
                "claim_bearing=false"
            )
        return 0
    except (OSError, RestrictionError, json.JSONDecodeError,
            subprocess.SubprocessError, KeyError, TypeError) as error:
        print(f"RESTRICTION INPUT REJECTED: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
