#include <algorithm>
#include <array>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <stdexcept>

#include "capd/capdlib.h"
#include "tail_graph_generated.hpp"

using capd::interval;

namespace papera_ad {

struct Jet3 {
  interval value;
  std::array<interval,3> gradient;
  std::array<std::array<interval,3>,3> hessian;

  Jet3() : value(0.) { clear(); }
  Jet3(int x) : value(x) { clear(); }
  Jet3(long x) : value(static_cast<double>(x)) { clear(); }
  Jet3(long long x) : value(static_cast<double>(x)) { clear(); }
  Jet3(double x) : value(x) { clear(); }
  Jet3(const interval& x) : value(x) { clear(); }

  void clear() {
    for(auto& x:gradient) x=0.;
    for(auto& row:hessian) for(auto& x:row) x=0.;
  }

  static Jet3 variable(const interval& x,int index) {
    Jet3 result(x);
    result.gradient[index]=1.;
    return result;
  }

  // Set the value and an exact affine derivative.  This lets us evaluate on
  // old-coordinate boxes (e,d,omega), while differentiating with respect to
  // x=(e,c,omega), c=d-sqrt(3)omega/2, without dependency inflation.
  static Jet3 affine(const interval& x,const std::array<interval,3>& derivative) {
    Jet3 result(x);
    result.gradient=derivative;
    return result;
  }

  Jet3& operator+=(const Jet3& other) {
    value+=other.value;
    for(int i=0;i<3;++i) {
      gradient[i]+=other.gradient[i];
      for(int j=0;j<3;++j) hessian[i][j]+=other.hessian[i][j];
    }
    return *this;
  }

  Jet3& operator-=(const Jet3& other) {
    value-=other.value;
    for(int i=0;i<3;++i) {
      gradient[i]-=other.gradient[i];
      for(int j=0;j<3;++j) hessian[i][j]-=other.hessian[i][j];
    }
    return *this;
  }
};

Jet3 operator+(Jet3 x,const Jet3& y) { return x+=y; }
Jet3 operator-(Jet3 x,const Jet3& y) { return x-=y; }
Jet3 operator-(const Jet3& x) {
  Jet3 result;
  result.value=-x.value;
  for(int i=0;i<3;++i) {
    result.gradient[i]=-x.gradient[i];
    for(int j=0;j<3;++j) result.hessian[i][j]=-x.hessian[i][j];
  }
  return result;
}

Jet3 operator*(const Jet3& x,const Jet3& y) {
  Jet3 result;
  result.value=x.value*y.value;
  for(int i=0;i<3;++i) {
    result.gradient[i]=x.gradient[i]*y.value+x.value*y.gradient[i];
    for(int j=0;j<3;++j)
      result.hessian[i][j]
        =x.hessian[i][j]*y.value+x.gradient[i]*y.gradient[j]
         +x.gradient[j]*y.gradient[i]+x.value*y.hessian[i][j];
  }
  return result;
}

Jet3 reciprocal(const Jet3& x) {
  Jet3 result;
  const interval inverse=interval(1.)/x.value;
  const interval first=-inverse*inverse;
  const interval second=interval(2.)*inverse*inverse*inverse;
  result.value=inverse;
  for(int i=0;i<3;++i) {
    result.gradient[i]=first*x.gradient[i];
    for(int j=0;j<3;++j)
      result.hessian[i][j]
        =second*x.gradient[i]*x.gradient[j]+first*x.hessian[i][j];
  }
  return result;
}

Jet3 operator/(const Jet3& x,const Jet3& y) { return x*reciprocal(y); }

Jet3 sqrt(const Jet3& x) {
  using std::sqrt;
  Jet3 result;
  const interval root=sqrt(x.value);
  const interval first=interval(1.)/(interval(2.)*root);
  const interval second=-interval(1.)/(interval(4.)*x.value*root);
  result.value=root;
  for(int i=0;i<3;++i) {
    result.gradient[i]=first*x.gradient[i];
    for(int j=0;j<3;++j)
      result.hessian[i][j]
        =second*x.gradient[i]*x.gradient[j]+first*x.hessian[i][j];
  }
  return result;
}

} // namespace papera_ad

namespace {

using papera_ad::Jet3;

double absUpper(const interval& x) {
  return std::max(std::abs(x.leftBound()),std::abs(x.rightBound()));
}

interval magnitudeEnclosure(const interval& x) {
  return interval(0.,absUpper(x));
}

double frobeniusVector(const std::array<interval,3>& x) {
  interval sum(0.);
  for(const auto& value:x) {
    const interval magnitude=magnitudeEnclosure(value);
    sum+=magnitude*magnitude;
  }
  using std::sqrt;
  return sqrt(sum).rightBound();
}

double frobeniusMatrix(const std::array<std::array<interval,3>,3>& x) {
  interval sum(0.);
  for(const auto& row:x) for(const auto& value:row) {
    const interval magnitude=magnitudeEnclosure(value);
    sum+=magnitude*magnitude;
  }
  using std::sqrt;
  return sqrt(sum).rightBound();
}

double tensorFrobenius(const std::array<Jet3,3>& x) {
  interval sum(0.);
  for(const auto& output:x)
    for(const auto& row:output.hessian)
      for(const auto& value:row) {
        const interval magnitude=magnitudeEnclosure(value);
        sum+=magnitude*magnitude;
      }
  using std::sqrt;
  return sqrt(sum).rightBound();
}

double matrixGradientFrobenius(const std::array<Jet3,3>& x) {
  interval sum(0.);
  for(const auto& output:x)
    for(const auto& value:output.gradient) {
      const interval magnitude=magnitudeEnclosure(value);
      sum+=magnitude*magnitude;
    }
  using std::sqrt;
  return sqrt(sum).rightBound();
}

double logarithmicNormGershgorin(const std::array<Jet3,3>& field) {
  double bound=-std::numeric_limits<double>::infinity();
  for(int i=0;i<3;++i) {
    interval row=field[i].gradient[i];
    for(int j=0;j<3;++j) if(i!=j) {
      const interval symmetric=(field[i].gradient[j]+field[j].gradient[i])/2.;
      row+=magnitudeEnclosure(symmetric);
    }
    bound=std::max(bound,row.rightBound());
  }
  return bound;
}

struct Bounds {
  double defect=0.;
  double amin=std::numeric_limits<double>::infinity();
  double mu=-std::numeric_limits<double>::infinity();
  double B=0.;
  double D=0.;
  double Fyy=0.;
  double Fyxi=0.;
  double Gyy=0.;
  double Gyxi=0.;
};

void includeCell(Bounds& bounds,
                 const interval& eBox,
                 const interval& dBox,
                 const interval& omegaBox,
                 const interval& xiBox) {
  using papera_ad::sqrt;
  const Jet3 e=Jet3::variable(eBox,0);
  const Jet3 omega=Jet3::variable(omegaBox,2);
  const Jet3 r3=sqrt(Jet3(3));
  const Jet3 k=r3/Jet3(2);
  const Jet3 d=Jet3::affine(dBox,{interval(0.),interval(1.),k.value});
  const Jet3 q=d-Jet3(2)/r3;
  const Jet3 xi(xiBox);

  const Jet3 h=papera_tail::h7(e,d,omega);
  const Jet3 R=papera_tail::h7_defect(e,d,omega);
  const Jet3 A=papera_tail::h7_expansion(e,d,omega);

  const Jet3 Fe=e*(h+xi);
  const Jet3 Fd=Jet3(1.5)*(h+xi)*q-e;
  const Jet3 Fo=e*q+Jet3(2)*(h+xi)*(omega-Jet3(1));
  const std::array<Jet3,3> F={Fe,Fd-k*Fo,Fo};

  // F_xi in the sheared coordinates; its x-gradient is F_{y xi}.
  const Jet3 Be=e;
  const Jet3 Bd=Jet3(1.5)*q-k*Jet3(2)*(omega-Jet3(1));
  const Jet3 Bo=Jet3(2)*(omega-Jet3(1));
  const std::array<Jet3,3> B={Be,Bd,Bo};

  const Jet3 G=R+A*xi+Jet3(1.5)*xi*xi;

  bounds.defect=std::max(bounds.defect,absUpper(R.value));
  bounds.amin=std::min(bounds.amin,(A.value+interval(3.)*xiBox).leftBound());
  bounds.mu=std::max(bounds.mu,logarithmicNormGershgorin(F));
  std::array<interval,3> bValues={B[0].value,B[1].value,B[2].value};
  bounds.B=std::max(bounds.B,frobeniusVector(bValues));
  bounds.D=std::max(bounds.D,frobeniusVector(G.gradient));
  bounds.Fyy=std::max(bounds.Fyy,tensorFrobenius(F));
  bounds.Fyxi=std::max(bounds.Fyxi,matrixGradientFrobenius(B));
  bounds.Gyy=std::max(bounds.Gyy,frobeniusMatrix(G.hessian));
  bounds.Gyxi=std::max(bounds.Gyxi,frobeniusVector(A.gradient));
}

interval cell(const interval& domain,int index,int count) {
  const interval lo(domain.leftBound());
  const interval hi(domain.rightBound());
  const interval width=hi-lo;
  const interval left=lo+width*interval(index)/interval(count);
  const interval right=lo+width*interval(index+1)/interval(count);
  // Adjacent cells overlap by any rounding uncertainty, so their union is a
  // certified cover of the decimal input domain.
  return interval(left.leftBound(),right.rightBound());
}

} // namespace

int main() {
  try {
    // Subdivision is part of the certificate: every cell is evaluated with
    // outward-rounded FILIB intervals.  The boxes exactly tile D.
    constexpr int ne=24, nd=8, no=24;
    const interval xi("-0.00000001","0.00000001");
    const interval eUpper("0.06","0.06");
    const interval eDomain(0.,eUpper.rightBound());
    const interval dDomain("-0.001","0.001");
    const interval omegaDomain("-0.01","0.02");
    Bounds bounds;
    for(int i=0;i<ne;++i)
      for(int j=0;j<nd;++j)
        for(int k=0;k<no;++k)
          includeCell(bounds,
                      cell(eDomain,i,ne),
                      cell(dDomain,j,nd),
                      cell(omegaDomain,k,no),xi);

    constexpr double rho=1e-8;
    constexpr double alpha=1e-5;
    constexpr double beta=1e-3;
    const interval rhoI(rho),alphaI(alpha);
    const interval normalLower(bounds.amin),muUpper(bounds.mu);
    const interval bUpper(bounds.B),dUpper(bounds.D);
    const double exitMargin=(
      normalLower*rhoI-interval(bounds.defect)
      -interval(1.5)*rhoI*rhoI
    ).leftBound();
    const double coneMargin=(
      alphaI*(normalLower-muUpper)-dUpper-bUpper*alphaI*alphaI
    ).leftBound();
    const double verticalGrowth=(normalLower-dUpper/alphaI).leftBound();
    const double gamma1=(
      normalLower-muUpper-interval(2.)*bUpper*alphaI
    ).leftBound();
    const double gamma2=(
      normalLower-interval(2.)*muUpper-interval(3.)*bUpper*alphaI
    ).leftBound();
    const interval q2Upper=
      interval(bounds.Gyy)+interval(2.)*interval(bounds.Gyxi)*alphaI
      +interval(3.)*alphaI*alphaI
      +alphaI*(interval(bounds.Fyy)
               +interval(2.)*interval(bounds.Fyxi)*alphaI);
    const double q2=q2Upper.rightBound();
    const double betaRequired=(q2Upper/interval(gamma2)).rightBound();

    if(!(exitMargin>0.)) throw std::runtime_error("vertical exit failed");
    if(!(coneMargin>0.)) throw std::runtime_error("C1 cone failed");
    if(!(verticalGrowth>0.)) throw std::runtime_error("vertical growth failed");
    if(!(gamma1>0.)) throw std::runtime_error("C1 rate failed");
    if(!(gamma2>0.)) throw std::runtime_error("C2 bunching failed");
    if(!(betaRequired<beta)) throw std::runtime_error("C2 graph bound failed");

    std::cout << std::setprecision(17)
      << "{\n"
      << "  \"status\": \"PASS-GRAPH-TRANSFORM-INEQUALITIES\",\n"
      << "  \"tail_block_e\": \"" << eDomain << "\",\n"
      << "  \"tail_block_d\": \"" << dDomain << "\",\n"
      << "  \"tail_block_omega\": \"" << omegaDomain << "\",\n"
      << "  \"subdivision\": [" << ne << "," << nd << "," << no << "],\n"
      << "  \"rho\": " << rho << ",\n"
      << "  \"alpha\": " << alpha << ",\n"
      << "  \"beta\": " << beta << ",\n"
      << "  \"defect_bound\": " << bounds.defect << ",\n"
      << "  \"normal_expansion_lower\": " << bounds.amin << ",\n"
      << "  \"base_log_norm_upper\": " << bounds.mu << ",\n"
      << "  \"B_norm_upper\": " << bounds.B << ",\n"
      << "  \"D_norm_upper\": " << bounds.D << ",\n"
      << "  \"Fyy_norm_upper\": " << bounds.Fyy << ",\n"
      << "  \"Fyxi_norm_upper\": " << bounds.Fyxi << ",\n"
      << "  \"Gyy_norm_upper\": " << bounds.Gyy << ",\n"
      << "  \"Gyxi_norm_upper\": " << bounds.Gyxi << ",\n"
      << "  \"vertical_exit_margin\": " << exitMargin << ",\n"
      << "  \"cone_margin\": " << coneMargin << ",\n"
      << "  \"vertical_growth_lower\": " << verticalGrowth << ",\n"
      << "  \"C1_gap\": " << gamma1 << ",\n"
      << "  \"C2_gap\": " << gamma2 << ",\n"
      << "  \"C2_forcing\": " << q2 << ",\n"
      << "  \"C2_bound_required\": " << betaRequired << "\n"
      << "}\n";
    return 0;
  } catch(const std::exception& error) {
    std::cerr << "FAIL: " << error.what() << "\n";
    return 10;
  }
}
