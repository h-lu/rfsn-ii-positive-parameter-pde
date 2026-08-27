#ifndef RFSN_RIGOROUS_EXACT_POLYNOMIAL_HPP
#define RFSN_RIGOROUS_EXACT_POLYNOMIAL_HPP

#include <array>
#include <cstdint>
#include <map>
#include <numeric>
#include <stdexcept>

namespace rfsn::rigorous::exact {

constexpr std::size_t kVariableCount = 7;
using Monomial = std::array<int, kVariableCount>;

struct Rational {
  std::int64_t numerator = 0;
  std::int64_t denominator = 1;

  Rational() = default;
  Rational(std::int64_t n) : numerator(n), denominator(1) {}
  Rational(std::int64_t n, std::int64_t d) : numerator(n), denominator(d) {
    normalize();
  }

  void normalize() {
    if (denominator == 0) throw std::invalid_argument("zero rational denominator");
    if (denominator < 0) {
      numerator = -numerator;
      denominator = -denominator;
    }
    const auto divisor = std::gcd(numerator < 0 ? -numerator : numerator,
                                  denominator);
    numerator /= divisor;
    denominator /= divisor;
  }

  friend Rational operator+(const Rational& x, const Rational& y) {
    return Rational(x.numerator * y.denominator + y.numerator * x.denominator,
                    x.denominator * y.denominator);
  }
  friend Rational operator-(const Rational& x, const Rational& y) {
    return Rational(x.numerator * y.denominator - y.numerator * x.denominator,
                    x.denominator * y.denominator);
  }
  friend Rational operator-(const Rational& x) {
    return Rational(-x.numerator, x.denominator);
  }
  friend Rational operator*(const Rational& x, const Rational& y) {
    return Rational(x.numerator * y.numerator, x.denominator * y.denominator);
  }
  friend bool operator==(const Rational& x, const Rational& y) {
    return x.numerator == y.numerator && x.denominator == y.denominator;
  }
};

class Polynomial {
 public:
  Polynomial() = default;
  explicit Polynomial(const Rational& value) {
    if (value.numerator != 0) terms_[Monomial{}] = value;
  }

  static Polynomial variable(std::size_t index, int exponent = 1) {
    if (index >= kVariableCount) throw std::out_of_range("polynomial variable");
    Monomial monomial{};
    monomial[index] = exponent;
    Polynomial result;
    result.terms_[monomial] = Rational(1);
    return result;
  }

  Polynomial derivative(std::size_t index) const {
    Polynomial result;
    for (const auto& [monomial, coefficient] : terms_) {
      const int exponent = monomial[index];
      if (exponent == 0) continue;
      Monomial differentiated = monomial;
      differentiated[index] -= 1;
      result.add(differentiated, coefficient * Rational(exponent));
    }
    return result;
  }

  Polynomial signSubstitution(const std::array<int, kVariableCount>& signs) const {
    Polynomial result;
    for (const auto& [monomial, coefficient] : terms_) {
      int sign = 1;
      for (std::size_t index = 0; index < kVariableCount; ++index) {
        if (signs[index] == -1 && monomial[index] % 2 != 0) sign = -sign;
      }
      result.add(monomial, coefficient * Rational(sign));
    }
    return result;
  }

  bool isZero() const { return terms_.empty(); }

  friend Polynomial operator+(const Polynomial& left, const Polynomial& right) {
    Polynomial result = left;
    for (const auto& [monomial, coefficient] : right.terms_)
      result.add(monomial, coefficient);
    return result;
  }
  friend Polynomial operator-(const Polynomial& left, const Polynomial& right) {
    Polynomial result = left;
    for (const auto& [monomial, coefficient] : right.terms_)
      result.add(monomial, -coefficient);
    return result;
  }
  friend Polynomial operator-(const Polynomial& value) {
    return Polynomial(Rational(-1)) * value;
  }
  friend Polynomial operator*(const Polynomial& left, const Polynomial& right) {
    Polynomial result;
    for (const auto& [leftMonomial, leftCoefficient] : left.terms_) {
      for (const auto& [rightMonomial, rightCoefficient] : right.terms_) {
        Monomial product{};
        for (std::size_t index = 0; index < kVariableCount; ++index)
          product[index] = leftMonomial[index] + rightMonomial[index];
        result.add(product, leftCoefficient * rightCoefficient);
      }
    }
    return result;
  }
  friend bool operator==(const Polynomial& left, const Polynomial& right) {
    return left.terms_ == right.terms_;
  }

 private:
  void add(const Monomial& monomial, const Rational& coefficient) {
    if (coefficient.numerator == 0) return;
    const auto iterator = terms_.find(monomial);
    if (iterator == terms_.end()) {
      terms_[monomial] = coefficient;
    } else {
      const Rational sum = iterator->second + coefficient;
      if (sum.numerator == 0)
        terms_.erase(iterator);
      else
        iterator->second = sum;
    }
  }

  std::map<Monomial, Rational> terms_;
};

inline Polynomial power(Polynomial value, int exponent) {
  if (exponent < 0) throw std::invalid_argument("negative polynomial power");
  Polynomial result(Rational(1));
  while (exponent > 0) {
    if (exponent & 1) result = result * value;
    exponent >>= 1;
    if (exponent) value = value * value;
  }
  return result;
}

}  // namespace rfsn::rigorous::exact

#endif
