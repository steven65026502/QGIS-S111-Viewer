# Spatial Stats Validation Report

- Generated at: 2026-05-04T17:19:34
- Package: `C:\Users\Rong\Desktop\test_h5_files\daily_results\20250815`
- Spatial CSV: `C:\Users\Rong\Desktop\test_h5_files\daily_results\20250815\20250812_day3_spatial_stats_72h.csv`
- Hindcast H5: `C:\Users\Rong\Desktop\test_h5_files\20250815.h5`
- Forecast H5: `C:\Users\Rong\Desktop\test_h5_files\20250812.h5`
- Target date: `2025-08-15`
- Offset hours: `72`
- Valid spatial rows checked for percentile denominator: `231641`

## Method

1. Read the exported `spatial_stats` CSV.
2. Select deterministic cells: low mean error, median-like percentile, high mean error, and high standard deviation.
3. Open the original hindcast and forecast HDF5 files directly with `h5py`.
4. For each selected cell, read the 24 hourly scalar values from HDF5, applying the same vertical flip used by the pipeline.
5. Recompute absolute speed error, circular absolute direction error, mean, median, and population standard deviation.
6. Independently recompute percentile ranks from all valid spatial rows in the CSV.

## Summary

- Maximum absolute statistic difference across sampled cells: `5.8424155327e-06`
- Maximum absolute percentile difference across sampled cells: `2.52161304104e-06`

## Sample Cell Statistic Checks

### low mean cell row=319 col=378

- lon/lat: `119.785000`, `26.805000`
- CSV valid_count: `24`
- HDF5 included hours: `24` (2025-08-15 00:00:00 to 2025-08-15 23:00:00)

| Metric | CSV | Recomputed from HDF5 | Abs diff |
| --- | ---: | ---: | ---: |
| `mean_abs_error` | 0.000937111 | 0.000937111 | 2.48595218846e-11 |
| `median_abs_error` | 0.000966193 | 0.000966193 | 2.18278728426e-11 |
| `std_abs_error` | 0.000573288 | 0.000573288 | 1.42053827468e-12 |
| `mean_abs_dir_error` | 18.159339905 | 18.159339428 | 4.76837158203e-07 |
| `median_abs_dir_error` | 8.580810547 | 8.580810547 | 0 |
| `std_abs_dir_error` | 26.887168884 | 26.887169481 | 5.96516983364e-07 |
| `mean_truth_speed` | 0.004005736 | 0.004005736 | 1.98269844986e-10 |
| `mean_truth_direction` | 154.093460083 | 154.093454241 | 5.8424155327e-06 |

| Percentile field | CSV percentile | Recomputed rank | Abs diff |
| --- | ---: | ---: | ---: |
| `mean_abs_error` | 0.000000 | 0.000000 | 0 |
| `median_abs_error` | 0.000000 | 0.000000 | 0 |
| `std_abs_error` | 0.000000 | 0.000000 | 0 |
| `mean_abs_dir_error` | 57.333794 | 57.333794 | 1.77856719574e-07 |
| `median_abs_dir_error` | 40.341476 | 40.341478 | 1.71532924753e-06 |
| `std_abs_dir_error` | 71.969437 | 71.969435 | 1.3148222564e-06 |

### median-like percentile cell row=401 col=548

- lon/lat: `121.485000`, `25.985000`
- CSV valid_count: `24`
- HDF5 included hours: `24` (2025-08-15 00:00:00 to 2025-08-15 23:00:00)

| Metric | CSV | Recomputed from HDF5 | Abs diff |
| --- | ---: | ---: | ---: |
| `mean_abs_error` | 0.066407442 | 0.066407440 | 2.48352687027e-09 |
| `median_abs_error` | 0.080991313 | 0.080991313 | 0 |
| `std_abs_error` | 0.044384476 | 0.044384476 | 1.07354236611e-10 |
| `mean_abs_dir_error` | 12.797503471 | 12.797503312 | 1.58945718809e-07 |
| `median_abs_dir_error` | 10.172248840 | 10.172248840 | 0 |
| `std_abs_dir_error` | 10.802847862 | 10.802847837 | 2.52364422693e-08 |
| `mean_truth_speed` | 0.533314228 | 0.533314245 | 1.73846880225e-08 |
| `mean_truth_direction` | 328.233215332 | 328.233209902 | 5.43042762047e-06 |

| Percentile field | CSV percentile | Recomputed rank | Abs diff |
| --- | ---: | ---: | ---: |
| `mean_abs_error` | 28.482128 | 28.482127 | 7.04180862954e-07 |
| `median_abs_error` | 50.000000 | 50.000000 | 0 |
| `std_abs_error` | 29.849335 | 29.849335 | 4.58475099663e-07 |
| `mean_abs_dir_error` | 37.938179 | 37.938180 | 9.18267652139e-07 |
| `median_abs_dir_error` | 50.693317 | 50.693317 | 1.96959852872e-07 |
| `std_abs_dir_error` | 32.078224 | 32.078225 | 6.49506390005e-07 |

### high mean cell row=663 col=362

- lon/lat: `119.625000`, `23.365000`
- CSV valid_count: `24`
- HDF5 included hours: `24` (2025-08-15 00:00:00 to 2025-08-15 23:00:00)

| Metric | CSV | Recomputed from HDF5 | Abs diff |
| --- | ---: | ---: | ---: |
| `mean_abs_error` | 0.453522980 | 0.453522968 | 1.24176343097e-08 |
| `median_abs_error` | 0.354435563 | 0.354435563 | 0 |
| `std_abs_error` | 0.350123882 | 0.350123896 | 1.36571146059e-08 |
| `mean_abs_dir_error` | 41.266201019 | 41.266200701 | 3.17891441171e-07 |
| `median_abs_dir_error` | 30.211147308 | 30.211147070 | 2.38418579102e-07 |
| `std_abs_dir_error` | 38.818122864 | 38.818122521 | 3.4284295225e-07 |
| `mean_truth_speed` | 0.903154254 | 0.903154225 | 2.85605589179e-08 |
| `mean_truth_direction` | 37.512416840 | 37.512418736 | 1.8959452035e-06 |

| Percentile field | CSV percentile | Recomputed rank | Abs diff |
| --- | ---: | ---: | ---: |
| `mean_abs_error` | 100.000000 | 100.000000 | 0 |
| `median_abs_error` | 99.643410 | 99.643412 | 2.46232745837e-06 |
| `std_abs_error` | 99.996117 | 99.996115 | 1.97750323139e-06 |
| `mean_abs_dir_error` | 92.624763 | 92.624763 | 9.26172404547e-07 |
| `median_abs_dir_error` | 93.056465 | 93.056467 | 1.78251956129e-06 |
| `std_abs_dir_error` | 90.421341 | 90.421343 | 2.52161304104e-06 |

### high std cell row=589 col=456

- lon/lat: `120.565000`, `24.105000`
- CSV valid_count: `24`
- HDF5 included hours: `24` (2025-08-15 00:00:00 to 2025-08-15 23:00:00)

| Metric | CSV | Recomputed from HDF5 | Abs diff |
| --- | ---: | ---: | ---: |
| `mean_abs_error` | 0.369880915 | 0.369880904 | 1.11758708954e-08 |
| `median_abs_error` | 0.094374299 | 0.094374299 | 0 |
| `std_abs_error` | 0.607470036 | 0.607470011 | 2.41275359691e-08 |
| `mean_abs_dir_error` | 19.088300705 | 19.088300546 | 1.58945720585e-07 |
| `median_abs_dir_error` | 6.296409607 | 6.296409607 | 0 |
| `std_abs_dir_error` | 37.152416229 | 37.152414647 | 1.58216896295e-06 |
| `mean_truth_speed` | 1.223361015 | 1.223361031 | 1.55220429843e-08 |
| `mean_truth_direction` | 154.066879272 | 154.066879056 | 2.1608727252e-07 |

| Percentile field | CSV percentile | Recomputed rank | Abs diff |
| --- | ---: | ---: | ---: |
| `mean_abs_error` | 99.751770 | 99.751770 | 3.16189812111e-08 |
| `median_abs_error` | 60.421345 | 60.421343 | 1.29308421748e-06 |
| `std_abs_error` | 100.000000 | 100.000000 | 0 |
| `mean_abs_dir_error` | 60.435589 | 60.435590 | 8.71497924493e-07 |
| `median_abs_dir_error` | 24.519081 | 24.519081 | 2.1738043543e-07 |
| `std_abs_dir_error` | 88.565880 | 88.565878 | 1.73509110368e-06 |

## Threshold Count Table

| Check | Count |
| --- | ---: |
| mean_abs_error >= 0.2 kn | 15020 |
| median_abs_error >= 0.2 kn | 14232 |
| std_abs_error >= 0.2 kn | 959 |
| mean_abs_error >= 0.3 kn | 2044 |
| median_abs_error >= 0.3 kn | 2175 |
| std_abs_error >= 0.3 kn | 21 |
| mean_abs_error >= 0.4 kn | 290 |
| median_abs_error >= 0.4 kn | 376 |
| std_abs_error >= 0.4 kn | 4 |
| mean_abs_error >= 0.5 kn | 0 |
| median_abs_error >= 0.5 kn | 11 |
| std_abs_error >= 0.5 kn | 2 |
| mean_abs_error >= 1.0 kn | 0 |
| median_abs_error >= 1.0 kn | 0 |
| std_abs_error >= 1.0 kn | 0 |
| mean_abs_dir_error >= 22.5 deg | 68466 |
| median_abs_dir_error >= 22.5 deg | 27458 |
| std_abs_dir_error >= 22.5 deg | 84832 |
| mean_abs_dir_error >= 30.0 deg | 36149 |
| median_abs_dir_error >= 30.0 deg | 16325 |
| std_abs_dir_error >= 30.0 deg | 52536 |
| mean_abs_dir_error >= 45.0 deg | 13030 |
| median_abs_dir_error >= 45.0 deg | 5861 |
| std_abs_dir_error >= 45.0 deg | 10747 |
| mean_abs_dir_error >= 60.0 deg | 4241 |
| median_abs_dir_error >= 60.0 deg | 2461 |
| std_abs_dir_error >= 60.0 deg | 289 |

## Interpretation

- The sampled CSV statistics match direct HDF5 recomputation within floating-point tolerance.
- Percentile fields match independent spatial-rank recomputation from the full valid-grid denominator.
- The threshold table is a reproducible count table for deciding and explaining warning criteria.
