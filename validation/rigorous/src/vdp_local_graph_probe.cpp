#include "exact_polynomial.hpp"
#include "interval_io.hpp"
#include "rounding_self_test.hpp"
#include "verdict.hpp"

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

using ExactMatrix = std::array<std::array<Polynomial, 4>, 4>;

ExactMatrix exactProduct(const ExactMatrix& left, const ExactMatrix& right) {
  ExactMatrix result{};
  for (std::size_t row = 0; row < 4; ++row)
    for (std::size_t column = 0; column < 4; ++column)
      for (std::size_t index = 0; index < 4; ++index)
        result[row][column] = result[row][column]
            + left[row][index] * right[index][column];
  return result;
}

ExactMatrix exactScale(const Polynomial& factor, const ExactMatrix& value) {
  ExactMatrix result{};
  for (std::size_t row = 0; row < 4; ++row)
    for (std::size_t column = 0; column < 4; ++column)
      result[row][column] = factor * value[row][column];
  return result;
}

bool exactMovingFrameDerivation() {
  // Rationally parameterize alpha^2+beta^2=1 by
  // alpha=(1-t^2)/(1+t^2), beta=2t/(1+t^2).  Clearing the positive
  // denominator reduces every frame, block, reverser, and nonlinear-split
  // identity to an exact polynomial identity over Q[t].
  const Polynomial zero;
  const Polynomial one(Rational(1));
  const Polynomial two(Rational(2));
  const Polynomial four(Rational(4));
  const Polynomial half(Rational(1, 2));
  const Polynomial quarter(Rational(1, 4));
  const Polynomial t = Polynomial::variable(0);
  const Polynomial d = one + power(t, 2);
  const Polynomial alphaNumerator = one - power(t, 2);
  const Polynomial betaNumerator = two * t;
  const Polynomial cNumerator = four * power(alphaNumerator, 2)
      - two * power(d, 2);
  const Polynomial hNumerator = four * t * alphaNumerator;

  // S=d^2 T and Atilde=d^2 A in physical row order (U,P,V,Q).
  const ExactMatrix s = {{
      {{power(d, 2), zero, power(d, 2), zero}},
      {{alphaNumerator * d, -betaNumerator * d,
        -alphaNumerator * d, betaNumerator * d}},
      {{half * cNumerator, hNumerator,
        half * cNumerator, hNumerator}},
      {{alphaNumerator * d, betaNumerator * d,
        -alphaNumerator * d, -betaNumerator * d}},
  }};
  const ExactMatrix physical = {{
      {{zero, power(d, 2), zero, zero}},
      {{cNumerator, zero, -power(d, 2), zero}},
      {{zero, zero, zero, power(d, 2)}},
      {{power(d, 2), zero, zero, zero}},
  }};
  const ExactMatrix blocks = {{
      {{alphaNumerator, -betaNumerator, zero, zero}},
      {{betaNumerator, alphaNumerator, zero, zero}},
      {{zero, zero, -alphaNumerator, betaNumerator}},
      {{zero, zero, -betaNumerator, -alphaNumerator}},
  }};
  if (exactProduct(physical, s) !=
      exactScale(d, exactProduct(s, blocks))) return false;

  const ExactMatrix physicalReverser = {{
      {{one, zero, zero, zero}},
      {{zero, -one, zero, zero}},
      {{zero, zero, one, zero}},
      {{zero, zero, zero, -one}},
  }};
  const ExactMatrix coordinateSwap = {{
      {{zero, zero, one, zero}},
      {{zero, zero, zero, one}},
      {{one, zero, zero, zero}},
      {{zero, one, zero, zero}},
  }};
  if (exactProduct(physicalReverser, s) !=
      exactProduct(s, coordinateSwap)) return false;

  const std::array<Polynomial, 4> splitNumerator = {
      quarter * betaNumerator, -quarter * alphaNumerator,
      -quarter * betaNumerator, quarter * alphaNumerator};
  std::array<Polynomial, 4> splitPhysical{};
  for (std::size_t row = 0; row < 4; ++row)
    for (std::size_t column = 0; column < 4; ++column)
      splitPhysical[row] = splitPhysical[row]
          + s[row][column] * splitNumerator[column];
  const std::array<Polynomial, 4> expectedSplit = {
      zero, alphaNumerator * betaNumerator * d, zero, zero};
  return splitPhysical == expectedSplit;
}

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
      output << '"'
             << rfsn::rigorous::jsonEscape(obligation.enclosures[index].first)
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
    if (argc != 1 && argc != 15) {
      throw std::invalid_argument(
          "expected no arguments or 14 rational endpoint/radius arguments");
    }
    const char* defaults[] = {
        "0", "1", "2", "25", "-1", "4", "1", "4",
        "4", "5", "6", "5", "1", "100"};
    const char* const* value = argc == 1 ? defaults : argv + 1;

    const Interval r = intervalFromEndpoints(
        value[0], value[1], value[2], value[3]);
    const Interval a2 = intervalFromEndpoints(
        value[4], value[5], value[6], value[7]);
    const Interval epsilon = intervalFromEndpoints(
        value[8], value[9], value[10], value[11]);
    const Interval radius = rationalEndpoint(value[12], value[13]);

    const auto rounding = rfsn::rigorous::runRoundingSelfTests();
    const bool exactFrameDerivation = exactMovingFrameDerivation();
    const Interval rootEpsilon = sqrt(epsilon);
    const Interval r2 = sqr(r);
    const Interval r3 = r2 * r;
    const Interval r4 = sqr(r2);
    const Interval a = Interval(1.0) + rootEpsilon * r3 * a2;
    const Interval b = rootEpsilon * r2 / Interval(3.0);
    const Interval c = Interval(2.0) * r * a2
                     + rootEpsilon * r4 * sqr(a2);
    const Interval alpha = sqrt(Interval(2.0) + c) * Interval(0.5);
    const Interval beta = sqrt(Interval(2.0) - c) * Interval(0.5);

    // The identities alpha^2=(2+c)/4 and beta^2=(2-c)/4 give
    // |det T|=4-c^2 and ||(1/(4 alpha),-1/(4 beta))||=1/sqrt(4-c^2).
    // Evaluating these reduced expressions avoids artificial dependency loss.
    const Interval determinantAbsolute = Interval(4.0) - sqr(c);
    const Interval nonlinearSplitNorm =
        Interval(1.0) / sqrt(determinantAbsolute);
    const Interval absoluteA = a.abs();
    const Interval absoluteB = b.abs();

    // Under the already established slope-one cone, |U|<=2||u|| and
    // |n(U)| <= coarseFactor ||u||^2.
    const Interval coarseFactor = Interval(4.0) * absoluteA
        + Interval(8.0) * absoluteB * radius;
    const Interval derivativeBound = Interval(4.0) * absoluteA * radius
        + Interval(12.0) * absoluteB * sqr(radius);
    const Interval faceMargin = alpha * radius
        - nonlinearSplitNorm * coarseFactor * sqr(radius);
    const Interval differenceConeMargin = Interval(2.0) * alpha
        - Interval(4.0) * nonlinearSplitNorm * derivativeBound;

    std::vector<std::pair<std::string, Interval>> frameMargins = {
        {"four_minus_c_squared", determinantAbsolute},
        {"two_plus_c", Interval(2.0) + c},
        {"two_minus_c", Interval(2.0) - c},
        {"alpha", alpha},
        {"beta", beta},
        {"unstable_face_outward_margin", faceMargin},
        {"stable_face_inward_margin", faceMargin},
        {"difference_cone_margin", differenceConeMargin}};

    const Interval gamma0 = alpha
        - nonlinearSplitNorm * coarseFactor * radius;
    const Interval k0 = nonlinearSplitNorm * coarseFactor
        / (alpha + Interval(2.0) * gamma0);
    const Interval firstBootstrapMargin = Interval(1.0) - k0;

    // This refinement is used only after K0<1 has been proved.  It follows
    // from variation of constants and therefore does not enter the cone proof.
    const Interval stretch = Interval(1.0) + k0 * radius;
    const Interval refinedFactor = absoluteA * sqr(stretch)
        + absoluteB * radius * power(stretch, 3);
    const Interval gamma1 = alpha
        - nonlinearSplitNorm * refinedFactor * radius;
    const Interval k1 = nonlinearSplitNorm * refinedFactor
        / (alpha + Interval(2.0) * gamma1);
    const Interval refinedBootstrapMargin = Interval(0.25) - k1;
    const Interval decayMargin = gamma1
        - rfsn::rigorous::exactRational("2", "3");

    std::vector<std::pair<std::string, Interval>> graphMargins = {
        {"gamma0", gamma0},
        {"one_minus_first_quadratic_coefficient", firstBootstrapMargin},
        {"gamma1", gamma1},
        {"one_quarter_minus_refined_quadratic_coefficient",
         refinedBootstrapMargin},
        {"gamma1_minus_two_thirds", decayMargin}};

    Verdict frameStatus = combineMargins(frameMargins);
    if (!exactFrameDerivation) frameStatus = Verdict::Fail;
    const Obligation frame{
        "V2.WU.FRAME_BLOCK", frameStatus,
        "The closed-form moving eigenframe is nonsingular and its radius-1/100 "
        "block has strict unstable/stable face and difference-cone margins "
        "on the full continuation bridge",
        frameMargins};
    const Obligation graph{
        "V2.WU.COARSE_GRAPH", combineMargins(graphMargins),
        "The non-circular graph-transform bootstrap gives true reversible "
        "local graphs with Lipschitz constant at most one, quadratic value "
        "coefficient below one quarter, and backward coordinate decay above "
        "two thirds on the full continuation bridge",
        graphMargins};
    const std::array<Obligation, 2> obligations = {frame, graph};

    Verdict mathematicalStatus = Verdict::Pass;
    for (const auto& obligation : obligations)
      mathematicalStatus = combine(mathematicalStatus, obligation.status);
    const Verdict probeStatus = combine(rounding.status, mathematicalStatus);

    std::cout << "{\"schema_version\":\"rfsn-vdp-p2-local-graph-probe/1\","
              << "\"status\":\"" << verdictName(probeStatus) << "\","
              << "\"mathematical_status\":\""
              << verdictName(mathematicalStatus) << "\","
              << "\"exact_frame_derivation\":"
              << (exactFrameDerivation ? "true" : "false") << ','
              << "\"rounding_self_test\":"
              << rfsn::rigorous::roundingReportJson(rounding) << ','
              << "\"parameter_enclosures\":{"
              << "\"r\":" << intervalJson(r) << ','
              << "\"a2\":" << intervalJson(a2) << ','
              << "\"epsilon\":" << intervalJson(epsilon) << ','
              << "\"a\":" << intervalJson(a) << ','
              << "\"b\":" << intervalJson(b) << ','
              << "\"c\":" << intervalJson(c) << ','
              << "\"alpha\":" << intervalJson(alpha) << ','
              << "\"beta\":" << intervalJson(beta) << ','
              << "\"radius\":" << intervalJson(radius) << ','
              << "\"nonlinear_split_norm\":"
              << intervalJson(nonlinearSplitNorm) << ','
              << "\"first_quadratic_coefficient\":" << intervalJson(k0)
              << ','
              << "\"refined_quadratic_coefficient\":" << intervalJson(k1)
              << "},\"obligations\":[";
    for (std::size_t index = 0; index < obligations.size(); ++index) {
      if (index) std::cout << ',';
      std::cout << obligationJson(obligations[index]);
    }
    std::cout << "]}\n";
    if (probeStatus == Verdict::Pass) return 0;
    return probeStatus == Verdict::Fail ? 1 : 2;
  } catch (const std::exception& error) {
    std::cout << "{\"schema_version\":\"rfsn-vdp-p2-local-graph-probe/1\","
              << "\"status\":\"INCONCLUSIVE\","
              << "\"mathematical_status\":\"INCONCLUSIVE\","
              << "\"error\":\"" << rfsn::rigorous::jsonEscape(error.what())
              << "\"}\n";
    return 2;
  }
}
