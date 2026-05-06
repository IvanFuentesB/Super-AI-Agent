# open_obsidian_vault.ps1 — Open the Ghoti Obsidian vault in Obsidian (if installed).
# Read-only helper. Does not modify vault contents.
# Safety: no network calls, no writes, no account actions.

param(
    [switch]$Check,
    [switch]$Open
)

$RepoRoot = Split-Path -Parent $PSScriptRoot
$VaultPath = Join-Path $RepoRoot "14_context\obsidian_vault"

if (-not (Test-Path $VaultPath)) {
    Write-Host "ERROR: Vault not found at $VaultPath"
    exit 1
}

$files = Get-ChildItem $VaultPath -Filter "*.md" | Measure-Object
Write-Host "Vault: $VaultPath"
Write-Host "Files: $($files.Count) markdown files"

if ($Check) {
    $required = @("00_Index.md", "01_Current_State.md", "02_Next_Actions.md", "09_Migration_Handoff.md")
    foreach ($f in $required) {
        $fp = Join-Path $VaultPath $f
        if (Test-Path $fp) {
            Write-Host "  OK: $f"
        } else {
            Write-Host "  MISSING: $f"
        }
    }
    exit 0
}

if ($Open) {
    $obsidianUri = "obsidian://open?path=" + [uri]::EscapeDataString($VaultPath)
    Write-Host "Opening: $obsidianUri"
    Start-Process $obsidianUri
    exit 0
}

Write-Host ""
Write-Host "Usage:"
Write-Host "  .\open_obsidian_vault.ps1 -Check   # Verify required files exist"
Write-Host "  .\open_obsidian_vault.ps1 -Open    # Open vault in Obsidian app"
