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

constexpr std::size_t kStateDimension = 3;
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
  Interval lambda;
  Interval chiZero;
  Interval cZero;
  Interval c;
  Interval d;
  Interval quadraticLeading;
  Interval quadraticConstant;
  Interval discriminant;
  Interval negativeRoot;
  Interval chi;
  Interval rootDerivative;
  Interval s;
  Interval pi;
  std::array<Interval, kStateDimension> field;
  std::array<Gradient, kStateDimension> jacobian;
};

Evaluation evaluate(const Interval& r, const Interval& a2,
                    const Interval& epsilon, const Interval& zBox,
                    const Interval& bBox, const Interval& nBox) {
  const Interval delta = sqr(r);
  const Interval a = Interval(1.0) + sqrt(epsilon) * delta * r * a2;
  const Interval primitiveA =
      sqr(sqr(a)) * rational(1, 12) - sqr(a) * rational(1, 2);

  const Dual z = Dual::variable(zBox, 0);
  const Dual b = Dual::variable(bBox, 1);
  const Dual n = Dual::variable(nBox, 2);
  const Dual one(Interval(1.0));
  const Dual two(Interval(2.0));
  const Dual three(Interval(3.0));
  const Dual five(Interval(5.0));
  const Dual half(rational(1, 2));
  const Dual twoThirds(rational(2, 3));
  const Dual epsilonDual(epsilon);
  const Dual deltaDual(delta);
  const Dual aDual(a);
  const Dual primitiveADual(primitiveA);

  const Dual z2 = square(z);
  const Dual z3 = z2 * z;
  const Dual z4 = square(z2);
  const Dual oneMinusZ2 = one - z2;
  const Dual lambda = sqrtDual(oneMinusZ2);
  const Dual chiZero = sqrtDual(
      epsilonDual / Dual(rational(6))
      * cube(one - z) * (five * z + three));
  const Dual cZero = z2 * chiZero / oneMinusZ2;

  // These explicit first derivatives are kept as Dual expressions, so their
  // z derivatives enter the Jacobian of the transformed field exactly.
  const Dual chiZeroZ = chiZero * half
      * (-three / (one - z) + five / (five * z + three));
  const Dual cZeroZ =
      (two * z * chiZero + z2 * chiZeroZ) / oneMinusZ2
      + two * z3 * chiZero / square(oneMinusZ2);
  const Dual lambdaZ = -z / lambda;

  // Spectral coordinates for the scaled variables A=alpha/delta,
  // B=beta/delta: C=A+B=C0+b+n and D=A-B=lambda*(n-b).
  const Dual c = cZero + b + n;
  const Dual d = lambda * (n - b);

  // Exact H=0 positive root of V5(25).  Since S=chi+C, this is the
  // quadratic leading*chi^2-2*linearHalf*chi-constant=0.
  const Dual leading = one - epsilonDual * square(deltaDual) * z4;
  const Dual linearHalf =
      epsilonDual * square(deltaDual) * c * z4;
  const Dual rightWithoutSquareS =
      epsilonDual * half
      - twoThirds * aDual * epsilonDual * z
      - epsilonDual * (one + two * deltaDual * d) * z2
      + two * aDual * epsilonDual * (one + deltaDual * d) * z3
      + two * epsilonDual * primitiveADual * z4;
  const Dual constantPositive = rightWithoutSquareS
      + epsilonDual * square(deltaDual) * square(c) * z4;
  const Dual discriminant =
      square(linearHalf) + leading * constantPositive;
  const Dual root = sqrtDual(discriminant);
  const Dual negativeRoot = (linearHalf - root) / leading;
  const Dual chi = (linearHalf + root) / leading;
  const Dual rootDerivative = two * root;
  const Dual s = chi + c;
  const Dual pi = deltaDual * s;

  // Exact scaled V4 field V5(24), first written in (z,C,D), then pulled
  // back through the z-dependent spectral frame.
  const Dual zDot = -deltaDual * s * z3;
  // Write the pullback in cancellation-free form.  Direct interval
  // subtraction of Cdot and Ddot/lambda loses the exact -lambda*b and
  // +lambda*n diagonal terms.  Likewise, chi-chi0 is obtained by
  // rationalizing the two energy equations.  With t=a-1,
  // F(1+t)-F(1)=-(2/3)t+(1/3)t^3+(1/12)t^4 exactly.
  const Dual t = aDual - one;
  const Dual primitiveDifference =
      -twoThirds * t + Dual(rational(1, 3)) * cube(t)
      + Dual(rational(1, 12)) * fourth(t);
  const Dual chiSquareDifference =
      -twoThirds * epsilonDual * t * z
      - two * epsilonDual * deltaDual * d * z2
      + two * epsilonDual * (t + aDual * deltaDual * d) * z3
      + (two * epsilonDual * primitiveDifference
         + epsilonDual * square(deltaDual) * square(s)) * z4;
  const Dual chiDifference = chiSquareDifference / (chi + chiZero);
  const Dual commonCorrection = deltaDual
      * (z2 * (-epsilonDual * (one - aDual * z) + two * chi * s)
         + cZeroZ * s * z3);
  const Dual differenceCorrection = z2 * chiDifference / lambda
      + deltaDual * s * (n - b)
          * (z2 - lambdaZ * z3 / lambda);
  const Dual bDot = -lambda * b
      + half * (commonCorrection + differenceCorrection);
  const Dual nDot = lambda * n
      + half * (commonCorrection - differenceCorrection);
  const std::array<Dual, kStateDimension> field = {zDot, bDot, nDot};

  Evaluation result;
  result.lambda = lambda.value;
  result.chiZero = chiZero.value;
  result.cZero = cZero.value;
  result.c = c.value;
  result.d = d.value;
  result.quadraticLeading = leading.value;
  result.quadraticConstant = constantPositive.value;
  result.discriminant = discriminant.value;
  result.negativeRoot = negativeRoot.value;
  result.chi = chi.value;
  result.rootDerivative = rootDerivative.value;
  result.s = s.value;
  result.pi = pi.value;
  for (std::size_t row = 0; row < kStateDimension; ++row) {
    result.field[row] = field[row].value;
    result.jacobian[row] = field[row].derivative;
  }
  return result;
}

double mu2GershgorinUpper(
    const std::array<Gradient, kStateDimension>& jacobian) {
  double result = -std::numeric_limits<double>::infinity();
  constexpr std::array<std::size_t, 2> base = {0, 1};
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
  for (const std::size_t row : {std::size_t(0), std::size_t(1)})
    sum += sqr(jacobian[row][2].abs());
  return sqrt(sum).rightBound();
}

double dNormUpper(
    const std::array<Gradient, kStateDimension>& jacobian) {
  Interval sum(0.0);
  for (const std::size_t column : {std::size_t(0), std::size_t(1)})
    sum += sqr(jacobian[2][column].abs());
  return sqrt(sum).rightBound();
}

Interval hull(const Interval& left, const Interval& right) {
  return Interval(std::min(left.leftBound(), right.leftBound()),
                  std::max(left.rightBound(), right.rightBound()));
}

void includeInterval(bool initialized, Interval& target,
                     const Interval& value) {
  target = initialized ? hull(target, value) : value;
}

struct Aggregate {
  bool initialized = false;
  Interval lambda;
  Interval chiZero;
  Interval cZero;
  Interval quadraticLeading;
  Interval quadraticConstant;
  Interval discriminant;
  Interval negativeRoot;
  Interval chi;
  Interval rootDerivative;
  Interval s;
  Interval pi;
  Interval zZeroField;
  Interval zFaceMargin;
  Interval bPlusMargin;
  Interval bMinusMargin;
  Interval nPlusMargin;
  Interval nMinusMargin;
  Interval r2Z;
  Interval r2Pi;
  Interval r2Omega;
  Interval r2Q1;
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

void includeCore(Aggregate& aggregate, const Evaluation& evaluation) {
  const bool initialized = aggregate.initialized;
  includeInterval(initialized, aggregate.lambda, evaluation.lambda);
  includeInterval(initialized, aggregate.chiZero, evaluation.chiZero);
  includeInterval(initialized, aggregate.cZero, evaluation.cZero);
  includeInterval(initialized, aggregate.quadraticLeading,
                  evaluation.quadraticLeading);
  includeInterval(initialized, aggregate.quadraticConstant,
                  evaluation.quadraticConstant);
  includeInterval(initialized, aggregate.discriminant,
                  evaluation.discriminant);
  includeInterval(initialized, aggregate.negativeRoot,
                  evaluation.negativeRoot);
  includeInterval(initialized, aggregate.chi, evaluation.chi);
  includeInterval(initialized, aggregate.rootDerivative,
                  evaluation.rootDerivative);
  includeInterval(initialized, aggregate.s, evaluation.s);
  includeInterval(initialized, aggregate.pi, evaluation.pi);

  const double muC = mu2GershgorinUpper(evaluation.jacobian);
  const double bNorm = bNormUpper(evaluation.jacobian);
  const double dNorm = dNormUpper(evaluation.jacobian);
  const double aLower = evaluation.jacobian[2][2].leftBound();
  aggregate.muCUpper = std::max(aggregate.muCUpper, muC);
  aggregate.bNormUpper = std::max(aggregate.bNormUpper, bNorm);
  aggregate.dNormUpper = std::max(aggregate.dNormUpper, dNorm);
  aggregate.aLower = std::min(aggregate.aLower, aLower);

  const Interval cone = Interval(aLower) - Interval(dNorm)
      - Interval(muC) - Interval(bNorm);
  const Interval normal = Interval(aLower) - Interval(bNorm);
  const Interval tangent = Interval(muC) + Interval(bNorm);
  aggregate.coneLower = std::min(aggregate.coneLower, cone.leftBound());
  aggregate.normalLower = std::min(
      aggregate.normalLower, normal.leftBound());
  for (std::size_t order = 0; order < aggregate.gammaLower.size(); ++order) {
    const Interval gamma = normal - Interval(static_cast<double>(order))
        * tangent;
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

Interval scalar(double value) { return Interval(value); }

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
    const Interval zMaximum = rational(2, 9);
    const Interval bRadius = rational(1, 16);
    const Interval bBox(-bRadius.rightBound(), bRadius.rightBound());
    const Interval nRadius = rational(1, 100000);
    const Interval nBox(-nRadius.rightBound(), nRadius.rightBound());
    const Interval bPlus = bRadius;
    const Interval bMinus = -bRadius;
    const Interval nPlus = nRadius;
    const Interval nMinus = -nRadius;
    const Interval nu = rational(1, 64);
    const Interval lambdaFloor = sqrt(
        Interval(1.0) - sqr(zMaximum));

    constexpr long kRSlabs = 4;
    constexpr long kA2Slabs = 8;
    constexpr long kEpsilonSlabs = 4;
    constexpr long kZSlabs = 64;
    constexpr long kBSlabs = 8;
    const std::array<std::pair<long, long>, 5> rNodes = {{
        {1, 100}, {1, 80}, {3, 200}, {7, 400}, {1, 50}}};

    Aggregate aggregate;
    bool zZeroInitialized = false;
    bool zFaceInitialized = false;
    bool bPlusInitialized = false;
    bool bMinusInitialized = false;
    bool nPlusInitialized = false;
    bool nMinusInitialized = false;
    bool r2Initialized = false;
    std::size_t cellCount = 0;

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
          for (long zIndex = 0; zIndex < kZSlabs; ++zIndex) {
            const Interval z = intervalFromRationals(
                2 * zIndex, 9 * kZSlabs,
                2 * (zIndex + 1), 9 * kZSlabs);
            for (long bIndex = 0; bIndex < kBSlabs; ++bIndex) {
              const Interval b = intervalFromRationals(
                  bIndex - 4, 64, bIndex - 3, 64);
              const Evaluation core = evaluate(r, a2, epsilon, z, b, nBox);
              includeCore(aggregate, core);

              const Evaluation nUpper = evaluate(
                  r, a2, epsilon, z, b, nPlus);
              includeFace(aggregate.nPlusMargin, nPlusInitialized,
                          nUpper.field[2]);
              const Evaluation nLower = evaluate(
                  r, a2, epsilon, z, b, nMinus);
              includeFace(aggregate.nMinusMargin, nMinusInitialized,
                          -nLower.field[2]);
              ++cellCount;
            }

            const Evaluation bUpper = evaluate(
                r, a2, epsilon, z, bPlus, nBox);
            includeFace(aggregate.bPlusMargin, bPlusInitialized,
                        -bUpper.field[1]);
            const Evaluation bLower = evaluate(
                r, a2, epsilon, z, bMinus, nBox);
            includeFace(aggregate.bMinusMargin, bMinusInitialized,
                        bLower.field[1]);
          }

          const Evaluation zZero = evaluate(
              r, a2, epsilon, Interval(0.0), bBox, nBox);
          includeFace(aggregate.zZeroField, zZeroInitialized,
                      zZero.field[0]);
          const Evaluation zFace = evaluate(
              r, a2, epsilon, zMaximum, bBox, nBox);
          includeFace(aggregate.zFaceMargin, zFaceInitialized,
                      -zFace.field[0]);

          // At r1=R=2, z=(1+4*sqrt(epsilon))^{-1}.  Equation V5(37)
          // gives C=2*epsilon*Pi-chi and D=4*epsilon*z*Omega.
          const Interval zR = Interval(1.0)
              / (Interval(1.0) + Interval(4.0) * sqrt(epsilon));
          for (long bIndex = 0; bIndex < kBSlabs; ++bIndex) {
            const Interval b = intervalFromRationals(
                bIndex - 4, 64, bIndex - 3, 64);
            const Evaluation atR2 = evaluate(
                r, a2, epsilon, zR, b, nBox);
            const Interval k1Pi =
                (atR2.c + atR2.chi) / (Interval(2.0) * epsilon);
            const Interval k1Omega =
                atR2.d / (Interval(4.0) * epsilon * zR);
            const Interval k1Q1 = atR2.chi
                / (Interval(8.0) * sqr(zR) * epsilon * sqrt(epsilon));
            includeInterval(r2Initialized, aggregate.r2Z, zR);
            includeInterval(r2Initialized, aggregate.r2Pi, k1Pi);
            includeInterval(r2Initialized, aggregate.r2Omega, k1Omega);
            includeInterval(r2Initialized, aggregate.r2Q1, k1Q1);
            r2Initialized = true;
          }
        }
      }
    }

    std::vector<Obligation> obligations;
    Verdict positiveBranch = strictPositive(aggregate.lambda);
    positiveBranch = combine(
        positiveBranch, strictPositive(aggregate.chiZero));
    positiveBranch = combine(
        positiveBranch, strictPositive(aggregate.quadraticLeading));
    positiveBranch = combine(
        positiveBranch, strictPositive(aggregate.quadraticConstant));
    positiveBranch = combine(
        positiveBranch, strictPositive(aggregate.discriminant));
    positiveBranch = combine(
        positiveBranch, strictPositive(-aggregate.negativeRoot));
    positiveBranch = combine(positiveBranch, strictPositive(aggregate.chi));
    positiveBranch = combine(
        positiveBranch, strictPositive(aggregate.rootDerivative));
    positiveBranch = combine(positiveBranch, strictPositive(aggregate.s));
    positiveBranch = combine(positiveBranch, strictPositive(aggregate.pi));
    obligations.push_back({
        "V4.AD_ZERO.POSITIVE_BRANCH", positiveBranch,
        "The adapted frame is regular and the exact H=0 energy equation has one regular positive chi root with S>0 and pi=delta*S>0",
        {{"lambda", aggregate.lambda},
         {"chi_zero", aggregate.chiZero},
         {"C_zero", aggregate.cZero},
         {"quadratic_leading", aggregate.quadraticLeading},
         {"quadratic_constant", aggregate.quadraticConstant},
         {"quarter_discriminant", aggregate.discriminant},
         {"negative_root", aggregate.negativeRoot},
         {"chi", aggregate.chi},
         {"implicit_chi_derivative", aggregate.rootDerivative},
         {"S", aggregate.s},
         {"pi", aggregate.pi}}});

    Verdict faces = exactZero(aggregate.zZeroField);
    faces = combine(faces, strictPositive(aggregate.zFaceMargin));
    faces = combine(faces, strictPositive(aggregate.bPlusMargin));
    faces = combine(faces, strictPositive(aggregate.bMinusMargin));
    faces = combine(faces, strictPositive(aggregate.nPlusMargin));
    faces = combine(faces, strictPositive(aggregate.nMinusMargin));
    obligations.push_back({
        "V4.AD_ZERO.CORRIDOR_FACES", faces,
        "z=0 is invariant, z=2/9 and both stable b faces are inward, and both unstable n faces are outward",
        {{"z_dot_at_z_zero", aggregate.zZeroField},
         {"minus_z_dot_at_z_max", aggregate.zFaceMargin},
         {"minus_b_dot_at_b_plus", aggregate.bPlusMargin},
         {"b_dot_at_b_minus", aggregate.bMinusMargin},
         {"n_dot_at_n_plus", aggregate.nPlusMargin},
         {"minus_n_dot_at_n_minus", aggregate.nMinusMargin}}});

    const double muMargin =
        (nu - scalar(aggregate.muCUpper)).leftBound();
    const double bMargin =
        (nu - scalar(aggregate.bNormUpper)).leftBound();
    const double dMargin =
        (nu - scalar(aggregate.dNormUpper)).leftBound();
    const double aMargin =
        (scalar(aggregate.aLower) - (lambdaFloor - nu)).leftBound();
    Verdict blocks = strictPositive(muMargin);
    blocks = combine(blocks, strictPositive(bMargin));
    blocks = combine(blocks, strictPositive(dMargin));
    blocks = combine(blocks, strictPositive(aMargin));
    obligations.push_back({
        "V4.AD_ZERO.GENERATOR_BLOCKS", blocks,
        "For base X=(z,b), mu2(C), ||B||, ||D|| <= nu=1/64 and a_n >= sqrt(1-(2/9)^2)-nu",
        {{"mu2_C_upper", scalar(aggregate.muCUpper)},
         {"B_norm_upper", scalar(aggregate.bNormUpper)},
         {"D_norm_upper", scalar(aggregate.dNormUpper)},
         {"a_n_lower", scalar(aggregate.aLower)},
         {"lambda_floor", lambdaFloor},
         {"nu_minus_mu2_C", scalar(muMargin)},
         {"nu_minus_B_norm", scalar(bMargin)},
         {"nu_minus_D_norm", scalar(dMargin)},
         {"a_minus_lambda_floor_plus_nu", scalar(aMargin)}}});

    Verdict rates = strictPositive(aggregate.coneLower);
    rates = combine(rates, strictPositive(aggregate.normalLower));
    for (const double gamma : aggregate.gammaLower)
      rates = combine(rates, strictPositive(gamma));
    obligations.push_back({
        "V4.AD_ZERO.CONE_AND_BUNCHING", rates,
        "The slope-one cone, normal rate, and graph-transform gaps gamma_j for j=0,...,3 are strict",
        {{"slope_one_cone_lower", scalar(aggregate.coneLower)},
         {"normal_rate_lower", scalar(aggregate.normalLower)},
         {"gamma_0_lower", scalar(aggregate.gammaLower[0])},
         {"gamma_1_lower", scalar(aggregate.gammaLower[1])},
         {"gamma_2_lower", scalar(aggregate.gammaLower[2])},
         {"gamma_3_lower", scalar(aggregate.gammaLower[3])},
         {"theorem_cone_floor_lambda_minus_4nu",
          lambdaFloor - Interval(4.0) * nu},
         {"theorem_normal_floor_lambda_minus_2nu",
          lambdaFloor - Interval(2.0) * nu},
         {"theorem_gamma3_floor_lambda_minus_8nu",
          lambdaFloor - Interval(8.0) * nu}}});

    const Verdict r2Status = combine(
        strictPositive(aggregate.r2Z),
        combine(strictPositive(zMaximum - aggregate.r2Z),
        combine(strictPositive(aggregate.r2Pi),
                strictPositive(aggregate.r2Q1))));
    obligations.push_back({
        "V4.AD_ZERO.R2_ATTACHMENT_TUBE", r2Status,
        "The parameter-dependent R=2 cut lies inside the z corridor and the adapted graph tube gives finite positive K1 Pi and q1 enclosures there",
        {{"z_R2", aggregate.r2Z},
         {"z_max_minus_z_R2", zMaximum - aggregate.r2Z},
         {"Pi_R2", aggregate.r2Pi},
         {"Omega_R2", aggregate.r2Omega},
         {"q1_R2", aggregate.r2Q1},
         {"normal_graph_tube", nBox}}});

    Verdict mathematical = Verdict::Pass;
    for (const auto& obligation : obligations)
      mathematical = combine(mathematical, obligation.status);
    const Verdict status = combine(rounding.status, mathematical);

    std::cout
        << "{\"schema_version\":\"rfsn-vdp-v4-adapted-zero-tube-probe/1\","
        << "\"status\":\"" << verdictName(status) << "\","
        << "\"mathematical_status\":\"" << verdictName(mathematical)
        << "\",\"claim_bearing\":false,"
        << "\"claim_boundary\":{"
        << "\"parent_obligation\":\"V4 zero-energy adapted subgraph local mathematical PASS; Issue #7 aggregate remains PENDING\","
        << "\"proved_scope\":\"unique maximal future-staying graph n=Gamma_ad(z,b) in the displayed H=0 scaled spectral tube, with an R=2 attachment enclosure\","
        << "\"open_scope\":[\"V5 incidence and scalar root\","
           "\"resolved K1 graph transport\",\"Issue #7 aggregate and release\"]},"
        << "\"scope\":\"ZERO_ENERGY_ADAPTED_SPECTRAL_TUBE\","
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
        << ",\"z_slabs\":" << kZSlabs
        << ",\"b_slabs\":" << kBSlabs
        << ",\"cell_count\":" << cellCount << "},"
        << "\"corridor\":{"
        << "\"z\":" << intervalJson(Interval(0.0, zMaximum.rightBound()))
        << ",\"H\":" << intervalJson(Interval(0.0))
        << ",\"b\":" << intervalJson(bBox)
        << ",\"n\":" << intervalJson(nBox)
        << ",\"nu\":" << intervalJson(nu) << "},"
        << "\"coordinate_map\":{"
        << "\"C\":\"C0(z,epsilon)+b+n\","
        << "\"D\":\"sqrt(1-z^2)*(n-b)\","
        << "\"A\":\"(C+D)/2\",\"B\":\"(C-D)/2\","
        << "\"alpha\":\"delta*A\",\"beta\":\"delta*B\"},"
        << "\"obligations\":[";
    for (std::size_t index = 0; index < obligations.size(); ++index) {
      if (index) std::cout << ',';
      std::cout << obligationJson(obligations[index]);
    }
    std::cout << "]}\n";
    return status == Verdict::Pass ? 0 : 1;
  } catch (const std::exception& error) {
    std::cerr << "vdp_v4_adapted_zero_tube_probe: " << error.what() << '\n';
    return 2;
  }
}
