# S-111 Hotspot 圖層切分說明

這份文件記錄目前的決定：資料庫不用把 hotspot 拆成很多張表，但 API、GeoJSON、QGIS 或前端顯示時，要把 hotspot 當成不同圖層來看。

## 核心結論

```text
資料庫：維持一張 hotspot_points
顯示端：依 error_type + metric + severity 分圖層
```

這樣做的原因是：

- 資料庫比較乾淨，不會因為每多一種指標就多一張表。
- API 可以用參數切出前端需要的資料。
- QGIS 或網頁可以依 `layer_id` 決定要畫哪一層。

## 前端應該怎麼分

建議把下面幾種圖層分開：

| 圖層 | API 查詢方式 | 用途 |
| --- | --- | --- |
| 正式流速 hotspot | `error_type=speed&metric=official` 或不填 `metric` | 流速誤差超標點 |
| 正式流向 hotspot | `error_type=direction&metric=official` 或不填 `metric` | 0.48 kn 流速門檻後，流向中位數誤差超標點 |
| 流向 STD hotspot | `error_type=direction&metric=std_dir` | 看模型穩定度/離散度差的地方 |
| 流向 mean hotspot | `error_type=direction&metric=mean_dir` | 輔助比較平均誤差 |
| 流速 median/std hotspot | `error_type=speed&metric=median` 或 `metric=std` | 輔助比較流速統計指標 |

重要：`hotspot_points.metric IS NULL` 才是正式 hotspot。`metric=std_dir`、`metric=mean_dir` 這類是診斷用圖層，不是取代正式主線。

## API 已補上的 layer metadata

`/api/threshold-hotspots`、`/api/drawing-data`、`/api/hotspots` 都會在回傳中帶 `layer`。每筆 `rows` 或 GeoJSON feature properties 也會帶 `layer_id` 等欄位。

範例：

```json
{
  "layer_id": "official_direction_median_hotspots",
  "layer_name": "Official Direction Median Hotspots",
  "layer_name_zh": "正式流向中位數誤差 hotspot",
  "layer_role": "official_direction_hotspot",
  "statistic": "median_abs_dir_error",
  "unit": "deg",
  "speed_gate_kn": 0.48,
  "value_meaning": "official direction median absolute error after the 0.48 kn speed gate"
}
```

前端可以直接用：

```text
layer_id -> 決定圖層名稱
color -> 決定點顏色
lon / lat -> 決定點位置
value -> 顯示誤差值
unit -> 顯示單位
```

## 查詢範例

正式流速 hotspot：

```text
http://159.65.4.22/api/threshold-hotspots?date=2026-04-10&lead_hours=24&error_type=speed&threshold=0.6&limit=1000
```

正式流向 hotspot：

```text
http://159.65.4.22/api/threshold-hotspots?date=2026-04-10&lead_hours=24&error_type=direction&threshold=30&limit=1000
```

流向 STD hotspot：

```text
http://159.65.4.22/api/threshold-hotspots?date=2026-04-10&lead_hours=24&error_type=direction&metric=std_dir&threshold=30&limit=1000
```

GeoJSON 版：

```text
http://159.65.4.22/api/threshold-hotspots?date=2026-04-10&lead_hours=24&error_type=direction&metric=std_dir&threshold=30&format=geojson&limit=1000
```

## 跟箭頭圖層的差別

| 資料 | 代表什麼 | 是否是 hotspot |
| --- | --- | --- |
| 原始箭頭 | 海流本身的流速、流向 | 否 |
| spatial stats GeoJSON | 每個格點的 mean/median/std 統計結果 | 不一定 |
| hotspot API | 超過門檻、值得注意的點 | 是 |

`hotspot_points.direction` 是輔助欄位，代表參考流向；真正用來判斷流向 hotspot 的值是 `error_value`，正式流向主線代表 `median_abs_dir_error`。

## 目前 GeoJSON 與箭頭的判讀規則

目前流向 spatial stats GeoJSON 是「全部有效格點」的空間統計結果，不是只保留超標點。

```text
spatial stats GeoJSON = 所有可計算的有效格點
hotspot GeoJSON / hotspot API = 超過門檻後被挑出的點
```

流向 spatial stats GeoJSON 中的 `median_abs_dir_error`、`mean_abs_dir_error`、`std_abs_dir_error` 是在有效流速條件下計算；目前流向誤差的最低流速門檻是 `0.48 kn`。也就是說，流速太小、方向不穩的樣本不拿來當流向誤差判斷依據。

箭頭圖層本身是輔助判讀流場用的視覺化：箭頭方向來自流向欄位，箭頭大小來自流速欄位。如果是「異常箭頭」或 hotspot 顯示，才會再依 warning/critical 門檻做分色或篩選。

## 目前決定

- 不把 `hotspot_points` 拆成多張資料庫表。
- API 回傳加入 `layer_id`、`layer_name`、`layer_name_zh`、`layer_role`、`statistic`。
- 學長前端若要顯示不同圖層，使用 `layer_id` 分層即可。
- 若未來要完整熱度圖或完整 24 小時曲線，需要新增「完整格點資料表」，那是另一個功能，不屬於現在 hotspot API。
