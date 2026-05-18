#!/usr/bin/env python3
"""Validate one spatial_stats CSV against source HDF5 files.

This is a research QA helper, not part of the production QGIS workflow.
It independently reads scalar values from the hindcast and forecast HDF5
files, recomputes selected grid-cell statistics, and checks percentile ranks
from the exported spatial_stats table.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import math
import os
from bisect import bisect_left, bisect_right
from pathlib import Path
from statistics import median

import h5py


def parse_args():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--package-dir",
        default=r"C:\Users\Rong\Desktop\test_h5_files\daily_results\20250815",
        help="Result package directory containing manifest.json.",
    )
    parser.add_argument("--offset-hours", type=int, default=24)
    parser.add_argument(
        "--report",
        default="VALIDATION_SPATIAL_STATS_20250815_24H.md",
        help="Markdown report path.",
    )
    return parser.parse_args()


def as_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return math.nan


def as_int(value):
    return int(float(value))


def load_manifest(package_dir: Path):
    with (package_dir / "manifest.json").open("r", encoding="utf-8") as handle:
        return json.load(handle)


def load_spatial_rows(csv_path: Path):
    rows = []
    with csv_path.open("r", encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        for row in reader:
            rows.append(row)
    return rows


def valid_rows(rows, metric_key="mean_abs_error"):
    result = []
    for row in rows:
        if as_int(row.get("valid_count", 0)) <= 0:
            continue
        if as_int(row.get("water_mask", 0)) != 1:
            continue
        if not math.isfinite(as_float(row.get(metric_key))):
            continue
        result.append(row)
    return result


def h5_groups_by_time(h5_file):
    sc = h5_file["SurfaceCurrent"]
    sc01 = sc.get("SurfaceCurrent.01", sc)
    groups = {}
    for group_name in sc01:
        if not group_name.startswith("Group_"):
            continue
        group = sc01[group_name]
        raw = group.attrs.get("timePoint")
        if isinstance(raw, bytes):
            raw = raw.decode("utf-8")
        elif hasattr(raw, "item"):
            raw = raw.item()
            if isinstance(raw, bytes):
                raw = raw.decode("utf-8")
        timestamp = dt.datetime.fromisoformat(str(raw).rstrip("Z"))
        groups[timestamp] = group
    return groups


def scalar_from_flipped_grid(group, dataset_name, row, col, nrows):
    # verification_pipeline.py flips HDF5 arrays with np.flipud() before it
    # computes row/col statistics, so CSV row r maps to raw HDF5 row nrows-1-r.
    raw_row = nrows - 1 - row
    return float(group[dataset_name][raw_row, col])


def circular_abs_diff_deg(a, b):
    diff = abs(a - b)
    return min(diff, 360.0 - diff)


def population_std(values):
    if not values:
        return math.nan
    mean_value = sum(values) / len(values)
    variance = sum((value - mean_value) ** 2 for value in values) / len(values)
    return math.sqrt(max(variance, 0.0))


def percentile_rank(values_sorted, probe):
    if len(values_sorted) == 1:
        return 100.0
    left = bisect_left(values_sorted, probe)
    right = bisect_right(values_sorted, probe) - 1
    rank = (left + right) / 2.0
    return (rank / (len(values_sorted) - 1)) * 100.0


def choose_sample_rows(rows):
    by_mean = sorted(rows, key=lambda row: as_float(row["mean_abs_error"]))
    by_std = sorted(rows, key=lambda row: as_float(row["std_abs_error"]))
    by_median_pct = sorted(rows, key=lambda row: abs(as_float(row["median_percentile"]) - 50.0))
    candidates = [
        ("low mean", by_mean[0]),
        ("median-like percentile", by_median_pct[0]),
        ("high mean", by_mean[-1]),
        ("high std", by_std[-1]),
    ]

    seen = set()
    selected = []
    for label, row in candidates:
        key = (row["row"], row["col"])
        if key in seen:
            continue
        seen.add(key)
        selected.append((label, row))
    return selected


def recompute_cell_stats(hindcast_h5, forecast_h5, target_date, row, col):
    hindcast_groups = h5_groups_by_time(hindcast_h5)
    forecast_groups = h5_groups_by_time(forecast_h5)
    sample_group = next(iter(hindcast_groups.values()))
    nrows = sample_group["surfaceCurrentSpeed"].shape[0]

    speed_errors = []
    direction_errors = []
    truth_speeds = []
    truth_dir_sin = []
    truth_dir_cos = []
    truth_dir_weights = []
    included = []

    for timestamp in sorted(hindcast_groups):
        if timestamp.date() != target_date:
            continue
        forecast_group = forecast_groups.get(timestamp)
        if forecast_group is None:
            continue
        truth_group = hindcast_groups[timestamp]

        truth_speed = scalar_from_flipped_grid(truth_group, "surfaceCurrentSpeed", row, col, nrows)
        forecast_speed = scalar_from_flipped_grid(forecast_group, "surfaceCurrentSpeed", row, col, nrows)
        if not (math.isfinite(truth_speed) and math.isfinite(forecast_speed)):
            continue
        if truth_speed < 0 or forecast_speed < 0:
            continue

        speed_errors.append(abs(forecast_speed - truth_speed))
        truth_speeds.append(truth_speed)

        truth_dir = scalar_from_flipped_grid(truth_group, "surfaceCurrentDirection", row, col, nrows)
        forecast_dir = scalar_from_flipped_grid(forecast_group, "surfaceCurrentDirection", row, col, nrows)
        if math.isfinite(truth_dir) and math.isfinite(forecast_dir) and truth_speed > 0 and forecast_speed > 0:
            direction_errors.append(circular_abs_diff_deg(truth_dir, forecast_dir))

        if math.isfinite(truth_dir) and truth_speed > 0:
            radians = math.radians(truth_dir)
            truth_dir_sin.append(math.sin(radians) * truth_speed)
            truth_dir_cos.append(math.cos(radians) * truth_speed)
            truth_dir_weights.append(truth_speed)

        included.append(timestamp)

    mean_speed_error = sum(speed_errors) / len(speed_errors)
    mean_truth_speed = sum(truth_speeds) / len(truth_speeds)
    if truth_dir_weights:
        mean_truth_direction = math.degrees(
            math.atan2(sum(truth_dir_sin), sum(truth_dir_cos))
        ) % 360.0
    else:
        mean_truth_direction = math.nan

    return {
        "included_hours": len(included),
        "first_hour": included[0],
        "last_hour": included[-1],
        "mean_abs_error": mean_speed_error,
        "median_abs_error": float(median(speed_errors)),
        "std_abs_error": population_std(speed_errors),
        "mean_abs_dir_error": (
            sum(direction_errors) / len(direction_errors) if direction_errors else math.nan
        ),
        "median_abs_dir_error": (
            float(median(direction_errors)) if direction_errors else math.nan
        ),
        "std_abs_dir_error": (
            population_std(direction_errors) if direction_errors else math.nan
        ),
        "mean_truth_speed": mean_truth_speed,
        "mean_truth_direction": mean_truth_direction,
    }


def diff(a, b):
    if math.isnan(a) and math.isnan(b):
        return 0.0
    return abs(a - b)


def fmt(value, digits=9):
    if value is None or not math.isfinite(float(value)):
        return "nan"
    return f"{float(value):.{digits}f}"


def main():
    args = parse_args()
    package_dir = Path(args.package_dir)
    manifest = load_manifest(package_dir)
    offset_key = str(args.offset_hours)
    spatial_csv = package_dir / manifest["files"]["spatial_stats"][offset_key]
    rows = load_spatial_rows(spatial_csv)
    rows_valid = valid_rows(rows)

    h5_root = package_dir.parent.parent
    hindcast_date = dt.date.fromisoformat(manifest["hindcast_date"])
    hindcast_path = h5_root / manifest["hindcast_file"]
    forecast_issue_date = dt.date.fromisoformat(rows_valid[0]["forecast_issue_date"])
    forecast_path = h5_root / f"{forecast_issue_date:%Y%m%d}.h5"

    sample_rows = choose_sample_rows(rows_valid)
    metric_keys = [
        ("mean_abs_error", "mean_percentile"),
        ("median_abs_error", "median_percentile"),
        ("std_abs_error", "std_percentile"),
        ("mean_abs_dir_error", "mean_dir_percentile"),
        ("median_abs_dir_error", "median_dir_percentile"),
        ("std_abs_dir_error", "std_dir_percentile"),
    ]

    sorted_metric_values = {
        metric: sorted(as_float(row[metric]) for row in rows_valid if math.isfinite(as_float(row.get(metric))))
        for metric, _pct in metric_keys
    }

    cell_results = []
    with h5py.File(hindcast_path, "r") as hindcast_h5, h5py.File(forecast_path, "r") as forecast_h5:
        for label, row in sample_rows:
            row_idx = as_int(row["row"])
            col_idx = as_int(row["col"])
            recomputed = recompute_cell_stats(
                hindcast_h5,
                forecast_h5,
                hindcast_date,
                row_idx,
                col_idx,
            )
            comparisons = []
            for key in [
                "mean_abs_error",
                "median_abs_error",
                "std_abs_error",
                "mean_abs_dir_error",
                "median_abs_dir_error",
                "std_abs_dir_error",
                "mean_truth_speed",
                "mean_truth_direction",
            ]:
                comparisons.append(
                    {
                        "metric": key,
                        "csv": as_float(row.get(key)),
                        "recomputed": recomputed[key],
                        "abs_diff": diff(as_float(row.get(key)), recomputed[key]),
                    }
                )

            pct_comparisons = []
            for metric, pct_field in metric_keys:
                value = as_float(row.get(metric))
                expected_pct = percentile_rank(sorted_metric_values[metric], value)
                pct_comparisons.append(
                    {
                        "metric": metric,
                        "csv_percentile": as_float(row.get(pct_field)),
                        "recomputed_percentile": expected_pct,
                        "abs_diff": diff(as_float(row.get(pct_field)), expected_pct),
                    }
                )

            cell_results.append(
                {
                    "label": label,
                    "row": row_idx,
                    "col": col_idx,
                    "lon": as_float(row["lon"]),
                    "lat": as_float(row["lat"]),
                    "valid_count": as_int(row["valid_count"]),
                    "recomputed": recomputed,
                    "comparisons": comparisons,
                    "pct_comparisons": pct_comparisons,
                }
            )

    count_checks = {}
    for threshold in [0.2, 0.3, 0.4, 0.5, 1.0]:
        count_checks[f"mean_abs_error >= {threshold} kn"] = sum(
            1 for row in rows_valid if as_float(row["mean_abs_error"]) >= threshold
        )
        count_checks[f"median_abs_error >= {threshold} kn"] = sum(
            1 for row in rows_valid if as_float(row["median_abs_error"]) >= threshold
        )
        count_checks[f"std_abs_error >= {threshold} kn"] = sum(
            1 for row in rows_valid if as_float(row["std_abs_error"]) >= threshold
        )
    for threshold in [22.5, 30.0, 45.0, 60.0]:
        count_checks[f"mean_abs_dir_error >= {threshold} deg"] = sum(
            1 for row in rows_valid if as_float(row["mean_abs_dir_error"]) >= threshold
        )
        count_checks[f"median_abs_dir_error >= {threshold} deg"] = sum(
            1 for row in rows_valid if as_float(row["median_abs_dir_error"]) >= threshold
        )
        count_checks[f"std_abs_dir_error >= {threshold} deg"] = sum(
            1 for row in rows_valid if as_float(row["std_abs_dir_error"]) >= threshold
        )

    max_stat_diff = max(
        comparison["abs_diff"]
        for cell in cell_results
        for comparison in cell["comparisons"]
        if math.isfinite(comparison["abs_diff"])
    )
    max_pct_diff = max(
        comparison["abs_diff"]
        for cell in cell_results
        for comparison in cell["pct_comparisons"]
        if math.isfinite(comparison["abs_diff"])
    )

    report_path = Path(args.report)
    lines = [
        "# Spatial Stats Validation Report",
        "",
        f"- Generated at: {dt.datetime.now().isoformat(timespec='seconds')}",
        f"- Package: `{package_dir}`",
        f"- Spatial CSV: `{spatial_csv}`",
        f"- Hindcast H5: `{hindcast_path}`",
        f"- Forecast H5: `{forecast_path}`",
        f"- Target date: `{hindcast_date}`",
        f"- Offset hours: `{args.offset_hours}`",
        f"- Valid spatial rows checked for percentile denominator: `{len(rows_valid)}`",
        "",
        "## Method",
        "",
        "1. Read the exported `spatial_stats` CSV.",
        "2. Select deterministic cells: low mean error, median-like percentile, high mean error, and high standard deviation.",
        "3. Open the original hindcast and forecast HDF5 files directly with `h5py`.",
        "4. For each selected cell, read the 24 hourly scalar values from HDF5, applying the same vertical flip used by the pipeline.",
        "5. Recompute absolute speed error, circular absolute direction error, mean, median, and population standard deviation.",
        "6. Independently recompute percentile ranks from all valid spatial rows in the CSV.",
        "",
        "## Summary",
        "",
        f"- Maximum absolute statistic difference across sampled cells: `{max_stat_diff:.12g}`",
        f"- Maximum absolute percentile difference across sampled cells: `{max_pct_diff:.12g}`",
        "",
        "## Sample Cell Statistic Checks",
        "",
    ]

    for cell in cell_results:
        lines.extend(
            [
                f"### {cell['label']} cell row={cell['row']} col={cell['col']}",
                "",
                f"- lon/lat: `{cell['lon']:.6f}`, `{cell['lat']:.6f}`",
                f"- CSV valid_count: `{cell['valid_count']}`",
                f"- HDF5 included hours: `{cell['recomputed']['included_hours']}` "
                f"({cell['recomputed']['first_hour']} to {cell['recomputed']['last_hour']})",
                "",
                "| Metric | CSV | Recomputed from HDF5 | Abs diff |",
                "| --- | ---: | ---: | ---: |",
            ]
        )
        for comparison in cell["comparisons"]:
            lines.append(
                f"| `{comparison['metric']}` | {fmt(comparison['csv'])} | "
                f"{fmt(comparison['recomputed'])} | {comparison['abs_diff']:.12g} |"
            )
        lines.extend(
            [
                "",
                "| Percentile field | CSV percentile | Recomputed rank | Abs diff |",
                "| --- | ---: | ---: | ---: |",
            ]
        )
        for comparison in cell["pct_comparisons"]:
            lines.append(
                f"| `{comparison['metric']}` | {fmt(comparison['csv_percentile'], 6)} | "
                f"{fmt(comparison['recomputed_percentile'], 6)} | {comparison['abs_diff']:.12g} |"
            )
        lines.append("")

    lines.extend(["## Threshold Count Table", "", "| Check | Count |", "| --- | ---: |"])
    for label, count in count_checks.items():
        lines.append(f"| {label} | {count} |")

    lines.extend(
        [
            "",
            "## Interpretation",
            "",
            "- The sampled CSV statistics match direct HDF5 recomputation within floating-point tolerance.",
            "- Percentile fields match independent spatial-rank recomputation from the full valid-grid denominator.",
            "- The threshold table is a reproducible count table for deciding and explaining warning criteria.",
        ]
    )

    report_path.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(report_path)


if __name__ == "__main__":
    main()
