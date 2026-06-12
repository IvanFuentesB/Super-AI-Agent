[CmdletBinding()]
param()

$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$Script = Join-Path $RepoRoot '03_scripts\agent_command_center\ghoti_agent_command_center.py'

$check = & python $Script --check --json | Out-String | ConvertFrom-Json
$health = & python $Script --health --json | Out-String | ConvertFrom-Json
$content = & python $Script --scenario content-revenue-research --json | Out-String | ConvertFrom-Json
$ecommerce = & python $Script --scenario ecommerce-product-research --json | Out-String | ConvertFrom-Json
$code = & python $Script --scenario code-maintenance-swarm --json | Out-String | ConvertFrom-Json

$ok = (
    $check.ok -eq $true -and
    $health.ok -eq $true -and
    $health.binds_loopback_only -eq $true -and
    $health.has_post_routes -eq $false -and
    $content.ok -eq $true -and
    $ecommerce.ok -eq $true -and
    $code.ok -eq $true
)

[ordered]@{
    ok = [bool]$ok
    wrapper = 'check_agent_command_center'
    local_only = $true
    simulation = $true
    live_execution = $false
    scenarios_valid = [bool]($content.ok -and $ecommerce.ok -and $code.ok)
    binds_loopback_only = [bool]$health.binds_loopback_only
    has_post_routes = [bool]$health.has_post_routes
} | ConvertTo-Json -Depth 5

if (-not $ok) { exit 1 }
