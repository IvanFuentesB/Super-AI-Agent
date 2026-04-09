[CmdletBinding()]
param(
    [Parameter(Mandatory = $true)]
    [ValidateSet('list_windows', 'get_active_window', 'focus_window', 'open_allowed_app', 'capture_desktop_screenshot')]
    [string]$Action,

    [string]$Target = '',

    [string]$ArtifactPath = '',

    [string]$AllowedRoot = 'C:\Users\ai_sandbox\Documents\AI_Managed_Only'
)

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

Add-Type -AssemblyName System.Windows.Forms
Add-Type -AssemblyName System.Drawing

$signature = @'
using System;
using System.Collections.Generic;
using System.Runtime.InteropServices;
using System.Text;

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

function Write-Field {
    param(
        [string]$Name,
        [string]$Value
    )

    Write-Output ("{0}: {1}" -f $Name, $Value)
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

function Get-AllowedWindows {
    $windows = @()
    foreach ($processItem in Get-Process | Where-Object { $_.MainWindowHandle -ne 0 -and -not [string]::IsNullOrWhiteSpace($_.MainWindowTitle) }) {
        $title = $processItem.MainWindowTitle.Trim()
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
            }
        }
    }
    return @($windows)
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

function Get-ActiveWindowInfo {
    $handle = [DesktopBridgeNative]::GetForegroundWindow()
    if ($handle -eq [IntPtr]::Zero) {
        return [pscustomobject]@{
            Handle = [IntPtr]::Zero
            Title = ''
            Alias = 'none'
        }
    }

    $title = ''
    foreach ($processItem in Get-Process | Where-Object { $_.MainWindowHandle -eq $handle }) {
        $title = $processItem.MainWindowTitle.Trim()
        break
    }
    $alias = 'unsupported'

    foreach ($entry in $allowedWindowTargets.GetEnumerator()) {
        foreach ($needle in $entry.Value) {
            if ($title.IndexOf($needle, [System.StringComparison]::OrdinalIgnoreCase) -ge 0) {
                $alias = $entry.Key
                break
            }
        }

        if ($alias -ne 'unsupported') {
            break
        }
    }

    return [pscustomobject]@{
        Handle = $handle
        Title = $title
        Alias = $alias
    }
}

function Invoke-DesktopAction {
    switch ($Action) {
        'list_windows' {
            $windows = @(Get-AllowedWindows)
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
            return
        }

        'get_active_window' {
            $activeWindow = Get-ActiveWindowInfo
            Write-Field 'action_type' 'get_active_window'
            Write-Field 'status' 'succeeded'
            Write-Field 'target' 'foreground_window'
            Write-Field 'headline' ($(if ($activeWindow.Title) { 'Active window detected.' } else { 'No active window title detected.' }))
            Write-Field 'active_window_alias' $activeWindow.Alias
            Write-Field 'active_window_title' ($(if ($activeWindow.Title) { $activeWindow.Title } else { 'none' }))
            return
        }

        'focus_window' {
            $alias = $Target.Trim().ToLowerInvariant()
            if ([string]::IsNullOrWhiteSpace($alias)) {
                throw 'focus_window requires a target alias.'
            }
            if (-not $allowedWindowTargets.Contains($alias)) {
                throw "Unsupported focus target: $alias"
            }

            $window = Get-WindowByAlias -Alias $alias
            if ($null -eq $window) {
                throw "No visible allowlisted window found for target: $alias"
            }

            $shell = New-Object -ComObject WScript.Shell
            $focusOk = $false

            if ($shell.AppActivate($window.Title)) {
                $focusOk = $true
            }

            if (-not $focusOk) {
                [void][DesktopBridgeNative]::ShowWindowAsync($window.Handle, 5)
                $focusOk = [DesktopBridgeNative]::SetForegroundWindow($window.Handle)
                [void][DesktopBridgeNative]::BringWindowToTop($window.Handle)
            }

            Start-Sleep -Milliseconds 350
            $activeWindow = Get-ActiveWindowInfo
            if (-not ($activeWindow.Alias -eq $alias -or $activeWindow.Title -eq $window.Title)) {
                throw "Windows did not move focus to the requested allowlisted window: $alias"
            }

            Write-Field 'action_type' 'focus_window'
            Write-Field 'status' 'succeeded'
            Write-Field 'target' $alias
            Write-Field 'headline' ("Focused allowlisted window: {0}" -f $alias)
            Write-Field 'focused_window_title' $window.Title
            return
        }

        'open_allowed_app' {
            $alias = $Target.Trim().ToLowerInvariant()
            if ([string]::IsNullOrWhiteSpace($alias)) {
                throw 'open_allowed_app requires a target alias.'
            }

            $resolved = Resolve-AllowedApp -Alias $alias
            $startProcessParams = @{
                FilePath = $resolved.CommandPath
                PassThru = $true
            }
            if ($resolved.Arguments.Count -gt 0) {
                $startProcessParams.ArgumentList = $resolved.Arguments
            }
            $process = Start-Process @startProcessParams
            Write-Field 'action_type' 'open_allowed_app'
            Write-Field 'status' 'succeeded'
            Write-Field 'target' $alias
            Write-Field 'headline' ("Opened allowlisted app: {0}" -f $alias)
            Write-Field 'command_path' $resolved.CommandPath
            Write-Field 'process_id' "$($process.Id)"
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

            $bounds = [System.Windows.Forms.SystemInformation]::VirtualScreen
            $bitmap = New-Object System.Drawing.Bitmap $bounds.Width, $bounds.Height
            $graphics = [System.Drawing.Graphics]::FromImage($bitmap)
            try {
                $graphics.CopyFromScreen($bounds.X, $bounds.Y, 0, 0, $bitmap.Size)
                $bitmap.Save($resolvedArtifactPath, [System.Drawing.Imaging.ImageFormat]::Png)
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
    }
}

try {
    Invoke-DesktopAction
    exit 0
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
