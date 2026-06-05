<#
.SYNOPSIS
  Start the Ghoti agent arena (N+6.21A) locally on 127.0.0.1. Simulation-only.

.DESCRIPTION
  Resolves a working Python (skipping a broken PATH shim) with
  ghoti_python_resolver.ps1, then starts the local-only arena server
  (--serve --host 127.0.0.1 --port 8766) attached to THIS window so closing the
  window stops it. The arena is simulation-only and read-only: it binds the loopback
  interface only, exposes no POST routes, launches no agent, and runs no command.

  The bind host is fixed to 127.0.0.1; this wrapper never exposes the arena
  externally. It opens the browser only when -OpenBrowser is passed; by default it
  opens nothing. Pass -DryRun to print the would-run command and a JSON status without
  starting the server. No Invoke-Expression; the server is launched with an argument
  array. No secrets are read or required.
#>
[CmdletBinding()]
param(
    [switch]$DryRun,
    [switch]$OpenBrowser,
    [int]$Port = 8766
)

$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$BindHost = '127.0.0.1'
$Arena    = Join-Path $RepoRoot '03_scripts\agent_arena\ghoti_agent_arena.py'

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

$arenaExists = Test-Path -LiteralPath $Arena
$ready = ($pyOk -and $arenaExists)
$url = ('http://{0}:{1}/' -f $BindHost, $Port)
$wouldRun = if ($pyExe) {
    ('"{0}" "{1}" --serve --host {2} --port {3}' -f $pyExe, $Arena, $BindHost, $Port)
} else {
    ('(no python resolved) "{0}" --serve --host {1} --port {2}' -f $Arena, $BindHost, $Port)
}

$status = [ordered]@{
    ok                        = [bool]$ready
    wrapper                   = 'start_agent_arena'
    dry_run                   = [bool]$DryRun
    simulation_only           = $true
    read_only                 = $true
    live_execution            = $false
    python_ok                 = [bool]$pyOk
    python_executable         = $pyExe
    arena_script_present      = [bool]$arenaExists
    bind_host                 = $BindHost
    port                      = $Port
    url                       = $url
    localhost_only            = $true
    open_browser              = [bool]$OpenBrowser
    ready_to_start            = [bool]$ready
    would_run_command         = $wouldRun
    external_access_enabled   = $false
    command_execution_enabled = $false
    launches_agents           = $false
    warning                   = 'Keep this window open. If it closes, the arena stops.'
}
$status | ConvertTo-Json -Depth 6

if ($DryRun) { exit 0 }

if (-not $ready) {
    Write-Host 'Cannot start: resolve a working Python and ensure the arena script is present.'
    exit 1
}

if ($OpenBrowser) {
    try { Start-Process $url | Out-Null } catch {}
}

Write-Host ('Ghoti agent arena on {0} (simulation-only). Keep this window open; Ctrl+C stops it.' -f $url)
& $pyExe $Arena --serve --host $BindHost --port $Port
exit $LASTEXITCODE
