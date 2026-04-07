# Local dashboard MVP checker with safe local-only behavior.

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
        [string[]]$Arguments
    )

    $argumentsJson = ConvertTo-Json -InputObject @($Arguments) -Compress
    $argumentsEncoded = [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($argumentsJson))
    $runtimeSrcEscaped = $runtimeSrc.Replace('\', '\\').Replace("'", "\\'")
    $scriptPath = [System.IO.Path]::ChangeExtension([System.IO.Path]::GetTempFileName(), '.py')
    $code = @"
import base64
import json
import sys
sys.path.insert(0, r'$runtimeSrcEscaped')
from super_ai_agent.cli import main
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
    '04_docs/supervisor_foundation.md',
    '04_docs/approval_inbox_plan.md',
    '04_docs/notification_adapter_plan.md',
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
$serverStdout = [System.IO.Path]::GetTempFileName()
$serverStderr = [System.IO.Path]::GetTempFileName()
$serverProcess = $null

try {
    Remove-GeneratedFile -Path $browserArtifactPath

    $previousPort = $env:PORT
    $env:PORT = "$port"
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

    $pendingApprovals = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/approvals/pending" -Method Get -TimeoutSec 30
    $pendingApprovalsOk = $pendingApprovals.ok -and $pendingApprovals.localOnly -and $null -ne $pendingApprovals.summary.requests
    Write-Check -Name 'Pending approvals endpoint' -Passed $pendingApprovalsOk -Detail ($(if ($pendingApprovalsOk) { $pendingApprovals.summary.headline } else { 'pending approvals missing structured output' }))
    if (-not $pendingApprovalsOk) { $failed++ }

    $executorList = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/executor/tasks" -Method Get -TimeoutSec 30
    $executorListOk = $executorList.ok -and $executorList.localOnly -and $null -ne $executorList.summary.tasks
    Write-Check -Name 'Executor task list endpoint' -Passed $executorListOk -Detail ($(if ($executorListOk) { $executorList.summary.headline } else { 'executor task list missing structured output' }))
    if (-not $executorListOk) { $failed++ }

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
    $browserSmokeOk = $browserSmoke.ok -and (Test-Path -LiteralPath $browserArtifactPath -PathType Leaf)
    Write-Check -Name 'Browser smoke endpoint' -Passed $browserSmokeOk -Detail ($(if ($browserSmokeOk) { $browserSmoke.summary.headline } else { 'browser smoke artifact missing' }))
    if (-not $browserSmokeOk) { $failed++ }

    $visibleCheck = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/browser/visible" -Method Post -ContentType 'application/json' -Body (@{ checkOnly = $true } | ConvertTo-Json) -TimeoutSec 30
    $visibleCheckOk = $visibleCheck.ok
    Write-Check -Name 'Visible demo endpoint' -Passed $visibleCheckOk -Detail ($(if ($visibleCheckOk) { 'visible endpoint responded in check-only mode' } else { 'visible endpoint failed' }))
    if (-not $visibleCheckOk) { $failed++ }

    $desktopStatus = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/desktop-bridge/status" -Method Get -TimeoutSec 30
    $desktopStatusOk = $desktopStatus.ok -and $desktopStatus.localOnly -and $desktopStatus.summary.powerShellAvailable
    Write-Check -Name 'Desktop bridge status endpoint' -Passed $desktopStatusOk -Detail ($(if ($desktopStatusOk) { $desktopStatus.summary.headline } else { 'desktop bridge status missing structured output' }))
    if (-not $desktopStatusOk) { $failed++ }

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
        $desktopOpenExecuteOk = $desktopOpenExecute.ok -and `
            $desktopOpenExecute.task.status -eq 'completed' -and `
            $desktopOpenExecute.task.lastExecutionStatus -eq 'succeeded'
        Write-Check -Name 'Desktop open_allowed_app execution endpoint' -Passed $desktopOpenExecuteOk -Detail ($(if ($desktopOpenExecuteOk) { $desktopOpenExecute.summary.headline } else { 'desktop open_allowed_app execute failed' }))
        if (-not $desktopOpenExecuteOk) { $failed++ }
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
        $desktopFocusExecuteOk = $desktopFocusExecute.ok -and `
            $desktopFocusExecute.task.status -eq 'completed' -and `
            $desktopFocusExecute.task.lastExecutionStatus -eq 'succeeded'
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
        $desktopScreenshotExecuteOk = $desktopScreenshotExecute.ok -and `
            $desktopScreenshotExecute.task.status -eq 'completed' -and `
            $desktopScreenshotExecute.task.lastExecutionStatus -eq 'succeeded' -and `
            (Test-Path -LiteralPath $desktopArtifactPath -PathType Leaf)
        Write-Check -Name 'Desktop screenshot execution endpoint' -Passed $desktopScreenshotExecuteOk -Detail ($(if ($desktopScreenshotExecuteOk) { $desktopScreenshotExecute.summary.headline } else { 'desktop screenshot execute failed' }))
        if (-not $desktopScreenshotExecuteOk) { $failed++ }

        $desktopScreenshotDetail = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/tasks/item?taskId=$desktopScreenshotTaskId" -Method Get -TimeoutSec 30
        $desktopScreenshotDetailOk = $desktopScreenshotDetail.ok -and `
            $desktopScreenshotDetail.summary.lastExecutionStatus -eq 'succeeded' -and `
            $desktopScreenshotDetail.summary.lastArtifactPath -eq $desktopArtifactPath
        Write-Check -Name 'Desktop screenshot result persists in task detail' -Passed $desktopScreenshotDetailOk -Detail ($(if ($desktopScreenshotDetailOk) { $desktopScreenshotDetail.summary.lastArtifactPath } else { 'desktop screenshot result not persisted' }))
        if (-not $desktopScreenshotDetailOk) { $failed++ }
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
