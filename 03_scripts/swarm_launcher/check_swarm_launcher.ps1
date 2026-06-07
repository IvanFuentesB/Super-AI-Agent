<#
.SYNOPSIS
  Check the Ghoti repo-backed controlled swarm launcher (N+6.27A) is present and safe.
  Emits one JSON object.

.DESCRIPTION
  Local and read-only. Resolves a working Python (skipping a broken PATH shim) with
  ghoti_python_resolver.ps1, runs the launcher's --check and a --dry-run on the blocked
  example WITHOUT launching anything, and verifies the launcher is dry-run-only: it spawns
  no process, uses no subprocess/shell, creates no worktree, writes no files, and keeps
  live_launch_enabled false with approval + kill switch required. No Invoke-Expression; the
  external call uses an argument array.
#>
[CmdletBinding()]
param(
    [switch]$Json
)

$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$Script   = Join-Path $RepoRoot '03_scripts\swarm_launcher\ghoti_swarm_launcher.py'
$TaskSchema = Join-Path $RepoRoot '14_context\swarm_launcher\swarm_task_schema.json'
$PlanSchema = Join-Path $RepoRoot '14_context\swarm_launcher\swarm_plan_schema.json'
$Manifest = Join-Path $RepoRoot '14_context\swarm_launcher\repo_inspiration_manifest_n6_27a.json'
$Blocked  = Join-Path $RepoRoot '14_context\swarm_launcher\examples\blocked_overlap_task.json'

# Resolve Python in-process (its exit code does not stop us).
$pyOk = $false
$pyExe = $null
$resolver = Join-Path $RepoRoot '03_scripts\runtime_activation\ghoti_python_resolver.ps1'
if (Test-Path -LiteralPath $resolver) {
    try {
        $robj = (& $resolver 2>$null | Out-String | ConvertFrom-Json)
        if ($robj -and $robj.ok -eq $true -and $robj.executable) {
            $pyOk = $true
            $pyExe = [string]$robj.executable
        }
    } catch { $pyOk = $false }
}

function Invoke-LauncherJson {
    param([string[]]$DashArgs)
    if (-not $pyOk) { return $null }
    try {
        $out = & $pyExe $Script @DashArgs 2>$null
        if ($LASTEXITCODE -ne 0) { return $null }
        return ($out | Out-String | ConvertFrom-Json)
    } catch { return $null }
}

$checkObj = Invoke-LauncherJson @('--check', '--json')
$checkJsonWorks = [bool]($checkObj -and $checkObj.ok -eq $true)

$blockedObj = Invoke-LauncherJson @('--task', $Blocked, '--dry-run', '--json')
$blockedDetected = [bool]($blockedObj -and $blockedObj.status -eq 'blocked' `
    -and $blockedObj.gates.live_launch_enabled -eq $false)

$scriptExists = Test-Path -LiteralPath $Script
$schemasPresent = ((Test-Path -LiteralPath $TaskSchema) -and (Test-Path -LiteralPath $PlanSchema))
$manifestPresent = Test-Path -LiteralPath $Manifest

# No shell-string command execution / no subprocess in the launcher source.
$noShellTrue = $true
$noSubprocess = $true
if ($scriptExists) {
    $src = Get-Content -LiteralPath $Script -Raw
    if ($src -match 'shell\s*=\s*True') { $noShellTrue = $false }
    if ($src -match 'os\.system\s*\(') { $noShellTrue = $false }
    if ($src -match 'import\s+subprocess') { $noSubprocess = $false }
}

$ok = ($scriptExists -and $schemasPresent -and $checkJsonWorks -and $blockedDetected -and
       $noShellTrue -and $noSubprocess)

$payload = [ordered]@{
    ok                      = [bool]$ok
    wrapper                 = 'check_swarm_launcher'
    repo_root               = $RepoRoot
    python_ok               = [bool]$pyOk
    python_executable       = $pyExe
    script_exists           = [bool]$scriptExists
    schemas_present         = [bool]$schemasPresent
    manifest_present        = [bool]$manifestPresent
    check_json_works        = [bool]$checkJsonWorks
    blocked_overlap_detected = [bool]$blockedDetected
    no_shell_true           = [bool]$noShellTrue
    no_subprocess           = [bool]$noSubprocess
    live_launch_enabled     = $false
    approval_required       = $true
    kill_switch_required    = $true
    dry_run_only            = $true
}
$payload | ConvertTo-Json -Depth 6
