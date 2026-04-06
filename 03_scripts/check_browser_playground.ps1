# Browser playground checker with no destructive behavior.

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

    $names = @($PrimaryName) + $FallbackNames
    foreach ($name in $names) {
        $command = Get-Command $name -ErrorAction SilentlyContinue
        if ($command) {
            return $command.Source
        }
    }

    return $null
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$projectRoot = Join-Path $repoRoot '01_projects\browser_playground'
$artifactPath = Join-Path $projectRoot 'artifacts\smoke-click.png'

$expectedFiles = @(
    '04_docs/browser_control_playground.md',
    '04_docs/windows_control_path.md',
    '04_docs/leak_repo_policy.md',
    '08_research/repo_intake_matrix.md',
    '23_configs/repo_manifest.example.json',
    '01_projects/browser_playground/README.md',
    '01_projects/browser_playground/package.json',
    '01_projects/browser_playground/demo_site/index.html',
    '01_projects/browser_playground/scripts/smoke_click_demo.js',
    '01_projects/browser_playground/artifacts/.gitkeep'
)

$failed = 0

foreach ($relativePath in $expectedFiles) {
    $exists = Test-Path -LiteralPath (Join-Path $repoRoot $relativePath) -PathType Leaf
    Write-Check -Name 'File exists' -Passed $exists -Detail $relativePath
    if (-not $exists) { $failed++ }
}

$nodePath = Resolve-CommandPath -PrimaryName 'node.exe' -FallbackNames @('node')
$npmPath = Resolve-CommandPath -PrimaryName 'npm.cmd' -FallbackNames @('npm')

$nodeOk = -not [string]::IsNullOrWhiteSpace($nodePath)
$npmOk = -not [string]::IsNullOrWhiteSpace($npmPath)
Write-Check -Name 'Node available' -Passed $nodeOk -Detail ($(if ($nodeOk) { $nodePath } else { 'node not found' }))
Write-Check -Name 'npm available' -Passed $npmOk -Detail ($(if ($npmOk) { $npmPath } else { 'npm not found' }))
if (-not $nodeOk) { $failed++ }
if (-not $npmOk) { $failed++ }

if (-not ($nodeOk -and $npmOk)) {
    Write-Host ''
    Write-Host ('Summary: {0} browser playground check(s) failed before runtime execution.' -f $failed)
    exit 1
}

$dependencyMarker = Join-Path $projectRoot 'node_modules\playwright'
if (-not (Test-Path -LiteralPath $dependencyMarker)) {
    $installResult = Invoke-CommandCapture -FilePath $npmPath -Arguments @('install', '--package-lock=false') -WorkingDirectory $projectRoot
    $installOk = $installResult.ExitCode -eq 0
    Write-Check -Name 'npm install' -Passed $installOk -Detail (($installResult.Output | Out-String).Trim())
    if (-not $installOk) {
        $failed++
        Write-Host ''
        Write-Host ('Summary: {0} browser playground check(s) failed.' -f $failed)
        exit 1
    }
}
else {
    Write-Check -Name 'npm install' -Passed $true -Detail 'playwright dependency already installed'
}

$browserPathResult = Invoke-CommandCapture -FilePath $nodePath -Arguments @('-e', "const { chromium } = require('playwright'); process.stdout.write(chromium.executablePath());") -WorkingDirectory $projectRoot
$browserPath = ($browserPathResult.Output | Out-String).Trim()
$browserInstalled = $browserPathResult.ExitCode -eq 0 -and -not [string]::IsNullOrWhiteSpace($browserPath) -and (Test-Path -LiteralPath $browserPath -PathType Leaf)
if (-not $browserInstalled) {
    $browserInstallResult = Invoke-CommandCapture -FilePath $npmPath -Arguments @('run', 'install-browsers') -WorkingDirectory $projectRoot
    $browserInstallOk = $browserInstallResult.ExitCode -eq 0
    Write-Check -Name 'Playwright browser install' -Passed $browserInstallOk -Detail (($browserInstallResult.Output | Out-String).Trim())
    if (-not $browserInstallOk) {
        $failed++
        Write-Host ''
        Write-Host ('Summary: {0} browser playground check(s) failed.' -f $failed)
        exit 1
    }
}
else {
    Write-Check -Name 'Playwright browser install' -Passed $true -Detail $browserPath
}

if (Test-Path -LiteralPath $artifactPath -PathType Leaf) {
    Remove-Item -LiteralPath $artifactPath -Force
}

$smokeResult = Invoke-CommandCapture -FilePath $npmPath -Arguments @('run', 'smoke') -WorkingDirectory $projectRoot
$smokeOk = $smokeResult.ExitCode -eq 0
Write-Check -Name 'Browser smoke test' -Passed $smokeOk -Detail (($smokeResult.Output | Out-String).Trim())
if (-not $smokeOk) { $failed++ }

$artifactOk = Test-Path -LiteralPath $artifactPath -PathType Leaf
Write-Check -Name 'Screenshot exists' -Passed $artifactOk -Detail $artifactPath
if (-not $artifactOk) { $failed++ }

Write-Host ''
if ($failed -eq 0) {
    Write-Host 'Summary: browser playground checks passed.'
    exit 0
}

Write-Host ('Summary: {0} browser playground check(s) failed.' -f $failed)
exit 1
