#include <algorithm>
#include <iomanip>
#include <iostream>
#include <stdexcept>

#include "capd/capdlib.h"

using namespace capd;

namespace {

double lower(const interval& x) { return x.leftBound(); }
double upper(const interval& x) { return x.rightBound(); }

} // namespace

int main() {
  try {
    // All displayed decimal constants are deliberately rounded away from
    // the sharp values proved by the dependency certificates.
    const interval c = interval(1.) / sqrt(interval(2.));
    const interval delta(.01);
    const interval rhoPlus(.00012);       // hyperbolic Fix(R) radius
    const interval physicalRPlus = interval(2.) * rhoPlus;
    const interval graphSlope(.005237906);
    const interval graphQuadratic(.25);
    const interval targetHalfWidth(2e-6);
    const interval heteroclinicCentreMismatch(1.19e-11);
    const interval thetaSlope1(1.209084078);
    const interval thetaSlope2(.829376691);
    const interval thetaSlope = thetaSlope1 + thetaSlope2;

    // If w=s-H(u), then |w(0)| <= rho + |H(u)| and the exact
    // difference equation gives D|w| <= -kappa |w|.
    const interval w0 = rhoPlus + graphQuadratic * sqr(rhoPlus);
    const interval kappa = c - (interval(1.) + graphSlope)
      * (delta + graphQuadratic * sqr(delta) + w0);

    // The sharper radial upper error is increasing for rho<=r<=delta:
    // |n|/r <= (r+.25 r^2+w0)^2/(2r).
    const interval radialError = sqr(
      delta + graphQuadratic * sqr(delta) + w0)
      / (interval(2.) * delta);
    const interval gamma = kappa / (c + radialError);
    const interval radiusRatio = rhoPlus / delta;
    const interval wExit = w0 * exp(gamma * log(radiusRatio));

    // The target chart controls its exit phase on the whole closed stable
    // square.  Compare any first-boundary point with the validated
    // heteroclinic point inside that square.
    const interval phaseSpan = thetaSlope
      * (targetHalfWidth + heteroclinicCentreMismatch);
    const interval unstableGraphDrift = graphSlope * delta * phaseSpan;
    const interval stableDisplacement = wExit + unstableGraphDrift
      + heteroclinicCentreMismatch;
    const interval stableSquareMargin = targetHalfWidth - stableDisplacement;

    // First angular variation.  With y=log(r/rho), p=d_theta/d_phi and
    // k=d(s/r)/d_phi, the exact polar equations yield
    // |p_y| <= r(C11|p|+C12|k|),
    // D|k| <= -m|k|+C21 r|p|.
    const interval a = c - interval(2.) * delta;
    const interval b = c + interval(2.) * delta;
    const interval matrixNorm = c * sqrt(interval(5.));
    const interval C11 = interval(8.) * b / sqr(a);
    const interval C12 = interval(4.) * b / sqr(a);
    const interval m = interval(2.) * c / b - delta * (
      interval(6.) / a
      + interval(2.) * (matrixNorm + interval(4.) * delta) / sqr(a));
    const interval C21 = interval(6.) / a
      + interval(4.) * (matrixNorm + interval(4.) * delta) / sqr(a);
    const interval q = C21 * delta / (m + interval(1.));
    const interval A = exp(C11 * delta);
    const interval denominator = interval(1.) - A * C12 * delta * q;
    const interval P = A * (interval(1.) + C12 * delta) / denominator;
    const interval K = interval(1.) + q * P;
    const interval pError = delta * (C11 * P + C12 * K);
    const interval pLower = interval(1.) - pError;
    const interval kExit = exp(m * log(radiusRatio)) + q * P;
    const interval intersectionDerivative = pLower
      - thetaSlope * delta * kExit;

    const interval quarterRMinus = physicalRPlus
      * exp(-interval::pi() / interval(2.));
    const interval turnRMinus = physicalRPlus
      * exp(-interval(2.) * interval::pi());

    if(!(lower(kappa) > .696
         && upper(wExit) < 1.585e-6
         && lower(stableSquareMargin) > 4e-7
         && lower(m) > 1.78
         && lower(denominator) > .99
         && lower(pLower) > .78
         && lower(intersectionDerivative) > .78))
      throw std::runtime_error("a local-annulus strict inequality failed");

    std::cout << std::setprecision(17)
      << "{\n"
      << "  \"status\": \"PASS-QUANTITATIVE-LOCAL-ANNULUS\",\n"
      << "  \"hyperbolic_exit_radius\": \"" << delta << "\",\n"
      << "  \"hyperbolic_source_radius_upper\": \"" << rhoPlus << "\",\n"
      << "  \"physical_source_radius_upper\": \"" << physicalRPlus << "\",\n"
      << "  \"physical_pi_over_2_annulus_radius_lower\": \""
      << quarterRMinus << "\",\n"
      << "  \"physical_turn_annulus_radius_lower\": \"" << turnRMinus << "\",\n"
      << "  \"graph_C1_bound_used\": \"" << graphSlope << "\",\n"
      << "  \"initial_w_upper\": \"" << w0 << "\",\n"
      << "  \"w_contraction_lower\": \"" << kappa << "\",\n"
      << "  \"radial_error_upper\": \"" << radialError << "\",\n"
      << "  \"decay_exponent\": \"" << gamma << "\",\n"
      << "  \"exit_w_upper\": \"" << wExit << "\",\n"
      << "  \"target_phase_span_upper\": \"" << phaseSpan << "\",\n"
      << "  \"unstable_graph_drift_upper\": \""
      << unstableGraphDrift << "\",\n"
      << "  \"stable_square_margin_lower\": \""
      << stableSquareMargin << "\",\n"
      << "  \"C11\": \"" << C11 << "\",\n"
      << "  \"C12\": \"" << C12 << "\",\n"
      << "  \"stable_log_norm_m\": \"" << m << "\",\n"
      << "  \"C21\": \"" << C21 << "\",\n"
      << "  \"q\": \"" << q << "\",\n"
      << "  \"p_sup_upper\": \"" << P << "\",\n"
      << "  \"k_sup_upper\": \"" << K << "\",\n"
      << "  \"p_lower\": \"" << pLower << "\",\n"
      << "  \"k_exit_upper\": \"" << kExit << "\",\n"
      << "  \"intersection_derivative_lower\": \""
      << intersectionDerivative << "\"\n"
      << "}\n";
    return 0;
  } catch(const std::exception& error) {
    std::cerr << "EXCEPTION: " << error.what() << "\n";
    return 12;
  }
}
