# start_telegram_status_bot.ps1 - start the status-only Telegram bot (foreground).
# Verifies the runtime token / allowed-chat / config files exist (outside the repo),
# then runs the Python bot attached to THIS window so closing the window stops the bot.
# The token is never placed on the command line and is never printed. Pass -DryRun to
# print the would-run command and a JSON status without starting the poll loop.
# Safety: runs only the local bot script; no token in args; no network change here.

[CmdletBinding()]
param(
    [switch]$DryRun
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

$ScriptDir = $PSScriptRoot

$RuntimeDir   = Join-Path $HOME '.ghoti_runtime'
$SecretDir    = Join-Path $HOME '.ghoti_secrets'
$TokenFile    = Join-Path $SecretDir 'telegram_bot_token.txt'
$ChatFile     = Join-Path $SecretDir 'telegram_allowed_chat_id.txt'
$ConfigFile   = Join-Path $RuntimeDir 'telegram_status_config.json'
$PyScript     = Join-Path $ScriptDir 'ghoti_telegram_status_bot.py'

try {
    $tokenExists  = Test-Path -LiteralPath $TokenFile
    $chatExists   = Test-Path -LiteralPath $ChatFile
    $configExists = Test-Path -LiteralPath $ConfigFile
    $ready = $tokenExists -and $chatExists -and $configExists
    $wouldRun = "python -u `"$PyScript`""

    $status = [ordered]@{
        ok                          = $true
        wrapper                     = 'start_telegram_status_bot'
        dry_run                     = [bool]$DryRun
        status_only                 = $true
        token_file_exists           = [bool]$tokenExists
        allowed_chat_id_file_exists = [bool]$chatExists
        config_file_exists          = [bool]$configExists
        ready_to_start              = [bool]$ready
        would_run_command           = $wouldRun
        token_in_command_line       = $false
        warning                     = 'Keep this window open. If it closes, the bot stops.'
    }
    $status | ConvertTo-Json -Depth 6

    if ($DryRun) { exit 0 }

    if (-not $ready) {
        Write-Host 'Cannot start: run setup_telegram_status_bot.ps1 first to create the token, chat id, and runtime config.'
        exit 1
    }

    Write-Host 'Keep this window open. If it closes, the bot stops.'
    & python -u $PyScript
    exit $LASTEXITCODE
}
catch {
    [ordered]@{ ok = $false; wrapper = 'start_telegram_status_bot'; error = $_.Exception.Message; status_only = $true } | ConvertTo-Json -Depth 4
    exit 1
}
