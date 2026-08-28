#include <iomanip>
#include <iostream>
#include <stdexcept>

#include "capd/capdlib.h"
#include "heteroclinic_centres.hpp"
#include "weighted_tail_generated.hpp"

using capd::interval;

int main() {
  try {
    // This is the complete terminal node X used by the robust 148-dimensional
    // Krawczyk evaluation, not the much smaller final Krawczyk image.
    constexpr int n = papera_heteroclinic_centres::kSegments;
    const double u0 = papera_heteroclinic_centres::kCentres[n][0];
    const double p0 = papera_heteroclinic_centres::kCentres[n][1];
    const double v0 = papera_heteroclinic_centres::kCentres[n][2];
    const double q0 = papera_heteroclinic_centres::kCentres[n][3];
    const double ru = 2e-9 + 5e-7;
    const double rp = 2e-9 + 2e-6;
    const double rv = 2e-9 + 8e-6;
    const double rq = 2e-9 + 2e-6;
    const interval U(u0 - ru, u0 + ru);
    const interval P(p0 - rp, p0 + rp);
    const interval V(v0 - rv, v0 + rv);
    const interval Q(q0 - rq, q0 + rq);
    const interval e = -interval(1.) / U;
    const interval e32 = e * sqrt(e);
    const interval d = Q * e32 + interval(2.) / sqrt(interval(3.));
    const interval omega = interval(1.) + V * e * e;
    const interval a = d / (e * e * e);
    const interval b = (omega - e * e / interval(6.))
      / (e * e * e * e);
    const interval zeta(-2., 2.);
    const interval graphEnergy =
      papera_weighted_tail::energy(e, a, b, zeta);

    if(!(e.leftBound() > 0. && e.rightBound() < .06))
      throw std::runtime_error("terminal e leaves weighted corridor");
    if(!(a.leftBound() > -.0065 && a.rightBound() < .0065))
      throw std::runtime_error("terminal a leaves weighted corridor");
    if(!(b.leftBound() > -.01 && b.rightBound() < .01))
      throw std::runtime_error("terminal b leaves weighted corridor");
    if(!(graphEnergy.leftBound() > -.012
         && graphEnergy.rightBound() < .012))
      throw std::runtime_error("terminal graph fiber leaves energy slab");

    std::cout << std::setprecision(17)
      << "{\n"
      << "  \"status\": \"PASS-TERMINAL-PHYSICAL-CONTRACT\",\n"
      << "  \"terminal_X_U\": \"" << U << "\",\n"
      << "  \"terminal_X_P\": \"" << P << "\",\n"
      << "  \"terminal_X_V\": \"" << V << "\",\n"
      << "  \"terminal_X_Q\": \"" << Q << "\",\n"
      << "  \"e\": \"" << e << "\",\n"
      << "  \"a\": \"" << a << "\",\n"
      << "  \"b\": \"" << b << "\",\n"
      << "  \"energy_for_abs_zeta_le_2\": \""
      << graphEnergy << "\"\n"
      << "}\n";
    return 0;
  } catch(const std::exception& error) {
    std::cerr << "FAIL: " << error.what() << "\n";
    return 10;
  }
}
