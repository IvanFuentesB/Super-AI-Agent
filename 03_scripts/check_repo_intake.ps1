# Verify the curated repo intake layer.

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

function Test-GitRepo {
    param([string]$Path)

    $null = & git -C $Path rev-parse --is-inside-work-tree 2>$null
    return $LASTEXITCODE -eq 0
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$manifestPath = Join-Path $repoRoot '23_configs\repo_manifest.example.json'
$thirdPartyRoot = Join-Path $repoRoot '21_repos\third_party'

$expectedFiles = @(
    '04_docs/provider_adapter_roadmap.md',
    '04_docs/remote_access_and_auth.md',
    '04_docs/public_repo_split_plan.md',
    '04_docs/repo_intake_strategy.md',
    '08_research/repo_intake_matrix.md',
    '23_configs/repo_manifest.example.json',
    '03_scripts/sync_third_party_repos.ps1',
    '03_scripts/check_repo_intake.ps1',
    '21_repos/third_party/.gitkeep',
    '14_context/status_board.md'
)

$failed = 0

foreach ($relativePath in $expectedFiles) {
    $fullPath = Join-Path $repoRoot $relativePath
    $exists = Test-Path -LiteralPath $fullPath -PathType Leaf
    Write-Check -Name 'File exists' -Passed $exists -Detail $relativePath
    if (-not $exists) {
        $failed++
    }
}

$thirdPartyExists = Test-Path -LiteralPath $thirdPartyRoot -PathType Container
Write-Check -Name 'Third-party root exists' -Passed $thirdPartyExists -Detail '21_repos/third_party'
if (-not $thirdPartyExists) {
    $failed++
}

$gitCommand = Get-Command git -ErrorAction SilentlyContinue
$gitOk = $null -ne $gitCommand
Write-Check -Name 'Git available' -Passed $gitOk -Detail ($(if ($gitOk) { $gitCommand.Source } else { 'git command not found' }))
if (-not $gitOk) {
    Write-Host ''
    Write-Host ("Summary: {0} repo intake check(s) failed." -f ($failed + 1))
    exit 1
}

if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
    Write-Host ''
    Write-Host ("Summary: {0} repo intake check(s) failed." -f ($failed + 1))
    exit 1
}

$manifest = Get-Content -Raw $manifestPath | ConvertFrom-Json

foreach ($repo in $manifest.repos) {
    $targetPath = Join-Path $repoRoot $repo.local_path
    $exists = Test-Path -LiteralPath $targetPath -PathType Container
    Write-Check -Name 'Repo folder exists' -Passed $exists -Detail $repo.local_path
    if (-not $exists) {
        $failed++
        continue
    }

    $isGitRepo = Test-GitRepo -Path $targetPath
    Write-Check -Name 'Repo is git' -Passed $isGitRepo -Detail $repo.local_path
    if (-not $isGitRepo) {
        $failed++
    }
}

Write-Host ''
if ($failed -eq 0) {
    Write-Host 'Summary: repo intake checks passed.'
    exit 0
}

Write-Host ("Summary: {0} repo intake check(s) failed." -f $failed)
exit 1
