# S-111 Hotspot Threshold API

這份 API 只針對資料庫中的 hotspot/超標點。
目前也支援 `metric` 參數，可查老師提到的標準差圖層，例如 `metric=std_dir`。

流程是：

```text
設定 threshold -> 從 hotspot_points 抓超過門檻的點 -> 回傳 lon/lat/value/color -> 前端畫在地圖上
```

## 1. 抓超標點

```text
GET /api/threshold-hotspots?date=2026-04-10&lead_hours=24&error_type=speed&threshold=0.6&limit=1000
```

回傳 `rows` 是多筆點資料，不是一筆。

查流向誤差標準差，也就是穩定度/離散度較差的點：

```text
GET /api/threshold-hotspots?date=2026-04-10&lead_hours=24&error_type=direction&metric=std_dir&threshold=30&limit=1000
```

主要參數：

| 參數 | 說明 |
| --- | --- |
| `date` | 目標日期，格式 `YYYY-MM-DD` 或 `YYYYMMDD`；不填則取資料庫最新日期 |
| `lead_hours` | 預報時距，例如 `24`、`48`、`72` |
| `error_type` | `speed` 或 `direction` |
| `metric` | 可選；不填是官方 hotspot。可用 `median_dir`、`std_dir`、`mean_dir`、`median`、`std` |
| `threshold` | 只回傳 `value >= threshold` 的點；speed 單位是 `kn`，direction 單位是 `deg` |
| `critical_threshold` | 可選，決定 critical 顏色分級；speed 預設 `1.0`，direction 預設 `45` |
| `bbox` | 可選，限制經緯度框，格式 `min_lon,min_lat,max_lon,max_lat` |
| `limit` | 最多回傳幾筆，預設 `5000` |
| `offset` | 分頁起點 |
| `format` | `json` 或 `geojson`，預設 `json` |

## 2. 回傳欄位

每筆 `rows` 代表一個要畫在地圖上的點：

| 欄位 | 說明 |
| --- | --- |
| `id` | hotspot 點資料 ID，點選後查細節可用 |
| `lon` | 經度，QGIS / 前端 X 欄位 |
| `lat` | 緯度，QGIS / 前端 Y 欄位 |
| `value` | 誤差值，來源是資料庫 `error_value` |
| `unit` | 單位，`kn` 或 `deg` |
| `error_type` | `speed` 或 `direction` |
| `metric` | 若查 metric hotspot，會顯示實際資料庫欄位，例如 `std_abs_dir_error` |
| `layer_id` | 建議前端/QGIS 用來分圖層的 ID |
| `layer_name_zh` | 中文圖層名稱 |
| `layer_role` | 圖層用途，例如 official 或 diagnostic |
| `statistic` | 此圖層代表的統計指標 |
| `severity` | `warning` 或 `critical` |
| `color` | 建議繪圖顏色 |
| `target_date` | 目標日期 |
| `target_timestamp` | 目標時間 |
| `lead_hours` | 預報時距 |

範例：

```json
{
  "id": 119051239,
  "lon": 120.295,
  "lat": 26.345,
  "value": 0.608061254,
  "unit": "kn",
  "error_type": "speed",
  "layer_id": "official_speed_hotspots",
  "layer_name_zh": "正式流速誤差 hotspot",
  "layer_role": "official_speed_hotspot",
  "statistic": "speed_abs_error",
  "severity": "warning",
  "color": "#FFD700",
  "target_date": "2026-04-10",
  "target_timestamp": "2026-04-10T00:00:00",
  "lead_hours": 24
}
```

`std_dir` 範例：

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

API 也會在最外層回傳 `layer`，用來說明這次查詢整體屬於哪一個圖層。資料庫仍維持一張 `hotspot_points`，前端或 QGIS 顯示時再依 `layer_id` 分層。

## 3. QGIS / 地圖繪圖設定

```text
geometry = Point
crs = EPSG:4326
x_field = lon
y_field = lat
value_field = value
color_field = color
```

顏色規則：

| 類型 | 等級 | 預設門檻 | 顏色 |
| --- | --- | --- | --- |
| speed | warning | 0.5-1.0 kn | `#FFD700` |
| speed | critical | >= 1.0 kn | `#FF0000` |
| direction | warning | 30-45 deg | `#F8A718` |
| direction | critical | >= 45 deg | `#7652E2` |

## 4. 點選後查資料

前端畫出 threshold hotspot 點後，使用者點某個點，可以用該點 `id` 查時間資料：

```text
GET /api/hotspot-series?id=119051239
```

如果這個 id 來自 `metric=std_dir` 的點，API 會自動沿用該點的 `std_abs_dir_error`，不會跳回官方 hotspot。

也可以用經緯度找最近的 hotspot 點：

```text
GET /api/hotspot-series?lon=120.295&lat=26.345&date=2026-04-10&lead_hours=24&error_type=speed&radius_deg=0.02
```

曲線欄位：

```text
x_field = target_timestamp
y_field = value
unit_field = unit
color_field = color
```

注意：目前 `hotspot-series` 是從 `hotspot_points` 查，所以只會回傳該點有出現在 hotspot/超標資料表的時間。若未來要完整 24 小時所有格點曲線，需要另外儲存完整格點資料。
