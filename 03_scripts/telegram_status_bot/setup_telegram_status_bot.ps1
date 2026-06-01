# setup_telegram_status_bot.ps1 - one-time setup for the status-only Telegram bot.
# Creates the runtime/secret folders OUTSIDE the repo, optionally prompts for the bot
# token (as a SecureString) and the allowed chat id, and seeds the runtime config +
# feature flags from the repo examples. It never prints the token, never commits
# anything, never enables a Telegram plugin, and never starts the bot unless the
# explicit -StartAfterSetup flag is passed. Reports a JSON summary.
# Safety: writes only under the user home (.ghoti_runtime/.ghoti_secrets); no repo writes.

[CmdletBinding()]
param(
    [switch]$NoSecretsRequired,
    [switch]$StartAfterSetup
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

$ScriptDir = $PSScriptRoot
$RepoRoot  = Split-Path -Parent (Split-Path -Parent $ScriptDir)

$RuntimeDir    = Join-Path $HOME '.ghoti_runtime'
$SecretDir     = Join-Path $HOME '.ghoti_secrets'
$TokenFile     = Join-Path $SecretDir 'telegram_bot_token.txt'
$ChatFile      = Join-Path $SecretDir 'telegram_allowed_chat_id.txt'
$FlagsRuntime  = Join-Path $RuntimeDir 'ghoti_feature_flags.json'
$ConfigRuntime = Join-Path $RuntimeDir 'telegram_status_config.json'
$FlagsExample  = Join-Path $RepoRoot '23_configs\ghoti_feature_flags.example.json'
$ConfigExample = Join-Path $RepoRoot '23_configs\telegram_status_bot.example.json'

function Write-Utf8NoBom([string]$Path, [string]$Text) {
    [System.IO.File]::WriteAllText($Path, $Text, (New-Object System.Text.UTF8Encoding($false)))
}

try {
    $started = $false

    foreach ($dir in @($RuntimeDir, $SecretDir)) {
        if (-not (Test-Path -LiteralPath $dir)) {
            New-Item -ItemType Directory -Path $dir -Force | Out-Null
        }
    }

    if ((Test-Path -LiteralPath $FlagsExample) -and -not (Test-Path -LiteralPath $FlagsRuntime)) {
        Copy-Item -LiteralPath $FlagsExample -Destination $FlagsRuntime
    }
    if ((Test-Path -LiteralPath $ConfigExample) -and -not (Test-Path -LiteralPath $ConfigRuntime)) {
        Copy-Item -LiteralPath $ConfigExample -Destination $ConfigRuntime
    }

    if (-not $NoSecretsRequired) {
        if (-not (Test-Path -LiteralPath $TokenFile)) {
            $secure = Read-Host -AsSecureString 'Paste the GhotiDeepBot token (input hidden)'
            $bstr = [Runtime.InteropServices.Marshal]::SecureStringToBSTR($secure)
            try {
                $plain = [Runtime.InteropServices.Marshal]::PtrToStringBSTR($bstr)
                Write-Utf8NoBom -Path $TokenFile -Text $plain
            }
            finally {
                [Runtime.InteropServices.Marshal]::ZeroFreeBSTR($bstr)
                $plain = $null
            }
            Write-Host 'Token saved outside the repo. It was not printed.'
        }
        if (-not (Test-Path -LiteralPath $ChatFile)) {
            $chatId = Read-Host 'Enter the allowed Telegram chat id'
            Write-Utf8NoBom -Path $ChatFile -Text ($chatId.Trim())
            Write-Host 'Allowed chat id saved outside the repo.'
        }
    }

    $tokenExists = Test-Path -LiteralPath $TokenFile
    $chatExists  = Test-Path -LiteralPath $ChatFile

    if ($StartAfterSetup -and $tokenExists -and $chatExists) {
        $started = $true
        & (Join-Path $ScriptDir 'start_telegram_status_bot.ps1')
    }

    $result = [ordered]@{
        ok                          = $true
        wrapper                     = 'setup_telegram_status_bot'
        runtime_dir                 = $RuntimeDir
        secret_dir                  = $SecretDir
        token_file_exists           = [bool]$tokenExists
        allowed_chat_id_file_exists = [bool]$chatExists
        config_file_exists          = (Test-Path -LiteralPath $ConfigRuntime)
        feature_flags_file_exists   = (Test-Path -LiteralPath $FlagsRuntime)
        started                     = [bool]$started
        secrets_printed             = $false
        repo_modified               = $false
    }
    $result | ConvertTo-Json -Depth 6
    exit 0
}
catch {
    [ordered]@{ ok = $false; wrapper = 'setup_telegram_status_bot'; error = $_.Exception.Message; secrets_printed = $false; repo_modified = $false } | ConvertTo-Json -Depth 4
    exit 1
}
