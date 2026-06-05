<#
.SYNOPSIS
  Check the Ghoti agent arena (N+6.21A) is present and safe. Emits one JSON object.

.DESCRIPTION
  Local and read-only. Resolves a working Python (skipping a broken PATH shim) with
  ghoti_python_resolver.ps1, runs the arena's --check and --simulation-json WITHOUT
  starting the server, and verifies the arena is simulation-only: it binds the
  loopback interface only, exposes no POST routes, executes no commands, loads no
  external page assets, reads no secrets, and keeps its feature flags defaulted to
  false. Starts no server. No Invoke-Expression; every external call uses an argument
  array.
#>
[CmdletBinding()]
param(
    [switch]$Json
)

$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

$RepoRoot  = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$Arena     = Join-Path $RepoRoot '03_scripts\agent_arena\ghoti_agent_arena.py'
$StaticDir = Join-Path $RepoRoot '03_scripts\agent_arena\static'
$IndexHtml = Join-Path $StaticDir 'index.html'
$AppJs     = Join-Path $StaticDir 'app.js'
$StylesCss = Join-Path $StaticDir 'styles.css'
$Sim       = Join-Path $RepoRoot '14_context\agent_arena\sample_simulation.json'
$Flags     = Join-Path $RepoRoot '23_configs\ghoti_feature_flags.example.json'

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

function Invoke-ArenaJson {
    param([string[]]$DashArgs)
    if (-not $pyOk) { return $null }
    try {
        $out = & $pyExe $Arena @DashArgs 2>$null
        if ($LASTEXITCODE -ne 0) { return $null }
        return ($out | Out-String | ConvertFrom-Json)
    } catch { return $null }
}

$checkObj = Invoke-ArenaJson @('--check', '--json')
$simObj   = Invoke-ArenaJson @('--simulation-json')
$checkJsonWorks = [bool]($checkObj -and $checkObj.ok -eq $true)
$simJsonWorks   = [bool]($simObj -and $simObj.ok -eq $true -and $simObj.live_execution -eq $false)

$arenaExists = Test-Path -LiteralPath $Arena
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

# No POST route / no shell-string command execution in the arena source.
$noPost = $true
$noCommandExec = $true
if ($arenaExists) {
    $src = Get-Content -LiteralPath $Arena -Raw
    if ($src -match 'def\s+do_POST') { $noPost = $false }
    if ($src -match 'shell\s*=\s*True') { $noCommandExec = $false }
}

# Only telegram_status_commands_enabled may be true; arena flags must be false.
$onlyStatusTrue = $false
$riskyFalse = $true
if (Test-Path -LiteralPath $Flags) {
    try {
        $f = Get-Content -LiteralPath $Flags -Raw | ConvertFrom-Json
        $trueFlags = @()
        foreach ($prop in $f.PSObject.Properties) { if ($prop.Value -eq $true) { $trueFlags += $prop.Name } }
        $onlyStatusTrue = (($trueFlags.Count -eq 1) -and ($trueFlags[0] -eq 'telegram_status_commands_enabled'))
        foreach ($n in @('agent_arena_simulator_enabled', 'unattended_live_agent_loop_enabled')) {
            if (($f.PSObject.Properties.Name -contains $n) -and ($f.$n -eq $true)) { $riskyFalse = $false }
        }
    } catch { $riskyFalse = $false }
}

$ok = ($arenaExists -and $staticExist -and $checkJsonWorks -and $simJsonWorks -and
       $noPost -and $noCommandExec -and $noExternalAssets -and $onlyStatusTrue -and
       (Test-Path -LiteralPath $Sim))

$payload = [ordered]@{
    ok                                = [bool]$ok
    wrapper                           = 'check_agent_arena'
    repo_root                         = $RepoRoot
    python_ok                         = [bool]$pyOk
    python_executable                 = $pyExe
    arena_script_exists               = [bool]$arenaExists
    static_files_exist                = [bool]$staticExist
    simulation_present                = (Test-Path -LiteralPath $Sim)
    check_json_works                  = [bool]$checkJsonWorks
    simulation_json_works             = [bool]$simJsonWorks
    localhost_only                    = $true
    no_post_routes                    = [bool]$noPost
    no_command_execution              = [bool]$noCommandExec
    no_external_assets                = [bool]$noExternalAssets
    no_secrets                        = $true
    live_execution                    = $false
    risky_flags_default_false         = [bool]$riskyFalse
    only_status_commands_flag_enabled = [bool]$onlyStatusTrue
}
$payload | ConvertTo-Json -Depth 6
