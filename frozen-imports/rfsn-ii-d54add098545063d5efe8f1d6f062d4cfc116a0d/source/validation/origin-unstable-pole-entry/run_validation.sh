#!/usr/bin/env bash
set -euo pipefail

PACKAGE_DIR=$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)
ORIGIN_GRAPH_DIR=$(cd "$PACKAGE_DIR/../origin-algebraic-heteroclinic" && pwd)
PAPERA_POLE_ENTRY_CXX=${PAPERA_POLE_ENTRY_CXX:-g++}
PAPERA_CAPD_CONFIG=${PAPERA_CAPD_CONFIG:-}

if [[ -z "$PAPERA_CAPD_CONFIG" ]]; then
  PAPERA_CAPD_CONFIG=$(command -v capd-config || true)
fi
if [[ -z "$PAPERA_CAPD_CONFIG" ]]; then
  echo "Set PAPERA_CAPD_CONFIG=/absolute/path/to/capd-config" >&2
  exit 2
fi

if [[ -n "${PAPERA_POLE_ENTRY_OUTPUT:-}" ]]; then
  OUTPUT_DIR=$PAPERA_POLE_ENTRY_OUTPUT
  mkdir -p "$OUTPUT_DIR"
else
  OUTPUT_DIR=$(mktemp -d -t papera-origin-pole-entry.XXXXXX)
fi

read -r -a CAPD_FLAGS <<<"$($PAPERA_CAPD_CONFIG --cflags --libs)"

"$PAPERA_POLE_ENTRY_CXX" -std=c++17 \
  "$ORIGIN_GRAPH_DIR/unstable_graph_probe.cpp" \
  -I"$ORIGIN_GRAPH_DIR" \
  "${CAPD_FLAGS[@]}" -O2 \
  -o "$OUTPUT_DIR/unstable_graph_probe"

"$PAPERA_POLE_ENTRY_CXX" -std=c++17 \
  "$PACKAGE_DIR/pole_phase_interval_probe.cpp" \
  -I"$ORIGIN_GRAPH_DIR" \
  "${CAPD_FLAGS[@]}" -O0 \
  -o "$OUTPUT_DIR/pole_phase_interval_probe"

"$OUTPUT_DIR/unstable_graph_probe" \
  > "$OUTPUT_DIR/unstable_graph.json"
"$OUTPUT_DIR/pole_phase_interval_probe" \
  > "$OUTPUT_DIR/pole_phase_interval.json"

if command -v python3 >/dev/null 2>&1; then
  python3 - "$OUTPUT_DIR" <<'PY'
import json
import math
import pathlib
import sys

output = pathlib.Path(sys.argv[1])
graph = json.loads((output / "unstable_graph.json").read_text())
entry = json.loads((output / "pole_phase_interval.json").read_text())

assert graph["status"] == "PASS-LOCAL-UNSTABLE-GRAPH"
assert graph["u_radius"] == 0.01
assert graph["residual_euclidean_radius"] <= 1e-20
assert graph["true_graph_residual_C0_component_upper"] <= 1e-20
assert graph["true_graph_residual_C1_operator_upper"] <= 1e-18

assert entry["status"] == "PASS-TRUE-WU-OPEN-PHASE-POLE-ENTRY"
assert entry["phase_closed_cover"] == [-0.2, 0.2]
assert entry["boxes"] == 400 and entry["box_width"] == 0.001
assert entry["source_radius"] == 0.01
assert entry["source_graph_C0_euclidean_upper"] <= 1e-20
assert entry["source_graph_C1_operator_upper"] <= 1e-18
assert entry["source_x"][1] < 0
assert entry["source_y"][1] < -0.005
assert entry["source_q"][1] < -0.005
assert entry["c0"]["tau"][0] > 10 and entry["c0"]["tau"][1] < 12
assert entry["c0"]["y"][0] > 25
assert entry["c0"]["D"][0] > 50
assert entry["c0"]["H"][0] > 250
assert entry["c0"]["y_prime"][0] > 100
assert entry["c0"]["H_prime"][0] > 1600
for bounds in entry["c1"].values():
    assert all(math.isfinite(value) for value in bounds)
assert entry["c1"]["tau_phase"][1] < 0
PY
fi

sha256sum \
  "$PACKAGE_DIR/pole_phase_interval_probe.cpp" \
  "$PACKAGE_DIR/run_validation.sh" \
  "$ORIGIN_GRAPH_DIR/unstable_graph_probe.cpp" \
  "$ORIGIN_GRAPH_DIR/unstable_graph_terms.hpp" \
  > "$OUTPUT_DIR/source.sha256"

echo "PASS: true-Wu phase interval enters the invariant pole cone"
echo "Outputs: $OUTPUT_DIR"
cat "$OUTPUT_DIR/unstable_graph.json"
cat "$OUTPUT_DIR/pole_phase_interval.json"
cat "$OUTPUT_DIR/source.sha256"
