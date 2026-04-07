[CmdletBinding()]
param(
    [switch]$StatusOnly
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-Check {
    param(
        [string]$Name,
        [bool]$Passed,
        [string]$Detail
    )

    $label = if ($Passed) { 'PASS' } else { 'FAIL' }
    Write-Host ("[{0}] {1}: {2}" -f $label, $Name, $Detail)
}

$failed = 0
$mode = if ($StatusOnly) { 'status' } else { 'check' }

$powerShellVersion = $PSVersionTable.PSVersion.ToString()
$powerShellAvailable = $true
Write-Check -Name 'PowerShell environment' -Passed $powerShellAvailable -Detail $powerShellVersion

$explorerCommand = Get-Command explorer.exe -ErrorAction SilentlyContinue
$explorerAvailable = $null -ne $explorerCommand
Write-Check -Name 'Explorer available' -Passed $explorerAvailable -Detail ($(if ($explorerAvailable) { $explorerCommand.Source } else { 'explorer.exe not found' }))
if (-not $explorerAvailable) { $failed++ }

$processCount = 0
$processVisibility = $false
try {
    $processCount = @(Get-Process | Select-Object -First 5).Count
    $processVisibility = $processCount -gt 0
}
catch {
    $processVisibility = $false
}
Write-Check -Name 'Process visibility' -Passed $processVisibility -Detail ($(if ($processVisibility) { "$processCount sample processes visible" } else { 'unable to enumerate processes' }))
if (-not $processVisibility) { $failed++ }

$shellResult = powershell.exe -NoProfile -Command "Write-Output desktop_bridge_shell_ok"
$shellCommandCapability = $LASTEXITCODE -eq 0 -and $shellResult -match 'desktop_bridge_shell_ok'
Write-Check -Name 'Shell command capability' -Passed $shellCommandCapability -Detail ($(if ($shellCommandCapability) { 'child PowerShell command succeeded' } else { 'child PowerShell command failed' }))
if (-not $shellCommandCapability) { $failed++ }

$launcherCapability = $false
$launcherDetail = 'not run'
if (-not $StatusOnly) {
    try {
        $launcher = Start-Process `
            -FilePath 'cmd.exe' `
            -ArgumentList '/c', 'exit 0' `
            -NoNewWindow `
            -PassThru `
            -Wait
        $launcherCapability = $launcher.ExitCode -eq 0
        $launcherDetail = if ($launcherCapability) { 'cmd.exe launched and exited cleanly' } else { "launcher exit code $($launcher.ExitCode)" }
    }
    catch {
        $launcherCapability = $false
        $launcherDetail = $_.Exception.Message
    }

    Write-Check -Name 'Local launcher capability' -Passed $launcherCapability -Detail $launcherDetail
    if (-not $launcherCapability) { $failed++ }
}
else {
    Write-Check -Name 'Local launcher capability' -Passed $true -Detail 'status-only mode skipped live launcher test'
}

$headline = if ($failed -eq 0) {
    'Desktop bridge foundation is available for safe local checks.'
}
else {
    'Desktop bridge foundation has failing prerequisites.'
}

Write-Output "mode: $mode"
Write-Output "headline: $headline"
Write-Output "powershell_available: yes"
Write-Output "powershell_version: $powerShellVersion"
Write-Output "explorer_available: $(if ($explorerAvailable) { 'yes' } else { 'no' })"
Write-Output "process_visibility: $(if ($processVisibility) { 'yes' } else { 'no' })"
Write-Output "shell_command_capability: $(if ($shellCommandCapability) { 'yes' } else { 'no' })"
Write-Output "launcher_capability: $(if ($StatusOnly) { 'not_run' } elseif ($launcherCapability) { 'yes' } else { 'no' })"
Write-Output "desktop_control_implemented: no"
Write-Output "available_now:"
Write-Output "- PowerShell environment check"
Write-Output "- Local process visibility"
Write-Output "- Harmless shell command execution"
if (-not $StatusOnly) {
    Write-Output "- Harmless local launcher test"
}
Write-Output "missing_now:"
Write-Output "- App switching"
Write-Output "- Click and type control"
Write-Output "- Copy paste orchestration"
Write-Output "- Human approval wait loop"
Write-Output "- Observation loop and audit log"

Write-Host ''
if ($failed -eq 0) {
    Write-Host 'Summary: desktop playground checks passed.'
    exit 0
}

Write-Host ("Summary: {0} desktop playground check(s) failed." -f $failed)
exit 1
