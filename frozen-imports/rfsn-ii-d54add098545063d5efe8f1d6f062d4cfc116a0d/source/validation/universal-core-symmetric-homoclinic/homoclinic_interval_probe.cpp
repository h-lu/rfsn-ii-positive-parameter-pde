#include <algorithm>
#include <array>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>
#include <string>

#include "capd/capdlib.h"
#include "../origin-algebraic-heteroclinic/unstable_graph_terms.hpp"

using namespace capd;

namespace {

constexpr double kRadius = .01;
constexpr double kGraphC0 = 1.e-20;
constexpr double kGraphC1 = 1.e-18;

double absUpper(const interval& value) {
  return std::max(std::abs(value.leftBound()),
                  std::abs(value.rightBound()));
}

bool interior(const interval& x, const interval& y) {
  return y.leftBound() < x.leftBound() && x.rightBound() < y.rightBound();
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

struct SourceData {
  IVector state;
  IVector phaseDerivative;
};

SourceData sourceData(const interval& phase, bool robust) {
  const interval rho(kRadius, kRadius);
  const interval u1 = rho * cos(phase);
  const interval u2 = rho * sin(phase);
  const interval du1 = -rho * sin(phase);
  const interval du2 = rho * cos(phase);
  interval s1 = polynomial(kH1Terms, u1, u2);
  interval s2 = polynomial(kH2Terms, u1, u2);
  if(robust) {
    s1 += interval(-kGraphC0, kGraphC0);
    s2 += interval(-kGraphC0, kGraphC0);
  }

  const interval h1x = polynomial(kH1Terms, u1, u2, 1, 0);
  const interval h1y = polynomial(kH1Terms, u1, u2, 0, 1);
  const interval h2x = polynomial(kH2Terms, u1, u2, 1, 0);
  const interval h2y = polynomial(kH2Terms, u1, u2, 0, 1);
  interval ds1 = h1x * du1 + h1y * du2;
  interval ds2 = h2x * du1 + h2y * du2;
  if(robust) {
    // ||D(H_true-H10)||_{2->2} <= kGraphC1 and ||du/dphi||=.01.
    const double directionalError = kGraphC1 * kRadius;
    ds1 += interval(-directionalError, directionalError);
    ds2 += interval(-directionalError, directionalError);
  }

  const interval c = interval(1.) / sqrt(interval(2.));
  IVector state(4), derivative(4);
  state[0] = u1 + s1;
  state[1] = c * (u1 - s1 - u2 + s2);
  state[2] = u2 + s2;
  state[3] = c * (u1 - s1 + u2 - s2);
  derivative[0] = du1 + ds1;
  derivative[1] = c * (du1 - ds1 - du2 + ds2);
  derivative[2] = du2 + ds2;
  derivative[3] = c * (du1 - ds1 + du2 - ds2);
  return {state, derivative};
}

IVector fieldAt(const IVector& z) {
  IVector result(4);
  result[0] = z[1];
  result[1] = -sqr(z[0]) - z[2];
  result[2] = z[3];
  result[3] = z[0];
  return result;
}

std::string decimalHundredths(int value) {
  std::ostringstream output;
  output << value / 100 << "." << std::setw(2) << std::setfill('0')
         << value % 100;
  return output.str();
}

IVector orbitTube(IOdeSolver& solver, const IVector& initial,
                  const std::string& lo, const std::string& hi) {
  ITimeMap map(solver);
  C0HOTripletonSet set(initial);
  return map(interval(lo, hi), set);
}

void requireSignCells(IOdeSolver& solver, const IVector& initial,
                      int first, int last, int step, int component,
                      int sign, interval& hull, bool& hullInitialized) {
  for(int index = first; index < last; index += step) {
    const int next = std::min(index + step, last);
    const IVector tube = orbitTube(solver, initial,
      decimalHundredths(index), decimalHundredths(next));
    const interval value = tube[component];
    if((sign > 0 && value.leftBound() <= 0.)
       || (sign < 0 && value.rightBound() >= 0.))
      throw std::runtime_error("first-hit sign cell failed");
    hull = hullInitialized ? intervalHull(hull, value) : value;
    hullInitialized = true;
  }
}

}  // namespace

int main() {
  try {
    std::cout << std::setprecision(17);
    IMap field("var:U,P,V,Q;fun:P,-U*U-V,Q,U;");
    IOdeSolver solver(field, 30);
    solver.setAbsoluteTolerance(1e-14);
    solver.setRelativeTolerance(1e-14);

    IVector centre(2), box(2);
    centre[0] = interval("5.861505585644824", "5.861505585644824");
    centre[1] = interval("9.637442067896563", "9.637442067896563");
    box[0] = interval("5.861505584644824", "5.861505586644824");
    box[1] = interval("9.637442066896563", "9.637442068896563");

    const SourceData sourceCentre = sourceData(centre[0], true);
    const SourceData sourceBox = sourceData(box[0], true);

    ITimeMap centreMap(solver);
    C0HOTripletonSet centreSet(sourceCentre.state);
    const IVector endpointCentre = centreMap(centre[1], centreSet);
    IVector residual(2);
    residual[0] = endpointCentre[1];
    residual[1] = endpointCentre[3];

    ITimeMap boxMap(solver);
    C1HORect2Set boxSet(sourceBox.state);
    const IVector endpointBox = boxMap(box[1], boxSet);
    const IMatrix monodromy = (IMatrix)boxSet;
    const IVector phaseColumn = monodromy * sourceBox.phaseDerivative;
    const IVector timeColumn = fieldAt(endpointBox);
    IMatrix derivative(2, 2);
    derivative[0][0] = phaseColumn[1];
    derivative[1][0] = phaseColumn[3];
    derivative[0][1] = timeColumn[1];
    derivative[1][1] = timeColumn[3];

    DMatrix midpoint(2, 2);
    for(int i = 0; i < 2; ++i)
      for(int j = 0; j < 2; ++j)
        midpoint[i][j] = derivative[i][j].mid().leftBound();
    const DMatrix inverse = matrixAlgorithms::inverseMatrix(midpoint);
    IMatrix preconditioner(2, 2);
    for(int i = 0; i < 2; ++i)
      for(int j = 0; j < 2; ++j)
        preconditioner[i][j] = inverse[i][j];
    const IMatrix remainder = IMatrix::Identity(2)
      - preconditioner * derivative;
    const IVector contractionImage = remainder * (box - centre);
    const IVector krawczyk = centre - preconditioner * residual
      + contractionImage;
    if(!interior(krawczyk[0], box[0])
       || !interior(krawczyk[1], box[1]))
      throw std::runtime_error("homoclinic Krawczyk inclusion failed");

    double inclusionRatio = 0.;
    double contractionRatio = 0.;
    for(int i = 0; i < 2; ++i) {
      const double c = centre[i].mid().leftBound();
      const double correction = std::max(
        std::abs(krawczyk[i].leftBound() - c),
        std::abs(krawczyk[i].rightBound() - c));
      const double radius = std::min(c - box[i].leftBound(),
                                     box[i].rightBound() - c);
      inclusionRatio = std::max(inclusionRatio, correction / radius);
      contractionRatio = std::max(
        contractionRatio, absUpper(contractionImage[i]) / radius);
    }
    if(contractionRatio >= 1.)
      throw std::runtime_error("homoclinic Krawczyk contraction failed");

    const interval determinant = derivative[0][0] * derivative[1][1]
      - derivative[0][1] * derivative[1][0];
    if(determinant.contains(0.))
      throw std::runtime_error("homoclinic shooting determinant contains zero");
    if(phaseColumn[0].contains(0.) || phaseColumn[2].contains(0.))
      throw std::runtime_error("endpoint L-phase column is not sign definite");
    if(endpointBox[0].leftBound() <= 1.)
      throw std::runtime_error("homoclinic endpoint may be the origin");

    // Every source represented by the Krawczyk box lies in this initial box.
    // The following sign cells prove that no positive Fix(R) hit precedes T.
    const SourceData sourceRootBox = sourceData(krawczyk[0], true);
    interval pPositive, qPositive, pNegative, qNegative;
    bool havePPositive = false, haveQPositive = false;
    bool havePNegative = false, haveQNegative = false;
    if(sourceRootBox.state[1].leftBound() <= 0.)
      throw std::runtime_error("initial source P is not positive");
    // A TimeMap call with the interval [0,.05] is interpreted as a zero-time
    // request.  Dense output instead encloses every internal step from t=0
    // to the point time .05, including the complete first open cell.
    ITimeMap initialTimeMap(solver);
    initialTimeMap.stopAfterStep(true);
    C0HOTripletonSet initialSet(sourceRootBox.state);
    pPositive = sourceRootBox.state[1];
    havePPositive = true;
    do {
      initialTimeMap(interval(".05", ".05"), initialSet);
      const IVector enclosure = initialSet.getLastEnclosure();
      if(enclosure[1].leftBound() <= 0.)
        throw std::runtime_error("initial dense-output P tube failed");
      pPositive = intervalHull(pPositive, enclosure[1]);
    } while(!initialTimeMap.completed());
    requireSignCells(solver, sourceRootBox.state, 5, 165, 5, 1, +1,
                     pPositive, havePPositive);
    requireSignCells(solver, sourceRootBox.state, 165, 175, 1, 3, +1,
                     qPositive, haveQPositive);
    requireSignCells(solver, sourceRootBox.state, 175, 735, 5, 1, -1,
                     pNegative, havePNegative);
    requireSignCells(solver, sourceRootBox.state, 735, 955, 5, 3, -1,
                     qNegative, haveQNegative);
    const IVector finalTube = orbitTube(solver, sourceRootBox.state,
      "9.55", "9.637442068896563");
    if(finalTube[0].leftBound() <= 0.)
      throw std::runtime_error("final Q-monotonicity tube has U<=0");

    const interval energy = sqr(endpointBox[3]) - sqr(endpointBox[1])
      - interval(2.) * power(endpointBox[0], 3) / interval(3.)
      - interval(2.) * endpointBox[0] * endpointBox[2];

    std::cout
      << "centre_endpoint " << endpointCentre << "\n"
      << "root_box " << krawczyk << "\n"
      << "endpoint_box " << endpointBox << "\n"
      << "shooting_derivative " << derivative << "\n"
      << "phase_endpoint_L " << phaseColumn[0] << " "
      << phaseColumn[2] << "\n"
      << "shooting_determinant " << determinant << "\n"
      << "Krawczyk_inclusion_ratio " << inclusionRatio << "\n"
      << "Krawczyk_contraction_ratio " << contractionRatio << "\n"
      << "P_positive_hull " << pPositive << "\n"
      << "Q_positive_bridge_hull " << qPositive << "\n"
      << "P_negative_hull " << pNegative << "\n"
      << "Q_negative_hull " << qNegative << "\n"
      << "final_U_monotonicity_hull " << finalTube[0] << "\n"
      << "correlation_blind_endpoint_energy " << energy << "\n"
      << "PASS robust symmetric-homoclinic Krawczyk, first-hit, and "
         "nondegeneracy\n";
    return 0;
  } catch(const std::exception& error) {
    std::cerr << "FAIL: " << error.what() << "\n";
    return 10;
  }
}
