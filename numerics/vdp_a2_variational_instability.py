"""Minimal A2 co-periodic instability calculation.

This module evaluates the one scalar inequality used by the self-adjoint
operator-pencil criterion in ``van-der-pol/A2_PERIODIC_SPECTRAL_INSTABILITY.md``.
It deliberately does not approximate a complete Bloch spectrum.  The saved
profile is floating-point evidence, so every result produced here remains
``COMPUTED/E1`` until a validated periodic shooting enclosure supplies the
same strict inequality for a true profile.
"""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = ROOT / "numerics/config/vdp_a2_periodic_spectral_v1.json"
EVIDENCE_STATUS = "COMPUTED/E1 NONRIGOROUS_A2_VARIATIONAL_INSTABILITY_SEED"


def sha256_file(path: str | Path) -> str:
    """Return the SHA-256 digest of *path*."""

    digest = hashlib.sha256()
    with Path(path).open("rb") as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(block)
    return digest.hexdigest()


def load_contract(path: str | Path = DEFAULT_CONFIG) -> dict[str, Any]:
    """Load the frozen S0 contract."""

    return json.loads(Path(path).read_text(encoding="utf-8"))


def cubic_reaction(value: np.ndarray | float) -> np.ndarray | float:
    """The physical van der Pol reaction primitive ``f(u)=u^3/3-u``."""

    return value**3 / 3.0 - value


def cubic_reaction_derivative(value: np.ndarray | float) -> np.ndarray | float:
    """Return ``f'(u)=u^2-1``."""

    return value**2 - 1.0


def pointwise_moment_identity_residual(
    value: np.ndarray | float, *, a: float
) -> np.ndarray | float:
    """Residual in the exact polynomial identity behind the criterion.

    With ``w=value-a``, the identity is

    ``-w*f(a+w)+f'(a+w)*w^2 = -f(a)*w+a*w^3+(2/3)*w^4``.
    """

    w = value - a
    left = -w * cubic_reaction(value) + cubic_reaction_derivative(value) * w**2
    right = -cubic_reaction(a) * w + a * w**3 + (2.0 / 3.0) * w**4
    return left - right


def _periodic_integral(grid: np.ndarray, values: np.ndarray) -> float:
    """Composite trapezoidal integral on an endpoint-duplicated grid."""

    return float(np.trapezoid(values, grid))


def physical_moments(
    grid: np.ndarray, profile_u: np.ndarray, *, a: float
) -> dict[str, float]:
    """Return the mean defect and second through fourth centered moments."""

    x = np.asarray(grid, dtype=np.float64)
    u = np.asarray(profile_u, dtype=np.float64)
    if x.ndim != 1 or u.shape != x.shape or x.size < 3:
        raise ValueError("grid and profile_u must be equal-length vectors")
    if not np.all(np.isfinite(x)) or not np.all(np.isfinite(u)):
        raise ValueError("grid and profile_u must be finite")
    if not np.all(np.diff(x) > 0.0):
        raise ValueError("grid must be strictly increasing")
    w = u - float(a)
    return {
        "mean_defect_integral": _periodic_integral(x, w),
        "m2": _periodic_integral(x, w**2),
        "m3": _periodic_integral(x, w**3),
        "m4": _periodic_integral(x, w**4),
    }


def _subsampled_moment_bounds(
    grid: np.ndarray, profile_u: np.ndarray, *, a: float
) -> list[dict[str, float | int]]:
    """Give floating grid-refinement evidence without treating it as an error bound."""

    interval_count = grid.size - 1
    records: list[dict[str, float | int]] = []
    for stride in (20, 10, 5, 2, 1):
        if interval_count % stride:
            continue
        moments = physical_moments(grid[::stride], profile_u[::stride], a=a)
        q0 = a * moments["m3"] + (2.0 / 3.0) * moments["m4"]
        records.append(
            {
                "stride": stride,
                "point_count": int(grid[::stride].size),
                "q0": q0,
                **moments,
            }
        )
    return records


def evaluate_a2_contract(
    config_path: str | Path = DEFAULT_CONFIG,
) -> dict[str, Any]:
    """Evaluate the frozen variational inequality on the saved A2 seed."""

    contract_path = Path(config_path)
    contract = load_contract(contract_path)
    seed = contract["profile_seed"]
    archive_path = ROOT / seed["path"]
    actual_sha = sha256_file(archive_path)
    expected_sha = str(seed["sha256"])
    if actual_sha != expected_sha:
        raise ValueError(
            f"A2 archive SHA-256 mismatch: expected {expected_sha}, got {actual_sha}"
        )

    prefix = str(seed["array_prefix"])
    with np.load(archive_path, allow_pickle=False) as archive:
        x = np.asarray(archive[f"{prefix}physical_x"], dtype=np.float64)
        u = np.asarray(archive[f"{prefix}physical_u"], dtype=np.float64)
        v = np.asarray(archive[f"{prefix}physical_v"], dtype=np.float64)
        xi = np.asarray(archive[f"{prefix}xi"], dtype=np.float64)
        central_state = np.asarray(archive[f"{prefix}state"], dtype=np.float64)

    parameters = contract["parameters"]
    target = contract["variational_instability_target"]
    a = float(parameters["a"])
    lambda_lower = float(target["lambda_lower"])
    required_upper = float(target["required_strict_upper_bound"])
    moments = physical_moments(x, u, a=a)
    q0 = a * moments["m3"] + (2.0 / 3.0) * moments["m4"]
    lambda_lower_rayleigh_numerator_upper = q0 + lambda_lower * moments["m2"]
    threshold_margin = required_upper - lambda_lower_rayleigh_numerator_upper

    central_target = contract["central_augmented_integral"]
    half_point_count = (xi.size + 1) // 2
    central_u = central_state[0, :half_point_count]
    central_xi = xi[:half_point_count]
    r = float(parameters["r"])
    central_integrand = (
        lambda_lower * central_u**2
        - r**2 * central_u**3
        + (2.0 / 3.0) * r**4 * central_u**4
    )
    central_z = _periodic_integral(central_xi, central_integrand)
    physical_from_central = 2.0 * r**5 * central_z

    refinements = _subsampled_moment_bounds(x, u, a=a)
    refinement_values = np.asarray(
        [float(row["q0"]) + lambda_lower * float(row["m2"]) for row in refinements]
    )

    return {
        "schema_version": "vdp-a2-variational-report/1",
        "status": EVIDENCE_STATUS,
        "claim_bearing": False,
        "contract": {
            "path": str(contract_path.relative_to(ROOT)),
            "schema_version": contract["schema_version"],
            "frozen_at": contract["frozen_at"],
        },
        "input": {
            "path": str(archive_path.relative_to(ROOT)),
            "sha256": actual_sha,
            "array_prefix": prefix,
            "point_count_with_duplicate_endpoint": int(x.size),
            "physical_period": float(x[-1] - x[0]),
            "endpoint_u_defect": float(u[-1] - u[0]),
            "endpoint_v_defect": float(v[-1] - v[0]),
            "endpoint_warning": (
                "The saved second half was generated by exact reversible reflection; "
                "endpoint equality is not an independent shooting validation."
            ),
        },
        "parameters": parameters,
        "moments": moments,
        "variational_criterion": {
            "q0": q0,
            "lambda_lower": lambda_lower,
            "lambda_lower_rayleigh_numerator_upper": (
                lambda_lower_rayleigh_numerator_upper
            ),
            "required_strict_upper_bound": required_upper,
            "computed_threshold_margin": threshold_margin,
            "floating_gate_pass": bool(
                lambda_lower_rayleigh_numerator_upper < required_upper < 0.0
            ),
            "lambda_upper": float(target["lambda_upper"]),
            "conditional_spectral_conclusion": target[
                "conclusion_if_validated"
            ],
        },
        "central_augmented_integral": {
            "half_period_xi": float(central_xi[-1] - central_xi[0]),
            "saved_candidate_z_at_half_period": central_z,
            "physical_M_from_central_identity": physical_from_central,
            "physical_grid_identity_defect": float(
                physical_from_central - lambda_lower_rayleigh_numerator_upper
            ),
            "required_interval_upper_bound": float(
                central_target["required_interval_upper_bound"]
            ),
            "floating_gate_pass": bool(
                central_z < float(central_target["required_interval_upper_bound"])
            ),
            "equation": central_target["half_orbit_equation"],
        },
        "floating_refinement": {
            "records": refinements,
            "maximum_lambda_lower_numerator_spread": float(
                np.ptp(refinement_values)
            ),
            "interpretation": (
                "Grid agreement is QA only; it is not an outward-rounded quadrature "
                "or profile-enclosure error bound."
            ),
        },
        "floating_fourier_crosscheck": contract["floating_spectral_crosscheck"],
        "proof_boundary": {
            "proved_analytic_implication": (
                "Any true periodic stationary profile satisfying the strict moment "
                "inequality has a real co-periodic eigenvalue in the frozen positive interval."
            ),
            "missing_for_a2_theorem": contract["completion_rule"][
                "minimal_claim_bearing_inputs"
            ],
            "nonclaims": contract["nonclaims"],
        },
    }


def write_report(report: dict[str, Any], output: str | Path) -> None:
    """Write a stable, human-readable JSON report."""

    path = Path(output)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = evaluate_a2_contract(args.config)
    if args.output is not None:
        write_report(report, args.output)
    print(json.dumps(report, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()


__all__ = [
    "DEFAULT_CONFIG",
    "EVIDENCE_STATUS",
    "cubic_reaction",
    "cubic_reaction_derivative",
    "evaluate_a2_contract",
    "load_contract",
    "physical_moments",
    "pointwise_moment_identity_residual",
    "sha256_file",
    "write_report",
]
