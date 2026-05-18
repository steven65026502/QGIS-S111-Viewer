# Spatial Stats Validation Report

- Generated at: 2026-05-04T17:15:28
- Package: `C:\Users\Rong\Desktop\test_h5_files\daily_results\20250815`
- Spatial CSV: `C:\Users\Rong\Desktop\test_h5_files\daily_results\20250815\20250814_day1_spatial_stats_24h.csv`
- Hindcast H5: `C:\Users\Rong\Desktop\test_h5_files\20250815.h5`
- Forecast H5: `C:\Users\Rong\Desktop\test_h5_files\20250814.h5`
- Target date: `2025-08-15`
- Offset hours: `24`
- Valid spatial rows checked for percentile denominator: `231641`

## Method

1. Read the exported `spatial_stats` CSV.
2. Select deterministic cells: low mean error, median-like percentile, high mean error, and high standard deviation.
3. Open the original hindcast and forecast HDF5 files directly with `h5py`.
4. For each selected cell, read the 24 hourly scalar values from HDF5, applying the same vertical flip used by the pipeline.
5. Recompute absolute speed error, circular absolute direction error, mean, median, and population standard deviation.
6. Independently recompute percentile ranks from all valid spatial rows in the CSV.

## Summary

- Maximum absolute statistic difference across sampled cells: `6.52233046594e-06`
- Maximum absolute percentile difference across sampled cells: `3.70864195531e-06`

## Sample Cell Statistic Checks

### low mean cell row=319 col=378

- lon/lat: `119.785000`, `26.805000`
- CSV valid_count: `24`
- HDF5 included hours: `24` (2025-08-15 00:00:00 to 2025-08-15 23:00:00)

| Metric | CSV | Recomputed from HDF5 | Abs diff |
| --- | ---: | ---: | ---: |
| `mean_abs_error` | 0.000742275 | 0.000742275 | 2.48595218846e-11 |
| `median_abs_error` | 0.000541472 | 0.000541472 | 0 |
| `std_abs_error` | 0.000670719 | 0.000670719 | 8.98216342884e-12 |
| `mean_abs_dir_error` | 15.305401802 | 15.305401802 | 0 |
| `median_abs_dir_error` | 7.536422729 | 7.536422729 | 0 |
| `std_abs_dir_error` | 29.304971695 | 29.304971956 | 2.61428976245e-07 |
| `mean_truth_speed` | 0.004005736 | 0.004005736 | 1.98269844986e-10 |
| `mean_truth_direction` | 154.093460083 | 154.093454241 | 5.8424155327e-06 |

| Percentile field | CSV percentile | Recomputed rank | Abs diff |
| --- | ---: | ---: | ---: |
| `mean_abs_error` | 0.000000 | 0.000000 | 0 |
| `median_abs_error` | 0.000000 | 0.000000 | 0 |
| `std_abs_error` | 0.000000 | 0.000000 | 0 |
| `mean_abs_dir_error` | 77.624329 | 77.624331 | 2.24494704071e-06 |
| `median_abs_dir_error` | 61.642418 | 61.642419 | 1.36356818103e-06 |
| `std_abs_dir_error` | 90.677773 | 90.677776 | 3.33711903977e-06 |

### median-like percentile cell row=679 col=385

- lon/lat: `119.855000`, `23.205000`
- CSV valid_count: `24`
- HDF5 included hours: `24` (2025-08-15 00:00:00 to 2025-08-15 23:00:00)

| Metric | CSV | Recomputed from HDF5 | Abs diff |
| --- | ---: | ---: | ---: |
| `mean_abs_error` | 0.067291372 | 0.067291374 | 2.32830643654e-09 |
| `median_abs_error` | 0.049118772 | 0.049118772 | 0 |
| `std_abs_error` | 0.049471457 | 0.049471455 | 1.52099545458e-09 |
| `mean_abs_dir_error` | 10.104039192 | 10.104039152 | 3.97364292581e-08 |
| `median_abs_dir_error` | 8.329338074 | 8.329338491 | 4.17232513428e-07 |
| `std_abs_dir_error` | 13.757304192 | 13.757304249 | 5.77252698974e-08 |
| `mean_truth_speed` | 0.623265862 | 0.623265851 | 1.16415321827e-08 |
| `mean_truth_direction` | 33.533664703 | 33.533663122 | 1.58098857383e-06 |

| Percentile field | CSV percentile | Recomputed rank | Abs diff |
| --- | ---: | ---: | ---: |
| `mean_abs_error` | 60.486099 | 60.486099 | 1.23840976585e-07 |
| `median_abs_error` | 49.999783 | 49.999784 | 1.58555971552e-06 |
| `std_abs_error` | 68.963043 | 68.963046 | 2.89313597079e-06 |
| `mean_abs_dir_error` | 53.752808 | 53.752806 | 1.53878999498e-06 |
| `median_abs_dir_error` | 67.934296 | 67.934295 | 1.05923557214e-06 |
| `std_abs_dir_error` | 68.575378 | 68.575376 | 2.83516784805e-06 |

### high mean cell row=589 col=456

- lon/lat: `120.565000`, `24.105000`
- CSV valid_count: `24`
- HDF5 included hours: `24` (2025-08-15 00:00:00 to 2025-08-15 23:00:00)

| Metric | CSV | Recomputed from HDF5 | Abs diff |
| --- | ---: | ---: | ---: |
| `mean_abs_error` | 0.398037553 | 0.398037557 | 4.34617203338e-09 |
| `median_abs_error` | 0.125423849 | 0.125423849 | 0 |
| `std_abs_error` | 0.549211800 | 0.549211799 | 1.54693613474e-09 |
| `mean_abs_dir_error` | 25.568420410 | 25.568419456 | 9.53674316406e-07 |
| `median_abs_dir_error` | 3.052089691 | 3.052089691 | 0 |
| `std_abs_dir_error` | 40.799873352 | 40.799875253 | 1.90095096286e-06 |
| `mean_truth_speed` | 1.223361015 | 1.223361031 | 1.55220429843e-08 |
| `mean_truth_direction` | 154.066879272 | 154.066879056 | 2.1608727252e-07 |

| Percentile field | CSV percentile | Recomputed rank | Abs diff |
| --- | ---: | ---: | ---: |
| `mean_abs_error` | 100.000000 | 100.000000 | 0 |
| `median_abs_error` | 93.152306 | 93.152305 | 3.01697696159e-07 |
| `std_abs_error` | 99.999565 | 99.999568 | 3.17111943104e-06 |
| `mean_abs_dir_error` | 94.461235 | 94.461233 | 2.09870928813e-06 |
| `median_abs_dir_error` | 15.755483 | 15.755483 | 2.81606471475e-08 |
| `std_abs_dir_error` | 98.280525 | 98.280521 | 3.70864195531e-06 |

### high std cell row=648 col=352

- lon/lat: `119.525000`, `23.515000`
- CSV valid_count: `24`
- HDF5 included hours: `24` (2025-08-15 00:00:00 to 2025-08-15 23:00:00)

| Metric | CSV | Recomputed from HDF5 | Abs diff |
| --- | ---: | ---: | ---: |
| `mean_abs_error` | 0.238957688 | 0.238957692 | 4.03573116592e-09 |
| `median_abs_error` | 0.069355339 | 0.069355339 | 0 |
| `std_abs_error` | 0.643947542 | 0.643947515 | 2.68249554791e-08 |
| `mean_abs_dir_error` | 6.956769466 | 6.956769625 | 1.58945719697e-07 |
| `median_abs_dir_error` | 4.036437988 | 4.036437988 | 0 |
| `std_abs_dir_error` | 10.721076965 | 10.721077390 | 4.24436057855e-07 |
| `mean_truth_speed` | 0.872682393 | 0.872682377 | 1.58324837685e-08 |
| `mean_truth_direction` | 303.601470947 | 303.601464425 | 6.52233046594e-06 |

| Percentile field | CSV percentile | Recomputed rank | Abs diff |
| --- | ---: | ---: | ---: |
| `mean_abs_error` | 99.839836 | 99.839838 | 1.55855184403e-06 |
| `median_abs_error` | 70.389397 | 70.389397 | 6.73220625913e-07 |
| `std_abs_error` | 100.000000 | 100.000000 | 0 |
| `mean_abs_dir_error` | 32.192196 | 32.192195 | 1.10732275971e-06 |
| `median_abs_dir_error` | 26.110775 | 26.110775 | 3.47149963886e-07 |
| `std_abs_dir_error` | 58.398376 | 58.398377 | 3.26729377775e-07 |

## Threshold Count Table

| Check | Count |
| --- | ---: |
| mean_abs_error >= 0.2 kn | 870 |
| median_abs_error >= 0.2 kn | 1266 |
| std_abs_error >= 0.2 kn | 34 |
| mean_abs_error >= 0.3 kn | 8 |
| median_abs_error >= 0.3 kn | 30 |
| std_abs_error >= 0.3 kn | 3 |
| mean_abs_error >= 0.4 kn | 0 |
| median_abs_error >= 0.4 kn | 0 |
| std_abs_error >= 0.4 kn | 2 |
| mean_abs_error >= 0.5 kn | 0 |
| median_abs_error >= 0.5 kn | 0 |
| std_abs_error >= 0.5 kn | 2 |
| mean_abs_error >= 1.0 kn | 0 |
| median_abs_error >= 1.0 kn | 0 |
| std_abs_error >= 1.0 kn | 0 |
| mean_abs_dir_error >= 22.5 deg | 19707 |
| median_abs_dir_error >= 22.5 deg | 5030 |
| std_abs_dir_error >= 22.5 deg | 37138 |
| mean_abs_dir_error >= 30.0 deg | 7162 |
| median_abs_dir_error >= 30.0 deg | 1700 |
| std_abs_dir_error >= 30.0 deg | 20235 |
| mean_abs_dir_error >= 45.0 deg | 959 |
| median_abs_dir_error >= 45.0 deg | 260 |
| std_abs_dir_error >= 45.0 deg | 1878 |
| mean_abs_dir_error >= 60.0 deg | 177 |
| median_abs_dir_error >= 60.0 deg | 68 |
| std_abs_dir_error >= 60.0 deg | 98 |

## Interpretation

- The sampled CSV statistics match direct HDF5 recomputation within floating-point tolerance.
- Percentile fields match independent spatial-rank recomputation from the full valid-grid denominator.
- The threshold table is a reproducible count table for deciding and explaining warning criteria.
