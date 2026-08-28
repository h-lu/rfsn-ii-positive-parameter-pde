#!/usr/bin/env bash
set -euo pipefail

PACKAGE_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
PAPERA_ANNULUS_CXX=${PAPERA_ANNULUS_CXX:-g++}
PAPERA_ANNULUS_CAPD_CONFIG=${PAPERA_ANNULUS_CAPD_CONFIG:-}

if [[ -z "$PAPERA_ANNULUS_CAPD_CONFIG" ]]; then
  PAPERA_ANNULUS_CAPD_CONFIG=$(command -v capd-config || true)
fi
if [[ -z "$PAPERA_ANNULUS_CAPD_CONFIG" ]]; then
  echo "Set PAPERA_ANNULUS_CAPD_CONFIG=/absolute/path/to/capd-config" >&2
  exit 2
fi

if [[ -n "${PAPERA_ANNULUS_OUTPUT:-}" ]]; then
  OUTPUT_DIR=$PAPERA_ANNULUS_OUTPUT
  mkdir -p "$OUTPUT_DIR"
else
  OUTPUT_DIR=$(mktemp -d -t papera-fundamental-annulus.XXXXXX)
fi

read -r -a CAPD_FLAGS <<<"$($PAPERA_ANNULUS_CAPD_CONFIG --cflags --libs)"

"$PAPERA_ANNULUS_CXX" \
  "$PACKAGE_DIR/local_annulus_bounds_probe.cpp" \
  "${CAPD_FLAGS[@]}" -O0 \
  -o "$OUTPUT_DIR/local_annulus_bounds_probe"
"$PAPERA_ANNULUS_CXX" \
  "$PACKAGE_DIR/exit_target_chart_probe.cpp" \
  "${CAPD_FLAGS[@]}" -O0 \
  -o "$OUTPUT_DIR/exit_target_chart_probe"
"$PAPERA_ANNULUS_CXX" \
  "$PACKAGE_DIR/fixed_radial_source_probe.cpp" \
  "${CAPD_FLAGS[@]}" -O0 \
  -o "$OUTPUT_DIR/fixed_radial_source_probe"

"$OUTPUT_DIR/local_annulus_bounds_probe" \
  > "$OUTPUT_DIR/local_annulus_bounds.json"
"$OUTPUT_DIR/exit_target_chart_probe" --stable-half-width 2e-6 \
  > "$OUTPUT_DIR/exit_target_chart.json"
"$OUTPUT_DIR/exit_target_chart_probe" --stable-half-width 1e-12 \
  > "$OUTPUT_DIR/exit_target_centre.json"
"$OUTPUT_DIR/fixed_radial_source_probe" --half-width 1e-12 \
  > "$OUTPUT_DIR/fixed_radial_source.json"

if command -v python3 >/dev/null 2>&1; then
  python3 -m json.tool "$OUTPUT_DIR/local_annulus_bounds.json" >/dev/null
  python3 -m json.tool "$OUTPUT_DIR/exit_target_chart.json" >/dev/null
  python3 -m json.tool "$OUTPUT_DIR/exit_target_centre.json" >/dev/null
  python3 -m json.tool "$OUTPUT_DIR/fixed_radial_source.json" >/dev/null
fi

sha256sum \
  "$PACKAGE_DIR/local_annulus_bounds_probe.cpp" \
  "$PACKAGE_DIR/exit_target_chart_probe.cpp" \
  "$PACKAGE_DIR/exit_target_centres.hpp" \
  "$PACKAGE_DIR/fixed_radial_source_probe.cpp" \
  "$PACKAGE_DIR/fixed_radial_source_centres.hpp" \
  "$PACKAGE_DIR/run_validation.sh" \
  > "$OUTPUT_DIR/source.sha256"

sha256sum \
  "$PACKAGE_DIR/../future-target-fold/tail_graph_generated.hpp" \
  "$PACKAGE_DIR/../future-target-fold/weighted_tail_generated.hpp" \
  "$PACKAGE_DIR/../future-target-fold/certificate.json" \
  "$PACKAGE_DIR/../origin-algebraic-heteroclinic/certificate.json" \
  > "$OUTPUT_DIR/dependency.sha256"

echo "PASS: quantitative local annulus, exit chart, and fixed radial seam"
echo "Outputs: $OUTPUT_DIR"
cat "$OUTPUT_DIR/local_annulus_bounds.json"
cat "$OUTPUT_DIR/exit_target_chart.json"
cat "$OUTPUT_DIR/exit_target_centre.json"
cat "$OUTPUT_DIR/fixed_radial_source.json"
cat "$OUTPUT_DIR/source.sha256"
cat "$OUTPUT_DIR/dependency.sha256"
