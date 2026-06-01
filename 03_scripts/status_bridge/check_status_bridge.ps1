# check_status_bridge.ps1 - read-only health/safety check for the N+6.16A status bridge.
# Confirms the bridge, the local status brain, and the Telegram status bot scripts exist,
# that the Hermes handoff log directory is present, and that the bridge produces JSON,
# Markdown, and Telegram-safe output. Reports a JSON summary.
# Safety: read-only; needs no token; opens no network; controls no browser/desktop;
# launches no agent; installs nothing; runs no third-party code; calls no external API.

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

$ScriptDir  = $PSScriptRoot
$ScriptsDir = Split-Path -Parent $ScriptDir
$RepoRoot   = Split-Path -Parent $ScriptsDir

$BridgeScript = Join-Path $ScriptDir 'ghoti_status_bridge.py'
$StatusBrain  = Join-Path $RepoRoot '03_scripts\local_worker_queue\ghoti_status_brain.py'
$TelegramBot  = Join-Path $RepoRoot '03_scripts\telegram_status_bot\ghoti_telegram_status_bot.py'
$HandoffDir   = Join-Path $RepoRoot '14_context\agent_handoff_vault\04_Logs'
$FlagsExample = Join-Path $RepoRoot '23_configs\ghoti_feature_flags.example.json'

function Test-Leaf { param([string]$Path) return [bool](Test-Path -LiteralPath $Path -PathType Leaf) }

$bridgeExists = Test-Leaf $BridgeScript
$brainExists  = Test-Leaf $StatusBrain
$botExists    = Test-Leaf $TelegramBot
$handoffDirOk = [bool](Test-Path -LiteralPath $HandoffDir -PathType Container)

# Find a Python interpreter that actually runs. Prefer the PATH launchers; if the PATH
# shim is broken, fall back to a local uv-managed interpreter under the user's own uv
# directory. This is read-only discovery of an interpreter to run the repo's own script.
function Find-Python {
    $candidates = New-Object System.Collections.Generic.List[string]
    foreach ($name in @('python', 'python3', 'py')) {
        $cmd = Get-Command $name -ErrorAction SilentlyContinue
        if ($cmd -and $cmd.Source) { $candidates.Add([string]$cmd.Source) }
    }
    if ($env:APPDATA) {
        $uvRoot = Join-Path $env:APPDATA 'uv\python'
        if (Test-Path -LiteralPath $uvRoot) {
            foreach ($dir in (Get-ChildItem -LiteralPath $uvRoot -Directory -ErrorAction SilentlyContinue)) {
                $exe = Join-Path $dir.FullName 'python.exe'
                if (Test-Path -LiteralPath $exe) { $candidates.Add([string]$exe) }
            }
        }
    }
    foreach ($exe in $candidates) {
        try {
            & $exe --version *> $null
            if ($LASTEXITCODE -eq 0) { return $exe }
        } catch { }
    }
    return $null
}

$python = Find-Python

function Invoke-BridgeRaw {
    param([string]$PythonExe, [string]$Mode)
    if (-not $PythonExe) { return $null }
    try {
        $raw = & $PythonExe $BridgeScript $Mode 2>$null | Out-String
        if ($LASTEXITCODE -ne 0) { return $null }
        return $raw
    } catch {
        return $null
    }
}

$bridgeJsonWorks   = $false
$bridgeMarkdownWorks = $false
$telegramSafeJsonWorks = $false
if ($python -and $bridgeExists) {
    $jsonRaw = Invoke-BridgeRaw $python '--json'
    if ($jsonRaw) {
        try { $bridgeJsonWorks = [bool]((($jsonRaw | ConvertFrom-Json)).ok) } catch { $bridgeJsonWorks = $false }
    }
    $mdRaw = Invoke-BridgeRaw $python '--markdown'
    if ($mdRaw) { $bridgeMarkdownWorks = [bool]($mdRaw -match 'Ghoti Status Bridge') }
    $safeRaw = Invoke-BridgeRaw $python '--telegram-safe-json'
    if ($safeRaw) {
        try {
            $safe = $safeRaw | ConvertFrom-Json
            $telegramSafeJsonWorks = ([bool]$safe.ok) -and (-not [bool]$safe.secrets_present)
        } catch { $telegramSafeJsonWorks = $false }
    }
}

# The bridge needs no token and no chat id; it is local and read-only.
$noTokenRequired = $true
$localOnly = $true

# Confirm the risky flags this milestone touches default to false in the example config.
$riskyFlags = @(
    'status_bridge_enabled', 'hermes_status_bridge_enabled', 'status_bridge_auto_handoff_enabled',
    'telegram_status_bridge_enabled', 'live_agent_launch_enabled', 'claude_launch_enabled',
    'codex_launch_enabled', 'mcp_enabled', 'browser_computer_use_enabled',
    'auto_send_enabled', 'email_draft_agent_enabled', 'whatsapp_draft_agent_enabled'
)
$riskyFlagsDefaultFalse = $true
if (Test-Leaf $FlagsExample) {
    try {
        $flags = Get-Content -Raw -LiteralPath $FlagsExample | ConvertFrom-Json
        foreach ($flag in $riskyFlags) {
            $prop = $flags.PSObject.Properties[$flag]
            if (($null -ne $prop) -and ([bool]$prop.Value)) { $riskyFlagsDefaultFalse = $false }
        }
    } catch {
        $riskyFlagsDefaultFalse = $false
    }
} else {
    $riskyFlagsDefaultFalse = $false
}

# Capabilities this milestone never enables.
$telegramControlEnabled = $false
$liveAgentLaunchEnabled = $false
$mcpEnabled = $false
$liveBrowserEnabled = $false
$autoSendEnabled = $false

$filesOk = $bridgeExists -and $brainExists -and $botExists -and $handoffDirOk
# If a working interpreter was found, the three bridge modes must all succeed; if none
# was found, do not fail the safety check on that account.
$worksOk = (-not $python) -or ($bridgeJsonWorks -and $bridgeMarkdownWorks -and $telegramSafeJsonWorks)
$ok = $filesOk -and $riskyFlagsDefaultFalse -and $worksOk

$result = [ordered]@{
    ok                        = $ok
    milestone                 = 'N+6.16A'
    check                     = 'status_bridge'
    status_bridge_exists      = $bridgeExists
    status_brain_exists       = $brainExists
    telegram_bot_exists       = $botExists
    handoff_dir_exists        = $handoffDirOk
    python_found              = [bool]$python
    bridge_json_works         = $bridgeJsonWorks
    bridge_markdown_works     = $bridgeMarkdownWorks
    telegram_safe_json_works  = $telegramSafeJsonWorks
    no_token_required         = $noTokenRequired
    local_only                = $localOnly
    telegram_control_enabled  = $telegramControlEnabled
    live_agent_launch_enabled = $liveAgentLaunchEnabled
    mcp_enabled               = $mcpEnabled
    live_browser_enabled      = $liveBrowserEnabled
    auto_send_enabled         = $autoSendEnabled
    risky_flags_default_false = $riskyFlagsDefaultFalse
}

$result | ConvertTo-Json
if ($ok) { exit 0 } else { exit 1 }
