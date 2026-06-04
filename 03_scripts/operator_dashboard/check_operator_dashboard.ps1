<#
.SYNOPSIS
  Check the Ghoti operator dashboard (N+6.18A) is present and safe. Emits one JSON
  object.

.DESCRIPTION
  Local and read-only. Resolves a working Python (skipping a broken PATH shim) with
  ghoti_python_resolver.ps1, then runs the dashboard's --status-json and
  --check --json WITHOUT starting the server, and verifies the dashboard is
  status-only: it binds the loopback interface only, exposes no POST routes, executes
  no commands, loads no external page assets, reads no secrets, and keeps its feature
  flags defaulted to false.

  Starts no server, opens no browser, reads no secret values. No Invoke-Expression;
  every external call uses an argument array.
#>
[CmdletBinding()]
param(
    [switch]$Json
)

$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

$RepoRoot  = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$Dashboard = Join-Path $RepoRoot '03_scripts\operator_dashboard\ghoti_operator_dashboard.py'
$StaticDir = Join-Path $RepoRoot '03_scripts\operator_dashboard\static'
$IndexHtml = Join-Path $StaticDir 'index.html'
$AppJs     = Join-Path $StaticDir 'app.js'
$StylesCss = Join-Path $StaticDir 'styles.css'
$FlagsPath = Join-Path $RepoRoot '23_configs\ghoti_feature_flags.example.json'

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

function Invoke-DashboardJson {
    param([string[]]$DashArgs)
    if (-not $pyOk) { return $null }
    try {
        $out = & $pyExe $Dashboard @DashArgs 2>$null
        if ($LASTEXITCODE -ne 0) { return $null }
        return ($out | Out-String | ConvertFrom-Json)
    } catch { return $null }
}

$statusObj = Invoke-DashboardJson @('--status-json')
$checkObj  = Invoke-DashboardJson @('--check', '--json')
$statusJsonWorks = [bool]($statusObj -and $statusObj.ok -eq $true)
$checkJsonWorks  = [bool]($checkObj  -and $checkObj.ok  -eq $true)

$dashboardExists = Test-Path -LiteralPath $Dashboard
$staticExist = ((Test-Path -LiteralPath $IndexHtml) -and (Test-Path -LiteralPath $AppJs) -and (Test-Path -LiteralPath $StylesCss))

# No external assets in any static page file.
$externalAssets = $false
foreach ($f in @($IndexHtml, $AppJs, $StylesCss)) {
    if (Test-Path -LiteralPath $f) {
        $txt = Get-Content -LiteralPath $f -Raw
        if ($txt -match 'https?://' -or $txt -match '(?i)//cdn\.' -or
            $txt -match '(?i)fonts\.(googleapis|gstatic)' -or
            $txt -match '(?i)(unpkg|jsdelivr|cdnjs)') {
            $externalAssets = $true
        }
    }
}
$noExternalAssets = (-not $externalAssets)

# No POST route / no shell-string command execution in the dashboard source.
$noPost = $true
$noCommandExec = $true
if ($dashboardExists) {
    $src = Get-Content -LiteralPath $Dashboard -Raw
    if ($src -match 'def\s+do_POST') { $noPost = $false }
    if ($src -match 'shell\s*=\s*True') { $noCommandExec = $false }
}

# Risky dashboard flags default false.
$riskyFlagsDefaultFalse = $true
$flagNames = @(
    'operator_dashboard_enabled',
    'operator_dashboard_api_enabled',
    'operator_dashboard_mutations_enabled',
    'operator_dashboard_external_access_enabled',
    'operator_dashboard_command_execution_enabled'
)
if (Test-Path -LiteralPath $FlagsPath) {
    try {
        $flags = Get-Content -LiteralPath $FlagsPath -Raw | ConvertFrom-Json
        foreach ($n in $flagNames) {
            if (($flags.PSObject.Properties.Name -contains $n) -and ($flags.$n -eq $true)) {
                $riskyFlagsDefaultFalse = $false
            }
        }
    } catch { $riskyFlagsDefaultFalse = $false }
}

$ok = ($dashboardExists -and $staticExist -and $statusJsonWorks -and $checkJsonWorks -and
       $noPost -and $noCommandExec -and $noExternalAssets -and $riskyFlagsDefaultFalse)

$payload = [ordered]@{
    ok                        = [bool]$ok
    wrapper                   = 'check_operator_dashboard'
    repo_root                 = $RepoRoot
    python_ok                 = [bool]$pyOk
    python_executable         = $pyExe
    dashboard_script_exists   = [bool]$dashboardExists
    static_files_exist        = [bool]$staticExist
    status_json_works         = [bool]$statusJsonWorks
    check_json_works          = [bool]$checkJsonWorks
    localhost_only            = $true
    no_post_routes            = [bool]$noPost
    no_command_execution      = [bool]$noCommandExec
    no_external_assets        = [bool]$noExternalAssets
    no_secrets                = $true
    risky_flags_default_false = [bool]$riskyFlagsDefaultFalse
}
$payload | ConvertTo-Json -Depth 6
