#include <algorithm>
#include <array>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>

#include "capd/capdlib.h"
#include "fold_centres_generated.hpp"
#include "tail_graph_generated.hpp"

using namespace capd;

namespace papera_autodiff {

struct Jet4 {
  interval value;
  std::array<interval,4> gradient;
  std::array<std::array<interval,4>,4> hessian;

  Jet4() : value(0.) { clear(); }
  Jet4(int x) : value(x) { clear(); }
  Jet4(long x) : value(static_cast<double>(x)) { clear(); }
  Jet4(long long x) : value(static_cast<double>(x)) { clear(); }
  Jet4(double x) : value(x) { clear(); }
  Jet4(const interval& x) : value(x) { clear(); }

  void clear() {
    for(auto& x:gradient) x=0.;
    for(auto& row:hessian) for(auto& x:row) x=0.;
  }

  static Jet4 variable(const interval& x, int index) {
    Jet4 result(x);
    result.gradient[index]=1.;
    return result;
  }

  Jet4& operator+=(const Jet4& other);
  Jet4& operator-=(const Jet4& other);
};

Jet4& Jet4::operator+=(const Jet4& other) {
  value+=other.value;
  for(int i=0;i<4;++i) {
    gradient[i]+=other.gradient[i];
    for(int j=0;j<4;++j) hessian[i][j]+=other.hessian[i][j];
  }
  return *this;
}

Jet4& Jet4::operator-=(const Jet4& other) {
  value-=other.value;
  for(int i=0;i<4;++i) {
    gradient[i]-=other.gradient[i];
    for(int j=0;j<4;++j) hessian[i][j]-=other.hessian[i][j];
  }
  return *this;
}

Jet4 operator+(Jet4 left,const Jet4& right) { return left+=right; }
Jet4 operator-(Jet4 left,const Jet4& right) { return left-=right; }
Jet4 operator-(const Jet4& x) {
  Jet4 result;
  result.value=-x.value;
  for(int i=0;i<4;++i) {
    result.gradient[i]=-x.gradient[i];
    for(int j=0;j<4;++j) result.hessian[i][j]=-x.hessian[i][j];
  }
  return result;
}

Jet4 operator*(const Jet4& x,const Jet4& y) {
  Jet4 result;
  result.value=x.value*y.value;
  for(int i=0;i<4;++i) {
    result.gradient[i]=x.gradient[i]*y.value+x.value*y.gradient[i];
    for(int j=0;j<4;++j)
      result.hessian[i][j]
        =x.hessian[i][j]*y.value+x.gradient[i]*y.gradient[j]
         +x.gradient[j]*y.gradient[i]+x.value*y.hessian[i][j];
  }
  return result;
}

Jet4 reciprocal(const Jet4& x) {
  Jet4 result;
  const interval inverse=interval(1.)/x.value;
  const interval first=-sqr(inverse);
  const interval second=interval(2.)*inverse*inverse*inverse;
  result.value=inverse;
  for(int i=0;i<4;++i) {
    result.gradient[i]=first*x.gradient[i];
    for(int j=0;j<4;++j)
      result.hessian[i][j]
        =second*x.gradient[i]*x.gradient[j]+first*x.hessian[i][j];
  }
  return result;
}

Jet4 operator/(const Jet4& x,const Jet4& y) { return x*reciprocal(y); }

Jet4 sqrt(const Jet4& x) {
  using std::sqrt;
  Jet4 result;
  const interval root=sqrt(x.value);
  const interval first=interval(1.)/(interval(2.)*root);
  const interval second=-interval(1.)
    /(interval(4.)*x.value*root);
  result.value=root;
  for(int i=0;i<4;++i) {
    result.gradient[i]=first*x.gradient[i];
    for(int j=0;j<4;++j)
      result.hessian[i][j]
        =second*x.gradient[i]*x.gradient[j]+first*x.hessian[i][j];
  }
  return result;
}

} // namespace papera_autodiff

namespace {

using papera_autodiff::Jet4;
constexpr int kSegments=papera_fold_centres::kSegments;
constexpr int kExtendedDimension=8;
constexpr int kUnknowns=kExtendedDimension*(kSegments+1);
constexpr double kStep=papera_fold_centres::kFinalTime/kSegments;

int column(int node,int component) { return 8*node+component; }

IVector node(const IVector& all,int index) {
  IVector result(8);
  for(int component=0;component<8;++component)
    result[component]=all[column(index,component)];
  return result;
}

IVector centreVector() {
  IVector result(kUnknowns);
  for(int n=0;n<=kSegments;++n)
    for(int component=0;component<8;++component)
      result[column(n,component)]
        =papera_fold_centres::kCentres[n][component];
  return result;
}

double radiusAt(int nodeIndex,int component,bool robust) {
  if(!robust) return 3e-8;
  const double x=static_cast<double>(nodeIndex)/kSegments;
  switch(component) {
    case 0: return 2.5e-8+6e-7*std::pow(x,2);
    case 1: return 1e-7+1.25e-6*std::pow(x,20);
    case 2: return 1e-7+7.5e-6*std::pow(x,4);
    case 3: return 1e-7+2.5e-6*std::pow(x,3);
    case 4: return 5e-5+4e-2*std::pow(x,24);
    case 5: return 2e-4+1.6e-1*std::pow(x,40);
    case 6: return 2e-4+2.5e-2*std::pow(x,7);
    case 7: return 2e-5+1.5e-2*std::pow(x,5);
  }
  throw std::runtime_error("invalid component");
}

IVector boxAround(const IVector& centre,bool robust) {
  IVector result(kUnknowns);
  for(int i=0;i<kUnknowns;++i) {
    const double c=centre[i].mid().leftBound();
    const double radius=radiusAt(i/8,i%8,robust);
    result[i]=interval(c-radius,c+radius);
  }
  return result;
}

struct TargetCoordinates {
  Jet4 residual;
  std::array<Jet4,3> base;
};

TargetCoordinates targetCoordinates(const IVector& z) {
  using papera_autodiff::sqrt;
  const Jet4 U=Jet4::variable(z[0],0);
  const Jet4 P=Jet4::variable(z[1],1);
  const Jet4 V=Jet4::variable(z[2],2);
  const Jet4 Q=Jet4::variable(z[3],3);
  const Jet4 e=-Jet4(1)/U;
  const Jet4 e32=e*sqrt(e);
  const Jet4 p=P*e32;
  const Jet4 q=Q*e32;
  const Jet4 omega=Jet4(1)+V*e*e;
  const Jet4 d=q+Jet4(2)/sqrt(Jet4(3));
  const Jet4 c=d-sqrt(Jet4(3))*omega/Jet4(2);
  return {p-papera_tail::h7(e,d,omega),{e,c,omega}};
}

interval tangentTarget(const Jet4& target,const IVector& terminal) {
  interval result=0.;
  for(int i=0;i<4;++i) result+=target.gradient[i]*terminal[4+i];
  return result;
}

struct RobustTargetData {
  interval residual;
  interval tangentResidual;
  IVector gradient;
  IVector tangentStateDerivative;
};

RobustTargetData robustTarget(const IVector& point,
                              const IVector& box,
                              bool robust) {
  const TargetCoordinates pointData=targetCoordinates(point);
  const TargetCoordinates boxData=targetCoordinates(box);
  const interval rho=robust ? interval(-1e-8,1e-8) : interval(0.);
  const interval slope=robust ? interval(-1e-5,1e-5) : interval(0.);
  const interval curvature=robust ? interval(-1e-3,1e-3) : interval(0.);

  IVector gradient(4);
  IVector pointGradient(4);
  for(int i=0;i<4;++i) {
    gradient[i]=boxData.residual.gradient[i];
    pointGradient[i]=pointData.residual.gradient[i];
    for(int a=0;a<3;++a) {
      gradient[i]-=slope*boxData.base[a].gradient[i];
      pointGradient[i]-=slope*pointData.base[a].gradient[i];
    }
  }

  interval tangentResidual=0.;
  for(int i=0;i<4;++i)
    tangentResidual+=pointGradient[i]*point[4+i];

  IVector tangentStateDerivative(4);
  for(int i=0;i<4;++i) {
    interval derivative=0.;
    for(int j=0;j<4;++j)
      derivative+=boxData.residual.hessian[i][j]*box[4+j];

    for(int a=0;a<3;++a) {
      interval baseTangent=0.;
      for(int j=0;j<4;++j)
        baseTangent+=boxData.base[a].gradient[j]*box[4+j];
      for(int b=0;b<3;++b)
        derivative-=curvature*boxData.base[b].gradient[i]*baseTangent;
      interval secondCoordinate=0.;
      for(int j=0;j<4;++j)
        secondCoordinate+=boxData.base[a].hessian[i][j]*box[4+j];
      derivative-=slope*secondCoordinate;
    }
    tangentStateDerivative[i]=derivative;
  }
  return {pointData.residual.value+rho,tangentResidual,
          gradient,tangentStateDerivative};
}

double absUpper(const interval& x) {
  return std::max(std::abs(x.leftBound()),std::abs(x.rightBound()));
}

} // namespace

int main(int argc,char** argv) {
  try {
    const bool robust=(argc==2 && std::string(argv[1])=="--robust");
    const IVector centre=centreVector();
    const IVector X=boxAround(centre,robust);

    IMap field(
      "var:U,P,V,Q,a,b,c,d;"
      "fun:P,-U*U-V,Q,U,b,-2*U*a-c,d,a;"
    );
    IOdeSolver solver(field,25);
    solver.setAbsoluteTolerance(1e-14);
    solver.setRelativeTolerance(1e-14);

    IVector residual(kUnknowns);
    IMatrix derivative(kUnknowns,kUnknowns);
    derivative.clear();
    double residualSup=0.;

    for(int segment=0;segment<kSegments;++segment) {
      const IVector initialCentre=node(centre,segment);
      const IVector initialBox=node(X,segment);

      ITimeMap c0TimeMap(solver);
      C0HOTripletonSet c0Set(initialCentre);
      const IVector imageCentre=c0TimeMap(interval(kStep),c0Set);

      ITimeMap c1TimeMap(solver);
      C1HORect2Set c1Set(initialBox);
      c1TimeMap(interval(kStep),c1Set);
      const IMatrix monodromy=(IMatrix)c1Set;

      const IVector nextCentre=node(centre,segment+1);
      for(int output=0;output<8;++output) {
        const int row=8*segment+output;
        residual[row]=nextCentre[output]-imageCentre[output];
        residualSup=std::max(residualSup,absUpper(residual[row]));
        for(int input=0;input<8;++input)
          derivative[row][column(segment,input)]=-monodromy[output][input];
        derivative[row][column(segment+1,output)]+=1.;
      }
    }

    int row=8*kSegments;
    const IVector leftCentre=node(centre,0);
    const IVector terminalCentre=node(centre,kSegments);
    const IVector leftBox=node(X,0);
    const IVector terminalBox=node(X,kSegments);

    // P(0)=Q(0)=0, w_U(0)=1, w_P(0)=w_Q(0)=0.
    residual[row]=leftCentre[1];
    derivative[row++][column(0,1)]=1.;
    residual[row]=leftCentre[3];
    derivative[row++][column(0,3)]=1.;
    residual[row]=leftCentre[4]-1.;
    derivative[row++][column(0,4)]=1.;
    residual[row]=leftCentre[5];
    derivative[row++][column(0,5)]=1.;
    residual[row]=leftCentre[7];
    derivative[row++][column(0,7)]=1.;

    const RobustTargetData target=robustTarget(
      terminalCentre,terminalBox,robust
    );
    residual[row]=target.residual;
    for(int i=0;i<4;++i)
      derivative[row][column(kSegments,i)]=target.gradient[i];
    ++row;

    residual[row]=target.tangentResidual;
    for(int i=0;i<4;++i) {
      derivative[row][column(kSegments,i)]=target.tangentStateDerivative[i];
      derivative[row][column(kSegments,4+i)]=target.gradient[i];
    }
    ++row;

    const interval U0=leftCentre[0], V0=leftCentre[2];
    const interval a0=leftCentre[4], c0=leftCentre[6];
    residual[row]=(-interval(2.)*sqr(U0)-interval(2.)*V0)*a0
                  -interval(2.)*U0*c0;
    const interval U=leftBox[0], V=leftBox[2];
    const interval a=leftBox[4], c=leftBox[6];
    derivative[row][column(0,0)]=-interval(4.)*U*a-interval(2.)*c;
    derivative[row][column(0,2)]=-interval(2.)*a;
    derivative[row][column(0,4)]=-interval(2.)*sqr(U)-interval(2.)*V;
    derivative[row][column(0,6)]=-interval(2.)*U;
    ++row;
    if(row!=kUnknowns) throw std::runtime_error("row count mismatch");

    for(int i=8*kSegments;i<kUnknowns;++i)
      residualSup=std::max(residualSup,absUpper(residual[i]));

    DMatrix midpoint(kUnknowns,kUnknowns);
    for(int i=0;i<kUnknowns;++i)
      for(int j=0;j<kUnknowns;++j)
        midpoint[i][j]=derivative[i][j].mid().leftBound();
    const DMatrix doubleInverse=matrixAlgorithms::inverseMatrix(midpoint);
    IMatrix preconditioner(kUnknowns,kUnknowns);
    for(int i=0;i<kUnknowns;++i)
      for(int j=0;j<kUnknowns;++j)
        preconditioner[i][j]=doubleInverse[i][j];
    IMatrix remainder=IMatrix::Identity(kUnknowns)-preconditioner*derivative;
    const IVector contractionImage=remainder*(X-centre);
    const IVector krawczyk=centre-preconditioner*residual+contractionImage;
    double ratio=0.;
    double contractionRatio=0.;
    int worstIndex=-1;
    for(int i=0;i<kUnknowns;++i) {
      const double cMid=centre[i].mid().leftBound();
      const double correction=std::max(std::abs(krawczyk[i].leftBound()-cMid),
                                       std::abs(krawczyk[i].rightBound()-cMid));
      const double radius=radiusAt(i/8,i%8,robust);
      if(correction/radius>ratio) {
        ratio=correction/radius;
        worstIndex=i;
      }
      contractionRatio=std::max(
        contractionRatio,absUpper(contractionImage[i])/radius
      );
    }
    if(!subsetInterior(krawczyk,X)) {
      std::cerr << "Krawczyk failure ratio=" << ratio
                << " worst_index=" << worstIndex
                << " component=" << (worstIndex%8)
                << " node=" << (worstIndex/8) << "\n";
      std::array<std::pair<double,int>,kUnknowns> ranked{};
      for(int i=0;i<kUnknowns;++i) {
        const double cMid=centre[i].mid().leftBound();
        const double correction=std::max(std::abs(krawczyk[i].leftBound()-cMid),
                                         std::abs(krawczyk[i].rightBound()-cMid));
        const double radius=radiusAt(i/8,i%8,robust);
        ranked[i]={correction/radius,i};
      }
      std::sort(ranked.begin(),ranked.end(),
                [](const auto& a,const auto& b){ return a.first>b.first; });
      for(int k=0;k<12;++k) {
        const int i=ranked[k].second;
        std::cerr << "  rank=" << k+1 << " ratio=" << ranked[k].first
                  << " node=" << (i/8) << " component=" << (i%8)
                  << " K=" << krawczyk[i] << " centre=" << centre[i] << "\n";
      }
      for(int component=0;component<8;++component) {
        double maxCorrection=0.;
        int maxNode=-1;
        for(int n=0;n<=kSegments;++n) {
          const int i=column(n,component);
          const double cMid=centre[i].mid().leftBound();
          const double correction=std::max(std::abs(krawczyk[i].leftBound()-cMid),
                                           std::abs(krawczyk[i].rightBound()-cMid));
          if(correction>maxCorrection) { maxCorrection=correction; maxNode=n; }
        }
        std::cerr << "  component=" << component
                  << " max_correction=" << maxCorrection
                  << " node=" << maxNode << "\n";
      }
      std::cerr << "  base_corrections_by_node:\n";
      for(int n=0;n<=kSegments;++n) {
        std::cerr << "    " << n;
        for(int component=0;component<4;++component) {
          const int i=column(n,component);
          const double cMid=centre[i].mid().leftBound();
          const double correction=std::max(std::abs(krawczyk[i].leftBound()-cMid),
                                           std::abs(krawczyk[i].rightBound()-cMid));
          std::cerr << " " << correction;
        }
        std::cerr << "\n";
      }
      std::cerr << "  tangent_corrections_by_node:\n";
      for(int n=0;n<=kSegments;++n) {
        std::cerr << "    " << n;
        for(int component=4;component<8;++component) {
          const int i=column(n,component);
          const double cMid=centre[i].mid().leftBound();
          const double correction=std::max(std::abs(krawczyk[i].leftBound()-cMid),
                                           std::abs(krawczyk[i].rightBound()-cMid));
          std::cerr << " " << correction;
        }
        std::cerr << "\n";
      }
      throw std::runtime_error("Krawczyk inclusion failed");
    }

    const interval u=krawczyk[column(0,0)];
    const interval v=krawczyk[column(0,2)];
    const interval energy=-interval(2.)*u*u*u/interval(3.)
                          -interval(2.)*u*v;
    const IVector terminal=node(krawczyk,kSegments);
    using std::sqrt;
    const interval compactE=-interval(1.)/terminal[0];
    const interval compactE32=compactE*sqrt(compactE);
    const interval compactP=terminal[1]*compactE32;
    const interval compactD=terminal[3]*compactE32
                            +interval(2.)/sqrt(interval(3.));
    const interval compactOmega=interval(1.)+terminal[2]*compactE*compactE;
    if(!(compactE.leftBound()>0. && compactE.rightBound()<.06
         && compactD.leftBound()>-.001 && compactD.rightBound()<.001
         && compactOmega.leftBound()>-.01 && compactOmega.rightBound()<.02))
      throw std::runtime_error("terminal root is not inside certified tail block");
    const IVector terminalEvaluation=node(X,kSegments);
    const interval evaluationE=-interval(1.)/terminalEvaluation[0];
    const interval evaluationE32=evaluationE*sqrt(evaluationE);
    const interval evaluationD=terminalEvaluation[3]*evaluationE32
                               +interval(2.)/sqrt(interval(3.));
    const interval evaluationOmega=interval(1.)
      +terminalEvaluation[2]*evaluationE*evaluationE;
    const interval evaluationA=evaluationD
      /(evaluationE*evaluationE*evaluationE);
    const interval evaluationB=(evaluationOmega-evaluationE*evaluationE/6.)
      /(evaluationE*evaluationE*evaluationE*evaluationE);
    const interval evaluationGraphP=papera_tail::h7(
      evaluationE,evaluationD,evaluationOmega
    )+interval(-2.,2.)*evaluationE*evaluationE*evaluationE*evaluationE
                         *evaluationE*evaluationE*evaluationE*evaluationE;
    const interval evaluationQ=evaluationD-interval(2.)/sqrt(interval(3.));
    const interval evaluationGraphEnergy=(evaluationQ*evaluationQ
      -evaluationGraphP*evaluationGraphP+interval(2.)*evaluationOmega
      -interval(4.)/interval(3.))
      /(evaluationE*evaluationE*evaluationE);
    if(robust && !(evaluationA.leftBound()>.001
                   && evaluationA.rightBound()<.0065
                   && evaluationB.leftBound()>-.01
                   && evaluationB.rightBound()<.01
                   && evaluationGraphEnergy.leftBound()>-.012
                   && evaluationGraphEnergy.rightBound()<-.005))
      throw std::runtime_error("terminal evaluation box leaves weighted corridor");
    std::cout << std::setprecision(17)
      << "{\n"
      << "  \"status\": \""
      << (robust ? "PASS-ROBUST-H7-GRAPH-BOUNDS" : "PASS-TRUNCATED-H7-FOLD")
      << "\",\n"
      << "  \"unknowns\": " << kUnknowns << ",\n"
      << "  \"segments\": " << kSegments << ",\n"
      << "  \"source_u\": \"" << u << "\",\n"
      << "  \"source_v\": \"" << v << "\",\n"
      << "  \"energy\": \"" << energy << "\",\n"
      << "  \"newton_ratio\": " << ratio << ",\n"
      << "  \"contraction_ratio\": " << contractionRatio << ",\n"
      << "  \"terminal_compact_e\": \"" << compactE << "\",\n"
      << "  \"terminal_compact_p\": \"" << compactP << "\",\n"
      << "  \"terminal_compact_d\": \"" << compactD << "\",\n"
      << "  \"terminal_compact_omega\": \"" << compactOmega << "\",\n"
      << "  \"terminal_evaluation_e\": \"" << evaluationE << "\",\n"
      << "  \"terminal_evaluation_a\": \"" << evaluationA << "\",\n"
      << "  \"terminal_evaluation_b\": \"" << evaluationB << "\",\n"
      << "  \"terminal_evaluation_graph_energy\": \""
      << evaluationGraphEnergy << "\",\n"
      << "  \"centre_residual_sup\": " << residualSup << "\n"
      << "}\n";
    return 0;
  } catch(const std::exception& error) {
    std::cerr << "FAIL: " << error.what() << "\n";
    return 10;
  }
}
