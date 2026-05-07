# screenpipe_retention_cleanup.ps1
# Dry-run by default. Pass -Execute to actually delete files.
# Refuses to run on repo root, C:\Users, C:\, or system folders.
#
# Usage:
#   powershell -ExecutionPolicy Bypass -File 03_scripts\screenpipe_retention_cleanup.ps1
#   powershell -ExecutionPolicy Bypass -File 03_scripts\screenpipe_retention_cleanup.ps1 -Execute

param(
    [int]    $RetentionDays = 3,
    [string] $Root          = "C:\Users\ai_sandbox\Documents\AI_Managed_Only\output\screenpipe",
    [switch] $Execute
)

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

# Paths that must never be touched
$BLOCKED_ROOTS = @(
    "C:\",
    "C:\Users",
    "C:\Windows",
    "C:\Program Files",
    "C:\Program Files (x86)",
    "C:\Users\ai_sandbox\Documents\AI_Managed_Only\14_context",
    "C:\Users\ai_sandbox\Documents\AI_Managed_Only\01_projects",
    "C:\Users\ai_sandbox\Documents\AI_Managed_Only\02_automation",
    "C:\Users\ai_sandbox\Documents\AI_Managed_Only\03_scripts",
    "C:\Users\ai_sandbox\Documents\AI_Managed_Only\20_agents",
    "C:\Users\ai_sandbox\Documents\AI_Managed_Only\21_repos",
    "C:\Users\ai_sandbox\Documents\AI_Managed_Only\23_configs"
)

$ALLOWED_ROOTS = @(
    "C:\Users\ai_sandbox\Documents\AI_Managed_Only\output\screenpipe",
    "C:\Users\ai_sandbox\Documents\AI_Managed_Only\05_logs\screenpipe"
)

function Resolve-NormalizedPath([string] $p) {
    return $p.TrimEnd('\').TrimEnd('/').ToLowerInvariant()
}

# Safety check: Root must be under an allowed path
$normalizedRoot = Resolve-NormalizedPath $Root
$isAllowed = $false
foreach ($allowed in $ALLOWED_ROOTS) {
    $normalizedAllowed = Resolve-NormalizedPath $allowed
    if ($normalizedRoot -eq $normalizedAllowed -or $normalizedRoot.StartsWith($normalizedAllowed + "\")) {
        $isAllowed = $true
        break
    }
}
if (-not $isAllowed) {
    # Path not in allowed list — also check it is not a dangerous broad path before reporting
    foreach ($blocked in $BLOCKED_ROOTS) {
        $normalizedBlocked = Resolve-NormalizedPath $blocked
        if ($normalizedRoot -eq $normalizedBlocked -or $normalizedRoot.StartsWith($normalizedBlocked + "\")) {
            Write-Error "[screenpipe_cleanup] ERROR: Root '$Root' is not in the allowed roots list and overlaps blocked path '$blocked'. Aborting."
            exit 1
        }
    }
    Write-Error "[screenpipe_cleanup] ERROR: Root '$Root' is not in the allowed roots list. Aborting."
    exit 1
}

Write-Host "[screenpipe_cleanup] Root         : $Root"
Write-Host "[screenpipe_cleanup] RetentionDays: $RetentionDays"
Write-Host "[screenpipe_cleanup] Execute       : $Execute"
Write-Host "[screenpipe_cleanup] Mode          : $(if ($Execute) { 'LIVE DELETE' } else { 'DRY RUN (no files deleted)' })"
Write-Host ""

if (-not (Test-Path $Root)) {
    Write-Host "[screenpipe_cleanup] Root path does not exist. Nothing to do."
    exit 0
}

$cutoff    = (Get-Date).AddDays(-$RetentionDays)
$candidates = Get-ChildItem -Path $Root -Recurse -File -ErrorAction SilentlyContinue |
              Where-Object { $_.LastWriteTime -lt $cutoff }

if ($candidates.Count -eq 0) {
    Write-Host "[screenpipe_cleanup] No files older than $RetentionDays days found under $Root."
    exit 0
}

Write-Host "[screenpipe_cleanup] Files older than $RetentionDays days: $($candidates.Count)"
foreach ($f in $candidates) {
    Write-Host "  $($f.FullName)  [$($f.LastWriteTime.ToString('yyyy-MM-dd HH:mm:ss'))]"
}
Write-Host ""

if ($Execute) {
    $deleted = 0
    foreach ($f in $candidates) {
        try {
            Remove-Item -Path $f.FullName -Force
            Write-Host "[screenpipe_cleanup] DELETED: $($f.FullName)"
            $deleted++
        } catch {
            Write-Warning "[screenpipe_cleanup] Failed to delete $($f.FullName): $_"
        }
    }
    Write-Host ""
    Write-Host "[screenpipe_cleanup] Deleted $deleted of $($candidates.Count) files."
} else {
    Write-Host "[screenpipe_cleanup] DRY RUN complete. Pass -Execute to delete these $($candidates.Count) file(s)."
}
