#include <algorithm>
#include <array>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <stdexcept>
#include <string>
#include <vector>

#include "capd/capdlib.h"
#include "../rigorous/include/rounding_self_test.hpp"

// A target-specific CAPD validator for the A2 periodic profile.
//
// This program proves only two facts at
//
//     r = 2/25, a2 = 0, epsilon = 1:
//
// (i)  a reversible zero-energy orbit leaves Fix(R), meets Fix(R) again near
//      the saved A2 seed, and hence gives a true periodic stationary profile;
// (ii) along its half orbit,
//
//        z' = (1/100) u^2 - r^2 u^3 + (2/3) r^4 u^4
//
//      has z(T) < -1/10.
//
// The second inequality is the only numerical input needed by the
// self-adjoint-pencil proof of a real co-periodic temporal eigenvalue
// lambda > 1/100.  There is deliberately no Fourier truncation, Evans
// function, generic certificate schema, or independent-replay layer here.

using namespace capd;

namespace {

constexpr int kStateDimension = 4;
constexpr int kNodeCount = 13;
constexpr int kUnknownDimension = 1 + kStateDimension * kNodeCount;
constexpr double kSeed = 4.925566666129073;
constexpr double kSeedRadius = 2.0e-12;
constexpr double kNodeRadius = 1.0e-7;

// The nodes are endpoint-free centres at central times 1,...,13.  They are
// merely Newton centres.  Every proof operation below starts from an interval
// box and is performed by CAPD/FILIB with outward rounding.
constexpr std::array<std::array<double, kStateDimension>, kNodeCount>
    kNodeCentres{{
        {{0.6602257113848915, -4.1869987744304922,
          -6.0712215679518797, 3.115423504525447}},
        {{-1.1932986733576723, -0.29080195149726745,
          -3.104921612390382, 2.5218629730386195}},
        {{-1.0147939018161147, 0.40452658545876419,
          -1.1791311230441985, 1.3634391643160122}},
        {{-0.59729287888499893, 0.39067278832157221,
          -0.25296583650910548, 0.55912359751959806}},
        {{-0.26863911160474041, 0.26096405630952169,
          0.067707790241991611, 0.13709187171172763}},
        {{-0.075011610645078816, 0.13072111173322024,
          0.10824329380823264, -0.023824084913696666}},
        {{0.0067095713940848855, 0.041061966164773339,
          0.064343606257526151, -0.050494776685342579}},
        {{0.023336319221248476, -0.00075891757164644926,
          0.021763294359795977, -0.032012472511288248}},
        {{0.015853574332528628, -0.010648974388193072,
          0.00059939153009408138, -0.011621616302267134}},
        {{0.0061895985017906769, -0.0077665547806307573,
          -0.0048262975949929093, -0.00085543563922560982}},
        {{0.00076992024705107231, -0.0032727489886485561,
          -0.0036813153893886195, 0.0022455627250698956}},
        {{-0.0010460136549160512, -0.00073404064230804587,
          -0.0014620888931006347, 0.0018965186054668221}},
        {{-0.0013177955878688802, -0.000026593082041131573,
          -0.00016428958232302213, 0.00065740548873081158}},
    }};

double midpoint(const interval& value) {
  return value.mid().leftBound();
}

double absoluteUpper(const interval& value) {
  return std::max(std::abs(value.leftBound()),
                  std::abs(value.rightBound()));
}

bool strictInterior(const interval& inner, const interval& outer) {
  return outer.leftBound() < inner.leftBound() &&
         inner.rightBound() < outer.rightBound();
}

bool liesStrictlyInsideExactBox(const interval& value,
                                const interval& exactLower,
                                const interval& exactUpper) {
  // exactLower and exactUpper enclose the corresponding exact decimal
  // endpoints.  Comparing against their inward-facing endpoints makes this
  // a proof of containment in the exact decimal box, not just in a rounded
  // double approximation to that box.
  return exactLower.rightBound() < value.leftBound() &&
         value.rightBound() < exactUpper.leftBound();
}

double infinityNormUpper(const IMatrix& matrix) {
  double result = 0.0;
  for (unsigned int row = 0; row < matrix.numberOfRows(); ++row) {
    interval rowSum(0.0);
    for (unsigned int column = 0; column < matrix.numberOfColumns();
         ++column) {
      rowSum += matrix[row][column].abs();
    }
    result = std::max(result, rowSum.rightBound());
  }
  return result;
}

IVector pointVector(const std::array<double, kStateDimension>& centre) {
  IVector result(kStateDimension);
  for (int j = 0; j < kStateDimension; ++j) {
    result[j] = interval(centre[static_cast<std::size_t>(j)]);
  }
  return result;
}

IVector nodeBox(int node) {
  IVector result(kStateDimension);
  for (int j = 0; j < kStateDimension; ++j) {
    const double centre =
        kNodeCentres[static_cast<std::size_t>(node)]
                    [static_cast<std::size_t>(j)];
    result[j] = interval(centre - kNodeRadius, centre + kNodeRadius);
  }
  return result;
}

interval exactR() {
  return interval(2.0) / interval(25.0);
}

interval zeroEnergyV(const interval& u) {
  const interval r2 = sqr(exactR());
  return -sqr(u) / interval(3.0) + r2 * u * sqr(u) / interval(12.0);
}

interval zeroEnergyVDerivative(const interval& u) {
  const interval r2 = sqr(exactR());
  return -interval(2.0) * u / interval(3.0) +
         r2 * sqr(u) / interval(4.0);
}

IVector initialState(const interval& seed) {
  IVector result(kStateDimension);
  result[0] = seed;
  result[1] = interval(0.0);
  result[2] = zeroEnergyV(seed);
  result[3] = interval(0.0);
  return result;
}

IVector initialDerivative(const interval& seed) {
  IVector result(kStateDimension);
  result[0] = interval(1.0);
  result[1] = interval(0.0);
  result[2] = zeroEnergyVDerivative(seed);
  result[3] = interval(0.0);
  return result;
}

IMap stateField() {
  IMap field("par:r2;var:u,p,v,q;"
             "fun:p,-v-u*u+r2*u*u*u/3,q,u;");
  field.setParameter("r2", sqr(exactR()));
  return field;
}

IMap augmentedField() {
  IMap field(
      "par:r2,lambda;var:u,p,v,q,z;"
      "fun:p,-v-u*u+r2*u*u*u/3,q,u,"
      "lambda*u*u-r2*u*u*u+2*r2*r2*u*u*u*u/3;");
  field.setParameter("r2", sqr(exactR()));
  field.setParameter("lambda", interval(1.0) / interval(100.0));
  return field;
}

void configure(IOdeSolver& solver) {
  solver.setAbsoluteTolerance(1.0e-13);
  solver.setRelativeTolerance(1.0e-13);
  solver.setMaxStep(0.05);
}

std::pair<IVector, IMatrix> timeOneC1(IOdeSolver& solver,
                                      const IVector& initial) {
  ITimeMap map(solver);
  C1HORect2Set set(initial);
  const IVector endpoint = map(interval(1.0), set);
  return {endpoint, static_cast<IMatrix>(set)};
}

IVector timeOneC0(IOdeSolver& solver, const IVector& initial) {
  ITimeMap map(solver);
  C0HOTripletonSet set(initial);
  return map(interval(1.0), set);
}

struct PoincareData {
  IVector endpoint;
  IMatrix derivative;
  interval flightTime;
};

PoincareData finalPoincare(IOdeSolver& solver, const IVector& initial) {
  ICoordinateSection section(kStateDimension, 3);
  IPoincareMap map(solver, section, poincare::PlusMinus);
  C1HORect2Set set(initial);
  IMatrix flowDerivative(kStateDimension, kStateDimension);
  interval flightTime;
  const IVector endpoint = map(set, flowDerivative, flightTime);
  const IMatrix derivative =
      map.computeDP(endpoint, flowDerivative, flightTime);
  return {endpoint, derivative, flightTime};
}

IMatrix midpointInverse(const IMatrix& matrix) {
  const int dimension = matrix.numberOfRows();
  DMatrix centre(dimension, dimension);
  for (int i = 0; i < dimension; ++i) {
    for (int j = 0; j < dimension; ++j) {
      centre[i][j] = midpoint(matrix[i][j]);
    }
  }
  const DMatrix inverse = matrixAlgorithms::inverseMatrix(centre);
  IMatrix result(dimension, dimension);
  for (int i = 0; i < dimension; ++i) {
    for (int j = 0; j < dimension; ++j) {
      result[i][j] = interval(inverse[i][j]);
    }
  }
  return result;
}

double variableScale(int column) {
  return column == 0 ? kSeedRadius : kNodeRadius;
}

IVector normalizedUnitBox() {
  IVector result(kUnknownDimension);
  for (int i = 0; i < kUnknownDimension; ++i) {
    result[i] = interval(-1.0, 1.0);
  }
  return result;
}

// Residual at the floating Newton centre.  The result is nevertheless an
// interval enclosure because every flow and Poincare map is evaluated by
// CAPD from degenerate interval initial data.
IVector centreResidual(IOdeSolver& solver) {
  IVector result(kUnknownDimension);

  const IVector firstFlow =
      timeOneC0(solver, initialState(interval(kSeed)));
  const IVector firstNode = pointVector(kNodeCentres[0]);
  for (int j = 0; j < kStateDimension; ++j) {
    result[j] = firstNode[j] - firstFlow[j];
  }

  for (int node = 1; node < kNodeCount; ++node) {
    const IVector flow =
        timeOneC0(solver, pointVector(kNodeCentres[node - 1]));
    const IVector target = pointVector(kNodeCentres[node]);
    const int row = kStateDimension * node;
    for (int j = 0; j < kStateDimension; ++j) {
      result[row + j] = target[j] - flow[j];
    }
  }

  const PoincareData final =
      finalPoincare(solver, pointVector(kNodeCentres[kNodeCount - 1]));
  result[kUnknownDimension - 1] = final.endpoint[1];
  return result;
}

// Interval Jacobian with respect to normalized correction variables.  The
// physical seed correction is 2e-12*x[0], and every physical node correction
// is 1e-7*x[j].
IMatrix residualDerivative(IOdeSolver& solver) {
  IMatrix derivative(kUnknownDimension, kUnknownDimension);
  for (int i = 0; i < kUnknownDimension; ++i) {
    for (int j = 0; j < kUnknownDimension; ++j) {
      derivative[i][j] = interval(0.0);
    }
  }

  const interval seed(kSeed - kSeedRadius, kSeed + kSeedRadius);
  const auto first = timeOneC1(solver, initialState(seed));
  const IVector seedDerivative = initialDerivative(seed);
  const IVector firstColumn = first.second * seedDerivative;
  for (int row = 0; row < kStateDimension; ++row) {
    derivative[row][0] = -firstColumn[row] * interval(kSeedRadius);
    derivative[row][1 + row] = interval(kNodeRadius);
  }

  for (int node = 1; node < kNodeCount; ++node) {
    const auto flow = timeOneC1(solver, nodeBox(node - 1));
    const int rowBase = kStateDimension * node;
    const int previousBase = 1 + kStateDimension * (node - 1);
    const int currentBase = 1 + kStateDimension * node;
    for (int row = 0; row < kStateDimension; ++row) {
      derivative[rowBase + row][currentBase + row] =
          interval(kNodeRadius);
      for (int column = 0; column < kStateDimension; ++column) {
        derivative[rowBase + row][previousBase + column] =
            -flow.second[row][column] * interval(kNodeRadius);
      }
    }
  }

  const PoincareData final = finalPoincare(solver, nodeBox(kNodeCount - 1));
  const int lastBase = 1 + kStateDimension * (kNodeCount - 1);
  for (int column = 0; column < kStateDimension; ++column) {
    derivative[kUnknownDimension - 1][lastBase + column] =
        final.derivative[1][column] * interval(kNodeRadius);
  }
  return derivative;
}

struct KrawczykResult {
  bool passed;
  bool inclusionPassed;
  bool contractionPassed;
  IVector image;
  IVector rootBox;
  double maximumImageRadius;
  double contractionInfinityNormUpper;
  int worstComponent;
};

KrawczykResult validateRoot(IOdeSolver& solver) {
  const IVector residual = centreResidual(solver);
  const IMatrix derivative = residualDerivative(solver);
  const IMatrix inverse = midpointInverse(derivative);
  const IVector unit = normalizedUnitBox();

  IMatrix identity(kUnknownDimension, kUnknownDimension);
  for (int i = 0; i < kUnknownDimension; ++i) {
    for (int j = 0; j < kUnknownDimension; ++j) {
      identity[i][j] = interval(i == j ? 1.0 : 0.0);
    }
  }
  const IMatrix defect = identity - inverse * derivative;
  const IVector image = -inverse * residual + defect * unit;

  bool inclusionPassed = true;
  double maximumRadius = 0.0;
  int worstComponent = -1;
  IVector rootBox(kUnknownDimension);
  for (int i = 0; i < kUnknownDimension; ++i) {
    inclusionPassed = inclusionPassed && strictInterior(image[i], unit[i]);
    const double radius = absoluteUpper(image[i]);
    if (radius > maximumRadius) {
      maximumRadius = radius;
      worstComponent = i;
    }
    const double scale = variableScale(i);
    if (i == 0) {
      rootBox[i] = interval(kSeed) + interval(scale) * image[i];
    } else {
      const int flat = i - 1;
      const int node = flat / kStateDimension;
      const int component = flat % kStateDimension;
      rootBox[i] =
          interval(kNodeCentres[static_cast<std::size_t>(node)]
                               [static_cast<std::size_t>(component)]) +
          interval(scale) * image[i];
    }
  }
  const double contractionBound = infinityNormUpper(defect);
  const bool contractionPassed = contractionBound < 1.0;
  return {inclusionPassed && contractionPassed,
          inclusionPassed,
          contractionPassed,
          image,
          rootBox,
          maximumRadius,
          contractionBound,
          worstComponent};
}

IVector augmentedInitial(const IVector& state) {
  IVector result(5);
  for (int j = 0; j < kStateDimension; ++j) {
    result[j] = state[j];
  }
  result[4] = interval(0.0);
  return result;
}

interval fixedSegmentMoment(IOdeSolver& solver, const IVector& state) {
  ITimeMap map(solver);
  C0HOTripletonSet set(augmentedInitial(state));
  const IVector endpoint = map(interval(1.0), set);
  return endpoint[4];
}

struct FinalSegmentResult {
  interval moment;
  interval flightTime;
  interval finalU;
};

FinalSegmentResult finalSegmentMoment(IOdeSolver& solver,
                                      const IVector& state) {
  ICoordinateSection section(5, 3);
  IPoincareMap map(solver, section, poincare::PlusMinus);
  C0HOTripletonSet set(augmentedInitial(state));
  interval flightTime;
  const IVector endpoint = map(set, flightTime);
  return {endpoint[4], flightTime, endpoint[0]};
}

struct MomentResult {
  interval halfMoment;
  interval finalFlightTime;
  interval halfPeriod;
  interval physicalPeriod;
  interval physicalMoment;
  interval lastNodeQ;
  interval finalU;
};

MomentResult validateMoment(const KrawczykResult& root) {
  IMap field = augmentedField();
  IOdeSolver solver(field, 30);
  configure(solver);

  interval halfMoment(0.0);
  halfMoment += fixedSegmentMoment(solver, initialState(root.rootBox[0]));
  for (int node = 0; node < kNodeCount - 1; ++node) {
    IVector state(kStateDimension);
    const int base = 1 + kStateDimension * node;
    for (int j = 0; j < kStateDimension; ++j) {
      state[j] = root.rootBox[base + j];
    }
    halfMoment += fixedSegmentMoment(solver, state);
  }

  IVector last(kStateDimension);
  const int lastBase = 1 + kStateDimension * (kNodeCount - 1);
  for (int j = 0; j < kStateDimension; ++j) {
    last[j] = root.rootBox[lastBase + j];
  }
  const auto final = finalSegmentMoment(solver, last);
  halfMoment += final.moment;
  const interval halfPeriod = interval(13.0) + final.flightTime;
  const interval physicalPeriod = interval(2.0) * exactR() * halfPeriod;
  const interval physicalMoment =
      interval(2.0) * power(exactR(), 5) * halfMoment;
  return {halfMoment, final.flightTime, halfPeriod, physicalPeriod,
          physicalMoment, last[3], final.finalU};
}

void printInterval(const interval& value) {
  std::cout << rfsn::rigorous::intervalJson(value);
}

}  // namespace

int main() {
  try {
    const auto roundingReport = rfsn::rigorous::runRoundingSelfTests();
    if (roundingReport.status != rfsn::rigorous::Verdict::Pass) {
      std::cout << "{\n";
      std::cout << "  \"schema\":\"rfsn-vdp-a2-periodic-capd/1\",\n";
      std::cout << "  \"rounding_self_test\":"
                << rfsn::rigorous::roundingReportJson(roundingReport)
                << ",\n";
      std::cout << "  \"mathematical_status\":\"INCONCLUSIVE\"\n";
      std::cout << "}\n";
      return 1;
    }

    IMap field = stateField();
    IOdeSolver solver(field, 30);
    configure(solver);
    const KrawczykResult root = validateRoot(solver);

    std::cout << "{\n";
    std::cout << "  \"schema\":\"rfsn-vdp-a2-periodic-capd/1\",\n";
    std::cout << "  \"rounding_self_test\":"
              << rfsn::rigorous::roundingReportJson(roundingReport) << ",\n";
    std::cout << "  \"krawczyk_max_normalized_radius\":"
              << std::setprecision(17) << root.maximumImageRadius << ",\n";
    std::cout << "  \"krawczyk_defect_infinity_norm_upper\":"
              << std::setprecision(17)
              << root.contractionInfinityNormUpper << ",\n";
    std::cout << "  \"krawczyk_defect_infinity_norm_upper_hex\":\""
              << rfsn::rigorous::hexDouble(
                     root.contractionInfinityNormUpper)
              << "\",\n";
    std::cout << "  \"krawczyk_inclusion_status\":\""
              << (root.inclusionPassed ? "PASS" : "FAIL") << "\",\n";
    std::cout << "  \"krawczyk_contraction_status\":\""
              << (root.contractionPassed ? "PASS" : "FAIL") << "\",\n";
    std::cout << "  \"krawczyk_worst_component\":"
              << root.worstComponent << ",\n";
    std::cout << "  \"krawczyk_worst_interval\":";
    printInterval(root.image[root.worstComponent]);
    std::cout << ",\n";
    std::cout << "  \"root_status\":\""
              << (root.passed ? "PASS" : "FAIL") << "\",\n";

    if (!root.passed) {
      std::cout << "  \"mathematical_status\":\"INCONCLUSIVE\"\n";
      std::cout << "}\n";
      return 2;
    }

    const MomentResult moment = validateMoment(root);
    const interval seedLower =
        rfsn::rigorous::exactRational("492556665", "100000000");
    const interval seedUpper =
        rfsn::rigorous::exactRational("492556669", "100000000");
    const interval halfPeriodLower =
        rfsn::rigorous::exactRational("1349788", "100000");
    const interval halfPeriodUpper =
        rfsn::rigorous::exactRational("1349789", "100000");
    const interval halfMomentGate =
        rfsn::rigorous::exactRational("-1", "10");
    const interval physicalMomentGate =
        rfsn::rigorous::exactRational("-5", "10000000");

    const bool seedPreselectionPassed = liesStrictlyInsideExactBox(
        root.rootBox[0], seedLower, seedUpper);
    const bool halfPeriodPreselectionPassed = liesStrictlyInsideExactBox(
        moment.halfPeriod, halfPeriodLower, halfPeriodUpper);
    const bool lastNodeQPassed = moment.lastNodeQ.leftBound() > 0.0;
    const bool finalUPassed = moment.finalU.rightBound() < 0.0;
    const bool halfMomentPassed =
        moment.halfMoment.rightBound() < halfMomentGate.leftBound();
    const bool physicalMomentPassed =
        moment.physicalMoment.rightBound() < physicalMomentGate.leftBound();
    const bool geometricPassed = seedPreselectionPassed &&
        halfPeriodPreselectionPassed && lastNodeQPassed && finalUPassed;
    const bool mathematicalPassed =
        geometricPassed && halfMomentPassed && physicalMomentPassed;
    std::cout << "  \"seed_root_box\":";
    printInterval(root.rootBox[0]);
    std::cout << ",\n  \"final_flight_time\":";
    printInterval(moment.finalFlightTime);
    std::cout << ",\n  \"central_half_period\":";
    printInterval(moment.halfPeriod);
    std::cout << ",\n  \"physical_period\":";
    printInterval(moment.physicalPeriod);
    std::cout << ",\n  \"half_moment_z\":";
    printInterval(moment.halfMoment);
    std::cout << ",\n  \"physical_moment_M_0.01\":";
    printInterval(moment.physicalMoment);
    std::cout << ",\n  \"last_node_q\":";
    printInterval(moment.lastNodeQ);
    std::cout << ",\n  \"final_section_u\":";
    printInterval(moment.finalU);
    std::cout << ",\n  \"moment_gate\":-0.1,\n";
    std::cout << "  \"physical_moment_gate\":-5e-7,\n";
    std::cout << "  \"seed_preselection_status\":\""
              << (seedPreselectionPassed ? "PASS" : "FAIL") << "\",\n";
    std::cout << "  \"half_period_preselection_status\":\""
              << (halfPeriodPreselectionPassed ? "PASS" : "FAIL")
              << "\",\n";
    std::cout << "  \"last_node_q_positive_status\":\""
              << (lastNodeQPassed ? "PASS" : "FAIL") << "\",\n";
    std::cout << "  \"final_section_u_negative_status\":\""
              << (finalUPassed ? "PASS" : "FAIL") << "\",\n";
    std::cout << "  \"moment_status\":\""
              << (halfMomentPassed ? "PASS" : "FAIL") << "\",\n";
    std::cout << "  \"physical_moment_status\":\""
              << (physicalMomentPassed ? "PASS" : "FAIL") << "\",\n";
    std::cout << "  \"uniqueness_scope\":"
              << "\"the hard-coded lifted outer box X; K(X) is the smaller root enclosure used for the moment bound\",\n";
    std::cout << "  \"spectral_consequence\":\""
              << (mathematicalPassed
                      ? "self-adjoint pencil gives a real co-periodic eigenvalue lambda>0.01"
                      : "not established")
              << "\",\n";
    std::cout << "  \"mathematical_status\":\""
              << (mathematicalPassed ? "PASS" : "INCONCLUSIVE") << "\"\n";
    std::cout << "}\n";
    return mathematicalPassed ? 0 : 3;
  } catch (const std::exception& error) {
    std::cerr << "A2 CAPD validator failed: " << error.what() << "\n";
    return 1;
  }
}
