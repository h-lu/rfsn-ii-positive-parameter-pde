#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>

#include "capd/capdlib.h"
#include "fold_centres_generated.hpp"
#include "tail_graph_generated.hpp"
#include "weighted_tail_generated.hpp"

using namespace capd;

namespace papera_mixed_fold_autodiff {

struct Jet4 {
  interval value;
  std::array<interval, 4> gradient;
  std::array<std::array<interval, 4>, 4> hessian;

  Jet4() : value(0.) { clear(); }
  Jet4(int value) : value(value) { clear(); }
  Jet4(long value) : value(static_cast<double>(value)) { clear(); }
  Jet4(long long value) : value(static_cast<double>(value)) { clear(); }
  Jet4(double value) : value(value) { clear(); }
  Jet4(const interval& value) : value(value) { clear(); }

  void clear() {
    gradient.fill(interval(0.));
    for(auto& row : hessian) row.fill(interval(0.));
  }

  static Jet4 variable(const interval& value, int index) {
    Jet4 result(value);
    result.gradient[index] = 1.;
    return result;
  }

  Jet4& operator+=(const Jet4& other) {
    value += other.value;
    for(int i = 0; i < 4; ++i) {
      gradient[i] += other.gradient[i];
      for(int j = 0; j < 4; ++j)
        hessian[i][j] += other.hessian[i][j];
    }
    return *this;
  }

  Jet4& operator-=(const Jet4& other) {
    value -= other.value;
    for(int i = 0; i < 4; ++i) {
      gradient[i] -= other.gradient[i];
      for(int j = 0; j < 4; ++j)
        hessian[i][j] -= other.hessian[i][j];
    }
    return *this;
  }
};

Jet4 operator+(Jet4 left, const Jet4& right) { return left += right; }
Jet4 operator-(Jet4 left, const Jet4& right) { return left -= right; }

Jet4 operator-(const Jet4& value) {
  Jet4 result;
  result.value = -value.value;
  for(int i = 0; i < 4; ++i) {
    result.gradient[i] = -value.gradient[i];
    for(int j = 0; j < 4; ++j)
      result.hessian[i][j] = -value.hessian[i][j];
  }
  return result;
}

Jet4 operator*(const Jet4& left, const Jet4& right) {
  Jet4 result;
  result.value = left.value * right.value;
  for(int i = 0; i < 4; ++i) {
    result.gradient[i] = left.gradient[i] * right.value
      + left.value * right.gradient[i];
    for(int j = 0; j < 4; ++j)
      result.hessian[i][j] = left.hessian[i][j] * right.value
        + left.gradient[i] * right.gradient[j]
        + left.gradient[j] * right.gradient[i]
        + left.value * right.hessian[i][j];
  }
  return result;
}

Jet4 reciprocal(const Jet4& value) {
  Jet4 result;
  const interval inverse = interval(1.) / value.value;
  const interval first = -sqr(inverse);
  const interval second = interval(2.) * inverse * inverse * inverse;
  result.value = inverse;
  for(int i = 0; i < 4; ++i) {
    result.gradient[i] = first * value.gradient[i];
    for(int j = 0; j < 4; ++j)
      result.hessian[i][j] = second * value.gradient[i]
        * value.gradient[j] + first * value.hessian[i][j];
  }
  return result;
}

Jet4 operator/(const Jet4& left, const Jet4& right) {
  return left * reciprocal(right);
}

Jet4 sqrt(const Jet4& value) {
  using std::sqrt;
  Jet4 result;
  const interval root = sqrt(value.value);
  const interval first = interval(1.) / (interval(2.) * root);
  const interval second = -interval(1.)
    / (interval(4.) * value.value * root);
  result.value = root;
  for(int i = 0; i < 4; ++i) {
    result.gradient[i] = first * value.gradient[i];
    for(int j = 0; j < 4; ++j)
      result.hessian[i][j] = second * value.gradient[i]
        * value.gradient[j] + first * value.hessian[i][j];
  }
  return result;
}

} // namespace papera_mixed_fold_autodiff

namespace {

using papera_mixed_fold_autodiff::Jet4;

constexpr int kSegments = 30;
constexpr int kBaseDimension = 4;
constexpr int kExtendedDimension = 8;
constexpr int kUnknowns = kExtendedDimension * (kSegments + 1);
constexpr int kSwitchNode = 4;
constexpr int kTransitionSegment = kSwitchNode - 1;
constexpr double kStep = .5;
constexpr double kSlopeBound = 1e-5;
constexpr double kHessianBound = 1e-3;

double gCapHalfWidth = 1.5e-6;
double gRadiusScale = 1.;
bool gContainmentOnly = false;
std::string gFamilySeedFile;
std::int64_t gFamilySeedOffset = 0;
double gFamilyHalfWidth = 0.;
double gFamilyRadiusScale = 1.;

// Floating second derivatives of the centre branch are used only to size the
// declared augmented uniqueness box.  The interval inclusion, not this table,
// proves existence and uniqueness.
constexpr double kCurvature[kSegments + 1][kBaseDimension] = {
  {0., 0., -113.59519100189209, 1.7838973193394e-18},
  {13.8991975, 55.3929213, -113.304994, 2.31990182},
  {54.9604256, 108.163175, -108.972611, 18.4342661},
  {121.07716, 155.007166, -90.3762185, 61.4664342},
  {14706.7025, -7894.33327, 3353.6704, 25443.8025},
  {5938.27526, -2999.04253, 1016.06087, 6534.01315},
  {2987.6077, -1525.38637, 362.342257, 2305.66985},
  {1695.51277, -894.110154, 135.814466, 952.881885},
  {1042.40841, -567.751446, 50.8774949, 434.746449},
  {680.402994, -379.861985, 18.5156335, 214.096524},
  {465.832971, -264.297459, 6.41753788, 112.84035},
  {331.710138, -189.94686, 2.07694948, 63.3441858},
  {244.074995, -140.422904, .605618767, 37.6563024},
  {184.607361, -106.437403, .141494841, 23.5298853},
  {142.918496, -82.473997, .00899885129, 15.3323583},
  {112.861027, -65.1503912, -.0221204535, 10.3450249},
  {90.6574596, -52.3392051, -.0250664921, 7.18667559},
  {73.9065514, -42.6700508, -.0214344591, 5.11820316},
  {61.0347892, -35.2389315, -.0170640045, 3.72438525},
  {50.9826994, -29.4353546, -.0133100938, 2.7618547},
  {43.0194885, -24.8377087, -.010344318, 2.0826955},
  {36.6301266, -21.1487207, -.00805368119, 1.59426263},
  {31.4446111, -18.1547884, -.00630557335, 1.236926},
  {27.1925133, -15.6997811, -.00496633599, .971455636},
  {23.6730895, -13.6677973, -.0039364191, .771456604},
  {20.735215, -11.9715825, -.00314186948, .618855215},
  {18.263654, -10.5446018, -.00252526395, .501056913},
  {16.1695035, -9.33552556, -.00204416731, .409153699},
  {14.383436, -8.30432545, -.00166311409, .336741623},
  {12.8508523, -7.41947761, -.00136286044, .279170761},
  {11.5283588, -6.65592784, -.00112447089, .233005776}
};

double absUpper(const interval& value) {
  return std::max(std::abs(value.leftBound()),
                  std::abs(value.rightBound()));
}

int column(int nodeIndex, int component) {
  return kExtendedDimension * nodeIndex + component;
}

IVector node(const IVector& all, int nodeIndex) {
  IVector result(kExtendedDimension);
  for(int component = 0; component < kExtendedDimension; ++component)
    result[component] = all[column(nodeIndex, component)];
  return result;
}

std::array<double, kExtendedDimension> mixedCentreAt(int nodeIndex) {
  const double* raw = papera_fold_centres::kCentres[nodeIndex];
  if(nodeIndex < kSwitchNode)
    return {raw[0], raw[1], raw[2], raw[3],
            raw[4], raw[5], raw[6], raw[7]};
  const double U = raw[0], P = raw[1], V = raw[2], Q = raw[3];
  const double wU = raw[4], wP = raw[5], wV = raw[6], wQ = raw[7];
  const double e = -1. / U;
  const double rootE = std::sqrt(e);
  const double e32 = e * rootE;
  const double we = wU / (U * U);
  return {
    e,
    P * e32,
    Q * e32 + 2. / std::sqrt(3.),
    1. + V * e * e,
    we,
    wP * e32 + 1.5 * P * rootE * we,
    wQ * e32 + 1.5 * Q * rootE * we,
    wV * e * e + 2. * V * e * we
  };
}

IVector centreVector() {
  IVector result(kUnknowns);
  for(int n = 0; n <= kSegments; ++n) {
    const auto centre = mixedCentreAt(n);
    for(int component = 0; component < kExtendedDimension; ++component)
      result[column(n, component)] = centre[component];
  }
  return result;
}

double radiusAt(const IVector& centre, int nodeIndex, int component) {
  const double value = centre[column(nodeIndex, component)].mid().leftBound();
  if(component < kBaseDimension) {
    double floor = nodeIndex < kSwitchNode ? 4e-8 : 4e-9;
    // The legacy robust fold image has an 8e-9-wide terminal d enclosure.
    // Keep a strict full-state identification margin in that coordinate.
    if(nodeIndex == kSegments && component == 2) floor = 1.5e-8;
    const double tangent = centre[column(nodeIndex, component + 4)]
      .mid().leftBound();
    return gRadiusScale * (floor + 1.4 * gCapHalfWidth
      * std::abs(tangent));
  }
  const int tangentComponent = component - kBaseDimension;
  const double relative = nodeIndex == 0
    ? 5.1e-3
    : (nodeIndex >= kSwitchNode && tangentComponent == 2
       ? 2.5e-2 : 5e-3);
  return gRadiusScale * (
    relative * (1. + std::abs(value))
    + 2.5 * gCapHalfWidth
      * std::abs(kCurvature[nodeIndex][tangentComponent])
  );
}

IVector boxAround(const IVector& centre) {
  IVector result(kUnknowns);
  for(int i = 0; i < kUnknowns; ++i) {
    const double value = centre[i].mid().leftBound();
    const double radius = radiusAt(
      centre, i / kExtendedDimension, i % kExtendedDimension);
    result[i] = interval(value - radius, value + radius);
  }
  return result;
}

struct FamilySeed {
  double sourceU = 0.;
  double sourceV = 0.;
  std::array<std::array<double, kBaseDimension>, kSegments + 1> centre{};
  std::array<std::array<double, kBaseDimension>, kSegments + 1> tangent{};
  std::array<std::array<double, kBaseDimension>, kSegments + 1> curvature{};
};

FamilySeed loadFamilySeed(const std::string& path, std::int64_t offset) {
  std::ifstream input(path);
  if(!input) throw std::runtime_error("cannot open family seed file");
  input.seekg(offset);
  if(!input) throw std::runtime_error("cannot seek family seed file");
  FamilySeed result;
  input >> result.sourceU >> result.sourceV;
  for(int n = 0; n <= kSegments; ++n)
    for(int component = 0; component < kBaseDimension; ++component)
      input >> result.centre[n][component];
  for(int n = 0; n <= kSegments; ++n)
    for(int component = 0; component < kBaseDimension; ++component)
      input >> result.tangent[n][component];
  for(int n = 0; n <= kSegments; ++n)
    for(int component = 0; component < kBaseDimension; ++component)
      input >> result.curvature[n][component];
  if(!input) throw std::runtime_error("malformed family seed file");
  return result;
}

IVector familyAugmentedBox(const FamilySeed& seed, double halfWidth,
                           double radiusScale = 1.) {
  IVector result(kUnknowns);
  for(int n = 0; n <= kSegments; ++n)
    for(int component = 0; component < kBaseDimension; ++component) {
      const double baseFloor = n < kSwitchNode ? 3e-8 : 3e-9;
      double scaledFloor = radiusScale * baseFloor;
      if(n == kSwitchNode) scaledFloor = baseFloor;
      const double baseRadius = scaledFloor + radiusScale * 1.35 * halfWidth
        * std::abs(seed.tangent[n][component]);
      result[column(n, component)] = interval(
        seed.centre[n][component] - baseRadius,
        seed.centre[n][component] + baseRadius);
      const double relative = n == 0 ? 5e-3
        : (n >= kSwitchNode && component == 2 ? 2e-2 : 5e-3);
      const double tangentRadius = relative
        * (1. + std::abs(seed.tangent[n][component]))
        + 1.5 * halfWidth * std::abs(seed.curvature[n][component]);
      result[column(n, 4 + component)] = interval(
        seed.tangent[n][component] - tangentRadius,
        seed.tangent[n][component] + tangentRadius);
    }
  return result;
}

struct TargetCoordinates {
  Jet4 residual;
  std::array<Jet4, 3> base;
};

TargetCoordinates targetCoordinates(const IVector& compact) {
  const Jet4 e = Jet4::variable(compact[0], 0);
  const Jet4 p = Jet4::variable(compact[1], 1);
  const Jet4 d = Jet4::variable(compact[2], 2);
  const Jet4 omega = Jet4::variable(compact[3], 3);
  return {p - papera_tail::h7(e, d, omega), {e, d, omega}};
}

interval eighthPower(const interval& value) {
  const interval square = value * value;
  const interval fourth = square * square;
  return fourth * fourth;
}

struct RobustTargetData {
  interval residual;
  interval tangentResidual;
  IVector gradient;
  IVector tangentStateDerivative;
  double valueBound = 0.;
};

RobustTargetData robustTarget(const IVector& point, const IVector& box) {
  const TargetCoordinates pointData = targetCoordinates(point);
  const TargetCoordinates boxData = targetCoordinates(box);
  const double valueBound = 2. * absUpper(eighthPower(box[0]));
  const interval slope(-kSlopeBound, kSlopeBound);
  const interval curvature(-kHessianBound, kHessianBound);

  IVector gradient(kBaseDimension), pointGradient(kBaseDimension);
  for(int i = 0; i < kBaseDimension; ++i) {
    gradient[i] = boxData.residual.gradient[i];
    pointGradient[i] = pointData.residual.gradient[i];
    for(int base = 0; base < 3; ++base) {
      gradient[i] -= slope * boxData.base[base].gradient[i];
      pointGradient[i] -= slope * pointData.base[base].gradient[i];
    }
  }

  interval tangentResidual = 0.;
  for(int i = 0; i < kBaseDimension; ++i)
    tangentResidual += pointGradient[i] * point[4 + i];

  IVector tangentStateDerivative(kBaseDimension);
  for(int i = 0; i < kBaseDimension; ++i) {
    interval derivative = 0.;
    for(int j = 0; j < kBaseDimension; ++j)
      derivative += boxData.residual.hessian[i][j] * box[4 + j];
    for(int base = 0; base < 3; ++base) {
      interval baseTangent = 0.;
      for(int j = 0; j < kBaseDimension; ++j)
        baseTangent += boxData.base[base].gradient[j] * box[4 + j];
      for(int otherBase = 0; otherBase < 3; ++otherBase)
        derivative -= curvature
          * boxData.base[otherBase].gradient[i] * baseTangent;
      interval secondCoordinate = 0.;
      for(int j = 0; j < kBaseDimension; ++j)
        secondCoordinate += boxData.base[base].hessian[i][j]
          * box[4 + j];
      derivative -= slope * secondCoordinate;
    }
    tangentStateDerivative[i] = derivative;
  }
  return {
    pointData.residual.value + interval(-valueBound, valueBound),
    tangentResidual,
    gradient,
    tangentStateDerivative,
    valueBound
  };
}

TargetCoordinates oldRawTargetCoordinates(const IVector& raw) {
  using papera_mixed_fold_autodiff::sqrt;
  const Jet4 U = Jet4::variable(raw[0], 0);
  const Jet4 P = Jet4::variable(raw[1], 1);
  const Jet4 V = Jet4::variable(raw[2], 2);
  const Jet4 Q = Jet4::variable(raw[3], 3);
  const Jet4 e = -Jet4(1) / U;
  const Jet4 e32 = e * sqrt(e);
  const Jet4 p = P * e32;
  const Jet4 d = Q * e32 + Jet4(2) / sqrt(Jet4(3));
  const Jet4 omega = Jet4(1) + V * e * e;
  const Jet4 c = d - sqrt(Jet4(3)) * omega / Jet4(2);
  return {p - papera_tail::h7(e, d, omega), {e, c, omega}};
}

RobustTargetData oldRobustTarget(const IVector& point,
                                 const IVector& box) {
  const TargetCoordinates pointData = oldRawTargetCoordinates(point);
  const TargetCoordinates boxData = oldRawTargetCoordinates(box);
  const interval valueError(-1e-8, 1e-8);
  const interval slope(-1e-5, 1e-5);
  const interval curvature(-1e-3, 1e-3);
  IVector gradient(kBaseDimension), pointGradient(kBaseDimension);
  for(int i = 0; i < kBaseDimension; ++i) {
    gradient[i] = boxData.residual.gradient[i];
    pointGradient[i] = pointData.residual.gradient[i];
    for(int base = 0; base < 3; ++base) {
      gradient[i] -= slope * boxData.base[base].gradient[i];
      pointGradient[i] -= slope * pointData.base[base].gradient[i];
    }
  }
  interval tangentResidual = 0.;
  for(int i = 0; i < kBaseDimension; ++i)
    tangentResidual += pointGradient[i] * point[4 + i];
  IVector tangentStateDerivative(kBaseDimension);
  for(int i = 0; i < kBaseDimension; ++i) {
    interval derivative = 0.;
    for(int j = 0; j < kBaseDimension; ++j)
      derivative += boxData.residual.hessian[i][j] * box[4 + j];
    for(int base = 0; base < 3; ++base) {
      interval baseTangent = 0.;
      for(int j = 0; j < kBaseDimension; ++j)
        baseTangent += boxData.base[base].gradient[j] * box[4 + j];
      for(int otherBase = 0; otherBase < 3; ++otherBase)
        derivative -= curvature
          * boxData.base[otherBase].gradient[i] * baseTangent;
      interval secondCoordinate = 0.;
      for(int j = 0; j < kBaseDimension; ++j)
        secondCoordinate += boxData.base[base].hessian[i][j]
          * box[4 + j];
      derivative -= slope * secondCoordinate;
    }
    tangentStateDerivative[i] = derivative;
  }
  return {
    pointData.residual.value + valueError,
    tangentResidual,
    gradient,
    tangentStateDerivative,
    1e-8
  };
}

double oldFoldRadius(int nodeIndex, int component) {
  const double x = static_cast<double>(nodeIndex) / kSegments;
  switch(component) {
    case 0: return 2.5e-8 + 6e-7 * std::pow(x, 2);
    case 1: return 1e-7 + 1.25e-6 * std::pow(x, 20);
    case 2: return 1e-7 + 7.5e-6 * std::pow(x, 4);
    case 3: return 1e-7 + 2.5e-6 * std::pow(x, 3);
    case 4: return 5e-5 + 4e-2 * std::pow(x, 24);
    case 5: return 2e-4 + 1.6e-1 * std::pow(x, 40);
    case 6: return 2e-4 + 2.5e-2 * std::pow(x, 7);
    case 7: return 2e-5 + 1.5e-2 * std::pow(x, 5);
  }
  throw std::runtime_error("invalid old-fold component");
}

struct OldFoldProof {
  IVector box;
  IVector krawczyk;
  double ratio = 0.;
  double contractionRatio = 0.;
};

OldFoldProof certifyExistingFold() {
  IVector centre(kUnknowns), X(kUnknowns);
  for(int n = 0; n <= kSegments; ++n)
    for(int component = 0; component < kExtendedDimension; ++component) {
      const int i = column(n, component);
      const double value = papera_fold_centres::kCentres[n][component];
      centre[i] = value;
      const double radius = oldFoldRadius(n, component);
      X[i] = interval(value - radius, value + radius);
    }

  IMap field(
    "var:U,P,V,Q,a,b,c,h;"
    "fun:P,-U*U-V,Q,U,b,-2*U*a-c,h,a;"
  );
  IOdeSolver solver(field, 25);
  solver.setAbsoluteTolerance(1e-14);
  solver.setRelativeTolerance(1e-14);
  IVector residual(kUnknowns);
  IMatrix derivative(kUnknowns, kUnknowns);
  derivative.clear();
  for(int segment = 0; segment < kSegments; ++segment) {
    const IVector initialCentre = node(centre, segment);
    const IVector initialBox = node(X, segment);
    ITimeMap c0TimeMap(solver);
    C0HOTripletonSet c0Set(initialCentre);
    const IVector imageCentre = c0TimeMap(interval(kStep), c0Set);
    ITimeMap c1TimeMap(solver);
    C1HORect2Set c1Set(initialBox);
    c1TimeMap(interval(kStep), c1Set);
    const IMatrix monodromy = (IMatrix)c1Set;
    const IVector nextCentre = node(centre, segment + 1);
    for(int output = 0; output < kExtendedDimension; ++output) {
      const int row = kExtendedDimension * segment + output;
      residual[row] = nextCentre[output] - imageCentre[output];
      for(int input = 0; input < kExtendedDimension; ++input)
        derivative[row][column(segment, input)]
          = -monodromy[output][input];
      derivative[row][column(segment + 1, output)] += 1.;
    }
  }

  int row = kExtendedDimension * kSegments;
  const IVector sourceCentre = node(centre, 0);
  const IVector sourceBox = node(X, 0);
  const IVector terminalCentre = node(centre, kSegments);
  const IVector terminalBox = node(X, kSegments);
  residual[row] = sourceCentre[1];
  derivative[row++][column(0, 1)] = 1.;
  residual[row] = sourceCentre[3];
  derivative[row++][column(0, 3)] = 1.;
  residual[row] = sourceCentre[4] - 1.;
  derivative[row++][column(0, 4)] = 1.;
  residual[row] = sourceCentre[5];
  derivative[row++][column(0, 5)] = 1.;
  residual[row] = sourceCentre[7];
  derivative[row++][column(0, 7)] = 1.;
  const RobustTargetData target = oldRobustTarget(
    terminalCentre, terminalBox);
  residual[row] = target.residual;
  for(int i = 0; i < kBaseDimension; ++i)
    derivative[row][column(kSegments, i)] = target.gradient[i];
  ++row;
  residual[row] = target.tangentResidual;
  for(int i = 0; i < kBaseDimension; ++i) {
    derivative[row][column(kSegments, i)]
      = target.tangentStateDerivative[i];
    derivative[row][column(kSegments, 4 + i)] = target.gradient[i];
  }
  ++row;
  const interval U0 = sourceCentre[0], V0 = sourceCentre[2];
  const interval wU0 = sourceCentre[4], wV0 = sourceCentre[6];
  residual[row] = (-interval(2.) * sqr(U0) - interval(2.) * V0)
    * wU0 - interval(2.) * U0 * wV0;
  const interval U = sourceBox[0], V = sourceBox[2];
  const interval wU = sourceBox[4], wV = sourceBox[6];
  derivative[row][column(0, 0)] = -interval(4.) * U * wU
    - interval(2.) * wV;
  derivative[row][column(0, 2)] = -interval(2.) * wU;
  derivative[row][column(0, 4)] = -interval(2.) * sqr(U)
    - interval(2.) * V;
  derivative[row][column(0, 6)] = -interval(2.) * U;
  ++row;
  if(row != kUnknowns)
    throw std::runtime_error("old-fold row count mismatch");

  DMatrix midpoint(kUnknowns, kUnknowns);
  for(int i = 0; i < kUnknowns; ++i)
    for(int j = 0; j < kUnknowns; ++j)
      midpoint[i][j] = derivative[i][j].mid().leftBound();
  const DMatrix inverse = matrixAlgorithms::inverseMatrix(midpoint);
  IMatrix preconditioner(kUnknowns, kUnknowns);
  for(int i = 0; i < kUnknowns; ++i)
    for(int j = 0; j < kUnknowns; ++j)
      preconditioner[i][j] = inverse[i][j];
  const IMatrix remainder = IMatrix::Identity(kUnknowns)
    - preconditioner * derivative;
  const IVector contractionImage = remainder * (X - centre);
  const IVector krawczyk = centre - preconditioner * residual
    + contractionImage;
  double ratio = 0., contractionRatio = 0.;
  for(int i = 0; i < kUnknowns; ++i) {
    const double centreValue = centre[i].mid().leftBound();
    const double correction = std::max(
      std::abs(krawczyk[i].leftBound() - centreValue),
      std::abs(krawczyk[i].rightBound() - centreValue));
    ratio = std::max(ratio, correction /
      oldFoldRadius(i / kExtendedDimension, i % kExtendedDimension));
    contractionRatio = std::max(contractionRatio,
      absUpper(contractionImage[i]) /
      oldFoldRadius(i / kExtendedDimension, i % kExtendedDimension));
  }
  if(!subsetInterior(krawczyk, X))
    throw std::runtime_error("existing robust fold replay failed");
  return {X, krawczyk, ratio, contractionRatio};
}

IVector rawExtendedToMixed(const IVector& raw, int nodeIndex) {
  if(nodeIndex < kSwitchNode) return raw;
  using std::sqrt;
  const interval e = -interval(1.) / raw[0];
  const interval rootE = sqrt(e);
  const interval e32 = e * rootE;
  const interval we = raw[4] / sqr(raw[0]);
  IVector result(kExtendedDimension);
  result[0] = e;
  result[1] = raw[1] * e32;
  result[2] = raw[3] * e32 + interval(2.) / sqrt(interval(3.));
  result[3] = interval(1.) + raw[2] * sqr(e);
  result[4] = we;
  result[5] = raw[5] * e32
    + interval(1.5) * raw[1] * rootE * we;
  result[6] = raw[7] * e32
    + interval(1.5) * raw[3] * rootE * we;
  result[7] = raw[6] * sqr(e)
    + interval(2.) * raw[2] * e * we;
  return result;
}

void parseArguments(int argc, char** argv) {
  for(int i = 1; i < argc; ++i) {
    const std::string argument(argv[i]);
    if(argument == "--cap-half-width" && i + 1 < argc)
      gCapHalfWidth = std::stod(argv[++i]);
    else if(argument == "--radius-scale" && i + 1 < argc)
      gRadiusScale = std::stod(argv[++i]);
    else if(argument == "--containment-only")
      gContainmentOnly = true;
    else if(argument == "--family-seed-file" && i + 1 < argc)
      gFamilySeedFile = argv[++i];
    else if(argument == "--family-seed-offset" && i + 1 < argc)
      gFamilySeedOffset = std::stoll(argv[++i]);
    else if(argument == "--family-half-width" && i + 1 < argc)
      gFamilyHalfWidth = std::stod(argv[++i]);
    else if(argument == "--family-radius-scale" && i + 1 < argc)
      gFamilyRadiusScale = std::stod(argv[++i]);
    else
      throw std::runtime_error("invalid command-line argument");
  }
  if(!(gCapHalfWidth > 0.) || !(gRadiusScale > 0.))
    throw std::runtime_error("cap width and radius scale must be positive");
  if(gContainmentOnly && (gFamilySeedFile.empty()
       || gFamilySeedOffset < 0 || !(gFamilyHalfWidth > 0.)))
    throw std::runtime_error("incomplete family containment arguments");
  if(!gFamilySeedFile.empty()
     && (gFamilySeedOffset < 0 || !(gFamilyHalfWidth > 0.)
         || !(gFamilyRadiusScale > 0.)))
    throw std::runtime_error("incomplete optional family arguments");
}

struct PhysicalContract {
  interval e, a, b, graphEnergy;
};

PhysicalContract physicalContract(const IVector& compact) {
  const interval e = compact[0];
  const interval d = compact[2];
  const interval omega = compact[3];
  const interval a = d / (e * e * e);
  const interval b = (omega - e * e / interval(6.))
    / (e * e * e * e);
  const interval graphEnergy = papera_weighted_tail::energy(
    e, a, b, interval(-2., 2.));
  if(!(e.leftBound() > 0. && e.rightBound() < .06
       && a.leftBound() > -.0065 && a.rightBound() < .0065
       && b.leftBound() > -.01 && b.rightBound() < .01
       && graphEnergy.leftBound() > -.012
       && graphEnergy.rightBound() < .012))
    throw std::runtime_error("fold cap terminal box leaves physical corridor");
  return {e, a, b, graphEnergy};
}

} // namespace

int main(int argc, char** argv) {
  try {
    parseArguments(argc, argv);
    const IVector centre = centreVector();
    const IVector X = boxAround(centre);
    if(gContainmentOnly) {
      const FamilySeed seed = loadFamilySeed(
        gFamilySeedFile, gFamilySeedOffset);
      const IVector family = familyAugmentedBox(
        seed, gFamilyHalfWidth, gFamilyRadiusScale);
      if(!subsetInterior(family, X)) {
        double worstMargin = std::numeric_limits<double>::infinity();
        int worst = -1;
        for(int i = 0; i < kUnknowns; ++i) {
          const double margin = std::min(
            family[i].leftBound() - X[i].leftBound(),
            X[i].rightBound() - family[i].rightBound());
          if(margin < worstMargin) {
            worstMargin = margin;
            worst = i;
          }
        }
        std::cerr << std::setprecision(17)
          << "family cap containment failure margin=" << worstMargin
          << " node=" << worst / kExtendedDimension
          << " component=" << worst % kExtendedDimension
          << " family=" << family[worst] << " cap=" << X[worst] << "\n";
        throw std::runtime_error(
          "family augmented uniqueness box leaves fold cap");
      }
      double margin = std::numeric_limits<double>::infinity();
      for(int i = 0; i < kUnknowns; ++i)
        margin = std::min({
          margin,
          family[i].leftBound() - X[i].leftBound(),
          X[i].rightBound() - family[i].rightBound()
        });
      std::cout << std::setprecision(17)
        << "{\n"
        << "  \"status\": \"PASS-FAMILY-FULL-STATE-IN-FOLD-CAP\",\n"
        << "  \"unknowns\": " << kUnknowns << ",\n"
        << "  \"source_parameter\": \"["
          << seed.sourceU - gFamilyHalfWidth << ", "
          << seed.sourceU + gFamilyHalfWidth << "]\",\n"
        << "  \"minimum_full_state_margin\": " << margin << "\n"
        << "}\n";
      return 0;
    }
    const PhysicalContract physical = physicalContract(node(X, kSegments));

    IMap rawField(
      "var:U,P,V,Q,a,b,c,h;"
      "fun:P,-U*U-V,Q,U,b,-2*U*a-c,h,a;"
    );
    IMap compactField(
      "var:e,p,d,o,a,b,c,h;"
      "fun:"
      "p*sqrt(e),"
      "(1.5*p*p-o)/sqrt(e),"
      "(1.5*p*(d-2/sqrt(3))-e)/sqrt(e),"
      "(e*(d-2/sqrt(3))+2*p*(o-1))/sqrt(e),"
      "p/(2*sqrt(e))*a+sqrt(e)*b,"
      "-(1.5*p*p-o)/(2*e*sqrt(e))*a+3*p/sqrt(e)*b-h/sqrt(e),"
      "(-1/sqrt(e)-(1.5*p*(d-2/sqrt(3))-e)/(2*e*sqrt(e)))*a"
        "+1.5*(d-2/sqrt(3))/sqrt(e)*b+1.5*p/sqrt(e)*c,"
      "((d-2/sqrt(3))/sqrt(e)"
        "-(e*(d-2/sqrt(3))+2*p*(o-1))/(2*e*sqrt(e)))*a"
        "+2*(o-1)/sqrt(e)*b+sqrt(e)*c+2*p/sqrt(e)*h;"
    );
    IMap transform(
      "var:U,P,V,Q,a,b,c,h;"
      "fun:"
      "-1/U,"
      "P*(-1/U)*sqrt(-1/U),"
      "Q*(-1/U)*sqrt(-1/U)+2/sqrt(3),"
      "1+V*(-1/U)*(-1/U),"
      "a/(U*U),"
      "b*(-1/U)*sqrt(-1/U)"
        "+1.5*P*sqrt(-1/U)*a/(U*U),"
      "h*(-1/U)*sqrt(-1/U)"
        "+1.5*Q*sqrt(-1/U)*a/(U*U),"
      "c*(-1/U)*(-1/U)"
        "+2*V*(-1/U)*a/(U*U);"
    );

    IVector residual(kUnknowns);
    IMatrix derivative(kUnknowns, kUnknowns);
    derivative.clear();
    double residualSup = 0.;
    for(int segment = 0; segment < kSegments; ++segment) {
      IMap& field = segment <= kTransitionSegment ? rawField : compactField;
      IOdeSolver solver(field, 25);
      solver.setAbsoluteTolerance(1e-14);
      solver.setRelativeTolerance(1e-14);
      const IVector initialCentre = node(centre, segment);
      const IVector initialBox = node(X, segment);

      ITimeMap c0TimeMap(solver);
      C0HOTripletonSet c0Set(initialCentre);
      IVector imageCentre = c0TimeMap(interval(kStep), c0Set);
      ITimeMap c1TimeMap(solver);
      C1HORect2Set c1Set(initialBox);
      c1TimeMap(interval(kStep), c1Set);
      const IVector imageBox = (IVector)c1Set;
      IMatrix segmentDerivative = (IMatrix)c1Set;

      if(segment == kTransitionSegment) {
        IMatrix transformDerivative(kExtendedDimension, kExtendedDimension);
        transform(imageBox, transformDerivative);
        segmentDerivative = transformDerivative * segmentDerivative;
        imageCentre = transform(imageCentre);
      }

      const IVector nextCentre = node(centre, segment + 1);
      for(int output = 0; output < kExtendedDimension; ++output) {
        const int row = kExtendedDimension * segment + output;
        residual[row] = nextCentre[output] - imageCentre[output];
        residualSup = std::max(residualSup, absUpper(residual[row]));
        for(int input = 0; input < kExtendedDimension; ++input)
          derivative[row][column(segment, input)]
            = -segmentDerivative[output][input];
        derivative[row][column(segment + 1, output)] += 1.;
      }
    }

    int row = kExtendedDimension * kSegments;
    const IVector sourceCentre = node(centre, 0);
    const IVector sourceBox = node(X, 0);
    const IVector terminalCentre = node(centre, kSegments);
    const IVector terminalBox = node(X, kSegments);

    residual[row] = sourceCentre[1];
    derivative[row++][column(0, 1)] = 1.;
    residual[row] = sourceCentre[3];
    derivative[row++][column(0, 3)] = 1.;
    residual[row] = sourceCentre[4] - 1.;
    derivative[row++][column(0, 4)] = 1.;
    residual[row] = sourceCentre[5];
    derivative[row++][column(0, 5)] = 1.;
    residual[row] = sourceCentre[7];
    derivative[row++][column(0, 7)] = 1.;

    const RobustTargetData target = robustTarget(
      terminalCentre, terminalBox);
    residual[row] = target.residual;
    for(int i = 0; i < kBaseDimension; ++i)
      derivative[row][column(kSegments, i)] = target.gradient[i];
    ++row;

    residual[row] = target.tangentResidual;
    for(int i = 0; i < kBaseDimension; ++i) {
      derivative[row][column(kSegments, i)]
        = target.tangentStateDerivative[i];
      derivative[row][column(kSegments, 4 + i)] = target.gradient[i];
    }
    ++row;

    const interval U0 = sourceCentre[0], V0 = sourceCentre[2];
    const interval wU0 = sourceCentre[4], wV0 = sourceCentre[6];
    residual[row] = (-interval(2.) * sqr(U0) - interval(2.) * V0)
      * wU0 - interval(2.) * U0 * wV0;
    const interval U = sourceBox[0], V = sourceBox[2];
    const interval wU = sourceBox[4], wV = sourceBox[6];
    derivative[row][column(0, 0)] = -interval(4.) * U * wU
      - interval(2.) * wV;
    derivative[row][column(0, 2)] = -interval(2.) * wU;
    derivative[row][column(0, 4)] = -interval(2.) * sqr(U)
      - interval(2.) * V;
    derivative[row][column(0, 6)] = -interval(2.) * U;
    ++row;
    if(row != kUnknowns) throw std::runtime_error("row count mismatch");

    for(int i = kExtendedDimension * kSegments; i < kUnknowns; ++i)
      residualSup = std::max(residualSup, absUpper(residual[i]));

    DMatrix midpoint(kUnknowns, kUnknowns);
    for(int i = 0; i < kUnknowns; ++i)
      for(int j = 0; j < kUnknowns; ++j)
        midpoint[i][j] = derivative[i][j].mid().leftBound();
    const DMatrix inverse = matrixAlgorithms::inverseMatrix(midpoint);
    IMatrix preconditioner(kUnknowns, kUnknowns);
    for(int i = 0; i < kUnknowns; ++i)
      for(int j = 0; j < kUnknowns; ++j)
        preconditioner[i][j] = inverse[i][j];
    const IMatrix remainder = IMatrix::Identity(kUnknowns)
      - preconditioner * derivative;
    const IVector contractionImage = remainder * (X - centre);
    const IVector krawczyk = centre - preconditioner * residual
      + contractionImage;

    double ratio = 0.;
    double contractionRatio = 0.;
    int worst = -1;
    for(int i = 0; i < kUnknowns; ++i) {
      const double centreValue = centre[i].mid().leftBound();
      const double correction = std::max(
        std::abs(krawczyk[i].leftBound() - centreValue),
        std::abs(krawczyk[i].rightBound() - centreValue));
      const double radius = radiusAt(
        centre, i / kExtendedDimension, i % kExtendedDimension);
      if(correction / radius > ratio) {
        ratio = correction / radius;
        worst = i;
      }
      contractionRatio = std::max(
        contractionRatio, absUpper(contractionImage[i]) / radius);
    }
    if(!subsetInterior(krawczyk, X)) {
      std::cerr << std::setprecision(17)
        << "Krawczyk failure ratio=" << ratio
        << " contraction=" << contractionRatio
        << " worst_node=" << worst / kExtendedDimension
        << " worst_component=" << worst % kExtendedDimension << "\n";
      std::array<std::pair<double, int>, kUnknowns> ranked{};
      for(int i = 0; i < kUnknowns; ++i) {
        const double centreValue = centre[i].mid().leftBound();
        const double correction = std::max(
          std::abs(krawczyk[i].leftBound() - centreValue),
          std::abs(krawczyk[i].rightBound() - centreValue));
        ranked[i] = {
          correction / radiusAt(
            centre, i / kExtendedDimension, i % kExtendedDimension), i
        };
      }
      std::sort(ranked.begin(), ranked.end(),
        [](const auto& left, const auto& right) {
          return left.first > right.first;
        });
      for(int i = 0; i < 12; ++i)
        std::cerr << "  rank=" << i + 1 << " ratio=" << ranked[i].first
          << " node=" << ranked[i].second / kExtendedDimension
          << " component=" << ranked[i].second % kExtendedDimension
          << " K=" << krawczyk[ranked[i].second] << "\n";
      throw std::runtime_error("mixed fold-cap Krawczyk inclusion failed");
    }

    // Replay the already certified robust fixed fold, transform its complete
    // base+tangent Krawczyk image to the mixed chart, and place it strictly
    // inside this cap.  Hence the cap's unique augmented zero is the existing
    // fold, not merely a numerically nearby critical point.
    const OldFoldProof existingFold = certifyExistingFold();
    double existingFoldCapMargin = std::numeric_limits<double>::infinity();
    for(int n = 0; n <= kSegments; ++n) {
      const IVector mixedFold = rawExtendedToMixed(
        node(existingFold.krawczyk, n), n);
      const IVector capNode = node(X, n);
      if(!subsetInterior(mixedFold, capNode)) {
        std::cerr << "existing fold leaves mixed cap at node=" << n
          << " fold=" << mixedFold << " cap=" << capNode << "\n";
        throw std::runtime_error(
          "existing robust fold is not contained in mixed cap");
      }
      for(int component = 0; component < kExtendedDimension; ++component)
        existingFoldCapMargin = std::min({
          existingFoldCapMargin,
          mixedFold[component].leftBound() - capNode[component].leftBound(),
          capNode[component].rightBound() - mixedFold[component].rightBound()
        });
    }
    bool existingFoldInFixedFamily = false;
    double existingFoldFamilyMargin = 0.;
    double existingFoldParameterMargin = 0.;
    if(!gFamilySeedFile.empty()) {
      const FamilySeed seed = loadFamilySeed(
        gFamilySeedFile, gFamilySeedOffset);
      const IVector family = familyAugmentedBox(
        seed, gFamilyHalfWidth, gFamilyRadiusScale);
      existingFoldFamilyMargin = std::numeric_limits<double>::infinity();
      for(int n = 0; n <= kSegments; ++n) {
        const IVector mixedFold = rawExtendedToMixed(
          node(existingFold.krawczyk, n), n);
        const IVector familyNode = node(family, n);
        if(!subsetInterior(mixedFold, familyNode)) {
          double worstMargin = std::numeric_limits<double>::infinity();
          int worstComponent = -1;
          for(int component = 0; component < kExtendedDimension; ++component) {
            const double margin = std::min(
              mixedFold[component].leftBound()
                - familyNode[component].leftBound(),
              familyNode[component].rightBound()
                - mixedFold[component].rightBound());
            if(margin < worstMargin) {
              worstMargin = margin;
              worstComponent = component;
            }
          }
          std::cerr << std::setprecision(17)
            << "existing fold leaves fixed-family box at node=" << n
            << " component=" << worstComponent
            << " margin=" << worstMargin
            << " fold=" << mixedFold[worstComponent]
            << " family=" << familyNode[worstComponent] << "\n";
          throw std::runtime_error(
            "existing robust fold is not contained in fixed family box");
        }
        for(int component = 0; component < kExtendedDimension; ++component)
          existingFoldFamilyMargin = std::min({
            existingFoldFamilyMargin,
            mixedFold[component].leftBound()
              - familyNode[component].leftBound(),
            familyNode[component].rightBound()
              - mixedFold[component].rightBound()
          });
      }
      const interval parameter(
        seed.sourceU - gFamilyHalfWidth,
        seed.sourceU + gFamilyHalfWidth);
      const interval foldParameter = existingFold.krawczyk[column(0, 0)];
      if(!subsetInterior(foldParameter, parameter))
        throw std::runtime_error(
          "existing fold parameter leaves fixed-family parameter interval");
      existingFoldParameterMargin = std::min(
        foldParameter.leftBound() - parameter.leftBound(),
        parameter.rightBound() - foldParameter.rightBound());
      existingFoldInFixedFamily = true;
    }

    const interval sourceU = krawczyk[column(0, 0)];
    const interval sourceV = krawczyk[column(0, 2)];
    const interval energy = -interval(2.) * sourceU * sourceU * sourceU
      / interval(3.) - interval(2.) * sourceU * sourceV;
    const interval energyDerivative =
      (-interval(2.) * sqr(sourceU) - interval(2.) * sourceV)
        * krawczyk[column(0, 4)]
      - interval(2.) * sourceU * krawczyk[column(0, 6)];

    double minimumMargin = std::numeric_limits<double>::infinity();
    for(int i = 0; i < kUnknowns; ++i)
      minimumMargin = std::min({
        minimumMargin,
        krawczyk[i].leftBound() - X[i].leftBound(),
        X[i].rightBound() - krawczyk[i].rightBound()
      });

    std::cout << std::setprecision(17)
      << "{\n"
      << "  \"status\": \"PASS-MIXED-CHART-AUGMENTED-FOLD-CAP\",\n"
      << "  \"segments\": " << kSegments << ",\n"
      << "  \"unknowns\": " << kUnknowns << ",\n"
      << "  \"switch_node\": " << kSwitchNode << ",\n"
      << "  \"switch_time\": 2.0,\n"
      << "  \"declared_cap_half_width\": " << gCapHalfWidth << ",\n"
      << "  \"source_X_U\": \"" << sourceBox[0] << "\",\n"
      << "  \"source_U\": \"" << sourceU << "\",\n"
      << "  \"source_V\": \"" << sourceV << "\",\n"
      << "  \"source_energy\": \"" << energy << "\",\n"
      << "  \"d_source_energy_dU\": \"" << energyDerivative << "\",\n"
      << "  \"target_eta_C0_bound\": " << target.valueBound << ",\n"
      << "  \"target_eta_C1_bound\": " << kSlopeBound << ",\n"
      << "  \"target_eta_C2_bound\": " << kHessianBound << ",\n"
      << "  \"terminal_X_e\": \"" << physical.e << "\",\n"
      << "  \"terminal_X_a\": \"" << physical.a << "\",\n"
      << "  \"terminal_X_b\": \"" << physical.b << "\",\n"
      << "  \"terminal_X_graph_energy\": \""
        << physical.graphEnergy << "\",\n"
      << "  \"krawczyk_ratio\": " << ratio << ",\n"
      << "  \"contraction_ratio\": " << contractionRatio << ",\n"
      << "  \"minimum_containment_margin\": " << minimumMargin << ",\n"
      << "  \"existing_fold_full_state_contained\": true,\n"
      << "  \"existing_fold_cap_margin\": "
        << existingFoldCapMargin << ",\n"
      << "  \"existing_fold_krawczyk_ratio\": "
        << existingFold.ratio << ",\n"
      << "  \"existing_fold_contraction_ratio\": "
        << existingFold.contractionRatio << ",\n"
      << "  \"existing_fold_in_fixed_family_full_state\": "
        << (existingFoldInFixedFamily ? "true" : "false") << ",\n"
      << "  \"existing_fold_fixed_family_margin\": "
        << existingFoldFamilyMargin << ",\n"
      << "  \"existing_fold_fixed_parameter_margin\": "
        << existingFoldParameterMargin << ",\n"
      << "  \"residual_sup\": " << residualSup << ",\n"
      << "  \"worst_node\": " << worst / kExtendedDimension << ",\n"
      << "  \"worst_component\": " << worst % kExtendedDimension << "\n"
      << "}\n";
    return 0;
  } catch(const std::exception& error) {
    std::cerr << "FAIL: " << error.what() << "\n";
    return 12;
  }
}
