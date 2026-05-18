# S-111 API Data Version

更新日期：2026-05-14

補充更新：2026-05-18

```text
本次只更新流向誤差顯示顏色與交接文件。
資料庫、dump、hotspot_points 筆數、0.48 kn 門檻、median/std 計算邏輯都沒有重算。
direction warning  = #F8A718
direction critical = #7652E2
```

## 目前公開 API

Base URL:

```text
http://159.65.4.22
```

資料庫：`s111_verification`

資料日期範圍：

```text
2025-08-12 ~ 2026-04-10
```

## Official Hotspot

官方 hotspot 仍維持「主要預警」用途：

```text
speed official     = metric IS NULL, error_type = speed
direction official = metric IS NULL, error_type = direction
```

目前筆數：

```text
official speed     = 3,037,373
official direction = 155,781
```

官方 direction hotspot 的判斷方式：

```text
最低流速門檻：0.48 kn
流向誤差統計：median_dir / median_abs_dir_error
warning：30 deg
critical：45 deg
```

## Metric Hotspot

為了把老師提到的標準差一起提供給學長，API 也已經匯入 metric hotspot rows。

目前可查的 metric：

| API metric | DB metric | error_type | 用途 | 筆數 |
| --- | --- | --- | --- | ---: |
| `mean` | `mean_abs_error` | speed | 流速平均絕對誤差 | 24,755 |
| `median` | `median_abs_error` | speed | 流速中位數誤差 | 27,108 |
| `std` | `std_abs_error` | speed | 流速誤差標準差 | 147 |
| `mean_dir` | `mean_abs_dir_error` | direction | 流向平均絕對誤差 | 377,949 |
| `median_dir` | `median_abs_dir_error` | direction | 流向中位數誤差 | 155,781 |
| `std_dir` | `std_abs_dir_error` | direction | 流向誤差標準差，代表穩定度/離散度 | 652,623 |

metric hotspot 總筆數：

```text
1,238,363
```

## 給學長的主要 API

官方 direction hotspot：

```text
http://159.65.4.22/api/threshold-hotspots?date=2026-04-10&lead_hours=24&error_type=direction&threshold=30&limit=1000
```

流向誤差標準差 hotspot：

```text
http://159.65.4.22/api/threshold-hotspots?date=2026-04-10&lead_hours=24&error_type=direction&metric=std_dir&threshold=30&limit=1000
```

GeoJSON 版本：

```text
http://159.65.4.22/api/threshold-hotspots?date=2026-04-10&lead_hours=24&error_type=direction&metric=std_dir&threshold=30&format=geojson&limit=1000
```

## 0.6 kn 舊基準比較

舊基準：`0.6 kn + median_dir`

新基準：`0.48 kn + median_dir`

全資料集：

```text
0.6 kn + median_dir  = 51,174
0.48 kn + median_dir = 155,781
增加                  = 104,607
倍率                  = 3.04x
```

2026-04-10：

```text
0.6 kn + median_dir  = 56
0.48 kn + median_dir = 1,692
增加                  = 1,636
倍率                  = 30.21x
```

## 驗證結果

已確認公開 API 可回傳 `metric=std_dir`：

```text
GET /api/threshold-hotspots?date=2026-04-10&lead_hours=24&error_type=direction&metric=std_dir&threshold=30&limit=3
```

回傳資料包含：

```text
lon, lat, value, unit, error_type, severity, color, metric, target_date, lead_hours
```

`value` 代表 `std_abs_dir_error`，單位為 `deg`。
