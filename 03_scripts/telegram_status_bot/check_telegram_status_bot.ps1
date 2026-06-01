# check_telegram_status_bot.ps1 - read-only health/safety check for the status bot pack.
# Confirms the runtime scripts and config examples exist, reports whether the runtime
# secret/config files are present (existence only, never their values), and reports the
# standing safety flags from the runtime flags file if present, otherwise the repo
# example. Reports a JSON summary. Pass -NoSecretsRequired for CI/test (no secret needed).
# Safety: read-only; prints no token; prints no raw chat id; makes no repo or network change.

[CmdletBinding()]
param(
    [switch]$NoSecretsRequired
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

$ScriptDir = $PSScriptRoot
$RepoRoot  = Split-Path -Parent (Split-Path -Parent $ScriptDir)

$RuntimeDir   = Join-Path $HOME '.ghoti_runtime'
$SecretDir    = Join-Path $HOME '.ghoti_secrets'
$TokenFile    = Join-Path $SecretDir 'telegram_bot_token.txt'
$ChatFile     = Join-Path $SecretDir 'telegram_allowed_chat_id.txt'
$FlagsRuntime = Join-Path $RuntimeDir 'ghoti_feature_flags.json'

$PyScript      = Join-Path $ScriptDir 'ghoti_telegram_status_bot.py'
$SetupScript   = Join-Path $ScriptDir 'setup_telegram_status_bot.ps1'
$StartScript   = Join-Path $ScriptDir 'start_telegram_status_bot.ps1'
$ConfigExample = Join-Path $RepoRoot '23_configs\telegram_status_bot.example.json'
$FlagsExample  = Join-Path $RepoRoot '23_configs\ghoti_feature_flags.example.json'

# Risky flags: every flag except the read-only status command toggle must default false.
$RiskyFlagNames = @(
    'global_kill_switch', 'telegram_status_bot_enabled', 'telegram_run_commands_enabled',
    'telegram_send_commands_enabled', 'mcp_enabled', 'mcp_filesystem_read_only_enabled',
    'live_agent_launch_enabled', 'claude_launch_enabled', 'codex_launch_enabled',
    'browser_computer_use_enabled', 'email_draft_agent_enabled', 'whatsapp_draft_agent_enabled',
    'auto_send_enabled', 'external_repo_install_enabled', 'affiliate_program_enabled',
    'dashboard_local_analytics_enabled', 'docker_runtime_enabled', 'vps_runtime_enabled'
)

function Get-Flags {
    $source = if (Test-Path -LiteralPath $FlagsRuntime) { $FlagsRuntime } elseif (Test-Path -LiteralPath $FlagsExample) { $FlagsExample } else { $null }
    if ($null -eq $source) { return $null }
    try { return (Get-Content -LiteralPath $source -Raw | ConvertFrom-Json) } catch { return $null }
}

function Flag-Bool($flags, [string]$name) {
    if ($null -eq $flags) { return $false }
    if ($flags.PSObject.Properties.Name -contains $name) { return [bool]$flags.$name }
    return $false
}

try {
    $flags = Get-Flags

    $riskyAllFalse = $true
    if ($null -ne $flags) {
        foreach ($name in $RiskyFlagNames) {
            if (Flag-Bool $flags $name) { $riskyAllFalse = $false }
        }
    }

    $result = [ordered]@{
        ok                          = $true
        wrapper                     = 'check_telegram_status_bot'
        repo_root                   = $RepoRoot
        no_secrets_required         = [bool]$NoSecretsRequired
        python_script_exists        = (Test-Path -LiteralPath $PyScript)
        setup_script_exists         = (Test-Path -LiteralPath $SetupScript)
        start_script_exists         = (Test-Path -LiteralPath $StartScript)
        example_config_exists       = (Test-Path -LiteralPath $ConfigExample)
        feature_flags_example_exists = (Test-Path -LiteralPath $FlagsExample)
        token_file_exists           = (Test-Path -LiteralPath $TokenFile)
        allowed_chat_id_file_exists = (Test-Path -LiteralPath $ChatFile)
        telegram_status_bot_enabled = (Flag-Bool $flags 'telegram_status_bot_enabled')
        global_kill_switch          = (Flag-Bool $flags 'global_kill_switch')
        risky_flags_default_false   = [bool]$riskyAllFalse
        no_live_agent_launch        = (-not (Flag-Bool $flags 'live_agent_launch_enabled') -and -not (Flag-Bool $flags 'claude_launch_enabled') -and -not (Flag-Bool $flags 'codex_launch_enabled'))
        no_mcp                      = (-not (Flag-Bool $flags 'mcp_enabled') -and -not (Flag-Bool $flags 'mcp_filesystem_read_only_enabled'))
        no_browser_computer_use     = (-not (Flag-Bool $flags 'browser_computer_use_enabled'))
        no_auto_send                = (-not (Flag-Bool $flags 'auto_send_enabled'))
    }
    $result | ConvertTo-Json -Depth 6
    exit 0
}
catch {
    [ordered]@{ ok = $false; wrapper = 'check_telegram_status_bot'; error = $_.Exception.Message } | ConvertTo-Json -Depth 4
    exit 1
}
