#include <algorithm>
#include <chrono>
#include <cmath>
#include <cstdlib>
#include <iomanip>
#include <iostream>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>

#include "capd/capdlib.h"
#include "../origin-algebraic-heteroclinic/unstable_graph_terms.hpp"

using namespace capd;

namespace {

constexpr int kFirst = -200;
constexpr int kLast = 199;
constexpr double kRadius = .01;
constexpr double kGraphC0 = 1.e-20;
constexpr double kGraphC1 = 1.e-18;

struct Hull {
  double lo = std::numeric_limits<double>::infinity();
  double hi = -std::numeric_limits<double>::infinity();

  void add(const interval& value) {
    lo = std::min(lo, value.leftBound());
    hi = std::max(hi, value.rightBound());
  }
};

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

struct SourceData {
  IVector state;
  IVector phaseDerivative;
};

SourceData sourceData(const interval& phase) {
  const interval rho(kRadius, kRadius);
  const interval u1 = rho * cos(phase);
  const interval u2 = rho * sin(phase);
  const interval du1 = -rho * sin(phase);
  const interval du2 = rho * cos(phase);

  // H_true=H10+delta H.  The two component error intervals contain the
  // certified Euclidean C0 ball ||delta H||_2<=1e-20.
  interval s1 = polynomial(kH1Terms, u1, u2)
    + interval(-kGraphC0, kGraphC0);
  interval s2 = polynomial(kH2Terms, u1, u2)
    + interval(-kGraphC0, kGraphC0);

  const interval h1x = polynomial(kH1Terms, u1, u2, 1, 0);
  const interval h1y = polynomial(kH1Terms, u1, u2, 0, 1);
  const interval h2x = polynomial(kH2Terms, u1, u2, 1, 0);
  const interval h2y = polynomial(kH2Terms, u1, u2, 0, 1);
  const double directionalError = kGraphC1 * kRadius;
  interval ds1 = h1x * du1 + h1y * du2
    + interval(-directionalError, directionalError);
  interval ds2 = h2x * du1 + h2y * du2
    + interval(-directionalError, directionalError);

  const interval c = interval(1.) / sqrt(interval(2.));
  const interval U = u1 + s1;
  const interval P = c * (u1 - s1 - u2 + s2);
  const interval V = u2 + s2;
  const interval Q = c * (u1 - s1 + u2 - s2);
  const interval dU = du1 + ds1;
  const interval dP = c * (du1 - ds1 - du2 + ds2);
  const interval dV = du2 + ds2;
  const interval dQ = c * (du1 - ds1 + du2 - ds2);

  // Pole variables are (x,y,q,w)=(-U,-P,-Q,-V).
  IVector state(4), derivative(4);
  state[0] = -U;
  state[1] = -P;
  state[2] = -Q;
  state[3] = -V;
  derivative[0] = -dU;
  derivative[1] = -dP;
  derivative[2] = -dQ;
  derivative[3] = -dV;
  return {state, derivative};
}

std::string phasePoint(int index) {
  std::ostringstream out;
  if(index < 0) out << '-';
  const int magnitude = std::abs(index);
  out << magnitude / 1000 << '.' << std::setw(3) << std::setfill('0')
      << magnitude % 1000;
  return out.str();
}

std::string intervalString(const interval& value) {
  std::ostringstream out;
  out << std::setprecision(17) << value;
  return out.str();
}

[[noreturn]] void fail(const std::string& kind, int index,
                       const std::string& detail) {
  std::cerr << "FAIL " << kind << " phase=[" << phasePoint(index)
            << ',' << phasePoint(index + 1) << "] " << detail << '\n';
  std::exit(kind == "C0" ? 10 : 11);
}

}  // namespace

int main() {
  const auto started = std::chrono::steady_clock::now();
  try {
    const interval X0("10", "10");
    const interval theta("0.5", "0.5");
    IMap c0Field("var:x,y,q,w;fun:y,x*x-w,x,q;");
    IOdeSolver c0Solver(c0Field, 30);
    c0Solver.setAbsoluteTolerance(1e-13);
    c0Solver.setRelativeTolerance(1e-13);
    ICoordinateSection c0Section(4, 0, X0);
    // Both is essential: CAPD returns the first section encounter, without
    // silently skipping a crossing having the opposite orientation.
    IPoincareMap c0Map(c0Solver, c0Section, poincare::Both);
    c0Map.setMaxReturnTime(30.);
    c0Map.setBlowUpMaxNorm(1e6);

    IMap c1Field("var:x,y,q,w;fun:y,x*x-w,x,q;");
    IOdeSolver c1Solver(c1Field, 30);
    c1Solver.setAbsoluteTolerance(1e-13);
    c1Solver.setRelativeTolerance(1e-13);
    ICoordinateSection c1Section(4, 0, X0);
    IPoincareMap c1Map(c1Solver, c1Section, poincare::Both);
    c1Map.setMaxReturnTime(30.);
    c1Map.setBlowUpMaxNorm(1e6);

    Hull sourceX, sourceY, sourceQ, sourceW;
    Hull tau, yHull, qHull, wHull, dHull, hHull;
    Hull yPrimeHull, hPrimeHull, tauDerivative;
    Hull eventDx, eventDy, eventDq, eventDw;

    for(int index = kFirst; index <= kLast; ++index) {
      const interval phase(phasePoint(index), phasePoint(index + 1));
      const SourceData source = sourceData(phase);
      sourceX.add(source.state[0]);
      sourceY.add(source.state[1]);
      sourceQ.add(source.state[2]);
      sourceW.add(source.state[3]);
      if(source.state[0].rightBound() >= 0.)
        fail("C0", index, "source does not satisfy x<0: "
             + intervalString(source.state[0]));
      if(source.state[1].rightBound() >= -.005)
        fail("C0", index, "source is not separated from raw-crest y=0: "
             + intervalString(source.state[1]));
      if(source.state[2].rightBound() >= -.005)
        fail("C0", index, "source is not separated from raw-crest q=0: "
             + intervalString(source.state[2]));

      C0HOTripletonSet c0Set(source.state);
      interval returnTime;
      const IVector event = c0Map(c0Set, returnTime);
      const interval y = event[1];
      const interval q = event[2];
      const interval w = event[3];
      const interval D = theta * sqr(X0) - w;
      const interval H = interval(2.) * theta * X0 * y - q;
      const interval yPrime = sqr(X0) - w;
      const interval hPrime = interval(2.) * theta
        * (sqr(y) + X0 * yPrime) - X0;

      // Declared open margins.  Since the source starts with x<0 and the
      // map uses Both, this is the first x=10 encounter.  The y margin says
      // that this first encounter crosses inward through the x face.
      if(!(returnTime.leftBound() > 10. && returnTime.rightBound() < 12.))
        fail("C0", index, "first-event time not in (10,12): "
             + intervalString(returnTime));
      if(y.leftBound() <= 25.)
        fail("C0", index, "x-face speed y<=25: " + intervalString(y));
      if(D.leftBound() <= 50.)
        fail("C0", index, "D face margin <=50: " + intervalString(D));
      if(H.leftBound() <= 250.)
        fail("C0", index, "H face margin <=250: " + intervalString(H));
      if(yPrime.leftBound() <= 100.)
        fail("C0", index, "y-face inward derivative <=100: "
             + intervalString(yPrime));
      if(hPrime.leftBound() <= 1600.)
        fail("C0", index, "H-face inward derivative <=1600: "
             + intervalString(hPrime));

      tau.add(returnTime);
      yHull.add(y);
      qHull.add(q);
      wHull.add(w);
      dHull.add(D);
      hHull.add(H);
      yPrimeHull.add(yPrime);
      hPrimeHull.add(hPrime);

      C1HORect2Set c1Set(source.state);
      IMatrix monodromy(4, 4);
      interval c1ReturnTime;
      const IVector event1 = c1Map(c1Set, monodromy, c1ReturnTime);
      const IMatrix eventDerivative = c1Map.computeDP(event1, monodromy);
      const IVector flowVariation = monodromy * source.phaseDerivative;
      const IVector eventVariation = eventDerivative * source.phaseDerivative;
      const interval tauPrime = -flowVariation[0] / event1[1];
      for(int component = 0; component < 4; ++component) {
        if(!(std::isfinite(absUpper(eventVariation[component]))
             && absUpper(eventVariation[component]) < 1e5))
          fail("C1", index, "event phase derivative is unbounded");
      }
      if(!(std::isfinite(absUpper(tauPrime)) && absUpper(tauPrime) < 1e4))
        fail("C1", index, "event-time phase derivative is unbounded");
      tauDerivative.add(tauPrime);
      eventDx.add(eventVariation[0]);
      eventDy.add(eventVariation[1]);
      eventDq.add(eventVariation[2]);
      eventDw.add(eventVariation[3]);
    }

    const double seconds = std::chrono::duration<double>(
      std::chrono::steady_clock::now() - started).count();
    std::cout << std::setprecision(17)
      << "{\n"
      << "  \"status\": \"PASS-TRUE-WU-OPEN-PHASE-POLE-ENTRY\",\n"
      << "  \"phase_closed_cover\": [-0.2, 0.2],\n"
      << "  \"phase_open_interval\": \"(-0.2,0.2) modulo 2*pi\",\n"
      << "  \"boxes\": " << (kLast - kFirst + 1) << ",\n"
      << "  \"box_width\": 0.001,\n"
      << "  \"source_radius\": 0.01,\n"
      << "  \"source_graph_C0_euclidean_upper\": 1e-20,\n"
      << "  \"source_graph_C0_component_interval_upper\": 1e-20,\n"
      << "  \"source_graph_C1_operator_upper\": 1e-18,\n"
      << "  \"source_graph_phase_directional_component_upper\": 1e-20,\n"
      << "  \"source_x\": [" << sourceX.lo << ", " << sourceX.hi << "],\n"
      << "  \"source_y\": [" << sourceY.lo << ", " << sourceY.hi << "],\n"
      << "  \"source_q\": [" << sourceQ.lo << ", " << sourceQ.hi << "],\n"
      << "  \"source_w\": [" << sourceW.lo << ", " << sourceW.hi << "],\n"
      << "  \"section_x\": 10,\n"
      << "  \"poincare_crossing_mode\": \"Both (first section encounter)\",\n"
      << "  \"c0\": {\n"
      << "    \"tau\": [" << tau.lo << ", " << tau.hi << "],\n"
      << "    \"y\": [" << yHull.lo << ", " << yHull.hi << "],\n"
      << "    \"q\": [" << qHull.lo << ", " << qHull.hi << "],\n"
      << "    \"w\": [" << wHull.lo << ", " << wHull.hi << "],\n"
      << "    \"D\": [" << dHull.lo << ", " << dHull.hi << "],\n"
      << "    \"H\": [" << hHull.lo << ", " << hHull.hi << "],\n"
      << "    \"y_prime\": [" << yPrimeHull.lo << ", "
      << yPrimeHull.hi << "],\n"
      << "    \"H_prime\": [" << hPrimeHull.lo << ", "
      << hPrimeHull.hi << "]\n"
      << "  },\n"
      << "  \"c1\": {\n"
      << "    \"tau_phase\": [" << tauDerivative.lo << ", "
      << tauDerivative.hi << "],\n"
      << "    \"event_phase_x\": [" << eventDx.lo << ", "
      << eventDx.hi << "],\n"
      << "    \"event_phase_y\": [" << eventDy.lo << ", "
      << eventDy.hi << "],\n"
      << "    \"event_phase_q\": [" << eventDq.lo << ", "
      << eventDq.hi << "],\n"
      << "    \"event_phase_w\": [" << eventDw.lo << ", "
      << eventDw.hi << "]\n"
      << "  },\n"
      << "  \"wall_seconds\": " << seconds << "\n"
      << "}\n";
    return 0;
  } catch(const std::exception& error) {
    std::cerr << "EXCEPTION: " << error.what() << '\n';
    return 12;
  }
}
