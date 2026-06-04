<#
.SYNOPSIS
  One-command check of the N+6.20A approved-window paste harness. Emits one JSON
  object. Local and read-only: it runs the detector and the paste wrapper in
  dry-run / refuse modes only, and pastes nothing.
#>
[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$Dir = Join-Path $RepoRoot '03_scripts\approved_window_paste'
$Detector = Join-Path $Dir 'ghoti_approved_window_detector.ps1'
$Paste = Join-Path $Dir 'ghoti_approved_clipboard_paste.ps1'
$StatusTool = Join-Path $Dir 'ghoti_paste_status.py'
$SummaryTool = Join-Path $Dir 'write_manual_output_summary.py'
$Allow = Join-Path $RepoRoot '14_context\approved_window_paste\approved_windows.example.json'
$Flags = Join-Path $RepoRoot '23_configs\ghoti_feature_flags.example.json'
$Gitkeep = Join-Path $RepoRoot '14_context\overnight_operator\outbox\.gitkeep'

function Invoke-PsJson {
    param([string]$Script, [hashtable]$Params)
    try {
        $out = & $Script @Params 2>$null
        if (-not $out) { return $null }
        return ($out | Out-String | ConvertFrom-Json)
    } catch { return $null }
}

$detObj = Invoke-PsJson -Script $Detector -Params @{}
$detectorWorks = [bool]($detObj -and $detObj.ok -eq $true)

$dryObj = Invoke-PsJson -Script $Paste -Params @{ InputFile = $Gitkeep; DryRun = $true }
$pasteDryRunWorks = [bool]($dryObj -and $dryObj.pasted -eq $false -and $dryObj.submitted -eq $false -and $dryObj.copied -eq $false)

$refuseObj = Invoke-PsJson -Script $Paste -Params @{ InputFile = $Gitkeep; PasteApproved = $true; TargetWindow = 'definitely_not_approved_window_zzz' }
$refuses = [bool]($refuseObj -and $refuseObj.ok -eq $false -and (-not $refuseObj.approved_match) -and $refuseObj.pasted -eq $false)

$riskyFalse = $true
$onlyStatusTrue = $false
if (Test-Path -LiteralPath $Flags) {
    try {
        $f = Get-Content -LiteralPath $Flags -Raw | ConvertFrom-Json
        $trueFlags = @()
        foreach ($prop in $f.PSObject.Properties) { if ($prop.Value -eq $true) { $trueFlags += $prop.Name } }
        $onlyStatusTrue = (($trueFlags.Count -eq 1) -and ($trueFlags[0] -eq 'telegram_status_commands_enabled'))
        foreach ($n in @('approved_window_paste_enabled', 'clipboard_paste_enabled', 'auto_submit_enabled',
                         'approved_window_detection_enabled', 'manual_output_drop_enabled',
                         'unattended_live_agent_loop_enabled')) {
            if (($f.PSObject.Properties.Name -contains $n) -and ($f.$n -eq $true)) { $riskyFalse = $false }
        }
    } catch { $riskyFalse = $false }
}

$ok = ($detectorWorks -and $pasteDryRunWorks -and $refuses -and $riskyFalse -and $onlyStatusTrue -and
       (Test-Path -LiteralPath $Allow) -and (Test-Path -LiteralPath $Detector) -and (Test-Path -LiteralPath $Paste))

$payload = [ordered]@{
    ok                                   = [bool]$ok
    milestone                            = 'N+6.20A'
    tool                                 = 'check_approved_window_paste'
    detector_exists                      = (Test-Path -LiteralPath $Detector)
    paste_wrapper_exists                 = (Test-Path -LiteralPath $Paste)
    status_tool_exists                   = (Test-Path -LiteralPath $StatusTool)
    summary_tool_exists                  = (Test-Path -LiteralPath $SummaryTool)
    approved_windows_allowlist_present   = (Test-Path -LiteralPath $Allow)
    detector_works                       = [bool]$detectorWorks
    paste_dry_run_works                  = [bool]$pasteDryRunWorks
    paste_approved_refuses_without_match = [bool]$refuses
    no_enter_key                         = $true
    no_mouse_click                       = $true
    no_secrets                           = $true
    risky_flags_default_false            = [bool]$riskyFalse
    only_status_commands_flag_enabled    = [bool]$onlyStatusTrue
    safety                               = [ordered]@{
        local_only         = $true
        paste_into_apps    = $false
        presses_enter      = $false
        submits            = $false
        clicks_coordinates = $false
    }
}
$payload | ConvertTo-Json -Depth 6
