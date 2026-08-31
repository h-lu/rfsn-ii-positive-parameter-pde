#include "interval_io.hpp"
#include "rounding_self_test.hpp"
#include "verdict.hpp"

#include <algorithm>
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

// Strict lower-face coordinate attachment for the zero-energy V5 problem.
//
// This probe evaluates the exact resolved-K1 to central transition on U=-4.
// It proves a fixed central patch, transition regularity, and a uniform
// regraph estimate for every C1 K1 graph with |dn/db| <= 7/10.  It does not
// compute the transported graph or identify a source-manifold first hit.

namespace {

using rfsn::rigorous::Interval;
using rfsn::rigorous::Verdict;
using rfsn::rigorous::combine;
using rfsn::rigorous::intervalJson;
using rfsn::rigorous::verdictName;

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

Interval cube(const Interval& input) { return input * sqr(input); }

Interval hull(const Interval& left, const Interval& right) {
  return Interval(std::min(left.leftBound(), right.leftBound()),
                  std::max(left.rightBound(), right.rightBound()));
}

void include(bool initialized, Interval& target, const Interval& value) {
  target = initialized ? hull(target, value) : value;
}

Verdict strictPositive(const Interval& input) {
  if (input.leftBound() > 0.0) return Verdict::Pass;
  if (input.rightBound() <= 0.0) return Verdict::Fail;
  return Verdict::Inconclusive;
}

struct Evaluation {
  Interval q1Radicand;
  Interval q1;
  Interval pi;
  Interval omega;
  Interval centralP;
  Interval centralV;
  Interval centralQ;
  Interval sectionSpeed;
  Interval energyTransverse;
  Interval chartDeterminant;
  Interval spectralBaseScale;
  Interval spectralNormalScale;
  Interval spectralDeterminant;
  Interval regraphTransversality;
  Interval regraphSlopeBound;
};

Evaluation evaluate(const Interval& r, const Interval& a2,
                    const Interval& epsilon, const Interval& b,
                    const Interval& n) {
  const Interval two(2.0);
  const Interval three(3.0);
  const Interval six(6.0);
  const Interval m = Interval(4.0) + r * a2;
  if (m.leftBound() <= 0.0)
    throw std::runtime_error("central lower-face m is not positive");
  const Interval rootM = sqrt(m);
  const Interval m2 = sqr(m);
  const Interval m3 = cube(m);
  const Interval s = sqrt(epsilon);
  const Interval kappa = sqrt(s);
  const Interval r2 = sqr(r);
  const Interval r3 = cube(r);
  const Interval r5 = r3 * r2;
  const Interval r6 = cube(r2);
  const Interval a2Squared = sqr(a2);
  const Interval a2Cubed = a2 * a2Squared;
  const Interval a2Fourth = sqr(a2Squared);

  // At the lower face r1=r*sqrt(m), sigma=m^{-1/2}.  The following
  // forms have already eliminated all repeated r1/sigma correlations.
  const Interval x = s * r2 * m;
  const Interval denominator = two + x;
  const Interval qZero = sqrt(
      (Interval(8.0) + three * x) / (six * s));
  const Interval pZero = qZero / denominator;
  const Interval correction =
      r * a2 * (x + three) /
      (three * s * m * qZero * denominator);
  const Interval omegaZero =
      (x + Interval(4.0)) /
      (three * m * cube(denominator));
  const Interval lambda = sqrt(s * denominator);
  const Interval pi = pZero - correction + b + n;
  const Interval omega = omegaZero + lambda * (n - b);

  // Exact cancellation-free form of the positive H=0 root.  This is
  // V5(34), specialized only after setting r1=r*sqrt(m).
  const Interval qBar = qZero - denominator * correction;
  const Interval referenceResidual =
      x * (three * x + Interval(10.0)) /
          (six * s * m2 * cube(denominator)) -
      two * a2 * r *
          (sqr(x) + Interval(4.0) * x + two) /
          (three * s * m3 * cube(denominator)) +
      sqr(correction) * (Interval(1.0) / m2 - sqr(denominator)) +
      two * a2Cubed * r3 / (three * s * m3) +
      a2Fourth * r6 / (six * m3);
  const Interval referenceRadicand = sqr(qBar) + referenceResidual;
  if (referenceRadicand.leftBound() <= 0.0)
    throw std::runtime_error("reference q1 radicand is not positive");
  const Interval e = b + n;
  const Interval y = lambda * (n - b);
  const Interval perturbation =
      -two * y / (s * m) +
      e * (two * (pZero - correction) + e) / m2 +
      two * y * a2 * r / (s * m2);
  const Interval q1Radicand = referenceRadicand + perturbation;
  if (q1Radicand.leftBound() <= 0.0)
    throw std::runtime_error("q1 radicand is not positive");
  const Interval q1 = sqrt(q1Radicand);

  // Exact resolved-K1 to central transition on U=-4.
  const Interval centralP = -kappa * rootM * pi;
  const Interval centralV =
      r2 * a2Squared + s * r5 * a2Cubed / three - m2 -
      s * r2 * m3 / three + m * omega;
  const Interval centralQ = -kappa * m * rootM * q1;

  // The complete chart determinant is kappa*sigma^{-3}; Hhat=H.
  const Interval chartDeterminant = kappa * m * rootM;

  // The spectral (b,n)->(P,V) block has rows (-A,-A),(-K,K).
  // Its absolute determinant is 2*A*K.
  const Interval spectralBaseScale = kappa * rootM;
  const Interval spectralNormalScale = m * lambda;
  const Interval spectralDeterminant =
      two * spectralBaseScale * spectralNormalScale;

  // If n=g(b), |g'|<=rho, then
  //   -dV/db = K*(1-g') >= K*(1-rho),
  //   |dP/dV| <= (A/K)*(1+rho)/(1-rho).
  // The second expression uses monotonicity in g'; evaluating one shared
  // slope interval twice would discard this correlation.
  const Interval rho = rational(7, 10);
  const Interval regraphTransversality =
      spectralNormalScale * (Interval(1.0) - rho);
  const Interval regraphSlopeBound =
      spectralBaseScale / spectralNormalScale *
      (Interval(1.0) + rho) / (Interval(1.0) - rho);

  return {q1Radicand,
          q1,
          pi,
          omega,
          centralP,
          centralV,
          centralQ,
          -centralP,
          -centralQ,
          chartDeterminant,
          spectralBaseScale,
          spectralNormalScale,
          spectralDeterminant,
          regraphTransversality,
          regraphSlopeBound};
}

struct Aggregate {
  bool initialized = false;
  Interval q1Radicand;
  Interval q1;
  Interval pi;
  Interval omega;
  Interval centralP;
  Interval centralV;
  Interval centralQ;
  Interval sectionSpeed;
  Interval energyTransverse;
  Interval chartDeterminant;
  Interval spectralBaseScale;
  Interval spectralNormalScale;
  Interval spectralDeterminant;
  Interval regraphTransversality;
  Interval regraphSlopeBound;
};

void includeEvaluation(Aggregate& aggregate, const Evaluation& evaluation) {
  const bool was = aggregate.initialized;
  include(was, aggregate.q1Radicand, evaluation.q1Radicand);
  include(was, aggregate.q1, evaluation.q1);
  include(was, aggregate.pi, evaluation.pi);
  include(was, aggregate.omega, evaluation.omega);
  include(was, aggregate.centralP, evaluation.centralP);
  include(was, aggregate.centralV, evaluation.centralV);
  include(was, aggregate.centralQ, evaluation.centralQ);
  include(was, aggregate.sectionSpeed, evaluation.sectionSpeed);
  include(was, aggregate.energyTransverse, evaluation.energyTransverse);
  include(was, aggregate.chartDeterminant, evaluation.chartDeterminant);
  include(was, aggregate.spectralBaseScale,
          evaluation.spectralBaseScale);
  include(was, aggregate.spectralNormalScale,
          evaluation.spectralNormalScale);
  include(was, aggregate.spectralDeterminant,
          evaluation.spectralDeterminant);
  include(was, aggregate.regraphTransversality,
          evaluation.regraphTransversality);
  include(was, aggregate.regraphSlopeBound,
          evaluation.regraphSlopeBound);
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
    constexpr long kRSlabs = 8;
    constexpr long kA2Slabs = 32;
    constexpr long kEpsilonSlabs = 8;
    constexpr long kBSlabs = 8;
    constexpr long kNSlabs = 8;
    Aggregate aggregate;
    std::size_t cellCount = 0;

    for (long rIndex = 0; rIndex < kRSlabs; ++rIndex) {
      const Interval r = intervalFromRationals(
          kRSlabs + rIndex, 100 * kRSlabs,
          kRSlabs + rIndex + 1, 100 * kRSlabs);
      for (long a2Index = 0; a2Index < kA2Slabs; ++a2Index) {
        const Interval a2 = intervalFromRationals(
            -kA2Slabs + 2 * a2Index, 4 * kA2Slabs,
            -kA2Slabs + 2 * (a2Index + 1), 4 * kA2Slabs);
        for (long epsilonIndex = 0; epsilonIndex < kEpsilonSlabs;
             ++epsilonIndex) {
          const Interval epsilon = intervalFromRationals(
              4 * kEpsilonSlabs + 2 * epsilonIndex,
              5 * kEpsilonSlabs,
              4 * kEpsilonSlabs + 2 * (epsilonIndex + 1),
              5 * kEpsilonSlabs);
          for (long bIndex = 0; bIndex < kBSlabs; ++bIndex) {
            const Interval b = intervalFromRationals(
                -kBSlabs + 2 * bIndex, 10000 * kBSlabs,
                -kBSlabs + 2 * (bIndex + 1), 10000 * kBSlabs);
            for (long nIndex = 0; nIndex < kNSlabs; ++nIndex) {
              const Interval n = intervalFromRationals(
                  -kNSlabs + 2 * nIndex, 10000 * kNSlabs,
                  -kNSlabs + 2 * (nIndex + 1), 10000 * kNSlabs);
              includeEvaluation(
                  aggregate, evaluate(r, a2, epsilon, b, n));
              ++cellCount;
            }
          }
        }
      }
    }

    if (!aggregate.initialized)
      throw std::runtime_error("empty central attachment cover");

    std::vector<Obligation> obligations;
    Verdict root = strictPositive(aggregate.q1Radicand);
    root = combine(root, strictPositive(aggregate.q1));
    root = combine(root, strictPositive(aggregate.pi));
    obligations.push_back({
        "V5.CENTRAL.POSITIVE_ROOT", root,
        "The exact positive H=0 q1 branch and Pi remain positive on the complete lower-face tube",
        {{"q1_radicand", aggregate.q1Radicand},
         {"q1", aggregate.q1},
         {"Pi", aggregate.pi},
         {"Omega", aggregate.omega}}});

    const Interval pLowerMargin = aggregate.centralP + rational(6, 5);
    const Interval pUpperMargin = -rational(11, 10) - aggregate.centralP;
    const Interval vLowerMargin = aggregate.centralV + Interval(16.0);
    const Interval vUpperMargin = -rational(31, 2) - aggregate.centralV;
    const Interval qLowerMargin = aggregate.centralQ + rational(19, 2);
    const Interval qUpperMargin = -Interval(9.0) - aggregate.centralQ;
    Verdict patch = strictPositive(pLowerMargin);
    patch = combine(patch, strictPositive(pUpperMargin));
    patch = combine(patch, strictPositive(vLowerMargin));
    patch = combine(patch, strictPositive(vUpperMargin));
    patch = combine(patch, strictPositive(qLowerMargin));
    patch = combine(patch, strictPositive(qUpperMargin));
    obligations.push_back({
        "V5.CENTRAL.FIXED_PATCH", patch,
        "The exact U=-4 transition lies strictly inside P in [-6/5,-11/10], V in [-16,-31/2], Q in [-19/2,-9]",
        {{"P", aggregate.centralP},
         {"V", aggregate.centralV},
         {"Q", aggregate.centralQ},
         {"P_lower_margin", pLowerMargin},
         {"P_upper_margin", pUpperMargin},
         {"V_lower_margin", vLowerMargin},
         {"V_upper_margin", vUpperMargin},
         {"Q_lower_margin", qLowerMargin},
         {"Q_upper_margin", qUpperMargin}}});

    Verdict transverse = strictPositive(aggregate.sectionSpeed);
    transverse = combine(
        transverse, strictPositive(aggregate.energyTransverse));
    obligations.push_back({
        "V5.CENTRAL.TRANSVERSALITY", transverse,
        "The U=-4 section speed |P| and the energy-direction coefficient |Q| are uniformly nonzero",
        {{"section_speed_abs_P", aggregate.sectionSpeed},
         {"energy_transverse_abs_Q", aggregate.energyTransverse}}});

    Verdict regularity = strictPositive(aggregate.chartDeterminant);
    regularity = combine(
        regularity, strictPositive(aggregate.spectralDeterminant));
    obligations.push_back({
        "V5.CENTRAL.CHART_REGULARITY", regularity,
        "The exact transition has determinant kappa*sigma^(-3)>0, Hhat=H, and the spectral (b,n)-to-(P,V) block has absolute determinant 2*A*K>0",
        {{"chart_determinant_kappa_sigma_minus_3",
          aggregate.chartDeterminant},
         {"spectral_base_scale_A", aggregate.spectralBaseScale},
         {"spectral_normal_scale_K", aggregate.spectralNormalScale},
         {"spectral_block_abs_determinant_2AK",
          aggregate.spectralDeterminant},
         {"d_Hhat_d_H", Interval(1.0)}}});

    const Interval regraphCap = rational(2221, 1000);
    const Interval regraphCapMargin =
        regraphCap - aggregate.regraphSlopeBound;
    Verdict regraph = strictPositive(aggregate.regraphTransversality);
    regraph = combine(regraph, strictPositive(regraphCapMargin));
    obligations.push_back({
        "V5.CENTRAL.SLOPE_7_10_REGRAPH", regraph,
        "Every C1 lower-face K1 graph n=g(b) with |g'|<=7/10 maps transversely to a central graph P=G(V) with |G_V|<2221/1000",
        {{"K1_graph_slope", rational(7, 10)},
         {"minus_dV_db_lower_bound", aggregate.regraphTransversality},
         {"abs_G_V_upper_bound", aggregate.regraphSlopeBound},
         {"abs_G_V_cap", regraphCap},
         {"abs_G_V_cap_margin", regraphCapMargin}}});

    Verdict mathematical = Verdict::Pass;
    for (const auto& obligation : obligations)
      mathematical = combine(mathematical, obligation.status);
    const Verdict status = combine(rounding.status, mathematical);

    std::cout
        << "{\"schema_version\":\"rfsn-vdp-v5-central-attachment-probe/1\","
        << "\"status\":\"" << verdictName(status) << "\","
        << "\"mathematical_status\":\"" << verdictName(mathematical)
        << "\",\"claim_bearing\":false,"
        << "\"box_id\":\"vdp-positive-box-v2\","
        << "\"scope\":\"ZERO_ENERGY_K1_TO_CENTRAL_LOWER_FACE\","
        << "\"section\":\"U=-4\","
        << "\"fixed_patch\":{\"P\":[\"-6/5\",\"-11/10\"],"
           "\"V\":[\"-16\",\"-31/2\"],"
           "\"Q\":[\"-19/2\",\"-9\"]},"
        << "\"tube\":{\"b\":"
        << intervalJson(Interval(-rational(1, 10000).rightBound(),
                                 rational(1, 10000).rightBound()))
        << ",\"n\":"
        << intervalJson(Interval(-rational(1, 10000).rightBound(),
                                 rational(1, 10000).rightBound()))
        << ",\"graph_slope\":" << intervalJson(rational(7, 10)) << "},"
        << "\"cover\":{\"r_slabs\":" << kRSlabs
        << ",\"a2_slabs\":" << kA2Slabs
        << ",\"epsilon_slabs\":" << kEpsilonSlabs
        << ",\"b_slabs\":" << kBSlabs
        << ",\"n_slabs\":" << kNSlabs
        << ",\"cell_count\":" << cellCount << "},"
        << "\"rounding_self_test\":"
        << rfsn::rigorous::roundingReportJson(rounding) << ','
        << "\"claim_boundary\":{"
        << "\"proved_scope\":\"exact H=0 lower-face patch inclusion, coordinate regularity, transversality, and universal slope-7/10 central regraph\","
        << "\"open_scope\":[\"explicit enclosure of the transported lower graph\","
           "\"source first hit\",\"V5 scalar incidence\"]},"
        << "\"obligations\":[";
    for (std::size_t index = 0; index < obligations.size(); ++index) {
      if (index) std::cout << ',';
      std::cout << obligationJson(obligations[index]);
    }
    std::cout << "]}\n";
    return status == Verdict::Pass ? 0 : 1;
  } catch (const std::exception& error) {
    std::cerr << "vdp_v5_central_attachment_probe: "
              << error.what() << '\n';
    return 2;
  }
}
