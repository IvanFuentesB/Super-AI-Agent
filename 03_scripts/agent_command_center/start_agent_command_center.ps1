[CmdletBinding()]
param(
    [switch]$DryRun,
    [int]$Port = 8770
)

$ErrorActionPreference = 'Stop'
$RepoRoot = (Resolve-Path (Join-Path $PSScriptRoot '..\..')).Path
$Script = Join-Path $RepoRoot '03_scripts\agent_command_center\ghoti_agent_command_center.py'
$BindHost = '127.0.0.1'
$Url = "http://${BindHost}:${Port}/"

[ordered]@{
    ok = (Test-Path -LiteralPath $Script)
    wrapper = 'start_agent_command_center'
    dry_run = [bool]$DryRun
    url = $Url
    bind_host = $BindHost
    binds_loopback_only = $true
    get_only = $true
    has_post_routes = $false
    simulation = $true
    live_execution = $false
    launches_agents = $false
} | ConvertTo-Json -Depth 5

if ($DryRun) { exit 0 }
& python $Script --serve --host $BindHost --port $Port --json
exit $LASTEXITCODE
