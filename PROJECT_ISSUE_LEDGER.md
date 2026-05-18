# Project Issue Ledger

Last updated: 2026-05-18 11:49 +08:00

## Layer 0: Snapshot

- Current focus: Direction-error warning/critical color update has been synced to Droplet API, Google Drive handoff files, and Obsidian while keeping the S-111 arrow symbol shape.
- Open issues: None.
- In progress: None.
- Recently resolved: DB-000, DB-001, DB-002, DB-003, DB-004, API-001, API-002, API-003, API-004, API-005, API-006, API-007, API-008, API-009, DEPLOY-001, DOC-001, DOC-002, THESIS-001, VIS-001, VIS-002, VIS-003, METRIC-001, VALID-001.
- Main blocker: None for the currently checked database path.
- Recommended next step: Share `API_HOTSPOT_LAYER_SPLIT_GUIDE.md` with the senior and tell them to split map layers by `layer_id`; use `s111_verification_20260514_0p48_median_metrics.dump` for restored DB handoff.

## Layer 1: Issue Index

| ID | Status | Area | Title | Last Evidence | Next Step |
| --- | --- | --- | --- | --- | --- |
| DB-000 | resolved | Database | PostgreSQL connection and required tables verified | `summary_stats` and `hotspot_points` exist with required columns | Keep DB config documented |
| DB-001 | resolved | Database | Database summary text now uses latest whole-day aggregation | SQL returned 24 hourly points for each lead on 2026-04-10 | Keep summary and hotspot layers aligned as whole-day output |
| DB-002 | resolved | Database | Hotspot query loads whole-day hotspots by design | User confirmed whole-day hotspot display is intended | Keep whole-day behavior; do not add timestamp filter |
| DB-003 | resolved | Database | Direction hotspot data caught up to latest speed hotspot date | Backfill confirmed direction and speed hotspot max date are both 2026-04-10 | Keep package-hotspot DB writer for future runs |
| DB-004 | resolved | Pipeline | Pipeline summary write now uses hourly upsert key | Transaction test accepted `ON CONFLICT (target_date, target_timestamp, lead_hours)` and rolled back cleanly | Verify with the next real pipeline run |
| API-001 | resolved | API | Read-only HTTP API exposes verification summary and hotspot GeoJSON | Local server returned `/api/status`, `/api/summary`, `/api/hotspot-summary`, and `/api/hotspots` successfully | Decide deployment scope and add auth before any public exposure |
| API-002 | resolved | API | API omits null fields by default and supports full debug output | `/api/summary` returned no null values by default; `include_nulls=true` still returned full columns | Keep default response clean for handoff users |
| API-003 | resolved | API | API supports bbox-based spatial monitoring queries | `/api/area-monitoring?bbox=119,21,120,23...` returned in-range monitoring summary and `/api/hotspots` returned bbox-filtered GeoJSON | Confirm with senior whether bbox is enough or true polygon cell clipping is required |
| API-004 | resolved | API | API supports ENC chart cell ID lookup and monitoring | `/api/cells?cell_id=1U319210` returned ENC metadata; `/api/cell-monitoring?cell_id=1U319220...` returned monitoring summary | Confirm whether bbox-per-cell is enough or exact polygon clipping is required |
| API-005 | resolved | API | API exposes threshold-filtered drawing rows and click detail | `/api/threshold-hotspots?...threshold=0.6` returned only values >= 0.6; `/api/hotspot-series?id=...` returned same-point time rows | Ask senior to confirm the row shape and whether hotspot-only time rows are enough |
| API-006 | resolved | API | Public handoff API removes chart-cell/product-ID traces | `rg` found no `cell_id`, `productID`, `ENC`, or chart-cell endpoints in API script and handoff folder | Keep handoff docs focused on threshold hotspot workflow |
| API-007 | resolved | API | API exposes metric hotspot layers including direction STD | Public `/api/threshold-hotspots?...metric=std_dir...` returned `std_abs_dir_error` rows; DB has 1,238,363 metric rows | Share metric examples with senior |
| API-008 | resolved | Pipeline/API | Unneeded squared-error metric removed from active outputs | `py_compile` passed; active output paths no longer expose the metric | Re-export/redeploy if the public API process or DB dump must reflect this immediately |
| API-009 | resolved | API/Docs | Hotspot display layers explicitly split without changing DB storage | API rows/GeoJSON now include `layer_id`, `layer_name_zh`, `layer_role`, and `statistic`; Obsidian guide added | Share layer guide with senior |
| DEPLOY-001 | resolved | Deployment | Droplet deployment files prepared | `py_compile` passed and `scripts.s111_api_server:create_app()` imported successfully | Use the Droplet docs page for API copy/test |
| DOC-001 | resolved | API Docs | Web API docs page added | `http://159.65.4.22/docs` returned HTTP 200 with copyable endpoint URLs | Share `/docs` with senior for quick testing |
| DOC-002 | resolved | Obsidian | Obsidian S-111 notes synced to metric-hotspot version | Obsidian search found no old no-metric dump name or old SHA; latest docs include `std_dir`, `4,431,517`, and `median_metrics` | Keep Obsidian docs updated after future DB/API changes |
| PERF-001 | watch | Database | Hotspot lookup could benefit from a composite index | Existing index covers date and lead, then filters `error_type` | Add index after deciding timestamp behavior |
| THESIS-001 | resolved | Thesis | Percentile meaning confirmed as spatial ranking | User confirmed issue 1 is completed | Use wording in thesis/method section |
| VIS-001 | resolved | Visualization | PNG legend shows error value and cumulative percentage | User confirmed issue 2 is completed | Keep PNG/screenshot legend readable |
| VIS-002 | resolved | Visualization | Spatial statistic workflow will use plugin-loaded GeoJSON | User confirmed QGIS plugin import and screenshots are the intended thesis workflow | Do not prioritize automated PNG export |
| VIS-003 | resolved | Visualization/API | Direction-error warning/critical colors made more distinguishable | QGIS/API constants now use direction warning `#F8A718` and critical `#7652E2`; S-111 arrow symbol unchanged | Use the new colors in screenshots and handoff |
| METRIC-001 | resolved | Method | Direction-error speed threshold decided and rebuilt | Local/remote DB and handoff GeoJSON now use `0.48 kn + median_dir`; direction rows are 155,781 | Use this basis in thesis text and future runs |
| VALID-001 | resolved | Validation | Spatial-stat validation reports created for 24h/48h/72h | HDF5 recomputation matched CSV within floating-point tolerance for all three leads | Repeat on another date only if broader thesis QA is required |
| CASE-001 | watch | Case Study | Typhoon track image exists for thesis context | `C:\Users\Rong\Desktop\論文參考資料\圖片\楊柳.png` confirmed present | Use it when composing the case-study figure/caption |
| PROD-001 | watch | Workflow | Experimental validation kept separate from production | Validation script created as research QA helper only | Keep production outputs limited to confirmed workflow |

## Layer 2: Issue Cards

### DB-000 - PostgreSQL Connection And Required Tables Verified

- Status: resolved
- Area: Database
- First seen: 2026-05-04
- Last updated: 2026-05-04 17:26 +08:00
- Symptom: Need to confirm whether the plugin can connect to the configured database and whether expected tables exist.
- Impact: Without this, DB hotspot loading could fail before reaching query logic.
- Likely cause: N/A.
- Next action: Keep connection settings and schema assumptions visible when changing DB code.

#### Evidence Trail

- 2026-05-04 16:13 +08:00 - Python found `psycopg2`.
- 2026-05-04 16:13 +08:00 - Connected to `s111_verification` as `postgres` on `localhost:5432`.
- 2026-05-04 16:13 +08:00 - `summary_stats` exists with 2736 rows and all required plugin columns.
- 2026-05-04 16:13 +08:00 - `hotspot_points` exists with 27498137 rows and all required plugin columns.

#### Decision And Verification

- 2026-05-04 16:13 +08:00 - Marked resolved because connection, table presence, and required columns were verified by read-only queries.

### DB-001 - Database Summary Text Now Uses Latest Whole-Day Aggregation

- Status: resolved
- Area: Database
- First seen: 2026-05-04
- Last updated: 2026-05-04 16:52 +08:00
- Symptom: The UI said it loaded latest database verification results, but the old SQL only selected one row per lead from the latest date.
- Impact: The text summary could describe one hour while the hotspot map displayed whole-day hotspot data.
- Likely cause: `load_hotspots_from_db()` used `DISTINCT ON (lead_hours)` with `ORDER BY lead_hours, target_date DESC`, but the table has hourly rows.
- Next action: None for this issue. Keep whole-day summary and whole-day hotspot layers aligned.

#### Evidence Trail

- 2026-05-04 16:13 +08:00 - `summary_stats` has 24 rows per lead for target date `2026-04-10`.
- 2026-05-04 16:13 +08:00 - The exact plugin-style query returned `2026-04-10 12:00` for 24h, `17:00` for 48h, and `07:00` for 72h.
- 2026-05-04 16:13 +08:00 - Maximum `target_timestamp` for each lead on the latest date is `2026-04-10 23:00`.
- 2026-05-04 16:52 +08:00 - Updated `s111_viewer.py` so `load_hotspots_from_db()` aggregates all rows on the latest `target_date` by `lead_hours`.
- 2026-05-04 16:52 +08:00 - New SQL returned latest date `2026-04-10` with 24 hourly points from `00:00` to `23:00` for 24h, 48h, and 72h.

#### Decision And Verification

- 2026-05-04 16:52 +08:00 - Marked resolved after `python -m py_compile .\s111_viewer.py` passed and the aggregate SQL returned whole-day rows from the live database.

### DB-002 - Hotspot Query Loads Whole-Day Hotspots By Design

- Status: resolved
- Area: Database
- First seen: 2026-05-04
- Last updated: 2026-05-04 16:45 +08:00
- Symptom: Hotspot layers are queried by `target_date`, `lead_hours`, and `error_type`, but not by `target_timestamp`.
- Impact: This means the map shows all hotspot points for the selected day and lead time.
- Likely cause: `load_hotspots_from_db()` intentionally filters by day and lead only.
- Next action: Keep this behavior unless the user later asks for a single-hour hotspot view.

#### Evidence Trail

- 2026-05-04 16:13 +08:00 - Latest `hotspot_points` date has 24 distinct timestamps per speed lead.
- 2026-05-04 16:13 +08:00 - Latest `2026-04-10` speed groups are 12001 points for 24h, 11122 for 48h, and 12966 for 72h across the whole day.
- 2026-05-04 16:45 +08:00 - User confirmed the intended behavior is to use whole-day/all hotspot data.

#### Decision And Verification

- 2026-05-04 16:45 +08:00 - Marked resolved because whole-day loading is confirmed as the intended product behavior.

### DB-003 - Direction Hotspot Data Is Older Than Speed Hotspot Data

- Status: resolved
- Area: Database
- First seen: 2026-05-04
- Last updated: 2026-05-04 18:12 +08:00
- Symptom: Latest speed hotspots are available for `2026-04-10`, but latest direction hotspots stop at `2026-03-23`.
- Impact: The DB loader may create speed layers for recent dates but no direction layers.
- Likely cause: Recent pipeline outputs may not be writing direction hotspot rows, or direction export may be disabled for the latest runs.
- Next action: Keep the package-hotspot DB writer in use for future runs.

#### Evidence Trail

- 2026-05-04 16:13 +08:00 - `hotspot_points` max date by `error_type`: `speed` is `2026-04-10`, `direction` is `2026-03-23`.
- 2026-05-04 16:13 +08:00 - Hourly direction aggregate columns had values for latest rows, but direction aggregate hotspot count fields were null.
- 2026-05-04 18:12 +08:00 - `daily_results\20260410\20260410_hotspots.csv` contains 36,089 speed rows and 133,592 direction rows, so the data existed before DB backfill.
- 2026-05-04 18:12 +08:00 - Root cause found: the DB writer was looking for result packages beside the H5 path instead of under `daily_results`, so package hotspot rows were not being imported.
- 2026-05-04 18:12 +08:00 - Updated `verification_pipeline.py` to resolve result packages through `RESULT_PACKAGE_ROOT` with fallback to the H5 sibling `daily_results` directory, and to write package `hotspots.csv` rows into `hotspot_points`.
- 2026-05-04 18:12 +08:00 - Updated `s111_viewer.py` DB hotspot query to use `metric IS NULL`, keeping official hotspot rows separate from metric-specific rows.
- 2026-05-04 18:12 +08:00 - Backfilled 1,507,428 hotspot rows from available packages dated 2026-03-24 through 2026-04-10.
- 2026-05-04 18:12 +08:00 - Verification query now shows `metric IS NULL` hotspot max date is `2026-04-10` for both `speed` and `direction`; for 2026-04-10 counts are speed 36,089 and direction 133,592.

#### Decision And Verification

- 2026-05-04 16:13 +08:00 - Classified as `watch` because this may be expected data coverage rather than a confirmed code defect.
- 2026-05-04 18:12 +08:00 - Marked resolved after code changes, successful `py_compile`, DB backfill, and max-date verification.

### DB-004 - Pipeline Upsert Conflict Target Does Not Match Live Unique Constraint

- Status: resolved
- Area: Pipeline
- First seen: 2026-05-04
- Last updated: 2026-05-04 18:02 +08:00
- Symptom: `verification_pipeline.py` writes summary rows with an `ON CONFLICT` target that does not match the live table constraint.
- Impact: Running the pipeline DB write path may fail when PostgreSQL cannot find a matching unique or exclusion constraint.
- Likely cause: The live table evolved to hourly uniqueness, but the pipeline still has a daily-only upsert target.
- Next action: Verify with the next real pipeline run that hourly rows are inserted/updated as expected.

#### Evidence Trail

- 2026-05-04 16:13 +08:00 - Live unique constraint is `UNIQUE (target_date, target_timestamp, lead_hours)`.
- 2026-05-04 16:13 +08:00 - `verification_pipeline.py` uses `ON CONFLICT (target_date, lead_hours)`.
- 2026-05-04 16:13 +08:00 - `summary_stats.target_timestamp` has no nulls.
- 2026-05-04 17:26 +08:00 - Live `summary_stats` has 2736 rows, 2736 distinct `(target_date, target_timestamp, lead_hours)` keys, but only 114 distinct `(target_date, lead_hours)` keys; this confirms the live table is hourly, not daily lead-level.
- 2026-05-04 17:26 +08:00 - Code inspection shows `verification_pipeline.py` creates `UNIQUE (target_date, lead_hours)` around line 1191 and inserts without `target_timestamp` around lines 1411-1419.
- 2026-05-04 18:02 +08:00 - Updated `verification_pipeline.py` so `summary_stats` schema includes `target_timestamp`, the hourly uniqueness is `(target_date, target_timestamp, lead_hours)`, and old daily uniqueness is removed if present.
- 2026-05-04 18:02 +08:00 - Updated `write_to_database()` to write one row per `target_time` and lead instead of aggregating 24 hours into one daily row.
- 2026-05-04 18:02 +08:00 - PostgreSQL transaction test accepted an insert using `ON CONFLICT (target_date, target_timestamp, lead_hours)` and was rolled back.

#### Decision And Verification

- 2026-05-04 16:13 +08:00 - Left open; no migration or code change applied yet.
- 2026-05-04 18:02 +08:00 - Marked resolved after `python -m py_compile .\verification_pipeline.py` passed and the live database accepted the new hourly conflict target in a rollback test.

### PERF-001 - Hotspot Lookup Could Benefit From A Composite Index

- Status: watch
- Area: Database
- First seen: 2026-05-04
- Last updated: 2026-05-04 16:13 +08:00
- Symptom: Hotspot table is large and the lookup filters `error_type` after using a date/lead index.
- Impact: Loading DB hotspot layers may become slow, especially for direction data or timestamp-specific queries.
- Likely cause: Existing index covers `(target_date, lead_hours)` but not `error_type` or `target_timestamp`.
- Next action: After DB-002 is decided, add a composite index matching the final query shape.

#### Evidence Trail

- 2026-05-04 16:13 +08:00 - `hotspot_points` has 27498137 rows.
- 2026-05-04 16:13 +08:00 - Existing indexes include `(target_date, lead_hours)` and `(metric)`.
- 2026-05-04 16:13 +08:00 - `EXPLAIN` used `idx_hotspots_date_lead` and then filtered by `error_type`.

#### Decision And Verification

- 2026-05-04 16:13 +08:00 - Classified as `watch` until the final query behavior is chosen.

### THESIS-001 - Percentile Meaning Confirmed As Spatial Ranking

- Status: resolved
- Area: Thesis
- First seen: 2026-05-04
- Last updated: 2026-05-04 17:15 +08:00
- Symptom: The percentile in the current figure is not clearly defined.
- Impact: Readers may not know whether the percentage means rank, cumulative spatial point count, or something else.
- Likely cause: The figure/legend uses percentile language without explaining the denominator and accumulation method.
- Next action: Use the confirmed definition in thesis text: percentile is spatial ranking among valid grid cells for the selected map/statistic.

#### Evidence Trail

- 2026-05-04 16:56 +08:00 - Advisor asked whether percentile means examples like 50 of 2000 points, 200 of 2000 points, and whether 100% below 0.45 kt means all points have error below 0.45 kt.
- 2026-05-04 17:15 +08:00 - User confirmed issue 1 is completed.

#### Decision And Verification

- 2026-05-04 17:15 +08:00 - Marked resolved by user confirmation and code inspection of `_compute_percentile_array()`.

### VIS-001 - PNG Legend Shows Error Value And Cumulative Percentage

- Status: resolved
- Area: Visualization
- First seen: 2026-05-04
- Last updated: 2026-05-04 17:15 +08:00
- Symptom: The current legend/color scale does not clearly show what error value each color represents.
- Impact: The reader cannot interpret whether a color means high error, what value it corresponds to, or what cumulative percentage it covers.
- Likely cause: Current legend emphasizes percentile/color but not the actual error value and unit.
- Next action: Keep the screenshot/PNG legend readable when preparing thesis figures.

#### Evidence Trail

- 2026-05-04 16:56 +08:00 - Advisor said the legend must let people see "this color corresponds to how much error" and then show cumulative spatial percentage.
- 2026-05-04 16:56 +08:00 - Advisor suggested a dynamic color scale from light to yellow/orange/red, with labels like value and cumulative percentage.
- 2026-05-04 17:15 +08:00 - User confirmed issue 2 is completed.

#### Decision And Verification

- 2026-05-04 17:15 +08:00 - Marked resolved by user confirmation; exported PNG legend already contains `Value` and `Pct`.

### VIS-002 - Spatial Statistic Workflow Will Use Plugin-Loaded GeoJSON

- Status: resolved
- Area: Visualization
- First seen: 2026-05-04
- Last updated: 2026-05-04 17:15 +08:00
- Symptom: A bottom curve or fully averaged plot hides spatial information and gives little useful interpretation.
- Impact: The figure cannot show where errors concentrate or which areas need attention.
- Likely cause: Averaging all points/times collapses spatial distribution into a small value such as 0.1 kt.
- Next action: Use generated GeoJSON in the QGIS plugin and capture thesis screenshots manually.

#### Evidence Trail

- 2026-05-04 16:56 +08:00 - Advisor said the bottom averaged curve has little reference value and should not be used.
- 2026-05-04 16:56 +08:00 - Advisor repeatedly asked whether each map value is a single hour, maximum, median, mean, or another statistic.
- 2026-05-04 17:15 +08:00 - User confirmed the intended workflow is to import generated GeoJSON into the QGIS plugin and take manual thesis screenshots; automated PNG export is not the priority.

#### Decision And Verification

- 2026-05-04 17:15 +08:00 - Marked resolved by workflow confirmation; QGIS plugin supports spatial metric selection and GeoJSON/QML sidecar loading.

### VIS-003 - Direction-Error Warning/Critical Colors Made More Distinguishable

- Status: resolved
- Area: Visualization/API
- First seen: 2026-05-18
- Last updated: 2026-05-18 11:12 +08:00
- Symptom: Direction-error warning and critical arrows used two blue-family colors that looked too similar on map backgrounds.
- Impact: Warning and critical direction-error points could be hard to distinguish in QGIS screenshots and API-driven web maps.
- Likely cause: Earlier direction colors were chosen as light blue and dark blue; both carried the same hue family.
- Next action: Use the updated direction colors for future screenshots, API handoff examples, and QGIS reviews.

#### Evidence Trail

- 2026-05-18 11:12 +08:00 - Updated `s111_viewer.py` so direction warning uses S-111 orange `#F8A718` and direction critical uses S-111 purple `#7652E2`.
- 2026-05-18 11:12 +08:00 - Updated `scripts/s111_api_server.py` so API `color` and `qgis_symbol` match the QGIS plugin constants.
- 2026-05-18 11:12 +08:00 - Updated handoff docs and the threshold-hotspot JSON example with the same colors.

#### Decision And Verification

- 2026-05-18 11:12 +08:00 - Kept the S-111 arrow symbol shape; only warning/critical colors changed.
- 2026-05-18 11:12 +08:00 - `python -m py_compile .\s111_viewer.py .\scripts\s111_api_server.py` passed.
- 2026-05-18 11:12 +08:00 - Deployed `scripts/s111_api_server.py` to Droplet and restarted `s111-api`; service state returned `active`.
- 2026-05-18 11:12 +08:00 - Public API query confirmed direction warning returns `color=#F8A718` and direction critical returns `color=#7652E2`.
- 2026-05-18 11:49 +08:00 - Re-synced `s111_api_server.py`, `API_HANDOFF_給學長.md`, `API_DRAWING_DATA_給學長.md`, and `API_THRESHOLD_HOTSPOTS_FORMAT_給學長.json` to Google Drive `06_API服務`.
- 2026-05-18 11:49 +08:00 - Re-deployed Droplet API and verified `/api/status` returned `ok=true`; warning/critical direction color queries still returned `#F8A718` and `#7652E2`.
- 2026-05-18 11:56 +08:00 - Added `API_UPDATE_LOG_20260518_DIRECTION_COLOR.md` so the handoff package explicitly states what changed, what did not change, verification results, and recommended GitHub scope.
- 2026-05-18 11:56 +08:00 - Updated `API_HANDOFF_給學長.md` and `API_DATA_VERSION_20260514.md` to point readers to the color-update log and clarify that no database or GeoJSON recomputation was performed.

### METRIC-001 - Direction-Error Speed Threshold Decided By Median Retention

- Status: resolved
- Area: Method
- First seen: 2026-05-04
- Last updated: 2026-05-14 08:30 +08:00
- Symptom: The threshold-retention chart was being discussed without clearly stating that it targeted the flow-speed gate for direction-error monitoring.
- Impact: The thesis could justify the wrong question, or confuse the direction-error speed gate with the API hotspot threshold.
- Likely cause: The meeting discussion mixed general metric selection, API filtering, and the direction-error speed-threshold problem.
- Next action: Use `median_dir_count` and `0.48 kn` in the thesis method text; rerun/backfill packages only if historical outputs must reflect the new gate.

#### Evidence Trail

- 2026-05-04 16:56 +08:00 - Advisor said the thesis cannot just try 0.2, 0.3, 0.4 without a method or turning point rationale.
- 2026-05-04 16:56 +08:00 - Advisor suggested considering mean plus standard deviation, median, maximum absolute error, and literature-backed verification practices.
- 2026-05-04 17:15 +08:00 - User confirmed candidate indicators should simply be stored for now.
- 2026-05-14 08:30 +08:00 - Advisor correction clarified that the chart addresses the flow-speed threshold for direction-error monitoring.
- 2026-05-14 08:30 +08:00 - Advisor recommended `median` as the basis and `0.48 kn` as the final speed threshold because CV is greater than 1 and the mean is sensitive to outliers.
- 2026-05-14 08:30 +08:00 - Added `THESIS_DIRECTION_SPEED_THRESHOLD_DECISION.md` documenting the corrected rationale and thesis wording.
- 2026-05-14 08:58 +08:00 - Rebuilt 42 daily result packages from existing `spatial_stats` with the `0.48 kn` gate; regenerated official direction hotspots and per-metric hotspot GeoJSON files.
- 2026-05-14 08:58 +08:00 - Local DB `hotspot_points` now has 3,415,322 rows: 3,037,373 speed and 377,949 direction.
- 2026-05-14 08:58 +08:00 - Droplet DB and `http://159.65.4.22/api/status` report the same speed/direction row counts.
- 2026-05-14 08:58 +08:00 - Synced updated handoff GeoJSON files to Google Drive: 43 daily hotspot GeoJSON files and 114 metric hotspot GeoJSON files.
- 2026-05-14 08:58 +08:00 - Exported updated DB dump `s111_verification_20260514_0p48.dump`; SHA256 `355BEAD29B2C9709670D4DB85FE9383FFA5680D08BC2431BE9BD90AF983A82DE`.
- 2026-05-14 09:53 +08:00 - Corrected the official direction hotspot basis from `mean_dir` to `median_dir` after user clarified the advisor's intent.
- 2026-05-14 09:53 +08:00 - Rebuilt local packages, local DB, Droplet DB/API, Google Drive handoff GeoJSON, and dump again with `0.48 kn + median_dir`.
- 2026-05-14 09:53 +08:00 - Final DB `hotspot_points` counts are 3,193,154 total rows: 3,037,373 speed and 155,781 direction.
- 2026-05-14 09:53 +08:00 - Fair comparison against old `0.6 kn + median_dir`: direction rows increased from 51,174 to 155,781.
- 2026-05-14 09:53 +08:00 - Exported no-metric median dump `s111_verification_20260514_0p48_median.dump`; SHA256 `B182EE190F35E17C9F35A0C0AF2FB0CC00FD91661BA8021EA46F756EEC77A0F3`.
- 2026-05-14 17:05 +08:00 - Superseded the no-metric median dump with `s111_verification_20260514_0p48_median_metrics.dump`; SHA256 `53E53F88A370CF0E90DDFC0ECC264D9318A33F6F0ABA874A41C0B6C7C7009FAB`.
- 2026-05-15 00:00 +08:00 - Sensitivity check for the 2025-08-15 typhoon case: at `0.48 kn`, all-data median direction hotspots = 155,781, excluding 2025-08-12 through 2025-08-15 = 149,702, typhoon-period contribution = 6,079 (3.90%); retention changes from 9.24% to 9.03%, so the selected gate is not dominated by the case.
- 2026-05-14 09:56 +08:00 - Added `API_DATA_VERSION_20260514.md` and synced API files to Google Drive `06_API服務`.
- 2026-05-14 09:56 +08:00 - Uploaded API script and data-version note to Droplet `/opt/s111_viewer`, ran remote `py_compile`, restarted `s111-api`, and verified `/api/status` plus `/docs`.

#### Decision And Verification

- 2026-05-04 17:15 +08:00 - Moved to watch; no final metric decision required at this step.
- 2026-05-14 08:30 +08:00 - Marked resolved for the direction-error speed-threshold decision; `verification_pipeline.py` default `S111_DIR_HOTSPOT_MIN_TRUTH_SPEED_KN` changed from `1.0` to `0.48`.
- 2026-05-14 08:58 +08:00 - Verified rebuild by querying local and remote PostgreSQL plus remote API: latest `2026-04-10` direction counts are 4,744 for 24h, 5,127 for 48h, and 5,726 for 72h.
- 2026-05-14 09:53 +08:00 - Superseded the 08:58 mean-dir rebuild; final verified latest `2026-04-10` median-dir direction counts are 287 for 24h, 625 for 48h, and 780 for 72h.

### VALID-001 - Verify Every Computed Count And Statistic Step By Step

- Status: resolved
- Area: Validation
- First seen: 2026-05-04
- Last updated: 2026-05-04 17:20 +08:00
- Symptom: Some counts such as median/mean/std direction-error threshold exceedances need independent checking.
- Impact: If an early statistic is wrong, later maps, tables, and thesis conclusions may all need rework.
- Likely cause: Too many derived metrics are being generated before each calculation is individually verified.
- Next action: None for the 2025-08-15 three-lead spatial-stat validation set; repeat on another date only if broader thesis QA is required.

#### Evidence Trail

- 2026-05-04 16:56 +08:00 - Advisor asked to verify numbers like median over 30 degrees, mean over 30 degrees, and standard deviation over 30 degrees before continuing.
- 2026-05-04 17:15 +08:00 - Created `scripts/validate_spatial_stats.py`, a research QA helper that directly reads HDF5 scalar values and independently recomputes sampled grid-cell statistics.
- 2026-05-04 17:15 +08:00 - Generated `VALIDATION_SPATIAL_STATS_20250815_24H.md` for the 2025-08-15 24h typhoon case.
- 2026-05-04 17:15 +08:00 - Validation result: maximum sampled statistic difference was `6.52233046594e-06`; maximum percentile-rank difference was `3.70864195531e-06`.
- 2026-05-04 17:20 +08:00 - Generated `VALIDATION_SPATIAL_STATS_20250815_48H.md`; maximum sampled statistic difference was `7.8114783264e-06`; maximum percentile-rank difference was `3.63881673593e-06`.
- 2026-05-04 17:20 +08:00 - Generated `VALIDATION_SPATIAL_STATS_20250815_72H.md`; maximum sampled statistic difference was `5.8424155327e-06`; maximum percentile-rank difference was `2.52161304104e-06`.

#### Decision And Verification

- 2026-05-04 17:15 +08:00 - Kept in progress because one convincing validation report existed, but additional leads/cases were still useful.
- 2026-05-04 17:20 +08:00 - Marked resolved for the selected typhoon package after 24h, 48h, and 72h validation reports all matched direct HDF5 recomputation within floating-point tolerance; `python -m py_compile .\scripts\validate_spatial_stats.py` also passed.

### CASE-001 - Typhoon Case Needs Explicit Track And Location Context

- Status: watch
- Area: Case Study
- First seen: 2026-05-04
- Last updated: 2026-05-04 17:15 +08:00
- Symptom: Case-study text says the typhoon is near Taiwan Strait or southeast China coast, but the location is too vague.
- Impact: Readers cannot connect the error pattern to the typhoon path and timing.
- Likely cause: Figure narrative lacks a clear track map, date marker, direction, or distance reference.
- Next action: Use the existing typhoon track map when composing the case-study figure/caption.

#### Evidence Trail

- 2026-05-04 16:56 +08:00 - Advisor said direct labeling or using the track map would be clearer than vague text.
- 2026-05-04 17:15 +08:00 - Confirmed typhoon track image exists at `C:\Users\Rong\Desktop\論文參考資料\圖片\楊柳.png`.

#### Decision And Verification

- 2026-05-04 17:15 +08:00 - Moved to watch; image source exists and can be used during thesis figure composition.

### PROD-001 - Keep Experimental Validation Out Of Production Until Confirmed

- Status: watch
- Area: Workflow
- First seen: 2026-05-04
- Last updated: 2026-05-04 17:15 +08:00
- Symptom: Experimental validation calculations may be mixed into the workstation/production workflow too early.
- Impact: Production resources may be spent generating metrics that are not final or useful.
- Likely cause: Research/testing outputs and final operational outputs are not clearly separated yet.
- Next action: Keep validation and metric experiments in research scripts/reports until final selected outputs are confirmed.

#### Evidence Trail

- 2026-05-04 16:56 +08:00 - Advisor said the workstation is production, not a research/test environment, and only confirmed final outputs should enter that process.
- 2026-05-04 17:15 +08:00 - `scripts/validate_spatial_stats.py` was created as a research QA helper and is not wired into the production QGIS workflow.

#### Decision And Verification

- 2026-05-04 17:15 +08:00 - Moved to watch; current validation work remains outside production.

### API-001 - Read-Only HTTP API Exposes Verification Summary And Hotspot GeoJSON

- Status: resolved
- Area: API
- First seen: 2026-05-06
- Last updated: 2026-05-06 14:21 +08:00
- Symptom: User wanted an API similar to the NTOU ENC servlet, where data can be requested through a URL and returned over the network.
- Impact: Without an API, sharing results requires direct database restore, direct file transfer, or QGIS/manual loading.
- Likely cause: Current workflow is file/QGIS/database centered, not HTTP centered.
- Next action: Decide whether the API is only for local/LAN use or whether it should later be deployed with authentication, HTTPS, and managed database credentials.

#### Evidence Trail

- 2026-05-06 14:21 +08:00 - NTOU reference endpoint returned JSON keyed by product/cell ID, with coordinates and metadata.
- 2026-05-06 14:21 +08:00 - Added `scripts/s111_api_server.py` with read-only Flask endpoints for status, summary rows, hotspot summaries, and hotspot GeoJSON.
- 2026-05-06 14:21 +08:00 - Added `run_s111_api.ps1` and `API_README_S111.md` for repeatable startup and usage notes.
- 2026-05-06 14:21 +08:00 - Local API process started on `http://127.0.0.1:8111/api`.

#### Decision And Verification

- 2026-05-06 14:21 +08:00 - Kept the API separate from the QGIS plugin so it does not affect existing plugin behavior.
- 2026-05-06 14:21 +08:00 - `python -m py_compile .\scripts\s111_api_server.py` passed.
- 2026-05-06 14:21 +08:00 - `/api/status` returned `summary_stats` count 2736 and latest summary shape of 24 hourly rows for 24h, 48h, and 72h on 2026-04-10.
- 2026-05-06 14:21 +08:00 - `/api/summary?date=2026-04-10&lead_hours=24` returned 24 rows from `2026-04-10T00:00:00` through `2026-04-10T23:00:00`.
- 2026-05-06 14:21 +08:00 - `/api/hotspot-summary?date=2026-04-10` returned 12 grouped rows.
- 2026-05-06 14:21 +08:00 - `/api/hotspots?date=2026-04-10&lead_hours=24&error_type=speed&limit=3` returned a GeoJSON FeatureCollection with 3 features.

### API-002 - API Omits Null Fields By Default And Supports Full Debug Output

- Status: resolved
- Area: API
- First seen: 2026-05-06
- Last updated: 2026-05-06 14:48 +08:00
- Symptom: `/api/summary` exposed many `null` fields such as direction mean/median/std columns that are not populated in the current `summary_stats` rows.
- Impact: Handoff users could mistake reserved or not-yet-populated fields for API failure.
- Likely cause: The first API version returned every selected database column exactly as stored.
- Next action: Keep default output clean; use `include_nulls=true` only when debugging raw database columns.

#### Evidence Trail

- 2026-05-06 14:48 +08:00 - User confirmed the API should hide null fields by default and expose full fields only when requested.
- 2026-05-06 14:48 +08:00 - Updated `scripts/s111_api_server.py` so `/api/summary`, `/api/hotspot-summary`, and `/api/hotspots` omit `null` fields by default.
- 2026-05-06 14:48 +08:00 - Added `include_nulls=true` support for raw-column inspection.
- 2026-05-06 14:48 +08:00 - Updated `verification_pipeline.py` so future hourly summary upserts include `forecast_file`, lead-step fields, `threshold`, and `dir_threshold`.
- 2026-05-06 14:48 +08:00 - Backfilled existing `summary_stats.dir_threshold` to `30.0` for 2736 rows with valid direction summary values.

#### Decision And Verification

- 2026-05-06 14:48 +08:00 - `python -m py_compile .\scripts\s111_api_server.py .\verification_pipeline.py` passed.
- 2026-05-06 14:48 +08:00 - `/api/summary?date=2026-04-10&lead_hours=24` returned 24 rows; the first row had no null values, included `dir_threshold=30.0`, and omitted `dir_mean_abs_error`.
- 2026-05-06 14:48 +08:00 - `/api/summary?date=2026-04-10&lead_hours=24&include_nulls=true` returned the full row including `dir_mean_abs_error: null`.
- 2026-05-06 14:48 +08:00 - `/api/hotspots?date=2026-04-10&lead_hours=24&error_type=speed&limit=3` returned GeoJSON properties without null values.
- 2026-05-06 14:48 +08:00 - Copied updated API files and handoff docs to `G:\我的雲端硬碟\geojson\S111_給學長_完整交付版_全部資料\06_API服務`.
- 2026-05-06 14:50 +08:00 - Re-exported the handoff PostgreSQL dump after the `dir_threshold` backfill; updated dump SHA256 is `750AF747D7489F70BAEA494DD9FA71037A25976CAD9E95DC9517A870D506D946`.

### API-003 - API Supports Bbox-Based Spatial Monitoring Queries

- Status: resolved
- Area: API
- First seen: 2026-05-06
- Last updated: 2026-05-06 15:40 +08:00
- Symptom: Senior clarified that the future workflow should accept a chart/cell spatial extent and return monitoring data for that extent.
- Impact: Whole-database or whole-day endpoints are not enough for a map UI where the user selects one chart cell.
- Likely cause: The first API version was database/table oriented, not spatial-selection oriented.
- Next action: Confirm whether `bbox=min_lon,min_lat,max_lon,max_lat` is enough for the senior workflow or whether exact polygon clipping by chart-cell boundary is needed.

#### Evidence Trail

- 2026-05-06 15:40 +08:00 - User provided senior's example UI showing a selected chart cell such as `[1U319210] SOUTHEAST OF TAIWAN STRAIT`.
- 2026-05-06 15:40 +08:00 - Senior said the next step is to provide a spatial range and extract monitoring data.
- 2026-05-06 15:40 +08:00 - Updated `/api/hotspots` to accept optional `bbox=min_lon,min_lat,max_lon,max_lat`.
- 2026-05-06 15:40 +08:00 - Added `/api/area-monitoring` to summarize hotspot count, warning count, critical count, and min/mean/max error inside a bbox.
- 2026-05-06 15:40 +08:00 - Updated API handoff documents and synced them to `G:\我的雲端硬碟\geojson\S111_給學長_完整交付版_全部資料\06_API服務`.

#### Decision And Verification

- 2026-05-06 15:40 +08:00 - `python -m py_compile .\scripts\s111_api_server.py` passed.
- 2026-05-06 15:40 +08:00 - `/api/area-monitoring?bbox=119,21,120,23&days=14&lead_hours=24&error_type=speed` returned one summary row for `2026-04-10` with 302 speed warning hotspots and `max_error=0.6207385063171387`.
- 2026-05-06 15:40 +08:00 - `/api/hotspots?bbox=119,21,120,23&date=2026-04-10&lead_hours=24&error_type=speed&limit=5` returned a GeoJSON FeatureCollection with 5 in-range features.

### API-004 - API Supports ENC Chart Cell ID Lookup And Monitoring

- Status: resolved
- Area: API
- First seen: 2026-05-06
- Last updated: 2026-05-06 17:15 +08:00
- Symptom: Senior's UI uses many chart-cell squares with IDs such as `1U319210`; bbox-only querying would force the caller to resolve each cell extent externally.
- Impact: Frontend integration is easier if it can pass a cell ID directly and let the API resolve the extent.
- Likely cause: The first spatial API layer accepted raw coordinate ranges but did not integrate the NTOU ENC cell-index endpoint.
- Next action: Confirm with senior whether bbox-per-cell is accurate enough or whether exact polygon clipping is required for irregular cells.

#### Evidence Trail

- 2026-05-06 17:15 +08:00 - Added `/api/cells` to fetch/return NTOU `getENCMap` cell metadata as JSON or GeoJSON.
- 2026-05-06 17:15 +08:00 - Added `cell_id` support to `/api/cell-monitoring`, `/api/area-monitoring`, and `/api/hotspots`.
- 2026-05-06 17:15 +08:00 - Added local ENC cell cache at `data/enc_cells_cache.json` and copied it to the handoff API folder.
- 2026-05-06 17:15 +08:00 - Added SSL fallback for the public NTOU cell-index request because Python rejects the current certificate chain while browsers load it.

#### Decision And Verification

- 2026-05-06 17:15 +08:00 - `python -m py_compile .\scripts\s111_api_server.py` passed.
- 2026-05-06 17:15 +08:00 - `/api/cells?cell_id=1U319210` returned title `SOUTHEAST OF TAIWAN STRAIT` and bbox lon `119~120`, lat `21~22`.
- 2026-05-06 17:15 +08:00 - `/api/cells?cell_id=1U319210&format=geojson` returned a GeoJSON FeatureCollection with one feature.
- 2026-05-06 17:15 +08:00 - `/api/cell-monitoring?cell_id=1U319210&days=14&lead_hours=24&error_type=speed` returned 0 rows, which matches the current DB having no latest hotspots in that exact cell bbox.
- 2026-05-06 17:15 +08:00 - `/api/cell-monitoring?cell_id=1U319220&days=14&lead_hours=24&error_type=speed` returned one row with 302 speed warning hotspots on `2026-04-10`.
- 2026-05-06 17:15 +08:00 - Synced updated API files and `data/enc_cells_cache.json` to `G:\我的雲端硬碟\geojson\S111_給學長_完整交付版_全部資料\06_API服務`.

### API-005 - API Exposes Threshold-Filtered Drawing Rows And Click Detail

- Status: resolved
- Area: API
- First seen: 2026-05-07
- Last updated: 2026-05-07 11:29 +08:00
- Symptom: Senior integration needs a threshold value, then the API should return the points exceeding that threshold for map display.
- Impact: Returning too much descriptive metadata can make the integration harder to understand; the caller mainly needs coordinates, value, unit, severity, and color.
- Likely cause: Earlier API versions were built around database status, summaries, bbox/cell monitoring, and GeoJSON handoff rather than a minimal drawing-data contract.
- Next action: Ask senior to confirm whether hotspot-only time rows are sufficient, or whether the database must also store full grid-cell values for complete 24-hour curves.

#### Evidence Trail

- 2026-05-07 11:03 +08:00 - User asked to make the API match database drawing data and return longitude, latitude, value, QGIS drawing parameters, and color.
- 2026-05-07 11:03 +08:00 - Added `/api/drawing-data` and alias `/api/qgis-points`.
- 2026-05-07 11:03 +08:00 - Added drawing metadata with `geometry=Point`, `crs=EPSG:4326`, `x_field=lon`, `y_field=lat`, `value_field=value`, and `color_field=color`.
- 2026-05-07 11:03 +08:00 - Added color rules matching the QGIS/plugin constants. Current colors are speed warning `#FFD700`, speed critical `#FF0000`, direction warning `#F8A718`, direction critical `#7652E2`.
- 2026-05-07 11:03 +08:00 - Added `API_DRAWING_DATA_給學長.md` and synced it with the updated API script to the Google Drive handoff folder.
- 2026-05-07 11:17 +08:00 - Added `/api/threshold-hotspots` alias and `threshold` / `critical_threshold` request parameters.
- 2026-05-07 11:17 +08:00 - Added `API_THRESHOLD_HOTSPOTS_FORMAT_給學長.json` as a shareable API response-format sample.
- 2026-05-07 11:29 +08:00 - Added `/api/hotspot-series` and alias `/api/point-monitoring` for map-click detail by hotspot `id` or nearest `lon`/`lat`.
- 2026-05-07 11:29 +08:00 - Updated handoff docs to explain that point-series data currently comes from `hotspot_points`, so it is hotspot-row-only rather than a full all-grid 24-hour curve.

#### Decision And Verification

- 2026-05-07 11:03 +08:00 - `python -m py_compile .\scripts\s111_api_server.py` passed.
- 2026-05-07 11:03 +08:00 - `/api/drawing-data?date=2026-04-10&lead_hours=24&error_type=speed&limit=2` returned rows with fields `lon`, `lat`, `value`, `unit`, `severity`, `color`, and `qgis_symbol`.
- 2026-05-07 11:03 +08:00 - `/api/drawing-data?date=2026-04-10&lead_hours=24&error_type=direction&limit=2` returned direction rows with `unit=deg`; current warning color is `#F8A718`.
- 2026-05-07 11:03 +08:00 - `/api/drawing-data?...&include_db_fields=true` returned optional database fields such as `speed`, `direction`, and `source_error_value`.
- 2026-05-07 11:03 +08:00 - `/api/hotspots` GeoJSON properties now also include `value`, `unit`, `color`, and `qgis_symbol`.
- 2026-05-07 11:17 +08:00 - `/api/threshold-hotspots?date=2026-04-10&lead_hours=24&error_type=speed&threshold=0.6&limit=5` returned values all >= 0.6.
- 2026-05-07 11:17 +08:00 - `/api/threshold-hotspots?date=2026-04-10&lead_hours=24&error_type=speed&threshold=0.9&limit=5` returned values all >= 0.9.
- 2026-05-07 11:17 +08:00 - `/api/threshold-hotspots?date=2026-04-10&lead_hours=24&error_type=direction&threshold=40&limit=5` returned direction rows with `unit=deg` and values all >= 40.
- 2026-05-07 11:29 +08:00 - `/api/hotspot-series?id=119051239` returned 3 rows for the selected point `lon=120.295`, `lat=26.345`.
- 2026-05-07 11:29 +08:00 - `/api/hotspot-series?lon=120.295&lat=26.345&date=2026-04-10&lead_hours=24&error_type=speed&radius_deg=0.02` returned the nearest point and the same 3 rows.

### API-006 - Public Handoff API Removes Chart-Cell/Product-ID Traces

- Status: resolved
- Area: API
- First seen: 2026-05-07
- Last updated: 2026-05-07 11:40 +08:00
- Symptom: The API had shifted to threshold hotspot data, but the public index/docs still exposed old chart-cell/product-ID endpoints and parameters.
- Impact: Senior could misunderstand the current integration contract as chart-cell based instead of database hotspot threshold based.
- Likely cause: Earlier prototype work integrated chart-cell lookup before the requirement was clarified.
- Next action: Keep the handoff package focused on `threshold-hotspots`, `drawing-data`, and `hotspot-series`.

#### Evidence Trail

- 2026-05-07 11:40 +08:00 - Removed public `/api/cells`, `/api/area-monitoring`, and `/api/cell-monitoring` routes from `scripts/s111_api_server.py`.
- 2026-05-07 11:40 +08:00 - Removed `cell_id` handling from hotspot and drawing-data endpoints.
- 2026-05-07 11:40 +08:00 - Removed ENC fetch/cache code and deleted `enc_cells_cache.json` from the local workspace and handoff API folder.
- 2026-05-07 11:40 +08:00 - Rewrote `API_README_S111.md`, `API_HANDOFF_給學長.md`, and `API_DRAWING_DATA_給學長.md` around the threshold hotspot workflow.

#### Decision And Verification

- 2026-05-07 11:40 +08:00 - `python -m py_compile .\scripts\s111_api_server.py` passed.
- 2026-05-07 11:40 +08:00 - `/api` returned only database/hotspot endpoints and no chart-cell endpoints.
- 2026-05-07 11:40 +08:00 - `rg` found no `cell_id`, `cells`, `cell-monitoring`, `area-monitoring`, `ENC`, `productID`, `product_id`, `圖幅`, `usage_band`, `S111_ENC`, or `enc_cells` in the API script and handoff docs.
- 2026-05-07 11:40 +08:00 - The same `rg` check found no matches in the Google Drive `06_API服務` handoff folder.

### API-007 - API Exposes Metric Hotspot Layers Including Direction STD

- Status: resolved
- Area: API
- First seen: 2026-05-14
- Last updated: 2026-05-14 11:28 +08:00
- Symptom: Teacher asked that standard deviation also be provided because it reflects model stability/dispersion.
- Impact: Senior's web map could only consume official hotspot points, not the supplementary `std_dir` stability layer.
- Likely cause: Metric hotspot GeoJSON files existed in result packages, but metric rows had not been imported into `hotspot_points` for API use.
- Next action: Share `metric=std_dir` examples with senior; keep official hotspot as `metric=official`.

#### Evidence Trail

- 2026-05-14 11:28 +08:00 - Updated `scripts/rebuild_direction_speed_gate_outputs.py` so `--update-db` also imports metric hotspot rows from `*.metric_hotspots.csv`.
- 2026-05-14 11:28 +08:00 - Local and Droplet DBs now contain 1,238,363 metric hotspot rows, including 652,623 `std_abs_dir_error` rows.
- 2026-05-14 11:28 +08:00 - `2026-04-10` `std_abs_dir_error` counts are 6,024 for 24h, 6,337 for 48h, and 6,889 for 72h.
- 2026-05-14 11:28 +08:00 - Added `metric=std_dir` alias in `scripts/s111_api_server.py` and exposed metric counts in `/api/status`.
- 2026-05-14 11:28 +08:00 - Updated handoff docs and dump to `s111_verification_20260514_0p48_median_metrics.dump`.

#### Decision And Verification

- 2026-05-14 11:28 +08:00 - `python -m py_compile .\scripts\s111_api_server.py .\scripts\rebuild_direction_speed_gate_outputs.py` passed.
- 2026-05-14 11:28 +08:00 - Droplet `systemctl restart s111-api` returned `active`.
- 2026-05-14 11:28 +08:00 - Public API query `/api/threshold-hotspots?date=2026-04-10&lead_hours=24&error_type=direction&metric=std_dir&threshold=30&limit=3` returned rows with `metric=std_abs_dir_error`, `unit=deg`, and `color`.
- 2026-05-14 11:28 +08:00 - Public GeoJSON query with `metric=std_dir&format=geojson&limit=1` returned one feature with `value=58.7962646484375 deg`.
- 2026-05-14 11:28 +08:00 - Public `/api/hotspot-series?id=121117003` auto-preserved the clicked metric row and returned `metric=std_abs_dir_error`.

### API-008 - Unneeded Squared-Error Metric Removed From Active Outputs

- Status: resolved
- Area: Pipeline/API
- First seen: 2026-05-14
- Last updated: 2026-05-14 17:05 +08:00
- Symptom: User confirmed the teacher did not request the root-mean-square error metric.
- Impact: Keeping it in generated CSV/API/QGIS summaries could confuse the thesis method and handoff data shape.
- Likely cause: Earlier verification prototype included generic verification metrics before the teacher narrowed the required indicators.
- Next action: Re-export/redeploy if the public API process or a new DB dump must reflect this exact removal immediately.

#### Evidence Trail

- 2026-05-14 17:05 +08:00 - Removed active root-mean-square error fields from `verification_pipeline.py`, `scripts/s111_api_server.py`, `s111_viewer.py`, `result_package_loader.py`, `RESULT_PACKAGE_FIELD_GUIDE.md`, and `老師要求_口試圖表整理.md`.
- 2026-05-14 17:05 +08:00 - Pipeline now keeps speed MAE/median/std/bias/max and direction mean/median/std/bias/max, plus hotspot counts.
- 2026-05-14 17:05 +08:00 - Future schema initialization drops old summary columns for the removed metric when the pipeline schema migration runs.

#### Decision And Verification

- 2026-05-14 17:05 +08:00 - `python -m py_compile verification_pipeline.py scripts\s111_api_server.py result_package_loader.py s111_viewer.py` passed.
- 2026-05-14 17:05 +08:00 - Search now only finds the removed metric in guard/drop-migration code paths.

### API-009 - Hotspot Display Layers Explicitly Split Without Changing DB Storage

- Status: resolved
- Area: API/Docs
- First seen: 2026-05-17
- Last updated: 2026-05-17 20:05 +08:00
- Symptom: User asked whether hotspot should be split like GeoJSON layers; the old API could filter by `error_type` and `metric`, but the response did not explicitly state which display layer each row belonged to.
- Impact: The senior/front-end side could misread `hotspot_points` as one undifferentiated layer, or confuse official direction hotspot with diagnostic `std_dir`/metric hotspot layers.
- Likely cause: Database design intentionally kept hotspot data in one table, while display-layer metadata had not yet been made explicit in the API response.
- Next action: Share `API_HOTSPOT_LAYER_SPLIT_GUIDE.md` and tell the senior to split map layers by `layer_id`.

#### Evidence Trail

- 2026-05-17 20:05 +08:00 - Added API helper metadata for official speed, official direction median, speed mean/median/std, and direction mean/median/std hotspot layers.
- 2026-05-17 20:05 +08:00 - `/api/threshold-hotspots`, `/api/drawing-data`, and `/api/hotspots` now expose selected `layer` metadata.
- 2026-05-17 20:05 +08:00 - Each drawing row and GeoJSON feature property now includes `layer_id`, `layer_name`, `layer_name_zh`, `layer_role`, and `statistic`.
- 2026-05-17 20:05 +08:00 - Added `API_HOTSPOT_LAYER_SPLIT_GUIDE.md` and synced the same guide into Obsidian.

#### Decision And Verification

- 2026-05-17 20:05 +08:00 - Decision: keep one database table `hotspot_points`; split only API/QGIS/GeoJSON/frontend display layers.
- 2026-05-17 20:05 +08:00 - Decision: `direction` inside a hotspot row remains an auxiliary reference-flow direction; hotspot severity is based on `error_value`.
- 2026-05-17 20:05 +08:00 - `python -m py_compile .\scripts\s111_api_server.py` passed.
- 2026-05-17 20:05 +08:00 - Lightweight helper check returned `official_speed_hotspots`, `official_direction_median_hotspots`, and `metric_direction_std_hotspots` for the expected API cases.
- 2026-05-17 20:12 +08:00 - Deployed `scripts/s111_api_server.py` to Droplet `/opt/s111_viewer`, restarted `s111-api`, and verified service state `active`.
- 2026-05-17 20:12 +08:00 - Public `/api/threshold-hotspots?...error_type=direction&metric=std_dir...` returned `layer_id=metric_direction_std_hotspots`, `layer_name_zh=流向標準差 hotspot`, and `statistic=std_abs_dir_error`.
- 2026-05-17 20:12 +08:00 - Public `/api/hotspots?...error_type=direction&format=geojson...` returned GeoJSON feature properties with `layer_id=official_direction_median_hotspots`, `layer_name_zh=正式流向中位數誤差 hotspot`, and `statistic=median_abs_dir_error`.
- 2026-05-17 20:16 +08:00 - Public `/docs` page contains the updated `layer_id` and `metric` guidance.

### DEPLOY-001 - Droplet Deployment Files Prepared

- Status: resolved
- Area: Deployment
- First seen: 2026-05-12
- Last updated: 2026-05-12 18:32 +08:00
- Symptom: Need deployment artifacts that match the current Flask API instead of a FastAPI/Uvicorn plan.
- Impact: Without these files, the Droplet setup would rely on ad hoc commands and could expose the database or run the API in development mode.
- Likely cause: The API prototype started locally, while cloud deployment details were not yet written down.
- Next action: User creates the Droplet and uploads the API folder/dump; then follow `DEPLOY_DROPLET_README.md`.

#### Evidence Trail

- 2026-05-12 18:32 +08:00 - Added `DEPLOY_DROPLET_README.md` with Ubuntu, PostgreSQL/PostGIS, dump restore, Gunicorn, Nginx, firewall, SSH tunnel, and verification steps.
- 2026-05-12 18:32 +08:00 - Added `requirements_api.txt` for Flask, Gunicorn, and psycopg2.
- 2026-05-12 18:32 +08:00 - Added `.env.example` and `deploy/s111-api.env.example`.
- 2026-05-12 18:32 +08:00 - Added `deploy/s111-api.service` and `deploy/nginx_s111_api.conf`.
- 2026-05-12 18:32 +08:00 - Added `scripts/__init__.py` so Gunicorn can import `scripts.s111_api_server:create_app()` reliably.
- 2026-05-12 18:32 +08:00 - Synced deployment files to the Google Drive `06_API服務` handoff folder.

#### Decision And Verification

- 2026-05-12 18:32 +08:00 - `python -m py_compile .\scripts\s111_api_server.py .\scripts\__init__.py` passed.
- 2026-05-12 18:32 +08:00 - Python import test created the Flask app from `scripts.s111_api_server:create_app()` successfully and found 12 routes.

### DOC-001 - Web API Docs Page Added

- Status: resolved
- Area: API Docs
- First seen: 2026-05-13
- Last updated: 2026-05-13 17:47 +08:00
- Symptom: User needed a convenient web page for copying and testing API URLs.
- Impact: Without a docs page, testing required copying URLs from chat or markdown files.
- Likely cause: The previous `/api` index returned JSON metadata, not a human-facing test page.
- Next action: Share `http://159.65.4.22/docs` or `http://159.65.4.22/api/docs` with testers.

#### Evidence Trail

- 2026-05-13 17:47 +08:00 - Added `/docs` and `/api/docs` routes to `scripts/s111_api_server.py`.
- 2026-05-13 17:47 +08:00 - Docs page includes copy/open controls for status, threshold hotspots, GeoJSON, drawing-data, hotspot-summary, hotspot-series, nearest-point lookup, and summary endpoints.
- 2026-05-13 17:47 +08:00 - Synced updated API script to Google Drive handoff folder and Droplet `/opt/s111_viewer/scripts/s111_api_server.py`.

#### Decision And Verification

- 2026-05-13 17:47 +08:00 - `python -m py_compile .\scripts\s111_api_server.py` passed locally.
- 2026-05-13 17:47 +08:00 - Droplet `python3 -m py_compile /opt/s111_viewer/scripts/s111_api_server.py` passed and `systemctl restart s111-api` returned active.
- 2026-05-13 17:47 +08:00 - `curl -i http://159.65.4.22/docs` returned HTTP 200 with `Content-Type: text/html; charset=utf-8`.
- 2026-05-13 17:47 +08:00 - `http://159.65.4.22/api` now lists `"docs": "/docs"`.

### DOC-002 - Obsidian S-111 Notes Synced To Metric-Hotspot Version

- Status: resolved
- Area: Obsidian
- First seen: 2026-05-14
- Last updated: 2026-05-14 16:10 +08:00
- Symptom: Obsidian still referenced the no-metric `s111_verification_20260514_0p48_median.dump` and old `hotspot_points = 3,193,154` total after code/data changed.
- Impact: Future reading or handoff preparation could use stale database counts and miss the `std_dir` API layer.
- Likely cause: Obsidian notes were imported before the final metric-row DB/API update.
- Next action: Keep Obsidian docs in sync after future DB/API changes.

#### Evidence Trail

- 2026-05-14 16:10 +08:00 - Updated Obsidian docs for API data version, database handoff, API handoff, drawing-data, restore runbook, thesis decision, project summary, troubleshooting, and presentation notes.
- 2026-05-14 16:10 +08:00 - Added source-note warnings for `scripts_s111_api_server.py.md` and `scripts_rebuild_direction_speed_gate_outputs.py.md` so readers know the repo code now includes metric aliases and metric DB import.

#### Decision And Verification

- 2026-05-14 16:10 +08:00 - Obsidian global search found zero matches for the old no-metric dump name `s111_verification_20260514_0p48_median.dump`.
- 2026-05-14 16:10 +08:00 - Obsidian global search found zero matches for old SHA `B182EE190F35E17C9F35A0C0AF2FB0CC00FD91661BA8021EA46F756EEC77A0F3`.
- 2026-05-14 16:10 +08:00 - Obsidian search now finds current keys such as `median_metrics`, `std_dir`, and `4,431,517`.

## Layer 3: Cross-Cutting Notes

- Assumptions: The QGIS plugin should show whole-day hotspot layers for database results.
- Spatial-output distinction: direction spatial stats GeoJSON represents all valid grid points for the selected statistic, while hotspot GeoJSON/API represents only threshold-selected points. Direction spatial stats use the `0.48 kn` valid-speed gate for direction-error calculation; arrow layers are flow-field visualization, and abnormal/hotspot arrows are the views that apply warning/critical styling.
- Risks: Validation currently covers the selected 2025-08-15 typhoon package; repeat the same report on another date if the thesis needs multi-case QA evidence. Older `20260504`, `20260512`, non-median `20260514_0p48`, and no-metric `20260514_0p48_median` dumps remain in the handoff folder as archives; the current restored DB should use `s111_verification_20260514_0p48_median_metrics.dump`.
- External dependencies: Local PostgreSQL service, `s111_verification` database, `psycopg2`, and Flask for the local API server.

## Layer 4: Session Change Log

- 2026-05-04 16:13 +08:00 - Created the initial layered issue ledger from the database inspection session.
- 2026-05-04 16:45 +08:00 - Marked DB-002 resolved after user confirmed whole-day hotspot loading is intended.
- 2026-05-04 16:52 +08:00 - Resolved DB-001 by changing database summary loading from one-row-per-lead selection to latest-day aggregation.
- 2026-05-04 16:56 +08:00 - Added advisor feedback issues for thesis percentile definition, legends, spatial maps, metric selection, validation, case-study context, and production boundaries.
- 2026-05-04 17:15 +08:00 - Updated thesis feedback statuses from user confirmation and created the first reproducible spatial-stat validation report.
- 2026-05-04 17:20 +08:00 - Added 48h and 72h spatial-stat validation reports and marked VALID-001 resolved for the selected typhoon package.
- 2026-05-04 17:26 +08:00 - Rechecked DB-004 against live database constraints and confirmed the pipeline is daily-level while the live `summary_stats` table is hourly.
- 2026-05-04 18:02 +08:00 - Resolved DB-004 by changing `verification_pipeline.py` to write hourly `summary_stats` rows keyed by `(target_date, target_timestamp, lead_hours)`.
- 2026-05-04 18:12 +08:00 - Resolved DB-003 by fixing package hotspot DB import, backfilling existing package rows, and confirming direction hotspots now reach 2026-04-10.
- 2026-05-06 14:21 +08:00 - Resolved API-001 by adding and locally verifying a read-only Flask API for database status, hourly summaries, hotspot summaries, and hotspot GeoJSON.
- 2026-05-06 14:48 +08:00 - Resolved API-002 by hiding null fields by default, adding `include_nulls=true`, backfilling `dir_threshold`, syncing updated API handoff files, and refreshing the DB dump.
- 2026-05-06 15:40 +08:00 - Resolved API-003 by adding bbox-based monitoring and hotspot queries for chart/cell spatial extents.
- 2026-05-06 17:15 +08:00 - Resolved API-004 by adding NTOU ENC cell ID lookup, cell-based monitoring/hotspot queries, local cell cache, and handoff docs.
- 2026-05-07 11:03 +08:00 - Resolved API-005 by adding `/api/drawing-data` for QGIS-ready lon/lat/value/color rows and syncing the drawing-data handoff doc.
- 2026-05-07 11:17 +08:00 - Updated API-005 with `/api/threshold-hotspots`, custom threshold filtering, and a shareable JSON response-format file for the senior.
- 2026-05-07 11:29 +08:00 - Updated API-005 with `/api/hotspot-series` so map clicks can query same-point hotspot time rows by id or nearest coordinate.
- 2026-05-07 11:40 +08:00 - Resolved API-006 by removing chart-cell/product-ID endpoints, docs, cache, and visible handoff traces from the public API package.
- 2026-05-12 18:32 +08:00 - Resolved DEPLOY-001 by preparing Droplet deployment docs, requirements, environment examples, Gunicorn systemd service, Nginx config, and syncing them to the handoff folder.
- 2026-05-13 17:47 +08:00 - Resolved DOC-001 by adding a web docs page with copyable API test URLs and deploying it to the Droplet.
- 2026-05-14 08:30 +08:00 - Resolved METRIC-001 for the direction-error speed threshold by documenting `median_dir_count` as the basis, setting the threshold to `0.48 kn`, and updating `verification_pipeline.py`.
- 2026-05-14 08:58 +08:00 - Completed the `0.48 kn` rebuild across local packages, local DB, Droplet DB/API, Google Drive handoff GeoJSON, restore script, and new DB dump.
- 2026-05-14 09:53 +08:00 - Corrected the rebuild to use `median_dir` as the official direction hotspot statistic, refreshed all handoff/API/DB outputs, and documented the fair `0.6 kn` comparison.
- 2026-05-14 09:56 +08:00 - Synced the final API files/data-version note to both the Google Drive API handoff folder and the live Droplet API service.
- 2026-05-14 11:28 +08:00 - Resolved API-007 by importing metric hotspot rows into local/Droplet DBs, exposing `metric=std_dir`, updating API docs, and creating `s111_verification_20260514_0p48_median_metrics.dump`.
- 2026-05-14 16:10 +08:00 - Resolved DOC-002 by syncing Obsidian S-111 notes with the `median_metrics` dump, metric row counts, `std_dir` API layer, and updated SHA.
- 2026-05-14 17:05 +08:00 - Resolved API-008 by removing the unneeded root-mean-square error metric from active pipeline/API/QGIS outputs and related docs.
- 2026-05-17 20:12 +08:00 - Resolved API-009 by adding explicit hotspot layer metadata to API rows/GeoJSON, deploying it to the Droplet API, and documenting the one-table storage, multi-layer display rule in Obsidian.
- 2026-05-18 11:01 +08:00 - Clarified in Obsidian that direction spatial stats GeoJSON is all valid grid points, while hotspot GeoJSON/API is threshold-selected; arrow visualization is separate from the spatial-stat GeoJSON layer.
- 2026-05-15 00:00 +08:00 - Added 0815 typhoon sensitivity check to `THESIS_DIRECTION_SPEED_THRESHOLD_DECISION.md`; synced it to Obsidian.
- 2026-05-18 11:12 +08:00 - Resolved VIS-003 by changing direction-error warning/critical colors to S-111 orange `#F8A718` and S-111 purple `#7652E2`, while preserving the S-111 arrow symbol.
- 2026-05-18 11:49 +08:00 - Synced the VIS-003 color update to Google Drive `06_API服務` and redeployed the Droplet API; public API verification passed.
- 2026-05-18 11:56 +08:00 - Added explicit update-log documentation for the VIS-003 color change before re-syncing the handoff package.
- 2026-05-18 11:38 +08:00 - Added filename interpretation notes for `hotspots.geojson`, `spatial_stats_XXh.geojson`, and `metric_hotspots.geojson` to the output/product guide and Obsidian field guide.
