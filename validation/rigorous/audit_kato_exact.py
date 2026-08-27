#!/usr/bin/env python3
"""Exact symbolic audit for the frozen P2bK Kato interface.

This program deliberately performs no floating-point evaluation and no
sampling.  Every successful check is an identity in an exact rational or
algebraic function field (with the indicated defining relations imposed by
exact polynomial remainder).  It prints exactly one deterministic JSON line.
"""

from __future__ import annotations

import json
import sys


SCHEMA_VERSION = "rfsn-vdp-p2-kato-exact-audit/1"


def emit(payload: dict[str, object]) -> None:
    """Emit the sole machine-readable output line."""

    print(json.dumps(payload, sort_keys=True, separators=(",", ":")))


def main() -> int:
    try:
        import sympy as sp
    except Exception as error:  # pragma: no cover - exercised only if missing
        emit({
            "backend": {"name": "sympy", "version": None},
            "checks": {},
            "error": f"{type(error).__name__}: {error}",
            "schema_version": SCHEMA_VERSION,
            "status": "FAIL",
        })
        return 1

    checks: dict[str, bool] = {}

    def exact_zero(value: sp.Expr) -> bool:
        """Test equality to zero using exact symbolic normalization only."""

        return sp.cancel(sp.trigsimp(sp.simplify(value))) == 0

    def exact_matrix_zero(value: sp.MatrixBase) -> bool:
        return all(exact_zero(entry) for entry in value)

    def remainder(
        value: sp.Expr, variable: sp.Symbol, relation: sp.Expr
    ) -> sp.Expr:
        """Reduce a rational expression modulo one monic exact relation."""

        numerator, denominator = sp.fraction(sp.together(value))
        reduced = sp.rem(
            sp.Poly(numerator, variable), sp.Poly(relation, variable)
        ).as_expr()
        return sp.cancel(reduced / denominator)

    def matrix_zero_mod(
        value: sp.MatrixBase,
        variable: sp.Symbol,
        relation: sp.Expr,
    ) -> bool:
        return all(
            exact_zero(remainder(entry, variable, relation)) for entry in value
        )

    def matrix_nonzero_mod(
        value: sp.MatrixBase,
        variable: sp.Symbol,
        relation: sp.Expr,
    ) -> bool:
        return any(
            not exact_zero(remainder(entry, variable, relation))
            for entry in value
        )

    def require(name: str, predicate: bool) -> None:
        if not isinstance(predicate, bool):
            raise TypeError(f"check {name!r} did not produce a Python bool")
        checks[name] = predicate

    def make_a(c_value: sp.Expr) -> sp.MutableDenseMatrix:
        return sp.Matrix([
            [0, 1, 0, 0],
            [c_value, 0, -1, 0],
            [0, 0, 0, 1],
            [1, 0, 0, 0],
        ])

    try:
        identity4 = sp.eye(4)
        sqrt_two = sp.sqrt(2)

        # ------------------------------------------------------------------
        # Riesz projector, spectral labels, reverser, and Kato commutator.
        # We use c=4*alpha^2-2, exactly equivalent to
        # alpha=sqrt(2+c)/2 on its declared positive branch.
        # ------------------------------------------------------------------
        alpha = sp.symbols("alpha", positive=True, nonzero=True)
        c = 4 * alpha**2 - 2
        a_matrix = make_a(c)
        projector = identity4 / 2 + (
            a_matrix + a_matrix.inv()
        ) / (4 * alpha)
        reverser = sp.diag(1, -1, 1, -1)
        kato_m = sp.Matrix([
            [-1, 0, 0, 0],
            [0, 1, 0, 2],
            [2, 0, 1, 0],
            [0, 0, 0, -1],
        ])

        require("A_inverse_exists_exactly", exact_zero(a_matrix.det() - 1))
        require(
            "riesz_projector_idempotent",
            exact_matrix_zero(projector * projector - projector),
        )
        require(
            "riesz_projector_commutes_with_A",
            exact_matrix_zero(a_matrix * projector - projector * a_matrix),
        )
        require(
            "riesz_projector_reverser_exchange",
            exact_matrix_zero(
                reverser * projector * reverser - (identity4 - projector)
            ),
        )
        require(
            "riesz_projector_trace_two",
            exact_zero(sp.trace(projector) - 2),
        )
        require(
            "expanding_spectral_factor_on_projector_range",
            exact_matrix_zero(
                (a_matrix**2 - 2 * alpha * a_matrix + identity4)
                * projector
            ),
        )
        require(
            "stable_spectral_factor_on_complement",
            exact_matrix_zero(
                (a_matrix**2 + 2 * alpha * a_matrix + identity4)
                * (identity4 - projector)
            ),
        )

        # dc/dalpha=8*alpha on the positive alpha branch.
        projector_c = projector.diff(alpha) / (8 * alpha)
        commutator_c = (
            projector_c * projector - projector * projector_c
        )
        require(
            "projector_commutator_closed_form",
            exact_matrix_zero(
                commutator_c - kato_m / (4 * (2 + c))
            ),
        )
        require(
            "kato_commutator_involution",
            exact_matrix_zero(kato_m * kato_m - identity4),
        )

        # ------------------------------------------------------------------
        # Closed Kato transport.  Put q^2=sqrt(2)*alpha, so that
        # q=((2+c)/2)^(1/4)>0 and tau=log(q).  This removes logarithms and
        # hyperbolic functions without changing their exact positive branch.
        # ------------------------------------------------------------------
        q = sp.symbols("q", positive=True, nonzero=True)
        alpha_q = q**2 / sqrt_two
        c_q = 2 * q**4 - 2
        a_q = make_a(c_q)
        projector_q = identity4 / 2 + (
            a_q + a_q.inv()
        ) / (4 * alpha_q)
        a_zero = make_a(0)
        alpha_zero = 1 / sqrt_two
        projector_zero = identity4 / 2 + (
            a_zero + a_zero.inv()
        ) / (4 * alpha_zero)

        cosh_tau = (q + 1 / q) / 2
        sinh_tau = (q - 1 / q) / 2
        transport = cosh_tau * identity4 + sinh_tau * kato_m
        require(
            "tau_and_hyperbolic_closed_forms",
            exact_zero(sp.log((2 + c_q) / 2) / 4 - sp.log(q))
            and exact_zero(sp.cosh(sp.log(q)) - cosh_tau)
            and exact_zero(sp.sinh(sp.log(q)) - sinh_tau),
        )
        require(
            "kato_transport_initial_value",
            exact_matrix_zero(transport.subs(q, 1) - identity4),
        )
        require(
            "kato_transport_projector_intertwining",
            exact_matrix_zero(
                projector_q * transport - transport * projector_zero
            ),
        )

        # q_c/q=1/(4*(2+c)); use the chain rule in q exactly.
        q_c = q / (4 * (2 + c_q))
        transport_c = transport.diff(q) * q_c
        projector_q_c = projector_q.diff(q) * q_c
        commutator_q_c = (
            projector_q_c * projector_q
            - projector_q * projector_q_c
        )
        require(
            "tau_derivative_sign_convention",
            exact_zero(q_c / q - 1 / (4 * (2 + c_q))),
        )
        require(
            "kato_transport_differential_equation",
            exact_matrix_zero(
                transport_c - commutator_q_c * transport
            ),
        )

        k_star = sp.Matrix([
            1 / sqrt_two,
            sp.Rational(1, 2),
            0,
            sp.Rational(1, 2),
        ])
        g_q = sp.Matrix([
            1,
            2 * alpha_q - 1 / sqrt_two,
            sqrt_two * alpha_q - 1,
            1 / sqrt_two,
        ])
        normalizer_squared_q = (
            6 * alpha_q**2 - 4 * sqrt_two * alpha_q + 3
        )
        transported_star = transport * k_star
        require(
            "transported_core_vector_bridge",
            exact_matrix_zero(
                transported_star - g_q / (sqrt_two * q)
            ),
        )
        require(
            "transported_core_vector_norm_squared_bridge",
            exact_zero(
                transported_star.dot(transported_star)
                - normalizer_squared_q / (2 * q**2)
            ),
        )
        transported_normalizer = sp.symbols(
            "N_transport", positive=True, nonzero=True
        )
        require(
            "normalized_transport_is_g_over_N",
            exact_matrix_zero(
                transported_star
                / (transported_normalizer / (sqrt_two * q))
                - g_q / transported_normalizer
            ),
        )
        require(
            "normalizer_is_g_norm_squared",
            exact_zero(g_q.dot(g_q) - normalizer_squared_q),
        )

        # ------------------------------------------------------------------
        # Algebraic frame E, normalized Kato frame K, and complex structure.
        # Here beta^2=1-alpha^2 is imposed by exact polynomial remainder.
        # ------------------------------------------------------------------
        beta = sp.symbols("beta", positive=True, nonzero=True)
        beta_relation = beta**2 - (1 - alpha**2)
        require(
            "alpha_beta_spectral_relations",
            exact_zero(c - (4 * alpha**2 - 2))
            and exact_zero(
                remainder(
                    beta**2 - (2 - c) / 4,
                    beta,
                    beta_relation,
                )
            ),
        )
        h = 2 * alpha * beta
        algebraic_frame = sp.Matrix([
            [1, 0],
            [alpha, -beta],
            [c / 2, h],
            [alpha, beta],
        ])
        expanding_block = sp.Matrix([
            [alpha, -beta],
            [beta, alpha],
        ])
        j_zero = sp.Matrix([[0, -1], [1, 0]])
        j_unstable = (a_matrix - alpha * identity4) / beta

        require(
            "algebraic_frame_spans_projector_range",
            matrix_zero_mod(
                projector * algebraic_frame - algebraic_frame,
                beta,
                beta_relation,
            ),
        )
        require(
            "algebraic_frame_expanding_block",
            matrix_zero_mod(
                a_matrix * algebraic_frame
                - algebraic_frame * expanding_block,
                beta,
                beta_relation,
            ),
        )
        require(
            "algebraic_frame_rank_two_minor",
            exact_zero(
                algebraic_frame.extract([0, 1], [0, 1]).det() + beta
            )
            and bool(beta.is_nonzero),
        )
        require(
            "unstable_complex_structure_on_projector_range",
            matrix_zero_mod(
                (j_unstable**2 + identity4) * projector,
                beta,
                beta_relation,
            ),
        )
        require(
            "unstable_complex_structure_intertwines_E_J0",
            matrix_zero_mod(
                j_unstable * algebraic_frame - algebraic_frame * j_zero,
                beta,
                beta_relation,
            ),
        )
        require(
            "unstable_complex_structure_not_global_identity",
            matrix_nonzero_mod(
                j_unstable**2 + identity4,
                beta,
                beta_relation,
            ),
        )
        require(
            "unstable_complex_structure_fails_on_stable_complement",
            matrix_nonzero_mod(
                (j_unstable**2 + identity4) * (identity4 - projector),
                beta,
                beta_relation,
            ),
        )

        y = (1 / sqrt_two - alpha) / beta
        normalizer_squared = 6 * alpha**2 - 4 * sqrt_two * alpha + 3
        normalizer = sp.symbols("N", positive=True, nonzero=True)
        normalizer_relation = normalizer**2 - normalizer_squared
        g = sp.Matrix([
            1,
            2 * alpha - 1 / sqrt_two,
            sqrt_two * alpha - 1,
            1 / sqrt_two,
        ])
        c_ak = sp.Matrix([[1, -y], [y, 1]]) / normalizer
        k_from_coordinates = algebraic_frame * c_ak
        k_one = g / normalizer
        k_two = j_unstable * k_one
        k_direct = k_one.row_join(k_two)

        require(
            "y_two_closed_forms_agree",
            matrix_zero_mod(
                sp.Matrix([
                    y
                    + c
                    / (
                        (2 * beta)
                        * (sqrt_two + 2 * alpha)
                    )
                ]),
                beta,
                beta_relation,
            ),
        )
        require(
            "normalizer_is_physical_g_norm_squared",
            exact_zero(g.dot(g) - normalizer_squared),
        )
        require(
            "normalized_first_kato_vector_has_unit_norm",
            exact_zero(
                remainder(
                    k_one.dot(k_one) - 1,
                    normalizer,
                    normalizer_relation,
                )
            ),
        )
        require(
            "K_equals_E_times_C_AK",
            matrix_zero_mod(
                k_from_coordinates - k_direct,
                beta,
                beta_relation,
            ),
        )
        require(
            "C_AK_first_column_gives_k1",
            matrix_zero_mod(
                algebraic_frame * c_ak[:, 0] - k_one,
                beta,
                beta_relation,
            ),
        )
        require(
            "C_AK_second_column_gives_Ju_k1",
            matrix_zero_mod(
                algebraic_frame * c_ak[:, 1] - k_two,
                beta,
                beta_relation,
            ),
        )

        c_ak_inverse = (
            normalizer
            * sp.Matrix([[1, y], [-y, 1]])
            / (1 + y**2)
        )
        conformal_square = (1 + y**2) / normalizer**2
        require(
            "C_AK_inverse_closed_form",
            exact_matrix_zero(c_ak * c_ak_inverse - sp.eye(2))
            and exact_matrix_zero(c_ak_inverse * c_ak - sp.eye(2)),
        )
        require(
            "C_AK_conformal_gram_identity",
            exact_matrix_zero(
                c_ak.T * c_ak - conformal_square * sp.eye(2)
            ),
        )
        require(
            "C_AK_determinant_is_sigma_squared",
            exact_zero(c_ak.det() - conformal_square),
        )
        require(
            "C_AK_orientation_is_positive",
            bool(sp.ask(sp.Q.positive(conformal_square))),
        )

        radial = sp.sqrt(1 + y**2)
        sigma = radial / normalizer
        rotation_chi = sp.Matrix([[1, -y], [y, 1]]) / radial
        require(
            "C_AK_positive_radial_rotation_factorization",
            exact_matrix_zero(c_ak - sigma * rotation_chi),
        )
        require(
            "R_chi_is_special_orthogonal",
            exact_matrix_zero(rotation_chi.T * rotation_chi - sp.eye(2))
            and exact_zero(rotation_chi.det() - 1),
        )

        # ------------------------------------------------------------------
        # Direct source circle: same graph boundary, +chi direction, and
        # degree +1.  The lift calculation is global and exact, not sampled.
        # ------------------------------------------------------------------
        phi, chi = sp.symbols("phi chi", real=True)
        source_radius = sp.Rational(1, 100)
        e_phi = sp.Matrix([sp.cos(phi), sp.sin(phi)])
        rotation_symbolic = sp.Matrix([
            [sp.cos(chi), -sp.sin(chi)],
            [sp.sin(chi), sp.cos(chi)],
        ])
        source_coordinate = source_radius * rotation_symbolic * e_phi
        phase_tangent = source_coordinate.diff(phi)
        require(
            "source_coordinate_fixed_radius",
            exact_zero(
                source_coordinate.dot(source_coordinate) - source_radius**2
            ),
        )
        require(
            "source_phase_derivative_J0_identity",
            exact_matrix_zero(
                phase_tangent - j_zero * source_coordinate
            ),
        )
        require(
            "source_phase_speed_fixed_radius",
            exact_zero(phase_tangent.dot(phase_tangent) - source_radius**2),
        )
        phase_plus_chi = sp.Matrix([
            sp.cos(phi + chi),
            sp.sin(phi + chi),
        ])
        require(
            "coordinate_direction_is_phi_plus_chi",
            exact_matrix_zero(rotation_symbolic * e_phi - phase_plus_chi),
        )
        require(
            "source_phase_degree_plus_one",
            exact_zero(
                ((phi + 2 * sp.pi) + chi) - (phi + chi) - 2 * sp.pi
            )
            and exact_zero(rotation_symbolic.det() - 1),
        )

        # C_AK=sigma*R_chi with sigma>0 makes normalized C_AK e_phi
        # precisely R_chi e_phi; this checks that Kato coordinates are sent
        # to algebraic coordinates in the declared (not inverse) direction.
        require(
            "same_graph_boundary_normalized_C_AK_direction",
            exact_matrix_zero(
                c_ak * e_phi / sigma - rotation_chi * e_phi
            ),
        )

        # ------------------------------------------------------------------
        # Complete r=0 anchor face for the Kato objects.  The graph equality
        # itself is supplied by the separately certified graph uniqueness;
        # this audit proves the exact algebraic inputs to that implication.
        # ------------------------------------------------------------------
        r, a_two = sp.symbols("r a2", real=True)
        epsilon = sp.symbols("epsilon", positive=True)
        c_parameter = (
            2 * r * a_two
            + sp.sqrt(epsilon) * r**4 * a_two**2
        )
        require(
            "anchor_face_c_is_zero_and_dummy_independent",
            exact_zero(c_parameter.subs(r, 0))
            and exact_zero(sp.diff(c_parameter, a_two).subs(r, 0))
            and exact_zero(sp.diff(c_parameter, epsilon).subs(r, 0))
            and exact_zero(
                sp.diff(c_parameter, a_two, epsilon).subs(r, 0)
            ),
        )

        y_zero = y.subs({alpha: 1 / sqrt_two, beta: 1 / sqrt_two})
        normalizer_squared_zero = normalizer_squared.subs(
            alpha, 1 / sqrt_two
        )
        c_ak_zero = c_ak.subs({
            alpha: 1 / sqrt_two,
            beta: 1 / sqrt_two,
            normalizer: sqrt_two,
        })
        rotation_zero = rotation_chi.subs({
            alpha: 1 / sqrt_two,
            beta: 1 / sqrt_two,
        })
        require("anchor_face_y_zero", exact_zero(y_zero))
        require(
            "anchor_face_chi_zero_on_positive_cosine_branch",
            exact_zero(sp.atan(y_zero)),
        )
        require(
            "anchor_face_normalizer_squared_two",
            exact_zero(normalizer_squared_zero - 2),
        )
        require(
            "anchor_face_transport_identity",
            exact_matrix_zero(transport.subs(q, 1) - identity4),
        )
        require(
            "anchor_face_C_AK_is_I_over_sqrt_two",
            exact_matrix_zero(c_ak_zero - sp.eye(2) / sqrt_two),
        )
        require(
            "anchor_face_rotation_is_identity",
            exact_matrix_zero(rotation_zero - sp.eye(2)),
        )
        require(
            "anchor_face_source_is_pointwise_core_circle",
            exact_matrix_zero(
                source_coordinate.subs(chi, 0) - source_radius * e_phi
            ),
        )

        # ------------------------------------------------------------------
        # Frozen scalar derivative formulas (still exact, with no cells or
        # point samples).  They are later composed with interval c-jets.
        # ------------------------------------------------------------------
        def d_dc(expression: sp.Expr) -> sp.Expr:
            return (
                sp.diff(expression, alpha) / (8 * alpha)
                - sp.diff(expression, beta) / (8 * beta)
            )

        alpha_c = 1 / (8 * alpha)
        alpha_cc = -1 / (64 * alpha**3)
        beta_c = -1 / (8 * beta)
        beta_cc = -1 / (64 * beta**3)
        y_c = -1 / (8 * alpha * beta) + y / (8 * beta**2)
        y_cc = (
            1 / (64 * alpha**3 * beta)
            - 1 / (64 * alpha * beta**3)
            + y_c / (8 * beta**2)
            + y / (32 * beta**4)
        )
        require(
            "alpha_first_second_derivative_formulas",
            exact_zero(d_dc(alpha) - alpha_c)
            and exact_zero(d_dc(alpha_c) - alpha_cc),
        )
        require(
            "beta_first_second_derivative_formulas",
            exact_zero(d_dc(beta) - beta_c)
            and exact_zero(d_dc(beta_c) - beta_cc),
        )
        require(
            "y_first_second_derivative_formulas",
            exact_zero(d_dc(y) - y_c)
            and exact_zero(d_dc(y_c) - y_cc),
        )
        chi_expression = sp.atan(y)
        chi_c = y_c / (1 + y**2)
        chi_cc = y_cc / (1 + y**2) - 2 * y * y_c**2 / (1 + y**2) ** 2
        require(
            "chi_first_second_derivative_formulas",
            exact_zero(d_dc(chi_expression) - chi_c)
            and exact_zero(d_dc(chi_c) - chi_cc),
        )

        failed = sorted(name for name, passed in checks.items() if not passed)
        status = "PASS" if not failed else "FAIL"
        payload: dict[str, object] = {
            "backend": {"name": "sympy", "version": sp.__version__},
            "checks": checks,
            "method": "exact-symbolic-identities-no-sampling",
            "schema_version": SCHEMA_VERSION,
            "status": status,
        }
        if failed:
            payload["failed_checks"] = failed
        emit(payload)
        return 0 if status == "PASS" else 1
    except Exception as error:
        emit({
            "backend": {"name": "sympy", "version": sp.__version__},
            "checks": checks,
            "error": f"{type(error).__name__}: {error}",
            "schema_version": SCHEMA_VERSION,
            "status": "FAIL",
        })
        return 1


if __name__ == "__main__":
    sys.exit(main())
