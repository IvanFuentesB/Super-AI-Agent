# check_agent_system_adapter.ps1 — N+6.36A PowerShell status checker
# Usage: .\check_agent_system_adapter.ps1 [--json]

param([switch]$Json)

$ErrorActionPreference = "Stop"

$RepoRoot = Resolve-Path (Join-Path $PSScriptRoot "..\..") | Select-Object -ExpandProperty Path
$AdapterScript = Join-Path $RepoRoot "03_scripts\agent_system_adapter\ghoti_agent_system_adapter.py"
$SandboxRoot   = Join-Path $RepoRoot "21_repos\third_party_runtime_sandbox"
$SchemaPath    = Join-Path $RepoRoot "14_context\agent_system_adapter\agent_system_adapter_status_schema.json"

$findings = @()
$ok = $true

# 1. Adapter script present
if (-not (Test-Path $AdapterScript)) { $findings += "MISSING: $AdapterScript"; $ok = $false }

# 2. Schema file present
if (-not (Test-Path $SchemaPath)) { $findings += "MISSING: $SchemaPath"; $ok = $false }

# 3. claude_swarm sandbox present
$claudeSwarmPath = Join-Path $SandboxRoot "claude_swarm"
$swarmPresent = Test-Path $claudeSwarmPath

# 4. No claude_swarm code tracked by git
$adapterCheckOk = $false
try {
    $tracked = & git -C $RepoRoot ls-files "21_repos/third_party_runtime_sandbox/claude_swarm" 2>&1
    if ($tracked -and ($tracked -notmatch "^\s*$")) {
        $findings += "GITIGNORE_VIOLATION: claude_swarm files tracked by git"
        $ok = $false
    }
} catch {
    $findings += "GIT_CHECK_SKIPPED: $_"
}

# 5. Run adapter --check
$checkResult = $null
try {
    $raw = & python $AdapterScript --check --json 2>&1
    $checkResult = $raw | ConvertFrom-Json
    if ($checkResult.ok) {
        $adapterCheckOk = $true
    } else {
        $findings += "ADAPTER_CHECK_FAILED: ok=false"
        $ok = $false
    }
} catch {
    $findings += "ADAPTER_CHECK_SKIPPED: $_"
}

# 6. Run adapter --smoke (if sandbox present)
$smokeOk = $false
if ($swarmPresent) {
    try {
        $raw = & python $AdapterScript --smoke --json 2>&1
        $smokeResult = $raw | ConvertFrom-Json
        if ($smokeResult.ok -and $smokeResult.accepted) {
            $smokeOk = $true
        } else {
            $findings += "SMOKE_FAILED: accepted=$($smokeResult.accepted)"
        }
    } catch {
        $findings += "SMOKE_SKIPPED: $_"
    }
}

$summary = [ordered]@{
    ok                    = $ok
    milestone             = "N+6.36A"
    adapter_present       = (Test-Path $AdapterScript)
    schema_present        = (Test-Path $SchemaPath)
    sandbox_swarm_present = $swarmPresent
    adapter_check_ok      = $adapterCheckOk
    smoke_ok              = $smokeOk
    findings              = $findings
}

if ($Json) {
    $summary | ConvertTo-Json -Depth 3
} else {
    Write-Host "[N+6.36A] ok=$($summary.ok) milestone=N+6.36A"
    Write-Host "  adapter_present=$($summary.adapter_present)  schema_present=$($summary.schema_present)"
    Write-Host "  sandbox_swarm_present=$($summary.sandbox_swarm_present)"
    Write-Host "  adapter_check_ok=$($summary.adapter_check_ok)  smoke_ok=$($summary.smoke_ok)"
    if ($findings.Count -gt 0) {
        Write-Host "  findings:"
        foreach ($f in $findings) { Write-Host "    - $f" }
    }
}
