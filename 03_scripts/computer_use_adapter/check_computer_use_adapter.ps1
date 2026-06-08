# check_computer_use_adapter.ps1
# N+6.29A Computer-Use Adapter system check (PowerShell)
# Runs the adapter --check and validates key safety fields.
# No real OS actions; dry-run only.

param(
    [string]$AdapterScript = "03_scripts/computer_use_adapter/ghoti_computer_use_adapter.py",
    [string]$ExampleAllowed = "14_context/computer_use_adapter/examples/dry_run_local_fixture_action.json",
    [string]$ExampleBlocked = "14_context/computer_use_adapter/examples/blocked_external_website_action.json",
    [switch]$Verbose
)

$ErrorActionPreference = "Stop"
$passed = 0
$failed = 0
$errors = @()

function Assert-Field {
    param($obj, $field, $expected, $label)
    $val = $obj.$field
    if ($null -eq $val) { $val = $obj | Select-Object -ExpandProperty $field -ErrorAction SilentlyContinue }
    if ($val -eq $expected) {
        $script:passed++
        if ($Verbose) { Write-Host "  PASS $label : $field = $val" -ForegroundColor Green }
    } else {
        $script:failed++
        $script:errors += "FAIL $label : $field expected=$expected got=$val"
        Write-Host "  FAIL $label : $field expected=$expected got=$val" -ForegroundColor Red
    }
}

Write-Host "`n=== N+6.29A Computer-Use Adapter Check ===" -ForegroundColor Cyan

# 1. System check
Write-Host "`n[1] Running --check ..." -ForegroundColor Yellow
$checkRaw = python $AdapterScript --check --json 2>&1
try {
    $check = $checkRaw | ConvertFrom-Json
} catch {
    Write-Host "FAIL: could not parse --check JSON output" -ForegroundColor Red
    Write-Host $checkRaw
    exit 1
}

Assert-Field $check "ok" $true "--check"
Assert-Field $check "mode" "dry_run" "--check"
Assert-Field $check "computer_use_enabled" $false "--check"
Assert-Field $check "live_browser_enabled" $false "--check"
Assert-Field $check "real_os_input_enabled" $false "--check"
Assert-Field $check "auto_submit_enabled" $false "--check"
Assert-Field $check "docker_enabled" $false "--check"
Assert-Field $check "mcp_enabled" $false "--check"
Assert-Field $check "secrets_access_enabled" $false "--check"
Assert-Field $check "rust_policy_bridge_ready" $false "--check"

# 2. Allowed plan
Write-Host "`n[2] Running --plan (allowed) ..." -ForegroundColor Yellow
$allowedRaw = python $AdapterScript --plan $ExampleAllowed --dry-run --json 2>&1
try {
    $allowed = $allowedRaw | ConvertFrom-Json
} catch {
    Write-Host "FAIL: could not parse allowed plan JSON output" -ForegroundColor Red
    Write-Host $allowedRaw
    exit 1
}

Assert-Field $allowed "ok" $true "allowed-plan"
Assert-Field $allowed "status" "allowed" "allowed-plan"
Assert-Field $allowed "mode" "dry_run" "allowed-plan"
Assert-Field $allowed "real_action_performed" $false "allowed-plan"
Assert-Field $allowed "real_click_performed" $false "allowed-plan"
Assert-Field $allowed "real_type_performed" $false "allowed-plan"
Assert-Field $allowed "os_input_used" $false "allowed-plan"
Assert-Field $allowed "secrets_accessed" $false "allowed-plan"
Assert-Field $allowed "auto_submit_performed" $false "allowed-plan"
Assert-Field $allowed "target_verified" $true "allowed-plan"
Assert-Field $allowed.arena_status "simulation" $true "allowed-plan.arena_status"
Assert-Field $allowed.arena_status "live_execution" $false "allowed-plan.arena_status"
Assert-Field $allowed.arena_status "live_computer_use_enabled" $false "allowed-plan.arena_status"
Assert-Field $allowed.safety "dry_run_only" $true "allowed-plan.safety"
Assert-Field $allowed.safety "no_real_os_input" $true "allowed-plan.safety"
Assert-Field $allowed.safety "no_live_browser" $true "allowed-plan.safety"
Assert-Field $allowed.safety "real_action_performed" $false "allowed-plan.safety"

# 3. Blocked plan
Write-Host "`n[3] Running --plan (blocked) ..." -ForegroundColor Yellow
$blockedRaw = python $AdapterScript --plan $ExampleBlocked --dry-run --json 2>&1
try {
    $blocked = $blockedRaw | ConvertFrom-Json
} catch {
    Write-Host "FAIL: could not parse blocked plan JSON output" -ForegroundColor Red
    Write-Host $blockedRaw
    exit 1
}

Assert-Field $blocked "ok" $false "blocked-plan"
Assert-Field $blocked "status" "blocked" "blocked-plan"
Assert-Field $blocked "mode" "dry_run" "blocked-plan"
Assert-Field $blocked "real_action_performed" $false "blocked-plan"
Assert-Field $blocked "os_input_used" $false "blocked-plan"

if ($blocked.blocked_reasons.Count -gt 0) {
    $passed++
    if ($Verbose) { Write-Host "  PASS blocked-plan: blocked_reasons.Count=$($blocked.blocked_reasons.Count)" -ForegroundColor Green }
} else {
    $failed++
    $errors += "FAIL blocked-plan: blocked_reasons should not be empty"
    Write-Host "  FAIL blocked-plan: blocked_reasons should not be empty" -ForegroundColor Red
}

# Summary
Write-Host "`n=== Summary ===" -ForegroundColor Cyan
Write-Host "Passed : $passed" -ForegroundColor Green
Write-Host "Failed : $failed" -ForegroundColor $(if ($failed -gt 0) { "Red" } else { "Green" })

if ($errors.Count -gt 0) {
    Write-Host "`nFailures:" -ForegroundColor Red
    $errors | ForEach-Object { Write-Host "  $_" -ForegroundColor Red }
}

$result = @{
    ok = ($failed -eq 0)
    milestone = "N+6.29A"
    passed = $passed
    failed = $failed
    errors = $errors
}
$result | ConvertTo-Json -Depth 3

if ($failed -gt 0) { exit 1 } else { exit 0 }
