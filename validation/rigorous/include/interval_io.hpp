#ifndef RFSN_RIGOROUS_INTERVAL_IO_HPP
#define RFSN_RIGOROUS_INTERVAL_IO_HPP

#include <capd/intervals/lib.h>

#include <cmath>
#include <cstring>
#include <iomanip>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>

namespace rfsn::rigorous {

using Interval = capd::interval;

inline std::string jsonEscape(const std::string& value) {
  std::ostringstream output;
  for (const unsigned char character : value) {
    switch (character) {
      case '"': output << "\\\""; break;
      case '\\': output << "\\\\"; break;
      case '\b': output << "\\b"; break;
      case '\f': output << "\\f"; break;
      case '\n': output << "\\n"; break;
      case '\r': output << "\\r"; break;
      case '\t': output << "\\t"; break;
      default:
        if (character < 0x20) {
          output << "\\u" << std::hex << std::setw(4) << std::setfill('0')
                 << static_cast<int>(character) << std::dec;
        } else {
          output << character;
        }
    }
  }
  return output.str();
}

inline std::string hexDouble(double value) {
  if (!std::isfinite(value)) {
    throw std::runtime_error("certificate endpoint is not finite");
  }
  std::ostringstream output;
  output << std::hexfloat << value;
  return output.str();
}

inline std::string intervalJson(const Interval& value) {
  return std::string("{\"lower_hex\":\"") + hexDouble(value.leftBound())
      + "\",\"upper_hex\":\"" + hexDouble(value.rightBound())
      + "\",\"endpoint_format\":\"IEEE754_BINARY64_HEX\"}";
}

inline Interval exactRational(const std::string& numerator,
                              const std::string& denominator) {
  if (denominator.empty() || denominator[0] == '-') {
    throw std::invalid_argument("rational denominator must be positive");
  }
  const Interval bottom(denominator, denominator);
  if (bottom.leftBound() <= 0.) {
    throw std::invalid_argument("rational denominator must be strictly positive");
  }
  // FILIB's directed division may widen the mathematically exact quotient
  // 0/q to one subnormal ulp below zero.  Preserve the exact anchor face
  // r=0 instead of silently turning the bridge into a negative-r interval.
  if (numerator == "0" || numerator == "-0") return Interval(0.0);
  const Interval top(numerator, numerator);
  return top / bottom;
}

inline bool bitEqual(double left, double right) {
  return std::memcmp(&left, &right, sizeof(double)) == 0;
}

}  // namespace rfsn::rigorous

#endif
