<#
.SYNOPSIS
  Write the Hermes-readable status handoff note via the local status bridge.

.DESCRIPTION
  Resolves a working Python (skipping a broken PATH shim) with
  ghoti_python_resolver.ps1, then calls the local read-only status bridge with
  --write-hermes-handoff so WSL Hermes can read one status source instead of
  repeating a generic summary. Emits a single JSON object.

  Local and read-only except for the single Markdown note the bridge writes inside
  the repo. No secrets, no network, no external API, no agent launch, no Telegram
  control, no MCP, no live browser/computer-use, no OS input. No Invoke-Expression;
  the bridge is called with an argument array.

  Pass -DryRun to print what would run and write nothing.
#>
[CmdletBinding()]
param(
    [switch]$DryRun,
    [switch]$UseGemmaIfAvailable
)

$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$bridge = Join-Path $RepoRoot '03_scripts\status_bridge\ghoti_status_bridge.py'

# Resolve Python via the resolver script (in-process; its exit code does not stop us).
$pyOk = $false
$pyExe = $null
$resolver = Join-Path $PSScriptRoot 'ghoti_python_resolver.ps1'
if (Test-Path -LiteralPath $resolver) {
    try {
        $rout = & $resolver 2>$null
        $robj = ($rout | Out-String | ConvertFrom-Json)
        if ($robj -and $robj.ok -eq $true -and $robj.executable) {
            $pyOk = $true
            $pyExe = [string]$robj.executable
        }
    } catch { $pyOk = $false }
}

$bridgePresent = Test-Path -LiteralPath $bridge
$ready = ($pyOk -and $bridgePresent)
$handoffRel = '14_context/agent_handoff_vault/04_Logs/HERMES_STATUS_BRIDGE_LAST_RUN.md'

$gemmaArg = if ($UseGemmaIfAvailable) { ' --use-gemma-if-available' } else { '' }
$wouldRun = if ($pyExe) {
    ('"{0}" "{1}" --json --write-hermes-handoff{2}' -f $pyExe, $bridge, $gemmaArg)
} else {
    '(no python resolved)'
}

if ($DryRun -or -not $ready) {
    $status = [ordered]@{
        ok                    = [bool]$ready
        wrapper               = 'write_hermes_status_handoff'
        dry_run               = [bool]$DryRun
        ready                 = [bool]$ready
        python_ok             = [bool]$pyOk
        python_executable     = $pyExe
        status_bridge_present = [bool]$bridgePresent
        would_run_command     = $wouldRun
        handoff_path          = $handoffRel
        handoff_written       = $false
        secrets_present       = $false
        local_only            = $true
    }
    $status | ConvertTo-Json -Depth 6
    if (-not $ready) { exit 1 }
    exit 0
}

# Real run: call the bridge read-only; it writes the handoff note inside the repo.
$bridgeArgs = @($bridge, '--json', '--write-hermes-handoff')
if ($UseGemmaIfAvailable) { $bridgeArgs += '--use-gemma-if-available' }

$written = $false
$writtenPath = $null
$bridgeOk = $false
try {
    $out = & $pyExe @bridgeArgs 2>$null
    if ($LASTEXITCODE -eq 0) {
        $obj = ($out | Out-String | ConvertFrom-Json)
        if ($obj) {
            $bridgeOk = [bool]$obj.ok
            $written = [bool]$obj.hermes_handoff_written
            if ($obj.hermes_handoff_path) { $writtenPath = [string]$obj.hermes_handoff_path }
        }
    }
} catch { $bridgeOk = $false }

$status = [ordered]@{
    ok                    = ($bridgeOk -and $written)
    wrapper               = 'write_hermes_status_handoff'
    dry_run               = $false
    ready                 = $true
    python_ok             = $true
    python_executable     = $pyExe
    status_bridge_present = $true
    bridge_ok             = [bool]$bridgeOk
    handoff_path          = $(if ($writtenPath) { $writtenPath } else { $handoffRel })
    handoff_written       = [bool]$written
    secrets_present       = $false
    local_only            = $true
}
$status | ConvertTo-Json -Depth 6
if (-not ($bridgeOk -and $written)) { exit 1 }
exit 0
