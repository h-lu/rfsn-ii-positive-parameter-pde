#ifndef RFSN_RIGOROUS_VERDICT_HPP
#define RFSN_RIGOROUS_VERDICT_HPP

#include <string>

namespace rfsn::rigorous {

enum class Verdict { Pass, Fail, Inconclusive };

inline const char* verdictName(Verdict verdict) {
  switch (verdict) {
    case Verdict::Pass:
      return "PASS";
    case Verdict::Fail:
      return "FAIL";
    case Verdict::Inconclusive:
      return "INCONCLUSIVE";
  }
  return "INCONCLUSIVE";
}

inline Verdict combine(Verdict left, Verdict right) {
  if (left == Verdict::Fail || right == Verdict::Fail) return Verdict::Fail;
  if (left == Verdict::Inconclusive || right == Verdict::Inconclusive)
    return Verdict::Inconclusive;
  return Verdict::Pass;
}

}  // namespace rfsn::rigorous

#endif

