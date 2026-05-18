# S-111 PostgreSQL Database Handoff

這個資料夾提供 PostgreSQL 資料庫交接檔，給需要還原完整 DB 的人使用。

## 檔案

- `s111_verification_20260514_0p48_median_metrics.dump`
  - PostgreSQL custom-format dump。
  - 來源資料庫：`s111_verification`
  - 匯出日期：2026-05-14
  - 更新內容：流向誤差 hotspot 已改用 `0.48 kn` 最低流速門檻，官方 direction hotspot 採 `median_dir / median_abs_dir_error`，並加入 metric hotspot rows，包含 `std_dir / std_abs_dir_error`。
  - 檔案大小：104,281,893 bytes（約 99.4 MB）
  - SHA256：`53E53F88A370CF0E90DDFC0ECC264D9318A33F6F0ABA874A41C0B6C7C7009FAB`
  - 備註：已移除未使用的 root-mean-square error 相關欄位，保留 mean/median/std/bias/max/hotspot count。

- `restore_s111_verification.ps1`
  - Windows PowerShell 還原範例腳本。
  - 需要先安裝 PostgreSQL，並能找到 `createdb.exe` 與 `pg_restore.exe`。

## 資料表內容

| table | rows | 說明 |
| --- | ---: | --- |
| `summary_stats` | 2,736 | 每小時驗證統計，key 為 `target_date + target_timestamp + lead_hours` |
| `hotspot_points` | 4,431,517 | official speed/direction hotspot + metric hotspot 點位 |
| `thresholds` | 0 | 預留警示門檻設定 |
| `alert_log` | 0 | 預留警示紀錄 |

資料範圍：

- `summary_stats`：2025-08-12 到 2026-04-10
- `hotspot_points` official speed：2025-08-12 到 2026-04-10，共 3,037,373 筆
- `hotspot_points` official direction：2025-08-12 到 2026-04-10，共 155,781 筆（已套用 `0.48 kn` 流向誤差最低流速門檻，並採 `median_dir`）
- `hotspot_points` metric rows：共 1,238,363 筆，其中 `std_abs_dir_error` 共 652,623 筆。

## 還原方式

建議使用 PostgreSQL 16。

在這個資料夾開 PowerShell，執行：

```powershell
.\restore_s111_verification.ps1
```

如果電腦裡已經有 `s111_verification`，請選一種方式：

保留原本資料庫，還原成新名稱：

```powershell
.\restore_s111_verification.ps1 -DbName s111_verification_20260514_0p48_median_metrics
```

確認要覆蓋舊的 `s111_verification`：

```powershell
.\restore_s111_verification.ps1 -Overwrite
```

或手動執行：

```powershell
$env:PGPASSWORD="你的PostgreSQL密碼"
createdb -h localhost -p 5432 -U postgres s111_verification
pg_restore -h localhost -p 5432 -U postgres -d s111_verification ".\s111_verification_20260514_0p48_median_metrics.dump"
```

如果已經有同名資料庫，請先改資料庫名稱，或自行備份後再清掉舊資料。

## 注意

- 不建議只複製單一 `pg_dump.exe` 或 `pg_restore.exe` 執行，Windows 會缺 DLL，例如 `zlib1.dll`。
- 請使用 PostgreSQL 安裝後內建的 `pg_restore.exe`，或在 PostgreSQL 的 `bin` 目錄內執行。
- 若只是要看 GeoJSON，不需要還原 DB，直接看上一層的 `01_每日成果包`。
- 若要接 QGIS plugin 或重現資料庫查詢，請使用這個 `.dump` 還原。
