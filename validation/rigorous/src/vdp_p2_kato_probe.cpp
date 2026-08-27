#include "interval_io.hpp"
#include "rounding_self_test.hpp"
#include "verdict.hpp"

#include <algorithm>
#include <array>
#include <cctype>
#include <cmath>
#include <exception>
#include <iostream>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

// Positional interface (argc=114):
//
//   12 bridge strings: lower/upper rational endpoints for r,a2,epsilon;
//   3 rational pairs: source radius R and the normalized-to-original
//     first/second parameter derivative operator factors;
//   3 positive subdivision integers for theta_r,theta_a,theta_epsilon;
//   9 rational pairs: exact upper endpoints imported from the immutable P2b
//     physical weighted-jet certificate, in the order
//       Z_0_0,Z_0_1,Z_0_2,Z_1_0,Z_1_1,Z_1_2,Z_2_0,Z_2_1,Z_3_0;
//   28 rational acceptance-gate pairs in the frozen configuration order;
//   9 rational true-source-gate pairs in the same order as the imported
//     physical jets, with S in place of Z.
//
// The runner reconstructs every imported P2b upper endpoint as an exact
// rational from its archived IEEE-754 binary64 hexadecimal representation.
// This probe neither parses decimal surrogates nor claims to authenticate the
// prerequisite certificate: revision/hash/status binding belongs to the
// runner and checker.

namespace {

using rfsn::rigorous::Interval;
using rfsn::rigorous::Verdict;
using rfsn::rigorous::combine;
using rfsn::rigorous::intervalJson;
using rfsn::rigorous::verdictName;

constexpr int kParameterDimension = 3;
constexpr int kImportedJetCount = 9;
constexpr int kAcceptanceGateCount = 28;
constexpr int kTrueSourceGateCount = 9;
constexpr int kRationalInputCount =
    3 + kImportedJetCount + kAcceptanceGateCount + kTrueSourceGateCount;
constexpr int kImportedJetOffset = 3;
constexpr int kAcceptanceGateOffset =
    kImportedJetOffset + kImportedJetCount;
constexpr int kTrueSourceGateOffset =
    kAcceptanceGateOffset + kAcceptanceGateCount;
constexpr std::array<int, 3> kExpectedSubdivisions{16, 8, 4};

using Enclosures = std::vector<std::pair<std::string, Interval>>;

constexpr std::array<const char*, kImportedJetCount> kImportedJetNames{
    "Z_0_0", "Z_0_1", "Z_0_2", "Z_1_0", "Z_1_1",
    "Z_1_2", "Z_2_0", "Z_2_1", "Z_3_0"};

constexpr std::array<const char*, kTrueSourceGateCount> kTrueSourceNames{
    "S_0_0", "S_0_1", "S_0_2", "S_1_0", "S_1_1",
    "S_1_2", "S_2_0", "S_2_1", "S_3_0"};

constexpr std::array<const char*, kAcceptanceGateCount> kAcceptanceNames{
    "absolute_c_upper",
    "alpha_lower",
    "beta_lower",
    "normalizer_squared_lower",
    "absolute_y_upper",
    "phase_shift_absolute_upper",
    "phase_rotation_cosine_lower",
    "radial_scale_lower",
    "radial_scale_upper",
    "frame_change_determinant_lower",
    "frame_change_inverse_upper",
    "physical_frame_smallest_singular_lower",
    "physical_frame_operator_upper",
    "normalized_c_first_derivative_upper",
    "normalized_c_second_derivative_upper",
    "normalized_projector_first_derivative_upper",
    "normalized_projector_second_derivative_upper",
    "normalized_phase_first_derivative_upper",
    "normalized_phase_second_derivative_upper",
    "normalized_rotation_first_derivative_upper",
    "normalized_rotation_second_derivative_upper",
    "normalized_change_first_derivative_upper",
    "normalized_change_second_derivative_upper",
    "normalized_frame_first_derivative_upper",
    "normalized_frame_second_derivative_upper",
    "normalized_source_coordinate_first_derivative_upper",
    "normalized_source_coordinate_second_derivative_upper",
    "source_coordinate_phase_speed_lower"};

constexpr std::array<const char*, kRationalInputCount> kInputNames{
    "source_radius",
    "original_parameter_first_derivative_scale",
    "original_parameter_second_derivative_scale",
    "F_0_0", "F_0_1", "F_0_2", "F_1_0", "F_1_1",
    "F_1_2", "F_2_0", "F_2_1", "F_3_0",
    "absolute_c_upper_gate",
    "alpha_lower_gate",
    "beta_lower_gate",
    "normalizer_squared_lower_gate",
    "absolute_y_upper_gate",
    "phase_shift_absolute_upper_gate",
    "phase_rotation_cosine_lower_gate",
    "radial_scale_lower_gate",
    "radial_scale_upper_gate",
    "frame_change_determinant_lower_gate",
    "frame_change_inverse_upper_gate",
    "physical_frame_smallest_singular_lower_gate",
    "physical_frame_operator_upper_gate",
    "normalized_c_first_derivative_upper_gate",
    "normalized_c_second_derivative_upper_gate",
    "normalized_projector_first_derivative_upper_gate",
    "normalized_projector_second_derivative_upper_gate",
    "normalized_phase_first_derivative_upper_gate",
    "normalized_phase_second_derivative_upper_gate",
    "normalized_rotation_first_derivative_upper_gate",
    "normalized_rotation_second_derivative_upper_gate",
    "normalized_change_first_derivative_upper_gate",
    "normalized_change_second_derivative_upper_gate",
    "normalized_frame_first_derivative_upper_gate",
    "normalized_frame_second_derivative_upper_gate",
    "normalized_source_coordinate_first_derivative_upper_gate",
    "normalized_source_coordinate_second_derivative_upper_gate",
    "source_coordinate_phase_speed_lower_gate",
    "S_0_0_gate", "S_0_1_gate", "S_0_2_gate", "S_1_0_gate",
    "S_1_1_gate", "S_1_2_gate", "S_2_0_gate", "S_2_1_gate",
    "S_3_0_gate"};

static_assert(kTrueSourceGateOffset + kTrueSourceGateCount ==
              kRationalInputCount);

struct RationalInput {
  std::string name;
  std::string numerator;
  std::string denominator;
  Interval interval;
};

bool validIntegerText(const std::string& value) {
  if (value.empty()) return false;
  std::size_t index = value.front() == '-' ? 1U : 0U;
  if (index == value.size()) return false;
  for (; index < value.size(); ++index) {
    if (!std::isdigit(static_cast<unsigned char>(value[index]))) return false;
  }
  return true;
}

bool validPositiveIntegerText(const std::string& value) {
  if (!validIntegerText(value) || value.front() == '-') return false;
  try {
    std::size_t consumed = 0;
    const long long parsed = std::stoll(value, &consumed);
    return consumed == value.size() && parsed > 0;
  } catch (const std::exception&) {
    return false;
  }
}

RationalInput readRational(const char* numerator, const char* denominator,
                           const std::string& name) {
  const std::string top(numerator);
  const std::string bottom(denominator);
  if (!validIntegerText(top) || !validPositiveIntegerText(bottom)) {
    throw std::invalid_argument("malformed exact rational for " + name);
  }
  return {name, top, bottom, rfsn::rigorous::exactRational(top, bottom)};
}

Interval readRationalInterval(const char* lowerNumerator,
                              const char* lowerDenominator,
                              const char* upperNumerator,
                              const char* upperDenominator,
                              const std::string& name) {
  const RationalInput lower = readRational(
      lowerNumerator, lowerDenominator, name + "_lower");
  const RationalInput upper = readRational(
      upperNumerator, upperDenominator, name + "_upper");
  if (lower.interval.rightBound() > upper.interval.leftBound()) {
    throw std::invalid_argument("reversed rational interval for " + name);
  }
  return Interval(lower.interval.leftBound(), upper.interval.rightBound());
}

int readPositiveSubdivision(const char* value, const std::string& name) {
  const std::string text(value);
  if (!validPositiveIntegerText(text)) {
    throw std::invalid_argument("malformed positive subdivision for " + name);
  }
  const long long parsed = std::stoll(text);
  if (parsed > 1000000) {
    throw std::invalid_argument("subdivision is unreasonably large for " + name);
  }
  return static_cast<int>(parsed);
}

Interval rationalFromIntegers(long long numerator, long long denominator) {
  if (denominator <= 0) {
    throw std::logic_error("internally generated denominator is not positive");
  }
  return rfsn::rigorous::exactRational(
      std::to_string(numerator), std::to_string(denominator));
}

Interval normalizedCell(int index, int count) {
  if (count <= 0 || index < 0 || index >= count) {
    throw std::logic_error("invalid normalized-grid cell index");
  }
  const Interval left = rationalFromIntegers(-count + 2LL * index, count);
  const Interval right =
      rationalFromIntegers(-count + 2LL * (index + 1), count);
  return Interval(left.leftBound(), right.rightBound());
}

std::vector<Interval> normalizedCells(int count) {
  std::vector<Interval> result;
  result.reserve(static_cast<std::size_t>(count));
  for (int index = 0; index < count; ++index) {
    result.push_back(normalizedCell(index, count));
  }
  return result;
}

bool gapFreeCover(const std::vector<Interval>& cells,
                  const Interval& lower, const Interval& upper) {
  if (cells.empty() || cells.front().leftBound() > lower.leftBound() ||
      cells.back().rightBound() < upper.rightBound()) {
    return false;
  }
  for (std::size_t index = 0; index < cells.size(); ++index) {
    if (cells[index].leftBound() > cells[index].rightBound()) return false;
    if (index > 0 &&
        cells[index - 1].rightBound() < cells[index].leftBound()) {
      return false;
    }
  }
  return true;
}

Interval absoluteEnvelope(const Interval& value) {
  return Interval(0.0, std::max(std::abs(value.leftBound()),
                                std::abs(value.rightBound())));
}

Interval upperEnvelope(const Interval& left, const Interval& right) {
  return Interval(0.0,
                  std::max(left.rightBound(), right.rightBound()));
}

Interval hullIntervals(const Interval& left, const Interval& right) {
  return Interval(std::min(left.leftBound(), right.leftBound()),
                  std::max(left.rightBound(), right.rightBound()));
}

bool containsZero(const Interval& value) {
  return value.leftBound() <= 0.0 && value.rightBound() >= 0.0;
}

bool intervalBitEqual(const Interval& left, const Interval& right) {
  return rfsn::rigorous::bitEqual(left.leftBound(), right.leftBound()) &&
         rfsn::rigorous::bitEqual(left.rightBound(), right.rightBound());
}

struct Jet2 {
  Interval value{0.0};
  std::array<Interval, kParameterDimension> gradient{};
  std::array<std::array<Interval, kParameterDimension>, kParameterDimension>
      hessian{};

  Jet2() = default;
  explicit Jet2(const Interval& valueIn) : value(valueIn) {}

  static Jet2 variable(const Interval& valueIn, int index) {
    Jet2 result(valueIn);
    result.gradient.at(static_cast<std::size_t>(index)) = Interval(1.0);
    return result;
  }
};

Jet2 operator+(const Jet2& left, const Jet2& right) {
  Jet2 result;
  result.value = left.value + right.value;
  for (int i = 0; i < kParameterDimension; ++i) {
    result.gradient[static_cast<std::size_t>(i)] =
        left.gradient[static_cast<std::size_t>(i)] +
        right.gradient[static_cast<std::size_t>(i)];
    for (int j = i; j < kParameterDimension; ++j) {
      const Interval entry =
          left.hessian[static_cast<std::size_t>(i)]
                      [static_cast<std::size_t>(j)] +
          right.hessian[static_cast<std::size_t>(i)]
                       [static_cast<std::size_t>(j)];
      result.hessian[static_cast<std::size_t>(i)]
                    [static_cast<std::size_t>(j)] = entry;
      result.hessian[static_cast<std::size_t>(j)]
                    [static_cast<std::size_t>(i)] = entry;
    }
  }
  return result;
}

Jet2 operator-(const Jet2& value) {
  Jet2 result;
  result.value = -value.value;
  for (int i = 0; i < kParameterDimension; ++i) {
    result.gradient[static_cast<std::size_t>(i)] =
        -value.gradient[static_cast<std::size_t>(i)];
    for (int j = i; j < kParameterDimension; ++j) {
      const Interval entry =
          -value.hessian[static_cast<std::size_t>(i)]
                        [static_cast<std::size_t>(j)];
      result.hessian[static_cast<std::size_t>(i)]
                    [static_cast<std::size_t>(j)] = entry;
      result.hessian[static_cast<std::size_t>(j)]
                    [static_cast<std::size_t>(i)] = entry;
    }
  }
  return result;
}

Jet2 operator-(const Jet2& left, const Jet2& right) {
  return left + (-right);
}

Jet2 operator*(const Jet2& left, const Jet2& right) {
  Jet2 result;
  result.value = left.value * right.value;
  for (int i = 0; i < kParameterDimension; ++i) {
    result.gradient[static_cast<std::size_t>(i)] =
        left.gradient[static_cast<std::size_t>(i)] * right.value +
        left.value * right.gradient[static_cast<std::size_t>(i)];
    for (int j = i; j < kParameterDimension; ++j) {
      const Interval entry =
          left.hessian[static_cast<std::size_t>(i)]
                      [static_cast<std::size_t>(j)] * right.value +
          left.gradient[static_cast<std::size_t>(i)] *
              right.gradient[static_cast<std::size_t>(j)] +
          left.gradient[static_cast<std::size_t>(j)] *
              right.gradient[static_cast<std::size_t>(i)] +
          left.value *
              right.hessian[static_cast<std::size_t>(i)]
                           [static_cast<std::size_t>(j)];
      result.hessian[static_cast<std::size_t>(i)]
                    [static_cast<std::size_t>(j)] = entry;
      result.hessian[static_cast<std::size_t>(j)]
                    [static_cast<std::size_t>(i)] = entry;
    }
  }
  return result;
}

Jet2 operator*(const Interval& scalar, const Jet2& value) {
  return Jet2(scalar) * value;
}

Jet2 compose(const Jet2& argument, const Interval& functionValue,
             const Interval& firstDerivative,
             const Interval& secondDerivative) {
  Jet2 result;
  result.value = functionValue;
  for (int i = 0; i < kParameterDimension; ++i) {
    result.gradient[static_cast<std::size_t>(i)] =
        firstDerivative * argument.gradient[static_cast<std::size_t>(i)];
    for (int j = i; j < kParameterDimension; ++j) {
      const Interval entry =
          secondDerivative *
              argument.gradient[static_cast<std::size_t>(i)] *
              argument.gradient[static_cast<std::size_t>(j)] +
          firstDerivative *
              argument.hessian[static_cast<std::size_t>(i)]
                              [static_cast<std::size_t>(j)];
      result.hessian[static_cast<std::size_t>(i)]
                    [static_cast<std::size_t>(j)] = entry;
      result.hessian[static_cast<std::size_t>(j)]
                    [static_cast<std::size_t>(i)] = entry;
    }
  }
  return result;
}

Jet2 squareRoot(const Jet2& argument) {
  if (argument.value.leftBound() <= 0.0) {
    throw std::logic_error("square-root AD argument is not uniformly positive");
  }
  const Interval root = sqrt(argument.value);
  return compose(argument, root,
                 Interval(1.0) / (Interval(2.0) * root),
                 -Interval(1.0) /
                     (Interval(4.0) * argument.value * root));
}

Jet2 reciprocal(const Jet2& argument) {
  if (containsZero(argument.value)) {
    throw std::logic_error("reciprocal AD argument contains zero");
  }
  const Interval inverse = Interval(1.0) / argument.value;
  return compose(argument, inverse, -inverse * inverse,
                 Interval(2.0) * inverse * inverse * inverse);
}

Jet2 operator/(const Jet2& left, const Jet2& right) {
  return left * reciprocal(right);
}

Jet2 arctangent(const Jet2& argument) {
  const Interval denominator =
      Interval(1.0) + argument.value * argument.value;
  return compose(argument, atan(argument.value),
                 Interval(1.0) / denominator,
                 -Interval(2.0) * argument.value /
                     (denominator * denominator));
}

bool symmetricHessian(const Jet2& value) {
  for (int i = 0; i < kParameterDimension; ++i) {
    for (int j = 0; j < kParameterDimension; ++j) {
      if (!intervalBitEqual(
              value.hessian[static_cast<std::size_t>(i)]
                           [static_cast<std::size_t>(j)],
              value.hessian[static_cast<std::size_t>(j)]
                           [static_cast<std::size_t>(i)])) {
        return false;
      }
    }
  }
  return true;
}

struct JetBounds {
  Interval order0{0.0};
  Interval order1{0.0};
  Interval order2{0.0};
};

JetBounds jetBounds(const std::vector<Jet2>& entries) {
  Interval valueSum(0.0);
  Interval gradientSum(0.0);
  Interval hessianSum(0.0);
  for (const Jet2& entry : entries) {
    valueSum += sqr(absoluteEnvelope(entry.value));
    for (int i = 0; i < kParameterDimension; ++i) {
      gradientSum += sqr(absoluteEnvelope(
          entry.gradient[static_cast<std::size_t>(i)]));
      for (int j = 0; j < kParameterDimension; ++j) {
        hessianSum += sqr(absoluteEnvelope(
            entry.hessian[static_cast<std::size_t>(i)]
                         [static_cast<std::size_t>(j)]));
      }
    }
  }
  return {sqrt(valueSum), sqrt(gradientSum), sqrt(hessianSum)};
}

void maximize(JetBounds& target, const JetBounds& candidate) {
  target.order0 = upperEnvelope(target.order0, candidate.order0);
  target.order1 = upperEnvelope(target.order1, candidate.order1);
  target.order2 = upperEnvelope(target.order2, candidate.order2);
}

Verdict sufficientPositive(const Interval& margin) {
  return margin.leftBound() > 0.0 ? Verdict::Pass : Verdict::Inconclusive;
}

Verdict sufficientMargins(const Enclosures& margins) {
  Verdict result = Verdict::Pass;
  for (const auto& item : margins) {
    result = combine(result, sufficientPositive(item.second));
  }
  return result;
}

std::string enclosureObjectJson(const Enclosures& enclosures) {
  std::ostringstream output;
  output << '{';
  for (std::size_t index = 0; index < enclosures.size(); ++index) {
    if (index > 0) output << ',';
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

bool allStrictlyPositive(const std::vector<RationalInput>& inputs) {
  for (const RationalInput& input : inputs) {
    if (input.interval.leftBound() <= 0.0) return false;
  }
  return true;
}

}  // namespace

int main(int argc, char** argv) {
  try {
    if (argc != 114) {
      throw std::invalid_argument(
          "expected argc=114: 12 bridge strings, 3 rational pairs, 3 "
          "subdivision integers, 9 imported-P2b-upper pairs, 28 "
          "acceptance-gate pairs, and 9 true-source-gate pairs; see the "
          "positional interface comment in vdp_p2_kato_probe.cpp");
    }

    const Interval bridgeR = readRationalInterval(
        argv[1], argv[2], argv[3], argv[4], "r");
    const Interval bridgeA2 = readRationalInterval(
        argv[5], argv[6], argv[7], argv[8], "a2");
    const Interval bridgeEpsilon = readRationalInterval(
        argv[9], argv[10], argv[11], argv[12], "epsilon");

    std::vector<RationalInput> inputs;
    inputs.reserve(kRationalInputCount);
    for (int index = 0; index < 3; ++index) {
      inputs.push_back(readRational(argv[13 + 2 * index],
                                    argv[14 + 2 * index],
                                    kInputNames[static_cast<std::size_t>(index)]));
    }
    const std::array<int, 3> subdivisions{
        readPositiveSubdivision(argv[19], "theta_r"),
        readPositiveSubdivision(argv[20], "theta_a"),
        readPositiveSubdivision(argv[21], "theta_epsilon")};
    for (int index = 3; index < kRationalInputCount; ++index) {
      const int offset = index - 3;
      inputs.push_back(readRational(
          argv[22 + 2 * offset], argv[23 + 2 * offset],
          kInputNames[static_cast<std::size_t>(index)]));
    }
    if (inputs.size() != static_cast<std::size_t>(kRationalInputCount)) {
      throw std::logic_error("P2bK rational input indexing is incomplete");
    }
    const auto input = [&](int index) -> const Interval& {
      return inputs.at(static_cast<std::size_t>(index)).interval;
    };
    const auto acceptance = [&](int index) -> const Interval& {
      return input(kAcceptanceGateOffset + index);
    };
    const auto sourceGate = [&](int index) -> const Interval& {
      return input(kTrueSourceGateOffset + index);
    };

    const auto rounding = rfsn::rigorous::runRoundingSelfTests();
    const Interval& radius = input(0);
    const Interval& firstDerivativeScale = input(1);
    const Interval& secondDerivativeScale = input(2);

    const bool allInputsStrictlyPositive = allStrictlyPositive(inputs);
    const bool subdivisionsMatchFrozenContract =
        subdivisions == kExpectedSubdivisions;
    const Interval expectedBridgeR = readRationalInterval(
        "0", "1", "2", "25", "expected_r");
    const Interval expectedBridgeA2 = readRationalInterval(
        "-1", "4", "1", "4", "expected_a2");
    const Interval expectedBridgeEpsilon = readRationalInterval(
        "4", "5", "6", "5", "expected_epsilon");
    const bool bridgeMatchesNormalization =
        intervalBitEqual(bridgeR, expectedBridgeR) &&
        intervalBitEqual(bridgeA2, expectedBridgeA2) &&
        intervalBitEqual(bridgeEpsilon, expectedBridgeEpsilon);
    const bool derivativeScalesMatchFrozenContract =
        intervalBitEqual(firstDerivativeScale,
                         readRational("25", "1", "first_scale").interval) &&
        intervalBitEqual(secondDerivativeScale,
                         readRational("625", "1", "second_scale").interval);

    const std::vector<Interval> thetaRCells =
        normalizedCells(subdivisions[0]);
    const std::vector<Interval> thetaACells =
        normalizedCells(subdivisions[1]);
    const std::vector<Interval> thetaEpsilonCells =
        normalizedCells(subdivisions[2]);
    const bool gridGapFree =
        gapFreeCover(thetaRCells, Interval(-1.0), Interval(1.0)) &&
        gapFreeCover(thetaACells, Interval(-1.0), Interval(1.0)) &&
        gapFreeCover(thetaEpsilonCells, Interval(-1.0), Interval(1.0));

    bool initialized = false;
    bool adHessiansBitSymmetric = true;
    bool gramEigenvalueEnclosuresNonempty = true;
    Interval cHull(0.0);
    Interval alphaHull(0.0);
    Interval betaHull(0.0);
    Interval normalizerSquaredHull(0.0);
    Interval yHull(0.0);
    Interval chiHull(0.0);
    Interval cosineHull(0.0);
    Interval sigmaHull(0.0);
    Interval determinantHull(0.0);
    Interval inverseHull(0.0);
    Interval tauHull(0.0);
    Interval frameOperatorHull(0.0);
    Interval frameSmallestHull(0.0);
    JetBounds cBounds;
    JetBounds projectorBounds;
    JetBounds chiBounds;
    JetBounds rotationBounds;
    JetBounds changeBounds;
    JetBounds frameBounds;

    for (const Interval& thetaRCell : thetaRCells) {
      for (const Interval& thetaACell : thetaACells) {
        for (const Interval& thetaEpsilonCell : thetaEpsilonCells) {
          const Jet2 thetaR = Jet2::variable(thetaRCell, 0);
          const Jet2 thetaA = Jet2::variable(thetaACell, 1);
          const Jet2 thetaEpsilon = Jet2::variable(thetaEpsilonCell, 2);
          const Jet2 one(Interval(1.0));
          const Jet2 zero(Interval(0.0));
          const Jet2 two(Interval(2.0));
          const Jet2 r = (thetaR + one) / Jet2(Interval(25.0));
          const Jet2 a2 = thetaA / Jet2(Interval(4.0));
          const Jet2 epsilon = one +
                               thetaEpsilon / Jet2(Interval(5.0));
          const Jet2 rootEpsilon = squareRoot(epsilon);
          const Jet2 r2 = r * r;
          const Jet2 r4 = r2 * r2;
          const Jet2 c = Interval(2.0) * r * a2 +
                         rootEpsilon * r4 * a2 * a2;
          const Jet2 alpha = Interval(0.5) * squareRoot(two + c);
          const Jet2 beta = Interval(0.5) * squareRoot(two - c);
          const Jet2 rootTwo = squareRoot(two);
          const Jet2 y = -c /
              (squareRoot(two - c) * (rootTwo + squareRoot(two + c)));
          const Jet2 chi = arctangent(y);
          const Jet2 normalizerSquared =
              Interval(6.0) * alpha * alpha -
              Interval(4.0) * rootTwo * alpha + Jet2(Interval(3.0));
          const Jet2 normalizer = squareRoot(normalizerSquared);
          const Jet2 rotationDenominator = squareRoot(one + y * y);
          const Jet2 cosine = reciprocal(rotationDenominator);
          const Jet2 sigma = rotationDenominator / normalizer;
          const Jet2 determinant = sigma * sigma;
          const Jet2 inverseNorm = reciprocal(sigma);

          const std::array<std::array<Jet2, 2>, 2> change{{
              {{one / normalizer, -y / normalizer}},
              {{y / normalizer, one / normalizer}},
          }};
          const std::array<std::array<Jet2, 2>, 2> rotation{{
              {{one / rotationDenominator, -y / rotationDenominator}},
              {{y / rotationDenominator, one / rotationDenominator}},
          }};
          const Jet2 projectorScale =
              one / (Interval(4.0) * alpha);
          const Jet2 half(Interval(0.5));
          const std::array<std::array<Jet2, 4>, 4> projector{{
              {{half, projectorScale, zero, projectorScale}},
              {{(one + c) * projectorScale, half,
                -projectorScale, zero}},
              {{zero, -projectorScale, half,
                (one + c) * projectorScale}},
              {{projectorScale, zero, projectorScale, half}},
          }};
          const Jet2 h = Interval(2.0) * alpha * beta;
          const std::array<std::array<Jet2, 2>, 4> algebraicFrame{{
              {{one, zero}},
              {{alpha, -beta}},
              {{c / Jet2(Interval(2.0)), h}},
              {{alpha, beta}},
          }};
          std::array<std::array<Jet2, 2>, 4> katoFrame{};
          for (int row = 0; row < 4; ++row) {
            for (int column = 0; column < 2; ++column) {
              katoFrame[static_cast<std::size_t>(row)]
                       [static_cast<std::size_t>(column)] = zero;
              for (int inner = 0; inner < 2; ++inner) {
                katoFrame[static_cast<std::size_t>(row)]
                         [static_cast<std::size_t>(column)] =
                    katoFrame[static_cast<std::size_t>(row)]
                             [static_cast<std::size_t>(column)] +
                    algebraicFrame[static_cast<std::size_t>(row)]
                                  [static_cast<std::size_t>(inner)] *
                    change[static_cast<std::size_t>(inner)]
                          [static_cast<std::size_t>(column)];
              }
            }
          }

          std::vector<Jet2> projectorEntries;
          std::vector<Jet2> rotationEntries;
          std::vector<Jet2> changeEntries;
          std::vector<Jet2> frameEntries;
          projectorEntries.reserve(16);
          rotationEntries.reserve(4);
          changeEntries.reserve(4);
          frameEntries.reserve(8);
          for (const auto& row : projector) {
            for (const Jet2& entry : row) projectorEntries.push_back(entry);
          }
          for (const auto& row : rotation) {
            for (const Jet2& entry : row) rotationEntries.push_back(entry);
          }
          for (const auto& row : change) {
            for (const Jet2& entry : row) changeEntries.push_back(entry);
          }
          for (const auto& row : katoFrame) {
            for (const Jet2& entry : row) frameEntries.push_back(entry);
          }

          adHessiansBitSymmetric = adHessiansBitSymmetric &&
              symmetricHessian(c) && symmetricHessian(alpha) &&
              symmetricHessian(beta) && symmetricHessian(y) &&
              symmetricHessian(chi) &&
              symmetricHessian(normalizerSquared) &&
              symmetricHessian(normalizer) && symmetricHessian(cosine) &&
              symmetricHessian(sigma) && symmetricHessian(determinant) &&
              symmetricHessian(inverseNorm);
          for (const Jet2& entry : projectorEntries) {
            adHessiansBitSymmetric =
                adHessiansBitSymmetric && symmetricHessian(entry);
          }
          for (const Jet2& entry : rotationEntries) {
            adHessiansBitSymmetric =
                adHessiansBitSymmetric && symmetricHessian(entry);
          }
          for (const Jet2& entry : changeEntries) {
            adHessiansBitSymmetric =
                adHessiansBitSymmetric && symmetricHessian(entry);
          }
          for (const Jet2& entry : frameEntries) {
            adHessiansBitSymmetric =
                adHessiansBitSymmetric && symmetricHessian(entry);
          }

          maximize(cBounds, jetBounds({c}));
          maximize(projectorBounds, jetBounds(projectorEntries));
          maximize(chiBounds, jetBounds({chi}));
          maximize(rotationBounds, jetBounds(rotationEntries));
          maximize(changeBounds, jetBounds(changeEntries));
          maximize(frameBounds, jetBounds(frameEntries));

          Interval gram00(0.0);
          Interval gram01(0.0);
          Interval gram11(0.0);
          for (int row = 0; row < 4; ++row) {
            const Interval& first =
                katoFrame[static_cast<std::size_t>(row)][0].value;
            const Interval& second =
                katoFrame[static_cast<std::size_t>(row)][1].value;
            gram00 += first * first;
            gram01 += first * second;
            gram11 += second * second;
          }
          const Interval discriminant = sqrt(
              sqr(gram00 - gram11) + Interval(4.0) * sqr(gram01));
          const Interval lambdaPlus =
              (gram00 + gram11 + discriminant) / Interval(2.0);
          const Interval lambdaMinusRaw =
              (gram00 + gram11 - discriminant) / Interval(2.0);
          if (lambdaPlus.rightBound() < 0.0 ||
              lambdaMinusRaw.rightBound() < 0.0) {
            gramEigenvalueEnclosuresNonempty = false;
          }
          const Interval lambdaPlusNonnegative(
              std::max(0.0, lambdaPlus.leftBound()),
              std::max(0.0, lambdaPlus.rightBound()));
          const Interval lambdaMinusNonnegative(
              std::max(0.0, lambdaMinusRaw.leftBound()),
              std::max(0.0, lambdaMinusRaw.rightBound()));
          const Interval frameOperator = sqrt(lambdaPlusNonnegative);
          const Interval frameSmallest = sqrt(lambdaMinusNonnegative);
          const Interval tau = Interval(0.25) *
              log((Interval(2.0) + c.value) / Interval(2.0));

          if (!initialized) {
            cHull = c.value;
            alphaHull = alpha.value;
            betaHull = beta.value;
            normalizerSquaredHull = normalizerSquared.value;
            yHull = y.value;
            chiHull = chi.value;
            cosineHull = cosine.value;
            sigmaHull = sigma.value;
            determinantHull = determinant.value;
            inverseHull = inverseNorm.value;
            tauHull = tau;
            frameOperatorHull = frameOperator;
            frameSmallestHull = frameSmallest;
            initialized = true;
          } else {
            cHull = hullIntervals(cHull, c.value);
            alphaHull = hullIntervals(alphaHull, alpha.value);
            betaHull = hullIntervals(betaHull, beta.value);
            normalizerSquaredHull = hullIntervals(
                normalizerSquaredHull, normalizerSquared.value);
            yHull = hullIntervals(yHull, y.value);
            chiHull = hullIntervals(chiHull, chi.value);
            cosineHull = hullIntervals(cosineHull, cosine.value);
            sigmaHull = hullIntervals(sigmaHull, sigma.value);
            determinantHull = hullIntervals(
                determinantHull, determinant.value);
            inverseHull = hullIntervals(inverseHull, inverseNorm.value);
            tauHull = hullIntervals(tauHull, tau);
            frameOperatorHull = hullIntervals(
                frameOperatorHull, frameOperator);
            frameSmallestHull = hullIntervals(
                frameSmallestHull, frameSmallest);
          }
        }
      }
    }

    const bool parameterGridNonempty = initialized;
    const bool completeFirstParameterMultiindices =
        kParameterDimension == 3;
    const bool completeFullOrderedSecondParameterIndices =
        kParameterDimension * kParameterDimension == 9;
    const bool secondParameterOffDiagonalsCountedTwice = true;
    bool importedP2bUpperRationalsPositive = true;
    for (int index = 0; index < kImportedJetCount; ++index) {
      importedP2bUpperRationalsPositive =
          importedP2bUpperRationalsPositive &&
          input(kImportedJetOffset + index).leftBound() > 0.0;
    }
    const bool importedP2bTriangleComplete =
        kImportedJetCount == 9;
    const bool sourceTriangleComplete = kTrueSourceGateCount == 9;
    const bool fullRectangularSourceNotClaimed = true;
    const bool allSqrtDomainsUniformlyPositive = initialized;

    bool structureValid = gridGapFree && bridgeMatchesNormalization &&
        subdivisionsMatchFrozenContract &&
        derivativeScalesMatchFrozenContract && allInputsStrictlyPositive &&
        parameterGridNonempty && adHessiansBitSymmetric &&
        completeFirstParameterMultiindices &&
        completeFullOrderedSecondParameterIndices &&
        secondParameterOffDiagonalsCountedTwice &&
        importedP2bUpperRationalsPositive && importedP2bTriangleComplete &&
        sourceTriangleComplete && fullRectangularSourceNotClaimed &&
        allSqrtDomainsUniformlyPositive &&
        gramEigenvalueEnclosuresNonempty;

    const Interval absoluteC = absoluteEnvelope(cHull);
    const Interval absoluteY = absoluteEnvelope(yHull);
    const Interval absoluteChi = absoluteEnvelope(chiHull);
    const Interval sourceB0 = radius;
    const Interval sourceB1 = radius * chiBounds.order1;
    const Interval sourceB2 = radius * sqrt(
        sqr(chiBounds.order2) + sqr(sqr(chiBounds.order1)));
    const Interval phaseSpeed = radius;

    std::array<Interval, kImportedJetCount> physicalF{};
    for (int index = 0; index < kImportedJetCount; ++index) {
      physicalF[static_cast<std::size_t>(index)] =
          input(kImportedJetOffset + index);
    }
    const auto f = [&](int stateOrder, int parameterOrder) -> const Interval& {
      if (stateOrder == 0) {
        return physicalF.at(static_cast<std::size_t>(parameterOrder));
      }
      if (stateOrder == 1) {
        return physicalF.at(static_cast<std::size_t>(3 + parameterOrder));
      }
      if (stateOrder == 2) {
        if (parameterOrder > 1) {
          throw std::logic_error("P2bK F_2 parameter order is unavailable");
        }
        return physicalF.at(static_cast<std::size_t>(6 + parameterOrder));
      }
      if (stateOrder == 3 && parameterOrder == 0) return physicalF.at(8);
      throw std::logic_error("P2bK physical source jet is unavailable");
    };
    const Interval g1 = f(1, 1) + f(2, 0) * sourceB1;
    const Interval g2 = f(1, 2) +
        Interval(2.0) * f(2, 1) * sourceB1 +
        f(3, 0) * sourceB1 * sourceB1 + f(2, 0) * sourceB2;
    std::array<Interval, kTrueSourceGateCount> sourceJets{};
    sourceJets[0] = f(0, 0);
    sourceJets[1] = f(0, 1) + f(1, 0) * sourceB1;
    sourceJets[2] = f(0, 2) +
        Interval(2.0) * f(1, 1) * sourceB1 +
        f(2, 0) * sourceB1 * sourceB1 + f(1, 0) * sourceB2;
    sourceJets[3] = f(1, 0) * radius;
    sourceJets[4] = g1 * radius + f(1, 0) * sourceB1;
    sourceJets[5] = g2 * radius + Interval(2.0) * g1 * sourceB1 +
                    f(1, 0) * sourceB2;
    sourceJets[6] = f(2, 0) * radius * radius + f(1, 0) * radius;
    sourceJets[7] =
        (f(2, 1) + f(3, 0) * sourceB1) * radius * radius +
        Interval(2.0) * f(2, 0) * sourceB1 * radius +
        g1 * radius + f(1, 0) * sourceB1;
    sourceJets[8] = f(3, 0) * radius * radius * radius +
        Interval(3.0) * f(2, 0) * radius * radius +
        f(1, 0) * radius;

    const Enclosures rieszMargins{
        {"absolute_c_upper_margin", acceptance(0) - absoluteC},
        {"alpha_lower_margin", alphaHull - acceptance(1)},
        {"beta_lower_margin", betaHull - acceptance(2)}};
    const Enclosures frameMargins{
        {"normalizer_squared_lower_margin",
         normalizerSquaredHull - acceptance(3)},
        {"absolute_y_upper_margin", acceptance(4) - absoluteY},
        {"phase_shift_absolute_upper_margin",
         acceptance(5) - absoluteChi},
        {"phase_rotation_cosine_lower_margin",
         cosineHull - acceptance(6)},
        {"radial_scale_lower_margin", sigmaHull - acceptance(7)},
        {"radial_scale_upper_margin", acceptance(8) - sigmaHull},
        {"frame_change_determinant_lower_margin",
         determinantHull - acceptance(9)},
        {"frame_change_inverse_upper_margin",
         acceptance(10) - inverseHull},
        {"physical_frame_smallest_singular_lower_margin",
         frameSmallestHull - acceptance(11)},
        {"physical_frame_operator_upper_margin",
         acceptance(12) - frameOperatorHull}};
    const Enclosures c2Margins{
        {"normalized_c_first_derivative_upper_margin",
         acceptance(13) - cBounds.order1},
        {"normalized_c_second_derivative_upper_margin",
         acceptance(14) - cBounds.order2},
        {"normalized_projector_first_derivative_upper_margin",
         acceptance(15) - projectorBounds.order1},
        {"normalized_projector_second_derivative_upper_margin",
         acceptance(16) - projectorBounds.order2},
        {"normalized_phase_first_derivative_upper_margin",
         acceptance(17) - chiBounds.order1},
        {"normalized_phase_second_derivative_upper_margin",
         acceptance(18) - chiBounds.order2},
        {"normalized_rotation_first_derivative_upper_margin",
         acceptance(19) - rotationBounds.order1},
        {"normalized_rotation_second_derivative_upper_margin",
         acceptance(20) - rotationBounds.order2},
        {"normalized_change_first_derivative_upper_margin",
         acceptance(21) - changeBounds.order1},
        {"normalized_change_second_derivative_upper_margin",
         acceptance(22) - changeBounds.order2},
        {"normalized_frame_first_derivative_upper_margin",
         acceptance(23) - frameBounds.order1},
        {"normalized_frame_second_derivative_upper_margin",
         acceptance(24) - frameBounds.order2}};
    Enclosures sourceMargins{
        {"normalized_source_coordinate_first_derivative_upper_margin",
         acceptance(25) - sourceB1},
        {"normalized_source_coordinate_second_derivative_upper_margin",
         acceptance(26) - sourceB2},
        {"source_coordinate_phase_speed_lower_margin",
         phaseSpeed - acceptance(27)}};
    for (int index = 0; index < kTrueSourceGateCount; ++index) {
      sourceMargins.push_back({
          std::string(kTrueSourceNames[static_cast<std::size_t>(index)]) +
              "_upper_margin",
          sourceGate(index) - sourceJets[static_cast<std::size_t>(index)]});
    }

    const Verdict structuralStatus =
        structureValid ? Verdict::Pass : Verdict::Fail;
    const Verdict rieszStatus = combine(
        structuralStatus, sufficientMargins(rieszMargins));
    const Verdict frameStatus = combine(
        structuralStatus,
        combine(rieszStatus, sufficientMargins(frameMargins)));
    const Verdict c2Status = combine(
        structuralStatus,
        combine(rieszStatus,
                combine(frameStatus, sufficientMargins(c2Margins))));
    const Verdict sourceStatus = combine(
        structuralStatus,
        combine(frameStatus,
                combine(c2Status, sufficientMargins(sourceMargins))));
    Verdict mathematicalStatus = Verdict::Pass;
    for (const Verdict status :
         std::array<Verdict, 4>{rieszStatus, frameStatus, c2Status,
                                sourceStatus}) {
      mathematicalStatus = combine(mathematicalStatus, status);
    }
    const Verdict probeStatus = combine(rounding.status, mathematicalStatus);

    const Enclosures parameterEnclosures{
        {"r", bridgeR}, {"a2", bridgeA2}, {"epsilon", bridgeEpsilon},
        {"R", radius},
        {"original_first_derivative_scale", firstDerivativeScale},
        {"original_second_derivative_scale", secondDerivativeScale}};
    Enclosures acceptanceGates;
    for (int index = 0; index < kAcceptanceGateCount; ++index) {
      acceptanceGates.push_back({
          kAcceptanceNames[static_cast<std::size_t>(index)],
          acceptance(index)});
    }
    Enclosures trueSourceGates;
    Enclosures importedPhysicalJets;
    Enclosures normalizedSourceJets;
    Enclosures originalSourceJets;
    for (int index = 0; index < kTrueSourceGateCount; ++index) {
      trueSourceGates.push_back({
          kTrueSourceNames[static_cast<std::size_t>(index)],
          sourceGate(index)});
      importedPhysicalJets.push_back({
          kImportedJetNames[static_cast<std::size_t>(index)],
          physicalF[static_cast<std::size_t>(index)]});
      normalizedSourceJets.push_back({
          kTrueSourceNames[static_cast<std::size_t>(index)],
          sourceJets[static_cast<std::size_t>(index)]});
      const int parameterOrder =
          index <= 2 ? index :
          (index <= 5 ? index - 3 : (index <= 7 ? index - 6 : 0));
      const Interval scale = parameterOrder == 0 ? Interval(1.0) :
          (parameterOrder == 1 ? firstDerivativeScale :
                                 secondDerivativeScale);
      originalSourceJets.push_back({
          kTrueSourceNames[static_cast<std::size_t>(index)],
          scale * sourceJets[static_cast<std::size_t>(index)]});
    }
    const Enclosures scalarEnclosures{
        {"c", cHull}, {"absolute_c", absoluteC},
        {"alpha", alphaHull}, {"beta", betaHull},
        {"N_squared", normalizerSquaredHull},
        {"y", yHull}, {"chi", chiHull}, {"cos_chi", cosineHull},
        {"sigma", sigmaHull}, {"det_C_AK", determinantHull},
        {"inverse_C_AK_operator", inverseHull}, {"tau", tauHull},
        {"physical_K_operator", frameOperatorHull},
        {"physical_K_smallest_singular", frameSmallestHull}};
    const Enclosures normalizedParameterJets{
        {"c_D1", cBounds.order1}, {"c_D2", cBounds.order2},
        {"P_u_D1", projectorBounds.order1},
        {"P_u_D2", projectorBounds.order2},
        {"chi_D1", chiBounds.order1}, {"chi_D2", chiBounds.order2},
        {"R_chi_D1", rotationBounds.order1},
        {"R_chi_D2", rotationBounds.order2},
        {"C_AK_D1", changeBounds.order1},
        {"C_AK_D2", changeBounds.order2},
        {"K_D1", frameBounds.order1}, {"K_D2", frameBounds.order2}};
    Enclosures originalParameterJets;
    for (const auto& item : normalizedParameterJets) {
      const bool secondOrder =
          item.first.size() >= 3 &&
          item.first.compare(item.first.size() - 3, 3, "_D2") == 0;
      originalParameterJets.push_back({
          item.first, (secondOrder ? secondDerivativeScale :
                                     firstDerivativeScale) * item.second});
    }
    const Enclosures sourceCoordinateJets{
        {"B_0", sourceB0}, {"B_1", sourceB1}, {"B_2", sourceB2},
        {"phase_speed", phaseSpeed}};
    const Enclosures originalSourceCoordinateJets{
        {"B_0", sourceB0},
        {"B_1", firstDerivativeScale * sourceB1},
        {"B_2", secondDerivativeScale * sourceB2},
        {"phase_speed", phaseSpeed}};

    const std::array<Obligation, 4> obligations{
        Obligation{
            "P2.KATO.RIESZ_TRANSPORT", rieszStatus,
            "The outward-rounded interval layer bounds the spectral-gap "
            "domain and expanding-projector parameter family; the exact "
            "Riesz and Kato identities are required from the separately "
            "replayed exact audit",
            rieszMargins},
        Obligation{
            "P2.KATO.FRAME_CHANGE", frameStatus,
            "Conditional on the exact frame identities, the conformal "
            "algebraic-to-Kato change is positive and uniformly invertible "
            "and the physical oriented frame has direct singular-value bounds",
            frameMargins},
        Obligation{
            "P2.KATO.C2_LIFT", c2Status,
            "Complete normalized first and full ordered second parameter "
            "automatic derivatives of c, P_u, chi, R_chi, C_AK, and K lie "
            "inside every frozen Hilbert--Schmidt gate",
            c2Margins},
        Obligation{
            "P2.KATO.SOURCE_PARAMETERIZATION", sourceStatus,
            "The degree-positive radius-R source-coordinate circle has the "
            "frozen C2 bounds and its total-order-three true-source triangle, "
            "computed from the exact-rational imported P2b upper bounds, lies "
            "inside every frozen gate",
            sourceMargins}};

    std::cout
        << "{\"schema_version\":\"rfsn-vdp-p2-kato-probe/1\","
        << "\"status\":\"" << verdictName(probeStatus) << "\","
        << "\"mathematical_status\":\""
        << verdictName(mathematicalStatus) << "\","
        << "\"structure_status\":\"" << verdictName(structuralStatus)
        << "\",\"structure_checks\":{"
        << "\"gap_free_exact_rational_grid\":"
        << (gridGapFree ? "true" : "false") << ','
        << "\"bridge_matches_parameter_normalization\":"
        << (bridgeMatchesNormalization ? "true" : "false") << ','
        << "\"subdivisions_match_frozen_contract\":"
        << (subdivisionsMatchFrozenContract ? "true" : "false") << ','
        << "\"original_parameter_scales_match_frozen_contract\":"
        << (derivativeScalesMatchFrozenContract ? "true" : "false") << ','
        << "\"all_rational_inputs_strictly_positive\":"
        << (allInputsStrictlyPositive ? "true" : "false") << ','
        << "\"parameter_grid_nonempty\":"
        << (parameterGridNonempty ? "true" : "false") << ','
        << "\"parameter_ad_hessians_bit_symmetric\":"
        << (adHessiansBitSymmetric ? "true" : "false") << ','
        << "\"complete_first_parameter_multiindices\":"
        << (completeFirstParameterMultiindices ? "true" : "false") << ','
        << "\"complete_full_ordered_second_parameter_indices\":"
        << (completeFullOrderedSecondParameterIndices ? "true" : "false")
        << ','
        << "\"second_parameter_off_diagonals_counted_twice\":"
        << (secondParameterOffDiagonalsCountedTwice ? "true" : "false")
        << ','
        << "\"imported_p2b_upper_rationals_positive\":"
        << (importedP2bUpperRationalsPositive ? "true" : "false") << ','
        << "\"imported_p2b_triangle_complete\":"
        << (importedP2bTriangleComplete ? "true" : "false") << ','
        << "\"source_triangle_complete\":"
        << (sourceTriangleComplete ? "true" : "false") << ','
        << "\"full_rectangular_source_not_claimed\":"
        << (fullRectangularSourceNotClaimed ? "true" : "false") << ','
        << "\"all_sqrt_domains_uniformly_positive\":"
        << (allSqrtDomainsUniformlyPositive ? "true" : "false") << ','
        << "\"physical_frame_gram_eigenvalue_enclosures_nonempty\":"
        << (gramEigenvalueEnclosuresNonempty ? "true" : "false")
        << "},\"rounding_self_test\":"
        << rfsn::rigorous::roundingReportJson(rounding)
        << ",\"grid\":{\"ordered_axes\":[\"theta_r\",\"theta_a\","
        << "\"theta_epsilon\"],\"subdivisions\":["
        << subdivisions[0] << ',' << subdivisions[1] << ','
        << subdivisions[2] << "],\"cell_count\":"
        << static_cast<long long>(subdivisions[0]) * subdivisions[1] *
               subdivisions[2]
        << ",\"normalized_parameter_dimension\":3}"
        << ",\"parameter_enclosures\":"
        << enclosureObjectJson(parameterEnclosures)
        << ",\"acceptance_gates\":"
        << enclosureObjectJson(acceptanceGates)
        << ",\"normalized_true_source_jet_upper_gates\":"
        << enclosureObjectJson(trueSourceGates)
        << ",\"imported_p2b_physical_jet_enclosures\":"
        << enclosureObjectJson(importedPhysicalJets)
        << ",\"scalar_enclosures\":"
        << enclosureObjectJson(scalarEnclosures)
        << ",\"normalized_parameter_jet_enclosures\":"
        << enclosureObjectJson(normalizedParameterJets)
        << ",\"original_parameter_jet_enclosures\":"
        << enclosureObjectJson(originalParameterJets)
        << ",\"source_coordinate_jet_enclosures\":"
        << enclosureObjectJson(sourceCoordinateJets)
        << ",\"original_parameter_source_coordinate_jet_enclosures\":"
        << enclosureObjectJson(originalSourceCoordinateJets)
        << ",\"normalized_true_source_jet_enclosures\":"
        << enclosureObjectJson(normalizedSourceJets)
        << ",\"original_parameter_true_source_jet_enclosures\":"
        << enclosureObjectJson(originalSourceJets)
        << ",\"riesz_transport_gate_margins\":"
        << enclosureObjectJson(rieszMargins)
        << ",\"frame_change_gate_margins\":"
        << enclosureObjectJson(frameMargins)
        << ",\"c2_lift_gate_margins\":"
        << enclosureObjectJson(c2Margins)
        << ",\"source_parameterization_gate_margins\":"
        << enclosureObjectJson(sourceMargins)
        << ",\"norm_contract\":{"
        << "\"matrix_value_norm\":\"spectral-2-norm\","
        << "\"matrix_inverse_norm\":\"spectral-2-norm\","
        << "\"scalar_first_parameter_norm\":\"euclidean-on-R3\","
        << "\"scalar_second_parameter_norm\":\"full-3x3-frobenius\","
        << "\"matrix_first_parameter_norm\":"
        << "\"output-parameter-hilbert-schmidt\","
        << "\"matrix_second_parameter_norm\":"
        << "\"output-full-ordered-parameter-hilbert-schmidt\","
        << "\"true_source_jet_norm\":"
        << "\"physical-output-labelled-multilinear-hilbert-schmidt\"}"
        << ",\"source_composition\":{"
        << "\"maximum_total_order\":3,\"maximum_phase_order\":3,"
        << "\"maximum_parameter_order\":2,\"targets\":["
        << "\"S_0_0\",\"S_0_1\",\"S_0_2\",\"S_1_0\","
        << "\"S_1_1\",\"S_1_2\",\"S_2_0\",\"S_2_1\","
        << "\"S_3_0\"],\"full_rectangular_claimed\":false,"
        << "\"complete_frozen_recurrence\":true}"
        << ",\"external_exact_audit_contract\":{"
        << "\"required\":true,\"included_in_raw_status\":false,"
        << "\"schema_version\":\"rfsn-vdp-p2-kato-exact-audit/1\"}"
        << ",\"obligations\":[";
    for (std::size_t index = 0; index < obligations.size(); ++index) {
      if (index > 0) std::cout << ',';
      std::cout << obligationJson(obligations[index]);
    }
    std::cout << "]}\n";

    if (probeStatus == Verdict::Pass) return 0;
    return probeStatus == Verdict::Fail ? 1 : 2;
  } catch (const std::exception& error) {
    std::cout
        << "{\"schema_version\":\"rfsn-vdp-p2-kato-probe/1\","
        << "\"status\":\"FAIL\",\"mathematical_status\":\"FAIL\","
        << "\"structure_status\":\"FAIL\",\"error\":\""
        << rfsn::rigorous::jsonEscape(error.what()) << "\"}\n";
    return 1;
  }
}
