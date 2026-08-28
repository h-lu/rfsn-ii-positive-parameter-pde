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
#include "tail_graph_generated.hpp"
#include "weighted_tail_generated.hpp"

using namespace capd;

namespace {

constexpr int kSegments = 30;
constexpr int kDimension = 4;
constexpr int kUnknowns = kDimension * (kSegments + 1);
constexpr int kSwitchNode = 4;
constexpr int kTransitionSegment = kSwitchNode - 1;
constexpr double kStep = .5;
constexpr double kTailEntryE = .06;
constexpr double kTargetSlopeError = 1e-5;

struct Seed {
  double sourceU = 0.;
  double sourceV = 0.;
  std::array<std::array<double, kDimension>, kSegments + 1> centre{};
  std::array<std::array<double, kDimension>, kSegments + 1> tangent{};
  std::array<std::array<double, kDimension>, kSegments + 1> curvature{};
};

std::string gSeedFile;
std::int64_t gSeedOffset = 0;
double gHalfWidth = 2e-5;
double gRadiusScale = 1.;
bool gExactC0 = false;
bool gDoBridge = false;
std::string gBridgeSeedFile;
std::int64_t gBridgeSeedOffset = 0;
double gBridgeHalfWidth = 0.;
double gBridgeRadiusScale = 1.;
double gBridgeParameter = 0.;
std::array<double, 3> gSlopeCentre{{0., 0., 0.}};
double gSlopeHalfWidth = kTargetSlopeError;
double gSourceTangentRelative = 5e-3;

double absUpper(const interval& value) {
  return std::max(std::abs(value.leftBound()),
                  std::abs(value.rightBound()));
}

int column(int nodeIndex, int component) {
  return kDimension * nodeIndex + component;
}

IVector node(const IVector& all, int nodeIndex) {
  IVector result(kDimension);
  for(int component = 0; component < kDimension; ++component)
    result[component] = all[column(nodeIndex, component)];
  return result;
}

Seed loadSeed(const std::string& path, std::int64_t offset) {
  std::ifstream input(path);
  if(!input) throw std::runtime_error("cannot open seed file");
  input.seekg(offset);
  if(!input) throw std::runtime_error("cannot seek seed file");
  Seed result;
  input >> result.sourceU >> result.sourceV;
  for(int n = 0; n <= kSegments; ++n)
    for(int component = 0; component < kDimension; ++component)
      input >> result.centre[n][component];
  for(int n = 0; n <= kSegments; ++n)
    for(int component = 0; component < kDimension; ++component)
      input >> result.tangent[n][component];
  for(int n = 0; n <= kSegments; ++n)
    for(int component = 0; component < kDimension; ++component)
      input >> result.curvature[n][component];
  if(!input) throw std::runtime_error("malformed seed file");
  return result;
}

double baseRadius(int nodeIndex, int component) {
  if(nodeIndex < kSwitchNode) return 3e-8;
  switch(component) {
    case 0: return 3e-9;
    case 1: return 3e-9;
    case 2: return 3e-9;
    case 3: return 3e-9;
  }
  throw std::runtime_error("invalid component");
}

double radiusAt(const Seed& seed, double halfWidth, double radiusScale,
                int nodeIndex, int component) {
  const double tangentTube = 1.35 * halfWidth
    * std::abs(seed.tangent[nodeIndex][component]);
  double base = radiusScale * baseRadius(nodeIndex, component);
  // The raw-to-compact transition has a fixed outward-rounded centre image
  // correction in omega.  Retain its proved base allowance when a narrow
  // endpoint audit scales the remaining tube.
  if(nodeIndex == kSwitchNode)
    base = baseRadius(nodeIndex, component);
  return base + radiusScale * tangentTube;
}

double tangentBaseRadius(int nodeIndex, int component,
                         double tangentValue) {
  const double relative = nodeIndex == 0 ? gSourceTangentRelative
    : (nodeIndex >= kSwitchNode && component == 2 ? 2e-2 : 5e-3);
  return relative * (1. + std::abs(tangentValue));
}

double tangentRadiusAt(const Seed& seed, double halfWidth,
                       int nodeIndex, int component) {
  const double value = seed.tangent[nodeIndex][component];
  return tangentBaseRadius(nodeIndex, component, value)
    + 1.5 * halfWidth * std::abs(seed.curvature[nodeIndex][component]);
}

IVector centreVector(const Seed& seed) {
  IVector result(kUnknowns);
  for(int n = 0; n <= kSegments; ++n)
    for(int component = 0; component < kDimension; ++component)
      result[column(n, component)] = seed.centre[n][component];
  return result;
}

IVector boxAround(const Seed& seed, double halfWidth, double radiusScale) {
  IVector result(kUnknowns);
  for(int n = 0; n <= kSegments; ++n)
    for(int component = 0; component < kDimension; ++component) {
      const double centre = seed.centre[n][component];
      const double radius = radiusAt(
        seed, halfWidth, radiusScale, n, component);
      result[column(n, component)] = interval(
        centre - radius, centre + radius);
    }
  return result;
}

struct Jet4 {
  interval value;
  std::array<interval, kDimension> gradient;

  Jet4() : value(0.) { gradient.fill(interval(0.)); }
  Jet4(int x) : value(x) { gradient.fill(interval(0.)); }
  Jet4(long x) : value(static_cast<double>(x)) {
    gradient.fill(interval(0.));
  }
  Jet4(long long x) : value(static_cast<double>(x)) {
    gradient.fill(interval(0.));
  }
  Jet4(double x) : value(x) { gradient.fill(interval(0.)); }
  Jet4(const interval& x) : value(x) { gradient.fill(interval(0.)); }

  static Jet4 variable(const interval& value, int index) {
    Jet4 result(value);
    result.gradient[index] = 1.;
    return result;
  }
  Jet4& operator+=(const Jet4& other) {
    value += other.value;
    for(int i = 0; i < kDimension; ++i)
      gradient[i] += other.gradient[i];
    return *this;
  }
  Jet4& operator-=(const Jet4& other) {
    value -= other.value;
    for(int i = 0; i < kDimension; ++i)
      gradient[i] -= other.gradient[i];
    return *this;
  }
};

Jet4 operator+(Jet4 left, const Jet4& right) { return left += right; }
Jet4 operator-(Jet4 left, const Jet4& right) { return left -= right; }
Jet4 operator-(const Jet4& value) {
  Jet4 result;
  result.value = -value.value;
  for(int i = 0; i < kDimension; ++i)
    result.gradient[i] = -value.gradient[i];
  return result;
}
Jet4 operator*(const Jet4& left, const Jet4& right) {
  Jet4 result;
  result.value = left.value * right.value;
  for(int i = 0; i < kDimension; ++i)
    result.gradient[i] = left.gradient[i] * right.value
      + left.value * right.gradient[i];
  return result;
}
Jet4 reciprocal(const Jet4& value) {
  Jet4 result;
  result.value = interval(1.) / value.value;
  for(int i = 0; i < kDimension; ++i)
    result.gradient[i] = -value.gradient[i] / sqr(value.value);
  return result;
}
Jet4 operator/(const Jet4& left, const Jet4& right) {
  return left * reciprocal(right);
}
Jet4 sqrt(const Jet4& value) {
  using std::sqrt;
  Jet4 result;
  result.value = sqrt(value.value);
  for(int i = 0; i < kDimension; ++i)
    result.gradient[i] = value.gradient[i]
      / (interval(2.) * result.value);
  return result;
}

std::array<Jet4, kDimension> rawToCompactJets(const IVector& raw) {
  const Jet4 U = Jet4::variable(raw[0], 0);
  const Jet4 P = Jet4::variable(raw[1], 1);
  const Jet4 V = Jet4::variable(raw[2], 2);
  const Jet4 Q = Jet4::variable(raw[3], 3);
  const Jet4 e = -Jet4(1) / U;
  const Jet4 e32 = e * sqrt(e);
  return {
    e,
    P * e32,
    Q * e32 + Jet4(2) / sqrt(Jet4(3)),
    Jet4(1) + V * e * e
  };
}

IVector rawToCompactValues(const IVector& raw) {
  const auto jets = rawToCompactJets(raw);
  IVector result(kDimension);
  for(int i = 0; i < kDimension; ++i) result[i] = jets[i].value;
  return result;
}

struct TargetData {
  Jet4 residual;
  std::array<Jet4, 3> base;
};

TargetData targetData(const IVector& compact) {
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

struct TargetRow {
  interval value;
  std::array<interval, kDimension> gradient;
  double etaBound = 0.;
};

TargetRow targetRow(const IVector& point, const IVector& box) {
  const TargetData pointData = targetData(point);
  const TargetData boxData = targetData(box);
  TargetRow result;
  result.etaBound = 2. * absUpper(eighthPower(box[0]));
  result.value = pointData.residual.value
    + interval(-result.etaBound, result.etaBound);
  for(int i = 0; i < kDimension; ++i) {
    result.gradient[i] = boxData.residual.gradient[i];
    for(int base = 0; base < 3; ++base) {
      const interval slope(
        gSlopeCentre[base] - gSlopeHalfWidth,
        gSlopeCentre[base] + gSlopeHalfWidth);
      result.gradient[i] -= slope * boxData.base[base].gradient[i];
    }
  }
  return result;
}

struct PhysicalContract {
  interval e, a, b, graphEnergy;
};

PhysicalContract terminalPhysicalContract(const IVector& compact) {
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
       && graphEnergy.rightBound() < .012)) {
    std::ostringstream message;
    message << "terminal box leaves physical target corridor: e=" << e
      << " a=" << a << " b=" << b << " E=" << graphEnergy;
    throw std::runtime_error(message.str());
  }
  return {e, a, b, graphEnergy};
}

void parseArguments(int argc, char** argv) {
  for(int i = 1; i < argc; ++i) {
    const std::string argument(argv[i]);
    if(argument == "--seed-file" && i + 1 < argc)
      gSeedFile = argv[++i];
    else if(argument == "--seed-offset" && i + 1 < argc)
      gSeedOffset = std::stoll(argv[++i]);
    else if(argument == "--half-width" && i + 1 < argc)
      gHalfWidth = std::stod(argv[++i]);
    else if(argument == "--radius-scale" && i + 1 < argc)
      gRadiusScale = std::stod(argv[++i]);
    else if(argument == "--exact-c0")
      gExactC0 = true;
    else if(argument == "--bridge-seed-file" && i + 1 < argc) {
      gBridgeSeedFile = argv[++i];
      gDoBridge = true;
    }
    else if(argument == "--bridge-seed-offset" && i + 1 < argc)
      gBridgeSeedOffset = std::stoll(argv[++i]);
    else if(argument == "--bridge-half-width" && i + 1 < argc)
      gBridgeHalfWidth = std::stod(argv[++i]);
    else if(argument == "--bridge-radius-scale" && i + 1 < argc)
      gBridgeRadiusScale = std::stod(argv[++i]);
    else if(argument == "--bridge-parameter" && i + 1 < argc)
      gBridgeParameter = std::stod(argv[++i]);
    else if(argument == "--slope-e-centre" && i + 1 < argc)
      gSlopeCentre[0] = std::stod(argv[++i]);
    else if(argument == "--slope-d-centre" && i + 1 < argc)
      gSlopeCentre[1] = std::stod(argv[++i]);
    else if(argument == "--slope-omega-centre" && i + 1 < argc)
      gSlopeCentre[2] = std::stod(argv[++i]);
    else if(argument == "--slope-half-width" && i + 1 < argc)
      gSlopeHalfWidth = std::stod(argv[++i]);
    else if(argument == "--source-tangent-relative" && i + 1 < argc)
      gSourceTangentRelative = std::stod(argv[++i]);
    else
      throw std::runtime_error("invalid command-line argument");
  }
  if(gSeedFile.empty() || gSeedOffset < 0 || !(gHalfWidth > 0.)
     || !(gRadiusScale > 0.))
    throw std::runtime_error("incomplete seed/box arguments");
  if(gDoBridge && (gBridgeSeedFile.empty() || gBridgeSeedOffset < 0
                   || !(gBridgeHalfWidth > 0.)
                   || !(gBridgeRadiusScale > 0.)))
    throw std::runtime_error("incomplete bridge arguments");
  if(!(gSlopeHalfWidth > 0.))
    throw std::runtime_error("slope half width must be positive");
  if(!(gSourceTangentRelative > 0.))
    throw std::runtime_error("source tangent relative radius must be positive");
  for(double centre:gSlopeCentre)
    if(centre - gSlopeHalfWidth < -kTargetSlopeError
       || centre + gSlopeHalfWidth > kTargetSlopeError)
      throw std::runtime_error("slope subbox leaves declared target jet cube");
}

interval rigorousK0() {
  // verify_jost_constant.py independently proves that the exact gamma-ratio
  // lies strictly between these two binary64 endpoints.
  return interval(0x1.12090b7dc7279p-1, 0x1.12090b7dc727bp-1);
}

struct FirstEventAudit {
  double lowerTime = 0.;
  double upperTime = 0.;
};

FirstEventAudit verifyFirstTailEntry(IMap& rawField, IMap& compactField,
                                     const IVector& root) {
  const double sectionU = -1. / kTailEntryE;
  for(int segment = 0; segment < kSwitchNode; ++segment) {
    IOdeSolver solver(rawField, 25);
    solver.setAbsoluteTolerance(1e-14);
    solver.setRelativeTolerance(1e-14);
    ITimeMap timeMap(solver);
    timeMap.stopAfterStep(true);
    C0HORect2Set set(node(root, segment));
    do {
      timeMap(interval(kStep), set);
      if(!(set.getLastEnclosure()[0].leftBound() > sectionU))
        throw std::runtime_error("tail-entry section met before compact switch");
    } while(!timeMap.completed());
  }

  for(int segment = kSwitchNode; segment < kSegments; ++segment) {
    IOdeSolver solver(compactField, 25);
    solver.setAbsoluteTolerance(1e-14);
    solver.setRelativeTolerance(1e-14);
    ITimeMap timeMap(solver);
    timeMap.stopAfterStep(true);
    C0HORect2Set set(node(root, segment));
    do {
      timeMap(interval(kStep), set);
      const IVector enclosure = set.getLastEnclosure();
      if(!(enclosure[0].leftBound() > 0.))
        throw std::runtime_error("compact e loses positivity");
      if(!(enclosure[1].rightBound() < 0.))
        throw std::runtime_error("compact p is not strictly negative");
    } while(!timeMap.completed());
  }

  if(!(node(root, kSwitchNode)[0].leftBound() > kTailEntryE
       && node(root, kSegments)[0].rightBound() < kTailEntryE))
    throw std::runtime_error("compact endpoints do not bracket e=.06");
  int lastAbove = kSwitchNode;
  int firstBelow = -1;
  for(int n = kSwitchNode; n <= kSegments; ++n) {
    const interval e = node(root, n)[0];
    if(e.leftBound() > kTailEntryE) lastAbove = n;
    if(firstBelow < 0 && e.rightBound() < kTailEntryE) firstBelow = n;
  }
  if(firstBelow < 0 || !(lastAbove < firstBelow))
    throw std::runtime_error("could not isolate first tail-entry event bracket");
  return {kStep * lastAbove, kStep * firstBelow};
}

struct ExactAudit {
  bool stateContained = false;
  bool targetBudget = false;
  bool jostSlopeContained = false;
  double minimumMargin = 0.;
  interval k0, jostSlope, algebraicTargetResidual;
};

ExactAudit verifyExactC0(const IVector& X, const IVector& tangentKrawczyk,
                         const interval& sourceParameter) {
  if(!(sourceParameter.leftBound() < 0.
       && sourceParameter.rightBound() > 0.))
    throw std::runtime_error("c0 parameter is not strictly interior");
  ExactAudit result;
  result.minimumMargin = std::numeric_limits<double>::infinity();
  for(int n = 0; n <= kSegments; ++n) {
    const interval t(kStep * n);
    IVector raw(kDimension);
    raw[0] = -t * t / interval(12.);
    raw[1] = -t / interval(6.);
    raw[2] = interval(1.) / interval(6.)
      - t * t * t * t / interval(144.);
    raw[3] = -t * t * t / interval(36.);
    const IVector exact = n < kSwitchNode ? raw : rawToCompactValues(raw);
    const IVector box = node(X, n);
    if(!subsetInterior(exact, box))
      throw std::runtime_error("exact algebraic orbit leaves first uniqueness box");
    for(int component = 0; component < kDimension; ++component)
      result.minimumMargin = std::min({
        result.minimumMargin,
        exact[component].leftBound() - box[component].leftBound(),
        box[component].rightBound() - exact[component].rightBound()
      });
  }
  result.stateContained = true;
  IVector terminalRaw(kDimension);
  const interval T(15.);
  terminalRaw[0] = -T * T / interval(12.);
  terminalRaw[1] = -T / interval(6.);
  terminalRaw[2] = interval(1.) / interval(6.)
    - T * T * T * T / interval(144.);
  terminalRaw[3] = -T * T * T / interval(36.);
  const IVector terminal = rawToCompactValues(terminalRaw);
  result.algebraicTargetResidual = targetData(terminal).residual.value;
  const double etaBound = 2. * absUpper(eighthPower(terminal[0]));
  if(!(absUpper(result.algebraicTargetResidual) < etaBound))
    throw std::runtime_error("exact algebraic target value leaves C0 budget");
  result.targetBudget = true;
  result.k0 = rigorousK0();
  result.jostSlope = -interval(2.) * result.k0;
  const interval tangentSourceV = tangentKrawczyk[column(0, 2)];
  if(!(result.jostSlope.leftBound() > tangentSourceV.leftBound()
       && result.jostSlope.rightBound() < tangentSourceV.rightBound()))
    throw std::runtime_error("exact Jost source slope leaves tangent enclosure");
  result.jostSlopeContained = true;
  return result;
}

} // namespace

int main(int argc, char** argv) {
  try {
    parseArguments(argc, argv);
    const Seed seed = loadSeed(gSeedFile, gSeedOffset);
    const IVector centre = centreVector(seed);
    const IVector X = boxAround(seed, gHalfWidth, gRadiusScale);
    const interval sourceParameter(
      seed.sourceU - gHalfWidth, seed.sourceU + gHalfWidth);
    const PhysicalContract physical = terminalPhysicalContract(
      node(X, kSegments));

    IMap rawField("var:U,P,V,Q;fun:P,-U*U-V,Q,U;");
    IMap compactField(
      "var:e,p,d,o;"
      "fun:p*sqrt(e),(1.5*p*p-o)/sqrt(e),"
      "(1.5*p*(d-2/sqrt(3))-e)/sqrt(e),"
      "(e*(d-2/sqrt(3))+2*p*(o-1))/sqrt(e);"
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
      IVector imageBox = (IVector)c1Set;
      IMatrix monodromy = (IMatrix)c1Set;

      IMatrix segmentDerivative(kDimension, kDimension);
      if(segment == kTransitionSegment) {
        const auto centreTransform = rawToCompactJets(imageCentre);
        const auto boxTransform = rawToCompactJets(imageBox);
        for(int output = 0; output < kDimension; ++output) {
          imageCentre[output] = centreTransform[output].value;
          for(int input = 0; input < kDimension; ++input) {
            segmentDerivative[output][input] = 0.;
            for(int middle = 0; middle < kDimension; ++middle)
              segmentDerivative[output][input]
                += boxTransform[output].gradient[middle]
                   * monodromy[middle][input];
          }
        }
      } else {
        segmentDerivative = monodromy;
      }

      const IVector nextCentre = node(centre, segment + 1);
      for(int output = 0; output < kDimension; ++output) {
        const int row = kDimension * segment + output;
        residual[row] = nextCentre[output] - imageCentre[output];
        residualSup = std::max(residualSup, absUpper(residual[row]));
        for(int input = 0; input < kDimension; ++input)
          derivative[row][column(segment, input)]
            = -segmentDerivative[output][input];
        derivative[row][column(segment + 1, output)] += 1.;
      }
    }

    int row = kDimension * kSegments;
    const IVector sourcePoint = node(centre, 0);
    residual[row] = sourcePoint[0] - sourceParameter;
    derivative[row++][column(0, 0)] = 1.;
    residual[row] = sourcePoint[1];
    derivative[row++][column(0, 1)] = 1.;
    residual[row] = sourcePoint[3];
    derivative[row++][column(0, 3)] = 1.;
    const IVector terminalPoint = node(centre, kSegments);
    const IVector terminalBox = node(X, kSegments);
    const TargetRow target = targetRow(terminalPoint, terminalBox);
    residual[row] = target.value;
    for(int i = 0; i < kDimension; ++i)
      derivative[row][column(kSegments, i)] = target.gradient[i];
    ++row;
    if(row != kUnknowns) throw std::runtime_error("row count mismatch");
    for(int i = kDimension * kSegments; i < kUnknowns; ++i)
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
        seed, gHalfWidth, gRadiusScale, i / kDimension, i % kDimension);
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
        << " worst_node=" << worst / kDimension
        << " worst_component=" << worst % kDimension << "\n";
      throw std::runtime_error("base Krawczyk inclusion failed");
    }

    IVector tangentCentre(kUnknowns), tangentBox(kUnknowns), tangentRhs(kUnknowns);
    tangentRhs.clear();
    tangentRhs[kDimension * kSegments] = 1.;
    std::array<double, kUnknowns> tangentRadii{};
    for(int n = 0; n <= kSegments; ++n)
      for(int component = 0; component < kDimension; ++component) {
        const int i = column(n, component);
        const double value = seed.tangent[n][component];
        const double radius = tangentRadiusAt(
          seed, gHalfWidth, n, component);
        tangentCentre[i] = value;
        tangentRadii[i] = radius;
        tangentBox[i] = interval(value - radius, value + radius);
      }
    const IVector tangentResidual = derivative * tangentCentre - tangentRhs;
    const IVector tangentKrawczyk = tangentCentre
      - preconditioner * tangentResidual
      + remainder * (tangentBox - tangentCentre);
    double tangentRatio = 0.;
    int tangentWorst = -1;
    for(int i = 0; i < kUnknowns; ++i) {
      const double centreValue = tangentCentre[i].mid().leftBound();
      const double correction = std::max(
        std::abs(tangentKrawczyk[i].leftBound() - centreValue),
        std::abs(tangentKrawczyk[i].rightBound() - centreValue));
      if(correction / tangentRadii[i] > tangentRatio) {
        tangentRatio = correction / tangentRadii[i];
        tangentWorst = i;
      }
    }
    if(!subsetInterior(tangentKrawczyk, tangentBox)) {
      std::cerr << std::setprecision(17)
        << "tangent failure ratio=" << tangentRatio
        << " worst_node=" << tangentWorst / kDimension
        << " worst_component=" << tangentWorst % kDimension << "\n";
      throw std::runtime_error("tangent Krawczyk inclusion failed");
    }

    const FirstEventAudit event = verifyFirstTailEntry(
      rawField, compactField, krawczyk);
    const IVector sourceRoot = node(krawczyk, 0);
    const interval sourceEnergy = -interval(2.) * sourceRoot[0]
      * sourceRoot[0] * sourceRoot[0] / interval(3.)
      - interval(2.) * sourceRoot[0] * sourceRoot[2];
    const interval energyDerivative =
      (-interval(2.) * sqr(sourceRoot[0])
       - interval(2.) * sourceRoot[2]) * tangentKrawczyk[column(0, 0)]
      - interval(2.) * sourceRoot[0] * tangentKrawczyk[column(0, 2)];

    bool bridgeCertified = false;
    double bridgeCurrentMargin = 0.;
    double bridgeNextMargin = 0.;
    double bridgeNextParameterMargin = 0.;
    if(gDoBridge) {
      IVector bridgeResidual = residual;
      bridgeResidual[kDimension * kSegments]
        = sourcePoint[0] - interval(gBridgeParameter);
      const IVector bridgeKrawczyk = centre
        - preconditioner * bridgeResidual + contractionImage;
      if(!subsetInterior(bridgeKrawczyk, X))
        throw std::runtime_error("bridge root leaves current uniqueness box");
      const Seed nextSeed = loadSeed(gBridgeSeedFile, gBridgeSeedOffset);
      const IVector nextX = boxAround(
        nextSeed, gBridgeHalfWidth, gBridgeRadiusScale);
      if(!subsetInterior(bridgeKrawczyk, nextX))
        throw std::runtime_error("bridge root leaves next uniqueness box");
      const interval nextParameter(
        nextSeed.sourceU - gBridgeHalfWidth,
        nextSeed.sourceU + gBridgeHalfWidth);
      const interval selectedParameter = node(bridgeKrawczyk, 0)[0];
      if(!subsetInterior(selectedParameter, nextParameter))
        throw std::runtime_error("bridge parameter leaves next interval");
      bridgeCurrentMargin = std::numeric_limits<double>::infinity();
      bridgeNextMargin = std::numeric_limits<double>::infinity();
      for(int i = 0; i < kUnknowns; ++i) {
        bridgeCurrentMargin = std::min({
          bridgeCurrentMargin,
          bridgeKrawczyk[i].leftBound() - X[i].leftBound(),
          X[i].rightBound() - bridgeKrawczyk[i].rightBound()
        });
        bridgeNextMargin = std::min({
          bridgeNextMargin,
          bridgeKrawczyk[i].leftBound() - nextX[i].leftBound(),
          nextX[i].rightBound() - bridgeKrawczyk[i].rightBound()
        });
      }
      bridgeNextParameterMargin = std::min(
        selectedParameter.leftBound() - nextParameter.leftBound(),
        nextParameter.rightBound() - selectedParameter.rightBound());
      bridgeCertified = true;
    }

    ExactAudit exact;
    if(gExactC0)
      exact = verifyExactC0(X, tangentKrawczyk, sourceParameter);

    std::cout << std::setprecision(17)
      << "{\n"
      << "  \"status\": \"PASS-FIXED-TIME-PARAMETRIC-COVER-BOX\",\n"
      << "  \"segments\": " << kSegments << ",\n"
      << "  \"unknowns\": " << kUnknowns << ",\n"
      << "  \"switch_node\": " << kSwitchNode << ",\n"
      << "  \"switch_time\": 2.0,\n"
      << "  \"source_parameter\": \"" << sourceParameter << "\",\n"
      << "  \"source_U\": \"" << sourceRoot[0] << "\",\n"
      << "  \"source_V\": \"" << sourceRoot[2] << "\",\n"
      << "  \"source_energy\": \"" << sourceEnergy << "\",\n"
      << "  \"d_source_energy_dU\": \"" << energyDerivative << "\",\n"
      << "  \"d_source_V_dU\": \""
      << tangentKrawczyk[column(0, 2)] << "\",\n"
      << "  \"terminal_e\": \"" << node(krawczyk, kSegments)[0] << "\",\n"
      << "  \"terminal_X_physical_a\": \"" << physical.a << "\",\n"
      << "  \"terminal_X_physical_b\": \"" << physical.b << "\",\n"
      << "  \"terminal_X_graph_energy_abs_zeta_le_2\": \""
      << physical.graphEnergy << "\",\n"
      << "  \"target_eta_C0_bound\": " << target.etaBound << ",\n"
      << "  \"target_eta_partial_bound\": 1e-5,\n"
      << "  \"target_slope_e_interval\": \"["
      << gSlopeCentre[0] - gSlopeHalfWidth << ", "
      << gSlopeCentre[0] + gSlopeHalfWidth << "]\",\n"
      << "  \"target_slope_d_interval\": \"["
      << gSlopeCentre[1] - gSlopeHalfWidth << ", "
      << gSlopeCentre[1] + gSlopeHalfWidth << "]\",\n"
      << "  \"target_slope_omega_interval\": \"["
      << gSlopeCentre[2] - gSlopeHalfWidth << ", "
      << gSlopeCentre[2] + gSlopeHalfWidth << "]\",\n"
      << "  \"first_e_0.06_event\": true,\n"
      << "  \"first_event_time_bracket\": \"[" << event.lowerTime
      << ", " << event.upperTime << "]\",\n"
      << "  \"krawczyk_ratio\": " << ratio << ",\n"
      << "  \"contraction_ratio\": " << contractionRatio << ",\n"
      << "  \"tangent_krawczyk_ratio\": " << tangentRatio << ",\n"
      << "  \"residual_sup\": " << residualSup << ",\n"
      << "  \"adjacent_bridge_certified\": "
      << (bridgeCertified ? "true" : "false") << ",\n"
      << "  \"bridge_current_containment_margin\": "
      << bridgeCurrentMargin << ",\n"
      << "  \"bridge_next_containment_margin\": "
      << bridgeNextMargin << ",\n"
      << "  \"bridge_next_parameter_margin\": "
      << bridgeNextParameterMargin << ",\n"
      << "  \"exact_c0_state_contained\": "
      << (exact.stateContained ? "true" : "false") << ",\n"
      << "  \"exact_c0_minimum_state_margin\": "
      << exact.minimumMargin << ",\n"
      << "  \"exact_algebraic_target_within_C0_budget\": "
      << (exact.targetBudget ? "true" : "false") << ",\n"
      << "  \"exact_algebraic_target_residual\": \""
      << exact.algebraicTargetResidual << "\",\n"
      << "  \"rigorous_k0\": \"" << exact.k0 << "\",\n"
      << "  \"exact_Jost_dV_dU\": \"" << exact.jostSlope << "\",\n"
      << "  \"exact_Jost_slope_contained\": "
      << (exact.jostSlopeContained ? "true" : "false") << ",\n"
      << "  \"worst_node\": " << worst / kDimension << ",\n"
      << "  \"worst_component\": " << worst % kDimension << ",\n"
      << "  \"tangent_worst_node\": "
      << tangentWorst / kDimension << ",\n"
      << "  \"tangent_worst_component\": "
      << tangentWorst % kDimension << "\n"
      << "}\n";
    return 0;
  } catch(const std::exception& error) {
    std::cerr << "FAIL: " << error.what() << "\n";
    return 12;
  }
}
