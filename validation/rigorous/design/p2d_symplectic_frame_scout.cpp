// Design-only interval scout for the P2d reversible symplectic frame.
//
// This program is deliberately outside validation/rigorous/src. Its JSON
// output is a gate-design aid, not a certificate and not evidence for an
// exact identity. Exact symplectic, inverse, and reverser identities remain
// the responsibility of audit_p2d_exact_chart.py.

// Reuse the small, already exercised Jet2 interval-algebra kernel without
// changing the historical P2bK scout. Renaming its entry point keeps this a
// single self-contained design translation unit.
#if defined(__GNUC__)
#pragma GCC diagnostic push
#pragma GCC diagnostic ignored "-Wreturn-type"
#endif
#define main p2b_kato_scout_unused_entry_point
#include "p2b_kato_scout.cpp"
#undef main
#if defined(__GNUC__)
#pragma GCC diagnostic pop
#endif

#include <cstddef>
#include <string>

namespace {

template <std::size_t Rows, std::size_t Columns>
using JetMatrix = std::array<std::array<Jet2, Columns>, Rows>;

template <std::size_t Rows, std::size_t Inner, std::size_t Columns>
JetMatrix<Rows, Columns> multiply(
    const JetMatrix<Rows, Inner>& left,
    const JetMatrix<Inner, Columns>& right) {
  JetMatrix<Rows, Columns> result{};
  for (std::size_t row = 0; row < Rows; ++row) {
    for (std::size_t column = 0; column < Columns; ++column) {
      for (std::size_t inner = 0; inner < Inner; ++inner)
        result[row][column] =
            result[row][column] + left[row][inner] * right[inner][column];
    }
  }
  return result;
}

template <std::size_t Rows, std::size_t Columns>
JetMatrix<Columns, Rows> transpose(
    const JetMatrix<Rows, Columns>& value) {
  JetMatrix<Columns, Rows> result{};
  for (std::size_t row = 0; row < Rows; ++row)
    for (std::size_t column = 0; column < Columns; ++column)
      result[column][row] = value[row][column];
  return result;
}

template <std::size_t Rows, std::size_t Columns>
JetMatrix<Rows, Columns> subtract(
    const JetMatrix<Rows, Columns>& left,
    const JetMatrix<Rows, Columns>& right) {
  JetMatrix<Rows, Columns> result{};
  for (std::size_t row = 0; row < Rows; ++row)
    for (std::size_t column = 0; column < Columns; ++column)
      result[row][column] = left[row][column] - right[row][column];
  return result;
}

template <std::size_t Rows, std::size_t Columns>
std::vector<Jet2> flatten(const JetMatrix<Rows, Columns>& value) {
  std::vector<Jet2> result;
  result.reserve(Rows * Columns);
  for (const auto& row : value)
    for (const auto& entry : row) result.push_back(entry);
  return result;
}

Jet2 originalParameterJet(const Jet2& normalized) {
  // theta_r=25r-1, theta_a=4a_2, theta_epsilon=5(epsilon-1).
  const std::array<Interval, kParameterDimension> scale{
      Interval(25.0), Interval(4.0), Interval(5.0)};
  Jet2 result(normalized.value);
  for (int i = 0; i < kParameterDimension; ++i) {
    result.gradient[i] = scale[i] * normalized.gradient[i];
    for (int j = 0; j < kParameterDimension; ++j)
      result.hessian[i][j] =
          scale[i] * scale[j] * normalized.hessian[i][j];
  }
  return result;
}

std::vector<Jet2> originalParameterJets(
    const std::vector<Jet2>& normalized) {
  std::vector<Jet2> result;
  result.reserve(normalized.size());
  for (const auto& entry : normalized)
    result.push_back(originalParameterJet(entry));
  return result;
}

struct ScalarSummary {
  bool initialized{false};
  Interval range{0.0};
  Bounds normalized;
  Bounds original;

  void update(const Jet2& value) {
    range = initialized ? hull(range, value.value) : value.value;
    initialized = true;
    maximize(normalized, jetBounds({value}));
    maximize(original, jetBounds({originalParameterJet(value)}));
  }
};

struct MatrixSummary {
  explicit MatrixSummary(std::size_t rowsIn, std::size_t columnsIn)
      : rows(rowsIn), columns(columnsIn) {}

  std::size_t rows;
  std::size_t columns;
  bool initialized{false};
  std::vector<Interval> entryRanges;
  Bounds normalized;
  Bounds original;

  void update(const std::vector<Jet2>& entries) {
    if (entries.size() != rows * columns)
      throw std::logic_error("matrix summary dimension mismatch");
    if (!initialized) {
      entryRanges.reserve(entries.size());
      for (const auto& entry : entries) entryRanges.push_back(entry.value);
      initialized = true;
    } else {
      for (std::size_t index = 0; index < entries.size(); ++index)
        entryRanges[index] = hull(entryRanges[index], entries[index].value);
    }
    maximize(normalized, jetBounds(entries));
    maximize(original, jetBounds(originalParameterJets(entries)));
  }
};

struct FrameData {
  Jet2 alpha;
  Jet2 beta;
  Jet2 normalizerSquared;
  Jet2 y;
  Jet2 d;
  Jet2 e;
  Jet2 kappa;
  Jet2 kappaPlusD;
  Jet2 halfDenominator;
  Jet2 cosineHalf;
  Jet2 sineHalf;
  Jet2 theta;
  Jet2 radialScale;
  JetMatrix<2, 2> halfRotation;
  JetMatrix<2, 2> crossPairing;
  JetMatrix<4, 2> expanding;
  JetMatrix<4, 2> stable;
  JetMatrix<4, 4> completion;
  JetMatrix<4, 4> inverse;
};

FrameData buildFrame(const Jet2& c) {
  const Jet2 zero(Interval(0.0));
  const Jet2 one(Interval(1.0));
  const Jet2 rootTwo = squareRoot(Jet2(Interval(2.0)));
  FrameData result;
  result.alpha = Interval(0.5) *
                 squareRoot(Jet2(Interval(2.0)) + c);
  result.beta = Interval(0.5) *
                squareRoot(Jet2(Interval(2.0)) - c);
  result.normalizerSquared =
      Interval(6.0) * result.alpha * result.alpha
      - Interval(4.0) * rootTwo * result.alpha
      + Jet2(Interval(3.0));
  const Jet2 normalizer = squareRoot(result.normalizerSquared);
  result.y = (reciprocal(rootTwo) - result.alpha) / result.beta;

  JetMatrix<4, 2> algebraic{{
      {{one, zero}},
      {{result.alpha, -result.beta}},
      {{c / Jet2(Interval(2.0)),
        Interval(2.0) * result.alpha * result.beta}},
      {{result.alpha, result.beta}},
  }};
  JetMatrix<2, 2> katoChange{{
      {{one / normalizer, -result.y / normalizer}},
      {{result.y / normalizer, one / normalizer}},
  }};
  const JetMatrix<4, 2> kato = multiply(algebraic, katoChange);

  result.d = Interval(2.0) * result.alpha / result.normalizerSquared;
  result.e = Interval(2.0) * result.alpha
      * (Interval(3.0) * result.alpha - Interval(2.0) * rootTwo)
      / (result.normalizerSquared * result.beta);
  result.kappa = Interval(4.0) * result.alpha * result.beta
      * (one + result.y * result.y) / result.normalizerSquared;
  result.kappaPlusD = result.kappa + result.d;
  result.halfDenominator = squareRoot(
      Interval(2.0) * result.kappa * result.kappaPlusD);
  result.cosineHalf = result.kappaPlusD / result.halfDenominator;
  result.sineHalf = result.e / result.halfDenominator;
  result.theta = arctangent(result.sineHalf / result.cosineHalf);
  result.radialScale = reciprocal(squareRoot(result.kappa));
  result.halfRotation = {{
      {{result.cosineHalf, -result.sineHalf}},
      {{result.sineHalf, result.cosineHalf}},
  }};
  result.crossPairing = {{
      {{result.d, result.e}},
      {{result.e, -result.d}},
  }};

  result.expanding = multiply(kato, result.halfRotation);
  for (auto& row : result.expanding)
    for (auto& entry : row) entry = result.radialScale * entry;

  const std::array<Interval, 4> reverserDiagonal{
      Interval(1.0), Interval(-1.0), Interval(1.0), Interval(-1.0)};
  const std::array<Interval, 2> cZeroDiagonal{
      Interval(1.0), Interval(-1.0)};
  for (std::size_t row = 0; row < 4; ++row) {
    for (std::size_t column = 0; column < 2; ++column) {
      result.stable[row][column] = reverserDiagonal[row]
          * cZeroDiagonal[column] * result.expanding[row][column];
      result.completion[row][column] = result.stable[row][column];
      result.completion[row][column + 2] = result.expanding[row][column];
    }
  }

  JetMatrix<4, 4> omega{};
  omega[0][1] = Jet2(Interval(-1.0));
  omega[1][0] = one;
  omega[2][3] = one;
  omega[3][2] = Jet2(Interval(-1.0));
  JetMatrix<4, 4> minusOmegaZero{};
  minusOmegaZero[0][2] = one;
  minusOmegaZero[1][3] = one;
  minusOmegaZero[2][0] = Jet2(Interval(-1.0));
  minusOmegaZero[3][1] = Jet2(Interval(-1.0));
  result.inverse = multiply(
      multiply(minusOmegaZero, transpose(result.completion)), omega);
  return result;
}

double upper(const Interval& value) { return value.rightBound(); }

double maxAbs(const Interval& value) {
  return std::max(std::abs(value.leftBound()),
                  std::abs(value.rightBound()));
}

void printIntervalArray(const Interval& value) {
  std::cout << '[' << value.leftBound() << ',' << value.rightBound() << ']';
}

void printBoundsObject(const Bounds& value) {
  std::cout << "{\"order0\":" << upper(value.order0)
            << ",\"order1_hs\":" << upper(value.order1)
            << ",\"order2_hs\":" << upper(value.order2) << '}';
}

void printScalarSummary(const ScalarSummary& value) {
  std::cout << "{\"range\":";
  printIntervalArray(value.range);
  std::cout << ",\"normalized\":";
  printBoundsObject(value.normalized);
  std::cout << ",\"original\":";
  printBoundsObject(value.original);
  std::cout << '}';
}

void printMatrixSummary(const MatrixSummary& value) {
  std::cout << "{\"entry_hulls\":[";
  for (std::size_t row = 0; row < value.rows; ++row) {
    if (row != 0) std::cout << ',';
    std::cout << '[';
    for (std::size_t column = 0; column < value.columns; ++column) {
      if (column != 0) std::cout << ',';
      printIntervalArray(value.entryRanges[row * value.columns + column]);
    }
    std::cout << ']';
  }
  std::cout << "],\"normalized\":";
  printBoundsObject(value.normalized);
  std::cout << ",\"original\":";
  printBoundsObject(value.original);
  std::cout << '}';
}

void printGate(const char* name, const char* proposedGate,
               double observed, bool passes, bool& first) {
  if (!first) std::cout << ',';
  first = false;
  std::cout << "{\"name\":\"" << name
            << "\",\"proposed_gate\":\"" << proposedGate
            << "\",\"observed_worst\":" << observed
            << ",\"passes\":" << (passes ? "true" : "false") << '}';
}

}  // namespace

int main() {
  const std::array<int, 3> subdivisions{16, 8, 4};
  const FrameData anchor = buildFrame(Jet2(Interval(0.0)));

  ScalarSummary cSummary, alphaSummary, betaSummary;
  ScalarSummary normalizerSquaredSummary, ySummary, dSummary, eSummary;
  ScalarSummary kappaSummary, kappaPlusDSummary, halfDenominatorSummary;
  ScalarSummary cosineHalfSummary, sineHalfSummary, thetaSummary;
  ScalarSummary radialScaleSummary;
  MatrixSummary expandingSummary(4, 2), stableSummary(4, 2);
  MatrixSummary completionSummary(4, 4), inverseSummary(4, 4);

  double halfAngleUnitResidual = 0.0;
  double diagonalizationResidual = 0.0;
  double symplecticResidual = 0.0;
  double inverseLeftResidual = 0.0;
  double inverseRightResidual = 0.0;
  double reverserResidual = 0.0;
  double anchorDeviation = 0.0;

  const Jet2 one(Interval(1.0));
  JetMatrix<4, 4> omega{};
  omega[0][1] = Jet2(Interval(-1.0));
  omega[1][0] = one;
  omega[2][3] = one;
  omega[3][2] = Jet2(Interval(-1.0));
  JetMatrix<4, 4> omegaZero{};
  omegaZero[0][2] = Jet2(Interval(-1.0));
  omegaZero[1][3] = Jet2(Interval(-1.0));
  omegaZero[2][0] = one;
  omegaZero[3][1] = one;
  JetMatrix<4, 4> identity{};
  for (std::size_t index = 0; index < 4; ++index)
    identity[index][index] = one;
  JetMatrix<4, 4> physicalReverser{};
  physicalReverser[0][0] = one;
  physicalReverser[1][1] = Jet2(Interval(-1.0));
  physicalReverser[2][2] = one;
  physicalReverser[3][3] = Jet2(Interval(-1.0));
  JetMatrix<4, 4> standardReverser{};
  standardReverser[0][2] = one;
  standardReverser[1][3] = Jet2(Interval(-1.0));
  standardReverser[2][0] = one;
  standardReverser[3][1] = Jet2(Interval(-1.0));

  for (int ir = 0; ir < subdivisions[0]; ++ir) {
    for (int ia = 0; ia < subdivisions[1]; ++ia) {
      for (int ie = 0; ie < subdivisions[2]; ++ie) {
        const Jet2 thetaR = Jet2::variable(
            normalizedCell(ir, subdivisions[0]), 0);
        const Jet2 thetaA = Jet2::variable(
            normalizedCell(ia, subdivisions[1]), 1);
        const Jet2 thetaEpsilon = Jet2::variable(
            normalizedCell(ie, subdivisions[2]), 2);
        const Jet2 r = (thetaR + one) / Jet2(Interval(25.0));
        const Jet2 a2 = thetaA / Jet2(Interval(4.0));
        const Jet2 epsilon = one
            + thetaEpsilon / Jet2(Interval(5.0));
        const Jet2 r2 = r * r;
        const Jet2 r4 = r2 * r2;
        const Jet2 c = Interval(2.0) * r * a2
            + squareRoot(epsilon) * r4 * a2 * a2;
        const FrameData frame = buildFrame(c);

        cSummary.update(c);
        alphaSummary.update(frame.alpha);
        betaSummary.update(frame.beta);
        normalizerSquaredSummary.update(frame.normalizerSquared);
        ySummary.update(frame.y);
        dSummary.update(frame.d);
        eSummary.update(frame.e);
        kappaSummary.update(frame.kappa);
        kappaPlusDSummary.update(frame.kappaPlusD);
        halfDenominatorSummary.update(frame.halfDenominator);
        cosineHalfSummary.update(frame.cosineHalf);
        sineHalfSummary.update(frame.sineHalf);
        thetaSummary.update(frame.theta);
        radialScaleSummary.update(frame.radialScale);
        expandingSummary.update(flatten(frame.expanding));
        stableSummary.update(flatten(frame.stable));
        completionSummary.update(flatten(frame.completion));
        inverseSummary.update(flatten(frame.inverse));

        const Jet2 unitResidual = frame.cosineHalf * frame.cosineHalf
            + frame.sineHalf * frame.sineHalf - one;
        halfAngleUnitResidual = std::max(
            halfAngleUnitResidual, maxAbs(unitResidual.value));

        JetMatrix<2, 2> expectedDiagonal{};
        expectedDiagonal[0][0] = frame.kappa;
        expectedDiagonal[1][1] = -frame.kappa;
        const auto diagonalResidual = subtract(
            multiply(multiply(transpose(frame.halfRotation),
                              frame.crossPairing),
                     frame.halfRotation),
            expectedDiagonal);
        diagonalizationResidual = std::max(
            diagonalizationResidual,
            upper(jetBounds(flatten(diagonalResidual)).order0));

        const auto symplecticMatrixResidual = subtract(
            multiply(multiply(transpose(frame.completion), omega),
                     frame.completion),
            omegaZero);
        symplecticResidual = std::max(
            symplecticResidual,
            upper(jetBounds(flatten(symplecticMatrixResidual)).order0));
        const auto inverseLeft = subtract(
            multiply(frame.inverse, frame.completion), identity);
        const auto inverseRight = subtract(
            multiply(frame.completion, frame.inverse), identity);
        inverseLeftResidual = std::max(
            inverseLeftResidual,
            upper(jetBounds(flatten(inverseLeft)).order0));
        inverseRightResidual = std::max(
            inverseRightResidual,
            upper(jetBounds(flatten(inverseRight)).order0));
        const auto reverserMatrixResidual = subtract(
            multiply(physicalReverser, frame.completion),
            multiply(frame.completion, standardReverser));
        reverserResidual = std::max(
            reverserResidual,
            upper(jetBounds(flatten(reverserMatrixResidual)).order0));
        anchorDeviation = std::max(
            anchorDeviation,
            upper(jetBounds(flatten(subtract(
                frame.completion, anchor.completion))).order0));
      }
    }
  }

  const double completionNormUpper = 1.0 + anchorDeviation;
  const double completionSmallestLower = 1.0 - anchorDeviation;
  const double inverseNormUpper = 1.0 / completionSmallestLower;
  const double normalizedCompletionD1 =
      upper(completionSummary.normalized.order1);
  const double normalizedCompletionD2 =
      upper(completionSummary.normalized.order2);
  const double normalizedInverseD1 = upper(inverseSummary.normalized.order1);
  const double normalizedInverseD2 = upper(inverseSummary.normalized.order2);
  const double originalCompletionD1 = upper(completionSummary.original.order1);
  const double originalCompletionD2 = upper(completionSummary.original.order2);
  const double originalInverseD1 = upper(inverseSummary.original.order1);
  const double originalInverseD2 = upper(inverseSummary.original.order2);

  std::cout << std::setprecision(17);
  std::cout << '{';
  std::cout << "\"schema_version\":\"rfsn-vdp-p2d-symplectic-frame-scout/1\",";
  std::cout << "\"status\":\"DESIGN_ONLY\",";
  std::cout << "\"claim_boundary\":{"
            << "\"claim_bearing\":false,"
            << "\"certificate\":false,"
            << "\"obligation_discharged\":false,"
            << "\"exact_identity_evidence\":\"validation/rigorous/audit_p2d_exact_chart.py\","
            << "\"interval_residual_role\":\"diagnostic_only\"},";
  std::cout << "\"grid\":{"
            << "\"normalized_box\":[[-1,1],[-1,1],[-1,1]],"
            << "\"subdivisions\":[16,8,4],\"cells\":512,"
            << "\"map\":[\"theta_r=25*r-1\",\"theta_a=4*a2\","
            << "\"theta_epsilon=5*(epsilon-1)\"]},";
  std::cout << "\"norm_convention\":\"order0 Frobenius; complete first jet and full 3x3 symmetric Hessian in Hilbert-Schmidt norm, with off-diagonal entries counted twice\",";

  std::cout << "\"scalar_branch_and_c2\":{";
  bool firstScalar = true;
  const auto scalar = [&](const char* name, const ScalarSummary& summary) {
    if (!firstScalar) std::cout << ',';
    firstScalar = false;
    std::cout << '\"' << name << "\":";
    printScalarSummary(summary);
  };
  scalar("c", cSummary);
  scalar("alpha", alphaSummary);
  scalar("beta", betaSummary);
  scalar("N_squared", normalizerSquaredSummary);
  scalar("y", ySummary);
  scalar("d", dSummary);
  scalar("e", eSummary);
  scalar("kappa", kappaSummary);
  scalar("kappa_plus_d", kappaPlusDSummary);
  scalar("half_denominator", halfDenominatorSummary);
  scalar("cos_theta", cosineHalfSummary);
  scalar("sin_theta", sineHalfSummary);
  scalar("theta", thetaSummary);
  scalar("kappa_inverse_sqrt", radialScaleSummary);
  std::cout << "},";

  std::cout << "\"matrix_branch_and_c2\":{";
  std::cout << "\"Y\":";
  printMatrixSummary(expandingSummary);
  std::cout << ",\"X\":";
  printMatrixSummary(stableSummary);
  std::cout << ",\"L\":";
  printMatrixSummary(completionSummary);
  std::cout << ",\"L_inverse\":";
  printMatrixSummary(inverseSummary);
  std::cout << "},";

  std::cout << "\"derived_conditioning_if_L0_orthogonal\":{"
            << "\"formal_use_requires_exact_audit_of_L0_orthogonality\":true,"
            << "\"L_minus_L0_frobenius_upper\":" << anchorDeviation << ','
            << "\"L_operator_upper_from_anchor\":" << completionNormUpper << ','
            << "\"L_smallest_singular_lower_from_anchor\":"
            << completionSmallestLower << ','
            << "\"L_inverse_operator_upper_from_anchor\":"
            << inverseNormUpper << "},";

  std::cout << "\"diagnostic_interval_residuals\":{"
            << "\"role\":\"dependency-prone outward interval diagnostics, not exact-identity proofs\","
            << "\"half_angle_unit_abs_upper\":" << halfAngleUnitResidual << ','
            << "\"A_transpose_B_A_minus_kappa_C0_frobenius_upper\":"
            << diagonalizationResidual << ','
            << "\"L_transpose_Omega_L_minus_Omega0_frobenius_upper\":"
            << symplecticResidual << ','
            << "\"L_inverse_L_minus_I_frobenius_upper\":"
            << inverseLeftResidual << ','
            << "\"L_L_inverse_minus_I_frobenius_upper\":"
            << inverseRightResidual << ','
            << "\"R_L_minus_L_R0_frobenius_upper\":"
            << reverserResidual << "},";

  std::cout << "\"gate_suggestions\":[";
  bool firstGate = true;
  printGate("d_positive", "d>2/3", dSummary.range.leftBound(),
            dSummary.range.leftBound() > 2.0 / 3.0, firstGate);
  printGate("e_negative", "-e>3/5", -eSummary.range.rightBound(),
            eSummary.range.rightBound() < -3.0 / 5.0, firstGate);
  printGate("kappa_lower", "kappa>19/20",
            kappaSummary.range.leftBound(),
            kappaSummary.range.leftBound() > 19.0 / 20.0, firstGate);
  printGate("kappa_upper", "kappa<21/20",
            kappaSummary.range.rightBound(),
            kappaSummary.range.rightBound() < 21.0 / 20.0, firstGate);
  printGate("kappa_plus_d", "kappa+d>8/5",
            kappaPlusDSummary.range.leftBound(),
            kappaPlusDSummary.range.leftBound() > 8.0 / 5.0, firstGate);
  printGate("half_denominator", "D_theta>17/10",
            halfDenominatorSummary.range.leftBound(),
            halfDenominatorSummary.range.leftBound() > 17.0 / 10.0,
            firstGate);
  printGate("positive_half_cosine", "c_theta>7/8",
            cosineHalfSummary.range.leftBound(),
            cosineHalfSummary.range.leftBound() > 7.0 / 8.0, firstGate);
  printGate("half_sine", "abs(s_theta)<5/12",
            maxAbs(sineHalfSummary.range),
            maxAbs(sineHalfSummary.range) < 5.0 / 12.0, firstGate);
  printGate("radial_scale_lower", "kappa^(-1/2)>19/20",
            radialScaleSummary.range.leftBound(),
            radialScaleSummary.range.leftBound() > 19.0 / 20.0, firstGate);
  printGate("radial_scale_upper", "kappa^(-1/2)<21/20",
            radialScaleSummary.range.rightBound(),
            radialScaleSummary.range.rightBound() < 21.0 / 20.0,
            firstGate);
  printGate("phase_origin", "abs(theta)<1/2",
            maxAbs(thetaSummary.range),
            maxAbs(thetaSummary.range) < 1.0 / 2.0, firstGate);
  printGate("anchor_deviation", "norm_F(L-L0)<1/8",
            anchorDeviation, anchorDeviation < 1.0 / 8.0, firstGate);
  printGate("normalized_L_D1", "norm_HS(D_theta L)<1/10",
            normalizedCompletionD1, normalizedCompletionD1 < 1.0 / 10.0,
            firstGate);
  printGate("normalized_L_D2", "norm_HS(D_theta^2 L)<1/10",
            normalizedCompletionD2, normalizedCompletionD2 < 1.0 / 10.0,
            firstGate);
  printGate("normalized_L_inverse_D1",
            "norm_HS(D_theta L_inverse)<1/10", normalizedInverseD1,
            normalizedInverseD1 < 1.0 / 10.0, firstGate);
  printGate("normalized_L_inverse_D2",
            "norm_HS(D_theta^2 L_inverse)<1/10", normalizedInverseD2,
            normalizedInverseD2 < 1.0 / 10.0, firstGate);
  printGate("original_L_D1", "norm_HS(D_mu L)<2",
            originalCompletionD1, originalCompletionD1 < 2.0, firstGate);
  printGate("original_L_D2", "norm_HS(D_mu^2 L)<20",
            originalCompletionD2, originalCompletionD2 < 20.0, firstGate);
  printGate("original_L_inverse_D1", "norm_HS(D_mu L_inverse)<2",
            originalInverseD1, originalInverseD1 < 2.0, firstGate);
  printGate("original_L_inverse_D2", "norm_HS(D_mu^2 L_inverse)<20",
            originalInverseD2, originalInverseD2 < 20.0, firstGate);
  std::cout << "]}" << '\n';
}
