# Local dashboard MVP checker with safe local-only behavior.

param(
    [switch]$RuntimeLockSafe
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

function Invoke-CommandCapture {
    param(
        [string]$FilePath,
        [string[]]$Arguments,
        [string]$WorkingDirectory
    )

    $stdoutPath = [System.IO.Path]::GetTempFileName()
    $stderrPath = [System.IO.Path]::GetTempFileName()

    try {
        $process = Start-Process `
            -FilePath $FilePath `
            -ArgumentList $Arguments `
            -WorkingDirectory $WorkingDirectory `
            -NoNewWindow `
            -PassThru `
            -Wait `
            -RedirectStandardOutput $stdoutPath `
            -RedirectStandardError $stderrPath

        $parts = @()
        if (Test-Path -LiteralPath $stdoutPath) {
            $stdoutText = Get-Content -Raw -LiteralPath $stdoutPath
            if (-not [string]::IsNullOrWhiteSpace($stdoutText)) {
                $parts += $stdoutText.TrimEnd()
            }
        }
        if (Test-Path -LiteralPath $stderrPath) {
            $stderrText = Get-Content -Raw -LiteralPath $stderrPath
            if (-not [string]::IsNullOrWhiteSpace($stderrText)) {
                $parts += $stderrText.TrimEnd()
            }
        }

        return @{
            ExitCode = $process.ExitCode
            Output = ($parts -join [Environment]::NewLine)
        }
    }
    finally {
        Remove-Item -LiteralPath $stdoutPath, $stderrPath -Force -ErrorAction SilentlyContinue
    }
}

function Resolve-CommandPath {
    param(
        [string]$PrimaryName,
        [string[]]$FallbackNames = @()
    )

    foreach ($name in (@($PrimaryName) + $FallbackNames)) {
        $command = Get-Command $name -ErrorAction SilentlyContinue
        if ($command) {
            return $command.Source
        }
    }

    return $null
}

function Resolve-PythonPath {
    $command = Get-Command python -ErrorAction SilentlyContinue
    if ($command) {
        return $command.Source
    }

    $candidates = @(
        'C:\Users\ai_sandbox\AppData\Local\Programs\Python\Python313\python.exe',
        'C:\Program Files\KiCad\9.0\bin\python.exe',
        'C:\Program Files\SOLIDWORKS Corp\SOLIDWORKS\Simulation\Topology\tools\smapy\python\python.exe'
    )

    foreach ($candidate in $candidates) {
        if (Test-Path -LiteralPath $candidate -PathType Leaf) {
            return $candidate
        }
    }

    return $null
}

function Invoke-ModuleCommand {
    param(
        [string]$PythonPath,
        [string[]]$Arguments,
        [hashtable]$EnvOverrides = @{}
    )

    $argumentsJson = ConvertTo-Json -InputObject @($Arguments) -Compress
    $argumentsEncoded = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($argumentsJson))
    $envOverridesJson = ConvertTo-Json -InputObject $EnvOverrides -Compress -Depth 5
    $envOverridesEncoded = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($envOverridesJson))
    $runtimeSrcEscaped = $runtimeSrc.Replace('\', '\\').Replace("'", "\\'")
    $scriptPath = [System.IO.Path]::ChangeExtension([System.IO.Path]::GetTempFileName(), '.py')
    $code = @"
import base64
import json
import os
import sys
sys.path.insert(0, r'$runtimeSrcEscaped')
from super_ai_agent.cli import main
env_overrides = json.loads(base64.b64decode('$envOverridesEncoded').decode('utf-8'))
for key, value in env_overrides.items():
    os.environ[str(key)] = str(value)
argv = json.loads(base64.b64decode('$argumentsEncoded').decode('utf-8'))
raise SystemExit(main(argv))
"@

    $stdoutPath = [System.IO.Path]::GetTempFileName()
    $stderrPath = [System.IO.Path]::GetTempFileName()

    try {
        Set-Content -LiteralPath $scriptPath -Value $code -Encoding UTF8
        $process = Start-Process `
            -FilePath $PythonPath `
            -ArgumentList $scriptPath `
            -NoNewWindow `
            -PassThru `
            -Wait `
            -RedirectStandardOutput $stdoutPath `
            -RedirectStandardError $stderrPath

        $parts = @()
        if (Test-Path -LiteralPath $stdoutPath) {
            $stdoutText = Get-Content -Raw -LiteralPath $stdoutPath
            if (-not [string]::IsNullOrWhiteSpace($stdoutText)) {
                $parts += $stdoutText.TrimEnd()
            }
        }
        if (Test-Path -LiteralPath $stderrPath) {
            $stderrText = Get-Content -Raw -LiteralPath $stderrPath
            if (-not [string]::IsNullOrWhiteSpace($stderrText)) {
                $parts += $stderrText.TrimEnd()
            }
        }

        return @{
            ExitCode = $process.ExitCode
            Output = ($parts -join [Environment]::NewLine)
        }
    }
    finally {
        Remove-Item -LiteralPath $scriptPath, $stdoutPath, $stderrPath -Force -ErrorAction SilentlyContinue
    }
}

function Remove-GeneratedFile {
    param(
        [string]$Path
    )

    if (-not (Test-Path -LiteralPath $Path -PathType Leaf)) {
        return
    }

    try {
        Remove-Item -LiteralPath $Path -Force -ErrorAction Stop
    }
    catch {
        cmd /c del /f /q "$Path" | Out-Null
    }
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$projectRoot = Join-Path $repoRoot '01_projects\dashboard_mvp'
$browserArtifactPath = Join-Path $repoRoot '01_projects\browser_playground\artifacts\smoke-click.png'
$desktopArtifactPath = Join-Path $repoRoot '05_logs\tmp\desktop\dashboard-desktop-check.png'
$runtimeRoot = Join-Path $repoRoot '01_projects\runtime_mvp'
$runtimeSrc = Join-Path $runtimeRoot 'src'

$expectedFiles = @(
    '04_docs/local_dashboard_mvp.md',
    '04_docs/operator_mode_plan.md',
    '04_docs/browser_control_playground.md',
    '04_docs/artifact_ux_plan.md',
    '04_docs/desktop_bridge_foundation.md',
    '04_docs/ghoti_control_center.md',
    '04_docs/supervisor_foundation.md',
    '04_docs/approval_inbox_plan.md',
    '04_docs/notification_adapter_plan.md',
    '08_research/repo_integration_map.md',
    '14_context/chat_handoff_latest.md',
    '01_projects/dashboard_mvp/README.md',
    '01_projects/dashboard_mvp/package.json',
    '01_projects/dashboard_mvp/server.js',
    '01_projects/dashboard_mvp/public/index.html',
    '01_projects/dashboard_mvp/public/app.js',
    '01_projects/dashboard_mvp/public/styles.css',
    '01_projects/dashboard_mvp/artifacts/.gitkeep',
    '01_projects/desktop_playground/README.md',
    '01_projects/desktop_playground/check_desktop_playground.ps1',
    '01_projects/desktop_playground/desktop_bridge_actions.ps1'
)

$failed = 0

foreach ($relativePath in $expectedFiles) {
    $exists = Test-Path -LiteralPath (Join-Path $repoRoot $relativePath) -PathType Leaf
    Write-Check -Name 'File exists' -Passed $exists -Detail $relativePath
    if (-not $exists) { $failed++ }
}

$nodePath = Resolve-CommandPath -PrimaryName 'node.exe' -FallbackNames @('node')
$npmPath = Resolve-CommandPath -PrimaryName 'npm.cmd' -FallbackNames @('npm')
$pythonPath = Resolve-PythonPath

$nodeOk = -not [string]::IsNullOrWhiteSpace($nodePath)
$npmOk = -not [string]::IsNullOrWhiteSpace($npmPath)
$pythonOk = -not [string]::IsNullOrWhiteSpace($pythonPath)
Write-Check -Name 'Node available' -Passed $nodeOk -Detail ($(if ($nodeOk) { $nodePath } else { 'node not found' }))
Write-Check -Name 'npm available' -Passed $npmOk -Detail ($(if ($npmOk) { $npmPath } else { 'npm not found' }))
Write-Check -Name 'Python available for dashboard-integrated runtime actions' -Passed $pythonOk -Detail ($(if ($pythonOk) { $pythonPath } else { 'python not found' }))
if (-not $nodeOk) { $failed++ }
if (-not $npmOk) { $failed++ }
if (-not $pythonOk) { $failed++ }

if (-not ($nodeOk -and $npmOk -and $pythonOk)) {
    Write-Host ''
    Write-Host ('Summary: {0} dashboard check(s) failed before server execution.' -f $failed)
    exit 1
}

$packageCheckResult = Invoke-CommandCapture -FilePath $npmPath -Arguments @('run', 'check') -WorkingDirectory $projectRoot
$packageCheckOk = $packageCheckResult.ExitCode -eq 0
Write-Check -Name 'Dashboard package check' -Passed $packageCheckOk -Detail (($packageCheckResult.Output | Out-String).Trim())
if (-not $packageCheckOk) {
    $failed++
    Write-Host ''
    Write-Host ('Summary: {0} dashboard check(s) failed.' -f $failed)
    exit 1
}

$port = 3211
$handoffFixtureWindowsJson = @(
    @{ Title = 'Codex - Task'; ProcessId = 1201; Active = $true },
    @{ Title = 'ChatGPT - Browser'; ProcessId = 2202; Active = $false },
    @{ Title = 'ChatGPT Notes'; ProcessId = 2203; Active = $false }
) | ConvertTo-Json -Compress
$serverStdout = [System.IO.Path]::GetTempFileName()
$serverStderr = [System.IO.Path]::GetTempFileName()
$serverProcess = $null

try {
    Remove-GeneratedFile -Path $browserArtifactPath

    $previousPort = $env:PORT
    $hadWindowFixturesEnv = Test-Path Env:SUPER_AGENT_DESKTOP_TEST_WINDOW_FIXTURES
    $previousWindowFixturesEnv = if ($hadWindowFixturesEnv) { (Get-Item Env:SUPER_AGENT_DESKTOP_TEST_WINDOW_FIXTURES).Value } else { $null }
    $env:PORT = "$port"
    $env:SUPER_AGENT_DESKTOP_TEST_WINDOW_FIXTURES = $handoffFixtureWindowsJson
    $serverProcess = Start-Process `
        -FilePath $nodePath `
        -ArgumentList @('server.js') `
        -WorkingDirectory $projectRoot `
        -PassThru `
        -RedirectStandardOutput $serverStdout `
        -RedirectStandardError $serverStderr
    if ($null -eq $previousPort) {
        Remove-Item Env:PORT -ErrorAction SilentlyContinue
    }
    else {
        $env:PORT = $previousPort
    }
    if ($hadWindowFixturesEnv) {
        $env:SUPER_AGENT_DESKTOP_TEST_WINDOW_FIXTURES = $previousWindowFixturesEnv
    }
    else {
        Remove-Item Env:SUPER_AGENT_DESKTOP_TEST_WINDOW_FIXTURES -ErrorAction SilentlyContinue
    }

    $healthUri = "http://127.0.0.1:$port/api/health"
    $serverReady = $false
    foreach ($attempt in 1..30) {
        Start-Sleep -Milliseconds 500
        try {
            $health = Invoke-RestMethod -Uri $healthUri -Method Get -TimeoutSec 5
            if ($health.ok) {
                $serverReady = $true
                break
            }
        }
        catch {
            if ($serverProcess.HasExited) {
                break
            }
        }
    }

    $serverDetail = if ($serverReady) { $healthUri } else { 'server did not become ready' }
    Write-Check -Name 'Dashboard server start' -Passed $serverReady -Detail $serverDetail
    if (-not $serverReady) {
        $failed++
        throw 'Dashboard server failed to start.'
    }

    $operatorStatus = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/operator-status" -Method Get -TimeoutSec 30
    $operatorOk = $operatorStatus.ok -and $operatorStatus.localOnly -and $operatorStatus.liveNow.Count -gt 0
    Write-Check -Name 'Operator status endpoint' -Passed $operatorOk -Detail ($(if ($operatorOk) { 'operator mode status returned and is local-only' } else { 'operator mode status missing or not local-only' }))
    if (-not $operatorOk) { $failed++ }

    $supervisorStatus = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/supervisor/status" -Method Get -TimeoutSec 30
    $supervisorStatusOk = $supervisorStatus.ok -and $supervisorStatus.localOnly -and $supervisorStatus.summary.status
    Write-Check -Name 'Supervisor status endpoint' -Passed $supervisorStatusOk -Detail ($(if ($supervisorStatusOk) { $supervisorStatus.summary.headline } else { 'supervisor status missing structured output' }))
    if (-not $supervisorStatusOk) { $failed++ }

    $ghotiStatusOk = $supervisorStatus.ok -and `
        $supervisorStatus.summary.ghotiState -and `
        $null -ne $supervisorStatus.summary.resourceGuardEventCount -and `
        $supervisorStatus.summary.operatorNextStep
    Write-Check -Name 'Supervisor endpoint includes Ghoti state fields' -Passed $ghotiStatusOk -Detail ($(if ($ghotiStatusOk) { "$($supervisorStatus.summary.ghotiState) | $($supervisorStatus.summary.operatorNextStep)" } else { 'Ghoti state fields missing from supervisor status' }))
    if (-not $ghotiStatusOk) { $failed++ }

    $pendingApprovals = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/approvals/pending" -Method Get -TimeoutSec 30
    $pendingApprovalsOk = $pendingApprovals.ok -and $pendingApprovals.localOnly -and $null -ne $pendingApprovals.summary.requests
    Write-Check -Name 'Pending approvals endpoint' -Passed $pendingApprovalsOk -Detail ($(if ($pendingApprovalsOk) { $pendingApprovals.summary.headline } else { 'pending approvals missing structured output' }))
    if (-not $pendingApprovalsOk) { $failed++ }

    $executorList = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/executor/tasks" -Method Get -TimeoutSec 30
    $executorListOk = $executorList.ok -and $executorList.localOnly -and $null -ne $executorList.summary.tasks
    Write-Check -Name 'Executor task list endpoint' -Passed $executorListOk -Detail ($(if ($executorListOk) { $executorList.summary.headline } else { 'executor task list missing structured output' }))
    if (-not $executorListOk) { $failed++ }

    $ghotiControlCenter = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/ghoti/control-center" -Method Get -TimeoutSec 30
    $ghotiControlCenterOk = $ghotiControlCenter.ok -and `
        $ghotiControlCenter.localOnly -and `
        $ghotiControlCenter.summary.ghotiState -and `
        $ghotiControlCenter.summary.emergencyStopHotkey -eq 'Ctrl+8' -and `
        $ghotiControlCenter.summary.watchdog.status -and `
        $ghotiControlCenter.summary.desktopActionTruth.currentAction -and `
        $ghotiControlCenter.summary.desktopActionTruth.currentTarget -ne $null -and `
        ($ghotiControlCenter.summary.desktopActionTruth.typingEnabled -in @('yes', 'no')) -and `
        $ghotiControlCenter.summary.desktopActionTruth.cueStatus -and `
        $ghotiControlCenter.summary.brain.activeProvider -and `
        $ghotiControlCenter.summary.brain.activeModel -and `
        $ghotiControlCenter.summary.brain.lastModelCallStatus -and `
        ($ghotiControlCenter.summary.brain.currentTaskUsedModelInference -in @($true, $false)) -and `
        $ghotiControlCenter.summary.specialistRole.currentRoleId -and `
        $ghotiControlCenter.summary.specialistRole.currentRoleProvider -and `
        $null -ne $ghotiControlCenter.summary.browser.browserUseInstalled -and `
        $null -ne $ghotiControlCenter.summary.browser.playwrightReady -and `
        $ghotiControlCenter.summary.memory.root -and `
        $null -ne $ghotiControlCenter.summary.memory.ready -and `
        $ghotiControlCenter.summary.relay.relayState -and `
        $ghotiControlCenter.summary.relay.currentStep -and `
        $ghotiControlCenter.summary.relay.sourceTargetAlias -and `
        $ghotiControlCenter.summary.relay.destinationTargetAlias -and `
        $ghotiControlCenter.summary.relay.codexModePreset -and `
        $ghotiControlCenter.summary.relay.codexReasoningPreset -and `
        $ghotiControlCenter.summary.relay.codexExecutionStatus -and `
        $ghotiControlCenter.summary.overlayTarget.label -and `
        $null -ne $ghotiControlCenter.summary.watchdog.alerts -and `
        $ghotiControlCenter.summary.cliCommands.Count -ge 4 -and `
        $ghotiControlCenter.summary.whatGhotiCanDoNow.Count -gt 0 -and `
        $ghotiControlCenter.summary.whatOperatorShouldDoNext.Count -gt 0 -and `
        $ghotiControlCenter.summary.hideCompletedByDefault -and `
        ($ghotiControlCenter.summary.noDeletionPolicy -match 'No task deletion') -and `
        $null -ne $ghotiControlCenter.summary.recentActionableTasks
    Write-Check -Name 'Ghoti control-center endpoint' -Passed $ghotiControlCenterOk -Detail ($(if ($ghotiControlCenterOk) { $ghotiControlCenter.summary.headline } else { 'Ghoti control-center summary missing expected operator fields' }))
    if (-not $ghotiControlCenterOk) { $failed++ }

    if ($RuntimeLockSafe) {
        Write-Check -Name 'Runtime-lock-safe dashboard mode' -Passed $true -Detail 'Skipped dashboard actions that mutate runtime state because this checker is running inside the repo executor lock.'
    }
    else {
    $ghotiFilterSeedPayload = @{
        actionType = 'get_clipboard_text'
    } | ConvertTo-Json
    $ghotiFilterSeedQueue = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/executor/queue" -Method Post -ContentType 'application/json' -Body $ghotiFilterSeedPayload -TimeoutSec 30
    $ghotiFilterSeedQueueOk = $ghotiFilterSeedQueue.ok -and `
        $ghotiFilterSeedQueue.localOnly -and `
        $ghotiFilterSeedQueue.task.status -eq 'queued' -and `
        $ghotiFilterSeedQueue.task.executorActionType -eq 'get_clipboard_text'
    Write-Check -Name 'Seed Ghoti control-center desktop filter task' -Passed $ghotiFilterSeedQueueOk -Detail ($(if ($ghotiFilterSeedQueueOk) { $ghotiFilterSeedQueue.summary.headline } else { 'Ghoti desktop filter seed queue failed' }))
    if (-not $ghotiFilterSeedQueueOk) { $failed++ }

    $ghotiControlCenterDesktopFilter = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/ghoti/control-center?visibility=all&taskType=desktop&taskStatus=queued&activeOnly=true&limit=12" -Method Get -TimeoutSec 30
    $ghotiFilteredTasks = @($ghotiControlCenterDesktopFilter.summary.recentActionableTasks)
    $ghotiControlCenterDesktopFilterOk = $ghotiControlCenterDesktopFilter.ok -and `
        $ghotiControlCenterDesktopFilter.localOnly -and `
        $ghotiControlCenterDesktopFilter.summary.filters.visibility -eq 'all' -and `
        $ghotiControlCenterDesktopFilter.summary.filters.taskType -eq 'desktop' -and `
        $ghotiControlCenterDesktopFilter.summary.filters.taskStatus -eq 'queued' -and `
        $ghotiControlCenterDesktopFilter.summary.filters.activeOnly -eq $true -and `
        $ghotiFilteredTasks.Count -ge 1 -and `
        (@($ghotiFilteredTasks | Where-Object { $_.taskType -ne 'desktop' -or $_.status -ne 'queued' }).Count -eq 0)
    Write-Check -Name 'Ghoti control-center filters recent active desktop tasks honestly' -Passed $ghotiControlCenterDesktopFilterOk -Detail ($(if ($ghotiControlCenterDesktopFilterOk) { "$($ghotiFilteredTasks.Count) filtered desktop task(s) visible" } else { 'Ghoti control-center filter output did not match the requested desktop queued active-only view' }))
    if (-not $ghotiControlCenterDesktopFilterOk) { $failed++ }

    $approvalQueueSeed = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('enqueue', '--title', 'dashboard checker approval task', '--description', 'Validate dashboard approval queue actions.', '--risk', 'ask')
    $approvalQueueSeedOk = $approvalQueueSeed.ExitCode -eq 0
    Write-Check -Name 'Seed approval for dashboard test' -Passed $approvalQueueSeedOk -Detail (($approvalQueueSeed.Output | Out-String).Trim())
    if (-not $approvalQueueSeedOk) {
        $failed++
    }

    $approvalIdMatch = [regex]::Match(($approvalQueueSeed.Output | Out-String), 'approval_request_id:\s*(\S+)')
    $approvalId = if ($approvalIdMatch.Success) { $approvalIdMatch.Groups[1].Value } else { $null }
    $approvalIdOk = -not [string]::IsNullOrWhiteSpace($approvalId)
    Write-Check -Name 'Dashboard approval id parsed' -Passed $approvalIdOk -Detail ($(if ($approvalIdOk) { $approvalId } else { 'missing approval id from seed task output' }))
    if (-not $approvalIdOk) { $failed++ }

    if ($approvalIdOk) {
        $approvalDetail = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/approvals/item?approvalId=$approvalId" -Method Get -TimeoutSec 30
        $approvalDetailOk = $approvalDetail.ok -and $approvalDetail.localOnly -and $approvalDetail.summary.status -eq 'pending'
        Write-Check -Name 'Approval detail endpoint' -Passed $approvalDetailOk -Detail ($(if ($approvalDetailOk) { $approvalDetail.summary.headline } else { 'approval detail did not return pending state' }))
        if (-not $approvalDetailOk) { $failed++ }

        $approvalDecisionPayload = @{
            approvalId = $approvalId
            decision = 'defer'
            note = 'dashboard checker deferred this request'
        } | ConvertTo-Json
        $approvalDecision = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/approvals/decision" -Method Post -ContentType 'application/json' -Body $approvalDecisionPayload -TimeoutSec 30
        $approvalDecisionOk = $approvalDecision.ok -and $approvalDecision.localOnly -and $approvalDecision.approval.status -eq 'deferred'
        Write-Check -Name 'Approval decision endpoint' -Passed $approvalDecisionOk -Detail ($(if ($approvalDecisionOk) { $approvalDecision.summary.headline } else { 'approval decision did not persist deferred state' }))
        if (-not $approvalDecisionOk) { $failed++ }

        $approvalDetailAfter = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/approvals/item?approvalId=$approvalId" -Method Get -TimeoutSec 30
        $approvalDetailAfterOk = $approvalDetailAfter.ok -and $approvalDetailAfter.summary.status -eq 'deferred' -and $approvalDetailAfter.summary.decisionHistory.Count -gt 0
        Write-Check -Name 'Approval detail reflects decision history' -Passed $approvalDetailAfterOk -Detail ($(if ($approvalDetailAfterOk) { $approvalDetailAfter.summary.headline } else { 'approval history not visible after dashboard decision' }))
        if (-not $approvalDetailAfterOk) { $failed++ }
    }

    $outOfScopeSeed = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @(
        'enqueue',
        '--title', 'dashboard checker out-of-scope task',
        '--description', 'Review C:\Windows\Temp\dashboard-outside-target.txt before any action.',
        '--risk', 'safe'
    )
    $outOfScopeSeedOk = $outOfScopeSeed.ExitCode -eq 0
    Write-Check -Name 'Seed out-of-scope approval for dashboard test' -Passed $outOfScopeSeedOk -Detail (($outOfScopeSeed.Output | Out-String).Trim())
    if (-not $outOfScopeSeedOk) { $failed++ }

    $outOfScopeApprovalMatch = [regex]::Match(($outOfScopeSeed.Output | Out-String), 'approval_request_id:\s*(\S+)')
    $outOfScopeApprovalId = if ($outOfScopeApprovalMatch.Success) { $outOfScopeApprovalMatch.Groups[1].Value } else { $null }
    $outOfScopeTaskMatch = [regex]::Match(($outOfScopeSeed.Output | Out-String), 'task_id:\s*(\S+)')
    $outOfScopeTaskId = if ($outOfScopeTaskMatch.Success) { $outOfScopeTaskMatch.Groups[1].Value } else { $null }
    $outOfScopeApprovalIdOk = -not [string]::IsNullOrWhiteSpace($outOfScopeApprovalId)
    Write-Check -Name 'Out-of-scope approval id parsed' -Passed $outOfScopeApprovalIdOk -Detail ($(if ($outOfScopeApprovalIdOk) { $outOfScopeApprovalId } else { 'missing approval id for out-of-scope task' }))
    if (-not $outOfScopeApprovalIdOk) { $failed++ }

    if ($outOfScopeApprovalIdOk) {
        $outOfScopeDetail = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/approvals/item?approvalId=$outOfScopeApprovalId" -Method Get -TimeoutSec 30
        $outOfScopeDetailOk = $outOfScopeDetail.ok -and `
            $outOfScopeDetail.summary.workspaceScope -eq 'out_of_scope' -and `
            $outOfScopeDetail.summary.workspacePolicy -eq 'blocked_by_workspace_policy'
        Write-Check -Name 'Out-of-scope approval detail is classified clearly' -Passed $outOfScopeDetailOk -Detail ($(if ($outOfScopeDetailOk) { $outOfScopeDetail.summary.workspaceReason } else { 'workspace classification missing from approval detail' }))
        if (-not $outOfScopeDetailOk) { $failed++ }

        $outOfScopeDecisionPayload = @{
            approvalId = $outOfScopeApprovalId
            decision = 'approve'
            note = 'dashboard checker recorded out-of-scope approval'
        } | ConvertTo-Json
        $outOfScopeDecision = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/approvals/decision" -Method Post -ContentType 'application/json' -Body $outOfScopeDecisionPayload -TimeoutSec 30
        $outOfScopeDecisionOk = $outOfScopeDecision.ok -and `
            $outOfScopeDecision.approval.status -eq 'approved' -and `
            $outOfScopeDecision.approval.workspacePolicy -eq 'blocked_by_workspace_policy'
        Write-Check -Name 'Out-of-scope dashboard approval stays policy-blocked' -Passed $outOfScopeDecisionOk -Detail ($(if ($outOfScopeDecisionOk) { $outOfScopeDecision.summary.headline } else { 'out-of-scope approval did not stay policy-blocked' }))
        if (-not $outOfScopeDecisionOk) { $failed++ }

        $blockedTaskVisible = $false
        if ($null -ne $outOfScopeDecision.supervisor.humanNeededTasks) {
            $blockedTaskVisible = @($outOfScopeDecision.supervisor.humanNeededTasks | Where-Object {
                $_.taskId -eq $outOfScopeTaskId -and $_.workspacePolicy -eq 'blocked_by_workspace_policy'
            }).Count -gt 0
        }
        Write-Check -Name 'Out-of-scope task is visible in human-needed list' -Passed $blockedTaskVisible -Detail ($(if ($blockedTaskVisible) { $outOfScopeTaskId } else { 'human-needed list did not show blocked workspace task' }))
        if (-not $blockedTaskVisible) { $failed++ }

        if ($outOfScopeTaskId) {
            $blockedTaskDetail = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/tasks/item?taskId=$outOfScopeTaskId" -Method Get -TimeoutSec 30
            $blockedTaskDetailOk = $blockedTaskDetail.ok -and $blockedTaskDetail.localOnly -and $blockedTaskDetail.summary.workspacePolicy -eq 'blocked_by_workspace_policy'
            Write-Check -Name 'Blocked task detail endpoint' -Passed $blockedTaskDetailOk -Detail ($(if ($blockedTaskDetailOk) { $blockedTaskDetail.summary.headline } else { 'blocked task detail missing policy state' }))
            if (-not $blockedTaskDetailOk) { $failed++ }

            $blockedReviewPayload = @{
                taskId = $outOfScopeTaskId
                action = 'review'
                note = 'dashboard checker reviewed the blocked task'
            } | ConvertTo-Json
            $blockedReview = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/tasks/action" -Method Post -ContentType 'application/json' -Body $blockedReviewPayload -TimeoutSec 30
            $blockedReviewOk = $blockedReview.ok -and `
                $blockedReview.task.status -eq 'blocked_human_needed' -and `
                $blockedReview.task.workspacePolicy -eq 'blocked_by_workspace_policy'
            Write-Check -Name 'Blocked task review stays blocked' -Passed $blockedReviewOk -Detail ($(if ($blockedReviewOk) { $blockedReview.summary.headline } else { 'blocked task review moved forward unexpectedly' }))
            if (-not $blockedReviewOk) { $failed++ }
        }
    }

    $humanLoopSeed = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('enqueue', '--title', 'dashboard checker human-needed task', '--description', 'Validate review and re-queue flow.', '--risk', 'safe')
    $humanLoopSeedOk = $humanLoopSeed.ExitCode -eq 0
    Write-Check -Name 'Seed human-needed task for dashboard loop' -Passed $humanLoopSeedOk -Detail (($humanLoopSeed.Output | Out-String).Trim())
    if (-not $humanLoopSeedOk) { $failed++ }

    $humanLoopTaskMatch = [regex]::Match(($humanLoopSeed.Output | Out-String), 'task_id:\s*(\S+)')
    $humanLoopTaskId = if ($humanLoopTaskMatch.Success) { $humanLoopTaskMatch.Groups[1].Value } else { $null }
    $humanLoopTaskIdOk = -not [string]::IsNullOrWhiteSpace($humanLoopTaskId)
    Write-Check -Name 'Human-needed loop task id parsed' -Passed $humanLoopTaskIdOk -Detail ($(if ($humanLoopTaskIdOk) { $humanLoopTaskId } else { 'missing task id for human-needed loop' }))
    if (-not $humanLoopTaskIdOk) { $failed++ }

    if ($humanLoopTaskIdOk) {
        $seedHumanNeeded = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('mark-human-needed', '--task-id', $humanLoopTaskId, '--reason', 'dashboard checker needs a manual review')
        $seedHumanNeededOk = $seedHumanNeeded.ExitCode -eq 0
        Write-Check -Name 'Seed mark-human-needed for dashboard loop' -Passed $seedHumanNeededOk -Detail (($seedHumanNeeded.Output | Out-String).Trim())
        if (-not $seedHumanNeededOk) { $failed++ }

        $humanTaskDetail = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/tasks/item?taskId=$humanLoopTaskId" -Method Get -TimeoutSec 30
        $humanTaskDetailOk = $humanTaskDetail.ok -and $humanTaskDetail.summary.status -eq 'blocked_human_needed'
        Write-Check -Name 'Human-needed task detail endpoint' -Passed $humanTaskDetailOk -Detail ($(if ($humanTaskDetailOk) { $humanTaskDetail.summary.headline } else { 'human-needed task detail missing blocked state' }))
        if (-not $humanTaskDetailOk) { $failed++ }

        $reviewPayload = @{
            taskId = $humanLoopTaskId
            action = 'review'
            note = 'dashboard checker reviewed the human-needed task'
        } | ConvertTo-Json
        $reviewResult = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/tasks/action" -Method Post -ContentType 'application/json' -Body $reviewPayload -TimeoutSec 30
        $reviewResultOk = $reviewResult.ok -and $reviewResult.task.status -eq 'ready_to_resume'
        Write-Check -Name 'Task review endpoint' -Passed $reviewResultOk -Detail ($(if ($reviewResultOk) { $reviewResult.summary.headline } else { 'task review did not move to ready_to_resume' }))
        if (-not $reviewResultOk) { $failed++ }

        $requeuePayload = @{
            taskId = $humanLoopTaskId
            action = 'requeue'
            note = 'dashboard checker re-queued the reviewed task'
        } | ConvertTo-Json
        $requeueResult = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/tasks/action" -Method Post -ContentType 'application/json' -Body $requeuePayload -TimeoutSec 30
        $requeueResultOk = $requeueResult.ok -and $requeueResult.task.status -eq 'queued'
        Write-Check -Name 'Task requeue endpoint' -Passed $requeueResultOk -Detail ($(if ($requeueResultOk) { $requeueResult.summary.headline } else { 'task requeue did not return queued state' }))
        if (-not $requeueResultOk) { $failed++ }
    }

    $waitingLoopSeed = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('enqueue', '--title', 'dashboard checker waiting task', '--description', 'Validate waiting resume flow.', '--risk', 'safe')
    $waitingLoopSeedOk = $waitingLoopSeed.ExitCode -eq 0
    Write-Check -Name 'Seed waiting task for dashboard loop' -Passed $waitingLoopSeedOk -Detail (($waitingLoopSeed.Output | Out-String).Trim())
    if (-not $waitingLoopSeedOk) { $failed++ }

    $waitingTaskMatch = [regex]::Match(($waitingLoopSeed.Output | Out-String), 'task_id:\s*(\S+)')
    $waitingTaskId = if ($waitingTaskMatch.Success) { $waitingTaskMatch.Groups[1].Value } else { $null }
    $waitingTaskIdOk = -not [string]::IsNullOrWhiteSpace($waitingTaskId)
    Write-Check -Name 'Waiting task id parsed' -Passed $waitingTaskIdOk -Detail ($(if ($waitingTaskIdOk) { $waitingTaskId } else { 'missing task id for waiting loop' }))
    if (-not $waitingTaskIdOk) { $failed++ }

    if ($waitingTaskIdOk) {
        $seedWaiting = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('wait', '--task-id', $waitingTaskId, '--reason', 'dashboard checker waiting for reply')
        $seedWaitingOk = $seedWaiting.ExitCode -eq 0
        Write-Check -Name 'Seed wait for dashboard loop' -Passed $seedWaitingOk -Detail (($seedWaiting.Output | Out-String).Trim())
        if (-not $seedWaitingOk) { $failed++ }

        $waitingPayload = @{
            taskId = $waitingTaskId
            action = 'resume'
        } | ConvertTo-Json
        $waitingResume = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/tasks/action" -Method Post -ContentType 'application/json' -Body $waitingPayload -TimeoutSec 30
        $waitingResumeOk = $waitingResume.ok -and $waitingResume.task.status -eq 'queued'
        Write-Check -Name 'Waiting task resume endpoint' -Passed $waitingResumeOk -Detail ($(if ($waitingResumeOk) { $waitingResume.summary.headline } else { 'waiting task did not resume to queued' }))
        if (-not $waitingResumeOk) { $failed++ }
    }

    $executorReadPayload = @{
        actionType = 'read_file'
        target = '14_context/current_state.md'
    } | ConvertTo-Json
    $executorReadQueue = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/executor/queue" -Method Post -ContentType 'application/json' -Body $executorReadPayload -TimeoutSec 30
    $executorReadQueueOk = $executorReadQueue.ok -and `
        $executorReadQueue.localOnly -and `
        $executorReadQueue.task.status -eq 'queued' -and `
        $executorReadQueue.task.executorActionType -eq 'read_file' -and `
        $executorReadQueue.task.workspaceScope -eq 'in_scope'
    Write-Check -Name 'Executor read_file queue endpoint' -Passed $executorReadQueueOk -Detail ($(if ($executorReadQueueOk) { $executorReadQueue.summary.headline } else { 'executor read_file queue failed' }))
    if (-not $executorReadQueueOk) { $failed++ }

    $executorReadTaskId = $executorReadQueue.summary.taskId
    $executorReadTaskIdOk = -not [string]::IsNullOrWhiteSpace($executorReadTaskId)
    Write-Check -Name 'Executor read_file task id returned' -Passed $executorReadTaskIdOk -Detail ($(if ($executorReadTaskIdOk) { $executorReadTaskId } else { 'executor read_file task id missing' }))
    if (-not $executorReadTaskIdOk) { $failed++ }

    if ($executorReadTaskIdOk) {
        $executorReadDetail = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/tasks/item?taskId=$executorReadTaskId" -Method Get -TimeoutSec 30
        $executorReadDetailOk = $executorReadDetail.ok -and `
            $executorReadDetail.localOnly -and `
            $executorReadDetail.summary.executorActionType -eq 'read_file'
        Write-Check -Name 'Executor read_file task detail endpoint' -Passed $executorReadDetailOk -Detail ($(if ($executorReadDetailOk) { $executorReadDetail.summary.headline } else { 'executor read_file task detail missing action type' }))
        if (-not $executorReadDetailOk) { $failed++ }

        $executorReadExecutePayload = @{
            taskId = $executorReadTaskId
            action = 'execute'
        } | ConvertTo-Json
        $executorReadExecute = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/tasks/action" -Method Post -ContentType 'application/json' -Body $executorReadExecutePayload -TimeoutSec 30
        $executorReadExecuteOk = $executorReadExecute.ok -and `
            $executorReadExecute.task.status -eq 'completed' -and `
            $executorReadExecute.task.lastExecutionStatus -eq 'succeeded'
        Write-Check -Name 'Executor read_file execution endpoint' -Passed $executorReadExecuteOk -Detail ($(if ($executorReadExecuteOk) { $executorReadExecute.summary.headline } else { 'executor read_file execute failed' }))
        if (-not $executorReadExecuteOk) { $failed++ }

        $executorReadDetailAfter = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/tasks/item?taskId=$executorReadTaskId" -Method Get -TimeoutSec 30
        $executorReadDetailAfterOk = $executorReadDetailAfter.ok -and `
            $executorReadDetailAfter.summary.lastExecutionStatus -eq 'succeeded' -and `
            $executorReadDetailAfter.summary.executionHistory.Count -gt 0
        Write-Check -Name 'Executor read_file result persists in task detail' -Passed $executorReadDetailAfterOk -Detail ($(if ($executorReadDetailAfterOk) { $executorReadDetailAfter.summary.lastExecutionSummary } else { 'executor read_file result not persisted' }))
        if (-not $executorReadDetailAfterOk) { $failed++ }
    }

    $executorArtifactPath = Join-Path $repoRoot '11_exports\personal_ops\dashboard-executor-artifact.md'
    Remove-GeneratedFile -Path $executorArtifactPath
    $executorArtifactPayload = @{
        actionType = 'create_artifact'
        target = '11_exports/personal_ops/dashboard-executor-artifact.md'
        content = "# Dashboard Executor Artifact`n`nCreated through the dashboard executor test."
    } | ConvertTo-Json
    $executorArtifactQueue = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/executor/queue" -Method Post -ContentType 'application/json' -Body $executorArtifactPayload -TimeoutSec 30
    $executorArtifactQueueOk = $executorArtifactQueue.ok -and `
        $executorArtifactQueue.localOnly -and `
        $executorArtifactQueue.task.status -eq 'pending_approval' -and `
        $executorArtifactQueue.task.approvalState -eq 'pending'
    Write-Check -Name 'Executor create_artifact queue endpoint' -Passed $executorArtifactQueueOk -Detail ($(if ($executorArtifactQueueOk) { $executorArtifactQueue.summary.headline } else { 'executor create_artifact queue failed' }))
    if (-not $executorArtifactQueueOk) { $failed++ }

    $executorArtifactTaskId = $executorArtifactQueue.summary.taskId
    $executorArtifactApprovalId = if ($null -ne $executorArtifactQueue.task) { $executorArtifactQueue.task.approvalRequestId } else { $null }
    $executorArtifactIdsOk = (-not [string]::IsNullOrWhiteSpace($executorArtifactTaskId)) -and (-not [string]::IsNullOrWhiteSpace($executorArtifactApprovalId)) -and ($executorArtifactApprovalId -ne 'none')
    Write-Check -Name 'Executor create_artifact ids returned' -Passed $executorArtifactIdsOk -Detail ($(if ($executorArtifactIdsOk) { "$executorArtifactTaskId | $executorArtifactApprovalId" } else { 'executor create_artifact ids missing' }))
    if (-not $executorArtifactIdsOk) { $failed++ }

    if ($executorArtifactIdsOk) {
        $executorArtifactApprovePayload = @{
            approvalId = $executorArtifactApprovalId
            decision = 'approve'
            note = 'dashboard checker approved artifact execution'
        } | ConvertTo-Json
        $executorArtifactApprove = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/approvals/decision" -Method Post -ContentType 'application/json' -Body $executorArtifactApprovePayload -TimeoutSec 30
        $executorArtifactApproveOk = $executorArtifactApprove.ok -and `
            $executorArtifactApprove.approval.status -eq 'approved' -and `
            $executorArtifactApprove.approval.workspacePolicy -eq 'allowed'
        Write-Check -Name 'Executor create_artifact approval endpoint' -Passed $executorArtifactApproveOk -Detail ($(if ($executorArtifactApproveOk) { $executorArtifactApprove.summary.headline } else { 'executor create_artifact approval failed' }))
        if (-not $executorArtifactApproveOk) { $failed++ }

        $executorArtifactExecutePayload = @{
            taskId = $executorArtifactTaskId
            action = 'execute'
        } | ConvertTo-Json
        $executorArtifactExecute = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/tasks/action" -Method Post -ContentType 'application/json' -Body $executorArtifactExecutePayload -TimeoutSec 30
        $executorArtifactExecuteOk = $executorArtifactExecute.ok -and `
            $executorArtifactExecute.task.status -eq 'completed' -and `
            $executorArtifactExecute.task.lastExecutionStatus -eq 'succeeded' -and `
            (Test-Path -LiteralPath $executorArtifactPath -PathType Leaf)
        Write-Check -Name 'Executor create_artifact execution endpoint' -Passed $executorArtifactExecuteOk -Detail ($(if ($executorArtifactExecuteOk) { $executorArtifactExecute.summary.headline } else { 'executor create_artifact execute failed' }))
        if (-not $executorArtifactExecuteOk) { $failed++ }

        $executorArtifactDetail = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/tasks/item?taskId=$executorArtifactTaskId" -Method Get -TimeoutSec 30
        $executorArtifactDetailOk = $executorArtifactDetail.ok -and `
            $executorArtifactDetail.summary.lastExecutionStatus -eq 'succeeded' -and `
            $executorArtifactDetail.summary.lastArtifactPath -eq $executorArtifactPath -and `
            $executorArtifactDetail.summary.executionHistory.Count -gt 0
        Write-Check -Name 'Executor create_artifact result persists in task detail' -Passed $executorArtifactDetailOk -Detail ($(if ($executorArtifactDetailOk) { $executorArtifactDetail.summary.lastArtifactPath } else { 'executor create_artifact result not persisted' }))
        if (-not $executorArtifactDetailOk) { $failed++ }
    }

    $capability = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/capability-summary" -Method Get -TimeoutSec 30
    $capabilityOk = $capability.ok -and $capability.localOnly -and $capability.summary.availableCount -ge 0
    Write-Check -Name 'Capability endpoint' -Passed $capabilityOk -Detail ($(if ($capabilityOk) { $capability.summary.headline } else { 'capability summary missing structured output' }))
    if (-not $capabilityOk) { $failed++ }

    $githubStatus = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/github-updates" -Method Get -TimeoutSec 30
    $githubOk = $githubStatus.ok -and $githubStatus.localOnly -and $githubStatus.summary.branch
    Write-Check -Name 'GitHub updates endpoint' -Passed $githubOk -Detail ($(if ($githubOk) { $githubStatus.summary.headline } else { 'GitHub updates missing structured output' }))
    if (-not $githubOk) { $failed++ }

    $artifacts = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/artifacts" -Method Get -TimeoutSec 30
    $artifactsOk = $artifacts.ok -and $artifacts.localOnly -and $null -ne $artifacts.artifacts
    Write-Check -Name 'Artifact list endpoint' -Passed $artifactsOk -Detail ($(if ($artifactsOk) { "returned $($artifacts.artifacts.Count) artifact entries" } else { 'artifact list missing structured output' }))
    if (-not $artifactsOk) { $failed++ }

    $internshipPayload = @{
        targetRole = 'Applied AI Intern'
        company = 'Example Labs'
        jobSource = 'dashboard checker'
        fitSummary = 'Checker-created internship pack for the local dashboard MVP.'
    } | ConvertTo-Json
    $internship = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/scaffold/internship" -Method Post -ContentType 'application/json' -Body $internshipPayload -TimeoutSec 30
    $internshipPath = $internship.summary.outputPath
    $internshipOk = $internship.ok -and $internshipPath -and (Test-Path -LiteralPath $internshipPath -PathType Leaf)
    Write-Check -Name 'Internship scaffold endpoint' -Passed $internshipOk -Detail ($(if ($internshipOk) { $internshipPath } else { 'internship scaffold was not created' }))
    if (-not $internshipOk) { $failed++ }

    if ($internshipOk) {
        $previewPayload = @{ path = $internshipPath } | ConvertTo-Json
        $artifactPreview = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/artifacts/preview" -Method Post -ContentType 'application/json' -Body $previewPayload -TimeoutSec 30
        $previewOk = $artifactPreview.ok -and $artifactPreview.localOnly -and $artifactPreview.preview.format -eq 'markdown'
        Write-Check -Name 'Artifact preview endpoint' -Passed $previewOk -Detail ($(if ($previewOk) { $artifactPreview.preview.path } else { 'artifact preview failed for markdown output' }))
        if (-not $previewOk) { $failed++ }
    }

    $browserSmoke = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/browser/smoke" -Method Post -ContentType 'application/json' -Body '{}' -TimeoutSec 90
    $browserSmokeDegradedOk = $browserSmoke.degraded -and $browserSmoke.summary.missingDependency -eq 'playwright'
    $browserSmokeOk = ($browserSmoke.ok -and (Test-Path -LiteralPath $browserArtifactPath -PathType Leaf)) -or $browserSmokeDegradedOk
    Write-Check -Name 'Browser smoke endpoint' -Passed $browserSmokeOk -Detail ($(if ($browserSmokeOk) { $browserSmoke.summary.headline } else { 'browser smoke artifact missing or dependency state was not reported truthfully' }))
    if (-not $browserSmokeOk) { $failed++ }

    $visibleCheck = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/browser/visible" -Method Post -ContentType 'application/json' -Body (@{ checkOnly = $true } | ConvertTo-Json) -TimeoutSec 30
    $visibleCheckOk = $visibleCheck.ok -or ($visibleCheck.degraded -and $visibleCheck.summary.missingDependency -eq 'playwright')
    Write-Check -Name 'Visible demo endpoint' -Passed $visibleCheckOk -Detail ($(if ($visibleCheckOk) { $visibleCheck.summary.headline } else { 'visible endpoint failed or dependency state was not reported truthfully' }))
    if (-not $visibleCheckOk) { $failed++ }

    $desktopStatus = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/desktop-bridge/status" -Method Get -TimeoutSec 30
    $desktopStatusOk = $desktopStatus.ok -and $desktopStatus.localOnly -and $desktopStatus.summary.powerShellAvailable
    Write-Check -Name 'Desktop bridge status endpoint' -Passed $desktopStatusOk -Detail ($(if ($desktopStatusOk) { $desktopStatus.summary.headline } else { 'desktop bridge status missing structured output' }))
    if (-not $desktopStatusOk) { $failed++ }

    $desktopGuardSummaryOk = $desktopStatus.ok -and `
        $null -ne $desktopStatus.summary.terminalWindowCount -and `
        $null -ne $desktopStatus.summary.powerShellProcessCount -and `
        $null -ne $desktopStatus.summary.nodeProcessCount -and `
        $null -ne $desktopStatus.summary.pythonProcessCount -and `
        $null -ne $desktopStatus.summary.resourceGuardOk -and `
        $null -ne $desktopStatus.summary.clipboardGuardOk
    Write-Check -Name 'Desktop bridge status includes resource guard fields' -Passed $desktopGuardSummaryOk -Detail ($(if ($desktopGuardSummaryOk) { "term=$($desktopStatus.summary.terminalWindowCount) | pwsh=$($desktopStatus.summary.powerShellProcessCount) | node=$($desktopStatus.summary.nodeProcessCount)" } else { 'desktop bridge resource guard fields missing' }))
    if (-not $desktopGuardSummaryOk) { $failed++ }

    $desktopCheck = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/desktop-bridge/check" -Method Post -ContentType 'application/json' -Body '{}' -TimeoutSec 60
    $desktopCheckOk = $desktopCheck.ok -and $desktopCheck.localOnly -and $desktopCheck.summary.shellCommandCapability
    Write-Check -Name 'Desktop bridge check endpoint' -Passed $desktopCheckOk -Detail ($(if ($desktopCheckOk) { $desktopCheck.summary.headline } else { 'desktop bridge check failed' }))
    if (-not $desktopCheckOk) { $failed++ }

    $desktopListPayload = @{
        actionType = 'list_windows'
    } | ConvertTo-Json
    $desktopListQueue = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/executor/queue" -Method Post -ContentType 'application/json' -Body $desktopListPayload -TimeoutSec 30
    $desktopListQueueOk = $desktopListQueue.ok -and `
        $desktopListQueue.localOnly -and `
        $desktopListQueue.task.status -eq 'queued' -and `
        $desktopListQueue.task.executorActionType -eq 'list_windows'
    Write-Check -Name 'Desktop list_windows queue endpoint' -Passed $desktopListQueueOk -Detail ($(if ($desktopListQueueOk) { $desktopListQueue.summary.headline } else { 'desktop list_windows queue failed' }))
    if (-not $desktopListQueueOk) { $failed++ }

    $desktopListTaskId = $desktopListQueue.summary.taskId
    $desktopListTaskIdOk = -not [string]::IsNullOrWhiteSpace($desktopListTaskId)
    Write-Check -Name 'Desktop list_windows task id returned' -Passed $desktopListTaskIdOk -Detail ($(if ($desktopListTaskIdOk) { $desktopListTaskId } else { 'desktop list_windows task id missing' }))
    if (-not $desktopListTaskIdOk) { $failed++ }

    if ($desktopListTaskIdOk) {
        $desktopListExecutePayload = @{
            taskId = $desktopListTaskId
            action = 'execute'
        } | ConvertTo-Json
        $desktopListExecute = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/tasks/action" -Method Post -ContentType 'application/json' -Body $desktopListExecutePayload -TimeoutSec 30
        $desktopListExecuteOk = $desktopListExecute.ok -and `
            $desktopListExecute.task.status -eq 'completed' -and `
            $desktopListExecute.task.lastExecutionStatus -eq 'succeeded'
        Write-Check -Name 'Desktop list_windows execution endpoint' -Passed $desktopListExecuteOk -Detail ($(if ($desktopListExecuteOk) { $desktopListExecute.summary.headline } else { 'desktop list_windows execute failed' }))
        if (-not $desktopListExecuteOk) { $failed++ }
    }

    $desktopActivePayload = @{
        actionType = 'get_active_window'
    } | ConvertTo-Json
    $desktopActiveQueue = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/executor/queue" -Method Post -ContentType 'application/json' -Body $desktopActivePayload -TimeoutSec 30
    $desktopActiveQueueOk = $desktopActiveQueue.ok -and `
        $desktopActiveQueue.localOnly -and `
        $desktopActiveQueue.task.status -eq 'queued' -and `
        $desktopActiveQueue.task.executorActionType -eq 'get_active_window'
    Write-Check -Name 'Desktop get_active_window queue endpoint' -Passed $desktopActiveQueueOk -Detail ($(if ($desktopActiveQueueOk) { $desktopActiveQueue.summary.headline } else { 'desktop get_active_window queue failed' }))
    if (-not $desktopActiveQueueOk) { $failed++ }

    $desktopActiveTaskId = $desktopActiveQueue.summary.taskId
    $desktopActiveTaskIdOk = -not [string]::IsNullOrWhiteSpace($desktopActiveTaskId)
    Write-Check -Name 'Desktop get_active_window task id returned' -Passed $desktopActiveTaskIdOk -Detail ($(if ($desktopActiveTaskIdOk) { $desktopActiveTaskId } else { 'desktop get_active_window task id missing' }))
    if (-not $desktopActiveTaskIdOk) { $failed++ }

    if ($desktopActiveTaskIdOk) {
        $desktopActiveExecutePayload = @{
            taskId = $desktopActiveTaskId
            action = 'execute'
        } | ConvertTo-Json
        $desktopActiveExecute = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/tasks/action" -Method Post -ContentType 'application/json' -Body $desktopActiveExecutePayload -TimeoutSec 30
        $desktopActiveExecuteOk = $desktopActiveExecute.ok -and `
            $desktopActiveExecute.task.status -eq 'completed' -and `
            $desktopActiveExecute.task.lastExecutionStatus -eq 'succeeded'
        Write-Check -Name 'Desktop get_active_window execution endpoint' -Passed $desktopActiveExecuteOk -Detail ($(if ($desktopActiveExecuteOk) { $desktopActiveExecute.summary.headline } else { 'desktop get_active_window execute failed' }))
        if (-not $desktopActiveExecuteOk) { $failed++ }
    }

    $desktopOpenPayload = @{
        actionType = 'open_allowed_app'
        target = 'terminal'
    } | ConvertTo-Json
    $desktopOpenQueue = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/executor/queue" -Method Post -ContentType 'application/json' -Body $desktopOpenPayload -TimeoutSec 30
    $desktopOpenQueueOk = $desktopOpenQueue.ok -and `
        $desktopOpenQueue.localOnly -and `
        $desktopOpenQueue.task.status -eq 'pending_approval' -and `
        $desktopOpenQueue.task.executorActionType -eq 'open_allowed_app'
    Write-Check -Name 'Desktop open_allowed_app queue endpoint' -Passed $desktopOpenQueueOk -Detail ($(if ($desktopOpenQueueOk) { $desktopOpenQueue.summary.headline } else { 'desktop open_allowed_app queue failed' }))
    if (-not $desktopOpenQueueOk) { $failed++ }

    $desktopOpenTaskId = $desktopOpenQueue.summary.taskId
    $desktopOpenApprovalId = if ($null -ne $desktopOpenQueue.task) { $desktopOpenQueue.task.approvalRequestId } else { $null }
    $desktopOpenIdsOk = (-not [string]::IsNullOrWhiteSpace($desktopOpenTaskId)) -and (-not [string]::IsNullOrWhiteSpace($desktopOpenApprovalId)) -and ($desktopOpenApprovalId -ne 'none')
    Write-Check -Name 'Desktop open_allowed_app ids returned' -Passed $desktopOpenIdsOk -Detail ($(if ($desktopOpenIdsOk) { "$desktopOpenTaskId | $desktopOpenApprovalId" } else { 'desktop open_allowed_app ids missing' }))
    if (-not $desktopOpenIdsOk) { $failed++ }

    if ($desktopOpenIdsOk) {
        $desktopOpenApprovePayload = @{
            approvalId = $desktopOpenApprovalId
            decision = 'approve'
            note = 'dashboard checker approved open_allowed_app'
        } | ConvertTo-Json
        $desktopOpenApprove = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/approvals/decision" -Method Post -ContentType 'application/json' -Body $desktopOpenApprovePayload -TimeoutSec 30
        $desktopOpenApproveOk = $desktopOpenApprove.ok -and $desktopOpenApprove.approval.status -eq 'approved'
        Write-Check -Name 'Desktop open_allowed_app approval endpoint' -Passed $desktopOpenApproveOk -Detail ($(if ($desktopOpenApproveOk) { $desktopOpenApprove.summary.headline } else { 'desktop open_allowed_app approval failed' }))
        if (-not $desktopOpenApproveOk) { $failed++ }

        $desktopOpenExecutePayload = @{
            taskId = $desktopOpenTaskId
            action = 'execute'
        } | ConvertTo-Json
        $desktopOpenExecute = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/tasks/action" -Method Post -ContentType 'application/json' -Body $desktopOpenExecutePayload -TimeoutSec 30
        $desktopOpenExecuteOk = $desktopOpenExecute.ok -and (`
            ((`
                $desktopOpenExecute.task.status -eq 'completed' -and `
                $desktopOpenExecute.task.lastExecutionStatus -eq 'succeeded'`
            ) -or (`
                $desktopOpenExecute.task.status -eq 'blocked_human_needed' -and `
                $desktopOpenExecute.task.lastExecutionStatus -eq 'failed' -and `
                ($desktopOpenExecute.summary.headline -match 'manual operator focus' -or `
                 $desktopOpenExecute.summary.headline -match 'Resource guard blocked')`
            )))
        Write-Check -Name 'Desktop open_allowed_app execution endpoint' -Passed $desktopOpenExecuteOk -Detail ($(if ($desktopOpenExecuteOk) { $desktopOpenExecute.summary.headline } else { 'desktop open_allowed_app execute failed' }))
        if (-not $desktopOpenExecuteOk) { $failed++ }

        $desktopOpenDetail = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/tasks/item?taskId=$desktopOpenTaskId" -Method Get -TimeoutSec 30
        $desktopOpenDetailOk = $desktopOpenDetail.ok -and (`
            ((`
                $desktopOpenDetail.summary.lastExecutionStatus -eq 'succeeded' -and `
                $desktopOpenDetail.summary.lastExecutionSummary -match 'Focused existing allowlisted app window'`
            ) -or (`
                $desktopOpenDetail.summary.status -eq 'blocked_human_needed' -and `
                $desktopOpenDetail.summary.lastExecutionStatus -eq 'failed' -and `
                ($desktopOpenDetail.summary.lastExecutionSummary -match 'manual operator focus' -or `
                 $desktopOpenDetail.summary.lastExecutionSummary -match 'Resource guard blocked')`
            )))
        Write-Check -Name 'Desktop open_allowed_app result reflects focus-first reuse or clear manual focus blocking' -Passed $desktopOpenDetailOk -Detail ($(if ($desktopOpenDetailOk) { $desktopOpenDetail.summary.lastExecutionSummary } else { 'desktop open_allowed_app did not report focused existing window reuse or clear blocking' }))
        if (-not $desktopOpenDetailOk) { $failed++ }
    }

    $guardSeed = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @(
        'queue-executor-action',
        '--action-type', 'open_allowed_app',
        '--target', 'terminal'
    )
    $guardSeedOk = $guardSeed.ExitCode -eq 0
    Write-Check -Name 'Seed dashboard resource-guard task' -Passed $guardSeedOk -Detail (($guardSeed.Output | Out-String).Trim())
    if (-not $guardSeedOk) { $failed++ }

    $guardTaskMatch = [regex]::Match(($guardSeed.Output | Out-String), 'task_id:\s*(\S+)')
    $guardTaskId = if ($guardTaskMatch.Success) { $guardTaskMatch.Groups[1].Value } else { $null }
    $guardApprovalMatch = [regex]::Match(($guardSeed.Output | Out-String), 'approval_request_id:\s*(\S+)')
    $guardApprovalId = if ($guardApprovalMatch.Success) { $guardApprovalMatch.Groups[1].Value } else { $null }

    if (-not [string]::IsNullOrWhiteSpace($guardApprovalId)) {
        $guardApprove = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('approve-approval', '--approval-id', $guardApprovalId, '--note', 'dashboard checker approved guarded terminal open')
        $guardApproveOk = $guardApprove.ExitCode -eq 0
        Write-Check -Name 'Seed resource-guard approval' -Passed $guardApproveOk -Detail (($guardApprove.Output | Out-String).Trim())
        if (-not $guardApproveOk) { $failed++ }
    }

    if (-not [string]::IsNullOrWhiteSpace($guardTaskId)) {
        $guardExecute = Invoke-ModuleCommand `
            -PythonPath $pythonPath `
            -Arguments @('execute-task', '--task-id', $guardTaskId) `
            -EnvOverrides @{
                SUPER_AGENT_DESKTOP_TEST_TERMINAL_WINDOW_COUNT = '3'
                SUPER_AGENT_DESKTOP_TEST_TERMINAL_PROCESS_COUNT = '6'
                SUPER_AGENT_DESKTOP_TEST_FORCE_RESOURCE_GUARD = '1'
            }
        $guardExecuteOk = $guardExecute.ExitCode -eq 0 -and (($guardExecute.Output | Out-String) -match 'status:\s+blocked_human_needed')
        Write-Check -Name 'Seed resource-guard execution' -Passed $guardExecuteOk -Detail (($guardExecute.Output | Out-String).Trim())
        if (-not $guardExecuteOk) { $failed++ }

        $guardTaskDetail = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/tasks/item?taskId=$guardTaskId" -Method Get -TimeoutSec 30
        $guardTaskDetailOk = $guardTaskDetail.ok -and `
            $guardTaskDetail.summary.status -eq 'blocked_human_needed' -and `
            $guardTaskDetail.summary.lastResourceGuardReason -match 'resource guard'
        Write-Check -Name 'Task detail shows resource guard reason' -Passed $guardTaskDetailOk -Detail ($(if ($guardTaskDetailOk) { $guardTaskDetail.summary.lastResourceGuardReason } else { 'resource guard reason missing from dashboard task detail' }))
        if (-not $guardTaskDetailOk) { $failed++ }

        $guardSupervisor = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/supervisor/status" -Method Get -TimeoutSec 30
        $guardSupervisorOk = $guardSupervisor.ok -and `
            $guardSupervisor.summary.ghotiState -eq 'resource_guard_triggered' -and `
            $guardSupervisor.summary.resourceGuardEventCount -ge 1
        Write-Check -Name 'Supervisor view shows resource guard state' -Passed $guardSupervisorOk -Detail ($(if ($guardSupervisorOk) { $guardSupervisor.summary.ghotiReason } else { 'resource guard state missing from supervisor view' }))
        if (-not $guardSupervisorOk) { $failed++ }
    }

    $retrySeed = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @(
        'queue-executor-action',
        '--action-type', 'focus_window',
        '--target', 'terminal'
    )
    $retrySeedOk = $retrySeed.ExitCode -eq 0
    Write-Check -Name 'Seed dashboard retry-limit task' -Passed $retrySeedOk -Detail (($retrySeed.Output | Out-String).Trim())
    if (-not $retrySeedOk) { $failed++ }

    $retryTaskMatch = [regex]::Match(($retrySeed.Output | Out-String), 'task_id:\s*(\S+)')
    $retryTaskId = if ($retryTaskMatch.Success) { $retryTaskMatch.Groups[1].Value } else { $null }
    $retryApprovalMatch = [regex]::Match(($retrySeed.Output | Out-String), 'approval_request_id:\s*(\S+)')
    $retryApprovalId = if ($retryApprovalMatch.Success) { $retryApprovalMatch.Groups[1].Value } else { $null }

    if (-not [string]::IsNullOrWhiteSpace($retryApprovalId)) {
        $retryApprove = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('approve-approval', '--approval-id', $retryApprovalId, '--note', 'dashboard checker approved retry-limit test')
        $retryApproveOk = $retryApprove.ExitCode -eq 0
        Write-Check -Name 'Seed retry-limit approval' -Passed $retryApproveOk -Detail (($retryApprove.Output | Out-String).Trim())
        if (-not $retryApproveOk) { $failed++ }
    }

    if (-not [string]::IsNullOrWhiteSpace($retryTaskId)) {
        $retryExecute = Invoke-ModuleCommand `
            -PythonPath $pythonPath `
            -Arguments @('execute-task', '--task-id', $retryTaskId) `
            -EnvOverrides @{ SUPER_AGENT_DESKTOP_TEST_FAIL_ACTIONS = 'focus_window' }
        $retryExecuteOk = $retryExecute.ExitCode -eq 0 -and (($retryExecute.Output | Out-String) -match 'status:\s+failed')
        Write-Check -Name 'Seed retry-limit execution' -Passed $retryExecuteOk -Detail (($retryExecute.Output | Out-String).Trim())
        if (-not $retryExecuteOk) { $failed++ }

        $retryTaskDetail = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/tasks/item?taskId=$retryTaskId" -Method Get -TimeoutSec 30
        $retryTaskDetailOk = $retryTaskDetail.ok -and `
            $retryTaskDetail.summary.status -eq 'failed' -and `
            $retryTaskDetail.summary.lastAttemptCount -eq 2 -and `
            $retryTaskDetail.summary.retryLimit -eq 2 -and `
            $retryTaskDetail.summary.lastFailureReason -match 'Failed after 2 attempt'
        Write-Check -Name 'Task detail shows retry limit and failure reason' -Passed $retryTaskDetailOk -Detail ($(if ($retryTaskDetailOk) { $retryTaskDetail.summary.lastFailureReason } else { 'retry-limit fields missing from dashboard task detail' }))
        if (-not $retryTaskDetailOk) { $failed++ }
    }

    Start-Sleep -Milliseconds 1200

    $desktopFocusPayload = @{
        actionType = 'focus_window'
        target = 'terminal'
    } | ConvertTo-Json
    $desktopFocusQueue = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/executor/queue" -Method Post -ContentType 'application/json' -Body $desktopFocusPayload -TimeoutSec 30
    $desktopFocusQueueOk = $desktopFocusQueue.ok -and `
        $desktopFocusQueue.localOnly -and `
        $desktopFocusQueue.task.status -eq 'pending_approval' -and `
        $desktopFocusQueue.task.executorActionType -eq 'focus_window'
    Write-Check -Name 'Desktop focus_window queue endpoint' -Passed $desktopFocusQueueOk -Detail ($(if ($desktopFocusQueueOk) { $desktopFocusQueue.summary.headline } else { 'desktop focus_window queue failed' }))
    if (-not $desktopFocusQueueOk) { $failed++ }

    $desktopFocusTaskId = $desktopFocusQueue.summary.taskId
    $desktopFocusApprovalId = if ($null -ne $desktopFocusQueue.task) { $desktopFocusQueue.task.approvalRequestId } else { $null }
    $desktopFocusIdsOk = (-not [string]::IsNullOrWhiteSpace($desktopFocusTaskId)) -and (-not [string]::IsNullOrWhiteSpace($desktopFocusApprovalId)) -and ($desktopFocusApprovalId -ne 'none')
    Write-Check -Name 'Desktop focus_window ids returned' -Passed $desktopFocusIdsOk -Detail ($(if ($desktopFocusIdsOk) { "$desktopFocusTaskId | $desktopFocusApprovalId" } else { 'desktop focus_window ids missing' }))
    if (-not $desktopFocusIdsOk) { $failed++ }

    if ($desktopFocusIdsOk) {
        $desktopFocusApprovePayload = @{
            approvalId = $desktopFocusApprovalId
            decision = 'approve'
            note = 'dashboard checker approved focus_window'
        } | ConvertTo-Json
        $desktopFocusApprove = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/approvals/decision" -Method Post -ContentType 'application/json' -Body $desktopFocusApprovePayload -TimeoutSec 30
        $desktopFocusApproveOk = $desktopFocusApprove.ok -and $desktopFocusApprove.approval.status -eq 'approved'
        Write-Check -Name 'Desktop focus_window approval endpoint' -Passed $desktopFocusApproveOk -Detail ($(if ($desktopFocusApproveOk) { $desktopFocusApprove.summary.headline } else { 'desktop focus_window approval failed' }))
        if (-not $desktopFocusApproveOk) { $failed++ }

        $desktopFocusExecutePayload = @{
            taskId = $desktopFocusTaskId
            action = 'execute'
        } | ConvertTo-Json
        $desktopFocusExecute = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/tasks/action" -Method Post -ContentType 'application/json' -Body $desktopFocusExecutePayload -TimeoutSec 30
        $desktopFocusExecuteOk = $desktopFocusExecute.ok -and (`
            ((`
                $desktopFocusExecute.task.status -eq 'completed' -and `
                $desktopFocusExecute.task.lastExecutionStatus -eq 'succeeded'`
            ) -or (`
                $desktopFocusExecute.task.status -eq 'blocked_human_needed' -and `
                $desktopFocusExecute.task.lastExecutionStatus -eq 'failed' -and `
                ($desktopFocusExecute.summary.headline -match 'manual operator focus' -or `
                 $desktopFocusExecute.summary.headline -match 'manual target resolution is required')`
            )))
        Write-Check -Name 'Desktop focus_window execution endpoint' -Passed $desktopFocusExecuteOk -Detail ($(if ($desktopFocusExecuteOk) { $desktopFocusExecute.summary.headline } else { 'desktop focus_window execute failed' }))
        if (-not $desktopFocusExecuteOk) { $failed++ }
    }

    Remove-GeneratedFile -Path $desktopArtifactPath
    $desktopScreenshotPayload = @{
        actionType = 'capture_desktop_screenshot'
        target = '05_logs/tmp/desktop/dashboard-desktop-check.png'
    } | ConvertTo-Json
    $desktopScreenshotQueue = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/executor/queue" -Method Post -ContentType 'application/json' -Body $desktopScreenshotPayload -TimeoutSec 30
    $desktopScreenshotQueueOk = $desktopScreenshotQueue.ok -and `
        $desktopScreenshotQueue.localOnly -and `
        $desktopScreenshotQueue.task.status -eq 'pending_approval' -and `
        $desktopScreenshotQueue.task.executorActionType -eq 'capture_desktop_screenshot'
    Write-Check -Name 'Desktop screenshot queue endpoint' -Passed $desktopScreenshotQueueOk -Detail ($(if ($desktopScreenshotQueueOk) { $desktopScreenshotQueue.summary.headline } else { 'desktop screenshot queue failed' }))
    if (-not $desktopScreenshotQueueOk) { $failed++ }

    $desktopScreenshotTaskId = $desktopScreenshotQueue.summary.taskId
    $desktopScreenshotApprovalId = if ($null -ne $desktopScreenshotQueue.task) { $desktopScreenshotQueue.task.approvalRequestId } else { $null }
    $desktopScreenshotIdsOk = (-not [string]::IsNullOrWhiteSpace($desktopScreenshotTaskId)) -and (-not [string]::IsNullOrWhiteSpace($desktopScreenshotApprovalId)) -and ($desktopScreenshotApprovalId -ne 'none')
    Write-Check -Name 'Desktop screenshot ids returned' -Passed $desktopScreenshotIdsOk -Detail ($(if ($desktopScreenshotIdsOk) { "$desktopScreenshotTaskId | $desktopScreenshotApprovalId" } else { 'desktop screenshot ids missing' }))
    if (-not $desktopScreenshotIdsOk) { $failed++ }

    if ($desktopScreenshotIdsOk) {
        $desktopScreenshotApprovePayload = @{
            approvalId = $desktopScreenshotApprovalId
            decision = 'approve'
            note = 'dashboard checker approved desktop screenshot'
        } | ConvertTo-Json
        $desktopScreenshotApprove = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/approvals/decision" -Method Post -ContentType 'application/json' -Body $desktopScreenshotApprovePayload -TimeoutSec 30
        $desktopScreenshotApproveOk = $desktopScreenshotApprove.ok -and $desktopScreenshotApprove.approval.status -eq 'approved'
        Write-Check -Name 'Desktop screenshot approval endpoint' -Passed $desktopScreenshotApproveOk -Detail ($(if ($desktopScreenshotApproveOk) { $desktopScreenshotApprove.summary.headline } else { 'desktop screenshot approval failed' }))
        if (-not $desktopScreenshotApproveOk) { $failed++ }

        $desktopScreenshotExecutePayload = @{
            taskId = $desktopScreenshotTaskId
            action = 'execute'
        } | ConvertTo-Json
        $desktopScreenshotExecute = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/tasks/action" -Method Post -ContentType 'application/json' -Body $desktopScreenshotExecutePayload -TimeoutSec 30
        $desktopScreenshotExecuteOk = $desktopScreenshotExecute.ok -and (`
            ((`
                $desktopScreenshotExecute.task.status -eq 'completed' -and `
                $desktopScreenshotExecute.task.lastExecutionStatus -eq 'succeeded' -and `
                (Test-Path -LiteralPath $desktopArtifactPath -PathType Leaf)`
            ) -or (`
                $desktopScreenshotExecute.task.status -eq 'blocked_human_needed' -and `
                $desktopScreenshotExecute.task.lastExecutionStatus -eq 'failed' -and `
                $desktopScreenshotExecute.summary.headline -match 'manual screenshot is required'`
            )))
        Write-Check -Name 'Desktop screenshot execution endpoint' -Passed $desktopScreenshotExecuteOk -Detail ($(if ($desktopScreenshotExecuteOk) { $desktopScreenshotExecute.summary.headline } else { 'desktop screenshot execute failed' }))
        if (-not $desktopScreenshotExecuteOk) { $failed++ }

        $desktopScreenshotDetail = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/tasks/item?taskId=$desktopScreenshotTaskId" -Method Get -TimeoutSec 30
        $desktopScreenshotDetailOk = $desktopScreenshotDetail.ok -and (`
            ((`
                $desktopScreenshotDetail.summary.lastExecutionStatus -eq 'succeeded' -and `
                $desktopScreenshotDetail.summary.lastArtifactPath -eq $desktopArtifactPath`
            ) -or (`
                $desktopScreenshotDetail.summary.status -eq 'blocked_human_needed' -and `
                $desktopScreenshotDetail.summary.lastExecutionStatus -eq 'failed' -and `
                $desktopScreenshotDetail.summary.lastExecutionSummary -match 'manual screenshot is required'`
            )))
        Write-Check -Name 'Desktop screenshot result persists in task detail' -Passed $desktopScreenshotDetailOk -Detail ($(if ($desktopScreenshotDetailOk) { $desktopScreenshotDetail.summary.lastExecutionSummary } else { 'desktop screenshot result not persisted' }))
        if (-not $desktopScreenshotDetailOk) { $failed++ }
    }

    $desktopSetClipboardPayload = @{
        actionType = 'set_clipboard_text'
        content = 'dashboard-desktop-clipboard-check'
    } | ConvertTo-Json
    $desktopSetClipboardQueue = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/executor/queue" -Method Post -ContentType 'application/json' -Body $desktopSetClipboardPayload -TimeoutSec 30
    $desktopSetClipboardQueueOk = $desktopSetClipboardQueue.ok -and `
        $desktopSetClipboardQueue.localOnly -and `
        $desktopSetClipboardQueue.task.status -eq 'pending_approval' -and `
        $desktopSetClipboardQueue.task.executorActionType -eq 'set_clipboard_text'
    Write-Check -Name 'Desktop set_clipboard_text queue endpoint' -Passed $desktopSetClipboardQueueOk -Detail ($(if ($desktopSetClipboardQueueOk) { $desktopSetClipboardQueue.summary.headline } else { 'desktop set_clipboard_text queue failed' }))
    if (-not $desktopSetClipboardQueueOk) { $failed++ }

    $desktopSetClipboardTaskId = $desktopSetClipboardQueue.summary.taskId
    $desktopSetClipboardApprovalId = if ($null -ne $desktopSetClipboardQueue.task) { $desktopSetClipboardQueue.task.approvalRequestId } else { $null }
    $desktopSetClipboardIdsOk = (-not [string]::IsNullOrWhiteSpace($desktopSetClipboardTaskId)) -and (-not [string]::IsNullOrWhiteSpace($desktopSetClipboardApprovalId)) -and ($desktopSetClipboardApprovalId -ne 'none')
    Write-Check -Name 'Desktop set_clipboard_text ids returned' -Passed $desktopSetClipboardIdsOk -Detail ($(if ($desktopSetClipboardIdsOk) { "$desktopSetClipboardTaskId | $desktopSetClipboardApprovalId" } else { 'desktop set_clipboard_text ids missing' }))
    if (-not $desktopSetClipboardIdsOk) { $failed++ }

    if ($desktopSetClipboardIdsOk) {
        $desktopSetClipboardApprovePayload = @{
            approvalId = $desktopSetClipboardApprovalId
            decision = 'approve'
            note = 'dashboard checker approved set_clipboard_text'
        } | ConvertTo-Json
        $desktopSetClipboardApprove = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/approvals/decision" -Method Post -ContentType 'application/json' -Body $desktopSetClipboardApprovePayload -TimeoutSec 30
        $desktopSetClipboardApproveOk = $desktopSetClipboardApprove.ok -and $desktopSetClipboardApprove.approval.status -eq 'approved'
        Write-Check -Name 'Desktop set_clipboard_text approval endpoint' -Passed $desktopSetClipboardApproveOk -Detail ($(if ($desktopSetClipboardApproveOk) { $desktopSetClipboardApprove.summary.headline } else { 'desktop set_clipboard_text approval failed' }))
        if (-not $desktopSetClipboardApproveOk) { $failed++ }

        $desktopSetClipboardExecutePayload = @{
            taskId = $desktopSetClipboardTaskId
            action = 'execute'
        } | ConvertTo-Json
        $desktopSetClipboardExecute = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/tasks/action" -Method Post -ContentType 'application/json' -Body $desktopSetClipboardExecutePayload -TimeoutSec 30
        $desktopSetClipboardExecuteOk = $desktopSetClipboardExecute.ok -and `
            $desktopSetClipboardExecute.task.status -eq 'completed' -and `
            $desktopSetClipboardExecute.task.lastExecutionStatus -eq 'succeeded'
        Write-Check -Name 'Desktop set_clipboard_text execution endpoint' -Passed $desktopSetClipboardExecuteOk -Detail ($(if ($desktopSetClipboardExecuteOk) { $desktopSetClipboardExecute.summary.headline } else { 'desktop set_clipboard_text execute failed' }))
        if (-not $desktopSetClipboardExecuteOk) { $failed++ }
    }

    $desktopReadClipboardPayload = @{
        actionType = 'get_clipboard_text'
    } | ConvertTo-Json
    $desktopReadClipboardQueue = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/executor/queue" -Method Post -ContentType 'application/json' -Body $desktopReadClipboardPayload -TimeoutSec 30
    $desktopReadClipboardQueueOk = $desktopReadClipboardQueue.ok -and `
        $desktopReadClipboardQueue.localOnly -and `
        $desktopReadClipboardQueue.task.status -eq 'queued' -and `
        $desktopReadClipboardQueue.task.executorActionType -eq 'get_clipboard_text'
    Write-Check -Name 'Desktop get_clipboard_text queue endpoint' -Passed $desktopReadClipboardQueueOk -Detail ($(if ($desktopReadClipboardQueueOk) { $desktopReadClipboardQueue.summary.headline } else { 'desktop get_clipboard_text queue failed' }))
    if (-not $desktopReadClipboardQueueOk) { $failed++ }

    $desktopReadClipboardTaskId = $desktopReadClipboardQueue.summary.taskId
    $desktopReadClipboardTaskIdOk = -not [string]::IsNullOrWhiteSpace($desktopReadClipboardTaskId)
    Write-Check -Name 'Desktop get_clipboard_text task id returned' -Passed $desktopReadClipboardTaskIdOk -Detail ($(if ($desktopReadClipboardTaskIdOk) { $desktopReadClipboardTaskId } else { 'desktop get_clipboard_text task id missing' }))
    if (-not $desktopReadClipboardTaskIdOk) { $failed++ }

    if ($desktopReadClipboardTaskIdOk) {
        $desktopReadClipboardExecutePayload = @{
            taskId = $desktopReadClipboardTaskId
            action = 'execute'
        } | ConvertTo-Json
        $desktopReadClipboardExecute = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/tasks/action" -Method Post -ContentType 'application/json' -Body $desktopReadClipboardExecutePayload -TimeoutSec 30
        $desktopReadClipboardExecuteOk = $desktopReadClipboardExecute.ok -and `
            $desktopReadClipboardExecute.task.status -eq 'completed' -and `
            $desktopReadClipboardExecute.task.lastExecutionStatus -eq 'succeeded'
        Write-Check -Name 'Desktop get_clipboard_text execution endpoint' -Passed $desktopReadClipboardExecuteOk -Detail ($(if ($desktopReadClipboardExecuteOk) { $desktopReadClipboardExecute.summary.headline } else { 'desktop get_clipboard_text execute failed' }))
        if (-not $desktopReadClipboardExecuteOk) { $failed++ }

        $desktopReadClipboardDetail = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/tasks/item?taskId=$desktopReadClipboardTaskId" -Method Get -TimeoutSec 30
        $desktopReadClipboardDetailOk = $desktopReadClipboardDetail.ok -and `
            $desktopReadClipboardDetail.summary.lastExecutionSummary -match 'Read clipboard text'
        Write-Check -Name 'Desktop get_clipboard_text result persists in task detail' -Passed $desktopReadClipboardDetailOk -Detail ($(if ($desktopReadClipboardDetailOk) { $desktopReadClipboardDetail.summary.lastExecutionSummary } else { 'desktop clipboard read result not persisted' }))
        if (-not $desktopReadClipboardDetailOk) { $failed++ }
    }

    $desktopHotkeyPayload = @{
        actionType = 'send_hotkey'
        target = 'terminal|ctrl+v'
    } | ConvertTo-Json
    $desktopHotkeyQueue = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/executor/queue" -Method Post -ContentType 'application/json' -Body $desktopHotkeyPayload -TimeoutSec 30
    $desktopHotkeyQueueOk = $desktopHotkeyQueue.ok -and `
        $desktopHotkeyQueue.localOnly -and `
        $desktopHotkeyQueue.task.status -eq 'pending_approval' -and `
        $desktopHotkeyQueue.task.executorActionType -eq 'send_hotkey'
    Write-Check -Name 'Desktop send_hotkey queue endpoint' -Passed $desktopHotkeyQueueOk -Detail ($(if ($desktopHotkeyQueueOk) { $desktopHotkeyQueue.summary.headline } else { 'desktop send_hotkey queue failed' }))
    if (-not $desktopHotkeyQueueOk) { $failed++ }

    $desktopHotkeyTaskId = $desktopHotkeyQueue.summary.taskId
    $desktopHotkeyApprovalId = if ($null -ne $desktopHotkeyQueue.task) { $desktopHotkeyQueue.task.approvalRequestId } else { $null }
    $desktopHotkeyIdsOk = (-not [string]::IsNullOrWhiteSpace($desktopHotkeyTaskId)) -and (-not [string]::IsNullOrWhiteSpace($desktopHotkeyApprovalId)) -and ($desktopHotkeyApprovalId -ne 'none')
    Write-Check -Name 'Desktop send_hotkey ids returned' -Passed $desktopHotkeyIdsOk -Detail ($(if ($desktopHotkeyIdsOk) { "$desktopHotkeyTaskId | $desktopHotkeyApprovalId" } else { 'desktop send_hotkey ids missing' }))
    if (-not $desktopHotkeyIdsOk) { $failed++ }

    if ($desktopHotkeyIdsOk) {
        $desktopHotkeyApprovePayload = @{
            approvalId = $desktopHotkeyApprovalId
            decision = 'approve'
            note = 'dashboard checker approved send_hotkey'
        } | ConvertTo-Json
        $desktopHotkeyApprove = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/approvals/decision" -Method Post -ContentType 'application/json' -Body $desktopHotkeyApprovePayload -TimeoutSec 30
        $desktopHotkeyApproveOk = $desktopHotkeyApprove.ok -and $desktopHotkeyApprove.approval.status -eq 'approved'
        Write-Check -Name 'Desktop send_hotkey approval endpoint' -Passed $desktopHotkeyApproveOk -Detail ($(if ($desktopHotkeyApproveOk) { $desktopHotkeyApprove.summary.headline } else { 'desktop send_hotkey approval failed' }))
        if (-not $desktopHotkeyApproveOk) { $failed++ }

        $desktopHotkeyExecutePayload = @{
            taskId = $desktopHotkeyTaskId
            action = 'execute'
        } | ConvertTo-Json
        $desktopHotkeyExecute = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/tasks/action" -Method Post -ContentType 'application/json' -Body $desktopHotkeyExecutePayload -TimeoutSec 30
        $desktopHotkeyExecuteOk = $desktopHotkeyExecute.ok -and (`
            ((`
                $desktopHotkeyExecute.task.status -eq 'completed' -and `
                $desktopHotkeyExecute.task.lastExecutionStatus -eq 'succeeded'`
            ) -or (`
                ($desktopHotkeyExecute.task.status -eq 'blocked_human_needed' -or `
                 $desktopHotkeyExecute.task.status -eq 'failed') -and `
                $desktopHotkeyExecute.task.lastExecutionStatus -eq 'failed' -and `
                ($desktopHotkeyExecute.summary.headline -match 'manual operator focus' -or `
                 $desktopHotkeyExecute.summary.headline -match 'manual target resolution is required' -or `
                 $desktopHotkeyExecute.summary.headline -match 'Failed after 2 attempt')`
            )))
        Write-Check -Name 'Desktop send_hotkey execution endpoint' -Passed $desktopHotkeyExecuteOk -Detail ($(if ($desktopHotkeyExecuteOk) { $desktopHotkeyExecute.summary.headline } else { 'desktop send_hotkey execute failed' }))
        if (-not $desktopHotkeyExecuteOk) { $failed++ }
    }

    $desktopMoveMousePayload = @{
        actionType = 'move_mouse'
        target = 'terminal|center'
    } | ConvertTo-Json
    $desktopMoveMouseQueue = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/executor/queue" -Method Post -ContentType 'application/json' -Body $desktopMoveMousePayload -TimeoutSec 30
    $desktopMoveMouseQueueOk = $desktopMoveMouseQueue.ok -and `
        $desktopMoveMouseQueue.localOnly -and `
        $desktopMoveMouseQueue.task.status -eq 'pending_approval' -and `
        $desktopMoveMouseQueue.task.executorActionType -eq 'move_mouse'
    Write-Check -Name 'Desktop move_mouse queue endpoint' -Passed $desktopMoveMouseQueueOk -Detail ($(if ($desktopMoveMouseQueueOk) { $desktopMoveMouseQueue.summary.headline } else { 'desktop move_mouse queue failed' }))
    if (-not $desktopMoveMouseQueueOk) { $failed++ }

    $desktopMoveMouseTaskId = $desktopMoveMouseQueue.summary.taskId
    $desktopMoveMouseApprovalId = if ($null -ne $desktopMoveMouseQueue.task) { $desktopMoveMouseQueue.task.approvalRequestId } else { $null }
    $desktopMoveMouseIdsOk = (-not [string]::IsNullOrWhiteSpace($desktopMoveMouseTaskId)) -and (-not [string]::IsNullOrWhiteSpace($desktopMoveMouseApprovalId)) -and ($desktopMoveMouseApprovalId -ne 'none')
    Write-Check -Name 'Desktop move_mouse ids returned' -Passed $desktopMoveMouseIdsOk -Detail ($(if ($desktopMoveMouseIdsOk) { "$desktopMoveMouseTaskId | $desktopMoveMouseApprovalId" } else { 'desktop move_mouse ids missing' }))
    if (-not $desktopMoveMouseIdsOk) { $failed++ }

    if ($desktopMoveMouseIdsOk) {
        $desktopMoveMouseApprovePayload = @{
            approvalId = $desktopMoveMouseApprovalId
            decision = 'approve'
            note = 'dashboard checker approved move_mouse'
        } | ConvertTo-Json
        $desktopMoveMouseApprove = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/approvals/decision" -Method Post -ContentType 'application/json' -Body $desktopMoveMouseApprovePayload -TimeoutSec 30
        $desktopMoveMouseApproveOk = $desktopMoveMouseApprove.ok -and $desktopMoveMouseApprove.approval.status -eq 'approved'
        Write-Check -Name 'Desktop move_mouse approval endpoint' -Passed $desktopMoveMouseApproveOk -Detail ($(if ($desktopMoveMouseApproveOk) { $desktopMoveMouseApprove.summary.headline } else { 'desktop move_mouse approval failed' }))
        if (-not $desktopMoveMouseApproveOk) { $failed++ }

        $desktopMoveMouseExecutePayload = @{
            taskId = $desktopMoveMouseTaskId
            action = 'execute'
        } | ConvertTo-Json
        $desktopMoveMouseExecute = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/tasks/action" -Method Post -ContentType 'application/json' -Body $desktopMoveMouseExecutePayload -TimeoutSec 30
        $desktopMoveMouseExecuteOk = $desktopMoveMouseExecute.ok -and `
            ((`
                $desktopMoveMouseExecute.task.status -eq 'completed' -and `
                $desktopMoveMouseExecute.task.lastExecutionStatus -eq 'succeeded'`
            ) -or (`
                $desktopMoveMouseExecute.task.status -eq 'failed' -and `
                $desktopMoveMouseExecute.task.lastExecutionStatus -eq 'failed' -and `
                $desktopMoveMouseExecute.summary.headline -match 'Failed after 2 attempt|Windows did not place the mouse'`
            ))
        Write-Check -Name 'Desktop move_mouse execution endpoint' -Passed $desktopMoveMouseExecuteOk -Detail ($(if ($desktopMoveMouseExecuteOk) { $desktopMoveMouseExecute.summary.headline } else { 'desktop move_mouse execute failed without a clear safe result' }))
        if (-not $desktopMoveMouseExecuteOk) { $failed++ }
    }

    $desktopLeftClickPayload = @{
        actionType = 'left_click'
        target = 'terminal|center'
    } | ConvertTo-Json
    $desktopLeftClickQueue = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/executor/queue" -Method Post -ContentType 'application/json' -Body $desktopLeftClickPayload -TimeoutSec 30
    $desktopLeftClickQueueOk = $desktopLeftClickQueue.ok -and `
        $desktopLeftClickQueue.localOnly -and `
        $desktopLeftClickQueue.task.status -eq 'pending_approval' -and `
        $desktopLeftClickQueue.task.executorActionType -eq 'left_click'
    Write-Check -Name 'Desktop left_click queue endpoint' -Passed $desktopLeftClickQueueOk -Detail ($(if ($desktopLeftClickQueueOk) { $desktopLeftClickQueue.summary.headline } else { 'desktop left_click queue failed' }))
    if (-not $desktopLeftClickQueueOk) { $failed++ }

    $desktopLeftClickTaskId = $desktopLeftClickQueue.summary.taskId
    $desktopLeftClickApprovalId = if ($null -ne $desktopLeftClickQueue.task) { $desktopLeftClickQueue.task.approvalRequestId } else { $null }
    $desktopLeftClickIdsOk = (-not [string]::IsNullOrWhiteSpace($desktopLeftClickTaskId)) -and (-not [string]::IsNullOrWhiteSpace($desktopLeftClickApprovalId)) -and ($desktopLeftClickApprovalId -ne 'none')
    Write-Check -Name 'Desktop left_click ids returned' -Passed $desktopLeftClickIdsOk -Detail ($(if ($desktopLeftClickIdsOk) { "$desktopLeftClickTaskId | $desktopLeftClickApprovalId" } else { 'desktop left_click ids missing' }))
    if (-not $desktopLeftClickIdsOk) { $failed++ }

    if ($desktopLeftClickIdsOk) {
        $desktopLeftClickApprovePayload = @{
            approvalId = $desktopLeftClickApprovalId
            decision = 'approve'
            note = 'dashboard checker approved left_click'
        } | ConvertTo-Json
        $desktopLeftClickApprove = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/approvals/decision" -Method Post -ContentType 'application/json' -Body $desktopLeftClickApprovePayload -TimeoutSec 30
        $desktopLeftClickApproveOk = $desktopLeftClickApprove.ok -and $desktopLeftClickApprove.approval.status -eq 'approved'
        Write-Check -Name 'Desktop left_click approval endpoint' -Passed $desktopLeftClickApproveOk -Detail ($(if ($desktopLeftClickApproveOk) { $desktopLeftClickApprove.summary.headline } else { 'desktop left_click approval failed' }))
        if (-not $desktopLeftClickApproveOk) { $failed++ }

        $desktopLeftClickExecutePayload = @{
            taskId = $desktopLeftClickTaskId
            action = 'execute'
        } | ConvertTo-Json
        $desktopLeftClickExecute = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/tasks/action" -Method Post -ContentType 'application/json' -Body $desktopLeftClickExecutePayload -TimeoutSec 30
        $desktopLeftClickExecuteOk = $desktopLeftClickExecute.ok -and (`
            ((`
                $desktopLeftClickExecute.task.status -eq 'completed' -and `
                $desktopLeftClickExecute.task.lastExecutionStatus -eq 'succeeded'`
            ) -or (`
                ($desktopLeftClickExecute.task.status -eq 'blocked_human_needed' -or `
                 $desktopLeftClickExecute.task.status -eq 'failed') -and `
                $desktopLeftClickExecute.task.lastExecutionStatus -eq 'failed' -and `
                ($desktopLeftClickExecute.summary.headline -match 'manual operator focus' -or `
                 $desktopLeftClickExecute.summary.headline -match 'Failed after 2 attempt')`
            )))
        Write-Check -Name 'Desktop left_click execution endpoint' -Passed $desktopLeftClickExecuteOk -Detail ($(if ($desktopLeftClickExecuteOk) { $desktopLeftClickExecute.summary.headline } else { 'desktop left_click execute failed' }))
        if (-not $desktopLeftClickExecuteOk) { $failed++ }
    }

    $desktopInterruptSeed = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @(
        'queue-executor-action',
        '--action-type', 'wait_seconds',
        '--target', '5'
    )
    $desktopInterruptSeedOk = $desktopInterruptSeed.ExitCode -eq 0 -and `
        (($desktopInterruptSeed.Output | Out-String) -match 'status:\s+queued') -and `
        (($desktopInterruptSeed.Output | Out-String) -match 'executor_action_type:\s+wait_seconds')
    Write-Check -Name 'Desktop interrupt seed task queued' -Passed $desktopInterruptSeedOk -Detail (($desktopInterruptSeed.Output | Out-String).Trim())
    if (-not $desktopInterruptSeedOk) { $failed++ }

    $desktopInterruptTaskMatch = [regex]::Match(($desktopInterruptSeed.Output | Out-String), 'task_id:\s*(\S+)')
    $desktopInterruptTaskId = if ($desktopInterruptTaskMatch.Success) { $desktopInterruptTaskMatch.Groups[1].Value } else { $null }
    $desktopInterruptTaskOk = -not [string]::IsNullOrWhiteSpace($desktopInterruptTaskId)
    Write-Check -Name 'Desktop interrupt task id returned' -Passed $desktopInterruptTaskOk -Detail ($(if ($desktopInterruptTaskOk) { $desktopInterruptTaskId } else { 'desktop interrupt task id missing' }))
    if (-not $desktopInterruptTaskOk) { $failed++ }

    if ($desktopInterruptTaskOk) {
        $desktopInterruptExecute = Invoke-ModuleCommand `
            -PythonPath $pythonPath `
            -Arguments @('execute-task', '--task-id', $desktopInterruptTaskId) `
            -EnvOverrides @{ SUPER_AGENT_DESKTOP_TEST_INTERRUPT_AFTER_MS = '300' }
        $desktopInterruptExecuteOk = $desktopInterruptExecute.ExitCode -eq 0 -and `
            (($desktopInterruptExecute.Output | Out-String) -match 'status:\s+interrupted') -and `
            (($desktopInterruptExecute.Output | Out-String) -match 'execution_status:\s+interrupted')
        Write-Check -Name 'Desktop interrupt seed executes into interrupted state' -Passed $desktopInterruptExecuteOk -Detail (($desktopInterruptExecute.Output | Out-String).Trim())
        if (-not $desktopInterruptExecuteOk) { $failed++ }

        $supervisorAfterInterrupt = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/supervisor/status" -Method Get -TimeoutSec 30
        $supervisorAfterInterruptOk = $supervisorAfterInterrupt.ok -and `
            $supervisorAfterInterrupt.summary.interruptedTasks.taskId -contains $desktopInterruptTaskId
        Write-Check -Name 'Interrupted desktop task is visible in supervisor status' -Passed $supervisorAfterInterruptOk -Detail ($(if ($supervisorAfterInterruptOk) { $desktopInterruptTaskId } else { 'interrupted desktop task missing from supervisor status' }))
        if (-not $supervisorAfterInterruptOk) { $failed++ }

        $desktopInterruptDetail = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/tasks/item?taskId=$desktopInterruptTaskId" -Method Get -TimeoutSec 30
        $desktopInterruptDetailOk = $desktopInterruptDetail.ok -and `
            $desktopInterruptDetail.summary.status -eq 'interrupted' -and `
            $desktopInterruptDetail.summary.lastExecutionStatus -eq 'interrupted' -and `
            $desktopInterruptDetail.summary.blockedReason -match 'Ctrl\+8'
        Write-Check -Name 'Interrupted desktop task detail shows failsafe reason' -Passed $desktopInterruptDetailOk -Detail ($(if ($desktopInterruptDetailOk) { $desktopInterruptDetail.summary.blockedReason } else { 'interrupted desktop task detail missing failsafe reason' }))
        if (-not $desktopInterruptDetailOk) { $failed++ }
    }

    $recipeQueuePayload = @{
        actionType = 'run_operator_recipe'
        target = 'observe_desktop_state'
    } | ConvertTo-Json
    $recipeQueue = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/executor/queue" -Method Post -ContentType 'application/json' -Body $recipeQueuePayload -TimeoutSec 30
    $recipeQueueOk = $recipeQueue.ok -and `
        $recipeQueue.localOnly -and `
        $recipeQueue.task.status -eq 'queued' -and `
        $recipeQueue.task.approvalState -eq 'not_required' -and `
        $recipeQueue.task.executorActionType -eq 'run_operator_recipe' -and `
        $recipeQueue.task.recipeName -eq 'observe_desktop_state'
    Write-Check -Name 'Operator recipe queue endpoint' -Passed $recipeQueueOk -Detail ($(if ($recipeQueueOk) { $recipeQueue.summary.headline } else { 'operator recipe queue failed' }))
    if (-not $recipeQueueOk) { $failed++ }

    $recipeTaskId = $recipeQueue.summary.taskId
    $recipeTaskIdOk = -not [string]::IsNullOrWhiteSpace($recipeTaskId)
    Write-Check -Name 'Operator recipe task id returned' -Passed $recipeTaskIdOk -Detail ($(if ($recipeTaskIdOk) { $recipeTaskId } else { 'operator recipe task id missing' }))
    if (-not $recipeTaskIdOk) { $failed++ }

    if ($recipeTaskIdOk) {
        $recipeDetail = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/tasks/item?taskId=$recipeTaskId" -Method Get -TimeoutSec 30
        $recipeDetailOk = $recipeDetail.ok -and `
            $recipeDetail.localOnly -and `
            $recipeDetail.summary.recipeName -eq 'observe_desktop_state' -and `
            $recipeDetail.summary.recipeSteps.Count -ge 2
        Write-Check -Name 'Operator recipe detail endpoint' -Passed $recipeDetailOk -Detail ($(if ($recipeDetailOk) { $recipeDetail.summary.headline } else { 'operator recipe detail missing planned steps' }))
        if (-not $recipeDetailOk) { $failed++ }

        $recipeExecutePayload = @{
            taskId = $recipeTaskId
            action = 'execute'
        } | ConvertTo-Json
        $recipeExecute = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/tasks/action" -Method Post -ContentType 'application/json' -Body $recipeExecutePayload -TimeoutSec 30
        $recipeExecuteOk = $recipeExecute.ok -and `
            $recipeExecute.task.status -eq 'completed' -and `
            $recipeExecute.task.lastExecutionStatus -eq 'succeeded'
        Write-Check -Name 'Operator recipe execution endpoint' -Passed $recipeExecuteOk -Detail ($(if ($recipeExecuteOk) { $recipeExecute.summary.headline } else { 'operator recipe execute failed' }))
        if (-not $recipeExecuteOk) { $failed++ }

        $recipeDetailAfter = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/tasks/item?taskId=$recipeTaskId" -Method Get -TimeoutSec 30
        $recipeDetailAfterOk = $recipeDetailAfter.ok -and `
            $recipeDetailAfter.summary.recipeStatus -eq 'succeeded' -and `
            $recipeDetailAfter.summary.recipeLastRunSteps.Count -ge 2 -and `
            $recipeDetailAfter.summary.recipeRunHistory.Count -ge 1
        Write-Check -Name 'Operator recipe result persists in dashboard detail' -Passed $recipeDetailAfterOk -Detail ($(if ($recipeDetailAfterOk) { $recipeDetailAfter.summary.recipeSummary } else { 'operator recipe result history not persisted in dashboard detail' }))
        if (-not $recipeDetailAfterOk) { $failed++ }
    }

    $handoffSeedPayload = @{
        actionType = 'set_clipboard_text'
        content = 'ghoti dashboard handoff payload'
    } | ConvertTo-Json -Compress
    $handoffSeedQueue = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/executor/queue" -Method Post -ContentType 'application/json' -Body $handoffSeedPayload -TimeoutSec 30
    $handoffSeedQueueOk = $handoffSeedQueue.ok -and `
        $handoffSeedQueue.task.status -eq 'pending_approval' -and `
        $handoffSeedQueue.task.executorActionType -eq 'set_clipboard_text'
    Write-Check -Name 'Dashboard handoff safe clipboard seed queue endpoint' -Passed $handoffSeedQueueOk -Detail ($(if ($handoffSeedQueueOk) { $handoffSeedQueue.summary.headline } else { 'handoff safe clipboard seed queue failed' }))
    if (-not $handoffSeedQueueOk) { $failed++ }

    $handoffSeedTaskId = $handoffSeedQueue.summary.taskId
    $handoffSeedApprovalId = $handoffSeedQueue.task.approvalRequestId
    if (-not [string]::IsNullOrWhiteSpace($handoffSeedApprovalId)) {
        $handoffSeedApprovePayload = @{
            approvalId = $handoffSeedApprovalId
            decision = 'approve'
            note = 'dashboard checker approved safe handoff clipboard seed'
        } | ConvertTo-Json -Compress
        $handoffSeedApprove = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/approvals/decision" -Method Post -ContentType 'application/json' -Body $handoffSeedApprovePayload -TimeoutSec 30
        $handoffSeedApproveOk = $handoffSeedApprove.ok -and $handoffSeedApprove.approval.status -eq 'approved'
        Write-Check -Name 'Dashboard handoff safe clipboard seed approval endpoint' -Passed $handoffSeedApproveOk -Detail ($(if ($handoffSeedApproveOk) { $handoffSeedApprove.summary.headline } else { 'handoff safe clipboard seed approval failed' }))
        if (-not $handoffSeedApproveOk) { $failed++ }
    }

    if (-not [string]::IsNullOrWhiteSpace($handoffSeedTaskId)) {
        $handoffSeedExecutePayload = @{
            taskId = $handoffSeedTaskId
            action = 'execute'
        } | ConvertTo-Json -Compress
        $handoffSeedExecute = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/tasks/action" -Method Post -ContentType 'application/json' -Body $handoffSeedExecutePayload -TimeoutSec 30
        $handoffSeedExecuteOk = $handoffSeedExecute.ok -and $handoffSeedExecute.task.status -eq 'completed'
        Write-Check -Name 'Dashboard handoff safe clipboard seed execution endpoint' -Passed $handoffSeedExecuteOk -Detail ($(if ($handoffSeedExecuteOk) { $handoffSeedExecute.summary.headline } else { 'handoff safe clipboard seed execution failed' }))
        if (-not $handoffSeedExecuteOk) { $failed++ }
    }

    $handoffUiHtmlPath = Join-Path $projectRoot 'public\index.html'
    $handoffUiHtml = if (Test-Path $handoffUiHtmlPath) { Get-Content $handoffUiHtmlPath -Raw } else { '' }
    $handoffUiTargetsOk = -not [string]::IsNullOrWhiteSpace($handoffUiHtml) -and `
        $handoffUiHtml -match '(?s)<select id="handoff-source-window">.*?<option value="codex"' -and `
        $handoffUiHtml -match '(?s)<select id="handoff-target-window">.*?<option value="chatgpt"' -and `
        $handoffUiHtml -notmatch '(?s)<select id="handoff-source-window">.*?<option value="terminal"' -and `
        $handoffUiHtml -notmatch '(?s)<select id="handoff-target-window">.*?<option value="terminal"'
    Write-Check -Name 'Dashboard handoff UI does not expose terminal fallback targets' -Passed $handoffUiTargetsOk -Detail ($(if ($handoffUiTargetsOk) { 'handoff source and target controls only expose Codex and ChatGPT for this recipe' } else { 'handoff UI still exposes terminal fallback targets' }))
    if (-not $handoffUiTargetsOk) { $failed++ }

    $handoffTargetCandidates = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/desktop-bridge/handoff-targets" -Method Get -TimeoutSec 30
    $handoffTargetCandidatesOk = $handoffTargetCandidates.ok -and `
        $handoffTargetCandidates.summary.codexCandidates.Count -eq 1 -and `
        $handoffTargetCandidates.summary.chatgptCandidates.Count -eq 2 -and `
        ($handoffTargetCandidates.summary.codexCandidates.candidateId -contains 'pid:1201') -and `
        ($handoffTargetCandidates.summary.chatgptCandidates.candidateId -contains 'pid:2202') -and `
        ($handoffTargetCandidates.summary.chatgptCandidates.candidateId -contains 'pid:2203')
    Write-Check -Name 'Dashboard handoff target candidate endpoint lists real-window matches' -Passed $handoffTargetCandidatesOk -Detail ($(if ($handoffTargetCandidatesOk) { 'codex and chatgpt candidates loaded from deterministic fixtures' } else { 'handoff target candidates missing or incomplete' }))
    if (-not $handoffTargetCandidatesOk) { $failed++ }

    $handoffCandidateUiOk = -not [string]::IsNullOrWhiteSpace($handoffUiHtml) -and `
        $handoffUiHtml -match 'handoff-source-candidate' -and `
        $handoffUiHtml -match 'handoff-target-candidate' -and `
        $handoffUiHtml -match 'refresh-handoff-targets'
    Write-Check -Name 'Dashboard handoff UI exposes manual target candidate controls' -Passed $handoffCandidateUiOk -Detail ($(if ($handoffCandidateUiOk) { 'manual handoff candidate controls found in dashboard HTML' } else { 'handoff candidate controls missing from dashboard HTML' }))
    if (-not $handoffCandidateUiOk) { $failed++ }

    $handoffManualCandidatePayload = @{
        actionType = 'run_operator_recipe'
        target = 'codex_to_chatgpt_handoff_mvp'
        content = '{"sourceWindow":"codex","targetWindow":"chatgpt","sourceWindowCandidateId":"pid:1201","targetWindowCandidateId":"pid:2202","usePreparedClipboard":true,"waitSeconds":0}'
    } | ConvertTo-Json -Compress
    $handoffManualCandidateQueue = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/executor/queue" -Method Post -ContentType 'application/json' -Body $handoffManualCandidatePayload -TimeoutSec 30
    $handoffManualCandidateQueueOk = $handoffManualCandidateQueue.ok -and `
        $handoffManualCandidateQueue.task.status -eq 'pending_approval' -and `
        $handoffManualCandidateQueue.task.recipeName -eq 'codex_to_chatgpt_handoff_mvp'
    Write-Check -Name 'Dashboard handoff manual-candidate queue endpoint' -Passed $handoffManualCandidateQueueOk -Detail ($(if ($handoffManualCandidateQueueOk) { $handoffManualCandidateQueue.summary.headline } else { 'manual-candidate handoff queue failed' }))
    if (-not $handoffManualCandidateQueueOk) { $failed++ }

    $handoffManualCandidateTaskId = $handoffManualCandidateQueue.summary.taskId
    if (-not [string]::IsNullOrWhiteSpace($handoffManualCandidateTaskId)) {
        $handoffManualCandidateDetail = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/tasks/item?taskId=$handoffManualCandidateTaskId" -Method Get -TimeoutSec 30
        $handoffManualCandidateDetailOk = $handoffManualCandidateDetail.ok -and `
            $handoffManualCandidateDetail.summary.recipeSourceWindowCandidateId -eq 'pid:1201' -and `
            $handoffManualCandidateDetail.summary.recipeTargetWindowCandidateId -eq 'pid:2202' -and `
            $handoffManualCandidateDetail.summary.handoffSourceSelectionMode -eq 'manual_candidate_selected' -and `
            $handoffManualCandidateDetail.summary.handoffTargetSelectionMode -eq 'manual_candidate_selected'
        Write-Check -Name 'Dashboard handoff detail shows manual target selection metadata' -Passed $handoffManualCandidateDetailOk -Detail ($(if ($handoffManualCandidateDetailOk) { $handoffManualCandidateDetail.summary.recipeSummary } else { 'manual target selection detail missing from handoff task' }))
        if (-not $handoffManualCandidateDetailOk) { $failed++ }
    }

    $handoffRecipePayload = @{
        actionType = 'run_operator_recipe'
        target = 'codex_to_chatgpt_handoff_mvp'
        content = '{"sourceWindow":"codex","targetWindow":"chatgpt","usePreparedClipboard":true,"waitSeconds":1}'
    } | ConvertTo-Json -Compress
    $handoffRecipeQueue = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/executor/queue" -Method Post -ContentType 'application/json' -Body $handoffRecipePayload -TimeoutSec 30
    $handoffRecipeQueueOk = $handoffRecipeQueue.ok -and `
        $handoffRecipeQueue.task.status -eq 'pending_approval' -and `
        $handoffRecipeQueue.task.recipeName -eq 'codex_to_chatgpt_handoff_mvp' -and `
        $handoffRecipeQueue.task.recipeSourceWindow -eq 'codex' -and `
        $handoffRecipeQueue.task.recipeTargetWindow -eq 'chatgpt' -and `
        $handoffRecipeQueue.task.handoffSendBehavior -eq 'paste_only' -and `
        $handoffRecipeQueue.task.handoffFallbackDenied -eq 'terminal_shell_fallback_blocked'
    Write-Check -Name 'Dashboard Codex to ChatGPT handoff queue endpoint' -Passed $handoffRecipeQueueOk -Detail ($(if ($handoffRecipeQueueOk) { $handoffRecipeQueue.summary.headline } else { 'handoff recipe queue failed' }))
    if (-not $handoffRecipeQueueOk) { $failed++ }

    $handoffRecipeTaskId = $handoffRecipeQueue.summary.taskId
    $handoffRecipeApprovalId = $handoffRecipeQueue.task.approvalRequestId
    if (-not [string]::IsNullOrWhiteSpace($handoffRecipeTaskId)) {
        $handoffRecipeDetailBefore = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/tasks/item?taskId=$handoffRecipeTaskId" -Method Get -TimeoutSec 30
        $handoffRecipeDetailBeforeOk = $handoffRecipeDetailBefore.ok -and `
            $handoffRecipeDetailBefore.summary.recipeClipboardMode -eq 'prepared_clipboard' -and `
            $handoffRecipeDetailBefore.summary.recipeSourceWindow -eq 'codex' -and `
            $handoffRecipeDetailBefore.summary.recipeTargetWindow -eq 'chatgpt' -and `
            $handoffRecipeDetailBefore.summary.handoffSendBehavior -eq 'paste_only' -and `
            $handoffRecipeDetailBefore.summary.handoffFallbackDenied -eq 'terminal_shell_fallback_blocked' -and `
            (-not ($handoffRecipeDetailBefore.summary.recipeSteps.actionType -contains 'send_hotkey'))
        Write-Check -Name 'Dashboard Codex to ChatGPT handoff defaults to paste-only with strict targets' -Passed $handoffRecipeDetailBeforeOk -Detail ($(if ($handoffRecipeDetailBeforeOk) { $handoffRecipeDetailBefore.summary.recipeSummary } else { 'handoff detail did not show strict paste-only default' }))
        if (-not $handoffRecipeDetailBeforeOk) { $failed++ }
    }

    if (-not [string]::IsNullOrWhiteSpace($handoffRecipeApprovalId)) {
        $handoffRecipeApprovePayload = @{
            approvalId = $handoffRecipeApprovalId
            decision = 'approve'
            note = 'dashboard checker approved safe handoff recipe'
        } | ConvertTo-Json -Compress
        $handoffRecipeApprove = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/approvals/decision" -Method Post -ContentType 'application/json' -Body $handoffRecipeApprovePayload -TimeoutSec 30
        $handoffRecipeApproveOk = $handoffRecipeApprove.ok -and $handoffRecipeApprove.approval.status -eq 'approved'
        Write-Check -Name 'Dashboard Codex to ChatGPT handoff approval endpoint' -Passed $handoffRecipeApproveOk -Detail ($(if ($handoffRecipeApproveOk) { $handoffRecipeApprove.summary.headline } else { 'handoff approval failed' }))
        if (-not $handoffRecipeApproveOk) { $failed++ }
    }

    if (-not [string]::IsNullOrWhiteSpace($handoffRecipeTaskId)) {
        $handoffRecipeExecutePayload = @{
            taskId = $handoffRecipeTaskId
            action = 'execute'
        } | ConvertTo-Json -Compress
        $handoffRecipeExecute = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/tasks/action" -Method Post -ContentType 'application/json' -Body $handoffRecipeExecutePayload -TimeoutSec 30
        $handoffRecipeExecuteOk = $handoffRecipeExecute.ok -and `
            $handoffRecipeExecute.task.status -eq 'blocked_human_needed' -and `
            $handoffRecipeExecute.task.lastExecutionStatus -eq 'failed'
        Write-Check -Name 'Dashboard Codex to ChatGPT handoff blocks safely when real target matching is ambiguous' -Passed $handoffRecipeExecuteOk -Detail ($(if ($handoffRecipeExecuteOk) { $handoffRecipeExecute.summary.headline } else { 'handoff execution did not stop for manual target resolution' }))
        if (-not $handoffRecipeExecuteOk) { $failed++ }

        $handoffRecipeDetailAfter = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/tasks/item?taskId=$handoffRecipeTaskId" -Method Get -TimeoutSec 30
        $handoffRecipeDetailAfterOk = $handoffRecipeDetailAfter.ok -and `
            $handoffRecipeDetailAfter.summary.recipeStatus -eq 'blocked' -and `
            $handoffRecipeDetailAfter.summary.handoffPayloadClassification -eq 'valid_handoff_text' -and `
            $handoffRecipeDetailAfter.summary.handoffPasteAllowed -eq 'no' -and `
            $handoffRecipeDetailAfter.summary.handoffTargetResolutionStatus -eq 'manual_target_resolution_required' -and `
            $handoffRecipeDetailAfter.summary.handoffManualTargetResolution -eq 'required' -and `
            $handoffRecipeDetailAfter.summary.handoffFallbackDenied -eq 'yes' -and `
            $handoffRecipeDetailAfter.summary.handoffTargetSelectionMode -eq 'manual_selection_required'
        Write-Check -Name 'Dashboard handoff detail keeps manual target resolution state and denies terminal fallback' -Passed $handoffRecipeDetailAfterOk -Detail ($(if ($handoffRecipeDetailAfterOk) { $handoffRecipeDetailAfter.summary.recipeSummary } else { 'handoff detail missing safe payload or manual target resolution state' }))
        if (-not $handoffRecipeDetailAfterOk) { $failed++ }
    }

    $handoffBadSeedPayload = @{
        actionType = 'set_clipboard_text'
        content = 'Run Desktop Bridge Check'
    } | ConvertTo-Json -Compress
    $handoffBadSeedQueue = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/executor/queue" -Method Post -ContentType 'application/json' -Body $handoffBadSeedPayload -TimeoutSec 30
    $handoffBadSeedQueueOk = $handoffBadSeedQueue.ok -and $handoffBadSeedQueue.task.status -eq 'pending_approval'
    Write-Check -Name 'Dashboard handoff bad clipboard seed queue endpoint' -Passed $handoffBadSeedQueueOk -Detail ($(if ($handoffBadSeedQueueOk) { $handoffBadSeedQueue.summary.headline } else { 'handoff bad clipboard seed queue failed' }))
    if (-not $handoffBadSeedQueueOk) { $failed++ }

    $handoffBadSeedTaskId = $handoffBadSeedQueue.summary.taskId
    $handoffBadSeedApprovalId = $handoffBadSeedQueue.task.approvalRequestId
    if (-not [string]::IsNullOrWhiteSpace($handoffBadSeedApprovalId)) {
        $handoffBadSeedApprovePayload = @{
            approvalId = $handoffBadSeedApprovalId
            decision = 'approve'
            note = 'dashboard checker approved suspicious handoff clipboard seed'
        } | ConvertTo-Json -Compress
        $handoffBadSeedApprove = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/approvals/decision" -Method Post -ContentType 'application/json' -Body $handoffBadSeedApprovePayload -TimeoutSec 30
        $handoffBadSeedApproveOk = $handoffBadSeedApprove.ok -and $handoffBadSeedApprove.approval.status -eq 'approved'
        Write-Check -Name 'Dashboard handoff bad clipboard seed approval endpoint' -Passed $handoffBadSeedApproveOk -Detail ($(if ($handoffBadSeedApproveOk) { $handoffBadSeedApprove.summary.headline } else { 'handoff bad clipboard seed approval failed' }))
        if (-not $handoffBadSeedApproveOk) { $failed++ }
    }

    if (-not [string]::IsNullOrWhiteSpace($handoffBadSeedTaskId)) {
        $handoffBadSeedExecutePayload = @{
            taskId = $handoffBadSeedTaskId
            action = 'execute'
        } | ConvertTo-Json -Compress
        $handoffBadSeedExecute = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/tasks/action" -Method Post -ContentType 'application/json' -Body $handoffBadSeedExecutePayload -TimeoutSec 30
        $handoffBadSeedExecuteOk = $handoffBadSeedExecute.ok -and $handoffBadSeedExecute.task.status -eq 'completed'
        Write-Check -Name 'Dashboard handoff bad clipboard seed execution endpoint' -Passed $handoffBadSeedExecuteOk -Detail ($(if ($handoffBadSeedExecuteOk) { $handoffBadSeedExecute.summary.headline } else { 'handoff bad clipboard seed execution failed' }))
        if (-not $handoffBadSeedExecuteOk) { $failed++ }
    }

    $handoffBlockedPayload = @{
        actionType = 'run_operator_recipe'
        target = 'codex_to_chatgpt_handoff_mvp'
        content = '{"sourceWindow":"codex","targetWindow":"chatgpt","targetWindowCandidateId":"pid:2202","usePreparedClipboard":true,"waitSeconds":0}'
    } | ConvertTo-Json -Compress
    $handoffBlockedQueue = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/executor/queue" -Method Post -ContentType 'application/json' -Body $handoffBlockedPayload -TimeoutSec 30
    $handoffBlockedQueueOk = $handoffBlockedQueue.ok -and `
        $handoffBlockedQueue.task.status -eq 'pending_approval' -and `
        $handoffBlockedQueue.task.recipeSourceWindow -eq 'codex' -and `
        $handoffBlockedQueue.task.recipeTargetWindow -eq 'chatgpt'
    Write-Check -Name 'Dashboard Codex to ChatGPT blocked-payload queue endpoint' -Passed $handoffBlockedQueueOk -Detail ($(if ($handoffBlockedQueueOk) { $handoffBlockedQueue.summary.headline } else { 'blocked handoff queue failed' }))
    if (-not $handoffBlockedQueueOk) { $failed++ }

    $handoffBlockedTaskId = $handoffBlockedQueue.summary.taskId
    $handoffBlockedApprovalId = $handoffBlockedQueue.task.approvalRequestId
    if (-not [string]::IsNullOrWhiteSpace($handoffBlockedApprovalId)) {
        $handoffBlockedApprovePayload = @{
            approvalId = $handoffBlockedApprovalId
            decision = 'approve'
            note = 'dashboard checker approved blocked handoff payload test'
        } | ConvertTo-Json -Compress
        $handoffBlockedApprove = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/approvals/decision" -Method Post -ContentType 'application/json' -Body $handoffBlockedApprovePayload -TimeoutSec 30
        $handoffBlockedApproveOk = $handoffBlockedApprove.ok -and $handoffBlockedApprove.approval.status -eq 'approved'
        Write-Check -Name 'Dashboard Codex to ChatGPT blocked-payload approval endpoint' -Passed $handoffBlockedApproveOk -Detail ($(if ($handoffBlockedApproveOk) { $handoffBlockedApprove.summary.headline } else { 'blocked handoff approval failed' }))
        if (-not $handoffBlockedApproveOk) { $failed++ }
    }

    if (-not [string]::IsNullOrWhiteSpace($handoffBlockedTaskId)) {
        $handoffBlockedExecutePayload = @{
            taskId = $handoffBlockedTaskId
            action = 'execute'
        } | ConvertTo-Json -Compress
        $handoffBlockedExecute = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/tasks/action" -Method Post -ContentType 'application/json' -Body $handoffBlockedExecutePayload -TimeoutSec 30
        $handoffBlockedExecuteOk = $handoffBlockedExecute.ok -and `
            $handoffBlockedExecute.task.status -eq 'blocked_human_needed' -and `
            $handoffBlockedExecute.task.lastExecutionStatus -eq 'failed'
        Write-Check -Name 'Dashboard Codex to ChatGPT blocks junk payload before paste' -Passed $handoffBlockedExecuteOk -Detail ($(if ($handoffBlockedExecuteOk) { $handoffBlockedExecute.summary.headline } else { 'blocked handoff execution failed' }))
        if (-not $handoffBlockedExecuteOk) { $failed++ }

        $handoffBlockedDetail = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/tasks/item?taskId=$handoffBlockedTaskId" -Method Get -TimeoutSec 30
        $handoffBlockedDetailOk = $handoffBlockedDetail.ok -and `
            $handoffBlockedDetail.summary.recipeStatus -eq 'blocked' -and `
            ($handoffBlockedDetail.summary.handoffPayloadClassification -match 'junk_label_payload|repeated_ui_label_garbage') -and `
            $handoffBlockedDetail.summary.handoffPasteAllowed -eq 'no' -and `
            $handoffBlockedDetail.summary.handoffBlockedPayloadRepeats -eq 1
        Write-Check -Name 'Dashboard blocked handoff detail keeps payload classification and paste denial' -Passed $handoffBlockedDetailOk -Detail ($(if ($handoffBlockedDetailOk) { $handoffBlockedDetail.summary.handoffPayloadReason } else { 'blocked handoff detail missing classification state' }))
        if (-not $handoffBlockedDetailOk) { $failed++ }

        $handoffBlockedReviewPayload = @{
            taskId = $handoffBlockedTaskId
            action = 'review'
            note = 'dashboard checker reviewed repeated blocked handoff payload'
        } | ConvertTo-Json -Compress
        $handoffBlockedReview = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/tasks/action" -Method Post -ContentType 'application/json' -Body $handoffBlockedReviewPayload -TimeoutSec 30
        $handoffBlockedReviewOk = $handoffBlockedReview.ok -and $handoffBlockedReview.task.status -eq 'ready_to_resume'
        Write-Check -Name 'Dashboard blocked handoff task can be reviewed for manual re-queue' -Passed $handoffBlockedReviewOk -Detail ($(if ($handoffBlockedReviewOk) { $handoffBlockedReview.summary.headline } else { 'blocked handoff review failed' }))
        if (-not $handoffBlockedReviewOk) { $failed++ }

        $handoffBlockedRequeuePayload = @{
            taskId = $handoffBlockedTaskId
            action = 'requeue'
            note = 'dashboard checker re-queued repeated blocked handoff payload'
        } | ConvertTo-Json -Compress
        $handoffBlockedRequeue = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/tasks/action" -Method Post -ContentType 'application/json' -Body $handoffBlockedRequeuePayload -TimeoutSec 30
        $handoffBlockedRequeueOk = $handoffBlockedRequeue.ok -and $handoffBlockedRequeue.task.status -eq 'queued'
        Write-Check -Name 'Dashboard blocked handoff task re-queues only after explicit operator action' -Passed $handoffBlockedRequeueOk -Detail ($(if ($handoffBlockedRequeueOk) { $handoffBlockedRequeue.summary.headline } else { 'blocked handoff requeue failed' }))
        if (-not $handoffBlockedRequeueOk) { $failed++ }

        $handoffBlockedExecuteAgainPayload = @{
            taskId = $handoffBlockedTaskId
            action = 'execute'
        } | ConvertTo-Json -Compress
        $handoffBlockedExecuteAgain = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/tasks/action" -Method Post -ContentType 'application/json' -Body $handoffBlockedExecuteAgainPayload -TimeoutSec 30
        $handoffBlockedExecuteAgainOk = $handoffBlockedExecuteAgain.ok -and `
            $handoffBlockedExecuteAgain.task.status -eq 'blocked_human_needed' -and `
            $handoffBlockedExecuteAgain.task.lastExecutionStatus -eq 'failed'
        Write-Check -Name 'Dashboard repeated identical junk handoff payload blocks again without looping' -Passed $handoffBlockedExecuteAgainOk -Detail ($(if ($handoffBlockedExecuteAgainOk) { $handoffBlockedExecuteAgain.summary.headline } else { 'repeated blocked handoff execution failed' }))
        if (-not $handoffBlockedExecuteAgainOk) { $failed++ }

        $handoffBlockedDetailAgain = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/tasks/item?taskId=$handoffBlockedTaskId" -Method Get -TimeoutSec 30
        $handoffBlockedDetailAgainOk = $handoffBlockedDetailAgain.ok -and `
            $handoffBlockedDetailAgain.summary.handoffBlockedPayloadRepeats -eq 2 -and `
            $handoffBlockedDetailAgain.summary.handoffPayloadReason -match 'Repeated identical blocked handoff payload detected again'
        Write-Check -Name 'Dashboard repeated identical junk handoff payload is counted and reported clearly' -Passed $handoffBlockedDetailAgainOk -Detail ($(if ($handoffBlockedDetailAgainOk) { $handoffBlockedDetailAgain.summary.handoffPayloadReason } else { 'repeated blocked handoff detail missing repeat count' }))
        if (-not $handoffBlockedDetailAgainOk) { $failed++ }
    }

    $dashboardHtmlPath = Join-Path $projectRoot 'public\index.html'
    $dashboardHtml = if (Test-Path $dashboardHtmlPath) { Get-Content $dashboardHtmlPath -Raw } else { '' }
    $taskFilterUiOk = -not [string]::IsNullOrWhiteSpace($dashboardHtml) -and `
        $dashboardHtml -match 'task-visibility-filter' -and `
        $dashboardHtml -match 'task-recency-filter' -and `
        $dashboardHtml -match 'ghoti-control-center' -and `
        $dashboardHtml -match 'ghoti-target-marker' -and `
        $dashboardHtml -match 'ghoti-overlay-watchdog-pill' -and `
        $dashboardHtml -match 'ghoti-watchdog-state' -and `
        $dashboardHtml -match 'ghoti-brain-provider' -and `
        $dashboardHtml -match 'ghoti-brain-model' -and `
        $dashboardHtml -match 'ghoti-brain-last-call' -and `
        $dashboardHtml -match 'ghoti-role-current' -and `
        $dashboardHtml -match 'ghoti-browser-use-installed' -and `
        $dashboardHtml -match 'ghoti-relay-state' -and `
        $dashboardHtml -match 'ghoti-relay-preset' -and `
        $dashboardHtml -match 'ghoti-memory-ready' -and `
        $dashboardHtml -match 'Brain / Provider Truth' -and `
        $dashboardHtml -match 'Specialist-Agent Truth' -and `
        $dashboardHtml -match 'Browser-Agent Truth' -and `
        $dashboardHtml -match 'Relay-Loop Truth' -and `
        $dashboardHtml -match 'Compact Memory Truth' -and `
        $dashboardHtml -match 'Operator Watchdog' -and `
        $dashboardHtml -match 'Runtime Truth' -and `
        $dashboardHtml -match 'Supervisor Truth' -and `
        $dashboardHtml -match 'Approval Truth' -and `
        $dashboardHtml -match 'Dashboard Truth' -and `
        $dashboardHtml -match 'Content MVP Truth' -and `
        $dashboardHtml -match 'External Repo / Skill Intake Truth' -and `
        $dashboardHtml -match 'no clone/install/run' -and `
        $dashboardHtml -match 'no runtime wiring' -and `
        $dashboardHtml -match 'human approval required' -and `
        $dashboardHtml -match 'ghoti-task-visibility-filter' -and `
        $dashboardHtml -match 'ghoti-show-active-tasks' -and `
        $dashboardHtml -match 'ghoti-queue-focus-window' -and `
        $dashboardHtml -match 'ghoti-run-runtime-checker' -and `
        $dashboardHtml -match 'ghoti-cli-command-list' -and `
        $dashboardHtml -match 'ghoti-control-hotkey' -and `
        $dashboardHtml -match 'Ctrl\+8' -and `
        $dashboardHtml -match 'queue-recipe-codex-handoff' -and `
        $dashboardHtml -match 'This handoff never falls back to terminal or PowerShell'
    Write-Check -Name 'Dashboard task filter controls are present for noise reduction' -Passed $taskFilterUiOk -Detail ($(if ($taskFilterUiOk) { 'task filter controls found in dashboard HTML' } else { 'task filter controls missing from dashboard HTML' }))
    if (-not $taskFilterUiOk) { $failed++ }

    $noDeleteUiOk = -not [string]::IsNullOrWhiteSpace($dashboardHtml) -and `
        $dashboardHtml -match 'No task deletion without explicit approval' -and `
        $dashboardHtml -notmatch 'delete-task' -and `
        $dashboardHtml -notmatch '>\s*Delete Task\s*<'
    Write-Check -Name 'Dashboard control center keeps no-delete policy explicit' -Passed $noDeleteUiOk -Detail ($(if ($noDeleteUiOk) { 'dashboard HTML shows the no-delete policy and exposes no delete-task control' } else { 'dashboard HTML is missing the no-delete policy or exposes a delete-task control' }))
    if (-not $noDeleteUiOk) { $failed++ }

    $approvalAwareRecipePayload = @{
        actionType = 'run_operator_recipe'
        target = 'focus_or_reuse_terminal'
    } | ConvertTo-Json
    $approvalAwareRecipeQueue = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/executor/queue" -Method Post -ContentType 'application/json' -Body $approvalAwareRecipePayload -TimeoutSec 30
    $approvalAwareRecipeQueueOk = $approvalAwareRecipeQueue.ok -and `
        $approvalAwareRecipeQueue.localOnly -and `
        $approvalAwareRecipeQueue.task.status -eq 'pending_approval' -and `
        $approvalAwareRecipeQueue.task.approvalState -eq 'pending' -and `
        $approvalAwareRecipeQueue.task.recipeName -eq 'focus_or_reuse_terminal'
    Write-Check -Name 'Approval-aware recipe queue endpoint' -Passed $approvalAwareRecipeQueueOk -Detail ($(if ($approvalAwareRecipeQueueOk) { $approvalAwareRecipeQueue.summary.headline } else { 'approval-aware recipe queue failed' }))
    if (-not $approvalAwareRecipeQueueOk) { $failed++ }

    $recipeInterruptSeed = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @(
        'queue-executor-action',
        '--action-type', 'run_operator_recipe',
        '--target', 'wait_and_resume_operator_step',
        '--content', '{"waitSeconds":5}'
    )
    $recipeInterruptSeedOk = $recipeInterruptSeed.ExitCode -eq 0 -and `
        (($recipeInterruptSeed.Output | Out-String) -match 'status:\s+queued') -and `
        (($recipeInterruptSeed.Output | Out-String) -match 'approval_state:\s+not_required') -and `
        (($recipeInterruptSeed.Output | Out-String) -match 'recipe_name:\s+wait_and_resume_operator_step')
    Write-Check -Name 'Operator recipe interrupt seed queued' -Passed $recipeInterruptSeedOk -Detail (($recipeInterruptSeed.Output | Out-String).Trim())
    if (-not $recipeInterruptSeedOk) { $failed++ }

    $recipeInterruptTaskMatch = [regex]::Match(($recipeInterruptSeed.Output | Out-String), 'task_id:\s*(\S+)')
    $recipeInterruptTaskId = if ($recipeInterruptTaskMatch.Success) { $recipeInterruptTaskMatch.Groups[1].Value } else { $null }
    $recipeInterruptTaskOk = -not [string]::IsNullOrWhiteSpace($recipeInterruptTaskId)
    Write-Check -Name 'Operator recipe interrupt task id returned' -Passed $recipeInterruptTaskOk -Detail ($(if ($recipeInterruptTaskOk) { $recipeInterruptTaskId } else { 'operator recipe interrupt task id missing' }))
    if (-not $recipeInterruptTaskOk) { $failed++ }

    if ($recipeInterruptTaskOk) {
        $recipeInterruptExecute = Invoke-ModuleCommand `
            -PythonPath $pythonPath `
            -Arguments @('execute-task', '--task-id', $recipeInterruptTaskId) `
            -EnvOverrides @{ SUPER_AGENT_DESKTOP_TEST_INTERRUPT_AFTER_MS = '300' }
        $recipeInterruptExecuteOk = $recipeInterruptExecute.ExitCode -eq 0 -and `
            (($recipeInterruptExecute.Output | Out-String) -match 'status:\s+interrupted') -and `
            (($recipeInterruptExecute.Output | Out-String) -match 'execution_status:\s+interrupted')
        Write-Check -Name 'Operator recipe interrupt executes into interrupted state' -Passed $recipeInterruptExecuteOk -Detail (($recipeInterruptExecute.Output | Out-String).Trim())
        if (-not $recipeInterruptExecuteOk) { $failed++ }

        $recipeInterruptDetail = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/tasks/item?taskId=$recipeInterruptTaskId" -Method Get -TimeoutSec 30
        $recipeInterruptDetailOk = $recipeInterruptDetail.ok -and `
            $recipeInterruptDetail.summary.status -eq 'interrupted' -and `
            $recipeInterruptDetail.summary.recipeStatus -eq 'interrupted' -and `
            $recipeInterruptDetail.summary.blockedReason -match 'Ctrl\+8'
        Write-Check -Name 'Operator recipe interrupt detail shows failsafe state' -Passed $recipeInterruptDetailOk -Detail ($(if ($recipeInterruptDetailOk) { $recipeInterruptDetail.summary.blockedReason } else { 'operator recipe interrupt detail missing failsafe state' }))
        if (-not $recipeInterruptDetailOk) { $failed++ }
    }
    }

    $recentActions = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/recent-actions" -Method Get -TimeoutSec 30
    $recentActionsOk = $recentActions.ok -and $recentActions.localOnly -and $recentActions.actions.Count -gt 0
    Write-Check -Name 'Recent actions endpoint' -Passed $recentActionsOk -Detail ($(if ($recentActionsOk) { 'recent actions log returned entries' } else { 'recent actions log missing entries' }))
    if (-not $recentActionsOk) { $failed++ }
}
finally {
    Remove-GeneratedFile -Path $browserArtifactPath
    Remove-GeneratedFile -Path $desktopArtifactPath

    if ($serverProcess -and -not $serverProcess.HasExited) {
        Stop-Process -Id $serverProcess.Id -Force -ErrorAction SilentlyContinue
    }

    Remove-Item -LiteralPath $serverStdout, $serverStderr -Force -ErrorAction SilentlyContinue
}

Write-Host ''
if ($failed -eq 0) {
    Write-Host 'Summary: dashboard MVP checks passed.'
    exit 0
}

Write-Host ('Summary: {0} dashboard check(s) failed.' -f $failed)
exit 1
