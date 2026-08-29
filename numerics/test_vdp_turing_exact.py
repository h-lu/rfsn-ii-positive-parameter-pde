"""Independent exact-symbolic regression for the Turing exclusion theorem.

This file deliberately does not import ``numerics.vdp_turing``.  It rebuilds
the Fourier symbol from the reaction Jacobian and checks the manuscript's
algebra with SymPy exact arithmetic.  The regression guards transcription;
the proposition itself is proved analytically in the manuscript.
"""

from __future__ import annotations

import unittest

import sympy as sp


class ExactTuringRegression(unittest.TestCase):
    def setUp(self) -> None:
        self.a, self.d, self.epsilon, self.q = sp.symbols(
            "a d epsilon q", positive=True
        )
        self.alpha = self.a**2 - 1

    def test_symbol_trace_and_determinant_from_reaction_jacobian(self) -> None:
        u, v = sp.symbols("u v")
        reaction = sp.Matrix(
            [v - (u**3 / 3 - u), self.epsilon * (self.a - u)]
        )
        reaction_jacobian = reaction.jacobian((u, v)).subs(u, self.a)
        symbol = reaction_jacobian - sp.diag(self.d, 1) * self.q
        self.assertEqual(
            sp.simplify(
                sp.trace(symbol) - (-self.alpha - (1 + self.d) * self.q)
            ),
            0,
        )
        self.assertEqual(
            sp.simplify(
                symbol.det()
                - (self.d * self.q**2 + self.alpha * self.q + self.epsilon)
            ),
            0,
        )

    def test_both_stationary_neutral_branches_are_exact_zeros(self) -> None:
        r, a2, s = sp.symbols("r a2 s", positive=True)
        for branch_sign in (-1, 1):
            branch = (
                branch_sign * sp.sqrt(1 - 2 * r**2 * s) - 1
            ) / (s * r**3)
            branch_a = 1 + s * r**3 * branch
            branch_alpha = sp.expand(branch_a**2 - 1)
            q_critical = s / r**2
            determinant = (
                r**4 * q_critical**2
                + branch_alpha * q_critical
                + s**2
            )
            self.assertEqual(sp.simplify(determinant), 0)

    def test_cusp_factorization_and_frozen_box_margin_are_exact(self) -> None:
        r, a2, s = sp.symbols("r a2 s", positive=True)
        a_cusp = 1 + s * r**3 * a2
        alpha_cusp = sp.expand(a_cusp**2 - 1)
        factored = s * r**2 * (2 + 2 * r * a2 + s * r**4 * a2**2)
        self.assertEqual(sp.expand(alpha_cusp + 2 * s * r**2 - factored), 0)

        r_max = sp.Rational(2, 25)
        a2_abs_max = sp.Rational(1, 4)
        exact_linear_floor = 2 - 2 * r_max * a2_abs_max
        self.assertEqual(exact_linear_floor, sp.Rational(49, 25))


if __name__ == "__main__":
    unittest.main()
