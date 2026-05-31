# mcp_read_only_plan.ps1 — MCP read-only plan (PLANNING ONLY).
# Describes the planned Phase-3 first MCP: a filesystem read-only server scoped to the
# vault / docs / tool_intake / hermes_integrations folders. Reports JSON. Nothing is
# installed and no MCP server is started.
# Safety: planning only; no install; no network; no MCP server; no arbitrary commands.

Set-StrictMode -Version Latest
$ErrorActionPreference = 'Stop'
try { [Console]::OutputEncoding = [System.Text.Encoding]::UTF8 } catch {}

try {
    $result = [ordered]@{
        ok                      = $true
        wrapper                 = 'mcp_read_only_plan'
        mcp_phase               = 'planned_only'
        first_mcp               = 'filesystem_read_only'
        allowed_paths           = @(
            '14_context/agent_handoff_vault',
            'docs',
            '14_context/tool_intake',
            '14_context/hermes_integrations'
        )
        forbidden               = @(
            'write filesystem MCP',
            'browser MCP',
            'account action MCP',
            'social posting MCP',
            'unrestricted root filesystem MCP'
        )
        install_performed       = $false
        network_used            = $false
        enabled                 = $false
        requires_human_approval = $true
        local_only              = $true
    }
    $result | ConvertTo-Json -Depth 6
    exit 0
}
catch {
    [ordered]@{ ok = $false; wrapper = 'mcp_read_only_plan'; error = $_.Exception.Message; enabled = $false; requires_human_approval = $true; local_only = $true } | ConvertTo-Json -Depth 4
    exit 1
}
