#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <sstream>
#include <stdexcept>

#include "capd/capdlib.h"

using namespace capd;

namespace {

bool interior(const interval& x, const interval& y) {
  return y.leftBound() < x.leftBound() && x.rightBound() < y.rightBound();
}

std::string hundredths(int value) {
  std::ostringstream out;
  out << (value/100) << "." << std::setw(2) << std::setfill('0')
      << (value%100);
  return out.str();
}

IVector orbitTube(IOdeSolver& solver, const IVector& initial,
                  const std::string& lo, const std::string& hi) {
  ITimeMap map(solver);
  C0HOTripletonSet set(initial);
  return map(interval(lo,hi),set);
}

}  // namespace

int main() {
  std::cout << std::setprecision(17);
  IMap field("var:U,P,V,Q;fun:P,-U*U-V,Q,U;");
  IOdeSolver solver(field, 30);
  solver.setAbsoluteTolerance(1e-14);
  solver.setRelativeTolerance(1e-14);

  IVector centre(2), box(2);
  centre[0] = interval("0.041783788071385504",
                       "0.041783788071385504");
  centre[1] = interval("7.509609721997845",
                       "7.509609721997845");
  box[0] = interval("0.041783787871385501",
                    "0.041783788271385507");
  box[1] = interval("7.5096097217978448",
                    "7.5096097221978448");

  IVector initialCentre(4), initialBox(4);
  initialCentre[0] = centre[0];
  initialCentre[1] = 0.;
  initialCentre[2] = interval("0.08", "0.08");
  initialCentre[3] = 0.;
  initialBox[0] = box[0];
  initialBox[1] = 0.;
  initialBox[2] = interval("0.08", "0.08");
  initialBox[3] = 0.;

  ITimeMap centreMap(solver);
  C0HOTripletonSet centreSet(initialCentre);
  const IVector zc = centreMap(centre[1], centreSet);
  IVector residual(2);
  residual[0] = zc[1];
  residual[1] = zc[3];

  ITimeMap boxMap(solver);
  C1HORect2Set boxSet(initialBox);
  const IVector zb = boxMap(box[1], boxSet);
  const IMatrix flowDerivative = (IMatrix)boxSet;

  IMatrix derivative(2,2);
  derivative[0][0] = flowDerivative[1][0];
  derivative[1][0] = flowDerivative[3][0];
  derivative[0][1] = -sqr(zb[0]) - zb[2];
  derivative[1][1] = zb[0];

  DMatrix midpoint(2,2);
  for(int i=0;i<2;++i)
    for(int j=0;j<2;++j)
      midpoint[i][j] = derivative[i][j].mid().leftBound();
  const DMatrix inverse = matrixAlgorithms::inverseMatrix(midpoint);
  IMatrix A(2,2);
  for(int i=0;i<2;++i)
    for(int j=0;j<2;++j)
      A[i][j] = inverse[i][j];

  const IMatrix remainder = IMatrix::Identity(2) - A*derivative;
  const IVector K = centre - A*residual + remainder*(box-centre);

  std::cout << "centre endpoint " << zc << "\n";
  std::cout << "box endpoint " << zb << "\n";
  std::cout << "derivative " << derivative << "\n";
  std::cout << "residual " << residual << "\n";
  std::cout << "K " << K << "\n";
  std::cout << "box " << box << "\n";
  if(!interior(K[0],box[0]) || !interior(K[1],box[1]))
    throw std::runtime_error("Krawczyk inclusion failed");
  double inclusionRatio = 0.;
  for(int i=0;i<2;++i) {
    const double c = centre[i].mid().leftBound();
    const double correction = std::max(std::abs(K[i].leftBound()-c),
                                       std::abs(K[i].rightBound()-c));
    const double radius = std::min(c-box[i].leftBound(),
                                   box[i].rightBound()-c);
    inclusionRatio = std::max(inclusionRatio,correction/radius);
  }

  interval pHull;
  bool firstP = true;
  for(int i=5;i<200;i+=5) {
    const IVector tube = orbitTube(solver,initialBox,
                                   hundredths(i),hundredths(i+5));
    if(tube[1].rightBound()>=0.)
      throw std::runtime_error("P sign cover failed");
    pHull = firstP ? tube[1] : intervalHull(pHull,tube[1]);
    firstP = false;
  }

  interval qHull;
  bool firstQ = true;
  for(int i=200;i<740;i+=5) {
    const IVector tube = orbitTube(solver,initialBox,
                                   hundredths(i),hundredths(i+5));
    if(tube[3].rightBound()>=0.)
      throw std::runtime_error("Q coarse sign cover failed");
    qHull = firstQ ? tube[3] : intervalHull(qHull,tube[3]);
    firstQ = false;
  }
  for(int i=740;i<749;++i) {
    const IVector tube = orbitTube(solver,initialBox,
                                   hundredths(i),hundredths(i+1));
    if(tube[3].rightBound()>=0.)
      throw std::runtime_error("Q fine sign cover failed");
    qHull = intervalHull(qHull,tube[3]);
  }

  const IVector finalTube = orbitTube(
    solver,initialBox,"7.49","7.5096097221978448"
  );
  if(finalTube[0].leftBound()<=0.)
    throw std::runtime_error("final U monotonicity failed");

  const interval det = derivative[0][0]*derivative[1][1]
                     - derivative[0][1]*derivative[1][0];
  if(det.contains(0.))
    throw std::runtime_error("return Jacobian may be singular");
  const interval sourceEnergy = -interval(2.)*power(box[0],3)/interval(3.)
                              - interval(2.)*box[0]*interval("0.08","0.08");
  const interval period = interval(2.)*box[1];
  if(zb[0].leftBound()<=box[0].rightBound()+1.)
    throw std::runtime_error("endpoint separation failed");

  std::cout << "P sign hull on [0.05,2] " << pHull << "\n";
  std::cout << "Q sign hull on [2,7.49] " << qHull << "\n";
  std::cout << "final U tube " << finalTube[0] << "\n";
  std::cout << "return determinant " << det << "\n";
  std::cout << "source energy " << sourceEnergy << "\n";
  std::cout << "period " << period << "\n";
  std::cout << "Krawczyk inclusion ratio " << inclusionRatio << "\n";

  std::cout << "PASS periodic-return Krawczyk\n";
  return 0;
}
