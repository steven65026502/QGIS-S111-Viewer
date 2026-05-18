#!/usr/bin/env python3
"""
Small HTTP API for the S-111 verification database.

This is intentionally separate from the QGIS plugin. It exposes read-only
JSON/GeoJSON endpoints that can be called from a browser, another program, or a
web map.
"""

from __future__ import annotations

import argparse
import datetime as dt
import html
import json
import os
from typing import Any

import psycopg2
import psycopg2.extras
from flask import Flask, Response, jsonify, request


DEFAULT_DB_CONFIG = {
    "host": os.environ.get("S111_DB_HOST", "localhost"),
    "port": int(os.environ.get("S111_DB_PORT", "5432")),
    "dbname": os.environ.get("S111_DB_NAME", "s111_verification"),
    "user": os.environ.get("S111_DB_USER", "postgres"),
    "password": os.environ.get("S111_DB_PASSWORD", ""),
}

DEFAULT_LIMIT = int(os.environ.get("S111_API_DEFAULT_LIMIT", "5000"))
MAX_LIMIT = int(os.environ.get("S111_API_MAX_LIMIT", "50000"))
CORS_ORIGIN = os.environ.get("S111_API_CORS_ORIGIN", "*")

HOTSPOT_WARN_KN = 0.5
HOTSPOT_CRITICAL_KN = 1.0
DIR_HOTSPOT_WARN_DEG = 30.0
DIR_HOTSPOT_CRITICAL_DEG = 45.0

HOTSPOT_WARNING_COLOR = "#FFD700"
HOTSPOT_CRITICAL_COLOR = "#FF0000"
DIR_HOTSPOT_WARNING_COLOR = "#F8A718"
DIR_HOTSPOT_CRITICAL_COLOR = "#7652E2"

REMOVED_FIELDS = {"rmse", "dir_rmse"}

METRIC_ALIASES = {
    "mean": "mean_abs_error",
    "mean_speed": "mean_abs_error",
    "mean_abs_error": "mean_abs_error",
    "median": "median_abs_error",
    "median_speed": "median_abs_error",
    "median_abs_error": "median_abs_error",
    "std": "std_abs_error",
    "std_speed": "std_abs_error",
    "std_abs_error": "std_abs_error",
    "mean_dir": "mean_abs_dir_error",
    "mean_direction": "mean_abs_dir_error",
    "mean_abs_dir_error": "mean_abs_dir_error",
    "median_dir": "median_abs_dir_error",
    "median_direction": "median_abs_dir_error",
    "median_abs_dir_error": "median_abs_dir_error",
    "std_dir": "std_abs_dir_error",
    "std_direction": "std_abs_dir_error",
    "std_abs_dir_error": "std_abs_dir_error",
}

METRIC_LAYER_DETAILS = {
    "mean_abs_error": {
        "error_type": "speed",
        "metric_alias": "mean",
        "statistic": "mean_abs_error",
        "layer_id": "metric_speed_mean_hotspots",
        "layer_name": "Metric Speed Mean Hotspots",
        "layer_name_zh": "流速平均絕對誤差 hotspot",
        "layer_role": "diagnostic_speed_mean",
        "unit": "kn",
        "value_meaning": "speed mean absolute error",
    },
    "median_abs_error": {
        "error_type": "speed",
        "metric_alias": "median",
        "statistic": "median_abs_error",
        "layer_id": "metric_speed_median_hotspots",
        "layer_name": "Metric Speed Median Hotspots",
        "layer_name_zh": "流速中位數誤差 hotspot",
        "layer_role": "diagnostic_speed_median",
        "unit": "kn",
        "value_meaning": "speed median absolute error",
    },
    "std_abs_error": {
        "error_type": "speed",
        "metric_alias": "std",
        "statistic": "std_abs_error",
        "layer_id": "metric_speed_std_hotspots",
        "layer_name": "Metric Speed STD Hotspots",
        "layer_name_zh": "流速標準差 hotspot",
        "layer_role": "diagnostic_speed_std",
        "unit": "kn",
        "value_meaning": "speed absolute-error standard deviation",
    },
    "mean_abs_dir_error": {
        "error_type": "direction",
        "metric_alias": "mean_dir",
        "statistic": "mean_abs_dir_error",
        "layer_id": "metric_direction_mean_hotspots",
        "layer_name": "Metric Direction Mean Hotspots",
        "layer_name_zh": "流向平均絕對誤差 hotspot",
        "layer_role": "diagnostic_direction_mean",
        "unit": "deg",
        "value_meaning": "direction mean absolute error after speed gate",
    },
    "median_abs_dir_error": {
        "error_type": "direction",
        "metric_alias": "median_dir",
        "statistic": "median_abs_dir_error",
        "layer_id": "metric_direction_median_hotspots",
        "layer_name": "Metric Direction Median Hotspots",
        "layer_name_zh": "流向中位數誤差 hotspot",
        "layer_role": "diagnostic_direction_median",
        "unit": "deg",
        "value_meaning": "direction median absolute error after speed gate",
    },
    "std_abs_dir_error": {
        "error_type": "direction",
        "metric_alias": "std_dir",
        "statistic": "std_abs_dir_error",
        "layer_id": "metric_direction_std_hotspots",
        "layer_name": "Metric Direction STD Hotspots",
        "layer_name_zh": "流向標準差 hotspot",
        "layer_role": "diagnostic_direction_std",
        "unit": "deg",
        "value_meaning": "direction absolute-error standard deviation after speed gate",
    },
}

SUMMARY_COLUMNS = (
    "id",
    "target_date",
    "target_timestamp",
    "lead_hours",
    "forecast_file",
    "forecast_issue_date",
    "lead_step_start",
    "lead_step_end",
    "bias",
    "max_error",
    "threshold",
    "mean_abs_error",
    "median_error",
    "std_error",
    "hotspot_warn_count",
    "hotspot_critical_count",
    "dir_bias",
    "dir_max_error",
    "dir_threshold",
    "dir_mean_abs_error",
    "dir_median_error",
    "dir_std_error",
    "dir_hotspot_warn_count",
    "dir_hotspot_critical_count",
)

HOTSPOT_COLUMNS = (
    "id",
    "target_date",
    "target_timestamp",
    "lead_hours",
    "lon",
    "lat",
    "error_value",
    "error_type",
    "severity",
    "metric",
    "speed",
    "direction",
)


class ApiError(Exception):
    def __init__(self, message: str, status_code: int = 400):
        super().__init__(message)
        self.message = message
        self.status_code = status_code


def create_app(db_config: dict[str, Any] | None = None) -> Flask:
    app = Flask(__name__)
    app.config["DB_CONFIG"] = dict(db_config or DEFAULT_DB_CONFIG)

    @app.after_request
    def add_cors_headers(response: Response) -> Response:
        response.headers["Access-Control-Allow-Origin"] = CORS_ORIGIN
        response.headers["Access-Control-Allow-Methods"] = "GET, OPTIONS"
        response.headers["Access-Control-Allow-Headers"] = "Content-Type"
        return response

    @app.errorhandler(ApiError)
    def handle_api_error(error: ApiError):
        return jsonify({"ok": False, "error": error.message}), error.status_code

    @app.errorhandler(psycopg2.Error)
    def handle_database_error(error: psycopg2.Error):
        return jsonify({"ok": False, "error": str(error).strip()}), 500

    @app.route("/")
    @app.route("/api")
    def index():
        return jsonify(
            {
                "ok": True,
                "name": "S-111 Verification API",
                "endpoints": {
                    "docs": "/docs",
                    "status": "/api/status",
                    "summary": "/api/summary?date=2026-04-10&lead_hours=24",
                    "hotspot_summary": "/api/hotspot-summary?date=2026-04-10",
                    "drawing_data": "/api/drawing-data?date=2026-04-10&lead_hours=24&error_type=speed&limit=1000",
                    "threshold_hotspots": "/api/threshold-hotspots?date=2026-04-10&lead_hours=24&error_type=speed&threshold=0.6&limit=1000",
                    "std_direction_hotspots": "/api/threshold-hotspots?date=2026-04-10&lead_hours=24&error_type=direction&metric=std_dir&threshold=30&limit=1000",
                    "hotspot_series": "/api/hotspot-series?id=119051239",
                    "hotspots_geojson": "/api/hotspots?date=2026-04-10&lead_hours=24&error_type=speed&limit=1000",
                },
                "notes": [
                    "date accepts YYYY-MM-DD or YYYYMMDD.",
                    "bbox is min_lon,min_lat,max_lon,max_lat.",
                    "hotspots returns GeoJSON by default.",
                    "drawing-data returns DB-like point rows with lon, lat, value, unit, severity, and color for QGIS/web-map drawing.",
                    "threshold-hotspots is the same drawing-data response, filtered by error_value >= threshold.",
                    "hotspot-series returns the same hotspot point through time after a map user clicks a point.",
                    "metric=official means metric IS NULL, which matches the main daily hotspot layer.",
                    "metric=median_dir returns the official direction-error median layer; metric=std_dir returns the direction-error stability/dispersion layer.",
                    "null fields are omitted by default; add include_nulls=true to inspect full database columns.",
                ],
            }
        )

    @app.route("/docs")
    @app.route("/api/docs")
    def docs():
        base_url = request.host_url.rstrip("/")
        return Response(render_docs_page(base_url), content_type="text/html; charset=utf-8")

    @app.route("/api/status")
    def status():
        with get_connection(app) as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute("SELECT COUNT(*) AS count, MIN(target_date) AS min_date, MAX(target_date) AS max_date FROM summary_stats")
            summary = dict(cur.fetchone())
            cur.execute(
                """
                SELECT error_type, COUNT(*) AS count, MAX(target_date) AS max_date
                FROM hotspot_points
                WHERE metric IS NULL
                GROUP BY error_type
                ORDER BY error_type
                """
            )
            hotspot_counts = [dict(row) for row in cur.fetchall()]
            cur.execute(
                """
                SELECT metric, error_type, COUNT(*) AS count, MAX(target_date) AS max_date
                FROM hotspot_points
                WHERE metric IS NOT NULL
                GROUP BY metric, error_type
                ORDER BY error_type, metric
                """
            )
            metric_counts = [dict(row) for row in cur.fetchall()]
            cur.execute(
                """
                SELECT target_date, lead_hours, COUNT(*) AS hourly_rows
                FROM summary_stats
                WHERE target_date = (SELECT MAX(target_date) FROM summary_stats)
                GROUP BY target_date, lead_hours
                ORDER BY lead_hours
                """
            )
            latest_summary_shape = [dict(row) for row in cur.fetchall()]

        return jsonify(
            {
                "ok": True,
                "database": safe_db_config(app.config["DB_CONFIG"]),
                "summary_stats": serialize_value(summary),
                "hotspot_points_official": serialize_value(hotspot_counts),
                "hotspot_points_metrics": serialize_value(metric_counts),
                "latest_summary_shape": serialize_value(latest_summary_shape),
            }
        )

    @app.route("/api/summary")
    def summary():
        target_date = parse_date_arg(request.args.get("date"))
        lead_hours = parse_optional_int("lead_hours")
        include_nulls = parse_bool_arg("include_nulls", False)

        where = []
        params: list[Any] = []
        if target_date is None:
            where.append("target_date = (SELECT MAX(target_date) FROM summary_stats)")
        else:
            where.append("target_date = %s")
            params.append(target_date)
        if lead_hours is not None:
            where.append("lead_hours = %s")
            params.append(lead_hours)

        sql = f"""
            SELECT {", ".join(SUMMARY_COLUMNS)}
            FROM summary_stats
            WHERE {" AND ".join(where)}
            ORDER BY target_date, lead_hours, target_timestamp
        """
        with get_connection(app) as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            rows = [dict(row) for row in cur.fetchall()]

        return jsonify(
            {
                "ok": True,
                "count": len(rows),
                "filters": {
                    "date": target_date.isoformat() if target_date else "latest",
                    "lead_hours": lead_hours,
                    "include_nulls": include_nulls,
                },
                "rows": serialize_rows(rows, include_nulls=include_nulls),
            }
        )

    @app.route("/api/hotspot-summary")
    def hotspot_summary():
        target_date = parse_date_arg(request.args.get("date"))
        include_nulls = parse_bool_arg("include_nulls", False)
        metric_raw = request.args.get("metric", "official")
        metric_filter, metric_params = parse_metric_filter(metric_raw)

        where = [metric_filter]
        params: list[Any] = list(metric_params)
        if target_date is None:
            where.append("target_date = (SELECT MAX(target_date) FROM hotspot_points WHERE metric IS NULL)")
        else:
            where.append("target_date = %s")
            params.append(target_date)

        sql = f"""
            SELECT target_date, lead_hours, error_type, severity, COUNT(*) AS count,
                   MIN(error_value) AS min_error, MAX(error_value) AS max_error,
                   AVG(error_value) AS mean_error
            FROM hotspot_points
            WHERE {" AND ".join(where)}
            GROUP BY target_date, lead_hours, error_type, severity
            ORDER BY target_date, lead_hours, error_type, severity
        """
        with get_connection(app) as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            rows = [dict(row) for row in cur.fetchall()]

        return jsonify(
            {
                "ok": True,
                "count": len(rows),
                "filters": {
                    "date": target_date.isoformat() if target_date else "latest",
                    "metric": request.args.get("metric", "official"),
                    "include_nulls": include_nulls,
                },
                "rows": serialize_rows(rows, include_nulls=include_nulls),
            }
        )

    @app.route("/api/hotspots")
    def hotspots():
        target_date = parse_date_arg(request.args.get("date"))
        lead_hours = parse_optional_int("lead_hours")
        bbox = parse_bbox_arg(required=False)
        error_type = normalize_choice("error_type", {"speed", "direction"})
        severity = normalize_choice("severity", {"warning", "critical"}, required=False)
        limit = parse_limit()
        offset = parse_nonnegative_int("offset", 0)
        output_format = normalize_choice("format", {"geojson", "json"}, required=False) or "geojson"
        include_nulls = parse_bool_arg("include_nulls", False)
        metric_raw = request.args.get("metric", "official")
        metric_filter, metric_params = parse_metric_filter(metric_raw)

        where = [metric_filter]
        params: list[Any] = list(metric_params)
        add_bbox_filter(where, params, bbox)
        if target_date is None:
            where.append("target_date = (SELECT MAX(target_date) FROM hotspot_points WHERE metric IS NULL)")
        else:
            where.append("target_date = %s")
            params.append(target_date)
        if lead_hours is not None:
            where.append("lead_hours = %s")
            params.append(lead_hours)
        if error_type is not None:
            where.append("error_type = %s")
            params.append(error_type)
        if severity is not None:
            where.append("severity = %s")
            params.append(severity)

        params.extend([limit, offset])
        sql = f"""
            SELECT {", ".join(HOTSPOT_COLUMNS)}
            FROM hotspot_points
            WHERE {" AND ".join(where)}
              AND lon IS NOT NULL
              AND lat IS NOT NULL
            ORDER BY error_value DESC NULLS LAST, id
            LIMIT %s OFFSET %s
        """
        with get_connection(app) as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            rows = [dict(row) for row in cur.fetchall()]

        payload = {
            "ok": True,
            "count": len(rows),
            "limit": limit,
            "offset": offset,
            "filters": {
                "date": target_date.isoformat() if target_date else "latest",
                "bbox": bbox_to_dict(bbox) if bbox else None,
                "lead_hours": lead_hours,
                "error_type": error_type,
                "severity": severity,
                "metric": metric_raw,
                "include_nulls": include_nulls,
            },
            "layer": hotspot_layer_metadata(error_type=error_type, metric_raw=metric_raw),
        }
        if output_format == "json":
            payload["rows"] = serialize_rows(rows, include_nulls=include_nulls)
            return jsonify(payload)

        feature_collection = {
            "type": "FeatureCollection",
            "metadata": payload,
            "features": [hotspot_row_to_feature(row, include_nulls=include_nulls) for row in rows],
        }
        return json_response(feature_collection)

    @app.route("/api/drawing-data")
    @app.route("/api/threshold-hotspots")
    @app.route("/api/qgis-points")
    def drawing_data():
        target_date = parse_date_arg(request.args.get("date"))
        lead_hours = parse_optional_int("lead_hours")
        bbox = parse_bbox_arg(required=False)
        error_type = normalize_choice("error_type", {"speed", "direction"}, required=False)
        severity = normalize_choice("severity", {"warning", "critical"}, required=False)
        threshold = parse_optional_float("threshold")
        critical_threshold = parse_optional_float("critical_threshold")
        if threshold is not None and error_type is None:
            raise ApiError("error_type is required when threshold is used")
        limit = parse_limit()
        offset = parse_nonnegative_int("offset", 0)
        output_format = normalize_choice("format", {"json", "geojson"}, required=False) or "json"
        include_nulls = parse_bool_arg("include_nulls", False)
        include_style = parse_bool_arg("include_style", True)
        include_db_fields = parse_bool_arg("include_db_fields", False)
        metric_raw = request.args.get("metric", "official")
        metric_filter, metric_params = parse_metric_filter(metric_raw)

        where = [metric_filter]
        params: list[Any] = list(metric_params)
        add_bbox_filter(where, params, bbox)
        if target_date is None:
            where.append("target_date = (SELECT MAX(target_date) FROM hotspot_points WHERE metric IS NULL)")
        else:
            where.append("target_date = %s")
            params.append(target_date)
        if lead_hours is not None:
            where.append("lead_hours = %s")
            params.append(lead_hours)
        if error_type is not None:
            where.append("error_type = %s")
            params.append(error_type)
        if severity is not None:
            where.append("severity = %s")
            params.append(severity)
        if threshold is not None:
            where.append("error_value >= %s")
            params.append(threshold)

        params.extend([limit, offset])
        sql = f"""
            SELECT {", ".join(HOTSPOT_COLUMNS)}
            FROM hotspot_points
            WHERE {" AND ".join(where)}
              AND lon IS NOT NULL
              AND lat IS NOT NULL
              AND error_value IS NOT NULL
            ORDER BY target_date, target_timestamp, lead_hours, error_type, id
            LIMIT %s OFFSET %s
        """
        with get_connection(app) as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            cur.execute(sql, params)
            rows = [dict(row) for row in cur.fetchall()]

        drawing_rows = [
            hotspot_row_to_drawing_row(
                row,
                include_nulls=include_nulls,
                include_db_fields=include_db_fields,
                warning_threshold=threshold,
                critical_threshold=critical_threshold,
            )
            for row in rows
        ]
        payload = {
            "ok": True,
            "count": len(drawing_rows),
            "limit": limit,
            "offset": offset,
            "filters": {
                "date": target_date.isoformat() if target_date else "latest",
                "bbox": bbox_to_dict(bbox) if bbox else None,
                "lead_hours": lead_hours,
                "error_type": error_type,
                "severity": severity,
                "threshold": threshold,
                "critical_threshold": critical_threshold,
                "metric": metric_raw,
                "include_nulls": include_nulls,
                "include_db_fields": include_db_fields,
            },
            "layer": hotspot_layer_metadata(error_type=error_type, metric_raw=metric_raw),
            "rows": drawing_rows,
        }
        if include_style:
            payload["qgis_drawing"] = qgis_drawing_metadata(
                error_type=error_type,
                metric_raw=metric_raw,
                warning_threshold=threshold,
                critical_threshold=critical_threshold,
            )

        if output_format == "geojson":
            metadata = dict(payload)
            metadata.pop("rows", None)
            return json_response(
                {
                    "type": "FeatureCollection",
                    "metadata": metadata,
                    "features": [
                        drawing_row_to_feature(row)
                        for row in drawing_rows
                    ],
                }
            )

        return jsonify(payload)

    @app.route("/api/hotspot-series")
    @app.route("/api/point-monitoring")
    def hotspot_series():
        point_id = parse_optional_int("id")
        target_date = parse_date_arg(request.args.get("date"))
        lead_hours = parse_optional_int("lead_hours")
        error_type = normalize_choice("error_type", {"speed", "direction"}, required=False)
        input_lon = parse_optional_float("lon")
        input_lat = parse_optional_float("lat")
        radius_deg = parse_optional_float("radius_deg")
        threshold = parse_optional_float("threshold")
        critical_threshold = parse_optional_float("critical_threshold")
        include_db_fields = parse_bool_arg("include_db_fields", False)
        include_nulls = parse_bool_arg("include_nulls", False)
        raw_metric = request.args.get("metric")
        metric_filter, metric_params = parse_metric_filter(raw_metric or "official")

        if radius_deg is not None and radius_deg < 0:
            raise ApiError("radius_deg must be >= 0")
        if point_id is None and (input_lon is None or input_lat is None):
            raise ApiError("id or lon/lat is required")
        if point_id is None and error_type is None:
            raise ApiError("error_type is required when selecting by lon/lat")

        with get_connection(app) as conn, conn.cursor(cursor_factory=psycopg2.extras.RealDictCursor) as cur:
            if point_id is not None:
                cur.execute(
                    f"""
                    SELECT {", ".join(HOTSPOT_COLUMNS)}
                    FROM hotspot_points
                    WHERE id = %s
                    """,
                    [point_id],
                )
                anchor = cur.fetchone()
                if anchor is None:
                    raise ApiError(f"unknown hotspot id: {point_id}", status_code=404)
                anchor = dict(anchor)
            else:
                nearest_where = [metric_filter, "lon IS NOT NULL", "lat IS NOT NULL"]
                nearest_params: list[Any] = list(metric_params)
                if target_date is None:
                    nearest_where.append("target_date = (SELECT MAX(target_date) FROM hotspot_points WHERE metric IS NULL)")
                else:
                    nearest_where.append("target_date = %s")
                    nearest_params.append(target_date)
                if lead_hours is not None:
                    nearest_where.append("lead_hours = %s")
                    nearest_params.append(lead_hours)
                nearest_where.append("error_type = %s")
                nearest_params.append(error_type)
                if threshold is not None:
                    nearest_where.append("error_value >= %s")
                    nearest_params.append(threshold)
                if radius_deg is not None:
                    nearest_where.append("lon BETWEEN %s AND %s AND lat BETWEEN %s AND %s")
                    nearest_params.extend([
                        input_lon - radius_deg,
                        input_lon + radius_deg,
                        input_lat - radius_deg,
                        input_lat + radius_deg,
                    ])
                cur.execute(
                    f"""
                    SELECT lon, lat,
                           MIN(((lon - %s) * (lon - %s)) + ((lat - %s) * (lat - %s))) AS distance_sq
                    FROM hotspot_points
                    WHERE {" AND ".join(nearest_where)}
                    GROUP BY lon, lat
                    ORDER BY distance_sq
                    LIMIT 1
                    """,
                    [input_lon, input_lon, input_lat, input_lat] + nearest_params,
                )
                nearest = cur.fetchone()
                if nearest is None:
                    raise ApiError("no hotspot point found near the requested lon/lat", status_code=404)
                nearest = dict(nearest)
                if radius_deg is not None and float(nearest["distance_sq"]) > radius_deg * radius_deg:
                    raise ApiError("no hotspot point found inside radius_deg", status_code=404)
                anchor = {
                    "id": None,
                    "target_date": target_date,
                    "lead_hours": lead_hours,
                    "lon": nearest["lon"],
                    "lat": nearest["lat"],
                    "error_type": error_type,
                    "distance_deg": float(nearest["distance_sq"]) ** 0.5,
                }

            series_date = target_date or anchor.get("target_date")
            series_lead_hours = lead_hours if lead_hours is not None else anchor.get("lead_hours")
            series_error_type = error_type or anchor.get("error_type")
            if series_date is None:
                series_date = get_latest_hotspot_date(cur)
            if series_lead_hours is None:
                raise ApiError("lead_hours is required when it cannot be inferred from id")
            if series_error_type is None:
                raise ApiError("error_type is required when it cannot be inferred from id")

            series_metric_raw = raw_metric
            if point_id is not None and (
                series_metric_raw is None or series_metric_raw.strip().lower() == "official"
            ):
                anchor_metric = anchor.get("metric")
                if anchor_metric is not None:
                    series_metric_raw = str(anchor_metric)
            series_metric_filter, series_metric_params = parse_metric_filter(series_metric_raw or "official")
            series_where = [
                series_metric_filter,
                "target_date = %s",
                "lead_hours = %s",
                "error_type = %s",
                "lon = %s",
                "lat = %s",
                "error_value IS NOT NULL",
            ]
            series_params: list[Any] = list(series_metric_params)
            series_params.extend([
                series_date,
                series_lead_hours,
                series_error_type,
                anchor.get("lon"),
                anchor.get("lat"),
            ])
            if threshold is not None:
                series_where.append("error_value >= %s")
                series_params.append(threshold)

            cur.execute(
                f"""
                SELECT {", ".join(HOTSPOT_COLUMNS)}
                FROM hotspot_points
                WHERE {" AND ".join(series_where)}
                ORDER BY target_timestamp, id
                """,
                series_params,
            )
            rows = [dict(row) for row in cur.fetchall()]

        drawing_rows = [
            hotspot_row_to_drawing_row(
                row,
                include_nulls=include_nulls,
                include_db_fields=include_db_fields,
                warning_threshold=threshold,
                critical_threshold=critical_threshold,
            )
            for row in rows
        ]
        return jsonify(
            {
                "ok": True,
                "count": len(drawing_rows),
                "selected_point": serialize_value(
                    {
                        "source_id": point_id,
                        "lon": anchor.get("lon"),
                        "lat": anchor.get("lat"),
                        "nearest_distance_deg": anchor.get("distance_deg"),
                    }
                ),
                "filters": {
                    "date": series_date.isoformat() if hasattr(series_date, "isoformat") else series_date,
                    "lead_hours": series_lead_hours,
                    "error_type": series_error_type,
                    "threshold": threshold,
                    "critical_threshold": critical_threshold,
                    "metric": series_metric_raw or "official",
                    "series_scope": "hotspot_rows_only",
                },
                "chart": {
                    "x_field": "target_timestamp",
                    "y_field": "value",
                    "unit_field": "unit",
                    "color_field": "color",
                },
                "rows": drawing_rows,
                "notes": [
                    "This endpoint uses hotspot_points, so it returns only rows that exist as hotspot/threshold records.",
                    "A complete all-grid 24-hour curve requires storing full grid-cell values, not only hotspot rows.",
                ],
            }
        )

    return app


def get_connection(app: Flask):
    return psycopg2.connect(**app.config["DB_CONFIG"])


def safe_db_config(config: dict[str, Any]) -> dict[str, Any]:
    safe = dict(config)
    safe["password"] = "***"
    return safe


def get_latest_hotspot_date(cur) -> dt.date:
    cur.execute("SELECT MAX(target_date) AS target_date FROM hotspot_points WHERE metric IS NULL")
    row = cur.fetchone()
    value = row["target_date"] if isinstance(row, dict) else row[0]
    if value is None:
        raise ApiError("hotspot_points has no target_date", status_code=404)
    return value


def render_docs_page(base_url: str) -> str:
    safe_base_url = html.escape(base_url, quote=True)
    examples = [
        {
            "method": "GET",
            "path": "/api/status",
            "title": "服務健康檢查",
            "description": "確認 API、資料庫連線、資料日期範圍與資料筆數。",
            "tag": "Health",
        },
        {
            "method": "GET",
            "path": "/api/threshold-hotspots?date=2026-04-10&lead_hours=24&error_type=speed&threshold=0.6&limit=1000",
            "title": "預警核心：Threshold Hotspots",
            "description": "抓出超過門檻的 hotspot 點，回傳 lon、lat、value、color 與 layer_id，前端可直接分圖層畫在地圖上。",
            "tag": "Core",
        },
        {
            "method": "GET",
            "path": "/api/threshold-hotspots?date=2026-04-10&lead_hours=24&error_type=direction&metric=std_dir&threshold=30&limit=1000",
            "title": "Direction Std Hotspots",
            "description": "流向誤差標準差圖層，用來看模型穩定度與離散程度。",
            "tag": "Metric",
        },
        {
            "method": "GET",
            "path": "/api/threshold-hotspots?date=2026-04-10&lead_hours=24&error_type=speed&threshold=0.6&format=geojson&limit=1000",
            "title": "Threshold Hotspots GeoJSON",
            "description": "同樣的超標點資料，以 GeoJSON FeatureCollection 回傳。",
            "tag": "GeoJSON",
        },
        {
            "method": "GET",
            "path": "/api/drawing-data?date=2026-04-10&lead_hours=24&error_type=speed&limit=1000",
            "title": "地圖繪製資料",
            "description": "回傳 hotspot 點位資料，包含 lon、lat、value、unit、severity、color、layer_id、layer_name_zh。",
            "tag": "Map",
        },
        {
            "method": "GET",
            "path": "/api/hotspot-summary?date=2026-04-10",
            "title": "Hotspot 統計摘要",
            "description": "依日期、lead_hours、error_type、severity 統計 hotspot 數量與誤差範圍。",
            "tag": "Stats",
        },
        {
            "method": "GET",
            "path": "/api/hotspot-series?id=119051239",
            "title": "點選後查時間資料",
            "description": "使用者點地圖上的 hotspot 後，用 id 查該點的 hotspot 時間資料。",
            "tag": "Click",
        },
        {
            "method": "GET",
            "path": "/api/hotspot-series?lon=120.295&lat=26.345&date=2026-04-10&lead_hours=24&error_type=speed&radius_deg=0.02",
            "title": "用經緯度找最近 Hotspot 點",
            "description": "沒有 id 時，可用 lon/lat 找附近最近的 hotspot 點。",
            "tag": "Click",
        },
        {
            "method": "GET",
            "path": "/api/summary?date=2026-04-10&lead_hours=24",
            "title": "Summary Stats",
            "description": "查每日每小時的 summary_stats 資料。",
            "tag": "Stats",
        },
    ]

    cards = []
    for item in examples:
        full_url = f"{base_url}{item['path']}"
        safe_full_url = html.escape(full_url, quote=True)
        safe_path = html.escape(item["path"])
        cards.append(
            f"""
            <section class="card">
              <div class="card-top">
                <span class="method">{html.escape(item['method'])}</span>
                <code>{safe_path}</code>
                <span class="tag">{html.escape(item['tag'])}</span>
              </div>
              <h2>{html.escape(item['title'])}</h2>
              <p>{html.escape(item['description'])}</p>
              <div class="url-row">
                <input readonly value="{safe_full_url}" aria-label="{html.escape(item['title'], quote=True)} URL">
                <button type="button" data-copy="{safe_full_url}">複製</button>
                <a href="{safe_full_url}" target="_blank" rel="noreferrer">開啟</a>
              </div>
            </section>
            """
        )

    return f"""<!doctype html>
<html lang="zh-Hant">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>S-111 Verification API Docs</title>
  <style>
    :root {{
      color-scheme: light;
      --bg: #f7f8fa;
      --panel: #ffffff;
      --ink: #1f2937;
      --muted: #64748b;
      --line: #d9dee7;
      --blue: #2b6cb0;
      --blue-soft: #e8f1fb;
      --green: #277a3e;
      --green-soft: #e8f6ec;
      --warn: #fff7df;
    }}
    * {{ box-sizing: border-box; }}
    body {{
      margin: 0;
      background: var(--bg);
      color: var(--ink);
      font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", "Noto Sans TC", "Microsoft JhengHei", sans-serif;
      line-height: 1.5;
    }}
    main {{
      width: min(1120px, calc(100vw - 32px));
      margin: 28px auto 44px;
    }}
    header {{
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 16px;
      margin-bottom: 22px;
    }}
    h1 {{
      margin: 0;
      font-size: 28px;
      letter-spacing: 0;
    }}
    .base {{
      display: flex;
      align-items: center;
      gap: 10px;
      color: var(--muted);
      white-space: nowrap;
    }}
    .base code {{
      color: #111827;
      background: #f0f2f5;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 8px 12px;
      font-size: 15px;
    }}
    .card {{
      background: var(--panel);
      border: 1px solid var(--line);
      border-radius: 8px;
      padding: 20px;
      margin: 14px 0;
      box-shadow: 0 1px 2px rgba(15, 23, 42, 0.04);
    }}
    .card.core {{
      border-color: var(--blue);
    }}
    .card-top {{
      display: flex;
      align-items: center;
      gap: 12px;
      flex-wrap: wrap;
      margin-bottom: 8px;
    }}
    .method {{
      color: var(--green);
      background: var(--green-soft);
      border-radius: 999px;
      padding: 3px 11px;
      font-size: 13px;
      font-weight: 700;
    }}
    .tag {{
      margin-left: auto;
      color: var(--blue);
      background: var(--blue-soft);
      border-radius: 999px;
      padding: 3px 11px;
      font-size: 13px;
      font-weight: 700;
    }}
    code {{
      font-family: "Cascadia Mono", "Consolas", monospace;
      font-size: 16px;
    }}
    h2 {{
      margin: 6px 0 4px;
      font-size: 20px;
    }}
    p {{
      margin: 0 0 14px;
      color: var(--muted);
    }}
    .url-row {{
      display: grid;
      grid-template-columns: 1fr auto auto;
      gap: 10px;
      align-items: center;
    }}
    input {{
      width: 100%;
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 10px 12px;
      font-family: "Cascadia Mono", "Consolas", monospace;
      font-size: 14px;
      color: #111827;
      background: #fbfcfd;
    }}
    button, a {{
      border: 1px solid var(--line);
      border-radius: 6px;
      padding: 10px 13px;
      background: #fff;
      color: var(--ink);
      font: inherit;
      text-decoration: none;
      cursor: pointer;
      white-space: nowrap;
    }}
    button:hover, a:hover {{
      border-color: var(--blue);
      color: var(--blue);
    }}
    .params {{
      background: #fffdf5;
      border: 1px solid #eadfbd;
      border-radius: 8px;
      padding: 18px 20px;
      margin-top: 24px;
    }}
    .params-grid {{
      display: grid;
      grid-template-columns: repeat(2, minmax(0, 1fr));
      gap: 8px 28px;
    }}
    .params code {{
      color: #111827;
    }}
    .note {{
      margin-top: 14px;
      color: #7a5b13;
    }}
    @media (max-width: 760px) {{
      header, .base {{ align-items: flex-start; flex-direction: column; }}
      .tag {{ margin-left: 0; }}
      .url-row {{ grid-template-columns: 1fr; }}
      .params-grid {{ grid-template-columns: 1fr; }}
    }}
  </style>
</head>
<body>
  <main>
    <header>
      <h1>S-111 Verification API</h1>
      <div class="base"><span>Base URL</span><code>{safe_base_url}</code></div>
    </header>
    {''.join(cards)}
    <section class="params">
      <h2>參數說明</h2>
      <div class="params-grid">
        <div><code>date</code> YYYY-MM-DD 或 YYYYMMDD</div>
        <div><code>lead_hours</code> 24 / 48 / 72</div>
        <div><code>error_type</code> speed / direction</div>
        <div><code>metric</code> official / median_dir / std_dir / mean_dir / median / std</div>
        <div><code>threshold</code> 門檻值，speed 用 kn，direction 用 deg</div>
        <div><code>limit</code> 回傳筆數上限</div>
        <div><code>format</code> json / geojson</div>
        <div><code>bbox</code> min_lon,min_lat,max_lon,max_lat</div>
      </div>
      <p class="note">目前資料最新日期範例為 2026-04-10；主要資料來源是 hotspot_points。資料庫維持一張表，前端請用 layer_id 分正式流速、正式流向、流向 STD 等圖層。</p>
    </section>
  </main>
  <script>
    document.querySelectorAll("[data-copy]").forEach((button) => {{
      button.addEventListener("click", async () => {{
        const text = button.getAttribute("data-copy");
        try {{
          await navigator.clipboard.writeText(text);
          const original = button.textContent;
          button.textContent = "已複製";
          setTimeout(() => button.textContent = original, 1200);
        }} catch (error) {{
          window.prompt("複製這個網址", text);
        }}
      }});
    }});
  </script>
</body>
</html>"""


def parse_date_arg(raw: str | None) -> dt.date | None:
    if raw is None or raw.strip() == "":
        return None
    value = raw.strip()
    try:
        if len(value) == 8 and value.isdigit():
            return dt.datetime.strptime(value, "%Y%m%d").date()
        return dt.date.fromisoformat(value)
    except ValueError as exc:
        raise ApiError("date must be YYYY-MM-DD or YYYYMMDD") from exc


def parse_optional_int(name: str) -> int | None:
    raw = request.args.get(name)
    if raw is None or raw.strip() == "":
        return None
    try:
        return int(raw)
    except ValueError as exc:
        raise ApiError(f"{name} must be an integer") from exc


def parse_optional_float(name: str) -> float | None:
    raw = request.args.get(name)
    if raw is None or raw.strip() == "":
        return None
    try:
        return float(raw)
    except ValueError as exc:
        raise ApiError(f"{name} must be a number") from exc


def parse_nonnegative_int(name: str, default: int) -> int:
    raw = request.args.get(name)
    if raw is None or raw.strip() == "":
        return default
    try:
        value = int(raw)
    except ValueError as exc:
        raise ApiError(f"{name} must be an integer") from exc
    if value < 0:
        raise ApiError(f"{name} must be >= 0")
    return value


def parse_positive_int(name: str, default: int) -> int:
    value = parse_nonnegative_int(name, default)
    if value <= 0:
        raise ApiError(f"{name} must be > 0")
    return value


def parse_bool_arg(name: str, default: bool = False) -> bool:
    raw = request.args.get(name)
    if raw is None or raw.strip() == "":
        return default
    value = raw.strip().lower()
    if value in {"1", "true", "yes", "y", "on"}:
        return True
    if value in {"0", "false", "no", "n", "off"}:
        return False
    raise ApiError(f"{name} must be true or false")


def parse_limit() -> int:
    limit = parse_nonnegative_int("limit", DEFAULT_LIMIT)
    if limit == 0:
        raise ApiError("limit must be > 0")
    return min(limit, MAX_LIMIT)


def parse_float_value(raw: str, name: str) -> float:
    try:
        return float(raw)
    except ValueError as exc:
        raise ApiError(f"{name} must be a number") from exc


def parse_bbox_arg(required: bool = False) -> tuple[float, float, float, float] | None:
    raw = request.args.get("bbox")
    if raw is not None and raw.strip() != "":
        parts = [part.strip() for part in raw.split(",")]
        if len(parts) != 4:
            raise ApiError("bbox must be min_lon,min_lat,max_lon,max_lat")
        min_lon, min_lat, max_lon, max_lat = [
            parse_float_value(part, "bbox") for part in parts
        ]
    else:
        values = {
            name: request.args.get(name)
            for name in ("min_lon", "min_lat", "max_lon", "max_lat")
        }
        if all(value in (None, "") for value in values.values()):
            if required:
                raise ApiError("bbox is required")
            return None
        missing = [name for name, value in values.items() if value in (None, "")]
        if missing:
            raise ApiError(f"missing bbox parameter(s): {', '.join(missing)}")
        min_lon = parse_float_value(values["min_lon"], "min_lon")
        min_lat = parse_float_value(values["min_lat"], "min_lat")
        max_lon = parse_float_value(values["max_lon"], "max_lon")
        max_lat = parse_float_value(values["max_lat"], "max_lat")

    if min_lon > max_lon:
        min_lon, max_lon = max_lon, min_lon
    if min_lat > max_lat:
        min_lat, max_lat = max_lat, min_lat
    if min_lon == max_lon or min_lat == max_lat:
        raise ApiError("bbox must cover a non-zero area")
    if not (-180 <= min_lon <= 180 and -180 <= max_lon <= 180):
        raise ApiError("bbox longitude must be between -180 and 180")
    if not (-90 <= min_lat <= 90 and -90 <= max_lat <= 90):
        raise ApiError("bbox latitude must be between -90 and 90")
    return min_lon, min_lat, max_lon, max_lat


def bbox_to_dict(bbox: tuple[float, float, float, float]) -> dict[str, float]:
    min_lon, min_lat, max_lon, max_lat = bbox
    return {
        "min_lon": min_lon,
        "min_lat": min_lat,
        "max_lon": max_lon,
        "max_lat": max_lat,
    }


def add_bbox_filter(
    where: list[str],
    params: list[Any],
    bbox: tuple[float, float, float, float] | None,
) -> None:
    if bbox is None:
        return
    min_lon, min_lat, max_lon, max_lat = bbox
    where.append("lon >= %s AND lon <= %s AND lat >= %s AND lat <= %s")
    params.extend([min_lon, max_lon, min_lat, max_lat])


def normalize_choice(name: str, allowed: set[str], required: bool = False) -> str | None:
    raw = request.args.get(name)
    if raw is None or raw.strip() == "":
        if required:
            raise ApiError(f"{name} is required")
        return None
    value = raw.strip().lower()
    if value not in allowed:
        raise ApiError(f"{name} must be one of: {', '.join(sorted(allowed))}")
    return value


def parse_metric_filter(raw: str | None) -> tuple[str, list[Any]]:
    value = (raw or "official").strip()
    if value == "" or value.lower() == "official":
        return "metric IS NULL", []
    if value.lower() in {"all", "any"}:
        return "TRUE", []
    value = METRIC_ALIASES.get(value.lower(), value)
    return "metric = %s", [value]


def normalize_metric_layer_key(raw: Any) -> str:
    value = str(raw or "official").strip().lower()
    if value in {"", "official", "null", "none"}:
        return "official"
    if value in {"all", "any"}:
        return "all"
    return METRIC_ALIASES.get(value, value)


def hotspot_layer_metadata(error_type: Any = None, metric_raw: Any = "official") -> dict[str, Any]:
    normalized_error_type = str(error_type or "").strip().lower() or None
    metric_key = normalize_metric_layer_key(metric_raw)
    base = {
        "storage_table": "hotspot_points",
        "geometry": "Point",
        "crs": "EPSG:4326",
        "split_by": ["error_type", "metric", "severity"],
        "value_field": "value",
        "source_value_field": "error_value",
        "x_field": "lon",
        "y_field": "lat",
        "color_field": "color",
        "direction_field": "direction",
        "speed_field": "speed",
        "direction_field_note": "direction is an auxiliary reference-flow direction, not the direction-error value.",
        "display_note": "Keep hotspot_points as one database table; split map/QGIS layers by layer_id, error_type, metric, and severity.",
    }

    if metric_key == "official":
        if normalized_error_type == "direction":
            base.update({
                "layer_id": "official_direction_median_hotspots",
                "layer_name": "Official Direction Median Hotspots",
                "layer_name_zh": "正式流向中位數誤差 hotspot",
                "layer_role": "official_direction_hotspot",
                "error_type": "direction",
                "metric": "official",
                "statistic": "median_abs_dir_error",
                "speed_gate_kn": 0.48,
                "unit": "deg",
                "value_meaning": "official direction median absolute error after the 0.48 kn speed gate",
            })
            return base
        if normalized_error_type == "speed":
            base.update({
                "layer_id": "official_speed_hotspots",
                "layer_name": "Official Speed Hotspots",
                "layer_name_zh": "正式流速誤差 hotspot",
                "layer_role": "official_speed_hotspot",
                "error_type": "speed",
                "metric": "official",
                "statistic": "speed_abs_error",
                "unit": "kn",
                "value_meaning": "official speed absolute error",
            })
            return base
        base.update({
            "layer_id": "official_mixed_hotspots",
            "layer_name": "Official Mixed Hotspots",
            "layer_name_zh": "正式混合 hotspot",
            "layer_role": "official_mixed_hotspot",
            "error_type": normalized_error_type,
            "metric": "official",
            "statistic": "mixed_official_error",
            "unit": None,
            "value_meaning": "official hotspot error value; inspect each row error_type for unit",
        })
        return base

    if metric_key == "all":
        base.update({
            "layer_id": "all_hotspot_layers",
            "layer_name": "All Hotspot Layers",
            "layer_name_zh": "全部 hotspot 圖層",
            "layer_role": "mixed_hotspot_layers",
            "error_type": normalized_error_type,
            "metric": "all",
            "statistic": "mixed",
            "unit": None,
            "value_meaning": "mixed official and metric hotspot values; split by each row layer_id before display",
        })
        return base

    detail = METRIC_LAYER_DETAILS.get(metric_key)
    if detail:
        selected = dict(detail)
        if normalized_error_type and normalized_error_type != selected["error_type"]:
            selected["layer_role"] = f"{selected['layer_role']}_filtered_as_{normalized_error_type}"
        base.update({
            "layer_id": selected["layer_id"],
            "layer_name": selected["layer_name"],
            "layer_name_zh": selected["layer_name_zh"],
            "layer_role": selected["layer_role"],
            "error_type": normalized_error_type or selected["error_type"],
            "metric": metric_key,
            "metric_alias": selected["metric_alias"],
            "statistic": selected["statistic"],
            "unit": selected["unit"],
            "value_meaning": selected["value_meaning"],
        })
        if selected["error_type"] == "direction":
            base["speed_gate_kn"] = 0.48
        return base

    base.update({
        "layer_id": f"metric_{metric_key}_hotspots",
        "layer_name": f"Metric {metric_key} Hotspots",
        "layer_name_zh": f"metric={metric_key} hotspot",
        "layer_role": "custom_metric_hotspot",
        "error_type": normalized_error_type,
        "metric": metric_key,
        "statistic": metric_key,
        "unit": "deg" if normalized_error_type == "direction" else "kn" if normalized_error_type == "speed" else None,
        "value_meaning": "custom metric hotspot error value",
    })
    return base


def serialize_rows(rows: list[dict[str, Any]], include_nulls: bool = False) -> list[dict[str, Any]]:
    return [serialize_row(row, include_nulls=include_nulls) for row in rows]


def serialize_row(row: dict[str, Any], include_nulls: bool = False) -> dict[str, Any]:
    return {
        key: serialize_value(value)
        for key, value in row.items()
        if key not in REMOVED_FIELDS and (include_nulls or value is not None)
    }


def hotspot_row_to_feature(row: dict[str, Any], include_nulls: bool = False) -> dict[str, Any]:
    drawing = hotspot_row_to_drawing_row(row, include_nulls=include_nulls)
    properties = {
        key: serialize_value(value)
        for key, value in row.items()
        if key not in {"lon", "lat"} and key not in REMOVED_FIELDS and (include_nulls or value is not None)
    }
    properties.update({
        "value": drawing.get("value"),
        "unit": drawing.get("unit"),
        "color": drawing.get("color"),
        "qgis_symbol": drawing.get("qgis_symbol"),
        "layer_id": drawing.get("layer_id"),
        "layer_name": drawing.get("layer_name"),
        "layer_name_zh": drawing.get("layer_name_zh"),
        "layer_role": drawing.get("layer_role"),
        "statistic": drawing.get("statistic"),
    })
    return {
        "type": "Feature",
        "id": row.get("id"),
        "geometry": {
            "type": "Point",
            "coordinates": [row.get("lon"), row.get("lat")],
        },
        "properties": properties,
    }


def hotspot_row_to_drawing_row(
    row: dict[str, Any],
    include_nulls: bool = False,
    include_db_fields: bool = False,
    warning_threshold: float | None = None,
    critical_threshold: float | None = None,
) -> dict[str, Any]:
    style = hotspot_style(
        row.get("error_type"),
        row.get("severity"),
        row.get("error_value"),
        warning_threshold=warning_threshold,
        critical_threshold=critical_threshold,
    )
    layer = hotspot_layer_metadata(
        error_type=row.get("error_type"),
        metric_raw=row.get("metric") or "official",
    )
    payload = {
        "id": row.get("id"),
        "target_date": row.get("target_date"),
        "target_timestamp": row.get("target_timestamp"),
        "lead_hours": row.get("lead_hours"),
        "lon": row.get("lon"),
        "lat": row.get("lat"),
        "value": row.get("error_value"),
        "value_field": "error_value",
        "unit": style["unit"],
        "error_type": row.get("error_type"),
        "severity": style["severity"],
        "layer_id": layer["layer_id"],
        "layer_name": layer["layer_name"],
        "layer_name_zh": layer["layer_name_zh"],
        "layer_role": layer["layer_role"],
        "statistic": layer["statistic"],
        "color": style["color"],
        "qgis_symbol": {
            "geometry": "Point",
            "crs": "EPSG:4326",
            "color": style["color"],
            "outline_color": style["color"],
            "size_mm": 3.5,
        },
    }

    optional_fields = {
        "source_error_value": row.get("error_value"),
        "metric": row.get("metric"),
        "speed": row.get("speed"),
        "direction": row.get("direction"),
    }
    if row.get("metric") is not None:
        payload["metric"] = row.get("metric")
    if include_db_fields or include_nulls:
        payload.update(optional_fields)
    return serialize_row(payload, include_nulls=include_nulls)


def drawing_row_to_feature(row: dict[str, Any]) -> dict[str, Any]:
    properties = {
        key: value for key, value in row.items()
        if key not in {"lon", "lat"}
    }
    return {
        "type": "Feature",
        "id": row.get("id"),
        "geometry": {
            "type": "Point",
            "coordinates": [row.get("lon"), row.get("lat")],
        },
        "properties": properties,
    }


def hotspot_style(
    error_type: Any,
    severity: Any,
    error_value: Any,
    warning_threshold: float | None = None,
    critical_threshold: float | None = None,
) -> dict[str, str]:
    normalized_error_type = str(error_type or "speed").strip().lower()
    normalized_severity = normalize_hotspot_severity(
        normalized_error_type,
        severity,
        error_value,
        warning_threshold=warning_threshold,
        critical_threshold=critical_threshold,
    )
    if normalized_error_type == "direction":
        return {
            "severity": normalized_severity,
            "unit": "deg",
            "color": (
                DIR_HOTSPOT_CRITICAL_COLOR
                if normalized_severity == "critical"
                else DIR_HOTSPOT_WARNING_COLOR
            ),
        }
    return {
        "severity": normalized_severity,
        "unit": "kn",
        "color": (
            HOTSPOT_CRITICAL_COLOR
            if normalized_severity == "critical"
            else HOTSPOT_WARNING_COLOR
        ),
    }


def normalize_hotspot_severity(
    error_type: str,
    severity: Any,
    error_value: Any,
    warning_threshold: float | None = None,
    critical_threshold: float | None = None,
) -> str:
    if warning_threshold is not None or critical_threshold is not None:
        try:
            value = float(error_value)
        except (TypeError, ValueError):
            return "warning"
        critical = default_critical_threshold(error_type) if critical_threshold is None else critical_threshold
        return "critical" if value >= critical else "warning"

    normalized = str(severity or "").strip().lower()
    if normalized in {"warning", "critical"}:
        return normalized
    try:
        value = float(error_value)
    except (TypeError, ValueError):
        return "warning"
    if error_type == "direction":
        return "critical" if value >= DIR_HOTSPOT_CRITICAL_DEG else "warning"
    return "critical" if value >= HOTSPOT_CRITICAL_KN else "warning"


def default_warning_threshold(error_type: str | None) -> float:
    return DIR_HOTSPOT_WARN_DEG if error_type == "direction" else HOTSPOT_WARN_KN


def default_critical_threshold(error_type: str | None) -> float:
    return DIR_HOTSPOT_CRITICAL_DEG if error_type == "direction" else HOTSPOT_CRITICAL_KN


def qgis_drawing_metadata(
    error_type: str | None = None,
    metric_raw: Any = "official",
    warning_threshold: float | None = None,
    critical_threshold: float | None = None,
) -> dict[str, Any]:
    speed_warning = HOTSPOT_WARN_KN
    speed_critical = HOTSPOT_CRITICAL_KN
    direction_warning = DIR_HOTSPOT_WARN_DEG
    direction_critical = DIR_HOTSPOT_CRITICAL_DEG

    if error_type == "speed":
        speed_warning = warning_threshold if warning_threshold is not None else speed_warning
        speed_critical = critical_threshold if critical_threshold is not None else speed_critical
    elif error_type == "direction":
        direction_warning = warning_threshold if warning_threshold is not None else direction_warning
        direction_critical = critical_threshold if critical_threshold is not None else direction_critical

    return {
        "geometry": "Point",
        "crs": "EPSG:4326",
        "x_field": "lon",
        "y_field": "lat",
        "value_field": "value",
        "source_value_field": "error_value",
        "color_field": "color",
        "unit_field": "unit",
        "layer": hotspot_layer_metadata(error_type=error_type, metric_raw=metric_raw),
        "recommended_symbol": {
            "type": "simple_marker",
            "shape": "circle",
            "size_mm": 3.5,
            "fill_color_field": "color",
            "outline_color_field": "color",
        },
        "color_rules": [
            {
                "error_type": "speed",
                "severity": "warning",
                "min": speed_warning,
                "max": speed_critical,
                "unit": "kn",
                "color": HOTSPOT_WARNING_COLOR,
                "label": f"{speed_warning:g}-{speed_critical:g} kn",
            },
            {
                "error_type": "speed",
                "severity": "critical",
                "min": speed_critical,
                "max": None,
                "unit": "kn",
                "color": HOTSPOT_CRITICAL_COLOR,
                "label": f">= {speed_critical:g} kn",
            },
            {
                "error_type": "direction",
                "severity": "warning",
                "min": direction_warning,
                "max": direction_critical,
                "unit": "deg",
                "color": DIR_HOTSPOT_WARNING_COLOR,
                "label": f"{direction_warning:g}-{direction_critical:g} deg",
            },
            {
                "error_type": "direction",
                "severity": "critical",
                "min": direction_critical,
                "max": None,
                "unit": "deg",
                "color": DIR_HOTSPOT_CRITICAL_COLOR,
                "label": f">= {direction_critical:g} deg",
            },
        ],
    }


def serialize_value(value: Any) -> Any:
    if isinstance(value, (dt.date, dt.datetime)):
        return value.isoformat()
    if isinstance(value, list):
        return [serialize_value(item) for item in value]
    if isinstance(value, tuple):
        return [serialize_value(item) for item in value]
    if isinstance(value, dict):
        return {key: serialize_value(item) for key, item in value.items()}
    return value


def json_response(payload: dict[str, Any]) -> Response:
    return Response(
        json.dumps(payload, ensure_ascii=False, allow_nan=False),
        content_type="application/geo+json; charset=utf-8",
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run the S-111 verification read-only API.")
    parser.add_argument("--host", default=os.environ.get("S111_API_HOST", "127.0.0.1"))
    parser.add_argument("--port", type=int, default=int(os.environ.get("S111_API_PORT", "8111")))
    parser.add_argument("--debug", action="store_true")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    app = create_app()
    app.run(host=args.host, port=args.port, debug=args.debug)


if __name__ == "__main__":
    main()
