#include <algorithm>
#include <array>
#include <cmath>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <limits>
#include <memory>
#include <stdexcept>
#include <string>
#include <vector>

#include "capd/capdlib.h"
#include "unstable_graph_terms.hpp"

// Outward-rounded design kernel for the two non-return P2e axis channels.
//
// The source is the exact zero-energy chart from P2E_AXIS_SOURCE_CHART.md,
// with the complete proved C0 graph-error interval |eta|<=1/200000.  Each
// invocation treats one prospectively frozen bridge cell and one complete
// axis entrance interval.  This design program is not itself an atlas
// certificate: it proves neither the global first-event census nor the
// incidence complex, transported traces, or numerical m_ax.

using namespace capd;

namespace {

constexpr int kRCells = 8;
constexpr int kA2Cells = 128;
constexpr int kEpsilonCells = 4;

interval rationalCell(int leftNumerator, int rightNumerator,
                      int denominator) {
  const interval left = interval(leftNumerator) / interval(denominator);
  const interval right = interval(rightNumerator) / interval(denominator);
  return interval(left.leftBound(), right.rightBound());
}

int parseIndex(const char* text, int upperExclusive, const char* name) {
  std::size_t used = 0;
  const std::string value(text);
  const int index = std::stoi(value, &used);
  if (used != value.size() || index < 0 || index >= upperExclusive) {
    throw std::invalid_argument(std::string(name) + " must lie in [0," +
                                std::to_string(upperExclusive) + ")");
  }
  return index;
}

interval integerPower(interval value, int exponent) {
  interval result(1.);
  for (int index = 0; index < exponent; ++index) result *= value;
  return result;
}

int fallingFactorial(int exponent, int derivatives) {
  int result = 1;
  for (int index = 0; index < derivatives; ++index)
    result *= exponent - index;
  return result;
}

interval coefficient(const PolynomialTerm& term) {
  interval result = interval(term.numerator, term.numerator) /
                    interval(term.denominator, term.denominator);
  if (term.times_sqrt_two) result *= sqrt(interval(2.));
  return result;
}

template <std::size_t Size>
interval polynomial(const PolynomialTerm (&terms)[Size], const interval& x,
                    const interval& y, int dx = 0, int dy = 0) {
  interval result(0.);
  for (const auto& term : terms) {
    if (term.px < dx || term.py < dy) continue;
    result += coefficient(term) *
              interval(static_cast<double>(fallingFactorial(term.px, dx))) *
              interval(static_cast<double>(fallingFactorial(term.py, dy))) *
              integerPower(x, term.px - dx) *
              integerPower(y, term.py - dy);
  }
  return result;
}

struct Parameters {
  interval r;
  interval a2;
  interval epsilon;
  interval a;
  interval b;
  interval c;
  interval alpha;
  interval beta;
  interval h;
  interval chi;
};

Parameters parameters(int rIndex, int a2Index, int epsilonIndex) {
  const interval r = rationalCell(rIndex, rIndex + 1, 400);
  const interval a2 = rationalCell(a2Index - 64, a2Index - 63, 256);
  const interval epsilon =
      rationalCell(epsilonIndex + 8, epsilonIndex + 9, 10);
  const interval rootEpsilon = sqrt(epsilon);
  const interval r2 = sqr(r);
  const interval r4 = sqr(r2);
  const interval a = interval(1.) + rootEpsilon * r2 * r * a2;
  const interval b = rootEpsilon * r2 / interval(3.);
  const interval c = interval(2.) * r * a2 + rootEpsilon * r4 * sqr(a2);
  const interval alpha = interval(.5) * sqrt(interval(2.) + c);
  const interval beta = interval(.5) * sqrt(interval(2.) - c);
  // Preserve the shared c dependence.  Multiplying separate alpha/beta
  // intervals introduces an artificial first-order width, whereas h varies
  // only through c^2.
  const interval h = interval(.5) * sqrt(interval(4.) - sqr(c));
  const interval chi = atan(
      (interval(1.) / sqrt(interval(2.)) - alpha) / beta);
  return {r, a2, epsilon, a, b, c, alpha, beta, h, chi};
}

interval twoPi() {
  const interval lower = interval(103993) / interval(16551);
  const interval upper = interval(208696) / interval(33215);
  return interval(lower.leftBound(), upper.rightBound());
}

struct Channel {
  std::string id;
  interval phase;
  interval terminalU;
};

Channel channel(const std::string& id) {
  // The direct apertures cover the retained disk on the zero-action axis:
  // |x_1|<=sqrt(5/4) in the pole chart, and the corresponding frozen ALG
  // window.  They are not assertions about a larger rectangular carrier.
  if (id == "ALG") {
    const interval anchor("5.7566913947049203", "5.7566913967948983");
    const interval radius = interval(9.) / interval(80000000.);
    return {id, anchor + interval(-radius.rightBound(), radius.rightBound()),
            -interval(400.) / interval(23.)};
  }
  if (id == "ALG_SEAM") {
    const interval anchor("5.7566913947049203", "5.7566913967948983");
    const interval radius = interval(9.) / interval(80000000.);
    return {id, anchor + interval(-radius.rightBound(), radius.rightBound()),
            interval(-4.)};
  }
  if (id == "POLE") {
    const interval radius = interval(9.) / interval(800000.);
    return {id, twoPi() + interval(-radius.rightBound(), radius.rightBound()),
            interval(-10.)};
  }
  throw std::invalid_argument("channel must be ALG, ALG_SEAM, or POLE");
}

IVector source(const Parameters& p, const interval& theta,
               const interval& graphError) {
  const interval rho = interval(1.) / interval(100.);
  const interval angle = theta + p.chi;
  const interval u1 = rho * cos(angle);
  const interval u2 = rho * sin(angle);
  if (u1.leftBound() <= 0.)
    throw std::runtime_error("axis source chart lost its u1>0 denominator");

  const interval s1 = polynomial(kH1Terms, u1, u2) + graphError;
  const interval X = u1 + s1;
  const interval s2 = -(u2 / u1) * s1
      - p.a * integerPower(X, 3) / (interval(6.) * p.h * u1)
      + p.b * integerPower(X, 4) / (interval(8.) * p.h * u1);

  IVector result(7);
  result[0] = X;
  result[1] = p.alpha * u1 - p.beta * u2
      - p.alpha * s1 + p.beta * s2;
  result[2] = p.c * X / interval(2.) + p.h * (u2 + s2);
  result[3] = p.alpha * u1 + p.beta * u2
      - p.alpha * s1 - p.beta * s2;
  result[4] = p.r;
  result[5] = p.a2;
  result[6] = p.epsilon;
  return result;
}

double midpointValue(const interval& value) {
  return value.mid().leftBound();
}

interval midpointInterval(const interval& value) {
  return interval(midpointValue(value));
}

interval halfInterval(const interval& value, int half) {
  if (half != 0 && half != 1)
    throw std::invalid_argument("split_half must be 0 or 1");
  const interval middle = midpointInterval(value);
  return half == 0 ? interval(value.leftBound(), middle.rightBound())
                   : interval(middle.leftBound(), value.rightBound());
}

IVector midpointVector(const IVector& value) {
  IVector result(value.dimension());
  for (int index = 0; index < value.dimension(); ++index)
    result[index] = midpointInterval(value[index]);
  return result;
}

double absoluteUpper(const interval& value) {
  return std::max(std::abs(value.leftBound()),
                  std::abs(value.rightBound()));
}

struct FirstJet {
  static constexpr int kDimension = 5;
  interval value;
  std::array<interval, kDimension> derivative;

  explicit FirstJet(const interval& input = interval(0.))
      : value(input), derivative{interval(0.), interval(0.), interval(0.),
                                 interval(0.), interval(0.)} {}

  static FirstJet variable(const interval& input, int column) {
    FirstJet result(input);
    result.derivative[column] = interval(1.);
    return result;
  }
};

FirstJet operator+(const FirstJet& left, const FirstJet& right) {
  FirstJet result(left.value + right.value);
  for (int index = 0; index < FirstJet::kDimension; ++index)
    result.derivative[index] =
        left.derivative[index] + right.derivative[index];
  return result;
}

FirstJet operator-(const FirstJet& left, const FirstJet& right) {
  FirstJet result(left.value - right.value);
  for (int index = 0; index < FirstJet::kDimension; ++index)
    result.derivative[index] =
        left.derivative[index] - right.derivative[index];
  return result;
}

FirstJet operator-(const FirstJet& input) {
  FirstJet result(-input.value);
  for (int index = 0; index < FirstJet::kDimension; ++index)
    result.derivative[index] = -input.derivative[index];
  return result;
}

FirstJet operator*(const FirstJet& left, const FirstJet& right) {
  FirstJet result(left.value * right.value);
  for (int index = 0; index < FirstJet::kDimension; ++index) {
    result.derivative[index] = left.derivative[index] * right.value +
                               left.value * right.derivative[index];
  }
  return result;
}

FirstJet reciprocal(const FirstJet& input) {
  FirstJet result(interval(1.) / input.value);
  for (int index = 0; index < FirstJet::kDimension; ++index)
    result.derivative[index] = -input.derivative[index] / sqr(input.value);
  return result;
}

FirstJet operator/(const FirstJet& left, const FirstJet& right) {
  return left * reciprocal(right);
}

FirstJet jetPower(FirstJet input, int exponent) {
  FirstJet result(interval(1.));
  for (int index = 0; index < exponent; ++index) result = result * input;
  return result;
}

FirstJet jetSquare(const FirstJet& input) {
  FirstJet result(sqr(input.value));
  for (int index = 0; index < FirstJet::kDimension; ++index)
    result.derivative[index] =
        interval(2.) * input.value * input.derivative[index];
  return result;
}

FirstJet jetSqrt(const FirstJet& input) {
  FirstJet result(sqrt(input.value));
  for (int index = 0; index < FirstJet::kDimension; ++index)
    result.derivative[index] =
        input.derivative[index] / (interval(2.) * result.value);
  return result;
}

FirstJet jetSin(const FirstJet& input) {
  FirstJet result(sin(input.value));
  for (int index = 0; index < FirstJet::kDimension; ++index)
    result.derivative[index] = cos(input.value) * input.derivative[index];
  return result;
}

FirstJet jetCos(const FirstJet& input) {
  FirstJet result(cos(input.value));
  for (int index = 0; index < FirstJet::kDimension; ++index)
    result.derivative[index] = -sin(input.value) * input.derivative[index];
  return result;
}

FirstJet jetAtan(const FirstJet& input) {
  FirstJet result(atan(input.value));
  for (int index = 0; index < FirstJet::kDimension; ++index) {
    result.derivative[index] =
        input.derivative[index] / (interval(1.) + sqr(input.value));
  }
  return result;
}

template <std::size_t Size>
FirstJet jetPolynomial(const PolynomialTerm (&terms)[Size],
                       const FirstJet& x, const FirstJet& y) {
  FirstJet result(interval(0.));
  for (const auto& term : terms) {
    result = result + FirstJet(coefficient(term)) * jetPower(x, term.px) *
                          jetPower(y, term.py);
  }
  return result;
}

using MuBox = std::array<interval, 3>;
using MuSlopes = std::array<IVector, 3>;

std::array<FirstJet, 4> sourceFirstJet(
    const MuBox& centre, const MuBox& offsets, const interval& phaseCentre,
    const interval& phaseOffset, const interval& graphCentre,
    const interval& graphOffset) {
  const FirstJet dr = FirstJet::variable(offsets[0], 0);
  const FirstJet da2 = FirstJet::variable(offsets[1], 1);
  const FirstJet depsilon = FirstJet::variable(offsets[2], 2);
  const FirstJet dphase = FirstJet::variable(phaseOffset, 3);
  const FirstJet eta = FirstJet(graphCentre) +
                       FirstJet::variable(graphOffset, 4);
  const FirstJet one(interval(1.));
  const FirstJet two(interval(2.));
  const FirstJet r = FirstJet(centre[0]) + dr;
  const FirstJet a2 = FirstJet(centre[1]) + da2;
  const FirstJet epsilon = FirstJet(centre[2]) + depsilon;
  const FirstJet rootEpsilon = jetSqrt(epsilon);
  const FirstJet r2 = jetSquare(r);
  const FirstJet r3 = r2 * r;
  const FirstJet r4 = jetSquare(r2);
  const FirstJet a = one + rootEpsilon * r3 * a2;
  const FirstJet b = rootEpsilon * r2 / FirstJet(interval(3.));
  const FirstJet c = two * r * a2 + rootEpsilon * r4 * jetSquare(a2);
  const FirstJet alpha = FirstJet(interval(.5)) * jetSqrt(two + c);
  const FirstJet beta = FirstJet(interval(.5)) * jetSqrt(two - c);
  const FirstJet h = FirstJet(interval(.5)) *
                     jetSqrt(FirstJet(interval(4.)) - jetSquare(c));
  const FirstJet inverseSqrtTwo = one / jetSqrt(two);
  const FirstJet chi = jetAtan((inverseSqrtTwo - alpha) / beta);
  const FirstJet angle = FirstJet(phaseCentre) + dphase + chi;
  const FirstJet rho(interval(1.) / interval(100.));
  const FirstJet u1 = rho * jetCos(angle);
  const FirstJet u2 = rho * jetSin(angle);
  if (u1.value.contains(0.))
    throw std::runtime_error("affine source lost its u1>0 denominator");
  const FirstJet s1 = jetPolynomial(kH1Terms, u1, u2) + eta;
  const FirstJet U = u1 + s1;
  const FirstJet s2 = -s1 * u2 / u1 -
      a * jetPower(U, 3) / (FirstJet(interval(6.)) * h * u1) +
      b * jetPower(U, 4) / (FirstJet(interval(8.)) * h * u1);
  std::array<FirstJet, 4> state;
  state[0] = U;
  state[1] = alpha * u1 - beta * u2 - alpha * s1 + beta * s2;
  state[2] = c * U / FirstJet(interval(2.)) + h * (u2 + s2);
  state[3] = alpha * u1 + beta * u2 - alpha * s1 - beta * s2;
  return state;
}

struct AffineInitialData {
  IVector centre;
  IMatrix coordinates;
  IVector radii;
  IVector remainder;
};

AffineInitialData affineSourceData(const MuBox& parameterCentre,
                                   const MuBox& offsets,
                                   const interval& phaseCentre,
                                   const interval& phaseOffset,
                                   const interval& graphError) {
  const interval graphCentre = midpointInterval(graphError);
  const interval graphOffset = graphError - graphCentre;
  const std::array<FirstJet, 4> jet = sourceFirstJet(
      parameterCentre, offsets, phaseCentre, phaseOffset, graphCentre,
      graphOffset);
  const Parameters pointParameters = [&]() {
    const interval r = parameterCentre[0];
    const interval a2 = parameterCentre[1];
    const interval epsilon = parameterCentre[2];
    const interval rootEpsilon = sqrt(epsilon);
    const interval r2 = sqr(r);
    const interval r4 = sqr(r2);
    const interval a = interval(1.) + rootEpsilon * r2 * r * a2;
    const interval b = rootEpsilon * r2 / interval(3.);
    const interval c = interval(2.) * r * a2 +
                       rootEpsilon * r4 * sqr(a2);
    const interval alpha = interval(.5) * sqrt(interval(2.) + c);
    const interval beta = interval(.5) * sqrt(interval(2.) - c);
    const interval h = interval(.5) * sqrt(interval(4.) - sqr(c));
    const interval chi = atan(
        (interval(1.) / sqrt(interval(2.)) - alpha) / beta);
    return Parameters{r, a2, epsilon, a, b, c, alpha, beta, h, chi};
  }();
  const IVector exactCentre = midpointVector(
      source(pointParameters, phaseCentre, graphCentre));

  MuSlopes parameterSlopes{IVector(4), IVector(4), IVector(4)};
  IVector phaseSlope(4), errorSlope(4);
  for (int coordinate = 0; coordinate < 4; ++coordinate) {
    for (int parameter = 0; parameter < 3; ++parameter) {
      parameterSlopes[parameter][coordinate] =
          midpointInterval(jet[coordinate].derivative[parameter]);
    }
    phaseSlope[coordinate] =
        midpointInterval(jet[coordinate].derivative[3]);
    errorSlope[coordinate] =
        midpointInterval(jet[coordinate].derivative[4]);
  }

  IVector centre(9), radii(9), remainder(9);
  IMatrix coordinates(9, 9);
  for (int row = 0; row < 9; ++row) {
    centre[row] = interval(0.);
    radii[row] = interval(0.);
    remainder[row] = interval(0.);
    for (int column = 0; column < 9; ++column)
      coordinates[row][column] = interval(0.);
  }
  for (int coordinate = 0; coordinate < 4; ++coordinate)
    centre[coordinate] = exactCentre[coordinate];
  for (int parameter = 0; parameter < 3; ++parameter) {
    radii[parameter] = offsets[parameter];
    coordinates[4 + parameter][parameter] = interval(1.);
    for (int coordinate = 0; coordinate < 4; ++coordinate) {
      coordinates[coordinate][parameter] =
          parameterSlopes[parameter][coordinate];
    }
  }
  radii[3] = phaseOffset;
  radii[4] = graphOffset;
  coordinates[7][3] = interval(1.);
  coordinates[8][4] = interval(1.);
  for (int coordinate = 0; coordinate < 4; ++coordinate) {
    coordinates[coordinate][3] = phaseSlope[coordinate];
    coordinates[coordinate][4] = errorSlope[coordinate];
    coordinates[coordinate][5 + coordinate] = interval(1.);
  }

  // Mean-value remainder after removing the chosen midpoint affine frame.
  for (int coordinate = 0; coordinate < 4; ++coordinate) {
    interval raw =
        source(pointParameters, phaseCentre, graphCentre)[coordinate] -
        exactCentre[coordinate];
    for (int parameter = 0; parameter < 3; ++parameter) {
      raw += (jet[coordinate].derivative[parameter] -
              parameterSlopes[parameter][coordinate]) * offsets[parameter];
    }
    raw += (jet[coordinate].derivative[3] - phaseSlope[coordinate]) *
           phaseOffset;
    raw += (jet[coordinate].derivative[4] - errorSlope[coordinate]) *
           graphOffset;
    const double radius = absoluteUpper(raw);
    remainder[coordinate] = interval(-radius, radius);
  }
  return {centre, coordinates, radii, remainder};
}

IVector affineHull(const AffineInitialData& data) {
  return data.centre + data.coordinates * data.radii + data.remainder;
}

std::string intervalString(const interval& value) {
  std::ostringstream output;
  output << std::setprecision(17) << value;
  return output.str();
}

}  // namespace

int main(int argc, char** argv) {
  try {
    if (argc < 5) {
      std::cerr << "usage: " << argv[0]
                << " ALG|ALG_SEAM|POLE r_index a2_index epsilon_index "
                   "[r|a2|epsilon|phase|eta split_half]... "
                   "[eta_box lower upper] "
                   "[pole_route BASE|V_STEPS|TURN_REDUCED]\n";
      return 2;
    }
    const Channel selected = channel(argv[1]);
    const int rIndex = parseIndex(argv[2], kRCells, "r_index");
    const int a2Index = parseIndex(argv[3], kA2Cells, "a2_index");
    const int epsilonIndex =
        parseIndex(argv[4], kEpsilonCells, "epsilon_index");
    Parameters p = parameters(rIndex, a2Index, epsilonIndex);
    interval selectedPhase = selected.phase;
    interval graphRadius = interval(1.) / interval(200000.);
    interval graphError(-graphRadius.rightBound(), graphRadius.rightBound());
    std::string poleRoute = "BASE";
    std::string splitPath;
    int rSplitCount = 0;
    int canonicalRLocalIndex = 0;
    bool sawEtaBox = false;
    bool sawEtaSplit = false;
    bool sawPoleRoute = false;
    for (int splitArgument = 5; splitArgument < argc;) {
      const std::string splitVariable(argv[splitArgument]);
      if (splitVariable == "eta_box") {
        if (sawEtaBox || sawEtaSplit)
          throw std::invalid_argument(
              "eta_box is unique and cannot be combined with eta splits");
        if (splitArgument + 2 >= argc)
          throw std::invalid_argument("eta_box requires lower and upper");
        const interval lower(argv[splitArgument + 1],
                             argv[splitArgument + 1]);
        const interval upper(argv[splitArgument + 2],
                             argv[splitArgument + 2]);
        graphError = interval(lower.leftBound(), upper.rightBound());
        const interval provedRadius = interval(1.) / interval(200000.);
        const interval proved(-provedRadius.rightBound(),
                              provedRadius.rightBound());
        if (!subset(graphError, proved))
          throw std::invalid_argument(
              "eta_box must lie inside the proved |eta|<=1/200000 tube");
        if (!splitPath.empty()) splitPath += ",";
        splitPath += "eta_box";
        sawEtaBox = true;
        splitArgument += 3;
        continue;
      }
      if (splitVariable == "pole_route") {
        if (selected.id != "POLE" || sawPoleRoute)
          throw std::invalid_argument(
              "pole_route is unique and available only for POLE");
        if (splitArgument + 1 >= argc)
          throw std::invalid_argument("pole_route requires BASE or V_STEPS");
        poleRoute = argv[splitArgument + 1];
        if (poleRoute != "BASE" && poleRoute != "V_STEPS" &&
            poleRoute != "TURN_REDUCED")
          throw std::invalid_argument(
              "pole_route must be BASE, V_STEPS, or TURN_REDUCED");
        if (!splitPath.empty()) splitPath += ",";
        splitPath += "pole_route:" + poleRoute;
        sawPoleRoute = true;
        splitArgument += 2;
        continue;
      }
      if (splitArgument + 1 >= argc)
        throw std::invalid_argument("split variable requires split_half");
      const int splitHalf =
          parseIndex(argv[splitArgument + 1], 2, "split_half");
      if (!splitPath.empty()) splitPath += ",";
      splitPath += splitVariable + ":" + std::to_string(splitHalf);
      if (splitVariable == "r") {
        ++rSplitCount;
        canonicalRLocalIndex = 2 * canonicalRLocalIndex + splitHalf;
        if (rSplitCount == 3) {
          // The source certificate uses the exact canonical leaf
          // [i/3200,(i+1)/3200].  Reconstruct that leaf directly instead of
          // retaining the extra ulps produced by three successive midpoint
          // splits; otherwise a root-conditioned terminal request can extend
          // infinitesimally beyond its source certificate.
          const int globalRLeaf = 8 * rIndex + canonicalRLocalIndex;
          p.r = rationalCell(globalRLeaf, globalRLeaf + 1, 3200);
        } else {
          p.r = halfInterval(p.r, splitHalf);
        }
      }
      else if (splitVariable == "a2") p.a2 = halfInterval(p.a2, splitHalf);
      else if (splitVariable == "epsilon")
        p.epsilon = halfInterval(p.epsilon, splitHalf);
      else if (splitVariable == "phase")
        selectedPhase = halfInterval(selectedPhase, splitHalf);
      else if (splitVariable == "eta") {
        if (sawEtaBox)
          throw std::invalid_argument(
              "eta splits cannot be combined with eta_box");
        sawEtaSplit = true;
        graphError = halfInterval(graphError, splitHalf);
      } else
        throw std::invalid_argument(
            "split variable must be r, a2, epsilon, phase, or eta");
      // Recompute every derived interval after each parameter split.
      if (splitVariable == "r" || splitVariable == "a2" ||
          splitVariable == "epsilon") {
        const interval rootEpsilon = sqrt(p.epsilon);
        const interval r2 = sqr(p.r);
        const interval r4 = sqr(r2);
        p.a = interval(1.) + rootEpsilon * r2 * p.r * p.a2;
        p.b = rootEpsilon * r2 / interval(3.);
        p.c = interval(2.) * p.r * p.a2 +
              rootEpsilon * r4 * sqr(p.a2);
        p.alpha = interval(.5) * sqrt(interval(2.) + p.c);
        p.beta = interval(.5) * sqrt(interval(2.) - p.c);
        p.h = interval(.5) * sqrt(interval(4.) - sqr(p.c));
        p.chi = atan((interval(1.) / sqrt(interval(2.)) - p.alpha) /
                     p.beta);
      }
      splitArgument += 2;
    }
    const MuBox parameterCentre = {
        midpointInterval(p.r), midpointInterval(p.a2),
        midpointInterval(p.epsilon)};
    const MuBox parameterOffsets = {
        p.r - parameterCentre[0], p.a2 - parameterCentre[1],
        p.epsilon - parameterCentre[2]};
    const interval phaseCentre = midpointInterval(selectedPhase);
    const interval phaseOffset = selectedPhase - phaseCentre;
    const AffineInitialData initialData = affineSourceData(
        parameterCentre, parameterOffsets, phaseCentre, phaseOffset,
        graphError);
    const IVector initial = affineHull(initialData);
    if (initial[0].leftBound() <= 0.)
      throw std::runtime_error(
          "source is not strictly on the U>0 side of the first section");
    if (initial[0].leftBound() <= selected.terminalU.rightBound())
      throw std::runtime_error("source is not strictly before terminal U");

    IMap field(
        "par:rc,a2c,epsc;var:U,P,V,Q,er,ea,ee,dphi,eta;"
        "fun:P,(2*(rc+er)*(a2c+ea)+sqrt(epsc+ee)*(rc+er)^4*"
        "(a2c+ea)^2)*U-V-(1+sqrt(epsc+ee)*(rc+er)^3*"
        "(a2c+ea))*U^2+(sqrt(epsc+ee)/3)*(rc+er)^2*U^3,"
        "Q,U,0,0,0,0,0;");
    field.setParameter("rc", parameterCentre[0]);
    field.setParameter("a2c", parameterCentre[1]);
    field.setParameter("epsc", parameterCentre[2]);
    IOdeSolver solver(field, 20);
    solver.setAbsoluteTolerance(1.e-13);
    solver.setRelativeTolerance(1.e-13);
    solver.setMaxStep(.02);
    C0HOTripletonSet set(initialData.centre, initialData.coordinates,
                         initialData.radii, initialData.remainder);
    interval returnTime;
    IVector event(9);
    std::vector<interval> legTimes;
    std::vector<std::string> legLabels;
    std::vector<int> legExpectedSigns;
    std::vector<interval> legSectionSpeeds;
    std::vector<interval> legSectionResiduals;
    std::vector<interval> algReducedTimes;
    std::vector<interval> algReducedW;
    std::vector<interval> algReducedQ;
    std::unique_ptr<C0HOTripletonSet> firstDownSet;
    bool algReducedApplicable = false;
    bool algReducedPassed = true;
    interval algSeamTime(0.), algSeamP(0.), algSeamQ(0.);
    interval algTerminalEnergy(0.);
    interval algTailClock(0.), algDenseWHull(0.);
    int algDenseSteps = 0;
    bool turnReducedApplicable = false;
    bool turnReducedPassed = true;
    interval turnSeamV(0.), turnClock(0.), turnDensePHull(0.);
    int turnDenseSteps = 0;
    bool escapeReducedApplicable = false;
    bool escapeReducedPassed = true;
    interval escapeSeamQ(0.), escapeReducedClock(0.);
    interval escapeDenseQHull(0.);
    int escapeDenseSteps = 0;
    int legCount = 0;
    const auto hitSection = [&](int coordinate, const interval& target,
                                const std::string& label,
                                int expectedSign) {
      ICoordinateSection section(9, coordinate, target);
      IPoincareMap map(solver, section, expectedSign < 0
          ? poincare::PlusMinus : poincare::MinusPlus);
      map.setMaxReturnTime(30.);
      map.setBlowUpMaxNorm(1.e8);
      interval hitTime;
      IVector hit(9);
      try {
        hit = map(set, hitTime);
      } catch (const std::exception& error) {
        throw std::runtime_error(label + ": " + error.what());
      }
      legTimes.push_back(hitTime);
      legLabels.push_back(label);
      legExpectedSigns.push_back(expectedSign);
      legSectionResiduals.push_back(hit[coordinate] - target);
      if (coordinate == 0) {
        legSectionSpeeds.push_back(hit[1]);
      } else if (coordinate == 1) {
        legSectionSpeeds.push_back(
            p.c * hit[0] - hit[2] - p.a * sqr(hit[0]) +
            p.b * integerPower(hit[0], 3));
      } else if (coordinate == 2) {
        legSectionSpeeds.push_back(hit[3]);
      } else if (coordinate == 3) {
        legSectionSpeeds.push_back(hit[0]);
      } else {
        throw std::runtime_error("unsupported intermediate section");
      }
      if (label == "U=-.05 DOWN I")
        firstDownSet = std::make_unique<C0HOTripletonSet>(set);
      ++legCount;
      return hit;
    };
    if (selected.id == "POLE") {
      // Follow the actual global turn sequence before the escaping pole
      // leg.  A naive U=-.5 intermediate section is almost tangent to the
      // first left excursion and causes severe wrapping.  The two Q=0 and
      // two P=0 turns separate that bounded excursion from the final escape.
      event = hitSection(
          0, -interval(1.) / interval(20.), "U=-.05 DOWN I", -1);
      event = hitSection(3, interval(0.), "Q=0 DOWN", -1);
      event = hitSection(1, interval(0.), "P=0 MIN", +1);
      event = hitSection(
          0, -interval(1.) / interval(20.), "U=-.05 UP", +1);
      if (poleRoute == "TURN_REDUCED") {
        // The Poincare image lies on H=0.  Rebuild a fresh product enclosure
        // on the exact U=-1/20 section from its rigorous P,Q and parameter
        // hulls, eliminating V with the Hamiltonian identity.  This is a
        // superset operation (correlations are discarded), but it removes
        // the numerically unstable energy-normal direction before the long
        // upper turn.
        const interval turnU = -interval(1.) / interval(20.);
        const interval turnV = (sqr(event[3]) - sqr(event[1]) +
            p.c * sqr(turnU) - interval(2.) * p.a *
            integerPower(turnU, 3) / interval(3.) +
            p.b * integerPower(turnU, 4) / interval(2.)) /
            (interval(2.) * turnU);
        interval turnVIntersection;
        if (!intersection(event[2], turnV, turnVIntersection))
          throw std::runtime_error(
              "upper-turn physical and zero-energy V enclosures are disjoint");
        turnReducedApplicable = true;
        turnSeamV = turnVIntersection;
        IVector turnInitial(7);
        turnInitial[0] = event[1];
        turnInitial[1] = turnVIntersection;
        turnInitial[2] = event[3];
        turnInitial[3] = event[4];
        turnInitial[4] = event[5];
        turnInitial[5] = event[6];
        turnInitial[6] = interval(0.);
        C0HOTripletonSet turnSet(turnInitial);
        turnSet.setCurrentTime(turnU);
        turnDensePHull = turnInitial[0];
        if (turnDensePHull.leftBound() <= 0.)
          throw std::runtime_error("upper-turn seam lost P>0");
        IMap turnField(
            "time:x;par:rc,a2c,epsc;"
            "var:pp,vv,qq,er,ea,ee,clock;"
            "fun:((2*(rc+er)*(a2c+ea)+sqrt(epsc+ee)*(rc+er)^4*"
            "(a2c+ea)^2)*x-vv-(1+sqrt(epsc+ee)*(rc+er)^3*"
            "(a2c+ea))*x^2+(sqrt(epsc+ee)/3)*(rc+er)^2*x^3)/pp,"
            "qq/pp,x/pp,0,0,0,1/pp;");
        turnField.setParameter("rc", parameterCentre[0]);
        turnField.setParameter("a2c", parameterCentre[1]);
        turnField.setParameter("epsc", parameterCentre[2]);
        IOdeSolver turnSolver(turnField, 20);
        turnSolver.setAbsoluteTolerance(1.e-13);
        turnSolver.setRelativeTolerance(1.e-13);
        turnSolver.setMaxStep(.02);
        ITimeMap turnMap(turnSolver);
        turnMap.stopAfterStep(true);
        const interval turnTargetU = interval(11.) / interval(5.);
        IVector turnEvent(7);
        do {
          turnEvent = turnMap(turnTargetU, turnSet);
          const interval stepP = turnSet.getLastEnclosure()[0];
          turnDensePHull = intervalHull(turnDensePHull, stepP);
          ++turnDenseSteps;
          if (stepP.leftBound() <= 0.)
            throw std::runtime_error("upper-turn U-time passage lost P>0");
        } while (!turnMap.completed());
        turnClock = turnEvent[6];
        turnReducedPassed = turnClock.leftBound() > 0. &&
            turnEvent[0].leftBound() > 0.;
        if (!turnReducedPassed)
          throw std::runtime_error("upper-turn U-time passage did not close");
        IVector turnPhysical(9);
        turnPhysical[0] = turnTargetU;
        turnPhysical[1] = turnEvent[0];
        turnPhysical[2] = turnEvent[1];
        turnPhysical[3] = turnEvent[2];
        turnPhysical[4] = turnEvent[3];
        turnPhysical[5] = turnEvent[4];
        turnPhysical[6] = turnEvent[5];
        turnPhysical[7] = event[7];
        turnPhysical[8] = event[8];
        const interval physicalTurnTime = set.getCurrentTime() + turnClock;
        set = C0HOTripletonSet(turnPhysical);
        set.setCurrentTime(physicalTurnTime);
      }
      event = hitSection(3, interval(0.), "Q=0 UP", +1);
      if (poleRoute == "TURN_REDUCED") {
        // P remains positive between Q=0 and the following maximum.
        event = hitSection(
            0, interval(5.) / interval(2.), "U=2.5 UP", +1);
        event = hitSection(
            0, interval(11.) / interval(4.), "U=2.75 UP", +1);
      }
      event = hitSection(1, interval(0.), "P=0 MAX", -1);
      event = hitSection(2, interval(0.), "V=0 UP", +1);
      if (poleRoute == "TURN_REDUCED") {
        // On the escaping arc Q>0, so use V as the independent variable from
        // V=0 to V=4/5.  Reconstruct the positive Q branch from H=0 and
        // intersect it with the physical Poincare image before starting.
        escapeReducedApplicable = true;
        const interval escapeRadicand = sqr(event[1]) -
            p.c * sqr(event[0]) + interval(2.) * p.a *
            integerPower(event[0], 3) / interval(3.) -
            p.b * integerPower(event[0], 4) / interval(2.);
        if (escapeRadicand.leftBound() <= 0.)
          throw std::runtime_error(
              "escape seam lost the positive zero-energy Q branch");
        interval escapeQIntersection;
        if (!intersection(event[3], sqrt(escapeRadicand),
                          escapeQIntersection))
          throw std::runtime_error(
              "escape physical and zero-energy Q enclosures are disjoint");
        escapeSeamQ = escapeQIntersection;
        IVector escapeInitial(7);
        escapeInitial[0] = event[0];
        escapeInitial[1] = event[1];
        escapeInitial[2] = escapeQIntersection;
        escapeInitial[3] = event[4];
        escapeInitial[4] = event[5];
        escapeInitial[5] = event[6];
        escapeInitial[6] = interval(0.);
        C0HOTripletonSet escapeSet(escapeInitial);
        escapeSet.setCurrentTime(interval(0.));
        escapeDenseQHull = escapeInitial[2];
        IMap escapeField(
            "time:vv;par:rc,a2c,epsc;"
            "var:uu,pp,qq,er,ea,ee,clock;"
            "fun:pp/qq,((2*(rc+er)*(a2c+ea)+sqrt(epsc+ee)*(rc+er)^4*"
            "(a2c+ea)^2)*uu-vv-(1+sqrt(epsc+ee)*(rc+er)^3*"
            "(a2c+ea))*uu^2+(sqrt(epsc+ee)/3)*(rc+er)^2*uu^3)/qq,"
            "uu/qq,0,0,0,1/qq;");
        escapeField.setParameter("rc", parameterCentre[0]);
        escapeField.setParameter("a2c", parameterCentre[1]);
        escapeField.setParameter("epsc", parameterCentre[2]);
        IOdeSolver escapeSolver(escapeField, 20);
        escapeSolver.setAbsoluteTolerance(1.e-13);
        escapeSolver.setRelativeTolerance(1.e-13);
        escapeSolver.setMaxStep(.01);
        ITimeMap escapeMap(escapeSolver);
        escapeMap.stopAfterStep(true);
        const interval escapeTargetV = interval(4.) / interval(5.);
        IVector escapeEvent(7);
        do {
          escapeEvent = escapeMap(escapeTargetV, escapeSet);
          const interval stepQ = escapeSet.getLastEnclosure()[2];
          escapeDenseQHull = intervalHull(escapeDenseQHull, stepQ);
          ++escapeDenseSteps;
          if (stepQ.leftBound() <= 0.)
            throw std::runtime_error("escape V-time passage lost Q>0");
        } while (!escapeMap.completed());
        escapeReducedClock = escapeEvent[6];
        escapeReducedPassed = escapeReducedClock.leftBound() > 0. &&
            escapeEvent[2].leftBound() > 0.;
        if (!escapeReducedPassed)
          throw std::runtime_error("escape V-time passage did not close");
        IVector escapePhysical(9);
        escapePhysical[0] = escapeEvent[0];
        escapePhysical[1] = escapeEvent[1];
        escapePhysical[2] = escapeTargetV;
        escapePhysical[3] = escapeEvent[2];
        escapePhysical[4] = escapeEvent[3];
        escapePhysical[5] = escapeEvent[4];
        escapePhysical[6] = escapeEvent[5];
        escapePhysical[7] = event[7];
        escapePhysical[8] = event[8];
        const interval physicalEscapeTime =
            set.getCurrentTime() + escapeReducedClock;
        set = C0HOTripletonSet(escapePhysical);
        set.setCurrentTime(physicalEscapeTime);
      } else if (poleRoute == "V_STEPS") {
        event = hitSection(2, interval(1.) / interval(2.), "V=.5 UP", +1);
        event = hitSection(2, interval(3.) / interval(4.), "V=.75 UP", +1);
        event = hitSection(
            2, interval(4.) / interval(5.), "V=.8 UP", +1);
      }
      event = hitSection(
          0, -interval(1.) / interval(5.), "U=-.2 DOWN", -1);
      event = hitSection(
          0, -interval(1.) / interval(2.), "U=-.5 DOWN", -1);
      event = hitSection(0, interval(-1.), "U=-1 DOWN", -1);
      event = hitSection(0, interval(-2.), "U=-2 DOWN", -1);
      event = hitSection(0, interval(-4.), "U=-4 DOWN", -1);
      event = hitSection(0, interval(-7.), "U=-7 DOWN", -1);
      event = hitSection(0, selected.terminalU, "U=-10 DOWN", -1);
      returnTime = legTimes.back();
    } else if (selected.id == "ALG") {
      // The physical four-dimensional enclosure reaches U=-4 reliably, but
      // its energy-normal wrapping is exponentially amplified on the long
      // algebraic tail.  At the first U=-4 hit, restrict again to H=0 and use
      // the exact weighted two-dimensional system
      //
      //   e=-1/U, p=P e^(3/2), q=Q e^(3/2), tau=1/4-e.
      //
      // The variables r,a2,epsilon and the physical clock are carried as
      // static/dynamic auxiliaries.  On the negative branch p=-sqrt(w), and
      // completion while w>0 gives dU/dtau=-e^{-2}<0.  Thus the fixed
      // terminal gate is the first hit after the U=-4 seam.
      const std::array<interval, 7> algSections = {
          -interval(1.) / interval(20.),
          -interval(1.) / interval(5.),
          -interval(1.) / interval(2.),
          interval(-1.), interval(-2.), interval(-3.), interval(-4.)};
      for (std::size_t index = 0; index < algSections.size(); ++index) {
        const interval target = algSections[index];
        event = hitSection(
            0, interval(target),
            index + 1 == algSections.size()
                ? "U=-4 DOWN" : "ALG U STEP DOWN", -1);
      }
      algReducedApplicable = true;
      algSeamTime = legTimes.back();
      algSeamP = event[1];
      algSeamQ = event[3];
      if (algSeamP.rightBound() >= 0.)
        throw std::runtime_error("ALG seam lost P<0");
      // On the negative branch put w=p^2, where p=P e^(3/2) and e=1/4 at
      // the seam.  The exact (w,q) field regularizes the radial equation;
      // q and the clock retain 1/sqrt(w), so every accepted time step is
      // checked to stay in w>0.  Start from the rigorous segmented C0
      // Poincare image; no unverified C1 composition is used here.
      IVector reducedInitial(6);
      reducedInitial[0] = sqr(event[1] / interval(8.));
      reducedInitial[1] = event[3] / interval(8.);
      reducedInitial[2] = event[4];
      reducedInitial[3] = event[5];
      reducedInitial[4] = event[6];
      reducedInitial[5] = interval(0.);
      C0HOTripletonSet reducedSet(reducedInitial);
      algDenseWHull = reducedInitial[0];
      if (reducedInitial[0].leftBound() <= 0.)
        throw std::runtime_error("ALG seam does not enter w>0");

      IMap reducedField(
          "time:tau;par:rc,a2c,epsc;"
          "var:w,qq,er,ea,ee,clock;"
          "fun:-2*w/(0.25-tau)-qq^2/(0.25-tau)"
          "+4*(1+sqrt(epsc+ee)*(rc+er)^3*(a2c+ea))"
          "/(3*(0.25-tau))"
          "+(2*(rc+er)*(a2c+ea)+sqrt(epsc+ee)*(rc+er)^4*"
          "(a2c+ea)^2)"
          "+3*(sqrt(epsc+ee)*(rc+er)^2/3)"
          "/(2*(0.25-tau)^2),"
          "-1/sqrt(w)-3*qq/(2*(0.25-tau)),"
          "0,0,0,1/sqrt(w*(0.25-tau));");
      reducedField.setParameter("rc", parameterCentre[0]);
      reducedField.setParameter("a2c", parameterCentre[1]);
      reducedField.setParameter("epsc", parameterCentre[2]);
      IOdeSolver reducedSolver(reducedField, 20);
      reducedSolver.setAbsoluteTolerance(1.e-13);
      reducedSolver.setRelativeTolerance(1.e-13);
      reducedSolver.setMaxStep(.002);
      ITimeMap reducedMap(reducedSolver);
      reducedMap.stopAfterStep(true);
      IVector reducedEvent(6);
      constexpr int kAlgTailSlabs = 15;
      for (int slab = 1; slab <= kAlgTailSlabs; ++slab) {
        const interval targetTau = interval(77 * slab) /
                                   interval(400 * kAlgTailSlabs);
        do {
          reducedEvent = reducedMap(targetTau, reducedSet);
          const interval stepW = reducedSet.getLastEnclosure()[0];
          algDenseWHull = intervalHull(algDenseWHull, stepW);
          ++algDenseSteps;
          if (stepW.leftBound() <= 0.)
            throw std::runtime_error("ALG reduced tail lost w>0");
        } while (!reducedMap.completed());
        algReducedTimes.push_back(targetTau);
        algReducedW.push_back(reducedEvent[0]);
        algReducedQ.push_back(reducedEvent[1]);
        if (reducedEvent[0].leftBound() <= 0.)
          throw std::runtime_error("ALG reduced tail lost w>0");
      }
      const interval terminalE = interval(23.) / interval(400.);
      const interval terminalScale = terminalE * sqrt(terminalE);
      const interval terminalR = parameterCentre[0] + reducedEvent[2];
      const interval terminalA2 = parameterCentre[1] + reducedEvent[3];
      const interval terminalEpsilon = parameterCentre[2] + reducedEvent[4];
      const interval terminalRootEpsilon = sqrt(terminalEpsilon);
      const interval terminalR2 = sqr(terminalR);
      const interval terminalA = interval(1.) + terminalRootEpsilon *
                                 terminalR2 * terminalR * terminalA2;
      const interval terminalB = terminalRootEpsilon * terminalR2 /
                                 interval(3.);
      const interval terminalC = interval(2.) * terminalR * terminalA2 +
          terminalRootEpsilon * sqr(terminalR2) * sqr(terminalA2);
      event = IVector(9);
      event[0] = -interval(1.) / terminalE;
      event[1] = -sqrt(reducedEvent[0]) / terminalScale;
      event[3] = reducedEvent[1] / terminalScale;
      event[2] = (reducedEvent[0] - sqr(reducedEvent[1]) -
          interval(2.) * terminalA / interval(3.)) /
          (interval(2.) * sqr(terminalE)) -
          terminalC / (interval(2.) * terminalE) -
          terminalB /
          (interval(4.) * integerPower(terminalE, 3));
      event[4] = terminalR;
      event[5] = terminalA2;
      event[6] = terminalEpsilon;
      event[7] = interval(0.);
      event[8] = interval(0.);
      algTailClock = reducedEvent[5];
      returnTime = algSeamTime + algTailClock;
      algTerminalEnergy = sqr(event[1]) / interval(2.) -
          sqr(event[3]) / interval(2.) -
          terminalC * sqr(event[0]) / interval(2.) +
          event[0] * event[2] + terminalA * integerPower(event[0], 3) /
          interval(3.) - terminalB * integerPower(event[0], 4) /
          interval(4.);
      algReducedPassed = algTailClock.leftBound() > 0. &&
          event[1].rightBound() < 0. && reducedEvent[0].leftBound() > 0.;
    } else {
      event = hitSection(0, selected.terminalU, "TERMINAL U DOWN", -1);
      returnTime = legTimes[0];
    }
    const interval sectionResidual = event[0] - selected.terminalU;
    const bool transverse = event[1].rightBound() < 0.;
    const bool timePositive = returnTime.leftBound() > 0.;
    bool eventSequencePassed = true;
    for (int leg = 0; leg < legCount; ++leg) {
      eventSequencePassed = eventSequencePassed &&
          legTimes[leg].leftBound() > 0. &&
          legSectionResiduals[leg].contains(0.) &&
          !legSectionSpeeds[leg].contains(0.);
    }
    for (int leg = 0; leg < legCount; ++leg) {
      eventSequencePassed = eventSequencePassed &&
          (legExpectedSigns[leg] < 0
               ? legSectionSpeeds[leg].rightBound() < 0.
               : legSectionSpeeds[leg].leftBound() > 0.);
    }
    bool escapeConePassed = selected.id != "POLE";
    bool preEscapeGuardPassed = selected.id != "POLE";
    interval guardMinimumU(0.), guardMinimumAcceleration(0.);
    interval guardMaximumU(0.), guardMaximumAcceleration(0.);
    interval guardFinalP(0.);
    interval guardEscapeResidual(0.);
    interval guardMinimumTime(0.), guardMaximumTime(0.);
    interval guardEscapeTime(0.);
    interval escapeY(0.), escapeD(0.), escapeK(0.), escapeGamma(0.);
    interval escapeKPrimeMargin(0.);
    if (selected.id == "POLE") {
      // A second, section-independent guard starts at the first U=-.05
      // crossing.  It takes the first upward P=0 crossing (the bounded
      // minimum), the next downward P=0 crossing (the bounded maximum), and
      // then the first downward U=-.2 crossing.  Between these three events
      // U is respectively decreasing, increasing, and unable to reach -10
      // before crossing -.2.  This excludes an earlier pole gate even though
      // the main enclosure uses Q/V sections for numerical conditioning.
      if (!firstDownSet)
        throw std::runtime_error("missing first-down guard source");
      C0HOTripletonSet guardSet(*firstDownSet);
      const auto guardHit = [&](int coordinate, const interval& target,
                                poincare::CrossingDirection direction,
                                interval& hitTime) {
        IOdeSolver guardSolver(field, 20);
        guardSolver.setAbsoluteTolerance(1.e-13);
        guardSolver.setRelativeTolerance(1.e-13);
        guardSolver.setMaxStep(.02);
        ICoordinateSection guardSection(9, coordinate, target);
        IPoincareMap guardPoincare(guardSolver, guardSection, direction);
        guardPoincare.setMaxReturnTime(30.);
        guardPoincare.setBlowUpMaxNorm(1.e8);
        return guardPoincare(guardSet, hitTime);
      };
      const IVector minimum = guardHit(
          1, interval(0.), poincare::MinusPlus, guardMinimumTime);
      guardMinimumU = minimum[0];
      guardMinimumAcceleration = p.c * minimum[0] - minimum[2] -
          p.a * sqr(minimum[0]) + p.b * integerPower(minimum[0], 3);
      const IVector maximum = guardHit(
          1, interval(0.), poincare::PlusMinus, guardMaximumTime);
      guardMaximumU = maximum[0];
      guardMaximumAcceleration = p.c * maximum[0] - maximum[2] -
          p.a * sqr(maximum[0]) + p.b * integerPower(maximum[0], 3);
      const IVector guardedEscape = guardHit(
          0, -interval(1.) / interval(5.), poincare::PlusMinus,
          guardEscapeTime);
      guardFinalP = guardedEscape[1];
      guardEscapeResidual = guardedEscape[0] +
                            interval(1.) / interval(5.);
      preEscapeGuardPassed = guardMinimumU.leftBound() > -1. &&
          guardMinimumAcceleration.leftBound() > 0. &&
          guardMaximumU.leftBound() > 0. &&
          guardMaximumAcceleration.rightBound() < 0. &&
          guardFinalP.rightBound() < 0. &&
          guardEscapeResidual.contains(0.) &&
          guardMinimumTime.leftBound() > 0. &&
          guardMaximumTime.leftBound() > guardMinimumTime.rightBound() &&
          guardEscapeTime.leftBound() > guardMaximumTime.rightBound() &&
          returnTime.leftBound() > guardEscapeTime.rightBound();

      // Evaluate the invariant cone on the guard's first U=-1/5 image, not
      // on the separately propagated numerical route.  This joins the
      // no-earlier-hit argument and the escape argument pointwise.
      const interval escapeX = interval(1.) / interval(5.);
      escapeY = -guardedEscape[1];
      escapeD = sqr(escapeX) / interval(2.) + guardedEscape[2];
      escapeK = escapeX * escapeY + guardedEscape[3];
      // For x>=1/5 and a>1/2,
      //   y' >= D + gamma*x,
      // gamma=(a-1/2)/5+c.  Hence on the positive (y,D,K) cone,
      // K' >= y_entry^2 + gamma*x^2-x
      //    >= y_entry^2-1/(4 gamma).
      // These strict entry inequalities make that cone forward invariant;
      // in particular x'=y>0 up to and beyond the x=10 gate.
      escapeGamma = (p.a - interval(.5)) * escapeX + p.c;
      if (escapeGamma.leftBound() > 0.) {
        escapeKPrimeMargin = sqr(escapeY) -
            interval(1.) / (interval(4.) * escapeGamma);
      }
      escapeConePassed = guardEscapeResidual.contains(0.) &&
          escapeY.leftBound() > 2. && escapeD.leftBound() > 0. &&
          escapeK.leftBound() > 0. && p.a.leftBound() > .5 &&
          escapeGamma.leftBound() > 0. && p.b.leftBound() >= 0. &&
          escapeKPrimeMargin.leftBound() > 0.;
    }
    // A rigorous Poincare image is an enclosure of points on the section;
    // its ambient coordinate enclosure need not collapse to the point value.
    // Requiring a tiny residual width would therefore be a representation
    // error, not a mathematical transversality test.
    const bool sectionPassed = sectionResidual.contains(0.);
    bool conePassed = true;
    bool p3ZeroActionEntryPassed = true;
    interval poleY(0.), poleD(0.), poleK(0.), poleYPrime(0.);
    interval poleKPrime(0.);
    if (selected.id == "POLE") {
      // Pole coordinates are (x,y,z,zeta)=(-U,-P,-V,-Q).  On x=10,
      // D=x^2/2-z=50+V and K=xy-zeta=-10P+Q.  Strict positivity places
      // the complete event image in the interior of the forward-invariant
      // cone used by Theorem V3.
      const interval poleX(10.);
      poleY = -event[1];
      poleD = sqr(poleX) / interval(2.) + event[2];
      poleK = poleX * poleY + event[3];
      poleYPrime = poleD + (p.a - interval(.5)) * sqr(poleX) +
                   p.c * poleX + p.b * integerPower(poleX, 3);
      poleKPrime = sqr(poleY) + poleX * poleYPrime - poleX;
      conePassed = poleY.leftBound() > 0. && poleD.leftBound() > 0. &&
                   poleK.leftBound() > 0. &&
                   poleYPrime.leftBound() > 0. &&
                   poleKPrime.leftBound() > 0.;
      p3ZeroActionEntryPassed = poleY.leftBound() >= 13. &&
          poleD.leftBound() >= 26. && poleK.leftBound() >= 131.;
    }
    const bool passed = transverse && timePositive && sectionPassed &&
                        eventSequencePassed && preEscapeGuardPassed &&
                        escapeConePassed && conePassed &&
                        p3ZeroActionEntryPassed && algReducedPassed &&
                        turnReducedPassed && escapeReducedPassed;

    std::cout << std::setprecision(17)
              << "{\"status\":\"" << (passed ? "PASS" : "INCONCLUSIVE")
              << "\",\"scope\":\"P2E_AXIS_" << selected.id
              << "_TERMINAL_FIRST_HIT_CELL_SCOUT\",\"claim_bearing\":false"
              << ",\"cell\":{"
              << "\"r_index\":" << rIndex << ",\"a2_index\":" << a2Index
              << ",\"epsilon_index\":" << epsilonIndex << "}"
              << ",\"split_path\":\"" << splitPath << "\""
              << ",\"pole_route\":\"" << poleRoute << "\""
              << ",\"parameter_box\":{\"r\":" << intervalString(p.r)
              << ",\"a2\":" << intervalString(p.a2)
              << ",\"epsilon\":" << intervalString(p.epsilon) << "}"
              << ",\"phase\":" << intervalString(selectedPhase)
              << ",\"graph_error\":" << intervalString(graphError)
              << ",\"source_U\":" << intervalString(initial[0])
              << ",\"return_time\":" << intervalString(returnTime)
              << ",\"event_sequence_labels\":[";
    for (int leg = 0; leg < legCount; ++leg) {
      if (leg) std::cout << ',';
      std::cout << '\"' << legLabels[leg] << '\"';
    }
    std::cout << "]"
              << ",\"leg_return_times\":[";
    for (int leg = 0; leg < legCount; ++leg) {
      if (leg) std::cout << ',';
      std::cout << intervalString(legTimes[leg]);
    }
    std::cout << "]\n"
              << ",\"leg_section_residuals\":[";
    for (int leg = 0; leg < legCount; ++leg) {
      if (leg) std::cout << ',';
      std::cout << intervalString(legSectionResiduals[leg]);
    }
    std::cout << "]"
              << ",\"leg_section_speeds\":[";
    for (int leg = 0; leg < legCount; ++leg) {
      if (leg) std::cout << ',';
      std::cout << intervalString(legSectionSpeeds[leg]);
    }
    std::cout << "]"
              << ",\"event_sequence_passed\":"
              << (eventSequencePassed ? "true" : "false")
              << ",\"escape_cone_entry\":{\"applicable\":"
              << (selected.id == "POLE" ? "true" : "false")
              << ",\"passed\":" << (escapeConePassed ? "true" : "false")
              << ",\"x\":[0.2,0.2]"
              << ",\"y\":" << intervalString(escapeY)
              << ",\"D\":" << intervalString(escapeD)
              << ",\"K\":" << intervalString(escapeK)
              << ",\"gamma\":" << intervalString(escapeGamma)
              << ",\"K_prime_boundary_margin\":"
              << intervalString(escapeKPrimeMargin) << "}"
              << ",\"pre_escape_no_pole_guard\":{\"applicable\":"
              << (selected.id == "POLE" ? "true" : "false")
              << ",\"passed\":"
              << (preEscapeGuardPassed ? "true" : "false")
              << ",\"minimum_time\":" << intervalString(guardMinimumTime)
              << ",\"minimum_U\":" << intervalString(guardMinimumU)
              << ",\"minimum_P_prime\":"
              << intervalString(guardMinimumAcceleration)
              << ",\"maximum_time\":" << intervalString(guardMaximumTime)
              << ",\"maximum_U\":" << intervalString(guardMaximumU)
              << ",\"maximum_P_prime\":"
              << intervalString(guardMaximumAcceleration)
              << ",\"escape_time\":" << intervalString(guardEscapeTime)
              << ",\"escape_P\":" << intervalString(guardFinalP)
              << ",\"escape_section_residual\":"
              << intervalString(guardEscapeResidual) << "}"
              << ",\"terminal_U\":" << intervalString(event[0])
              << ",\"terminal_P\":" << intervalString(event[1])
              << ",\"terminal_V\":" << intervalString(event[2])
              << ",\"terminal_Q\":" << intervalString(event[3])
              << ",\"section_residual\":"
              << intervalString(sectionResidual)
              << ",\"first_section_encounter_mode\":"
                 "\"DIRECTED_BY_STRICT_SPEED_SIGN\""
              << ",\"terminal_speed_strictly_negative\":"
              << (transverse ? "true" : "false")
              << ",\"pole_upper_turn_reduced_passage\":{\"applicable\":"
              << (turnReducedApplicable ? "true" : "false")
              << ",\"passed\":" << (turnReducedPassed ? "true" : "false")
              << ",\"seam_U\":"
              << intervalString(-interval(1.) / interval(20.))
              << ",\"seam_V\":" << intervalString(turnSeamV)
              << ",\"terminal_U\":"
              << intervalString(interval(11.) / interval(5.))
              << ",\"clock\":" << intervalString(turnClock)
              << ",\"dense_step_count\":" << turnDenseSteps
              << ",\"dense_P_hull\":" << intervalString(turnDensePHull)
              << "}"
              << ",\"pole_escape_reduced_passage\":{\"applicable\":"
              << (escapeReducedApplicable ? "true" : "false")
              << ",\"passed\":"
              << (escapeReducedPassed ? "true" : "false")
              << ",\"seam_V\":" << intervalString(interval(0.))
              << ",\"seam_Q\":" << intervalString(escapeSeamQ)
              << ",\"terminal_V\":"
              << intervalString(interval(4.) / interval(5.))
              << ",\"clock\":" << intervalString(escapeReducedClock)
              << ",\"dense_step_count\":" << escapeDenseSteps
              << ",\"dense_Q_hull\":" << intervalString(escapeDenseQHull)
              << "}"
              << ",\"alg_reduced_zero_energy_tail\":{\"applicable\":"
              << (algReducedApplicable ? "true" : "false")
              << ",\"passed\":" << (algReducedPassed ? "true" : "false")
              << ",\"seam_time\":" << intervalString(algSeamTime)
              << ",\"seam_P\":" << intervalString(algSeamP)
              << ",\"seam_Q\":" << intervalString(algSeamQ)
              << ",\"tail_clock\":" << intervalString(algTailClock)
              << ",\"dense_step_count\":" << algDenseSteps
              << ",\"dense_w_hull\":" << intervalString(algDenseWHull)
              << ",\"tau_nodes\":[";
    for (std::size_t index = 0; index < algReducedTimes.size(); ++index) {
      if (index) std::cout << ',';
      std::cout << intervalString(algReducedTimes[index]);
    }
    std::cout << "]"
              << ",\"w_nodes\":[";
    for (std::size_t index = 0; index < algReducedW.size(); ++index) {
      if (index) std::cout << ',';
      std::cout << intervalString(algReducedW[index]);
    }
    std::cout << "]"
              << ",\"q_nodes\":[";
    for (std::size_t index = 0; index < algReducedQ.size(); ++index) {
      if (index) std::cout << ',';
      std::cout << intervalString(algReducedQ[index]);
    }
    std::cout << "]"
              << ",\"energy_reconstruction_identity\":"
              << (algReducedApplicable ? "true" : "false")
              << ",\"energy_reconstruction_identity_kind\":"
                 "\"BY_EXACT_ZERO_ENERGY_FORMULA_CONSTRUCTION\""
              << ",\"naive_interval_energy_diagnostic_nonpredicate\":"
              << intervalString(algTerminalEnergy) << "}"
              << ",\"pole_cone\":{\"applicable\":"
              << (selected.id == "POLE" ? "true" : "false")
              << ",\"passed\":" << (conePassed ? "true" : "false")
              << ",\"y\":" << intervalString(poleY)
              << ",\"D\":" << intervalString(poleD)
              << ",\"K\":" << intervalString(poleK)
              << ",\"y_prime\":" << intervalString(poleYPrime)
              << ",\"K_prime\":" << intervalString(poleKPrime) << "}"
              << ",\"p3_zero_action_entry_bounds\":{\"applicable\":"
              << (selected.id == "POLE" ? "true" : "false")
              << ",\"passed\":"
              << (p3ZeroActionEntryPassed ? "true" : "false")
              << ",\"thresholds\":{\"y\":13,\"D\":26,\"K\":131}}"
              << ",\"nonclaim\":\"One outward-rounded bridge-cell hit is "
                 "not the complete first-event skeleton, incidence census, "
                 "or V2.EVENT_ATLAS.\"}\n";
    return passed ? 0 : 10;
  } catch (const std::exception& error) {
    std::cerr << "P2e axis terminal first-hit scout failed: " << error.what()
              << '\n';
    return 11;
  }
}
