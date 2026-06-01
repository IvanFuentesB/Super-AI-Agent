# Verify the N+6.15A local worker queue + status brain. Emits one JSON object.
# This check only tests for file presence and reads the example feature-flags
# config. It launches no browser, controls no desktop, clicks/types nothing,
# sends nothing, installs nothing, runs no third-party code, and calls no
# external API. Gemma summarization is optional and local-only.

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$scriptDir = $PSScriptRoot
$scriptsDir = Split-Path -Parent $scriptDir
$repoRoot = Split-Path -Parent $scriptsDir

$statusBrain = Join-Path $scriptDir 'ghoti_status_brain.py'
$queueScript = Join-Path $scriptDir 'ghoti_local_worker_queue.py'
$examplesDir = Join-Path $repoRoot '14_context\local_worker_queue\queue_examples'
$handoffDir = Join-Path $repoRoot '14_context\agent_handoff_vault\04_Logs'
$flagsPath = Join-Path $repoRoot '23_configs\ghoti_feature_flags.example.json'

function Test-Leaf {
    param([string]$Path)
    return [bool](Test-Path -LiteralPath $Path -PathType Leaf)
}

$statusBrainExists = Test-Leaf $statusBrain
$queueScriptExists = Test-Leaf $queueScript

$exampleNames = @(
    'status_summary_task.json',
    'computer_use_sandbox_status_task.json',
    'repo_intake_summary_task.json'
)
$queueExamplesExist = $true
foreach ($name in $exampleNames) {
    if (-not (Test-Leaf (Join-Path $examplesDir $name))) { $queueExamplesExist = $false }
}

$handoffDirExists = [bool](Test-Path -LiteralPath $handoffDir -PathType Container)

# Gemma is always optional and never required by this milestone.
$gemmaOptional = $true

# Verify the N+6.15A risky feature flags default to false in the example config.
$riskyFlags = @(
    'local_worker_queue_enabled',
    'local_status_brain_enabled',
    'local_gemma_summary_enabled',
    'auto_schedule_worker_enabled',
    'telegram_status_bridge_enabled',
    'hermes_memory_writer_enabled'
)
$riskyFlagsDefaultFalse = $true
if (Test-Leaf $flagsPath) {
    try {
        $flags = Get-Content -Raw -LiteralPath $flagsPath | ConvertFrom-Json
        foreach ($flag in $riskyFlags) {
            $value = $flags.PSObject.Properties[$flag]
            if (($null -eq $value) -or ([bool]$value.Value)) {
                $riskyFlagsDefaultFalse = $false
            }
        }
    } catch {
        $riskyFlagsDefaultFalse = $false
    }
} else {
    $riskyFlagsDefaultFalse = $false
}

$filesOk = $statusBrainExists -and $queueScriptExists -and $queueExamplesExist -and $handoffDirExists
$ok = $filesOk -and $riskyFlagsDefaultFalse

$result = [ordered]@{
    ok = $ok
    milestone = 'N+6.15A'
    check = 'local_worker_queue'
    status_brain_exists = $statusBrainExists
    queue_script_exists = $queueScriptExists
    queue_examples_exist = $queueExamplesExist
    handoff_dir_exists = $handoffDirExists
    gemma_optional = $gemmaOptional
    local_only = $true
    live_browser_used = $false
    os_input_used = $false
    external_api_used = $false
    telegram_control_used = $false
    mcp_used = $false
    auto_send_used = $false
    risky_flags_default_false = $riskyFlagsDefaultFalse
}

$result | ConvertTo-Json
if ($ok) { exit 0 } else { exit 1 }
