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

function Remove-GeneratedFile {
    param(
        [string]$Path
    )

    if (Test-Path -LiteralPath $Path -PathType Leaf) {
        Remove-Item -LiteralPath $Path -Force -ErrorAction SilentlyContinue
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
    '01_projects/runtime_mvp/src/super_ai_agent/brain.py',
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
    '04_docs/ghoti_control_center.md',
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
    '08_research/repo_integration_map.md',
    '08_research/career_ops_extraction_map.md',
    '08_research/repo_intake_matrix.md',
    '14_context/chat_handoff_latest.md',
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
    '23_configs/brain_provider.example.json',
    '23_configs/council_policy.example.json',
    '23_configs/personal_workflow_catalog.example.json',
    '23_configs/owned_account_policy.example.json',
    '23_configs/workflow_catalog.example.json',
    '23_configs/publish_policy.example.json',
    '23_configs/truth_council_policy.example.json',
    '01_projects/desktop_playground/desktop_bridge_actions.ps1'
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

$ghotiHelpResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('ghoti-help')
$ghotiHelpOk = $ghotiHelpResult.ExitCode -eq 0 -and `
    (($ghotiHelpResult.Output | Out-String) -match 'ghoti_help:\s+supervised local-first operator control overview') -and `
    (($ghotiHelpResult.Output | Out-String) -match 'dashboard_url:\s+http://127\.0\.0\.1:3210') -and `
    (($ghotiHelpResult.Output | Out-String) -match 'control_center_doc:\s+.*04_docs[\\/]+ghoti_control_center\.md') -and `
    (($ghotiHelpResult.Output | Out-String) -match 'Ctrl\+8') -and `
    (($ghotiHelpResult.Output | Out-String) -match 'no task deletion without explicit user approval') -and `
    (($ghotiHelpResult.Output | Out-String) -match 'floating Ghoti overlay')
Write-Check -Name 'CLI ghoti-help' -Passed $ghotiHelpOk -Detail (($ghotiHelpResult.Output | Out-String).Trim())
if (-not $ghotiHelpOk) { $failed++ }

$ghotiHotkeysResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('ghoti-hotkeys')
$ghotiHotkeysOk = $ghotiHotkeysResult.ExitCode -eq 0 -and `
    (($ghotiHotkeysResult.Output | Out-String) -match 'primary_hotkey:\s+Ctrl\+8') -and `
    (($ghotiHotkeysResult.Output | Out-String) -match 'after_interrupt:\s+') -and `
    (($ghotiHotkeysResult.Output | Out-String) -match 'handoff_safety:\s+') -and `
    (($ghotiHotkeysResult.Output | Out-String) -match 'overlay_visibility:\s+')
Write-Check -Name 'CLI ghoti-hotkeys' -Passed $ghotiHotkeysOk -Detail (($ghotiHotkeysResult.Output | Out-String).Trim())
if (-not $ghotiHotkeysOk) { $failed++ }

$ghotiStatusResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('ghoti-status')
$ghotiStatusOk = $ghotiStatusResult.ExitCode -eq 0 -and `
    (($ghotiStatusResult.Output | Out-String) -match 'ghoti_status:\s+local operator control snapshot') -and `
    (($ghotiStatusResult.Output | Out-String) -match 'dashboard_url:\s+http://127\.0\.0\.1:3210') -and `
    (($ghotiStatusResult.Output | Out-String) -match 'control_center_doc:\s+.*04_docs[\\/]+ghoti_control_center\.md') -and `
    (($ghotiStatusResult.Output | Out-String) -match 'ghoti_state:\s+\S+') -and `
    (($ghotiStatusResult.Output | Out-String) -match 'active_brain_provider:\s+\S+') -and `
    (($ghotiStatusResult.Output | Out-String) -match 'active_brain_model:\s+\S+') -and `
    (($ghotiStatusResult.Output | Out-String) -match 'current_specialist_role:\s+\S+') -and `
    (($ghotiStatusResult.Output | Out-String) -match 'current_specialist_role_provider:\s+\S+') -and `
    (($ghotiStatusResult.Output | Out-String) -match 'browser_use_installed:\s+(yes|no)') -and `
    (($ghotiStatusResult.Output | Out-String) -match 'playwright_ready:\s+(yes|no)') -and `
    (($ghotiStatusResult.Output | Out-String) -match 'compact_memory_ready:\s+(yes|no)') -and `
    (($ghotiStatusResult.Output | Out-String) -match 'current_task_used_model_inference:\s+(yes|no)') -and `
    (($ghotiStatusResult.Output | Out-String) -match 'last_model_call_status:\s+\S+') -and `
    (($ghotiStatusResult.Output | Out-String) -match 'watchdog_status:\s+\S+') -and `
    (($ghotiStatusResult.Output | Out-String) -match 'watchdog_headline:\s+') -and `
    (($ghotiStatusResult.Output | Out-String) -match 'overlay_target:\s+') -and `
    (($ghotiStatusResult.Output | Out-String) -match 'desktop_current_action:\s+\S+') -and `
    (($ghotiStatusResult.Output | Out-String) -match 'desktop_current_target:\s+') -and `
    (($ghotiStatusResult.Output | Out-String) -match 'desktop_current_typing_enabled:\s+(yes|no)') -and `
    (($ghotiStatusResult.Output | Out-String) -match 'desktop_visual_cue_status:\s+\S+') -and `
    (($ghotiStatusResult.Output | Out-String) -match 'watchdog_alerts:') -and `
    (($ghotiStatusResult.Output | Out-String) -match 'recent_actionable_tasks:') -and `
    (($ghotiStatusResult.Output | Out-String) -match 'recent_failures:') -and `
    (($ghotiStatusResult.Output | Out-String) -match 'what_to_do_next:')
Write-Check -Name 'CLI ghoti-status' -Passed $ghotiStatusOk -Detail (($ghotiStatusResult.Output | Out-String).Trim())
if (-not $ghotiStatusOk) { $failed++ }

$ghotiRecentResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('ghoti-recent')
$ghotiRecentOk = $ghotiRecentResult.ExitCode -eq 0 -and `
    (($ghotiRecentResult.Output | Out-String) -match 'ghoti_recent:\s+recent actionable work, failures, approvals, and artifacts') -and `
    (($ghotiRecentResult.Output | Out-String) -match 'active_brain_provider:\s+\S+') -and `
    (($ghotiRecentResult.Output | Out-String) -match 'active_brain_model:\s+\S+') -and `
    (($ghotiRecentResult.Output | Out-String) -match 'current_specialist_role:\s+\S+') -and `
    (($ghotiRecentResult.Output | Out-String) -match 'browser_use_installed:\s+(yes|no)') -and `
    (($ghotiRecentResult.Output | Out-String) -match 'playwright_ready:\s+(yes|no)') -and `
    (($ghotiRecentResult.Output | Out-String) -match 'compact_memory_ready:\s+(yes|no)') -and `
    (($ghotiRecentResult.Output | Out-String) -match 'current_task_used_model_inference:\s+(yes|no)') -and `
    (($ghotiRecentResult.Output | Out-String) -match 'last_model_call_status:\s+\S+') -and `
    (($ghotiRecentResult.Output | Out-String) -match 'watchdog_status:\s+\S+') -and `
    (($ghotiRecentResult.Output | Out-String) -match 'watchdog_headline:\s+') -and `
    (($ghotiRecentResult.Output | Out-String) -match 'overlay_target:\s+') -and `
    (($ghotiRecentResult.Output | Out-String) -match 'desktop_current_action:\s+\S+') -and `
    (($ghotiRecentResult.Output | Out-String) -match 'desktop_current_typing_enabled:\s+(yes|no)') -and `
    (($ghotiRecentResult.Output | Out-String) -match 'recent_actionable_tasks:') -and `
    (($ghotiRecentResult.Output | Out-String) -match 'active_only_tasks:') -and `
    (($ghotiRecentResult.Output | Out-String) -match 'recent_failures:') -and `
    (($ghotiRecentResult.Output | Out-String) -match 'watchdog_alerts:') -and `
    (($ghotiRecentResult.Output | Out-String) -match 'pending_approvals:') -and `
    (($ghotiRecentResult.Output | Out-String) -match 'recent_artifacts:')
Write-Check -Name 'CLI ghoti-recent' -Passed $ghotiRecentOk -Detail (($ghotiRecentResult.Output | Out-String).Trim())
if (-not $ghotiRecentOk) { $failed++ }

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

$brainStatusResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('brain-status')
$brainStatusOk = $brainStatusResult.ExitCode -eq 0 -and `
    (($brainStatusResult.Output | Out-String) -match 'brain_status:\s+local brain/provider snapshot') -and `
    (($brainStatusResult.Output | Out-String) -match 'active_brain_provider:\s+\S+') -and `
    (($brainStatusResult.Output | Out-String) -match 'active_brain_model:\s+\S+') -and `
    (($brainStatusResult.Output | Out-String) -match 'brain_inference_ready:\s+(yes|no)') -and `
    (($brainStatusResult.Output | Out-String) -match 'current_task_used_model_inference:\s+(yes|no)') -and `
    (($brainStatusResult.Output | Out-String) -match 'last_model_call_status:\s+\S+')
Write-Check -Name 'CLI brain-status' -Passed $brainStatusOk -Detail (($brainStatusResult.Output | Out-String).Trim())
if (-not $brainStatusOk) { $failed++ }

$listAgentRolesResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('list-agent-roles')
$listAgentRolesOk = $listAgentRolesResult.ExitCode -eq 0 -and `
    (($listAgentRolesResult.Output | Out-String) -match 'agent_roles:\s+specialist role registry snapshot') -and `
    (($listAgentRolesResult.Output | Out-String) -match 'current_specialist_role:\s+\S+') -and `
    (($listAgentRolesResult.Output | Out-String) -match 'current_specialist_role_provider:\s+\S+') -and `
    (($listAgentRolesResult.Output | Out-String) -match 'specialist_role_registry_count:\s+\d+') -and `
    (($listAgentRolesResult.Output | Out-String) -match 'roles:')
Write-Check -Name 'CLI list-agent-roles' -Passed $listAgentRolesOk -Detail (($listAgentRolesResult.Output | Out-String).Trim())
if (-not $listAgentRolesOk) { $failed++ }

$browserStatusResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('browser-status')
$browserStatusOk = $browserStatusResult.ExitCode -eq 0 -and `
    (($browserStatusResult.Output | Out-String) -match 'browser_status:\s+browser-agent capability snapshot') -and `
    (($browserStatusResult.Output | Out-String) -match 'browser_use_installed:\s+(yes|no)') -and `
    (($browserStatusResult.Output | Out-String) -match 'browser_use_ready:\s+(yes|no)') -and `
    (($browserStatusResult.Output | Out-String) -match 'playwright_installed:\s+(yes|no)') -and `
    (($browserStatusResult.Output | Out-String) -match 'playwright_ready:\s+(yes|no)') -and `
    (($browserStatusResult.Output | Out-String) -match 'current_browser_role:\s+\S+') -and `
    (($browserStatusResult.Output | Out-String) -match 'browser_notes:')
Write-Check -Name 'CLI browser-status' -Passed $browserStatusOk -Detail (($browserStatusResult.Output | Out-String).Trim())
if (-not $browserStatusOk) { $failed++ }

$memoryStatusResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('memory-status')
$memoryStatusOk = $memoryStatusResult.ExitCode -eq 0 -and `
    (($memoryStatusResult.Output | Out-String) -match 'memory_status:\s+compact markdown memory snapshot') -and `
    (($memoryStatusResult.Output | Out-String) -match 'compact_memory_ready:\s+(yes|no)') -and `
    (($memoryStatusResult.Output | Out-String) -match 'compact_memory_root:\s+') -and `
    (($memoryStatusResult.Output | Out-String) -match 'compact_memory_file_count:\s+\d+') -and `
    (($memoryStatusResult.Output | Out-String) -match 'compact_memory_notes:')
Write-Check -Name 'CLI memory-status' -Passed $memoryStatusOk -Detail (($memoryStatusResult.Output | Out-String).Trim())
if (-not $memoryStatusOk) { $failed++ }

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

    $ghotiFieldsOk = (($supervisorStatusResult.Output | Out-String) -match 'ghoti_state:\s+\S+') -and `
        (($supervisorStatusResult.Output | Out-String) -match 'operator_next_step:\s+\S+') -and `
        (($supervisorStatusResult.Output | Out-String) -match 'resource_guard_event_count:\s+\d+')
    Write-Check -Name 'Supervisor status reports Ghoti state fields' -Passed $ghotiFieldsOk -Detail (($supervisorStatusResult.Output | Out-String).Trim())
    if (-not $ghotiFieldsOk) { $failed++ }

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

    $taskStatusResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('task-status', '--task-id', $taskId)
    $taskStatusOk = $taskStatusResult.ExitCode -eq 0 -and `
        (($taskStatusResult.Output | Out-String) -match 'status:\s+completed') -and `
        (($taskStatusResult.Output | Out-String) -match 'history:') -and `
        (($taskStatusResult.Output | Out-String) -match '- completed \|')
    Write-Check -Name 'CLI task-status' -Passed $taskStatusOk -Detail (($taskStatusResult.Output | Out-String).Trim())
    if (-not $taskStatusOk) { $failed++ }
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

    $externalTaskIdMatch = [regex]::Match(($externalPathGuardResult.Output | Out-String), 'task_id:\s*(\S+)')
    $externalTaskId = if ($externalTaskIdMatch.Success) { $externalTaskIdMatch.Groups[1].Value } else { $null }
    $externalTaskIdOk = -not [string]::IsNullOrWhiteSpace($externalTaskId)
    Write-Check -Name 'External path task id parsed' -Passed $externalTaskIdOk -Detail ($(if ($externalTaskIdOk) { $externalTaskId } else { 'missing task id for external path guard scenario' }))
    if (-not $externalTaskIdOk) { $failed++ }

    if ($externalTaskIdOk) {
        $externalReviewResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('review-task', '--task-id', $externalTaskId, '--note', 'checker reviewed the workspace-blocked task')
        $externalReviewOk = $externalReviewResult.ExitCode -eq 0 -and `
            (($externalReviewResult.Output | Out-String) -match 'status:\s+blocked_human_needed') -and `
            (($externalReviewResult.Output | Out-String) -match 'workspace_policy:\s+blocked_by_workspace_policy')
        Write-Check -Name 'Workspace-blocked task stays blocked after review' -Passed $externalReviewOk -Detail (($externalReviewResult.Output | Out-String).Trim())
        if (-not $externalReviewOk) { $failed++ }
    }
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

    $reviewTaskResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('review-task', '--task-id', $safeTaskId, '--note', 'checker reviewed the human-needed task')
    $reviewTaskOk = $reviewTaskResult.ExitCode -eq 0 -and `
        (($reviewTaskResult.Output | Out-String) -match 'status:\s+ready_to_resume') -and `
        (($reviewTaskResult.Output | Out-String) -match 'next_action:\s+Re-queue the task')
    Write-Check -Name 'CLI review-task' -Passed $reviewTaskOk -Detail (($reviewTaskResult.Output | Out-String).Trim())
    if (-not $reviewTaskOk) { $failed++ }

    $requeueTaskResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('requeue-task', '--task-id', $safeTaskId, '--note', 'checker re-queued the reviewed task')
    $requeueTaskOk = $requeueTaskResult.ExitCode -eq 0 -and `
        (($requeueTaskResult.Output | Out-String) -match 'status:\s+queued')
    Write-Check -Name 'CLI requeue-task' -Passed $requeueTaskOk -Detail (($requeueTaskResult.Output | Out-String).Trim())
    if (-not $requeueTaskOk) { $failed++ }

    $reviewedTaskStatusResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('task-status', '--task-id', $safeTaskId)
    $reviewedTaskStatusOk = $reviewedTaskStatusResult.ExitCode -eq 0 -and `
        (($reviewedTaskStatusResult.Output | Out-String) -match 'history:') -and `
        (($reviewedTaskStatusResult.Output | Out-String) -match '- human_needed \|') -and `
        (($reviewedTaskStatusResult.Output | Out-String) -match '- ready_to_resume \|') -and `
        (($reviewedTaskStatusResult.Output | Out-String) -match '- resumed \|')
    Write-Check -Name 'Task history reflects manual supervisor loop' -Passed $reviewedTaskStatusOk -Detail (($reviewedTaskStatusResult.Output | Out-String).Trim())
    if (-not $reviewedTaskStatusOk) { $failed++ }
}

$executorReadResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @(
    'queue-executor-action',
    '--action-type', 'read_file',
    '--target', '14_context/current_state.md'
)
$executorReadQueuedOk = $executorReadResult.ExitCode -eq 0 -and `
    (($executorReadResult.Output | Out-String) -match 'status:\s+queued') -and `
    (($executorReadResult.Output | Out-String) -match 'approval_state:\s+not_required') -and `
    (($executorReadResult.Output | Out-String) -match 'executor_action_type:\s+read_file') -and `
    (($executorReadResult.Output | Out-String) -match 'workspace_scope:\s+in_scope')
Write-Check -Name 'Executor read_file queue stays in scope' -Passed $executorReadQueuedOk -Detail (($executorReadResult.Output | Out-String).Trim())
if (-not $executorReadQueuedOk) { $failed++ }

$executorReadTaskMatch = [regex]::Match(($executorReadResult.Output | Out-String), 'task_id:\s*(\S+)')
$executorReadTaskId = if ($executorReadTaskMatch.Success) { $executorReadTaskMatch.Groups[1].Value } else { $null }
$executorReadTaskOk = -not [string]::IsNullOrWhiteSpace($executorReadTaskId)
Write-Check -Name 'Executor read_file task id parsed' -Passed $executorReadTaskOk -Detail ($(if ($executorReadTaskOk) { $executorReadTaskId } else { 'missing read_file task id' }))
if (-not $executorReadTaskOk) { $failed++ }

if ($executorReadTaskOk) {
    $executorReadExecute = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('execute-task', '--task-id', $executorReadTaskId)
    $executorReadExecuteOk = $executorReadExecute.ExitCode -eq 0 -and `
        (($executorReadExecute.Output | Out-String) -match 'status:\s+completed') -and `
        (($executorReadExecute.Output | Out-String) -match 'execution_status:\s+succeeded')
    Write-Check -Name 'Executor read_file execution succeeds' -Passed $executorReadExecuteOk -Detail (($executorReadExecute.Output | Out-String).Trim())
    if (-not $executorReadExecuteOk) { $failed++ }

    $executorReadStatus = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('task-status', '--task-id', $executorReadTaskId)
    $executorReadStatusOk = $executorReadStatus.ExitCode -eq 0 -and `
        (($executorReadStatus.Output | Out-String) -match 'execution_count:\s+1') -and `
        (($executorReadStatus.Output | Out-String) -match 'last_execution_status:\s+succeeded') -and `
        (($executorReadStatus.Output | Out-String) -match 'execution_history:') -and `
        (($executorReadStatus.Output | Out-String) -match '- succeeded \|')
    Write-Check -Name 'Executor read_file result persists in task history' -Passed $executorReadStatusOk -Detail (($executorReadStatus.Output | Out-String).Trim())
    if (-not $executorReadStatusOk) { $failed++ }
}

$executorArtifactRelative = '11_exports/personal_ops/checker-executor-artifact.md'
$executorArtifactPath = Join-Path $repoRoot $executorArtifactRelative
$executorArtifactContent = "# Checker Executor Artifact`n`nCreated by the runtime checker."
$executorArtifactQueue = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @(
    'queue-executor-action',
    '--action-type', 'create_artifact',
    '--target', $executorArtifactRelative,
    '--content', $executorArtifactContent
)
$executorArtifactQueuedOk = $executorArtifactQueue.ExitCode -eq 0 -and `
    (($executorArtifactQueue.Output | Out-String) -match 'status:\s+pending_approval') -and `
    (($executorArtifactQueue.Output | Out-String) -match 'approval_state:\s+pending') -and `
    (($executorArtifactQueue.Output | Out-String) -match 'workspace_scope:\s+in_scope')
Write-Check -Name 'Executor create_artifact queues with approval' -Passed $executorArtifactQueuedOk -Detail (($executorArtifactQueue.Output | Out-String).Trim())
if (-not $executorArtifactQueuedOk) { $failed++ }

$executorArtifactTaskMatch = [regex]::Match(($executorArtifactQueue.Output | Out-String), 'task_id:\s*(\S+)')
$executorArtifactTaskId = if ($executorArtifactTaskMatch.Success) { $executorArtifactTaskMatch.Groups[1].Value } else { $null }
$executorArtifactTaskOk = -not [string]::IsNullOrWhiteSpace($executorArtifactTaskId)
Write-Check -Name 'Executor create_artifact task id parsed' -Passed $executorArtifactTaskOk -Detail ($(if ($executorArtifactTaskOk) { $executorArtifactTaskId } else { 'missing create_artifact task id' }))
if (-not $executorArtifactTaskOk) { $failed++ }

$executorArtifactApprovalMatch = [regex]::Match(($executorArtifactQueue.Output | Out-String), 'approval_request_id:\s*(\S+)')
$executorArtifactApprovalId = if ($executorArtifactApprovalMatch.Success) { $executorArtifactApprovalMatch.Groups[1].Value } else { $null }
$executorArtifactApprovalOk = -not [string]::IsNullOrWhiteSpace($executorArtifactApprovalId)
Write-Check -Name 'Executor create_artifact approval id parsed' -Passed $executorArtifactApprovalOk -Detail ($(if ($executorArtifactApprovalOk) { $executorArtifactApprovalId } else { 'missing create_artifact approval id' }))
if (-not $executorArtifactApprovalOk) { $failed++ }

if ($executorArtifactApprovalOk) {
    $executorArtifactApprove = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('approve-approval', '--approval-id', $executorArtifactApprovalId, '--note', 'runtime checker approved the artifact write')
    $executorArtifactApproveOk = $executorArtifactApprove.ExitCode -eq 0 -and `
        (($executorArtifactApprove.Output | Out-String) -match 'status:\s+approved') -and `
        (($executorArtifactApprove.Output | Out-String) -match 'task_status:\s+queued')
    Write-Check -Name 'Executor create_artifact approval persists' -Passed $executorArtifactApproveOk -Detail (($executorArtifactApprove.Output | Out-String).Trim())
    if (-not $executorArtifactApproveOk) { $failed++ }
}

if ($executorArtifactTaskOk) {
    $executorArtifactExecute = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('execute-task', '--task-id', $executorArtifactTaskId)
    $executorArtifactExecuteOk = $executorArtifactExecute.ExitCode -eq 0 -and `
        (($executorArtifactExecute.Output | Out-String) -match 'status:\s+completed') -and `
        (($executorArtifactExecute.Output | Out-String) -match 'execution_status:\s+succeeded') -and `
        (Test-Path -LiteralPath $executorArtifactPath -PathType Leaf)
    Write-Check -Name 'Executor create_artifact execution succeeds' -Passed $executorArtifactExecuteOk -Detail (($executorArtifactExecute.Output | Out-String).Trim())
    if (-not $executorArtifactExecuteOk) { $failed++ }

    $executorArtifactStatus = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('task-status', '--task-id', $executorArtifactTaskId)
    $executorArtifactStatusOk = $executorArtifactStatus.ExitCode -eq 0 -and `
        (($executorArtifactStatus.Output | Out-String) -match 'execution_count:\s+1') -and `
        (($executorArtifactStatus.Output | Out-String) -match 'last_execution_status:\s+succeeded') -and `
        (($executorArtifactStatus.Output | Out-String) -match "last_artifact_path:\s+$([regex]::Escape($executorArtifactPath))") -and `
        (($executorArtifactStatus.Output | Out-String) -match 'execution_history:') -and `
        (($executorArtifactStatus.Output | Out-String) -match '- succeeded \|')
    Write-Check -Name 'Executor create_artifact result persists' -Passed $executorArtifactStatusOk -Detail (($executorArtifactStatus.Output | Out-String).Trim())
    if (-not $executorArtifactStatusOk) { $failed++ }
}

$executorCheckerQueue = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @(
    'queue-executor-action',
    '--action-type', 'run_checker',
    '--target', 'dashboard'
)
$executorCheckerQueuedOk = $executorCheckerQueue.ExitCode -eq 0 -and `
    (($executorCheckerQueue.Output | Out-String) -match 'status:\s+pending_approval') -and `
    (($executorCheckerQueue.Output | Out-String) -match 'executor_action_type:\s+run_checker')
Write-Check -Name 'Executor run_checker queues with approval' -Passed $executorCheckerQueuedOk -Detail (($executorCheckerQueue.Output | Out-String).Trim())
if (-not $executorCheckerQueuedOk) { $failed++ }

$executorCheckerTaskMatch = [regex]::Match(($executorCheckerQueue.Output | Out-String), 'task_id:\s*(\S+)')
$executorCheckerTaskId = if ($executorCheckerTaskMatch.Success) { $executorCheckerTaskMatch.Groups[1].Value } else { $null }
$executorCheckerTaskOk = -not [string]::IsNullOrWhiteSpace($executorCheckerTaskId)
Write-Check -Name 'Executor checker task id parsed' -Passed $executorCheckerTaskOk -Detail ($(if ($executorCheckerTaskOk) { $executorCheckerTaskId } else { 'missing checker task id' }))
if (-not $executorCheckerTaskOk) { $failed++ }

$executorCheckerApprovalMatch = [regex]::Match(($executorCheckerQueue.Output | Out-String), 'approval_request_id:\s*(\S+)')
$executorCheckerApprovalId = if ($executorCheckerApprovalMatch.Success) { $executorCheckerApprovalMatch.Groups[1].Value } else { $null }
$executorCheckerApprovalOk = -not [string]::IsNullOrWhiteSpace($executorCheckerApprovalId)
Write-Check -Name 'Executor checker approval id parsed' -Passed $executorCheckerApprovalOk -Detail ($(if ($executorCheckerApprovalOk) { $executorCheckerApprovalId } else { 'missing checker approval id' }))
if (-not $executorCheckerApprovalOk) { $failed++ }

if ($executorCheckerApprovalOk) {
    $executorCheckerApprove = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('approve-approval', '--approval-id', $executorCheckerApprovalId, '--note', 'runtime checker approved dashboard checker execution')
    $executorCheckerApproveOk = $executorCheckerApprove.ExitCode -eq 0 -and `
        (($executorCheckerApprove.Output | Out-String) -match 'status:\s+approved') -and `
        (($executorCheckerApprove.Output | Out-String) -match 'task_status:\s+queued')
    Write-Check -Name 'Executor run_checker approval persists' -Passed $executorCheckerApproveOk -Detail (($executorCheckerApprove.Output | Out-String).Trim())
    if (-not $executorCheckerApproveOk) { $failed++ }
}

if ($executorCheckerTaskOk) {
    $executorCheckerExecute = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('execute-task', '--task-id', $executorCheckerTaskId)
    $executorCheckerExecuteOk = $executorCheckerExecute.ExitCode -eq 0 -and `
        (($executorCheckerExecute.Output | Out-String) -match 'status:\s+completed') -and `
        (($executorCheckerExecute.Output | Out-String) -match 'execution_status:\s+succeeded') -and `
        (($executorCheckerExecute.Output | Out-String) -match 'Summary:\s+dashboard MVP checks passed\.')
    Write-Check -Name 'Executor run_checker execution succeeds' -Passed $executorCheckerExecuteOk -Detail (($executorCheckerExecute.Output | Out-String).Trim())
    if (-not $executorCheckerExecuteOk) { $failed++ }

    $executorCheckerStatus = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('task-status', '--task-id', $executorCheckerTaskId)
    $executorCheckerStatusOk = $executorCheckerStatus.ExitCode -eq 0 -and `
        (($executorCheckerStatus.Output | Out-String) -match 'execution_count:\s+1') -and `
        (($executorCheckerStatus.Output | Out-String) -match 'last_execution_status:\s+succeeded') -and `
        (($executorCheckerStatus.Output | Out-String) -match 'last_execution_summary:\s+Summary:\s+dashboard MVP checks passed\.')
    Write-Check -Name 'Executor run_checker result persists' -Passed $executorCheckerStatusOk -Detail (($executorCheckerStatus.Output | Out-String).Trim())
    if (-not $executorCheckerStatusOk) { $failed++ }
}

$executorOutsideQueue = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @(
    'queue-executor-action',
    '--action-type', 'read_file',
    '--target', 'C:\Windows\Temp\checker-executor-outside.txt'
)
$executorOutsideQueuedOk = $executorOutsideQueue.ExitCode -eq 0 -and `
    (($executorOutsideQueue.Output | Out-String) -match 'status:\s+pending_approval') -and `
    (($executorOutsideQueue.Output | Out-String) -match 'workspace_scope:\s+out_of_scope') -and `
    (($executorOutsideQueue.Output | Out-String) -match 'workspace_policy:\s+blocked_by_workspace_policy')
Write-Check -Name 'Executor out-of-scope path is escalated and blocked' -Passed $executorOutsideQueuedOk -Detail (($executorOutsideQueue.Output | Out-String).Trim())
if (-not $executorOutsideQueuedOk) { $failed++ }

$executorOutsideTaskMatch = [regex]::Match(($executorOutsideQueue.Output | Out-String), 'task_id:\s*(\S+)')
$executorOutsideTaskId = if ($executorOutsideTaskMatch.Success) { $executorOutsideTaskMatch.Groups[1].Value } else { $null }
$executorOutsideTaskOk = -not [string]::IsNullOrWhiteSpace($executorOutsideTaskId)
Write-Check -Name 'Executor out-of-scope task id parsed' -Passed $executorOutsideTaskOk -Detail ($(if ($executorOutsideTaskOk) { $executorOutsideTaskId } else { 'missing out-of-scope executor task id' }))
if (-not $executorOutsideTaskOk) { $failed++ }

$executorOutsideApprovalMatch = [regex]::Match(($executorOutsideQueue.Output | Out-String), 'approval_request_id:\s*(\S+)')
$executorOutsideApprovalId = if ($executorOutsideApprovalMatch.Success) { $executorOutsideApprovalMatch.Groups[1].Value } else { $null }
$executorOutsideApprovalOk = -not [string]::IsNullOrWhiteSpace($executorOutsideApprovalId)
Write-Check -Name 'Executor out-of-scope approval id parsed' -Passed $executorOutsideApprovalOk -Detail ($(if ($executorOutsideApprovalOk) { $executorOutsideApprovalId } else { 'missing out-of-scope executor approval id' }))
if (-not $executorOutsideApprovalOk) { $failed++ }

if ($executorOutsideApprovalOk) {
    $executorOutsideApprove = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('approve-approval', '--approval-id', $executorOutsideApprovalId, '--note', 'runtime checker recorded the out-of-scope executor request')
    $executorOutsideApproveOk = $executorOutsideApprove.ExitCode -eq 0 -and `
        (($executorOutsideApprove.Output | Out-String) -match 'task_status:\s+blocked_human_needed') -and `
        (($executorOutsideApprove.Output | Out-String) -match 'workspace_policy:\s+blocked_by_workspace_policy')
    Write-Check -Name 'Executor out-of-scope task stays blocked after approval' -Passed $executorOutsideApproveOk -Detail (($executorOutsideApprove.Output | Out-String).Trim())
    if (-not $executorOutsideApproveOk) { $failed++ }
}

if ($executorOutsideTaskOk) {
    $executorOutsideStatus = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('task-status', '--task-id', $executorOutsideTaskId)
    $executorOutsideStatusOk = $executorOutsideStatus.ExitCode -eq 0 -and `
        (($executorOutsideStatus.Output | Out-String) -match 'status:\s+blocked_human_needed') -and `
        (($executorOutsideStatus.Output | Out-String) -match 'workspace_policy:\s+blocked_by_workspace_policy')
    Write-Check -Name 'Executor out-of-scope task remains blocked in task status' -Passed $executorOutsideStatusOk -Detail (($executorOutsideStatus.Output | Out-String).Trim())
    if (-not $executorOutsideStatusOk) { $failed++ }
}

$desktopListQueue = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @(
    'queue-executor-action',
    '--action-type', 'list_windows'
)
$desktopListQueueOk = $desktopListQueue.ExitCode -eq 0 -and `
    (($desktopListQueue.Output | Out-String) -match 'status:\s+queued') -and `
    (($desktopListQueue.Output | Out-String) -match 'approval_state:\s+not_required') -and `
    (($desktopListQueue.Output | Out-String) -match 'executor_action_type:\s+list_windows')
Write-Check -Name 'Desktop executor list_windows queues without approval' -Passed $desktopListQueueOk -Detail (($desktopListQueue.Output | Out-String).Trim())
if (-not $desktopListQueueOk) { $failed++ }

$desktopListTaskMatch = [regex]::Match(($desktopListQueue.Output | Out-String), 'task_id:\s*(\S+)')
$desktopListTaskId = if ($desktopListTaskMatch.Success) { $desktopListTaskMatch.Groups[1].Value } else { $null }
$desktopListTaskOk = -not [string]::IsNullOrWhiteSpace($desktopListTaskId)
Write-Check -Name 'Desktop executor list_windows task id parsed' -Passed $desktopListTaskOk -Detail ($(if ($desktopListTaskOk) { $desktopListTaskId } else { 'missing list_windows task id' }))
if (-not $desktopListTaskOk) { $failed++ }

if ($desktopListTaskOk) {
    $desktopListExecute = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('execute-task', '--task-id', $desktopListTaskId)
    $desktopListExecuteOk = $desktopListExecute.ExitCode -eq 0 -and `
        (($desktopListExecute.Output | Out-String) -match 'status:\s+completed') -and `
        (($desktopListExecute.Output | Out-String) -match 'execution_status:\s+succeeded')
    Write-Check -Name 'Desktop executor list_windows execution succeeds' -Passed $desktopListExecuteOk -Detail (($desktopListExecute.Output | Out-String).Trim())
    if (-not $desktopListExecuteOk) { $failed++ }
}

$desktopActiveQueue = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @(
    'queue-executor-action',
    '--action-type', 'get_active_window'
)
$desktopActiveQueueOk = $desktopActiveQueue.ExitCode -eq 0 -and `
    (($desktopActiveQueue.Output | Out-String) -match 'status:\s+queued') -and `
    (($desktopActiveQueue.Output | Out-String) -match 'executor_action_type:\s+get_active_window')
Write-Check -Name 'Desktop executor get_active_window queues without approval' -Passed $desktopActiveQueueOk -Detail (($desktopActiveQueue.Output | Out-String).Trim())
if (-not $desktopActiveQueueOk) { $failed++ }

$desktopActiveTaskMatch = [regex]::Match(($desktopActiveQueue.Output | Out-String), 'task_id:\s*(\S+)')
$desktopActiveTaskId = if ($desktopActiveTaskMatch.Success) { $desktopActiveTaskMatch.Groups[1].Value } else { $null }
$desktopActiveTaskOk = -not [string]::IsNullOrWhiteSpace($desktopActiveTaskId)
Write-Check -Name 'Desktop executor get_active_window task id parsed' -Passed $desktopActiveTaskOk -Detail ($(if ($desktopActiveTaskOk) { $desktopActiveTaskId } else { 'missing get_active_window task id' }))
if (-not $desktopActiveTaskOk) { $failed++ }

if ($desktopActiveTaskOk) {
    $desktopActiveExecute = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('execute-task', '--task-id', $desktopActiveTaskId)
    $desktopActiveExecuteOk = $desktopActiveExecute.ExitCode -eq 0 -and `
        (($desktopActiveExecute.Output | Out-String) -match 'status:\s+completed') -and `
        (($desktopActiveExecute.Output | Out-String) -match 'execution_status:\s+succeeded')
    Write-Check -Name 'Desktop executor get_active_window execution succeeds' -Passed $desktopActiveExecuteOk -Detail (($desktopActiveExecute.Output | Out-String).Trim())
    if (-not $desktopActiveExecuteOk) { $failed++ }
}

$desktopOpenQueue = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @(
    'queue-executor-action',
    '--action-type', 'open_allowed_app',
    '--target', 'terminal'
)
$desktopOpenQueueOk = $desktopOpenQueue.ExitCode -eq 0 -and `
    (($desktopOpenQueue.Output | Out-String) -match 'status:\s+pending_approval') -and `
    (($desktopOpenQueue.Output | Out-String) -match 'executor_action_type:\s+open_allowed_app')
Write-Check -Name 'Desktop executor open_allowed_app queues with approval' -Passed $desktopOpenQueueOk -Detail (($desktopOpenQueue.Output | Out-String).Trim())
if (-not $desktopOpenQueueOk) { $failed++ }

$desktopOpenTaskMatch = [regex]::Match(($desktopOpenQueue.Output | Out-String), 'task_id:\s*(\S+)')
$desktopOpenTaskId = if ($desktopOpenTaskMatch.Success) { $desktopOpenTaskMatch.Groups[1].Value } else { $null }
$desktopOpenApprovalMatch = [regex]::Match(($desktopOpenQueue.Output | Out-String), 'approval_request_id:\s*(\S+)')
$desktopOpenApprovalId = if ($desktopOpenApprovalMatch.Success) { $desktopOpenApprovalMatch.Groups[1].Value } else { $null }
$desktopOpenIdsOk = (-not [string]::IsNullOrWhiteSpace($desktopOpenTaskId)) -and (-not [string]::IsNullOrWhiteSpace($desktopOpenApprovalId))
Write-Check -Name 'Desktop executor open_allowed_app ids parsed' -Passed $desktopOpenIdsOk -Detail ($(if ($desktopOpenIdsOk) { "$desktopOpenTaskId | $desktopOpenApprovalId" } else { 'missing open_allowed_app task or approval id' }))
if (-not $desktopOpenIdsOk) { $failed++ }

if (-not [string]::IsNullOrWhiteSpace($desktopOpenApprovalId)) {
    $desktopOpenApprove = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('approve-approval', '--approval-id', $desktopOpenApprovalId, '--note', 'runtime checker approved open_allowed_app')
    $desktopOpenApproveOk = $desktopOpenApprove.ExitCode -eq 0 -and `
        (($desktopOpenApprove.Output | Out-String) -match 'task_status:\s+queued')
    Write-Check -Name 'Desktop executor open_allowed_app approval persists' -Passed $desktopOpenApproveOk -Detail (($desktopOpenApprove.Output | Out-String).Trim())
    if (-not $desktopOpenApproveOk) { $failed++ }
}

if (-not [string]::IsNullOrWhiteSpace($desktopOpenTaskId)) {
    $desktopOpenExecute = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('execute-task', '--task-id', $desktopOpenTaskId)
    $desktopOpenExecuteText = ($desktopOpenExecute.Output | Out-String)
    $desktopOpenExecuteOk = $desktopOpenExecute.ExitCode -eq 0 -and (
        (
            ($desktopOpenExecuteText -match 'status:\s+completed') -and
            ($desktopOpenExecuteText -match 'execution_status:\s+succeeded')
        ) -or (
            ($desktopOpenExecuteText -match 'status:\s+blocked_human_needed') -and
            ($desktopOpenExecuteText -match 'execution_status:\s+failed') -and
            ($desktopOpenExecuteText -match 'manual operator focus|Resource guard blocked opening another terminal window')
        )
    )
    Write-Check -Name 'Desktop executor open_allowed_app execution stays honest about focus reuse or manual focus blocking' -Passed $desktopOpenExecuteOk -Detail $desktopOpenExecuteText.Trim()
    if (-not $desktopOpenExecuteOk) { $failed++ }

    $desktopOpenStatus = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('task-status', '--task-id', $desktopOpenTaskId)
    $desktopOpenStatusText = ($desktopOpenStatus.Output | Out-String)
    $desktopOpenStatusOk = $desktopOpenStatus.ExitCode -eq 0 -and (
        (
            ($desktopOpenStatusText -match 'last_execution_status:\s+succeeded') -and
            (
                ($desktopOpenStatusText -match 'last_execution_summary:\s+Focused existing allowlisted app window') -or
                ($desktopOpenStatusText -match 'last_execution_summary:\s+Opened allowlisted app:\s+terminal')
            )
        ) -or (
            ($desktopOpenStatusText -match 'status:\s+blocked_human_needed') -and
            ($desktopOpenStatusText -match 'last_execution_status:\s+failed') -and
            ($desktopOpenStatusText -match 'manual operator focus|Resource guard blocked opening another terminal window')
        )
    )
    Write-Check -Name 'Desktop executor open_allowed_app reports reuse-first success or clear manual-focus blocking' -Passed $desktopOpenStatusOk -Detail $desktopOpenStatusText.Trim()
    if (-not $desktopOpenStatusOk) { $failed++ }
}

$desktopGuardQueue = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @(
    'queue-executor-action',
    '--action-type', 'open_allowed_app',
    '--target', 'terminal'
)
$desktopGuardQueueOk = $desktopGuardQueue.ExitCode -eq 0 -and `
    (($desktopGuardQueue.Output | Out-String) -match 'status:\s+pending_approval') -and `
    (($desktopGuardQueue.Output | Out-String) -match 'executor_action_type:\s+open_allowed_app')
Write-Check -Name 'Desktop resource-guard task queues for terminal open' -Passed $desktopGuardQueueOk -Detail (($desktopGuardQueue.Output | Out-String).Trim())
if (-not $desktopGuardQueueOk) { $failed++ }

$desktopGuardTaskMatch = [regex]::Match(($desktopGuardQueue.Output | Out-String), 'task_id:\s*(\S+)')
$desktopGuardTaskId = if ($desktopGuardTaskMatch.Success) { $desktopGuardTaskMatch.Groups[1].Value } else { $null }
$desktopGuardApprovalMatch = [regex]::Match(($desktopGuardQueue.Output | Out-String), 'approval_request_id:\s*(\S+)')
$desktopGuardApprovalId = if ($desktopGuardApprovalMatch.Success) { $desktopGuardApprovalMatch.Groups[1].Value } else { $null }
$desktopGuardIdsOk = (-not [string]::IsNullOrWhiteSpace($desktopGuardTaskId)) -and (-not [string]::IsNullOrWhiteSpace($desktopGuardApprovalId))
Write-Check -Name 'Desktop resource-guard ids parsed' -Passed $desktopGuardIdsOk -Detail ($(if ($desktopGuardIdsOk) { "$desktopGuardTaskId | $desktopGuardApprovalId" } else { 'missing resource-guard task or approval id' }))
if (-not $desktopGuardIdsOk) { $failed++ }

if (-not [string]::IsNullOrWhiteSpace($desktopGuardApprovalId)) {
    $desktopGuardApprove = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('approve-approval', '--approval-id', $desktopGuardApprovalId, '--note', 'runtime checker approved the guarded terminal open')
    $desktopGuardApproveOk = $desktopGuardApprove.ExitCode -eq 0 -and `
        (($desktopGuardApprove.Output | Out-String) -match 'task_status:\s+queued')
    Write-Check -Name 'Desktop resource-guard approval persists' -Passed $desktopGuardApproveOk -Detail (($desktopGuardApprove.Output | Out-String).Trim())
    if (-not $desktopGuardApproveOk) { $failed++ }
}

if (-not [string]::IsNullOrWhiteSpace($desktopGuardTaskId)) {
    $desktopGuardExecute = Invoke-ModuleCommand `
        -PythonPath $pythonPath `
        -Arguments @('execute-task', '--task-id', $desktopGuardTaskId) `
        -EnvOverrides @{
            SUPER_AGENT_DESKTOP_TEST_TERMINAL_WINDOW_COUNT = '3'
            SUPER_AGENT_DESKTOP_TEST_TERMINAL_PROCESS_COUNT = '6'
            SUPER_AGENT_DESKTOP_TEST_FORCE_RESOURCE_GUARD = '1'
        }
    $desktopGuardExecuteOk = $desktopGuardExecute.ExitCode -eq 0 -and `
        (($desktopGuardExecute.Output | Out-String) -match 'status:\s+blocked_human_needed') -and `
        (($desktopGuardExecute.Output | Out-String) -match 'execution_status:\s+failed') -and `
        (($desktopGuardExecute.Output | Out-String) -match 'resource guard')
    Write-Check -Name 'Desktop resource guard blocks duplicate terminal spawning in runtime executor' -Passed $desktopGuardExecuteOk -Detail (($desktopGuardExecute.Output | Out-String).Trim())
    if (-not $desktopGuardExecuteOk) { $failed++ }

    $desktopGuardStatus = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('task-status', '--task-id', $desktopGuardTaskId)
    $desktopGuardStatusOk = $desktopGuardStatus.ExitCode -eq 0 -and `
        (($desktopGuardStatus.Output | Out-String) -match 'status:\s+blocked_human_needed') -and `
        (($desktopGuardStatus.Output | Out-String) -match 'last_resource_guard_reason:\s+\S+') -and `
        (($desktopGuardStatus.Output | Out-String) -match 'waiting_for:\s+resource_guard_review')
    Write-Check -Name 'Runtime task status persists resource guard blocking detail' -Passed $desktopGuardStatusOk -Detail (($desktopGuardStatus.Output | Out-String).Trim())
    if (-not $desktopGuardStatusOk) { $failed++ }

    $guardSupervisorStatus = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('supervisor-status')
    $guardSupervisorStatusOk = $guardSupervisorStatus.ExitCode -eq 0 -and `
        (($guardSupervisorStatus.Output | Out-String) -match 'ghoti_state:\s+resource_guard_triggered') -and `
        (($guardSupervisorStatus.Output | Out-String) -match 'resource_guard_event_count:\s+[1-9]')
    Write-Check -Name 'Supervisor reflects resource guard state clearly' -Passed $guardSupervisorStatusOk -Detail (($guardSupervisorStatus.Output | Out-String).Trim())
    if (-not $guardSupervisorStatusOk) { $failed++ }
}

Start-Sleep -Milliseconds 1200

$desktopFocusQueue = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @(
    'queue-executor-action',
    '--action-type', 'focus_window',
    '--target', 'terminal'
)
$desktopFocusQueueOk = $desktopFocusQueue.ExitCode -eq 0 -and `
    (($desktopFocusQueue.Output | Out-String) -match 'status:\s+pending_approval') -and `
    (($desktopFocusQueue.Output | Out-String) -match 'executor_action_type:\s+focus_window')
Write-Check -Name 'Desktop executor focus_window queues with approval' -Passed $desktopFocusQueueOk -Detail (($desktopFocusQueue.Output | Out-String).Trim())
if (-not $desktopFocusQueueOk) { $failed++ }

$desktopFocusTaskMatch = [regex]::Match(($desktopFocusQueue.Output | Out-String), 'task_id:\s*(\S+)')
$desktopFocusTaskId = if ($desktopFocusTaskMatch.Success) { $desktopFocusTaskMatch.Groups[1].Value } else { $null }
$desktopFocusApprovalMatch = [regex]::Match(($desktopFocusQueue.Output | Out-String), 'approval_request_id:\s*(\S+)')
$desktopFocusApprovalId = if ($desktopFocusApprovalMatch.Success) { $desktopFocusApprovalMatch.Groups[1].Value } else { $null }
$desktopFocusIdsOk = (-not [string]::IsNullOrWhiteSpace($desktopFocusTaskId)) -and (-not [string]::IsNullOrWhiteSpace($desktopFocusApprovalId))
Write-Check -Name 'Desktop executor focus_window ids parsed' -Passed $desktopFocusIdsOk -Detail ($(if ($desktopFocusIdsOk) { "$desktopFocusTaskId | $desktopFocusApprovalId" } else { 'missing focus_window task or approval id' }))
if (-not $desktopFocusIdsOk) { $failed++ }

if (-not [string]::IsNullOrWhiteSpace($desktopFocusApprovalId)) {
    $desktopFocusApprove = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('approve-approval', '--approval-id', $desktopFocusApprovalId, '--note', 'runtime checker approved focus_window')
    $desktopFocusApproveOk = $desktopFocusApprove.ExitCode -eq 0 -and `
        (($desktopFocusApprove.Output | Out-String) -match 'task_status:\s+queued')
    Write-Check -Name 'Desktop executor focus_window approval persists' -Passed $desktopFocusApproveOk -Detail (($desktopFocusApprove.Output | Out-String).Trim())
    if (-not $desktopFocusApproveOk) { $failed++ }
}

if (-not [string]::IsNullOrWhiteSpace($desktopFocusTaskId)) {
    $desktopFocusExecute = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('execute-task', '--task-id', $desktopFocusTaskId)
    $desktopFocusExecuteText = ($desktopFocusExecute.Output | Out-String)
    $desktopFocusExecuteOk = $desktopFocusExecute.ExitCode -eq 0 -and (
        (
            ($desktopFocusExecuteText -match 'status:\s+completed') -and
            ($desktopFocusExecuteText -match 'execution_status:\s+succeeded')
        ) -or (
            ($desktopFocusExecuteText -match 'status:\s+blocked_human_needed') -and
            ($desktopFocusExecuteText -match 'execution_status:\s+failed') -and
            ($desktopFocusExecuteText -match 'manual operator focus|manual target resolution is required')
        )
    )
    Write-Check -Name 'Desktop executor focus_window execution succeeds or blocks safely for manual focus' -Passed $desktopFocusExecuteOk -Detail $desktopFocusExecuteText.Trim()
    if (-not $desktopFocusExecuteOk) { $failed++ }
}

$runtimeDesktopArtifactPath = Join-Path $repoRoot '05_logs\tmp\desktop\runtime-checker-desktop-capture.png'
Remove-GeneratedFile -Path $runtimeDesktopArtifactPath
$desktopScreenshotQueue = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @(
    'queue-executor-action',
    '--action-type', 'capture_desktop_screenshot',
    '--target', $runtimeDesktopArtifactPath
)
$desktopScreenshotQueueOk = $desktopScreenshotQueue.ExitCode -eq 0 -and `
    (($desktopScreenshotQueue.Output | Out-String) -match 'status:\s+pending_approval') -and `
    (($desktopScreenshotQueue.Output | Out-String) -match 'workspace_scope:\s+in_scope')
Write-Check -Name 'Desktop executor screenshot queues with approval' -Passed $desktopScreenshotQueueOk -Detail (($desktopScreenshotQueue.Output | Out-String).Trim())
if (-not $desktopScreenshotQueueOk) { $failed++ }

$desktopScreenshotTaskMatch = [regex]::Match(($desktopScreenshotQueue.Output | Out-String), 'task_id:\s*(\S+)')
$desktopScreenshotTaskId = if ($desktopScreenshotTaskMatch.Success) { $desktopScreenshotTaskMatch.Groups[1].Value } else { $null }
$desktopScreenshotApprovalMatch = [regex]::Match(($desktopScreenshotQueue.Output | Out-String), 'approval_request_id:\s*(\S+)')
$desktopScreenshotApprovalId = if ($desktopScreenshotApprovalMatch.Success) { $desktopScreenshotApprovalMatch.Groups[1].Value } else { $null }
$desktopScreenshotIdsOk = (-not [string]::IsNullOrWhiteSpace($desktopScreenshotTaskId)) -and (-not [string]::IsNullOrWhiteSpace($desktopScreenshotApprovalId))
Write-Check -Name 'Desktop executor screenshot ids parsed' -Passed $desktopScreenshotIdsOk -Detail ($(if ($desktopScreenshotIdsOk) { "$desktopScreenshotTaskId | $desktopScreenshotApprovalId" } else { 'missing screenshot task or approval id' }))
if (-not $desktopScreenshotIdsOk) { $failed++ }

if (-not [string]::IsNullOrWhiteSpace($desktopScreenshotApprovalId)) {
    $desktopScreenshotApprove = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('approve-approval', '--approval-id', $desktopScreenshotApprovalId, '--note', 'runtime checker approved screenshot capture')
    $desktopScreenshotApproveOk = $desktopScreenshotApprove.ExitCode -eq 0 -and `
        (($desktopScreenshotApprove.Output | Out-String) -match 'task_status:\s+queued')
    Write-Check -Name 'Desktop executor screenshot approval persists' -Passed $desktopScreenshotApproveOk -Detail (($desktopScreenshotApprove.Output | Out-String).Trim())
    if (-not $desktopScreenshotApproveOk) { $failed++ }
}

if (-not [string]::IsNullOrWhiteSpace($desktopScreenshotTaskId)) {
    $desktopScreenshotExecute = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('execute-task', '--task-id', $desktopScreenshotTaskId)
    $desktopScreenshotExecuteText = ($desktopScreenshotExecute.Output | Out-String)
    $desktopScreenshotExecuteOk = $desktopScreenshotExecute.ExitCode -eq 0 -and (
        (
            ($desktopScreenshotExecuteText -match 'status:\s+completed') -and
            ($desktopScreenshotExecuteText -match 'execution_status:\s+succeeded') -and
            (Test-Path -LiteralPath $runtimeDesktopArtifactPath -PathType Leaf)
        ) -or (
            ($desktopScreenshotExecuteText -match 'status:\s+blocked_human_needed') -and
            ($desktopScreenshotExecuteText -match 'execution_status:\s+failed') -and
            ($desktopScreenshotExecuteText -match 'manual screenshot is required')
        )
    )
    Write-Check -Name 'Desktop executor screenshot execution succeeds or blocks safely for manual capture' -Passed $desktopScreenshotExecuteOk -Detail $desktopScreenshotExecuteText.Trim()
    if (-not $desktopScreenshotExecuteOk) { $failed++ }

    $desktopScreenshotStatus = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('task-status', '--task-id', $desktopScreenshotTaskId)
    $desktopScreenshotStatusText = ($desktopScreenshotStatus.Output | Out-String)
    $desktopScreenshotStatusOk = $desktopScreenshotStatus.ExitCode -eq 0 -and (
        (
            ($desktopScreenshotStatusText -match "last_artifact_path:\s+$([regex]::Escape($runtimeDesktopArtifactPath))") -and
            ($desktopScreenshotStatusText -match 'last_execution_status:\s+succeeded')
        ) -or (
            ($desktopScreenshotStatusText -match 'status:\s+blocked_human_needed') -and
            ($desktopScreenshotStatusText -match 'last_execution_status:\s+failed') -and
            ($desktopScreenshotStatusText -match 'manual screenshot is required')
        )
    )
    Write-Check -Name 'Desktop executor screenshot result persists or reports manual capture blocking clearly' -Passed $desktopScreenshotStatusOk -Detail $desktopScreenshotStatusText.Trim()
    if (-not $desktopScreenshotStatusOk) { $failed++ }
}

$desktopSetClipboardQueue = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @(
    'queue-executor-action',
    '--action-type', 'set_clipboard_text',
    '--content', 'runtime-desktop-clipboard-check'
)
$desktopSetClipboardQueueOk = $desktopSetClipboardQueue.ExitCode -eq 0 -and `
    (($desktopSetClipboardQueue.Output | Out-String) -match 'status:\s+pending_approval') -and `
    (($desktopSetClipboardQueue.Output | Out-String) -match 'executor_action_type:\s+set_clipboard_text')
Write-Check -Name 'Desktop executor set_clipboard_text queues with approval' -Passed $desktopSetClipboardQueueOk -Detail (($desktopSetClipboardQueue.Output | Out-String).Trim())
if (-not $desktopSetClipboardQueueOk) { $failed++ }

$desktopSetClipboardTaskMatch = [regex]::Match(($desktopSetClipboardQueue.Output | Out-String), 'task_id:\s*(\S+)')
$desktopSetClipboardTaskId = if ($desktopSetClipboardTaskMatch.Success) { $desktopSetClipboardTaskMatch.Groups[1].Value } else { $null }
$desktopSetClipboardApprovalMatch = [regex]::Match(($desktopSetClipboardQueue.Output | Out-String), 'approval_request_id:\s*(\S+)')
$desktopSetClipboardApprovalId = if ($desktopSetClipboardApprovalMatch.Success) { $desktopSetClipboardApprovalMatch.Groups[1].Value } else { $null }
$desktopSetClipboardIdsOk = (-not [string]::IsNullOrWhiteSpace($desktopSetClipboardTaskId)) -and (-not [string]::IsNullOrWhiteSpace($desktopSetClipboardApprovalId))
Write-Check -Name 'Desktop executor set_clipboard_text ids parsed' -Passed $desktopSetClipboardIdsOk -Detail ($(if ($desktopSetClipboardIdsOk) { "$desktopSetClipboardTaskId | $desktopSetClipboardApprovalId" } else { 'missing set_clipboard_text task or approval id' }))
if (-not $desktopSetClipboardIdsOk) { $failed++ }

if (-not [string]::IsNullOrWhiteSpace($desktopSetClipboardApprovalId)) {
    $desktopSetClipboardApprove = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('approve-approval', '--approval-id', $desktopSetClipboardApprovalId, '--note', 'runtime checker approved set_clipboard_text')
    $desktopSetClipboardApproveOk = $desktopSetClipboardApprove.ExitCode -eq 0 -and `
        (($desktopSetClipboardApprove.Output | Out-String) -match 'task_status:\s+queued')
    Write-Check -Name 'Desktop executor set_clipboard_text approval persists' -Passed $desktopSetClipboardApproveOk -Detail (($desktopSetClipboardApprove.Output | Out-String).Trim())
    if (-not $desktopSetClipboardApproveOk) { $failed++ }
}

if (-not [string]::IsNullOrWhiteSpace($desktopSetClipboardTaskId)) {
    $desktopSetClipboardExecute = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('execute-task', '--task-id', $desktopSetClipboardTaskId)
    $desktopSetClipboardExecuteOk = $desktopSetClipboardExecute.ExitCode -eq 0 -and `
        (($desktopSetClipboardExecute.Output | Out-String) -match 'status:\s+completed') -and `
        (($desktopSetClipboardExecute.Output | Out-String) -match 'execution_summary:\s+Updated clipboard text\.')
    Write-Check -Name 'Desktop executor set_clipboard_text execution succeeds' -Passed $desktopSetClipboardExecuteOk -Detail (($desktopSetClipboardExecute.Output | Out-String).Trim())
    if (-not $desktopSetClipboardExecuteOk) { $failed++ }
}

$desktopReadClipboardQueue = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @(
    'queue-executor-action',
    '--action-type', 'get_clipboard_text'
)
$desktopReadClipboardQueueOk = $desktopReadClipboardQueue.ExitCode -eq 0 -and `
    (($desktopReadClipboardQueue.Output | Out-String) -match 'status:\s+queued') -and `
    (($desktopReadClipboardQueue.Output | Out-String) -match 'executor_action_type:\s+get_clipboard_text')
Write-Check -Name 'Desktop executor get_clipboard_text queues without approval' -Passed $desktopReadClipboardQueueOk -Detail (($desktopReadClipboardQueue.Output | Out-String).Trim())
if (-not $desktopReadClipboardQueueOk) { $failed++ }

$desktopReadClipboardTaskMatch = [regex]::Match(($desktopReadClipboardQueue.Output | Out-String), 'task_id:\s*(\S+)')
$desktopReadClipboardTaskId = if ($desktopReadClipboardTaskMatch.Success) { $desktopReadClipboardTaskMatch.Groups[1].Value } else { $null }
$desktopReadClipboardTaskOk = -not [string]::IsNullOrWhiteSpace($desktopReadClipboardTaskId)
Write-Check -Name 'Desktop executor get_clipboard_text task id parsed' -Passed $desktopReadClipboardTaskOk -Detail ($(if ($desktopReadClipboardTaskOk) { $desktopReadClipboardTaskId } else { 'missing get_clipboard_text task id' }))
if (-not $desktopReadClipboardTaskOk) { $failed++ }

if ($desktopReadClipboardTaskOk) {
    $desktopReadClipboardExecute = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('execute-task', '--task-id', $desktopReadClipboardTaskId)
    $desktopReadClipboardExecuteOk = $desktopReadClipboardExecute.ExitCode -eq 0 -and `
        (($desktopReadClipboardExecute.Output | Out-String) -match 'status:\s+completed') -and `
        (($desktopReadClipboardExecute.Output | Out-String) -match 'execution_summary:\s+Read clipboard text\.')
    Write-Check -Name 'Desktop executor get_clipboard_text execution succeeds' -Passed $desktopReadClipboardExecuteOk -Detail (($desktopReadClipboardExecute.Output | Out-String).Trim())
    if (-not $desktopReadClipboardExecuteOk) { $failed++ }

    $desktopReadClipboardStatus = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('task-status', '--task-id', $desktopReadClipboardTaskId)
    $desktopReadClipboardStatusOk = $desktopReadClipboardStatus.ExitCode -eq 0 -and `
        (($desktopReadClipboardStatus.Output | Out-String) -match 'last_execution_status:\s+succeeded') -and `
        (($desktopReadClipboardStatus.Output | Out-String) -match 'last_execution_summary:\s+Read clipboard text\.')
    Write-Check -Name 'Desktop executor clipboard read result persists' -Passed $desktopReadClipboardStatusOk -Detail (($desktopReadClipboardStatus.Output | Out-String).Trim())
    if (-not $desktopReadClipboardStatusOk) { $failed++ }
}

$desktopPasteQueue = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @(
    'queue-executor-action',
    '--action-type', 'paste_clipboard',
    '--target', 'terminal'
)
$desktopPasteQueueOk = $desktopPasteQueue.ExitCode -eq 0 -and `
    (($desktopPasteQueue.Output | Out-String) -match 'status:\s+pending_approval') -and `
    (($desktopPasteQueue.Output | Out-String) -match 'executor_action_type:\s+paste_clipboard')
Write-Check -Name 'Desktop executor paste_clipboard queues with approval' -Passed $desktopPasteQueueOk -Detail (($desktopPasteQueue.Output | Out-String).Trim())
if (-not $desktopPasteQueueOk) { $failed++ }

$desktopPasteTaskMatch = [regex]::Match(($desktopPasteQueue.Output | Out-String), 'task_id:\s*(\S+)')
$desktopPasteTaskId = if ($desktopPasteTaskMatch.Success) { $desktopPasteTaskMatch.Groups[1].Value } else { $null }
$desktopPasteApprovalMatch = [regex]::Match(($desktopPasteQueue.Output | Out-String), 'approval_request_id:\s*(\S+)')
$desktopPasteApprovalId = if ($desktopPasteApprovalMatch.Success) { $desktopPasteApprovalMatch.Groups[1].Value } else { $null }
$desktopPasteIdsOk = (-not [string]::IsNullOrWhiteSpace($desktopPasteTaskId)) -and (-not [string]::IsNullOrWhiteSpace($desktopPasteApprovalId))
Write-Check -Name 'Desktop executor paste_clipboard ids parsed' -Passed $desktopPasteIdsOk -Detail ($(if ($desktopPasteIdsOk) { "$desktopPasteTaskId | $desktopPasteApprovalId" } else { 'missing paste_clipboard task or approval id' }))
if (-not $desktopPasteIdsOk) { $failed++ }

if (-not [string]::IsNullOrWhiteSpace($desktopPasteApprovalId)) {
    $desktopPasteApprove = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('approve-approval', '--approval-id', $desktopPasteApprovalId, '--note', 'runtime checker approved paste_clipboard')
    $desktopPasteApproveOk = $desktopPasteApprove.ExitCode -eq 0 -and `
        (($desktopPasteApprove.Output | Out-String) -match 'task_status:\s+queued')
    Write-Check -Name 'Desktop executor paste_clipboard approval persists' -Passed $desktopPasteApproveOk -Detail (($desktopPasteApprove.Output | Out-String).Trim())
    if (-not $desktopPasteApproveOk) { $failed++ }
}

if (-not [string]::IsNullOrWhiteSpace($desktopPasteTaskId)) {
    $desktopPasteExecute = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('execute-task', '--task-id', $desktopPasteTaskId)
    $desktopPasteExecuteText = ($desktopPasteExecute.Output | Out-String)
    $desktopPasteExecuteOk = $desktopPasteExecute.ExitCode -eq 0 -and (
        (
            ($desktopPasteExecuteText -match 'status:\s+completed') -and
            ($desktopPasteExecuteText -match 'execution_summary:\s+Pasted clipboard into allowlisted window')
        ) -or (
            ($desktopPasteExecuteText -match 'status:\s+blocked_human_needed') -and
            ($desktopPasteExecuteText -match 'execution_status:\s+failed') -and
            ($desktopPasteExecuteText -match 'manual operator focus|manual target resolution is required')
        )
    )
    Write-Check -Name 'Desktop executor paste_clipboard execution succeeds or blocks safely for manual focus' -Passed $desktopPasteExecuteOk -Detail $desktopPasteExecuteText.Trim()
    if (-not $desktopPasteExecuteOk) { $failed++ }
}

$desktopHotkeyQueue = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @(
    'queue-executor-action',
    '--action-type', 'send_hotkey',
    '--target', 'terminal|ctrl+v'
)
$desktopHotkeyQueueOk = $desktopHotkeyQueue.ExitCode -eq 0 -and `
    (($desktopHotkeyQueue.Output | Out-String) -match 'status:\s+pending_approval') -and `
    (($desktopHotkeyQueue.Output | Out-String) -match 'executor_action_type:\s+send_hotkey')
Write-Check -Name 'Desktop executor send_hotkey queues with approval' -Passed $desktopHotkeyQueueOk -Detail (($desktopHotkeyQueue.Output | Out-String).Trim())
if (-not $desktopHotkeyQueueOk) { $failed++ }

$desktopHotkeyTaskMatch = [regex]::Match(($desktopHotkeyQueue.Output | Out-String), 'task_id:\s*(\S+)')
$desktopHotkeyTaskId = if ($desktopHotkeyTaskMatch.Success) { $desktopHotkeyTaskMatch.Groups[1].Value } else { $null }
$desktopHotkeyApprovalMatch = [regex]::Match(($desktopHotkeyQueue.Output | Out-String), 'approval_request_id:\s*(\S+)')
$desktopHotkeyApprovalId = if ($desktopHotkeyApprovalMatch.Success) { $desktopHotkeyApprovalMatch.Groups[1].Value } else { $null }
$desktopHotkeyIdsOk = (-not [string]::IsNullOrWhiteSpace($desktopHotkeyTaskId)) -and (-not [string]::IsNullOrWhiteSpace($desktopHotkeyApprovalId))
Write-Check -Name 'Desktop executor send_hotkey ids parsed' -Passed $desktopHotkeyIdsOk -Detail ($(if ($desktopHotkeyIdsOk) { "$desktopHotkeyTaskId | $desktopHotkeyApprovalId" } else { 'missing send_hotkey task or approval id' }))
if (-not $desktopHotkeyIdsOk) { $failed++ }

if (-not [string]::IsNullOrWhiteSpace($desktopHotkeyApprovalId)) {
    $desktopHotkeyApprove = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('approve-approval', '--approval-id', $desktopHotkeyApprovalId, '--note', 'runtime checker approved send_hotkey')
    $desktopHotkeyApproveOk = $desktopHotkeyApprove.ExitCode -eq 0 -and `
        (($desktopHotkeyApprove.Output | Out-String) -match 'task_status:\s+queued')
    Write-Check -Name 'Desktop executor send_hotkey approval persists' -Passed $desktopHotkeyApproveOk -Detail (($desktopHotkeyApprove.Output | Out-String).Trim())
    if (-not $desktopHotkeyApproveOk) { $failed++ }
}

if (-not [string]::IsNullOrWhiteSpace($desktopHotkeyTaskId)) {
    $desktopHotkeyExecute = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('execute-task', '--task-id', $desktopHotkeyTaskId)
    $desktopHotkeyExecuteText = ($desktopHotkeyExecute.Output | Out-String)
    $desktopHotkeyExecuteOk = $desktopHotkeyExecute.ExitCode -eq 0 -and (
        (
            ($desktopHotkeyExecuteText -match 'status:\s+completed') -and
            ($desktopHotkeyExecuteText -match 'execution_summary:\s+Sent allowlisted hotkey ctrl\+v to terminal')
        ) -or (
            ($desktopHotkeyExecuteText -match 'status:\s+blocked_human_needed') -and
            ($desktopHotkeyExecuteText -match 'execution_status:\s+failed') -and
            ($desktopHotkeyExecuteText -match 'manual operator focus|manual target resolution is required')
        )
    )
    Write-Check -Name 'Desktop executor send_hotkey execution succeeds or blocks safely for manual focus' -Passed $desktopHotkeyExecuteOk -Detail $desktopHotkeyExecuteText.Trim()
    if (-not $desktopHotkeyExecuteOk) { $failed++ }
}

$clipboardGuardSetQueue = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @(
    'queue-executor-action',
    '--action-type', 'set_clipboard_text',
    '--content', 'Run Desktop Bridge Check'
)
$clipboardGuardSetQueueOk = $clipboardGuardSetQueue.ExitCode -eq 0 -and `
    (($clipboardGuardSetQueue.Output | Out-String) -match 'status:\s+pending_approval')
Write-Check -Name 'Clipboard guard seed queue succeeds' -Passed $clipboardGuardSetQueueOk -Detail (($clipboardGuardSetQueue.Output | Out-String).Trim())
if (-not $clipboardGuardSetQueueOk) { $failed++ }

$clipboardGuardSetTaskMatch = [regex]::Match(($clipboardGuardSetQueue.Output | Out-String), 'task_id:\s*(\S+)')
$clipboardGuardSetTaskId = if ($clipboardGuardSetTaskMatch.Success) { $clipboardGuardSetTaskMatch.Groups[1].Value } else { $null }
$clipboardGuardSetApprovalMatch = [regex]::Match(($clipboardGuardSetQueue.Output | Out-String), 'approval_request_id:\s*(\S+)')
$clipboardGuardSetApprovalId = if ($clipboardGuardSetApprovalMatch.Success) { $clipboardGuardSetApprovalMatch.Groups[1].Value } else { $null }

if (-not [string]::IsNullOrWhiteSpace($clipboardGuardSetApprovalId)) {
    $clipboardGuardSetApprove = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('approve-approval', '--approval-id', $clipboardGuardSetApprovalId, '--note', 'runtime checker seeded suspicious clipboard text')
    $clipboardGuardSetApproveOk = $clipboardGuardSetApprove.ExitCode -eq 0
    Write-Check -Name 'Clipboard guard seed approval persists' -Passed $clipboardGuardSetApproveOk -Detail (($clipboardGuardSetApprove.Output | Out-String).Trim())
    if (-not $clipboardGuardSetApproveOk) { $failed++ }
}

if (-not [string]::IsNullOrWhiteSpace($clipboardGuardSetTaskId)) {
    $clipboardGuardSetExecute = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('execute-task', '--task-id', $clipboardGuardSetTaskId)
    $clipboardGuardSetExecuteOk = $clipboardGuardSetExecute.ExitCode -eq 0 -and `
        (($clipboardGuardSetExecute.Output | Out-String) -match 'status:\s+completed')
    Write-Check -Name 'Clipboard guard seed execution succeeds' -Passed $clipboardGuardSetExecuteOk -Detail (($clipboardGuardSetExecute.Output | Out-String).Trim())
    if (-not $clipboardGuardSetExecuteOk) { $failed++ }
}

$clipboardGuardPasteQueue = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @(
    'queue-executor-action',
    '--action-type', 'paste_clipboard',
    '--target', 'terminal'
)
$clipboardGuardPasteQueueOk = $clipboardGuardPasteQueue.ExitCode -eq 0 -and `
    (($clipboardGuardPasteQueue.Output | Out-String) -match 'status:\s+pending_approval')
Write-Check -Name 'Clipboard guard paste task queues' -Passed $clipboardGuardPasteQueueOk -Detail (($clipboardGuardPasteQueue.Output | Out-String).Trim())
if (-not $clipboardGuardPasteQueueOk) { $failed++ }

$clipboardGuardPasteTaskMatch = [regex]::Match(($clipboardGuardPasteQueue.Output | Out-String), 'task_id:\s*(\S+)')
$clipboardGuardPasteTaskId = if ($clipboardGuardPasteTaskMatch.Success) { $clipboardGuardPasteTaskMatch.Groups[1].Value } else { $null }
$clipboardGuardPasteApprovalMatch = [regex]::Match(($clipboardGuardPasteQueue.Output | Out-String), 'approval_request_id:\s*(\S+)')
$clipboardGuardPasteApprovalId = if ($clipboardGuardPasteApprovalMatch.Success) { $clipboardGuardPasteApprovalMatch.Groups[1].Value } else { $null }

if (-not [string]::IsNullOrWhiteSpace($clipboardGuardPasteApprovalId)) {
    $clipboardGuardPasteApprove = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('approve-approval', '--approval-id', $clipboardGuardPasteApprovalId, '--note', 'runtime checker approved guarded paste test')
    $clipboardGuardPasteApproveOk = $clipboardGuardPasteApprove.ExitCode -eq 0
    Write-Check -Name 'Clipboard guard paste approval persists' -Passed $clipboardGuardPasteApproveOk -Detail (($clipboardGuardPasteApprove.Output | Out-String).Trim())
    if (-not $clipboardGuardPasteApproveOk) { $failed++ }
}

if (-not [string]::IsNullOrWhiteSpace($clipboardGuardPasteTaskId)) {
    $clipboardGuardPasteExecute = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('execute-task', '--task-id', $clipboardGuardPasteTaskId)
    $clipboardGuardPasteExecuteOk = $clipboardGuardPasteExecute.ExitCode -eq 0 -and `
        (($clipboardGuardPasteExecute.Output | Out-String) -match 'status:\s+blocked_human_needed') -and `
        (($clipboardGuardPasteExecute.Output | Out-String) -match 'execution_status:\s+failed') -and `
        (($clipboardGuardPasteExecute.Output | Out-String) -match '(Clipboard guard blocked|checker or recipe label|payload was blocked)')
    Write-Check -Name 'Clipboard guard blocks suspicious paste into terminal' -Passed $clipboardGuardPasteExecuteOk -Detail (($clipboardGuardPasteExecute.Output | Out-String).Trim())
    if (-not $clipboardGuardPasteExecuteOk) { $failed++ }
}

$desktopWaitForWindowQueue = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @(
    'queue-executor-action',
    '--action-type', 'wait_for_window',
    '--target', 'terminal|2'
)
$desktopWaitForWindowQueueOk = $desktopWaitForWindowQueue.ExitCode -eq 0 -and `
    (($desktopWaitForWindowQueue.Output | Out-String) -match 'status:\s+queued') -and `
    (($desktopWaitForWindowQueue.Output | Out-String) -match 'executor_action_type:\s+wait_for_window')
Write-Check -Name 'Desktop executor wait_for_window queues without approval' -Passed $desktopWaitForWindowQueueOk -Detail (($desktopWaitForWindowQueue.Output | Out-String).Trim())
if (-not $desktopWaitForWindowQueueOk) { $failed++ }

$desktopWaitForWindowTaskMatch = [regex]::Match(($desktopWaitForWindowQueue.Output | Out-String), 'task_id:\s*(\S+)')
$desktopWaitForWindowTaskId = if ($desktopWaitForWindowTaskMatch.Success) { $desktopWaitForWindowTaskMatch.Groups[1].Value } else { $null }
$desktopWaitForWindowTaskOk = -not [string]::IsNullOrWhiteSpace($desktopWaitForWindowTaskId)
Write-Check -Name 'Desktop executor wait_for_window task id parsed' -Passed $desktopWaitForWindowTaskOk -Detail ($(if ($desktopWaitForWindowTaskOk) { $desktopWaitForWindowTaskId } else { 'missing wait_for_window task id' }))
if (-not $desktopWaitForWindowTaskOk) { $failed++ }

if ($desktopWaitForWindowTaskOk) {
    $desktopWaitForWindowExecute = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('execute-task', '--task-id', $desktopWaitForWindowTaskId)
    $desktopWaitForWindowExecuteText = ($desktopWaitForWindowExecute.Output | Out-String)
    $desktopWaitForWindowExecuteOk = $desktopWaitForWindowExecute.ExitCode -eq 0 -and (
        (
            $desktopWaitForWindowExecuteText -match 'status:\s+completed' -and
            $desktopWaitForWindowExecuteText -match 'execution_summary:\s+Detected allowlisted window: terminal'
        ) -or (
            $desktopWaitForWindowExecuteText -match 'status:\s+failed' -and
            $desktopWaitForWindowExecuteText -match 'Timed out waiting for allowlisted window: terminal'
        )
    )
    Write-Check -Name 'Desktop executor wait_for_window execution succeeds' -Passed $desktopWaitForWindowExecuteOk -Detail $desktopWaitForWindowExecuteText.Trim()
    if (-not $desktopWaitForWindowExecuteOk) { $failed++ }
}

$desktopMoveMouseQueue = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @(
    'queue-executor-action',
    '--action-type', 'move_mouse',
    '--target', 'terminal|center'
)
$desktopMoveMouseQueueOk = $desktopMoveMouseQueue.ExitCode -eq 0 -and `
    (($desktopMoveMouseQueue.Output | Out-String) -match 'status:\s+pending_approval') -and `
    (($desktopMoveMouseQueue.Output | Out-String) -match 'executor_action_type:\s+move_mouse')
Write-Check -Name 'Desktop executor move_mouse queues with approval' -Passed $desktopMoveMouseQueueOk -Detail (($desktopMoveMouseQueue.Output | Out-String).Trim())
if (-not $desktopMoveMouseQueueOk) { $failed++ }

$desktopMoveMouseTaskMatch = [regex]::Match(($desktopMoveMouseQueue.Output | Out-String), 'task_id:\s*(\S+)')
$desktopMoveMouseTaskId = if ($desktopMoveMouseTaskMatch.Success) { $desktopMoveMouseTaskMatch.Groups[1].Value } else { $null }
$desktopMoveMouseApprovalMatch = [regex]::Match(($desktopMoveMouseQueue.Output | Out-String), 'approval_request_id:\s*(\S+)')
$desktopMoveMouseApprovalId = if ($desktopMoveMouseApprovalMatch.Success) { $desktopMoveMouseApprovalMatch.Groups[1].Value } else { $null }
$desktopMoveMouseIdsOk = (-not [string]::IsNullOrWhiteSpace($desktopMoveMouseTaskId)) -and (-not [string]::IsNullOrWhiteSpace($desktopMoveMouseApprovalId))
Write-Check -Name 'Desktop executor move_mouse ids parsed' -Passed $desktopMoveMouseIdsOk -Detail ($(if ($desktopMoveMouseIdsOk) { "$desktopMoveMouseTaskId | $desktopMoveMouseApprovalId" } else { 'missing move_mouse task or approval id' }))
if (-not $desktopMoveMouseIdsOk) { $failed++ }

if (-not [string]::IsNullOrWhiteSpace($desktopMoveMouseApprovalId)) {
    $desktopMoveMouseApprove = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('approve-approval', '--approval-id', $desktopMoveMouseApprovalId, '--note', 'runtime checker approved move_mouse')
    $desktopMoveMouseApproveOk = $desktopMoveMouseApprove.ExitCode -eq 0 -and `
        (($desktopMoveMouseApprove.Output | Out-String) -match 'task_status:\s+queued')
    Write-Check -Name 'Desktop executor move_mouse approval persists' -Passed $desktopMoveMouseApproveOk -Detail (($desktopMoveMouseApprove.Output | Out-String).Trim())
    if (-not $desktopMoveMouseApproveOk) { $failed++ }
}

if (-not [string]::IsNullOrWhiteSpace($desktopMoveMouseTaskId)) {
    $desktopMoveMouseExecute = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('execute-task', '--task-id', $desktopMoveMouseTaskId)
    $desktopMoveMouseExecuteText = ($desktopMoveMouseExecute.Output | Out-String)
    $desktopMoveMouseExecuteOk = $desktopMoveMouseExecute.ExitCode -eq 0 -and (
        (
            ($desktopMoveMouseExecuteText -match 'status:\s+completed') -and
            ($desktopMoveMouseExecuteText -match 'execution_summary:\s+Moved mouse to')
        ) -or (
            ($desktopMoveMouseExecuteText -match 'status:\s+blocked_human_needed') -and
            ($desktopMoveMouseExecuteText -match 'execution_status:\s+failed') -and
            ($desktopMoveMouseExecuteText -match 'manual operator focus')
        ) -or (
            ($desktopMoveMouseExecuteText -match 'status:\s+failed') -and
            ($desktopMoveMouseExecuteText -match 'Timed out waiting for allowlisted window: terminal')
        )
    )
    Write-Check -Name 'Desktop executor move_mouse execution succeeds or blocks safely for manual focus' -Passed $desktopMoveMouseExecuteOk -Detail $desktopMoveMouseExecuteText.Trim()
    if (-not $desktopMoveMouseExecuteOk) { $failed++ }
}

$desktopLeftClickQueue = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @(
    'queue-executor-action',
    '--action-type', 'left_click',
    '--target', 'terminal|center'
)
$desktopLeftClickQueueOk = $desktopLeftClickQueue.ExitCode -eq 0 -and `
    (($desktopLeftClickQueue.Output | Out-String) -match 'status:\s+pending_approval') -and `
    (($desktopLeftClickQueue.Output | Out-String) -match 'executor_action_type:\s+left_click')
Write-Check -Name 'Desktop executor left_click queues with approval' -Passed $desktopLeftClickQueueOk -Detail (($desktopLeftClickQueue.Output | Out-String).Trim())
if (-not $desktopLeftClickQueueOk) { $failed++ }

$desktopLeftClickTaskMatch = [regex]::Match(($desktopLeftClickQueue.Output | Out-String), 'task_id:\s*(\S+)')
$desktopLeftClickTaskId = if ($desktopLeftClickTaskMatch.Success) { $desktopLeftClickTaskMatch.Groups[1].Value } else { $null }
$desktopLeftClickApprovalMatch = [regex]::Match(($desktopLeftClickQueue.Output | Out-String), 'approval_request_id:\s*(\S+)')
$desktopLeftClickApprovalId = if ($desktopLeftClickApprovalMatch.Success) { $desktopLeftClickApprovalMatch.Groups[1].Value } else { $null }
$desktopLeftClickIdsOk = (-not [string]::IsNullOrWhiteSpace($desktopLeftClickTaskId)) -and (-not [string]::IsNullOrWhiteSpace($desktopLeftClickApprovalId))
Write-Check -Name 'Desktop executor left_click ids parsed' -Passed $desktopLeftClickIdsOk -Detail ($(if ($desktopLeftClickIdsOk) { "$desktopLeftClickTaskId | $desktopLeftClickApprovalId" } else { 'missing left_click task or approval id' }))
if (-not $desktopLeftClickIdsOk) { $failed++ }

if (-not [string]::IsNullOrWhiteSpace($desktopLeftClickApprovalId)) {
    $desktopLeftClickApprove = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('approve-approval', '--approval-id', $desktopLeftClickApprovalId, '--note', 'runtime checker approved left_click')
    $desktopLeftClickApproveOk = $desktopLeftClickApprove.ExitCode -eq 0 -and `
        (($desktopLeftClickApprove.Output | Out-String) -match 'task_status:\s+queued')
    Write-Check -Name 'Desktop executor left_click approval persists' -Passed $desktopLeftClickApproveOk -Detail (($desktopLeftClickApprove.Output | Out-String).Trim())
    if (-not $desktopLeftClickApproveOk) { $failed++ }
}

if (-not [string]::IsNullOrWhiteSpace($desktopLeftClickTaskId)) {
    $desktopLeftClickExecute = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('execute-task', '--task-id', $desktopLeftClickTaskId)
    $desktopLeftClickExecuteText = ($desktopLeftClickExecute.Output | Out-String)
    $desktopLeftClickExecuteOk = $desktopLeftClickExecute.ExitCode -eq 0 -and (
        (
            ($desktopLeftClickExecuteText -match 'status:\s+completed') -and
            ($desktopLeftClickExecuteText -match 'execution_summary:\s+Left click completed at')
        ) -or (
            ($desktopLeftClickExecuteText -match 'status:\s+blocked_human_needed') -and
            ($desktopLeftClickExecuteText -match 'execution_status:\s+failed') -and
            ($desktopLeftClickExecuteText -match 'manual operator focus')
        ) -or (
            ($desktopLeftClickExecuteText -match 'status:\s+failed') -and
            ($desktopLeftClickExecuteText -match 'Timed out waiting for allowlisted window: terminal')
        )
    )
    Write-Check -Name 'Desktop executor left_click execution succeeds or blocks safely for manual focus' -Passed $desktopLeftClickExecuteOk -Detail $desktopLeftClickExecuteText.Trim()
    if (-not $desktopLeftClickExecuteOk) { $failed++ }
}

$desktopInterruptQueue = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @(
    'queue-executor-action',
    '--action-type', 'wait_seconds',
    '--target', '5'
)
$desktopInterruptQueueOk = $desktopInterruptQueue.ExitCode -eq 0 -and `
    (($desktopInterruptQueue.Output | Out-String) -match 'status:\s+queued') -and `
    (($desktopInterruptQueue.Output | Out-String) -match 'executor_action_type:\s+wait_seconds')
Write-Check -Name 'Desktop executor wait_seconds queues without approval for failsafe test' -Passed $desktopInterruptQueueOk -Detail (($desktopInterruptQueue.Output | Out-String).Trim())
if (-not $desktopInterruptQueueOk) { $failed++ }

$desktopInterruptTaskMatch = [regex]::Match(($desktopInterruptQueue.Output | Out-String), 'task_id:\s*(\S+)')
$desktopInterruptTaskId = if ($desktopInterruptTaskMatch.Success) { $desktopInterruptTaskMatch.Groups[1].Value } else { $null }
$desktopInterruptTaskOk = -not [string]::IsNullOrWhiteSpace($desktopInterruptTaskId)
Write-Check -Name 'Desktop executor interrupt task id parsed' -Passed $desktopInterruptTaskOk -Detail ($(if ($desktopInterruptTaskOk) { $desktopInterruptTaskId } else { 'missing wait_seconds interrupt task id' }))
if (-not $desktopInterruptTaskOk) { $failed++ }

if ($desktopInterruptTaskOk) {
    $desktopInterruptExecute = Invoke-ModuleCommand `
        -PythonPath $pythonPath `
        -Arguments @('execute-task', '--task-id', $desktopInterruptTaskId) `
        -EnvOverrides @{ SUPER_AGENT_DESKTOP_TEST_INTERRUPT_AFTER_MS = '300' }
    $desktopInterruptExecuteOk = $desktopInterruptExecute.ExitCode -eq 0 -and `
        (($desktopInterruptExecute.Output | Out-String) -match 'status:\s+interrupted') -and `
        (($desktopInterruptExecute.Output | Out-String) -match 'execution_status:\s+interrupted') -and `
        (($desktopInterruptExecute.Output | Out-String) -match 'Ctrl\+8')
    Write-Check -Name 'Desktop executor Ctrl+8 failsafe interruption persists' -Passed $desktopInterruptExecuteOk -Detail (($desktopInterruptExecute.Output | Out-String).Trim())
    if (-not $desktopInterruptExecuteOk) { $failed++ }

    $desktopInterruptStatus = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('task-status', '--task-id', $desktopInterruptTaskId)
    $desktopInterruptStatusOk = $desktopInterruptStatus.ExitCode -eq 0 -and `
        (($desktopInterruptStatus.Output | Out-String) -match 'status:\s+interrupted') -and `
        (($desktopInterruptStatus.Output | Out-String) -match 'last_execution_status:\s+interrupted') -and `
        (($desktopInterruptStatus.Output | Out-String) -match 'waiting_for:\s+operator_review_after_interrupt')
    Write-Check -Name 'Interrupted desktop task stays stopped for operator review' -Passed $desktopInterruptStatusOk -Detail (($desktopInterruptStatus.Output | Out-String).Trim())
    if (-not $desktopInterruptStatusOk) { $failed++ }

    $desktopInterruptReview = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('review-task', '--task-id', $desktopInterruptTaskId, '--note', 'runtime checker reviewed the interrupted desktop task')
    $desktopInterruptReviewOk = $desktopInterruptReview.ExitCode -eq 0 -and `
        (($desktopInterruptReview.Output | Out-String) -match 'status:\s+ready_to_resume')
    Write-Check -Name 'Interrupted desktop task can be marked reviewed manually' -Passed $desktopInterruptReviewOk -Detail (($desktopInterruptReview.Output | Out-String).Trim())
    if (-not $desktopInterruptReviewOk) { $failed++ }

    $desktopInterruptRequeue = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('requeue-task', '--task-id', $desktopInterruptTaskId, '--note', 'runtime checker re-queued the interrupted desktop task')
    $desktopInterruptRequeueOk = $desktopInterruptRequeue.ExitCode -eq 0 -and `
        (($desktopInterruptRequeue.Output | Out-String) -match 'status:\s+queued')
    Write-Check -Name 'Interrupted desktop task only continues after explicit re-queue' -Passed $desktopInterruptRequeueOk -Detail (($desktopInterruptRequeue.Output | Out-String).Trim())
    if (-not $desktopInterruptRequeueOk) { $failed++ }
}

$desktopRetryQueue = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @(
    'queue-executor-action',
    '--action-type', 'focus_window',
    '--target', 'terminal'
)
$desktopRetryQueueOk = $desktopRetryQueue.ExitCode -eq 0 -and `
    (($desktopRetryQueue.Output | Out-String) -match 'status:\s+pending_approval') -and `
    (($desktopRetryQueue.Output | Out-String) -match 'executor_action_type:\s+focus_window')
Write-Check -Name 'Desktop retry-limit task queues' -Passed $desktopRetryQueueOk -Detail (($desktopRetryQueue.Output | Out-String).Trim())
if (-not $desktopRetryQueueOk) { $failed++ }

$desktopRetryTaskMatch = [regex]::Match(($desktopRetryQueue.Output | Out-String), 'task_id:\s*(\S+)')
$desktopRetryTaskId = if ($desktopRetryTaskMatch.Success) { $desktopRetryTaskMatch.Groups[1].Value } else { $null }
$desktopRetryApprovalMatch = [regex]::Match(($desktopRetryQueue.Output | Out-String), 'approval_request_id:\s*(\S+)')
$desktopRetryApprovalId = if ($desktopRetryApprovalMatch.Success) { $desktopRetryApprovalMatch.Groups[1].Value } else { $null }

if (-not [string]::IsNullOrWhiteSpace($desktopRetryApprovalId)) {
    $desktopRetryApprove = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('approve-approval', '--approval-id', $desktopRetryApprovalId, '--note', 'runtime checker approved retry-limit focus_window test')
    $desktopRetryApproveOk = $desktopRetryApprove.ExitCode -eq 0
    Write-Check -Name 'Desktop retry-limit approval persists' -Passed $desktopRetryApproveOk -Detail (($desktopRetryApprove.Output | Out-String).Trim())
    if (-not $desktopRetryApproveOk) { $failed++ }
}

if (-not [string]::IsNullOrWhiteSpace($desktopRetryTaskId)) {
    $desktopRetryExecute = Invoke-ModuleCommand `
        -PythonPath $pythonPath `
        -Arguments @('execute-task', '--task-id', $desktopRetryTaskId) `
        -EnvOverrides @{ SUPER_AGENT_DESKTOP_TEST_FAIL_ACTIONS = 'focus_window' }
    $desktopRetryExecuteOk = $desktopRetryExecute.ExitCode -eq 0 -and `
        (($desktopRetryExecute.Output | Out-String) -match 'status:\s+failed') -and `
        (($desktopRetryExecute.Output | Out-String) -match 'execution_status:\s+failed')
    Write-Check -Name 'Desktop retry-limit execution fails safely after repeated failure' -Passed $desktopRetryExecuteOk -Detail (($desktopRetryExecute.Output | Out-String).Trim())
    if (-not $desktopRetryExecuteOk) { $failed++ }

    $desktopRetryStatus = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('task-status', '--task-id', $desktopRetryTaskId)
    $desktopRetryStatusOk = $desktopRetryStatus.ExitCode -eq 0 -and `
        (($desktopRetryStatus.Output | Out-String) -match 'status:\s+failed') -and `
        (($desktopRetryStatus.Output | Out-String) -match 'last_attempt_count:\s+2') -and `
        (($desktopRetryStatus.Output | Out-String) -match 'retry_limit:\s+2') -and `
        (($desktopRetryStatus.Output | Out-String) -match 'last_failure_reason:\s+Failed after 2 attempt\(s\)\.')
    Write-Check -Name 'Retry limit persists after two failed attempts' -Passed $desktopRetryStatusOk -Detail (($desktopRetryStatus.Output | Out-String).Trim())
    if (-not $desktopRetryStatusOk) { $failed++ }
}

$recipeObserveQueue = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @(
    'queue-executor-action',
    '--action-type', 'run_operator_recipe',
    '--target', 'observe_desktop_state'
)
$recipeObserveQueueOk = $recipeObserveQueue.ExitCode -eq 0 -and `
    (($recipeObserveQueue.Output | Out-String) -match 'status:\s+queued') -and `
    (($recipeObserveQueue.Output | Out-String) -match 'approval_state:\s+not_required') -and `
    (($recipeObserveQueue.Output | Out-String) -match 'executor_action_type:\s+run_operator_recipe') -and `
    (($recipeObserveQueue.Output | Out-String) -match 'recipe_name:\s+observe_desktop_state')
Write-Check -Name 'Operator recipe observe_desktop_state queues without approval' -Passed $recipeObserveQueueOk -Detail (($recipeObserveQueue.Output | Out-String).Trim())
if (-not $recipeObserveQueueOk) { $failed++ }

$recipeObserveTaskMatch = [regex]::Match(($recipeObserveQueue.Output | Out-String), 'task_id:\s*(\S+)')
$recipeObserveTaskId = if ($recipeObserveTaskMatch.Success) { $recipeObserveTaskMatch.Groups[1].Value } else { $null }
$recipeObserveTaskOk = -not [string]::IsNullOrWhiteSpace($recipeObserveTaskId)
Write-Check -Name 'Operator recipe observe_desktop_state task id parsed' -Passed $recipeObserveTaskOk -Detail ($(if ($recipeObserveTaskOk) { $recipeObserveTaskId } else { 'missing observe_desktop_state task id' }))
if (-not $recipeObserveTaskOk) { $failed++ }

if ($recipeObserveTaskOk) {
    $recipeObserveExecute = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('execute-task', '--task-id', $recipeObserveTaskId)
    $recipeObserveExecuteOk = $recipeObserveExecute.ExitCode -eq 0 -and `
        (($recipeObserveExecute.Output | Out-String) -match 'status:\s+completed') -and `
        (($recipeObserveExecute.Output | Out-String) -match 'execution_status:\s+succeeded')
    Write-Check -Name 'Operator recipe observe_desktop_state execution succeeds' -Passed $recipeObserveExecuteOk -Detail (($recipeObserveExecute.Output | Out-String).Trim())
    if (-not $recipeObserveExecuteOk) { $failed++ }

    $recipeObserveStatus = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('task-status', '--task-id', $recipeObserveTaskId)
    $recipeObserveStatusOk = $recipeObserveStatus.ExitCode -eq 0 -and `
        (($recipeObserveStatus.Output | Out-String) -match 'recipe_name:\s+observe_desktop_state') -and `
        (($recipeObserveStatus.Output | Out-String) -match 'recipe_status:\s+succeeded') -and `
        (($recipeObserveStatus.Output | Out-String) -match 'recipe_run_count:\s+[1-9]') -and `
        (($recipeObserveStatus.Output | Out-String) -match 'recipe_last_run_steps:\s*') -and `
        (($recipeObserveStatus.Output | Out-String) -match 'action=list_windows')
    Write-Check -Name 'Operator recipe observe_desktop_state result persists' -Passed $recipeObserveStatusOk -Detail (($recipeObserveStatus.Output | Out-String).Trim())
    if (-not $recipeObserveStatusOk) { $failed++ }
}

$recipeFocusTerminalQueue = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @(
    'queue-executor-action',
    '--action-type', 'run_operator_recipe',
    '--target', 'focus_or_reuse_terminal'
)
$recipeFocusTerminalQueueOk = $recipeFocusTerminalQueue.ExitCode -eq 0 -and `
    (($recipeFocusTerminalQueue.Output | Out-String) -match 'status:\s+pending_approval') -and `
    (($recipeFocusTerminalQueue.Output | Out-String) -match 'approval_state:\s+pending') -and `
    (($recipeFocusTerminalQueue.Output | Out-String) -match 'recipe_name:\s+focus_or_reuse_terminal')
Write-Check -Name 'Operator recipe focus_or_reuse_terminal stays approval-aware' -Passed $recipeFocusTerminalQueueOk -Detail (($recipeFocusTerminalQueue.Output | Out-String).Trim())
if (-not $recipeFocusTerminalQueueOk) { $failed++ }

$handoffFixtureWindowsJson = @(
    @{ Title = 'Codex - Task'; ProcessId = 1201; Active = $true },
    @{ Title = 'ChatGPT - Browser'; ProcessId = 2202; Active = $false },
    @{ Title = 'ChatGPT Notes'; ProcessId = 2203; Active = $false }
) | ConvertTo-Json -Compress
$handoffWrongActiveWindowsJson = @(
    @{ Title = 'Windows PowerShell'; ProcessId = 3301; Active = $true },
    @{ Title = 'ChatGPT - Browser'; ProcessId = 2202; Active = $false },
    @{ Title = 'Codex - Task'; ProcessId = 1201; Active = $false }
) | ConvertTo-Json -Compress

$handoffSeedQueue = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @(
    'queue-executor-action',
    '--action-type', 'set_clipboard_text',
    '--content', 'ghoti safe handoff payload'
)
$handoffSeedQueueOk = $handoffSeedQueue.ExitCode -eq 0 -and `
    (($handoffSeedQueue.Output | Out-String) -match 'status:\s+pending_approval')
Write-Check -Name 'Handoff safe clipboard seed queues with approval' -Passed $handoffSeedQueueOk -Detail (($handoffSeedQueue.Output | Out-String).Trim())
if (-not $handoffSeedQueueOk) { $failed++ }

$handoffSeedTaskMatch = [regex]::Match(($handoffSeedQueue.Output | Out-String), 'task_id:\s*(\S+)')
$handoffSeedTaskId = if ($handoffSeedTaskMatch.Success) { $handoffSeedTaskMatch.Groups[1].Value } else { $null }
$handoffSeedApprovalMatch = [regex]::Match(($handoffSeedQueue.Output | Out-String), 'approval_request_id:\s*(\S+)')
$handoffSeedApprovalId = if ($handoffSeedApprovalMatch.Success) { $handoffSeedApprovalMatch.Groups[1].Value } else { $null }
$handoffSeedIdsOk = (-not [string]::IsNullOrWhiteSpace($handoffSeedTaskId)) -and (-not [string]::IsNullOrWhiteSpace($handoffSeedApprovalId))
Write-Check -Name 'Handoff safe clipboard seed ids parsed' -Passed $handoffSeedIdsOk -Detail ($(if ($handoffSeedIdsOk) { "$handoffSeedTaskId | $handoffSeedApprovalId" } else { 'missing safe clipboard seed ids' }))
if (-not $handoffSeedIdsOk) { $failed++ }

if (-not [string]::IsNullOrWhiteSpace($handoffSeedApprovalId)) {
    $handoffSeedApprove = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('approve-approval', '--approval-id', $handoffSeedApprovalId, '--note', 'runtime checker approved safe handoff clipboard seed')
    $handoffSeedApproveOk = $handoffSeedApprove.ExitCode -eq 0 -and `
        (($handoffSeedApprove.Output | Out-String) -match 'task_status:\s+queued')
    Write-Check -Name 'Handoff safe clipboard seed approval persists' -Passed $handoffSeedApproveOk -Detail (($handoffSeedApprove.Output | Out-String).Trim())
    if (-not $handoffSeedApproveOk) { $failed++ }
}

if (-not [string]::IsNullOrWhiteSpace($handoffSeedTaskId)) {
    $handoffSeedExecute = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('execute-task', '--task-id', $handoffSeedTaskId)
    $handoffSeedExecuteOk = $handoffSeedExecute.ExitCode -eq 0 -and `
        (($handoffSeedExecute.Output | Out-String) -match 'status:\s+completed')
    Write-Check -Name 'Handoff safe clipboard seed execution succeeds' -Passed $handoffSeedExecuteOk -Detail (($handoffSeedExecute.Output | Out-String).Trim())
    if (-not $handoffSeedExecuteOk) { $failed++ }
}

$handoffInvalidQueue = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @(
    'queue-executor-action',
    '--action-type', 'run_operator_recipe',
    '--target', 'codex_to_chatgpt_handoff_mvp',
    '--content', '{"sourceWindow":"terminal","targetWindow":"terminal","usePreparedClipboard":true,"waitSeconds":1}'
)
$handoffInvalidQueueOk = $handoffInvalidQueue.ExitCode -ne 0 -and `
    (($handoffInvalidQueue.Output | Out-String) -match 'must not use terminal or shell targets')
Write-Check -Name 'Codex to ChatGPT handoff rejects terminal fallback targets' -Passed $handoffInvalidQueueOk -Detail (($handoffInvalidQueue.Output | Out-String).Trim())
if (-not $handoffInvalidQueueOk) { $failed++ }

$handoffRecipeQueue = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @(
    'queue-executor-action',
    '--action-type', 'run_operator_recipe',
    '--target', 'codex_to_chatgpt_handoff_mvp',
    '--content', '{"sourceWindow":"codex","targetWindow":"chatgpt","usePreparedClipboard":true,"waitSeconds":1}'
)
$handoffRecipeQueueOk = $handoffRecipeQueue.ExitCode -eq 0 -and `
    (($handoffRecipeQueue.Output | Out-String) -match 'status:\s+pending_approval') -and `
    (($handoffRecipeQueue.Output | Out-String) -match 'recipe_name:\s+codex_to_chatgpt_handoff_mvp') -and `
    (($handoffRecipeQueue.Output | Out-String) -match 'recipe_source_window:\s+codex') -and `
    (($handoffRecipeQueue.Output | Out-String) -match 'recipe_target_window:\s+chatgpt') -and `
    (($handoffRecipeQueue.Output | Out-String) -match 'handoff_send_behavior:\s+paste_only') -and `
    (($handoffRecipeQueue.Output | Out-String) -match 'handoff_fallback_denied:\s+terminal_shell_fallback_blocked')
Write-Check -Name 'Codex to ChatGPT handoff queues with strict safe targets' -Passed $handoffRecipeQueueOk -Detail (($handoffRecipeQueue.Output | Out-String).Trim())
if (-not $handoffRecipeQueueOk) { $failed++ }

$handoffRecipeTaskMatch = [regex]::Match(($handoffRecipeQueue.Output | Out-String), 'task_id:\s*(\S+)')
$handoffRecipeTaskId = if ($handoffRecipeTaskMatch.Success) { $handoffRecipeTaskMatch.Groups[1].Value } else { $null }
$handoffRecipeApprovalMatch = [regex]::Match(($handoffRecipeQueue.Output | Out-String), 'approval_request_id:\s*(\S+)')
$handoffRecipeApprovalId = if ($handoffRecipeApprovalMatch.Success) { $handoffRecipeApprovalMatch.Groups[1].Value } else { $null }
$handoffRecipeIdsOk = (-not [string]::IsNullOrWhiteSpace($handoffRecipeTaskId)) -and (-not [string]::IsNullOrWhiteSpace($handoffRecipeApprovalId))
Write-Check -Name 'Codex to ChatGPT handoff ids parsed' -Passed $handoffRecipeIdsOk -Detail ($(if ($handoffRecipeIdsOk) { "$handoffRecipeTaskId | $handoffRecipeApprovalId" } else { 'missing handoff recipe ids' }))
if (-not $handoffRecipeIdsOk) { $failed++ }

if ($handoffRecipeIdsOk) {
    $handoffRecipeStatusBefore = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('task-status', '--task-id', $handoffRecipeTaskId)
    $handoffRecipeStatusBeforeOk = $handoffRecipeStatusBefore.ExitCode -eq 0 -and `
        (($handoffRecipeStatusBefore.Output | Out-String) -match 'recipe_clipboard_mode:\s+prepared_clipboard') -and `
        (($handoffRecipeStatusBefore.Output | Out-String) -match 'handoff_send_behavior:\s+paste_only') -and `
        (($handoffRecipeStatusBefore.Output | Out-String) -match 'handoff_fallback_denied:\s+terminal_shell_fallback_blocked') -and `
        (($handoffRecipeStatusBefore.Output | Out-String) -notmatch 'action=send_hotkey') -and `
        (($handoffRecipeStatusBefore.Output | Out-String) -notmatch 'target=terminal')
    Write-Check -Name 'Codex to ChatGPT handoff defaults to paste-only with no terminal step' -Passed $handoffRecipeStatusBeforeOk -Detail (($handoffRecipeStatusBefore.Output | Out-String).Trim())
    if (-not $handoffRecipeStatusBeforeOk) { $failed++ }
}

$handoffCandidateQueue = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @(
    'queue-executor-action',
    '--action-type', 'run_operator_recipe',
    '--target', 'codex_to_chatgpt_handoff_mvp',
    '--content', '{"sourceWindow":"codex","targetWindow":"chatgpt","sourceWindowCandidateId":"pid:1201","targetWindowCandidateId":"pid:2202","usePreparedClipboard":true,"waitSeconds":0}'
)
$handoffCandidateQueueOk = $handoffCandidateQueue.ExitCode -eq 0 -and `
    (($handoffCandidateQueue.Output | Out-String) -match 'status:\s+pending_approval') -and `
    (($handoffCandidateQueue.Output | Out-String) -match 'recipe_name:\s+codex_to_chatgpt_handoff_mvp')
Write-Check -Name 'Codex to ChatGPT handoff manual-candidate queue persists' -Passed $handoffCandidateQueueOk -Detail (($handoffCandidateQueue.Output | Out-String).Trim())
if (-not $handoffCandidateQueueOk) { $failed++ }

$handoffCandidateTaskMatch = [regex]::Match(($handoffCandidateQueue.Output | Out-String), 'task_id:\s*(\S+)')
$handoffCandidateTaskId = if ($handoffCandidateTaskMatch.Success) { $handoffCandidateTaskMatch.Groups[1].Value } else { $null }
$handoffCandidateApprovalMatch = [regex]::Match(($handoffCandidateQueue.Output | Out-String), 'approval_request_id:\s*(\S+)')
$handoffCandidateApprovalId = if ($handoffCandidateApprovalMatch.Success) { $handoffCandidateApprovalMatch.Groups[1].Value } else { $null }
if (-not [string]::IsNullOrWhiteSpace($handoffCandidateTaskId)) {
    $handoffCandidateStatus = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('task-status', '--task-id', $handoffCandidateTaskId)
    $handoffCandidateStatusOk = $handoffCandidateStatus.ExitCode -eq 0 -and `
        (($handoffCandidateStatus.Output | Out-String) -match 'recipe_source_window_candidate_id:\s+pid:1201') -and `
        (($handoffCandidateStatus.Output | Out-String) -match 'recipe_target_window_candidate_id:\s+pid:2202') -and `
        (($handoffCandidateStatus.Output | Out-String) -match 'handoff_source_selection_mode:\s+manual_candidate_selected') -and `
        (($handoffCandidateStatus.Output | Out-String) -match 'handoff_target_selection_mode:\s+manual_candidate_selected')
    Write-Check -Name 'Codex to ChatGPT handoff manual candidate selection is visible before execution' -Passed $handoffCandidateStatusOk -Detail (($handoffCandidateStatus.Output | Out-String).Trim())
    if (-not $handoffCandidateStatusOk) { $failed++ }
}

if (-not [string]::IsNullOrWhiteSpace($handoffCandidateApprovalId)) {
    $handoffCandidateApprove = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('approve-approval', '--approval-id', $handoffCandidateApprovalId, '--note', 'runtime checker approved manual-candidate handoff target test')
    $handoffCandidateApproveOk = $handoffCandidateApprove.ExitCode -eq 0 -and `
        (($handoffCandidateApprove.Output | Out-String) -match 'task_status:\s+queued')
    Write-Check -Name 'Codex to ChatGPT handoff manual-candidate approval persists' -Passed $handoffCandidateApproveOk -Detail (($handoffCandidateApprove.Output | Out-String).Trim())
    if (-not $handoffCandidateApproveOk) { $failed++ }
}

if (-not [string]::IsNullOrWhiteSpace($handoffCandidateTaskId)) {
    $handoffCandidateExecute = Invoke-ModuleCommand `
        -PythonPath $pythonPath `
        -Arguments @('execute-task', '--task-id', $handoffCandidateTaskId) `
        -EnvOverrides @{ SUPER_AGENT_DESKTOP_TEST_WINDOW_FIXTURES = $handoffWrongActiveWindowsJson }
    $handoffCandidateExecuteText = ($handoffCandidateExecute.Output | Out-String)
    $handoffCandidateExecuteOk = $handoffCandidateExecute.ExitCode -eq 0 -and `
        ($handoffCandidateExecuteText -match 'status:\s+blocked_human_needed') -and `
        ($handoffCandidateExecuteText -match 'execution_status:\s+failed') -and `
        ($handoffCandidateExecuteText -match 'unexpected_active_window|blocked before input') -and `
        ($handoffCandidateExecuteText -notmatch 'target=terminal')
    Write-Check -Name 'Codex to ChatGPT handoff blocks before paste when terminal stays foreground' -Passed $handoffCandidateExecuteOk -Detail $handoffCandidateExecuteText.Trim()
    if (-not $handoffCandidateExecuteOk) { $failed++ }

    $handoffCandidateStatusAfter = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('task-status', '--task-id', $handoffCandidateTaskId)
    $handoffCandidateStatusAfterText = ($handoffCandidateStatusAfter.Output | Out-String)
    $handoffCandidateStatusAfterOk = $handoffCandidateStatusAfter.ExitCode -eq 0 -and `
        ($handoffCandidateStatusAfterText -match 'recipe_status:\s+blocked') -and `
        ($handoffCandidateStatusAfterText -match 'handoff_target_resolution_status:\s+blocked_wrong_active_window') -and `
        ($handoffCandidateStatusAfterText -match 'handoff_manual_target_resolution:\s+required') -and `
        ($handoffCandidateStatusAfterText -match 'handoff_paste_allowed:\s+no') -and `
        ($handoffCandidateStatusAfterText -match 'handoff_send_allowed:\s+no') -and `
        ($handoffCandidateStatusAfterText -match 'handoff_fallback_denied:\s+yes') -and `
        ($handoffCandidateStatusAfterText -match 'handoff_target_match:\s+expected chatgpt \| active terminal') -and `
        ($handoffCandidateStatusAfterText -notmatch 'target=terminal')
    Write-Check -Name 'Codex to ChatGPT handoff keeps wrong-window metadata after terminal block' -Passed $handoffCandidateStatusAfterOk -Detail $handoffCandidateStatusAfterText.Trim()
    if (-not $handoffCandidateStatusAfterOk) { $failed++ }
}

if (-not [string]::IsNullOrWhiteSpace($handoffRecipeApprovalId)) {
    $handoffRecipeApprove = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('approve-approval', '--approval-id', $handoffRecipeApprovalId, '--note', 'runtime checker approved safe handoff recipe')
    $handoffRecipeApproveOk = $handoffRecipeApprove.ExitCode -eq 0 -and `
        (($handoffRecipeApprove.Output | Out-String) -match 'task_status:\s+queued')
    Write-Check -Name 'Codex to ChatGPT handoff approval persists' -Passed $handoffRecipeApproveOk -Detail (($handoffRecipeApprove.Output | Out-String).Trim())
    if (-not $handoffRecipeApproveOk) { $failed++ }
}

if (-not [string]::IsNullOrWhiteSpace($handoffRecipeTaskId)) {
    $handoffRecipeExecute = Invoke-ModuleCommand `
        -PythonPath $pythonPath `
        -Arguments @('execute-task', '--task-id', $handoffRecipeTaskId) `
        -EnvOverrides @{ SUPER_AGENT_DESKTOP_TEST_WINDOW_FIXTURES = $handoffFixtureWindowsJson }
    $handoffRecipeExecuteText = ($handoffRecipeExecute.Output | Out-String)
    $handoffRecipeExecuteOk = $handoffRecipeExecute.ExitCode -eq 0 -and `
        ($handoffRecipeExecuteText -match 'status:\s+blocked_human_needed') -and `
        ($handoffRecipeExecuteText -match 'execution_status:\s+failed') -and `
        ($handoffRecipeExecuteText -match 'manual target resolution is required|manual_target_resolution_required')
    Write-Check -Name 'Codex to ChatGPT handoff blocks safely when real target matching is ambiguous' -Passed $handoffRecipeExecuteOk -Detail $handoffRecipeExecuteText.Trim()
    if (-not $handoffRecipeExecuteOk) { $failed++ }

    $handoffRecipeStatus = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('task-status', '--task-id', $handoffRecipeTaskId)
    $handoffRecipeStatusText = ($handoffRecipeStatus.Output | Out-String)
    $handoffRecipeStatusOk = $handoffRecipeStatus.ExitCode -eq 0 -and `
        ($handoffRecipeStatusText -match 'recipe_status:\s+blocked') -and `
        ($handoffRecipeStatusText -match 'handoff_payload_classification:\s+valid_handoff_text') -and `
        ($handoffRecipeStatusText -match 'handoff_paste_allowed:\s+no') -and `
        ($handoffRecipeStatusText -match 'handoff_target_resolution_status:\s+manual_target_resolution_required') -and `
        ($handoffRecipeStatusText -match 'handoff_manual_target_resolution:\s+required') -and `
        ($handoffRecipeStatusText -match 'handoff_target_selection_mode:\s+manual_selection_required') -and `
        ($handoffRecipeStatusText -match 'handoff_fallback_denied:\s+yes') -and `
        ($handoffRecipeStatusText -notmatch 'target=terminal')
    Write-Check -Name 'Codex to ChatGPT handoff keeps manual-resolution metadata and denies terminal fallback' -Passed $handoffRecipeStatusOk -Detail $handoffRecipeStatusText.Trim()
    if (-not $handoffRecipeStatusOk) { $failed++ }
}

$explicitSendQueue = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @(
    'queue-executor-action',
    '--action-type', 'run_operator_recipe',
    '--target', 'codex_to_chatgpt_handoff_mvp',
    '--content', '{"sourceWindow":"codex","targetWindow":"chatgpt","usePreparedClipboard":true,"allowSend":true,"waitSeconds":0}'
)
$explicitSendQueueOk = $explicitSendQueue.ExitCode -eq 0 -and `
    (($explicitSendQueue.Output | Out-String) -match 'status:\s+pending_approval') -and `
    (($explicitSendQueue.Output | Out-String) -match 'handoff_send_behavior:\s+explicit_enter_after_paste') -and `
    (($explicitSendQueue.Output | Out-String) -match 'recipe_target_window:\s+chatgpt') -and `
    (($explicitSendQueue.Output | Out-String) -notmatch 'recipe_target_window:\s+terminal')
Write-Check -Name 'Codex to ChatGPT handoff can expose Enter only when explicitly allowed' -Passed $explicitSendQueueOk -Detail (($explicitSendQueue.Output | Out-String).Trim())
if (-not $explicitSendQueueOk) { $failed++ }

$explicitSendTaskMatch = [regex]::Match(($explicitSendQueue.Output | Out-String), 'task_id:\s*(\S+)')
$explicitSendTaskId = if ($explicitSendTaskMatch.Success) { $explicitSendTaskMatch.Groups[1].Value } else { $null }
if (-not [string]::IsNullOrWhiteSpace($explicitSendTaskId)) {
    $explicitSendStatus = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('task-status', '--task-id', $explicitSendTaskId)
    $explicitSendStatusOk = $explicitSendStatus.ExitCode -eq 0 -and `
        (($explicitSendStatus.Output | Out-String) -match 'handoff_send_behavior:\s+explicit_enter_after_paste') -and `
        (($explicitSendStatus.Output | Out-String) -match 'action=send_hotkey') -and `
        (($explicitSendStatus.Output | Out-String) -match 'target=chatgpt\|enter')
    Write-Check -Name 'Explicit send handoff adds Enter step only when requested for ChatGPT' -Passed $explicitSendStatusOk -Detail (($explicitSendStatus.Output | Out-String).Trim())
    if (-not $explicitSendStatusOk) { $failed++ }
}

$handoffBadSeedQueue = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @(
    'queue-executor-action',
    '--action-type', 'set_clipboard_text',
    '--content', 'Run Desktop Bridge Check'
)
$handoffBadSeedQueueOk = $handoffBadSeedQueue.ExitCode -eq 0 -and `
    (($handoffBadSeedQueue.Output | Out-String) -match 'status:\s+pending_approval')
Write-Check -Name 'Handoff suspicious clipboard seed queues with approval' -Passed $handoffBadSeedQueueOk -Detail (($handoffBadSeedQueue.Output | Out-String).Trim())
if (-not $handoffBadSeedQueueOk) { $failed++ }

$handoffBadSeedTaskMatch = [regex]::Match(($handoffBadSeedQueue.Output | Out-String), 'task_id:\s*(\S+)')
$handoffBadSeedTaskId = if ($handoffBadSeedTaskMatch.Success) { $handoffBadSeedTaskMatch.Groups[1].Value } else { $null }
$handoffBadSeedApprovalMatch = [regex]::Match(($handoffBadSeedQueue.Output | Out-String), 'approval_request_id:\s*(\S+)')
$handoffBadSeedApprovalId = if ($handoffBadSeedApprovalMatch.Success) { $handoffBadSeedApprovalMatch.Groups[1].Value } else { $null }
if (-not [string]::IsNullOrWhiteSpace($handoffBadSeedApprovalId)) {
    $handoffBadSeedApprove = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('approve-approval', '--approval-id', $handoffBadSeedApprovalId, '--note', 'runtime checker seeded suspicious handoff clipboard text')
    $handoffBadSeedApproveOk = $handoffBadSeedApprove.ExitCode -eq 0
    Write-Check -Name 'Handoff suspicious clipboard seed approval persists' -Passed $handoffBadSeedApproveOk -Detail (($handoffBadSeedApprove.Output | Out-String).Trim())
    if (-not $handoffBadSeedApproveOk) { $failed++ }
}

if (-not [string]::IsNullOrWhiteSpace($handoffBadSeedTaskId)) {
    $handoffBadSeedExecute = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('execute-task', '--task-id', $handoffBadSeedTaskId)
    $handoffBadSeedExecuteOk = $handoffBadSeedExecute.ExitCode -eq 0 -and `
        (($handoffBadSeedExecute.Output | Out-String) -match 'status:\s+completed')
    Write-Check -Name 'Handoff suspicious clipboard seed execution succeeds' -Passed $handoffBadSeedExecuteOk -Detail (($handoffBadSeedExecute.Output | Out-String).Trim())
    if (-not $handoffBadSeedExecuteOk) { $failed++ }
}

$handoffBlockedQueue = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @(
    'queue-executor-action',
    '--action-type', 'run_operator_recipe',
    '--target', 'codex_to_chatgpt_handoff_mvp',
    '--content', '{"sourceWindow":"codex","targetWindow":"chatgpt","usePreparedClipboard":true,"waitSeconds":0}'
)
$handoffBlockedQueueOk = $handoffBlockedQueue.ExitCode -eq 0 -and `
    (($handoffBlockedQueue.Output | Out-String) -match 'status:\s+pending_approval') -and `
    (($handoffBlockedQueue.Output | Out-String) -match 'recipe_source_window:\s+codex') -and `
    (($handoffBlockedQueue.Output | Out-String) -match 'recipe_target_window:\s+chatgpt')
Write-Check -Name 'Codex to ChatGPT handoff blocked-payload recipe queues' -Passed $handoffBlockedQueueOk -Detail (($handoffBlockedQueue.Output | Out-String).Trim())
if (-not $handoffBlockedQueueOk) { $failed++ }

$handoffBlockedTaskMatch = [regex]::Match(($handoffBlockedQueue.Output | Out-String), 'task_id:\s*(\S+)')
$handoffBlockedTaskId = if ($handoffBlockedTaskMatch.Success) { $handoffBlockedTaskMatch.Groups[1].Value } else { $null }
$handoffBlockedApprovalMatch = [regex]::Match(($handoffBlockedQueue.Output | Out-String), 'approval_request_id:\s*(\S+)')
$handoffBlockedApprovalId = if ($handoffBlockedApprovalMatch.Success) { $handoffBlockedApprovalMatch.Groups[1].Value } else { $null }
if (-not [string]::IsNullOrWhiteSpace($handoffBlockedApprovalId)) {
    $handoffBlockedApprove = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('approve-approval', '--approval-id', $handoffBlockedApprovalId, '--note', 'runtime checker approved blocked handoff payload test')
    $handoffBlockedApproveOk = $handoffBlockedApprove.ExitCode -eq 0
    Write-Check -Name 'Codex to ChatGPT handoff blocked-payload approval persists' -Passed $handoffBlockedApproveOk -Detail (($handoffBlockedApprove.Output | Out-String).Trim())
    if (-not $handoffBlockedApproveOk) { $failed++ }
}

if (-not [string]::IsNullOrWhiteSpace($handoffBlockedTaskId)) {
    $handoffBlockedExecute = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('execute-task', '--task-id', $handoffBlockedTaskId)
    $handoffBlockedExecuteOk = $handoffBlockedExecute.ExitCode -eq 0 -and `
        (($handoffBlockedExecute.Output | Out-String) -match 'status:\s+blocked_human_needed') -and `
        (($handoffBlockedExecute.Output | Out-String) -match 'execution_status:\s+failed') -and `
        (($handoffBlockedExecute.Output | Out-String) -match '(Handoff payload blocked before paste|checker or recipe label|payload was blocked)') -and `
        (($handoffBlockedExecute.Output | Out-String) -notmatch 'target=terminal')
    Write-Check -Name 'Codex to ChatGPT handoff blocks junk payload before paste' -Passed $handoffBlockedExecuteOk -Detail (($handoffBlockedExecute.Output | Out-String).Trim())
    if (-not $handoffBlockedExecuteOk) { $failed++ }

    $handoffBlockedStatus = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('task-status', '--task-id', $handoffBlockedTaskId)
    $handoffBlockedStatusOk = $handoffBlockedStatus.ExitCode -eq 0 -and `
        (($handoffBlockedStatus.Output | Out-String) -match 'recipe_status:\s+blocked') -and `
        (($handoffBlockedStatus.Output | Out-String) -match 'handoff_payload_classification:\s+(junk_label_payload|repeated_ui_label_garbage)') -and `
        (($handoffBlockedStatus.Output | Out-String) -match 'handoff_paste_allowed:\s+no') -and `
        (($handoffBlockedStatus.Output | Out-String) -match 'handoff_blocked_payload_repeats:\s+1')
    Write-Check -Name 'Codex to ChatGPT blocked payload classification persists' -Passed $handoffBlockedStatusOk -Detail (($handoffBlockedStatus.Output | Out-String).Trim())
    if (-not $handoffBlockedStatusOk) { $failed++ }

    $handoffBlockedNoRetryLoopOk = $handoffBlockedStatus.ExitCode -eq 0 -and `
        (($handoffBlockedStatus.Output | Out-String) -match 'action=get_clipboard_text') -and `
        (($handoffBlockedStatus.Output | Out-String) -match 'attempts=1 \| max_attempts=2')
    Write-Check -Name 'Blocked junk handoff payload stops immediately instead of retrying the same paste path' -Passed $handoffBlockedNoRetryLoopOk -Detail (($handoffBlockedStatus.Output | Out-String).Trim())
    if (-not $handoffBlockedNoRetryLoopOk) { $failed++ }

    $handoffBlockedReview = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('review-task', '--task-id', $handoffBlockedTaskId, '--note', 'runtime checker reviewed repeated blocked payload')
    $handoffBlockedReviewOk = $handoffBlockedReview.ExitCode -eq 0 -and `
        (($handoffBlockedReview.Output | Out-String) -match 'status:\s+ready_to_resume')
    Write-Check -Name 'Blocked handoff task can be reviewed for manual re-queue' -Passed $handoffBlockedReviewOk -Detail (($handoffBlockedReview.Output | Out-String).Trim())
    if (-not $handoffBlockedReviewOk) { $failed++ }

    $handoffBlockedRequeue = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('requeue-task', '--task-id', $handoffBlockedTaskId, '--note', 'runtime checker re-queued repeated blocked payload')
    $handoffBlockedRequeueOk = $handoffBlockedRequeue.ExitCode -eq 0 -and `
        (($handoffBlockedRequeue.Output | Out-String) -match 'status:\s+queued')
    Write-Check -Name 'Blocked handoff task re-queues only after explicit operator action' -Passed $handoffBlockedRequeueOk -Detail (($handoffBlockedRequeue.Output | Out-String).Trim())
    if (-not $handoffBlockedRequeueOk) { $failed++ }

    $handoffBlockedExecuteAgain = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('execute-task', '--task-id', $handoffBlockedTaskId)
    $handoffBlockedExecuteAgainOk = $handoffBlockedExecuteAgain.ExitCode -eq 0 -and `
        (($handoffBlockedExecuteAgain.Output | Out-String) -match 'status:\s+blocked_human_needed') -and `
        (($handoffBlockedExecuteAgain.Output | Out-String) -match 'execution_status:\s+failed')
    Write-Check -Name 'Repeated identical junk handoff payload blocks again without looping' -Passed $handoffBlockedExecuteAgainOk -Detail (($handoffBlockedExecuteAgain.Output | Out-String).Trim())
    if (-not $handoffBlockedExecuteAgainOk) { $failed++ }

    $handoffBlockedStatusAgain = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('task-status', '--task-id', $handoffBlockedTaskId)
    $handoffBlockedStatusAgainOk = $handoffBlockedStatusAgain.ExitCode -eq 0 -and `
        (($handoffBlockedStatusAgain.Output | Out-String) -match 'handoff_blocked_payload_repeats:\s+2') -and `
        (($handoffBlockedStatusAgain.Output | Out-String) -match 'Repeated identical blocked handoff payload detected again')
    Write-Check -Name 'Repeated identical junk handoff payload is counted and reported clearly' -Passed $handoffBlockedStatusAgainOk -Detail (($handoffBlockedStatusAgain.Output | Out-String).Trim())
    if (-not $handoffBlockedStatusAgainOk) { $failed++ }
}

$recipeInterruptQueue = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @(
    'queue-executor-action',
    '--action-type', 'run_operator_recipe',
    '--target', 'wait_and_resume_operator_step',
    '--content', '{"waitSeconds":5}'
)
$recipeInterruptQueueOk = $recipeInterruptQueue.ExitCode -eq 0 -and `
    (($recipeInterruptQueue.Output | Out-String) -match 'status:\s+queued') -and `
    (($recipeInterruptQueue.Output | Out-String) -match 'approval_state:\s+not_required') -and `
    (($recipeInterruptQueue.Output | Out-String) -match 'recipe_name:\s+wait_and_resume_operator_step')
Write-Check -Name 'Operator recipe wait_and_resume_operator_step queues without approval' -Passed $recipeInterruptQueueOk -Detail (($recipeInterruptQueue.Output | Out-String).Trim())
if (-not $recipeInterruptQueueOk) { $failed++ }

$recipeInterruptTaskMatch = [regex]::Match(($recipeInterruptQueue.Output | Out-String), 'task_id:\s*(\S+)')
$recipeInterruptTaskId = if ($recipeInterruptTaskMatch.Success) { $recipeInterruptTaskMatch.Groups[1].Value } else { $null }
$recipeInterruptTaskOk = -not [string]::IsNullOrWhiteSpace($recipeInterruptTaskId)
Write-Check -Name 'Operator recipe wait_and_resume_operator_step task id parsed' -Passed $recipeInterruptTaskOk -Detail ($(if ($recipeInterruptTaskOk) { $recipeInterruptTaskId } else { 'missing wait_and_resume_operator_step task id' }))
if (-not $recipeInterruptTaskOk) { $failed++ }

if ($recipeInterruptTaskOk) {
    $recipeInterruptExecute = Invoke-ModuleCommand `
        -PythonPath $pythonPath `
        -Arguments @('execute-task', '--task-id', $recipeInterruptTaskId) `
        -EnvOverrides @{ SUPER_AGENT_DESKTOP_TEST_INTERRUPT_AFTER_MS = '300' }
    $recipeInterruptExecuteOk = $recipeInterruptExecute.ExitCode -eq 0 -and `
        (($recipeInterruptExecute.Output | Out-String) -match 'status:\s+interrupted') -and `
        (($recipeInterruptExecute.Output | Out-String) -match 'execution_status:\s+interrupted') -and `
        (($recipeInterruptExecute.Output | Out-String) -match 'Ctrl\+8')
    Write-Check -Name 'Operator recipe interruption persists through Ctrl+8 failsafe' -Passed $recipeInterruptExecuteOk -Detail (($recipeInterruptExecute.Output | Out-String).Trim())
    if (-not $recipeInterruptExecuteOk) { $failed++ }

    $recipeInterruptStatus = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('task-status', '--task-id', $recipeInterruptTaskId)
    $recipeInterruptStatusOk = $recipeInterruptStatus.ExitCode -eq 0 -and `
        (($recipeInterruptStatus.Output | Out-String) -match 'status:\s+interrupted') -and `
        (($recipeInterruptStatus.Output | Out-String) -match 'recipe_status:\s+interrupted') -and `
        (($recipeInterruptStatus.Output | Out-String) -match 'waiting_for:\s+operator_review_after_interrupt')
    Write-Check -Name 'Interrupted operator recipe stays stopped for operator review' -Passed $recipeInterruptStatusOk -Detail (($recipeInterruptStatus.Output | Out-String).Trim())
    if (-not $recipeInterruptStatusOk) { $failed++ }
}

$invalidRecipeQueue = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @(
    'queue-executor-action',
    '--action-type', 'run_operator_recipe',
    '--target', 'not_a_recipe'
)
$invalidRecipeQueueOk = $invalidRecipeQueue.ExitCode -ne 0 -and `
    (($invalidRecipeQueue.Output | Out-String) -match 'Unsupported operator recipe')
Write-Check -Name 'Unsupported operator recipe fails safely' -Passed $invalidRecipeQueueOk -Detail (($invalidRecipeQueue.Output | Out-String).Trim())
if (-not $invalidRecipeQueueOk) { $failed++ }

$desktopInvalidTarget = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @(
    'queue-executor-action',
    '--action-type', 'focus_window',
    '--target', 'not_allowed'
)
$desktopInvalidTargetOk = $desktopInvalidTarget.ExitCode -ne 0 -and `
    (($desktopInvalidTarget.Output | Out-String) -match 'focus_window target must be one of')
Write-Check -Name 'Desktop executor unsupported target fails safely' -Passed $desktopInvalidTargetOk -Detail (($desktopInvalidTarget.Output | Out-String).Trim())
if (-not $desktopInvalidTargetOk) { $failed++ }

Remove-GeneratedFile -Path $runtimeDesktopArtifactPath

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

