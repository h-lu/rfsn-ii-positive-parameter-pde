#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <stdexcept>

#include "capd/capdlib.h"
#include "unstable_graph_terms.hpp"

using capd::interval;

namespace {

double absUpper(const interval& value) {
  return std::max(std::abs(value.leftBound()),
                  std::abs(value.rightBound()));
}

interval integerPower(interval value, int exponent) {
  interval result(1.);
  for(int index = 0; index < exponent; ++index) result *= value;
  return result;
}

int fallingFactorial(int exponent, int derivatives) {
  int result = 1;
  for(int index = 0; index < derivatives; ++index)
    result *= exponent - index;
  return result;
}

interval coefficient(const PolynomialTerm& term) {
  interval result = interval(term.numerator, term.numerator)
    / interval(term.denominator, term.denominator);
  if(term.times_sqrt_two) result *= sqrt(interval(2.));
  return result;
}

template<std::size_t Size>
interval absolutePolynomialBound(const PolynomialTerm (&terms)[Size],
                                 const interval& radius,
                                 int dx = 0, int dy = 0) {
  interval result(0.);
  for(const auto& term : terms) {
    if(term.px < dx || term.py < dy) continue;
    result += interval(0., absUpper(coefficient(term)))
      * interval(static_cast<double>(fallingFactorial(term.px, dx)))
      * interval(static_cast<double>(fallingFactorial(term.py, dy)))
      * integerPower(radius, term.px + term.py - dx - dy);
  }
  return result;
}

} // namespace

int main() {
  try {
    const interval radius("0.01", "0.01");
    const interval rho("1e-20", "1e-20");
    const interval c = interval(1.) / sqrt(interval(2.));

    const interval h1 = absolutePolynomialBound(kH1Terms, radius);
    const interval h2 = absolutePolynomialBound(kH2Terms, radius);
    const interval h = sqrt(sqr(h1) + sqr(h2));
    const interval h1x = absolutePolynomialBound(kH1Terms, radius, 1, 0);
    const interval h1y = absolutePolynomialBound(kH1Terms, radius, 0, 1);
    const interval h2x = absolutePolynomialBound(kH2Terms, radius, 1, 0);
    const interval h2y = absolutePolynomialBound(kH2Terms, radius, 0, 1);
    const interval dh = sqrt(sqr(h1x) + sqr(h1y)
                           + sqr(h2x) + sqr(h2y));
    const interval h1xx = absolutePolynomialBound(kH1Terms, radius, 2, 0);
    const interval h1xy = absolutePolynomialBound(kH1Terms, radius, 1, 1);
    const interval h1yy = absolutePolynomialBound(kH1Terms, radius, 0, 2);
    const interval h2xx = absolutePolynomialBound(kH2Terms, radius, 2, 0);
    const interval h2xy = absolutePolynomialBound(kH2Terms, radius, 1, 1);
    const interval h2yy = absolutePolynomialBound(kH2Terms, radius, 0, 2);
    const interval d2h = sqrt(sqr(h1xx) + interval(2.) * sqr(h1xy)
                            + sqr(h1yy) + sqr(h2xx)
                            + interval(2.) * sqr(h2xy) + sqr(h2yy));

    const interval r1 = absolutePolynomialBound(kDefect1Terms, radius);
    const interval r2 = absolutePolynomialBound(kDefect2Terms, radius);
    const interval defect = sqrt(sqr(r1) + sqr(r2));
    const interval ddefect = sqrt(
      sqr(absolutePolynomialBound(kDefect1Terms, radius, 1, 0))
      + sqr(absolutePolynomialBound(kDefect1Terms, radius, 0, 1))
      + sqr(absolutePolynomialBound(kDefect2Terms, radius, 1, 0))
      + sqr(absolutePolynomialBound(kDefect2Terms, radius, 0, 1)));

    // For w=s-H10(u), the nonlinear coupling contains only u1+s1.
    // These scalar inequalities use Euclidean norms.  The true residual
    // disk ||w||_2<=rho is consequently contained in the component square
    // later supplied to CAPD and to the robust source rows.
    const interval nonlinear = radius + h1 + rho;
    const interval contraction = c - nonlinear * (interval(1.) + dh);
    const interval boundary = contraction * rho - defect;
    const interval unstableExit = c * sqr(radius)
      - interval(.5) * radius * sqr(nonlinear);
    const interval residualUVariation = ddefect
      + (sqr(interval(1.) + dh) + d2h * nonlinear) * rho;
    const interval differenceCone = interval(2.) * contraction
      - nonlinear - residualUVariation;
    const interval slope("1e-18", "1e-18");
    const interval smallCone = interval(2.) * contraction * slope
      - residualUVariation - nonlinear * sqr(slope);

    if(!(h.rightBound() < 4.e-5
         && contraction.leftBound() > .69
         && defect.rightBound() < 3.e-24
         && boundary.leftBound() > 6.e-21
         && unstableExit.leftBound() > 7.e-5
         && differenceCone.leftBound() > 1.3
         && smallCone.leftBound() > 1.3e-18))
      throw std::runtime_error("local unstable-graph inequality failed");

    std::cout << std::setprecision(17)
      << "{\n"
      << "  \"status\": \"PASS-LOCAL-UNSTABLE-GRAPH\",\n"
      << "  \"u_radius\": 0.01,\n"
      << "  \"residual_euclidean_radius\": 1e-20,\n"
      << "  \"H10_norm_upper\": " << h.rightBound() << ",\n"
      << "  \"DH10_frobenius_upper\": " << dh.rightBound() << ",\n"
      << "  \"D2H10_frobenius_upper\": " << d2h.rightBound() << ",\n"
      << "  \"defect_norm_upper\": " << defect.rightBound() << ",\n"
      << "  \"defect_derivative_upper\": " << ddefect.rightBound() << ",\n"
      << "  \"normal_contraction_lower\": "
      << contraction.leftBound() << ",\n"
      << "  \"normal_boundary_margin_lower\": "
      << boundary.leftBound() << ",\n"
      << "  \"unstable_exit_margin_lower\": "
      << unstableExit.leftBound() << ",\n"
      << "  \"difference_cone_margin_lower\": "
      << differenceCone.leftBound() << ",\n"
      << "  \"true_graph_residual_C0_component_upper\": 1e-20,\n"
      << "  \"true_graph_residual_C1_operator_upper\": 1e-18,\n"
      << "  \"small_cone_margin_lower\": "
      << smallCone.leftBound() << "\n"
      << "}\n";
    return 0;
  } catch(const std::exception& error) {
    std::cerr << "FAIL: " << error.what() << "\n";
    return 10;
  }
}
