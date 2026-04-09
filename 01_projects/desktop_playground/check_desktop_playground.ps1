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
        [string]$ArtifactPath = '',
        [string]$TextContent = '',
        [hashtable]$EnvOverrides = @{}
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

    if (-not [string]::IsNullOrWhiteSpace($TextContent)) {
        $arguments += @('-TextContent', $TextContent)
    }

    $previousEnv = @{}
    foreach ($name in $EnvOverrides.Keys) {
        $envPath = "Env:$name"
        $hadValue = Test-Path $envPath
        $previousEnv[$name] = if ($hadValue) { (Get-Item $envPath).Value } else { $null }
        Set-Item -Path $envPath -Value ([string]$EnvOverrides[$name])
    }

    try {
        $output = & powershell.exe @arguments 2>&1 | Out-String
        return @{
            ExitCode = $LASTEXITCODE
            Output = ($output.Trim())
        }
    }
    finally {
        foreach ($name in $EnvOverrides.Keys) {
            $envPath = "Env:$name"
            if ($null -eq $previousEnv[$name]) {
                Remove-Item $envPath -ErrorAction SilentlyContinue
            }
            else {
                Set-Item -Path $envPath -Value $previousEnv[$name]
            }
        }
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
$clipboardSeed = 'desktop-playground-check'

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
$openAllowedAppOk = $StatusOnly
$duplicateTerminalAvoidanceOk = $StatusOnly
$focusWindowOk = $StatusOnly
$clipboardWriteOk = $StatusOnly
$clipboardReadOk = $StatusOnly
$pasteClipboardOk = $StatusOnly
$hotkeyOk = $StatusOnly
$copySelectionOk = $StatusOnly
$waitSecondsOk = $StatusOnly
$waitForWindowOk = $StatusOnly
$mouseMoveOk = $StatusOnly
$leftClickOk = $StatusOnly
$scrollMouseOk = $StatusOnly
$resourceGuardOk = $StatusOnly
$clipboardGuardOk = $StatusOnly
$failsafeOk = $StatusOnly
$screenshotOk = $StatusOnly
$unsupportedActionBlocked = $StatusOnly
$foregroundAccessAvailable = $StatusOnly
$terminalWindowCount = 0
$powerShellProcessCount = 0
$nodeProcessCount = 0
$pythonProcessCount = 0
$terminalWindowLimit = 0
$terminalProcessLimit = 0
$ollamaPresent = 'no'

if ($desktopActionScriptExists) {
    $listWindowsResult = Invoke-DesktopAction -Action 'list_windows'
    $listWindowsOk = $listWindowsResult.ExitCode -eq 0 -and `
        $listWindowsResult.Output -match 'status:\s+succeeded' -and `
        $listWindowsResult.Output -match 'headline:\s+Detected'
    Write-Check -Name 'Desktop action list_windows' -Passed $listWindowsOk -Detail $listWindowsResult.Output
    if (-not $listWindowsOk) { $failed++ }
    $terminalWindowMatch = [regex]::Match($listWindowsResult.Output, 'terminal_window_count:\s*(\d+)')
    $powerShellProcessMatch = [regex]::Match($listWindowsResult.Output, 'powershell_process_count:\s*(\d+)')
    $nodeProcessMatch = [regex]::Match($listWindowsResult.Output, 'node_process_count:\s*(\d+)')
    $pythonProcessMatch = [regex]::Match($listWindowsResult.Output, 'python_process_count:\s*(\d+)')
    $terminalWindowLimitMatch = [regex]::Match($listWindowsResult.Output, 'terminal_window_limit:\s*(\d+)')
    $terminalProcessLimitMatch = [regex]::Match($listWindowsResult.Output, 'terminal_process_limit:\s*(\d+)')
    $ollamaPresentMatch = [regex]::Match($listWindowsResult.Output, 'ollama_present:\s*(yes|no)')
    if ($terminalWindowMatch.Success) { $terminalWindowCount = [int]$terminalWindowMatch.Groups[1].Value }
    if ($powerShellProcessMatch.Success) { $powerShellProcessCount = [int]$powerShellProcessMatch.Groups[1].Value }
    if ($nodeProcessMatch.Success) { $nodeProcessCount = [int]$nodeProcessMatch.Groups[1].Value }
    if ($pythonProcessMatch.Success) { $pythonProcessCount = [int]$pythonProcessMatch.Groups[1].Value }
    if ($terminalWindowLimitMatch.Success) { $terminalWindowLimit = [int]$terminalWindowLimitMatch.Groups[1].Value }
    if ($terminalProcessLimitMatch.Success) { $terminalProcessLimit = [int]$terminalProcessLimitMatch.Groups[1].Value }
    if ($ollamaPresentMatch.Success) { $ollamaPresent = $ollamaPresentMatch.Groups[1].Value }

    $activeWindowResult = Invoke-DesktopAction -Action 'get_active_window'
    $activeWindowOk = $activeWindowResult.ExitCode -eq 0 -and `
        $activeWindowResult.Output -match 'status:\s+succeeded' -and `
        $activeWindowResult.Output -match 'active_window_alias:\s+\S+'
    $foregroundAccessAvailable = $activeWindowResult.Output -match 'foreground_access:\s+available'
    Write-Check -Name 'Desktop action get_active_window' -Passed $activeWindowOk -Detail $activeWindowResult.Output
    if (-not $activeWindowOk) { $failed++ }

    if (-not $StatusOnly) {
        $openAllowedAppResult = Invoke-DesktopAction -Action 'open_allowed_app' -Target 'terminal'
        $openAllowedAppOk = (
            $openAllowedAppResult.ExitCode -eq 0 -and `
            $openAllowedAppResult.Output -match 'status:\s+succeeded' -and `
            $openAllowedAppResult.Output -match 'reused_existing_window:\s+(yes|no)'
        ) -or (
            $openAllowedAppResult.ExitCode -eq 41 -and `
            $openAllowedAppResult.Output -match 'guard_state:\s+manual_focus_required'
        )
        Write-Check -Name 'Desktop action open_allowed_app' -Passed $openAllowedAppOk -Detail $openAllowedAppResult.Output
        if (-not $openAllowedAppOk) { $failed++ }

        $openAllowedAppAgain = Invoke-DesktopAction -Action 'open_allowed_app' -Target 'terminal'
        $duplicateTerminalAvoidanceOk = (
            $openAllowedAppAgain.ExitCode -eq 0 -and `
            $openAllowedAppAgain.Output -match 'status:\s+succeeded' -and `
            $openAllowedAppAgain.Output -match 'reused_existing_window:\s+yes'
        ) -or (
            $openAllowedAppAgain.ExitCode -eq 41 -and `
            $openAllowedAppAgain.Output -match 'guard_state:\s+manual_focus_required'
        )
        Write-Check -Name 'Focus-first duplicate terminal avoidance' -Passed $duplicateTerminalAvoidanceOk -Detail $openAllowedAppAgain.Output
        if (-not $duplicateTerminalAvoidanceOk) { $failed++ }

        $resourceGuardResult = Invoke-DesktopAction -Action 'open_allowed_app' -Target 'terminal' -EnvOverrides @{
            SUPER_AGENT_DESKTOP_TEST_TERMINAL_WINDOW_COUNT = '3'
            SUPER_AGENT_DESKTOP_TEST_TERMINAL_PROCESS_COUNT = '6'
            SUPER_AGENT_DESKTOP_TEST_FORCE_RESOURCE_GUARD = '1'
        }
        $resourceGuardOk = $resourceGuardResult.ExitCode -eq 41 -and `
            $resourceGuardResult.Output -match 'status:\s+blocked' -and `
            $resourceGuardResult.Output -match 'guard_state:\s+resource_guard_triggered' -and `
            $resourceGuardResult.Output -match 'terminal_window_count:\s+3' -and `
            $resourceGuardResult.Output -match 'powershell_process_count:\s+6'
        Write-Check -Name 'Desktop resource guard blocks duplicate terminal spawning' -Passed $resourceGuardOk -Detail $resourceGuardResult.Output
        if (-not $resourceGuardOk) { $failed++ }

        $focusWindowResult = Invoke-DesktopAction -Action 'focus_window' -Target 'terminal'
        $focusWindowOk = (
            $focusWindowResult.ExitCode -eq 0 -and `
            $focusWindowResult.Output -match 'status:\s+succeeded' -and `
            $focusWindowResult.Output -match 'focused_window_alias:\s+terminal'
        ) -or (
            $focusWindowResult.ExitCode -eq 41 -and `
            $focusWindowResult.Output -match 'guard_state:\s+manual_focus_required'
        )
        Write-Check -Name 'Desktop action focus_window' -Passed $focusWindowOk -Detail $focusWindowResult.Output
        if (-not $focusWindowOk) { $failed++ }

        $clipboardWriteResult = Invoke-DesktopAction -Action 'set_clipboard_text' -TextContent $clipboardSeed
        $clipboardWriteOk = $clipboardWriteResult.ExitCode -eq 0 -and `
            $clipboardWriteResult.Output -match 'status:\s+succeeded' -and `
            $clipboardWriteResult.Output -match 'clipboard_preview:\s+desktop-playground-check'
        Write-Check -Name 'Desktop action set_clipboard_text' -Passed $clipboardWriteOk -Detail $clipboardWriteResult.Output
        if (-not $clipboardWriteOk) { $failed++ }

        $clipboardReadResult = Invoke-DesktopAction -Action 'get_clipboard_text'
        $clipboardReadOk = $clipboardReadResult.ExitCode -eq 0 -and `
            $clipboardReadResult.Output -match 'status:\s+succeeded' -and `
            $clipboardReadResult.Output -match 'clipboard_preview:\s+desktop-playground-check'
        Write-Check -Name 'Desktop action get_clipboard_text' -Passed $clipboardReadOk -Detail $clipboardReadResult.Output
        if (-not $clipboardReadOk) { $failed++ }

        $pasteClipboardResult = Invoke-DesktopAction -Action 'paste_clipboard' -Target 'terminal'
        $pasteClipboardOk = (
            $pasteClipboardResult.ExitCode -eq 0 -and `
            $pasteClipboardResult.Output -match 'status:\s+succeeded' -and `
            $pasteClipboardResult.Output -match 'clipboard_preview:\s+desktop-playground-check'
        ) -or (
            $pasteClipboardResult.ExitCode -eq 41 -and `
            $pasteClipboardResult.Output -match 'guard_state:\s+manual_focus_required'
        )
        Write-Check -Name 'Desktop action paste_clipboard' -Passed $pasteClipboardOk -Detail $pasteClipboardResult.Output
        if (-not $pasteClipboardOk) { $failed++ }

        $clipboardGuardSeed = Invoke-DesktopAction -Action 'set_clipboard_text' -TextContent 'Run Desktop Bridge Check'
        $clipboardGuardSeedOk = $clipboardGuardSeed.ExitCode -eq 0
        $clipboardGuardResult = Invoke-DesktopAction -Action 'paste_clipboard' -Target 'terminal'
        $clipboardGuardOk = $clipboardGuardSeedOk -and `
            $clipboardGuardResult.ExitCode -eq 41 -and `
            $clipboardGuardResult.Output -match 'status:\s+blocked' -and `
            $clipboardGuardResult.Output -match 'guard_state:\s+clipboard_guard_triggered'
        Write-Check -Name 'Clipboard guard blocks checker text from terminal paste' -Passed $clipboardGuardOk -Detail $clipboardGuardResult.Output
        if (-not $clipboardGuardOk) { $failed++ }

        $safeClipboardReset = Invoke-DesktopAction -Action 'set_clipboard_text' -TextContent $clipboardSeed
        $safeClipboardResetOk = $safeClipboardReset.ExitCode -eq 0

        $hotkeyResult = Invoke-DesktopAction -Action 'send_hotkey' -Target 'terminal|ctrl+v'
        $hotkeyOk = $safeClipboardResetOk -and ((
            $hotkeyResult.ExitCode -eq 0 -and `
            $hotkeyResult.Output -match 'status:\s+succeeded' -and `
            $hotkeyResult.Output -match 'sent_hotkey:\s+ctrl\+v'
        ) -or (
            $hotkeyResult.ExitCode -eq 41 -and `
            $hotkeyResult.Output -match 'guard_state:\s+manual_focus_required'
        ))
        Write-Check -Name 'Desktop action send_hotkey' -Passed $hotkeyOk -Detail $hotkeyResult.Output
        if (-not $hotkeyOk) { $failed++ }

        $copySelectionResult = Invoke-DesktopAction -Action 'copy_selection' -Target 'terminal'
        $copySelectionOk = (
            $copySelectionResult.ExitCode -eq 0 -and `
            $copySelectionResult.Output -match 'status:\s+succeeded' -and `
            $copySelectionResult.Output -match 'clipboard_preview:\s+\S+'
        ) -or (
            $copySelectionResult.ExitCode -eq 41 -and `
            $copySelectionResult.Output -match 'guard_state:\s+manual_focus_required'
        )
        Write-Check -Name 'Desktop action copy_selection' -Passed $copySelectionOk -Detail $copySelectionResult.Output
        if (-not $copySelectionOk) { $failed++ }

        $waitSecondsResult = Invoke-DesktopAction -Action 'wait_seconds' -Target '1'
        $waitSecondsOk = $waitSecondsResult.ExitCode -eq 0 -and `
            $waitSecondsResult.Output -match 'status:\s+succeeded' -and `
            $waitSecondsResult.Output -match 'waited_seconds:\s+1'
        Write-Check -Name 'Desktop action wait_seconds' -Passed $waitSecondsOk -Detail $waitSecondsResult.Output
        if (-not $waitSecondsOk) { $failed++ }

        $waitForWindowResult = Invoke-DesktopAction -Action 'wait_for_window' -Target 'terminal|2'
        $waitForWindowOk = $waitForWindowResult.ExitCode -eq 0 -and `
            $waitForWindowResult.Output -match 'status:\s+succeeded' -and `
            $waitForWindowResult.Output -match 'wait_window_alias:\s+terminal'
        Write-Check -Name 'Desktop action wait_for_window' -Passed $waitForWindowOk -Detail $waitForWindowResult.Output
        if (-not $waitForWindowOk) { $failed++ }

        $mouseMoveResult = Invoke-DesktopAction -Action 'move_mouse' -Target 'terminal|center'
        $mouseMoveOk = (
            $mouseMoveResult.ExitCode -eq 0 -and `
            $mouseMoveResult.Output -match 'status:\s+succeeded' -and `
            $mouseMoveResult.Output -match 'coordinates:\s+\d+,\d+'
        ) -or (
            $mouseMoveResult.ExitCode -eq 41 -and `
            $mouseMoveResult.Output -match 'guard_state:\s+manual_focus_required'
        )
        Write-Check -Name 'Desktop action move_mouse' -Passed $mouseMoveOk -Detail $mouseMoveResult.Output
        if (-not $mouseMoveOk) { $failed++ }

        $leftClickResult = Invoke-DesktopAction -Action 'left_click' -Target 'terminal|center'
        $leftClickOk = (
            $leftClickResult.ExitCode -eq 0 -and `
            $leftClickResult.Output -match 'status:\s+succeeded' -and `
            $leftClickResult.Output -match 'coordinates:\s+\d+,\d+'
        ) -or (
            $leftClickResult.ExitCode -eq 41 -and `
            $leftClickResult.Output -match 'guard_state:\s+manual_focus_required'
        )
        Write-Check -Name 'Desktop action left_click' -Passed $leftClickOk -Detail $leftClickResult.Output
        if (-not $leftClickOk) { $failed++ }

        $scrollMouseResult = Invoke-DesktopAction -Action 'scroll_mouse' -Target 'terminal|240'
        $scrollMouseOk = (
            $scrollMouseResult.ExitCode -eq 0 -and `
            $scrollMouseResult.Output -match 'status:\s+succeeded' -and `
            $scrollMouseResult.Output -match 'scroll_delta:\s+240'
        ) -or (
            $scrollMouseResult.ExitCode -eq 41 -and `
            $scrollMouseResult.Output -match 'guard_state:\s+manual_focus_required'
        )
        Write-Check -Name 'Desktop action scroll_mouse' -Passed $scrollMouseOk -Detail $scrollMouseResult.Output
        if (-not $scrollMouseOk) { $failed++ }

        $failsafeResult = Invoke-DesktopAction -Action 'wait_seconds' -Target '5' -EnvOverrides @{ SUPER_AGENT_DESKTOP_TEST_INTERRUPT_AFTER_MS = '300' }
        $failsafeOk = $failsafeResult.ExitCode -eq 130 -and `
            $failsafeResult.Output -match 'status:\s+interrupted' -and `
            $failsafeResult.Output -match 'interruption_reason:\s+Emergency stop requested with Ctrl\+8'
        Write-Check -Name 'Desktop Ctrl+8 failsafe path' -Passed $failsafeOk -Detail $failsafeResult.Output
        if (-not $failsafeOk) { $failed++ }

        Remove-GeneratedFile -Path $screenshotPath
        $screenshotResult = Invoke-DesktopAction -Action 'capture_desktop_screenshot' -ArtifactPath $screenshotPath
        $screenshotOk = (
            $screenshotResult.ExitCode -eq 0 -and `
            $screenshotResult.Output -match 'status:\s+succeeded' -and `
            (Test-Path -LiteralPath $screenshotPath -PathType Leaf)
        ) -or (
            $screenshotResult.ExitCode -eq 41 -and `
            $screenshotResult.Output -match 'guard_state:\s+desktop_capture_unavailable'
        )
        Write-Check -Name 'Desktop action capture_desktop_screenshot' -Passed $screenshotOk -Detail $screenshotResult.Output
        if (-not $screenshotOk) { $failed++ }

        $unsupportedResult = Invoke-DesktopAction -Action 'send_hotkey' -Target 'terminal|ctrl+shift+x'
        $unsupportedActionBlocked = $unsupportedResult.ExitCode -ne 0 -and `
            $unsupportedResult.Output -match 'failure_reason:\s+Unsupported hotkey target'
        Write-Check -Name 'Unsupported desktop target fails safely' -Passed $unsupportedActionBlocked -Detail $unsupportedResult.Output
        if (-not $unsupportedActionBlocked) { $failed++ }
    }
}

$headline = if ($failed -eq 0) {
    if ($StatusOnly) {
        'Desktop bridge status is available for safe local operator checks.'
    }
    else {
        'Desktop bridge checks passed for the current local operator environment.'
    }
}
else {
    'Desktop bridge checks found one or more failures.'
}

Write-Output "mode: $mode"
Write-Output "headline: $headline"
Write-Output "powershell_available: yes"
Write-Output "powershell_version: $powerShellVersion"
Write-Output "explorer_available: $(if ($explorerAvailable) { 'yes' } else { 'no' })"
Write-Output "process_visibility: $(if ($processVisibility) { 'yes' } else { 'no' })"
Write-Output "shell_command_capability: $(if ($shellCommandCapability) { 'yes' } else { 'no' })"
Write-Output "launcher_capability: $(if ($StatusOnly) { 'not_run' } elseif ($launcherCapability) { 'yes' } else { 'no' })"
Write-Output "failsafe_hotkey: Ctrl+8"
Write-Output "desktop_control_implemented: no"
Write-Output "terminal_window_count: $terminalWindowCount"
Write-Output "powershell_process_count: $powerShellProcessCount"
Write-Output "node_process_count: $nodeProcessCount"
Write-Output "python_process_count: $pythonProcessCount"
Write-Output "ollama_present: $ollamaPresent"
Write-Output "terminal_window_limit: $terminalWindowLimit"
Write-Output "terminal_process_limit: $terminalProcessLimit"
Write-Output "list_windows_ok: $(if ($listWindowsOk) { 'yes' } else { 'no' })"
Write-Output "active_window_ok: $(if ($activeWindowOk) { 'yes' } else { 'no' })"
Write-Output "open_allowed_app_ok: $(if ($openAllowedAppOk) { 'yes' } else { 'no' })"
Write-Output "duplicate_terminal_avoidance_ok: $(if ($duplicateTerminalAvoidanceOk) { 'yes' } else { 'no' })"
Write-Output "focus_window_ok: $(if ($focusWindowOk) { 'yes' } else { 'no' })"
Write-Output "clipboard_write_ok: $(if ($clipboardWriteOk) { 'yes' } else { 'no' })"
Write-Output "clipboard_read_ok: $(if ($clipboardReadOk) { 'yes' } else { 'no' })"
Write-Output "paste_clipboard_ok: $(if ($pasteClipboardOk) { 'yes' } else { 'no' })"
Write-Output "send_hotkey_ok: $(if ($hotkeyOk) { 'yes' } else { 'no' })"
Write-Output "copy_selection_ok: $(if ($copySelectionOk) { 'yes' } else { 'no' })"
Write-Output "wait_seconds_ok: $(if ($waitSecondsOk) { 'yes' } else { 'no' })"
Write-Output "wait_for_window_ok: $(if ($waitForWindowOk) { 'yes' } else { 'no' })"
Write-Output "move_mouse_ok: $(if ($mouseMoveOk) { 'yes' } else { 'no' })"
Write-Output "left_click_ok: $(if ($leftClickOk) { 'yes' } else { 'no' })"
Write-Output "scroll_mouse_ok: $(if ($scrollMouseOk) { 'yes' } else { 'no' })"
Write-Output "resource_guard_ok: $(if ($resourceGuardOk) { 'yes' } else { 'no' })"
Write-Output "clipboard_guard_ok: $(if ($clipboardGuardOk) { 'yes' } else { 'no' })"
Write-Output "failsafe_interrupt_ok: $(if ($failsafeOk) { 'yes' } else { 'no' })"
Write-Output "capture_desktop_screenshot_ok: $(if ($screenshotOk) { 'yes' } else { 'no' })"
Write-Output "unsupported_action_blocked: $(if ($unsupportedActionBlocked) { 'yes' } else { 'no' })"
Write-Output "allowlisted_actions:"
Write-Output "- list_windows"
Write-Output "- get_active_window"
Write-Output "- focus_window"
Write-Output "- open_allowed_app"
Write-Output "- capture_desktop_screenshot"
Write-Output "- get_clipboard_text"
Write-Output "- set_clipboard_text"
Write-Output "- copy_selection"
Write-Output "- paste_clipboard"
Write-Output "- send_hotkey"
Write-Output "- wait_seconds"
Write-Output "- wait_for_window"
Write-Output "- move_mouse"
Write-Output "- left_click"
Write-Output "- double_click"
Write-Output "- right_click"
Write-Output "- scroll_mouse"
Write-Output "available_now:"
Write-Output "- Allowlisted window discovery"
Write-Output "- Foreground window detection"
Write-Output "- Focus existing allowlisted windows before opening duplicates"
Write-Output "- Open allowlisted local apps when no reusable window exists"
Write-Output "- Clipboard read, set, copy, and paste actions"
Write-Output "- Narrow allowlisted hotkeys"
Write-Output "- Explicit waits and window waits"
Write-Output "- Narrow mouse move, click, and scroll actions"
Write-Output "- Repo-local desktop screenshot artifacts"
Write-Output "- Ctrl+8 emergency stop during desktop macro execution"
Write-Output "missing_now:"
Write-Output "- Arbitrary desktop or app control"
Write-Output "- Freeform typing into arbitrary contexts"
Write-Output "- Unrestricted mouse roaming or drag automation"
Write-Output "- Background daemon behavior"
Write-Output "- Remote notifications or remote control"

Remove-GeneratedFile -Path $screenshotPath

Write-Host ''
if ($failed -eq 0) {
    Write-Host 'Summary: desktop playground checks passed.'
    exit 0
}

Write-Host ("Summary: {0} desktop playground check(s) failed." -f $failed)
exit 1
