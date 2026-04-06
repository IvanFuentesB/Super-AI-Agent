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

$expectedFiles = @(
    '04_docs/local_dashboard_mvp.md',
    '04_docs/browser_control_playground.md',
    '01_projects/dashboard_mvp/README.md',
    '01_projects/dashboard_mvp/package.json',
    '01_projects/dashboard_mvp/server.js',
    '01_projects/dashboard_mvp/public/index.html',
    '01_projects/dashboard_mvp/public/app.js',
    '01_projects/dashboard_mvp/public/styles.css',
    '01_projects/dashboard_mvp/artifacts/.gitkeep'
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

    $capability = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/capability-summary" -Method Get -TimeoutSec 30
    $capabilityOk = $capability.ok -and $capability.stdout
    Write-Check -Name 'Capability endpoint' -Passed $capabilityOk -Detail ($(if ($capabilityOk) { 'capability summary returned' } else { 'capability summary missing output' }))
    if (-not $capabilityOk) { $failed++ }

    $githubStatus = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/github-status" -Method Get -TimeoutSec 30
    $githubOk = $githubStatus.ok -and $githubStatus.stdout
    Write-Check -Name 'GitHub status endpoint' -Passed $githubOk -Detail ($(if ($githubOk) { 'github status returned' } else { 'github status missing output' }))
    if (-not $githubOk) { $failed++ }

    $internshipPayload = @{
        targetRole = 'Applied AI Intern'
        company = 'Example Labs'
        jobSource = 'dashboard checker'
        fitSummary = 'Checker-created internship pack for the local dashboard MVP.'
    } | ConvertTo-Json
    $internship = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/scaffold/internship" -Method Post -ContentType 'application/json' -Body $internshipPayload -TimeoutSec 30
    $internshipPath = $null
    if ($internship.stdout -match 'personal_ops_path:\s*(.+)$') {
        $internshipPath = $matches[1].Trim()
    }
    $internshipOk = $internship.ok -and $internshipPath -and (Test-Path -LiteralPath $internshipPath -PathType Leaf)
    Write-Check -Name 'Internship scaffold endpoint' -Passed $internshipOk -Detail ($(if ($internshipOk) { $internshipPath } else { 'internship scaffold was not created' }))
    if (-not $internshipOk) { $failed++ }

    $browserSmoke = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/browser/smoke" -Method Post -ContentType 'application/json' -Body '{}' -TimeoutSec 90
    $browserSmokeOk = $browserSmoke.ok -and (Test-Path -LiteralPath $browserArtifactPath -PathType Leaf)
    Write-Check -Name 'Browser smoke endpoint' -Passed $browserSmokeOk -Detail ($(if ($browserSmokeOk) { $browserArtifactPath } else { 'browser smoke artifact missing' }))
    if (-not $browserSmokeOk) { $failed++ }

    $visibleCheck = Invoke-RestMethod -Uri "http://127.0.0.1:$port/api/browser/visible" -Method Post -ContentType 'application/json' -Body (@{ checkOnly = $true } | ConvertTo-Json) -TimeoutSec 30
    $visibleCheckOk = $visibleCheck.ok
    Write-Check -Name 'Visible demo endpoint' -Passed $visibleCheckOk -Detail ($(if ($visibleCheckOk) { 'visible endpoint responded in check-only mode' } else { 'visible endpoint failed' }))
    if (-not $visibleCheckOk) { $failed++ }
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
