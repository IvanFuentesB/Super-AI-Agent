<#
.SYNOPSIS
  Resolve a working Python interpreter for the Ghoti runtime, skipping a broken
  PATH "python" shim.

.DESCRIPTION
  Tries, in order: python, python3, py -3, uv-managed CPython installs, and a repo
  virtualenv if present. Each candidate is validated by running a tiny probe that
  prints sys.executable as JSON; a candidate that does not return valid JSON (for
  example a broken launcher shim) is skipped.

  Emits a single JSON object: ok, executable, source, tried, error.

  Local and read-only: no installs, no downloads, no network, no Invoke-Expression,
  and no shell string is ever executed (every call uses an argument array).
#>
[CmdletBinding()]
param(
    [switch]$Json
)

$ErrorActionPreference = 'Stop'

$probeCode = "import sys, json; print(json.dumps({'ok': True, 'executable': sys.executable}))"
$tried = New-Object System.Collections.Generic.List[string]
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path

function Test-Candidate {
    param(
        [Parameter(Mandatory = $true)][string]$Exe,
        [string[]]$PreArgs = @()
    )
    if (-not $Exe) { return $null }
    try {
        $argv = @()
        if ($PreArgs.Count -gt 0) { $argv += $PreArgs }
        $argv += @('-c', $probeCode)
        $out = & $Exe @argv 2>$null
        if ($LASTEXITCODE -ne 0) { return $null }
        $text = ($out | Out-String).Trim()
        if (-not $text) { return $null }
        $obj = $text | ConvertFrom-Json
        if ($obj -and $obj.ok -eq $true -and $obj.executable) {
            return [string]$obj.executable
        }
        return $null
    } catch {
        return $null
    }
}

$result = $null
$source = $null

# 1) Interpreters on PATH.
$pathCandidates = @(
    @{ name = 'python';  exe = 'python';  pre = @() },
    @{ name = 'python3'; exe = 'python3'; pre = @() },
    @{ name = 'py -3';   exe = 'py';      pre = @('-3') }
)
foreach ($c in $pathCandidates) {
    $tried.Add([string]$c.name)
    $r = Test-Candidate -Exe ([string]$c.exe) -PreArgs ([string[]]$c.pre)
    if ($r) { $result = $r; $source = [string]$c.name; break }
}

# 2) uv-managed CPython installs, then 3) repo virtualenvs.
if (-not $result) {
    $uvBases = @(
        (Join-Path $env:USERPROFILE '.local\share\uv\python'),
        (Join-Path $env:APPDATA 'uv\python'),
        (Join-Path $env:LOCALAPPDATA 'uv\python')
    )
    $candidatePaths = New-Object System.Collections.Generic.List[string]
    foreach ($base in $uvBases) {
        if ($base -and (Test-Path -LiteralPath $base)) {
            try {
                $dirs = Get-ChildItem -LiteralPath $base -Directory -ErrorAction SilentlyContinue | Sort-Object Name -Descending
                foreach ($d in $dirs) {
                    $p = Join-Path $d.FullName 'python.exe'
                    if (Test-Path -LiteralPath $p) { $candidatePaths.Add([string]$p) }
                }
            } catch { }
        }
    }
    foreach ($vp in @(
        (Join-Path $RepoRoot '.venv\Scripts\python.exe'),
        (Join-Path $RepoRoot '01_projects\runtime_mvp\.venv\Scripts\python.exe')
    )) {
        if (Test-Path -LiteralPath $vp) { $candidatePaths.Add([string]$vp) }
    }

    foreach ($p in $candidatePaths) {
        $tried.Add([string]$p)
        $r = Test-Candidate -Exe ([string]$p)
        if ($r) {
            $result = $r
            if ($p -like '*\uv\python\*') { $source = "uv:$p" } else { $source = "venv:$p" }
            break
        }
    }
}

$ok = [bool]$result
$errMsg = $null
if (-not $ok) { $errMsg = 'No working Python interpreter found (broken PATH shim skipped).' }

$payload = [ordered]@{
    ok         = $ok
    executable = $result
    source     = $source
    tried      = @($tried)
    error      = $errMsg
}

$payload | ConvertTo-Json -Depth 5
if (-not $ok) { exit 1 }
exit 0
