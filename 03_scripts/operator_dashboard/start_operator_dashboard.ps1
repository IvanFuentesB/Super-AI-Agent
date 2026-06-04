<#
.SYNOPSIS
  Start the Ghoti operator dashboard (N+6.18A) locally on 127.0.0.1. Status-only.

.DESCRIPTION
  Resolves a working Python (skipping a broken PATH shim) with
  ghoti_python_resolver.ps1, then starts the local-only dashboard server
  (--serve --host 127.0.0.1 --port 8765) attached to THIS window so closing the
  window stops it. The dashboard is status-only and read-only: it binds the loopback
  interface only, exposes no POST routes, executes no commands, and starts or stops
  no processes.

  The bind host is fixed to 127.0.0.1; this wrapper never exposes the dashboard
  externally. It opens the browser only when -OpenBrowser is passed; by default it
  opens nothing. Pass -DryRun to print the would-run command and a JSON status
  without starting the server. No Invoke-Expression; the server is launched with an
  argument array. No secrets are read or required.
#>
[CmdletBinding()]
param(
    [switch]$DryRun,
    [switch]$OpenBrowser,
    [int]$Port = 8765
)

$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

$RepoRoot  = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$BindHost  = '127.0.0.1'
$Dashboard = Join-Path $RepoRoot '03_scripts\operator_dashboard\ghoti_operator_dashboard.py'

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

$dashExists = Test-Path -LiteralPath $Dashboard
$ready = ($pyOk -and $dashExists)
$url = ('http://{0}:{1}/' -f $BindHost, $Port)
$wouldRun = if ($pyExe) {
    ('"{0}" "{1}" --serve --host {2} --port {3}' -f $pyExe, $Dashboard, $BindHost, $Port)
} else {
    ('(no python resolved) "{0}" --serve --host {1} --port {2}' -f $Dashboard, $BindHost, $Port)
}

$status = [ordered]@{
    ok                        = [bool]$ready
    wrapper                   = 'start_operator_dashboard'
    dry_run                   = [bool]$DryRun
    status_only               = $true
    read_only                 = $true
    python_ok                 = [bool]$pyOk
    python_executable         = $pyExe
    dashboard_script_present  = [bool]$dashExists
    bind_host                 = $BindHost
    port                      = $Port
    url                       = $url
    localhost_only            = $true
    open_browser              = [bool]$OpenBrowser
    ready_to_start            = [bool]$ready
    would_run_command         = $wouldRun
    external_access_enabled   = $false
    command_execution_enabled = $false
    mutations_enabled         = $false
    warning                   = 'Keep this window open. If it closes, the dashboard stops.'
}
$status | ConvertTo-Json -Depth 6

if ($DryRun) { exit 0 }

if (-not $ready) {
    Write-Host 'Cannot start: resolve a working Python and ensure the dashboard script is present.'
    exit 1
}

if ($OpenBrowser) {
    try { Start-Process $url | Out-Null } catch {}
}

Write-Host ('Ghoti operator dashboard on {0} (status-only). Keep this window open; Ctrl+C stops it.' -f $url)
& $pyExe $Dashboard --serve --host $BindHost --port $Port
exit $LASTEXITCODE
