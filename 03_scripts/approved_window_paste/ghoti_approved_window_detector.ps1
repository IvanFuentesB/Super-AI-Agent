<#
.SYNOPSIS
  List visible windows (process name + title + pid) and mark which ones match the
  approved-window allowlist. Read-only: it enumerates windows only and controls
  nothing.

.DESCRIPTION
  Uses Get-Process to read windows that currently have a title. It focuses no window,
  presses no key, clicks nothing, and submits nothing. Output is a single local JSON
  object; nothing is sent anywhere and no secret value is read.
#>
[CmdletBinding()]
param(
    [string]$ApprovedWindowsFile
)

$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
if (-not $ApprovedWindowsFile) {
    $ApprovedWindowsFile = Join-Path $RepoRoot '14_context\approved_window_paste\approved_windows.example.json'
}

$approvedList = @()
if (Test-Path -LiteralPath $ApprovedWindowsFile) {
    try {
        $allow = Get-Content -LiteralPath $ApprovedWindowsFile -Raw | ConvertFrom-Json
        if ($allow -and $allow.approved_windows) { $approvedList = $allow.approved_windows }
    } catch { $approvedList = @() }
}

function Get-ApprovedName {
    param([string]$ProcName, [string]$Title)
    foreach ($entry in $approvedList) {
        $pn = [string]$entry.process_name
        $tc = [string]$entry.title_contains
        if ($pn -and ($ProcName -ieq $pn)) {
            if (-not $tc -or ($Title -and $Title.ToLower().Contains($tc.ToLower()))) {
                return [string]$entry.name
            }
        }
    }
    return $null
}

$windows = @()
foreach ($p in (Get-Process | Where-Object { $_.MainWindowHandle -ne 0 -and $_.MainWindowTitle })) {
    $title = [string]$p.MainWindowTitle
    $name = [string]$p.ProcessName
    $windows += [ordered]@{
        process_name   = $name
        title          = $title
        pid            = $p.Id
        approved_match = (Get-ApprovedName -ProcName $name -Title $title)
    }
}

$payload = [ordered]@{
    ok                   = $true
    milestone            = 'N+6.20A'
    tool                 = 'ghoti_approved_window_detector'
    window_count         = @($windows).Count
    approved_match_count = @($windows | Where-Object { $_.approved_match }).Count
    windows              = @($windows)
    safety               = [ordered]@{
        local_only          = $true
        read_only           = $true
        controls_windows    = $false
        focuses_window      = $false
        presses_enter       = $false
        clicks_coordinates  = $false
        reads_secret_values = $false
    }
}
$payload | ConvertTo-Json -Depth 6
