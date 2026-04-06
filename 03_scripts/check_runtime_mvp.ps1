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
    $code = "import sys; sys.path.insert(0, r'$runtimeSrcEscaped'); from super_ai_agent.cli import main; raise SystemExit(main($pythonList))"
    $output = & $PythonPath -c $code 2>&1
    return @{
        ExitCode = $LASTEXITCODE
        Output = $output
    }
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$runtimeRoot = Join-Path $repoRoot '01_projects\runtime_mvp'
$runtimeSrc = Join-Path $runtimeRoot 'src'
$runtimeData = Join-Path $runtimeRoot 'runtime_data'

$expectedFiles = @(
    '01_projects/runtime_mvp/README.md',
    '01_projects/runtime_mvp/pyproject.toml',
    '01_projects/runtime_mvp/src/super_ai_agent/__init__.py',
    '01_projects/runtime_mvp/src/super_ai_agent/models.py',
    '01_projects/runtime_mvp/src/super_ai_agent/storage.py',
    '01_projects/runtime_mvp/src/super_ai_agent/queue.py',
    '01_projects/runtime_mvp/src/super_ai_agent/handoff.py',
    '01_projects/runtime_mvp/src/super_ai_agent/cli.py',
    '01_projects/runtime_mvp/runtime_data/.gitkeep',
    '04_docs/runtime_mvp.md'
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

$oldPythonPath = $env:PYTHONPATH
$env:PYTHONPATH = if ([string]::IsNullOrWhiteSpace($oldPythonPath)) { $runtimeSrc } else { "$runtimeSrc;$oldPythonPath" }

try {
    $initResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('init-data')
    $initOk = $initResult.ExitCode -eq 0
    Write-Check -Name 'CLI init-data' -Passed $initOk -Detail (($initResult.Output | Out-String).Trim())
    if (-not $initOk) { $failed++ }

    $enqueueResult = Invoke-ModuleCommand -PythonPath $pythonPath -Arguments @('enqueue', '--title', 'checker task', '--description', 'runtime check', '--risk', 'ask')
    $enqueueOk = $enqueueResult.ExitCode -eq 0
    Write-Check -Name 'CLI enqueue' -Passed $enqueueOk -Detail (($enqueueResult.Output | Out-String).Trim())
    if (-not $enqueueOk) { $failed++ }

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
}
finally {
    $env:PYTHONPATH = $oldPythonPath
}

$artifactPaths = @(
    '01_projects/runtime_mvp/runtime_data/tasks.json',
    '01_projects/runtime_mvp/runtime_data/approvals.json',
    '01_projects/runtime_mvp/runtime_data/handoff_snapshot.md'
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
