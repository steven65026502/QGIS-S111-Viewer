# S-111 API 交接說明

目前 API 已改成資料庫 hotspot threshold 版本。
2026-05-14 已補上 metric hotspot，其中 `std_dir` 可用來查流向誤差標準差，也就是穩定度/離散度較差的點。
2026-05-17 已補上 `layer_id` / `layer_name_zh` / `layer_role`，前端可以直接用這些欄位把 hotspot 顯示成不同圖層；資料庫仍維持一張 `hotspot_points`。
2026-05-18 已更新流向誤差顏色：warning 改為 `#F8A718`，critical 改為 `#7652E2`。這次只更新顯示顏色與文件，沒有重算資料庫或 GeoJSON 成果包；詳見 `API_UPDATE_LOG_20260518_DIRECTION_COLOR.md`。

## 使用情境

1. 前端設定 threshold。
2. API 從 `hotspot_points` 抓出超過 threshold 的點。
3. 回傳每個點的經緯度、誤差值、單位、顏色。
4. 前端將點畫在地圖上。
5. 使用者點選某個點後，再查該點的 hotspot 時間資料。

## 啟動

```powershell
.\run_s111_api.ps1
```

預設網址：

```text
http://127.0.0.1:8111
```

## 主要 API

### 1. 查超標點

```text
GET /api/threshold-hotspots?date=2026-04-10&lead_hours=24&error_type=speed&threshold=0.6&limit=1000
```

回傳 `rows` 是多筆點資料。

官方流向 hotspot：

```text
GET /api/threshold-hotspots?date=2026-04-10&lead_hours=24&error_type=direction&threshold=30&limit=1000
```

流向誤差標準差 hotspot：

```text
GET /api/threshold-hotspots?date=2026-04-10&lead_hours=24&error_type=direction&metric=std_dir&threshold=30&limit=1000
```

`metric=std_dir` 代表資料庫中的 `std_abs_dir_error`，單位是 `deg`。

### 2. 地圖點選後查該點資料

```text
GET /api/hotspot-series?id=119051239
```

如果點的是 `metric=std_dir` 回傳的點，直接用該點 `id` 查，API 會自動沿用該點的 `std_abs_dir_error` metric。

或用經緯度查最近 hotspot 點：

```text
GET /api/hotspot-series?lon=120.295&lat=26.345&date=2026-04-10&lead_hours=24&error_type=speed&radius_deg=0.02
```

## 回傳點資料格式

```json
{
  "id": 121117003,
  "lon": 121.065,
  "lat": 26.995,
  "value": 58.7962646484375,
  "unit": "deg",
  "error_type": "direction",
  "metric": "std_abs_dir_error",
  "layer_id": "metric_direction_std_hotspots",
  "layer_name_zh": "流向標準差 hotspot",
  "layer_role": "diagnostic_direction_std",
  "statistic": "std_abs_dir_error",
  "severity": "critical",
  "color": "#7652E2",
  "target_date": "2026-04-10",
  "lead_hours": 24
}
```

最外層也會有 `layer` 物件，說明這次查詢的圖層用途。若同一次查詢混合多種 metric，請以前端每筆 row 的 `layer_id` 分圖層。

## 前端或 QGIS 繪圖欄位

```text
geometry = Point
crs = EPSG:4326
x_field = lon
y_field = lat
value_field = value
color_field = color
```

## 顏色規則

| 類型 | 等級 | 預設門檻 | 顏色 |
| --- | --- | --- | --- |
| speed | warning | 0.5-1.0 kn | `#FFD700` |
| speed | critical | >= 1.0 kn | `#FF0000` |
| direction | warning | 30-45 deg | `#F8A718` |
| direction | critical | >= 45 deg | `#7652E2` |

## 可用 metric

| API 參數 | 實際資料庫欄位 | 說明 |
| --- | --- | --- |
| `official` 或不填 | `metric IS NULL` | 官方 hotspot |
| `median_dir` | `median_abs_dir_error` | 官方流向誤差中位數指標 |
| `std_dir` | `std_abs_dir_error` | 流向誤差標準差，穩定度/離散度指標 |
| `mean_dir` | `mean_abs_dir_error` | 流向平均絕對誤差 |
| `median` | `median_abs_error` | 流速中位數誤差 |
| `std` | `std_abs_error` | 流速誤差標準差 |

## 限制

目前資料來源是 `hotspot_points`，所以 API 回傳的是 hotspot/超標點。
如果未來要回傳所有格點，或要查某一點完整 24 小時曲線，即包含未超標時段，需要另外建立完整格點資料表。
