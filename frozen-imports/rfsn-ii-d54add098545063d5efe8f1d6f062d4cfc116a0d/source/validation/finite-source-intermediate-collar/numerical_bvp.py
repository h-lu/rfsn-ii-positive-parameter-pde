"""Self-contained floating-point BVP machinery for cover seed generation.

Nothing in this module is proof data.  CAPD/FILIB validation is performed by
source_cover_probe.cpp after these centres have been generated.
"""

from __future__ import annotations

import math

import numpy as np
import sympy as sp
from scipy.integrate import solve_bvp


FOLD_U = 0.04152701249
FOLD_V = 0.10250373810


def degree_seven_graph():
    """Construct the canonical h7 exactly over Q(sqrt(2),sqrt(3))."""
    e, d, omega = sp.symbols("e d omega")
    variables = (e, d, omega)
    q = d - 2 / sp.sqrt(3)
    graph = -e / sp.sqrt(3) + omega / sp.sqrt(2)

    def homogeneous(poly, degree):
        return sp.Add(
            *[
                coefficient * e ** powers[0] * d ** powers[1] * omega ** powers[2]
                for powers, coefficient in sp.Poly(sp.expand(poly), *variables).terms()
                if sum(powers) == degree
            ]
        )

    def defect(h):
        p_dot = sp.Rational(3, 2) * h**2 - omega
        e_dot = e * h
        d_dot = sp.Rational(3, 2) * h * q - e
        omega_dot = e * q + 2 * h * (omega - 1)
        return sp.expand(
            p_dot
            - sp.diff(h, e) * e_dot
            - sp.diff(h, d) * d_dot
            - sp.diff(h, omega) * omega_dot
        )

    for degree in range(2, 8):
        monomials = [
            e**i * d**j * omega ** (degree - i - j)
            for i in range(degree + 1)
            for j in range(degree - i + 1)
        ]
        coefficients = sp.symbols(f"c{degree}_0:{len(monomials)}")
        correction = sum(c * monomial for c, monomial in zip(coefficients, monomials))
        residual = homogeneous(defect(graph + correction), degree)
        equations = [
            sp.expand(residual)
            .coeff(e, i)
            .coeff(d, j)
            .coeff(omega, degree - i - j)
            for i in range(degree + 1)
            for j in range(degree - i + 1)
        ]
        solutions = sp.solve(equations, coefficients, dict=True, simplify=False)
        if len(solutions) != 1:
            raise RuntimeError(f"degree {degree}: nonunique homological solve")
        graph = sp.expand(graph + correction.subs(solutions[0]))
    gradient = tuple(sp.diff(graph, variable) for variable in variables)
    return (
        graph,
        sp.lambdify(variables, graph, "numpy"),
        sp.lambdify(variables, gradient, "numpy"),
    )


def core(_time, state):
    return np.vstack(
        (state[1], -state[0] ** 2 - state[2], state[3], state[0])
    )


def gamma0(time):
    time = np.asarray(time)
    return np.vstack(
        (
            -time * time / 12,
            -time / 6,
            np.full_like(time, 1 / 6) - time**4 / 144,
            -time**3 / 36,
        )
    )


class BranchProblem:
    def __init__(self, h7, h7_gradient, section_e, tolerance, max_nodes):
        self.h7 = h7
        self.h7_gradient = h7_gradient
        self.section_e = float(section_e)
        self.tolerance = tolerance
        self.max_nodes = max_nodes
        self.mesh = np.linspace(0.0, 1.0, 501)

    def target(self, state):
        U, P, V, Q = state
        e = -1.0 / U
        e32 = e**1.5
        p = P * e32
        q = Q * e32
        omega = 1.0 + V * e**2
        d = q + 2.0 / np.sqrt(3.0)
        return p - self.h7(e, d, omega)

    @staticmethod
    def scaled_field(_scaled_time, state, parameters):
        return parameters[-1] * core(_scaled_time, state)

    def bootstrap_fixed_time(self, target_u, terminal_time=15.0):
        mesh_time = np.linspace(0.0, terminal_time, 601)
        values = gamma0(mesh_time)
        solution = None
        increments = max(24, int(math.ceil(abs(target_u) / 0.00075)))
        for source_u in np.linspace(0.0, target_u, increments + 1):
            values[0] += source_u - values[0, 0]

            def boundary(left, right, fixed_u=float(source_u)):
                return np.asarray(
                    [left[0] - fixed_u, left[1], left[3], self.target(right)]
                )

            solution = solve_bvp(
                core,
                boundary,
                mesh_time,
                values,
                tol=min(self.tolerance, 3e-9),
                max_nodes=self.max_nodes,
            )
            if not solution.success:
                raise RuntimeError(
                    f"fixed-time bootstrap failed at U={source_u}: {solution.message}"
                )
            mesh_time, values = solution.x, solution.y
        return solution

    def fixed_u_event(self, fixed_u, guess, parameters=None):
        if parameters is None:
            parameters = np.asarray([float(guess.y[2, 0]), 15.0])
        values = (
            guess.sol(15.0 * self.mesh)
            if guess.x[-1] > 1.000001
            else guess.sol(self.mesh)
        )

        def boundary(left, right, unknown):
            return np.asarray(
                [
                    left[1],
                    left[3],
                    left[0] - fixed_u,
                    left[2] - unknown[0],
                    -1.0 / right[0] - self.section_e,
                    self.target(right),
                ]
            )

        solution = solve_bvp(
            self.scaled_field,
            boundary,
            self.mesh,
            values,
            p=np.asarray(parameters, dtype=float),
            tol=self.tolerance,
            max_nodes=self.max_nodes,
        )
        if not solution.success:
            raise RuntimeError(
                f"fixed-U event solve failed at U={fixed_u}: {solution.message}"
            )
        return solution
