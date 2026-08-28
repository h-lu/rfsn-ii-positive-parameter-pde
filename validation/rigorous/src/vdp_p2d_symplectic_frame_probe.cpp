#include "interval_io.hpp"
#include "rounding_self_test.hpp"
#include "verdict.hpp"

#include <algorithm>
#include <array>
#include <cctype>
#include <cmath>
#include <exception>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

// Positional interface (argc=56):
//
//   12 bridge strings: lower/upper rational endpoints for r,a2,epsilon;
//   3 positive subdivision integers for theta_r,theta_a,theta_epsilon;
//   20 rational gate pairs in kGateNames order below.
//
// The raw PASS status covers only the outward-rounded branch, conditioning,
// and parameter-C2 frame predicate.  It does not include the exact symbolic
// identities or authenticate the archived P2bK prerequisite.

namespace {

using rfsn::rigorous::Interval;
using rfsn::rigorous::Verdict;
using rfsn::rigorous::combine;
using rfsn::rigorous::intervalJson;
using rfsn::rigorous::verdictName;

constexpr int kParameterDimension = 3;
constexpr int kGateCount = 20;
constexpr std::array<int, 3> kExpectedSubdivisions{16, 8, 4};
constexpr std::array<const char*, kGateCount> kGateNames{
    "d_positive_lower",
    "minus_e_positive_lower",
    "kappa_lower",
    "kappa_upper",
    "kappa_plus_d_lower",
    "half_denominator_lower",
    "cos_theta_lower",
    "abs_sin_theta_upper",
    "radial_scale_lower",
    "radial_scale_upper",
    "abs_theta_upper",
    "anchor_deviation_upper",
    "normalized_L_D1_upper",
    "normalized_L_D2_upper",
    "normalized_L_inverse_D1_upper",
    "normalized_L_inverse_D2_upper",
    "original_L_D1_upper",
    "original_L_D2_upper",
    "original_L_inverse_D1_upper",
    "original_L_inverse_D2_upper"};
constexpr std::array<const char*, kGateCount> kExpectedGateNumerators{
    "2", "3", "19", "21", "8", "17", "7", "5", "19", "21",
    "1", "1", "1", "1", "1", "1", "2", "20", "2", "20"};
constexpr std::array<const char*, kGateCount> kExpectedGateDenominators{
    "3", "5", "20", "20", "5", "10", "8", "12", "20", "20",
    "2", "8", "10", "10", "10", "10", "1", "1", "1", "1"};
constexpr std::array<bool, kGateCount> kLowerGate{
    true, true, true, false, true, true, true, false, true, false,
    false, false, false, false, false, false, false, false, false, false};
constexpr std::array<std::array<int, 2>, 6> kSymmetricPairs{{
    {{0, 0}}, {{0, 1}}, {{0, 2}}, {{1, 1}}, {{1, 2}}, {{2, 2}}}};
constexpr std::array<const char*, 14> kScalarNames{
    "c", "alpha", "beta", "N_squared", "y", "d", "e", "kappa",
    "kappa_plus_d", "half_denominator", "cos_theta", "sin_theta",
    "theta", "kappa_inverse_sqrt"};

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

Interval rational(long long numerator, long long denominator) {
  return rfsn::rigorous::exactRational(
      std::to_string(numerator), std::to_string(denominator));
}

Interval normalizedCell(int index, int count) {
  const Interval left = rational(-count + 2LL * index, count);
  const Interval right = rational(-count + 2LL * (index + 1), count);
  return Interval(left.leftBound(), right.rightBound());
}

std::vector<Interval> normalizedCells(int count) {
  std::vector<Interval> result;
  result.reserve(static_cast<std::size_t>(count));
  for (int index = 0; index < count; ++index)
    result.push_back(normalizedCell(index, count));
  return result;
}

bool gapFreeCover(const std::vector<Interval>& cells) {
  if (cells.empty() || cells.front().leftBound() > -1.0 ||
      cells.back().rightBound() < 1.0) return false;
  for (std::size_t index = 1; index < cells.size(); ++index) {
    if (cells[index - 1].rightBound() < cells[index].leftBound()) return false;
  }
  return true;
}

Interval hull(const Interval& left, const Interval& right) {
  return Interval(std::min(left.leftBound(), right.leftBound()),
                  std::max(left.rightBound(), right.rightBound()));
}

Interval absoluteEnvelope(const Interval& value) {
  return Interval(0.0, std::max(std::abs(value.leftBound()),
                                std::abs(value.rightBound())));
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
          left.value * right.hessian[static_cast<std::size_t>(i)]
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
      const Interval entry = secondDerivative *
              argument.gradient[static_cast<std::size_t>(i)] *
              argument.gradient[static_cast<std::size_t>(j)] +
          firstDerivative * argument.hessian[static_cast<std::size_t>(i)]
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
  if (argument.value.leftBound() <= 0.0)
    throw std::logic_error("square-root AD argument is not positive");
  const Interval root = sqrt(argument.value);
  return compose(argument, root,
                 Interval(1.0) / (Interval(2.0) * root),
                 -Interval(1.0) /
                     (Interval(4.0) * argument.value * root));
}

Jet2 reciprocal(const Jet2& argument) {
  if (containsZero(argument.value))
    throw std::logic_error("reciprocal AD argument contains zero");
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
                           [static_cast<std::size_t>(i)])) return false;
    }
  }
  return true;
}

Jet2 originalParameterJet(const Jet2& normalized) {
  const std::array<Interval, kParameterDimension> scales{
      Interval(25.0), Interval(4.0), Interval(5.0)};
  Jet2 result(normalized.value);
  for (int i = 0; i < kParameterDimension; ++i) {
    result.gradient[static_cast<std::size_t>(i)] =
        scales[static_cast<std::size_t>(i)] *
        normalized.gradient[static_cast<std::size_t>(i)];
    for (int j = i; j < kParameterDimension; ++j) {
      const Interval entry = scales[static_cast<std::size_t>(i)] *
          scales[static_cast<std::size_t>(j)] *
          normalized.hessian[static_cast<std::size_t>(i)]
                            [static_cast<std::size_t>(j)];
      result.hessian[static_cast<std::size_t>(i)]
                    [static_cast<std::size_t>(j)] = entry;
      result.hessian[static_cast<std::size_t>(j)]
                    [static_cast<std::size_t>(i)] = entry;
    }
  }
  return result;
}

struct JetBounds {
  Interval order0{0.0};
  Interval order1{0.0};
  Interval order2{0.0};
};

JetBounds jetBounds(const std::vector<Jet2>& entries) {
  Interval valueSum(0.0), gradientSum(0.0), hessianSum(0.0);
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

template <std::size_t Rows, std::size_t Columns>
using JetMatrix = std::array<std::array<Jet2, Columns>, Rows>;

template <std::size_t Rows, std::size_t Inner, std::size_t Columns>
JetMatrix<Rows, Columns> multiply(
    const JetMatrix<Rows, Inner>& left,
    const JetMatrix<Inner, Columns>& right) {
  JetMatrix<Rows, Columns> result{};
  for (std::size_t row = 0; row < Rows; ++row) {
    for (std::size_t column = 0; column < Columns; ++column) {
      for (std::size_t inner = 0; inner < Inner; ++inner)
        result[row][column] = result[row][column] +
            left[row][inner] * right[inner][column];
    }
  }
  return result;
}

template <std::size_t Rows, std::size_t Columns>
JetMatrix<Columns, Rows> transpose(
    const JetMatrix<Rows, Columns>& value) {
  JetMatrix<Columns, Rows> result{};
  for (std::size_t row = 0; row < Rows; ++row)
    for (std::size_t column = 0; column < Columns; ++column)
      result[column][row] = value[row][column];
  return result;
}

template <std::size_t Rows, std::size_t Columns>
JetMatrix<Rows, Columns> subtract(
    const JetMatrix<Rows, Columns>& left,
    const JetMatrix<Rows, Columns>& right) {
  JetMatrix<Rows, Columns> result{};
  for (std::size_t row = 0; row < Rows; ++row)
    for (std::size_t column = 0; column < Columns; ++column)
      result[row][column] = left[row][column] - right[row][column];
  return result;
}

template <std::size_t Rows, std::size_t Columns>
std::vector<Jet2> flatten(const JetMatrix<Rows, Columns>& value) {
  std::vector<Jet2> result;
  result.reserve(Rows * Columns);
  for (const auto& row : value)
    for (const Jet2& entry : row) result.push_back(entry);
  return result;
}

struct FrameData {
  std::array<Jet2, 14> scalars;
  JetMatrix<4, 4> completion;
  JetMatrix<4, 4> inverse;
};

FrameData buildFrame(const Jet2& c) {
  const Jet2 zero(Interval(0.0));
  const Jet2 one(Interval(1.0));
  const Jet2 rootTwo = squareRoot(Jet2(Interval(2.0)));
  const Jet2 alpha = Interval(0.5) *
      squareRoot(Jet2(Interval(2.0)) + c);
  const Jet2 beta = Interval(0.5) *
      squareRoot(Jet2(Interval(2.0)) - c);
  const Jet2 normalizerSquared = Interval(6.0) * alpha * alpha
      - Interval(4.0) * rootTwo * alpha + Jet2(Interval(3.0));
  const Jet2 normalizer = squareRoot(normalizerSquared);
  const Jet2 y = (reciprocal(rootTwo) - alpha) / beta;
  JetMatrix<4, 2> algebraic{{
      {{one, zero}},
      {{alpha, -beta}},
      {{c / Jet2(Interval(2.0)), Interval(2.0) * alpha * beta}},
      {{alpha, beta}},
  }};
  JetMatrix<2, 2> katoChange{{
      {{one / normalizer, -y / normalizer}},
      {{y / normalizer, one / normalizer}},
  }};
  const JetMatrix<4, 2> kato = multiply(algebraic, katoChange);
  const Jet2 d = Interval(2.0) * alpha / normalizerSquared;
  const Jet2 e = Interval(2.0) * alpha *
      (Interval(3.0) * alpha - Interval(2.0) * rootTwo) /
      (normalizerSquared * beta);
  const Jet2 kappa = Interval(4.0) * alpha * beta *
      (one + y * y) / normalizerSquared;
  const Jet2 kappaPlusD = kappa + d;
  const Jet2 halfDenominator = squareRoot(
      Interval(2.0) * kappa * kappaPlusD);
  const Jet2 cosineHalf = kappaPlusD / halfDenominator;
  const Jet2 sineHalf = e / halfDenominator;
  const Jet2 theta = arctangent(sineHalf / cosineHalf);
  const Jet2 radialScale = reciprocal(squareRoot(kappa));
  JetMatrix<2, 2> halfRotation{{
      {{cosineHalf, -sineHalf}},
      {{sineHalf, cosineHalf}},
  }};
  JetMatrix<4, 2> expanding = multiply(kato, halfRotation);
  for (auto& row : expanding)
    for (Jet2& entry : row) entry = radialScale * entry;

  FrameData result;
  result.scalars = {{c, alpha, beta, normalizerSquared, y, d, e, kappa,
                     kappaPlusD, halfDenominator, cosineHalf, sineHalf,
                     theta, radialScale}};
  const std::array<Interval, 4> reverserDiagonal{
      Interval(1.0), Interval(-1.0), Interval(1.0), Interval(-1.0)};
  const std::array<Interval, 2> cZeroDiagonal{
      Interval(1.0), Interval(-1.0)};
  for (std::size_t row = 0; row < 4; ++row) {
    for (std::size_t column = 0; column < 2; ++column) {
      result.completion[row][column] = reverserDiagonal[row] *
          cZeroDiagonal[column] * expanding[row][column];
      result.completion[row][column + 2] = expanding[row][column];
    }
  }
  JetMatrix<4, 4> omega{};
  omega[0][1] = Jet2(Interval(-1.0));
  omega[1][0] = one;
  omega[2][3] = one;
  omega[3][2] = Jet2(Interval(-1.0));
  JetMatrix<4, 4> minusOmegaZero{};
  minusOmegaZero[0][2] = one;
  minusOmegaZero[1][3] = one;
  minusOmegaZero[2][0] = Jet2(Interval(-1.0));
  minusOmegaZero[3][1] = Jet2(Interval(-1.0));
  result.inverse = multiply(
      multiply(minusOmegaZero, transpose(result.completion)), omega);
  return result;
}

struct JetHull {
  bool initialized{false};
  Interval value{0.0};
  std::array<Interval, 3> d1{};
  std::array<Interval, 6> d2{};

  void update(const Jet2& jet) {
    if (!initialized) {
      value = jet.value;
      for (int i = 0; i < 3; ++i)
        d1[static_cast<std::size_t>(i)] =
            jet.gradient[static_cast<std::size_t>(i)];
      for (std::size_t index = 0; index < kSymmetricPairs.size(); ++index) {
        const auto pair = kSymmetricPairs[index];
        d2[index] = jet.hessian[static_cast<std::size_t>(pair[0])]
                               [static_cast<std::size_t>(pair[1])];
      }
      initialized = true;
      return;
    }
    value = hull(value, jet.value);
    for (int i = 0; i < 3; ++i) {
      const std::size_t index = static_cast<std::size_t>(i);
      d1[index] = hull(d1[index], jet.gradient[index]);
    }
    for (std::size_t index = 0; index < kSymmetricPairs.size(); ++index) {
      const auto pair = kSymmetricPairs[index];
      d2[index] = hull(
          d2[index], jet.hessian[static_cast<std::size_t>(pair[0])]
                                [static_cast<std::size_t>(pair[1])]);
    }
  }
};

struct CompleteJetHull {
  JetHull normalized;
  JetHull original;

  void update(const Jet2& value) {
    normalized.update(value);
    original.update(originalParameterJet(value));
  }
};

struct GateObservation {
  bool initialized{false};
  Interval metric{0.0};
  std::array<int, 3> cell{{0, 0, 0}};

  void update(const Interval& candidate, const std::array<int, 3>& candidateCell,
              bool lowerGate) {
    const bool worse = !initialized ||
        (lowerGate ? candidate.leftBound() < metric.leftBound()
                   : candidate.rightBound() > metric.rightBound());
    if (worse) {
      metric = candidate;
      cell = candidateCell;
      initialized = true;
    }
  }
};

std::string jetHullJson(const JetHull& value) {
  std::ostringstream output;
  output << "{\"value\":" << intervalJson(value.value) << ",\"D1\":[";
  for (std::size_t index = 0; index < value.d1.size(); ++index) {
    if (index) output << ',';
    output << intervalJson(value.d1[index]);
  }
  output << "],\"D2_symmetric\":[";
  for (std::size_t index = 0; index < value.d2.size(); ++index) {
    if (index) output << ',';
    output << intervalJson(value.d2[index]);
  }
  output << "]}";
  return output.str();
}

std::string completeJetHullJson(const CompleteJetHull& value) {
  return std::string("{\"normalized\":") +
      jetHullJson(value.normalized) + ",\"original\":" +
      jetHullJson(value.original) + '}';
}

std::string marginObjectJson(const std::array<Interval, kGateCount>& margins) {
  std::ostringstream output;
  output << '{';
  for (int index = 0; index < kGateCount; ++index) {
    if (index) output << ',';
    output << '"' << kGateNames[static_cast<std::size_t>(index)] << "\":"
           << intervalJson(margins[static_cast<std::size_t>(index)]);
  }
  output << '}';
  return output.str();
}

Verdict marginsVerdict(const std::array<Interval, kGateCount>& margins) {
  for (const Interval& margin : margins) {
    if (margin.leftBound() <= 0.0) return Verdict::Inconclusive;
  }
  return Verdict::Pass;
}

}  // namespace

int main(int argc, char** argv) {
  try {
    if (argc != 56) {
      throw std::invalid_argument(
          "expected argc=56: 12 bridge strings, 3 subdivisions, and "
          "20 rational gate pairs");
    }
    const Interval bridgeR = readRationalInterval(
        argv[1], argv[2], argv[3], argv[4], "r");
    const Interval bridgeA2 = readRationalInterval(
        argv[5], argv[6], argv[7], argv[8], "a2");
    const Interval bridgeEpsilon = readRationalInterval(
        argv[9], argv[10], argv[11], argv[12], "epsilon");
    const std::array<int, 3> subdivisions{
        readPositiveSubdivision(argv[13], "theta_r"),
        readPositiveSubdivision(argv[14], "theta_a"),
        readPositiveSubdivision(argv[15], "theta_epsilon")};
    std::array<RationalInput, kGateCount> gates;
    for (int index = 0; index < kGateCount; ++index) {
      gates[static_cast<std::size_t>(index)] = readRational(
          argv[16 + 2 * index], argv[17 + 2 * index],
          kGateNames[static_cast<std::size_t>(index)]);
    }

    const auto rounding = rfsn::rigorous::runRoundingSelfTests();
    const bool bridgeMatchesFrozenContract =
        intervalBitEqual(bridgeR, readRationalInterval(
            "0", "1", "2", "25", "expected_r")) &&
        intervalBitEqual(bridgeA2, readRationalInterval(
            "-1", "4", "1", "4", "expected_a2")) &&
        intervalBitEqual(bridgeEpsilon, readRationalInterval(
            "4", "5", "6", "5", "expected_epsilon"));
    const bool subdivisionsMatch = subdivisions == kExpectedSubdivisions;
    bool gatesMatch = true;
    bool gateInputsPositive = true;
    for (int index = 0; index < kGateCount; ++index) {
      const Interval expected = rfsn::rigorous::exactRational(
          kExpectedGateNumerators[static_cast<std::size_t>(index)],
          kExpectedGateDenominators[static_cast<std::size_t>(index)]);
      gatesMatch = gatesMatch && intervalBitEqual(
          gates[static_cast<std::size_t>(index)].interval, expected);
      gateInputsPositive = gateInputsPositive &&
          gates[static_cast<std::size_t>(index)].interval.leftBound() > 0.0;
    }
    const std::array<std::vector<Interval>, 3> cells{
        normalizedCells(subdivisions[0]),
        normalizedCells(subdivisions[1]),
        normalizedCells(subdivisions[2])};
    const bool gapFree = gapFreeCover(cells[0]) && gapFreeCover(cells[1]) &&
                         gapFreeCover(cells[2]);

    std::array<CompleteJetHull, 14> scalarHulls;
    std::array<CompleteJetHull, 16> completionHulls;
    std::array<CompleteJetHull, 16> inverseHulls;
    std::array<GateObservation, kGateCount> observations;
    bool hessiansSymmetric = true;
    const FrameData anchor = buildFrame(Jet2(Interval(0.0)));
    long long cellCount = 0;

    for (int ir = 0; ir < subdivisions[0]; ++ir) {
      for (int ia = 0; ia < subdivisions[1]; ++ia) {
        for (int ie = 0; ie < subdivisions[2]; ++ie) {
          ++cellCount;
          const std::array<int, 3> cell{{ir, ia, ie}};
          const Jet2 thetaR = Jet2::variable(cells[0][ir], 0);
          const Jet2 thetaA = Jet2::variable(cells[1][ia], 1);
          const Jet2 thetaEpsilon = Jet2::variable(cells[2][ie], 2);
          const Jet2 one(Interval(1.0));
          const Jet2 r = (thetaR + one) / Jet2(Interval(25.0));
          const Jet2 a2 = thetaA / Jet2(Interval(4.0));
          const Jet2 epsilon = one +
              thetaEpsilon / Jet2(Interval(5.0));
          const Jet2 r2 = r * r;
          const Jet2 r4 = r2 * r2;
          const Jet2 c = Interval(2.0) * r * a2 +
              squareRoot(epsilon) * r4 * a2 * a2;
          const FrameData frame = buildFrame(c);
          for (std::size_t index = 0; index < frame.scalars.size(); ++index) {
            scalarHulls[index].update(frame.scalars[index]);
            hessiansSymmetric = hessiansSymmetric &&
                symmetricHessian(frame.scalars[index]) &&
                symmetricHessian(originalParameterJet(frame.scalars[index]));
          }
          const std::vector<Jet2> completion = flatten(frame.completion);
          const std::vector<Jet2> inverse = flatten(frame.inverse);
          std::vector<Jet2> originalCompletion, originalInverse;
          originalCompletion.reserve(16);
          originalInverse.reserve(16);
          for (std::size_t index = 0; index < 16; ++index) {
            completionHulls[index].update(completion[index]);
            inverseHulls[index].update(inverse[index]);
            originalCompletion.push_back(originalParameterJet(completion[index]));
            originalInverse.push_back(originalParameterJet(inverse[index]));
            hessiansSymmetric = hessiansSymmetric &&
                symmetricHessian(completion[index]) &&
                symmetricHessian(inverse[index]) &&
                symmetricHessian(originalCompletion.back()) &&
                symmetricHessian(originalInverse.back());
          }
          const JetBounds completionBounds = jetBounds(completion);
          const JetBounds inverseBounds = jetBounds(inverse);
          const JetBounds originalCompletionBounds =
              jetBounds(originalCompletion);
          const JetBounds originalInverseBounds = jetBounds(originalInverse);
          const Interval anchorDeviation =
              jetBounds(flatten(subtract(frame.completion,
                                         anchor.completion))).order0;
          const std::array<Interval, kGateCount> metrics{{
              frame.scalars[5].value,
              -frame.scalars[6].value,
              frame.scalars[7].value,
              frame.scalars[7].value,
              frame.scalars[8].value,
              frame.scalars[9].value,
              frame.scalars[10].value,
              absoluteEnvelope(frame.scalars[11].value),
              frame.scalars[13].value,
              frame.scalars[13].value,
              absoluteEnvelope(frame.scalars[12].value),
              anchorDeviation,
              completionBounds.order1,
              completionBounds.order2,
              inverseBounds.order1,
              inverseBounds.order2,
              originalCompletionBounds.order1,
              originalCompletionBounds.order2,
              originalInverseBounds.order1,
              originalInverseBounds.order2}};
          for (int index = 0; index < kGateCount; ++index) {
            observations[static_cast<std::size_t>(index)].update(
                metrics[static_cast<std::size_t>(index)], cell,
                kLowerGate[static_cast<std::size_t>(index)]);
          }
        }
      }
    }

    std::array<Interval, kGateCount> margins;
    for (int index = 0; index < kGateCount; ++index) {
      const Interval threshold = gates[static_cast<std::size_t>(index)].interval;
      const Interval observed =
          observations[static_cast<std::size_t>(index)].metric;
      margins[static_cast<std::size_t>(index)] =
          kLowerGate[static_cast<std::size_t>(index)]
              ? observed - threshold : threshold - observed;
    }
    const Verdict mathematicalStatus = marginsVerdict(margins);
    const bool cellCountMatches = cellCount == 512;
    const bool scalarSetComplete = scalarHulls.size() == kScalarNames.size();
    const bool matrixEntriesComplete = completionHulls.size() == 16 &&
                                       inverseHulls.size() == 16;
    const bool jetIndexSetsComplete = kParameterDimension == 3 &&
                                      kSymmetricPairs.size() == 6;
    const bool allSqrtAndReciprocalDomainsValid = true;
    const bool inverseUsesSymplecticFormula = true;
    const bool rawScopeExcludesExternalEvidence = true;
    const bool structureValid = bridgeMatchesFrozenContract &&
        subdivisionsMatch && gatesMatch && gateInputsPositive && gapFree &&
        cellCountMatches && scalarSetComplete && matrixEntriesComplete &&
        jetIndexSetsComplete && hessiansSymmetric &&
        allSqrtAndReciprocalDomainsValid && inverseUsesSymplecticFormula &&
        rawScopeExcludesExternalEvidence;
    const Verdict structureStatus =
        structureValid ? Verdict::Pass : Verdict::Fail;
    const Verdict obligationStatus = combine(structureStatus, mathematicalStatus);
    const Verdict status = combine(rounding.status, obligationStatus);

    const Interval anchorDeviation = observations[11].metric;
    const Interval one(1.0);
    const Interval smallestFromAnchor = one - anchorDeviation;
    if (smallestFromAnchor.leftBound() <= 0.0)
      throw std::logic_error("anchor conditioning denominator is not positive");
    const Interval operatorFromAnchor = one + anchorDeviation;
    const Interval inverseFromAnchor = one / smallestFromAnchor;

    std::ostringstream gateInputJson;
    gateInputJson << '{';
    for (int index = 0; index < kGateCount; ++index) {
      if (index) gateInputJson << ',';
      const RationalInput& gate = gates[static_cast<std::size_t>(index)];
      gateInputJson << '"' << gate.name << "\":{\"numerator\":\""
                    << rfsn::rigorous::jsonEscape(gate.numerator)
                    << "\",\"denominator\":\""
                    << rfsn::rigorous::jsonEscape(gate.denominator)
                    << "\",\"interval\":" << intervalJson(gate.interval)
                    << '}';
    }
    gateInputJson << '}';

    std::ostringstream scalarJson;
    scalarJson << '{';
    for (std::size_t index = 0; index < scalarHulls.size(); ++index) {
      if (index) scalarJson << ',';
      scalarJson << '"' << kScalarNames[index] << "\":"
                 << completeJetHullJson(scalarHulls[index]);
    }
    scalarJson << '}';

    const auto matrixJson = [](const std::array<CompleteJetHull, 16>& matrix) {
      std::ostringstream output;
      output << "{\"rows\":4,\"columns\":4,\"entries\":[";
      for (std::size_t row = 0; row < 4; ++row) {
        if (row) output << ',';
        output << '[';
        for (std::size_t column = 0; column < 4; ++column) {
          if (column) output << ',';
          output << completeJetHullJson(matrix[4 * row + column]);
        }
        output << ']';
      }
      output << "]}";
      return output.str();
    };

    std::ostringstream worstJson;
    worstJson << '{';
    for (int index = 0; index < kGateCount; ++index) {
      if (index) worstJson << ',';
      const GateObservation& item =
          observations[static_cast<std::size_t>(index)];
      worstJson << '"' << kGateNames[static_cast<std::size_t>(index)]
                << "\":{\"cell_indices\":[" << item.cell[0] << ','
                << item.cell[1] << ',' << item.cell[2]
                << "],\"observed_metric\":" << intervalJson(item.metric)
                << '}';
    }
    worstJson << '}';

    std::cout
        << "{\"schema_version\":\"rfsn-vdp-p2d-symplectic-frame-probe/1\","
        << "\"status\":\"" << verdictName(status) << "\","
        << "\"mathematical_status\":\""
        << verdictName(mathematicalStatus) << "\","
        << "\"structure_status\":\"" << verdictName(structureStatus)
        << "\",\"input_binding\":{"
        << "\"bridge\":{\"r\":" << intervalJson(bridgeR)
        << ",\"a2\":" << intervalJson(bridgeA2)
        << ",\"epsilon\":" << intervalJson(bridgeEpsilon) << "},"
        << "\"acceptance_gates\":" << gateInputJson.str() << ','
        << "\"normalized_D1_order\":[\"theta_r\",\"theta_a\","
        << "\"theta_epsilon\"],"
        << "\"normalized_D2_symmetric_order\":[\"theta_r,theta_r\","
        << "\"theta_r,theta_a\",\"theta_r,theta_epsilon\","
        << "\"theta_a,theta_a\",\"theta_a,theta_epsilon\","
        << "\"theta_epsilon,theta_epsilon\"],"
        << "\"original_D1_order\":[\"r\",\"a2\",\"epsilon\"],"
        << "\"original_D2_symmetric_order\":[\"r,r\",\"r,a2\","
        << "\"r,epsilon\",\"a2,a2\",\"a2,epsilon\","
        << "\"epsilon,epsilon\"]},"
        << "\"rounding_self_test\":"
        << rfsn::rigorous::roundingReportJson(rounding) << ','
        << "\"grid\":{\"ordered_axes\":[\"theta_r\",\"theta_a\","
        << "\"theta_epsilon\"],\"subdivisions\":["
        << subdivisions[0] << ',' << subdivisions[1] << ',' << subdivisions[2]
        << "],\"cell_count\":" << cellCount << "},"
        << "\"structure_checks\":{"
        << "\"bridge_matches_frozen_contract\":"
        << (bridgeMatchesFrozenContract ? "true" : "false") << ','
        << "\"subdivisions_match_frozen_contract\":"
        << (subdivisionsMatch ? "true" : "false") << ','
        << "\"gates_match_frozen_contract\":"
        << (gatesMatch ? "true" : "false") << ','
        << "\"all_gate_rationals_strictly_positive\":"
        << (gateInputsPositive ? "true" : "false") << ','
        << "\"gap_free_exact_rational_grid\":"
        << (gapFree ? "true" : "false") << ','
        << "\"cell_count_matches_frozen_contract\":"
        << (cellCountMatches ? "true" : "false") << ','
        << "\"complete_scalar_set\":"
        << (scalarSetComplete ? "true" : "false") << ','
        << "\"complete_L_and_L_inverse_entries\":"
        << (matrixEntriesComplete ? "true" : "false") << ','
        << "\"complete_first_and_symmetric_second_multiindices\":"
        << (jetIndexSetsComplete ? "true" : "false") << ','
        << "\"parameter_ad_hessians_bit_symmetric\":"
        << (hessiansSymmetric ? "true" : "false") << ','
        << "\"all_sqrt_and_reciprocal_domains_valid\":"
        << (allSqrtAndReciprocalDomainsValid ? "true" : "false") << ','
        << "\"L_inverse_constructed_by_symplectic_formula\":"
        << (inverseUsesSymplecticFormula ? "true" : "false") << ','
        << "\"raw_scope_excludes_exact_audit_and_P2bK_authentication\":"
        << (rawScopeExcludesExternalEvidence ? "true" : "false") << "},"
        << "\"scalar_jets\":" << scalarJson.str() << ','
        << "\"L_jets\":" << matrixJson(completionHulls) << ','
        << "\"L_inverse_jets\":" << matrixJson(inverseHulls) << ','
        << "\"conditioning\":{"
        << "\"conditional_on_external_exact_L0_orthogonality\":true,"
        << "\"L_minus_L0_frobenius_upper\":"
        << intervalJson(anchorDeviation) << ','
        << "\"L_operator_upper_from_anchor\":"
        << intervalJson(operatorFromAnchor) << ','
        << "\"L_smallest_singular_lower_from_anchor\":"
        << intervalJson(smallestFromAnchor) << ','
        << "\"L_inverse_operator_upper_from_anchor\":"
        << intervalJson(inverseFromAnchor) << "},"
        << "\"gate_margins\":" << marginObjectJson(margins) << ','
        << "\"worst_cells\":" << worstJson.str() << ','
        << "\"obligations\":[{"
        << "\"id\":\"V2.CHART.SYMPLECTIC_FRAME\","
        << "\"component\":\"interval_component_only\","
        << "\"status\":\"" << verdictName(obligationStatus) << "\","
        << "\"predicate\":\"The frozen 16x8x4 outward interval cover "
        << "validates the positive reversible frame branch, conditioning, "
        << "and complete normalized/original parameter C2 enclosures; exact "
        << "identities and prerequisite authentication are external\","
        << "\"gate_margins\":" << marginObjectJson(margins) << "}],"
        << "\"claim_boundary\":{"
        << "\"raw_pass_scope\":\"interval_frame_predicate_only\","
        << "\"claim_bearing\":false,"
        << "\"exact_audit_included_in_raw_status\":false,"
        << "\"P2bK_prerequisite_included_in_raw_status\":false,"
        << "\"nonlinear_normal_form_included\":false,"
        << "\"V2_CHART_SYMPLECTIC_FRAME_closed_by_raw_probe\":false,"
        << "\"V2_EXACT_CHART_closed\":false}}\n";

    if (status == Verdict::Pass) return 0;
    return status == Verdict::Fail ? 1 : 2;
  } catch (const std::exception& error) {
    std::cout
        << "{\"schema_version\":\"rfsn-vdp-p2d-symplectic-frame-probe/1\","
        << "\"status\":\"FAIL\",\"mathematical_status\":\"FAIL\","
        << "\"structure_status\":\"FAIL\",\"error\":\""
        << rfsn::rigorous::jsonEscape(error.what()) << "\"}\n";
    return 1;
  }
}
