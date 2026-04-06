# Sync curated third-party repos for evaluation only.

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

function Write-Result {
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

    $null = & git -c core.longpaths=true -C $Path rev-parse --is-inside-work-tree 2>$null
    return $LASTEXITCODE -eq 0
}

function Invoke-Clone {
    param(
        [string]$Source,
        [string]$TargetPath,
        [bool]$UseGh
    )

    if ($UseGh) {
        & gh repo clone $Source $TargetPath -- --depth 1 | Out-Null
        if ($LASTEXITCODE -ne 0) {
            return $false
        }
        & git -C $TargetPath config core.longpaths true | Out-Null
        return $LASTEXITCODE -eq 0
    }

    $cloneUrl = "https://github.com/$Source.git"
    & git -c core.longpaths=true clone --depth 1 $cloneUrl $TargetPath | Out-Null
    if ($LASTEXITCODE -ne 0) {
        return $false
    }
    & git -C $TargetPath config core.longpaths true | Out-Null
    return $LASTEXITCODE -eq 0
}

function Invoke-Update {
    param(
        [string]$Source,
        [string]$TargetPath
    )

    & git -C $TargetPath config core.longpaths true | Out-Null
    $originUrl = (& git -c core.longpaths=true -C $TargetPath remote get-url origin 2>$null).Trim()
    if ($LASTEXITCODE -ne 0) {
        throw "Unable to read origin URL."
    }

    if ($originUrl -notmatch [regex]::Escape($Source)) {
        throw "Origin mismatch. Expected to contain '$Source', found '$originUrl'."
    }

    $dirty = (& git -c core.longpaths=true -C $TargetPath status --porcelain 2>$null | Out-String).Trim()
    if ($dirty) {
        throw "Repository has local changes."
    }

    & git -c core.longpaths=true -C $TargetPath fetch --depth 1 origin | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Fetch failed."
    }

    & git -c core.longpaths=true -C $TargetPath pull --ff-only --no-rebase | Out-Null
    if ($LASTEXITCODE -ne 0) {
        throw "Fast-forward pull failed."
    }
}

$repoRoot = Split-Path -Parent $PSScriptRoot
$thirdPartyRoot = Join-Path $repoRoot '21_repos\third_party'
$manifestPath = Join-Path $repoRoot '23_configs\repo_manifest.example.json'

if (-not (Test-Path -LiteralPath $manifestPath -PathType Leaf)) {
    Write-Result -Name 'Manifest' -Passed $false -Detail '23_configs/repo_manifest.example.json not found'
    exit 1
}

New-Item -ItemType Directory -Force -Path $thirdPartyRoot | Out-Null

$gitCommand = Get-Command git -ErrorAction SilentlyContinue
if (-not $gitCommand) {
    Write-Result -Name 'Git available' -Passed $false -Detail 'git command not found'
    exit 1
}

$useGh = $null -ne (Get-Command gh -ErrorAction SilentlyContinue)
$manifest = Get-Content -Raw $manifestPath | ConvertFrom-Json

$failures = 0
foreach ($repo in $manifest.repos) {
    $targetPath = Join-Path $repoRoot $repo.local_path
    try {
        if (Test-Path -LiteralPath $targetPath) {
            if (Test-GitRepo -Path $targetPath) {
                Invoke-Update -Source $repo.source -TargetPath $targetPath
                Write-Result -Name $repo.repo_id -Passed $true -Detail "updated at $($repo.local_path)"
            } else {
                throw "Target path exists but is not a git repo."
            }
        } else {
            $parent = Split-Path -Parent $targetPath
            New-Item -ItemType Directory -Force -Path $parent | Out-Null
            $cloned = Invoke-Clone -Source $repo.source -TargetPath $targetPath -UseGh $useGh
            if (-not $cloned) {
                throw "Clone failed."
            }
            Write-Result -Name $repo.repo_id -Passed $true -Detail "cloned to $($repo.local_path)"
        }
    } catch {
        Write-Result -Name $repo.repo_id -Passed $false -Detail $_.Exception.Message
        $failures++
    }
}

Write-Host ''
if ($failures -eq 0) {
    Write-Host 'Summary: third-party repo sync passed.'
    exit 0
}

Write-Host ("Summary: {0} repo sync failure(s)." -f $failures)
exit 1
