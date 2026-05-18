param(
    [string]$DbName = "s111_verification",
    [string]$PgUser = "postgres",
    [string]$PgHost = "localhost",
    [string]$PgPort = "5432",
    [switch]$Overwrite
)

$ErrorActionPreference = "Stop"

$DumpPath = Join-Path $PSScriptRoot "s111_verification_20260514_0p48_median_metrics.dump"
if (!(Test-Path -LiteralPath $DumpPath)) {
    throw "找不到 dump 檔：$DumpPath"
}

$candidateBins = @(
    "C:\Program Files\PostgreSQL\16\bin",
    "C:\Program Files\PostgreSQL\15\bin",
    "C:\Program Files\PostgreSQL\14\bin"
)

$pgBin = $candidateBins | Where-Object {
    (Test-Path (Join-Path $_ "createdb.exe")) -and
    (Test-Path (Join-Path $_ "pg_restore.exe"))
} | Select-Object -First 1

if (-not $pgBin) {
    throw "找不到 PostgreSQL bin 目錄，請先安裝 PostgreSQL，或手動把 createdb.exe / pg_restore.exe 加入 PATH。"
}

$createdb = Join-Path $pgBin "createdb.exe"
$dropdb = Join-Path $pgBin "dropdb.exe"
$psql = Join-Path $pgBin "psql.exe"
$pgRestore = Join-Path $pgBin "pg_restore.exe"

$plainPassword = Read-Host "請輸入 PostgreSQL 使用者 $PgUser 的密碼"
$env:PGPASSWORD = $plainPassword

$dbExists = (& $psql -h $PgHost -p $PgPort -U $PgUser -d postgres -tAc "SELECT 1 FROM pg_database WHERE datname = '$DbName'").Trim()
if ($dbExists -eq "1") {
    if (-not $Overwrite) {
        Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
        throw "資料庫 $DbName 已經存在。請改用其他名稱，例如：.\restore_s111_verification.ps1 -DbName s111_verification_20260514_0p48_median_metrics，或確認要覆蓋後加上 -Overwrite。"
    }

    Write-Host "資料庫 $DbName 已存在，準備覆蓋..."
    & $psql -h $PgHost -p $PgPort -U $PgUser -d postgres -c "SELECT pg_terminate_backend(pid) FROM pg_stat_activity WHERE datname = '$DbName' AND pid <> pg_backend_pid();"
    if ($LASTEXITCODE -ne 0) { throw "無法中止 $DbName 的現有連線。" }

    & $dropdb -h $PgHost -p $PgPort -U $PgUser $DbName
    if ($LASTEXITCODE -ne 0) { throw "刪除既有資料庫 $DbName 失敗。" }
}

Write-Host "建立資料庫 $DbName ..."
& $createdb -h $PgHost -p $PgPort -U $PgUser $DbName
if ($LASTEXITCODE -ne 0) { throw "建立資料庫 $DbName 失敗。" }

Write-Host "還原 dump：$DumpPath"
& $pgRestore -h $PgHost -p $PgPort -U $PgUser -d $DbName $DumpPath
if ($LASTEXITCODE -ne 0) { throw "還原 dump 失敗。" }

Remove-Item Env:PGPASSWORD -ErrorAction SilentlyContinue
Write-Host "完成：$DbName"
