#include <algorithm>
#include <array>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <limits>
#include <sstream>
#include <stdexcept>
#include <string>

#include "capd/capdlib.h"
#include "unstable_graph_terms.hpp"

// Design scout for a tight value enclosure of the direct P2bK source point.
// It propagates the already proved quadratic local-Wu enclosure from a tiny
// expanding circle to the inherited radius-1/100 physical outgoing face.
// Its phase is the direct P2bK phase, not the transported P2d face phase;
// this file is not a P2e trace certificate and its output is not claim bearing.

using namespace capd;
using capd::autodiff::Node;

namespace {

interval innerRadius() {
  return interval(1.) / interval(1000000.);
}

interval outerRadius() {
  return interval(1.) / interval(100.);
}

double midpoint(const interval& value) {
  return value.mid().leftBound();
}

interval point(const char* text) {
  return interval(text, text);
}

interval cell(const char* left, const char* right) {
  const interval lo = point(left);
  const interval hi = point(right);
  return interval(lo.leftBound(), hi.rightBound());
}

interval midpointInterval(const interval& value) {
  return interval(midpoint(value));
}

interval halfInterval(const interval& value, int half) {
  if (half != 0 && half != 1)
    throw std::invalid_argument("split half must be 0 or 1");
  const interval middle = midpointInterval(value);
  return half == 0 ? interval(value.leftBound(), middle.rightBound())
                   : interval(middle.leftBound(), value.rightBound());
}

int index(const char* text, int upperExclusive, const char* name) {
  std::size_t used = 0;
  const std::string input(text);
  const int value = std::stoi(input, &used);
  if (used != input.size() || value < 0 || value >= upperExclusive)
    throw std::invalid_argument(std::string(name) + " index is outside [0," +
                                std::to_string(upperExclusive) + ")");
  return value;
}

interval rationalCell(int lowerNumerator, int upperNumerator,
                      int denominator) {
  const interval lo = interval(lowerNumerator) / interval(denominator);
  const interval hi = interval(upperNumerator) / interval(denominator);
  return interval(lo.leftBound(), hi.rightBound());
}

std::array<interval, 3> parameterCell(int rLeafIndex, int a2Index,
                                      int epsilonIndex) {
  // The frozen 8 x 128 x 4 comparison bridge is refined uniformly by eight
  // only in r for this source-to-face shooting kernel.  Hence the exact leaf
  // cover is 64 x 128 x 4 and does not change the atlas bridge topology.
  return {
    rationalCell(rLeafIndex, rLeafIndex + 1, 3200),
    rationalCell(a2Index - 64, a2Index - 63, 256),
    rationalCell(epsilonIndex + 8, epsilonIndex + 9, 10)};
}

interval fixedTargetPhase(const std::string& kind) {
  if (kind == "DIRECT_ALG") {
    const interval anchor =
      cell("5.7566913947049203", "5.7566913967948983");
    const interval radius = interval(9.) / interval(80000000.);
    return anchor + interval(-radius.rightBound(), radius.rightBound());
  }
  if (kind == "DIRECT_POLE_CENTER") {
    const interval lo = interval(103993) / interval(16551);
    const interval hi = interval(208696) / interval(33215);
    const interval radius = interval(9.) / interval(800000.);
    return interval(lo.leftBound(), hi.rightBound())
      + interval(-radius.rightBound(), radius.rightBound());
  }
  throw std::invalid_argument(
    "target kind must be DIRECT_ALG or DIRECT_POLE_CENTER; these are "
    "direct P2bK phases, not transported P2d phases");
}

interval absoluteEnvelope(const interval& x) {
  return interval(0., std::max(std::abs(x.leftBound()),
                               std::abs(x.rightBound())));
}

interval integerPower(interval value, int exponent) {
  interval result(1.);
  for (int index = 0; index < exponent; ++index) result *= value;
  return result;
}

int fallingFactorial(int exponent, int derivatives) {
  int result = 1;
  for (int index = 0; index < derivatives; ++index)
    result *= exponent - index;
  return result;
}

interval coefficient(const PolynomialTerm& term) {
  interval result = interval(term.numerator, term.numerator)
    / interval(term.denominator, term.denominator);
  if (term.times_sqrt_two) result *= sqrt(interval(2.));
  return result;
}

template <std::size_t Size>
interval polynomial(const PolynomialTerm (&terms)[Size], const interval& x,
                    const interval& y, int dx = 0, int dy = 0) {
  interval result(0.);
  for (const auto& term : terms) {
    if (term.px < dx || term.py < dy) continue;
    result += coefficient(term)
      * interval(static_cast<double>(fallingFactorial(term.px, dx)))
      * interval(static_cast<double>(fallingFactorial(term.py, dy)))
      * integerPower(x, term.px - dx)
      * integerPower(y, term.py - dy);
  }
  return result;
}

std::string intervalString(const interval& value) {
  std::ostringstream output;
  output << std::setprecision(17) << value;
  return output.str();
}

struct Parameters {
  interval r;
  interval a2;
  interval epsilon;
  interval a;
  interval b;
  interval c;
  interval alpha;
  interval beta;
  interval chi;
};

Parameters parameters(const interval& r, const interval& a2,
                      const interval& epsilon) {
  if (epsilon.leftBound() <= 0.)
    throw std::invalid_argument("epsilon must be positive");
  const interval rootEpsilon = sqrt(epsilon);
  const interval r2 = sqr(r);
  const interval r4 = sqr(r2);
  const interval a = interval(1.) + rootEpsilon * r2 * r * a2;
  const interval b = rootEpsilon * r2 / interval(3.);
  const interval c = interval(2.) * r * a2
    + rootEpsilon * r4 * sqr(a2);
  if (c.leftBound() <= -2. || c.rightBound() >= 2.)
    throw std::invalid_argument("parameter box leaves the saddle-focus wedge");
  const interval alpha = interval(.5) * sqrt(interval(2.) + c);
  const interval beta = interval(.5) * sqrt(interval(2.) - c);
  const interval chi = atan(
    (interval(1.) / sqrt(interval(2.)) - alpha) / beta);
  return {r, a2, epsilon, a, b, c, alpha, beta, chi};
}

void katoPolarField(Node, Node in[], int, Node out[], int,
                    Node parameter[], int) {
  const Node r = parameter[0] + in[4];
  const Node a2 = parameter[1] + in[5];
  const Node epsilon = parameter[2] + in[6];
  const Node rootEpsilon = sqrt(epsilon);
  const Node r2 = r * r;
  const Node r4 = r2 * r2;
  const Node a = 1 + rootEpsilon * r2 * r * a2;
  const Node b = rootEpsilon * r2 / 3;
  const Node c = 2 * r * a2 + rootEpsilon * r4 * a2 * a2;
  const Node alpha = .5 * sqrt(2 + c);
  const Node beta = .5 * sqrt(2 - c);
  const Node y = (1 / sqrt(Node(2.)) - alpha) / beta;
  const Node cosChi = 1 / sqrt(1 + y * y);
  const Node sinChi = y * cosChi;
  // The expanding pair is represented by (ell,theta), with rho=exp(ell)
  // and theta the unwrapped transported Kato phase.  Polar coordinates keep
  // radial and phase parameter variations separated during the long flight.
  const Node rho = exp(in[0]);
  const Node cosTheta = cos(in[1]);
  const Node sinTheta = sin(in[1]);
  const Node v1 = rho * cosTheta;
  const Node v2 = rho * sinTheta;
  // Rotate only the expanding pair back to the algebraic graph coordinates.
  const Node u1 = cosChi * v1 - sinChi * v2;
  const Node u2 = sinChi * v1 + cosChi * v2;
  const Node U = u1 + in[2];
  const Node nonlinear = -a * U * U + b * U * U * U;
  const Node du1 = alpha * u1 - beta * u2
    + nonlinear / (4 * alpha);
  const Node du2 = beta * u1 + alpha * u2
    - nonlinear / (4 * beta);
  const Node dv1 = cosChi * du1 + sinChi * du2;
  const Node dv2 = -sinChi * du1 + cosChi * du2;
  const Node radialVelocity = cosTheta * dv1 + sinTheta * dv2;
  out[0] = radialVelocity / rho;
  out[1] = (-sinTheta * dv1 + cosTheta * dv2) / rho;
  out[2] = -alpha * in[2] + beta * in[3]
    - nonlinear / (4 * alpha);
  out[3] = -beta * in[2] - alpha * in[3]
    + nonlinear / (4 * beta);
  out[4] = Node(0.);
  out[5] = Node(0.);
  out[6] = Node(0.);
}

struct AffineInitialData {
  IVector centre;
  IMatrix coordinates;
  IVector radii;
  IVector remainder;
  interval thetaRange;
};

AffineInitialData initialData(
    const std::array<interval, 3>& parameterCell,
    const std::array<interval, 3>& parameterCentre,
    const interval& theta0, const std::array<interval, 3>& thetaSlopes,
    const interval& delta) {
  std::array<interval, 3> eta;
  interval thetaRange = theta0 + delta;
  for (int parameter = 0; parameter < 3; ++parameter) {
    eta[parameter] = parameterCell[parameter] - parameterCentre[parameter];
    thetaRange += thetaSlopes[parameter] * eta[parameter];
  }
  IVector centre(7), radii(7), remainder(7);
  IMatrix coordinates(7, 7);
  for (int row = 0; row < 7; ++row) {
    centre[row] = interval(0.);
    radii[row] = interval(0.);
    remainder[row] = interval(0.);
    for (int column = 0; column < 7; ++column)
      coordinates[row][column] = interval(0.);
  }
  centre[0] = log(innerRadius());
  centre[1] = theta0;
  for (int parameter = 0; parameter < 3; ++parameter) {
    coordinates[1][parameter] = thetaSlopes[parameter];
    coordinates[4 + parameter][parameter] = interval(1.);
    radii[parameter] = eta[parameter];
  }
  coordinates[1][3] = interval(1.);
  radii[3] = delta;
  coordinates[2][4] = interval(1.);
  coordinates[3][5] = interval(1.);
  // Complete the Lohner coordinate frame with a zero-radius log-radial
  // column.  The represented source is six-dimensional, but the set
  // implementation requires a nonsingular ambient 7-by-7 matrix.
  coordinates[0][6] = interval(1.);
  const interval graphRadius = sqr(innerRadius()) / interval(4.);
  radii[4] = interval(-graphRadius.rightBound(), graphRadius.rightBound());
  radii[5] = radii[4];
  return {centre, coordinates, radii, remainder, thetaRange};
}

IVector initialPhaseTangent(const interval&, bool includeGraphTangent) {
  IVector result(7);
  result[0] = interval(0.);
  result[1] = interval(1.);
  // P2a proves ||DH_mu||<=1 on the whole local block.  Along the inner
  // circle, ||du/dtheta||=R_i, so each stable-coordinate derivative is
  // enclosed by [-R_i,R_i].
  const interval graphDerivative = includeGraphTangent
    ? innerRadius()
    : interval(0.);
  result[2] = interval(-graphDerivative.rightBound(),
                       graphDerivative.rightBound());
  result[3] = result[2];
  result[4] = interval(0.);
  result[5] = interval(0.);
  result[6] = interval(0.);
  return result;
}

struct MapResult {
  IVector sourceHull;
  IVector endpoint;
  interval returnTime;
  interval sectionResidualBox;
  interval radius;
  interval radialSectionResidual;
  interval rootResidual;
  IVector rootStateDerivative;
  interval geometricPhaseDerivative;
  interval graphPhaseDerivative;
};

IVector affineHull(const AffineInitialData& data) {
  return data.centre + data.coordinates * data.radii + data.remainder;
}

MapResult propagate(IMap& field, const AffineInitialData& data,
                    const interval& targetPhase) {
  IOdeSolver solver(field, 20);
  solver.setAbsoluteTolerance(1.e-14);
  solver.setRelativeTolerance(1.e-14);
  solver.setMaxStep(.02);
  const interval pi(
    "3.141592653589793238462643383279502884",
    "3.141592653589793238462643383279502885");
  const interval targetUnwrapped = targetPhase + interval(2.) * pi;
  const interval targetLogRadius = log(outerRadius());
  INonlinearSection section(
    "par:TARGET;var:ell,theta,s1,s2,er,ea,ee;fun:ell-TARGET;");
  section.setParameter("TARGET", targetLogRadius);
  IPoincareMap map(solver, section, poincare::MinusPlus);
  map.setMaxReturnTime(25.);
  C1HORect2Set set(
    data.centre, data.coordinates, data.radii, data.remainder);
  IMatrix flowDerivative(7, 7);
  interval returnTime;
  const IVector endpoint = map(set, flowDerivative, returnTime, 1);
  const IMatrix derivative = map.computeDP(
    endpoint, flowDerivative, returnTime);
  // The Poincare map itself selects the first outward physical-radius hit.
  // Newton then solves coincidence of that first hit with the fixed terminal
  // phase.  This ordering rules out the spurious "leave and return" branch
  // that a phase-section/radius-root formulation would permit.
  const interval rootResidual = endpoint[1] - targetUnwrapped;
  IVector rootStateDerivative(7);
  for (int column = 0; column < 7; ++column)
    rootStateDerivative[column] = derivative[1][column];
  const interval geometricPhaseDerivative = rootStateDerivative
    * initialPhaseTangent(data.thetaRange, false);
  const interval graphPhaseDerivative = rootStateDerivative
    * initialPhaseTangent(data.thetaRange, true);
  const interval sectionResidualBox = endpoint[0] - targetLogRadius;
  const interval radius = exp(endpoint[0]);
  const interval radialSectionResidual = radius - outerRadius();
  return {affineHull(data), endpoint, returnTime, sectionResidualBox,
          radius, radialSectionResidual, rootResidual, rootStateDerivative,
          geometricPhaseDerivative,
          graphPhaseDerivative};
}

bool strictInterior(const interval& inner, const interval& outer) {
  return outer.leftBound() < inner.leftBound()
    && inner.rightBound() < outer.rightBound();
}

int run(int rLeafIndex, int a2Index, int epsilonIndex,
        const std::array<interval, 3>& parameterCell,
        const interval& theta0,
        const std::array<interval, 3>& thetaSlopes,
        const interval& delta, const interval& targetPhase,
        const std::string& targetKind, const std::string& splitPath) {
  if (!delta.contains(0.))
    throw std::invalid_argument("the Newton correction box must contain zero");
  std::array<interval, 3> centre;
  for (int parameter = 0; parameter < 3; ++parameter)
    centre[parameter] = interval(midpoint(parameterCell[parameter]));
  const Parameters p = parameters(
    parameterCell[0], parameterCell[1], parameterCell[2]);
  // The flow state uses Kato-rotated expanding coordinates, so targetPhase
  // itself defines the cross residual.  Log the corresponding algebraic
  // angle only as a convention audit.
  const interval targetAlgebraicPhase = targetPhase + p.chi;
  const interval pi(
    "3.141592653589793238462643383279502884",
    "3.141592653589793238462643383279502885");
  const interval targetUnwrapped = targetPhase + interval(2.) * pi;
  IMap field(katoPolarField, 7, 7, 3);
  field.setParameter(0, centre[0]);
  field.setParameter(1, centre[1]);
  field.setParameter(2, centre[2]);

  const AffineInitialData pointData = initialData(
    centre, centre, theta0, thetaSlopes, interval(0.));
  const AffineInitialData fullData = initialData(
    parameterCell, centre, theta0, thetaSlopes, delta);
  const MapResult pointMap = propagate(field, pointData, targetPhase);
  const MapResult fullMap = propagate(field, fullData, targetPhase);
  interval predictorResidual = pointMap.rootResidual;
  for (int parameter = 0; parameter < 3; ++parameter) {
    const interval eta = parameterCell[parameter] - centre[parameter];
    const interval composedParameterDerivative =
      fullMap.rootStateDerivative[4 + parameter]
      + thetaSlopes[parameter] * fullMap.geometricPhaseDerivative;
    predictorResidual += composedParameterDerivative * eta;
  }
  const bool derivativeSeparated =
    !fullMap.graphPhaseDerivative.contains(0.);
  interval newton(-std::numeric_limits<double>::max(),
                  std::numeric_limits<double>::max());
  if (derivativeSeparated)
    newton = -predictorResidual / fullMap.graphPhaseDerivative;
  const bool newtonIncluded = derivativeSeparated
    && strictInterior(newton, delta);
  const interval newtonCentre(midpoint(newton));
  const interval newtonRemainder = newton - newtonCentre;
  const AffineInitialData rootData = initialData(
    parameterCell, centre, theta0 + newtonCentre, thetaSlopes,
    newtonRemainder);
  const MapResult rootMap = propagate(field, rootData, targetPhase);
  const interval outerAngle = targetPhase + p.chi;
  const interval outerU1 = outerRadius() * cos(outerAngle);
  const interval outerU2 = outerRadius() * sin(outerAngle);
  const interval h10S1 = polynomial(kH1Terms, outerU1, outerU2);
  const interval rootEta = rootMap.endpoint[2] - h10S1;
  const interval provedEtaRadius = interval(1.) / interval(200000.);
  const interval provedEta(-provedEtaRadius.rightBound(),
                            provedEtaRadius.rightBound());
  const bool rootConditioned = newtonIncluded
    && rootMap.rootResidual.contains(0.)
    && rootMap.sectionResidualBox.contains(0.)
    && rootMap.returnTime.leftBound() > 0.
    && subset(rootEta, provedEta);
  const interval rho = outerRadius();
  const interval graphAtRho = sqr(rho) / interval(4.);
  const interval absoluteU = rho + graphAtRho;
  // On the local Wu graph, |U|<=q(rho):=rho+rho^2/4.  Both
  // q(rho)^2/rho and q(rho)^3/rho increase for rho>0, so evaluation at the
  // outer radius bounds the polar correction along the whole first passage.
  const interval nonlinearUpper = absoluteEnvelope(p.a) * sqr(absoluteU)
    + absoluteEnvelope(p.b) * power(absoluteU, 3);
  const interval polarCorrection = nonlinearUpper
    * sqrt(interval(1.) / sqr(p.alpha)
           + interval(1.) / sqr(p.beta))
    / (interval(4.) * rho);
  const interval radialLogRate = p.alpha - polarCorrection;
  const interval phaseRate = p.beta - polarCorrection;
  const bool startBelowTarget =
    fullMap.sourceHull[1].rightBound() < targetUnwrapped.leftBound();
  const bool localWuMonotonicity = radialLogRate.leftBound() > 0.
    && phaseRate.leftBound() > 0.;
  const bool correctBranch = startBelowTarget && localWuMonotonicity
    && pointMap.returnTime.leftBound() > 10.
    && fullMap.returnTime.leftBound() > 10.
    && pointMap.returnTime.rightBound() < 16.
    && fullMap.returnTime.rightBound() < 16.;
  const bool returnResolved = pointMap.returnTime.leftBound() > 0.
    && fullMap.returnTime.leftBound() > 0.
    && pointMap.returnTime.rightBound() < 25.
    && fullMap.returnTime.rightBound() < 25.;
  const interval sourceRadius = exp(fullMap.sourceHull[0]);
  const bool sourceStrictlyInsidePhysicalFace =
    sourceRadius.rightBound() < outerRadius().leftBound();
  const bool radialSectionEnclosed =
    pointMap.sectionResidualBox.contains(0.)
    && fullMap.sectionResidualBox.contains(0.);
  // The pinned CAPD Poincare map returns the first positive crossing of the
  // declared section.  The actual graph orbit starts strictly inside it, and
  // the local-Wu rate bound is positive until that crossing.  Consequently
  // this is the unique first outward radius hit; Newton imposes its phase.
  const bool radialFirstHitResolved = sourceStrictlyInsidePhysicalFace
    && radialLogRate.leftBound() > 0. && radialSectionEnclosed
    && returnResolved;
  const bool success = derivativeSeparated && newtonIncluded && correctBranch
    && radialFirstHitResolved && returnResolved && rootConditioned;

  std::cout << std::setprecision(17)
    << "scope P2bK_direct_source_first_radius_hit_design_scout\n"
    << "evidence COMPUTED_INTERVAL_DESIGN_NONCLAIM\n"
    << "grid r_leaf_index " << rLeafIndex << " of_64 a2_index "
       << a2Index << " of_128 epsilon_index " << epsilonIndex
       << " of_4 r_refinement_factor 8\n"
    << "parameters " << p.r << " " << p.a2 << " " << p.epsilon << "\n"
    << "theta_affine " << theta0 << " slopes " << thetaSlopes[0] << " "
       << thetaSlopes[1] << " " << thetaSlopes[2]
       << " delta " << delta << " fixed_target_kind " << targetKind
       << " target_kato_phase " << targetPhase
       << " target_algebraic_phase " << targetAlgebraicPhase << "\n"
    << "source_full " << fullMap.sourceHull << "\n"
    << "endpoint_point_predictor " << pointMap.endpoint << "\n"
    << "endpoint_full_delta " << fullMap.endpoint << "\n"
    << "return_time_point_predictor " << pointMap.returnTime
       << " full_delta " << fullMap.returnTime << "\n"
    << "local_wu_log_radial_rate_lower " << radialLogRate
       << " local_wu_phase_rate_lower " << phaseRate << "\n"
    << "source_below_unwrapped_target "
       << (startBelowTarget ? "PASS" : "INCONCLUSIVE") << "\n"
    << "source_strictly_inside_physical_face "
       << (sourceStrictlyInsidePhysicalFace ? "PASS" : "INCONCLUSIVE")
       << "\n"
    << "radial_section_enclosed "
       << (radialSectionEnclosed ? "PASS" : "INCONCLUSIVE") << "\n"
    << "log_radius_section_residual_box_full "
       << fullMap.sectionResidualBox << "\n"
    << "radius_full " << fullMap.radius
       << " radial_section_residual_full "
       << fullMap.radialSectionResidual << "\n"
    << "first_radius_hit_phase_residual_point_predictor "
       << pointMap.rootResidual
       << " direct_full_box " << fullMap.rootResidual
       << " mean_value_predictor " << predictorResidual << "\n"
    << "first_hit_phase_geometric_source_derivative "
       << fullMap.geometricPhaseDerivative << "\n"
    << "first_hit_phase_graph_source_derivative "
       << fullMap.graphPhaseDerivative << "\n"
    << "interval_newton " << newton << " inside_delta "
       << (newtonIncluded ? "PASS" : "INCONCLUSIVE") << "\n"
    << "root_conditioned_endpoint " << rootMap.endpoint << "\n"
    << "root_conditioned_return_time " << rootMap.returnTime << "\n"
    << "root_conditioned_phase_residual " << rootMap.rootResidual << "\n"
    << "root_conditioned_eta " << rootEta << " inside_P2b0_tube "
       << (subset(rootEta, provedEta) ? "PASS" : "INCONCLUSIVE") << "\n"
    << "phase_derivative_separated " << (derivativeSeparated ? "PASS" : "INCONCLUSIVE") << "\n"
    << "RESULT_JSON {\"status\":\""
       << (success ? "PASS" : "INCONCLUSIVE")
       << "\",\"scope\":\"P2E_DIRECT_SOURCE_ROOT_CONDITIONED_LEAF\""
       << ",\"claim_bearing\":false"
       << ",\"target_kind\":\"" << targetKind << "\""
       << ",\"leaf\":[" << rLeafIndex << ',' << a2Index << ','
       << epsilonIndex << ']'
       << ",\"split_path\":\"" << splitPath << "\""
       << ",\"parameter_box\":{\"r\":" << intervalString(p.r)
       << ",\"a2\":" << intervalString(p.a2)
       << ",\"epsilon\":" << intervalString(p.epsilon) << "}"
       << ",\"target_phase\":" << intervalString(targetPhase)
       << ",\"theta0\":" << intervalString(theta0)
       << ",\"theta_parameter_slopes\":["
       << intervalString(thetaSlopes[0]) << ','
       << intervalString(thetaSlopes[1]) << ','
       << intervalString(thetaSlopes[2]) << ']'
       << ",\"trial_delta\":" << intervalString(delta)
       << ",\"interval_newton\":" << intervalString(newton)
       << ",\"phase_derivative\":"
       << intervalString(fullMap.graphPhaseDerivative)
       << ",\"log_radial_rate\":" << intervalString(radialLogRate)
       << ",\"phase_rate\":" << intervalString(phaseRate)
       << ",\"root_eta\":" << intervalString(rootEta)
       << ",\"root_stable_coordinates\":["
       << intervalString(rootMap.endpoint[2]) << ','
       << intervalString(rootMap.endpoint[3]) << ']'
       << ",\"root_return_time\":"
       << intervalString(rootMap.returnTime)
       << ",\"root_phase_residual\":"
       << intervalString(rootMap.rootResidual)
       << ",\"nonclaim\":\"One root-conditioned source leaf does not "
          "prove a terminal first hit or the P2e event atlas.\"}\n"
    << (success ? "PASS" : "INCONCLUSIVE")
    << " source trace design scout\n";
  return success ? 0 : 20;
}

}  // namespace

int main(int argc, char** argv) {
  try {
    if (argc < 10 || (argc - 10) % 2 != 0)
      throw std::invalid_argument(
        "usage: r_leaf_index a2_index epsilon_index theta0 "
        "theta_r theta_a2 theta_epsilon delta_radius target_kind "
        "[r|a2|epsilon split_half]...");
    const int rLeafIndex = index(argv[1], 64, "r leaf");
    const int a2Index = index(argv[2], 128, "a2");
    const int epsilonIndex = index(argv[3], 4, "epsilon");
    const std::array<interval, 3> parentBox = parameterCell(
      rLeafIndex, a2Index, epsilonIndex);
    std::array<interval, 3> cellBox = parentBox;
    const std::array<interval, 3> thetaSlopes = {
      point(argv[5]), point(argv[6]), point(argv[7])};
    std::string splitPath;
    for (int argument = 10; argument < argc; argument += 2) {
      const std::string variable(argv[argument]);
      const int half = index(argv[argument + 1], 2, "split half");
      int coordinate = -1;
      if (variable == "r") coordinate = 0;
      else if (variable == "a2") coordinate = 1;
      else if (variable == "epsilon") coordinate = 2;
      else
        throw std::invalid_argument(
          "source split variable must be r, a2, or epsilon");
      cellBox[coordinate] = halfInterval(cellBox[coordinate], half);
      if (!splitPath.empty()) splitPath += ",";
      splitPath += variable + ":" + std::to_string(half);
    }
    interval shiftedTheta0 = point(argv[4]);
    for (int parameter = 0; parameter < 3; ++parameter) {
      shiftedTheta0 += thetaSlopes[parameter]
        * (midpointInterval(cellBox[parameter])
           - midpointInterval(parentBox[parameter]));
    }
    const interval deltaRadius = point(argv[8]);
    if (deltaRadius.leftBound() <= 0.)
      throw std::invalid_argument("delta radius must be positive");
    const interval delta(-deltaRadius.rightBound(), deltaRadius.rightBound());
    const std::string targetKind(argv[9]);
    return run(rLeafIndex, a2Index, epsilonIndex, cellBox, shiftedTheta0,
               thetaSlopes, delta, fixedTargetPhase(targetKind), targetKind,
               splitPath);
  } catch (const std::exception& error) {
    std::cerr << "FAIL: " << error.what() << "\n";
    return 10;
  }
}
