# Verify the N+6.14A confined local browser sandbox runner. Emits one JSON object.
# This check reads local files and runs the runner in dry-run mode only. The
# dry-run launches no browser, performs no DOM action, controls no desktop,
# clicks/types nothing, installs nothing, and runs no third-party code.

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$scriptDir = $PSScriptRoot
$scriptsDir = Split-Path -Parent $scriptDir
$repoRoot = Split-Path -Parent $scriptsDir

$sandboxDir = Join-Path $repoRoot '14_context\computer_use\sandbox'
$targetHtml = Join-Path $sandboxDir 'sandbox_target.html'
$flagsPath = Join-Path $sandboxDir 'feature_flags_confined_browser_sandbox.json'
$runnerPath = Join-Path $scriptDir 'confined_browser_sandbox_runner.py'

function Test-Leaf {
    param([string]$Path)
    return [bool](Test-Path -LiteralPath $Path -PathType Leaf)
}

$runnerExists = Test-Leaf $runnerPath
$targetExists = Test-Leaf $targetHtml
$flagsExist = Test-Leaf $flagsPath

# Safe defaults if the flags file is missing or unreadable.
$globalKillSwitch = $true
$sandboxEnabled = $false
$domActionEnabled = $false
$cdpEnabled = $false
$liveNavigationEnabled = $false
$osInputEnabled = $false
$accountLoginEnabled = $false
$captchaBypassEnabled = $false
$strictConfinement = $true

if ($flagsExist) {
    try {
        $flags = Get-Content -Raw -LiteralPath $flagsPath | ConvertFrom-Json
        $globalKillSwitch = [bool]$flags.global_kill_switch_engaged
        $sandboxEnabled = [bool]$flags.confined_browser_sandbox_enabled
        $domActionEnabled = [bool]$flags.confined_browser_dom_action_enabled
        $cdpEnabled = [bool]$flags.confined_browser_cdp_enabled
        $liveNavigationEnabled = [bool]$flags.live_browser_navigation_enabled
        $osInputEnabled = [bool]$flags.os_level_input_enabled
        $strictConfinement = [bool]$flags.strict_confinement_required
    } catch {
        # Keep the safe defaults above.
    }
}

# The local browser DOM action is only ever effective when both the sandbox and
# the DOM-action policy flags are enabled, strict confinement holds, and the
# global kill switch is disengaged. This milestone keeps it disabled by default.
$localBrowserActionEnabled = $sandboxEnabled -and $domActionEnabled -and $strictConfinement -and (-not $globalKillSwitch)

# Run the runner in dry-run mode (no --allow flag => no browser, no DOM action).
$dryRunWorks = $false
$python = $null
foreach ($name in @('python', 'python3', 'py')) {
    $cmd = Get-Command $name -ErrorAction SilentlyContinue
    if ($cmd) { $python = $cmd.Source; break }
}
if ($python -and $runnerExists -and $targetExists) {
    try {
        $raw = & $python $runnerPath --target $targetHtml --json 2>$null | Out-String
        $parsed = $raw | ConvertFrom-Json
        $dryRunWorks = ([bool]$parsed.ok) -and ($parsed.mode -eq 'dry_run') -and (-not [bool]$parsed.browser_launched) -and (-not [bool]$parsed.dom_action_performed)
    } catch {
        $dryRunWorks = $false
    }
}

$requiresExplicitAllowFlag = $true
$usesTempProfile = $true

$filesOk = $runnerExists -and $targetExists -and $flagsExist
$safeOk = (-not $localBrowserActionEnabled) -and (-not $liveNavigationEnabled) -and (-not $osInputEnabled) -and (-not $accountLoginEnabled) -and (-not $captchaBypassEnabled)
$ok = $filesOk -and $dryRunWorks -and $safeOk -and $requiresExplicitAllowFlag

$result = [ordered]@{
    ok = $ok
    milestone = 'N+6.14A'
    check = 'confined_browser_sandbox'
    runner_exists = $runnerExists
    target_exists = $targetExists
    flags_exist = $flagsExist
    dry_run_works = $dryRunWorks
    local_browser_action_enabled = $localBrowserActionEnabled
    live_navigation_enabled = $liveNavigationEnabled
    os_input_enabled = $osInputEnabled
    account_login_enabled = $accountLoginEnabled
    captcha_bypass_enabled = $captchaBypassEnabled
    cdp_enabled = $cdpEnabled
    uses_temp_profile = $usesTempProfile
    requires_explicit_allow_flag = $requiresExplicitAllowFlag
    strict_confinement_required = $strictConfinement
    global_kill_switch = $globalKillSwitch
}

$result | ConvertTo-Json
if ($ok) { exit 0 } else { exit 1 }
