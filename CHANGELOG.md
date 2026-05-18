# Changelog

## 2026-05-18

### Changed

- Added the S-111 Verification API handoff documents and deployment helpers so the web frontend can request hotspot, drawing, summary, and point-series data from PostgreSQL/PostGIS.
- Removed RMSE from the API-facing data contract and QGIS result-package loader. The monitoring output now focuses on bias, max error, mean absolute error, median error, and standard deviation.
- Normalized forecast lead naming to `lead_hours` for API responses, GeoJSON properties, result-package loading, and database-backed hotspot display.
- Updated direction-error hotspot colors to make warning and critical layers easier to distinguish while keeping the standard S-111 arrow symbol shape:
  - warning: `#F8A718`
  - critical: `#7652E2`
- Documented the current direction speed-gate decision: direction-error monitoring uses the `0.48 kn` speed threshold and prioritizes the median-based criterion.

### Security

- Removed hard-coded local database passwords from the API server and QGIS plugin database configuration. Runtime database credentials must now be provided through `S111_DB_*` environment variables.

### Documentation

- Added API usage, deployment, handoff, threshold-hotspot format, layer-splitting, validation, and data-version notes.
- Added `API_UPDATE_LOG_20260518_DIRECTION_COLOR.md` to explicitly describe the 2026-05-18 color update, its scope, and what was not recalculated.

### Validation

- Verified the deployed API returned the updated direction hotspot colors.
- Verified the Google Drive handoff package and Obsidian notes were synchronized with the same update log.
