<#
.SYNOPSIS
  Resume the same WSL Hermes session (preview by default).

.DESCRIPTION
  Prints the exact, ready-to-run command that resumes the existing WSL Hermes
  session 20260601_081506_d35c70 inside the repo mount, and emits a JSON status. By
  default it only PREVIEWS the command and launches nothing. Pass -Run to actually
  start WSL Hermes attached to this window (keep the window open).

  Defaults (distro, session id, repo mount) are read from
  23_configs/runtime_activation.example.json when present. WSL Hermes is the only
  Hermes installation now; the Windows Hermes Desktop app was deleted.

  No Invoke-Expression; when -Run is passed, wsl is launched with an argument array.
  No installs, no secrets, and no network change is made by this wrapper itself.
#>
[CmdletBinding()]
param(
    [switch]$Run
)

$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path

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
$distro    = Get-CfgValue 'hermes_wsl_distro' 'Ubuntu'
$sessionId = Get-CfgValue 'hermes_session_id' '20260601_081506_d35c70'
$repoMount = Get-CfgValue 'hermes_repo_mount' '/mnt/c/Users/ai_sandbox/Documents/AI_Managed_Only'

# The in-WSL command. PATH is set first so the hermes launcher is found in a
# non-login context; then the same session is resumed.
$innerPath = '/home/ai_sandbox/.local/bin:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin'
$innerCmd = "export PATH=$innerPath; hermes --resume $sessionId"

# Argument array (PowerShell executes no shell string; wsl parses from -- onward).
$wslArgs = @('-d', $distro, '--cd', $repoMount, '--', 'bash', '-lc', $innerCmd)
$commandPreview = "wsl -d $distro --cd $repoMount -- bash -lc '$innerCmd'"

$wslAvailable = [bool](Get-Command 'wsl' -ErrorAction SilentlyContinue)

$status = [ordered]@{
    ok                             = $true
    wrapper                        = 'resume_wsl_hermes_session'
    run                            = [bool]$Run
    wsl_available                  = [bool]$wslAvailable
    distro                         = $distro
    session_id                     = $sessionId
    repo_mount                     = $repoMount
    command_preview                = $commandPreview
    hermes_wsl_only                = $true
    windows_hermes_desktop_deleted = $true
    local_only                     = $true
    secrets_present                = $false
}
$status | ConvertTo-Json -Depth 6

if (-not $Run) { exit 0 }

if (-not $wslAvailable) {
    Write-Host 'Cannot resume: wsl is not available on this host.'
    exit 1
}
Write-Host ('Resuming WSL Hermes session {0} (keep this window open).' -f $sessionId)
& wsl @wslArgs
exit $LASTEXITCODE
