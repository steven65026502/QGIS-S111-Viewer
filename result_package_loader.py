"""
result_package_loader.py

S-111 驗證系統成果包讀取層。
讀取 daily_results/YYYYMMDD/ 目錄下的 manifest.json 與各 CSV 檔案，
將欄位正規化後回傳 Python 原生結構（list of dict / dict）。
僅依賴標準函式庫（csv、json、os），可在 QGIS 外單獨測試。
"""

import csv
import json
import os

# ---------------------------------------------------------------------------
# 欄位正規化映射：舊名 -> 新名
# ---------------------------------------------------------------------------
_FIELD_RENAME = {
    "hindcast_date": "target_date",
    "target_time": "target_timestamp",
    "offset_hours": "forecast_lead_hours",
    "error_val": "error_value",
}

# 需要嘗試轉為 float 的欄位集合（凡出現即轉，轉失敗給 None）
_NUMERIC_FIELDS = {
    "forecast_lead_hours",
    "offset_days",
    "lon",
    "lat",
    "error_value",
    "speed",
    "direction",
    "row",
    "col",
    "valid_count",
    "water_mask",
    "mean_abs_error",
    "median_abs_error",
    "std_abs_error",
    "mean_percentile",
    "median_percentile",
    "std_percentile",
    "mean_abs_dir_error",
    "median_abs_dir_error",
    "std_abs_dir_error",
    "mean_dir_percentile",
    "median_dir_percentile",
    "std_dir_percentile",
    "mean_truth_speed",
    "mean_truth_direction",
    "r2",
    "rmse",
    "bias",
    "max_err",
    "threshold",
    "mean_abs_err",
    "median_err",
    "std_err",
    "hotspot_warn_count",
    "hotspot_critical_count",
    "dir_rmse",
    "dir_bias",
    "dir_max_err",
    "dir_threshold",
    "sample_count",
    "lead_step_start",
    "lead_step_end",
}


# ---------------------------------------------------------------------------
# 內部工具
# ---------------------------------------------------------------------------

def _normalize_row(row: dict) -> dict:
    """將 CSV 的一列欄位名正規化，並對數值欄位做 float() 轉型。"""
    out = {}
    for key, val in row.items():
        # 去掉可能的空白（csv 有時會有前綴空格）
        clean_key = key.strip().lstrip("\ufeff")
        # 欄位改名
        new_key = _FIELD_RENAME.get(clean_key, clean_key)
        # 數值轉型
        if new_key in _NUMERIC_FIELDS:
            try:
                out[new_key] = float(val)
            except (ValueError, TypeError):
                out[new_key] = None
        else:
            out[new_key] = val.strip() if isinstance(val, str) else val
    return out


def _resolve_manifest(manifest_or_path):
    """
    接受 str（manifest.json 路徑）或 dict（已載入的 manifest）。
    回傳 (manifest_dict, package_dir)。
    package_dir 是 manifest.json 所在目錄。
    若讀檔失敗回傳 (None, None)。
    """
    if isinstance(manifest_or_path, str):
        path = manifest_or_path
        if not os.path.isfile(path):
            print(f"[result_package_loader] 找不到 manifest 檔案：{path}")
            return None, None
        try:
            with open(path, "r", encoding="utf-8") as f:
                manifest = json.load(f)
        except Exception as e:
            print(f"[result_package_loader] 讀取 manifest 失敗：{path}  ({e})")
            return None, None
        package_dir = os.path.dirname(os.path.abspath(path))
        return manifest, package_dir

    if isinstance(manifest_or_path, dict):
        # dict 模式：package_dir 無法從這裡推導，
        # 呼叫端須自行確保 CSV 路徑可解析（見各 load 函式）
        return manifest_or_path, None

    print(f"[result_package_loader] manifest_or_path 型別不支援：{type(manifest_or_path)}")
    return None, None


def _read_csv(filepath: str) -> list:
    """讀取 CSV 並回傳 list of dict（原始欄位，未正規化）。失敗回傳空 list。"""
    if not os.path.isfile(filepath):
        print(f"[result_package_loader] 找不到 CSV 檔案：{filepath}")
        return []
    try:
        with open(filepath, newline="", encoding="utf-8-sig") as f:
            reader = csv.DictReader(f)
            return [dict(row) for row in reader]
    except Exception as e:
        print(f"[result_package_loader] 讀取 CSV 失敗：{filepath}  ({e})")
        return []


def _resolve_file(manifest: dict, package_dir: str, *keys) -> str | None:
    """
    從 manifest["files"] 依序用 keys 取得相對路徑，
    組合 package_dir 後回傳絕對路徑。
    keys 支援多層：例如 ("spatial_stats", "24")。
    """
    if package_dir is None:
        print("[result_package_loader] package_dir 未知，無法解析 CSV 路徑。")
        return None
    node = manifest.get("files", {})
    for k in keys:
        if not isinstance(node, dict):
            return None
        node = node.get(k)
    if not isinstance(node, str):
        return None
    return os.path.join(package_dir, node)


# ---------------------------------------------------------------------------
# 公開 API
# ---------------------------------------------------------------------------

def load_manifest(manifest_path: str) -> dict:
    """
    讀取並回傳 manifest dict。
    檔案不存在或解析失敗時回傳空 dict。
    """
    manifest, _ = _resolve_manifest(manifest_path)
    return manifest if manifest is not None else {}


def load_summary_stats(manifest_or_path) -> list:
    """
    讀取 summary_stats.csv，欄位正規化後回傳 list of dict。
    失敗或檔案不存在時回傳空 list。
    """
    manifest, package_dir = _resolve_manifest(manifest_or_path)
    if manifest is None:
        return []
    filepath = _resolve_file(manifest, package_dir, "summary_stats")
    if filepath is None:
        print("[result_package_loader] manifest 中找不到 summary_stats 路徑。")
        return []
    raw_rows = _read_csv(filepath)
    return [_normalize_row(row) for row in raw_rows]


def load_hotspots(manifest_or_path, offset_hours=None) -> list:
    """
    讀取 hotspots.csv，欄位正規化後回傳 list of dict。
    offset_hours（整數）不為 None 時，只回傳該 forecast_lead_hours 的列。
    失敗或檔案不存在時回傳空 list。
    """
    manifest, package_dir = _resolve_manifest(manifest_or_path)
    if manifest is None:
        return []
    filepath = _resolve_file(manifest, package_dir, "hotspots")
    if filepath is None:
        print("[result_package_loader] manifest 中找不到 hotspots 路徑。")
        return []
    raw_rows = _read_csv(filepath)
    result = [_normalize_row(row) for row in raw_rows]
    if offset_hours is not None:
        target = float(offset_hours)
        result = [r for r in result if r.get("forecast_lead_hours") == target]
    return result


def load_spatial_stats(manifest_or_path, offset_hours: int) -> list:
    """
    讀取指定 offset_hours 的 spatial_stats CSV，欄位正規化後回傳 list of dict。
    manifest 的 spatial_stats key 為字串（"24"/"48"/"72"），以 str(offset_hours) 查詢。
    找不到對應檔案或失敗時回傳空 list。
    """
    manifest, package_dir = _resolve_manifest(manifest_or_path)
    if manifest is None:
        return []
    key = str(offset_hours)
    filepath = _resolve_file(manifest, package_dir, "spatial_stats", key)
    if filepath is None:
        print(f"[result_package_loader] manifest 中找不到 spatial_stats[{key!r}] 路徑。")
        return []
    raw_rows = _read_csv(filepath)
    return [_normalize_row(row) for row in raw_rows]
