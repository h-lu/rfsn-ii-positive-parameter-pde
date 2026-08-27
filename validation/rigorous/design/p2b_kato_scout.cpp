// Design-only interval scout for the P2bK normalized-Kato interface.
//
// This program is deliberately outside validation/rigorous/src.  Its output
// cannot discharge an obligation.  It selects rational gates before the
// formal Kato configuration and certificate source are frozen.

#include "interval_io.hpp"

#include <algorithm>
#include <array>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <vector>

namespace {

using rfsn::rigorous::Interval;

constexpr int kParameterDimension = 3;

Interval rational(long long numerator, long long denominator) {
  return rfsn::rigorous::exactRational(
      std::to_string(numerator), std::to_string(denominator));
}

Interval normalizedCell(int index, int count) {
  const Interval left = rational(-count + 2 * index, count);
  const Interval right = rational(-count + 2 * (index + 1), count);
  return Interval(left.leftBound(), right.rightBound());
}

Interval absoluteEnvelope(const Interval& value) {
  return Interval(0.0, std::max(std::abs(value.leftBound()),
                                std::abs(value.rightBound())));
}

Interval hull(const Interval& left, const Interval& right) {
  return Interval(std::min(left.leftBound(), right.leftBound()),
                  std::max(left.rightBound(), right.rightBound()));
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
      result.hessian[i][j] =
          left.hessian[i][j] + right.hessian[i][j];
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
    throw std::logic_error("nonpositive square-root argument");
  const Interval root = sqrt(argument.value);
  return compose(argument, root,
                 Interval(1.0) / (Interval(2.0) * root),
                 -Interval(1.0) /
                     (Interval(4.0) * argument.value * root));
}

Jet2 reciprocal(const Jet2& argument) {
  if (argument.value.leftBound() <= 0.0 &&
      argument.value.rightBound() >= 0.0)
    throw std::logic_error("reciprocal argument contains zero");
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
  const Interval first = Interval(1.0) / denominator;
  const Interval second =
      -Interval(2.0) * argument.value / (denominator * denominator);
  return compose(argument, atan(argument.value), first, second);
}

struct Bounds {
  Interval order0{0.0};
  Interval order1{0.0};
  Interval order2{0.0};
};

Bounds jetBounds(const std::vector<Jet2>& entries) {
  Interval valueSum(0.0);
  Interval gradientSum(0.0);
  Interval hessianSum(0.0);
  for (const auto& entry : entries) {
    valueSum += sqr(absoluteEnvelope(entry.value));
    for (int i = 0; i < kParameterDimension; ++i) {
      gradientSum += sqr(absoluteEnvelope(entry.gradient[i]));
      for (int j = 0; j < kParameterDimension; ++j)
        hessianSum += sqr(absoluteEnvelope(entry.hessian[i][j]));
    }
  }
  return {sqrt(valueSum), sqrt(gradientSum), sqrt(hessianSum)};
}

void maximize(Bounds& target, const Bounds& candidate) {
  target.order0 = Interval(
      0.0, std::max(target.order0.rightBound(),
                    candidate.order0.rightBound()));
  target.order1 = Interval(
      0.0, std::max(target.order1.rightBound(),
                    candidate.order1.rightBound()));
  target.order2 = Interval(
      0.0, std::max(target.order2.rightBound(),
                    candidate.order2.rightBound()));
}

}  // namespace

int main() {
  const std::array<int, 3> subdivisions{16, 8, 4};
  bool initialized = false;
  Interval cHull(0.0);
  Interval yHull(0.0);
  Interval chiHull(0.0);
  Interval sigmaHull(0.0);
  Interval determinantHull(0.0);
  Interval inverseHull(0.0);
  Interval tauHull(0.0);
  Bounds chiBounds;
  Bounds changeBounds;
  Bounds frameBounds;

  for (int ir = 0; ir < subdivisions[0]; ++ir) {
    for (int ia = 0; ia < subdivisions[1]; ++ia) {
      for (int ie = 0; ie < subdivisions[2]; ++ie) {
        const Jet2 thetaR = Jet2::variable(
            normalizedCell(ir, subdivisions[0]), 0);
        const Jet2 thetaA = Jet2::variable(
            normalizedCell(ia, subdivisions[1]), 1);
        const Jet2 thetaEpsilon = Jet2::variable(
            normalizedCell(ie, subdivisions[2]), 2);
        const Jet2 r = (thetaR + Jet2(Interval(1.0))) /
                       Jet2(Interval(25.0));
        const Jet2 a2 = thetaA / Jet2(Interval(4.0));
        const Jet2 epsilon = Jet2(Interval(1.0))
                             + thetaEpsilon / Jet2(Interval(5.0));
        const Jet2 rootEpsilon = squareRoot(epsilon);
        const Jet2 r2 = r * r;
        const Jet2 r4 = r2 * r2;
        const Jet2 c = Interval(2.0) * r * a2
                       + rootEpsilon * r4 * a2 * a2;
        const Jet2 alpha = Interval(0.5) *
                           squareRoot(Jet2(Interval(2.0)) + c);
        const Jet2 beta = Interval(0.5) *
                          squareRoot(Jet2(Interval(2.0)) - c);
        const Jet2 rootTwo = squareRoot(Jet2(Interval(2.0)));
        const Jet2 stableY = -c /
            (squareRoot(Jet2(Interval(2.0)) - c)
             * (rootTwo + squareRoot(Jet2(Interval(2.0)) + c)));
        const Jet2 chi = arctangent(stableY);
        const Jet2 nSquared = Interval(6.0) * alpha * alpha
                              - Interval(4.0) * rootTwo * alpha
                              + Jet2(Interval(3.0));
        const Jet2 n = squareRoot(nSquared);
        const Jet2 one(Interval(1.0));
        const Jet2 zero(Interval(0.0));
        const Jet2 conformalScale =
            squareRoot(one + stableY * stableY) / n;
        const Jet2 determinant = conformalScale * conformalScale;
        const Jet2 inverseNorm = reciprocal(conformalScale);
        const Jet2 tau = Jet2(Interval(0.25)) * compose(
            (Jet2(Interval(2.0)) + c) / Jet2(Interval(2.0)),
            log(((Interval(2.0) + c.value) / Interval(2.0))),
            Interval(2.0) / (Interval(2.0) + c.value),
            -Interval(4.0) /
                ((Interval(2.0) + c.value) *
                 (Interval(2.0) + c.value)));

        const std::array<std::array<Jet2, 2>, 2> change{{
            {{one / n, -stableY / n}},
            {{stableY / n, one / n}},
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
            katoFrame[row][column] = zero;
            for (int inner = 0; inner < 2; ++inner)
              katoFrame[row][column] = katoFrame[row][column]
                  + algebraicFrame[row][inner] * change[inner][column];
          }
        }

        std::vector<Jet2> changeEntries;
        std::vector<Jet2> frameEntries;
        for (const auto& row : change)
          for (const auto& entry : row) changeEntries.push_back(entry);
        for (const auto& row : katoFrame)
          for (const auto& entry : row) frameEntries.push_back(entry);
        maximize(chiBounds, jetBounds({chi}));
        maximize(changeBounds, jetBounds(changeEntries));
        maximize(frameBounds, jetBounds(frameEntries));

        if (!initialized) {
          cHull = c.value;
          yHull = stableY.value;
          chiHull = chi.value;
          sigmaHull = conformalScale.value;
          determinantHull = determinant.value;
          inverseHull = inverseNorm.value;
          tauHull = tau.value;
          initialized = true;
        } else {
          cHull = hull(cHull, c.value);
          yHull = hull(yHull, stableY.value);
          chiHull = hull(chiHull, chi.value);
          sigmaHull = hull(sigmaHull, conformalScale.value);
          determinantHull = hull(determinantHull, determinant.value);
          inverseHull = hull(inverseHull, inverseNorm.value);
          tauHull = hull(tauHull, tau.value);
        }
      }
    }
  }

  const double radius = 1.0 / 100.0;
  const double sourceFirst = radius * chiBounds.order1.rightBound();
  const double sourceSecond = radius *
      (chiBounds.order2.rightBound()
       + chiBounds.order1.rightBound() * chiBounds.order1.rightBound());
  std::cout << std::setprecision(17);
  const auto printInterval = [](const char* name, const Interval& value) {
    std::cout << name << " " << value.leftBound() << " "
              << value.rightBound() << '\n';
  };
  const auto printBounds = [](const char* name, const Bounds& value) {
    std::cout << name << " " << value.order0.rightBound() << " "
              << value.order1.rightBound() << " "
              << value.order2.rightBound() << '\n';
  };
  printInterval("c", cHull);
  printInterval("y", yHull);
  printInterval("chi", chiHull);
  printInterval("sigma", sigmaHull);
  printInterval("det", determinantHull);
  printInterval("inverse", inverseHull);
  printInterval("tau", tauHull);
  printBounds("chi_abs_d1_d2", chiBounds);
  printBounds("C_frobenius_d1_d2", changeBounds);
  printBounds("K_frobenius_d1_d2", frameBounds);
  std::cout << "source_circle_dtheta " << sourceFirst << " "
            << sourceSecond << '\n';
}
