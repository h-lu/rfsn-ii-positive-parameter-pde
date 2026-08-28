#!/usr/bin/env python3
"""Generate exact term tables for the degree-ten unstable graph.

The homological recursion is included below and works exactly over
Q(sqrt(2)). A cached tuple may be supplied with --pickle to shorten
development runs; the checked header is independent of that cache.
"""

from __future__ import annotations

import argparse
import pickle
from pathlib import Path

import sympy as sp


def homogeneous(poly, variables, degree):
    result = sp.Integer(0)
    for powers, coefficient in sp.Poly(sp.expand(poly), *variables).terms():
        if sum(powers) != degree:
            continue
        monomial = coefficient
        for variable, power in zip(variables, powers):
            monomial *= variable**power
        result += monomial
    return result


def unstable_graph(degree):
    """Return the degree-N formal graph (s1,s2)=H_N(u1,u2)."""
    x, y = sp.symbols("x y")
    variables = (x, y)
    c = 1 / sp.sqrt(2)
    h1 = sp.Integer(0)
    h2 = sp.Integer(0)

    def defect(first, second):
        physical_u = x + first
        fu1 = c * (x - y) - c * physical_u**2 / 2
        fu2 = c * (x + y) + c * physical_u**2 / 2
        fs1 = -c * (first - second) + c * physical_u**2 / 2
        fs2 = -c * (first + second) - c * physical_u**2 / 2
        return (
            sp.expand(fs1 - sp.diff(first, x) * fu1
                      - sp.diff(first, y) * fu2),
            sp.expand(fs2 - sp.diff(second, x) * fu1
                      - sp.diff(second, y) * fu2),
        )

    for current_degree in range(2, degree + 1):
        monomials = [
            x**index * y ** (current_degree - index)
            for index in range(current_degree + 1)
        ]
        first_coefficients = sp.symbols(
            f"a{current_degree}_0:{current_degree + 1}"
        )
        second_coefficients = sp.symbols(
            f"b{current_degree}_0:{current_degree + 1}"
        )
        first_correction = sum(c0 * m for c0, m in zip(
            first_coefficients, monomials
        ))
        second_correction = sum(c0 * m for c0, m in zip(
            second_coefficients, monomials
        ))
        first_defect, second_defect = defect(
            h1 + first_correction, h2 + second_correction
        )
        equations = []
        for index in range(current_degree + 1):
            equations.extend([
                sp.expand(homogeneous(
                    first_defect, variables, current_degree
                )).coeff(x, index).coeff(y, current_degree - index),
                sp.expand(homogeneous(
                    second_defect, variables, current_degree
                )).coeff(x, index).coeff(y, current_degree - index),
            ])
        solutions = sp.solve(
            equations, first_coefficients + second_coefficients,
            dict=True, simplify=False
        )
        if len(solutions) != 1:
            raise RuntimeError(
                f"degree {current_degree}: expected one homological solve"
            )
        h1 = sp.expand(h1 + first_correction.subs(solutions[0]))
        h2 = sp.expand(h2 + second_correction.subs(solutions[0]))
    first_defect, second_defect = defect(h1, h2)
    return variables, h1, h2, first_defect, second_defect


def terms(poly, x, y, sqrt_factor=False):
    result = []
    for (px, py), coefficient in sp.Poly(poly, x, y).terms():
        if sqrt_factor:
            coefficient = sp.simplify(coefficient / sp.sqrt(2))
        if not coefficient.is_Rational:
            raise RuntimeError(f"non-rational normalized coefficient {coefficient}")
        result.append((px, py, int(coefficient.p), int(coefficient.q)))
    return result


def emit_array(name, rows, times_sqrt_two):
    lines = [f"inline constexpr PolynomialTerm {name}[] = {{"]
    flag = "true" if times_sqrt_two else "false"
    for px, py, numerator, denominator in rows:
        lines.append(
            f'  {{{px}, {py}, "{numerator}", "{denominator}", {flag}}},'
        )
    lines.append("};")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--pickle", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    if args.pickle:
        with args.pickle.open("rb") as stream:
            h1, h2 = pickle.load(stream)
        x, y = sorted(h1.free_symbols, key=str)
    else:
        (x, y), h1, h2, _defect1, _defect2 = unstable_graph(10)

    c = 1 / sp.sqrt(2)
    a = x + h1
    fu1 = c * (x - y) - c * a**2 / 2
    fu2 = c * (x + y) + c * a**2 / 2
    fs1 = -c * (h1 - h2) + c * a**2 / 2
    fs2 = -c * (h1 + h2) - c * a**2 / 2
    defect1 = sp.expand(
        fs1 - sp.diff(h1, x) * fu1 - sp.diff(h1, y) * fu2
    )
    defect2 = sp.expand(
        fs2 - sp.diff(h2, x) * fu1 - sp.diff(h2, y) * fu2
    )

    blocks = [
        "#pragma once",
        "",
        "struct PolynomialTerm {",
        "  int px;",
        "  int py;",
        "  const char* numerator;",
        "  const char* denominator;",
        "  bool times_sqrt_two;",
        "};",
        "",
        emit_array("kH1Terms", terms(h1, x, y), False),
        "",
        emit_array("kH2Terms", terms(h2, x, y), False),
        "",
        emit_array("kDefect1Terms", terms(defect1, x, y, True), True),
        "",
        emit_array("kDefect2Terms", terms(defect2, x, y, True), True),
        "",
    ]
    args.output.write_text("\n".join(blocks))


if __name__ == "__main__":
    main()
