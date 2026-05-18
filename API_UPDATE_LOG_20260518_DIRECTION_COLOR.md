# 2026-05-18 API / QGIS 顯示顏色更新紀錄

## 這次更新的目的

這次更新是為了讓「流向誤差」的 warning / critical 顏色更容易分辨。

原本流向誤差使用兩個藍色系：

```text
direction warning  = #4FC3F7
direction critical = #1565C0
```

在海圖或淺藍底圖上，兩者容易看起來太接近。
因此這次改成 S-111 標準色帶中差異較明顯的顏色：

```text
direction warning  = #F8A718  S-111 orange
direction critical = #7652E2  S-111 purple
```

## 有更新的內容

| 類型 | 更新內容 |
| --- | --- |
| QGIS plugin | `s111_viewer.py` 的流向 hotspot / 異常箭頭顏色常數 |
| API | `scripts/s111_api_server.py` 的 direction warning / critical 回傳顏色 |
| API 文件 | `API_HANDOFF_給學長.md`、`API_DRAWING_DATA_給學長.md` |
| API 範例 | `API_THRESHOLD_HOTSPOTS_FORMAT_給學長.json` |
| Obsidian | `PROJECT_ISSUE_LEDGER.md` 紀錄為 `VIS-003` |
| Google Drive | `06_API服務` 已同步新版 API 程式與文件 |
| Droplet | `http://159.65.4.22` 的 API 已部署新版顏色 |

## 沒有更新的內容

這次不是資料重算，因此沒有更新：

```text
資料庫資料表
資料庫 dump
hotspot_points 筆數
spatial_stats GeoJSON
daily_results 成果包
0.48 kn 門檻
median_dir / std_dir 計算邏輯
```

## 對使用者或學長的影響

學長前端如果使用 API 回傳的 `color` 欄位，就會自動拿到新版顏色。

範例：

```json
{
  "error_type": "direction",
  "severity": "warning",
  "color": "#F8A718"
}
```

```json
{
  "error_type": "direction",
  "severity": "critical",
  "color": "#7652E2"
}
```

QGIS plugin 重新載入圖層後，也會用新版顏色顯示流向誤差 warning / critical。

## 驗證紀錄

已完成：

```text
python -m py_compile s111_viewer.py scripts/s111_api_server.py
Droplet s111-api active
GET /api/status -> ok=true
direction warning API -> #F8A718
direction critical API -> #7652E2
Google Drive 06_API服務 無舊色碼 #4FC3F7 / #1565C0
```

## 對 GitHub 的建議

若要推到 GitHub，這次更新應該包含：

```text
s111_viewer.py
scripts/s111_api_server.py
API_HANDOFF_給學長.md
API_DRAWING_DATA_給學長.md
API_THRESHOLD_HOTSPOTS_FORMAT_給學長.json
API_UPDATE_LOG_20260518_DIRECTION_COLOR.md
```

不建議上 GitHub：

```text
資料庫 dump
大型 GeoJSON / daily_results 成果包
任何含密碼或本機環境資訊的 .env
```
