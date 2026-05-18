# Spatial Stats Validation Report

- Generated at: 2026-05-04T17:19:29
- Package: `C:\Users\Rong\Desktop\test_h5_files\daily_results\20250815`
- Spatial CSV: `C:\Users\Rong\Desktop\test_h5_files\daily_results\20250815\20250813_day2_spatial_stats_48h.csv`
- Hindcast H5: `C:\Users\Rong\Desktop\test_h5_files\20250815.h5`
- Forecast H5: `C:\Users\Rong\Desktop\test_h5_files\20250813.h5`
- Target date: `2025-08-15`
- Offset hours: `48`
- Valid spatial rows checked for percentile denominator: `231641`

## Method

1. Read the exported `spatial_stats` CSV.
2. Select deterministic cells: low mean error, median-like percentile, high mean error, and high standard deviation.
3. Open the original hindcast and forecast HDF5 files directly with `h5py`.
4. For each selected cell, read the 24 hourly scalar values from HDF5, applying the same vertical flip used by the pipeline.
5. Recompute absolute speed error, circular absolute direction error, mean, median, and population standard deviation.
6. Independently recompute percentile ranks from all valid spatial rows in the CSV.

## Summary

- Maximum absolute statistic difference across sampled cells: `7.8114783264e-06`
- Maximum absolute percentile difference across sampled cells: `3.63881673593e-06`

## Sample Cell Statistic Checks

### low mean cell row=319 col=378

- lon/lat: `119.785000`, `26.805000`
- CSV valid_count: `24`
- HDF5 included hours: `24` (2025-08-15 00:00:00 to 2025-08-15 23:00:00)

| Metric | CSV | Recomputed from HDF5 | Abs diff |
| --- | ---: | ---: | ---: |
| `mean_abs_error` | 0.001145494 | 0.001145494 | 4.91127138957e-11 |
| `median_abs_error` | 0.001056988 | 0.001056988 | 0 |
| `std_abs_error` | 0.000737944 | 0.000737944 | 1.8675878552e-11 |
| `mean_abs_dir_error` | 23.272289276 | 23.272288402 | 8.7420145789e-07 |
| `median_abs_dir_error` | 6.482013702 | 6.482013702 | 0 |
| `std_abs_dir_error` | 33.073966980 | 33.073966229 | 7.51416997957e-07 |
| `mean_truth_speed` | 0.004005736 | 0.004005736 | 1.98269844986e-10 |
| `mean_truth_direction` | 154.093460083 | 154.093454241 | 5.8424155327e-06 |

| Percentile field | CSV percentile | Recomputed rank | Abs diff |
| --- | ---: | ---: | ---: |
| `mean_abs_error` | 0.000000 | 0.000000 | 0 |
| `median_abs_error` | 0.000000 | 0.000000 | 0 |
| `std_abs_error` | 0.000000 | 0.000000 | 0 |
| `mean_abs_dir_error` | 78.836555 | 78.836557 | 1.24499703702e-06 |
| `median_abs_dir_error` | 34.179760 | 34.179762 | 1.71994034304e-06 |
| `std_abs_dir_error` | 87.832848 | 87.832844 | 3.52683287019e-06 |

### median-like percentile cell row=809 col=379

- lon/lat: `119.795000`, `21.905000`
- CSV valid_count: `24`
- HDF5 included hours: `24` (2025-08-15 00:00:00 to 2025-08-15 23:00:00)

| Metric | CSV | Recomputed from HDF5 | Abs diff |
| --- | ---: | ---: | ---: |
| `mean_abs_error` | 0.097670957 | 0.097670954 | 3.10440857743e-09 |
| `median_abs_error` | 0.068978585 | 0.068978585 | 0 |
| `std_abs_error` | 0.080643594 | 0.080643591 | 3.01707506201e-09 |
| `mean_abs_dir_error` | 31.840812683 | 31.840812102 | 5.8114528656e-07 |
| `median_abs_dir_error` | 14.172336578 | 14.172336578 | 0 |
| `std_abs_dir_error` | 31.666606903 | 31.666606842 | 6.11438437659e-08 |
| `mean_truth_speed` | 0.342900932 | 0.342900937 | 5.58793544769e-09 |
| `mean_truth_direction` | 349.358306885 | 349.358299073 | 7.8114783264e-06 |

| Percentile field | CSV percentile | Recomputed rank | Abs diff |
| --- | ---: | ---: | ---: |
| `mean_abs_error` | 64.414612 | 64.414609 | 2.9405644284e-06 |
| `median_abs_error` | 50.000000 | 50.000000 | 0 |
| `std_abs_error` | 82.466324 | 82.466327 | 3.2066907778e-06 |
| `mean_abs_dir_error` | 90.720947 | 90.720946 | 9.69648482396e-07 |
| `median_abs_dir_error` | 76.027458 | 76.027456 | 1.79305921222e-06 |
| `std_abs_dir_error` | 85.790451 | 85.790451 | 3.50443613684e-07 |

### high mean cell row=703 col=329

- lon/lat: `119.295000`, `22.965000`
- CSV valid_count: `24`
- HDF5 included hours: `24` (2025-08-15 00:00:00 to 2025-08-15 23:00:00)

| Metric | CSV | Recomputed from HDF5 | Abs diff |
| --- | ---: | ---: | ---: |
| `mean_abs_error` | 0.510676503 | 0.510676533 | 2.98023223877e-08 |
| `median_abs_error` | 0.485752493 | 0.485752493 | 0 |
| `std_abs_error` | 0.191820383 | 0.191820386 | 3.40971345603e-09 |
| `mean_abs_dir_error` | 35.238887787 | 35.238887529 | 2.58286796395e-07 |
| `median_abs_dir_error` | 24.652114868 | 24.652115822 | 9.53674316406e-07 |
| `std_abs_dir_error` | 37.802742004 | 37.802743474 | 1.4700278399e-06 |
| `mean_truth_speed` | 0.874547720 | 0.874547702 | 1.80055698129e-08 |
| `mean_truth_direction` | 72.621429443 | 72.621428319 | 1.12426582177e-06 |

| Percentile field | CSV percentile | Recomputed rank | Abs diff |
| --- | ---: | ---: | ---: |
| `mean_abs_error` | 100.000000 | 100.000000 | 0 |
| `median_abs_error` | 99.974533 | 99.974529 | 3.63881673593e-06 |
| `std_abs_error` | 99.376617 | 99.376619 | 1.45974256327e-06 |
| `mean_abs_dir_error` | 93.244690 | 93.244690 | 9.48569152115e-08 |
| `median_abs_dir_error` | 92.766365 | 92.766362 | 3.45569017668e-06 |
| `std_abs_dir_error` | 93.206268 | 93.206268 | 3.68887924651e-08 |

### high std cell row=562 col=215

- lon/lat: `118.155000`, `24.375000`
- CSV valid_count: `24`
- HDF5 included hours: `24` (2025-08-15 00:00:00 to 2025-08-15 23:00:00)

| Metric | CSV | Recomputed from HDF5 | Abs diff |
| --- | ---: | ---: | ---: |
| `mean_abs_error` | 0.213596761 | 0.213596756 | 4.96705374053e-09 |
| `median_abs_error` | 0.061882012 | 0.061882012 | 0 |
| `std_abs_error` | 0.406099200 | 0.406099196 | 4.20656176559e-09 |
| `mean_abs_dir_error` | 12.167696953 | 12.167696695 | 2.58286794619e-07 |
| `median_abs_dir_error` | 3.801895142 | 3.801895142 | 0 |
| `std_abs_dir_error` | 23.129596710 | 23.129595875 | 8.35099037033e-07 |
| `mean_truth_speed` | 0.823891699 | 0.823891688 | 1.17967525748e-08 |
| `mean_truth_direction` | 219.260604858 | 219.260600378 | 4.48031050837e-06 |

| Percentile field | CSV percentile | Recomputed rank | Abs diff |
| --- | ---: | ---: | ---: |
| `mean_abs_error` | 96.871437 | 96.871438 | 1.36620309377e-06 |
| `median_abs_error` | 43.663445 | 43.663443 | 1.24499703702e-06 |
| `std_abs_error` | 100.000000 | 100.000000 | 0 |
| `mean_abs_dir_error` | 44.587292 | 44.587291 | 1.09414818894e-06 |
| `median_abs_dir_error` | 11.524780 | 11.524780 | 4.4266561261e-07 |
| `std_abs_dir_error` | 72.948975 | 72.948973 | 2.06577286122e-06 |

## Threshold Count Table

| Check | Count |
| --- | ---: |
| mean_abs_error >= 0.2 kn | 9710 |
| median_abs_error >= 0.2 kn | 9264 |
| std_abs_error >= 0.2 kn | 1066 |
| mean_abs_error >= 0.3 kn | 1589 |
| median_abs_error >= 0.3 kn | 1334 |
| std_abs_error >= 0.3 kn | 40 |
| mean_abs_error >= 0.4 kn | 273 |
| median_abs_error >= 0.4 kn | 260 |
| std_abs_error >= 0.4 kn | 1 |
| mean_abs_error >= 0.5 kn | 21 |
| median_abs_error >= 0.5 kn | 30 |
| std_abs_error >= 0.5 kn | 0 |
| mean_abs_error >= 1.0 kn | 0 |
| median_abs_error >= 1.0 kn | 0 |
| std_abs_error >= 1.0 kn | 0 |
| mean_abs_dir_error >= 22.5 deg | 52501 |
| median_abs_dir_error >= 22.5 deg | 21189 |
| std_abs_dir_error >= 22.5 deg | 65096 |
| mean_abs_dir_error >= 30.0 deg | 25787 |
| median_abs_dir_error >= 30.0 deg | 10495 |
| std_abs_dir_error >= 30.0 deg | 38209 |
| mean_abs_dir_error >= 45.0 deg | 7251 |
| median_abs_dir_error >= 45.0 deg | 3066 |
| std_abs_dir_error >= 45.0 deg | 4898 |
| mean_abs_dir_error >= 60.0 deg | 1970 |
| median_abs_dir_error >= 60.0 deg | 1207 |
| std_abs_dir_error >= 60.0 deg | 135 |

## Interpretation

- The sampled CSV statistics match direct HDF5 recomputation within floating-point tolerance.
- Percentile fields match independent spatial-rank recomputation from the full valid-grid denominator.
- The threshold table is a reproducible count table for deciding and explaining warning criteria.
