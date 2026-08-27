#include "exact_polynomial.hpp"
#include "interval_io.hpp"
#include "rounding_self_test.hpp"
#include "verdict.hpp"

#include <algorithm>
#include <array>
#include <exception>
#include <iostream>
#include <sstream>
#include <string>
#include <utility>
#include <vector>

namespace {

using rfsn::rigorous::Interval;
using rfsn::rigorous::Verdict;
using rfsn::rigorous::combine;
using rfsn::rigorous::intervalJson;
using rfsn::rigorous::verdictName;
using rfsn::rigorous::exact::Polynomial;
using rfsn::rigorous::exact::Rational;
using rfsn::rigorous::exact::power;

struct Obligation {
  std::string id;
  Verdict status;
  std::string predicate;
  std::vector<std::pair<std::string, Interval>> enclosures;
};

Verdict strictPositive(const Interval& margin) {
  if (margin.leftBound() > 0.0) return Verdict::Pass;
  if (margin.rightBound() <= 0.0) return Verdict::Fail;
  return Verdict::Inconclusive;
}

Verdict combineMargins(
    const std::vector<std::pair<std::string, Interval>>& margins) {
  Verdict result = Verdict::Pass;
  for (const auto& [name, margin] : margins) {
    (void)name;
    result = combine(result, strictPositive(margin));
  }
  return result;
}

std::array<Obligation, 2> exactV1Obligations() {
  enum Variable : std::size_t { U, P, V, Q, A, EPSILON, DELTA };
  const Polynomial u = Polynomial::variable(U);
  const Polynomial p = Polynomial::variable(P);
  const Polynomial v = Polynomial::variable(V);
  const Polynomial q = Polynomial::variable(Q);
  const Polynomial a = Polynomial::variable(A);
  const Polynomial epsilon = Polynomial::variable(EPSILON);
  const Polynomial delta = Polynomial::variable(DELTA);
  const Polynomial inverseDelta = Polynomial::variable(DELTA, -1);

  const Polynomial f = Polynomial(Rational(1, 3)) * power(u, 3) - u;
  const Polynomial primitiveF =
      Polynomial(Rational(1, 12)) * power(u, 4) -
      Polynomial(Rational(1, 2)) * power(u, 2);
  const std::array<Polynomial, 4> field = {
      p, f - v, delta * q, epsilon * delta * (u - a)};
  const Polynomial firstIntegral =
      Polynomial(Rational(1, 2)) *
          (epsilon * power(p, 2) - power(q, 2)) -
      epsilon * (primitiveF + (a - u) * v);
  const Polynomial hamiltonian = -firstIntegral;
  const std::array<Polynomial, 4> primitive = {
      epsilon * p, Polynomial(), -inverseDelta * q, Polynomial()};
  const std::array<Polynomial, 4> contraction = {
      epsilon * field[1], -epsilon * field[0],
      -inverseDelta * field[3], inverseDelta * field[2]};

  bool hamiltonianIdentity = true;
  for (std::size_t index = 0; index < 4; ++index) {
    hamiltonianIdentity = hamiltonianIdentity &&
                          contraction[index] == hamiltonian.derivative(index);
  }
  Polynomial firstIntegralDerivative;
  for (std::size_t index = 0; index < 4; ++index) {
    firstIntegralDerivative =
        firstIntegralDerivative + firstIntegral.derivative(index) * field[index];
  }
  hamiltonianIdentity = hamiltonianIdentity && firstIntegralDerivative.isZero();

  const std::array<int, rfsn::rigorous::exact::kVariableCount> signs =
      {1, -1, 1, -1, 1, 1, 1};
  bool reversibility = true;
  for (std::size_t index = 0; index < 4; ++index) {
    reversibility = reversibility &&
        (field[index].signSubstitution(signs) +
         Polynomial(Rational(signs[index])) * field[index]).isZero();
    reversibility = reversibility &&
        (Polynomial(Rational(signs[index])) *
             primitive[index].signSubstitution(signs) +
         primitive[index]).isZero();
  }

  return {{
      {"V1.REVERSIBILITY", reversibility ? Verdict::Pass : Verdict::Fail,
       "Exact Laurent-polynomial identities DR X = -X o R and R*lambda = -lambda",
       {}},
      {"V1.HAMILTONIAN", hamiltonianIdentity ? Verdict::Pass : Verdict::Fail,
       "Exact Laurent-polynomial identities i_X d lambda = dH and dG/dy = 0",
       {}}
  }};
}

bool exactCharacteristicPolynomial() {
  const Polynomial spectral = Polynomial::variable(0);
  const Polynomial c = Polynomial::variable(1);
  const Polynomial zero;
  const Polynomial one(Rational(1));
  const std::array<std::array<Polynomial, 4>, 4> spectralMatrix = {{
      {{spectral, -one, zero, zero}},
      {{-c, spectral, one, zero}},
      {{zero, zero, spectral, -one}},
      {{-one, zero, zero, spectral}},
  }};
  Polynomial determinant;
  std::array<int, 4> permutation = {0, 1, 2, 3};
  do {
    int inversions = 0;
    for (std::size_t left = 0; left < permutation.size(); ++left)
      for (std::size_t right = left + 1; right < permutation.size(); ++right)
        if (permutation[left] > permutation[right]) ++inversions;
    Polynomial term(Rational((inversions & 1) ? -1 : 1));
    for (std::size_t row = 0; row < permutation.size(); ++row)
      term = term * spectralMatrix[row][permutation[row]];
    determinant = determinant + term;
  } while (std::next_permutation(permutation.begin(), permutation.end()));
  const Polynomial expected = power(spectral, 4) - c * power(spectral, 2) + one;
  return determinant == expected;
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

std::string obligationJson(const Obligation& obligation) {
  std::ostringstream output;
  output << "{\"id\":\"" << rfsn::rigorous::jsonEscape(obligation.id)
         << "\",\"status\":\"" << verdictName(obligation.status)
         << "\",\"predicate\":\""
         << rfsn::rigorous::jsonEscape(obligation.predicate) << "\"";
  if (!obligation.enclosures.empty()) {
    output << ",\"enclosures\":{";
    for (std::size_t index = 0; index < obligation.enclosures.size(); ++index) {
      if (index) output << ',';
      output << '"' << rfsn::rigorous::jsonEscape(
                              obligation.enclosures[index].first)
             << "\":" << intervalJson(obligation.enclosures[index].second);
    }
    output << '}';
  }
  output << '}';
  return output.str();
}

}  // namespace

int main(int argc, char** argv) {
  try {
    if (argc != 1 && argc != 13) {
      throw std::invalid_argument(
          "expected no arguments or 12 rational endpoint arguments");
    }
    const char* defaults[] = {"1", "25", "2", "25", "-1", "4",
                              "1", "4", "4", "5", "6", "5"};
    const char* const* value = argc == 1 ? defaults : argv + 1;
    const Interval r = intervalFromEndpoints(value[0], value[1], value[2], value[3]);
    const Interval a2 = intervalFromEndpoints(value[4], value[5], value[6], value[7]);
    const Interval epsilon =
        intervalFromEndpoints(value[8], value[9], value[10], value[11]);

    const auto rounding = rfsn::rigorous::runRoundingSelfTests();
    const auto exact = exactV1Obligations();
    const bool characteristicPolynomial = exactCharacteristicPolynomial();

    const Interval delta = sqr(r);
    const Interval d = sqr(delta);
    const Interval rootEpsilon = sqrt(epsilon);
    const Interval r3 = delta * r;
    const Interval r4 = d;
    const Interval a = Interval(1.0) + rootEpsilon * r3 * a2;
    const Interval c = Interval(2.0) * r * a2 +
                       rootEpsilon * r4 * sqr(a2);
    const Interval alpha = sqrt(Interval(2.0) + c) * Interval(0.5);
    const Interval beta = sqrt(Interval(2.0) - c) * Interval(0.5);
    const Interval absoluteA2 = a2.abs();

    std::vector<Obligation> obligations(exact.begin(), exact.end());
    std::vector<std::pair<std::string, Interval>> wedgeMargins = {
        {"one_minus_2Ar_minus_sqrtE_A2_r4",
         Interval(1.0) - (Interval(2.0) * r * absoluteA2 +
                          rootEpsilon * sqr(absoluteA2) * r4)},
        {"one_half_minus_sqrtE_A_r3",
         Interval(0.5) - rootEpsilon * absoluteA2 * r3}};
    obligations.push_back(
        {"V2.1.WEDGE", combineMargins(wedgeMargins),
         "The explicit wedge inequalities have strictly positive slack",
         wedgeMargins});

    std::vector<std::pair<std::string, Interval>> positivityMargins = {
        {"r", r}, {"d", d}, {"delta", delta}, {"epsilon", epsilon}, {"a", a}};
    obligations.push_back(
        {"V2.1.POSITIVITY", combineMargins(positivityMargins),
         "r, d, delta, epsilon, and a are uniformly strictly positive",
         positivityMargins});

    std::vector<std::pair<std::string, Interval>> spectralMargins = {
        {"two_plus_c", Interval(2.0) + c},
        {"two_minus_c", Interval(2.0) - c},
        {"alpha_minus_one_half", alpha - Interval(0.5)},
        {"beta_minus_one_half", beta - Interval(0.5)}};
    Verdict spectralStatus = combineMargins(spectralMargins);
    if (!characteristicPolynomial) spectralStatus = Verdict::Fail;
    obligations.push_back(
        {"V2.1.SADDLE_FOCUS", spectralStatus,
         "Exact det(mu I-A)=mu^4-c mu^2+1 and the interval saddle-focus "
         "radicals are real with alpha,beta exceeding one half",
         spectralMargins});

    Verdict mathematicalStatus = Verdict::Pass;
    for (const auto& obligation : obligations)
      mathematicalStatus = combine(mathematicalStatus, obligation.status);
    const Verdict probeStatus = combine(rounding.status, mathematicalStatus);

    std::cout << "{\"schema_version\":\"rfsn-vdp-phase1-probe/1\","
              << "\"status\":\"" << verdictName(probeStatus) << "\","
              << "\"mathematical_status\":\""
              << verdictName(mathematicalStatus) << "\","
              << "\"exact_characteristic_polynomial\":"
              << (characteristicPolynomial ? "true" : "false") << ','
              << "\"rounding_self_test\":"
              << rfsn::rigorous::roundingReportJson(rounding) << ','
              << "\"parameter_enclosures\":{"
              << "\"r\":" << intervalJson(r) << ','
              << "\"a2\":" << intervalJson(a2) << ','
              << "\"epsilon\":" << intervalJson(epsilon) << ','
              << "\"d\":" << intervalJson(d) << ','
              << "\"delta\":" << intervalJson(delta) << ','
              << "\"a\":" << intervalJson(a) << ','
              << "\"c\":" << intervalJson(c) << ','
              << "\"alpha\":" << intervalJson(alpha) << ','
              << "\"beta\":" << intervalJson(beta) << "},"
              << "\"obligations\":[";
    for (std::size_t index = 0; index < obligations.size(); ++index) {
      if (index) std::cout << ',';
      std::cout << obligationJson(obligations[index]);
    }
    std::cout << "]}\n";
    if (probeStatus == Verdict::Pass) return 0;
    return probeStatus == Verdict::Fail ? 1 : 2;
  } catch (const std::exception& error) {
    std::cout << "{\"schema_version\":\"rfsn-vdp-phase1-probe/1\","
              << "\"status\":\"INCONCLUSIVE\","
              << "\"mathematical_status\":\"INCONCLUSIVE\","
              << "\"error\":\"" << rfsn::rigorous::jsonEscape(error.what())
              << "\"}\n";
    return 2;
  }
}
