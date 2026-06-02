<#
.SYNOPSIS
  Enable the Telegram /status status-bridge path in the LOCAL runtime config.

.DESCRIPTION
  Turns on the two status-bridge flags in the status-only Telegram bot's runtime
  config so /status answers from the status bridge. The runtime config lives OUTSIDE
  the repo (default C:/Users/ai_sandbox/.ghoti_runtime/telegram_status_config.json)
  and is never committed.

  This script writes NO secrets. The config holds only file PATHS to the token and
  allowed-chat-id files, which live outside the repo; their values are never read or
  written here. Telegram stays status-only: there is no /run and no live control.

  If a runtime config already exists it is loaded and only the two bridge flags are
  set (every other value preserved); otherwise a fresh status-only config is built
  from 23_configs/runtime_activation.example.json.

  Pass -DryRun to read any existing config read-only and print what WOULD be written,
  writing nothing. No Invoke-Expression, no network, no external API.
#>
[CmdletBinding()]
param(
    [switch]$DryRun,
    [string]$ConfigPath,
    [string]$RepoRootOverride
)

$ErrorActionPreference = 'Stop'
$RepoRoot = if ($RepoRootOverride) {
    $RepoRootOverride
} else {
    (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
}

# Defaults from the activation example config when available.
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

$runtimeDir   = Get-CfgValue 'runtime_dir' 'C:/Users/ai_sandbox/.ghoti_runtime'
$targetConfig = if ($ConfigPath) { $ConfigPath } else { Get-CfgValue 'telegram_config_path' (Join-Path $runtimeDir 'telegram_status_config.json') }
$tokenFile    = Get-CfgValue 'telegram_token_file' 'C:/Users/ai_sandbox/.ghoti_secrets/telegram_bot_token.txt'
$chatIdFile   = Get-CfgValue 'telegram_allowed_chat_id_file' 'C:/Users/ai_sandbox/.ghoti_secrets/telegram_allowed_chat_id.txt'
$repoRootForConfig = Get-CfgValue 'repo_root' $RepoRoot
$featureFlags = (Join-Path $runtimeDir 'ghoti_feature_flags.json')

# Load an existing runtime config (read-only) so we preserve everything but the two
# bridge flags; otherwise start from the documented status-only defaults.
$existing = $null
$configExisted = Test-Path -LiteralPath $targetConfig
if ($configExisted) {
    try { $existing = Get-Content -LiteralPath $targetConfig -Raw | ConvertFrom-Json } catch { $existing = $null }
}
function Get-Field {
    param([string]$Key, $Default)
    if ($existing -and ($existing.PSObject.Properties.Name -contains $Key) -and ($null -ne $existing.$Key)) { return $existing.$Key }
    return $Default
}

$newConfig = [ordered]@{
    repo_root                             = [string](Get-Field 'repo_root' $repoRootForConfig)
    token_file                            = [string](Get-Field 'token_file' $tokenFile)
    allowed_chat_id_file                  = [string](Get-Field 'allowed_chat_id_file' $chatIdFile)
    feature_flags_file                    = [string](Get-Field 'feature_flags_file' $featureFlags)
    poll_timeout_seconds                  = [int](Get-Field 'poll_timeout_seconds' 25)
    message_preview_limit                 = [int](Get-Field 'message_preview_limit' 3500)
    status_only                           = $true
    status_bridge_enabled                 = $true
    status_bridge_script_path             = [string](Get-Field 'status_bridge_script_path' '03_scripts/status_bridge/ghoti_status_bridge.py')
    status_bridge_timeout_seconds         = [int](Get-Field 'status_bridge_timeout_seconds' 20)
    use_status_bridge_for_telegram_status = $true
}

$json = ($newConfig | ConvertTo-Json -Depth 6)

$normTarget = ($targetConfig -replace '\\', '/')
$normRoot = ($RepoRoot -replace '\\', '/')
$configOutsideRepo = (-not $normTarget.StartsWith($normRoot, [System.StringComparison]::OrdinalIgnoreCase))

# Never read or echo secret VALUES; only report whether the config would change and
# which secret-file PATHS it points at.
$status = [ordered]@{
    ok                                    = $true
    wrapper                               = 'enable_status_bridge_runtime_config'
    dry_run                               = [bool]$DryRun
    runtime_config_path                   = $targetConfig
    config_existed                        = [bool]$configExisted
    config_outside_repo                   = [bool]$configOutsideRepo
    status_only                           = $true
    status_bridge_enabled                 = $true
    use_status_bridge_for_telegram_status = $true
    telegram_control_enabled              = $false
    token_file_path                       = [string]$newConfig.token_file
    allowed_chat_id_file_path             = [string]$newConfig.allowed_chat_id_file
    secrets_written                       = $false
    config_written                        = (-not [bool]$DryRun)
    config_preview                        = $newConfig
}

if ($DryRun) {
    $status | ConvertTo-Json -Depth 8
    exit 0
}

# Real write: create the runtime dir and write the config OUTSIDE the repo. Only file
# paths to secrets are written - never a token value and never a chat id value.
$targetDir = Split-Path -Parent $targetConfig
if ($targetDir -and -not (Test-Path -LiteralPath $targetDir)) {
    New-Item -ItemType Directory -Path $targetDir -Force | Out-Null
}
Set-Content -LiteralPath $targetConfig -Value $json -Encoding UTF8
$status | ConvertTo-Json -Depth 8
exit 0
