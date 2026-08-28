#include <algorithm>
#include <array>
#include <cmath>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <cstdint>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>
#include <vector>

#include "capd/capdlib.h"
#include "../fundamental-annulus-overlap/fixed_radial_source_centres.hpp"
#if __has_include("tail_graph_generated.hpp")
#include "tail_graph_generated.hpp"
#include "weighted_tail_generated.hpp"
#else
#include "../future-target-fold/tail_graph_generated.hpp"
#include "../future-target-fold/weighted_tail_generated.hpp"
#endif

using namespace capd;

namespace {

#ifdef PAPERA_SEGMENTS
constexpr int kSegments = PAPERA_SEGMENTS;
#else
constexpr int kSegments = 36;
#endif
constexpr int kDimension = 5;
constexpr int kUnknowns = kDimension * (kSegments + 1);
constexpr double kStep = 1.0 / kSegments;
constexpr double kSectionE = .0575;
constexpr double kTargetSlopeError = 1e-5;

double gHalfWidth = 1e-5;
double gRadiusScale = 1.;
std::string gParameter = "v";
std::string gSeedTangentKind = "v";
std::string gSeedFile;
std::int64_t gSeedOffset = 0;
std::string gBridgeSeedFile;
std::int64_t gBridgeSeedOffset = 0;
std::string gBridgeChart;
double gBridgeHalfWidth = 0.;
double gBridgeParameter = 0.;
bool gDoBridge = false;
std::string gCoarseSeedFile;
std::int64_t gCoarseSeedOffset = 0;
int gCoarseSegments = 0;
std::string gCoarseChart;
double gCoarseHalfWidth = 0.;
double gCoarseRadiusScale = 1.;
bool gDoCoarseContainment = false;
bool gDoFixedRadialSeamContainment = false;

struct RuntimeSeed {
  double sourceV = 0.;
  double sourceU = 0.;
  double totalTime = 0.;
  std::array<std::array<double,kDimension>,kSegments + 1> centre{};
  std::array<std::array<double,kDimension>,kSegments + 1> derivativeV{};
};

RuntimeSeed gRuntimeSeed;
bool gUseRuntimeSeed = false;

double seedSourceV() {
  return gRuntimeSeed.sourceV;
}

double seedCentre(int nodeIndex, int component) {
  return gRuntimeSeed.centre[nodeIndex][component];
}

double seedDerivativeV(int nodeIndex, int component) {
  return gRuntimeSeed.derivativeV[nodeIndex][component];
}

void loadRuntimeSeed(const std::string& path) {
  std::ifstream input(path);
  if(!input) throw std::runtime_error("cannot open seed file");
  input.seekg(gSeedOffset);
  if(!input) throw std::runtime_error("cannot seek seed file");
  input >> gRuntimeSeed.sourceV >> gRuntimeSeed.sourceU
    >> gRuntimeSeed.totalTime;
  for(int nodeIndex = 0; nodeIndex <= kSegments; ++nodeIndex)
    for(int component = 0; component < kDimension; ++component)
      input >> gRuntimeSeed.centre[nodeIndex][component];
  for(int nodeIndex = 0; nodeIndex <= kSegments; ++nodeIndex)
    for(int component = 0; component < kDimension; ++component)
      input >> gRuntimeSeed.derivativeV[nodeIndex][component];
  if(!input) throw std::runtime_error("malformed seed file");
  gUseRuntimeSeed = true;
}

struct GenericSeed {
  double sourceV = 0.;
  double sourceU = 0.;
  double totalTime = 0.;
  std::vector<std::array<double,kDimension>> centre;
  std::vector<std::array<double,kDimension>> derivativeV;
};

GenericSeed loadGenericSeed(const std::string& path, std::int64_t offset,
                            int segments) {
  std::ifstream input(path);
  if(!input) throw std::runtime_error("cannot open coarse seed file");
  input.seekg(offset);
  if(!input) throw std::runtime_error("cannot seek coarse seed file");
  GenericSeed result;
  result.centre.resize(segments + 1);
  result.derivativeV.resize(segments + 1);
  input >> result.sourceV >> result.sourceU >> result.totalTime;
  for(int nodeIndex = 0; nodeIndex <= segments; ++nodeIndex)
    for(int component = 0; component < kDimension; ++component)
      input >> result.centre[nodeIndex][component];
  for(int nodeIndex = 0; nodeIndex <= segments; ++nodeIndex)
    for(int component = 0; component < kDimension; ++component)
      input >> result.derivativeV[nodeIndex][component];
  if(!input) throw std::runtime_error("malformed coarse seed file");
  return result;
}

int column(int node, int component) {
  return kDimension * node + component;
}

double absUpper(const interval& value) {
  return std::max(std::abs(value.leftBound()), std::abs(value.rightBound()));
}

IVector node(const IVector& all, int index) {
  IVector result(kDimension);
  for(int component = 0; component < kDimension; ++component)
    result[component] = all[column(index, component)];
  return result;
}

IVector centreVector() {
  IVector result(kUnknowns);
  for(int n = 0; n <= kSegments; ++n)
    for(int component = 0; component < kDimension; ++component)
      result[column(n, component)] = seedCentre(n, component);
  return result;
}

double baseRadius(int nodeIndex, int component) {
  const double x = static_cast<double>(nodeIndex) / kSegments;
  switch(component) {
    case 0: return 3e-8 + 3e-7 * std::pow(x, 6);
    case 1: return 3e-8 + 2e-6 * std::pow(x, 8);
    case 2: return 3e-8 + 6e-6 * std::pow(x, 5);
    case 3: return 3e-8 + 2e-6 * std::pow(x, 5);
    case 4: return 2e-7;
  }
  throw std::runtime_error("invalid component");
}

double centreEnergyDerivativeV() {
  const double U = seedCentre(0, 0);
  const double V = seedCentre(0, 2);
  const double dU = seedDerivativeV(0, 0);
  return (-2. * U * U - 2. * V) * dU - 2. * U;
}

double centreRadiusDerivativeV() {
  const double U = seedCentre(0, 0);
  const double V = seedCentre(0, 2);
  const double dU = seedDerivativeV(0, 0);
  const double radius = std::hypot(U, V);
  if(!(radius > 0.))
    throw std::runtime_error("radius chart is singular at the origin");
  return (U * dU + V) / radius;
}

double parameterTangentAt(int nodeIndex, int component) {
  const double derivativeV = seedDerivativeV(nodeIndex, component);
  if(gSeedTangentKind == "active") return derivativeV;
  if(gParameter == "v") return derivativeV;
  if(gParameter == "u") {
    const double sourceUDerivative = seedDerivativeV(0, 0);
    if(std::abs(sourceUDerivative) < 1e-3)
      throw std::runtime_error("u chart too close to a source-U turn");
    return derivativeV / sourceUDerivative;
  }
  if(gParameter == "radius") {
    const double radiusDerivative = centreRadiusDerivativeV();
    if(std::abs(radiusDerivative) < 1e-3)
      throw std::runtime_error("radius chart too close to a radial turn");
    return derivativeV / radiusDerivative;
  }
  const double energyDerivative = centreEnergyDerivativeV();
  if(std::abs(energyDerivative) < 1e-5)
    throw std::runtime_error("energy chart too close to an energy fold");
  return derivativeV / energyDerivative;
}

double sourceParameterCentre() {
  if(gParameter == "v") return seedSourceV();
  if(gParameter == "u") return seedCentre(0, 0);
  if(gParameter == "radius")
    return std::hypot(seedCentre(0, 0), seedCentre(0, 2));
  const double U = seedCentre(0, 0);
  const double V = seedCentre(0, 2);
  return -2. * U * U * U / 3. - 2. * U * V;
}

double radiusAt(int nodeIndex, int component) {
  const double derivative = parameterTangentAt(nodeIndex, component);
  const double tangentTube = 1.35 * gHalfWidth
    * std::abs(derivative);
  return gRadiusScale * (baseRadius(nodeIndex, component) + tangentTube);
}

double tangentRadiusAt(int nodeIndex, int component) {
  return .5 * (1. + std::abs(parameterTangentAt(nodeIndex, component)));
}

double genericParameterTangentAt(const GenericSeed& seed,
                                 const std::string& chart,
                                 int nodeIndex, int component) {
  const double derivativeV = seed.derivativeV[nodeIndex][component];
  if(chart == "v") return derivativeV;
  if(chart == "u") {
    const double dU = seed.derivativeV[0][0];
    if(std::abs(dU) < 1e-3)
      throw std::runtime_error("coarse U chart is singular");
    return derivativeV / dU;
  }
  if(chart == "radius") {
    const double U = seed.centre[0][0];
    const double V = seed.centre[0][2];
    const double radius = std::hypot(U, V);
    const double dRadius = (U * seed.derivativeV[0][0] + V) / radius;
    if(std::abs(dRadius) < 1e-3)
      throw std::runtime_error("coarse radius chart is singular");
    return derivativeV / dRadius;
  }
  const double U = seed.centre[0][0];
  const double V = seed.centre[0][2];
  const double dU = seed.derivativeV[0][0];
  const double dEnergy = (-2. * U * U - 2. * V) * dU - 2. * U;
  if(std::abs(dEnergy) < 1e-5)
    throw std::runtime_error("coarse energy chart is singular");
  return derivativeV / dEnergy;
}

double genericRadiusAt(const GenericSeed& seed, const std::string& chart,
                       double halfWidth, double radiusScale,
                       int nodeIndex, int component) {
  const double tangentTube = 1.35 * halfWidth * std::abs(
    genericParameterTangentAt(seed, chart, nodeIndex, component));
  const double x = static_cast<double>(nodeIndex) /
    static_cast<double>(seed.centre.size() - 1);
  double base = 0.;
  switch(component) {
    case 0: base = 3e-8 + 3e-7 * std::pow(x, 6); break;
    case 1: base = 3e-8 + 2e-6 * std::pow(x, 8); break;
    case 2: base = 3e-8 + 6e-6 * std::pow(x, 5); break;
    case 3: base = 3e-8 + 2e-6 * std::pow(x, 5); break;
    case 4: base = 2e-7; break;
    default: throw std::runtime_error("invalid generic seed component");
  }
  return radiusScale * (base + tangentTube);
}

IVector boxAround(const IVector& centre) {
  IVector result(kUnknowns);
  for(int i = 0; i < kUnknowns; ++i) {
    const double midpoint = centre[i].mid().leftBound();
    const double radius = radiusAt(i / kDimension, i % kDimension);
    result[i] = interval(midpoint - radius, midpoint + radius);
  }
  return result;
}

struct Jet5 {
  interval value;
  std::array<interval,5> gradient;

  Jet5() : value(0.) { gradient.fill(interval(0.)); }
  Jet5(int x) : value(x) { gradient.fill(interval(0.)); }
  Jet5(long x) : value(static_cast<double>(x)) { gradient.fill(interval(0.)); }
  Jet5(long long x) : value(static_cast<double>(x)) { gradient.fill(interval(0.)); }
  Jet5(double x) : value(x) { gradient.fill(interval(0.)); }
  Jet5(const interval& x) : value(x) { gradient.fill(interval(0.)); }

  static Jet5 variable(const interval& x, int index) {
    Jet5 result(x);
    result.gradient[index] = 1.;
    return result;
  }
  Jet5& operator+=(const Jet5& other) {
    value += other.value;
    for(int i = 0; i < 5; ++i) gradient[i] += other.gradient[i];
    return *this;
  }
  Jet5& operator-=(const Jet5& other) {
    value -= other.value;
    for(int i = 0; i < 5; ++i) gradient[i] -= other.gradient[i];
    return *this;
  }
};

Jet5 operator+(Jet5 left, const Jet5& right) { return left += right; }
Jet5 operator-(Jet5 left, const Jet5& right) { return left -= right; }
Jet5 operator-(const Jet5& x) {
  Jet5 result;
  result.value = -x.value;
  for(int i = 0; i < 5; ++i) result.gradient[i] = -x.gradient[i];
  return result;
}
Jet5 operator*(const Jet5& x, const Jet5& y) {
  Jet5 result;
  result.value = x.value * y.value;
  for(int i = 0; i < 5; ++i)
    result.gradient[i] = x.gradient[i] * y.value
      + x.value * y.gradient[i];
  return result;
}
Jet5 reciprocal(const Jet5& x) {
  Jet5 result;
  result.value = interval(1.) / x.value;
  for(int i = 0; i < 5; ++i)
    result.gradient[i] = -x.gradient[i] / sqr(x.value);
  return result;
}
Jet5 operator/(const Jet5& x, const Jet5& y) { return x * reciprocal(y); }
Jet5 sqrt(const Jet5& x) {
  using std::sqrt;
  Jet5 result;
  result.value = sqrt(x.value);
  for(int i = 0; i < 5; ++i)
    result.gradient[i] = x.gradient[i] / (interval(2.) * result.value);
  return result;
}

struct TargetCoordinates {
  Jet5 residual;
  std::array<Jet5,3> base;
  Jet5 e;
};

TargetCoordinates targetCoordinates(const IVector& z) {
  const Jet5 U = Jet5::variable(z[0], 0);
  const Jet5 P = Jet5::variable(z[1], 1);
  const Jet5 V = Jet5::variable(z[2], 2);
  const Jet5 Q = Jet5::variable(z[3], 3);
  const Jet5 e = -Jet5(1) / U;
  const Jet5 e32 = e * sqrt(e);
  const Jet5 p = P * e32;
  const Jet5 q = Q * e32;
  const Jet5 omega = Jet5(1) + V * e * e;
  const Jet5 d = q + Jet5(2) / sqrt(Jet5(3));
  const Jet5 c = d - sqrt(Jet5(3)) * omega / Jet5(2);
  return {p - papera_tail::h7(e, d, omega), {e, c, omega}, e};
}

interval eighthPower(interval e) {
  interval e2 = e * e;
  interval e4 = e2 * e2;
  return e4 * e4;
}

struct TargetRow {
  interval value;
  std::array<interval,5> gradient;
};

TargetRow targetRow(const IVector& point, const IVector& box) {
  const TargetCoordinates p = targetCoordinates(point);
  const TargetCoordinates z = targetCoordinates(box);
  TargetRow result;
  const double etaBound = 2. * absUpper(eighthPower(z.e.value));
  result.value = p.residual.value + interval(-etaBound, etaBound);
  const interval slope(-kTargetSlopeError, kTargetSlopeError);
  for(int i = 0; i < 5; ++i) {
    result.gradient[i] = z.residual.gradient[i];
    for(int base = 0; base < 3; ++base)
      result.gradient[i] -= slope * z.base[base].gradient[i];
  }
  return result;
}

struct PhysicalContract {
  interval e, a, b, graphEnergy;
};

PhysicalContract terminalPhysicalContract(const IVector& terminalBox) {
  const interval e = -interval(1.) / terminalBox[0];
  const interval e32 = e * sqrt(e);
  const interval d = terminalBox[3] * e32
    + interval(2.) / sqrt(interval(3.));
  const interval omega = interval(1.) + terminalBox[2] * e * e;
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
  {
    std::ostringstream message;
    message << "terminal X leaves signed physical corridor: e=" << e
      << " a=" << a << " b=" << b << " E=" << graphEnergy;
    throw std::runtime_error(message.str());
  }
  return {e, a, b, graphEnergy};
}

bool verifyFirstEvent(IMap& field, const IVector& root) {
  IOdeSolver solver(field, 25);
  solver.setAbsoluteTolerance(1e-14);
  solver.setRelativeTolerance(1e-14);
  const double sectionU = -1. / kSectionE;
  for(int segment = 0; segment < kSegments; ++segment) {
    ITimeMap timeMap(solver);
    timeMap.stopAfterStep(true);
    C0HORect2Set set(node(root, segment));
    do {
      timeMap(interval(kStep), set);
      const IVector enclosure = set.getLastEnclosure();
      if(segment + 1 < kSegments) {
        if(!(enclosure[0].leftBound() > sectionU)) return false;
      } else {
        if(!(enclosure[1].rightBound() < 0.)) return false;
      }
    } while(!timeMap.completed());
  }
  return true;
}

void parseArguments(int argc, char** argv) {
  for(int i = 1; i < argc; ++i) {
    const std::string arg(argv[i]);
    if(arg == "--half-width" && i + 1 < argc) gHalfWidth = std::stod(argv[++i]);
    else if(arg == "--radius-scale" && i + 1 < argc) gRadiusScale = std::stod(argv[++i]);
    else if(arg == "--parameter" && i + 1 < argc) gParameter = argv[++i];
    else if(arg == "--seed-tangent-kind" && i + 1 < argc)
      gSeedTangentKind = argv[++i];
    else if(arg == "--seed-file" && i + 1 < argc) gSeedFile = argv[++i];
    else if(arg == "--seed-offset" && i + 1 < argc)
      gSeedOffset = std::stoll(argv[++i]);
    else if(arg == "--bridge-seed-file" && i + 1 < argc) {
      gBridgeSeedFile = argv[++i];
      gDoBridge = true;
    }
    else if(arg == "--bridge-seed-offset" && i + 1 < argc)
      gBridgeSeedOffset = std::stoll(argv[++i]);
    else if(arg == "--bridge-chart" && i + 1 < argc)
      gBridgeChart = argv[++i];
    else if(arg == "--bridge-half-width" && i + 1 < argc)
      gBridgeHalfWidth = std::stod(argv[++i]);
    else if(arg == "--bridge-parameter" && i + 1 < argc)
      gBridgeParameter = std::stod(argv[++i]);
    else if(arg == "--coarse-seed-file" && i + 1 < argc) {
      gCoarseSeedFile = argv[++i];
      gDoCoarseContainment = true;
    }
    else if(arg == "--coarse-seed-offset" && i + 1 < argc)
      gCoarseSeedOffset = std::stoll(argv[++i]);
    else if(arg == "--coarse-segments" && i + 1 < argc)
      gCoarseSegments = std::stoi(argv[++i]);
    else if(arg == "--coarse-chart" && i + 1 < argc)
      gCoarseChart = argv[++i];
    else if(arg == "--coarse-half-width" && i + 1 < argc)
      gCoarseHalfWidth = std::stod(argv[++i]);
    else if(arg == "--coarse-radius-scale" && i + 1 < argc)
      gCoarseRadiusScale = std::stod(argv[++i]);
    else if(arg == "--fixed-radial-seam-containment")
      gDoFixedRadialSeamContainment = true;
    else throw std::runtime_error("usage: source_cover_probe --seed-file PATH --seed-offset N [--parameter v|u|radius|energy] [--half-width H] [--radius-scale S]");
  }
  if(!gSeedFile.empty()) loadRuntimeSeed(gSeedFile);
  if(!gUseRuntimeSeed)
    throw std::runtime_error("--seed-file is required");
  if(!(gHalfWidth > 0.) || !(gRadiusScale > 0.))
    throw std::runtime_error("width and radius scale must be positive");
  if(gSeedOffset < 0) throw std::runtime_error("seed offset must be nonnegative");
  if(gParameter != "v" && gParameter != "u"
     && gParameter != "radius" && gParameter != "energy")
    throw std::runtime_error("parameter must be v, u, radius, or energy");
  if(gSeedTangentKind != "v" && gSeedTangentKind != "active")
    throw std::runtime_error("seed tangent kind must be v or active");
  if(gDoBridge) {
    if(gBridgeSeedFile.empty() || gBridgeSeedOffset < 0
       || !(gBridgeHalfWidth > 0.))
      throw std::runtime_error("incomplete bridge arguments");
    if(gBridgeChart != "v" && gBridgeChart != "u"
       && gBridgeChart != "radius" && gBridgeChart != "energy")
      throw std::runtime_error("invalid bridge chart");
  }
  if(gDoCoarseContainment) {
    if(gCoarseSeedFile.empty() || gCoarseSeedOffset < 0
       || gCoarseSegments <= 0 || kSegments % gCoarseSegments
       || !(gCoarseHalfWidth > 0.) || !(gCoarseRadiusScale > 0.))
      throw std::runtime_error("incomplete or incompatible coarse containment arguments");
    if(gCoarseChart != "v" && gCoarseChart != "u"
       && gCoarseChart != "radius" && gCoarseChart != "energy")
      throw std::runtime_error("invalid coarse chart");
  }
  if(gDoFixedRadialSeamContainment && gParameter != "radius")
    throw std::runtime_error("fixed radial seam containment requires radius chart");
}

interval sourceParameterValue(const IVector& source, const std::string& chart) {
  if(chart == "v") return source[2];
  if(chart == "u") return source[0];
  if(chart == "radius") return sqrt(sqr(source[0]) + sqr(source[2]));
  return -interval(2.) * source[0] * source[0] * source[0] / interval(3.)
    - interval(2.) * source[0] * source[2];
}

} // namespace

int main(int argc, char** argv) {
  try {
    parseArguments(argc, argv);
    const double parameterCentre = sourceParameterCentre();
    const interval sourceParameter(
      parameterCentre - gHalfWidth, parameterCentre + gHalfWidth);
    const IVector centre = centreVector();
    const IVector X = boxAround(centre);
    const PhysicalContract physical = terminalPhysicalContract(node(X, kSegments));

    IMap field("var:U,P,V,Q,T;fun:T*P,T*(-U*U-V),T*Q,T*U,0;");
    IOdeSolver solver(field, 25);
    solver.setAbsoluteTolerance(1e-14);
    solver.setRelativeTolerance(1e-14);

    IVector residual(kUnknowns);
    IMatrix derivative(kUnknowns, kUnknowns);
    derivative.clear();
    double residualSup = 0.;
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
      for(int output = 0; output < kDimension; ++output) {
        const int row = kDimension * segment + output;
        residual[row] = nextCentre[output] - imageCentre[output];
        residualSup = std::max(residualSup, absUpper(residual[row]));
        for(int input = 0; input < kDimension; ++input)
          derivative[row][column(segment, input)] = -monodromy[output][input];
        derivative[row][column(segment + 1, output)] += 1.;
      }
    }

    int row = kDimension * kSegments;
    const IVector sourcePoint = node(centre, 0);
    const IVector sourceBox = node(X, 0);
    residual[row] = sourcePoint[1];
    derivative[row][column(0, 1)] = 1.;
    ++row;
    residual[row] = sourcePoint[3];
    derivative[row][column(0, 3)] = 1.;
    ++row;
    if(gParameter == "v") {
      residual[row] = sourcePoint[2] - sourceParameter;
      derivative[row][column(0, 2)] = 1.;
    } else if(gParameter == "u") {
      residual[row] = sourcePoint[0] - sourceParameter;
      derivative[row][column(0, 0)] = 1.;
    } else if(gParameter == "radius") {
      residual[row] = sqrt(sqr(sourcePoint[0]) + sqr(sourcePoint[2]))
        - sourceParameter;
      const interval sourceRadius = sqrt(
        sqr(sourceBox[0]) + sqr(sourceBox[2]));
      derivative[row][column(0, 0)] = sourceBox[0] / sourceRadius;
      derivative[row][column(0, 2)] = sourceBox[2] / sourceRadius;
    } else {
      residual[row] = -interval(2.) * sourcePoint[0] * sourcePoint[0]
        * sourcePoint[0] / interval(3.)
        - interval(2.) * sourcePoint[0] * sourcePoint[2]
        - sourceParameter;
      derivative[row][column(0, 0)] =
        -interval(2.) * sqr(sourceBox[0]) - interval(2.) * sourceBox[2];
      derivative[row][column(0, 2)] = -interval(2.) * sourceBox[0];
    }
    ++row;

    const IVector terminalPoint = node(centre, kSegments);
    const IVector terminalBox = node(X, kSegments);
    residual[row] = -interval(1.) / terminalPoint[0] - interval(kSectionE);
    derivative[row][column(kSegments, 0)] = interval(1.) / sqr(terminalBox[0]);
    ++row;
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
    const DMatrix doubleInverse = matrixAlgorithms::inverseMatrix(midpoint);
    IMatrix preconditioner(kUnknowns, kUnknowns);
    for(int i = 0; i < kUnknowns; ++i)
      for(int j = 0; j < kUnknowns; ++j)
        preconditioner[i][j] = doubleInverse[i][j];
    const IMatrix remainder = IMatrix::Identity(kUnknowns)
      - preconditioner * derivative;
    const IVector contractionImage = remainder * (X - centre);
    const IVector krawczyk = centre - preconditioner * residual
      + contractionImage;

    double ratio = 0.;
    double contractionRatio = 0.;
    int worst = -1;
    for(int i = 0; i < kUnknowns; ++i) {
      const double midpointValue = centre[i].mid().leftBound();
      const double correction = std::max(
        std::abs(krawczyk[i].leftBound() - midpointValue),
        std::abs(krawczyk[i].rightBound() - midpointValue));
      const double radius = radiusAt(i / kDimension, i % kDimension);
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
      throw std::runtime_error("Krawczyk inclusion failed");
    }

    bool coarseContainmentCertified = false;
    double coarseContainmentMargin = 0.;
    if(gDoCoarseContainment) {
      const GenericSeed coarse = loadGenericSeed(
        gCoarseSeedFile, gCoarseSeedOffset, gCoarseSegments);
      const int stride = kSegments / gCoarseSegments;
      coarseContainmentMargin = std::numeric_limits<double>::infinity();
      for(int coarseNode = 0; coarseNode <= gCoarseSegments; ++coarseNode) {
        const int fineNode = stride * coarseNode;
        for(int component = 0; component < kDimension; ++component) {
          const double radius = genericRadiusAt(
            coarse, gCoarseChart, gCoarseHalfWidth, gCoarseRadiusScale,
            coarseNode, component);
          const double centreValue = coarse.centre[coarseNode][component];
          const interval coarseBox(centreValue - radius, centreValue + radius);
          const interval fineRoot = krawczyk[column(fineNode, component)];
          if(!subsetInterior(fineRoot, coarseBox))
            throw std::runtime_error(
              "fine root is not contained in coarse endpoint uniqueness box");
          coarseContainmentMargin = std::min({
            coarseContainmentMargin,
            fineRoot.leftBound() - coarseBox.leftBound(),
            coarseBox.rightBound() - fineRoot.rightBound()
          });
        }
      }
      coarseContainmentCertified = true;
    }

    bool fixedRadialSeamContainmentCertified = false;
    double fixedRadialSeamContainmentMargin = 0.;
    if(gDoFixedRadialSeamContainment) {
      using namespace papera_fixed_radial_source_centres;
      fixedRadialSeamContainmentMargin =
        std::numeric_limits<double>::infinity();
      for(int component = 0; component < 4; ++component) {
        const double seamRadius = 2e-9 + 1.35e-12
          * std::abs(kDerivative[0][component]);
        const interval seamBox(
          kCentre[0][component] - seamRadius,
          kCentre[0][component] + seamRadius);
        const interval fineRoot = krawczyk[column(0, component)];
        if(!subsetInterior(fineRoot, seamBox))
          throw std::runtime_error(
            "event root source is not contained in fixed radial seam box");
        fixedRadialSeamContainmentMargin = std::min({
          fixedRadialSeamContainmentMargin,
          fineRoot.leftBound() - seamBox.leftBound(),
          seamBox.rightBound() - fineRoot.rightBound()
        });
      }
      const interval seamParameter(kRadius - 1e-12, kRadius + 1e-12);
      if(sourceParameter.leftBound() < seamParameter.leftBound()
         || sourceParameter.rightBound() > seamParameter.rightBound())
        throw std::runtime_error(
          "event radius parameter is not inside fixed radial seam parameter box");
      fixedRadialSeamContainmentCertified = true;
    }

    bool bridgeCertified = false;
    double bridgeCurrentContainmentMargin = 0.;
    double bridgeNextContainmentMargin = 0.;
    double bridgeNextParameterMargin = 0.;
    interval bridgeNextParameter(0.);
    IVector bridgeKrawczyk(kUnknowns);
    if(gDoBridge) {
      const int parameterRow = kDimension * kSegments + 2;
      IVector bridgeResidual = residual;
      bridgeResidual[parameterRow] =
        sourceParameterValue(sourcePoint, gParameter) - interval(gBridgeParameter);
      bridgeKrawczyk = centre - preconditioner * bridgeResidual
        + contractionImage;
      if(!subsetInterior(bridgeKrawczyk, X))
        throw std::runtime_error("bridge point root leaves current uniqueness box");
      bridgeCurrentContainmentMargin =
        std::numeric_limits<double>::infinity();
      for(int i = 0; i < kUnknowns; ++i)
        bridgeCurrentContainmentMargin = std::min({
          bridgeCurrentContainmentMargin,
          bridgeKrawczyk[i].leftBound() - X[i].leftBound(),
          X[i].rightBound() - bridgeKrawczyk[i].rightBound()
        });

      const RuntimeSeed savedSeed = gRuntimeSeed;
      const bool savedUseRuntime = gUseRuntimeSeed;
      const std::int64_t savedOffset = gSeedOffset;
      const std::string savedChart = gParameter;
      const double savedHalfWidth = gHalfWidth;
      gSeedOffset = gBridgeSeedOffset;
      loadRuntimeSeed(gBridgeSeedFile);
      gParameter = gBridgeChart;
      gHalfWidth = gBridgeHalfWidth;
      const IVector nextCentre = centreVector();
      const IVector nextX = boxAround(nextCentre);
      const double nextParameterCentre = sourceParameterCentre();
      bridgeNextParameter = interval(
        nextParameterCentre - gBridgeHalfWidth,
        nextParameterCentre + gBridgeHalfWidth);
      gRuntimeSeed = savedSeed;
      gUseRuntimeSeed = savedUseRuntime;
      gSeedOffset = savedOffset;
      gParameter = savedChart;
      gHalfWidth = savedHalfWidth;

      if(!subsetInterior(bridgeKrawczyk, nextX))
        throw std::runtime_error("bridge root enclosure not contained in next uniqueness box");
      bridgeNextContainmentMargin =
        std::numeric_limits<double>::infinity();
      for(int i = 0; i < kUnknowns; ++i)
        bridgeNextContainmentMargin = std::min({
          bridgeNextContainmentMargin,
          bridgeKrawczyk[i].leftBound() - nextX[i].leftBound(),
          nextX[i].rightBound() - bridgeKrawczyk[i].rightBound()
        });
      const interval selectedNextParameter = sourceParameterValue(
        node(bridgeKrawczyk, 0), gBridgeChart);
      if(!subsetInterior(selectedNextParameter, bridgeNextParameter))
        throw std::runtime_error("bridge root parameter not inside next parameter interval");
      bridgeNextParameterMargin = std::min(
        selectedNextParameter.leftBound() - bridgeNextParameter.leftBound(),
        bridgeNextParameter.rightBound() - selectedNextParameter.rightBound());
      bridgeCertified = true;
    }

    // Uniformly enclose dx/dlambda from J(x,lambda) x_lambda = -F_lambda.
    // Only the active source equation depends explicitly on lambda, so
    // -F_lambda is the unit vector in that row.  This is not needed for
    // existence, but it supplies a rigorous tangent diagnostic on every
    // regular chart box.
    IVector tangentCentre(kUnknowns), tangentBox(kUnknowns), tangentRhs(kUnknowns);
    std::array<double,kUnknowns> tangentRadii{};
    tangentRhs.clear();
    tangentRhs[kDimension * kSegments + 2] = 1.;
    for(int i = 0; i < kUnknowns; ++i) {
      const int tangentNode = i / kDimension;
      const int tangentComponent = i % kDimension;
      const double value = parameterTangentAt(tangentNode, tangentComponent);
      const double radius = tangentRadiusAt(tangentNode, tangentComponent);
      tangentCentre[i] = value;
      tangentRadii[i] = radius;
      tangentBox[i] = interval(value - radius, value + radius);
    }
    const IVector tangentResidual = derivative * tangentCentre - tangentRhs;
    const IVector tangentCorrection = -preconditioner * tangentResidual;
    IVector tangentKrawczyk = tangentCentre + tangentCorrection
      + remainder * (tangentBox - tangentCentre);
    bool tangentUsedScaledPrimalRadii = false;
    double tangentPrimalScale = 0.;
    if(!subsetInterior(tangentKrawczyk, tangentBox)) {
      // The same interval Jacobian controls both the root and tangent
      // equations.  When the heuristic relative tangent box wraps badly,
      // use a scaled copy of the already contracting primal radii.  If
      // |R|r < r componentwise, choosing
      //   scale > |C residual| / (r-|R|r)
      // gives a strict tangent Krawczyk inclusion by construction.
      IVector primalRadiusBox(kUnknowns);
      for(int i = 0; i < kUnknowns; ++i) {
        const double radius = radiusAt(i / kDimension, i % kDimension);
        primalRadiusBox[i] = interval(-radius, radius);
      }
      const IVector unitImage = remainder * primalRadiusBox;
      tangentPrimalScale = 1.;
      for(int i = 0; i < kUnknowns; ++i) {
        const double primalRadius = radiusAt(i / kDimension, i % kDimension);
        const double margin = primalRadius - absUpper(unitImage[i]);
        if(!(margin > 0.))
          throw std::runtime_error("no componentwise tangent radius margin");
        tangentPrimalScale = std::max(
          tangentPrimalScale, 1.02 * absUpper(tangentCorrection[i]) / margin);
      }
      for(int i = 0; i < kUnknowns; ++i) {
        const double value = tangentCentre[i].mid().leftBound();
        tangentRadii[i] = tangentPrimalScale
          * radiusAt(i / kDimension, i % kDimension);
        tangentBox[i] = interval(
          value - tangentRadii[i], value + tangentRadii[i]);
      }
      tangentKrawczyk = tangentCentre + tangentCorrection
        + remainder * (tangentBox - tangentCentre);
      tangentUsedScaledPrimalRadii = true;
    }
    double tangentRatio = 0.;
    for(int i = 0; i < kUnknowns; ++i) {
      const double value = tangentCentre[i].mid().leftBound();
      const double correction = std::max(
        std::abs(tangentKrawczyk[i].leftBound() - value),
        std::abs(tangentKrawczyk[i].rightBound() - value));
      tangentRatio = std::max(
        tangentRatio, correction / tangentRadii[i]);
    }
    const bool tangentCertified = subsetInterior(tangentKrawczyk, tangentBox);

    const bool firstEvent = verifyFirstEvent(field, krawczyk);
    if(!firstEvent) throw std::runtime_error("first-event enclosure failed");

    const IVector sourceRoot = node(krawczyk, 0);
    const interval sourceRadius = sqrt(sqr(sourceRoot[0]) + sqr(sourceRoot[2]));
    const interval sourceEnergy = -interval(2.) * sourceRoot[0] * sourceRoot[0]
      * sourceRoot[0] / interval(3.)
      - interval(2.) * sourceRoot[0] * sourceRoot[2];
    interval sourceUprime(0.), sourceEnergyPrime(0.);
    if(tangentCertified) {
      sourceUprime = tangentKrawczyk[0];
      sourceEnergyPrime =
        (-interval(2.) * sqr(sourceRoot[0])
         -interval(2.) * sourceRoot[2]) * sourceUprime
        -interval(2.) * sourceRoot[0] * tangentKrawczyk[2];
    }
    const IVector terminalRoot = node(krawczyk, kSegments);

    std::cout << std::setprecision(17)
      << "{\n"
      << "  \"status\": \"PASS-PARAMETRIC-SOURCE-COVER-BOX\",\n"
      << "  \"segments\": " << kSegments << ",\n"
      << "  \"unknowns\": " << kUnknowns << ",\n"
      << "  \"equations\": " << kUnknowns << ",\n"
      << "  \"parameter_kind\": \"" << gParameter << "\",\n"
      << "  \"source_parameter\": \"" << sourceParameter << "\",\n"
      << "  \"source_U\": \"" << sourceRoot[0] << "\",\n"
      << "  \"source_P\": \"" << sourceRoot[1] << "\",\n"
      << "  \"source_V\": \"" << sourceRoot[2] << "\",\n"
      << "  \"source_Q\": \"" << sourceRoot[3] << "\",\n"
      << "  \"source_radius\": \"" << sourceRadius << "\",\n"
      << "  \"source_energy\": \"" << sourceEnergy << "\",\n";
    if(tangentCertified)
      std::cout
        << "  \"d_source_U_dparameter\": \"" << sourceUprime << "\",\n"
        << "  \"d_source_energy_dparameter\": \"" << sourceEnergyPrime << "\",\n";
    else
      std::cout
        << "  \"d_source_U_dparameter\": null,\n"
        << "  \"d_source_energy_dparameter\": null,\n";
    std::cout
      << "  \"flight_time\": \"" << sourceRoot[4] << "\",\n"
      << "  \"terminal_U\": \"" << terminalRoot[0] << "\",\n"
      << "  \"terminal_e\": \"" << -interval(1.) / terminalRoot[0] << "\",\n"
      << "  \"terminal_X_physical_a\": \"" << physical.a << "\",\n"
      << "  \"terminal_X_physical_b\": \"" << physical.b << "\",\n"
      << "  \"terminal_X_graph_energy_abs_zeta_le_2\": \""
      << physical.graphEnergy << "\",\n"
      << "  \"target_graph_C0_budget\": \"2 e^8\",\n"
      << "  \"target_graph_C1_budget\": 1e-5,\n"
      << "  \"first_event\": true,\n"
      << "  \"residual_sup\": " << residualSup << ",\n"
      << "  \"krawczyk_ratio\": " << ratio << ",\n"
      << "  \"contraction_ratio\": " << contractionRatio << ",\n"
      << "  \"tangent_certified\": "
      << (tangentCertified ? "true" : "false") << ",\n"
      << "  \"tangent_krawczyk_ratio\": " << tangentRatio << ",\n"
      << "  \"tangent_radius_mode\": \""
      << (tangentUsedScaledPrimalRadii ? "scaled-primal" : "relative")
      << "\",\n"
      << "  \"tangent_primal_scale\": " << tangentPrimalScale << ",\n"
      << "  \"adjacent_bridge_certified\": "
      << (bridgeCertified ? "true" : "false") << ",\n";
    if(bridgeCertified)
      std::cout
        << "  \"bridge_parameter\": " << gBridgeParameter << ",\n"
        << "  \"bridge_next_parameter_interval\": \""
        << bridgeNextParameter << "\",\n"
        << "  \"bridge_current_containment_margin\": "
        << bridgeCurrentContainmentMargin << ",\n"
        << "  \"bridge_next_containment_margin\": "
        << bridgeNextContainmentMargin << ",\n"
        << "  \"bridge_next_parameter_margin\": "
        << bridgeNextParameterMargin << ",\n";
    std::cout
      << "  \"coarse_endpoint_containment_certified\": "
      << (coarseContainmentCertified ? "true" : "false") << ",\n"
      << "  \"coarse_endpoint_containment_margin\": "
      << coarseContainmentMargin << ",\n"
      << "  \"fixed_radial_seam_source_containment_certified\": "
      << (fixedRadialSeamContainmentCertified ? "true" : "false") << ",\n"
      << "  \"fixed_radial_seam_source_containment_margin\": "
      << fixedRadialSeamContainmentMargin << ",\n"
      << "  \"worst_node\": " << worst / kDimension << ",\n"
      << "  \"worst_component\": " << worst % kDimension << "\n"
      << "}\n";
    return 0;
  } catch(const std::exception& error) {
    std::cerr << "EXCEPTION: " << error.what() << "\n";
    return 12;
  }
}
