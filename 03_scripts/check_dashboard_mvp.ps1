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

    $escapedArgs = foreach ($item in $Arguments) {
        $value = $item.Replace('\', '\\').Replace("'", "\\'")
        "'$value'"
    }
    $pythonList = '[' + ($escapedArgs -join ', ') + ']'
    $runtimeSrcEscaped = $runtimeSrc.Replace('\', '\\').Replace("'", "\\'")
    $scriptPath = [System.IO.Path]::ChangeExtension([System.IO.Path]::GetTempFileName(), '.py')
    $code = @"
import sys
sys.path.insert(0, r'$runtimeSrcEscaped')
from super_ai_agent.cli import main
raise SystemExit(main($pythonList))
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
    '01_projects/desktop_playground/check_desktop_playground.ps1'
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

    $recentActions = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/recent-actions" -Method Get -TimeoutSec 30
    $recentActionsOk = $recentActions.ok -and $recentActions.localOnly -and $recentActions.actions.Count -gt 0
    Write-Check -Name 'Recent actions endpoint' -Passed $recentActionsOk -Detail ($(if ($recentActionsOk) { 'recent actions log returned entries' } else { 'recent actions log missing entries' }))
    if (-not $recentActionsOk) { $failed++ }
}
finally {
    Remove-GeneratedFile -Path $browserArtifactPath

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
