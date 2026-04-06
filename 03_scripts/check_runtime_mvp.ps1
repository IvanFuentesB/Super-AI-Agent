# Runtime MVP checker with no external dependencies.

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

        $outputParts = @()
        if (Test-Path -LiteralPath $stdoutPath) {
            $stdoutText = Get-Content -Raw -LiteralPath $stdoutPath
            if (-not [string]::IsNullOrWhiteSpace($stdoutText)) {
                $outputParts += $stdoutText.TrimEnd()
            }
        }
        if (Test-Path -LiteralPath $stderrPath) {
            $stderrText = Get-Content -Raw -LiteralPath $stderrPath
            if (-not [string]::IsNullOrWhiteSpace($stderrText)) {
                $outputParts += $stderrText.TrimEnd()
            }
        }
    }
    finally {
        Remove-Item -LiteralPath $scriptPath, $stdoutPath, $stderrPath -Force -ErrorAction SilentlyContinue
    }

    return @{
        ExitCode = $process.ExitCode
        Output = ($outputParts -join [Environment]::NewLine)
    }
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$runtimeRoot = Join-Path $repoRoot '01_projects\runtime_mvp'
$runtimeSrc = Join-Path $runtimeRoot 'src'

$expectedFiles = @(
    '01_projects/runtime_mvp/README.md',
    '01_projects/runtime_mvp/pyproject.toml',
    '01_projects/runtime_mvp/src/super_ai_agent/__init__.py',
    '01_projects/runtime_mvp/src/super_ai_agent/environment.py',
    '01_projects/runtime_mvp/src/super_ai_agent/integrations.py',
    '01_projects/runtime_mvp/src/super_ai_agent/github_adapter.py',
    '01_projects/runtime_mvp/src/super_ai_agent/github_actions.py',
    '01_projects/runtime_mvp/src/super_ai_agent/mail_adapter.py',
    '01_projects/runtime_mvp/src/super_ai_agent/notion_adapter.py',
    '01_projects/runtime_mvp/src/super_ai_agent/models.py',
    '01_projects/runtime_mvp/src/super_ai_agent/storage.py',
    '01_projects/runtime_mvp/src/super_ai_agent/queue.py',
    '01_projects/runtime_mvp/src/super_ai_agent/handoff.py',
    '01_projects/runtime_mvp/src/super_ai_agent/personal_ops.py',
    '01_projects/runtime_mvp/src/super_ai_agent/providers.py',
    '01_projects/runtime_mvp/src/super_ai_agent/council.py',
    '01_projects/runtime_mvp/src/super_ai_agent/truth_council.py',
    '01_projects/runtime_mvp/src/super_ai_agent/publishability.py',
    '01_projects/runtime_mvp/src/super_ai_agent/workflow_catalog.py',
    '01_projects/runtime_mvp/src/super_ai_agent/report_builder.py',
    '01_projects/runtime_mvp/src/super_ai_agent/cli.py',
    '01_projects/runtime_mvp/runtime_data/.gitkeep',
    '04_docs/runtime_mvp.md',
    '04_docs/runtime_environment.md',
    '04_docs/tool_capability_matrix.md',
    '04_docs/gh_path_and_auth.md',
    '04_docs/integration_adapter_architecture.md',
    '04_docs/github_adapter.md',
    '04_docs/github_write_actions.md',
    '04_docs/github_approval_flow.md',
    '04_docs/mail_adapter_plan.md',
    '04_docs/notion_adapter_plan.md',
    '04_docs/publishability_scope.md',
    '04_docs/personal_ops_architecture.md',
    '04_docs/owned_account_workflows.md',
    '04_docs/mail_linkedin_cv_pipeline.md',
    '04_docs/integration_priority_matrix.md',
    '04_docs/access_control_architecture.md',
    '04_docs/publishability_checklist.md',
    '04_docs/licensing_strategy.md',
    '04_docs/truth_council_architecture.md',
    '04_docs/browser_app_control_architecture.md',
    '07_templates/inbox_triage_runbook.md',
    '07_templates/linkedin_update_pack.md',
    '07_templates/cv_update_pack.md',
    '07_templates/outreach_draft.md',
    '07_templates/github_issue_draft.md',
    '07_templates/github_pr_draft.md',
    '11_exports/github/.gitkeep',
    '11_exports/personal_ops/.gitkeep',
    '23_configs/integration_policy.example.json',
    '23_configs/publish_scope.example.json',
    '23_configs/github_action_policy.example.json',
    '23_configs/tool_detection_policy.example.json',
    '23_configs/provider_profiles.example.json',
    '23_configs/council_policy.example.json',
    '23_configs/personal_workflow_catalog.example.json',
    '23_configs/owned_account_policy.example.json',
    '23_configs/workflow_catalog.example.json',
    '23_configs/publish_policy.example.json',
    '23_configs/truth_council_policy.example.json'
)

$failed = 0

$allFilesPresent = $true
foreach ($relativePath in $expectedFiles) {
    $fullPath = Join-Path $repoRoot $relativePath
    $exists = Test-Path -LiteralPath $fullPath -PathType Leaf
    Write-Check -Name 'File exists' -Passed $exists -Detail $relativePath
    if (-not $exists) {
        $allFilesPresent = $false
        $failed++
    }
}

$pythonPath = Resolve-PythonPath
$pythonOk = -not [string]::IsNullOrWhiteSpace($pythonPath)
Write-Check -Name 'Python available' -Passed $pythonOk -Detail ($(if ($pythonOk) { $pythonPath } else { 'python interpreter not found' }))
if (-not $pythonOk) {
    Write-Host ''
    Write-Host ('Summary: {0} check(s) failed before runtime execution.' -f $failed)
    exit 1
}

$initResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('init-data')
$initOk = $initResult.ExitCode -eq 0
Write-Check -Name 'CLI init-data' -Passed $initOk -Detail (($initResult.Output | Out-String).Trim())
if (-not $initOk) { $failed++ }

$envDiagnoseResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('env-diagnose')
$envDiagnoseOk = $envDiagnoseResult.ExitCode -eq 0
Write-Check -Name 'CLI env-diagnose' -Passed $envDiagnoseOk -Detail (($envDiagnoseResult.Output | Out-String).Trim())
if (-not $envDiagnoseOk) { $failed++ }

$ghModeKnown = (($envDiagnoseResult.Output | Out-String) -match 'gh_source:\s+(path|fallback|missing|disabled)')
Write-Check -Name 'Environment diagnosis reports gh source' -Passed $ghModeKnown -Detail ($(if ($ghModeKnown) { 'gh source was reported clearly.' } else { 'gh source was not reported clearly.' }))
if (-not $ghModeKnown) { $failed++ }

$ghPathModeKnown = (($envDiagnoseResult.Output | Out-String) -match 'gh_path_visible:\s+(yes|no)')
Write-Check -Name 'Environment diagnosis reports gh PATH visibility' -Passed $ghPathModeKnown -Detail ($(if ($ghPathModeKnown) { 'gh PATH visibility was reported clearly.' } else { 'gh PATH visibility was not reported clearly.' }))
if (-not $ghPathModeKnown) { $failed++ }

$capabilityMatrixResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('capability-matrix')
$capabilityMatrixOk = $capabilityMatrixResult.ExitCode -eq 0
Write-Check -Name 'CLI capability-matrix' -Passed $capabilityMatrixOk -Detail (($capabilityMatrixResult.Output | Out-String).Trim())
if (-not $capabilityMatrixOk) { $failed++ }

$ghAuthStatusResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('gh-auth-status')
$ghAuthStatusOk = $ghAuthStatusResult.ExitCode -eq 0
Write-Check -Name 'CLI gh-auth-status' -Passed $ghAuthStatusOk -Detail (($ghAuthStatusResult.Output | Out-String).Trim())
if (-not $ghAuthStatusOk) { $failed++ }

$ghAuthModeKnown = (($ghAuthStatusResult.Output | Out-String) -match 'status:\s+(checked|skipped|unknown)')
Write-Check -Name 'gh auth status is clearly classified' -Passed $ghAuthModeKnown -Detail ($(if ($ghAuthModeKnown) { 'gh auth status output is readable.' } else { 'gh auth status output is unclear.' }))
if (-not $ghAuthModeKnown) { $failed++ }

$providersResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('list-providers')
$providersOk = $providersResult.ExitCode -eq 0
Write-Check -Name 'CLI list-providers' -Passed $providersOk -Detail (($providersResult.Output | Out-String).Trim())
if (-not $providersOk) { $failed++ }

$councilResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('council-plan', '--goal-type', 'planning', '--privacy', 'balanced', '--speed', 'balanced', '--require-reviewer')
$councilOk = $councilResult.ExitCode -eq 0
Write-Check -Name 'CLI council-plan' -Passed $councilOk -Detail (($councilResult.Output | Out-String).Trim())
if (-not $councilOk) { $failed++ }

$listWorkflowsResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('list-workflows')
$listWorkflowsOk = $listWorkflowsResult.ExitCode -eq 0
Write-Check -Name 'CLI list-workflows' -Passed $listWorkflowsOk -Detail (($listWorkflowsResult.Output | Out-String).Trim())
if (-not $listWorkflowsOk) { $failed++ }

$showWorkflowResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('show-workflow', '--workflow-id', 'report_pack')
$showWorkflowOk = $showWorkflowResult.ExitCode -eq 0
Write-Check -Name 'CLI show-workflow' -Passed $showWorkflowOk -Detail (($showWorkflowResult.Output | Out-String).Trim())
if (-not $showWorkflowOk) { $failed++ }

$reportResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('scaffold-report', '--title', 'Checker Council Report', '--workflow-id', 'report_pack', '--summary', 'Runtime checker scaffold.')
$reportOk = $reportResult.ExitCode -eq 0
Write-Check -Name 'CLI scaffold-report' -Passed $reportOk -Detail (($reportResult.Output | Out-String).Trim())
if (-not $reportOk) { $failed++ }

$truthPlanResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('truth-plan', '--question', 'Should this stay planning-only?', '--proposer', 'Keep external execution gated.', '--challenger', 'Planning alone may be too passive.', '--evidence', 'Current runtime has no live integrations.', '--evidence-quality', 'medium', '--disagreement', 'medium', '--source-count', '2')
$truthPlanOk = $truthPlanResult.ExitCode -eq 0
Write-Check -Name 'CLI truth-plan' -Passed $truthPlanOk -Detail (($truthPlanResult.Output | Out-String).Trim())
if (-not $truthPlanOk) { $failed++ }

$publishCheckResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('publish-check')
$publishCheckOk = $publishCheckResult.ExitCode -eq 0
Write-Check -Name 'CLI publish-check' -Passed $publishCheckOk -Detail (($publishCheckResult.Output | Out-String).Trim())
if (-not $publishCheckOk) { $failed++ }

$publishCheckCoreResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('publish-check-core')
$publishCheckCoreOk = $publishCheckCoreResult.ExitCode -eq 0
Write-Check -Name 'CLI publish-check-core' -Passed $publishCheckCoreOk -Detail (($publishCheckCoreResult.Output | Out-String).Trim())
if (-not $publishCheckCoreOk) { $failed++ }

$coreScanClean = (($publishCheckCoreResult.Output | Out-String) -notmatch '21_repos/third_party')
Write-Check -Name 'Core publish scan excludes third-party intake' -Passed $coreScanClean -Detail ($(if ($coreScanClean) { 'no third-party intake paths found in scoped scan output' } else { 'scoped scan still reported third-party intake paths' }))
if (-not $coreScanClean) { $failed++ }

$listIntegrationsResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('list-integrations')
$listIntegrationsOk = $listIntegrationsResult.ExitCode -eq 0
Write-Check -Name 'CLI list-integrations' -Passed $listIntegrationsOk -Detail (($listIntegrationsResult.Output | Out-String).Trim())
if (-not $listIntegrationsOk) { $failed++ }

$githubStatusResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('github-status')
$githubStatusOk = $githubStatusResult.ExitCode -eq 0
Write-Check -Name 'CLI github-status' -Passed $githubStatusOk -Detail (($githubStatusResult.Output | Out-String).Trim())
if (-not $githubStatusOk) { $failed++ }

$ghDiagnoseResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('github-gh-diagnose')
$ghDiagnoseOk = $ghDiagnoseResult.ExitCode -eq 0
Write-Check -Name 'CLI github-gh-diagnose' -Passed $ghDiagnoseOk -Detail (($ghDiagnoseResult.Output | Out-String).Trim())
if (-not $ghDiagnoseOk) { $failed++ }

$githubIssueDraftResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('github-issue-draft', '--title', 'Checker GitHub Issue', '--objective', 'Validate issue draft generation', '--context', 'Runtime checker', '--body', 'Draft issue body for checker.', '--labels', 'runtime,checker')
$githubIssueDraftOk = $githubIssueDraftResult.ExitCode -eq 0
Write-Check -Name 'CLI github-issue-draft' -Passed $githubIssueDraftOk -Detail (($githubIssueDraftResult.Output | Out-String).Trim())
if (-not $githubIssueDraftOk) { $failed++ }

$githubPrDraftResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('github-pr-draft', '--title', 'Checker GitHub PR', '--objective', 'Validate PR draft generation', '--source-branch', 'feat/checker-source', '--target-branch', 'main', '--summary', 'Draft PR summary for checker.', '--risk-notes', 'No remote mutation should occur.')
$githubPrDraftOk = $githubPrDraftResult.ExitCode -eq 0
Write-Check -Name 'CLI github-pr-draft' -Passed $githubPrDraftOk -Detail (($githubPrDraftResult.Output | Out-String).Trim())
if (-not $githubPrDraftOk) { $failed++ }

$githubCreateBranchResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('github-create-branch', '--branch-name', 'feat/checker-branch', '--approve', 'no')
$githubCreateBranchRefused = $githubCreateBranchResult.ExitCode -ne 0 -and (($githubCreateBranchResult.Output | Out-String) -match 'Approval required')
Write-Check -Name 'CLI github-create-branch approve=no refusal' -Passed $githubCreateBranchRefused -Detail (($githubCreateBranchResult.Output | Out-String).Trim())
if (-not $githubCreateBranchRefused) { $failed++ }

$githubCreateIssueResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('github-create-issue', '--title', 'Checker remote issue', '--body', 'This should refuse without approval.', '--approve', 'no')
$githubCreateIssueRefused = $githubCreateIssueResult.ExitCode -ne 0 -and (($githubCreateIssueResult.Output | Out-String) -match 'Approval required')
Write-Check -Name 'CLI github-create-issue approve=no refusal' -Passed $githubCreateIssueRefused -Detail (($githubCreateIssueResult.Output | Out-String).Trim())
if (-not $githubCreateIssueRefused) { $failed++ }

$githubCreatePrResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('github-create-pr', '--title', 'Checker remote pr', '--body', 'This should refuse without approval.', '--base-branch', 'main', '--approve', 'no')
$githubCreatePrRefused = $githubCreatePrResult.ExitCode -ne 0 -and (($githubCreatePrResult.Output | Out-String) -match 'Approval required')
Write-Check -Name 'CLI github-create-pr approve=no refusal' -Passed $githubCreatePrRefused -Detail (($githubCreatePrResult.Output | Out-String).Trim())
if (-not $githubCreatePrRefused) { $failed++ }

$ghAvailableForRemote = (($ghDiagnoseResult.Output | Out-String) -match 'gh_available:\s+yes')
Write-Check -Name 'Remote GitHub write test policy' -Passed $true -Detail ($(if ($ghAvailableForRemote) { 'SKIPPED: gh is available but checker does not create live remote issues or PRs.' } else { 'SKIPPED: gh is unavailable, so live remote issue/PR tests were not attempted.' }))

$mailPlanResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('mail-plan', '--account-label', 'Primary Inbox', '--goal', 'Prepare a triage plan')
$mailPlanOk = $mailPlanResult.ExitCode -eq 0
Write-Check -Name 'CLI mail-plan' -Passed $mailPlanOk -Detail (($mailPlanResult.Output | Out-String).Trim())
if (-not $mailPlanOk) { $failed++ }

$notionPlanResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('notion-plan', '--page-label', 'Operations Hub', '--objective', 'Plan a workspace update')
$notionPlanOk = $notionPlanResult.ExitCode -eq 0
Write-Check -Name 'CLI notion-plan' -Passed $notionPlanOk -Detail (($notionPlanResult.Output | Out-String).Trim())
if (-not $notionPlanOk) { $failed++ }

$listPersonalWorkflowsResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('list-personal-workflows')
$listPersonalWorkflowsOk = $listPersonalWorkflowsResult.ExitCode -eq 0
Write-Check -Name 'CLI list-personal-workflows' -Passed $listPersonalWorkflowsOk -Detail (($listPersonalWorkflowsResult.Output | Out-String).Trim())
if (-not $listPersonalWorkflowsOk) { $failed++ }

$showPersonalWorkflowResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('show-personal-workflow', '--workflow-id', 'inbox_triage_pack')
$showPersonalWorkflowOk = $showPersonalWorkflowResult.ExitCode -eq 0
Write-Check -Name 'CLI show-personal-workflow' -Passed $showPersonalWorkflowOk -Detail (($showPersonalWorkflowResult.Output | Out-String).Trim())
if (-not $showPersonalWorkflowOk) { $failed++ }

$inboxPackResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('scaffold-inbox-triage', '--account-label', 'Primary Inbox', '--goal', 'Prepare a daily triage pack')
$inboxPackOk = $inboxPackResult.ExitCode -eq 0
Write-Check -Name 'CLI scaffold-inbox-triage' -Passed $inboxPackOk -Detail (($inboxPackResult.Output | Out-String).Trim())
if (-not $inboxPackOk) { $failed++ }

$linkedinPackResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('scaffold-linkedin-pack', '--profile-label', 'Main Profile', '--target-role', 'AI Automation Lead', '--focus', 'execution systems')
$linkedinPackOk = $linkedinPackResult.ExitCode -eq 0
Write-Check -Name 'CLI scaffold-linkedin-pack' -Passed $linkedinPackOk -Detail (($linkedinPackResult.Output | Out-String).Trim())
if (-not $linkedinPackOk) { $failed++ }

$cvPackResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('scaffold-cv-pack', '--target-role', 'AI Automation Lead', '--summary', 'Execution-first operator focused on controllable AI systems.')
$cvPackOk = $cvPackResult.ExitCode -eq 0
Write-Check -Name 'CLI scaffold-cv-pack' -Passed $cvPackOk -Detail (($cvPackResult.Output | Out-String).Trim())
if (-not $cvPackOk) { $failed++ }

$outreachDraftResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('scaffold-outreach-draft', '--recipient-label', 'Partner Contact', '--purpose', 'Prepare a reviewed partnership note', '--notes', 'Keep it direct and legitimate.')
$outreachDraftOk = $outreachDraftResult.ExitCode -eq 0
Write-Check -Name 'CLI scaffold-outreach-draft' -Passed $outreachDraftOk -Detail (($outreachDraftResult.Output | Out-String).Trim())
if (-not $outreachDraftOk) { $failed++ }

$enqueueResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('enqueue', '--title', 'checker task', '--description', 'runtime check', '--risk', 'ask')
$enqueueOk = $enqueueResult.ExitCode -eq 0
Write-Check -Name 'CLI enqueue' -Passed $enqueueOk -Detail (($enqueueResult.Output | Out-String).Trim())
if (-not $enqueueOk) { $failed++ }

$taskIdMatch = [regex]::Match(($enqueueResult.Output | Out-String), 'task_id:\s*(\S+)')
$taskId = if ($taskIdMatch.Success) { $taskIdMatch.Groups[1].Value } else { $null }
$taskIdOk = -not [string]::IsNullOrWhiteSpace($taskId)
Write-Check -Name 'Task id parsed' -Passed $taskIdOk -Detail ($(if ($taskIdOk) { $taskId } else { 'missing task id from enqueue output' }))
if (-not $taskIdOk) { $failed++ }

if ($taskIdOk) {
    $approveResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('approve', '--task-id', $taskId, '--note', 'checker approval')
    $approveOk = $approveResult.ExitCode -eq 0
    Write-Check -Name 'CLI approve' -Passed $approveOk -Detail (($approveResult.Output | Out-String).Trim())
    if (-not $approveOk) { $failed++ }

    $waitResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('wait', '--task-id', $taskId)
    $waitOk = $waitResult.ExitCode -eq 0
    Write-Check -Name 'CLI wait' -Passed $waitOk -Detail (($waitResult.Output | Out-String).Trim())
    if (-not $waitOk) { $failed++ }

    $resumeResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('resume', '--task-id', $taskId)
    $resumeOk = $resumeResult.ExitCode -eq 0
    Write-Check -Name 'CLI resume' -Passed $resumeOk -Detail (($resumeResult.Output | Out-String).Trim())
    if (-not $resumeOk) { $failed++ }

    $runOnceResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('run-once', '--task-id', $taskId)
    $runOnceOk = $runOnceResult.ExitCode -eq 0
    Write-Check -Name 'CLI run-once' -Passed $runOnceOk -Detail (($runOnceResult.Output | Out-String).Trim())
    if (-not $runOnceOk) { $failed++ }
}

$listResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('list')
$listOk = $listResult.ExitCode -eq 0
Write-Check -Name 'CLI list' -Passed $listOk -Detail (($listResult.Output | Out-String).Trim())
if (-not $listOk) { $failed++ }

$statusResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('status')
$statusOk = $statusResult.ExitCode -eq 0
Write-Check -Name 'CLI status' -Passed $statusOk -Detail (($statusResult.Output | Out-String).Trim())
if (-not $statusOk) { $failed++ }

$snapshotResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('snapshot')
$snapshotOk = $snapshotResult.ExitCode -eq 0
Write-Check -Name 'CLI snapshot' -Passed $snapshotOk -Detail (($snapshotResult.Output | Out-String).Trim())
if (-not $snapshotOk) { $failed++ }

$artifactPaths = @(
    '01_projects/runtime_mvp/runtime_data/tasks.json',
    '01_projects/runtime_mvp/runtime_data/approvals.json',
    '01_projects/runtime_mvp/runtime_data/handoff_snapshot.md',
    '11_exports/reports/checker-council-report.md',
    '11_exports/github/checker-github-issue-issue-draft.md',
    '11_exports/github/checker-github-pr-pr-draft.md',
    '11_exports/personal_ops/primary-inbox-inbox-triage-pack.md',
    '11_exports/personal_ops/main-profile-linkedin-update-pack.md',
    '11_exports/personal_ops/ai-automation-lead-cv-update-pack.md',
    '11_exports/personal_ops/partner-contact-outreach-draft.md'
)

$artifactsOk = $true
foreach ($relativePath in $artifactPaths) {
    $fullPath = Join-Path $repoRoot $relativePath
    $exists = Test-Path -LiteralPath $fullPath -PathType Leaf
    Write-Check -Name 'Artifact exists' -Passed $exists -Detail $relativePath
    if (-not $exists) {
        $artifactsOk = $false
        $failed++
    }
}

Write-Host ''
if ($failed -eq 0 -and $allFilesPresent -and $artifactsOk) {
    Write-Host 'Summary: runtime MVP checks passed.'
    exit 0
}

Write-Host ('Summary: {0} runtime MVP check(s) failed.' -f $failed)
exit 1
