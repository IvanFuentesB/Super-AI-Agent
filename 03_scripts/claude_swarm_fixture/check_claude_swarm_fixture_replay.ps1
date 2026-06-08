# check_claude_swarm_fixture_replay.ps1
# N+6.38A — Provider-free claude-swarm fixture replay checker (PowerShell)
#
# Validates the fixture replay system without executing claude-swarm or calling any provider.
# Safe to run on any machine — no API keys required, no network calls made.
#
# Usage:
#   .\check_claude_swarm_fixture_replay.ps1
#   .\check_claude_swarm_fixture_replay.ps1 -Verbose
#   .\check_claude_swarm_fixture_replay.ps1 -FixturePath "14_context\claude_swarm_fixture\sample_claude_swarm_plan.json"

param(
    [string]$FixturePath = "14_context\claude_swarm_fixture\sample_claude_swarm_plan.json",
    [switch]$Verbose
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$WrapperScript = Join-Path $PSScriptRoot "ghoti_claude_swarm_fixture_replay.py"
$SchemaPath = Join-Path $RepoRoot "14_context\claude_swarm_fixture\claude_swarm_fixture_schema.json"
$FullFixturePath = Join-Path $RepoRoot $FixturePath

$Results = @()
$Passed = 0
$Failed = 0

function Add-Result {
    param([string]$Name, [bool]$Pass, [string]$Detail = "")
    $script:Results += [PSCustomObject]@{ Name = $Name; Pass = $Pass; Detail = $Detail }
    if ($Pass) { $script:Passed++ } else { $script:Failed++ }
    $icon = if ($Pass) { "[PASS]" } else { "[FAIL]" }
    $color = if ($Pass) { "Green" } else { "Red" }
    Write-Host "$icon $Name" -ForegroundColor $color
    if ($Verbose -and $Detail) { Write-Host "       $Detail" -ForegroundColor Gray }
}

Write-Host "`n=== N+6.38A Claude-Swarm Fixture Replay Checker ===" -ForegroundColor Cyan
Write-Host "Repo root: $RepoRoot"
Write-Host "Fixture:   $FullFixturePath`n"

# 1. Python available
try {
    $pyVersion = python --version 2>&1
    Add-Result "Python available" $true $pyVersion
} catch {
    Add-Result "Python available" $false "python not found in PATH"
}

# 2. Wrapper script exists
$wrapperExists = Test-Path $WrapperScript
Add-Result "Wrapper script exists" $wrapperExists $WrapperScript

# 3. Fixture file exists
$fixtureExists = Test-Path $FullFixturePath
Add-Result "Fixture file exists" $fixtureExists $FullFixturePath

# 4. Schema file exists
$schemaExists = Test-Path $SchemaPath
Add-Result "Schema file exists" $schemaExists $SchemaPath

# 5. Fixture is valid JSON
if ($fixtureExists) {
    try {
        $fixtureJson = Get-Content $FullFixturePath -Raw | ConvertFrom-Json
        Add-Result "Fixture is valid JSON" $true
    } catch {
        Add-Result "Fixture is valid JSON" $false $_.Exception.Message
        $fixtureJson = $null
    }
} else {
    Add-Result "Fixture is valid JSON" $false "file not found"
    $fixtureJson = $null
}

# 6. Fixture source == "static_fixture"
if ($fixtureJson) {
    $sourceOk = $fixtureJson.source -eq "static_fixture"
    Add-Result "Fixture source is static_fixture" $sourceOk "source=$($fixtureJson.source)"
}

# 7. Fixture swarm.live_execution == false
if ($fixtureJson) {
    $liveOk = $fixtureJson.swarm.live_execution -eq $false
    Add-Result "swarm.live_execution is false" $liveOk "live_execution=$($fixtureJson.swarm.live_execution)"
}

# 8. Fixture swarm.simulation == true
if ($fixtureJson) {
    $simOk = $fixtureJson.swarm.simulation -eq $true
    Add-Result "swarm.simulation is true" $simOk "simulation=$($fixtureJson.swarm.simulation)"
}

# 9. Fixture safety.live_agent_launch == false
if ($fixtureJson) {
    $agentOk = $fixtureJson.safety.live_agent_launch -eq $false
    Add-Result "safety.live_agent_launch is false" $agentOk "live_agent_launch=$($fixtureJson.safety.live_agent_launch)"
}

# 10. Fixture safety.api_key_used == false
if ($fixtureJson) {
    $apiOk = $fixtureJson.safety.api_key_used -eq $false
    Add-Result "safety.api_key_used is false" $apiOk "api_key_used=$($fixtureJson.safety.api_key_used)"
}

# 11. Fixture has tasks array with at least 1 task
if ($fixtureJson) {
    $taskCount = if ($fixtureJson.tasks) { $fixtureJson.tasks.Count } else { 0 }
    $tasksOk = $taskCount -gt 0
    Add-Result "Fixture has tasks" $tasksOk "task_count=$taskCount"
}

# 12. No API key env vars set
$apiKeyVars = @("ANTHROPIC_API_KEY", "CLAUDE_API_KEY", "OPENAI_API_KEY")
$presentKeys = $apiKeyVars | Where-Object { [System.Environment]::GetEnvironmentVariable($_) }
$noApiKeys = $presentKeys.Count -eq 0
$keyDetail = if ($noApiKeys) { "none present" } else { "FOUND: $($presentKeys -join ', ') — replay blocked" }
Add-Result "No provider API keys in env" $noApiKeys $keyDetail

# 13. Wrapper script does not import claude_swarm
if ($wrapperExists) {
    $wrapperContent = Get-Content $WrapperScript -Raw
    $noImport = -not ($wrapperContent -match "^import claude_swarm|^from claude_swarm")
    Add-Result "Wrapper does not import claude_swarm" $noImport
}

# 14. Wrapper script contains MILESTONE N+6.38A
if ($wrapperExists) {
    $hasMilestone = $wrapperContent -match "N\+6\.38A"
    Add-Result "Wrapper declares milestone N+6.38A" $hasMilestone
}

# 15. Run --check via Python wrapper
if ($wrapperExists) {
    try {
        $checkOutput = python $WrapperScript --check 2>&1 | Out-String
        $checkPassed = $LASTEXITCODE -eq 0
        Add-Result "Wrapper --check exits 0" $checkPassed "exit=$LASTEXITCODE"
        if ($Verbose) { Write-Host "  Output: $($checkOutput.Trim())" -ForegroundColor Gray }
    } catch {
        Add-Result "Wrapper --check exits 0" $false $_.Exception.Message
    }
}

# 16. Run --validate via Python wrapper
if ($wrapperExists -and $fixtureExists) {
    try {
        $validateOutput = python $WrapperScript --validate --fixture $FullFixturePath 2>&1 | Out-String
        $validatePassed = $LASTEXITCODE -eq 0
        Add-Result "Wrapper --validate exits 0" $validatePassed "exit=$LASTEXITCODE"
        if ($Verbose) { Write-Host "  Output: $($validateOutput.Trim())" -ForegroundColor Gray }
    } catch {
        Add-Result "Wrapper --validate exits 0" $false $_.Exception.Message
    }
}

# 17. Run --replay via Python wrapper (only if no API keys)
if ($wrapperExists -and $fixtureExists -and $noApiKeys) {
    try {
        $replayOutput = python $WrapperScript --replay 2>&1 | Out-String
        $replayPassed = $LASTEXITCODE -eq 0
        Add-Result "Wrapper --replay exits 0" $replayPassed "exit=$LASTEXITCODE"
        if ($Verbose) { Write-Host "  Output: $($replayOutput.Trim())" -ForegroundColor Gray }
    } catch {
        Add-Result "Wrapper --replay exits 0" $false $_.Exception.Message
    }
} elseif (-not $noApiKeys) {
    Add-Result "Wrapper --replay exits 0" $false "SKIPPED: API key present — would be blocked"
}

# Summary
$Total = $Passed + $Failed
Write-Host "`n--- Summary ---" -ForegroundColor Cyan
Write-Host "Passed: $Passed / $Total"
if ($Failed -gt 0) {
    Write-Host "Failed: $Failed" -ForegroundColor Red
    $Results | Where-Object { -not $_.Pass } | ForEach-Object {
        Write-Host "  FAIL: $($_.Name)  $($_.Detail)" -ForegroundColor Red
    }
    exit 1
} else {
    Write-Host "All checks passed." -ForegroundColor Green
    exit 0
}
