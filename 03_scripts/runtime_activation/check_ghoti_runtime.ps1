<#
.SYNOPSIS
  One command to check Ghoti runtime health. Emits a single JSON object.

.DESCRIPTION
  Local and read-only. Resolves a working Python (skipping a broken PATH shim),
  reports origin/main, checks that the status brain and status bridge scripts are
  present, checks that the Telegram bot scripts and secret files are present
  (existence only, never reading secret values), and best-effort probes WSL Hermes,
  ollama, and a local gemma model.

  No network, no external API, no agent launch, no Telegram control, no MCP, no live
  browser, no OS input, no auto-send, no installs. No Invoke-Expression; every
  external call uses an argument array.
#>
[CmdletBinding()]
param(
    [switch]$Json
)

$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path

function Test-CommandAvailable {
    param([string]$Name)
    return [bool](Get-Command $Name -ErrorAction SilentlyContinue)
}

function Get-GemmaAvailable {
    if (-not (Test-CommandAvailable 'ollama')) { return $false }
    try {
        $job = Start-Job -ScriptBlock { try { & ollama list 2>$null | Out-String } catch { '' } }
        if (Wait-Job $job -Timeout 12) {
            $out = Receive-Job $job
            Remove-Job $job -Force -ErrorAction SilentlyContinue
            return ([string]$out -match '(?i)gemma')
        } else {
            Stop-Job $job -ErrorAction SilentlyContinue
            Remove-Job $job -Force -ErrorAction SilentlyContinue
            return $false
        }
    } catch { return $false }
}

# Load the activation example config for default paths / session id.
$cfg = $null
$cfgPath = Join-Path $RepoRoot '23_configs\runtime_activation.example.json'
if (Test-Path -LiteralPath $cfgPath) {
    try { $cfg = Get-Content -LiteralPath $cfgPath -Raw | ConvertFrom-Json } catch { $cfg = $null }
}
function Get-CfgValue {
    param([string]$Key, [string]$Default)
    if ($cfg -and ($cfg.PSObject.Properties.Name -contains $Key) -and $cfg.$Key) { return [string]$cfg.$Key }
    return $Default
}
$sessionId         = Get-CfgValue 'hermes_session_id' '20260601_081506_d35c70'
$runtimeConfigPath = Get-CfgValue 'telegram_config_path' 'C:/Users/ai_sandbox/.ghoti_runtime/telegram_status_config.json'
$tokenFile         = Get-CfgValue 'telegram_token_file' 'C:/Users/ai_sandbox/.ghoti_secrets/telegram_bot_token.txt'
$chatIdFile        = Get-CfgValue 'telegram_allowed_chat_id_file' 'C:/Users/ai_sandbox/.ghoti_secrets/telegram_allowed_chat_id.txt'

# Resolve Python via the resolver script (in-process; its exit code does not stop us).
$pyOk = $false
$pyExe = $null
$resolver = Join-Path $PSScriptRoot 'ghoti_python_resolver.ps1'
if (Test-Path -LiteralPath $resolver) {
    try {
        $rout = & $resolver 2>$null
        $robj = ($rout | Out-String | ConvertFrom-Json)
        if ($robj -and $robj.ok -eq $true -and $robj.executable) {
            $pyOk = $true
            $pyExe = [string]$robj.executable
        }
    } catch { $pyOk = $false }
}

# origin/main (read-only git).
$originMainShort = $null
try {
    $g = & git -C $RepoRoot rev-parse --short origin/main 2>$null
    if ($LASTEXITCODE -eq 0 -and $g) { $originMainShort = ([string]$g).Trim() }
} catch { $originMainShort = $null }

# Presence checks.
$statusBrainOk = Test-Path -LiteralPath (Join-Path $RepoRoot '03_scripts\local_worker_queue\ghoti_status_brain.py')
$statusBridgeOk = Test-Path -LiteralPath (Join-Path $RepoRoot '03_scripts\status_bridge\ghoti_status_bridge.py')
$botScript = Join-Path $RepoRoot '03_scripts\telegram_status_bot\ghoti_telegram_status_bot.py'
$telegramBotScriptsPresent = Test-Path -LiteralPath $botScript
$telegramSecretFilesPresent = ((Test-Path -LiteralPath $tokenFile) -and (Test-Path -LiteralPath $chatIdFile))

$payload = [ordered]@{
    ok                            = ($pyOk -and $statusBrainOk -and $statusBridgeOk)
    repo_root                     = $RepoRoot
    origin_main_short             = $originMainShort
    python_ok                     = $pyOk
    python_executable             = $pyExe
    status_brain_ok               = $statusBrainOk
    status_bridge_ok              = $statusBridgeOk
    telegram_bot_scripts_present  = $telegramBotScriptsPresent
    telegram_secret_files_present = $telegramSecretFilesPresent
    hermes_wsl_available          = (Test-CommandAvailable 'wsl')
    ollama_available              = (Test-CommandAvailable 'ollama')
    gemma_available               = (Get-GemmaAvailable)
    same_session_id               = $sessionId
    runtime_config_path           = $runtimeConfigPath
    local_only                    = $true
    live_browser_enabled          = $false
    telegram_control_enabled      = $false
    mcp_enabled                   = $false
    auto_send_enabled             = $false
}

$payload | ConvertTo-Json -Depth 5
