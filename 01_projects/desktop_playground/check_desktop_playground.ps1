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

function Invoke-DesktopAction {
    param(
        [string]$Action,
        [string]$Target = '',
        [string]$ArtifactPath = ''
    )

    $arguments = @(
        '-ExecutionPolicy', 'Bypass',
        '-File', $desktopActionScript,
        '-Action', $Action,
        '-AllowedRoot', $allowedRoot
    )

    if (-not [string]::IsNullOrWhiteSpace($Target)) {
        $arguments += @('-Target', $Target)
    }

    if (-not [string]::IsNullOrWhiteSpace($ArtifactPath)) {
        $arguments += @('-ArtifactPath', $ArtifactPath)
    }

    $output = & powershell.exe @arguments 2>&1 | Out-String
    return @{
        ExitCode = $LASTEXITCODE
        Output = ($output.Trim())
    }
}

function Remove-GeneratedFile {
    param(
        [string]$Path
    )

    if (Test-Path -LiteralPath $Path -PathType Leaf) {
        Remove-Item -LiteralPath $Path -Force -ErrorAction SilentlyContinue
    }
}

$repoRoot = Split-Path -Parent (Split-Path -Parent $PSScriptRoot)
$allowedRoot = $repoRoot
$desktopActionScript = Join-Path $PSScriptRoot 'desktop_bridge_actions.ps1'
$screenshotPath = Join-Path $repoRoot '05_logs\tmp\desktop\desktop-playground-check.png'
$failed = 0
$mode = if ($StatusOnly) { 'status' } else { 'check' }

$powerShellVersion = $PSVersionTable.PSVersion.ToString()
$powerShellAvailable = $true
Write-Check -Name 'PowerShell environment' -Passed $powerShellAvailable -Detail $powerShellVersion

$desktopActionScriptExists = Test-Path -LiteralPath $desktopActionScript -PathType Leaf
Write-Check -Name 'Desktop action script exists' -Passed $desktopActionScriptExists -Detail ($(if ($desktopActionScriptExists) { $desktopActionScript } else { 'desktop bridge action script not found' }))
if (-not $desktopActionScriptExists) { $failed++ }

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

$listWindowsOk = $false
$activeWindowOk = $false
$focusWindowOk = $StatusOnly
$openAllowedAppOk = $StatusOnly
$screenshotOk = $StatusOnly
$unsupportedActionBlocked = $StatusOnly
$listWindowsDetail = 'not run'
$activeWindowDetail = 'not run'
$focusWindowDetail = if ($StatusOnly) { 'status-only mode skipped live focus test' } else { 'not run' }
$openAllowedAppDetail = if ($StatusOnly) { 'status-only mode skipped live app launch test' } else { 'not run' }
$screenshotDetail = if ($StatusOnly) { 'status-only mode skipped live screenshot test' } else { 'not run' }
$unsupportedDetail = if ($StatusOnly) { 'status-only mode skipped unsupported-target test' } else { 'not run' }

if ($desktopActionScriptExists) {
    $listWindowsResult = Invoke-DesktopAction -Action 'list_windows'
    $listWindowsOk = $listWindowsResult.ExitCode -eq 0 -and `
        $listWindowsResult.Output -match 'status:\s+succeeded' -and `
        $listWindowsResult.Output -match 'headline:\s+Detected'
    $listWindowsDetail = $listWindowsResult.Output
    Write-Check -Name 'Desktop action list_windows' -Passed $listWindowsOk -Detail $listWindowsDetail
    if (-not $listWindowsOk) { $failed++ }

    $activeWindowResult = Invoke-DesktopAction -Action 'get_active_window'
    $activeWindowOk = $activeWindowResult.ExitCode -eq 0 -and `
        $activeWindowResult.Output -match 'status:\s+succeeded' -and `
        $activeWindowResult.Output -match 'active_window_alias:\s+\S+'
    $activeWindowDetail = $activeWindowResult.Output
    Write-Check -Name 'Desktop action get_active_window' -Passed $activeWindowOk -Detail $activeWindowDetail
    if (-not $activeWindowOk) { $failed++ }

    if (-not $StatusOnly) {
        $openAllowedAppResult = Invoke-DesktopAction -Action 'open_allowed_app' -Target 'terminal'
        $openAllowedAppOk = $openAllowedAppResult.ExitCode -eq 0 -and `
            $openAllowedAppResult.Output -match 'status:\s+succeeded' -and `
            $openAllowedAppResult.Output -match 'command_path:\s+'
        $openAllowedAppDetail = $openAllowedAppResult.Output
        Write-Check -Name 'Desktop action open_allowed_app' -Passed $openAllowedAppOk -Detail $openAllowedAppDetail
        if (-not $openAllowedAppOk) { $failed++ }

        Start-Sleep -Milliseconds 1200

        $focusWindowResult = Invoke-DesktopAction -Action 'focus_window' -Target 'terminal'
        $focusWindowOk = $focusWindowResult.ExitCode -eq 0 -and `
            $focusWindowResult.Output -match 'status:\s+succeeded' -and `
            $focusWindowResult.Output -match 'focused_window_title:\s+'
        $focusWindowDetail = $focusWindowResult.Output
        Write-Check -Name 'Desktop action focus_window' -Passed $focusWindowOk -Detail $focusWindowDetail
        if (-not $focusWindowOk) { $failed++ }

        Remove-GeneratedFile -Path $screenshotPath
        $screenshotResult = Invoke-DesktopAction -Action 'capture_desktop_screenshot' -ArtifactPath $screenshotPath
        $screenshotOk = $screenshotResult.ExitCode -eq 0 -and `
            $screenshotResult.Output -match 'status:\s+succeeded' -and `
            (Test-Path -LiteralPath $screenshotPath -PathType Leaf)
        $screenshotDetail = $screenshotResult.Output
        Write-Check -Name 'Desktop action capture_desktop_screenshot' -Passed $screenshotOk -Detail $screenshotDetail
        if (-not $screenshotOk) { $failed++ }

        $unsupportedResult = Invoke-DesktopAction -Action 'focus_window' -Target 'not_allowed'
        $unsupportedActionBlocked = $unsupportedResult.ExitCode -ne 0 -and `
            $unsupportedResult.Output -match 'failure_reason:\s+Unsupported focus target'
        $unsupportedDetail = $unsupportedResult.Output
        Write-Check -Name 'Unsupported desktop target fails safely' -Passed $unsupportedActionBlocked -Detail $unsupportedDetail
        if (-not $unsupportedActionBlocked) { $failed++ }
    }
}

$headline = if ($failed -eq 0) {
    if ($StatusOnly) {
        'Desktop bridge status is available for safe local operator checks.'
    }
    else {
        'Desktop bridge action checks passed for the current local operator environment.'
    }
}
else {
    'Desktop bridge action checks found one or more failures.'
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
Write-Output "list_windows_ok: $(if ($listWindowsOk) { 'yes' } else { 'no' })"
Write-Output "active_window_ok: $(if ($activeWindowOk) { 'yes' } else { 'no' })"
Write-Output "focus_window_ok: $(if ($focusWindowOk) { 'yes' } else { 'no' })"
Write-Output "open_allowed_app_ok: $(if ($openAllowedAppOk) { 'yes' } else { 'no' })"
Write-Output "capture_desktop_screenshot_ok: $(if ($screenshotOk) { 'yes' } else { 'no' })"
Write-Output "unsupported_action_blocked: $(if ($unsupportedActionBlocked) { 'yes' } else { 'no' })"
Write-Output "allowlisted_actions:"
Write-Output "- list_windows"
Write-Output "- get_active_window"
Write-Output "- focus_window"
Write-Output "- open_allowed_app"
Write-Output "- capture_desktop_screenshot"
Write-Output "available_now:"
Write-Output "- Allowlisted window discovery"
Write-Output "- Foreground window detection"
Write-Output "- Focus allowlisted windows with approval"
Write-Output "- Open allowlisted local apps with approval"
Write-Output "- Capture repo-local desktop screenshot artifacts with approval"
Write-Output "missing_now:"
Write-Output "- Arbitrary desktop or app control"
Write-Output "- General click and type automation"
Write-Output "- Copy paste orchestration"
Write-Output "- Observation loop and audit log"
Write-Output "- Background daemon behavior"

Remove-GeneratedFile -Path $screenshotPath

Write-Host ''
if ($failed -eq 0) {
    Write-Host 'Summary: desktop playground checks passed.'
    exit 0
}

Write-Host ("Summary: {0} desktop playground check(s) failed." -f $failed)
exit 1
