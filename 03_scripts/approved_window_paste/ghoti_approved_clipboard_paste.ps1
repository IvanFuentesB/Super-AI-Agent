<#
.SYNOPSIS
  Approved-window clipboard/paste harness (N+6.20A). Defaults to a dry run.

.DESCRIPTION
  Modes:
    (default / -DryRun)  Validate only. Copies nothing, pastes nothing.
    -CopyOnly            Copy the outbox packet text to the clipboard. Nothing else.
    -PasteApproved       Validate the -TargetWindow against the approved allowlist.
                         On a match it reports "approved" but DEFERS - it performs no
                         live keystroke paste in this milestone. On no match it
                         refuses.

  The input file must live under 14_context/overnight_operator/outbox/. The harness
  rejects secret-shaped patterns in the input and never reads secret values. It never
  presses Enter, never submits, never clicks coordinates, and never controls chat,
  browser, or agent windows. There is no Invoke-Expression and no shell string.
#>
[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)][string]$InputFile,
    [switch]$DryRun,
    [switch]$CopyOnly,
    [switch]$PasteApproved,
    [string]$TargetWindow,
    [string]$ApprovedWindowsFile
)

$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$OutboxRoot = Join-Path $RepoRoot '14_context\overnight_operator\outbox'

# -DryRun always wins; otherwise CopyOnly, then PasteApproved; default is dry-run.
$mode = 'dry_run'
if ($DryRun) { $mode = 'dry_run' }
elseif ($CopyOnly) { $mode = 'copy_only' }
elseif ($PasteApproved) { $mode = 'paste_approved' }

# Resolve and contain the input file: it must be under the overnight_operator outbox.
$inputResolved = $null
$inputExists = $false
if (Test-Path -LiteralPath $InputFile) {
    $inputResolved = (Resolve-Path -LiteralPath $InputFile).Path
    $inputExists = $true
} elseif (Test-Path -LiteralPath (Join-Path $RepoRoot $InputFile)) {
    $inputResolved = (Resolve-Path -LiteralPath (Join-Path $RepoRoot $InputFile)).Path
    $inputExists = $true
}

$underOutbox = $false
if ($inputResolved -and (Test-Path -LiteralPath $OutboxRoot)) {
    $outboxResolved = (Resolve-Path -LiteralPath $OutboxRoot).Path
    $underOutbox = $inputResolved.ToLower().StartsWith($outboxResolved.ToLower())
}

$chars = 0
$secretDetected = $false
$text = $null
if ($inputExists -and $underOutbox) {
    try { $text = Get-Content -LiteralPath $inputResolved -Raw } catch { $text = $null }
    if ($text) {
        $chars = $text.Length
        if ($text -match '\b\d{8,10}:[A-Za-z0-9_-]{35}\b' -or
            $text -match '\bsk-[A-Za-z0-9_-]{20,}' -or
            $text -match 'BEGIN (?:RSA |OPENSSH |EC |DSA )?PRIVATE KEY') {
            $secretDetected = $true
        }
    }
}

$copied = $false
$approvedMatch = $null
$status = 'ok'
$reason = $null

if (-not $inputExists) {
    $status = 'input_not_found'; $reason = 'input file not found'
} elseif (-not $underOutbox) {
    $status = 'rejected'; $reason = 'input file must be under 14_context/overnight_operator/outbox'
} elseif ($secretDetected) {
    $status = 'rejected'; $reason = 'secret-shaped pattern detected in input; refusing to copy or paste'
} elseif ($mode -eq 'copy_only') {
    Set-Clipboard -Value $text
    $copied = $true
} elseif ($mode -eq 'paste_approved') {
    if (-not $ApprovedWindowsFile) {
        $ApprovedWindowsFile = Join-Path $RepoRoot '14_context\approved_window_paste\approved_windows.example.json'
    }
    $allow = $null
    if (Test-Path -LiteralPath $ApprovedWindowsFile) {
        try { $allow = Get-Content -LiteralPath $ApprovedWindowsFile -Raw | ConvertFrom-Json } catch { $allow = $null }
    }
    if ($allow -and $allow.approved_windows -and $TargetWindow) {
        foreach ($entry in $allow.approved_windows) {
            if (([string]$entry.name -ieq $TargetWindow) -or ([string]$entry.process_name -ieq $TargetWindow)) {
                $approvedMatch = [string]$entry.name; break
            }
        }
    }
    if (-not $approvedMatch) {
        $status = 'rejected'
        $reason = 'target window not in approved allowlist (or no -TargetWindow given); refusing to paste'
    } else {
        $status = 'approved_paste_deferred'
        $reason = 'approved window matched; live keystroke paste is deferred behind approved_window_paste_enabled. Paste manually with Ctrl+V. No Enter, no submit.'
    }
}

$ok = (($status -eq 'ok') -or ($status -eq 'approved_paste_deferred')) -and (-not $secretDetected)

$payload = [ordered]@{
    ok                 = [bool]$ok
    milestone          = 'N+6.20A'
    tool               = 'ghoti_approved_clipboard_paste'
    mode               = $mode
    dry_run            = ($mode -eq 'dry_run')
    input_file         = $InputFile
    input_exists       = [bool]$inputExists
    input_under_outbox = [bool]$underOutbox
    secret_detected    = [bool]$secretDetected
    characters         = [int]$chars
    copied             = [bool]$copied
    pasted             = $false
    submitted          = $false
    target_window      = $TargetWindow
    approved_match     = $approvedMatch
    status             = $status
    reason             = $reason
    safety             = [ordered]@{
        local_only                    = $true
        paste_into_apps               = $false
        presses_enter                 = $false
        submits                       = $false
        clicks_coordinates            = $false
        controls_chat_or_browser_apps = $false
        reads_secret_values           = $false
        input_must_be_under_outbox    = $true
    }
}
$payload | ConvertTo-Json -Depth 6
