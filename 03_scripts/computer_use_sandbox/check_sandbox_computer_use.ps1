# Verify the N+6.13A sandbox computer-use action harness. Emits a single JSON object.
# This check reads local files only. It never starts a browser, controls the
# desktop, clicks, types, installs anything, or runs third-party code.

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$scriptDir = $PSScriptRoot
$scriptsDir = Split-Path -Parent $scriptDir
$repoRoot = Split-Path -Parent $scriptsDir

$sandboxDir = Join-Path $repoRoot '14_context\computer_use\sandbox'
$targetHtml = Join-Path $sandboxDir 'sandbox_target.html'
$fixturePath = Join-Path $sandboxDir 'sandbox_observation_fixture.json'
$flagsPath = Join-Path $sandboxDir 'feature_flags_sandbox_computer_use.json'
$plannerPath = Join-Path $scriptDir 'sandbox_action_planner.py'
$runnerPath = Join-Path $scriptDir 'sandbox_action_runner.py'

function Test-Leaf {
    param([string]$Path)
    return [bool](Test-Path -LiteralPath $Path -PathType Leaf)
}

$sandboxTargetExists = Test-Leaf $targetHtml
$fixtureExists = Test-Leaf $fixturePath
$plannerExists = Test-Leaf $plannerPath
$runnerExists = Test-Leaf $runnerPath
$flagsExist = Test-Leaf $flagsPath

# Safe defaults if the flags file is missing or unreadable.
$dryRunEnabled = $true
$liveBrowserEnabled = $false
$accountLoginEnabled = $false
$captchaBypassEnabled = $false
$realClickFlag = $false
$realTypeFlag = $false
$globalKillSwitch = $true
$strictConfinement = $false

if ($flagsExist) {
    try {
        $flags = Get-Content -Raw -LiteralPath $flagsPath | ConvertFrom-Json
        $dryRunEnabled = [bool]$flags.sandbox_computer_use_dry_run_enabled
        $liveBrowserEnabled = [bool]$flags.live_browser_computer_use_enabled
        $accountLoginEnabled = [bool]$flags.account_login_automation_enabled
        $captchaBypassEnabled = [bool]$flags.captcha_bypass_enabled
        $realClickFlag = [bool]$flags.sandbox_computer_use_real_click_enabled
        $realTypeFlag = [bool]$flags.sandbox_computer_use_real_type_enabled
        $globalKillSwitch = [bool]$flags.global_kill_switch_engaged
        $strictConfinement = [bool]$flags.strict_sandbox_confinement_guaranteed
    } catch {
        # Keep the safe defaults above.
    }
}

# Real click/type are only ever effective if strict confinement is guaranteed and
# the global kill switch is disengaged. This milestone keeps both off.
$realClickEnabled = $realClickFlag -and $strictConfinement -and (-not $globalKillSwitch)
$realTypeEnabled = $realTypeFlag -and $strictConfinement -and (-not $globalKillSwitch)

$filesOk = $sandboxTargetExists -and $fixtureExists -and $plannerExists -and $runnerExists -and $flagsExist
$safeOk = $dryRunEnabled -and (-not $liveBrowserEnabled) -and (-not $accountLoginEnabled) -and (-not $captchaBypassEnabled) -and (-not $realClickEnabled) -and (-not $realTypeEnabled)
$ok = $filesOk -and $safeOk

$result = [ordered]@{
    ok = $ok
    milestone = 'N+6.13A'
    check = 'sandbox_computer_use'
    sandbox_target_exists = $sandboxTargetExists
    fixture_exists = $fixtureExists
    planner_exists = $plannerExists
    runner_exists = $runnerExists
    feature_flags_exists = $flagsExist
    dry_run_enabled = $dryRunEnabled
    live_browser_enabled = $liveBrowserEnabled
    account_login_enabled = $accountLoginEnabled
    captcha_bypass_enabled = $captchaBypassEnabled
    real_click_enabled = $realClickEnabled
    real_type_enabled = $realTypeEnabled
    strict_sandbox_confinement_guaranteed = $strictConfinement
    global_kill_switch = $globalKillSwitch
}

$result | ConvertTo-Json
if ($ok) { exit 0 } else { exit 1 }
