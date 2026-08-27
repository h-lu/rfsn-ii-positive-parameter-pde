// Design-only interval scout for the P2b mixed-jet contract.
//
// This program is deliberately outside validation/rigorous/src.  Its output
// is not a certificate and cannot discharge an obligation.  It is used only
// to choose rational budgets before the formal P2b configuration is frozen.

#include "interval_io.hpp"

#include <algorithm>
#include <array>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <map>
#include <stdexcept>
#include <string>
#include <vector>

namespace {

using rfsn::rigorous::Interval;

constexpr int parameterDimension = 3;

double absoluteUpper(const Interval& value) {
  return std::max(std::abs(value.leftBound()),
                  std::abs(value.rightBound()));
}

struct Jet2 {
  Interval value{0.0};
  std::array<Interval, parameterDimension> gradient{};
  std::array<std::array<Interval, parameterDimension>, parameterDimension>
      hessian{};

  Jet2() = default;
  explicit Jet2(const Interval& valueIn) : value(valueIn) {}

  static Jet2 variable(const Interval& value, int index) {
    Jet2 result(value);
    result.gradient.at(index) = Interval(1.0);
    return result;
  }
};

Jet2 operator+(const Jet2& left, const Jet2& right) {
  Jet2 result;
  result.value = left.value + right.value;
  for (int i = 0; i < parameterDimension; ++i) {
    result.gradient[i] = left.gradient[i] + right.gradient[i];
    for (int j = 0; j < parameterDimension; ++j)
      result.hessian[i][j] = left.hessian[i][j] + right.hessian[i][j];
  }
  return result;
}

Jet2 operator-(const Jet2& value) {
  Jet2 result;
  result.value = -value.value;
  for (int i = 0; i < parameterDimension; ++i) {
    result.gradient[i] = -value.gradient[i];
    for (int j = 0; j < parameterDimension; ++j)
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
  for (int i = 0; i < parameterDimension; ++i) {
    result.gradient[i] =
        left.gradient[i] * right.value + left.value * right.gradient[i];
    for (int j = 0; j < parameterDimension; ++j) {
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
  for (int i = 0; i < parameterDimension; ++i) {
    result.gradient[i] = firstDerivative * argument.gradient[i];
    for (int j = 0; j < parameterDimension; ++j) {
      result.hessian[i][j] =
          secondDerivative * argument.gradient[i] * argument.gradient[j]
          + firstDerivative * argument.hessian[i][j];
    }
  }
  return result;
}

Jet2 squareRoot(const Jet2& argument) {
  const Interval root = sqrt(argument.value);
  const Interval first = Interval(1.0) / (Interval(2.0) * root);
  const Interval second =
      -Interval(1.0) / (Interval(4.0) * argument.value * root);
  return compose(argument, root, first, second);
}

Jet2 reciprocal(const Jet2& argument) {
  const Interval inverse = Interval(1.0) / argument.value;
  const Interval first = -inverse * inverse;
  const Interval second = Interval(2.0) * inverse * inverse * inverse;
  return compose(argument, inverse, first, second);
}

Jet2 operator/(const Jet2& left, const Jet2& right) {
  return left * reciprocal(right);
}

struct VectorJetBounds {
  double order0 = 0.0;
  double order1 = 0.0;
  double order2 = 0.0;
};

VectorJetBounds vectorBounds(const std::array<Jet2, 2>& vector) {
  double sum0 = 0.0;
  double sum1 = 0.0;
  double sum2 = 0.0;
  for (const auto& component : vector) {
    sum0 += std::pow(absoluteUpper(component.value), 2);
    for (int i = 0; i < parameterDimension; ++i) {
      sum1 += std::pow(absoluteUpper(component.gradient[i]), 2);
      for (int j = 0; j < parameterDimension; ++j)
        sum2 += std::pow(absoluteUpper(component.hessian[i][j]), 2);
    }
  }
  return {std::sqrt(sum0), std::sqrt(sum1), std::sqrt(sum2)};
}

VectorJetBounds blockBounds(const Jet2& alpha, const Jet2& beta,
                            bool subtractCore) {
  const Interval lambda = sqrt(Interval(2.0)) / Interval(2.0);
  std::array<Jet2, 2> pair{alpha, beta};
  if (subtractCore) {
    pair[0].value -= lambda;
    pair[1].value -= lambda;
  }
  return vectorBounds(pair);
}

void maximize(VectorJetBounds& target, const VectorJetBounds& candidate) {
  target.order0 = std::max(target.order0, candidate.order0);
  target.order1 = std::max(target.order1, candidate.order1);
  target.order2 = std::max(target.order2, candidate.order2);
}

Interval cell(int index, int count) {
  const double left = -1.0 + 2.0 * static_cast<double>(index) / count;
  const double right = -1.0 + 2.0 * static_cast<double>(index + 1) / count;
  return Interval(left, right);
}

Interval stateCell(int index, int count, double radius) {
  const double left = -radius + 2.0 * radius * index / count;
  const double right = -radius + 2.0 * radius * (index + 1) / count;
  return Interval(left, right);
}

using JetIndex = std::pair<int, int>;

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
  for (auto& block : blocks) {
    block.push_back(labels[position]);
    partitionsRecursive(labels, position + 1, blocks, output, maximumBlocks);
    block.pop_back();
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

double recurrenceRemainder(
    int stateOrder, int parameterOrder,
    const std::array<std::array<double, 3>, 4>& coefficients,
    const std::map<JetIndex, double>& jets) {
  std::vector<Label> labels;
  for (int i = 0; i < stateOrder; ++i) labels.push_back({false});
  for (int j = 0; j < parameterOrder; ++j) labels.push_back({true});
  const int labelCount = static_cast<int>(labels.size());
  double result = 0.0;

  // A mask selects parameter labels on which derivatives act explicitly on
  // the coefficient R_theta.  The remaining labels enter through Z(theta,b).
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
      if (stateOrder == 0)
        result += coefficients[0][explicitOrder];
      continue;
    }
    for (const auto& partition : partitions(remaining, 3)) {
      const int p = static_cast<int>(partition.size());
      if (explicitOrder == 0 && p == 1 &&
          partition.front().size() == labels.size()) {
        continue;  // The target D_Z R Z_ij is moved to the left.
      }
      double term = coefficients[p][explicitOrder];
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
      result += term;
    }
  }
  return result;
}

}  // namespace

int main(int argc, char** argv) {
  const std::array<int, 4> subdivision{16, 8, 4, 2};
  const double xRadius = 251.0 / 25000.0;

  VectorJetBounds block;
  VectorJetBounds value;
  VectorJetBounds first;
  VectorJetBounds second;
  VectorJetBounds third;
  double alphaLower = 1.0;

  for (int ir = 0; ir < subdivision[0]; ++ir) {
    for (int ia = 0; ia < subdivision[1]; ++ia) {
      for (int ie = 0; ie < subdivision[2]; ++ie) {
        const Jet2 thetaR = Jet2::variable(cell(ir, subdivision[0]), 0);
        const Jet2 thetaA = Jet2::variable(cell(ia, subdivision[1]), 1);
        const Jet2 thetaE = Jet2::variable(cell(ie, subdivision[2]), 2);
        const Jet2 r = (thetaR + Jet2(Interval(1.0))) /
                       Jet2(Interval(25.0));
        const Jet2 a2 = thetaA / Jet2(Interval(4.0));
        const Jet2 epsilon = Jet2(Interval(1.0)) +
                             thetaE / Jet2(Interval(5.0));
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
        const std::array<Jet2, 2> q{
            reciprocal(Interval(4.0) * alpha),
            -reciprocal(Interval(4.0) * beta)};
        alphaLower = std::min(alphaLower, alpha.value.leftBound());
        maximize(block, blockBounds(alpha, beta, true));

        for (int ix = 0; ix < subdivision[3]; ++ix) {
          const Jet2 x(stateCell(ix, subdivision[3], xRadius));
          const Jet2 n = -a * x * x + b * x * x * x;
          const Jet2 np = Interval(-2.0) * a * x
                          + Interval(3.0) * b * x * x;
          const Jet2 npp = Interval(-2.0) * a
                           + Interval(6.0) * b * x;
          const Jet2 nppp = Interval(6.0) * b;
          std::array<Jet2, 2> gv;
          std::array<Jet2, 2> g1;
          std::array<Jet2, 2> g2;
          std::array<Jet2, 2> g3;
          for (int component = 0; component < 2; ++component) {
            gv[component] = q[component] * n;
            g1[component] = q[component] * np;
            g2[component] = q[component] * npp;
            g3[component] = q[component] * nppp;
          }
          maximize(value, vectorBounds(gv));
          maximize(first, vectorBounds(g1));
          maximize(second, vectorBounds(g2));
          maximize(third, vectorBounds(g3));
        }
      }
    }
  }

  const double radius = 1.0 / 100.0;
  std::array<std::array<double, 3>, 4> coefficient{};
  const std::array<double, 3> B{block.order0, block.order1, block.order2};
  const std::array<double, 3> h{value.order0, value.order1, value.order2};
  const std::array<double, 3> ell{first.order0, first.order1, first.order2};
  const std::array<double, 3> m{second.order0, second.order1, second.order2};
  const std::array<double, 3> t{third.order0, third.order1, third.order2};
  for (int order = 0; order <= 2; ++order) {
    coefficient[0][order] = B[order] * radius + h[order];
    coefficient[1][order] = B[order] + 2.0 * ell[order];
    coefficient[2][order] = 4.0 * m[order];
    coefficient[3][order] = 8.0 * t[order];
  }

  const double lambda = 1.0 / std::sqrt(2.0);
  const double omega = argc > 1 ? std::stod(argv[1]) : 1.0 / 4.0;
  const double green = 1.0 / (lambda - omega);
  const double contraction = green * coefficient[1][0];
  const double resolvent = 1.0 / (1.0 - contraction);

  std::map<JetIndex, double> jets;
  jets[{0, 0}] = radius;
  for (int total = 1; total <= 5; ++total) {
    for (int stateOrder = 0; stateOrder <= 3; ++stateOrder) {
      for (int parameterOrder = 0; parameterOrder <= 2; ++parameterOrder) {
        if (stateOrder + parameterOrder != total) continue;
        const double direct = stateOrder == 1 && parameterOrder == 0
                                  ? 1.0 : 0.0;
        const double remainder = recurrenceRemainder(
            stateOrder, parameterOrder, coefficient, jets);
        jets[{stateOrder, parameterOrder}] =
            resolvent * (direct + green * remainder);
      }
    }
  }

  const double derivativeBound = 111.0 / 20000.0;
  const double sigma2 = 0.5;
  const double sigma3 = 9.0 / 8.0;
  const double kappa = alphaLower - (1.0 + derivativeBound) * first.order0;
  const double forcing2 = second.order0 *
                          std::pow(1.0 + derivativeBound, 3);
  const double forcing3 =
      (1.0 + derivativeBound) *
          (third.order0 * std::pow(1.0 + derivativeBound, 3)
           + 3.0 * second.order0 * sigma2 *
                 (1.0 + derivativeBound))
      + 3.0 * sigma2 *
          (second.order0 * std::pow(1.0 + derivativeBound, 2)
           + first.order0 * sigma2);
  const double state2Margin = 3.0 * kappa * sigma2 - forcing2;
  const double state3Margin = 4.0 * kappa * sigma3 - forcing3;
  const double origin2Margin =
      3.0 * alphaLower * sigma2 - second.order0;
  const double origin3Margin =
      4.0 * alphaLower * sigma3
      - (third.order0 + 6.0 * second.order0 * sigma2);

  std::cout << std::setprecision(17);
  std::cout << "alpha_lower " << alphaLower << '\n';
  const auto printBounds = [](const std::string& name,
                              const VectorJetBounds& bounds) {
    std::cout << name << " " << bounds.order0 << " " << bounds.order1
              << " " << bounds.order2 << '\n';
  };
  printBounds("B", block);
  printBounds("h", value);
  printBounds("ell", first);
  printBounds("m", second);
  printBounds("t", third);
  for (int p = 0; p <= 3; ++p) {
    std::cout << "L" << p;
    for (int j = 0; j <= 2; ++j) std::cout << " " << coefficient[p][j];
    std::cout << '\n';
  }
  std::cout << "green " << green << '\n';
  std::cout << "contraction " << contraction << '\n';
  std::cout << "resolvent " << resolvent << '\n';
  std::cout << "kappa " << kappa << '\n';
  std::cout << "state_margins " << state2Margin << " " << state3Margin
            << '\n';
  std::cout << "origin_margins " << origin2Margin << " " << origin3Margin
            << '\n';
  for (int i = 0; i <= 3; ++i) {
    std::cout << "Z" << i;
    for (int j = 0; j <= 2; ++j) std::cout << " " << jets.at({i, j});
    std::cout << '\n';
  }
}
