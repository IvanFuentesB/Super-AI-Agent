# check_claude_swarm_dry_run.ps1 — N+6.37A PowerShell status checker
# Usage: .\check_claude_swarm_dry_run.ps1 [--json]

param([switch]$Json)

$ErrorActionPreference = "Stop"

$RepoRoot     = Resolve-Path (Join-Path $PSScriptRoot "..\..") | Select-Object -ExpandProperty Path
$WrapperScript = Join-Path $RepoRoot "03_scripts\claude_swarm_dry_run\ghoti_claude_swarm_dry_run.py"
$SchemaPath   = Join-Path $RepoRoot "14_context\claude_swarm_dry_run\claude_swarm_dry_run_status_schema.json"
$SandboxPath  = Join-Path $RepoRoot "21_repos\third_party_runtime_sandbox\claude_swarm"

$findings = @()
$ok = $true

# 1. Wrapper present
if (-not (Test-Path $WrapperScript)) { $findings += "MISSING: $WrapperScript"; $ok = $false }

# 2. Schema present
if (-not (Test-Path $SchemaPath)) { $findings += "MISSING: $SchemaPath"; $ok = $false }

# 3. No API key in env
if ($env:ANTHROPIC_API_KEY) {
    $findings += "SECURITY: ANTHROPIC_API_KEY is set — remove before running"
    $ok = $false
}

# 4. claude_swarm sandbox present (gitignored)
$sandboxPresent = Test-Path $SandboxPath

# 5. Sandbox not tracked by git
try {
    $tracked = & git -C $RepoRoot ls-files "21_repos/third_party_runtime_sandbox/claude_swarm" 2>&1
    if ($tracked -and ($tracked -notmatch "^\s*$")) {
        $findings += "GITIGNORE_VIOLATION: claude_swarm tracked by git"
        $ok = $false
    }
} catch {
    $findings += "GIT_CHECK_SKIPPED: $_"
}

# 6. Run wrapper --check
$checkOk = $false
$checkResult = $null
try {
    $raw = & python $WrapperScript --check --json 2>&1
    $checkResult = $raw | ConvertFrom-Json
    if ($checkResult.ok) { $checkOk = $true }
    else { $findings += "WRAPPER_CHECK_FAILED"; $ok = $false }
} catch {
    $findings += "WRAPPER_CHECK_SKIPPED: $_"
}

# 7. Run wrapper --probe
$probeOk = $false
try {
    $raw = & python $WrapperScript --probe --json 2>&1
    $probeResult = $raw | ConvertFrom-Json
    $probeOk = ($probeResult.ok -eq $true)
} catch {
    $findings += "PROBE_SKIPPED: $_"
}

$summary = [ordered]@{
    ok                    = $ok
    milestone             = "N+6.37A"
    wrapper_present       = (Test-Path $WrapperScript)
    schema_present        = (Test-Path $SchemaPath)
    api_key_present       = ($null -ne $env:ANTHROPIC_API_KEY)
    sandbox_present       = $sandboxPresent
    wrapper_check_ok      = $checkOk
    probe_ok              = $probeOk
    dry_run_status        = if ($checkResult) { $checkResult.dry_run_flag_status } else { "unknown" }
    findings              = $findings
}

if ($Json) {
    $summary | ConvertTo-Json -Depth 3
} else {
    Write-Host "[N+6.37A] ok=$($summary.ok) milestone=N+6.37A"
    Write-Host "  wrapper_present=$($summary.wrapper_present)  schema_present=$($summary.schema_present)"
    Write-Host "  api_key_present=$($summary.api_key_present)  sandbox_present=$($summary.sandbox_present)"
    Write-Host "  wrapper_check_ok=$($summary.wrapper_check_ok)  probe_ok=$($summary.probe_ok)"
    Write-Host "  dry_run_status: $($summary.dry_run_status)"
    if ($findings.Count -gt 0) {
        Write-Host "  findings:"
        foreach ($f in $findings) { Write-Host "    - $f" }
    }
}
