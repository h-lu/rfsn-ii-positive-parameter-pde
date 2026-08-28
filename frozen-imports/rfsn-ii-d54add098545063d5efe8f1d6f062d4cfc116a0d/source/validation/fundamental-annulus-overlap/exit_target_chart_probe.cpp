#include <algorithm>
#include <array>
#include <cmath>
#include <cstdlib>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <cstdint>
#include <sstream>
#include <stdexcept>
#include <string>

#include "capd/capdlib.h"
#include "exit_target_centres.hpp"
#include "../future-target-fold/tail_graph_generated.hpp"
#include "../future-target-fold/weighted_tail_generated.hpp"

using namespace capd;

namespace {

constexpr int kSegments = papera_exit_target_centres::kSegments;
constexpr int kDimension = 5;
constexpr int kUnknowns = kDimension * (kSegments + 1);
constexpr double kStep = 1.0 / kSegments;
constexpr double kSectionE = .0575;
constexpr double kTargetSlopeError = 1e-5;

double gStableHalfWidth = 1e-5;
double gRadiusScale = 1.;

double seedCentre(int nodeIndex, int component) {
  return papera_exit_target_centres::kCentre[nodeIndex][component];
}

double seedTangent(int parameter, int nodeIndex, int component) {
  return parameter == 0
    ? papera_exit_target_centres::kDs1[nodeIndex][component]
    : papera_exit_target_centres::kDs2[nodeIndex][component];
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

struct HyperbolicCoordinates {
  interval u1, u2, s1, s2;
  std::array<interval,5> du1, du2, ds1, ds2;
};

HyperbolicCoordinates hyperbolicCoordinates(const IVector& z) {
  const interval c = interval(1.) / sqrt(interval(2.));
  HyperbolicCoordinates result;
  result.u1 = (z[0] + c * (z[1] + z[3])) / interval(2.);
  result.s1 = (z[0] - c * (z[1] + z[3])) / interval(2.);
  result.u2 = (z[2] + c * (z[3] - z[1])) / interval(2.);
  result.s2 = (z[2] - c * (z[3] - z[1])) / interval(2.);
  result.du1 = {interval(.5), c / interval(2.), interval(0.), c / interval(2.), interval(0.)};
  result.ds1 = {interval(.5), -c / interval(2.), interval(0.), -c / interval(2.), interval(0.)};
  result.du2 = {interval(0.), -c / interval(2.), interval(.5), c / interval(2.), interval(0.)};
  result.ds2 = {interval(0.), c / interval(2.), interval(.5), -c / interval(2.), interval(0.)};
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
    case 0: return 2e-9 + 5e-7 * std::pow(x, 6);
    case 1: return 2e-9 + 2e-6 * std::pow(x, 8);
    case 2: return 2e-9 + 8e-6 * std::pow(x, 5);
    case 3: return 2e-9 + 2e-6 * std::pow(x, 5);
    case 4: return 2e-7;
  }
  throw std::runtime_error("invalid component");
}

double radiusAt(int nodeIndex, int component) {
  const double tangentTube = 1.35 * gStableHalfWidth
    * (std::abs(seedTangent(0, nodeIndex, component))
       + std::abs(seedTangent(1, nodeIndex, component)));
  return gRadiusScale * (baseRadius(nodeIndex, component) + tangentTube);
}

double tangentRadiusAt(int parameter, int nodeIndex, int component) {
  return .5 * (1. + std::abs(seedTangent(parameter, nodeIndex, component)));
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
    if(arg == "--stable-half-width" && i + 1 < argc)
      gStableHalfWidth = std::stod(argv[++i]);
    else if(arg == "--radius-scale" && i + 1 < argc) gRadiusScale = std::stod(argv[++i]);
    else throw std::runtime_error(
      "usage: exit_target_chart_probe [--stable-half-width H] [--radius-scale S]");
  }
  if(!(gStableHalfWidth > 0.) || !(gRadiusScale > 0.))
    throw std::runtime_error("width and radius scale must be positive");
}

} // namespace

int main(int argc, char** argv) {
  try {
    parseArguments(argc, argv);
    const interval stableParameter1(
      papera_exit_target_centres::kStableCentre[0] - gStableHalfWidth,
      papera_exit_target_centres::kStableCentre[0] + gStableHalfWidth);
    const interval stableParameter2(
      papera_exit_target_centres::kStableCentre[1] - gStableHalfWidth,
      papera_exit_target_centres::kStableCentre[1] + gStableHalfWidth);
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
    const HyperbolicCoordinates source = hyperbolicCoordinates(sourcePoint);
    const HyperbolicCoordinates sourceDomain = hyperbolicCoordinates(sourceBox);
    residual[row] = sqr(source.u1) + sqr(source.u2) - interval(.0001);
    for(int component = 0; component < kDimension; ++component)
      derivative[row][column(0, component)] =
        interval(2.) * sourceDomain.u1 * sourceDomain.du1[component]
        + interval(2.) * sourceDomain.u2 * sourceDomain.du2[component];
    ++row;
    residual[row] = source.s1 - stableParameter1;
    for(int component = 0; component < kDimension; ++component)
      derivative[row][column(0, component)] = sourceDomain.ds1[component];
    ++row;
    residual[row] = source.s2 - stableParameter2;
    for(int component = 0; component < kDimension; ++component)
      derivative[row][column(0, component)] = sourceDomain.ds2[component];
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

    IVector tangentKrawczyk1(kUnknowns), tangentKrawczyk2(kUnknowns);
    auto certifyTangent = [&](int parameter, IVector& enclosure) {
      IVector tangentCentre(kUnknowns), tangentBox(kUnknowns), tangentRhs(kUnknowns);
      tangentRhs.clear();
      tangentRhs[kDimension * kSegments + 1 + parameter] = 1.;
      for(int i = 0; i < kUnknowns; ++i) {
        const int tangentNode = i / kDimension;
        const int tangentComponent = i % kDimension;
        const double value = seedTangent(parameter, tangentNode, tangentComponent);
        const double radius = tangentRadiusAt(
          parameter, tangentNode, tangentComponent);
        tangentCentre[i] = value;
        tangentBox[i] = interval(value - radius, value + radius);
      }
      const IVector tangentResidual = derivative * tangentCentre - tangentRhs;
      enclosure = tangentCentre - preconditioner * tangentResidual
        + remainder * (tangentBox - tangentCentre);
      double tangentRatio = 0.;
      for(int i = 0; i < kUnknowns; ++i) {
        const double value = tangentCentre[i].mid().leftBound();
        const double correction = std::max(
          std::abs(enclosure[i].leftBound() - value),
          std::abs(enclosure[i].rightBound() - value));
        tangentRatio = std::max(
          tangentRatio,
          correction / tangentRadiusAt(parameter, i / kDimension, i % kDimension));
      }
      if(!subsetInterior(enclosure, tangentBox))
        throw std::runtime_error("target-chart tangent inclusion failed");
      return tangentRatio;
    };
    const double tangentRatio1 = certifyTangent(0, tangentKrawczyk1);
    const double tangentRatio2 = certifyTangent(1, tangentKrawczyk2);

    const bool firstEvent = verifyFirstEvent(field, krawczyk);
    if(!firstEvent) throw std::runtime_error("first-event enclosure failed");

    const IVector sourceRoot = node(krawczyk, 0);
    const HyperbolicCoordinates exitRoot = hyperbolicCoordinates(sourceRoot);
    const interval exitPhase = interval(2.) * interval::pi()
      + atan(exitRoot.u2 / exitRoot.u1);
    const interval sourceRadius = sqrt(sqr(sourceRoot[0]) + sqr(sourceRoot[2]));
    const interval sourceEnergy = sqr(sourceRoot[3]) - sqr(sourceRoot[1])
      - interval(2.) * sourceRoot[0] * sourceRoot[0] * sourceRoot[0]
        / interval(3.)
      - interval(2.) * sourceRoot[0] * sourceRoot[2];
    const HyperbolicCoordinates tangent1 = hyperbolicCoordinates(
      node(tangentKrawczyk1, 0));
    const HyperbolicCoordinates tangent2 = hyperbolicCoordinates(
      node(tangentKrawczyk2, 0));
    const interval phaseDerivative1 =
      (exitRoot.u1 * tangent1.u2 - exitRoot.u2 * tangent1.u1)
      / (sqr(exitRoot.u1) + sqr(exitRoot.u2));
    const interval phaseDerivative2 =
      (exitRoot.u1 * tangent2.u2 - exitRoot.u2 * tangent2.u1)
      / (sqr(exitRoot.u1) + sqr(exitRoot.u2));
    auto energyDerivative = [&](const IVector& tangent) {
      return interval(2.) * sourceRoot[3] * tangent[3]
        - interval(2.) * sourceRoot[1] * tangent[1]
        + (-interval(2.) * sqr(sourceRoot[0])
           - interval(2.) * sourceRoot[2]) * tangent[0]
        - interval(2.) * sourceRoot[0] * tangent[2];
    };
    const interval energyDerivative1 = energyDerivative(
      node(tangentKrawczyk1, 0));
    const interval energyDerivative2 = energyDerivative(
      node(tangentKrawczyk2, 0));
    const IVector terminalRoot = node(krawczyk, kSegments);

    std::cout << std::setprecision(17)
      << "{\n"
      << "  \"status\": \"PASS-EXIT-TARGET-CHART\",\n"
      << "  \"segments\": " << kSegments << ",\n"
      << "  \"unknowns\": " << kUnknowns << ",\n"
      << "  \"equations\": " << kUnknowns << ",\n"
      << "  \"stable_parameter_half_width\": " << gStableHalfWidth << ",\n"
      << "  \"source_s1_parameter\": \"" << stableParameter1 << "\",\n"
      << "  \"source_s2_parameter\": \"" << stableParameter2 << "\",\n"
      << "  \"source_u1\": \"" << exitRoot.u1 << "\",\n"
      << "  \"source_u2\": \"" << exitRoot.u2 << "\",\n"
      << "  \"source_phase\": \"" << exitPhase << "\",\n"
      << "  \"source_s1\": \"" << exitRoot.s1 << "\",\n"
      << "  \"source_s2\": \"" << exitRoot.s2 << "\",\n"
      << "  \"source_energy\": \"" << sourceEnergy << "\",\n";
    std::cout
      << "  \"d_exit_phase_ds1\": \"" << phaseDerivative1 << "\",\n"
      << "  \"d_exit_phase_ds2\": \"" << phaseDerivative2 << "\",\n"
      << "  \"d_source_energy_ds1\": \""
      << energyDerivative1 << "\",\n"
      << "  \"d_source_energy_ds2\": \""
      << energyDerivative2 << "\",\n"
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
      << "  \"tangent_krawczyk_ratio_ds1\": " << tangentRatio1 << ",\n"
      << "  \"tangent_krawczyk_ratio_ds2\": " << tangentRatio2 << ",\n"
      << "  \"worst_node\": " << worst / kDimension << ",\n"
      << "  \"worst_component\": " << worst % kDimension << "\n"
      << "}\n";
    return 0;
  } catch(const std::exception& error) {
    std::cerr << "EXCEPTION: " << error.what() << "\n";
    return 12;
  }
}
