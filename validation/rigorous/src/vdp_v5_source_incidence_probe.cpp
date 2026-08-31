#include "interval_io.hpp"
#include "rounding_self_test.hpp"
#include "unstable_graph_terms.hpp"
#include "verdict.hpp"

#include <capd/capdlib.h>

#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
#include <exception>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

// Strict, zero-energy source-to-V5-lower-face incidence kernel.
//
// The exact H10+e source chart is propagated to its first U=-4 crossing.
// A slanted phase coordinate phi=Phi(mu)+theta-(11/8)e keeps the complete
// certified |e|<=5e-6 tube correlated with the narrow incidence strip.  The
// two e half-tubes are evaluated separately solely to control wrapping; their
// closed union is the complete tube.  Phi is a numerical polynomial used
// only to centre interval boxes.  Every asserted sign is recomputed by CAPD
// on the complete rational parameter cover and does not assume an error bound
// for that predictor.

using namespace capd;

namespace {

using rfsn::rigorous::Interval;
using rfsn::rigorous::Verdict;
using rfsn::rigorous::combine;
using rfsn::rigorous::intervalJson;
using rfsn::rigorous::verdictName;

struct PredictorTerm {
  int rPower;
  int aPower;
  int epsilonPower;
  const char* coefficient;
};

// Total-degree-four least-squares predictor on the disclosed 225-point
// design grid.  Decimal strings are parsed outward.  No fit residual enters
// a proof gate: the polynomial only chooses the centre of each phase face.
constexpr std::array<PredictorTerm, 35> kPredictor{{
    {0, 0, 0, "5.756767223225202"},
    {0, 0, 1, "7.579431512224715e-6"},
    {0, 0, 2, "-3.7886754079759785e-7"},
    {0, 0, 3, "4.092651123317211e-8"},
    {0, 0, 4, "-5.138544156985927e-9"},
    {0, 1, 0, "2.1646570250130368e-2"},
    {0, 1, 1, "3.16541224152404e-8"},
    {0, 1, 2, "-1.873847204973114e-9"},
    {0, 1, 3, "1.8891584217112234e-10"},
    {0, 2, 0, "-3.3894294366220226e-5"},
    {0, 2, 1, "1.0152735770152521e-9"},
    {0, 2, 2, "-5.1265427666868923e-11"},
    {0, 3, 0, "1.4437372675293143e-7"},
    {0, 3, 1, "-5.298214124371814e-12"},
    {0, 4, 0, "-8.789506553141813e-10"},
    {1, 0, 0, "5.054376632393368e-5"},
    {1, 0, 1, "5.052584250610746e-6"},
    {1, 0, 2, "-2.563978901879392e-7"},
    {1, 0, 3, "2.584931067068849e-8"},
    {1, 1, 0, "7.215736772066651e-3"},
    {1, 1, 1, "3.280783653558314e-8"},
    {1, 1, 2, "-1.656643618726944e-9"},
    {1, 2, 0, "-2.2591371530547404e-5"},
    {1, 2, 1, "1.1067978706929757e-9"},
    {1, 3, 0, "1.276293752012006e-7"},
    {2, 0, 0, "8.418623394483387e-6"},
    {2, 0, 1, "8.448690174969135e-7"},
    {2, 0, 2, "-4.273987361420872e-8"},
    {2, 1, 0, "1.3572089817281974e-7"},
    {2, 1, 1, "1.0599706658747629e-8"},
    {2, 2, 0, "-3.7622304386607397e-6"},
    {3, 0, 0, "-1.3627956121984967e-9"},
    {3, 0, 1, "-3.1249201230126866e-10"},
    {3, 1, 0, "1.5072379548920485e-8"},
    {4, 0, 0, "-1.1314253800889275e-10"},
}};

double absUpper(const interval& value) {
  return std::max(std::abs(value.leftBound()),
                  std::abs(value.rightBound()));
}

interval absoluteEnvelope(const interval& value) {
  return interval(0., absUpper(value));
}

double midpointValue(const interval& value) {
  return value.mid().leftBound();
}

interval decimal(const char* value) { return interval(value, value); }

interval rational(long numerator, long denominator = 1) {
  return rfsn::rigorous::exactRational(
      std::to_string(numerator), std::to_string(denominator));
}

// These are theorem constants, not binary64 approximations.  In particular,
// using interval(.01) or interval(.7) would put only the rounded machine
// number in the interval and need not contain the stated rational constant.
interval sourceRadius() { return rational(1, 100); }
interval graphC0() { return rational(1, 200000); }
interval graphPhaseC1() { return rational(3, 1000000); }
interval thetaFace() { return rational(4, 25000000); }
interval thetaHalfWidth() { return rational(1, 1000000000); }
interval lowerGraphBaseHalfWidth() { return rational(27, 200000); }
interval lowerGraphNormalHalfWidth() { return rational(1, 10000); }
interval lowerGraphSlope() { return rational(7, 10); }

interval intervalFromEndpoints(const interval& lower,
                               const interval& upper) {
  return interval(lower.leftBound(), upper.rightBound());
}

interval hull(const interval& left, const interval& right) {
  return interval(std::min(left.leftBound(), right.leftBound()),
                  std::max(left.rightBound(), right.rightBound()));
}

void include(bool initialized, interval& aggregate, const interval& value) {
  aggregate = initialized ? hull(aggregate, value) : value;
}

struct FirstJet {
  static constexpr int dimension = 5;
  interval value;
  std::array<interval, dimension> derivative;

  explicit FirstJet(const interval& input = interval(0.))
      : value(input), derivative{interval(0.), interval(0.), interval(0.),
                                 interval(0.), interval(0.)} {}

  static FirstJet variable(const interval& input, int column) {
    FirstJet result(input);
    result.derivative.at(static_cast<std::size_t>(column)) = interval(1.);
    return result;
  }
};

FirstJet operator+(const FirstJet& left, const FirstJet& right) {
  FirstJet result(left.value + right.value);
  for (int index = 0; index < FirstJet::dimension; ++index)
    result.derivative[index] =
        left.derivative[index] + right.derivative[index];
  return result;
}

FirstJet operator-(const FirstJet& left, const FirstJet& right) {
  FirstJet result(left.value - right.value);
  for (int index = 0; index < FirstJet::dimension; ++index)
    result.derivative[index] =
        left.derivative[index] - right.derivative[index];
  return result;
}

FirstJet operator-(const FirstJet& input) {
  FirstJet result(-input.value);
  for (int index = 0; index < FirstJet::dimension; ++index)
    result.derivative[index] = -input.derivative[index];
  return result;
}

FirstJet operator*(const FirstJet& left, const FirstJet& right) {
  FirstJet result(left.value * right.value);
  for (int index = 0; index < FirstJet::dimension; ++index)
    result.derivative[index] =
        left.derivative[index] * right.value +
        left.value * right.derivative[index];
  return result;
}

FirstJet reciprocal(const FirstJet& input) {
  FirstJet result(interval(1.) / input.value);
  for (int index = 0; index < FirstJet::dimension; ++index)
    result.derivative[index] =
        -input.derivative[index] / sqr(input.value);
  return result;
}

FirstJet operator/(const FirstJet& left, const FirstJet& right) {
  return left * reciprocal(right);
}

FirstJet jetPower(const FirstJet& input, int exponent) {
  FirstJet result(interval(1.));
  for (int index = 0; index < exponent; ++index) result = result * input;
  return result;
}

FirstJet jetSqrt(const FirstJet& input) {
  FirstJet result(sqrt(input.value));
  for (int index = 0; index < FirstJet::dimension; ++index)
    result.derivative[index] =
        input.derivative[index] / (interval(2.) * result.value);
  return result;
}

FirstJet jetSin(const FirstJet& input) {
  FirstJet result(sin(input.value));
  for (int index = 0; index < FirstJet::dimension; ++index)
    result.derivative[index] = cos(input.value) * input.derivative[index];
  return result;
}

FirstJet jetCos(const FirstJet& input) {
  FirstJet result(cos(input.value));
  for (int index = 0; index < FirstJet::dimension; ++index)
    result.derivative[index] = -sin(input.value) * input.derivative[index];
  return result;
}

FirstJet jetAtan(const FirstJet& input) {
  FirstJet result(atan(input.value));
  for (int index = 0; index < FirstJet::dimension; ++index)
    result.derivative[index] =
        input.derivative[index] / (interval(1.) + sqr(input.value));
  return result;
}

template <std::size_t Size>
FirstJet graphPolynomial(const PolynomialTerm (&terms)[Size],
                         const FirstJet& x, const FirstJet& y) {
  FirstJet result(interval(0.));
  for (const auto& term : terms) {
    interval coefficient(term.numerator, term.numerator);
    coefficient /= interval(term.denominator, term.denominator);
    if (term.times_sqrt_two) coefficient *= sqrt(interval(2.));
    result = result + FirstJet(coefficient) *
        jetPower(x, term.px) * jetPower(y, term.py);
  }
  return result;
}

FirstJet phasePredictor(const FirstJet& r, const FirstJet& a2,
                        const FirstJet& epsilon) {
  const FirstJet x = FirstJet(interval(200.)) *
      (r - FirstJet(decimal("0.015")));
  const FirstJet y = FirstJet(interval(4.)) * a2;
  const FirstJet z = FirstJet(interval(5.)) *
      (epsilon - FirstJet(interval(1.)));
  FirstJet result(interval(0.));
  for (const auto& term : kPredictor) {
    result = result + FirstJet(decimal(term.coefficient)) *
        jetPower(x, term.rPower) * jetPower(y, term.aPower) *
        jetPower(z, term.epsilonPower);
  }
  return result;
}

using Box = std::array<interval, 3>;

interval sourceKatoU1(const Box& centre, const Box& offsets,
                      const interval& thetaCentre,
                      const interval& thetaOffset,
                      const interval& graphCentre,
                      const interval& graphOffset) {
  const interval r = centre[0] + offsets[0];
  const interval a2 = centre[1] + offsets[1];
  const interval epsilon = centre[2] + offsets[2];
  const interval rootEpsilon = sqrt(epsilon);
  const interval c = interval(2.) * r * a2 +
      rootEpsilon * sqr(sqr(r)) * sqr(a2);
  const interval alpha = interval(.5) * sqrt(interval(2.) + c);
  const interval beta = interval(.5) * sqrt(interval(2.) - c);
  const interval chi = atan(
      (interval(1.) / sqrt(interval(2.)) - alpha) / beta);
  const interval predictor =
      phasePredictor(FirstJet(r), FirstJet(a2), FirstJet(epsilon)).value;
  const interval graph = graphCentre + graphOffset;
  const interval phase = predictor + thetaCentre + thetaOffset -
      rational(11, 8) * graph;
  return sourceRadius() * cos(phase + chi);
}

std::array<FirstJet, 4> sourceJet(
    const Box& centre, const Box& offsets, const interval& thetaCentre,
    const interval& thetaOffset, const interval& graphCentre,
    const interval& graphOffset,
    bool differentiatePhasePredictor = true) {
  const FirstJet dr = FirstJet::variable(offsets[0], 0);
  const FirstJet da = FirstJet::variable(offsets[1], 1);
  const FirstJet depsilon = FirstJet::variable(offsets[2], 2);
  const FirstJet dtheta = FirstJet::variable(thetaOffset, 3);
  const FirstJet dgraph = FirstJet::variable(graphOffset, 4);
  const FirstJet one(interval(1.));
  const FirstJet two(interval(2.));
  const FirstJet r = FirstJet(centre[0]) + dr;
  const FirstJet a2 = FirstJet(centre[1]) + da;
  const FirstJet epsilon = FirstJet(centre[2]) + depsilon;
  const FirstJet graphError = FirstJet(graphCentre) + dgraph;
  const FirstJet rootEpsilon = jetSqrt(epsilon);
  const FirstJet r2 = r * r;
  const FirstJet r3 = r2 * r;
  const FirstJet r4 = r2 * r2;
  const FirstJet aa = one + rootEpsilon * r3 * a2;
  const FirstJet bb = rootEpsilon * r2 / FirstJet(interval(3.));
  const FirstJet cc = two * r * a2 +
      rootEpsilon * r4 * a2 * a2;
  const FirstJet alpha = FirstJet(interval(.5)) * jetSqrt(two + cc);
  const FirstJet beta = FirstJet(interval(.5)) * jetSqrt(two - cc);
  const FirstJet h = FirstJet(interval(.5)) *
      jetSqrt(FirstJet(interval(4.)) - cc * cc);
  const FirstJet chi = jetAtan(
      (one / jetSqrt(two) - alpha) / beta);
  const FirstJet predictor = phasePredictor(r, a2, epsilon);
  const FirstJet phase =
      (differentiatePhasePredictor ? predictor
                                   : FirstJet(predictor.value)) +
      FirstJet(thetaCentre) + dtheta -
      FirstJet(rational(11, 8)) * graphError;
  const FirstJet angle = phase + chi;
  const FirstJet rho{sourceRadius()};
  const FirstJet u1 = rho * jetCos(angle);
  const FirstJet u2 = rho * jetSin(angle);
  const FirstJet s1 = graphPolynomial(kH1Terms, u1, u2) + graphError;
  const FirstJet U = u1 + s1;
  const FirstJet s2 = -s1 * u2 / u1 -
      aa * jetPower(U, 3) /
          (FirstJet(interval(6.)) * h * u1) +
      bb * jetPower(U, 4) /
          (FirstJet(interval(8.)) * h * u1);
  return {
      U,
      alpha * u1 - beta * u2 - alpha * s1 + beta * s2,
      cc * U / FirstJet(interval(2.)) + h * (u2 + s2),
      alpha * u1 + beta * u2 - alpha * s1 - beta * s2};
}

struct InitialData {
  IVector centre;
  IMatrix coordinates;
  IVector radii;
  IVector remainder;
  std::array<interval, 4> thetaTangent;
  std::array<interval, 4> graphTangent;
  IMatrix parameterTangent;
  IMatrix fixedPhaseParameterTangent;
};

InitialData initialData(const Box& centre, const Box& offsets,
                        const interval& thetaCentre,
                        const interval& thetaOffset,
                        const interval& graphCentre,
                        const interval& graphOffset) {
  const auto jet = sourceJet(centre, offsets, thetaCentre, thetaOffset,
                             graphCentre, graphOffset);
  const auto fixedPhaseJet = sourceJet(
      centre, offsets, thetaCentre, thetaOffset,
      graphCentre, graphOffset, false);
  const Box zeroOffsets = {interval(0.), interval(0.), interval(0.)};
  const auto pointJet = sourceJet(
      centre, zeroOffsets, thetaCentre, interval(0.), graphCentre,
      interval(0.));
  IVector x(9), radii(9), remainder(9);
  IMatrix coordinates(9, 9);
  IMatrix parameterTangent(9, 3);
  IMatrix fixedPhaseParameterTangent(9, 3);
  for (int row = 0; row < 9; ++row) {
    x[row] = interval(0.);
    radii[row] = interval(0.);
    remainder[row] = interval(0.);
    for (int column = 0; column < 9; ++column)
      coordinates[row][column] = interval(0.);
    for (int column = 0; column < 3; ++column)
      parameterTangent[row][column] = interval(0.);
    for (int column = 0; column < 3; ++column)
      fixedPhaseParameterTangent[row][column] = interval(0.);
  }
  for (int row = 0; row < 4; ++row) x[row] = pointJet[row].value;
  for (int index = 0; index < 3; ++index) {
    radii[index] = offsets[index];
    coordinates[4 + index][index] = interval(1.);
  }
  x[7] = thetaCentre;
  x[8] = graphCentre;
  radii[3] = thetaOffset;
  radii[4] = graphOffset;
  coordinates[7][3] = interval(1.);
  coordinates[8][4] = interval(1.);
  std::array<interval, 4> thetaTangent;
  std::array<interval, 4> graphTangent;
  for (int physical = 0; physical < 4; ++physical) {
    for (int column = 0; column < 5; ++column)
      coordinates[physical][column] =
          interval(midpointValue(jet[physical].derivative[column]));
    coordinates[physical][5 + physical] = interval(1.);
    thetaTangent[physical] = jet[physical].derivative[3];
    graphTangent[physical] = jet[physical].derivative[4];
    for (int parameter = 0; parameter < 3; ++parameter)
      parameterTangent[physical][parameter] =
          jet[physical].derivative[parameter];
    for (int parameter = 0; parameter < 3; ++parameter)
      fixedPhaseParameterTangent[physical][parameter] =
          fixedPhaseJet[physical].derivative[parameter];
    interval raw(0.);
    for (int column = 0; column < 3; ++column)
      raw += (jet[physical].derivative[column] -
              coordinates[physical][column]) * offsets[column];
    raw += (jet[physical].derivative[3] -
            coordinates[physical][3]) * thetaOffset;
    raw += (jet[physical].derivative[4] -
            coordinates[physical][4]) * graphOffset;
    const double radius = absUpper(raw);
    remainder[physical] = interval(-radius, radius);
  }
  for (int parameter = 0; parameter < 3; ++parameter)
    parameterTangent[4 + parameter][parameter] = interval(1.);
  for (int parameter = 0; parameter < 3; ++parameter)
    fixedPhaseParameterTangent[4 + parameter][parameter] = interval(1.);
  return {x, coordinates, radii, remainder, thetaTangent, graphTangent,
          parameterTangent, fixedPhaseParameterTangent};
}

struct Spectral {
  interval b;
  interval n;
  interval db;
  interval dn;
};

struct CellResult {
  interval b;
  interval n;
  interval aligned;
  interval centreAligned;
  interval db;
  interval dn;
  interval sourceSlope;
  interval coneMargin;
  interval terminalQ;
  interval phaseDomainMargin;
  interval sourceU;
  interval seamP;
  interval preSeamMargin;
  interval denseW;
  interval hitTime;
  std::array<interval, 3> bOnNZeroParameterDerivative;
  interval fixedEtaNTheta;
  interval exteriorSeamP;
  bool rootDerivativeComputed;
  Verdict status;
};

struct SeamData {
  IVector centre;
  IMatrix coordinates;
  IVector radii;
  IVector remainder;
  IVector event;
  IVector tangent;
  IMatrix parameterTangent;
  interval hitTime;
  interval energy;
  interval preSeamMargin;
};

struct ExteriorSeamData {
  interval vW;
  interval vQ;
  interval determinantWQ;
  interval eventP;
};

ExteriorSeamData hitFixedCutExterior(const InitialData& initial,
                                     const Box& parameterCentre,
                                     int parameter) {
  if (parameter < 0 || parameter >= 3)
    throw std::invalid_argument("invalid exterior parameter index");
  const std::string r = "(rc+er)";
  const std::string a2 = "(a2c+ea)";
  const std::string epsilon = "(epsc+ee)";
  const std::string rootEpsilon = "sqrt(" + epsilon + ")";
  const std::string linearCoefficient =
      "(2*" + r + "*" + a2 + "+" + rootEpsilon + "*" + r +
      "^4*" + a2 + "^2)";
  const std::string quadratic =
      "(1+" + rootEpsilon + "*" + r + "^3*" + a2 + ")";
  const std::string cubic =
      "(" + rootEpsilon + "*" + r + "^2/3)";
  const std::string normalDerivative =
      "(" + linearCoefficient + "-2*" + quadratic + "*U+" +
      rootEpsilon + "*" + r + "^2*U^2)";
  std::string forcing;
  if (parameter == 0) {
    forcing = "((2*" + a2 + "+4*" + rootEpsilon + "*" + r +
        "^3*" + a2 + "^2)*U-3*" + rootEpsilon + "*" + r +
        "^2*" + a2 + "*U^2+2*" + rootEpsilon + "*" + r +
        "*U^3/3)";
  } else if (parameter == 1) {
    forcing = "((2*" + r + "+2*" + rootEpsilon + "*" + r +
        "^4*" + a2 + ")*U-" + rootEpsilon + "*" + r +
        "^3*U^2)";
  } else {
    forcing = "(" + r + "^4*" + a2 + "^2*U/(2*" +
        rootEpsilon + ")-" + r + "^3*" + a2 + "*U^2/(2*" +
        rootEpsilon + ")+" + r + "^2*U^3/(6*" +
        rootEpsilon + "))";
  }
  const std::string fieldText =
      "par:rc,a2c,epsc;"
      "var:U,P,V,Q,er,ea,ee,vU,vP,vV,vQ,"
      "w01,w02,w03,w12,w13,w23;fun:"
      "P," + linearCoefficient + "*U-V-" + quadratic + "*U^2+" +
      cubic + "*U^3,Q,U,0,0,0," +
      "vP," + normalDerivative + "*vU-vV,vQ,vU," +
      "-w02-" + forcing + "*vU," +
      "w12+w03,w13," +
      normalDerivative + "*w02+w13+" + forcing + "*vV," +
      normalDerivative + "*w03-w23-w01+" + forcing + "*vQ," +
      "-w02;";
  IMap field(fieldText);
  field.setParameter("rc", parameterCentre[0]);
  field.setParameter("a2c", parameterCentre[1]);
  field.setParameter("epsc", parameterCentre[2]);

  constexpr int dimension = 17;
  IVector centre(dimension), radii(dimension), remainder(dimension);
  IMatrix coordinates(dimension, dimension);
  for (int row = 0; row < dimension; ++row) {
    centre[row] = interval(0.);
    radii[row] = interval(0.);
    remainder[row] = interval(0.);
    for (int column = 0; column < dimension; ++column)
      coordinates[row][column] = interval(0.);
  }
  for (int row = 0; row < 7; ++row) {
    centre[row] = initial.centre[row];
    remainder[row] = initial.remainder[row];
    for (int column = 0; column < 9; ++column)
      coordinates[row][column] = initial.coordinates[row][column];
  }
  for (int column = 0; column < 9; ++column)
    radii[column] = initial.radii[column];
  std::array<interval, 4> phase;
  std::array<interval, 4> parameterTangent;
  for (int row = 0; row < 4; ++row) {
    phase[row] = initial.thetaTangent[row];
    parameterTangent[row] =
        initial.fixedPhaseParameterTangent[row][parameter];
    centre[7 + row] = interval(midpointValue(phase[row]));
    remainder[7 + row] = phase[row] - centre[7 + row];
  }
  constexpr std::array<std::array<int, 2>, 6> pairs{{
      {{0, 1}}, {{0, 2}}, {{0, 3}},
      {{1, 2}}, {{1, 3}}, {{2, 3}},
  }};
  for (int index = 0; index < 6; ++index) {
    const int left = pairs[index][0];
    const int right = pairs[index][1];
    const interval wedge = parameterTangent[left] * phase[right] -
        parameterTangent[right] * phase[left];
    centre[11 + index] = interval(midpointValue(wedge));
    remainder[11 + index] = wedge - centre[11 + index];
  }

  IOdeSolver prefixSolver(field, 24);
  prefixSolver.setAbsoluteTolerance(1.e-13);
  prefixSolver.setRelativeTolerance(1.e-13);
  prefixSolver.setMaxStep(.02);
  C0HORect2Set set(centre, coordinates, radii, remainder);
  ITimeMap prefixMap(prefixSolver);
  (void)prefixMap(rational(13, 4), set);

  IOdeSolver eventSolver(field, 24);
  eventSolver.setAbsoluteTolerance(1.e-13);
  eventSolver.setRelativeTolerance(1.e-13);
  eventSolver.setMaxStep(.02);
  ICoordinateSection section(dimension, 0, -rational(1, 20));
  IPoincareMap eventMap(
      eventSolver, section, poincare::PlusMinus);
  eventMap.setMaxReturnTime(20.);
  interval eventTime;
  const IVector event = eventMap(set, eventTime);
  if (event[1].rightBound() >= 0.)
    throw std::runtime_error(
        "exterior seam event is not contained in P<0");

  const interval physicalR = parameterCentre[0] + event[4];
  const interval physicalA2 = parameterCentre[1] + event[5];
  const interval physicalEpsilon = parameterCentre[2] + event[6];
  const interval physicalRootEpsilon = sqrt(physicalEpsilon);
  const interval physicalLinear = interval(2.) * physicalR * physicalA2 +
      physicalRootEpsilon * sqr(sqr(physicalR)) * sqr(physicalA2);
  const interval physicalQuadratic = interval(1.) +
      physicalRootEpsilon * sqr(physicalR) * physicalR * physicalA2;
  const interval physicalCubic =
      physicalRootEpsilon * sqr(physicalR) / interval(3.);
  const interval fP = physicalLinear * event[0] - event[2] -
      physicalQuadratic * sqr(event[0]) +
      physicalCubic * event[0] * sqr(event[0]);
  const interval projectedVP =
      event[8] - fP * event[7] / event[1];
  const interval projectedVQ =
      event[10] - event[0] * event[7] / event[1];
  return {interval(2.) * event[1] * projectedVP,
          projectedVQ,
          interval(2.) *
              (event[1] * event[15] - fP * event[13] +
               event[0] * event[11]),
          event[1]};
}

SeamData hitFixedCut(const InitialData& initial,
                     const Box& parameterCentre,
                     const interval& cutU,
                     int prefixQuarterCount) {
  IMap field(
      "par:rc,a2c,epsc;var:U,P,V,Q,er,ea,ee,dtheta,e;"
      "fun:P,(2*(rc+er)*(a2c+ea)+sqrt(epsc+ee)*(rc+er)^4*"
      "(a2c+ea)^2)*U-V-(1+sqrt(epsc+ee)*(rc+er)^3*"
      "(a2c+ea))*U^2+(sqrt(epsc+ee)/3)*(rc+er)^2*U^3,"
      "Q,U,0,0,0,0,0;");
  field.setParameter("rc", parameterCentre[0]);
  field.setParameter("a2c", parameterCentre[1]);
  field.setParameter("epsc", parameterCentre[2]);
  const interval graphPrime = intervalFromEndpoints(
      -graphPhaseC1(), graphPhaseC1());
  const interval slant = -rational(11, 8);
  const interval graphTheta =
      graphPrime / (interval(1.) - slant * graphPrime);
  IVector sourceTangent(9);
  for (int index = 0; index < 9; ++index)
    sourceTangent[index] = interval(0.);
  // graphTangent is the derivative at fixed slanted theta, namely
  // S_e^slant=S_e-(11/8)S_phi.  Consequently the following expression is
  // exactly (S_phi+S_e e_phi)/(1+(11/8)e_phi).
  for (int index = 0; index < 4; ++index)
    sourceTangent[index] = initial.thetaTangent[index] +
        initial.graphTangent[index] * graphTheta;
  sourceTangent[7] = interval(1.);
  sourceTangent[8] = graphTheta;

  // The source orbit makes a long saddle-focus turn before it reaches the
  // finite algebraic seam.  A single Poincare enclosure loses the affine
  // parameter/phase correlations.  Recondition at fixed quarter-time cuts,
  // retaining the same five primary radii, and verify on every dense step
  // that U remains strictly above the seam.  The final Poincare leg is then
  // short, and the dense inequalities exclude an earlier U=-1/20 hit.
  IVector affineCentre = initial.centre;
  IMatrix affineCoordinates = initial.coordinates;
  const IVector radii = initial.radii;
  IVector affineRemainder = initial.remainder;
  IMatrix propagatedTangents(9, 9);
  for (int row = 0; row < 9; ++row) {
    for (int column = 0; column < 9; ++column)
      propagatedTangents[row][column] = interval(0.);
    for (int parameter = 0; parameter < 3; ++parameter)
      propagatedTangents[row][parameter] =
          initial.parameterTangent[row][parameter];
    propagatedTangents[row][3] = sourceTangent[row];
  }
  interval elapsed(0.);
  interval preSeamMargin;
  bool marginInitialized = false;
  if (prefixQuarterCount <= 0)
    throw std::invalid_argument("cut prefix must contain a positive number of quarters");
  for (int quarter = 0; quarter < prefixQuarterCount; ++quarter) {
    const interval duration = rational(1, 4);
    IOdeSolver pointSolver(field, 24);
    pointSolver.setAbsoluteTolerance(1.e-13);
    pointSolver.setRelativeTolerance(1.e-13);
    pointSolver.setMaxStep(.02);
    C1HORect2Set pointSet(affineCentre);
    ITimeMap pointMap(pointSolver);
    const IVector pointEvent = pointMap(duration, pointSet);

    IOdeSolver solver(field, 24);
    solver.setAbsoluteTolerance(1.e-13);
    solver.setRelativeTolerance(1.e-13);
    solver.setMaxStep(.02);
    C1HORect2Set set(affineCentre, affineCoordinates,
                     radii, affineRemainder);
    ITimeMap map(solver);
    map.stopAfterStep(true);
    do {
      (void)map(duration, set);
      const interval stepMargin =
          set.getLastEnclosure()[0] - cutU;
      include(marginInitialized, preSeamMargin, stepMargin);
      marginInitialized = true;
      if (stepMargin.leftBound() <= 0.)
        throw std::runtime_error(
            "fixed-time source prefix does not exclude an earlier seam hit");
    } while (!map.completed());

    const IMatrix flow = (IMatrix)set;

    IOdeSolver tangentSolver(field, 24);
    tangentSolver.setAbsoluteTolerance(1.e-13);
    tangentSolver.setRelativeTolerance(1.e-13);
    tangentSolver.setMaxStep(.02);
    C1HORect2Set::C0BaseSet tangentC0(
        affineCentre, affineCoordinates, radii, affineRemainder);
    C1HORect2Set::C1BaseSet tangentC1(propagatedTangents);
    C1HORect2Set tangentSet(tangentC0, tangentC1);
    ITimeMap tangentMap(tangentSolver);
    (void)tangentMap(duration, tangentSet);
    propagatedTangents = (IMatrix)tangentSet;

    const IMatrix linear = flow * affineCoordinates;
    IVector nextCentre(9), nextRemainder(9);
    IMatrix nextCoordinates(9, 9);
    for (int row = 0; row < 9; ++row) {
      nextCentre[row] = interval(midpointValue(pointEvent[row]));
      nextRemainder[row] = pointEvent[row] - nextCentre[row];
      for (int column = 0; column < 9; ++column) {
        nextCoordinates[row][column] =
            interval(midpointValue(linear[row][column]));
        nextRemainder[row] +=
            (linear[row][column] - nextCoordinates[row][column]) *
                radii[column] +
            flow[row][column] * affineRemainder[column];
      }
    }
    affineCentre = nextCentre;
    affineCoordinates = nextCoordinates;
    affineRemainder = nextRemainder;
    elapsed += duration;
  }

  IOdeSolver pointSolver(field, 24);
  pointSolver.setAbsoluteTolerance(1.e-13);
  pointSolver.setRelativeTolerance(1.e-13);
  pointSolver.setMaxStep(.02);
  C1HORect2Set pointSet(affineCentre);
  ICoordinateSection pointSection(9, 0, cutU);
  IPoincareMap pointMap(
      pointSolver, pointSection, poincare::PlusMinus);
  pointMap.setMaxReturnTime(20.);
  interval pointTime;
  const IVector pointEvent = pointMap(pointSet, pointTime);

  IOdeSolver solver(field, 24);
  solver.setAbsoluteTolerance(1.e-13);
  solver.setRelativeTolerance(1.e-13);
  solver.setMaxStep(.02);
  C1HORect2Set set(affineCentre, affineCoordinates,
                   radii, affineRemainder);
  ICoordinateSection section(9, 0, cutU);
  IPoincareMap map(solver, section, poincare::PlusMinus);
  map.setMaxReturnTime(20.);
  interval hitTime;
  IMatrix flowDerivative(9, 9);
  const IVector event = map(set, flowDerivative, hitTime);
  const IMatrix derivative =
      map.computeDP(event, flowDerivative, hitTime);
  const IMatrix eventTangents = derivative * propagatedTangents;
  IVector eventTangent(9);
  IMatrix eventParameterTangent(9, 3);
  for (int row = 0; row < 9; ++row) {
    eventTangent[row] = eventTangents[row][3];
    for (int parameter = 0; parameter < 3; ++parameter)
      eventParameterTangent[row][parameter] =
          eventTangents[row][parameter];
  }
  IVector seamCentre(9), seamRemainder(9);
  IMatrix seamCoordinates(9, 9);
  const IMatrix linear = derivative * affineCoordinates;
  for (int row = 0; row < 9; ++row) {
    seamCentre[row] = interval(midpointValue(pointEvent[row]));
    seamRemainder[row] = pointEvent[row] - seamCentre[row];
    for (int column = 0; column < 9; ++column) {
      seamCoordinates[row][column] =
          interval(midpointValue(linear[row][column]));
      seamRemainder[row] +=
          (linear[row][column] - seamCoordinates[row][column]) *
              radii[column] +
          derivative[row][column] * affineRemainder[column];
    }
  }
  seamCentre[0] = cutU;
  seamRemainder[0] = interval(0.);
  for (int column = 0; column < 9; ++column)
    seamCoordinates[0][column] = interval(0.);
  const interval r = parameterCentre[0] + event[4];
  const interval a2 = parameterCentre[1] + event[5];
  const interval epsilon = parameterCentre[2] + event[6];
  const interval rootEpsilon = sqrt(epsilon);
  const interval cubic = rootEpsilon * sqr(r) / interval(3.);
  const interval quadratic =
      interval(1.) + rootEpsilon * sqr(r) * r * a2;
  const interval linearCoefficient =
      interval(2.) * r * a2 + rootEpsilon * sqr(sqr(r)) * sqr(a2);
  const interval energy = sqr(event[1]) / interval(2.) -
      sqr(event[3]) / interval(2.) -
      linearCoefficient * sqr(cutU) / interval(2.) +
      cutU * event[2] + quadratic * cutU * sqr(cutU) /
          interval(3.) - cubic * sqr(sqr(cutU)) / interval(4.);
  return {seamCentre, seamCoordinates, radii, seamRemainder,
          event, eventTangent, eventParameterTangent,
          elapsed + hitTime, energy,
          preSeamMargin};
}

struct ReducedInitialData {
  IVector centre;
  IMatrix coordinates;
  IVector radii;
  IVector remainder;
  IMatrix tangents;
};

ReducedInitialData reducedInitialData(const SeamData& seam) {
  constexpr int dimension = 9;
  IVector centre(dimension), radii(dimension), remainder(dimension);
  IMatrix coordinates(dimension, dimension), tangents(dimension, dimension);
  for (int row = 0; row < dimension; ++row) {
    centre[row] = interval(0.);
    radii[row] = interval(0.);
    remainder[row] = interval(0.);
    for (int column = 0; column < dimension; ++column) {
      coordinates[row][column] = interval(0.);
      tangents[row][column] = interval(0.);
    }
  }
  for (int column = 0; column < 5; ++column)
    radii[column] = seam.radii[column];
  const interval pCentre = seam.centre[1];
  const interval pHull = seam.centre[1] +
      seam.coordinates[1] * seam.radii + seam.remainder[1];
  centre[0] = sqr(pCentre);
  centre[1] = seam.centre[3];
  centre[2] = interval(0.);
  centre[3] = interval(0.);
  centre[4] = interval(0.);
  centre[5] = seam.centre[7];
  centre[6] = seam.centre[8];
  centre[7] = interval(0.);
  centre[8] = interval(0.);
  interval wRemainder(0.);
  for (int column = 0; column < 5; ++column) {
    const interval wDerivative =
        interval(2.) * pHull * seam.coordinates[1][column];
    coordinates[0][column] = interval(midpointValue(wDerivative));
    wRemainder +=
        (wDerivative - coordinates[0][column]) * seam.radii[column];
    coordinates[1][column] = seam.coordinates[3][column];
  }
  wRemainder += interval(2.) * pHull * seam.remainder[1];
  const double wRadius = absUpper(wRemainder);
  const double qRadius = absUpper(seam.remainder[3]);
  radii[5] = interval(-wRadius, wRadius);
  radii[6] = interval(-qRadius, qRadius);
  coordinates[0][5] = interval(1.);
  coordinates[1][6] = interval(1.);
  coordinates[2][0] = interval(1.);
  coordinates[3][1] = interval(1.);
  coordinates[4][2] = interval(1.);
  coordinates[5][3] = interval(1.);
  coordinates[6][4] = interval(1.);
  tangents[0][3] = interval(2.) * seam.event[1] * seam.tangent[1];
  tangents[1][3] = seam.tangent[3];
  tangents[5][3] = interval(1.);
  tangents[6][3] = seam.tangent[8];
  for (int parameter = 0; parameter < 3; ++parameter) {
    tangents[0][parameter] =
        interval(2.) * seam.event[1] *
        seam.parameterTangent[1][parameter];
    tangents[1][parameter] =
        seam.parameterTangent[3][parameter];
    for (int row = 2; row <= 6; ++row)
      tangents[row][parameter] =
          seam.parameterTangent[row + 2][parameter];
  }
  return {centre, coordinates, radii, remainder, tangents};
}

struct ReducedSpectralFormulas {
  std::string map;
  std::string b;
  std::string n;
  std::string error;
};

ReducedSpectralFormulas reducedSpectralFormulas() {
  const std::string r = "(rc+er)";
  const std::string a2 = "(a2c+ea)";
  const std::string epsilon = "(epsc+ee)";
  const std::string s = "sqrt(" + epsilon + ")";
  const std::string kappa = "sqrt(" + s + ")";
  const std::string m = "(4+" + r + "*" + a2 + ")";
  const std::string rootM = "sqrt(" + m + ")";
  const std::string x = "(" + s + "*" + r + "^2*" + m + ")";
  const std::string denominator = "(2+" + x + ")";
  const std::string q0 =
      "sqrt((8+3*" + x + ")/(6*" + s + "))";
  const std::string p0 = "(" + q0 + "/" + denominator + ")";
  const std::string correction =
      "(" + r + "*" + a2 + "*(" + x + "+3)/(3*" + s + "*" +
      m + "*" + q0 + "*" + denominator + "))";
  const std::string omega0 =
      "((" + x + "+4)/(3*" + m + "*" + denominator + "^3))";
  const std::string lambda = "sqrt(" + s + "*" + denominator + ")";
  const std::string physicalP = "(-sqrt(w))";
  const std::string pi =
      "(-" + physicalP + "/(" + kappa + "*" + rootM + "))";
  // On H=0 at U=-4, combine the large V/reference terms before interval
  // evaluation.  Expanding the old expression gives this exact identity;
  // the combined form retains the cancellation needed by the normal
  // coordinate and its parameter derivatives.
  const std::string omegaNumerator =
      "((w-qq^2)/8+32/3+4*" + r + "*" + a2 + "+" + s +
      "*(2*" + r + "^4*" + a2 + "^2+32*" + r + "^3*" + a2 +
      "/3+16*" + r + "^2))";
  const std::string omega =
      "(" + omegaNumerator + "/" + m + ")";
  const std::string error =
      "(" + pi + "-(" + p0 + "-" + correction + "))";
  const std::string normal = "(" + omega + "-" + omega0 + ")";
  const std::string b =
      "((" + error + "-" + normal + "/" + lambda + ")/2)";
  const std::string n =
      "((" + error + "+" + normal + "/" + lambda + ")/2)";
  const std::string aligned = "(" + b + "+(" + n + ")/32)";
  const std::string prefix =
      "par:rc,a2c,epsc;var:w,qq,er,ea,ee,dtheta,e,clock,z;fun:";
  return {prefix + b + "," + n + "," + aligned + ";",
          prefix + b + ";", prefix + n + ";",
          prefix + error + ";"};
}

struct TerminalData {
  interval b;
  interval n;
  interval aligned;
  interval db;
  interval dn;
  interval q;
  interval reducedClock;
  interval denseW;
  std::array<interval, 3> bParameterDerivative;
  std::array<interval, 3> nParameterDerivative;
  std::array<interval, 3> alignedParameterDerivative;
  std::array<interval, 3> qParameterDerivative;
};

TerminalData propagateReduced(const ReducedInitialData& initial,
                              const Box& parameterCentre) {
  constexpr int dimension = 9;
  IMap field(
      "time:x;par:rc,a2c,epsc;"
      "var:w,qq,er,ea,ee,dtheta,e,clock,z;"
      "fun:w/x-qq^2/x+"
      "(2*(rc+er)*(a2c+ea)+sqrt(epsc+ee)*(rc+er)^4*"
      "(a2c+ea)^2)*x+"
      "4*(1+sqrt(epsc+ee)*(rc+er)^3*(a2c+ea))*x^2/3+"
      "sqrt(epsc+ee)*(rc+er)^2*x^3/2,"
      "-x/sqrt(w),0,0,0,0,0,1/sqrt(w),0;");
  field.setParameter("rc", parameterCentre[0]);
  field.setParameter("a2c", parameterCentre[1]);
  field.setParameter("epsc", parameterCentre[2]);
  IVector affineCentre = initial.centre;
  IMatrix affineCoordinates = initial.coordinates;
  const IVector radii = initial.radii;
  IVector affineRemainder = initial.remainder;
  IMatrix reducedTangents = initial.tangents;
  interval currentX = rational(1, 20);
  interval denseW =
      affineCentre[0] + affineCoordinates[0] * radii +
      affineRemainder[0];
  const std::array<interval, 13> targets = {
      rational(1, 5), rational(1, 2), interval(1.), interval(2.),
      interval(3.), rational(25, 8), rational(26, 8), rational(27, 8),
      rational(28, 8), rational(29, 8), rational(30, 8), rational(31, 8),
      interval(4.)};
  for (const interval& target : targets) {
    IOdeSolver pointSolver(field, 24);
    pointSolver.setAbsoluteTolerance(1.e-13);
    pointSolver.setRelativeTolerance(1.e-13);
    pointSolver.setMaxStep(.005);
    C1HORect2Set pointSet(affineCentre);
    pointSet.setCurrentTime(currentX);
    ITimeMap pointMap(pointSolver);
    const IVector pointEvent = pointMap(target, pointSet);

    IOdeSolver solver(field, 24);
    solver.setAbsoluteTolerance(1.e-13);
    solver.setRelativeTolerance(1.e-13);
    solver.setMaxStep(.005);
    C1HORect2Set set(affineCentre, affineCoordinates,
                     radii, affineRemainder);
    set.setCurrentTime(currentX);
    ITimeMap map(solver);
    map.stopAfterStep(true);
    do {
      (void)map(target, set);
      denseW = hull(denseW, set.getLastEnclosure()[0]);
      if (denseW.leftBound() <= 0.)
        throw std::runtime_error(
            "zero-energy reduced passage lost w>0");
    } while (!map.completed());
    const IMatrix flow = (IMatrix)set;

    IOdeSolver tangentSolver(field, 24);
    tangentSolver.setAbsoluteTolerance(1.e-13);
    tangentSolver.setRelativeTolerance(1.e-13);
    tangentSolver.setMaxStep(.005);
    C1HORect2Set::C0BaseSet tangentC0(
        affineCentre, affineCoordinates, radii, affineRemainder);
    C1HORect2Set::C1BaseSet tangentC1(reducedTangents);
    C1HORect2Set tangentSet(tangentC0, tangentC1);
    tangentSet.setCurrentTime(currentX);
    ITimeMap tangentMap(tangentSolver);
    (void)tangentMap(target, tangentSet);
    reducedTangents = (IMatrix)tangentSet;

    const IMatrix linear = flow * affineCoordinates;
    IVector nextCentre(dimension), nextRemainder(dimension);
    IMatrix nextCoordinates(dimension, dimension);
    for (int row = 0; row < dimension; ++row) {
      nextCentre[row] = interval(midpointValue(pointEvent[row]));
      nextRemainder[row] = pointEvent[row] - nextCentre[row];
      for (int column = 0; column < dimension; ++column) {
        nextCoordinates[row][column] =
            interval(midpointValue(linear[row][column]));
        nextRemainder[row] +=
            (linear[row][column] - nextCoordinates[row][column]) *
                radii[column] +
            flow[row][column] * affineRemainder[column];
      }
    }
    affineCentre = nextCentre;
    affineCoordinates = nextCoordinates;
    affineRemainder = nextRemainder;
    currentX = target;
  }
  const IVector reduced =
      affineCentre + affineCoordinates * radii + affineRemainder;
  const ReducedSpectralFormulas formulas = reducedSpectralFormulas();
  IMap coordinateMap(formulas.map);
  coordinateMap.setParameter("rc", parameterCentre[0]);
  coordinateMap.setParameter("a2c", parameterCentre[1]);
  coordinateMap.setParameter("epsc", parameterCentre[2]);
  IMatrix gradient(3, 9), pointGradient(3, 9);
  const IVector naive = coordinateMap(reduced, gradient);
  const IVector pointValue = coordinateMap(affineCentre, pointGradient);
  std::array<interval, 3> values{
      interval(0.), interval(0.), interval(0.)};
  std::array<interval, 3> derivatives{
      interval(0.), interval(0.), interval(0.)};
  std::array<interval, 3> bParameterDerivative;
  std::array<interval, 3> nParameterDerivative;
  std::array<interval, 3> alignedParameterDerivative;
  std::array<interval, 3> qParameterDerivative;
  for (int row = 0; row < 3; ++row) {
    interval meanValue = pointValue[row];
    for (int column = 0; column < dimension; ++column) {
      interval pointSlope(0.), slopeRange(0.);
      for (int state = 0; state < 9; ++state) {
        pointSlope += pointGradient[row][state] *
            affineCoordinates[state][column];
        slopeRange += gradient[row][state] *
            affineCoordinates[state][column];
      }
      meanValue += pointSlope * radii[column] +
          (slopeRange - pointSlope) * radii[column];
    }
    for (int state = 0; state < 9; ++state) {
      meanValue += gradient[row][state] * affineRemainder[state];
      derivatives[row] +=
          gradient[row][state] * reducedTangents[state][3];
    }
    if (!intersection(naive[row], meanValue, values[row]))
      throw std::runtime_error(
          "empty terminal affine-coordinate intersection");
  }
  for (int parameter = 0; parameter < 3; ++parameter) {
    bParameterDerivative[parameter] = interval(0.);
    nParameterDerivative[parameter] = interval(0.);
    alignedParameterDerivative[parameter] = interval(0.);
    for (int state = 0; state < 9; ++state) {
      bParameterDerivative[parameter] +=
          gradient[0][state] * reducedTangents[state][parameter];
      nParameterDerivative[parameter] +=
          gradient[1][state] * reducedTangents[state][parameter];
      alignedParameterDerivative[parameter] +=
          gradient[2][state] * reducedTangents[state][parameter];
    }
    qParameterDerivative[parameter] =
        reducedTangents[1][parameter];
  }
  return {values[0], values[1], values[2], derivatives[0], derivatives[1],
          reduced[1], reduced[7], denseW, bParameterDerivative,
          nParameterDerivative, alignedParameterDerivative,
          qParameterDerivative};
}

struct RootDerivativeData {
  interval bTheta;
  interval nTheta;
  interval slope;
  std::array<interval, 3> bOnNZeroParameterDerivative;
  std::array<interval, 3> qOnNZeroParameterDerivative;
  std::array<interval, 3> terminalDeterminantWQ;
};

RootDerivativeData propagateReducedExterior(
    const ReducedInitialData& initial,
    const Box& parameterCentre,
    const std::array<ExteriorSeamData, 3>& exterior) {
  const std::string r = "(rc+er)";
  const std::string a2 = "(a2c+ea)";
  const std::string epsilon = "(epsc+ee)";
  const std::string rootEpsilon = "sqrt(" + epsilon + ")";
  const std::string parameterR =
      "(2*" + a2 + "+4*" + rootEpsilon + "*" + r + "^3*" +
      a2 + "^2+4*" + rootEpsilon + "*" + r + "^2*" + a2 +
      "*x+" + rootEpsilon + "*" + r + "*x^2)";
  const std::string parameterA =
      "(2*" + r + "+2*" + rootEpsilon + "*" + r + "^4*" +
      a2 + "+4*" + rootEpsilon + "*" + r + "^3*x/3)";
  const std::string parameterEpsilon =
      "(" + r + "^4*" + a2 + "^2/(2*" + rootEpsilon + ")+2*" +
      r + "^3*" + a2 + "*x/(3*" + rootEpsilon + ")+" + r +
      "^2*x^2/(4*" + rootEpsilon + "))";
  const std::string fieldText =
      "time:x;par:rc,a2c,epsc;"
      "var:w,qq,er,ea,ee,dtheta,e,clock,z,vw,vq,dr,da,de;fun:"
      "w/x-qq^2/x+"
      "(2*" + r + "*" + a2 + "+" + rootEpsilon + "*" + r +
      "^4*" + a2 + "^2)*x+4*(1+" + rootEpsilon + "*" + r +
      "^3*" + a2 + ")*x^2/3+" + rootEpsilon + "*" + r +
      "^2*x^3/2,-x/sqrt(w),0,0,0,0,0,1/sqrt(w),0,"
      "vw/x-2*qq*vq/x,x*vw/(2*w^(3/2))," +
      parameterR + "*vq," + parameterA + "*vq," +
      parameterEpsilon + "*vq;";
  IMap field(fieldText);
  field.setParameter("rc", parameterCentre[0]);
  field.setParameter("a2c", parameterCentre[1]);
  field.setParameter("epsc", parameterCentre[2]);

  constexpr int dimension = 14;
  IVector centre(dimension), radii(dimension), remainder(dimension);
  IMatrix coordinates(dimension, dimension);
  for (int row = 0; row < dimension; ++row) {
    centre[row] = interval(0.);
    radii[row] = interval(0.);
    remainder[row] = interval(0.);
    for (int column = 0; column < dimension; ++column)
      coordinates[row][column] = interval(0.);
  }
  for (int row = 0; row < 9; ++row) {
    centre[row] = initial.centre[row];
    radii[row] = initial.radii[row];
    remainder[row] = initial.remainder[row];
    for (int column = 0; column < 9; ++column)
      coordinates[row][column] = initial.coordinates[row][column];
  }
  interval initialVW = exterior[0].vW;
  interval initialVQ = exterior[0].vQ;
  for (int parameter = 1; parameter < 3; ++parameter) {
    initialVW = hull(initialVW, exterior[parameter].vW);
    initialVQ = hull(initialVQ, exterior[parameter].vQ);
  }
  centre[9] = interval(midpointValue(initialVW));
  centre[10] = interval(midpointValue(initialVQ));
  remainder[9] = initialVW - centre[9];
  remainder[10] = initialVQ - centre[10];
  const interval initialX = rational(1, 20);
  for (int parameter = 0; parameter < 3; ++parameter) {
    const interval scaled =
        exterior[parameter].determinantWQ / initialX;
    centre[11 + parameter] = interval(midpointValue(scaled));
    remainder[11 + parameter] = scaled - centre[11 + parameter];
  }

  interval currentX = initialX;
  IVector affineCentre = centre;
  IMatrix affineCoordinates = coordinates;
  IVector affineRemainder = remainder;
  const std::array<interval, 13> targets = {
      rational(1, 5), rational(1, 2), interval(1.), interval(2.),
      interval(3.), rational(25, 8), rational(26, 8), rational(27, 8),
      rational(28, 8), rational(29, 8), rational(30, 8), rational(31, 8),
      interval(4.)};
  for (const interval& target : targets) {
    IOdeSolver pointSolver(field, 24);
    pointSolver.setAbsoluteTolerance(1.e-13);
    pointSolver.setRelativeTolerance(1.e-13);
    pointSolver.setMaxStep(.005);
    C1HORect2Set pointSet(affineCentre);
    pointSet.setCurrentTime(currentX);
    ITimeMap pointMap(pointSolver);
    const IVector pointEvent = pointMap(target, pointSet);

    IOdeSolver solver(field, 24);
    solver.setAbsoluteTolerance(1.e-13);
    solver.setRelativeTolerance(1.e-13);
    solver.setMaxStep(.005);
    C1HORect2Set set(
        affineCentre, affineCoordinates, radii, affineRemainder);
    set.setCurrentTime(currentX);
    ITimeMap map(solver);
    (void)map(target, set);
    const IMatrix flow = (IMatrix)set;
    const IMatrix linear = flow * affineCoordinates;
    IVector nextCentre(dimension), nextRemainder(dimension);
    IMatrix nextCoordinates(dimension, dimension);
    for (int row = 0; row < dimension; ++row) {
      nextCentre[row] = interval(midpointValue(pointEvent[row]));
      nextRemainder[row] = pointEvent[row] - nextCentre[row];
      for (int column = 0; column < dimension; ++column) {
        nextCoordinates[row][column] =
            interval(midpointValue(linear[row][column]));
        nextRemainder[row] +=
            (linear[row][column] - nextCoordinates[row][column]) *
                radii[column] +
            flow[row][column] * affineRemainder[column];
      }
    }
    affineCentre = nextCentre;
    affineCoordinates = nextCoordinates;
    affineRemainder = nextRemainder;
    currentX = target;
  }
  const IVector result =
      affineCentre + affineCoordinates * radii + affineRemainder;

  IVector base(9);
  for (int row = 0; row < 9; ++row) base[row] = result[row];
  const ReducedSpectralFormulas formulas = reducedSpectralFormulas();
  IMap coordinateMap(formulas.map);
  coordinateMap.setParameter("rc", parameterCentre[0]);
  coordinateMap.setParameter("a2c", parameterCentre[1]);
  coordinateMap.setParameter("epsc", parameterCentre[2]);
  IMatrix gradient(3, 9);
  (void)coordinateMap(base, gradient);
  IMap errorMap(formulas.error);
  errorMap.setParameter("rc", parameterCentre[0]);
  errorMap.setParameter("a2c", parameterCentre[1]);
  errorMap.setParameter("epsc", parameterCentre[2]);
  IMatrix errorGradient(1, 9);
  (void)errorMap(base, errorGradient);
  const interval bTheta =
      gradient[0][0] * result[9] + gradient[0][1] * result[10];
  const interval nTheta =
      gradient[1][0] * result[9] + gradient[1][1] * result[10];
  if (nTheta.rightBound() >= 0.)
    throw std::runtime_error(
        "reduced exterior passage does not keep n_theta<0");
  const interval physicalR = parameterCentre[0] + base[2];
  const interval physicalA2 = parameterCentre[1] + base[3];
  const interval physicalRootEpsilon =
      sqrt(parameterCentre[2] + base[4]);
  const interval physicalM =
      interval(4.) + physicalR * physicalA2;
  const interval physicalLambda = sqrt(
      physicalRootEpsilon *
      (interval(2.) + physicalRootEpsilon * sqr(physicalR) * physicalM));
  const interval nQ =
      -base[1] /
      (interval(8.) * physicalM * physicalLambda);
  std::array<interval, 3> bDerivative;
  std::array<interval, 3> qDerivative;
  std::array<interval, 3> determinant;
  for (int parameter = 0; parameter < 3; ++parameter) {
    determinant[parameter] = interval(4.) * result[11 + parameter];
    const interval explicitN = gradient[1][2 + parameter];
    bDerivative[parameter] =
        errorGradient[0][0] *
            (nQ * determinant[parameter] -
             result[9] * explicitN) /
            nTheta +
        errorGradient[0][2 + parameter];
    qDerivative[parameter] =
        (-gradient[1][0] * determinant[parameter] -
         result[10] * explicitN) /
        nTheta;
  }
  std::array<interval, 3> subdividedBDerivative;
  bool subdividedInitialized = false;
  constexpr int epsilonParts = 16;
  constexpr int thetaParts = 8;
  constexpr int wRemainderParts = 4;
  constexpr int qRemainderParts = 4;
  for (int epsilonPart = 0; epsilonPart < epsilonParts; ++epsilonPart) {
      for (int thetaPart = 0; thetaPart < thetaParts; ++thetaPart) {
        for (int wPart = 0; wPart < wRemainderParts; ++wPart) {
          for (int qPart = 0; qPart < qRemainderParts; ++qPart) {
            IVector subRadii = radii;
            const auto partition = [&](int axis, int index, int count) {
              const interval leftEndpoint(radii[axis].leftBound());
              const interval diameter =
                  interval(radii[axis].rightBound()) - leftEndpoint;
              const interval lower = leftEndpoint +
                  diameter * rational(index, count);
              const interval upper = leftEndpoint +
                  diameter * rational(index + 1, count);
              return intervalFromEndpoints(lower, upper);
            };
            subRadii[2] = partition(2, epsilonPart, epsilonParts);
            subRadii[3] = partition(3, thetaPart, thetaParts);
            subRadii[5] = partition(5, wPart, wRemainderParts);
            subRadii[6] = partition(6, qPart, qRemainderParts);
            const IVector subState = affineCentre +
                affineCoordinates * subRadii + affineRemainder;
            IVector subBase(9);
            for (int row = 0; row < 9; ++row)
              subBase[row] = subState[row];
            IMatrix subGradient(3, 9), subErrorGradient(1, 9);
            (void)coordinateMap(subBase, subGradient);
            (void)errorMap(subBase, subErrorGradient);
            const interval subNTheta =
                subGradient[1][0] * subState[9] +
                subGradient[1][1] * subState[10];
            if (subNTheta.rightBound() >= 0.)
              throw std::runtime_error(
                  "terminal affine subbox does not keep n_theta<0");
            const interval subR = parameterCentre[0] + subBase[2];
            const interval subA2 = parameterCentre[1] + subBase[3];
            const interval subRootEpsilon =
                sqrt(parameterCentre[2] + subBase[4]);
            const interval subM = interval(4.) + subR * subA2;
            const interval subLambda = sqrt(
                subRootEpsilon *
                (interval(2.) +
                 subRootEpsilon * sqr(subR) * subM));
            const interval subNQ =
                -subBase[1] / (interval(8.) * subM * subLambda);
            for (int parameter = 0; parameter < 3; ++parameter) {
              const interval subD =
                  interval(4.) * subState[11 + parameter];
              const interval subExplicitN =
                  subGradient[1][2 + parameter];
              const interval subDerivative =
                  subErrorGradient[0][0] *
                      (subNQ * subD -
                       subState[9] * subExplicitN) /
                      subNTheta +
                  subErrorGradient[0][2 + parameter];
              subdividedBDerivative[parameter] =
                  subdividedInitialized
                      ? hull(subdividedBDerivative[parameter],
                             subDerivative)
                      : subDerivative;
            }
            subdividedInitialized = true;
          }
      }
    }
  }
  bDerivative = subdividedBDerivative;
  return {bTheta, nTheta, bTheta / nTheta,
          bDerivative, qDerivative, determinant};
}

enum class PhaseRegion { LowerFace, UpperFace, FullStrip };

CellResult evaluateCellRegion(const Box& parameterCell, PhaseRegion region,
                              int graphSliceIndex,
                              int graphSliceCount = 2,
                              const interval* customThetaCentre = nullptr,
                              const interval* customThetaHalfWidth = nullptr,
                              bool computeExterior = false) {
  if (graphSliceCount <= 0 || graphSliceIndex < 0 ||
      graphSliceIndex >= graphSliceCount)
    throw std::invalid_argument("invalid source graph-error slice");
  Box centre;
  Box offsets;
  bool degenerateParameterCell = true;
  for (int index = 0; index < 3; ++index) {
    centre[index] = interval(midpointValue(parameterCell[index]));
    offsets[index] = parameterCell[index] - centre[index];
    degenerateParameterCell = degenerateParameterCell &&
        offsets[index].leftBound() == 0. &&
        offsets[index].rightBound() == 0.;
  }
  const bool lowerFace = region == PhaseRegion::LowerFace;
  const bool upperFace = region == PhaseRegion::UpperFace;
  const interval thetaCentre = customThetaCentre != nullptr
      ? *customThetaCentre
      : (lowerFace ? -thetaFace()
                   : (upperFace ? thetaFace() : interval(0.)));
  const interval fullTheta = thetaFace() + thetaHalfWidth();
  const interval thetaOffset = customThetaHalfWidth != nullptr
      ? intervalFromEndpoints(-*customThetaHalfWidth,
                              *customThetaHalfWidth)
      : (region == PhaseRegion::FullStrip
             ? intervalFromEndpoints(-fullTheta, fullTheta)
             : intervalFromEndpoints(-thetaHalfWidth(), thetaHalfWidth()));
  const interval graphSliceHalfWidth =
      graphC0() * rational(1, graphSliceCount);
  const interval graphCentre = -graphC0() +
      graphSliceHalfWidth * rational(2L * graphSliceIndex + 1);
  const interval graphOffset = intervalFromEndpoints(
      -graphSliceHalfWidth, graphSliceHalfWidth);
  const interval katoU1 = sourceKatoU1(
      centre, offsets, thetaCentre, thetaOffset,
      graphCentre, graphOffset);
  if (katoU1.leftBound() <= 0.)
    throw std::runtime_error(
        "slanted source strip leaves the positive-u1 Kato phase domain");
  InitialData initial = initialData(centre, offsets, thetaCentre,
                                   thetaOffset, graphCentre, graphOffset);
  const interval sourceU = initial.centre[0] +
      initial.coordinates[0] * initial.radii + initial.remainder[0];
  if (sourceU.leftBound() <= 0.)
    throw std::runtime_error(
        "true source strip does not start on the positive-U side");

  const SeamData seam = hitFixedCut(
      initial, centre, -rational(1, 20), 13);
  if (seam.event[1].rightBound() >= 0.)
    throw std::runtime_error(
        "finite seam is not contained in P<0");
  // The source formula enforces H=0 algebraically: after using
  // 2*alpha*beta=h, substitution reduces H to
  // 2*h*(u1*s2+s1*u2)+A*U^3/3-B*U^4/4, and the displayed definition of
  // s2 cancels this expression term by term.  The interval energy is only
  // a correlation-blind consistency enclosure for that exact identity.
  if (!seam.energy.contains(0.))
    throw std::runtime_error(
        "finite seam energy enclosure lost the exact zero-energy image");
  const ReducedInitialData reducedInitial = reducedInitialData(seam);
  const TerminalData terminal = propagateReduced(reducedInitial, centre);
  std::array<interval, 3> rootParameterDerivative{
      interval(0.), interval(0.), interval(0.)};
  interval fixedEtaNTheta(0.);
  interval exteriorSeamP(0.);
  bool rootDerivativeComputed = false;
  if (computeExterior) {
    std::array<ExteriorSeamData, 3> exterior;
    for (int parameter = 0; parameter < 3; ++parameter) {
      exterior[parameter] =
          hitFixedCutExterior(initial, centre, parameter);
      include(parameter != 0, exteriorSeamP, exterior[parameter].eventP);
    }
    const RootDerivativeData root =
        propagateReducedExterior(reducedInitial, centre, exterior);
    rootParameterDerivative = root.bOnNZeroParameterDerivative;
    fixedEtaNTheta = root.nTheta;
    rootDerivativeComputed = true;
  }
  // On an exact point parameter cell, the full-cell and centre-parameter
  // inputs coincide interval by interval.  Reuse the already checked
  // enclosure rather than repeat the identical rigorous propagation.
  TerminalData centreTerminal = terminal;
  if (!degenerateParameterCell) {
    const Box zeroOffsets = {interval(0.), interval(0.), interval(0.)};
    const InitialData centreInitial = initialData(
        centre, zeroOffsets, thetaCentre, thetaOffset,
        graphCentre, graphOffset);
    const SeamData centreSeam = hitFixedCut(
        centreInitial, centre, -rational(1, 20), 13);
    if (centreSeam.event[1].rightBound() >= 0.)
      throw std::runtime_error(
          "centre-parameter seam is not contained in P<0");
    if (!centreSeam.energy.contains(0.))
      throw std::runtime_error(
          "centre-parameter energy enclosure lost the exact zero-energy image");
    centreTerminal = propagateReduced(
        reducedInitialData(centreSeam), centre);
  }

  interval meanValueB = centreTerminal.b;
  interval meanValueN = centreTerminal.n;
  interval meanValueQ = centreTerminal.q;
  for (int parameter = 0; parameter < 3; ++parameter) {
    meanValueB += terminal.bParameterDerivative[parameter] *
        offsets[parameter];
    meanValueN += terminal.nParameterDerivative[parameter] *
        offsets[parameter];
    meanValueQ += terminal.qParameterDerivative[parameter] *
        offsets[parameter];
  }
  interval tightB, tightN, tightQ;
  if (!intersection(terminal.b, meanValueB, tightB) ||
      !intersection(terminal.n, meanValueN, tightN) ||
      !intersection(terminal.q, meanValueQ, tightQ))
    throw std::runtime_error(
        "empty parameter mean-value intersection at the terminal cut");
  const Spectral coordinates{tightB, tightN,
                             terminal.db, terminal.dn};
  const interval coneMargin = -coordinates.dn -
      lowerGraphSlope() * absoluteEnvelope(coordinates.db);
  interval sourceSlope(0., 1.e300);
  if (coordinates.dn.rightBound() < 0.)
    sourceSlope =
        absoluteEnvelope(coordinates.db) / (-coordinates.dn);
  const interval graphBase = lowerGraphBaseHalfWidth();
  const interval graphNormal = lowerGraphNormalHalfWidth();

  Verdict status = Verdict::Pass;
  if (!(tightQ.leftBound() > -rational(19, 2).rightBound() &&
        tightQ.rightBound() < -rational(9).leftBound()))
    status = Verdict::Inconclusive;
  if (region == PhaseRegion::FullStrip) {
    if (!(coneMargin.leftBound() > 0. &&
          coordinates.b.leftBound() > (-graphBase).rightBound() &&
          coordinates.b.rightBound() < graphBase.leftBound()))
      status = Verdict::Inconclusive;
  } else if (lowerFace) {
    if (!(coordinates.n.leftBound() > graphNormal.rightBound()))
      status = Verdict::Inconclusive;
  } else if (!(coordinates.n.rightBound() < (-graphNormal).leftBound())) {
    status = Verdict::Inconclusive;
  }
  return {coordinates.b, coordinates.n, terminal.aligned,
          centreTerminal.aligned, coordinates.db, coordinates.dn,
          sourceSlope, coneMargin, tightQ, katoU1, sourceU,
          seam.event[1], seam.preSeamMargin, terminal.denseW,
          seam.hitTime + terminal.reducedClock,
          rootParameterDerivative, fixedEtaNTheta, exteriorSeamP,
          rootDerivativeComputed, status};
}

Box parameterCell(int rIndex, int rCount, int aIndex, int aCount,
                  int epsilonIndex, int epsilonCount) {
  if (rCount <= 0 || aCount <= 0 || epsilonCount <= 0 ||
      rIndex < 0 || rIndex >= rCount || aIndex < 0 || aIndex >= aCount ||
      epsilonIndex < 0 || epsilonIndex >= epsilonCount)
    throw std::invalid_argument("invalid parameter grid cell");
  const interval rLower = rational(rCount + rIndex, 100L * rCount);
  const interval rUpper = rational(rCount + rIndex + 1, 100L * rCount);
  const interval aLower = rational(-aCount + 2L * aIndex, 4L * aCount);
  const interval aUpper = rational(-aCount + 2L * (aIndex + 1),
                                   4L * aCount);
  const interval epsilonLower = rational(4L * epsilonCount +
                                             2L * epsilonIndex,
                                         5L * epsilonCount);
  const interval epsilonUpper = rational(4L * epsilonCount +
                                             2L * (epsilonIndex + 1),
                                         5L * epsilonCount);
  return {intervalFromEndpoints(rLower, rUpper),
          intervalFromEndpoints(aLower, aUpper),
          intervalFromEndpoints(epsilonLower, epsilonUpper)};
}

struct Aggregate {
  bool initialized = false;
  bool lowerInitialized = false;
  bool upperInitialized = false;
  bool stripInitialized = false;
  interval lowerB;
  interval lowerN;
  interval upperB;
  interval upperN;
  interval stripB;
  interval stripN;
  interval stripAligned;
  interval centreAligned;
  interval db;
  interval dn;
  interval sourceSlope;
  interval coneMargin;
  interval terminalQ;
  interval phaseDomainMargin;
  interval sourceU;
  interval preSeamMargin;
  interval denseW;
  interval hitTime;
  bool rootDerivativeInitialized = false;
  std::array<interval, 3> bOnNZeroParameterDerivative{
      interval(0.), interval(0.), interval(0.)};
  interval fixedEtaNTheta;
  interval exteriorSeamP;
  Verdict status = Verdict::Pass;
  std::size_t evaluationCount = 0;
  std::size_t inconclusiveCount = 0;
  std::array<int, 5> firstInconclusive{{-1, -1, -1, -1, -1}};
};

void includeResult(Aggregate& aggregate, const CellResult& result,
                   PhaseRegion region, int rIndex, int aIndex,
                   int epsilonIndex, int graphHalf) {
  if (region == PhaseRegion::LowerFace) {
    include(aggregate.lowerInitialized, aggregate.lowerB, result.b);
    include(aggregate.lowerInitialized, aggregate.lowerN, result.n);
    aggregate.lowerInitialized = true;
  } else if (region == PhaseRegion::UpperFace) {
    include(aggregate.upperInitialized, aggregate.upperB, result.b);
    include(aggregate.upperInitialized, aggregate.upperN, result.n);
    aggregate.upperInitialized = true;
  } else {
    include(aggregate.stripInitialized, aggregate.stripB, result.b);
    include(aggregate.stripInitialized, aggregate.stripN, result.n);
    include(aggregate.stripInitialized, aggregate.stripAligned,
            result.aligned);
    include(aggregate.stripInitialized, aggregate.centreAligned,
            result.centreAligned);
    include(aggregate.stripInitialized, aggregate.db, result.db);
    include(aggregate.stripInitialized, aggregate.dn, result.dn);
    include(aggregate.stripInitialized, aggregate.sourceSlope,
            result.sourceSlope);
    include(aggregate.stripInitialized, aggregate.coneMargin,
            result.coneMargin);
    aggregate.stripInitialized = true;
  }
  if (result.rootDerivativeComputed) {
    for (int parameter = 0; parameter < 3; ++parameter)
      include(aggregate.rootDerivativeInitialized,
              aggregate.bOnNZeroParameterDerivative[parameter],
              result.bOnNZeroParameterDerivative[parameter]);
    include(aggregate.rootDerivativeInitialized,
            aggregate.fixedEtaNTheta, result.fixedEtaNTheta);
    include(aggregate.rootDerivativeInitialized,
            aggregate.exteriorSeamP, result.exteriorSeamP);
    aggregate.rootDerivativeInitialized = true;
  }
  include(aggregate.initialized, aggregate.terminalQ, result.terminalQ);
  include(aggregate.initialized, aggregate.phaseDomainMargin,
          result.phaseDomainMargin);
  include(aggregate.initialized, aggregate.sourceU, result.sourceU);
  include(aggregate.initialized, aggregate.preSeamMargin,
          result.preSeamMargin);
  include(aggregate.initialized, aggregate.denseW, result.denseW);
  include(aggregate.initialized, aggregate.hitTime, result.hitTime);
  aggregate.initialized = true;
  aggregate.status = combine(aggregate.status, result.status);
  ++aggregate.evaluationCount;
  if (result.status != Verdict::Pass) {
    if (aggregate.inconclusiveCount == 0)
      aggregate.firstInconclusive =
          {{rIndex, aIndex, epsilonIndex,
            region == PhaseRegion::LowerFace
                ? 0
                : (region == PhaseRegion::UpperFace ? 1 : 2),
            graphHalf}};
    ++aggregate.inconclusiveCount;
  }
}

std::string boolJson(bool value) { return value ? "true" : "false"; }

void printResult(const Aggregate& aggregate, int rCount, int aCount,
                 int epsilonCount, bool completeCover) {
  const auto rounding = rfsn::rigorous::runRoundingSelfTests();
  const Verdict mathematicalStatus = aggregate.status;
  const Verdict status = combine(rounding.status, mathematicalStatus);
  const interval coordinateJacobian =
      interval(1.) + rational(11, 8) *
          intervalFromEndpoints(-graphPhaseC1(), graphPhaseC1());
  const interval graphBase = lowerGraphBaseHalfWidth();
  const interval graphNormal = lowerGraphNormalHalfWidth();
  std::cout << "{\"schema_version\":"
            << "\"rfsn-vdp-v5-source-incidence-probe/2\","
            << "\"box_id\":\"vdp-positive-box-v2\","
            << "\"scope\":\"ZERO_ENERGY_TRUE_SOURCE_TO_V5_LOWER_GRAPH\","
            << "\"section\":\"FIRST_U_MINUS_4\","
            << "\"status\":\"" << verdictName(status) << "\","
            << "\"mathematical_status\":\""
            << verdictName(mathematicalStatus) << "\","
            << "\"claim_bearing\":false,"
            << "\"cover\":{\"r_slabs\":" << rCount
            << ",\"a2_slabs\":" << aCount
            << ",\"epsilon_slabs\":" << epsilonCount
            << ",\"graph_error_halves\":2,\"phase_faces\":2,"
            << "\"full_phase_strips\":1,"
            << "\"parameter_cell_count\":"
            << static_cast<long long>(rCount) * aCount * epsilonCount
            << ",\"evaluation_count\":" << aggregate.evaluationCount
            << ",\"complete_v2_cover\":" << boolJson(completeCover)
            << "},\"source_contract\":{"
            << "\"radius\":\"1/100\",\"graph_c0\":\"1/200000\","
            << "\"graph_phase_c1\":\"3/1000000\","
            << "\"phase_slant\":\"-11/8\","
            << "\"theta_faces\":[\"-4/25000000\",\"4/25000000\"],"
            << "\"theta_face_half_width\":\"1/1000000000\","
            << "\"theta_coordinate_jacobian_lower\":"
            << intervalJson(coordinateJacobian) << "},"
            << "\"target_graph_contract\":{"
            << "\"base_half_width\":\"27/200000\","
            << "\"normal_half_width\":\"1/10000\","
            << "\"slope_bound\":\"7/10\"},"
            << "\"enclosures\":{"
            << "\"lower_face_b\":" << intervalJson(aggregate.lowerB)
            << ",\"lower_face_n\":" << intervalJson(aggregate.lowerN)
            << ",\"upper_face_b\":" << intervalJson(aggregate.upperB)
            << ",\"upper_face_n\":" << intervalJson(aggregate.upperN)
            << ",\"full_strip_b\":" << intervalJson(aggregate.stripB)
            << ",\"full_strip_n\":" << intervalJson(aggregate.stripN)
            << ",\"full_strip_aligned\":"
            << intervalJson(aggregate.stripAligned)
            << ",\"centre_parameter_aligned\":"
            << intervalJson(aggregate.centreAligned)
            << ",\"db_dtheta\":" << intervalJson(aggregate.db)
            << ",\"dn_dtheta\":" << intervalJson(aggregate.dn)
            << ",\"source_abs_db_over_minus_dn\":"
            << intervalJson(aggregate.sourceSlope)
            << ",\"fixed_eta_b_on_n_zero_parameter_derivative\":["
            << intervalJson(aggregate.bOnNZeroParameterDerivative[0])
            << ','
            << intervalJson(aggregate.bOnNZeroParameterDerivative[1])
            << ','
            << intervalJson(aggregate.bOnNZeroParameterDerivative[2])
            << "],\"root_derivative_computed\":"
            << boolJson(aggregate.rootDerivativeInitialized)
            << ",\"fixed_eta_n_theta\":"
            << intervalJson(aggregate.fixedEtaNTheta)
            << ",\"exterior_seam_P\":"
            << intervalJson(aggregate.exteriorSeamP)
            << ",\"incidence_cone_margin\":"
            << intervalJson(aggregate.coneMargin)
            << ",\"terminal_Q\":" << intervalJson(aggregate.terminalQ)
            << ",\"source_u1_phase_domain_margin\":"
            << intervalJson(aggregate.phaseDomainMargin)
            << ",\"source_U\":" << intervalJson(aggregate.sourceU)
            << ",\"pre_seam_U_margin\":"
            << intervalJson(aggregate.preSeamMargin)
            << ",\"dense_W\":" << intervalJson(aggregate.denseW)
            << ",\"first_hit_time\":" << intervalJson(aggregate.hitTime)
            << "},\"gates\":{"
            << "\"theta_coordinate_regular\":"
            << boolJson(coordinateJacobian.leftBound() > 0.) << ','
            << "\"lower_face_above_graph_tube\":"
            << boolJson(aggregate.lowerN.leftBound() > graphNormal.rightBound())
            << ",\"upper_face_below_graph_tube\":"
            << boolJson(aggregate.upperN.rightBound() <
                        (-graphNormal).leftBound())
            << ",\"terminal_b_inside_graph_base\":"
            << boolJson(aggregate.stripB.leftBound() >
                            (-graphBase).rightBound() &&
                        aggregate.stripB.rightBound() < graphBase.leftBound())
            << ",\"b_phase_orientation_positive\":"
            << boolJson(aggregate.db.leftBound() > 0.)
            << ",\"slope_7_10_separation\":"
            << boolJson(aggregate.coneMargin.leftBound() > 0.)
            << ",\"negative_K1_sheet_patch\":"
            << boolJson(aggregate.terminalQ.leftBound() >
                            -rational(19, 2).rightBound() &&
                        aggregate.terminalQ.rightBound() <
                            -rational(9).leftBound())
            << ",\"source_phase_domain\":"
            << boolJson(aggregate.phaseDomainMargin.leftBound() > 0.)
            << ",\"source_positive_U\":"
            << boolJson(aggregate.sourceU.leftBound() > 0.)
            << ",\"no_earlier_finite_seam_hit\":"
            << boolJson(aggregate.preSeamMargin.leftBound() > 0.)
            << ",\"reduced_x_clock_regular\":"
            << boolJson(aggregate.denseW.leftBound() > 0.)
            << "},"
            << "\"inconclusive_evaluation_count\":"
            << aggregate.inconclusiveCount << ','
            << "\"first_inconclusive_index\":["
            << aggregate.firstInconclusive[0] << ','
            << aggregate.firstInconclusive[1] << ','
            << aggregate.firstInconclusive[2] << ','
            << aggregate.firstInconclusive[3] << ','
            << aggregate.firstInconclusive[4] << "],"
            << "\"rounding_self_test\":{\"status\":\""
            << verdictName(rounding.status) << "\"},"
            << "\"claim_boundary\":{"
            << "\"established_if_pass\":\"uniform source strip signs and "
               "transversality against every lower graph with |g'|<=7/10\","
            << "\"open_scope\":[\"invoke the K1 graph transform in a "
               "composite theorem\",\"identify the resulting stationary "
               "PDE branch\"]}}\n";
}

}  // namespace

int main(int argc, char** argv) {
  try {
    if (argc != 5 && argc != 8 && argc != 9)
      throw std::invalid_argument(
          "usage: probe cover NR NA NE | probe cell NR NA NE IR IA IE | "
          "probe slab NR NA NE IR IA IE IS | "
          "probe incidence-cell NR NA NE IR IA IE | "
          "probe incidence-merged-cell NR NA NE IR IA IE");
    const std::string mode(argv[1]);
    const int rCount = std::stoi(argv[2]);
    const int aCount = std::stoi(argv[3]);
    const int epsilonCount = std::stoi(argv[4]);
    Aggregate aggregate;
    if (mode == "incidence-cell" ||
        mode == "incidence-merged-cell") {
      if (argc != 8)
        throw std::invalid_argument(
            "incidence cell mode requires IR IA IE");
      const bool mergedExteriorMode =
          mode == "incidence-merged-cell";
      const int rIndex = std::stoi(argv[5]);
      const int aIndex = std::stoi(argv[6]);
      const int epsilonIndex = std::stoi(argv[7]);
      const Box cell = parameterCell(rIndex, rCount, aIndex, aCount,
                                     epsilonIndex, epsilonCount);
      Box centreCell;
      Box offsets;
      for (int parameter = 0; parameter < 3; ++parameter) {
        centreCell[parameter] =
            interval(midpointValue(cell[parameter]));
        offsets[parameter] = cell[parameter] - centreCell[parameter];
      }
      const interval continuationFace = rational(1, 25000);
      constexpr int slabCount = 8;
      constexpr int graphErrorHalfCount = 2;
      constexpr int anchorGraphSliceCount = 4;
      constexpr int mergedExteriorGroupCount = 8;
      static_assert(slabCount % mergedExteriorGroupCount == 0);
      constexpr int mergedExteriorSlabsPerGroup =
          slabCount / mergedExteriorGroupCount;
      const interval slabHalfWidth =
          continuationFace / interval(slabCount);
      const interval graphBase = lowerGraphBaseHalfWidth();
      const interval graphNormal = lowerGraphNormalHalfWidth();
      const interval sourceSlopeLimit = rational(1, 2);
      interval anchorAligned(0.);
      interval rootDerivativeR(0.);
      interval rootDerivativeA(0.);
      interval rootDerivativeEpsilon(0.);
      interval fixedEtaNTheta(0.);
      interval exteriorSeamP(0.);
      interval sourceSlope(0.);
      interval candidateQ(0.);
      interval candidatePhaseDomainMargin(0.);
      interval candidateSourceU(0.);
      interval candidateSeamP(0.);
      interval candidatePreSeamMargin(0.);
      interval candidateDenseW(0.);
      interval continuationNTheta(0.);
      interval anchorRootPhase(0.);
      interval anchorRootN(0.);
      std::array<interval, anchorGraphSliceCount> anchorNAtZero;
      std::array<std::array<interval, mergedExteriorGroupCount>,
                 graphErrorHalfCount> mergedCandidatePhaseHullByGroup;
      bool anchorInitialized = false;
      bool rootInitialized = false;
      bool slopeInitialized = false;
      bool qInitialized = false;
      bool passageInitialized = false;
      bool phaseDerivativeInitialized = false;
      bool anchorRootNInitialized = false;
      std::array<std::array<bool, mergedExteriorGroupCount>,
                 graphErrorHalfCount>
          mergedCandidatePhaseHullInitializedByGroup{};
      std::array<bool, anchorGraphSliceCount> anchorNewtonBySlice{};
      std::array<bool, anchorGraphSliceCount> anchorRootNBySlice{};
      std::array<std::array<bool, mergedExteriorGroupCount>,
                 graphErrorHalfCount>
          mergedCandidateNIncludesZeroByGroup{};
      std::array<std::array<bool, slabCount>, graphErrorHalfCount>
          zeroCandidateBySlabAndHalf{};
      std::array<bool, 2> continuationFacesByHalf{{true, true}};
      bool derivativeGate = true;
      bool phaseMonotonicityGate = true;
      bool sourceSlopeGate = true;
      bool qGate = true;
      bool passageGate = true;
      bool exteriorGate = true;
      std::array<int, 2> zeroCandidateCount{{0, 0}};
      std::array<int, 2> graphTubeCandidateCount{{0, 0}};
      int exteriorEvaluationCount = 0;
      const auto overlaps = [](const interval& left,
                               const interval& right) {
        return left.leftBound() <= right.rightBound() &&
            right.leftBound() <= left.rightBound();
      };
      const interval graphTube =
          intervalFromEndpoints(-graphNormal, graphNormal);
      const interval coordinateJacobian =
          interval(1.) + rational(11, 8) *
              intervalFromEndpoints(-graphPhaseC1(), graphPhaseC1());
      const interval errorHalf = graphC0() / interval(2.);
      const interval negativeErrorHalf =
          -errorHalf + intervalFromEndpoints(-errorHalf, errorHalf);
      const interval positiveErrorHalf =
          errorHalf + intervalFromEndpoints(-errorHalf, errorHalf);
      const bool completeGraphErrorHalfUnion =
          negativeErrorHalf.leftBound() <= (-graphC0()).leftBound() &&
          negativeErrorHalf.rightBound() >= 0. &&
          positiveErrorHalf.leftBound() <= 0. &&
          positiveErrorHalf.rightBound() >= graphC0().rightBound();
      bool completeAnchorGraphSliceUnion = true;
      interval previousGraphSliceUpper(0.);
      const interval anchorGraphSliceHalfWidth =
          graphC0() * rational(1, anchorGraphSliceCount);
      for (int graphSlice = 0; graphSlice < anchorGraphSliceCount;
           ++graphSlice) {
        const interval graphSliceCentre = -graphC0() +
            anchorGraphSliceHalfWidth * rational(2L * graphSlice + 1);
        const interval graphSliceLower =
            graphSliceCentre - anchorGraphSliceHalfWidth;
        const interval graphSliceUpper =
            graphSliceCentre + anchorGraphSliceHalfWidth;
        if (graphSlice == 0) {
          completeAnchorGraphSliceUnion =
              completeAnchorGraphSliceUnion &&
              graphSliceLower.leftBound() <= (-graphC0()).leftBound();
        } else {
          completeAnchorGraphSliceUnion =
              completeAnchorGraphSliceUnion &&
              previousGraphSliceUpper.rightBound() >=
                  graphSliceLower.leftBound();
        }
        previousGraphSliceUpper = graphSliceUpper;
      }
      completeAnchorGraphSliceUnion = completeAnchorGraphSliceUnion &&
          previousGraphSliceUpper.rightBound() >= graphC0().rightBound();
      bool completePhaseSlabUnion = true;
      interval previousSlabUpper(0.);
      for (int slabIndex = 0; slabIndex < slabCount; ++slabIndex) {
        const interval slabCentre = -continuationFace +
            continuationFace *
                rational(2L * slabIndex + 1, slabCount);
        const interval slabLower = slabCentre - slabHalfWidth;
        const interval slabUpper = slabCentre + slabHalfWidth;
        if (slabIndex == 0) {
          completePhaseSlabUnion = completePhaseSlabUnion &&
              slabLower.leftBound() <=
                  (-continuationFace).leftBound();
        } else {
          completePhaseSlabUnion = completePhaseSlabUnion &&
              previousSlabUpper.rightBound() >=
                  slabLower.leftBound();
        }
        previousSlabUpper = slabUpper;
      }
      completePhaseSlabUnion = completePhaseSlabUnion &&
          previousSlabUpper.rightBound() >=
              continuationFace.rightBound();
      const interval zeroTheta(0.);
      const interval zeroThetaHalfWidth(0.);
      for (int graphSlice = 0; graphSlice < anchorGraphSliceCount;
           ++graphSlice)
        anchorNAtZero[graphSlice] = evaluateCellRegion(
            centreCell, PhaseRegion::FullStrip, graphSlice,
            anchorGraphSliceCount, &zeroTheta,
            &zeroThetaHalfWidth).n;
      for (int graphHalf = 0; graphHalf < graphErrorHalfCount;
           ++graphHalf) {
        const interval lowerCentre = -continuationFace;
        const interval upperCentre = continuationFace;
        const interval faceHalfWidth = thetaHalfWidth();
        const CellResult continuationLower = evaluateCellRegion(
            cell, PhaseRegion::LowerFace, graphHalf,
            graphErrorHalfCount,
            &lowerCentre, &faceHalfWidth);
        const CellResult continuationUpper = evaluateCellRegion(
            cell, PhaseRegion::UpperFace, graphHalf,
            graphErrorHalfCount,
            &upperCentre, &faceHalfWidth);
        continuationFacesByHalf[graphHalf] =
            continuationLower.n.leftBound() > graphNormal.rightBound() &&
            continuationUpper.n.rightBound() <
                (-graphNormal).leftBound();

        for (int slabIndex = 0; slabIndex < slabCount; ++slabIndex) {
          const interval slabCentre = -continuationFace +
              continuationFace *
                  rational(2L * slabIndex + 1, slabCount);
          const CellResult slab = evaluateCellRegion(
              cell, PhaseRegion::FullStrip, graphHalf,
              graphErrorHalfCount,
              &slabCentre, &slabHalfWidth, false);
          include(phaseDerivativeInitialized, continuationNTheta,
                  slab.dn);
          phaseDerivativeInitialized = true;
          phaseMonotonicityGate = phaseMonotonicityGate &&
              slab.dn.rightBound() < 0.;
          const bool zeroCandidate = slab.n.contains(0.);
          const bool graphTubeCandidate = overlaps(slab.n, graphTube);
          if (zeroCandidate) {
            zeroCandidateBySlabAndHalf[graphHalf][slabIndex] = true;
            ++zeroCandidateCount[graphHalf];
            if (mergedExteriorMode) {
              const int mergedGroup =
                  slabIndex * mergedExteriorGroupCount / slabCount;
              const interval slabPhase = intervalFromEndpoints(
                  slabCentre - slabHalfWidth,
                  slabCentre + slabHalfWidth);
              include(
                  mergedCandidatePhaseHullInitializedByGroup[graphHalf]
                                                                 [mergedGroup],
                  mergedCandidatePhaseHullByGroup[graphHalf][mergedGroup],
                  slabPhase);
              mergedCandidatePhaseHullInitializedByGroup[graphHalf]
                                                              [mergedGroup] =
                  true;
            }
          }
          if (zeroCandidate && !mergedExteriorMode) {
            const CellResult rootSlab = evaluateCellRegion(
                cell, PhaseRegion::FullStrip, graphHalf,
                graphErrorHalfCount,
                &slabCentre, &slabHalfWidth, true);
            ++exteriorEvaluationCount;
            derivativeGate = derivativeGate &&
                rootSlab.rootDerivativeComputed &&
                rootSlab.fixedEtaNTheta.rightBound() < 0.;
            exteriorGate = exteriorGate &&
                rootSlab.exteriorSeamP.rightBound() < 0.;
            if (rootSlab.rootDerivativeComputed) {
              include(rootInitialized, rootDerivativeR,
                      rootSlab.bOnNZeroParameterDerivative[0]);
              include(rootInitialized, rootDerivativeA,
                      rootSlab.bOnNZeroParameterDerivative[1]);
              include(rootInitialized, rootDerivativeEpsilon,
                      rootSlab.bOnNZeroParameterDerivative[2]);
              include(rootInitialized, fixedEtaNTheta,
                      rootSlab.fixedEtaNTheta);
              include(rootInitialized, exteriorSeamP,
                      rootSlab.exteriorSeamP);
              rootInitialized = true;
            }
          }
          if (graphTubeCandidate) {
            ++graphTubeCandidateCount[graphHalf];
            include(slopeInitialized, sourceSlope, slab.sourceSlope);
            include(qInitialized, candidateQ, slab.terminalQ);
            include(passageInitialized, candidatePhaseDomainMargin,
                    slab.phaseDomainMargin);
            include(passageInitialized, candidateSourceU,
                    slab.sourceU);
            include(passageInitialized, candidateSeamP,
                    slab.seamP);
            include(passageInitialized, candidatePreSeamMargin,
                    slab.preSeamMargin);
            include(passageInitialized, candidateDenseW,
                    slab.denseW);
            slopeInitialized = true;
            qInitialized = true;
            passageInitialized = true;
            sourceSlopeGate = sourceSlopeGate &&
                slab.dn.rightBound() < 0. &&
                slab.sourceSlope.rightBound() <
                    sourceSlopeLimit.leftBound();
            qGate = qGate &&
                slab.terminalQ.leftBound() >
                    -rational(19, 2).rightBound() &&
                slab.terminalQ.rightBound() <
                    -rational(9).leftBound();
            passageGate = passageGate &&
                slab.phaseDomainMargin.leftBound() > 0. &&
                slab.sourceU.leftBound() > 0. &&
                slab.seamP.rightBound() < 0. &&
                slab.preSeamMargin.leftBound() > 0. &&
                slab.denseW.leftBound() > 0.;
          }
        }
      }
      bool mergedExteriorGate = !mergedExteriorMode;
      bool mergedCandidateHullsNCompatible = !mergedExteriorMode;
      if (mergedExteriorMode) {
        // The face signs and n_theta<0 give one root for every fixed
        // (parameter, eta).  Its phase lies in a slab whose interval image
        // contains zero, so the hulls of all selected slabs cover the entire
        // root branch.  Enlarging those hulls to fixed adjacent phase groups
        // preserves containment and permits coalescing whenever more than one
        // selected slab belongs to the same group.
        mergedExteriorGate = true;
        mergedCandidateHullsNCompatible = true;
        std::array<bool, graphErrorHalfCount>
            evaluatedMergedHalf{};
        for (int graphHalf = 0; graphHalf < graphErrorHalfCount;
             ++graphHalf) {
          for (int mergedGroup = 0;
               mergedGroup < mergedExteriorGroupCount;
               ++mergedGroup) {
            if (!mergedCandidatePhaseHullInitializedByGroup[graphHalf]
                                                                 [mergedGroup])
              continue;
            evaluatedMergedHalf[graphHalf] = true;
            const interval rootPhase =
                mergedCandidatePhaseHullByGroup[graphHalf][mergedGroup];
            const interval rootCentre(midpointValue(rootPhase));
            const interval rootHalfWidth(
                absUpper(rootPhase - rootCentre));
            const CellResult rootCell = evaluateCellRegion(
                cell, PhaseRegion::FullStrip, graphHalf,
                graphErrorHalfCount, &rootCentre,
                &rootHalfWidth, true);
            ++exteriorEvaluationCount;
            mergedCandidateNIncludesZeroByGroup[graphHalf][mergedGroup] =
                rootCell.n.contains(0.);
            mergedCandidateHullsNCompatible =
                mergedCandidateHullsNCompatible &&
                mergedCandidateNIncludesZeroByGroup[graphHalf]
                                                        [mergedGroup];
            derivativeGate = derivativeGate &&
                rootCell.rootDerivativeComputed &&
                rootCell.fixedEtaNTheta.rightBound() < 0.;
            exteriorGate = exteriorGate &&
                rootCell.exteriorSeamP.rightBound() < 0.;
            if (rootCell.rootDerivativeComputed) {
              include(rootInitialized, rootDerivativeR,
                      rootCell.bOnNZeroParameterDerivative[0]);
              include(rootInitialized, rootDerivativeA,
                      rootCell.bOnNZeroParameterDerivative[1]);
              include(rootInitialized, rootDerivativeEpsilon,
                      rootCell.bOnNZeroParameterDerivative[2]);
              include(rootInitialized, fixedEtaNTheta,
                      rootCell.fixedEtaNTheta);
              include(rootInitialized, exteriorSeamP,
                      rootCell.exteriorSeamP);
              rootInitialized = true;
            }
          }
          mergedExteriorGate = mergedExteriorGate &&
              evaluatedMergedHalf[graphHalf] &&
              zeroCandidateCount[graphHalf] > 0;
        }
      }
      for (int graphSlice = 0; graphSlice < anchorGraphSliceCount;
           ++graphSlice) {
        interval rootPhase(0.);
        const bool canDivide = phaseDerivativeInitialized &&
            continuationNTheta.rightBound() < 0.;
        if (canDivide)
          rootPhase = -anchorNAtZero[graphSlice] /
              continuationNTheta;
        anchorNewtonBySlice[graphSlice] = canDivide &&
            rootPhase.leftBound() > (-continuationFace).rightBound() &&
            rootPhase.rightBound() < continuationFace.leftBound();
        if (!anchorNewtonBySlice[graphSlice]) {
          anchorRootNBySlice[graphSlice] = false;
          continue;
        }
        const interval rootCentre(midpointValue(rootPhase));
        const double rootRadius = absUpper(rootPhase - rootCentre);
        const interval rootHalfWidth(rootRadius);
        const CellResult anchorRoot = evaluateCellRegion(
            centreCell, PhaseRegion::FullStrip, graphSlice,
            anchorGraphSliceCount, &rootCentre, &rootHalfWidth);
        anchorRootNBySlice[graphSlice] = anchorRoot.n.contains(0.);
        include(anchorInitialized, anchorAligned,
                anchorRoot.centreAligned);
        include(anchorInitialized, anchorRootPhase, rootPhase);
        include(anchorRootNInitialized, anchorRootN, anchorRoot.n);
        anchorInitialized = true;
        anchorRootNInitialized = true;
      }
      const interval parameterVariation =
          absoluteEnvelope(rootDerivativeR) *
              absoluteEnvelope(offsets[0]) +
          absoluteEnvelope(rootDerivativeA) *
              absoluteEnvelope(offsets[1]) +
          absoluteEnvelope(rootDerivativeEpsilon) *
              absoluteEnvelope(offsets[2]);
      const interval sourceExcursion =
          absoluteEnvelope(sourceSlope) * graphNormal;
      const interval incidenceBudget =
          absoluteEnvelope(anchorAligned) + parameterVariation +
          sourceExcursion;
      const interval baseMargin = graphBase - incidenceBudget;
      const bool budgetGate = baseMargin.leftBound() > 0.;
      const bool contractionGate =
          (lowerGraphSlope() * absoluteEnvelope(sourceSlope)).rightBound() <
          1.;
      bool anchorNewton = completeAnchorGraphSliceUnion &&
          phaseMonotonicityGate && phaseDerivativeInitialized;
      bool anchorRootContainsZero = anchorRootNInitialized;
      for (int graphSlice = 0; graphSlice < anchorGraphSliceCount;
           ++graphSlice) {
        anchorNewton = anchorNewton &&
            anchorNewtonBySlice[graphSlice];
        anchorRootContainsZero = anchorRootContainsZero &&
            anchorRootNBySlice[graphSlice];
      }
      const bool continuationFaces =
          continuationFacesByHalf[0] &&
          continuationFacesByHalf[1];
      const bool mergedKernelGate = !mergedExteriorMode ||
          (mergedExteriorGate && mergedCandidateHullsNCompatible);
      const bool nonemptyCandidates =
          zeroCandidateCount[0] > 0 && zeroCandidateCount[1] > 0 &&
          graphTubeCandidateCount[0] > 0 &&
          graphTubeCandidateCount[1] > 0 && rootInitialized &&
          slopeInitialized && qInitialized && passageInitialized;
      const bool mathematicalPass =
          anchorNewton && anchorRootContainsZero && continuationFaces &&
          derivativeGate &&
          completePhaseSlabUnion && completeGraphErrorHalfUnion &&
          completeAnchorGraphSliceUnion &&
          coordinateJacobian.leftBound() > 0. && sourceSlopeGate &&
          qGate && passageGate && exteriorGate && budgetGate &&
          contractionGate && nonemptyCandidates && mergedKernelGate;
      const auto rounding = rfsn::rigorous::runRoundingSelfTests();
      const Verdict mathematicalStatus =
          mathematicalPass ? Verdict::Pass : Verdict::Inconclusive;
      const Verdict status = combine(rounding.status, mathematicalStatus);
      std::cout << "{\"schema_version\":"
                << (mergedExteriorMode
                        ? "\"rfsn-vdp-v5-source-incidence-merged-cell/1\","
                        : "\"rfsn-vdp-v5-source-incidence-cell/2\",")
                << "\"status\":\"" << verdictName(status) << "\","
                << "\"mathematical_status\":\""
                << verdictName(mathematicalStatus) << "\","
                << "\"claim_bearing\":false,"
                << "\"box_id\":\"vdp-positive-box-v2\","
                << "\"cell_index\":[" << rIndex << ',' << aIndex
                << ',' << epsilonIndex << "],"
                << "\"grid\":[" << rCount << ',' << aCount << ','
                << epsilonCount << "],"
                << "\"phase_cover\":{\"continuation_face\":"
                << "\"1/25000\",\"slab_count\":" << slabCount
                << ",\"graph_error_halves\":" << graphErrorHalfCount
                << ",\"anchor_graph_error_slices\":"
                << anchorGraphSliceCount << ','
                << "\"anchor_interval_newton_evaluations\":"
                << 2 * anchorGraphSliceCount << ','
                << "\"zero_candidate_evaluations\":"
                << zeroCandidateCount[0] + zeroCandidateCount[1] << ','
                << "\"zero_candidate_evaluations_by_half\":["
                << zeroCandidateCount[0] << ','
                << zeroCandidateCount[1] << "],"
                << "\"graph_tube_candidate_evaluations\":"
                << graphTubeCandidateCount[0] +
                       graphTubeCandidateCount[1]
                << ','
                << "\"graph_tube_candidate_evaluations_by_half\":["
                << graphTubeCandidateCount[0] << ','
                << graphTubeCandidateCount[1] << "],"
                << "\"exterior_evaluations\":"
                << exteriorEvaluationCount << ','
                << "\"terminal_affine_subboxes_per_evaluation\":2048,"
                << "\"terminal_affine_subbox_evaluations\":"
                << 2048 * exteriorEvaluationCount << "},";
      if (mergedExteriorMode) {
        std::cout
            << "\"merged_root_exterior\":{"
            << "\"route\":"
               "\"UNIFORM_PHASE_GROUPS_PER_GRAPH_ERROR_HALF\","
            << "\"group_count_per_half\":"
            << mergedExteriorGroupCount
            << ",\"slabs_per_group\":"
            << mergedExteriorSlabsPerGroup
            << ",\"selected_slab_mask_by_half\":[";
        for (int graphHalf = 0; graphHalf < graphErrorHalfCount;
             ++graphHalf) {
          if (graphHalf != 0)
            std::cout << ',';
          std::cout << '[';
          for (int slabIndex = 0; slabIndex < slabCount; ++slabIndex) {
            if (slabIndex != 0)
              std::cout << ',';
            std::cout << boolJson(
                zeroCandidateBySlabAndHalf[graphHalf][slabIndex]);
          }
          std::cout << ']';
        }
        std::cout
            << ']'
            << ",\"candidate_phase_hull_by_half_and_group\":[";
        for (int graphHalf = 0; graphHalf < graphErrorHalfCount;
             ++graphHalf) {
          if (graphHalf != 0)
            std::cout << ',';
          std::cout << '[';
          for (int mergedGroup = 0;
               mergedGroup < mergedExteriorGroupCount;
               ++mergedGroup) {
            if (mergedGroup != 0)
              std::cout << ',';
            if (mergedCandidatePhaseHullInitializedByGroup[graphHalf]
                                                                [mergedGroup])
              std::cout << intervalJson(
                  mergedCandidatePhaseHullByGroup[graphHalf][mergedGroup]);
            else
              std::cout << "null";
          }
          std::cout << ']';
        }
        std::cout << "],\"candidate_hull_initialized_by_half_and_group\":[";
        for (int graphHalf = 0; graphHalf < graphErrorHalfCount;
             ++graphHalf) {
          if (graphHalf != 0)
            std::cout << ',';
          std::cout << '[';
          for (int mergedGroup = 0;
               mergedGroup < mergedExteriorGroupCount;
               ++mergedGroup) {
            if (mergedGroup != 0)
              std::cout << ',';
            std::cout << boolJson(
                mergedCandidatePhaseHullInitializedByGroup[graphHalf]
                                                                [mergedGroup]);
          }
          std::cout << ']';
        }
        std::cout
            << "],\"candidate_hull_normal_image_contains_zero_by_half_and_group\":[";
        for (int graphHalf = 0; graphHalf < graphErrorHalfCount;
             ++graphHalf) {
          if (graphHalf != 0)
            std::cout << ',';
          std::cout << '[';
          for (int mergedGroup = 0;
               mergedGroup < mergedExteriorGroupCount;
               ++mergedGroup) {
            if (mergedGroup != 0)
              std::cout << ',';
            if (mergedCandidatePhaseHullInitializedByGroup[graphHalf]
                                                                [mergedGroup])
              std::cout << boolJson(
                  mergedCandidateNIncludesZeroByGroup[graphHalf]
                                                         [mergedGroup]);
            else
              std::cout << "null";
          }
          std::cout << ']';
        }
        std::cout << "],\"candidate_hull_consistency_gate\":"
                  << boolJson(mergedCandidateHullsNCompatible)
                  << ",\"kernel_gate\":"
                  << boolJson(mergedKernelGate) << "},";
      }
      std::cout << "\"derivative_convention\":{"
                << "\"parameter_fibre\":\"fixed_eta_auxiliary_fibre\","
                << "\"coordinate_shift_wedge_invariance\":true,"
                << "\"actual_eta_phi_used_only_in_source_slope\":true},"
                << "\"target_graph_contract\":{"
                << "\"base_half_width\":\"27/200000\","
                << "\"normal_half_width\":\"1/10000\","
                << "\"slope_bound\":\"7/10\","
                << "\"source_slope_limit\":\"1/2\"},"
                << "\"enclosures\":{\"anchor_aligned\":"
                << intervalJson(anchorAligned)
                << ",\"anchor_root_phase\":"
                << intervalJson(anchorRootPhase)
                << ",\"anchor_root_normal\":"
                << intervalJson(anchorRootN)
                << ",\"continuation_n_theta\":"
                << intervalJson(continuationNTheta)
                << ",\"fixed_eta_b_on_n_zero_parameter_derivative\":["
                << intervalJson(rootDerivativeR) << ','
                << intervalJson(rootDerivativeA) << ','
                << intervalJson(rootDerivativeEpsilon) << "],"
                << "\"fixed_eta_n_theta\":"
                << intervalJson(fixedEtaNTheta)
                << ",\"exterior_seam_P\":"
                << intervalJson(exteriorSeamP)
                << ",\"source_abs_db_over_minus_dn\":"
                << intervalJson(sourceSlope)
                << ",\"candidate_terminal_Q\":"
                << intervalJson(candidateQ)
                << ",\"candidate_source_u1_phase_domain_margin\":"
                << intervalJson(candidatePhaseDomainMargin)
                << ",\"candidate_source_U\":"
                << intervalJson(candidateSourceU)
                << ",\"candidate_seam_P\":"
                << intervalJson(candidateSeamP)
                << ",\"candidate_pre_seam_U_margin\":"
                << intervalJson(candidatePreSeamMargin)
                << ",\"candidate_dense_W\":"
                << intervalJson(candidateDenseW)
                << ",\"parameter_variation_budget\":"
                << intervalJson(parameterVariation)
                << ",\"source_excursion_budget\":"
                << intervalJson(sourceExcursion)
                << ",\"incidence_base_margin\":"
                << intervalJson(baseMargin) << "},"
                << "\"gates\":{\"anchor_interval_newton\":"
                << boolJson(anchorNewton)
                << ",\"anchor_root_boxes_contain_zero\":"
                << boolJson(anchorRootContainsZero)
                << ",\"exact_source_zero_energy_identity\":true"
                << ",\"theta_coordinate_regular\":"
                << boolJson(coordinateJacobian.leftBound() > 0.)
                << ",\"complete_graph_error_half_union\":"
                << boolJson(completeGraphErrorHalfUnion)
                << ",\"complete_anchor_graph_error_slice_union\":"
                << boolJson(completeAnchorGraphSliceUnion)
                << ",\"complete_phase_slab_union\":"
                << boolJson(completePhaseSlabUnion)
                << ",\"continuation_faces\":"
                << boolJson(continuationFaces)
                << ",\"phase_monotonicity_on_continuation_cover\":"
                << boolJson(phaseMonotonicityGate &&
                            phaseDerivativeInitialized)
                << ",\"anchor_interval_newton_by_slice\":[";
      for (int graphSlice = 0; graphSlice < anchorGraphSliceCount;
           ++graphSlice) {
        if (graphSlice != 0)
          std::cout << ',';
        std::cout << boolJson(anchorNewtonBySlice[graphSlice]);
      }
      std::cout << ']'
                << ",\"anchor_root_contains_zero_by_slice\":[";
      for (int graphSlice = 0; graphSlice < anchorGraphSliceCount;
           ++graphSlice) {
        if (graphSlice != 0)
          std::cout << ',';
        std::cout << boolJson(anchorRootNBySlice[graphSlice]);
      }
      std::cout << ']'
                << ",\"continuation_faces_by_half\":["
                << boolJson(continuationFacesByHalf[0]) << ','
                << boolJson(continuationFacesByHalf[1]) << ']'
                << ",\"root_derivatives\":"
                << boolJson(derivativeGate && rootInitialized)
                << ",\"fixed_eta_n_theta_negative\":"
                << boolJson(rootInitialized &&
                            fixedEtaNTheta.rightBound() < 0.)
                << ",\"exterior_seam_P_negative\":"
                << boolJson(rootInitialized && exteriorGate)
                << ",\"source_slope_below_one_half\":"
                << boolJson(sourceSlopeGate && slopeInitialized)
                << ",\"graph_slope_contraction\":"
                << boolJson(contractionGate)
                << ",\"negative_K1_sheet_patch\":"
                << boolJson(qGate && qInitialized)
                << ",\"regular_source_to_terminal_passage\":"
                << boolJson(passageGate && passageInitialized)
                << ",\"base_budget\":" << boolJson(budgetGate)
                << ",\"nonempty_candidates\":"
                << boolJson(nonemptyCandidates) << "},"
                << "\"rounding_self_test\":{\"status\":\""
                << verdictName(rounding.status) << "\"},"
                << "\"claim_boundary\":{"
                << "\"established_if_pass\":\"one parameter cell has "
                   "a unique strictly secant-separated true-source "
                   "incidence with every admissible V5 lower graph in the "
                   "prescribed source-phase component, transverse whenever "
                   "the target graph is C1\","
                << "\"open_scope\":[\"complete v2 parameter cover\","
                   "\"claim-bearing composite theorem\"]}}\n";
      return status == Verdict::Pass ? 0 : 1;
    }
    if (mode == "slab") {
      if (argc != 9)
        throw std::invalid_argument("slab mode requires IR IA IE IS");
      const int rIndex = std::stoi(argv[5]);
      const int aIndex = std::stoi(argv[6]);
      const int epsilonIndex = std::stoi(argv[7]);
      const int slabIndex = std::stoi(argv[8]);
      constexpr int slabCount = 16;
      if (slabIndex < 0 || slabIndex >= slabCount)
        throw std::invalid_argument("invalid phase slab index");
      const interval continuationFace = rational(1, 25000);
      const interval slabCentre = -continuationFace +
          continuationFace * rational(2L * slabIndex + 1, slabCount);
      const interval slabHalfWidth =
          continuationFace / interval(slabCount);
      const Box cell = parameterCell(rIndex, rCount, aIndex, aCount,
                                     epsilonIndex, epsilonCount);
      for (int graphHalf = 0; graphHalf < 2; ++graphHalf)
        includeResult(
            aggregate,
            evaluateCellRegion(
                cell, PhaseRegion::FullStrip, graphHalf, 2,
                &slabCentre, &slabHalfWidth, true),
            PhaseRegion::FullStrip, rIndex, aIndex,
            epsilonIndex, graphHalf);
      printResult(aggregate, rCount, aCount, epsilonCount, false);
      return aggregate.status == Verdict::Pass ? 0 : 1;
    }
    if (mode == "cell") {
      if (argc != 8)
        throw std::invalid_argument("cell mode requires IR IA IE");
      const int rIndex = std::stoi(argv[5]);
      const int aIndex = std::stoi(argv[6]);
      const int epsilonIndex = std::stoi(argv[7]);
      const Box cell = parameterCell(rIndex, rCount, aIndex, aCount,
                                     epsilonIndex, epsilonCount);
      for (int phaseRegion = 0; phaseRegion < 3; ++phaseRegion)
        for (int graphHalf = 0; graphHalf < 2; ++graphHalf)
          includeResult(
              aggregate,
              evaluateCellRegion(
                  cell, static_cast<PhaseRegion>(phaseRegion),
                  graphHalf, 2),
              static_cast<PhaseRegion>(phaseRegion), rIndex, aIndex,
              epsilonIndex, graphHalf);
      printResult(aggregate, rCount, aCount, epsilonCount, false);
      return aggregate.status == Verdict::Pass ? 0 : 1;
    }
    if (mode != "cover" || argc != 5)
      throw std::invalid_argument(
          "usage: probe cover NR NA NE | probe cell NR NA NE IR IA IE | "
          "probe slab NR NA NE IR IA IE IS | "
          "probe incidence-cell NR NA NE IR IA IE | "
          "probe incidence-merged-cell NR NA NE IR IA IE");
    for (int rIndex = 0; rIndex < rCount; ++rIndex) {
      for (int aIndex = 0; aIndex < aCount; ++aIndex) {
        for (int epsilonIndex = 0; epsilonIndex < epsilonCount;
             ++epsilonIndex) {
          const Box cell = parameterCell(rIndex, rCount, aIndex, aCount,
                                         epsilonIndex, epsilonCount);
          for (int phaseRegion = 0; phaseRegion < 3; ++phaseRegion) {
            for (int graphHalf = 0; graphHalf < 2; ++graphHalf) {
              includeResult(
                  aggregate,
                  evaluateCellRegion(
                      cell, static_cast<PhaseRegion>(phaseRegion),
                      graphHalf, 2),
                  static_cast<PhaseRegion>(phaseRegion), rIndex, aIndex,
                  epsilonIndex, graphHalf);
            }
          }
        }
      }
      std::cerr << "completed r slab " << rIndex + 1 << '/' << rCount
                << '\n';
    }
    printResult(aggregate, rCount, aCount, epsilonCount, true);
    return aggregate.status == Verdict::Pass ? 0 : 1;
  } catch (const std::exception& error) {
    std::cerr << "v5 source incidence probe: " << error.what() << '\n';
    return 2;
  }
}
