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
    '01_projects/runtime_mvp/src/super_ai_agent/notification_adapter.py',
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
    '04_docs/showcase_plan.md',
    '04_docs/internship_showcase_strategy.md',
    '04_docs/claude_openclaw_fit.md',
    '04_docs/career_ops_fit.md',
    '04_docs/browser_executor_research.md',
    '04_docs/skills_in_codex.md',
    '04_docs/internship_ops_plan.md',
    '04_docs/runtime_environment.md',
    '04_docs/tool_capability_matrix.md',
    '04_docs/gh_path_and_auth.md',
    '04_docs/integration_adapter_architecture.md',
    '04_docs/github_adapter.md',
    '04_docs/github_write_actions.md',
    '04_docs/github_approval_flow.md',
    '04_docs/github_remote_smoke_tests.md',
    '04_docs/supervisor_foundation.md',
    '04_docs/approval_inbox_plan.md',
    '04_docs/notification_adapter_plan.md',
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
    '08_research/career_ops_extraction_map.md',
    '08_research/repo_intake_matrix.md',
    '07_templates/inbox_triage_runbook.md',
    '07_templates/linkedin_update_pack.md',
    '07_templates/cv_update_pack.md',
    '07_templates/outreach_draft.md',
    '07_templates/internship_application_pack.md',
    '07_templates/project_showcase_case_study.md',
    '07_templates/portfolio_project_page.md',
    '07_templates/github_issue_draft.md',
    '07_templates/github_pr_draft.md',
    '11_exports/github/.gitkeep',
    '11_exports/personal_ops/.gitkeep',
    '23_configs/integration_policy.example.json',
    '23_configs/publish_scope.example.json',
    '23_configs/github_action_policy.example.json',
    '23_configs/github_smoke_policy.example.json',
    '23_configs/supervisor_policy.example.json',
    '23_configs/tool_detection_policy.example.json',
    '23_configs/repo_manifest.example.json',
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

$githubRemoteCapabilityResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('github-remote-capability')
$githubRemoteCapabilityOk = $githubRemoteCapabilityResult.ExitCode -eq 0
Write-Check -Name 'CLI github-remote-capability' -Passed $githubRemoteCapabilityOk -Detail (($githubRemoteCapabilityResult.Output | Out-String).Trim())
if (-not $githubRemoteCapabilityOk) { $failed++ }

$ghRemoteCapabilityClear = (($githubRemoteCapabilityResult.Output | Out-String) -match 'remote_write_possible:\s+(yes|no)')
Write-Check -Name 'Remote capability is clearly classified' -Passed $ghRemoteCapabilityClear -Detail ($(if ($ghRemoteCapabilityClear) { 'remote capability output is readable.' } else { 'remote capability output is unclear.' }))
if (-not $ghRemoteCapabilityClear) { $failed++ }

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

$githubSmokeIssueResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('github-smoke-issue', '--title', '[SMOKE TEST] Checker smoke issue', '--body', 'This should refuse without approval.', '--labels', 'smoke-test', '--approve', 'no')
$githubSmokeIssueRefused = $githubSmokeIssueResult.ExitCode -ne 0 -and (($githubSmokeIssueResult.Output | Out-String) -match 'Approval required')
Write-Check -Name 'CLI github-smoke-issue approve=no refusal' -Passed $githubSmokeIssueRefused -Detail (($githubSmokeIssueResult.Output | Out-String).Trim())
if (-not $githubSmokeIssueRefused) { $failed++ }

$githubSmokePrResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('github-smoke-pr', '--title', '[SMOKE TEST] Checker smoke pr', '--body', 'This should refuse without approval.', '--base-branch', 'main', '--approve', 'no')
$githubSmokePrRefused = $githubSmokePrResult.ExitCode -ne 0 -and (($githubSmokePrResult.Output | Out-String) -match 'Approval required')
Write-Check -Name 'CLI github-smoke-pr approve=no refusal' -Passed $githubSmokePrRefused -Detail (($githubSmokePrResult.Output | Out-String).Trim())
if (-not $githubSmokePrRefused) { $failed++ }

$remoteSmokePossible = (($githubRemoteCapabilityResult.Output | Out-String) -match 'remote_write_possible:\s+yes')
Write-Check -Name 'Remote GitHub smoke test policy' -Passed $true -Detail ($(if ($remoteSmokePossible) { 'SKIPPED: remote smoke actions are possible, but checker stays non-mutating by default.' } else { 'SKIPPED: remote smoke actions are not ready in this environment.' }))

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

$internshipPackResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('scaffold-internship-pack', '--target-role', 'Applied AI Internship', '--company', 'Example Labs', '--job-source', 'https://example.com/jobs/applied-ai-intern', '--fit-summary', 'Strong fit for execution, documentation, and AI workflow work.')
$internshipPackOk = $internshipPackResult.ExitCode -eq 0
Write-Check -Name 'CLI scaffold-internship-pack' -Passed $internshipPackOk -Detail (($internshipPackResult.Output | Out-String).Trim())
if (-not $internshipPackOk) { $failed++ }

$showcaseCaseStudyResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('scaffold-showcase-case-study', '--project-name', 'Super AI Agent', '--objective', 'Show the strongest current execution-first workflow demo.', '--highlights', 'GitHub control, internship packs, and durable context.')
$showcaseCaseStudyOk = $showcaseCaseStudyResult.ExitCode -eq 0
Write-Check -Name 'CLI scaffold-showcase-case-study' -Passed $showcaseCaseStudyOk -Detail (($showcaseCaseStudyResult.Output | Out-String).Trim())
if (-not $showcaseCaseStudyOk) { $failed++ }

$portfolioProjectPageResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('scaffold-portfolio-project-page', '--project-name', 'Super AI Agent', '--summary', 'Execution-first AI operating framework with controllable outputs.', '--stack', 'Python standard library, PowerShell, Git, GitHub, Continue, Codex')
$portfolioProjectPageOk = $portfolioProjectPageResult.ExitCode -eq 0
Write-Check -Name 'CLI scaffold-portfolio-project-page' -Passed $portfolioProjectPageOk -Detail (($portfolioProjectPageResult.Output | Out-String).Trim())
if (-not $portfolioProjectPageOk) { $failed++ }

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
    $pendingApprovalsResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('pending-approvals')
    $pendingApprovalsOk = $pendingApprovalsResult.ExitCode -eq 0 -and (($pendingApprovalsResult.Output | Out-String) -match 'count:\s+\d+')
    Write-Check -Name 'CLI pending-approvals' -Passed $pendingApprovalsOk -Detail (($pendingApprovalsResult.Output | Out-String).Trim())
    if (-not $pendingApprovalsOk) { $failed++ }

    $approvalIdMatch = [regex]::Match(($pendingApprovalsResult.Output | Out-String), 'approval-[A-Za-z0-9]+')
    $approvalId = if ($approvalIdMatch.Success) { $approvalIdMatch.Value } else { $null }
    $approvalIdOk = -not [string]::IsNullOrWhiteSpace($approvalId)
    Write-Check -Name 'Approval id parsed' -Passed $approvalIdOk -Detail ($(if ($approvalIdOk) { $approvalId } else { 'missing approval id from pending approvals output' }))
    if (-not $approvalIdOk) { $failed++ }

    $supervisorStatusResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('supervisor-status')
    $supervisorStatusOk = $supervisorStatusResult.ExitCode -eq 0 -and (($supervisorStatusResult.Output | Out-String) -match 'status:\s+\S+')
    Write-Check -Name 'CLI supervisor-status' -Passed $supervisorStatusOk -Detail (($supervisorStatusResult.Output | Out-String).Trim())
    if (-not $supervisorStatusOk) { $failed++ }

    $approvalStatusListResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('approval-status')
    $approvalStatusListOk = $approvalStatusListResult.ExitCode -eq 0 -and (($approvalStatusListResult.Output | Out-String) -match 'count:\s+\d+')
    Write-Check -Name 'CLI approval-status list' -Passed $approvalStatusListOk -Detail (($approvalStatusListResult.Output | Out-String).Trim())
    if (-not $approvalStatusListOk) { $failed++ }

    if ($approvalIdOk) {
        $approvalStatusResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('approval-status', '--approval-id', $approvalId)
        $approvalStatusOk = $approvalStatusResult.ExitCode -eq 0 -and (($approvalStatusResult.Output | Out-String) -match 'status:\s+pending')
        Write-Check -Name 'CLI approval-status single' -Passed $approvalStatusOk -Detail (($approvalStatusResult.Output | Out-String).Trim())
        if (-not $approvalStatusOk) { $failed++ }
    }

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

$approvalDecisionScenarios = @(
    @{
        Name = 'approve'
        Command = 'approve-approval'
        Note = 'checker approval queue action'
        ExpectedStatus = 'approved'
        ExpectedTaskStatus = 'queued'
    },
    @{
        Name = 'deny'
        Command = 'deny-approval'
        Note = 'checker denied this request'
        ExpectedStatus = 'denied'
        ExpectedTaskStatus = 'rejected'
    },
    @{
        Name = 'defer'
        Command = 'defer-approval'
        Note = 'checker deferred this request'
        ExpectedStatus = 'deferred'
        ExpectedTaskStatus = 'waiting'
    }
)

foreach ($scenario in $approvalDecisionScenarios) {
    $decisionEnqueueResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('enqueue', '--title', "checker $($scenario.Name) approval task", '--description', "Validate $($scenario.Name) approval action.", '--risk', 'ask')
    $decisionEnqueueOk = $decisionEnqueueResult.ExitCode -eq 0
    Write-Check -Name "CLI enqueue for $($scenario.Name) approval" -Passed $decisionEnqueueOk -Detail (($decisionEnqueueResult.Output | Out-String).Trim())
    if (-not $decisionEnqueueOk) {
        $failed++
        continue
    }

    $decisionApprovalIdMatch = [regex]::Match(($decisionEnqueueResult.Output | Out-String), 'approval_request_id:\s*(\S+)')
    $decisionApprovalId = if ($decisionApprovalIdMatch.Success) { $decisionApprovalIdMatch.Groups[1].Value } else { $null }
    $decisionApprovalIdOk = -not [string]::IsNullOrWhiteSpace($decisionApprovalId)
    Write-Check -Name "$($scenario.Name) approval id parsed" -Passed $decisionApprovalIdOk -Detail ($(if ($decisionApprovalIdOk) { $decisionApprovalId } else { 'missing approval id from enqueue output' }))
    if (-not $decisionApprovalIdOk) {
        $failed++
        continue
    }

    $decisionResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @($scenario.Command, '--approval-id', $decisionApprovalId, '--note', $scenario.Note)
    $decisionOk = $decisionResult.ExitCode -eq 0 -and (($decisionResult.Output | Out-String) -match "status:\s+$($scenario.ExpectedStatus)") -and (($decisionResult.Output | Out-String) -match "task_status:\s+$($scenario.ExpectedTaskStatus)")
    Write-Check -Name "CLI $($scenario.Command)" -Passed $decisionOk -Detail (($decisionResult.Output | Out-String).Trim())
    if (-not $decisionOk) {
        $failed++
        continue
    }

    $postDecisionStatus = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('approval-status', '--approval-id', $decisionApprovalId)
    $postDecisionStatusOk = $postDecisionStatus.ExitCode -eq 0 -and (($postDecisionStatus.Output | Out-String) -match "status:\s+$($scenario.ExpectedStatus)") -and (($postDecisionStatus.Output | Out-String) -match "decision_history:") -and (($postDecisionStatus.Output | Out-String) -match "- $($scenario.ExpectedStatus) \|")
    Write-Check -Name "CLI approval-status after $($scenario.Name)" -Passed $postDecisionStatusOk -Detail (($postDecisionStatus.Output | Out-String).Trim())
    if (-not $postDecisionStatusOk) { $failed++ }
}

$insideScopePath = Join-Path $repoRoot '11_exports\personal_ops\inside-scope-check.txt'
$insideScopeResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @(
    'enqueue',
    '--title', 'checker in-scope path task',
    '--description', "Review $insideScopePath before any action.",
    '--risk', 'safe'
)
$insideScopeOk = $insideScopeResult.ExitCode -eq 0 -and `
    (($insideScopeResult.Output | Out-String) -match 'status:\s+queued') -and `
    (($insideScopeResult.Output | Out-String) -match 'approval_state:\s+not_required') -and `
    (($insideScopeResult.Output | Out-String) -match 'workspace_scope:\s+in_scope') -and `
    (($insideScopeResult.Output | Out-String) -match 'workspace_policy:\s+allowed')
Write-Check -Name 'In-scope workspace path stays normal local work' -Passed $insideScopeOk -Detail (($insideScopeResult.Output | Out-String).Trim())
if (-not $insideScopeOk) { $failed++ }

$externalPathGuardResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @(
    'enqueue',
    '--title', 'checker external path task',
    '--description', 'Review C:\Windows\Temp\outside-target.txt before any action.',
    '--risk', 'safe'
)
$externalPathGuardOk = $externalPathGuardResult.ExitCode -eq 0 -and (($externalPathGuardResult.Output | Out-String) -match 'status:\s+pending_approval') -and (($externalPathGuardResult.Output | Out-String) -match 'approval_state:\s+pending')
Write-Check -Name 'Repo-root safety guard escalates external path task' -Passed $externalPathGuardOk -Detail (($externalPathGuardResult.Output | Out-String).Trim())
if (-not $externalPathGuardOk) { $failed++ }

$externalApprovalIdMatch = [regex]::Match(($externalPathGuardResult.Output | Out-String), 'approval_request_id:\s*(\S+)')
$externalApprovalId = if ($externalApprovalIdMatch.Success) { $externalApprovalIdMatch.Groups[1].Value } else { $null }
$externalApprovalIdOk = -not [string]::IsNullOrWhiteSpace($externalApprovalId)
Write-Check -Name 'External path approval id parsed' -Passed $externalApprovalIdOk -Detail ($(if ($externalApprovalIdOk) { $externalApprovalId } else { 'missing approval id for external path guard scenario' }))
if (-not $externalApprovalIdOk) { $failed++ }

if ($externalApprovalIdOk) {
    $externalApprovalStatusResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('approval-status', '--approval-id', $externalApprovalId)
    $externalApprovalStatusOk = $externalApprovalStatusResult.ExitCode -eq 0 -and `
        (($externalApprovalStatusResult.Output | Out-String) -match 'risk_level:\s+high_risk') -and `
        (($externalApprovalStatusResult.Output | Out-String) -match 'workspace_scope:\s+out_of_scope') -and `
        (($externalApprovalStatusResult.Output | Out-String) -match 'workspace_policy:\s+blocked_by_workspace_policy')
    Write-Check -Name 'External path approval is marked high risk' -Passed $externalApprovalStatusOk -Detail (($externalApprovalStatusResult.Output | Out-String).Trim())
    if (-not $externalApprovalStatusOk) { $failed++ }

    $externalApprovalDecisionResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('approve-approval', '--approval-id', $externalApprovalId, '--note', 'checker recorded the out-of-scope approval')
    $externalApprovalDecisionOk = $externalApprovalDecisionResult.ExitCode -eq 0 -and `
        (($externalApprovalDecisionResult.Output | Out-String) -match 'task_status:\s+blocked_human_needed') -and `
        (($externalApprovalDecisionResult.Output | Out-String) -match 'workspace_policy:\s+blocked_by_workspace_policy')
    Write-Check -Name 'Out-of-scope approval stays blocked by workspace policy' -Passed $externalApprovalDecisionOk -Detail (($externalApprovalDecisionResult.Output | Out-String).Trim())
    if (-not $externalApprovalDecisionOk) { $failed++ }
}

$safeTaskResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('enqueue', '--title', 'checker safe task', '--description', 'supervisor and human-needed check', '--risk', 'safe')
$safeTaskOk = $safeTaskResult.ExitCode -eq 0
Write-Check -Name 'CLI enqueue safe task' -Passed $safeTaskOk -Detail (($safeTaskResult.Output | Out-String).Trim())
if (-not $safeTaskOk) { $failed++ }

$safeTaskIdMatch = [regex]::Match(($safeTaskResult.Output | Out-String), 'task_id:\s*(\S+)')
$safeTaskId = if ($safeTaskIdMatch.Success) { $safeTaskIdMatch.Groups[1].Value } else { $null }
$safeTaskIdOk = -not [string]::IsNullOrWhiteSpace($safeTaskId)
Write-Check -Name 'Safe task id parsed' -Passed $safeTaskIdOk -Detail ($(if ($safeTaskIdOk) { $safeTaskId } else { 'missing safe task id from enqueue output' }))
if (-not $safeTaskIdOk) { $failed++ }

if ($safeTaskIdOk) {
    $requestApprovalResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('request-approval', '--task-id', $safeTaskId, '--action-label', 'Checker approval request', '--reason', 'Validate the structured approval inbox path.', '--risk-level', 'high_risk', '--scope', 'runtime checker', '--rollback-plan', 'Keep the task paused until approval is resolved.', '--requires-admin', 'no')
    $requestApprovalOk = $requestApprovalResult.ExitCode -eq 0 -and (($requestApprovalResult.Output | Out-String) -match 'notification_mode:\s+local_dashboard')
    Write-Check -Name 'CLI request-approval' -Passed $requestApprovalOk -Detail (($requestApprovalResult.Output | Out-String).Trim())
    if (-not $requestApprovalOk) { $failed++ }

    $humanNeededResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('mark-human-needed', '--task-id', $safeTaskId, '--reason', 'Checker needs a human confirmation before continuing.')
    $humanNeededOk = $humanNeededResult.ExitCode -eq 0 -and (($humanNeededResult.Output | Out-String) -match 'status:\s+blocked_human_needed')
    Write-Check -Name 'CLI mark-human-needed' -Passed $humanNeededOk -Detail (($humanNeededResult.Output | Out-String).Trim())
    if (-not $humanNeededOk) { $failed++ }

    $postHumanSupervisorResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('supervisor-status')
    $postHumanSupervisorOk = $postHumanSupervisorResult.ExitCode -eq 0 -and (($postHumanSupervisorResult.Output | Out-String) -match 'human_needed_tasks:')
    Write-Check -Name 'Supervisor reflects human-needed state' -Passed $postHumanSupervisorOk -Detail (($postHumanSupervisorResult.Output | Out-String).Trim())
    if (-not $postHumanSupervisorOk) { $failed++ }
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
    '01_projects/runtime_mvp/runtime_data/approval_requests.json',
    '01_projects/runtime_mvp/runtime_data/supervisor_state.json',
    '01_projects/runtime_mvp/runtime_data/handoff_snapshot.md',
    '11_exports/reports/checker-council-report.md',
    '11_exports/github/checker-github-issue-issue-draft.md',
    '11_exports/github/checker-github-pr-pr-draft.md',
    '11_exports/personal_ops/primary-inbox-inbox-triage-pack.md',
    '11_exports/personal_ops/main-profile-linkedin-update-pack.md',
    '11_exports/personal_ops/ai-automation-lead-cv-update-pack.md',
    '11_exports/personal_ops/partner-contact-outreach-draft.md',
    '11_exports/personal_ops/example-labs-applied-ai-internship-internship-application-pack.md',
    '11_exports/personal_ops/super-ai-agent-showcase-case-study.md',
    '11_exports/personal_ops/super-ai-agent-portfolio-project-page.md'
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
