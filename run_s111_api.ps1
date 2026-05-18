param(
    [string]$HostAddress = "127.0.0.1",
    [int]$Port = 8111
)

$ErrorActionPreference = "Stop"

$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
Set-Location $scriptDir

Write-Host "Starting S-111 Verification API..."
Write-Host "URL: http://$HostAddress`:$Port/api"
Write-Host ""
Write-Host "Press Ctrl+C to stop."

python .\scripts\s111_api_server.py --host $HostAddress --port $Port
