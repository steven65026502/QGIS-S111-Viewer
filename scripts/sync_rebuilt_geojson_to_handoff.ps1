param(
    [string]$SourceRoot = "C:\Users\Rong\Desktop\test_h5_files\daily_results",
    [string]$HandoffRoot = $env:S111_HANDOFF_ROOT
)

$ErrorActionPreference = "Stop"

if (-not (Test-Path -LiteralPath $SourceRoot)) {
    throw "SourceRoot not found: $SourceRoot"
}
if (-not $HandoffRoot) {
    throw "HandoffRoot is empty. Set S111_HANDOFF_ROOT or pass -HandoffRoot."
}
if (-not (Test-Path -LiteralPath $HandoffRoot)) {
    throw "HandoffRoot not found: $HandoffRoot"
}

$dateDirs = Get-ChildItem -LiteralPath $HandoffRoot -Recurse -Directory |
    Where-Object { $_.Name -match '^\d{8}$' } |
    Sort-Object FullName

$dailyCopied = 0
$metricCopied = 0
$skipped = 0

foreach ($targetDateDir in $dateDirs) {
    $dateText = $targetDateDir.Name
    $sourceDateDir = Join-Path $SourceRoot $dateText
    if (-not (Test-Path -LiteralPath $sourceDateDir)) {
        $skipped += 1
        Write-Output "[skip] $dateText source package not found"
        continue
    }

    $dailyTarget = Get-ChildItem -LiteralPath $targetDateDir.FullName -Directory |
        Where-Object { $_.Name -like "*daily_hotspots" } |
        Select-Object -First 1
    if ($dailyTarget) {
        $dailySource = Join-Path $sourceDateDir "${dateText}_hotspots.geojson"
        if (Test-Path -LiteralPath $dailySource) {
            Copy-Item -LiteralPath $dailySource -Destination $dailyTarget.FullName -Force
            $dailyCopied += 1
        }
    }

    $metricTarget = Get-ChildItem -LiteralPath $targetDateDir.FullName -Directory |
        Where-Object { $_.Name -like "*metric_hotspots" } |
        Select-Object -First 1
    if ($metricTarget) {
        $metricSources = Get-ChildItem -LiteralPath $sourceDateDir -File -Filter "*.metric_hotspots.geojson"
        foreach ($metricSource in $metricSources) {
            Copy-Item -LiteralPath $metricSource.FullName -Destination $metricTarget.FullName -Force
            $metricCopied += 1
        }
    }

    Write-Output "[sync] $dateText daily_total=$dailyCopied metric_total=$metricCopied"
}

Write-Output "[summary] daily_geojson_copied=$dailyCopied metric_geojson_copied=$metricCopied skipped=$skipped"
