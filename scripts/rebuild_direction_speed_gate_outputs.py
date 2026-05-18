#!/usr/bin/env python3
"""Rebuild direction hotspot outputs after changing the direction speed gate.

This script reuses existing daily result packages. It does not recompute NC/H5
verification statistics. It rebuilds the derived hotspot layers that depend on
``S111_DIR_HOTSPOT_MIN_TRUTH_SPEED_KN``:

- official daily direction hotspots in ``*_hotspots.csv/.geojson``
- per-metric ``*.metric_hotspots.csv/.geojson``
- manifest threshold/count metadata

Optionally it also refreshes local PostgreSQL ``hotspot_points`` direction rows.
"""

from __future__ import annotations

import argparse
import csv
import datetime as dt
import json
import os
from pathlib import Path
from typing import Iterable

import sys

SCRIPT_DIR = Path(__file__).resolve().parent
PROJECT_DIR = SCRIPT_DIR.parent
if str(PROJECT_DIR) not in sys.path:
    sys.path.insert(0, str(PROJECT_DIR))

import verification_pipeline as vp  # noqa: E402


HOTSPOT_FIELDNAMES = [
    "target_date",
    "target_timestamp",
    "offset_days",
    "forecast_lead_hours",
    "lon",
    "lat",
    "error_value",
    "severity",
    "error_type",
    "speed",
    "direction",
]

METRIC_HOTSPOT_FIELDNAMES = HOTSPOT_FIELDNAMES[:9] + [
    "metric",
    "speed",
    "direction",
]


def default_package_root() -> Path:
    explicit = os.environ.get("S111_RESULT_PACKAGE_DIR")
    if explicit:
        return Path(explicit)

    desktop_root = Path.home() / "Desktop" / "test_h5_files" / "daily_results"
    if desktop_root.exists():
        return desktop_root

    return PROJECT_DIR / "data" / "h5" / "daily_results"


def read_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8-sig") as handle:
        return json.load(handle)


def write_json(path: Path, payload: dict) -> None:
    with path.open("w", encoding="utf-8") as handle:
        json.dump(payload, handle, ensure_ascii=False, indent=2)
        handle.write("\n")


def read_csv_rows(path: Path) -> list[dict]:
    with path.open("r", encoding="utf-8-sig", newline="") as handle:
        return list(csv.DictReader(handle))


def package_dirs(root: Path, dates: set[str] | None = None) -> Iterable[Path]:
    for entry in sorted(root.iterdir(), key=lambda path: path.name):
        if not entry.is_dir():
            continue
        if dates and entry.name not in dates:
            continue
        if (entry / "manifest.json").exists():
            yield entry


def parse_hindcast_date(manifest: dict, package_dir: Path) -> dt.date:
    date_text = str(manifest.get("hindcast_date") or package_dir.name)
    return dt.date.fromisoformat(
        f"{date_text[:4]}-{date_text[4:6]}-{date_text[6:]}"
        if len(date_text) == 8 and date_text.isdigit()
        else date_text
    )


def forecast_lead(row: dict) -> int | None:
    value = row.get("forecast_lead_hours") or row.get("lead_hours")
    try:
        return int(float(value))
    except (TypeError, ValueError):
        return None


def to_float_or_zero(value) -> float:
    try:
        result = float(value)
    except (TypeError, ValueError):
        return 0.0
    return result if result == result else 0.0


def is_direction_row(row: dict) -> bool:
    return str(row.get("error_type") or "").strip().lower() == "direction"


def keep_existing_speed_hotspots(hotspots_path: Path) -> list[dict]:
    if not hotspots_path.exists():
        return []
    rows = []
    for row in read_csv_rows(hotspots_path):
        if is_direction_row(row):
            continue
        normalized = {field: row.get(field, "") for field in HOTSPOT_FIELDNAMES}
        if not normalized.get("error_type"):
            normalized["error_type"] = "speed"
        rows.append(normalized)
    return rows


def spatial_rows_for_offset(package_dir: Path, manifest: dict, offset_key: str) -> list[dict]:
    spatial_name = ((manifest.get("files") or {}).get("spatial_stats") or {}).get(offset_key)
    if not spatial_name:
        return []
    spatial_path = package_dir / spatial_name
    if not spatial_path.exists():
        return []
    return read_csv_rows(spatial_path)


def metric_file_name(manifest: dict, offset_key: str) -> str:
    files = manifest.setdefault("files", {})
    existing = (files.get("hotspot_metric") or {}).get(offset_key)
    if existing:
        return str(existing)

    spatial_name = (files.get("spatial_stats") or {}).get(offset_key)
    if not spatial_name:
        return f"{offset_key}h.metric_hotspots.csv"
    stem = Path(spatial_name).stem.replace("_spatial_stats_", "_")
    return f"{stem}.metric_hotspots.csv"


def rebuild_package(package_dir: Path, dry_run: bool = False) -> dict:
    manifest_path = package_dir / "manifest.json"
    manifest = read_json(manifest_path)
    hindcast_date = parse_hindcast_date(manifest, package_dir)
    files = manifest.setdefault("files", {})

    hotspot_name = files.get("hotspots") or f"{package_dir.name}_hotspots.csv"
    hotspot_geojson_name = files.get("hotspots_geojson") or hotspot_name.replace(".csv", ".geojson")
    hotspot_path = package_dir / hotspot_name
    hotspot_geojson_path = package_dir / hotspot_geojson_name

    speed_rows = keep_existing_speed_hotspots(hotspot_path)
    direction_rows = []
    metric_files = {}
    metric_geojson_files = {}
    metric_counts = {}

    spatial_files = files.get("spatial_stats") or {}
    for offset_key in sorted(spatial_files, key=lambda value: int(value)):
        offset_hours = int(offset_key)
        spatial_rows = spatial_rows_for_offset(package_dir, manifest, offset_key)
        if not spatial_rows:
            continue

        direction_rows.extend(
            vp._daily_direction_hotspot_rows_for_package(
                hindcast_date,
                spatial_rows,
                offset_hours,
            )
        )

        metric_rows = []
        metric_counts[offset_key] = {}
        for metric_spec in vp.DAILY_HOTSPOT_METRIC_SPECS:
            rows = vp._daily_metric_hotspot_rows_for_package(
                hindcast_date,
                spatial_rows,
                offset_hours,
                metric_spec,
            )
            metric_rows.extend(rows)
            metric_counts[offset_key][metric_spec["suffix"]] = len(rows)

        metric_name = metric_file_name(manifest, offset_key)
        metric_geojson_name = metric_name.replace(".csv", ".geojson")
        metric_files[offset_key] = metric_name
        metric_geojson_files[offset_key] = metric_geojson_name

        if not dry_run:
            vp._write_csv_rows(package_dir / metric_name, METRIC_HOTSPOT_FIELDNAMES, metric_rows)
            vp._write_hotspots_geojson(package_dir / metric_geojson_name, metric_rows)

    all_hotspot_rows = speed_rows + direction_rows
    if not dry_run:
        vp._write_csv_rows(hotspot_path, HOTSPOT_FIELDNAMES, all_hotspot_rows)
        vp._write_hotspots_geojson(hotspot_geojson_path, all_hotspot_rows)

        files["hotspots"] = hotspot_name
        files["hotspots_geojson"] = hotspot_geojson_name
        files["hotspot_metric"] = metric_files
        files["hotspot_metric_geojson"] = metric_geojson_files
        manifest["hotspot_thresholds_dir_deg"] = {
            "warning": vp.DIR_HOTSPOT_WARN_DEG,
            "critical": vp.DIR_HOTSPOT_CRITICAL_DEG,
        }
        gate_payload = {
            "minimum_mean_truth_speed": vp.DIR_HOTSPOT_MIN_TRUTH_SPEED_KN,
            "selection_basis": "median_dir_count retention curve",
        }
        manifest["hotspot_thresholds_dir_truth_speed_kn"] = gate_payload
        # Keep the legacy key updated for older readers.
        manifest["hotspot_thresholds_dir_speed_kn"] = gate_payload.copy()
        counts = manifest.setdefault("counts", {})
        counts["hotspot_rows"] = len(all_hotspot_rows)
        counts["hotspot_metric_rows_by_offset"] = metric_counts
        manifest["direction_speed_gate_regenerated_at"] = dt.datetime.now().isoformat(timespec="seconds")
        write_json(manifest_path, manifest)

    direction_by_offset: dict[int, int] = {}
    for row in direction_rows:
        lead = forecast_lead(row)
        if lead is not None:
            direction_by_offset[lead] = direction_by_offset.get(lead, 0) + 1

    return {
        "package_dir": str(package_dir),
        "date": hindcast_date.isoformat(),
        "speed_rows": len(speed_rows),
        "direction_rows": len(direction_rows),
        "hotspot_rows": len(all_hotspot_rows),
        "direction_by_offset": direction_by_offset,
        "metric_counts": metric_counts,
    }


def update_db_direction_rows(conn, summary: dict) -> int:
    from psycopg2.extras import execute_values

    package_dir = Path(summary["package_dir"])
    manifest = read_json(package_dir / "manifest.json")
    hindcast_date = parse_hindcast_date(manifest, package_dir)
    hotspots_name = (manifest.get("files") or {}).get("hotspots")
    if not hotspots_name:
        return 0

    rows = []
    for row in read_csv_rows(package_dir / hotspots_name):
        if not is_direction_row(row):
            continue
        rows.append(
            (
                hindcast_date,
                None,
                forecast_lead(row),
                float(row.get("lon")),
                float(row.get("lat")),
                float(row.get("error_value")),
                "direction",
                row.get("severity"),
                None,
                float(row.get("speed") or 0.0),
                float(row.get("direction") or 0.0),
            )
        )

    with conn.cursor() as cur:
        cur.execute(
            """
            DELETE FROM hotspot_points
            WHERE target_date = %s
              AND error_type = 'direction'
              AND metric IS NULL
            """,
            (hindcast_date,),
        )
        if rows:
            execute_values(
                cur,
                """
                INSERT INTO hotspot_points
                    (target_date, target_timestamp, lead_hours, lon, lat,
                     error_value, error_type, severity, metric, speed, direction)
                VALUES %s
                """,
                rows,
                page_size=5000,
            )
    conn.commit()
    return len(rows)


def update_db_metric_rows(conn, summary: dict) -> int:
    from psycopg2.extras import execute_values

    package_dir = Path(summary["package_dir"])
    manifest = read_json(package_dir / "manifest.json")
    hindcast_date = parse_hindcast_date(manifest, package_dir)
    files = manifest.get("files") or {}
    metric_files = files.get("hotspot_metric") or {}
    if not metric_files:
        return 0

    rows = []
    for offset_key in sorted(metric_files, key=lambda value: int(value)):
        metric_path = package_dir / str(metric_files[offset_key])
        if not metric_path.exists():
            continue
        for row in read_csv_rows(metric_path):
            metric = str(row.get("metric") or "").strip()
            error_type = str(row.get("error_type") or "").strip().lower()
            lead_hours = forecast_lead(row)
            if not metric or error_type not in {"speed", "direction"} or lead_hours is None:
                continue
            rows.append(
                (
                    hindcast_date,
                    None,
                    lead_hours,
                    to_float_or_zero(row.get("lon")),
                    to_float_or_zero(row.get("lat")),
                    to_float_or_zero(row.get("error_value")),
                    error_type,
                    row.get("severity"),
                    metric,
                    to_float_or_zero(row.get("speed")),
                    to_float_or_zero(row.get("direction")),
                )
            )

    with conn.cursor() as cur:
        cur.execute(
            """
            DELETE FROM hotspot_points
            WHERE target_date = %s
              AND metric IS NOT NULL
            """,
            (hindcast_date,),
        )
        if rows:
            execute_values(
                cur,
                """
                INSERT INTO hotspot_points
                    (target_date, target_timestamp, lead_hours, lon, lat,
                     error_value, error_type, severity, metric, speed, direction)
                VALUES %s
                """,
                rows,
                page_size=5000,
            )
    conn.commit()
    return len(rows)


def connect_db(args):
    import psycopg2

    return psycopg2.connect(
        host=args.db_host,
        port=args.db_port,
        dbname=args.db_name,
        user=args.db_user,
        password=args.db_password,
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", default=str(default_package_root()))
    parser.add_argument("--date", action="append", help="Limit to YYYYMMDD; can be used multiple times.")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument(
        "--db-only",
        action="store_true",
        help="Use already rebuilt hotspot files and refresh only DB hotspot rows.",
    )
    parser.add_argument("--update-db", action="store_true", help="Refresh DB official direction rows and metric hotspot rows.")
    parser.add_argument("--db-host", default=vp.DB_CONFIG["host"])
    parser.add_argument("--db-port", default=vp.DB_CONFIG["port"], type=int)
    parser.add_argument("--db-name", default=vp.DB_CONFIG["dbname"])
    parser.add_argument("--db-user", default=vp.DB_CONFIG["user"])
    parser.add_argument("--db-password", default=os.environ.get("S111_DB_PASSWORD", vp.DB_CONFIG["password"]))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    package_root = Path(args.package_root)
    dates = {str(date).replace("-", "") for date in args.date} if args.date else None

    print(f"[設定] package_root={package_root}")
    print(f"[設定] direction speed gate={vp.DIR_HOTSPOT_MIN_TRUTH_SPEED_KN} kn")
    print(f"[設定] dry_run={args.dry_run}, update_db={args.update_db}, db_only={args.db_only}")

    conn = connect_db(args) if args.update_db and not args.dry_run else None
    try:
        processed = 0
        total_direction = 0
        total_metric = 0
        for package_dir in package_dirs(package_root, dates):
            if args.db_only:
                manifest = read_json(package_dir / "manifest.json")
                hotspots_name = (manifest.get("files") or {}).get("hotspots")
                direction_rows = 0
                if hotspots_name and (package_dir / hotspots_name).exists():
                    direction_rows = sum(
                        1 for row in read_csv_rows(package_dir / hotspots_name)
                        if is_direction_row(row)
                    )
                summary = {
                    "package_dir": str(package_dir),
                    "date": parse_hindcast_date(manifest, package_dir).isoformat(),
                    "speed_rows": 0,
                    "direction_rows": direction_rows,
                    "hotspot_rows": 0,
                    "direction_by_offset": {},
                    "metric_counts": {},
                }
            else:
                summary = rebuild_package(package_dir, dry_run=args.dry_run)
            db_rows = 0
            db_metric_rows = 0
            if conn is not None:
                db_rows = update_db_direction_rows(conn, summary)
                db_metric_rows = update_db_metric_rows(conn, summary)
            processed += 1
            total_direction += summary["direction_rows"]
            total_metric += db_metric_rows
            print(
                "[完成] {date} speed={speed_rows:,} direction={direction_rows:,} "
                "hotspot_total={hotspot_rows:,} db_direction={db_rows:,}".format(
                    db_rows=db_rows,
                    **summary,
                )
            )
        print(f"[總結] packages={processed}, direction_rows={total_direction:,}")
    finally:
        if conn is not None:
            conn.close()


if __name__ == "__main__":
    main()
