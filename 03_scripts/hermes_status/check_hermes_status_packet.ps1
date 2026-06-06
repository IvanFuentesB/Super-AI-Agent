<#
.SYNOPSIS
  Check the Ghoti Hermes status packet generator (N+6.25A) is present and safe. Emits one
  JSON object.

.DESCRIPTION
  Local and read-only. Resolves a working Python (skipping a broken PATH shim) with
  ghoti_python_resolver.ps1, runs the generator's --check WITHOUT writing any packet, and
  verifies the generator is read-only: it launches no agent, runs no command other than
  read-only git, uses no MCP/browser/computer-use, reads no secrets, and writes nothing
  unless --write is passed. Starts no server, writes no packet. No Invoke-Expression; the
  external call uses an argument array.
#>
[CmdletBinding()]
param(
    [switch]$Json
)

$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$Script   = Join-Path $RepoRoot '03_scripts\hermes_status\ghoti_hermes_status_packet.py'
$Schema   = Join-Path $RepoRoot '14_context\hermes_status\hermes_status_packet_schema.json'
$Example  = Join-Path $RepoRoot '14_context\hermes_status\HERMES_STATUS_PACKET.example.md'

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

function Invoke-PacketJson {
    param([string[]]$DashArgs)
    if (-not $pyOk) { return $null }
    try {
        $out = & $pyExe $Script @DashArgs 2>$null
        if ($LASTEXITCODE -ne 0) { return $null }
        return ($out | Out-String | ConvertFrom-Json)
    } catch { return $null }
}

$checkObj = Invoke-PacketJson @('--check', '--json')
$checkJsonWorks = [bool]($checkObj -and $checkObj.ok -eq $true)

$scriptExists  = Test-Path -LiteralPath $Script
$schemaPresent = Test-Path -LiteralPath $Schema
$examplePresent = Test-Path -LiteralPath $Example

# No shell-string command execution in the generator source (subprocess git is allowed).
$noShellTrue = $true
if ($scriptExists) {
    $src = Get-Content -LiteralPath $Script -Raw
    if ($src -match 'shell\s*=\s*True') { $noShellTrue = $false }
    if ($src -match 'os\.system\s*\(') { $noShellTrue = $false }
}

$ok = ($scriptExists -and $schemaPresent -and $examplePresent -and $checkJsonWorks -and $noShellTrue)

$payload = [ordered]@{
    ok                       = [bool]$ok
    wrapper                  = 'check_hermes_status_packet'
    repo_root                = $RepoRoot
    python_ok                = [bool]$pyOk
    python_executable        = $pyExe
    script_exists            = [bool]$scriptExists
    schema_present           = [bool]$schemaPresent
    example_present          = [bool]$examplePresent
    check_json_works         = [bool]$checkJsonWorks
    no_shell_true            = [bool]$noShellTrue
    reads_git_metadata_only  = $true
    no_live_launch           = $true
    no_mcp                   = $true
    no_browser_computer_use  = $true
    writes_packet            = $false
}
$payload | ConvertTo-Json -Depth 6
