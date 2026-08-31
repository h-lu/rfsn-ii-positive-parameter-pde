#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
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

constexpr std::int64_t kLargestExactlyRepresentableInteger =
    std::int64_t{1} << 53;

interval exactInteger(std::int64_t value) {
  if (value < -kLargestExactlyRepresentableInteger ||
      value > kLargestExactlyRepresentableInteger)
    throw std::overflow_error(
        "rational-cell integer exceeds exact binary64 range");
  return interval(static_cast<double>(value));
}

interval rationalCell(std::int64_t leftNumerator,
                      std::int64_t rightNumerator,
                      std::int64_t denominator) {
  if (denominator <= 0)
    throw std::invalid_argument("rational-cell denominator must be positive");
  const interval left = exactInteger(leftNumerator) /
                        exactInteger(denominator);
  const interval right = exactInteger(rightNumerator) /
                         exactInteger(denominator);
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
    std::int64_t rLocalIndex = 0;
    std::int64_t rSubdivisionCount = 1;
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
        if (rSubdivisionCount >
            kLargestExactlyRepresentableInteger / (2 * 400))
          throw std::invalid_argument(
              "too many r splits for exact rational-grid reconstruction");
        rSubdivisionCount *= 2;
        rLocalIndex = 2 * rLocalIndex + splitHalf;
        // Reconstruct every binary descendant directly on the exact rational
        // grid of its parent [rIndex/400,(rIndex+1)/400].  In particular,
        // extra splits after the three canonical bits never inherit a rounded
        // binary64 midpoint that can protrude beyond the requested/source box.
        const std::int64_t globalRLeaf =
            std::int64_t{rIndex} * rSubdivisionCount + rLocalIndex;
        const std::int64_t denominator = 400 * rSubdivisionCount;
        p.r = rationalCell(globalRLeaf, globalRLeaf + 1, denominator);
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
    std::vector<interval> algReducedD;
    std::vector<interval> algReducedCancellationResiduals;
    std::unique_ptr<C0HOTripletonSet> firstDownSet;
    IVector firstDownEvent(9);
    interval firstDownTime(0.);
    bool firstDownRecorded = false;
    bool firstDownEntryPassed = selected.id != "POLE";
    bool firstDownFallbackTriggered = false;
    std::string firstDownEntryMethod = "NOT_APPLICABLE";
    interval firstDownAnchorTime(0.), firstDownAnchorResidual(0.);
    interval firstDownAnchorP(0.), firstDownPreZeroClock(0.);
    interval firstDownPreZeroPHull(0.), firstDownZeroTime(0.);
    interval firstDownZeroP(0.), firstDownZeroQ(0.);
    interval firstDownZeroBranchQ(0.), firstDownPostZeroClock(0.);
    interval firstDownPostZeroPHull(0.);
    int firstDownPreZeroSteps = 0, firstDownPostZeroSteps = 0;
    bool algReducedApplicable = false;
    bool algReducedPassed = true;
    bool algFiniteReducedApplicable = false;
    bool algFiniteReducedPassed = true;
    interval algFiniteSeamTime(0.), algFiniteSeamP(0.);
    interval algFiniteSeamEnergy(0.), algFiniteSeamV(0.);
    interval algFiniteDenseWHull(0.), algFiniteClock(0.);
    interval algFiniteTerminalEnergy(0.);
    int algFiniteDenseSteps = 0;
    std::vector<interval> algFiniteX;
    std::vector<interval> algFiniteClocks;
    std::vector<interval> algFiniteW;
    std::vector<interval> algFiniteQ;
    interval algSeamTime(0.), algSeamP(0.), algSeamQ(0.);
    interval algTerminalEnergy(0.);
    interval algTailClock(0.), algDenseWHull(0.);
    int algDenseSteps = 0;
    bool turnReducedApplicable = false;
    bool turnReducedPassed = true;
    interval turnSeamV(0.), turnSeamTime(0.), turnClock(0.);
    interval turnTerminalTime(0.), turnDensePHull(0.);
    int turnDenseSteps = 0;
    bool escapeReducedApplicable = false;
    bool escapeReducedPassed = true;
    interval escapeSeamTime(0.), escapeTerminalTime(0.);
    interval escapePmaxU(0.), escapePmaxV(0.), escapePmaxQ(0.);
    interval escapePmaxF(0.), escapeMClock(0.), escapeMDenseFHull(0.);
    interval escapeUClock(0.), escapeUDensePHull(0.);
    interval escapeZeroP(0.), escapeZeroQ(0.), escapeZeroBranchQ(0.);
    interval escapeXClock(0.), escapeXDensePHull(0.);
    int escapeMDenseSteps = 0, escapeUDenseSteps = 0;
    int escapeXDenseSteps = 0;
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
      if (label == "U=-.05 DOWN I") {
        firstDownSet = std::make_unique<C0HOTripletonSet>(set);
        firstDownEvent = hit;
        firstDownTime = hitTime;
        firstDownRecorded = true;
      }
      ++legCount;
      return hit;
    };
    if (selected.id == "POLE") {
      // Follow the actual global turn sequence before the escaping pole
      // leg.  A naive U=-.5 intermediate section is almost tangent to the
      // first left excursion and causes severe wrapping.  The two Q=0 and
      // two P=0 turns separate that bounded excursion from the final escape.
      const interval firstDownTargetU =
          -interval(1.) / interval(20.);
      try {
        // Keep the main set and solver untouched until the direct map has
        // succeeded.  A failed CAPD Poincare call may leave its set near the
        // problematic section and is not a valid fallback source.
        C0HOTripletonSet directSet(set);
        IOdeSolver directSolver(field, 20);
        directSolver.setAbsoluteTolerance(1.e-13);
        directSolver.setRelativeTolerance(1.e-13);
        directSolver.setMaxStep(.02);
        ICoordinateSection directSection(9, 0, firstDownTargetU);
        IPoincareMap directMap(
            directSolver, directSection, poincare::PlusMinus);
        directMap.setMaxReturnTime(30.);
        directMap.setBlowUpMaxNorm(1.e8);
        interval directTime;
        const IVector directEvent = directMap(directSet, directTime);
        if (directEvent[1].rightBound() >= 0.)
          throw std::runtime_error(
              "direct first-down image lost strict P<0");
        set = directSet;
        event = directEvent;
        firstDownSet = std::make_unique<C0HOTripletonSet>(set);
        firstDownEvent = event;
        firstDownTime = directTime;
        firstDownRecorded = true;
        firstDownEntryPassed = true;
        firstDownEntryMethod =
            "DIRECT_U_MINUS_ONE_TWENTIETH_POINCARE";
        legTimes.push_back(firstDownTime);
        legLabels.push_back("U=-.05 DOWN I");
        legExpectedSigns.push_back(-1);
        legSectionResiduals.push_back(event[0] - firstDownTargetU);
        legSectionSpeeds.push_back(event[1]);
        ++legCount;
      } catch (const std::exception&) {
        // Some narrow true-Wu leaves reach the section transversely, but the
        // ambient energy-normal enclosure wraps before CAPD can validate the
        // direct U=-1/20 Poincare image.  First hit the nearby positive
        // section U=1/1000, then use x=-U as the independent variable.  Dense
        // P<0 on both passages proves that the resulting x=0 and x=1/20
        // images are their first arrivals after the directed anchor hit.
        firstDownFallbackTriggered = true;
        firstDownEntryMethod = "U_POSITIVE_ANCHOR_H0_X_TIME";
        const interval anchorU = interval(1.) / interval(1000.);
        if (initial[0].leftBound() <= anchorU.rightBound())
          throw std::runtime_error(
              "first-down fallback source is not above U=1/1000");

        C0HOTripletonSet anchorSet(set);
        IOdeSolver anchorSolver(field, 20);
        anchorSolver.setAbsoluteTolerance(1.e-13);
        anchorSolver.setRelativeTolerance(1.e-13);
        anchorSolver.setMaxStep(.02);
        ICoordinateSection anchorSection(9, 0, anchorU);
        IPoincareMap anchorMap(
            anchorSolver, anchorSection, poincare::PlusMinus);
        anchorMap.setMaxReturnTime(30.);
        anchorMap.setBlowUpMaxNorm(1.e8);
        IVector anchorEvent;
        try {
          anchorEvent = anchorMap(anchorSet, firstDownAnchorTime);
        } catch (const std::exception& error) {
          throw std::runtime_error(
              std::string("first-down U=1/1000 anchor: ") + error.what());
        }
        firstDownAnchorResidual = anchorEvent[0] - anchorU;
        firstDownAnchorP = anchorEvent[1];
        if (!firstDownAnchorResidual.contains(0.) ||
            firstDownAnchorP.rightBound() >= 0. ||
            firstDownAnchorTime.leftBound() <= 0.)
          throw std::runtime_error(
              "first-down U=1/1000 anchor lacks a strict downward hit");

        IMap firstDownXField(
            "time:x;par:rc,a2c,epsc;"
            "var:pp,vv,qq,er,ea,ee,clock;"
            "fun:((2*(rc+er)*(a2c+ea)+sqrt(epsc+ee)*(rc+er)^4*"
            "(a2c+ea)^2)*x+vv+(1+sqrt(epsc+ee)*(rc+er)^3*"
            "(a2c+ea))*x^2+(sqrt(epsc+ee)/3)*(rc+er)^2*x^3)/pp,"
            "-qq/pp,x/pp,0,0,0,-1/pp;");
        firstDownXField.setParameter("rc", parameterCentre[0]);
        firstDownXField.setParameter("a2c", parameterCentre[1]);
        firstDownXField.setParameter("epsc", parameterCentre[2]);

        IVector preZeroInitial(7);
        preZeroInitial[0] = anchorEvent[1];
        preZeroInitial[1] = anchorEvent[2];
        preZeroInitial[2] = anchorEvent[3];
        preZeroInitial[3] = anchorEvent[4];
        preZeroInitial[4] = anchorEvent[5];
        preZeroInitial[5] = anchorEvent[6];
        preZeroInitial[6] = interval(0.);
        C0HOTripletonSet preZeroSet(preZeroInitial);
        preZeroSet.setCurrentTime(-anchorU);
        firstDownPreZeroPHull = preZeroInitial[0];
        IOdeSolver preZeroSolver(firstDownXField, 20);
        preZeroSolver.setAbsoluteTolerance(1.e-13);
        preZeroSolver.setRelativeTolerance(1.e-13);
        preZeroSolver.setMaxStep(1.e-4);
        ITimeMap preZeroMap(preZeroSolver);
        preZeroMap.stopAfterStep(true);
        IVector zeroEvent(7);
        do {
          zeroEvent = preZeroMap(interval(0.), preZeroSet);
          const interval denseP = preZeroSet.getLastEnclosure()[0];
          firstDownPreZeroPHull = intervalHull(
              firstDownPreZeroPHull, denseP);
          ++firstDownPreZeroSteps;
          if (denseP.rightBound() >= 0.)
            throw std::runtime_error(
                "first-down anchor-to-zero x passage lost P<0");
        } while (!preZeroMap.completed());
        firstDownPreZeroClock = zeroEvent[6];
        firstDownZeroTime = firstDownAnchorTime + firstDownPreZeroClock;
        firstDownZeroP = zeroEvent[0];
        firstDownZeroQ = zeroEvent[2];
        if (firstDownPreZeroClock.leftBound() <= 0. ||
            firstDownZeroTime.leftBound() <=
                firstDownAnchorTime.rightBound() ||
            firstDownZeroP.rightBound() >= 0. ||
            firstDownZeroQ.leftBound() <= 0.)
          throw std::runtime_error(
              "first-down U=0 image lost its strict P<0,Q>0 branch");

        // On the zero-energy axis at U=0,
        //   H=(P^2-Q^2)/2=0.
        // The strict signs above select P=-Q.  Intersecting the two physical
        // hulls and then discarding all remaining correlations is a superset
        // reconditioning of the true H=0 image, not a numerical projection.
        if (!intersection(firstDownZeroQ, -firstDownZeroP,
                          firstDownZeroBranchQ))
          throw std::runtime_error(
              "first-down U=0 H=0 P=-Q intersection is empty");
        if (firstDownZeroBranchQ.leftBound() <= 0.)
          throw std::runtime_error(
              "first-down U=0 H=0 branch lost Q>0");

        IVector postZeroInitial(7);
        postZeroInitial[0] = -firstDownZeroBranchQ;
        postZeroInitial[1] = zeroEvent[1];
        postZeroInitial[2] = firstDownZeroBranchQ;
        postZeroInitial[3] = zeroEvent[3];
        postZeroInitial[4] = zeroEvent[4];
        postZeroInitial[5] = zeroEvent[5];
        postZeroInitial[6] = interval(0.);
        C0HOTripletonSet postZeroSet(postZeroInitial);
        postZeroSet.setCurrentTime(interval(0.));
        firstDownPostZeroPHull = postZeroInitial[0];
        IOdeSolver postZeroSolver(firstDownXField, 20);
        postZeroSolver.setAbsoluteTolerance(1.e-13);
        postZeroSolver.setRelativeTolerance(1.e-13);
        postZeroSolver.setMaxStep(.001);
        ITimeMap postZeroMap(postZeroSolver);
        postZeroMap.stopAfterStep(true);
        IVector postZeroEvent(7);
        const interval targetX = interval(1.) / interval(20.);
        do {
          postZeroEvent = postZeroMap(targetX, postZeroSet);
          const interval denseP = postZeroSet.getLastEnclosure()[0];
          firstDownPostZeroPHull = intervalHull(
              firstDownPostZeroPHull, denseP);
          ++firstDownPostZeroSteps;
          if (denseP.rightBound() >= 0.)
            throw std::runtime_error(
                "first-down zero-to-one-twentieth x passage lost P<0");
        } while (!postZeroMap.completed());
        firstDownPostZeroClock = postZeroEvent[6];
        firstDownTime = firstDownZeroTime + firstDownPostZeroClock;
        if (firstDownPostZeroClock.leftBound() <= 0. ||
            firstDownTime.leftBound() <= firstDownZeroTime.rightBound() ||
            postZeroEvent[0].rightBound() >= 0.)
          throw std::runtime_error(
              "first-down post-zero x passage did not close");

        IVector firstDownPhysical(9);
        firstDownPhysical[0] = -targetX;
        firstDownPhysical[1] = postZeroEvent[0];
        firstDownPhysical[2] = postZeroEvent[1];
        firstDownPhysical[3] = postZeroEvent[2];
        firstDownPhysical[4] = postZeroEvent[3];
        firstDownPhysical[5] = postZeroEvent[4];
        firstDownPhysical[6] = postZeroEvent[5];
        // dphi and eta are static flow coordinates.  The independent-variable
        // product enclosures intentionally discard their correlations, so
        // their complete anchor hulls must be carried to the physical restart.
        firstDownPhysical[7] = anchorEvent[7];
        firstDownPhysical[8] = anchorEvent[8];
        set = C0HOTripletonSet(firstDownPhysical);
        set.setCurrentTime(firstDownTime);
        event = firstDownPhysical;
        firstDownSet = std::make_unique<C0HOTripletonSet>(set);
        firstDownEvent = event;
        firstDownRecorded = true;
        firstDownEntryPassed = true;
        legTimes.push_back(firstDownTime);
        legLabels.push_back("U=-.05 DOWN I");
        legExpectedSigns.push_back(-1);
        legSectionResiduals.push_back(event[0] - firstDownTargetU);
        legSectionSpeeds.push_back(event[1]);
        ++legCount;
      }
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
        turnSeamTime = legTimes.back();
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
        // Stay in the well-conditioned U-time representation beyond the
        // Q=0 crossing.  Returning to the ambient physical flow at U=11/5
        // and asking it to locate Q=0 reintroduces precisely the wrapping
        // direction removed at the seam.  U=11/4 is still strictly before
        // the maximum on this route, so dense P>0 proves the whole passage
        // is monotone and gives a safe physical restart for the P=0 event.
        const interval turnTargetU = interval(11.) / interval(4.);
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
        // The Poincare set has already been advanced just past its section.
        // The reduced state, however, is rebuilt from the exact section image,
        // so its physical base time is the Poincare hit time, not the current
        // time carried by that post-section set.
        turnTerminalTime = turnSeamTime + turnClock;
        set = C0HOTripletonSet(turnPhysical);
        set.setCurrentTime(turnTerminalTime);
      }
      if (poleRoute != "TURN_REDUCED")
        event = hitSection(3, interval(0.), "Q=0 UP", +1);
      event = hitSection(1, interval(0.), "P=0 MAX", -1);
      if (poleRoute != "TURN_REDUCED")
        event = hitSection(2, interval(0.), "V=0 UP", +1);
      if (poleRoute == "TURN_REDUCED") {
        // The exact P=0 maximum image lies on H=0.  Eliminate V there before
        // changing independent variables; this removes the energy-normal
        // wrapping that made a downstream V=4/5 seam nonuniform across the
        // bridge box.
        escapeReducedApplicable = true;
        escapeSeamTime = legTimes.back();
        escapePmaxU = event[0];
        escapePmaxQ = event[3];
        if (escapePmaxU.leftBound() <= 0.)
          throw std::runtime_error("escape P=0 maximum lost U>0");
        const interval pmaxVIdentity =
            (sqr(escapePmaxQ) + p.c * sqr(escapePmaxU) -
             interval(2.) * p.a * integerPower(escapePmaxU, 3) /
                 interval(3.) +
             p.b * integerPower(escapePmaxU, 4) / interval(2.)) /
            (interval(2.) * escapePmaxU);
        if (!intersection(event[2], pmaxVIdentity, escapePmaxV))
          throw std::runtime_error(
              "escape P=0 maximum physical and H=0 V enclosures are "
              "disjoint");
        const auto escapeF = [&](const interval& escapeU,
                                  const interval& escapeV) {
          return p.c * escapeU - escapeV - p.a * sqr(escapeU) +
                 p.b * integerPower(escapeU, 3);
        };
        escapePmaxF = escapeF(escapePmaxU, escapePmaxV);
        if (escapePmaxF.rightBound() >= 0.)
          throw std::runtime_error(
              "escape P=0 maximum is not strict F<0");

        // Put m=-P.  Since dm/dt=-F>0 after the strict maximum, advance
        // m from 0 to 1/10 with
        //   dU/dm=m/F, dV/dm=-Q/F, dQ/dm=-U/F, dt/dm=-1/F.
        IVector mInitial(7);
        mInitial[0] = escapePmaxU;
        mInitial[1] = escapePmaxV;
        mInitial[2] = escapePmaxQ;
        mInitial[3] = event[4];
        mInitial[4] = event[5];
        mInitial[5] = event[6];
        mInitial[6] = interval(0.);
        C0HOTripletonSet mSet(mInitial);
        mSet.setCurrentTime(interval(0.));
        escapeMDenseFHull = escapePmaxF;
        IMap mField(
            "time:mm;par:rc,a2c,epsc;"
            "var:uu,vv,qq,er,ea,ee,clock;"
            "fun:mm/((2*(rc+er)*(a2c+ea)+sqrt(epsc+ee)*(rc+er)^4*"
            "(a2c+ea)^2)*uu-vv-(1+sqrt(epsc+ee)*(rc+er)^3*"
            "(a2c+ea))*uu^2+(sqrt(epsc+ee)/3)*(rc+er)^2*uu^3),"
            "-qq/((2*(rc+er)*(a2c+ea)+sqrt(epsc+ee)*(rc+er)^4*"
            "(a2c+ea)^2)*uu-vv-(1+sqrt(epsc+ee)*(rc+er)^3*"
            "(a2c+ea))*uu^2+(sqrt(epsc+ee)/3)*(rc+er)^2*uu^3),"
            "-uu/((2*(rc+er)*(a2c+ea)+sqrt(epsc+ee)*(rc+er)^4*"
            "(a2c+ea)^2)*uu-vv-(1+sqrt(epsc+ee)*(rc+er)^3*"
            "(a2c+ea))*uu^2+(sqrt(epsc+ee)/3)*(rc+er)^2*uu^3),"
            "0,0,0,-1/((2*(rc+er)*(a2c+ea)+sqrt(epsc+ee)*(rc+er)^4*"
            "(a2c+ea)^2)*uu-vv-(1+sqrt(epsc+ee)*(rc+er)^3*"
            "(a2c+ea))*uu^2+(sqrt(epsc+ee)/3)*(rc+er)^2*uu^3);");
        mField.setParameter("rc", parameterCentre[0]);
        mField.setParameter("a2c", parameterCentre[1]);
        mField.setParameter("epsc", parameterCentre[2]);
        IOdeSolver mSolver(mField, 20);
        mSolver.setAbsoluteTolerance(1.e-13);
        mSolver.setRelativeTolerance(1.e-13);
        mSolver.setMaxStep(.005);
        ITimeMap mMap(mSolver);
        mMap.stopAfterStep(true);
        const interval smallM = interval(1.) / interval(10.);
        IVector mEvent(7);
        do {
          mEvent = mMap(smallM, mSet);
          const IVector dense = mSet.getLastEnclosure();
          const interval denseF = escapeF(dense[0], dense[1]);
          escapeMDenseFHull = intervalHull(escapeMDenseFHull, denseF);
          ++escapeMDenseSteps;
          if (denseF.rightBound() >= 0.)
            throw std::runtime_error(
                "escape m passage lost F<0 at m=" +
                intervalString(mSet.getCurrentTime()) + " with F=" +
                intervalString(denseF));
        } while (!mMap.completed());
        escapeMClock = mEvent[6];
        if (escapeMClock.leftBound() <= 0.)
          throw std::runtime_error("escape m clock is not positive");

        // Recondition H=0 at m=1/10 before the long decreasing-U passage.
        const interval smallP = -smallM;
        const interval mVIdentity =
            (sqr(mEvent[2]) - sqr(smallP) + p.c * sqr(mEvent[0]) -
             interval(2.) * p.a * integerPower(mEvent[0], 3) /
                 interval(3.) +
             p.b * integerPower(mEvent[0], 4) / interval(2.)) /
            (interval(2.) * mEvent[0]);
        interval mV;
        if (!intersection(mEvent[1], mVIdentity, mV))
          throw std::runtime_error(
              "escape m=.1 physical and H=0 V enclosures are disjoint");

        // Advance in x=-U from the positive-U image to x=0.  This is the
        // requested U-time passage in a forward coordinate.  Dense P<0
        // proves that U decreases strictly throughout it.
        IMap escapeXField(
            "time:x;par:rc,a2c,epsc;"
            "var:pp,vv,qq,er,ea,ee,clock;"
            "fun:((2*(rc+er)*(a2c+ea)+sqrt(epsc+ee)*(rc+er)^4*"
            "(a2c+ea)^2)*x+vv+(1+sqrt(epsc+ee)*(rc+er)^3*"
            "(a2c+ea))*x^2+(sqrt(epsc+ee)/3)*(rc+er)^2*x^3)/pp,"
            "-qq/pp,x/pp,0,0,0,-1/pp;");
        escapeXField.setParameter("rc", parameterCentre[0]);
        escapeXField.setParameter("a2c", parameterCentre[1]);
        escapeXField.setParameter("epsc", parameterCentre[2]);
        IVector uInitial(7);
        uInitial[0] = smallP;
        uInitial[1] = mV;
        uInitial[2] = mEvent[2];
        uInitial[3] = mEvent[3];
        uInitial[4] = mEvent[4];
        uInitial[5] = mEvent[5];
        uInitial[6] = interval(0.);
        C0HOTripletonSet uSet(uInitial);
        uSet.setCurrentTime(-mEvent[0]);
        escapeUDensePHull = smallP;
        IOdeSolver uSolver(escapeXField, 20);
        uSolver.setAbsoluteTolerance(1.e-13);
        uSolver.setRelativeTolerance(1.e-13);
        uSolver.setMaxStep(.01);
        ITimeMap uMap(uSolver);
        uMap.stopAfterStep(true);
        IVector zeroEvent(7);
        do {
          zeroEvent = uMap(interval(0.), uSet);
          const interval denseP = uSet.getLastEnclosure()[0];
          escapeUDensePHull = intervalHull(escapeUDensePHull, denseP);
          ++escapeUDenseSteps;
          if (denseP.rightBound() >= 0.)
            throw std::runtime_error(
                "escape U-to-zero passage lost P<0 at U=" +
                intervalString(-uSet.getCurrentTime()) + " with P=" +
                intervalString(denseP));
        } while (!uMap.completed());
        escapeUClock = zeroEvent[6];
        escapeZeroP = zeroEvent[0];
        escapeZeroQ = zeroEvent[2];
        if (escapeUClock.leftBound() <= 0. ||
            escapeZeroP.rightBound() >= 0. ||
            escapeZeroQ.leftBound() <= 0.)
          throw std::runtime_error(
              "escape U=0 image lost positive time or P<0,Q>0");

        // At U=0 the zero-energy identity is P^2=Q^2.  The already proved
        // signs P<0<Q select P=-Q; intersect the two rigorous hulls and
        // discard their remaining correlations before the final x passage.
        if (!intersection(escapeZeroQ, -escapeZeroP,
                          escapeZeroBranchQ))
          throw std::runtime_error(
              "escape U=0 H=0 P=-Q intersection is empty");
        if (escapeZeroBranchQ.leftBound() <= 0.)
          throw std::runtime_error(
              "escape U=0 H=0 branch lost Q>0");

        IVector escapeXInitial(7);
        escapeXInitial[0] = -escapeZeroBranchQ;
        escapeXInitial[1] = zeroEvent[1];
        escapeXInitial[2] = escapeZeroBranchQ;
        escapeXInitial[3] = zeroEvent[3];
        escapeXInitial[4] = zeroEvent[4];
        escapeXInitial[5] = zeroEvent[5];
        escapeXInitial[6] = interval(0.);
        C0HOTripletonSet escapeXSet(escapeXInitial);
        escapeXSet.setCurrentTime(interval(0.));
        escapeXDensePHull = escapeXInitial[0];
        IOdeSolver escapeXSolver(escapeXField, 20);
        escapeXSolver.setAbsoluteTolerance(1.e-13);
        escapeXSolver.setRelativeTolerance(1.e-13);
        escapeXSolver.setMaxStep(.005);
        ITimeMap escapeXMap(escapeXSolver);
        escapeXMap.stopAfterStep(true);
        const interval escapeTargetX = interval(1.) / interval(5.);
        IVector escapeXEvent(7);
        do {
          escapeXEvent = escapeXMap(escapeTargetX, escapeXSet);
          const interval denseP = escapeXSet.getLastEnclosure()[0];
          escapeXDensePHull = intervalHull(escapeXDensePHull, denseP);
          ++escapeXDenseSteps;
          if (denseP.rightBound() >= 0.)
            throw std::runtime_error(
                "escape zero-to-.2 x passage lost P<0 at x=" +
                intervalString(escapeXSet.getCurrentTime()) + " with P=" +
                intervalString(denseP));
        } while (!escapeXMap.completed());
        escapeXClock = escapeXEvent[6];
        escapeReducedPassed = escapeXClock.leftBound() > 0. &&
            escapeXEvent[0].rightBound() < 0.;
        if (!escapeReducedPassed)
          throw std::runtime_error(
              "escape zero-to-.2 x passage did not close");
        IVector escapePhysical(9);
        escapePhysical[0] = -escapeTargetX;
        escapePhysical[1] = escapeXEvent[0];
        escapePhysical[2] = escapeXEvent[1];
        escapePhysical[3] = escapeXEvent[2];
        escapePhysical[4] = escapeXEvent[3];
        escapePhysical[5] = escapeXEvent[4];
        escapePhysical[6] = escapeXEvent[5];
        escapePhysical[7] = event[7];
        escapePhysical[8] = event[8];
        // The ledger begins at the exact P=0 maximum event, not at the
        // already post-section physical set.
        escapeTerminalTime = escapeSeamTime + escapeMClock +
                             escapeUClock + escapeXClock;
        set = C0HOTripletonSet(escapePhysical);
        set.setCurrentTime(escapeTerminalTime);
      } else if (poleRoute == "V_STEPS") {
        event = hitSection(2, interval(1.) / interval(2.), "V=.5 UP", +1);
        event = hitSection(2, interval(3.) / interval(4.), "V=.75 UP", +1);
        event = hitSection(
            2, interval(4.) / interval(5.), "V=.8 UP", +1);
      }
      if (poleRoute != "TURN_REDUCED")
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
      // A physical Poincare map is needed only up to U=-1/20.  There P<0
      // is already separated from zero.  Reimpose the exact conserved
      // identity H=0, put x=-U and w=P^2, and use x as the independent
      // variable.  On the negative branch P=-sqrt(w),
      //
      //   dw/dx = w/x-Q^2/x+c x+(4a/3)x^2+(3b/2)x^3,
      //   dQ/dx = -x/sqrt(w),       dt/dx = 1/sqrt(w).
      //
      // Dense w>0 therefore proves P<0 and makes every later fixed-x face
      // the first such face after the directed U=-1/20 hit.  This finite
      // reduction prevents the energy-normal wrapping produced by chaining
      // six additional four-dimensional Poincare maps.
      const interval finiteStartX = interval(1.) / interval(20.);
      event = hitSection(
          0, -finiteStartX, "ALG U STEP DOWN", -1);
      algFiniteReducedApplicable = true;
      algFiniteSeamTime = legTimes.back();
      algFiniteSeamP = event[1];
      algFiniteSeamEnergy = sqr(event[1]) / interval(2.) -
          sqr(event[3]) / interval(2.) - p.c * sqr(event[0]) /
          interval(2.) + event[0] * event[2] +
          p.a * integerPower(event[0], 3) / interval(3.) -
          p.b * integerPower(event[0], 4) / interval(4.);
      if (algFiniteSeamP.rightBound() >= 0. ||
          !algFiniteSeamEnergy.contains(0.))
        throw std::runtime_error(
            "ALG finite seam lacks P<0 or the exact H=0 image");
      const auto algZeroEnergyV = [&](const interval& algU,
                                      const interval& algP,
                                      const interval& algQ) {
        return (sqr(algQ) - sqr(algP) + p.c * sqr(algU) -
                interval(2.) * p.a * integerPower(algU, 3) /
                    interval(3.) +
                p.b * integerPower(algU, 4) / interval(2.)) /
               (interval(2.) * algU);
      };
      if (!intersection(
              event[2], algZeroEnergyV(event[0], event[1], event[3]),
              algFiniteSeamV))
        throw std::runtime_error(
            "ALG finite seam H=0 reconstruction misses physical V");

      IVector finiteInitial(6);
      finiteInitial[0] = sqr(event[1]);
      finiteInitial[1] = event[3];
      finiteInitial[2] = event[4];
      finiteInitial[3] = event[5];
      finiteInitial[4] = event[6];
      finiteInitial[5] = interval(0.);
      algFiniteDenseWHull = finiteInitial[0];
      if (algFiniteDenseWHull.leftBound() <= 0.)
        throw std::runtime_error("ALG finite seam lost w>0");
      IMap finiteField(
          "time:x;par:rc,a2c,epsc;"
          "var:w,qq,er,ea,ee,clock;"
          "fun:w/x-qq^2/x+"
          "(2*(rc+er)*(a2c+ea)+sqrt(epsc+ee)*(rc+er)^4*"
          "(a2c+ea)^2)*x+"
          "4*(1+sqrt(epsc+ee)*(rc+er)^3*(a2c+ea))*x^2/3+"
          "sqrt(epsc+ee)*(rc+er)^2*x^3/2,"
          "-x/sqrt(w),0,0,0,1/sqrt(w);");
      finiteField.setParameter("rc", parameterCentre[0]);
      finiteField.setParameter("a2c", parameterCentre[1]);
      finiteField.setParameter("epsc", parameterCentre[2]);
      IOdeSolver finiteSolver(finiteField, 20);
      finiteSolver.setAbsoluteTolerance(1.e-13);
      finiteSolver.setRelativeTolerance(1.e-13);
      finiteSolver.setMaxStep(.005);
      ITimeMap finiteMap(finiteSolver);
      finiteMap.stopAfterStep(true);
      IVector finiteEvent(6);
      IVector finiteState = finiteInitial;
      interval finiteCurrentX = finiteStartX;
      // The six displayed x-faces are the mathematical event ledger.  Extra
      // exact restart faces in [3,4] only rebox the Lohner enclosure where W
      // becomes small near the algebraic corner; they introduce no new
      // event claim.
      const std::array<interval, 13> finiteRestartTargets = {
          interval(1.) / interval(5.), interval(1.) / interval(2.),
          interval(1.), interval(2.), interval(3.),
          interval(25.) / interval(8.), interval(26.) / interval(8.),
          interval(27.) / interval(8.), interval(28.) / interval(8.),
          interval(29.) / interval(8.), interval(30.) / interval(8.),
          interval(31.) / interval(8.), interval(4.)};
      for (std::size_t index = 0; index < finiteRestartTargets.size();
           ++index) {
        const interval targetX = finiteRestartTargets[index];
        // Restart the Lohner representation at each exact x-face.  This
        // discards correlations but keeps a rigorous interval superset and
        // prevents a single long coordinate frame from accumulating
        // artificial wrapping across all six slabs.
        C0HOTripletonSet finiteSegmentSet(finiteState);
        finiteSegmentSet.setCurrentTime(finiteCurrentX);
        do {
          try {
            finiteEvent = finiteMap(targetX, finiteSegmentSet);
          } catch (const std::exception& error) {
            throw std::runtime_error(
                "ALG finite x=" + intervalString(targetX) +
                " from w=" + intervalString(finiteInitial[0]) +
                ": " + error.what());
          }
          const interval stepW = finiteSegmentSet.getLastEnclosure()[0];
          algFiniteDenseWHull = intervalHull(
              algFiniteDenseWHull, stepW);
          ++algFiniteDenseSteps;
          if (stepW.leftBound() <= 0.)
            throw std::runtime_error(
                "ALG finite reduced passage lost w>0");
        } while (!finiteMap.completed());
        if (finiteEvent[0].leftBound() <= 0.)
          throw std::runtime_error(
              "ALG finite reduced node lost w>0");
        const bool reportFace = index < 5 ||
            index + 1 == finiteRestartTargets.size();
        if (reportFace) {
          algFiniteX.push_back(targetX);
          algFiniteClocks.push_back(finiteEvent[5]);
          algFiniteW.push_back(finiteEvent[0]);
          algFiniteQ.push_back(finiteEvent[1]);
          legTimes.push_back(algFiniteSeamTime + finiteEvent[5]);
          legLabels.push_back(
              index + 1 == finiteRestartTargets.size()
                  ? "U=-4 DOWN" : "ALG U STEP DOWN");
          legExpectedSigns.push_back(-1);
          legSectionResiduals.push_back(-targetX - (-targetX));
          legSectionSpeeds.push_back(-sqrt(finiteEvent[0]));
          ++legCount;
        }
        finiteState = finiteEvent;
        finiteCurrentX = targetX;
      }
      algFiniteClock = finiteEvent[5];
      event = IVector(9);
      event[0] = -finiteRestartTargets.back();
      event[1] = -sqrt(finiteEvent[0]);
      event[3] = finiteEvent[1];
      event[2] = algZeroEnergyV(event[0], event[1], event[3]);
      event[4] = finiteEvent[2];
      event[5] = finiteEvent[3];
      event[6] = finiteEvent[4];
      event[7] = initial[7];
      event[8] = initial[8];
      algFiniteTerminalEnergy = sqr(event[1]) / interval(2.) -
          sqr(event[3]) / interval(2.) - p.c * sqr(event[0]) /
          interval(2.) + event[0] * event[2] +
          p.a * integerPower(event[0], 3) / interval(3.) -
          p.b * integerPower(event[0], 4) / interval(4.);
      algFiniteReducedPassed = algFiniteClock.leftBound() > 0. &&
          algFiniteDenseWHull.leftBound() > 0. &&
          event[1].rightBound() < 0. &&
          algFiniteTerminalEnergy.contains(0.);
      if (!algFiniteReducedPassed)
        throw std::runtime_error(
            "ALG finite zero-energy passage did not close");
      algReducedApplicable = true;
      algSeamTime = legTimes.back();
      algSeamP = event[1];
      algSeamQ = event[3];
      if (algSeamP.rightBound() >= 0.)
        throw std::runtime_error("ALG seam lost P<0");
      // On the negative branch put w=p^2, where p=P e^(3/2) and e=1/4 at
      // the seam.  The exact (w,q) field regularizes the radial equation;
      // q and the clock retain 1/sqrt(w), so every accepted time step is
      // checked to stay in w>0.
      IVector reducedInitial(7);
      reducedInitial[0] = sqr(event[1] / interval(8.));
      reducedInitial[1] = event[3] / interval(8.);
      reducedInitial[2] = interval(4.) * p.a / interval(3.) -
                          interval(2.) * reducedInitial[0] -
                          sqr(reducedInitial[1]);
      reducedInitial[3] = event[4];
      reducedInitial[4] = event[5];
      reducedInitial[5] = event[6];
      reducedInitial[6] = interval(0.);
      algDenseWHull = reducedInitial[0];
      if (reducedInitial[0].leftBound() <= 0. ||
          reducedInitial[1].rightBound() >= 0.)
        throw std::runtime_error("ALG seam does not enter w>0,q<0");

      IMap reducedField(
          "time:tau;par:rc,a2c,epsc;"
          "var:w,qq,dd,er,ea,ee,clock;"
          "fun:-2*w/(0.25-tau)-qq^2/(0.25-tau)"
          "+4*(1+sqrt(epsc+ee)*(rc+er)^3*(a2c+ea))"
          "/(3*(0.25-tau))"
          "+(2*(rc+er)*(a2c+ea)+sqrt(epsc+ee)*(rc+er)^4*"
          "(a2c+ea)^2)"
          "+3*(sqrt(epsc+ee)*(rc+er)^2/3)"
          "/(2*(0.25-tau)^2),"
          "-1/sqrt(w)-3*qq/(2*(0.25-tau)),"
          "2*qq/sqrt(w)+3*qq^2/(0.25-tau)-2*dd/(0.25-tau)"
          "-2*(2*(rc+er)*(a2c+ea)+sqrt(epsc+ee)*(rc+er)^4*"
          "(a2c+ea)^2)-sqrt(epsc+ee)*(rc+er)^2/"
          "(0.25-tau)^2,"
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
      IVector reducedEvent(7);
      IVector reducedState = reducedInitial;
      interval reducedCurrentTau(0.);
      const auto reducedA = [&](const IVector& reduced) {
        const interval reducedR = parameterCentre[0] + reduced[3];
        const interval reducedA2 = parameterCentre[1] + reduced[4];
        const interval reducedEpsilon = parameterCentre[2] + reduced[5];
        return interval(1.) + sqrt(reducedEpsilon) *
               integerPower(reducedR, 3) * reducedA2;
      };
      constexpr int kAlgTailSlabs = 15;
      for (int slab = 1; slab <= kAlgTailSlabs; ++slab) {
        const interval targetTau = interval(77 * slab) /
                                   interval(400 * kAlgTailSlabs);
        C0HOTripletonSet reducedSet(reducedState);
        reducedSet.setCurrentTime(reducedCurrentTau);
        do {
          try {
            reducedEvent = reducedMap(targetTau, reducedSet);
          } catch (const std::exception& error) {
            throw std::runtime_error(
                "ALG tail tau=" + intervalString(targetTau) +
                " from w=" + intervalString(reducedState[0]) +
                ": " + error.what());
          }
          const interval stepW = reducedSet.getLastEnclosure()[0];
          algDenseWHull = intervalHull(algDenseWHull, stepW);
          ++algDenseSteps;
          if (stepW.leftBound() <= 0.)
            throw std::runtime_error("ALG reduced tail lost w>0");
        } while (!reducedMap.completed());
        // The third state is an exactly redundant cancellation coordinate.
        // Intersect its integrated enclosure with its defining identity, and
        // then use the same identity in the reverse directions to sharpen w
        // and the already selected negative q branch.  The half-axis q<0 is
        // forward invariant here: at q=0 the exact reduced equation gives
        // q'=-1/sqrt(w)<0.  Every intersection therefore retains the true
        // trajectory and only removes inconsistent box combinations
        // introduced by interval wrapping.
        for (int recondition = 0; recondition < 2; ++recondition) {
          const interval aAtNode = reducedA(reducedEvent);
          interval tightened;
          const interval dIdentity = interval(4.) * aAtNode / interval(3.) -
              interval(2.) * reducedEvent[0] - sqr(reducedEvent[1]);
          if (!intersection(reducedEvent[2], dIdentity, tightened))
            throw std::runtime_error(
                "ALG tail cancellation identity misses d");
          reducedEvent[2] = tightened;
          const interval wIdentity =
              (interval(4.) * aAtNode / interval(3.) -
               sqr(reducedEvent[1]) - reducedEvent[2]) / interval(2.);
          if (!intersection(reducedEvent[0], wIdentity, tightened))
            throw std::runtime_error(
                "ALG tail cancellation identity misses w");
          reducedEvent[0] = tightened;
          const interval qSquare = interval(4.) * aAtNode / interval(3.) -
              interval(2.) * reducedEvent[0] - reducedEvent[2];
          if (qSquare.leftBound() <= 0. ||
              !intersection(reducedEvent[1], -sqrt(qSquare), tightened))
            throw std::runtime_error(
                "ALG tail cancellation identity misses negative q");
          reducedEvent[1] = tightened;
        }
        algReducedTimes.push_back(targetTau);
        algReducedW.push_back(reducedEvent[0]);
        algReducedQ.push_back(reducedEvent[1]);
        algReducedD.push_back(reducedEvent[2]);
        algReducedCancellationResiduals.push_back(
            reducedEvent[2] -
            (interval(4.) * reducedA(reducedEvent) / interval(3.) -
             interval(2.) * reducedEvent[0] - sqr(reducedEvent[1])));
        if (reducedEvent[0].leftBound() <= 0. ||
            reducedEvent[1].rightBound() >= 0.)
          throw std::runtime_error("ALG reduced tail lost w>0,q<0");
        reducedState = reducedEvent;
        reducedCurrentTau = targetTau;
      }
      const interval terminalE = interval(23.) / interval(400.);
      const interval terminalScale = terminalE * sqrt(terminalE);
      const interval terminalR = parameterCentre[0] + reducedEvent[3];
      const interval terminalA2 = parameterCentre[1] + reducedEvent[4];
      const interval terminalEpsilon = parameterCentre[2] + reducedEvent[5];
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
      algTailClock = reducedEvent[6];
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
    interval guardFinalP(0.), guardFinalV(0.), guardFinalQ(0.);
    interval guardEscapeResidual(0.);
    interval guardMinimumTime(0.), guardMaximumTime(0.);
    interval guardEscapeTime(0.);
    std::string guardMethod = "NOT_APPLICABLE";
    bool guardMonotoneApplicable = false;
    bool guardMonotonePassed = true;
    const std::array<std::string, 8> guardSegmentLabels = {
        "x=.05->.4 P<0", "P->0 MIN F>0", "P=0->.1 F>0",
        "U->2.2 P>0", "m=-P->0 MAX F<0", "m=0->.1 F<0",
        "x=-U POSTMAX->0 P<0", "x=0->.2 P<0"};
    std::array<interval, 8> guardSegmentClocks = {
        interval(0.), interval(0.), interval(0.), interval(0.),
        interval(0.), interval(0.), interval(0.), interval(0.)};
    std::array<int, 8> guardSegmentSteps = {0, 0, 0, 0, 0, 0, 0, 0};
    interval guardDownPHull(0.), guardMinApproachFHull(0.);
    interval guardMinApproachUHull(0.), guardMinExitFHull(0.);
    interval guardRisePHull(0.), guardMaxApproachFHull(0.);
    interval guardMaxApproachUHull(0.), guardMaxExitFHull(0.);
    interval guardPostMaxZeroPHull(0.), guardZeroP(0.), guardZeroQ(0.);
    interval guardZeroBranchQ(0.), guardEscapeXPHull(0.);
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
      if (!firstDownSet || !firstDownRecorded)
        throw std::runtime_error("missing first-down guard source");
      const auto acceleration = [&](const interval& guardU,
                                    const interval& guardV) {
        return p.c * guardU - guardV - p.a * sqr(guardU) +
               p.b * integerPower(guardU, 3);
      };
      try {
        // The inexpensive path is retained for cells on which direct
        // segmented Poincare propagation stays narrow.  If CAPD cannot
        // enclose one of its crossings, the catch block below restarts from
        // the already rigorous first-down image and proves the same ordering
        // through monotone independent-variable passages.
        guardMethod = "DIRECT_SEGMENTED_POINCARE";
        C0HOTripletonSet guardSet(*firstDownSet);
        const auto guardHit = [&](int coordinate, const interval& target,
                                  poincare::CrossingDirection direction,
                                  interval& hitTime,
                                  const std::string& label) {
          IOdeSolver guardSolver(field, 20);
          guardSolver.setAbsoluteTolerance(1.e-13);
          guardSolver.setRelativeTolerance(1.e-13);
          guardSolver.setMaxStep(.02);
          ICoordinateSection guardSection(9, coordinate, target);
          IPoincareMap guardPoincare(guardSolver, guardSection, direction);
          guardPoincare.setMaxReturnTime(30.);
          guardPoincare.setBlowUpMaxNorm(1.e8);
          try {
            return guardPoincare(guardSet, hitTime);
          } catch (const std::exception& error) {
            throw std::runtime_error("GUARD " + label + ": " +
                                     error.what());
          }
        };
        const IVector minimum = guardHit(
            1, interval(0.), poincare::MinusPlus, guardMinimumTime,
            "P=0 MIN");
        guardMinimumU = minimum[0];
        guardMinimumAcceleration = acceleration(minimum[0], minimum[2]);
        const IVector maximum = guardHit(
            1, interval(0.), poincare::PlusMinus, guardMaximumTime,
            "P=0 MAX");
        guardMaximumU = maximum[0];
        guardMaximumAcceleration = acceleration(maximum[0], maximum[2]);
        const IVector guardedEscape = guardHit(
            0, -interval(1.) / interval(5.), poincare::PlusMinus,
            guardEscapeTime, "U=-.2 DOWN");
        guardFinalP = guardedEscape[1];
        guardFinalV = guardedEscape[2];
        guardFinalQ = guardedEscape[3];
        guardEscapeResidual = guardedEscape[0] +
                              interval(1.) / interval(5.);
        if (guardMinimumU.leftBound() <= -1. ||
            guardMinimumAcceleration.leftBound() <= 0. ||
            guardMaximumU.leftBound() <= 0. ||
            guardMaximumAcceleration.rightBound() >= 0. ||
            guardFinalP.rightBound() >= 0. ||
            !guardEscapeResidual.contains(0.) ||
            guardMinimumTime.leftBound() <= 0. ||
            guardMaximumTime.leftBound() <= guardMinimumTime.rightBound() ||
            guardEscapeTime.leftBound() <= guardMaximumTime.rightBound() ||
            returnTime.leftBound() <= guardEscapeTime.rightBound())
          throw std::runtime_error(
              "GUARD direct Poincare margins are inconclusive");
      } catch (const std::exception&) {
        guardMethod = "H0_RECONDITIONED_MONOTONE_INDEPENDENT_VARIABLES";
        guardMonotoneApplicable = true;

        // The exact Hamiltonian identity on H=0 is
        //   V=(Q^2-P^2+cU^2-2aU^3/3+bU^4/2)/(2U).
        // Reconditioning only discards correlations and intersects with the
        // physical enclosure; it never narrows away a true zero-energy
        // trajectory.
        const auto zeroEnergyV = [&](const interval& guardU,
                                     const interval& guardP,
                                     const interval& guardQ) {
          return (sqr(guardQ) - sqr(guardP) + p.c * sqr(guardU) -
                  interval(2.) * p.a * integerPower(guardU, 3) /
                      interval(3.) +
                  p.b * integerPower(guardU, 4) / interval(2.)) /
                 (interval(2.) * guardU);
        };
        const auto intersectOrThrow = [&](const interval& physical,
                                          const interval& identity,
                                          const std::string& label) {
          interval result;
          if (!intersection(physical, identity, result))
            throw std::runtime_error("GUARD " + label +
                                     " H=0 intersection is empty");
          return result;
        };
        const auto configure = [&](IOdeSolver& reducedSolver,
                                   double maxStep) {
          reducedSolver.setAbsoluteTolerance(1.e-13);
          reducedSolver.setRelativeTolerance(1.e-13);
          reducedSolver.setMaxStep(maxStep);
        };

        const interval firstU = -interval(1.) / interval(20.);
        if (!firstDownEvent[0].contains(firstU) ||
            firstDownEvent[1].rightBound() >= 0.)
          throw std::runtime_error(
              "GUARD first-down image is not U=-.05 with P<0");
        const interval firstV = intersectOrThrow(
            firstDownEvent[2],
            zeroEnergyV(firstU, firstDownEvent[1], firstDownEvent[3]),
            "first-down");

        // Segment 0: x=-U grows from .05 to .4.  Every accepted CAPD step
        // is checked for P<0, so this is the first arrival at U=-.4 and no
        // pole section U=-1 can have occurred.
        IVector downInitial(7);
        downInitial[0] = firstDownEvent[1];
        downInitial[1] = firstV;
        downInitial[2] = firstDownEvent[3];
        downInitial[3] = firstDownEvent[4];
        downInitial[4] = firstDownEvent[5];
        downInitial[5] = firstDownEvent[6];
        downInitial[6] = interval(0.);
        C0HOTripletonSet downSet(downInitial);
        downSet.setCurrentTime(interval(1.) / interval(20.));
        guardDownPHull = downInitial[0];
        IMap downField(
            "time:x;par:rc,a2c,epsc;"
            "var:pp,vv,qq,er,ea,ee,clock;"
            "fun:((2*(rc+er)*(a2c+ea)+sqrt(epsc+ee)*(rc+er)^4*"
            "(a2c+ea)^2)*x+vv+(1+sqrt(epsc+ee)*(rc+er)^3*"
            "(a2c+ea))*x^2+(sqrt(epsc+ee)/3)*(rc+er)^2*x^3)/pp,"
            "-qq/pp,x/pp,0,0,0,-1/pp;");
        downField.setParameter("rc", parameterCentre[0]);
        downField.setParameter("a2c", parameterCentre[1]);
        downField.setParameter("epsc", parameterCentre[2]);
        IOdeSolver downSolver(downField, 20);
        configure(downSolver, .005);
        ITimeMap downMap(downSolver);
        downMap.stopAfterStep(true);
        IVector downEvent(7);
        const interval downTargetX = interval(2.) / interval(5.);
        do {
          downEvent = downMap(downTargetX, downSet);
          const interval stepP = downSet.getLastEnclosure()[0];
          guardDownPHull = intervalHull(guardDownPHull, stepP);
          ++guardSegmentSteps[0];
          if (stepP.rightBound() >= 0.)
            throw std::runtime_error(
                "GUARD x=.05->.4 passage lost P<0");
        } while (!downMap.completed());
        guardSegmentClocks[0] = downEvent[6];
        const interval downU = -downTargetX;
        const interval downF = acceleration(downU, downEvent[1]);
        if (downF.leftBound() <= 0.)
          throw std::runtime_error("GUARD U=-.4 does not have F>0");

        // Segment 1: use P itself as time until P=0.  F>0 on every
        // accepted step makes this the first minimum; U>-1 is checked on
        // the complete dense enclosures, not only at the endpoint.
        const interval downV = intersectOrThrow(
            downEvent[1], zeroEnergyV(downU, downEvent[0], downEvent[2]),
            "U=-.4");
        IVector minInitial(7);
        minInitial[0] = downU;
        minInitial[1] = downV;
        minInitial[2] = downEvent[2];
        minInitial[3] = downEvent[3];
        minInitial[4] = downEvent[4];
        minInitial[5] = downEvent[5];
        minInitial[6] = interval(0.);
        C0HOTripletonSet minSet(minInitial);
        minSet.setCurrentTime(downEvent[0]);
        guardMinApproachFHull = downF;
        guardMinApproachUHull = downU;
        IMap positivePField(
            "time:pp;par:rc,a2c,epsc;"
            "var:uu,vv,qq,er,ea,ee,clock;"
            "fun:pp/((2*(rc+er)*(a2c+ea)+sqrt(epsc+ee)*(rc+er)^4*"
            "(a2c+ea)^2)*uu-vv-(1+sqrt(epsc+ee)*(rc+er)^3*"
            "(a2c+ea))*uu^2+(sqrt(epsc+ee)/3)*(rc+er)^2*uu^3),"
            "qq/((2*(rc+er)*(a2c+ea)+sqrt(epsc+ee)*(rc+er)^4*"
            "(a2c+ea)^2)*uu-vv-(1+sqrt(epsc+ee)*(rc+er)^3*"
            "(a2c+ea))*uu^2+(sqrt(epsc+ee)/3)*(rc+er)^2*uu^3),"
            "uu/((2*(rc+er)*(a2c+ea)+sqrt(epsc+ee)*(rc+er)^4*"
            "(a2c+ea)^2)*uu-vv-(1+sqrt(epsc+ee)*(rc+er)^3*"
            "(a2c+ea))*uu^2+(sqrt(epsc+ee)/3)*(rc+er)^2*uu^3),"
            "0,0,0,1/((2*(rc+er)*(a2c+ea)+sqrt(epsc+ee)*(rc+er)^4*"
            "(a2c+ea)^2)*uu-vv-(1+sqrt(epsc+ee)*(rc+er)^3*"
            "(a2c+ea))*uu^2+(sqrt(epsc+ee)/3)*(rc+er)^2*uu^3);");
        positivePField.setParameter("rc", parameterCentre[0]);
        positivePField.setParameter("a2c", parameterCentre[1]);
        positivePField.setParameter("epsc", parameterCentre[2]);
        IOdeSolver minSolver(positivePField, 20);
        configure(minSolver, .005);
        ITimeMap minMap(minSolver);
        minMap.stopAfterStep(true);
        IVector minimum(7);
        do {
          minimum = minMap(interval(0.), minSet);
          const IVector dense = minSet.getLastEnclosure();
          const interval denseF = acceleration(dense[0], dense[1]);
          guardMinApproachFHull = intervalHull(
              guardMinApproachFHull, denseF);
          guardMinApproachUHull = intervalHull(
              guardMinApproachUHull, dense[0]);
          ++guardSegmentSteps[1];
          if (denseF.leftBound() <= 0. || dense[0].leftBound() <= -1.)
            throw std::runtime_error(
                "GUARD P->0 minimum passage lost F>0 or U>-1");
        } while (!minMap.completed());
        guardSegmentClocks[1] = minimum[6];
        guardMinimumU = minimum[0];
        const interval minimumV = intersectOrThrow(
            minimum[1], zeroEnergyV(minimum[0], interval(0.), minimum[2]),
            "minimum");
        guardMinimumAcceleration = acceleration(minimum[0], minimumV);

        // Segment 2: leave the minimum on the fixed P=.1 section while F>0.
        IVector minExitInitial(7);
        minExitInitial[0] = minimum[0];
        minExitInitial[1] = minimumV;
        minExitInitial[2] = minimum[2];
        minExitInitial[3] = minimum[3];
        minExitInitial[4] = minimum[4];
        minExitInitial[5] = minimum[5];
        minExitInitial[6] = interval(0.);
        C0HOTripletonSet minExitSet(minExitInitial);
        minExitSet.setCurrentTime(interval(0.));
        guardMinExitFHull = guardMinimumAcceleration;
        IOdeSolver minExitSolver(positivePField, 20);
        configure(minExitSolver, .005);
        ITimeMap minExitMap(minExitSolver);
        minExitMap.stopAfterStep(true);
        IVector minExit(7);
        const interval smallP = interval(1.) / interval(10.);
        do {
          minExit = minExitMap(smallP, minExitSet);
          const IVector dense = minExitSet.getLastEnclosure();
          const interval denseF = acceleration(dense[0], dense[1]);
          guardMinExitFHull = intervalHull(guardMinExitFHull, denseF);
          ++guardSegmentSteps[2];
          if (denseF.leftBound() <= 0.)
            throw std::runtime_error(
                "GUARD minimum exit lost F>0");
        } while (!minExitMap.completed());
        guardSegmentClocks[2] = minExit[6];

        // Segment 3: U is the independent variable up to U=11/5.  Dense
        // P>0 proves that no second turning point occurred on this passage.
        IVector riseInitial(7);
        riseInitial[0] = smallP;
        riseInitial[1] = minExit[1];
        riseInitial[2] = minExit[2];
        riseInitial[3] = minExit[3];
        riseInitial[4] = minExit[4];
        riseInitial[5] = minExit[5];
        riseInitial[6] = interval(0.);
        C0HOTripletonSet riseSet(riseInitial);
        riseSet.setCurrentTime(minExit[0]);
        guardRisePHull = smallP;
        IMap riseField(
            "time:uu;par:rc,a2c,epsc;"
            "var:pp,vv,qq,er,ea,ee,clock;"
            "fun:((2*(rc+er)*(a2c+ea)+sqrt(epsc+ee)*(rc+er)^4*"
            "(a2c+ea)^2)*uu-vv-(1+sqrt(epsc+ee)*(rc+er)^3*"
            "(a2c+ea))*uu^2+(sqrt(epsc+ee)/3)*(rc+er)^2*uu^3)/pp,"
            "qq/pp,uu/pp,0,0,0,1/pp;");
        riseField.setParameter("rc", parameterCentre[0]);
        riseField.setParameter("a2c", parameterCentre[1]);
        riseField.setParameter("epsc", parameterCentre[2]);
        IOdeSolver riseSolver(riseField, 20);
        configure(riseSolver, .01);
        ITimeMap riseMap(riseSolver);
        riseMap.stopAfterStep(true);
        IVector rise(7);
        const interval riseTargetU = interval(11.) / interval(5.);
        do {
          rise = riseMap(riseTargetU, riseSet);
          const interval denseP = riseSet.getLastEnclosure()[0];
          guardRisePHull = intervalHull(guardRisePHull, denseP);
          ++guardSegmentSteps[3];
          if (denseP.leftBound() <= 0.)
            throw std::runtime_error(
                "GUARD U->2.2 passage lost P>0");
        } while (!riseMap.completed());
        guardSegmentClocks[3] = rise[6];
        const interval riseF = acceleration(riseTargetU, rise[1]);
        if (riseF.rightBound() >= 0.)
          throw std::runtime_error("GUARD U=2.2 does not have F<0");

        // Segments 4 and 5 use m=-P, which increases first to the maximum
        // (m=0) and then to P=-.1.  F<0 on every accepted enclosure makes
        // the maximum the first one after the minimum.
        IMap negativePField(
            "time:mm;par:rc,a2c,epsc;"
            "var:uu,vv,qq,er,ea,ee,clock;"
            "fun:mm/((2*(rc+er)*(a2c+ea)+sqrt(epsc+ee)*(rc+er)^4*"
            "(a2c+ea)^2)*uu-vv-(1+sqrt(epsc+ee)*(rc+er)^3*"
            "(a2c+ea))*uu^2+(sqrt(epsc+ee)/3)*(rc+er)^2*uu^3),"
            "-qq/((2*(rc+er)*(a2c+ea)+sqrt(epsc+ee)*(rc+er)^4*"
            "(a2c+ea)^2)*uu-vv-(1+sqrt(epsc+ee)*(rc+er)^3*"
            "(a2c+ea))*uu^2+(sqrt(epsc+ee)/3)*(rc+er)^2*uu^3),"
            "-uu/((2*(rc+er)*(a2c+ea)+sqrt(epsc+ee)*(rc+er)^4*"
            "(a2c+ea)^2)*uu-vv-(1+sqrt(epsc+ee)*(rc+er)^3*"
            "(a2c+ea))*uu^2+(sqrt(epsc+ee)/3)*(rc+er)^2*uu^3),"
            "0,0,0,-1/((2*(rc+er)*(a2c+ea)+sqrt(epsc+ee)*(rc+er)^4*"
            "(a2c+ea)^2)*uu-vv-(1+sqrt(epsc+ee)*(rc+er)^3*"
            "(a2c+ea))*uu^2+(sqrt(epsc+ee)/3)*(rc+er)^2*uu^3);");
        negativePField.setParameter("rc", parameterCentre[0]);
        negativePField.setParameter("a2c", parameterCentre[1]);
        negativePField.setParameter("epsc", parameterCentre[2]);
        IVector maxInitial(7);
        maxInitial[0] = riseTargetU;
        maxInitial[1] = rise[1];
        maxInitial[2] = rise[2];
        maxInitial[3] = rise[3];
        maxInitial[4] = rise[4];
        maxInitial[5] = rise[5];
        maxInitial[6] = interval(0.);
        C0HOTripletonSet maxSet(maxInitial);
        maxSet.setCurrentTime(-rise[0]);
        guardMaxApproachFHull = riseF;
        guardMaxApproachUHull = riseTargetU;
        IOdeSolver maxSolver(negativePField, 20);
        configure(maxSolver, .005);
        ITimeMap maxMap(maxSolver);
        maxMap.stopAfterStep(true);
        IVector maximum(7);
        do {
          maximum = maxMap(interval(0.), maxSet);
          const IVector dense = maxSet.getLastEnclosure();
          const interval denseF = acceleration(dense[0], dense[1]);
          guardMaxApproachFHull = intervalHull(
              guardMaxApproachFHull, denseF);
          guardMaxApproachUHull = intervalHull(
              guardMaxApproachUHull, dense[0]);
          ++guardSegmentSteps[4];
          if (denseF.rightBound() >= 0. || dense[0].leftBound() <= 0.)
            throw std::runtime_error(
                "GUARD m->0 maximum passage lost F<0 or U>0");
        } while (!maxMap.completed());
        guardSegmentClocks[4] = maximum[6];
        guardMaximumU = maximum[0];
        const interval maximumV = intersectOrThrow(
            maximum[1], zeroEnergyV(maximum[0], interval(0.), maximum[2]),
            "maximum");
        guardMaximumAcceleration = acceleration(maximum[0], maximumV);

        IVector maxExitInitial(7);
        maxExitInitial[0] = maximum[0];
        maxExitInitial[1] = maximumV;
        maxExitInitial[2] = maximum[2];
        maxExitInitial[3] = maximum[3];
        maxExitInitial[4] = maximum[4];
        maxExitInitial[5] = maximum[5];
        maxExitInitial[6] = interval(0.);
        C0HOTripletonSet maxExitSet(maxExitInitial);
        maxExitSet.setCurrentTime(interval(0.));
        guardMaxExitFHull = guardMaximumAcceleration;
        IOdeSolver maxExitSolver(negativePField, 20);
        configure(maxExitSolver, .005);
        ITimeMap maxExitMap(maxExitSolver);
        maxExitMap.stopAfterStep(true);
        IVector maxExit(7);
        do {
          maxExit = maxExitMap(smallP, maxExitSet);
          const IVector dense = maxExitSet.getLastEnclosure();
          const interval denseF = acceleration(dense[0], dense[1]);
          guardMaxExitFHull = intervalHull(guardMaxExitFHull, denseF);
          ++guardSegmentSteps[5];
          if (denseF.rightBound() >= 0.)
            throw std::runtime_error("GUARD maximum exit lost F<0");
        } while (!maxExitMap.completed());
        guardSegmentClocks[5] = maxExit[6];

        // Segment 6: recondition V on H=0 at the strict P=-.1 exit, where
        // U>0 keeps the Hamiltonian formula regular.  Then advance in the
        // increasing coordinate x=-U from the positive-U side to x=0.
        // Dense P<0 proves that this is the first post-maximum U=0 arrival.
        const interval maxExitV = intersectOrThrow(
            maxExit[1], zeroEnergyV(maxExit[0], -smallP, maxExit[2]),
            "post-maximum P=-.1");
        IVector zeroInitial(7);
        zeroInitial[0] = -smallP;
        zeroInitial[1] = maxExitV;
        zeroInitial[2] = maxExit[2];
        zeroInitial[3] = maxExit[3];
        zeroInitial[4] = maxExit[4];
        zeroInitial[5] = maxExit[5];
        zeroInitial[6] = interval(0.);
        C0HOTripletonSet zeroSet(zeroInitial);
        zeroSet.setCurrentTime(-maxExit[0]);
        guardPostMaxZeroPHull = zeroInitial[0];
        IOdeSolver zeroSolver(downField, 20);
        configure(zeroSolver, .01);
        ITimeMap zeroMap(zeroSolver);
        zeroMap.stopAfterStep(true);
        IVector zeroEvent(7);
        do {
          zeroEvent = zeroMap(interval(0.), zeroSet);
          const interval denseP = zeroSet.getLastEnclosure()[0];
          guardPostMaxZeroPHull = intervalHull(
              guardPostMaxZeroPHull, denseP);
          ++guardSegmentSteps[6];
          if (denseP.rightBound() >= 0.)
            throw std::runtime_error(
                "GUARD post-maximum x=-U passage to zero lost P<0");
        } while (!zeroMap.completed());
        guardSegmentClocks[6] = zeroEvent[6];
        guardZeroP = zeroEvent[0];
        guardZeroQ = zeroEvent[2];
        if (guardSegmentClocks[6].leftBound() <= 0. ||
            guardZeroP.rightBound() >= 0. ||
            guardZeroQ.leftBound() <= 0.)
          throw std::runtime_error(
              "GUARD U=0 image lost P<0 or Q>0");

        // On H=0 at U=0, P^2=Q^2.  The strict signs select P=-Q.
        // Intersecting the two physical hulls and discarding the remaining
        // correlations is a rigorous superset reconditioning.
        if (!intersection(guardZeroQ, -guardZeroP, guardZeroBranchQ))
          throw std::runtime_error(
              "GUARD U=0 H=0 P=-Q intersection is empty");
        if (guardZeroBranchQ.leftBound() <= 0.)
          throw std::runtime_error("GUARD U=0 branch lost Q>0");

        // Segment 7: continue in x=-U from zero to x=1/5.  Dense P<0 makes
        // this the first U=-1/5 hit after the maximum and excludes every
        // earlier U=-10 gate.
        IVector escapeInitial(7);
        escapeInitial[0] = -guardZeroBranchQ;
        escapeInitial[1] = zeroEvent[1];
        escapeInitial[2] = guardZeroBranchQ;
        escapeInitial[3] = zeroEvent[3];
        escapeInitial[4] = zeroEvent[4];
        escapeInitial[5] = zeroEvent[5];
        escapeInitial[6] = interval(0.);
        C0HOTripletonSet escapeSet(escapeInitial);
        escapeSet.setCurrentTime(interval(0.));
        guardEscapeXPHull = escapeInitial[0];
        IOdeSolver escapeSolver(downField, 20);
        configure(escapeSolver, .005);
        ITimeMap escapeMap(escapeSolver);
        escapeMap.stopAfterStep(true);
        IVector guardedEscape(7);
        const interval escapeX = interval(1.) / interval(5.);
        do {
          guardedEscape = escapeMap(escapeX, escapeSet);
          const interval denseP = escapeSet.getLastEnclosure()[0];
          guardEscapeXPHull = intervalHull(guardEscapeXPHull, denseP);
          ++guardSegmentSteps[7];
          if (denseP.rightBound() >= 0.)
            throw std::runtime_error(
                "GUARD x->.2 escape passage lost P<0");
        } while (!escapeMap.completed());
        guardSegmentClocks[7] = guardedEscape[6];
        guardFinalP = guardedEscape[0];
        guardFinalV = guardedEscape[1];
        guardFinalQ = guardedEscape[2];
        guardEscapeResidual = interval(0.);

        guardMinimumTime = firstDownTime + guardSegmentClocks[0] +
            guardSegmentClocks[1];
        guardMaximumTime = guardMinimumTime + guardSegmentClocks[2] +
            guardSegmentClocks[3] + guardSegmentClocks[4];
        guardEscapeTime = guardMaximumTime + guardSegmentClocks[5] +
            guardSegmentClocks[6] + guardSegmentClocks[7];
        guardMonotonePassed = true;
        for (std::size_t segment = 0; segment < guardSegmentClocks.size();
             ++segment) {
          guardMonotonePassed = guardMonotonePassed &&
              guardSegmentClocks[segment].leftBound() > 0. &&
              guardSegmentSteps[segment] > 0;
        }
        guardMonotonePassed = guardMonotonePassed &&
            guardDownPHull.rightBound() < 0. &&
            guardMinApproachFHull.leftBound() > 0. &&
            guardMinApproachUHull.leftBound() > -1. &&
            guardMinExitFHull.leftBound() > 0. &&
            guardRisePHull.leftBound() > 0. &&
            guardMaxApproachFHull.rightBound() < 0. &&
            guardMaxApproachUHull.leftBound() > 0. &&
            guardMaxExitFHull.rightBound() < 0. &&
            guardPostMaxZeroPHull.rightBound() < 0. &&
            guardZeroP.rightBound() < 0. &&
            guardZeroQ.leftBound() > 0. &&
            guardZeroBranchQ.leftBound() > 0. &&
            guardEscapeXPHull.rightBound() < 0.;
      }
      preEscapeGuardPassed = guardMinimumU.leftBound() > -1. &&
          guardMinimumAcceleration.leftBound() > 0. &&
          guardMaximumU.leftBound() > 0. &&
          guardMaximumAcceleration.rightBound() < 0. &&
          guardFinalP.rightBound() < 0. &&
          guardEscapeResidual.contains(0.) &&
          guardMinimumTime.leftBound() > 0. &&
          guardMaximumTime.leftBound() > guardMinimumTime.rightBound() &&
          guardEscapeTime.leftBound() > guardMaximumTime.rightBound() &&
          returnTime.leftBound() > guardEscapeTime.rightBound() &&
          (!guardMonotoneApplicable || guardMonotonePassed);

      // Evaluate the invariant cone on the guard's first U=-1/5 image, not
      // on the separately propagated numerical route.  This joins the
      // no-earlier-hit argument and the escape argument pointwise.
      const interval escapeX = interval(1.) / interval(5.);
      escapeY = -guardFinalP;
      escapeD = sqr(escapeX) / interval(2.) + guardFinalV;
      escapeK = escapeX * escapeY + guardFinalQ;
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
                        algFiniteReducedPassed &&
                        turnReducedPassed && escapeReducedPassed &&
                        firstDownEntryPassed;

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
              << ",\"pole_first_down_entry\":{\"applicable\":"
              << (selected.id == "POLE" ? "true" : "false")
              << ",\"passed\":"
              << (firstDownEntryPassed ? "true" : "false")
              << ",\"method\":\"" << firstDownEntryMethod << "\""
              << ",\"fallback_triggered\":"
              << (firstDownFallbackTriggered ? "true" : "false")
              << ",\"target_U\":"
              << intervalString(-interval(1.) / interval(20.))
              << ",\"anchor_U\":"
              << intervalString(interval(1.) / interval(1000.))
              << ",\"anchor_time\":"
              << intervalString(firstDownAnchorTime)
              << ",\"anchor_section_residual\":"
              << intervalString(firstDownAnchorResidual)
              << ",\"anchor_P\":" << intervalString(firstDownAnchorP)
              << ",\"pre_zero_clock\":"
              << intervalString(firstDownPreZeroClock)
              << ",\"pre_zero_dense_P_hull\":"
              << intervalString(firstDownPreZeroPHull)
              << ",\"pre_zero_step_count\":"
              << firstDownPreZeroSteps
              << ",\"zero_time\":"
              << intervalString(firstDownZeroTime)
              << ",\"zero_P\":" << intervalString(firstDownZeroP)
              << ",\"zero_Q\":" << intervalString(firstDownZeroQ)
              << ",\"zero_branch_Q\":"
              << intervalString(firstDownZeroBranchQ)
              << ",\"h0_branch_identity_kind\":\""
              << (firstDownFallbackTriggered
                      ? "U_ZERO_P_EQUALS_MINUS_Q_BY_H0_AND_SIGNS"
                      : "NOT_APPLICABLE")
              << "\""
              << ",\"post_zero_clock\":"
              << intervalString(firstDownPostZeroClock)
              << ",\"post_zero_dense_P_hull\":"
              << intervalString(firstDownPostZeroPHull)
              << ",\"post_zero_step_count\":"
              << firstDownPostZeroSteps
              << ",\"first_down_time\":"
              << intervalString(firstDownTime)
              << ",\"first_down_section_residual\":"
              << intervalString(
                     firstDownEvent[0] + interval(1.) / interval(20.))
              << ",\"first_down_P\":"
              << intervalString(firstDownEvent[1]) << "}"
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
              << intervalString(guardEscapeResidual)
              << ",\"method\":\"" << guardMethod << "\""
              << ",\"monotone_passages\":{\"applicable\":"
              << (guardMonotoneApplicable ? "true" : "false")
              << ",\"passed\":"
              << (guardMonotonePassed ? "true" : "false")
              << ",\"labels\":[";
    for (std::size_t segment = 0; segment < guardSegmentLabels.size();
         ++segment) {
      if (segment) std::cout << ',';
      std::cout << '\"' << guardSegmentLabels[segment] << '\"';
    }
    std::cout << "]"
              << ",\"clocks\":[";
    for (std::size_t segment = 0; segment < guardSegmentClocks.size();
         ++segment) {
      if (segment) std::cout << ',';
      std::cout << intervalString(guardSegmentClocks[segment]);
    }
    std::cout << "]"
              << ",\"step_counts\":[";
    for (std::size_t segment = 0; segment < guardSegmentSteps.size();
         ++segment) {
      if (segment) std::cout << ',';
      std::cout << guardSegmentSteps[segment];
    }
    std::cout << "]"
              << ",\"dense_sign_hulls\":{"
              << "\"down_P\":" << intervalString(guardDownPHull)
              << ",\"minimum_approach_F\":"
              << intervalString(guardMinApproachFHull)
              << ",\"minimum_approach_U\":"
              << intervalString(guardMinApproachUHull)
              << ",\"minimum_exit_F\":"
              << intervalString(guardMinExitFHull)
              << ",\"rise_P\":" << intervalString(guardRisePHull)
              << ",\"maximum_approach_F\":"
              << intervalString(guardMaxApproachFHull)
              << ",\"maximum_approach_U\":"
              << intervalString(guardMaxApproachUHull)
              << ",\"maximum_exit_F\":"
              << intervalString(guardMaxExitFHull)
              << ",\"post_max_to_zero_P\":"
              << intervalString(guardPostMaxZeroPHull)
              << ",\"zero_P\":" << intervalString(guardZeroP)
              << ",\"zero_Q\":" << intervalString(guardZeroQ)
              << ",\"zero_branch_Q\":"
              << intervalString(guardZeroBranchQ)
              << ",\"escape_x_P\":"
              << intervalString(guardEscapeXPHull)
              << "}}}"
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
              << ",\"seam_time\":" << intervalString(turnSeamTime)
              << ",\"terminal_U\":"
              << intervalString(interval(11.) / interval(4.))
              << ",\"terminal_time\":"
              << intervalString(turnTerminalTime)
              << ",\"clock\":" << intervalString(turnClock)
              << ",\"dense_step_count\":" << turnDenseSteps
              << ",\"dense_P_hull\":" << intervalString(turnDensePHull)
              << "}"
              << ",\"pole_escape_reduced_passage\":{\"applicable\":"
              << (escapeReducedApplicable ? "true" : "false")
              << ",\"passed\":"
              << (escapeReducedPassed ? "true" : "false")
              << ",\"method\":"
                 "\"PMAX_H0_M_TO_U_ZERO_H0_BRANCH_X_TO_ONE_FIFTH\""
              << ",\"seam_P\":" << intervalString(interval(0.))
              << ",\"seam_time\":" << intervalString(escapeSeamTime)
              << ",\"pmax_U\":" << intervalString(escapePmaxU)
              << ",\"pmax_V_H0\":" << intervalString(escapePmaxV)
              << ",\"pmax_Q\":" << intervalString(escapePmaxQ)
              << ",\"pmax_F\":" << intervalString(escapePmaxF)
              << ",\"m_terminal\":"
              << intervalString(interval(1.) / interval(10.))
              << ",\"m_clock\":" << intervalString(escapeMClock)
              << ",\"m_dense_step_count\":" << escapeMDenseSteps
              << ",\"m_dense_F_hull\":"
              << intervalString(escapeMDenseFHull)
              << ",\"U_terminal\":" << intervalString(interval(0.))
              << ",\"U_clock\":" << intervalString(escapeUClock)
              << ",\"U_dense_step_count\":" << escapeUDenseSteps
              << ",\"U_dense_P_hull\":"
              << intervalString(escapeUDensePHull)
              << ",\"zero_P\":" << intervalString(escapeZeroP)
              << ",\"zero_Q\":" << intervalString(escapeZeroQ)
              << ",\"zero_H0_branch_Q\":"
              << intervalString(escapeZeroBranchQ)
              << ",\"zero_H0_branch_identity\":"
                 "\"P_EQUALS_MINUS_Q_BY_H0_AND_STRICT_SIGNS\""
              << ",\"terminal_x\":"
              << intervalString(interval(1.) / interval(5.))
              << ",\"terminal_time\":"
              << intervalString(escapeTerminalTime)
              << ",\"x_clock\":" << intervalString(escapeXClock)
              << ",\"x_dense_step_count\":" << escapeXDenseSteps
              << ",\"x_dense_P_hull\":"
              << intervalString(escapeXDensePHull)
              << "}"
              << ",\"alg_finite_zero_energy_passage\":{\"applicable\":"
              << (algFiniteReducedApplicable ? "true" : "false")
              << ",\"passed\":"
              << (algFiniteReducedPassed ? "true" : "false")
              << ",\"method\":\"U_MINUS_ONE_TWENTIETH_H0_WQ_X_TIME\""
              << ",\"seam_x\":"
              << intervalString(interval(1.) / interval(20.))
              << ",\"seam_time\":" << intervalString(algFiniteSeamTime)
              << ",\"seam_P\":" << intervalString(algFiniteSeamP)
              << ",\"seam_V_H0_intersection\":"
              << intervalString(algFiniteSeamV)
              << ",\"seam_energy_diagnostic\":"
              << intervalString(algFiniteSeamEnergy)
              << ",\"clock\":" << intervalString(algFiniteClock)
              << ",\"dense_step_count\":" << algFiniteDenseSteps
              << ",\"dense_w_hull\":"
              << intervalString(algFiniteDenseWHull)
              << ",\"x_nodes\":[";
    for (std::size_t index = 0; index < algFiniteX.size(); ++index) {
      if (index) std::cout << ',';
      std::cout << intervalString(algFiniteX[index]);
    }
    std::cout << "]"
              << ",\"clock_nodes\":[";
    for (std::size_t index = 0; index < algFiniteClocks.size(); ++index) {
      if (index) std::cout << ',';
      std::cout << intervalString(algFiniteClocks[index]);
    }
    std::cout << "]"
              << ",\"w_nodes\":[";
    for (std::size_t index = 0; index < algFiniteW.size(); ++index) {
      if (index) std::cout << ',';
      std::cout << intervalString(algFiniteW[index]);
    }
    std::cout << "]"
              << ",\"q_nodes\":[";
    for (std::size_t index = 0; index < algFiniteQ.size(); ++index) {
      if (index) std::cout << ',';
      std::cout << intervalString(algFiniteQ[index]);
    }
    std::cout << "]"
              << ",\"energy_reconstruction_identity\":"
              << (algFiniteReducedApplicable ? "true" : "false")
              << ",\"energy_reconstruction_identity_kind\":"
                 "\"BY_EXACT_SOURCE_HAMILTONIAN_CONSERVATION\""
              << ",\"terminal_energy_diagnostic\":"
              << intervalString(algFiniteTerminalEnergy) << "}"
              << ",\"alg_reduced_zero_energy_tail\":{\"applicable\":"
              << (algReducedApplicable ? "true" : "false")
              << ",\"passed\":" << (algReducedPassed ? "true" : "false")
              << ",\"seam_time\":" << intervalString(algSeamTime)
              << ",\"seam_P\":" << intervalString(algSeamP)
              << ",\"seam_Q\":" << intervalString(algSeamQ)
              << ",\"tail_clock\":" << intervalString(algTailClock)
              << ",\"dense_step_count\":" << algDenseSteps
              << ",\"dense_w_hull\":" << intervalString(algDenseWHull)
              << ",\"coordinate_kind\":"
                 "\"W_Q_WITH_REDUNDANT_CANCELLATION_D\""
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
              << ",\"d_nodes\":[";
    for (std::size_t index = 0; index < algReducedD.size(); ++index) {
      if (index) std::cout << ',';
      std::cout << intervalString(algReducedD[index]);
    }
    std::cout << "]"
              << ",\"cancellation_residuals\":[";
    for (std::size_t index = 0;
         index < algReducedCancellationResiduals.size(); ++index) {
      if (index) std::cout << ',';
      std::cout << intervalString(algReducedCancellationResiduals[index]);
    }
    std::cout << "]"
              << ",\"cancellation_reconditioned_at_every_tau_node\":"
              << (algReducedApplicable ? "true" : "false")
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
