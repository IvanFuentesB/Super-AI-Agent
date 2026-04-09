[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet(
        'list_windows',
        'get_active_window',
        'focus_window',
        'open_allowed_app',
        'capture_desktop_screenshot',
        'get_clipboard_text',
        'set_clipboard_text',
        'copy_selection',
        'paste_clipboard',
        'send_hotkey',
        'wait_seconds',
        'wait_for_window',
        'move_mouse',
        'left_click',
        'double_click',
        'right_click',
        'scroll_mouse'
    )]
    [string]$Action,

    [string]$Target = '',

    [string]$ArtifactPath = '',

    [string]$TextContent = '',

    [string]$AllowedRoot = 'C:\Users\ai_sandbox\Documents\AI_Managed_Only'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$signature = @'
using System;
using System.Runtime.InteropServices;
using System.Text;

[StructLayout(LayoutKind.Sequential)]
public struct RECT
{
    public int Left;
    public int Top;
    public int Right;
    public int Bottom;
}

public static class DesktopBridgeNative
{
    [DllImport("user32.dll")]
    public static extern IntPtr GetForegroundWindow();

    [DllImport("user32.dll")]
    public static extern bool SetForegroundWindow(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern bool BringWindowToTop(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern bool ShowWindowAsync(IntPtr hWnd, int nCmdShow);

    [DllImport("user32.dll")]
    public static extern short GetAsyncKeyState(int vKey);

    [DllImport("user32.dll")]
    public static extern bool SetCursorPos(int X, int Y);

    [DllImport("user32.dll")]
    public static extern bool GetWindowRect(IntPtr hWnd, out RECT lpRect);

    [DllImport("user32.dll", CharSet = CharSet.Unicode)]
    public static extern int GetWindowText(IntPtr hWnd, StringBuilder text, int count);

    [DllImport("user32.dll")]
    public static extern int GetWindowTextLength(IntPtr hWnd);

    [DllImport("user32.dll")]
    public static extern uint GetWindowThreadProcessId(IntPtr hWnd, out uint processId);

    [DllImport("user32.dll")]
    public static extern void mouse_event(uint dwFlags, uint dx, uint dy, uint dwData, UIntPtr dwExtraInfo);
}
'@

if (-not ('DesktopBridgeNative' -as [type])) {
    Add-Type -TypeDefinition $signature
}

$allowedWindowTargets = [ordered]@{
    cursor = @('Cursor')
    vscode = @('Visual Studio Code')
    terminal = @('Windows Terminal', 'PowerShell', 'Command Prompt')
    dashboard_browser = @('Super-AI-Agent Operator Console', '127.0.0.1:3210')
}

$allowedAppSpecs = [ordered]@{
    cursor = @{
        Commands = @('cursor.cmd', 'cursor')
        Fallbacks = @(
            'C:\Users\ai_sandbox\AppData\Local\Programs\cursor\resources\app\bin\cursor.cmd',
            'C:\Users\Navif\AppData\Local\Programs\cursor\resources\app\bin\cursor.cmd'
        )
        Arguments = @()
    }
    vscode = @{
        Commands = @('code.cmd', 'code')
        Fallbacks = @(
            'C:\Users\ai_sandbox\AppData\Local\Programs\Microsoft VS Code\bin\code.cmd'
        )
        Arguments = @()
    }
    terminal = @{
        Commands = @('wt.exe', 'wt', 'powershell.exe')
        Fallbacks = @(
            'C:\Users\ai_sandbox\AppData\Local\Microsoft\WindowsApps\wt.exe',
            'C:\Windows\System32\WindowsPowerShell\v1.0\powershell.exe'
        )
        Arguments = @()
    }
    dashboard_browser = @{
        Commands = @('chrome.exe', 'msedge.exe')
        Fallbacks = @(
            'C:\Program Files\Google\Chrome\Application\chrome.exe',
            'C:\Program Files (x86)\Microsoft\Edge\Application\msedge.exe'
        )
        Arguments = @('http://127.0.0.1:3210')
    }
}

$allowedHotkeys = [ordered]@{
    'ctrl+c' = '^c'
    'ctrl+v' = '^v'
    'ctrl+l' = '^l'
    'enter' = '{ENTER}'
    'escape' = '{ESC}'
}

$mouseEventFlags = @{
    LEFTDOWN = 0x0002
    LEFTUP = 0x0004
    RIGHTDOWN = 0x0008
    RIGHTUP = 0x0010
    WHEEL = 0x0800
}

$testInterruptAfterMs = 0
if ($env:SUPER_AGENT_DESKTOP_TEST_INTERRUPT_AFTER_MS -match '^\d+$') {
    $testInterruptAfterMs = [int]$env:SUPER_AGENT_DESKTOP_TEST_INTERRUPT_AFTER_MS
}
$interruptStopwatch = [System.Diagnostics.Stopwatch]::StartNew()
$forcedFailureActions = @()
if (-not [string]::IsNullOrWhiteSpace($env:SUPER_AGENT_DESKTOP_TEST_FAIL_ACTIONS)) {
    $forcedFailureActions = @(
        $env:SUPER_AGENT_DESKTOP_TEST_FAIL_ACTIONS.Split(',') |
            ForEach-Object { $_.Trim().ToLowerInvariant() } |
            Where-Object { -not [string]::IsNullOrWhiteSpace($_) }
    )
}
$resourceGuardThresholds = [ordered]@{
    TerminalWindowLimit = 3
    TerminalProcessLimit = 6
    NodeProcessLimit = 10
    PythonProcessLimit = 10
}

function Write-Field {
    param(
        [string]$Name,
        [string]$Value
    )

    Write-Output ("{0}: {1}" -f $Name, $Value)
}

function Short-Preview {
    param(
        [string]$Text,
        [int]$Limit = 120
    )

    $normalized = (([string]$Text) -replace '\s+', ' ').Trim()
    if ([string]::IsNullOrWhiteSpace($normalized)) {
        return 'empty'
    }

    if ($normalized.Length -le $Limit) {
        return $normalized
    }

    return ($normalized.Substring(0, $Limit - 3).TrimEnd() + '...')
}

function Get-EnvOverrideInt {
    param(
        [string]$Name,
        [int]$DefaultValue
    )

    $raw = [Environment]::GetEnvironmentVariable($Name)
    if ([string]::IsNullOrWhiteSpace($raw)) {
        return $DefaultValue
    }

    $value = 0
    if ([int]::TryParse($raw, [ref]$value)) {
        return $value
    }

    return $DefaultValue
}

function Get-ProcessCountSafe {
    param(
        [string[]]$Names
    )

    try {
        return @(
            Get-Process -ErrorAction SilentlyContinue |
                Where-Object { $Names -contains $_.ProcessName.ToLowerInvariant() }
        ).Count
    }
    catch {
        return 0
    }
}

function Get-ResourceGuardSnapshot {
    $terminalWindowCount = @(Get-AllowedWindows | Where-Object { $_.Aliases -contains 'terminal' }).Count
    $powerShellProcessCount = Get-ProcessCountSafe -Names @('powershell', 'pwsh')
    $nodeProcessCount = Get-ProcessCountSafe -Names @('node', 'npm')
    $pythonProcessCount = Get-ProcessCountSafe -Names @('python', 'pythonw')
    $ollamaPresent = (Get-ProcessCountSafe -Names @('ollama')) -gt 0

    $terminalWindowCount = Get-EnvOverrideInt -Name 'SUPER_AGENT_DESKTOP_TEST_TERMINAL_WINDOW_COUNT' -DefaultValue $terminalWindowCount
    $powerShellProcessCount = Get-EnvOverrideInt -Name 'SUPER_AGENT_DESKTOP_TEST_TERMINAL_PROCESS_COUNT' -DefaultValue $powerShellProcessCount
    $nodeProcessCount = Get-EnvOverrideInt -Name 'SUPER_AGENT_DESKTOP_TEST_NODE_PROCESS_COUNT' -DefaultValue $nodeProcessCount
    $pythonProcessCount = Get-EnvOverrideInt -Name 'SUPER_AGENT_DESKTOP_TEST_PYTHON_PROCESS_COUNT' -DefaultValue $pythonProcessCount

    return [pscustomobject]@{
        TerminalWindowCount = $terminalWindowCount
        PowerShellProcessCount = $powerShellProcessCount
        NodeProcessCount = $nodeProcessCount
        PythonProcessCount = $pythonProcessCount
        OllamaPresent = $ollamaPresent
    }
}

function Write-ResourceGuardSnapshot {
    param(
        [pscustomobject]$Snapshot
    )

    Write-Field 'terminal_window_count' "$($Snapshot.TerminalWindowCount)"
    Write-Field 'powershell_process_count' "$($Snapshot.PowerShellProcessCount)"
    Write-Field 'node_process_count' "$($Snapshot.NodeProcessCount)"
    Write-Field 'python_process_count' "$($Snapshot.PythonProcessCount)"
    Write-Field 'ollama_present' $(if ($Snapshot.OllamaPresent) { 'yes' } else { 'no' })
    Write-Field 'terminal_window_limit' "$($resourceGuardThresholds.TerminalWindowLimit)"
    Write-Field 'terminal_process_limit' "$($resourceGuardThresholds.TerminalProcessLimit)"
}

function Assert-NotForcedFailure {
    param(
        [string]$ActionName
    )

    if ($forcedFailureActions -contains $ActionName.Trim().ToLowerInvariant()) {
        throw "Forced desktop action failure for testing: $ActionName"
    }
}

function Stop-BlockedAction {
    param(
        [string]$Reason,
        [string]$GuardState = 'blocked',
        [string]$TargetValue = ''
    )

    $snapshot = Get-ResourceGuardSnapshot
    $effectiveTarget = 'none'
    if (-not [string]::IsNullOrWhiteSpace($TargetValue)) {
        $effectiveTarget = $TargetValue
    }
    elseif (-not [string]::IsNullOrWhiteSpace($Target)) {
        $effectiveTarget = $Target
    }
    Write-Field 'action_type' $Action
    Write-Field 'status' 'blocked'
    Write-Field 'target' $effectiveTarget
    Write-Field 'guard_state' $GuardState
    Write-Field 'failure_reason' $Reason
    Write-Field 'headline' $Reason
    Write-ResourceGuardSnapshot -Snapshot $snapshot
    exit 41
}

function Test-SuspiciousTerminalClipboardText {
    param(
        [string]$ClipboardText
    )

    $normalized = (([string]$ClipboardText) -replace '\s+', ' ').Trim()
    if ([string]::IsNullOrWhiteSpace($normalized)) {
        return $false
    }

    return $normalized -match '(?i)(^run desktop bridge check$|^refresh console status$|^refresh github summary$|^focus or reuse terminal$|^copy from focused window$|^paste into target window$|check_runtime_mvp\.ps1|check_dashboard_mvp\.ps1|check_desktop_playground\.ps1|write-check -name|\[(pass|fail)\])'
}

function Resolve-SafePath {
    param(
        [string]$PathValue
    )

    if ([string]::IsNullOrWhiteSpace($PathValue)) {
        return ''
    }

    $candidate = $PathValue
    if (-not [System.IO.Path]::IsPathRooted($candidate)) {
        $candidate = Join-Path $AllowedRoot $candidate
    }

    return [System.IO.Path]::GetFullPath($candidate)
}

function Test-InAllowedRoot {
    param(
        [string]$ResolvedPath
    )

    if ([string]::IsNullOrWhiteSpace($ResolvedPath)) {
        return $false
    }

    $allowed = [System.IO.Path]::GetFullPath($AllowedRoot).TrimEnd('\')
    $candidate = [System.IO.Path]::GetFullPath($ResolvedPath)
    return $candidate.StartsWith("$allowed\", [System.StringComparison]::OrdinalIgnoreCase) -or
        $candidate.Equals($allowed, [System.StringComparison]::OrdinalIgnoreCase)
}

function New-DefaultScreenshotPath {
    $directory = Join-Path $AllowedRoot '05_logs\tmp\desktop'
    $timestamp = Get-Date -Format 'yyyyMMdd-HHmmss'
    return Join-Path $directory ("desktop-capture-{0}.png" -f $timestamp)
}

function Resolve-AllowedApp {
    param(
        [string]$Alias
    )

    if (-not $allowedAppSpecs.Contains($Alias)) {
        throw "Unsupported allowed app target: $Alias"
    }

    $spec = $allowedAppSpecs[$Alias]
    foreach ($commandName in $spec.Commands) {
        $command = Get-Command $commandName -ErrorAction SilentlyContinue
        if ($null -ne $command) {
            return @{
                Alias = $Alias
                CommandPath = $command.Source
                Arguments = @($spec.Arguments)
            }
        }
    }

    foreach ($fallback in $spec.Fallbacks) {
        if (Test-Path -LiteralPath $fallback -PathType Leaf) {
            return @{
                Alias = $Alias
                CommandPath = $fallback
                Arguments = @($spec.Arguments)
            }
        }
    }

    throw "Allowed app target could not be resolved locally: $Alias"
}

function Test-EmergencyStopRequested {
    $ctrlDown = ([DesktopBridgeNative]::GetAsyncKeyState(0x11) -band 0x8000) -ne 0
    $eightDown = ([DesktopBridgeNative]::GetAsyncKeyState(0x38) -band 0x8000) -ne 0
    $numpadEightDown = ([DesktopBridgeNative]::GetAsyncKeyState(0x68) -band 0x8000) -ne 0

    if ($ctrlDown -and ($eightDown -or $numpadEightDown)) {
        return $true
    }

    if ($testInterruptAfterMs -gt 0 -and $interruptStopwatch.ElapsedMilliseconds -ge $testInterruptAfterMs) {
        return $true
    }

    return $false
}

function Assert-NotInterrupted {
    param(
        [string]$Phase = 'desktop action'
    )

    if (Test-EmergencyStopRequested) {
        throw [System.OperationCanceledException]::new("Emergency stop requested with Ctrl+8 during $Phase.")
    }
}

function Wait-WithInterrupt {
    param(
        [int]$Milliseconds,
        [string]$Phase = 'desktop action wait'
    )

    if ($Milliseconds -le 0) {
        Assert-NotInterrupted -Phase $Phase
        return
    }

    $remaining = $Milliseconds
    while ($remaining -gt 0) {
        Assert-NotInterrupted -Phase $Phase
        $chunk = [Math]::Min(100, $remaining)
        Start-Sleep -Milliseconds $chunk
        $remaining -= $chunk
    }

    Assert-NotInterrupted -Phase $Phase
}

function Get-AllowedWindows {
    $windows = @()
    foreach ($processItem in Get-Process | Where-Object { $_.MainWindowHandle -ne 0 -and -not [string]::IsNullOrWhiteSpace($_.MainWindowTitle) }) {
        $title = Get-WindowTitleByHandle -Handle ([System.IntPtr]$processItem.MainWindowHandle)
        if ([string]::IsNullOrWhiteSpace($title)) {
            $title = $processItem.MainWindowTitle.Trim()
        }
        $aliases = @()
        foreach ($entry in $allowedWindowTargets.GetEnumerator()) {
            foreach ($needle in $entry.Value) {
                if ($title.IndexOf($needle, [System.StringComparison]::OrdinalIgnoreCase) -ge 0) {
                    $aliases += $entry.Key
                    break
                }
            }
        }

        if ($aliases.Count -gt 0) {
            $windows += [pscustomobject]@{
                Handle = [System.IntPtr]$processItem.MainWindowHandle
                Title = $title
                Aliases = @($aliases)
                ProcessId = $processItem.Id
            }
        }
    }

    return @($windows)
}

function Get-WindowTitleByHandle {
    param(
        [System.IntPtr]$Handle
    )

    if ($Handle -eq [System.IntPtr]::Zero) {
        return ''
    }

    $length = [DesktopBridgeNative]::GetWindowTextLength($Handle)
    $bufferSize = [Math]::Max($length + 1, 256)
    $builder = New-Object System.Text.StringBuilder $bufferSize
    [void][DesktopBridgeNative]::GetWindowText($Handle, $builder, $builder.Capacity)
    return $builder.ToString().Trim()
}

function Get-AllowedAliasByTitle {
    param(
        [string]$Title
    )

    $normalizedTitle = ([string]$Title).Trim()
    if ([string]::IsNullOrWhiteSpace($normalizedTitle)) {
        return 'none'
    }

    foreach ($entry in $allowedWindowTargets.GetEnumerator()) {
        foreach ($needle in $entry.Value) {
            if ($normalizedTitle.IndexOf($needle, [System.StringComparison]::OrdinalIgnoreCase) -ge 0) {
                return $entry.Key
            }
        }
    }

    return 'unsupported'
}

function Get-WindowByAlias {
    param(
        [string]$Alias
    )

    $matches = @(Get-AllowedWindows | Where-Object { $_.Aliases -contains $Alias })
    if ($matches.Count -eq 0) {
        return $null
    }

    return $matches[0]
}

function Get-WindowRectangle {
    param(
        [System.IntPtr]$Handle
    )

    $rect = New-Object RECT
    if (-not [DesktopBridgeNative]::GetWindowRect($Handle, [ref]$rect)) {
        return $null
    }

    return [pscustomobject]@{
        Left = $rect.Left
        Top = $rect.Top
        Right = $rect.Right
        Bottom = $rect.Bottom
        Width = ($rect.Right - $rect.Left)
        Height = ($rect.Bottom - $rect.Top)
        CenterX = [int]([Math]::Round(($rect.Left + $rect.Right) / 2.0))
        CenterY = [int]([Math]::Round(($rect.Top + $rect.Bottom) / 2.0))
    }
}

function Get-ActiveWindowInfo {
    $handle = [DesktopBridgeNative]::GetForegroundWindow()
    if ($handle -eq [IntPtr]::Zero) {
        return [pscustomobject]@{
            Handle = [IntPtr]::Zero
            Title = ''
            Alias = 'none'
            ProcessId = 0
        }
    }

    $title = Get-WindowTitleByHandle -Handle $handle
    $alias = Get-AllowedAliasByTitle -Title $title
    $processId = [uint32]0
    [void][DesktopBridgeNative]::GetWindowThreadProcessId($handle, [ref]$processId)

    return [pscustomobject]@{
        Handle = $handle
        Title = $title
        Alias = $alias
        ProcessId = [int]$processId
    }
}

function Focus-AllowedWindowInternal {
    param(
        [string]$Alias
    )

    if (-not $allowedWindowTargets.Contains($Alias)) {
        throw "Unsupported focus target: $Alias"
    }

    $window = Get-WindowByAlias -Alias $Alias
    if ($null -eq $window) {
        throw "No visible allowlisted window found for target: $Alias"
    }

    Assert-NotInterrupted -Phase "focusing $Alias"

    $activeBefore = Get-ActiveWindowInfo
    if ($activeBefore.Handle -eq $window.Handle -or $activeBefore.Alias -eq $Alias -or $activeBefore.Title -eq $window.Title) {
        return [pscustomobject]@{
            Alias = $Alias
            Title = $window.Title
            Handle = $window.Handle
            ActiveAlias = $activeBefore.Alias
            ActiveTitle = $activeBefore.Title
        }
    }

    $shell = New-Object -ComObject WScript.Shell
    $activeWindow = $activeBefore
    $focusOk = $false

    foreach ($attempt in 1..4) {
        Assert-NotInterrupted -Phase "focusing $Alias (attempt $attempt)"

        if ($window.ProcessId -gt 0 -and $shell.AppActivate([int]$window.ProcessId)) {
            $focusOk = $true
        }

        if (-not $focusOk -and $shell.AppActivate($window.Title)) {
            $focusOk = $true
        }

        [void]$shell.SendKeys('%')
        Start-Sleep -Milliseconds 80
        [void][DesktopBridgeNative]::ShowWindowAsync($window.Handle, 9)
        [void][DesktopBridgeNative]::BringWindowToTop($window.Handle)
        if ([DesktopBridgeNative]::SetForegroundWindow($window.Handle)) {
            $focusOk = $true
        }

        if (-not $focusOk) {
            [void][DesktopBridgeNative]::ShowWindowAsync($window.Handle, 5)
            if ([DesktopBridgeNative]::SetForegroundWindow($window.Handle)) {
                $focusOk = $true
            }
            [void][DesktopBridgeNative]::BringWindowToTop($window.Handle)
        }

        Wait-WithInterrupt -Milliseconds 220 -Phase "verifying focus for $Alias"
        $activeWindow = Get-ActiveWindowInfo
        if ($activeWindow.Handle -eq $window.Handle -or $activeWindow.Alias -eq $Alias -or $activeWindow.Title -eq $window.Title) {
            $focusOk = $true
            break
        }
    }

    if (-not ($activeWindow.Handle -eq $window.Handle -or $activeWindow.Alias -eq $Alias -or $activeWindow.Title -eq $window.Title)) {
        throw "Windows did not move focus to the requested allowlisted window: $Alias"
    }

    return [pscustomobject]@{
        Alias = $Alias
        Title = $window.Title
        Handle = $window.Handle
        ActiveAlias = $activeWindow.Alias
        ActiveTitle = $activeWindow.Title
    }
}

function Wait-ForAllowedWindowInternal {
    param(
        [string]$Alias,
        [int]$TimeoutSeconds = 15
    )

    if (-not $allowedWindowTargets.Contains($Alias)) {
        throw "Unsupported allowed window target: $Alias"
    }

    $deadline = (Get-Date).AddSeconds($TimeoutSeconds)
    while ((Get-Date) -lt $deadline) {
        Assert-NotInterrupted -Phase "waiting for window $Alias"
        $window = Get-WindowByAlias -Alias $Alias
        if ($null -ne $window) {
            return $window
        }
        Start-Sleep -Milliseconds 250
    }

    throw "Timed out waiting for allowlisted window: $Alias"
}

function Get-ClipboardTextSafe {
    if ([System.Windows.Forms.Clipboard]::ContainsText()) {
        return [System.Windows.Forms.Clipboard]::GetText()
    }

    return ''
}

function Set-ClipboardTextSafe {
    param(
        [string]$Value
    )

    if ([string]::IsNullOrEmpty($Value)) {
        [System.Windows.Forms.Clipboard]::Clear()
        return
    }

    [System.Windows.Forms.Clipboard]::SetText($Value)
}

function Resolve-InputWindowContext {
    param(
        [string]$Alias = ''
    )

    if (-not [string]::IsNullOrWhiteSpace($Alias)) {
        return Focus-AllowedWindowInternal -Alias $Alias
    }

    $activeWindow = Get-ActiveWindowInfo
    if (-not $allowedWindowTargets.Contains($activeWindow.Alias)) {
        throw 'Desktop input actions require a focused allowlisted window or an explicit allowed target.'
    }

    return [pscustomobject]@{
        Alias = $activeWindow.Alias
        Title = $activeWindow.Title
        Handle = $activeWindow.Handle
        ActiveAlias = $activeWindow.Alias
        ActiveTitle = $activeWindow.Title
    }
}

function Focus-AllowedWindowOrBlock {
    param(
        [string]$Alias,
        [string]$ActionLabel = 'desktop action'
    )

    try {
        return Focus-AllowedWindowInternal -Alias $Alias
    }
    catch {
        $message = $_.Exception.Message
        if ($message -like 'Windows did not move focus to the requested allowlisted window:*') {
            $activeWindow = Get-ActiveWindowInfo
            $reason = if ($activeWindow.Handle -eq [System.IntPtr]::Zero) {
                "Foreground desktop access is unavailable in this session, so $ActionLabel requires manual operator focus for target: $Alias."
            }
            else {
                "Windows did not confirm focus for allowlisted target $Alias, so $ActionLabel requires manual operator focus."
            }
            Stop-BlockedAction -Reason $reason -GuardState 'manual_focus_required' -TargetValue $Alias
        }

        throw
    }
}

function Resolve-InputWindowContextOrBlock {
    param(
        [string]$Alias = '',
        [string]$ActionLabel = 'desktop input action'
    )

    try {
        return Resolve-InputWindowContext -Alias $Alias
    }
    catch {
        $message = $_.Exception.Message
        if (
            $message -like 'Windows did not move focus to the requested allowlisted window:*' -or
            $message -like 'Desktop input actions require a focused allowlisted window or an explicit allowed target.'
        ) {
            $effectiveTarget = if ([string]::IsNullOrWhiteSpace($Alias)) { 'active_allowlisted_window' } else { $Alias }
            $activeWindow = Get-ActiveWindowInfo
            $reason = if ($activeWindow.Handle -eq [System.IntPtr]::Zero) {
                "Foreground desktop access is unavailable in this session, so $ActionLabel requires manual operator focus for target: $effectiveTarget."
            }
            else {
                "Desktop input focus could not be verified for target $effectiveTarget, so $ActionLabel requires manual operator focus."
            }
            Stop-BlockedAction -Reason $reason -GuardState 'manual_focus_required' -TargetValue $effectiveTarget
        }

        throw
    }
}

function Resolve-HotkeySpec {
    param(
        [string]$HotkeyTarget
    )

    $normalized = ([string]$HotkeyTarget).Trim().ToLowerInvariant()
    if ([string]::IsNullOrWhiteSpace($normalized)) {
        throw 'send_hotkey requires a hotkey target.'
    }

    $alias = ''
    $hotkey = $normalized
    if ($normalized.Contains('|')) {
        $parts = $normalized.Split('|', 2)
        $alias = $parts[0].Trim()
        $hotkey = $parts[1].Trim()
    }

    if (-not [string]::IsNullOrWhiteSpace($alias) -and -not $allowedWindowTargets.Contains($alias)) {
        throw "Unsupported allowed window alias for hotkey target: $alias"
    }

    if (-not $allowedHotkeys.Contains($hotkey)) {
        throw "Unsupported hotkey target: $hotkey"
    }

    return [pscustomobject]@{
        Alias = $alias
        Hotkey = $hotkey
        SendKeys = $allowedHotkeys[$hotkey]
    }
}

function Parse-WaitForWindowTarget {
    param(
        [string]$WaitTarget
    )

    $normalized = ([string]$WaitTarget).Trim().ToLowerInvariant()
    if ([string]::IsNullOrWhiteSpace($normalized)) {
        throw 'wait_for_window requires a target alias.'
    }

    $alias = $normalized
    $timeoutSeconds = 15
    if ($normalized.Contains('|')) {
        $parts = $normalized.Split('|', 2)
        $alias = $parts[0].Trim()
        $timeoutRaw = $parts[1].Trim()
        if (-not [int]::TryParse($timeoutRaw, [ref]$timeoutSeconds)) {
            throw 'wait_for_window timeout must be an integer.'
        }
    }

    if (-not $allowedWindowTargets.Contains($alias)) {
        throw "Unsupported wait_for_window target: $alias"
    }
    if ($timeoutSeconds -lt 1 -or $timeoutSeconds -gt 120) {
        throw 'wait_for_window timeout must be between 1 and 120 seconds.'
    }

    return [pscustomobject]@{
        Alias = $alias
        TimeoutSeconds = $timeoutSeconds
    }
}

function Parse-PointTarget {
    param(
        [string]$PointTarget
    )

    $normalized = ([string]$PointTarget).Trim().ToLowerInvariant()
    if ([string]::IsNullOrWhiteSpace($normalized)) {
        throw 'Mouse actions require an explicit point target.'
    }

    $alias = ''
    $pointSpec = $normalized
    if ($normalized.Contains('|')) {
        $parts = $normalized.Split('|', 2)
        $alias = $parts[0].Trim()
        $pointSpec = $parts[1].Trim()
    }

    if (-not [string]::IsNullOrWhiteSpace($alias) -and -not $allowedWindowTargets.Contains($alias)) {
        throw "Unsupported mouse target window alias: $alias"
    }

    $x = 0
    $y = 0
    if ($pointSpec -eq 'center') {
        if ([string]::IsNullOrWhiteSpace($alias)) {
            throw 'center mouse targets require an allowed window alias.'
        }
        $window = Wait-ForAllowedWindowInternal -Alias $alias -TimeoutSeconds 5
        $rect = Get-WindowRectangle -Handle $window.Handle
        if ($null -eq $rect) {
            throw "Unable to read the window rectangle for target: $alias"
        }
        $x = $rect.CenterX
        $y = $rect.CenterY
    }
    else {
        if ($pointSpec -notmatch '^\s*(-?\d+)\s*,\s*(-?\d+)\s*$') {
            throw 'Mouse point targets must be x,y or alias|center.'
        }
        $x = [int]$matches[1]
        $y = [int]$matches[2]
    }

    $bounds = [System.Windows.Forms.SystemInformation]::VirtualScreen
    $insideBounds = $x -ge $bounds.Left -and $x -le ($bounds.Right - 1) -and $y -ge $bounds.Top -and $y -le ($bounds.Bottom - 1)
    if (-not $insideBounds) {
        throw "Mouse target is outside the visible desktop bounds: $x,$y"
    }

    return [pscustomobject]@{
        Alias = $alias
        X = $x
        Y = $y
        Coordinates = "$x,$y"
    }
}

function Parse-ScrollTarget {
    param(
        [string]$ScrollTarget
    )

    $normalized = ([string]$ScrollTarget).Trim().ToLowerInvariant()
    if ([string]::IsNullOrWhiteSpace($normalized)) {
        throw 'scroll_mouse requires a scroll amount target.'
    }

    $alias = ''
    $deltaText = $normalized
    if ($normalized.Contains('|')) {
        $parts = $normalized.Split('|', 2)
        $alias = $parts[0].Trim()
        $deltaText = $parts[1].Trim()
    }

    if (-not [string]::IsNullOrWhiteSpace($alias) -and -not $allowedWindowTargets.Contains($alias)) {
        throw "Unsupported mouse target window alias: $alias"
    }

    $delta = 0
    if (-not [int]::TryParse($deltaText, [ref]$delta)) {
        throw 'scroll_mouse target must be an integer amount or alias|amount.'
    }
    if ($delta -eq 0 -or [Math]::Abs($delta) -gt 1200) {
        throw 'scroll_mouse amount must be between -1200 and 1200 and cannot be zero.'
    }

    return [pscustomobject]@{
        Alias = $alias
        Delta = $delta
    }
}

function Invoke-MouseClickSequence {
    param(
        [uint32]$DownFlag,
        [uint32]$UpFlag,
        [int]$ClickCount = 1,
        [string]$Phase = 'mouse click'
    )

    for ($index = 0; $index -lt $ClickCount; $index++) {
        Assert-NotInterrupted -Phase $Phase
        [DesktopBridgeNative]::mouse_event($DownFlag, 0, 0, 0, [UIntPtr]::Zero)
        Wait-WithInterrupt -Milliseconds 70 -Phase $Phase
        [DesktopBridgeNative]::mouse_event($UpFlag, 0, 0, 0, [UIntPtr]::Zero)
        if ($index -lt ($ClickCount - 1)) {
            Wait-WithInterrupt -Milliseconds 90 -Phase $Phase
        }
    }
}

function Invoke-DesktopAction {
    Assert-NotForcedFailure -ActionName $Action

    switch ($Action) {
        'list_windows' {
            $windows = @(Get-AllowedWindows)
            $snapshot = Get-ResourceGuardSnapshot
            $targetFilter = $Target.Trim().ToLowerInvariant()
            if ($targetFilter) {
                if (-not $allowedWindowTargets.Contains($targetFilter)) {
                    throw "Unsupported focus target: $targetFilter"
                }
                $windows = @($windows | Where-Object { $_.Aliases -contains $targetFilter })
            }

            Write-Field 'action_type' 'list_windows'
            Write-Field 'status' 'succeeded'
            Write-Field 'target' ($(if ($targetFilter) { $targetFilter } else { 'all_allowed_windows' }))
            Write-Field 'headline' ("Detected {0} allowlisted window(s)." -f $windows.Count)
            Write-Output 'windows:'
            if ($windows.Count -eq 0) {
                Write-Output '- none'
            }
            else {
                foreach ($window in $windows) {
                    Write-Output ("- {0} | {1}" -f ($window.Aliases -join ','), $window.Title)
                }
            }
            Write-Output 'allowed_targets:'
            foreach ($alias in $allowedWindowTargets.Keys) {
                Write-Output ("- {0}" -f $alias)
            }
            Write-ResourceGuardSnapshot -Snapshot $snapshot
            return
        }

        'get_active_window' {
            $activeWindow = Get-ActiveWindowInfo
            $snapshot = Get-ResourceGuardSnapshot
            Write-Field 'action_type' 'get_active_window'
            Write-Field 'status' 'succeeded'
            Write-Field 'target' 'foreground_window'
            Write-Field 'headline' ($(if ($activeWindow.Title) { 'Active window detected.' } else { 'No active window title detected.' }))
            Write-Field 'active_window_alias' $activeWindow.Alias
            Write-Field 'active_window_title' ($(if ($activeWindow.Title) { $activeWindow.Title } else { 'none' }))
            Write-Field 'foreground_access' $(if ($activeWindow.Handle -eq [System.IntPtr]::Zero) { 'unavailable' } else { 'available' })
            Write-ResourceGuardSnapshot -Snapshot $snapshot
            return
        }

        'focus_window' {
            $alias = $Target.Trim().ToLowerInvariant()
            if ([string]::IsNullOrWhiteSpace($alias)) {
                throw 'focus_window requires a target alias.'
            }

            $focused = Focus-AllowedWindowOrBlock -Alias $alias -ActionLabel 'focusing an allowlisted window'
            Write-Field 'action_type' 'focus_window'
            Write-Field 'status' 'succeeded'
            Write-Field 'target' $alias
            Write-Field 'headline' ("Focused allowlisted window: {0}" -f $alias)
            Write-Field 'focused_window_alias' $focused.ActiveAlias
            Write-Field 'focused_window_title' $focused.ActiveTitle
            return
        }

        'open_allowed_app' {
            $alias = $Target.Trim().ToLowerInvariant()
            if ([string]::IsNullOrWhiteSpace($alias)) {
                throw 'open_allowed_app requires a target alias.'
            }

            $forceResourceGuardCheck = [Environment]::GetEnvironmentVariable('SUPER_AGENT_DESKTOP_TEST_FORCE_RESOURCE_GUARD') -eq '1'
            $existingWindow = if ($forceResourceGuardCheck) { $null } else { Get-WindowByAlias -Alias $alias }
            if ($null -ne $existingWindow) {
                $snapshot = Get-ResourceGuardSnapshot
                $focused = Focus-AllowedWindowOrBlock -Alias $alias -ActionLabel 'reusing an existing allowlisted app window'
                Write-Field 'action_type' 'open_allowed_app'
                Write-Field 'status' 'succeeded'
                Write-Field 'target' $alias
                Write-Field 'headline' ("Focused existing allowlisted app window: {0}" -f $alias)
                Write-Field 'focused_window_title' $focused.ActiveTitle
                Write-Field 'reused_existing_window' 'yes'
                Write-Field 'command_path' 'none'
                Write-ResourceGuardSnapshot -Snapshot $snapshot
                return
            }

            $snapshot = Get-ResourceGuardSnapshot
            if (
                $alias -eq 'terminal' -and (
                    $snapshot.TerminalWindowCount -ge $resourceGuardThresholds.TerminalWindowLimit -or
                    $snapshot.PowerShellProcessCount -ge $resourceGuardThresholds.TerminalProcessLimit
                )
            ) {
                Stop-BlockedAction `
                    -Reason ("Resource guard blocked opening another terminal window because {0} terminal window(s) and {1} PowerShell process(es) are already present." -f $snapshot.TerminalWindowCount, $snapshot.PowerShellProcessCount) `
                    -GuardState 'resource_guard_triggered' `
                    -TargetValue $alias
            }

            $resolved = Resolve-AllowedApp -Alias $alias
            Assert-NotInterrupted -Phase "opening $alias"
            $startProcessParams = @{
                FilePath = $resolved.CommandPath
                PassThru = $true
            }
            if ($resolved.Arguments.Count -gt 0) {
                $startProcessParams.ArgumentList = $resolved.Arguments
            }
            $process = Start-Process @startProcessParams
            [void](Wait-ForAllowedWindowInternal -Alias $alias -TimeoutSeconds 15)
            $focused = Focus-AllowedWindowOrBlock -Alias $alias -ActionLabel 'opening an allowlisted local app'

            Write-Field 'action_type' 'open_allowed_app'
            Write-Field 'status' 'succeeded'
            Write-Field 'target' $alias
            Write-Field 'headline' ("Opened allowlisted app: {0}" -f $alias)
            Write-Field 'command_path' $resolved.CommandPath
            Write-Field 'process_id' "$($process.Id)"
            Write-Field 'reused_existing_window' 'no'
            Write-Field 'focused_window_title' $focused.ActiveTitle
            Write-ResourceGuardSnapshot -Snapshot $snapshot
            return
        }

        'capture_desktop_screenshot' {
            $resolvedArtifactPath = Resolve-SafePath ($(if ($ArtifactPath) { $ArtifactPath } else { New-DefaultScreenshotPath }))
            if (-not (Test-InAllowedRoot -ResolvedPath $resolvedArtifactPath)) {
                throw "Screenshot artifact path is outside the allowed workspace root: $resolvedArtifactPath"
            }

            $artifactDirectory = Split-Path -Parent $resolvedArtifactPath
            if (-not (Test-Path -LiteralPath $artifactDirectory -PathType Container)) {
                New-Item -ItemType Directory -Path $artifactDirectory -Force | Out-Null
            }

            Assert-NotInterrupted -Phase 'desktop screenshot capture'
            $bounds = [System.Windows.Forms.SystemInformation]::VirtualScreen
            $bitmap = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
            $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
            try {
                $graphics.CopyFromScreen($bounds.X, $bounds.Y, 0, 0, $bitmap.Size)
                $bitmap.Save($resolvedArtifactPath, [System.Drawing.Imaging.ImageFormat]::Png)
            }
            catch {
                $message = $_.Exception.Message
                if ($message -match 'CopyFromScreen|Controlador no v[aá]lido|invalid (handle|parameter|driver)|The handle is invalid|Invalid driver') {
                    Stop-BlockedAction `
                        -Reason 'Desktop screenshot capture is unavailable in this Windows session, so a manual screenshot is required.' `
                        -GuardState 'desktop_capture_unavailable' `
                        -TargetValue 'desktop'
                }
                throw
            }
            finally {
                $graphics.Dispose()
                $bitmap.Dispose()
            }

            Write-Field 'action_type' 'capture_desktop_screenshot'
            Write-Field 'status' 'succeeded'
            Write-Field 'target' 'desktop'
            Write-Field 'headline' 'Captured desktop screenshot artifact.'
            Write-Field 'artifact_path' $resolvedArtifactPath
            return
        }

        'get_clipboard_text' {
            $clipboardText = Get-ClipboardTextSafe
            Write-Field 'action_type' 'get_clipboard_text'
            Write-Field 'status' 'succeeded'
            Write-Field 'target' 'clipboard'
            Write-Field 'headline' 'Read clipboard text.'
            Write-Field 'clipboard_preview' (Short-Preview -Text $clipboardText)
            return
        }

        'set_clipboard_text' {
            Assert-NotInterrupted -Phase 'setting clipboard text'
            Set-ClipboardTextSafe -Value $TextContent
            Write-Field 'action_type' 'set_clipboard_text'
            Write-Field 'status' 'succeeded'
            Write-Field 'target' 'clipboard'
            Write-Field 'headline' 'Updated clipboard text.'
            Write-Field 'clipboard_preview' (Short-Preview -Text (Get-ClipboardTextSafe))
            return
        }

        'copy_selection' {
            $alias = $Target.Trim().ToLowerInvariant()
            if (-not [string]::IsNullOrWhiteSpace($alias) -and -not $allowedWindowTargets.Contains($alias)) {
                throw "Unsupported allowed input target: $alias"
            }

            $context = Resolve-InputWindowContextOrBlock -Alias $alias -ActionLabel 'copying a selection'
            Assert-NotInterrupted -Phase "copying selection from $($context.ActiveAlias)"
            [System.Windows.Forms.SendKeys]::SendWait('^c')
            Wait-WithInterrupt -Milliseconds 450 -Phase 'waiting for clipboard copy'

            Write-Field 'action_type' 'copy_selection'
            Write-Field 'status' 'succeeded'
            Write-Field 'target' ($(if ($alias) { $alias } else { $context.ActiveAlias }))
            Write-Field 'headline' ("Copied selection from allowlisted window: {0}" -f $context.ActiveAlias)
            Write-Field 'active_window_alias' $context.ActiveAlias
            Write-Field 'active_window_title' $context.ActiveTitle
            Write-Field 'clipboard_preview' (Short-Preview -Text (Get-ClipboardTextSafe))
            return
        }

        'paste_clipboard' {
            $alias = $Target.Trim().ToLowerInvariant()
            if (-not [string]::IsNullOrWhiteSpace($alias) -and -not $allowedWindowTargets.Contains($alias)) {
                throw "Unsupported allowed input target: $alias"
            }

            $clipboardText = Get-ClipboardTextSafe
            $clipboardPreview = Short-Preview -Text $clipboardText
            if ((-not [string]::IsNullOrWhiteSpace($alias) -and $alias -eq 'terminal' -and (Test-SuspiciousTerminalClipboardText -ClipboardText $clipboardText))) {
                Stop-BlockedAction `
                    -Reason 'Clipboard guard blocked pasting likely checker or recipe label text into the terminal.' `
                    -GuardState 'clipboard_guard_triggered' `
                    -TargetValue 'terminal'
            }

            $context = Resolve-InputWindowContextOrBlock -Alias $alias -ActionLabel 'pasting clipboard text'
            if ($context.ActiveAlias -eq 'terminal' -and (Test-SuspiciousTerminalClipboardText -ClipboardText $clipboardText)) {
                Stop-BlockedAction `
                    -Reason 'Clipboard guard blocked pasting likely checker or recipe label text into the terminal.' `
                    -GuardState 'clipboard_guard_triggered' `
                    -TargetValue $context.ActiveAlias
            }
            Assert-NotInterrupted -Phase "pasting clipboard into $($context.ActiveAlias)"
            [System.Windows.Forms.SendKeys]::SendWait('^v')
            Wait-WithInterrupt -Milliseconds 250 -Phase 'waiting after clipboard paste'

            Write-Field 'action_type' 'paste_clipboard'
            Write-Field 'status' 'succeeded'
            Write-Field 'target' ($(if ($alias) { $alias } else { $context.ActiveAlias }))
            Write-Field 'headline' ("Pasted clipboard into allowlisted window: {0}" -f $context.ActiveAlias)
            Write-Field 'active_window_alias' $context.ActiveAlias
            Write-Field 'active_window_title' $context.ActiveTitle
            Write-Field 'clipboard_preview' $clipboardPreview
            return
        }

        'send_hotkey' {
            $spec = Resolve-HotkeySpec -HotkeyTarget $Target
            if ($spec.Hotkey -eq 'ctrl+v') {
                $clipboardText = Get-ClipboardTextSafe
                if (
                    ((-not [string]::IsNullOrWhiteSpace($spec.Alias) -and $spec.Alias -eq 'terminal') -or [string]::IsNullOrWhiteSpace($spec.Alias)) -and
                    (Test-SuspiciousTerminalClipboardText -ClipboardText $clipboardText)
                ) {
                    Stop-BlockedAction `
                        -Reason 'Clipboard guard blocked Ctrl+V because the clipboard looks like checker or recipe label text.' `
                        -GuardState 'clipboard_guard_triggered' `
                        -TargetValue $(if ([string]::IsNullOrWhiteSpace($spec.Alias)) { 'active_allowlisted_window' } else { $spec.Alias })
                }
            }
            $context = Resolve-InputWindowContextOrBlock -Alias $spec.Alias -ActionLabel ("sending hotkey {0}" -f $spec.Hotkey)
            Assert-NotInterrupted -Phase "sending hotkey $($spec.Hotkey)"
            [System.Windows.Forms.SendKeys]::SendWait($spec.SendKeys)
            Wait-WithInterrupt -Milliseconds 220 -Phase "waiting after hotkey $($spec.Hotkey)"

            Write-Field 'action_type' 'send_hotkey'
            Write-Field 'status' 'succeeded'
            Write-Field 'target' $spec.Hotkey
            Write-Field 'headline' ("Sent allowlisted hotkey {0} to {1}" -f $spec.Hotkey, $context.ActiveAlias)
            Write-Field 'active_window_alias' $context.ActiveAlias
            Write-Field 'active_window_title' $context.ActiveTitle
            Write-Field 'sent_hotkey' $spec.Hotkey
            return
        }

        'wait_seconds' {
            $seconds = 0
            if (-not [int]::TryParse($Target.Trim(), [ref]$seconds)) {
                throw 'wait_seconds target must be an integer number of seconds.'
            }
            if ($seconds -lt 1 -or $seconds -gt 60) {
                throw 'wait_seconds target must be between 1 and 60 seconds.'
            }

            Wait-WithInterrupt -Milliseconds ($seconds * 1000) -Phase "waiting $seconds second(s)"
            Write-Field 'action_type' 'wait_seconds'
            Write-Field 'status' 'succeeded'
            Write-Field 'target' $seconds
            Write-Field 'headline' ("Waited {0} second(s)." -f $seconds)
            Write-Field 'waited_seconds' $seconds
            return
        }

        'wait_for_window' {
            $spec = Parse-WaitForWindowTarget -WaitTarget $Target
            $window = Wait-ForAllowedWindowInternal -Alias $spec.Alias -TimeoutSeconds $spec.TimeoutSeconds
            Write-Field 'action_type' 'wait_for_window'
            Write-Field 'status' 'succeeded'
            Write-Field 'target' $spec.Alias
            Write-Field 'headline' ("Detected allowlisted window: {0}" -f $spec.Alias)
            Write-Field 'wait_window_alias' $spec.Alias
            Write-Field 'matched_window_title' $window.Title
            Write-Field 'timeout_seconds' $spec.TimeoutSeconds
            return
        }

        'move_mouse' {
            $point = Parse-PointTarget -PointTarget $Target
            if (-not [string]::IsNullOrWhiteSpace($point.Alias)) {
                [void](Resolve-InputWindowContextOrBlock -Alias $point.Alias -ActionLabel 'moving the mouse')
            }
            else {
                [void](Resolve-InputWindowContextOrBlock -ActionLabel 'moving the mouse')
            }

            Assert-NotInterrupted -Phase "moving mouse to $($point.Coordinates)"
            if (-not [DesktopBridgeNative]::SetCursorPos($point.X, $point.Y)) {
                throw "Windows could not move the mouse to $($point.Coordinates)"
            }
            Wait-WithInterrupt -Milliseconds 120 -Phase 'verifying mouse move'
            $cursor = [System.Windows.Forms.Cursor]::Position
            $deltaX = [Math]::Abs($cursor.X - $point.X)
            $deltaY = [Math]::Abs($cursor.Y - $point.Y)
            if ($deltaX -gt 6 -or $deltaY -gt 6) {
                throw "Windows did not place the mouse at the requested coordinates: $($point.Coordinates) (actual $($cursor.X),$($cursor.Y))"
            }

            Write-Field 'action_type' 'move_mouse'
            Write-Field 'status' 'succeeded'
            Write-Field 'target' $Target
            Write-Field 'headline' ("Moved mouse to {0}" -f $point.Coordinates)
            Write-Field 'coordinates' $point.Coordinates
            Write-Field 'actual_coordinates' ("{0},{1}" -f $cursor.X, $cursor.Y)
            return
        }

        'left_click' {
            $point = Parse-PointTarget -PointTarget $Target
            if (-not [string]::IsNullOrWhiteSpace($point.Alias)) {
                [void](Resolve-InputWindowContextOrBlock -Alias $point.Alias -ActionLabel 'left clicking')
            }
            else {
                [void](Resolve-InputWindowContextOrBlock -ActionLabel 'left clicking')
            }

            if (-not [DesktopBridgeNative]::SetCursorPos($point.X, $point.Y)) {
                throw "Windows could not move the mouse to $($point.Coordinates)"
            }
            Wait-WithInterrupt -Milliseconds 120 -Phase 'settling mouse before left click'
            Invoke-MouseClickSequence -DownFlag $mouseEventFlags.LEFTDOWN -UpFlag $mouseEventFlags.LEFTUP -ClickCount 1 -Phase 'left click'

            Write-Field 'action_type' 'left_click'
            Write-Field 'status' 'succeeded'
            Write-Field 'target' $Target
            Write-Field 'headline' ("Left click completed at {0}" -f $point.Coordinates)
            Write-Field 'coordinates' $point.Coordinates
            return
        }

        'double_click' {
            $point = Parse-PointTarget -PointTarget $Target
            if (-not [string]::IsNullOrWhiteSpace($point.Alias)) {
                [void](Resolve-InputWindowContextOrBlock -Alias $point.Alias -ActionLabel 'double clicking')
            }
            else {
                [void](Resolve-InputWindowContextOrBlock -ActionLabel 'double clicking')
            }

            if (-not [DesktopBridgeNative]::SetCursorPos($point.X, $point.Y)) {
                throw "Windows could not move the mouse to $($point.Coordinates)"
            }
            Wait-WithInterrupt -Milliseconds 120 -Phase 'settling mouse before double click'
            Invoke-MouseClickSequence -DownFlag $mouseEventFlags.LEFTDOWN -UpFlag $mouseEventFlags.LEFTUP -ClickCount 2 -Phase 'double click'

            Write-Field 'action_type' 'double_click'
            Write-Field 'status' 'succeeded'
            Write-Field 'target' $Target
            Write-Field 'headline' ("Double click completed at {0}" -f $point.Coordinates)
            Write-Field 'coordinates' $point.Coordinates
            return
        }

        'right_click' {
            $point = Parse-PointTarget -PointTarget $Target
            if (-not [string]::IsNullOrWhiteSpace($point.Alias)) {
                [void](Resolve-InputWindowContextOrBlock -Alias $point.Alias -ActionLabel 'right clicking')
            }
            else {
                [void](Resolve-InputWindowContextOrBlock -ActionLabel 'right clicking')
            }

            if (-not [DesktopBridgeNative]::SetCursorPos($point.X, $point.Y)) {
                throw "Windows could not move the mouse to $($point.Coordinates)"
            }
            Wait-WithInterrupt -Milliseconds 120 -Phase 'settling mouse before right click'
            Invoke-MouseClickSequence -DownFlag $mouseEventFlags.RIGHTDOWN -UpFlag $mouseEventFlags.RIGHTUP -ClickCount 1 -Phase 'right click'

            Write-Field 'action_type' 'right_click'
            Write-Field 'status' 'succeeded'
            Write-Field 'target' $Target
            Write-Field 'headline' ("Right click completed at {0}" -f $point.Coordinates)
            Write-Field 'coordinates' $point.Coordinates
            return
        }

        'scroll_mouse' {
            $scroll = Parse-ScrollTarget -ScrollTarget $Target
            if (-not [string]::IsNullOrWhiteSpace($scroll.Alias)) {
                [void](Resolve-InputWindowContextOrBlock -Alias $scroll.Alias -ActionLabel 'scrolling mouse input')
            }
            else {
                [void](Resolve-InputWindowContextOrBlock -ActionLabel 'scrolling mouse input')
            }

            Assert-NotInterrupted -Phase 'scrolling mouse'
            [DesktopBridgeNative]::mouse_event($mouseEventFlags.WHEEL, 0, 0, [uint32]$scroll.Delta, [UIntPtr]::Zero)
            Wait-WithInterrupt -Milliseconds 120 -Phase 'settling after mouse scroll'

            Write-Field 'action_type' 'scroll_mouse'
            Write-Field 'status' 'succeeded'
            Write-Field 'target' $Target
            Write-Field 'headline' ("Mouse scroll completed with delta {0}" -f $scroll.Delta)
            Write-Field 'scroll_delta' $scroll.Delta
            return
        }
    }
}

try {
    Invoke-DesktopAction
    exit 0
}
catch [System.OperationCanceledException] {
    $message = $_.Exception.Message
    Write-Field 'action_type' $Action
    Write-Field 'status' 'interrupted'
    Write-Field 'target' ($(if ($Target) { $Target } else { 'none' }))
    Write-Field 'interruption_reason' $message
    Write-Field 'headline' ("Desktop bridge action interrupted: {0}" -f $message)
    exit 130
}
catch {
    $message = $_.Exception.Message
    Write-Field 'action_type' $Action
    Write-Field 'status' 'failed'
    Write-Field 'target' ($(if ($Target) { $Target } else { 'none' }))
    Write-Field 'failure_reason' $message
    Write-Field 'failure_detail' ($_.ScriptStackTrace -replace '\r?\n', ' | ')
    Write-Field 'headline' ("Desktop bridge action failed: {0}" -f $message)
    exit 1
}
