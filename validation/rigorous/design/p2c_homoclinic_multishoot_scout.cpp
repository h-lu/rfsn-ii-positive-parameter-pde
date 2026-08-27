#include <algorithm>
#include <array>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

#include "capd/capdlib.h"

// Feasibility scout only: this is deliberately not certificate/replay
// infrastructure.  The frozen H10 coefficient table must be materialized
// from the Git object locked in flagship_import.lock.json and injected with
// an absolute -include compiler argument; the flagship working tree is not
// an input.
//
// At a fixed positive parameter the local zero-energy equation is
//   -2h(u1*s2 + u2*s1) - a(u1+s1)^3/3 + b(u1+s1)^4/4 = 0.
// It eliminates s2 and prevents the certified C0 graph tube from being
// treated as two independent stable errors.  The remaining graph error
// p(phi)=s1(phi)-H10_1(phi) is represented by the equation e-p(phi)=0 with
// |p|<=5e-6 and |p'|<=3e-4*.01=3e-6.  Thus the Krawczyk inclusion is uniform
// for every fixed actual C1 graph-error function satisfying those budgets.
// In cell mode only the affine shooting centres are built at the parameter
// midpoint; the base residual and the complete X-Jacobian use the full
// outward-rounded parameter cell.

using namespace capd;

namespace {
constexpr double kRadius=.01;
constexpr double kGraphC0=5e-6;
constexpr double kGraphC1=3e-4;
constexpr int kSegments=9;
constexpr std::array<double,kSegments> kNodeTimes={1.55,1.82,3.2,4.8,6.2,7.38,8.3,9.0,9.55};

interval integerPower(interval x,int n){interval r(1.);for(int i=0;i<n;++i)r*=x;return r;}
int fallingFactorial(int n,int k){int r=1;for(int i=0;i<k;++i)r*=n-i;return r;}
interval coefficient(const PolynomialTerm&t){interval r=interval(t.numerator,t.numerator)/interval(t.denominator,t.denominator);if(t.times_sqrt_two)r*=sqrt(interval(2.));return r;}
template<std::size_t N> interval polynomial(const PolynomialTerm(&terms)[N],const interval&x,const interval&y,int dx=0,int dy=0){interval r(0.);for(const auto&t:terms){if(t.px<dx||t.py<dy)continue;r+=coefficient(t)*interval(fallingFactorial(t.px,dx))*interval(fallingFactorial(t.py,dy))*integerPower(x,t.px-dx)*integerPower(y,t.py-dy);}return r;}
struct Parameters{
  interval r,a2,epsilon,a,b,c,alpha,beta,h,chi;
};
Parameters parameters(const interval&r,const interval&a2,const interval&epsilon){
 const interval rootEpsilon=sqrt(epsilon),r2=sqr(r),r4=sqr(r2);
 const interval a=interval(1.)+rootEpsilon*r2*r*a2;
 const interval b=rootEpsilon*r2/interval(3.);
 const interval c=interval(2.)*r*a2+rootEpsilon*r4*sqr(a2);
 const interval alpha=interval(.5)*sqrt(interval(2.)+c);
 const interval beta=interval(.5)*sqrt(interval(2.)-c);
 // Keep the common c dependence: 2*alpha*beta evaluated as an interval
 // product has an artificial O(|c|) width, whereas h varies only as c^2.
 const interval h=interval(.5)*sqrt(interval(4.)-sqr(c));
 const interval chi=atan((interval(1.)/sqrt(interval(2.))-alpha)/beta);
 return {r,a2,epsilon,a,b,c,alpha,beta,h,chi};
}
struct SourceData{IVector state,phaseDerivative,errorDerivative;};
SourceData sourceData(const Parameters&p,const interval& phase,const interval& graphError){
 const interval angle=phase+p.chi;
 const interval rho(kRadius),u1=rho*cos(angle),u2=rho*sin(angle),du1=-rho*sin(angle),du2=rho*cos(angle);
 if(u1.contains(0.))
   throw std::runtime_error("zero-energy source solve has u1 containing zero");
 interval s1=polynomial(kH1Terms,u1,u2)+graphError;
 const interval h1x=polynomial(kH1Terms,u1,u2,1,0),h1y=polynomial(kH1Terms,u1,u2,0,1);
 interval ds1=h1x*du1+h1y*du2;
 const interval U=u1+s1;
 const interval numerator=-u2*s1-p.a*power(U,3)/(interval(6.)*p.h)
   +p.b*power(U,4)/(interval(8.)*p.h);
 const interval s2=numerator/u1;
 const interval dU=du1+ds1;
 const interval dNumerator=-du2*s1-u2*ds1
   -p.a*sqr(U)*dU/(interval(2.)*p.h)
   +p.b*power(U,3)*dU/(interval(2.)*p.h);
 const interval ds2=(dNumerator*u1-numerator*du1)/sqr(u1);
 const interval es1(1.);
 const interval es2=(-u2-p.a*sqr(U)/(interval(2.)*p.h)
   +p.b*power(U,3)/(interval(2.)*p.h))/u1;
 IVector z(4),d(4),e(4);
 z[0]=U;
 z[1]=p.alpha*u1-p.beta*u2-p.alpha*s1+p.beta*s2;
 z[2]=p.c*u1/interval(2.)+p.h*u2+p.c*s1/interval(2.)+p.h*s2;
 z[3]=p.alpha*u1+p.beta*u2-p.alpha*s1-p.beta*s2;
 d[0]=dU;
 d[1]=p.alpha*du1-p.beta*du2-p.alpha*ds1+p.beta*ds2;
 d[2]=p.c*du1/interval(2.)+p.h*du2+p.c*ds1/interval(2.)+p.h*ds2;
 d[3]=p.alpha*du1+p.beta*du2-p.alpha*ds1-p.beta*ds2;
 e[0]=es1;
 e[1]=-p.alpha*es1+p.beta*es2;
 e[2]=p.c*es1/interval(2.)+p.h*es2;
 e[3]=-p.alpha*es1-p.beta*es2;
 return {z,d,e};
}
double midpointValue(const interval&x){return x.mid().leftBound();}
interval pointAtMidpoint(const interval&x){return interval(midpointValue(x));}
double absUpper(const interval&x){return std::max(std::abs(x.leftBound()),std::abs(x.rightBound()));}
bool interior(const interval&x,const interval&y){return y.leftBound()<x.leftBound()&&x.rightBound()<y.rightBound();}
IVector pointMid(const IVector&x){IVector y(x.dimension());for(int i=0;i<x.dimension();++i)y[i]=interval(midpointValue(x[i]));return y;}
IVector pointMatVec(const IMatrix&A,const IVector&x){IVector y(A.numberOfRows());for(int i=0;i<A.numberOfRows();++i){double s=0.;for(int j=0;j<A.numberOfColumns();++j)s+=midpointValue(A[i][j])*midpointValue(x[j]);y[i]=interval(s);}return y;}
IVector flowC0(IOdeSolver&solver,const IVector&z,const interval&t){ITimeMap tm(solver);C0HOTripletonSet set(z);return tm(t,set);}
std::pair<IVector,IMatrix> flowC1(IOdeSolver&solver,const IVector&z,const interval&t){ITimeMap tm(solver);C1HORect2Set set(z);IVector out=tm(t,set);return {out,(IMatrix)set};}
IMatrix midpointInverse(const IMatrix&D){int n=D.numberOfRows();DMatrix M(n,n);for(int i=0;i<n;++i)for(int j=0;j<n;++j)M[i][j]=midpointValue(D[i][j]);DMatrix inv=matrixAlgorithms::inverseMatrix(M);IMatrix C(n,n);for(int i=0;i<n;++i)for(int j=0;j<n;++j)C[i][j]=interval(inv[i][j]);return C;}
struct DerivativeData{
  IMatrix D;
  IVector endpoint;
  IVector endpointPhaseColumn;
  interval returnTime;
};

constexpr double kA2SlopeStep=1.e-3;
constexpr double kPhaseA2Slope=.4343321825175;

struct PointOrbit{
  SourceData source;
  std::vector<IVector> nodes;
  std::vector<IVector> phaseTangents;
  std::vector<IVector> errorTangents;
};

PointOrbit pointOrbit(const Parameters&p,const interval&phase){
  IMap field("par:a,b,c;var:U,P,V,Q;"
             "fun:P,c*U-V-a*U*U+b*U*U*U,Q,U;");
  field.setParameter("a",p.a);field.setParameter("b",p.b);
  field.setParameter("c",p.c);
  IOdeSolver solver(field,30);
  solver.setAbsoluteTolerance(1e-14);solver.setRelativeTolerance(1e-14);
  const SourceData rawSource=sourceData(p,phase,interval(0.));
  SourceData source{pointMid(rawSource.state),pointMid(rawSource.phaseDerivative),
                    pointMid(rawSource.errorDerivative)};
  IVector z=source.state,v=source.phaseDerivative,w=source.errorDerivative;
  PointOrbit result{source,{},{},{}};
  result.nodes.reserve(kSegments);result.phaseTangents.reserve(kSegments);
  result.errorTangents.reserve(kSegments);
  for(int i=0;i<kSegments;++i){
    const interval step(kNodeTimes[i]-(i?kNodeTimes[i-1]:0.));
    auto [out,A]=flowC1(solver,z,step);
    z=pointMid(out);v=pointMatVec(A,v);w=pointMatVec(A,w);
    result.nodes.push_back(z);result.phaseTangents.push_back(v);
    result.errorTangents.push_back(w);
  }
  return result;
}

IVector pointDifference(const IVector&plus,const IVector&minus,double width){
  IVector result(plus.dimension());
  for(int i=0;i<plus.dimension();++i)
    result[i]=interval((midpointValue(plus[i])-midpointValue(minus[i]))/width);
  return result;
}

IVector augmentedCentre(const IVector&physical){
  IVector result(7);
  for(int i=0;i<4;++i)result[i]=physical[i];
  for(int i=4;i<7;++i)result[i]=interval(0.);
  return result;
}

IMatrix residualFrame(const IVector&parameterSlope,const IVector&phaseSlope,
                      const IVector&errorSlope){
  IMatrix result(4,7);
  for(int i=0;i<4;++i){
    for(int j=0;j<7;++j)result[i][j]=interval(0.);
    result[i][i]=interval(1.);
    result[i][4]=-parameterSlope[i];
    result[i][5]=-phaseSlope[i];
    result[i][6]=-errorSlope[i];
  }
  return result;
}

struct AffineInitialData{
  IVector centre;
  IMatrix coordinates;
  IVector radii;
  IVector remainder;
};

struct FirstJet{
  interval value;
  std::array<interval,3> derivative;
  explicit FirstJet(const interval&v=interval(0.))
    :value(v),derivative{interval(0.),interval(0.),interval(0.)}{}
  static FirstJet variable(const interval&v,int column){
    FirstJet result(v);result.derivative[column]=interval(1.);return result;
  }
};

FirstJet operator+(const FirstJet&x,const FirstJet&y){
  FirstJet result(x.value+y.value);
  for(int i=0;i<3;++i)result.derivative[i]=x.derivative[i]+y.derivative[i];
  return result;
}
FirstJet operator-(const FirstJet&x,const FirstJet&y){
  FirstJet result(x.value-y.value);
  for(int i=0;i<3;++i)result.derivative[i]=x.derivative[i]-y.derivative[i];
  return result;
}
FirstJet operator-(const FirstJet&x){
  FirstJet result(-x.value);
  for(int i=0;i<3;++i)result.derivative[i]=-x.derivative[i];
  return result;
}
FirstJet operator*(const FirstJet&x,const FirstJet&y){
  FirstJet result(x.value*y.value);
  for(int i=0;i<3;++i)
    result.derivative[i]=x.derivative[i]*y.value+x.value*y.derivative[i];
  return result;
}
FirstJet jetReciprocal(const FirstJet&x){
  FirstJet result(interval(1.)/x.value);
  for(int i=0;i<3;++i)
    result.derivative[i]=-x.derivative[i]/sqr(x.value);
  return result;
}
FirstJet operator/(const FirstJet&x,const FirstJet&y){
  return x*jetReciprocal(y);
}
FirstJet jetPower(FirstJet x,int exponent){
  FirstJet result(interval(1.));
  for(int i=0;i<exponent;++i)result=result*x;
  return result;
}
FirstJet jetSquare(const FirstJet&x){
  FirstJet result(sqr(x.value));
  for(int i=0;i<3;++i)
    result.derivative[i]=interval(2.)*x.value*x.derivative[i];
  return result;
}
FirstJet jetSqrt(const FirstJet&x){
  FirstJet result(sqrt(x.value));
  for(int i=0;i<3;++i)
    result.derivative[i]=x.derivative[i]/(interval(2.)*result.value);
  return result;
}
FirstJet jetSin(const FirstJet&x){
  FirstJet result(sin(x.value));
  for(int i=0;i<3;++i)result.derivative[i]=cos(x.value)*x.derivative[i];
  return result;
}
FirstJet jetCos(const FirstJet&x){
  FirstJet result(cos(x.value));
  for(int i=0;i<3;++i)result.derivative[i]=-sin(x.value)*x.derivative[i];
  return result;
}
FirstJet jetAtan(const FirstJet&x){
  FirstJet result(atan(x.value));
  for(int i=0;i<3;++i)
    result.derivative[i]=x.derivative[i]/(interval(1.)+sqr(x.value));
  return result;
}

template<std::size_t Size>
FirstJet jetPolynomial(const PolynomialTerm(&terms)[Size],
                       const FirstJet&x,const FirstJet&y){
  FirstJet result(interval(0.));
  for(const auto&term:terms)
    result=result+FirstJet(coefficient(term))*jetPower(x,term.px)
      *jetPower(y,term.py);
  return result;
}

std::array<FirstJet,4> sourceFirstJet(
    const interval&fixedR,const interval&a2Centre,const interval&phi0,
    const interval&etaBox,const interval&deltaBox,const interval&errorBox){
  const FirstJet eta=FirstJet::variable(etaBox,0);
  const FirstJet delta=FirstJet::variable(deltaBox,1);
  const FirstJet graphError=FirstJet::variable(errorBox,2);
  const FirstJet one(interval(1.)),two(interval(2.));
  const FirstJet r(fixedR),r2=jetSquare(r),r3=r2*r,r4=jetSquare(r2);
  const FirstJet q=FirstJet(a2Centre)+eta;
  const FirstJet a=one+r3*q;
  const FirstJet b=r2/FirstJet(interval(3.));
  const FirstJet c=two*r*q+r4*jetSquare(q);
  if((two.value+c.value).leftBound()<=0.
      || (two.value-c.value).leftBound()<=0.)
    throw std::runtime_error("affine source leaves the real saddle-focus frame");
  const FirstJet alpha=FirstJet(interval(.5))*jetSqrt(two+c);
  const FirstJet beta=FirstJet(interval(.5))*jetSqrt(two-c);
  const FirstJet h=FirstJet(interval(.5))*jetSqrt(
    FirstJet(interval(4.))-jetSquare(c));
  if(beta.value.contains(0.) || h.value.contains(0.))
    throw std::runtime_error("affine source has a singular physical frame");
  const FirstJet inverseSqrtTwo=one/jetSqrt(two);
  const FirstJet chi=jetAtan((inverseSqrtTwo-alpha)/beta);
  const FirstJet angle=FirstJet(phi0)+FirstJet(interval(kPhaseA2Slope))*eta
    +delta+chi;
  const FirstJet u1=FirstJet(interval(kRadius))*jetCos(angle);
  const FirstJet u2=FirstJet(interval(kRadius))*jetSin(angle);
  if(u1.value.contains(0.))
    throw std::runtime_error("affine zero-energy source has u1 containing zero");
  const FirstJet s1=jetPolynomial(kH1Terms,u1,u2)+graphError;
  const FirstJet U=u1+s1;
  const FirstJet s2=-s1*u2/u1-a*jetPower(U,3)/(FirstJet(interval(6.))*h*u1)
    +b*jetPower(U,4)/(FirstJet(interval(8.))*h*u1);
  std::array<FirstJet,4> state;
  state[0]=U;
  state[1]=alpha*u1-beta*u2-alpha*s1+beta*s2;
  state[2]=c*u1/FirstJet(interval(2.))+h*u2
    +c*s1/FirstJet(interval(2.))+h*s2;
  state[3]=alpha*u1+beta*u2-alpha*s1-beta*s2;
  return state;
}

AffineInitialData affineNodeData(
    const IVector&centre,const IVector&parameterSlope,
    const IVector&phaseSlope,const IVector&errorSlope,
    const interval&eta,const interval&delta,const interval&graphError,
    const std::array<interval,4>&nodeRemainder){
  IVector x=augmentedCentre(centre),r0(7),remainder(7);
  IMatrix C(7,7);
  for(int i=0;i<7;++i){
    r0[i]=interval(0.);remainder[i]=interval(0.);
    for(int j=0;j<7;++j)C[i][j]=interval(0.);
  }
  r0[0]=eta;r0[1]=delta;r0[2]=graphError;
  for(int j=0;j<4;++j)r0[3+j]=nodeRemainder[j];
  for(int i=0;i<4;++i){
    C[i][0]=parameterSlope[i];C[i][1]=phaseSlope[i];
    C[i][2]=errorSlope[i];C[i][3+i]=interval(1.);
  }
  C[4][0]=interval(1.);C[5][1]=interval(1.);C[6][2]=interval(1.);
  return {x,C,r0,remainder};
}

AffineInitialData affineSourceData(
    const interval&fixedR,const interval&a2Centre,const interval&phi0,
    const IVector&sourceCentre,const IVector&parameterSlope,
    const IVector&phaseSlope,const IVector&errorSlope,const interval&eta,
    const interval&delta,const interval&graphError){
  const std::array<interval,4> zero={interval(0.),interval(0.),
                                     interval(0.),interval(0.)};
  AffineInitialData result=affineNodeData(
    sourceCentre,parameterSlope,phaseSlope,errorSlope,
    eta,delta,graphError,zero);
  const std::array<FirstJet,4> jet=sourceFirstJet(
    fixedR,a2Centre,phi0,eta,delta,graphError);
  const Parameters centreParameters=parameters(
    fixedR,a2Centre,interval(1.));
  const SourceData exactCentre=sourceData(
    centreParameters,phi0,interval(0.));
  for(int i=0;i<4;++i){
    interval raw=exactCentre.state[i]-sourceCentre[i];
    raw+=(jet[i].derivative[0]-parameterSlope[i])*eta;
    raw+=(jet[i].derivative[1]-phaseSlope[i])*delta;
    raw+=(jet[i].derivative[2]-errorSlope[i])*graphError;
    const double radius=absUpper(raw);
    result.remainder[i]=interval(-radius,radius);
  }
  return result;
}

IVector initialColumn(const IVector&physical,int staticIndex){
  IVector result(7);
  for(int i=0;i<7;++i)result[i]=interval(0.);
  for(int i=0;i<4;++i)result[i]=physical[i];
  result[staticIndex]=interval(1.);
  return result;
}

struct AffineEvaluation{
  IVector residual;
  IMatrix derivative;
  IVector endpoint;
  IVector endpointPhaseColumn;
  interval returnTime;
};

struct A2AffineCellResult{
  bool success;
  interval a2Cell,a2Centre,phi0;
  PointOrbit chart;
  std::vector<IVector> parameterSlopes;
  IVector X,K;
  double maxInclusion,maxContraction;
  interval determinant;
};

A2AffineCellResult buildA2AffineCell(
    double radiusFactor,const interval&a2Cell,const interval&phi0,
    bool report){
  if(a2Cell.leftBound()>=a2Cell.rightBound())
    throw std::invalid_argument("a2-affine cell must have positive width");
  const interval certifiedA2Domain("-0.25","0.25");
  if(a2Cell.leftBound()<certifiedA2Domain.leftBound()
      || a2Cell.rightBound()>certifiedA2Domain.rightBound())
    throw std::invalid_argument("a2-affine cell leaves the certified graph domain");
  // Derive every source and flow coefficient from one outward enclosure of
  // the exact primary-face rational; independent decimal literals can miss
  // one another by an ulp and would describe a nearby artificial problem.
  const interval fixedR=interval(2.)/interval(25.);
  const double a2CentreValue=midpointValue(a2Cell);
  const interval a2Centre(a2CentreValue);
  const interval eta=a2Cell-a2Centre;
  const interval reconstructedCell=a2Centre+eta;
  if(!eta.contains(0.)
      || reconstructedCell.leftBound()>a2Cell.leftBound()
      || reconstructedCell.rightBound()<a2Cell.rightBound())
    throw std::runtime_error("outward eta coordinates do not cover the a2 cell");
  const Parameters centreParameters=parameters(
    fixedR,a2Centre,interval(1.));
  const interval slopeStep(kA2SlopeStep);
  const Parameters plusParameters=parameters(
    fixedR,a2Centre+slopeStep,interval(1.));
  const Parameters minusParameters=parameters(
    fixedR,a2Centre-slopeStep,interval(1.));
  const PointOrbit centre=pointOrbit(centreParameters,phi0);
  const PointOrbit plus=pointOrbit(
    plusParameters,phi0+interval(kPhaseA2Slope*kA2SlopeStep));
  const PointOrbit minus=pointOrbit(
    minusParameters,phi0-interval(kPhaseA2Slope*kA2SlopeStep));
  const IVector sourceParameterSlope=pointDifference(
    plus.source.state,minus.source.state,2.*kA2SlopeStep);
  std::vector<IVector> parameterSlopes;
  parameterSlopes.reserve(kSegments);
  for(int i=0;i<kSegments;++i)
    parameterSlopes.push_back(pointDifference(
      plus.nodes[i],minus.nodes[i],2.*kA2SlopeStep));

  IMap augmentedField(
    "par:r3,r4,ac,cc,ce,b;var:U,P,V,Q,eta,delta,e;"
    "fun:P,(cc+ce*eta+r4*eta*eta)*U-V-(ac+r3*eta)*U*U+"
    "b*U*U*U,Q,U,0,0,0;");
  const interval r2=sqr(fixedR),r3=r2*fixedR,r4=sqr(r2);
  const interval twoR=interval(2.)*fixedR;
  augmentedField.setParameter("r3",r3);
  augmentedField.setParameter("r4",r4);
  augmentedField.setParameter("ac",interval(1.)+r3*a2Centre);
  augmentedField.setParameter("cc",twoR*a2Centre+r4*sqr(a2Centre));
  augmentedField.setParameter("ce",twoR+interval(2.)*r4*a2Centre);
  augmentedField.setParameter("b",r2/interval(3.));
  IOdeSolver solver(augmentedField,30);
  solver.setAbsoluteTolerance(1e-14);solver.setRelativeTolerance(1e-14);
  ICoordinateSection section(7,3);
  const int dimension=2+4*kSegments;
  C1HORect2Set referenceSet(augmentedCentre(centre.nodes.back()));
  IPoincareMap referencePoincare(solver,section,poincare::MinusPlus);
  interval referenceReturnTime;
  const IVector referenceEndpoint=referencePoincare(
    referenceSet,referenceReturnTime);
  const interval referencePDot=centreParameters.c*referenceEndpoint[0]
    -referenceEndpoint[2]-centreParameters.a*sqr(referenceEndpoint[0])
    +centreParameters.b*power(referenceEndpoint[0],3);
  const interval eventShear(-midpointValue(referencePDot/referenceEndpoint[0]));

  auto evaluate=[&](const IVector&X)->AffineEvaluation{
    IVector F(dimension);IMatrix D(dimension,dimension);
    for(int i=0;i<dimension;++i){
      F[i]=interval(0.);
      for(int j=0;j<dimension;++j)D[i][j]=interval(0.);
    }
    F[0]=interval(-kGraphC0,kGraphC0);
    D[0][0]=interval(-kGraphC1*kRadius,kGraphC1*kRadius);
    D[0][1]=interval(1.);
    IVector propagatedPhase(7);

    AffineInitialData firstData=affineSourceData(
      fixedR,a2Centre,phi0,centre.source.state,sourceParameterSlope,
      centre.source.phaseDerivative,centre.source.errorDerivative,
      eta,X[0],X[1]);
    C1HORect2Set firstSet(firstData.centre,firstData.coordinates,
                          firstData.radii,firstData.remainder);
    ITimeMap firstMap(solver);
    firstMap(interval(kNodeTimes[0]),firstSet);
    const IMatrix firstFrame=residualFrame(
      parameterSlopes[0],centre.phaseTangents[0],centre.errorTangents[0]);
    const IVector firstResidual=firstSet.affineTransformation(
      firstFrame,augmentedCentre(centre.nodes[0]));
    const IMatrix firstFlow=(IMatrix)firstSet;
    const IMatrix firstA=firstFrame*firstFlow;
    const Parameters naturalParameters=parameters(
      fixedR,a2Centre+eta,interval(1.));
    const SourceData naturalSource=sourceData(
      naturalParameters,phi0+interval(kPhaseA2Slope)*eta+X[0],X[1]);
    const IVector deltaColumn=initialColumn(naturalSource.phaseDerivative,5);
    const IVector errorColumn=initialColumn(naturalSource.errorDerivative,6);
    for(int j=0;j<4;++j){
      const int row=1+j;
      F[row]=-firstResidual[j];
      D[row][0]=-(firstA*deltaColumn)[j];
      D[row][1]=-(firstA*errorColumn)[j];
      D[row][2+j]=interval(1.);
    }
    const interval graphPrime(-kGraphC1*kRadius,kGraphC1*kRadius);
    propagatedPhase=firstFlow*(deltaColumn+errorColumn*graphPrime);

    for(int node=1;node<kSegments;++node){
      std::array<interval,4> xi;
      for(int j=0;j<4;++j)xi[j]=X[2+4*(node-1)+j];
      const AffineInitialData data=affineNodeData(
        centre.nodes[node-1],parameterSlopes[node-1],
        centre.phaseTangents[node-1],centre.errorTangents[node-1],
        eta,X[0],X[1],xi);
      C1HORect2Set set(data.centre,data.coordinates,data.radii,data.remainder);
      ITimeMap map(solver);
      map(interval(kNodeTimes[node]-kNodeTimes[node-1]),set);
      const IMatrix frame=residualFrame(
        parameterSlopes[node],centre.phaseTangents[node],
        centre.errorTangents[node]);
      const IVector flowResidual=set.affineTransformation(
        frame,augmentedCentre(centre.nodes[node]));
      const IMatrix flow=(IMatrix)set;
      const IMatrix A=frame*flow;
      const IVector nodeDelta=initialColumn(centre.phaseTangents[node-1],5);
      const IVector nodeError=initialColumn(centre.errorTangents[node-1],6);
      for(int j=0;j<4;++j){
        const int row=1+4*node+j;
        F[row]=-flowResidual[j];
        D[row][0]=-(A*nodeDelta)[j];
        D[row][1]=-(A*nodeError)[j];
        D[row][2+4*node+j]=interval(1.);
        for(int k=0;k<4;++k)D[row][2+4*(node-1)+k]=-A[j][k];
      }
      propagatedPhase=flow*propagatedPhase;
    }

    std::array<interval,4> finalXi;
    for(int j=0;j<4;++j)finalXi[j]=X[2+4*(kSegments-1)+j];
    const AffineInitialData finalData=affineNodeData(
      centre.nodes.back(),parameterSlopes.back(),centre.phaseTangents.back(),
      centre.errorTangents.back(),eta,X[0],X[1],finalXi);
    C1HORect2Set residualSet(finalData.centre,finalData.coordinates,
                            finalData.radii,finalData.remainder);
    IPoincareMap residualPoincare(solver,section,poincare::MinusPlus);
    IVector eventCentre(7);
    for(int i=0;i<7;++i)eventCentre[i]=interval(0.);
    IMatrix eventCoordinates=IMatrix::Identity(7);
    // P+lambda*Q equals P on the Q=0 section.  Choosing lambda so that
    // its Lie derivative vanishes at the core event removes the dominant
    // first-order return-time wrapping without changing the equation.
    eventCoordinates[1][3]=eventShear;
    interval residualReturnTime;
    const IVector affineEndpoint=residualPoincare(
      residualSet,eventCentre,eventCoordinates,residualReturnTime);

    C1HORect2Set finalSet(finalData.centre,finalData.coordinates,
                          finalData.radii,finalData.remainder);
    IPoincareMap poincare(solver,section,poincare::MinusPlus);
    interval returnTime;IMatrix flowDerivative(7,7);
    const IVector endpoint=poincare(finalSet,flowDerivative,returnTime);
    const IMatrix DP=poincare.computeDP(endpoint,flowDerivative,returnTime);
    const IVector finalDelta=initialColumn(centre.phaseTangents.back(),5);
    const IVector finalError=initialColumn(centre.errorTangents.back(),6);
    // This overload evaluates the section residual directly in the
    // doubleton coordinates.  Taking endpoint[1] from the ordinary vector
    // hull discards the common eta/delta/e dependence before Krawczyk sees
    // it and causes severe wrapping at the last event.
    F[dimension-1]=affineEndpoint[1];
    D[dimension-1][0]=(DP*finalDelta)[1];
    D[dimension-1][1]=(DP*finalError)[1];
    for(int k=0;k<4;++k)D[dimension-1][2+4*(kSegments-1)+k]=DP[1][k];
    const IVector endpointPhase=DP*propagatedPhase;
    return {F,D,endpoint,endpointPhase,returnTime};
  };

  IVector zero(dimension),preliminary(dimension);
  for(int i=0;i<dimension;++i){zero[i]=interval(0.);preliminary[i]=interval(0.);}
  preliminary[0]=interval(-.002,.002);
  preliminary[1]=interval(-kGraphC0,kGraphC0);
  for(int i=2;i<dimension;++i)preliminary[i]=interval(-1e-8,1e-8);
  const AffineEvaluation base=evaluate(zero);
  const AffineEvaluation pre=evaluate(preliminary);
  const IMatrix Cpre=midpointInverse(pre.derivative);
  const IVector predicted=-(Cpre*base.residual);
  IVector X(dimension);
  for(int i=0;i<dimension;++i){
    const double floor=i==0?2e-5:(i==1?1e-8:3e-5);
    const double radius=radiusFactor*absUpper(predicted[i])+floor;
    X[i]=interval(-radius,radius);
  }
  const AffineInitialData sourceDiagnostic=affineSourceData(
    fixedR,a2Centre,phi0,centre.source.state,sourceParameterSlope,
    centre.source.phaseDerivative,centre.source.errorDerivative,
    eta,zero[0],zero[1]);
  if(report)
    std::cout<<std::setprecision(17)
      <<"mode a2-affine-cell\n"
      <<"parameters "<<fixedR<<" "<<a2Cell<<" "<<interval(1.)<<"\n"
      <<"a2_centre "<<a2Centre<<" eta "<<eta<<"\n"
      <<"phase_centre "<<phi0<<" phase_a2_slope "<<kPhaseA2Slope<<"\n"
      <<"event_shear "<<eventShear<<" reference_return "
         <<referenceReturnTime<<"\n"
      <<"source_columns "<<sourceParameterSlope<<" "
         <<centre.source.phaseDerivative<<" "
         <<centre.source.errorDerivative<<"\n"
      <<"source_zero_remainder "<<sourceDiagnostic.remainder<<"\n"
      <<"base_event_residual "<<base.residual[dimension-1]<<"\n"
      <<"pre_delta_prediction "<<predicted[0]<<" final_delta_box "<<X[0]<<"\n"
      <<"pre_last_node_boxes "<<X[dimension-4]<<" "<<X[dimension-3]
         <<" "<<X[dimension-2]<<" "<<X[dimension-1]<<"\n"<<std::flush;
  const AffineEvaluation data=evaluate(X);
  const IMatrix C=midpointInverse(data.derivative);
  const IMatrix R=IMatrix::Identity(dimension)-C*data.derivative;
  const IVector correction=-(C*base.residual),contraction=R*X;
  const IVector K=correction+contraction;
  double maxInclusion=0.,maxContraction=0.;int worstInclusion=-1,worstContraction=-1;
  bool inclusion=true;
  for(int i=0;i<dimension;++i){
    const double radius=absUpper(X[i]);
    const double inclusionRatio=absUpper(K[i])/radius;
    const double contractionRatio=absUpper(contraction[i])/radius;
    if(inclusionRatio>maxInclusion){maxInclusion=inclusionRatio;worstInclusion=i;}
    if(contractionRatio>maxContraction){maxContraction=contractionRatio;worstContraction=i;}
    inclusion=inclusion&&interior(K[i],X[i]);
  }
  const interval determinant=data.endpointPhaseColumn[1]*data.endpoint[0];
  const bool transverse=!determinant.contains(0.)
    && !data.endpointPhaseColumn[0].contains(0.)
    && !data.endpointPhaseColumn[2].contains(0.);
  const bool success=inclusion&&maxContraction<1.&&transverse
    &&data.endpoint[0].leftBound()>1.;
  if(report)
    std::cout<<std::setprecision(17)
      <<"source_full_box_remainder "<<affineSourceData(
         fixedR,a2Centre,phi0,centre.source.state,sourceParameterSlope,
         centre.source.phaseDerivative,centre.source.errorDerivative,
         eta,X[0],X[1]).remainder<<"\n"
      <<"base_event_residual "<<base.residual[dimension-1]<<"\n"
      <<"delta_predicted "<<predicted[0]<<" box "<<X[0]<<" K "<<K[0]<<"\n"
      <<"endpoint_box "<<data.endpoint<<" return_box "<<data.returnTime<<"\n"
      <<"event_delta_column "<<data.endpointPhaseColumn[1]<<"\n"
      <<"event_L_phase_column "<<data.endpointPhaseColumn[0]<<" "
         <<data.endpointPhaseColumn[2]<<"\n"
      <<"shooting_determinant "<<determinant<<"\n"
      <<"max_inclusion_ratio "<<maxInclusion<<" index "<<worstInclusion<<"\n"
      <<"max_contraction_ratio "<<maxContraction<<" index "<<worstContraction<<"\n"
      <<(success?"PASS":"INCONCLUSIVE")<<" a2-affine multiple shooting\n";
  return {success,a2Cell,a2Centre,phi0,centre,parameterSlopes,X,K,
          maxInclusion,maxContraction,determinant};
}

int runA2AffineCell(double radiusFactor,const interval&a2Cell,
                    const interval&phi0){
  return buildA2AffineCell(radiusFactor,a2Cell,phi0,true).success?0:20;
}

struct FaceContainmentResult{
  bool success;
  IVector mapped;
  double maxRatio;
  int worstIndex;
};

FaceContainmentResult mapFaceEnclosure(
    const A2AffineCellResult&source,const A2AffineCellResult&target,
    const interval&face){
  if(face.leftBound()<source.a2Cell.leftBound()
      || face.rightBound()>source.a2Cell.rightBound()
      || face.leftBound()<target.a2Cell.leftBound()
      || face.rightBound()>target.a2Cell.rightBound())
    throw std::invalid_argument("common face does not belong to both cells");
  if(source.K.dimension()!=target.X.dimension()
      || source.K.dimension()!=2+4*kSegments)
    throw std::runtime_error("incompatible affine shooting charts");
  const interval sourceEta=face-source.a2Centre;
  const interval targetEta=face-target.a2Centre;
  // Both source charts describe the same physical source phase.  This is
  // the exact affine change between their phase-correction coordinates.
  const interval deltaShift=source.phi0-target.phi0
    +interval(kPhaseA2Slope)*(sourceEta-targetEta);
  IVector mapped(source.K.dimension());
  mapped[0]=source.K[0]+deltaShift;
  mapped[1]=source.K[1];
  for(int node=0;node<kSegments;++node){
    for(int coordinate=0;coordinate<4;++coordinate){
      const int index=2+4*node+coordinate;
      mapped[index]=source.chart.nodes[node][coordinate]
        -target.chart.nodes[node][coordinate]
        +source.parameterSlopes[node][coordinate]*sourceEta
        -target.parameterSlopes[node][coordinate]*targetEta
        -target.chart.phaseTangents[node][coordinate]*deltaShift
        +(source.chart.phaseTangents[node][coordinate]
          -target.chart.phaseTangents[node][coordinate])*source.K[0]
        +(source.chart.errorTangents[node][coordinate]
          -target.chart.errorTangents[node][coordinate])*source.K[1]
        +source.K[index];
    }
  }
  bool success=source.success&&target.success;
  double maxRatio=0.;
  int worstIndex=-1;
  for(int i=0;i<mapped.dimension();++i){
    const double ratio=absUpper(mapped[i])/absUpper(target.X[i]);
    if(ratio>maxRatio){maxRatio=ratio;worstIndex=i;}
    success=success&&interior(mapped[i],target.X[i]);
  }
  return {success,mapped,maxRatio,worstIndex};
}

std::string shootingCoordinateName(int index){
  if(index<0)return "none";
  if(index==0)return "delta";
  if(index==1)return "graph-e";
  return "node-"+std::to_string((index-2)/4)+"-coordinate-"
    +std::to_string((index-2)%4);
}

int runA2CommonFaces(double radiusFactor,
                     const std::array<interval,4>&phaseCentres){
  // These are exact dyadic rationals.  Constructing them arithmetically
  // makes the common endpoints and the derived chart centres identical
  // outward interval objects in the two adjacent runs.
  const interval one(1.),zero(0.);
  const std::array<interval,5> faces={
    -one/interval(32.),-one/interval(64.),zero,
     one/interval(64.), one/interval(32.)};
  std::vector<A2AffineCellResult> cells;
  cells.reserve(4);
  bool success=true;
  std::cout<<std::setprecision(17)<<"mode a2-common-faces\n";
  for(int i=0;i<4;++i){
    const interval cell(faces[i].leftBound(),faces[i+1].rightBound());
    cells.push_back(buildA2AffineCell(
      radiusFactor,cell,phaseCentres[i],false));
    const A2AffineCellResult&result=cells.back();
    success=success&&result.success;
    std::cout<<"cell "<<i<<" "<<result.a2Cell
      <<" centre "<<result.a2Centre<<" phase "<<result.phi0
      <<" max_inclusion "<<result.maxInclusion
      <<" max_contraction "<<result.maxContraction
      <<" determinant "<<result.determinant<<" "
      <<(result.success?"PASS":"INCONCLUSIVE")<<"\n";
  }
  for(int faceIndex=1;faceIndex<4;++faceIndex){
    for(int direction=0;direction<2;++direction){
      const int sourceIndex=direction?faceIndex:faceIndex-1;
      const int targetIndex=direction?faceIndex-1:faceIndex;
      const FaceContainmentResult result=mapFaceEnclosure(
        cells[sourceIndex],cells[targetIndex],faces[faceIndex]);
      success=success&&result.success;
      std::cout<<"face "<<faces[faceIndex]<<" direction "
        <<sourceIndex<<"->"<<targetIndex
        <<" delta "<<result.mapped[0]
        <<" graph_e "<<result.mapped[1]
        <<" max_ratio "<<result.maxRatio
        <<" worst "<<result.worstIndex<<" "
        <<shootingCoordinateName(result.worstIndex)<<" "
        <<(result.success?"PASS":"INCONCLUSIVE")<<"\n";
      for(int node=0;node<kSegments;++node){
        double nodeRatio=0.;
        bool nodeSuccess=true;
        for(int coordinate=0;coordinate<4;++coordinate){
          const int index=2+4*node+coordinate;
          nodeRatio=std::max(nodeRatio,
            absUpper(result.mapped[index])/absUpper(cells[targetIndex].X[index]));
          nodeSuccess=nodeSuccess
            &&interior(result.mapped[index],cells[targetIndex].X[index]);
        }
        std::cout<<"face_node "<<faceIndex<<" direction "
          <<sourceIndex<<"->"<<targetIndex<<" node "<<node
          <<" max_ratio "<<nodeRatio<<" "
          <<(nodeSuccess?"PASS":"INCONCLUSIVE")<<"\n";
      }
    }
  }
  std::cout<<(success?"PASS":"INCONCLUSIVE")
    <<" common-face root identification\n";
  return success?0:20;
}
}

int main(int argc,char**argv){
 std::string stage="argument parsing";
 try{
 if(argc==6 && std::string(argv[1])=="a2-affine"){
   const double factor=std::stod(argv[2]);
   if(!std::isfinite(factor)||factor<=1.)
     throw std::invalid_argument("radius_factor must be finite and greater than one");
   stage="a2-affine cell experiment";
   return runA2AffineCell(factor,interval(argv[3],argv[4]),
                          interval(argv[5],argv[5]));
 }
 if(argc==7 && std::string(argv[1])=="a2-faces"){
   const double factor=std::stod(argv[2]);
   if(!std::isfinite(factor)||factor<=1.)
     throw std::invalid_argument("radius_factor must be finite and greater than one");
   std::array<interval,4> phaseCentres;
   for(int i=0;i<4;++i)phaseCentres[i]=interval(argv[3+i],argv[3+i]);
   stage="a2 common-face experiment";
   return runA2CommonFaces(factor,phaseCentres);
 }
 if(argc!=1 && argc!=6 && argc!=9)
   throw std::invalid_argument(
     "usage: [radius_factor r a2 epsilon phi0] or "
     "[radius_factor r_lo r_hi a2_lo a2_hi eps_lo eps_hi phi0] or "
     "[a2-affine radius_factor a2_lo a2_hi phi0] or "
     "[a2-faces radius_factor phi0_0 phi0_1 phi0_2 phi0_3]");
 const bool cellMode=argc==9;
 const double radiusFactor=argc==1?1.5:std::stod(argv[1]);
 if(!std::isfinite(radiusFactor) || radiusFactor<=1.)
   throw std::invalid_argument("radius_factor must be finite and greater than one");
 const interval r=cellMode?interval(argv[2],argv[3])
   :(argc==6?interval(argv[2],argv[2]):interval(0.));
 const interval a2=cellMode?interval(argv[4],argv[5])
   :(argc==6?interval(argv[3],argv[3]):interval(0.));
 const interval epsilon=cellMode?interval(argv[6],argv[7])
   :(argc==6?interval(argv[4],argv[4]):interval(1.));
 const interval phi0=cellMode?interval(argv[8],argv[8])
   :(argc==6?interval(argv[5],argv[5])
     :interval("5.861505585644824","5.861505585644824"));
 if(epsilon.leftBound()<=0.)
   throw std::invalid_argument("epsilon must be positive");
 const Parameters pCell=parameters(r,a2,epsilon);
 const Parameters pCentre=cellMode
   ?parameters(pointAtMidpoint(r),pointAtMidpoint(a2),pointAtMidpoint(epsilon))
   :pCell;
 if(pCell.c.leftBound()<=-2. || pCell.c.rightBound()>=2.)
   throw std::invalid_argument("parameter input lies outside the real saddle-focus frame");
 std::cout<<std::setprecision(17);
 std::cout<<"mode "<<(cellMode?"cell":"fixed")<<"\n"
          <<"parameters "<<pCell.r<<" "<<pCell.a2<<" "<<pCell.epsilon<<"\n"
          <<"centre_parameters "<<pCentre.r<<" "<<pCentre.a2<<" "<<pCentre.epsilon<<"\n"
          <<"coefficients "<<pCell.a<<" "<<pCell.b<<" "<<pCell.c<<"\n"
          <<"frame "<<pCell.alpha<<" "<<pCell.beta<<" "<<pCell.h<<" "<<pCell.chi<<"\n"
          <<"phase_centre "<<phi0<<"\n";
 stage="centre construction";
 IMap centreField("par:a,b,c;var:U,P,V,Q;fun:P,c*U-V-a*U*U+b*U*U*U,Q,U;");
 centreField.setParameter("a",pCentre.a);centreField.setParameter("b",pCentre.b);centreField.setParameter("c",pCentre.c);
 IOdeSolver centreSolver(centreField,30);centreSolver.setAbsoluteTolerance(1e-14);centreSolver.setRelativeTolerance(1e-14);
 IMap cellField("par:a,b,c;var:U,P,V,Q;fun:P,c*U-V-a*U*U+b*U*U*U,Q,U;");
 cellField.setParameter("a",pCell.a);cellField.setParameter("b",pCell.b);cellField.setParameter("c",pCell.c);
 IOdeSolver cellSolver(cellField,30);cellSolver.setAbsoluteTolerance(1e-14);cellSolver.setRelativeTolerance(1e-14);
 SourceData src0=sourceData(pCentre,phi0,interval(0.));std::vector<IVector> centres,tangents,errorTangents;centres.reserve(kSegments);tangents.reserve(kSegments);errorTangents.reserve(kSegments);IVector z=src0.state,v=src0.phaseDerivative,w=src0.errorDerivative;
 for(int i=0;i<kSegments;++i){interval step(kNodeTimes[i]-(i?kNodeTimes[i-1]:0.));auto [out,A]=flowC1(centreSolver,z,step);z=pointMid(out);v=pointMatVec(A,v);w=pointMatVec(A,w);centres.push_back(z);tangents.push_back(v);errorTangents.push_back(w);}
 stage="base residual propagation";
 const int n=2+4*kSegments;IVector F0(n);for(int i=0;i<n;++i)F0[i]=interval(0.);
 F0[0]=interval(-kGraphC0,kGraphC0);
 SourceData cellSourceCentre=sourceData(pCell,phi0,interval(0.));
 IVector firstCentre=flowC0(cellSolver,cellSourceCentre.state,interval(kNodeTimes[0]));for(int j=0;j<4;++j)F0[1+j]=centres[0][j]-firstCentre[j];
 for(int i=1;i<kSegments;++i){IVector out=flowC0(cellSolver,centres[i-1],interval(kNodeTimes[i]-kNodeTimes[i-1]));for(int j=0;j<4;++j)F0[1+4*i+j]=centres[i][j]-out[j];}
 ICoordinateSection section(4,3);IPoincareMap pc(cellSolver,section,poincare::MinusPlus);interval rt0;C0HOTripletonSet lastCentreSet(centres.back());IVector end0=pc(lastCentreSet,rt0);F0[n-1]=end0[1];
	 auto buildDerivative=[&](const IVector&X)->DerivativeData{
	   IMatrix D(n,n);for(int i=0;i<n;++i)for(int j=0;j<n;++j)D[i][j]=interval(0.);
	   D[0][0]=interval(-kGraphC1*kRadius,kGraphC1*kRadius);D[0][1]=interval(1.);
	   SourceData srcBox=sourceData(pCell,phi0+X[0],X[1]);auto [firstBox,A0]=flowC1(cellSolver,srcBox.state,interval(kNodeTimes[0]));IVector firstPhase=A0*srcBox.phaseDerivative,firstError=A0*srcBox.errorDerivative;
	   IVector trueSourcePhase=srcBox.phaseDerivative
	     + srcBox.errorDerivative*interval(-kGraphC1*kRadius,kGraphC1*kRadius);
	   IVector propagatedPhase=A0*trueSourcePhase;
	   for(int j=0;j<4;++j){int row=1+j;D[row][0]=tangents[0][j]-firstPhase[j];D[row][1]=errorTangents[0][j]-firstError[j];D[row][2+j]=interval(1.);}
	   for(int i=1;i<kSegments;++i){IVector physical(4);for(int j=0;j<4;++j)physical[j]=centres[i-1][j]+tangents[i-1][j]*X[0]+errorTangents[i-1][j]*X[1]+X[2+4*(i-1)+j];auto [out,A]=flowC1(cellSolver,physical,interval(kNodeTimes[i]-kNodeTimes[i-1]));propagatedPhase=A*propagatedPhase;for(int j=0;j<4;++j){int row=1+4*i+j;interval d=tangents[i][j],e=errorTangents[i][j];for(int k=0;k<4;++k){d-=A[j][k]*tangents[i-1][k];e-=A[j][k]*errorTangents[i-1][k];}D[row][0]=d;D[row][1]=e;D[row][2+4*i+j]=interval(1.);for(int k=0;k<4;++k)D[row][2+4*(i-1)+k]=-A[j][k];}}
	   IVector physical(4);for(int j=0;j<4;++j)physical[j]=centres.back()[j]+tangents.back()[j]*X[0]+errorTangents.back()[j]*X[1]+X[2+4*(kSegments-1)+j];IPoincareMap pb(cellSolver,section,poincare::MinusPlus);interval rt;C1HORect2Set set(physical);IMatrix flowDerivative(4,4);IVector endpoint=pb(set,flowDerivative,rt);IMatrix DP=pb.computeDP(endpoint,flowDerivative,rt);IVector endpointPhaseColumn=DP*propagatedPhase;interval d(0.),e(0.);for(int j=0;j<4;++j){d+=DP[1][j]*tangents.back()[j];e+=DP[1][j]*errorTangents.back()[j];}D[n-1][0]=d;D[n-1][1]=e;for(int j=0;j<4;++j)D[n-1][2+4*(kSegments-1)+j]=DP[1][j];return {D,endpoint,endpointPhaseColumn,rt};
 };
 IVector preliminary(n);preliminary[0]=interval(-.002,.002);preliminary[1]=interval(-kGraphC0,kGraphC0);for(int i=2;i<n;++i)preliminary[i]=interval(-1e-8,1e-8);
 stage="preliminary derivative enclosure";
 DerivativeData pre=buildDerivative(preliminary);IMatrix Cpre=midpointInverse(pre.D);IVector predicted=-(Cpre*F0);
 IVector X(n);for(int i=0;i<n;++i){double floor=i==0?2e-5:(i==1?1e-8:3e-5);double radius=radiusFactor*absUpper(predicted[i])+floor;X[i]=interval(-radius,radius);}
	 stage="final derivative enclosure";
	 DerivativeData data=buildDerivative(X);IMatrix C=midpointInverse(data.D);IMatrix R=IMatrix::Identity(n)-C*data.D;IVector correction=-(C*F0),contraction=R*X,K=correction+contraction;
	 double maxInc=0.,maxCon=0.;int wi=-1,wc=-1;bool incl=true;for(int i=0;i<n;++i){double rad=absUpper(X[i]),a=absUpper(K[i])/rad,b=absUpper(contraction[i])/rad;if(a>maxInc){maxInc=a;wi=i;}if(b>maxCon){maxCon=b;wc=i;}incl&=interior(K[i],X[i]);}
	 const interval determinant=data.endpointPhaseColumn[1]*data.endpoint[0];
	 const bool transverse=!determinant.contains(0.)
	   && !data.endpointPhaseColumn[0].contains(0.)
	   && !data.endpointPhaseColumn[2].contains(0.);
	 const bool nonzeroEndpoint=data.endpoint[0].leftBound()>1.;
	 const bool success=incl && maxCon<1. && transverse && nonzeroEndpoint;
 stage="reporting";
 std::cout<<"segments "<<kSegments<<" final_node_time "<<kNodeTimes.back()<<" radius_factor "<<radiusFactor<<"\n"
          <<"event_base_interval "<<end0<<" return "<<rt0<<" residual "<<F0[n-1]<<"\n"
          <<"delta_predicted "<<predicted[0]<<" radius "<<X[0]<<" correction "<<correction[0]<<" K "<<K[0]<<"\n"
          <<"graph_error_predicted "<<predicted[1]<<" radius "<<X[1]<<"\n"
          <<"last_predicted "<<predicted[n-5]<<" "<<predicted[n-4]<<" "<<predicted[n-3]<<" "<<predicted[n-2]<<"\n"
          <<"last_radii "<<X[n-5]<<" "<<X[n-4]<<" "<<X[n-3]<<" "<<X[n-2]<<"\n"
	          <<"endpoint_box "<<data.endpoint<<" return_box "<<data.returnTime<<"\n"
	          <<"event_delta_column "<<data.endpointPhaseColumn[1]<<"\n"
	          <<"event_L_phase_column "<<data.endpointPhaseColumn[0]<<" "<<data.endpointPhaseColumn[2]<<"\n"
	          <<"shooting_determinant "<<determinant<<"\n"
          <<"max_inclusion_ratio "<<maxInc<<" index "<<wi<<"\n"
          <<"max_contraction_ratio "<<maxCon<<" index "<<wc<<"\n"
	          <<(success?"PASS":"INCONCLUSIVE")<<" multiple shooting\n";
	 return success?0:20;
 }catch(const std::exception&e){std::cerr<<"FAIL at "<<stage<<": "<<e.what()<<"\n";return 10;}
}
