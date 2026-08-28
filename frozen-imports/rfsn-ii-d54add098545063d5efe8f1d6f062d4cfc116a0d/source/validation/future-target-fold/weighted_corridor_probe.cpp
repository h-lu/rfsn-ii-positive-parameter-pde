#include <algorithm>
#include <array>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <stdexcept>

#include "capd/capdlib.h"
#include "weighted_tail_generated.hpp"

using capd::interval;

namespace papera_weighted_ad {

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

  static Jet4 variable(const interval& x,int index) {
    Jet4 result(x);
    result.gradient[index]=1.;
    return result;
  }

  Jet4& operator+=(const Jet4& other) {
    value+=other.value;
    for(int i=0;i<4;++i) gradient[i]+=other.gradient[i];
    return *this;
  }
  Jet4& operator-=(const Jet4& other) {
    value-=other.value;
    for(int i=0;i<4;++i) gradient[i]-=other.gradient[i];
    return *this;
  }
};

Jet4 operator+(Jet4 x,const Jet4& y) { return x+=y; }
Jet4 operator-(Jet4 x,const Jet4& y) { return x-=y; }
Jet4 operator-(const Jet4& x) {
  Jet4 result;
  result.value=-x.value;
  for(int i=0;i<4;++i) result.gradient[i]=-x.gradient[i];
  return result;
}
Jet4 operator*(const Jet4& x,const Jet4& y) {
  Jet4 result;
  result.value=x.value*y.value;
  for(int i=0;i<4;++i)
    result.gradient[i]=x.gradient[i]*y.value+x.value*y.gradient[i];
  return result;
}
Jet4 reciprocal(const Jet4& x) {
  Jet4 result;
  result.value=interval(1.)/x.value;
  for(int i=0;i<4;++i)
    result.gradient[i]=-x.gradient[i]/(x.value*x.value);
  return result;
}
Jet4 operator/(const Jet4& x,const Jet4& y) { return x*reciprocal(y); }
Jet4 sqrt(const Jet4& x) {
  using std::sqrt;
  Jet4 result;
  result.value=sqrt(x.value);
  for(int i=0;i<4;++i)
    result.gradient[i]=x.gradient[i]/(interval(2.)*result.value);
  return result;
}

} // namespace papera_weighted_ad

namespace {

using papera_weighted_ad::Jet4;

double absUpper(const interval& x) {
  return std::max(std::abs(x.leftBound()),std::abs(x.rightBound()));
}

interval magnitudeEnclosure(const interval& x) {
  return interval(0.,absUpper(x));
}

interval cell(const interval& domain,int index,int count) {
  const interval lo(domain.leftBound()), hi(domain.rightBound());
  const interval width=hi-lo;
  const interval left=lo+width*interval(index)/interval(count);
  const interval right=lo+width*interval(index+1)/interval(count);
  return interval(left.leftBound(),right.rightBound());
}

double vectorNorm(const std::array<interval,3>& x) {
  interval sum(0.);
  for(const auto& value:x) {
    const interval magnitude=magnitudeEnclosure(value);
    sum+=magnitude*magnitude;
  }
  using std::sqrt;
  return sqrt(sum).rightBound();
}

double logNormGershgorin(
    const std::array<std::array<interval,3>,3>& matrix) {
  double bound=-std::numeric_limits<double>::infinity();
  for(int i=0;i<3;++i) {
    interval row=matrix[i][i];
    for(int j=0;j<3;++j) if(i!=j)
      row+=magnitudeEnclosure((matrix[i][j]+matrix[j][i])/interval(2.));
    bound=std::max(bound,row.rightBound());
  }
  return bound;
}

struct Bounds {
  double energyLowMin=std::numeric_limits<double>::infinity();
  double energyLowMax=-std::numeric_limits<double>::infinity();
  double energyHighMin=std::numeric_limits<double>::infinity();
  double energyHighMax=-std::numeric_limits<double>::infinity();
  double energyAMin=std::numeric_limits<double>::infinity();
  double energyAMax=-std::numeric_limits<double>::infinity();
  double pOverEMin=std::numeric_limits<double>::infinity();
  double pOverEMax=-std::numeric_limits<double>::infinity();
  double bLowerMin=std::numeric_limits<double>::infinity();
  double bUpperMax=-std::numeric_limits<double>::infinity();
  double zetaLowerMax=-std::numeric_limits<double>::infinity();
  double zetaUpperMin=std::numeric_limits<double>::infinity();
  double mu=-std::numeric_limits<double>::infinity();
  double B=0.;
  double D=0.;
  double normalMin=std::numeric_limits<double>::infinity();
};

template<class S>
std::array<S,4> oldField(const S& e,const S& aa,const S& bb,const S& zeta) {
  return {
    papera_weighted_tail::e_dot(e,aa,bb,zeta),
    papera_weighted_tail::a_dot(e,aa,bb,zeta),
    papera_weighted_tail::b_dot(e,aa,bb,zeta),
    papera_weighted_tail::zeta_dot(e,aa,bb,zeta)
  };
}

void includeCell(Bounds& bounds,
                 const interval& eBox,
                 const interval& aBox,
                 const interval& bBox,
                 const interval& zetaBox) {
  using papera_weighted_ad::sqrt;
  const Jet4 e=Jet4::variable(eBox,0);
  const Jet4 aa=Jet4::variable(aBox,1);
  const Jet4 bb=Jet4::variable(bBox,2);
  const Jet4 zeta=Jet4::variable(zetaBox,3);
  const auto field=oldField(e,aa,bb,zeta);
  const Jet4 energy=papera_weighted_tail::energy(e,aa,bb,zeta);
  const Jet4 action=-sqrt(Jet4(3))*energy/Jet4(4);

  bounds.energyAMin=std::min(bounds.energyAMin,
                            energy.gradient[1].leftBound());
  bounds.energyAMax=std::max(bounds.energyAMax,
                            energy.gradient[1].rightBound());
  const interval pOverE=papera_weighted_tail::p_over_e(
    eBox,aBox,bBox,zetaBox
  );
  bounds.pOverEMin=std::min(bounds.pOverEMin,pOverE.leftBound());
  bounds.pOverEMax=std::max(bounds.pOverEMax,pOverE.rightBound());

  // Derivative of w=(e,a,b,zeta) with respect to
  // x=(e, action=-sqrt(3)E/4, b, zeta).
  std::array<std::array<interval,4>,4> inverse{};
  for(auto& row:inverse) row.fill(interval(0.));
  inverse[0][0]=1.;
  inverse[1][0]=-action.gradient[0]/action.gradient[1];
  inverse[1][1]=interval(1.)/action.gradient[1];
  inverse[1][2]=-action.gradient[2]/action.gradient[1];
  inverse[1][3]=-action.gradient[3]/action.gradient[1];
  inverse[2][2]=1.;
  inverse[3][3]=1.;

  std::array<std::array<interval,4>,4> transformed{};
  for(auto& row:transformed) row.fill(interval(0.));
  // New field is (e_dot, 0, b_dot, zeta_dot).
  for(int output:{0,2,3})
    for(int input=0;input<4;++input)
      for(int oldInput=0;oldInput<4;++oldInput)
        transformed[output][input]
          +=field[output].gradient[oldInput]*inverse[oldInput][input];

  std::array<std::array<interval,3>,3> C{};
  std::array<interval,3> B{},D{};
  const int baseOutputs[3]={0,1,2};
  const int baseInputs[3]={0,1,2};
  for(int i=0;i<3;++i) {
    B[i]=transformed[baseOutputs[i]][3];
    D[i]=transformed[3][baseInputs[i]];
    for(int j=0;j<3;++j)
      C[i][j]=transformed[baseOutputs[i]][baseInputs[j]];
  }
  bounds.mu=std::max(bounds.mu,logNormGershgorin(C));
  bounds.B=std::max(bounds.B,vectorNorm(B));
  bounds.D=std::max(bounds.D,vectorNorm(D));
  bounds.normalMin=std::min(bounds.normalMin,
                           transformed[3][3].leftBound());
}

void includeFaces(Bounds& bounds,
                  const interval& eBox,
                  const interval& bOrABox,
                  const interval& zetaBox,
                  bool energyFaces) {
  if(energyFaces) {
    const interval bBox=bOrABox;
    const interval low=papera_weighted_tail::energy(
      eBox,interval("0.001","0.001"),bBox,zetaBox
    );
    const interval high=papera_weighted_tail::energy(
      eBox,interval("0.0065","0.0065"),bBox,zetaBox
    );
    bounds.energyLowMin=std::min(bounds.energyLowMin,low.leftBound());
    bounds.energyLowMax=std::max(bounds.energyLowMax,low.rightBound());
    bounds.energyHighMin=std::min(bounds.energyHighMin,high.leftBound());
    bounds.energyHighMax=std::max(bounds.energyHighMax,high.rightBound());
  } else {
    const interval aBox=bOrABox;
    const interval bLower=papera_weighted_tail::b_dot(
      eBox,aBox,interval("-0.01","-0.01"),zetaBox
    );
    const interval bUpper=papera_weighted_tail::b_dot(
      eBox,aBox,interval("0.01","0.01"),zetaBox
    );
    const interval zetaLower=papera_weighted_tail::zeta_dot(
      eBox,aBox,interval("-0.01","0.01"),interval("-2","-2")
    );
    const interval zetaUpper=papera_weighted_tail::zeta_dot(
      eBox,aBox,interval("-0.01","0.01"),interval("2","2")
    );
    bounds.bLowerMin=std::min(bounds.bLowerMin,bLower.leftBound());
    bounds.bUpperMax=std::max(bounds.bUpperMax,bUpper.rightBound());
    bounds.zetaLowerMax=std::max(bounds.zetaLowerMax,zetaLower.rightBound());
    bounds.zetaUpperMin=std::min(bounds.zetaUpperMin,zetaUpper.leftBound());
  }
}

} // namespace

int main() {
  try {
    const interval eUpper("0.06","0.06");
    const interval eDomain(0.,eUpper.rightBound());
    const interval aDomain("0.001","0.0065");
    const interval bDomain("-0.01","0.01");
    const interval zetaDomain("-2","2");
    const interval energyTarget("-0.012","-0.005");
    constexpr int ne=12, na=3, nb=8, nz=4;
    Bounds bounds;
    for(int i=0;i<ne;++i) {
      const interval eBox=cell(eDomain,i,ne);
      for(int k=0;k<nb;++k)
        for(int l=0;l<nz;++l)
          includeFaces(bounds,eBox,cell(bDomain,k,nb),
                       cell(zetaDomain,l,nz),true);
      for(int j=0;j<na;++j) {
        const interval aBox=cell(aDomain,j,na);
        for(int l=0;l<nz;++l)
          includeFaces(bounds,eBox,aBox,cell(zetaDomain,l,nz),false);
        for(int k=0;k<nb;++k)
          for(int l=0;l<nz;++l)
            includeCell(bounds,eBox,aBox,cell(bDomain,k,nb),
                        cell(zetaDomain,l,nz));
      }
    }

    // A deliberately generous slope for the graph zeta=Gamma(e,action,b).
    constexpr double alpha=10.;
    const interval alphaI(alpha);
    const interval normalLower(bounds.normalMin);
    const interval muUpper(bounds.mu);
    const interval bUpper(bounds.B);
    const interval dUpper(bounds.D);
    const double coneMargin=(
      alphaI*(normalLower-muUpper)-dUpper-bUpper*alphaI*alphaI
    ).leftBound();
    const double verticalGrowth=(normalLower-dUpper/alphaI).leftBound();
    const double c0Gap=(normalLower-bUpper*alphaI).leftBound();
    const double c1Gap=(
      normalLower-muUpper-interval(2.)*bUpper*alphaI
    ).leftBound();
    const double c2Gap=(
      normalLower-interval(2.)*muUpper-interval(3.)*bUpper*alphaI
    ).leftBound();

    if(!(bounds.energyLowMin>energyTarget.rightBound()))
      throw std::runtime_error("energy does not exclude lower a face");
    if(!(bounds.energyHighMax<energyTarget.leftBound()))
      throw std::runtime_error("energy does not exclude upper a face");
    if(!(bounds.energyAMax<0.))
      throw std::runtime_error("energy is not monotone in a");
    if(!(bounds.pOverEMax<0.))
      throw std::runtime_error("e is not strictly decreasing for e>0");
    if(!(bounds.bLowerMin>0. && bounds.bUpperMax<0.))
      throw std::runtime_error("b faces are not inward");
    if(!(bounds.zetaLowerMax<0. && bounds.zetaUpperMin>0.))
      throw std::runtime_error("zeta faces are not outward");
    if(!(coneMargin>0. && verticalGrowth>0. && c0Gap>0.
         && c1Gap>0. && c2Gap>0.)) {
      std::cerr << std::setprecision(17)
        << "weighted cone diagnostics: mu=" << bounds.mu
        << " B=" << bounds.B << " D=" << bounds.D
        << " normal=" << bounds.normalMin
        << " alpha=" << alpha << " margin=" << coneMargin
        << " growth=" << verticalGrowth << " C0=" << c0Gap
        << " C1=" << c1Gap
        << " C2=" << c2Gap << "\n";
      throw std::runtime_error("weighted graph cone failed");
    }

    std::cout << std::setprecision(17)
      << "{\n"
      << "  \"status\": \"PASS-WEIGHTED-PHYSICAL-CORRIDOR\",\n"
      << "  \"subdivision\": [" << ne << "," << na << ","
      << nb << "," << nz << "],\n"
      << "  \"energy_target\": \"" << energyTarget << "\",\n"
      << "  \"energy_at_a_lower\": \"[" << bounds.energyLowMin
      << ", " << bounds.energyLowMax << "]\",\n"
      << "  \"energy_at_a_upper\": \"[" << bounds.energyHighMin
      << ", " << bounds.energyHighMax << "]\",\n"
      << "  \"energy_da\": \"[" << bounds.energyAMin << ", "
      << bounds.energyAMax << "]\",\n"
      << "  \"p_over_e\": \"[" << bounds.pOverEMin << ", "
      << bounds.pOverEMax << "]\",\n"
      << "  \"b_lower_face_min\": " << bounds.bLowerMin << ",\n"
      << "  \"b_upper_face_max\": " << bounds.bUpperMax << ",\n"
      << "  \"zeta_lower_face_max\": " << bounds.zetaLowerMax << ",\n"
      << "  \"zeta_upper_face_min\": " << bounds.zetaUpperMin << ",\n"
      << "  \"base_log_norm_upper\": " << bounds.mu << ",\n"
      << "  \"B_norm_upper\": " << bounds.B << ",\n"
      << "  \"D_norm_upper\": " << bounds.D << ",\n"
      << "  \"normal_expansion_lower\": " << bounds.normalMin << ",\n"
      << "  \"cone_alpha\": " << alpha << ",\n"
      << "  \"cone_margin\": " << coneMargin << ",\n"
      << "  \"vertical_growth_lower\": " << verticalGrowth << ",\n"
      << "  \"C0_gap\": " << c0Gap << ",\n"
      << "  \"C1_gap\": " << c1Gap << ",\n"
      << "  \"C2_gap\": " << c2Gap << "\n"
      << "}\n";
    return 0;
  } catch(const std::exception& error) {
    std::cerr << "FAIL: " << error.what() << "\n";
    return 10;
  }
}
