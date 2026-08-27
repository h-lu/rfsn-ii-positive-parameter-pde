#include <algorithm>
#include <array>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <stdexcept>
#include <string>
#include <utility>
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
interval cliPoint(const char*text){
  const std::string token(text);
  const std::size_t exponent=token.find_first_of("eE");
  const std::size_t mantissaEnd=exponent==std::string::npos?token.size():exponent;
  bool hasDigit=false,hasNonzeroDigit=false;
  for(std::size_t i=0;i<mantissaEnd;++i){
    if(token[i]>='0'&&token[i]<='9'){
      hasDigit=true;
      hasNonzeroDigit=hasNonzeroDigit||token[i]!='0';
    }
  }
  if(hasDigit&&!hasNonzeroDigit)return interval(0.);
  return interval(text,text);
}
interval cliCell(const char*left,const char*right){
  const interval lower=cliPoint(left),upper=cliPoint(right);
  return interval(lower.leftBound(),upper.rightBound());
}
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
  static constexpr int derivativeDimension=5;
  interval value;
  std::array<interval,derivativeDimension> derivative;
  explicit FirstJet(const interval&v=interval(0.))
    :value(v),derivative{interval(0.),interval(0.),interval(0.),
                         interval(0.),interval(0.)}{}
  static FirstJet variable(const interval&v,int column){
    FirstJet result(v);result.derivative[column]=interval(1.);return result;
  }
};

FirstJet operator+(const FirstJet&x,const FirstJet&y){
  FirstJet result(x.value+y.value);
  for(int i=0;i<FirstJet::derivativeDimension;++i)
    result.derivative[i]=x.derivative[i]+y.derivative[i];
  return result;
}
FirstJet operator-(const FirstJet&x,const FirstJet&y){
  FirstJet result(x.value-y.value);
  for(int i=0;i<FirstJet::derivativeDimension;++i)
    result.derivative[i]=x.derivative[i]-y.derivative[i];
  return result;
}
FirstJet operator-(const FirstJet&x){
  FirstJet result(-x.value);
  for(int i=0;i<FirstJet::derivativeDimension;++i)
    result.derivative[i]=-x.derivative[i];
  return result;
}
FirstJet operator*(const FirstJet&x,const FirstJet&y){
  FirstJet result(x.value*y.value);
  for(int i=0;i<FirstJet::derivativeDimension;++i)
    result.derivative[i]=x.derivative[i]*y.value+x.value*y.derivative[i];
  return result;
}
FirstJet jetReciprocal(const FirstJet&x){
  FirstJet result(interval(1.)/x.value);
  for(int i=0;i<FirstJet::derivativeDimension;++i)
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
  for(int i=0;i<FirstJet::derivativeDimension;++i)
    result.derivative[i]=interval(2.)*x.value*x.derivative[i];
  return result;
}
FirstJet jetSqrt(const FirstJet&x){
  FirstJet result(sqrt(x.value));
  for(int i=0;i<FirstJet::derivativeDimension;++i)
    result.derivative[i]=x.derivative[i]/(interval(2.)*result.value);
  return result;
}
FirstJet jetSin(const FirstJet&x){
  FirstJet result(sin(x.value));
  for(int i=0;i<FirstJet::derivativeDimension;++i)
    result.derivative[i]=cos(x.value)*x.derivative[i];
  return result;
}
FirstJet jetCos(const FirstJet&x){
  FirstJet result(cos(x.value));
  for(int i=0;i<FirstJet::derivativeDimension;++i)
    result.derivative[i]=-sin(x.value)*x.derivative[i];
  return result;
}
FirstJet jetAtan(const FirstJet&x){
  FirstJet result(atan(x.value));
  for(int i=0;i<FirstJet::derivativeDimension;++i)
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
  const interval origin(0.);
  const interval derivativeEta=intervalHull(eta,origin);
  const interval derivativeDelta=intervalHull(delta,origin);
  const interval derivativeGraphError=intervalHull(graphError,origin);
  const std::array<FirstJet,4> jet=sourceFirstJet(
    fixedR,a2Centre,phi0,derivativeEta,derivativeDelta,
    derivativeGraphError);
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

using MuBox=std::array<interval,3>;
using MuSlopes=std::array<IVector,3>;

std::array<FirstJet,4> muSourceFirstJet(
    const MuBox&centre,const MuBox&eta,const interval&phi0,
    const MuBox&phaseSlopes,const interval&deltaBox,
    const interval&errorBox){
  const FirstJet dr=FirstJet::variable(eta[0],0);
  const FirstJet da=FirstJet::variable(eta[1],1);
  const FirstJet deps=FirstJet::variable(eta[2],2);
  const FirstJet delta=FirstJet::variable(deltaBox,3);
  const FirstJet graphError=FirstJet::variable(errorBox,4);
  const FirstJet one(interval(1.)),two(interval(2.));
  const FirstJet r=FirstJet(centre[0])+dr;
  const FirstJet a2=FirstJet(centre[1])+da;
  const FirstJet epsilon=FirstJet(centre[2])+deps;
  if(epsilon.value.leftBound()<=0.)
    throw std::runtime_error("mu-affine source has nonpositive epsilon");
  const FirstJet rootEpsilon=jetSqrt(epsilon);
  const FirstJet r2=jetSquare(r),r3=r2*r,r4=jetSquare(r2);
  const FirstJet a=one+rootEpsilon*r3*a2;
  const FirstJet b=rootEpsilon*r2/FirstJet(interval(3.));
  const FirstJet c=two*r*a2+rootEpsilon*r4*jetSquare(a2);
  if((two.value+c.value).leftBound()<=0.
      || (two.value-c.value).leftBound()<=0.)
    throw std::runtime_error("mu-affine source leaves the real saddle-focus frame");
  const FirstJet alpha=FirstJet(interval(.5))*jetSqrt(two+c);
  const FirstJet beta=FirstJet(interval(.5))*jetSqrt(two-c);
  const FirstJet h=FirstJet(interval(.5))*jetSqrt(
    FirstJet(interval(4.))-jetSquare(c));
  if(beta.value.contains(0.) || h.value.contains(0.))
    throw std::runtime_error("mu-affine source has a singular physical frame");
  const FirstJet inverseSqrtTwo=one/jetSqrt(two);
  const FirstJet chi=jetAtan((inverseSqrtTwo-alpha)/beta);
  FirstJet angle=FirstJet(phi0)+delta+chi;
  angle=angle+FirstJet(phaseSlopes[0])*dr
    +FirstJet(phaseSlopes[1])*da+FirstJet(phaseSlopes[2])*deps;
  const FirstJet u1=FirstJet(interval(kRadius))*jetCos(angle);
  const FirstJet u2=FirstJet(interval(kRadius))*jetSin(angle);
  if(u1.value.contains(0.))
    throw std::runtime_error("mu-affine zero-energy source has u1 containing zero");
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

IVector muAugmentedCentre(const IVector&physical){
  IVector result(9);
  for(int i=0;i<4;++i)result[i]=physical[i];
  for(int i=4;i<9;++i)result[i]=interval(0.);
  return result;
}

IMatrix muResidualFrame(const MuSlopes&parameterSlopes,
                        const IVector&phaseSlope,
                        const IVector&errorSlope){
  IMatrix result(4,9);
  for(int i=0;i<4;++i){
    for(int j=0;j<9;++j)result[i][j]=interval(0.);
    result[i][i]=interval(1.);
    for(int parameter=0;parameter<3;++parameter)
      result[i][4+parameter]=-parameterSlopes[parameter][i];
    result[i][7]=-phaseSlope[i];
    result[i][8]=-errorSlope[i];
  }
  return result;
}

AffineInitialData muAffineNodeData(
    const IVector&centre,const MuSlopes&parameterSlopes,
    const IVector&phaseSlope,const IVector&errorSlope,
    const MuBox&eta,const interval&delta,const interval&graphError,
    const std::array<interval,4>&nodeRemainder){
  IVector x=muAugmentedCentre(centre),r0(9),remainder(9);
  IMatrix C(9,9);
  for(int i=0;i<9;++i){
    r0[i]=interval(0.);remainder[i]=interval(0.);
    for(int j=0;j<9;++j)C[i][j]=interval(0.);
  }
  for(int parameter=0;parameter<3;++parameter)r0[parameter]=eta[parameter];
  r0[3]=delta;r0[4]=graphError;
  for(int j=0;j<4;++j)r0[5+j]=nodeRemainder[j];
  for(int i=0;i<4;++i){
    for(int parameter=0;parameter<3;++parameter)
      C[i][parameter]=parameterSlopes[parameter][i];
    C[i][3]=phaseSlope[i];C[i][4]=errorSlope[i];
    C[i][5+i]=interval(1.);
  }
  for(int parameter=0;parameter<3;++parameter)C[4+parameter][parameter]=interval(1.);
  C[7][3]=interval(1.);C[8][4]=interval(1.);
  return {x,C,r0,remainder};
}

AffineInitialData muAffineSourceData(
    const MuBox&parameterCentre,const MuBox&eta,const interval&phi0,
    const MuBox&phaseSlopes,const IVector&sourceCentre,
    const MuSlopes&parameterSlopes,const IVector&phaseSlope,
    const IVector&errorSlope,const interval&delta,
    const interval&graphError){
  const std::array<interval,4> zero={interval(0.),interval(0.),
                                     interval(0.),interval(0.)};
  AffineInitialData result=muAffineNodeData(
    sourceCentre,parameterSlopes,phaseSlope,errorSlope,
    eta,delta,graphError,zero);
  const interval origin(0.);
  MuBox derivativeEta;
  for(int parameter=0;parameter<3;++parameter)
    derivativeEta[parameter]=intervalHull(eta[parameter],origin);
  const interval derivativeDelta=intervalHull(delta,origin);
  const interval derivativeGraphError=intervalHull(graphError,origin);
  const std::array<FirstJet,4> jet=muSourceFirstJet(
    parameterCentre,derivativeEta,phi0,phaseSlopes,derivativeDelta,
    derivativeGraphError);
  const Parameters centreParameters=parameters(
    parameterCentre[0],parameterCentre[1],parameterCentre[2]);
  const SourceData exactCentre=sourceData(
    centreParameters,phi0,interval(0.));
  for(int i=0;i<4;++i){
    interval raw=exactCentre.state[i]-sourceCentre[i];
    for(int parameter=0;parameter<3;++parameter)
      raw+=(jet[i].derivative[parameter]-parameterSlopes[parameter][i])
        *eta[parameter];
    raw+=(jet[i].derivative[3]-phaseSlope[i])*delta;
    raw+=(jet[i].derivative[4]-errorSlope[i])*graphError;
    const double radius=absUpper(raw);
    result.remainder[i]=interval(-radius,radius);
  }
  return result;
}

IVector muInitialColumn(const IVector&physical,int staticIndex){
  IVector result(9);
  for(int i=0;i<9;++i)result[i]=interval(0.);
  for(int i=0;i<4;++i)result[i]=physical[i];
  result[staticIndex]=interval(1.);
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

struct MuAffineCellResult{
  bool success;
  MuBox parameterCell,parameterCentre,phaseSlopes;
  interval phi0;
  PointOrbit chart;
  MuSlopes sourceParameterSlopes;
  std::vector<MuSlopes> parameterSlopes;
  IVector X,K;
  double maxInclusion,maxContraction;
  interval determinant;
};

MuAffineCellResult buildMuAffineCell(
    double radiusFactor,const MuBox&parameterCell,const interval&phi0,
    const MuBox&phaseSlopes,bool report,bool allowPointCell=false,
    const IVector*minimumX=nullptr){
  // Decimal CLI endpoints are parsed outward.  Use the same outward decimal
  // enclosure for the frozen rational bridge so boundary cells are accepted
  // and prove a harmless ulp-sized superset rather than being rejected.
  const MuBox certifiedDomain={interval(0.),
    interval("-0.25","-0.25"),interval("0.8","0.8")};
  const MuBox certifiedUpper={interval("0.08","0.08"),
    interval("0.25","0.25"),interval("1.2","1.2")};
  MuBox centre,eta;
  bool positiveWidth=false;
  for(int parameter=0;parameter<3;++parameter){
    if(parameterCell[parameter].leftBound()<certifiedDomain[parameter].leftBound()
        || parameterCell[parameter].rightBound()>certifiedUpper[parameter].rightBound())
      throw std::invalid_argument("mu-affine cell leaves the certified bridge");
    if(parameterCell[parameter].leftBound()>parameterCell[parameter].rightBound())
      throw std::invalid_argument("mu-affine cell has reversed endpoints");
    positiveWidth=positiveWidth
      ||parameterCell[parameter].leftBound()<parameterCell[parameter].rightBound();
    centre[parameter]=pointAtMidpoint(parameterCell[parameter]);
    eta[parameter]=parameterCell[parameter]-centre[parameter];
    const interval reconstructed=centre[parameter]+eta[parameter];
    if(!eta[parameter].contains(0.)
        ||reconstructed.leftBound()>parameterCell[parameter].leftBound()
        ||reconstructed.rightBound()<parameterCell[parameter].rightBound())
      throw std::runtime_error("outward mu coordinates do not cover the cell");
  }
  if(!positiveWidth&&!allowPointCell)
    throw std::invalid_argument("mu-affine mode requires a positive-width cell");
  if(parameterCell[2].leftBound()<=0.)
    throw std::invalid_argument("mu-affine epsilon must be positive");
  const Parameters cellParameters=parameters(
    parameterCell[0],parameterCell[1],parameterCell[2]);
  if(cellParameters.c.leftBound()<=-2. || cellParameters.c.rightBound()>=2.)
    throw std::invalid_argument("mu-affine cell leaves the real saddle-focus frame");
  const Parameters centreParameters=parameters(centre[0],centre[1],centre[2]);
  const PointOrbit chart=pointOrbit(centreParameters,phi0);

  const std::array<double,3> slopeSteps={1.e-4,1.e-3,1.e-3};
  std::vector<PointOrbit> plusOrbits,minusOrbits;
  plusOrbits.reserve(3);minusOrbits.reserve(3);
  for(int parameter=0;parameter<3;++parameter){
    MuBox plusCentre=centre,minusCentre=centre;
    plusCentre[parameter]+=interval(slopeSteps[parameter]);
    minusCentre[parameter]-=interval(slopeSteps[parameter]);
    plusOrbits.push_back(pointOrbit(
      parameters(plusCentre[0],plusCentre[1],plusCentre[2]),
      phi0+phaseSlopes[parameter]*interval(slopeSteps[parameter])));
    minusOrbits.push_back(pointOrbit(
      parameters(minusCentre[0],minusCentre[1],minusCentre[2]),
      phi0-phaseSlopes[parameter]*interval(slopeSteps[parameter])));
  }
  const MuSlopes sourceParameterSlopes={
    pointDifference(plusOrbits[0].source.state,minusOrbits[0].source.state,
                    interval(2.*slopeSteps[0]).mid().leftBound()),
    pointDifference(plusOrbits[1].source.state,minusOrbits[1].source.state,
                    interval(2.*slopeSteps[1]).mid().leftBound()),
    pointDifference(plusOrbits[2].source.state,minusOrbits[2].source.state,
                    interval(2.*slopeSteps[2]).mid().leftBound())};
  std::vector<MuSlopes> parameterSlopes;
  parameterSlopes.reserve(kSegments);
  for(int node=0;node<kSegments;++node){
    parameterSlopes.push_back(MuSlopes{
      pointDifference(plusOrbits[0].nodes[node],minusOrbits[0].nodes[node],
                      2.*slopeSteps[0]),
      pointDifference(plusOrbits[1].nodes[node],minusOrbits[1].nodes[node],
                      2.*slopeSteps[1]),
      pointDifference(plusOrbits[2].nodes[node],minusOrbits[2].nodes[node],
                      2.*slopeSteps[2])});
  }

  IMap augmentedField(
    "par:rc,a2c,epsc;var:U,P,V,Q,er,ea,ee,delta,ge;"
    "fun:P,(2*(rc+er)*(a2c+ea)+sqrt(epsc+ee)*(rc+er)^4*(a2c+ea)^2)*U-V-"
    "(1+sqrt(epsc+ee)*(rc+er)^3*(a2c+ea))*U*U+"
    "sqrt(epsc+ee)*(rc+er)^2/3*U*U*U,Q,U,0,0,0,0,0;");
  augmentedField.setParameter("rc",centre[0]);
  augmentedField.setParameter("a2c",centre[1]);
  augmentedField.setParameter("epsc",centre[2]);
  IOdeSolver solver(augmentedField,30);
  solver.setAbsoluteTolerance(1e-14);solver.setRelativeTolerance(1e-14);
  ICoordinateSection section(9,3);
  const int dimension=2+4*kSegments;

  C1HORect2Set referenceSet(muAugmentedCentre(chart.nodes.back()));
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
    IVector propagatedPhase(9);

    const AffineInitialData firstData=muAffineSourceData(
      centre,eta,phi0,phaseSlopes,chart.source.state,
      sourceParameterSlopes,chart.source.phaseDerivative,
      chart.source.errorDerivative,X[0],X[1]);
    C1HORect2Set firstSet(firstData.centre,firstData.coordinates,
                          firstData.radii,firstData.remainder);
    ITimeMap firstMap(solver);
    firstMap(interval(kNodeTimes[0]),firstSet);
    const IMatrix firstFrame=muResidualFrame(
      parameterSlopes[0],chart.phaseTangents[0],chart.errorTangents[0]);
    const IVector firstResidual=firstSet.affineTransformation(
      firstFrame,muAugmentedCentre(chart.nodes[0]));
    const IMatrix firstFlow=(IMatrix)firstSet;
    const IMatrix firstA=firstFrame*firstFlow;
    MuBox naturalBox;
    for(int parameter=0;parameter<3;++parameter)
      naturalBox[parameter]=centre[parameter]+eta[parameter];
    interval naturalPhase=phi0+X[0];
    for(int parameter=0;parameter<3;++parameter)
      naturalPhase+=phaseSlopes[parameter]*eta[parameter];
    const SourceData naturalSource=sourceData(
      parameters(naturalBox[0],naturalBox[1],naturalBox[2]),
      naturalPhase,X[1]);
    const IVector deltaColumn=muInitialColumn(naturalSource.phaseDerivative,7);
    const IVector errorColumn=muInitialColumn(naturalSource.errorDerivative,8);
    for(int coordinate=0;coordinate<4;++coordinate){
      const int row=1+coordinate;
      F[row]=-firstResidual[coordinate];
      D[row][0]=-(firstA*deltaColumn)[coordinate];
      D[row][1]=-(firstA*errorColumn)[coordinate];
      D[row][2+coordinate]=interval(1.);
    }
    const interval graphPrime(-kGraphC1*kRadius,kGraphC1*kRadius);
    propagatedPhase=firstFlow*(deltaColumn+errorColumn*graphPrime);

    for(int node=1;node<kSegments;++node){
      std::array<interval,4> xi;
      for(int coordinate=0;coordinate<4;++coordinate)
        xi[coordinate]=X[2+4*(node-1)+coordinate];
      const AffineInitialData data=muAffineNodeData(
        chart.nodes[node-1],parameterSlopes[node-1],
        chart.phaseTangents[node-1],chart.errorTangents[node-1],
        eta,X[0],X[1],xi);
      C1HORect2Set set(data.centre,data.coordinates,data.radii,data.remainder);
      ITimeMap map(solver);
      map(interval(kNodeTimes[node]-kNodeTimes[node-1]),set);
      const IMatrix frame=muResidualFrame(
        parameterSlopes[node],chart.phaseTangents[node],chart.errorTangents[node]);
      const IVector flowResidual=set.affineTransformation(
        frame,muAugmentedCentre(chart.nodes[node]));
      const IMatrix flow=(IMatrix)set;
      const IMatrix A=frame*flow;
      const IVector nodeDelta=muInitialColumn(chart.phaseTangents[node-1],7);
      const IVector nodeError=muInitialColumn(chart.errorTangents[node-1],8);
      for(int coordinate=0;coordinate<4;++coordinate){
        const int row=1+4*node+coordinate;
        F[row]=-flowResidual[coordinate];
        D[row][0]=-(A*nodeDelta)[coordinate];
        D[row][1]=-(A*nodeError)[coordinate];
        D[row][2+4*node+coordinate]=interval(1.);
        for(int k=0;k<4;++k)
          D[row][2+4*(node-1)+k]=-A[coordinate][k];
      }
      propagatedPhase=flow*propagatedPhase;
    }

    std::array<interval,4> finalXi;
    for(int coordinate=0;coordinate<4;++coordinate)
      finalXi[coordinate]=X[2+4*(kSegments-1)+coordinate];
    const AffineInitialData finalData=muAffineNodeData(
      chart.nodes.back(),parameterSlopes.back(),chart.phaseTangents.back(),
      chart.errorTangents.back(),eta,X[0],X[1],finalXi);
    C1HORect2Set residualSet(finalData.centre,finalData.coordinates,
                            finalData.radii,finalData.remainder);
    IPoincareMap residualPoincare(solver,section,poincare::MinusPlus);
    IVector eventCentre(9);
    for(int i=0;i<9;++i)eventCentre[i]=interval(0.);
    IMatrix eventCoordinates=IMatrix::Identity(9);
    eventCoordinates[1][3]=eventShear;
    interval residualReturnTime;
    const IVector affineEndpoint=residualPoincare(
      residualSet,eventCentre,eventCoordinates,residualReturnTime);

    C1HORect2Set finalSet(finalData.centre,finalData.coordinates,
                          finalData.radii,finalData.remainder);
    IPoincareMap poincareMap(solver,section,poincare::MinusPlus);
    interval returnTime;IMatrix flowDerivative(9,9);
    const IVector endpoint=poincareMap(finalSet,flowDerivative,returnTime);
    const IMatrix DP=poincareMap.computeDP(endpoint,flowDerivative,returnTime);
    const IVector finalDelta=muInitialColumn(chart.phaseTangents.back(),7);
    const IVector finalError=muInitialColumn(chart.errorTangents.back(),8);
    F[dimension-1]=affineEndpoint[1];
    D[dimension-1][0]=(DP*finalDelta)[1];
    D[dimension-1][1]=(DP*finalError)[1];
    for(int k=0;k<4;++k)
      D[dimension-1][2+4*(kSegments-1)+k]=DP[1][k];
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
  if(minimumX&&minimumX->dimension()!=dimension)
    throw std::invalid_argument("mu-affine prescribed box has wrong dimension");
  for(int i=0;i<dimension;++i){
    const double floor=i==0?2e-5:(i==1?1e-8:3e-5);
    double radius=radiusFactor*absUpper(predicted[i])+floor;
    if(minimumX)radius=std::max(radius,absUpper((*minimumX)[i]));
    X[i]=interval(-radius,radius);
  }
  const AffineInitialData sourceDiagnostic=muAffineSourceData(
    centre,eta,phi0,phaseSlopes,chart.source.state,sourceParameterSlopes,
    chart.source.phaseDerivative,chart.source.errorDerivative,zero[0],zero[1]);
  if(report)
    std::cout<<std::setprecision(17)
      <<"mode mu-affine-cell\n"
      <<"parameter_cell "<<parameterCell[0]<<" "<<parameterCell[1]<<" "
         <<parameterCell[2]<<"\n"
      <<"parameter_centre "<<centre[0]<<" "<<centre[1]<<" "<<centre[2]<<"\n"
      <<"parameter_eta "<<eta[0]<<" "<<eta[1]<<" "<<eta[2]<<"\n"
      <<"phase_centre "<<phi0<<" phase_slopes "<<phaseSlopes[0]<<" "
         <<phaseSlopes[1]<<" "<<phaseSlopes[2]<<"\n"
      <<"event_shear "<<eventShear<<" reference_return "<<referenceReturnTime<<"\n"
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
  double maxInclusion=0.,maxContraction=0.;
  int worstInclusion=-1,worstContraction=-1;
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
    &&!data.endpointPhaseColumn[0].contains(0.)
    &&!data.endpointPhaseColumn[2].contains(0.);
  const bool success=inclusion&&maxContraction<1.&&transverse
    &&data.endpoint[0].leftBound()>1.;
  if(report)
    std::cout<<std::setprecision(17)
      <<"source_full_box_remainder "<<muAffineSourceData(
         centre,eta,phi0,phaseSlopes,chart.source.state,sourceParameterSlopes,
         chart.source.phaseDerivative,chart.source.errorDerivative,X[0],X[1]).remainder
         <<"\n"
      <<"delta_predicted "<<predicted[0]<<" box "<<X[0]<<" K "<<K[0]<<"\n"
      <<"endpoint_box "<<data.endpoint<<" return_box "<<data.returnTime<<"\n"
      <<"event_delta_column "<<data.endpointPhaseColumn[1]<<"\n"
      <<"event_L_phase_column "<<data.endpointPhaseColumn[0]<<" "
         <<data.endpointPhaseColumn[2]<<"\n"
      <<"shooting_determinant "<<determinant<<"\n"
      <<"max_inclusion_ratio "<<maxInclusion<<" index "<<worstInclusion<<"\n"
      <<"max_contraction_ratio "<<maxContraction<<" index "<<worstContraction<<"\n"
      <<(success?"PASS":"INCONCLUSIVE")<<" mu-affine multiple shooting\n";
  return {success,parameterCell,centre,phaseSlopes,phi0,chart,
          sourceParameterSlopes,parameterSlopes,X,K,
          maxInclusion,maxContraction,determinant};
}

int runMuAffineCell(double radiusFactor,const MuBox&parameterCell,
                    const interval&phi0,const MuBox&phaseSlopes){
  return buildMuAffineCell(
    radiusFactor,parameterCell,phi0,phaseSlopes,true).success?0:20;
}

FaceContainmentResult mapMuFaceEnclosure(
    const MuAffineCellResult&source,const MuAffineCellResult&target,
    const MuBox&face){
  for(int parameter=0;parameter<3;++parameter){
    if(face[parameter].leftBound()<source.parameterCell[parameter].leftBound()
        ||face[parameter].rightBound()>source.parameterCell[parameter].rightBound()
        ||face[parameter].leftBound()<target.parameterCell[parameter].leftBound()
        ||face[parameter].rightBound()>target.parameterCell[parameter].rightBound())
      throw std::invalid_argument("common mu face does not belong to both cells");
  }
  if(source.K.dimension()!=target.X.dimension()
      ||source.K.dimension()!=2+4*kSegments
      ||source.parameterSlopes.size()!=kSegments
      ||target.parameterSlopes.size()!=kSegments)
    throw std::runtime_error("incompatible mu-affine shooting charts");
  MuBox faceCentre,faceOffset,sourceCentreOffset,targetCentreOffset;
  MuBox phaseSlopeDifference;
  interval deltaConstant=source.phi0-target.phi0;
  for(int parameter=0;parameter<3;++parameter){
    // A face parameter is one shared interval variable.  Centre the exact
    // affine difference so interval arithmetic does not treat the same
    // parameter as two independent copies in the source and target charts.
    faceCentre[parameter]=pointAtMidpoint(face[parameter]);
    faceOffset[parameter]=face[parameter]-faceCentre[parameter];
    sourceCentreOffset[parameter]=
      faceCentre[parameter]-source.parameterCentre[parameter];
    targetCentreOffset[parameter]=
      faceCentre[parameter]-target.parameterCentre[parameter];
    phaseSlopeDifference[parameter]=source.phaseSlopes[parameter]
      -target.phaseSlopes[parameter];
    deltaConstant+=source.phaseSlopes[parameter]
        *sourceCentreOffset[parameter]
      -target.phaseSlopes[parameter]*targetCentreOffset[parameter];
  }
  interval deltaShift=deltaConstant;
  for(int parameter=0;parameter<3;++parameter)
    deltaShift+=phaseSlopeDifference[parameter]*faceOffset[parameter];
  IVector mapped(source.K.dimension());
  mapped[0]=source.K[0]+deltaShift;
  mapped[1]=source.K[1];
  for(int node=0;node<kSegments;++node){
    for(int coordinate=0;coordinate<4;++coordinate){
      const int index=2+4*node+coordinate;
      interval physical=source.chart.nodes[node][coordinate]
        -target.chart.nodes[node][coordinate]
        -target.chart.phaseTangents[node][coordinate]*deltaConstant
        +(source.chart.phaseTangents[node][coordinate]
          -target.chart.phaseTangents[node][coordinate])*source.K[0]
        +(source.chart.errorTangents[node][coordinate]
          -target.chart.errorTangents[node][coordinate])*source.K[1]
        +source.K[index];
      for(int parameter=0;parameter<3;++parameter)
        physical+=source.parameterSlopes[node][parameter][coordinate]
            *sourceCentreOffset[parameter]
          -target.parameterSlopes[node][parameter][coordinate]
            *targetCentreOffset[parameter]
          +(source.parameterSlopes[node][parameter][coordinate]
            -target.parameterSlopes[node][parameter][coordinate]
            -target.chart.phaseTangents[node][coordinate]
              *phaseSlopeDifference[parameter])
            *faceOffset[parameter];
      mapped[index]=physical;
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

std::pair<interval,MuBox> rFacePredictor(const interval&rCentre){
  const interval predictorBase("5.861505585644824","5.861505585644824");
  const interval predictorQuadratic("0.211","0.211");
  const interval phi0=pointAtMidpoint(
    predictorBase-predictorQuadratic*sqr(rCentre));
  const MuBox slopes={pointAtMidpoint(
    -interval(2.)*predictorQuadratic*rCentre),interval(0.),interval(0.)};
  return {phi0,slopes};
}

constexpr int kMuGridRCells=32;
constexpr int kMuGridA2Cells=128;
constexpr int kMuGridEpsilonCells=4;

interval muGridRFace(int index){
  if(index<0||index>kMuGridRCells)
    throw std::out_of_range("mu-grid r face index");
  return index==0?interval(0.):interval(index)/interval(400);
}

interval muGridA2Face(int index){
  if(index<0||index>kMuGridA2Cells)
    throw std::out_of_range("mu-grid a2 face index");
  const int numerator=index-64;
  return numerator==0?interval(0.):interval(numerator)/interval(256);
}

interval muGridEpsilonFace(int index){
  if(index<0||index>kMuGridEpsilonCells)
    throw std::out_of_range("mu-grid epsilon face index");
  const int numerator=8+index;
  return numerator==10?interval(1.):interval(numerator)/interval(10);
}

MuBox muGridCellBox(int rIndex,int a2Index,int epsilonIndex){
  const interval rLeft=muGridRFace(rIndex),rRight=muGridRFace(rIndex+1);
  const interval aLeft=muGridA2Face(a2Index),aRight=muGridA2Face(a2Index+1);
  const interval eLeft=muGridEpsilonFace(epsilonIndex);
  const interval eRight=muGridEpsilonFace(epsilonIndex+1);
  return {interval(rLeft.leftBound(),rRight.rightBound()),
          interval(aLeft.leftBound(),aRight.rightBound()),
          interval(eLeft.leftBound(),eRight.rightBound())};
}

std::pair<interval,MuBox> muGridPhasePredictor(const MuBox&centre){
  // This fitted binary64 polynomial chooses a shooting chart only.  It is
  // not an enclosure of the true phase or its derivatives: the phase
  // correction remains a Newton unknown and every proof gate below uses the
  // outward-rounded flow, source remainder, and full interval Jacobian.
  const double r=midpointValue(centre[0]);
  const double a2=midpointValue(centre[1]);
  const double epsilon=midpointValue(centre[2]);
  const double r2=r*r,r3=r2*r,r4=r2*r2,a2Squared=a2*a2;
  const double s=std::sqrt(epsilon)-1.;
  const double B0=5.861505575152651
    -.210967554368243*r2-.144824979256505*r4;
  const double B1=5.418818020704685*r
    -.00126716957025419*r2+1.744493268274117*r3;
  const double B2=.000246297424945125*r
    -1.933406374738756*r2+.232626825497133*r3;
  const double C0=-.211485862199655*r2-.187230618196915*r4;
  const double C1=-.00600542276151165*r+.203700985551162*r2;
  const double C2=.000510439999174864*r;
  const double phase=B0+a2*B1+a2Squared*B2
    +s*(C0+a2*C1+a2Squared*C2);
  const double phaseR=-2.*.210967554368243*r
    -4.*.144824979256505*r3
    +a2*(5.418818020704685-2.*.00126716957025419*r
      +3.*1.744493268274117*r2)
    +a2Squared*(.000246297424945125-2.*1.933406374738756*r
      +3.*.232626825497133*r2)
    +s*(-2.*.211485862199655*r-4.*.187230618196915*r3
      +a2*(-.00600542276151165+2.*.203700985551162*r)
      +a2Squared*.000510439999174864);
  const double phaseA2=B1+2.*a2*B2+s*(C1+2.*a2*C2);
  const double phaseEpsilon=(C0+a2*C1+a2Squared*C2)
    /(2.*std::sqrt(epsilon));
  return {interval(phase),
          MuBox{interval(phaseR),interval(phaseA2),interval(phaseEpsilon)}};
}

MuAffineCellResult buildMuGridBox(
    double radiusFactor,const MuBox&cell){
  MuBox centre;
  for(int parameter=0;parameter<3;++parameter)
    centre[parameter]=pointAtMidpoint(cell[parameter]);
  const auto predictor=muGridPhasePredictor(centre);
  return buildMuAffineCell(
    radiusFactor,cell,predictor.first,predictor.second,false);
}

MuAffineCellResult buildMuGridCell(
    double radiusFactor,int rIndex,int a2Index,int epsilonIndex){
  return buildMuGridBox(
    radiusFactor,muGridCellBox(rIndex,a2Index,epsilonIndex));
}

MuBox muRootEta(const MuAffineCellResult&cell){
  MuBox eta;
  for(int parameter=0;parameter<3;++parameter)
    eta[parameter]=cell.parameterCell[parameter]-cell.parameterCentre[parameter];
  return eta;
}

AffineInitialData muRootSourceData(const MuAffineCellResult&cell){
  // The actual root for the fixed true graph lies in K.  This source set
  // encloses that root; it does not assert that every point of K is a root.
  return muAffineSourceData(
    cell.parameterCentre,muRootEta(cell),cell.phi0,cell.phaseSlopes,
    cell.chart.source.state,cell.sourceParameterSlopes,
    cell.chart.source.phaseDerivative,cell.chart.source.errorDerivative,
    cell.K[0],cell.K[1]);
}

AffineInitialData muRootNodeData(
    const MuAffineCellResult&cell,int node){
  if(node<0||node>=kSegments)
    throw std::out_of_range("mu root node index");
  std::array<interval,4> correction;
  for(int coordinate=0;coordinate<4;++coordinate)
    correction[coordinate]=cell.K[2+4*node+coordinate];
  return muAffineNodeData(
    cell.chart.nodes[node],cell.parameterSlopes[node],
    cell.chart.phaseTangents[node],cell.chart.errorTangents[node],
    muRootEta(cell),cell.K[0],cell.K[1],correction);
}

C0HOTripletonSet muRootSet(const AffineInitialData&data){
  return C0HOTripletonSet(
    data.centre,data.coordinates,data.radii,data.remainder);
}

struct DenseSignResult{
  bool success;
  interval hull;
  int steps;
  std::array<interval,4> physicalHull;
};

bool hasRequiredSign(const interval&value,int sign){
  return sign>0?value.leftBound()>0.:value.rightBound()<0.;
}

DenseSignResult advanceAndRequireSign(
    IOdeSolver&solver,C0HOTripletonSet&set,const interval&targetTime,
    int component,int sign){
  const IVector initial=set;
  interval hull=initial[component];
  std::array<interval,4> physicalHull;
  for(int coordinate=0;coordinate<4;++coordinate)
    physicalHull[coordinate]=initial[coordinate];
  bool success=hasRequiredSign(hull,sign);
  int steps=0;
  ITimeMap timeMap(solver);
  timeMap.stopAfterStep(true);
  do{
    timeMap(targetTime,set);
    const IVector enclosure=set.getLastEnclosure();
    const interval signedComponent=enclosure[component];
    hull=intervalHull(hull,signedComponent);
    for(int coordinate=0;coordinate<4;++coordinate)
      physicalHull[coordinate]=intervalHull(
        physicalHull[coordinate],enclosure[coordinate]);
    success=success&&hasRequiredSign(signedComponent,sign);
    ++steps;
  }while(!timeMap.completed());
  return {success,hull,steps,physicalHull};
}

void mergeSignResult(
    DenseSignResult&aggregate,const DenseSignResult&piece,bool initialized){
  if(!initialized){aggregate=piece;return;}
  aggregate.success=aggregate.success&&piece.success;
  aggregate.hull=intervalHull(aggregate.hull,piece.hull);
  aggregate.steps+=piece.steps;
  for(int coordinate=0;coordinate<4;++coordinate)
    aggregate.physicalHull[coordinate]=intervalHull(
      aggregate.physicalHull[coordinate],piece.physicalHull[coordinate]);
}

struct MuFirstHitResult{
  bool success;
  DenseSignResult pPositive,qPositive,pNegative,qNegative,uPositive;
  interval returnTime;
  IVector endpoint;
};

MuFirstHitResult validateMuFirstHit(const MuAffineCellResult&cell){
  // This is the compact source-to-symmetry-event part of the first-hit
  // proof.  The origin-to-source exclusion is the separate P2a/P2bK local
  // graph argument recorded as an imported prerequisite in the report.
  IMap field(
    "par:rc,a2c,epsc;var:U,P,V,Q,er,ea,ee,delta,ge;"
    "fun:P,(2*(rc+er)*(a2c+ea)+sqrt(epsc+ee)*(rc+er)^4*(a2c+ea)^2)*U-V-"
    "(1+sqrt(epsc+ee)*(rc+er)^3*(a2c+ea))*U*U+"
    "sqrt(epsc+ee)*(rc+er)^2/3*U*U*U,Q,U,0,0,0,0,0;");
  field.setParameter("rc",cell.parameterCentre[0]);
  field.setParameter("a2c",cell.parameterCentre[1]);
  field.setParameter("epsc",cell.parameterCentre[2]);
  IOdeSolver solver(field,30);
  solver.setAbsoluteTolerance(1e-14);solver.setRelativeTolerance(1e-14);

  C0HOTripletonSet source=muRootSet(muRootSourceData(cell));
  DenseSignResult pPositive=advanceAndRequireSign(
    solver,source,interval(kNodeTimes[0]),1,+1);

  C0HOTripletonSet node0=muRootSet(muRootNodeData(cell,0));
  DenseSignResult qPositive=advanceAndRequireSign(
    solver,node0,interval(kNodeTimes[1]-kNodeTimes[0]),3,+1);

  C0HOTripletonSet node1=muRootSet(muRootNodeData(cell,1));
  const DenseSignResult qPositiveTail=advanceAndRequireSign(
    solver,node1,interval(1.90-kNodeTimes[1]),3,+1);
  mergeSignResult(qPositive,qPositiveTail,true);
  DenseSignResult pNegative=advanceAndRequireSign(
    solver,node1,interval(kNodeTimes[2]-kNodeTimes[1]),1,-1);

  for(int node=2;node<=3;++node){
    C0HOTripletonSet rootNode=muRootSet(muRootNodeData(cell,node));
    const DenseSignResult piece=advanceAndRequireSign(
      solver,rootNode,interval(kNodeTimes[node+1]-kNodeTimes[node]),1,-1);
    mergeSignResult(pNegative,piece,true);
  }
  C0HOTripletonSet node4=muRootSet(muRootNodeData(cell,4));
  const DenseSignResult pNegativeTail=advanceAndRequireSign(
    solver,node4,interval(7.35-kNodeTimes[4]),1,-1);
  mergeSignResult(pNegative,pNegativeTail,true);
  DenseSignResult qNegative=advanceAndRequireSign(
    solver,node4,interval(kNodeTimes[5]-kNodeTimes[4]),3,-1);

  for(int node=5;node<=7;++node){
    C0HOTripletonSet rootNode=muRootSet(muRootNodeData(cell,node));
    const DenseSignResult piece=advanceAndRequireSign(
      solver,rootNode,interval(kNodeTimes[node+1]-kNodeTimes[node]),3,-1);
    mergeSignResult(qNegative,piece,true);
  }

  const interval finalDuration=interval(1.)/interval(5.);
  const AffineInitialData finalData=muRootNodeData(cell,kSegments-1);
  C0HOTripletonSet finalTube=muRootSet(finalData);
  DenseSignResult uPositive=advanceAndRequireSign(
    solver,finalTube,finalDuration,0,+1);

  C0HOTripletonSet eventSet=muRootSet(finalData);
  ICoordinateSection section(9,3);
  IPoincareMap poincareMap(solver,section,poincare::MinusPlus);
  interval returnTime;
  const IVector endpoint=poincareMap(eventSet,returnTime);
  const bool eventSuccess=returnTime.leftBound()>0.
    &&returnTime.rightBound()<finalDuration.leftBound()
    &&endpoint[0].leftBound()>1.;
  const bool success=cell.success&&pPositive.success&&qPositive.success
    &&pNegative.success&&qNegative.success&&uPositive.success&&eventSuccess;
  return {success,pPositive,qPositive,pNegative,qNegative,uPositive,
          returnTime,endpoint};
}

void reportMuFirstHit(
    int rIndex,int a2Index,int epsilonIndex,
    const MuAffineCellResult&cell,const MuFirstHitResult&result){
  std::cout<<std::setprecision(17)
    <<"scope selected_source_to_symmetry_event\n"
    <<"indices "<<rIndex<<" "<<a2Index<<" "<<epsilonIndex<<"\n"
    <<"parameter_cell "<<cell.parameterCell[0]<<" "
       <<cell.parameterCell[1]<<" "<<cell.parameterCell[2]<<"\n"
    <<"P_positive_hull "<<result.pPositive.hull
       <<" steps "<<result.pPositive.steps<<" "
       <<(result.pPositive.success?"PASS":"INCONCLUSIVE")<<"\n"
    <<"Q_positive_hull "<<result.qPositive.hull
       <<" steps "<<result.qPositive.steps<<" "
       <<(result.qPositive.success?"PASS":"INCONCLUSIVE")<<"\n"
    <<"P_negative_hull "<<result.pNegative.hull
       <<" steps "<<result.pNegative.steps<<" "
       <<(result.pNegative.success?"PASS":"INCONCLUSIVE")<<"\n"
    <<"Q_negative_hull "<<result.qNegative.hull
       <<" steps "<<result.qNegative.steps<<" "
       <<(result.qNegative.success?"PASS":"INCONCLUSIVE")<<"\n"
    <<"U_final_hull "<<result.uPositive.hull
       <<" steps "<<result.uPositive.steps<<" "
       <<(result.uPositive.success?"PASS":"INCONCLUSIVE")<<"\n"
    <<"endpoint "<<result.endpoint<<" return_time "<<result.returnTime<<"\n"
    <<(result.success?"PASS":"INCONCLUSIVE")
       <<" mu-grid selected-source first symmetry hit\n";
}

int runMuGridFirstHitCell(
    double radiusFactor,int rIndex,int a2Index,int epsilonIndex){
  const MuAffineCellResult cell=buildMuGridCell(
    radiusFactor,rIndex,a2Index,epsilonIndex);
  const MuFirstHitResult result=validateMuFirstHit(cell);
  std::cout<<"mode mu-grid-first-hit\n";
  reportMuFirstHit(rIndex,a2Index,epsilonIndex,cell,result);
  return result.success?0:20;
}

struct MuFirstHitSlabStats{
  bool success=true,initialized=false;
  int count=0,passCount=0,denseSteps=0;
  interval pPositive,qPositive,pNegative,qNegative,uPositive,returnTime;
  std::array<interval,4> physicalHull;
  std::array<double,5> minimumSignedMargins;
  std::array<int,5> worstA2,worstEpsilon;
};

void updateMuFirstHitSlabStats(
    MuFirstHitSlabStats&stats,const MuFirstHitResult&result,
    int a2Index,int epsilonIndex){
  const std::array<double,5> margins={
    result.pPositive.hull.leftBound(),
    result.qPositive.hull.leftBound(),
    -result.pNegative.hull.rightBound(),
    -result.qNegative.hull.rightBound(),
    result.uPositive.hull.leftBound()};
  std::array<interval,4> cellPhysical=result.pPositive.physicalHull;
  const std::array<const DenseSignResult*,4> otherTubes={
    &result.qPositive,&result.pNegative,&result.qNegative,&result.uPositive};
  for(const DenseSignResult*tube:otherTubes)
    for(int coordinate=0;coordinate<4;++coordinate)
      cellPhysical[coordinate]=intervalHull(
        cellPhysical[coordinate],tube->physicalHull[coordinate]);
  if(!stats.initialized){
    stats.pPositive=result.pPositive.hull;
    stats.qPositive=result.qPositive.hull;
    stats.pNegative=result.pNegative.hull;
    stats.qNegative=result.qNegative.hull;
    stats.uPositive=result.uPositive.hull;
    stats.returnTime=result.returnTime;
    stats.physicalHull=cellPhysical;
    stats.minimumSignedMargins=margins;
    for(int gate=0;gate<5;++gate){
      stats.worstA2[gate]=a2Index;
      stats.worstEpsilon[gate]=epsilonIndex;
    }
    stats.initialized=true;
  }else{
    stats.pPositive=intervalHull(stats.pPositive,result.pPositive.hull);
    stats.qPositive=intervalHull(stats.qPositive,result.qPositive.hull);
    stats.pNegative=intervalHull(stats.pNegative,result.pNegative.hull);
    stats.qNegative=intervalHull(stats.qNegative,result.qNegative.hull);
    stats.uPositive=intervalHull(stats.uPositive,result.uPositive.hull);
    stats.returnTime=intervalHull(stats.returnTime,result.returnTime);
    for(int coordinate=0;coordinate<4;++coordinate)
      stats.physicalHull[coordinate]=intervalHull(
        stats.physicalHull[coordinate],cellPhysical[coordinate]);
    for(int gate=0;gate<5;++gate)
      if(margins[gate]<stats.minimumSignedMargins[gate]){
        stats.minimumSignedMargins[gate]=margins[gate];
        stats.worstA2[gate]=a2Index;
        stats.worstEpsilon[gate]=epsilonIndex;
      }
  }
  ++stats.count;
  if(result.success)++stats.passCount;
  stats.success=stats.success&&result.success;
  stats.denseSteps+=result.pPositive.steps+result.qPositive.steps
    +result.pNegative.steps+result.qNegative.steps+result.uPositive.steps;
}

int runMuGridFirstHitSlab(double radiusFactor,int rIndex){
  if(rIndex<0||rIndex>=kMuGridRCells)
    throw std::invalid_argument("mu-grid first-hit r_index must lie in [0,31]");
  MuFirstHitSlabStats stats;
  for(int a2Index=0;a2Index<kMuGridA2Cells;++a2Index)
    for(int epsilonIndex=0;epsilonIndex<kMuGridEpsilonCells;++epsilonIndex){
      const MuAffineCellResult cell=buildMuGridCell(
        radiusFactor,rIndex,a2Index,epsilonIndex);
      const MuFirstHitResult result=validateMuFirstHit(cell);
      updateMuFirstHitSlabStats(stats,result,a2Index,epsilonIndex);
      if(!result.success)
        reportMuFirstHit(rIndex,a2Index,epsilonIndex,cell,result);
    }
  std::cout<<std::setprecision(17)
    <<"mode mu-grid-first-hit-slab\n"
    <<"scope selected_source_to_symmetry_event\n"
    <<"time_partition P_positive 0 1.55 Q_positive 1.55 1.90 "
       <<"P_negative 1.90 7.35 Q_negative 7.35 9.55\n"
    <<"final_flow_box U_positive relative_duration "
       <<interval(1.)/interval(5.)<<"\n"
    <<"pre_source_local_graph_exclusion imported_prerequisite_not_evaluated\n"
    <<"grid "<<kMuGridRCells<<" "<<kMuGridA2Cells<<" "
       <<kMuGridEpsilonCells<<" radius_factor "<<radiusFactor<<"\n"
    <<"r_index "<<rIndex<<" r_cell "
       <<muGridCellBox(rIndex,0,0)[0]<<"\n"
    <<"cells "<<stats.count<<" pass "<<stats.passCount
       <<" dense_steps "<<stats.denseSteps<<"\n"
    <<"P_positive_hull "<<stats.pPositive<<"\n"
    <<"Q_positive_hull "<<stats.qPositive<<"\n"
    <<"P_negative_hull "<<stats.pNegative<<"\n"
    <<"Q_negative_hull "<<stats.qNegative<<"\n"
    <<"U_final_hull "<<stats.uPositive<<"\n"
    <<"return_time_hull "<<stats.returnTime<<"\n"
    <<"half_time_hull "<<interval(kNodeTimes.back())+stats.returnTime<<"\n"
    <<"physical_state_hull "<<stats.physicalHull[0]<<" "
       <<stats.physicalHull[1]<<" "<<stats.physicalHull[2]<<" "
       <<stats.physicalHull[3]<<"\n"
    <<"signed_margin P_positive "<<stats.minimumSignedMargins[0]
       <<" worst_a2_index "<<stats.worstA2[0]
       <<" worst_epsilon_index "<<stats.worstEpsilon[0]<<"\n"
    <<"signed_margin Q_positive "<<stats.minimumSignedMargins[1]
       <<" worst_a2_index "<<stats.worstA2[1]
       <<" worst_epsilon_index "<<stats.worstEpsilon[1]<<"\n"
    <<"signed_margin P_negative "<<stats.minimumSignedMargins[2]
       <<" worst_a2_index "<<stats.worstA2[2]
       <<" worst_epsilon_index "<<stats.worstEpsilon[2]<<"\n"
    <<"signed_margin Q_negative "<<stats.minimumSignedMargins[3]
       <<" worst_a2_index "<<stats.worstA2[3]
       <<" worst_epsilon_index "<<stats.worstEpsilon[3]<<"\n"
    <<"signed_margin U_final "<<stats.minimumSignedMargins[4]
       <<" worst_a2_index "<<stats.worstA2[4]
       <<" worst_epsilon_index "<<stats.worstEpsilon[4]<<"\n"
    <<(stats.success?"PASS":"INCONCLUSIVE")
       <<" mu-grid selected-source first symmetry-hit slab\n";
  return stats.success?0:20;
}

// The C2 root-jet scout uses the actual P2bK true source rather than the
// fitted phase predictor or an invented C2 graph-error function.  The
// existing 38-dimensional Krawczyk enclosure supplies a position tube for
// that actual root.  We then differentiate the exact 37-dimensional
// residual whose unknowns are the absolute Kato phase and nine physical
// nodes.  External parameters are the normalized coordinates
//   theta=(25*r-1,4*a2,5*(epsilon-1)).
constexpr int kTrueRootDimension=1+4*kSegments;
constexpr int kThetaDimension=3;
constexpr int kRootJetDomainDimension=kTrueRootDimension+kThetaDimension;
constexpr std::array<double,kThetaDimension> kThetaScales={25.,4.,5.};

interval symmetricInterval(const interval&upper){
  const double radius=absUpper(upper);
  return interval(-radius,radius);
}

interval actualSecondDerivative(
    const IHessian&coefficients,int output,int first,int second){
  return coefficients(output,first,second)
    *interval(first==second?2.:1.);
}

interval actualSecondDerivative(
    const IMatrix&coefficients,int first,int second){
  return coefficients[first][second]*interval(first==second?2.:1.);
}

AffineInitialData normalizedThetaData(const AffineInitialData&physicalData){
  if(physicalData.centre.dimension()!=9
      ||physicalData.coordinates.numberOfRows()!=9
      ||physicalData.coordinates.numberOfColumns()!=9
      ||physicalData.radii.dimension()!=9
      ||physicalData.remainder.dimension()!=9)
    throw std::invalid_argument("normalized theta data requires dimension nine");
  AffineInitialData result=physicalData;
  for(int parameter=0;parameter<kThetaDimension;++parameter){
    const interval scale(kThetaScales[parameter]);
    result.radii[parameter]*=scale;
    for(int physical=0;physical<4;++physical)
      result.coordinates[physical][parameter]/=scale;
    // Rows 4--6 now carry normalized parameter offsets.  Their unit
    // coordinate columns stay unchanged while the field divides by scale.
  }
  return result;
}

IMap normalizedThetaAugmentedField(const MuAffineCellResult&cell){
  IMap field(
    "par:rc,a2c,epsc;var:U,P,V,Q,tr,ta,te,delta,ge;"
    "fun:P,(2*(rc+tr/25)*(a2c+ta/4)+sqrt(epsc+te/5)*(rc+tr/25)^4*"
    "(a2c+ta/4)^2)*U-V-(1+sqrt(epsc+te/5)*(rc+tr/25)^3*"
    "(a2c+ta/4))*U*U+sqrt(epsc+te/5)*(rc+tr/25)^2/3*U*U*U,"
    "Q,U,0,0,0,0,0;",2);
  field.setParameter("rc",cell.parameterCentre[0]);
  field.setParameter("a2c",cell.parameterCentre[1]);
  field.setParameter("epsc",cell.parameterCentre[2]);
  return field;
}

struct C2FlowMapData{
  IVector endpoint;
  IMatrix first;
  IHessian second;
};

C2FlowMapData advanceC2(
    IC2OdeSolver&solver,const AffineInitialData&data,const interval&duration){
  C2Rect2Set set(data.centre,data.coordinates,data.radii,data.remainder);
  IC2TimeMap timeMap(solver);
  const IVector endpoint=timeMap(duration,set);
  return {endpoint,(IMatrix)set,(IHessian)set};
}

struct C2EventMapData{
  IVector endpoint;
  IMatrix first;
  IHessian second;
  interval returnTime;
  IVector timeFirst;
  IMatrix timeSecond;
};

C2EventMapData advanceC2ToQSection(
    IC2OdeSolver&solver,const AffineInitialData&data){
  C2Rect2Set set(data.centre,data.coordinates,data.radii,data.remainder);
  ICoordinateSection section(9,3);
  IC2PoincareMap poincareMap(solver,section,poincare::MinusPlus);
  IMatrix flowFirst(9,9);IHessian flowSecond(9,9);
  interval returnTime;
  const IVector endpoint=poincareMap(
    set,flowFirst,flowSecond,returnTime);
  IMatrix eventFirst(9,9);IHessian eventSecond(9,9);
  IVector timeFirst(9);IMatrix timeSecond(9,9);
  poincareMap.computeDP(
    endpoint,flowFirst,flowSecond,eventFirst,eventSecond,
    timeFirst,timeSecond,returnTime);
  return {endpoint,eventFirst,eventSecond,returnTime,timeFirst,timeSecond};
}

IMatrix zeroMatrix(int rows,int columns){
  IMatrix result(rows,columns);
  for(int row=0;row<rows;++row)
    for(int column=0;column<columns;++column)
      result[row][column]=interval(0.);
  return result;
}

IHessian zeroHessian(int image,int domain){
  IHessian result(image,domain);
  result.clear();
  return result;
}

void addComposedC2Component(
    int targetRow,int mapOutput,const interval&multiplier,
    const IMatrix&mapFirst,const IHessian&mapSecond,
    const IMatrix&inputFirst,const IHessian&inputSecond,
    IMatrix&resultFirst,IHessian&resultSecond){
  const int ambient=mapFirst.numberOfColumns();
  const int domain=inputFirst.numberOfColumns();
  if(mapOutput<0||mapOutput>=mapFirst.numberOfRows()
      ||inputFirst.numberOfRows()!=ambient
      ||inputSecond.imageDimension()!=ambient
      ||inputSecond.dimension()!=domain)
    throw std::invalid_argument("incompatible C2 composition dimensions");
  for(int first=0;first<domain;++first){
    interval value(0.);
    for(int ambientFirst=0;ambientFirst<ambient;++ambientFirst)
      value+=mapFirst[mapOutput][ambientFirst]
        *inputFirst[ambientFirst][first];
    resultFirst[targetRow][first]+=multiplier*value;
    for(int second=first;second<domain;++second){
      interval secondValue(0.);
      for(int ambientFirst=0;ambientFirst<ambient;++ambientFirst){
        secondValue+=mapFirst[mapOutput][ambientFirst]
          *inputSecond(ambientFirst,first,second);
        for(int ambientSecond=0;ambientSecond<ambient;++ambientSecond)
          secondValue+=actualSecondDerivative(
            mapSecond,mapOutput,ambientFirst,ambientSecond)
            *inputFirst[ambientFirst][first]
            *inputFirst[ambientSecond][second];
      }
      resultSecond(targetRow,first,second)+=multiplier*secondValue;
    }
  }
}

void composeC2Time(
    const IVector&mapFirst,const IMatrix&mapSecond,
    const IMatrix&inputFirst,const IHessian&inputSecond,
    IVector&resultFirst,IHessian&resultSecond){
  const int ambient=mapFirst.dimension();
  const int domain=inputFirst.numberOfColumns();
  if(inputFirst.numberOfRows()!=ambient
      ||inputSecond.imageDimension()!=ambient
      ||inputSecond.dimension()!=domain
      ||mapSecond.numberOfRows()!=ambient
      ||mapSecond.numberOfColumns()!=ambient)
    throw std::invalid_argument("incompatible return-time C2 dimensions");
  for(int first=0;first<domain;++first){
    interval value(0.);
    for(int ambientFirst=0;ambientFirst<ambient;++ambientFirst)
      value+=mapFirst[ambientFirst]*inputFirst[ambientFirst][first];
    resultFirst[first]=value;
    for(int second=first;second<domain;++second){
      interval secondValue(0.);
      for(int ambientFirst=0;ambientFirst<ambient;++ambientFirst){
        secondValue+=mapFirst[ambientFirst]
          *inputSecond(ambientFirst,first,second);
        for(int ambientSecond=0;ambientSecond<ambient;++ambientSecond)
          secondValue+=actualSecondDerivative(
            mapSecond,ambientFirst,ambientSecond)
            *inputFirst[ambientFirst][first]
            *inputFirst[ambientSecond][second];
      }
      resultSecond(0,first,second)=secondValue;
    }
  }
}

struct MuTrueRootResidualJets{
  bool eventTransverse;
  IMatrix first;
  IHessian second;
  interval phase,halfTime,returnTime;
  IVector timeFirst;
  IHessian timeSecond;
  IVector eventEndpoint;
};

interval physicalRootPhase(const MuAffineCellResult&cell){
  interval phase=cell.phi0+cell.K[0];
  for(int parameter=0;parameter<kThetaDimension;++parameter)
    phase+=cell.phaseSlopes[parameter]
      *(cell.parameterCell[parameter]-cell.parameterCentre[parameter]);
  return phase;
}

MuTrueRootResidualJets buildMuTrueRootResidualJets(
    const MuAffineCellResult&cell){
  IMap field=normalizedThetaAugmentedField(cell);
  IC2OdeSolver solver(field,30);
  solver.setAbsoluteTolerance(1e-14);solver.setRelativeTolerance(1e-14);

  IMatrix residualFirst=zeroMatrix(
    kTrueRootDimension,kRootJetDomainDimension);
  IHessian residualSecond=zeroHessian(
    kTrueRootDimension,kRootJetDomainDimension);

  // The frozen rational P2bK gates are conservative upper bounds for the
  // physical-output labelled Hilbert--Schmidt source derivatives.  Hence
  // they bound every component and every labelled parameter entry.
  const interval sourceThetaBound=interval(3.)/interval(1250.); // S_01
  const interval sourcePhiPhiBound=interval(1.)/interval(20.);  // S_20
  const interval sourcePhiThetaBound=interval(3.)/interval(1000.); // S_11
  const interval sourceThetaThetaBound=interval(9.)/interval(5000.); // S_02
  const interval sourceTheta=symmetricInterval(sourceThetaBound);
  const interval sourcePhiPhi=symmetricInterval(sourcePhiPhiBound);
  const interval sourcePhiTheta=symmetricInterval(sourcePhiThetaBound);
  const interval sourceThetaTheta=symmetricInterval(sourceThetaThetaBound);

  IMatrix inputFirst=zeroMatrix(9,kRootJetDomainDimension);
  IHessian inputSecond=zeroHessian(9,kRootJetDomainDimension);
  const interval phase=physicalRootPhase(cell);
  const SourceData sourceDerivative=sourceData(
    parameters(cell.parameterCell[0],cell.parameterCell[1],
               cell.parameterCell[2]),phase,cell.K[1]);
  const interval graphPrime(-kGraphC1*kRadius,kGraphC1*kRadius);
  const IVector tightPhaseDerivative=
    sourceDerivative.phaseDerivative+sourceDerivative.errorDerivative*graphPrime;
  for(int physical=0;physical<4;++physical){
    inputFirst[physical][0]=tightPhaseDerivative[physical];
    inputSecond(physical,0,0)=sourcePhiPhi;
    for(int parameter=0;parameter<kThetaDimension;++parameter){
      const int thetaColumn=kTrueRootDimension+parameter;
      inputFirst[physical][thetaColumn]=sourceTheta;
      inputSecond(physical,0,thetaColumn)=sourcePhiTheta;
      for(int secondParameter=parameter;
          secondParameter<kThetaDimension;++secondParameter)
        inputSecond(physical,thetaColumn,
          kTrueRootDimension+secondParameter)=sourceThetaTheta;
    }
  }
  for(int parameter=0;parameter<kThetaDimension;++parameter)
    inputFirst[4+parameter][kTrueRootDimension+parameter]=interval(1.);

  const C2FlowMapData firstSegment=advanceC2(
    solver,normalizedThetaData(muRootSourceData(cell)),
    interval(kNodeTimes[0]));
  for(int physical=0;physical<4;++physical){
    addComposedC2Component(
      physical,physical,interval(-1.),firstSegment.first,
      firstSegment.second,inputFirst,inputSecond,
      residualFirst,residualSecond);
    residualFirst[physical][1+physical]+=interval(1.);
  }

  for(int node=1;node<kSegments;++node){
    inputFirst=zeroMatrix(9,kRootJetDomainDimension);
    inputSecond=zeroHessian(9,kRootJetDomainDimension);
    const int previousNodeColumn=1+4*(node-1);
    for(int physical=0;physical<4;++physical)
      inputFirst[physical][previousNodeColumn+physical]=interval(1.);
    for(int parameter=0;parameter<kThetaDimension;++parameter)
      inputFirst[4+parameter][kTrueRootDimension+parameter]=interval(1.);
    const C2FlowMapData segment=advanceC2(
      solver,normalizedThetaData(muRootNodeData(cell,node-1)),
      interval(kNodeTimes[node]-kNodeTimes[node-1]));
    const int row=4*node;
    const int nodeColumn=1+4*node;
    for(int physical=0;physical<4;++physical){
      addComposedC2Component(
        row+physical,physical,interval(-1.),segment.first,segment.second,
        inputFirst,inputSecond,residualFirst,residualSecond);
      residualFirst[row+physical][nodeColumn+physical]+=interval(1.);
    }
  }

  inputFirst=zeroMatrix(9,kRootJetDomainDimension);
  inputSecond=zeroHessian(9,kRootJetDomainDimension);
  const int finalNodeColumn=1+4*(kSegments-1);
  for(int physical=0;physical<4;++physical)
    inputFirst[physical][finalNodeColumn+physical]=interval(1.);
  for(int parameter=0;parameter<kThetaDimension;++parameter)
    inputFirst[4+parameter][kTrueRootDimension+parameter]=interval(1.);
  const C2EventMapData event=advanceC2ToQSection(
    solver,normalizedThetaData(muRootNodeData(cell,kSegments-1)));
  addComposedC2Component(
    kTrueRootDimension-1,1,interval(1.),event.first,event.second,
    inputFirst,inputSecond,residualFirst,residualSecond);
  IVector timeFirst(kRootJetDomainDimension);
  for(int column=0;column<kRootJetDomainDimension;++column)
    timeFirst[column]=interval(0.);
  IHessian timeSecond=zeroHessian(1,kRootJetDomainDimension);
  composeC2Time(
    event.timeFirst,event.timeSecond,inputFirst,inputSecond,
    timeFirst,timeSecond);
  // On Q=0 the event denominator is Q'=U.  Positivity of the endpoint U,
  // together with this short return-time window, binds the same transverse
  // local event used by the first-hit proof.
  const bool eventTransverse=event.endpoint[0].leftBound()>1.
    &&event.returnTime.leftBound()>0.
    &&event.returnTime.rightBound()<.2;
  return {eventTransverse,residualFirst,residualSecond,phase,
          interval(kNodeTimes.back())+event.returnTime,event.returnTime,
          timeFirst,timeSecond,event.endpoint};
}

double matrixInfinityNormUpper(const IMatrix&matrix){
  double maximum=0.;
  for(int row=0;row<matrix.numberOfRows();++row){
    interval sum(0.);
    for(int column=0;column<matrix.numberOfColumns();++column)
      sum+=interval(0.,absUpper(matrix[row][column]));
    maximum=std::max(maximum,sum.rightBound());
  }
  return maximum;
}

struct WeightedRemainderGate{
  double contraction,unweightedContraction;
  std::vector<double> weights;
};

double weightedMatrixInfinityNormUpper(
    const IMatrix&matrix,const std::vector<double>&weights){
  if(static_cast<int>(weights.size())!=matrix.numberOfRows()
      ||matrix.numberOfRows()!=matrix.numberOfColumns())
    throw std::invalid_argument("weighted matrix norm dimension mismatch");
  double maximum=0.;
  for(int row=0;row<matrix.numberOfRows();++row){
    if(!(weights[row]>0.)||!std::isfinite(weights[row]))
      throw std::invalid_argument("weighted matrix norm needs positive weights");
    interval sum(0.);
    for(int column=0;column<matrix.numberOfColumns();++column)
      sum+=interval(0.,absUpper(matrix[row][column]))
        *interval(weights[column]);
    maximum=std::max(maximum,
      (sum/interval(weights[row])).rightBound());
  }
  return maximum;
}

WeightedRemainderGate buildWeightedRemainderGate(
    const IMatrix&remainder){
  const int dimension=remainder.numberOfRows();
  if(dimension!=remainder.numberOfColumns())
    throw std::invalid_argument("remainder matrix must be square");
  std::vector<double> weights(dimension,1.),bestWeights=weights;
  double best=weightedMatrixInfinityNormUpper(remainder,weights);
  // A positive power iterate is only a numerical choice of diagonal scale.
  // The returned Collatz row bound is recomputed with interval arithmetic,
  // so no spectral information from this iteration is trusted as proof.
  for(int iteration=0;iteration<512;++iteration){
    std::vector<double> next(dimension,0.);
    double maximum=0.;
    for(int row=0;row<dimension;++row){
      long double sum=0.;
      for(int column=0;column<dimension;++column)
        sum+=static_cast<long double>(absUpper(remainder[row][column]))
          *static_cast<long double>(weights[column]);
      next[row]=static_cast<double>(sum);
      maximum=std::max(maximum,next[row]);
    }
    if(!(maximum>0.)||!std::isfinite(maximum))break;
    for(double&value:next)
      value=std::max(1e-12,value/maximum);
    const double candidate=weightedMatrixInfinityNormUpper(remainder,next);
    if(candidate<best){best=candidate;bestWeights=next;}
    weights=std::move(next);
  }
  return {best,matrixInfinityNormUpper(remainder),bestWeights};
}

struct NeumannSolveResult{
  bool success;
  IVector enclosure;
  double maxInclusionRatio;
};

NeumannSolveResult solveWithNeumannGate(
    const IMatrix&preconditioner,const IMatrix&remainder,
    const WeightedRemainderGate&gate,const IVector&rightHandSide){
  const int dimension=rightHandSide.dimension();
  if(static_cast<int>(gate.weights.size())!=dimension)
    throw std::invalid_argument("Neumann weights have wrong dimension");
  const IVector affine=preconditioner*rightHandSide;
  const IVector centre=pointMid(affine);
  const IVector defect=affine-centre+remainder*centre;
  if(!(gate.contraction<1.))
    return {false,affine,std::numeric_limits<double>::infinity()};
  // The proof of uniqueness uses the weighted contraction above.  For a
  // useful enclosure, solve the associated nonnegative radius inequality
  // componentwise instead of imposing one Perron-scaled radius on variables
  // with very different physical units.  This iteration is only a box
  // predictor; the interval inclusion below is the acceptance test.
  std::vector<double> defectRadius(dimension),radius(dimension);
  for(int row=0;row<dimension;++row)
    radius[row]=defectRadius[row]=absUpper(defect[row]);
  for(int iteration=0;iteration<1024;++iteration){
    std::vector<double> next(dimension);
    double relativeChange=0.;
    for(int row=0;row<dimension;++row){
      long double sum=defectRadius[row];
      for(int column=0;column<dimension;++column)
        sum+=static_cast<long double>(absUpper(remainder[row][column]))
          *static_cast<long double>(radius[column]);
      next[row]=static_cast<double>(sum);
      relativeChange=std::max(relativeChange,
        std::abs(next[row]-radius[row])/(1e-300+std::abs(next[row])));
    }
    radius=std::move(next);
    if(relativeChange<1e-13)break;
  }
  for(double&value:radius)
    value=std::nextafter(std::max(1e-15,1.01*value),
      std::numeric_limits<double>::infinity());
  IVector enclosure(dimension),image(dimension);
  double maxRatio=std::numeric_limits<double>::infinity();
  bool success=false;
  for(int attempt=0;attempt<64&&!success;++attempt){
    for(int i=0;i<dimension;++i){
      enclosure[i]=centre[i]+interval(-radius[i],radius[i]);
    }
    image=affine+remainder*enclosure;
    success=true;maxRatio=0.;
    for(int i=0;i<dimension;++i){
      const bool componentSuccess=interior(image[i],enclosure[i]);
      success=success&&componentSuccess;
      const double componentRadius=absUpper(enclosure[i]-centre[i]);
      maxRatio=std::max(maxRatio,
        absUpper(image[i]-centre[i])/componentRadius);
      if(!componentSuccess)
        radius[i]=std::nextafter(std::max(
          1.01*radius[i],1.01*absUpper(image[i]-centre[i])),
          std::numeric_limits<double>::infinity());
    }
  }
  return {success,enclosure,maxRatio};
}

IVector hessianBilinear(
    const IHessian&hessian,const IVector&first,const IVector&second){
  const int image=hessian.imageDimension();
  const int domain=hessian.dimension();
  if(first.dimension()!=domain||second.dimension()!=domain)
    throw std::invalid_argument("Hessian bilinear direction mismatch");
  IVector result(image);
  for(int output=0;output<image;++output){
    result[output]=interval(0.);
    for(int i=0;i<domain;++i)
      for(int j=0;j<domain;++j)
        result[output]+=hessian(output,i,j)*first[i]*second[j];
  }
  return result;
}

interval dotProduct(const IVector&left,const IVector&right){
  if(left.dimension()!=right.dimension())
    throw std::invalid_argument("dot-product dimension mismatch");
  interval result(0.);
  for(int i=0;i<left.dimension();++i)result+=left[i]*right[i];
  return result;
}

struct MuTrueRootJetResult{
  bool success;
  double inverseContraction,unweightedInverseContraction,maxSolveInclusion;
  interval phase,halfTime,returnTime;
  std::array<IVector,kThetaDimension> first;
  std::array<IVector,6> second;
  std::array<interval,kThetaDimension> phaseFirst,timeFirst;
  std::array<interval,6> phaseSecond,timeSecond;
  IVector eventEndpoint;
};

int symmetricPairIndex(int first,int second){
  if(first>second)std::swap(first,second);
  int index=0;
  for(int i=0;i<kThetaDimension;++i)
    for(int j=i;j<kThetaDimension;++j,++index)
      if(i==first&&j==second)return index;
  throw std::out_of_range("symmetric pair index");
}

MuTrueRootJetResult validateMuTrueRootJets(const MuAffineCellResult&cell){
  const MuTrueRootResidualJets residual=buildMuTrueRootResidualJets(cell);
  IMatrix A(kTrueRootDimension,kTrueRootDimension);
  for(int row=0;row<kTrueRootDimension;++row)
    for(int column=0;column<kTrueRootDimension;++column)
      A[row][column]=residual.first[row][column];
  const IMatrix preconditioner=midpointInverse(A);
  const IMatrix remainder=IMatrix::Identity(kTrueRootDimension)
    -preconditioner*A;
  const WeightedRemainderGate gate=buildWeightedRemainderGate(remainder);
  bool success=cell.success&&residual.eventTransverse&&gate.contraction<1.;
  double maxSolveInclusion=0.;
  std::array<IVector,kThetaDimension> first={
    IVector(kTrueRootDimension),IVector(kTrueRootDimension),
    IVector(kTrueRootDimension)};
  for(int parameter=0;parameter<kThetaDimension;++parameter){
    IVector rightHandSide(kTrueRootDimension);
    for(int row=0;row<kTrueRootDimension;++row)
      rightHandSide[row]=-residual.first[row][kTrueRootDimension+parameter];
    const NeumannSolveResult solve=solveWithNeumannGate(
      preconditioner,remainder,gate,rightHandSide);
    first[parameter]=solve.enclosure;
    success=success&&solve.success;
    maxSolveInclusion=std::max(maxSolveInclusion,solve.maxInclusionRatio);
  }

  std::array<IVector,kThetaDimension> totalFirst={
    IVector(kRootJetDomainDimension),IVector(kRootJetDomainDimension),
    IVector(kRootJetDomainDimension)};
  for(int parameter=0;parameter<kThetaDimension;++parameter){
    for(int i=0;i<kTrueRootDimension;++i)
      totalFirst[parameter][i]=first[parameter][i];
    for(int external=0;external<kThetaDimension;++external)
      totalFirst[parameter][kTrueRootDimension+external]
        =interval(parameter==external?1.:0.);
  }

  std::array<IVector,6> second={
    IVector(kTrueRootDimension),IVector(kTrueRootDimension),
    IVector(kTrueRootDimension),IVector(kTrueRootDimension),
    IVector(kTrueRootDimension),IVector(kTrueRootDimension)};
  std::array<interval,6> phaseSecond,timeSecond;
  std::array<interval,kThetaDimension> phaseFirst,timeFirst;
  for(int parameter=0;parameter<kThetaDimension;++parameter){
    phaseFirst[parameter]=first[parameter][0];
    timeFirst[parameter]=dotProduct(
      residual.timeFirst,totalFirst[parameter]);
  }
  for(int firstParameter=0;firstParameter<kThetaDimension;++firstParameter)
    for(int secondParameter=firstParameter;
        secondParameter<kThetaDimension;++secondParameter){
      const int pair=symmetricPairIndex(firstParameter,secondParameter);
      const IVector curvature=hessianBilinear(
        residual.second,totalFirst[firstParameter],totalFirst[secondParameter]);
      const NeumannSolveResult solve=solveWithNeumannGate(
        preconditioner,remainder,gate,-curvature);
      second[pair]=solve.enclosure;
      success=success&&solve.success;
      maxSolveInclusion=std::max(maxSolveInclusion,solve.maxInclusionRatio);
      phaseSecond[pair]=second[pair][0];
      IVector totalSecond(kRootJetDomainDimension);
      for(int i=0;i<kTrueRootDimension;++i)
        totalSecond[i]=second[pair][i];
      for(int parameter=0;parameter<kThetaDimension;++parameter)
        totalSecond[kTrueRootDimension+parameter]=interval(0.);
      timeSecond[pair]=hessianBilinear(
        residual.timeSecond,totalFirst[firstParameter],
        totalFirst[secondParameter])[0]
        +dotProduct(residual.timeFirst,totalSecond);
    }
  return {success,gate.contraction,gate.unweightedContraction,
          maxSolveInclusion,residual.phase,
          residual.halfTime,residual.returnTime,first,second,
          phaseFirst,timeFirst,phaseSecond,timeSecond,residual.eventEndpoint};
}

void reportMuTrueRootJets(
    int rIndex,int a2Index,int epsilonIndex,
    const MuAffineCellResult&cell,const MuTrueRootJetResult&result){
  static const std::array<const char*,kThetaDimension> thetaNames={
    "theta_r","theta_a","theta_epsilon"};
  std::cout<<std::setprecision(17)
    <<"mode mu-grid-root-jets\n"
    <<"scope selected_true_source_root_C2\n"
    <<"indices "<<rIndex<<" "<<a2Index<<" "<<epsilonIndex<<"\n"
    <<"parameter_cell "<<cell.parameterCell[0]<<" "
       <<cell.parameterCell[1]<<" "<<cell.parameterCell[2]<<"\n"
    <<"root_dimension "<<kTrueRootDimension
       <<" combined_dimension "<<kRootJetDomainDimension<<"\n"
    <<"phase_hull "<<result.phase<<" half_time_hull "<<result.halfTime
       <<" return_time_hull "<<result.returnTime<<"\n"
    <<"event_endpoint "<<result.eventEndpoint<<"\n"
    <<"weighted_inverse_contraction "<<result.inverseContraction
       <<" unweighted_inverse_contraction "
       <<result.unweightedInverseContraction
       <<" max_solve_inclusion "<<result.maxSolveInclusion<<"\n";
  for(int parameter=0;parameter<kThetaDimension;++parameter)
    std::cout<<"normalized_first "<<thetaNames[parameter]
      <<" phase "<<result.phaseFirst[parameter]
      <<" half_time "<<result.timeFirst[parameter]
      <<" original_phase "
      <<result.phaseFirst[parameter]*interval(kThetaScales[parameter])
      <<" original_half_time "
      <<result.timeFirst[parameter]*interval(kThetaScales[parameter])<<"\n";
  int pair=0;
  for(int first=0;first<kThetaDimension;++first)
    for(int second=first;second<kThetaDimension;++second,++pair)
      std::cout<<"normalized_second "<<thetaNames[first]<<" "
        <<thetaNames[second]<<" phase "<<result.phaseSecond[pair]
        <<" half_time "<<result.timeSecond[pair]
        <<" original_phase "<<result.phaseSecond[pair]
          *interval(kThetaScales[first]*kThetaScales[second])
        <<" original_half_time "<<result.timeSecond[pair]
          *interval(kThetaScales[first]*kThetaScales[second])<<"\n";
  std::cout<<(result.success?"PASS":"INCONCLUSIVE")
    <<" mu-grid true-source root C2 jets\n";
}

int runMuGridRootJets(
    double radiusFactor,int rIndex,int a2Index,int epsilonIndex){
  const MuAffineCellResult cell=buildMuGridCell(
    radiusFactor,rIndex,a2Index,epsilonIndex);
  const MuTrueRootJetResult result=validateMuTrueRootJets(cell);
  reportMuTrueRootJets(rIndex,a2Index,epsilonIndex,cell,result);
  return result.success?0:20;
}

struct MuRootJetSlabStats{
  bool success=true,initialized=false;
  int count=0,passCount=0;
  double maxWeightedContraction=0.,maxUnweightedContraction=0.;
  double maxSolveInclusion=0.;
  int worstWeightedA2=-1,worstWeightedEpsilon=-1;
  int worstSolveA2=-1,worstSolveEpsilon=-1;
  interval phaseHull,halfTimeHull,returnTimeHull;
  double minimumEventU=std::numeric_limits<double>::infinity();
  double maximumEventQ=0.;
  std::array<double,kThetaDimension> rootFirstAbs={0.,0.,0.};
  std::array<double,6> rootSecondAbs={0.,0.,0.,0.,0.,0.};
  std::array<double,kThetaDimension> phaseFirstAbs={0.,0.,0.};
  std::array<double,kThetaDimension> timeFirstAbs={0.,0.,0.};
  std::array<double,6> phaseSecondAbs={0.,0.,0.,0.,0.,0.};
  std::array<double,6> timeSecondAbs={0.,0.,0.,0.,0.,0.};
};

void updateMuRootJetSlabStats(
    MuRootJetSlabStats&stats,const MuTrueRootJetResult&result,
    int a2Index,int epsilonIndex){
  ++stats.count;
  if(result.success)++stats.passCount;
  stats.success=stats.success&&result.success;
  if(result.inverseContraction>stats.maxWeightedContraction){
    stats.maxWeightedContraction=result.inverseContraction;
    stats.worstWeightedA2=a2Index;
    stats.worstWeightedEpsilon=epsilonIndex;
  }
  stats.maxUnweightedContraction=std::max(
    stats.maxUnweightedContraction,result.unweightedInverseContraction);
  if(result.maxSolveInclusion>stats.maxSolveInclusion){
    stats.maxSolveInclusion=result.maxSolveInclusion;
    stats.worstSolveA2=a2Index;
    stats.worstSolveEpsilon=epsilonIndex;
  }
  if(!stats.initialized){
    stats.phaseHull=result.phase;
    stats.halfTimeHull=result.halfTime;
    stats.returnTimeHull=result.returnTime;
    stats.initialized=true;
  }else{
    stats.phaseHull=intervalHull(stats.phaseHull,result.phase);
    stats.halfTimeHull=intervalHull(stats.halfTimeHull,result.halfTime);
    stats.returnTimeHull=intervalHull(stats.returnTimeHull,result.returnTime);
  }
  stats.minimumEventU=std::min(
    stats.minimumEventU,result.eventEndpoint[0].leftBound());
  stats.maximumEventQ=std::max(
    stats.maximumEventQ,absUpper(result.eventEndpoint[3]));
  for(int parameter=0;parameter<kThetaDimension;++parameter){
    for(int coordinate=0;coordinate<kTrueRootDimension;++coordinate)
      stats.rootFirstAbs[parameter]=std::max(
        stats.rootFirstAbs[parameter],absUpper(result.first[parameter][coordinate]));
    stats.phaseFirstAbs[parameter]=std::max(
      stats.phaseFirstAbs[parameter],absUpper(result.phaseFirst[parameter]));
    stats.timeFirstAbs[parameter]=std::max(
      stats.timeFirstAbs[parameter],absUpper(result.timeFirst[parameter]));
  }
  for(int pair=0;pair<6;++pair){
    for(int coordinate=0;coordinate<kTrueRootDimension;++coordinate)
      stats.rootSecondAbs[pair]=std::max(
        stats.rootSecondAbs[pair],absUpper(result.second[pair][coordinate]));
    stats.phaseSecondAbs[pair]=std::max(
      stats.phaseSecondAbs[pair],absUpper(result.phaseSecond[pair]));
    stats.timeSecondAbs[pair]=std::max(
      stats.timeSecondAbs[pair],absUpper(result.timeSecond[pair]));
  }
}

double outwardScaledUpper(double bound,double scale){
  return (interval(bound)*interval(scale)).rightBound();
}

int runMuGridRootJetSlab(double radiusFactor,int rIndex){
  if(rIndex<0||rIndex>=kMuGridRCells)
    throw std::out_of_range("mu-grid root-jet r index");
  MuRootJetSlabStats stats;
  for(int a2Index=0;a2Index<kMuGridA2Cells;++a2Index)
    for(int epsilonIndex=0;epsilonIndex<kMuGridEpsilonCells;
        ++epsilonIndex){
      const MuAffineCellResult cell=buildMuGridCell(
        radiusFactor,rIndex,a2Index,epsilonIndex);
      updateMuRootJetSlabStats(
        stats,validateMuTrueRootJets(cell),a2Index,epsilonIndex);
    }
  static const std::array<const char*,kThetaDimension> thetaNames={
    "theta_r","theta_a","theta_epsilon"};
  std::cout<<std::setprecision(17)
    <<"mode mu-grid-root-jets-slab\n"
    <<"scope selected_true_source_root_C2\n"
    <<"grid "<<kMuGridRCells<<" "<<kMuGridA2Cells<<" "
       <<kMuGridEpsilonCells<<" radius_factor "<<radiusFactor<<"\n"
    <<"r_index "<<rIndex<<" r_cell "<<muGridCellBox(rIndex,0,0)[0]<<"\n"
    <<"cells "<<stats.passCount<<"/"<<stats.count<<"\n"
    <<"phase_hull "<<stats.phaseHull
       <<" half_time_hull "<<stats.halfTimeHull
       <<" return_time_hull "<<stats.returnTimeHull<<"\n"
    <<"event_minimum_U "<<stats.minimumEventU
       <<" event_maximum_abs_Q "<<stats.maximumEventQ<<"\n"
    <<"maximum_weighted_inverse_contraction "
       <<stats.maxWeightedContraction
       <<" worst_a2_index "<<stats.worstWeightedA2
       <<" worst_epsilon_index "<<stats.worstWeightedEpsilon<<"\n"
    <<"maximum_unweighted_inverse_contraction "
       <<stats.maxUnweightedContraction<<"\n"
    <<"maximum_solve_inclusion "<<stats.maxSolveInclusion
       <<" worst_a2_index "<<stats.worstSolveA2
       <<" worst_epsilon_index "<<stats.worstSolveEpsilon<<"\n";
  for(int parameter=0;parameter<kThetaDimension;++parameter)
    std::cout<<"normalized_first_abs "<<thetaNames[parameter]
      <<" root "<<stats.rootFirstAbs[parameter]
      <<" phase "<<stats.phaseFirstAbs[parameter]
      <<" half_time "<<stats.timeFirstAbs[parameter]
      <<" original_root "
      <<outwardScaledUpper(
        stats.rootFirstAbs[parameter],kThetaScales[parameter])
      <<" original_phase "
      <<outwardScaledUpper(
        stats.phaseFirstAbs[parameter],kThetaScales[parameter])
      <<" original_half_time "
      <<outwardScaledUpper(
        stats.timeFirstAbs[parameter],kThetaScales[parameter])<<"\n";
  int pair=0;
  for(int first=0;first<kThetaDimension;++first)
    for(int second=first;second<kThetaDimension;++second,++pair){
      const double scale=kThetaScales[first]*kThetaScales[second];
      std::cout<<"normalized_second_abs "<<thetaNames[first]<<" "
        <<thetaNames[second]<<" root "<<stats.rootSecondAbs[pair]
        <<" phase "<<stats.phaseSecondAbs[pair]
        <<" half_time "<<stats.timeSecondAbs[pair]
        <<" original_root "
        <<outwardScaledUpper(stats.rootSecondAbs[pair],scale)
        <<" original_phase "
        <<outwardScaledUpper(stats.phaseSecondAbs[pair],scale)
        <<" original_half_time "
        <<outwardScaledUpper(stats.timeSecondAbs[pair],scale)<<"\n";
    }
  std::cout<<(stats.success?"PASS":"INCONCLUSIVE")
    <<" mu-grid true-source root C2 jet slab\n";
  return stats.success?0:20;
}

struct MuGridCellStats{
  bool success=true;
  int count=0,passCount=0;
  double maxInclusion=0.,maxContraction=0.;
  double determinantLower=0.,determinantUpper=0.;
  int worstInclusionA2=-1,worstInclusionEpsilon=-1;
  int worstContractionA2=-1,worstContractionEpsilon=-1;
};

void updateMuGridCellStats(MuGridCellStats&stats,
    const MuAffineCellResult&cell,int a2Index,int epsilonIndex){
  if(stats.count==0){
    stats.determinantLower=cell.determinant.leftBound();
    stats.determinantUpper=cell.determinant.rightBound();
  }else{
    stats.determinantLower=std::min(
      stats.determinantLower,cell.determinant.leftBound());
    stats.determinantUpper=std::max(
      stats.determinantUpper,cell.determinant.rightBound());
  }
  ++stats.count;
  if(cell.success)++stats.passCount;
  stats.success=stats.success&&cell.success;
  if(cell.maxInclusion>stats.maxInclusion){
    stats.maxInclusion=cell.maxInclusion;
    stats.worstInclusionA2=a2Index;
    stats.worstInclusionEpsilon=epsilonIndex;
  }
  if(cell.maxContraction>stats.maxContraction){
    stats.maxContraction=cell.maxContraction;
    stats.worstContractionA2=a2Index;
    stats.worstContractionEpsilon=epsilonIndex;
  }
}

struct MuGridFaceStats{
  bool success=true;
  int count=0,passCount=0;
  double maxRatio=0.;
  int worstCoordinate=-1;
  int worstA2=-1,worstEpsilon=-1;
};

void updateMuGridFaceStats(MuGridFaceStats&stats,
    const FaceContainmentResult&face,int a2Index,int epsilonIndex){
  ++stats.count;
  if(face.success)++stats.passCount;
  stats.success=stats.success&&face.success;
  if(face.maxRatio>stats.maxRatio){
    stats.maxRatio=face.maxRatio;
    stats.worstCoordinate=face.worstIndex;
    stats.worstA2=a2Index;
    stats.worstEpsilon=epsilonIndex;
  }
}

int muGridSlabOffset(int a2Index,int epsilonIndex){
  return a2Index*kMuGridEpsilonCells+epsilonIndex;
}

std::vector<MuAffineCellResult> buildMuGridSlab(
    double radiusFactor,int rIndex,MuGridCellStats*stats=nullptr){
  std::vector<MuAffineCellResult> slab;
  slab.reserve(kMuGridA2Cells*kMuGridEpsilonCells);
  for(int a2Index=0;a2Index<kMuGridA2Cells;++a2Index)
    for(int epsilonIndex=0;epsilonIndex<kMuGridEpsilonCells;++epsilonIndex){
      slab.push_back(buildMuGridCell(
        radiusFactor,rIndex,a2Index,epsilonIndex));
      if(stats)updateMuGridCellStats(
        *stats,slab.back(),a2Index,epsilonIndex);
    }
  return slab;
}

int runMuGridFace(double radiusFactor,const std::string&axis,
                  int rIndex,int a2Index,int epsilonIndex){
  if(rIndex<0||rIndex>=kMuGridRCells
      ||a2Index<0||a2Index>=kMuGridA2Cells
      ||epsilonIndex<0||epsilonIndex>=kMuGridEpsilonCells)
    throw std::invalid_argument("mu-grid face lower-cell index is out of range");
  int upperR=rIndex,upperA2=a2Index,upperEpsilon=epsilonIndex;
  const MuBox lowerBox=muGridCellBox(rIndex,a2Index,epsilonIndex);
  MuBox face;
  if(axis=="r"){
    if(rIndex+1>=kMuGridRCells)
      throw std::invalid_argument("mu-grid r face has no upper cell");
    ++upperR;
    face={muGridRFace(rIndex+1),lowerBox[1],lowerBox[2]};
  }else if(axis=="a2"){
    if(a2Index+1>=kMuGridA2Cells)
      throw std::invalid_argument("mu-grid a2 face has no upper cell");
    ++upperA2;
    face={lowerBox[0],muGridA2Face(a2Index+1),lowerBox[2]};
  }else if(axis=="epsilon"){
    if(epsilonIndex+1>=kMuGridEpsilonCells)
      throw std::invalid_argument("mu-grid epsilon face has no upper cell");
    ++upperEpsilon;
    face={lowerBox[0],lowerBox[1],
          muGridEpsilonFace(epsilonIndex+1)};
  }else{
    throw std::invalid_argument("mu-grid face axis must be r, a2, or epsilon");
  }
  const MuAffineCellResult lower=buildMuGridCell(
    radiusFactor,rIndex,a2Index,epsilonIndex);
  const MuAffineCellResult upper=buildMuGridCell(
    radiusFactor,upperR,upperA2,upperEpsilon);
  const FaceContainmentResult lowerIntoUpper=mapMuFaceEnclosure(
    lower,upper,face);
  const FaceContainmentResult upperIntoLower=mapMuFaceEnclosure(
    upper,lower,face);
  const bool success=lower.success&&upper.success&&lowerIntoUpper.success;
  std::cout<<std::setprecision(17)
    <<"mode mu-grid-face\n"
    <<"axis "<<axis<<" lower_indices "<<rIndex<<" "<<a2Index<<" "
       <<epsilonIndex<<" upper_indices "<<upperR<<" "<<upperA2<<" "
       <<upperEpsilon<<"\n"
    <<"face "<<face[0]<<" "<<face[1]<<" "<<face[2]<<"\n"
    <<"lower max_inclusion "<<lower.maxInclusion
    <<" max_contraction "<<lower.maxContraction<<" "
       <<(lower.success?"PASS":"INCONCLUSIVE")<<"\n"
    <<"upper max_inclusion "<<upper.maxInclusion
    <<" max_contraction "<<upper.maxContraction<<" "
       <<(upper.success?"PASS":"INCONCLUSIVE")<<"\n"
    <<"direct_face_map direction lower->upper max_ratio "
       <<lowerIntoUpper.maxRatio
    <<" worst "<<lowerIntoUpper.worstIndex<<" "
       <<shootingCoordinateName(lowerIntoUpper.worstIndex)<<" "
       <<(lowerIntoUpper.success?"PASS":"INCONCLUSIVE")<<"\n"
    <<"direct_face_map direction upper->lower max_ratio "
       <<upperIntoLower.maxRatio
    <<" worst "<<upperIntoLower.worstIndex<<" "
       <<shootingCoordinateName(upperIntoLower.worstIndex)<<" "
       <<(upperIntoLower.success?"PASS":"INCONCLUSIVE")
       <<" diagnostic_not_required\n"
    <<(success?"PASS":"INCONCLUSIVE")
    <<" mu-grid face root identification\n";
  return success?0:20;
}

void reportMuGridFaceStats(const char*axis,const MuGridFaceStats&stats){
  std::cout<<axis<<"_faces "<<stats.count
    <<" pass "<<stats.passCount
    <<" max_ratio "<<stats.maxRatio
    <<" worst_a2_index "<<stats.worstA2
    <<" worst_epsilon_index "<<stats.worstEpsilon
    <<" worst_coordinate "<<stats.worstCoordinate<<" "
    <<shootingCoordinateName(stats.worstCoordinate)<<" "
    <<(stats.success?"PASS":"INCONCLUSIVE")<<"\n";
}

int runMuGridSlab(double radiusFactor,int rIndex){
  if(rIndex<0||rIndex>=kMuGridRCells)
    throw std::invalid_argument("mu-grid r_index must lie in [0,31]");
  MuGridCellStats cellStats;
  const std::vector<MuAffineCellResult> slab=buildMuGridSlab(
    radiusFactor,rIndex,&cellStats);
  MuGridFaceStats a2Faces,epsilonFaces,rFaces;
  const MuBox firstCell=muGridCellBox(rIndex,0,0);
  const interval rCell=firstCell[0];
  for(int a2Index=0;a2Index+1<kMuGridA2Cells;++a2Index)
    for(int epsilonIndex=0;epsilonIndex<kMuGridEpsilonCells;++epsilonIndex){
      const MuBox cell=muGridCellBox(rIndex,a2Index,epsilonIndex);
      const MuBox face={rCell,muGridA2Face(a2Index+1),cell[2]};
      updateMuGridFaceStats(a2Faces,mapMuFaceEnclosure(
        slab[muGridSlabOffset(a2Index,epsilonIndex)],
        slab[muGridSlabOffset(a2Index+1,epsilonIndex)],face),
        a2Index,epsilonIndex);
    }
  for(int a2Index=0;a2Index<kMuGridA2Cells;++a2Index)
    for(int epsilonIndex=0;
        epsilonIndex+1<kMuGridEpsilonCells;++epsilonIndex){
      const MuBox cell=muGridCellBox(rIndex,a2Index,epsilonIndex);
      const MuBox face={rCell,cell[1],
                        muGridEpsilonFace(epsilonIndex+1)};
      updateMuGridFaceStats(epsilonFaces,mapMuFaceEnclosure(
        slab[muGridSlabOffset(a2Index,epsilonIndex)],
        slab[muGridSlabOffset(a2Index,epsilonIndex+1)],face),
        a2Index,epsilonIndex);
    }
  if(rIndex+1<kMuGridRCells){
    const std::vector<MuAffineCellResult> next=buildMuGridSlab(
      radiusFactor,rIndex+1);
    for(int a2Index=0;a2Index<kMuGridA2Cells;++a2Index)
      for(int epsilonIndex=0;epsilonIndex<kMuGridEpsilonCells;
          ++epsilonIndex){
        const MuBox cell=muGridCellBox(rIndex,a2Index,epsilonIndex);
        const MuBox face={muGridRFace(rIndex+1),cell[1],cell[2]};
        updateMuGridFaceStats(rFaces,mapMuFaceEnclosure(
          slab[muGridSlabOffset(a2Index,epsilonIndex)],
          next[muGridSlabOffset(a2Index,epsilonIndex)],face),
          a2Index,epsilonIndex);
      }
  }
  const bool success=cellStats.success&&a2Faces.success
    &&epsilonFaces.success&&rFaces.success;
  std::cout<<std::setprecision(17)
    <<"mode mu-grid-slab\n"
    <<"grid "<<kMuGridRCells<<" "<<kMuGridA2Cells<<" "
       <<kMuGridEpsilonCells<<" radius_factor "<<radiusFactor<<"\n"
    <<"r_index "<<rIndex<<" r_cell "<<rCell<<"\n"
    <<"cells "<<cellStats.count<<" pass "<<cellStats.passCount
    <<" max_inclusion "<<cellStats.maxInclusion
    <<" worst_inclusion_a2_index "<<cellStats.worstInclusionA2
    <<" worst_inclusion_epsilon_index "
       <<cellStats.worstInclusionEpsilon
    <<" max_contraction "<<cellStats.maxContraction
    <<" worst_contraction_a2_index "<<cellStats.worstContractionA2
    <<" worst_contraction_epsilon_index "
       <<cellStats.worstContractionEpsilon
    <<" determinant_hull "
       <<interval(cellStats.determinantLower,cellStats.determinantUpper)<<" "
    <<(cellStats.success?"PASS":"INCONCLUSIVE")<<"\n";
  reportMuGridFaceStats("a2",a2Faces);
  reportMuGridFaceStats("epsilon",epsilonFaces);
  reportMuGridFaceStats("r",rFaces);
  std::cout<<(success?"PASS":"INCONCLUSIVE")
    <<" mu-grid slab root identification\n";
  return success?0:20;
}

FaceContainmentResult importFrozenCoreRoot(
    const MuAffineCellResult&core){
  const interval zero(0.);
  const MuBox zeroBox={zero,zero,zero};
  IVector zeroPhysical(4);
  for(int coordinate=0;coordinate<4;++coordinate)
    zeroPhysical[coordinate]=interval(0.);
  const MuSlopes zeroParameterSlopes={
    zeroPhysical,zeroPhysical,zeroPhysical};
  const interval certifiedPhase(
    "5.8615055856447817","5.8615055856450482");
  const interval delta=certifiedPhase-core.phi0;
  const interval graphError("-1e-20","1e-20");
  const AffineInitialData source=muAffineSourceData(
    core.parameterCentre,zeroBox,core.phi0,core.phaseSlopes,
    core.chart.source.state,zeroParameterSlopes,
    core.chart.source.phaseDerivative,core.chart.source.errorDerivative,
    delta,graphError);

  IMap augmentedField(
    "par:rc,a2c,epsc;var:U,P,V,Q,er,ea,ee,delta,ge;"
    "fun:P,(2*(rc+er)*(a2c+ea)+sqrt(epsc+ee)*(rc+er)^4*(a2c+ea)^2)*U-V-"
    "(1+sqrt(epsc+ee)*(rc+er)^3*(a2c+ea))*U*U+"
    "sqrt(epsc+ee)*(rc+er)^2/3*U*U*U,Q,U,0,0,0,0,0;");
  augmentedField.setParameter("rc",core.parameterCentre[0]);
  augmentedField.setParameter("a2c",core.parameterCentre[1]);
  augmentedField.setParameter("epsc",core.parameterCentre[2]);
  IOdeSolver solver(augmentedField,30);
  solver.setAbsoluteTolerance(1e-14);solver.setRelativeTolerance(1e-14);
  IVector frozen(2+4*kSegments);
  frozen[0]=delta;frozen[1]=graphError;
  C1HORect2Set set(source.centre,source.coordinates,
                   source.radii,source.remainder);
  for(int node=0;node<kSegments;++node){
    // TimeMap reads set.getCurrentTime() and takes an absolute target time.
    // A segment length here would make every call after the first a no-op.
    ITimeMap map(solver);
    map(interval(kNodeTimes[node]),set);
    const IMatrix frame=muResidualFrame(
      core.parameterSlopes[node],core.chart.phaseTangents[node],
      core.chart.errorTangents[node]);
    const IVector xi=set.affineTransformation(
      frame,muAugmentedCentre(core.chart.nodes[node]));
    for(int coordinate=0;coordinate<4;++coordinate)
      frozen[2+4*node+coordinate]=xi[coordinate];
  }
  bool success=core.success;
  double maxRatio=0.;
  int worstIndex=-1;
  for(int i=0;i<frozen.dimension();++i){
    const double ratio=absUpper(frozen[i])/absUpper(core.X[i]);
    if(ratio>maxRatio){maxRatio=ratio;worstIndex=i;}
    success=success&&interior(frozen[i],core.X[i]);
  }
  return {success,frozen,maxRatio,worstIndex};
}

int runMuGridAnchor(double radiusFactor){
  // The exact point (0,0,1) is the lower-r/upper-a2/upper-epsilon corner of
  // this grid cell.  One successful core-to-cell map anchors the connected
  // common-face cover; no separate anchor is needed for every degenerate
  // (a2,epsilon) representation on r=0.
  constexpr int anchorR=0,anchorA2=63,anchorEpsilon=1;
  const MuAffineCellResult cell=buildMuGridCell(
    radiusFactor,anchorR,anchorA2,anchorEpsilon);
  const interval zero(0.),one(1.);
  const MuBox coreCell={zero,zero,one};
  const MuBox zeroSlopes={zero,zero,zero};
  const interval corePhase=rFacePredictor(zero).first;
  constexpr double coreRadiusFactor=1.5;
  const MuAffineCellResult core=buildMuAffineCell(
    coreRadiusFactor,coreCell,corePhase,zeroSlopes,false,true);
  const MuBox anchorPoint={zero,zero,one};
  const FaceContainmentResult intoCell=mapMuFaceEnclosure(
    core,cell,anchorPoint);
  const FaceContainmentResult frozenImport=importFrozenCoreRoot(core);
  double coreParameterSlopeMax=0.;
  for(const MuSlopes&nodeSlopes:core.parameterSlopes)
    for(int parameter=0;parameter<3;++parameter)
      for(int coordinate=0;coordinate<4;++coordinate)
        coreParameterSlopeMax=std::max(coreParameterSlopeMax,
          absUpper(nodeSlopes[parameter][coordinate]));
  const bool success=cell.success&&core.success
    &&coreParameterSlopeMax==0.&&intoCell.success&&frozenImport.success;
  std::cout<<std::setprecision(17)
    <<"mode mu-grid-anchor\n"
    <<"grid_radius_factor "<<radiusFactor
       <<" core_radius_factor "<<coreRadiusFactor<<"\n"
    <<"anchor_cell_indices "<<anchorR<<" "<<anchorA2<<" "
       <<anchorEpsilon<<" parameter_cell "<<cell.parameterCell[0]<<" "
       <<cell.parameterCell[1]<<" "<<cell.parameterCell[2]<<"\n"
    <<"anchor_point "<<anchorPoint[0]<<" "<<anchorPoint[1]<<" "
       <<anchorPoint[2]<<"\n"
    <<"anchor_cell max_inclusion "<<cell.maxInclusion
    <<" max_contraction "<<cell.maxContraction
    <<" determinant "<<cell.determinant<<" "
    <<(cell.success?"PASS":"INCONCLUSIVE")<<"\n"
    <<"core max_inclusion "<<core.maxInclusion
    <<" max_contraction "<<core.maxContraction
    <<" determinant "<<core.determinant
    <<" node_parameter_slope_max "<<coreParameterSlopeMax<<" "
    <<(core.success&&coreParameterSlopeMax==0.?"PASS":"INCONCLUSIVE")<<"\n"
    <<"anchor_face direction core->cell max_ratio "<<intoCell.maxRatio
    <<" worst "<<intoCell.worstIndex<<" "
       <<shootingCoordinateName(intoCell.worstIndex)<<" "
    <<(intoCell.success?"PASS":"INCONCLUSIVE")<<"\n"
    <<"anchor_import phase "
       <<interval("5.8615055856447817","5.8615055856450482")
    <<" graph_c0 "<<interval("-1e-20","1e-20")
    <<" max_ratio "<<frozenImport.maxRatio
    <<" worst "<<frozenImport.worstIndex<<" "
       <<shootingCoordinateName(frozenImport.worstIndex)<<" "
    <<(frozenImport.success?"PASS":"INCONCLUSIVE")<<"\n"
    <<(success?"PASS":"INCONCLUSIVE")
    <<" mu-grid frozen-core anchor\n";
  return success?0:20;
}

int runMuRFaces(double radiusFactor){
  const interval zero(0.),one(1.);
  std::array<interval,17> faces;
  faces[0]=zero;
  for(int i=1;i<=16;++i)faces[i]=interval(i)/interval(200.);
  std::vector<MuAffineCellResult> cells;
  cells.reserve(16);
  bool success=true;
  std::cout<<std::setprecision(17)<<"mode mu-r-common-faces\n";
  for(int i=0;i<16;++i){
    const MuBox cell={
      interval(faces[i].leftBound(),faces[i+1].rightBound()),zero,one};
    const interval rCentre=pointAtMidpoint(cell[0]);
    const auto predictor=rFacePredictor(rCentre);
    cells.push_back(buildMuAffineCell(
      radiusFactor,cell,predictor.first,predictor.second,false));
    const MuAffineCellResult&result=cells.back();
    success=success&&result.success;
    std::cout<<"cell "<<i<<" r "<<result.parameterCell[0]
      <<" centre "<<result.parameterCentre[0]
      <<" phase "<<result.phi0
      <<" phase_r "<<result.phaseSlopes[0]
      <<" max_inclusion "<<result.maxInclusion
      <<" max_contraction "<<result.maxContraction
      <<" determinant "<<result.determinant<<" "
      <<(result.success?"PASS":"INCONCLUSIVE")<<"\n";
  }
  for(int faceIndex=1;faceIndex<16;++faceIndex){
    const MuBox face={faces[faceIndex],zero,one};
    for(int direction=0;direction<2;++direction){
      const int sourceIndex=direction?faceIndex:faceIndex-1;
      const int targetIndex=direction?faceIndex-1:faceIndex;
      const FaceContainmentResult result=mapMuFaceEnclosure(
        cells[sourceIndex],cells[targetIndex],face);
      success=success&&result.success;
      std::cout<<"face "<<faces[faceIndex]<<" direction "
        <<sourceIndex<<"->"<<targetIndex
        <<" delta "<<result.mapped[0]
        <<" graph_e "<<result.mapped[1]
        <<" max_ratio "<<result.maxRatio
        <<" worst "<<result.worstIndex<<" "
        <<shootingCoordinateName(result.worstIndex)<<" "
        <<(result.success?"PASS":"INCONCLUSIVE")<<"\n";
    }
  }

  const MuBox coreCell={zero,zero,one};
  const MuBox zeroSlopes={zero,zero,zero};
  const interval corePhase=rFacePredictor(zero).first;
  const MuAffineCellResult seedCore=buildMuAffineCell(
    radiusFactor,coreCell,corePhase,zeroSlopes,false,true);
  const MuBox anchorFace={faces[0],zero,one};
  const FaceContainmentResult seedIntoCore=mapMuFaceEnclosure(
    cells.front(),seedCore,anchorFace);
  IVector coreMinimum(seedCore.X.dimension());
  for(int i=0;i<coreMinimum.dimension();++i){
    const double radius=1.05*absUpper(seedIntoCore.mapped[i])+1.e-12;
    coreMinimum[i]=interval(-radius,radius);
  }
  const MuAffineCellResult core=buildMuAffineCell(
    radiusFactor,coreCell,corePhase,zeroSlopes,false,true,&coreMinimum);
  double coreParameterSlopeMax=0.;
  for(const MuSlopes&nodeSlopes:core.parameterSlopes)
    for(int parameter=0;parameter<3;++parameter)
      for(int coordinate=0;coordinate<4;++coordinate)
        coreParameterSlopeMax=std::max(coreParameterSlopeMax,
          absUpper(nodeSlopes[parameter][coordinate]));
  success=success&&core.success&&coreParameterSlopeMax==0.;
  std::cout<<"core r "<<core.parameterCell[0]
    <<" phase "<<core.phi0
    <<" node_parameter_slope_max "<<coreParameterSlopeMax
    <<" max_inclusion "<<core.maxInclusion
    <<" max_contraction "<<core.maxContraction
    <<" determinant "<<core.determinant<<" "
    <<(core.success&&coreParameterSlopeMax==0.?"PASS":"INCONCLUSIVE")<<"\n";
  const FaceContainmentResult intoCore=mapMuFaceEnclosure(
    cells.front(),core,anchorFace);
  const FaceContainmentResult intoFirst=mapMuFaceEnclosure(
    core,cells.front(),anchorFace);
  const FaceContainmentResult anchorImport=importFrozenCoreRoot(core);
  success=success&&intoCore.success&&anchorImport.success;
  std::cout<<"anchor_face "<<faces[0]<<" direction cell-0->core"
    <<" max_ratio "<<intoCore.maxRatio
    <<" worst "<<intoCore.worstIndex<<" "
    <<shootingCoordinateName(intoCore.worstIndex)<<" "
    <<(intoCore.success?"PASS":"INCONCLUSIVE")<<"\n"
    <<"anchor_face "<<faces[0]<<" direction core->cell-0"
    <<" max_ratio "<<intoFirst.maxRatio
    <<" worst "<<intoFirst.worstIndex<<" "
    <<shootingCoordinateName(intoFirst.worstIndex)<<" "
    <<(intoFirst.success?"PASS":"INCONCLUSIVE")<<"\n"
    <<"anchor_import phase "
    <<interval("5.8615055856447817","5.8615055856450482")
    <<" graph_c0 "<<interval("-1e-20","1e-20")
    <<" max_ratio "<<anchorImport.maxRatio
    <<" worst "<<anchorImport.worstIndex<<" "
    <<shootingCoordinateName(anchorImport.worstIndex)<<" "
    <<(anchorImport.success?"PASS":"INCONCLUSIVE")<<"\n";
  std::cout<<(success?"PASS":"INCONCLUSIVE")
    <<" mu-r common-face root identification\n";
  return success?0:20;
}
}

int main(int argc,char**argv){
 std::string stage="argument parsing";
 try{
 if(argc==4 && std::string(argv[1])=="mu-grid-root-jets-slab"){
   const double factor=std::stod(argv[2]);
   if(!std::isfinite(factor)||factor<=1.)
     throw std::invalid_argument("radius_factor must be finite and greater than one");
   stage="mu-grid true-source root C2 slab experiment";
   return runMuGridRootJetSlab(factor,std::stoi(argv[3]));
 }
 if(argc==6 && std::string(argv[1])=="mu-grid-root-jets"){
   const double factor=std::stod(argv[2]);
   if(!std::isfinite(factor)||factor<=1.)
     throw std::invalid_argument("radius_factor must be finite and greater than one");
   stage="mu-grid true-source root C2 experiment";
   return runMuGridRootJets(
     factor,std::stoi(argv[3]),std::stoi(argv[4]),std::stoi(argv[5]));
 }
 if(argc==6 && std::string(argv[1])=="mu-grid-first-hit"){
   const double factor=std::stod(argv[2]);
   if(!std::isfinite(factor)||factor<=1.)
     throw std::invalid_argument("radius_factor must be finite and greater than one");
   stage="mu-grid first-hit experiment";
   return runMuGridFirstHitCell(
     factor,std::stoi(argv[3]),std::stoi(argv[4]),std::stoi(argv[5]));
 }
 if(argc==4 && std::string(argv[1])=="mu-grid-first-hit-slab"){
   const double factor=std::stod(argv[2]);
   if(!std::isfinite(factor)||factor<=1.)
     throw std::invalid_argument("radius_factor must be finite and greater than one");
   stage="mu-grid first-hit slab experiment";
   return runMuGridFirstHitSlab(factor,std::stoi(argv[3]));
 }
 if(argc==7 && std::string(argv[1])=="mu-grid-face"){
   const double factor=std::stod(argv[2]);
   if(!std::isfinite(factor)||factor<=1.)
     throw std::invalid_argument("radius_factor must be finite and greater than one");
   stage="mu-grid common-face experiment";
   return runMuGridFace(factor,argv[3],std::stoi(argv[4]),
                        std::stoi(argv[5]),std::stoi(argv[6]));
 }
 if(argc==4 && std::string(argv[1])=="mu-grid-slab"){
   const double factor=std::stod(argv[2]);
   if(!std::isfinite(factor)||factor<=1.)
     throw std::invalid_argument("radius_factor must be finite and greater than one");
   stage="mu-grid slab experiment";
   return runMuGridSlab(factor,std::stoi(argv[3]));
 }
 if(argc==3 && std::string(argv[1])=="mu-grid-anchor"){
   const double factor=std::stod(argv[2]);
   if(!std::isfinite(factor)||factor<=1.)
     throw std::invalid_argument("radius_factor must be finite and greater than one");
   stage="mu-grid frozen-core anchor experiment";
   return runMuGridAnchor(factor);
 }
 if(argc==3 && std::string(argv[1])=="mu-r-faces"){
   const double factor=std::stod(argv[2]);
   if(!std::isfinite(factor)||factor<=1.)
     throw std::invalid_argument("radius_factor must be finite and greater than one");
   stage="mu-r common-face experiment";
   return runMuRFaces(factor);
 }
 if(argc==13 && std::string(argv[1])=="mu-affine"){
   const double factor=std::stod(argv[2]);
   if(!std::isfinite(factor)||factor<=1.)
     throw std::invalid_argument("radius_factor must be finite and greater than one");
   const MuBox parameterCell={cliCell(argv[3],argv[4]),
     cliCell(argv[5],argv[6]),cliCell(argv[7],argv[8])};
   const MuBox phaseSlopes={cliPoint(argv[10]),
     cliPoint(argv[11]),cliPoint(argv[12])};
   stage="mu-affine cell experiment";
   return runMuAffineCell(
     factor,parameterCell,cliPoint(argv[9]),phaseSlopes);
 }
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
     "[a2-faces radius_factor phi0_0 phi0_1 phi0_2 phi0_3] or "
     "[mu-r-faces radius_factor] or "
     "[mu-grid-anchor radius_factor] or "
     "[mu-grid-root-jets radius_factor r_index a2_index epsilon_index] or "
     "[mu-grid-root-jets-slab radius_factor r_index] or "
     "[mu-grid-first-hit radius_factor r_index a2_index epsilon_index] or "
     "[mu-grid-first-hit-slab radius_factor r_index] or "
     "[mu-grid-face radius_factor axis r_index a2_index epsilon_index] or "
     "[mu-grid-slab radius_factor r_index] or "
     "[mu-affine radius_factor r_lo r_hi a2_lo a2_hi eps_lo eps_hi "
     "phi0 phi_r phi_a2 phi_epsilon]");
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
