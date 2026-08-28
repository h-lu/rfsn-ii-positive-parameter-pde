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

using namespace capd;

namespace {

constexpr int kFirst = 50;
constexpr int kLast = 1999;

struct Hull {
  double lo = std::numeric_limits<double>::infinity();
  double hi = -std::numeric_limits<double>::infinity();

  void add(const interval& a) {
    lo = std::min(lo,a.leftBound());
    hi = std::max(hi,a.rightBound());
  }
};

struct InitialData {
  interval R;
  IVector center;
  IMatrix C;
  IVector radii;

  InitialData(const std::string& loText, const std::string& hiText)
    : R(loText,hiText), center(4), C(4,4), radii(4) {
    C.clear();
    radii.clear();

    // R is constructed from decimal strings with outward rounding.  If
    // r=m+s, then the exact source curve is
    //   (-2r,0,0,r^2)
    // = (-2m,0,0,m^2) + (-2,0,0,2m)s + (0,0,0,s^2).
    // The first generator retains the x--w correlation; the second one
    // encloses s^2.  Every arithmetic operation here is interval-valued.
    const double m = (R.leftBound()+R.rightBound())/2.;
    const interval mI(m);
    const interval s = R-mI;

    center[0] = interval(-2.)*mI;
    center[1] = 0.;
    center[2] = 0.;
    center[3] = sqr(mI);
    C[0][0] = -2.;
    C[3][0] = interval(2.)*mI;
    C[3][1] = 1.;
    radii[0] = s;
    radii[1] = sqr(s);
  }
};

std::string gridPoint(int i) {
  std::ostringstream out;
  // Integer formatting, not floating-point stepping: adjacent boxes use
  // byte-for-byte identical endpoint strings.
  out << (i/1000) << "." << std::setw(3) << std::setfill('0') << (i%1000);
  return out.str();
}

double absUpper(const interval& a) {
  return std::max(std::abs(a.leftBound()),std::abs(a.rightBound()));
}

std::string intervalString(const interval& a) {
  std::ostringstream out;
  out << std::setprecision(17) << a;
  return out.str();
}

[[noreturn]] void fail(const std::string& kind, int i,
                       const std::string& detail) {
  std::cerr << "FAIL " << kind << " box=[" << gridPoint(i) << ","
            << gridPoint(i+1) << "] " << detail << "\n";
  std::exit(kind == "C0" ? 10 : 11);
}

} // namespace

int main() {
  const auto started = std::chrono::steady_clock::now();
  try {
    const interval X0("20","20");
    const interval theta("0.5","0.5");

    IMap c0Field("var:x,y,q,w;fun:y,x*x-w,x,q;");
    IOdeSolver c0Solver(c0Field,25);
    c0Solver.setAbsoluteTolerance(1e-13);
    c0Solver.setRelativeTolerance(1e-13);
    ICoordinateSection c0Section(4,0,X0);
    IPoincareMap c0Map(c0Solver,c0Section,poincare::MinusPlus);
    c0Map.setMaxReturnTime(30.);
    c0Map.setBlowUpMaxNorm(1e6);

    IMap c1Field("var:x,y,q,w;fun:y,x*x-w,x,q;");
    IOdeSolver c1Solver(c1Field,25);
    c1Solver.setAbsoluteTolerance(1e-13);
    c1Solver.setRelativeTolerance(1e-13);
    ICoordinateSection c1Section(4,0,X0);
    IPoincareMap c1Map(c1Solver,c1Section,poincare::MinusPlus);
    c1Map.setMaxReturnTime(30.);
    c1Map.setBlowUpMaxNorm(1e6);

    Hull tau, yHull, qHull, wHull, dHull, hHull, inwardHull;
    Hull tauDerivative;
    double eventDerivativeSup = 0.;

    for(int i=kFirst; i<=kLast; ++i) {
      const std::string loText = gridPoint(i);
      const std::string hiText = gridPoint(i+1);
      const InitialData initial(loText,hiText);

      // C0 certificate: every exact source point in this r-box reaches
      // x=20 in the MinusPlus direction and is enclosed by z.
      C0HOTripletonSet c0Set(initial.center,initial.C,initial.radii);
      interval returnTime;
      const IVector z = c0Map(c0Set,returnTime);
      const interval y = z[1];
      const interval q = z[2];
      const interval w = z[3];
      const interval D = theta*sqr(X0)-w;
      const interval H = interval(2.)*theta*X0*y-q;
      const interval inward = interval(2.)*theta*(interval(1.)-theta)
                            *X0*X0*X0-X0;

      // Predeclared strict margins.  Any loss of a margin is a failed
      // certificate, not merely a warning in the summary.
      if(!(returnTime.leftBound()>2. && returnTime.rightBound()<6.))
        fail("C0",i,"return time not contained in (2,6): "+intervalString(returnTime));
      if(!(y.leftBound()>60.))
        fail("C0",i,"y lower bound <= 60: "+intervalString(y));
      if(!(q.leftBound()>5.))
        fail("C0",i,"q lower bound <= 5: "+intervalString(q));
      if(!(D.leftBound()>194.))
        fail("C0",i,"D lower bound <= 194: "+intervalString(D));
      if(!(H.leftBound()>1200.))
        fail("C0",i,"H lower bound <= 1200: "+intervalString(H));
      if(!(inward.leftBound()>3970.))
        fail("C0",i,"inward lower bound <= 3970: "+intervalString(inward));

      tau.add(returnTime);
      yHull.add(y);
      qHull.add(q);
      wHull.add(w);
      dHull.add(D);
      hHull.add(H);
      inwardHull.add(inward);

      // C1 certificate: the C1 set bounds the ambient flow derivative on
      // the same initial enclosure.  Multiplication by the exact source
      // tangent (-2,0,0,2r) gives a valid enclosure for d/dr along the
      // source curve.  The event-time correction is computed explicitly.
      C1HORect2Set c1Set(initial.center,initial.C,initial.radii);
      IMatrix monodromy(4,4);
      interval c1ReturnTime;
      const IVector z1 = c1Map(c1Set,monodromy,c1ReturnTime);
      const IMatrix eventDerivative = c1Map.computeDP(z1,monodromy);
      IVector sourceTangent(4);
      sourceTangent.clear();
      sourceTangent[0] = -2.;
      sourceTangent[3] = interval(2.)*initial.R;
      const IVector flowVariation = monodromy*sourceTangent;
      const IVector eventVariation = eventDerivative*sourceTangent;
      const interval tauPrime = -flowVariation[0]/z1[1];

      if(!(tauPrime.leftBound()>-40. && tauPrime.rightBound()<-0.3))
        fail("C1",i,"tau_r not contained in (-40,-0.3): "+intervalString(tauPrime));
      for(int j=0;j<4;++j) {
        const double a = absUpper(eventVariation[j]);
        if(!(std::isfinite(a) && a<20000.)) {
          std::ostringstream detail;
          detail << "event derivative component " << j << " has |.| upper " << a;
          fail("C1",i,detail.str());
        }
        eventDerivativeSup = std::max(eventDerivativeSup,a);
      }
      tauDerivative.add(tauPrime);
    }

    const double seconds = std::chrono::duration<double>(
      std::chrono::steady_clock::now()-started).count();
    std::cout << std::setprecision(17)
      << "{\n"
      << "  \"status\": \"PASS\",\n"
      << "  \"boxes\": " << (kLast-kFirst+1) << ",\n"
      << "  \"cover\": \"[i/1000,(i+1)/1000], i=50,...,1999\",\n"
      << "  \"theta\": 0.5,\n"
      << "  \"X0\": 20,\n"
      << "  \"c0\": {\n"
      << "    \"tau\": [" << tau.lo << ", " << tau.hi << "],\n"
      << "    \"y\": [" << yHull.lo << ", " << yHull.hi << "],\n"
      << "    \"q\": [" << qHull.lo << ", " << qHull.hi << "],\n"
      << "    \"w\": [" << wHull.lo << ", " << wHull.hi << "],\n"
      << "    \"D\": [" << dHull.lo << ", " << dHull.hi << "],\n"
      << "    \"H\": [" << hHull.lo << ", " << hHull.hi << "],\n"
      << "    \"inward\": [" << inwardHull.lo << ", " << inwardHull.hi << "]\n"
      << "  },\n"
      << "  \"c1\": {\n"
      << "    \"tau_r\": [" << tauDerivative.lo << ", "
      << tauDerivative.hi << "],\n"
      << "    \"event_derivative_sup\": " << eventDerivativeSup << "\n"
      << "  },\n"
      << "  \"wall_seconds\": " << seconds << "\n"
      << "}\n";
    return 0;
  } catch(const std::exception& e) {
    std::cerr << "EXCEPTION: " << e.what() << "\n";
    return 12;
  }
}
