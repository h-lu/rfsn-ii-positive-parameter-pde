#include "interval_io.hpp"
#include "rounding_self_test.hpp"
#include "verdict.hpp"

// The runner injects the hash-checked frozen H10 table with an absolute
// `-include` compiler argument.  Keeping no filename-based include here
// prevents a same-named file in this or an earlier include directory from
// shadowing the materialized Git object.

#include <algorithm>
#include <array>
#include <cmath>
#include <exception>
#include <iostream>
#include <set>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {

using rfsn::rigorous::Interval;
using rfsn::rigorous::Verdict;
using rfsn::rigorous::combine;
using rfsn::rigorous::intervalJson;
using rfsn::rigorous::verdictName;

using Enclosures = std::vector<std::pair<std::string, Interval>>;

double absUpper(const Interval& value) {
  return std::max(std::abs(value.leftBound()),
                  std::abs(value.rightBound()));
}

Interval integerPower(Interval value, int exponent) {
  Interval result(1.0);
  for (int index = 0; index < exponent; ++index) result *= value;
  return result;
}

int fallingFactorial(int exponent, int derivatives) {
  int result = 1;
  for (int index = 0; index < derivatives; ++index)
    result *= exponent - index;
  return result;
}

Interval coefficient(const PolynomialTerm& term) {
  const Interval denominator(term.denominator, term.denominator);
  if (denominator.leftBound() <= 0.0)
    throw std::invalid_argument("polynomial denominator is not positive");
  Interval result = Interval(term.numerator, term.numerator) / denominator;
  if (term.times_sqrt_two) result *= sqrt(Interval(2.0));
  return result;
}

template <std::size_t Size>
Interval absolutePolynomialBound(const PolynomialTerm (&terms)[Size],
                                 const Interval& radius,
                                 int dx = 0, int dy = 0) {
  Interval result(0.0);
  for (const auto& term : terms) {
    if (term.px < dx || term.py < dy) continue;
    result += Interval(0.0, absUpper(coefficient(term)))
        * Interval(static_cast<double>(fallingFactorial(term.px, dx)))
        * Interval(static_cast<double>(fallingFactorial(term.py, dy)))
        * integerPower(radius, term.px + term.py - dx - dy);
  }
  return result;
}

template <std::size_t Size>
bool tableStructureValid(const PolynomialTerm (&terms)[Size],
                         std::size_t expectedSize,
                         int expectedMinimumDegree,
                         int expectedMaximumDegree,
                         bool expectedSqrtTwoFlag) {
  if (Size != expectedSize) return false;
  int minimumDegree = expectedMaximumDegree + 1;
  int maximumDegree = -1;
  std::set<std::pair<int, int>> powers;
  for (const auto& term : terms) {
    if (term.px < 0 || term.py < 0 ||
        term.times_sqrt_two != expectedSqrtTwoFlag) return false;
    const Interval denominator(term.denominator, term.denominator);
    if (denominator.leftBound() <= 0.0) return false;
    const int degree = term.px + term.py;
    minimumDegree = std::min(minimumDegree, degree);
    maximumDegree = std::max(maximumDegree, degree);
    if (!powers.emplace(term.px, term.py).second) return false;
  }
  return minimumDegree == expectedMinimumDegree &&
         maximumDegree == expectedMaximumDegree;
}

Verdict sufficientPositive(const Interval& margin) {
  return margin.leftBound() > 0.0 ? Verdict::Pass : Verdict::Inconclusive;
}

Verdict sufficientMargins(const Enclosures& margins) {
  Verdict result = Verdict::Pass;
  for (const auto& [name, margin] : margins) {
    (void)name;
    result = combine(result, sufficientPositive(margin));
  }
  return result;
}

Interval rationalEndpoint(const char* numerator, const char* denominator) {
  return rfsn::rigorous::exactRational(numerator, denominator);
}

Interval intervalFromEndpoints(const char* lowerNumerator,
                               const char* lowerDenominator,
                               const char* upperNumerator,
                               const char* upperDenominator) {
  const Interval lower = rationalEndpoint(lowerNumerator, lowerDenominator);
  const Interval upper = rationalEndpoint(upperNumerator, upperDenominator);
  return Interval(lower.leftBound(), upper.rightBound());
}

std::string enclosureObjectJson(const Enclosures& enclosures) {
  std::ostringstream output;
  output << '{';
  for (std::size_t index = 0; index < enclosures.size(); ++index) {
    if (index) output << ',';
    output << '"' << rfsn::rigorous::jsonEscape(enclosures[index].first)
           << "\":" << intervalJson(enclosures[index].second);
  }
  output << '}';
  return output.str();
}

struct Obligation {
  std::string id;
  Verdict status;
  std::string predicate;
  Enclosures enclosures;
};

std::string obligationJson(const Obligation& obligation) {
  std::ostringstream output;
  output << "{\"id\":\"" << rfsn::rigorous::jsonEscape(obligation.id)
         << "\",\"status\":\"" << verdictName(obligation.status)
         << "\",\"predicate\":\""
         << rfsn::rigorous::jsonEscape(obligation.predicate)
         << "\",\"enclosures\":"
         << enclosureObjectJson(obligation.enclosures) << '}';
  return output.str();
}

void append(Enclosures& target, const Enclosures& source) {
  target.insert(target.end(), source.begin(), source.end());
}

}  // namespace

int main(int argc, char** argv) {
  try {
    if (argc != 19) {
      throw std::invalid_argument(
          "expected 18 rational arguments: bridge endpoints, R, rho, eta");
    }
    const char* const* value = argv + 1;
    const Interval r = intervalFromEndpoints(
        value[0], value[1], value[2], value[3]);
    const Interval a2 = intervalFromEndpoints(
        value[4], value[5], value[6], value[7]);
    const Interval epsilon = intervalFromEndpoints(
        value[8], value[9], value[10], value[11]);
    const Interval radius = rationalEndpoint(value[12], value[13]);
    const Interval rho = rationalEndpoint(value[14], value[15]);
    const Interval eta = rationalEndpoint(value[16], value[17]);

    const auto rounding = rfsn::rigorous::runRoundingSelfTests();
    const bool materializedCenterStructure =
        tableStructureValid(kH1Terms, 54, 2, 10, false) &&
        tableStructureValid(kH2Terms, 63, 2, 10, false) &&
        tableStructureValid(kDefect1Terms, 361, 11, 29, true) &&
        tableStructureValid(kDefect2Terms, 361, 11, 29, true);

    // Absolute coefficient sums preserve the exact degree-ten cancellations
    // materialized in the frozen term table.  Frobenius/Hilbert--Schmidt
    // bounds dominate the operator and bilinear norms used below.
    const Interval h1 = absolutePolynomialBound(kH1Terms, radius);
    const Interval h2 = absolutePolynomialBound(kH2Terms, radius);
    const Interval h = sqrt(sqr(h1) + sqr(h2));
    const Interval h1x = absolutePolynomialBound(
        kH1Terms, radius, 1, 0);
    const Interval h1y = absolutePolynomialBound(
        kH1Terms, radius, 0, 1);
    const Interval h2x = absolutePolynomialBound(
        kH2Terms, radius, 1, 0);
    const Interval h2y = absolutePolynomialBound(
        kH2Terms, radius, 0, 1);
    const Interval dh = sqrt(sqr(h1x) + sqr(h1y) +
                             sqr(h2x) + sqr(h2y));
    const Interval h1xx = absolutePolynomialBound(
        kH1Terms, radius, 2, 0);
    const Interval h1xy = absolutePolynomialBound(
        kH1Terms, radius, 1, 1);
    const Interval h1yy = absolutePolynomialBound(
        kH1Terms, radius, 0, 2);
    const Interval h2xx = absolutePolynomialBound(
        kH2Terms, radius, 2, 0);
    const Interval h2xy = absolutePolynomialBound(
        kH2Terms, radius, 1, 1);
    const Interval h2yy = absolutePolynomialBound(
        kH2Terms, radius, 0, 2);
    const Interval d2h = sqrt(
        sqr(h1xx) + Interval(2.0) * sqr(h1xy) + sqr(h1yy) +
        sqr(h2xx) + Interval(2.0) * sqr(h2xy) + sqr(h2yy));

    const Interval defect1 = absolutePolynomialBound(
        kDefect1Terms, radius);
    const Interval defect2 = absolutePolynomialBound(
        kDefect2Terms, radius);
    const Interval coreDefect = sqrt(sqr(defect1) + sqr(defect2));
    const Interval coreDefectDerivative = sqrt(
        sqr(absolutePolynomialBound(kDefect1Terms, radius, 1, 0)) +
        sqr(absolutePolynomialBound(kDefect1Terms, radius, 0, 1)) +
        sqr(absolutePolynomialBound(kDefect2Terms, radius, 1, 0)) +
        sqr(absolutePolynomialBound(kDefect2Terms, radius, 0, 1)));

    const Interval rootEpsilon = sqrt(epsilon);
    const Interval r2 = sqr(r);
    const Interval r3 = r2 * r;
    const Interval r4 = sqr(r2);
    const Interval a = Interval(1.0) + rootEpsilon * r3 * a2;
    const Interval b = rootEpsilon * r2 / Interval(3.0);
    const Interval c = Interval(2.0) * r * a2 +
                       rootEpsilon * r4 * sqr(a2);
    const Interval alpha = sqrt(Interval(2.0) + c) * Interval(0.5);
    const Interval beta = sqrt(Interval(2.0) - c) * Interval(0.5);
    const Interval lambda = Interval(1.0) / sqrt(Interval(2.0));
    const Interval determinantAbsolute = Interval(4.0) - sqr(c);
    const Interval qNorm = Interval(1.0) / sqrt(determinantAbsolute);
    const Interval q1 = Interval(1.0) / (Interval(4.0) * alpha);
    const Interval q2 = -Interval(1.0) / (Interval(4.0) * beta);
    const Interval q01 = lambda * Interval(0.5);
    const Interval q02 = -q01;
    const Interval deltaBlock = sqrt(
        sqr(alpha - lambda) + sqr(beta - lambda));
    const Interval deltaQ = sqrt(sqr(q1 - q01) + sqr(q2 - q02));
    const Interval deltaA = (a - Interval(1.0)).abs();
    const Interval absoluteB = b.abs();
    const Interval absoluteC = c.abs();

    // These are precisely the symbolically differenced scalar majorants
    // frozen before the P2b0 interval run.
    const Interval x0Bound = radius + h;
    const Interval xBound = x0Bound + rho;
    const Interval cq = deltaQ * (Interval(1.0) + deltaA) +
                        Interval(0.5) * deltaA;
    const Interval deltaG =
        (cq + qNorm * absoluteB * x0Bound) * sqr(x0Bound);
    const Interval deltaGPrime = Interval(2.0) * cq * x0Bound +
        Interval(3.0) * qNorm * absoluteB * sqr(x0Bound);
    const Interval e0 = coreDefect + deltaBlock * h +
        (Interval(1.0) + dh) * deltaG +
        dh * deltaBlock * radius;
    const Interval e1 = coreDefectDerivative + deltaBlock * dh +
        (Interval(1.0) + dh) * deltaGPrime +
        d2h * (deltaBlock * radius + deltaG) +
        dh * (deltaBlock +
              (Interval(1.0) + dh) * deltaGPrime);
    const Interval ell = qNorm *
        (Interval(2.0) * (Interval(1.0) + deltaA) * xBound +
         Interval(3.0) * absoluteB * sqr(xBound));
    const Interval secondNonlinear = qNorm *
        (Interval(2.0) * (Interval(1.0) + deltaA) +
         Interval(6.0) * absoluteB * xBound);
    const Interval kappa = alpha - (Interval(1.0) + dh) * ell;
    const Interval gu = e1 +
        (d2h * ell + sqr(Interval(1.0) + dh) * secondNonlinear) * rho;
    const Interval c0Inward = kappa * rho - e0;
    const Interval c1Cone = Interval(2.0) * kappa * eta - gu -
                            ell * sqr(eta);

    const Enclosures referenceMargins = {
        {"h10_euclidean_reference_margin",
         rationalEndpoint("33", "1000000") - h},
        {"dh10_frobenius_reference_margin",
         rationalEndpoint("21", "4000") - dh},
        {"d2h10_frobenius_reference_margin",
         rationalEndpoint("427", "1000") - d2h},
        {"core_defect_euclidean_reference_margin",
         rationalEndpoint("23", "10000000000000000000000000") -
             coreDefect},
        {"core_defect_derivative_frobenius_reference_margin",
         rationalEndpoint("21", "10000000000000000000000") -
             coreDefectDerivative}};
    const Enclosures parameterMargins = {
        {"absolute_a_minus_one_parameter_margin",
         rationalEndpoint("11", "78125") - deltaA},
        {"b_parameter_margin",
         rationalEndpoint("22", "9375") - absoluteB},
        {"absolute_c_parameter_margin",
         rationalEndpoint("156261", "3906250") - absoluteC},
        {"alpha_parameter_margin",
         alpha - rationalEndpoint("699", "1000")},
        {"q_norm_parameter_margin",
         rationalEndpoint("501", "1000") - qNorm},
        {"delta_block_operator_parameter_margin",
         rationalEndpoint("101", "10000") - deltaBlock},
        {"delta_q_norm_parameter_margin",
         rationalEndpoint("51", "10000") - deltaQ}};
    const Enclosures acceptanceMargins = {
        {"center_residual_euclidean_margin",
         rationalEndpoint("3", "2000000") - e0},
        {"center_residual_derivative_frobenius_margin",
         rationalEndpoint("27", "100000") - e1},
        {"weighted_nonlinear_lipschitz_margin",
         rationalEndpoint("101", "10000") - ell},
        {"weighted_nonlinear_second_margin",
         rationalEndpoint("101", "100") - secondNonlinear},
        {"normal_contraction_margin",
         kappa - rationalEndpoint("17", "25")},
        {"c0_inward_margin_margin",
         c0Inward - rationalEndpoint("19", "10000000")},
        {"c1_cone_margin_margin",
         c1Cone - rationalEndpoint("1", "8000")}};

    Enclosures c0Margins = {
        referenceMargins[0], referenceMargins[1], referenceMargins[3]};
    append(c0Margins, parameterMargins);
    c0Margins.push_back(acceptanceMargins[0]);
    c0Margins.push_back(acceptanceMargins[2]);
    c0Margins.push_back(acceptanceMargins[4]);
    c0Margins.push_back(acceptanceMargins[5]);
    Verdict c0Status = sufficientMargins(c0Margins);
    if (!materializedCenterStructure) c0Status = Verdict::Fail;

    const Enclosures c1OwnMargins = {
        referenceMargins[2], referenceMargins[4], acceptanceMargins[1],
        acceptanceMargins[3], acceptanceMargins[6]};
    Verdict c1Status = combine(c0Status, sufficientMargins(c1OwnMargins));
    if (!materializedCenterStructure) c1Status = Verdict::Fail;

    const Obligation c0Obligation{
        "V2.WU.H10_C0_TUBE", c0Status,
        "The true parameter-dependent local graphs stay in the frozen "
        "Euclidean C0 tube about the degree-ten core graph on the full "
        "continuation bridge",
        c0Margins};
    const Obligation c1Obligation{
        "V2.WU.H10_C1_TUBE", c1Status,
        "The state derivative of each true parameter-dependent local graph "
        "stays in the frozen Frobenius C1 tube about the degree-ten core "
        "graph on the full continuation bridge",
        c1OwnMargins};
    const std::array<Obligation, 2> obligations = {
        c0Obligation, c1Obligation};

    Verdict mathematicalStatus = Verdict::Pass;
    for (const auto& obligation : obligations)
      mathematicalStatus = combine(mathematicalStatus, obligation.status);
    const Verdict probeStatus = combine(rounding.status, mathematicalStatus);

    const Enclosures parameterEnclosures = {
        {"r", r}, {"a2", a2}, {"epsilon", epsilon},
        {"radius", radius}, {"rho", rho}, {"eta", eta},
        {"a", a}, {"b", b}, {"c", c}, {"alpha", alpha},
        {"beta", beta}, {"q_norm", qNorm},
        {"absolute_a_minus_one", deltaA}, {"absolute_c", absoluteC},
        {"delta_block_operator", deltaBlock}, {"delta_q_norm", deltaQ}};
    const Enclosures centerEnclosures = {
        {"h10_component_1_abs", h1},
        {"h10_component_2_abs", h2},
        {"h10_euclidean", h},
        {"dh10_frobenius", dh},
        {"d2h10_frobenius", d2h},
        {"core_defect_euclidean", coreDefect},
        {"core_defect_derivative_frobenius", coreDefectDerivative},
        {"X0", x0Bound}, {"X", xBound}, {"Cq", cq},
        {"delta_G", deltaG}, {"delta_G_prime", deltaGPrime},
        {"E0", e0}, {"E1", e1}, {"ell", ell},
        {"m", secondNonlinear}, {"kappa", kappa}, {"Gu", gu},
        {"c0_inward_margin", c0Inward},
        {"c1_cone_margin", c1Cone}};

    std::cout
        << "{\"schema_version\":\"rfsn-vdp-p2-h10-c01-probe/1\","
        << "\"status\":\"" << verdictName(probeStatus) << "\","
        << "\"mathematical_status\":\""
        << verdictName(mathematicalStatus) << "\","
        << "\"materialized_center_structure\":"
        << (materializedCenterStructure ? "true" : "false") << ','
        << "\"rounding_self_test\":"
        << rfsn::rigorous::roundingReportJson(rounding) << ','
        << "\"parameter_enclosures\":"
        << enclosureObjectJson(parameterEnclosures) << ','
        << "\"center_enclosures\":"
        << enclosureObjectJson(centerEnclosures) << ','
        << "\"reference_gate_margins\":"
        << enclosureObjectJson(referenceMargins) << ','
        << "\"parameter_gate_margins\":"
        << enclosureObjectJson(parameterMargins) << ','
        << "\"acceptance_gate_margins\":"
        << enclosureObjectJson(acceptanceMargins) << ','
        << "\"obligations\":[";
    for (std::size_t index = 0; index < obligations.size(); ++index) {
      if (index) std::cout << ',';
      std::cout << obligationJson(obligations[index]);
    }
    std::cout << "]}\n";

    if (probeStatus == Verdict::Pass) return 0;
    return probeStatus == Verdict::Fail ? 1 : 2;
  } catch (const std::exception& error) {
    std::cout
        << "{\"schema_version\":\"rfsn-vdp-p2-h10-c01-probe/1\","
        << "\"status\":\"INCONCLUSIVE\","
        << "\"mathematical_status\":\"INCONCLUSIVE\","
        << "\"error\":\"" << rfsn::rigorous::jsonEscape(error.what())
        << "\"}\n";
    return 2;
  }
}
