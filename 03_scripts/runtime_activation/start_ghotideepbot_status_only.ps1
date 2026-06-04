<#
.SYNOPSIS
  Start the status-only GhotiDeepBot Telegram runtime using a resolved Python.

.DESCRIPTION
  Like 03_scripts/telegram_status_bot/start_telegram_status_bot.ps1, but first
  resolves a working Python interpreter (skipping a broken PATH shim) with
  ghoti_python_resolver.ps1, then runs the local status-only bot attached to THIS
  window so closing the window stops the bot.

  The bot is status-only: there is no /run and no live control. It verifies the
  runtime token / allowed-chat / config files exist OUTSIDE the repo (existence
  only, never reading their values). The token is never placed on the command line
  and never printed.

  Pass -DryRun to print the would-run command and a JSON status without starting the
  poll loop. No Invoke-Expression; the bot is launched with an argument array. This
  wrapper itself makes no network change.
#>
[CmdletBinding()]
param(
    [switch]$DryRun
)

$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path

$RuntimeDir = Join-Path $HOME '.ghoti_runtime'
$SecretDir  = Join-Path $HOME '.ghoti_secrets'
$TokenFile  = Join-Path $SecretDir 'telegram_bot_token.txt'
$ChatFile   = Join-Path $SecretDir 'telegram_allowed_chat_id.txt'
$ConfigFile = Join-Path $RuntimeDir 'telegram_status_config.json'
$PyScript   = Join-Path $RepoRoot '03_scripts\telegram_status_bot\ghoti_telegram_status_bot.py'

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

$tokenExists  = Test-Path -LiteralPath $TokenFile
$chatExists   = Test-Path -LiteralPath $ChatFile
$configExists = Test-Path -LiteralPath $ConfigFile
$botExists    = Test-Path -LiteralPath $PyScript
$ready = ($pyOk -and $botExists -and $tokenExists -and $chatExists -and $configExists)

$wouldRun = if ($pyExe) {
    ('"{0}" -u "{1}"' -f $pyExe, $PyScript)
} else {
    ('(no python resolved) -u "{0}"' -f $PyScript)
}

$status = [ordered]@{
    ok                          = [bool]$ready
    wrapper                     = 'start_ghotideepbot_status_only'
    dry_run                     = [bool]$DryRun
    status_only                 = $true
    python_ok                   = [bool]$pyOk
    python_executable           = $pyExe
    bot_script_present          = [bool]$botExists
    token_file_exists           = [bool]$tokenExists
    allowed_chat_id_file_exists = [bool]$chatExists
    config_file_exists          = [bool]$configExists
    ready_to_start              = [bool]$ready
    would_run_command           = $wouldRun
    token_in_command_line       = $false
    telegram_control_enabled    = $false
    warning                     = 'Keep this window open. If it closes, the bot stops.'
}
$status | ConvertTo-Json -Depth 6

if ($DryRun) { exit 0 }

if (-not $ready) {
    Write-Host 'Cannot start: resolve Python and run the Telegram status setup first (token, chat id, runtime config).'
    exit 1
}

Write-Host 'Keep this window open. If it closes, the bot stops.'
& $pyExe -u $PyScript
exit $LASTEXITCODE
