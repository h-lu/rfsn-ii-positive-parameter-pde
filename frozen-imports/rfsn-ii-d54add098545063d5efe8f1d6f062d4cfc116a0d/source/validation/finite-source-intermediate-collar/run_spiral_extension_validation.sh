#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 3 || $# -gt 4 ]]; then
  echo "usage: $0 WORK_ROOT COARSE_MANIFEST COARSE_SEEDS [WORKERS]" >&2
  exit 64
fi

HERE=$(cd -- "$(dirname -- "$0")" && pwd)
REPO_ROOT=$(git -C "$HERE" rev-parse --show-toplevel)
WORK_ROOT=$1
COARSE_MANIFEST=$2
COARSE_SEEDS=$3
WORKERS=${4:-24}
CAPD_CONFIG=${CAPD_CONFIG:-capd-config}

mkdir -p -- "$WORK_ROOT"
WORK_ROOT=$(cd -- "$WORK_ROOT" && pwd)
case "$WORK_ROOT/" in
  "$REPO_ROOT/"*)
    echo "WORK_ROOT must be outside the repository" >&2
    exit 65
    ;;
esac
if [[ ! -f "$COARSE_MANIFEST" || ! -f "$COARSE_SEEDS" ]]; then
  echo "the promoted coarse manifest and seeds must both exist" >&2
  exit 66
fi

export PYTHONDONTWRITEBYTECODE=1

python3 "$HERE/generate_spiral_extension_cover.py" \
  --output-dir "$WORK_ROOT/base" \
  --segments 108

python3 "$HERE/refine_spiral_extension_cover.py" \
  --base-dir "$WORK_ROOT/base" \
  --plan "$HERE/spiral_extension_refinement_plan.json" \
  --output-dir "$WORK_ROOT/refined"

python3 "$HERE/validate_spiral_extension_cover.py" \
  --input-dir "$WORK_ROOT/refined" \
  --output-dir "$WORK_ROOT/validation" \
  --coarse-manifest "$COARSE_MANIFEST" \
  --coarse-seeds "$COARSE_SEEDS" \
  --coarse-segments 36 \
  --capd-config "$CAPD_CONFIG" \
  --workers "$WORKERS"

python3 "$HERE/build_spiral_extension_certificate.py" \
  --base-centres-dir "$WORK_ROOT/base" \
  --centres-dir "$WORK_ROOT/refined" \
  --validation-dir "$WORK_ROOT/validation" \
  --refinement-plan "$HERE/spiral_extension_refinement_plan.json" \
  --coarse-manifest "$COARSE_MANIFEST" \
  --coarse-seeds "$COARSE_SEEDS" \
  --output "$WORK_ROOT/spiral_extension_certificate.json"

sha256sum \
  "$WORK_ROOT/base/spiral_extension_boxes.jsonl" \
  "$WORK_ROOT/base/spiral_extension_seeds.txt" \
  "$WORK_ROOT/base/spiral_extension_centres_summary.json" \
  "$WORK_ROOT/refined/spiral_extension_boxes.jsonl" \
  "$WORK_ROOT/refined/spiral_extension_seeds.txt" \
  "$WORK_ROOT/refined/spiral_extension_centres_summary.json" \
  "$WORK_ROOT/validation/spiral_extension_results.jsonl" \
  "$WORK_ROOT/validation/spiral_extension_bridge_results.jsonl" \
  "$WORK_ROOT/spiral_extension_certificate.json"
