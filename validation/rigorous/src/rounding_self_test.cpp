#include "rounding_self_test.hpp"

#include <exception>
#include <iostream>

int main() {
  try {
    const auto report = rfsn::rigorous::runRoundingSelfTests();
    std::cout << "{\"schema_version\":\"rfsn-rounding-probe/1\","
              << "\"rounding_self_test\":"
              << rfsn::rigorous::roundingReportJson(report) << "}\n";
    return report.status == rfsn::rigorous::Verdict::Pass ? 0 : 1;
  } catch (const std::exception& error) {
    std::cout << "{\"schema_version\":\"rfsn-rounding-probe/1\","
              << "\"rounding_self_test\":{\"status\":\"INCONCLUSIVE\","
              << "\"tests\":[{\"id\":\"ROUND.EXCEPTION\","
              << "\"status\":\"INCONCLUSIVE\",\"detail\":\""
              << rfsn::rigorous::jsonEscape(error.what()) << "\"}]}}\n";
    return 2;
  }
}
