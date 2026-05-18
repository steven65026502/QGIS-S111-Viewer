# S-111 Verification API

這個 API 目前以資料庫 `hotspot_points` 為主，提供 threshold hotspot 點資料給前端或 QGIS 顯示。

## 啟動

```powershell
.\run_s111_api.ps1
```

本機網址：

```text
http://127.0.0.1:8111/api
```

## 主要 Endpoint

### 1. Threshold Hotspots

```text
GET /api/threshold-hotspots?date=2026-04-10&lead_hours=24&error_type=speed&threshold=0.6&limit=1000
```

用途：依照 threshold 從資料庫抓出超標點，回傳經緯度、數值與顏色。

### 2. Drawing Data

```text
GET /api/drawing-data?date=2026-04-10&lead_hours=24&error_type=speed&limit=1000
```

用途：回傳同樣格式的繪圖點資料；若沒有指定 `threshold`，則回傳符合查詢條件的 hotspot 點。

### 3. Hotspot Series

```text
GET /api/hotspot-series?id=119051239
```

用途：使用者在地圖上點選某個 hotspot 點後，查該點在 hotspot 資料表中的時間資料。

也可用經緯度查最近點：

```text
GET /api/hotspot-series?lon=120.295&lat=26.345&date=2026-04-10&lead_hours=24&error_type=speed&radius_deg=0.02
```

### 4. GeoJSON

```text
GET /api/threshold-hotspots?date=2026-04-10&lead_hours=24&error_type=speed&threshold=0.6&format=geojson&limit=1000
```

用途：回傳 GeoJSON FeatureCollection，方便地圖程式直接載入。

## 主要參數

| 參數 | 說明 |
| --- | --- |
| `date` | 目標日期，格式 `YYYY-MM-DD` 或 `YYYYMMDD` |
| `lead_hours` | 預報時距，例如 `24`、`48`、`72` |
| `error_type` | `speed` 或 `direction` |
| `threshold` | 只回傳 `value >= threshold` 的點 |
| `critical_threshold` | 可選，決定 critical 顏色分級 |
| `bbox` | 可選，限制經緯度框，格式 `min_lon,min_lat,max_lon,max_lat` |
| `limit` | 最多回傳筆數 |
| `offset` | 分頁起點 |
| `format` | `json` 或 `geojson` |

## 回傳欄位

```json
{
  "id": 119051239,
  "lon": 120.295,
  "lat": 26.345,
  "value": 0.608061254,
  "unit": "kn",
  "error_type": "speed",
  "severity": "warning",
  "color": "#FFD700",
  "target_date": "2026-04-10",
  "target_timestamp": "2026-04-10T00:00:00",
  "lead_hours": 24
}
```

QGIS / 地圖繪圖欄位：

```text
geometry = Point
crs = EPSG:4326
x_field = lon
y_field = lat
value_field = value
color_field = color
```

## 注意

目前資料來源是 `hotspot_points`，因此回傳的是 hotspot/超標點，不是所有格點。若未來要完整顯示每一個格點或完整 24 小時曲線，需要另外儲存完整格點資料。
