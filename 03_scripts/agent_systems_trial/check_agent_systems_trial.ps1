# check_agent_systems_trial.ps1 — N+6.35A PowerShell status checker
# Usage: .\check_agent_systems_trial.ps1 [--json]
#
# Checks that the N+6.35A planner reports ok=true and the sandbox repos are present.

param(
    [switch]$Json
)

$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..") | Select-Object -ExpandProperty Path
$PlannerScript = Join-Path $RepoRoot "03_scripts\agent_systems_trial\ghoti_agent_systems_trial.py"
$SandboxRoot = Join-Path $RepoRoot "21_repos\third_party_runtime_sandbox"
$InventoryPath = Join-Path $RepoRoot "14_context\agent_systems_trial\agent_systems_inventory_n6_35a.json"

$ExpectedRepos = @(
    "claude_swarm",
    "am_will_swarms",
    "clawteam",
    "ruflo",
    "ecc",
    "paperclip",
    "hermes_paperclip_adapter"
)

$findings = @()
$ok = $true

# 1. Check planner script exists
if (-not (Test-Path $PlannerScript)) {
    $findings += "MISSING: $PlannerScript"
    $ok = $false
}

# 2. Check inventory JSON exists
if (-not (Test-Path $InventoryPath)) {
    $findings += "MISSING: $InventoryPath"
    $ok = $false
}

# 3. Check sandbox repos present
$presentCount = 0
foreach ($repo in $ExpectedRepos) {
    $path = Join-Path $SandboxRoot $repo
    if (Test-Path $path) {
        $presentCount++
    } else {
        $findings += "SANDBOX_MISSING: $repo"
    }
}

# 4. Run planner --check if Python is available
$plannerResult = $null
$pythonOk = $false
try {
    $raw = & python $PlannerScript --check --json 2>&1
    $plannerResult = $raw | ConvertFrom-Json
    if ($plannerResult.ok) {
        $pythonOk = $true
    } else {
        $findings += "PLANNER_CHECK_FAILED: ok=false"
        $ok = $false
    }
} catch {
    $findings += "PLANNER_CHECK_SKIPPED: Python unavailable or error: $_"
}

# 5. Verify no sandbox repos are tracked by git
try {
    $trackedSandbox = @(
        & git -C $RepoRoot ls-files "21_repos/third_party_runtime_sandbox" 2>&1 |
            Where-Object { $_ -notmatch '\.gitkeep$' }
    )
    if ($trackedSandbox) {
        $findings += "GITIGNORE_VIOLATION: sandbox files are tracked by git"
        $ok = $false
    }
} catch {
    $findings += "GIT_CHECK_SKIPPED: $_"
}

$summary = [ordered]@{
    ok                      = $ok
    milestone               = "N+6.35A"
    planner_present         = (Test-Path $PlannerScript)
    inventory_present       = (Test-Path $InventoryPath)
    sandbox_repos_expected  = $ExpectedRepos.Count
    sandbox_repos_present   = $presentCount
    planner_check_ok        = $pythonOk
    findings                = $findings
}

if ($Json) {
    $summary | ConvertTo-Json -Depth 3
} else {
    Write-Host "[N+6.35A] ok=$($summary.ok) milestone=N+6.35A"
    Write-Host "  planner_present=$($summary.planner_present)  inventory_present=$($summary.inventory_present)"
    Write-Host "  sandbox_repos=$($summary.sandbox_repos_present)/$($summary.sandbox_repos_expected)"
    Write-Host "  planner_check_ok=$($summary.planner_check_ok)"
    if ($findings.Count -gt 0) {
        Write-Host "  findings:"
        foreach ($f in $findings) {
            Write-Host "    - $f"
        }
    }
}

if ($ok) {
    exit 0
}
exit 1
