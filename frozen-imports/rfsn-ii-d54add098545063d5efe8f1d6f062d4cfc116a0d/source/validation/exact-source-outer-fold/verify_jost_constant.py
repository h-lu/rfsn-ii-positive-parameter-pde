#!/usr/bin/env python3
"""Directed-MPFR verification of the hard-coded k0 interval."""

import gmpy2


PRECISION = 256
DECLARED_LOWER = float.fromhex("0x1.12090b7dc7279p-1")
DECLARED_UPPER = float.fromhex("0x1.12090b7dc727bp-1")


def rounded(direction, operation):
    context = gmpy2.get_context().copy()
    context.precision = PRECISION
    context.round = direction
    with gmpy2.context(context):
        return +operation()


def main():
    down = gmpy2.RoundDown
    up = gmpy2.RoundUp
    quarter = rounded(down, lambda: gmpy2.mpfr(1) / 4)
    three_quarters = rounded(down, lambda: gmpy2.mpfr(3) / 4)
    pi_lower = rounded(down, gmpy2.const_pi)
    pi_upper = rounded(up, gmpy2.const_pi)
    root_pi_lower = rounded(down, lambda: gmpy2.sqrt(pi_lower))
    root_pi_upper = rounded(up, lambda: gmpy2.sqrt(pi_upper))
    gamma_quarter_lower = rounded(down, lambda: gmpy2.gamma(quarter))
    gamma_quarter_upper = rounded(up, lambda: gmpy2.gamma(quarter))
    gamma_three_lower = rounded(down, lambda: gmpy2.gamma(three_quarters))
    gamma_three_upper = rounded(up, lambda: gmpy2.gamma(three_quarters))
    root_six_lower = rounded(down, lambda: gmpy2.sqrt(6))
    root_six_upper = rounded(up, lambda: gmpy2.sqrt(6))
    numerator_lower = rounded(
        down, lambda: root_pi_lower * gamma_quarter_lower
    )
    numerator_upper = rounded(
        up, lambda: root_pi_upper * gamma_quarter_upper
    )
    denominator_lower = rounded(
        down, lambda: 4 * root_six_lower * gamma_three_lower
    )
    denominator_upper = rounded(
        up, lambda: 4 * root_six_upper * gamma_three_upper
    )
    lower = rounded(down, lambda: numerator_lower / denominator_upper)
    upper = rounded(up, lambda: numerator_upper / denominator_lower)
    if not gmpy2.mpfr(DECLARED_LOWER) < lower:
        raise RuntimeError("declared k0 lower endpoint is not strict")
    if not upper < gmpy2.mpfr(DECLARED_UPPER):
        raise RuntimeError("declared k0 upper endpoint is not strict")
    print(
        '{"status":"PASS-DIRECTED-MPFR-K0",'
        f'"declared":[{DECLARED_LOWER:.17g},{DECLARED_UPPER:.17g}],'
        f'"precision_bits":{PRECISION}}}'
    )


if __name__ == "__main__":
    main()
