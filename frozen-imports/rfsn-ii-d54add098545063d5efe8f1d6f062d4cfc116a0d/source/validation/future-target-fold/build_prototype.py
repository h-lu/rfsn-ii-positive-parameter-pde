#!/usr/bin/env python3
"""Generate the degree-seven tail graph and multiple-shooting centres.

This is a reconnaissance/prototype generator.  The polynomial is obtained
from the invariance equation exactly over Q(sqrt(2),sqrt(3)); the BVP
centres are floating-point data and have no evidentiary status by themselves.
"""

import argparse
from pathlib import Path

import numpy as np
import sympy as sp
from scipy.integrate import solve_bvp


HERE = Path(__file__).resolve().parent
DEGREE = 7
T_FINAL = 15.0
N_SEGMENTS = 30
TARGET_US = (0.040, 0.043)


def tail_graph():
    e, d, o = sp.symbols("e d o")
    variables = (e, d, o)
    q = -2 / sp.sqrt(3) + d
    h = -e / sp.sqrt(3) + o / sp.sqrt(2)

    def homogeneous(poly, degree):
        return sp.Add(
            *[
                coefficient * e ** powers[0] * d ** powers[1] * o ** powers[2]
                for powers, coefficient in sp.Poly(sp.expand(poly), *variables).terms()
                if sum(powers) == degree
            ]
        )

    def defect(graph):
        fp = sp.Rational(3, 2) * graph**2 - o
        fe = e * graph
        fq = sp.Rational(3, 2) * graph * q - e
        fo = e * q + 2 * graph * (o - 1)
        return sp.expand(
            fp
            - (
                sp.diff(graph, e) * fe
                + sp.diff(graph, d) * fq
                + sp.diff(graph, o) * fo
            )
        )

    for degree in range(2, DEGREE + 1):
        monomials = [
            e**i * d**j * o ** (degree - i - j)
            for i in range(degree + 1)
            for j in range(degree - i + 1)
        ]
        coefficients = sp.symbols(f"c{degree}_0:{len(monomials)}")
        correction = sum(c * m for c, m in zip(coefficients, monomials))
        residual = homogeneous(defect(h + correction), degree)
        equations = [
            sp.expand(residual)
            .coeff(e, i)
            .coeff(d, j)
            .coeff(o, degree - i - j)
            for i in range(degree + 1)
            for j in range(degree - i + 1)
        ]
        solution = sp.solve(
            equations, coefficients, dict=True, simplify=False
        )
        if len(solution) != 1:
            raise RuntimeError(f"degree {degree}: expected one homological solution")
        h = sp.expand(h + correction.subs(solution[0]))

    he, hd, ho = (sp.diff(h, variable) for variable in variables)
    residual = defect(h)
    expansion = sp.expand(
        3 * h
        - e * he
        - sp.Rational(3, 2) * q * hd
        - 2 * (o - 1) * ho
    )
    return variables, h, he, hd, ho, residual, expansion


def coefficient_parts(coefficient):
    coefficient = sp.expand(coefficient)
    for radical in (1, 2, 3, 6):
        factor = sp.Integer(1) if radical == 1 else sp.sqrt(radical)
        ratio = sp.simplify(coefficient / factor)
        if ratio.is_Rational:
            return int(ratio.p), int(ratio.q), radical
    raise ValueError(f"unsupported coefficient {coefficient}")


def cpp_coefficient(coefficient):
    pieces = []
    for term in sp.Add.make_args(sp.expand(coefficient)):
        numerator, denominator, radical = coefficient_parts(term)
        piece = f"({cpp_integer(numerator)}/{cpp_integer(denominator)})"
        if radical != 1:
            piece += f"*r{radical}"
        pieces.append(piece)
    return "(" + "+".join(pieces) + ")"


def cpp_function(name, expression, variables):
    argument_names = [str(variable) for variable in variables]
    arguments = ", ".join(
        f"const S& {argument}" for argument in argument_names
    )
    lines = [f"template<class S> inline S {name}({arguments}) {{"]
    lines += [
        "  using std::sqrt;",
        "  const S r2 = sqrt(S(2));",
        "  const S r3 = sqrt(S(3));",
        "  const S r6 = sqrt(S(6));",
        "  S out = S(0);",
    ]
    for powers, coefficient in sp.Poly(sp.expand(expression), *variables).terms():
        factors = [cpp_coefficient(coefficient)]
        for symbol, power in zip(argument_names, powers):
            factors.extend([symbol] * power)
        lines.append("  out += " + "*".join(factors) + ";")
    lines += ["  return out;", "}", ""]
    return "\n".join(lines)


def cpp_integer(value):
    """Build an exact interval integer without oversized C++ literals."""
    if value < 0:
        return f"(-{cpp_integer(-value)})"
    if value <= 1_000_000_000_000:
        return f"S({value})"
    quotient, remainder = divmod(value, 1_000_000)
    return f"({cpp_integer(quotient)}*S(1000000)+S({remainder}))"


def write_graph_header(graph_data):
    variables, h, he, hd, ho, residual, expansion = graph_data
    body = [
        "#pragma once",
        "#include <cmath>",
        "",
        "// Generated exactly by build_prototype.py.",
        "namespace papera_tail {",
        cpp_function("h7", h, variables),
        cpp_function("h7_e", he, variables),
        cpp_function("h7_d", hd, variables),
        cpp_function("h7_o", ho, variables),
        cpp_function("h7_defect", residual, variables),
        cpp_function("h7_expansion", expansion, variables),
        "} // namespace papera_tail",
        "",
    ]
    (HERE / "tail_graph_generated.hpp").write_text("\n".join(body))


def write_weighted_header(graph_data):
    variables, h, _he, _hd, _ho, residual, expansion = graph_data
    e, d, o = variables
    aa, bb, zeta = sp.symbols("aa bb zeta")
    weighted_variables = (e, aa, bb, zeta)
    substitution = {
        d: e**3 * aa,
        o: e**2 / 6 + e**4 * bb,
    }
    graph = sp.expand(h.subs(substitution))
    p = graph + e**8 * zeta
    q = e**3 * aa - 2 / sp.sqrt(3)
    omega = e**2 / 6 + e**4 * bb
    e_dot = sp.expand(e * p)
    d_dot = sp.expand(sp.Rational(3, 2) * p * q - e)
    omega_dot = sp.expand(e * q + 2 * p * (omega - 1))
    shifted_omega_dot = sp.expand(omega_dot - e * e_dot / 3)
    a_dot = sp.expand(
        sp.cancel((d_dot - 3 * aa * e**2 * e_dot) / e**3)
    )
    b_dot = sp.expand(
        sp.cancel((shifted_omega_dot - 4 * bb * e**3 * e_dot) / e**4)
    )
    p_over_e = sp.expand(sp.cancel(p / e))
    weighted_defect = sp.expand(
        sp.cancel(residual.subs(substitution) / e**8)
    )
    weighted_expansion = sp.expand(expansion.subs(substitution))
    zeta_dot = sp.expand(
        weighted_defect
        + weighted_expansion * zeta
        + sp.Rational(3, 2) * e**8 * zeta**2
        - 8 * p * zeta
    )
    energy = sp.expand(
        sp.cancel((q**2 - p**2 + 2 * omega - sp.Rational(4, 3)) / e**3)
    )
    conservation = sp.expand(
        sp.diff(energy, e) * e_dot
        + sp.diff(energy, aa) * a_dot
        + sp.diff(energy, bb) * b_dot
        + sp.diff(energy, zeta) * zeta_dot
    )
    if conservation != 0:
        raise RuntimeError("weighted energy identity did not simplify to zero")
    algebraic_zeta = sp.expand(
        sp.cancel((-e / sp.sqrt(3) - graph.subs({aa: 0, bb: 0})) / e**8)
    )
    algebraic_substitution = {aa: 0, bb: 0, zeta: algebraic_zeta}
    algebraic_checks = {
        "energy": energy.subs(algebraic_substitution),
        "a_dot": a_dot.subs(algebraic_substitution),
        "b_dot": b_dot.subs(algebraic_substitution),
        "e_dot": e_dot.subs(algebraic_substitution) + e**2 / sp.sqrt(3),
        "zeta_tangency": (
            zeta_dot.subs(algebraic_substitution)
            - sp.diff(algebraic_zeta, e)
              * e_dot.subs(algebraic_substitution)
        ),
    }
    for name, expression in algebraic_checks.items():
        if sp.expand(expression) != 0:
            raise RuntimeError(
                f"weighted algebraic-reference identity {name} did not simplify to zero"
            )
    body = [
        "#pragma once",
        "#include <cmath>",
        "",
        "// Generated exactly by build_prototype.py after weighted cancellation.",
        "namespace papera_weighted_tail {",
        cpp_function("algebraic_zeta", algebraic_zeta, (e,)),
        cpp_function("p_over_e", p_over_e, weighted_variables),
        cpp_function("energy", energy, weighted_variables),
        cpp_function("e_dot", e_dot, weighted_variables),
        cpp_function("a_dot", a_dot, weighted_variables),
        cpp_function("b_dot", b_dot, weighted_variables),
        cpp_function("zeta_dot", zeta_dot, weighted_variables),
        "} // namespace papera_weighted_tail",
        "",
    ]
    (HERE / "weighted_tail_generated.hpp").write_text("\n".join(body))


def continuation_centres(h):
    h_float = sp.lambdify(sp.symbols("e d o"), h, "numpy")
    mesh = np.linspace(0.0, T_FINAL, 501)

    def gamma(t):
        return np.vstack(
            [
                -t * t / 12,
                -t / 6,
                np.full_like(t, 1 / 6) - t**4 / 144,
                -t**3 / 36,
            ]
        )

    def field(_t, z):
        return np.vstack([z[1], -z[0] ** 2 - z[2], z[3], z[0]])

    def target(z):
        U, P, V, Q = z
        ee = -1 / U
        pp = P * ee**1.5
        qq = Q * ee**1.5
        oo = 1 + V * ee**2
        return pp - h_float(ee, qq + 2 / np.sqrt(3), oo)

    solution_values = gamma(mesh)
    captured = {}
    nearby = {}
    target_set = {int(round(u * 1000)): u for u in TARGET_US}
    for u_index in range(0, max(target_set) + 1):
        u = u_index / 1000
        solution_values[0] += u - solution_values[0, 0]

        def boundary(left, right):
            return np.array([left[0] - u, left[1], left[3], target(right)])

        solution = solve_bvp(
            field,
            boundary,
            mesh,
            solution_values,
            tol=2e-10,
            max_nodes=20000,
        )
        if solution.status != 0:
            raise RuntimeError(
                f"BVP failed at u={u}: {solution.message}; "
                f"max residual={solution.rms_residuals.max()}"
            )
        mesh, solution_values = solution.x, solution.y
        if u_index in target_set:
            nodes = np.linspace(0.0, T_FINAL, N_SEGMENTS + 1)
            states = solution.sol(nodes).T
            captured[target_set[u_index]] = states
            v = states[0, 2]
            energy = -2 * u**3 / 3 - 2 * u * v
            print(
                f"u={u:.6f} v={v:.17g} E={energy:.17g} "
                f"max_residual={solution.rms_residuals.max():.3e}"
            )

        if u_index in (41, 42):
            nearby[u_index] = solution

    return captured, nearby, h_float


def fold_centres(nearby, h_float):
    mesh = np.linspace(0.0, T_FINAL, 801)
    base41 = nearby[41].sol(mesh)
    base42 = nearby[42].sol(mesh)
    tangent = (base42 - base41) / 0.001
    initial = np.vstack([base42, tangent])

    def target_and_gradient(z):
        U, P, V, Q = z
        ee = -1 / U
        root_e = np.sqrt(ee)
        e32 = ee * root_e
        pp = P * e32
        qq = Q * e32
        oo = 1 + V * ee**2
        dd = qq + 2 / np.sqrt(3)
        # The degree-seven polynomial is differentiated once symbolically
        # below through a small centred finite difference only for the
        # floating BVP seed.  The interval fold program differentiates it
        # exactly with second-order jets.
        value = pp - h_float(ee, dd, oo)
        gradient = np.empty(4)
        scale = np.maximum(1.0, np.abs(z))
        for index in range(4):
            step = 2e-6 * scale[index]
            plus = z.copy()
            minus = z.copy()
            plus[index] += step
            minus[index] -= step

            def scalar(state):
                u0, p0, v0, q0 = state
                e0 = -1 / u0
                e0_32 = e0**1.5
                return p0 * e0_32 - h_float(
                    e0,
                    q0 * e0_32 + 2 / np.sqrt(3),
                    1 + v0 * e0**2,
                )

            gradient[index] = (scalar(plus) - scalar(minus)) / (2 * step)
        return value, gradient

    def field(_t, y):
        U, P, V, Q, a, b, c, d0 = y
        return np.vstack(
            [P, -U**2 - V, Q, U, b, -2 * U * a - c, d0, a]
        )

    def boundary(left, right):
        target, target_gradient = target_and_gradient(right[:4])
        U, _P, V, _Q, a, _b, _c, d0 = left
        return np.array(
            [
                left[1],
                left[3],
                a - 1,
                left[5],
                left[7],
                target,
                target_gradient @ right[4:],
                (-2 * U**2 - 2 * V) * a - 2 * U * left[6],
            ]
        )

    solution = solve_bvp(
        field,
        boundary,
        mesh,
        initial,
        tol=3e-9,
        max_nodes=30000,
    )
    if solution.status != 0:
        raise RuntimeError(
            f"fold BVP failed: {solution.message}; "
            f"max residual={solution.rms_residuals.max()}"
        )
    nodes = np.linspace(0.0, T_FINAL, N_SEGMENTS + 1)
    states = solution.sol(nodes).T
    U, _P, V, _Q = states[0, :4]
    energy = -2 * U**3 / 3 - 2 * U * V
    print(
        f"fold u={U:.17g} v={V:.17g} E={energy:.17g} "
        f"max_residual={solution.rms_residuals.max():.3e}"
    )
    return states


def write_centres_header(captured):
    lines = [
        "#pragma once",
        "namespace papera_shooting {",
        f"constexpr int kSegments = {N_SEGMENTS};",
        f"constexpr double kFinalTime = {T_FINAL:.17g};",
        f"constexpr int kCases = {len(TARGET_US)};",
        "constexpr double kSourceU[kCases] = {"
        + ", ".join(f"{u:.17g}" for u in TARGET_US)
        + "};",
        "constexpr double kCentres[kCases][kSegments+1][4] = {",
    ]
    for u in TARGET_US:
        lines.append("  {")
        for state in captured[u]:
            lines.append(
                "    {" + ", ".join(f"{value:.17g}" for value in state) + "},"
            )
        lines.append("  },")
    lines += ["};", "} // namespace papera_shooting", ""]
    (HERE / "shooting_centres_generated.hpp").write_text("\n".join(lines))


def write_fold_header(states):
    lines = [
        "#pragma once",
        "namespace papera_fold_centres {",
        f"constexpr int kSegments = {N_SEGMENTS};",
        f"constexpr double kFinalTime = {T_FINAL:.17g};",
        "constexpr double kCentres[kSegments+1][8] = {",
    ]
    for state in states:
        lines.append(
            "  {" + ", ".join(f"{value:.17g}" for value in state) + "},"
        )
    lines += ["};", "} // namespace papera_fold_centres", ""]
    (HERE / "fold_centres_generated.hpp").write_text("\n".join(lines))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--tails-only",
        action="store_true",
        help="generate only the exact formal-tail headers",
    )
    arguments = parser.parse_args()
    graph_data = tail_graph()
    write_graph_header(graph_data)
    write_weighted_header(graph_data)
    if arguments.tails_only:
        print(f"generated exact tail files in {HERE}")
        return
    captured, nearby, h_float = continuation_centres(graph_data[1])
    write_centres_header(captured)
    fold = fold_centres(nearby, h_float)
    write_fold_header(fold)
    print(f"generated files in {HERE}")


if __name__ == "__main__":
    main()
