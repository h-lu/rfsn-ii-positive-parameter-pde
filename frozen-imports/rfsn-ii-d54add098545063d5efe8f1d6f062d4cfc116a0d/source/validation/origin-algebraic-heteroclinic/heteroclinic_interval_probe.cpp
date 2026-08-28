#include <algorithm>
#include <array>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>

#include "capd/capdlib.h"
#include "heteroclinic_centres.hpp"
#include "../future-target-fold/tail_graph_generated.hpp"
#include "unstable_graph_terms.hpp"
#include "../future-target-fold/weighted_tail_generated.hpp"

using namespace capd;

namespace {

constexpr int kSegments = papera_heteroclinic_centres::kSegments;
constexpr int kDimension = 4;
constexpr int kUnknowns = kDimension * (kSegments + 1);
constexpr double kStep =
  papera_heteroclinic_centres::kFinalTime / kSegments;
constexpr double kSourceValueError = 1e-20;
constexpr double kSourceSlopeError = 1e-18;
constexpr double kTargetValueError = 1e-8;
constexpr double kTargetSlopeError = 1e-5;

int column(int node, int component) {
  return kDimension * node + component;
}

double absUpper(const interval& value) {
  return std::max(std::abs(value.leftBound()),
                  std::abs(value.rightBound()));
}

interval integerPower(interval value, int exponent) {
  interval result(1.);
  for(int index = 0; index < exponent; ++index) result *= value;
  return result;
}

int fallingFactorial(int exponent, int derivatives) {
  int result = 1;
  for(int index = 0; index < derivatives; ++index)
    result *= exponent - index;
  return result;
}

interval coefficient(const PolynomialTerm& term) {
  interval result = interval(term.numerator, term.numerator)
    / interval(term.denominator, term.denominator);
  if(term.times_sqrt_two) result *= sqrt(interval(2.));
  return result;
}

template<std::size_t Size>
interval polynomial(const PolynomialTerm (&terms)[Size],
                    const interval& x, const interval& y,
                    int dx = 0, int dy = 0) {
  interval result(0.);
  for(const auto& term : terms) {
    if(term.px < dx || term.py < dy) continue;
    result += coefficient(term)
      * interval(static_cast<double>(fallingFactorial(term.px, dx)))
      * interval(static_cast<double>(fallingFactorial(term.py, dy)))
      * integerPower(x, term.px - dx)
      * integerPower(y, term.py - dy);
  }
  return result;
}

IVector node(const IVector& all, int index) {
  IVector result(kDimension);
  for(int component = 0; component < kDimension; ++component)
    result[component] = all[column(index, component)];
  return result;
}

IVector centreVector() {
  IVector result(kUnknowns);
  for(int n = 0; n <= kSegments; ++n)
    for(int component = 0; component < kDimension; ++component)
      result[column(n, component)] =
        papera_heteroclinic_centres::kCentres[n][component];
  return result;
}

double radiusAt(int nodeIndex, int component, bool robust) {
  const double x = static_cast<double>(nodeIndex) / kSegments;
  if(!robust) return 2e-9;
  switch(component) {
    case 0: return 2e-9 + 5e-7 * std::pow(x, 6);
    case 1: return 2e-9 + 2e-6 * std::pow(x, 8);
    case 2: return 2e-9 + 8e-6 * std::pow(x, 5);
    case 3: return 2e-9 + 2e-6 * std::pow(x, 5);
  }
  throw std::runtime_error("invalid component");
}

IVector boxAround(const IVector& centre, bool robust) {
  IVector result(kUnknowns);
  for(int i = 0; i < kUnknowns; ++i) {
    const double midpoint = centre[i].mid().leftBound();
    const double radius = radiusAt(i / kDimension, i % kDimension, robust);
    result[i] = interval(midpoint - radius, midpoint + radius);
  }
  return result;
}

struct Coordinates {
  interval u1, u2, s1, s2;
  std::array<interval,4> du1, du2, ds1, ds2;
};

Coordinates sourceCoordinates(const IVector& z) {
  const interval c = interval(1.) / sqrt(interval(2.));
  Coordinates result;
  result.u1 = (z[0] + c * (z[1] + z[3])) / interval(2.);
  result.s1 = (z[0] - c * (z[1] + z[3])) / interval(2.);
  result.u2 = (z[2] + c * (z[3] - z[1])) / interval(2.);
  result.s2 = (z[2] - c * (z[3] - z[1])) / interval(2.);
  result.du1 = {interval(.5), c / interval(2.), interval(0.), c / interval(2.)};
  result.ds1 = {interval(.5), -c / interval(2.), interval(0.), -c / interval(2.)};
  result.du2 = {interval(0.), -c / interval(2.), interval(.5), c / interval(2.)};
  result.ds2 = {interval(0.), c / interval(2.), interval(.5), -c / interval(2.)};
  return result;
}

struct SourceRows {
  std::array<interval,3> value;
  std::array<std::array<interval,4>,3> gradient;
};

SourceRows sourceRows(const IVector& point, const IVector& box,
                      bool robust) {
  const Coordinates p = sourceCoordinates(point);
  const Coordinates z = sourceCoordinates(box);
  SourceRows result{};
  result.value[0] = sqr(p.u1) + sqr(p.u2) - interval("0.0001", "0.0001");
  result.value[1] = p.s1 - polynomial(kH1Terms, p.u1, p.u2);
  result.value[2] = p.s2 - polynomial(kH2Terms, p.u1, p.u2);
  if(robust) {
    result.value[1] += interval(-kSourceValueError, kSourceValueError);
    result.value[2] += interval(-kSourceValueError, kSourceValueError);
  }

  const interval h1x = polynomial(kH1Terms, z.u1, z.u2, 1, 0);
  const interval h1y = polynomial(kH1Terms, z.u1, z.u2, 0, 1);
  const interval h2x = polynomial(kH2Terms, z.u1, z.u2, 1, 0);
  const interval h2y = polynomial(kH2Terms, z.u1, z.u2, 0, 1);
  const interval slope = robust
    ? interval(-kSourceSlopeError, kSourceSlopeError) : interval(0.);
  for(int i = 0; i < 4; ++i) {
    result.gradient[0][i] = interval(2.) * z.u1 * z.du1[i]
      + interval(2.) * z.u2 * z.du2[i];
    result.gradient[1][i] = z.ds1[i] - h1x * z.du1[i]
      - h1y * z.du2[i] - slope * z.du1[i] - slope * z.du2[i];
    result.gradient[2][i] = z.ds2[i] - h2x * z.du1[i]
      - h2y * z.du2[i] - slope * z.du1[i] - slope * z.du2[i];
  }
  return result;
}

struct Jet4 {
  interval value;
  std::array<interval,4> gradient;

  Jet4() : value(0.) { gradient.fill(interval(0.)); }
  Jet4(int x) : value(x) { gradient.fill(interval(0.)); }
  Jet4(long x) : value(static_cast<double>(x)) { gradient.fill(interval(0.)); }
  Jet4(long long x) : value(static_cast<double>(x)) {
    gradient.fill(interval(0.));
  }
  Jet4(double x) : value(x) { gradient.fill(interval(0.)); }
  Jet4(const interval& x) : value(x) { gradient.fill(interval(0.)); }

  static Jet4 variable(const interval& x, int index) {
    Jet4 result(x);
    result.gradient[index] = 1.;
    return result;
  }
  Jet4& operator+=(const Jet4& other) {
    value += other.value;
    for(int i = 0; i < 4; ++i) gradient[i] += other.gradient[i];
    return *this;
  }
  Jet4& operator-=(const Jet4& other) {
    value -= other.value;
    for(int i = 0; i < 4; ++i) gradient[i] -= other.gradient[i];
    return *this;
  }
};

Jet4 operator+(Jet4 left, const Jet4& right) { return left += right; }
Jet4 operator-(Jet4 left, const Jet4& right) { return left -= right; }
Jet4 operator-(const Jet4& x) {
  Jet4 result;
  result.value = -x.value;
  for(int i = 0; i < 4; ++i) result.gradient[i] = -x.gradient[i];
  return result;
}
Jet4 operator*(const Jet4& x, const Jet4& y) {
  Jet4 result;
  result.value = x.value * y.value;
  for(int i = 0; i < 4; ++i)
    result.gradient[i] = x.gradient[i] * y.value
      + x.value * y.gradient[i];
  return result;
}
Jet4 reciprocal(const Jet4& x) {
  Jet4 result;
  result.value = interval(1.) / x.value;
  for(int i = 0; i < 4; ++i)
    result.gradient[i] = -x.gradient[i] / sqr(x.value);
  return result;
}
Jet4 operator/(const Jet4& x, const Jet4& y) { return x * reciprocal(y); }
Jet4 sqrt(const Jet4& x) {
  using std::sqrt;
  Jet4 result;
  result.value = sqrt(x.value);
  for(int i = 0; i < 4; ++i)
    result.gradient[i] = x.gradient[i] / (interval(2.) * result.value);
  return result;
}

struct TargetCoordinates {
  Jet4 residual;
  std::array<Jet4,3> base;
};

TargetCoordinates targetCoordinates(const IVector& z) {
  const Jet4 U = Jet4::variable(z[0], 0);
  const Jet4 P = Jet4::variable(z[1], 1);
  const Jet4 V = Jet4::variable(z[2], 2);
  const Jet4 Q = Jet4::variable(z[3], 3);
  const Jet4 e = -Jet4(1) / U;
  const Jet4 e32 = e * sqrt(e);
  const Jet4 p = P * e32;
  const Jet4 q = Q * e32;
  const Jet4 omega = Jet4(1) + V * e * e;
  const Jet4 d = q + Jet4(2) / sqrt(Jet4(3));
  const Jet4 c = d - sqrt(Jet4(3)) * omega / Jet4(2);
  return {p - papera_tail::h7(e, d, omega), {e, c, omega}};
}

struct TargetRow {
  interval value;
  std::array<interval,4> gradient;
};

TargetRow targetRow(const IVector& point, const IVector& box, bool robust) {
  const TargetCoordinates p = targetCoordinates(point);
  const TargetCoordinates z = targetCoordinates(box);
  TargetRow result;
  result.value = p.residual.value;
  if(robust)
    result.value += interval(-kTargetValueError, kTargetValueError);
  const interval slope = robust
    ? interval(-kTargetSlopeError, kTargetSlopeError) : interval(0.);
  for(int i = 0; i < 4; ++i) {
    result.gradient[i] = z.residual.gradient[i];
    for(int base = 0; base < 3; ++base)
      result.gradient[i] -= slope * z.base[base].gradient[i];
  }
  return result;
}

struct PhysicalContract {
  interval e, a, b, graphEnergy;
};

PhysicalContract terminalPhysicalContract(const IVector& terminalBox) {
  const interval e = -interval(1.) / terminalBox[0];
  const interval e32 = e * sqrt(e);
  const interval d = terminalBox[3] * e32
    + interval(2.) / sqrt(interval(3.));
  const interval omega = interval(1.) + terminalBox[2] * e * e;
  const interval a = d / (e * e * e);
  const interval b = (omega - e * e / interval(6.))
    / (e * e * e * e);
  const interval graphEnergy = papera_weighted_tail::energy(
    e, a, b, interval(-2., 2.));
  if(!(e.leftBound() > 0. && e.rightBound() < .06
       && a.leftBound() > -.0065 && a.rightBound() < .0065
       && b.leftBound() > -.01 && b.rightBound() < .01
       && graphEnergy.leftBound() > -.012
       && graphEnergy.rightBound() < .012))
    throw std::runtime_error("terminal X leaves signed physical corridor");
  return {e, a, b, graphEnergy};
}

} // namespace

int main(int argc, char** argv) {
  try {
    const bool robust = argc == 2 && std::string(argv[1]) == "--robust";
    const IVector centre = centreVector();
    const IVector X = boxAround(centre, robust);
    const PhysicalContract physical = terminalPhysicalContract(
      node(X, kSegments));

    IMap field("var:U,P,V,Q;fun:P,-U*U-V,Q,U;");
    IOdeSolver solver(field, 25);
    solver.setAbsoluteTolerance(1e-14);
    solver.setRelativeTolerance(1e-14);

    IVector residual(kUnknowns);
    IMatrix derivative(kUnknowns, kUnknowns);
    derivative.clear();
    double residualSup = 0.;
    for(int segment = 0; segment < kSegments; ++segment) {
      const IVector initialCentre = node(centre, segment);
      const IVector initialBox = node(X, segment);
      ITimeMap c0TimeMap(solver);
      C0HOTripletonSet c0Set(initialCentre);
      const IVector imageCentre = c0TimeMap(interval(kStep), c0Set);
      ITimeMap c1TimeMap(solver);
      C1HORect2Set c1Set(initialBox);
      c1TimeMap(interval(kStep), c1Set);
      const IMatrix monodromy = (IMatrix)c1Set;
      const IVector nextCentre = node(centre, segment + 1);
      for(int output = 0; output < kDimension; ++output) {
        const int row = kDimension * segment + output;
        residual[row] = nextCentre[output] - imageCentre[output];
        residualSup = std::max(residualSup, absUpper(residual[row]));
        for(int input = 0; input < kDimension; ++input)
          derivative[row][column(segment, input)] =
            -monodromy[output][input];
        derivative[row][column(segment + 1, output)] += 1.;
      }
    }

    int row = kDimension * kSegments;
    const SourceRows source = sourceRows(node(centre, 0), node(X, 0), robust);
    for(int equation = 0; equation < 3; ++equation) {
      residual[row] = source.value[equation];
      for(int i = 0; i < 4; ++i)
        derivative[row][column(0, i)] = source.gradient[equation][i];
      ++row;
    }
    const TargetRow target = targetRow(
      node(centre, kSegments), node(X, kSegments), robust);
    residual[row] = target.value;
    for(int i = 0; i < 4; ++i)
      derivative[row][column(kSegments, i)] = target.gradient[i];
    ++row;
    if(row != kUnknowns) throw std::runtime_error("row count mismatch");
    for(int i = kDimension * kSegments; i < kUnknowns; ++i)
      residualSup = std::max(residualSup, absUpper(residual[i]));

    DMatrix midpoint(kUnknowns, kUnknowns);
    for(int i = 0; i < kUnknowns; ++i)
      for(int j = 0; j < kUnknowns; ++j)
        midpoint[i][j] = derivative[i][j].mid().leftBound();
    const DMatrix doubleInverse = matrixAlgorithms::inverseMatrix(midpoint);
    IMatrix preconditioner(kUnknowns, kUnknowns);
    for(int i = 0; i < kUnknowns; ++i)
      for(int j = 0; j < kUnknowns; ++j)
        preconditioner[i][j] = doubleInverse[i][j];
    const IMatrix remainder = IMatrix::Identity(kUnknowns)
      - preconditioner * derivative;
    const IVector contractionImage = remainder * (X - centre);
    const IVector krawczyk = centre - preconditioner * residual
      + contractionImage;
    double ratio = 0.;
    double contractionRatio = 0.;
    int worst = -1;
    for(int i = 0; i < kUnknowns; ++i) {
      const double midpointValue = centre[i].mid().leftBound();
      const double correction = std::max(
        std::abs(krawczyk[i].leftBound() - midpointValue),
        std::abs(krawczyk[i].rightBound() - midpointValue));
      const double radius = radiusAt(i / kDimension, i % kDimension, robust);
      if(correction / radius > ratio) {
        ratio = correction / radius;
        worst = i;
      }
      contractionRatio = std::max(
        contractionRatio, absUpper(contractionImage[i]) / radius);
    }
    if(!subsetInterior(krawczyk, X)) {
      std::cerr << std::setprecision(17)
        << "Krawczyk failure ratio=" << ratio
        << " contraction=" << contractionRatio
        << " worst_node=" << worst / kDimension
        << " worst_component=" << worst % kDimension << "\n";
      throw std::runtime_error("Krawczyk inclusion failed");
    }

    const IVector left = node(krawczyk, 0);
    const Coordinates sourceRoot = sourceCoordinates(left);
    const interval sourcePhase = interval(2.) * interval::pi()
      + atan(sourceRoot.u2 / sourceRoot.u1);
    const interval sourceEnergy = sqr(left[3]) - sqr(left[1])
      - interval(2.) * left[0] * left[0] * left[0] / interval(3.)
      - interval(2.) * left[0] * left[2];
    const IVector terminal = node(krawczyk, kSegments);
    const interval e = -interval(1.) / terminal[0];
    const interval e32 = e * sqrt(e);
    const interval p = terminal[1] * e32;
    const interval d = terminal[3] * e32
      + interval(2.) / sqrt(interval(3.));
    const interval omega = interval(1.) + terminal[2] * e * e;
    const interval a = d / (e * e * e);
    const interval b = (omega - e * e / interval(6.))
      / (e * e * e * e);
    const interval energy = sqr(terminal[3]) - sqr(terminal[1])
      - interval(2.) * terminal[0] * terminal[0] * terminal[0] / interval(3.)
      - interval(2.) * terminal[0] * terminal[2];
    if(!(e.leftBound() > 0. && e.rightBound() < .06
         && d.leftBound() > -.001 && d.rightBound() < .001
         && omega.leftBound() > -.01 && omega.rightBound() < .02))
      throw std::runtime_error("terminal root leaves tail graph box");

    std::cout << std::setprecision(17)
      << "{\n"
      << "  \"status\": \""
      << (robust ? "PASS-ROBUST-HETEROCLINIC" : "PASS-H7-CENTRE")
      << "\",\n"
      << "  \"segments\": " << kSegments << ",\n"
      << "  \"unknowns\": " << kUnknowns << ",\n"
      << "  \"step\": " << kStep << ",\n"
      << "  \"total_time\": "
      << papera_heteroclinic_centres::kFinalTime << ",\n"
      << "  \"source_graph_C0_component_budget\": 1e-20,\n"
      << "  \"source_graph_C1_operator_budget\": 1e-18,\n"
      << "  \"target_graph_C0_budget\": 1e-8,\n"
      << "  \"target_graph_C1_budget\": 1e-5,\n"
      << "  \"terminal_X_physical_e\": \"" << physical.e << "\",\n"
      << "  \"terminal_X_physical_a\": \"" << physical.a << "\",\n"
      << "  \"terminal_X_physical_b\": \"" << physical.b << "\",\n"
      << "  \"terminal_X_graph_energy_for_abs_zeta_le_2\": \""
      << physical.graphEnergy << "\",\n"
      << "  \"residual_sup\": " << residualSup << ",\n"
      << "  \"krawczyk_ratio\": " << ratio << ",\n"
      << "  \"contraction_ratio\": " << contractionRatio << ",\n"
      << "  \"source_u1\": \"" << sourceRoot.u1 << "\",\n"
      << "  \"source_u2\": \"" << sourceRoot.u2 << "\",\n"
      << "  \"source_s1\": \"" << sourceRoot.s1 << "\",\n"
      << "  \"source_s2\": \"" << sourceRoot.s2 << "\",\n"
      << "  \"source_phase\": \"" << sourcePhase << "\",\n"
      << "  \"source_U\": \"" << left[0] << "\",\n"
      << "  \"source_P\": \"" << left[1] << "\",\n"
      << "  \"source_V\": \"" << left[2] << "\",\n"
      << "  \"source_Q\": \"" << left[3] << "\",\n"
      << "  \"source_energy_enclosure\": \""
      << sourceEnergy << "\",\n"
      << "  \"terminal_U\": \"" << terminal[0] << "\",\n"
      << "  \"terminal_P\": \"" << terminal[1] << "\",\n"
      << "  \"terminal_V\": \"" << terminal[2] << "\",\n"
      << "  \"terminal_Q\": \"" << terminal[3] << "\",\n"
      << "  \"terminal_e\": \"" << e << "\",\n"
      << "  \"terminal_p\": \"" << p << "\",\n"
      << "  \"terminal_d\": \"" << d << "\",\n"
      << "  \"terminal_omega\": \"" << omega << "\",\n"
      << "  \"terminal_a\": \"" << a << "\",\n"
      << "  \"terminal_b\": \"" << b << "\",\n"
      << "  \"terminal_energy_enclosure\": \"" << energy << "\",\n"
      << "  \"exact_orbit_energy_by_conservation\": 0\n"
      << "}\n";
    return 0;
  } catch(const std::exception& error) {
    std::cerr << "EXCEPTION: " << error.what() << "\n";
    return 12;
  }
}
