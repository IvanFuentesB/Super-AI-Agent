# open_obsidian_vault.ps1 — Open the Ghoti Obsidian vault in Obsidian (if installed).
# N+3.56-FIX: unified Obsidian detection — uses obsidian_probe.py if available,
#             else checks same candidate paths as obsidian_probe.py.
# Read-only helper. Does not modify vault contents.
# Safety: no network calls, no writes, no account actions.

param(
    [switch]$Check,
    [switch]$Open
)

$RepoRoot = Split-Path -Parent $PSScriptRoot
$VaultPath = Join-Path $RepoRoot "14_context\obsidian_vault"
$ProbeScript = Join-Path $RepoRoot "03_scripts\obsidian_probe.py"

# Always show vault path and existence
Write-Host "Vault path : $VaultPath"
Write-Host "Vault exists: $(Test-Path $VaultPath)"

if (Test-Path $VaultPath) {
    $files = Get-ChildItem $VaultPath -Filter "*.md" -ErrorAction SilentlyContinue | Measure-Object
    Write-Host "Vault .md files: $($files.Count)"
}

if ($Check) {
    Write-Host ""
    Write-Host "=== Obsidian Check ==="

    # Use obsidian_probe.py if available for unified detection
    if (Test-Path $ProbeScript) {
        Write-Host "Using obsidian_probe.py for unified detection..."
        python $ProbeScript --status
        Write-Host ""
        Write-Host "--- How to Open Vault ---"
        $escapedVault = [uri]::EscapeDataString($VaultPath)
        $obsidianUri = "obsidian://open?path=$escapedVault"
        Write-Host "  Obsidian URI: $obsidianUri"
        Write-Host "  Run with -Open flag to launch:"
        Write-Host "    powershell -ExecutionPolicy Bypass -File '$PSCommandPath' -Open"
        Write-Host ""
        Write-Host "=== End Obsidian Check ==="
        exit 0
    }

    # Inline fallback if probe script not available
    $required = @("00_Index.md", "01_Current_State.md", "02_Next_Actions.md", "09_Migration_Handoff.md")
    foreach ($f in $required) {
        $fp = Join-Path $VaultPath $f
        if (Test-Path $fp) {
            Write-Host "  OK: $f"
        } else {
            Write-Host "  MISSING: $f"
        }
    }

    # Check winget for Obsidian
    Write-Host ""
    Write-Host "--- Obsidian App Check ---"
    try {
        $wingetResult = winget list --id Obsidian.Obsidian 2>&1
        if ($LASTEXITCODE -eq 0 -and $wingetResult -match "Obsidian") {
            Write-Host "  Winget: Obsidian FOUND"
            $wingetResult | Where-Object { $_ -match "Obsidian" } | Select-Object -First 2 | ForEach-Object { Write-Host "  $_" }
        } else {
            Write-Host "  Winget: Obsidian NOT found via winget list"
        }
    } catch {
        Write-Host "  Winget: not available or error: $($_.Exception.Message)"
    }

    # Find likely executable candidates — same list as obsidian_probe.py
    Write-Host ""
    Write-Host "--- Likely Obsidian Executable Candidates ---"
    $candidates = @(
        "C:\Users\Navif\AppData\Local\Programs\Obsidian\Obsidian.exe",
        "C:\Users\ai_sandbox\AppData\Local\Programs\Obsidian\Obsidian.exe",
        "C:\Users\ai_sandbox\AppData\Local\Obsidian\Obsidian.exe",
        "C:\Program Files\Obsidian\Obsidian.exe",
        "$env:LOCALAPPDATA\Programs\Obsidian\Obsidian.exe",
        "$env:LOCALAPPDATA\Obsidian\Obsidian.exe"
    )
    $found = $false
    foreach ($c in $candidates) {
        if (Test-Path $c) {
            Write-Host "  FOUND: $c"
            $found = $true
        }
    }
    if (-not $found) {
        Write-Host "  No standard Obsidian executable found in common locations."
        Write-Host "  If installed via winget, try:"
        Write-Host "    winget show Obsidian.Obsidian"
    }

    Write-Host ""
    Write-Host "--- How to Open Vault ---"
    $escapedVault = [uri]::EscapeDataString($VaultPath)
    $obsidianUri = "obsidian://open?path=$escapedVault"
    Write-Host "  Obsidian URI: $obsidianUri"
    Write-Host "  PowerShell launch command:"
    Write-Host "    Start-Process '$obsidianUri'"
    Write-Host "  Or run with -Open flag:"
    Write-Host "    powershell -ExecutionPolicy Bypass -File '$PSCommandPath' -Open"
    Write-Host ""
    Write-Host "=== End Obsidian Check ==="
    exit 0
}

if ($Open) {
    if (-not (Test-Path $VaultPath)) {
        Write-Host "ERROR: Vault not found at $VaultPath"
        exit 1
    }
    $escapedVault = [uri]::EscapeDataString($VaultPath)
    $obsidianUri = "obsidian://open?path=$escapedVault"
    Write-Host "Opening vault via URI: $obsidianUri"
    Start-Process $obsidianUri
    exit 0
}

Write-Host ""
Write-Host "Usage:"
Write-Host "  .\open_obsidian_vault.ps1 -Check   # Check vault, Obsidian install, open instructions"
Write-Host "  .\open_obsidian_vault.ps1 -Open    # Open vault in Obsidian app via URI"
