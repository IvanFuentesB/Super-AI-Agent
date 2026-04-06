# Foundation checker for the current repo baseline.

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

$failed = 0

try {
    $repoRoot = (git rev-parse --show-toplevel 2>$null).Trim()
    $insideRepo = $LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($repoRoot)
} catch {
    $insideRepo = $false
    $repoRoot = $null
}

Write-Check -Name 'Git repo' -Passed $insideRepo -Detail ($(if ($insideRepo) { $repoRoot } else { 'not inside a git repository' }))
if (-not $insideRepo) {
    Write-Host ''
    Write-Host 'Summary: foundation checks failed before file validation.'
    exit 1
}

$requiredFiles = @(
    'README.md',
    '.gitignore',
    '04_docs/git_workflow.md',
    '04_docs/approval_system.md',
    '04_docs/memory_architecture.md',
    '13_prompts/continue_handoff_prompt.md',
    '13_prompts/codex_master_batch_prompt.md',
    '14_context/current_state.md',
    '14_context/next_actions.md',
    '14_context/decisions.md',
    '14_context/open_questions.md',
    '14_context/recent_failures.md',
    '14_context/status_board.md',
    '23_configs/approval_policy.example.yaml',
    '23_configs/memory_policy.example.yaml'
)

foreach ($relativePath in $requiredFiles) {
    $fullPath = Join-Path $repoRoot $relativePath
    $exists = Test-Path -LiteralPath $fullPath -PathType Leaf
    Write-Check -Name 'File exists' -Passed $exists -Detail $relativePath
    if (-not $exists) {
        $failed++
    }
}

$branch = (git -C $repoRoot branch --show-current 2>$null).Trim()
$branchOk = $LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($branch)
Write-Check -Name 'Current branch' -Passed $branchOk -Detail ($(if ($branchOk) { $branch } else { 'unavailable' }))
if (-not $branchOk) {
    $failed++
}

$statusLines = @(git -C $repoRoot status --porcelain 2>$null)
$treeClean = $LASTEXITCODE -eq 0 -and $statusLines.Count -eq 0
$treeDetail = if ($treeClean) { 'clean' } else { 'dirty' }
Write-Check -Name 'Working tree' -Passed $treeClean -Detail $treeDetail
if (-not $treeClean) {
    $failed++
}

$commitLine = (git -C $repoRoot log -1 --pretty=format:'%H %s' 2>$null).Trim()
$commitOk = $LASTEXITCODE -eq 0 -and -not [string]::IsNullOrWhiteSpace($commitLine)
Write-Check -Name 'Latest commit' -Passed $commitOk -Detail ($(if ($commitOk) { $commitLine } else { 'unavailable' }))
if (-not $commitOk) {
    $failed++
}

Write-Host ''
if ($failed -eq 0) {
    Write-Host ('Summary: all required foundation checks passed ({0} files verified).' -f $requiredFiles.Count)
    exit 0
}

Write-Host ('Summary: {0} foundation check(s) failed.' -f $failed)
exit 1
