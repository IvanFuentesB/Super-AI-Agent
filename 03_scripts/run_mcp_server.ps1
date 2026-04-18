Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'

$repoRoot = Split-Path -Parent $PSScriptRoot
$pythonCommand = Get-Command python -ErrorAction SilentlyContinue

if (-not $pythonCommand) {
    throw 'Python is not available on PATH. Start the Ghoti MCP server with a Python install that can run 01_projects/mcp_server/server.py.'
}

Write-Host 'Starting Ghoti MCP server...'
& $pythonCommand.Source (Join-Path $repoRoot '01_projects\mcp_server\server.py')
