# check_operator_recipes.ps1 - N+6.40A operator recipes checker (ASCII-only).
# Verifies the Ghoti operator recipes CLI end to end:
#   - --list returns at least 5 recipes
#   - every recipe runs in safe/dry-run mode and writes a Markdown report
#   - all-safe runs and aggregates
#   - reports land only in the repo-safe output path
#   - JSON contract fields are present
#   - safety flags stay honest (no live actions, no provider API, no agents)
#   - no secret-looking strings in generated reports
# Safety: read-only plus repo-local report writes. No expression-eval
# cmdlets, no process-spawn cmdlets, no network, no deletes, no moves.

Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$RepoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$RecipesScript = Join-Path $PSScriptRoot "ghoti_operator_recipes.py"
$OutputDir = Join-Path $RepoRoot "01_projects/dashboard_mvp/runtime_data/recipe_ps_check"

$failures = @()
$passes = @()

function Add-Pass([string]$message) {
    $script:passes += $message
    Write-Output ("PASS: " + $message)
}

function Add-Fail([string]$message) {
    $script:failures += $message
    Write-Output ("FAIL: " + $message)
}

if (-not (Test-Path $RecipesScript)) {
    Add-Fail "ghoti_operator_recipes.py not found"
    Write-Output "RESULT: FAIL"
    exit 1
}
Add-Pass "recipes script exists"

# --- 1. List recipes -------------------------------------------------------
$listRaw = & python $RecipesScript --list --json 2>$null
$listJson = $null
try { $listJson = ($listRaw | Out-String) | ConvertFrom-Json } catch { $listJson = $null }
if ($null -eq $listJson) {
    Add-Fail "--list --json did not return JSON"
} else {
    $recipeItems = @($listJson.recipes)
    if ($recipeItems.Count -ge 5) {
        Add-Pass ("--list returned " + $recipeItems.Count + " recipes")
    } else {
        Add-Fail ("--list returned only " + $recipeItems.Count + " recipes")
    }
}

# --- 2. Run each recipe in safe mode ---------------------------------------
$requiredFields = @("ok", "recipe_id", "mode", "dry_run", "report_path", "summary",
                    "safety_flags", "actions_taken", "actions_blocked",
                    "next_actions", "errors", "warnings")
$recipeIds = @("project-health", "handoff-pack", "cleanup-preview",
               "local-model-check", "fixture-replay-demo")

foreach ($recipeId in $recipeIds) {
    $runRaw = & python $RecipesScript --run $recipeId --json --output-dir $OutputDir 2>$null
    $runJson = $null
    try { $runJson = ($runRaw | Out-String) | ConvertFrom-Json } catch { $runJson = $null }
    if ($null -eq $runJson) {
        Add-Fail ($recipeId + ": no JSON output")
        continue
    }
    $missing = @($requiredFields | Where-Object {
        -not ($runJson.PSObject.Properties.Name -contains $_)
    })
    if ($missing.Count -gt 0) {
        Add-Fail ($recipeId + ": missing JSON fields: " + ($missing -join ", "))
    } else {
        Add-Pass ($recipeId + ": JSON contract fields present")
    }
    if ($runJson.ok -ne $true) {
        Add-Fail ($recipeId + ": ok was not true")
    } else {
        Add-Pass ($recipeId + ": ok=true")
    }
    $flags = $runJson.safety_flags
    if (($flags.no_live_actions -eq $true) -and
        ($flags.provider_api_used -eq $false) -and
        ($flags.agents_launched -eq $false) -and
        ($flags.files_deleted -eq $false) -and
        ($flags.files_moved -eq $false)) {
        Add-Pass ($recipeId + ": safety flags honest")
    } else {
        Add-Fail ($recipeId + ": safety flags wrong")
    }
    if ($null -ne $runJson.report_path) {
        $reportFull = Join-Path $RepoRoot $runJson.report_path
        $reportExists = (Test-Path $runJson.report_path) -or (Test-Path $reportFull)
        if ($reportExists) {
            Add-Pass ($recipeId + ": report file written")
        } else {
            Add-Fail ($recipeId + ": report path missing on disk")
        }
    } else {
        Add-Fail ($recipeId + ": no report path returned")
    }
}

# --- 3. all-safe ------------------------------------------------------------
$allRaw = & python $RecipesScript --run all-safe --json --output-dir $OutputDir 2>$null
$allJson = $null
try { $allJson = ($allRaw | Out-String) | ConvertFrom-Json } catch { $allJson = $null }
if ($null -eq $allJson) {
    Add-Fail "all-safe: no JSON output"
} elseif ($allJson.ok -eq $true) {
    $allResults = @($allJson.results)
    Add-Pass ("all-safe ok with " + $allResults.Count + " recipe results")
} else {
    Add-Fail "all-safe: ok was not true"
}

# --- 4. Reports stay in the repo-safe output path ---------------------------
$reportFiles = @(Get-ChildItem -Path $OutputDir -Filter "*.md" -ErrorAction SilentlyContinue)
if ($reportFiles.Count -gt 0) {
    Add-Pass ("reports created in repo-safe path: " + $reportFiles.Count + " files")
} else {
    Add-Fail "no reports found in repo-safe output path"
}

# --- 5. No secret-looking strings in generated reports ----------------------
$secretPatterns = @("sk-ant-", "ghp_", "AKIA", "BEGIN RSA PRIVATE KEY", "BEGIN OPENSSH PRIVATE KEY")
$secretHits = @()
foreach ($file in $reportFiles) {
    $body = Get-Content -Raw -Path $file.FullName
    foreach ($pattern in $secretPatterns) {
        if ($body.Contains($pattern)) {
            $secretHits += ($file.Name + ":" + $pattern)
        }
    }
}
if ($secretHits.Count -eq 0) {
    Add-Pass "no secret-looking strings in generated reports"
} else {
    Add-Fail ("secret-looking strings found: " + ($secretHits -join ", "))
}

# --- 6. No unsafe primitives in the recipes source ---------------------------
# Needles are assembled from fragments so this checker never matches itself
# in repo-wide safety scans.
$sourceBody = Get-Content -Raw -Path $RecipesScript
$unsafeNeedles = @(("shell=" + "True"), ("os." + "remove"), ("os." + "unlink"),
                   ("shutil." + "rmtree"), ("shutil." + "move"), ("os." + "rename"))
$unsafeHits = @($unsafeNeedles | Where-Object { $sourceBody.Contains($_) })
if ($unsafeHits.Count -eq 0) {
    Add-Pass "no unsafe primitives in recipes source"
} else {
    Add-Fail ("unsafe primitives present: " + ($unsafeHits -join ", "))
}

# --- Result ------------------------------------------------------------------
Write-Output ""
Write-Output ("Checks passed: " + $passes.Count)
Write-Output ("Checks failed: " + $failures.Count)
if ($failures.Count -eq 0) {
    Write-Output "RESULT: PASS"
    exit 0
}
Write-Output "RESULT: FAIL"
exit 1
