#include <algorithm>
#include <cmath>
#include <iomanip>
#include <iostream>
#include <stdexcept>

#include "../rigorous/include/rounding_self_test.hpp"

// Reuse the already-audited P2c shooting implementation rather than create a
// second homoclinic solver.  Renaming its command-line entry point leaves its
// internal interval objects available in this translation unit.  A release
// record must therefore bind both this file and the included P2c source.
#define main p2c_archived_command_line_main
#include "../rigorous/design/p2c_homoclinic_multishoot_scout.cpp"
#undef main

namespace {

constexpr int kPhysicalDimension = 4;

interval targetR() {
  return interval(2.0) / interval(25.0);
}

IMap pulseMomentField() {
  IMap field(
      "par:r2,lambda;var:U,P,V,Q,z;"
      "fun:P,-V-U*U+r2*U*U*U/3,Q,U,"
      "lambda*U*U-r2*U*U*U+2*r2*r2*U*U*U*U/3;");
  field.setParameter("r2", sqr(targetR()));
  field.setParameter("lambda", interval(1.0) / interval(100.0));
  return field;
}

void configurePulseSolver(IOdeSolver& solver) {
  solver.setAbsoluteTolerance(1.0e-13);
  solver.setRelativeTolerance(1.0e-13);
  solver.setMaxStep(0.05);
}

IVector physicalHull(const AffineInitialData& data) {
  C0HOTripletonSet set(
      data.centre, data.coordinates, data.radii, data.remainder);
  const IVector full = set;
  IVector physical(kPhysicalDimension);
  for (int component = 0; component < kPhysicalDimension; ++component) {
    physical[component] = full[component];
  }
  return physical;
}

IVector augmentedInitial(const IVector& physical) {
  IVector result(5);
  for (int component = 0; component < kPhysicalDimension; ++component) {
    result[component] = physical[component];
  }
  result[4] = interval(0.0);
  return result;
}

interval fixedSegmentMoment(IOdeSolver& solver, const IVector& physical,
                            const interval& duration) {
  ITimeMap map(solver);
  C0HOTripletonSet set(augmentedInitial(physical));
  const IVector endpoint = map(duration, set);
  return endpoint[4];
}

struct EventMoment {
  interval moment;
  interval flightTime;
  interval centreU;
  interval centreP;
  interval centreV;
  interval centreQ;
};

EventMoment finalEventMoment(IOdeSolver& solver, const IVector& physical) {
  ICoordinateSection section(5, 3);
  IPoincareMap map(solver, section, poincare::MinusPlus);
  C0HOTripletonSet set(augmentedInitial(physical));
  interval flightTime;
  const IVector endpoint = map(set, flightTime);
  return {endpoint[4], flightTime, endpoint[0], endpoint[1], endpoint[2],
          endpoint[3]};
}

struct CompactMoment {
  interval value;
  interval finalFlightTime;
  interval halfTime;
  interval centreU;
  interval centreP;
  interval centreV;
  interval centreQ;
};

CompactMoment compactSourceToCentreMoment(const MuAffineCellResult& root) {
  IMap field = pulseMomentField();
  IOdeSolver solver(field, 30);
  configurePulseSolver(solver);

  interval moment(0.0);
  moment += fixedSegmentMoment(
      solver, physicalHull(muRootSourceData(root)), interval(kNodeTimes[0]));
  for (int node = 0; node + 1 < kSegments; ++node) {
    moment += fixedSegmentMoment(
        solver, physicalHull(muRootNodeData(root, node)),
        interval(kNodeTimes[node + 1] - kNodeTimes[node]));
  }
  const EventMoment event = finalEventMoment(
      solver, physicalHull(muRootNodeData(root, kSegments - 1)));
  moment += event.moment;
  return {moment, event.flightTime,
          interval(kNodeTimes.back()) + event.flightTime,
          event.centreU, event.centreP, event.centreV, event.centreQ};
}

// P2c proves, for the selected centred homoclinic, the stronger imported
// bounds
//
//   |Gamma(xi)| <= 1.081619 exp(-|xi|/5),  |xi| >= T_h,
//   T_h > 9.605.
//
// We deliberately round these to the simple rational constants C=541/500
// and T0=48/5.  Bounding each monomial by its absolute value gives a rigorous
// upper bound for the unintegrated half-tail.
interval importedHalfTailUpperBound() {
  const interval C = interval(541.0) / interval(500.0);
  const interval eta = interval(1.0) / interval(5.0);
  const interval T0 = interval(48.0) / interval(5.0);
  const interval r2 = sqr(targetR());
  const interval lambda = interval(1.0) / interval(100.0);

  interval bound(0.0);
  bound += lambda * sqr(C) * exp(-interval(2.0) * eta * T0) /
           (interval(2.0) * eta);
  bound += r2 * power(C, 3) * exp(-interval(3.0) * eta * T0) /
           (interval(3.0) * eta);
  bound += interval(2.0) * sqr(r2) * power(C, 4) *
           exp(-interval(4.0) * eta * T0) /
           (interval(3.0) * interval(4.0) * eta);
  return interval(0.0, bound.rightBound());
}

void printInterval(const interval& value) {
  std::cout << rfsn::rigorous::intervalJson(value);
}

bool strictlyInsideExactBox(const interval& value, const interval& lower,
                            const interval& upper) {
  return lower.rightBound() < value.leftBound() &&
         value.rightBound() < upper.leftBound();
}

}  // namespace

int main() {
  try {
    const auto roundingReport = rfsn::rigorous::runRoundingSelfTests();
    if (roundingReport.status != rfsn::rigorous::Verdict::Pass) {
      std::cout << "{\n"
                << "  \"schema\":\"rfsn-vdp-pulse-1-capd/1\",\n"
                << "  \"rounding_self_test\":"
                << rfsn::rigorous::roundingReportJson(roundingReport)
                << ",\n  \"mathematical_status\":\"INCONCLUSIVE\"\n}\n";
      return 1;
    }

    const MuBox target = {targetR(), interval(0.0), interval(1.0)};
    const auto predictor = muGridPhasePredictor(target);
    const MuAffineCellResult root = buildMuAffineCell(
        1.5, target, predictor.first, predictor.second, false, true);
    // This is the archived P2c grid cell whose r/a2/epsilon corner is the
    // target point.  Containment of the point root in its uniqueness tube
    // identifies the fresh target enclosure with the frozen selected branch.
    const MuAffineCellResult selectedCell =
        buildMuGridCell(3.0, 31, 64, 2);
    const FaceContainmentResult selectedBranchIdentification =
        mapMuFaceEnclosure(root, selectedCell, target);

    std::cout << "{\n"
              << "  \"schema\":\"rfsn-vdp-pulse-1-capd/1\",\n"
              << "  \"rounding_self_test\":"
              << rfsn::rigorous::roundingReportJson(roundingReport) << ",\n"
              << "  \"homoclinic_root_status\":\""
              << (root.success ? "PASS" : "FAIL") << "\",\n"
              << "  \"selected_p2c_grid_cell_status\":\""
              << (selectedCell.success ? "PASS" : "FAIL") << "\",\n"
              << "  \"point_root_to_selected_cell_status\":\""
              << (selectedBranchIdentification.success ? "PASS" : "FAIL")
              << "\",\n"
              << "  \"point_root_to_selected_cell_max_ratio\":"
              << std::setprecision(17)
              << selectedBranchIdentification.maxRatio << ",\n"
              << "  \"krawczyk_max_inclusion_ratio\":"
              << root.maxInclusion << ",\n"
              << "  \"krawczyk_max_contraction_ratio\":"
              << root.maxContraction << ",\n"
              << "  \"shooting_determinant\":";
    printInterval(root.determinant);
    std::cout << ",\n";

    if (!root.success || !selectedCell.success ||
        !selectedBranchIdentification.success) {
      std::cout << "  \"mathematical_status\":\"INCONCLUSIVE\"\n}\n";
      return 2;
    }

    const CompactMoment compact = compactSourceToCentreMoment(root);
    const interval tailUpper = importedHalfTailUpperBound();
    const interval tailEnclosure(
        -tailUpper.rightBound(), tailUpper.rightBound());
    const interval halfMomentEnclosure = compact.value + tailEnclosure;
    const interval physicalMomentEnclosure =
        interval(2.0) * power(targetR(), 5) * halfMomentEnclosure;

    const interval halfGate =
        rfsn::rigorous::exactRational("-13", "100");
    const interval physicalGate =
        rfsn::rigorous::exactRational("-8", "10000000");
    const interval tailGate =
        rfsn::rigorous::exactRational("1", "1000");
    const bool compactPassed =
        compact.value.rightBound() < halfGate.leftBound();
    const bool tailImportPassed =
        tailUpper.rightBound() < tailGate.leftBound();
    const bool halfPassed =
        halfMomentEnclosure.rightBound() < halfGate.leftBound();
    const bool physicalPassed =
        physicalMomentEnclosure.rightBound() < physicalGate.leftBound();
    const bool centrePassed =
        strictlyInsideExactBox(
            compact.halfTime,
            rfsn::rigorous::exactRational("965", "100"),
            rfsn::rigorous::exactRational("966", "100")) &&
        strictlyInsideExactBox(
            compact.centreU,
            rfsn::rigorous::exactRational("492", "100"),
            rfsn::rigorous::exactRational("493", "100")) &&
        strictlyInsideExactBox(
            compact.centreV,
            rfsn::rigorous::exactRational("-804", "100"),
            rfsn::rigorous::exactRational("-800", "100")) &&
        compact.centreP.contains(0.0) && compact.centreQ.contains(0.0);
    const bool mathematicalPassed = compactPassed && tailImportPassed &&
        halfPassed && physicalPassed && centrePassed;

    std::cout << "  \"phase_predictor\":";
    printInterval(predictor.first);
    std::cout << ",\n  \"compact_source_to_centre_moment\":";
    printInterval(compact.value);
    std::cout << ",\n  \"imported_half_tail_upper_bound\":";
    printInterval(tailUpper);
    std::cout << ",\n  \"full_half_moment_enclosure\":";
    printInterval(halfMomentEnclosure);
    std::cout << ",\n  \"physical_full_line_moment_enclosure\":";
    printInterval(physicalMomentEnclosure);
    std::cout << ",\n  \"final_flight_time\":";
    printInterval(compact.finalFlightTime);
    std::cout << ",\n  \"source_to_centre_time\":";
    printInterval(compact.halfTime);
    std::cout << ",\n  \"symmetry_centre_U\":";
    printInterval(compact.centreU);
    std::cout << ",\n  \"symmetry_centre_P\":";
    printInterval(compact.centreP);
    std::cout << ",\n  \"symmetry_centre_V\":";
    printInterval(compact.centreV);
    std::cout << ",\n  \"symmetry_centre_Q\":";
    printInterval(compact.centreQ);
    std::cout << ",\n  \"compact_moment_below_minus_0.13_status\":\""
              << (compactPassed ? "PASS" : "FAIL") << "\",\n"
              << "  \"tail_import_below_0.001_status\":\""
              << (tailImportPassed ? "PASS" : "FAIL") << "\",\n"
              << "  \"half_moment_below_minus_0.13_status\":\""
              << (halfPassed ? "PASS" : "FAIL") << "\",\n"
              << "  \"physical_moment_below_minus_8e-7_status\":\""
              << (physicalPassed ? "PASS" : "FAIL") << "\",\n"
              << "  \"centre_selection_status\":\""
              << (centrePassed ? "PASS" : "FAIL") << "\",\n"
              << "  \"spectral_consequence\":\""
              << (mathematicalPassed
                      ? "self-adjoint whole-line pencil gives a real L2 eigenvalue lambda in (0.01,2)"
                      : "not established")
              << "\",\n"
              << "  \"mathematical_status\":\""
              << (mathematicalPassed ? "PASS" : "INCONCLUSIVE")
              << "\"\n}\n";
    return mathematicalPassed ? 0 : 3;
  } catch (const std::exception& error) {
    std::cerr << "pulse_1 CAPD validator failed: " << error.what() << "\n";
    return 1;
  }
}
