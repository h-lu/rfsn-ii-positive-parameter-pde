#include "interval_io.hpp"
#include "rounding_self_test.hpp"
#include "verdict.hpp"

#include <algorithm>
#include <array>
#include <cmath>
#include <cstddef>
#include <cstdlib>
#include <exception>
#include <iostream>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>
#include <utility>
#include <vector>

// Strict finite resolved-K1 tube for the zero-energy V5 matching problem.
//
// The physical leaf has sigma=r/r1.  Around the explicit leading centre
// curve (Pi0,Omega0), use the frozen saddle eigenbasis
//
//   b = ((Pi-Pi0) - (Omega-Omega0)/lambda)/2,
//   n = ((Pi-Pi0) + (Omega-Omega0)/lambda)/2.
//
// Here b is the future-stable base coordinate and n the future-unstable
// normal coordinate.  The calculation below verifies a finite nonautonomous
// graph-transform tube from the parameter-dependent U=-4 cut to r1=2.  It
// does not by itself identify the V4 terminal graph or a source incidence.

namespace {

using rfsn::rigorous::Interval;
using rfsn::rigorous::Verdict;
using rfsn::rigorous::combine;
using rfsn::rigorous::intervalJson;
using rfsn::rigorous::verdictName;

constexpr std::size_t kDimension = 3;  // (r1,b,n)
using Gradient = std::array<Interval, kDimension>;

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

  explicit Dual(const Interval& input = Interval(0.0)) : value(input) {
    for (auto& entry : derivative) entry = Interval(0.0);
  }

  static Dual variable(const Interval& input, std::size_t index) {
    Dual result(input);
    result.derivative.at(index) = Interval(1.0);
    return result;
  }
};

Dual operator+(const Dual& left, const Dual& right) {
  Dual result(left.value + right.value);
  for (std::size_t index = 0; index < kDimension; ++index)
    result.derivative[index] =
        left.derivative[index] + right.derivative[index];
  return result;
}

Dual operator-(const Dual& left, const Dual& right) {
  Dual result(left.value - right.value);
  for (std::size_t index = 0; index < kDimension; ++index)
    result.derivative[index] =
        left.derivative[index] - right.derivative[index];
  return result;
}

Dual operator-(const Dual& input) {
  Dual result(-input.value);
  for (std::size_t index = 0; index < kDimension; ++index)
    result.derivative[index] = -input.derivative[index];
  return result;
}

Dual operator*(const Dual& left, const Dual& right) {
  Dual result(left.value * right.value);
  for (std::size_t index = 0; index < kDimension; ++index) {
    result.derivative[index] =
        left.derivative[index] * right.value +
        left.value * right.derivative[index];
  }
  return result;
}

Dual reciprocal(const Dual& input) {
  if (input.value.contains(0.0))
    throw std::runtime_error("dual reciprocal denominator contains zero");
  Dual result(Interval(1.0) / input.value);
  for (std::size_t index = 0; index < kDimension; ++index)
    result.derivative[index] = -input.derivative[index] / sqr(input.value);
  return result;
}

Dual operator/(const Dual& left, const Dual& right) {
  return left * reciprocal(right);
}

Dual operator+(const Interval& left, const Dual& right) {
  return Dual(left) + right;
}

Dual operator+(const Dual& left, const Interval& right) {
  return left + Dual(right);
}

Dual operator*(const Interval& left, const Dual& right) {
  return Dual(left) * right;
}

Dual operator/(const Dual& left, const Interval& right) {
  return left / Dual(right);
}

Dual sqrtDual(const Dual& input) {
  if (input.value.leftBound() <= 0.0)
    throw std::runtime_error("dual square-root argument is not positive");
  const Interval root = sqrt(input.value);
  Dual result(root);
  for (std::size_t index = 0; index < kDimension; ++index)
    result.derivative[index] =
        input.derivative[index] / (Interval(2.0) * root);
  return result;
}

Dual square(const Dual& input) { return input * input; }
Dual cube(const Dual& input) { return square(input) * input; }

struct Evaluation {
  Interval q1Radicand;
  Interval q1;
  Interval pi;
  Interval omega;
  Interval r1Speed;
  Interval faceTimeScale;
  Interval bField;
  Interval nField;
  Interval bOrientedField;
  Interval nOrientedField;
  Interval bOrientedR1Derivative;
  Interval nOrientedR1Derivative;
  std::array<std::array<Interval, 2>, 2> jacobian;
};

Evaluation evaluate(const Interval& r, const Interval& a2,
                    const Interval& epsilon, const Interval& r1Box,
                    const Interval& bBox, const Interval& nBox) {
  const Dual r1 = Dual::variable(r1Box, 0);
  const Dual b = Dual::variable(bBox, 1);
  const Dual n = Dual::variable(nBox, 2);
  const Dual two(Interval(2.0));
  const Dual half(rational(1, 2));
  const Dual rootEpsilon(sqrt(epsilon));
  const Dual a2Dual(a2);
  const Dual rDual(r);
  const Dual sigma = rDual / r1;
  const Dual sigma2 = square(sigma);
  const Dual sigma3 = cube(sigma);
  const Dual sigma4 = square(sigma2);
  const Dual sigma5 = sigma4 * sigma;
  const Dual sigma9 = cube(cube(sigma));
  const Dual sigma12 = square(square(cube(sigma)));

  // Leading singular branch and the displayed finite-sigma reference from
  // V5.  We keep the exact identities below in terms of P,Q,K,W rather
  // than subtracting two O(1) vector-field expressions and then dividing
  // by the O(sigma^2) r1 clock.
  const Dual xParameter = rootEpsilon * square(r1);
  const Dual denominator = two + xParameter;
  const Dual qZero = sqrtDual(
      (Dual(Interval(8.0)) + Interval(3.0) * xParameter) /
      (Interval(6.0) * rootEpsilon));
  const Dual pZero = qZero / denominator;
  const Dual correction =
      sigma3 * a2Dual * r1 * (xParameter + Interval(3.0)) /
      (Interval(3.0) * rootEpsilon * qZero * denominator);
  const Dual omegaZero =
      sigma2 * (xParameter + Interval(4.0)) /
      (Interval(3.0) * cube(denominator));
  const Dual lambda = sqrtDual(rootEpsilon * denominator);

  // Pi=P+eta equals (P-K)+e with e=b+n, while Omega=W+y.
  const Dual e = b + n;
  const Dual eta = e - correction;
  const Dual y = lambda * (n - b);
  const Dual pi = pZero + eta;
  const Dual omega = omegaZero + y;

  // Exact V5(34) positive root on H=0.  On the reference (e,y)=(0,0),
  // the O(sigma^3 a2) term is exactly -2*Q*D*K.  Compare first with
  // qBar=Q-D*K so that this term cancels before interval evaluation.
  const Dual qBar = qZero - denominator * correction;
  const Dual sigma7 = sigma5 * sigma2;
  // Fully expanded remainder after the -2*Q*D*K cancellation.  In
  // particular, P^2*sigma^4-2*W*sigma^2/s is evaluated as its exact
  // positive rational form, which prevents a final loss near r1=2.
  const Dual referenceResidualNumerator =
      sigma4 * xParameter *
          (Interval(3.0) * xParameter + Interval(10.0)) /
          (Interval(6.0) * rootEpsilon * cube(denominator)) -
      two * a2Dual * r1 * sigma7 *
          (square(xParameter) + Interval(4.0) * xParameter +
           Interval(2.0)) /
          (Interval(3.0) * rootEpsilon * cube(denominator)) +
      square(correction) * (sigma4 - square(denominator)) +
      two * cube(a2Dual) * cube(r1) * sigma9 /
          (Interval(3.0) * rootEpsilon) +
      square(square(a2Dual)) * cube(square(r1)) * sigma12 /
          Interval(6.0);
  const Dual referenceQ1Radicand =
      square(qBar) + referenceResidualNumerator;
  const Dual referenceQ1 = sqrtDual(referenceQ1Radicand);
  const Dual referenceQ1Residual =
      referenceResidualNumerator / (referenceQ1 + qBar);

  // The remaining perturbation is exact and vanishes at e=y=0.
  const Dual perturbationRadicand =
      -two * y * sigma2 / rootEpsilon +
      e * (two * (pZero - correction) + e) * sigma4 +
      two * y * a2Dual * r1 * sigma5 / rootEpsilon;
  const Dual q1Radicand = referenceQ1Radicand + perturbationRadicand;
  const Dual q1 = sqrtDual(q1Radicand);
  const Dual perturbationQ1 =
      perturbationRadicand / (q1 + referenceQ1);
  // q1-Q=-D*K+qResidual.  Keeping the first term symbolic below removes
  // its exact cancellation with the spectral K terms.
  const Dual qResidual = referenceQ1Residual + perturbationQ1;

  const Dual r1Speed =
      half * rootEpsilon * sigma2 * pi * r1;

  // Exact logarithmic derivative of K.  It is regular when a2=0 because
  // K itself then vanishes.
  const Dual correctionPrime = correction / r1 *
      (-two + two * xParameter /
          (xParameter + Interval(3.0)) -
       Interval(3.0) * xParameter /
          (Interval(8.0) + Interval(3.0) * xParameter) -
       two * xParameter / denominator);

  // Exact r1-time residual field for x=Pi-(P-K)=b+n and
  // y=Omega-W=lambda(n-b).  All singular leading terms have cancelled
  // algebraically before interval evaluation.
  const Dual xFactor =
      two / (rootEpsilon * sigma2 * r1 * pZero * pi);
  const Dual yFactor =
      two / (sigma2 * r1 * pZero * pi);
  const Dual omegaReferenceCorrection =
      Interval(4.0) * sigma2 * xParameter *
          (xParameter + Interval(5.0)) /
          (Interval(3.0) * square(square(denominator)) * r1);
  const Dual lambdaLogPrime = xParameter / (r1 * denominator);

  // Combine the two spectral equations before interval evaluation.  The
  // identities y=lambda(n-b), Q=P(2+x), and
  // lambda^2=s(2+x) remove the large opposite-signed eigenline terms.
  // Evaluating xField +/- yField/lambda separately would reintroduce an
  // artificial O(sigma^-2) interval width.
  const Dual bField = half *
      (-two * xFactor * pZero * lambda * b -
       xFactor * omegaZero * eta +
       yFactor * pZero * qResidual / lambda +
       (n - Interval(3.0) * b + correction) / r1 +
       correctionPrime - omegaReferenceCorrection / lambda +
       (n - b) * lambdaLogPrime);
  const Dual nField = half *
      (two * xFactor * pZero * lambda * n -
       xFactor * omegaZero * eta -
       yFactor * pZero * qResidual / lambda +
       (b - Interval(3.0) * n + correction) / r1 +
       correctionPrime + omegaReferenceCorrection / lambda -
       (n - b) * lambdaLogPrime);

  // For the isolating faces use an algebraically distributed positive
  // multiple of the r1-time field.  Its scale
  // s*sigma^2*r1*P*Pi*lambda is positive on the certified branch.  Face
  // signs are therefore unchanged, while every sigma^-2 denominator is
  // removed before interval evaluation.
  const Dual faceTimeScale =
      rootEpsilon * sigma2 * r1 * pZero * pi * lambda;
  const Dual bOrientedField = half *
      (-Interval(4.0) * pZero * square(lambda) * b -
       two * omegaZero * eta * lambda +
       two * rootEpsilon * pZero * qResidual +
       faceTimeScale *
          ((n - Interval(3.0) * b + correction) / r1 +
           correctionPrime - omegaReferenceCorrection / lambda +
           (n - b) * lambdaLogPrime));
  const Dual nOrientedField = half *
      (Interval(4.0) * pZero * square(lambda) * n -
       two * omegaZero * eta * lambda -
       two * rootEpsilon * pZero * qResidual +
       faceTimeScale *
          ((b - Interval(3.0) * n + correction) / r1 +
           correctionPrime + omegaReferenceCorrection / lambda -
           (n - b) * lambdaLogPrime));

  Evaluation result;
  result.q1Radicand = q1Radicand.value;
  result.q1 = q1.value;
  result.pi = pi.value;
  result.omega = omega.value;
  result.r1Speed = r1Speed.value;
  result.bField = bField.value;
  result.nField = nField.value;
  result.faceTimeScale = faceTimeScale.value;
  result.bOrientedField = bOrientedField.value;
  result.nOrientedField = nOrientedField.value;
  result.bOrientedR1Derivative = bOrientedField.derivative[0];
  result.nOrientedR1Derivative = nOrientedField.derivative[0];
  result.jacobian = {{{bField.derivative[1], bField.derivative[2]},
                      {nField.derivative[1], nField.derivative[2]}}};
  return result;
}

double absoluteUpper(const Interval& input) {
  return input.abs().rightBound();
}

Interval hull(const Interval& left, const Interval& right) {
  return Interval(std::min(left.leftBound(), right.leftBound()),
                  std::max(left.rightBound(), right.rightBound()));
}

Interval meanValueEnclosure(const Interval& centreValue,
                            const Interval& derivative,
                            const Interval& variable,
                            double centre) {
  return centreValue + derivative * (variable - Interval(centre));
}

void include(bool initialized, Interval& target, const Interval& value) {
  target = initialized ? hull(target, value) : value;
}

Verdict strictPositive(const Interval& input) {
  if (input.leftBound() > 0.0) return Verdict::Pass;
  if (input.rightBound() <= 0.0) return Verdict::Fail;
  return Verdict::Inconclusive;
}

struct Aggregate {
  bool initialized = false;
  Interval q1Radicand;
  Interval q1;
  Interval pi;
  Interval omega;
  Interval r1Speed;
  Interval faceTimeScale;
  Interval bPlusMargin;
  Interval bMinusMargin;
  Interval nPlusMargin;
  Interval nMinusMargin;
  double cUpper = -std::numeric_limits<double>::infinity();
  double bCrossUpper = 0.0;
  double dCrossUpper = 0.0;
  double aLower = std::numeric_limits<double>::infinity();
  double slopeMarginLower = std::numeric_limits<double>::infinity();
};

void includeCore(Aggregate& aggregate, const Evaluation& evaluation,
                 const Interval& slope) {
  const bool was = aggregate.initialized;
  include(was, aggregate.q1Radicand, evaluation.q1Radicand);
  include(was, aggregate.q1, evaluation.q1);
  include(was, aggregate.pi, evaluation.pi);
  include(was, aggregate.omega, evaluation.omega);
  include(was, aggregate.r1Speed, evaluation.r1Speed);
  include(was, aggregate.faceTimeScale, evaluation.faceTimeScale);
  const double cUpper = evaluation.jacobian[0][0].rightBound();
  const double bCross = absoluteUpper(evaluation.jacobian[0][1]);
  const double dCross = absoluteUpper(evaluation.jacobian[1][0]);
  const double aLower = evaluation.jacobian[1][1].leftBound();
  aggregate.cUpper = std::max(aggregate.cUpper, cUpper);
  aggregate.bCrossUpper = std::max(aggregate.bCrossUpper, bCross);
  aggregate.dCrossUpper = std::max(aggregate.dCrossUpper, dCross);
  aggregate.aLower = std::min(aggregate.aLower, aLower);
  const Interval margin =
      slope * (Interval(aLower) - Interval(cUpper) -
               Interval(bCross) * slope) - Interval(dCross);
  aggregate.slopeMarginLower = std::min(
      aggregate.slopeMarginLower, margin.leftBound());
  aggregate.initialized = true;
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
         << rfsn::rigorous::jsonEscape(obligation.predicate)
         << "\",\"enclosures\":{";
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
    const Interval bRadius = rational(27, 200000);
    const Interval nRadius = rational(1, 10000);
    const Interval bBox(-bRadius.rightBound(), bRadius.rightBound());
    const Interval nBox(-nRadius.rightBound(), nRadius.rightBound());
    const Interval bPlus = bRadius;
    const Interval bMinus = -bRadius;
    const Interval nPlus = nRadius;
    const Interval nMinus = -nRadius;
    const Interval graphSlope = rational(7, 10);

    constexpr long kRSlabs = 8;
    constexpr long kA2Slabs = 32;
    constexpr long kEpsilonSlabs = 8;
    constexpr long kR1Slabs = 32;
    constexpr long kBSlabs = 16;
    const bool centreSmoke = std::getenv("RFSN_V5_K1_CENTER_SMOKE") != nullptr;
    const long rSlabs = centreSmoke ? 1 : kRSlabs;
    const long a2Slabs = centreSmoke ? 1 : kA2Slabs;
    const long epsilonSlabs = centreSmoke ? 1 : kEpsilonSlabs;
    Aggregate aggregate;
    bool bPlusInitialized = false;
    bool bMinusInitialized = false;
    bool nPlusInitialized = false;
    bool nMinusInitialized = false;
    std::size_t cellCount = 0;

    for (long rIndex = 0; rIndex < rSlabs; ++rIndex) {
      const Interval r = centreSmoke ? rational(3, 200) :
          intervalFromRationals(
              kRSlabs + rIndex, 100 * kRSlabs,
              kRSlabs + rIndex + 1, 100 * kRSlabs);
      for (long a2Index = 0; a2Index < a2Slabs; ++a2Index) {
        const Interval a2 = centreSmoke ? Interval(0.0) :
            intervalFromRationals(
                -kA2Slabs + 2 * a2Index, 4 * kA2Slabs,
                -kA2Slabs + 2 * (a2Index + 1), 4 * kA2Slabs);
        const Interval r1Central =
            r * sqrt(Interval(4.0) + r * a2);
        for (long epsilonIndex = 0; epsilonIndex < epsilonSlabs;
             ++epsilonIndex) {
          const Interval epsilon = centreSmoke ? Interval(1.0) :
              intervalFromRationals(
                  4 * kEpsilonSlabs + 2 * epsilonIndex,
                  5 * kEpsilonSlabs,
                  4 * kEpsilonSlabs + 2 * (epsilonIndex + 1),
                  5 * kEpsilonSlabs);
          for (long r1Index = 0; r1Index < kR1Slabs; ++r1Index) {
            const Interval unit = intervalFromRationals(
                r1Index * r1Index, kR1Slabs * kR1Slabs,
                (r1Index + 1) * (r1Index + 1),
                kR1Slabs * kR1Slabs);
            // The map c+(2-c)u is increasing in both c and u on this
            // box.  Evaluating its two endpoint pairs avoids losing the
            // repeated-u correlation in ordinary interval arithmetic.
            const Interval centralLower(r1Central.leftBound());
            const Interval centralUpper(r1Central.rightBound());
            const Interval unitLower(unit.leftBound());
            const Interval unitUpper(unit.rightBound());
            const Interval r1Lower = centralLower +
                (Interval(2.0) - centralLower) * unitLower;
            const Interval r1Upper = centralUpper +
                (Interval(2.0) - centralUpper) * unitUpper;
            const Interval r1(
                r1Lower.leftBound(), r1Upper.rightBound());
            const double r1Centre = r1.leftBound() +
                (r1.rightBound() - r1.leftBound()) / 2.0;
            const Interval r1Point(r1Centre);
            for (long bIndex = 0; bIndex < kBSlabs; ++bIndex) {
              const Interval bLower = -bRadius +
                  Interval(2.0) * bRadius *
                      rational(bIndex, kBSlabs);
              const Interval bUpper = -bRadius +
                  Interval(2.0) * bRadius *
                      rational(bIndex + 1, kBSlabs);
              const Interval b(
                  bLower.leftBound(), bUpper.rightBound());
              const Evaluation core = evaluate(
                  r, a2, epsilon, r1, b, nBox);
              includeCore(aggregate, core, graphSlope);

              const Evaluation nUpper = evaluate(
                  r, a2, epsilon, r1, b, nPlus);
              const Evaluation nUpperCentre = evaluate(
                  r, a2, epsilon, r1Point, b, nPlus);
              include(nPlusInitialized, aggregate.nPlusMargin,
                      meanValueEnclosure(
                          nUpperCentre.nOrientedField,
                          nUpper.nOrientedR1Derivative, r1, r1Centre));
              nPlusInitialized = true;
              const Evaluation nLower = evaluate(
                  r, a2, epsilon, r1, b, nMinus);
              const Evaluation nLowerCentre = evaluate(
                  r, a2, epsilon, r1Point, b, nMinus);
              include(nMinusInitialized, aggregate.nMinusMargin,
                      -meanValueEnclosure(
                          nLowerCentre.nOrientedField,
                          nLower.nOrientedR1Derivative, r1, r1Centre));
              nMinusInitialized = true;
              ++cellCount;
            }

            const Evaluation bUpper = evaluate(
                r, a2, epsilon, r1, bPlus, nBox);
            const Evaluation bUpperCentre = evaluate(
                r, a2, epsilon, r1Point, bPlus, nBox);
            include(bPlusInitialized, aggregate.bPlusMargin,
                    -meanValueEnclosure(
                        bUpperCentre.bOrientedField,
                        bUpper.bOrientedR1Derivative, r1, r1Centre));
            bPlusInitialized = true;
            const Evaluation bLower = evaluate(
                r, a2, epsilon, r1, bMinus, nBox);
            const Evaluation bLowerCentre = evaluate(
                r, a2, epsilon, r1Point, bMinus, nBox);
            include(bMinusInitialized, aggregate.bMinusMargin,
                    meanValueEnclosure(
                        bLowerCentre.bOrientedField,
                        bLower.bOrientedR1Derivative, r1, r1Centre));
            bMinusInitialized = true;
          }
        }
      }
    }

    std::vector<Obligation> obligations;
    Verdict branch = strictPositive(aggregate.q1Radicand);
    branch = combine(branch, strictPositive(aggregate.q1));
    branch = combine(branch, strictPositive(aggregate.pi));
    branch = combine(branch, strictPositive(aggregate.r1Speed));
    branch = combine(branch, strictPositive(aggregate.faceTimeScale));
    obligations.push_back({
        "V5.K1.POSITIVE_ROOT_AND_CLOCK", branch,
        "The exact H=0 q1 root is positive and r1 is a strict forward coordinate on the whole finite tube",
        {{"q1_radicand", aggregate.q1Radicand},
         {"q1", aggregate.q1},
         {"Pi", aggregate.pi},
         {"r1_speed", aggregate.r1Speed},
         {"positive_face_time_scale", aggregate.faceTimeScale}}});

    Verdict faces = strictPositive(aggregate.bPlusMargin);
    faces = combine(faces, strictPositive(aggregate.bMinusMargin));
    faces = combine(faces, strictPositive(aggregate.nPlusMargin));
    faces = combine(faces, strictPositive(aggregate.nMinusMargin));
    obligations.push_back({
        "V5.K1.TUBE_FACES", faces,
        "Both stable b faces are inward and both unstable n faces are strict exits, evaluated with the displayed positive face-time scale",
        {{"minus_b_field_at_b_plus", aggregate.bPlusMargin},
         {"b_field_at_b_minus", aggregate.bMinusMargin},
         {"n_field_at_n_plus", aggregate.nPlusMargin},
         {"minus_n_field_at_n_minus", aggregate.nMinusMargin}}});

    const Interval coneMargin(aggregate.slopeMarginLower);
    obligations.push_back({
        "V5.K1.PROJECTIVE_CONE", strictPositive(coneMargin),
        "The cellwise pointwise base-to-normal slope-7/10 projectivized cone is strictly backward invariant in the finite resolved-K1 tube",
        {{"graph_slope", graphSlope},
         {"C_upper", Interval(aggregate.cUpper)},
         {"B_cross_upper", Interval(aggregate.bCrossUpper)},
         {"D_cross_upper", Interval(aggregate.dCrossUpper)},
         {"a_normal_lower", Interval(aggregate.aLower)},
         {"cellwise_pointwise_cone_margin", coneMargin}}});

    Verdict mathematical = Verdict::Pass;
    for (const auto& obligation : obligations)
      mathematical = combine(mathematical, obligation.status);
    const Verdict status = combine(rounding.status, mathematical);

    std::cout
        << "{\"schema_version\":\"rfsn-vdp-v5-k1-tube-probe/3\","
        << "\"status\":\"" << verdictName(status) << "\","
        << "\"mathematical_status\":\"" << verdictName(mathematical)
        << "\",\"claim_bearing\":false,"
        << "\"box_id\":\"vdp-positive-box-v2\","
        << "\"scope\":\"ZERO_ENERGY_FINITE_RESOLVED_K1_TUBE\","
        << "\"sections\":{\"central\":\"U=-4\",\"outer\":\"r1=2\"},"
        << "\"tube\":{\"b\":" << intervalJson(bBox)
        << ",\"n\":" << intervalJson(nBox)
        << ",\"graph_slope\":" << intervalJson(graphSlope) << "},"
        << "\"cover\":{\"r_slabs\":" << rSlabs
        << ",\"a2_slabs\":" << a2Slabs
        << ",\"epsilon_slabs\":" << epsilonSlabs
        << ",\"r1_slabs\":" << kR1Slabs
        << ",\"b_slabs\":" << kBSlabs
        << ",\"cell_count\":" << cellCount << "},"
        << "\"rounding_self_test\":"
        << rfsn::rigorous::roundingReportJson(rounding) << ','
        << "\"claim_boundary\":{"
        << "\"proved_scope\":\"positive-root, clock, face, and slope-7/10 projective-cone bounds for a finite H=0 resolved-K1 tube\","
        << "\"open_scope\":[\"central regraph\",\"source first hit\","
           "\"V5 incidence\"]},"
        << "\"obligations\":[";
    for (std::size_t index = 0; index < obligations.size(); ++index) {
      if (index) std::cout << ',';
      std::cout << obligationJson(obligations[index]);
    }
    std::cout << "]}\n";
    return status == Verdict::Pass ? 0 : 1;
  } catch (const std::exception& error) {
    std::cerr << "vdp_v5_k1_tube_probe: " << error.what() << '\n';
    return 2;
  }
}
