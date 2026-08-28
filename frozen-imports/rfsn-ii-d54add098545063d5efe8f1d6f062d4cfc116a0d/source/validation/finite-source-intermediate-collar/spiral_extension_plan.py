#!/usr/bin/env python3
"""Conservative work-list design for the unvalidated local-annulus extension.

The axis locations are floating reconnaissance values.  This script only
counts a proposed mesh; it deliberately emits no theorem/certificate status.
"""

from __future__ import annotations

import json
import math


REGIONS = [
    {
        "name": "quadrant-IV-u-chart",
        "chart": "u",
        "start": 0.023799818459857215,
        "stop": 0.0,
        "half_width": 4.0e-6,
        "maximum_stride": 6.0e-6,
        "segments": 108,
    },
    {
        "name": "quadrant-III-v-chart-outer",
        "chart": "v",
        "start": -0.0070364116384065934,
        "stop": -0.002,
        "half_width": 3.0e-6,
        "maximum_stride": 4.5e-6,
        "segments": 108,
    },
    {
        "name": "quadrant-III-v-chart-inner",
        "chart": "v",
        "start": -0.002,
        "stop": 0.0,
        "half_width": 1.0e-6,
        "maximum_stride": 1.5e-6,
        "segments": 108,
    },
    {
        "name": "quadrant-II-u-chart-outer",
        "chart": "u",
        "start": -0.0014633844332579526,
        "stop": -0.0005,
        "half_width": 5.0e-7,
        "maximum_stride": 7.5e-7,
        "segments": 108,
    },
    {
        "name": "quadrant-II-u-chart-annulus",
        "chart": "u",
        "start": -0.0005,
        "stop": 0.0,
        "half_width": 2.0e-7,
        "maximum_stride": 3.0e-7,
        "segments": 108,
    },
]


def main():
    total = 0
    regions = []
    for region in REGIONS:
        steps = int(math.ceil(abs(region["stop"] - region["start"]) / region["maximum_stride"]))
        count = steps + 1
        actual_stride = abs(region["stop"] - region["start"]) / steps
        overlap = 2 * region["half_width"] - actual_stride
        if overlap <= 0:
            raise RuntimeError(f"{region['name']}: nonpositive proposed overlap")
        regions.append(
            {
                **region,
                "proposed_box_count_including_region_endpoints": count,
                "actual_stride": actual_stride,
                "planned_parameter_overlap": overlap,
            }
        )
        total += count
    print(
        json.dumps(
            {
                "status": "PROPOSED-NOT-GENERATED-NOT-INTERVAL-VALIDATED",
                "purpose": "extend R≈0.025 collar toward the local source annulus",
                "regions": regions,
                "proposed_runs_including_boundary_duplicates": total,
                "required_adjacency_gate": "common-root containment at every pair and both chart switches",
                "reconnaissance_annulus_axis": {
                    "U": 0.0,
                    "V": 0.00030436859259991468,
                    "radius": 0.00030436859259991468,
                    "current_strict_local_outer_radius": 0.00024,
                    "overlaps_current_strict_local_annulus": False,
                },
            },
            indent=2,
            sort_keys=True,
        )
    )


if __name__ == "__main__":
    main()
