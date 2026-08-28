#!/usr/bin/env python3
"""Exact sparse audit for the low-order P2d Moser algebra.

The audit has no command-line inputs, reads no project files, performs no
sampling or floating-point evaluation, and emits exactly one deterministic
JSON line.  It verifies the degree-three homological solve and the resonant
degree-four block in the already frozen Kato-oriented linear coordinates.
It does *not* prove convergence of the infinite Lie normalization and hence
does not close ``V2.CHART.ANALYTIC_NORMAL_FORM``.
"""

from __future__ import annotations

from collections.abc import Callable, Iterator
from math import factorial
import json
import sys
from typing import TypeAlias


SCHEMA_VERSION = "rfsn-vdp-p2d-normal-form-exact-audit/1"
METHOD = "exact-sparse-homological-algebra-no-sampling-no-file-inputs"
INPUT_POLICY: dict[str, object] = {
    "external_files": [],
    "floating_point": False,
    "sampling": False,
}
CLAIM_BOUNDARY: dict[str, object] = {
    "claim_bearing": False,
    "exact_identity_scope_only": [
        "complex canonical coordinate and reverser dictionary",
        "degree-three normalized homological solve",
        "degree-four resonant finite sum",
        "degree-four normalized homological solve",
        "exact r=0 quartic normal-form anchor",
        "conditional formal core zero-energy coefficient comparison",
    ],
    "open_scope": [
        "infinite analytic Lie-majorant induction and tail convergence",
        "uniform positive-parameter complex domain",
        "normalizing map and inverse-map domain inclusions",
        "normalized exact primitive and its convergent gauge",
        "two external parameter derivatives of the infinite normalization",
        "outward-rounded positive-parameter coefficient bounds",
        "nonlinear zero-energy branch existence uniqueness and uniformity",
    ],
    "conditional_formal_coefficient_only": (
        "Conditional on continuation of a formal zero-energy action graph "
        "I1=-nu+c2*nu^2+..., core coefficient comparison gives c2=0; "
        "this audit constructs neither a formal nor an analytic branch."
    ),
    "local_obligation": "V2.CHART.ANALYTIC_NORMAL_FORM remains OPEN",
    "parent_obligation": "V2.EXACT_CHART remains OPEN",
    "low_order_audit_closes_atom": False,
}
EXACT_FORMULAS: dict[str, object] = {
    "complex_coordinates": {
        "z1": "conjugate(u)/sqrt(2)",
        "z2": "u/sqrt(2)",
        "w1": "v/sqrt(2)",
        "w2": "conjugate(v)/sqrt(2)",
        "fixed_change": "unitary and complex-bilinear symplectic",
        "poisson": "{z_j,w_k}=-delta_jk",
        "reverser": "R0(z,w)=(w,z)",
    },
    "quadratic_hamiltonian": (
        "H2=(alpha+i*beta)*z1*w1+(alpha-i*beta)*z2*w2"
    ),
    "actions": {
        "J1": "z1*w1=(I1-i*I2K)/2",
        "J2": "z2*w2=(I1+i*I2K)/2",
        "I1": "J1+J2",
        "I2K": "i*(J1-J2)",
    },
    "physical_U_covector": {
        "C": "(p+i*q)/2",
        "D": "(p-i*q)/2",
        "ell": (
            "sqrt(2)*D*(z1+w1)+sqrt(2)*C*(z2+w2)"
        ),
    },
    "nonlinear_blocks": {
        "gamma": "1+sqrt(epsilon)*r^3*a2",
        "eta": "sqrt(epsilon)*r^2",
        "H3": "-(gamma/3)*ell^3",
        "H4": "(eta/12)*ell^4",
        "higher_original_blocks": "assumed zero in the encoded model formula",
    },
    "homological_divisor": (
        "Delta_ab=(a1-b1)*(alpha+i*beta)"
        "+(a2-b2)*(alpha-i*beta)"
    ),
    "frozen_homological_sign": (
        "-L(chi3)+Z3=H3, Z3=0, chi3_ab=-H3_ab/Delta_ab"
    ),
    "quartic_lie_block": "K4=H4+(1/2)*{H3,chi3}",
    "quartic_generator": (
        "chi4_ab=-K4_ab/Delta_ab off resonance, Pi(chi4)=0"
    ),
    "quartic_resonant_basis": ["J1^2", "J1*J2", "J2^2"],
    "core_anchor": {
        "alpha": "1/sqrt(2)",
        "beta": "1/sqrt(2)",
        "gamma": "1",
        "eta": "0",
        "p": "sqrt(4+2*sqrt(2))/4",
        "q": "sqrt(4-2*sqrt(2))/4",
        "K20": "-1/60",
        "K11": "0",
        "K02": "-1/60",
        "Z4": "((I2K)^2-I1^2)/120",
    },
    "core_conditional_formal_zero_energy_coefficient": {
        "linear_branch": "I1=-I2K",
        "quartic_value_on_linear_branch": "0",
        "formal_ansatz": "I1=-nu+c2*nu^2+...",
        "conditional_coefficient": "c2=0",
        "scope": (
            "conditional formal coefficient comparison through action degree "
            "two only; no formal or analytic branch is constructed"
        ),
    },
}


def emit(payload: dict[str, object]) -> None:
    """Emit the sole machine-readable output line."""

    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))


def failure_payload(
    *, version: str | None, checks: dict[str, bool], error: Exception
) -> dict[str, object]:
    return {
        "backend": {"name": "sympy", "version": version},
        "checks": checks,
        "claim_boundary": CLAIM_BOUNDARY,
        "error": f"{type(error).__name__}: {error}",
        "exact_formulas": EXACT_FORMULAS,
        "input_policy": INPUT_POLICY,
        "method": METHOD,
        "schema_version": SCHEMA_VERSION,
        "status": "FAIL",
    }


def main() -> int:
    try:
        import sympy as sp
    except Exception as error:  # pragma: no cover - only without backend
        emit(failure_payload(version=None, checks={}, error=error))
        return 1

    Exponent: TypeAlias = tuple[int, int, int, int]
    Polynomial: TypeAlias = dict[Exponent, sp.Expr]
    zero_exponent: Exponent = (0, 0, 0, 0)
    checks: dict[str, bool] = {}

    def exact_zero(value: sp.Expr) -> bool:
        if value == 0:
            return True
        return sp.cancel(sp.together(value)) == 0

    def require(name: str, predicate: bool) -> None:
        if not isinstance(predicate, bool):
            raise TypeError(f"check {name!r} did not produce a Python bool")
        checks[name] = predicate

    def compositions(total: int, slots: int = 4) -> Iterator[Exponent]:
        if slots != 4:
            raise ValueError("this audit freezes four complex variables")
        for first in range(total + 1):
            for second in range(total - first + 1):
                for third in range(total - first - second + 1):
                    fourth = total - first - second - third
                    yield (first, second, third, fourth)

    def monomial(exponent: Exponent, coefficient: sp.Expr = sp.S.One) -> Polynomial:
        return {exponent: coefficient}

    def add_term(polynomial: Polynomial, exponent: Exponent, value: sp.Expr) -> None:
        if value == 0:
            return
        polynomial[exponent] = polynomial.get(exponent, sp.S.Zero) + value

    def add(*polynomials: Polynomial) -> Polynomial:
        result: Polynomial = {}
        for polynomial in polynomials:
            for exponent, coefficient in polynomial.items():
                add_term(result, exponent, coefficient)
        return result

    def scale(polynomial: Polynomial, scalar: sp.Expr) -> Polynomial:
        return {
            exponent: scalar * coefficient
            for exponent, coefficient in polynomial.items()
        }

    def multiply(left: Polynomial, right: Polynomial) -> Polynomial:
        result: Polynomial = {}
        for left_exponent, left_coefficient in left.items():
            for right_exponent, right_coefficient in right.items():
                exponent = tuple(
                    left_exponent[index] + right_exponent[index]
                    for index in range(4)
                )
                add_term(
                    result,
                    exponent,  # type: ignore[arg-type]
                    left_coefficient * right_coefficient,
                )
        return result

    def derivative(polynomial: Polynomial, index: int) -> Polynomial:
        result: Polynomial = {}
        for exponent, coefficient in polynomial.items():
            power = exponent[index]
            if power == 0:
                continue
            lowered = list(exponent)
            lowered[index] -= 1
            add_term(
                result,
                tuple(lowered),  # type: ignore[arg-type]
                power * coefficient,
            )
        return result

    def poisson(left: Polynomial, right: Polynomial) -> Polynomial:
        # {F,G}=sum_j(-F_zj G_wj+F_wj G_zj), so {z_j,w_k}=-delta_jk.
        result: Polynomial = {}
        for index in range(2):
            result = add(
                result,
                scale(
                    multiply(
                        derivative(left, index),
                        derivative(right, index + 2),
                    ),
                    -1,
                ),
                multiply(
                    derivative(left, index + 2),
                    derivative(right, index),
                ),
            )
        return result

    def polynomial_equal(left: Polynomial, right: Polynomial) -> bool:
        return all(
            exact_zero(left.get(exponent, 0) - right.get(exponent, 0))
            for exponent in set(left) | set(right)
        )

    def map_exponents(
        polynomial: Polynomial,
        mapping: Callable[[Exponent], Exponent],
        coefficient_map: Callable[[sp.Expr], sp.Expr] = lambda value: value,
    ) -> Polynomial:
        result: Polynomial = {}
        for exponent, coefficient in polynomial.items():
            add_term(result, mapping(exponent), coefficient_map(coefficient))
        return result

    def reverse_exponent(exponent: Exponent) -> Exponent:
        return (exponent[2], exponent[3], exponent[0], exponent[1])

    def conjugate_exponent(exponent: Exponent) -> Exponent:
        return (exponent[1], exponent[0], exponent[3], exponent[2])

    def reverse(polynomial: Polynomial) -> Polynomial:
        return map_exponents(polynomial, reverse_exponent)

    def real_star(polynomial: Polynomial) -> Polynomial:
        return map_exponents(polynomial, conjugate_exponent, sp.conjugate)

    def linear_power(
        degree: int, coefficient: sp.Expr, entries: tuple[sp.Expr, ...]
    ) -> Polynomial:
        result: Polynomial = {}
        for exponent in compositions(degree):
            multinomial = factorial(degree)
            for power in exponent:
                multinomial //= factorial(power)
            result[exponent] = (
                coefficient
                * multinomial
                * sp.prod(
                    entries[index] ** exponent[index]
                    for index in range(4)
                )
            )
        return result

    try:
        alpha = sp.Symbol("alpha", positive=True, real=True)
        beta = sp.Symbol("beta", positive=True, real=True)
        gamma = sp.Symbol("gamma", real=True)
        eta = sp.Symbol("eta", real=True)
        p = sp.Symbol("p", real=True)
        q = sp.Symbol("q", real=True)
        imaginary = sp.I
        sqrt_two = sp.sqrt(2)

        # This is the explicit bridge from the frozen real Kato coordinates
        # to the complex variables used by the sparse homological audit.  The
        # transpose below is algebraic, not Hermitian: the Poisson bracket is
        # complex-bilinear on the complexified polynomial algebra.
        x1, x2, y1, y2 = sp.symbols("x1 x2 y1 y2", real=True)
        real_state = sp.Matrix([x1, x2, y1, y2])
        omega_zero = sp.Matrix([
            [0, 0, -1, 0],
            [0, 0, 0, -1],
            [1, 0, 0, 0],
            [0, 1, 0, 0],
        ])
        real_reverser = sp.Matrix([
            [0, 0, 1, 0],
            [0, 0, 0, -1],
            [1, 0, 0, 0],
            [0, -1, 0, 0],
        ])
        complex_change = sp.Matrix([
            [1, -imaginary, 0, 0],
            [1, imaginary, 0, 0],
            [0, 0, 1, imaginary],
            [0, 0, 1, -imaginary],
        ]) / sqrt_two
        complex_state = complex_change * real_state
        complex_reverser = sp.Matrix([
            [0, 0, 1, 0],
            [0, 0, 0, 1],
            [1, 0, 0, 0],
            [0, 1, 0, 0],
        ])
        j_one_real = complex_state[0] * complex_state[2]
        j_two_real = complex_state[1] * complex_state[3]
        i_one_real = x1 * y1 + x2 * y2
        i_two_kato_real = x2 * y1 - x1 * y2
        complex_c = (p + imaginary * q) / 2
        complex_d = (p - imaginary * q) / 2
        ell_from_complex_dictionary = sqrt_two * (
            complex_d * (complex_state[0] + complex_state[2])
            + complex_c * (complex_state[1] + complex_state[3])
        )
        physical_u_covector = p * (x1 + y1) + q * (y2 - x2)
        require(
            "real_to_complex_matrix_dictionary_is_exact",
            exact_zero(complex_change.det() - 1)
            and all(
                exact_zero(entry)
                for entry in (
                    complex_change.conjugate().T * complex_change
                    - sp.eye(4)
                )
            )
            and all(
                exact_zero(entry)
                for entry in complex_change
                * omega_zero
                * complex_change.T
                - omega_zero
            )
            and all(
                exact_zero(entry)
                for entry in complex_change
                * real_reverser
                * complex_change.inv()
                - complex_reverser
            )
            and exact_zero(
                j_one_real
                - (i_one_real - imaginary * i_two_kato_real) / 2
            )
            and exact_zero(
                j_two_real
                - (i_one_real + imaginary * i_two_kato_real) / 2
            )
            and exact_zero(
                ell_from_complex_dictionary - physical_u_covector
            ),
        )

        variables = [
            monomial((1, 0, 0, 0)),
            monomial((0, 1, 0, 0)),
            monomial((0, 0, 1, 0)),
            monomial((0, 0, 0, 1)),
        ]
        coordinate_pair_checks = []
        anti_poisson_checks = []
        for left_index, left in enumerate(variables):
            for right_index, right in enumerate(variables):
                expected_value = -1 if right_index == left_index + 2 else 0
                if left_index >= 2:
                    expected_value = 1 if left_index == right_index + 2 else 0
                expected = (
                    monomial(zero_exponent, sp.Integer(expected_value))
                    if expected_value
                    else {}
                )
                coordinate_pair_checks.append(
                    polynomial_equal(poisson(left, right), expected)
                )
                anti_poisson_checks.append(
                    polynomial_equal(
                        reverse(poisson(left, right)),
                        scale(poisson(reverse(left), reverse(right)), -1),
                    )
                )
        require(
            "complex_poisson_coordinate_pairs_are_canonical",
            all(coordinate_pair_checks),
        )
        require(
            "standard_reverser_is_involutive_and_anti_poisson",
            all(reverse_exponent(reverse_exponent(exponent)) == exponent
                for exponent in compositions(4))
            and all(anti_poisson_checks),
        )

        lambda_one = alpha + imaginary * beta
        lambda_two = alpha - imaginary * beta
        j_one = monomial((1, 0, 1, 0))
        j_two = monomial((0, 1, 0, 1))
        i_one = add(j_one, j_two)
        i_two_kato = scale(add(j_one, scale(j_two, -1)), imaginary)
        h_two = add(scale(j_one, lambda_one), scale(j_two, lambda_two))
        h_two_actions = add(scale(i_one, alpha), scale(i_two_kato, beta))
        require(
            "quadratic_hamiltonian_is_alpha_I1_plus_beta_I2K",
            polynomial_equal(h_two, h_two_actions),
        )
        require(
            "quadratic_hamiltonian_is_real_and_reverser_invariant",
            polynomial_equal(real_star(h_two), h_two)
            and polynomial_equal(reverse(h_two), h_two),
        )

        def divisor(exponent: Exponent) -> sp.Expr:
            first_difference = exponent[0] - exponent[2]
            second_difference = exponent[1] - exponent[3]
            return (
                first_difference * lambda_one
                + second_difference * lambda_two
            )

        input_exponents = list(compositions(3)) + list(compositions(4))
        require(
            "homological_operator_is_diagonal_with_frozen_divisor",
            all(
                polynomial_equal(
                    poisson(h_two, monomial(exponent)),
                    monomial(exponent, divisor(exponent)),
                )
                for exponent in input_exponents
            ),
        )
        divisor_map = sp.Matrix([[1, 1], [1, -1]])
        require(
            "divisor_real_imaginary_integer_map_is_invertible",
            divisor_map.det() == -2
            and bool(sp.ask(sp.Q.nonzero(alpha)))
            and bool(sp.ask(sp.Q.nonzero(beta))),
        )

        def resonant(exponent: Exponent) -> bool:
            return exponent[0] == exponent[2] and exponent[1] == exponent[3]

        cubic_resonances = [
            exponent for exponent in compositions(3) if resonant(exponent)
        ]
        quartic_resonances = [
            exponent for exponent in compositions(4) if resonant(exponent)
        ]
        expected_quartic_resonances = [
            (0, 2, 0, 2),
            (1, 1, 1, 1),
            (2, 0, 2, 0),
        ]
        require(
            "resonant_kernel_is_generated_by_J1_and_J2",
            all(
                (exponent[0] - exponent[2] == 0)
                and (exponent[1] - exponent[3] == 0)
                for exponent in quartic_resonances
            )
            and quartic_resonances == expected_quartic_resonances,
        )
        require("degree_three_has_no_resonances", cubic_resonances == [])
        require(
            "degree_four_has_exactly_three_action_resonances",
            quartic_resonances == expected_quartic_resonances,
        )

        ell_entries = (
            sqrt_two * complex_d,
            sqrt_two * complex_c,
            sqrt_two * complex_d,
            sqrt_two * complex_c,
        )
        h_three = linear_power(3, -gamma / 3, ell_entries)
        h_four = linear_power(4, eta / 12, ell_entries)
        require("cubic_block_has_exactly_20_monomials", len(h_three) == 20)
        require("quartic_block_has_exactly_35_monomials", len(h_four) == 35)
        require(
            "nonlinear_input_blocks_are_real_and_reverser_invariant",
            polynomial_equal(real_star(h_three), h_three)
            and polynomial_equal(reverse(h_three), h_three)
            and polynomial_equal(real_star(h_four), h_four)
            and polynomial_equal(reverse(h_four), h_four),
        )

        chi_three: Polynomial = {}
        for exponent, coefficient in h_three.items():
            current_divisor = divisor(exponent)
            if current_divisor == 0:
                raise ZeroDivisionError(
                    f"unexpected cubic resonance at {exponent}"
                )
            chi_three[exponent] = -coefficient / current_divisor
        require(
            "cubic_generator_uses_frozen_negative_homological_sign",
            all(
                exact_zero(
                    chi_three[exponent]
                    + h_three[exponent] / divisor(exponent)
                )
                for exponent in h_three
            ),
        )
        require(
            "cubic_generator_is_real_and_reverser_anti_invariant",
            polynomial_equal(real_star(chi_three), chi_three)
            and polynomial_equal(reverse(chi_three), scale(chi_three, -1)),
        )
        h_two_chi = poisson(h_two, chi_three)
        require(
            "degree_three_is_cancelled_exactly",
            polynomial_equal(add(h_three, h_two_chi), {}),
        )

        h_three_chi = poisson(h_three, chi_three)
        k_four = add(h_four, scale(h_three_chi, sp.Rational(1, 2)))
        direct_bch_four = add(
            h_four,
            h_three_chi,
            scale(poisson(h_two_chi, chi_three), sp.Rational(1, 2)),
        )
        require(
            "quartic_BCH_block_reduces_to_H4_plus_half_bracket",
            polynomial_equal(direct_bch_four, k_four),
        )
        z_four = {
            exponent: k_four[exponent]
            for exponent in expected_quartic_resonances
        }
        require(
            "quartic_resonant_projection_has_three_action_monomials",
            set(z_four) == set(expected_quartic_resonances),
        )
        require(
            "quartic_resonant_projection_is_real_and_reverser_invariant",
            polynomial_equal(real_star(z_four), z_four)
            and polynomial_equal(reverse(z_four), z_four),
        )

        chi_four: Polynomial = {}
        for exponent, coefficient in k_four.items():
            if resonant(exponent):
                continue
            current_divisor = divisor(exponent)
            if current_divisor == 0:
                raise ZeroDivisionError(
                    "unexpected quartic nonresonant zero divisor at "
                    f"{exponent}"
                )
            chi_four[exponent] = -coefficient / current_divisor
        require(
            "quartic_generator_has_zero_resonant_projection",
            len(chi_four) == 32
            and all(not resonant(exponent) for exponent in chi_four),
        )
        require(
            "quartic_generator_is_real_and_reverser_anti_invariant",
            polynomial_equal(real_star(chi_four), chi_four)
            and polynomial_equal(reverse(chi_four), scale(chi_four, -1)),
        )
        require(
            "degree_four_is_normalized_exactly_to_Z4",
            polynomial_equal(
                add(k_four, poisson(h_two, chi_four)), z_four
            ),
        )

        root_two = sp.sqrt(2)
        anchor_p = sp.sqrt(4 + 2 * root_two) / 4
        anchor_q = sp.sqrt(4 - 2 * root_two) / 4
        anchor_substitution = {
            alpha: 1 / root_two,
            beta: 1 / root_two,
            gamma: 1,
            eta: 0,
            p: anchor_p,
            q: anchor_q,
        }
        algebraic_field = sp.QQ.algebraic_field(
            sp.I, root_two, anchor_p, anchor_q
        )

        def anchor_zero(value: sp.Expr) -> bool:
            return (
                algebraic_field.from_sympy(value.subs(anchor_substitution))
                == algebraic_field.zero
            )

        k_twenty = z_four[(2, 0, 2, 0)]
        k_eleven = z_four[(1, 1, 1, 1)]
        k_zero_two = z_four[(0, 2, 0, 2)]
        require(
            "core_anchor_quartic_action_coefficients_are_exact",
            anchor_zero(k_twenty + sp.Rational(1, 60))
            and anchor_zero(k_eleven)
            and anchor_zero(k_zero_two + sp.Rational(1, 60)),
        )

        core_z_four = {
            exponent: coefficient.subs(anchor_substitution)
            for exponent, coefficient in z_four.items()
        }
        expected_core_z_four = scale(
            add(multiply(i_two_kato, i_two_kato),
                scale(multiply(i_one, i_one), -1)),
            sp.Rational(1, 120),
        )
        require(
            "core_anchor_Z4_is_I2K_squared_minus_I1_squared_over_120",
            all(
                anchor_zero(
                    core_z_four.get(exponent, 0)
                    - expected_core_z_four.get(exponent, 0)
                )
                for exponent in set(core_z_four) | set(expected_core_z_four)
            ),
        )

        # Application-facing, but deliberately only formal: evaluate the
        # computed core Z4 on the linear zero-energy action direction and
        # compare the coefficient of nu^2 in the conditional formal ansatz
        # I1=-nu+c2*nu^2+... .  The calculation does not construct even a
        # full formal branch, let alone an analytic implicit-function branch.
        nu = sp.Symbol("nu", real=True)
        core_quadratic_coefficient = sp.Symbol(
            "core_quadratic_coefficient", real=True
        )
        reduced_core_z_four = {
            exponent: algebraic_field.to_sympy(
                algebraic_field.from_sympy(coefficient)
            )
            for exponent, coefficient in core_z_four.items()
        }
        j_one_on_linear_branch = -(1 + imaginary) * nu / 2
        j_two_on_linear_branch = (-1 + imaginary) * nu / 2
        branch_values = (
            sp.S.One,
            sp.S.One,
            j_one_on_linear_branch,
            j_two_on_linear_branch,
        )
        core_z_four_on_linear_branch = sum(
            coefficient
            * sp.prod(
                branch_values[index] ** exponent[index]
                for index in range(4)
            )
            for exponent, coefficient in reduced_core_z_four.items()
        )
        formal_i_one = -nu + core_quadratic_coefficient * nu**2
        formal_core_prefix = (
            formal_i_one / root_two
            + nu / root_two
            + (nu**2 - formal_i_one**2) / 120
        )
        formal_nu_squared_coefficient = sp.Poly(
            formal_core_prefix, nu
        ).coeff_monomial(nu**2)
        require(
            "core_conditional_formal_zero_energy_coefficient_c2_is_zero",
            exact_zero(core_z_four_on_linear_branch)
            and exact_zero(
                formal_nu_squared_coefficient
                - core_quadratic_coefficient / root_two
            )
            and not exact_zero(1 / root_two)
            and sp.solve(
                formal_nu_squared_coefficient,
                core_quadratic_coefficient,
            ) == [0],
        )
        require(
            "encoded_model_input_has_only_degree_three_and_four_blocks",
            all(sum(exponent) == 3 for exponent in h_three)
            and all(sum(exponent) == 4 for exponent in h_four),
        )

        status = "PASS" if checks and all(checks.values()) else "FAIL"
        payload: dict[str, object] = {
            "backend": {"name": "sympy", "version": sp.__version__},
            "checks": checks,
            "claim_boundary": CLAIM_BOUNDARY,
            "exact_formulas": EXACT_FORMULAS,
            "input_policy": INPUT_POLICY,
            "method": METHOD,
            "sparse_counts": {
                "cubic_input_monomials": len(h_three),
                "cubic_generator_monomials": len(chi_three),
                "quartic_input_monomials": len(h_four),
                "quartic_generator_monomials": len(chi_four),
                "quartic_resonant_monomials": len(z_four),
            },
            "schema_version": SCHEMA_VERSION,
            "status": status,
        }
        emit(payload)
        return 0 if status == "PASS" else 1
    except Exception as error:
        emit(
            failure_payload(
                version=sp.__version__, checks=checks, error=error
            )
        )
        return 1


if __name__ == "__main__":
    sys.exit(main())
