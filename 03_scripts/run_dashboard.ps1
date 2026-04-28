# Ghoti Operator Dashboard Launcher
# Starts the Node.js dashboard server at http://localhost:3210
# No service installed. No auto-start. Operator-triggered only.

param(
    [switch]$OpenBrowser
)

$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$DashboardDir = Join-Path $RepoRoot "01_projects\dashboard_mvp"
$ServerJs = Join-Path $DashboardDir "server.js"

if (-not (Test-Path $ServerJs)) {
    Write-Error "server.js not found at: $ServerJs"
    exit 1
}

Write-Host "Ghoti Dashboard — starting..."
Write-Host "Repo root : $RepoRoot"
Write-Host "Dashboard : $DashboardDir"
Write-Host "URL       : http://localhost:3210"
Write-Host ""
Write-Host "Press Ctrl+C to stop."
Write-Host ""

if ($OpenBrowser) {
    Start-Process "http://localhost:3210"
}

Set-Location $DashboardDir
node server.js
