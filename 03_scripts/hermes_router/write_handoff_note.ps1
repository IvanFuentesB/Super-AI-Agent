# write_handoff_note.ps1 — Hermes router wrapper (DRY-RUN by default).
# Prepares (and, only with -AllowWrite, writes) a handoff note under the vault's
# 04_Logs folder. Default is dry-run: it computes the safe target and writes nothing.
# Safety: bounded to 04_Logs only; filename is sanitized so path traversal is
# structurally impossible; an explicit containment check refuses any path outside
# 04_Logs; no network; no launch; never runs arbitrary commands.

param(
    [Parameter(Mandatory = $true)]
    [string]$Title,
    [string]$Body = '',
    [switch]$AllowWrite,
    [switch]$Overwrite
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

$ScriptDir = $PSScriptRoot
$RepoRoot  = Split-Path -Parent (Split-Path -Parent $ScriptDir)
$VaultPath = Join-Path $RepoRoot '14_context\agent_handoff_vault'
$LogsDir   = Join-Path $VaultPath '04_Logs'

try {
    # Sanitize the title into a safe filename: only [a-z0-9_-] survive, so '..',
    # '/', '\' and ':' all collapse to '_' and cannot escape the folder.
    $base = $Title.ToLowerInvariant()
    $safe = ($base -replace '[^a-z0-9_\-]', '_').Trim('_')
    $validName = ($safe -match '[a-z0-9]')
    $safeFile = $safe + '.md'

    $target = Join-Path $LogsDir $safeFile

    # Defense in depth: resolve absolute paths and require the target to live
    # strictly inside 04_Logs.
    $fullLogs   = [System.IO.Path]::GetFullPath($LogsDir)
    $fullTarget = [System.IO.Path]::GetFullPath($target)
    $sep        = [System.IO.Path]::DirectorySeparatorChar
    $fullLogsWithSep = $fullLogs.TrimEnd($sep) + $sep
    $underLogs = $fullTarget.StartsWith($fullLogsWithSep, [System.StringComparison]::OrdinalIgnoreCase)

    $existsBefore = Test-Path -LiteralPath $target -PathType Leaf
    $wrote = $false
    $mode  = 'dry_run'

    if ($AllowWrite.IsPresent) {
        if (-not $validName) { throw 'Title contains no alphanumeric characters after sanitization.' }
        if (-not $underLogs) { throw 'Refusing to write outside 04_Logs (path containment failed).' }
        if ($existsBefore -and -not $Overwrite.IsPresent) { throw 'Target note already exists; pass -Overwrite to replace it.' }
        $content = "# $Title`n`n$Body`n"
        Set-Content -LiteralPath $target -Value $content -Encoding UTF8
        $wrote = $true
        $mode  = 'write'
    }

    $result = [ordered]@{
        ok            = $true
        wrapper       = 'write_handoff_note'
        mode          = $mode
        title         = $Title
        safe_filename = $safeFile
        valid_name    = $validName
        target_path   = $target
        under_logs    = $underLogs
        exists_before = $existsBefore
        allow_write   = $AllowWrite.IsPresent
        wrote         = $wrote
        live_action   = $false
        local_only    = $true
    }
    $result | ConvertTo-Json -Depth 6
    exit 0
}
catch {
    [ordered]@{ ok = $false; wrapper = 'write_handoff_note'; error = $_.Exception.Message; wrote = $false; live_action = $false; local_only = $true } | ConvertTo-Json -Depth 4
    exit 1
}
