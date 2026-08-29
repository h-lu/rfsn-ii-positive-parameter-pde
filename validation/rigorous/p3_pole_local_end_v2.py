#!/usr/bin/env python3
"""One-shot analytic-majorant validation of the frozen v2 pole end block."""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
from dataclasses import dataclass
from fractions import Fraction as F
from pathlib import Path
from typing import Any

import sympy as sp


HERE = Path(__file__).resolve().parent
REPOSITORY = HERE.parents[1]
CONFIG = HERE / "config" / "vdp_p3_pole_local_end_v2.json"
BOX = HERE / "config" / "vdp_box_v2.json"
OUTPUT = HERE / "results" / "vdp_box_v2_p3_pole_local_end.json"


@dataclass(frozen=True)
class I:
    lo: F
    hi: F

    def __post_init__(self) -> None:
        if self.lo > self.hi:
            raise ValueError("reversed interval")

    @classmethod
    def point(cls, value: F | int) -> "I":
        value = F(value)
        return cls(value, value)

    @classmethod
    def symmetric(cls, radius: F) -> "I":
        return cls(-radius, radius)

    def __add__(self, other: "I" | F | int) -> "I":
        other = as_i(other)
        return I(self.lo + other.lo, self.hi + other.hi)

    __radd__ = __add__

    def __neg__(self) -> "I":
        return I(-self.hi, -self.lo)

    def __sub__(self, other: "I" | F | int) -> "I":
        return self + (-as_i(other))

    def __rsub__(self, other: "I" | F | int) -> "I":
        return as_i(other) - self

    def __mul__(self, other: "I" | F | int) -> "I":
        other = as_i(other)
        products = (
            self.lo * other.lo, self.lo * other.hi,
            self.hi * other.lo, self.hi * other.hi,
        )
        return I(min(products), max(products))

    __rmul__ = __mul__

    def reciprocal(self) -> "I":
        if self.lo <= 0 <= self.hi:
            raise ZeroDivisionError("interval contains zero")
        return I(min(1 / self.lo, 1 / self.hi),
                 max(1 / self.lo, 1 / self.hi))

    def __truediv__(self, other: "I" | F | int) -> "I":
        return self * as_i(other).reciprocal()

    def __pow__(self, exponent: int) -> "I":
        if exponent < 0:
            return (self.reciprocal()) ** (-exponent)
        result = I.point(1)
        base = self
        power = exponent
        while power:
            if power & 1:
                result = result * base
            base = base * base
            power //= 2
        return result

    def abs_upper(self) -> F:
        return max(abs(self.lo), abs(self.hi))


def as_i(value: I | F | int) -> I:
    return value if isinstance(value, I) else I.point(F(value))


def q(value: F) -> dict[str, str]:
    nearest = float(value)
    return {
        "lower_hex": math.nextafter(nearest, -math.inf).hex(),
        "upper_hex": math.nextafter(nearest, math.inf).hex(),
        "endpoint_format": "OUTWARD_BINARY64_HEX",
    }


def qi(value: I) -> dict[str, str]:
    lower = math.nextafter(float(value.lo), -math.inf)
    upper = math.nextafter(float(value.hi), math.inf)
    return {
        "lower_hex": lower.hex(),
        "upper_hex": upper.hex(),
        "endpoint_format": "OUTWARD_BINARY64_HEX",
    }


def frac(item: dict[str, str]) -> F:
    return F(int(item["numerator"]), int(item["denominator"]))


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


# A polynomial is a finite sum coeff[p,q] sigma^p (log sigma)^q.
Poly = dict[tuple[int, int], sp.Expr]


def padd(*polys: Poly) -> Poly:
    result: Poly = {}
    for poly in polys:
        for key, value in poly.items():
            result[key] = sp.expand(result.get(key, 0) + value)
    return {key: value for key, value in result.items() if value != 0}


def pscale(poly: Poly, scalar: sp.Expr) -> Poly:
    return {key: sp.expand(scalar * value) for key, value in poly.items()
            if value != 0}


def pmul(left: Poly, right: Poly) -> Poly:
    result: Poly = {}
    for (p1, q1), c1 in left.items():
        for (p2, q2), c2 in right.items():
            key = (p1 + p2, q1 + q2)
            result[key] = sp.expand(result.get(key, 0) + c1 * c2)
    return {key: sp.expand(value) for key, value in result.items()
            if sp.expand(value) != 0}


def pd(poly: Poly) -> Poly:
    result: Poly = {}
    for (power, log_power), coefficient in poly.items():
        result[(power, log_power)] = sp.expand(
            result.get((power, log_power), 0) + power * coefficient
        )
        if log_power:
            result[(power, log_power - 1)] = sp.expand(
                result.get((power, log_power - 1), 0)
                + log_power * coefficient
            )
    return {key: value for key, value in result.items() if value != 0}


def pintegrate(poly: Poly) -> Poly:
    result: Poly = {}
    for (power, log_power), coefficient in poly.items():
        if power <= -1:
            raise ValueError("nonintegrable monomial")
        n = power + 1
        factorial = 1
        for k in range(log_power + 1):
            if k:
                factorial *= log_power - k + 1
            target = (n, log_power - k)
            term = coefficient * (-1) ** k * factorial / F(n ** (k + 1))
            result[target] = sp.expand(result.get(target, 0) + term)
    return {key: value for key, value in result.items() if value != 0}


def pshift(poly: Poly, amount: int) -> Poly:
    return {(power + amount, log_power): coefficient
            for (power, log_power), coefficient in poly.items()}


def pdiff(poly: Poly, symbol: sp.Symbol) -> Poly:
    return {key: sp.diff(value, symbol) for key, value in poly.items()
            if sp.diff(value, symbol) != 0}


def eval_expr(expression: sp.Expr, env: dict[sp.Symbol, I]) -> I:
    if expression.is_Rational:
        return I.point(F(int(expression.p), int(expression.q)))
    if expression.is_Integer:
        return I.point(F(int(expression)))
    if expression.is_Symbol:
        return env[expression]
    if expression.is_Add:
        result = I.point(0)
        for term in expression.args:
            result += eval_expr(term, env)
        return result
    if expression.is_Mul:
        result = I.point(1)
        for factor in expression.args:
            result *= eval_expr(factor, env)
        return result
    if expression.is_Pow and expression.exp.is_Integer:
        return eval_expr(expression.base, env) ** int(expression.exp)
    raise TypeError(f"unsupported exact coefficient: {expression}")


def eval_poly(poly: Poly, sigma: F, log_sigma: I,
              env: dict[sp.Symbol, I]) -> I:
    result = I.point(0)
    for (power, log_power), coefficient in poly.items():
        result += (eval_expr(coefficient, env) * sigma**power
                   * log_sigma**log_power)
    return result


def poly_norm(poly: Poly, sigma0: F, p_upper: F,
              env: dict[sp.Symbol, I]) -> F:
    """Bound |poly|/[sigma^5(1+|log sigma|)^2] on (0,sigma0]."""
    total = F(0)
    for (power, log_power), coefficient in poly.items():
        if power < 5 or (power == 5 and log_power > 2):
            raise ValueError(f"residual is outside the claimed weight: {(power, log_power)}")
        if log_power > 2 and power - 5 < log_power - 2:
            raise ValueError(
                f"unproved power-log monotonicity: {(power, log_power)}"
            )
        log_factor = p_upper ** max(log_power - 2, 0)
        total += (eval_expr(coefficient, env).abs_upper()
                  * sigma0 ** (power - 5) * log_factor)
    return total


def poly_sup(poly: Poly, sigma0: F, p_upper: F,
             env: dict[sp.Symbol, I]) -> F:
    return sum(
        eval_expr(coefficient, env).abs_upper()
        * sigma0**power * p_upper**log_power
        for (power, log_power), coefficient in poly.items()
    )


def ln10_interval(terms: int = 160) -> I:
    """Exact atanh-series enclosure: log(10)=2*atanh(9/11)."""
    x = F(9, 11)
    partial = sum(x ** (2 * k + 1) / (2 * k + 1) for k in range(terms))
    lower = 2 * partial
    remainder = 2 * x ** (2 * terms + 1) / ((2 * terms + 1) * (1 - x*x))
    return I(lower, lower + remainder)


def determinant(matrix: list[list[I]]) -> I:
    total = I.point(0)
    for permutation in itertools.permutations(range(4)):
        inversions = sum(permutation[i] > permutation[j]
                         for i in range(4) for j in range(i + 1, 4))
        term = I.point(-1 if inversions % 2 else 1)
        for row, column in enumerate(permutation):
            term *= matrix[row][column]
        total += term
    return total


def build_polynomials() -> tuple[Poly, Poly, Poly, dict[str, sp.Symbol]]:
    D, H, E, A, Z, W, C = sp.symbols("D H E A Z W C")
    HI = 1 / H
    x2 = D**2 / 6
    x3 = Z * HI * D**2 / 4
    m2 = -E * D**2 / 10
    m1 = W * HI * D**2 / 5 + 6 * E * D**2 / 25
    jet: Poly = {
        (2, 0): x2, (3, 0): x3,
        (4, 2): m2, (4, 1): m1, (4, 0): C,
    }
    integral_h_over_s = pintegrate(pshift(jet, -1))
    w_poly = padd({(0, 0): W, (1, 0): A * E},
                  pscale(integral_h_over_s, -H * E))
    z_poly = padd({(0, 0): Z},
                  pscale(pintegrate(padd(w_poly, {(0, 0): H * E})), -1))
    dj = pd(jet)
    lj = padd(pd(pd(jet)), pscale(pd(jet), -3), pscale(jet, -4))
    forcing = padd(
        pscale(pmul(jet, jet), 6),
        pscale(pmul(pmul(jet, jet), jet), 2),
        {(2, 0): -D**2},
        pscale(pshift(jet, 2), -D**2),
        pscale(pshift(z_poly, 3), -HI * D**2),
        {(4, 1): -E * D**2},
    )
    residual = padd(forcing, pscale(lj, -1))
    offending = {key: value for key, value in residual.items() if key[0] < 5}
    if offending:
        raise ValueError(
            f"displayed resonant jet failed its exact cancellations: {offending}"
        )
    return jet, w_poly, z_poly, {
        "D": D, "H": H, "E": E,
        "A": A, "Z": Z, "W": W, "C": C,
        "residual": residual, "DJ": dj, "D2J": pd(dj),
    }


def build_certificate() -> dict[str, Any]:
    config = json.loads(CONFIG.read_text(encoding="utf-8"))
    box = json.loads(BOX.read_text(encoding="utf-8"))
    sigma = frac(config["section"]["sigma0"])
    M = frac(config["remainder_ball"]["C0_radius"])
    p_upper = F(29)
    ln10 = ln10_interval()
    log_sigma = I(-12 * ln10.hi, -12 * ln10.lo)
    if 1 - log_sigma.lo > p_upper:
        raise ValueError("frozen logarithmic majorant is too small")

    variables = box["variables"]
    rlo = frac(variables["r"]["lower"])
    rhi = frac(variables["r"]["upper"])
    epslo = frac(variables["epsilon"]["lower"])
    epshi = frac(variables["epsilon"]["upper"])
    delta_lo, delta_hi = rlo**2, rhi**2
    ell_lo, ell_hi = F(12, 5) * delta_lo, F(5, 2) * delta_hi
    adev = F(11, 5_000_000)

    jet, w_poly, z_poly, symbols = build_polynomials()
    label_box = config["label_rectangle"]
    env = {
        symbols["D"]: I(1 / delta_hi, 1 / delta_lo),
        symbols["H"]: I(ell_lo, ell_hi),
        symbols["E"]: I(epslo, epshi),
        symbols["A"]: I(1 - adev, 1 + adev),
        symbols["Z"]: I(frac(label_box["Z0"]["lower"]),
                         frac(label_box["Z0"]["upper"])),
        symbols["W"]: I(frac(label_box["W0"]["lower"]),
                         frac(label_box["W0"]["upper"])),
        symbols["C"]: I(frac(label_box["c4"]["lower"]),
                         frac(label_box["c4"]["upper"])),
    }
    residual: Poly = symbols["residual"]  # type: ignore[assignment]
    residual_norm = poly_norm(residual, sigma, p_upper, env)
    jet_sup = poly_sup(jet, sigma, p_upper, env)
    weight_at_section = sigma**5 * p_upper**2
    Dmax = env[symbols["D"]].hi
    Emax = env[symbols["E"]].hi
    linear = (
        12 * jet_sup + 6 * jet_sup**2 + sigma**2 * Dmax**2
        + Emax * Dmax**2 * F(37, 540) * sigma**4
    )
    nonlinear_quadratic = (6 + 6 * jet_sup) * M**2 * weight_at_section
    nonlinear_cubic = 2 * M**3 * weight_at_section**2
    self_map_rhs = residual_norm + linear * M + nonlinear_quadratic + nonlinear_cubic
    contraction = (
        linear + 12 * (1 + jet_sup) * M * weight_at_section
        + 6 * M**2 * weight_at_section**2
    )
    self_map_pass = self_map_rhs < M
    contraction_gate = frac(config["acceptance_gates"]["contraction_upper_strict"])
    contraction_pass = contraction < contraction_gate

    label_derivative_input: dict[str, F] = {}
    label_polys: dict[str, Poly] = {}
    for name, symbol in (("c4", symbols["C"]),
                         ("Z0", symbols["Z"]),
                         ("W0", symbols["W"])):
        jtheta = pdiff(jet, symbol)
        etheta = pdiff(residual, symbol)
        jsup = poly_sup(jtheta, sigma, p_upper, env)
        partial_input = (
            poly_norm(etheta, sigma, p_upper, env)
            + 12 * (1 + jet_sup) * jsup * M
            + 6 * jsup * M**2 * weight_at_section
        )
        label_derivative_input[name] = partial_input / (1 - contraction)
        label_polys[name] = jtheta

    # Section enclosures for the exact fixed point and its first label jets.
    J = eval_poly(jet, sigma, log_sigma, env)
    DJ = eval_poly(symbols["DJ"], sigma, log_sigma, env)  # type: ignore[arg-type]
    D2J = eval_poly(symbols["D2J"], sigma, log_sigma, env)  # type: ignore[arg-type]
    h = J + I.symmetric(M * weight_at_section)
    Dh = DJ + I.symmetric(6 * M * weight_at_section)
    D2h = D2J + I.symmetric(27 * M * weight_at_section)
    Wbase = eval_poly(w_poly, sigma, log_sigma, env)
    Zbase = eval_poly(z_poly, sigma, log_sigma, env)
    HEmax = ell_hi * epshi
    Wstate = Wbase + I.symmetric(HEmax * F(37, 125) * M * weight_at_section)
    Zstate = Zbase + I.symmetric(
        HEmax * F(37, 540) * M * sigma * weight_at_section
    )

    htheta: dict[str, I] = {}
    Dhtheta: dict[str, I] = {}
    Wtheta: dict[str, I] = {}
    Ztheta: dict[str, I] = {}
    for name, symbol in (("c4", symbols["C"]),
                         ("Z0", symbols["Z"]),
                         ("W0", symbols["W"])):
        bound = label_derivative_input[name]
        jtheta = label_polys[name]
        htheta[name] = (
            eval_poly(jtheta, sigma, log_sigma, env)
            + I.symmetric(bound * weight_at_section)
        )
        Dhtheta[name] = (
            eval_poly(pd(jtheta), sigma, log_sigma, env)
            + I.symmetric(6 * bound * weight_at_section)
        )
        Wtheta[name] = (
            eval_poly(pdiff(w_poly, symbol), sigma, log_sigma, env)
            + I.symmetric(HEmax * F(37, 125) * bound * weight_at_section)
        )
        Ztheta[name] = (
            eval_poly(pdiff(z_poly, symbol), sigma, log_sigma, env)
            + I.symmetric(
                HEmax * F(37, 540) * bound * sigma * weight_at_section
            )
        )

    # Rows u,p are divided by ell/sigma^2 and ell*delta/sigma^3;
    # the c4 column is divided by sigma^5.  The resulting determinant is
    # exactly the full physical coordinate determinant/(ell^2*delta).
    one = I.point(1)
    row_u = [
        Dh - one - h,
        htheta["c4"] / sigma**4,
        sigma * htheta["Z0"],
        sigma * htheta["W0"],
    ]
    row_p = [
        3 * Dh - D2h - 2 - 2 * h,
        (htheta["c4"] - Dhtheta["c4"]) / sigma**4,
        sigma * (htheta["Z0"] - Dhtheta["Z0"]),
        sigma * (htheta["W0"] - Dhtheta["W0"]),
    ]
    row_v = [
        -Wstate + env[symbols["H"]] * env[symbols["E"]] * log_sigma,
        Ztheta["c4"] / sigma**5,
        Ztheta["Z0"],
        Ztheta["W0"],
    ]
    row_q = [
        env[symbols["A"]] * env[symbols["E"]]
        - env[symbols["H"]] * env[symbols["E"]] * (1 + h) / sigma,
        Wtheta["c4"] / sigma**5,
        Wtheta["Z0"],
        Wtheta["W0"],
    ]
    scaled_determinant = determinant([row_u, row_p, row_v, row_q])
    determinant_gate = frac(
        config["acceptance_gates"]["full_scaled_coordinate_jacobian_abs_lower_strict"]
    )
    determinant_abs_lower = (
        min(abs(scaled_determinant.lo), abs(scaled_determinant.hi))
        if not (scaled_determinant.lo <= 0 <= scaled_determinant.hi) else F(0)
    )
    determinant_pass = determinant_abs_lower > determinant_gate
    local_status = (
        "LOCAL_C1_BLOCK_PASS" if self_map_pass and contraction_pass and determinant_pass
        else "INCONCLUSIVE"
    )

    return {
        "schema_version": "rfsn-vdp-p3-pole-local-end-result/1",
        "configuration_id": config["configuration_id"],
        "configuration_sha256": sha(CONFIG),
        "status": local_status,
        "mathematical_status": "PARTIAL_LOCAL_PASS" if local_status.endswith("PASS") else "INCONCLUSIVE",
        "claim_bearing": False,
        "frozen_domain": {
            "sigma0": q(sigma),
            "label_rectangle": config["label_rectangle"],
            "remainder_C0_radius": q(M),
        },
        "regular_singular_spectra": {
            "desingularized_flow_spectrum": ["-1", "-4", "0", "0", "+1"],
            "normalized_power_spectrum": ["-1", "0", "0", "1", "4"],
            "conversion": "a desingularized-flow eigenvalue lambda corresponds to the power sigma^(-lambda)",
            "admissible_positive_power_roots": ["1", "4"],
        },
        "analytic_majorant": {
            "log_sigma_interval": qi(log_sigma),
            "green_operator_exact_majorant": q(F(103, 108)),
            "green_operator_norm_upper": q(F(1)),
            "displayed_jet_sup": q(jet_sup),
            "normalized_residual_upper": q(residual_norm),
            "self_map_rhs_upper": q(self_map_rhs),
            "self_map_margin": q(M - self_map_rhs),
            "contraction_upper": q(contraction),
            "contraction_margin_to_one_half": q(contraction_gate - contraction),
            "label_remainder_input_norms": {
                name: q(value) for name, value in label_derivative_input.items()
            },
        },
        "section_enclosures": {
            "h": qi(h), "D_h": qi(Dh), "D2_h": qi(D2h),
            "W": qi(Wstate), "Z": qi(Zstate),
        },
        "full_coordinate_jacobian": {
            "normalization": "det D_(sigma,c4,Z0,W0)(u,p,v,q)/(ell^2*delta)",
            "interval": qi(scaled_determinant),
            "absolute_lower": q(determinant_abs_lower),
            "required_strict_lower": q(determinant_gate),
            "status": "PASS" if determinant_pass else "INCONCLUSIVE",
        },
        "atoms": [
            {"id": "V3.POLE_TAIL.LOCAL_C0_SELF_MAP", "status": "PASS" if self_map_pass else "INCONCLUSIVE"},
            {"id": "V3.POLE_TAIL.LOCAL_C0_CONTRACTION", "status": "PASS" if contraction_pass else "INCONCLUSIVE"},
            {"id": "V3.POLE_TAIL.LOCAL_C1_LABEL_JETS", "status": "PASS" if contraction_pass else "INCONCLUSIVE"},
            {"id": "V3.POLE_TAIL.LOCAL_COORDINATE_JACOBIAN", "status": "PASS" if determinant_pass else "INCONCLUSIVE"},
        ],
        "parent_obligations": [
            {"id": "V3.SOURCE_TO_POLE", "status": "INCONCLUSIVE"},
            {"id": "V3.POLE_TAIL", "status": "INCONCLUSIVE",
             "reason": "The local block does not yet enclose mixed parameter two-jets or the C2 action-density remainder, and no global source image is shown to arrive in the frozen label rectangle."},
        ],
        "nonclaims": [
            "This local end block is conditional on membership in the frozen label rectangle.",
            "No source-to-label arrival, mixed parameter C2 remainder, or action finite-part tail is passed.",
            "The parent V3.POLE_TAIL obligation remains INCONCLUSIVE even when every local atom passes.",
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
            raise SystemExit("stored local pole-end result is stale")
    else:
        args.output.write_text(rendered, encoding="utf-8")
    print(certificate["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
