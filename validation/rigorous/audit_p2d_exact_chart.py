#!/usr/bin/env python3
"""Exact symbolic audit for the linear P2d exact-chart interface.

The audit has no command-line inputs, reads no project files, performs no
sampling or floating-point evaluation, and emits exactly one deterministic
JSON line.  Its scope is deliberately narrower than ``V2.EXACT_CHART``: it
checks the exact linear reversible symplectic completion, the Kato-oriented
action sign, and the algebra of a scout radial section.  It does not construct
the nonlinear analytic Moser chart or validate a zero-energy passage.
"""

from __future__ import annotations

import json
import sys


SCHEMA_VERSION = "rfsn-vdp-p2d-exact-chart-audit/2"
METHOD = "exact-symbolic-identities-no-sampling-no-file-inputs"
CLAIM_BOUNDARY: dict[str, object] = {
    "claim_bearing": False,
    "exact_identity_scope_only": [
        "linear reversible symplectic completion of the frozen Kato frame",
        "Kato-oriented quadratic action convention",
        "linear incoming and outgoing scout section forms and primitive gauges",
    ],
    "open_scope": [
        "nonlinear analytic Moser normal form",
        "nonlinear zero-energy fiber existence and uniqueness",
        "weighted-log local passage bounds",
        "exact nonlinear chart gauges and overlap compatibility",
        "frozen-box positive-radial branch margins",
        "parameter two-jets of the symplectic completion",
    ],
    "parent_obligation": "V2.EXACT_CHART remains OPEN",
    "v2_chart_atoms": {
        "V2.CHART.ANALYTIC_NORMAL_FORM": "OPEN",
        "V2.CHART.EXACT_SECTIONS": "OPEN",
        "V2.CHART.OVERLAPS": "OPEN",
        "V2.CHART.PHYSICAL_SLIDES": "OPEN",
        "V2.CHART.SYMPLECTIC_FRAME": "OPEN",
        "V2.CHART.WEIGHTED_PASSAGE": "OPEN",
        "V2.CHART.ZERO_ENERGY": "OPEN",
    },
}
INPUT_POLICY: dict[str, object] = {
    "external_files": [],
    "floating_point": False,
    "sampling": False,
}
EXACT_FORMULAS: dict[str, object] = {
    "kato_euclidean_gram": [
        [
            "1",
            "2*alpha*(alpha^2-1/2)/(N^2*beta)",
        ],
        [
            "2*alpha*(alpha^2-1/2)/(N^2*beta)",
            "6*(alpha^4-(2*sqrt(2)/3)*alpha^3-alpha^2/2+1/2)/(N^2*beta^2)",
        ],
    ],
    "kato_euclidean_status": (
        "The current normalized Kato complex frame has a unit first column "
        "but is not Euclidean orthonormal in general."
    ),
    "linear_phase_increment": (
        "Delta_lin=(beta/alpha)*log(alpha*rho^2/|nu|)"
    ),
    "linear_phase_log_slope": "D_log(Delta_lin)=-beta/alpha",
    "linear_positive_flight_domain": "0<|nu|<alpha*rho^2",
    "linear_positive_flight_parameterization": (
        "|nu|=alpha*rho^2/(1+sigma), sigma>0"
    ),
    "linear_reach_time": (
        "T_lin=(1/alpha)*log(alpha*rho^2/|nu|)"
    ),
    "normalizer_squared": "6*alpha^2-4*sqrt(2)*alpha+3",
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
    except Exception as error:  # pragma: no cover - only without the backend
        emit(failure_payload(version=None, checks={}, error=error))
        return 1

    checks: dict[str, bool] = {}

    def exact_zero(value: sp.Expr) -> bool:
        normalized = sp.cancel(sp.trigsimp(sp.simplify(value)))
        return normalized == 0

    def exact_matrix_zero(value: sp.MatrixBase) -> bool:
        return all(exact_zero(entry) for entry in value)

    def remainder(
        value: sp.Expr, variable: sp.Symbol, relation: sp.Expr
    ) -> sp.Expr:
        # All radicals retain their declared positive principal branches.  In
        # particular, do not use ``powdenest(force=True)`` here: forced power
        # rewriting would make an exact audit silently forget branch data.
        normalized = sp.cancel(sp.together(value))
        numerator, denominator = sp.fraction(normalized)
        reduced = sp.rem(
            sp.Poly(sp.expand(numerator), variable),
            sp.Poly(relation, variable),
        ).as_expr()
        return sp.cancel(reduced / denominator)

    def exact_zero_mod(
        value: sp.Expr, variable: sp.Symbol, relation: sp.Expr
    ) -> bool:
        return exact_zero(remainder(value, variable, relation))

    def matrix_zero_mod(
        value: sp.MatrixBase,
        variable: sp.Symbol,
        relation: sp.Expr,
    ) -> bool:
        return all(
            exact_zero_mod(entry, variable, relation) for entry in value
        )

    def exact_zero_mod_two(
        value: sp.Expr,
        first_variable: sp.Symbol,
        first_relation: sp.Expr,
        second_variable: sp.Symbol,
        second_relation: sp.Expr,
    ) -> bool:
        first_remainder = remainder(value, first_variable, first_relation)
        return exact_zero(
            remainder(first_remainder, second_variable, second_relation)
        )

    def require(name: str, predicate: bool) -> None:
        if not isinstance(predicate, bool):
            raise TypeError(f"check {name!r} did not produce a Python bool")
        checks[name] = predicate

    def block2(
        top_left: sp.MatrixBase,
        top_right: sp.MatrixBase,
        bottom_left: sp.MatrixBase,
        bottom_right: sp.MatrixBase,
    ) -> sp.Matrix:
        return sp.Matrix.vstack(
            sp.Matrix.hstack(top_left, top_right),
            sp.Matrix.hstack(bottom_left, bottom_right),
        )

    try:
        # --------------------------------------------------------------
        # Physical Hamiltonian convention and reversibility.
        # --------------------------------------------------------------
        identity2 = sp.eye(2)
        identity4 = sp.eye(4)
        zero2 = sp.zeros(2)
        omega = sp.Matrix([
            [0, -1, 0, 0],
            [1, 0, 0, 0],
            [0, 0, 0, 1],
            [0, 0, -1, 0],
        ])
        reverser = sp.diag(1, -1, 1, -1)

        require(
            "omega_is_skew_and_nondegenerate",
            exact_matrix_zero(omega.T + omega)
            and exact_zero(omega.det() - 1),
        )
        require(
            "reverser_is_anti_symplectic_involution",
            exact_matrix_zero(reverser * reverser - identity4)
            and exact_matrix_zero(reverser.T * omega * reverser + omega),
        )

        U, P, V, Q = sp.symbols("U P V Q", real=True)
        c_state, cubic, quartic = sp.symbols(
            "c_state cubic quartic", real=True
        )
        state = sp.Matrix([U, P, V, Q])
        hamiltonian = (
            (Q**2 - P**2) / 2
            - U * V
            + c_state * U**2 / 2
            - cubic * U**3 / 3
            + quartic * U**4
        )
        gradient = sp.Matrix([sp.diff(hamiltonian, item) for item in state])
        field = sp.Matrix([
            P,
            c_state * U - V - cubic * U**2 + 4 * quartic * U**3,
            Q,
            U,
        ])
        reversed_state = reverser * state
        reverse_substitution = dict(zip(state, reversed_state, strict=True))
        hamiltonian_reversed = hamiltonian.subs(
            reverse_substitution, simultaneous=True
        )
        field_reversed = field.subs(reverse_substitution, simultaneous=True)
        require(
            "hamiltonian_vector_field_identity",
            exact_matrix_zero(omega * gradient - field),
        )
        require(
            "hamiltonian_is_reverser_invariant",
            exact_zero(hamiltonian_reversed - hamiltonian),
        )
        require(
            "vector_field_is_reversible",
            exact_matrix_zero(reverser * field + field_reversed),
        )

        # --------------------------------------------------------------
        # Frozen Kato expanding frame and its physical symplectic pairing.
        # --------------------------------------------------------------
        sqrt_two = sp.sqrt(2)
        alpha = sp.symbols("alpha", positive=True, nonzero=True)
        beta = sp.symbols("beta", positive=True, nonzero=True)
        normalizer = sp.symbols("N", positive=True, nonzero=True)
        beta_relation = beta**2 - (1 - alpha**2)
        c = 4 * alpha**2 - 2
        h = 2 * alpha * beta
        linearization = sp.Matrix([
            [0, 1, 0, 0],
            [c, 0, -1, 0],
            [0, 0, 0, 1],
            [1, 0, 0, 0],
        ])
        require(
            "linearization_is_hamiltonian_and_reversible",
            exact_matrix_zero(linearization.T * omega + omega * linearization)
            and exact_matrix_zero(
                linearization * reverser + reverser * linearization
            ),
        )

        algebraic_frame = sp.Matrix([
            [1, 0],
            [alpha, -beta],
            [c / 2, h],
            [alpha, beta],
        ])
        j_zero = sp.Matrix([[0, -1], [1, 0]])
        expanding_block = alpha * identity2 + beta * j_zero
        y_shift = (1 / sqrt_two - alpha) / beta
        coordinate_change = (
            sp.Matrix([[1, -y_shift], [y_shift, 1]]) / normalizer
        )
        kato_frame = algebraic_frame * coordinate_change
        normalizer_squared = (
            6 * alpha**2 - 4 * sqrt_two * alpha + 3
        )
        normalizer_relation = normalizer**2 - normalizer_squared
        transported_vector = sp.Matrix([
            1,
            2 * alpha - 1 / sqrt_two,
            sqrt_two * alpha - 1,
            1 / sqrt_two,
        ])
        require(
            "kato_frame_equals_algebraic_frame_times_change",
            exact_matrix_zero(
                kato_frame - algebraic_frame * coordinate_change
            ),
        )
        require(
            "first_kato_column_is_transported_vector_over_normalizer",
            exact_matrix_zero(
                kato_frame[:, 0] - transported_vector / normalizer
            ),
        )
        require(
            "second_kato_column_is_positive_complex_partner",
            matrix_zero_mod(
                kato_frame[:, 1]
                - (linearization - alpha * identity4)
                * kato_frame[:, 0]
                / beta,
                beta,
                beta_relation,
            ),
        )
        require(
            "kato_frame_has_expanding_block",
            matrix_zero_mod(
                linearization * kato_frame
                - kato_frame * expanding_block,
                beta,
                beta_relation,
            ),
        )
        require(
            "kato_expanding_plane_is_lagrangian",
            matrix_zero_mod(
                kato_frame.T * omega * kato_frame,
                beta,
                beta_relation,
            ),
        )
        require(
            "normalizer_squared_is_exact_transported_vector_norm",
            exact_zero(
                transported_vector.dot(transported_vector)
                - normalizer_squared
            ),
        )
        require(
            "normalized_first_kato_vector_has_unit_euclidean_norm",
            exact_zero_mod_two(
                kato_frame[:, 0].dot(kato_frame[:, 0]) - 1,
                beta,
                beta_relation,
                normalizer,
                normalizer_relation,
            ),
        )
        kato_gram = kato_frame.T * kato_frame
        gram_off_diagonal = (
            2 * alpha * (alpha**2 - sp.Rational(1, 2))
            / (normalizer**2 * beta)
        )
        gram_second_diagonal = (
            6
            * (
                alpha**4
                - 2 * sqrt_two * alpha**3 / 3
                - alpha**2 / 2
                + sp.Rational(1, 2)
            )
            / (normalizer**2 * beta**2)
        )
        kato_gram_closed = sp.Matrix([
            [normalizer_squared / normalizer**2, gram_off_diagonal],
            [gram_off_diagonal, gram_second_diagonal],
        ])
        require(
            "kato_euclidean_gram_has_exact_nonorthogonal_closed_form",
            matrix_zero_mod(
                kato_gram - kato_gram_closed,
                beta,
                beta_relation,
            ),
        )
        require(
            "current_kato_complex_frame_is_not_euclidean_orthonormal_in_general",
            not exact_zero_mod(
                gram_off_diagonal, beta, beta_relation
            )
            and not exact_zero_mod_two(
                gram_second_diagonal - 1,
                beta,
                beta_relation,
                normalizer,
                normalizer_relation,
            ),
        )
        require(
            "reverser_maps_expanding_to_stable",
            matrix_zero_mod(
                linearization * (reverser * kato_frame)
                + (reverser * kato_frame) * expanding_block,
                beta,
                beta_relation,
            ),
        )

        cross_pairing = kato_frame.T * omega * reverser * kato_frame
        d_closed = 2 * alpha / normalizer**2
        e_closed = (
            2
            * alpha
            * (3 * alpha - 2 * sqrt_two)
            / (normalizer**2 * beta)
        )
        cross_closed = sp.Matrix([
            [d_closed, e_closed],
            [e_closed, -d_closed],
        ])
        require(
            "cross_pairing_is_symmetric_traceless",
            matrix_zero_mod(
                cross_pairing - cross_pairing.T,
                beta,
                beta_relation,
            )
            and exact_zero_mod(
                sp.trace(cross_pairing), beta, beta_relation
            ),
        )
        require(
            "cross_pairing_closed_form_d_e",
            matrix_zero_mod(
                cross_pairing - cross_closed,
                beta,
                beta_relation,
            ),
        )
        kappa_closed = (
            4
            * alpha
            * beta
            * (1 + y_shift**2)
            / normalizer**2
        )
        require(
            "kappa_positive_closed_form",
            bool(sp.ask(sp.Q.positive(kappa_closed))),
        )
        require(
            "kappa_squared_is_d_squared_plus_e_squared",
            exact_zero_mod(
                kappa_closed**2 - d_closed**2 - e_closed**2,
                beta,
                beta_relation,
            ),
        )
        require(
            "cross_pairing_determinant_is_minus_kappa_squared",
            exact_zero_mod(
                cross_pairing.det() + kappa_closed**2,
                beta,
                beta_relation,
            ),
        )

        # --------------------------------------------------------------
        # Generic half-angle lemma.  It applies to the exact d,e,kappa
        # formulas above and avoids hiding a branch choice in atan2.
        # --------------------------------------------------------------
        d_symbol = sp.symbols("d", positive=True, nonzero=True)
        e_symbol = sp.symbols("e", real=True)
        kappa = sp.symbols("kappa", positive=True, nonzero=True)
        e_relation = e_symbol**2 - (kappa**2 - d_symbol**2)
        half_denominator = sp.sqrt(
            2 * kappa * (kappa + d_symbol)
        )
        cosine_half = (kappa + d_symbol) / half_denominator
        sine_half = e_symbol / half_denominator
        half_rotation = sp.Matrix([
            [cosine_half, -sine_half],
            [sine_half, cosine_half],
        ])
        c_zero = sp.diag(1, -1)
        cross_generic = sp.Matrix([
            [d_symbol, e_symbol],
            [e_symbol, -d_symbol],
        ])
        require(
            "half_angle_unit_circle_and_positive_cosine",
            exact_zero_mod(
                cosine_half**2 + sine_half**2 - 1,
                e_symbol,
                e_relation,
            )
            and bool(sp.ask(sp.Q.positive(cosine_half))),
        )
        require(
            "half_angle_double_angle_formulas",
            exact_zero_mod(
                cosine_half**2 - sine_half**2 - d_symbol / kappa,
                e_symbol,
                e_relation,
            )
            and exact_zero_mod(
                2 * cosine_half * sine_half - e_symbol / kappa,
                e_symbol,
                e_relation,
            ),
        )
        require(
            "half_angle_is_special_orthogonal",
            matrix_zero_mod(
                half_rotation.T * half_rotation - identity2,
                e_symbol,
                e_relation,
            )
            and exact_zero_mod(
                half_rotation.det() - 1,
                e_symbol,
                e_relation,
            ),
        )
        diagonalized_cross = (
            half_rotation.T * cross_generic * half_rotation / kappa
        )
        require(
            "half_angle_diagonalizes_cross_pairing",
            matrix_zero_mod(
                diagonalized_cross - c_zero,
                e_symbol,
                e_relation,
            ),
        )

        # Instantiate the branch with the frozen physical d,e,kappa formulas.
        # This is intentionally not an abstract block-Gram surrogate: the
        # matrices Y, X, and L below are the actual physical completion.
        actual_half_denominator = sp.sqrt(
            2 * kappa_closed * (kappa_closed + d_closed)
        )
        actual_cosine_half = (
            kappa_closed + d_closed
        ) / actual_half_denominator
        actual_sine_half = e_closed / actual_half_denominator
        actual_half_rotation = sp.Matrix([
            [actual_cosine_half, -actual_sine_half],
            [actual_sine_half, actual_cosine_half],
        ])
        require(
            "actual_half_angle_branch_diagonalizes_physical_cross_pairing",
            bool(sp.ask(sp.Q.positive(actual_cosine_half)))
            and matrix_zero_mod(
                actual_half_rotation.T
                * cross_pairing
                * actual_half_rotation
                / kappa_closed
                - c_zero,
                beta,
                beta_relation,
            )
            and exact_matrix_zero(
                actual_half_rotation * j_zero
                - j_zero * actual_half_rotation
            )
            and exact_zero_mod(
                actual_half_rotation.det() - 1,
                beta,
                beta_relation,
            ),
        )

        actual_expanding_frame = (
            kato_frame * actual_half_rotation / sp.sqrt(kappa_closed)
        )
        actual_stable_frame = reverser * actual_expanding_frame * c_zero
        actual_completion = actual_stable_frame.row_join(
            actual_expanding_frame
        )
        omega_zero = block2(zero2, -identity2, identity2, zero2)
        require(
            "actual_completion_L_is_exact_symplectic",
            matrix_zero_mod(
                actual_completion.T * omega * actual_completion - omega_zero,
                beta,
                beta_relation,
            ),
        )
        standard_reverser = block2(zero2, c_zero, c_zero, zero2)
        require(
            "actual_completion_intertwines_physical_and_standard_reversers",
            exact_matrix_zero(
                reverser * actual_completion
                - actual_completion * standard_reverser
            ),
        )

        stable_block = -c_zero * expanding_block * c_zero
        expected_stable_block = -alpha * identity2 + beta * j_zero
        linear_blocks = block2(
            stable_block, zero2, zero2, expanding_block
        )
        actual_completion_inverse = (
            -omega_zero * actual_completion.T * omega
        )
        require(
            "actual_completion_inverse_conjugates_physical_linearization_to_kato_blocks",
            exact_matrix_zero(stable_block - expected_stable_block)
            and matrix_zero_mod(
                actual_completion_inverse * actual_completion - identity4,
                beta,
                beta_relation,
            )
            and matrix_zero_mod(
                actual_completion_inverse
                * linearization
                * actual_completion
                - linear_blocks,
                beta,
                beta_relation,
            ),
        )

        # --------------------------------------------------------------
        # The coordinate polynomials differ between the frozen flagship and
        # positive-Kato conventions.  The full four-dimensional T dictionary
        # transports one to the other without flipping the action value.  This
        # is a coordinate seam, not a dynamical sign change.
        # --------------------------------------------------------------
        x1, x2, y1, y2 = sp.symbols("x1 x2 y1 y2", real=True)
        standard_state = sp.Matrix([x1, x2, y1, y2])
        phi, nu, tau = sp.symbols("phi nu tau", real=True)
        e_phi = sp.Matrix([sp.cos(phi), sp.sin(phi)])
        e_minus_phi = sp.Matrix([sp.cos(phi), -sp.sin(phi)])
        j_e_phi = j_zero * e_phi
        i_one = x1 * y1 + x2 * y2
        i_two_kato = x2 * y1 - x1 * y2
        i_two_flagship = x1 * y2 - x2 * y1
        h_two_kato = alpha * i_one + beta * i_two_kato
        pulled_hessian = -omega_zero * linear_blocks
        require(
            "quadratic_hamiltonian_uses_I2K",
            exact_matrix_zero(
                pulled_hessian
                - sp.hessian(h_two_kato, tuple(standard_state))
            ),
        )
        require(
            "flagship_I2F_is_minus_I2K",
            exact_zero(i_two_flagship + i_two_kato),
        )

        # The complete frozen-to-Kato dictionary is the four-dimensional
        # symplectic map T=diag(C0,C0).  It commutes with the standard
        # reverser, preserves I1, and sends I2F to I2K without negating the
        # action value.
        dictionary_t = block2(c_zero, zero2, zero2, c_zero)
        require(
            "FK_dictionary_T_is_symplectic_involution",
            exact_matrix_zero(dictionary_t * dictionary_t - identity4)
            and exact_matrix_zero(
                dictionary_t.T * omega_zero * dictionary_t - omega_zero
            ),
        )
        require(
            "FK_dictionary_T_commutes_with_standard_reverser",
            exact_matrix_zero(
                dictionary_t * standard_reverser
                - standard_reverser * dictionary_t
            ),
        )
        dictionary_state = dictionary_t * standard_state
        dictionary_i_one = (
            dictionary_state[0] * dictionary_state[2]
            + dictionary_state[1] * dictionary_state[3]
        )
        dictionary_i_two_flagship = (
            dictionary_state[0] * dictionary_state[3]
            - dictionary_state[1] * dictionary_state[2]
        )
        require(
            "FK_dictionary_T_preserves_I1",
            exact_zero(dictionary_i_one - i_one),
        )
        require(
            "FK_dictionary_T_sends_I2F_to_I2K_without_action_flip",
            exact_zero(dictionary_i_two_flagship - i_two_kato),
        )
        require(
            "FK_dictionary_C0_sends_phase_phi_to_minus_phi",
            exact_matrix_zero(c_zero * e_phi - e_minus_phi),
        )
        require(
            "FK_dictionary_C0_reverses_J_phase_orientation",
            exact_matrix_zero(
                c_zero * j_e_phi + j_zero * e_minus_phi
            ),
        )
        dictionary_h_two_flagship = (
            alpha * dictionary_i_one + beta * dictionary_i_two_flagship
        )
        require(
            "FK_dictionary_transports_flagship_H2_to_kato_H2",
            exact_zero(dictionary_h_two_flagship - h_two_kato),
        )

        # --------------------------------------------------------------
        # Linear scout section.  No nonlinear zero-energy root is claimed.
        # --------------------------------------------------------------
        radius = sp.symbols("rho", positive=True, nonzero=True)
        require(
            "kato_expanding_phase_speed_is_plus_beta",
            exact_zero(
                j_e_phi.dot(expanding_block * e_phi) - beta
            ),
        )

        h_two_section = alpha * tau + beta * nu
        q_linear = -beta * nu / alpha
        require(
            "linear_zero_energy_h2_is_alpha_tau_plus_beta_nu",
            exact_zero(
                h_two_kato.subs({
                    x1: tau / radius,
                    x2: nu / radius,
                    y1: radius,
                    y2: 0,
                })
                - h_two_section
            ),
        )
        require(
            "linear_zero_energy_q_is_minus_beta_over_alpha_nu",
            exact_zero(h_two_section.subs(tau, q_linear)),
        )
        require(
            "linear_zero_energy_partial_tau_is_alpha",
            exact_zero(sp.diff(h_two_section, tau) - alpha),
        )

        # Outgoing: the expanding coordinate y has fixed radius.
        x_outgoing = (tau * e_phi + nu * j_e_phi) / radius
        y_outgoing = radius * e_phi
        require(
            "outgoing_scout_expanding_radius_is_rho",
            exact_zero(y_outgoing.dot(y_outgoing) - radius**2),
        )
        require(
            "outgoing_scout_I1_is_tau",
            exact_zero(x_outgoing.dot(y_outgoing) - tau),
        )
        outgoing_i_two_kato = (
            x_outgoing[1] * y_outgoing[0]
            - x_outgoing[0] * y_outgoing[1]
        )
        require(
            "outgoing_scout_I2K_is_nu",
            exact_zero(outgoing_i_two_kato - nu),
        )

        root_function = sp.Function("q")(phi, nu)
        x_outgoing_root = (
            root_function * e_phi + nu * j_e_phi
        ) / radius
        outgoing_state = x_outgoing_root.col_join(y_outgoing)
        outgoing_jacobian = outgoing_state.jacobian([phi, nu])
        section_form = sp.Matrix([[0, 1], [-1, 0]])
        require(
            "outgoing_scout_pullback_is_dphi_wedge_dnu",
            exact_matrix_zero(
                outgoing_jacobian.T
                * omega_zero
                * outgoing_jacobian
                - section_form
            ),
        )
        outgoing_lambda_zero = -omega_zero * outgoing_state / 2
        pulled_outgoing_lambda = (
            outgoing_jacobian.T * outgoing_lambda_zero
        )
        expected_outgoing_lambda = sp.Matrix([
            -nu + sp.diff(root_function, phi) / 2,
            sp.diff(root_function, nu) / 2,
        ])
        require(
            "outgoing_scout_primitive_is_minus_nu_dphi_plus_half_dq",
            exact_matrix_zero(
                pulled_outgoing_lambda - expected_outgoing_lambda
            ),
        )

        # Incoming: the stable coordinate x has fixed radius.  The sign in
        # y=(q e-nu J e)/rho is forced by I2K=nu and by the same section form.
        x_incoming = radius * e_phi
        y_incoming = (tau * e_phi - nu * j_e_phi) / radius
        require(
            "incoming_scout_stable_radius_is_rho",
            exact_zero(x_incoming.dot(x_incoming) - radius**2),
        )
        require(
            "incoming_scout_I1_is_tau",
            exact_zero(x_incoming.dot(y_incoming) - tau),
        )
        incoming_i_two_kato = (
            x_incoming[1] * y_incoming[0]
            - x_incoming[0] * y_incoming[1]
        )
        require(
            "incoming_scout_I2K_is_nu",
            exact_zero(incoming_i_two_kato - nu),
        )
        y_incoming_root = (
            root_function * e_phi - nu * j_e_phi
        ) / radius
        incoming_state = x_incoming.col_join(y_incoming_root)
        incoming_jacobian = incoming_state.jacobian([phi, nu])
        require(
            "incoming_scout_pullback_is_dphi_wedge_dnu",
            exact_matrix_zero(
                incoming_jacobian.T
                * omega_zero
                * incoming_jacobian
                - section_form
            ),
        )
        incoming_lambda_zero = -omega_zero * incoming_state / 2
        pulled_incoming_lambda = (
            incoming_jacobian.T * incoming_lambda_zero
        )
        expected_incoming_lambda = sp.Matrix([
            -nu - sp.diff(root_function, phi) / 2,
            -sp.diff(root_function, nu) / 2,
        ])
        require(
            "incoming_scout_primitive_is_minus_nu_dphi_minus_half_dq",
            exact_matrix_zero(
                pulled_incoming_lambda - expected_incoming_lambda
            ),
        )

        # The phase sign is now seeded by the actual linear incoming radius,
        # rather than by defining a logarithmic phase formula.  On h2=0 the
        # incoming expanding coordinate has radius |nu|/(alpha*rho).  Its
        # growth at rate alpha reaches rho after T_lin below; the already
        # checked positive Kato phase speed +beta then fixes the log slope.
        incoming_linear_y = y_incoming.subs(tau, q_linear)
        require(
            "linear_incoming_expanding_radius_squared_is_nu_squared_over_alpha_squared_rho_squared",
            exact_zero_mod(
                incoming_linear_y.dot(incoming_linear_y)
                - nu**2 / (alpha**2 * radius**2),
                beta,
                beta_relation,
            ),
        )
        nu_absolute = sp.symbols(
            "nu_absolute", positive=True, nonzero=True
        )
        flight_slack = sp.symbols(
            "sigma", positive=True, nonzero=True
        )
        domain_nu_absolute = (
            alpha * radius**2 / (1 + flight_slack)
        )
        domain_upper_margin = sp.factor(
            alpha * radius**2 - domain_nu_absolute
        )
        incoming_radius_positive = nu_absolute / (alpha * radius)
        linear_reach_time = (
            sp.log(alpha * radius**2 / nu_absolute) / alpha
        )
        domain_reach_time = sp.simplify(
            linear_reach_time.subs(
                nu_absolute, domain_nu_absolute
            )
        )
        require(
            "linear_positive_flight_domain_is_zero_less_abs_nu_less_alpha_rho_squared",
            bool(sp.ask(sp.Q.positive(domain_nu_absolute)))
            and bool(sp.ask(sp.Q.positive(domain_upper_margin)))
            and exact_zero(
                domain_reach_time
                - sp.log(1 + flight_slack) / alpha
            )
            and bool(sp.ask(sp.Q.positive(domain_reach_time))),
        )
        dlog_linear_reach_time = (
            nu_absolute * sp.diff(linear_reach_time, nu_absolute)
        )
        require(
            "linear_reach_time_hits_rho_and_has_Dlog_minus_one_over_alpha",
            exact_zero(
                sp.exp(alpha * linear_reach_time)
                * incoming_radius_positive
                - radius
            )
            and exact_zero(dlog_linear_reach_time + 1 / alpha),
        )
        linear_phase_increment = beta * linear_reach_time
        require(
            "linear_phase_Dlog_from_plus_beta_speed_is_minus_beta_over_alpha",
            exact_zero(
                nu_absolute
                * sp.diff(linear_phase_increment, nu_absolute)
                + beta / alpha
            ),
        )

        physical_lambda = sp.Matrix([P, 0, -Q, 0])
        symmetric_lambda = -omega * state / 2
        physical_gauge = (U * P - V * Q) / 2
        physical_gauge_gradient = sp.Matrix([
            sp.diff(physical_gauge, item) for item in state
        ])
        require(
            "physical_primitive_gauge_is_exact",
            exact_matrix_zero(
                physical_lambda
                - symmetric_lambda
                - physical_gauge_gradient
            ),
        )
        require(
            "actual_linear_symplectic_frame_preserves_symmetric_primitive",
            matrix_zero_mod(
                -actual_completion.T
                * omega
                * actual_completion
                * standard_state
                / 2
                + omega_zero * standard_state / 2,
                beta,
                beta_relation,
            ),
        )

        failed = sorted(name for name, passed in checks.items() if not passed)
        status = "PASS" if not failed else "FAIL"
        payload: dict[str, object] = {
            "backend": {"name": "sympy", "version": sp.__version__},
            "checks": checks,
            "claim_boundary": CLAIM_BOUNDARY,
            "exact_formulas": EXACT_FORMULAS,
            "input_policy": INPUT_POLICY,
            "method": METHOD,
            "schema_version": SCHEMA_VERSION,
            "status": status,
        }
        if failed:
            payload["failed_checks"] = failed
        emit(payload)
        return 0 if status == "PASS" else 1
    except Exception as error:
        emit(failure_payload(
            version=sp.__version__, checks=checks, error=error
        ))
        return 1


if __name__ == "__main__":
    sys.exit(main())
