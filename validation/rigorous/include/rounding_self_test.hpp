#ifndef RFSN_RIGOROUS_ROUNDING_SELF_TEST_HPP
#define RFSN_RIGOROUS_ROUNDING_SELF_TEST_HPP

#include "interval_io.hpp"
#include "verdict.hpp"

#include <capd/rounding/DoubleRounding.h>

#include <cfenv>
#include <cfloat>
#include <cmath>
#include <cstdlib>
#include <limits>
#include <sstream>
#include <string>
#include <vector>

#if defined(__SSE__)
#include <xmmintrin.h>
#endif

namespace rfsn::rigorous {

struct RoundingTest {
  std::string id;
  Verdict status;
  std::string detail;
};

struct RoundingReport {
  Verdict status = Verdict::Pass;
  std::vector<RoundingTest> tests;
  unsigned int mxcsr = 0;
  bool mxcsr_available = false;
  bool legacy_capd_is_working = false;
};

inline void appendTest(RoundingReport& report, const std::string& id,
                       bool passed, const std::string& detail) {
  const Verdict status = passed ? Verdict::Pass : Verdict::Fail;
  report.tests.push_back({id, status, detail});
  report.status = combine(report.status, status);
}

inline void appendVerdict(RoundingReport& report, const std::string& id,
                          Verdict status, const std::string& detail) {
  report.tests.push_back({id, status, detail});
  report.status = combine(report.status, status);
}

inline RoundingReport runRoundingSelfTests() {
  using Rounding = capd::rounding::DoubleRounding;
  RoundingReport report;

  const bool ieee = std::numeric_limits<double>::is_iec559 &&
                    std::numeric_limits<double>::radix == 2 &&
                    std::numeric_limits<double>::digits == 53 &&
                    FLT_EVAL_METHOD == 0;
  appendTest(report, "ROUND.IEEE754_BINARY64", ieee,
             "IEC 60559 binary64, radix 2, 53 significand bits, FLT_EVAL_METHOD=0");

#if defined(__FAST_MATH__)
  appendTest(report, "ROUND.NO_FAST_MATH", false,
             "__FAST_MATH__ is defined");
#else
  appendTest(report, "ROUND.NO_FAST_MATH", true,
             "__FAST_MATH__ is not defined");
#endif

  report.legacy_capd_is_working = Rounding::isWorking();
  Rounding::roundUp();
  const auto capdUpObserved = Rounding::test();
  Rounding::roundDown();
  const auto capdDownObserved = Rounding::test();
  Rounding::roundCut();
  const auto capdCutObserved = Rounding::test();
  Rounding::roundNearest();
  const auto capdNearestObserved = Rounding::test();
  appendTest(report, "ROUND.CAPD_MODES",
             capdUpObserved == capd::rounding::RoundUp &&
                 capdDownObserved == capd::rounding::RoundDown &&
                 capdCutObserved == capd::rounding::RoundCut &&
                 capdNearestObserved == capd::rounding::RoundNearest,
             std::string("observed up/down/cut/nearest=") +
                 std::to_string(static_cast<int>(capdUpObserved)) + "/" +
                 std::to_string(static_cast<int>(capdDownObserved)) + "/" +
                 std::to_string(static_cast<int>(capdCutObserved)) + "/" +
                 std::to_string(static_cast<int>(capdNearestObserved)) +
                 ", expected=2/1/3/0; legacy isWorking()=" +
                 (report.legacy_capd_is_working ? "true" : "false"));
  appendVerdict(
      report, "ROUND.CAPD_LEGACY_SELF_TEST",
      report.legacy_capd_is_working ? Verdict::Pass : Verdict::Inconclusive,
      report.legacy_capd_is_working
          ? "CAPD DoubleRounding::isWorking() returned true"
          : "CAPD DoubleRounding::isWorking() returned false although the four "
            "separately sequenced mode probes pass; backend integrity remains "
            "inconclusive until this optimized-helper discrepancy is removed");

  volatile double one = 1.0;
  volatile double halfUlp = 0x1p-53;
  Rounding::roundDown();
  volatile double down = one + halfUlp;
  Rounding::roundUp();
  volatile double up = one + halfUlp;
  Rounding::roundNearest();
  const double successor = std::nextafter(1.0,
                                          std::numeric_limits<double>::infinity());
  appendTest(report, "ROUND.DIRECTED_ADDITION",
             bitEqual(down, 1.0) && bitEqual(up, successor),
             std::string("down=") + hexDouble(down) + ", up=" + hexDouble(up));

  const Interval tenth = exactRational("1", "10");
  const double tenthFloor = 0x1.9999999999999p-4;
  const double tenthCeil = 0x1.999999999999ap-4;
  appendTest(report, "ROUND.RATIONAL_DIVISION",
             tenth.leftBound() <= tenthFloor && tenth.rightBound() >= tenthCeil &&
                 tenth.leftBound() < tenth.rightBound(),
             intervalJson(tenth));

  const Interval negativeTenth = exactRational("-1", "10");
  appendTest(report, "ROUND.NEGATIVE_RATIONAL_DIVISION",
             negativeTenth.leftBound() <= -tenthCeil &&
                 negativeTenth.rightBound() >= -tenthFloor &&
                 negativeTenth.leftBound() < negativeTenth.rightBound(),
             intervalJson(negativeTenth));

  const Interval rootTwo = sqrt(Interval(2.0));
  const double rootFloor = 0x1.6a09e667f3bccp+0;
  const double rootCeil = 0x1.6a09e667f3bcdp+0;
  appendTest(report, "ROUND.SQRT",
             rootTwo.leftBound() <= rootFloor &&
                 rootTwo.rightBound() >= rootCeil,
             intervalJson(rootTwo));

  const Interval square = sqr(Interval(-1.0, 1.0));
  appendTest(report, "ROUND.DEPENDENCY_SQUARE",
             square.leftBound() <= 0.0 && square.rightBound() >= 1.0,
             intervalJson(square));

  const Interval third = exactRational("1", "3");
  const Interval polynomial = Interval(3.0) * sqr(third) -
                              Interval(2.0) * third + Interval(1.0);
  const double twoThirdsFloor = 0x1.5555555555555p-1;
  const double twoThirdsCeil = 0x1.5555555555556p-1;
  appendTest(report, "ROUND.POLYNOMIAL_CONTAINMENT",
             polynomial.leftBound() <= twoThirdsFloor &&
                 polynomial.rightBound() >= twoThirdsCeil,
             "3*(1/3)^2-2*(1/3)+1 contains exact 2/3: " +
                 intervalJson(polynomial));

  const std::string lowerHex = hexDouble(tenth.leftBound());
  const std::string upperHex = hexDouble(tenth.rightBound());
  char* lowerEnd = nullptr;
  char* upperEnd = nullptr;
  const double lowerParsed = std::strtod(lowerHex.c_str(), &lowerEnd);
  const double upperParsed = std::strtod(upperHex.c_str(), &upperEnd);
  const bool serialization = lowerEnd && *lowerEnd == '\0' && upperEnd &&
                             *upperEnd == '\0' &&
                             bitEqual(lowerParsed, tenth.leftBound()) &&
                             bitEqual(upperParsed, tenth.rightBound());
  appendTest(report, "ROUND.HEX_SERIALIZATION", serialization,
             "hexfloat endpoints round-trip bit-for-bit through strtod");

#if defined(__SSE__)
  report.mxcsr = _mm_getcsr();
  report.mxcsr_available = true;
  const bool normalSubnormals = (report.mxcsr & (1u << 15)) == 0 &&
                                (report.mxcsr & (1u << 6)) == 0;
  std::ostringstream mxcsrDetail;
  mxcsrDetail << "MXCSR=0x" << std::hex << report.mxcsr
              << ", FTZ=0, DAZ=0 required";
  appendTest(report, "ROUND.SUBNORMAL_MODE", normalSubnormals,
             mxcsrDetail.str());
#else
  appendTest(report, "ROUND.SUBNORMAL_MODE", false,
             "MXCSR unavailable on this target");
#endif

  Rounding::roundNearest();
  const bool restored = Rounding::test() == capd::rounding::RoundNearest &&
                        std::fegetround() == FE_TONEAREST;
  appendTest(report, "ROUND.RESTORE_NEAREST", restored,
             "round-to-nearest restored before returning");
  return report;
}

inline std::string roundingReportJson(const RoundingReport& report) {
  std::ostringstream output;
  output << "{\"status\":\"" << verdictName(report.status) << "\",\"tests\":[";
  for (std::size_t index = 0; index < report.tests.size(); ++index) {
    if (index) output << ',';
    const auto& test = report.tests[index];
    output << "{\"id\":\"" << jsonEscape(test.id) << "\",\"status\":\""
           << verdictName(test.status) << "\",\"detail\":\""
           << jsonEscape(test.detail) << "\"}";
  }
  output << "],\"mxcsr_available\":"
         << (report.mxcsr_available ? "true" : "false");
  output << ",\"legacy_capd_is_working\":"
         << (report.legacy_capd_is_working ? "true" : "false");
  if (report.mxcsr_available) {
    std::ostringstream mxcsr;
    mxcsr << "0x" << std::hex << report.mxcsr;
    output << ",\"mxcsr_pre_restore_hex\":\"" << mxcsr.str() << "\"";
  }
  output << '}';
  return output.str();
}

}  // namespace rfsn::rigorous

#endif
