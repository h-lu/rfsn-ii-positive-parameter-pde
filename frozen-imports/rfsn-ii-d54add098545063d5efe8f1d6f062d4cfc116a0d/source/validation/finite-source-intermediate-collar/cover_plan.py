#!/usr/bin/env python3
"""Emit the exact mesh used for the validated first-stage inner-arc cover.

This is a deterministic work-list description, not a certificate.  The
floating centres and every interval box/bridge must still be regenerated and
validated.
"""

from __future__ import annotations

import argparse
import json
import math

from generate_full_cover import INNER_U, u_worklist, v_worklist


SWITCH_U = 0.03426454453805599


def summarize(chart, jobs):
    intervals = [(value - width, value + width) for _name, value, width in jobs]
    overlaps = [
        min(left[1], right[1]) - max(left[0], right[0])
        for left, right in zip(intervals[:-1], intervals[1:])
    ]
    if overlaps and min(overlaps) <= 0:
        raise RuntimeError(f"{chart}: nonpositive planned overlap")
    return {
        "chart": chart,
        "box_count": len(jobs),
        "parameter_range": [
            min(value for _name, value, _width in jobs),
            max(value for _name, value, _width in jobs),
        ],
        "minimum_parameter_overlap": min(overlaps) if overlaps else None,
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--emit-boxes", action="store_true")
    args = parser.parse_args()
    v_jobs = v_worklist()
    u_jobs = u_worklist(SWITCH_U)
    boxes = []
    if args.emit_boxes:
        for chart, jobs in (("v", v_jobs), ("u", u_jobs)):
            boxes.extend(
                {
                    "region": name,
                    "chart": chart,
                    "centre": value,
                    "half_width": width,
                    "lower": value - width,
                    "upper": value + width,
                }
                for name, value, width in jobs
            )
    result = {
        "status": "FIRST-STAGE-WORKLIST-ONLY-NOT-A-CERTIFICATE",
        "regions": [summarize("v", v_jobs), summarize("u", u_jobs)],
        "total_box_runs_including_chart_switch_duplicate": len(v_jobs) + len(u_jobs),
        "outer_anchor": {"chart": "v", "V": v_jobs[0][1]},
        "chart_switch": {
            "V": 0.0,
            "U": SWITCH_U,
            "required": "true common-root containment bridge, not parameter overlap",
        },
        "intermediate_inner_anchor": {
            "chart": "u",
            "U": INNER_U,
            "numerical_V": -0.007704604741999802,
            "numerical_radius": math.hypot(INNER_U, -0.007704604741999802),
            "warning": "not the local fundamental annulus",
        },
        "boxes": boxes if args.emit_boxes else "use --emit-boxes",
    }
    print(json.dumps(result, indent=2, sort_keys=True))


if __name__ == "__main__":
    main()
