#include "interval_io.hpp"
#include "rounding_self_test.hpp"
#include "verdict.hpp"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
#include <exception>
#include <iostream>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

namespace {

using rfsn::rigorous::Interval;
using rfsn::rigorous::Verdict;
using rfsn::rigorous::combine;
using rfsn::rigorous::intervalJson;
using rfsn::rigorous::verdictName;

constexpr std::size_t kStateDimension = 4;
using Gradient = std::array<Interval, kStateDimension>;

Interval rational(long numerator, long denominator = 1) {
  return rfsn::rigorous::exactRational(
      std::to_string(numerator), std::to_string(denominator));
}

Interval intervalFromRationals(long lowerNumerator, long lowerDenominator,
                               long upperNumerator, long upperDenominator) {
  const Interval lower = rational(lowerNumerator, lowerDenominator);
  const Interval upper = rational(upperNumerator, upperDenominator);
  return Interval(lower.leftBound(), upper.rightBound());
}

struct Dual {
  Interval value;
  Gradient derivative{};

  Dual() : value(0.0) {
    for (auto& entry : derivative) entry = Interval(0.0);
  }

  explicit Dual(const Interval& initial) : value(initial) {
    for (auto& entry : derivative) entry = Interval(0.0);
  }

  static Dual variable(const Interval& initial, std::size_t index) {
    Dual result(initial);
    result.derivative.at(index) = Interval(1.0);
    return result;
  }
};

Dual operator+(const Dual& left, const Dual& right) {
  Dual result(left.value + right.value);
  for (std::size_t index = 0; index < kStateDimension; ++index)
    result.derivative[index] =
        left.derivative[index] + right.derivative[index];
  return result;
}

Dual operator-(const Dual& left, const Dual& right) {
  Dual result(left.value - right.value);
  for (std::size_t index = 0; index < kStateDimension; ++index)
    result.derivative[index] =
        left.derivative[index] - right.derivative[index];
  return result;
}

Dual operator-(const Dual& value) {
  Dual result(-value.value);
  for (std::size_t index = 0; index < kStateDimension; ++index)
    result.derivative[index] = -value.derivative[index];
  return result;
}

Dual operator*(const Dual& left, const Dual& right) {
  Dual result(left.value * right.value);
  for (std::size_t index = 0; index < kStateDimension; ++index) {
    result.derivative[index] =
        left.derivative[index] * right.value
        + left.value * right.derivative[index];
  }
  return result;
}

Dual reciprocal(const Dual& value) {
  if (value.value.contains(0.0))
    throw std::runtime_error("dual reciprocal denominator contains zero");
  Dual result(Interval(1.0) / value.value);
  const Interval denominator = sqr(value.value);
  for (std::size_t index = 0; index < kStateDimension; ++index)
    result.derivative[index] = -value.derivative[index] / denominator;
  return result;
}

Dual operator/(const Dual& left, const Dual& right) {
  return left * reciprocal(right);
}

Dual sqrtDual(const Dual& value) {
  if (value.value.leftBound() <= 0.0)
    throw std::runtime_error("dual square-root argument is not positive");
  const Interval root = sqrt(value.value);
  Dual result(root);
  const Interval denominator = Interval(2.0) * root;
  for (std::size_t index = 0; index < kStateDimension; ++index)
    result.derivative[index] = value.derivative[index] / denominator;
  return result;
}

Dual square(const Dual& value) { return value * value; }
Dual cube(const Dual& value) { return square(value) * value; }
Dual fourth(const Dual& value) { return square(square(value)); }

struct Evaluation {
  Interval quadraticLeading;
  Interval quadraticConstant;
  Interval discriminant;
  Interval negativeRoot;
  Interval chi;
  Interval rootDerivative;
  Interval pi;
  std::array<Interval, kStateDimension> field;
  std::array<Gradient, kStateDimension> jacobian;
};

Evaluation evaluate(const Interval& r, const Interval& a2,
                    const Interval& epsilon, const Interval& zBox,
                    const Interval& energyBox, const Interval& betaBox,
                    const Interval& alphaBox) {
  const Interval delta = sqr(r);
  const Interval a = Interval(1.0) + sqrt(epsilon) * delta * r * a2;
  const Interval primitiveA =
      sqr(sqr(a)) * rational(1, 12) - sqr(a) * rational(1, 2);

  const Dual z = Dual::variable(zBox, 0);
  const Dual energy = Dual::variable(energyBox, 1);
  const Dual beta = Dual::variable(betaBox, 2);
  const Dual alpha = Dual::variable(alphaBox, 3);
  const Dual one(Interval(1.0));
  const Dual two(Interval(2.0));
  const Dual half(rational(1, 2));
  const Dual twoThirds(rational(2, 3));
  const Dual epsilonDual(epsilon);
  const Dual deltaDual(delta);
  const Dual aDual(a);
  const Dual primitiveADual(primitiveA);

  const Dual w = alpha - beta;
  const Dual sum = alpha + beta;
  const Dual z2 = square(z);
  const Dual z3 = z2 * z;
  const Dual z4 = square(z2);

  // Equation (19) with pi=delta*chi+alpha+beta is the quadratic
  // A*chi^2-2*b*chi-D=0.  The displayed formula selects its positive root.
  const Dual leading = one - epsilonDual * square(deltaDual) * z4;
  const Dual linearHalf = epsilonDual * deltaDual * sum * z4;
  const Dual rightWithoutPi =
      epsilonDual * half
      - twoThirds * aDual * epsilonDual * z
      - epsilonDual * (two * w + one) * z2
      + two * aDual * epsilonDual * (w + one) * z3
      + (two * energy + two * epsilonDual * primitiveADual) * z4;
  const Dual constantPositive =
      rightWithoutPi + epsilonDual * square(sum) * z4;
  const Dual discriminant =
      square(linearHalf) + leading * constantPositive;
  const Dual root = sqrtDual(discriminant);
  const Dual negativeRoot = (linearHalf - root) / leading;
  const Dual chi = (linearHalf + root) / leading;
  // Exactly 2*(A*chi_+-b)=2*sqrt(b^2+A*D); use the latter form to avoid
  // interval dependency in the regularity margin.
  const Dual rootDerivative = two * root;
  const Dual pi = deltaDual * chi + sum;

  const Dual common =
      -square(deltaDual) * epsilonDual * (one - aDual * z)
      + two * deltaDual * chi * pi;
  const Dual betaDot =
      -beta + half * z2 * (common + pi + pi * w);
  const Dual alphaDot =
      alpha + half * z2 * (common - pi - pi * w);
  const std::array<Dual, kStateDimension> field = {
      -pi * z3, Dual(Interval(0.0)), betaDot, alphaDot};

  Evaluation result;
  result.quadraticLeading = leading.value;
  result.quadraticConstant = constantPositive.value;
  result.discriminant = discriminant.value;
  result.negativeRoot = negativeRoot.value;
  result.chi = chi.value;
  result.rootDerivative = rootDerivative.value;
  result.pi = pi.value;
  for (std::size_t row = 0; row < kStateDimension; ++row) {
    result.field[row] = field[row].value;
    result.jacobian[row] = field[row].derivative;
  }
  return result;
}

double absoluteUpper(const Interval& value) {
  return value.abs().rightBound();
}

Interval scalarUpper(double value) { return Interval(value); }

double mu2GershgorinUpper(
    const std::array<Gradient, kStateDimension>& jacobian) {
  double result = -std::numeric_limits<double>::infinity();
  // The full graph base is X=(z,E,beta).
  constexpr std::array<std::size_t, 3> base = {0, 1, 2};
  for (const std::size_t row : base) {
    Interval bound = jacobian[row][row];
    for (const std::size_t column : base) {
      if (column == row) continue;
      const Interval symmetric =
          (jacobian[row][column] + jacobian[column][row]) * rational(1, 2);
      bound += symmetric.abs();
    }
    result = std::max(result, bound.rightBound());
  }
  return result;
}

double bNormUpper(
    const std::array<Gradient, kStateDimension>& jacobian) {
  Interval sum(0.0);
  for (const std::size_t row :
       {std::size_t(0), std::size_t(1), std::size_t(2)}) {
    const Interval absolute = jacobian[row][3].abs();
    sum += sqr(absolute);
  }
  return sqrt(sum).rightBound();
}

double dNormUpper(
    const std::array<Gradient, kStateDimension>& jacobian) {
  Interval sum(0.0);
  for (const std::size_t column :
       {std::size_t(0), std::size_t(1), std::size_t(2)}) {
    const Interval absolute = jacobian[3][column].abs();
    sum += sqr(absolute);
  }
  return sqrt(sum).rightBound();
}

struct Aggregate {
  bool initialized = false;
  Interval quadraticLeading;
  Interval quadraticConstant;
  Interval discriminant;
  Interval negativeRoot;
  Interval chi;
  Interval rootDerivative;
  Interval pi;
  Interval zZeroField;
  Interval energyField;
  Interval zFaceMargin;
  Interval betaPlusMargin;
  Interval betaMinusMargin;
  Interval alphaPlusMargin;
  Interval alphaMinusMargin;
  double muCUpper = -std::numeric_limits<double>::infinity();
  double bNormUpper = 0.0;
  double dNormUpper = 0.0;
  double aLower = std::numeric_limits<double>::infinity();
  double coneLower = std::numeric_limits<double>::infinity();
  double normalLower = std::numeric_limits<double>::infinity();
  std::array<double, 4> gammaLower = {
      std::numeric_limits<double>::infinity(),
      std::numeric_limits<double>::infinity(),
      std::numeric_limits<double>::infinity(),
      std::numeric_limits<double>::infinity()};
};

Interval hull(const Interval& left, const Interval& right) {
  return Interval(std::min(left.leftBound(), right.leftBound()),
                  std::max(left.rightBound(), right.rightBound()));
}

void includeInterval(bool initialized, Interval& target,
                     const Interval& value) {
  if (!initialized) {
    target = value;
  } else {
    target = hull(target, value);
  }
}

void includeCore(Aggregate& aggregate, const Evaluation& evaluation) {
  const bool wasInitialized = aggregate.initialized;
  includeInterval(wasInitialized, aggregate.quadraticLeading,
                  evaluation.quadraticLeading);
  includeInterval(wasInitialized, aggregate.quadraticConstant,
                  evaluation.quadraticConstant);
  includeInterval(wasInitialized, aggregate.discriminant,
                  evaluation.discriminant);
  includeInterval(wasInitialized, aggregate.negativeRoot,
                  evaluation.negativeRoot);
  includeInterval(wasInitialized, aggregate.chi, evaluation.chi);
  includeInterval(wasInitialized, aggregate.rootDerivative,
                  evaluation.rootDerivative);
  includeInterval(wasInitialized, aggregate.pi, evaluation.pi);

  const double muC = mu2GershgorinUpper(evaluation.jacobian);
  const double bNorm = bNormUpper(evaluation.jacobian);
  const double dNorm = dNormUpper(evaluation.jacobian);
  const double aLower = evaluation.jacobian[3][3].leftBound();
  aggregate.muCUpper = std::max(aggregate.muCUpper, muC);
  aggregate.bNormUpper = std::max(aggregate.bNormUpper, bNorm);
  aggregate.dNormUpper = std::max(aggregate.dNormUpper, dNorm);
  aggregate.aLower = std::min(aggregate.aLower, aLower);

  const Interval cone = Interval(aLower) - Interval(dNorm)
      - Interval(muC) - Interval(bNorm);
  const Interval normal = Interval(aLower) - Interval(bNorm);
  const Interval tangent = Interval(muC) + Interval(bNorm);
  aggregate.coneLower = std::min(
      aggregate.coneLower, cone.leftBound());
  aggregate.normalLower = std::min(
      aggregate.normalLower, normal.leftBound());
  for (std::size_t order = 0; order < aggregate.gammaLower.size(); ++order) {
    const Interval gamma = normal - Interval(static_cast<double>(order)) * tangent;
    aggregate.gammaLower[order] = std::min(
        aggregate.gammaLower[order], gamma.leftBound());
  }
  aggregate.initialized = true;
}

void includeFace(Interval& target, bool& initialized, const Interval& value) {
  includeInterval(initialized, target, value);
  initialized = true;
}

Verdict strictPositive(double lower) {
  if (lower > 0.0) return Verdict::Pass;
  if (lower < 0.0) return Verdict::Fail;
  return Verdict::Inconclusive;
}

Verdict strictPositive(const Interval& value) {
  if (value.leftBound() > 0.0) return Verdict::Pass;
  if (value.rightBound() <= 0.0) return Verdict::Fail;
  return Verdict::Inconclusive;
}

Verdict exactZero(const Interval& value) {
  if (value.leftBound() == 0.0 && value.rightBound() == 0.0)
    return Verdict::Pass;
  if (!value.contains(0.0)) return Verdict::Fail;
  return Verdict::Inconclusive;
}

struct Obligation {
  std::string id;
  Verdict status;
  std::string predicate;
  std::vector<std::pair<std::string, Interval>> enclosures;
};

std::string obligationJson(const Obligation& obligation) {
  std::ostringstream output;
  output << "{\"id\":\"" << rfsn::rigorous::jsonEscape(obligation.id)
         << "\",\"status\":\"" << verdictName(obligation.status)
         << "\",\"predicate\":\""
         << rfsn::rigorous::jsonEscape(obligation.predicate) << "\""
         << ",\"enclosures\":{";
  for (std::size_t index = 0; index < obligation.enclosures.size(); ++index) {
    if (index) output << ',';
    output << '"'
           << rfsn::rigorous::jsonEscape(obligation.enclosures[index].first)
           << "\":" << intervalJson(obligation.enclosures[index].second);
  }
  output << "}}";
  return output.str();
}

}  // namespace

int main() {
  try {
    const auto rounding = rfsn::rigorous::runRoundingSelfTests();
    const Interval energyRadius = rational(1, 1000);
    const Interval energyCorridor(
        -energyRadius.rightBound(), energyRadius.rightBound());
    const Interval radius = rational(1, 100000);
    const Interval stateBox(-radius.rightBound(), radius.rightBound());
    const Interval betaPlus = radius;
    const Interval betaMinus = -radius;
    const Interval alphaPlus = radius;
    const Interval alphaMinus = -radius;
    const Interval zMaximum = rational(2, 9);

    constexpr long kRSlabs = 4;
    constexpr long kA2Slabs = 8;
    constexpr long kEpsilonSlabs = 4;
    constexpr long kEnergySlabs = 2;
    constexpr long kZSlabs = 64;
    Aggregate aggregate;
    bool zFaceInitialized = false;
    bool zZeroInitialized = false;
    bool energyFieldInitialized = false;
    bool betaPlusInitialized = false;
    bool betaMinusInitialized = false;
    bool alphaPlusInitialized = false;
    bool alphaMinusInitialized = false;
    std::size_t cellCount = 0;

    const std::array<std::pair<long, long>, 5> rNodes = {{
        {1, 100}, {1, 80}, {3, 200}, {7, 400}, {1, 50}}};

    for (long rIndex = 0; rIndex < kRSlabs; ++rIndex) {
      const Interval r = intervalFromRationals(
          rNodes[rIndex].first, rNodes[rIndex].second,
          rNodes[rIndex + 1].first, rNodes[rIndex + 1].second);
      for (long a2Index = 0; a2Index < kA2Slabs; ++a2Index) {
        const Interval a2 = intervalFromRationals(
            a2Index - 4, 16, a2Index - 3, 16);
        for (long epsilonIndex = 0; epsilonIndex < kEpsilonSlabs;
             ++epsilonIndex) {
          const Interval epsilon = intervalFromRationals(
              8 + epsilonIndex, 10, 9 + epsilonIndex, 10);
          for (long energyIndex = 0; energyIndex < kEnergySlabs;
               ++energyIndex) {
            const Interval energy = intervalFromRationals(
                energyIndex - 1, 1000, energyIndex, 1000);
            for (long zIndex = 0; zIndex < kZSlabs; ++zIndex) {
              const Interval z = intervalFromRationals(
                  2 * zIndex, 9 * kZSlabs,
                  2 * (zIndex + 1), 9 * kZSlabs);
              const Evaluation core = evaluate(
                  r, a2, epsilon, z, energy, stateBox, stateBox);
              includeCore(aggregate, core);
              includeFace(aggregate.energyField, energyFieldInitialized,
                          core.field[1]);

              const Evaluation betaUpper = evaluate(
                  r, a2, epsilon, z, energy, betaPlus, stateBox);
              includeFace(aggregate.betaPlusMargin, betaPlusInitialized,
                          -betaUpper.field[2]);
              const Evaluation betaLower = evaluate(
                  r, a2, epsilon, z, energy, betaMinus, stateBox);
              includeFace(aggregate.betaMinusMargin, betaMinusInitialized,
                          betaLower.field[2]);
              const Evaluation alphaUpper = evaluate(
                  r, a2, epsilon, z, energy, stateBox, alphaPlus);
              includeFace(aggregate.alphaPlusMargin, alphaPlusInitialized,
                          alphaUpper.field[3]);
              const Evaluation alphaLower = evaluate(
                  r, a2, epsilon, z, energy, stateBox, alphaMinus);
              includeFace(aggregate.alphaMinusMargin, alphaMinusInitialized,
                          -alphaLower.field[3]);
              ++cellCount;
            }

            const Evaluation zFace = evaluate(
                r, a2, epsilon, zMaximum, energy, stateBox, stateBox);
            includeFace(aggregate.zFaceMargin, zFaceInitialized,
                        -zFace.field[0]);
            const Evaluation zZero = evaluate(
                r, a2, epsilon, Interval(0.0), energy, stateBox, stateBox);
            includeFace(
                aggregate.zZeroField, zZeroInitialized, zZero.field[0]);
          }
        }
      }
    }

    const Interval nu = rational(1, 32);
    std::vector<Obligation> obligations;
    obligations.push_back({
        "V4.OUTER_GRAPH.POSITIVE_BRANCH",
        combine(strictPositive(aggregate.quadraticLeading),
                combine(strictPositive(aggregate.quadraticConstant),
                combine(strictPositive(aggregate.discriminant),
                combine(strictPositive(-aggregate.negativeRoot),
                combine(strictPositive(aggregate.chi),
                combine(strictPositive(aggregate.rootDerivative),
                        strictPositive(aggregate.pi))))))),
        "The energy quadratic has one negative and one regular positive chi root, and pi>0, on the full energy collar",
        {{"quadratic_leading", aggregate.quadraticLeading},
         {"quadratic_constant_D", aggregate.quadraticConstant},
         {"quarter_discriminant", aggregate.discriminant},
         {"negative_root", aggregate.negativeRoot},
         {"chi", aggregate.chi},
         {"implicit_chi_derivative", aggregate.rootDerivative},
         {"pi", aggregate.pi}}});
    Verdict faces = exactZero(aggregate.zZeroField);
    faces = combine(faces, exactZero(aggregate.energyField));
    faces = combine(faces, strictPositive(aggregate.zFaceMargin));
    faces = combine(faces, strictPositive(aggregate.betaPlusMargin));
    faces = combine(faces, strictPositive(aggregate.betaMinusMargin));
    faces = combine(faces, strictPositive(aggregate.alphaPlusMargin));
    faces = combine(faces, strictPositive(aggregate.alphaMinusMargin));
    obligations.push_back({
        "V4.OUTER_GRAPH.CORRIDOR_FACES", faces,
        "z=0 and both energy faces are invariant, z=2/9 is inward, beta faces are inward, and alpha faces are strict exits",
        {{"z_dot_at_z_zero", aggregate.zZeroField},
         {"E_dot_on_energy_faces", aggregate.energyField},
         {"minus_z_dot_at_z_max", aggregate.zFaceMargin},
         {"minus_beta_dot_at_beta_plus", aggregate.betaPlusMargin},
         {"beta_dot_at_beta_minus", aggregate.betaMinusMargin},
         {"alpha_dot_at_alpha_plus", aggregate.alphaPlusMargin},
         {"minus_alpha_dot_at_alpha_minus", aggregate.alphaMinusMargin}}});

    const Interval theoremConeFloor =
        Interval(1.0) - Interval(4.0) * nu;
    const Interval theoremNormalFloor =
        Interval(1.0) - Interval(2.0) * nu;
    const Interval theoremGamma3Floor =
        Interval(1.0) - Interval(8.0) * nu;
    const Interval graphSlope = rational(1, 32);
    const double blockMuMargin =
        (nu - Interval(aggregate.muCUpper)).leftBound();
    const double blockBMargin =
        (nu - Interval(aggregate.bNormUpper)).leftBound();
    const double blockDMargin =
        (nu - Interval(aggregate.dNormUpper)).leftBound();
    const double blockAMargin =
        (Interval(aggregate.aLower) - (Interval(1.0) - nu)).leftBound();
    Verdict blocks = strictPositive(blockMuMargin);
    blocks = combine(blocks, strictPositive(blockBMargin));
    blocks = combine(blocks, strictPositive(blockDMargin));
    blocks = combine(blocks, strictPositive(blockAMargin));
    obligations.push_back({
        "V4.OUTER_GRAPH.GENERATOR_BLOCKS", blocks,
        "For the full base X=(z,E,beta), mu2(C), ||B||, ||D|| <= nu=1/32 and a >= 1-nu",
        {{"mu2_C_upper", scalarUpper(aggregate.muCUpper)},
         {"B_norm_upper", scalarUpper(aggregate.bNormUpper)},
         {"D_norm_upper", scalarUpper(aggregate.dNormUpper)},
         {"a_lower", scalarUpper(aggregate.aLower)},
         {"nu_minus_mu2_C", scalarUpper(blockMuMargin)},
         {"nu_minus_B_norm", scalarUpper(blockBMargin)},
         {"nu_minus_D_norm", scalarUpper(blockDMargin)},
         {"a_minus_one_minus_nu", scalarUpper(blockAMargin)}}});

    Verdict rates = strictPositive(aggregate.coneLower);
    rates = combine(rates, strictPositive(aggregate.normalLower));
    for (const double gamma : aggregate.gammaLower)
      rates = combine(rates, strictPositive(gamma));
    obligations.push_back({
        "V4.OUTER_GRAPH.CONE_AND_BUNCHING", rates,
        "The slope-one cone, normal rate, and generator gaps gamma_j for j=0,...,3 are strict",
        {{"slope_one_cone_lower", scalarUpper(aggregate.coneLower)},
         {"normal_rate_lower", scalarUpper(aggregate.normalLower)},
         {"gamma_0_lower", scalarUpper(aggregate.gammaLower[0])},
         {"gamma_1_lower", scalarUpper(aggregate.gammaLower[1])},
         {"gamma_2_lower", scalarUpper(aggregate.gammaLower[2])},
         {"gamma_3_lower", scalarUpper(aggregate.gammaLower[3])},
         {"theorem_cone_floor_1_minus_4nu",
          theoremConeFloor},
         {"theorem_normal_floor_1_minus_2nu",
          theoremNormalFloor},
         {"theorem_gamma3_floor_1_minus_8nu",
          theoremGamma3Floor}}});

    // For a graph with base-to-normal slope kappa, the boundary of the
    // projectivized cone is strictly inward whenever
    //
    //   kappa * (a_n-mu_2(C)-||B||*kappa) - ||D|| > 0.
    //
    // The same full-corridor block extrema used above therefore certify a
    // much narrower cone than the slope-one cone needed for existence.
    const Interval graphSlopeMargin =
        graphSlope *
            (Interval(aggregate.aLower) -
             Interval(aggregate.muCUpper) -
             Interval(aggregate.bNormUpper) * graphSlope) -
        Interval(aggregate.dNormUpper);
    obligations.push_back({
        "V4.OUTER_GRAPH.SLOPE_1_32",
        strictPositive(graphSlopeMargin),
        "The base-to-normal graph slope is at most kappa=1/32 on the full corridor because the kappa projectivized cone is strictly invariant",
        {{"kappa", graphSlope},
         {"kappa_cone_margin", graphSlopeMargin}}});

    Verdict mathematical = Verdict::Pass;
    for (const auto& obligation : obligations)
      mathematical = combine(mathematical, obligation.status);
    const Verdict status = combine(rounding.status, mathematical);

    std::cout
        << "{\"schema_version\":\"rfsn-vdp-v4-outer-graph-probe/2\","
        << "\"status\":\"" << verdictName(status) << "\","
        << "\"mathematical_status\":\"" << verdictName(mathematical)
        << "\",\"claim_bearing\":false,"
        << "\"claim_boundary\":{"
        << "\"parent_obligation\":\"V4.OUTER_GRAPH local mathematical PASS; "
           "Issue #7 aggregate remains PENDING\","
        << "\"proved_scope\":\"unique maximal full-energy future-staying graph "
           "with normal expansion, slope at most 1/32, third-order "
           "bunching, and mixed regularity\","
        << "\"open_scope\":[\"V5 incidence\",\"outer action finite part\","
           "\"Issue #7 aggregate and release\"]},"
        << "\"scope\":\"FULL_ENERGY_COLLAR\","
        << "\"box_id\":\"vdp-positive-box-v2\","
        << "\"parameter_box\":{"
        << "\"r\":"
        << intervalJson(intervalFromRationals(1, 100, 1, 50)) << ','
        << "\"a2\":"
        << intervalJson(intervalFromRationals(-1, 4, 1, 4)) << ','
        << "\"epsilon\":"
        << intervalJson(intervalFromRationals(4, 5, 6, 5)) << "},"
        << "\"rounding_self_test\":"
        << rfsn::rigorous::roundingReportJson(rounding) << ','
        << "\"cover\":{\"r_slabs\":" << kRSlabs
        << ",\"a2_slabs\":" << kA2Slabs
        << ",\"epsilon_slabs\":" << kEpsilonSlabs
        << ",\"energy_slabs\":" << kEnergySlabs
        << ",\"z_slabs\":" << kZSlabs
        << ",\"cell_count\":" << cellCount << "},"
        << "\"corridor\":{"
        << "\"z\":" << intervalJson(Interval(0.0, zMaximum.rightBound()))
        << ",\"E\":" << intervalJson(energyCorridor)
        << ",\"beta\":" << intervalJson(stateBox)
        << ",\"alpha\":" << intervalJson(stateBox)
        << ",\"nu\":" << intervalJson(nu)
        << ",\"graph_slope_kappa\":" << intervalJson(graphSlope) << "},"
        << "\"obligations\":[";
    for (std::size_t index = 0; index < obligations.size(); ++index) {
      if (index) std::cout << ',';
      std::cout << obligationJson(obligations[index]);
    }
    std::cout << "]}\n";
    return status == Verdict::Pass ? 0 : 1;
  } catch (const std::exception& error) {
    std::cerr << "vdp_v4_outer_graph_probe: " << error.what() << '\n';
    return 2;
  }
}
