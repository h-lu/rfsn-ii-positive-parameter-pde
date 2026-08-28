#include <algorithm>
#include <array>
#include <cmath>
#include <cstdint>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <limits>
#include <memory>
#include <sstream>
#include <stdexcept>
#include <string>

#include "capd/capdlib.h"

std::unique_ptr<capd::IVector> gCapturedFoldKrawczyk;
std::unique_ptr<capd::IVector> gCapturedFoldBox;

bool captureFoldSubsetInterior(const capd::IVector& K,
                               const capd::IVector& X) {
  gCapturedFoldKrawczyk = std::make_unique<capd::IVector>(K);
  gCapturedFoldBox = std::make_unique<capd::IVector>(X);
  return capd::vectalg::subsetInterior(K, X);
}

#define subsetInterior(K, X) captureFoldSubsetInterior((K), (X))
#define main paperaUpstreamFoldProbeMain
#include "fold_interval_probe.cpp"
#undef main
#undef subsetInterior

using namespace capd;

namespace {

constexpr int kFoldSegments = papera_fold_centres::kSegments;
constexpr int kEventSegments = 36;
constexpr int kDimension = 5;
constexpr double kFoldStep = papera_fold_centres::kFinalTime / kFoldSegments;
constexpr double kSectionE = 0.0575;
constexpr double kHalfWidth = 2e-5;
constexpr double kDeltaLower = 0.003004;
constexpr double kDeltaUpper = 0.003008;

std::string gSeedFile;
std::int64_t gSeedOffset = 0;

struct RuntimeSeed {
  double sourceV = 0.;
  double sourceU = 0.;
  double totalTime = 0.;
  std::array<std::array<double, kDimension>, kEventSegments + 1> centre{};
  std::array<std::array<double, kDimension>, kEventSegments + 1> derivativeV{};
};

RuntimeSeed gSeed;

void parseArguments(int argc, char** argv) {
  for(int i = 1; i < argc; ++i) {
    const std::string argument(argv[i]);
    if(argument == "--seed-file" && i + 1 < argc)
      gSeedFile = argv[++i];
    else if(argument == "--seed-offset" && i + 1 < argc)
      gSeedOffset = std::stoll(argv[++i]);
    else
      throw std::runtime_error("usage: fold_event_flow_bridge_probe --seed-file PATH [--seed-offset N]");
  }
  if(gSeedFile.empty()) throw std::runtime_error("--seed-file is required");
  std::ifstream input(gSeedFile);
  if(!input) throw std::runtime_error("cannot open seed file");
  input.seekg(gSeedOffset);
  input >> gSeed.sourceV >> gSeed.sourceU >> gSeed.totalTime;
  for(int node = 0; node <= kEventSegments; ++node)
    for(int component = 0; component < kDimension; ++component)
      input >> gSeed.centre[node][component];
  for(int node = 0; node <= kEventSegments; ++node)
    for(int component = 0; component < kDimension; ++component)
      input >> gSeed.derivativeV[node][component];
  if(!input) throw std::runtime_error("malformed seed file");
}

IVector foldBaseBox(int node) {
  IVector result(4);
  if(!gCapturedFoldKrawczyk)
    throw std::runtime_error("upstream fold Krawczyk image was not captured");
  for(int component = 0; component < 4; ++component)
    result[component] = (*gCapturedFoldKrawczyk)[8 * node + component];
  return result;
}

double collarRadius(int node, int component) {
  const double x = static_cast<double>(node) / kEventSegments;
  double base = 0.;
  switch(component) {
    case 0: base = 3e-8 + 3e-7 * std::pow(x, 6); break;
    case 1: base = 3e-8 + 2e-6 * std::pow(x, 8); break;
    case 2: base = 3e-8 + 6e-6 * std::pow(x, 5); break;
    case 3: base = 3e-8 + 2e-6 * std::pow(x, 5); break;
    case 4: base = 2e-7; break;
    default: throw std::runtime_error("invalid collar component");
  }
  return base + 1.35 * kHalfWidth
    * std::abs(gSeed.derivativeV[node][component]);
}

interval collarInterval(int node, int component) {
  const double centre = gSeed.centre[node][component];
  const double radius = collarRadius(node, component);
  return interval(centre - radius, centre + radius);
}

IVector flowImage(IMap& field, const IVector& initial,
                  const interval& duration) {
  IOdeSolver solver(field, 25);
  solver.setAbsoluteTolerance(1e-14);
  solver.setRelativeTolerance(1e-14);
  ITimeMap timeMap(solver);
  C0HORect2Set set(initial);
  return timeMap(duration, set);
}

bool negativePOnShortExtension(IMap& field, const IVector& initial,
                               double duration) {
  IOdeSolver solver(field, 25);
  solver.setAbsoluteTolerance(1e-14);
  solver.setRelativeTolerance(1e-14);
  ITimeMap timeMap(solver);
  timeMap.stopAfterStep(true);
  C0HORect2Set set(initial);
  do {
    timeMap(interval(duration), set);
    if(!(set.getLastEnclosure()[1].rightBound() < 0.)) return false;
  } while(!timeMap.completed());
  return true;
}

} // namespace

int main(int argc, char** argv) {
  try {
    parseArguments(argc, argv);
    char upstreamProgram[] = "fold_interval_probe";
    char robustArgument[] = "--robust";
    char* upstreamArguments[] = {upstreamProgram, robustArgument, nullptr};
    std::ostringstream upstreamOutput;
    std::streambuf* savedOutput = std::cout.rdbuf(upstreamOutput.rdbuf());
    const int upstreamReturnCode = paperaUpstreamFoldProbeMain(
      2, upstreamArguments);
    std::cout.rdbuf(savedOutput);
    if(upstreamReturnCode != 0 || !gCapturedFoldKrawczyk)
      throw std::runtime_error("upstream robust fold Krawczyk replay failed");
    IMap field("var:U,P,V,Q;fun:P,-U*U-V,Q,U;");
    IMap backwardField("var:U,P,V,Q;fun:-P,U*U+V,-Q,-U;");
    const IVector terminalFoldBox = foldBaseBox(kFoldSegments);
    const IVector before = flowImage(field, terminalFoldBox,
                                     interval(kDeltaLower));
    const IVector after = flowImage(field, terminalFoldBox,
                                    interval(kDeltaUpper));
    const interval eBefore = -interval(1.) / before[0];
    const interval eAfter = -interval(1.) / after[0];
    if(!(eBefore.leftBound() > kSectionE))
      throw std::runtime_error("lower event-time bracket is not before the event");
    if(!(eAfter.rightBound() < kSectionE))
      throw std::runtime_error("upper event-time bracket is not after the event");
    if(!negativePOnShortExtension(field, terminalFoldBox, kDeltaUpper))
      throw std::runtime_error("P is not strictly negative on the event bracket");

    IOdeSolver poincareSolver(field, 25);
    poincareSolver.setAbsoluteTolerance(1e-14);
    poincareSolver.setRelativeTolerance(1e-14);
    ICoordinateSection eventSection(4, 0, -1. / kSectionE);
    IPoincareMap poincareMap(
      poincareSolver, eventSection, poincare::PlusMinus);
    C0HORect2Set poincareSet(terminalFoldBox);
    interval eventReturnTime;
    const IVector eventImage = poincareMap(poincareSet, eventReturnTime);
    if(!(eventReturnTime.leftBound() > kDeltaLower
         && eventReturnTime.rightBound() < kDeltaUpper))
      throw std::runtime_error("Poincare return time leaves the strict bracket");
    const interval totalTime = interval(papera_fold_centres::kFinalTime)
      + eventReturnTime;
    for(int eventNode = 0; eventNode <= kEventSegments; ++eventNode)
      if(!subsetInterior(totalTime, collarInterval(eventNode, 4)))
        throw std::runtime_error("event-time bracket leaves collar box-0 time tube");

    const interval foldSourceV = foldBaseBox(0)[2];
    const interval collarParameter(
      gSeed.sourceV - kHalfWidth, gSeed.sourceV + kHalfWidth);
    if(!subsetInterior(foldSourceV, collarParameter))
      throw std::runtime_error("fold source V leaves collar box-0 parameter interval");

    double minimumAbsoluteMargin = std::numeric_limits<double>::infinity();
    double maximumRelativeRadius = 0.;
    int worstNode = -1;
    int worstComponent = -1;
    for(int eventNode = 0; eventNode <= kEventSegments; ++eventNode) {
      const interval physicalTime = interval(
        static_cast<double>(eventNode) / kEventSegments) * totalTime;
      const double physicalMidpoint = 0.5 * (
        physicalTime.leftBound() + physicalTime.rightBound());
      int foldNode = static_cast<int>(std::floor(
        physicalMidpoint / kFoldStep));
      foldNode = std::max(0, std::min(kFoldSegments, foldNode));
      interval duration = physicalTime - interval(kFoldStep * foldNode);
      IVector image(4);
      if(eventNode == kEventSegments)
        image = eventImage;
      else if(duration.rightBound() <= 0.)
        image = flowImage(backwardField, foldBaseBox(foldNode), -duration);
      else
        image = flowImage(field, foldBaseBox(foldNode), duration);
      for(int component = 0; component < 4; ++component) {
        const interval collar = collarInterval(eventNode, component);
        if(!subsetInterior(image[component], collar)) {
          std::cerr << std::setprecision(17)
            << "containment failure event_node=" << eventNode
            << " fold_node=" << foldNode
            << " component=" << component
            << " duration=" << duration
            << " image=" << image[component]
            << " collar=" << collar << "\n";
          throw std::runtime_error("propagated fold box leaves collar box-0 tube");
        }
        const double margin = std::min(
          image[component].leftBound() - collar.leftBound(),
          collar.rightBound() - image[component].rightBound());
        const double collarRadiusValue = collarRadius(eventNode, component);
        const double imageRadius = 0.5 * (
          image[component].rightBound() - image[component].leftBound());
        const double relative = imageRadius / collarRadiusValue;
        if(relative > maximumRelativeRadius) {
          maximumRelativeRadius = relative;
          worstNode = eventNode;
          worstComponent = component;
        }
        minimumAbsoluteMargin = std::min(minimumAbsoluteMargin, margin);
      }
    }

    const interval foldTangentV(
      (*gCapturedFoldKrawczyk)[6]);
    const interval foldSlope = interval(1.) / foldTangentV;

    std::cout << std::setprecision(17)
      << "{\n"
      << "  \"status\": \"PASS-FOLD-BOX-FLOW-CONTAINMENT-IN-COLLAR-BOX0\",\n"
      << "  \"upstream_robust_fold_krawczyk_replayed\": true,\n"
      << "  \"fold_box_input\": \"upstream robust Krawczyk image\",\n"
      << "  \"event_delta_bracket\": \"[" << kDeltaLower << ", "
      << kDeltaUpper << "]\",\n"
      << "  \"poincare_return_time\": \"" << eventReturnTime << "\",\n"
      << "  \"event_total_time_bracket\": \"" << totalTime << "\",\n"
      << "  \"event_e_at_lower_delta\": \"" << eBefore << "\",\n"
      << "  \"event_e_at_upper_delta\": \"" << eAfter << "\",\n"
      << "  \"strict_negative_P_on_event_bracket\": true,\n"
      << "  \"first_event_after_T15\": true,\n"
      << "  \"collar_nodes_contained\": " << kEventSegments + 1 << ",\n"
      << "  \"collar_components_per_node\": 5,\n"
      << "  \"strict_flow_containment_in_box0\": true,\n"
      << "  \"strict_time_containment_in_box0\": true,\n"
      << "  \"fold_source_V\": \"" << foldSourceV << "\",\n"
      << "  \"collar_box0_V_parameter\": \"" << collarParameter << "\",\n"
      << "  \"fold_V_strictly_inside_collar_parameter\": true,\n"
      << "  \"minimum_absolute_containment_margin\": "
      << minimumAbsoluteMargin << ",\n"
      << "  \"maximum_image_radius_over_collar_radius\": "
      << maximumRelativeRadius << ",\n"
      << "  \"worst_node\": " << worstNode << ",\n"
      << "  \"worst_component\": " << worstComponent << ",\n"
      << "  \"fold_source_dU_dV_enclosure\": \"" << foldSlope << "\"\n"
      << "}\n";
    return 0;
  } catch(const std::exception& error) {
    std::cerr << "FAIL: " << error.what() << "\n";
    return 12;
  }
}
