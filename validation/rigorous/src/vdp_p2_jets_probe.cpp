#include "interval_io.hpp"
#include "rounding_self_test.hpp"
#include "verdict.hpp"

#include <algorithm>
#include <array>
#include <cctype>
#include <cstdint>
#include <exception>
#include <iostream>
#include <limits>
#include <map>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

// Positional interface (argc=107):
//
//   12 bridge strings: lower/upper rational endpoints for r,a2,epsilon;
//   9 rational pairs:
//   R, X_star, D_star, omega_local, omega_hom_reserved, sigma_2, sigma_3,
//   original_parameter_first_derivative_scale,
//   original_parameter_second_derivative_scale;
//   4 positive subdivision integers for theta_r,theta_a,theta_epsilon,x;
//   36 rational gate pairs:
//   B_0,B_1,B_2,h_0,h_1,h_2,ell_0,ell_1,ell_2,
//   m_0,m_1,m_2,t_0,t_1,t_2,
//   alpha_lower,green_upper,contraction_upper,resolvent_upper,kappa_lower,
//   state_2_margin_lower,state_3_margin_lower,
//   origin_2_margin_lower,origin_3_margin_lower,
//   Z_0_0,Z_0_1,Z_0_2,Z_1_0,Z_1_1,Z_1_2,
//   Z_2_0,Z_2_1,Z_2_2,Z_3_0,Z_3_1,Z_3_2.
//
// All acceptance budgets are therefore supplied from the hash-checked frozen
// configuration by the runner; no acceptance threshold is compiled here.

namespace {

using rfsn::rigorous::Interval;
using rfsn::rigorous::Verdict;
using rfsn::rigorous::combine;
using rfsn::rigorous::intervalJson;
using rfsn::rigorous::verdictName;

constexpr int kParameterDimension = 3;
constexpr int kRationalInputCount = 45;
constexpr std::array<int, 4> kExpectedSubdivisions{16, 8, 4, 2};

using Enclosures = std::vector<std::pair<std::string, Interval>>;
using JetIndex = std::pair<int, int>;

constexpr std::array<const char*, kRationalInputCount> kInputNames{
    "unstable_radius",
    "true_graph_x_absolute_upper",
    "true_graph_first_derivative_upper",
    "local_tail_weight",
    "final_homoclinic_weight_reserved",
    "sigma_2",
    "sigma_3",
    "original_parameter_first_derivative_scale",
    "original_parameter_second_derivative_scale",
    "B_0_gate",
    "B_1_gate",
    "B_2_gate",
    "h_0_gate",
    "h_1_gate",
    "h_2_gate",
    "ell_0_gate",
    "ell_1_gate",
    "ell_2_gate",
    "m_0_gate",
    "m_1_gate",
    "m_2_gate",
    "t_0_gate",
    "t_1_gate",
    "t_2_gate",
    "alpha_lower_gate",
    "green_operator_upper_gate",
    "linearized_contraction_upper_gate",
    "resolvent_upper_gate",
    "state_normal_gap_lower_gate",
    "state_second_no_first_exit_margin_lower_gate",
    "state_third_no_first_exit_margin_lower_gate",
    "origin_second_margin_lower_gate",
    "origin_third_margin_lower_gate",
    "Z_0_0_gate",
    "Z_0_1_gate",
    "Z_0_2_gate",
    "Z_1_0_gate",
    "Z_1_1_gate",
    "Z_1_2_gate",
    "Z_2_0_gate",
    "Z_2_1_gate",
    "Z_2_2_gate",
    "Z_3_0_gate",
    "Z_3_1_gate",
    "Z_3_2_gate"};

struct RationalInput {
  std::string name;
  std::string numerator;
  std::string denominator;
  Interval interval;
};

bool validIntegerText(const std::string& value) {
  if (value.empty()) return false;
  std::size_t index = value.front() == '-' ? 1 : 0;
  if (index == value.size()) return false;
  for (; index < value.size(); ++index)
    if (!std::isdigit(static_cast<unsigned char>(value[index]))) return false;
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
  if (!validIntegerText(top) || !validPositiveIntegerText(bottom))
    throw std::invalid_argument("malformed exact rational for " + name);
  return {name, top, bottom,
          rfsn::rigorous::exactRational(top, bottom)};
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
  if (lower.interval.rightBound() > upper.interval.leftBound())
    throw std::invalid_argument("reversed rational interval for " + name);
  return Interval(lower.interval.leftBound(), upper.interval.rightBound());
}

int readPositiveSubdivision(const char* value, const std::string& name) {
  const std::string text(value);
  if (!validPositiveIntegerText(text))
    throw std::invalid_argument("malformed positive subdivision for " + name);
  const long long parsed = std::stoll(text);
  if (parsed > 1000000)
    throw std::invalid_argument("subdivision is unreasonably large for " + name);
  return static_cast<int>(parsed);
}

Interval rationalFromIntegers(long long numerator, long long denominator) {
  if (denominator <= 0)
    throw std::logic_error("internally generated rational denominator is not positive");
  return rfsn::rigorous::exactRational(
      std::to_string(numerator), std::to_string(denominator));
}

Interval normalizedCell(int index, int count) {
  if (count <= 0 || index < 0 || index >= count)
    throw std::logic_error("invalid normalized-grid cell index");
  const long long denominator = count;
  const Interval left = rationalFromIntegers(-count + 2 * index, denominator);
  const Interval right =
      rationalFromIntegers(-count + 2 * (index + 1), denominator);
  return Interval(left.leftBound(), right.rightBound());
}

Interval scaledSymmetricCell(int index, int count,
                             const RationalInput& radius) {
  if (count <= 0 || index < 0 || index >= count)
    throw std::logic_error("invalid scaled-grid cell index");
  const long long radiusNumerator = std::stoll(radius.numerator);
  const long long radiusDenominator = std::stoll(radius.denominator);
  if (radiusNumerator <= 0)
    throw std::invalid_argument("scaled-grid radius is not positive");
  if (radiusDenominator > std::numeric_limits<long long>::max() / count ||
      radiusNumerator > std::numeric_limits<long long>::max() / (2LL * count))
    throw std::invalid_argument("scaled-grid rational overflows int64");
  const long long denominator = radiusDenominator * count;
  const Interval left = rationalFromIntegers(
      radiusNumerator * (-count + 2 * index), denominator);
  const Interval right = rationalFromIntegers(
      radiusNumerator * (-count + 2 * (index + 1)), denominator);
  return Interval(left.leftBound(), right.rightBound());
}

std::vector<Interval> normalizedCells(int count) {
  std::vector<Interval> result;
  result.reserve(count);
  for (int index = 0; index < count; ++index)
    result.push_back(normalizedCell(index, count));
  return result;
}

std::vector<Interval> scaledSymmetricCells(int count,
                                           const RationalInput& radius) {
  std::vector<Interval> result;
  result.reserve(count);
  for (int index = 0; index < count; ++index)
    result.push_back(scaledSymmetricCell(index, count, radius));
  return result;
}

bool gapFreeCover(const std::vector<Interval>& cells,
                  const Interval& lower, const Interval& upper) {
  if (cells.empty() || cells.front().leftBound() > lower.leftBound() ||
      cells.back().rightBound() < upper.rightBound()) return false;
  for (std::size_t index = 0; index < cells.size(); ++index) {
    if (cells[index].leftBound() > cells[index].rightBound()) return false;
    if (index && cells[index - 1].rightBound() < cells[index].leftBound())
      return false;
  }
  return true;
}

Interval absoluteEnvelope(const Interval& value) {
  const double upper = std::max(
      std::abs(value.leftBound()), std::abs(value.rightBound()));
  return Interval(0.0, upper);
}

Interval integerPower(Interval value, int exponent) {
  if (exponent < 0) throw std::logic_error("negative integer power");
  Interval result(1.0);
  for (int index = 0; index < exponent; ++index) result *= value;
  return result;
}

Interval upperEnvelope(const Interval& left, const Interval& right) {
  return Interval(0.0, std::max(left.rightBound(), right.rightBound()));
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
    result.gradient.at(index) = Interval(1.0);
    return result;
  }
};

Jet2 operator+(const Jet2& left, const Jet2& right) {
  Jet2 result;
  result.value = left.value + right.value;
  for (int i = 0; i < kParameterDimension; ++i) {
    result.gradient[i] = left.gradient[i] + right.gradient[i];
    for (int j = 0; j < kParameterDimension; ++j)
      result.hessian[i][j] = left.hessian[i][j] + right.hessian[i][j];
  }
  return result;
}

Jet2 operator-(const Jet2& value) {
  Jet2 result;
  result.value = -value.value;
  for (int i = 0; i < kParameterDimension; ++i) {
    result.gradient[i] = -value.gradient[i];
    for (int j = 0; j < kParameterDimension; ++j)
      result.hessian[i][j] = -value.hessian[i][j];
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
    result.gradient[i] =
        left.gradient[i] * right.value + left.value * right.gradient[i];
    for (int j = 0; j < kParameterDimension; ++j) {
      result.hessian[i][j] =
          left.hessian[i][j] * right.value
          + left.gradient[i] * right.gradient[j]
          + left.gradient[j] * right.gradient[i]
          + left.value * right.hessian[i][j];
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
    result.gradient[i] = firstDerivative * argument.gradient[i];
    for (int j = 0; j < kParameterDimension; ++j) {
      result.hessian[i][j] =
          secondDerivative * argument.gradient[i] * argument.gradient[j]
          + firstDerivative * argument.hessian[i][j];
    }
  }
  return result;
}

Jet2 squareRoot(const Jet2& argument) {
  if (argument.value.leftBound() <= 0.0)
    throw std::logic_error("square-root AD argument is not uniformly positive");
  const Interval root = sqrt(argument.value);
  const Interval first = Interval(1.0) / (Interval(2.0) * root);
  const Interval second =
      -Interval(1.0) / (Interval(4.0) * argument.value * root);
  return compose(argument, root, first, second);
}

Jet2 reciprocal(const Jet2& argument) {
  if (containsZero(argument.value))
    throw std::logic_error("reciprocal AD argument contains zero");
  const Interval inverse = Interval(1.0) / argument.value;
  const Interval first = -inverse * inverse;
  const Interval second = Interval(2.0) * inverse * inverse * inverse;
  return compose(argument, inverse, first, second);
}

Jet2 operator/(const Jet2& left, const Jet2& right) {
  return left * reciprocal(right);
}

bool symmetricHessian(const Jet2& value) {
  for (int i = 0; i < kParameterDimension; ++i)
    for (int j = 0; j < kParameterDimension; ++j)
      if (value.hessian[i][j].rightBound() <
              value.hessian[j][i].leftBound() ||
          value.hessian[j][i].rightBound() <
              value.hessian[i][j].leftBound())
        return false;
  return true;
}

bool jetContainsZero(const Jet2& value) {
  if (!containsZero(value.value)) return false;
  for (int i = 0; i < kParameterDimension; ++i) {
    if (!containsZero(value.gradient[i])) return false;
    for (int j = 0; j < kParameterDimension; ++j)
      if (!containsZero(value.hessian[i][j])) return false;
  }
  return true;
}

struct VectorJetBounds {
  Interval order0{0.0};
  Interval order1{0.0};
  Interval order2{0.0};
};

VectorJetBounds vectorBounds(const std::array<Jet2, 2>& vector) {
  Interval sum0(0.0);
  Interval sum1(0.0);
  Interval sum2(0.0);
  for (const auto& component : vector) {
    sum0 += sqr(absoluteEnvelope(component.value));
    for (int i = 0; i < kParameterDimension; ++i) {
      sum1 += sqr(absoluteEnvelope(component.gradient[i]));
      for (int j = 0; j < kParameterDimension; ++j)
        sum2 += sqr(absoluteEnvelope(component.hessian[i][j]));
    }
  }
  return {sqrt(sum0), sqrt(sum1), sqrt(sum2)};
}

VectorJetBounds physicalFrameBounds(
    const std::array<std::array<Jet2, 4>, 4>& matrix) {
  Interval sum0(0.0);
  Interval sum1(0.0);
  Interval sum2(0.0);
  for (const auto& row : matrix) {
    for (const auto& entry : row) {
      sum0 += sqr(absoluteEnvelope(entry.value));
      for (int i = 0; i < kParameterDimension; ++i) {
        sum1 += sqr(absoluteEnvelope(entry.gradient[i]));
        for (int j = 0; j < kParameterDimension; ++j)
          sum2 += sqr(absoluteEnvelope(entry.hessian[i][j]));
      }
    }
  }
  // |z|_2 <= sqrt(2) max{|u|_2,|s|_2}; Frobenius/Hilbert--Schmidt
  // bounds then dominate the corresponding labelled multilinear operator
  // norms from the moving max-block coordinates to physical Euclidean space.
  const Interval blockConversion = sqrt(Interval(2.0));
  return {blockConversion * sqrt(sum0),
          blockConversion * sqrt(sum1),
          blockConversion * sqrt(sum2)};
}

VectorJetBounds blockBounds(const Jet2& alpha, const Jet2& beta) {
  const Interval lambda = Interval(1.0) / sqrt(Interval(2.0));
  std::array<Jet2, 2> pair{alpha, beta};
  pair[0].value -= lambda;
  pair[1].value -= lambda;
  return vectorBounds(pair);
}

void maximize(VectorJetBounds& target, const VectorJetBounds& candidate) {
  target.order0 = upperEnvelope(target.order0, candidate.order0);
  target.order1 = upperEnvelope(target.order1, candidate.order1);
  target.order2 = upperEnvelope(target.order2, candidate.order2);
}

struct Label {
  bool parameter;
};

void partitionsRecursive(const std::vector<int>& labels, int position,
                         std::vector<std::vector<int>>& blocks,
                         std::vector<std::vector<std::vector<int>>>& output,
                         int maximumBlocks) {
  if (position == static_cast<int>(labels.size())) {
    if (!blocks.empty() && static_cast<int>(blocks.size()) <= maximumBlocks)
      output.push_back(blocks);
    return;
  }
  const std::size_t existingBlocks = blocks.size();
  for (std::size_t blockIndex = 0; blockIndex < existingBlocks; ++blockIndex) {
    blocks[blockIndex].push_back(labels[position]);
    partitionsRecursive(labels, position + 1, blocks, output, maximumBlocks);
    blocks[blockIndex].pop_back();
  }
  if (static_cast<int>(blocks.size()) < maximumBlocks) {
    blocks.push_back({labels[position]});
    partitionsRecursive(labels, position + 1, blocks, output, maximumBlocks);
    blocks.pop_back();
  }
}

std::vector<std::vector<std::vector<int>>> partitions(
    const std::vector<int>& labels, int maximumBlocks) {
  std::vector<std::vector<std::vector<int>>> output;
  std::vector<std::vector<int>> blocks;
  blocks.reserve(maximumBlocks);
  partitionsRecursive(labels, 0, blocks, output, maximumBlocks);
  return output;
}

long long binomialInteger(int n, int k) {
  if (k < 0 || k > n) return 0;
  k = std::min(k, n - k);
  long long result = 1;
  for (int i = 1; i <= k; ++i) result = result * (n - k + i) / i;
  return result;
}

long long stirlingSecond(int n, int k) {
  if (n == 0) return k == 0 ? 1 : 0;
  if (k <= 0 || k > n) return 0;
  return k * stirlingSecond(n - 1, k)
         + stirlingSecond(n - 1, k - 1);
}

std::size_t expectedRemainderTerms(int stateOrder, int parameterOrder) {
  if (stateOrder == 0 && parameterOrder == 0) return 0;
  long long result = 0;
  const int total = stateOrder + parameterOrder;
  for (int explicitOrder = 0; explicitOrder <= parameterOrder;
       ++explicitOrder) {
    const long long choices = binomialInteger(parameterOrder, explicitOrder);
    const int remaining = total - explicitOrder;
    if (remaining == 0) {
      if (stateOrder == 0) result += choices;
      continue;
    }
    long long partitionCount = 0;
    for (int blocks = 1; blocks <= std::min(3, remaining); ++blocks)
      partitionCount += stirlingSecond(remaining, blocks);
    if (explicitOrder == 0) --partitionCount;
    result += choices * partitionCount;
  }
  if (result < 0) throw std::logic_error("negative recurrence term count");
  return static_cast<std::size_t>(result);
}

struct RecurrenceResult {
  Interval remainder{0.0};
  std::size_t termCount = 0;
};

RecurrenceResult recurrenceRemainder(
    int stateOrder, int parameterOrder,
    const std::array<std::array<Interval, 3>, 4>& coefficients,
    const std::map<JetIndex, Interval>& jets) {
  std::vector<Label> labels;
  for (int i = 0; i < stateOrder; ++i) labels.push_back({false});
  for (int j = 0; j < parameterOrder; ++j) labels.push_back({true});
  const int labelCount = static_cast<int>(labels.size());
  RecurrenceResult result;

  // Each mask selects the labelled parameter derivatives that act explicitly
  // on R_theta.  Every remaining labelled derivative is partitioned into at
  // most three nonempty Z-blocks because the state nonlinearity is cubic.
  for (int mask = 0; mask < (1 << labelCount); ++mask) {
    bool validMask = true;
    int explicitOrder = 0;
    std::vector<int> remaining;
    for (int index = 0; index < labelCount; ++index) {
      if ((mask >> index) & 1) {
        if (!labels[index].parameter) validMask = false;
        ++explicitOrder;
      } else {
        remaining.push_back(index);
      }
    }
    if (!validMask || explicitOrder > 2) continue;
    if (remaining.empty()) {
      if (stateOrder == 0) {
        result.remainder += coefficients[0][explicitOrder];
        ++result.termCount;
      }
      continue;
    }
    for (const auto& partition : partitions(remaining, 3)) {
      const int blockCount = static_cast<int>(partition.size());
      if (explicitOrder == 0 && blockCount == 1 &&
          partition.front().size() == labels.size())
        continue;  // Move the unique unpartitioned D_Z R target to the left.
      Interval term = coefficients[blockCount][explicitOrder];
      for (const auto& block : partition) {
        int blockState = 0;
        int blockParameter = 0;
        for (int index : block) {
          if (labels[index].parameter)
            ++blockParameter;
          else
            ++blockState;
        }
        const auto found = jets.find({blockState, blockParameter});
        if (found == jets.end())
          throw std::logic_error(
              "jet recurrence is not triangular: target=(" +
              std::to_string(stateOrder) + "," +
              std::to_string(parameterOrder) + "), block=(" +
              std::to_string(blockState) + "," +
              std::to_string(blockParameter) + ")");
        term *= found->second;
      }
      result.remainder += term;
      ++result.termCount;
    }
  }
  return result;
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

bool allStrictlyPositive(const std::vector<RationalInput>& inputs) {
  for (const auto& input : inputs)
    if (input.interval.leftBound() <= 0.0) return false;
  return true;
}

}  // namespace

int main(int argc, char** argv) {
  try {
    if (argc != 107) {
      throw std::invalid_argument(
          "expected argc=107: 12 bridge strings, 9 rational pairs, 4 "
          "subdivision integers, 15 coefficient-gate pairs, 9 "
          "acceptance-gate pairs, and 12 weighted-jet-gate pairs; "
          "see the positional interface comment in vdp_p2_jets_probe.cpp");
    }

    const Interval bridgeR = readRationalInterval(
        argv[1], argv[2], argv[3], argv[4], "r");
    const Interval bridgeA2 = readRationalInterval(
        argv[5], argv[6], argv[7], argv[8], "a2");
    const Interval bridgeEpsilon = readRationalInterval(
        argv[9], argv[10], argv[11], argv[12], "epsilon");

    std::vector<RationalInput> inputs;
    inputs.reserve(kRationalInputCount);
    for (int index = 0; index < 9; ++index)
      inputs.push_back(readRational(argv[13 + 2 * index],
                                    argv[14 + 2 * index],
                                    kInputNames[index]));
    const std::array<int, 4> subdivisions{
        readPositiveSubdivision(argv[31], "theta_r"),
        readPositiveSubdivision(argv[32], "theta_a"),
        readPositiveSubdivision(argv[33], "theta_epsilon"),
        readPositiveSubdivision(argv[34], "x")};
    for (int index = 9; index < kRationalInputCount; ++index) {
      const int gateOffset = index - 9;
      inputs.push_back(readRational(argv[35 + 2 * gateOffset],
                                    argv[36 + 2 * gateOffset],
                                    kInputNames[index]));
    }
    const auto input = [&](int index) -> const Interval& {
      return inputs.at(index).interval;
    };

    const auto rounding = rfsn::rigorous::runRoundingSelfTests();

    const Interval& radius = input(0);
    const Interval& xAbsoluteUpper = input(1);
    const Interval& derivativeUpper = input(2);
    const Interval& localWeight = input(3);
    const Interval& finalHomoclinicWeight = input(4);
    const Interval& sigma2 = input(5);
    const Interval& sigma3 = input(6);
    const Interval& originalFirstDerivativeScale = input(7);
    const Interval& originalSecondDerivativeScale = input(8);

    // Positivity of radii, weights, tensor balls, and every frozen gate is a
    // configuration-structure requirement, not a numerical sufficient gate.
    const bool allInputsStrictlyPositive = allStrictlyPositive(inputs);
    const bool homoclinicWeightBelowLocalWeight =
        finalHomoclinicWeight.rightBound() < localWeight.leftBound();
    bool structureValid = allInputsStrictlyPositive &&
                          homoclinicWeightBelowLocalWeight;
    const bool subdivisionsMatchFrozenContract =
        subdivisions == kExpectedSubdivisions;
    structureValid = structureValid && subdivisionsMatchFrozenContract;

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
    structureValid = structureValid && bridgeMatchesNormalization;
    const bool originalParameterScalesMatchFrozenContract =
        intervalBitEqual(originalFirstDerivativeScale,
                         readRational("25", "1", "expected_first_scale").interval) &&
        intervalBitEqual(originalSecondDerivativeScale,
                         readRational("625", "1", "expected_second_scale").interval);
    structureValid = structureValid &&
                     originalParameterScalesMatchFrozenContract;

    const auto thetaRCells = normalizedCells(subdivisions[0]);
    const auto thetaACells = normalizedCells(subdivisions[1]);
    const auto thetaEpsilonCells = normalizedCells(subdivisions[2]);
    const auto xCells = scaledSymmetricCells(subdivisions[3], inputs[1]);
    const Interval normalizedLower(-1.0);
    const Interval normalizedUpper(1.0);
    const Interval xLower = -xAbsoluteUpper;
    const Interval xUpper = xAbsoluteUpper;
    const bool gridGapFree =
        gapFreeCover(thetaRCells, normalizedLower, normalizedUpper) &&
        gapFreeCover(thetaACells, normalizedLower, normalizedUpper) &&
        gapFreeCover(thetaEpsilonCells, normalizedLower, normalizedUpper) &&
        gapFreeCover(xCells, xLower, xUpper);
    structureValid = structureValid && gridGapFree;

    VectorJetBounds block;
    VectorJetBounds nonlinearValue;
    VectorJetBounds nonlinearFirst;
    VectorJetBounds nonlinearSecond;
    VectorJetBounds nonlinearThird;
    VectorJetBounds physicalFrame;
    Interval alphaEnvelope;
    bool haveAlpha = false;
    bool adHessiansSymmetric = true;
    bool algebraicIdentitiesContainZero = true;

    for (const Interval& thetaRCell : thetaRCells) {
      for (const Interval& thetaACell : thetaACells) {
        for (const Interval& thetaEpsilonCell : thetaEpsilonCells) {
          const Jet2 thetaR = Jet2::variable(thetaRCell, 0);
          const Jet2 thetaA = Jet2::variable(thetaACell, 1);
          const Jet2 thetaEpsilon = Jet2::variable(thetaEpsilonCell, 2);
          const Jet2 r = (thetaR + Jet2(Interval(1.0))) /
                         Jet2(Interval(25.0));
          const Jet2 a2 = thetaA / Jet2(Interval(4.0));
          const Jet2 epsilon = Jet2(Interval(1.0)) +
                               thetaEpsilon / Jet2(Interval(5.0));
          const Jet2 rootEpsilon = squareRoot(epsilon);
          const Jet2 r2 = r * r;
          const Jet2 r3 = r2 * r;
          const Jet2 r4 = r2 * r2;
          const Jet2 a = Jet2(Interval(1.0)) + rootEpsilon * r3 * a2;
          const Jet2 b = rootEpsilon * r2 / Jet2(Interval(3.0));
          const Jet2 c = Interval(2.0) * r * a2
                         + rootEpsilon * r4 * a2 * a2;
          const Jet2 alpha = Interval(0.5) *
                             squareRoot(Jet2(Interval(2.0)) + c);
          const Jet2 beta = Interval(0.5) *
                            squareRoot(Jet2(Interval(2.0)) - c);
          const Jet2 frameH = Interval(2.0) * alpha * beta;
          const std::array<Jet2, 2> q{
              reciprocal(Interval(4.0) * alpha),
              -reciprocal(Interval(4.0) * beta)};

          if (!haveAlpha) {
            alphaEnvelope = alpha.value;
            haveAlpha = true;
          } else {
            alphaEnvelope = hullIntervals(alphaEnvelope, alpha.value);
          }
          maximize(block, blockBounds(alpha, beta));
          const Jet2 zero(Interval(0.0));
          const Jet2 one(Interval(1.0));
          const std::array<std::array<Jet2, 4>, 4> frame{{
              {{one, zero, one, zero}},
              {{alpha, -beta, -alpha, beta}},
              {{Interval(0.5) * c, frameH,
                Interval(0.5) * c, frameH}},
              {{alpha, beta, -alpha, -beta}},
          }};
          maximize(physicalFrame, physicalFrameBounds(frame));

          const Jet2 alphaIdentity =
              alpha * alpha -
              (Jet2(Interval(2.0)) + c) / Jet2(Interval(4.0));
          const Jet2 betaIdentity =
              beta * beta -
              (Jet2(Interval(2.0)) - c) / Jet2(Interval(4.0));
          const Jet2 q1Identity =
              Interval(4.0) * alpha * q[0] - Jet2(Interval(1.0));
          const Jet2 q2Identity =
              Interval(4.0) * beta * q[1] + Jet2(Interval(1.0));
          algebraicIdentitiesContainZero = algebraicIdentitiesContainZero &&
              jetContainsZero(alphaIdentity) &&
              jetContainsZero(betaIdentity) &&
              jetContainsZero(q1Identity) && jetContainsZero(q2Identity);
          adHessiansSymmetric = adHessiansSymmetric &&
              symmetricHessian(a) && symmetricHessian(b) &&
              symmetricHessian(c) && symmetricHessian(alpha) &&
              symmetricHessian(beta) && symmetricHessian(frameH) &&
              symmetricHessian(q[0]) &&
              symmetricHessian(q[1]);

          for (const Interval& xCell : xCells) {
            const Jet2 x(xCell);  // Parameter derivatives are at fixed x.
            const Jet2 n = -a * x * x + b * x * x * x;
            const Jet2 np = Interval(-2.0) * a * x
                            + Interval(3.0) * b * x * x;
            const Jet2 npp = -Interval(2.0) * a
                             + Interval(6.0) * b * x;
            const Jet2 nppp = Interval(6.0) * b;
            std::array<Jet2, 2> gValue;
            std::array<Jet2, 2> gFirst;
            std::array<Jet2, 2> gSecond;
            std::array<Jet2, 2> gThird;
            for (int component = 0; component < 2; ++component) {
              gValue[component] = q[component] * n;
              gFirst[component] = q[component] * np;
              gSecond[component] = q[component] * npp;
              gThird[component] = q[component] * nppp;
              adHessiansSymmetric = adHessiansSymmetric &&
                  symmetricHessian(gValue[component]) &&
                  symmetricHessian(gFirst[component]) &&
                  symmetricHessian(gSecond[component]) &&
                  symmetricHessian(gThird[component]);
            }
            maximize(nonlinearValue, vectorBounds(gValue));
            maximize(nonlinearFirst, vectorBounds(gFirst));
            maximize(nonlinearSecond, vectorBounds(gSecond));
            maximize(nonlinearThird, vectorBounds(gThird));
          }
        }
      }
    }

    // The displayed construction is cubic in the fixed state coordinate x;
    // all state derivatives of order four and higher vanish identically.
    const bool stateDegreeStructure = true;
    structureValid = structureValid && haveAlpha && adHessiansSymmetric &&
                     algebraicIdentitiesContainZero && stateDegreeStructure;

    const std::array<VectorJetBounds, 5> coefficientGroups{
        block, nonlinearValue, nonlinearFirst,
        nonlinearSecond, nonlinearThird};
    const std::array<const char*, 5> coefficientPrefixes{
        "B", "h", "ell", "m", "t"};
    Enclosures coefficientEnclosures;
    Enclosures coefficientGateMargins;
    int gateIndex = 9;
    for (std::size_t group = 0; group < coefficientGroups.size(); ++group) {
      const std::array<Interval, 3> orders{
          coefficientGroups[group].order0,
          coefficientGroups[group].order1,
          coefficientGroups[group].order2};
      for (int order = 0; order <= 2; ++order) {
        const std::string name =
            std::string(coefficientPrefixes[group]) + "_" +
            std::to_string(order);
        coefficientEnclosures.push_back({name, orders[order]});
        coefficientGateMargins.push_back(
            {name + "_upper_margin", input(gateIndex) - orders[order]});
        ++gateIndex;
      }
    }
    if (gateIndex != 24)
      throw std::logic_error("coefficient gate indexing is incomplete");

    const std::array<Interval, 3> B{
        block.order0, block.order1, block.order2};
    const std::array<Interval, 3> ell{
        nonlinearFirst.order0, nonlinearFirst.order1,
        nonlinearFirst.order2};
    const std::array<Interval, 3> m{
        nonlinearSecond.order0, nonlinearSecond.order1,
        nonlinearSecond.order2};
    const std::array<Interval, 3> third{
        nonlinearThird.order0, nonlinearThird.order1,
        nonlinearThird.order2};

    std::array<std::array<Interval, 3>, 4> coefficients{};
    Enclosures lpCoefficientEnclosures;
    for (int order = 0; order <= 2; ++order) {
      coefficients[1][order] = B[order] + Interval(2.0) * ell[order];
      coefficients[0][order] = coefficients[1][order] * radius;
      coefficients[2][order] = Interval(4.0) * m[order];
      coefficients[3][order] = Interval(8.0) * third[order];
      for (int stateDerivative = 0; stateDerivative <= 3;
           ++stateDerivative) {
        lpCoefficientEnclosures.push_back(
            {"L_" + std::to_string(stateDerivative) + "_" +
                 std::to_string(order),
             coefficients[stateDerivative][order]});
      }
    }

    const Interval lambda = Interval(1.0) / sqrt(Interval(2.0));
    const Interval weightGap = lambda - localWeight;
    if (weightGap.leftBound() <= 0.0)
      throw std::logic_error(
          "local tail weight does not lie below the fixed core rate");
    const Interval green = Interval(1.0) / weightGap;
    const Interval contraction = green * coefficients[1][0];
    const Interval resolventDenominator = Interval(1.0) - contraction;
    if (resolventDenominator.leftBound() <= 0.0)
      throw std::logic_error(
          "linearized Lyapunov-Perron denominator is not positive");
    const Interval resolvent = Interval(1.0) / resolventDenominator;

    const Interval onePlusDerivative = Interval(1.0) + derivativeUpper;
    const Interval kappa =
        alphaEnvelope - onePlusDerivative * nonlinearFirst.order0;
    const Interval forcing2 = nonlinearSecond.order0 *
                              integerPower(onePlusDerivative, 3);
    const Interval forcing3 =
        onePlusDerivative *
            (nonlinearThird.order0 * integerPower(onePlusDerivative, 3)
             + Interval(3.0) * nonlinearSecond.order0 * sigma2 *
                   onePlusDerivative)
        + Interval(3.0) * sigma2 *
            (nonlinearSecond.order0 * integerPower(onePlusDerivative, 2)
             + nonlinearFirst.order0 * sigma2);
    const Interval state2Margin =
        Interval(3.0) * kappa * sigma2 - forcing2;
    const Interval state3Margin =
        Interval(4.0) * kappa * sigma3 - forcing3;
    const Interval origin2Margin =
        Interval(3.0) * alphaEnvelope * sigma2 - nonlinearSecond.order0;
    const Interval origin3Margin =
        Interval(4.0) * alphaEnvelope * sigma3 -
        (nonlinearThird.order0 +
         Interval(6.0) * nonlinearSecond.order0 * sigma2);

    const Enclosures stateTensorEnclosures{
        {"alpha", alphaEnvelope},
        {"kappa_bar", kappa},
        {"M_2", forcing2},
        {"M_3", forcing3},
        {"state_second_no_first_exit_margin", state2Margin},
        {"state_third_no_first_exit_margin", state3Margin},
        {"origin_second_margin", origin2Margin},
        {"origin_third_margin", origin3Margin}};
    const Enclosures stateTensorGateMargins{
        {"state_normal_gap_lower_margin", kappa - input(28)},
        {"state_second_no_first_exit_gate_margin",
         state2Margin - input(29)},
        {"state_third_no_first_exit_gate_margin",
         state3Margin - input(30)},
        {"origin_second_gate_margin", origin2Margin - input(31)},
        {"origin_third_gate_margin", origin3Margin - input(32)}};

    const Enclosures lpEnclosures{
        {"fixed_core_rate", lambda},
        {"local_tail_weight", localWeight},
        {"final_homoclinic_weight_reserved", finalHomoclinicWeight},
        {"core_rate_minus_local_weight", weightGap},
        {"local_minus_reserved_weight",
         localWeight - finalHomoclinicWeight},
        {"green_operator", green},
        {"linearized_contraction", contraction},
        {"one_minus_linearized_contraction", resolventDenominator},
        {"resolvent", resolvent}};
    const Enclosures lpGateMargins{
        {"alpha_lower_margin", alphaEnvelope - input(24)},
        {"core_rate_minus_local_weight", weightGap},
        {"local_minus_reserved_weight",
         localWeight - finalHomoclinicWeight},
        {"green_operator_upper_margin", input(25) - green},
        {"linearized_contraction_upper_margin", input(26) - contraction},
        {"resolvent_upper_margin", input(27) - resolvent}};

    std::map<JetIndex, Interval> jets;
    std::map<JetIndex, std::size_t> recurrenceTermCounts;
    jets[{0, 0}] = radius;
    recurrenceTermCounts[{0, 0}] = 0;
    bool recurrenceComplete = true;
    for (int totalOrder = 1; totalOrder <= 5; ++totalOrder) {
      for (int stateOrder = 0; stateOrder <= 3; ++stateOrder) {
        for (int parameterOrder = 0; parameterOrder <= 2;
             ++parameterOrder) {
          if (stateOrder + parameterOrder != totalOrder) continue;
          const Interval direct =
              stateOrder == 1 && parameterOrder == 0
                  ? Interval(1.0) : Interval(0.0);
          const RecurrenceResult remainder = recurrenceRemainder(
              stateOrder, parameterOrder, coefficients, jets);
          const std::size_t expected =
              expectedRemainderTerms(stateOrder, parameterOrder);
          recurrenceComplete = recurrenceComplete &&
                               remainder.termCount == expected;
          recurrenceTermCounts[{stateOrder, parameterOrder}] =
              remainder.termCount;
          jets[{stateOrder, parameterOrder}] =
              resolvent * (direct + green * remainder.remainder);
        }
      }
    }
    recurrenceComplete = recurrenceComplete && jets.size() == 12 &&
                         recurrenceTermCounts.size() == 12;
    structureValid = structureValid && recurrenceComplete;

    Enclosures weightedJetEnclosures;
    Enclosures originalParameterWeightedJetEnclosures;
    Enclosures physicalWeightedJetEnclosures;
    Enclosures originalParameterPhysicalWeightedJetEnclosures;
    Enclosures weightedJetGateMargins;
    int weightedGateIndex = 33;
    for (int stateOrder = 0; stateOrder <= 3; ++stateOrder) {
      for (int parameterOrder = 0; parameterOrder <= 2;
           ++parameterOrder) {
        const std::string name = "Z_" + std::to_string(stateOrder) + "_" +
                                 std::to_string(parameterOrder);
        const Interval& jet = jets.at({stateOrder, parameterOrder});
        weightedJetEnclosures.push_back({name, jet});
        const Interval originalScale =
            parameterOrder == 0 ? Interval(1.0) :
            (parameterOrder == 1 ? originalFirstDerivativeScale :
                                   originalSecondDerivativeScale);
        originalParameterWeightedJetEnclosures.push_back(
            {name, originalScale * jet});
        weightedJetGateMargins.push_back(
            {name + "_upper_margin", input(weightedGateIndex) - jet});
        ++weightedGateIndex;
      }
    }
    if (weightedGateIndex != kRationalInputCount)
      throw std::logic_error("weighted-jet gate indexing is incomplete");

    const std::array<Interval, 3> frameDerivativeBounds{
        physicalFrame.order0, physicalFrame.order1, physicalFrame.order2};
    for (int stateOrder = 0; stateOrder <= 3; ++stateOrder) {
      for (int parameterOrder = 0; parameterOrder <= 2;
           ++parameterOrder) {
        Interval physicalJet(0.0);
        for (int frameOrder = 0; frameOrder <= parameterOrder;
             ++frameOrder) {
          physicalJet += Interval(static_cast<double>(
              binomialInteger(parameterOrder, frameOrder))) *
              frameDerivativeBounds[frameOrder] *
              jets.at({stateOrder, parameterOrder - frameOrder});
        }
        const std::string name = "Z_" + std::to_string(stateOrder) + "_" +
                                 std::to_string(parameterOrder);
        physicalWeightedJetEnclosures.push_back({name, physicalJet});
        const Interval originalScale =
            parameterOrder == 0 ? Interval(1.0) :
            (parameterOrder == 1 ? originalFirstDerivativeScale :
                                   originalSecondDerivativeScale);
        originalParameterPhysicalWeightedJetEnclosures.push_back(
            {name, originalScale * physicalJet});
      }
    }

    const Verdict structuralStatus =
        structureValid ? Verdict::Pass : Verdict::Fail;
    const Verdict coefficientOwnStatus =
        sufficientMargins(coefficientGateMargins);
    const Verdict stateOwnStatus = sufficientMargins(stateTensorGateMargins);
    Verdict mixedOwnStatus = sufficientMargins(lpGateMargins);
    mixedOwnStatus = combine(
        mixedOwnStatus, sufficientMargins(weightedJetGateMargins));
    const Verdict weightedOwnStatus = mixedOwnStatus;

    const Verdict coefficientStatus = combine(
        structuralStatus, coefficientOwnStatus);
    const Verdict stateStatus = combine(
        structuralStatus, combine(coefficientStatus, stateOwnStatus));
    const Verdict mixedStatus = combine(
        structuralStatus,
        combine(stateStatus, combine(coefficientStatus, mixedOwnStatus)));
    const Verdict weightedStatus = combine(
        structuralStatus, combine(coefficientStatus, weightedOwnStatus));

    Enclosures weightedObligationEnclosures = lpGateMargins;
    append(weightedObligationEnclosures, weightedJetGateMargins);
    const std::array<Obligation, 4> obligations{
        Obligation{
            "P2.JETS.COEFFICIENTS", coefficientStatus,
            "The exact-rational grid and second-order normalized-parameter "
            "AD bound the moving blocks and the state derivatives through "
            "cubic order by every frozen coefficient budget",
            coefficientGateMargins},
        Obligation{
            "V2.WU.STATE_C23", stateStatus,
            "The true local graph has uniform Hilbert-Schmidt C2 and C3 "
            "tensor balls, with positive no-first-exit margins both on the "
            "true graph tube and at the origin",
            stateTensorGateMargins},
        Obligation{
            "V2.WU.MIXED_JETS", mixedStatus,
            "The complete labelled Faà di Bruno recurrence bounds all "
            "D_b^i D_theta^j graph traces for 0<=i<=3 and 0<=j<=2",
            weightedJetGateMargins},
        Obligation{
            "V2.WU.WEIGHTED_HALF_ORBITS", weightedStatus,
            "The Lyapunov-Perron Green, contraction, and resolvent bounds "
            "give the same full rectangular weighted jets for unstable and "
            "reverser-transported stable local half-orbits",
            weightedObligationEnclosures}};

    Verdict mathematicalStatus = Verdict::Pass;
    for (const auto& obligation : obligations)
      mathematicalStatus = combine(mathematicalStatus, obligation.status);
    const Verdict probeStatus = combine(rounding.status, mathematicalStatus);

    const Enclosures parameterEnclosures{
        {"r", bridgeR},
        {"a2", bridgeA2},
        {"epsilon", bridgeEpsilon},
        {"R", radius},
        {"Xstar", xAbsoluteUpper},
        {"Dstar", derivativeUpper},
        {"omega", localWeight},
        {"hom_weight", finalHomoclinicWeight},
        {"sigma2", sigma2},
        {"sigma3", sigma3},
        {"original_first_derivative_scale", originalFirstDerivativeScale},
        {"original_second_derivative_scale", originalSecondDerivativeScale}};
    Enclosures coefficientGates;
    for (int index = 9; index < 24; ++index)
      coefficientGates.push_back({inputs[index].name, inputs[index].interval});
    Enclosures acceptanceGates;
    for (int index = 24; index < 33; ++index)
      acceptanceGates.push_back({inputs[index].name, inputs[index].interval});
    Enclosures weightedGates;
    for (int index = 33; index < kRationalInputCount; ++index)
      weightedGates.push_back({inputs[index].name, inputs[index].interval});
    const Enclosures frameDerivativeEnclosures{
        {"T_0", physicalFrame.order0},
        {"T_1", physicalFrame.order1},
        {"T_2", physicalFrame.order2}};

    std::ostringstream recurrenceJson;
    recurrenceJson << "{\"complete\":"
                   << (recurrenceComplete ? "true" : "false")
                   << ",\"target_count\":" << jets.size()
                   << ",\"maximum_state_order\":3,"
                   << "\"maximum_parameter_order\":2,"
                   << "\"normalized_parameter_dimension\":3,"
                   << "\"first_parameter_multiindices\":["
                   << "\"theta_r\",\"theta_a\",\"theta_epsilon\"],"
                   << "\"second_symmetric_parameter_multiindices\":["
                   << "\"theta_r,theta_r\",\"theta_r,theta_a\","
                   << "\"theta_r,theta_epsilon\",\"theta_a,theta_a\","
                   << "\"theta_a,theta_epsilon\","
                   << "\"theta_epsilon,theta_epsilon\"],"
                   << "\"term_counts\":{";
    bool firstCount = true;
    for (int stateOrder = 0; stateOrder <= 3; ++stateOrder) {
      for (int parameterOrder = 0; parameterOrder <= 2;
           ++parameterOrder) {
        if (!firstCount) recurrenceJson << ',';
        firstCount = false;
        recurrenceJson << "\"Z_" << stateOrder << '_' << parameterOrder
                       << "\":"
                       << recurrenceTermCounts.at(
                              {stateOrder, parameterOrder});
      }
    }
    recurrenceJson << "}}";

    std::cout
        << "{\"schema_version\":\"rfsn-vdp-p2-jets-probe/1\","
        << "\"status\":\"" << verdictName(probeStatus) << "\","
        << "\"mathematical_status\":\""
        << verdictName(mathematicalStatus) << "\","
        << "\"structure_status\":\""
        << verdictName(structuralStatus) << "\","
        << "\"structure_checks\":{"
        << "\"gap_free_exact_rational_grid\":"
        << (gridGapFree ? "true" : "false") << ','
        << "\"bridge_matches_parameter_normalization\":"
        << (bridgeMatchesNormalization ? "true" : "false") << ','
        << "\"subdivisions_match_frozen_contract\":"
        << (subdivisionsMatchFrozenContract ? "true" : "false") << ','
        << "\"parameter_ad_hessians_symmetric\":"
        << (adHessiansSymmetric ? "true" : "false") << ','
        << "\"algebraic_identities_contain_zero\":"
        << (algebraicIdentitiesContainZero ? "true" : "false") << ','
        << "\"state_degree_at_most_three\":"
        << (stateDegreeStructure ? "true" : "false") << ','
        << "\"complete_parameter_multiindex_coverage\":true,"
        << "\"original_parameter_scales_match_frozen_contract\":"
        << (originalParameterScalesMatchFrozenContract ? "true" : "false")
        << ','
        << "\"all_inputs_strictly_positive\":"
        << (allInputsStrictlyPositive ? "true" : "false") << ','
        << "\"homoclinic_weight_below_local_weight\":"
        << (homoclinicWeightBelowLocalWeight ? "true" : "false") << ','
        << "\"parameter_grid_nonempty\":"
        << (haveAlpha ? "true" : "false") << ','
        << "\"recurrence_complete\":"
        << (recurrenceComplete ? "true" : "false")
        << "},"
        << "\"rounding_self_test\":"
        << rfsn::rigorous::roundingReportJson(rounding) << ','
        << "\"grid\":{"
        << "\"ordered_axes\":[\"theta_r\",\"theta_a\","
        << "\"theta_epsilon\",\"x\"],"
        << "\"subdivisions\":[" << subdivisions[0] << ','
        << subdivisions[1] << ',' << subdivisions[2] << ','
        << subdivisions[3] << "],"
        << "\"cell_count\":"
        << static_cast<long long>(subdivisions[0]) * subdivisions[1] *
               subdivisions[2] * subdivisions[3]
        << ','
        << "\"parameter_derivatives_taken_at_fixed_x\":true},"
        << "\"parameter_enclosures\":"
        << enclosureObjectJson(parameterEnclosures) << ','
        << "\"coefficient_upper_gates\":"
        << enclosureObjectJson(coefficientGates) << ','
        << "\"acceptance_gates\":"
        << enclosureObjectJson(acceptanceGates) << ','
        << "\"normalized_weighted_jet_upper_gates\":"
        << enclosureObjectJson(weightedGates) << ','
        << "\"coefficient_enclosures\":"
        << enclosureObjectJson(coefficientEnclosures) << ','
        << "\"coefficient_gate_margins\":"
        << enclosureObjectJson(coefficientGateMargins) << ','
        << "\"lyapunov_perron_coefficients\":"
        << enclosureObjectJson(lpCoefficientEnclosures) << ','
        << "\"lyapunov_perron_enclosures\":"
        << enclosureObjectJson(lpEnclosures) << ','
        << "\"lyapunov_perron_gate_margins\":"
        << enclosureObjectJson(lpGateMargins) << ','
        << "\"state_tensor_enclosures\":"
        << enclosureObjectJson(stateTensorEnclosures) << ','
        << "\"state_tensor_gate_margins\":"
        << enclosureObjectJson(stateTensorGateMargins) << ','
        << "\"weighted_jet_enclosures\":"
        << enclosureObjectJson(weightedJetEnclosures) << ','
        << "\"original_parameter_weighted_jet_enclosures\":"
        << enclosureObjectJson(originalParameterWeightedJetEnclosures) << ','
        << "\"frame_derivative_enclosures\":"
        << enclosureObjectJson(frameDerivativeEnclosures) << ','
        << "\"physical_weighted_jet_enclosures\":"
        << enclosureObjectJson(physicalWeightedJetEnclosures) << ','
        << "\"original_parameter_physical_weighted_jet_enclosures\":"
        << enclosureObjectJson(
               originalParameterPhysicalWeightedJetEnclosures) << ','
        << "\"coordinate_composition\":{"
        << "\"moving_state_norm\":"
        << "\"max-of-two-euclidean-blocks\","
        << "\"physical_state_norm\":\"euclidean\","
        << "\"jet_tensor_norm\":"
        << "\"labelled-multilinear-operator\","
        << "\"pure_graph_state_tensor_norm\":"
        << "\"hilbert-schmidt\","
        << "\"frame_bound_method\":"
        << "\"sqrt(2)-times-parameter-HS-Frobenius\","
        << "\"complete_leibniz_composition\":true},"
        << "\"linearization_contract\":{"
        << "\"actual_family_source\":"
        << "\"analytic-unstable-manifold-plus-P2a-cone-continuation\","
        << "\"coefficient_domain\":"
        << "\"P2b0-true-orbit-sharpened-x-tube\","
        << "\"inverse_mode\":\"along-true-orbit-Neumann\","
        << "\"full_product_ball_contraction_claimed\":false},"
        << "\"weighted_jet_gate_margins\":"
        << enclosureObjectJson(weightedJetGateMargins) << ','
        << "\"recurrence\":" << recurrenceJson.str() << ','
        << "\"obligations\":[";
    for (std::size_t index = 0; index < obligations.size(); ++index) {
      if (index) std::cout << ',';
      std::cout << obligationJson(obligations[index]);
    }
    std::cout << "]}\n";

    if (probeStatus == Verdict::Pass) return 0;
    return probeStatus == Verdict::Fail ? 1 : 2;
  } catch (const std::exception& error) {
    // Malformed rational input, a broken recurrence, or an impossible AD
    // operation is structural/formula corruption and therefore FAIL, not a
    // merely insufficient numerical gate.
    std::cout
        << "{\"schema_version\":\"rfsn-vdp-p2-jets-probe/1\","
        << "\"status\":\"FAIL\",\"mathematical_status\":\"FAIL\","
        << "\"structure_status\":\"FAIL\",\"error\":\""
        << rfsn::rigorous::jsonEscape(error.what()) << "\"}\n";
    return 1;
  }
}
