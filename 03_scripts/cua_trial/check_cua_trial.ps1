# check_cua_trial.ps1 - N+6.34A CUA Trial Adapter System Check
# Dry-run only. No real CUA execution. No OS input. No Docker/VM.
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File 03_scripts/cua_trial/check_cua_trial.ps1
#
# This script runs the Python adapter's --check mode and reports readiness.
# It does NOT clone CUA, run any CUA code, or perform any live action.

$ErrorActionPreference = "Stop"
$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$AdapterScript = Join-Path $PSScriptRoot "ghoti_cua_trial_adapter.py"

Write-Host "[N+6.34A] CUA Trial Adapter - system check" -ForegroundColor Cyan

if (-not (Test-Path $AdapterScript)) {
    Write-Host "MISSING: $AdapterScript" -ForegroundColor Red
    exit 1
}

# System check (no CUA required)
$checkResult = python "$AdapterScript" --check --json 2>&1
if ($LASTEXITCODE -ne 0) {
    Write-Host "FAILED: adapter --check returned $LASTEXITCODE" -ForegroundColor Red
    Write-Host $checkResult
    exit 1
}
$check = $checkResult | ConvertFrom-Json
Write-Host "  check:             $($check.check)"
Write-Host "  bridge_available:  $($check.bridge_available)"
Write-Host "  cua_code_imported: $($check.cua_code_imported)"
Write-Host "  cua_code_executed: $($check.cua_code_executed)"
Write-Host "  live_os_enabled:   $($check.live_os_input_enabled)"
Write-Host "  docker_vm_enabled: $($check.docker_vm_enabled)"

# Sandbox presence (informational)
$sandboxPath = Join-Path $RepoRoot "21_repos\third_party_runtime_sandbox\cua"
if (Test-Path $sandboxPath) {
    Write-Host "  cua_sandbox:       present ($sandboxPath)" -ForegroundColor Green
    Write-Host "  NOTE: Run --trial to perform metadata smoke." -ForegroundColor Yellow
} else {
    Write-Host "  cua_sandbox:       ABSENT - clone with:" -ForegroundColor Yellow
    Write-Host "    git clone --depth=1 --no-tags --template='' https://github.com/trycua/cua $sandboxPath" -ForegroundColor Yellow
}

if ($check.ok -eq $true) {
    Write-Host "[N+6.34A] check: PASS" -ForegroundColor Green
    exit 0
} else {
    Write-Host "[N+6.34A] check: FAIL" -ForegroundColor Red
    exit 1
}
